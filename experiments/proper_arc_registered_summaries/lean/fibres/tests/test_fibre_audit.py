from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate_fibres import DESTINATION, PREFIX, check_report, declarations, preserved_inputs


def output_for(report):
    return "PLACEMENT_FIBRE_JSON\n"+json.dumps(report)+"\n"+"\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class FibreAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)),self.report)

    def test_five_frozen_layers_preserved(self):
        preserved_inputs()

    def test_actual_cut_schedule_cannot_be_removed(self):
        report=deepcopy(self.report)
        report["targets"][3]["dependencies"].remove("RegisteredAbsorptionChains.allCut_realize_target")
        with self.assertRaisesRegex(RuntimeError,"incomplete fibre closure"):
            check_report(output_for(report))

    def test_actual_carrier_node_cannot_be_omitted(self):
        report=deepcopy(self.report)
        report["nodes"]=[row for row in report["nodes"] if row["name"]!=PREFIX+"canonical_code_carrier"]
        with self.assertRaisesRegex(RuntimeError,"missing classification dependency node"):
            check_report(output_for(report))

    def test_origin_read_must_be_same_history(self):
        report=deepcopy(self.report)
        key=PREFIX+"ActualCodePlacements"
        report["definitions"][key]=report["definitions"][key].replace("originRecord","unrelatedOrigin")
        with self.assertRaisesRegex(RuntimeError,"same-history origin"):
            check_report(output_for(report))

    def test_parameters_cannot_assume_reachability(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"CodeFiberParams"]+=" ReachableExecution F s"
        with self.assertRaisesRegex(RuntimeError,"parameter type assumes reachability"):
            check_report(output_for(report))

    def test_actual_domain_cannot_be_formal_targets(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"ActualCodePlacements"]="Set.range positiveFiberTarget"
        with self.assertRaisesRegex(RuntimeError,"same-history origin"):
            check_report(output_for(report))

    def test_reverse_cannot_require_clean_outside(self):
        report=deepcopy(self.report)
        report["targets"][2]["signature"]+=" CleanOutside C s -> result"
        with self.assertRaisesRegex(RuntimeError,"restricted to clean histories"):
            check_report(output_for(report))

    def test_full_carrier_branch_cannot_be_omitted(self):
        report=deepcopy(self.report)
        report["definitions"][PREFIX+"CodeFiberParams"]="FiberParams n k"
        with self.assertRaisesRegex(RuntimeError,"full-carrier parameter branch"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report=deepcopy(self.report)
        report["targets"][9]["axioms"].append("assumedProperArcFibre")
        with self.assertRaisesRegex(RuntimeError,"unexpected fibre axioms"):
            check_report(output_for(report))


if __name__=="__main__":
    unittest.main()
