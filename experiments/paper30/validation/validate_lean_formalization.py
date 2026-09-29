#!/usr/bin/env python3
"""Validate and optionally replay the Paper XXX partial Lean spine."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments" / "paper30" / "lean"
MANIFEST_PATH = LEAN_ROOT / "formalization-manifest.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper30" / "Paper XXX.md"
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.33.0"
EXPECTED_MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
EXPECTED_SOURCES = (
    "Paper30.lean",
    "Paper30/OrbitReduction.lean",
    "Paper30/CycleGluing.lean",
    "Paper30/BranchFiber.lean",
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
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rime.paper30.lean-formalization-manifest.v1":
        errors.append("formalization manifest schema mismatch")
    if manifest.get("formalization_id") != "PAPER30-RETURN-GROUP-SPINE-V1":
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
        'name = "rime_paper30_spine"',
        'defaultTargets = ["Paper30"]',
        'name = "Paper30"',
        f'rev = "{EXPECTED_MATHLIB_REVISION}"',
    ):
        if marker not in lakefile:
            errors.append(f"lakefile missing {marker!r}")

    lake_manifest = json.loads(
        (LEAN_ROOT / "lake-manifest.json").read_text(encoding="utf-8")
    )
    if lake_manifest.get("name") != "rime_paper30_spine":
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
    for relative, digest in source_hashes.items():
        path = LEAN_ROOT / relative
        if not path.is_file():
            errors.append(f"missing formalization file: {relative}")
        elif sha256(path) != digest:
            errors.append(f"formalization file changed: {relative}")

    placeholder = re.compile(r"\b(?:sorry|admit)\b|^\s*axiom\b", re.MULTILINE)
    for relative in EXPECTED_SOURCES:
        text = (LEAN_ROOT / relative).read_text(encoding="utf-8")
        if placeholder.search(text):
            errors.append(f"placeholder or custom axiom in {relative}")

    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
    for marker in (
        "Theorem 4.1 (exact relation-valued orbit reduction)",
        "Theorem 6.2 (exact cycle-gluing theorem)",
        "Corollary 6.4 (fixed-collision branch fiber and exact gluing",
        "point-orbits of $G_d$ on $D$",
    ):
        if marker not in manuscript:
            errors.append(f"manuscript surface missing: {marker}")

    readme = " ".join((LEAN_ROOT / "README.md").read_text(encoding="utf-8").split())
    for marker in (
        "The development does not formalize:",
        "the punctured-rotation conjugacy or its gcd-dependent cycle type",
        "It does not manufacture Theorem 6.1",
    ):
        if marker not in readme:
            errors.append(f"Lean noncoverage boundary missing: {marker}")
    return manifest, errors


def replay() -> int:
    completed = subprocess.run(
        [lake_executable(), "build"],
        cwd=LEAN_ROOT,
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
        print("FAIL Paper XXX Lean spine")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "compiled" if args.replay else "static closure checked"
    print(
        "PASS Paper XXX Lean spine: "
        f"{mode}; {len(manifest['source_sha256'])} bound files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
