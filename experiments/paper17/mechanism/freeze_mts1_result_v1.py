#!/usr/bin/env python3
"""Freeze the completed MTS-1 result into a compact result-owned closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


MECHANISM_ROOT = Path(__file__).resolve().parent
REPO_ROOT = MECHANISM_ROOT.parents[2]
RESULT_ROOT = MECHANISM_ROOT / "results" / "mts1-v1"
INVENTORY_PATH = RESULT_ROOT / "inventory.json"
RESOURCE_RECEIPT_PATH = RESULT_ROOT / "resource-execution-receipt.json"
CLASSIFICATION_PATH = RESULT_ROOT / "validation" / "mechanism_classification.v1.json"
VALIDATION_RECEIPT_PATH = (
    RESULT_ROOT / "validation" / "mechanism_validation.v1.receipt.json"
)
AUTHORITY_PATH = MECHANISM_ROOT / "mechanism_mts1_execution_authority.v1.json"
AUTHORITY_RECEIPT_PATH = (
    MECHANISM_ROOT
    / "results"
    / "mechanism_mts1_execution_authority.v1.validation-receipt.json"
)
FREEZE_MANIFEST_PATH = MECHANISM_ROOT / "results" / "mts1-v1.freeze-manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def artifact(path: Path, role: str) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "role": role,
        "path": resolved.relative_to(REPO_ROOT).as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def ordered_closure_digest(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(
            (
                f"{entry['role']}\t{entry['path']}\t"
                f"{entry['bytes']}\t{entry['sha256']}\n"
            ).encode("ascii")
        )
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_freeze() -> dict[str, Any]:
    inventory = load_json(INVENTORY_PATH)
    resource_receipt = load_json(RESOURCE_RECEIPT_PATH)
    classification = load_json(CLASSIFICATION_PATH)
    validation_receipt = load_json(VALIDATION_RECEIPT_PATH)
    authority = load_json(AUTHORITY_PATH)
    authority_receipt = load_json(AUTHORITY_RECEIPT_PATH)

    require(
        inventory["status"]
        == "SOURCE_ADDRESSED_PRODUCTION_COMPLETE_AWAITING_EXHAUSTIVE_VALIDATION",
        "unexpected production inventory status",
    )
    require(resource_receipt["status"] == "PASS", "capped execution did not pass")
    require(resource_receipt["result_promoted"] is True, "result was not promoted")
    require(classification["status"] == "PASS", "classification did not pass")
    require(
        classification["outcome"] == "EXACT_TRANSITION_LAYER_LOCALIZATION",
        "unexpected MTS-1 outcome",
    )
    require(validation_receipt["status"] == "PASS", "result validation did not pass")
    require(
        validation_receipt["classification"]["sha256"]
        == sha256_file(CLASSIFICATION_PATH),
        "classification receipt binding mismatch",
    )
    require(
        validation_receipt["result_inventory"]["sha256"]
        == sha256_file(INVENTORY_PATH),
        "inventory receipt binding mismatch",
    )
    require(
        validation_receipt["verified"]["ordered_artifact_closure_sha256"]
        == inventory["ordered_artifact_closure_sha256"],
        "validated sidecar closure digest mismatch",
    )
    require(authority["status"] == "AUTHORIZED", "execution authority mismatch")
    require(authority_receipt["status"] == "PASS", "authority validation mismatch")
    require(
        authority_receipt["authority"]["sha256"] == sha256_file(AUTHORITY_PATH),
        "authority receipt binding mismatch",
    )

    sidecar_entries = inventory["ordered_artifacts"]
    sidecar_bytes = sum(int(entry["bytes"]) for entry in sidecar_entries)
    separators = classification["classification"]["exact_separators"]

    closure = [
        artifact(AUTHORITY_PATH, "EXECUTION_AUTHORITY"),
        artifact(AUTHORITY_RECEIPT_PATH, "EXECUTION_AUTHORITY_RECEIPT"),
        artifact(RESOURCE_RECEIPT_PATH, "CAPPED_EXECUTION_RECEIPT"),
        artifact(INVENTORY_PATH, "EXACT_SIDECAR_INVENTORY"),
        artifact(CLASSIFICATION_PATH, "VALIDATOR_DERIVED_CLASSIFICATION"),
        artifact(VALIDATION_RECEIPT_PATH, "EXHAUSTIVE_VALIDATION_RECEIPT"),
        artifact(
            MECHANISM_ROOT / "mechanism_nontrivial_contrast.registration-v1.json",
            "FROZEN_CONTRAST_POLICY",
        ),
        artifact(
            MECHANISM_ROOT / "run_mts1_source_production_capped_v1.py",
            "CAPPED_EXECUTION_RUNNER",
        ),
        artifact(
            MECHANISM_ROOT / "source_addressed_mechanism_producer_v1.py",
            "SOURCE_ADDRESSED_PRODUCER",
        ),
        artifact(
            MECHANISM_ROOT / "mechanism_result_validation_v1.py",
            "EXHAUSTIVE_RESULT_VALIDATOR",
        ),
        artifact(Path(__file__).resolve(), "RESULT_FREEZE_BUILDER"),
        artifact(
            MECHANISM_ROOT / "validation" / "validate_mts1_result_freeze_v1.py",
            "RESULT_FREEZE_VALIDATOR",
        ),
    ]

    return {
        "schema": "rime.paper17.mts1-result-freeze-manifest.v1",
        "status": "POST_EXECUTION_FROZEN",
        "execution_authority": "NONE_COMPLETED",
        "evidence_level": "Computational Certificate",
        "validation_mode": "LOCAL_EXHAUSTIVE_EXACT_REDERIVATION",
        "independent_validation": False,
        "producer_replayed_by_validator": False,
        "primary_result": {
            "outcome": classification["outcome"],
            "source_count": inventory["source_count"],
            "source_transition_cache_record_count": inventory[
                "source_transition_cache_record_count"
            ],
            "pair_count": inventory["pair_count"],
            "pair_transition_record_count": inventory[
                "pair_transition_record_count"
            ],
            "comparison_cell_count": classification["classification"][
                "comparison_cell_count"
            ],
            "differing_comparison_cell_count": classification["classification"][
                "differing_comparison_cell_count"
            ],
            "exact_separators": separators,
        },
        "exact_sidecar_identity": {
            "storage_role": "LOCAL_RESULT_SIDECAR",
            "artifact_count": len(sidecar_entries),
            "total_bytes": sidecar_bytes,
            "inventory_sha256": sha256_file(INVENTORY_PATH),
            "ordered_artifact_closure_sha256": inventory[
                "ordered_artifact_closure_sha256"
            ],
            "all_pair_records_byte_equal_rederivation": validation_receipt[
                "verified"
            ]["all_pair_records_byte_equal_rederivation"],
            "external_immutable_anchor": None,
            "tracked_in_git": False,
        },
        "artifact_closure": closure,
        "ordered_compact_closure_sha256": ordered_closure_digest(closure),
        "claim_boundary": {
            "declared_finite_cohorts_and_transition_grid_only": True,
            "external_world_input": "NONE",
            "statistical_inference": "NONE",
            "causal_attribution": "NONE",
            "quadrant_labels_are_mechanism_labels": False,
            "identity_layer_replay_is_mechanism_finding": False,
            "independent_replication_claimed": False,
            "population_prevalence_claimed": False,
            "external_sidecar_durability_claimed": False,
        },
    }


def main() -> int:
    manifest = build_freeze()
    write_json(FREEZE_MANIFEST_PATH, manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "outcome": manifest["primary_result"]["outcome"],
                "sidecar": manifest["exact_sidecar_identity"],
                "manifest": str(FREEZE_MANIFEST_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
