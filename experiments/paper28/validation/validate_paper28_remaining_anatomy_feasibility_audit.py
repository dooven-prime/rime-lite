#!/usr/bin/env python3
"""Replay the P28.5m remaining-anatomy feasibility audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_remaining_anatomy_feasibility_audit import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_RULE,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED_QUADRANTS = {
    "length_3__fresh_consumed": [74, 1224],
    "length_3__fresh_not_consumed": [126, 1751],
    "length_not_3__fresh_consumed": [142, 5032],
    "length_not_3__fresh_not_consumed": [220, 7113],
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def _assert_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected P28.5m schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("P28.5m content digest mismatch")
    scope = payload["scope"]
    if scope["new_oracle_evaluation"] or scope["good_or_success_field_read"]:
        raise AssertionError("P28.5m crossed the zero-success-information boundary")
    if scope["fourth_candidate_selected"]:
        raise AssertionError("P28.5m unexpectedly selected a fourth carrier")
    if scope["rooted_context_count"] != 15120:
        raise AssertionError("P28.5m rooted scope drift")
    if scope["future_free_signature_cell_count"] != 562:
        raise AssertionError("P28.5m signature-cell count drift")

    observed = {
        row["quadrant"]: [row["signature_cell_count"], row["context_count"]]
        for row in payload["quadrants"]
    }
    if observed != EXPECTED_QUADRANTS:
        raise AssertionError(f"P28.5m quadrant drift: {observed!r}")
    if sum(value[0] for value in observed.values()) != 562:
        raise AssertionError("P28.5m cell partition drift")
    if sum(value[1] for value in observed.values()) != 15120:
        raise AssertionError("P28.5m context partition drift")
    if payload["fresh_participation_checksum"] != {
        "consumed_context_count": 6256,
        "not_consumed_context_count": 8864,
    }:
        raise AssertionError("P28.5m fresh-participation checksum drift")

    feasibility = payload["derived_feasibility"]
    if not feasibility["length_3_fresh_consumed_nonempty"]:
        raise AssertionError("preferred one-variable hostile class became empty")
    gate = payload["next_stage_gate"]
    if gate["status"] != "HOSTILE_CLASS_FEASIBLE_CARRIER_NOT_SELECTED":
        raise AssertionError("P28.5m next-stage gate drift")
    if gate["fourth_candidate_selected"]:
        raise AssertionError("P28.5m gate serialized a fourth candidate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--rule", type=Path, default=DEFAULT_RULE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.input, args.rule)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored P28.5m artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = _load(receipt_path)
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected P28.5m receipt schema")
    expected_receipt = build_receipt(
        input_path=args.input,
        rule_path=args.rule,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored P28.5m receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "quadrants": EXPECTED_QUADRANTS,
                "fresh_consumed_contexts": 6256,
                "fresh_not_consumed_contexts": 8864,
                "next_stage": stored["next_stage_gate"]["status"],
                "fourth_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
