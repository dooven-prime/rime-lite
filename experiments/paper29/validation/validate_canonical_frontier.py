#!/usr/bin/env python3
"""Replay the paper-owned Paper XXIX finite canonical-frontier audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER_ROOT = ROOT / "experiments" / "paper29"
RESULT_PATH = PAPER_ROOT / "results" / "canonical_frontier_audit_v1.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper29" / "Paper XXIX.md"
EXPECTED_MIN_N = 5
EXPECTED_MAX_N = 12
EXPECTED_NS = list(range(EXPECTED_MIN_N, EXPECTED_MAX_N + 1))

sys.path.insert(0, str(PAPER_ROOT))

from canonical_frontier import SCHEMA, STATUS, build_result  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result",
        type=Path,
        default=RESULT_PATH,
        help="retained result to compare with a fresh replay",
    )
    return parser.parse_args()


def require_manuscript_boundary() -> None:
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    required = (
        "Theorem 5.4 (all-$n$ canonical spectator-safe classification)",
        "Theorem 6.2 (canonical survivor and frontier classification)",
    )
    for text in required:
        if text not in manuscript:
            raise AssertionError(f"manuscript theorem surface missing: {text}")
    if "Finite graph searches used during development are sanity checks" not in manuscript:
        raise AssertionError("manuscript finite-check boundary is missing")


def validate_record(record: dict[str, object]) -> None:
    n = int(record["n"])
    predicates = (
        "safe_hit_equals_omega_adjacency",
        "order_fiber_strongly_connected",
        "boundary_spectrum_exact",
    )
    for predicate in predicates:
        if record[predicate] is not True:
            raise AssertionError(f"{predicate} failed at n={n}")
    if n >= 6:
        if record["r1_identity"] is not True or record["r2_cycle"] is not True:
            raise AssertionError(f"section symmetry failed at n={n}")
    if record["configuration_states"] != record["predicted_configuration_states"]:
        raise AssertionError(f"configuration count mismatch at n={n}")
    if record["order_fiber_states"] != record["predicted_order_fiber_states"]:
        raise AssertionError(f"order-fiber count mismatch at n={n}")
    if record["boundary_incidence_count"] != record["predicted_boundary_incidence_count"]:
        raise AssertionError(f"boundary count mismatch at n={n}")


def main() -> int:
    args = parse_args()
    retained = json.loads(args.result.read_text(encoding="utf-8"))
    if retained.get("schema") != SCHEMA or retained.get("status") != STATUS:
        raise AssertionError("unexpected result schema or status")
    scope = retained["scope"]
    min_n = int(scope["min_n"])
    max_n = int(scope["max_n"])
    if (min_n, max_n) != (EXPECTED_MIN_N, EXPECTED_MAX_N):
        raise AssertionError(
            "retained audit range changed: "
            f"expected {EXPECTED_MIN_N}..{EXPECTED_MAX_N}, got {min_n}..{max_n}"
        )
    record_ns = [int(record["n"]) for record in retained["records"]]
    if record_ns != EXPECTED_NS:
        raise AssertionError(
            f"retained record domain changed: expected {EXPECTED_NS}, got {record_ns}"
        )
    replayed = build_result(EXPECTED_MIN_N, EXPECTED_MAX_N)
    if replayed != retained:
        raise AssertionError("retained result differs from fresh exact replay")
    control = retained["coarse_non_descent_control"]
    if control["frontiers_disjoint"] is not True:
        raise AssertionError("coarse non-descent control failed")
    for record in retained["records"]:
        validate_record(record)
    require_manuscript_boundary()
    print(
        "PASS Paper XXIX canonical raw audit: "
        f"n={min_n}..{max_n}, no private source dependency"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
