#!/usr/bin/env python3
"""Negative contract tests; no producer import and no assertion dependence."""

import copy
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from validate_package import child_environment
from validate_lean_formalization import DECLARATIONS, check_axioms, check_static
from validate_return_budget import replay_case, verify_shape
from audit_scope import RESULT_PATH, branches


ROOT = Path(__file__).resolve().parents[3]


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / RESULT_PATH).read_text(encoding="utf-8"))

    def altered(self):
        return copy.deepcopy(self.record)

    def rejects(self, record):
        with self.assertRaises(ValueError):
            verify_shape(record)

    def test_fixed_inventory_passes(self):
        verify_shape(self.record)

    def test_missing_case_fails(self):
        record = self.altered()
        record["cases"].pop()
        self.rejects(record)

    def test_duplicate_case_fails(self):
        record = self.altered()
        record["cases"][1] = record["cases"][0]
        self.rejects(record)

    def test_scope_cannot_shrink_budget(self):
        record = self.altered()
        record["scope"]["exact_return_counts"] = [1, 2]
        self.rejects(record)

    def test_layers_cannot_shrink_with_scope(self):
        record = self.altered()
        record["cases"][0]["layers"] = record["cases"][0]["layers"][:2]
        self.rejects(record)

    def test_terminal_return_is_not_free(self):
        record = self.altered()
        record["scope"]["terminal_return_is_counted"] = False
        self.rejects(record)

    def test_extra_result_field_fails(self):
        record = self.altered()
        record["independent_validation"] = True
        self.rejects(record)

    def test_missing_matched_family_fails(self):
        record = self.altered()
        record["matched_controls"].pop()
        self.rejects(record)

    def test_equal_counts_do_not_replace_survivor_maps(self):
        record = self.altered()
        record["matched_controls"][0]["consecutive_pair_controls"][0]["at_most_one"]["reflection1"] = [[6, 9, 12]]
        self.rejects(record)

    def test_tampered_witness_is_replayed(self):
        record = self.altered()
        case = record["cases"][0]
        case["actual_terminal_witnesses"][0]["labels"] = [1]
        with self.assertRaises(ValueError):
            replay_case(case, branches()[0], 1)

    def test_tampered_complete_set_fingerprint_fails(self):
        record = self.altered()
        case = record["cases"][0]
        case["layers"][0]["exact"]["survivor_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            replay_case(case, branches()[0], 1)

    def test_exact_layer_is_not_cumulative_layer(self):
        case = next(case for case in self.record["cases"] if case["group_order"] == 120
                    and sum(p_i > p_j for i, p_i in enumerate(case["input"]["local_permutations"][0])
                            for p_j in case["input"]["local_permutations"][0][i + 1:]) % 2 == 1)
        self.assertEqual(case["layers"][-1]["exact"]["terminal_count"], 60)
        self.assertEqual(case["layers"][-1]["cumulative"]["terminal_count"], 120)

    def test_optimization_environment_is_removed(self):
        with patch.dict(os.environ, {"PYTHONOPTIMIZE": "2"}):
            self.assertNotIn("PYTHONOPTIMIZE", child_environment())
            self.assertEqual(child_environment()["PYTHONDONTWRITEBYTECODE"], "1")

    def test_partial_formal_manifest_matches_sources(self):
        check_static()

    def audit_output(self):
        return "\n".join(f"'Rime.Paper38.{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
                         for name in DECLARATIONS)

    def test_standard_axiom_footprint_allowed(self):
        check_axioms(self.audit_output())

    def test_project_axiom_is_rejected(self):
        with self.assertRaises(ValueError):
            check_axioms(self.audit_output().replace("propext", "Rime.Paper38.unproved_geometry", 1))

    def test_missing_axiom_audit_line_fails(self):
        with self.assertRaises(ValueError):
            check_axioms("\n".join(self.audit_output().splitlines()[1:]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
