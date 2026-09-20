#!/usr/bin/env python3
"""Validate the fixed-n=6 selected Entry-section image decomposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "experiments" / "paper27"
sys.path.insert(0, str(MODULE))

from analyze_n6_entry_section_image import (
    EXPECTED_RESIDUAL_FORMS,
    OUTPUT_SCHEMA,
    RESIDUAL_TYPE_II,
)
from analyze_n6_low_rank_obstruction_peeling import _digest

EXPECTED_COUNTS = {
    "balanced_section_endpoints": 995,
    "balanced_type_ii_only": 2,
    "balanced_with_type_i": 993,
    "easy_unbalanced_type_i": 707,
    "residual_action_types": 2,
    "residual_intrinsic_source_forms": 2,
    "residual_unbalanced_type_ii": 2,
    "selected_section_actions": 1704,
    "selected_section_type_ii_only": 4,
    "selected_section_with_type_i": 1700,
    "stratum:BALANCED_LEMMA_A": 995,
    "stratum:EASY_UNBALANCED_TYPE_I_G4_CLOSED_TRIANGLE": 161,
    "stratum:EASY_UNBALANCED_TYPE_I_G4_OPEN_WEDGE": 430,
    "stratum:EASY_UNBALANCED_TYPE_I_OUTSIDE_G4": 116,
    "stratum:RESIDUAL_UNBALANCED_TYPE_II": 2,
    "unbalanced_section_endpoints": 709,
}

EXPECTED_RESIDUALS = {
    ("102503", (3, 1, 1, 0, 0, 1), "d102503__H0_x5_y2_z1"),
    ("403205", (3, 0, 1, 0, 1, 1), "d403205__H0_x2_y5_z4"),
}


def _input_path(payload: dict, suffix: str) -> Path:
    matches = [relative for relative in payload["inputs"] if relative.endswith(suffix)]
    if len(matches) != 1:
        raise AssertionError(f"expected one input ending in {suffix}")
    return ROOT / matches[0]


def validate(path: Path) -> dict[str, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != OUTPUT_SCHEMA:
        raise AssertionError("unexpected Entry-section image schema")
    content = dict(payload)
    recorded = content.pop("content_sha256")
    if _digest(content) != recorded:
        raise AssertionError("Entry-section image content digest mismatch")
    for section in ("inputs", "sources"):
        for relative, expected in payload[section].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise AssertionError(f"Entry-section image {section} drift: {relative}")
    if payload["counts"] != EXPECTED_COUNTS:
        raise AssertionError("Entry-section image counts drift")

    rows = payload["selected_section_rows"]
    if len(rows) != 1704 or len({row["defect"] for row in rows}) != 1704:
        raise AssertionError("selected Entry-section action closure drift")
    strata = Counter(row["stratum"] for row in rows)
    expected_strata = {
        key.removeprefix("stratum:"): value
        for key, value in EXPECTED_COUNTS.items()
        if key.startswith("stratum:")
    }
    if strata != Counter(expected_strata):
        raise AssertionError("selected Entry-section stratum closure drift")

    entry_path = _input_path(
        payload,
        "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
    )
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    choices = {
        action["defect"]: action["entry_choice_audit"]["section_choice"]
        for action in entry["synchronizing_action_rows"]
    }
    for row in rows:
        choice = choices[row["defect"]]
        if row["checkpoint"] != choice["checkpoint"]:
            raise AssertionError("section-image checkpoint differs from sigma_6")
        if row["entry_edge"] != choice["entry_edge"]:
            raise AssertionError("section-image entry edge differs from sigma_6")
        if row["activated_basis_sha256"] != _digest(choice["activated_basis"]):
            raise AssertionError("section-image activation basis drift")
        if row["local_type_i_descent_count"]:
            if row["local_descent_receipt"]["type"] != "I":
                raise AssertionError("easy stratum lost its Type-I receipt")
        elif row["local_descent_receipt"]["type"] != "II":
            raise AssertionError("residual stratum lost its Type-II receipt")

    residuals = payload["residual_rows"]
    actual_residuals = {
        (
            row["defect"],
            tuple(int(value) for value in row["checkpoint"]),
            row["intrinsic_source_form"],
        )
        for row in residuals
    }
    if actual_residuals != EXPECTED_RESIDUALS:
        raise AssertionError("selected Entry residual identity drift")
    if {row["intrinsic_source_form"] for row in residuals} != EXPECTED_RESIDUAL_FORMS:
        raise AssertionError("selected residual source-form closure drift")
    for row in residuals:
        if row["stratum"] != RESIDUAL_TYPE_II:
            raise AssertionError("residual row has the wrong stratum")
        if row["local_type_i_descent_count"] != 0:
            raise AssertionError("residual row unexpectedly has Type-I descent")
        if row["local_type_ii_descent_count"] <= 0:
            raise AssertionError("residual row lost Type-II descent")

    theorem = payload["theorem_boundary"]
    if not theorem["fixed_n6_section_image_decomposition_holds"]:
        raise AssertionError("fixed-n=6 section image theorem lost")
    return payload["counts"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    path = args.path or (
        MODULE / "results" / "single_defect_n6_entry_section_image_v1.json"
    )
    counts = validate(path)
    print("PASS fixed-n=6 Entry-section image decomposition")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
