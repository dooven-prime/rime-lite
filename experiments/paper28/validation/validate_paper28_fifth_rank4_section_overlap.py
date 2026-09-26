#!/usr/bin/env python3
"""Replay the read-only fifth rank-four section-overlap audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_audit_fifth_rank4_section_overlap import (
    DEFAULT_FOURTH_AUTHORITY,
    DEFAULT_OUTPUT,
    DEFAULT_SECOND_AUTHORITY,
    DEFAULT_SELECTION,
    DEFAULT_THIRD_AUTHORITY,
    RECEIPT_SCHEMA,
    SCHEMA,
    _digest,
    _load,
    _sha256,
    build_payload,
    build_receipt,
    default_receipt_path,
)

EXPECTED = {
    "fifth_context_count": 10,
    "second_intersection_count": 0,
    "third_intersection_count": 0,
    "fourth_intersection_count": 0,
    "certified_union_intersection_count": 0,
    "fifth_only_count": 10,
    "classification": "DISJOINT_FROM_CERTIFIED_RANK4_SECTIONS",
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fifth overlap schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("fifth overlap content digest mismatch")
    if payload["scope"] != {
        "ambient_n": 7,
        "candidate_membership_mutated": False,
        "menu_constructed": False,
        "good_4_evaluated": False,
    }:
        raise AssertionError("fifth overlap scope drift")
    overlap = payload["overlap"]
    observed = {
        "fifth_context_count": overlap["fifth_candidate_context_count"],
        "second_intersection_count": overlap["sections"]["second"][
            "intersection_count"
        ],
        "third_intersection_count": overlap["sections"]["third"]["intersection_count"],
        "fourth_intersection_count": overlap["sections"]["fourth"][
            "intersection_count"
        ],
        "certified_union_intersection_count": overlap[
            "certified_union_intersection_count"
        ],
        "fifth_only_count": overlap["fifth_only_count"],
        "classification": overlap["classification"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fifth overlap drift: {observed!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument(
        "--second-authority", type=Path, default=DEFAULT_SECOND_AUTHORITY
    )
    parser.add_argument("--third-authority", type=Path, default=DEFAULT_THIRD_AUTHORITY)
    parser.add_argument(
        "--fourth-authority", type=Path, default=DEFAULT_FOURTH_AUTHORITY
    )
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(
        args.selection,
        args.second_authority,
        args.third_authority,
        args.fourth_authority,
    )
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fifth overlap artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fifth overlap receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        second_authority_path=args.second_authority,
        third_authority_path=args.third_authority,
        fourth_authority_path=args.fourth_authority,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fifth overlap receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **EXPECTED,
                "candidate_membership_mutated": False,
                "good_4_evaluated": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
