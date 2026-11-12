"""Exact finite identities supporting the supercritical-memory corollary.

These algebraic tests do not prove the asymptotic result or extend the
saved generated-domain replay report.
"""

from fractions import Fraction
from math import comb
import unittest

from prefix_observer_spectrum_control import exact_count


def chain_length_counts(n):
    outside = n - 2
    return [n * 2**length * comb(2 * outside, outside - length)
            for length in range(outside + 1)]


def checkpoint_summary_count(n):
    outside = n - 2
    return n * (comb(2 * outside, outside) + 2 * sum(
        3**(checkpoint - 1) * comb(2 * outside - checkpoint, outside - checkpoint)
        for checkpoint in range(1, outside + 1)))


class SupercriticalMemoryTests(unittest.TestCase):
    def test_critical_window_exact_decomposition(self):
        def choose(n, k):
            return comb(n, k) if 0 <= k <= n else 0

        for n in range(3, 63):
            outside = n - 2
            profile = chain_length_counts(n)
            registerable = n * comb(2 * outside, outside - 1)
            for depth in range(1, outside + 1):
                short = sum(2**length * comb(outside - 1, length - 1)
                            for length in range(1, depth))
                edge = (choose(2 * outside + 1, outside - depth)
                        + choose(2 * outside + 1, outside - depth - 1)
                        - choose(outside, depth) - choose(outside, depth + 1))
                expected = (sum(profile[:depth]) - (n - 1) * short
                            + n * 2**depth * edge
                            + 2**depth * choose(outside, depth))
                observed = exact_count(n, depth) - 1 - registerable
                self.assertEqual(observed, expected, (n, depth))

    def test_weighted_chain_length_convolution(self):
        for outside in range(1, 51):
            for length in range(1, outside + 1):
                observed = sum(
                    comb(checkpoint - 1, length - 1)
                    * comb(2 * outside - checkpoint, outside - checkpoint)
                    for checkpoint in range(length, outside + 1))
                self.assertEqual(observed, comb(2 * outside, outside - length))

    def test_complete_summary_profile(self):
        for n in range(3, 63):
            self.assertEqual(sum(chain_length_counts(n)), checkpoint_summary_count(n))

    def test_exact_binomial_reweighting(self):
        for n in range(3, 43):
            outside = n - 2
            mass = n * Fraction(9, 2)**outside
            for length, count in enumerate(chain_length_counts(n)):
                k = outside - length
                probability = (comb(2 * outside, k)
                               * Fraction(1, 3)**k
                               * Fraction(2, 3)**(2 * outside - k))
                self.assertEqual(Fraction(count, 1) / mass, probability)
            ratio = Fraction(checkpoint_summary_count(n), 1) / mass
            self.assertLessEqual(1 - Fraction(8, 9)**outside, ratio)
            self.assertLessEqual(ratio, 1)

    def test_deficit_bound_at_every_finite_depth(self):
        for n in range(3, 53):
            outside = n - 2
            profile = chain_length_counts(n)
            summary = sum(profile)
            common = 1 + n * comb(2 * outside, outside - 1)
            full = common + summary
            phase_loss = (n - 1) * 2 * 3**(outside - 1)
            for depth in range(1, outside + 2):
                loss = full - exact_count(n, depth)
                long_histories = sum(profile[depth + 1:])
                self.assertGreaterEqual(loss, phase_loss)
                self.assertLessEqual(loss, phase_loss + long_histories)
                if depth >= outside:
                    self.assertEqual(loss, phase_loss)


if __name__ == "__main__":
    unittest.main()
