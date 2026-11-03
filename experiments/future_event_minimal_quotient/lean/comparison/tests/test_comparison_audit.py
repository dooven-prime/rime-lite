"""Rejection controls for the actual-observer comparison proof closure."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_comparison import DESTINATION, TARGETS, check_report, declarations, preserved_inputs


def output_for(report):
    printed = "\n".join(f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
                        for name in declarations())
    return "OBSERVER_COMPARISON_JSON\n" + json.dumps(report) + "\n" + printed


class ComparisonAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_frozen_graph(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_preserved_milestones(self):
        self.assertEqual(len(preserved_inputs()), 3)

    def test_missing_actual_full_count(self):
        report = deepcopy(self.report)
        report["targets"][1]["dependencies"].remove("FullSummary.card_fullQuotient_closed")
        with self.assertRaisesRegex(RuntimeError, "incomplete comparison closure"):
            check_report(output_for(report))

    def test_missing_actual_future_count(self):
        report = deepcopy(self.report)
        report["targets"][2]["dependencies"].remove("FutureEvent.card_futureQuotient_closed")
        with self.assertRaisesRegex(RuntimeError, "incomplete comparison closure"):
            check_report(output_for(report))

    def test_proxy_signature_rejected(self):
        report = deepcopy(self.report)
        report["targets"][1]["signature"] = "Tendsto (fun m => formalCount m) atTop (nhds (4/81))"
        with self.assertRaisesRegex(RuntimeError, "full count is a proxy"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][2]["axioms"].append("assumedAsymptotic")
        with self.assertRaisesRegex(RuntimeError, "comparison axioms"):
            check_report(output_for(report))

    def test_missing_node_rejected(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != TARGETS[2]]
        with self.assertRaisesRegex(RuntimeError, "missing comparison dependency node"):
            check_report(output_for(report))

    def test_axiom_inventory_rejected(self):
        text = output_for(self.report)
        text = text.replace(f"'{declarations()[-1]}' depends", "'notTheAuditedTheorem' depends")
        with self.assertRaisesRegex(RuntimeError, "axiom inventory drift"):
            check_report(text)


if __name__ == "__main__":
    unittest.main()
