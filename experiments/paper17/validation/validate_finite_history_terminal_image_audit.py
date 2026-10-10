#!/usr/bin/env python3
"""Replay the Paper XVII terminal-image boundary audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_finite_history_terminal_image_v1 import OUTPUT_PATH, build_audit
from finite_history_execution_common import write_json
from optimized_exact_common import load_json, sha256_file


DEFAULT_RECEIPT = (
    ROOT
    / "results"
    / "finite_history_terminal_image_audit.v1.validation-receipt.json"
)


def validate(path: Path) -> dict[str, object]:
    recorded = load_json(path)
    replayed = build_audit()
    if recorded != replayed:
        raise ValueError("terminal-image audit replay mismatch")

    profile = recorded["exact_image_profile"]
    classification = recorded["classification"]
    if profile["distinct_observations_by_time"] != {"2": 614, "3": 614, "4": 614}:
        raise ValueError("unexpected exact image cardinalities")
    if profile["t4_intersection_with_common_image_size"] != 0:
        raise ValueError("terminal image unexpectedly returns to common image")
    if classification["coarse_endomap_on_common_image_verified"]:
        raise ValueError("coarse endomap was silently promoted")

    return {
        "schema": "rime.paper17.finite-history-terminal-image-audit-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_RESULT_OWNED_TERMINAL_IMAGE_REPLAY",
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
            "distinct_observations_by_time": profile[
                "distinct_observations_by_time"
            ],
            "common_image_size": profile["common_image_size"],
            "registered_internal_shift_count": classification[
                "registered_internal_shift_count"
            ],
            "t4_intersection_with_common_image_size": profile[
                "t4_intersection_with_common_image_size"
            ],
            "coarse_endomap_on_common_image_verified": False,
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
