#!/usr/bin/env python3
"""Replay the P28.5h third rank-five return candidate selection."""

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

from paper28_select_third_rank5_return_candidate import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_RULE,
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
        raise AssertionError("unexpected third candidate-selection schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("third selector evaluated downstream success")
    if payload["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("third pre-section carrier gained recursive authority")

    audit = payload["carrier_audit"]
    if audit["signature_cell_count"] != 562 or audit["context_count"] != 15120:
        raise AssertionError("future-free carrier scope drift")
    if audit["non_1_plus_1_cell_count"] != 381:
        raise AssertionError("non-1+1 cell count drift")
    if audit["preferred_1_plus_2_cell_count"] != 272:
        raise AssertionError("preferred 1+2 cell count drift")
    if audit["primary_distance_distribution"] != {"2": 12, "3": 95, "4": 129, "5": 36}:
        raise AssertionError("primary distance distribution drift")
    if audit["primary_tie_boundary_distance_distribution"] != {
        "1": 1,
        "2": 1,
        "3": 3,
        "4": 3,
        "5": 2,
    }:
        raise AssertionError("refined boundary distance distribution drift")

    candidate = payload["candidate"]
    if candidate["preferred_fusion"] != [1, 2] or not candidate["preferred_fusion_applied"]:
        raise AssertionError("preferred 1+2 rule drift")
    if candidate["primary_minimum_distance"] != 2:
        raise AssertionError("primary minimum distance drift")
    if candidate["primary_minimizer_count"] != 12:
        raise AssertionError("primary tie count drift")
    if candidate["primary_minimizer_context_count"] != 157:
        raise AssertionError("primary tie context count drift")
    if candidate["nonzero_surplus_minimizer_count"] != 10:
        raise AssertionError("nonzero-surplus tie count drift")
    if candidate["nonzero_surplus_context_count"] != 139:
        raise AssertionError("nonzero-surplus context count drift")
    if candidate["minimum_refined_boundary_distance"] != 1:
        raise AssertionError("refined boundary minimum drift")
    if candidate["refined_finalist_count"] != 1:
        raise AssertionError("third source-local selector is no longer unique")
    if candidate["selected_signature"] != EXPECTED_CANDIDATE_SIGNATURE:
        raise AssertionError("third candidate signature drift")
    if candidate["context_count"] != 36:
        raise AssertionError("third candidate context count drift")

    anatomy = payload["candidate_anatomy"]
    if anatomy["sigma6_word_distribution"] != {"001": 36}:
        raise AssertionError("third candidate Sigma_6 word distribution drift")
    if anatomy["sigma5_word_distribution"] != {"001": 36}:
        raise AssertionError("third candidate Sigma_5 word distribution drift")
    if anatomy["source_mass_placement_count"] != 6:
        raise AssertionError("third candidate source placement count drift")
    if anatomy["target_mass_placement_count"] != 12:
        raise AssertionError("third candidate target placement count drift")

    contexts = candidate["contexts"]
    if len({row["defect"] for row in contexts}) != 36:
        raise AssertionError("third candidate defects are not distinct")
    if any(row["carrier_signature"] != EXPECTED_CANDIDATE_SIGNATURE for row in contexts):
        raise AssertionError("third candidate row escaped the selected signature")

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
    parser.add_argument("--rule", type=Path, default=DEFAULT_RULE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.input, args.rule)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored third candidate selection differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected third candidate receipt schema")
    expected_receipt = build_receipt(
        input_path=args.input,
        rule_path=args.rule,
        output=args.artifact,
        payload=stored,
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
                "primary_minimizers": 12,
                "candidate_family": EXPECTED_CANDIDATE_SIGNATURE["family"],
                "candidate_contexts": 36,
                "section_authority": "NOT_GRANTED",
                "good_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
