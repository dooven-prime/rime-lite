#!/usr/bin/env python3
"""Recompute and validate the Paper XXVIII boundary-generator factorization."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_factor_boundary_generators import (  # noqa: E402
    AUDIT_SCHEMA,
    DEFAULT_CATALOG,
    DEFAULT_OUTPUT,
    PRIMITIVE_KINDS,
    build_receipt,
    build_audit,
    default_receipt_path,
)

EXPECTED = {
    "exact_receipt_count": 11252,
    "exact_operation_occurrence_count": 123240,
    "exact_state_count": 14482,
    "operation_occurrence_counts": {
        "FUSION": 20870,
        "RETURN": 52714,
        "TRANSPORT": 49656,
    },
    "relation_row_count": 24355,
    "relation_row_counts_by_kind": {
        "FUSION": 4189,
        "RETURN": 8113,
        "TRANSPORT": 12053,
    },
    "max_exact_realization_fiber_by_kind": {
        "FUSION": 192,
        "RETURN": 336,
        "TRANSPORT": 200,
    },
    "source_boundary_count": 8763,
    "max_relation_menu_size": 32,
    "max_generator_kind_menu_size": 2,
    "historical_features": {
        "one_corridor_completion": 1634,
        "rank_two_52_fallback": 106,
        "rank_two_61_heavy_target": 3936,
        "repeated_fusion_heavy_chain": 9608,
        "two_corridor_repayment": 9618,
        "zero_surplus_rank_two_52_fallback": 87,
        "zero_surplus_rank_two_61_heavy_target": 1020,
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _assert_expected(payload: dict[str, Any]) -> None:
    if payload.get("schema") != AUDIT_SCHEMA:
        raise AssertionError("unexpected audit schema")
    factorization = payload["factorization"]
    relations = payload["generator_relations"]
    if payload["scope"]["exact_receipt_count"] != EXPECTED["exact_receipt_count"]:
        raise AssertionError("exact receipt count drift")
    for field in ("exact_operation_occurrence_count", "exact_state_count"):
        if factorization[field] != EXPECTED[field]:
            raise AssertionError(f"{field} drift")
    if factorization["operation_occurrence_counts"] != EXPECTED[
        "operation_occurrence_counts"
    ]:
        raise AssertionError("operation occurrence counts drift")
    for field in (
        "relation_row_count",
        "relation_row_counts_by_kind",
        "max_exact_realization_fiber_by_kind",
        "source_boundary_count",
        "max_relation_menu_size",
        "max_generator_kind_menu_size",
    ):
        if relations[field] != EXPECTED[field]:
            raise AssertionError(f"{field} drift")
    if payload["historical_name_reduction"]["receipt_feature_counts"] != EXPECTED[
        "historical_features"
    ]:
        raise AssertionError("historical feature counts drift")
    if factorization["residual_receipt_count"] != 0:
        raise AssertionError("generator cover acquired residual receipts")
    for field in (
        "all_exact_endpoints_replayed",
        "all_lengths_recovered",
        "all_surpluses_recovered",
        "all_words_reconstructed",
        "all_adjacent_operations_share_exact_boundary",
        "every_corridor_has_one_terminal_fusion",
    ):
        if not factorization[field]:
            raise AssertionError(f"factorization invariant failed: {field}")
    if not relations["every_relation_row_has_exact_lift"]:
        raise AssertionError("an abstract generator row lacks an exact lift")
    if tuple(payload["generator_definition"]["primitive_kinds"]) != PRIMITIVE_KINDS:
        raise AssertionError("primitive generator kinds drift")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_audit(args.catalog)
    _assert_expected(stored)
    _assert_expected(recomputed)
    if stored != recomputed:
        raise AssertionError("stored artifact differs from full recomputation")
    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected_receipt = build_receipt(
        output=args.artifact,
        payload=stored,
        catalog_path=args.catalog,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or does not bind the closure")
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "artifact_sha256": _sha256(args.artifact),
                "content_sha256": stored["content_sha256"],
                "exact_receipts": stored["scope"]["exact_receipt_count"],
                "exact_operation_occurrences": stored["factorization"][
                    "exact_operation_occurrence_count"
                ],
                "generator_relation_rows": stored["generator_relations"][
                    "relation_row_count"
                ],
                "residual_receipts": stored["factorization"][
                    "residual_receipt_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
