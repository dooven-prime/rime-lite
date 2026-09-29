#!/usr/bin/env python3
"""Paper XXIX canonical rank-five frontier checker.

This module is paper-owned and uses only Python's standard library.  It
replays finite instances of the intrinsic raw geometry in the manuscript:

* spectator-safe reachability in Conf_{2,3};
* the missing-image section identities R_1 = id and R_2 = C_{n-1};
* strong connectivity of the cyclic-order-preserving lineage fiber;
* the complete canonical boundary-incidence spectrum; and
* the five-state coarse-quotient non-descent control.

The finite checks are development controls.  They are not the all-n proof.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias


Config: TypeAlias = tuple[frozenset[int], frozenset[int]]
Injection: TypeAlias = tuple[int, int, int, int, int]
Incidence: TypeAlias = tuple[int, int, int, int, int]

SCHEMA = "rime.paper29.canonical-frontier-audit.v1"
STATUS = "FINITE_SANITY_CHECK_NOT_ALL_N_PROOF"


def canonical_defect(n: int, q: int) -> int:
    """The canonical defect d_n on Q = Z/nZ."""

    if not 0 <= q < n:
        raise ValueError(f"coordinate {q} is outside Z/{n}Z")
    return 0 if q <= 1 else q - 1


def validate_config(n: int, state: Config) -> None:
    pair, holes = state
    if n < 5:
        raise ValueError("rank-five configurations require n >= 5")
    if len(pair) != 2:
        raise ValueError("the marked pair must contain two coordinates")
    if len(holes) != n - 5:
        raise ValueError("the hole set must have size n - 5")
    if pair & holes:
        raise ValueError("marked tokens and holes must be disjoint")
    if any(q < 0 or q >= n for q in pair | holes):
        raise ValueError("configuration coordinate outside Q")


def p_config(n: int, state: Config) -> Config:
    pair, holes = state
    return (
        frozenset((q + 1) % n for q in pair),
        frozenset((q + 1) % n for q in holes),
    )


def p_power_config(n: int, state: Config, exponent: int) -> Config:
    pair, holes = state
    shift = exponent % n
    return (
        frozenset((q + shift) % n for q in pair),
        frozenset((q + shift) % n for q in holes),
    )


def d_config(n: int, state: Config) -> Config | None:
    """Apply d_n when it is injective on the five occupied coordinates."""

    pair, holes = state
    kernel = frozenset((0, 1))
    if not holes & kernel:
        return None
    occupied = frozenset(range(n)) - holes
    image = frozenset(canonical_defect(n, q) for q in occupied)
    if len(image) != 5:
        raise AssertionError("guarded canonical defect did not preserve rank five")
    result = (
        frozenset(canonical_defect(n, q) for q in pair),
        frozenset(range(n)) - image,
    )
    validate_config(n, result)
    return result


def return_config(n: int, state: Config, exponent: int) -> Config | None:
    """The section return R_t = d_n o p^t."""

    return d_config(n, p_power_config(n, state, exponent))


def all_configs(n: int) -> Iterator[Config]:
    q = range(n)
    for pair_tuple in combinations(q, 2):
        pair = frozenset(pair_tuple)
        available = [x for x in q if x not in pair]
        for holes_tuple in combinations(available, n - 5):
            yield pair, frozenset(holes_tuple)


def omega_adjacent(n: int, state: Config) -> bool:
    """Whether the two P tokens are adjacent after deleting all holes."""

    pair, holes = state
    occupied = [q for q in range(n) if q not in holes]
    pair_positions = [i for i, q in enumerate(occupied) if q in pair]
    if len(occupied) != 5 or len(pair_positions) != 2:
        raise AssertionError("invalid token/hole state")
    i, j = pair_positions
    return (i - j) % 5 in (1, 4)


def reverse_safe_hit_set(n: int) -> tuple[set[Config], int]:
    """Return all configurations that can reach A = {0,1}."""

    states = tuple(all_configs(n))
    state_set = set(states)
    reverse: dict[Config, list[Config]] = {state: [] for state in states}
    edge_count = 0
    for state in states:
        successors = [p_config(n, state)]
        d_successor = d_config(n, state)
        if d_successor is not None:
            successors.append(d_successor)
        for successor in successors:
            if successor not in state_set:
                raise AssertionError("transition left Conf_{2,3}")
            reverse[successor].append(state)
            edge_count += 1

    kernel = frozenset((0, 1))
    reached = {state for state in states if state[0] == kernel}
    queue = deque(reached)
    while queue:
        state = queue.popleft()
        for predecessor in reverse[state]:
            if predecessor not in reached:
                reached.add(predecessor)
                queue.append(predecessor)
    return reached, edge_count


def tau_section_state(n: int, state: Config) -> Config:
    """Rotate the non-missing section coordinates by one."""

    pair, holes = state
    missing = n - 1

    def tau(q: int) -> int:
        if q == missing:
            return missing
        return (q + 1) % (n - 1)

    return frozenset(tau(q) for q in pair), frozenset(tau(q) for q in holes)


def section_audit(n: int) -> dict[str, int | bool | None]:
    if n < 6:
        return {
            "section_states": 0,
            "r1_identity": None,
            "r2_cycle": None,
        }
    missing = n - 1
    section = [state for state in all_configs(n) if missing in state[1]]
    r1_identity = all(return_config(n, state, 1) == state for state in section)
    r2_cycle = all(
        return_config(n, state, 2) == tau_section_state(n, state)
        for state in section
    )
    return {
        "section_states": len(section),
        "r1_identity": r1_identity,
        "r2_cycle": r2_cycle,
    }


def cyclic_order_injections(n: int) -> Iterator[Injection]:
    """All placements preserving one fixed positive order of five labels."""

    for support in combinations(range(n), 5):
        for shift in range(5):
            rotated = support[shift:] + support[:shift]
            yield rotated  # type: ignore[misc]


def p_injection(n: int, placement: Injection) -> Injection:
    return tuple((q + 1) % n for q in placement)  # type: ignore[return-value]


def d_injection(n: int, placement: Injection) -> Injection | None:
    support = set(placement)
    if {0, 1} <= support:
        return None
    image = tuple(canonical_defect(n, q) for q in placement)
    if len(set(image)) != 5:
        raise AssertionError("guarded lineage update is not injective")
    return image  # type: ignore[return-value]


def reachable(start: Injection, graph: dict[Injection, list[Injection]]) -> set[Injection]:
    reached = {start}
    queue = deque((start,))
    while queue:
        state = queue.popleft()
        for successor in graph[state]:
            if successor not in reached:
                reached.add(successor)
                queue.append(successor)
    return reached


def lineage_graph_audit(n: int) -> dict[str, int | bool]:
    states = tuple(cyclic_order_injections(n))
    state_set = set(states)
    if len(state_set) != len(states):
        raise AssertionError("duplicate cyclic-order placements")
    graph: dict[Injection, list[Injection]] = {state: [] for state in states}
    reverse: dict[Injection, list[Injection]] = {state: [] for state in states}
    edge_count = 0
    for state in states:
        successors = [p_injection(n, state)]
        d_successor = d_injection(n, state)
        if d_successor is not None:
            successors.append(d_successor)
        for successor in successors:
            if successor not in state_set:
                raise AssertionError("canonical step changed cyclic lineage order")
            graph[state].append(successor)
            reverse[successor].append(state)
            edge_count += 1

    start = states[0]
    strongly_connected = (
        len(reachable(start, graph)) == len(states)
        and len(reachable(start, reverse)) == len(states)
    )
    return {
        "order_fiber_states": len(states),
        "predicted_order_fiber_states": 5 * comb(n, 5),
        "order_fiber_edges": edge_count,
        "order_fiber_strongly_connected": strongly_connected,
    }


def actual_boundary_spectrum(n: int) -> set[Incidence]:
    spectrum: set[Incidence] = set()
    for placement in cyclic_order_injections(n):
        if {0, 1} <= set(placement):
            beta = tuple(canonical_defect(n, q) for q in placement)
            spectrum.add(beta)  # type: ignore[arg-type]
    return spectrum


def expected_boundary_spectrum(n: int) -> set[Incidence]:
    spectrum: set[Incidence] = set()
    for first in range(5):
        second = (first + 1) % 5
        survivors = ((first + 2) % 5, (first + 3) % 5, (first + 4) % 5)
        for values in combinations(range(1, n - 1), 3):
            beta = [0, 0, 0, 0, 0]
            beta[first] = 0
            beta[second] = 0
            for lineage, value in zip(survivors, values, strict=True):
                beta[lineage] = value
            spectrum.add(tuple(beta))  # type: ignore[arg-type]
    return spectrum


def coarse_non_descent_control() -> dict[str, int | bool]:
    defects = (
        (0, 0, 1, 2, 3),
        (0, 0, 2, 1, 3),
    )

    def endpoint(table: tuple[int, ...], exponent: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
        packets: dict[int, list[int]] = {}
        for source in range(5):
            coordinate = (source + exponent) % 5
            output = table[coordinate]
            packets.setdefault(output, []).append(source)
        return tuple(
            (coordinate, tuple(sorted(labels)))
            for coordinate, labels in sorted(packets.items())
        )

    frontiers = [
        {endpoint(table, exponent) for exponent in range(5)}
        for table in defects
    ]
    return {
        "left_frontier_size": len(frontiers[0]),
        "right_frontier_size": len(frontiers[1]),
        "frontiers_disjoint": frontiers[0].isdisjoint(frontiers[1]),
    }


def audit_n(n: int) -> dict[str, object]:
    states = tuple(all_configs(n))
    for state in states:
        validate_config(n, state)
    safe_hit, edge_count = reverse_safe_hit_set(n)
    omega_positive = {state for state in states if omega_adjacent(n, state)}
    section = section_audit(n)
    lineage = lineage_graph_audit(n)
    actual = actual_boundary_spectrum(n)
    expected = expected_boundary_spectrum(n)
    return {
        "n": n,
        "configuration_states": len(states),
        "predicted_configuration_states": 10 * comb(n, 5),
        "configuration_edges": edge_count,
        "safe_hit_states": len(safe_hit),
        "omega_adjacent_states": len(omega_positive),
        "safe_hit_equals_omega_adjacency": safe_hit == omega_positive,
        **section,
        **lineage,
        "boundary_incidence_count": len(actual),
        "predicted_boundary_incidence_count": 5 * comb(n - 2, 3),
        "boundary_spectrum_exact": actual == expected,
    }


def build_result(min_n: int, max_n: int) -> dict[str, object]:
    if min_n < 5 or max_n < min_n:
        raise ValueError("require 5 <= min_n <= max_n")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "family": "canonical single-defect circular automata",
            "rank": 5,
            "min_n": min_n,
            "max_n": max_n,
            "claim_boundary": (
                "Finite exact replay of manuscript definitions; "
                "not the all-n proof and not a typed transfer audit."
            ),
        },
        "coarse_non_descent_control": coarse_non_descent_control(),
        "records": [audit_n(n) for n in range(min_n, max_n + 1)],
    }


def write_result(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result(args.min_n, args.max_n)
    if args.output is None:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        write_result(args.output, result)
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
