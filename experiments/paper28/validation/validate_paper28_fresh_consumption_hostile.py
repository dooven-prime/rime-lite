#!/usr/bin/env python3
"""Replay the P28.5n fresh-consumption hostile selector."""

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

from paper28_select_fresh_consumption_hostile import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_REFERENCE,
    DEFAULT_RULE,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)

EXPECTED = {
    "selection_status": "UNIQUE_SOURCE_LOCAL_MINIMIZER",
    "primary_minimizer_count": 1,
    "minimum_structural_distance": 1,
    "finalist_count": 1,
    "minimum_placement_distance": 3,
    "context_count": 36,
}

EXPECTED_SIGNATURE = {
    "binary_kernel_mass_multiset": [0, 3],
    "cyclic_offsets_F4_to_kernel": [0, 2],
    "family": "22111__12_TO_3211",
    "fusion_contains_inherited_fresh": True,
    "fusion_parent_sizes": [1, 2],
    "rank4_partition": [3, 2, 1, 1],
    "rank5_partition": [2, 2, 1, 1, 1],
    "sigma5_length": 3,
    "sigma5_surplus": 2,
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
        raise AssertionError("unexpected P28.5n schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("P28.5n content digest mismatch")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("P28.5n contains a return evaluation")
    if payload["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("P28.5n granted section authority")
    if payload["scope"]["winner_selected"]:
        raise AssertionError("P28.5n selected a winner")

    candidate = payload["candidate"]
    observed = {
        "selection_status": candidate["selection_status"],
        "primary_minimizer_count": candidate["primary_minimizer_count"],
        "minimum_structural_distance": candidate["minimum_structural_distance"],
        "finalist_count": candidate["finalist_count"],
        "minimum_placement_distance": candidate[
            "minimum_action_relative_placement_distance"
        ],
        "context_count": candidate["context_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"P28.5n selection drift: {observed!r}")
    if candidate["eligible_signature_cell_count"] != 74:
        raise AssertionError("P28.5n 74-cell class drift")
    if candidate["preferred_signature_cell_count"] != 41:
        raise AssertionError("P28.5n 41-cell 1+2 preference drift")
    if candidate["preferred_context_count"] != 672:
        raise AssertionError("P28.5n preferred context count drift")
    if candidate["finalists"][0]["signature"] != EXPECTED_SIGNATURE:
        raise AssertionError("P28.5n finalist signature drift")
    for finalist in candidate["finalists"]:
        signature = finalist["signature"]
        if signature["fusion_contains_inherited_fresh"] is not True:
            raise AssertionError("P28.5n finalist does not consume fresh ancestry")
        if signature["sigma5_length"] != 3:
            raise AssertionError("P28.5n finalist changed the length control")
        if signature["fusion_parent_sizes"] != [1, 2]:
            raise AssertionError("P28.5n finalist left the preferred 1+2 family")
    candidate_copy = dict(candidate)
    if payload["candidate_payload_sha256"] != _digest(candidate_copy):
        raise AssertionError("P28.5n candidate payload digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--rule", type=Path, default=DEFAULT_RULE)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.input, args.rule, args.reference)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored P28.5n artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected P28.5n receipt schema")
    expected_receipt = build_receipt(
        input_path=args.input,
        rule_path=args.rule,
        reference_path=args.reference,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored P28.5n receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **EXPECTED,
                "evaluation_status": "NOT_RUN",
                "section_authority": "NOT_GRANTED",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
