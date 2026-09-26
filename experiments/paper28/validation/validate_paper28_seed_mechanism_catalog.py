#!/usr/bin/env python3
"""Validate the deterministic Paper XXVIII ``4+35`` seed catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
if str(EXPERIMENT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT))

from paper28_mechanism_schema import (
    audit_composition_matrix,
    audit_unary_matrix,
    exact_receipt_sha256,
    validate_receipt,
)
from paper28_project_seed_mechanisms import (
    CATALOG_SCHEMA,
    DEFAULT_OUTPUT,
    OBSERVABLES,
    _digest,
    _resolve_n6_input,
    _resolve_n7_input,
    _sha256,
    build_payload,
    build_receipt,
    default_receipt_path,
    read_catalog,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--n6-entry-input", type=Path)
    parser.add_argument("--n7-carrier-input", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = read_catalog(args.catalog)
    assert catalog["schema"] == CATALOG_SCHEMA
    assert catalog["counts"]["seed_contexts"] == 39
    assert catalog["counts"]["n6_seed_contexts"] == 4
    assert catalog["counts"]["n7_seed_contexts"] == 35

    n6_input = _resolve_n6_input(args.n6_entry_input)
    n7_input = _resolve_n7_input(args.n7_carrier_input)
    assert catalog["inputs"]["n6_entry_exhaustiveness"]["sha256"] == _sha256(
        n6_input.resolve()
    )
    assert catalog["inputs"]["n7_extremal_carrier"]["sha256"] == _sha256(
        n7_input.resolve()
    )

    receipts = catalog["receipts"]
    ids = []
    for receipt in receipts:
        validate_receipt(receipt)
        expected_id = f"r-{exact_receipt_sha256(receipt)[:24]}"
        assert receipt["receipt_id"] == expected_id
        ids.append(expected_id)
    assert len(ids) == len(set(ids)) == catalog["counts"]["exact_receipts"]

    edges = [
        (row["source_receipt_id"], row["successor_receipt_id"])
        for row in catalog["compatibility_edges"]
    ]
    by_source_context: dict[str, set[str]] = {}
    for receipt in receipts:
        by_source_context.setdefault(
            receipt["exact"]["source_context_id"], set()
        ).add(receipt["receipt_id"])
    expected_edges = sorted(
        (receipt["receipt_id"], successor)
        for receipt in receipts
        for successor in by_source_context.get(
            receipt["exact"]["target_context"]["context_id"], set()
        )
    )
    assert sorted(edges) == expected_edges
    assert len(edges) == catalog["counts"]["compatibility_edges"]
    assert catalog["unary_observable_audit"] == audit_unary_matrix(
        receipts, OBSERVABLES
    )
    assert catalog["composition_congruence_audit"] == audit_composition_matrix(
        receipts, edges
    )

    without_digest = dict(catalog)
    content_sha256 = without_digest.pop("content_sha256")
    assert content_sha256 == _digest(without_digest)

    rebuilt = build_payload(n6_input.resolve(), n7_input.resolve())
    assert rebuilt == catalog
    receipt_path = args.receipt or default_receipt_path(args.catalog)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt == build_receipt(output=args.catalog, payload=catalog)
    print(
        "paper28 4+35 seed mechanism catalog: PASS "
        f"({len(receipts)} receipts, {len(edges)} compatibility edges)"
    )


if __name__ == "__main__":
    main()
