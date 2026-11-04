"""Rejection controls for the first proper-arc proof milestone."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_companion import DESTINATION, check_report, declarations, lean_code


def output_for(report):
    printed = "\n".join(f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
                        for name in declarations())
    return "PROPER_ARC_JSON\n" + json.dumps(report) + "\n" + printed


class OriginAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_complete_frozen_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_actual_run_dependency_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][2]["dependencies"].remove("RegisteredAbsorptionChains.run")
        with self.assertRaisesRegex(RuntimeError, "incomplete dependency closure"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][2]["axioms"].append("assumedProperArcReachability")
        with self.assertRaisesRegex(RuntimeError, "origin axioms"):
            check_report(output_for(report))

    def test_missing_node_rejected(self):
        report = deepcopy(self.report)
        report["nodes"] = [node for node in report["nodes"] if node["name"] != "ProperArc.run_originWord"]
        with self.assertRaisesRegex(RuntimeError, "missing dependency node"):
            check_report(output_for(report))

    def test_realization_cannot_be_a_reachability_premise(self):
        report = deepcopy(self.report)
        report["targets"][2]["signature"] += " ReachableExecution F s -> run F s originWord = target"
        with self.assertRaisesRegex(RuntimeError, "became conditional"):
            check_report(output_for(report))

    def test_lint_masks_comments_not_proofs(self):
        source = '/- sorry /- nested axiom -/ -/\n-- admit\n"sorry"\ntheorem open : True := by sorry\n'
        code = lean_code(source)
        self.assertEqual(code.count("sorry"), 1)
        self.assertNotIn("axiom", code)


if __name__ == "__main__":
    unittest.main()
