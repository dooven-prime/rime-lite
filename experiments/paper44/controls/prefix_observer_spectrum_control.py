"""Bounded minimization controls for the variable-depth prefix observer note."""

from fractions import Fraction
from math import comb, exp, log
from pathlib import Path
import argparse
import json

import minimum_sufficient_quotient as quotient
import shortest_summary_search as search


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def prefix_labels(r, depth):
    if r < 0 or depth < 1:
        raise ValueError("r >= 0 and positive prefix depth are required")
    if r == 0:
        return 1
    saturated = (1 << depth) * choose(r + 1, depth + 1)
    stopped = sum((1 << length) * choose(r - 1, length - 1)
                  for length in range(1, min(depth, r + 1)))
    return saturated + stopped


def terminal_labels(outside, depth):
    if outside < 1 or depth < 1:
        raise ValueError("positive outside size and prefix depth are required")
    return ((1 << depth) * choose(outside, depth)
            + sum((1 << length) * choose(outside - 1, length - 1)
                  for length in range(1, min(depth, outside + 1))))


def exact_count(n, depth):
    if n < 3 or depth < 1:
        raise ValueError("n >= 3 and positive prefix depth are required")
    outside = n - 2
    registered = n * sum(prefix_labels(r, depth) * comb(2 * outside - r, outside - r)
                         for r in range(outside))
    return (1 + n * comb(2 * outside, outside - 1)
            + terminal_labels(outside, depth) + registered)


def predicted_base(theta):
    theta = float(theta)
    if not 0 <= theta <= 1:
        raise ValueError("theta must be in [0,1]")
    beta = min(theta, 1 / 3)
    return exp((2 + beta) * log(2) - (1 + beta) * log(1 + beta)
               - (1 - beta) * log(1 - beta))


def current_report(state, depth):
    _placement, origin, chain = state
    if origin is None:
        return ("unregistered",)
    marker = "stopped" if len(chain) < depth else "saturated"
    return ("registered", origin, chain[:depth], marker)


def canonical_ids(signatures):
    ids = {}
    return [ids.setdefault(signature, len(ids)) for signature in signatures]


def minimize(states, edges, outputs, depth):
    blocks = canonical_ids(current_report(state, depth) for state in states)
    rounds = 0
    while True:
        refined = canonical_ids((blocks[i], outputs[i], tuple(blocks[t] for t in edges[i]))
                                for i in range(len(states)))
        rounds += 1
        if refined == blocks:
            return blocks, rounds
        blocks = refined


def expected_key(state, depth):
    placement, origin, _chain = state
    if origin is None:
        blocks = {frozenset(block) for _site, block in placement}
        if frozenset((0,)) in blocks and frozenset((1,)) in blocks:
            return ("registerable", placement)
        return ("dead",)
    if len(placement) == 1:
        return ("terminal", current_report(state, depth))
    return ("registered", placement, current_report(state, depth))


def check_partition(states, blocks, depth):
    forward, backward = {}, {}
    for state, block in zip(states, blocks):
        key = expected_key(state, depth)
        if forward.setdefault(block, key) != key or backward.setdefault(key, block) != block:
            raise AssertionError("minimized partition differs from the predicted normal form")


def finite_control(n):
    F = search.validate_input(n, (0, 1))
    distances, _ = search.bfs_distances(n, F, max_states=250000, retain_predecessors=False)
    states = list(distances)
    index = {state: i for i, state in enumerate(states)}
    edges, outputs = [], []
    for state in states:
        successors = [search.successor(n, F, state, letter) for letter in search.RAW_LETTERS]
        edges.append(tuple(index[target] for target in successors))
        outputs.append(tuple(quotient._event_output(F, state, target) for target in successors))
    rows = []
    for depth in range(1, n):
        blocks, rounds = minimize(states, edges, outputs, depth)
        check_partition(states, blocks, depth)
        observed = len(set(blocks))
        expected = exact_count(n, depth)
        if observed != expected:
            raise AssertionError((n, depth, observed, expected))
        rows.append({"depth": depth, "classes": observed, "refinement_rounds": rounds,
                     "full_partition_matches": True})
    return {"n": n, "reachable_consumer_states": len(states), "depths": rows}


def algebra_controls():
    for n in range(3, 101):
        if exact_count(n, 1) != quotient.first_absorption_prefix_quotient_count_closed(n):
            raise AssertionError("first-prefix recovery failed")
        outside = n - 2
        if terminal_labels(outside, 2) != 2 + 2 * outside * (outside - 1):
            raise AssertionError("second-prefix terminal recovery failed")
        for r in range(outside):
            expected = 1 if r == 0 else 2 + 2 * r * (r * r - 1) // 3
            if prefix_labels(r, 2) != expected:
                raise AssertionError("second-prefix nonterminal recovery failed")
        summary = n * (comb(2 * outside, outside) + 2 * sum(
            3 ** (b - 1) * comb(2 * outside - b, outside - b)
            for b in range(1, outside + 1)))
        saturated = (1 + n * comb(2 * outside, outside - 1) + summary
                     - (n - 1) * 2 * 3 ** (outside - 1))
        if exact_count(n, outside) != saturated or exact_count(n, outside + 1) != saturated:
            raise AssertionError("full-memory endpoint recovery failed")


def growth_controls():
    rows = []
    for theta in (Fraction(1, 12), Fraction(1, 6), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2)):
        samples = []
        for n in (64, 128, 256):
            depth = (theta.numerator * n) // theta.denominator
            samples.append({"n": n, "depth": depth, "count_root": exp(log(exact_count(n, depth)) / n)})
        rows.append({"theta": str(theta), "proved_rate_in_note": predicted_base(theta),
                     "finite_formula_samples_not_a_limit_proof": samples})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 3 <= args.max_n <= 7:
        raise ValueError("this bounded control is restricted to 3 <= max-n <= 7")
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)
    algebra_controls()
    controls = []
    for n in range(3, args.max_n + 1):
        row = finite_control(n)
        controls.append(row)
        print(json.dumps(row), flush=True)
    report = {"status": "PASS_BOUNDED_PREFIX_OBSERVER_CONTROL", "evidence": "BOUNDED_CONSISTENCY_ONLY",
              "finite_models": controls, "algebra_recovery_range": [3, 100],
              "growth_samples": growth_controls(), "kernel_formalization_claimed": False}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "models": len(controls),
                      "depth_cases": sum(len(row["depths"]) for row in controls)}))


if __name__ == "__main__":
    main()
