#!/usr/bin/env python3
"""Validate the self-contained Paper XXXIII working package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "paper33"
MANIFEST = PACKAGE / "development-manifest.json"
OUTER_RELEASE_PATHS = {
    PACKAGE / "release-environment.json",
    PACKAGE / "release-manifest.json",
    PACKAGE / "results" / "paper33_public_package_v1.validation-receipt.json",
    PACKAGE / "validation" / "validate_public_package.py",
}
STATUS = "DRAFT_PAPER_OWNED_CLOSURE"
EXPECTED_PATHS = (
    "papers/paper33/Paper XXXIII.md",
    "papers/paper33/references-v1.bib",
    "figures/paper33/render.py",
    "figures/paper33/fig1_source_addressed_incidence.png",
    "experiments/paper33/README.md",
    "experiments/paper33/stabilizer_hostile_audit.py",
    "experiments/paper33/results/stabilizer_hostile_audit_v1.json",
    "experiments/paper33/results/stabilizer_n10_delta2_full_v1.json",
    "experiments/paper33/lean/README.md",
    "experiments/paper33/lean/Paper33.lean",
    "experiments/paper33/lean/Paper33/CapacityObstruction.lean",
    "experiments/paper33/lean/formalization-manifest.json",
    "experiments/paper33/lean/lakefile.toml",
    "experiments/paper33/lean/lake-manifest.json",
    "experiments/paper33/lean/lean-toolchain",
    "experiments/paper33/validation/validate_lean_formalization.py",
    "experiments/paper33/validation/validate_source.py",
    "experiments/paper33/validation/validate_stabilizer_hostile_audit.py",
    "experiments/paper33/validation/validate_package.py",
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
            if path == MANIFEST or path in OUTER_RELEASE_PATHS or path.suffix == ".pyc":
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_static() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["development manifest is missing"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper33.development-manifest.v1":
        errors.append("development manifest schema mismatch")
    if manifest.get("status") != STATUS:
        errors.append("development status mismatch")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("working package must not claim a release identity")
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
        path for path in EXPECTED_PATHS if path.startswith("experiments/paper33/")
    }
    actual_package = package_files()
    if actual_package != expected_package:
        missing = sorted(expected_package - actual_package)
        extra = sorted(actual_package - expected_package)
        if missing:
            errors.append(f"package files missing: {missing}")
        if extra:
            errors.append(f"unlisted package files: {extra}")

    if "papers/paper33/DIRECTION_DRAFT.md" in paths:
        errors.append("research direction ledger entered the development closure")

    forbidden_dependency = "experiments/" + "synchronizing_automata"
    for relative in EXPECTED_PATHS:
        path = ROOT / relative
        if path.suffix.lower() not in {
            ".md",
            ".py",
            ".json",
            ".bib",
            ".lean",
            ".toml",
        }:
            continue
        raw = path.read_bytes()
        if b"\r" in raw:
            errors.append(f"non-LF artifact: {relative}")
        text = raw.decode("utf-8")
        if forbidden_dependency in text:
            errors.append(f"broader exploratory dependency in {relative}")
    return errors


def run_validator(path: Path, extra: list[str] | None = None) -> list[str]:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    command = [sys.executable, "-B", str(path), *(extra or [])]
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"{path.name} failed:\n{result.stdout}{result.stderr}"]
    print(result.stdout.strip())
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-small", action="store_true")
    parser.add_argument("--replay-hostile", action="store_true")
    parser.add_argument("--replay-lean", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_static()
    errors.extend(run_validator(PACKAGE / "validation" / "validate_source.py"))
    lean_args = ["--replay"] if args.replay_lean else []
    errors.extend(
        run_validator(
            PACKAGE / "validation" / "validate_lean_formalization.py",
            lean_args,
        )
    )
    replay_args: list[str] = []
    if args.replay_small:
        replay_args.append("--replay-small")
    if args.replay_hostile:
        replay_args.append("--replay-hostile")
    errors.extend(
        run_validator(
            PACKAGE / "validation" / "validate_stabilizer_hostile_audit.py",
            replay_args,
        )
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXIII working package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
