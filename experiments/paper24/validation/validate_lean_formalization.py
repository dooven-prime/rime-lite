#!/usr/bin/env python3
"""Validate the portable Paper XXIV Lean development and its declared scope."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments" / "paper24" / "lean"
MANUSCRIPT_PATH = ROOT / "papers" / "paper24" / "Paper XXIV.md"
MANIFEST_PATH = LEAN_ROOT / "formalization-manifest.json"
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.33.0"
EXPECTED_MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"


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


def main() -> int:
    manuscript = " ".join(MANUSCRIPT_PATH.read_text(encoding="utf-8").split())
    if "This paper is Paper XXIV of the RIME program" not in manuscript:
        raise AssertionError("Paper XXIV publication identity is absent")
    if "finite local-to-global theory for typed section and relation data" not in manuscript:
        raise AssertionError("Paper XXIV mathematical scope is absent")
    if "Exact Admissible-Section Characterization" not in manuscript:
        raise AssertionError("Paper XXIV exact section-descent theorem is absent")
    if "Imported Theorem 6 (Relational Acyclicity Characterization)" not in manuscript:
        raise AssertionError("Paper XXIV imported-theorem boundary is absent")
    if "Relation-valued descent is treated as a different local object type" not in manuscript:
        raise AssertionError("Paper XXIV local-object type boundary is absent")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPILED_PAPER_OWNED_SOURCE_CLOSURE":
        raise AssertionError("unexpected formalization status")
    if manifest["build"]["mathlib_revision"] != EXPECTED_MATHLIB_REVISION:
        raise AssertionError("unexpected Mathlib revision")
    toolchain = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    if toolchain != EXPECTED_TOOLCHAIN:
        raise AssertionError("unexpected Lean toolchain")
    for source, digest in manifest["source_sha256"].items():
        if sha256(LEAN_ROOT / source) != digest:
            raise AssertionError(f"formalization source changed: {source}")
    completed = subprocess.run(
        [lake_executable(), "build", "FiniteTypedContextDescent"],
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
        return 1
    print("PASS Paper XXIV Lean core: declared free-signature scope compiled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
