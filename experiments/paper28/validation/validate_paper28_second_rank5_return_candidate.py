#!/usr/bin/env python3
"""Replay the P28.5d second rank-five return candidate selection."""

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

from paper28_select_second_rank5_return_candidate import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    EXPECTED_CANDIDATE_SIGNATURE,
    FORBIDDEN_OUTPUT_FIELDS,
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
        raise AssertionError("unexpected candidate-selection schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate selector evaluated downstream success")
    if payload["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("pre-section carrier gained recursive authority")
    if payload["carrier_audit"]["signature_cell_count"] != 562:
        raise AssertionError("future-free carrier cell count drift")
    if payload["carrier_audit"]["context_count"] != 15120:
        raise AssertionError("future-free carrier lost inherited contexts")

    candidate = payload["candidate"]
    if candidate["selected_signature"] != EXPECTED_CANDIDATE_SIGNATURE:
        raise AssertionError("selected candidate signature drift")
    if candidate["minimum_continuity_distance"] != 0:
        raise AssertionError("selected candidate is no longer a zero-distance continuation")
    if candidate["minimizer_count"] != 1:
        raise AssertionError("second-realization selector is no longer unique")
    if candidate["context_count"] != 48:
        raise AssertionError("selected candidate context count drift")
    if payload["candidate_anatomy"]["sigma6_word_distribution"] != {"1": 48}:
        raise AssertionError("candidate Sigma_6 word distribution drift")
    if payload["candidate_anatomy"]["sigma5_word_distribution"] != {
        "001": 24,
        "011": 24,
    }:
        raise AssertionError("candidate Sigma_5 tied-word distribution drift")
    if len(payload["candidate_anatomy"]["source_mass_placement_distribution"]) != 2:
        raise AssertionError("candidate source placement count drift")
    if payload["candidate_anatomy"]["target_mass_placement_count"] != 21:
        raise AssertionError("candidate target placement count drift")

    contexts = candidate["contexts"]
    if len({row["defect"] for row in contexts}) != 48:
        raise AssertionError("candidate defects are not distinct")
    if any(row["carrier_signature"] != EXPECTED_CANDIDATE_SIGNATURE for row in contexts):
        raise AssertionError("candidate row escaped the selected signature")

    encoded = json.dumps(
        candidate, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).lower()
    for field in FORBIDDEN_OUTPUT_FIELDS:
        if field in encoded:
            raise AssertionError(f"future-success field leaked into candidate: {field}")

    if payload["candidate_payload_sha256"] != _digest(candidate):
        raise AssertionError("candidate payload digest mismatch")
    content = dict(payload)
    observed = content.pop("content_sha256")
    if observed != _digest(content):
        raise AssertionError("artifact content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.input)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored candidate selection differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected candidate-selection receipt schema")
    expected_receipt = build_receipt(
        input_path=args.input, output=args.artifact, payload=stored
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or closure binding drifted")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "candidate_family": EXPECTED_CANDIDATE_SIGNATURE["family"],
                "candidate_contexts": 48,
                "section_authority": "NOT_GRANTED",
                "good_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
