from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate_summary import DESTINATION, PREFIX, check_report, declarations, preserved_inputs


def output_for(report):
    return "DEPENDENT_SUMMARY_JSON\n"+json.dumps(report)+"\n"+"\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class SummaryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)),self.report)

    def test_six_frozen_layers_preserved(self):
        preserved_inputs()

    def test_round_trip_dependency_cannot_be_omitted(self):
        report=deepcopy(self.report)
        report["targets"][7]["dependencies"].remove(PREFIX+"encodeSummary_decodeSummary")
        with self.assertRaisesRegex(RuntimeError,"incomplete summary closure"):
            check_report(output_for(report))

    def test_origin_classification_node_cannot_be_omitted(self):
        report=deepcopy(self.report)
        report["nodes"]=[row for row in report["nodes"] if row["name"]!="ProperArc.actual_registered_origin_unique"]
        with self.assertRaisesRegex(RuntimeError,"missing classification dependency node"):
            check_report(output_for(report))

    def test_actual_domain_cannot_be_decoder_image(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"ActualRegisteredSummaries"]="Set.range decodeSummary"
        with self.assertRaisesRegex(RuntimeError,"registered seed history"):
            check_report(output_for(report))

    def test_actual_domain_cannot_have_clean_admission(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"ActualRegisteredSummaries"]+=" CleanOutside C s"
        with self.assertRaisesRegex(RuntimeError,"restricted to constructed states"):
            check_report(output_for(report))

    def test_parameter_family_cannot_assume_reachability(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"SummaryParams"]+=" ReachableExecution F s"
        with self.assertRaisesRegex(RuntimeError,"parameters assume actual reachability"):
            check_report(output_for(report))

    def test_same_word_certificate_must_include_placement(self):
        report=deepcopy(self.report)
        report["targets"][9]["signature"]=report["targets"][9]["signature"].replace("placed","missingRead")
        with self.assertRaisesRegex(RuntimeError,"jointly realized summary field"):
            check_report(output_for(report))

    def test_decoder_must_retain_complete_chain(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"decodeSummary"]=report["definitions"][PREFIX+"decodeSummary"].replace("decodeChain","pairOnlyRead")
        with self.assertRaisesRegex(RuntimeError,"full summary fields"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report=deepcopy(self.report)
        report["targets"][7]["axioms"].append("assumedGeneratedSummaryClassification")
        with self.assertRaisesRegex(RuntimeError,"unexpected summary axioms"):
            check_report(output_for(report))


if __name__=="__main__":
    unittest.main()
