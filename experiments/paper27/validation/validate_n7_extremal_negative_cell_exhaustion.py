#!/usr/bin/env python3
"""Validate the five-cell n=7 negative relation projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
EXPERIMENT = HERE.parents[1]
ROOT = HERE.parents[3]
if str(EXPERIMENT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT))

from analyze_n7_extremal_negative_cell_exhaustion import (
    EXPECTED_SPECTRA,
    SCHEMA,
    _fusion_parent_roles,
    build_payload,
)
from section_return_core import CompleteExitOracle, digest_payload

EXPECTED_COUNTS = {
    "negative_cells": 5,
    "complete_C4_representatives": 129,
    "post_tag_states": 17,
    "kinematic_one_return_exponents": 40,
    "relation_observed_one_return_exponents": 8,
    "admitted_one_return_exponents": 8,
    "relation_completeness_gaps": 0,
    "kinematic_direct_candidates": 15,
    "admitted_direct_candidates": 14,
    "direct_relation_members": 24,
    "one_return_relation_members": 13,
    "typed_Gamma_states": 5,
    "Gamma_continuations": 17,
}

EXPECTED_ADMISSION_PROFILE = {
    "ACCOUNTING": 1,
    "ADMITTED": 8,
    "NORMALIZATION": 21,
    "NORMALIZATION_AND_ACCOUNTING": 10,
}
EXPECTED_DIRECT_PROFILE = {"ADMITTED": 14, "NORMALIZATION": 1}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_hashes(rows: list[dict[str, Any]], kind: str) -> None:
    for row in rows:
        path = ROOT / row["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise AssertionError(f"negative exhaustion {kind} drift: {row['path']}")


def _word(values: list[int]) -> str:
    return "".join(str(value) for value in values)


def _mass(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(value) for value in values)


def _role_state(rows: list[dict[str, Any]]) -> str:
    return ",".join(
        f"{row['coordinate']}:{'+'.join(row['roles'])}"
        for row in rows
    )


def _cell_label(cell: dict[str, Any]) -> str:
    alpha = "".join(str(value) for value in cell["alpha"])
    beta = "I" if cell["beta"] == "IDENTITY" else "S"
    return f"{alpha}/{cell['j']},({cell['h']},{beta})"


def _accounting_label(candidate: dict[str, Any]) -> str:
    accounting = candidate["accounting"]
    if "second_surplus" in accounting:
        first = int(accounting["first_surplus"])
        second = int(accounting["second_surplus"])
        total = int(accounting["total_surplus"])
        operator = "+" if second >= 0 else ""
        return f"{first}{operator}{second}={total}"
    return (
        f"S1={accounting['first_surplus']}; "
        f"{accounting['repaying_second_corridors']}/"
        f"{accounting['role_compatible_second_corridors']}"
    )


def _result_label(candidate: dict[str, Any]) -> str:
    if candidate["predicted_admitted"]:
        return "in Q"
    return {
        "NORMALIZATION": "N",
        "ACCOUNTING": "A",
        "NORMALIZATION_AND_ACCOUNTING": "N+A",
    }[candidate["rejection_basis"]]


def _check_paper_tables(payload: dict[str, Any], paper_path: Path) -> None:
    """Check that the theorem-facing finite tables match the bound artifact."""

    text = paper_path.read_text(encoding="utf-8")
    indexed_x: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    index = 0
    for cell in payload["cells"]:
        for x in cell["post_tag_states"]:
            index += 1
            indexed_x.append((index, cell, x))

    for index, cell, x in indexed_x:
        prefixes = sorted(
            _word(row["marked_prefix_word"])
            for row in x["prefix_provenances"]
        )
        accounting = x["accounting_state"]
        table_row = (
            f"| `X{index}` | `{_cell_label(cell)}` | "
            f"`{x['corridor']}/{x['incoming_role']}` | "
            f"`{{{','.join(prefixes)}}}` | {x['marked_prefix_length']} | "
            f"`{_role_state(x['post_tag_role_state'])}` | "
            f"`({accounting['surplus_entering_corridor']},"
            f"{accounting['marked_prefix_cost']},"
            f"{accounting['running_balance_after_tag']})` | "
            f"`{_role_state(x['corridor_source_role_state'])}` |"
        )
        if table_row not in text:
            raise AssertionError(f"paper Back-Solving row drift: X{index}")

        for candidate in x["one_return_gate_audit"]:
            table_row = (
                f"| `X{index}` | {x['corridor']} | "
                f"{candidate['return_rotation_exponent']} | "
                f"{candidate['terminal_rotation_exponent']} | "
                f"`{_mass(candidate['target_mass'])}` | "
                f"{candidate['candidate_corridor_length']}/"
                f"{candidate['endpoint_minimum_length']} | "
                f"`{_accounting_label(candidate)}` | "
                f"{'yes' if candidate['endpoint_normalized'] else 'no'} | "
                f"{'yes' if candidate['accounting_admissible'] else 'no'} | "
                f"`{_result_label(candidate)}` |"
            )
            if table_row not in text:
                raise AssertionError(
                    "paper one-return admission row drift: "
                    f"X{index},q={candidate['return_rotation_exponent']}"
                )

        direct = x["direct_gate_audit"]
        if direct is not None:
            result = "direct" if direct["predicted_admitted"] else "`N`"
            table_row = (
                f"| `X{index}` | {x['corridor']} | "
                f"{direct['terminal_rotation_exponent']} | "
                f"`{_mass(direct['target_mass'])}` | "
                f"{direct['candidate_corridor_length']}/"
                f"{direct['endpoint_minimum_length']} | "
                f"`{_accounting_label(direct)}` | "
                f"{'yes' if direct['endpoint_normalized'] else 'no'} | "
                f"{'yes' if direct['accounting_admissible'] else 'no'} | "
                f"{result} |"
            )
            if table_row not in text:
                raise AssertionError(f"paper direct admission row drift: X{index}")

    seen_y: set[str] = set()
    y_index = 0
    for cell in payload["cells"]:
        defect = tuple(int(value) for value in cell["source_geometry"]["defect_map"])
        cycle = tuple((coordinate + 1) % 7 for coordinate in range(7))
        exits = CompleteExitOracle((cycle, defect), 7)
        for gamma in cell["Gamma"]:
            if gamma["Y_id"] in seen_y:
                continue
            seen_y.add(gamma["Y_id"])
            y_index += 1
            typed_y = gamma["Y"]
            state = {
                int(row["coordinate"]): frozenset(str(role) for role in row["roles"])
                for row in typed_y["role_state"]
            }
            heavy = {packet for packet in state.values() if "s" not in packet}
            bound = int(typed_y["maximum_length_second_under_debt"])
            admitted: list[dict[str, Any]] = []
            over_debt: list[dict[str, Any]] = []
            wrong_pair = 0
            for exit_row in exits.exits(tuple(int(value) for value in typed_y["mass"])):
                parents = _fusion_parent_roles(
                    state,
                    [int(value) for value in exit_row["word"]],
                    defect,
                )
                if parents is None or set(parents) != heavy:
                    wrong_pair += 1
                elif int(exit_row["length"]) <= bound:
                    admitted.append(exit_row)
                else:
                    over_debt.append(exit_row)

            artifact_admitted = {
                (
                    tuple(int(value) for value in row["word"]),
                    int(row["length"]),
                    tuple(int(value) for value in row["target_mass"]),
                )
                for row in gamma["continuations"]
            }
            recomputed_admitted = {
                (
                    tuple(int(value) for value in row["word"]),
                    int(row["length"]),
                    tuple(int(value) for value in row["target"]),
                )
                for row in admitted
            }
            if artifact_admitted != recomputed_admitted:
                raise AssertionError(f"paper exit recomputation drift: Y{y_index}")

            paper_row = next(
                (
                    line
                    for line in text.splitlines()
                    if line.startswith(f"| `Y{y_index}` |")
                ),
                None,
            )
            if paper_row is None:
                raise AssertionError(f"paper Heavy-Pair Exit row absent: Y{y_index}")
            paper_admitted = {
                (word, int(length), target, int(landing), int(surplus))
                for word, length, target, landing, surplus in re.findall(
                    r"`([01]+) \[(\d+),(\d{7}),(\d),(-?\d+)\]`",
                    paper_row,
                )
            }
            expected_admitted = {
                (
                    _word(row["word"]),
                    int(row["length"]),
                    _mass(row["target_mass"]),
                    int(row["final_singleton_offset"]),
                    int(row["surplus"]),
                )
                for row in gamma["continuations"]
            }
            paper_over = {
                (word, int(length), target)
                for word, length, target in re.findall(
                    r"`([01]+) \[(\d+),(\d{7})\]`",
                    paper_row,
                )
            }
            expected_over = {
                (
                    _word(list(row["word"])),
                    int(row["length"]),
                    _mass(row["target"]),
                )
                for row in over_debt
            }
            split = (
                f"`{len(admitted) + len(over_debt) + wrong_pair}="
                f"{len(admitted)}+{len(over_debt)}+{wrong_pair}_wrong-pair`"
            )
            gamma_image = "{" + ",".join(
                str(value) for value in gamma["Gamma_image"]
            ) + "}"
            if (
                paper_admitted != expected_admitted
                or paper_over != expected_over
                or split not in paper_row
                or f"`{gamma_image}`" not in paper_row
            ):
                raise AssertionError(f"paper Heavy-Pair Exit row drift: Y{y_index}")


def _check_static(payload: dict[str, Any]) -> Path:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected negative-cell exhaustion schema")
    if payload["counts"] != EXPECTED_COUNTS:
        raise AssertionError("negative-cell exhaustion count drift")
    if payload["one_return_admission_profile"] != EXPECTED_ADMISSION_PROFILE:
        raise AssertionError("one-return admission profile drift")
    if payload["direct_admission_profile"] != EXPECTED_DIRECT_PROFILE:
        raise AssertionError("direct admission profile drift")
    _check_hashes(payload["inputs"], "input")
    _check_hashes(payload["source_closure"], "source")

    if len(payload["cells"]) != 5:
        raise AssertionError("negative-cell relation lost its five-cell scope")
    for cell in payload["cells"]:
        identity = (
            tuple(cell["alpha"]),
            int(cell["j"]),
            int(cell["h"]),
            str(cell["beta"]),
        )
        if identity not in EXPECTED_SPECTRA:
            raise AssertionError(f"unexpected negative cell: {identity}")
        expected_d, expected_r = EXPECTED_SPECTRA[identity]
        if set(cell["direct_landing_spectrum"]) != expected_d:
            raise AssertionError(f"direct spectrum drift: {identity}")
        if set(cell["one_return_landing_spectrum"]) != expected_r:
            raise AssertionError(f"return spectrum drift: {identity}")
        if 1 in expected_d or 1 in expected_r or cell["long_germ"] is not None:
            raise AssertionError(f"negative cell acquired a menu witness: {identity}")

        x_keys = {
            (
                int(row["corridor"]),
                str(row["incoming_role"]),
                int(row["marked_prefix_length"]),
                json.dumps(row["accounting_state"], sort_keys=True),
                json.dumps(row["corridor_source_role_state"], sort_keys=True),
                json.dumps(row["post_tag_role_state"], sort_keys=True),
            )
            for row in cell["post_tag_states"]
        }
        if len(x_keys) != len(cell["post_tag_states"]):
            raise AssertionError("typed post-tag state identity collision")
        if any(key[2] <= 0 for key in x_keys):
            raise AssertionError("post-tag state has a nonpositive prefix length")
        for row in cell["post_tag_states"]:
            kinematic = set(row["kinematic_one_return_rotations"])
            relation_observed = set(
                row["relation_observed_one_return_rotations"]
            )
            admitted = set(row["admissible_one_return_rotations"])
            if not admitted <= kinematic:
                raise AssertionError("admitted return is not kinematically valid")
            if relation_observed != admitted:
                raise AssertionError("complete relation and exact admission disagree")
            if not row["prefix_transport_is_gate_invariant"]:
                raise AssertionError("equivalent marked prefixes changed a gate")
            if not row["prefix_provenances"]:
                raise AssertionError("typed post-tag state lost prefix provenance")
            audit = row["one_return_gate_audit"]
            if {item["return_rotation_exponent"] for item in audit} != kinematic:
                raise AssertionError("one-return audit does not exhaust Q^kin")
            predicted = {
                item["return_rotation_exponent"]
                for item in audit
                if item["predicted_admitted"]
            }
            if predicted != admitted:
                raise AssertionError("one-return gate audit does not reconstruct Q")
            if any(not item["role_completion_exists"] for item in audit):
                raise AssertionError("one-return audit exposed a hidden role gate")
            for item in audit:
                expected = (
                    item["role_completion_exists"]
                    and item["endpoint_normalized"]
                    and item["accounting_admissible"]
                )
                if item["predicted_admitted"] != expected:
                    raise AssertionError("one-return admission is not exactly N and A")
                if item["relation_observed"] != (
                    item["return_rotation_exponent"] in relation_observed
                ):
                    raise AssertionError("relation-observed Q annotation drift")
                if item["relation_completeness_gap"]:
                    raise AssertionError("one-return relation completeness gap")
            direct = row["direct_gate_audit"]
            if direct is not None:
                expected = (
                    direct["role_completion_exists"]
                    and direct["endpoint_normalized"]
                    and direct["accounting_admissible"]
                )
                if direct["predicted_admitted"] != expected:
                    raise AssertionError("direct admission is not exactly N and A")
                if direct["relation_completeness_gap"]:
                    raise AssertionError("direct relation completeness gap")

        gamma_by_id = {row["Y_id"]: row for row in cell["Gamma"]}
        for gamma in gamma_by_id.values():
            image = {row["final_singleton_offset"] for row in gamma["continuations"]}
            if image != set(gamma["Gamma_image"]):
                raise AssertionError("Gamma image no longer matches its continuations")
            bound = gamma["Y"]["maximum_length_second_under_debt"]
            if any(row["length"] > bound for row in gamma["continuations"]):
                raise AssertionError(
                    "Gamma retained a continuation outside its debt bound"
                )

        for name, depth in (("D", 0), ("R", 1)):
            for member in cell[name]:
                member_x = (
                    int(member["corridor"]),
                    str(member["incoming_role"]),
                    int(member["marked_letter_index"]) + 1,
                    json.dumps(
                        {
                            "surplus_entering_corridor": (
                                0
                                if int(member["corridor"]) == 1
                                else int(member["association"]["surplus_first"])
                            ),
                            "marked_prefix_cost": int(member["marked_letter_index"])
                            + 1,
                            "running_balance_after_tag": (
                                0
                                if int(member["corridor"]) == 1
                                else int(member["association"]["surplus_first"])
                            )
                            - int(member["marked_letter_index"])
                            - 1,
                        },
                        sort_keys=True,
                    ),
                    json.dumps(member["post_tag_role_state"], sort_keys=True),
                )
                reduced_x_keys = {
                    key[:4] + key[5:]
                    for key in x_keys
                }
                if member_x not in reduced_x_keys:
                    raise AssertionError(
                        "relation member lost its typed post-tag state"
                    )
                if member["depth"] != depth:
                    raise AssertionError(
                        f"{name} relation acquired the wrong germ depth"
                    )
                if member["landing_equation"]["final_singleton_offset"] == 1:
                    raise AssertionError("negative relation acquired offset one")
                if member["corridor"] == 1:
                    gamma = gamma_by_id.get(member["Y_id"])
                    if gamma is None:
                        raise AssertionError(
                            "first-corridor member lost its typed Gamma state"
                        )
                    if member["Gamma_image"] != gamma["Gamma_image"]:
                        raise AssertionError("first-corridor Gamma image drift")
                    if member["rank3_singleton_coordinate"] != gamma["t"]:
                        raise AssertionError("first-corridor singleton handoff drift")
                elif "Y_id" in member:
                    raise AssertionError(
                        "second-corridor member retained a Gamma state"
                    )
    return ROOT / payload["inputs"][0]["path"]


def validate(
    path: Path,
    replay: bool = False,
    paper_path: Path | None = None,
) -> dict[str, Any]:
    payload = _load(path)
    failure_path = _check_static(payload)
    expected_digest = digest_payload(
        {
            "counts": payload["counts"],
            "one_return_admission_profile": payload[
                "one_return_admission_profile"
            ],
            "direct_admission_profile": payload["direct_admission_profile"],
            "cells": payload["cells"],
        }
    )
    if payload["projection_digest"] != expected_digest:
        raise AssertionError("negative-cell projection digest drift")
    if replay:
        rebuilt = build_payload(failure_path)
        if rebuilt["projection_digest"] != payload["projection_digest"]:
            raise AssertionError("negative-cell replay drift")
    if paper_path is not None:
        _check_paper_tables(payload, paper_path)
    return {
        "schema": payload["schema"],
        "counts": payload["counts"],
        "projection_digest": payload["projection_digest"],
        "paper_tables_checked": paper_path is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument(
        "--paper",
        type=Path,
        help="also check theorem-facing table transcription",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            validate(args.artifact, replay=args.replay, paper_path=args.paper),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
