#!/usr/bin/env python3
"""Replay and validate the binary clean-corridor exhaustion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import _bootstrap  # noqa: F401
from enumerate_binary_clean_corridors import build_certificate
from registry import payload_digest


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if payload.get("schema") != (
        "rime.synchronizing-automata.binary-clean-exhaustion.v1"
    ):
        errors.append("schema mismatch")
    unsigned = dict(payload)
    digest = unsigned.pop("content_sha256", None)
    if digest != payload_digest(unsigned):
        errors.append("content digest mismatch")
    maximum = payload.get("scope", {}).get("maximum_state_count")
    if isinstance(maximum, int):
        if build_certificate(maximum) != payload:
            errors.append("exhaustive replay mismatch")
    else:
        errors.append("invalid maximum state count")
    for row in payload.get("rows", []):
        n = row["state_count"]
        if row.get("one_wait_theorem_failure_count"):
            errors.append(f"one-wait theorem failed at n={n}")
        expected_extremal = 1 if n == 2 else n
        if row.get("theorem_extremal_reset_depth") != expected_extremal:
            errors.append(f"extremal theorem field mismatch at n={n}")
        if not row.get("theorem_extremal_depth_verified"):
            errors.append(f"extremal theorem verification failed at n={n}")
        if not row.get("candidate_n_bound_holds_in_enumeration"):
            errors.append(f"candidate n bound failed at n={n}")
        if n >= 3:
            witness = row.get("explicit_depth_n_witness")
            if witness is None or witness.get("reset_depth") != n:
                errors.append(f"explicit depth-n witness failed at n={n}")
    return errors


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
    print(f"PASS BINARY-CLEAN-EXHAUSTION: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
