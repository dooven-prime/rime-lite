#!/usr/bin/env python3
"""Replay the read-only fourth rank-four overlap audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_audit_fourth_rank4_section_overlap import (
    DEFAULT_OUTPUT,
    DEFAULT_SECOND_AUTHORITY,
    DEFAULT_SELECTION,
    DEFAULT_THIRD_AUTHORITY,
    RECEIPT_SCHEMA,
    SCHEMA,
    _digest,
    _load,
    build_payload,
    build_receipt,
    default_receipt_path,
)


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fourth overlap schema")
    overlap = payload["overlap"]
    expected = {
        "fourth": 36,
        "second": 48,
        "third": 36,
        "second_intersection": 0,
        "third_intersection": 0,
        "union_intersection": 0,
        "fourth_only": 36,
        "classification": "DISJOINT_FROM_CERTIFIED_RANK4_SECTIONS",
    }
    observed = {
        "fourth": overlap["fourth_candidate_context_count"],
        "second": overlap["second_section_context_count"],
        "third": overlap["third_section_context_count"],
        "second_intersection": overlap["second_intersection_count"],
        "third_intersection": overlap["third_intersection_count"],
        "union_intersection": overlap["certified_union_intersection_count"],
        "fourth_only": overlap["fourth_only_count"],
        "classification": overlap["classification"],
    }
    if observed != expected:
        raise AssertionError(f"fourth overlap drift: {observed!r}")
    scope = payload["scope"]
    if scope["candidate_membership_mutated"] or scope["menu_constructed"]:
        raise AssertionError("fourth overlap audit changed the candidate")
    if scope["good_4_evaluated"]:
        raise AssertionError("fourth overlap audit evaluated Good_4")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("fourth overlap content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument(
        "--second-authority", type=Path, default=DEFAULT_SECOND_AUTHORITY
    )
    parser.add_argument("--third-authority", type=Path, default=DEFAULT_THIRD_AUTHORITY)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(
        args.selection, args.second_authority, args.third_authority
    )
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fourth overlap audit differs from replay")
    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="ascii"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fourth overlap receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        second_authority_path=args.second_authority,
        third_authority_path=args.third_authority,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fourth overlap receipt is stale")
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "fourth_contexts": 36,
                "union_intersection": 0,
                "candidate_membership_mutated": False,
                "good_4_evaluated": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
