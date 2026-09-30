#!/usr/bin/env python3
"""Validate the retained Paper XXXIII stabilizer discovery controls."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from math import gcd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper33"
PRODUCER = PACKAGE / "stabilizer_hostile_audit.py"
SMALL_RESULT = PACKAGE / "results" / "stabilizer_hostile_audit_v1.json"
HOSTILE_RESULT = PACKAGE / "results" / "stabilizer_n10_delta2_full_v1.json"
README = PACKAGE / "README.md"
MANUSCRIPT = ROOT / "papers" / "paper33" / "Paper XXXIII.md"

SCHEMA = "rime.paper33.stabilizer-hostile-audit.v1"
STATUS = "FINITE_THEOREM_DISCOVERY_CONTROL"
FAMILY_STATUS = "BOUNDED_CONTROL_OF_SYMBOLIC_OBSTRUCTION_NOT_PROOF"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing file: {path.relative_to(ROOT).as_posix()}")
        return ""
    raw = path.read_bytes()
    require(b"\r" not in raw, f"non-LF text artifact: {path.name}", errors)
    require(b"\x00" not in raw, f"NUL byte in text artifact: {path.name}", errors)
    return raw.decode("utf-8")


def validate_family(result: dict[str, object], errors: list[str]) -> None:
    family = result.get("capacity_isolated_family_control")
    require(isinstance(family, dict), "missing capacity-family control", errors)
    if not isinstance(family, dict):
        return
    require(family.get("min_g") == 2, "capacity family min_g mismatch", errors)
    require(family.get("max_g") == 12, "capacity family max_g mismatch", errors)
    require(family.get("status") == FAMILY_STATUS, "capacity status mismatch", errors)
    rows = family.get("rows")
    require(isinstance(rows, list), "capacity family rows missing", errors)
    if not isinstance(rows, list):
        return
    require(len(rows) == 11, "capacity family row count mismatch", errors)
    for expected_g, row in zip(range(2, 13), rows, strict=False):
        require(isinstance(row, dict), f"invalid capacity row for g={expected_g}", errors)
        if not isinstance(row, dict):
            continue
        expected = {
            "g": expected_g,
            "n": 5 * expected_g,
            "delta": expected_g,
            "states_checked": 5 * (expected_g - 1),
            "enabled_edges": 25 * (expected_g - 1) ** 2,
            "disabled_edges": 25 * (expected_g - 1),
        }
        require(row == expected, f"capacity row mismatch for g={expected_g}", errors)


def validate_common(
    path: Path, result: dict[str, object], errors: list[str]
) -> None:
    require(result.get("schema") == SCHEMA, f"{path.name}: schema mismatch", errors)
    require(result.get("status") == STATUS, f"{path.name}: status mismatch", errors)
    boundary = result.get("claim_boundary")
    require(isinstance(boundary, list), f"{path.name}: claim boundary missing", errors)
    if isinstance(boundary, list):
        joined = "\n".join(str(item) for item in boundary)
        require("not an all-n theorem" in joined, f"{path.name}: all-n firewall missing", errors)
        require("raw Safe-Hit" in joined, f"{path.name}: raw/typed firewall missing", errors)
    validate_family(result, errors)


def validate_small(result: dict[str, object], errors: list[str]) -> None:
    scope = result.get("scope")
    totals = result.get("totals")
    domains = result.get("domains")
    require(isinstance(scope, dict), "small scope missing", errors)
    require(isinstance(totals, dict), "small totals missing", errors)
    require(isinstance(domains, list), "small domains missing", errors)
    if not isinstance(scope, dict) or not isinstance(totals, dict):
        return
    require(scope.get("min_n") == 6, "small min_n mismatch", errors)
    require(scope.get("max_n") == 9, "small max_n mismatch", errors)
    require(scope.get("selected_domains") == [], "small selected-domain drift", errors)
    expected_totals = {
        "break_set_non_descent_domains": 0,
        "domains": 8,
        "incidence_factorization_checks": 656,
        "stabilizer_branches": 656,
        "strong_coarse_non_descent_domains": 0,
        "x3_failures": 0,
    }
    require(totals == expected_totals, "small totals mismatch", errors)
    if isinstance(domains, list):
        expected_domains = {
            (n, delta)
            for n in range(6, 10)
            for delta in range(1, n)
            if gcd(n, delta) > 1
        }
        actual_domains = {
            (int(row["n"]), int(row["delta"]))
            for row in domains
            if isinstance(row, dict)
        }
        require(actual_domains == expected_domains, "small domain set mismatch", errors)
        require(
            all(
                isinstance(row, dict)
                and row.get("x3_holds_on_retained_domain") is True
                and row.get("first_x3_failure") is None
                for row in domains
            ),
            "small scan contains an unexpected X3 failure",
            errors,
        )


def validate_hostile(result: dict[str, object], errors: list[str]) -> None:
    scope = result.get("scope")
    totals = result.get("totals")
    domains = result.get("domains")
    require(isinstance(scope, dict), "hostile scope missing", errors)
    require(isinstance(totals, dict), "hostile totals missing", errors)
    require(isinstance(domains, list) and len(domains) == 1, "hostile domain count mismatch", errors)
    if not isinstance(scope, dict) or not isinstance(totals, dict):
        return
    require(scope.get("selected_domains") == [[10, 2]], "hostile selected-domain drift", errors)
    require(scope.get("factorization_limit_per_domain") == 8, "hostile factorization scope drift", errors)
    expected_totals = {
        "break_set_non_descent_domains": 0,
        "domains": 1,
        "incidence_factorization_checks": 8,
        "stabilizer_branches": 2880,
        "strong_coarse_non_descent_domains": 0,
        "x3_failures": 1,
    }
    require(totals == expected_totals, "hostile totals mismatch", errors)
    if not isinstance(domains, list) or len(domains) != 1:
        return
    row = domains[0]
    require(isinstance(row, dict), "hostile domain row malformed", errors)
    if not isinstance(row, dict):
        return
    expected_fields = {
        "n": 10,
        "delta": 2,
        "lane_lengths": [4, 5],
        "states": 1260,
        "orbits": 69,
        "adjacent_states": 505,
        "same_lane_states": 560,
        "stabilizer_branches": 2880,
        "incidence_factorization_checks": 8,
        "outcomes": {"ADJ": 80, "INTERMEDIATE": 160, "SAME": 2640},
        "x3_holds_on_retained_domain": False,
    }
    for key, value in expected_fields.items():
        require(row.get(key) == value, f"hostile {key} mismatch", errors)
    witness = row.get("first_x3_failure")
    require(isinstance(witness, dict), "hostile witness missing", errors)
    if isinstance(witness, dict):
        require(witness.get("punctured_map") == [0, 1, 3, 2], "hostile punctured map mismatch", errors)
        require(witness.get("break_pattern") == [0], "hostile break pattern mismatch", errors)
        require(witness.get("safe_hit_states") == 555, "hostile Safe-Hit count mismatch", errors)


def replay(args: list[str], expected: dict[str, object], label: str) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="paper33-replay-") as directory:
        output = Path(directory) / "result.json"
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        command = [sys.executable, "-B", str(PRODUCER), *args, "--output", str(output)]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        require(completed.returncode == 0, f"{label} replay failed: {completed.stderr}", errors)
        if completed.returncode == 0:
            actual = read_json(output)
            require(actual == expected, f"{label} replay differs from retained result", errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-small", action="store_true")
    parser.add_argument("--replay-hostile", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    for path in (PRODUCER, SMALL_RESULT, HOSTILE_RESULT, README, MANUSCRIPT):
        validate_text(path, errors)

    if not errors:
        small = read_json(SMALL_RESULT)
        hostile = read_json(HOSTILE_RESULT)
        validate_common(SMALL_RESULT, small, errors)
        validate_common(HOSTILE_RESULT, hostile, errors)
        validate_small(small, errors)
        validate_hostile(hostile, errors)

        source = PRODUCER.read_text(encoding="utf-8")
        manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        require(SCHEMA in source, "producer schema constant missing", errors)
        require(STATUS in source, "producer status constant missing", errors)
        require(
            "Theorem 5.1 (capacity-isolated break obstruction)" in manuscript,
            "manuscript lacks the capacity-isolation theorem",
            errors,
        )
        require(
            "Such a quotient non-descent theorem" in manuscript
            and "requires two branches with equal break sets" in manuscript,
            "manuscript lost the quotient non-descent firewall",
            errors,
        )
        require(
            "This does not prove that the break set itself is a non-descending quotient."
            in readme,
            "README lost the quotient non-descent firewall",
            errors,
        )

        if args.replay_small:
            errors.extend(replay(["--max-n", "9"], small, "small"))
        if args.replay_hostile:
            errors.extend(
                replay(
                    ["--domain", "10:2", "--factorization-limit", "8"],
                    hostile,
                    "hostile",
                )
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXIII stabilizer discovery controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
