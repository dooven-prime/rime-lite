#!/usr/bin/env python3
"""Audit edge-to-fusion germs in the n=7 extremal moved-slot menu."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analyze_n7_extremal_colored_obstructions import CHANNEL_C4
from analyze_n7_extremal_moved_slot_menu import (
    INPUT_SCHEMA as CHANNEL_SCHEMA,
)
from analyze_n7_extremal_moved_slot_menu import (
    SCHEMA as MENU_SCHEMA,
)
from analyze_n7_extremal_moved_slot_menu import (
    _landing_offset,
    _source_role_state,
)
from section_return_core import digest_payload

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_EDGE_GERMS_V1"
N = 7
CYCLE = tuple((coordinate + 1) % N for coordinate in range(N))

RolePacket = frozenset[str]
RoleState = dict[int, RolePacket]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply(state: RoleState, transformation: tuple[int, ...]) -> RoleState:
    target: RoleState = {}
    for coordinate, packet in state.items():
        image = transformation[coordinate]
        target[image] = target.get(image, frozenset()) | packet
    return target


def _terminal_rotation_exponent(word: list[int]) -> int:
    if not word or word[-1] != 1:
        raise AssertionError("strict corridor does not end in d")
    exponent = 0
    for letter in reversed(word[:-1]):
        if letter != 0:
            break
        exponent += 1
    return exponent


def _trace_corridor(
    state: RoleState,
    word: list[int],
    defect: tuple[int, ...],
    slot_coordinates: dict[int, int],
) -> tuple[RoleState, RoleState, dict[str, list[dict[str, Any]]]]:
    if not word or word[-1] != 1:
        raise AssertionError("strict corridor does not end in d")
    coordinate_to_slot = {
        coordinate: slot for slot, coordinate in slot_coordinates.items()
    }
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    preterminal: RoleState | None = None
    terminal_index = len(word) - 1
    terminal_rotation = _terminal_rotation_exponent(word)
    d_ordinal = 0
    for letter_index, letter in enumerate(word):
        transformation = CYCLE if letter == 0 else defect
        preterminal = state
        if letter == 1:
            f4_before = next(
                coordinate
                for coordinate, packet in state.items()
                if "F4" in packet
            )
            target = _apply(state, transformation)
            f4_after = next(
                coordinate
                for coordinate, packet in target.items()
                if "F4" in packet
            )
            for coordinate, packet in state.items():
                slot = coordinate_to_slot.get(coordinate)
                if slot is None:
                    continue
                for role in packet:
                    events[role].append(
                        {
                            "letter_index": letter_index,
                            "d_ordinal": d_ordinal,
                            "j": slot,
                            "carrier_coordinate": coordinate,
                            "alpha_image": defect[coordinate],
                            "incoming_coordinate_after": defect[coordinate],
                            "F4_coordinate_before": f4_before,
                            "F4_coordinate_after": f4_after,
                            "rank_preserving_d_after": sum(
                                later == 1
                                for later in word[letter_index + 1 : terminal_index]
                            ),
                            "terminal_rotation_exponent": terminal_rotation,
                            "tagged_to_terminal_word": word[letter_index:],
                            "edge_to_terminal_suffix": word[letter_index + 1 :],
                            "tagged_d_is_terminal": letter_index == terminal_index,
                        }
                    )
            state = target
            d_ordinal += 1
        else:
            state = _apply(state, transformation)
    if preterminal is None:
        raise AssertionError("empty corridor")
    return state, preterminal, events


def _representative_germs(
    context: dict[str, Any],
    representative: dict[str, Any],
    slot_coordinates: dict[int, int],
) -> dict[int, list[dict[str, Any]]]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    edge = representative["edge"]
    rank3, pre_first, first_events = _trace_corridor(
        _source_role_state(context),
        edge["first_word"],
        defect,
        slot_coordinates,
    )
    first_parents = pre_first[0] | pre_first[6]
    first_incoming = next(role for role in first_parents if role in {"D1", "D2"})

    _, pre_second, second_events = _trace_corridor(
        rank3,
        edge["second_word"],
        defect,
        slot_coordinates,
    )
    second_parents = pre_second[0] | pre_second[6]
    second_incoming = next(
        role for role in ("D1", "D2") if role != first_incoming
    )
    if second_incoming not in second_parents:
        raise AssertionError("second C4 fusion lost its incoming mass-two packet")

    germs: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for corridor, role, rows in (
        (1, first_incoming, first_events[first_incoming]),
        (2, second_incoming, second_events[second_incoming]),
    ):
        for row in rows:
            germs[row["j"]].append(
                {
                    **row,
                    "corridor": corridor,
                    "incoming_role": role,
                }
            )
    return germs


def _formula_k(context: dict[str, Any], alpha: list[int]) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["defect"])
    role_coordinates = {
        str(row["role"]).split("@")[0]: int(row["coordinate"])
        for row in context["source_geometry"]["packet_roles"]
    }
    predicted = {
        "F4": 0,
        "D_rec_1": int(alpha[1]),
        "D_rec_2": defect[int(alpha[1]) + 2],
        "s": defect[int(alpha[2]) + 2],
    }
    verified = (
        predicted["F4"] == role_coordinates["F4"]
        and predicted["s"] == role_coordinates["s"]
        and sorted((predicted["D_rec_1"], predicted["D_rec_2"]))
        == sorted((role_coordinates["D1"], role_coordinates["D2"]))
    )
    return {
        "predicted": predicted,
        "observed": role_coordinates,
        "verified": verified,
        "label_boundary": (
            "D_rec_1/D_rec_2 are ordered ancestry addresses; observed D1/D2 "
            "are canonically sorted by current coordinate"
        ),
    }


def _germ_witness(
    representative: dict[str, Any], event: dict[str, Any]
) -> dict[str, Any]:
    edge = representative["edge"]
    return {
        **event,
        "first_word": edge["first_word"],
        "second_word": edge["second_word"],
        "length_first": edge["length_first"],
        "length_second": edge["length_second"],
        "surplus_first": edge["surplus_first"],
        "surplus_second": edge["surplus_second"],
        "total_length": edge["total_length"],
        "landing_offset": _landing_offset(representative),
    }


def build_payload(menu_path: Path) -> dict[str, Any]:
    menu_payload = json.loads(menu_path.read_text(encoding="utf-8", newline="\n"))
    if menu_payload.get("schema") != MENU_SCHEMA:
        raise AssertionError("unexpected moved-slot menu schema")
    channel_path = ROOT / menu_payload["input"]["path"]
    channel_payload = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))
    if channel_payload.get("schema") != CHANNEL_SCHEMA:
        raise AssertionError("unexpected extremal channel schema")
    if _sha256(channel_path) != menu_payload["input"]["sha256"]:
        raise AssertionError("moved-slot input no longer binds the channel artifact")

    source_by_defect = {row["defect"]: row for row in channel_payload["contexts"]}
    contexts = []
    r_profile: Counter[int] = Counter()
    all_r_profile: Counter[int] = Counter()
    formula_k_verified = 0
    total_event_memberships = 0
    for menu_context in menu_payload["contexts"]:
        source = source_by_defect[menu_context["defect"]]
        slot_coordinates = {
            int(slot): int(coordinate)
            for slot, coordinate in menu_context["slot_coordinates"].items()
        }
        formula = _formula_k(source, menu_context["alpha"])
        formula_k_verified += int(formula["verified"])

        relation_by_slot: dict[
            int, list[tuple[dict[str, Any], list[dict[str, Any]]]]
        ] = {slot: [] for slot in menu_context["moved_slots"]}
        for representative in source["channel_relations"][CHANNEL_C4]:
            germs = _representative_germs(source, representative, slot_coordinates)
            for slot, events in germs.items():
                if slot not in relation_by_slot:
                    continue
                relation_by_slot[slot].append((representative, events))
                total_event_memberships += len(events)

        channels = []
        for expected in menu_context["channels"]:
            slot = int(expected["j"])
            relation = relation_by_slot[slot]
            if len(relation) != expected["representative_count"]:
                raise AssertionError("edge germs did not reconstruct W_j")
            all_events = [
                event for _, events in relation for event in events
            ]
            offset_one_events = [
                (representative, event)
                for representative, events in relation
                if _landing_offset(representative) == 1
                for event in events
            ]
            if bool(offset_one_events) != (
                expected["selected_offset_1_witness"] is not None
            ):
                raise AssertionError("edge germs did not reconstruct Land_1(W_j)")
            minimum_all = min(
                event["rank_preserving_d_after"] for event in all_events
            )
            all_r_profile[minimum_all] += 1
            if offset_one_events:
                selected_rep, selected_event = min(
                    offset_one_events,
                    key=lambda row: (
                        row[1]["rank_preserving_d_after"],
                        len(row[1]["edge_to_terminal_suffix"]),
                        row[0]["edge"]["total_length"],
                        row[0]["edge"]["first_word"],
                        row[0]["edge"]["second_word"],
                    ),
                )
                minimum_offset_one = selected_event["rank_preserving_d_after"]
                r_profile[minimum_offset_one] += 1
                witness = _germ_witness(selected_rep, selected_event)
            else:
                minimum_offset_one = None
                witness = None
            channels.append(
                {
                    "j": slot,
                    "carrier_coordinate": slot_coordinates[slot],
                    "directed_low_edge": expected["directed_low_edge"],
                    "representative_count": len(relation),
                    "tagged_event_count": len(all_events),
                    "landing_offsets": expected["landing_offsets"],
                    "r_min_all": minimum_all,
                    "r_min_Land_1": minimum_offset_one,
                    "selected_shallow_Land_1_germ": witness,
                }
            )
        contexts.append(
            {
                "index": menu_context["index"],
                "defect": menu_context["defect"],
                "h": menu_context["h"],
                "alpha": menu_context["alpha"],
                "alpha_cycle_type": menu_context["alpha_cycle_type"],
                "beta": menu_context["beta"],
                "moved_slots": menu_context["moved_slots"],
                "good_moved_slots": menu_context["good_moved_slots"],
                "formula_K": formula,
                "channels": channels,
            }
        )

    good_channels = sum(
        row["r_min_Land_1"] is not None
        for context in contexts
        for row in context["channels"]
    )
    if formula_k_verified != len(contexts):
        raise AssertionError("carrier packet-position formula (K) drift")
    if good_channels != 67:
        raise AssertionError("unexpected Land_1 moved-slot channel count")

    payload = {
        "schema": SCHEMA,
        "n": N,
        "inputs": [
            {
                "path": str(menu_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(menu_path),
                "schema": menu_payload["schema"],
                "projection_digest": menu_payload["projection_digest"],
            },
            {
                "path": str(channel_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(channel_path),
                "schema": channel_payload["schema"],
                "projection_digest": channel_payload["projection_digest"],
            },
        ],
        "scope": {
            "domain": "the 72 W_j channels in the 30 nontrivial-alpha extremal contexts",
            "germ_depth": (
                "number of additional rank-preserving d occurrences strictly "
                "between the tagged j->alpha(j) edge and the terminal strict d "
                "of the same incoming packet's fusion corridor"
            ),
            "choice_boundary": (
                "tagged germs are constructed before reading the landing offset; "
                "Land_1 is an evaluation-only filter"
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
            "channels": sum(len(row["channels"]) for row in contexts),
            "Land_1_channels": good_channels,
            "non_Land_1_channels": sum(
                row["r_min_Land_1"] is None
                for context in contexts
                for row in context["channels"]
            ),
            "tagged_event_memberships": total_event_memberships,
            "formula_K_verified_contexts": formula_k_verified,
        },
        "r_min_all_profile": {
            str(depth): count for depth, count in sorted(all_r_profile.items())
        },
        "r_min_Land_1_profile": {
            str(depth): count for depth, count in sorted(r_profile.items())
        },
        "shallow_germ_theorem": {
            "statement": (
                "every good moved-slot channel has an offset-one representative "
                "whose tagged edge-to-fusion germ uses at most the reported maximum "
                "additional rank-preserving d occurrences"
            ),
            "good_channels_checked": good_channels,
            "maximum_r_min_Land_1": max(r_profile),
            "formula_K_verified": formula_k_verified == len(contexts),
            "proof_boundary": (
                "complete fixed-carrier germ theorem; the modular fusion-equation "
                "derivation remains open"
            ),
        },
        "contexts": contexts,
        "source_closure": [
            {
                "path": str(Path(__file__).resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(Path(__file__)),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("analyze_n7_extremal_moved_slot_menu.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(
                    Path(__file__).with_name(
                        "analyze_n7_extremal_moved_slot_menu.py"
                    )
                ),
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
            "r_min_all_profile": payload["r_min_all_profile"],
            "r_min_Land_1_profile": payload["r_min_Land_1_profile"],
            "theorem": payload["shallow_germ_theorem"],
            "contexts": payload["contexts"],
        }
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("moved_slot_artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.moved_slot_artifact)
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
                "r_min_all_profile": payload["r_min_all_profile"],
                "r_min_Land_1_profile": payload["r_min_Land_1_profile"],
                "theorem": payload["shallow_germ_theorem"],
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
