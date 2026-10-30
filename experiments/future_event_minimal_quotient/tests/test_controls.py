"""Small hostile regressions for the manuscript-owned bounded package."""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit import example, report  # noqa: E402
from model import State, graph, packets, run, seed, step  # noqa: E402


class ControlTests(unittest.TestCase):
    def test_nonfusion_d_moves_into_hole(self):
        following, output, fusion = step(3, State((2, 1, 2)), "d")
        self.assertEqual(following.sites, (2, 0, 2))
        self.assertIsNone(output)
        self.assertIsNone(fusion)

    def test_introduction_has_two_actual_histories(self):
        control = example()
        first, _ = run(5, seed(5), control["word_one"])
        second, _ = run(5, seed(5), control["word_two"])
        self.assertEqual(first.sites, second.sites)
        self.assertEqual(first.origin, second.origin)
        self.assertNotEqual(first.chain, second.chain)
        self.assertEqual(len(packets(first.sites)), 2)

    def test_exhaustive_small_domain(self):
        data = report()
        self.assertEqual([row["reachable_retained_states"]
                          for row in data["controls"]], [30, 176, 920])
        self.assertEqual([row["future_classes"] for row in data["controls"]],
                         [10, 65, 336])
        self.assertEqual([row["full_classes"] for row in data["controls"]],
                         [16, 89, 486])
        self.assertEqual([row["candidate_class_pairs_checked"]
                          for row in data["controls"]], [45, 2080, 56280])

    def test_seed_is_in_generated_graph(self):
        states, _transitions, words = graph(3)
        self.assertEqual(states[0], seed(3))
        self.assertEqual(words[states[0]], "")


if __name__ == "__main__":
    unittest.main()
