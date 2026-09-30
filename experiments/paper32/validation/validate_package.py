#!/usr/bin/env python3
"""Validate the self-contained Paper XXXII development package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = ROOT / "experiments" / "paper32"
MANIFEST_PATH = PACKAGE_ROOT / "development-manifest.json"
OUTER_RELEASE_PATHS = {
    PACKAGE_ROOT / "release-environment.json",
    PACKAGE_ROOT / "release-manifest.json",
    PACKAGE_ROOT / "results" / "paper32_public_package_v1.validation-receipt.json",
    PACKAGE_ROOT / "validation" / "validate_public_package.py",
}
EXPECTED_STATUS = "DRAFT_PAPER_OWNED_CLOSURE"
EXPECTED_PATHS = (
    "papers/paper32/Paper XXXII.md",
    "papers/paper32/references-v1.bib",
    "experiments/paper32/README.md",
    "experiments/paper32/affine_five_token_audit.py",
    "experiments/paper32/results/affine_five_token_audit_v1.json",
    "experiments/paper32/validation/validate_source.py",
    "experiments/paper32/validation/validate_affine_five_token_audit.py",
    "experiments/paper32/validation/validate_package.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files() -> set[str]:
    files: set[str] = set()
    for directory, dirnames, filenames in os.walk(PACKAGE_ROOT):
        dirnames[:] = [name for name in dirnames if name != "__pycache__"]
        for filename in filenames:
            path = Path(directory) / filename
            if path == MANIFEST_PATH or path in OUTER_RELEASE_PATHS:
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_static() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        return ["development manifest is missing"]

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper32.development-manifest.v1":
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
        path for path in EXPECTED_PATHS if path.startswith("experiments/paper32/")
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
    text_suffixes = {".md", ".py", ".json", ".bib", ".toml"}
    for relative in EXPECTED_PATHS:
        path = ROOT / relative
        if path.suffix.lower() not in text_suffixes:
            continue
        raw = path.read_bytes()
        if b"\r" in raw:
            errors.append(f"non-LF text artifact: {relative}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"non-UTF-8 text artifact: {relative}: {error}")
            continue
        if text.startswith("\ufeff"):
            errors.append(f"UTF-8 BOM is not allowed: {relative}")
        if private_prefix in text:
            errors.append(f"broader-tree dependency reference in {relative}")

    result = json.loads(
        (PACKAGE_ROOT / "results" / "affine_five_token_audit_v1.json")
        .read_text(encoding="utf-8")
    )
    if result.get("status") != "FINITE_SANITY_CHECK_NOT_ALL_N_PROOF":
        errors.append("finite-result claim boundary drift")

    manuscript = (ROOT / "papers" / "paper32" / "Paper XXXII.md").read_text(
        encoding="utf-8"
    )
    normalized_manuscript = " ".join(manuscript.split())
    for marker in (
        "Paper XXXII | Version 1.0",
        "Proposition 3.1 (lane-wise dihedral classification)",
        "Theorem 4.3 (single-lane order-fiber transitivity)",
        "Theorem 5.1 (single-lane permutation dichotomy)",
        "Corollary 6.1 (lane-stabilizer Safe-Hit sandwich)",
        "## Computational Artifacts",
        "## Claim Status and Boundary",
        "Bounded arbitrary-permutation control",
        "The finite audits are bounded consistency controls",
        "not promoted as independent Computational Certificates",
        "Full lane-stabilizer promotion classification | Open",
    ):
        if marker not in normalized_manuscript:
            errors.append(f"manuscript scope marker missing: {marker}")

    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    for marker in (
        "This initial package does not claim a Paper XXXII Lean formalization.",
        "directed unit transfers on five-part weak compositions",
        "papers/paper32/DIRECTION_DRAFT.md",
        "intentionally excluded from this closure",
    ):
        if marker not in normalized_readme:
            errors.append(f"README scope marker missing: {marker}")

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
            [sys.executable, "experiments/paper32/validation/validate_source.py"],
            [
                sys.executable,
                "experiments/paper32/validation/validate_affine_five_token_audit.py",
                "--replay",
            ],
        )
        for command in commands:
            if run(command):
                errors.append(f"replay failed: {' '.join(command)}")
                break

    if errors:
        print("FAIL Paper XXXII development package")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "full replay" if args.replay else "static closure"
    print(
        f"PASS Paper XXXII development package: {mode}, "
        f"{len(EXPECTED_PATHS)} artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
