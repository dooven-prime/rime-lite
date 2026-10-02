#!/usr/bin/env python3
"""Exact six-point replay of the Paper XXXV order-phase theorem.

The producer exhausts all 120 branch permutations in the normalized
one-lane system with (n, delta) = (6, 1). It independently checks the
24-state cyclic-order relation, its eight double-coset orbitals, reachable
order saturation, terminal-phase collapse, the exact order-phase witness
bijection, and the complete survivor-count formula.

The retained output is a bounded consistency control. The manuscript owns the
data-independent all-n proof; the paper-owned theorem note is a bound
supplementary proof artifact. This script does not establish any typed transfer
or projectability claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterable, TypeAlias


Injection: TypeAlias = tuple[int, int, int, int, int]
Order: TypeAlias = tuple[int, int, int, int, int]
Pair: TypeAlias = tuple[int, int]
Perm: TypeAlias = tuple[int, ...]
Survivor: TypeAlias = tuple[int, int, int]

N = 6
DELTA = 1
Q = tuple(range(N))
E = tuple(range(1, N))
LABELS = tuple(range(5))
SOURCE: Injection = (1, 2, 3, 4, 5)
SCHEMA = "rime.paper35.order-phase-audit.v2"
STATUS = "EXHAUSTIVE_N6_PHASE_COLLAPSE_CONTROL"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_rotation(values: tuple[int, ...]) -> tuple[int, ...]:
    return min(values[index:] + values[:index] for index in range(len(values)))


def order_of(state: Injection) -> Order:
    require(set(state) == set(E), "order requested outside the six-point section")
    coordinate_to_label = {coordinate: label for label, coordinate in enumerate(state)}
    values = tuple(coordinate_to_label[coordinate] for coordinate in E)
    return canonical_rotation(values)  # type: ignore[return-value]


def terminal_order(placement: Injection) -> Order:
    coordinate_to_label = {
        coordinate: label for label, coordinate in enumerate(placement)
    }
    values = tuple(
        coordinate_to_label[coordinate]
        for coordinate in Q
        if coordinate in coordinate_to_label
    )
    require(len(values) == 5, "terminal order lost a lineage")
    return canonical_rotation(values)  # type: ignore[return-value]


def all_injections() -> tuple[Injection, ...]:
    return tuple(permutations(E))  # type: ignore[return-value]


def all_orders() -> tuple[Order, ...]:
    return tuple(sorted({order_of(state) for state in all_injections()}))


def compose(left: Perm, right: Perm) -> Perm:
    require(len(left) == len(right), "permutation carrier mismatch")
    return tuple(left[right[index]] for index in range(len(left)))


def inverse(perm: Perm) -> Perm:
    result = [0] * len(perm)
    for source, target in enumerate(perm):
        result[target] = source
    require(set(result) == set(range(len(perm))), "inverse received a non-permutation")
    return tuple(result)


def powers(generator: Perm) -> tuple[Perm, ...]:
    identity = tuple(range(len(generator)))
    rows = [identity]
    current = identity
    while True:
        current = compose(generator, current)
        if current == identity:
            return tuple(rows)
        require(current not in rows, "permutation powers failed to close")
        rows.append(current)


def generated_subgroup(generators: tuple[Perm, ...]) -> frozenset[Perm]:
    require(generators, "subgroup generation requires a generator")
    degree = len(generators[0])
    require(all(len(generator) == degree for generator in generators), "generator degree mismatch")
    identity = tuple(range(degree))
    reached = {identity}
    queue = deque([identity])
    while queue:
        element = queue.popleft()
        for generator in generators:
            successor = compose(generator, element)
            if successor not in reached:
                reached.add(successor)
                queue.append(successor)
    return frozenset(reached)


FIVE_CYCLE: Perm = (1, 2, 3, 4, 0)
H = powers(FIVE_CYCLE)
require(len(H) == 5, "cyclic-order stabilizer has the wrong order")


def double_coset(perm: Perm) -> frozenset[Perm]:
    return frozenset(compose(compose(left, perm), right) for left in H for right in H)


def double_coset_representative(perm: Perm) -> Perm:
    return min(double_coset(perm))


def pattern_representatives() -> tuple[Perm, ...]:
    reps = {
        double_coset_representative(perm)
        for perm in permutations(range(5))
    }
    require(len(reps) == 8, "C5\\S5/C5 did not have eight classes")
    return tuple(sorted(reps))


PATTERN_REPS = pattern_representatives()
PATTERN_ID = {rep: f"P{index}" for index, rep in enumerate(PATTERN_REPS)}


def relative_pattern(source: Order, target: Order) -> Perm:
    source_rep: Perm = tuple(source)
    target_rep: Perm = tuple(target)
    relative = compose(inverse(source_rep), target_rep)
    return double_coset_representative(relative)


def branch_perm(values: tuple[int, ...]) -> Perm:
    require(tuple(sorted(values)) == E, "branch is not a permutation of E")
    return (0, *values)


def inverse_branch(branch: Perm) -> Perm:
    require(branch[0] == 0 and set(branch[1:]) == set(E), "invalid branch")
    return inverse(branch)


def branch_as_s5(branch: Perm) -> Perm:
    return tuple(branch[coordinate] - 1 for coordinate in E)


def epsilon(coordinate: int) -> int:
    return DELTA if coordinate == 0 else coordinate


def shift(state: Injection, exponent: int) -> Injection:
    return tuple((coordinate + exponent) % N for coordinate in state)  # type: ignore[return-value]


def apply_branch(branch: Perm, state: Injection) -> Injection:
    return tuple(branch[coordinate] for coordinate in state)  # type: ignore[return-value]


def phi(branch: Perm, label: int, state: Injection) -> Injection | None:
    pre = shift(apply_branch(branch, state), label)
    if {0, DELTA} <= set(pre):
        return None
    output = tuple(epsilon(coordinate) for coordinate in pre)
    require(set(output) == set(E), "guarded return left the normalized section")
    return output  # type: ignore[return-value]


def reachable_injections(branch: Perm) -> frozenset[Injection]:
    reached = {SOURCE}
    queue = deque([SOURCE])
    while queue:
        state = queue.popleft()
        for label in Q:
            successor = phi(branch, label, state)
            if successor is not None and successor not in reached:
                reached.add(successor)
                queue.append(successor)
    return frozenset(reached)


def order_relation(branch: Perm, order_index: dict[Order, int]) -> frozenset[tuple[int, int]]:
    edges = {
        (
            order_index[order_of(state)],
            order_index[order_of(apply_branch(branch, state))],
        )
        for state in all_injections()
    }
    return frozenset(edges)


def orbital_edges(rep: Perm, orders: tuple[Order, ...]) -> frozenset[tuple[int, int]]:
    return frozenset(
        (left, right)
        for left, source in enumerate(orders)
        for right, target in enumerate(orders)
        if relative_pattern(source, target) == rep
    )


def graph_reachability(
    edges: frozenset[tuple[int, int]], source: int
) -> frozenset[int]:
    adjacency: defaultdict[int, list[int]] = defaultdict(list)
    for left, right in edges:
        adjacency[left].append(right)
    reached = {source}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for successor in adjacency[vertex]:
            if successor not in reached:
                reached.add(successor)
                queue.append(successor)
    return frozenset(reached)


def formal_terminal_placements() -> tuple[tuple[Pair, Injection, int], ...]:
    rows: list[tuple[Pair, Injection, int]] = []
    for placement in permutations(Q, 5):
        if not {0, 1} <= set(placement):
            continue
        fused = tuple(index for index, value in enumerate(placement) if value in {0, 1})
        require(len(fused) == 2, "terminal kernel did not have two source labels")
        missing = tuple(sorted(set(Q) - set(placement)))
        require(len(missing) == 1, "six-point placement did not have one hole")
        rows.append((fused, placement, missing[0]))  # type: ignore[arg-type]
    require(len(rows) == 480, "formal terminal-placement count drift")
    return tuple(rows)


FORMAL_TERMINALS = formal_terminal_placements()


def candidate_preimage(branch: Perm, placement: Injection, hole: int) -> Injection:
    rotated = shift(placement, -hole)
    require(0 not in rotated, "candidate hole did not delete coordinate zero")
    require(set(rotated) == set(E), "candidate preimage missed the normalized carrier")
    branch_inverse = inverse_branch(branch)
    return tuple(branch_inverse[coordinate] for coordinate in rotated)  # type: ignore[return-value]


def phase_pairs(
    branch: Perm, reachable_orders: frozenset[Order]
) -> frozenset[tuple[Injection, int]]:
    accepted: set[tuple[Injection, int]] = set()
    for _fused, placement, hole in FORMAL_TERMINALS:
        preimage = candidate_preimage(branch, placement, hole)
        if order_of(preimage) in reachable_orders:
            accepted.add((placement, hole))
    return frozenset(accepted)


def direct_terminal_witnesses(
    branch: Perm, reached: frozenset[Injection]
) -> frozenset[tuple[Injection, int]]:
    witnesses: set[tuple[Injection, int]] = set()
    for state in reached:
        branch_state = apply_branch(branch, state)
        for terminal_label in Q:
            placement = shift(branch_state, terminal_label)
            if {0, 1} <= set(placement):
                witnesses.add((placement, terminal_label))
    return frozenset(witnesses)


def fused_pair(placement: Injection) -> Pair:
    pair = tuple(index for index, value in enumerate(placement) if value in {0, 1})
    require(len(pair) == 2, "placement did not define one fused pair")
    return pair  # type: ignore[return-value]


def survivor_spectra(
    accepted: frozenset[tuple[Injection, int]],
) -> dict[Pair, frozenset[Survivor]]:
    rows: dict[Pair, set[Survivor]] = {
        pair: set() for pair in combinations(LABELS, 2)
    }
    for placement, _hole in accepted:
        pair = fused_pair(placement)
        survivors = tuple(index for index in LABELS if index not in pair)
        rows[pair].add(tuple(placement[index] for index in survivors))  # type: ignore[arg-type]
    return {pair: frozenset(values) for pair, values in rows.items()}


def boundary_spectra(
    accepted: frozenset[tuple[Injection, int]],
) -> dict[Pair, frozenset[Injection]]:
    rows: dict[Pair, set[Injection]] = {
        pair: set() for pair in combinations(LABELS, 2)
    }
    for placement, _hole in accepted:
        pair = fused_pair(placement)
        incidence = tuple(epsilon(coordinate) for coordinate in placement)
        rows[pair].add(incidence)  # type: ignore[arg-type]
    return {pair: frozenset(values) for pair, values in rows.items()}


def survivor_order_multiplicities(
    reachable_orders: frozenset[Order],
) -> dict[Pair, int]:
    rows: dict[Pair, int] = {}
    for pair in combinations(LABELS, 2):
        survivors = tuple(label for label in LABELS if label not in pair)
        allowed: set[tuple[int, int, int]] = set()
        for survivor_order in permutations(survivors):
            if any(
                canonical_rotation((*fused_order, *survivor_order))
                in reachable_orders
                for fused_order in permutations(pair)
            ):
                allowed.add(survivor_order)  # type: ignore[arg-type]
        rows[pair] = len(allowed)
    return rows


def digest(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def encoded_phase(accepted: frozenset[tuple[Injection, int]]) -> list[list[object]]:
    return [[list(placement), hole] for placement, hole in sorted(accepted)]


def encoded_spectra(
    spectra: dict[Pair, frozenset[Survivor]],
) -> list[list[object]]:
    return [
        [list(pair), [list(row) for row in sorted(rows)]]
        for pair, rows in sorted(spectra.items())
    ]


def encoded_boundary(
    spectra: dict[Pair, frozenset[Injection]],
) -> list[list[object]]:
    return [
        [list(pair), [list(row) for row in sorted(rows)]]
        for pair, rows in sorted(spectra.items())
    ]


def branch_analysis(
    branch: Perm,
    orders: tuple[Order, ...],
    order_index: dict[Order, int],
    injections_by_order: dict[Order, frozenset[Injection]],
    orbital_by_rep: dict[Perm, frozenset[tuple[int, int]]],
) -> dict[str, object]:
    branch_s5_perm = branch_as_s5(branch)
    subgroup = generated_subgroup((FIVE_CYCLE, branch_s5_perm))
    subgroup_names = {5: "C5", 10: "D10", 20: "F20", 60: "A5", 120: "S5"}
    require(len(subgroup) in subgroup_names, "unexpected overgroup of C5 in S5")
    relation = order_relation(branch, order_index)
    relation_patterns = {
        relative_pattern(orders[left], orders[right]) for left, right in relation
    }
    require(len(relation_patterns) == 1, "n=6 order relation occupied multiple orbitals")
    pattern_rep = next(iter(relation_patterns))
    require(relation == orbital_by_rep[pattern_rep], "orbital reconstruction failed")

    reached = reachable_injections(branch)
    reached_as_s5 = frozenset(
        tuple(coordinate - 1 for coordinate in state) for state in reached
    )
    require(reached_as_s5 == subgroup, "guarded injection fiber differed from <C5, g_a>")
    reached_orders = frozenset(order_of(state) for state in reached)
    saturated = frozenset(
        state for order in reached_orders for state in injections_by_order[order]
    )
    require(reached == saturated, "reachable order fiber was not saturated")

    source_order = order_index[order_of(SOURCE)]
    order_reach = graph_reachability(relation, source_order)
    actual_order_ids = frozenset(order_index[order] for order in reached_orders)
    require(order_reach == actual_order_ids, "24-state order reduction was not exact")
    require(
        len(reached_orders) == len(subgroup) // len(H),
        "reachable-order count differed from the subgroup coset count",
    )

    accepted = phase_pairs(branch, reached_orders)
    direct = direct_terminal_witnesses(branch, reached)
    require(accepted == direct, "order-phase set differed from direct witnesses")
    collapsed = frozenset(
        (placement, hole)
        for _pair, placement, hole in FORMAL_TERMINALS
        if terminal_order(placement) in reached_orders
    )
    require(accepted == collapsed, "terminal phase did not collapse to cyclic order")
    require(
        all(hole == next(iter(set(Q) - set(placement))) for placement, hole in accepted),
        "accepted terminal exponent was not the unique hole",
    )

    survivors = survivor_spectra(accepted)
    boundary = boundary_spectra(accepted)
    multiplicities = survivor_order_multiplicities(reached_orders)
    coordinate_choices = 4
    require(
        all(
            len(survivors[pair]) == multiplicities[pair] * coordinate_choices
            for pair in multiplicities
        ),
        "survivor spectrum violated the order-multiplicity formula",
    )
    phase_encoded = encoded_phase(accepted)
    survivor_encoded = encoded_spectra(survivors)
    boundary_encoded = encoded_boundary(boundary)
    pair_rows = {
        f"{pair[0]}-{pair[1]}": len(rows)
        for pair, rows in sorted(survivors.items())
    }
    return {
        "branch_perm": branch,
        "branch_s5": branch_s5_perm,
        "generated_subgroup": subgroup,
        "generated_subgroup_order": len(subgroup),
        "generated_subgroup_name": subgroup_names[len(subgroup)],
        "pattern_rep": pattern_rep,
        "pattern_id": PATTERN_ID[pattern_rep],
        "relation": relation,
        "reached": reached,
        "reachable_orders": reached_orders,
        "accepted": accepted,
        "survivors": survivors,
        "boundary": boundary,
        "row": {
            "branch": list(branch[1:]),
            "pattern_id": PATTERN_ID[pattern_rep],
            "relation_edges": len(relation),
            "reachable_injections": len(reached),
            "reachable_orders": len(reached_orders),
            "generated_subgroup_order": len(subgroup),
            "generated_subgroup_name": subgroup_names[len(subgroup)],
            "order_fiber_saturation": True,
            "order_reachability_exact": True,
            "pattern_reconstruction_exact": True,
            "formal_terminal_placements": len(FORMAL_TERMINALS),
            "phase_witnesses": len(accepted),
            "terminal_realization_exact": True,
            "order_phase_bijection_exact": True,
            "phase_collapse_exact": True,
            "survivor_count_formula_exact": True,
            "hittable_pairs": [
                list(pair) for pair, rows in sorted(survivors.items()) if rows
            ],
            "survivor_spectrum_sizes": pair_rows,
            "survivor_order_multiplicities": {
                f"{pair[0]}-{pair[1]}": multiplicities[pair]
                for pair in sorted(multiplicities)
            },
            "phase_digest": digest(phase_encoded),
            "survivor_digest": digest(survivor_encoded),
            "boundary_digest": digest(boundary_encoded),
        },
    }


def normalizes_h(perm: Perm) -> bool:
    conjugates = {compose(compose(perm, h), inverse(perm)) for h in H}
    return conjugates == set(H)


def build_result() -> dict[str, object]:
    injections = all_injections()
    orders = all_orders()
    require(len(injections) == 120, "lineage-bijection count drift")
    require(len(orders) == 24, "cyclic-order count drift")
    order_index = {order: index for index, order in enumerate(orders)}
    injections_by_order = {
        order: frozenset(state for state in injections if order_of(state) == order)
        for order in orders
    }
    require(
        {len(rows) for rows in injections_by_order.values()} == {5},
        "order-fiber size drift",
    )
    orbital_by_rep = {
        rep: orbital_edges(rep, orders) for rep in PATTERN_REPS
    }
    require(
        sorted(len(rows) for rows in orbital_by_rep.values())
        == [24, 24, 24, 24, 120, 120, 120, 120],
        "order-orbital edge-size drift",
    )

    analyses: list[dict[str, object]] = []
    for values in permutations(E):
        analyses.append(
            branch_analysis(
                branch_perm(values),
                orders,
                order_index,
                injections_by_order,
                orbital_by_rep,
            )
        )

    groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for analysis in analyses:
        groups[str(analysis["pattern_id"])].append(analysis)
    require(len(groups) == 8, "branch grouping did not use all eight patterns")
    branch_class_sizes = sorted(len(rows) for rows in groups.values())
    require(
        branch_class_sizes == [5, 5, 5, 5, 25, 25, 25, 25],
        "branch grouping did not have the expected double-coset sizes",
    )

    normalizer_branches = [
        analysis
        for analysis in analyses
        if normalizes_h(analysis["branch_s5"])  # type: ignore[arg-type]
    ]
    require(len(normalizer_branches) == 20, "C5 normalizer order drift")
    require(
        all(len(double_coset(analysis["pattern_rep"])) == 5 for analysis in normalizer_branches),  # type: ignore[arg-type]
        "normalizer branch entered a size-25 class",
    )

    pattern_rows: list[dict[str, object]] = []
    for pattern_id in sorted(groups):
        rows = groups[pattern_id]
        rep = rows[0]["pattern_rep"]
        require(isinstance(rep, tuple), "pattern representative missing")
        require(all(row["pattern_rep"] == rep for row in rows), "pattern id collision")
        pattern_rows.append(
            {
                "pattern_id": pattern_id,
                "representative": list(rep),
                "double_coset_size": len(double_coset(rep)),
                "branch_count": len(rows),
                "relation_edges": len(rows[0]["relation"]),  # type: ignore[arg-type]
                "distinct_phase_signatures": len(
                    {row["row"]["phase_digest"] for row in rows}  # type: ignore[index]
                ),
                "distinct_survivor_signatures": len(
                    {row["row"]["survivor_digest"] for row in rows}  # type: ignore[index]
                ),
                "reachable_injection_counts": sorted(
                    {row["row"]["reachable_injections"] for row in rows}  # type: ignore[index]
                ),
                "reachable_order_counts": sorted(
                    {row["row"]["reachable_orders"] for row in rows}  # type: ignore[index]
                ),
                "phase_witness_counts": sorted(
                    {row["row"]["phase_witnesses"] for row in rows}  # type: ignore[index]
                ),
                "hittable_pair_counts": sorted(
                    {len(row["row"]["hittable_pairs"]) for row in rows}  # type: ignore[index]
                ),
                "generated_subgroup_orders": sorted(
                    {row["generated_subgroup_order"] for row in rows}
                ),
                "generated_subgroup_names": sorted(
                    {row["generated_subgroup_name"] for row in rows}
                ),
            }
        )

    phase_descends = all(row["distinct_phase_signatures"] == 1 for row in pattern_rows)
    survivor_descends = all(
        row["distinct_survivor_signatures"] == 1 for row in pattern_rows
    )
    require(phase_descends, "phase did not descend through the exact order pattern")
    require(survivor_descends, "survivors did not descend through the exact order pattern")

    subgroup_groups: defaultdict[frozenset[Perm], list[dict[str, object]]] = defaultdict(list)
    for analysis in analyses:
        subgroup = analysis["generated_subgroup"]
        require(isinstance(subgroup, frozenset), "generated subgroup missing")
        subgroup_groups[subgroup].append(analysis)
    require(len(subgroup_groups) == 5, "six-point branches did not produce five overgroups")
    subgroup_rows: list[dict[str, object]] = []
    for subgroup, rows in sorted(subgroup_groups.items(), key=lambda item: len(item[0])):
        names = {row["generated_subgroup_name"] for row in rows}
        require(len(names) == 1, "one subgroup received multiple names")
        phase_digests = {row["row"]["phase_digest"] for row in rows}  # type: ignore[index]
        survivor_digests = {row["row"]["survivor_digest"] for row in rows}  # type: ignore[index]
        require(len(phase_digests) == 1, "phase did not descend through the generated subgroup")
        require(len(survivor_digests) == 1, "survivors did not descend through the generated subgroup")
        subgroup_rows.append(
            {
                "group_name": next(iter(names)),
                "group_order": len(subgroup),
                "pattern_ids": sorted({str(row["pattern_id"]) for row in rows}),
                "branch_count": len(rows),
                "reachable_order_count": len(subgroup) // len(H),
                "distinct_phase_signatures": len(phase_digests),
                "distinct_survivor_signatures": len(survivor_digests),
            }
        )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "n": N,
            "delta": DELTA,
            "source": list(SOURCE),
            "branch_permutations": 120,
            "lineage_bijections": 120,
            "cyclic_orders": 24,
            "formal_terminal_placements": len(FORMAL_TERMINALS),
            "complete_branch_scan": True,
        },
        "double_coset_control": {
            "group": "C5\\S5/C5",
            "pattern_classes": 8,
            "branch_class_sizes": branch_class_sizes,
            "order_orbital_edge_sizes": sorted(
                len(rows) for rows in orbital_by_rep.values()
            ),
            "normalizer_order": len(normalizer_branches),
            "singleton_pattern_per_branch": all(
                len({relative_pattern(orders[left], orders[right]) for left, right in analysis["relation"]}) == 1  # type: ignore[index]
                for analysis in analyses
            ),
            "status": "EXACT_EIGHT_ORBITAL_GROUPING_CONTROL",
        },
        "exact_reduction_checks": {
            "o0_order_fiber_saturation_all_branches": True,
            "o1_order_reachability_all_branches": True,
            "o1a_pattern_reconstruction_all_branches": True,
            "p0_terminal_realization_all_branches": True,
            "op_same_witness_bijection_all_branches": True,
            "unique_hole_phase_all_formal_placements": True,
            "phase_collapse_all_formal_placements": True,
            "survivor_count_formula_all_pairs": True,
        },
        "pattern_classes": pattern_rows,
        "subgroup_collapse_control": {
            "formula": "Omega_a = <C5,g_a>/C5 up to the fixed action convention",
            "overgroup_strata": subgroup_rows,
            "phase_descends_through_generated_subgroup_on_n6": True,
            "survivor_descends_through_generated_subgroup_on_n6": True,
            "status": "EXACT_N6_SUBGROUP_COLLAPSE_CONTROL",
        },
        "branch_rows": [analysis["row"] for analysis in analyses],
        "all_n_theorem_replay_control": {
            "phase_descends_through_pattern_on_n6": phase_descends,
            "survivor_spectrum_descends_through_pattern_on_n6": survivor_descends,
            "phase_collapse_replayed": True,
            "survivor_count_formula_replayed": True,
            "status": "EXACT_N6_REPLAY_OF_ORDER_PHASE_SURVIVOR_THEOREM",
        },
        "claim_boundary": [
            "the audit exhausts only the declared n=6 branch fiber",
            "the eight-class grouping is an exact finite group-action control",
            "the manuscript owns the all-n phase-collapse and survivor theorems; the theorem note is a bound supplementary proof artifact",
            "the finite replay is not the proof of an all-n statement",
            "raw terminal incidence does not establish typed transfer membership or projectability",
        ],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result()
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
