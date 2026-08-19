"""Validate SOFAUDIT v2.0 records, provenance, guards, and sparse coordinates."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.contract_api import (  # noqa: E402
    artifact_reference_errors,
    file_digest,
    load_json,
    resolve_artifact_path,
    result_claim_status_error,
    schema_errors,
)
from schemas.sofrs.api import v2_report_validation_receipt_errors  # noqa: E402
from experiments.paper12.validation.validate_sofrs_v2 import (  # noqa: E402
    standalone_report_errors,
)
from experiments.paper13.validation.audit_profiles import (  # noqa: E402
    GRIDWORLD_PROFILE,
    REGISTRY,
    STANDARD_PROFILE,
    STANDARD_PROFILE_ID,
    profile_errors,
)

# Backward-compatible public alias; the versioned profile remains normative.
STANDARD_COORDINATES = set(STANDARD_PROFILE["requested_coordinate_ids"])


DEFAULT_SCHEMA = ROOT / "schemas" / "sofaudit" / "v2.0.schema.json"
DEFAULT_DIR = PAPER_DIR / "results" / "audits"
NATIVE_DIR = PAPER_DIR / "results" / "native"
DEFAULT_INDEX = PAPER_DIR / "results" / "migration-index.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "sofaudit" / "validation-receipt-v2.0.schema.json"
MATCH_STATES = {"ALIGNED", "MISMATCH"}
CLAIM_COMPATIBILITY = {
    ("comparison_relation", None): {"comparison_specification", "audit_engine", "alignment_validator"},
    ("comparison_relation", "comparison_audit"): {"audit_engine", "alignment_validator"},
    ("external_mathematical_object", "object"): {"independent_oracle", "independent_validator"},
    ("empirical_domain_system", "object"): {"independent_validator", "external_evaluator"},
    ("representation_interface", None): {"comparison_specification", "migration_adapter"},
    ("representation_interface", "protocol_conformance"): {
        "comparison_specification",
        "independent_validator",
    },
    ("protocol_conformance", "protocol_conformance"): {"comparison_specification", "independent_validator"},
    ("migration_consistency", "migration_assembly"): {"migration_adapter", "independent_validator"},
}
UNAVAILABLE_STATE_PAIRS = {
    "NOT_DECLARED": "NOT_DECLARED",
    "NOT_APPLICABLE": "NOT_APPLICABLE",
    "INCOMPARABLE": "DECLARED",
    "UNRESOLVED": "DECLARED",
}
REQUIRED_RECEIPT_CHECKS = {
    "alignment-property-recomputation",
    "artifact-digest-closure",
    "claim-certificate-compatibility",
    "comparison-basis-recomputation",
    "guard-coordinate-coupling",
    "role-regime-profile-closure",
    "schema-validation",
    "source-report-receipt-validation",
}


def sha256(path: Path) -> str:
    return file_digest(path, "sha256")


def repo_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "digest": {"algorithm": "sha256", "value": sha256(path)},
    }


def closure_digest(ordered_artifacts: list[dict[str, Any]]) -> dict[str, str]:
    encoded = json.dumps(
        ordered_artifacts,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {"algorithm": "sha256", "value": hashlib.sha256(encoded).hexdigest()}


def contains_integer_sentinel(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 999
    if isinstance(value, list):
        return any(contains_integer_sentinel(item) for item in value)
    if isinstance(value, dict):
        return any(contains_integer_sentinel(item) for item in value.values())
    return False


def epistemic_classification_error(item: dict[str, Any], *, label: str) -> str | None:
    status = item["claim_status"]
    target = item["claim_target"]
    certificate_class = item["certificate_class"]
    if status is None:
        if target is not None or certificate_class is not None:
            return f"{label} has epistemic classification without a claim"
        return None
    if status == "Computational Certificate":
        if certificate_class is None:
            return f"{label} certificate lacks certificate_class"
    elif certificate_class is not None:
        return f"{label} non-certificate claim has certificate_class"
    if certificate_class == "object" and target not in {
        "external_mathematical_object",
        "empirical_domain_system",
    }:
        return f"{label} Object Certificate has a non-object target"
    if certificate_class == "protocol_conformance" and target not in {
        "representation_interface",
        "protocol_conformance",
    }:
        return f"{label} Protocol Certificate has the wrong target"
    if certificate_class == "migration_assembly" and target != "migration_consistency":
        return f"{label} Migration Certificate has the wrong target"
    if certificate_class == "comparison_audit" and target != "comparison_relation":
        return f"{label} Comparison Audit Certificate has the wrong target"
    if target == "comparison_relation" and certificate_class == "object":
        return f"{label} comparison_relation cannot be an Object Certificate"
    allowed_sources = CLAIM_COMPATIBILITY.get((target, certificate_class))
    if allowed_sources is None:
        return (
            f"{label} claim target {target} and certificate class "
            f"{certificate_class} are not a permitted combination"
        )
    if item["classification_source"] not in allowed_sources:
        return (
            f"{label} classification_source {item['classification_source']} is incompatible "
            f"with claim target {target} and certificate class {certificate_class}"
        )
    return None


def resolve_artifact(base: Path, artifact: dict[str, Any]) -> tuple[Path, list[str]]:
    try:
        path = resolve_artifact_path(
            artifact["uri"],
            repository_root=ROOT,
            base_directory=base,
        )
    except (KeyError, TypeError, ValueError):
        path = (base / str(artifact.get("uri", ""))).resolve()
    errors = artifact_reference_errors(
        artifact,
        label=f"artifact {artifact.get('uri', '<missing-uri>')}",
        repository_root=ROOT,
        base_directory=base,
        allowed_algorithms=("sha256",),
    )
    return path, errors


def expected_regime(reference_kind: str, target_kind: str) -> str:
    if reference_kind == "strict_sof" and target_kind == "strict_sof":
        return "strict_vs_strict"
    if reference_kind == "diagnostic_analogue" and target_kind == "diagnostic_analogue":
        return "analogue_vs_analogue"
    return "strict_vs_analogue"


def alignment_universe(report: dict[str, Any], kind: str) -> list[str]:
    metadata_key = "sector_metadata" if kind == "sector" else "observable_metadata"
    metadata = report.get("alignment_readiness", {}).get(metadata_key, {})
    labels = metadata.get("labels", [])
    return labels if isinstance(labels, list) else []


def report_item_index(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for collection in ("claims", "degradation_items", "findings"):
        for item in report.get(collection, []):
            item_id = item.get("report_item_id") or item.get("finding_id")
            if isinstance(item_id, str):
                index[item_id] = item
    return index


def alignment_errors(
    name: str,
    component: dict[str, Any] | None,
    reference_ids: list[str],
    target_ids: list[str],
    artifact_ids: set[str],
) -> tuple[list[str], bool]:
    if component is None:
        return [], False

    errors: list[str] = []
    pairs = component["pairs"]
    reference_universe = set(reference_ids)
    target_universe = set(target_ids)
    pair_refs = [pair["reference_id"] for pair in pairs]
    pair_targets = [pair["target_id"] for pair in pairs]
    mapped_refs = set(pair_refs)
    mapped_targets = set(pair_targets)

    unknown_refs = mapped_refs - reference_universe
    unknown_targets = mapped_targets - target_universe
    if unknown_refs:
        errors.append(f"{name} references unknown reference ids: {sorted(unknown_refs)}")
    if unknown_targets:
        errors.append(f"{name} references unknown target ids: {sorted(unknown_targets)}")

    duplicate_pairs = [
        pair for pair, count in Counter(zip(pair_refs, pair_targets)).items() if count > 1
    ]
    if duplicate_pairs:
        errors.append(f"{name} contains duplicate pairs: {duplicate_pairs}")

    expected_unmatched_reference = reference_universe - mapped_refs
    expected_unmatched_target = target_universe - mapped_targets
    if set(component["unmatched_reference_ids"]) != expected_unmatched_reference:
        errors.append(f"{name} unmatched_reference_ids do not match the report universe")
    if set(component["unmatched_target_ids"]) != expected_unmatched_target:
        errors.append(f"{name} unmatched_target_ids do not match the report universe")

    function_on_reference = len(pair_refs) == len(set(pair_refs))
    total_on_reference = bool(reference_universe) and mapped_refs == reference_universe
    total_on_target = bool(target_universe) and mapped_targets == target_universe
    injective = bool(pairs) and function_on_reference and len(pair_targets) == len(set(pair_targets))
    surjective = bool(pairs) and total_on_target
    recomputed = {
        "total_on_reference": total_on_reference,
        "total_on_target": total_on_target,
        "injective": injective,
        "surjective": surjective,
    }
    if component["properties"] != recomputed:
        errors.append(f"{name} properties differ from validator recomputation: {recomputed}")

    state = component["state"]
    if state == "TOTAL":
        if not (total_on_reference and total_on_target):
            errors.append(f"{name} TOTAL state lacks two-sided coverage")
        if expected_unmatched_reference or expected_unmatched_target:
            errors.append(f"{name} TOTAL state has unmatched identifiers")
    elif state == "PARTIAL":
        if not pairs or (total_on_reference and total_on_target):
            errors.append(f"{name} PARTIAL state is inconsistent with its pairs")
    elif pairs:
        errors.append(f"{name} {state} state cannot carry operative alignment pairs")

    map_kind = component["map_kind"]
    relations = {pair["relation"] for pair in pairs}
    if map_kind == "bijection" and not (
        total_on_reference and total_on_target and injective and surjective
    ):
        errors.append(f"{name} declared bijection is not a bijection")
    elif map_kind == "injection" and not (total_on_reference and injective):
        errors.append(f"{name} declared injection is not total and injective on reference")
    elif map_kind == "surjection" and not (
        total_on_reference and total_on_target and function_on_reference
    ):
        errors.append(f"{name} declared surjection is not a total surjective function")
    elif map_kind == "quotient":
        if relations - {"aggregation"}:
            errors.append(f"{name} quotient pairs must use reference-to-target aggregation")
        if not (total_on_reference and total_on_target and function_on_reference):
            errors.append(f"{name} quotient must cover both declared universes")
    elif map_kind == "refinement":
        if relations - {"refinement"}:
            errors.append(f"{name} refinement pairs must use reference-to-target refinement")
        if not (total_on_reference and total_on_target):
            errors.append(f"{name} refinement must cover both declared universes")
    if "aggregation" in relations and map_kind != "quotient":
        errors.append(f"{name} aggregation relation requires quotient map_kind")
    if "refinement" in relations and map_kind != "refinement":
        errors.append(f"{name} refinement relation requires refinement map_kind")

    for pair_index, pair in enumerate(pairs):
        unknown = set(pair["evidence_artifact_ids"]) - artifact_ids
        if unknown:
            errors.append(
                f"{name} pair {pair_index} references unknown artifacts: {sorted(unknown)}"
            )
    ready = state in {"TOTAL", "PARTIAL"} and not errors
    return errors, ready


def comparison_specification_errors(
    specification: dict[str, Any], artifact_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    normalization = specification["normalization"]
    tolerance = normalization["equality_tolerance"]
    if normalization["numeric_policy"] == "exact" and tolerance not in {None, 0}:
        errors.append("exact numeric policy requires null or zero equality tolerance")
    if normalization["numeric_policy"] == "float-tolerance" and (
        not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance <= 0
    ):
        errors.append("float-tolerance numeric policy requires a positive tolerance")

    depth = specification["depth_semantics"]
    if depth["mode"] == "truncated-first-hit" and (
        not isinstance(depth["reference_cutoff"], int)
        or depth["reference_cutoff"] <= 0
        or not isinstance(depth["target_cutoff"], int)
        or depth["target_cutoff"] <= 0
    ):
        errors.append("truncated-first-hit depth requires positive cutoffs")
    if depth["mode"] == "not-applicable" and (
        depth["carrier"] != "not-applicable"
        or depth["reference_cutoff"] is not None
        or depth["target_cutoff"] is not None
    ):
        errors.append("not-applicable depth must not declare a carrier or cutoff")

    threshold = specification["thresholds"]
    if (threshold["source"] == "not-applicable") != (threshold["value"] is None):
        errors.append("threshold value and not-applicable source are inconsistent")

    metric = specification["metric"]
    if metric["metric_id"] == "relative-difference":
        if metric["zero_denominator_policy"] == "not-applicable":
            errors.append("relative-difference requires a zero-denominator policy")
    elif metric["zero_denominator_policy"] != "not-applicable":
        errors.append("non-relative metric must use not-applicable zero-denominator policy")

    synchronization = specification["parameter_synchronization"]
    map_artifact_id = synchronization["map_artifact_id"]
    if synchronization["kind"] == "declared-map" and map_artifact_id is None:
        errors.append("declared-map synchronization requires a map artifact")
    if synchronization["kind"] == "not-applicable" and map_artifact_id is not None:
        errors.append("not-applicable synchronization cannot bind a map artifact")
    if map_artifact_id is not None and map_artifact_id not in artifact_ids:
        errors.append("parameter synchronization references an unknown map artifact")
    if synchronization["kind"] == "interpolation" and (
        synchronization["interpolation_method"] == "not-applicable"
        or not synchronization["extrapolation_forbidden"]
    ):
        errors.append("interpolation requires a method and forbids undeclared extrapolation")

    aggregation = specification["aggregation"]
    weights_id = aggregation["weights_artifact_id"]
    if aggregation["scalarization"] == "weighted-hamming" and (
        weights_id is None and not aggregation["weight_declaration"]
    ):
        errors.append("weighted-hamming requires weights evidence or a weight declaration")
    if weights_id is not None and weights_id not in artifact_ids:
        errors.append("aggregation references an unknown weights artifact")
    return errors


def semantic_errors(payload: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    provenance = payload["provenance"]
    artifacts = payload["source_artifacts"]
    artifact_ids = [artifact["id"] for artifact in artifacts]
    artifact_id_set = set(artifact_ids)
    if len(artifact_ids) != len(artifact_id_set):
        errors.append("source_artifacts ids must be unique")

    artifact_roles = [artifact["role"] for artifact in artifacts]
    if len(artifact_roles) != len(set(artifact_roles)):
        errors.append("source_artifacts roles must be unique")

    role_map = {artifact["role"]: artifact for artifact in artifacts}
    artifact_map = {artifact["id"]: artifact for artifact in artifacts}
    required_roles = {
        "reference-report",
        "target-report",
        "reference-report-validation-receipt",
        "target-report-validation-receipt",
        "audit-profile",
        "coordinate-semantics-registry",
    }
    if provenance["kind"] == "migration":
        required_roles.add("source-audit")
    for role in required_roles:
        if role not in role_map:
            errors.append(f"missing required source artifact role: {role}")

    resolved_artifacts: dict[str, Path] = {}
    for artifact in artifacts:
        resolved, artifact_errors = resolve_artifact(path.parent, artifact)
        errors.extend(artifact_errors)
        if resolved is not None and not artifact_errors:
            resolved_artifacts[artifact["id"]] = resolved

    linked_reports: dict[str, dict[str, Any]] = {}
    for side, role in (("reference", "reference-report"), ("target", "target-report")):
        report_ref = payload["source_reports"][side]
        if report_ref["comparison_role_basis"]["role"] != side:
            errors.append(f"{side} comparison role basis has the wrong role")
        report_path, ref_errors = resolve_artifact(path.parent, report_ref["artifact"])
        errors.extend(f"{side}: {error}" for error in ref_errors)
        if role in role_map and report_ref["artifact"] != {
            "uri": role_map[role]["uri"],
            "digest": role_map[role]["digest"],
        }:
            errors.append(f"{side} report reference does not match {role} artifact")
        receipt_role = f"{side}-report-validation-receipt"
        receipt_path, receipt_ref_errors = resolve_artifact(
            path.parent,
            report_ref["validation_receipt"],
        )
        errors.extend(f"{side} receipt: {error}" for error in receipt_ref_errors)
        if receipt_role in role_map and report_ref["validation_receipt"] != {
            "uri": role_map[receipt_role]["uri"],
            "digest": role_map[receipt_role]["digest"],
        }:
            errors.append(
                f"{side} validation receipt does not match {receipt_role} artifact"
            )
        if receipt_path.is_file():
            receipt = load_json(receipt_path)
            receipt_errors = v2_report_validation_receipt_errors(
                receipt,
                repository_root=ROOT,
                expected_report_reference=report_ref,
                expected_report_base_directory=path.parent,
            )
            errors.extend(f"{side} receipt: {error}" for error in receipt_errors)
        if report_path.is_file():
            report = load_json(report_path)
            linked_reports[side] = report
            errors.extend(
                f"{side} SOFRS validation: {error}"
                for error in standalone_report_errors(report_path)
            )
            if report.get("report_id") != report_ref["report_id"]:
                errors.append(f"{side} report_id does not match linked artifact")
            if report.get("sofrs_version") != report_ref["sofrs_version"]:
                errors.append(f"{side} sofrs_version does not match linked artifact")
            if report.get("record_kind") != report_ref["record_kind"]:
                errors.append(f"{side} record_kind does not match linked SOFRS v2 report")
            if report.get("sofrs_version") != "2.0":
                errors.append(f"{side} SOFAUDIT v2 input must bind a SOFRS v2 report")
        basis_artifacts = set(report_ref["comparison_role_basis"]["evidence_artifacts"])
        if not basis_artifacts.issubset(artifact_id_set):
            errors.append(f"{side} comparison role basis references unknown artifacts")

    declared_regime = payload["regime"]
    recomputed_regime = expected_regime(
        payload["source_reports"]["reference"]["record_kind"],
        payload["source_reports"]["target"]["record_kind"],
    )
    if declared_regime != recomputed_regime:
        errors.append(
            f"regime {declared_regime} differs from record-kind recomputation {recomputed_regime}"
        )
    if payload["audit_profile"]["applicable_regime"] != recomputed_regime:
        errors.append("Audit Profile applicable_regime differs from record-kind recomputation")
    declared_profile = payload["audit_profile"]
    profile_artifact_id = declared_profile["profile_artifact_id"]
    registry_artifact_id = declared_profile["coordinate_registry_artifact_id"]
    profile_role_valid = (
        artifact_map.get(profile_artifact_id, {}).get("role") == "audit-profile"
    )
    registry_role_valid = (
        artifact_map.get(registry_artifact_id, {}).get("role")
        == "coordinate-semantics-registry"
    )
    if not profile_role_valid:
        errors.append("Audit Profile does not bind the audit-profile artifact role")
    if not registry_role_valid:
        errors.append("Audit Profile does not bind the coordinate-semantics-registry artifact role")

    profile_path = resolved_artifacts.get(profile_artifact_id) if profile_role_valid else None
    registry_path = resolved_artifacts.get(registry_artifact_id) if registry_role_valid else None
    profile_document = load_json(profile_path) if profile_path is not None else None
    profile = (
        profile_document.get("audit_profile", profile_document)
        if isinstance(profile_document, dict)
        else None
    )
    registry = load_json(registry_path) if registry_path is not None else None
    value_schema_by_family: dict[str, str] = {}
    if profile is not None and registry is not None:
        if registry.get("registry_id") != "sofaudit.coordinate-semantics.v1":
            errors.append("coordinate semantics registry has an unsupported identity")
        coordinates = registry.get("coordinates")
        if not isinstance(coordinates, dict):
            errors.append("coordinate semantics registry lacks a coordinate map")
        else:
            value_schema_by_family = {
                family: item.get("value_schema_id")
                for family, item in coordinates.items()
                if isinstance(item, dict) and isinstance(item.get("value_schema_id"), str)
            }
            errors.extend(
                f"Audit Profile: {error}" for error in profile_errors(profile, registry)
            )
        expected_profile = {
            key: value
            for key, value in profile.items()
            if key
            not in {
                "applicable_regimes",
                "profile_contract_version",
                "profile_revision",
                "negative_boundary",
            }
        }
        expected_profile.update(
            {
                "profile_artifact_id": profile_artifact_id,
                "coordinate_registry_artifact_id": registry_artifact_id,
                "applicable_regime": recomputed_regime,
            }
        )
        if declared_profile != expected_profile:
            errors.append("embedded Audit Profile differs from its source-addressed profile artifact")
        if declared_profile["profile_version"] != profile["profile_version"]:
            errors.append("Audit Profile version differs from the versioned profile input")
        if recomputed_regime not in profile["applicable_regimes"]:
            errors.append("Audit Profile is not applicable to the recomputed regime")
        missing_profile_roles = set(declared_profile["required_evidence_roles"]) - set(
            artifact_roles
        )
        if missing_profile_roles:
            errors.append(
                "Audit Profile required evidence roles are missing: "
                f"{sorted(missing_profile_roles)}"
            )

    guards = payload["inherited_compiler_guards"]
    alignment_ready: dict[str, bool] = {}
    for alignment_name, kind in (
        ("sector_alignment", "sector"),
        ("observable_alignment", "observable"),
    ):
        component = payload["alignment"][alignment_name]
        if component is not None and component["alignment_kind"] != kind:
            errors.append(f"{alignment_name} has the wrong alignment_kind")
        reference_ids = alignment_universe(linked_reports.get("reference", {}), kind)
        target_ids = alignment_universe(linked_reports.get("target", {}), kind)
        component_errors, ready = alignment_errors(
            alignment_name,
            component,
            reference_ids,
            target_ids,
            artifact_id_set,
        )
        errors.extend(component_errors)
        alignment_ready[alignment_name] = ready

    checks = guards["condition_checks"]
    check_ids = [check["condition_id"] for check in checks]
    if len(check_ids) != len(set(check_ids)):
        errors.append("inherited guard condition ids must be unique")
    required_guard_prefixes = {
        "source-report-receipts-validate",
        "paper-x-record-kind-permission",
        "paper-x-carrier-alignment",
        "paper-x-policy-alignment",
        "paper-x-evidence-alignment",
        "paper-x-promotion-audit",
        "paper-xiii-sector-alignment",
        "paper-xiii-observable-alignment",
        "paper-xiii-comparison-specification",
    }
    if not required_guard_prefixes.issubset(check_ids):
        errors.append("required compiler, alignment, or comparison-specification guard is absent")

    check_map = {check["condition_id"]: check for check in checks}
    for alignment_name, condition_id in (
        ("sector_alignment", "paper-xiii-sector-alignment"),
        ("observable_alignment", "paper-xiii-observable-alignment"),
    ):
        if condition_id in check_map:
            component = payload["alignment"][alignment_name]
            expected_status = (
                "SATISFIED"
                if alignment_ready[alignment_name]
                else "FAILED"
                if component is not None and component["state"] == "INCOMPARABLE"
                else "NOT_CHECKED"
            )
            if check_map[condition_id]["status"] != expected_status:
                errors.append(
                    f"{condition_id} status differs from alignment recomputation"
                )

    if any(check["status"] == "FAILED" for check in checks):
        recomputed_guard_state = "REJECTED"
    elif any(check["status"] != "SATISFIED" for check in checks):
        recomputed_guard_state = "UNRESOLVED"
    else:
        recomputed_guard_state = "ADMITTED"
    if guards["state"] != recomputed_guard_state:
        errors.append(
            f"guard state {guards['state']} differs from condition recomputation "
            f"{recomputed_guard_state}"
        )

    if guards["state"] == "ADMITTED":
        unresolved = [
            check["condition_id"]
            for check in checks
            if check["status"] != "SATISFIED"
        ]
        if unresolved:
            errors.append(f"ADMITTED comparison has unresolved guards: {unresolved}")
        if not all(alignment_ready.values()):
            errors.append("No Comparison Without Alignment: admitted audit lacks validated Phi")
    elif guards["state"] == "UNRESOLVED":
        if any(
            coordinate["comparison_state"] in MATCH_STATES
            for coordinate in payload["coordinates"].values()
        ):
            errors.append("UNRESOLVED compiler guards cannot emit aligned or mismatch coordinates")
        if payload["claim"]["claim_target"] not in {
            None,
            "migration_consistency",
            "protocol_conformance",
        }:
            errors.append("UNRESOLVED guards cannot support an affirmative comparison claim")
    elif guards["state"] == "REJECTED":
        if payload["claim"]["claim_status"] is not None:
            errors.append("REJECTED compiler guards cannot emit an affirmative audit claim")
        if any(
            coordinate["comparison_state"] in MATCH_STATES
            for coordinate in payload["coordinates"].values()
        ):
            errors.append("REJECTED compiler guards cannot emit aligned or mismatch coordinates")
    for check in checks:
        unknown = set(check["evidence_artifact_ids"]) - artifact_id_set
        if unknown:
            errors.append(
                f"condition {check['condition_id']} references unknown artifacts: "
                f"{sorted(unknown)}"
            )

    requested = set(payload["audit_profile"]["requested_coordinate_ids"])
    coordinate_ids = set(payload["coordinates"])
    if coordinate_ids != requested:
        errors.append("coordinates must realize exactly the Audit Profile request")
    if profile is not None and requested != set(profile["requested_coordinate_ids"]):
        errors.append("coordinates must realize the versioned Audit Profile request")

    sector_alignment = payload["alignment"]["sector_alignment"]
    observable_alignment = payload["alignment"]["observable_alignment"]
    for coordinate_id, coordinate in payload["coordinates"].items():
        comparison_state = coordinate["comparison_state"]
        result_state = coordinate["result_state"]
        item_binding = coordinate.get("report_item_binding")
        if not isinstance(item_binding, dict):
            errors.append(f"{coordinate_id} lacks a valid report_item_binding")
        elif item_binding["binding_state"] == "paired":
            if not item_binding["reference_item_ref"] or not item_binding["target_item_ref"]:
                errors.append(f"{coordinate_id} paired binding lacks report item refs")
            for side, item_ref in (
                ("reference", item_binding["reference_item_ref"]),
                ("target", item_binding["target_item_ref"]),
            ):
                expected_report_id = payload["source_reports"][side]["report_id"]
                if item_ref and item_ref["report_id"] != expected_report_id:
                    errors.append(f"{coordinate_id} {side} item binding targets the wrong report")
                if item_ref:
                    report_artifact = role_map.get(f"{side}-report")
                    if report_artifact and item_ref["artifact_digest"] != report_artifact["digest"]:
                        errors.append(
                            f"{coordinate_id} {side} item binding has the wrong report digest"
                        )
                    report_items = report_item_index(linked_reports.get(side, {}))
                    bound_item = report_items.get(item_ref["report_item_id"])
                    if bound_item is None:
                        errors.append(
                            f"{coordinate_id} {side} item binding references an unknown report item"
                        )
                    elif bound_item.get("source_output_item_id") != item_ref["source_output_item_id"]:
                        errors.append(
                            f"{coordinate_id} {side} source_output_item_id does not match the report item"
                        )
            if item_binding["reason"] is not None:
                errors.append(f"{coordinate_id} paired binding must not carry a reason")
        else:
            if item_binding["binding_state"] in {
                "incomparable",
                "unresolved",
                "legacy_payload_only",
            } and not item_binding["reason"]:
                errors.append(f"{coordinate_id} non-paired binding lacks a reason")
        if not all(alignment_ready.values()) and coordinate["comparison_state"] in MATCH_STATES:
            errors.append(
                f"{coordinate_id} cannot be ALIGNED/MISMATCH without validated sector and observable alignment"
            )
        expected_value_schema = value_schema_by_family.get(coordinate["coordinate_family"])
        if expected_value_schema is None:
            errors.append(f"{coordinate_id} uses an unregistered coordinate family")
            continue
        if coordinate.get("value_schema_id") != expected_value_schema:
            errors.append(
                f"{coordinate_id} value_schema_id does not match coordinate family; "
                f"expected {expected_value_schema}"
            )
        if coordinate["value"] is not None and not isinstance(coordinate["value"], dict):
            errors.append(f"{coordinate_id} comparison value must be a typed object")
        if isinstance(coordinate["value"], dict) and "relation" not in coordinate["value"]:
            errors.append(f"{coordinate_id} comparison value lacks relation")
        if isinstance(coordinate["value"], dict) and "relation" in coordinate["value"]:
            relation = coordinate["value"]["relation"]
            if coordinate["comparison_state"] == "ALIGNED" and relation not in {"equal", "increased", "decreased"}:
                errors.append(f"{coordinate_id} ALIGNED coordinate has incompatible value relation")
            if coordinate["comparison_state"] == "MISMATCH" and relation not in {"mismatch", "increased", "decreased"}:
                errors.append(f"{coordinate_id} MISMATCH coordinate has incompatible value relation")
            metric_result = coordinate["value"].get("metric_result")
            if metric_result is not None and (
                metric_result.get("metric_id")
                != payload["comparison_specification"]["metric"]["metric_id"]
            ):
                errors.append(f"{coordinate_id} metric_result uses a different metric")
            oracle_ref = coordinate["value"].get("oracle_ref")
            if oracle_ref is not None and oracle_ref not in artifact_id_set:
                errors.append(f"{coordinate_id} value references an unknown oracle artifact")
        if (
            coordinate["certificate_class"] == "object"
            and (
                not isinstance(item_binding, dict)
                or item_binding["binding_state"] != "paired"
            )
        ):
            errors.append(f"{coordinate_id} Object Certificate requires paired report items")
        if comparison_state in MATCH_STATES:
            if result_state not in {"ESTABLISHED", "CERTIFIED", "OBSERVED"}:
                errors.append(
                    f"{coordinate_id} matched result has invalid result_state"
                )
            if coordinate["claim_status"] is None:
                errors.append(f"{coordinate_id} matched result lacks claim_status")
            status_error = result_claim_status_error(
                result_state,
                coordinate["claim_status"],
                label=f"coordinate {coordinate_id}",
            )
            if status_error:
                errors.append(status_error)
            classification_error = epistemic_classification_error(
                coordinate,
                label=f"coordinate {coordinate_id}",
            )
            if classification_error:
                errors.append(classification_error)
            if coordinate["value"] is None:
                errors.append(f"{coordinate_id} matched result lacks a value")
        else:
            expected_result_state = UNAVAILABLE_STATE_PAIRS[comparison_state]
            if result_state != expected_result_state:
                errors.append(
                    f"{coordinate_id} {comparison_state} must use "
                    f"{expected_result_state}"
                )
            if coordinate["claim_status"] is not None:
                errors.append(f"{coordinate_id} unavailable result has claim_status")
            classification_error = epistemic_classification_error(
                coordinate,
                label=f"coordinate {coordinate_id}",
            )
            if classification_error:
                errors.append(classification_error)
            if coordinate["value"] is not None:
                errors.append(f"{coordinate_id} unavailable result must have null value")
            if not coordinate.get("reason"):
                errors.append(f"{coordinate_id} unavailable result lacks reason")
        unknown = set(coordinate["source_artifact_ids"]) - artifact_id_set
        if unknown:
            errors.append(
                f"{coordinate_id} references unknown artifacts: {sorted(unknown)}"
            )

        binding = coordinate.get("wall_input_binding")
        if coordinate_id != "wall_record":
            if binding is not None:
                errors.append(
                    f"{coordinate_id} must not carry a wall_input_binding"
                )
            continue
        if binding is None:
            errors.append("wall_record coordinate lacks wall_input_binding")
            continue

        retained_sides = 0
        for side in ("reference_wall", "target_wall"):
            wall_input = binding[side]
            if wall_input["state"] == "RETAINED":
                retained_sides += 1
                for field in ("record_ref", "signature_ref", "source_artifact_id"):
                    if not wall_input[field]:
                        errors.append(f"{side} RETAINED input lacks {field}")
                if wall_input["reason"] is not None:
                    errors.append(f"{side} RETAINED input must not carry a reason")
                artifact_id = wall_input["source_artifact_id"]
                if artifact_id and artifact_id not in artifact_id_set:
                    errors.append(
                        f"{side} references unknown wall artifact: {artifact_id}"
                    )
                elif artifact_id and artifact_map[artifact_id]["role"] != "paper-xi-wall-record":
                    errors.append(
                        f"{side} retained input must reference a paper-xi-wall-record artifact"
                    )
            else:
                if any(
                    wall_input[field] is not None
                    for field in ("record_ref", "signature_ref", "source_artifact_id")
                ):
                    errors.append(
                        f"{side} unavailable input must not carry retained references"
                    )
                if not wall_input["reason"]:
                    errors.append(f"{side} unavailable input lacks reason")

        context = binding["comparison_context"]
        context_fields = (
            "context_kind",
            "context_alignment_ref",
            "orientation_alignment",
            "field_alignment",
        )
        if context["state"] == "READY":
            for field in context_fields:
                if not context[field]:
                    errors.append(f"READY wall comparison context lacks {field}")
            if context["reason"] is not None:
                errors.append("READY wall comparison context must not carry a reason")
        else:
            if any(context[field] is not None for field in context_fields):
                errors.append(
                    "unavailable wall comparison context must not carry comparison semantics"
                )
            if not context["reason"]:
                errors.append("unavailable wall comparison context lacks reason")

        if comparison_state in MATCH_STATES:
            if retained_sides != 2 or context["state"] != "READY":
                errors.append(
                    "wall_record ALIGNED/MISMATCH requires two retained Paper XI "
                    "wall inputs and a ready comparison context"
                )
        legacy_observation = binding.get("legacy_observation")
        if legacy_observation is not None:
            legacy_artifact_id = legacy_observation["source_artifact_id"]
            if legacy_artifact_id not in artifact_id_set:
                errors.append(
                    "wall legacy_observation references an unknown source artifact"
                )
            if comparison_state in MATCH_STATES:
                errors.append(
                    "compatibility-only legacy wall observation cannot establish an "
                    "ALIGNED/MISMATCH wall coordinate"
                )

    kinds = {
        payload["source_reports"]["reference"]["record_kind"],
        payload["source_reports"]["target"]["record_kind"],
    }
    if "diagnostic_analogue" in kinds and payload["claim"]["claim_status"] == "Theorem":
        errors.append("analogue-involving comparisons cannot instantiate a Theorem claim")

    claim_status_error = result_claim_status_error(
        payload["claim"]["result_state"],
        payload["claim"]["claim_status"],
        label="audit claim",
    )
    if claim_status_error:
        errors.append(claim_status_error)
    classification_error = epistemic_classification_error(
        payload["claim"],
        label="audit claim",
    )
    if classification_error:
        errors.append(classification_error)
    if provenance["kind"] == "native" and (
        payload["claim"]["claim_target"] == "migration_consistency"
        or payload["claim"]["certificate_class"] == "migration_assembly"
    ):
        errors.append("native provenance cannot issue a migration-consistency claim")

    basis = payload["comparison_basis"]
    if basis["reference_role_basis"] != payload["source_reports"]["reference"]["comparison_role_basis"]:
        errors.append(
            "comparison_basis reference_role_basis differs from the source reference basis"
        )
    oracle = basis["object_level_oracle"]
    independence = oracle["independence"]
    object_claim = payload["claim"]["claim_target"] in {
        "external_mathematical_object",
        "empirical_domain_system",
    }
    oracle_role_complete = (
        all(
            artifact_map.get(identifier, {}).get("role", "").startswith("raw-source")
            for identifier in oracle["raw_source_artifacts"]
        )
        and all(
            artifact_map.get(identifier, {}).get("role", "").startswith(
                "independent-recomputation"
            )
            for identifier in oracle["independent_recomputation_artifacts"]
        )
        and artifact_map.get(oracle["oracle_result_artifact"], {}).get("role")
        == "object-oracle-result"
        and artifact_map.get(oracle["audit_result_artifact"], {}).get("role")
        == "audit-result"
    )
    independence_complete = (
        independence["implementation_relation"] != "not_assessed"
        and independence["producer_relation"] != "not_assessed"
        and independence["input_source"]
        in {"canonical_raw_sources", "frozen_source_artifacts"}
        and independence["producer_cache_used"] is False
    )
    oracle_complete = (
        oracle["status"] == "SATISFIED"
        and bool(oracle["raw_source_artifacts"])
        and bool(oracle["independent_recomputation_artifacts"])
        and oracle["oracle_result_artifact"] is not None
        and oracle["audit_result_artifact"] is not None
        and oracle_role_complete
        and independence_complete
    )
    basis_ids = artifact_id_set
    referenced_basis_ids = (
        basis["reference_role_basis"]["evidence_artifacts"]
        + basis["alignment_evidence"]
        + basis["policy_compatibility"]["policy_artifact_ids"]
    )
    for artifact_id in referenced_basis_ids:
        if artifact_id not in basis_ids:
            errors.append(f"comparison_basis references unknown artifact: {artifact_id}")
    for artifact_id in (
        oracle["raw_source_artifacts"]
        + oracle["independent_recomputation_artifacts"]
        + ([oracle["oracle_result_artifact"]] if oracle["oracle_result_artifact"] else [])
        + ([oracle["audit_result_artifact"]] if oracle["audit_result_artifact"] else [])
    ):
        if artifact_id not in basis_ids:
            errors.append(f"comparison oracle references unknown artifact: {artifact_id}")

    reference_basis = basis["reference_role_basis"]
    reference_sufficient = reference_basis["role"] == "reference"
    if object_claim:
        reference_sufficient = reference_sufficient and (
            reference_basis["basis_kind"] != "declared_baseline_only"
            and reference_basis["authority_status"] == "ESTABLISHED"
        )
    alignment_sufficient = (
        all(alignment_ready.values())
        and bool(basis["alignment_evidence"])
        and all(identifier in artifact_id_set for identifier in basis["alignment_evidence"])
    )
    policy_sufficient = (
        basis["policy_compatibility"]["status"] == "SATISFIED"
        and bool(basis["policy_compatibility"]["policy_artifact_ids"])
        and all(
            identifier in artifact_id_set
            for identifier in basis["policy_compatibility"]["policy_artifact_ids"]
        )
    )
    basis_complete = (
        reference_sufficient
        and alignment_sufficient
        and policy_sufficient
        and (oracle_complete if object_claim else True)
    )
    expected_basis_status = "COMPLETE" if basis_complete else "PARTIAL"
    if basis["basis_status"] != expected_basis_status:
        errors.append(
            f"comparison_basis status differs from validator recomputation: "
            f"{expected_basis_status}"
        )
    if object_claim:
        if payload["claim"]["certificate_class"] != "object":
            errors.append("external object claim must use the Object Certificate class")
        if not oracle_complete:
            errors.append("Object Certificate requires a satisfied independent comparison oracle")
        if payload["claim"]["classification_source"] not in {
            "independent_oracle",
            "independent_validator",
        }:
            errors.append("external object claim must be classified by an independent oracle")
    if payload["claim"]["certificate_class"] == "comparison_audit" and not basis_complete:
        errors.append("Comparison Audit Certificate requires a complete alignment-relative basis")
    if set(oracle["raw_source_artifacts"]) & set(oracle["independent_recomputation_artifacts"]):
        errors.append("independent oracle recomputation artifacts must differ from raw sources")
    if oracle["status"] == "SATISFIED" and not oracle_role_complete:
        errors.append("satisfied object oracle uses incompatible artifact roles")
    if oracle["status"] == "SATISFIED" and not independence_complete:
        errors.append("satisfied object oracle lacks the declared independence boundary")

    for coordinate_id, coordinate in payload["coordinates"].items():
        if coordinate["claim_target"] in {
            "external_mathematical_object",
            "empirical_domain_system",
        } and (coordinate["certificate_class"] != "object" or not oracle_complete):
            errors.append(
                f"{coordinate_id} external object claim lacks the satisfied independent oracle"
            )

    unknown_claim_artifacts = (
        set(payload["claim"]["source_artifact_ids"]) - artifact_id_set
    )
    if unknown_claim_artifacts:
        errors.append(
            f"claim references unknown artifacts: {sorted(unknown_claim_artifacts)}"
        )

    if provenance["kind"] == "migration":
        source_id = provenance["source_audit_artifact_id"]
        if source_id not in artifact_id_set:
            errors.append("migration source_audit_artifact_id is unresolved")
        elif role_map.get("source-audit", {}).get("id") != source_id:
            errors.append("migration source id does not identify source-audit artifact")
    else:
        unknown_generation_ids = (
            set(provenance["generation_artifact_ids"]) - artifact_id_set
        )
        if unknown_generation_ids:
            errors.append(
                f"native provenance references unknown generation artifacts: "
                f"{sorted(unknown_generation_ids)}"
            )

    if contains_integer_sentinel(payload):
        errors.append("SOFAUDIT v2 contains legacy integer sentinel 999")
    errors.extend(
        comparison_specification_errors(
            payload["comparison_specification"], artifact_id_set
        )
    )
    return errors


def build_validation_receipt(audit_path: Path) -> dict[str, Any]:
    payload = load_json(audit_path)
    errors = schema_errors(payload, load_json(DEFAULT_SCHEMA)) + semantic_errors(
        payload, audit_path
    )
    if errors:
        raise ValueError(f"{audit_path}: " + "; ".join(errors))
    source_closure = []
    for artifact in payload["source_artifacts"]:
        resolved, resolve_errors = resolve_artifact(audit_path.parent, artifact)
        if resolve_errors:
            raise ValueError(f"{audit_path}: " + "; ".join(resolve_errors))
        source_closure.append(
            {"role": artifact["role"], "artifact": repo_reference(resolved)}
        )
    ordered_artifacts = [
        {"role": "audit", "artifact": repo_reference(audit_path)},
        *source_closure,
    ]
    return {
        "receipt_version": "2.0",
        "artifact_type": "sofaudit_validation_receipt",
        "receipt_id": f"receipt.{payload['audit_id']}.sofaudit-v2",
        "audit": {
            "audit_id": payload["audit_id"],
            "sofaudit_version": "2.0",
            "artifact": ordered_artifacts[0]["artifact"],
        },
        "validator": {
            "validator_id": "sofaudit.semantic-validator.v2",
            "validator_version": "2.0",
            "implementation": repo_reference(Path(__file__)),
            "receipt_contract": repo_reference(RECEIPT_SCHEMA),
        },
        "artifact_closure": {
            "artifact_count": len(ordered_artifacts),
            "ordered_artifacts": ordered_artifacts,
            "closure_digest": closure_digest(ordered_artifacts),
        },
        "status": "PASS",
        "checks": [
            {"check_id": check_id, "status": "PASS"}
            for check_id in sorted(REQUIRED_RECEIPT_CHECKS)
        ],
        "negative_boundaries": [
            "This receipt certifies SOFAUDIT v2 protocol conformance and the bound artifact closure; it is not an Object Certificate and does not assign correctness or action."
        ],
    }


def validation_receipt_errors(receipt_path: Path) -> list[str]:
    receipt = load_json(receipt_path)
    errors = schema_errors(receipt, load_json(RECEIPT_SCHEMA))
    if errors:
        return errors
    checks = [item["check_id"] for item in receipt["checks"]]
    if len(checks) != len(set(checks)) or set(checks) != REQUIRED_RECEIPT_CHECKS:
        errors.append("SOFAUDIT receipt check set is not exact")
    closure = receipt["artifact_closure"]
    ordered = closure["ordered_artifacts"]
    if closure["artifact_count"] != len(ordered):
        errors.append("SOFAUDIT receipt artifact_count differs from its closure")
    if closure["closure_digest"] != closure_digest(ordered):
        errors.append("SOFAUDIT receipt closure digest mismatch")
    for index, item in enumerate(ordered):
        errors.extend(
            artifact_reference_errors(
                item["artifact"],
                label=f"SOFAUDIT receipt artifact[{index}]",
                repository_root=ROOT,
            )
        )
    for label, reference in (
        ("SOFAUDIT validator implementation", receipt["validator"]["implementation"]),
        ("SOFAUDIT receipt contract", receipt["validator"]["receipt_contract"]),
    ):
        errors.extend(
            artifact_reference_errors(
                reference, label=label, repository_root=ROOT
            )
        )
    if receipt["validator"]["implementation"] != repo_reference(Path(__file__)):
        errors.append("SOFAUDIT receipt binds a different validator implementation")
    if receipt["validator"]["receipt_contract"] != repo_reference(RECEIPT_SCHEMA):
        errors.append("SOFAUDIT receipt binds a different receipt contract")
    if ordered[0]["role"] != "audit":
        errors.append("SOFAUDIT receipt closure does not begin with the audit")
        return errors
    audit_ref = ordered[0]["artifact"]
    if receipt["audit"]["artifact"] != audit_ref:
        errors.append("SOFAUDIT receipt audit reference differs from its closure")
    try:
        audit_path = resolve_artifact_path(
            audit_ref["uri"], repository_root=ROOT
        )
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    audit = load_json(audit_path)
    if receipt["audit"]["audit_id"] != audit.get("audit_id"):
        errors.append("SOFAUDIT receipt audit_id differs from the bound audit")
    errors.extend(schema_errors(audit, load_json(DEFAULT_SCHEMA)))
    errors.extend(semantic_errors(audit, audit_path))
    expected_source_closure = []
    for artifact in audit["source_artifacts"]:
        resolved, resolve_errors = resolve_artifact(audit_path.parent, artifact)
        errors.extend(resolve_errors)
        expected_source_closure.append(
            {"role": artifact["role"], "artifact": repo_reference(resolved)}
        )
    if ordered[1:] != expected_source_closure:
        errors.append("SOFAUDIT receipt closure differs from audit source artifacts")
    return errors


def index_errors(index_path: Path, paths: list[Path]) -> list[str]:
    index = load_json(index_path)
    errors: list[str] = []
    if index.get("target_sofaudit_version") != "2.0":
        errors.append("migration index target version is not 2.0")
    if index.get("record_count") != len(paths):
        errors.append("migration index record_count does not match artifact count")
    if index.get("profile_counts") != {STANDARD_PROFILE_ID: len(paths)}:
        errors.append("migration index profile census is inconsistent")
    sentinel_records = sum(
        1
        for path in paths
        if load_json(path)["provenance"]["kind"] == "migration"
        and load_json(path)["provenance"]["normalized_legacy_sentinels"]
    )
    if index.get("normalized_legacy_sentinel_record_count") != sentinel_records:
        errors.append("migration index sentinel-normalization census is inconsistent")
    unresolved_coordinates = sum(
        1
        for path in paths
        for coordinate in load_json(path)["coordinates"].values()
        if coordinate["comparison_state"] == "UNRESOLVED"
    )
    if index.get("unresolved_legacy_coordinate_count") != unresolved_coordinates:
        errors.append("migration index unresolved-coordinate census is inconsistent")
    unresolved_wall_records = sum(
        1
        for path in paths
        if load_json(path)["coordinates"]["wall_record"]["comparison_state"]
        == "UNRESOLVED"
    )
    if index.get("unresolved_legacy_wall_observation_count") != unresolved_wall_records:
        errors.append("migration index unresolved-wall census is inconsistent")

    expected_receipt_paths: set[Path] = set()
    for path in paths:
        payload = load_json(path)
        for side in ("reference", "target"):
            try:
                receipt_path = resolve_artifact_path(
                    payload["source_reports"][side]["validation_receipt"]["uri"],
                    repository_root=ROOT,
                    base_directory=path.parent,
                )
            except ValueError:
                continue
            expected_receipt_paths.add(receipt_path)
    indexed_receipts = {
        item["receipt_uri"]: item
        for item in index.get("source_report_receipts", [])
    }
    expected_receipt_uris = {
        receipt_path.relative_to(ROOT).as_posix()
        for receipt_path in expected_receipt_paths
    }
    if index.get("source_report_receipt_count") != len(expected_receipt_paths):
        errors.append("migration index source-report receipt census is inconsistent")
    if set(indexed_receipts) != expected_receipt_uris:
        errors.append("migration index source-report receipt set is inconsistent")
    for uri, item in indexed_receipts.items():
        receipt_path = ROOT / uri
        if not receipt_path.is_file():
            errors.append(f"migration index receipt is missing: {uri}")
        elif item["receipt_digest"]["value"].lower() != sha256(receipt_path):
            errors.append(f"migration index receipt digest mismatch: {uri}")

    records = {record["output_uri"]: record for record in index.get("records", [])}
    for path in paths:
        uri = f"audits/{path.name}"
        record = records.get(uri)
        if record is None:
            errors.append(f"migration index lacks {uri}")
        elif record["output_digest"]["value"].lower() != sha256(path):
            errors.append(f"migration index output digest mismatch: {uri}")
    if set(records) != {f"audits/{path.name}" for path in paths}:
        errors.append("migration index contains an unmatched output record")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema = load_json(args.schema)
    Draft202012Validator.check_schema(schema)
    migration_paths = sorted(DEFAULT_DIR.glob("*.sofaudit.json"))
    native_paths = sorted(NATIVE_DIR.glob("**/*.sofaudit.json"))
    paths = args.paths or [*migration_paths, *native_paths]
    if not paths:
        raise SystemExit("No SOFAUDIT v2 artifacts found.")

    failures = 0
    for path in paths:
        payload = load_json(path)
        errors = schema_errors(payload, schema) + semantic_errors(payload, path)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    if not args.paths:
        errors = index_errors(args.index, migration_paths)
        if errors:
            failures += 1
            print(f"FAIL {args.index}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS migration index: {args.index}")
        for receipt_path in sorted(NATIVE_DIR.glob("**/*.validation-receipt.json")):
            if load_json(receipt_path).get("artifact_type") != "sofaudit_validation_receipt":
                continue
            receipt_errors = validation_receipt_errors(receipt_path)
            if receipt_errors:
                failures += 1
                print(f"FAIL {receipt_path}")
                for error in receipt_errors:
                    print(f"  - {error}")
            else:
                print(f"PASS {receipt_path}")

    if failures:
        raise SystemExit(f"{failures} SOFAUDIT v2 validation target(s) failed.")
    print(
        f"Validated {len(paths)} SOFAUDIT v2 artifacts; the migration census "
        f"remains under {STANDARD_PROFILE_ID}."
    )


if __name__ == "__main__":
    main()
