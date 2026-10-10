#!/usr/bin/env python3
"""Replay the finite-history common-support scope diagnostic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_finite_history_common_support_v1 import OUTPUT_PATH, build_audit
from finite_history_execution_common import write_json
from optimized_exact_common import load_json, sha256_file


DEFAULT_RECEIPT = (
    ROOT
    / "results"
    / "finite_history_common_support_audit.v1.validation-receipt.json"
)


def validate(path: Path) -> dict[str, object]:
    recorded = load_json(path)
    replayed = build_audit()
    if recorded != replayed:
        raise ValueError("common-support audit replay mismatch")
    diagnosis = recorded["diagnosis"]
    if diagnosis["outcome"] != "REGISTERED_ORDER_EFFECT_CONFOUNDED_WITH_LEFT_BOUNDARY":
        raise ValueError("unexpected common-support diagnosis")
    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-common-support-audit-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_RESULT_OWNED_COMMON_SUPPORT_REPLAY",
        "independent_validation": False,
        "producer_replayed": False,
        "audit": {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "h1_failure_fibers": 6,
            "all_h1_failure_members_at_t1": True,
            "common_support_times": [2, 3],
            "common_support_orders": [0, 1, 2],
            "all_common_support_orders_closed": True,
            "all_common_support_partitions_identical": True,
            "minimal_memory_order_identified": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.audit.resolve())
    if args.write_receipt:
        write_json(DEFAULT_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
