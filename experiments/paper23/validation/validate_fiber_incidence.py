#!/usr/bin/env python3
"""Validate fiber-incidence potential audit artifacts."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _bootstrap  # noqa: F401
from registry import payload_digest


def _fraction(value: dict[str, int] | None) -> Fraction | None:
    if value is None:
        return None
    return Fraction(value["numerator"], value["denominator"])


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("schema") != "rime.synchronizing-automata.fiber-incidence-potential-audit.v1":
        errors.append("schema mismatch")
    unsigned = dict(payload)
    digest = unsigned.pop("content_sha256", None)
    if digest != payload_digest(unsigned):
        errors.append("content digest mismatch")
    for row in payload.get("rows", []):
        if not row.get("local_descent_verified"):
            errors.append(f"local descent failed at {row.get('id')}")
        if not row.get("synchronizing"):
            continue
        phi = _fraction(row.get("phi_fiber_incidence"))
        psi = row.get("psi")
        slack = _fraction(row.get("fiber_incidence_slack"))
        if phi is None or psi is None or slack != phi - psi:
            errors.append(f"fiber-incidence slack mismatch at {row.get('id')}")
        if slack is not None and slack < 0:
            errors.append(f"fiber-incidence potential bound failed at {row.get('id')}")
    for summary in payload.get("summaries", []):
        if summary.get("local_descent_failures"):
            errors.append(f"summary reports local failures at n={summary.get('state_count')}")
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
    print(f"PASS FIBER-INCIDENCE-POTENTIAL: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
