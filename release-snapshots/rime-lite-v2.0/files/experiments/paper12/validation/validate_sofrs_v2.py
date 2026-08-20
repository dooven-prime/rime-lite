"""Validate SOFRS v2.0 reports and their Manifest/IR/Profile contract stack."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
sys.path.insert(0, str(ROOT))

from experiments.paper12.validation.migrate_sofrs_v1_to_v2 import (  # noqa: E402
    ADAPTER_ID,
    ADAPTER_VERSION,
    ANALOGUE_ASSEMBLY_PROFILE,
    ANALOGUE_COMPILER_PROFILE,
    STRICT_ASSEMBLY_PROFILE,
    STRICT_COMPILER_PROFILE,
    CLASSIFICATIONS,
    assemble_sofrs_report,
    compile_modules,
    normalize_semantic_labels,
    replace_unreached,
)
from schemas.sofcompiler.api import (  # noqa: E402
    compile_output_v1,
    ir_reference_errors,
    manifest_errors,
    profile_errors,
)
from schemas.contract_api import (  # noqa: E402
    artifact_reference_errors,
    file_digest,
    load_json,
    resolve_artifact_path,
    schema_errors,
)
from schemas.sofrs.api import (  # noqa: E402
    build_v2_report_validation_receipt,
    v2_report_validation_receipt_errors,
)


V2_DIR = PAPER_DIR / "results"
INDEX_PATH = V2_DIR / "migration-index.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas" / "sofcompiler" / "capability-manifest-v1.0.schema.json"
IR_SCHEMA_PATH = ROOT / "schemas" / "sofcompiler" / "typed-sof-ir-v1.0.schema.json"
PROFILE_SCHEMA_PATH = ROOT / "schemas" / "sofcompiler" / "report-profile-v1.0.schema.json"
ASSEMBLY_PROFILE_SCHEMA_PATH = ROOT / "schemas" / "sofrs" / "assembly-profile-v2.0.schema.json"
COMPILER_OUTPUT_SCHEMA_PATH = ROOT / "schemas" / "sofcompiler" / "compiler-output-v1.0.schema.json"
RULE_REGISTRY_PATH = ROOT / "schemas" / "sofcompiler" / "rule-registry-v1.0.json"
REPORT_SCHEMA_PATH = ROOT / "schemas" / "sofrs" / "v2.0.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.0.schema.json"
RECEIPT_DIR = V2_DIR / "report-validation-receipts" / "paper12-v2"
VALIDATION_INDEX_PATH = RECEIPT_DIR / "validation-index.json"
VALIDATOR_URI = "experiments/paper12/validation/validate_sofrs_v2.py"
EXTERNAL_CONSTRAINT_IDS = {
    "source-snapshot-pinned",
    "object-level-recomputation",
    "realization-structure-validation",
    "domain-semantic-adequacy",
}
EXTERNAL_BASIS_LEVELS = {
    "source_identity",
    "object_level",
    "structure_level",
    "semantic_adequacy",
}
RESULT_CLAIM_STATUS = {
    "ESTABLISHED": "Theorem",
    "CERTIFIED": "Computational Certificate",
    "OBSERVED": "Computational Observation",
}
CLAIM_COMPATIBILITY = {
    ("external_mathematical_object", "object"): {
        "compiler_ir",
        "domain_adapter",
        "independent_validator",
        "external_evaluator",
    },
    ("empirical_domain_system", "object"): {
        "domain_adapter",
        "independent_validator",
        "external_evaluator",
    },
    ("empirical_domain_system", None): {
        "domain_adapter",
        "external_evaluator",
    },
    ("representation_interface", "protocol_conformance"): {
        "compiler_ir",
        "assembly_profile",
        "assembly_validator",
        "independent_validator",
    },
    ("representation_interface", None): {
        "domain_adapter",
        "migration_adapter",
    },
    ("protocol_conformance", "protocol_conformance"): {
        "compiler_ir",
        "assembly_profile",
        "assembly_validator",
        "independent_validator",
    },
    ("migration_consistency", "migration_assembly"): {
        "migration_adapter",
        "assembly_validator",
        "independent_validator",
    },
}


def repo_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def artifact_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": repo_uri(path),
        "digest": {"algorithm": "sha256", "value": file_digest(path)},
    }


def reference_errors(reference: dict[str, Any], label: str) -> list[str]:
    return artifact_reference_errors(
        reference,
        label=label,
        repository_root=ROOT,
        allowed_algorithms=("sha256",),
    )


def contains_legacy_sentinel(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 999
    if isinstance(value, list):
        return any(contains_legacy_sentinel(item) for item in value)
    if isinstance(value, dict):
        return any(contains_legacy_sentinel(item) for item in value.values())
    return False


def contains_unreached(value: Any) -> bool:
    if isinstance(value, list):
        return any(contains_unreached(item) for item in value)
    if isinstance(value, dict):
        return any(contains_unreached(item) for item in value.values())
    return value == "UNREACHED_AT_CUTOFF"


def cutoff_errors(ir: dict[str, Any]) -> list[str]:
    affected_findings = [
        finding for finding in ir["findings"] if contains_unreached(finding["value"])
    ]
    if not affected_findings:
        return []

    policies = {policy["id"]: policy for policy in ir["run_policies"]}
    errors: list[str] = []
    for finding in affected_findings:
        cutoff_policies = [
            policies[policy_id]
            for policy_id in finding["run_policy_ids"]
            if policy_id in policies and policies[policy_id]["kind"] == "cutoff"
        ]
        if not cutoff_policies:
            errors.append(
                f"{finding['id']}: UNREACHED_AT_CUTOFF lacks a referenced cutoff policy"
            )
            continue
        for policy in cutoff_policies:
            specification = policy["specification"]
            maximum_depth = specification.get("maximum_depth")
            if (
                not isinstance(maximum_depth, int)
                or isinstance(maximum_depth, bool)
                or maximum_depth < 1
            ):
                errors.append(
                    f"{finding['id']}: cutoff policy lacks a positive maximum_depth"
                )
            if specification.get("unreached_value") != "UNREACHED_AT_CUTOFF":
                errors.append(
                    f"{finding['id']}: cutoff policy has the wrong unreached value"
                )
    return errors


def summary_errors(report: dict[str, Any], ir: dict[str, Any]) -> list[str]:
    errors = []
    ir_claims = {item["id"]: item for item in ir["claims"]}
    ir_findings = {item["id"]: item for item in ir["findings"]}
    carrier_kinds = {item["id"]: item["kind"] for item in ir["carriers"]}

    for summary in report["claims"]:
        claim_id = summary["claim_id"]
        if claim_id not in ir_claims:
            errors.append(f"report claim {claim_id}: absent from IR")
            continue
        claim = ir_claims[claim_id]
        expected_kinds = sorted(
            carrier_kinds[carrier_id]
            for carrier_id in claim["carrier_ids"]
            if carrier_id in carrier_kinds
        )
        expected = {
            "claim_id": claim["id"],
            "statement": claim["statement"],
            "result_state": claim["result_state"],
            "claim_status": claim["claim_status"],
            "claim_target": summary["claim_target"],
            "certificate_class": summary["certificate_class"],
            "classification_source": summary["classification_source"],
            "external_basis_refs": summary["external_basis_refs"],
            "external_constraint_ids": summary["external_constraint_ids"],
            "carrier_kinds": expected_kinds,
            "scope": claim["scope"],
            "negative_boundary": claim["negative_boundary"],
        }
        rendered_summary = {
            key: value
            for key, value in summary.items()
            if key not in {"report_item_id", "source_output_item_id"}
        }
        if rendered_summary != expected:
            errors.append(f"report claim {claim_id}: summary differs from IR")

    for summary in report["findings"]:
        finding_id = summary["finding_id"]
        if finding_id not in ir_findings:
            errors.append(f"report finding {finding_id}: absent from IR")
            continue
        finding = ir_findings[finding_id]
        expected = {
            "finding_id": finding["id"],
            "kind": finding["kind"],
            "result_state": finding["result_state"],
            "value": finding["value"],
        }
        if summary != expected:
            errors.append(f"report finding {finding_id}: summary differs from IR")

    module_claim_ids = {
        claim_id
        for module in report["modules"]
        if module["status"] == "ENABLED"
        for claim_id in module["claim_ids"]
    }
    module_finding_ids = {
        finding_id
        for module in report["modules"]
        if module["status"] == "ENABLED"
        for finding_id in module["finding_ids"]
    }
    if module_claim_ids != {item["claim_id"] for item in report["claims"]}:
        errors.append("enabled module claim IDs do not match rendered claims")
    if module_finding_ids != {item["finding_id"] for item in report["findings"]}:
        errors.append("enabled module finding IDs do not match rendered findings")
    return errors


def external_basis_errors(report: dict[str, Any]) -> list[str]:
    registry = report["external_basis_registry"]
    errors: list[str] = []
    source_artifacts = report["source_artifacts"]
    packages = registry["packages"]
    package_by_id = {package["basis_id"]: package for package in packages}
    if len(package_by_id) != len(packages):
        errors.append("external basis package ids must be unique")
    package_by_level: dict[str, list[dict[str, Any]]] = {
        level: [] for level in EXTERNAL_BASIS_LEVELS
    }
    for package in packages:
        if package["level"] not in EXTERNAL_BASIS_LEVELS:
            errors.append(f"unknown external basis level: {package['level']}")
        else:
            package_by_level[package["level"]].append(package)
        for constraint_id in package["constraint_ids"]:
            if constraint_id not in EXTERNAL_CONSTRAINT_IDS:
                errors.append(
                    f"external basis package {package['basis_id']} references unknown constraint"
                )
        for index, reference in enumerate(package["evidence_artifacts"]):
            errors.extend(
                reference_errors(
                    reference,
                    f"external basis package {package['basis_id']} evidence {index}",
                )
            )
            if reference not in source_artifacts:
                errors.append(
                    f"external basis package {package['basis_id']} evidence is outside the report source-artifact closure"
                )
        if package["status"] == "SATISFIED" and not package["evidence_artifacts"]:
            errors.append(
                f"external basis package {package['basis_id']} is SATISFIED without evidence artifacts"
            )

    constraints = registry["constraints"]
    constraint_ids = [item["constraint_id"] for item in constraints]
    if set(constraint_ids) != EXTERNAL_CONSTRAINT_IDS:
        errors.append("external basis constraint set is incomplete or has unknown ids")
    if len(constraint_ids) != len(set(constraint_ids)):
        errors.append("external basis constraint ids must be unique")
    constraint_by_id = {item["constraint_id"]: item for item in constraints}
    for index, constraint in enumerate(constraints):
        if constraint["basis_id"] not in package_by_id:
            errors.append(
                f"external constraint {constraint['constraint_id']} references an unknown basis package"
            )
        elif constraint["basis_id"] not in {
            package["basis_id"]
            for package in packages
            if constraint["constraint_id"] in package["constraint_ids"]
        }:
            errors.append(
                f"external constraint {constraint['constraint_id']} is not registered by its basis package"
            )
        for reference in constraint["evidence_artifacts"]:
            errors.extend(
                reference_errors(
                    reference,
                    f"external constraint {index} evidence",
                )
            )
            if reference not in source_artifacts:
                errors.append(
                    f"external constraint {constraint['constraint_id']} evidence is outside the report source-artifact closure"
                )
        if constraint["status"] == "SATISFIED" and not constraint["evidence_artifacts"]:
            errors.append(
                f"external constraint {constraint['constraint_id']} is SATISFIED without evidence artifacts"
            )

    for constraint_id, constraint in constraint_by_id.items():
        package = package_by_id.get(constraint["basis_id"])
        if package is not None and package["status"] != constraint["status"]:
            errors.append(
                f"external constraint {constraint_id} status differs from its basis package"
            )

    if registry["basis_status"] == "COMPLETE":
        if any(
            not package_by_level[level]
            or any(package["status"] != "SATISFIED" for package in package_by_level[level])
            for level in EXTERNAL_BASIS_LEVELS
        ):
            errors.append("COMPLETE external basis requires every applicable level to be SATISFIED")
        if any(constraint["status"] != "SATISFIED" for constraint in constraints):
            errors.append("COMPLETE external basis has an unsatisfied mandatory constraint")

    source_packages = package_by_level["source_identity"]
    for package in source_packages:
        if package["status"] == "SATISFIED" and package["evidence_artifacts"] != source_artifacts:
            errors.append(
                "external source identity evidence differs from report source artifacts"
            )

    for claim in report["claims"]:
        for basis_ref in claim["external_basis_refs"]:
            if basis_ref not in package_by_id:
                errors.append(
                    f"report claim {claim['claim_id']} references an unknown external basis package"
                )
        for constraint_id in claim["external_constraint_ids"]:
            if constraint_id not in constraint_by_id:
                errors.append(
                    f"report claim {claim['claim_id']} references an unknown external constraint"
                )
            elif constraint_by_id[constraint_id]["basis_id"] not in claim["external_basis_refs"]:
                errors.append(
                    f"report claim {claim['claim_id']} does not bind the basis package for constraint {constraint_id}"
                )
        if claim["certificate_class"] == "object":
            object_packages = [
                package_by_id[basis_ref]
                for basis_ref in claim["external_basis_refs"]
                if basis_ref in package_by_id
                and package_by_id[basis_ref]["level"] == "object_level"
            ]
            if not object_packages or any(
                package["status"] != "SATISFIED" or not package["evidence_artifacts"]
                for package in object_packages
            ):
                errors.append(
                    f"report claim {claim['claim_id']}: Object Certificate lacks a satisfied external object basis"
                )
            if "object-level-recomputation" not in claim["external_constraint_ids"]:
                errors.append(
                    f"report claim {claim['claim_id']}: Object Certificate lacks the object-level constraint binding"
                )
    if report["record_kind"] == "strict_sof":
        structure_packages = package_by_level["structure_level"]
        if not structure_packages or any(
            package["status"] != "SATISFIED" for package in structure_packages
        ):
            errors.append("strict_sof report lacks a satisfied external structure-level basis")
    return errors


def epistemic_classification_errors(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for claim in report["claims"]:
        label = f"report claim {claim['claim_id']}"
        status = claim["claim_status"]
        result_state = claim["result_state"]
        target = claim["claim_target"]
        certificate_class = claim["certificate_class"]
        expected_status = RESULT_CLAIM_STATUS.get(result_state)
        if expected_status is not None and status != expected_status:
            errors.append(
                f"{label}: result_state {result_state} must pair with {expected_status}"
            )
        if expected_status is None and status is not None:
            errors.append(
                f"{label}: result_state {result_state} cannot carry a positive claim status"
            )
        if status == "Computational Certificate":
            if certificate_class is None:
                errors.append(f"{label}: certificate class is required")
        elif certificate_class is not None:
            errors.append(f"{label}: non-certificate claim has a certificate class")
        allowed_sources = CLAIM_COMPATIBILITY.get((target, certificate_class))
        if allowed_sources is None:
            errors.append(
                f"{label}: claim target and certificate class are incompatible"
            )
        elif claim["classification_source"] not in allowed_sources:
            errors.append(
                f"{label}: classification source {claim['classification_source']} "
                f"cannot establish target {target} with class {certificate_class}"
            )
    return errors


def boundary_errors(
    report: dict[str, Any],
    manifest: dict[str, Any],
    ir: dict[str, Any],
) -> list[str]:
    errors = []
    if report["record_kind"] != manifest["record_kind"] or report["record_kind"] != ir["record_kind"]:
        errors.append("record_kind differs across report, manifest, and IR")

    object_kinds = {item["kind"] for item in ir["objects"]}
    carrier_kinds = {item["kind"] for item in ir["carriers"]}
    capabilities = manifest["capabilities"]
    if report["record_kind"] == "strict_sof":
        if manifest["space"]["scalar_field"] != "complex":
            errors.append("strict_sof manifest is not complex")
        if not isinstance(manifest["space"]["dimension"], int):
            errors.append("strict_sof manifest lacks a finite dimension")
        for capability_id in ("sectorization", "operator_carrier"):
            if capabilities[capability_id]["availability"] != "DECLARED":
                errors.append(f"strict_sof lacks {capability_id}")
        for object_kind in ("finite_space", "sectorization", "labelled_alphabet"):
            if object_kind not in object_kinds:
                errors.append(f"strict_sof lacks {object_kind} object")
        if capabilities["diagnostic_analogue"]["availability"] == "DECLARED":
            errors.append("strict_sof also declares diagnostic_analogue")
        if not any(
            certificate["status"] == "PASS"
            and certificate["id"] == "cert.strict-admission"
            for certificate in ir["certificates"]
        ):
            errors.append("strict_sof lacks a PASS strict-admission certificate")
    else:
        if capabilities["diagnostic_analogue"]["availability"] != "DECLARED":
            errors.append("diagnostic_analogue capability is absent")
        if {"finite_space", "sector_projector", "lie_family"}.intersection(object_kinds):
            errors.append("diagnostic_analogue contains strict finite/Lie objects")
        if {"sector", "operator", "lie", "hall"}.intersection(carrier_kinds):
            errors.append("diagnostic_analogue contains a strict carrier")
        if any(claim["claim_status"] == "Theorem" for claim in ir["claims"]):
            errors.append("diagnostic_analogue emits a theorem claim")

    if contains_legacy_sentinel(manifest) or contains_legacy_sentinel(ir) or contains_legacy_sentinel(report):
        errors.append("generated v2 artifact contains legacy integer sentinel 999")
    return errors


def alignment_readiness_errors(
    report: dict[str, Any],
    manifest: dict[str, Any],
    ir: dict[str, Any],
    compiler_profile: dict[str, Any],
    assembly_profile: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    readiness = report["alignment_readiness"]
    if readiness["adapter"] != {
        "id": manifest["adapter"]["id"],
        "version": manifest["adapter"]["version"],
    }:
        errors.append("alignment readiness adapter differs from manifest")
    if readiness["compiler_profile_id"] != compiler_profile["profile_id"]:
        errors.append("alignment readiness compiler_profile_id differs")
    if readiness["assembly_profile_id"] != assembly_profile["assembly_profile_id"]:
        errors.append("alignment readiness assembly_profile_id differs")

    carrier_kinds = sorted({carrier["kind"] for carrier in ir["carriers"]})
    if readiness["carrier_kinds"] != carrier_kinds:
        errors.append("alignment readiness carrier kinds differ from IR")
    semantic_items = [
        {"id": item["id"], "kind": item["kind"]}
        for item in ir["semantic_conventions"]
    ]
    if readiness["semantic_conventions"] != semantic_items:
        errors.append("alignment readiness semantic conventions differ from IR")
    policy_items = [
        {"id": item["id"], "kind": item["kind"]}
        for item in ir["run_policies"]
    ]
    if readiness["run_policies"] != policy_items:
        errors.append("alignment readiness run policies differ from IR")
    if readiness["source_artifact_digests"] != report["source_artifacts"]:
        errors.append("alignment readiness source digests differ from report provenance")

    if report["record_kind"] == "strict_sof":
        if readiness["sector_metadata"]["status"] != "PRESENT":
            errors.append("strict report lacks alignment-ready sector metadata")
        if readiness["observable_metadata"]["status"] != "PRESENT":
            errors.append("strict report lacks alignment-ready observable metadata")
    else:
        if readiness["sector_metadata"]["status"] == "PRESENT":
            errors.append("analogue report presents undeclared strict sector metadata")
        if readiness["observable_metadata"]["status"] == "PRESENT":
            errors.append("analogue report presents undeclared strict observable metadata")
    return errors


def source_mapping_errors(
    report: dict[str, Any], manifest: dict[str, Any]
) -> list[str]:
    mapping = report["source_mapping"]
    errors: list[str] = []
    if mapping["adapter_id"] != manifest["adapter"]["id"]:
        errors.append("source mapping adapter_id differs from the manifest adapter")
    if mapping["adapter_version"] != manifest["adapter"]["version"]:
        errors.append("source mapping adapter_version differs from the manifest adapter")
    if mapping["status"] == "migrated":
        if mapping["adapter_id"] != ADAPTER_ID:
            errors.append("migrated source mapping uses a non-migration adapter")
        if mapping["adapter_version"] != ADAPTER_VERSION:
            errors.append("migrated source mapping uses the wrong migration-adapter version")
    elif report["provenance"]["kind"] != "native_generation":
        errors.append("native or adapter-derived source mapping must use native_generation provenance")
    return errors


def provenance_errors(report: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Check the disjoint native/migration provenance closure."""

    provenance = report["provenance"]
    source_artifacts = report["source_artifacts"]
    source_by_uri = {item["uri"]: item for item in source_artifacts}
    errors: list[str] = []

    def same_reference(left: dict[str, Any], right: dict[str, Any]) -> bool:
        return left.get("uri") == right.get("uri") and left.get("digest") == right.get("digest")

    def check_reference(reference: dict[str, Any], label: str) -> None:
        errors.extend(reference_errors(reference, label))

    kind = provenance.get("kind")
    status = report["source_mapping"]["status"]
    expected_kind = "migration" if status == "migrated" else "native_generation"
    if kind != expected_kind:
        errors.append(
            f"source_mapping.status={status!r} requires provenance.kind={expected_kind!r}"
        )

    if kind == "migration":
        source = provenance["source_artifact"]
        adapter = provenance["migration_adapter_ref"]
        receipt = provenance["migration_receipt_ref"]
        check_reference(source, "provenance.source_artifact")
        check_reference(adapter, "provenance.migration_adapter_ref")
        check_reference(receipt, "provenance.migration_receipt_ref")
        if source.get("uri") not in source_by_uri:
            errors.append("migration provenance source_artifact is absent from source_artifacts")
        elif not same_reference(source, source_by_uri[source["uri"]]):
            errors.append("migration provenance source_artifact digest differs from source_artifacts")
        if provenance.get("source_sofrs_version") == "2.0":
            errors.append("native-v2 cannot be declared as a migration source")
        if status != "migrated":
            errors.append("migration provenance requires source_mapping.status=migrated")
        return errors

    if kind == "native_generation":
        for key in (
            "producer",
            "source_snapshot",
            "adapter",
            "compiler_profile_ref",
            "compiler_output_ref",
            "assembly_profile_ref",
        ):
            check_reference(provenance[key], f"provenance.{key}")
        for key in ("producer", "source_snapshot"):
            if not any(same_reference(provenance[key], item) for item in source_artifacts):
                errors.append(f"native provenance {key} is absent from source_artifacts")
        if not same_reference(provenance["source_snapshot"], source_artifacts[0]):
            errors.append("native source_snapshot must be the first source artifact")
        if not same_reference(provenance["compiler_profile_ref"], report["compiler_contracts"]["compiler_profile"]):
            errors.append("native compiler_profile_ref differs from compiler_contracts")
        if not same_reference(provenance["compiler_output_ref"], report["compiler_contracts"]["compiler_output"]):
            errors.append("native compiler_output_ref differs from compiler_contracts")
        if not same_reference(provenance["assembly_profile_ref"], report["assembly_contract"]["assembly_profile"]):
            errors.append("native assembly_profile_ref differs from assembly_contract")
        if status not in {"native", "adapter-derived"}:
            errors.append("native_generation provenance cannot use migrated source mapping")
        if provenance["adapter"]["uri"] != provenance["producer"]["uri"]:
            errors.append("native adapter and producer must identify the same implementation")
    return errors


def reconstruction_errors(
    report: dict[str, Any], index_entry: dict[str, Any] | None = None
) -> list[str]:
    assessment = report["strict_reconstruction"]
    errors: list[str] = []
    if index_entry is not None and assessment != index_entry["strict_reconstruction"]:
        errors.append("strict reconstruction assessment differs from migration index")
    if report["record_kind"] == "strict_sof" and assessment["candidate_status"] != "not_applicable":
        errors.append("strict_sof report must mark reconstruction candidate status not_applicable")
    if report["record_kind"] == "diagnostic_analogue" and assessment["candidate_status"] == "not_applicable":
        errors.append("diagnostic analogue cannot mark reconstruction candidate not_applicable")
    if assessment["candidate_status"] == "yes":
        if not assessment["available_requirements"]:
            errors.append("reconstruction candidate lacks available requirements")
        if not assessment["missing_requirements"]:
            errors.append("reconstruction candidate lacks missing obligations")
        if report["record_kind"] != "diagnostic_analogue":
            errors.append("an admitted strict report cannot remain a reconstruction candidate")
    return errors


def compiler_output_errors(
    manifest: dict[str, Any],
    ir: dict[str, Any],
    profile: dict[str, Any],
    compiler_output: dict[str, Any],
    rule_registry: dict[str, Any],
) -> list[str]:
    expected = compile_output_v1(manifest, ir, profile, rule_registry)
    if compiler_output == expected:
        return []
    return ["bound CompilerOutput differs from canonical Paper X Compile_v1 output"]


def assemble_normative_items(
    compiler_output: dict[str, Any], ir: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Render the identity-bearing normative item envelope for focused tests."""

    claims: list[dict[str, Any]] = []
    degradations: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    ir_claims = {item["id"]: item for item in ir.get("claims", [])}
    for index, item in enumerate(compiler_output["items"]):
        source_item_id = f"compiler.item.{index:04d}"
        report_item_id = f"report.{item['item_kind']}-item.{index:04d}"
        bindings.append(
            {
                "compiler_output_item_id": source_item_id,
                "report_item_id": report_item_id,
                "item_kind": item["item_kind"],
                "rendering_status": "rendered",
            }
        )
        if item["item_kind"] == "degradation":
            degradation = {
                "report_item_id": report_item_id,
                "source_output_item_id": source_item_id,
                "module_id": item["module_id"],
                "action": item["action"],
                "reason_kind": item["reason_kind"],
                "details": deepcopy(item["details"]),
            }
            if "source_ir_id" in item:
                degradation["source_ir_id"] = item["source_ir_id"]
            degradations.append(degradation)
        elif item.get("claim_id") in ir_claims:
            claim = ir_claims[item["claim_id"]]
            claims.append(
                {
                    "report_item_id": report_item_id,
                    "source_output_item_id": source_item_id,
                    "claim_id": claim["id"],
                    "statement": claim["statement"],
                    "result_state": claim["result_state"],
                    "claim_status": claim["claim_status"],
                    "scope": claim["scope"],
                    "negative_boundary": claim["negative_boundary"],
                }
            )
    return claims, degradations, bindings


def assembly_faithfulness_errors(
    report: dict[str, Any],
    compiler_output: dict[str, Any],
    ir: dict[str, Any],
    compiler_profile: dict[str, Any],
    assembly_profile: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    ir_claims = {item["id"]: item for item in ir["claims"]}
    carrier_kinds = {item["id"]: item["kind"] for item in ir["carriers"]}
    classifications = {
        item["claim_id"]: {
            "claim_target": item["claim_target"],
            "certificate_class": item["certificate_class"],
            "classification_source": item["classification_source"],
            "external_basis_refs": item["external_basis_refs"],
            "external_constraint_ids": item["external_constraint_ids"],
        }
        for item in report["claims"]
    }
    expected_claims: list[dict[str, Any]] = []
    expected_degradations: list[dict[str, Any]] = []
    expected_bindings: list[dict[str, Any]] = []
    for index, item in enumerate(compiler_output["items"]):
        source_item_id = f"compiler.item.{index:04d}"
        report_item_id = f"report.{item['item_kind']}-item.{index:04d}"
        expected_bindings.append(
            {
                "compiler_output_item_id": source_item_id,
                "report_item_id": report_item_id,
                "item_kind": item["item_kind"],
                "rendering_status": "rendered",
            }
        )
        if item["item_kind"] == "claim":
            claim = ir_claims[item["claim_id"]]
            classification = classifications.get(claim["id"])
            if classification is None:
                errors.append(
                    f"CompilerOutput claim {claim['id']} lacks an assembly classification"
                )
                continue
            expected_claims.append(
                {
                    "report_item_id": report_item_id,
                    "source_output_item_id": source_item_id,
                    "claim_id": claim["id"],
                    "statement": claim["statement"],
                    "result_state": claim["result_state"],
                    "claim_status": claim["claim_status"],
                    **deepcopy(classification),
                    "carrier_kinds": sorted(
                        {
                            carrier_kinds[carrier_id]
                            for carrier_id in claim["carrier_ids"]
                            if carrier_id in carrier_kinds
                        }
                    ),
                    "scope": claim["scope"],
                    "negative_boundary": claim["negative_boundary"],
                }
            )
        else:
            degradation = {
                "report_item_id": report_item_id,
                "source_output_item_id": source_item_id,
                "module_id": item["module_id"],
                "action": item["action"],
                "reason_kind": item["reason_kind"],
                "details": deepcopy(item["details"]),
            }
            if "source_ir_id" in item:
                degradation["source_ir_id"] = item["source_ir_id"]
            expected_degradations.append(degradation)
    if report["claims"] != expected_claims:
        errors.append("assembled claim items are not faithful to CompilerOutput")
    if report["degradation_items"] != expected_degradations:
        errors.append("assembled degradation items are not faithful to CompilerOutput")
    if report["item_bindings"] != expected_bindings:
        errors.append("assembly item bindings are not a typed identity bijection")

    source_ids = [item["compiler_output_item_id"] for item in report["item_bindings"]]
    report_ids = [item["report_item_id"] for item in report["item_bindings"]]
    report_items = {
        item["report_item_id"]: "claim"
        for item in report["claims"]
    }
    report_items.update(
        {
            item["report_item_id"]: "degradation"
            for item in report["degradation_items"]
        }
    )
    compiler_items = {
        f"compiler.item.{index:04d}": item["item_kind"]
        for index, item in enumerate(compiler_output["items"])
    }
    if len(source_ids) != len(set(source_ids)):
        errors.append("assembly duplicates a CompilerOutput item identity")
    if len(report_ids) != len(set(report_ids)):
        errors.append("assembly duplicates a report item identity")
    if len(source_ids) != len(compiler_output["items"]):
        errors.append("assembly adds or removes normative CompilerOutput items")
    if set(source_ids) != set(compiler_items):
        errors.append("assembly bindings do not cover exactly the CompilerOutput items")
    if set(report_ids) != set(report_items):
        errors.append("assembly bindings do not cover exactly the report normative items")
    for binding in report["item_bindings"]:
        if binding["compiler_output_item_id"] in compiler_items and binding["item_kind"] != compiler_items[binding["compiler_output_item_id"]]:
            errors.append("assembly binding item_kind differs from CompilerOutput")
        if binding["report_item_id"] in report_items and binding["item_kind"] != report_items[binding["report_item_id"]]:
            errors.append("assembly binding item_kind differs from report item")

    binding = report["compiler_output_binding"]
    if binding["artifact"] != report["compiler_contracts"]["compiler_output"]:
        errors.append("direct CompilerOutput binding differs from compiler contracts")
    if binding["compiler_id"] != compiler_output["compiler_id"]:
        errors.append("direct CompilerOutput binding has the wrong compiler_id")
    if binding["compiler_output_version"] != compiler_output["compiler_output_version"]:
        errors.append("direct CompilerOutput binding has the wrong version")
    if binding["compiler_profile_id"] != compiler_output["profile_id"]:
        errors.append("direct CompilerOutput binding has the wrong compiler profile")

    assembly = report["assembly_contract"]
    if assembly["assembly_profile_id"] != assembly_profile["assembly_profile_id"]:
        errors.append("assembly contract binds the wrong assembly profile id")
    if assembly_profile["compiler_profile_id"] != compiler_profile["profile_id"]:
        errors.append("assembly profile targets a different compiler profile")
    if assembly_profile["record_kind"] != report["record_kind"]:
        errors.append("assembly profile targets a different record kind")
    return errors


def report_reassembly_errors(
    index_entry: dict[str, Any],
    report: dict[str, Any],
    manifest_path: Path,
    ir_path: Path,
    compiler_profile_path: Path,
    assembly_profile_path: Path,
    compiler_output_path: Path,
    manifest: dict[str, Any],
    ir: dict[str, Any],
    compiler_output: dict[str, Any],
) -> list[str]:
    legacy_path = ROOT / index_entry["source"]
    legacy = load_json(legacy_path)
    name = legacy_path.stem
    classification = CLASSIFICATIONS[name]
    _, bridge_count = replace_unreached(legacy.get("bridge_matrix"))
    _, repair_count = replace_unreached(legacy.get("repair_matrix"))
    _, wall_count = replace_unreached(legacy.get("wall_record"))
    _, _, _, semantic_normalizations = normalize_semantic_labels(
        name,
        legacy.get("bridge_matrix"),
        legacy.get("repair_matrix"),
        legacy.get("wall_record"),
    )
    expected = assemble_sofrs_report(
        legacy_path,
        legacy,
        manifest_path,
        ir_path,
        compiler_profile_path,
        assembly_profile_path,
        compiler_output_path,
        manifest,
        ir,
        compiler_output,
        classification,
        bridge_count + repair_count + wall_count,
    )
    expected["provenance"]["semantic_normalizations"] = semantic_normalizations
    if report == expected:
        return []
    return ["report differs from canonical Assemble_v2 recomputation"]


def validate_record(
    index_entry: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
    rule_registry: dict[str, Any],
) -> list[str]:
    errors = []
    manifest_path = ROOT / index_entry["manifest"]
    ir_path = ROOT / index_entry["ir"]
    report_path = ROOT / index_entry["report"]
    compiler_output_path = ROOT / index_entry["compiler_output"]
    manifest = load_json(manifest_path)
    ir = load_json(ir_path)
    report = load_json(report_path)
    compiler_output = load_json(compiler_output_path)
    compiler_profile_path = (
        STRICT_COMPILER_PROFILE
        if report["record_kind"] == "strict_sof"
        else ANALOGUE_COMPILER_PROFILE
    )
    assembly_profile_path = (
        STRICT_ASSEMBLY_PROFILE
        if report["record_kind"] == "strict_sof"
        else ANALOGUE_ASSEMBLY_PROFILE
    )
    compiler_profile = load_json(compiler_profile_path)
    assembly_profile = load_json(assembly_profile_path)

    for label, payload, schema in (
        ("manifest", manifest, schemas["manifest"]),
        ("ir", ir, schemas["ir"]),
        ("compiler profile", compiler_profile, schemas["profile"]),
        ("assembly profile", assembly_profile, schemas["assembly_profile"]),
        ("compiler output", compiler_output, schemas["compiler_output"]),
        ("report", report, schemas["report"]),
    ):
        errors.extend(f"{label} schema: {error}" for error in schema_errors(payload, schema))
    if errors:
        return errors

    errors.extend(manifest_errors(manifest))
    errors.extend(ir_reference_errors(manifest, ir, rule_registry))
    profile_validation_errors, _ = profile_errors(
        manifest, ir, compiler_profile, rule_registry
    )
    errors.extend(profile_validation_errors)

    errors.extend(compiler_output_errors(
        manifest,
        ir,
        compiler_profile,
        compiler_output,
        rule_registry,
    ))

    expected_modules = compile_modules(compiler_output, ir, compiler_profile)
    if report["modules"] != expected_modules:
        errors.append("compiled report modules differ from capability-gated profile output")

    errors.extend(summary_errors(report, ir))
    errors.extend(external_basis_errors(report))
    errors.extend(epistemic_classification_errors(report))
    errors.extend(
        assembly_faithfulness_errors(
            report,
            compiler_output,
            ir,
            compiler_profile,
            assembly_profile,
        )
    )
    errors.extend(
        report_reassembly_errors(
            index_entry,
            report,
            manifest_path,
            ir_path,
            compiler_profile_path,
            assembly_profile_path,
            compiler_output_path,
            manifest,
            ir,
            compiler_output,
        )
    )
    errors.extend(boundary_errors(report, manifest, ir))
    errors.extend(cutoff_errors(ir))
    errors.extend(
        alignment_readiness_errors(
            report, manifest, ir, compiler_profile, assembly_profile
        )
    )
    errors.extend(source_mapping_errors(report, manifest))
    errors.extend(provenance_errors(report, manifest))
    errors.extend(reconstruction_errors(report, index_entry))
    for label, reference in (
        ("manifest", report["compiler_contracts"]["capability_manifest"]),
        ("IR", report["compiler_contracts"]["typed_sof_ir"]),
        ("compiler profile", report["compiler_contracts"]["compiler_profile"]),
        ("compiler output", report["compiler_contracts"]["compiler_output"]),
        ("assembly profile", report["assembly_contract"]["assembly_profile"]),
        ("assembly implementation", report["assembly_contract"]["implementation"]),
    ):
        errors.extend(reference_errors(reference, label))
    for index, reference in enumerate(report["source_artifacts"]):
        errors.extend(reference_errors(reference, f"source_artifacts[{index}]"))

    source_by_uri = {reference["uri"]: reference for reference in report["source_artifacts"]}
    expected_source_uris = {index_entry["source"], index_entry["producer"]}
    if set(source_by_uri) != expected_source_uris:
        errors.append("report source artifacts differ from migration index")
    else:
        if (
            source_by_uri[index_entry["source"]]["digest"]["value"]
            != index_entry["source_digest"]
        ):
            errors.append("migration index source digest differs from report")
        if (
            source_by_uri[index_entry["producer"]]["digest"]["value"]
            != index_entry["producer_digest"]
        ):
            errors.append("migration index producer digest differs from report")

    if report["compiler_contracts"]["capability_manifest"]["uri"] != index_entry["manifest"]:
        errors.append("report manifest URI differs from migration index")
    if report["compiler_contracts"]["typed_sof_ir"]["uri"] != index_entry["ir"]:
        errors.append("report IR URI differs from migration index")
    if (
        report["compiler_contracts"]["compiler_profile"]["uri"]
        != index_entry["compiler_profile"]
    ):
        errors.append("report compiler profile URI differs from migration index")
    if (
        report["compiler_contracts"]["compiler_output"]["uri"]
        != index_entry["compiler_output"]
    ):
        errors.append("report CompilerOutput URI differs from migration index")
    if (
        report["assembly_contract"]["assembly_profile"]["uri"]
        != index_entry["assembly_profile"]
    ):
        errors.append("report assembly profile URI differs from migration index")
    if report["record_kind"] != index_entry["record_kind"]:
        errors.append("report record_kind differs from migration index")
    return errors


def standalone_report_errors(report_path: Path) -> list[str]:
    """Validate one SOFRS v2 report without assuming migration-index membership."""

    report = load_json(report_path)
    schemas = {
        "manifest": load_json(MANIFEST_SCHEMA_PATH),
        "ir": load_json(IR_SCHEMA_PATH),
        "profile": load_json(PROFILE_SCHEMA_PATH),
        "assembly_profile": load_json(ASSEMBLY_PROFILE_SCHEMA_PATH),
        "compiler_output": load_json(COMPILER_OUTPUT_SCHEMA_PATH),
        "report": load_json(REPORT_SCHEMA_PATH),
    }
    errors = schema_errors(report, schemas["report"])
    if errors:
        return [f"report schema: {error}" for error in errors]

    references = {
        "manifest": report["compiler_contracts"]["capability_manifest"],
        "ir": report["compiler_contracts"]["typed_sof_ir"],
        "compiler profile": report["compiler_contracts"]["compiler_profile"],
        "compiler output": report["compiler_contracts"]["compiler_output"],
        "assembly profile": report["assembly_contract"]["assembly_profile"],
        "assembly implementation": report["assembly_contract"]["implementation"],
    }
    paths: dict[str, Path] = {}
    for label, reference in references.items():
        errors.extend(reference_errors(reference, label))
        try:
            paths[label] = resolve_artifact_path(
                reference["uri"], repository_root=ROOT
            )
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
    for index, reference in enumerate(report["source_artifacts"]):
        errors.extend(reference_errors(reference, f"source_artifacts[{index}]"))
    if errors:
        return errors

    manifest = load_json(paths["manifest"])
    ir = load_json(paths["ir"])
    compiler_profile = load_json(paths["compiler profile"])
    compiler_output = load_json(paths["compiler output"])
    assembly_profile = load_json(paths["assembly profile"])
    for label, payload, schema in (
        ("manifest", manifest, schemas["manifest"]),
        ("IR", ir, schemas["ir"]),
        ("compiler profile", compiler_profile, schemas["profile"]),
        ("compiler output", compiler_output, schemas["compiler_output"]),
        ("assembly profile", assembly_profile, schemas["assembly_profile"]),
    ):
        errors.extend(f"{label} schema: {error}" for error in schema_errors(payload, schema))
    if errors:
        return errors

    rule_registry = load_json(RULE_REGISTRY_PATH)
    errors.extend(manifest_errors(manifest))
    errors.extend(ir_reference_errors(manifest, ir, rule_registry))
    profile_validation_errors, _ = profile_errors(
        manifest, ir, compiler_profile, rule_registry
    )
    errors.extend(profile_validation_errors)
    errors.extend(
        compiler_output_errors(
            manifest, ir, compiler_profile, compiler_output, rule_registry
        )
    )
    if report["modules"] != compile_modules(compiler_output, ir, compiler_profile):
        errors.append("compiled report modules differ from capability-gated profile output")
    errors.extend(summary_errors(report, ir))
    errors.extend(external_basis_errors(report))
    errors.extend(epistemic_classification_errors(report))
    errors.extend(
        assembly_faithfulness_errors(
            report, compiler_output, ir, compiler_profile, assembly_profile
        )
    )
    errors.extend(boundary_errors(report, manifest, ir))
    errors.extend(cutoff_errors(ir))
    errors.extend(
        alignment_readiness_errors(
            report, manifest, ir, compiler_profile, assembly_profile
        )
    )
    errors.extend(source_mapping_errors(report, manifest))
    errors.extend(provenance_errors(report, manifest))
    errors.extend(reconstruction_errors(report))
    return errors


def issue_validation_receipt(
    index_entry: dict[str, Any],
) -> tuple[Path, list[str]]:
    report_path = ROOT / index_entry["report"]
    report = load_json(report_path)
    stem = report_path.name.removesuffix(".sofreport.json")
    receipt_path = RECEIPT_DIR / f"{stem}.validation-receipt.json"
    receipt = build_v2_report_validation_receipt(
        report_path,
        report_uri=repo_uri(report_path),
        validator_path=Path(__file__),
        validator_uri=VALIDATOR_URI,
    )
    write_json(receipt_path, receipt)
    expected_report_reference = {
        "report_id": report["report_id"],
        "sofrs_version": report["sofrs_version"],
        "record_kind": report["record_kind"],
        "artifact": artifact_reference(report_path),
    }
    errors = v2_report_validation_receipt_errors(
        receipt,
        repository_root=ROOT,
        expected_report_reference=expected_report_reference,
    )
    return receipt_path, errors


def main() -> None:
    index = load_json(INDEX_PATH)
    if index.get("migration_version") != "2.0":
        raise SystemExit("Unsupported or missing SOFRS v2 migration index.")
    if len(index.get("records", [])) != 9:
        raise SystemExit("The SOFRS v2 migration index must contain nine records.")

    schemas = {
        "manifest": load_json(MANIFEST_SCHEMA_PATH),
        "ir": load_json(IR_SCHEMA_PATH),
        "profile": load_json(PROFILE_SCHEMA_PATH),
        "assembly_profile": load_json(ASSEMBLY_PROFILE_SCHEMA_PATH),
        "compiler_output": load_json(COMPILER_OUTPUT_SCHEMA_PATH),
        "report": load_json(REPORT_SCHEMA_PATH),
        "receipt": load_json(RECEIPT_SCHEMA_PATH),
    }
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    rule_registry = load_json(RULE_REGISTRY_PATH)

    failures = 0
    strict_count = 0
    analogue_count = 0
    reconstruction_yes_count = 0
    receipt_paths: list[Path] = []
    for entry in index["records"]:
        errors = validate_record(entry, schemas, rule_registry)
        receipt_path = None
        if not errors:
            receipt_path, receipt_errors = issue_validation_receipt(entry)
            errors.extend(f"validation receipt: {error}" for error in receipt_errors)
        if errors:
            failures += 1
            print(f"FAIL {entry['report']}")
            for error in errors:
                print(f"  - {error}")
        else:
            receipt_paths.append(receipt_path)
            print(
                f"PASS {entry['record_kind']} {entry['report']} "
                f"-> {repo_uri(receipt_path)}"
            )
        strict_count += entry["record_kind"] == "strict_sof"
        analogue_count += entry["record_kind"] == "diagnostic_analogue"
        reconstruction_yes_count += (
            entry["strict_reconstruction"]["candidate_status"] == "yes"
        )

    if failures:
        raise SystemExit(f"{failures} SOFRS v2 record(s) failed validation.")

    expected_receipts = set(receipt_paths)
    actual_receipts = set(RECEIPT_DIR.glob("*.validation-receipt.json"))
    if actual_receipts != expected_receipts:
        extra = sorted(repo_uri(path) for path in actual_receipts - expected_receipts)
        missing = sorted(repo_uri(path) for path in expected_receipts - actual_receipts)
        raise SystemExit(
            f"SOFRS v2 receipt set mismatch: extra={extra or 'none'}, "
            f"missing={missing or 'none'}"
        )
    validation_index = {
        "validation_version": "2.0",
        "validator": artifact_reference(Path(__file__)),
        "receipt_contract": artifact_reference(RECEIPT_SCHEMA_PATH),
        "report_count": len(receipt_paths),
        "receipts": [
            {
                "report": entry["report"],
                "receipt": repo_uri(path),
                "receipt_digest": {
                    "algorithm": "sha256",
                    "value": file_digest(path),
                },
            }
            for entry, path in zip(index["records"], receipt_paths, strict=True)
        ],
    }
    write_json(VALIDATION_INDEX_PATH, validation_index)
    print(
        f"Validated 9 SOFRS v2 reports: "
        f"{strict_count} strict_sof, {analogue_count} diagnostic_analogue; "
        f"{reconstruction_yes_count} controlled reconstruction assessment(s) "
        "with status yes."
    )
    print(
        "PASS compile_v1 recomputation, assembly faithfulness, capability gates, "
        "evidence links, strict/analogue boundary, and sentinel migration"
    )


if __name__ == "__main__":
    main()
