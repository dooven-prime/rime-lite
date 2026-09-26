#!/usr/bin/env python3
"""Recompute and validate the fixed-scope Paper XXVIII section-return menu."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_audit_section_return_menu import (  # noqa: E402
    AUDIT_SCHEMA,
    DEFAULT_CATALOG,
    DEFAULT_FACTORIZATION,
    DEFAULT_OUTPUT,
    build_audit,
    build_receipt,
    default_receipt_path,
)

EXPECTED_MENU = {
    "context_count": 35,
    "channel_count": 173,
    "accounting_refinement_count": 864,
    "exact_lift_count": 4182,
    "max_menu_size": 8,
    "menu_size_histogram": {
        "2": 1,
        "3": 6,
        "4": 5,
        "5": 12,
        "6": 6,
        "7": 3,
        "8": 2,
    },
}

EXPECTED_CERTIFICATION = {
    "successful_channel_count": 169,
    "failed_channel_count": 4,
    "successful_exact_lift_count": 2329,
    "failed_exact_lift_count": 1853,
    "certified_target_context_count": 303,
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


def _assert_expected(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != AUDIT_SCHEMA:
        raise AssertionError("unexpected section-return audit schema")
    menu = payload["future_free_menu"]
    certification = payload["success_certification"]
    for field, expected in EXPECTED_MENU.items():
        if menu[field] != expected:
            raise AssertionError(f"menu field drift: {field}")
    for field, expected in EXPECTED_CERTIFICATION.items():
        if certification[field] != expected:
            raise AssertionError(f"certification field drift: {field}")
    if not certification["all_declared_sources_have_successful_channel"]:
        raise AssertionError("a declared section source lacks a successful channel")
    if certification["evaluator_used_during_menu_generation"]:
        raise AssertionError("success evaluator leaked into menu generation")
    if payload["future_free_menu_content_sha256"] != _digest(menu):
        raise AssertionError("future-free menu digest mismatch")
    exclusion = payload["internal_boundary_exclusion"]
    for field in (
        "menu_source_not_in_declared_section_count",
        "recursive_target_not_in_certified_base_count",
        "internal_only_boundary_exported_as_checkpoint_count",
    ):
        if exclusion[field] != 0:
            raise AssertionError(f"internal-boundary exclusion failed: {field}")


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--factorization", type=Path, default=DEFAULT_FACTORIZATION
    )
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_audit(args.catalog, args.factorization)
    _assert_expected(stored)
    _assert_expected(recomputed)
    if stored != recomputed:
        raise AssertionError("stored section-return artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected_receipt = build_receipt(
        output=args.artifact,
        payload=stored,
        catalog_path=args.catalog,
        factorization_path=args.factorization,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or does not bind the closure")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "content_sha256": stored["content_sha256"],
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "declared_section_sources": stored["scope"][
                    "declared_section_context_count"
                ],
                "future_free_channels": stored["future_free_menu"][
                    "channel_count"
                ],
                "successful_channels": stored["success_certification"][
                    "successful_channel_count"
                ],
                "failed_channels": stored["success_certification"][
                    "failed_channel_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
