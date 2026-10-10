#!/usr/bin/env python3
"""Replay classification from the exact finite-history sidecar closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from finite_history_execution_common import (
    D0_PATH,
    RUNTIME_ROOT,
    load_scope_contract,
    resource_caps,
    verify_registration,
    write_json,
)
from optimized_exact_common import load_json, sha256_file
from run_finite_history_closure_v1 import _classify, _intern_observations


DEFAULT_RESULT = ROOT / "results" / "finite_history_closure.v1.json"
DEFAULT_RECEIPT = ROOT / "results" / "finite_history_closure.v1.validation-receipt.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(result_path: Path) -> dict[str, object]:
    verify_registration()
    scope, d0 = load_scope_contract()
    sources = [int(value) for value in d0]
    result = load_json(result_path)
    require(result["status"] == "COMPLETED", "result is not complete")
    require(result["run_id"] == "finite-history-v1", "run id mismatch")
    require(result["scope"]["source_count"] == 711, "source count mismatch")
    require(result["scope"]["H"] == 2 and result["scope"]["T"] == 4, "rectangle mismatch")
    require(not result["scope"]["D0_resized"], "D0 was resized")

    inventory_path = (ROOT / result["sidecar_inventory"]["path"]).resolve()
    require(inventory_path.is_relative_to(RUNTIME_ROOT.resolve()), "inventory escapes runtime root")
    require(inventory_path.stat().st_size == result["sidecar_inventory"]["bytes"], "inventory size mismatch")
    require(sha256_file(inventory_path) == result["sidecar_inventory"]["sha256"], "inventory digest mismatch")
    inventory = load_json(inventory_path)
    require(inventory["ordered_sources"] == sources, "inventory D0 ordering mismatch")
    require(len(inventory["shards"]) == 711, "shard count mismatch")
    run_root = inventory_path.parent
    for entry in inventory["shards"]:
        shard = run_root / entry["path"]
        metadata = run_root / entry["metadata_path"]
        require(shard.stat().st_size == entry["bytes"], f"shard size mismatch: {entry['source_id']}")
        require(sha256_file(shard) == entry["sha256"], f"shard digest mismatch: {entry['source_id']}")
        require(sha256_file(metadata) == entry["metadata_sha256"], f"metadata digest mismatch: {entry['source_id']}")

    sequences, replayed_observations, comparisons = _intern_observations(
        sources, run_root / "shards", 4
    )
    replayed = _classify(sources, sequences, 2, 4)
    require(replayed == result["classification"], "exact classification replay mismatch")
    require(
        replayed_observations == inventory["observation_inventory"],
        "observation inventory replay mismatch",
    )
    require(
        comparisons == inventory["exact_payload_comparisons_after_hash_match"],
        "exact payload comparison count mismatch",
    )
    caps = resource_caps()
    resources = result["resources"]
    require(resources["cumulative_wall_seconds"] <= caps["primary_wall_seconds"], "wall cap exceeded")
    require(resources["cumulative_cpu_seconds_sampled"] <= caps["primary_cpu_seconds"], "CPU cap exceeded")
    require(resources["peak_process_tree_rss_bytes"] <= caps["peak_process_tree_rss_bytes"], "RAM cap exceeded")
    require(resources["peak_incremental_storage_bytes"] <= caps["incremental_run_storage_bytes"], "storage cap exceeded")

    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_EXACT_SIDECAR_CLASSIFICATION_REPLAY",
        "independent_validation": False,
        "producer_replayed": False,
        "result": {
            "path": result_path.relative_to(ROOT).as_posix(),
            "bytes": result_path.stat().st_size,
            "sha256": sha256_file(result_path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "source_count": 711,
            "orders": [0, 1, 2],
            "exact_payload_comparison_after_hash_match": True,
            "classification_replayed": True,
            "resource_caps_satisfied": True,
            "D0_resized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    receipt = validate(args.result.resolve())
    if args.write_receipt:
        write_json(args.receipt.resolve(), receipt)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
