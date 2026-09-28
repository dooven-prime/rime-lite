#!/usr/bin/env python3
"""Build the deterministic Paper XVII result-anchor manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
SOURCE_ROOT = (
    REPO_ROOT
    / "experiments"
    / "exploratory"
    / "male_cns_connectome"
    / "dynamic_compression"
)
OUTPUT = ROOT / "result-anchor.v1.json"

IMPORTED_PATHS = [
    "FINITE_HISTORY_CLOSURE.md",
    "GROSS_BUDGET_RICHNESS_SCOPE.md",
    "audit_finite_history_common_support_v1.py",
    "audit_finite_history_transient_fibers_v1.py",
    "finite_history_binary.py",
    "finite_history_closure.design-v1.json",
    "finite_history_closure.preflight-v1.json",
    "finite_history_closure.preflight-v1.validation-receipt.json",
    "finite_history_closure.registration-v1.json",
    "finite_history_closure.registration-v1.validation-receipt.json",
    "finite_history_d0_cost_envelope.v1.json",
    "finite_history_d0_cost_envelope.v1.validation-receipt.json",
    "finite_history_execution_common.py",
    "finite_history_richness.v1.json",
    "finite_history_richness.v1.validation-receipt.json",
    "finite_history_scope.v1.json",
    "finite_history_scope.v1.validation-receipt.json",
    "freeze_finite_history_closure_v1.py",
    "gross_compute_budget.v1.json",
    "gross_compute_budget.v1.validation-receipt.json",
    "optimized_exact_common.py",
    "requirements-exact-optimized-v1.txt",
    "run_finite_history_closure_v1.py",
    "results/finite_history_D0.v1.npy",
    "results/finite_history_D0_admission.v1.json",
    "results/finite_history_D0_admission.v1.validation-receipt.json",
    "results/finite_history_closure.v1.freeze-manifest.json",
    "results/finite_history_closure.v1.freeze-validation-receipt.json",
    "results/finite_history_closure.v1.json",
    "results/finite_history_closure.v1.sector-labels.json",
    "results/finite_history_closure.v1.sidecar-inventory.json",
    "results/finite_history_closure.v1.sidecar.tar",
    "results/finite_history_closure.v1.validation-receipt.json",
    "results/finite_history_common_support_audit.v1.json",
    "results/finite_history_common_support_audit.v1.validation-receipt.json",
    "results/finite_history_source_universe.v1.json",
    "results/finite_history_source_universe.v1.npy",
    "results/finite_history_transient_fiber_audit.v1.json",
    "results/finite_history_transient_fiber_audit.v1.validation-receipt.json",
    "validation/test_finite_history_binary.py",
    "validation/test_finite_history_classification.py",
    "validation/validate_finite_history_closure_freeze.py",
    "validation/validate_finite_history_closure_v1.py",
    "validation/validate_finite_history_common_support_audit.py",
    "validation/validate_finite_history_transient_fiber_audit.py",
]

LOCAL_PATHS = [
    ".gitattributes",
    "README.md",
    "build_result_anchor.py",
    "validation/validate_result_anchor.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(relative: str, imported: bool) -> dict[str, Any]:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    entry: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if imported:
        source = SOURCE_ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"missing import source: {source}")
        source_sha = sha256_file(source)
        if source_sha != entry["sha256"]:
            raise ValueError(f"import byte mismatch: {relative}")
        entry["import_source"] = {
            "path": source.relative_to(REPO_ROOT).as_posix(),
            "sha256": source_sha,
        }
    return entry


def build_manifest() -> dict[str, Any]:
    artifacts = [artifact(path, True) for path in IMPORTED_PATHS]
    artifacts.extend(artifact(path, False) for path in LOCAL_PATHS)
    return {
        "schema": "rime.paper17.result-anchor.v1",
        "status": "RESULT_OWNED_ANCHOR_READY",
        "candidate_identity": {
            "paper": "Paper XVII",
            "title": "Exact Post-Transient Coarse-State Closure in a Reduced Male Drosophila CNS Model",
            "publication_status": "UNPUBLISHED_CANDIDATE",
        },
        "scope": {
            "source_count": 711,
            "D0_mode": "REDUCED_STRATIFIED_HASH_D0",
            "T": 4,
            "common_support_times": [2, 3],
            "full_domain_claimed": False,
            "indefinite_invariance_claimed": False,
        },
        "evidence_authority": {
            "historical_primary_result": "ORDER_SPECIFIC_DOMAINS_RETAINED_NOT_MINIMAL_MEMORY_AUTHORITY",
            "common_support_correction": "THEOREM_FACING_FINITE_CLASSIFICATION",
            "transient_fiber_decomposition": "THEOREM_FACING_POSTHOC_DESCRIPTIVE_LOCALIZATION",
            "producer_replayed": False,
            "independent_validation": False,
        },
        "canonical_claims": {
            "common_support_closed_noninjective": True,
            "common_support_partitions_identical_across_h_0_1_2": True,
            "minimal_memory_order_identified": False,
            "t1_obstruction_fiber_count": 6,
            "t1_obstruction_source_count": 51,
            "all_obstruction_sources_globally_singleton_at_t2": True,
            "persistent_cohort_sizes": [51, 25, 19, 4, 3],
            "persistent_membership_equal_at_t2_t3": True,
            "mechanism_identified": False,
        },
        "exact_sidecar": {
            "path": "results/finite_history_closure.v1.sidecar.tar",
            "bytes": 34621440,
            "sha256": "5ed5853b43901d927fb43d2ff1926f6bcb79343d95e15e62df8f770259c52ad9",
            "member_count": 1425,
            "ordered_files_sha256": "f8f315329ef93196048341e40ef0dcdb44f784bdd7095d4655e0ec3d3d15c785",
        },
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "receipt_path": "results/result-anchor.v1.validation-receipt.json",
    }


def main() -> int:
    manifest = build_manifest()
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"status": manifest["status"], "artifacts": len(manifest["artifacts"]), "output": OUTPUT.name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
