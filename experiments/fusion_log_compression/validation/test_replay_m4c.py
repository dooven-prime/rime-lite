"""Regression tests of the interpretation-layer evidence gate, not Lean proofs."""

import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

import replay_m4c


class InterpretationGateTests(unittest.TestCase):
    def test_current_inputs_and_audit_inventory(self):
        manifest = replay_m4c.verify_inputs()
        source = (replay_m4c.LEAN / "FusionLogInterpretation/AxiomAudit.lean").read_text(encoding="utf-8")
        targets = re.findall(r"^#print axioms (\S+)$", source, re.MULTILINE)
        self.assertEqual(targets, manifest["axiom_targets"])
        self.assertEqual(len(targets), 29)
        self.assertIn("FusionLogInterpretation.arbitrary_initial_log_endpoint_budget", targets)

    def test_parent_gate_failure_propagates(self):
        with mock.patch.object(replay_m4c.m4b, "verify_inputs", side_effect=RuntimeError("parent drift")):
            with self.assertRaisesRegex(RuntimeError, "parent drift"):
                replay_m4c.verify_inputs()

    def test_wrong_parent_digest_is_rejected(self):
        manifest = json.loads(replay_m4c.MANIFEST.read_text(encoding="utf-8"))
        manifest["m4b_manifest_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-parent.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(replay_m4c, "MANIFEST", path):
                with self.assertRaisesRegex(RuntimeError, "M4-B manifest drift"):
                    replay_m4c.verify_inputs()


if __name__ == "__main__":
    unittest.main()
