#!/usr/bin/env python3
"""Replay the frozen fifth rank-four menu and exact-lift relation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_prepare_fifth_rank4_section_candidate import (
    DEFAULT_OUTPUT,
    DEFAULT_OVERLAP,
    DEFAULT_SELECTION,
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
    "channel_count": 53,
    "accounting_refinement_count": 498,
    "exact_lift_count": 1476,
    "max_menu_size": 6,
    "menu_size_histogram": {"4": 1, "5": 5, "6": 4},
    "replay_state_count": 4239,
    "receipt_endpoint_state_count": 204,
    "internal_only_state_count": 4035,
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fifth rank-four candidate schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("fifth candidate content digest mismatch")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("fifth candidate contains Good_4 output")
    if payload["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("fifth candidate granted section authority")
    if payload["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("fifth candidate evaluator status drift")

    construction = payload["construction"]
    if payload["construction_payload_sha256"] != _digest(construction):
        raise AssertionError("fifth construction digest mismatch")
    menus = construction["menus"]
    checkpoint = construction["checkpoint_type_audit"]
    observed = {
        "source_context_count": menus["context_count"],
        "channel_count": menus["channel_count"],
        "accounting_refinement_count": menus["accounting_refinement_count"],
        "exact_lift_count": menus["exact_lift_count"],
        "max_menu_size": menus["max_menu_size"],
        "menu_size_histogram": menus["menu_size_histogram"],
        "replay_state_count": checkpoint["replay_state_count"],
        "receipt_endpoint_state_count": checkpoint["receipt_endpoint_state_count"],
        "internal_only_state_count": checkpoint["internal_only_state_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fifth rank-four relation drift: {observed!r}")
    if checkpoint["internal_only_exported_as_checkpoint"] != 0:
        raise AssertionError("fifth construction exported an internal checkpoint")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--overlap", type=Path, default=DEFAULT_OVERLAP)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.selection, args.overlap)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fifth candidate differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fifth candidate receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        overlap_path=args.overlap,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fifth candidate receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **EXPECTED,
                "good_4_evaluation": "NOT_RUN",
                "section_authority": "NOT_GRANTED",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
