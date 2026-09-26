#!/usr/bin/env python3
"""Replay the read-only P28.5i typed section-overlap audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_audit_third_rank4_section_overlap import (
    DEFAULT_AUTHORITY,
    DEFAULT_OUTPUT,
    DEFAULT_SELECTION,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = json.loads(args.artifact.read_text(encoding="ascii"))
    recomputed = build_payload(args.selection, args.authority)
    if stored != recomputed:
        raise AssertionError("stored typed-overlap audit differs from replay")
    if stored.get("schema") != SCHEMA:
        raise AssertionError("unexpected typed-overlap schema")
    if stored["scope"] != {
        "ambient_n": 7,
        "candidate_membership_mutated": False,
        "good_4_evaluated": False,
        "menu_constructed": False,
    }:
        raise AssertionError("typed-overlap audit crossed its phase boundary")
    expected = {
        "third_candidate_context_count": 36,
        "second_section_context_count": 48,
        "intersection_count": 0,
        "intersection_context_ids": [],
        "third_only_count": 36,
        "second_only_count": 48,
        "classification": "DISJOINT_TYPED_CONTEXTS",
    }
    if stored["overlap"] != expected:
        raise AssertionError(f"typed overlap drift: {stored['overlap']!r}")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    receipt = json.loads(receipt_path.read_text(encoding="ascii"))
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected typed-overlap receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        authority_path=args.authority,
        output=args.artifact,
        payload=stored,
    )
    if receipt != expected_receipt:
        raise AssertionError("typed-overlap receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "intersection": 0,
                "classification": "DISJOINT_TYPED_CONTEXTS",
                "candidate_membership_mutated": False,
                "good_4_evaluated": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
