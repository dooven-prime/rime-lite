#!/usr/bin/env python3
"""Exact bounded control of Paper XXXVI signed full-lane survivor incidence."""

from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import combinations, permutations, product
from pathlib import Path


SCHEMA = "rime.paper36.signed-lane-audit.v1"
STATUS = "BOUNDED_EXHAUSTIVE_G2_G3_CONSISTENCY_CONTROL"
G_VALUES = (2, 3)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def lanes(g: int) -> dict[int, tuple[int, ...]]:
    return {j: tuple(j + t * g for t in range(5)) for j in range(1, g)}


def branches(g: int):
    lane_ids = tuple(range(1, g))
    for lane_targets in permutations(lane_ids):
        for signs in product((-1, 1), repeat=g - 1):
            for phases in product(range(5), repeat=g - 1):
                for punctured in permutations(range(4)):
                    yield lane_targets, signs, phases, punctured


def branch_map(
    g: int,
    lane_targets: tuple[int, ...],
    signs: tuple[int, ...],
    phases: tuple[int, ...],
    punctured: tuple[int, ...],
) -> tuple[int, ...]:
    n = 5 * g
    table = [-1] * n
    ordinary = lanes(g)
    star = tuple(t * g for t in range(1, 5))
    for t, q in enumerate(star):
        table[q] = star[punctured[t]]
    for j, target in enumerate(lane_targets, start=1):
        for t, q in enumerate(ordinary[j]):
            table[q] = target + ((signs[j - 1] * t + phases[j - 1]) % 5) * g
    require(sorted(table[1:]) == list(range(1, n)), "branch not bijective")
    return tuple(table)


def preterminal(
    state: tuple[int, ...], table: tuple[int, ...], exponent: int, n: int
) -> tuple[int, ...]:
    return tuple((table[q] + exponent) % n for q in state)


def strict_or_plateau(
    state: tuple[int, ...], table: tuple[int, ...], label: int, g: int
) -> tuple[int, ...] | None:
    moved = preterminal(state, table, label, 5 * g)
    result = tuple(g if q == 0 else q for q in moved)
    return result if len(set(result)) == 5 else None


def reachable(
    start: tuple[int, ...], table: tuple[int, ...], g: int
) -> set[tuple[int, ...]]:
    found = {start}
    pending = deque([start])
    while pending:
        state = pending.popleft()
        for r in range(5 * g):
            next_state = strict_or_plateau(state, table, r, g)
            if next_state is not None and next_state not in found:
                found.add(next_state)
                pending.append(next_state)
    return found


def signed_vertices(
    source_lane: int,
    g: int,
    targets: tuple[int, ...],
    signs: tuple[int, ...],
) -> tuple[set[tuple[int, int]], set[int]]:
    vertices = {(source_lane, 1)}
    pending = deque([(source_lane, 1)])
    exit_signs: set[int] = set()
    while pending:
        j, sign = pending.popleft()
        exit_signs.add(sign * signs[j - 1])
        for r in range(5 * g):
            h = (targets[j - 1] + r) % g
            if h == 0:
                continue
            child = (h, sign * signs[j - 1])
            if child not in vertices:
                vertices.add(child)
                pending.append(child)
    return vertices, exit_signs


def observed_survivors(
    states: set[tuple[int, ...]], table: tuple[int, ...], g: int
) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    spectra = {f: set() for f in combinations(range(5), 2)}
    for state in states:
        for u in range(5 * g):
            mu = preterminal(state, table, u, 5 * g)
            pair = tuple(i for i, q in enumerate(mu) if q in (0, g))
            if len(pair) == 2:
                spectra[pair].add(tuple(mu[i] for i in range(5) if i not in pair))
    return spectra


def expected_survivors(
    signs: set[int], g: int
) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    spectra = {f: set() for f in combinations(range(5), 2)}
    for i in range(5):
        pair = tuple(sorted((i, (i + 1) % 5)))
        for sign in signs:
            mu = tuple(
                ((((q - i) % 5) if sign == 1 else 1 - ((q - i) % 5)) * g) % (5 * g)
                for q in range(5)
            )
            spectra[pair].add(tuple(mu[q] for q in range(5) if q not in pair))
    return spectra


def check_source(
    source_lane: int,
    g: int,
    table: tuple[int, ...],
    targets: tuple[int, ...],
    signs: tuple[int, ...],
) -> set[int]:
    ordinary = lanes(g)
    actual = reachable(ordinary[source_lane], table, g)
    vertices, exits = signed_vertices(source_lane, g, targets, signs)
    predicted = {
        tuple(j + ((phase + sign * i) % 5) * g for i in range(5))
        for j, sign in vertices
        for phase in range(5)
    }
    require(
        actual == predicted,
        f"g={g}, C_src={source_lane}: signed phase quotient mismatch",
    )
    for j, lane in ordinary.items():
        for r in range(5 * g):
            enabled = strict_or_plateau(lane, table, r, g) is not None
            require(
                enabled == ((targets[j - 1] + r) % g != 0),
                f"g={g}, lane={j}, label={r}: full-support guard mismatch",
            )
    require(
        observed_survivors(actual, table, g) == expected_survivors(exits, g),
        f"g={g}, C_src={source_lane}: survivor spectrum mismatch",
    )
    return exits


def unsigned_graph(table: tuple[int, ...], g: int) -> tuple[tuple, tuple]:
    internal = []
    boundary = []
    for j, lane in lanes(g).items():
        for r in range(5 * g):
            next_state = strict_or_plateau(lane, table, r, g)
            if next_state is not None:
                internal.append((j, r, tuple(sorted(next_state))))
            if set(preterminal(lane, table, r, 5 * g)) == {
                t * g for t in range(5)
            }:
                boundary.append((j, r))
    return tuple(internal), tuple(boundary)


def matched_control(g: int) -> dict[str, object]:
    count = g - 1
    targets = tuple(range(1, g))
    zero_phases = (0,) * count
    punctured = (0, 1, 2, 3)
    positive = branch_map(g, targets, (1,) * count, zero_phases, punctured)
    reflected = branch_map(g, targets, (-1,) * count, zero_phases, punctured)
    require(unsigned_graph(positive, g) == unsigned_graph(reflected, g),
            f"g={g}: unsigned matched graph differs")
    positive_states = reachable(lanes(g)[1], positive, g)
    reflected_states = reachable(lanes(g)[1], reflected, g)
    positive_spectra = observed_survivors(positive_states, positive, g)
    reflected_spectra = observed_survivors(reflected_states, reflected, g)
    consecutive = {tuple(sorted((i, (i + 1) % 5))) for i in range(5)}
    for pair in positive_spectra:
        wanted = (1, 2) if pair in consecutive else (0, 0)
        observed = (len(positive_spectra[pair]), len(reflected_spectra[pair]))
        require(observed == wanted, f"g={g}, F={pair}: matched spectrum mismatch")
    return {
        "unsigned_labelled_graph_equal": True,
        "same_fused_pairs": True,
        "survivors_per_consecutive_pair": {"identity": 1, "reflection": 2},
    }


def build_result() -> dict[str, object]:
    rows = []
    for g in G_VALUES:
        branch_count = 0
        source_count = 0
        positive_only = 0
        both = 0
        for targets, signs, phases, punctured in branches(g):
            branch_count += 1
            table = branch_map(g, targets, signs, phases, punctured)
            for source_lane in range(1, g):
                source_count += 1
                exits = check_source(source_lane, g, table, targets, signs)
                if exits == {1}:
                    positive_only += 1
                elif exits == {1, -1}:
                    both += 1
                else:
                    raise ValueError(f"g={g}, C_src={source_lane}: invalid exit signs")
        rows.append({
            "g": g,
            "n": 5 * g,
            "delta": g,
            "branch_count": branch_count,
            "source_cases": source_count,
            "exit_sign_cases": {"positive_only": positive_only, "both": both},
            "matched_identity_reflection": matched_control(g),
        })
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "g_values": list(G_VALUES),
            "branch_family": "all ordinary-lane permutations, signs, phases, and punctured-lane permutations",
            "source_policy": "every complete ordinary lane as C_src, five labels in positive order",
            "word_length_budget": None,
        },
        "checks": [
            "full-support guard",
            "reachable signed phase classes",
            "source-addressed survivor spectra",
            "matched unsigned labelled graph and terminal spectra",
        ],
        "domains": rows,
        "claim_boundary": "Bounded exact consistency control; manuscript proofs own all-g theorems.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the retained JSON result")
    args = parser.parse_args()
    payload = json.dumps(build_result(), indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"PASS: wrote {args.output}")


if __name__ == "__main__":
    main()
