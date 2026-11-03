"""Reject weakened or incomplete milestone reports without editing the freeze."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from freeze_finite_milestone import DESTINATION, TARGETS, audit_result


def audit_output(report):
    prints = "\n".join(
        f"'{row['name']}' depends on axioms: [{', '.join(row['axioms'])}]"
        for row in report["targets"]
    )
    return "FINITE_MILESTONE_JSON\n" + json.dumps(report) + "\n" + prints


class MilestoneAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_recorded_report_is_complete(self):
        self.assertEqual(audit_result(audit_output(self.report)), self.report)

    def test_custom_axiom_is_rejected(self):
        report = deepcopy(self.report)
        report["targets"][0]["axioms"].append("unprovedAssumption")
        with self.assertRaisesRegex(RuntimeError, "unexpected axioms"):
            audit_result(audit_output(report))

    def test_missing_dependency_is_rejected(self):
        report = deepcopy(self.report)
        report["targets"][0]["dependencies"].remove("FutureEvent.registerableNativeTarget_reachable")
        with self.assertRaisesRegex(RuntimeError, "incomplete dependency closure"):
            audit_result(audit_output(report))

    def test_reachability_in_parameter_is_rejected(self):
        report = deepcopy(self.report)
        report["parameters"][0]["dependencies"].append("FutureEvent.PairGenerated")
        with self.assertRaisesRegex(RuntimeError, "reachability hidden"):
            audit_result(audit_output(report))

    def test_missing_graph_node_is_rejected(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != TARGETS[0]]
        with self.assertRaisesRegex(RuntimeError, "missing dependency node"):
            audit_result(audit_output(report))


if __name__ == "__main__":
    unittest.main()
