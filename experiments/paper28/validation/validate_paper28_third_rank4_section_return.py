#!/usr/bin/env python3
"""Replay the post-freeze P28.5j third rank-four Good_4 evaluator."""

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

from paper28_evaluate_third_rank4_section_return import (
    DEFAULT_CANDIDATE,
    DEFAULT_OUTPUT,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED = {
    "source_context_count": 36,
    "channel_count": 172,
    "exact_lift_count": 5239,
    "successful_source_count": 36,
    "hostile_source_count": 0,
    "successful_channel_count": 171,
    "failed_channel_count": 1,
    "successful_exact_lift_count": 4208,
    "unsuccessful_exact_lift_count": 1031,
    "certified_target_context_count": 624,
    "good_channel_count_histogram": {"3": 2, "4": 12, "5": 16, "6": 5, "7": 1},
    "mixed_channel_count": 63,
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
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _assert_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected third rank-four evaluation schema")
    scope = payload["scope"]
    evaluation = payload["evaluation"]
    mixed_channel_count = sum(
        1
        for context in evaluation["contexts"]
        for channel in context["channels"]
        if channel["successful_exact_lift_count"]
        and channel["unsuccessful_exact_lift_count"]
    )
    observed = {
        "source_context_count": scope["source_context_count"],
        "channel_count": evaluation["channel_count"],
        "exact_lift_count": evaluation["exact_lift_count"],
        "successful_source_count": evaluation["successful_source_count"],
        "hostile_source_count": evaluation["hostile_source_count"],
        "successful_channel_count": evaluation["successful_channel_count"],
        "failed_channel_count": evaluation["failed_channel_count"],
        "successful_exact_lift_count": evaluation["successful_exact_lift_count"],
        "unsuccessful_exact_lift_count": evaluation[
            "unsuccessful_exact_lift_count"
        ],
        "certified_target_context_count": evaluation["certified_target_context_count"],
        "good_channel_count_histogram": evaluation["good_channel_count_histogram"],
        "mixed_channel_count": mixed_channel_count,
    }
    if observed != EXPECTED:
        raise AssertionError(f"third Good_4 finite equalities drift: {observed!r}")
    if scope["winner_selected"] or scope["menu_or_lift_rebuilt"]:
        raise AssertionError("third evaluator changed its quantifier boundary")
    if evaluation["successful_source_count"] + evaluation["hostile_source_count"] != 36:
        raise AssertionError("third source evaluation partition drift")
    if evaluation["successful_channel_count"] + evaluation["failed_channel_count"] != 172:
        raise AssertionError("third channel evaluation partition drift")
    if (
        evaluation["successful_exact_lift_count"]
        + evaluation["unsuccessful_exact_lift_count"]
        != 5239
    ):
        raise AssertionError("third exact-lift evaluation partition drift")
    if evaluation["all_sources_have_good_channel"] != (
        evaluation["hostile_source_count"] == 0
    ):
        raise AssertionError("third all-sources-good flag drift")

    authority = payload["certified_lower_section"]
    if evaluation["all_sources_have_good_channel"]:
        if authority["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
            raise AssertionError("successful third carrier did not receive authority")
        if authority["context_count"] != 36 or len(authority["contexts"]) != 36:
            raise AssertionError("third certified section context count drift")
    else:
        if authority["authority_status"] != "NOT_GRANTED_HOSTILE_SOURCES_PRESENT":
            raise AssertionError("hostile third carrier incorrectly received authority")
        if authority["context_count"] or authority["contexts"]:
            raise AssertionError("hostile third carrier exported section contexts")
    if payload["checkpoint_type_audit"]["internal_boundaries_exported_as_checkpoints"]:
        raise AssertionError("third internal boundary exported as checkpoint")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("third evaluation content digest mismatch")


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
        raise AssertionError("stored third Good_4 evaluation differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected third Good_4 receipt schema")
    expected_receipt = build_receipt(
        candidate_path=args.candidate, output=args.artifact, payload=stored
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("third Good_4 receipt is stale")

    evaluation = stored["evaluation"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "all_sources_have_good_channel": evaluation[
                    "all_sources_have_good_channel"
                ],
                "successful_sources": evaluation["successful_source_count"],
                "hostile_sources": evaluation["hostile_source_count"],
                "successful_channels": evaluation["successful_channel_count"],
                "failed_channels": evaluation["failed_channel_count"],
                "successful_exact_lifts": evaluation["successful_exact_lift_count"],
                "unsuccessful_exact_lifts": evaluation[
                    "unsuccessful_exact_lift_count"
                ],
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
