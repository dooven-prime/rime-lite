#!/usr/bin/env python3
"""Validate tagged fixed-scope PEC component completion."""

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

import paper28_evaluate_pec_component_completion as evaluator


ARTIFACT = PARENT / "results" / "paper28_pec_component_completion_v1.json.gz"
RECEIPT = evaluator.default_receipt_path(ARTIFACT)
HISTORICAL = {
    "cand3": (
        PARENT
        / "results"
        / "paper28_third_rank4_section_return_evaluation_v1.json.gz"
    ),
    "cand4": (
        PARENT
        / "results"
        / "paper28_fourth_rank4_section_return_evaluation_v1.json.gz"
    ),
    "cand5": (
        PARENT
        / "results"
        / "paper28_fifth_rank4_section_return_evaluation_v1.json.gz"
    ),
}

EXPECTED_BY_CARRIER = {
    "cand3": {
        "source_count": 36,
        "PEC_supported_source_count": 36,
        "completed_source_count": 36,
        "hostile_source_count": 0,
        "channel_count": 172,
        "returning_channel_count": 171,
        "nonreturning_channel_count": 1,
        "mixed_channel_count": 63,
        "mixed_source_count": 27,
        "exact_lift_count": 5239,
        "local_return_exact_lift_count": 4208,
        "nonreturning_exact_lift_count": 1031,
        "certified_target_context_count": 624,
    },
    "cand4": {
        "source_count": 36,
        "PEC_supported_source_count": 36,
        "completed_source_count": 36,
        "hostile_source_count": 0,
        "channel_count": 252,
        "returning_channel_count": 252,
        "nonreturning_channel_count": 0,
        "mixed_channel_count": 38,
        "mixed_source_count": 15,
        "exact_lift_count": 6498,
        "local_return_exact_lift_count": 5937,
        "nonreturning_exact_lift_count": 561,
        "certified_target_context_count": 768,
    },
    "cand5": {
        "source_count": 10,
        "PEC_supported_source_count": 10,
        "completed_source_count": 10,
        "hostile_source_count": 0,
        "channel_count": 53,
        "returning_channel_count": 53,
        "nonreturning_channel_count": 0,
        "mixed_channel_count": 18,
        "mixed_source_count": 8,
        "exact_lift_count": 1476,
        "local_return_exact_lift_count": 1205,
        "nonreturning_exact_lift_count": 271,
        "certified_target_context_count": 174,
    },
}

EXPECTED_POOLED = {
    "source_count": 82,
    "PEC_supported_source_count": 82,
    "completed_source_count": 82,
    "hostile_source_count": 0,
    "channel_count": 477,
    "returning_channel_count": 476,
    "nonreturning_channel_count": 1,
    "mixed_channel_count": 119,
    "mixed_source_count": 50,
    "exact_lift_count": 13213,
    "local_return_exact_lift_count": 11350,
    "nonreturning_exact_lift_count": 1863,
    "certified_tagged_target_count": 1566,
}


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
    rebuilt = evaluator.build_payload(
        declaration_path=evaluator.DEFAULT_DECLARATION,
        projectability_path=evaluator.DEFAULT_PROJECTABILITY,
        carrier_specs=evaluator.CARRIER_SPECS,
    )
    if artifact != rebuilt:
        raise AssertionError("artifact does not equal deterministic reconstruction")
    if receipt["schema"] != evaluator.RECEIPT_SCHEMA:
        raise AssertionError("receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("receipt artifact hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("receipt content binding mismatch")
    if (
        receipt["artifact"]["frozen_completion_input_sha256"]
        != artifact["frozen_completion_input_sha256"]
    ):
        raise AssertionError("receipt completion-input binding mismatch")

    closure = {row["name"]: row["sha256"] for row in receipt["source_closure"]}
    expected_sources = {
        "paper28_evaluate_pec_component_completion.py": _sha256(
            PARENT / "paper28_evaluate_pec_component_completion.py"
        ),
        "validation/validate_paper28_pec_component_completion.py": _sha256(
            Path(__file__).resolve()
        ),
    }
    for name, digest in expected_sources.items():
        if closure.get(name) != digest:
            raise AssertionError(f"source closure mismatch for {name}")

    actual_carriers = {
        str(row["carrier_id"]): row
        for row in artifact["evaluation"]["carriers"]
    }
    if set(actual_carriers) != set(EXPECTED_BY_CARRIER):
        raise AssertionError("carrier evaluation domain drift")
    for carrier_id, expected in EXPECTED_BY_CARRIER.items():
        row = actual_carriers[carrier_id]
        for key, value in expected.items():
            if row[key] != value:
                raise AssertionError(f"{carrier_id} drift for {key}")
        if not row["theorem_holds"]:
            raise AssertionError(f"{carrier_id} theorem failed")

    pooled = artifact["evaluation"]["pooled"]
    for key, value in EXPECTED_POOLED.items():
        if pooled[key] != value:
            raise AssertionError(f"pooled drift for {key}")
    if len(pooled["G_PEC_pool"]) != 82:
        raise AssertionError("tagged PEC good-provenance union drift")
    if len(
        {
            (row["carrier_id"], row["context_id"], row["kappa_4_ISE_id"])
            for row in pooled["G_PEC_pool"]
        }
    ) != 82:
        raise AssertionError("tagged PEC good-provenance keys are not unique")
    if not artifact["theorem"]["holds"]:
        raise AssertionError("tagged PEC completion theorem failed")
    if artifact["scope"]["historical_Good4_artifacts_loaded"]:
        raise AssertionError("historical Good_4 entered the evaluator")
    if artifact["scope"]["rank5_return_evaluators_loaded"]:
        raise AssertionError("rank-five evaluator entered PEC completion")
    if artifact["scope"]["winner_selected"]:
        raise AssertionError("PEC completion selected a winner")

    forbidden_names = {
        name for name in artifact["forbidden_inputs"] if name.endswith(".json.gz")
    }
    receipt_names = {row["name"] for row in receipt["inputs"]}
    if forbidden_names & receipt_names:
        raise AssertionError("forbidden evaluator entered the artifact input list")

    # Historical Good_4 artifacts are used only now, after artifact equality and
    # receipt closure have been checked, as regression checksums.
    historical_regression = {}
    for carrier_id, path in HISTORICAL.items():
        historical = _load_gzip(path)["evaluation"]
        row = actual_carriers[carrier_id]
        comparisons = {
            "source_count": (row["completed_source_count"], historical["successful_source_count"]),
            "channel_count": (row["channel_count"], historical["channel_count"]),
            "returning_channel_count": (row["returning_channel_count"], historical["successful_channel_count"]),
            "nonreturning_channel_count": (row["nonreturning_channel_count"], historical["failed_channel_count"]),
            "exact_lift_count": (row["exact_lift_count"], historical["exact_lift_count"]),
            "local_return_exact_lift_count": (row["local_return_exact_lift_count"], historical["successful_exact_lift_count"]),
            "nonreturning_exact_lift_count": (row["nonreturning_exact_lift_count"], historical["unsuccessful_exact_lift_count"]),
            "certified_target_context_count": (row["certified_target_context_count"], historical["certified_target_context_count"]),
        }
        drift = {
            key: {"new": values[0], "historical": values[1]}
            for key, values in comparisons.items()
            if values[0] != values[1]
        }
        if drift:
            raise AssertionError(f"{carrier_id} historical regression drift: {drift}")
        historical_regression[carrier_id] = "PASS"

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "frozen_completion_input_sha256": artifact[
                    "frozen_completion_input_sha256"
                ],
                "theorem_holds": True,
                "by_carrier": EXPECTED_BY_CARRIER,
                "pooled": EXPECTED_POOLED,
                "historical_regression": historical_regression,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
