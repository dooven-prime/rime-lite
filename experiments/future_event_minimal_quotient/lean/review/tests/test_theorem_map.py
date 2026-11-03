"""Controls for the crosswalk; these are not additional theorem proofs."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_theorem_map as mapping


class TheoremMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = mapping.load_layers()
        cls.papers = mapping.manuscript_data(False, False)
        cls.payload = mapping.make_payload(cls.layers, cls.papers)

    def test_checked_artifacts_match(self):
        data = (json.dumps(self.payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertEqual(mapping.MAP.read_bytes(), data)
        self.assertEqual(mapping.DOCUMENT.read_bytes(),
                         mapping.render(self.payload, mapping.digest(data)).encode("utf-8"))

    def test_four_signatures_are_from_frozen_report(self):
        expected = self.layers[-1]["report_data"]["targets"]
        actual = self.payload["final_targets"]
        self.assertEqual(len(actual), 4)
        self.assertEqual([(t["name"], t["signature"]) for t in actual],
                         [(t["name"], t["signature"]) for t in expected])

    def test_public_companion_not_inferred_from_hal(self):
        identity = self.payload["public_companion_identity"]
        self.assertEqual(identity["status"], "PENDING")
        self.assertIsNone(identity["source_commit"])
        self.assertIsNone(identity["archive_identifier"])
        self.assertEqual(self.payload["papers"]["future"]["hal_identifier"], "hal-05844771v1")

    def test_missing_paper_anchor_rejected(self):
        papers = deepcopy(self.papers)
        papers["future"]["lines"] = [line for line in papers["future"]["lines"]
                                      if not line.startswith(r"\tag{7.4}")]
        with self.assertRaisesRegex(RuntimeError, "ambiguous manuscript anchor"):
            mapping.make_payload(self.layers, papers)

    def test_declaration_must_be_in_frozen_sources(self):
        with self.assertRaisesRegex(RuntimeError, "missing or ambiguous source"):
            mapping.declaration_location("ObserverComparison.notInSnapshot", self.layers)

    def test_incomplete_dependency_graph_rejected(self):
        layers = deepcopy(self.layers)
        root = layers[-1]["report_data"]["targets"][0]["name"]
        layers[-1]["report_data"]["nodes"] = [node for node in layers[-1]["report_data"]["nodes"]
                                                if node["name"] != root]
        with self.assertRaisesRegex(RuntimeError, "incomplete target graph"):
            mapping.make_payload(layers, self.papers)

    def test_reference_copy_bytes_are_not_mutable_authority(self):
        with TemporaryDirectory() as folder:
            temporary = Path(folder)
            path = temporary / mapping.PAPERS["future"]["copy"]
            path.parent.mkdir(parents=True)
            path.write_bytes(b"different manuscript bytes\n")
            with patch.object(mapping, "HERE", temporary):
                with self.assertRaisesRegex(RuntimeError, "pinned manuscript byte drift"):
                    mapping.manuscript_data(False, False)


if __name__ == "__main__":
    unittest.main()
