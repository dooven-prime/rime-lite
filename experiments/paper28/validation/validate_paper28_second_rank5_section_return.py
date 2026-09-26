#!/usr/bin/env python3
"""Replay the post-freeze second rank-five typed return evaluator."""

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

from paper28_evaluate_second_rank5_section_return import (
    DEFAULT_CANDIDATE,
    DEFAULT_LOWER_SECTION,
    DEFAULT_OUTPUT,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED_SCOPE = {
    "source_context_count": 48,
    "channel_count": 96,
    "exact_lift_count": 195,
    "successful_source_count": 48,
    "hostile_source_count": 0,
    "successful_channel_count": 48,
    "failed_channel_count": 48,
    "successful_exact_lift_count": 48,
    "unsuccessful_exact_lift_count": 147,
    "good_channel_count_histogram": {"1": 48},
    "handoff_type_histogram": {"IDENTITY": 48},
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


def _assert_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected second rank-five evaluation schema")
    scope = payload["scope"]
    evaluation = payload["evaluation"]
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
        "good_channel_count_histogram": evaluation[
            "good_channel_count_histogram"
        ],
        "handoff_type_histogram": evaluation["handoff_type_histogram"],
    }
    if observed != EXPECTED_SCOPE:
        raise AssertionError(f"second rank-five scope drift: {observed!r}")
    if scope["winner_selected"] or scope["menu_or_lift_rebuilt"]:
        raise AssertionError("evaluator changed the frozen quantifier boundary")
    if evaluation["successful_source_count"] + evaluation[
        "hostile_source_count"
    ] != 48:
        raise AssertionError("source evaluation partition drift")
    if evaluation["successful_channel_count"] + evaluation[
        "failed_channel_count"
    ] != 96:
        raise AssertionError("channel evaluation partition drift")
    if evaluation["successful_exact_lift_count"] + evaluation[
        "unsuccessful_exact_lift_count"
    ] != 195:
        raise AssertionError("exact-lift evaluation partition drift")
    if evaluation["all_sources_have_good_channel"] != (
        evaluation["hostile_source_count"] == 0
    ):
        raise AssertionError("all-sources-good flag drift")
    handoff_count = sum(
        int(value) for value in evaluation["handoff_type_histogram"].values()
    )
    if handoff_count != evaluation["successful_exact_lift_count"]:
        raise AssertionError("typed handoff histogram does not cover successes")
    if payload["checkpoint_type_audit"][
        "internal_boundaries_exported_as_checkpoints"
    ]:
        raise AssertionError("internal boundary exported as checkpoint")
    if evaluation["all_sources_have_good_channel"]:
        authority = payload["certified_source_section"]
        if (
            authority["return_authority_status"]
            != "GRANTED_BY_FIXED_SCOPE_GOOD5_EVALUATION"
        ):
            raise AssertionError("successful source did not receive return authority")
        if authority["context_count"] != 48:
            raise AssertionError("certified source section count drift")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("evaluation content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument(
        "--lower-section",
        type=Path,
        default=DEFAULT_LOWER_SECTION,
    )
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.candidate, args.lower_section)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored second rank-five evaluation differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected second rank-five evaluation receipt schema")
    expected_receipt = build_receipt(
        candidate_path=args.candidate,
        lower_section_path=args.lower_section,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or closure binding drifted")

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
                "successful_exact_lifts": evaluation[
                    "successful_exact_lift_count"
                ],
                "unsuccessful_exact_lifts": evaluation[
                    "unsuccessful_exact_lift_count"
                ],
                "handoff_types": evaluation["handoff_type_histogram"],
                "source_return_authority": stored[
                    "certified_source_section"
                ]["return_authority_status"],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
