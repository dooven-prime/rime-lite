from __future__ import annotations

from collections import deque
import unittest

from antipodal_partition_cost import (
    antipodal_linear_word, antipodal_partition, audit_antipodal_linear_word,
)
from layer_allocation_geometry import construct_layer_allocation
from rsr2_model import State, replay, seed, step


class AntipodalPartitionCostTests(unittest.TestCase):
    def test_literal_endpoint_complete_events_and_raw_counts(self):
        for m in (*range(1, 33), 50, 100):
            with self.subTest(m=m):
                audit_antipodal_linear_word(m)
        with self.assertRaises(ValueError):
            antipodal_linear_word(0)

    def test_both_phase_coordinate_invariants(self):
        for m in range(1, 17):
            n = 2 * m
            word = antipodal_linear_word(m)
            state = seed(n)
            cursor = 0

            # After k first-pass loads, stored atoms have spacing two.
            for k in range(1, m + 1):
                stop = 1 + 4 * (k - 1)
                state = replay(state, word[cursor:stop])
                cursor = stop
                transferred = {(-j) % n for j in range(k)}
                lower, upper = [()] * n, [()] * n
                for atom in set(range(n)) - transferred:
                    lower[(atom + k - 1) % n] = (atom,)
                for j in range(k):
                    upper[2 * (k - 1 - j)] = ((-j) % n,)
                self.assertEqual(state.layers, (tuple(lower), tuple(upper)))

            # After k second-pass merges, completed pairs are even and the
            # pending mates are odd. The next receiver and mate are forced.
            for k in range(1, m + 1):
                stop = (4 * m - 3) + 6 + 5 * (k - 1)
                state = replay(state, word[cursor:stop])
                cursor = stop
                lower, upper = [()] * n, [()] * n
                for atom in range(1, m - k + 1):
                    lower[atom + m + k - 1] = (atom,)
                for j in range(k):
                    i = (-j) % m
                    upper[2 * (k - 1 - j)] = (i, i + m)
                for j in range(k, m):
                    upper[n + 2 * k - 1 - 2 * j] = ((-j) % n,)
                self.assertEqual(state.layers, (tuple(lower), tuple(upper)))
            self.assertEqual(cursor, len(word))

    def test_minimum_elevator_count_has_an_actual_witness(self):
        # This is a different word: keep one pair below and load the rest.
        # It attains the n-2 transfer-letter bound, not a raw-length optimum.
        for m in range(1, 13):
            state, word = construct_layer_allocation(
                2 * m, antipodal_partition(m), frozenset({m - 1}))
            self.assertEqual(word.count(("v", None)), 2 * m - 2)
            self.assertEqual(state.partition, antipodal_partition(m))

    def test_lower_fusion_gate_on_small_complete_target_pure_graphs(self):
        # Prune only irreversible cross-target fusions. Keep all five actions,
        # every layer allocation, whole-packet transfers, and the F0 observer.
        actions = (("p", 0), ("p", 1), ("d", 0), ("d", 1), ("v", None))
        for m in (1, 2):
            n = 2 * m
            initial = seed(n).layers
            queue = deque([(initial, 0, 0)])
            seen = {(initial, 0)}
            minimum_v = n
            minimum_length = None
            while queue:
                layers, lower_fusions, distance = queue.popleft()
                current = State(n, layers)
                if current.partition == antipodal_partition(m):
                    k0 = sum(bool(packet) for packet in layers[0])
                    self.assertLessEqual(k0, 1)
                    minimum_v = min(minimum_v, n - k0 - lower_fusions)
                    if minimum_length is None:
                        minimum_length = distance
                for action in actions:
                    if action == ("v", None) and (
                            not layers[0][0] or layers[1][0]):
                        continue
                    if action[0] == "d":
                        left, right = layers[action[1]][:2]
                        if left and right and left[0] % m != right[0] % m:
                            continue
                    result = step(current, action)
                    fusion = (action == ("d", 0)
                              and bool(layers[0][0]) and bool(layers[0][1]))
                    next_fusions = lower_fusions + int(fusion)
                    self.assertLessEqual(next_fusions, 1)
                    if fusion:
                        i = layers[0][0][0] % m
                        upper_atoms = {a for packet in layers[1] for a in packet}
                        for j in range(m):
                            if j != i:
                                self.assertTrue(j in upper_atoms or j + m in upper_atoms)
                        arcs = ({(i + d) % n for d in range(1, m)},
                                {(i + m + d) % n for d in range(1, m)})
                        self.assertTrue(any(arc <= upper_atoms for arc in arcs))
                    key = (result.layers, next_fusions)
                    if key not in seen:
                        seen.add(key)
                        queue.append((result.layers, next_fusions, distance + 1))
            self.assertEqual(minimum_v, n - 2)
            if m >= 2:
                self.assertGreaterEqual(minimum_length, 7 * m - 7)


if __name__ == "__main__":
    unittest.main()
