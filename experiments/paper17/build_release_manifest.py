#!/usr/bin/env python3
"""Build the exact Paper XVII release-candidate manifest."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUTPUT = ROOT / "release-manifest.v1.json"


ARTIFACTS = [
    ("canonical-manuscript", "theorem-facing-manuscript", "papers/paper17/Paper XVII.md"),
    ("reader-pdf", "theorem-facing-manuscript", "papers/paper17/paper17_arxiv.pdf"),
    ("bibliography-slice", "theorem-facing-manuscript", "papers/paper17/references-v1.bib"),
    ("figure", "theorem-facing-presentation", "figures/paper17/fig1_transient_separation_and_safe_forgetting.png"),
    ("figure-producer", "theorem-facing-presentation", "figures/paper17/render_fig1.py"),
    ("mechanism-figure", "theorem-facing-presentation", "figures/paper17/fig2_internal_transition_layer_contrast.png"),
    ("mechanism-figure-producer", "theorem-facing-presentation", "figures/paper17/render_fig2.py"),
    ("figure-runtime-lock", "theorem-facing-presentation", "figures/paper17/requirements.txt"),
    ("release-environment", "release-validation", "experiments/paper17/release-environment.json"),
    ("evidence-table", "theorem-facing-computational", "experiments/paper17/manuscript-evidence-table.v1.json"),
    ("evidence-table-receipt", "theorem-facing-computational", "experiments/paper17/results/manuscript-evidence-table.v1.validation-receipt.json"),
    ("evidence-table-validator", "release-validation", "experiments/paper17/validation/validate_manuscript_evidence_table.py"),
    ("registered-scope", "theorem-facing-computational", "experiments/paper17/finite_history_scope.v1.json"),
    ("D0-admission", "theorem-facing-computational", "experiments/paper17/results/finite_history_D0_admission.v1.json"),
    ("D0-admission-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_D0_admission.v1.validation-receipt.json"),
    ("D0-index", "theorem-facing-computational", "experiments/paper17/results/finite_history_D0.v1.npy"),
    ("source-universe", "theorem-facing-computational", "experiments/paper17/results/finite_history_source_universe.v1.json"),
    ("source-universe-index", "theorem-facing-computational", "experiments/paper17/results/finite_history_source_universe.v1.npy"),
    ("sector-labels", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.sector-labels.json"),
    ("primary-result", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.json"),
    ("primary-result-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.validation-receipt.json"),
    ("exact-sidecar", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.sidecar.tar"),
    ("sidecar-inventory", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.sidecar-inventory.json"),
    ("sidecar-freeze-manifest", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.freeze-manifest.json"),
    ("sidecar-freeze-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_closure.v1.freeze-validation-receipt.json"),
    ("binary-codec", "theorem-facing-computational", "experiments/paper17/finite_history_binary.py"),
    ("common-support-producer", "theorem-facing-computational", "experiments/paper17/audit_finite_history_common_support_v1.py"),
    ("common-support-result", "theorem-facing-computational", "experiments/paper17/results/finite_history_common_support_audit.v1.json"),
    ("common-support-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_common_support_audit.v1.validation-receipt.json"),
    ("common-support-validator", "release-validation", "experiments/paper17/validation/validate_finite_history_common_support_audit.py"),
    ("transient-fiber-producer", "theorem-facing-computational", "experiments/paper17/audit_finite_history_transient_fibers_v1.py"),
    ("transient-fiber-result", "theorem-facing-computational", "experiments/paper17/results/finite_history_transient_fiber_audit.v1.json"),
    ("transient-fiber-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_transient_fiber_audit.v1.validation-receipt.json"),
    ("transient-fiber-validator", "release-validation", "experiments/paper17/validation/validate_finite_history_transient_fiber_audit.py"),
    ("terminal-image-producer", "theorem-facing-computational", "experiments/paper17/audit_finite_history_terminal_image_v1.py"),
    ("terminal-image-result", "theorem-facing-computational", "experiments/paper17/results/finite_history_terminal_image_audit.v1.json"),
    ("terminal-image-receipt", "theorem-facing-computational", "experiments/paper17/results/finite_history_terminal_image_audit.v1.validation-receipt.json"),
    ("terminal-image-validator", "release-validation", "experiments/paper17/validation/validate_finite_history_terminal_image_audit.py"),
    ("mechanism-cohort-registry", "theorem-facing-computational", "experiments/paper17/mechanism/results/mechanism_cohort_registry.v1.json"),
    ("mechanism-contrast-policy", "theorem-facing-computational", "experiments/paper17/mechanism/mechanism_nontrivial_contrast.registration-v1.json"),
    ("mechanism-sidecar-inventory", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1/inventory.json"),
    ("mechanism-resource-receipt", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1/resource-execution-receipt.json"),
    ("mechanism-classification", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1/validation/mechanism_classification.v1.json"),
    ("mechanism-validation-receipt", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1/validation/mechanism_validation.v1.receipt.json"),
    ("mechanism-freeze-manifest", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1.freeze-manifest.json"),
    ("mechanism-freeze-receipt", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1.freeze-validation-receipt.json"),
    ("mechanism-global-pair-tally", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1.global-pair-tally.v1.json"),
    ("mechanism-global-pair-tally-receipt", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1.global-pair-tally.v1.validation-receipt.json"),
    ("mechanism-zenodo-sidecar-anchor", "theorem-facing-computational", "experiments/paper17/mechanism/results/mts1-v1.zenodo-anchor.v1.json"),
    ("mechanism-global-pair-tally-validator", "release-validation", "experiments/paper17/mechanism/audit_global_pair_tally_v1.py"),
    ("mechanism-evidence-interface-validator", "release-validation", "experiments/paper17/validation/validate_mts1_evidence_interface_v1.py"),
    ("mechanism-zenodo-anchor-binder", "release-validation", "experiments/paper17/mechanism/bind_mts1_zenodo_anchor_v1.py"),
    ("mechanism-contrast-logic", "release-validation", "experiments/paper17/mechanism/nontrivial_contrast_v1.py"),
    ("mechanism-result-validator", "release-validation", "experiments/paper17/mechanism/mechanism_result_validation_v1.py"),
    ("mechanism-freeze-builder", "release-validation", "experiments/paper17/mechanism/freeze_mts1_result_v1.py"),
    ("mechanism-freeze-validator", "release-validation", "experiments/paper17/mechanism/validation/validate_mts1_result_freeze_v1.py"),
    ("freeze-validator", "release-validation", "experiments/paper17/validation/validate_finite_history_closure_freeze.py"),
    ("result-validator", "release-validation", "experiments/paper17/validation/validate_finite_history_closure_v1.py"),
    ("binary-codec-test", "release-validation", "experiments/paper17/validation/test_finite_history_binary.py"),
    ("classification-test", "release-validation", "experiments/paper17/validation/test_finite_history_classification.py"),
    ("public-package-validator", "release-validation", "experiments/paper17/validation/validate_public_package.py"),
    ("release-validator", "release-validation", "experiments/paper17/validation/validate_release.py"),
    ("release-manifest-builder", "release-validation", "experiments/paper17/build_release_manifest.py"),
    ("historical-package-readme", "package-only-historical-production-context", "experiments/paper17/README.md"),
    ("current-evidence-guide", "public-package-documentation", "experiments/paper17/00_START_HERE.md"),
    ("result-anchor", "public-package-documentation", "experiments/paper17/result-anchor.v1.json"),
    ("result-anchor-receipt", "public-package-documentation", "experiments/paper17/results/result-anchor.v1.validation-receipt.json"),
    ("result-anchor-builder", "public-package-documentation", "experiments/paper17/build_result_anchor.py"),
    ("result-anchor-validator", "public-package-documentation", "experiments/paper17/validation/validate_result_anchor.py"),
    ("historical-design-note", "package-only-historical-production-context", "experiments/paper17/FINITE_HISTORY_CLOSURE.md"),
    ("historical-scope-note", "package-only-historical-production-context", "experiments/paper17/GROSS_BUDGET_RICHNESS_SCOPE.md"),
    ("historical-design-record", "package-only-historical-production-context", "experiments/paper17/finite_history_closure.design-v1.json"),
    ("historical-preflight", "package-only-historical-production-context", "experiments/paper17/finite_history_closure.preflight-v1.json"),
    ("historical-preflight-receipt", "package-only-historical-production-context", "experiments/paper17/finite_history_closure.preflight-v1.validation-receipt.json"),
    ("historical-registration", "package-only-historical-production-context", "experiments/paper17/finite_history_closure.registration-v1.json"),
    ("historical-registration-receipt", "package-only-historical-production-context", "experiments/paper17/finite_history_closure.registration-v1.validation-receipt.json"),
    ("historical-cost-envelope", "package-only-historical-production-context", "experiments/paper17/finite_history_d0_cost_envelope.v1.json"),
    ("historical-cost-envelope-receipt", "package-only-historical-production-context", "experiments/paper17/finite_history_d0_cost_envelope.v1.validation-receipt.json"),
    ("historical-richness", "package-only-historical-production-context", "experiments/paper17/finite_history_richness.v1.json"),
    ("historical-richness-receipt", "package-only-historical-production-context", "experiments/paper17/finite_history_richness.v1.validation-receipt.json"),
    ("historical-scope-receipt", "package-only-historical-production-context", "experiments/paper17/finite_history_scope.v1.validation-receipt.json"),
    ("historical-gross-budget", "package-only-historical-production-context", "experiments/paper17/gross_compute_budget.v1.json"),
    ("historical-gross-budget-receipt", "package-only-historical-production-context", "experiments/paper17/gross_compute_budget.v1.validation-receipt.json"),
    ("historical-freeze-builder", "package-only-historical-production-context", "experiments/paper17/freeze_finite_history_closure_v1.py"),
    ("historical-byte-policy", "package-only-historical-production-context", "experiments/paper17/.gitattributes"),
    ("historical-runner", "package-only-historical-production-context", "experiments/paper17/run_finite_history_closure_v1.py"),
    ("historical-execution-common", "package-only-historical-production-context", "experiments/paper17/finite_history_execution_common.py"),
    ("historical-optimized-common", "package-only-historical-production-context", "experiments/paper17/optimized_exact_common.py"),
    ("historical-runtime-lock", "package-only-historical-production-context", "experiments/paper17/requirements-exact-optimized-v1.txt"),
    ("mechanism-readme", "package-only-historical-production-context", "experiments/paper17/mechanism/README.md"),
    ("mechanism-design-note", "package-only-historical-production-context", "experiments/paper17/mechanism/MECHANISM_OF_TRANSIENT_SEPARATION.md"),
    ("mechanism-execution-note", "package-only-historical-production-context", "experiments/paper17/mechanism/MTS1_SCOPED_EXECUTION_AMENDMENT.md"),
    ("mechanism-record-note", "package-only-historical-production-context", "experiments/paper17/mechanism/MTS1_RECORD_SCHEMAS.md"),
    ("mechanism-codec-note", "package-only-historical-production-context", "experiments/paper17/mechanism/MTS1_EXACT_TRANSITION_PAYLOAD_CODECS.md"),
    ("mechanism-contrast-note", "package-only-historical-production-context", "experiments/paper17/mechanism/MTS1_NONTRIVIAL_CONTRAST.md"),
    ("mechanism-registration", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_of_transient_separation.registration-v1.json"),
    ("mechanism-execution-amendment", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_of_transient_separation.execution-amendment-v1.json"),
    ("mechanism-record-registration", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_record_schema.registration-v1.json"),
    ("mechanism-codec-registration", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_payload_codecs.registration-v1.json"),
    ("mechanism-producer-registration", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_source_addressed_producer.registration-v1.json"),
    ("mechanism-resource-contract", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_resource_contract.v1.json"),
    ("mechanism-resource-gate", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_validation_resource_gate.registration-v1.json"),
    ("mechanism-execution-authority", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_mts1_execution_authority.v1.json"),
    ("mechanism-execution-authority-receipt", "package-only-historical-production-context", "experiments/paper17/mechanism/results/mechanism_mts1_execution_authority.v1.validation-receipt.json"),
    ("mechanism-source-producer", "package-only-historical-production-context", "experiments/paper17/mechanism/source_addressed_mechanism_producer_v1.py"),
    ("mechanism-capped-runner", "package-only-historical-production-context", "experiments/paper17/mechanism/run_mts1_source_production_capped_v1.py"),
    ("mechanism-state-codec", "package-only-historical-production-context", "experiments/paper17/mechanism/exact_state_payload_v1.py"),
    ("mechanism-transition-codecs", "package-only-historical-production-context", "experiments/paper17/mechanism/exact_transition_payloads_v1.py"),
    ("mechanism-record-codec", "package-only-historical-production-context", "experiments/paper17/mechanism/mechanism_records_v1.py"),
]

IDENTITY_CLASSES = {
    "theorem-facing-manuscript",
    "theorem-facing-presentation",
    "theorem-facing-computational",
    "release-validation",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def closure_digest(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(entry["bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def build_manifest() -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    seen: set[str] = set()
    anchor = json.loads((ROOT / "result-anchor.v1.json").read_text(encoding="utf-8"))
    anchor_paths = {f"experiments/paper17/{entry['path']}" for entry in anchor["artifacts"]}
    declared_paths = {relative for _, _, relative in ARTIFACTS}
    missing = sorted(anchor_paths - declared_paths)
    if missing:
        raise ValueError(f"release inventory omits result-anchor artifacts: {missing}")
    for role, closure_class, relative in ARTIFACTS:
        if relative in seen:
            raise ValueError(f"duplicate artifact: {relative}")
        seen.add(relative)
        path = REPO / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        artifacts.append(
            {
                "role": role,
                "closure_class": closure_class,
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    identity = [entry for entry in artifacts if entry["closure_class"] in IDENTITY_CLASSES]
    counts = Counter(entry["closure_class"] for entry in artifacts)
    return {
        "schema": "rime.paper17.release-manifest.v1",
        "paper_id": "PAPER17",
        "release_version": "1.0-candidate",
        "status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "receipt_self_exclusion": True,
        "digest_policy": {
            "algorithm": "sha256",
            "scope": "exact_file_bytes",
            "path_resolution": "exact repository-relative path",
            "wildcards_allowed": False,
            "absolute_paths_allowed": False,
        },
        "release_identity": {
            "canonical_manuscript": "papers/paper17/Paper XVII.md",
            "reader_pdf": "papers/paper17/paper17_arxiv.pdf",
            "historical_evidence_commit": "99e2ac5a57afed27e5f213f658ddd5c3e6e93932",
            "release_content_commit": None,
            "external_anchor": None,
            "ordered_artifact_count": len(identity),
            "ordered_closure_sha256": closure_digest(identity),
        },
        "generation_closure": {
            "status": "INCOMPLETE_NOT_CLAIMED",
            "exact_result_replay_starts_from": "experiments/paper17/results/finite_history_closure.v1.sidecar.tar",
            "microscopic_producer_replayed": False,
            "clean_clone_generation_verified": False,
            "missing_historical_execution_dependencies": [
                "validation/validate_finite_history_closure_registration.py",
                "optimized_exact_sparse_kernel.pyx",
                "optimized_exact_implementation_benchmark.registration-v1.json",
                ".runtime-work/optimized-cache/manifest.json",
                ".runtime-work/k/optimized_exact_sparse_kernel.cp312-win_amd64.pyd",
            ],
            "mechanism_production": {
                "status": "LOCAL_EXECUTION_COMPLETED_COMPACT_CLOSURE_ONLY",
                "execution_authority": "NONE_COMPLETED",
                "source_producer_executed": True,
                "exhaustive_validator_completed": True,
                "clean_clone_producer_replay_verified": False,
                "exact_sidecar_tracked_in_git": False,
                "exact_sidecar_external_immutable_anchor": {
                    "doi": "10.5281/zenodo.23234143",
                    "binding": "experiments/paper17/mechanism/results/mts1-v1.zenodo-anchor.v1.json",
                    "binding_mode": "POST_FREEZE_PUBLIC_SPLIT_DEPOSIT",
                },
                "compact_freeze_manifest": "experiments/paper17/mechanism/results/mts1-v1.freeze-manifest.json",
            },
        },
        "registration_timing_boundary": {
            "declared_preexecution_record": True,
            "independently_anchored_before_execution": False,
            "first_joint_git_commit": "99e2ac5a57afed27e5f213f658ddd5c3e6e93932",
        },
        "claim_boundaries": {
            "coarse_endomap_verified": False,
            "indefinite_iteration_verified": False,
            "full_domain_claimed": False,
            "minimal_memory_order_claimed": False,
            "causal_mechanism_identified": False,
            "initial_separation_trigger_identified": False,
            "independent_validation": False,
        },
        "verified_claims": {
            "post_separation_transition_layer_contrast": True,
            "mechanism_source_count": 153,
            "mechanism_source_transition_cache_record_count": 459,
            "mechanism_pair_transition_record_count": 6975,
            "mechanism_comparison_cell_count": 15,
            "mechanism_differing_comparison_cell_count": 15,
            "mechanism_exact_separator_count": 4,
            "mechanism_global_post_separation_pair_tally_bound": True,
            "mechanism_universal_separator_at_1_to_2": False,
        },
        "artifact_count": len(artifacts),
        "artifact_count_by_closure_class": dict(sorted(counts.items())),
        "artifacts": artifacts,
        "receipt_path": "experiments/paper17/results/release.v1.validation-receipt.json",
    }


def main() -> int:
    manifest = build_manifest()
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": manifest["status"], "artifact_count": manifest["artifact_count"], "output": OUTPUT.name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
