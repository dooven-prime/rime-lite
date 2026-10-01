#!/usr/bin/env python3
"""Validate and optionally replay the Paper XXXIV survivor control."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper34"
PRODUCER = PACKAGE / "survivor_incidence_audit.py"
RESULT = PACKAGE / "results" / "survivor_incidence_n6_v2.json"
README = PACKAGE / "README.md"
FORMAL_NOTE = PACKAGE / "ONE_LANE_DIHEDRAL_SURVIVOR_CLASSIFICATION.md"

SCHEMA = "rime.paper34.survivor-incidence-audit.v2"
STATUS = "FINITE_THEOREM_DISCOVERY_CONTROL"
PAIRS = [[0, 1], [0, 4], [1, 2], [2, 3], [3, 4]]


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


def validate_result(result: dict[str, object], errors: list[str]) -> None:
    require(result.get("schema") == SCHEMA, "schema mismatch", errors)
    require(result.get("status") == STATUS, "status mismatch", errors)

    scope = result.get("scope")
    require(isinstance(scope, dict), "scope missing", errors)
    if isinstance(scope, dict):
        expected_scope = {
            "n": 6,
            "delta": 1,
            "source": [1, 2, 3, 4, 5],
            "branches_checked": 120,
            "branch_fiber_size": 120,
            "branch_scan_complete": True,
        }
        require(scope == expected_scope, "scope drift", errors)

    incidence = result.get("normalized_incidence_identity")
    require(isinstance(incidence, dict), "incidence identity missing", errors)
    if isinstance(incidence, dict):
        require(
            incidence.get("formula")
            == "beta = epsilon_delta o p^u o a o lambda",
            "incidence formula drift",
            errors,
        )
        require(
            incidence.get("same_witness_required") is True,
            "same-witness flag drift",
            errors,
        )

    identity = result.get("identity_branch")
    require(isinstance(identity, dict), "identity control missing", errors)
    if isinstance(identity, dict):
        require(identity.get("branch") == [1, 2, 3, 4, 5], "identity branch drift", errors)
        require(identity.get("reachable_lineage_states") == 5, "identity reachability drift", errors)
        require(identity.get("terminal_witnesses") == 20, "identity witness drift", errors)
        require(identity.get("hittable_pairs") == PAIRS, "identity fused-pair drift", errors)
        require(
            sorted(identity.get("survivor_spectrum_sizes", {}).values())
            == [0, 0, 0, 0, 0, 4, 4, 4, 4, 4],
            "identity survivor sizes drift",
            errors,
        )

    canonical = result.get("canonical_recovery")
    require(isinstance(canonical, dict), "canonical recovery missing", errors)
    if isinstance(canonical, dict):
        require(canonical.get("consecutive_pairs") == PAIRS, "canonical pair drift", errors)
        require(canonical.get("survivors_per_pair") == 4, "canonical survivor drift", errors)
        require(canonical.get("total_boundary_incidences") == 20, "canonical total drift", errors)
        require(canonical.get("paper29_expected_total") == 20, "Paper XXIX total drift", errors)
        require(
            canonical.get("status") == "MATCHED_CANONICAL_RECOVERY_CONTROL",
            "canonical status drift",
            errors,
        )

    reflection = result.get("identity_reflection_control")
    require(isinstance(reflection, dict), "identity/reflection control missing", errors)
    if isinstance(reflection, dict):
        require(reflection.get("same_hittable_pairs") is True, "matched pair signature failed", errors)
        require(reflection.get("hittable_pairs") == PAIRS, "reflection pair drift", errors)
        require(reflection.get("different_survivor_spectra") is True, "survivor variation missing", errors)
        require(reflection.get("differing_pairs") == PAIRS, "differing-pair set drift", errors)
        require(set(reflection.get("left_spectrum_sizes", {}).values()) == {4}, "left reflection sizes drift", errors)
        require(set(reflection.get("right_spectrum_sizes", {}).values()) == {8}, "right reflection sizes drift", errors)

    family = result.get("identity_reflection_family_control")
    require(isinstance(family, dict), "family control missing", errors)
    if isinstance(family, dict):
        require(family.get("min_n") == 6, "family min_n drift", errors)
        require(family.get("max_n") == 9, "family max_n drift", errors)
        require(
            family.get("status")
            == "BOUNDED_CONTROL_OF_SYMBOLIC_NONDESCENT_NOT_PROOF",
            "family status drift",
            errors,
        )
        expected_rows = [
            {"n": 6, "delta": 1, "hittable_pairs": 5, "identity_survivors_per_pair": 4, "reflection_survivors_per_pair": 8},
            {"n": 7, "delta": 1, "hittable_pairs": 5, "identity_survivors_per_pair": 10, "reflection_survivors_per_pair": 20},
            {"n": 8, "delta": 1, "hittable_pairs": 5, "identity_survivors_per_pair": 20, "reflection_survivors_per_pair": 40},
            {"n": 9, "delta": 1, "hittable_pairs": 5, "identity_survivors_per_pair": 35, "reflection_survivors_per_pair": 70},
        ]
        require(family.get("rows") == expected_rows, "family rows drift", errors)

    dihedral = result.get("one_lane_dihedral_family_control")
    require(isinstance(dihedral, dict), "dihedral family control missing", errors)
    if isinstance(dihedral, dict):
        require(dihedral.get("min_n") == 6, "dihedral min_n drift", errors)
        require(dihedral.get("max_n") == 9, "dihedral max_n drift", errors)
        require(
            dihedral.get("orientation_character")
            == {"rotation": "+1", "reflection": "-1"},
            "dihedral orientation character drift",
            errors,
        )
        require(
            dihedral.get("status")
            == "BOUNDED_CONTROL_OF_DIHEDRAL_CLASSIFICATION_NOT_PROOF",
            "dihedral status drift",
            errors,
        )
        expected_dihedral_rows = [
            {
                "n": n,
                "delta": 1,
                "dihedral_branches_checked": 2 * (n - 1),
                "rotations_checked": n - 1,
                "reflections_checked": n - 1,
                "hittable_pairs": 5,
                "positive_survivors_per_pair": expected,
                "reflection_survivors_per_pair": 2 * expected,
                "exact_orientation_spectra_matched": True,
            }
            for n, expected in ((6, 4), (7, 10), (8, 20), (9, 35))
        ]
        require(
            dihedral.get("rows") == expected_dihedral_rows,
            "dihedral family rows drift",
            errors,
        )

    matched = result.get("pair_summary_non_descent")
    require(isinstance(matched, dict), "matched non-descent witness missing", errors)
    if isinstance(matched, dict):
        require(matched.get("same_hittable_pairs") == PAIRS, "matched signature drift", errors)
        require(matched.get("left_branch") == [1, 2, 3, 4, 5], "matched left branch drift", errors)
        require(matched.get("right_branch") == [1, 5, 4, 3, 2], "matched right branch drift", errors)
        require(matched.get("left_spectrum_size") == 4, "matched left size drift", errors)
        require(matched.get("right_spectrum_size") == 8, "matched right size drift", errors)
        require(
            matched.get("status") == "FINITE_MATCHED_NON_DESCENT_WITNESS",
            "matched status drift",
            errors,
        )

    boundary = result.get("claim_boundary")
    require(isinstance(boundary, list), "claim boundary missing", errors)
    if isinstance(boundary, list):
        joined = "\n".join(str(item) for item in boundary)
        require("finite replay is only a control" in joined, "finite/theorem firewall missing", errors)
        require("typed transfer membership" in joined, "raw/typed firewall missing", errors)


def replay(expected: dict[str, object]) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="paper34-survivor-") as directory:
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
            require(read_json(output) == expected, "replay differs from retained result", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    texts = {
        path: validate_text(path, errors)
        for path in (PRODUCER, RESULT, README, FORMAL_NOTE)
    }
    if not errors:
        result = read_json(RESULT)
        validate_result(result, errors)
        require(SCHEMA in texts[PRODUCER], "producer schema constant missing", errors)
        require(
            "Theorem I1 (one-lane dihedral survivor-spectrum classification)"
            in texts[FORMAL_NOTE],
            "formal note theorem surface missing",
            errors,
        )
        require(
            "Corollary I2 (pair-level non-descent)" in texts[FORMAL_NOTE],
            "formal note non-descent corollary missing",
            errors,
        )
        require(
            "Separate terminal witnesses may not be" in texts[README],
            "README lost the same-witness firewall",
            errors,
        )
        require(
            "Every theorem-facing domain object must reference the declared"
            in texts[README],
            "README lost the concrete-state-space admission gate",
            errors,
        )
        require(
            "`separate_witnesses_do_not_combine`, is not domain evidence"
            in texts[README],
            "README promotes the abstract witness firewall to domain evidence",
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
    print(f"PASS: Paper XXXIV survivor-incidence control ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
