#!/usr/bin/env python3
"""Validate tagged fixed-scope GFPC component completion."""

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

import paper28_evaluate_gfpc_component_completion as evaluator

ARTIFACT = evaluator.DEFAULT_OUTPUT
RECEIPT = evaluator.default_receipt_path(ARTIFACT)
HISTORICAL_FPC = PARENT / "results" / "paper28_fpc_component_completion_v1.json.gz"
HISTORICAL_EXT = PARENT / "results" / "paper28_section_return_menu_audit_v1.json.gz"

EXPECTED_BY_CARRIER = {
    "cand2": {
        "source_count": 48,
        "GFPC_supported_source_count": 48,
        "completed_source_count": 48,
        "hostile_source_count": 0,
        "channel_count": 401,
        "returning_channel_count": 401,
        "nonreturning_channel_count": 0,
        "mixed_channel_count": 8,
        "mixed_source_count": 4,
        "exact_lift_count": 9600,
        "local_return_exact_lift_count": 9498,
        "nonreturning_exact_lift_count": 102,
        "certified_target_context_count": 1293,
    },
    "ext": {
        "source_count": 35,
        "GFPC_supported_source_count": 35,
        "completed_source_count": 35,
        "hostile_source_count": 0,
        "channel_count": 173,
        "returning_channel_count": 169,
        "nonreturning_channel_count": 4,
        "mixed_channel_count": 59,
        "mixed_source_count": 32,
        "exact_lift_count": 4182,
        "local_return_exact_lift_count": 2329,
        "nonreturning_exact_lift_count": 1853,
        "certified_target_context_count": 303,
    },
}

EXPECTED_POOLED = {
    "source_count": 83,
    "GFPC_supported_source_count": 83,
    "completed_source_count": 83,
    "hostile_source_count": 0,
    "channel_count": 574,
    "returning_channel_count": 570,
    "nonreturning_channel_count": 4,
    "mixed_channel_count": 67,
    "mixed_source_count": 36,
    "exact_lift_count": 13782,
    "local_return_exact_lift_count": 11827,
    "nonreturning_exact_lift_count": 1955,
    "certified_tagged_target_count": 1596,
}


def _load_gzip(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    artifact = _load_gzip(ARTIFACT)
    rebuilt = evaluator.build_payload(
        declaration_path=evaluator.DEFAULT_DECLARATION,
        carrier_specs=evaluator.CARRIER_SPECS,
    )
    if artifact != rebuilt:
        raise AssertionError("GFPC artifact differs from deterministic replay")
    if artifact["schema"] != evaluator.SCHEMA:
        raise AssertionError("GFPC completion schema drift")

    receipt = json.loads(RECEIPT.read_text(encoding="ascii"))
    if receipt["schema"] != evaluator.RECEIPT_SCHEMA:
        raise AssertionError("GFPC receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("GFPC receipt artifact hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("GFPC receipt content binding mismatch")
    if receipt["artifact"]["frozen_completion_input_sha256"] != artifact[
        "frozen_completion_input_sha256"
    ]:
        raise AssertionError("GFPC frozen-input receipt binding mismatch")

    closure = {row["name"]: row["sha256"] for row in receipt["source_closure"]}
    expected_sources = {
        "paper28_evaluate_gfpc_component_completion.py": _sha256(
            PARENT / "paper28_evaluate_gfpc_component_completion.py"
        ),
        "paper28_prepare_ext_rank4_section_candidate.py": _sha256(
            PARENT / "paper28_prepare_ext_rank4_section_candidate.py"
        ),
        "validation/validate_paper28_gfpc_component_completion.py": _sha256(
            Path(__file__).resolve()
        ),
    }
    for name, digest in expected_sources.items():
        if closure.get(name) != digest:
            raise AssertionError(f"source closure mismatch for {name}")

    carriers = {
        str(row["carrier_id"]): row
        for row in artifact["evaluation"]["carriers"]
    }
    if set(carriers) != set(EXPECTED_BY_CARRIER):
        raise AssertionError("GFPC carrier domain drift")
    for carrier_id, expected in EXPECTED_BY_CARRIER.items():
        row = carriers[carrier_id]
        for key, value in expected.items():
            if row[key] != value:
                raise AssertionError(f"{carrier_id} drift for {key}")
        if not row["theorem_holds"]:
            raise AssertionError(f"{carrier_id} GFPC theorem failed")

    pooled = artifact["evaluation"]["pooled"]
    for key, value in EXPECTED_POOLED.items():
        if pooled[key] != value:
            raise AssertionError(f"pooled GFPC drift for {key}")
    if len(pooled["G_GFPC_pool"]) != 83:
        raise AssertionError("tagged GFPC good-provenance union drift")
    if len(
        {
            (row["carrier_id"], row["context_id"], row["kappa_4_ISE_id"])
            for row in pooled["G_GFPC_pool"]
        }
    ) != 83:
        raise AssertionError("tagged GFPC provenance keys are not unique")
    if not artifact["theorem"]["holds"]:
        raise AssertionError("tagged GFPC completion theorem failed")

    scope = artifact["scope"]
    if scope["historical_FPC_completion_loaded"]:
        raise AssertionError("FPC completion entered the C3 proof input")
    if scope["historical_Good4_artifacts_loaded"]:
        raise AssertionError("historical Good_4 entered the C3 evaluator")
    if scope["rank5_return_evaluators_loaded"] or scope["winner_selected"]:
        raise AssertionError("rank-five success or winner entered C3")
    receipt_names = {row["name"] for row in receipt["inputs"]}
    forbidden_names = {
        name for name in artifact["forbidden_inputs"] if name.endswith(".json.gz")
    }
    if receipt_names & forbidden_names:
        raise AssertionError("forbidden completion/evaluator entered C3 inputs")

    # Historical outputs are opened only after deterministic artifact equality,
    # source closure, and theorem counts have all been checked.
    historical_fpc = _load_gzip(HISTORICAL_FPC)["evaluation"]
    cand2 = carriers["cand2"]
    fpc_pairs = {
        "source_count": (
            cand2["completed_source_count"],
            historical_fpc["completed_source_count"],
        ),
        "channel_count": (
            cand2["channel_count"],
            historical_fpc["channel_count"],
        ),
        "returning_channel_count": (
            cand2["returning_channel_count"],
            historical_fpc["returning_channel_count"],
        ),
        "exact_lift_count": (
            cand2["exact_lift_count"],
            historical_fpc["exact_lift_count"],
        ),
        "local_return_exact_lift_count": (
            cand2["local_return_exact_lift_count"],
            historical_fpc["local_return_exact_lift_count"],
        ),
    }
    if any(new != old for new, old in fpc_pairs.values()):
        raise AssertionError(f"cand2 historical FPC regression drift: {fpc_pairs}")

    historical_ext = _load_gzip(HISTORICAL_EXT)
    ext_history = historical_ext["success_certification"]
    ext = carriers["ext"]
    ext_pairs = {
        "source_count": (
            ext["completed_source_count"],
            historical_ext["future_free_menu"]["context_count"],
        ),
        "channel_count": (
            ext["channel_count"],
            historical_ext["future_free_menu"]["channel_count"],
        ),
        "returning_channel_count": (
            ext["returning_channel_count"],
            ext_history["successful_channel_count"],
        ),
        "nonreturning_channel_count": (
            ext["nonreturning_channel_count"],
            ext_history["failed_channel_count"],
        ),
        "exact_lift_count": (
            ext["exact_lift_count"],
            historical_ext["future_free_menu"]["exact_lift_count"],
        ),
        "local_return_exact_lift_count": (
            ext["local_return_exact_lift_count"],
            ext_history["successful_exact_lift_count"],
        ),
        "nonreturning_exact_lift_count": (
            ext["nonreturning_exact_lift_count"],
            ext_history["failed_exact_lift_count"],
        ),
        "certified_target_context_count": (
            ext["certified_target_context_count"],
            ext_history["certified_target_context_count"],
        ),
    }
    if any(new != old for new, old in ext_pairs.values()):
        raise AssertionError(f"ext historical regression drift: {ext_pairs}")

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
                "historical_regression": {
                    "cand2_FPC": "PASS_POST_FREEZE_ONLY",
                    "ext_Good4": "PASS_POST_FREEZE_ONLY",
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
