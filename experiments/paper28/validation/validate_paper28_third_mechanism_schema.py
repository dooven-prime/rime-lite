#!/usr/bin/env python3
"""Validate the P28.6u-A2 Pair-Extension Carry declaration."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import paper28_declare_third_mechanism_schema as declaration


ARTIFACT = (
    PARENT / "results" / "paper28_third_mechanism_schema_declaration_v1.json.gz"
)
RECEIPT = declaration.default_receipt_path(ARTIFACT)


def _load_gzip(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    artifact = _load_gzip(ARTIFACT)
    receipt = _load_json(RECEIPT)
    rebuilt = declaration.build_payload(input_path=declaration.DEFAULT_INPUT)
    if artifact != rebuilt:
        raise AssertionError("artifact does not equal deterministic reconstruction")
    if receipt["schema"] != declaration.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("receipt artifact hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("receipt content binding mismatch")
    if (
        receipt["artifact"]["common_profile_payload_sha256"]
        != artifact["unsupported_provenance_analysis"][
            "common_profile_payload_sha256"
        ]
    ):
        raise AssertionError("receipt common-profile binding mismatch")
    if receipt["source_closure"]["script"]["sha256"] != _sha256(
        PARENT / "paper28_declare_third_mechanism_schema.py"
    ):
        raise AssertionError("receipt source closure mismatch")

    summary = artifact["summary"]
    expected = {
        "unsupported_projectable_provenances": 82,
        "PEC_supported_provenances": 82,
        "expanded_family_supported_contexts": 82,
        "length_histogram": {"3": 72, "5": 10},
        "surplus_histogram": {"0": 10, "2": 72},
        "incoming_pair_role_histogram": {
            "CARRIED_PAIR": 36,
            "FUSED_PAIR": 46,
        },
        "incoming_participation_histogram": {"FIRST_ONLY": 46, "NONE": 36},
        "result": "THIRD_SCHEMA_DECLARED_AND_POOLED_SUPPORT_GAP_CLOSED",
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"summary drift for {key}")
    expected_by_carrier = {"cand3": 36, "cand4": 36, "cand5": 10}
    for carrier_id, count in expected_by_carrier.items():
        if summary["by_carrier"][carrier_id] != {
            "input_provenances": count,
            "PEC_supported_provenances": count,
        }:
            raise AssertionError(f"{carrier_id} support drift")
    if artifact["scope"]["success_evaluator_loaded"]:
        raise AssertionError("a success evaluator entered the declaration")
    if artifact["declaration"]["expanded_family"] != ["OW", "FPC", "PEC"]:
        raise AssertionError("expanded family drift")
    if not all(
        row["supported"] for row in artifact["declaration"]["support_rows"]
    ):
        raise AssertionError("PEC did not cover every pooled hostile provenance")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "common_profile_payload_sha256": artifact[
                    "unsupported_provenance_analysis"
                ]["common_profile_payload_sha256"],
                **expected,
                "by_carrier": expected_by_carrier,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
