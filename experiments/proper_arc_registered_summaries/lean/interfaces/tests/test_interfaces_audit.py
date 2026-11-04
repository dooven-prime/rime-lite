from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_interfaces import DESTINATION, check_report, declarations, preserved_inputs


def output_for(report):
    return "ORIGIN_INTERFACES_JSON\n" + json.dumps(report) + "\n" + "\n".join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in declarations())


class InterfaceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8"))

    def test_complete_report(self):
        self.assertEqual(check_report(output_for(self.report)), self.report)

    def test_origin_freeze_preserved(self):
        preserved_inputs()

    def test_fusion_dependency_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][0]["dependencies"].remove("ProperArc.run_local_unregistered")
        with self.assertRaisesRegex(RuntimeError, "incomplete interface closure"):
            check_report(output_for(report))

    def test_explicit_word_cannot_be_removed(self):
        report = deepcopy(self.report)
        report["targets"][1]["dependencies"].remove("ProperArc.originWord")
        with self.assertRaisesRegex(RuntimeError, "incomplete interface closure"):
            check_report(output_for(report))

    def test_extra_axiom_rejected(self):
        report = deepcopy(self.report)
        report["targets"][2]["axioms"].append("abstractHistoryChoice")
        with self.assertRaisesRegex(RuntimeError, "interface axioms"):
            check_report(output_for(report))


if __name__ == "__main__":
    unittest.main()
