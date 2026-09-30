#!/usr/bin/env python3
"""Bounded consistency controls for Paper XXXII.

The producer has two independent finite roles:

* exhaustively replay the single-lane affine dichotomy on 6 <= n <= 12; and
* exhaust all single-lane branch permutations on 6 <= n <= 7 against the
  cycle-automorphism dichotomy; and
* scan the small multi-lane affine-normalizer domain for hostile variation
  across phases and ordinary-lane permutations.

The retained result is not the proof of either all-n theorem.  The manuscript
proof of the single-lane result is data-independent, and the multi-lane
dichotomy remains open regardless of a bounded positive scan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial, gcd, lcm
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias


Config: TypeAlias = tuple[tuple[int, int], tuple[int, int, int]]
Perm: TypeAlias = tuple[int, ...]

SCHEMA = "rime.paper32.affine-five-token-audit.v1"
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
    require(tuple(sorted(values)) == carrier, "branch values are not a permutation of E")
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


def epsilon(delta: int, q: int) -> int:
    return delta if q == 0 else q


def psi_perm(n: int, delta: int) -> Perm:
    values = tuple(epsilon(delta, (q + delta) % n) for q in range(1, n))
    return perm_from_values(n, values)


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
    return tuple(sorted(cycles, key=lambda row: (len(row), row[0], row)))


def apply_perm_state(perm: Perm, state: Config) -> Config:
    pair, spectators = state
    return (
        tuple(sorted(perm[q] for q in pair)),  # type: ignore[return-value]
        tuple(sorted(perm[q] for q in spectators)),  # type: ignore[return-value]
    )


def phi_state(
    n: int, delta: int, branch: Perm, label: int, state: Config
) -> Config | None:
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


def transition_graph(
    n: int, delta: int, branch: Perm
) -> tuple[tuple[tuple[tuple[int, int], ...], ...], int]:
    index = state_index(n)
    graph: list[tuple[tuple[int, int], ...]] = []
    edge_count = 0
    for state in all_configs(n):
        edges: list[tuple[int, int]] = []
        for label in range(n):
            successor = phi_state(n, delta, branch, label, state)
            if successor is not None:
                edges.append((label, index[successor]))
                edge_count += 1
        graph.append(tuple(edges))
    return tuple(graph), edge_count


@lru_cache(maxsize=None)
def target_pair_orbit(n: int, delta: int) -> frozenset[frozenset[int]]:
    return frozenset(frozenset((q, (q + delta) % n)) for q in range(n))


def is_target(n: int, delta: int, branch: Perm, state: Config) -> bool:
    pair, _ = state
    image = frozenset(branch[q] for q in pair)
    return image in target_pair_orbit(n, delta)


def reverse_reachable(
    vertex_count: int, edges: Iterable[tuple[int, int]], targets: Iterable[int]
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
    targets = [
        index
        for index, state in enumerate(all_configs(n))
        if is_target(n, delta, branch, state)
    ]
    edges = (
        (source, target)
        for source, row in enumerate(graph)
        for _, target in row
    )
    return reverse_reachable(len(all_configs(n)), edges, targets)


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


def same_lane(n: int, delta: int, state: Config) -> bool:
    pair, _ = state
    return any(pair[0] in cycle and pair[1] in cycle for cycle in psi_cycles(n, delta))


def canonical_rotation(word: tuple[str, ...]) -> tuple[str, ...]:
    return min(word[index:] + word[:index] for index in range(len(word)))


def token_order(n: int, delta: int, state: Config) -> tuple[str, ...]:
    cycles = psi_cycles(n, delta)
    require(len(cycles) == 1, "token_order is the single-lane observable")
    pair, spectators = state
    pair_set = set(pair)
    spectator_set = set(spectators)
    colors = tuple(
        "P" if q in pair_set else "S"
        for q in cycles[0]
        if q in pair_set or q in spectator_set
    )
    require(len(colors) == 5, "single-lane token order lost an occupied point")
    return canonical_rotation(colors)


def gap_vector(
    cycle: tuple[int, ...], state: Config, start: int
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    require(start in cycle, "gap start is not in the lane")
    pair, spectators = state
    colors = {q: "P" for q in pair}
    colors.update({q: "S" for q in spectators})
    require(start in colors, "gap start is not occupied")
    offset = cycle.index(start)
    rotated = cycle[offset:] + cycle[:offset]
    positions = [index for index, q in enumerate(rotated) if q in colors]
    require(positions[0] == 0 and len(positions) == 5, "bad occupied lane encoding")
    gaps = tuple(
        (
            positions[(index + 1) % 5]
            + (len(cycle) if index == 4 else 0)
            - positions[index]
            - 1
        )
        for index in range(5)
    )
    order = tuple(colors[rotated[position]] for position in positions)
    return order, gaps


def reachable_vertices(
    graph: tuple[tuple[tuple[int, int], ...], ...],
    start: int,
    reverse: bool = False,
) -> set[int]:
    adjacency: list[list[int]] = [[] for _ in graph]
    for source, row in enumerate(graph):
        for _, target in row:
            if reverse:
                adjacency[target].append(source)
            else:
                adjacency[source].append(target)
    reached = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for target in adjacency[vertex]:
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def affine_branch(
    n: int,
    delta: int,
    multiplier: int,
    punctured_phase: int = 0,
    ordinary_permutation: tuple[int, ...] | None = None,
    ordinary_phases: tuple[int, ...] | None = None,
) -> Perm:
    cycles = psi_cycles(n, delta)
    short_length = min(len(cycle) for cycle in cycles)
    punctured_rows = [cycle for cycle in cycles if len(cycle) == short_length]
    require(len(punctured_rows) == 1, "punctured lane is not unique")
    punctured = punctured_rows[0]
    ordinary = [cycle for cycle in cycles if cycle is not punctured]

    if ordinary_permutation is None:
        ordinary_permutation = tuple(range(len(ordinary)))
    if ordinary_phases is None:
        ordinary_phases = tuple(0 for _ in ordinary)
    require(
        tuple(sorted(ordinary_permutation)) == tuple(range(len(ordinary))),
        "ordinary lane map is not a permutation",
    )
    require(len(ordinary_phases) == len(ordinary), "ordinary phase count mismatch")

    values: dict[int, int] = {}
    short = len(punctured)
    require(gcd(multiplier, short) == 1 or short == 1, "bad punctured multiplier")
    for index, q in enumerate(punctured):
        values[q] = punctured[(multiplier * index + punctured_phase) % short]

    for source_index, source_cycle in enumerate(ordinary):
        target_cycle = ordinary[ordinary_permutation[source_index]]
        length = len(source_cycle)
        require(len(target_cycle) == length, "ordinary lane length mismatch")
        require(gcd(multiplier, length) == 1, "bad ordinary multiplier")
        phase = ordinary_phases[source_index]
        for index, q in enumerate(source_cycle):
            values[q] = target_cycle[(multiplier * index + phase) % length]

    return perm_from_values(n, tuple(values[q] for q in range(1, n)))


def safe_digest(indices: set[int]) -> str:
    payload = ",".join(str(value) for value in sorted(indices)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def local_dihedral(multiplier: int, lengths: Iterable[int]) -> bool:
    for length in sorted(set(lengths)):
        if length <= 2:
            continue
        if multiplier % length not in {1, (-1) % length}:
            return False
    return True


def cycle_edges(n: int, delta: int) -> frozenset[frozenset[int]]:
    cycles = psi_cycles(n, delta)
    require(len(cycles) == 1, "cycle-edge check requires one lane")
    cycle = cycles[0]
    return frozenset(
        frozenset((cycle[index], cycle[(index + 1) % len(cycle)]))
        for index in range(len(cycle))
    )


def is_cycle_automorphism(n: int, delta: int, branch: Perm) -> bool:
    edges = cycle_edges(n, delta)
    image_edges = frozenset(
        frozenset(branch[q] for q in edge)
        for edge in edges
    )
    return image_edges == edges


def audit_single_lane_permutations(n: int, delta: int) -> dict[str, int]:
    require(gcd(n, delta) == 1, "permutation audit received multiple lanes")
    states = all_configs(n)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    full = set(range(len(states)))
    edges = cycle_edges(n, delta)
    automorphisms = 0
    nonautomorphisms = 0

    for values in permutations(range(1, n)):
        branch = perm_from_values(n, tuple(values))
        graph, _ = transition_graph(n, delta, branch)
        safe = safe_hit_indices(n, delta, branch, graph)
        automorphism = is_cycle_automorphism(n, delta, branch)
        expected = adjacent if automorphism else full
        require(
            safe == expected,
            f"permutation dichotomy failed at n={n}, delta={delta}, branch={values}",
        )
        if automorphism:
            automorphisms += 1
            continue

        nonautomorphisms += 1
        nonedge_to_edge = any(
            pair not in edges
            and frozenset(branch[q] for q in pair) in edges
            for pair in map(frozenset, combinations(range(1, n), 2))
        )
        require(nonedge_to_edge, "nonautomorphism has no nonedge-to-edge witness")

    length = n - 1
    require(automorphisms == 2 * length, "cycle automorphism count drift")
    require(
        automorphisms + nonautomorphisms == factorial(length),
        "permutation branch count drift",
    )
    return {
        "delta": delta,
        "states": len(states),
        "adjacent_states": len(adjacent),
        "branches": factorial(length),
        "cycle_automorphisms": automorphisms,
        "nonautomorphisms": nonautomorphisms,
    }


def verify_order_fibers(
    n: int,
    delta: int,
    graph: tuple[tuple[tuple[int, int], ...], ...],
) -> tuple[list[int], int]:
    states = all_configs(n)
    groups: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, state in enumerate(states):
        groups[token_order(n, delta, state)].append(index)

    for source, row in enumerate(graph):
        source_order = token_order(n, delta, states[source])
        for _, target in row:
            require(
                token_order(n, delta, states[target]) == source_order,
                f"token order changed at n={n}, delta={delta}",
            )

    for order, vertices in groups.items():
        vertex_set = set(vertices)
        root = vertices[0]
        forward = reachable_vertices(graph, root) & vertex_set
        backward = reachable_vertices(graph, root, reverse=True) & vertex_set
        require(
            forward == vertex_set and backward == vertex_set,
            f"order fiber is not strongly connected at n={n}, delta={delta}, order={order}",
        )
    return sorted(len(vertices) for vertices in groups.values()), len(groups)


def verify_local_gap_transfers(n: int, delta: int) -> int:
    cycles = psi_cycles(n, delta)
    require(len(cycles) == 1, "gap transfer check requires one lane")
    cycle = cycles[0]
    psi = psi_perm(n, delta)
    identity = identity_perm(n)
    checks = 0
    for state in all_configs(n):
        occupied = set(state[0] + state[1])
        for token in sorted(occupied):
            order, gaps = gap_vector(cycle, state, token)
            if gaps[0] == 0:
                continue
            exponent = (cycle.index(delta) - cycle.index(token)) % len(cycle)
            rotated = apply_perm_state(power_perm(psi, exponent), state)
            moved = phi_state(n, delta, identity, (-delta) % n, rotated)
            require(moved is not None, "declared local gap transfer is not guarded")
            moved_order, moved_gaps = gap_vector(cycle, moved, delta)
            expected = (gaps[0] - 1, gaps[1], gaps[2], gaps[3], gaps[4] + 1)
            require(moved_order == order, "local gap transfer changed token order")
            require(
                moved_gaps == expected,
                f"local gap transfer mismatch at n={n}, delta={delta}",
            )
            checks += 1
    return checks


def audit_single_lane(n: int, delta: int) -> dict[str, object]:
    require(gcd(n, delta) == 1, "single-lane audit received multiple lanes")
    states = all_configs(n)
    identity = identity_perm(n)
    graph, edge_count = transition_graph(n, delta, identity)
    safe_identity = safe_hit_indices(n, delta, identity, graph)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    require(safe_identity == adjacent, "identity Safe-Hit is not lane adjacency")

    fiber_sizes, order_count = verify_order_fibers(n, delta, graph)
    require(order_count == 2, "single lane does not have exactly two color orders")
    gap_checks = verify_local_gap_transfers(n, delta)

    length = n - 1
    units: list[dict[str, object]] = []
    for multiplier in range(1, length):
        if gcd(multiplier, length) != 1:
            continue
        branch = affine_branch(n, delta, multiplier)
        branch_graph, _ = transition_graph(n, delta, branch)
        safe = safe_hit_indices(n, delta, branch, branch_graph)
        dihedral = multiplier % length in {1, (-1) % length}
        expected = adjacent if dihedral else set(range(len(states)))
        require(
            safe == expected,
            f"single-lane dichotomy failed at n={n}, delta={delta}, u={multiplier}",
        )
        units.append(
            {
                "multiplier": multiplier,
                "dihedral": dihedral,
                "safe_hit_states": len(safe),
                "safe_hit_digest": safe_digest(safe),
                "classification": "ADJ" if safe == adjacent else "ALL",
            }
        )

    return {
        "delta": delta,
        "states": len(states),
        "identity_edges": edge_count,
        "token_order_fibers": order_count,
        "token_order_fiber_sizes": fiber_sizes,
        "local_gap_transfer_checks": gap_checks,
        "adjacent_states": len(adjacent),
        "units": units,
    }


def affine_parameter_rows(
    n: int, delta: int
) -> Iterator[tuple[int, int, tuple[int, ...], tuple[int, ...], Perm]]:
    cycles = psi_cycles(n, delta)
    short = min(len(cycle) for cycle in cycles)
    ordinary_count = len(cycles) - 1
    ordinary_length = max(len(cycle) for cycle in cycles)
    modulus = lcm(*(len(cycle) for cycle in cycles))

    for multiplier in range(1, modulus):
        if gcd(multiplier, modulus) != 1:
            continue
        for punctured_phase in range(short):
            for lane_permutation in permutations(range(ordinary_count)):
                for phases in product(range(ordinary_length), repeat=ordinary_count):
                    branch = affine_branch(
                        n,
                        delta,
                        multiplier,
                        punctured_phase,
                        tuple(lane_permutation),
                        tuple(phases),
                    )
                    yield (
                        multiplier,
                        punctured_phase,
                        tuple(lane_permutation),
                        tuple(phases),
                        branch,
                    )


def audit_multilane_hostile(n: int, delta: int) -> dict[str, object]:
    require(gcd(n, delta) > 1, "hostile scan received a single lane")
    states = all_configs(n)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    same = {index for index, state in enumerate(states) if same_lane(n, delta, state)}
    lengths = tuple(len(cycle) for cycle in psi_cycles(n, delta))
    modulus = lcm(*lengths)
    grouped: dict[int, dict[str, object]] = {}

    for multiplier, punctured_phase, lane_permutation, phases, branch in (
        affine_parameter_rows(n, delta)
    ):
        graph, _ = transition_graph(n, delta, branch)
        safe = safe_hit_indices(n, delta, branch, graph)
        require(adjacent <= safe <= same, "normalizer sandwich failed in hostile scan")
        if safe == adjacent:
            outcome = "ADJ"
        elif safe == same:
            outcome = "SAME"
        else:
            outcome = "INTERMEDIATE"
        digest = safe_digest(safe)
        row = grouped.setdefault(
            multiplier,
            {
                "multiplier": multiplier,
                "local_dihedral": local_dihedral(multiplier, lengths),
                "branch_count": 0,
                "outcomes": set(),
                "safe_hit_digests": set(),
                "first_branch_by_digest": {},
            },
        )
        row["branch_count"] = int(row["branch_count"]) + 1
        row["outcomes"].add(outcome)  # type: ignore[union-attr]
        row["safe_hit_digests"].add(digest)  # type: ignore[union-attr]
        first = row["first_branch_by_digest"]
        if digest not in first:  # type: ignore[operator]
            first[digest] = {  # type: ignore[index]
                "punctured_phase": punctured_phase,
                "ordinary_permutation": list(lane_permutation),
                "ordinary_phases": list(phases),
                "safe_hit_states": len(safe),
                "outcome": outcome,
            }

    rows: list[dict[str, object]] = []
    for multiplier in sorted(grouped):
        source = grouped[multiplier]
        digests = sorted(source["safe_hit_digests"])  # type: ignore[arg-type]
        outcomes = sorted(source["outcomes"])  # type: ignore[arg-type]
        local = bool(source["local_dihedral"])
        if local:
            require(outcomes == ["ADJ"], "lane-wise dihedral finite control failed")
        rows.append(
            {
                "multiplier": multiplier,
                "local_dihedral": local,
                "branch_count": source["branch_count"],
                "outcomes": outcomes,
                "distinct_safe_hit_sets": len(digests),
                "same_multiplier_variation": len(digests) > 1,
                "witnesses": [
                    {
                        "safe_hit_digest": digest,
                        **source["first_branch_by_digest"][digest],  # type: ignore[index]
                    }
                    for digest in digests
                ],
            }
        )

    return {
        "delta": delta,
        "states": len(states),
        "adjacent_states": len(adjacent),
        "same_lane_states": len(same),
        "lane_lengths": sorted(lengths),
        "multiplier_modulus": modulus,
        "multipliers": rows,
    }


def build_result(
    single_min_n: int,
    single_max_n: int,
    hostile_max_n: int,
    permutation_max_n: int = 7,
) -> dict[str, object]:
    if single_min_n < 6 or single_max_n < single_min_n:
        raise ValueError("invalid single-lane range")
    if hostile_max_n < 6 or hostile_max_n > single_max_n:
        raise ValueError("hostile range must lie inside the single-lane range")
    if permutation_max_n < 6 or permutation_max_n > single_max_n:
        raise ValueError("permutation range must lie inside the single-lane range")

    single_records: list[dict[str, object]] = []
    single_totals = {
        "delta_cells": 0,
        "state_cases": 0,
        "identity_edges": 0,
        "unit_cells": 0,
        "local_gap_transfer_checks": 0,
    }
    for n in range(single_min_n, single_max_n + 1):
        deltas = [
            audit_single_lane(n, delta)
            for delta in range(1, n)
            if gcd(n, delta) == 1
        ]
        single_records.append({"n": n, "deltas": deltas})
        single_totals["delta_cells"] += len(deltas)
        single_totals["state_cases"] += sum(int(row["states"]) for row in deltas)
        single_totals["identity_edges"] += sum(
            int(row["identity_edges"]) for row in deltas
        )
        single_totals["unit_cells"] += sum(len(row["units"]) for row in deltas)
        single_totals["local_gap_transfer_checks"] += sum(
            int(row["local_gap_transfer_checks"]) for row in deltas
        )

    permutation_records: list[dict[str, object]] = []
    permutation_totals = {
        "delta_cells": 0,
        "branch_cells": 0,
        "cycle_automorphism_cells": 0,
        "nonautomorphism_cells": 0,
    }
    for n in range(6, permutation_max_n + 1):
        deltas = [
            audit_single_lane_permutations(n, delta)
            for delta in range(1, n)
            if gcd(n, delta) == 1
        ]
        permutation_records.append({"n": n, "deltas": deltas})
        permutation_totals["delta_cells"] += len(deltas)
        permutation_totals["branch_cells"] += sum(
            int(row["branches"]) for row in deltas
        )
        permutation_totals["cycle_automorphism_cells"] += sum(
            int(row["cycle_automorphisms"]) for row in deltas
        )
        permutation_totals["nonautomorphism_cells"] += sum(
            int(row["nonautomorphisms"]) for row in deltas
        )

    hostile_records: list[dict[str, object]] = []
    hostile_totals = {
        "delta_cells": 0,
        "branch_cells": 0,
        "multiplier_cells": 0,
        "mixed_sign_multiplier_cells": 0,
        "same_multiplier_variation_cells": 0,
        "intermediate_multiplier_cells": 0,
    }
    for n in range(6, hostile_max_n + 1):
        deltas = [
            audit_multilane_hostile(n, delta)
            for delta in range(1, n)
            if gcd(n, delta) > 1
        ]
        hostile_records.append({"n": n, "deltas": deltas})
        hostile_totals["delta_cells"] += len(deltas)
        for delta_row in deltas:
            for row in delta_row["multipliers"]:
                hostile_totals["multiplier_cells"] += 1
                hostile_totals["branch_cells"] += int(row["branch_count"])
                if row["local_dihedral"]:
                    modulus = int(delta_row["multiplier_modulus"])
                    multiplier = int(row["multiplier"])
                    if multiplier % modulus not in {1, (-1) % modulus}:
                        hostile_totals["mixed_sign_multiplier_cells"] += 1
                if row["same_multiplier_variation"]:
                    hostile_totals["same_multiplier_variation_cells"] += 1
                if "INTERMEDIATE" in row["outcomes"]:
                    hostile_totals["intermediate_multiplier_cells"] += 1

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "single_min_n": single_min_n,
            "single_max_n": single_max_n,
            "permutation_min_n": 6,
            "permutation_max_n": permutation_max_n,
            "hostile_min_n": 6,
            "hostile_max_n": hostile_max_n,
            "single_lane_rule": "gcd(n, delta) = 1",
            "permutation_rule": "gcd(n, delta) = 1; every branch permutation",
            "hostile_rule": "gcd(n, delta) > 1; all affine normalizer parameters",
        },
        "claim_boundary": [
            "finite replay is not the all-n proof",
            "the single-lane replay covers only the affine normalizer subfamily",
            "the full single-lane permutation theorem is proved in the manuscript",
            "the multi-lane scan does not prove multiplier descent or X3",
            "raw Safe-Hit does not imply survivor incidence or typed projectability",
        ],
        "single_lane": {
            "records": single_records,
            "totals": single_totals,
        },
        "single_lane_permutation_control": {
            "records": permutation_records,
            "totals": permutation_totals,
        },
        "multilane_hostile": {
            "records": hostile_records,
            "totals": hostile_totals,
        },
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--single-min-n", type=int, default=6)
    parser.add_argument("--single-max-n", type=int, default=12)
    parser.add_argument("--permutation-max-n", type=int, default=7)
    parser.add_argument("--hostile-max-n", type=int, default=9)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result(
        args.single_min_n,
        args.single_max_n,
        args.hostile_max_n,
        args.permutation_max_n,
    )
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
