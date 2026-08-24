#!/usr/bin/env python3
"""Compile and validate the paper-owned Paper XXI Lean source closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAN_ROOT = ROOT / "experiments" / "paper21" / "lean"
ENTRYPOINT = LEAN_ROOT / "FiniteFieldRouteProfiles.lean"
MANIFEST_PATH = LEAN_ROOT / "formalization-manifest.json"
DEFAULT_RECEIPT = (
    ROOT
    / "experiments"
    / "paper21"
    / "results"
    / "route_profiles_lean_v1.validation-receipt.json"
)
CLOSURE_SOURCES = (
    "FiniteFieldRouteProfiles.lean",
    "Formalization/UniformModularZeroRoute.lean",
    "Formalization/UniformModularZeroRouteField.lean",
    "lake-manifest.json",
    "lakefile.toml",
    "lean-toolchain",
)
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.33.0"
EXPECTED_MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"
EXPECTED_STATUS = "COMPILED_PAPER_OWNED_SOURCE_CLOSURE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    candidate = Path.home() / ".elan" / "bin" / f"{name}.exe"
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError(f"unable to locate {name}")


def validate_pins(manifest: dict) -> None:
    toolchain = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    if toolchain != EXPECTED_TOOLCHAIN:
        raise AssertionError(f"unexpected Lean toolchain: {toolchain}")
    lakefile = (LEAN_ROOT / "lakefile.toml").read_text(encoding="utf-8")
    if f'rev = "{EXPECTED_MATHLIB_REVISION}"' not in lakefile:
        raise AssertionError("Mathlib revision is not pinned as declared")
    if manifest.get("status") != EXPECTED_STATUS:
        raise AssertionError("formalization is not a paper-owned source closure")
    build = manifest["build"]
    expected_build = {
        "project_root": "experiments/paper21/lean",
        "command": (
            "lake build Formalization.UniformModularZeroRouteField "
            "&& lake env lean FiniteFieldRouteProfiles.lean"
        ),
        "lean": "4.33.0",
        "lake": "5.0.0",
        "mathlib_revision": EXPECTED_MATHLIB_REVISION,
    }
    if build != expected_build:
        raise AssertionError("formalization build declaration changed")
    declared = manifest.get("source_sha256", {})
    for source in CLOSURE_SOURCES:
        if declared.get(source) != sha256(LEAN_ROOT / source):
            raise AssertionError(f"formalization source changed: {source}")


def build_receipt() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    validate_pins(manifest)
    lake = executable("lake")
    library_build = subprocess.run(
        [lake, "build", "Formalization.UniformModularZeroRouteField"],
        cwd=LEAN_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if library_build.returncode:
        raise AssertionError(
            "Lean library build failed:\n"
            + library_build.stdout
            + library_build.stderr
        )
    completed = subprocess.run(
        [lake, "env", "lean", ENTRYPOINT.name],
        cwd=LEAN_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        raise AssertionError(
            "Lean compilation failed:\n" + completed.stdout + completed.stderr
        )
    closure = {
        repo_path(LEAN_ROOT / source): sha256(LEAN_ROOT / source)
        for source in CLOSURE_SOURCES
    }
    closure[repo_path(MANIFEST_PATH)] = sha256(MANIFEST_PATH)
    validator_path = Path(__file__).resolve()
    receipt = {
        "schema": "paper.route-profiles.lean-validation-receipt.v1",
        "artifact_id": "ROUTE-PROFILES-LEAN-V1-COMPILED",
        "receipt_kind": "LEAN_COMPILATION_RECEIPT",
        "receipt_scope": "PAPER_OWNED_ROUTE_PROFILE_FORMALIZATION_COMPILATION",
        "status": "PASS",
        "environment": {
            "lean_toolchain": EXPECTED_TOOLCHAIN,
            "lake": "5.0.0",
            "mathlib_revision": EXPECTED_MATHLIB_REVISION,
            "formalization_root_role": "PAPER_OWNED_SOURCE_CLOSURE",
        },
        "source_closure": closure,
        "validator": {
            "path": repo_path(validator_path),
            "sha256": sha256(validator_path),
        },
        "compiler_diagnostics": {
            "warning_count": library_build.stderr.count("warning:")
            + library_build.stdout.count("warning:")
            + completed.stderr.count("warning:")
            + completed.stdout.count("warning:"),
            "error_count": 0,
        },
        "claim_boundary": {
            "certifies": (
                "source elaboration and theorem type checking for the declared "
                "paper-owned closure under pinned Lean and Mathlib versions"
            ),
            "does_not_certify": [
                "equivalence between Python replay and Lean theorem proofs",
                "formal coverage of every manuscript theorem",
            ],
        },
    }
    receipt["content_sha256"] = content_digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write_receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if not args.receipt.is_file():
        print(f"FAIL missing Lean receipt: {args.receipt}")
        return 1
    retained = json.loads(args.receipt.read_text(encoding="utf-8"))
    if retained != receipt:
        print(f"FAIL stale Lean receipt: {args.receipt}")
        return 1
    print(
        f"compiled {receipt['artifact_id']}: "
        f"{receipt['compiler_diagnostics']['warning_count']} warnings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
