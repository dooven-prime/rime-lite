#!/usr/bin/env python3
"""Project the 14-channel complement of direct n=7 moved-slot landing."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_n7_extremal_colored_obstructions import CHANNEL_C4
from analyze_n7_extremal_edge_germs import (
    SCHEMA as GERM_SCHEMA,
)
from analyze_n7_extremal_edge_germs import (
    _representative_germs,
)
from analyze_n7_extremal_moved_slot_menu import (
    _landing_offset,
    _source_role_state,
)
from section_return_core import digest_payload

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_DIRECT_COMPLEMENT_V1"
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


def _apply_prefix(
    state: RoleState,
    word: list[int],
    defect: tuple[int, ...],
) -> RoleState:
    for letter in word:
        state = _apply(state, CYCLE if letter == 0 else defect)
    return state


def _role_coordinate(state: RoleState, role: str) -> int:
    return next(
        coordinate for coordinate, packet in state.items() if role in packet
    )


def _corridor_source(
    context: dict[str, Any], representative: dict[str, Any], corridor: int
) -> RoleState:
    source = _source_role_state(context)
    if corridor == 1:
        return source
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    return _apply_prefix(source, representative["edge"]["first_word"], defect)


def _event_geometry(
    context: dict[str, Any],
    representative: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    word = representative["edge"][
        "first_word" if event["corridor"] == 1 else "second_word"
    ]
    before = _apply_prefix(
        _corridor_source(context, representative, event["corridor"]),
        word[: event["letter_index"]],
        defect,
    )
    after_tagged = _apply(before, defect)
    x_f = _role_coordinate(after_tagged, "F4")
    y_incoming = _role_coordinate(after_tagged, event["incoming_role"])
    singleton = _role_coordinate(after_tagged, "s")
    difference = (y_incoming - x_f) % N
    suffix = word[event["letter_index"] + 1 :]
    terminal_shift = event["terminal_rotation_exponent"]
    before_terminal = _apply_prefix(after_tagged, suffix[:-1], defect)
    terminal_pair = sorted(
        (
            _role_coordinate(before_terminal, "F4"),
            _role_coordinate(before_terminal, event["incoming_role"]),
        )
    )
    if terminal_pair != [0, 6]:
        raise AssertionError("tagged germ did not reach the binary kernel")
    row = {
        "corridor": event["corridor"],
        "j": event["j"],
        "alpha_image": event["alpha_image"],
        "incoming_role": event["incoming_role"],
        "x_F_after_tagged_d": x_f,
        "y_incoming_after_tagged_d": y_incoming,
        "singleton_after_tagged_d": singleton,
        "oriented_difference_mod_7": difference,
        "cyclically_adjacent_after_tagged_d": difference in {1, 6},
        "rank_preserving_d_after": event["rank_preserving_d_after"],
        "terminal_rotation_exponent": terminal_shift,
        "terminal_pair": terminal_pair,
        "landing_offset": _landing_offset(representative),
    }
    if event["rank_preserving_d_after"] == 1:
        next_d_index = suffix.index(1)
        before_return = _apply_prefix(after_tagged, suffix[:next_d_index], defect)
        after_return = _apply(before_return, defect)
        row["one_return"] = {
            "rotation_before_return": next_d_index,
            "F4_after_return": _role_coordinate(after_return, "F4"),
            "incoming_after_return": _role_coordinate(
                after_return, event["incoming_role"]
            ),
            "singleton_after_return": _role_coordinate(after_return, "s"),
            "oriented_difference_mod_7": (
                _role_coordinate(after_return, event["incoming_role"])
                - _role_coordinate(after_return, "F4")
            )
            % N,
        }
    return row


def _signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["corridor"],
        row["j"],
        row["alpha_image"],
        row["incoming_role"],
        row["x_F_after_tagged_d"],
        row["y_incoming_after_tagged_d"],
        row["singleton_after_tagged_d"],
        row["oriented_difference_mod_7"],
        row["rank_preserving_d_after"],
        row["terminal_rotation_exponent"],
        row["landing_offset"],
    )


def _selected_event(
    context: dict[str, Any],
    channel: dict[str, Any],
    representatives: list[dict[str, Any]],
    slot_coordinates: dict[int, int],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    witness = channel["selected_shallow_Land_1_germ"]
    if witness is None:
        return None
    for representative in representatives:
        edge = representative["edge"]
        if (
            edge["first_word"] != witness["first_word"]
            or edge["second_word"] != witness["second_word"]
            or _landing_offset(representative) != 1
        ):
            continue
        germs = _representative_germs(context, representative, slot_coordinates)
        for event in germs.get(channel["j"], []):
            if all(
                event[key] == witness[key]
                for key in (
                    "corridor",
                    "incoming_role",
                    "letter_index",
                    "rank_preserving_d_after",
                )
            ):
                return representative, event
    raise AssertionError("selected edge germ could not be replayed")


def build_payload(germ_path: Path) -> dict[str, Any]:
    germ_payload = json.loads(germ_path.read_text(encoding="utf-8", newline="\n"))
    if germ_payload.get("schema") != GERM_SCHEMA:
        raise AssertionError("unexpected edge-germ schema")
    menu_path = ROOT / germ_payload["inputs"][0]["path"]
    menu_payload = json.loads(menu_path.read_text(encoding="utf-8", newline="\n"))
    channel_path = ROOT / germ_payload["inputs"][1]["path"]
    channel_payload = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))
    source_by_defect = {row["defect"]: row for row in channel_payload["contexts"]}
    germ_by_defect = {row["defect"]: row for row in germ_payload["contexts"]}

    direct_location_profile: Counter[str] = Counter()
    complement_profile: Counter[str] = Counter()
    direct_channels = 0
    complement = []
    for menu_context in menu_payload["contexts"]:
        source = source_by_defect[menu_context["defect"]]
        germ_context = germ_by_defect[menu_context["defect"]]
        slot_coordinates = {
            int(slot): int(coordinate)
            for slot, coordinate in menu_context["slot_coordinates"].items()
        }
        representatives = source["channel_relations"][CHANNEL_C4]
        for channel in germ_context["channels"]:
            direct_geometries = []
            direct_corridors = set()
            for representative in representatives:
                germs = _representative_germs(
                    source, representative, slot_coordinates
                ).get(channel["j"], [])
                for event in germs:
                    if event["rank_preserving_d_after"] != 0:
                        continue
                    geometry = _event_geometry(source, representative, event)
                    direct_geometries.append(geometry)
                    if geometry["landing_offset"] == 1:
                        direct_corridors.add(geometry["corridor"])
            if direct_corridors:
                direct_channels += 1
                if direct_corridors == {1}:
                    direct_location_profile["FIRST_ONLY"] += 1
                elif direct_corridors == {2}:
                    direct_location_profile["SECOND_ONLY"] += 1
                elif direct_corridors == {1, 2}:
                    direct_location_profile["BOTH"] += 1
                else:
                    raise AssertionError("unexpected direct-corridor locus")
                continue

            selected = _selected_event(
                source, channel, representatives, slot_coordinates
            )
            if selected is None:
                kind = "BAD_DIRECTION"
                selected_geometry = None
            elif channel["r_min_Land_1"] == 1:
                kind = "ONE_RETURN"
                selected_geometry = _event_geometry(source, *selected)
            elif (menu_context["defect"], channel["j"]) == ("0315420", 2):
                kind = "ORBIT_CLOSURE"
                selected_geometry = _event_geometry(source, *selected)
            elif (menu_context["defect"], channel["j"]) == ("0321540", 3):
                kind = "ROOT_SHIFT_EXCHANGE"
                selected_geometry = _event_geometry(source, *selected)
            else:
                raise AssertionError("unclassified non-direct moved-slot channel")
            complement_profile[kind] += 1
            unique_direct = {
                _signature(row): row for row in direct_geometries
            }
            complement.append(
                {
                    "defect": menu_context["defect"],
                    "h": menu_context["h"],
                    "alpha": menu_context["alpha"],
                    "alpha_cycle_type": menu_context["alpha_cycle_type"],
                    "beta": menu_context["beta"],
                    "j": channel["j"],
                    "directed_low_edge": channel["directed_low_edge"],
                    "kind": kind,
                    "direct_candidate_germs": [
                        unique_direct[key] for key in sorted(unique_direct)
                    ],
                    "direct_candidate_landing_offsets": sorted(
                        {row["landing_offset"] for row in direct_geometries}
                    ),
                    "selected_non_direct_germ": selected_geometry,
                }
            )

    expected_complement = {
        "BAD_DIRECTION": 5,
        "ONE_RETURN": 5,
        "ORBIT_CLOSURE": 1,
    }
    if direct_channels != 61 or dict(complement_profile) != expected_complement:
        raise AssertionError(
            "direct/complement decomposition drift: "
            f"direct={direct_channels}, complement={dict(complement_profile)}"
        )
    if direct_location_profile != {
        "FIRST_ONLY": 13,
        "SECOND_ONLY": 7,
        "BOTH": 41,
    }:
        raise AssertionError(
            f"direct corridor-location profile drift: {dict(direct_location_profile)}"
        )

    payload = {
        "schema": SCHEMA,
        "n": N,
        "inputs": [
            {
                "path": str(germ_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(germ_path),
                "schema": germ_payload["schema"],
                "projection_digest": germ_payload["projection_digest"],
            },
            {
                "path": str(channel_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(channel_path),
                "schema": channel_payload["schema"],
                "projection_digest": channel_payload["projection_digest"],
            },
        ],
        "scope": {
            "universe": "the 72 nonempty W_j channels",
            "direct_predicate": (
                "there exists a tagged W_j event with no additional "
                "rank-preserving d before its own terminal strict d and with "
                "final heavy-comb singleton offset one"
            ),
            "projection_boundary": (
                "only modular role coordinates and germ depths are retained; "
                "no complete representative record is serialized"
            ),
            "nonclaim": (
                "a first-corridor direct germ does not determine final landing "
                "without the second corridor"
            ),
        },
        "decomposition": {
            "channels": 72,
            "direct": direct_channels,
            "complement": len(complement),
            "direct_location_profile": dict(sorted(direct_location_profile.items())),
            "complement_profile": dict(sorted(complement_profile.items())),
        },
        "complement": complement,
        "claims": [
            "The exact channel relation splits as 72=61 direct+5 one-return+1 long+5 bad.",
            "The only irreducible long channel is the independently closed Orbit-Closure germ.",
            "Thirteen direct channels have offset-one direct germs only in the first corridor, so a universal one-terminal singleton equation is too strong.",
        ],
        "source_closure": [
            {
                "path": str(Path(__file__).resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(Path(__file__)),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("analyze_n7_extremal_edge_germs.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(
                    Path(__file__).with_name("analyze_n7_extremal_edge_germs.py")
                ),
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
            "decomposition": payload["decomposition"],
            "complement": payload["complement"],
        }
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("edge_germ_artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.edge_germ_artifact)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "decomposition": payload["decomposition"],
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
