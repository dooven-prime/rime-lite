#!/usr/bin/env python3
"""Matched collision-exposure audit for the mixed rank-four classes.

The audit fixes mass partition and canonical K_d occupancy, then compares
local-descent placements with semigroup-only failures inside the three mixed
signature classes.  Pairwise packet exposure is computed on exact labelled
rank-preserving dynamics; no winning, reset-coaccessibility, or raw-membership
label enters the exposure calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Sequence

from analyze_n6_low_rank_obstruction_peeling import _digest
from analyze_n6_rank4_structural_descent import _signature
from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, pushforward_mass
from single_defect_low_rank_base import build_low_rank_base
from single_defect_transport import kernel_blocks, single_defect_alphabet_certificate


ROOT = Path(__file__).resolve().parents[2]
Mass = tuple[int, ...]
Letters = tuple[tuple[int, ...], ...]
TokenState = tuple[int, ...]


def _source_letters(source: dict[str, Any]) -> dict[int, Letters]:
    rows: dict[int, Letters] = {}
    for sample in source["type_ii_samples"]:
        if len(sample["profile"]["source_partition"]) != 4:
            continue
        index = int(sample["index"])
        letters = tuple(
            tuple(int(value) for value in row) for row in sample["letters"]
        )
        rows[index] = letters
    if len(rows) != 24:
        raise AssertionError("matched rank-four audit requires 24 automata")
    return rows


def _cycle_gaps(support: Sequence[int], n: int) -> list[int]:
    ordered = sorted(int(value) for value in support)
    gaps = [
        (ordered[(index + 1) % len(ordered)] - ordered[index]) % n
        for index in range(len(ordered))
    ]
    rotations = [tuple(gaps[index:] + gaps[:index]) for index in range(len(gaps))]
    return list(min(rotations))


def _geometry(mass: Mass, collision: tuple[int, int]) -> dict[str, Any]:
    n = len(mass)
    support = [index for index, value in enumerate(mass) if value]
    heavy = [index for index, value in enumerate(mass) if value == 3]
    heavy_index = heavy[0] if len(heavy) == 1 else None
    return {
        "support": support,
        "support_cyclic_gap_pattern": _cycle_gaps(support, n),
        "heavy_coordinate": heavy_index,
        "heavy_in_collision_pair": (
            None if heavy_index is None else heavy_index in collision
        ),
        "heavy_clockwise_distances_to_collision": (
            None
            if heavy_index is None
            else [int((site - heavy_index) % n) for site in collision]
        ),
        "heavy_undirected_distances_to_collision": (
            None
            if heavy_index is None
            else [
                min((site - heavy_index) % n, (heavy_index - site) % n)
                for site in collision
            ]
        ),
    }


def _token_bfs(
    source: Mass,
    letters: Letters,
    allowed_indices: tuple[int, ...],
) -> tuple[
    tuple[int, ...],
    dict[TokenState, int],
    dict[TokenState, tuple[TokenState, int]],
]:
    token_sources = tuple(index for index, value in enumerate(source) if value)
    start = token_sources
    distance = {start: 0}
    parent: dict[TokenState, tuple[TokenState, int]] = {}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for letter_index in allowed_indices:
            letter = letters[letter_index]
            target = tuple(letter[index] for index in current)
            if len(set(target)) != len(target):
                continue
            if target not in distance:
                distance[target] = distance[current] + 1
                parent[target] = (current, letter_index)
                queue.append(target)
    return token_sources, distance, parent


def _token_bfs_by_defect_use(
    source: Mass,
    letters: Letters,
    defect_index: int,
) -> tuple[
    tuple[int, ...],
    dict[tuple[TokenState, bool], int],
    dict[tuple[TokenState, bool], tuple[tuple[TokenState, bool], int]],
]:
    """Resolve shortest rank-preserving token paths by whether they use ``d``."""
    token_sources = tuple(index for index, value in enumerate(source) if value)
    start = (token_sources, False)
    distance = {start: 0}
    parent: dict[
        tuple[TokenState, bool], tuple[tuple[TokenState, bool], int]
    ] = {}
    queue = deque([start])
    while queue:
        current, used_defect = queue.popleft()
        for letter_index, letter in enumerate(letters):
            target = tuple(letter[index] for index in current)
            if len(set(target)) != len(target):
                continue
            key = (target, used_defect or letter_index == defect_index)
            if key not in distance:
                distance[key] = distance[(current, used_defect)] + 1
                parent[key] = ((current, used_defect), letter_index)
                queue.append(key)
    return token_sources, distance, parent


def _word_for(
    target: TokenState,
    parent: dict[TokenState, tuple[TokenState, int]],
) -> list[int]:
    word = []
    current = target
    while current in parent:
        current, letter_index = parent[current]
        word.append(letter_index)
    return list(reversed(word))


def _word_for_mode(
    target: tuple[TokenState, bool],
    parent: dict[
        tuple[TokenState, bool], tuple[tuple[TokenState, bool], int]
    ],
) -> list[int]:
    word = []
    current = target
    while current in parent:
        current, letter_index = parent[current]
        word.append(letter_index)
    return list(reversed(word))


def _pair_exposure_distances(
    token_sources: tuple[int, ...],
    distance: dict[TokenState, int],
    parent: dict[TokenState, tuple[TokenState, int]],
    collision: set[int],
    defect_index: int,
) -> dict[tuple[int, int], dict[str, Any]]:
    rows: dict[tuple[int, int], dict[str, Any]] = {}
    for state, value in distance.items():
        exposed = tuple(
            sorted(
                token_sources[index]
                for index, coordinate in enumerate(state)
                if coordinate in collision
            )
        )
        if len(exposed) != 2:
            continue
        word = _word_for(state, parent)
        candidate = {
            "plateau_prefix_cost": int(value),
            "word": word,
            "uses_rank_preserving_defect": defect_index in word,
            "boundary_token_coordinates": list(state),
        }
        current = rows.get(exposed)
        if current is None or (
            candidate["plateau_prefix_cost"],
            candidate["word"],
            candidate["boundary_token_coordinates"],
        ) < (
            current["plateau_prefix_cost"],
            current["word"],
            current["boundary_token_coordinates"],
        ):
            rows[exposed] = candidate
    return rows


def _defect_assisted_pair_exposure_distances(
    token_sources: tuple[int, ...],
    distance: dict[tuple[TokenState, bool], int],
    parent: dict[
        tuple[TokenState, bool], tuple[tuple[TokenState, bool], int]
    ],
    collision: set[int],
) -> dict[tuple[int, int], dict[str, Any]]:
    rows: dict[tuple[int, int], dict[str, Any]] = {}
    for key, value in distance.items():
        state, used_defect = key
        if not used_defect:
            continue
        exposed = tuple(
            sorted(
                token_sources[index]
                for index, coordinate in enumerate(state)
                if coordinate in collision
            )
        )
        if len(exposed) != 2:
            continue
        candidate = {
            "plateau_prefix_cost": int(value),
            "word": _word_for_mode(key, parent),
            "uses_rank_preserving_defect": True,
            "boundary_token_coordinates": list(state),
        }
        current = rows.get(exposed)
        if current is None or (
            candidate["plateau_prefix_cost"],
            candidate["word"],
            candidate["boundary_token_coordinates"],
        ) < (
            current["plateau_prefix_cost"],
            current["word"],
            current["boundary_token_coordinates"],
        ):
            rows[exposed] = candidate
    return rows


def _endpoint_normalized_pair_candidates(
    source: Mass,
    letters: Letters,
    token_sources: tuple[int, ...],
    distance: dict[TokenState, int],
    parent: dict[TokenState, tuple[TokenState, int]],
    collision: set[int],
    defect_index: int,
    p2: set[Mass],
    p3: set[Mass],
) -> dict[tuple[int, int], list[dict[str, Any]]]:
    """Keep every labelled-pair representative that is shortest for its endpoint."""
    defect = letters[defect_index]
    raw: list[dict[str, Any]] = []
    endpoint_distance: dict[Mass, int] = {}
    for state, prefix_cost in distance.items():
        exposed_indices = [
            index for index, coordinate in enumerate(state) if coordinate in collision
        ]
        if len(exposed_indices) != 2:
            continue
        pair = tuple(sorted(token_sources[index] for index in exposed_indices))
        boundary_mass = [0] * len(source)
        for source_index, coordinate in zip(token_sources, state):
            boundary_mass[coordinate] += int(source[source_index])
        target = pushforward_mass(tuple(boundary_mass), defect)
        if mass_rank(target) != 3:
            raise AssertionError("binary collision exposure must produce rank three")
        corridor_length = int(prefix_cost) + 1
        endpoint_distance[target] = min(
            corridor_length, endpoint_distance.get(target, corridor_length)
        )
        raw.append({
            "pair": pair,
            "target": target,
            "plateau_prefix_cost": int(prefix_cost),
            "corridor_length": corridor_length,
            "word": _word_for(state, parent) + [defect_index],
        })

    declared = {
        tuple(int(value) for value in row["target"]): int(row["length"])
        for row in endpoint_shortest_exits(source, letters, len(source))
        if int(row["target_rank"]) == 3
    }
    if declared != endpoint_distance:
        raise AssertionError("token and mass endpoint-normalization distances disagree")

    exit_cache: dict[Mass, list[dict[str, Any]]] = {}
    rows: dict[tuple[int, int], list[dict[str, Any]]] = {}
    seen: set[tuple[tuple[int, int], Mass, tuple[int, ...]]] = set()
    for item in raw:
        target = item["target"]
        if item["corridor_length"] != endpoint_distance[target]:
            continue
        key = (item["pair"], target, tuple(item["word"]))
        if key in seen:
            continue
        seen.add(key)
        reward = 2 * int(source[item["pair"][0]]) * int(source[item["pair"][1]])
        surplus = reward - int(item["corridor_length"])
        repayment = _repayment_capacity(target, letters, p2, exit_cache)
        rows.setdefault(item["pair"], []).append({
            "target": list(target),
            "plateau_prefix_cost": item["plateau_prefix_cost"],
            "corridor_length": item["corridor_length"],
            "first_surplus": surplus,
            "target_in_P3": target in p3,
            "maximum_repayment_to_P2": repayment,
            "type_i_descent": surplus >= 0 and target in p3,
            "type_ii_descent": (
                surplus < 0 and repayment is not None and repayment >= -surplus
            ),
            "word": item["word"],
        })
    for pair in rows:
        rows[pair].sort(
            key=lambda item: (
                item["corridor_length"],
                -item["first_surplus"],
                item["target"],
                item["word"],
            )
        )
    return rows


def _repayment_capacity(
    rank_three: Mass,
    letters: Letters,
    p2: set[Mass],
    exit_cache: dict[Mass, list[dict[str, Any]]],
) -> int | None:
    if rank_three not in exit_cache:
        exit_cache[rank_three] = endpoint_shortest_exits(
            rank_three, letters, len(rank_three)
        )
    values = [
        int(row["surplus"])
        for row in exit_cache[rank_three]
        if int(row["target_rank"]) == 2
        and tuple(int(value) for value in row["target"]) in p2
    ]
    return max(values, default=None)


def _exposure_table(
    source: Mass,
    letters: Letters,
    defect_index: int,
    p2: set[Mass],
    p3: set[Mass],
) -> dict[str, Any]:
    n = len(source)
    defect = letters[defect_index]
    collision_blocks = [block for block in kernel_blocks(defect, n) if len(block) == 2]
    if len(collision_blocks) != 1:
        raise AssertionError("single-defect exposure requires one binary block")
    collision_tuple = tuple(int(value) for value in collision_blocks[0])
    collision = set(collision_tuple)
    all_indices = tuple(range(len(letters)))
    permutation_indices = tuple(
        index for index in all_indices if index != defect_index
    )
    token_sources, full_distance, full_parent = _token_bfs(
        source, letters, all_indices
    )
    _, perm_distance, perm_parent = _token_bfs(
        source, letters, permutation_indices
    )
    _, mode_distance, mode_parent = _token_bfs_by_defect_use(
        source, letters, defect_index
    )
    full_exposure = _pair_exposure_distances(
        token_sources, full_distance, full_parent, collision, defect_index
    )
    perm_exposure = _pair_exposure_distances(
        token_sources, perm_distance, perm_parent, collision, defect_index
    )
    defect_assisted_exposure = _defect_assisted_pair_exposure_distances(
        token_sources, mode_distance, mode_parent, collision
    )
    pair_candidates = _endpoint_normalized_pair_candidates(
        source,
        letters,
        token_sources,
        full_distance,
        full_parent,
        collision,
        defect_index,
        p2,
        p3,
    )

    rows = []
    for left in range(len(token_sources)):
        for right in range(left + 1, len(token_sources)):
            pair = tuple(sorted((token_sources[left], token_sources[right])))
            masses = [int(source[index]) for index in pair]
            reward = 2 * masses[0] * masses[1]
            full = full_exposure.get(pair)
            perm = perm_exposure.get(pair)
            assisted = defect_assisted_exposure.get(pair)
            if full is None:
                raise AssertionError("full plateau cannot expose a packet pair")
            expected_margin = reward - (int(full["plateau_prefix_cost"]) + 1)
            candidates = pair_candidates.get(pair, [])
            rows.append({
                "packet_source_coordinates": list(pair),
                "packet_masses": masses,
                "reward_2uv": reward,
                "full_plateau_exposure": full,
                "permutation_only_exposure": perm,
                "defect_assisted_exposure": assisted,
                "defect_needed_for_minimum_exposure": (
                    perm is None
                    or int(full["plateau_prefix_cost"])
                    < int(perm["plateau_prefix_cost"])
                ),
                "steering_gain": (
                    None
                    if perm is None
                    else int(perm["plateau_prefix_cost"])
                    - int(full["plateau_prefix_cost"])
                ),
                "first_fusion_margin_at_minimum_exposure": expected_margin,
                "minimum_exposure_is_endpoint_normalized": any(
                    int(item["plateau_prefix_cost"])
                    == int(full["plateau_prefix_cost"])
                    for item in candidates
                ),
                "endpoint_candidate_count": len(candidates),
                "has_type_i_descent": any(
                    item["type_i_descent"] for item in candidates
                ),
                "has_type_ii_descent": any(
                    item["type_ii_descent"] for item in candidates
                ),
                "endpoint_candidates": candidates,
            })
    return {
        "collision_pair": list(collision_tuple),
        "geometry": _geometry(source, collision_tuple),
        "pair_exposures": rows,
        "has_local_descent_from_exposure": any(
            row["has_type_i_descent"] or row["has_type_ii_descent"]
            for row in rows
        ),
    }


def _sccs(rank_four: set[Mass], letters: Letters) -> dict[Mass, dict[str, Any]]:
    adjacency: dict[Mass, list[Mass]] = {mass: [] for mass in rank_four}
    for source in rank_four:
        for letter in letters:
            target = pushforward_mass(source, letter)
            if mass_rank(target) == 4:
                adjacency[source].append(target)
    index = 0
    indices: dict[Mass, int] = {}
    low: dict[Mass, int] = {}
    stack: list[Mass] = []
    on_stack: set[Mass] = set()
    components: list[list[Mass]] = []

    def visit(node: Mass) -> None:
        nonlocal index
        indices[node] = index
        low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in adjacency[node]:
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component = []
            while True:
                current = stack.pop()
                on_stack.remove(current)
                component.append(current)
                if current == node:
                    break
            components.append(sorted(component))

    for mass in sorted(rank_four):
        if mass not in indices:
            visit(mass)
    result = {}
    for component in components:
        identifier = hashlib.sha256(
            json.dumps(component, separators=(",", ":")).encode()
        ).hexdigest()[:16]
        for mass in component:
            result[mass] = {
                "scc_id": identifier,
                "scc_size": len(component),
                "scc_minimum_mass": list(component[0]),
            }
    return result


def _class_id(signature: str) -> str:
    return hashlib.sha256(signature.encode()).hexdigest()[:16]


def _grouped_exposure_signature(
    record: dict[str, Any], field: str
) -> tuple[tuple[tuple[int, int], tuple[int, ...]], ...]:
    grouped: dict[tuple[int, int], list[int]] = {}
    for row in record["exposure"]["pair_exposures"]:
        masses = tuple(sorted(int(value) for value in row["packet_masses"]))
        value = row[field]
        cost = 99 if value is None else int(value["plateau_prefix_cost"])
        grouped.setdefault(masses, []).append(cost)
    return tuple(
        (masses, tuple(sorted(costs)))
        for masses, costs in sorted(grouped.items())
    )


def _flatten_grouped_costs(
    signature: tuple[tuple[tuple[int, int], tuple[int, ...]], ...]
) -> tuple[int, ...]:
    return tuple(cost for _, costs in signature for cost in costs)


def _matching_key(
    failure: dict[str, Any], candidate: dict[str, Any]
) -> tuple[Any, ...]:
    """Order controls by pre-fusion geometry without reading descent labels."""
    failure_geometry = failure["exposure"]["geometry"]
    candidate_geometry = candidate["exposure"]["geometry"]
    failure_signatures = tuple(
        _grouped_exposure_signature(failure, field)
        for field in (
            "full_plateau_exposure",
            "permutation_only_exposure",
            "defect_assisted_exposure",
        )
    )
    candidate_signatures = tuple(
        _grouped_exposure_signature(candidate, field)
        for field in (
            "full_plateau_exposure",
            "permutation_only_exposure",
            "defect_assisted_exposure",
        )
    )
    exposure_distance = tuple(
        sum(
            abs(left - right)
            for left, right in zip(
                _flatten_grouped_costs(failure_signature),
                _flatten_grouped_costs(candidate_signature),
            )
        )
        for failure_signature, candidate_signature in zip(
            failure_signatures, candidate_signatures
        )
    )
    return (
        failure_geometry["support_cyclic_gap_pattern"]
        != candidate_geometry["support_cyclic_gap_pattern"],
        failure_geometry["heavy_undirected_distances_to_collision"]
        != candidate_geometry["heavy_undirected_distances_to_collision"],
        exposure_distance,
        candidate["mass"],
        candidate["automaton_index"],
    )


def _best_descent_margin(record: dict[str, Any]) -> int | None:
    margins = []
    for pair in record["exposure"]["pair_exposures"]:
        for candidate in pair["endpoint_candidates"]:
            surplus = int(candidate["first_surplus"])
            repayment = candidate["maximum_repayment_to_P2"]
            if surplus >= 0 and candidate["target_in_P3"]:
                margins.append(surplus)
            elif surplus < 0 and repayment is not None:
                margins.append(surplus + int(repayment))
    return max(margins, default=None)


def _exposure_signature_rows(
    counts: Counter[tuple[tuple[tuple[int, int], tuple[int, ...]], ...]]
) -> list[dict[str, Any]]:
    return [
        {
            "groups": [
                {
                    "packet_masses": list(masses),
                    "plateau_prefix_costs": list(costs),
                }
                for masses, costs in signature
            ],
            "count": count,
        }
        for signature, count in sorted(counts.items())
    ]


def analyze(rank_four_result: Path) -> dict[str, Any]:
    rank_four = json.loads(rank_four_result.read_text(encoding="utf-8", newline="\n"))
    if rank_four.get("schema") != "single-defect-n6-rank4-structural-descent-audit-v1":
        raise AssertionError("unexpected rank-four source schema")
    hostile_path = ROOT / rank_four["source_result"]
    hostile = json.loads(hostile_path.read_text(encoding="utf-8", newline="\n"))
    letters_by_index = _source_letters(hostile)
    mixed_signatures = {
        _signature(row["partition"], row["occupancy"]): row
        for row in rank_four["occupancy_signature_rows"]
        if row["classification"] == "MIXED"
    }
    if len(mixed_signatures) != 3:
        raise AssertionError("matched audit requires exactly three mixed classes")

    records_by_class: dict[str, list[dict[str, Any]]] = {
        signature: [] for signature in mixed_signatures
    }
    automaton_data = {}
    for automaton in rank_four["automaton_rows"]:
        automaton_index = int(automaton["automaton_index"])
        letters = letters_by_index[automaton_index]
        n = len(letters[0])
        certificate = single_defect_alphabet_certificate(letters, n)
        defect_index = int(certificate["defect_index"])
        base = build_low_rank_base(letters, n)
        p2 = {
            tuple(int(value) for value in row["mass"])
            for row in base["rows"]
            if int(row["rank"]) == 2 and row["in_low_rank_base"]
        }
        p3 = {
            tuple(int(value) for value in row["mass"])
            for row in base["rows"]
            if int(row["rank"]) == 3 and row["in_low_rank_base"]
        }
        states = {
            tuple(int(value) for value in row["mass"]): row
            for row in automaton["rank_four_states"]
        }
        scc = _sccs(set(states), letters)
        automaton_data[automaton_index] = {
            "letters": letters,
            "defect_index": defect_index,
            "states": states,
            "scc": scc,
        }
        for mass, row in states.items():
            signature = _signature(row["partition"], row["kernel_occupancy"])
            if signature not in mixed_signatures:
                continue
            exposure = _exposure_table(mass, letters, defect_index, p2, p3)
            if exposure["has_local_descent_from_exposure"] != bool(
                row["has_local_descent_to_P_le_3"]
            ):
                raise AssertionError("exposure table/local-descent parity failed")
            records_by_class[signature].append({
                "automaton_index": automaton_index,
                "mass": list(mass),
                "in_raw_macro_closure": bool(row["in_raw_macro_closure"]),
                "has_local_descent": bool(row["has_local_descent_to_P_le_3"]),
                "exposure": exposure,
                "plateau_scc": scc[mass],
            })

    class_rows = []
    matched_rows = []
    diagnostics = Counter()
    for signature, records in sorted(records_by_class.items()):
        failures = [row for row in records if not row["has_local_descent"]]
        raw_successes = [
            row for row in records
            if row["has_local_descent"] and row["in_raw_macro_closure"]
        ]
        all_successes = [row for row in records if row["has_local_descent"]]
        class_identifier = _class_id(signature)
        for failure in failures:
            same_automaton_raw = [
                row for row in raw_successes
                if row["automaton_index"] == failure["automaton_index"]
            ]
            same_automaton_success = [
                row for row in all_successes
                if row["automaton_index"] == failure["automaton_index"]
            ]
            if same_automaton_raw:
                pool = same_automaton_raw
                match_kind = "SAME_AUTOMATON_RAW_SUCCESS"
            elif same_automaton_success:
                pool = same_automaton_success
                match_kind = "SAME_AUTOMATON_SEMIGROUP_SUCCESS"
            elif raw_successes:
                pool = raw_successes
                match_kind = "CROSS_AUTOMATON_RAW_SUCCESS"
            else:
                pool = all_successes
                match_kind = "CROSS_AUTOMATON_SEMIGROUP_SUCCESS"
            success = min(
                pool,
                key=lambda row: _matching_key(failure, row),
            )
            nearest_pool = same_automaton_success or all_successes
            nearest_success = min(
                nearest_pool,
                key=lambda row: _matching_key(failure, row),
            )
            same_scc = (
                success["automaton_index"] == failure["automaton_index"]
                and success["plateau_scc"]["scc_id"]
                == failure["plateau_scc"]["scc_id"]
            )
            diagnostics[f"match:{match_kind}"] += 1
            diagnostics[f"same_scc:{same_scc}"] += 1
            failure_geometry = failure["exposure"]["geometry"]
            success_geometry = success["exposure"]["geometry"]
            diagnostics[
                "matched_gap_equal:"
                + str(
                    failure_geometry["support_cyclic_gap_pattern"]
                    == success_geometry["support_cyclic_gap_pattern"]
                )
            ] += 1
            diagnostics[
                "matched_heavy_distance_equal:"
                + str(
                    failure_geometry["heavy_undirected_distances_to_collision"]
                    == success_geometry["heavy_undirected_distances_to_collision"]
                )
            ] += 1
            nearest_failure_geometry = failure["exposure"]["geometry"]
            nearest_success_geometry = nearest_success["exposure"]["geometry"]
            diagnostics[
                "nearest_gap_equal:"
                + str(
                    nearest_failure_geometry["support_cyclic_gap_pattern"]
                    == nearest_success_geometry["support_cyclic_gap_pattern"]
                )
            ] += 1
            diagnostics[
                "nearest_heavy_distance_equal:"
                + str(
                    nearest_failure_geometry["heavy_undirected_distances_to_collision"]
                    == nearest_success_geometry["heavy_undirected_distances_to_collision"]
                )
            ] += 1
            matched_rows.append({
                "class_id": class_identifier,
                "match_kind": match_kind,
                "same_plateau_scc": same_scc,
                "failure_best_descent_margin": _best_descent_margin(failure),
                "success_best_descent_margin": _best_descent_margin(success),
                "nearest_geometry_success_ref": {
                    "automaton_index": nearest_success["automaton_index"],
                    "mass": nearest_success["mass"],
                    "in_raw_macro_closure": nearest_success["in_raw_macro_closure"],
                    "best_descent_margin": _best_descent_margin(nearest_success),
                },
                "success": success,
                "failure": failure,
            })
        failure_margins = Counter(
            str(_best_descent_margin(row)) for row in failures
        )
        success_margins = Counter(
            str(_best_descent_margin(row)) for row in all_successes
        )
        failure_gaps = Counter(
            str(tuple(row["exposure"]["geometry"]["support_cyclic_gap_pattern"]))
            for row in failures
        )
        success_gaps = Counter(
            str(tuple(row["exposure"]["geometry"]["support_cyclic_gap_pattern"]))
            for row in all_successes
        )
        failure_exposure_signatures = Counter(
            _grouped_exposure_signature(row, "full_plateau_exposure")
            for row in failures
        )
        success_exposure_signatures = Counter(
            _grouped_exposure_signature(row, "full_plateau_exposure")
            for row in all_successes
        )
        exposure_signature_overlap = (
            failure_exposure_signatures.keys() & success_exposure_signatures.keys()
        )
        class_rows.append({
            "class_id": class_identifier,
            "partition": mixed_signatures[signature]["partition"],
            "canonical_occupancy": mixed_signatures[signature]["occupancy"],
            "occurrences": len(records),
            "raw_successes": len(raw_successes),
            "all_successes": len(all_successes),
            "failures": len(failures),
            "failure_gap_patterns": dict(sorted(failure_gaps.items())),
            "success_gap_patterns": dict(sorted(success_gaps.items())),
            "failure_best_descent_margins": dict(sorted(failure_margins.items())),
            "success_best_descent_margins": dict(sorted(success_margins.items())),
            "failure_full_exposure_signatures": _exposure_signature_rows(
                failure_exposure_signatures
            ),
            "full_exposure_signature_counts": {
                "failure_unique": len(failure_exposure_signatures),
                "success_unique": len(success_exposure_signatures),
                "shared_unique": len(exposure_signature_overlap),
            },
            "records": records,
        })

    return {
        "schema": "single-defect-n6-rank4-matched-exposure-audit-v1",
        "rank_four_result": str(rank_four_result.relative_to(ROOT).as_posix()),
        "rank_four_result_sha256": hashlib.sha256(
            rank_four_result.read_bytes()
        ).hexdigest(),
        "hostile_result": rank_four["source_result"],
        "hostile_result_sha256": rank_four["source_result_sha256"],
        "scope": {
            "n": 6,
            "mixed_signature_classes": len(class_rows),
            "matched_failure_placements": len(matched_rows),
            "matching_priority": [
                "same automaton raw success",
                "same automaton semigroup success",
                "cross automaton raw success",
                "cross automaton semigroup success",
            ],
        },
        "conventions": {
            "plateau_prefix_cost": "h counts rank-preserving letters before final d",
            "corridor_length": "ell=h+1 includes the final strict d",
            "rank_four_unit_surplus": "S=2uv-ell for n=6 and r=4",
            "steering_gain": "L_perm-L_full when permutation exposure exists",
        },
        "diagnostic_counts": dict(sorted(diagnostics.items())),
        "class_rows": class_rows,
        "matched_rows": matched_rows,
        "claim_boundary": [
            "The audit fixes partition and canonical occupancy before comparing placements.",
            "Exposure distances are exact local labelled-action diagnostics, not a new global potential.",
            "Raw membership is used only to choose hostile controls and is not proposed as Q4.",
            "A matched finite separator does not by itself prove Entry inheritance or an all-n rank-four Escape lemma.",
            "The transport-exposure signature is a finite n=6 candidate separator, not a proved Q4 predicate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rank_four_result", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(args.rank_four_result.resolve())
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("analyze_n6_rank4_structural_descent.py"),
        producer.with_name("single_defect_low_rank_base.py"),
        producer.with_name("costed_endpoint_diagnostic.py"),
        producer.with_name("mass_maturity_legacy.py"),
        producer.with_name("single_defect_transport.py"),
    )
    payload["sources"] = {
        str(path.relative_to(ROOT).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in dependencies
    }
    payload["content_sha256"] = _digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "scope": payload["scope"],
        "diagnostic_counts": payload["diagnostic_counts"],
        "classes": [
            {
                "class_id": row["class_id"],
                "raw_successes": row["raw_successes"],
                "all_successes": row["all_successes"],
                "failures": row["failures"],
            }
            for row in payload["class_rows"]
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
