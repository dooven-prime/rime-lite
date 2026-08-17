#!/usr/bin/env python3
"""Replay the Paper VIII v2.1 exact finite-realization promotion."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    ROOT
    / "experiments"
    / "paper8"
    / "validation"
    / "validate_marked_finite_realizations_v2_1.py"
)
CERTIFICATE = (
    ROOT
    / "experiments"
    / "paper8"
    / "results"
    / "v2.1"
    / "marked_finite_realization_conformance_v2_1.json"
)
RECEIPT = CERTIFICATE.with_name(
    "marked_finite_realization_conformance_v2_1.validation-receipt.json"
)


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(CERTIFICATE)],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise AssertionError("Paper VIII finite-realization replay failed")
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert certificate["artifact_id"] == "P8V2.1-CONFORMANCE"
    assert receipt["artifact_id"] == "P8V2.1-REPLAY"
    assert receipt["status"] == "PASS"
    assert receipt["certificate"]["content_sha256"] == certificate[
        "content_sha256"
    ]
    print("Paper VIII v2.1 finite-realization replay passed.")


if __name__ == "__main__":
    main()
