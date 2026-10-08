#!/usr/bin/env python3
"""Produce bounded raw/group consistency controls, not an all-g proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from math import lcm
from pathlib import Path

from audit_scope import (
    AFFINE2, CHECKS, CLAIM_BOUNDARY, CYCLE, DOMAIN_COUNTS, IDENTITY,
    MATCHED_G_VALUES, PAIRS, RESULT_SCHEMA, RESULT_STATUS, THREE_CYCLE,
    TRANSPOSITION, Branch, branches, scope_record,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[q] for q in right)


def group(generators: tuple[tuple[int, ...], ...]) -> set[tuple[int, ...]]:
    found = {IDENTITY}
    queue = deque([IDENTITY])
    while queue:
        current = queue.popleft()
        for generator in generators:
            child = compose(generator, current)
            if child not in found:
                found.add(child)
                queue.append(child)
    return found


def mapping(branch: Branch) -> dict[int, int]:
    g = branch.g
    result = {
        t * g: (branch.punctured[t - 1] + 1) * g for t in range(1, 5)
    }
    for j, (target, sigma) in enumerate(
        zip(branch.targets, branch.restrictions, strict=True), 1
    ):
        result.update({j + t * g: target + sigma[t] * g for t in range(5)})
    require(set(result) == set(result.values()) == set(range(1, 5 * g)),
            "branch does not permute E")
    return result


def placed(g: int, j: int, kappa: tuple[int, ...] = IDENTITY) -> tuple[int, ...]:
    return tuple(j + t * g for t in kappa)


def preterminal(state: tuple[int, ...], a: dict[int, int], r: int, g: int) -> tuple[int, ...]:
    return tuple((a[q] + r) % (5 * g) for q in state)


def step(state: tuple[int, ...], a: dict[int, int], r: int, g: int) -> tuple[int, ...] | None:
    moved = preterminal(state, a, r, g)
    collapsed = tuple(g if q == 0 else q for q in moved)
    return collapsed if len(set(collapsed)) == 5 else None


def reachable(start: tuple[int, ...], a: dict[int, int], g: int) -> set[tuple[int, ...]]:
    found = {start}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        require(len({q % g for q in state}) == 1 and state[0] % g != 0,
                "reachable state left the ordinary lanes")
        for r in range(5 * g):
            child = step(state, a, r, g)
            should_enable = (a[state[0]] + r) % g != 0
            require((child is not None) == should_enable, "raw guard differs from lane guard")
            if child is not None and child not in found:
                found.add(child)
                queue.append(child)
    return found


def permutation_order(a: dict[int, int]) -> int:
    remaining = set(a)
    order = 1
    while remaining:
        start = min(remaining)
        q, length = start, 0
        while q in remaining:
            remaining.remove(q)
            q = a[q]
            length += 1
        require(q == start, "invalid permutation cycle")
        order = lcm(order, length)
    return order


def run_word(state: tuple[int, ...], word: tuple[int, ...],
             a: dict[int, int], g: int) -> tuple[int, ...]:
    for r in word:
        child = step(state, a, r, g)
        require(child is not None, "constructed word used a disabled return")
        state = child
    return state


def actual_words(branch: Branch, a: dict[int, int]) -> dict[str, int]:
    g, m = branch.g, permutation_order(a)
    inverse = (0,) * (m - 1)
    words = []
    for j in range(1, g):
        for h in range(1, g):
            word = inverse + ((h - j) % (5 * g),)
            require(run_word(placed(g, j), word, a, g) == placed(g, h),
                    "actual relocation failed")
            words.append(word)
    for h in range(1, g):
        phase = inverse + (g,)
        require(run_word(placed(g, h), phase, a, g) == placed(g, h, CYCLE),
                "actual phase word failed")
        words.append(phase)
        for j in range(1, g):
            word = (inverse + ((j - h) % (5 * g),) + (0,)
                    + inverse + ((h - branch.targets[j - 1]) % (5 * g),))
            require(run_word(placed(g, h), word, a, g)
                    == placed(g, h, branch.restrictions[j - 1]),
                    "actual local-generator loop failed")
            words.append(word)
    return {
        "branch_order": m,
        "executed_words": len(words),
        "maximum_word_length": max(map(len, words)),
    }


def phase_key(state: tuple[int, ...], g: int) -> tuple[int, tuple[int, ...]]:
    lane = state[0] % g
    indices = tuple((q - lane) // g for q in state)
    return lane, min(tuple((t + offset) % 5 for t in indices) for offset in range(5))


def phase_check(states: set[tuple[int, ...]], a: dict[int, int],
                branch: Branch, generated: set[tuple[int, ...]]) -> tuple[int, bool, object]:
    g = branch.g
    classes = {phase_key(state, g) for state in states}
    require(len(classes) == (g - 1) * len(generated) // 5, "right-coset count drift")
    outputs: dict[tuple, tuple] = {}
    witness = None
    for state in sorted(states):
        source_class = phase_key(state, g)
        for r in range(5 * g):
            child = step(state, a, r, g)
            if child is None:
                continue
            key, child_class = (source_class, r), phase_key(child, g)
            if key in outputs and outputs[key][1] != child_class and witness is None:
                witness = {
                    "label": r,
                    "source_representatives": [list(outputs[key][0]), list(state)],
                    "output_phase_classes": [
                        [outputs[key][1][0], list(outputs[key][1][1])],
                        [child_class[0], list(child_class[1])],
                    ],
                }
            outputs.setdefault(key, (state, child_class))
    phase_group = group((CYCLE,))
    normalizes = all(
        {compose(sigma, h) for h in phase_group}
        == {compose(h, sigma) for h in phase_group}
        for sigma in branch.restrictions
    )
    require(normalizes == (witness is None), "deterministic phase condition drift")
    return len(classes), normalizes, witness


def spectrum(terminals: set[tuple[int, ...]], g: int) -> dict[tuple[int, int], set[tuple[int, ...]]]:
    result = {pair: set() for pair in PAIRS}
    for mu in terminals:
        pair = tuple(i for i, q in enumerate(mu) if q in (0, g))
        require(len(pair) == 2, "terminal placement lacks exactly two kernel lineages")
        result[pair].add(tuple(mu[i] for i in range(5) if i not in pair))
    return result


def spectrum_rows(value: dict[tuple[int, int], set[tuple[int, ...]]]) -> list[dict[str, object]]:
    return [{"pair": list(pair), "placements": [list(s) for s in sorted(value[pair])]}
            for pair in PAIRS]


def analyze(branch: Branch, source: int) -> tuple[dict[str, object], set, dict]:
    g, a = branch.g, mapping(branch)
    generated = group((CYCLE,) + branch.restrictions)
    states = reachable(placed(g, source), a, g)
    expected = {placed(g, j, kappa) for j in range(1, g) for kappa in generated}
    require(states == expected, "reachable-injection theorem differs from raw BFS")
    terminals = set()
    for state in states:
        for u in range(5 * g):
            mu = preterminal(state, a, u, g)
            if {0, g}.issubset(mu):
                terminals.add(mu)
    predicted = {tuple(t * g for t in eta) for eta in generated}
    require(terminals == predicted, "terminal-placement theorem differs from actual events")
    actual_spectra = spectrum(terminals, g)
    require(actual_spectra == spectrum(predicted, g), "survivor set drift")
    kernel_swap = TRANSPOSITION in generated
    for pair in PAIRS:
        fiber = {eta for eta in generated if {eta[i] for i in pair} == {0, 1}}
        require(len(fiber) == len(actual_spectra[pair]) * (1 + kernel_swap),
                "survivor restriction multiplicity drift")
    phase_count, normalizes, witness = phase_check(states, a, branch, generated)
    record = {
        **branch.record(),
        "source_lane": source,
        "group_order": len(generated),
        "reachable_injections": len(states),
        "phase_classes": phase_count,
        "terminal_placements": len(terminals),
        "deterministic_phase_descent": normalizes,
        "phase_non_descent_witness": witness,
        "kernel_swap_in_group": kernel_swap,
        "actual_word_controls": actual_words(branch, a),
        "survivor_counts": [len(actual_spectra[pair]) for pair in PAIRS],
        "fused_pairs": [list(pair) for pair in PAIRS if actual_spectra[pair]],
        "digests": {
            "group": digest([list(k) for k in sorted(generated)]),
            "reachable_injections": digest([list(s) for s in sorted(states)]),
            "terminal_placements": digest([list(mu) for mu in sorted(terminals)]),
            "survivor_spectra": digest(spectrum_rows(actual_spectra)),
        },
    }
    return record, states, actual_spectra


def parity(sigma: tuple[int, ...]) -> int:
    return sum(sigma[i] > sigma[j] for i, j in PAIRS) % 2


def unsigned(branch: Branch) -> list[list[int]]:
    return [[j, r, (branch.targets[j - 1] + r) % branch.g]
            for j in range(1, branch.g) for r in range(5 * branch.g)]


def matched(g: int) -> dict[str, object]:
    rows = {}
    for name, sigma in (("F20", AFFINE2), ("A5", THREE_CYCLE), ("S5", TRANSPOSITION)):
        branch = Branch(f"matched-g{g}-{name}", g, tuple(range(1, g)),
                        (sigma,) + (IDENTITY,) * (g - 2), (0, 1, 2, 3))
        rows[name] = (branch, *analyze(branch, 1))
    f_branch, f_record, _, f_spectra = rows["F20"]
    _, a_record, a_states, a_spectra = rows["A5"]
    s_branch, s_record, s_states, s_spectra = rows["S5"]
    require(unsigned(f_branch) == unsigned(s_branch), "matched unsigned graph mismatch")
    require(tuple(map(parity, f_branch.restrictions))
            == tuple(map(parity, s_branch.restrictions)), "matched parity mismatch")
    require(all(f_spectra[pair] and s_spectra[pair] for pair in PAIRS),
            "matched pair coverage mismatch")
    require(all(len(f_spectra[pair]) == 2 and len(s_spectra[pair]) == 6 for pair in PAIRS),
            "F20/S5 survivor control failed")
    require(a_states != s_states and a_spectra == s_spectra,
            "A5/S5 full survivor-set equality failed")
    require((f_record["group_order"], a_record["group_order"], s_record["group_order"])
            == (20, 60, 120), "matched group generation drift")
    return {
        "g": g,
        "F20_S5": {
            "unsigned_labelled_graph_equal": True,
            "local_parity_equal": True,
            "fused_pairs_equal": [list(pair) for pair in PAIRS],
            "survivor_counts": {"F20": [2] * 10, "S5": [6] * 10},
            "survivor_digests": {
                "F20": f_record["digests"]["survivor_spectra"],
                "S5": s_record["digests"]["survivor_spectra"],
            },
        },
        "A5_S5": {
            "reachable_counts": {"A5": len(a_states), "S5": len(s_states)},
            "complete_survivor_sets_equal": True,
            "survivors_per_pair": 6,
            "common_survivor_digest": a_record["digests"]["survivor_spectra"],
        },
    }


def build_record() -> dict[str, object]:
    catalogue = branches()
    cases = [analyze(branch, source)[0]
             for branch in catalogue for source in range(1, branch.g)]
    domains = []
    for expected in DOMAIN_COUNTS:
        g = expected["g"]
        row = {"g": g, "n": 5 * g, "delta": g,
               "branches": sum(branch.g == g for branch in catalogue),
               "source_cases": sum(case["g"] == g for case in cases)}
        require(row == expected, "fixed finite catalogue coverage drift")
        domains.append(row)
    return {
        "schema": RESULT_SCHEMA,
        "status": RESULT_STATUS,
        "scope": scope_record(),
        "checks": list(CHECKS),
        "claim_boundary": CLAIM_BOUNDARY,
        "domains": domains,
        "cases": cases,
        "matched_controls": [matched(g) for g in MATCHED_G_VALUES],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="explicitly write a new bounded result")
    args = parser.parse_args()
    result = build_record()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8", newline="\n")
    print(f"PASS: bounded control; {sum(r['branches'] for r in result['domains'])} branches, "
          f"{len(result['cases'])} source cases, "
          f"{len(result['matched_controls'])} matched g-domains")


if __name__ == "__main__":
    main()
