"""Exact finite controls for class counts, pair splits, and coordinate scope."""

from fractions import Fraction
from itertools import combinations
import unittest

import numpy as np

import profile_heterogeneity_census as profile


class ProfileCensusTests(unittest.TestCase):
    def test_fraction_equivalence_and_pair_counts(self):
        mass = np.array([2, 4, 5, 3], dtype=np.int64)
        nums = np.array([[1, 1], [2, 2], [0, 0], [3, 0]], dtype=np.int64)
        codes = np.array([0, 0, 0, 1])
        result = profile.census(mass, nums, codes, ["A", "B"], np.arange(4))
        self.assertEqual(result["profile_classes_with_source_sector_retained"], 3)
        self.assertEqual(result["collision_profile_classes"], 1)
        self.assertEqual(result["sources_in_collision_profile_classes"], 2)
        self.assertEqual(result["all_unequal_profile_source_pairs"], 2)
        self.assertEqual(result["coordinate_separation"]["minimum_coordinate_count"], 1)
        self.assertEqual(result["coordinate_separation"]["minimum_coordinate_sets"], [["A"], ["B"]])
        for i, sector in enumerate(result["by_source_sector"]):
            members = [a for a in range(4) if codes[a] == i]
            exact = {a: tuple(Fraction(int(p), int(mass[a])) for p in nums[a])
                     for a in members}
            self.assertEqual(sector["exact_profile_classes"], len(set(exact.values())))
            for j, coordinate in enumerate(sector["coordinates"]):
                different = sum(exact[a][j] != exact[b][j] for a, b in combinations(members, 2))
                self.assertEqual(coordinate["separated_unordered_source_pairs"], different)

    def test_mandatory_coordinates_have_same_fiber_witnesses(self):
        mass = np.array([1, 1, 1, 0], dtype=np.int64)
        nums = np.array([[1, 0], [0, 1], [0, 0], [0, 0]], dtype=np.int64)
        result = profile.census(mass, nums, np.array([0, 0, 0, 1]),
                                ["A", "B"], np.array([100, 101, 102, 103]))
        separation = result["coordinate_separation"]
        self.assertEqual(separation["minimum_coordinate_count"], 2)
        self.assertEqual(separation["mandatory_coordinates"], ["A", "B"])
        for item in separation["mandatory_witnesses"]:
            a, b = item["source_indices"]
            j = ["A", "B"].index(item["coordinate"])
            self.assertNotEqual(nums[a, j], nums[b, j])
            self.assertEqual(nums[a, 1 - j], nums[b, 1 - j])

    def test_constant_profiles_need_no_coordinate(self):
        result = profile.census(np.array([2, 4]), np.array([[1, 1], [2, 2]]),
                                np.array([0, 0]), ["A", "B"], np.array([10, 11]))
        self.assertEqual(result["coordinate_separation"]["minimum_coordinate_count"], 0)
        self.assertEqual(result["all_unequal_profile_source_pairs"], 0)

    def test_safe_integer_accumulation_and_signs(self):
        rows, cols = np.array([0, 0, 1, 2]), np.array([0, 2, 0, 1])
        weights = np.array([2**60, 1, 7, 3], dtype=np.int64)
        mass, nums, bound = profile.accumulate(
            rows, cols, weights, np.array([1, -1, 0]), np.array([0, 0, 1]), 3, 2)
        self.assertEqual(mass.tolist(), [2**60 + 1, 7, 0])
        self.assertEqual(nums.tolist(), [[2**60, 1], [0, 0], [0, 0]])
        self.assertEqual(bound["partial_sum_upper_bound"], 4 * 2**60)

    def test_unsafe_integer_bound_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe int64"):
            profile.accumulate(np.array([0, 0, 1]), np.array([1, 0, 0]),
                               np.array([2**62, 1, 1], dtype=np.int64),
                               np.array([1, 1]), np.array([0, 1]), 2, 2)

    def test_floating_counts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be integers"):
            profile.accumulate(np.array([0]), np.array([0]), np.array([1.0]),
                               np.array([1]), np.array([0]), 1, 1)

    def test_many_coordinate_bounds_can_prove_a_minimum(self):
        keys = np.zeros((2, 10), dtype=np.int64)
        keys[1, 1] = 1
        result = profile.separation_scope(
            keys, np.array([0, 1]), np.array([0, 1]), np.array([10, 11]),
            [str(j) for j in range(9)])
        self.assertEqual(result["status"], "EXACT_BY_MATCHING_BOUNDS")
        self.assertEqual(result["minimum_coordinate_count"], 1)
        self.assertEqual(result["mandatory_coordinates"], ["0"])


if __name__ == "__main__":
    unittest.main()
