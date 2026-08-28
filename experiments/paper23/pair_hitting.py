#!/usr/bin/env python3
"""Pair-hitting representation and pair-distance packing certificates.

For a reachable subset T, let d2(x,y) be the shortest word merging the
distinct pair {x,y}.  Deterministic rank collapse has the exact identity

    omega(T) = min_{ {x,y} subset T } d2(x,y).

Thus the unit-capacity branch can be studied in the pair automaton.  For an
integer L, form the conflict graph with an edge when d2(x,y) <= L and define
P_A(L) as its independence number.  If r > P_A(L), every r-subset contains
a pair hit within L steps, so Omega_r <= L.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import deque
from math import comb
from pathlib import Path
from typing import Any

from fiber_incidence_controls import layer_incidence_controls
from path_potential import cerny_transition
from registry import (
    Transition,
    compose_maps,
    fiber_excess,
    image_subset,
    kernel_refines,
    pair_merge_distances,
    payload_digest,
    rank,
    reachable_subset_automaton,
    shortest_subset_reset_word,
    transformation_for_word,
    transformation_kernel_partition,
    transition_monoid_with_words,
)


def _rank_escape_witness(
    transition: Transition,
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
    start: tuple[int, ...],
) -> dict[str, Any] | None:
    rank_value = len(start)
    distance = {start: 0}
    words = {start: tuple()}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for letter_index, target in enumerate(edges[current]):
            if len(target) == rank_value and target not in distance:
                distance[target] = distance[current] + 1
                words[target] = words[current] + (letter_index,)
                queue.append(target)
    exits = [
        (
            distance[source] + 1,
            words[source] + (letter_index,),
            source,
            target,
            letter_index,
        )
        for source in distance
        for letter_index, target in enumerate(edges[source])
        if len(target) < rank_value
    ]
    if not exits:
        return None
    segment_length = min(row[0] for row in exits)
    shortest_exits = [row for row in exits if row[0] == segment_length]
    best_excess = max(
        fiber_excess(transition[row[4]], row[2]) for row in shortest_exits
    )
    best_shortest_exits = [
        row for row in shortest_exits
        if fiber_excess(transition[row[4]], row[2]) == best_excess
    ]
    segment_length, word, source, target, terminal_letter = min(
        best_shortest_exits
    )

    current = start
    prefix_rows = []
    for letter_index in word[:-1]:
        successor = edges[current][letter_index]
        prefix_rows.append({
            "source": list(current),
            "letter": letter_index,
            "target": list(successor),
            "injective_on_current_subset": len(successor) == len(current),
        })
        current = successor
    terminal_map: dict[int, list[int]] = {}
    for state in source:
        terminal_map.setdefault(transition[terminal_letter][state], []).append(state)
    collision_fibers = [
        sorted(fiber) for fiber in terminal_map.values() if len(fiber) > 1
    ]
    collision_pairs = [
        list(pair)
        for fiber in collision_fibers
        for pair in itertools.combinations(fiber, 2)
    ]
    excess = fiber_excess(transition[terminal_letter], source)
    return {
        "segment_length": segment_length,
        "word": list(word),
        "rank_preserving_prefix": list(word[:-1]),
        "prefix_transport": prefix_rows,
        "injective_prefix_verified": all(
            row["injective_on_current_subset"] for row in prefix_rows
        ),
        "terminal_source": list(source),
        "terminal_letter": terminal_letter,
        "terminal_target": list(target),
        "terminal_fiber_excess": excess,
        "best_shortest_escape_excess": best_excess,
        "terminal_collision_fibers": collision_fibers,
        "terminal_collision_pairs": collision_pairs,
        "unit_defect_unique_pair": excess == 1 and len(collision_pairs) == 1,
    }


def nearest_pair_distance(
    subset: tuple[int, ...],
    pair_distances: dict[tuple[int, int], int | None],
) -> int | None:
    values = [
        pair_distances[tuple(sorted(pair))]
        for pair in itertools.combinations(subset, 2)
    ]
    finite = [value for value in values if value is not None]
    return min(finite) if finite else None


def _mathematical_value(value: int | None) -> int | str:
    return value if value is not None else "infinity"


def _kernel_corridor_certificate(
    transition: Transition,
    reaching_word: tuple[int, ...],
    subset: tuple[int, ...],
    omega: int | None,
    escape_witness: dict[str, Any] | None,
) -> dict[str, Any]:
    """Certify a same-kernel suffix corridor and a selected first exit."""
    n = len(transition[0])
    current = transformation_for_word(reaching_word, transition, n)
    base_kernel = transformation_kernel_partition(current)
    prefix_rows = []
    if escape_witness is not None:
        for prefix_length, letter_index in enumerate(
            escape_witness["word"], start=1
        ):
            current = compose_maps(current, transition[letter_index])
            current_kernel = transformation_kernel_partition(current)
            if prefix_length < escape_witness["segment_length"]:
                prefix_rows.append({
                    "suffix_prefix_length": prefix_length,
                    "letter": letter_index,
                    "kernel_partition": [list(block) for block in current_kernel],
                    "equals_base_kernel": current_kernel == base_kernel,
                })
        terminal_kernel = transformation_kernel_partition(current)
        unit_exit = escape_witness["best_shortest_escape_excess"] == 1
        cover = (
            kernel_refines(base_kernel, terminal_kernel)
            and len(terminal_kernel) == len(base_kernel) - 1
        )
    else:
        terminal_kernel = None
        unit_exit = False
        cover = False
    plateau_verified = all(
        row["equals_base_kernel"] for row in prefix_rows
    )
    return {
        "reaching_word": list(reaching_word),
        "reached_subset_verified": image_subset(
            transformation_for_word(reaching_word, transition, n)
        ) == subset,
        "base_kernel_partition": [list(block) for block in base_kernel],
        "same_kernel_suffix_ball_radius": (
            "all_finite_lengths" if omega is None else max(omega - 1, 0)
        ),
        "suffix_ball_equivalence_status": "Exact theorem from rank/kernel monotonicity",
        "selected_prefix_kernel_rows": prefix_rows,
        "selected_prefix_plateau_verified": plateau_verified,
        "terminal_kernel_partition": (
            None if terminal_kernel is None
            else [list(block) for block in terminal_kernel]
        ),
        "terminal_kernel_coarsens_base": (
            None if terminal_kernel is None
            else kernel_refines(base_kernel, terminal_kernel)
        ),
        "terminal_kernel_block_loss": (
            None if terminal_kernel is None
            else len(base_kernel) - len(terminal_kernel)
        ),
        "all_shortest_exits_unit": unit_exit,
        "unit_first_exit_cover_verified": None if not unit_exit else (
            plateau_verified and cover
        ),
    }


def maximum_pair_packing(
    state_count: int,
    pair_distances: dict[tuple[int, int], int | None],
    threshold: int,
) -> tuple[int, list[int]]:
    """Return P_A(L) and one maximum subset with all pair distances > L."""
    if threshold < 0:
        raise ValueError("threshold must be nonnegative")
    states = tuple(range(state_count))
    best: tuple[int, ...] = tuple()
    for size in range(state_count, -1, -1):
        for subset in itertools.combinations(states, size):
            if all(
                pair_distances[tuple(sorted(pair))] is None
                or pair_distances[tuple(sorted(pair))] > threshold
                for pair in itertools.combinations(subset, 2)
            ):
                return size, list(subset)
    return 0, []


def packing_threshold_for_rank(
    state_count: int,
    pair_distances: dict[tuple[int, int], int | None],
    rank_value: int,
) -> int | None:
    """Return the least L for which P_A(L)<rank_value."""
    finite = [value for value in pair_distances.values() if value is not None]
    max_threshold = max(finite, default=0)
    for threshold in range(max_threshold + 1):
        packing, _witness = maximum_pair_packing(
            state_count, pair_distances, threshold
        )
        if packing < rank_value:
            return threshold
    return None


def pair_packing_profile(
    transition: Transition,
    pair_distances: dict[tuple[int, int], int | None],
) -> dict[str, Any]:
    """Return the full finite P_A(L) profile and common-transversal checks."""
    state_count = len(transition[0])
    finite = [value for value in pair_distances.values() if value is not None]
    max_finite = max(finite, default=0)
    monoid = transition_monoid_with_words(transition)
    rows = []
    previous = state_count
    for threshold in range(max_finite + 1):
        packing, witness = maximum_pair_packing(
            state_count, pair_distances, threshold
        )
        bounded_transformations = [
            transformation
            for transformation, word in monoid.items()
            if len(word) <= threshold
        ]
        minimum_rank = min(map(rank, bounded_transformations))
        rows.append({
            "L": threshold,
            "P_A_L": packing,
            "packing_witness": witness,
            "conflict_edge_count": sum(
                value is not None and value <= threshold
                for value in pair_distances.values()
            ),
            "minimum_transformation_rank_through_L": minimum_rank,
            "common_transversal_rank_bound_holds": packing <= minimum_rank,
            "strictly_improves_single_kernel_rank_bound": packing < minimum_rank,
            "monotone_from_previous": packing <= previous,
        })
        previous = packing
    eventual_packing, eventual_witness = maximum_pair_packing(
        state_count, pair_distances, max_finite
    )
    return {
        "rows": rows,
        "maximum_finite_pair_distance": max_finite if finite else None,
        "eventual_infinite_pair_packing": eventual_packing,
        "eventual_infinite_pair_packing_witness": eventual_witness,
        "all_monotonicity_checks_passed": all(
            row["monotone_from_previous"] for row in rows
        ),
        "all_common_transversal_rank_bounds_passed": all(
            row["common_transversal_rank_bound_holds"] for row in rows
        ),
    }


def unit_reachable_packing_profile(
    equality_rows: list[dict[str, Any]],
    state_count: int,
    max_threshold: int,
) -> dict[str, Any]:
    """Return reachable packing restricted to statewise unit-capacity rows."""
    rows = []
    for threshold in range(max_threshold + 1):
        candidates = [
            row for row in equality_rows
            if row["selected_escape"] is not None
            and row["selected_escape"]["best_shortest_escape_excess"] == 1
            and (
                row["nearest_pair_distance"] is None
                or row["nearest_pair_distance"] > threshold
            )
        ]
        witness = max(
            candidates,
            key=lambda row: (row["rank"], tuple(row["subset"])),
            default=None,
        )
        rows.append({
            "L": threshold,
            "P_A_U_reachable_L": 0 if witness is None else witness["rank"],
            "witness_subset": None if witness is None else witness["subset"],
            "witness_wait": (
                None if witness is None else witness["nearest_pair_distance"]
            ),
        })
    u_by_rank = {}
    for rank_value in range(2, state_count + 1):
        waits = [
            row["omega"]
            for row in equality_rows
            if row["rank"] == rank_value
            and row["selected_escape"] is not None
            and row["selected_escape"]["best_shortest_escape_excess"] == 1
        ]
        u_by_rank[rank_value] = max(waits, default=0)
    running = 0
    unit_tail = {}
    for index in range(state_count, 1, -1):
        running = max(running, u_by_rank[index])
        unit_tail[index] = running
    inversion_rows = []
    for index in range(2, state_count + 1):
        inverse = min(
            row["L"] for row in rows
            if row["P_A_U_reachable_L"] < index
        )
        inversion_rows.append({
            "j": index,
            "unit_wait_tail_u_bar_j": unit_tail[index],
            "packing_inverse_threshold": inverse,
            "inversion_holds": inverse == unit_tail[index],
        })
    unit_wait_tail_area = sum(unit_tail.values())
    reachable_unit_packing_area = sum(
        max(row["P_A_U_reachable_L"] - 1, 0) for row in rows
    )
    return {
        "rows": rows,
        "u_r_by_rank": {
            str(rank_value): value
            for rank_value, value in sorted(u_by_rank.items())
        },
        "unit_wait_tail_by_index": {
            str(index): value for index, value in sorted(unit_tail.items())
        },
        "packing_inversion_rows": inversion_rows,
        "all_packing_inversion_checks_passed": all(
            row["inversion_holds"] for row in inversion_rows
        ),
        "unit_wait_tail_area": unit_wait_tail_area,
        "reachable_unit_packing_area": reachable_unit_packing_area,
        "packing_area_identity_holds": (
            unit_wait_tail_area == reachable_unit_packing_area
        ),
        "definition": (
            "maximum cardinality of a reachable subset T with "
            "best-shortest-exit excess one and omega(T)>L"
        ),
        "claim_status": "Exact finite statewise unit-branch certificate",
    }


def pair_hitting_certificate(transition: Transition) -> dict[str, Any]:
    """Compute exact pair-hitting identities and packing bounds."""
    n = len(transition[0])
    distance, reaching_words, edges = reachable_subset_automaton(transition)
    pair_distances = pair_merge_distances(transition)
    packing_profile = pair_packing_profile(transition, pair_distances)
    equality_rows: list[dict] = []
    equality_failures: list[dict] = []
    by_rank: dict[int, list[tuple[int, ...]]] = {}
    for subset in distance:
        if len(subset) <= 1:
            continue
        by_rank.setdefault(len(subset), []).append(subset)
        witness = _rank_escape_witness(transition, edges, subset)
        omega = None if witness is None else witness["segment_length"]
        nearest = nearest_pair_distance(subset, pair_distances)
        kernel_corridor = _kernel_corridor_certificate(
            transition,
            reaching_words[subset],
            subset,
            omega,
            witness,
        )
        row = {
            "subset": list(subset),
            "rank": len(subset),
            "omega": omega,
            "omega_mathematical_value": _mathematical_value(omega),
            "nearest_pair_distance": nearest,
            "nearest_pair_mathematical_value": _mathematical_value(nearest),
            "identity_holds": omega == nearest,
            "selected_escape": witness,
            "kernel_corridor": kernel_corridor,
        }
        equality_rows.append(row)
        if omega != nearest:
            equality_failures.append(row)

    rank_rows = []
    for rank_value, subsets in sorted(by_rank.items()):
        layer_rows = [row for row in equality_rows if row["rank"] == rank_value]
        infinite_subset_count = sum(row["omega"] is None for row in layer_rows)
        exact_omega = (
            None if infinite_subset_count else max(row["omega"] for row in layer_rows)
        )
        threshold = packing_threshold_for_rank(n, pair_distances, rank_value)
        packing = None
        witness = None
        if threshold is not None:
            packing, witness = maximum_pair_packing(n, pair_distances, threshold)
        rank_rows.append({
            "rank": rank_value,
            "reachable_subset_count": len(subsets),
            "Omega_r_exact": exact_omega,
            "Omega_r_mathematical_value": _mathematical_value(exact_omega),
            "infinite_escape_subset_count": infinite_subset_count,
            "packing_threshold": threshold,
            "packing_threshold_mathematical_value": _mathematical_value(threshold),
            "packing_number_at_threshold": packing,
            "packing_witness": witness,
            "packing_bound_holds": (
                None if threshold is None
                else exact_omega is not None and exact_omega <= threshold
            ),
        })

    controls = layer_incidence_controls(transition)
    unit_rows = [
        rank_value for rank_value, row in controls.items()
        if row.get("status") == "FINITE_LAYER_ESCAPE"
        and row.get("epsilon_r") == 1
    ]
    high_rows = [
        rank_value for rank_value, row in controls.items()
        if row.get("status") == "FINITE_LAYER_ESCAPE"
        and row.get("epsilon_r", 0) > 1
    ]
    reset = shortest_subset_reset_word(transition)
    unit_packing = unit_reachable_packing_profile(
        equality_rows,
        n,
        packing_profile["maximum_finite_pair_distance"] or 0,
    )
    pin_frankl_checkpoints = []
    if reset is not None:
        for codimension in range(1, n):
            threshold = comb(codimension + 1, 2)
            packing, witness = maximum_pair_packing(
                n, pair_distances, threshold
            )
            bound = n - codimension
            pin_frankl_checkpoints.append({
                "codimension_parameter_t": codimension,
                "L": threshold,
                "P_A_L": packing,
                "pin_frankl_upper_bound": bound,
                "packing_witness": witness,
                "bound_holds": packing <= bound,
                "attains_bound": packing == bound,
            })
    return {
        "carrier": "pair_hitting_representation",
        "pair_distance_definition": "d2(x,y)=min{|w|: delta(x,w)=delta(y,w)}",
        "packing_definition": "P_A(L)=max{|T|: all distinct pairs in T have d2>L}",
        "pair_distances": [
            {
                "pair": list(pair),
                "distance": value,
                "mathematical_value": value if value is not None else "infinity",
            }
            for pair, value in sorted(pair_distances.items())
        ],
        "identity_rows": equality_rows,
        "identity_failures": equality_failures,
        "identity_row_count": len(equality_rows),
        "infinite_identity_row_count": sum(
            row["omega"] is None for row in equality_rows
        ),
        "rank_profile": rank_rows,
        "packing_profile": packing_profile,
        "unit_reachable_packing_profile": unit_packing,
        "pin_frankl_packing_checkpoints": pin_frankl_checkpoints,
        "statewise_waiting_capacity_profile": {
            str(rank_value): {
                "epsilon_r": row.get("epsilon_r"),
                "kappa_r": row.get("kappa_r"),
                "statewise_ratio_chi_r": row.get("statewise_ratio_chi_r"),
                "unit_shortest_escape_state_count": row.get(
                    "unit_shortest_escape_state_count"
                ),
                "high_capacity_shortest_escape_state_count": row.get(
                    "high_capacity_shortest_escape_state_count"
                ),
                "Omega_r_unit_states": row.get("Omega_r_unit_states"),
                "high_capacity_ratio_r": row.get("high_capacity_ratio_r"),
                "chi_at_most_kappa": row.get("chi_at_most_kappa"),
                "statewise_branch_identity_holds": row.get(
                    "statewise_branch_identity_holds"
                ),
            }
            for rank_value, row in sorted(controls.items())
            if row.get("status") == "FINITE_LAYER_ESCAPE"
        },
        "packing_equivalent_semantics": (
            "T is L-separated iff every word of length at most L is "
            "injective on T; equivalently T is a common partial transversal "
            "of the corresponding kernel partitions"
        ),
        "unit_capacity_ranks_U": sorted(unit_rows),
        "high_capacity_ranks_H": sorted(high_rows),
        "shortest_reset_depth": None if reset is None else len(reset),
        "claim_boundary": {
            "pair_hitting_identity": "Exact finite theorem",
            "packing_implication": "Exact finite theorem",
            "unit_defect_pair_representation": (
                "Exact when the selected terminal fiber excess is one"
            ),
            "automaton_specific_PAL": "Exact finite certificate",
            "kernel_common_transversal_equivalence": "Exact finite theorem",
            "single_kernel_rank_upper_bound": "Exact finite theorem",
            "statewise_chi_refinement": "Exact finite theorem",
            "unit_reachable_packing": "Exact finite certificate",
            "reachable_unit_packing_inversion": "Exact finite theorem",
            "same_kernel_suffix_corridor": "Exact finite theorem",
            "unit_plateau_kernel_cover": "Exact finite theorem",
            "pin_frankl_packing_profile": (
                "Equivalent reformulation of imported Pin--Frankl bounds"
            ),
            "universal_PnL_formula": "Open; not inferred from finite data",
            "quadratic_consequence": "Open",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = pair_hitting_certificate(cerny_transition(args.states))
    payload = {
        "schema": "rime.synchronizing-automata.pair-hitting-packing.v1",
        "transition_family": "Cerny",
        "result": result,
    }
    payload["content_sha256"] = payload_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "states": args.states,
        "identity_failures": len(result["identity_failures"]),
        "rank_profile": result["rank_profile"],
        "U": result["unit_capacity_ranks_U"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
