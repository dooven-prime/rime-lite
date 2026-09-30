#!/usr/bin/env python3
"""Validate and optionally replay the Paper XXXIII Lean capacity spine."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments" / "paper33" / "lean"
MANIFEST_PATH = LEAN_ROOT / "formalization-manifest.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper33" / "Paper XXXIII.md"
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.33.0"
EXPECTED_MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
EXPECTED_SOURCES = (
    "Paper33.lean",
    "Paper33/CapacityObstruction.lean",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lake_executable() -> str:
    found = shutil.which("lake")
    if found:
        return found
    candidate = Path.home() / ".elan" / "bin" / "lake.exe"
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError("unable to locate lake")


def validate_static() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        return {}, ["formalization manifest is missing"]
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper33.lean-formalization-manifest.v1":
        errors.append("formalization manifest schema mismatch")
    if manifest.get("formalization_id") != "PAPER33-CAPACITY-OBSTRUCTION-SPINE-V1":
        errors.append("formalization identity mismatch")
    if manifest.get("status") != "COMPILED_PAPER_OWNED_PARTIAL_FORMALIZATION":
        errors.append("formalization status drift")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("formalization validation mode mismatch")

    build = manifest.get("build", {})
    if build.get("mathlib_revision") != EXPECTED_MATHLIB_REVISION:
        errors.append("unexpected Mathlib revision")
    if build.get("lean") != "4.33.0":
        errors.append("unexpected Lean version")

    toolchain = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    if toolchain != EXPECTED_TOOLCHAIN:
        errors.append("unexpected Lean toolchain")

    lakefile = (LEAN_ROOT / "lakefile.toml").read_text(encoding="utf-8")
    for marker in (
        'name = "rime_paper33_capacity_spine"',
        'defaultTargets = ["Paper33"]',
        'name = "Paper33"',
        f'rev = "{EXPECTED_MATHLIB_REVISION}"',
    ):
        if marker not in lakefile:
            errors.append(f"lakefile missing {marker!r}")

    lake_manifest = json.loads(
        (LEAN_ROOT / "lake-manifest.json").read_text(encoding="utf-8")
    )
    if lake_manifest.get("name") != "rime_paper33_capacity_spine":
        errors.append("Lake lock has the wrong project identity")
    mathlib = next(
        (
            package
            for package in lake_manifest.get("packages", [])
            if package.get("name") == "mathlib"
        ),
        None,
    )
    if mathlib is None or mathlib.get("rev") != EXPECTED_MATHLIB_REVISION:
        errors.append("Lake lock does not bind the declared Mathlib revision")

    source_hashes = manifest.get("source_sha256", {})
    if set(source_hashes) != {
        "Paper33.lean",
        "Paper33/CapacityObstruction.lean",
        "README.md",
        "lakefile.toml",
        "lake-manifest.json",
        "lean-toolchain",
    }:
        errors.append("formalization source inventory mismatch")
    for relative, digest in source_hashes.items():
        path = LEAN_ROOT / relative
        if not path.is_file():
            errors.append(f"missing formalization file: {relative}")
        elif sha256(path) != digest:
            errors.append(f"formalization file changed: {relative}")

    placeholder = re.compile(r"\b(?:sorry|admit)\b|^\s*axiom\b", re.MULTILINE)
    for relative in EXPECTED_SOURCES:
        source = (LEAN_ROOT / relative).read_text(encoding="utf-8")
        if placeholder.search(source):
            errors.append(f"placeholder or custom axiom in {relative}")

    manuscript = " ".join(
        MANUSCRIPT_PATH.read_text(encoding="utf-8").split()
    )
    for marker in (
        "Theorem 5.1 (capacity-isolated break obstruction)",
        "A paper-owned Lean development machine-checks the data-independent",
        "does not formalize the finite databases",
    ):
        if marker not in manuscript:
            errors.append(f"manuscript surface missing: {marker}")

    readme = " ".join((LEAN_ROOT / "README.md").read_text(encoding="utf-8").split())
    for marker in (
        "The abstract CapacitySystem consumes the concrete facts proved in the manuscript:",
        "The Lean development does not construct the concrete branch",
        "typed transfer membership, projectability, recursive return",
    ):
        if marker not in readme:
            errors.append(f"Lean noncoverage boundary missing: {marker}")
    return manifest, errors


def replay() -> int:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    completed = subprocess.run(
        [lake_executable(), "build"],
        cwd=LEAN_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        output = completed.stdout + completed.stderr
        encoding = sys.stdout.encoding or "utf-8"
        print(output.encode(encoding, errors="backslashreplace").decode(encoding))
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()

    manifest, errors = validate_static()
    if not errors and args.replay and replay():
        errors.append("Lean replay failed")

    if errors:
        print("FAIL Paper XXXIII Lean capacity spine")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "compiled" if args.replay else "static closure checked"
    print(
        "PASS Paper XXXIII Lean capacity spine: "
        f"{mode}; {len(manifest['source_sha256'])} bound files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
