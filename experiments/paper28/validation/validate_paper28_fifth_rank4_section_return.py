#!/usr/bin/env python3
"""Replay Good_4 for the frozen fifth rank-four relation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_evaluate_fifth_rank4_section_return import (
    DEFAULT_CANDIDATE,
    DEFAULT_OUTPUT,
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
    "source_context_count": 10,
    "successful_source_count": 10,
    "hostile_source_count": 0,
    "channel_count": 53,
    "successful_channel_count": 53,
    "failed_channel_count": 0,
    "mixed_channel_count": 18,
    "exact_lift_count": 1476,
    "successful_exact_lift_count": 1205,
    "unsuccessful_exact_lift_count": 271,
    "good_channel_count_histogram": {"4": 1, "5": 5, "6": 4},
    "certified_target_context_count": 174,
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fifth Good_4 schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("fifth Good_4 content digest mismatch")
    evaluation = payload["evaluation"]
    observed = {
        "source_context_count": payload["scope"]["source_context_count"],
        "successful_source_count": evaluation["successful_source_count"],
        "hostile_source_count": evaluation["hostile_source_count"],
        "channel_count": evaluation["channel_count"],
        "successful_channel_count": evaluation["successful_channel_count"],
        "failed_channel_count": evaluation["failed_channel_count"],
        "mixed_channel_count": evaluation["mixed_channel_count"],
        "exact_lift_count": evaluation["exact_lift_count"],
        "successful_exact_lift_count": evaluation["successful_exact_lift_count"],
        "unsuccessful_exact_lift_count": evaluation["unsuccessful_exact_lift_count"],
        "good_channel_count_histogram": evaluation["good_channel_count_histogram"],
        "certified_target_context_count": evaluation["certified_target_context_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fifth Good_4 drift: {observed!r}")
    if evaluation["successful_source_count"] + evaluation["hostile_source_count"] != 10:
        raise AssertionError("fifth Good_4 source partition drift")
    if (
        evaluation["successful_channel_count"] + evaluation["failed_channel_count"]
        != evaluation["channel_count"]
    ):
        raise AssertionError("fifth Good_4 channel partition drift")
    if (
        evaluation["successful_exact_lift_count"]
        + evaluation["unsuccessful_exact_lift_count"]
        != evaluation["exact_lift_count"]
    ):
        raise AssertionError("fifth Good_4 lift partition drift")
    authority = payload["certified_lower_section"]
    if evaluation["all_sources_have_good_channel"]:
        if authority["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
            raise AssertionError("fifth Good_4 failed to grant authority")
        if authority["context_count"] != 10 or len(authority["contexts"]) != 10:
            raise AssertionError("fifth certified section count drift")
    elif authority["authority_status"] != "NOT_GRANTED_HOSTILE_SOURCES_PRESENT":
        raise AssertionError("fifth hostile evaluation authority drift")
    if payload["checkpoint_type_audit"]["internal_boundaries_exported_as_checkpoints"]:
        raise AssertionError("fifth evaluator exported internal checkpoint")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.candidate)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fifth Good_4 evaluation differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fifth Good_4 receipt schema")
    expected_receipt = build_receipt(
        candidate_path=args.candidate,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fifth Good_4 receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **EXPECTED,
                "section_authority": stored["certified_lower_section"][
                    "authority_status"
                ],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
