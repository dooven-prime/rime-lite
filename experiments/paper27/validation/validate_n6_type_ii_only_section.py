#!/usr/bin/env python3
"""Validate the four fixed-n=6 Type-II-only Entry-section endpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "experiments" / "paper27"
sys.path.insert(0, str(MODULE))

from analyze_n6_low_rank_obstruction_peeling import _digest
from analyze_n6_type_ii_only_section import (
    BALANCED_MECHANISM,
    OUTPUT_SCHEMA,
    UNBALANCED_MECHANISM,
)
from single_defect_low_rank_base import build_low_rank_base

N = 6
CYCLE = tuple((index + 1) % N for index in range(N))

EXPECTED_COUNTS = {
    "mechanism:BALANCED_12_THEN_32_REPAYMENT": 2,
    "mechanism:UNBALANCED_11_THEN_32_REPAYMENT": 2,
    "source_partition:(2, 2, 1, 1)": 2,
    "source_partition:(3, 1, 1, 1)": 2,
    "symbolic_receipt_differs_from_parent_best": 1,
    "type_ii_only_section_endpoints": 4,
}

EXPECTED_ROWS = {
    (
        "014320",
        (2, 0, 1, 1, 2, 0),
        BALANCED_MECHANISM,
        (0, 1, 0, 1, 0, 0, 1),
        2,
        7,
        -3,
        (0, 1, 0, 0, 0, 0, 1),
        6,
        7,
        3,
        (5, 1, 0, 0, 0, 0),
    ),
    (
        "032140",
        (2, 1, 2, 0, 1, 0),
        BALANCED_MECHANISM,
        (1, 0, 0, 0, 1),
        2,
        5,
        -1,
        (0, 1, 0, 0, 0, 1),
        6,
        6,
        4,
        (5, 0, 0, 1, 0, 0),
    ),
    (
        "102503",
        (3, 1, 1, 0, 0, 1),
        UNBALANCED_MECHANISM,
        (0, 0, 0, 0, 0, 1),
        1,
        6,
        -4,
        (0, 1),
        6,
        2,
        8,
        (5, 0, 1, 0, 0, 0),
    ),
    (
        "403205",
        (3, 0, 1, 0, 1, 1),
        UNBALANCED_MECHANISM,
        (0, 0, 1),
        1,
        3,
        -1,
        (0, 1),
        6,
        2,
        8,
        (5, 0, 0, 0, 0, 1),
    ),
}


def _input_path(payload: dict, suffix: str) -> Path:
    matches = [relative for relative in payload["inputs"] if relative.endswith(suffix)]
    if len(matches) != 1:
        raise AssertionError(f"expected one input ending in {suffix}")
    return ROOT / matches[0]


def validate(path: Path) -> dict[str, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != OUTPUT_SCHEMA:
        raise AssertionError("unexpected Type-II-only section schema")
    content = dict(payload)
    recorded = content.pop("content_sha256")
    if _digest(content) != recorded:
        raise AssertionError("Type-II-only section content digest mismatch")
    for section in ("inputs", "sources"):
        for relative, expected in payload[section].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise AssertionError(
                    f"Type-II-only section {section} drift: {relative}"
                )
    if any("route_f" in relative.lower() for relative in payload["inputs"]):
        raise AssertionError("canonical Type-II section still imports Route F")
    if any("route_f" in relative.lower() for relative in payload["sources"]):
        raise AssertionError("canonical Type-II producer still depends on Route F")
    if payload["counts"] != EXPECTED_COUNTS:
        raise AssertionError("Type-II-only section counts drift")

    entry_path = _input_path(
        payload,
        "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
    )
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    choices = {
        action["defect"]: action["entry_choice_audit"]["section_choice"]
        for action in entry["synchronizing_action_rows"]
        if not int(
            action["entry_choice_audit"]["section_choice"][
                "local_type_i_descent_count"
            ]
        )
    }
    if len(choices) != 4:
        raise AssertionError("Entry input lost its four Type-II-only choices")

    actual_rows = set()
    for row in payload["rows"]:
        choice = choices[row["defect"]]
        if row["source"] != choice["checkpoint"]:
            raise AssertionError("Type-II-only source differs from Entry section")
        if row["entry_activation_basis_sha256"] != _digest(
            choice["activated_basis"]
        ):
            raise AssertionError("Type-II-only activation basis drift")
        if row["receipt_selection"] != "MINIMUM_SECTION_LOCAL_COMMON_MECHANISM":
            raise AssertionError("Type-II receipt was not selected section-locally")
        if "route_f_form" in row:
            raise AssertionError("canonical Type-II row retained Route-F provenance")
        first = row["first_corridor"]
        second = row["second_corridor"]
        actual_rows.add(
            (
                row["defect"],
                tuple(int(value) for value in row["source"]),
                row["mechanism"],
                tuple(int(value) for value in first["word"]),
                int(first["delta_m_d"]),
                int(first["length"]),
                int(first["surplus"]),
                tuple(int(value) for value in second["word"]),
                int(second["delta_m_d"]),
                int(second["length"]),
                int(second["surplus"]),
                tuple(int(value) for value in second["target"]),
            )
        )
        if int(first["q_d"]) != 1 or int(second["q_d"]) != 1:
            raise AssertionError("Type-II-only receipt is not two unit drops")
        if int(first["surplus"]) >= 0:
            raise AssertionError("Type-II-only first corridor lost its debt")
        if int(second["surplus"]) < int(row["debt_required"]):
            raise AssertionError("Type-II-only second corridor lost repayment")
        if int(row["combined_surplus"]) != (
            int(first["surplus"]) + int(second["surplus"])
        ):
            raise AssertionError("Type-II combined surplus drift")

        defect = tuple(int(value) for value in row["defect"])
        base = build_low_rank_base((CYCLE, defect), N)
        base_labels = {
            tuple(int(value) for value in base_row["mass"]): bool(
                base_row["in_low_rank_base"]
            )
            for base_row in base["rows"]
        }
        if not base_labels.get(tuple(int(value) for value in second["target"])):
            raise AssertionError("Type-II-only target left exact P_<=3")
    if actual_rows != EXPECTED_ROWS:
        raise AssertionError("Type-II-only symbolic row closure drift")

    theorem = payload["theorem_boundary"]
    if theorem["type_i_section_endpoints"] != 1700:
        raise AssertionError("Type-I section count drift")
    if theorem["type_ii_only_section_endpoints"] != 4:
        raise AssertionError("Type-II-only section count drift")
    if not theorem["fixed_n6_section_image_is_type_i_or_two_type_ii_mechanisms"]:
        raise AssertionError("fixed-n=6 two-mechanism theorem lost")
    return payload["counts"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    path = args.path or (
        MODULE / "results" / "single_defect_n6_type_ii_only_section_v1.json"
    )
    counts = validate(path)
    print("PASS fixed-n=6 Type-II-only Entry section")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
