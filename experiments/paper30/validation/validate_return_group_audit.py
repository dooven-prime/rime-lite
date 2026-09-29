#!/usr/bin/env python3
"""Replay the paper-owned Paper XXX finite return-group audit."""

from __future__ import annotations

import json
import sys
from math import factorial
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER_ROOT = ROOT / "experiments" / "paper30"
RESULT_PATH = PAPER_ROOT / "results" / "general_defect_return_group_audit_v1.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper30" / "Paper XXX.md"
EXPECTED_MIN_N = 6
EXPECTED_MAX_N = 8
EXPECTED_NS = list(range(EXPECTED_MIN_N, EXPECTED_MAX_N + 1))

sys.path.insert(0, str(PAPER_ROOT))

from return_group_audit import SCHEMA, STATUS, build_result  # noqa: E402


def require_manuscript_boundary() -> None:
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    required = (
        "Theorem 3.1 (universal return-group theorem)",
        "Theorem 4.1 (exact relation-valued orbit reduction)",
        "Theorem 5.1 (punctured-rotation normal form)",
        "Theorem 6.2 (exact cycle-gluing theorem)",
        "Corollary 6.4 (fixed-collision branch fiber and exact gluing",
        "The retained finite audits are bounded consistency controls",
    )
    for marker in required:
        if marker not in manuscript:
            raise AssertionError(f"manuscript theorem or boundary missing: {marker}")


def main() -> int:
    retained = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    if retained.get("schema") != SCHEMA or retained.get("status") != STATUS:
        raise AssertionError("unexpected finite-audit schema or status")
    scope = retained.get("scope", {})
    if (scope.get("min_n"), scope.get("max_n")) != (
        EXPECTED_MIN_N,
        EXPECTED_MAX_N,
    ):
        raise AssertionError("retained finite-audit range drift")
    record_ns = [int(record["n"]) for record in retained.get("records", [])]
    if record_ns != EXPECTED_NS:
        raise AssertionError(f"retained record domain drift: {record_ns}")
    if retained.get("totals") != {
        "branch_completion_cases": 40200,
        "fixed_collision_fibers": 110,
    }:
        raise AssertionError("retained finite-audit totals drift")

    for record in retained["records"]:
        n = int(record["n"])
        deltas = record["deltas"]
        if [int(row["delta"]) for row in deltas] != list(range(1, n)):
            raise AssertionError(f"delta domain drift at n={n}")
        for row in deltas:
            for predicate in (
                "branch_completion_exact",
                "relative_return_exact",
                "cycle_gluing_exact",
                "fixed_collision_exact",
            ):
                if row.get(predicate) is not True:
                    raise AssertionError(f"{predicate} failed at n={n}")
            if int(row["branch_permutations"]) != factorial(n - 1):
                raise AssertionError(f"branch permutation count mismatch at n={n}")
            if int(row["fixed_collision_fiber_size"]) != factorial(n - 2):
                raise AssertionError(f"fixed-collision count mismatch at n={n}")

    replayed = build_result(EXPECTED_MIN_N, EXPECTED_MAX_N)
    if replayed != retained:
        raise AssertionError("retained result differs from fresh exact replay")
    require_manuscript_boundary()
    print(
        "PASS Paper XXX return-group audit: "
        "n=6..8, 40200 branch cases, 110 fixed-collision fibers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
