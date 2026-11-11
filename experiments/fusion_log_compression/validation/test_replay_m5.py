"""M5 evidence-gate tests, not replacements for the Lean proofs."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import replay_m5 as m5
import verify_ci_m5_ancestor as ancestor


class EnumerationGateTests(unittest.TestCase):
    def test_current_inputs_and_target_inventory(self):
        manifest = m5.verify_inputs()
        self.assertEqual(len(manifest["axiom_targets"]), 64)
        self.assertIn("FusionLogEnumeration.card_rawJoint", manifest["axiom_targets"])
        self.assertIn("FusionLogEnumeration.card_rawActualLogFiber_of_reachable", manifest["axiom_targets"])

    def test_frozen_parent_failure_propagates(self):
        with mock.patch.object(m5.m4d, "verify_inputs", side_effect=RuntimeError("parent drift")):
            with self.assertRaisesRegex(RuntimeError, "parent drift"):
                m5.verify_inputs()

    def check_altered_manifest(self, alter, expected):
        manifest = json.loads(m5.MANIFEST.read_text(encoding="utf-8"))
        alter(manifest)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "altered.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(m5, "MANIFEST", path):
                with self.assertRaisesRegex(RuntimeError, expected):
                    m5.verify_inputs()

    def test_wrong_parent_digest_rejected(self):
        self.check_altered_manifest(lambda m: m.update(m4d_manifest_sha256="0" * 64), "M4-D manifest drift")

    def test_changed_source_rejected(self):
        self.check_altered_manifest(lambda m: m["files"].update({
            "lean_m5/FusionLogEnumeration/RawLogFiber.lean": "0" * 64}), "source byte drift")

    def test_duplicate_audit_target_rejected(self):
        self.check_altered_manifest(lambda m: m["axiom_targets"].append(m["axiom_targets"][0]),
                                   "M5 axiom inventory drift")

    def test_method_name_is_not_tactic_placeholder(self):
        self.assertFalse(m5.has_placeholder("let frame := start.named.admit start.positiveOrder"))
        self.assertTrue(m5.has_placeholder("theorem bad : True := by admit"))
        self.assertTrue(m5.has_placeholder("theorem bad : True := by sorry"))

    def test_unknown_axiom_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected axioms"):
            m5.m3.parse_axiom_audit("'T' depends on axioms: [sorryAx]", ["T"])

    def test_wrong_parent_tag_target_rejected(self):
        with mock.patch.object(ancestor, "COMMIT", "0" * 40):
            with self.assertRaisesRegex(RuntimeError, "M4-D content commit drift"):
                ancestor.verify()


if __name__ == "__main__":
    unittest.main()
