#!/usr/bin/env python3
"""Audit credit reallocation and rooted colored obstructions at theta_*.

This producer reads the frozen 35-context extremal channel relation.  It does
not rerun the completion evaluator.  The functional-graph projection forgets
the identities of the two non-fresh mass-two packets, while retaining cyclic
coordinates relative to the collision root when the rooted projection is used.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from mass_maturity_legacy import simplified_deadline
from section_return_core import digest_payload

ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_COLORED_OBSTRUCTION_V1"

COLOR_MASS_TWO = "M2"
COLOR_SINGLETON = "S"
COLOR_EMPTY = "E"

BRIDGE_OBSTRUCTION = "ROOTED_MASS2_EMPTY_2_CYCLE"
FALLBACK_OBSTRUCTION = "ROOTED_SINGLETON_EMPTY_2_CYCLE"
CHANNEL_C4 = "C4_TYPE_II_22_TO_24_F4_BOTH"

Packet = frozenset[int]
PacketState = dict[int, Packet]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _color(mass: int) -> str:
    if mass == 2:
        return COLOR_MASS_TWO
    if mass == 1:
        return COLOR_SINGLETON
    if mass == 0:
        return COLOR_EMPTY
    raise AssertionError(f"unexpected non-kernel mass in extremal carrier: {mass}")


def _least_rotation(values: tuple[str, ...]) -> tuple[str, ...]:
    return min(values[index:] + values[:index] for index in range(len(values)))


def _cycles(defect: tuple[int, ...]) -> list[tuple[int, ...]]:
    non_kernel = set(range(1, 6))
    if {defect[index] for index in non_kernel} != non_kernel:
        raise AssertionError("non-kernel restriction is not a permutation")
    unseen = set(non_kernel)
    cycles: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        cycle: list[int] = []
        current = start
        while current not in cycle:
            if current not in unseen:
                raise AssertionError("functional graph cycles overlap")
            cycle.append(current)
            unseen.remove(current)
            current = defect[current]
        if current != start:
            raise AssertionError("non-kernel orbit did not close at its root")
        cycles.append(tuple(cycle))
    return cycles


def _unrooted_colored_signature(
    defect: tuple[int, ...], source: tuple[int, ...]
) -> tuple[tuple[str, ...], ...]:
    colored = []
    for cycle in _cycles(defect):
        colors = tuple(_color(source[index]) for index in cycle)
        colored.append(_least_rotation(colors))
    return tuple(sorted(colored))


def _rooted_rows(
    defect: tuple[int, ...], source: tuple[int, ...]
) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": coordinate,
            "color": _color(source[coordinate]),
            "defect_image": defect[coordinate],
        }
        for coordinate in range(1, 6)
    ]


def _rooted_two_cycles(
    defect: tuple[int, ...], source: tuple[int, ...]
) -> list[dict[str, Any]]:
    result = []
    for left in range(1, 6):
        right = defect[left]
        if left < right and defect[right] == left:
            result.append(
                {
                    "coordinates": [left, right],
                    "colors": [_color(source[left]), _color(source[right])],
                }
            )
    return result


def _obstruction_type(two_cycles: list[dict[str, Any]]) -> str | None:
    patterns = {
        (tuple(row["coordinates"]), tuple(row["colors"])) for row in two_cycles
    }
    if ((3, 4), (COLOR_MASS_TWO, COLOR_EMPTY)) in patterns:
        return BRIDGE_OBSTRUCTION
    if ((3, 5), (COLOR_SINGLETON, COLOR_EMPTY)) in patterns:
        return FALLBACK_OBSTRUCTION
    return None


def _push_packets(
    packets: PacketState, transformation: tuple[int, ...]
) -> PacketState:
    target: dict[int, set[int]] = {}
    for coordinate, packet in packets.items():
        target.setdefault(transformation[coordinate], set()).update(packet)
    return {
        coordinate: frozenset(packet) for coordinate, packet in target.items()
    }


def _theta_packet_recursion(defect: tuple[int, ...]) -> dict[str, Any]:
    cycle = tuple((coordinate + 1) % 7 for coordinate in range(7))
    p2 = tuple(cycle[cycle[coordinate]] for coordinate in range(7))
    initial: PacketState = {
        0: frozenset({0, 6}),
        **{coordinate: frozenset({coordinate}) for coordinate in range(1, 6)},
    }

    pre_rank5 = _push_packets(initial, p2)
    rank5_parents = (pre_rank5.get(0), pre_rank5.get(6))
    rank5 = _push_packets(pre_rank5, defect)
    inherited_fresh = (
        rank5_parents[0] | rank5_parents[1]
        if all(rank5_parents)
        else frozenset()
    )

    pre_rank4 = _push_packets(rank5, p2)
    rank4_parents = (pre_rank4.get(0), pre_rank4.get(6))
    rank4 = _push_packets(pre_rank4, defect)
    fresh_rank4 = (
        rank4_parents[0] | rank4_parents[1]
        if all(rank4_parents)
        else frozenset()
    )
    source_mass = [0] * 7
    for coordinate, packet in rank4.items():
        source_mass[coordinate] = len(packet)

    packet_condition = (
        len(rank5) == 5
        and sorted((len(packet) for packet in rank5.values()), reverse=True)
        == [2, 2, 1, 1, 1]
        and len(rank4) == 4
        and sorted((len(packet) for packet in rank4.values()), reverse=True)
        == [2, 2, 2, 1]
        and all(rank4_parents)
        and sorted(len(packet) for packet in rank4_parents) == [1, 1]
        and inherited_fresh not in rank4_parents
        and rank4.get(0) == fresh_rank4
    )
    permutation_condition = {4, 5} <= {defect[index] for index in (3, 4, 5)}
    if packet_condition != permutation_condition:
        raise AssertionError("theta packet recursion and permutation condition differ")
    return {
        "in_theta_recursion": packet_condition,
        "source_mass": source_mass,
        "rank5_fresh_packet": sorted(inherited_fresh),
        "rank4_fresh_packet": sorted(fresh_rank4),
    }


def _cycle_type(defect: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted((len(cycle) for cycle in _cycles(defect)), reverse=True))


def _carrier_coordinates(defect: tuple[int, ...]) -> dict[str, Any]:
    low = {1, 2, 3}
    high_domain = {3, 4, 5}
    returning = [coordinate for coordinate in high_domain if defect[coordinate] in low]
    if len(returning) != 1:
        raise AssertionError("carrier action has no unique returning high slot")
    h = returning[0]
    alpha = (defect[1], defect[2], defect[h])
    if set(alpha) != low:
        raise AssertionError("alpha is not a permutation of the low block")
    if alpha == (1, 2, 3):
        alpha_type = "IDENTITY"
    elif sum(value != index for index, value in enumerate(alpha, start=1)) == 2:
        alpha_type = "TRANSPOSITION"
    else:
        alpha_type = "THREE_CYCLE"
    remaining = sorted(high_domain - {h})
    beta_images = (defect[remaining[0]], defect[remaining[1]])
    if beta_images == (4, 5):
        beta = "IDENTITY"
    elif beta_images == (5, 4):
        beta = "SWAP"
    else:
        raise AssertionError("beta is not a permutation of the high block")

    reconstructed = [0] * 7
    reconstructed[0] = 0
    reconstructed[6] = 0
    reconstructed[1], reconstructed[2], reconstructed[h] = alpha
    reconstructed[remaining[0]], reconstructed[remaining[1]] = beta_images
    if tuple(reconstructed) != defect:
        raise AssertionError("(h,alpha,beta) did not reconstruct the defect")
    return {
        "h": h,
        "alpha": list(alpha),
        "alpha_cycle_type": alpha_type,
        "beta": beta,
    }


def _offset_one_accounting_templates(context: dict[str, Any]) -> set[tuple[Any, ...]]:
    templates = set()
    for representative in context["channel_relations"][CHANNEL_C4]:
        singleton = next(
            row for row in representative["target_packets"] if row["mass"] == 1
        )
        if singleton["coordinate"] != 1:
            continue
        other_role = next(
            role for role in representative["first_fusion_roles"] if role != "F4"
        )
        edge = representative["edge"]
        templates.add(
            (
                edge["length_first"],
                edge["length_second"],
                other_role.split("@")[0],
            )
        )
    return templates


def _minimum_template_cover(
    relations: list[set[tuple[Any, ...]]],
) -> tuple[tuple[Any, ...], ...]:
    universe = sorted(set().union(*relations))
    for size in range(1, len(relations) + 1):
        for candidate in itertools.combinations(universe, size):
            if all(any(template in relation for template in candidate) for relation in relations):
                return candidate
    raise AssertionError("offset-one accounting relation has no finite cover")


def _best_offset_one_witness(context: dict[str, Any]) -> dict[str, Any] | None:
    candidates = []
    for representative in context["channel_relations"][CHANNEL_C4]:
        singleton = next(
            row for row in representative["target_packets"] if row["mass"] == 1
        )
        if singleton["coordinate"] == 1:
            candidates.append(representative)
    if not candidates:
        return None
    selected = min(
        candidates,
        key=lambda row: (
            row["edge"]["total_length"],
            row["edge"]["first_word"],
            row["edge"]["second_word"],
            row["first_fusion_roles"],
        ),
    )
    edge = selected["edge"]
    return {
        "first_fusion_roles": selected["first_fusion_roles"],
        "first_word": edge["first_word"],
        "second_word": edge["second_word"],
        "surplus_first": edge["surplus_first"],
        "surplus_second": edge["surplus_second"],
        "total_length": edge["total_length"],
        "total_surplus": edge["total_surplus"],
    }


def _section_reconstruction(
    channel_payload: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    candidates = []
    for permutation in itertools.permutations(range(1, 6)):
        defect = (0, *permutation, 0)
        recursion = _theta_packet_recursion(defect)
        if recursion["in_theta_recursion"]:
            coordinates = _carrier_coordinates(defect)
            candidates.append(
                {
                    "defect": "".join(str(value) for value in defect),
                    "source_mass": recursion["source_mass"],
                    **coordinates,
                }
            )
    if len(candidates) != 36:
        raise AssertionError("theta packet recursion no longer gives 36 actions")

    predecessor = "0123450"
    selected_candidates = {
        row["defect"]: row for row in candidates if row["defect"] != predecessor
    }
    context_by_defect = {row["defect"]: row for row in rows}
    candidate_by_defect = {row["defect"]: row for row in candidates}
    if set(selected_candidates) != set(context_by_defect):
        raise AssertionError("packet-recursion section image does not match carrier")
    for defect, candidate in selected_candidates.items():
        if candidate["source_mass"] != context_by_defect[defect]["source_mass"]:
            raise AssertionError("packet-recursion source mass drift")

    alpha_counts = defaultdict(
        lambda: {"actions": 0, "selected_contexts": 0, "offset_1_present": 0}
    )
    for candidate in candidates:
        alpha_type = candidate["alpha_cycle_type"]
        alpha_counts[alpha_type]["actions"] += 1
        context = context_by_defect.get(candidate["defect"])
        if context is None:
            continue
        alpha_counts[alpha_type]["selected_contexts"] += 1
        alpha_counts[alpha_type]["offset_1_present"] += int(
            context["offset_1_in_R4"]
        )

    cycle_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"contexts": 0, "offset_1_present": 0, "offset_1_absent": 0}
    )
    single_transpositions = []
    low_transport_groups: dict[tuple[int, str, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for context in channel_payload["contexts"]:
        defect = tuple(int(value) for value in context["defect"])
        coordinates = candidate_by_defect[context["defect"]]
        if coordinates["alpha_cycle_type"] != "IDENTITY":
            low_transport_groups[
                (
                    coordinates["h"],
                    coordinates["alpha_cycle_type"],
                    coordinates["beta"],
                )
            ].append(context)
        cycle_type = _cycle_type(defect)
        key = "+".join(str(value) for value in cycle_type)
        has_offset_one = 1 in context["heavy_comb_safe_set"][
            "C4_landing_offsets"
        ]
        cycle_counts[key]["contexts"] += 1
        cycle_counts[key][
            "offset_1_present" if has_offset_one else "offset_1_absent"
        ] += 1
        if cycle_type != (2, 1, 1, 1):
            continue
        row = context_by_defect[context["defect"]]
        obstruction = row["rooted_obstruction_type"]
        if has_offset_one:
            branch = "OFFSET_1_HEAVY_COMB"
        elif obstruction == BRIDGE_OBSTRUCTION:
            branch = "OFFSET_2_HEAVY_COMB_BRIDGE"
        elif obstruction == FALLBACK_OBSTRUCTION:
            branch = "RANK_TWO_5_2_FALLBACK"
        else:
            raise AssertionError("single-transposition branch is unclassified")
        single_transpositions.append(
            {
                "defect": context["defect"],
                "source_mass": context["source_mass"],
                "rooted_two_cycle": row["rooted_nontrivial_two_cycles"][0],
                "offset_1_in_R4": has_offset_one,
                "completion_branch": branch,
                "offset_1_witness": _best_offset_one_witness(context),
            }
        )

    non_single = [
        context
        for context in channel_payload["contexts"]
        if _cycle_type(tuple(int(value) for value in context["defect"]))
        != (2, 1, 1, 1)
    ]
    if len(non_single) != 29 or not all(
        1 in context["heavy_comb_safe_set"]["C4_landing_offsets"]
        for context in non_single
    ):
        raise AssertionError("29-context generic cycle stratum drift")
    if len(single_transpositions) != 6:
        raise AssertionError("single-transposition stratum drift")

    low_transport_cells = []
    for (h, alpha_type, beta), contexts in sorted(low_transport_groups.items()):
        relations = [_offset_one_accounting_templates(context) for context in contexts]
        if not all(relations):
            raise AssertionError("nontrivial alpha lost its offset-one relation")
        common = set.intersection(*relations)
        cover = _minimum_template_cover(relations)
        low_transport_cells.append(
            {
                "h": h,
                "alpha_cycle_type": alpha_type,
                "beta": beta,
                "contexts": len(contexts),
                "common_accounting_templates": [list(row) for row in sorted(common)],
                "minimum_accounting_cover": [list(row) for row in cover],
                "minimum_accounting_cover_size": len(cover),
            }
        )
    if len(low_transport_cells) != 12:
        raise AssertionError("low-transport coarse projection drift")
    if max(row["minimum_accounting_cover_size"] for row in low_transport_cells) != 3:
        raise AssertionError("low-transport accounting-cover bound drift")

    alpha_identity_rows = []
    for candidate in candidates:
        if candidate["alpha_cycle_type"] != "IDENTITY":
            continue
        context = context_by_defect.get(candidate["defect"])
        if context is None:
            branch = "PREDECESSOR_IDEMPOTENT_SECTION_EXCLUDED"
            offset_one: bool | None = None
        elif context["offset_1_in_R4"]:
            branch = "OFFSET_1_HEAVY_COMB"
            offset_one = True
        elif context["rooted_obstruction_type"] == BRIDGE_OBSTRUCTION:
            branch = "OFFSET_2_HEAVY_COMB_BRIDGE"
            offset_one = False
        elif context["rooted_obstruction_type"] == FALLBACK_OBSTRUCTION:
            branch = "RANK_TWO_5_2_FALLBACK"
            offset_one = False
        else:
            raise AssertionError("identity-alpha section case is unclassified")
        alpha_identity_rows.append(
            {
                "defect": candidate["defect"],
                "h": candidate["h"],
                "beta": candidate["beta"],
                "selected_by_section": context is not None,
                "offset_1_in_R4": offset_one,
                "completion_branch": branch,
            }
        )
    if len(alpha_identity_rows) != 6:
        raise AssertionError("identity-alpha six-case table drift")

    return {
        "rooted_action_universe": "d=(0,pi(1),...,pi(5),0), pi in S_5",
        "section_words": {
            "Sigma_6": "p^2 d",
            "Sigma_5": "p^2 d",
        },
        "theta_recursion_condition": "pi^{-1}({4,5}) subset {3,4,5}",
        "equivalent_image_condition": "{4,5} subset pi({3,4,5})",
        "theta_recursion_actions": len(candidates),
        "predecessor_idempotent_excluded_by_section": predecessor,
        "selected_carrier_actions": len(selected_candidates),
        "source_mass_reconstruction_matches": True,
        "carrier_coordinate_counts": dict(sorted(alpha_counts.items())),
        "low_transport_lemma": {
            "statement": "alpha != identity implies 1 in R4(C_pi)",
            "nontrivial_alpha_contexts": sum(
                len(contexts) for contexts in low_transport_groups.values()
            ),
            "offset_1_successes": sum(
                1
                for contexts in low_transport_groups.values()
                for context in contexts
                if 1
                in context["heavy_comb_safe_set"]["C4_landing_offsets"]
            ),
            "coarse_signature": "(h, cycle_type(alpha), beta)",
            "coarse_cells": len(low_transport_cells),
            "cells_with_common_accounting_template": sum(
                bool(row["common_accounting_templates"])
                for row in low_transport_cells
            ),
            "maximum_minimum_accounting_cover_size": max(
                row["minimum_accounting_cover_size"]
                for row in low_transport_cells
            ),
            "cells": low_transport_cells,
            "proof_boundary": (
                "the implication is exact finite evidence; cycle type alone "
                "does not provide one deterministic accounting template"
            ),
        },
        "identity_alpha_cases": alpha_identity_rows,
        "cycle_type_counts": dict(sorted(cycle_counts.items())),
        "non_single_transposition_stratum": {
            "contexts": len(non_single),
            "all_reach_offset_1": True,
        },
        "single_transposition_stratum": {
            "contexts": len(single_transpositions),
            "offset_1_present": sum(
                row["offset_1_in_R4"] for row in single_transpositions
            ),
            "offset_1_absent": sum(
                not row["offset_1_in_R4"] for row in single_transpositions
            ),
            "rows": single_transpositions,
        },
    }


def _credit_reallocation(payload: dict[str, Any]) -> dict[str, Any]:
    source = (2, 2, 2, 1, 0, 0, 0)
    reset = (7, 0, 0, 0, 0, 0, 0)
    c4_target = (6, 1, 0, 0, 0, 0, 0)
    c2_target = (5, 2, 0, 0, 0, 0, 0)
    tau_source = simplified_deadline(source, 7)
    tau_reset = simplified_deadline(reset, 7)
    tau_c4 = simplified_deadline(c4_target, 7)
    tau_c2 = simplified_deadline(c2_target, 7)

    exception = payload["unique_C4_exception"]
    c4_lengths = sorted(
        {row["edge"]["total_length"] for row in exception["C4_relation"]}
    )
    c2_lengths = sorted(
        {row["edge"]["total_length"] for row in exception["C2_relation"]}
    )
    result = {
        "source_partition": [2, 2, 2, 1],
        "tau_source": tau_source,
        "tau_reset": tau_reset,
        "total_maturity_credit": tau_reset - tau_source,
        "C4_heavy_comb": {
            "rank2_partition": [6, 1],
            "tau_rank2": tau_c4,
            "rank4_to_rank2_credit": tau_c4 - tau_source,
            "rank2_tail_budget": tau_reset - tau_c4,
            "exception_realized_total_lengths": c4_lengths,
        },
        "C2_rank_two_5_2_fallback": {
            "rank2_partition": [5, 2],
            "tau_rank2": tau_c2,
            "rank4_to_rank2_credit": tau_c2 - tau_source,
            "rank2_tail_budget": tau_reset - tau_c2,
            "exception_realized_total_lengths": c2_lengths,
        },
        "reallocated_credit": (tau_c4 - tau_source) - (tau_c2 - tau_source),
        "identity": "20 + B2(6,1) = 12 + B2(5,2) = 27",
    }
    if result != {
        "source_partition": [2, 2, 2, 1],
        "tau_source": 9,
        "tau_reset": 36,
        "total_maturity_credit": 27,
        "C4_heavy_comb": {
            "rank2_partition": [6, 1],
            "tau_rank2": 29,
            "rank4_to_rank2_credit": 20,
            "rank2_tail_budget": 7,
            "exception_realized_total_lengths": [20],
        },
        "C2_rank_two_5_2_fallback": {
            "rank2_partition": [5, 2],
            "tau_rank2": 21,
            "rank4_to_rank2_credit": 12,
            "rank2_tail_budget": 15,
            "exception_realized_total_lengths": [12],
        },
        "reallocated_credit": 8,
        "identity": "20 + B2(6,1) = 12 + B2(5,2) = 27",
    }:
        raise AssertionError("extremal credit-reallocation identity drift")
    return result


def build_payload(channel_path: Path) -> dict[str, Any]:
    channel_payload = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))
    if channel_payload.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected extremal channel input schema")

    rows: list[dict[str, Any]] = []
    coarse_groups: dict[tuple[tuple[str, ...], ...], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for context in channel_payload["contexts"]:
        source = tuple(int(value) for value in context["source_mass"])
        defect = tuple(
            int(value) for value in context["source_geometry"]["defect_map"]
        )
        if source[0] != 2 or defect[0] != 0 or defect[6] != 0:
            raise AssertionError("extremal context lost its rooted carrier geometry")
        coarse = _unrooted_colored_signature(defect, source)
        two_cycles = _rooted_two_cycles(defect, source)
        has_offset_one = 1 in context["heavy_comb_safe_set"][
            "C4_landing_offsets"
        ]
        row = {
            "index": context["index"],
            "defect": context["defect"],
            "source_mass": list(source),
            "C4_landing_offsets": context["heavy_comb_safe_set"][
                "C4_landing_offsets"
            ],
            "offset_1_in_R4": has_offset_one,
            "unrooted_colored_cycle_signature": [list(cycle) for cycle in coarse],
            "rooted_nontrivial_two_cycles": two_cycles,
            "rooted_colored_functional_graph": _rooted_rows(defect, source),
            "rooted_obstruction_type": _obstruction_type(two_cycles),
        }
        rows.append(row)
        coarse_groups[coarse].append(row)

    missing = [row for row in rows if not row["offset_1_in_R4"]]
    rooted_obstructions = [
        row for row in rows if row["rooted_obstruction_type"] is not None
    ]
    rooted_two_cycle_patterns = {
        (tuple(cycle["coordinates"]), tuple(cycle["colors"]))
        for row in rows
        for cycle in row["rooted_nontrivial_two_cycles"]
    }
    if len(missing) != 2 or {
        row["rooted_obstruction_type"] for row in missing
    } != {BRIDGE_OBSTRUCTION, FALLBACK_OBSTRUCTION}:
        raise AssertionError("rooted colored obstruction classification drift")
    if {row["index"] for row in missing} != {
        row["index"] for row in rooted_obstructions
    }:
        raise AssertionError("rooted obstruction is not equivalent to missing offset one")

    mixed = []
    for signature, group in sorted(coarse_groups.items()):
        outcomes = {row["offset_1_in_R4"] for row in group}
        if len(outcomes) == 1:
            continue
        mixed.append(
            {
                "unrooted_colored_cycle_signature": [
                    list(cycle) for cycle in signature
                ],
                "rows": [
                    {
                        "defect": row["defect"],
                        "index": row["index"],
                        "offset_1_in_R4": row["offset_1_in_R4"],
                        "rooted_nontrivial_two_cycles": row[
                            "rooted_nontrivial_two_cycles"
                        ],
                    }
                    for row in group
                ],
            }
        )
    if len(mixed) != 2 or sum(len(group["rows"]) for group in mixed) != 5:
        raise AssertionError("unrooted hostile-control classification drift")

    input_relative = channel_path.resolve().relative_to(ROOT).as_posix()
    bridge = next(
        row for row in missing if row["rooted_obstruction_type"] == BRIDGE_OBSTRUCTION
    )
    fallback = next(
        row
        for row in missing
        if row["rooted_obstruction_type"] == FALLBACK_OBSTRUCTION
    )
    payload = {
        "schema": SCHEMA,
        "n": 7,
        "input": {
            "path": str(input_relative),
            "sha256": _sha256(channel_path),
            "schema": channel_payload["schema"],
            "projection_digest": channel_payload["projection_digest"],
        },
        "scope": {
            "domain": "the frozen 35-context theta_* carrier",
            "evaluation_policy": (
                "classification-only replay of the frozen channel relation; "
                "no completion evaluator is rerun"
            ),
            "packet_quotient": (
                "the two non-fresh mass-two packets are color-equivalent; "
                "rooted cyclic coordinates are retained"
            ),
            "proof_boundary": (
                "the rooted equivalence is a complete fixed-scope theorem; "
                "a non-enumerative derivation from theta_* remains open"
            ),
        },
        "section_reconstruction": _section_reconstruction(channel_payload, rows),
        "credit_reallocation": _credit_reallocation(channel_payload),
        "colored_obstruction_audit": {
            "contexts": len(rows),
            "offset_1_present": sum(row["offset_1_in_R4"] for row in rows),
            "offset_1_absent": len(missing),
            "unrooted_colored_cycle_classes": len(coarse_groups),
            "unrooted_mixed_classes": len(mixed),
            "unrooted_mixed_rows": sum(len(group["rows"]) for group in mixed),
            "unrooted_candidate_T_holds": False,
            "rooted_colored_two_cycle_patterns": len(rooted_two_cycle_patterns),
            "rooted_obstruction_rows": len(rooted_obstructions),
            "rooted_equivalence_holds": True,
            "equivalence": (
                "1 not in R4 iff the rooted colored functional graph has the "
                "(3,4) M2/E 2-cycle or the (3,5) S/E 2-cycle"
            ),
            "mixed_unrooted_hostile_controls": mixed,
        },
        "rooted_obstruction_normal_forms": {
            "mass_two_empty_bridge": bridge,
            "singleton_empty_5_2_fallback": fallback,
        },
        "contexts": rows,
        "claims": [
            "The theta_* carrier is reconstructed by two p^2 d packet returns from exactly 36 rooted local actions; the section excludes the predecessor idempotent and leaves the stored 35 contexts.",
            "All 29 contexts outside the single-transposition cycle stratum reach heavy-comb offset 1; the six single-transposition contexts split as four offset-1 witnesses and two rooted obstructions.",
            "The total maturity credit is 27, allocated as 20+7 by C4 and 12+15 by the (5,2)-fallback C2.",
            "Unrooted colored cycle type does not determine whether heavy-comb offset 1 is reachable.",
            "On the complete theta_* carrier, missing heavy-comb offset 1 is equivalent to exactly two root-addressed colored 2-cycle normal forms.",
            "The mass-two/empty normal form is the offset-2 bridge context; the singleton/empty normal form is the (5,2)-fallback context.",
        ],
        "nonclaims": [
            "The unrooted existence of a mass-two/empty or singleton/empty 2-cycle is not an obstruction theorem.",
            "The finite rooted equivalence is not yet a non-enumerative consequence of theta_*.",
        ],
        "source_closure": [
            {
                "path": str(Path(__file__).resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(Path(__file__)),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("mass_maturity_legacy.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(Path(__file__).with_name("mass_maturity_legacy.py")),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("section_return_core.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(Path(__file__).with_name("section_return_core.py")),
            },
        ],
    }
    payload["projection_digest"] = digest_payload(
        {
            "section_reconstruction": payload["section_reconstruction"],
            "credit_reallocation": payload["credit_reallocation"],
            "colored_obstruction_audit": payload["colored_obstruction_audit"],
            "normal_forms": payload["rooted_obstruction_normal_forms"],
            "contexts": payload["contexts"],
        }
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("channel_artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.channel_artifact)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "credit_reallocation": payload["credit_reallocation"],
                "colored_obstruction_audit": {
                    key: payload["colored_obstruction_audit"][key]
                    for key in (
                        "contexts",
                        "offset_1_present",
                        "offset_1_absent",
                        "unrooted_mixed_classes",
                        "rooted_equivalence_holds",
                    )
                },
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
