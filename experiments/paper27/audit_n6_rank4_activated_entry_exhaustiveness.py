#!/usr/bin/env python3
"""Complete fixed-n=6 audit of activated rank-four entry witnesses.

For every collision-image-rooted binary defect, this producer starts at the
canonical kernel-image mass ``mu_d`` and enumerates every admissible raw macro
block whose endpoint has rank four.  Each block is replayed on labelled
packets, so the resulting checkpoint carries a source-addressed activation
basis rather than a tag reconstructed from its mass bytes.

The conclusion is tested without Bellman, winning, reset-coaccessibility, or
raw-closure membership: the rank-four endpoint must have a local raw macro
descent into the exact nonrecursive base ``P_1 union P_2 union P_3``.  A
stronger witness-level diagnostic asks whether such a descent can fuse the
packet freshly created by the activated entry block.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from math import gcd
from pathlib import Path
from typing import Any

from analyze_n6_low_rank_obstruction_peeling import _digest
from analyze_n6_rank4_checkpoint_section import (
    _edge_key,
    _fusion_witness,
    _packet_mass,
    _push_packets,
    _serialize_packet_state,
)
from analyze_n6_rank4_matched_exposure import (
    _pair_exposure_distances,
    _token_bfs,
)
from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, pushforward_mass, simplified_deadline
from rank2_safety_floor_geometry import structural_floor_witness
from single_defect_low_rank_base import build_low_rank_base
from single_defect_macro_trap import _raw_type_i, _raw_type_ii
from single_defect_transport import kernel_blocks


ROOT = Path(__file__).resolve().parents[2]
N = 6
CYCLE = tuple((index + 1) % N for index in range(N))
Mass = tuple[int, ...]
Transformation = tuple[int, ...]
Letters = tuple[Transformation, ...]
Packet = frozenset[int]
PacketState = dict[int, Packet]

ANTIPODAL_BLOCKS = ({0, 3}, {1, 4}, {2, 5})
PARITY_BLOCKS = ({0, 2, 4}, {1, 3, 5})


def _binary_rooted_defects() -> list[Transformation]:
    rows = []
    for defect in itertools.product(range(N), repeat=N):
        counts = Counter(defect)
        if sorted(counts.values()) != [1, 1, 1, 1, 2]:
            continue
        if counts.get(0) != 2:
            continue
        rows.append(tuple(int(value) for value in defect))
    return rows


def _partition(mass: Mass) -> tuple[int, ...]:
    return tuple(sorted((value for value in mass if value), reverse=True))


def _pair_key(row: dict[str, Any]) -> tuple[Any, ...]:
    exposure = row["exposure"]
    return (
        int(exposure["plateau_prefix_cost"]),
        [int(value) for value in exposure["word"]],
        [int(value) for value in row["pair"]],
    )


def _primary_geometry(
    source: Mass,
    letters: tuple[Transformation, Transformation],
    collision: set[int],
) -> dict[str, Any] | None:
    token_sources, distance, parent = _token_bfs(source, letters, (0, 1))
    exposures = _pair_exposure_distances(
        token_sources, distance, parent, collision, 1
    )
    rows = [
        {
            "pair": pair,
            "masses": tuple(sorted((source[pair[0]], source[pair[1]]))),
            "exposure": exposure,
        }
        for pair, exposure in exposures.items()
    ]
    pair11 = sorted(
        (row for row in rows if row["masses"] == (1, 1)), key=_pair_key
    )
    pair31 = sorted(
        (row for row in rows if row["masses"] == (1, 3)), key=_pair_key
    )
    if not pair11 or len(pair31) < 2:
        return None
    if int(pair11[0]["exposure"]["plateau_prefix_cost"]) > 3:
        return None
    if int(pair31[1]["exposure"]["plateau_prefix_cost"]) > 6:
        return None

    primary = (pair11[0], pair31[0], pair31[1])
    heavy = next(index for index, value in enumerate(source) if value == 3)
    pair11_set = set(int(value) for value in primary[0]["pair"])
    primary_lights = {
        next(int(value) for value in row["pair"] if int(value) != heavy)
        for row in primary[1:]
    }
    common = pair11_set & primary_lights
    if len(common) != 1:
        return {
            "incidence": "CLOSED_TRIANGLE",
            "primary": primary,
            "token_sources": token_sources,
            "distance": distance,
            "parent": parent,
        }
    x = next(iter(common))
    y = next(iter(pair11_set - {x}))
    z = next(iter(primary_lights - {x}))
    return {
        "incidence": "OPEN_WEDGE",
        "primary": primary,
        "pair11_rows": pair11,
        "pair31_rows": pair31,
        "labels": (heavy, x, y, z),
        "token_sources": token_sources,
        "distance": distance,
        "parent": parent,
    }


def _defect_text(defect: Transformation) -> str:
    return "".join(str(value) for value in defect)


def _is_idempotent(defect: Transformation) -> bool:
    return tuple(defect[defect[index]] for index in range(N)) == defect


def _preserves_blocks(
    defect: Transformation, blocks: tuple[set[int], ...]
) -> bool:
    owner = {
        point: block_index
        for block_index, block in enumerate(blocks)
        for point in block
    }
    return all(
        len({owner[defect[point]] for point in block}) == 1
        for block in blocks
    )


def _is_predecessor_collapse(defect: Transformation) -> bool:
    predecessor = CYCLE.index(0)
    collision = next(
        block for block in kernel_blocks(defect, N) if len(block) == 2
    )
    return (
        _is_idempotent(defect)
        and set(collision) == {0, predecessor}
        and defect[0] == 0
    )


def _apply_word(
    mass: Mass, word: tuple[int, ...], letters: Letters
) -> Mass:
    current = mass
    for letter_index in word:
        current = pushforward_mass(current, letters[letter_index])
    return current


def _idempotent_comb_chain(
    defect: Transformation, prefix_length: int
) -> list[dict[str, Any]]:
    letters: Letters = (CYCLE, defect)
    word = (0,) * prefix_length + (1,)
    current = pushforward_mass((1,) * N, defect)
    rows = []
    while mass_rank(current) > 1:
        target = _apply_word(current, word, letters)
        credit = simplified_deadline(target, N) - simplified_deadline(
            current, N
        )
        rows.append({
            "source": list(current),
            "word": list(word),
            "target": list(target),
            "length": len(word),
            "credit": credit,
            "surplus": credit - len(word),
        })
        if mass_rank(target) != mass_rank(current) - 1:
            raise AssertionError("idempotent comb did not drop one rank")
        current = target
    return rows


def _activated_basis_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(int(value) for value in row["checkpoint"]),
        int(row["entry_edge"]["total_length"]),
        -int(row["entry_edge"]["total_surplus"]),
        tuple(int(value) for value in row["entry_edge"]["first_word"]),
        tuple(int(value) for value in row["ancestry"]["fresh_packet"]),
        tuple(int(value) for value in row["ancestry"]["parent_sizes"]),
    )


def _entry_choice_key(row: dict[str, Any]) -> tuple[Any, ...]:
    edge = row["activated_basis"]["entry_edge"]
    return (
        int(edge["total_length"]),
        -int(edge["total_surplus"]),
        tuple(int(value) for value in edge["first_word"]),
        tuple(int(value) for value in row["checkpoint"]),
    )


def _local_edge_summary(edge: dict[str, Any] | None) -> dict[str, Any] | None:
    if edge is None:
        return None
    return {
        "type": edge["type"],
        "first_word": [int(value) for value in edge["first_word"]],
        "second_word": [int(value) for value in edge["second_word"]],
        "target": [int(value) for value in edge["target"]],
        "total_length": int(edge["total_length"]),
        "total_surplus": int(edge["total_surplus"]),
    }


def _edge_receipt(
    edge: dict[str, Any],
    checkpoint_packets: PacketState,
    fresh_packet: Packet,
    letters: Letters,
) -> dict[str, Any]:
    _, fusion = _fusion_witness(
        checkpoint_packets, edge["first_word"], letters
    )
    parent_packets = [frozenset(row) for row in fusion["parent_packets"]]
    return {
        "type": edge["type"],
        "first_word": [int(value) for value in edge["first_word"]],
        "second_word": [int(value) for value in edge["second_word"]],
        "intermediate": edge["intermediate"],
        "target": [int(value) for value in edge["target"]],
        "target_rank": int(edge["rank_target"]),
        "total_length": int(edge["total_length"]),
        "surplus_first": int(edge["surplus_first"]),
        "surplus_second": int(edge["surplus_second"]),
        "total_surplus": int(edge["total_surplus"]),
        "first_fusion": fusion,
        "first_fusion_contains_fresh_packet": fresh_packet in parent_packets,
    }


def _analyze_defect(defect: Transformation) -> dict[str, Any]:
    letters: Letters = (CYCLE, defect)
    defect_text = _defect_text(defect)
    floor = structural_floor_witness(defect)
    base = build_low_rank_base(letters, N)
    synchronizing = bool(base["rank_counts"].get("1", {}).get("states", 0))
    if not synchronizing:
        return {
            "defect": defect_text,
            "synchronizing": False,
            "safety_floor": floor is not None,
            "counts": {},
            "checkpoint_rows": [],
            "failure_rows": [],
        }
    if floor is None:
        raise AssertionError("synchronizing rooted defect violates SafetyFloor")

    base_labels = {
        tuple(int(value) for value in row["mass"]): bool(
            row["in_low_rank_base"]
        )
        for row in base["rows"]
    }
    collision_blocks = [
        set(int(value) for value in block)
        for block in kernel_blocks(defect, N)
        if len(block) == 2
    ]
    if len(collision_blocks) != 1:
        raise AssertionError("binary defect lost its unique collision block")
    collision = collision_blocks[0]

    singleton_packets = {
        index: frozenset((index,)) for index in range(N)
    }
    mu_packets = _push_packets(singleton_packets, defect)
    mu_d = _packet_mass(mu_packets, N)
    if mass_rank(mu_d) != 5:
        raise AssertionError("binary defect did not produce rank-five mu_d")

    exit_cache: dict[Mass, list[dict[str, Any]]] = {}

    def exits_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in exit_cache:
            exit_cache[mass] = endpoint_shortest_exits(mass, letters, N)
        return exit_cache[mass]

    initial_edges = _raw_type_i(mu_d, exits_for(mu_d), N)
    initial_edges.extend(_raw_type_ii(mu_d, exits_for(mu_d), exits_for, N))
    entry_edges = [
        edge for edge in initial_edges if int(edge["rank_target"]) == 4
    ]
    if any(edge["type"] != "I" for edge in entry_edges):
        raise AssertionError("rank-five to rank-four entry was not Type-I")

    edges_by_checkpoint: dict[Mass, list[dict[str, Any]]] = defaultdict(list)
    for edge in entry_edges:
        checkpoint = tuple(int(value) for value in edge["target"])
        edges_by_checkpoint[checkpoint].append(edge)

    counts = Counter()
    checkpoint_rows = []
    failure_rows = []
    for checkpoint, activated_edges in sorted(edges_by_checkpoint.items()):
        part = _partition(checkpoint)
        local_edges = _raw_type_i(checkpoint, exits_for(checkpoint), N)
        local_edges.extend(
            _raw_type_ii(checkpoint, exits_for(checkpoint), exits_for, N)
        )
        local_edges = [
            edge
            for edge in local_edges
            if int(edge["rank_target"]) <= 3
            and base_labels.get(
                tuple(int(value) for value in edge["target"]), False
            )
        ]
        local_edges.sort(key=_edge_key)
        has_local_descent = bool(local_edges)
        local_type_i = [edge for edge in local_edges if edge["type"] == "I"]
        local_type_ii = [edge for edge in local_edges if edge["type"] == "II"]

        geometry = None
        if part == (3, 1, 1, 1):
            geometry = _primary_geometry(checkpoint, letters, collision)
        g4 = geometry is not None
        incidence = None if geometry is None else geometry["incidence"]
        geometry_labels = (
            None
            if geometry is None or "labels" not in geometry
            else [int(value) for value in geometry["labels"]]
        )

        basis_rows = []
        for entry_edge in sorted(activated_edges, key=_edge_key):
            checkpoint_packets, ancestry = _fusion_witness(
                mu_packets, entry_edge["first_word"], letters
            )
            if _packet_mass(checkpoint_packets, N) != checkpoint:
                raise AssertionError("activated packet basis misses checkpoint")
            fresh_packet = frozenset(ancestry["fresh_packet"])
            fresh_coordinates = [
                coordinate
                for coordinate, packet in checkpoint_packets.items()
                if packet == fresh_packet
            ]
            if fresh_coordinates != [ancestry["target_coordinate"]]:
                raise AssertionError("fresh packet coordinate is not activated")
            expected_fusion = {
                (3, 1, 1, 1): ([1, 2], 3),
                (2, 2, 1, 1): ([1, 1], 2),
            }.get(part)
            if expected_fusion is None:
                raise AssertionError("rank-four entry has an unexpected partition")
            expected_parents, expected_fresh_size = expected_fusion
            if ancestry["fresh_size"] != expected_fresh_size:
                raise AssertionError("rank-four entry fresh-packet size drift")
            if ancestry["parent_sizes"] != expected_parents:
                raise AssertionError("rank-four entry parent-size type drift")

            local_receipts = [
                _edge_receipt(
                    edge, checkpoint_packets, fresh_packet, letters
                )
                for edge in local_edges
            ]
            fresh_receipts = [
                receipt
                for receipt in local_receipts
                if receipt["first_fusion_contains_fresh_packet"]
            ]
            counts["activated_bases"] += 1
            counts["activated_bases_with_fresh_descent"] += int(
                bool(fresh_receipts)
            )
            basis = {
                "checkpoint": list(checkpoint),
                "entry_edge": {
                    "type": entry_edge["type"],
                    "first_word": [
                        int(value) for value in entry_edge["first_word"]
                    ],
                    "total_length": int(entry_edge["total_length"]),
                    "total_surplus": int(entry_edge["total_surplus"]),
                },
                "ancestry": ancestry,
                "checkpoint_packets": _serialize_packet_state(
                    checkpoint_packets
                ),
                "fresh_descent_count": len(fresh_receipts),
                "best_fresh_descent": (
                    fresh_receipts[0] if fresh_receipts else None
                ),
            }
            basis_rows.append(basis)
            if not fresh_receipts:
                failure_rows.append({
                    "kind": "NO_FRESH_PACKET_DESCENT",
                    "defect": defect_text,
                    "checkpoint": list(checkpoint),
                    "partition": list(part),
                    "activated_basis": basis,
                    "local_descent_count": len(local_edges),
                })

        basis_rows.sort(key=_activated_basis_key)
        counts["activated_checkpoints"] += 1
        counts[f"partition:{part}"] += 1
        counts[f"partition:{part}:with_local_descent"] += int(
            has_local_descent
        )
        counts["checkpoints_with_local_descent"] += int(has_local_descent)
        counts["checkpoints_without_local_descent"] += int(
            not has_local_descent
        )
        if part == (3, 1, 1, 1):
            counts["unbalanced_checkpoints"] += 1
            counts["unbalanced_checkpoints_passing_G4"] += int(g4)
            counts[f"unbalanced_incidence:{incidence}"] += 1
        if not has_local_descent:
            failure_rows.append({
                "kind": "NO_LOCAL_DESCENT",
                "defect": defect_text,
                "checkpoint": list(checkpoint),
                "partition": list(part),
                "activated_basis_count": len(basis_rows),
                "activated_bases": basis_rows,
            })

        checkpoint_rows.append({
            "checkpoint": list(checkpoint),
            "partition": list(part),
            "activated_basis_count": len(basis_rows),
            "has_local_descent": has_local_descent,
            "local_descent_count": len(local_edges),
            "local_type_i_descent_count": len(local_type_i),
            "local_type_ii_descent_count": len(local_type_ii),
            "best_local_descent": _local_edge_summary(
                local_edges[0] if local_edges else None
            ),
            "best_local_type_i_descent": _local_edge_summary(
                local_type_i[0] if local_type_i else None
            ),
            "best_local_type_ii_descent": _local_edge_summary(
                local_type_ii[0] if local_type_ii else None
            ),
            "G4": g4,
            "G4_incidence": incidence,
            "G4_labels_Hxyz": geometry_labels,
            "activated_bases": basis_rows,
        })

    section_candidates = [
        {
            "checkpoint": row["checkpoint"],
            "partition": row["partition"],
            "has_local_descent": row["has_local_descent"],
            "local_type_i_descent_count": row[
                "local_type_i_descent_count"
            ],
            "local_type_ii_descent_count": row[
                "local_type_ii_descent_count"
            ],
            "best_local_descent": row["best_local_descent"],
            "best_local_type_i_descent": row[
                "best_local_type_i_descent"
            ],
            "best_local_type_ii_descent": row[
                "best_local_type_ii_descent"
            ],
            "G4": row["G4"],
            "G4_incidence": row["G4_incidence"],
            "G4_labels_Hxyz": row["G4_labels_Hxyz"],
            "activated_basis": basis,
        }
        for row in checkpoint_rows
        for basis in row["activated_bases"]
    ]
    if not section_candidates:
        raise AssertionError("synchronizing action has no activated rank-four entry")
    minimum_choice = min(section_candidates, key=_entry_choice_key)
    section_choice = minimum_choice
    selector_case = "ENDPOINT_SHORTEST"
    if _is_predecessor_collapse(defect):
        exceptional = [
            row
            for row in section_candidates
            if row["activated_basis"]["entry_edge"]["first_word"]
            == [0] * (N - 1) + [1]
        ]
        if len(exceptional) != 1:
            raise AssertionError("predecessor-collapse entry normal form drift")
        section_choice = exceptional[0]
        selector_case = "PREDECESSOR_IDEMPOTENT_P5D"

    entry_choice_audit = {
        "selector_name": "ROOTED_N6_ENTRY_SECTION_V1",
        "selector_case": selector_case,
        "minimum_choice": {
            "checkpoint": minimum_choice["checkpoint"],
            "partition": minimum_choice["partition"],
            "entry_edge": minimum_choice["activated_basis"]["entry_edge"],
            "has_local_descent": minimum_choice["has_local_descent"],
            "local_type_i_descent_count": minimum_choice[
                "local_type_i_descent_count"
            ],
            "local_type_ii_descent_count": minimum_choice[
                "local_type_ii_descent_count"
            ],
            "best_local_descent": minimum_choice["best_local_descent"],
            "best_local_type_i_descent": minimum_choice[
                "best_local_type_i_descent"
            ],
            "best_local_type_ii_descent": minimum_choice[
                "best_local_type_ii_descent"
            ],
            "G4": minimum_choice["G4"],
            "G4_incidence": minimum_choice["G4_incidence"],
            "G4_labels_Hxyz": minimum_choice["G4_labels_Hxyz"],
        },
        "section_choice": {
            "checkpoint": section_choice["checkpoint"],
            "partition": section_choice["partition"],
            "entry_edge": section_choice["activated_basis"]["entry_edge"],
            "activated_basis": section_choice["activated_basis"],
            "has_local_descent": section_choice["has_local_descent"],
            "local_type_i_descent_count": section_choice[
                "local_type_i_descent_count"
            ],
            "local_type_ii_descent_count": section_choice[
                "local_type_ii_descent_count"
            ],
            "best_local_descent": section_choice["best_local_descent"],
            "best_local_type_i_descent": section_choice[
                "best_local_type_i_descent"
            ],
            "best_local_type_ii_descent": section_choice[
                "best_local_type_ii_descent"
            ],
            "G4": section_choice["G4"],
            "G4_incidence": section_choice["G4_incidence"],
            "G4_labels_Hxyz": section_choice["G4_labels_Hxyz"],
            "has_fresh_packet_descent": bool(
                section_choice["activated_basis"]["fresh_descent_count"]
            ),
        },
    }

    return {
        "defect": defect_text,
        "synchronizing": True,
        "safety_floor": True,
        "kernel_type": floor["kernel_type"],
        "mu_d": list(mu_d),
        "counts": dict(sorted(counts.items())),
        "entry_choice_audit": entry_choice_audit,
        "checkpoint_rows": checkpoint_rows,
        "failure_rows": failure_rows,
    }


def run(
    start: int,
    stop: int | None,
    workers: int,
    failure_limit: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    all_rooted = _binary_rooted_defects()
    upper = len(all_rooted) if stop is None else min(stop, len(all_rooted))
    selected = all_rooted[start:upper]
    if workers <= 1:
        action_rows = [_analyze_defect(defect) for defect in selected]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            action_rows = list(
                executor.map(_analyze_defect, selected, chunksize=4)
            )

    counts = Counter()
    minimum_entry_forms = Counter()
    synchronizing_action_rows = []
    failure_rows = []
    for action in action_rows:
        counts["rooted_binary_defects_scanned"] += 1
        counts["safety_floor_actions"] += int(action["safety_floor"])
        counts["synchronizing_actions"] += int(action["synchronizing"])
        if not action["synchronizing"]:
            continue
        synchronizing_action_rows.append({
            "defect": action["defect"],
            "kernel_type": action["kernel_type"],
            "mu_d": action["mu_d"],
            "counts": action["counts"],
            "entry_choice_audit": action["entry_choice_audit"],
        })
        counts.update(action["counts"])
        action_counts = Counter(action["counts"])
        counts["synchronizing_actions_with_activated_checkpoint"] += int(
            action_counts["activated_checkpoints"] > 0
        )
        counts["synchronizing_actions_with_good_activated_checkpoint"] += int(
            action_counts["checkpoints_with_local_descent"] > 0
        )
        counts["synchronizing_actions_with_bad_activated_checkpoint"] += int(
            action_counts["checkpoints_without_local_descent"] > 0
        )
        counts["synchronizing_actions_with_good_balanced_checkpoint"] += int(
            action_counts["partition:(2, 2, 1, 1):with_local_descent"] > 0
        )
        counts["synchronizing_actions_with_good_unbalanced_checkpoint"] += int(
            action_counts["partition:(3, 1, 1, 1):with_local_descent"] > 0
        )
        choice = action["entry_choice_audit"]
        minimum_word = tuple(
            int(value)
            for value in choice["minimum_choice"]["entry_edge"]["first_word"]
        )
        pure_rotation_entry = (
            minimum_word[-1:] == (1,)
            and all(value == 0 for value in minimum_word[:-1])
            and len(minimum_word) <= 3
        )
        if not pure_rotation_entry:
            raise AssertionError("minimum entry left the p^a d normal forms")
        minimum_entry_forms[
            (
                len(minimum_word) - 1,
                tuple(choice["minimum_choice"]["partition"]),
                bool(choice["minimum_choice"]["has_local_descent"]),
            )
        ] += 1
        counts["minimum_entry_selector_failures"] += int(
            not choice["minimum_choice"]["has_local_descent"]
        )
        counts["entry_section_selected_actions"] += 1
        counts["entry_section_selected_local_descents"] += int(
            choice["section_choice"]["has_local_descent"]
        )
        counts["entry_section_selected_fresh_descents"] += int(
            choice["section_choice"]["has_fresh_packet_descent"]
        )
        failure_rows.extend(action["failure_rows"])

    trichotomy_counts = Counter()
    trichotomy_rows = []
    for action in action_rows:
        defect = tuple(int(value) for value in action["defect"])
        preserves_antipodal = _preserves_blocks(defect, ANTIPODAL_BLOCKS)
        preserves_parity = _preserves_blocks(defect, PARITY_BLOCKS)
        predecessor_collapse = _is_predecessor_collapse(defect)
        if preserves_antipodal and preserves_parity:
            raise AssertionError("rooted defect preserves both cyclic block systems")
        if preserves_antipodal:
            case = "ANTIPODAL_BLOCK_OBSTRUCTION"
        elif preserves_parity:
            case = "PARITY_BLOCK_OBSTRUCTION"
        elif predecessor_collapse:
            case = "PREDECESSOR_IDEMPOTENT_EXCEPTION"
        else:
            case = "GENERIC_MINIMUM_ENTRY_SECTION"
        trichotomy_counts[case] += 1

        synchronizing = bool(action["synchronizing"])
        if preserves_antipodal or preserves_parity:
            if synchronizing:
                raise AssertionError("block-preserving rooted defect synchronized")
            minimum_good = False
        else:
            if not synchronizing:
                raise AssertionError("non-block-preserving rooted defect failed to sync")
            minimum_good = bool(
                action["entry_choice_audit"]["minimum_choice"][
                    "has_local_descent"
                ]
            )
        if minimum_good != (case == "GENERIC_MINIMUM_ENTRY_SECTION"):
            raise AssertionError("rooted minimum-entry trichotomy drift")
        trichotomy_rows.append({
            "defect": action["defect"],
            "case": case,
            "synchronizing": synchronizing,
            "minimum_entry_has_local_descent": minimum_good,
        })

    idempotent_rows = []
    for action in action_rows:
        defect = tuple(int(value) for value in action["defect"])
        if not _is_idempotent(defect):
            continue
        missing = next(iter(set(range(N)) - set(defect)))
        collision = next(
            block
            for block in kernel_blocks(defect, N)
            if len(block) == 2
        )
        idempotent_rows.append({
            "defect": action["defect"],
            "missing_image": missing,
            "kernel_pair": list(collision),
            "gcd_6_missing": gcd(N, missing),
            "synchronizing": bool(action["synchronizing"]),
        })
    if len(idempotent_rows) != 5:
        raise AssertionError("rooted idempotent classification drift")
    if any(
        row["synchronizing"] != (row["gcd_6_missing"] == 1)
        for row in idempotent_rows
    ):
        raise AssertionError("idempotent gcd synchronization criterion drift")

    predecessor = tuple(int(value) for value in "012340")
    successor = tuple(int(value) for value in "002345")
    predecessor_chain = _idempotent_comb_chain(predecessor, 5)
    successor_chain = _idempotent_comb_chain(successor, 1)
    if any(row["surplus"] != 0 for row in predecessor_chain):
        raise AssertionError("predecessor idempotent comb lost zero surplus")
    if any(row["surplus"] != 4 for row in successor_chain):
        raise AssertionError("successor idempotent comb surplus drift")

    minimum_failure_rows = [
        action
        for action in synchronizing_action_rows
        if not action["entry_choice_audit"]["minimum_choice"][
            "has_local_descent"
        ]
    ]
    if [row["defect"] for row in minimum_failure_rows] != ["012340"]:
        raise AssertionError("minimum-entry intrinsic exception drift")
    return {
        "schema": "single-defect-n6-rank4-activated-entry-exhaustiveness-v1",
        "scope": {
            "n": N,
            "cycle": list(CYCLE),
            "rooting": "the unique binary-kernel collision image is coordinate 0",
            "range": [start, upper],
            "complete_scope": start == 0 and upper == len(all_rooted),
            "checkpoint_semantics": (
                "rank-four endpoints of one admissible raw macro block from mu_d"
            ),
            "activation_semantics": (
                "a replayable preceding macro edge plus its actual parent and fresh packets"
            ),
            "conclusion_semantics": (
                "a local raw Type-I/II macro descent into exact P_1/P_2/P_3"
            ),
            "entry_section": (
                "choose the endpoint-shortest activated block, except the "
                "intrinsic predecessor idempotent chooses its p^5 d return block"
            ),
            "entry_section_forbidden_inputs": [
                "local-descent success",
                "P_1/P_2/P_3 target membership",
                "Bellman or winning data",
                "reset coaccessibility",
            ],
            "forbidden_predicate_inputs": [
                "Bellman policy or value",
                "winning label",
                "ordinary reset coaccessibility",
                "raw macro reachability as a state predicate",
                "mass-byte reconstruction of fresh ancestry",
            ],
        },
        "counts": dict(sorted(counts.items())),
        "synchronizing_action_rows": synchronizing_action_rows,
        "failure_rows": failure_rows[:failure_limit],
        "failure_rows_total": len(failure_rows),
        "symbolic_classification": {
            "minimum_entry_word_lemma": {
                "statement": (
                    "the local endpoint-shortest activated word is p^a d "
                    "for a in {0,1,2}"
                ),
                "proof_basis": (
                    "the rank-five support omits one coordinate; among three "
                    "successive omissions at most two can hit the binary "
                    "kernel pair"
                ),
                "normal_form_counts": [
                    {
                        "a": a,
                        "endpoint_partition": list(partition),
                        "has_local_descent": good,
                        "count": count,
                    }
                    for (a, partition, good), count
                    in sorted(minimum_entry_forms.items())
                ],
            },
            "rooted_idempotent_classification": {
                "statement": (
                    "a rooted binary idempotent is e_m: m maps to 0 and all "
                    "other image points are fixed; <p,e_m> synchronizes iff "
                    "gcd(6,m)=1"
                ),
                "rows": idempotent_rows,
                "synchronizing_orientations": {
                    "successor_collapse": "002345",
                    "predecessor_collapse": "012340",
                },
            },
            "rooted_minimum_entry_trichotomy": {
                "statement": (
                    "the minimum activated entry has a local descent iff d "
                    "preserves neither nontrivial cyclic block system and d "
                    "is not the predecessor idempotent"
                ),
                "block_systems": {
                    "antipodal": [sorted(block) for block in ANTIPODAL_BLOCKS],
                    "parity": [sorted(block) for block in PARITY_BLOCKS],
                },
                "counts": dict(sorted(trichotomy_counts.items())),
                "rows": trichotomy_rows,
                "proof_status": {
                    "block_obstruction": (
                        "symbolic: p and d preserve a nontrivial quotient, so "
                        "their semigroup cannot synchronize"
                    ),
                    "predecessor_exception": (
                        "symbolic: the minimum p^2 d endpoint is hostile and "
                        "the intrinsic p^5 d comb supplies the section"
                    ),
                    "generic_complement": (
                        "exact finite symbolic exhaustion with explicit local "
                        "P_<=3 receipts; a non-enumerative derivation remains open"
                    ),
                },
            },
            "predecessor_exception": {
                "intrinsic_condition": (
                    "idempotent with kernel {0,p^-1(0)} and collision image 0"
                ),
                "minimum_bad_entry": minimum_failure_rows[0][
                    "entry_choice_audit"
                ]["minimum_choice"],
                "selected_entry_word": [0, 0, 0, 0, 0, 1],
                "zero_surplus_comb": predecessor_chain,
            },
            "successor_control": {
                "intrinsic_condition": (
                    "idempotent with kernel {0,p(0)} and collision image 0"
                ),
                "positive_surplus_comb": successor_chain,
            },
            "remaining_symbolic_gap": (
                "replace the exact finite generic-complement exhaustion by a "
                "non-enumerative derivation of its local P_<=3 receipt"
            ),
        },
        "theorem_boundary": {
            "fixed_n6_existential_entry_escape_holds": (
                counts["synchronizing_actions"]
                == counts[
                    "synchronizing_actions_with_good_activated_checkpoint"
                ]
            ),
            "fixed_n6_local_entry_section_holds": (
                counts["entry_section_selected_actions"]
                == counts["entry_section_selected_local_descents"]
            ),
            "universal_activated_checkpoint_escape_holds": (
                counts["checkpoints_without_local_descent"] == 0
            ),
            "universal_fresh_packet_strengthening_holds": (
                counts["activated_bases"]
                == counts["activated_bases_with_fresh_descent"]
            ),
            "G4_is_not_the_checkpoint_predicate": True,
            "interpretation": (
                "Activated one-edge ancestry is a typed Entry witness. The "
                "fixed-n=6 section uses only rooted action and entry-corridor "
                "data; raw macro closure is not promoted to a state predicate."
            ),
        },
        "claim_boundary": [
            "This is a complete fixed-n=6 rooted binary-defect computation, not an all-n theorem.",
            "The result concerns the initial rank-four checkpoint reached from mu_d; higher-n return-map inheritance remains open.",
            "The activated witness is generated by one verified preceding macro edge and cannot be forged from endpoint mass bytes.",
            "G4 remains a useful exposure consequence on the unbalanced branch, but it is not sufficient for local escape.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--workers", type=int, default=max(1, min(12, os.cpu_count() or 1))
    )
    parser.add_argument("--failure-limit", type=int, default=100)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.start, args.stop, args.workers, args.failure_limit)
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("analyze_n6_rank4_checkpoint_section.py"),
        producer.with_name("analyze_n6_rank4_matched_exposure.py"),
        producer.with_name("analyze_n6_rank4_structural_descent.py"),
        producer.with_name("analyze_n6_low_rank_obstruction_peeling.py"),
        producer.with_name("rank2_safety_floor_geometry.py"),
        producer.with_name("single_defect_low_rank_base.py"),
        producer.with_name("single_defect_macro_trap.py"),
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
        "counts": payload["counts"],
        "failure_rows_total": payload["failure_rows_total"],
        "theorem_boundary": payload["theorem_boundary"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
