"""Focused schema and semantic regressions for the Registry v2.0 contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from registry.validate_snapshot import (
    ROOT,
    VALIDATOR_VERSION,
    registry_content_digest,
    validate_payload,
)


SCHEMA_PATH = ROOT / "schemas" / "registry" / "v2.0.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def digest_for(path: Path) -> dict[str, str]:
    return {"algorithm": "sha256", "value": hashlib.sha256(path.read_bytes()).hexdigest()}


def capability(availability: str, description: str) -> dict:
    result = {"availability": availability, "description": description}
    if availability == "DECLARED":
        result["configuration"] = {"registration": "test fixture"}
    return result


def capabilities(*declared: str) -> dict:
    names = (
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
    return {
        name: capability(
            "DECLARED" if name in declared else "NOT_DECLARED",
            f"{name} fixture declaration",
        )
        for name in names
    }


def artifact(
    artifact_id: str = "artifact.source",
    path: Path = SCHEMA_PATH,
    role: str = "source-input",
    evidence_scope: str = "active",
    generated_by_artifact_ids: list[str] | None = None,
    schema_version: str | None = "2.0",
) -> dict:
    return {
        "id": artifact_id,
        "uri": path.relative_to(ROOT).as_posix(),
        "digest": digest_for(path),
        "media_type": "application/json",
        "schema_version": schema_version,
        "role": role,
        "evidence_scope": evidence_scope,
        "generated_by_artifact_ids": generated_by_artifact_ids or [],
    }


def refresh_census(payload: dict) -> dict:
    entries = payload["entries"]
    findings = [finding for entry in entries for finding in entry["findings"]]
    payload["census_certificate"] = {
        "snapshot_id": payload["snapshot"]["id"],
        "content_digest": registry_content_digest(payload),
        "digest_scope": (
            "canonical JSON of the complete Registry payload excluding "
            "census_certificate"
        ),
        "schema_version": "2.0",
        "schema_artifact_id": "artifact.schema",
        "validator_id": "registry-validator",
        "validator_version": VALIDATOR_VERSION,
        "validation_status": "PASS",
        "query_version": "registry-census-v1",
        "summary": {
            "entry_count": len(entries),
            "strict_sof_count": sum(
                entry["record_kind"] == "strict_sof" for entry in entries
            ),
            "diagnostic_analogue_count": sum(
                entry["record_kind"] == "diagnostic_analogue" for entry in entries
            ),
            "capability_counts": {
                capability_id: sum(
                    entry["capabilities"][capability_id]["availability"]
                    == "DECLARED"
                    for entry in entries
                )
                for capability_id in entries[0]["capabilities"]
            },
            "finding_count": len(findings),
            "finding_claim_status_counts": {
                status: sum(
                    finding["claim_status"] == status for finding in findings
                )
                for status in (
                    "Theorem",
                    "Computational Certificate",
                    "Computational Observation",
                    "Research Program",
                )
            },
        },
        "artifact_ids": ["artifact.schema", "artifact.validator"],
    }
    return payload


def base_snapshot(entry: dict, artifacts: list[dict]) -> dict:
    payload = {
        "registry_schema_version": "2.0",
        "sof_semantics_version": "2.0",
        "snapshot": {
            "id": "registry-v2-test",
            "title": "Registry v2 test fixture",
            "release_date": "2026-07-29",
            "status": "draft",
            "source": "schemas/registry/v2.0.schema.json",
            "predecessor": {"id": "paper10-release-v1.0", "schema_version": "1.0"},
            "entry_count": 1,
            "scope_note": "Validator fixture only.",
        },
        "artifacts": artifacts,
        "entries": [entry],
    }
    return refresh_census(payload)


def strict_payload() -> dict:
    source = artifact("artifact.schema", SCHEMA_PATH, "source-input")
    validator = artifact(
        "artifact.validator",
        ROOT / "registry" / "validate_snapshot.py",
        "script",
    )
    entry = {
        "id": "strict-fixture",
        "species": {
            "name": "Strict fixture",
            "category": "test",
            "description": "A finite complex typed SOF fixture.",
        },
        "record_kind": "strict_sof",
        "source_map_status": "represented_realization",
        "evidence_role": "active_evidence",
        "capabilities": capabilities("sectorization", "operator_carrier"),
        "strict_core": {
            "space": {"dimension": 2, "scalar_field": "complex"},
            "sectorization": {
                "origin": "declared test projectors",
                "complete": True,
                "labels": ["a", "b"],
                "projector_data_status": "exact",
                "projector_object_ids": ["sector.a", "sector.b"],
                "provenance_artifact_ids": [source["id"]],
            },
            "operative_alphabet": {
                "id": "alphabet.y",
                "labels": ["y"],
                "word_convention": "positive",
                "adjoint_closed": False,
                "projectors_are_letters": False,
                "provenance_artifact_ids": [source["id"]],
            },
        },
        "analogue_core": None,
        "objects": [
            {"id": "sector.a", "kind": "sector_projector", "label": "Q_a", "artifact_ids": [source["id"]]},
            {"id": "sector.b", "kind": "sector_projector", "label": "Q_b", "artifact_ids": [source["id"]]},
            {"id": "alphabet.y", "kind": "operative_alphabet", "label": "Y", "artifact_ids": [source["id"]]},
        ],
        "semantic_conventions": [
            {"id": "convention.direction", "kind": "direction_convention", "specification": {"direction": "j-to-i"}}
        ],
        "run_policies": [
            {"id": "policy.threshold", "kind": "threshold", "specification": {"value": 0}}
        ],
        "carriers": [
            {
                "id": "carrier.sector",
                "kind": "sector",
                "capability_id": "sectorization",
                "semantics": "Marked sectors.",
                "object_ids": ["sector.a", "sector.b"],
                "semantic_convention_ids": [],
            },
            {
                "id": "carrier.operator",
                "kind": "operator",
                "capability_id": "operator_carrier",
                "semantics": "Declared labelled operator family.",
                "object_ids": ["alphabet.y"],
                "semantic_convention_ids": ["convention.direction"],
            },
        ],
        "observable_channels": [
            {
                "id": "channel.r1-op",
                "branch": "operator",
                "carrier_id": "carrier.operator",
                "field_kind": "labelled_direct_support",
                "semantics": "Generator-labelled direct support.",
                "depth_mode": "not_applicable",
                "depth_cutoff": None,
                "saturation_status": "not_applicable",
                "pair_scope": "off_diagonal",
                "semantic_convention_ids": ["convention.direction"],
                "run_policy_ids": ["policy.threshold"],
            }
        ],
        "dynamics": {
            "status": "static",
            "description": "Static fixture.",
            "variables": [],
            "fixed_labels": None,
            "fixed_conventions": None,
            "continuity": None,
            "comparison_map_object_id": None,
            "trajectory_object_id": None,
            "semantic_convention_ids": [],
            "run_policy_ids": [],
        },
        "artifact_ids": [source["id"]],
        "certificates": [],
        "findings": [
            {
                "id": "finding.r1-op",
                "kind": "boolean_support",
                "comparison_scope": "single_channel",
                "channel_ids": ["channel.r1-op"],
                "carrier_ids": ["carrier.operator"],
                "subject_object_ids": ["sector.a", "sector.b", "alphabet.y"],
                "value": True,
                "unit": None,
                "result_state": "OBSERVED",
                "claim_status": "Computational Observation",
                "semantic_convention_ids": ["convention.direction"],
                "run_policy_ids": ["policy.threshold"],
                "certificate_ids": [],
                "artifact_ids": [source["id"]],
                "qualification": "Finite fixture observation only.",
            }
        ],
        "claims": [
            {
                "id": "claim.r1-op",
                "statement": "The declared direct block is nonzero in the fixture.",
                "result_state": "OBSERVED",
                "claim_status": "Computational Observation",
                "capability_ids": ["operator_carrier"],
                "carrier_ids": ["carrier.operator"],
                "object_ids": ["sector.a", "sector.b", "alphabet.y"],
                "finding_ids": ["finding.r1-op"],
                "semantic_convention_ids": ["convention.direction"],
                "run_policy_ids": ["policy.threshold"],
                "hypotheses": [],
                "certificate_ids": [],
                "artifact_ids": [source["id"]],
                "scope": "Test fixture.",
                "negative_boundary": "No route, word, or Lie claim is made.",
            }
        ],
        "derivations": [],
        "contract_refs": {"capability_manifest": None, "typed_sof_ir": None},
        "metadata": {
            "paper": "Paper X",
            "notes": ["Validator fixture."],
            "predecessor_entry_ids": ["fixture-v1"],
        },
    }
    return base_snapshot(entry, [source, validator])


def analogue_payload() -> dict:
    payload = strict_payload()
    entry = payload["entries"][0]
    entry["id"] = "analogue-fixture"
    entry["record_kind"] = "diagnostic_analogue"
    entry["source_map_status"] = "analogue_mapping"
    entry["evidence_role"] = "external_precedent"
    entry["capabilities"] = capabilities("diagnostic_analogue")
    entry["strict_core"] = None
    entry["analogue_core"] = {
        "descriptors": [
            {"id": "descriptor.support", "kind": "support", "semantics": "Domain support descriptor."}
        ],
        "analogue_mapping": {
            "id": "mapping.analogue",
            "source_terms": ["domain support"],
            "target_analogues": ["structural support analogue"],
            "limitations": "No finite projector realization is declared.",
        },
        "source_provenance_artifact_ids": ["artifact.schema"],
        "negative_sof_boundary": "This record cannot instantiate a strict SOF theorem.",
    }
    entry["objects"] = [
        {"id": "object.analogue", "kind": "analogue_descriptor", "label": "support analogue", "artifact_ids": ["artifact.schema"]}
    ]
    entry["semantic_conventions"] = []
    entry["run_policies"] = []
    entry["carriers"] = [
        {
            "id": "carrier.analogue",
            "kind": "analogue",
            "capability_id": "diagnostic_analogue",
            "semantics": "Structural diagnostic analogue only.",
            "object_ids": ["object.analogue"],
            "semantic_convention_ids": [],
        }
    ]
    entry["observable_channels"] = [
        {
            "id": "channel.analogue",
            "branch": "analogue",
            "carrier_id": "carrier.analogue",
            "field_kind": "analogue_descriptor",
            "semantics": "Analogue support descriptor.",
            "depth_mode": "not_applicable",
            "depth_cutoff": None,
            "saturation_status": "not_applicable",
            "pair_scope": "not_applicable",
            "semantic_convention_ids": [],
            "run_policy_ids": [],
        }
    ]
    finding = entry["findings"][0]
    finding.update({
        "id": "finding.analogue",
        "kind": "status_only",
        "comparison_scope": "single_channel",
        "channel_ids": ["channel.analogue"],
        "carrier_ids": ["carrier.analogue"],
        "subject_object_ids": ["object.analogue"],
        "semantic_convention_ids": [],
        "run_policy_ids": [],
        "qualification": "Structural analogue; not a strict SOF result.",
    })
    claim = entry["claims"][0]
    claim.update({
        "id": "claim.analogue",
        "statement": "The source exposes a structurally analogous support descriptor.",
        "capability_ids": ["diagnostic_analogue"],
        "carrier_ids": ["carrier.analogue"],
        "object_ids": ["object.analogue"],
        "finding_ids": ["finding.analogue"],
        "semantic_convention_ids": [],
        "run_policy_ids": [],
        "negative_boundary": "No SOF theorem instance is asserted.",
    })
    return refresh_census(payload)


def assert_valid(payload: dict) -> None:
    errors = validate_payload(payload, SCHEMA)
    assert not errors, "\n".join(errors)


def assert_invalid(payload: dict, text: str) -> None:
    errors = validate_payload(payload, SCHEMA)
    assert errors, "invalid payload unexpectedly passed"
    assert any(text in error for error in errors), "\n".join(errors)


Draft202012Validator.check_schema(SCHEMA)
assert_valid(strict_payload())
assert_valid(analogue_payload())

generated_result = strict_payload()
producer = artifact(
    "artifact.paper7-producer",
    ROOT / "experiments" / "paper7" / "validation" / "rank_protected_bridge_audit.py",
    "script",
    schema_version=None,
)
result = artifact(
    "artifact.paper7-result",
    ROOT / "experiments" / "paper7" / "results" / "projected_composition_audit.json",
    "source-data",
    generated_by_artifact_ids=[producer["id"]],
    schema_version="paper7.projected-composition-audit.v2",
)
generated_result["artifacts"].extend([producer, result])
generated_result["entries"][0]["artifact_ids"].extend([producer["id"], result["id"]])
refresh_census(generated_result)
assert_valid(generated_result)

wrong_result_producer = strict_payload()
bad_result = artifact(
    "artifact.paper7-result",
    ROOT / "experiments" / "paper7" / "results" / "projected_composition_audit.json",
    "source-data",
    generated_by_artifact_ids=["artifact.validator"],
    schema_version="paper7.projected-composition-audit.v2",
)
wrong_result_producer["artifacts"].append(bad_result)
wrong_result_producer["entries"][0]["artifact_ids"].append(bad_result["id"])
assert_invalid(wrong_result_producer, "runtime.script_sha256 does not match a producer")

stale_digest = strict_payload()
stale_digest["snapshot"]["title"] = "Registry v2 stale-digest fixture"
assert_invalid(stale_digest, "content_digest does not match Registry content")

census_mismatch = strict_payload()
census_mismatch["census_certificate"]["summary"]["entry_count"] = 2
assert_invalid(census_mismatch, "summary does not match recomputed census")

hybrid = strict_payload()
hybrid["entries"][0]["analogue_core"] = analogue_payload()["entries"][0]["analogue_core"]
assert_invalid(hybrid, "None was expected")

carrier_mismatch = strict_payload()
carrier_mismatch["entries"][0]["carriers"][1]["capability_id"] = "word_carrier"
assert_invalid(carrier_mismatch, "requires capability")

incomplete_comparison = strict_payload()
incomplete_comparison["entries"][0]["findings"][0]["comparison_scope"] = (
    "cross_channel"
)
assert_invalid(incomplete_comparison, "is too short")

exact_without_saturation = strict_payload()
channel = exact_without_saturation["entries"][0]["observable_channels"][0]
channel["depth_mode"] = "exact"
channel["saturation_status"] = "exact_saturated"
assert_invalid(exact_without_saturation, "lacks saturation-audit policy")

exact_without_pass = strict_payload()
entry = exact_without_pass["entries"][0]
entry["run_policies"].append({
    "id": "policy.saturation",
    "kind": "saturation_audit",
    "specification": {"method": "closure stabilization"},
})
entry["observable_channels"][0].update({
    "field_kind": "depth",
    "depth_mode": "exact",
    "saturation_status": "computationally_saturated",
    "run_policy_ids": ["policy.saturation"],
})
entry["certificates"] = [{
    "id": "certificate.saturation",
    "kind": "saturation",
    "validator_id": "validator.saturation",
    "status": "FAIL",
    "scope": "Exact-depth saturation fixture.",
    "artifact_ids": ["artifact.schema"],
}]
entry["findings"][0].update({
    "kind": "depth",
    "depth_registration": {
        "mode": "exact",
        "cutoff": None,
        "saturation_certificate_id": "certificate.saturation",
    },
    "run_policy_ids": ["policy.saturation"],
    "certificate_ids": ["certificate.saturation"],
})
assert_invalid(exact_without_pass, "lacks PASS saturation evidence")

exact_without_certificate = strict_payload()
entry = exact_without_certificate["entries"][0]
entry["capabilities"]["word_carrier"] = capability(
    "DECLARED", "Word carrier fixture"
)
entry["run_policies"].append({
    "id": "policy.saturation",
    "kind": "saturation_audit",
    "specification": {"method": "closure stabilization"},
})
entry["objects"].append({
    "id": "object.word-depth",
    "kind": "depth_field",
    "label": "D_word",
    "carrier_id": "carrier.word",
    "artifact_ids": ["artifact.schema"],
})
entry["carriers"].append({
    "id": "carrier.word",
    "kind": "word",
    "capability_id": "word_carrier",
    "semantics": "Positive-word filtration.",
    "object_ids": ["object.word-depth"],
    "semantic_convention_ids": ["convention.alphabet"],
})
channel = entry["observable_channels"][0]
channel.update({
    "branch": "word",
    "carrier_id": "carrier.word",
    "field_kind": "depth",
    "depth_mode": "exact",
    "depth_cutoff": None,
    "saturation_status": "exact_saturated",
    "run_policy_ids": ["policy.saturation"],
})
finding = entry["findings"][0]
finding.update({
    "kind": "depth",
    "carrier_ids": ["carrier.word"],
    "subject_object_ids": ["object.word-depth"],
    "run_policy_ids": ["policy.saturation"],
    "certificate_ids": ["certificate.missing-saturation"],
    "depth_registration": {
        "mode": "exact",
        "cutoff": None,
        "saturation_certificate_id": "certificate.missing-saturation",
    },
})
claim = entry["claims"][0]
claim.update({
    "capability_ids": ["word_carrier"],
    "carrier_ids": ["carrier.word"],
    "object_ids": ["object.word-depth"],
    "run_policy_ids": ["policy.saturation"],
    "certificate_ids": ["certificate.missing-saturation"],
})
assert_invalid(exact_without_certificate, "lacks PASS saturation evidence")

cutoff_mismatch = strict_payload()
finding = cutoff_mismatch["entries"][0]["findings"][0]
finding["result_state"] = "UNREACHED_AT_CUTOFF"
finding["claim_status"] = "Computational Observation"
assert_invalid(cutoff_mismatch, "without truncated depth semantics")

response_without_policy = strict_payload()
finding = response_without_policy["entries"][0]["findings"][0]
finding["kind"] = "response_time"
assert_invalid(response_without_policy, "lacks policies")

archive_evidence = strict_payload()
archive_path = ROOT / "experiments" / "paper7" / "archive" / "markov_graph_sof.py"
archive_evidence["artifacts"][0] = artifact(
    "artifact.schema",
    archive_path,
    evidence_scope="historical_provenance",
)
assert_invalid(archive_evidence, "historical artifact")

analogue_theorem = analogue_payload()
analogue_theorem["artifacts"][0]["role"] = "proof-reference"
claim = analogue_theorem["entries"][0]["claims"][0]
claim["result_state"] = "ESTABLISHED"
claim["claim_status"] = "Theorem"
assert_invalid(analogue_theorem, "cannot instantiate an SOF theorem")

theorem_without_proof = strict_payload()
for owner in (
    theorem_without_proof["entries"][0]["findings"][0],
    theorem_without_proof["entries"][0]["claims"][0],
):
    owner["result_state"] = "ESTABLISHED"
    owner["claim_status"] = "Theorem"
assert_invalid(theorem_without_proof, "requires a proof-reference artifact")

certificate_without_pass = strict_payload()
for owner in (
    certificate_without_pass["entries"][0]["findings"][0],
    certificate_without_pass["entries"][0]["claims"][0],
):
    owner["result_state"] = "CERTIFIED"
    owner["claim_status"] = "Computational Certificate"
assert_invalid(certificate_without_pass, "requires PASS certificate evidence")

missing_comparison = strict_payload()
entry = missing_comparison["entries"][0]
entry["capabilities"]["deformation_chart"] = capability(
    "DECLARED", "Typed deformation fixture"
)
entry["objects"].append({
    "id": "object.deformation",
    "kind": "deformation_chart",
    "label": "deformation",
    "artifact_ids": ["artifact.schema"],
})
entry["carriers"].append({
    "id": "carrier.deformation",
    "kind": "deformation",
    "capability_id": "deformation_chart",
    "semantics": "Typed deformation chart.",
    "object_ids": ["object.deformation"],
    "semantic_convention_ids": [],
})
entry["dynamics"].update({
    "status": "typed_deformation_chart",
    "variables": ["t"],
    "fixed_labels": True,
    "fixed_conventions": True,
    "continuity": "continuous matrix entries",
    "comparison_map_object_id": "object.missing-comparison",
})
assert_invalid(missing_comparison, "lacks comparison-map object")

missing_response_policies = strict_payload()
entry = missing_response_policies["entries"][0]
entry["capabilities"]["deformation_chart"] = capability(
    "DECLARED", "Typed deformation fixture"
)
entry["objects"].extend([
    {
        "id": "object.deformation",
        "kind": "deformation_chart",
        "label": "deformation",
        "artifact_ids": ["artifact.schema"],
    },
    {
        "id": "object.comparison",
        "kind": "comparison_map",
        "label": "comparison map",
        "artifact_ids": ["artifact.schema"],
    },
    {
        "id": "object.trajectory",
        "kind": "trajectory",
        "label": "trajectory",
        "artifact_ids": ["artifact.schema"],
        "data": {"selected_observable_ids": ["alphabet.y"]},
    },
])
entry["carriers"].append({
    "id": "carrier.deformation",
    "kind": "deformation",
    "capability_id": "deformation_chart",
    "semantics": "Typed deformation chart.",
    "object_ids": [
        "object.deformation",
        "object.comparison",
        "object.trajectory",
    ],
    "semantic_convention_ids": [],
})
entry["dynamics"].update({
    "status": "typed_deformation_chart",
    "variables": ["t"],
    "fixed_labels": True,
    "fixed_conventions": True,
    "continuity": "continuous matrix entries",
    "comparison_map_object_id": "object.comparison",
    "trajectory_object_id": "object.trajectory",
})
entry["findings"][0]["kind"] = "response_time"
assert_invalid(missing_response_policies, "lacks policies")

contract_mismatch = strict_payload()
manifest_artifact = artifact("artifact.manifest", role="capability-manifest")
contract_mismatch["artifacts"].append(manifest_artifact)
entry = contract_mismatch["entries"][0]
entry["artifact_ids"].append("artifact.manifest")
entry["contract_refs"]["capability_manifest"] = {
    "artifact_id": "artifact.manifest",
    "version": "1.0",
    "digest": {"algorithm": "sha256", "value": "0" * 64},
}
assert_invalid(contract_mismatch, "digest does not match artifact")

unknown_rule = strict_payload()
unknown_rule["entries"][0]["derivations"] = [{
    "id": "derivation.unknown",
    "source_claim_ids": ["claim.r1-op"],
    "target_claim_id": "claim.r1-op",
    "rule_id": "unregistered-promotion-v1",
    "rule_registry_version": "1.0",
    "rule_status": "Research Program",
    "condition_checks": [{
        "condition_id": "condition.open",
        "description": "No promotion theorem has been registered.",
        "status": "NOT_CHECKED",
        "certificate_ids": [],
        "artifact_ids": [],
    }],
    "derivation_state": "UNRESOLVED",
}]
assert_invalid(unknown_rule, "references unknown rule")

print("test_registry_v2.py: OK")
