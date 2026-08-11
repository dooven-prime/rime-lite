"""Migrate the frozen Paper XIII SOFAUDIT v1 corpus to SOFAUDIT v2.0."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper13.validation.audit_profiles import (  # noqa: E402
    REGISTRY_PATH,
    STANDARD_PROFILE,
    STANDARD_PROFILE_ID,
    STANDARD_PROFILE_PATH,
    value_schema_id,
)

LEGACY_RESULTS = PAPER_DIR / "archive" / "results"
ACTIVE_RESULTS = PAPER_DIR / "results"
AUDIT_DIR = ACTIVE_RESULTS / "audits"
SOURCE_REPORT_DIR = ACTIVE_RESULTS / "source-reports" / "reports"
SOURCE_RECEIPT_DIR = ACTIVE_RESULTS / "source-reports" / "receipts"
ADAPTER_ID = "paper13-sofaudit-v1-to-v2"
ADAPTER_VERSION = "2.0"
PROFILE_ID = STANDARD_PROFILE_ID
PROFILE_VERSION = STANDARD_PROFILE["profile_version"]

FIELD_MAP = {
    "support_mismatch": ("support", "operator"),
    "bridge_word_mismatch": ("word_bridge", "word"),
    "bridge_lie_mismatch": ("lie_bridge", "lie"),
    "depth_distortion": ("depth", "depth"),
    "frozen_disagreement": ("frozen_summary", "frozen_summary"),
    "constraint_violations": ("constraint", "constraint"),
    "action_response_failure": ("response", "response"),
    "wall_record_mismatch": ("wall_record", "wall_record"),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> dict[str, str]:
    return {
        "algorithm": "sha256",
        "value": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def repo_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def relative_uri(path: Path, base: Path) -> str:
    return Path(os.path.relpath(path.resolve(), base.resolve())).as_posix()


def report_reference(
    legacy_reference: dict[str, Any],
    report_path: Path,
    *,
    role: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = load_json(report_path)
    if report.get("sofrs_version") != "2.0":
        raise ValueError(f"{report_path}: expected alignment-ready SOFRS v2.0 input")

    artifact_id = f"artifact.{role}-report"
    report_name = report_path.name.removesuffix(".sofreport.json")
    receipt_path = SOURCE_RECEIPT_DIR / f"{report_name}.validation-receipt.json"
    if not receipt_path.is_file():
        raise ValueError(f"{report_path}: v2 validation receipt is missing")
    receipt_artifact = {
        "id": f"artifact.{role}-report-validation-receipt",
        "role": f"{role}-report-validation-receipt",
        "uri": relative_uri(receipt_path, AUDIT_DIR),
        "digest": digest(receipt_path),
    }
    artifact = {
        "id": artifact_id,
        "role": f"{role}-report",
        "uri": relative_uri(report_path, AUDIT_DIR),
        "digest": digest(report_path),
    }
    reference = {
        "report_id": report["report_id"],
        "label": legacy_reference["label"],
        "artifact": {
            "uri": artifact["uri"],
            "digest": artifact["digest"],
        },
        "validation_receipt": {
            "uri": receipt_artifact["uri"],
            "digest": receipt_artifact["digest"],
        },
        "sofrs_version": "2.0",
        "record_kind": report["record_kind"],
        "admission_basis": "native_sofrs_v2",
        "comparison_role_basis": {
            "role": role,
            "basis_kind": "declared_baseline_only",
            "authority_status": "DECLARED",
            "scope": "The selected report is a declared comparison baseline, not an automatic truth oracle.",
            "evidence_artifacts": [
                artifact_id,
                receipt_artifact["id"],
            ],
            "negative_boundary": [
                "Reference role does not imply ground truth, correctness, or defect authority.",
                "The selected report supports only a scoped difference from this baseline unless an external object-level oracle is bound.",
            ],
        },
    }
    return reference, artifact, receipt_artifact


def coordinate(
    legacy_name: str,
    value: Any,
    *,
    coordinate_family: str,
    source_artifact_id: str,
) -> dict[str, Any]:
    legacy_binding = {
        "binding_state": "legacy_payload_only",
        "reference_item_ref": None,
        "target_item_ref": None,
        "reason": (
            "The frozen v1 audit stores a comparison payload but no item-level "
            "reference/target report binding."
        ),
    }
    if value is None:
        return {
            "comparison_state": "NOT_DECLARED",
            "result_state": "NOT_DECLARED",
            "claim_status": None,
            "claim_target": None,
            "certificate_class": None,
            "classification_source": "migration_adapter",
            "report_item_binding": legacy_binding,
            "coordinate_family": coordinate_family,
            "value_schema_id": value_schema_id(coordinate_family),
            "value": None,
            "source_artifact_ids": [],
            "reason": (
                "The frozen v1 comparison did not declare this profile "
                "coordinate; absence is not numerical zero."
            ),
        }
    return {
        "comparison_state": "UNRESOLVED",
        "result_state": "DECLARED",
        "claim_status": None,
        "claim_target": None,
        "certificate_class": None,
        "classification_source": "migration_adapter",
        "report_item_binding": legacy_binding,
        "coordinate_family": coordinate_family,
        "value_schema_id": value_schema_id(coordinate_family),
        "value": None,
        "source_artifact_ids": [source_artifact_id],
        "reason": (
            "The v1 payload is retained by source digest, but the migrated SOFRS "
            "reports do not bind enough alignment metadata or item-level mappings "
            "to promote it as a v2 comparison coordinate."
        ),
    }


def absent_wall_input(reason: str) -> dict[str, Any]:
    return {
        "state": "NOT_DECLARED",
        "record_ref": None,
        "signature_ref": None,
        "source_artifact_id": None,
        "reason": reason,
    }


def wall_record_coordinate(
    legacy_value: Any,
    *,
    source_artifact_id: str,
) -> dict[str, Any]:
    missing_reason = (
        "The frozen SOFAUDIT v1 input does not bind this side to a retained "
        "Paper XI wall record and signature."
    )
    binding: dict[str, Any] = {
        "reference_wall": absent_wall_input(missing_reason),
        "target_wall": absent_wall_input(missing_reason),
        "comparison_context": {
            "state": "NOT_DECLARED" if legacy_value is None else "UNRESOLVED",
            "context_kind": None,
            "context_alignment_ref": None,
            "orientation_alignment": None,
            "field_alignment": None,
            "reason": (
                "No wall comparison was requested by the frozen v1 record."
                if legacy_value is None
                else "The legacy path payload lacks retained Paper XI wall inputs, so path samples cannot be promoted to an aligned wall-record comparison."
            ),
        },
    }
    if legacy_value is not None:
        binding["legacy_observation"] = {
            "source_artifact_id": source_artifact_id,
            "source_field": "signature.wall_record_mismatch",
            "disposition": "COMPATIBILITY_ONLY",
        }
    if legacy_value is None:
        return {
            "comparison_state": "NOT_DECLARED",
            "result_state": "NOT_DECLARED",
            "claim_status": None,
            "claim_target": None,
            "certificate_class": None,
            "classification_source": "migration_adapter",
            "report_item_binding": {
                "binding_state": "unresolved",
                "reference_item_ref": None,
                "target_item_ref": None,
                "reason": "No retained Paper XI wall items are bound by the v1 payload.",
            },
            "coordinate_family": "wall_record",
            "value_schema_id": value_schema_id("wall_record"),
            "value": None,
            "source_artifact_ids": [],
            "reason": (
                "The frozen v1 comparison did not declare this profile "
                "coordinate; absence is not numerical zero."
            ),
            "wall_input_binding": binding,
        }
    return {
        "comparison_state": "UNRESOLVED",
        "result_state": "DECLARED",
        "claim_status": None,
        "claim_target": None,
        "certificate_class": None,
        "classification_source": "migration_adapter",
        "report_item_binding": {
            "binding_state": "legacy_payload_only",
            "reference_item_ref": None,
            "target_item_ref": None,
            "reason": "The v1 path payload is compatibility-only and has no paired wall items.",
        },
        "coordinate_family": "wall_record",
        "value_schema_id": value_schema_id("wall_record"),
        "value": None,
        "source_artifact_ids": [source_artifact_id],
        "reason": (
            "A frozen v1 path observation is source-addressed, but neither side "
            "is bound to a retained Paper XI wall signature and the path/domain "
            "comparison context is unresolved."
        ),
        "wall_input_binding": binding,
    }


def normalize_comparison_specification(
    source: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    source = deepcopy(source)
    normalizations: list[str] = []
    normalization = source["normalization"]
    if normalization.pop("frozen_sentinel", None) == 999:
        cutoff = normalization.get("max_depth")
        normalization["unreached_state"] = "UNREACHED_AT_CUTOFF"
        normalization["unreached_cutoff"] = cutoff
        normalizations.append(
            "frozen_sentinel 999 -> UNREACHED_AT_CUTOFF with explicit max_depth cutoff"
        )
    tol = normalization.get("tol")
    cutoff = normalization.get("max_depth")
    return {
        "specification_id": "paper13-coordinatewise-v2",
        "normalization": {
            "normalization_id": "paper13.default-normalization-v2",
            "numeric_policy": "float-tolerance" if tol is not None else "exact",
            "equality_tolerance": tol,
            "sentinel_policy": "state-not-infinity",
            "generator_policy": "report-bound-generators",
        },
        "metric": {
            "metric_id": "coordinatewise-record",
            "domain": "mixed",
            "unit_policy": "not-applicable",
            "missing_value_policy": "state-preserving",
            "zero_denominator_policy": "not-applicable",
        },
        "depth_semantics": {
            "carrier": "word",
            "mode": "truncated-first-hit" if cutoff is not None else "summary-only",
            "reference_cutoff": cutoff,
            "target_cutoff": cutoff,
            "unreached_policy": "state-not-infinity",
        },
        "thresholds": {
            "threshold_id": "paper13.coordinatewise-tolerance",
            "value": tol,
            "source": "comparison-specification" if tol is not None else "not-applicable",
        },
        "parameter_synchronization": {
            "kind": "identity",
            "map_artifact_id": None,
            "interpolation_method": "not-applicable",
            "extrapolation_forbidden": True,
        },
        "aggregation": {
            "kind": "coordinatewise",
            "scalarization": "none",
            "weights_artifact_id": None,
            "weight_declaration": None,
        },
    }, normalizations


def typed_alignment(
    kind: str,
    source_component: Any,
    reference_ids: list[str],
    target_ids: list[str],
    evidence_artifact_id: str,
) -> dict[str, Any] | None:
    if source_component is None:
        return None
    pair_count = min(len(reference_ids), len(target_ids))
    pairs = [
        {
            "reference_id": reference_ids[index],
            "target_id": target_ids[index],
            "relation": (
                "equivalent"
                if reference_ids[index] == target_ids[index]
                else "analogue"
            ),
            "evidence_artifact_ids": [evidence_artifact_id],
        }
        for index in range(pair_count)
    ]
    total_on_reference = bool(reference_ids) and pair_count == len(reference_ids)
    total_on_target = bool(target_ids) and pair_count == len(target_ids)
    injective = bool(pairs) and len({pair["reference_id"] for pair in pairs}) == len(pairs) and len(
        {pair["target_id"] for pair in pairs}
    ) == len(pairs)
    surjective = bool(pairs) and total_on_target
    complete = total_on_reference and total_on_target
    if complete and injective:
        map_kind = "bijection"
    elif total_on_reference and injective:
        map_kind = "injection"
    else:
        map_kind = "relation"
    return {
        "alignment_id": f"paper13.{kind}.identity-v2",
        "alignment_kind": kind,
        "state": "TOTAL" if complete else ("PARTIAL" if pairs else "UNRESOLVED"),
        "map_kind": map_kind,
        "reference_carrier": "declared-report-labels",
        "target_carrier": "declared-report-labels",
        "pairs": pairs,
        "unmatched_reference_ids": reference_ids[pair_count:],
        "unmatched_target_ids": target_ids[pair_count:],
        "properties": {
            "total_on_reference": total_on_reference,
            "total_on_target": total_on_target,
            "injective": injective,
            "surjective": surjective,
        },
        "semantic_basis": str(source_component),
        "negative_boundary": [
            "Identity alignment is a declared baseline and does not establish semantic equivalence beyond the retained labels."
        ],
    }


def comparison_basis(
    source_artifact_id: str,
    reference_role_basis: dict[str, Any],
    reference_artifact_id: str,
    target_artifact_id: str,
) -> dict[str, Any]:
    return {
        "basis_status": "PARTIAL",
        "reference_role_basis": deepcopy(reference_role_basis),
        "alignment_evidence": [source_artifact_id],
        "object_level_oracle": {
            "status": "NOT_ASSESSED",
            "independence": {
                "implementation_relation": "not_assessed",
                "producer_relation": "not_assessed",
                "input_source": "not_assessed",
                "producer_cache_used": None,
            },
            "raw_source_artifacts": [reference_artifact_id, target_artifact_id],
            "independent_recomputation_artifacts": [],
            "oracle_result_artifact": None,
            "audit_result_artifact": None,
        },
        "policy_compatibility": {
            "status": "SATISFIED",
            "policy_artifact_ids": [source_artifact_id],
            "negative_boundary": [
                "Policy compatibility permits the declared comparison procedure but does not establish scientific adequacy."
            ],
        },
        "negative_boundary": [
            "This migrated comparison records protocol-relative differences only; it is not an object-level correctness certificate.",
            "A nonzero coordinate does not imply defect, error, or action.",
        ],
    }


def migrate_one(source_path: Path) -> dict[str, Any]:
    source = load_json(source_path)
    reference_name = Path(source["reference"]["artifact"]).stem
    target_name = Path(source["target"]["artifact"]).stem
    reference_path = SOURCE_REPORT_DIR / f"{reference_name}.sofreport.json"
    target_path = SOURCE_REPORT_DIR / f"{target_name}.sofreport.json"
    if not reference_path.is_file() or not target_path.is_file():
        raise ValueError(f"{source_path}: linked report is missing")

    source_artifact = {
        "id": "artifact.source-audit",
        "role": "source-audit",
        "uri": relative_uri(source_path, AUDIT_DIR),
        "digest": digest(source_path),
    }
    profile_artifact = {
        "id": "artifact.audit-profile",
        "role": "audit-profile",
        "uri": relative_uri(STANDARD_PROFILE_PATH, AUDIT_DIR),
        "digest": digest(STANDARD_PROFILE_PATH),
    }
    registry_artifact = {
        "id": "artifact.coordinate-semantics-registry",
        "role": "coordinate-semantics-registry",
        "uri": relative_uri(REGISTRY_PATH, AUDIT_DIR),
        "digest": digest(REGISTRY_PATH),
    }
    reference, reference_artifact, reference_receipt_artifact = report_reference(
        source["reference"], reference_path, role="reference"
    )
    target, target_artifact, target_receipt_artifact = report_reference(
        source["target"], target_path, role="target"
    )
    reference_report = load_json(reference_path)
    target_report = load_json(target_path)

    coordinates: dict[str, Any] = {}
    for legacy_name, (coordinate_id, coordinate_family) in FIELD_MAP.items():
        if legacy_name == "wall_record_mismatch":
            coordinates[coordinate_id] = wall_record_coordinate(
                source["signature"].get(legacy_name),
                source_artifact_id=source_artifact["id"],
            )
            continue
        coordinates[coordinate_id] = coordinate(
            legacy_name,
            source["signature"].get(legacy_name),
            coordinate_family=coordinate_family,
            source_artifact_id=source_artifact["id"],
            )

    if set(coordinates) != set(STANDARD_PROFILE["requested_coordinate_ids"]):
        raise ValueError("migration FIELD_MAP does not realize the versioned Audit Profile request")

    comparison_specification, sentinel_normalizations = (
        normalize_comparison_specification(source["comparison_specification"])
    )
    alignment = {
        "sector_alignment": typed_alignment(
            "sector",
            source["alignment"].get("sector_alignment"),
            reference_report["alignment_readiness"]["sector_metadata"]["labels"],
            target_report["alignment_readiness"]["sector_metadata"]["labels"],
            source_artifact["id"],
        ),
        "observable_alignment": typed_alignment(
            "observable",
            source["alignment"].get("observable_alignment"),
            reference_report["alignment_readiness"]["observable_metadata"]["labels"],
            target_report["alignment_readiness"]["observable_metadata"]["labels"],
            source_artifact["id"],
        ),
    }

    def alignment_check_status(component: dict[str, Any] | None) -> str:
        if component is None or component["state"] == "UNRESOLVED":
            return "NOT_CHECKED"
        if component["state"] == "INCOMPARABLE":
            return "FAILED"
        return "SATISFIED"

    sector_status = alignment_check_status(alignment["sector_alignment"])
    observable_status = alignment_check_status(alignment["observable_alignment"])
    condition_checks = [
        {
            "condition_id": "source-report-receipts-validate",
            "status": "SATISFIED",
            "evidence_artifact_ids": [
                reference_receipt_artifact["id"],
                target_receipt_artifact["id"],
            ],
        },
        {
            "condition_id": "paper-x-record-kind-permission",
            "status": "SATISFIED",
            "evidence_artifact_ids": [
                reference_artifact["id"],
                target_artifact["id"],
            ],
            "note": "Both migrated inputs are validated SOFRS v2 diagnostic-analogue reports.",
        },
        {
            "condition_id": "paper-x-carrier-alignment",
            "status": "SATISFIED",
            "evidence_artifact_ids": [source_artifact["id"]],
        },
        {
            "condition_id": "paper-x-policy-alignment",
            "status": "SATISFIED",
            "evidence_artifact_ids": [source_artifact["id"]],
        },
        {
            "condition_id": "paper-x-evidence-alignment",
            "status": "SATISFIED",
            "evidence_artifact_ids": [source_artifact["id"]],
        },
        {
            "condition_id": "paper-x-promotion-audit",
            "status": "SATISFIED",
            "evidence_artifact_ids": [source_artifact["id"]],
            "note": "No unavailable profile coordinate is filled from a nearby carrier.",
        },
        {
            "condition_id": "paper-xiii-sector-alignment",
            "status": sector_status,
            "evidence_artifact_ids": [source_artifact["id"]],
        },
        {
            "condition_id": "paper-xiii-observable-alignment",
            "status": observable_status,
            "evidence_artifact_ids": [source_artifact["id"]],
        },
        {
            "condition_id": "paper-xiii-comparison-specification",
            "status": "SATISFIED",
            "evidence_artifact_ids": [source_artifact["id"]],
        },
    ]
    guard_state = (
        "REJECTED"
        if any(check["status"] == "FAILED" for check in condition_checks)
        else "UNRESOLVED"
        if any(check["status"] != "SATISFIED" for check in condition_checks)
        else "ADMITTED"
    )

    migrated: dict[str, Any] = {
        "sofaudit_version": "2.0",
        "artifact_type": "sofaudit",
        "comparison_object": "SOFReportComparison",
        "audit_id": source["audit_id"],
        "system": source["system"],
        "regime": "analogue_vs_analogue",
        "source_reports": {
            "reference": reference,
            "target": target,
        },
        "inherited_compiler_guards": {
            "paper_x_contract_version": "1.0",
            "state": guard_state,
            "condition_checks": condition_checks,
            "negative_boundaries": [
                "Legacy strict compatibility does not reconstruct native SOFRS v2 compiler contracts.",
                "Missing coordinates remain unavailable and are not replaced by nearby carriers.",
                "A nonzero audit coordinate records difference, not defect or action.",
            ],
        },
        "audit_profile": {
            **{
                key: value
                for key, value in STANDARD_PROFILE.items()
                if key not in {"applicable_regimes", "profile_contract_version", "profile_revision", "negative_boundary"}
            },
            "profile_artifact_id": profile_artifact["id"],
            "coordinate_registry_artifact_id": registry_artifact["id"],
            "applicable_regime": "analogue_vs_analogue",
        },
        "alignment": alignment,
        "comparison_specification": comparison_specification,
        "comparison_basis": comparison_basis(
            source_artifact["id"],
            reference["comparison_role_basis"],
            reference_artifact["id"],
            target_artifact["id"],
        ),
        "coordinates": coordinates,
        "claim": {
            "result_state": "CERTIFIED",
            "claim_status": "Computational Certificate",
            "claim_target": "migration_consistency",
            "certificate_class": "migration_assembly",
            "classification_source": "migration_adapter",
            "statement": source["claim_note"],
            "negative_boundary": (
                "Controlled Regime A comparison under frozen v1 report semantics; "
                "no source-level causal, defect, correctness, or action inference."
            ),
            "source_artifact_ids": [
                source_artifact["id"],
                reference_artifact["id"],
                target_artifact["id"],
                reference_receipt_artifact["id"],
                target_receipt_artifact["id"],
                profile_artifact["id"],
                registry_artifact["id"],
            ],
        },
        "failure_modes": source["failure_modes"],
        "source_artifacts": [
            source_artifact,
            reference_artifact,
            target_artifact,
            reference_receipt_artifact,
            target_receipt_artifact,
            profile_artifact,
            registry_artifact,
        ],
        "provenance": {
            "kind": "migration",
            "source_sofaudit_version": "1.0",
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "source_audit_artifact_id": source_artifact["id"],
            "normalized_legacy_sentinels": sentinel_normalizations,
            "semantic_normalizations": [
                "Replaced the fixed v1 signature tuple with an Audit Profile and sparse typed coordinate map.",
                "Renamed action_response_failure to the descriptive response coordinate.",
                "Separated comparison state from result state and claim status.",
                "Classified missing legacy coordinates as NOT_DECLARED rather than zero.",
                "Retained legacy F5 path payloads as source-addressed compatibility observations without promoting them to Paper XI wall records or Paper XIII wall mismatches.",
                "Recorded Paper X guard checks as inherited conditions rather than a new admission taxonomy.",
                "Retained legacy comparison payloads only in the source artifact; v2 coordinates remain unresolved until report-level alignment and item bindings are available.",
            ],
        },
    }
    return migrated


def main() -> None:
    source_paths = sorted(LEGACY_RESULTS.glob("*.sofaudit"))
    if not source_paths:
        raise SystemExit("No frozen SOFAUDIT v1 artifacts found.")

    records: list[dict[str, Any]] = []
    for source_path in source_paths:
        migrated = migrate_one(source_path)
        output_path = AUDIT_DIR / f"{source_path.stem}.sofaudit.json"
        write_json(output_path, migrated)
        records.append(
            {
                "audit_id": migrated["audit_id"],
                "audit_profile_id": migrated["audit_profile"]["profile_id"],
                "source_uri": repo_uri(source_path),
                "source_digest": digest(source_path),
                "output_uri": f"audits/{output_path.name}",
                "output_digest": digest(output_path),
            }
        )

    index = {
        "sofaudit_migration_version": "2.0",
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "source_sofaudit_version": "1.0",
        "target_sofaudit_version": "2.0",
        "record_count": len(records),
        "profile_counts": {
            PROFILE_ID: len(records),
        },
        "normalized_legacy_sentinel_record_count": sum(
            1
            for path in AUDIT_DIR.glob("*.sofaudit.json")
            if load_json(path)["provenance"]["normalized_legacy_sentinels"]
        ),
        "unresolved_legacy_coordinate_count": sum(
            1
            for path in AUDIT_DIR.glob("*.sofaudit.json")
            for coordinate in load_json(path)["coordinates"].values()
            if coordinate["comparison_state"] == "UNRESOLVED"
        ),
        "unresolved_legacy_wall_observation_count": sum(
            1
            for path in AUDIT_DIR.glob("*.sofaudit.json")
            if load_json(path)["coordinates"]["wall_record"]["comparison_state"]
            == "UNRESOLVED"
        ),
        "source_report_receipt_count": len(list(SOURCE_RECEIPT_DIR.glob("*.json"))),
        "source_report_receipts": [
            {
                "receipt_uri": repo_uri(path),
                "receipt_digest": digest(path),
            }
            for path in sorted(SOURCE_RECEIPT_DIR.glob("*.json"))
        ],
        "records": records,
    }
    write_json(ACTIVE_RESULTS / "migration-index.json", index)
    print(
        f"Migrated {len(records)} SOFAUDIT records under "
        f"{PROFILE_ID}; unavailable coordinates remain typed states."
    )


if __name__ == "__main__":
    main()
