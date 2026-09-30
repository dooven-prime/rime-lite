#!/usr/bin/env python3
"""Validate the self-contained Paper XXXI development package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = ROOT / "experiments" / "paper31"
MANIFEST_PATH = PACKAGE_ROOT / "development-manifest.json"
OUTER_RELEASE_PATHS = {
    PACKAGE_ROOT / "release-environment.json",
    PACKAGE_ROOT / "release-manifest.json",
    PACKAGE_ROOT / "results" / "paper31_public_package_v1.validation-receipt.json",
    PACKAGE_ROOT / "validation" / "validate_public_package.py",
}
EXPECTED_STATUS = "DRAFT_PAPER_OWNED_CLOSURE"
EXPECTED_PATHS = (
    "papers/paper31/Paper XXXI.md",
    "papers/paper31/references-v1.bib",
    "experiments/paper31/README.md",
    "experiments/paper31/partial_return_audit.py",
    "experiments/paper31/results/partial_return_hostile_audit_v1.json",
    "experiments/paper31/validation/validate_partial_return_audit.py",
    "experiments/paper31/lean/README.md",
    "experiments/paper31/lean/Paper31.lean",
    "experiments/paper31/lean/Paper31/Reachability.lean",
    "experiments/paper31/lean/Paper31/PartialConjugacy.lean",
    "experiments/paper31/lean/Paper31/SkewBoundary.lean",
    "experiments/paper31/lean/formalization-manifest.json",
    "experiments/paper31/lean/lakefile.toml",
    "experiments/paper31/lean/lake-manifest.json",
    "experiments/paper31/lean/lean-toolchain",
    "experiments/paper31/validation/validate_lean_formalization.py",
    "experiments/paper31/validation/validate_package.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files() -> set[str]:
    files: set[str] = set()
    for directory, dirnames, filenames in os.walk(PACKAGE_ROOT):
        dirnames[:] = [
            name for name in dirnames if name not in {".lake", "__pycache__"}
        ]
        for filename in filenames:
            path = Path(directory) / filename
            if path == MANIFEST_PATH or path in OUTER_RELEASE_PATHS:
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_static() -> list[str]:
    errors: list[str] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper31.development-manifest.v1":
        errors.append("development manifest schema mismatch")
    if manifest.get("status") != EXPECTED_STATUS:
        errors.append("development closure status mismatch")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("working package must not claim a release identity")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("validation mode mismatch")

    rows = manifest.get("artifacts", [])
    paths = [row.get("path") for row in rows]
    if tuple(paths) != EXPECTED_PATHS:
        errors.append("manifest artifact inventory or order mismatch")
    if len(paths) != len(set(paths)):
        errors.append("manifest contains duplicate artifact paths")

    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"nonportable artifact path: {row['path']}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing artifact: {row['path']}")
        elif sha256(path) != row.get("sha256"):
            errors.append(f"artifact changed: {row['path']}")

    expected_experiment_paths = {
        path for path in EXPECTED_PATHS if path.startswith("experiments/paper31/")
    }
    actual_package_files = package_files()
    if actual_package_files != expected_experiment_paths:
        missing = sorted(expected_experiment_paths - actual_package_files)
        extra = sorted(actual_package_files - expected_experiment_paths)
        if missing:
            errors.append(f"package files missing from disk: {missing}")
        if extra:
            errors.append(f"unlisted package files: {extra}")

    private_prefix = "experiments/" + "synchronizing_automata"
    for relative in EXPECTED_PATHS:
        path = ROOT / relative
        if path.suffix.lower() not in {".md", ".py", ".lean", ".json", ".toml"}:
            continue
        if private_prefix in path.read_text(encoding="utf-8"):
            errors.append(f"private-tree dependency reference in {relative}")

    result = json.loads(
        (PACKAGE_ROOT / "results" / "partial_return_hostile_audit_v1.json")
        .read_text(encoding="utf-8")
    )
    if result.get("status") != "FINITE_SANITY_CHECK_NOT_ALL_N_PROOF":
        errors.append("finite-result claim boundary drift")

    formalization = json.loads(
        (PACKAGE_ROOT / "lean" / "formalization-manifest.json")
        .read_text(encoding="utf-8")
    )
    if formalization.get("status") != "COMPILED_PAPER_OWNED_PARTIAL_FORMALIZATION":
        errors.append("Lean formalization status drift")

    manuscript = (ROOT / "papers" / "paper31" / "Paper XXXI.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "Paper XXXI | Version 1.0",
        "Theorem 2.1 (branch-normalized full return dynamics; N1)",
        "Theorem 4.3 (multi-lane Safe-Hit classification; N3)",
        "Theorem 5.1 (normalizer skew-orbit reduction; N4.1)",
        "Corollary 6.4 (normalizer Safe-Hit sandwich; N4.6)",
        "bounded consistency and formalization controls",
    ):
        if marker not in manuscript:
            errors.append(f"manuscript scope marker missing: {marker}")
    return errors


def run(command: list[str]) -> int:
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    errors = validate_static()
    if not errors and args.replay:
        commands = (
            [sys.executable, "experiments/paper31/validation/validate_partial_return_audit.py"],
            [
                sys.executable,
                "experiments/paper31/validation/validate_lean_formalization.py",
                "--replay",
            ],
        )
        for command in commands:
            if run(command):
                errors.append(f"replay failed: {' '.join(command)}")
                break

    if errors:
        print("FAIL Paper XXXI development package")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "full replay" if args.replay else "static closure"
    print(f"PASS Paper XXXI development package: {mode}, {len(EXPECTED_PATHS)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
