#!/usr/bin/env python3
"""Project the n=7 non-direct moved-slot channels to typed mod-7 equations."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_n7_extremal_colored_obstructions import CHANNEL_C4
from analyze_n7_extremal_direct_complement import (
    SCHEMA as COMPLEMENT_SCHEMA,
)
from analyze_n7_extremal_direct_complement import (
    _event_geometry,
)
from analyze_n7_extremal_edge_germs import (
    SCHEMA as GERM_SCHEMA,
)
from analyze_n7_extremal_edge_germs import (
    _representative_germs,
)
from analyze_n7_extremal_moved_slot_menu import _landing_offset
from section_return_core import digest_payload

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_FAILURE_EQUATIONS_V1"
N = 7


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply_coordinate(
    coordinate: int,
    word: list[int],
    defect: tuple[int, ...],
) -> int:
    for letter in word:
        coordinate = (coordinate + 1) % N if letter == 0 else defect[coordinate]
    return coordinate


def _slot_coordinates(context: dict[str, Any]) -> dict[int, int]:
    return {
        int(slot): int(coordinate)
        for slot, coordinate in context["slot_coordinates"].items()
    }


def _equation_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["corridor"],
        row["depth"],
        row["return_rotation_exponent"],
        tuple(row["active_triple"]),
        row["active_difference_mod_7"],
        row["terminal_rotation_exponent"],
        row["singleton_at_terminal_input"],
        row["singleton_after_terminal_d"],
        row["landing_equation"]["kind"],
        row["landing_equation"]["final_singleton_offset"],
    )


def _typed_equation(
    context: dict[str, Any],
    representative: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    geometry = _event_geometry(context, representative, event)
    depth = int(geometry["rank_preserving_d_after"])
    if depth not in {0, 1}:
        raise AssertionError("typed equation only accepts direct/one-return germs")

    if depth == 0:
        active = (
            int(geometry["x_F_after_tagged_d"]),
            int(geometry["y_incoming_after_tagged_d"]),
            int(geometry["singleton_after_tagged_d"]),
        )
        return_rotation = None
    else:
        returned = geometry.get("one_return")
        if returned is None:
            raise AssertionError("one-return geometry missing")
        active = (
            int(returned["F4_after_return"]),
            int(returned["incoming_after_return"]),
            int(returned["singleton_after_return"]),
        )
        return_rotation = int(returned["rotation_before_return"])

    difference = (active[1] - active[0]) % N
    terminal_rotation = int(geometry["terminal_rotation_exponent"])
    terminal_pair = sorted(
        ((active[0] + terminal_rotation) % N, (active[1] + terminal_rotation) % N)
    )
    if difference not in {1, 6} or terminal_pair != [0, 6]:
        raise AssertionError("typed germ lost its terminal adjacency equation")
    singleton_input = (active[2] + terminal_rotation) % N
    singleton_after_terminal = defect[singleton_input]
    edge = representative["edge"]
    target_offset = _landing_offset(representative)
    if event["corridor"] == 1:
        final_offset = _apply_coordinate(
            singleton_after_terminal,
            edge["second_word"],
            defect,
        )
        landing_equation = {
            "kind": "FIRST_CORRIDOR_CONTINUATION",
            "rank3_singleton_coordinate": singleton_after_terminal,
            "second_corridor_singleton_image": final_offset,
            "final_singleton_offset": final_offset,
            "satisfies_offset_one": final_offset == 1,
        }
    elif event["corridor"] == 2:
        final_offset = singleton_after_terminal
        landing_equation = {
            "kind": "SECOND_CORRIDOR_LOCAL",
            "local_terminal_d_image": final_offset,
            "final_singleton_offset": final_offset,
            "satisfies_offset_one": final_offset == 1,
        }
    else:
        raise AssertionError("unexpected corridor index")
    if final_offset != target_offset:
        raise AssertionError("typed singleton equation does not replay the target")

    return {
        "corridor": int(event["corridor"]),
        "depth": depth,
        "j": int(event["j"]),
        "directed_low_edge": [
            int(event["j"]),
            int(event["alpha_image"]),
        ],
        "return_rotation_exponent": return_rotation,
        "after_tagged_d": [
            int(geometry["x_F_after_tagged_d"]),
            int(geometry["y_incoming_after_tagged_d"]),
            int(geometry["singleton_after_tagged_d"]),
        ],
        "active_triple": list(active),
        "active_difference_mod_7": difference,
        "cyclically_adjacent": True,
        "terminal_rotation_exponent": terminal_rotation,
        "terminal_pair": terminal_pair,
        "singleton_at_terminal_input": singleton_input,
        "singleton_after_terminal_d": singleton_after_terminal,
        "landing_equation": landing_equation,
    }


def _channel_equations(
    source: dict[str, Any],
    representatives: list[dict[str, Any]],
    slot_coordinates: dict[int, int],
    slot: int,
) -> dict[int, list[dict[str, Any]]]:
    equations: dict[int, dict[tuple[Any, ...], dict[str, Any]]] = {0: {}, 1: {}}
    for representative in representatives:
        events = _representative_germs(
            source, representative, slot_coordinates
        ).get(slot, [])
        for event in events:
            depth = int(event["rank_preserving_d_after"])
            if depth not in equations:
                continue
            row = _typed_equation(source, representative, event)
            equations[depth][_equation_signature(row)] = row
    return {
        depth: [rows[key] for key in sorted(rows)]
        for depth, rows in equations.items()
    }


def _mechanism(
    equations: dict[int, list[dict[str, Any]]],
    *,
    long_kind: str | None,
) -> str:
    if any(
        row["landing_equation"]["satisfies_offset_one"]
        for row in equations[0]
    ):
        return "DIRECT"
    if any(
        row["landing_equation"]["satisfies_offset_one"]
        for row in equations[1]
    ):
        return "ONE_RETURN"
    if long_kind is not None:
        return long_kind
    return "BAD_DIRECTION"


def _failure_system(equations: dict[int, list[dict[str, Any]]]) -> list[str]:
    failures = []
    if equations[0]:
        if any(
            row["landing_equation"]["satisfies_offset_one"]
            for row in equations[0]
        ):
            raise AssertionError("complement row retained a direct landing")
        failures.append("WRONG_DIRECT_LANDING")
    else:
        failures.append("NO_DIRECT_GERM")
    if equations[1]:
        if any(
            row["landing_equation"]["satisfies_offset_one"]
            for row in equations[1]
        ):
            failures.append("ONE_RETURN_LANDING_EXISTS")
        else:
            failures.append("WRONG_ONE_RETURN_LANDING")
    else:
        failures.append("NO_ONE_RETURN_GERM")
    return failures


def build_payload(complement_path: Path) -> dict[str, Any]:
    complement_payload = json.loads(complement_path.read_text(encoding="utf-8", newline="\n"))
    if complement_payload.get("schema") != COMPLEMENT_SCHEMA:
        raise AssertionError("unexpected direct-complement schema")
    germ_path = ROOT / complement_payload["inputs"][0]["path"]
    germ_payload = json.loads(germ_path.read_text(encoding="utf-8", newline="\n"))
    if germ_payload.get("schema") != GERM_SCHEMA:
        raise AssertionError("unexpected edge-germ schema")
    menu_path = ROOT / germ_payload["inputs"][0]["path"]
    menu_payload = json.loads(menu_path.read_text(encoding="utf-8", newline="\n"))
    channel_path = ROOT / germ_payload["inputs"][1]["path"]
    channel_payload = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))

    menu_by_defect = {row["defect"]: row for row in menu_payload["contexts"]}
    source_by_defect = {row["defect"]: row for row in channel_payload["contexts"]}
    complement_by_identity = {
        (row["defect"], int(row["j"])): row
        for row in complement_payload["complement"]
    }

    equation_cache: dict[tuple[str, int], dict[int, list[dict[str, Any]]]] = {}

    def equations_for(defect: str, slot: int) -> dict[int, list[dict[str, Any]]]:
        identity = (defect, slot)
        if identity not in equation_cache:
            source = source_by_defect[defect]
            representatives = source["channel_relations"][CHANNEL_C4]
            equation_cache[identity] = _channel_equations(
                source,
                representatives,
                _slot_coordinates(menu_by_defect[defect]),
                slot,
            )
        return equation_cache[identity]

    complement_rows = []
    failure_profile: Counter[str] = Counter()
    typed_profile: Counter[str] = Counter()
    for identity, old_row in sorted(complement_by_identity.items()):
        defect, slot = identity
        equations = equations_for(defect, slot)
        failures = _failure_system(equations)
        failure_profile.update(failures)
        for depth, rows in equations.items():
            for row in rows:
                typed_profile[
                    f"R{depth}_CORRIDOR_{row['corridor']}"
                ] += 1
        complement_rows.append(
            {
                "defect": defect,
                "h": old_row["h"],
                "alpha": old_row["alpha"],
                "alpha_cycle_type": old_row["alpha_cycle_type"],
                "beta": old_row["beta"],
                "j": slot,
                "directed_low_edge": old_row["directed_low_edge"],
                "observed_mechanism": old_row["kind"],
                "failure_system": failures,
                "D": equations[0],
                "R": equations[1],
            }
        )

    reversal_rows = []
    for row in complement_rows:
        if row["observed_mechanism"] != "BAD_DIRECTION":
            continue
        alpha = [int(value) for value in row["alpha"]]
        reverse_slot = int(row["directed_low_edge"][1])
        if alpha[reverse_slot - 1] != row["j"]:
            raise AssertionError("bad channel is not a transposition direction")
        reverse_equations = equations_for(row["defect"], reverse_slot)
        reverse_complement = complement_by_identity.get(
            (row["defect"], reverse_slot)
        )
        long_kind = None
        if (
            reverse_complement is not None
            and reverse_complement["kind"] == "ORBIT_CLOSURE"
        ):
            long_kind = reverse_complement["kind"]
        reverse_mechanism = _mechanism(
            reverse_equations,
            long_kind=long_kind,
        )
        if reverse_mechanism == "BAD_DIRECTION":
            raise AssertionError("transposition retained two bad directions")
        reversal_rows.append(
            {
                "defect": row["defect"],
                "h": row["h"],
                "alpha": row["alpha"],
                "beta": row["beta"],
                "bad_edge": row["directed_low_edge"],
                "bad_failure_system": row["failure_system"],
                "reverse_edge": [reverse_slot, row["j"]],
                "reverse_mechanism": reverse_mechanism,
                "reverse_D_offset_one_equations": [
                    equation
                    for equation in reverse_equations[0]
                    if equation["landing_equation"]["satisfies_offset_one"]
                ],
                "reverse_R_offset_one_equations": [
                    equation
                    for equation in reverse_equations[1]
                    if equation["landing_equation"]["satisfies_offset_one"]
                ],
            }
        )

    transposition_failure_loci = []
    for alpha in ([1, 3, 2], [2, 1, 3], [3, 2, 1]):
        contexts = [
            row
            for row in menu_payload["contexts"]
            if row["alpha"] == alpha
        ]
        moved_slots = sorted(
            slot for slot, image in enumerate(alpha, start=1) if slot != image
        )
        if len(contexts) != 6 or len(moved_slots) != 2:
            raise AssertionError("transposition carrier parameterization drift")
        bad_by_slot: dict[int, list[dict[str, Any]]] = {}
        for slot in moved_slots:
            bad_parameters = []
            for context in contexts:
                equations = equations_for(context["defect"], slot)
                old = complement_by_identity.get((context["defect"], slot))
                long_kind = (
                    old["kind"]
                    if old is not None
                    and old["kind"]
                    == "ORBIT_CLOSURE"
                    else None
                )
                if _mechanism(equations, long_kind=long_kind) == "BAD_DIRECTION":
                    bad_parameters.append(
                        {"h": int(context["h"]), "beta": context["beta"]}
                    )
            bad_by_slot[slot] = sorted(
                bad_parameters,
                key=lambda row: (row["h"], row["beta"]),
            )
        left_locus = {
            (row["h"], row["beta"]) for row in bad_by_slot[moved_slots[0]]
        }
        right_locus = {
            (row["h"], row["beta"]) for row in bad_by_slot[moved_slots[1]]
        }
        intersection = sorted(left_locus & right_locus)
        if intersection:
            raise AssertionError("transposition directions can still be jointly bad")
        if not left_locus:
            contradiction = f"slot {moved_slots[0]} has empty bad locus"
        elif not right_locus:
            contradiction = f"slot {moved_slots[1]} has empty bad locus"
        else:
            contradiction = (
                "the two bad loci require incompatible (h,beta) parameters"
            )
        transposition_failure_loci.append(
            {
                "alpha": alpha,
                "moved_slots": moved_slots,
                "bad_parameters_by_slot": {
                    str(slot): bad_by_slot[slot] for slot in moved_slots
                },
                "simultaneous_bad_parameters": [
                    {"h": h, "beta": beta} for h, beta in intersection
                ],
                "contradiction": contradiction,
            }
        )

    cycle_rows = []
    cycle_mechanism_profile: Counter[str] = Counter()
    for menu_context in menu_payload["contexts"]:
        if menu_context["alpha_cycle_type"] != "THREE_CYCLE":
            continue
        mechanisms = []
        for slot in menu_context["moved_slots"]:
            equations = equations_for(menu_context["defect"], int(slot))
            old = complement_by_identity.get(
                (menu_context["defect"], int(slot))
            )
            long_kind = (
                old["kind"]
                if old is not None
                and old["kind"] == "ORBIT_CLOSURE"
                else None
            )
            mechanism = _mechanism(equations, long_kind=long_kind)
            if mechanism == "BAD_DIRECTION":
                raise AssertionError("3-cycle retained a bad direction")
            cycle_mechanism_profile[mechanism] += 1
            mechanisms.append(
                {
                    "j": int(slot),
                    "directed_low_edge": [
                        int(slot),
                        int(menu_context["alpha"][int(slot) - 1]),
                    ],
                    "mechanism": mechanism,
                }
            )
        cycle_rows.append(
            {
                "defect": menu_context["defect"],
                "h": menu_context["h"],
                "alpha": menu_context["alpha"],
                "beta": menu_context["beta"],
                "directions": mechanisms,
            }
        )

    if len(complement_rows) != 11 or len(reversal_rows) != 5:
        raise AssertionError("failure-equation scope drift")
    if len(cycle_rows) != 12:
        raise AssertionError("3-cycle context scope drift")
    if cycle_mechanism_profile != {
        "DIRECT": 35,
        "ORBIT_CLOSURE": 1,
    }:
        raise AssertionError(
            f"3-cycle mechanism profile drift: {dict(cycle_mechanism_profile)}"
        )
    observed_complement = Counter(
        row["observed_mechanism"] for row in complement_rows
    )
    expected_complement = {
        "BAD_DIRECTION": 5,
        "ONE_RETURN": 5,
        "ORBIT_CLOSURE": 1,
    }
    if dict(observed_complement) != expected_complement:
        raise AssertionError("11-channel mechanism profile drift")

    payload = {
        "schema": SCHEMA,
        "n": N,
        "inputs": [
            {
                "path": str(complement_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(complement_path),
                "schema": complement_payload["schema"],
                "projection_digest": complement_payload["projection_digest"],
            },
            {
                "path": str(channel_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(channel_path),
                "schema": channel_payload["schema"],
                "projection_digest": channel_payload["projection_digest"],
            },
        ],
        "scope": {
            "domain": "the 14-channel complement of direct offset-one landing",
            "equation_boundary": (
                "D and R retain only typed mod-7 coordinate equations for germ "
                "depth zero or one; no complete representative word is serialized"
            ),
            "corridor_boundary": (
                "a second-corridor equation checks d(s+a)=1 locally; a first-"
                "corridor equation retains the rank-3 singleton and checks its "
                "image under the complete second corridor"
            ),
            "forbidden_inputs": [
                "P_2/P_3 membership",
                "completion success labels",
                "W^(2C)",
                "reset coaccessibility",
                "Bellman policy",
            ],
        },
        "counts": {
            "complement_channels": len(complement_rows),
            "failure_profile": dict(sorted(failure_profile.items())),
            "typed_equation_profile": dict(sorted(typed_profile.items())),
            "transposition_reversals": len(reversal_rows),
            "three_cycle_contexts": len(cycle_rows),
            "three_cycle_directions": sum(
                len(row["directions"]) for row in cycle_rows
            ),
            "three_cycle_mechanism_profile": dict(
                sorted(cycle_mechanism_profile.items())
            ),
        },
        "complement": complement_rows,
        "transposition_reversal": reversal_rows,
        "transposition_failure_loci": transposition_failure_loci,
        "three_cycle": cycle_rows,
        "claims": [
            "Direct-germ existence and final offset-one landing are separate typed conditions.",
            "All six bad transposition directions have a good reverse direction in D, R, or the Root-Shift Exchange stratum.",
            "Every moved direction in each of the twelve nontrivial three-cycle contexts is good.",
        ],
        "source_closure": [
            {
                "path": str(Path(__file__).resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(Path(__file__)),
            },
            {
                "path": str(
                    Path(__file__)
                    .with_name("analyze_n7_extremal_direct_complement.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(
                    Path(__file__).with_name(
                        "analyze_n7_extremal_direct_complement.py"
                    )
                ),
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
                    .with_name("section_return_core.py")
                    .resolve()
                    .relative_to(ROOT).as_posix()
                ),
                "sha256": _sha256(
                    Path(__file__).with_name("section_return_core.py")
                ),
            },
        ],
    }
    payload["projection_digest"] = digest_payload(
        {
            "counts": payload["counts"],
            "complement": payload["complement"],
            "transposition_reversal": payload["transposition_reversal"],
            "transposition_failure_loci": payload[
                "transposition_failure_loci"
            ],
            "three_cycle": payload["three_cycle"],
        }
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direct_complement_artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.direct_complement_artifact)
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
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
