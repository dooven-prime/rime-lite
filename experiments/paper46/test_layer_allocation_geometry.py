from __future__ import annotations

import unittest
from itertools import permutations, product

from layer_allocation_geometry import (
    audit_reachable_geometry, construct_layer_allocation, lower_source_order_holds,
    minimum_transferred_mass, retention_admissible,
)
from rsr2_model import State, replay, seed, set_partitions


class LayerAllocationGeometryTests(unittest.TestCase):
    def test_crossing_and_nested_retention_obstructions(self):
        crossing = ((0, 2), (1, 3))
        self.assertFalse(retention_admissible(crossing, frozenset({0, 1})))
        self.assertEqual(minimum_transferred_mass(crossing)[0], 2)
        nested = ((0, 5), (1, 4), (2, 3))
        # Every pair can remain lower together, but all three cannot.
        for omitted in range(3):
            self.assertTrue(retention_admissible(nested, frozenset(set(range(3)) - {omitted})))
        self.assertFalse(retention_admissible(nested, frozenset(range(3))))
        self.assertEqual(minimum_transferred_mass(nested)[0], 2)
        with self.assertRaises(ValueError):
            construct_layer_allocation(4, crossing, frozenset({0, 1}))

    def test_interval_and_physical_order_are_both_checked(self):
        self.assertFalse(lower_source_order_holds(
            State(4, (((0, 2), (1, 3), (), ()), ((),) * 4))))
        self.assertFalse(lower_source_order_holds(
            State(4, (((0,), (2,), (1,), (3,)), ((),) * 4))))
        self.assertTrue(lower_source_order_holds(
            State(4, (((1, 3), (), (), ()), ((0, 2), (), (), ())))))

    def test_all_admissible_allocations_through_six(self):
        for n in range(2, 7):
            for target in set_partitions(n):
                for mask in range(1 << len(target)):
                    retained = frozenset(i for i in range(len(target)) if mask & (1 << i))
                    if not retention_admissible(target, retained):
                        continue
                    with self.subTest(n=n, target=target, retained=retained):
                        state, word = construct_layer_allocation(n, target, retained)
                        self.assertEqual(replay(seed(n), word), state)
                        self.assertEqual(state.partition, target)
                        self.assertEqual(
                            {packet for packet in state.layers[0] if packet},
                            {target[i] for i in retained},
                        )
                        transferred_mass = sum(len(event.packet) for event in state.events
                                               if event.kind == "vertical")
                        self.assertEqual(transferred_mass,
                                         sum(len(packet) for packet in state.layers[1]))
                        self.assertEqual(sum(event.kind == "fusion" for event in state.events),
                                         n - len(target))
                        current = seed(n)
                        for action in word:
                            current = replay(current, (action,))
                            self.assertTrue(lower_source_order_holds(current))

    def test_exhaustive_physical_graph_through_four(self):
        for n, bell in ((2, 2), (3, 5), (4, 15)):
            with self.subTest(n=n):
                receipt = audit_reachable_geometry(n)
                self.assertEqual(receipt["partitions"], bell)

    def test_antipodal_minimum_within_block_contiguous_loading(self):
        for m in range(1, 6):
            n = 2 * m
            best = None
            for order in permutations(range(m)):
                for orientations in product((False, True), repeat=m):
                    atoms = []
                    for pair, reverse in zip(order, orientations):
                        atoms.extend((pair + m, pair) if reverse else (pair, pair + m))
                    cost = (-atoms[0]) % n + sum(
                        (a - b) % n for a, b in zip(atoms, atoms[1:]))
                    best = cost if best is None else min(best, cost)
            self.assertEqual(best, m * m + m - 1)

    def test_antipodal_attaining_words_are_actual_executions(self):
        for m in range(1, 21):
            n = 2 * m
            atoms = [0, m]
            for _ in range(m - 1):
                first = (atoms[-1] - 1) % n
                atoms.extend((first, (first + m) % n))
            self.assertEqual(sorted(atoms), list(range(n)))
            state = seed(n)
            word = []
            for i, atom in enumerate(atoms):
                route = [("p", 1)] if i else []
                route += [("p", 0)] * ((-state.layers[0].index((atom,))) % n)
                route.append(("v", None))
                if i % 2:
                    route.append(("d", 1))
                state = replay(state, route)
                word.extend(route)
            self.assertEqual(state.partition, tuple((i, i + m) for i in range(m)))
            self.assertEqual(sum(action == ("p", 0) for action in word), m * m + m - 1)
            self.assertEqual(len(word), m * m + 6 * m - 2)


if __name__ == "__main__":
    unittest.main()
