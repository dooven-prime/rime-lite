#!/usr/bin/env python3
"""Exact rank-drop dynamic potential for synchronizing automata.

The construction separates rank-preserving motion from strict rank drops.  For
every reachable subset S, it computes shortest distances inside the directed
rank-|S| layer to every available collision boundary edge.  Dynamic
programming over decreasing ranks then assigns a path-compatible potential

    Psi({q}) = 0,
    Psi(S) = min_e (distance_to_e + 1 + Psi(target(e))).

The finite-state theorem is proved in SOF_RANK_COLLAPSE.md.  This file is an
exact certificate producer, not a claim of a general quadratic inequality.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Iterable

from registry import (
    Transition,
    Word,
    apply_word,
    payload_digest,
    reachable_subset_automaton,
    shortest_subset_reset_word,
)


def _layer_escape_options(
    subset: tuple[int, ...],
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
) -> list[dict]:
    """Enumerate shortest prefix-to-exit options in the fixed-rank layer."""
    rank = len(subset)
    distance = {subset: 0}
    words: dict[tuple[int, ...], Word] = {subset: tuple()}
    queue = deque([subset])
    while queue:
        current = queue.popleft()
        for letter, target in enumerate(edges[current]):
            if len(target) != rank or target in distance:
                continue
            distance[target] = distance[current] + 1
            words[target] = words[current] + (letter,)
            queue.append(target)

    options: list[dict] = []
    for source, prefix_distance in sorted(distance.items()):
        for letter, target in enumerate(edges[source]):
            if len(target) < rank:
                options.append(
                    {
                        "boundary_source": list(source),
                        "letter": letter,
                        "target": list(target),
                        "prefix_word": list(words[source]),
                        "prefix_distance": prefix_distance,
                        "segment_length": prefix_distance + 1,
                    }
                )
    options.sort(
        key=lambda item: (
            item["segment_length"],
            item["prefix_word"],
            item["letter"],
            item["target"],
        )
    )
    return options


def rank_drop_dynamic_potential(transition: Transition) -> dict:
    """Compute the exact rank-drop potential and its local descent certificate."""
    distance, _shortest_words, edges = reachable_subset_automaton(transition)
    subsets_by_rank: dict[int, list[tuple[int, ...]]] = {}
    for subset in distance:
        subsets_by_rank.setdefault(len(subset), []).append(subset)

    potential: dict[tuple[int, ...], int | None] = {}
    policy: dict[tuple[int, ...], dict | None] = {}
    for subset in subsets_by_rank.get(1, []):
        potential[subset] = 0
        policy[subset] = None

    for current_rank in range(2, len(transition[0]) + 1):
        for subset in sorted(subsets_by_rank.get(current_rank, [])):
            candidates = []
            for option in _layer_escape_options(subset, edges):
                target = tuple(option["target"])
                if potential.get(target) is None:
                    continue
                candidates.append(
                    (
                        option["segment_length"] + potential[target],
                        option["segment_length"],
                        option["prefix_word"],
                        option["letter"],
                        option["target"],
                        option,
                    )
                )
            if not candidates:
                potential[subset] = None
                policy[subset] = None
                continue
            candidates.sort(key=lambda item: item[:-1])
            value, _segment, _word, _letter, _target, option = candidates[0]
            potential[subset] = value
            policy[subset] = option

    records = []
    local_checks = []
    for subset in sorted(distance, key=lambda item: (len(item), item)):
        value = potential.get(subset)
        option = policy.get(subset)
        if value is None:
            records.append(
                {
                    "subset": list(subset),
                    "rank": len(subset),
                    "potential": None,
                    "status": "UNREACHABLE_RESET_FROM_SUBSET",
                }
            )
            continue
        if option is None:
            records.append(
                {
                    "subset": list(subset),
                    "rank": len(subset),
                    "potential": value,
                    "status": "SINGLETON",
                }
            )
            continue
        target = tuple(option["target"])
        expected = option["segment_length"] + potential[target]
        assert expected == value
        # Along the selected rank-preserving prefix, the same segment is a
        # valid continuation, so the dynamic potential drops by exactly one.
        current = subset
        prefix = tuple(option["prefix_word"])
        policy_remaining = value
        trace = [policy_remaining]
        for letter in prefix:
            nxt = tuple(sorted({transition[letter][state] for state in current}))
            policy_remaining -= 1
            local_checks.append(policy_remaining >= 0)
            trace.append(policy_remaining)
            current = nxt
        local_checks.append(policy_remaining == potential[target] + 1)
        trace.append(potential[target])
        records.append(
            {
                "subset": list(subset),
                "rank": len(subset),
                "potential": value,
                "status": "EXACT_RANK_DROP_POLICY",
                "escape_word": prefix + (option["letter"],),
                "segment_length": option["segment_length"],
                "boundary_source": option["boundary_source"],
                "target": option["target"],
                "target_potential": potential[target],
                "policy_potential_trace": trace,
            }
        )

    full = tuple(range(len(transition[0])))
    exact_reset = shortest_subset_reset_word(transition)
    exact_depth = None if exact_reset is None else len(exact_reset)
    potential_depth = potential.get(full)
    if potential_depth != exact_depth:
        raise AssertionError(
            f"rank-drop dynamic program disagrees with subset BFS: {potential_depth} != {exact_depth}"
        )
    return {
        "carrier": "rank_drop_dynamic_potential",
        "potential_formula": "Psi(singleton)=0; Psi(S)=min_e(|e|+Psi(target(e)))",
        "reachable_subset_count": len(distance),
        "records": records,
        "initial_subset": list(full),
        "initial_potential": potential_depth,
        "shortest_reset_depth": exact_depth,
        "shortest_reset_word": None if exact_reset is None else list(exact_reset),
        "local_descent_certificate": {
            "all_checks_passed": all(local_checks) if local_checks else True,
            "check_count": len(local_checks),
            "meaning": "each selected rank-preserving step has unit amortized potential descent",
        },
        "claim_boundary": (
            "exact finite rank-layer theorem; a quadratic bound requires a separate "
            "uniform estimate on the initial potential"
        ),
    }


def cerny_transition(n: int) -> Transition:
    if n < 2:
        raise ValueError("n must be at least two")
    cycle = tuple((state + 1) % n for state in range(n))
    defect = tuple(0 if state == n - 1 else state for state in range(n))
    return cycle, defect


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = rank_drop_dynamic_potential(cerny_transition(args.states))
    payload = {
        "schema": "rime.synchronizing-automata.rank-drop-potential.v1",
        "state_count": args.states,
        "transition_family": "Cerny",
        "result": result,
    }
    payload["content_sha256"] = payload_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "states": args.states,
        "initial_potential": result["initial_potential"],
        "local_checks": result["local_descent_certificate"]["check_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
