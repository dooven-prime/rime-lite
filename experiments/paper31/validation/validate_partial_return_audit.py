#!/usr/bin/env python3
"""Replay the paper-owned Paper XXXI bounded hostile audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER_ROOT = ROOT / "experiments" / "paper31"
RESULT_PATH = PAPER_ROOT / "results" / "partial_return_hostile_audit_v1.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper31" / "Paper XXXI.md"
CYCLIC_MIN_N = 6
CYCLIC_MAX_N = 12
NORMALIZER_MAX_N = 8

EXPECTED_CYCLIC_TOTALS = {
    "enabled_labelled_edges": 870540,
    "state_cases": 93720,
}
EXPECTED_NORMALIZER_TOTALS = {
    "normalizer_branches": 456,
    "orientation_compatible_state_cases": 36760,
    "quotient_edges_checked": 175216,
    "state_cases": 70560,
}

sys.path.insert(0, str(PAPER_ROOT))

from partial_return_audit import SCHEMA, STATUS, build_result  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_records(retained: dict[str, object]) -> None:
    cyclic = retained["cyclic_branch"]
    if not isinstance(cyclic, dict):
        raise RuntimeError("cyclic result block is not an object")
    cyclic_records = cyclic["records"]
    if not isinstance(cyclic_records, list):
        raise RuntimeError("cyclic records are not a list")
    require(
        [int(record["n"]) for record in cyclic_records]
        == list(range(CYCLIC_MIN_N, CYCLIC_MAX_N + 1)),
        "cyclic n-domain drift",
    )
    for record in cyclic_records:
        n = int(record["n"])
        deltas = record["deltas"]
        require(
            [int(row["delta"]) for row in deltas] == list(range(1, n)),
            f"cyclic delta-domain drift at n={n}",
        )
        for row in deltas:
            require(row["safe_hit_equals_lane_adjacency"] is True, "N3 control failed")
            require(row["lane_adjacency_edge_invariant"] is True, "N3.1 control failed")

    normalizer = retained["normalizer_branch"]
    if not isinstance(normalizer, dict):
        raise RuntimeError("normalizer result block is not an object")
    normalizer_records = normalizer["records"]
    if not isinstance(normalizer_records, list):
        raise RuntimeError("normalizer records are not a list")
    require(
        [int(record["n"]) for record in normalizer_records]
        == list(range(6, NORMALIZER_MAX_N + 1)),
        "normalizer n-domain drift",
    )
    predicates = (
        "skew_relation_exact",
        "target_orbit_exact",
        "quotient_reachability_exact",
        "normalizer_sandwich_exact",
        "orientation_compatible_exact",
    )
    for record in normalizer_records:
        n = int(record["n"])
        deltas = record["deltas"]
        require(
            [int(row["delta"]) for row in deltas] == list(range(1, n)),
            f"normalizer delta-domain drift at n={n}",
        )
        for row in deltas:
            for predicate in predicates:
                require(row[predicate] is True, f"{predicate} failed at n={n}")


def require_manuscript_boundary() -> None:
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    for marker in (
        "Theorem 2.1 (branch-normalized full return dynamics; N1)",
        "Theorem 3.1 (cyclic-branch exponent elimination; N2)",
        "Theorem 4.3 (multi-lane Safe-Hit classification; N3)",
        "Theorem 5.1 (normalizer skew-orbit reduction; N4.1)",
        "Theorem 6.3 (orientation-compatible normalizer classification; N4.5)",
        "bounded consistency and formalization controls",
        "independent Computational Certificates",
    ):
        require(marker in manuscript, f"manuscript marker missing: {marker}")


def main() -> int:
    retained = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    require(retained.get("schema") == SCHEMA, "finite schema mismatch")
    require(retained.get("status") == STATUS, "finite status mismatch")
    scope = retained.get("scope", {})
    require(
        (
            scope.get("cyclic_min_n"),
            scope.get("cyclic_max_n"),
            scope.get("normalizer_min_n"),
            scope.get("normalizer_max_n"),
        )
        == (CYCLIC_MIN_N, CYCLIC_MAX_N, 6, NORMALIZER_MAX_N),
        "retained finite scope drift",
    )
    require(retained["cyclic_branch"]["totals"] == EXPECTED_CYCLIC_TOTALS, "cyclic totals drift")
    require(
        retained["normalizer_branch"]["totals"] == EXPECTED_NORMALIZER_TOTALS,
        "normalizer totals drift",
    )
    validate_records(retained)
    replayed = build_result(CYCLIC_MIN_N, CYCLIC_MAX_N, NORMALIZER_MAX_N)
    require(replayed == retained, "retained result differs from fresh exact replay")
    require_manuscript_boundary()
    print(
        "PASS Paper XXXI hostile audit: "
        "93720 cyclic states, 870540 cyclic edges, "
        "456 normalizers, 70560 normalizer state cases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
