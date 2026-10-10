#!/usr/bin/env python3
"""Build the deterministic Paper XVII result-anchor manifest."""

from __future__ import annotations

import hashlib
import json
import argparse
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

THEOREM_FACING_IMPORTED_PATHS = [
    "audit_finite_history_common_support_v1.py",
    "audit_finite_history_transient_fibers_v1.py",
    "finite_history_binary.py",
    "freeze_finite_history_closure_v1.py",
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

PACKAGE_ONLY_IMPORTED_PATHS = [
    "FINITE_HISTORY_CLOSURE.md",
    "GROSS_BUDGET_RICHNESS_SCOPE.md",
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
    "gross_compute_budget.v1.json",
    "gross_compute_budget.v1.validation-receipt.json",
    "optimized_exact_common.py",
    "requirements-exact-optimized-v1.txt",
    "run_finite_history_closure_v1.py",
]

THEOREM_FACING_LOCAL_PATHS = [
    "audit_finite_history_terminal_image_v1.py",
    "results/finite_history_terminal_image_audit.v1.json",
    "results/finite_history_terminal_image_audit.v1.validation-receipt.json",
    "validation/validate_finite_history_terminal_image_audit.py",
    "mechanism/results/mechanism_cohort_registry.v1.json",
    "mechanism/mechanism_nontrivial_contrast.registration-v1.json",
    "mechanism/nontrivial_contrast_v1.py",
    "mechanism/mechanism_result_validation_v1.py",
    "mechanism/freeze_mts1_result_v1.py",
    "mechanism/validation/validate_mts1_result_freeze_v1.py",
    "mechanism/results/mts1-v1/inventory.json",
    "mechanism/results/mts1-v1/resource-execution-receipt.json",
    "mechanism/results/mts1-v1/validation/mechanism_classification.v1.json",
    "mechanism/results/mts1-v1/validation/mechanism_validation.v1.receipt.json",
    "mechanism/results/mts1-v1.freeze-manifest.json",
    "mechanism/results/mts1-v1.freeze-validation-receipt.json",
]

PACKAGE_LOCAL_PATHS = [
    ".gitattributes",
    "README.md",
    "build_result_anchor.py",
    "validation/validate_public_package.py",
    "validation/validate_result_anchor.py",
    "mechanism/README.md",
    "mechanism/MECHANISM_OF_TRANSIENT_SEPARATION.md",
    "mechanism/MTS1_SCOPED_EXECUTION_AMENDMENT.md",
    "mechanism/MTS1_RECORD_SCHEMAS.md",
    "mechanism/MTS1_EXACT_TRANSITION_PAYLOAD_CODECS.md",
    "mechanism/MTS1_NONTRIVIAL_CONTRAST.md",
    "mechanism/mechanism_of_transient_separation.registration-v1.json",
    "mechanism/mechanism_of_transient_separation.execution-amendment-v1.json",
    "mechanism/mechanism_record_schema.registration-v1.json",
    "mechanism/mechanism_payload_codecs.registration-v1.json",
    "mechanism/mechanism_source_addressed_producer.registration-v1.json",
    "mechanism/mechanism_resource_contract.v1.json",
    "mechanism/mechanism_validation_resource_gate.registration-v1.json",
    "mechanism/mechanism_mts1_execution_authority.v1.json",
    "mechanism/source_addressed_mechanism_producer_v1.py",
    "mechanism/run_mts1_source_production_capped_v1.py",
    "mechanism/exact_state_payload_v1.py",
    "mechanism/exact_transition_payloads_v1.py",
    "mechanism/mechanism_records_v1.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(
    relative: str,
    closure_class: str,
    historical_import: bool,
    compare_exploratory_source: bool,
) -> dict[str, Any]:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    entry: dict[str, Any] = {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "closure_class": closure_class,
    }
    if historical_import:
        source = SOURCE_ROOT / relative
        entry["import_source"] = {
            "path": source.relative_to(REPO_ROOT).as_posix(),
            "expected_sha256": entry["sha256"],
            "comparison_required_for_default_build": False,
        }
        if compare_exploratory_source:
            if not source.is_file():
                raise FileNotFoundError(f"missing import source: {source}")
            source_sha = sha256_file(source)
            if source_sha != entry["sha256"]:
                raise ValueError(f"import byte mismatch: {relative}")
            entry["import_source"]["comparison_performed"] = True
            entry["import_source"]["observed_sha256"] = source_sha
    return entry


def build_manifest(compare_exploratory_source: bool = False) -> dict[str, Any]:
    artifacts = [
        artifact(path, "theorem_facing_result_replay", True, compare_exploratory_source)
        for path in THEOREM_FACING_IMPORTED_PATHS
    ]
    artifacts.extend(
        artifact(path, "package_only_historical_production_context", True, compare_exploratory_source)
        for path in PACKAGE_ONLY_IMPORTED_PATHS
    )
    artifacts.extend(
        artifact(path, "theorem_facing_result_replay", False, compare_exploratory_source)
        for path in THEOREM_FACING_LOCAL_PATHS
    )
    artifacts.extend(
        artifact(path, "package_only_release_support", False, compare_exploratory_source)
        for path in PACKAGE_LOCAL_PATHS
    )
    class_counts: dict[str, int] = {}
    for entry in artifacts:
        class_counts[entry["closure_class"]] = class_counts.get(entry["closure_class"], 0) + 1
    return {
        "schema": "rime.paper17.result-anchor.v1",
        "status": "RESULT_OWNED_ANCHOR_READY",
        "candidate_identity": {
            "paper": "Paper XVII",
            "title": "Exact Post-Transient Coarse Factorization in a Reduced Male Drosophila CNS Model",
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
            "terminal_image_boundary": "THEOREM_FACING_NEGATIVE_PROMOTION_GATE",
            "post_separation_transition_layer_contrast": "THEOREM_FACING_FINITE_EXACT_CLASSIFICATION",
            "producer_replayed": False,
            "clean_clone_microscopic_generation_verified": False,
            "independent_validation": False,
        },
        "canonical_claims": {
            "common_support_one_step_factorization_noninjective": True,
            "common_support_partitions_identical_across_h_0_1_2": True,
            "coarse_endomap_verified": False,
            "registered_internal_shift_count": 1,
            "minimal_memory_order_identified": False,
            "t1_obstruction_fiber_count": 6,
            "t1_obstruction_source_count": 51,
            "all_obstruction_sources_globally_singleton_at_t2": True,
            "persistent_cohort_sizes": [51, 25, 19, 4, 3],
            "persistent_membership_equal_at_t2_t3": True,
            "post_separation_transition_layer_contrast_verified": True,
            "mts1_source_count": 153,
            "mts1_source_transition_cache_record_count": 459,
            "mts1_pair_transition_record_count": 6975,
            "mts1_comparison_cell_count": 15,
            "mts1_differing_comparison_cell_count": 15,
            "mts1_exact_separator_count": 4,
            "initial_separation_trigger_identified": False,
            "causal_mechanism_identified": False,
        },
        "closure_policy": {
            "default_build_uses_only_paper_owned_bytes": True,
            "exploratory_source_comparison_performed": compare_exploratory_source,
            "historical_production_documents_are_package_only": True,
            "microscopic_generation_closure": "INCOMPLETE_NOT_CLAIMED",
            "exact_result_replay_starts_from": "results/finite_history_closure.v1.sidecar.tar",
            "mts1_compact_result_closure_bound": True,
            "mts1_exact_sidecar_external_anchor": None,
        },
        "exact_sidecar": {
            "path": "results/finite_history_closure.v1.sidecar.tar",
            "bytes": 34621440,
            "sha256": "5ed5853b43901d927fb43d2ff1926f6bcb79343d95e15e62df8f770259c52ad9",
            "member_count": 1425,
            "ordered_files_sha256": "f8f315329ef93196048341e40ef0dcdb44f784bdd7095d4655e0ec3d3d15c785",
        },
        "mts1_exact_sidecar": {
            "inventory_path": "mechanism/results/mts1-v1/inventory.json",
            "inventory_sha256": "80460b331f748e56ab3aba1f93e58dbc111b92dee087018acda79fe32c38709c",
            "ordered_artifact_closure_sha256": "ea6725ad7acdb493ca2ccbe629b477e902f62563b00d25953735961237d86096",
            "artifact_count": 2481,
            "total_bytes": 4837598145,
            "external_immutable_anchor": None,
            "tracked_in_git": False,
        },
        "artifact_count": len(artifacts),
        "artifact_count_by_closure_class": class_counts,
        "artifacts": artifacts,
        "receipt_path": "results/result-anchor.v1.validation-receipt.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compare-exploratory-source",
        action="store_true",
        help="Optionally verify the historical exploratory import without making it a default build dependency.",
    )
    args = parser.parse_args()
    manifest = build_manifest(args.compare_exploratory_source)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"status": manifest["status"], "artifacts": len(manifest["artifacts"]), "output": OUTPUT.name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
