"""Regression checks of the M4 evidence gate, not tests of Lean proofs."""

from contextlib import contextmanager
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

import replay_m4


class BudgetReplayGateTests(unittest.TestCase):
    def test_current_inputs_and_audit_inventory(self):
        manifest = replay_m4.verify_inputs()
        audit = (replay_m4.M4 / "FusionLogReplay/AxiomAudit.lean").read_text(encoding="utf-8")
        names = re.findall(r"^#print axioms (\S+)$", audit, re.MULTILINE)
        self.assertEqual(names, manifest["axiom_targets"])
        self.assertEqual(len(names), 34)
        self.assertIn("FusionLogReplay.sourceOrdered_log_endpoint_budget", names)

    @contextmanager
    def fixture(self, source=b"theorem test : True := by trivial\n"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lean = root / "lean_m4"
            lean.mkdir()
            (root / "proof-manifest.v1.json").write_bytes(b"{}\n")
            file = lean / "Test.lean"
            file.write_bytes(source)
            manifest = root / "m4-development-manifest.v2.json"
            manifest.write_text(json.dumps({
                "m3_manifest_sha256": replay_m4.m3.sha256(root / "proof-manifest.v1.json"),
                "non_lean_inputs": [],
                "files": {"lean_m4/Test.lean": replay_m4.m3.sha256(file)},
            }), encoding="utf-8")
            with mock.patch.multiple(replay_m4, ROOT=root, M4=lean, MANIFEST=manifest), \
                    mock.patch.object(replay_m4.m3, "verify_inputs", return_value={}):
                yield root, file

    def test_byte_and_inventory_drift(self):
        with self.fixture() as (root, file):
            replay_m4.verify_inputs()
            file.write_bytes(b"changed\n")
            with self.assertRaisesRegex(RuntimeError, "byte drift"):
                replay_m4.verify_inputs()
        with self.fixture() as (root, _):
            (root / "lean_m4/Extra.lean").write_bytes(b"\n")
            with self.assertRaisesRegex(RuntimeError, "inventory mismatch"):
                replay_m4.verify_inputs()

    def test_new_axiom_or_placeholder_rejected(self):
        for source in (b"axiom unchecked : False\n", b"theorem unchecked : False := by sorry\n"):
            with self.subTest(source=source), self.fixture(source):
                with self.assertRaisesRegex(RuntimeError, "placeholder or new axiom"):
                    replay_m4.verify_inputs()

    def test_m3_anchor_drift(self):
        with self.fixture() as (root, _):
            (root / "proof-manifest.v1.json").write_bytes(b"changed\n")
            with self.assertRaisesRegex(RuntimeError, "M3 baseline manifest drift"):
                replay_m4.verify_inputs()


if __name__ == "__main__":
    unittest.main()
