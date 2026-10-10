#!/usr/bin/env python3
"""Run the read-only Paper XVII public-package validation surface."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUNTIME = {
    "python": "3.12.6",
    "numpy": "2.5.3",
    "gmpy2": "2.2.1",
}

RECEIPT_CHECKS = [
    ("validation/validate_result_anchor.py", "results/result-anchor.v1.validation-receipt.json"),
    ("validation/validate_finite_history_closure_freeze.py", "results/finite_history_closure.v1.freeze-validation-receipt.json"),
    ("validation/validate_finite_history_common_support_audit.py", "results/finite_history_common_support_audit.v1.validation-receipt.json"),
    ("validation/validate_finite_history_transient_fiber_audit.py", "results/finite_history_transient_fiber_audit.v1.validation-receipt.json"),
    ("validation/validate_finite_history_terminal_image_audit.py", "results/finite_history_terminal_image_audit.v1.validation-receipt.json"),
    ("validation/validate_manuscript_evidence_table.py", "results/manuscript-evidence-table.v1.validation-receipt.json"),
    (
        "mechanism/validation/validate_mts1_result_freeze_v1.py",
        "mechanism/results/mts1-v1.freeze-validation-receipt.json",
    ),
]

PLAIN_CHECKS = [
    "validation/test_finite_history_binary.py",
    "validation/test_finite_history_classification.py",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def installed_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError(f"missing required distribution: {distribution}") from exc


def run_check(relative: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        [sys.executable, str(ROOT / relative)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        process.returncode == 0,
        f"validation failed: {relative}\n"
        f"stdout:\n{process.stdout[-4000:]}\n"
        f"stderr:\n{process.stderr[-4000:]}",
    )
    return process


def main() -> int:
    observed = {
        "python": platform.python_version(),
        "numpy": installed_version("numpy"),
        "gmpy2": installed_version("gmpy2"),
    }
    require(observed == EXPECTED_RUNTIME, f"runtime mismatch: expected {EXPECTED_RUNTIME}, observed {observed}")

    child_env = dict(os.environ)
    child_env.pop("PYTHONOPTIMIZE", None)

    completed: list[str] = []
    validated_receipts: list[str] = []
    for relative, receipt_relative in RECEIPT_CHECKS:
        process = run_check(relative, child_env)
        try:
            replayed_receipt = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"validator did not emit one JSON receipt: {relative}") from exc
        receipt_path = ROOT / receipt_relative
        require(receipt_path.is_file(), f"missing retained receipt: {receipt_relative}")
        retained_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(
            retained_receipt == replayed_receipt,
            f"retained receipt does not match replay: {receipt_relative}",
        )
        completed.append(relative)
        validated_receipts.append(receipt_relative)

    for relative in PLAIN_CHECKS:
        run_check(relative, child_env)
        completed.append(relative)

    print(
        json.dumps(
            {
                "schema": "rime.paper17.public-package-read-only-validation.v1",
                "status": "PASS",
                "validation_mode": "LOCAL_RESULT_OWNED_EXACT_AND_COMPACT_MECHANISM_CLOSURE",
                "independent_validation": False,
                "producer_replayed": False,
                "runtime": observed,
                "completed_checks": completed,
                "check_count": len(completed),
                "validated_receipts": validated_receipts,
                "validated_receipt_count": len(validated_receipts),
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
