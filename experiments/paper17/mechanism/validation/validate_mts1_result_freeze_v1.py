#!/usr/bin/env python3
"""Validate the compact post-execution MTS-1 result freeze."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MECHANISM_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MECHANISM_ROOT))

from freeze_mts1_result_v1 import (  # noqa: E402
    FREEZE_MANIFEST_PATH,
    REPO_ROOT,
    build_freeze,
    load_json,
    ordered_closure_digest,
    sha256_file,
    write_json,
)


DEFAULT_RECEIPT = (
    MECHANISM_ROOT / "results" / "mts1-v1.freeze-validation-receipt.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    expected = build_freeze()
    require(manifest == expected, "freeze manifest does not match deterministic replay")
    require(manifest["status"] == "POST_EXECUTION_FROZEN", "freeze status mismatch")
    require(
        manifest["execution_authority"] == "NONE_COMPLETED",
        "completed authority state mismatch",
    )
    roles = [entry["role"] for entry in manifest["artifact_closure"]]
    require(len(roles) == len(set(roles)), "duplicate compact closure role")
    for entry in manifest["artifact_closure"]:
        artifact_path = REPO_ROOT / entry["path"]
        require(artifact_path.is_file(), f"missing closure artifact: {entry['path']}")
        require(
            artifact_path.stat().st_size == entry["bytes"],
            f"closure artifact size mismatch: {entry['path']}",
        )
        require(
            sha256_file(artifact_path) == entry["sha256"],
            f"closure artifact digest mismatch: {entry['path']}",
        )
    require(
        ordered_closure_digest(manifest["artifact_closure"])
        == manifest["ordered_compact_closure_sha256"],
        "ordered compact closure digest mismatch",
    )
    result = manifest["primary_result"]
    require(
        result["outcome"] == "EXACT_TRANSITION_LAYER_LOCALIZATION",
        "unexpected frozen scientific outcome",
    )
    require(result["source_count"] == 153, "source count mismatch")
    require(result["source_transition_cache_record_count"] == 459, "cache count mismatch")
    require(result["pair_count"] == 2325, "pair count mismatch")
    require(result["pair_transition_record_count"] == 6975, "record count mismatch")
    require(result["comparison_cell_count"] == 15, "comparison cell count mismatch")
    require(result["differing_comparison_cell_count"] == 15, "differing cell count mismatch")
    require(len(result["exact_separators"]) == 4, "exact separator count mismatch")

    return {
        "schema": "rime.paper17.mts1-result-freeze-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_COMPACT_CLOSURE_VERIFICATION",
        "independent_validation": False,
        "producer_replayed": False,
        "scientific_classification_replayed": False,
        "freeze_manifest": {
            "path": path.resolve().relative_to(REPO_ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "outcome": result["outcome"],
            "source_count": 153,
            "source_transition_cache_record_count": 459,
            "pair_transition_record_count": 6975,
            "comparison_cell_count": 15,
            "exact_separator_count": 4,
            "ordered_compact_closure_sha256": manifest[
                "ordered_compact_closure_sha256"
            ],
            "exact_sidecar_inventory_bound": True,
            "exact_sidecar_bytes_rehashed_during_freeze": False,
            "prior_exhaustive_validation_receipt_bound": True,
            "external_immutable_sidecar_anchor": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=FREEZE_MANIFEST_PATH)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.manifest.resolve())
    if args.write_receipt:
        write_json(DEFAULT_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
