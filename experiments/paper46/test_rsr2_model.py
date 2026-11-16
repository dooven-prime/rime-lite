from __future__ import annotations

import unittest
from itertools import permutations

from rsr2_model import (
    construct_partition,
    construct_partition_interleaved,
    replay,
    seed,
    set_partitions,
)


def power(letter: str, layer: int, count: int):
    return [(letter, layer)] * count


class RSR2ModelTests(unittest.TestCase):
    def test_short_crossing_witness(self):
        word = [("v", None), ("p", 1), ("d", 0), ("p", 0),
                ("d", 0), ("p", 0), ("v", None), ("d", 1)]
        state = replay(seed(4), word)
        self.assertEqual(state.layers[0], ((), (1, 3), (), ()))
        self.assertEqual(state.layers[1], ((0, 2), (), (), ()))
        self.assertEqual(state.partition, ((0, 2), (1, 3)))
        self.assertEqual([event.kind for event in state.events],
                         ["vertical", "fusion", "vertical", "fusion"])

    def test_crossing_witness(self):
        n = 4
        prefixes = [
            power("p", 0, 3) + [("v", None)],
            power("p", 0, 3) + [("v", None)] + power("p", 1, 1)
            + power("p", 0, 2) + [("v", None)],
        ]
        first, second = (replay(seed(n), prefix) for prefix in prefixes)
        self.assertEqual(first.layers[0], ((), (2,), (3,), (0,)))
        self.assertEqual(first.layers[1], ((1,), (), (), ()))
        self.assertEqual(second.layers[0], ((), (0,), (), (2,)))
        self.assertEqual(second.layers[1], ((3,), (1,), (), ()))

        word = prefixes[1] + [("d", 1)]
        after_layer1_fusion = replay(seed(n), word)
        self.assertEqual(after_layer1_fusion.layers[0], ((), (0,), (), (2,)))
        self.assertEqual(after_layer1_fusion.layers[1], ((1, 3), (), (), ()))

        word += [("d", 0), ("p", 0), ("d", 0)]
        state = replay(seed(n), word)
        self.assertEqual(state.partition, ((0, 2), (1, 3)))
        self.assertEqual(state.layers[0][0], (0, 2))
        self.assertEqual(state.layers[1][0], (1, 3))
        self.assertEqual([event.kind for event in state.events],
                         ["vertical", "vertical", "fusion", "fusion"])
        self.assertEqual([event.layer for event in state.events if event.kind == "fusion"],
                         [1, 0])

    def test_all_partitions_through_six(self):
        for n in range(2, 7):
            partitions = list(set_partitions(n))
            self.assertEqual(len(partitions), [0, 0, 2, 5, 15, 52, 203][n])
            for target in partitions:
                with self.subTest(n=n, target=target):
                    state, word = construct_partition(n, target)
                    self.assertEqual(state.partition, target)
                    self.assertEqual(sum(event.kind == "vertical" for event in state.events), n)
                    self.assertEqual(sum(event.kind == "fusion" for event in state.events),
                                     n - len(target))
                    d = n - len(target)
                    bound = n * n + n - 1 + 2 * n * d + d * (d - 1) // 2
                    self.assertLessEqual(len(word), bound)

    def test_interleaved_bell_construction_through_seven(self):
        for n in range(2, 8):
            for target in set_partitions(n):
                with self.subTest(n=n, target=target):
                    state, word = construct_partition_interleaved(n, target)
                    self.assertEqual(replay(seed(n), word), state)
                    self.assertEqual(state.partition, target)
                    self.assertEqual(state.layers[0], ((),) * n)
                    self.assertEqual(
                        sum(event.kind == "vertical" for event in state.events), n
                    )
                    self.assertEqual(
                        sum(event.kind == "fusion" for event in state.events),
                        n - len(target),
                    )
                    self.assertLessEqual(
                        len(word), n * n + 2 * n - len(target) - 1
                    )

    def test_permutation_loading_through_six(self):
        from rsr2_model import load_permutation

        for n in range(2, 7):
            for sigma in permutations(range(n)):
                with self.subTest(n=n, sigma=sigma):
                    state, word = load_permutation(n, sigma)
                    self.assertEqual(replay(seed(n), word), state)
                    self.assertEqual(
                        state.layers,
                        (((),) * n, tuple((atom,) for atom in sigma)),
                    )
                    self.assertFalse(any(event.kind == "fusion" for event in state.events))
                    self.assertEqual(
                        sum(event.kind == "vertical" for event in state.events), n
                    )
                    self.assertLessEqual(len(word), n * n + n - 1)


if __name__ == "__main__":
    unittest.main()
