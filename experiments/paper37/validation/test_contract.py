#!/usr/bin/env python3
"""Fast negative tests for fixed scope, exact sets, and replay environment."""

from __future__ import annotations

import copy
import os
import unittest
from unittest.mock import patch

import validate_ordinary_lane_audit as audit
from validate_package import child_environment
from validate_source import has_damaged_spacing
from validate_lean_formalization import check_axiom_output, DECLARATIONS


class AuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = audit.load_result()

    def test_fixed_catalogue(self) -> None:
        audit.check_structure(self.record)
        self.assertEqual(len(self.record["cases"]), 312)

    def test_coordinated_domain_shrink_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"] = record["cases"][:120]
        record["domains"] = record["domains"][:1]
        record["scope"]["g3_policy"] = "omitted"
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_case_omission_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"].pop()
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_reordered_inputs_are_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"][0], record["cases"][1] = record["cases"][1], record["cases"][0]
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_changed_branch_parameter_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"][0]["local_permutations"][0] = [1, 0, 2, 3, 4]
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_boolean_is_not_an_integer_coordinate(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"][0]["local_permutations"][0][0] = False
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_boolean_is_not_a_source_lane(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"][0]["source_lane"] = True
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_changed_set_digest_is_rejected_by_replay(self) -> None:
        record = copy.deepcopy(self.record)
        record["cases"][0]["digests"]["survivor_spectra"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "finite replay drift"):
            audit.validate(record)

    def test_matched_domain_omission_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["matched_controls"].pop()
        with self.assertRaises(ValueError):
            audit.check_structure(record)

    def test_same_counts_do_not_identify_survivor_maps(self) -> None:
        spec = audit.branches()[0]
        row, _, spectra = audit.recompute(spec, 1)
        changed = copy.deepcopy(spectra)
        pair = next(pair for pair, values in changed.items() if values)
        survivor = next(iter(changed[pair]))
        changed[pair] = {tuple(reversed(survivor))}
        self.assertEqual(len(changed[pair]), len(spectra[pair]))
        self.assertNotEqual(changed[pair], spectra[pair])
        self.assertTrue(row["digests"]["survivor_spectra"])

    def test_pythonoptimize_is_removed(self) -> None:
        with patch.dict(os.environ, {"PYTHONOPTIMIZE": "2", "P37_TEST_MARKER": "kept"}):
            environment = child_environment()
        self.assertNotIn("PYTHONOPTIMIZE", environment)
        self.assertEqual(environment["P37_TEST_MARKER"], "kept")

    def test_tex_spacing_lint(self) -> None:
        self.assertFalse(has_damaged_spacing(r"x,\qquad y,\quad z"))
        self.assertTrue(has_damaged_spacing("x,qquad y"))
        self.assertTrue(has_damaged_spacing("x quad (y)"))

    def test_extra_axiom_is_rejected(self) -> None:
        output = "\n".join(
            f"'Rime.Paper37.{name}' depends on axioms: [propext]"
            for name in DECLARATIONS
        )
        check_axiom_output(output)
        with self.assertRaises(ValueError):
            check_axiom_output(output.replace("[propext]", "[propext, sorryAx]", 1))

    def test_missing_axiom_audit_declaration_is_rejected(self) -> None:
        output = "\n".join(
            f"'Rime.Paper37.{name}' does not depend on any axioms"
            for name in DECLARATIONS[:-1]
        )
        with self.assertRaises(ValueError):
            check_axiom_output(output)


if __name__ == "__main__":
    unittest.main()
