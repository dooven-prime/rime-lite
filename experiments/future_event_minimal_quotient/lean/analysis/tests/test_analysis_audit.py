"""Negative controls for the separate analytic proof audit."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_analysis import DESTINATION, TARGETS, check_report, declaration_names


def output_for(report):
    prints = "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
        for name in declaration_names()
    )
    return "ANALYTIC_MILESTONE_JSON\n" + json.dumps(report) + "\n" + prints


class AnalysisAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_frozen_report_is_complete(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_missing_actual_count_bridge_is_rejected(self):
        report = deepcopy(self.report)
        report["targets"][2]["dependencies"].remove("FutureEvent.card_futureQuotient_closed")
        with self.assertRaisesRegex(RuntimeError, "incomplete analytic closure"):
            check_report(output_for(report))

    def test_extra_axiom_is_rejected(self):
        report = deepcopy(self.report)
        report["targets"][0]["axioms"].append("unprovedLimit")
        with self.assertRaisesRegex(RuntimeError, "analytic axioms"):
            check_report(output_for(report))

    def test_missing_graph_node_is_rejected(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != TARGETS[0]]
        with self.assertRaisesRegex(RuntimeError, "missing analytic dependency node"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
