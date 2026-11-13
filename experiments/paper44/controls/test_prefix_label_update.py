"""Bounded correspondence checks for the manuscript's visible-event contract.

The standalone updater below uses only a label and an emitted event. It is
compared against actual generated successors, without modifying the saved
minimization report or its transition code.
"""

import unittest

import minimum_sufficient_quotient as quotient
import prefix_observer_spectrum_control as prefix
import shortest_summary_search as search


def full_origin(origin, F):
    if origin is None:
        return None
    letter, (left_port, left), (right_port, right), target = origin
    return letter, left_port, right_port, left, right, target, tuple(sorted(F))


def semantic_label(state, depth, F):
    _placement, origin, chain = state
    if origin is None:
        return None
    marker = "short" if len(chain) < depth else "saturated"
    return full_origin(origin, F), chain[:depth], marker


def update_label(label, event, depth):
    if event is None:
        return label
    kind, record = event
    if kind == "registration":
        if label is not None:
            raise ValueError("registration requires an unregistered label")
        return record, (), "short"
    if kind != "selected_absorption" or label is None:
        raise ValueError("absorption requires prior registration")
    origin, retained, marker = label
    if marker == "saturated":
        return label
    retained += (record,)
    marker = "short" if len(retained) < depth else "saturated"
    return origin, retained, marker


def event_from_current_ports(state, letter, F):
    placement, origin, _chain = state
    packets = dict(placement)
    if letter != "d" or 0 not in packets or 1 not in packets:
        return None
    left, right = packets[0], packets[1]
    fresh = frozenset(left) | frozenset(right)
    record = "d", 0, 1, left, right, 0, tuple(sorted(fresh))
    if origin is None:
        return ("registration", record) if fresh == F else None
    if F <= frozenset(left) or F <= frozenset(right):
        return "selected_absorption", record
    return None


class PrefixLabelUpdateTests(unittest.TestCase):
    def test_generated_event_and_label_update_correspondence(self):
        coverage = set()
        for n in range(3, 8):
            F = frozenset((0, 1))
            states, _ = search.bfs_distances(
                n, F, max_states=250000, retain_predecessors=False)
            for state in states:
                for letter in search.RAW_LETTERS:
                    successor = search.successor(n, F, state, letter)
                    event = quotient._event_output(F, state, successor)
                    self.assertEqual(event, event_from_current_ports(state, letter, F))
                    if event is not None:
                        kind, record = event
                        coverage.add(kind)
                        fresh = frozenset(record[-1])
                        if kind == "registration":
                            self.assertEqual(fresh, F)
                            self.assertEqual(successor[2], ())
                        else:
                            self.assertLess(F, fresh)
                    elif len(successor[0]) < len(state[0]) and state[1] is not None:
                        coverage.add("unrelated_fusion_is_null")
                    for depth in range(1, n):
                        label = semantic_label(state, depth, F)
                        expected = semantic_label(successor, depth, F)
                        self.assertEqual(update_label(label, event, depth), expected)
                        raw_report = prefix.current_report(state, depth)
                        if label is None:
                            self.assertEqual(raw_report, ("unregistered",))
                        else:
                            self.assertEqual(full_origin(raw_report[1], F), label[0])
                            self.assertEqual(raw_report[2], label[1])
                            marker = "short" if raw_report[3] == "stopped" else raw_report[3]
                            self.assertEqual(marker, label[2])
                            if event is not None and label[2] == "saturated":
                                coverage.add("visible_absorption_after_saturation")
        self.assertEqual(coverage, {
            "registration", "selected_absorption", "unrelated_fusion_is_null",
            "visible_absorption_after_saturation"})


if __name__ == "__main__":
    unittest.main()
