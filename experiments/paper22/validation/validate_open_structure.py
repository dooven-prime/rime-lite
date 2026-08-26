#!/usr/bin/env python3
"""Validate the Paper XXII precursor feature table without rerunning Paper XXI."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(payload: dict[str, Any]) -> str:
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "paper22.open-structure-feature-table.v1":
        errors.append("schema mismatch")
    if payload.get("claim_status") != "computational_observation":
        errors.append("claim status must remain computational_observation")
    if payload.get("content_sha256") != content_digest(payload):
        errors.append("content digest mismatch")
    depths = payload.get("scope", {}).get("depth_range", [])
    for section in ("uniformity", "growth", "arithmetic"):
        rows = payload.get(section, [])
        if [row.get("depth") for row in rows] != depths:
            errors.append(f"{section} depth range mismatch")
    for row in payload.get("growth", []):
        depth = int(row["depth"])
        expected = 3**depth * fibonacci(depth + 3)
        if row.get("candidate_count") != expected:
            errors.append(f"depth {depth}: candidate count mismatch")
        if row.get("generic_zero_count", -1) < 0 or row.get("generic_nonzero_count", -1) < 0:
            errors.append(f"depth {depth}: negative count")
    for row in payload.get("uniformity", []):
        if row.get("sample_status") == "MATCHED" and row.get("eligible_mismatches"):
            errors.append(f"depth {row.get('depth')}: matched status has mismatches")
    return errors


def fibonacci(index: int) -> int:
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    errors = validate(args.artifact)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS PAPER22-FEATURE-TABLE: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
