#!/usr/bin/env python3
"""Build and validate the Paper XXIV source-addressed release receipt."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper24"
PACKAGE = ROOT / "experiments" / "paper24"
LEAN = PACKAGE / "lean"
MANIFEST = PACKAGE / "release-manifest.json"
RECEIPT = PACKAGE / "results" / "paper24_release_receipt_v1.json"
LEAN_VALIDATOR = PACKAGE / "validation" / "validate_lean_formalization.py"
FIXTURE_VALIDATOR = PACKAGE / "validation" / "validate_descent_fixtures.py"
MATHLIB_REVISION = "db584cd6d46c92f209a44c0f1c829460d327499d"

RECEIPT_SCHEMA = "paper.contextual-descent.release-receipt.v1"
RECEIPT_KIND = "PAPER_XXIV_LOCAL_RELEASE_CLOSURE_RECEIPT"
VALIDATOR_ID = "paper.contextual-descent.release-validator.python.v1"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha256(payload: dict[str, object]) -> str:
    unsigned = deepcopy(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def repo_path(path: Path) -> str:
    resolved = path.resolve()
    root = ROOT.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"artifact escapes repository root: {path}")
    return resolved.relative_to(root).as_posix()


def artifact_reference(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"missing release artifact: {path}")
    return {"uri": repo_path(path), "sha256": sha256(path)}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> None:
    expected = {
        "schema": "paper.contextual-descent.release-manifest.v1",
        "release_id": "PAPER-XXIV-V1-RELEASE-CANDIDATE",
        "status": "RELEASE_CANDIDATE",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"release manifest constant changed: {key}")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("release artifact registry is empty")
    roles = [row.get("role") for row in artifacts]
    paths = [row.get("path") for row in artifacts]
    if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
        raise ValueError("release artifact roles and paths must be unique")
    required_roles = {
        "manuscript",
        "reader-pdf",
        "bibliography",
        "evidence-readme",
        "lean-entrypoint",
        "lean-formalization-manifest",
        "lean-lake-manifest",
        "lean-project",
        "lean-toolchain",
        "lean-validator",
        "hostile-fixture-validator",
        "hostile-fixture-result",
        "release-validator",
    }
    if not required_roles <= set(roles):
        raise ValueError("release manifest is missing a required artifact role")
    if repo_path(RECEIPT) in paths or any(str(path).endswith("release_receipt_v1.json") for path in paths):
        raise ValueError("release receipt may not enter its own artifact closure")
    for path in paths:
        artifact_reference(ROOT / path)


def artifact_rows(manifest: dict) -> list[dict[str, object]]:
    rows = [
        {"role": row["role"], "artifact": artifact_reference(ROOT / row["path"])}
        for row in manifest["artifacts"]
    ]
    rows.append({"role": "release-manifest", "artifact": artifact_reference(MANIFEST)})
    return rows


def closure_digest(rows: list[dict[str, object]]) -> str:
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def bibliography_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", text))


def citation_keys(text: str) -> set[str]:
    return {
        key.strip()
        for group in re.findall(r"\\cite\{([^}]+)\}", text)
        for key in group.split(",")
    }


def validate_manuscript() -> None:
    manuscript_path = PAPER / "Paper XXIV.md"
    manuscript = manuscript_path.read_text(encoding="utf-8")
    normalized = " ".join(manuscript.split())
    required = (
        "## Abstract",
        "## Notation Table",
        "## Introduction",
        "Theorem 5 (Exact Admissible-Section Characterization)",
        "Corollary 5.1 (Universal Scope-Visibility Characterization)",
        "Imported Theorem 6 (Relational Acyclicity Characterization)",
        "Theorem 7 (Typed Relational Admissible-Descent Characterization)",
        "Theorem 8 (Finite Comparison Reconstruction)",
        "m\\ge 1",
        "A_{ij}:=A_i\\cap A_j",
        "No categorical pullback",
        "## Evidence Boundary",
        "## Claim Status and Boundary",
        "## Conclusion",
        "## Appendix A: Computational Artifacts",
        "Theorem 8: comparison reconstruction",
        "typed partial-map statement is a direct specialization",
        "not a novelty claim here",
    )
    for anchor in required:
        if anchor not in normalized:
            raise ValueError(f"manuscript release anchor is missing: {anchor}")
    forbidden = (
        "C_i\\cap_C C_j",
        "new sheaf theorem",
        "Lean formalization of Theorems 5, 7, or 8",
        "## References",
        "earlier draft",
        "INDEPENDENT_MATHEMATICAL_REVIEW",
        "test_paper24_contextual_descent",
    )
    for phrase in forbidden:
        if phrase in normalized:
            raise ValueError(f"forbidden manuscript overclaim or stale notation: {phrase}")

    bibliography = (PAPER / "references-v1.0.bib").read_text(encoding="utf-8")
    missing = citation_keys(manuscript) - bibliography_keys(bibliography)
    if missing:
        raise ValueError(f"missing bibliography keys: {sorted(missing)}")


def validate_mathlib_closure() -> dict[str, object]:
    formalization = load_json(LEAN / "formalization-manifest.json")
    if formalization.get("status") != "COMPILED_PAPER_OWNED_SOURCE_CLOSURE":
        raise ValueError("Lean formalization status changed")
    if formalization["build"].get("mathlib_revision") != MATHLIB_REVISION:
        raise ValueError("formalization manifest Mathlib revision changed")
    for name, expected in formalization["source_sha256"].items():
        path = LEAN / name
        if sha256(path) != expected:
            raise ValueError(f"formalization source digest mismatch: {name}")

    lake_manifest = load_json(LEAN / "lake-manifest.json")
    packages = {row["name"]: row for row in lake_manifest.get("packages", [])}
    mathlib = packages.get("mathlib")
    if not mathlib or mathlib.get("rev") != MATHLIB_REVISION:
        raise ValueError("lake manifest does not pin the declared Mathlib revision")
    if mathlib.get("url") != "https://github.com/leanprover-community/mathlib4.git":
        raise ValueError("lake manifest Mathlib source changed")
    if (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip() != "leanprover/lean4:v4.33.0":
        raise ValueError("Lean toolchain changed")
    return {
        "status": "PINNED_REVISION_CLOSURE_NOT_VENDORED_SOURCE",
        "mathlib_revision": MATHLIB_REVISION,
        "lake_manifest": artifact_reference(LEAN / "lake-manifest.json"),
        "formalization_manifest": artifact_reference(LEAN / "formalization-manifest.json"),
        "lean_toolchain": artifact_reference(LEAN / "lean-toolchain"),
        "transitive_package_count": len(packages),
    }


def run_validator(path: Path) -> str:
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (completed.stdout + completed.stderr).strip()
    if completed.returncode:
        raise ValueError(f"subvalidator failed: {repo_path(path)}: {output}")
    return output


def build_receipt() -> dict[str, object]:
    manifest = load_json(MANIFEST)
    validate_manifest(manifest)
    validate_manuscript()
    mathlib_closure = validate_mathlib_closure()
    fixture_output = run_validator(FIXTURE_VALIDATOR)
    lean_output = run_validator(LEAN_VALIDATOR)
    rows = artifact_rows(manifest)

    receipt: dict[str, object] = {
        "schema": RECEIPT_SCHEMA,
        "release_id": manifest["release_id"],
        "receipt_id": "PAPER-XXIV-V1-LOCAL-RELEASE-CLOSURE",
        "receipt_kind": RECEIPT_KIND,
        "status": "PASS",
        "date": "2026-08-28",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "artifact_closure": {
            "artifact_count": len(rows),
            "ordered_artifacts": rows,
            "closure_digest": closure_digest(rows),
            "receipt_in_own_closure": False,
        },
        "mathlib_closure": mathlib_closure,
        "replay": {
            "lean": {
                "status": "PASS",
                "validator": artifact_reference(LEAN_VALIDATOR),
                "output": lean_output,
                "formalized_surface": [
                    "free coverage and separatedness",
                    "free gluing of compatible local sections",
                    "three-label missing-coordinate nonseparation witness",
                ],
                "excluded_surface": [
                    "Theorem 5 and Corollary 5.1",
                    "Imported Theorem 6",
                    "Theorem 7",
                    "Theorem 8",
                ],
            },
            "finite_hostile_fixtures": {
                "status": "PASS",
                "validator": artifact_reference(FIXTURE_VALIDATOR),
                "result": artifact_reference(PACKAGE / "results" / "descent_hostile_fixtures_v1.json"),
                "output": fixture_output,
                "boundary": "two exact finite controls; not a proof of general relational acyclicity",
            },
        },
        "validator": {
            "validator_id": VALIDATOR_ID,
            "implementation": artifact_reference(Path(__file__).resolve()),
            "boundary": "self-bound local validator; implementation trust is not independently established",
        },
        "claim_boundary": {
            "certifies": (
                "declared release bytes, pinned Lean/Mathlib manifest closure, "
                "local Lean compilation, and exact hostile-fixture replay"
            ),
            "does_not_certify": [
                "independent proof of manuscript Theorems 5, 7, or 8",
                "a new sheaf or relational-acyclicity theorem",
                "independent validation of the release validator implementation",
                "vendored Mathlib source bytes beyond the pinned revision manifest",
                "a concrete Paper XIII comparison or audit",
            ],
        },
    }
    receipt["content_sha256"] = content_sha256(receipt)
    return receipt


def validate_receipt(receipt: dict) -> None:
    if receipt.get("content_sha256") != content_sha256(receipt):
        raise ValueError("release receipt content digest mismatch")
    expected = build_receipt()
    if receipt != expected:
        raise ValueError("release receipt differs from the current declared closure")
    closure_uris = {
        row["artifact"]["uri"]
        for row in receipt["artifact_closure"]["ordered_artifacts"]
    }
    if repo_path(RECEIPT) in closure_uris:
        raise ValueError("release receipt is included in its own closure")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    if args.write_receipt:
        receipt = build_receipt()
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"WROTE {repo_path(RECEIPT)}")

    if not RECEIPT.is_file():
        print(f"FAIL missing release receipt: {repo_path(RECEIPT)}")
        return 1
    try:
        validate_receipt(load_json(RECEIPT))
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {repo_path(RECEIPT)}: {exc}")
        return 1
    print("PASS PAPER-XXIV-V1-LOCAL-RELEASE-CLOSURE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
