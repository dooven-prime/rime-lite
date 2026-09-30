#!/usr/bin/env python3
"""Bounded hostile controls for the Paper XXXI partial-return theorems.

The standard-library-only audit replays two finite domains:

* every identity-branch state and labelled edge for 6 <= n <= 12; and
* every normalizer branch obtained from all permutations of E for 6 <= n <= 8.

The retained JSON is a bounded consistency control. It is not the proof of
the manuscript's all-n classification.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from functools import lru_cache
from itertools import combinations, permutations
from math import gcd, lcm
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias


Config: TypeAlias = tuple[tuple[int, int], tuple[int, int, int]]
Perm: TypeAlias = tuple[int, ...]
Edge: TypeAlias = tuple[int, int, int]

SCHEMA = "rime.paper31.partial-return-hostile-audit.v1"
STATUS = "FINITE_SANITY_CHECK_NOT_ALL_N_PROOF"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@lru_cache(maxsize=None)
def all_configs(n: int) -> tuple[Config, ...]:
    if n < 6:
        raise ValueError("rank-five normalized section requires n >= 6")
    carrier = tuple(range(1, n))
    states: list[Config] = []
    for pair in combinations(carrier, 2):
        remainder = tuple(q for q in carrier if q not in pair)
        for spectators in combinations(remainder, 3):
            states.append((pair, spectators))
    return tuple(states)


@lru_cache(maxsize=None)
def state_index(n: int) -> dict[Config, int]:
    return {state: index for index, state in enumerate(all_configs(n))}


def identity_perm(n: int) -> Perm:
    return tuple(range(n))


def perm_from_values(n: int, values: tuple[int, ...]) -> Perm:
    carrier = tuple(range(1, n))
    if tuple(sorted(values)) != carrier:
        raise ValueError("branch values are not a permutation of E")
    return (0, *values)


def compose_perm(left: Perm, right: Perm) -> Perm:
    require(len(left) == len(right), "permutation carrier mismatch")
    return tuple(0 if q == 0 else left[right[q]] for q in range(len(left)))


def inverse_perm(perm: Perm) -> Perm:
    result = [0] * len(perm)
    for q in range(1, len(perm)):
        result[perm[q]] = q
    require(set(result[1:]) == set(range(1, len(perm))), "map is not a permutation")
    return tuple(result)


def power_perm(perm: Perm, exponent: int) -> Perm:
    if exponent < 0:
        return power_perm(inverse_perm(perm), -exponent)
    result = identity_perm(len(perm))
    base = perm
    value = exponent
    while value:
        if value & 1:
            result = compose_perm(base, result)
        base = compose_perm(base, base)
        value >>= 1
    return result


def perm_order(perm: Perm) -> int:
    unseen = set(range(1, len(perm)))
    order = 1
    while unseen:
        start = min(unseen)
        current = start
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = perm[current]
            length += 1
        require(current == start, "permutation cycle did not close")
        order = lcm(order, length)
    return order


def epsilon(delta: int, q: int) -> int:
    return delta if q == 0 else q


def psi_perm(n: int, delta: int) -> Perm:
    values = []
    for q in range(1, n):
        values.append(epsilon(delta, (q + delta) % n))
    return perm_from_values(n, tuple(values))


def apply_perm_state(perm: Perm, state: Config) -> Config:
    pair, spectators = state
    return (
        tuple(sorted(perm[q] for q in pair)),  # type: ignore[return-value]
        tuple(sorted(perm[q] for q in spectators)),  # type: ignore[return-value]
    )


def phi_state(n: int, delta: int, branch: Perm, label: int, state: Config) -> Config | None:
    pair, spectators = state
    pre_pair = tuple((branch[q] + label) % n for q in pair)
    pre_spectators = tuple((branch[q] + label) % n for q in spectators)
    pre_support = set(pre_pair + pre_spectators)
    if {0, delta} <= pre_support:
        return None
    out_pair = tuple(sorted(epsilon(delta, q) for q in pre_pair))
    out_spectators = tuple(sorted(epsilon(delta, q) for q in pre_spectators))
    output = (out_pair, out_spectators)
    require(len(set(out_pair + out_spectators)) == 5, "enabled return lost rank")
    require(output in state_index(n), "enabled return left Conf_{2,3}(E)")
    return output  # type: ignore[return-value]


@lru_cache(maxsize=None)
def target_pair_orbit(n: int, delta: int) -> frozenset[frozenset[int]]:
    return frozenset(
        frozenset((q, (q + delta) % n))
        for q in range(n)
    )


def is_target(n: int, delta: int, branch: Perm, state: Config) -> bool:
    pair, _ = state
    image = frozenset(branch[q] for q in pair)
    return image in target_pair_orbit(n, delta)


@lru_cache(maxsize=None)
def psi_cycles(n: int, delta: int) -> tuple[tuple[int, ...], ...]:
    psi = psi_perm(n, delta)
    unseen = set(range(1, n))
    cycles: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        current = start
        cycle: list[int] = []
        while current in unseen:
            unseen.remove(current)
            cycle.append(current)
            current = psi[current]
        require(current == start, "punctured rotation cycle did not close")
        cycles.append(tuple(cycle))
    return tuple(cycles)


def same_lane(n: int, delta: int, state: Config) -> bool:
    pair, _ = state
    return any(pair[0] in cycle and pair[1] in cycle for cycle in psi_cycles(n, delta))


def lane_adjacent(n: int, delta: int, state: Config) -> bool:
    pair, spectators = state
    occupied = set(pair + spectators)
    for cycle in psi_cycles(n, delta):
        if pair[0] not in cycle or pair[1] not in cycle:
            continue
        token_order = [q for q in cycle if q in occupied]
        left = token_order.index(pair[0])
        right = token_order.index(pair[1])
        return (left - right) % len(token_order) in (1, len(token_order) - 1)
    return False


def transition_graph(
    n: int, delta: int, branch: Perm
) -> tuple[tuple[tuple[tuple[int, int], ...], ...], int]:
    states = all_configs(n)
    index = state_index(n)
    graph: list[tuple[tuple[int, int], ...]] = []
    edge_count = 0
    for state in states:
        edges: list[tuple[int, int]] = []
        for label in range(n):
            successor = phi_state(n, delta, branch, label, state)
            if successor is not None:
                edges.append((label, index[successor]))
                edge_count += 1
        graph.append(tuple(edges))
    return tuple(graph), edge_count


def reverse_reachable(
    vertex_count: int,
    edges: Iterable[tuple[int, int]],
    targets: Iterable[int],
) -> set[int]:
    reverse = [[] for _ in range(vertex_count)]
    for source, target in edges:
        reverse[target].append(source)
    reached = set(targets)
    queue = deque(reached)
    while queue:
        vertex = queue.popleft()
        for predecessor in reverse[vertex]:
            if predecessor not in reached:
                reached.add(predecessor)
                queue.append(predecessor)
    return reached


def safe_hit_indices(
    n: int,
    delta: int,
    branch: Perm,
    graph: tuple[tuple[tuple[int, int], ...], ...],
) -> set[int]:
    states = all_configs(n)
    targets = [index for index, state in enumerate(states) if is_target(n, delta, branch, state)]
    edges = (
        (source, target)
        for source, row in enumerate(graph)
        for _, target in row
    )
    return reverse_reachable(len(states), edges, targets)


def audit_cyclic_delta(n: int, delta: int) -> dict[str, object]:
    branch = identity_perm(n)
    states = all_configs(n)
    graph, edge_count = transition_graph(n, delta, branch)
    safe = safe_hit_indices(n, delta, branch, graph)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    if safe != adjacent:
        raise RuntimeError(f"N3 classification failed at n={n}, delta={delta}")
    for source, row in enumerate(graph):
        source_value = source in adjacent
        for _, target in row:
            if (target in adjacent) != source_value:
                raise RuntimeError(
                    f"lane adjacency changed on an enabled edge at n={n}, delta={delta}"
                )
    return {
        "delta": delta,
        "states": len(states),
        "enabled_labelled_edges": edge_count,
        "safe_hit_states": len(safe),
        "lane_adjacent_states": len(adjacent),
        "safe_hit_equals_lane_adjacency": True,
        "lane_adjacency_edge_invariant": True,
    }


def h_orbits(n: int, delta: int) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    states = all_configs(n)
    index = state_index(n)
    psi = psi_perm(n, delta)
    unseen = set(range(len(states)))
    orbit_of = [-1] * len(states)
    orbits: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        orbit: list[int] = []
        current = start
        while current in unseen:
            unseen.remove(current)
            orbit_of[current] = len(orbits)
            orbit.append(current)
            current = index[apply_perm_state(psi, states[current])]
        require(current == start, "state orbit did not close")
        orbits.append(tuple(orbit))
    return tuple(orbit_of), tuple(orbits)


def quotient_edges(
    graph: tuple[tuple[tuple[int, int], ...], ...], orbit_of: tuple[int, ...]
) -> set[Edge]:
    return {
        (orbit_of[source], label, orbit_of[target])
        for source, row in enumerate(graph)
        for label, target in row
    }


def normalizer_multiplier(n: int, delta: int, branch: Perm) -> int | None:
    psi = psi_perm(n, delta)
    order = perm_order(psi)
    conjugate = compose_perm(compose_perm(branch, psi), inverse_perm(branch))
    power = identity_perm(n)
    for exponent in range(order):
        if conjugate == power:
            return exponent if gcd(exponent, order) == 1 else None
        power = compose_perm(psi, power)
    return None


def audit_normalizer_delta(n: int, delta: int) -> dict[str, object]:
    states = all_configs(n)
    identity = identity_perm(n)
    base_graph, _ = transition_graph(n, delta, identity)
    base_safe = safe_hit_indices(n, delta, identity, base_graph)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    same = {
        index for index, state in enumerate(states) if same_lane(n, delta, state)
    }
    require(base_safe == adjacent, "normalizer audit requires the checked N3 base case")

    orbit_of, orbits = h_orbits(n, delta)
    base_relation = quotient_edges(base_graph, orbit_of)
    base_target_orbits = {
        orbit_of[index]
        for index, state in enumerate(states)
        if is_target(n, delta, identity, state)
    }

    normalizer_count = 0
    state_cases = 0
    orientation_compatible_cases = 0
    quotient_edges_checked = 0
    order = perm_order(psi_perm(n, delta))

    for values in permutations(range(1, n)):
        branch = perm_from_values(n, values)
        multiplier = normalizer_multiplier(n, delta, branch)
        if multiplier is None:
            continue
        normalizer_count += 1
        state_cases += len(states)

        graph, _ = transition_graph(n, delta, branch)
        safe = safe_hit_indices(n, delta, branch, graph)
        if not adjacent <= safe:
            raise RuntimeError("identity-branch simulation failed in finite control")
        if not safe <= same:
            raise RuntimeError("normalizer same-lane obstruction failed")

        if multiplier in {1 % order, (-1) % order}:
            orientation_compatible_cases += len(states)
            if safe != adjacent:
                raise RuntimeError("orientation-compatible classification failed")

        bar_map: dict[int, int] = {}
        for orbit_id, orbit in enumerate(orbits):
            images = {
                orbit_of[state_index(n)[apply_perm_state(branch, states[index])]]
                for index in orbit
            }
            if len(images) != 1:
                raise RuntimeError("normalizer branch did not induce an orbit map")
            bar_map[orbit_id] = images.pop()
        if len(set(bar_map.values())) != len(orbits):
            raise RuntimeError("induced orbit map is not a permutation")
        bar_inverse = {target: source for source, target in bar_map.items()}

        actual_relation = quotient_edges(graph, orbit_of)
        expected_relation = {
            (bar_inverse[source], label, target)
            for source, label, target in base_relation
        }
        if actual_relation != expected_relation:
            raise RuntimeError("normalizer skew quotient relation failed")
        quotient_edges_checked += len(actual_relation)

        actual_target_orbits = {
            orbit_of[index]
            for index, state in enumerate(states)
            if is_target(n, delta, branch, state)
        }
        expected_target_orbits = {bar_inverse[orbit] for orbit in base_target_orbits}
        if actual_target_orbits != expected_target_orbits:
            raise RuntimeError("normalizer target orbit equation failed")

        quotient_pairs = {
            (source, target) for source, _, target in actual_relation
        }
        quotient_safe = reverse_reachable(
            len(orbits), quotient_pairs, actual_target_orbits
        )
        if any((index in safe) != (orbit_of[index] in quotient_safe) for index in range(len(states))):
            raise RuntimeError("exact quotient reachability failed")

    return {
        "delta": delta,
        "normalizer_branches": normalizer_count,
        "state_cases": state_cases,
        "orientation_compatible_state_cases": orientation_compatible_cases,
        "quotient_edges_checked": quotient_edges_checked,
        "skew_relation_exact": True,
        "target_orbit_exact": True,
        "quotient_reachability_exact": True,
        "normalizer_sandwich_exact": True,
        "orientation_compatible_exact": True,
    }


def build_result(cyclic_min_n: int, cyclic_max_n: int, normalizer_max_n: int) -> dict[str, object]:
    if cyclic_min_n != 6 or cyclic_max_n < cyclic_min_n:
        raise ValueError("the retained cyclic audit begins at n=6")
    if normalizer_max_n < 6 or normalizer_max_n > cyclic_max_n:
        raise ValueError("normalizer range must lie inside the cyclic range")

    cyclic_records: list[dict[str, object]] = []
    cyclic_state_cases = 0
    cyclic_edges = 0
    for n in range(cyclic_min_n, cyclic_max_n + 1):
        deltas = [audit_cyclic_delta(n, delta) for delta in range(1, n)]
        cyclic_records.append({"n": n, "deltas": deltas})
        cyclic_state_cases += sum(int(row["states"]) for row in deltas)
        cyclic_edges += sum(int(row["enabled_labelled_edges"]) for row in deltas)

    normalizer_records: list[dict[str, object]] = []
    normalizer_count = 0
    normalizer_state_cases = 0
    orientation_cases = 0
    quotient_edges_checked = 0
    for n in range(6, normalizer_max_n + 1):
        deltas = [audit_normalizer_delta(n, delta) for delta in range(1, n)]
        normalizer_records.append({"n": n, "deltas": deltas})
        normalizer_count += sum(int(row["normalizer_branches"]) for row in deltas)
        normalizer_state_cases += sum(int(row["state_cases"]) for row in deltas)
        orientation_cases += sum(
            int(row["orientation_compatible_state_cases"]) for row in deltas
        )
        quotient_edges_checked += sum(
            int(row["quotient_edges_checked"]) for row in deltas
        )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "rank": 5,
            "cyclic_min_n": cyclic_min_n,
            "cyclic_max_n": cyclic_max_n,
            "normalizer_min_n": 6,
            "normalizer_max_n": normalizer_max_n,
            "claim_boundary": (
                "Bounded hostile replay of manuscript definitions; not the all-n "
                "proof, not a Computational Certificate, and not a typed transfer audit."
            ),
        },
        "cyclic_branch": {
            "records": cyclic_records,
            "totals": {
                "state_cases": cyclic_state_cases,
                "enabled_labelled_edges": cyclic_edges,
            },
        },
        "normalizer_branch": {
            "records": normalizer_records,
            "totals": {
                "normalizer_branches": normalizer_count,
                "state_cases": normalizer_state_cases,
                "orientation_compatible_state_cases": orientation_cases,
                "quotient_edges_checked": quotient_edges_checked,
            },
        },
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
    parser.add_argument("--cyclic-min-n", type=int, default=6)
    parser.add_argument("--cyclic-max-n", type=int, default=12)
    parser.add_argument("--normalizer-max-n", type=int, default=8)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result(
        args.cyclic_min_n,
        args.cyclic_max_n,
        args.normalizer_max_n,
    )
    if args.output is None:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        write_result(args.output, result)
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
