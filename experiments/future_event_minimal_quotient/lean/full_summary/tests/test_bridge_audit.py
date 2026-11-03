"""Negative controls for the actual full-summary observer/count audit."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_bridge import DESTINATION, TARGETS, check_report, declarations


def output_for(report):
    prints = "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
        for name in declarations()
    )
    return "FULL_SUMMARY_JSON\n" + json.dumps(report) + "\n" + prints


class BridgeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_frozen_report_is_complete(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_origin_dependency_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][3]["dependencies"].remove("RegisteredAbsorptionChains.actual_registered_origin_unique")
        with self.assertRaisesRegex(RuntimeError, "incomplete full-summary closure"):
            check_report(output_for(report))

    def test_terminal_summaries_cannot_be_discarded(self):
        report = deepcopy(self.report)
        report["targets"][2]["signature"] = report["targets"][2]["signature"].replace(
            "ActualRegisteredSummaries", "RegisteredNonterminalPlacements")
        with self.assertRaisesRegex(RuntimeError, "registered normal forms"):
            check_report(output_for(report))

    def test_extra_axiom_is_rejected(self):
        report = deepcopy(self.report)
        report["targets"][1]["axioms"].append("unprovedObserverBridge")
        with self.assertRaisesRegex(RuntimeError, "full-summary axioms"):
            check_report(output_for(report))

    def test_moore_contract_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][1]["dependencies"].remove("FullSummary.output")
        with self.assertRaisesRegex(RuntimeError, "incomplete full-summary closure"):
            check_report(output_for(report))

    def test_analytic_input_is_rejected(self):
        report = deepcopy(self.report)
        fake = "FutureEventAnalysis.unwantedInput"
        report["nodes"].append({"name": fake, "kind": "definition", "direct_dependencies": []})
        for node in report["nodes"]:
            if node["name"] == TARGETS[0]:
                node["direct_dependencies"].append(fake)
        for target in report["targets"]:
            if TARGETS[0] in target["dependencies"]:
                target["dependencies"].append(fake)
        with self.assertRaisesRegex(RuntimeError, "analytic result"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
