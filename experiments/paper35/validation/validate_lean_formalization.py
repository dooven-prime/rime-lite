#!/usr/bin/env python3
"""Validate and optionally replay the Paper XXXV Lean theorem spine."""

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
LEAN_ROOT = ROOT / "experiments" / "paper35" / "lean"
MANIFEST_PATH = LEAN_ROOT / "formalization-manifest.json"
MANUSCRIPT_PATH = ROOT / "papers" / "paper35" / "Paper XXXV.md"
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.33.0"
EXPECTED_MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
EXPECTED_SOURCES = (
    "Paper35.lean",
    "Paper35/PhaseCollapse.lean",
    "Paper35/LeftCosets.lean",
    "Paper35/SurvivorFrontier.lean",
)
EXPECTED_INVENTORY = {
    *EXPECTED_SOURCES,
    "README.md",
    "lakefile.toml",
    "lake-manifest.json",
    "lean-toolchain",
}


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
    if manifest.get("schema") != "rime.paper35.lean-formalization-manifest.v1":
        errors.append("formalization manifest schema mismatch")
    if manifest.get("formalization_id") != "PAPER35-ORDER-PHASE-SPINE-V1":
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
        'name = "rime_paper35_order_phase_spine"',
        'defaultTargets = ["Paper35"]',
        'name = "Paper35"',
        f'rev = "{EXPECTED_MATHLIB_REVISION}"',
    ):
        if marker not in lakefile:
            errors.append(f"lakefile missing {marker!r}")

    lake_manifest = json.loads(
        (LEAN_ROOT / "lake-manifest.json").read_text(encoding="utf-8")
    )
    if lake_manifest.get("name") != "rime_paper35_order_phase_spine":
        errors.append("Lake lock has the wrong project identity")
    if lake_manifest.get("packagesDir") != ".lake/packages":
        errors.append("Lake lock has a nonstandard packages directory")
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
    if set(source_hashes) != EXPECTED_INVENTORY:
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
        "Theorem A (order reduction)",
        "Theorem 4.2 (all-hole terminal-phase collapse; Theorem B)",
        "Theorem C (complete one-lane survivor frontier)",
        "A paper-owned Lean formalization machine-checks",
        "does not formalize the concrete guarded order graph",
    ):
        if marker not in manuscript:
            errors.append(f"manuscript surface missing: {marker}")

    readme = " ".join((LEAN_ROOT / "README.md").read_text(encoding="utf-8").split())
    for marker in (
        "consumes the manuscript's order-fiber saturation",
        "does not prove the eight-pattern",
        "makes no minimality statement and proves no converse",
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
        print("FAIL Paper XXXV Lean theorem spine")
        for error in errors:
            print(f"  - {error}")
        return 1
    mode = "compiled" if args.replay else "static closure checked"
    print(
        "PASS Paper XXXV Lean theorem spine: "
        f"{mode}; {len(manifest['source_sha256'])} bound files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
