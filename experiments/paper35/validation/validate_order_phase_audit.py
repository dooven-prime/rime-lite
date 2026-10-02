#!/usr/bin/env python3
"""Validate and optionally replay the Paper XXXV six-point theorem control."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper35"
PRODUCER = PACKAGE / "order_phase_audit.py"
RESULT = PACKAGE / "results" / "order_phase_n6_v2.json"
README = PACKAGE / "README.md"

SCHEMA = "rime.paper35.order-phase-audit.v2"
STATUS = "EXHAUSTIVE_N6_PHASE_COLLAPSE_CONTROL"
EXPECTED_SCOPE = {
    "n": 6,
    "delta": 1,
    "source": [1, 2, 3, 4, 5],
    "branch_permutations": 120,
    "lineage_bijections": 120,
    "cyclic_orders": 24,
    "formal_terminal_placements": 480,
    "complete_branch_scan": True,
}
EXPECTED_PATTERNS = [
    ("P0", [0, 1, 2, 3, 4], 5, 5, 24, "C5", 5, 5, 1, 20, 5),
    ("P1", [0, 1, 2, 4, 3], 25, 25, 120, "S5", 120, 120, 24, 480, 10),
    ("P2", [0, 1, 3, 4, 2], 25, 25, 120, "A5", 60, 60, 12, 240, 10),
    ("P3", [0, 1, 4, 3, 2], 25, 25, 120, "S5", 120, 120, 24, 480, 10),
    ("P4", [0, 2, 1, 4, 3], 25, 25, 120, "A5", 60, 60, 12, 240, 10),
    ("P5", [0, 2, 4, 1, 3], 5, 5, 24, "F20", 20, 20, 4, 80, 10),
    ("P6", [0, 3, 1, 4, 2], 5, 5, 24, "F20", 20, 20, 4, 80, 10),
    ("P7", [0, 4, 3, 2, 1], 5, 5, 24, "D10", 10, 10, 2, 40, 5),
]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing file: {path.relative_to(ROOT).as_posix()}")
        return ""
    raw = path.read_bytes()
    require(b"\r" not in raw, f"non-LF text artifact: {path.name}", errors)
    require(b"\x00" not in raw, f"NUL byte in text artifact: {path.name}", errors)
    return raw.decode("utf-8")


def validate_patterns(rows: object, errors: list[str]) -> None:
    require(isinstance(rows, list), "pattern rows missing", errors)
    if not isinstance(rows, list):
        return
    require(len(rows) == 8, "pattern-row count drift", errors)
    for row, expected in zip(rows, EXPECTED_PATTERNS, strict=False):
        require(isinstance(row, dict), "malformed pattern row", errors)
        if not isinstance(row, dict):
            continue
        (
            pattern_id,
            representative,
            double_coset_size,
            branch_count,
            relation_edges,
            subgroup_name,
            subgroup_order,
            reachable_injections,
            reachable_orders,
            phase_witnesses,
            hittable_pairs,
        ) = expected
        require(row.get("pattern_id") == pattern_id, f"{pattern_id} id drift", errors)
        require(
            row.get("representative") == representative,
            f"{pattern_id} representative drift",
            errors,
        )
        require(
            row.get("double_coset_size") == double_coset_size,
            f"{pattern_id} double-coset size drift",
            errors,
        )
        require(row.get("branch_count") == branch_count, f"{pattern_id} branch count drift", errors)
        require(row.get("relation_edges") == relation_edges, f"{pattern_id} edge count drift", errors)
        require(row.get("distinct_phase_signatures") == 1, f"{pattern_id} phase descent drift", errors)
        require(row.get("distinct_survivor_signatures") == 1, f"{pattern_id} survivor descent drift", errors)
        require(row.get("generated_subgroup_names") == [subgroup_name], f"{pattern_id} subgroup name drift", errors)
        require(row.get("generated_subgroup_orders") == [subgroup_order], f"{pattern_id} subgroup order drift", errors)
        require(row.get("reachable_injection_counts") == [reachable_injections], f"{pattern_id} injection reachability drift", errors)
        require(row.get("reachable_order_counts") == [reachable_orders], f"{pattern_id} order reachability drift", errors)
        require(row.get("phase_witness_counts") == [phase_witnesses], f"{pattern_id} phase count drift", errors)
        require(row.get("hittable_pair_counts") == [hittable_pairs], f"{pattern_id} pair count drift", errors)


def validate_result(result: dict[str, object], errors: list[str]) -> None:
    require(result.get("schema") == SCHEMA, "schema mismatch", errors)
    require(result.get("status") == STATUS, "status mismatch", errors)
    require(result.get("scope") == EXPECTED_SCOPE, "scope drift", errors)

    grouping = result.get("double_coset_control")
    require(isinstance(grouping, dict), "double-coset control missing", errors)
    if isinstance(grouping, dict):
        require(grouping.get("group") == "C5\\S5/C5", "group label drift", errors)
        require(grouping.get("pattern_classes") == 8, "pattern class count drift", errors)
        require(grouping.get("branch_class_sizes") == [5, 5, 5, 5, 25, 25, 25, 25], "branch grouping drift", errors)
        require(grouping.get("order_orbital_edge_sizes") == [24, 24, 24, 24, 120, 120, 120, 120], "orbital edge-size drift", errors)
        require(grouping.get("normalizer_order") == 20, "normalizer order drift", errors)
        require(grouping.get("singleton_pattern_per_branch") is True, "singleton-pattern property failed", errors)
        require(grouping.get("status") == "EXACT_EIGHT_ORBITAL_GROUPING_CONTROL", "grouping status drift", errors)

    checks = result.get("exact_reduction_checks")
    require(isinstance(checks, dict), "exact reduction checks missing", errors)
    if isinstance(checks, dict):
        require(checks and all(value is True for value in checks.values()), "an exact reduction check failed", errors)

    validate_patterns(result.get("pattern_classes"), errors)

    branches = result.get("branch_rows")
    require(isinstance(branches, list), "branch rows missing", errors)
    if isinstance(branches, list):
        require(len(branches) == 120, "branch-row count drift", errors)
        actual_branches = {
            tuple(row.get("branch", [])) for row in branches if isinstance(row, dict)
        }
        require(actual_branches == set(permutations(range(1, 6))), "branch fiber is not complete", errors)
        for row in branches:
            if not isinstance(row, dict):
                errors.append("malformed branch row")
                continue
            require(row.get("formal_terminal_placements") == 480, "terminal-placement scope drift", errors)
            for flag in (
                "order_fiber_saturation",
                "order_reachability_exact",
                "pattern_reconstruction_exact",
                "terminal_realization_exact",
                "order_phase_bijection_exact",
                "phase_collapse_exact",
                "survivor_count_formula_exact",
            ):
                require(row.get(flag) is True, f"branch failed {flag}", errors)
            multiplicities = row.get("survivor_order_multiplicities")
            sizes = row.get("survivor_spectrum_sizes")
            require(isinstance(multiplicities, dict), "survivor multiplicities missing", errors)
            require(isinstance(sizes, dict), "survivor sizes missing", errors)
            if isinstance(multiplicities, dict) and isinstance(sizes, dict):
                require(set(multiplicities) == set(sizes), "survivor pair keys drift", errors)
                require(
                    all(sizes[key] == 4 * multiplicities[key] for key in sizes),
                    "survivor count formula drift",
                    errors,
                )
            require(
                row.get("generated_subgroup_name")
                in {"C5", "D10", "F20", "A5", "S5"},
                "branch subgroup name drift",
                errors,
            )
            require(
                row.get("generated_subgroup_order") in {5, 10, 20, 60, 120},
                "branch subgroup order drift",
                errors,
            )
            for field in ("phase_digest", "survivor_digest", "boundary_digest"):
                value = row.get(field)
                require(
                    isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
                    f"invalid {field}",
                    errors,
                )
        grouped = {
            pattern_id: [
                row
                for row in branches
                if isinstance(row, dict) and row.get("pattern_id") == pattern_id
            ]
            for pattern_id, *_rest in EXPECTED_PATTERNS
        }
        for expected in EXPECTED_PATTERNS:
            (
                pattern_id,
                _representative,
                _double_coset_size,
                branch_count,
                relation_edges,
                subgroup_name,
                subgroup_order,
                reachable_injections,
                reachable_orders,
                phase_witnesses,
                hittable_pairs,
            ) = expected
            rows = grouped[pattern_id]
            require(len(rows) == branch_count, f"{pattern_id} row grouping drift", errors)
            require({row.get("relation_edges") for row in rows} == {relation_edges}, f"{pattern_id} row edge drift", errors)
            require({row.get("reachable_injections") for row in rows} == {reachable_injections}, f"{pattern_id} row injection drift", errors)
            require({row.get("reachable_orders") for row in rows} == {reachable_orders}, f"{pattern_id} row order drift", errors)
            require({row.get("phase_witnesses") for row in rows} == {phase_witnesses}, f"{pattern_id} row phase-count drift", errors)
            require({len(row.get("hittable_pairs", [])) for row in rows} == {hittable_pairs}, f"{pattern_id} row pair-count drift", errors)
            require({row.get("generated_subgroup_name") for row in rows} == {subgroup_name}, f"{pattern_id} row subgroup-name drift", errors)
            require({row.get("generated_subgroup_order") for row in rows} == {subgroup_order}, f"{pattern_id} row subgroup-order drift", errors)
            require(len({row.get("phase_digest") for row in rows}) == 1, f"{pattern_id} phase digest is not unique", errors)
            require(len({row.get("survivor_digest") for row in rows}) == 1, f"{pattern_id} survivor digest is not unique", errors)

    subgroup = result.get("subgroup_collapse_control")
    require(isinstance(subgroup, dict), "subgroup-collapse control missing", errors)
    if isinstance(subgroup, dict):
        require(
            subgroup.get("formula")
            == "Omega_a = <C5,g_a>/C5 up to the fixed action convention",
            "subgroup formula drift",
            errors,
        )
        expected_strata = [
            {"group_name": "C5", "group_order": 5, "pattern_ids": ["P0"], "branch_count": 5, "reachable_order_count": 1, "distinct_phase_signatures": 1, "distinct_survivor_signatures": 1},
            {"group_name": "D10", "group_order": 10, "pattern_ids": ["P7"], "branch_count": 5, "reachable_order_count": 2, "distinct_phase_signatures": 1, "distinct_survivor_signatures": 1},
            {"group_name": "F20", "group_order": 20, "pattern_ids": ["P5", "P6"], "branch_count": 10, "reachable_order_count": 4, "distinct_phase_signatures": 1, "distinct_survivor_signatures": 1},
            {"group_name": "A5", "group_order": 60, "pattern_ids": ["P2", "P4"], "branch_count": 50, "reachable_order_count": 12, "distinct_phase_signatures": 1, "distinct_survivor_signatures": 1},
            {"group_name": "S5", "group_order": 120, "pattern_ids": ["P1", "P3"], "branch_count": 50, "reachable_order_count": 24, "distinct_phase_signatures": 1, "distinct_survivor_signatures": 1},
        ]
        require(subgroup.get("overgroup_strata") == expected_strata, "overgroup strata drift", errors)
        require(subgroup.get("phase_descends_through_generated_subgroup_on_n6") is True, "phase subgroup descent failed", errors)
        require(subgroup.get("survivor_descends_through_generated_subgroup_on_n6") is True, "survivor subgroup descent failed", errors)
        require(subgroup.get("status") == "EXACT_N6_SUBGROUP_COLLAPSE_CONTROL", "subgroup status drift", errors)

    conclusion = result.get("all_n_theorem_replay_control")
    expected_conclusion = {
        "phase_descends_through_pattern_on_n6": True,
        "survivor_spectrum_descends_through_pattern_on_n6": True,
        "phase_collapse_replayed": True,
        "survivor_count_formula_replayed": True,
        "status": "EXACT_N6_REPLAY_OF_ORDER_PHASE_SURVIVOR_THEOREM",
    }
    require(conclusion == expected_conclusion, "theorem replay conclusion drift", errors)

    boundary = result.get("claim_boundary")
    require(isinstance(boundary, list), "claim boundary missing", errors)
    if isinstance(boundary, list):
        joined = "\n".join(str(item) for item in boundary)
        require("declared n=6 branch fiber" in joined, "finite-scope firewall missing", errors)
        require("the manuscript owns" in joined, "manuscript-ownership boundary missing", errors)
        require("supplementary proof artifact" in joined, "supplementary-note boundary missing", errors)
        require("not the proof" in joined, "finite-control boundary missing", errors)
        require("typed transfer membership" in joined, "raw/typed firewall missing", errors)


def replay(expected: dict[str, object]) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="paper35-order-phase-") as directory:
        output = Path(directory) / "result.json"
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        completed = subprocess.run(
            [sys.executable, "-B", str(PRODUCER), "--output", str(output)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        require(completed.returncode == 0, f"replay failed: {completed.stderr}", errors)
        if completed.returncode == 0:
            replayed = json.loads(output.read_text(encoding="utf-8"))
            require(replayed == expected, "replay differs from retained result", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    texts = {
        path: validate_text(path, errors) for path in (PRODUCER, RESULT, README)
    }
    if not errors:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        validate_result(result, errors)
        require(SCHEMA in texts[PRODUCER], "producer schema constant missing", errors)
        readme_flat = " ".join(texts[README].split())
        require(
            "bounded consistency control" in readme_flat,
            "README lost the finite-control status",
            errors,
        )
        require(
            "does not prove the all-$n$ theorem" in readme_flat,
            "README lost the all-n proof boundary",
            errors,
        )
        if args.replay:
            errors.extend(replay(result))

    if errors:
        for error in errors:
            if error:
                print(f"FAIL: {error}")
        return 1
    mode = "replayed" if args.replay else "static"
    print(f"PASS: Paper XXXV order-phase audit ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
