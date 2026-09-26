#!/usr/bin/env python3
"""Recompute and validate the Paper XXVIII credit-composition audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from paper28_audit_credit_composition import (
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
        raise AssertionError("credit-composition audit differs from full replay")

    observed_receipt = json.loads(receipt_path.read_text(encoding="ascii"))
    expected_receipt = build_receipt(
        audit_path,
        observed,
        catalog_path=catalog_path,
    )
    if observed_receipt != expected_receipt:
        raise AssertionError("audit receipt does not bind artifact/input/source closure")

    receipt_theorem = observed["exact_receipt_credit_theorem"]
    if receipt_theorem["receipt_count"] != 11252:
        raise AssertionError("exact receipt count changed")
    if not all(
        receipt_theorem[field]
        for field in (
            "all_corridor_telescopes_hold",
            "all_receipt_telescopes_hold",
            "all_credit_allocations_hold",
        )
    ):
        raise AssertionError("an exact receipt credit identity failed")

    lift_theorem = observed["exact_lift_composition_theorem"]
    if lift_theorem["exact_compatible_lift_count"] != 13054:
        raise AssertionError("exact compatible-lift count changed")
    if not all(
        lift_theorem[field]
        for field in (
            "all_middle_boundary_budgets_match",
            "all_gross_credits_add",
            "all_surpluses_add",
            "all_composite_allocations_hold",
        )
    ):
        raise AssertionError("an exact-lift composition identity failed")

    audits = {
        row["quotient_level"]: row for row in observed["edge_label_pair_audits"]
    }
    if audits["accounting"]["lifted_label_pair_count"] != 569:
        raise AssertionError("lifted accounting-label pair count changed")
    if audits["skeleton"]["lifted_label_pair_count"] != 26:
        raise AssertionError("lifted skeleton-label pair count changed")
    accounting_observables = {
        row["observable"]: row for row in audits["accounting"]["observable_audit"]
    }
    if not all(row["descends"] for row in accounting_observables.values()):
        raise AssertionError("credit summary is not well-defined on accounting pairs")
    if observed["lifted_accounting_composition_relation"][
        "label_pair_count"
    ] != audits["accounting"]["lifted_label_pair_count"]:
        raise AssertionError("accounting lift relation count drift")
    if not observed["lifted_accounting_composition_relation"][
        "composite_summary_is_well_defined"
    ]:
        raise AssertionError("accounting composite summary is not well-defined")

    skeleton_observables = {
        row["observable"]: row for row in audits["skeleton"]["observable_audit"]
    }
    expected_skeleton_failures = {
        "allocation_vector": 23,
        "composite_accounting_summary": 23,
        "composite_debt_profile": 15,
        "gross_credit_vector": 0,
        "length_vector": 23,
        "partition_chain": 0,
        "peak_composite_debt": 15,
        "surplus_vector": 23,
        "tail_budget_vector": 0,
        "total_length": 23,
        "total_surplus": 23,
    }
    actual_skeleton_failures = {
        observable: row["nonconstant_label_pair_count"]
        for observable, row in skeleton_observables.items()
    }
    if actual_skeleton_failures != expected_skeleton_failures:
        raise AssertionError("skeleton credit-allocation hostile controls changed")

    reallocation = observed["extremal_credit_reallocation"]
    if reallocation["identity"] != "20 + 7 = 12 + 15 = 27":
        raise AssertionError("extremal credit reallocation drift")
    if reallocation["channels"]["heavy_comb_6_1"][
        "exact_realization_count"
    ] != 1020:
        raise AssertionError("heavy-comb zero-surplus family count changed")
    if reallocation["channels"]["fallback_5_2"][
        "exact_realization_count"
    ] != 87:
        raise AssertionError("fallback zero-surplus family count changed")

    print(
        "PASS: exact receipt credit, exact-lift addition, accounting-label "
        "composition, hostile skeleton controls, and provenance all replay"
    )


if __name__ == "__main__":
    main()
