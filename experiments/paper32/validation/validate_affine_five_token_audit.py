#!/usr/bin/env python3
"""Validate or replay the Paper XXXII bounded affine five-token audit."""

from __future__ import annotations

import argparse
import json
import sys
from math import factorial, gcd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = ROOT / "experiments" / "paper32"
RESULT_PATH = PACKAGE_ROOT / "results" / "affine_five_token_audit_v1.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper32" / "Paper XXXII.md"

SINGLE_MIN_N = 6
SINGLE_MAX_N = 12
PERMUTATION_MAX_N = 7
HOSTILE_MAX_N = 9

EXPECTED_SINGLE_TOTALS = {
    "delta_cells": 36,
    "identity_edges": 481680,
    "local_gap_transfer_checks": 147000,
    "state_cases": 53300,
    "unit_cells": 172,
}
EXPECTED_HOSTILE_TOTALS = {
    "branch_cells": 320,
    "delta_cells": 8,
    "intermediate_multiplier_cells": 0,
    "mixed_sign_multiplier_cells": 4,
    "multiplier_cells": 18,
    "same_multiplier_variation_cells": 0,
}
EXPECTED_PERMUTATION_TOTALS = {
    "branch_cells": 4560,
    "cycle_automorphism_cells": 92,
    "delta_cells": 8,
    "nonautomorphism_cells": 4468,
}
EXPECTED_CLAIM_BOUNDARY = [
    "finite replay is not the all-n proof",
    "the single-lane replay covers only the affine normalizer subfamily",
    "the full single-lane permutation theorem is proved in the manuscript",
    "the multi-lane scan does not prove multiplier descent or X3",
    "raw Safe-Hit does not imply survivor incidence or typed projectability",
]

sys.path.insert(0, str(PACKAGE_ROOT))

from affine_five_token_audit import SCHEMA, STATUS, build_result  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_single_lane(retained: dict[str, object]) -> None:
    block = retained["single_lane"]
    require(isinstance(block, dict), "single-lane result block is not an object")
    records = block["records"]
    require(isinstance(records, list), "single-lane records are not a list")
    require(
        [int(record["n"]) for record in records]
        == list(range(SINGLE_MIN_N, SINGLE_MAX_N + 1)),
        "single-lane n-domain drift",
    )
    for record in records:
        n = int(record["n"])
        expected_deltas = [delta for delta in range(1, n) if gcd(n, delta) == 1]
        deltas = record["deltas"]
        require(
            [int(row["delta"]) for row in deltas] == expected_deltas,
            f"single-lane delta-domain drift at n={n}",
        )
        for row in deltas:
            require(int(row["token_order_fibers"]) == 2, "token-order fiber count drift")
            require(
                sum(int(value) for value in row["token_order_fiber_sizes"])
                == int(row["states"]),
                "token-order fibers do not cover the state space",
            )
            require(
                int(row["local_gap_transfer_checks"]) > 0 or n == 6,
                "local gap transfer domain unexpectedly empty",
            )
            length = n - 1
            expected_units = [
                unit for unit in range(1, length) if gcd(unit, length) == 1
            ]
            units = row["units"]
            require(
                [int(unit["multiplier"]) for unit in units] == expected_units,
                f"unit-domain drift at n={n}, delta={row['delta']}",
            )
            for unit in units:
                multiplier = int(unit["multiplier"])
                dihedral = multiplier % length in {1, (-1) % length}
                require(unit["dihedral"] is dihedral, "dihedral flag drift")
                expected = "ADJ" if dihedral else "ALL"
                require(
                    unit["classification"] == expected,
                    f"single-lane dichotomy control failed at n={n}, "
                    f"delta={row['delta']}, u={multiplier}",
                )
    require(block["totals"] == EXPECTED_SINGLE_TOTALS, "single-lane totals drift")


def validate_hostile(retained: dict[str, object]) -> None:
    block = retained["multilane_hostile"]
    require(isinstance(block, dict), "hostile result block is not an object")
    records = block["records"]
    require(isinstance(records, list), "hostile records are not a list")
    require(
        [int(record["n"]) for record in records] == list(range(6, HOSTILE_MAX_N + 1)),
        "hostile n-domain drift",
    )
    for record in records:
        n = int(record["n"])
        expected_deltas = [delta for delta in range(1, n) if gcd(n, delta) > 1]
        deltas = record["deltas"]
        require(
            [int(row["delta"]) for row in deltas] == expected_deltas,
            f"hostile delta-domain drift at n={n}",
        )
        for delta_row in deltas:
            for multiplier in delta_row["multipliers"]:
                require(
                    set(multiplier["outcomes"]) <= {"ADJ", "SAME", "INTERMEDIATE"},
                    "unknown hostile outcome",
                )
                require(
                    int(multiplier["distinct_safe_hit_sets"])
                    == len(multiplier["witnesses"]),
                    "hostile witness count does not match distinct safe sets",
                )
                if multiplier["local_dihedral"]:
                    require(
                        multiplier["outcomes"] == ["ADJ"],
                        "mixed-sign lane-wise dihedral control failed",
                    )
    require(block["totals"] == EXPECTED_HOSTILE_TOTALS, "hostile totals drift")


def validate_permutation_control(retained: dict[str, object]) -> None:
    block = retained["single_lane_permutation_control"]
    require(isinstance(block, dict), "permutation result block is not an object")
    records = block["records"]
    require(isinstance(records, list), "permutation records are not a list")
    require(
        [int(record["n"]) for record in records]
        == list(range(6, PERMUTATION_MAX_N + 1)),
        "permutation n-domain drift",
    )
    for record in records:
        n = int(record["n"])
        expected_deltas = [delta for delta in range(1, n) if gcd(n, delta) == 1]
        deltas = record["deltas"]
        require(
            [int(row["delta"]) for row in deltas] == expected_deltas,
            f"permutation delta-domain drift at n={n}",
        )
        for row in deltas:
            length = n - 1
            require(int(row["branches"]) == factorial(length), "branch count drift")
            require(
                int(row["cycle_automorphisms"]) == 2 * length,
                "cycle automorphism count drift",
            )
            require(
                int(row["cycle_automorphisms"])
                + int(row["nonautomorphisms"])
                == int(row["branches"]),
                "permutation classes do not cover the branch fiber",
            )
    require(
        block["totals"] == EXPECTED_PERMUTATION_TOTALS,
        "permutation totals drift",
    )


def validate_manuscript_boundary() -> None:
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    normalized = " ".join(manuscript.split())
    for marker in (
        "Proposition 3.1 (lane-wise dihedral classification)",
        "Theorem 4.3 (single-lane order-fiber transitivity)",
        "Theorem 5.1 (single-lane permutation dichotomy)",
        "proper subfamily of the permutation theorem",
        "The finite audits are bounded consistency controls",
        "They are not proofs of the all-$n$ theorems",
        "a bounded absence of variation is not an all-$n$ descent theorem",
    ):
        require(marker in normalized, f"manuscript boundary missing: {marker}")


def validate_retained(retained: dict[str, object]) -> None:
    require(retained.get("schema") == SCHEMA, "finite schema mismatch")
    require(retained.get("status") == STATUS, "finite status mismatch")
    require(
        retained.get("claim_boundary") == EXPECTED_CLAIM_BOUNDARY,
        "finite claim boundary drift",
    )
    scope = retained.get("scope")
    require(isinstance(scope, dict), "scope is not an object")
    require(
        (
            scope.get("single_min_n"),
            scope.get("single_max_n"),
            scope.get("permutation_min_n"),
            scope.get("permutation_max_n"),
            scope.get("hostile_min_n"),
            scope.get("hostile_max_n"),
        )
        == (
            SINGLE_MIN_N,
            SINGLE_MAX_N,
            6,
            PERMUTATION_MAX_N,
            6,
            HOSTILE_MAX_N,
        ),
        "retained finite scope drift",
    )
    validate_single_lane(retained)
    validate_permutation_control(retained)
    validate_hostile(retained)
    validate_manuscript_boundary()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    retained = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    validate_retained(retained)
    if args.replay:
        recomputed = build_result(
            SINGLE_MIN_N,
            SINGLE_MAX_N,
            HOSTILE_MAX_N,
            PERMUTATION_MAX_N,
        )
        require(recomputed == retained, "recomputed finite result does not match retained JSON")
    mode = "replayed" if args.replay else "retained result checked"
    print(
        "PASS Paper XXXII affine five-token audit: "
        f"{mode}; {EXPECTED_SINGLE_TOTALS['unit_cells']} single-lane unit cells, "
        f"{EXPECTED_PERMUTATION_TOTALS['branch_cells']} permutation branches, "
        f"{EXPECTED_HOSTILE_TOTALS['branch_cells']} hostile branches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
