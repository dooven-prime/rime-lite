#!/usr/bin/env python3
"""Validate the self-contained Paper XXX development package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = ROOT / "experiments" / "paper30"
MANIFEST_PATH = PACKAGE_ROOT / "development-manifest.json"
OUTER_RELEASE_PATHS = {
    PACKAGE_ROOT / "release-environment.json",
    PACKAGE_ROOT / "release-manifest.json",
    PACKAGE_ROOT / "results" / "paper30_public_package_v1.validation-receipt.json",
    PACKAGE_ROOT / "validation" / "validate_public_package.py",
}
EXPECTED_STATUS = "DRAFT_PAPER_OWNED_CLOSURE"
EXPECTED_PATHS = (
    "papers/paper30/Paper XXX.md",
    "papers/paper30/references-v1.bib",
    "experiments/paper30/README.md",
    "experiments/paper30/return_group_audit.py",
    "experiments/paper30/results/general_defect_return_group_audit_v1.json",
    "experiments/paper30/validation/validate_return_group_audit.py",
    "experiments/paper30/lean/README.md",
    "experiments/paper30/lean/Paper30.lean",
    "experiments/paper30/lean/Paper30/OrbitReduction.lean",
    "experiments/paper30/lean/Paper30/CycleGluing.lean",
    "experiments/paper30/lean/Paper30/BranchFiber.lean",
    "experiments/paper30/lean/formalization-manifest.json",
    "experiments/paper30/lean/lakefile.toml",
    "experiments/paper30/lean/lake-manifest.json",
    "experiments/paper30/lean/lean-toolchain",
    "experiments/paper30/validation/validate_lean_formalization.py",
    "experiments/paper30/validation/validate_package.py",
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
    if manifest.get("schema") != "rime.paper30.development-manifest.v1":
        errors.append("development manifest schema mismatch")
    if manifest.get("status") != EXPECTED_STATUS:
        errors.append("development closure status mismatch")
    if manifest.get("release_identity_claimed") is not False:
        errors.append("draft package must not claim a release identity")
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
        path for path in EXPECTED_PATHS if path.startswith("experiments/paper30/")
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
        (PACKAGE_ROOT / "results" / "general_defect_return_group_audit_v1.json")
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

    manuscript = (ROOT / "papers" / "paper30" / "Paper XXX.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "Paper XXX | Version 1.0",
        "Theorem 4.1 (exact relation-valued orbit reduction)",
        "Theorem 6.2 (exact cycle-gluing theorem)",
        "Corollary 6.4 (fixed-collision branch fiber and exact gluing",
        "The retained finite audits are bounded consistency controls",
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
            [sys.executable, "experiments/paper30/validation/validate_return_group_audit.py"],
            [
                sys.executable,
                "experiments/paper30/validation/validate_lean_formalization.py",
                "--replay",
            ],
        )
        for command in commands:
            if run(command):
                errors.append(f"replay failed: {' '.join(command)}")
                break

    if errors:
        print("FAIL Paper XXX development package")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "full replay" if args.replay else "static closure"
    print(f"PASS Paper XXX development package: {mode}, {len(EXPECTED_PATHS)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
