#!/usr/bin/env python3
"""Validate the source-addressed Paper XXVI public evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper26"
PACKAGE = ROOT / "experiments" / "paper26"
MANIFEST = PACKAGE / "release-manifest.json"
RECEIPT = PACKAGE / "results" / "paper26_public_package_v1.validation-receipt.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper26.pair_chain import (  # noqa: E402
    cerny_transition,
    pair_chain_diagnostics,
    rare_run_transition,
    shortest_reset_length,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def resolve_relative(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"non-canonical release path: {path_text}")
    if any(token in path_text for token in "*?[]"):
        raise ValueError(f"wildcard release path: {path_text}")
    resolved = (ROOT / path).resolve()
    resolved.relative_to(ROOT.resolve())
    return resolved


def artifact_rows(manifest: dict) -> list[dict]:
    rows = [
        {
            "role": "release-manifest",
            "artifact": {
                "uri": MANIFEST.relative_to(ROOT).as_posix(),
                "sha256": sha256(MANIFEST),
            },
        }
    ]
    rows.extend(
        {
            "role": artifact["role"],
            "artifact": {
                "uri": artifact["path"],
                "sha256": artifact["sha256"],
            },
        }
        for artifact in manifest["artifacts"]
    )
    return rows


def build_receipt(manifest: dict, replay: dict) -> dict:
    rows = artifact_rows(manifest)
    receipt = {
        "schema": "rime.paper26.public-package-receipt.v1",
        "artifact_id": "PAPER26-PUBLIC-EVIDENCE-V1-VALIDATED",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "replay": replay,
        "artifact_closure": {
            "artifact_count": len(rows),
            "closure_digest": canonical_digest(rows),
            "ordered_artifacts": rows,
        },
    }
    receipt["content_sha256"] = canonical_digest(receipt)
    return receipt


def close(actual: float, expected: float, tolerance: float, label: str, errors: list[str]) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        errors.append(f"{label}: {actual!r} != {expected!r} within {tolerance}")


def validate_result_sources(payload: dict, errors: list[str]) -> None:
    expected_paths = [
        "experiments/paper26/pair_chain.py",
        "experiments/paper26/generate_family_results.py",
    ]
    observed_paths = [entry.get("path") for entry in payload.get("source_artifacts", [])]
    if observed_paths != expected_paths:
        errors.append("result source inventory mismatch")
        return
    for source in payload["source_artifacts"]:
        path = resolve_relative(source["path"])
        if not path.is_file() or source.get("sha256") != sha256(path):
            errors.append(f"result source digest mismatch: {source['path']}")


def validate_results(errors: list[str]) -> dict:
    cerny = json.loads((PACKAGE / "results/cerny_pair_chain_v1.json").read_text(encoding="utf-8"))
    rare = json.loads((PACKAGE / "results/rare_run_pair_chain_v1.json").read_text(encoding="utf-8"))
    if cerny.get("schema") != "rime.paper26.cerny-pair-chain.v1":
        errors.append("Cerny result schema mismatch")
    if rare.get("schema") != "rime.paper26.rare-run-pair-chain.v1":
        errors.append("rare-run result schema mismatch")

    replay_counts = {"cerny_rows": 0, "rare_run_rows": 0}
    for name, payload in (("cerny", cerny), ("rare-run", rare)):
        numerical = payload.get("evidence", {}).get("numerical_fields", {})
        if numerical.get("status") != "BOUNDED_FLOAT64_OBSERVATION":
            errors.append(f"{name} numerical evidence status mismatch")
        if payload.get("evidence", {}).get("exact_fields", {}).get("status") != (
            "COMPUTATIONAL_REPRODUCTION_OF_PROVED_FORMULAS"
        ):
            errors.append(f"{name} exact evidence status mismatch")
        validate_result_sources(payload, errors)

    cerny_tolerance = float(cerny["evidence"]["numerical_fields"]["absolute_replay_tolerance"])
    if [row.get("n") for row in cerny.get("rows", [])] != list(range(3, 17)):
        errors.append("Cerny row inventory mismatch")
    for row in cerny.get("rows", []):
        n = row["n"]
        transition = cerny_transition(n)
        diagnostics = pair_chain_diagnostics(transition)
        expected_h2 = n**3 - 1.5 * n**2 + (n % 2) / 2
        if row["reset_length"] != shortest_reset_length(transition):
            errors.append(f"Cerny n={n} reset length mismatch")
        close(row["expected_H2"], expected_h2, 0.0, f"Cerny n={n} exact formula", errors)
        close(row["H2"], diagnostics["H2"], cerny_tolerance, f"Cerny n={n} H2 replay", errors)
        close(row["H2"], expected_h2, cerny_tolerance, f"Cerny n={n} H2 formula", errors)
        close(row["gap"], diagnostics["gap"], cerny_tolerance, f"Cerny n={n} gap replay", errors)
        close(row["n3_gap"], n**3 * diagnostics["gap"], cerny_tolerance, f"Cerny n={n} scaled gap", errors)
        close(row["gap_times_H2"], diagnostics["gap"] * diagnostics["H2"], cerny_tolerance, f"Cerny n={n} product", errors)
        replay_counts["cerny_rows"] += 1
    close(cerny.get("pi_squared_over_8", math.nan), math.pi**2 / 8, 1e-15, "pi^2/8", errors)

    rare_tolerance = float(rare["evidence"]["numerical_fields"]["absolute_replay_tolerance"])
    if [row.get("n") for row in rare.get("rows", [])] != list(range(2, 17)):
        errors.append("rare-run row inventory mismatch")
    for row in rare.get("rows", []):
        n = row["n"]
        transition = rare_run_transition(n)
        diagnostics = pair_chain_diagnostics(transition)
        expected_h2 = 2**n - 2
        if row["reset_length"] != shortest_reset_length(transition):
            errors.append(f"rare-run n={n} reset length mismatch")
        close(row["expected_H2"], expected_h2, 0.0, f"rare-run n={n} exact formula", errors)
        close(row["H2"], diagnostics["H2"], rare_tolerance, f"rare-run n={n} H2 replay", errors)
        close(row["H2"], expected_h2, rare_tolerance, f"rare-run n={n} H2 formula", errors)
        close(row["gap"], diagnostics["gap"], rare_tolerance, f"rare-run n={n} gap replay", errors)
        close(row["gap_times_H2"], diagnostics["gap"] * diagnostics["H2"], rare_tolerance, f"rare-run n={n} product", errors)
        replay_counts["rare_run_rows"] += 1

    return {
        "result_mode": "deterministic_recomputation",
        "numeric_arithmetic": "NumPy float64",
        "absolute_tolerance": max(cerny_tolerance, rare_tolerance),
        **replay_counts,
    }


def validate_manuscript_and_claims(errors: list[str]) -> None:
    manuscript = (PAPER / "Paper XXVI.md").read_text(encoding="utf-8")
    bibliography = (PAPER / "references-v1.bib").read_text(encoding="utf-8")
    claims = json.loads((PACKAGE / "claim-surface-map.json").read_text(encoding="utf-8"))

    required = [
        "Four inequivalent synchronization scales",
        "Gusev's uniform-input worst-pair mean, recovered",
        "Theorem 4.6 (Černý PF asymptotic)",
        "Theorem 6.1 (universal envelope)",
        "Proposition 6.2 (sharpness for every alphabet size)",
        "Proposition 6.3 (equality mechanism)",
        "Theorem A.1 (Second-order Černý refinement)",
        "Related Work and Novelty Boundary",
        "qualitative existence of exponentially slow random synchronization",
        "It is not independent",
    ]
    for marker in required:
        if marker not in manuscript:
            errors.append(f"manuscript marker missing: {marker}")
    for forbidden in (
        "release candidate",
        "## References",
        "Three inequivalent synchronization scales",
        "Relation to neighboring literatures",
        "similar at the determinant level",
        r"\=",
        r"\<",
        r"]\(",
    ):
        if forbidden in manuscript:
            errors.append(f"stale manuscript marker: {forbidden}")

    cite_groups = re.findall(r"\\cite\{([^}]+)\}", manuscript)
    cited = {key.strip() for group in cite_groups for key in group.split(",")}
    declared = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bibliography))
    missing = sorted(cited - declared)
    unused = sorted(declared - cited)
    if missing:
        errors.append(f"missing bibliography keys: {missing}")
    if unused:
        errors.append(f"unused bibliography keys: {unused}")
    if "10.1007/978-3-319-09698-8_7" not in bibliography:
        errors.append("Gusev DOI missing from bibliography")
    if "https://doi.org/10.5281/zenodo.22136087" not in bibliography:
        errors.append("Paper XXIII DOI URL missing from bibliography")

    if claims.get("schema") != "rime.paper26.claim-surface-map.v1":
        errors.append("claim-surface schema mismatch")
    by_id = {claim["id"]: claim for claim in claims.get("claims", [])}
    recovery = by_id.get("CERNY_UNIFORM_MEAN_RECOVERY", {})
    if recovery.get("ownership") != "prior_result_recovered_in_paper26_coordinates":
        errors.append("Cerny mean attribution boundary mismatch")
    rare = by_id.get("RARE_RUN_EXTREMAL_REALIZATION", {})
    if "qualitative existence" not in rare.get("boundary", ""):
        errors.append("rare-run prior-work boundary missing")
    if "proof" in by_id.get("CERNY_SECOND_ORDER_REFINEMENT", {}):
        errors.append("supplementary U3 record is incorrectly declared as a proof premise")


def validate_manifest(manifest: dict, errors: list[str]) -> None:
    if manifest.get("schema") != "rime.paper26.release-manifest.v1":
        errors.append("release manifest schema mismatch")
    if manifest.get("paper_id") != "PAPER26" or manifest.get("release_version") != "1.0":
        errors.append("release identity mismatch")
    if manifest.get("status") != "RELEASE_CANDIDATE":
        errors.append("release status mismatch")
    if manifest.get("validation_mode") != "LOCAL_CLOSURE_VERIFICATION":
        errors.append("validation mode mismatch")
    if manifest.get("receipt_self_exclusion") is not True:
        errors.append("receipt self-exclusion is not declared")

    seen: set[str] = set()
    for artifact in manifest.get("artifacts", []):
        path_text = artifact.get("path", "")
        if path_text in seen:
            errors.append(f"duplicate manifest path: {path_text}")
            continue
        seen.add(path_text)
        try:
            path = resolve_relative(path_text)
        except (ValueError, OSError) as error:
            errors.append(str(error))
            continue
        if not path.is_file():
            errors.append(f"missing manifest artifact: {path_text}")
        elif artifact.get("sha256") != sha256(path):
            errors.append(f"manifest digest mismatch: {path_text}")
        if path.resolve() == RECEIPT.resolve():
            errors.append("validation receipt occurs in its own closure")

    required_roles = {
        "manuscript",
        "reader-pdf",
        "bibliography",
        "figure-source",
        "figure-style-helper",
        "figure",
        "evidence-readme",
        "claim-surface-map",
        "release-environment",
        "pair-chain-implementation",
        "family-result-producer",
        "cerny-family-result",
        "rare-run-family-result",
        "lean-formalization-manifest",
        "lean-entrypoint",
        "lean-source",
        "lean-validator",
        "lean-validation-receipt",
        "public-package-validator",
    }
    roles = {artifact.get("role") for artifact in manifest.get("artifacts", [])}
    missing_roles = sorted(required_roles - roles)
    if missing_roles:
        errors.append(f"missing manifest roles: {missing_roles}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    validate_manifest(manifest, errors)
    validate_manuscript_and_claims(errors)
    replay = validate_results(errors)

    lean = subprocess.run(
        [sys.executable, str(PACKAGE / "validation/validate_lean_formalization.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if lean.returncode:
        errors.append(f"Lean closure validation failed: {lean.stdout.strip()} {lean.stderr.strip()}")
    replay["lean_closure_status"] = "PASS" if not lean.returncode else "FAIL"

    expected_receipt = build_receipt(manifest, replay)
    if not errors and args.write_receipt:
        RECEIPT.write_text(
            json.dumps(expected_receipt, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"WROTE {RECEIPT.relative_to(ROOT).as_posix()}")
    elif not errors:
        if not RECEIPT.is_file():
            errors.append("public-package receipt is missing")
        else:
            retained = json.loads(RECEIPT.read_text(encoding="utf-8"))
            if retained != expected_receipt:
                errors.append("public-package receipt differs from current closure or replay")

    if errors:
        print("FAIL Paper XXVI public package")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        "PASS Paper XXVI public package: "
        f"{expected_receipt['artifact_closure']['artifact_count']} bound artifacts, "
        f"closure {expected_receipt['artifact_closure']['closure_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
