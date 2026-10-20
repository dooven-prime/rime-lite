"""Packaging/replay boundary regressions, separate from the 30 application tests."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
import warnings
import zipfile

sys.dont_write_bytecode = True
from validate_package import PACKAGE, check_document_links, check_record, inspect_archive


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = (PACKAGE / "source/q2-source-v1.zip").read_bytes()
        cls.binding = json.loads((PACKAGE / "source/snapshot.v1.json").read_text(encoding="utf-8"))
        cls.record = json.loads((PACKAGE / "results/q2-controls.v1.json").read_text(encoding="utf-8"))

    def rewrite(self, change):
        stream = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.data)) as old, zipfile.ZipFile(stream, "w") as new:
            members = [(info, old.read(info)) for info in old.infolist()]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                for info, data in change(members):
                    new.writestr(info, data)
        data = stream.getvalue()
        binding = deepcopy(self.binding)
        binding["archive"].update(size=len(data), sha256=hashlib.sha256(data).hexdigest())
        return data, binding

    def test_declared_snapshot_and_record(self):
        payload = inspect_archive(self.data, self.binding)
        check_record(self.record)
        readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
        request = re.search(r"```json\s*\n(.*?)\n```", readme, re.S)
        self.assertIsNotNone(request)
        self.assertEqual(json.loads(request.group(1)),
                         json.loads(payload["examples/origin_read_failure.json"]))
        self.assert_runtime_commit_claim_rejected_after_rehash()

    def assert_runtime_commit_claim_rejected_after_rehash(self):
        def change(members):
            changed = []
            for info, value in members:
                if info.filename == "source-manifest.json":
                    manifest = json.loads(value)
                    entry = next(row for row in manifest["files"] if row["path"] == "q2/engine.py")
                    entry["origin"]["content_commit"] = "0" * 40
                    value = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
                changed.append((info, value))
            return changed

        data, binding = self.rewrite(change)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            raw = archive.read("source-manifest.json")
        binding["source_manifest"] = json.loads(raw)
        binding["source_manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, "runtime source origin drift"):
            inspect_archive(data, binding)

    def test_reader_links_cannot_depend_on_unbound_notes(self):
        with tempfile.TemporaryDirectory(prefix="paper40-links-") as temporary:
            root = Path(temporary)
            (root / "reader.md").write_text("[support](support.md)\n", encoding="utf-8")
            (root / "support.md").write_text("Bound documentation.\n", encoding="utf-8")
            check_document_links(root, ("reader.md", "support.md"))
            with self.assertRaisesRegex(ValueError, "outside candidate closure"):
                check_document_links(root, ("reader.md",))
            (root / "reader.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside candidate closure"):
                check_document_links(root, ("reader.md", "support.md"))

    def test_archive_byte_drift_rejected(self):
        with self.assertRaisesRegex(ValueError, "archive bytes drift"):
            inspect_archive(self.data[:-1] + bytes([self.data[-1] ^ 1]), self.binding)

    def test_duplicate_member_rejected(self):
        data, binding = self.rewrite(lambda members: members + [members[0]])
        with self.assertRaisesRegex(ValueError, "duplicate archive member"):
            inspect_archive(data, binding)

    def test_missing_member_rejected(self):
        data, binding = self.rewrite(lambda members: members[1:])
        with self.assertRaisesRegex(ValueError, "archive inventory drift"):
            inspect_archive(data, binding)

    def test_member_drift_rejected_after_outer_rehash(self):
        def change(members):
            return [(info, value + b"\n" if info.filename == "q2/engine.py" else value)
                    for info, value in members]
        data, binding = self.rewrite(change)
        with self.assertRaisesRegex(ValueError, "source payload drift"):
            inspect_archive(data, binding)

    def test_control_set_cannot_shrink(self):
        record = deepcopy(self.record)
        record["cases"].pop()
        with self.assertRaisesRegex(ValueError, "control set narrowed"):
            check_record(record)

    def test_domain_counts_cannot_shrink(self):
        record = deepcopy(self.record)
        record["cases"][0]["decision"]["domain"]["log_states"] -= 1
        with self.assertRaisesRegex(ValueError, "generated domain count drift"):
            check_record(record)

    def test_skipped_test_is_not_full_replay(self):
        record = deepcopy(self.record)
        record["tests"]["skipped"] = 1
        with self.assertRaisesRegex(ValueError, "unexecuted/narrowed test suite"):
            check_record(record)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    unittest.main()
