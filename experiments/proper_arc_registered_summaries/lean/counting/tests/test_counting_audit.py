from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_counting import DESTINATION, PREFIX, TARGETS, check_report, closure, declarations, preserved_inputs


def output_for(report):
    return "SUMMARY_COUNT_JSON\n"+json.dumps(report)+"\n"+"\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class CountingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_seven_frozen_layers_preserved(self):
        preserved_inputs()

    def test_actual_equivalence_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != PREFIX+"actualRegisteredSummariesEquivParams"]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_actual_fibre_count_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != PREFIX+"card_actualCodePlacements"]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_last_checkpoint_closure_cannot_be_truncated(self):
        report = deepcopy(self.report)
        report["targets"][4]["dependencies"].remove(PREFIX+"sum_codes_by_last_checkpoint")
        with self.assertRaisesRegex(RuntimeError, "incomplete counting closure"):
            check_report(output_for(report))

    def test_actual_left_side_cannot_be_replaced(self):
        report = deepcopy(self.report)
        report["targets"][5]["signature"] = report["targets"][5]["signature"].replace("ActualRegisteredSummaries", "FormalDecoderImage")
        with self.assertRaisesRegex(RuntimeError, "actual summary left side"):
            check_report(output_for(report))

    def test_actual_domain_cannot_be_decoder_range(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX+"ActualRegisteredSummaries"] = "Set.range decodeSummary"
        with self.assertRaisesRegex(RuntimeError, "registered seed history"):
            check_report(output_for(report))

    def test_parameter_family_cannot_assume_reachability(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX+"SummaryParams"] += " ReachableExecution F s"
        with self.assertRaisesRegex(RuntimeError, "parameters assume actual reachability"):
            check_report(output_for(report))

    def test_full_carrier_branch_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX+"CodeFiberParams"] = "FiberParams n (outsideCount hr v)"
        with self.assertRaisesRegex(RuntimeError, "independent full-carrier phase branch"):
            check_report(output_for(report))

    def test_boundary_interface_is_checked(self):
        report = deepcopy(self.report)
        report["targets"][6]["signature"] = report["targets"][6]["signature"].replace("n + 1", "n + 2")
        with self.assertRaisesRegex(RuntimeError, "short-complement regression"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][5]["axioms"].append("assumedProperArcTotal")
        with self.assertRaisesRegex(RuntimeError, "unexpected counting axioms"):
            check_report(output_for(report))

    def test_fixed_pair_total_shortcut_rejected(self):
        report = deepcopy(self.report)
        shortcut = "RegisteredAbsorptionChains.card_actualRegisteredSummaries_piecewise"
        report["nodes"].append({"name": shortcut, "kind": "theorem", "direct_dependencies": []})
        nodes = {row["name"]: row for row in report["nodes"]}
        nodes[TARGETS[5]]["direct_dependencies"].append(shortcut)
        for target in report["targets"]:
            target["dependencies"] = sorted(closure(nodes, target["name"]))
        with self.assertRaisesRegex(RuntimeError, "fixed-pair total"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
