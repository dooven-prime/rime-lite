#!/usr/bin/env python3
"""Exact small-domain hostile audit for the Paper XXXIII stabilizer program.

The audit has two deliberately separate roles:

* verify the source-addressed orbit-incidence factorization of every retained
  full-stabilizer branch; and
* search for failures of coarse stabilizer summaries such as the break set or
  the break set plus lane permutation and local restriction cycle types.

The output is a theorem-discovery control.  It is not an all-n proof, and an
unobserved counterexample is never interpreted as a positive theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
from typing import Iterable, Iterator, TypeAlias


Config: TypeAlias = tuple[tuple[int, int], tuple[int, int, int]]
Perm: TypeAlias = tuple[int, ...]

SCHEMA = "rime.paper33.stabilizer-hostile-audit.v1"
STATUS = "FINITE_THEOREM_DISCOVERY_CONTROL"


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


def perm_from_mapping(n: int, mapping: dict[int, int]) -> Perm:
    carrier = tuple(range(1, n))
    values = tuple(mapping[q] for q in carrier)
    require(tuple(sorted(values)) == carrier, "branch is not a permutation of E")
    return (0, *values)


def apply_perm_state(perm: Perm, state: Config) -> Config:
    pair, spectators = state
    return (
        tuple(sorted(perm[q] for q in pair)),  # type: ignore[return-value]
        tuple(sorted(perm[q] for q in spectators)),  # type: ignore[return-value]
    )


def epsilon(delta: int, q: int) -> int:
    return delta if q == 0 else q


def psi_perm(n: int, delta: int) -> Perm:
    mapping = {
        q: epsilon(delta, (q + delta) % n)
        for q in range(1, n)
    }
    return perm_from_mapping(n, mapping)


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
        require(current == start, "punctured-rotation cycle did not close")
        cycles.append(tuple(cycle))
    return tuple(sorted(cycles, key=lambda row: (len(row), row[0], row)))


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
    require(
        all(1 <= q < n for q in out_pair + out_spectators),
        "enabled return left the normalized carrier E",
    )
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


def safe_hit_indices(
    n: int,
    delta: int,
    branch: Perm,
    graph: tuple[tuple[tuple[int, int], ...], ...],
) -> set[int]:
    reverse = [[] for _ in graph]
    for source, row in enumerate(graph):
        for _, target in row:
            reverse[target].append(source)
    reached = {
        index
        for index, state in enumerate(all_configs(n))
        if is_target(n, delta, branch, state)
    }
    queue = deque(reached)
    while queue:
        vertex = queue.popleft()
        for predecessor in reverse[vertex]:
            if predecessor not in reached:
                reached.add(predecessor)
                queue.append(predecessor)
    return reached


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
    return any(
        pair[0] in cycle and pair[1] in cycle
        for cycle in psi_cycles(n, delta)
    )


def safe_digest(indices: set[int]) -> str:
    payload = ",".join(str(value) for value in sorted(indices)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def restriction_cycle_type(index_map: tuple[int, ...]) -> tuple[int, ...]:
    unseen = set(range(len(index_map)))
    lengths: list[int] = []
    while unseen:
        start = min(unseen)
        current = start
        length = 0
        while current in unseen:
            unseen.remove(current)
            length += 1
            current = index_map[current]
        require(current == start, "local restriction is not a permutation")
        lengths.append(length)
    return tuple(sorted(lengths))


def cycle_graph_isomorphism(index_map: tuple[int, ...]) -> bool:
    length = len(index_map)
    edges = {
        frozenset((index, (index + 1) % length))
        for index in range(length)
    }
    image_edges = {
        frozenset((index_map[index], index_map[(index + 1) % length]))
        for index in range(length)
    }
    return image_edges == edges


def stabilizer_branches(
    n: int, delta: int
) -> Iterator[tuple[dict[str, object], Perm]]:
    cycles = psi_cycles(n, delta)
    require(len(cycles) > 1, "stabilizer audit requires multiple lanes")
    short_length = min(len(cycle) for cycle in cycles)
    punctured_rows = [cycle for cycle in cycles if len(cycle) == short_length]
    require(len(punctured_rows) == 1, "punctured lane is not unique")
    punctured = punctured_rows[0]
    ordinary = tuple(cycle for cycle in cycles if cycle is not punctured)
    ordinary_length = len(ordinary[0])
    require(
        all(len(cycle) == ordinary_length for cycle in ordinary),
        "ordinary lanes have unequal lengths",
    )

    short_maps = tuple(permutations(range(len(punctured))))
    long_maps = tuple(permutations(range(ordinary_length)))
    for punctured_map in short_maps:
        for lane_permutation in permutations(range(len(ordinary))):
            for ordinary_maps in product(long_maps, repeat=len(ordinary)):
                mapping: dict[int, int] = {}
                for source_index, q in enumerate(punctured):
                    mapping[q] = punctured[punctured_map[source_index]]
                for lane_index, source_cycle in enumerate(ordinary):
                    target_cycle = ordinary[lane_permutation[lane_index]]
                    local_map = ordinary_maps[lane_index]
                    for source_index, q in enumerate(source_cycle):
                        mapping[q] = target_cycle[local_map[source_index]]

                local_maps = (tuple(punctured_map),) + tuple(
                    tuple(row) for row in ordinary_maps
                )
                break_pattern = tuple(
                    index
                    for index, row in enumerate(local_maps)
                    if not cycle_graph_isomorphism(row)
                )
                metadata: dict[str, object] = {
                    "punctured_map": list(punctured_map),
                    "ordinary_lane_permutation": list(lane_permutation),
                    "ordinary_maps": [list(row) for row in ordinary_maps],
                    "break_pattern": list(break_pattern),
                    "restriction_cycle_types": [
                        list(restriction_cycle_type(row)) for row in local_maps
                    ],
                }
                yield metadata, perm_from_mapping(n, mapping)


@lru_cache(maxsize=None)
def state_orbits(
    n: int, delta: int
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    psi = psi_perm(n, delta)
    states = all_configs(n)
    index = state_index(n)
    unseen = set(range(len(states)))
    orbits: list[tuple[int, ...]] = []
    orbit_of = [-1] * len(states)
    while unseen:
        start = min(unseen)
        current = start
        orbit: list[int] = []
        while current in unseen:
            unseen.remove(current)
            orbit_of[current] = len(orbits)
            orbit.append(current)
            current = index[apply_perm_state(psi, states[current])]
        require(current == start, "state orbit did not close")
        orbits.append(tuple(orbit))
    require(all(value >= 0 for value in orbit_of), "state orbit map is incomplete")
    return tuple(orbits), tuple(orbit_of)


def quotient_edges_direct(
    graph: tuple[tuple[tuple[int, int], ...], ...], orbit_of: tuple[int, ...]
) -> set[tuple[int, int, int]]:
    return {
        (orbit_of[source], label, orbit_of[target])
        for source, row in enumerate(graph)
        for label, target in row
    }


def quotient_edges_by_incidence(
    n: int, delta: int, branch: Perm
) -> set[tuple[int, int, int]]:
    states = all_configs(n)
    index = state_index(n)
    orbits, orbit_of = state_orbits(n, delta)
    identity = identity_perm(n)
    edges: set[tuple[int, int, int]] = set()
    for source_orbit, members in enumerate(orbits):
        for source in members:
            intermediate = apply_perm_state(branch, states[source])
            for label in range(n):
                output = phi_state(n, delta, identity, label, intermediate)
                if output is not None:
                    edges.add((source_orbit, label, orbit_of[index[output]]))
    return edges


def branch_key(metadata: dict[str, object]) -> tuple[object, ...]:
    return (
        tuple(metadata["break_pattern"]),  # type: ignore[arg-type]
        tuple(metadata["ordinary_lane_permutation"]),  # type: ignore[arg-type]
        tuple(
            tuple(row)
            for row in metadata["restriction_cycle_types"]  # type: ignore[union-attr]
        ),
    )


def capacity_obstruction_control(max_g: int = 12) -> dict[str, object]:
    """Check the capacity-isolated family n=5g, delta=g on bounded g."""

    rows: list[dict[str, object]] = []
    for g in range(2, max_g + 1):
        n = 5 * g
        delta = g
        cycles = psi_cycles(n, delta)
        punctured = cycles[0]
        ordinary = cycles[1:]
        require(len(punctured) == 4, "capacity family lost its short lane")
        require(
            all(len(cycle) == 5 for cycle in ordinary),
            "capacity family lost its ordinary lane length",
        )

        mapping = {q: q for q in range(1, n)}
        mapping[punctured[2]], mapping[punctured[3]] = (
            punctured[3],
            punctured[2],
        )
        branch = perm_from_mapping(n, mapping)
        require(
            not cycle_graph_isomorphism((0, 1, 3, 2)),
            "chosen punctured restriction is accidentally dihedral",
        )

        states_checked = 0
        enabled_edges = 0
        disabled_edges = 0
        for cycle in ordinary:
            edge_pairs = {
                frozenset((cycle[index], cycle[(index + 1) % 5]))
                for index in range(5)
            }
            for pair in combinations(cycle, 2):
                if frozenset(pair) in edge_pairs:
                    continue
                spectators = tuple(q for q in cycle if q not in pair)
                state: Config = (tuple(sorted(pair)), tuple(sorted(spectators)))
                require(same_lane(n, delta, state), "obstruction state is not same-lane")
                require(
                    not lane_adjacent(n, delta, state),
                    "obstruction pair is lane-adjacent",
                )
                require(
                    not is_target(n, delta, branch, state),
                    "obstruction state already lies in the branch target",
                )
                for label in range(n):
                    successor = phi_state(n, delta, branch, label, state)
                    if successor is None:
                        disabled_edges += 1
                        continue
                    enabled_edges += 1
                    support = set(successor[0] + successor[1])
                    target_lane = next(
                        (row for row in ordinary if support == set(row)),
                        None,
                    )
                    require(
                        target_lane is not None,
                        "enabled edge escaped the full ordinary-lane invariant",
                    )
                    require(
                        not lane_adjacent(n, delta, successor),
                        "enabled edge created lane adjacency inside the invariant",
                    )
                states_checked += 1
        rows.append(
            {
                "g": g,
                "n": n,
                "delta": delta,
                "states_checked": states_checked,
                "enabled_edges": enabled_edges,
                "disabled_edges": disabled_edges,
            }
        )
    return {
        "min_g": 2,
        "max_g": max_g,
        "family": "n=5g, delta=g; break only on the punctured four-cycle",
        "rows": rows,
        "status": "BOUNDED_CONTROL_OF_SYMBOLIC_OBSTRUCTION_NOT_PROOF",
    }


def witness_row(metadata: dict[str, object], safe: set[int]) -> dict[str, object]:
    return {
        **metadata,
        "safe_hit_states": len(safe),
        "safe_hit_digest": safe_digest(safe),
    }


def audit_domain(
    n: int, delta: int, factorization_limit: int | None = None
) -> dict[str, object]:
    require(gcd(n, delta) > 1, "full-stabilizer audit requires multiple lanes")
    states = all_configs(n)
    _, orbit_of = state_orbits(n, delta)
    adjacent = {
        index for index, state in enumerate(states) if lane_adjacent(n, delta, state)
    }
    same = {
        index for index, state in enumerate(states) if same_lane(n, delta, state)
    }
    outcomes: defaultdict[str, int] = defaultdict(int)
    break_groups: defaultdict[tuple[int, ...], dict[str, dict[str, object]]] = (
        defaultdict(dict)
    )
    coarse_groups: defaultdict[tuple[object, ...], dict[str, dict[str, object]]] = (
        defaultdict(dict)
    )
    first_x3_failure: dict[str, object] | None = None
    branch_count = 0
    factorization_checks = 0

    for metadata, branch in stabilizer_branches(n, delta):
        graph, _ = transition_graph(n, delta, branch)
        if factorization_limit is None or factorization_checks < factorization_limit:
            direct = quotient_edges_direct(graph, orbit_of)
            factored = quotient_edges_by_incidence(n, delta, branch)
            require(direct == factored, "source-addressed incidence factorization failed")
            factorization_checks += 1

        safe = safe_hit_indices(n, delta, branch, graph)
        require(adjacent <= safe <= same, "lane-stabilizer sandwich failed")
        breaks = tuple(metadata["break_pattern"])  # type: ignore[arg-type]
        if not breaks:
            require(safe == adjacent, "local-dihedral control failed")
        if safe == adjacent:
            outcome = "ADJ"
        elif safe == same:
            outcome = "SAME"
        else:
            outcome = "INTERMEDIATE"
        outcomes[outcome] += 1
        row = witness_row(metadata, safe)
        digest = row["safe_hit_digest"]
        break_groups[breaks].setdefault(str(digest), row)
        coarse_groups[branch_key(metadata)].setdefault(str(digest), row)
        if breaks and safe != same and first_x3_failure is None:
            first_x3_failure = row
        branch_count += 1

    break_variation = [
        {
            "break_pattern": list(key),
            "distinct_safe_hit_sets": len(rows),
            "witnesses": list(rows.values())[:2],
        }
        for key, rows in sorted(break_groups.items())
        if len(rows) > 1
    ]
    coarse_variation = [
        {
            "signature": {
                "break_pattern": list(key[0]),
                "ordinary_lane_permutation": list(key[1]),
                "restriction_cycle_types": [list(row) for row in key[2]],
            },
            "distinct_safe_hit_sets": len(rows),
            "witnesses": list(rows.values())[:2],
        }
        for key, rows in sorted(coarse_groups.items(), key=lambda item: repr(item[0]))
        if len(rows) > 1
    ]
    return {
        "n": n,
        "delta": delta,
        "lane_lengths": [len(cycle) for cycle in psi_cycles(n, delta)],
        "states": len(states),
        "orbits": max(orbit_of) + 1,
        "adjacent_states": len(adjacent),
        "same_lane_states": len(same),
        "stabilizer_branches": branch_count,
        "incidence_factorization_checks": factorization_checks,
        "outcomes": dict(sorted(outcomes.items())),
        "x3_holds_on_retained_domain": first_x3_failure is None,
        "first_x3_failure": first_x3_failure,
        "break_set_non_descent": break_variation,
        "strong_coarse_non_descent": coarse_variation,
    }


def build_result(
    max_n: int,
    selected_domains: tuple[tuple[int, int], ...] = (),
    factorization_limit: int | None = None,
) -> dict[str, object]:
    if max_n < 6:
        raise ValueError("max_n must be at least 6")
    domains: list[dict[str, object]] = []
    totals: defaultdict[str, int] = defaultdict(int)
    domains_to_run = selected_domains or tuple(
        (n, delta)
        for n in range(6, max_n + 1)
        for delta in range(1, n)
        if gcd(n, delta) > 1
    )
    for n, delta in domains_to_run:
        if n < 6 or not 1 <= delta < n or gcd(n, delta) == 1:
            raise ValueError(f"invalid multi-lane domain: {(n, delta)}")
        row = audit_domain(n, delta, factorization_limit)
        domains.append(row)
        totals["domains"] += 1
        totals["stabilizer_branches"] += int(row["stabilizer_branches"])
        totals["incidence_factorization_checks"] += int(
            row["incidence_factorization_checks"]
        )
        totals["x3_failures"] += int(not row["x3_holds_on_retained_domain"])
        totals["break_set_non_descent_domains"] += int(
            bool(row["break_set_non_descent"])
        )
        totals["strong_coarse_non_descent_domains"] += int(
            bool(row["strong_coarse_non_descent"])
        )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "min_n": min(n for n, _ in domains_to_run),
            "max_n": max(n for n, _ in domains_to_run),
            "domain_rule": "gcd(n, delta) > 1; full lane-partition stabilizer",
            "selected_domains": [list(row) for row in selected_domains],
            "factorization_limit_per_domain": factorization_limit,
        },
        "totals": dict(sorted(totals.items())),
        "domains": domains,
        "capacity_isolated_family_control": capacity_obstruction_control(),
        "claim_boundary": [
            "the incidence identity is algebraic; finite replay is only a control",
            "absence of a retained X3 failure is not an all-n theorem",
            "a finite matched pair proves non-descent only for the named quotient",
            "raw Safe-Hit does not establish typed transfer membership",
        ],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        metavar="N:DELTA",
        help="run only a selected multi-lane domain; may be repeated",
    )
    parser.add_argument(
        "--factorization-limit",
        type=int,
        help="check X0 on only the first N branches of each selected domain",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    selected_domains = tuple(
        tuple(int(value) for value in item.split(":"))
        for item in args.domain
    )
    if any(len(row) != 2 for row in selected_domains):
        raise ValueError("each --domain must have form N:DELTA")
    if args.factorization_limit is not None and args.factorization_limit < 0:
        raise ValueError("factorization limit must be nonnegative")
    result = build_result(
        args.max_n,
        selected_domains,  # type: ignore[arg-type]
        args.factorization_limit,
    )
    payload = json.dumps(result, indent=2, sort_keys=False) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
