from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import theorem_map as tm


class TheoremMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tm.collect()

    def test_generated_map_bytes_match_frozen_inputs(self):
        self.assertEqual(tm.INDEX.read_bytes(), tm.as_json(self.data).encode("utf-8"))
        self.assertEqual(tm.MARKDOWN.read_bytes(), tm.render(self.data).encode("utf-8"))

    def test_all_nine_local_freezes_are_present(self):
        self.assertEqual([row["id"] for row in self.data["milestones"]], [f"M{i}" for i in range(1, 10)])
        self.assertEqual(len(self.data["theorems"]), 17)

    def test_union_scope_covers_every_report_not_only_selected_targets(self):
        self.assertEqual(self.data["union_declaration_node_scope"], tm.UNION_SCOPE)
        self.assertIn(tm.UNION_SCOPE, tm.render(self.data))

    def test_owner_hash_mismatch_is_rejected(self):
        records = deepcopy(tm.MILESTONES)
        records[0] = (*records[0][:3], "0"*64, records[0][4])
        with patch.object(tm, "MILESTONES", records), self.assertRaisesRegex(RuntimeError, "map manifest drift"):
            tm.collect()

    def test_wrong_source_owner_is_rejected(self):
        rows = deepcopy(tm.THEOREMS)
        rows[0] = (*rows[0][:4], "M9", rows[0][5])
        with patch.object(tm, "THEOREMS", rows), self.assertRaisesRegex(RuntimeError, "unbound map source owner"):
            tm.collect()

    def test_closure_cannot_be_truncated(self):
        path = tm.BASE/self.data["milestones"][-1]["report"]
        report = json.loads(path.read_text("utf-8"))
        report["targets"][0]["dependencies"].pop()
        with self.assertRaisesRegex(RuntimeError, "incomplete map closure"):
            tm.audit_graph(report)

    def test_extra_axiom_is_rejected(self):
        path = tm.BASE/self.data["milestones"][-1]["report"]
        report = json.loads(path.read_text("utf-8"))
        report["targets"][0]["axioms"].append("assumedProperArcClassification")
        with self.assertRaisesRegex(RuntimeError, "unapproved map axiom"):
            tm.audit_graph(report)

    def test_summary_and_refinement_owners_are_distinct(self):
        rows = {row["id"]: row for row in self.data["theorems"]}
        self.assertEqual(rows["S1"]["owner_milestone"], "M7")
        self.assertEqual(rows["N1"]["owner_milestone"], "M8")
        self.assertEqual(rows["R1"]["owner_milestone"], "M9")
        self.assertNotIn("N1", rows["R1"]["mapped_dependencies"])
        self.assertNotIn("N1", rows["R2"]["mapped_dependencies"])
        self.assertIn("F0", rows["R0"]["mapped_dependencies"])

    def test_pending_analysis_is_not_a_kernel_claim(self):
        self.assertTrue(all(row["status"] == "PAPER_PROOF_PRESENT_LEAN_NOT_STARTED"
                            for row in self.data["pending_formalization"]))
        self.assertEqual(self.data["verification_mode"], "FROZEN_SOURCE_AND_REPORT_GRAPH_CHECK_NOT_NEW_KERNEL_REPLAY")
        self.assertIsNone(self.data["companion_public_release_identity"])
        self.assertFalse(self.data["hal_v1_proof_identity_changed"])

    def test_all_local_links_resolve_and_have_correct_source_line(self):
        text = tm.render(self.data)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith("https://"):
                continue
            filename = target.split("#", 1)[0]
            self.assertTrue((tm.BASE/filename).is_file(), filename)
        for row in self.data["theorems"]:
            line = (tm.BASE/row["source"]).read_text("utf-8").splitlines()[row["source_line"]-1]
            self.assertIn(row["declaration"].rsplit(".", 1)[1], line)


if __name__ == "__main__":
    unittest.main()
