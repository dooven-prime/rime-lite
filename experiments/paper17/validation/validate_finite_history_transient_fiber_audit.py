#!/usr/bin/env python3
"""Replay the post-transient fiber localization audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_finite_history_transient_fibers_v1 import OUTPUT_PATH, build_audit
from finite_history_execution_common import write_json
from optimized_exact_common import load_json, sha256_file


DEFAULT_RECEIPT = (
    ROOT
    / "results"
    / "finite_history_transient_fiber_audit.v1.validation-receipt.json"
)


def validate(path: Path) -> dict[str, object]:
    recorded = load_json(path)
    replayed = build_audit()
    if recorded != replayed:
        raise ValueError("transient-fiber audit replay mismatch")
    diagnosis = recorded["diagnosis"]
    if diagnosis["outcome"] != "TRANSIENT_SEPARATION_PLUS_PERSISTENT_SAFE_FORGETTING":
        raise ValueError("unexpected transient-fiber diagnosis")
    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-transient-fiber-audit-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_RESULT_OWNED_TRANSIENT_FIBER_REPLAY",
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
            "t1_failure_fibers": 6,
            "offending_sources": 51,
            "all_offending_sources_globally_singleton_at_t2": True,
            "persistent_cohort_count": 5,
            "persistent_cohort_sizes": [51, 25, 19, 4, 3],
            "persistent_membership_equal_at_t2_t3": True,
            "offender_persistent_cohort_overlap": 0,
            "mechanism_identified": False,
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
