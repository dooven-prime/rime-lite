"""Migrate the nine frozen SOFRS v1.0 reports into the SOFRS v2.0 stack.

The v1.0 artifacts remain immutable. Each migration emits:

* one Capability Manifest;
* one Typed SOF IR record;
* one Paper X CompilerOutput artifact;
* one capability-gated SOFRS v2.0 report.

Aggregate reports whose ambient space or sector schema changes are admitted as
diagnostic analogues. Their pointwise constituents may be migrated separately
in a future adapter, but the aggregate record is not promoted to a fixed typed
deformation chart.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.sofcompiler.api import compile_output_v1  # noqa: E402


V1_DIR = PAPER_DIR / "archive" / "results"
V2_DIR = PAPER_DIR / "results"
MANIFEST_DIR = V2_DIR / "manifests"
IR_DIR = V2_DIR / "ir"
COMPILER_OUTPUT_DIR = V2_DIR / "compiler-output"
REPORT_DIR = V2_DIR / "reports"

STRICT_COMPILER_PROFILE = (
    ROOT / "schemas" / "sofrs" / "paper12-strict-compiler-profile-v1.0.json"
)
ANALOGUE_COMPILER_PROFILE = (
    ROOT / "schemas" / "sofrs" / "paper12-analogue-compiler-profile-v1.0.json"
)
STRICT_ASSEMBLY_PROFILE = (
    ROOT / "schemas" / "sofrs" / "paper12-strict-assembly-profile-v2.0.json"
)
ANALOGUE_ASSEMBLY_PROFILE = (
    ROOT / "schemas" / "sofrs" / "paper12-analogue-assembly-profile-v2.0.json"
)
RULE_REGISTRY_PATH = ROOT / "schemas" / "sofcompiler" / "rule-registry-v1.0.json"
ADAPTER_ID = "paper12-v1-to-v2"
ADAPTER_VERSION = "2.0"
MIGRATION_RECEIPT_PATH = ROOT / "schemas" / "sofrs" / "migration-receipt-v2.0.json"
ASSEMBLY_CONTRACT_ID = "sofrs-assembly-v2.0"
ASSEMBLY_CONTRACT_VERSION = "2.0"
UNREACHED = "UNREACHED_AT_CUTOFF"


CLASSIFICATIONS: dict[str, dict[str, Any]] = {
    "qwen": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": True,
        "dimension": 40,
        "domain": "pretrained transformer attention",
        "source_type": "revision-pinned attention matrices",
        "producer": "qwen_attention_sof.py",
        "labels_from": "qwen",
        "word": False,
        "proxy": True,
        "cutoff": 3,
        "reason": (
            "The frozen v1 envelope identifies a 40-dimensional retained token "
            "space inside the 45-token probe and a candidate complete coordinate "
            "partition on that retained space, but it does not bind the fourteen "
            "operative matrices or projector-completeness certificate as explicit "
            "artifacts. The migration therefore retains a bounded reconstruction "
            "obligation as an analogue record."
        ),
        "negative_boundary": (
            "Strict admission requires a new source-addressed reconstruction of "
            "the complete (V,Q,Y) data. The general attention matrices are also "
            "not a declared skew-Hermitian Lie family."
        ),
    },
    "transformer": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": True,
        "dimension": 8,
        "domain": "synthetic transformer activation",
        "source_type": "finite token-space matrices",
        "producer": "transformer_activation_sof.py",
        "labels_from": "labels",
        "word": False,
        "proxy": True,
        "cutoff": 2,
        "reason": (
            "The frozen v1 envelope records finite token groups and derived "
            "shadows, but it does not bind the two operative matrices as an "
            "explicit reconstruction artifact."
        ),
        "negative_boundary": (
            "Strict admission requires a new source-addressed reconstruction of "
            "the complete (V,Q,Y) data. No independently declared "
            "skew-Hermitian family or Hall convention is present."
        ),
    },
    "moe": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": True,
        "dimension": 32,
        "domain": "synthetic mixture-of-experts routing",
        "source_type": "finite routing-overlap matrix",
        "producer": "moe_expert_sof.py",
        "labels_from": "labels",
        "word": True,
        "proxy": False,
        "cutoff": 3,
        "reason": (
            "The frozen v1 envelope records route classes and positive-word "
            "shadows, but it does not bind the routing-overlap operator as an "
            "explicit reconstruction artifact."
        ),
        "negative_boundary": (
            "Strict admission requires a new source-addressed reconstruction of "
            "the complete (V,Q,Y) data. The retained depth descriptor is "
            "positive-word rather than Lie/Hall depth."
        ),
    },
    "recommender": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": True,
        "dimension": 140,
        "domain": "synthetic recommender coverage",
        "source_type": "finite bipartite interaction matrices",
        "producer": "recommender_sof.py",
        "labels_from": "labels",
        "word": True,
        "proxy": True,
        "cutoff": 8,
        "reason": (
            "The frozen v1 envelope records user/item clusters and derived "
            "coverage shadows, but it does not bind the before/after operative "
            "matrices as explicit reconstruction artifacts."
        ),
        "negative_boundary": (
            "Strict admission requires a new source-addressed reconstruction of "
            "the complete (V,Q,Y) data. Cutoff reachability and the discrete "
            "intervention comparison are not a continuous wall or causal result."
        ),
    },
    "transformer_batch": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "domain": "cross-configuration transformer robustness",
        "source_type": "aggregate sweep over changing ambient dimensions",
        "producer": "transformer_batch_sweep.py",
        "cutoff": 4,
        "reason": (
            "The v1 report aggregates 240-, 300-, and 360-dimensional "
            "realizations. The aggregate is not one fixed finite (V,Q,Y)."
        ),
        "negative_boundary": (
            "Each configuration may be separately admitted as a strict "
            "Lie/Hall realization after declaring its Hall convention; the "
            "aggregate sweep is not itself a strict SOF object."
        ),
    },
    "diffusion": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "domain": "diffusion-time probe",
        "source_type": "trajectory with changing PCA-sign sector schema",
        "producer": "diffusion_denoising_sof.py",
        "reason": (
            "The report aggregates pointwise finite audits while the sector "
            "count and projector family change along the sampled path."
        ),
        "negative_boundary": (
            "Pointwise strict snapshots do not produce a typed deformation "
            "chart without fixed labels, comparison maps, and continuity data."
        ),
    },
    "maze": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "domain": "dynamic graph connectivity",
        "source_type": "component trajectory with changing sector count",
        "producer": "maze_wall_crossing.py",
        "reason": (
            "Connected-component sectors change from one to twenty-five and "
            "back; the aggregate report is a schema-transition diagnostic."
        ),
        "negative_boundary": (
            "Connectivity splits and merges are not fixed-sector word or Lie "
            "repair, and pointwise graph partitions do not create one typed chart."
        ),
    },
    "moe_bias_repair": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "domain": "mixture-of-experts routing control",
        "source_type": "expert-load and routing-bias trajectory",
        "producer": "moe_bias_repair_sof.py",
        "reason": (
            "The report declares expert-load, bias, and activation descriptors "
            "without an explicit complete projector realization and alphabet."
        ),
        "negative_boundary": (
            "Frozen-to-routed expert activation is a routing-control analogue, "
            "not an SOF word, Lie-depth, or theorem instance."
        ),
    },
    "nvidia_llama31_8b_20260711": {
        "record_kind": "diagnostic_analogue",
        "enumerable_reconstruction_obligations": False,
        "domain": "API-only language-model evaluation",
        "source_type": "behavioral prompt and evaluator records",
        "producer": "blackbox_llm_sof.py",
        "reason": (
            "Prompt protocols and task classes are probe descriptors, not "
            "orthogonal projectors on a declared finite complex space."
        ),
        "negative_boundary": (
            "Behavioral support, bridge, and repair descriptors do not "
            "reconstruct hidden operators or instantiate an SOF theorem."
        ),
    },
}


def reconstruction_assessment(
    classification: dict[str, Any],
) -> dict[str, Any]:
    if classification["record_kind"] == "strict_sof":
        return {
            "candidate_status": "not_applicable",
            "available_requirements": [],
            "missing_requirements": [],
            "evaluator_id": "paper12.strict-reconstruction-obligation-audit",
            "evaluator_version": "1.0",
            "interpretation": (
                "A strict report is already admitted as a strict realization; "
                "the reconstruction-candidate predicate is not applicable."
            ),
        }
    if classification["enumerable_reconstruction_obligations"]:
        return {
            "candidate_status": "yes",
            "available_requirements": [
                "finite_space_dimension",
                "candidate_complete_partition",
                "operator_family_descriptor",
            ],
            "missing_requirements": [
                "explicit_operator_artifacts",
                "projector_completeness_certificate",
                "operator_artifact_source_digest_binding",
            ],
            "evaluator_id": "paper12.strict-reconstruction-obligation-audit",
            "evaluator_version": "1.0",
            "interpretation": (
                "The missing strict-admission obligations are explicitly "
                "enumerated; candidate status does not predict successful "
                "strict reconstruction."
            ),
        }
    return {
        "candidate_status": "no",
        "available_requirements": [],
        "missing_requirements": [
            "bounded_strict_reconstruction_obligation_not_declared"
        ],
        "evaluator_id": "paper12.strict-reconstruction-obligation-audit",
        "evaluator_version": "1.0",
        "interpretation": (
            "No bounded strict-reconstruction obligation is declared for this "
            "migration row."
        ),
    }


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9.-]+", "-", value.lower()).strip("-.")
    if not result:
        raise ValueError(f"cannot derive an ID from {value!r}")
    return result


def repo_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": repo_uri(path),
        "digest": {"algorithm": "sha256", "value": sha256(path)},
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def replace_unreached(value: Any) -> tuple[Any, int]:
    if isinstance(value, bool):
        return value, 0
    if isinstance(value, int) and value == 999:
        return UNREACHED, 1
    if isinstance(value, list):
        converted = []
        count = 0
        for item in value:
            new_item, item_count = replace_unreached(item)
            converted.append(new_item)
            count += item_count
        return converted, count
    if isinstance(value, dict):
        converted_dict = {}
        count = 0
        for key, item in value.items():
            new_item, item_count = replace_unreached(item)
            converted_dict[key] = new_item
            count += item_count
        return converted_dict, count
    return value, 0


def normalize_semantic_labels(
    name: str,
    bridge: Any,
    repair: Any,
    wall: Any,
) -> tuple[Any, Any, Any, list[str]]:
    bridge = deepcopy(bridge)
    repair = deepcopy(repair)
    wall = deepcopy(wall)
    notes: list[str] = []

    if name in {"qwen", "transformer"}:
        if isinstance(bridge, dict):
            bridge["kind"] = "general matrix-commutator support proxy"
        if isinstance(repair, dict):
            repair["kind"] = "cutoff general matrix-commutator depth proxy"
            repair["claim_note"] = (
                "The operative matrices are not a declared skew-Hermitian "
                "Lie family; this is not Lie/Hall depth."
            )
        notes.append("legacy Lie-depth label -> general matrix-commutator proxy")
    elif name == "transformer_batch":
        if isinstance(bridge, dict):
            bridge["kind"] = "cross-configuration matrix-commutator support proxy"
        if isinstance(repair, dict):
            repair["kind"] = "cross-configuration cutoff commutator-depth proxy"
        notes.append("aggregate Lie-depth label -> cross-configuration proxy")
    elif name == "moe":
        if isinstance(bridge, dict):
            bridge["kind"] = "positive word-depth audit"
            bridge["claim_note"] = (
                "Finite positive-word filtration; no saturation or Lie-depth claim."
            )
        notes.append("routing closure label -> finite positive word-depth audit")

    if name == "diffusion" and isinstance(wall, dict):
        wall["wall_type"] = "sampled sector-schema transition"
        notes.append("wall label -> sampled sector-schema transition")
    elif name == "maze" and isinstance(wall, dict):
        wall["wall_type"] = "connected-component schema transition"
        notes.append("wall label -> connected-component schema transition")
    elif name == "moe_bias_repair" and isinstance(wall, dict):
        wall["wall_type"] = "routing activation event"
        notes.append("wall label -> routing activation event")

    return bridge, repair, wall, notes


def capability(
    availability: str,
    description: str,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "availability": availability,
        "description": description,
    }
    if availability == "DECLARED":
        if not configuration:
            raise ValueError(f"declared capability lacks configuration: {description}")
        result["configuration"] = configuration
    return result


def strict_labels(name: str, legacy: dict[str, Any]) -> list[str]:
    sectorization = legacy["sectorization"]
    if name == "qwen":
        retained = sectorization["retained_token_indices"]
        members = [item["members"] for item in sectorization["sectors"]]
        flattened = [token for group in members for token in group]
        if len(flattened) != len(set(flattened)) or set(flattened) != set(retained):
            raise ValueError("Qwen retained sectors are not a complete disjoint partition")
        return [f"target-{item['target']}" for item in sectorization["sectors"]]
    labels = sectorization.get("labels")
    if not isinstance(labels, list) or not labels:
        raise ValueError(f"{name}: strict sector labels are absent")
    return [json.dumps(label, separators=(",", ":")) if isinstance(label, list) else str(label)
            for label in labels]


def strict_structure_check(
    name: str,
    legacy: dict[str, Any],
    classification: dict[str, Any],
) -> list[str]:
    labels = strict_labels(name, legacy)
    dimension = classification["dimension"]
    sectorization = legacy["sectorization"]
    dimensions = sectorization.get("sector_dimensions")
    if dimensions is not None and sum(dimensions) != dimension:
        raise ValueError(f"{name}: sector dimensions do not sum to {dimension}")
    if name == "qwen" and len(sectorization["retained_token_indices"]) != dimension:
        raise ValueError("Qwen retained dimension does not match the adapter declaration")
    if name == "recommender" and len(labels) != 8:
        raise ValueError("recommender adapter expects eight cluster sectors")
    return labels


def base_capabilities() -> dict[str, dict[str, Any]]:
    return {
        key: capability("NOT_DECLARED", "Capability not declared by this record.")
        for key in (
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


def build_manifest(
    name: str,
    legacy: dict[str, Any],
    classification: dict[str, Any],
    labels: list[str] | None,
    has_unreached: bool,
) -> dict[str, Any]:
    record_kind = classification["record_kind"]
    capabilities = base_capabilities()
    if record_kind == "strict_sof":
        assert labels is not None
        capabilities["sectorization"] = capability(
            "DECLARED",
            "Complete coordinate-sector realization admitted by the v2 adapter.",
            {
                "origin": legacy["sectorization"]["origin"],
                "realization_status": "computationally certified finite realization",
                "complete": True,
                "labels": labels,
                "provenance": f"frozen SOFRS v1.0 report {name}.sofreport",
            },
        )
        capabilities["operator_carrier"] = capability(
            "DECLARED",
            "Labelled operative alphabet on the admitted finite space.",
            {
                "alphabet_id": f"{slug(name)}-operative-alphabet",
                "word_convention": "positive",
                "adjoint_closed": False,
                "projectors_are_letters": False,
            },
        )
        if classification["word"]:
            capabilities["word_carrier"] = capability(
                "DECLARED",
                "Positive full-word filtration with a finite cutoff.",
                {"semantics": "exact-length positive words in the declared alphabet"},
            )
        if classification["proxy"]:
            capabilities["proxy_diagnostic"] = capability(
                "DECLARED",
                "Carrier-qualified side diagnostic that is not promoted to a missing strict branch.",
                {"proxy_id": f"{slug(name)}-registered-proxy"},
            )
        capabilities["deformation_chart"] = capability(
            "NOT_APPLICABLE",
            "The migrated strict record does not declare a continuous deformation chart.",
        )
        capabilities["diagnostic_analogue"] = capability(
            "NOT_APPLICABLE",
            "The whole record is a strict SOF realization, not an analogue.",
        )
        semantic_requirements = {
            "operative_alphabet": "required",
            "word_convention": "required",
            "projector_letter_policy": "required",
            "direction_convention": "required",
            "depth_indexing": "required" if classification["word"] else "optional",
            "hall_convention": "not_applicable",
        }
        run_requirements = {
            "threshold": "required",
            "cutoff": "required",
            "norm": "required",
            "numerical_tolerance": "required",
            "saturation_audit": "not_applicable",
            "sampling_grid": "not_applicable",
            "trajectory_parameterization": "not_applicable",
        }
        space = {"dimension": classification["dimension"], "scalar_field": "complex"}
    else:
        capabilities["diagnostic_analogue"] = capability(
            "DECLARED",
            "Provenance-bound descriptors with an explicit mapping and strict negative boundary.",
            {"analogue_mapping_id": f"{slug(name)}-analogue-mapping"},
        )
        capabilities["deformation_chart"] = capability(
            "NOT_DECLARED",
            "No fixed typed deformation chart is declared by the aggregate record.",
        )
        semantic_requirements = {
            key: "not_applicable"
            for key in (
                "operative_alphabet",
                "word_convention",
                "projector_letter_policy",
                "direction_convention",
                "depth_indexing",
                "hall_convention",
            )
        }
        run_requirements = {
            "threshold": "optional",
            "cutoff": "required" if has_unreached else "not_applicable",
            "norm": "optional",
            "numerical_tolerance": "optional",
            "saturation_audit": "not_applicable",
            "sampling_grid": "optional",
            "trajectory_parameterization": "optional",
        }
        space = {"dimension": None, "scalar_field": "declared_analogue"}

    return {
        "manifest_version": "1.0",
        "manifest_id": f"paper12.{slug(name)}.v2",
        "record_kind": record_kind,
        "sof_semantics_version": "2.0",
        "adapter": {
            "id": ADAPTER_ID,
            "version": ADAPTER_VERSION,
            "domain": classification["domain"],
            "source_type": classification["source_type"],
        },
        "space": space,
        "capabilities": capabilities,
        "semantic_convention_requirements": semantic_requirements,
        "run_policy_requirements": run_requirements,
        "notes": [
            classification["reason"],
            classification["negative_boundary"],
        ],
    }


def object_record(
    object_id: str,
    kind: str,
    label: str,
    artifact_id: str,
    *,
    carrier_id: str | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": object_id,
        "kind": kind,
        "label": label,
        "provenance_artifact_ids": [artifact_id],
    }
    if carrier_id is not None:
        result["carrier_id"] = carrier_id
    if data is not None:
        result["data"] = data
    return result


def finding(
    finding_id: str,
    kind: str,
    carrier_id: str,
    object_ids: list[str],
    value: Any,
    result_state: str,
    *,
    convention_ids: list[str],
    policy_ids: list[str],
    certificate_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "kind": kind,
        "carrier_id": carrier_id,
        "subject_object_ids": object_ids,
        "value": value,
        "unit": None,
        "result_state": result_state,
        "semantic_convention_ids": convention_ids,
        "run_policy_ids": policy_ids,
        "certificate_ids": certificate_ids,
        "artifact_ids": ["artifact.legacy"],
    }


def claim_record(
    claim_id: str,
    statement: str,
    result_state: str,
    claim_status: str,
    capability_ids: list[str],
    carrier_ids: list[str],
    object_ids: list[str],
    finding_ids: list[str],
    convention_ids: list[str],
    policy_ids: list[str],
    certificate_ids: list[str],
    scope: str,
    negative_boundary: str,
) -> dict[str, Any]:
    return {
        "id": claim_id,
        "statement": statement,
        "result_state": result_state,
        "claim_status": claim_status,
        "capability_ids": capability_ids,
        "carrier_ids": carrier_ids,
        "object_ids": object_ids,
        "finding_ids": finding_ids,
        "semantic_convention_ids": convention_ids,
        "run_policy_ids": policy_ids,
        "hypotheses": [
            "The frozen v1 report, adapter classification, and declared policies are fixed."
        ],
        "certificate_ids": certificate_ids,
        "artifact_ids": ["artifact.legacy"],
        "scope": scope,
        "negative_boundary": negative_boundary,
    }


def strict_ir_content(
    name: str,
    legacy: dict[str, Any],
    classification: dict[str, Any],
    labels: list[str],
    normalized_bridge: Any,
    normalized_repair: Any,
    normalized_wall: Any,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    objects = [
        object_record(
            "space.v",
            "finite_space",
            f"V = C^{classification['dimension']}",
            "artifact.legacy",
            data={"dimension": classification["dimension"], "scalar_field": "complex"},
        ),
        object_record(
            "sectorization.q",
            "sectorization",
            "Complete marked sectorization",
            "artifact.legacy",
            carrier_id="carrier.sector",
            data={"labels": labels, "complete": True, "source": legacy["sectorization"]},
        ),
        object_record(
            "alphabet.y",
            "labelled_alphabet",
            "Declared operative alphabet Y",
            "artifact.legacy",
            carrier_id="carrier.operator",
            data={"source": legacy["observable_family"]},
        ),
        object_record(
            "shadow.r1",
            "support_shadow",
            "Direct operator support R_1[Y]",
            "artifact.legacy",
            carrier_id="carrier.operator",
            data={"source": legacy["support_matrix"]},
        ),
    ]
    conventions = [
        {
            "id": "semantic.alphabet",
            "kind": "operative_alphabet",
            "specification": {
                "alphabet_id": f"{slug(name)}-operative-alphabet",
                "labelled": True,
            },
        },
        {
            "id": "semantic.word",
            "kind": "word_convention",
            "specification": {"type": "positive"},
        },
        {
            "id": "semantic.projector-letter",
            "kind": "projector_letter_policy",
            "specification": {"projectors_are_letters": False},
        },
        {
            "id": "semantic.direction",
            "kind": "direction_convention",
            "specification": {"direction": "j-to-i", "block": "Q_i Y Q_j"},
        },
    ]
    policies = [
        {
            "id": "policy.threshold",
            "kind": "threshold",
            "specification": {"source": "frozen v1 report and generator"},
        },
        {
            "id": "policy.norm",
            "kind": "norm",
            "specification": {"type": "declared block norm"},
        },
        {
            "id": "policy.tolerance",
            "kind": "numerical_tolerance",
            "specification": {"source": "adapter-specific generator"},
        },
        {
            "id": "policy.cutoff",
            "kind": "cutoff",
            "specification": {
                "maximum_depth": classification["cutoff"],
                "unreached_value": UNREACHED,
            },
        },
    ]
    carriers = [
        {
            "id": "carrier.sector",
            "kind": "sector",
            "capability_id": "sectorization",
            "semantics": "Complete marked coordinate-sector decomposition.",
            "object_ids": ["sectorization.q"],
            "semantic_convention_ids": ["semantic.direction"],
        },
        {
            "id": "carrier.operator",
            "kind": "operator",
            "capability_id": "operator_carrier",
            "semantics": "Labelled operative matrices with direct block support.",
            "object_ids": ["alphabet.y", "shadow.r1"],
            "semantic_convention_ids": [
                "semantic.alphabet",
                "semantic.word",
                "semantic.projector-letter",
                "semantic.direction",
            ],
        },
    ]
    findings = [
        finding(
            "finding.direct-support",
            "boolean_support",
            "carrier.operator",
            ["shadow.r1"],
            legacy["support_matrix"],
            "CERTIFIED",
            convention_ids=["semantic.alphabet", "semantic.direction"],
            policy_ids=["policy.threshold", "policy.norm", "policy.tolerance"],
            certificate_ids=["cert.strict-admission"],
        )
    ]
    claims = [
        claim_record(
            "claim.strict-core",
            (
                "The adapter admits a finite complete sectorization and labelled "
                "operator alphabet; direct support is recorded on that operator carrier."
            ),
            "CERTIFIED",
            "Computational Certificate",
            ["sectorization", "operator_carrier"],
            ["carrier.operator"],
            ["space.v", "sectorization.q", "alphabet.y", "shadow.r1"],
            ["finding.direct-support"],
            ["semantic.alphabet", "semantic.direction"],
            ["policy.threshold", "policy.norm", "policy.tolerance"],
            ["cert.strict-admission"],
            f"Frozen Paper XII control {name}.sofreport under adapter v2.0.",
            (
                "Strict admission does not supply route, word, Lie/Hall, or "
                "deformation capabilities that are not separately declared."
            ),
        )
    ]

    if classification["word"]:
        objects.extend(
            [
                object_record(
                    "word-space.audit",
                    "word_space",
                    "Positive full-word audit",
                    "artifact.legacy",
                    carrier_id="carrier.word",
                    data={"bridge": normalized_bridge},
                ),
                object_record(
                    "depth.word",
                    "depth_field",
                    "Cutoff-qualified positive word depth",
                    "artifact.legacy",
                    carrier_id="carrier.word",
                    data={"repair": normalized_repair},
                ),
            ]
        )
        conventions.append(
            {
                "id": "semantic.depth",
                "kind": "depth_indexing",
                "specification": {
                    "direct_word_depth": 1,
                    "unreached": UNREACHED,
                },
            }
        )
        carriers.append(
            {
                "id": "carrier.word",
                "kind": "word",
                "capability_id": "word_carrier",
                "semantics": "Positive full words in the declared labelled alphabet.",
                "object_ids": ["word-space.audit", "depth.word"],
                "semantic_convention_ids": [
                    "semantic.alphabet",
                    "semantic.word",
                    "semantic.projector-letter",
                    "semantic.direction",
                    "semantic.depth",
                ],
            }
        )
        findings.append(
            finding(
                "finding.word-depth",
                "depth",
                "carrier.word",
                ["word-space.audit", "depth.word"],
                {"bridge": normalized_bridge, "repair": normalized_repair},
                "CERTIFIED",
                convention_ids=["semantic.word", "semantic.depth"],
                policy_ids=["policy.cutoff", "policy.threshold", "policy.norm"],
                certificate_ids=["cert.strict-admission"],
            )
        )
        claims.append(
            claim_record(
                "claim.word-audit",
                (
                    "The migrated record reports positive full-word support and "
                    "first-hit depth only through the declared finite cutoff."
                ),
                "CERTIFIED",
                "Computational Certificate",
                ["word_carrier"],
                ["carrier.word"],
                ["word-space.audit", "depth.word"],
                ["finding.word-depth"],
                ["semantic.word", "semantic.depth"],
                ["policy.cutoff", "policy.threshold", "policy.norm"],
                ["cert.strict-admission"],
                f"Positive-word audit in {name}.sofreport.",
                classification["negative_boundary"],
            )
        )

    if classification["proxy"]:
        objects.append(
            object_record(
                "proxy.registered",
                "proxy",
                "Registered side diagnostic",
                "artifact.legacy",
                carrier_id="carrier.proxy",
                data={
                    "bridge": normalized_bridge,
                    "repair": normalized_repair,
                    "wall": normalized_wall,
                },
            )
        )
        carriers.append(
            {
                "id": "carrier.proxy",
                "kind": "proxy",
                "capability_id": "proxy_diagnostic",
                "semantics": "Carrier-qualified diagnostic without strict promotion.",
                "object_ids": ["proxy.registered"],
                "semantic_convention_ids": [],
            }
        )
        findings.append(
            finding(
                "finding.proxy",
                "status_only",
                "carrier.proxy",
                ["proxy.registered"],
                {
                    "bridge": normalized_bridge,
                    "repair": normalized_repair,
                    "wall": normalized_wall,
                },
                "OBSERVED",
                convention_ids=[],
                policy_ids=["policy.cutoff"],
                certificate_ids=[],
            )
        )
        claims.append(
            claim_record(
                "claim.proxy",
                "The legacy bridge, repair, or comparison output is retained as a registered proxy.",
                "OBSERVED",
                "Computational Observation",
                ["proxy_diagnostic"],
                ["carrier.proxy"],
                ["proxy.registered"],
                ["finding.proxy"],
                [],
                ["policy.cutoff"],
                [],
                f"Side diagnostic in {name}.sofreport.",
                classification["negative_boundary"],
            )
        )

    return objects, carriers, conventions, policies, findings, claims


def analogue_ir_content(
    name: str,
    legacy: dict[str, Any],
    classification: dict[str, Any],
    normalized_bridge: Any,
    normalized_repair: Any,
    normalized_wall: Any,
    has_unreached: bool,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    sector_descriptor = deepcopy(legacy["sectorization"])
    if name == "qwen":
        sector_descriptor.pop(
            "strict_sof_realization_on_retained_subspace", None
        )
        retained_dimension = len(sector_descriptor["retained_token_indices"])
        sector_descriptor.update(
            {
                "original_probe_dimension": (
                    retained_dimension
                    + sector_descriptor["excluded_singleton_count"]
                ),
                "retained_space_dimension": retained_dimension,
                "candidate_complete_partition_on_retained_subspace": True,
                "strict_admission_status": "not_admitted",
            }
        )
    analogue_data = {
        "sector_descriptor": sector_descriptor,
        "observable_descriptor": legacy["observable_family"],
        "support_descriptor": legacy["support_matrix"],
        "bridge_descriptor": normalized_bridge,
        "repair_descriptor": normalized_repair,
        "wall_descriptor": normalized_wall,
        "analogue_mapping": classification["reason"],
    }
    objects = [
        object_record(
            "analogue.record",
            "diagnostic_analogue",
            "Provenance-bound diagnostic analogue",
            "artifact.legacy",
            carrier_id="carrier.analogue",
            data=analogue_data,
        )
    ]
    carriers = [
        {
            "id": "carrier.analogue",
            "kind": "analogue",
            "capability_id": "diagnostic_analogue",
            "semantics": "Descriptor-level support, bridge, repair, and wall analogues.",
            "object_ids": ["analogue.record"],
            "semantic_convention_ids": [],
        }
    ]
    policies = []
    policy_ids = []
    if has_unreached:
        cutoff = classification.get("cutoff")
        if not isinstance(cutoff, int) or isinstance(cutoff, bool) or cutoff < 1:
            raise ValueError(f"{name}: UNREACHED_AT_CUTOFF lacks a positive cutoff")
        policies.append(
            {
                "id": "policy.cutoff",
                "kind": "cutoff",
                "specification": {
                    "maximum_depth": cutoff,
                    "source": classification["producer"],
                    "unreached_value": UNREACHED,
                },
            }
        )
        policy_ids.append("policy.cutoff")
    findings = [
        finding(
            "finding.analogue",
            "status_only",
            "carrier.analogue",
            ["analogue.record"],
            analogue_data,
            "OBSERVED",
            convention_ids=[],
            policy_ids=policy_ids,
            certificate_ids=[],
        )
    ]
    claims = [
        claim_record(
            "claim.analogue",
            (
                "The source artifact supports a provenance-bound structurally "
                "analogous diagnostic under the declared mapping."
            ),
            "OBSERVED",
            "Computational Observation",
            ["diagnostic_analogue"],
            ["carrier.analogue"],
            ["analogue.record"],
            ["finding.analogue"],
            [],
            policy_ids,
            [],
            f"Descriptor-level Paper XII control {name}.sofreport.",
            classification["negative_boundary"],
        )
    ]
    return objects, carriers, [], policies, findings, claims


def build_ir(
    name: str,
    legacy_path: Path,
    legacy: dict[str, Any],
    manifest_path: Path,
    manifest: dict[str, Any],
    classification: dict[str, Any],
    labels: list[str] | None,
    normalized_bridge: Any,
    normalized_repair: Any,
    normalized_wall: Any,
    has_unreached: bool,
) -> dict[str, Any]:
    producer_path = PAPER_DIR / classification["producer"]
    if classification["record_kind"] == "strict_sof":
        objects, carriers, conventions, policies, findings, claims = strict_ir_content(
            name,
            legacy,
            classification,
            labels or [],
            normalized_bridge,
            normalized_repair,
            normalized_wall,
        )
        certificates = [
            {
                "id": "cert.strict-admission",
                "validator_id": ADAPTER_ID,
                "status": "PASS",
                "scope": (
                    "Finite complex space, complete coordinate-sector metadata, "
                    "labelled alphabet, and strict/analogue exclusivity."
                ),
                "artifact_ids": ["artifact.legacy", "artifact.manifest"],
            }
        ]
    else:
        objects, carriers, conventions, policies, findings, claims = analogue_ir_content(
            name,
            legacy,
            classification,
            normalized_bridge,
            normalized_repair,
            normalized_wall,
            has_unreached,
        )
        certificates = []

    manifest_digest = {"algorithm": "sha256", "value": sha256(manifest_path)}
    return {
        "ir_version": "1.0",
        "record_id": f"paper12.{slug(name)}.v2",
        "record_kind": classification["record_kind"],
        "manifest_ref": {
            "manifest_id": manifest["manifest_id"],
            "manifest_version": "1.0",
            "artifact_id": "artifact.manifest",
            "digest": manifest_digest,
        },
        "source": {
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "source_id": f"paper12.{slug(name)}.v1",
            "artifact_ids": ["artifact.legacy", "artifact.producer"],
        },
        "objects": objects,
        "carriers": carriers,
        "semantic_conventions": conventions,
        "run_policies": policies,
        "artifacts": [
            {
                "id": "artifact.manifest",
                "uri": repo_uri(manifest_path),
                "digest": manifest_digest,
                "media_type": "application/json",
                "schema_version": "1.0",
                "role": "manifest",
            },
            {
                "id": "artifact.legacy",
                "uri": repo_uri(legacy_path),
                "digest": {"algorithm": "sha256", "value": sha256(legacy_path)},
                "media_type": "application/json",
                "schema_version": "1.0",
                "role": "source-input",
            },
            {
                "id": "artifact.producer",
                "uri": repo_uri(producer_path),
                "digest": {"algorithm": "sha256", "value": sha256(producer_path)},
                "media_type": "text/x-python",
                "schema_version": "1.0",
                "role": "proof-reference",
            },
        ],
        "certificates": certificates,
        "findings": findings,
        "claims": claims,
        "derivations": [],
    }


def compile_modules(
    compiler_output: dict[str, Any],
    ir: dict[str, Any],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    findings = {item["id"]: item for item in ir["findings"]}
    claims = {item["id"]: item for item in ir["claims"]}
    output_by_module: dict[str, list[dict[str, Any]]] = {}
    for item in compiler_output["items"]:
        output_by_module.setdefault(item["module_id"], []).append(item)

    result: list[dict[str, Any]] = []

    for module in profile["modules"]:
        module_items = output_by_module.get(module["id"], [])
        claim_items = [
            item for item in module_items if item["item_kind"] == "claim"
        ]
        if not claim_items:
            degradation_details = [
                detail
                for item in module_items
                if item["item_kind"] == "degradation"
                for detail in item["details"]
            ]
            result.append(
                {
                    "module_id": module["id"],
                    "status": "UNAVAILABLE",
                    "carrier_kinds": module["carrier_kinds"],
                    "finding_ids": [],
                    "claim_ids": [],
                    "output_sections": module["output_sections"],
                    "reason": (
                        "; ".join(degradation_details)
                        if degradation_details
                        else "Paper X Compile_v1 emitted no eligible claim item."
                    ),
                }
            )
            continue

        eligible_claims = [claims[item["claim_id"]] for item in claim_items]
        finding_ids = sorted(
            {
                finding_id
                for claim in eligible_claims
                for finding_id in claim["finding_ids"]
                if finding_id in findings
            }
        )
        result.append(
            {
                "module_id": module["id"],
                "status": "ENABLED",
                "carrier_kinds": module["carrier_kinds"],
                "finding_ids": finding_ids,
                "claim_ids": [item["claim_id"] for item in claim_items],
                "output_sections": module["output_sections"],
            }
        )
    return result


def assemble_normative_items(
    compiler_output: dict[str, Any],
    ir: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    ir_claims = {item["id"]: item for item in ir["claims"]}
    carrier_kinds = {item["id"]: item["kind"] for item in ir["carriers"]}
    claims: list[dict[str, Any]] = []
    degradations: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []

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
        if item["item_kind"] == "claim":
            claim = ir_claims[item["claim_id"]]
            if claim["claim_status"] == "Computational Certificate":
                claim_target = "migration_consistency"
                certificate_class = "migration_assembly"
            else:
                claim_target = "representation_interface"
                certificate_class = None
            claims.append(
                {
                    "report_item_id": report_item_id,
                    "source_output_item_id": source_item_id,
                    "claim_id": claim["id"],
                    "statement": claim["statement"],
                    "result_state": claim["result_state"],
                    "claim_status": claim["claim_status"],
                    "claim_target": claim_target,
                    "certificate_class": certificate_class,
                    "classification_source": "migration_adapter",
                    "external_basis_refs": ["basis.source.identity"],
                    "external_constraint_ids": ["source-snapshot-pinned"],
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
            degradations.append(degradation)

    return claims, degradations, bindings


def build_alignment_readiness(
    legacy_path: Path,
    producer_path: Path,
    legacy: dict[str, Any],
    manifest: dict[str, Any],
    ir: dict[str, Any],
    compiler_profile: dict[str, Any],
    assembly_profile: dict[str, Any],
) -> dict[str, Any]:
    sector_capability = manifest["capabilities"]["sectorization"]
    operator_capability = manifest["capabilities"]["operator_carrier"]

    if sector_capability["availability"] == "DECLARED":
        sector_configuration = sector_capability["configuration"]
        sectorization = legacy["sectorization"]
        ranks = sectorization.get("sector_dimensions", [])
        if not ranks and "sectors" in sectorization:
            ranks = [
                len(sector["members"])
                for sector in sectorization["sectors"]
                if isinstance(sector, dict) and "members" in sector
            ]
        sector_metadata = {
            "status": "PRESENT",
            "labels": sector_configuration["labels"],
            "provenance": sector_configuration["provenance"],
            "ranks_or_dimensions": ranks,
            "semantics": sector_configuration["origin"],
        }
    else:
        sector_metadata = {
            "status": sector_capability["availability"],
            "labels": [],
            "provenance": None,
            "ranks_or_dimensions": [],
            "semantics": None,
        }

    if operator_capability["availability"] == "DECLARED":
        operator_configuration = operator_capability["configuration"]
        observable_metadata = {
            "status": "PRESENT",
            "labels": [operator_configuration["alphabet_id"]],
            "provenance": f"frozen SOFRS v1.0 report {legacy_path.name}",
            "ranks_or_dimensions": [],
            "semantics": (
                f"{operator_configuration['word_convention']} operative alphabet; "
                f"adjoint_closed={operator_configuration['adjoint_closed']}; "
                f"projectors_are_letters="
                f"{operator_configuration['projectors_are_letters']}"
            ),
        }
    else:
        observable_metadata = {
            "status": operator_capability["availability"],
            "labels": [],
            "provenance": None,
            "ranks_or_dimensions": [],
            "semantics": None,
        }

    return {
        "adapter": {
            "id": manifest["adapter"]["id"],
            "version": manifest["adapter"]["version"],
        },
        "compiler_profile_id": compiler_profile["profile_id"],
        "assembly_profile_id": assembly_profile["assembly_profile_id"],
        "sector_metadata": sector_metadata,
        "observable_metadata": observable_metadata,
        "carrier_kinds": sorted({carrier["kind"] for carrier in ir["carriers"]}),
        "semantic_conventions": [
            {"id": item["id"], "kind": item["kind"]}
            for item in ir["semantic_conventions"]
        ],
        "run_policies": [
            {"id": item["id"], "kind": item["kind"]}
            for item in ir["run_policies"]
        ],
        "comparison_keys": [
            f"report:{slug(legacy.get('report_id', legacy_path.stem))}",
            f"system:{slug(legacy['system'])}",
            f"record-kind:{manifest['record_kind']}",
        ],
        "source_artifact_digests": [
            artifact_reference(legacy_path),
            artifact_reference(producer_path),
        ],
    }


def build_external_basis_registry(
    legacy_path: Path,
    producer_path: Path,
    classification: dict[str, Any],
) -> dict[str, Any]:
    source_evidence = [
        artifact_reference(legacy_path),
        artifact_reference(producer_path),
    ]
    analogue = classification["record_kind"] == "diagnostic_analogue"
    levels = {
        "basis.source.identity": {
            "level": "source_identity",
            "constraint_id": "source-snapshot-pinned",
            "status": "SATISFIED",
            "method": "source-and-producer-digest-binding",
            "scope": "The frozen source envelope and its declared producer are source-addressed.",
            "evidence_artifacts": source_evidence,
            "negative_boundary": [
                "Digest binding identifies inputs and producer provenance; it does not establish scientific adequacy."
            ],
        },
        "basis.object.recomputation": {
            "level": "object_level",
            "constraint_id": "object-level-recomputation",
            "status": "NOT_ASSESSED",
            "method": "no-independent-object-recomputation",
            "scope": "No matrix, graph, depth, trajectory, or domain fact is independently recertified by this migration.",
            "evidence_artifacts": [],
            "negative_boundary": [
                "Migration consistency is not an Object Certificate."
            ],
        },
        "basis.structure.validation": {
            "level": "structure_level",
            "constraint_id": "realization-structure-validation",
            "status": "NOT_APPLICABLE" if analogue else "NOT_ASSESSED",
            "method": (
                "analogue-negative-boundary"
                if analogue
                else "strict-realization-validation-not-in-migration"
            ),
            "scope": (
                "The aggregate analogue does not claim a complete strict (V,Q,Y) realization."
                if analogue
                else "Strict realization legality requires a separate source-level validation artifact."
            ),
            "evidence_artifacts": [],
            "negative_boundary": [
                "This field does not authorize strict admission or carrier promotion."
            ],
        },
        "basis.semantic.adequacy": {
            "level": "semantic_adequacy",
            "constraint_id": "domain-semantic-adequacy",
            "status": "NOT_ASSESSED",
            "method": "domain-owner-assessment-not-bound",
            "scope": "The migration does not determine whether the adapter answers the source domain question adequately.",
            "evidence_artifacts": [],
            "negative_boundary": [
                "A protocol-valid analogue may remain scientifically misleading."
            ],
        },
    }
    packages = []
    for basis_id, level in levels.items():
        package = {
            "basis_id": basis_id,
            "level": level["level"],
            "constraint_ids": [level["constraint_id"]],
            **{key: value for key, value in level.items() if key not in {"level", "constraint_id"}},
        }
        packages.append(package)
    constraints = [
        {
            "constraint_id": "source-snapshot-pinned",
            "basis_id": "basis.source.identity",
            "status": "SATISFIED",
            "statement": "The source envelope and producer identity are bound by digests.",
            "evidence_artifacts": source_evidence,
        },
        {
            "constraint_id": "object-level-recomputation",
            "basis_id": "basis.object.recomputation",
            "status": "NOT_ASSESSED",
            "statement": "An independent object-level recomputation is not part of this migration.",
            "evidence_artifacts": [],
        },
        {
            "constraint_id": "realization-structure-validation",
            "basis_id": "basis.structure.validation",
            "status": "NOT_APPLICABLE" if analogue else "NOT_ASSESSED",
            "statement": (
                "The migrated analogue does not assert a complete strict realization."
                if analogue
                else "Strict realization structure requires a separate validation artifact."
            ),
            "evidence_artifacts": [],
        },
        {
            "constraint_id": "domain-semantic-adequacy",
            "basis_id": "basis.semantic.adequacy",
            "status": "NOT_ASSESSED",
            "statement": "Domain adequacy remains the adapter owner's responsibility.",
            "evidence_artifacts": [],
        },
    ]
    return {
        "registry_version": "1.0",
        "basis_status": "PARTIAL",
        "packages": packages,
        "constraints": constraints,
        "negative_boundary": [
            "The external basis records what has and has not been checked; it does not turn protocol conformance into scientific confirmation.",
            "Object-level claims require a satisfied object-level basis and independently checkable evidence.",
        ],
    }


def assemble_sofrs_report(
    legacy_path: Path,
    legacy: dict[str, Any],
    manifest_path: Path,
    ir_path: Path,
    compiler_profile_path: Path,
    assembly_profile_path: Path,
    compiler_output_path: Path,
    manifest: dict[str, Any],
    ir: dict[str, Any],
    compiler_output: dict[str, Any],
    classification: dict[str, Any],
    replacement_count: int,
) -> dict[str, Any]:
    producer_path = PAPER_DIR / classification["producer"]
    compiler_profile = json.loads(compiler_profile_path.read_text(encoding="utf-8"))
    assembly_profile = json.loads(assembly_profile_path.read_text(encoding="utf-8"))
    modules = compile_modules(compiler_output, ir, compiler_profile)
    enabled_finding_ids = {
        finding_id
        for module in modules
        if module["status"] == "ENABLED"
        for finding_id in module["finding_ids"]
    }
    claims, degradation_items, item_bindings = assemble_normative_items(
        compiler_output, ir
    )
    findings = [
        {
            "finding_id": item["id"],
            "kind": item["kind"],
            "result_state": item["result_state"],
            "value": item["value"],
        }
        for item in ir["findings"]
        if item["id"] in enabled_finding_ids
    ]
    failure_modes = deepcopy(legacy.get("failure_modes", []))
    failure_modes.append(classification["negative_boundary"])
    return {
        "sofrs_version": "2.0",
        "report_id": slug(legacy.get("report_id", legacy_path.stem)),
        "system": legacy["system"],
        "record_kind": classification["record_kind"],
        "strict_reconstruction": reconstruction_assessment(classification),
        "external_basis_registry": build_external_basis_registry(
            legacy_path,
            producer_path,
            classification,
        ),
        "compiler_contracts": {
            "capability_manifest": artifact_reference(manifest_path),
            "typed_sof_ir": artifact_reference(ir_path),
            "compiler_profile": artifact_reference(compiler_profile_path),
            "compiler_output": artifact_reference(compiler_output_path),
        },
        "compiler_output_binding": {
            "artifact_id": "artifact.compiler-output",
            "artifact": artifact_reference(compiler_output_path),
            "compiler_id": compiler_output["compiler_id"],
            "compiler_output_version": compiler_output["compiler_output_version"],
            "compiler_profile_id": compiler_output["profile_id"],
        },
        "assembly_contract": {
            "schema_id": ASSEMBLY_CONTRACT_ID,
            "version": ASSEMBLY_CONTRACT_VERSION,
            "implementation": artifact_reference(Path(__file__)),
            "assembly_profile": artifact_reference(assembly_profile_path),
            "assembly_profile_id": assembly_profile["assembly_profile_id"],
        },
        "item_bindings": item_bindings,
        "alignment_readiness": build_alignment_readiness(
            legacy_path,
            producer_path,
            legacy,
            manifest,
            ir,
            compiler_profile,
            assembly_profile,
        ),
        "source_mapping": {
            "status": "migrated",
            "construction": "v1-to-v2-adapter",
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "justification": (
                "The report is assembled by the versioned Paper XII adapter "
                "from a frozen SOFRS v1 envelope and declared v2 contracts."
            ),
            "limitations": [
                "The mapping preserves the v1 source envelope and does not "
                "promote missing strict (V,Q,Y) data."
            ],
        },
        "source_artifacts": [
            artifact_reference(legacy_path),
            artifact_reference(producer_path),
        ],
        "modules": modules,
        "findings": findings,
        "claims": claims,
        "degradation_items": degradation_items,
        "failure_modes": failure_modes,
        "provenance": {
            "kind": "migration",
            "source_artifact": artifact_reference(legacy_path),
            "source_sofrs_version": "1.0",
            "migration_adapter_ref": artifact_reference(Path(__file__)),
            "migration_ruleset_version": "2.0",
            "migration_receipt_ref": artifact_reference(MIGRATION_RECEIPT_PATH),
            "normalized_legacy_sentinels": (
                [f"{replacement_count} integer 999 value(s) -> {UNREACHED}"]
                if replacement_count
                else []
            ),
            "semantic_normalizations": [],
        },
    }


def migrate_one(name: str, classification: dict[str, Any]) -> dict[str, Any]:
    legacy_path = V1_DIR / f"{name}.sofreport"
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    normalized_bridge, bridge_count = replace_unreached(legacy.get("bridge_matrix"))
    normalized_repair, repair_count = replace_unreached(legacy.get("repair_matrix"))
    normalized_wall, wall_count = replace_unreached(legacy.get("wall_record"))
    (
        normalized_bridge,
        normalized_repair,
        normalized_wall,
        semantic_normalizations,
    ) = normalize_semantic_labels(
        name,
        normalized_bridge,
        normalized_repair,
        normalized_wall,
    )
    replacement_count = bridge_count + repair_count + wall_count
    has_unreached = replacement_count > 0

    labels = None
    if classification["record_kind"] == "strict_sof":
        labels = strict_structure_check(name, legacy, classification)

    manifest = build_manifest(
        name,
        legacy,
        classification,
        labels,
        has_unreached,
    )
    manifest_path = MANIFEST_DIR / f"{name}.capabilities.json"
    write_json(manifest_path, manifest)

    ir = build_ir(
        name,
        legacy_path,
        legacy,
        manifest_path,
        manifest,
        classification,
        labels,
        normalized_bridge,
        normalized_repair,
        normalized_wall,
        has_unreached,
    )
    ir_path = IR_DIR / f"{name}.ir.json"
    write_json(ir_path, ir)

    compiler_profile_path = (
        STRICT_COMPILER_PROFILE
        if classification["record_kind"] == "strict_sof"
        else ANALOGUE_COMPILER_PROFILE
    )
    assembly_profile_path = (
        STRICT_ASSEMBLY_PROFILE
        if classification["record_kind"] == "strict_sof"
        else ANALOGUE_ASSEMBLY_PROFILE
    )
    compiler_profile = json.loads(
        compiler_profile_path.read_text(encoding="utf-8")
    )
    rule_registry = json.loads(RULE_REGISTRY_PATH.read_text(encoding="utf-8"))
    compiler_output = compile_output_v1(
        manifest, ir, compiler_profile, rule_registry
    )
    compiler_output_path = COMPILER_OUTPUT_DIR / f"{name}.compiler-output.json"
    write_json(compiler_output_path, compiler_output)

    report = assemble_sofrs_report(
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
        replacement_count,
    )
    report["provenance"]["semantic_normalizations"] = semantic_normalizations
    report_path = REPORT_DIR / f"{name}.sofreport.json"
    write_json(report_path, report)
    return {
        "source": repo_uri(legacy_path),
        "source_digest": sha256(legacy_path),
        "producer": repo_uri(PAPER_DIR / classification["producer"]),
        "producer_digest": sha256(PAPER_DIR / classification["producer"]),
        "record_kind": classification["record_kind"],
        "strict_reconstruction": reconstruction_assessment(classification),
        "manifest": repo_uri(manifest_path),
        "ir": repo_uri(ir_path),
        "compiler_output": repo_uri(compiler_output_path),
        "compiler_profile": repo_uri(compiler_profile_path),
        "assembly_profile": repo_uri(assembly_profile_path),
        "report": repo_uri(report_path),
        "classification_reason": classification["reason"],
        "normalized_legacy_sentinel_count": replacement_count,
    }


def main() -> None:
    expected = {path.stem for path in V1_DIR.glob("*.sofreport")}
    classified = set(CLASSIFICATIONS)
    if expected != classified:
        missing = sorted(expected - classified)
        extra = sorted(classified - expected)
        raise SystemExit(
            f"classification mismatch: missing={missing or 'none'}, extra={extra or 'none'}"
        )

    migrations = [
        migrate_one(name, CLASSIFICATIONS[name])
        for name in sorted(CLASSIFICATIONS)
    ]
    index = {
        "migration_version": "2.0",
        "source_contract": "SOFRS v1.0",
        "target_contract": "SOFRS v2.0",
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "records": migrations,
    }
    write_json(V2_DIR / "migration-index.json", index)
    strict_count = sum(item["record_kind"] == "strict_sof" for item in migrations)
    analogue_count = len(migrations) - strict_count
    reconstruction_yes_count = sum(
        item["strict_reconstruction"]["candidate_status"] == "yes"
        for item in migrations
    )
    print(
        f"Migrated {len(migrations)} reports: "
        f"{strict_count} strict_sof, {analogue_count} diagnostic_analogue; "
        f"{reconstruction_yes_count} controlled reconstruction assessment(s) "
        "with status yes."
    )


if __name__ == "__main__":
    main()
