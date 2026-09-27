#!/usr/bin/env python3
"""Recompute and validate the Paper XXVIII boundary-liftability audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from paper28_audit_boundary_liftability import (
    AUDIT_SCHEMA,
    DEFAULT_CATALOG,
    DEFAULT_OUTPUT,
    _read_catalog,
    build_audit,
    build_receipt,
    default_receipt_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--audit", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog_path = args.catalog.resolve()
    audit_path = args.audit.resolve()
    receipt_path = (
        args.receipt.resolve()
        if args.receipt
        else default_receipt_path(audit_path)
    )

    observed = json.loads(audit_path.read_text(encoding="ascii"))
    if observed.get("schema") != AUDIT_SCHEMA:
        raise AssertionError(f"unexpected audit schema: {observed.get('schema')!r}")
    expected = build_audit(_read_catalog(catalog_path), catalog_path=catalog_path)
    if observed != expected:
        raise AssertionError("boundary-liftability audit differs from full replay")

    observed_receipt = json.loads(receipt_path.read_text(encoding="ascii"))
    expected_receipt = build_receipt(
        audit_path,
        observed,
        catalog_path=catalog_path,
    )
    if observed_receipt != expected_receipt:
        raise AssertionError("audit receipt does not bind artifact/input/source closure")

    factorization = {
        row["quotient_level"]: row
        for row in observed["composition_failure_factorization"]
    }
    if factorization["accounting"]["noncongruent_fiber_count"] != 103:
        raise AssertionError("accounting hostile-fiber count changed")
    if factorization["skeleton"]["noncongruent_fiber_count"] != 9:
        raise AssertionError("skeleton hostile-fiber count changed")
    if factorization["accounting"]["minimal_uniform_boundary_level_counts"] != {
        "action": 15,
        "normalized_mass": 88,
    }:
        raise AssertionError("accounting boundary factorization changed")
    if factorization["skeleton"]["minimal_uniform_boundary_level_counts"] != {
        "action": 1,
        "normalized_mass": 8,
    }:
        raise AssertionError("skeleton boundary factorization changed")
    if not all(
        row["exact_boundary_factorization_holds"]
        for row in factorization.values()
    ):
        raise AssertionError("exact typed boundary failed to factor composition")

    exact_rows = [
        row
        for row in observed["context_boundary_liftability"]
        if row["boundary_level"] == "exact_typed_context"
    ]
    if not all(row["fiber_uniform_liftability"] for row in exact_rows):
        raise AssertionError("exact context quotient is not fiber-uniform")

    boundary_rows = {
        (row["quotient_level"], row["boundary_level"]): row
        for row in observed["context_boundary_liftability"]
    }
    for quotient_level in ("accounting", "skeleton"):
        normalized = boundary_rows[(quotient_level, "normalized_mass")]
        if normalized["boundary_fiber_count"] != 492:
            raise AssertionError("normalized-mass boundary fiber count changed")
        if normalized["nonuniform_fiber_count"] != 0:
            raise AssertionError(
                f"{quotient_level} successors do not lift uniformly from mass boundary"
            )
        if normalized["nonempty_mismatch_fiber_count"] != 0:
            raise AssertionError(
                f"{quotient_level} successor nonemptiness changed on mass boundary"
            )

    menu = observed["menu_realization_split"]["surface_summaries"]
    expected_maxima = {
        "N6_TYPE_II_ONLY_SECTION": (4, 10, 22),
        "N7_EXTREMAL_35_CARRIER": (8, 46, 380),
    }
    for surface, maxima in expected_maxima.items():
        row = menu[surface]
        actual = (
            row["max_skeleton_menu_size"],
            row["max_accounting_menu_size"],
            row["max_exact_receipt_count"],
        )
        if actual != maxima:
            raise AssertionError(f"menu/fiber maxima changed for {surface}: {actual}")

    print(
        "PASS: boundary factorization, context liftability, menu/fiber split, "
        "and provenance receipt all match full replay"
    )


if __name__ == "__main__":
    main()
