"""Test source/evidence rejection gates; these tests are not Lean proofs."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import replay_m4d


class ScheduleGateTests(unittest.TestCase):
    def test_current_inventory(self):
        manifest = replay_m4d.verify_inputs()
        self.assertEqual(len(manifest["axiom_targets"]), 27)
        self.assertIn("FusionLogSchedule.abstract_schedule_endpoint_iff", manifest["axiom_targets"])
        self.assertIn("FusionLogSchedule.actual_trace_admissible", manifest["axiom_targets"])

    def test_parent_failure_propagates(self):
        with mock.patch.object(replay_m4d.m4c, "verify_inputs", side_effect=RuntimeError("parent drift")):
            with self.assertRaisesRegex(RuntimeError, "parent drift"):
                replay_m4d.verify_inputs()

    def test_wrong_parent_digest_rejected(self):
        manifest = json.loads(replay_m4d.MANIFEST.read_text(encoding="utf-8"))
        manifest["m4c_manifest_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-parent.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(replay_m4d, "MANIFEST", path):
                with self.assertRaisesRegex(RuntimeError, "M4-C manifest drift"):
                    replay_m4d.verify_inputs()

    def test_changed_source_rejected(self):
        manifest = json.loads(replay_m4d.MANIFEST.read_text(encoding="utf-8"))
        name = "lean_m4d/FusionLogSchedule/LiteralClassification.lean"
        manifest["files"][name] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-source.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(replay_m4d, "MANIFEST", path):
                with self.assertRaisesRegex(RuntimeError, "source byte drift"):
                    replay_m4d.verify_inputs()

    def test_unknown_axiom_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected axioms"):
            replay_m4d.m3.parse_axiom_audit("'T' depends on axioms: [sorryAx]", ["T"])


if __name__ == "__main__":
    unittest.main()
