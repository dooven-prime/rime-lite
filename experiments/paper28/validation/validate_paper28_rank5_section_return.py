#!/usr/bin/env python3
"""Replay and validate the fixed-scope P28.5b Good_5 evaluation."""

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

from paper28_evaluate_rank5_section_return import (
    DEFAULT_CANDIDATE,
    DEFAULT_OUTPUT,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_evaluation,
    build_receipt,
    default_receipt_path,
)

EXPECTED_SUMMARY = {
    "source_context_count": 35,
    "successful_source_count": 35,
    "hostile_source_count": 0,
    "channel_count": 87,
    "successful_channel_count": 35,
    "failed_channel_count": 52,
    "exact_lift_count": 214,
    "successful_exact_lift_count": 35,
    "unsuccessful_exact_lift_count": 179,
    "good_channel_count_histogram": {"1": 35},
    "all_sources_have_good_channel": True,
    "winner_selected": False,
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


def _assert_evaluation(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected rank-five return evaluation schema")
    if payload["summary"] != EXPECTED_SUMMARY:
        raise AssertionError(f"rank-five return summary drift: {payload['summary']!r}")
    discipline = payload["quantifier_discipline"]
    for field in (
        "candidate_rebuilt",
        "menu_rebuilt",
        "exact_lifts_rebuilt",
        "best_channel_selected",
    ):
        if discipline[field]:
            raise AssertionError(f"quantifier discipline failed: {field}")
    if payload["hostile_sources"]:
        raise AssertionError("a rank-five source lacks a good channel")

    channel_count = 0
    lift_count = 0
    successful_lifts = 0
    canonical_handoff_context_ids = set()
    for source in payload["sources"]:
        if source["menu_size"] != len(source["channels"]):
            raise AssertionError("source menu size drift")
        observed_good = [
            row["channel_id"] for row in source["channels"] if row["good_5"]
        ]
        if source["good_channel_ids"] != observed_good:
            raise AssertionError("source good-channel set drift")
        if source["good_channel_count"] != len(observed_good):
            raise AssertionError("source good-channel count drift")
        if source["has_good_channel"] != bool(observed_good):
            raise AssertionError("source existential return flag drift")
        channel_count += len(source["channels"])
        for channel in source["channels"]:
            successful = channel["successful_exact_lifts"]
            unsuccessful = channel["unsuccessful_exact_lifts"]
            if any(not row["target_in_lower_section"] for row in successful):
                raise AssertionError("successful lift misses the lower section")
            if any(row["target_in_lower_section"] for row in unsuccessful):
                raise AssertionError("unsuccessful lift entered the lower section")
            if channel["good_5"] != bool(successful):
                raise AssertionError("Good_5 channel value drift")
            if channel["successful_exact_lift_count"] != len(successful):
                raise AssertionError("successful lift count drift")
            if channel["unsuccessful_exact_lift_count"] != len(unsuccessful):
                raise AssertionError("unsuccessful lift count drift")
            if channel["exact_lift_count"] != len(successful) + len(unsuccessful):
                raise AssertionError("channel exact-lift partition drift")
            for lift in successful:
                handoff = lift["exact_role_handoff"]
                atom_rows = handoff["canonical_to_actual_atom_bijection"]
                if {row["canonical_atom"] for row in atom_rows} != set(range(7)):
                    raise AssertionError("handoff canonical atoms are not bijective")
                if {row["actual_atom"] for row in atom_rows} != set(range(7)):
                    raise AssertionError("handoff actual atoms are not bijective")
                if not handoff["distinguished_packet_preserved"]:
                    raise AssertionError("handoff lost the distinguished packet")
                canonical_handoff_context_ids.add(
                    handoff["canonical_source_context_id"]
                )
            lift_count += channel["exact_lift_count"]
            successful_lifts += len(successful)
    if channel_count != EXPECTED_SUMMARY["channel_count"]:
        raise AssertionError("global channel count drift")
    if lift_count != EXPECTED_SUMMARY["exact_lift_count"]:
        raise AssertionError("global exact-lift count drift")
    if successful_lifts != EXPECTED_SUMMARY["successful_exact_lift_count"]:
        raise AssertionError("global successful-lift count drift")
    if len(canonical_handoff_context_ids) != 35:
        raise AssertionError("section handoff does not cover 35 canonical sources")

    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("evaluation content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--n7-extremal-input", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_evaluation(args.candidate, args.n7_extremal_input)
    _assert_evaluation(stored)
    _assert_evaluation(recomputed)
    if stored != recomputed:
        raise AssertionError("stored Good_5 evaluation differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected rank-five evaluation receipt schema")
    expected_receipt = build_receipt(output=args.artifact, payload=stored)
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or closure binding drifted")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "content_sha256": stored["content_sha256"],
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **stored["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
