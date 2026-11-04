from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_chains import DESTINATION, check_report, declarations, preserved_inputs


def output_for(report):
    return "CHAIN_CONSTRUCTION_JSON\n" + json.dumps(report) + "\n" + "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class ChainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_previous_milestones_preserved(self):
        preserved_inputs()

    def test_embedding_cannot_be_called_equivalence(self):
        report = deepcopy(self.report)
        report["scope_status"] = "ACTUAL_CHAIN_EQUIVALENCE"
        with self.assertRaisesRegex(RuntimeError, "unproved chain-equivalence"):
            check_report(output_for(report))

    def test_actual_word_dependency_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][4]["dependencies"].remove("ProperArc.Chains.rename_run")
        with self.assertRaisesRegex(RuntimeError, "incomplete chain closure"):
            check_report(output_for(report))

    def test_old_proof_node_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != "ProperArc.run_originWord"]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_chain_domain_cannot_be_decoder_range(self):
        report = deepcopy(self.report)
        report["actual_chains_definition"] = "Set.range decodeChain"
        with self.assertRaisesRegex(RuntimeError, "real seed history"):
            check_report(output_for(report))

    def test_fixed_pair_length_cannot_replace_proper_arc_length(self):
        report = deepcopy(self.report)
        report["targets"][4]["signature"] = report["targets"][4]["signature"].replace("Code (n - r)", "Code (n - 2)")
        with self.assertRaisesRegex(RuntimeError, "proper-arc code length"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][5]["axioms"].append("assumedActualChainSurjectivity")
        with self.assertRaisesRegex(RuntimeError, "unexpected chain axioms"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
