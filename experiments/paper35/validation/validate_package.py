#!/usr/bin/env python3
"""Validate the self-contained Paper XXXV paper-owned package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper35"
MANIFEST = PACKAGE / "development-manifest.json"
STATUS = "DRAFT_PAPER_OWNED_CLOSURE"
EXPECTED_PATHS = (
    "papers/paper35/Paper XXXV.md",
    "papers/paper35/references-v1.bib",
    "experiments/paper35/ONE_LANE_ORDER_PHASE_SURVIVOR_THEOREM.md",
    "experiments/paper35/lean/README.md",
    "experiments/paper35/lean/Paper35.lean",
    "experiments/paper35/lean/Paper35/PhaseCollapse.lean",
    "experiments/paper35/lean/Paper35/LeftCosets.lean",
    "experiments/paper35/lean/Paper35/SurvivorFrontier.lean",
    "experiments/paper35/lean/formalization-manifest.json",
    "experiments/paper35/lean/lakefile.toml",
    "experiments/paper35/lean/lake-manifest.json",
    "experiments/paper35/lean/lean-toolchain",
    "experiments/paper35/order_phase_audit.py",
    "experiments/paper35/results/order_phase_n6_v2.json",
    "experiments/paper35/validation/validate_lean_formalization.py",
    "experiments/paper35/validation/validate_source.py",
    "experiments/paper35/validation/validate_order_phase_audit.py",
    "experiments/paper35/validation/validate_package.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files() -> set[str]:
    files: set[str] = set()
    for directory, dirnames, filenames in os.walk(PACKAGE):
        dirnames[:] = [
            name for name in dirnames if name not in {"__pycache__", ".lake"}
        ]
        for filename in filenames:
            path = Path(directory) / filename
            if path == MANIFEST or path.suffix == ".pyc":
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_static() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["development manifest is missing"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper35.development-manifest.v1":
        errors.append("development manifest schema mismatch")
    if manifest.get("status") != STATUS:
        errors.append("development status mismatch")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("development closure must not claim a release identity")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("validation mode mismatch")

    rows = manifest.get("artifacts", [])
    paths = [row.get("path") for row in rows]
    if tuple(paths) != EXPECTED_PATHS:
        errors.append("manifest inventory or order mismatch")
    if len(paths) != len(set(paths)):
        errors.append("manifest contains duplicate paths")

    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"nonportable path: {row['path']}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing artifact: {row['path']}")
        elif sha256(path) != row.get("sha256"):
            errors.append(f"artifact changed: {row['path']}")

    expected_package = {
        path for path in EXPECTED_PATHS if path.startswith("experiments/paper35/")
    }
    actual_package = package_files()
    allowed_release = {
        "experiments/paper35/README.md",
        "experiments/paper35/release-environment.json",
        "experiments/paper35/release-manifest.json",
        "experiments/paper35/results/paper35_public_package_v1.validation-receipt.json",
        "experiments/paper35/validation/validate_release.py",
    }
    if expected_package - actual_package or actual_package - expected_package - allowed_release:
        missing = sorted(expected_package - actual_package)
        extra = sorted(actual_package - expected_package - allowed_release)
        if missing:
            errors.append(f"package files missing: {missing}")
        if extra:
            errors.append(f"unlisted package files: {extra}")

    if "papers/paper35/DIRECTION_DRAFT.md" in paths:
        errors.append("research direction ledger entered the development closure")

    forbidden_dependency = "experiments/" + "synchronizing_automata"
    for relative in EXPECTED_PATHS:
        path = ROOT / relative
        raw = path.read_bytes()
        if b"\r" in raw:
            errors.append(f"non-LF artifact: {relative}")
        text = raw.decode("utf-8")
        if forbidden_dependency in text:
            errors.append(f"broader exploratory dependency in {relative}")
    return errors


def run_validator(replay: bool) -> list[str]:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    command = [
        sys.executable,
        "-B",
        str(PACKAGE / "validation" / "validate_order_phase_audit.py"),
    ]
    if replay:
        command.append("--replay")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"order-phase validator failed:\n{result.stdout}{result.stderr}"]
    print(result.stdout.strip())
    return []


def run_source_validator() -> list[str]:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(PACKAGE / "validation" / "validate_source.py"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"source validator failed:\n{result.stdout}{result.stderr}"]
    print(result.stdout.strip())
    return []


def run_lean_validator(replay: bool) -> list[str]:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    command = [
        sys.executable,
        "-B",
        str(PACKAGE / "validation" / "validate_lean_formalization.py"),
    ]
    if replay:
        command.append("--replay")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"Lean validator failed:\n{result.stdout}{result.stderr}"]
    print(result.stdout.strip())
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--replay-lean", action="store_true")
    args = parser.parse_args()

    errors = validate_static()
    errors.extend(run_source_validator())
    errors.extend(run_validator(args.replay))
    errors.extend(run_lean_validator(args.replay_lean))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXV paper-owned package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
