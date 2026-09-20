#!/usr/bin/env python3
"""Build the moved-low-slot channel menu on the extremal n=7 carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analyze_n7_extremal_colored_obstructions import (
    CHANNEL_C4,
    _carrier_coordinates,
)
from section_return_core import digest_payload

ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_MOVED_SLOT_MENU_V1"
N = 7
CYCLE = tuple((coordinate + 1) % N for coordinate in range(N))

RolePacket = frozenset[str]
RoleState = dict[int, RolePacket]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _moved_slot_labels(coordinates: dict[str, Any]) -> set[int]:
    alpha = tuple(int(value) for value in coordinates["alpha"])
    return {
        slot for slot, image in enumerate(alpha, start=1) if image != slot
    }


def _slot_coordinates(coordinates: dict[str, Any]) -> dict[int, int]:
    return {1: 1, 2: 2, 3: int(coordinates["h"])}


def _source_role_state(context: dict[str, Any]) -> RoleState:
    state = {}
    for row in context["source_geometry"]["packet_roles"]:
        role = str(row["role"]).split("@")[0]
        state[int(row["coordinate"])] = frozenset({role})
    if set().union(*state.values()) != {"F4", "D1", "D2", "s"}:
        raise AssertionError("extremal source roles drift")
    return state


def _run_corridor(
    state: RoleState,
    word: list[int],
    defect: tuple[int, ...],
    moved: set[int],
) -> tuple[RoleState, RoleState, dict[str, set[int]]]:
    if not word or word[-1] != 1:
        raise AssertionError("strict corridor does not end in d")
    touched: dict[str, set[int]] = defaultdict(set)
    preterminal: RoleState | None = None
    for letter in word:
        transformation = CYCLE if letter == 0 else defect
        if letter == 1:
            for coordinate, packet in state.items():
                if coordinate in moved:
                    for role in packet:
                        touched[role].add(coordinate)
        preterminal = state
        target: dict[int, RolePacket] = {}
        for coordinate, packet in state.items():
            image = transformation[coordinate]
            target[image] = target.get(image, frozenset()) | packet
        state = target
    if preterminal is None:
        raise AssertionError("empty corridor")
    return state, preterminal, touched


def _transport_tags(
    context: dict[str, Any],
    representative: dict[str, Any],
    moved_labels: set[int],
    slot_coordinates: dict[int, int],
) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    coordinate_to_slot = {coordinate: slot for slot, coordinate in slot_coordinates.items()}
    moved_coordinates = {slot_coordinates[slot] for slot in moved_labels}
    edge = representative["edge"]
    rank3, pre_first, first_touched = _run_corridor(
        _source_role_state(context), edge["first_word"], defect, moved_coordinates
    )
    first_parents = pre_first[0] | pre_first[6]
    if "F4" not in first_parents:
        raise AssertionError("C4 first fusion lost F4")
    first_incoming = next(
        role for role in first_parents if role in {"D1", "D2"}
    )

    _, pre_second, second_touched = _run_corridor(
        rank3, edge["second_word"], defect, moved_coordinates
    )
    second_parents = pre_second[0] | pre_second[6]
    second_incoming = next(
        role for role in ("D1", "D2") if role != first_incoming
    )
    if second_incoming not in second_parents:
        raise AssertionError("C4 second fusion lost its incoming mass-two packet")

    first_slots = sorted(
        coordinate_to_slot[coordinate]
        for coordinate in first_touched[first_incoming] & moved_coordinates
    )
    second_slots = sorted(
        coordinate_to_slot[coordinate]
        for coordinate in second_touched[second_incoming] & moved_coordinates
    )
    channel_slots = sorted(set(first_slots) | set(second_slots))
    return {
        "first_incoming_role": first_incoming,
        "second_incoming_role": second_incoming,
        "j_first": first_slots,
        "j_second": second_slots,
        "channel_slots": channel_slots,
    }


def _landing_offset(representative: dict[str, Any]) -> int:
    singleton = next(
        row for row in representative["target_packets"] if row["mass"] == 1
    )
    return int(singleton["coordinate"])


def _witness_summary(
    representative: dict[str, Any], tags: dict[str, Any]
) -> dict[str, Any]:
    edge = representative["edge"]
    return {
        **tags,
        "first_word": edge["first_word"],
        "second_word": edge["second_word"],
        "length_first": edge["length_first"],
        "length_second": edge["length_second"],
        "surplus_first": edge["surplus_first"],
        "surplus_second": edge["surplus_second"],
        "total_length": edge["total_length"],
        "total_surplus": edge["total_surplus"],
        "landing_offset": _landing_offset(representative),
    }


def build_payload(channel_path: Path) -> dict[str, Any]:
    channel_payload = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))
    if channel_payload.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected extremal channel input schema")

    contexts = []
    profile_counts: Counter[tuple[int, int]] = Counter()
    total_relations = 0
    total_memberships = 0
    untagged_relations = 0
    for context in channel_payload["contexts"]:
        defect = tuple(int(value) for value in context["defect"])
        coordinates = _carrier_coordinates(defect)
        moved_labels = _moved_slot_labels(coordinates)
        slot_coordinates = _slot_coordinates(coordinates)
        if not moved_labels:
            continue

        channel_relations: dict[int, list[tuple[dict[str, Any], dict[str, Any]]]] = {
            slot: [] for slot in sorted(moved_labels)
        }
        for representative in context["channel_relations"][CHANNEL_C4]:
            tags = _transport_tags(
                context,
                representative,
                moved_labels,
                slot_coordinates,
            )
            total_relations += 1
            if not tags["channel_slots"]:
                untagged_relations += 1
            for slot in tags["channel_slots"]:
                channel_relations[slot].append((representative, tags))
                total_memberships += 1

        channels = []
        good_slots = []
        for slot in sorted(moved_labels):
            relation = channel_relations[slot]
            offset_one = [
                (representative, tags)
                for representative, tags in relation
                if _landing_offset(representative) == 1
            ]
            if offset_one:
                good_slots.append(slot)
                selected, selected_tags = min(
                    offset_one,
                    key=lambda row: (
                        row[0]["edge"]["total_length"],
                        row[0]["edge"]["first_word"],
                        row[0]["edge"]["second_word"],
                        row[1]["j_first"],
                        row[1]["j_second"],
                    ),
                )
                witness = _witness_summary(selected, selected_tags)
            else:
                witness = None
            channels.append(
                {
                    "j": slot,
                    "carrier_coordinate": slot_coordinates[slot],
                    "directed_low_edge": [
                        slot,
                        int(coordinates["alpha"][slot - 1]),
                    ],
                    "representative_count": len(relation),
                    "landing_offsets": sorted(
                        {_landing_offset(representative) for representative, _ in relation}
                    ),
                    "offset_1_representative_count": len(offset_one),
                    "selected_offset_1_witness": witness,
                }
            )
        if not good_slots:
            raise AssertionError("moved-slot menu failed to cover a nontrivial alpha")
        profile_counts[(len(moved_labels), len(good_slots))] += 1
        contexts.append(
            {
                "index": context["index"],
                "defect": context["defect"],
                "source_mass": context["source_mass"],
                "h": coordinates["h"],
                "alpha": coordinates["alpha"],
                "alpha_cycle_type": coordinates["alpha_cycle_type"],
                "beta": coordinates["beta"],
                "slot_coordinates": {
                    str(slot): coordinate
                    for slot, coordinate in sorted(slot_coordinates.items())
                },
                "moved_slots": sorted(moved_labels),
                "good_moved_slots": good_slots,
                "N_good": len(good_slots),
                "channels": channels,
            }
        )

    if len(contexts) != 30:
        raise AssertionError("moved-slot audit did not isolate 30 nontrivial alphas")
    expected_profiles = {(2, 1): 5, (2, 2): 13, (3, 3): 12}
    if dict(profile_counts) != expected_profiles:
        raise AssertionError(
            f"moved-slot cover profile drift: {dict(profile_counts)}"
        )
    if any(
        channel["representative_count"] == 0
        for context in contexts
        for channel in context["channels"]
    ):
        raise AssertionError("a moved-slot relation channel is empty")

    payload = {
        "schema": SCHEMA,
        "n": N,
        "input": {
            "path": str(channel_path.resolve().relative_to(ROOT).as_posix()),
            "sha256": _sha256(channel_path),
            "schema": channel_payload["schema"],
            "projection_digest": channel_payload["projection_digest"],
        },
        "scope": {
            "domain": "the 30 theta_* contexts with nontrivial low transport alpha",
            "channel_definition": (
                "W_j contains each admissible endpoint-normalized C4 representative "
                "whose incoming mass-two packet traverses the carrier coordinate of "
                "the relabelled moved slot j during its own first or second fusion "
                "corridor"
            ),
            "choice_boundary": (
                "W_j is defined before reading its landing offset; offset 1 is used "
                "only to evaluate Land_1(W_j)"
            ),
            "forbidden_inputs": [
                "P_2/P_3 membership",
                "completion success",
                "W^(2C)",
                "reset coaccessibility",
                "Bellman policy",
            ],
        },
        "counts": {
            "contexts": len(contexts),
            "transposition_contexts": sum(
                row["alpha_cycle_type"] == "TRANSPOSITION" for row in contexts
            ),
            "three_cycle_contexts": sum(
                row["alpha_cycle_type"] == "THREE_CYCLE" for row in contexts
            ),
            "contexts_covered": sum(bool(row["good_moved_slots"]) for row in contexts),
            "C4_representatives": total_relations,
            "moved_slot_channel_memberships": total_memberships,
            "untagged_C4_representatives": untagged_relations,
            "moved_slot_channels": sum(len(row["channels"]) for row in contexts),
            "nonempty_moved_slot_channels": sum(
                channel["representative_count"] > 0
                for row in contexts
                for channel in row["channels"]
            ),
        },
        "cover_profile": {
            f"moved={moved}|good={good}": count
            for (moved, good), count in sorted(profile_counts.items())
        },
        "low_transport_menu_theorem": {
            "statement": (
                "alpha != identity implies there exists j in Mov(alpha) with "
                "Land_1(W_j) nonempty"
            ),
            "contexts_checked": len(contexts),
            "contexts_covered": sum(bool(row["good_moved_slots"]) for row in contexts),
            "maximum_menu_size": max(len(row["moved_slots"]) for row in contexts),
            "three_cycle_all_slots_good": all(
                len(row["good_moved_slots"]) == 3
                for row in contexts
                if row["alpha_cycle_type"] == "THREE_CYCLE"
            ),
            "transposition_at_least_one_slot_good": all(
                row["good_moved_slots"]
                for row in contexts
                if row["alpha_cycle_type"] == "TRANSPOSITION"
            ),
            "proof_boundary": (
                "complete fixed-carrier relation theorem; a symbolic derivation "
                "from the directed moved edge remains open"
            ),
        },
        "contexts": contexts,
        "claims": [
            "The future-free moved-slot channels cover all 30 nontrivial-alpha contexts.",
            "Every moved slot of every three-cycle alpha has an offset-one representative.",
            "Every transposition alpha has at least one good moved slot; six contexts have exactly one.",
            "No P_2 or completion-success label enters the channel definition.",
        ],
        "source_closure": [
            {
                "path": str(Path(__file__).resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(Path(__file__)),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("analyze_n7_extremal_colored_obstructions.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(
                    Path(__file__).with_name(
                        "analyze_n7_extremal_colored_obstructions.py"
                    )
                ),
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
            "counts": payload["counts"],
            "cover_profile": payload["cover_profile"],
            "theorem": payload["low_transport_menu_theorem"],
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
                "counts": payload["counts"],
                "cover_profile": payload["cover_profile"],
                "theorem": payload["low_transport_menu_theorem"],
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
