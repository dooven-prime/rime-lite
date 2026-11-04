from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_converse import DESTINATION, PREFIX, check_report, declarations, preserved_inputs


def output_for(report):
    return "CHAIN_CONVERSE_JSON\n" + json.dumps(report) + "\n" + "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class ConverseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_all_prior_milestones_preserved(self):
        preserved_inputs()

    def test_actual_interval_dependency_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][3]["dependencies"].remove(PREFIX + "actual_partner_is_end_interval")
        with self.assertRaisesRegex(RuntimeError, "incomplete converse closure"):
            check_report(output_for(report))

    def test_full_record_update_node_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["nodes"] = [row for row in report["nodes"] if row["name"] != "RegisteredAbsorptionChains.checkpoint_step_records"]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_clean_admission_rejected(self):
        report = deepcopy(self.report)
        report["targets"][3]["signature"] += " CleanOutside F s -> conclusion"
        with self.assertRaisesRegex(RuntimeError, "clean premise"):
            check_report(output_for(report))

    def test_reverse_invariant_cannot_require_cleanliness(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX + "ActualChainTrace"] += " CleanOutside C s"
        with self.assertRaisesRegex(RuntimeError, "reverse invariant narrowed"):
            check_report(output_for(report))

    def test_actual_domain_cannot_be_decoder_range(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX + "ActualSelectedChains"] = "Set.range decodeChain"
        with self.assertRaisesRegex(RuntimeError, "full fixed-origin history domain"):
            check_report(output_for(report))

    def test_converse_must_retain_actual_seed_history(self):
        report = deepcopy(self.report)
        report["targets"][5]["signature"] = "formalChain = decodeChain hr v"
        with self.assertRaisesRegex(RuntimeError, "actual seed-history premise"):
            check_report(output_for(report))

    def test_encoder_must_read_port_binding(self):
        report = deepcopy(self.report)
        report["definitions"][PREFIX + "encodeChain"] = "fun _ => none"
        with self.assertRaisesRegex(RuntimeError, "actual-record key reads"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][7]["axioms"].append("assumedProperArcClassification")
        with self.assertRaisesRegex(RuntimeError, "unexpected converse axioms"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
