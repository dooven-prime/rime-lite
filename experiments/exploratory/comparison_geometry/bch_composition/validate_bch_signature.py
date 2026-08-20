#!/usr/bin/env python3
"""Validate and independently inspect the Heisenberg BCH control bundle."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

from bch_signature import validate_control_bundle


def validate(path: Path) -> None:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    validate_control_bundle(bundle)

    xy = bundle["signatures"]["XY"]["homogeneous_coefficients"]
    yx = bundle["signatures"]["YX"]["homogeneous_coefficients"]
    assert Fraction(xy["1"]["X"]) == 1
    assert Fraction(xy["1"]["Y"]) == 1
    assert Fraction(yx["1"]["X"]) == 1
    assert Fraction(yx["1"]["Y"]) == 1
    assert Fraction(xy["2"]["Z"]) == Fraction(1, 2)
    assert Fraction(yx["2"]["Z"]) == Fraction(-1, 2)

    mismatch = bundle["comparisons"]["XY_vs_YX"]
    assert mismatch["bch_status"] == "CERTIFIED_MISMATCH"
    assert mismatch["lowest_differing_degree"] == 2
    assert mismatch["basis_label"] == "Z"
    assert mismatch["sofaudit_projection"]["comparison_state"] == "MISMATCH"

    exact = bundle["comparisons"]["XY_vs_copy"]
    assert exact["bch_status"] == "EXACT_MATCH"
    assert exact["sofaudit_projection"]["comparison_state"] == "ALIGNED"

    bounded = bundle["comparisons"]["degree_one_bounded_match"]
    assert bounded["bch_status"] == "TRUNCATED_MATCH"
    assert bounded["sofaudit_projection"]["comparison_state"] == "ALIGNED"
    assert bounded["sofaudit_projection"]["full_bch_comparison_state"] == (
        "UNRESOLVED"
    )

    full = bundle["comparisons"]["degree_one_full_bch"]
    assert full["bch_status"] == "UNRESOLVED"
    assert full["bounded_status"] == "TRUNCATED_MATCH"
    assert full["sofaudit_projection"]["comparison_state"] == "UNRESOLVED"

    assert bundle["comparisons"]["missing_capability"]["bch_status"] == (
        "NOT_DECLARED"
    )
    assert bundle["comparisons"]["missing_alignment"]["bch_status"] == (
        "INCOMPARABLE"
    )
    assert bundle["comparisons"]["unregistered_implementation"]["bch_status"] == (
        "INCOMPARABLE"
    )
    print(f"validated {bundle['bundle_id']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_bch_signature.py RESULT.json")
    validate(Path(sys.argv[1]))
