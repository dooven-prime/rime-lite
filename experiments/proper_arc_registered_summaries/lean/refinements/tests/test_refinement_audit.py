from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_refinements import (
    CHAIN_TARGETS, DESTINATION, PREFIX, RANK_TARGETS, UPSTREAM,
    check_report, closure, declarations, preserved_inputs,
)


def output_for(report):
    return "COMBINATORIAL_REFINEMENTS_JSON\n"+json.dumps(report)+"\n"+"\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class RefinementAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_eight_frozen_layers_preserved(self):
        preserved_inputs()

    def assert_missing_node_rejected(self, name):
        report = deepcopy(self.report)
        report["nodes"] = [node for node in report["nodes"] if node["name"] != name]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_actual_chain_equivalence_cannot_be_omitted(self):
        self.assert_missing_node_rejected(UPSTREAM[0])

    def test_positive_placement_equivalence_cannot_be_omitted(self):
        self.assert_missing_node_rejected(UPSTREAM[1])

    def test_full_carrier_equivalence_cannot_be_omitted(self):
        self.assert_missing_node_rejected(UPSTREAM[2])

    def test_chain_readback_closure_cannot_be_truncated(self):
        report = deepcopy(self.report)
        report["targets"][4]["dependencies"].remove(PREFIX+"decodeChain_length")
        with self.assertRaisesRegex(RuntimeError, "incomplete refinement closure"):
            check_report(output_for(report))

    def test_rank_readback_closure_cannot_be_truncated(self):
        report = deepcopy(self.report)
        report["targets"][8]["dependencies"].remove(PREFIX+"positiveFiberTarget_rank")
        with self.assertRaisesRegex(RuntimeError, "incomplete refinement closure"):
            check_report(output_for(report))

    def test_chain_type_cannot_be_only_formal_codes(self):
        report = deepcopy(self.report)
        report["targets"][4]["type_constants"].remove(PREFIX+"ActualSelectedChains")
        with self.assertRaisesRegex(RuntimeError, "chain count lost actual history type"):
            check_report(output_for(report))

    def test_rank_type_cannot_be_only_formal_params(self):
        report = deepcopy(self.report)
        report["targets"][8]["type_constants"].remove(PREFIX+"ActualRankCodePlacements")
        with self.assertRaisesRegex(RuntimeError, "rank count lost actual placement type"):
            check_report(output_for(report))

    def test_rank_filter_must_read_literal_placement(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX+"ActualRankCodePlacements"] = (
            "fun P : ActualCodePlacements c hr t v => (placedBlocks (positiveFiberTarget params)).card = s")
        with self.assertRaisesRegex(RuntimeError, "replaced by a parameter index"):
            check_report(output_for(report))

    def test_actual_chain_domain_cannot_require_cleanliness(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX+"ActualSelectedChains"] += " CleanOutside C s"
        with self.assertRaisesRegex(RuntimeError, "restricted to constructed states"):
            check_report(output_for(report))

    def test_full_carrier_zero_complement_must_remain_explicit(self):
        report = deepcopy(self.report)
        report["targets"][11]["signature"] = report["targets"][11]["signature"].replace("= 0", "= 1")
        with self.assertRaisesRegex(RuntimeError, "rank-one phase interface drift"):
            check_report(output_for(report))

    def test_positive_rank_domain_is_checked(self):
        report = deepcopy(self.report)
        report["targets"][8]["signature"] = report["targets"][8]["signature"].replace("2 ≤ s", "1 ≤ s")
        with self.assertRaisesRegex(RuntimeError, "positive-rank formula or domain drift"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][4]["axioms"].append("assumedAbsorptionRefinement")
        with self.assertRaisesRegex(RuntimeError, "unexpected refinement axioms"):
            check_report(output_for(report))

    def test_rank_branch_is_independent_of_new_chain_branch(self):
        report = deepcopy(self.report)
        nodes = {node["name"]: node for node in report["nodes"]}
        nodes[RANK_TARGETS[3]]["direct_dependencies"].append(PREFIX+"codeOfColors")
        for target in report["targets"]:
            target["dependencies"] = sorted(closure(nodes, target["name"]))
        with self.assertRaisesRegex(RuntimeError, "rank refinement depends on new chain branch"):
            check_report(output_for(report))

    def test_total_count_cannot_substitute_for_refinement(self):
        report = deepcopy(self.report)
        shortcut = PREFIX+"card_actual_registered_summaries"
        report["nodes"].append({"name": shortcut, "kind": "theorem", "direct_dependencies": []})
        nodes = {node["name"]: node for node in report["nodes"]}
        nodes[CHAIN_TARGETS[4]]["direct_dependencies"].append(shortcut)
        for target in report["targets"]:
            target["dependencies"] = sorted(closure(nodes, target["name"]))
        with self.assertRaisesRegex(RuntimeError, "total-count shortcut"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
