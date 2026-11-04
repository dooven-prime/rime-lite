from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_classification import DESTINATION, check_report, declarations, preserved_inputs


def output_for(report):
    return "ORIGIN_CLASSIFICATION_JSON\n" + json.dumps(report) + "\n" + "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class ClassificationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_prior_frozen_sources_preserved(self):
        preserved_inputs()

    def test_first_registration_input_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][2]["dependencies"].remove("ProperArc.actual_first_registration")
        with self.assertRaisesRegex(RuntimeError, "incomplete classification closure"):
            check_report(output_for(report))

    def test_upstream_transitive_node_cannot_be_omitted(self):
        report = deepcopy(self.report)
        report["nodes"] = [node for node in report["nodes"] if node["name"] != "ProperArc.run_local_unregistered"]
        with self.assertRaisesRegex(RuntimeError, "missing classification dependency node"):
            check_report(output_for(report))

    def test_extra_clean_admission_rejected(self):
        report = deepcopy(self.report)
        report["targets"][2]["signature"] += " CleanOutside F s -> conclusion"
        with self.assertRaisesRegex(RuntimeError, "extra admission premise"):
            check_report(output_for(report))

    def test_raw_origin_type_cannot_be_replaced_by_formal_range(self):
        report = deepcopy(self.report)
        report["actual_origins_definition"] = "Set.range originRecord"
        with self.assertRaisesRegex(RuntimeError, "real seed history"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][4]["axioms"].append("assumedOriginExhaustiveness")
        with self.assertRaisesRegex(RuntimeError, "classification axioms"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
