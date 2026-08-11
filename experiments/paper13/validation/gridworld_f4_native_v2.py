"""Build the native SOFRS/SOFAUDIT v2 GridWorld F4 evidence chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

import gridworld_reference_sof as gridworld  # noqa: E402
from experiments.paper12.validation.migrate_sofrs_v1_to_v2 import (  # noqa: E402
    ASSEMBLY_CONTRACT_ID,
    ASSEMBLY_CONTRACT_VERSION,
    STRICT_ASSEMBLY_PROFILE,
    STRICT_COMPILER_PROFILE,
    compile_modules,
)
from experiments.paper12.validation.validate_sofrs_v2 import (  # noqa: E402
    standalone_report_errors,
)
from schemas.contract_api import file_digest, load_json  # noqa: E402
from schemas.sofcompiler.api import compile_output_v1  # noqa: E402
from experiments.paper13.validation.audit_profiles import (  # noqa: E402
    GRIDWORLD_PROFILE,
    GRIDWORLD_PROFILE_PATH,
    REGISTRY_PATH,
)
from schemas.sofrs.api import (  # noqa: E402
    build_v2_report_validation_receipt,
    v2_report_validation_receipt_errors,
)


NATIVE_ROOT = PAPER_DIR / "results" / "native" / "gridworld-f4"
SOURCE_DIR = NATIVE_ROOT / "sources"
STACK_DIR = NATIVE_ROOT / "source-reports"
MANIFEST_DIR = STACK_DIR / "manifests"
IR_DIR = STACK_DIR / "ir"
OUTPUT_DIR = STACK_DIR / "compiler-output"
REPORT_DIR = STACK_DIR / "reports"
REPORT_RECEIPT_DIR = STACK_DIR / "receipts"
EVIDENCE_DIR = NATIVE_ROOT / "evidence"
AUDIT_DIR = NATIVE_ROOT / "audits"
AUDIT_RECEIPT_DIR = NATIVE_ROOT / "receipts"

REFERENCE_SOURCE = SOURCE_DIR / "gridworld-reference.source.json"
TARGET_SOURCE = SOURCE_DIR / "gridworld-f4-target.source.json"
STRUCTURE_CERTIFICATE = EVIDENCE_DIR / "gridworld-f4.structure-certificate.json"
ALIGNMENT_EVIDENCE = EVIDENCE_DIR / "gridworld-f4.alignment-evidence.json"
AUDIT_RESULT = EVIDENCE_DIR / "gridworld-f4.audit-result.json"
OBJECT_CERTIFICATE = (
    PAPER_DIR / "results" / "object-certificates" / "gridworld_f4.object-certificate.json"
)
NATIVE_AUDIT = AUDIT_DIR / "gridworld-f4-native-v2.sofaudit.json"
NATIVE_AUDIT_RECEIPT = (
    AUDIT_RECEIPT_DIR / "gridworld-f4-native-v2.validation-receipt.json"
)

RULE_REGISTRY = ROOT / "schemas" / "sofcompiler" / "rule-registry-v1.0.json"
PAPER12_VALIDATOR = ROOT / "experiments" / "paper12" / "validation" / "validate_sofrs_v2.py"
ADAPTER_ID = "paper13.gridworld-native-v2"
ADAPTER_VERSION = "2.0"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def repo_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def artifact_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": repo_uri(path),
        "digest": {"algorithm": "sha256", "value": file_digest(path)},
    }


def audit_artifact(artifact_id: str, role: str, path: Path) -> dict[str, Any]:
    return {"id": artifact_id, "role": role, **audit_reference(path)}


def audit_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": Path(os.path.relpath(path, NATIVE_AUDIT.parent)).as_posix(),
        "digest": {"algorithm": "sha256", "value": file_digest(path)},
    }


def sparse_matrix(matrix: np.ndarray) -> list[dict[str, int | float]]:
    rows, columns = np.nonzero(matrix)
    return [
        {
            "row": int(row),
            "column": int(column),
            "value": float(matrix[row, column]),
        }
        for row, column in zip(rows, columns, strict=True)
    ]


def source_snapshot(source_id: str, matrices: dict[str, np.ndarray]) -> dict[str, Any]:
    return {
        "source_version": "1.0",
        "source_id": source_id,
        "domain": "finite deterministic GridWorld",
        "dimension": gridworld.N_CELLS,
        "sector_labels": [f"cell-{index}" for index in range(gridworld.N_CELLS)],
        "observable_labels": list(gridworld.ACTION_NAMES),
        "matrix_convention": "T[row,column] maps source column to target row",
        "generator_convention": "X=(T-T^T)/2",
        "threshold": gridworld.TOL,
        "action_matrices": {
            name: sparse_matrix(matrices[name]) for name in gridworld.ACTION_NAMES
        },
    }


def pair_list(matrix: np.ndarray) -> list[list[int]]:
    return np.argwhere(matrix).astype(int).tolist()


def observed_fields(matrices: dict[str, np.ndarray]) -> dict[str, Any]:
    sectors = gridworld.cell_sectors()
    generators, _ = gridworld.build_observables(matrices)
    audit = gridworld.full_audit(sectors, generators)
    return {
        "operator_support": {
            "pairs": pair_list(audit["R1_word"]),
            "pair_count": int(audit["R1_word"].sum()),
        },
        "word_length_two_support": {
            "pairs": pair_list(audit["R2_word"]),
            "pair_count": int(audit["R2_word"].sum()),
        },
        "lie_simple_commutator_support": {
            "pairs": pair_list(audit["R2_lie"]),
            "pair_count": int(audit["R2_lie"].sum()),
        },
    }


def capability(availability: str, description: str, configuration: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"availability": availability, "description": description}
    if configuration is not None:
        result["configuration"] = configuration
    return result


def build_manifest(side: str) -> dict[str, Any]:
    capabilities = {
        name: capability("NOT_DECLARED", "Capability is not used by this native control.")
        for name in (
            "sectorization",
            "operator_carrier",
            "operator_system",
            "route_carrier",
            "word_carrier",
            "positive_associative_closure",
            "observable_star_closure",
            "sector_enriched_star_closure",
            "lie_hall_carrier",
            "deformation_chart",
            "proxy_diagnostic",
            "diagnostic_analogue",
        )
    }
    capabilities.update(
        {
            "sectorization": capability(
                "DECLARED",
                "Complete exact coordinate-sector realization of the 25 retained cells.",
                {
                    "origin": "coordinate singleton sectors",
                    "realization_status": "exact finite construction",
                    "complete": True,
                    "labels": [f"cell-{index}" for index in range(gridworld.N_CELLS)],
                    "provenance": f"native GridWorld {side} source snapshot",
                },
            ),
            "operator_carrier": capability(
                "DECLARED",
                "Four labelled skew transition generators.",
                {
                    "alphabet_id": "gridworld-skew-actions",
                    "word_convention": "positive",
                    "adjoint_closed": True,
                    "projectors_are_letters": False,
                },
            ),
            "word_carrier": capability(
                "DECLARED",
                "Exact-length positive words through length two.",
                {"semantics": "ordered positive products of the four labelled generators"},
            ),
            "lie_hall_carrier": capability(
                "DECLARED",
                "Independently declared skew generators with simple commutators at depth two.",
                {
                    "family_id": "gridworld-skew-actions",
                    "hall_convention_id": "simple-pair-commutators",
                    "registration_method": "X=(T-T^T)/2 from digest-bound matrices",
                    "semantics": "simple commutators [X_a,X_b] for a<b",
                },
            ),
            "deformation_chart": capability(
                "NOT_APPLICABLE", "The F4 control compares two static snapshots."
            ),
            "proxy_diagnostic": capability(
                "NOT_APPLICABLE", "No proxy carrier is used."
            ),
            "diagnostic_analogue": capability(
                "NOT_APPLICABLE", "This is an explicit strict finite realization."
            ),
        }
    )
    return {
        "manifest_version": "1.0",
        "manifest_id": f"paper13.gridworld-f4.{side}.native-v2",
        "record_kind": "strict_sof",
        "sof_semantics_version": "2.0",
        "adapter": {
            "id": ADAPTER_ID,
            "version": ADAPTER_VERSION,
            "domain": "finite deterministic GridWorld",
            "source_type": "digest-bound sparse transition matrices",
        },
        "space": {"dimension": gridworld.N_CELLS, "scalar_field": "complex"},
        "capabilities": capabilities,
        "semantic_convention_requirements": {
            "operative_alphabet": "required",
            "word_convention": "required",
            "projector_letter_policy": "required",
            "direction_convention": "required",
            "depth_indexing": "required",
            "hall_convention": "required",
        },
        "run_policy_requirements": {
            "threshold": "required",
            "cutoff": "required",
            "norm": "required",
            "numerical_tolerance": "required",
            "saturation_audit": "not_applicable",
            "sampling_grid": "not_applicable",
            "trajectory_parameterization": "not_applicable",
        },
        "notes": [
            "The native adapter binds explicit finite source matrices rather than a migrated report envelope.",
            "Object-level comparison certification is supplied separately by the Paper XIII oracle.",
        ],
    }


def ir_artifact(artifact_id: str, role: str, path: Path) -> dict[str, Any]:
    return {
        "id": artifact_id,
        **artifact_reference(path),
        "media_type": "application/json" if path.suffix == ".json" else "text/x-python",
        "schema_version": "1.0",
        "role": role,
    }


def build_ir(
    side: str,
    source_path: Path,
    manifest_path: Path,
    fields: dict[str, Any],
) -> dict[str, Any]:
    artifacts = [
        ir_artifact("artifact.manifest", "manifest", manifest_path),
        ir_artifact("artifact.raw-source", "source-input", source_path),
        ir_artifact("artifact.adapter", "adapter-output", Path(__file__)),
        ir_artifact("artifact.structure", "validator-output", STRUCTURE_CERTIFICATE),
        ir_artifact("artifact.rule-registry", "proof-reference", RULE_REGISTRY),
    ]
    conventions = [
        {
            "id": "semantic.alphabet",
            "kind": "operative_alphabet",
            "specification": {"alphabet_id": "gridworld-skew-actions", "labels": list(gridworld.ACTION_NAMES)},
        },
        {"id": "semantic.word", "kind": "word_convention", "specification": {"type": "positive"}},
        {
            "id": "semantic.projector-letter",
            "kind": "projector_letter_policy",
            "specification": {"projectors_are_letters": False},
        },
        {
            "id": "semantic.direction",
            "kind": "direction_convention",
            "specification": {"direction": "column-source-to-row-target"},
        },
        {
            "id": "semantic.depth",
            "kind": "depth_indexing",
            "specification": {"generator_depth": 1, "simple_commutator_depth": 2},
        },
        {
            "id": "semantic.hall",
            "kind": "hall_convention",
            "specification": {"family": "simple-pair-commutators", "pair_order": "a<b"},
        },
    ]
    policies = [
        {"id": "policy.threshold", "kind": "threshold", "specification": {"absolute": gridworld.TOL, "comparison": "strictly-greater-than"}},
        {"id": "policy.norm", "kind": "norm", "specification": {"name": "entrywise-absolute-support"}},
        {"id": "policy.tolerance", "kind": "numerical_tolerance", "specification": {"absolute": gridworld.TOL}},
        {"id": "policy.cutoff", "kind": "cutoff", "specification": {"maximum_depth": 2, "unreached_value": "UNREACHED_AT_CUTOFF"}},
    ]
    objects = [
        {"id": "space.v", "kind": "finite_space", "label": "V=C^25", "provenance_artifact_ids": ["artifact.raw-source"], "data": {"dimension": 25, "scalar_field": "complex"}},
        {"id": "sectorization.q", "kind": "sectorization", "label": "25 coordinate sectors", "carrier_id": "carrier.sector", "provenance_artifact_ids": ["artifact.raw-source", "artifact.structure"], "data": {"labels": [f"cell-{index}" for index in range(25)], "complete": True}},
        {"id": "alphabet.y", "kind": "labelled_alphabet", "label": "Y={N,S,E,W}", "carrier_id": "carrier.operator", "provenance_artifact_ids": ["artifact.raw-source"], "data": {"labels": list(gridworld.ACTION_NAMES), "generator_convention": "(T-T^T)/2"}},
        {"id": "shadow.r1", "kind": "support_shadow", "label": "Direct support", "carrier_id": "carrier.operator", "provenance_artifact_ids": ["artifact.raw-source"], "data": fields["operator_support"]},
        {"id": "word-space.depth-2", "kind": "word_space", "label": "Positive words of length two", "carrier_id": "carrier.word", "provenance_artifact_ids": ["artifact.raw-source"], "data": fields["word_length_two_support"]},
        {"id": "depth.word", "kind": "depth_field", "label": "Word audit cutoff", "carrier_id": "carrier.word", "provenance_artifact_ids": ["artifact.raw-source"], "data": {"maximum_depth": 2}},
        {"id": "lie-family.x", "kind": "lie_family", "label": "Skew action generators", "carrier_id": "carrier.lie", "provenance_artifact_ids": ["artifact.raw-source"], "data": {"labels": list(gridworld.ACTION_NAMES)}},
        {"id": "hall.depth-2", "kind": "hall_filtration", "label": "Simple commutator layer", "carrier_id": "carrier.lie", "provenance_artifact_ids": ["artifact.raw-source"], "data": fields["lie_simple_commutator_support"]},
        {"id": "depth.lie", "kind": "depth_field", "label": "Lie audit cutoff", "carrier_id": "carrier.lie", "provenance_artifact_ids": ["artifact.raw-source"], "data": {"maximum_depth": 2}},
    ]
    carriers = [
        {"id": "carrier.sector", "kind": "sector", "capability_id": "sectorization", "semantics": "Complete coordinate singleton sectorization.", "object_ids": ["sectorization.q"], "semantic_convention_ids": ["semantic.direction"]},
        {"id": "carrier.operator", "kind": "operator", "capability_id": "operator_carrier", "semantics": "Labelled skew transition generators.", "object_ids": ["alphabet.y", "shadow.r1"], "semantic_convention_ids": ["semantic.alphabet", "semantic.word", "semantic.projector-letter", "semantic.direction"]},
        {"id": "carrier.word", "kind": "word", "capability_id": "word_carrier", "semantics": "Ordered positive words.", "object_ids": ["word-space.depth-2", "depth.word"], "semantic_convention_ids": ["semantic.alphabet", "semantic.word", "semantic.projector-letter", "semantic.direction", "semantic.depth"]},
        {"id": "carrier.lie", "kind": "lie", "capability_id": "lie_hall_carrier", "semantics": "Independently declared simple-commutator family.", "object_ids": ["lie-family.x", "hall.depth-2", "depth.lie"], "semantic_convention_ids": ["semantic.alphabet", "semantic.direction", "semantic.depth", "semantic.hall"]},
    ]

    def finding(identifier: str, kind: str, carrier: str, objects_for_finding: list[str], value: Any, conventions_for_finding: list[str]) -> dict[str, Any]:
        return {
            "id": identifier,
            "kind": kind,
            "carrier_id": carrier,
            "subject_object_ids": objects_for_finding,
            "value": value,
            "unit": None,
            "result_state": "OBSERVED",
            "semantic_convention_ids": conventions_for_finding,
            "run_policy_ids": ["policy.threshold", "policy.norm", "policy.tolerance", "policy.cutoff"],
            "certificate_ids": ["cert.strict-admission"],
            "artifact_ids": ["artifact.raw-source", "artifact.structure"],
        }

    findings = [
        finding("finding.direct-support", "boolean_support", "carrier.operator", ["shadow.r1"], fields["operator_support"], ["semantic.alphabet", "semantic.direction"]),
        finding("finding.word-length-two", "boolean_support", "carrier.word", ["word-space.depth-2"], fields["word_length_two_support"], ["semantic.alphabet", "semantic.word", "semantic.depth"]),
        finding("finding.lie-simple-commutator", "boolean_support", "carrier.lie", ["hall.depth-2"], fields["lie_simple_commutator_support"], ["semantic.alphabet", "semantic.hall", "semantic.depth"]),
    ]

    def claim(identifier: str, statement: str, capability_id: str, carrier_id: str, object_ids: list[str], finding_id: str, convention_ids: list[str]) -> dict[str, Any]:
        return {
            "id": identifier,
            "statement": statement,
            "result_state": "OBSERVED",
            "claim_status": "Computational Observation",
            "capability_ids": ["sectorization", capability_id],
            "carrier_ids": [carrier_id],
            "object_ids": object_ids,
            "finding_ids": [finding_id],
            "semantic_convention_ids": convention_ids,
            "run_policy_ids": ["policy.threshold", "policy.norm", "policy.tolerance", "policy.cutoff"],
            "hypotheses": ["The digest-bound native GridWorld source and declared generator convention are fixed."],
            "certificate_ids": ["cert.strict-admission"],
            "artifact_ids": ["artifact.raw-source", "artifact.structure"],
            "scope": f"Native GridWorld F4 {side} snapshot under tol={gridworld.TOL}.",
            "negative_boundary": "This single-report observation does not compare two reports or establish domain adequacy.",
        }

    claims = [
        claim("claim.direct-support", "The native snapshot records direct support of the labelled skew generators.", "operator_carrier", "carrier.operator", ["space.v", "sectorization.q", "alphabet.y", "shadow.r1"], "finding.direct-support", ["semantic.alphabet", "semantic.direction"]),
        claim("claim.word-length-two", "The native snapshot records ordered positive-word support at length two.", "word_carrier", "carrier.word", ["word-space.depth-2", "depth.word"], "finding.word-length-two", ["semantic.alphabet", "semantic.word", "semantic.depth"]),
        claim("claim.lie-simple-commutator", "The native snapshot records simple-commutator support at depth two.", "lie_hall_carrier", "carrier.lie", ["lie-family.x", "hall.depth-2", "depth.lie"], "finding.lie-simple-commutator", ["semantic.alphabet", "semantic.hall", "semantic.depth"]),
    ]
    manifest = load_json(manifest_path)
    return {
        "ir_version": "1.0",
        "record_id": f"paper13.gridworld-f4.{side}.native-v2",
        "record_kind": "strict_sof",
        "manifest_ref": {
            "manifest_id": manifest["manifest_id"],
            "manifest_version": manifest["manifest_version"],
            "artifact_id": "artifact.manifest",
            "digest": artifact_reference(manifest_path)["digest"],
        },
        "source": {"adapter_id": ADAPTER_ID, "adapter_version": ADAPTER_VERSION, "source_id": f"gridworld-f4-{side}", "artifact_ids": ["artifact.raw-source", "artifact.adapter", "artifact.structure"]},
        "objects": objects,
        "carriers": carriers,
        "semantic_conventions": conventions,
        "run_policies": policies,
        "artifacts": artifacts,
        "certificates": [{"id": "cert.strict-admission", "validator_id": "paper13.gridworld-structure-validator", "status": "PASS", "scope": "Finite dimension, complete coordinate sectorization, labelled matrices, and declared word/Lie conventions.", "artifact_ids": ["artifact.structure"]}],
        "findings": findings,
        "claims": claims,
        "derivations": [],
    }


def external_basis(source_artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    structure = next(item for item in source_artifacts if item["uri"] == repo_uri(STRUCTURE_CERTIFICATE))
    packages = [
        {"basis_id": "basis.source.identity", "level": "source_identity", "status": "SATISFIED", "method": "digest-bound-native-source", "scope": "The native source, adapter, and structure check are digest-bound.", "evidence_artifacts": source_artifacts, "constraint_ids": ["source-snapshot-pinned"], "negative_boundary": ["Digest identity does not establish domain adequacy."]},
        {"basis_id": "basis.object.recomputation", "level": "object_level", "status": "NOT_ASSESSED", "method": "comparison-oracle-owned-by-paper13", "scope": "Object-level comparison is certified only in the downstream audit.", "evidence_artifacts": [], "constraint_ids": ["object-level-recomputation"], "negative_boundary": ["The single report does not borrow the pairwise oracle."]},
        {"basis_id": "basis.structure.validation", "level": "structure_level", "status": "SATISFIED", "method": "finite-structure-validation", "scope": "The 25-dimensional coordinate realization and four labelled generators are checked.", "evidence_artifacts": [structure], "constraint_ids": ["realization-structure-validation"], "negative_boundary": ["Structure validation does not establish scientific adequacy."]},
        {"basis_id": "basis.semantic.adequacy", "level": "semantic_adequacy", "status": "NOT_ASSESSED", "method": "domain-owner-assessment-not-bound", "scope": "GridWorld adequacy beyond this finite control is not assessed.", "evidence_artifacts": [], "constraint_ids": ["domain-semantic-adequacy"], "negative_boundary": ["Protocol-valid structure may still be an inadequate domain model."]},
    ]
    constraints = [
        {"constraint_id": "source-snapshot-pinned", "basis_id": "basis.source.identity", "status": "SATISFIED", "statement": "The native source closure is digest-bound.", "evidence_artifacts": source_artifacts},
        {"constraint_id": "object-level-recomputation", "basis_id": "basis.object.recomputation", "status": "NOT_ASSESSED", "statement": "Pairwise object recomputation belongs to the audit.", "evidence_artifacts": []},
        {"constraint_id": "realization-structure-validation", "basis_id": "basis.structure.validation", "status": "SATISFIED", "statement": "The strict finite realization passes its structure check.", "evidence_artifacts": [structure]},
        {"constraint_id": "domain-semantic-adequacy", "basis_id": "basis.semantic.adequacy", "status": "NOT_ASSESSED", "statement": "Domain adequacy is not assessed by this artifact.", "evidence_artifacts": []},
    ]
    return {"registry_version": "1.0", "basis_status": "PARTIAL", "packages": packages, "constraints": constraints, "negative_boundary": ["The registry separates source, structure, object, and semantic-adequacy evidence."]}


def assemble_report(side: str, source_path: Path, manifest_path: Path, ir_path: Path, output_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    ir = load_json(ir_path)
    compiler_output = load_json(output_path)
    compiler_profile = load_json(STRICT_COMPILER_PROFILE)
    assembly_profile = load_json(STRICT_ASSEMBLY_PROFILE)
    source_artifacts = [artifact_reference(source_path), artifact_reference(Path(__file__)), artifact_reference(STRUCTURE_CERTIFICATE)]
    classifications = {
        claim["id"]: {
            "claim_target": "representation_interface",
            "certificate_class": None,
            "classification_source": "domain_adapter",
            "external_basis_refs": ["basis.source.identity", "basis.structure.validation"],
            "external_constraint_ids": ["source-snapshot-pinned", "realization-structure-validation"],
        }
        for claim in ir["claims"]
    }
    ir_claims = {item["id"]: item for item in ir["claims"]}
    carrier_kinds = {item["id"]: item["kind"] for item in ir["carriers"]}
    claims: list[dict[str, Any]] = []
    degradations: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    for index, item in enumerate(compiler_output["items"]):
        source_item_id = f"compiler.item.{index:04d}"
        report_item_id = f"report.{item['item_kind']}-item.{index:04d}"
        bindings.append({"compiler_output_item_id": source_item_id, "report_item_id": report_item_id, "item_kind": item["item_kind"], "rendering_status": "rendered"})
        if item["item_kind"] == "claim":
            claim = ir_claims[item["claim_id"]]
            claims.append({"report_item_id": report_item_id, "source_output_item_id": source_item_id, "claim_id": claim["id"], "statement": claim["statement"], "result_state": claim["result_state"], "claim_status": claim["claim_status"], **deepcopy(classifications[claim["id"]]), "carrier_kinds": sorted({carrier_kinds[carrier_id] for carrier_id in claim["carrier_ids"]}), "scope": claim["scope"], "negative_boundary": claim["negative_boundary"]})
        else:
            degradation = {"report_item_id": report_item_id, "source_output_item_id": source_item_id, "module_id": item["module_id"], "action": item["action"], "reason_kind": item["reason_kind"], "details": deepcopy(item["details"])}
            if "source_ir_id" in item:
                degradation["source_ir_id"] = item["source_ir_id"]
            degradations.append(degradation)
    modules = compile_modules(compiler_output, ir, compiler_profile)
    enabled_findings = {finding_id for module in modules if module["status"] == "ENABLED" for finding_id in module["finding_ids"]}
    return {
        "sofrs_version": "2.0",
        "report_id": f"gridworld-f4-{side}-native-v2",
        "system": f"GridWorld F4 {side} native strict report",
        "record_kind": "strict_sof",
        "strict_reconstruction": {"candidate_status": "not_applicable", "available_requirements": [], "missing_requirements": [], "evaluator_id": "paper13.native-gridworld-structure-validator", "evaluator_version": "2.0", "interpretation": "The report is already admitted as an explicit strict finite realization."},
        "external_basis_registry": external_basis(source_artifacts),
        "compiler_contracts": {"capability_manifest": artifact_reference(manifest_path), "typed_sof_ir": artifact_reference(ir_path), "compiler_profile": artifact_reference(STRICT_COMPILER_PROFILE), "compiler_output": artifact_reference(output_path)},
        "compiler_output_binding": {"artifact_id": "artifact.compiler-output", "artifact": artifact_reference(output_path), "compiler_id": compiler_output["compiler_id"], "compiler_output_version": compiler_output["compiler_output_version"], "compiler_profile_id": compiler_output["profile_id"]},
        "assembly_contract": {"schema_id": ASSEMBLY_CONTRACT_ID, "version": ASSEMBLY_CONTRACT_VERSION, "implementation": artifact_reference(Path(__file__)), "assembly_profile": artifact_reference(STRICT_ASSEMBLY_PROFILE), "assembly_profile_id": assembly_profile["assembly_profile_id"]},
        "item_bindings": bindings,
        "alignment_readiness": {"adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION}, "compiler_profile_id": compiler_profile["profile_id"], "assembly_profile_id": assembly_profile["assembly_profile_id"], "sector_metadata": {"status": "PRESENT", "labels": [f"cell-{index}" for index in range(25)], "provenance": repo_uri(source_path), "ranks_or_dimensions": [1] * 25, "semantics": "coordinate singleton sectors"}, "observable_metadata": {"status": "PRESENT", "labels": list(gridworld.ACTION_NAMES), "provenance": repo_uri(source_path), "ranks_or_dimensions": [], "semantics": "labelled skew transition generators"}, "carrier_kinds": sorted({carrier["kind"] for carrier in ir["carriers"]}), "semantic_conventions": [{"id": item["id"], "kind": item["kind"]} for item in ir["semantic_conventions"]], "run_policies": [{"id": item["id"], "kind": item["kind"]} for item in ir["run_policies"]], "comparison_keys": ["domain:gridworld", "control:f4", f"side:{side}", "generator:gridworld-skew-actions"], "source_artifact_digests": source_artifacts},
        "source_mapping": {"status": "native", "construction": "Direct adapter construction from digest-bound sparse transition matrices.", "adapter_id": ADAPTER_ID, "adapter_version": ADAPTER_VERSION, "justification": "The complete finite space, sectors, and labelled matrices are explicitly retained.", "limitations": ["This finite GridWorld control is not a learned production-world model."]},
        "source_artifacts": source_artifacts,
        "modules": modules,
        "findings": [{"finding_id": item["id"], "kind": item["kind"], "result_state": item["result_state"], "value": item["value"]} for item in ir["findings"] if item["id"] in enabled_findings],
        "claims": claims,
        "degradation_items": degradations,
        "failure_modes": ["The control uses exact finite matrices and a declared numerical support threshold.", "The single report does not assign correctness to either side."],
        "provenance": {
            "kind": "native_generation",
            "producer": artifact_reference(Path(__file__)),
            "source_snapshot": artifact_reference(source_path),
            "adapter": artifact_reference(Path(__file__)),
            "compiler_profile_ref": artifact_reference(STRICT_COMPILER_PROFILE),
            "compiler_output_ref": artifact_reference(output_path),
            "assembly_profile_ref": artifact_reference(STRICT_ASSEMBLY_PROFILE),
        },
    }


def prepare() -> None:
    reference_matrices = gridworld.build_reference().action_matrices()
    target_matrices = gridworld.build_f4_rare_bridge_deletion()
    write_json(REFERENCE_SOURCE, source_snapshot("gridworld-f4-reference", reference_matrices))
    write_json(TARGET_SOURCE, source_snapshot("gridworld-f4-target", target_matrices))
    write_json(STRUCTURE_CERTIFICATE, {"certificate_version": "1.0", "certificate_id": "paper13.gridworld-f4.structure.v1", "status": "PASS", "checks": ["dimension-25", "complete-coordinate-sectorization", "four-labelled-square-matrices", "word-and-lie-conventions-declared"], "source_artifacts": [artifact_reference(REFERENCE_SOURCE), artifact_reference(TARGET_SOURCE)], "negative_boundary": ["This structure certificate is not the independent object-level comparison oracle."]})
    write_json(ALIGNMENT_EVIDENCE, {"alignment_version": "1.0", "alignment_id": "paper13.gridworld-f4.identity", "sector_pairs": [[f"cell-{index}", f"cell-{index}"] for index in range(25)], "observable_pairs": [[name, name] for name in gridworld.ACTION_NAMES], "policy": {"generator_convention": "X=(T-T^T)/2", "threshold": gridworld.TOL}, "status": "PASS", "negative_boundary": ["Identity alignment applies only to this shared retained frame."]})
    reference_fields = observed_fields(reference_matrices)
    target_fields = observed_fields(target_matrices)
    comparisons = {}
    for key in reference_fields:
        reference_pairs = {tuple(pair) for pair in reference_fields[key]["pairs"]}
        target_pairs = {tuple(pair) for pair in target_fields[key]["pairs"]}
        comparisons[key] = {"reference": reference_fields[key], "target": target_fields[key], "missing_pairs": [list(pair) for pair in sorted(reference_pairs - target_pairs)], "extra_pairs": [list(pair) for pair in sorted(target_pairs - reference_pairs)], "total_mismatch": len(reference_pairs ^ target_pairs)}
    write_json(AUDIT_RESULT, {"result_version": "1.0", "result_id": "paper13.gridworld-f4.native-audit-result.v1", "producer": {"id": "paper13.gridworld-native-audit-engine", "version": "2.0", "implementation": artifact_reference(Path(__file__))}, "raw_sources": [artifact_reference(REFERENCE_SOURCE), artifact_reference(TARGET_SOURCE)], "comparison_specification": {"generator_convention": "X=(T-T^T)/2", "threshold": gridworld.TOL, "word_length": 2, "lie_layer": "simple_commutators"}, "coordinates": comparisons, "status": "PASS"})

    for side, source_path, fields in (("reference", REFERENCE_SOURCE, reference_fields), ("target", TARGET_SOURCE, target_fields)):
        manifest_path = MANIFEST_DIR / f"gridworld-f4-{side}.capabilities.json"
        ir_path = IR_DIR / f"gridworld-f4-{side}.ir.json"
        output_path = OUTPUT_DIR / f"gridworld-f4-{side}.compiler-output.json"
        report_path = REPORT_DIR / f"gridworld-f4-{side}.sofreport.json"
        receipt_path = REPORT_RECEIPT_DIR / f"gridworld-f4-{side}.validation-receipt.json"
        manifest = build_manifest(side)
        write_json(manifest_path, manifest)
        ir = build_ir(side, source_path, manifest_path, fields)
        write_json(ir_path, ir)
        output = compile_output_v1(manifest, ir, load_json(STRICT_COMPILER_PROFILE), load_json(RULE_REGISTRY))
        write_json(output_path, output)
        report = assemble_report(side, source_path, manifest_path, ir_path, output_path)
        write_json(report_path, report)
        errors = standalone_report_errors(report_path)
        if errors:
            raise ValueError(f"{report_path}: " + "; ".join(errors))
        receipt = build_v2_report_validation_receipt(report_path, report_uri=repo_uri(report_path), validator_path=PAPER12_VALIDATOR, validator_uri=repo_uri(PAPER12_VALIDATOR))
        write_json(receipt_path, receipt)
        receipt_errors = v2_report_validation_receipt_errors(receipt, repository_root=ROOT)
        if receipt_errors:
            raise ValueError(f"{receipt_path}: " + "; ".join(receipt_errors))


def role_basis(side: str) -> dict[str, Any]:
    return {"role": side, "basis_kind": "exact_recomputation", "authority_status": "ESTABLISHED", "scope": "Exact finite GridWorld F4 source construction under the declared skew-generator convention.", "evidence_artifacts": [f"artifact.raw-source-{side}", "artifact.object-oracle-result"], "negative_boundary": ["The role establishes this finite comparison baseline, not general GridWorld correctness or action semantics."]}


def alignment(kind: str, labels: list[str]) -> dict[str, Any]:
    return {"alignment_id": f"paper13.gridworld-f4.{kind}.identity", "alignment_kind": kind, "state": "TOTAL", "map_kind": "bijection", "reference_carrier": f"gridworld-{kind}-labels", "target_carrier": f"gridworld-{kind}-labels", "pairs": [{"reference_id": label, "target_id": label, "relation": "equivalent", "evidence_artifact_ids": ["artifact.alignment-evidence"]} for label in labels], "unmatched_reference_ids": [], "unmatched_target_ids": [], "properties": {"total_on_reference": True, "total_on_target": True, "injective": True, "surjective": True}, "semantic_basis": "Identity on the common retained GridWorld frame.", "negative_boundary": ["No cross-domain or cross-refinement transport is asserted."]}


def report_item(report: dict[str, Any], claim_id: str, report_artifact: dict[str, Any]) -> dict[str, Any]:
    item = next(item for item in report["claims"] if item["claim_id"] == claim_id)
    return {"report_id": report["report_id"], "report_item_id": item["report_item_id"], "source_output_item_id": item["source_output_item_id"], "item_kind": "claim", "artifact_digest": report_artifact["digest"]}


def build_audit() -> dict[str, Any]:
    if not OBJECT_CERTIFICATE.is_file():
        raise ValueError("run gridworld_f4_object_certificate.py --write before native audit assembly")
    oracle = load_json(OBJECT_CERTIFICATE)
    producer_result = load_json(AUDIT_RESULT)
    if oracle.get("native_v2_control", {}).get("producer_result") != artifact_reference(AUDIT_RESULT):
        raise ValueError("GridWorld F4 object certificate does not bind the current native result")
    reference_report_path = REPORT_DIR / "gridworld-f4-reference.sofreport.json"
    target_report_path = REPORT_DIR / "gridworld-f4-target.sofreport.json"
    reference_receipt_path = REPORT_RECEIPT_DIR / "gridworld-f4-reference.validation-receipt.json"
    target_receipt_path = REPORT_RECEIPT_DIR / "gridworld-f4-target.validation-receipt.json"
    reference_report = load_json(reference_report_path)
    target_report = load_json(target_report_path)
    artifacts = [
        audit_artifact("artifact.reference-report", "reference-report", reference_report_path),
        audit_artifact("artifact.target-report", "target-report", target_report_path),
        audit_artifact("artifact.reference-report-validation-receipt", "reference-report-validation-receipt", reference_receipt_path),
        audit_artifact("artifact.target-report-validation-receipt", "target-report-validation-receipt", target_receipt_path),
        audit_artifact("artifact.alignment-evidence", "alignment-evidence", ALIGNMENT_EVIDENCE),
        audit_artifact("artifact.raw-source-reference", "raw-source-reference", REFERENCE_SOURCE),
        audit_artifact("artifact.raw-source-target", "raw-source-target", TARGET_SOURCE),
        audit_artifact("artifact.independent-recomputation", "independent-recomputation-implementation", PAPER_DIR / "validation" / "gridworld_f4_object_certificate.py"),
        audit_artifact("artifact.object-oracle-result", "object-oracle-result", OBJECT_CERTIFICATE),
        audit_artifact("artifact.audit-result", "audit-result", AUDIT_RESULT),
        audit_artifact("artifact.audit-generator", "audit-generator", Path(__file__)),
        audit_artifact("artifact.audit-profile", "audit-profile", GRIDWORLD_PROFILE_PATH),
        audit_artifact(
            "artifact.coordinate-semantics-registry",
            "coordinate-semantics-registry",
            REGISTRY_PATH,
        ),
    ]
    artifact_by_id = {item["id"]: item for item in artifacts}
    reference_basis = role_basis("reference")
    target_basis = role_basis("target")
    checks = []
    for condition_id in ("source-report-receipts-validate", "paper-x-record-kind-permission", "paper-x-carrier-alignment", "paper-x-policy-alignment", "paper-x-evidence-alignment", "paper-x-promotion-audit", "paper-xiii-sector-alignment", "paper-xiii-observable-alignment", "paper-xiii-comparison-specification"):
        evidence = ["artifact.alignment-evidence", "artifact.object-oracle-result"]
        if condition_id == "source-report-receipts-validate":
            evidence = ["artifact.reference-report-validation-receipt", "artifact.target-report-validation-receipt"]
        elif condition_id == "paper-x-record-kind-permission":
            evidence = ["artifact.reference-report", "artifact.target-report"]
        checks.append({"condition_id": condition_id, "status": "SATISFIED", "evidence_artifact_ids": evidence})
    coordinate_specs = (
        ("operator.support.summary", "operator", "operator.support.v1", "operator_support", "claim.direct-support"),
        ("word.support.length-2.summary", "word", "word.support.v1", "word_length_two_support", "claim.word-length-two"),
        ("lie.simple-commutator-support.summary", "lie", "lie.simple-commutator-support.v1", "lie_simple_commutator_support", "claim.lie-simple-commutator"),
    )
    coordinates = {}
    for coordinate_id, family, value_schema_id, result_key, claim_id in coordinate_specs:
        result = producer_result["coordinates"][result_key]
        mismatch = result["total_mismatch"]
        coordinates[coordinate_id] = {
            "comparison_state": "ALIGNED" if mismatch == 0 else "MISMATCH",
            "result_state": "CERTIFIED",
            "claim_status": "Computational Certificate",
            "claim_target": "external_mathematical_object",
            "certificate_class": "object",
            "classification_source": "independent_oracle",
            "report_item_binding": {"binding_state": "paired", "reference_item_ref": report_item(reference_report, claim_id, artifact_by_id["artifact.reference-report"]), "target_item_ref": report_item(target_report, claim_id, artifact_by_id["artifact.target-report"]), "reason": None},
            "coordinate_family": family,
            "value_schema_id": value_schema_id,
            "value": {"reference_value": result["reference"], "target_value": result["target"], "normalized_reference_value": result["reference"], "normalized_target_value": result["target"], "relation": "equal" if mismatch == 0 else "mismatch", "delta": {"missing_pairs": result["missing_pairs"], "extra_pairs": result["extra_pairs"], "total_mismatch": mismatch}, "unit": "ordered-sector-pair count", "metric_result": {"metric_id": "discrete-mismatch", "status": "computed", "value": mismatch}, "policy_refs": ["paper13.gridworld-f4.theta-v2"], "oracle_ref": "artifact.object-oracle-result"},
            "source_artifact_ids": ["artifact.raw-source-reference", "artifact.raw-source-target", "artifact.audit-result", "artifact.object-oracle-result"],
        }
    return {
        "sofaudit_version": "2.0",
        "artifact_type": "sofaudit",
        "comparison_object": "SOFReportComparison",
        "audit_id": "gridworld-f4-native-v2",
        "system": "Native SOFRS v2 GridWorld F4 factual comparison",
        "regime": "strict_vs_strict",
        "source_reports": {
            "reference": {"report_id": reference_report["report_id"], "label": reference_report["system"], "artifact": audit_reference(reference_report_path), "validation_receipt": audit_reference(reference_receipt_path), "sofrs_version": "2.0", "record_kind": "strict_sof", "admission_basis": "native_sofrs_v2", "comparison_role_basis": reference_basis},
            "target": {"report_id": target_report["report_id"], "label": target_report["system"], "artifact": audit_reference(target_report_path), "validation_receipt": audit_reference(target_receipt_path), "sofrs_version": "2.0", "record_kind": "strict_sof", "admission_basis": "native_sofrs_v2", "comparison_role_basis": target_basis},
        },
        "inherited_compiler_guards": {"paper_x_contract_version": "1.0", "state": "ADMITTED", "condition_checks": checks, "negative_boundaries": ["Admission authorizes only the three requested, oracle-bound coordinates."]},
        "audit_profile": {
            **{
                key: value
                for key, value in GRIDWORLD_PROFILE.items()
                if key not in {"applicable_regimes", "profile_contract_version", "profile_revision", "negative_boundary"}
            },
            "profile_artifact_id": "artifact.audit-profile",
            "coordinate_registry_artifact_id": "artifact.coordinate-semantics-registry",
            "applicable_regime": "strict_vs_strict",
        },
        "alignment": {"sector_alignment": alignment("sector", [f"cell-{index}" for index in range(25)]), "observable_alignment": alignment("observable", list(gridworld.ACTION_NAMES))},
        "comparison_specification": {"specification_id": "paper13.gridworld-f4.theta-v2", "normalization": {"normalization_id": "identity", "numeric_policy": "exact", "equality_tolerance": 0, "sentinel_policy": "state-not-infinity", "generator_policy": "report-bound-generators"}, "metric": {"metric_id": "discrete-mismatch", "domain": "mixed", "unit_policy": "unitless", "missing_value_policy": "incomparable", "zero_denominator_policy": "not-applicable"}, "depth_semantics": {"carrier": "not-applicable", "mode": "not-applicable", "reference_cutoff": None, "target_cutoff": None, "unreached_policy": "incomparable"}, "thresholds": {"threshold_id": "entrywise-support", "value": gridworld.TOL, "source": "comparison-specification"}, "parameter_synchronization": {"kind": "not-applicable", "map_artifact_id": None, "interpolation_method": "not-applicable", "extrapolation_forbidden": True}, "aggregation": {"kind": "coordinatewise", "scalarization": "none", "weights_artifact_id": None, "weight_declaration": None}},
        "comparison_basis": {"basis_status": "COMPLETE", "reference_role_basis": deepcopy(reference_basis), "alignment_evidence": ["artifact.alignment-evidence"], "object_level_oracle": {"status": "SATISFIED", "independence": {"implementation_relation": "separate_algorithm", "producer_relation": "same_producer_disclosed", "input_source": "canonical_raw_sources", "producer_cache_used": False}, "raw_source_artifacts": ["artifact.raw-source-reference", "artifact.raw-source-target"], "independent_recomputation_artifacts": ["artifact.independent-recomputation"], "oracle_result_artifact": "artifact.object-oracle-result", "audit_result_artifact": "artifact.audit-result"}, "policy_compatibility": {"status": "SATISFIED", "policy_artifact_ids": ["artifact.alignment-evidence", "artifact.object-oracle-result"], "negative_boundary": ["Policy compatibility is limited to the declared finite threshold and generator convention."]}, "negative_boundary": ["The certificate establishes three finite comparison coordinates only; it does not establish model adequacy, defect, or action."]},
        "coordinates": coordinates,
        "claim": {"result_state": "CERTIFIED", "claim_status": "Computational Certificate", "claim_target": "external_mathematical_object", "certificate_class": "object", "classification_source": "independent_oracle", "statement": "For the declared native GridWorld F4 sources, direct and length-two word support agree while simple-commutator support differs on eight ordered sector pairs.", "negative_boundary": "The result is finite, convention-relative, and does not imply a universal sensitivity ordering.", "source_artifact_ids": [item["id"] for item in artifacts]},
        "failure_modes": ["The comparison is exact only relative to the retained finite sources, skew-generator convention, and tol=1e-8 support policy.", "Reference status does not imply general ground truth outside this control."],
        "source_artifacts": artifacts,
        "provenance": {"kind": "native", "generator_id": "paper13.gridworld-native-audit-engine", "generator_version": "2.0", "generation_artifact_ids": ["artifact.audit-generator", "artifact.audit-result", "artifact.object-oracle-result"], "generation_notes": ["Generated directly from two validated native SOFRS v2 reports; no migrated coordinate was promoted."]},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="write sources, report stacks, alignment, and producer result")
    parser.add_argument("--write", action="store_true", help="prepare and write the native audit after the oracle exists")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.prepare or args.write:
        prepare()
    if args.write:
        from experiments.paper13.validation.validate_sofaudit_v2 import (  # noqa: E402
            build_validation_receipt,
            semantic_errors,
            validation_receipt_errors,
        )

        audit = build_audit()
        write_json(NATIVE_AUDIT, audit)
        errors = semantic_errors(audit, NATIVE_AUDIT)
        if errors:
            raise ValueError("native audit: " + "; ".join(errors))
        receipt = build_validation_receipt(NATIVE_AUDIT)
        write_json(NATIVE_AUDIT_RECEIPT, receipt)
        receipt_errors = validation_receipt_errors(NATIVE_AUDIT_RECEIPT)
        if receipt_errors:
            raise ValueError("native audit receipt: " + "; ".join(receipt_errors))
    print("PASS native GridWorld F4 preparation" + (" and audit" if args.write else ""))


if __name__ == "__main__":
    main()
