"""Validate the example SOF compiler contracts and their semantic links."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.contract_api import (  # noqa: E402
    RESULT_CLAIM_STATUS_MATRIX,
    artifact_reference_errors,
    file_digest,
    load_json,
    schema_errors,
)


EXAMPLES = HERE / "examples"

DEFAULT_MANIFEST = EXAMPLES / "strict-associative-capabilities-v1.0.json"
DEFAULT_IR = EXAMPLES / "strict-associative-ir-v1.0.json"
DEFAULT_PROFILE = EXAMPLES / "basic-associative-closure-profile-v1.0.json"
DEFAULT_RULE_REGISTRY = HERE / "rule-registry-v1.0.json"
DEFAULT_COMPILER_OUTPUT = EXAMPLES / "strict-associative-compiler-output-v1.0.json"
COMPILER_OUTPUT_SCHEMA = HERE / "compiler-output-v1.0.schema.json"

SCHEMAS = {
    "manifest": HERE / "capability-manifest-v1.0.schema.json",
    "ir": HERE / "typed-sof-ir-v1.0.schema.json",
    "profile": HERE / "report-profile-v1.0.schema.json",
}

REQUIRED_CONFIGURATION = {
    "sectorization": {
        "origin",
        "realization_status",
        "complete",
        "labels",
        "provenance",
    },
    "operator_carrier": {
        "alphabet_id",
        "word_convention",
        "adjoint_closed",
        "projectors_are_letters",
    },
    "operator_system": {"definition"},
    "route_carrier": {"semantics"},
    "word_carrier": {"semantics"},
    "positive_associative_closure": {"closure_id"},
    "observable_star_closure": {"closure_id"},
    "sector_enriched_star_closure": {"closure_id"},
    "lie_hall_carrier": {
        "family_id",
        "registration_method",
        "hall_convention_id",
    },
    "deformation_chart": {
        "chart_id",
        "comparison_map_id",
        "trajectory_required",
    },
    "proxy_diagnostic": {"proxy_id"},
    "diagnostic_analogue": {"analogue_mapping_id"},
}

RESULT_STATUS_MATRIX = RESULT_CLAIM_STATUS_MATRIX

OBSERVATION_ARTIFACT_ROLES = {
    "source-input",
    "adapter-output",
    "validator-output",
    "source-data",
    "log",
}


def indexed(items: list[dict], collection: str) -> tuple[dict[str, dict], list[str]]:
    result: dict[str, dict] = {}
    errors: list[str] = []
    for item in items:
        item_id = item["id"]
        if item_id in result:
            errors.append(f"{collection}: duplicate ID {item_id}")
        result[item_id] = item
    return result, errors


def manifest_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    capabilities = manifest["capabilities"]

    for capability_id, declaration in capabilities.items():
        if declaration["availability"] != "DECLARED":
            continue
        configuration = declaration.get("configuration", {})
        missing = sorted(REQUIRED_CONFIGURATION[capability_id] - configuration.keys())
        if missing:
            errors.append(
                f"manifest capability {capability_id}: missing configuration keys "
                + ", ".join(missing)
            )

    if manifest["record_kind"] == "strict_sof":
        if not isinstance(manifest["space"]["dimension"], int):
            errors.append("strict_sof requires a finite integer dimension")
        if manifest["space"]["scalar_field"] != "complex":
            errors.append("strict_sof semantics v2.0 requires complex scalar field")
        for capability_id in ("sectorization", "operator_carrier"):
            if capabilities[capability_id]["availability"] != "DECLARED":
                errors.append(
                    f"strict_sof requires declared capability {capability_id}"
                )
        if capabilities["diagnostic_analogue"]["availability"] == "DECLARED":
            errors.append("strict_sof cannot also declare diagnostic_analogue")
    elif capabilities["diagnostic_analogue"]["availability"] != "DECLARED":
        errors.append(
            "diagnostic_analogue record requires its analogue mapping capability"
        )

    if (
        capabilities["lie_hall_carrier"]["availability"] == "DECLARED"
        and manifest["semantic_convention_requirements"]["hall_convention"]
        != "required"
    ):
        errors.append("declared Lie/Hall carrier requires hall_convention")

    deformation = capabilities["deformation_chart"]
    if (
        deformation["availability"] == "DECLARED"
        and deformation["configuration"].get("trajectory_required")
        and manifest["run_policy_requirements"]["trajectory_parameterization"]
        != "required"
    ):
        errors.append(
            "trajectory-enabled deformation requires trajectory_parameterization"
        )

    return errors


def digest_value(path: Path, algorithm: str) -> str:
    return file_digest(path, algorithm)


def artifact_errors(artifacts: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    for artifact_id, artifact in artifacts.items():
        errors.extend(
            artifact_reference_errors(
                artifact,
                label=f"artifact {artifact_id}",
                repository_root=ROOT,
                allowed_algorithms=("sha256", "sha512"),
            )
        )
    return errors


def evidence_errors(
    claim: dict,
    artifacts: dict[str, dict],
    certificates: dict[str, dict],
) -> list[str]:
    errors: list[str] = []
    claim_id = claim["id"]
    status = claim["claim_status"]
    referenced_artifacts = [
        artifacts[artifact_id]
        for artifact_id in claim["artifact_ids"]
        if artifact_id in artifacts
    ]
    referenced_certificates = [
        certificates[certificate_id]
        for certificate_id in claim["certificate_ids"]
        if certificate_id in certificates
    ]

    if status == "Theorem":
        if not any(
            artifact["role"] == "proof-reference"
            for artifact in referenced_artifacts
        ):
            errors.append(f"claim {claim_id}: Theorem requires a proof-reference")
    elif status == "Computational Certificate":
        if not referenced_certificates or not all(
            certificate["status"] == "PASS"
            for certificate in referenced_certificates
        ):
            errors.append(
                f"claim {claim_id}: Computational Certificate requires PASS evidence"
            )
    elif status == "Computational Observation":
        if not any(
            artifact["role"] in OBSERVATION_ARTIFACT_ROLES
            for artifact in referenced_artifacts
        ):
            errors.append(
                f"claim {claim_id}: Computational Observation requires a source artifact"
            )
    elif status is None and claim["result_state"] not in {
        "DECLARED",
        "NOT_APPLICABLE",
        "NOT_DECLARED",
    }:
        errors.append(f"claim {claim_id}: active result has null claim status")

    return errors


def derivation_state_errors(
    derivation_state: str,
    rule_status: str,
    condition_statuses: list[str],
) -> list[str]:
    errors: list[str] = []
    if derivation_state == "VALID":
        if any(status != "SATISFIED" for status in condition_statuses):
            errors.append("VALID requires all conditions satisfied")
        if rule_status == "Research Program":
            errors.append("an open rule cannot yield a VALID derivation")
    elif derivation_state == "INVALID":
        if "FAILED" not in condition_statuses:
            errors.append("INVALID requires a failed condition")
    elif (
        "NOT_CHECKED" not in condition_statuses
        and rule_status != "Research Program"
    ):
        errors.append("UNRESOLVED requires an unchecked condition or open rule")
    return errors


def ir_reference_errors(
    manifest: dict,
    ir: dict,
    rule_registry: dict,
) -> list[str]:
    errors: list[str] = []
    capabilities = manifest["capabilities"]

    if ir["manifest_ref"]["manifest_id"] != manifest["manifest_id"]:
        errors.append("IR manifest_ref.manifest_id does not match the manifest")
    if ir["record_kind"] != manifest["record_kind"]:
        errors.append("IR record_kind does not match the manifest")
    if ir["source"]["adapter_id"] != manifest["adapter"]["id"]:
        errors.append("IR source.adapter_id does not match the manifest adapter")
    if ir["source"]["adapter_version"] != manifest["adapter"]["version"]:
        errors.append("IR source.adapter_version does not match the manifest adapter")

    collections: dict[str, dict[str, dict]] = {}
    for name in (
        "objects",
        "carriers",
        "semantic_conventions",
        "run_policies",
        "artifacts",
        "certificates",
        "findings",
        "claims",
        "derivations",
    ):
        collections[name], duplicate_errors = indexed(ir[name], name)
        errors.extend(duplicate_errors)

    objects = collections["objects"]
    carriers = collections["carriers"]
    conventions = collections["semantic_conventions"]
    policies = collections["run_policies"]
    artifacts = collections["artifacts"]
    certificates = collections["certificates"]
    findings = collections["findings"]
    claims = collections["claims"]

    rules, rule_id_errors = indexed(rule_registry["rules"], "rule registry")
    errors.extend(rule_id_errors)
    if rule_registry.get("rule_registry_version") != "1.0":
        errors.append("unsupported rule registry version")
    allowed_promotion_ids = set(
        load_json(SCHEMAS["profile"])["$defs"]["promotion_id"]["enum"]
    )
    for rule_id, rule in rules.items():
        missing = sorted(
            {"status", "promotion_id", "description", "source"} - rule.keys()
        )
        if missing:
            errors.append(
                f"rule registry {rule_id}: missing fields {', '.join(missing)}"
            )
        if rule.get("promotion_id") not in allowed_promotion_ids:
            errors.append(
                f"rule registry {rule_id}: unknown promotion_id "
                f"{rule.get('promotion_id')}"
            )

    errors.extend(artifact_errors(artifacts))

    manifest_artifact_id = ir["manifest_ref"]["artifact_id"]
    if manifest_artifact_id not in artifacts:
        errors.append("manifest_ref references an unknown artifact")
    else:
        manifest_artifact = artifacts[manifest_artifact_id]
        if manifest_artifact["role"] != "manifest":
            errors.append("manifest_ref artifact does not have manifest role")
        if manifest_artifact["digest"] != ir["manifest_ref"]["digest"]:
            errors.append("manifest_ref digest differs from artifact registry digest")

    for artifact_id in ir["source"]["artifact_ids"]:
        if artifact_id not in artifacts:
            errors.append(f"source references unknown artifact {artifact_id}")

    for object_id, obj in objects.items():
        carrier_id = obj.get("carrier_id")
        if carrier_id and carrier_id not in carriers:
            errors.append(f"object {object_id}: unknown carrier_id {carrier_id}")
        for artifact_id in obj["provenance_artifact_ids"]:
            if artifact_id not in artifacts:
                errors.append(
                    f"object {object_id}: unknown provenance artifact {artifact_id}"
                )

    for carrier_id, carrier in carriers.items():
        capability_id = carrier["capability_id"]
        if capabilities[capability_id]["availability"] != "DECLARED":
            errors.append(
                f"carrier {carrier_id}: capability {capability_id} is not declared"
            )
        for object_id in carrier["object_ids"]:
            if object_id not in objects:
                errors.append(f"carrier {carrier_id}: unknown object_id {object_id}")
        for convention_id in carrier["semantic_convention_ids"]:
            if convention_id not in conventions:
                errors.append(
                    f"carrier {carrier_id}: unknown convention {convention_id}"
                )

    convention_kinds = {item["kind"] for item in conventions.values()}
    for kind, requirement in manifest["semantic_convention_requirements"].items():
        if requirement == "required" and kind not in convention_kinds:
            errors.append(f"required semantic convention is absent from IR: {kind}")
        if requirement == "not_applicable" and kind in convention_kinds:
            errors.append(
                f"not-applicable semantic convention appears in IR: {kind}"
            )

    conventions_by_kind: dict[str, list[dict]] = {}
    for convention in conventions.values():
        conventions_by_kind.setdefault(convention["kind"], []).append(convention)
    operator_configuration = capabilities["operator_carrier"].get(
        "configuration",
        {},
    )
    identity_checks = (
        (
            "operative_alphabet",
            "alphabet_id",
            operator_configuration.get("alphabet_id"),
        ),
        (
            "word_convention",
            "type",
            operator_configuration.get("word_convention"),
        ),
        (
            "projector_letter_policy",
            "projectors_are_letters",
            operator_configuration.get("projectors_are_letters"),
        ),
    )
    for kind, field, expected in identity_checks:
        if expected is None:
            continue
        matches = conventions_by_kind.get(kind, [])
        if not any(
            convention["specification"].get(field) == expected
            for convention in matches
        ):
            errors.append(
                f"semantic convention {kind} does not match manifest "
                f"{field}={expected!r}"
            )

    policy_kinds = {item["kind"] for item in policies.values()}
    for kind, requirement in manifest["run_policy_requirements"].items():
        if requirement == "required" and kind not in policy_kinds:
            errors.append(f"required run policy is absent from IR: {kind}")
        if requirement == "not_applicable" and kind in policy_kinds:
            errors.append(f"not-applicable run policy appears in IR: {kind}")

    for certificate_id, certificate in certificates.items():
        for artifact_id in certificate["artifact_ids"]:
            if artifact_id not in artifacts:
                errors.append(
                    f"certificate {certificate_id}: unknown artifact {artifact_id}"
                )

    for finding_id, finding in findings.items():
        carrier_id = finding["carrier_id"]
        if carrier_id is not None and carrier_id not in carriers:
            errors.append(f"finding {finding_id}: unknown carrier {carrier_id}")
        for object_id in finding["subject_object_ids"]:
            if object_id not in objects:
                errors.append(f"finding {finding_id}: unknown object {object_id}")
        for convention_id in finding["semantic_convention_ids"]:
            if convention_id not in conventions:
                errors.append(
                    f"finding {finding_id}: unknown convention {convention_id}"
                )
        for policy_id in finding["run_policy_ids"]:
            if policy_id not in policies:
                errors.append(f"finding {finding_id}: unknown run policy {policy_id}")
        for certificate_id in finding["certificate_ids"]:
            if certificate_id not in certificates:
                errors.append(
                    f"finding {finding_id}: unknown certificate {certificate_id}"
                )
        for artifact_id in finding["artifact_ids"]:
            if artifact_id not in artifacts:
                errors.append(f"finding {finding_id}: unknown artifact {artifact_id}")

        if finding["result_state"] == "UNREACHED_AT_CUTOFF":
            cutoff_ids = {
                policy_id
                for policy_id, policy in policies.items()
                if policy["kind"] == "cutoff"
            }
            if not cutoff_ids.intersection(finding["run_policy_ids"]):
                errors.append(
                    f"finding {finding_id}: cutoff-unreached state lacks cutoff policy"
                )
        if finding["result_state"] in {"NOT_DECLARED", "NOT_APPLICABLE"}:
            if carrier_id is not None or finding["certificate_ids"]:
                errors.append(
                    f"finding {finding_id}: unavailable state has carrier/certificate"
                )

    for claim_id, claim in claims.items():
        references = (
            ("carrier", claim["carrier_ids"], carriers),
            ("object", claim["object_ids"], objects),
            ("finding", claim["finding_ids"], findings),
            ("convention", claim["semantic_convention_ids"], conventions),
            ("run policy", claim["run_policy_ids"], policies),
            ("certificate", claim["certificate_ids"], certificates),
            ("artifact", claim["artifact_ids"], artifacts),
        )
        for label, ids, known in references:
            for item_id in ids:
                if item_id not in known:
                    errors.append(f"claim {claim_id}: unknown {label} {item_id}")

        state = claim["result_state"]
        status = claim["claim_status"]
        if status not in RESULT_STATUS_MATRIX[state]:
            errors.append(
                f"claim {claim_id}: illegal result/claim status pair "
                f"{state!r} + {status!r}"
            )

        capability_states = {
            capability_id: capabilities[capability_id]["availability"]
            for capability_id in claim["capability_ids"]
        }
        if state == "NOT_DECLARED":
            if not all(value == "NOT_DECLARED" for value in capability_states.values()):
                errors.append(
                    f"claim {claim_id}: NOT_DECLARED mismatches capability availability"
                )
            if claim["carrier_ids"] or claim["certificate_ids"]:
                errors.append(
                    f"claim {claim_id}: NOT_DECLARED has carrier or certificate"
                )
        elif state == "NOT_APPLICABLE":
            if not all(
                value == "NOT_APPLICABLE" for value in capability_states.values()
            ):
                errors.append(
                    f"claim {claim_id}: NOT_APPLICABLE mismatches capability availability"
                )
            if claim["carrier_ids"] or claim["certificate_ids"]:
                errors.append(
                    f"claim {claim_id}: NOT_APPLICABLE has carrier or certificate"
                )
        else:
            unavailable = sorted(
                capability_id
                for capability_id, availability in capability_states.items()
                if availability != "DECLARED"
            )
            if unavailable:
                errors.append(
                    f"claim {claim_id}: active result uses unavailable capabilities "
                    + ", ".join(unavailable)
                )

        if state == "UNREACHED_AT_CUTOFF":
            cutoff_ids = {
                policy_id
                for policy_id, policy in policies.items()
                if policy["kind"] == "cutoff"
            }
            if not cutoff_ids.intersection(claim["run_policy_ids"]):
                errors.append(
                    f"claim {claim_id}: cutoff-unreached state lacks cutoff policy"
                )

        for finding_id in claim["finding_ids"]:
            if (
                finding_id in findings
                and status != "Theorem"
                and findings[finding_id]["result_state"] != state
            ):
                errors.append(
                    f"claim {claim_id}: finding {finding_id} has a different result state"
                )
            if finding_id not in findings:
                continue

            finding = findings[finding_id]
            dependency_sets = (
                (
                    "carrier",
                    {finding["carrier_id"]} if finding["carrier_id"] else set(),
                    set(claim["carrier_ids"]),
                ),
                (
                    "object",
                    set(finding["subject_object_ids"]),
                    set(claim["object_ids"]),
                ),
                (
                    "semantic convention",
                    set(finding["semantic_convention_ids"]),
                    set(claim["semantic_convention_ids"]),
                ),
                (
                    "run policy",
                    set(finding["run_policy_ids"]),
                    set(claim["run_policy_ids"]),
                ),
                (
                    "certificate",
                    set(finding["certificate_ids"]),
                    set(claim["certificate_ids"]),
                ),
                (
                    "artifact",
                    set(finding["artifact_ids"]),
                    set(claim["artifact_ids"]),
                ),
            )
            for label, required_ids, claim_ids in dependency_sets:
                missing = sorted(required_ids - claim_ids)
                if missing:
                    errors.append(
                        f"claim {claim_id}: finding {finding_id} dependency "
                        f"omits {label} {', '.join(missing)}"
                    )

        errors.extend(evidence_errors(claim, artifacts, certificates))

    for derivation_id, derivation in collections["derivations"].items():
        for claim_id in derivation["source_claim_ids"]:
            if claim_id not in claims:
                errors.append(
                    f"derivation {derivation_id}: unknown source claim {claim_id}"
                )
        target_claim_id = derivation["target_claim_id"]
        if target_claim_id not in claims:
            errors.append(
                f"derivation {derivation_id}: unknown target claim {target_claim_id}"
            )

        rule_id = derivation["rule_id"]
        if rule_id not in rules:
            errors.append(f"derivation {derivation_id}: unknown rule {rule_id}")
        else:
            rule = rules[rule_id]
            if derivation["rule_status"] != rule["status"]:
                errors.append(
                    f"derivation {derivation_id}: rule status differs from registry"
                )
        if derivation["rule_registry_version"] != rule_registry["rule_registry_version"]:
            errors.append(f"derivation {derivation_id}: rule registry version mismatch")

        condition_ids: set[str] = set()
        condition_statuses: list[str] = []
        for condition in derivation["condition_checks"]:
            condition_id = condition["condition_id"]
            if condition_id in condition_ids:
                errors.append(
                    f"derivation {derivation_id}: duplicate condition {condition_id}"
                )
            condition_ids.add(condition_id)
            condition_statuses.append(condition["status"])

            condition_certificates = [
                certificates[certificate_id]
                for certificate_id in condition["certificate_ids"]
                if certificate_id in certificates
            ]
            condition_artifacts = [
                artifacts[artifact_id]
                for artifact_id in condition["artifact_ids"]
                if artifact_id in artifacts
            ]
            for certificate_id in condition["certificate_ids"]:
                if certificate_id not in certificates:
                    errors.append(
                        f"derivation {derivation_id}: unknown condition certificate "
                        f"{certificate_id}"
                    )
            for artifact_id in condition["artifact_ids"]:
                if artifact_id not in artifacts:
                    errors.append(
                        f"derivation {derivation_id}: unknown condition artifact "
                        f"{artifact_id}"
                    )

            if condition["status"] == "SATISFIED":
                pass_certificate = any(
                    certificate["status"] == "PASS"
                    for certificate in condition_certificates
                )
                proof_reference = any(
                    artifact["role"] == "proof-reference"
                    for artifact in condition_artifacts
                )
                if not (pass_certificate or proof_reference):
                    errors.append(
                        f"derivation {derivation_id}: satisfied condition "
                        f"{condition_id} has no evidence"
                    )

        derivation_state = derivation["derivation_state"]
        for state_error in derivation_state_errors(
            derivation_state,
            derivation["rule_status"],
            condition_statuses,
        ):
            errors.append(f"derivation {derivation_id}: {state_error}")
        if derivation_state == "VALID":
            if (
                target_claim_id in claims
                and claims[target_claim_id]["result_state"]
                not in {"ESTABLISHED", "CERTIFIED"}
            ):
                errors.append(
                    f"derivation {derivation_id}: VALID target is not established/certified"
                )
    return errors


def expression_errors(values: set[str], expression: dict) -> list[str]:
    errors: list[str] = []
    missing_all = sorted(set(expression["all_of"]) - values)
    if missing_all:
        errors.append("missing all_of: " + ", ".join(missing_all))
    if expression["any_of"] and not values.intersection(expression["any_of"]):
        errors.append("no any_of member present: " + ", ".join(expression["any_of"]))
    prohibited = sorted(values.intersection(expression["none_of"]))
    if prohibited:
        errors.append("none_of member present: " + ", ".join(prohibited))
    return errors


def profile_evidence_errors(
    claim: dict,
    requirement: str,
    artifacts: dict[str, dict],
    certificates: dict[str, dict],
) -> list[str]:
    if requirement == "NO_EVIDENCE_REQUIRED" or requirement == "NO_CLAIM":
        return []
    if requirement == "PROOF_REFERENCE":
        if any(
            artifacts[artifact_id]["role"] == "proof-reference"
            for artifact_id in claim["artifact_ids"]
            if artifact_id in artifacts
        ):
            return []
    elif requirement == "PASS_CERTIFICATE":
        referenced = [
            certificates[certificate_id]
            for certificate_id in claim["certificate_ids"]
            if certificate_id in certificates
        ]
        if referenced and all(item["status"] == "PASS" for item in referenced):
            return []
    elif requirement == "SOURCE_ARTIFACT":
        if any(
            artifacts[artifact_id]["role"] in OBSERVATION_ARTIFACT_ROLES
            for artifact_id in claim["artifact_ids"]
            if artifact_id in artifacts
        ):
            return []
    return [f"claim {claim['id']} does not satisfy {requirement}"]


def claim_module_requirement_errors(
    claim: dict,
    module: dict,
    capabilities: dict[str, dict],
    objects: dict[str, dict],
    conventions: dict[str, dict],
    policies: dict[str, dict],
) -> list[str]:
    claim_capabilities = {
        capability_id
        for capability_id in claim["capability_ids"]
        if capability_id in capabilities
        and capabilities[capability_id]["availability"] == "DECLARED"
    }
    claim_object_kinds = {
        objects[object_id]["kind"]
        for object_id in claim["object_ids"]
        if object_id in objects
    }
    claim_convention_kinds = {
        conventions[convention_id]["kind"]
        for convention_id in claim["semantic_convention_ids"]
        if convention_id in conventions
    }
    claim_policy_kinds = {
        policies[policy_id]["kind"]
        for policy_id in claim["run_policy_ids"]
        if policy_id in policies
    }
    requirement_specs = (
        (
            "capability",
            claim_capabilities,
            module["capability_requirements"],
        ),
        (
            "object",
            claim_object_kinds,
            module["object_kind_requirements"],
        ),
        (
            "semantic convention",
            claim_convention_kinds,
            module["semantic_convention_requirements"],
        ),
        (
            "run policy",
            claim_policy_kinds,
            module["run_policy_requirements"],
        ),
    )

    errors: list[str] = []
    for label, values, expression in requirement_specs:
        for expression_error in expression_errors(values, expression):
            errors.append(f"{label}: {expression_error}")
    return errors


def claim_derivation_errors(
    claim: dict,
    derivations_by_target: dict[str, list[dict]],
    rules: dict[str, dict],
) -> list[str]:
    errors: list[str] = []
    for derivation in derivations_by_target.get(claim["id"], []):
        rule = rules.get(derivation["rule_id"])
        if rule is None:
            errors.append(f"unknown rule {derivation['rule_id']}")
            continue
        if derivation["derivation_state"] != "VALID":
            errors.append(
                f"derivation {derivation['id']} is "
                f"{derivation['derivation_state']}"
            )
        if derivation["rule_status"] == "Research Program":
            errors.append(f"derivation {derivation['id']} uses an open rule")
        unchecked = [
            condition["condition_id"]
            for condition in derivation["condition_checks"]
            if condition["status"] != "SATISFIED"
        ]
        if unchecked:
            errors.append(
                f"derivation {derivation['id']} has unsatisfied conditions "
                f"{', '.join(unchecked)}"
            )
    return errors


def _compiler_run(
    manifest: dict,
    ir: dict,
    profile: dict,
    rule_registry: dict,
) -> tuple[list[str], list[str], dict]:
    """Run compilation while retaining diagnostics for the validator CLI.

    This function implements module admission and claim emission. It does not
    serialize a SOFRS report; downstream report protocols consume this output.
    """
    errors: list[str] = []
    plan: list[str] = []
    items: list[dict] = []
    capabilities = manifest["capabilities"]
    declared_capabilities = {
        capability_id
        for capability_id, declaration in capabilities.items()
        if declaration["availability"] == "DECLARED"
    }
    object_kinds = {obj["kind"] for obj in ir["objects"]}
    convention_kinds = {
        convention["kind"] for convention in ir["semantic_conventions"]
    }
    policy_kinds = {policy["kind"] for policy in ir["run_policies"]}
    objects = {obj["id"]: obj for obj in ir["objects"]}
    conventions = {
        convention["id"]: convention for convention in ir["semantic_conventions"]
    }
    policies = {policy["id"]: policy for policy in ir["run_policies"]}
    carriers = {carrier["id"]: carrier for carrier in ir["carriers"]}
    artifacts = {artifact["id"]: artifact for artifact in ir["artifacts"]}
    certificates = {
        certificate["id"]: certificate for certificate in ir["certificates"]
    }
    rules = {rule["id"]: rule for rule in rule_registry["rules"]}
    derivations_by_target: dict[str, list[dict]] = {}
    for derivation in ir["derivations"]:
        derivations_by_target.setdefault(derivation["target_claim_id"], []).append(
            derivation
        )

    if manifest["record_kind"] not in profile["applies_to"]:
        errors.append("report profile does not apply to this record_kind")
        return errors, plan, {}

    module_ids = [module["id"] for module in profile["modules"]]
    duplicates = sorted(
        {module_id for module_id in module_ids if module_ids.count(module_id) > 1}
    )
    if duplicates:
        errors.append(f"profile modules: duplicate IDs: {', '.join(duplicates)}")

    expression_specs = (
        (
            "capability",
            declared_capabilities,
            "capability_requirements",
            "unsatisfied_capability_expression",
        ),
        (
            "object",
            object_kinds,
            "object_kind_requirements",
            "unsatisfied_object_expression",
        ),
        (
            "semantic convention",
            convention_kinds,
            "semantic_convention_requirements",
            "unsatisfied_policy_expression",
        ),
        (
            "run policy",
            policy_kinds,
            "run_policy_requirements",
            "unsatisfied_policy_expression",
        ),
    )

    for module in profile["modules"]:
        module_id = module["id"]
        blocked = False
        for label, values, field, degradation_field in expression_specs:
            failures = expression_errors(values, module[field])
            if failures:
                action = profile["degradation_policy"][degradation_field]
                plan.append(
                    f"{module_id}: {action} ({label}: {'; '.join(failures)})"
                )
                items.append(
                    {
                        "item_kind": "degradation",
                        "module_id": module_id,
                        "action": action,
                        "reason_kind": f"unsatisfied_{field}",
                        "details": failures,
                    }
                )
                if action == "fail_profile":
                    errors.append(
                        f"profile module {module_id}: unsatisfied {label} expression"
                    )
                blocked = True
        if blocked:
            continue

        eligible_claims: list[dict] = []
        for claim in ir["claims"]:
            claim_carrier_kinds = {
                carriers[carrier_id]["kind"]
                for carrier_id in claim["carrier_ids"]
                if carrier_id in carriers
            }
            if not claim_carrier_kinds.intersection(module["carrier_kinds"]):
                continue
            if claim["result_state"] not in module["accepted_result_states"]:
                continue
            if (
                claim["claim_status"] is not None
                and claim["claim_status"] not in module["accepted_claim_statuses"]
            ):
                continue
            requirement_failures = claim_module_requirement_errors(
                claim,
                module,
                capabilities,
                objects,
                conventions,
                policies,
            )
            if requirement_failures:
                plan.append(
                    f"{module_id}: omit_claim {claim['id']} "
                    f"({'; '.join(requirement_failures)})"
                )
                items.append(
                    {
                        "item_kind": "degradation",
                        "module_id": module_id,
                        "action": "omit_claim",
                        "reason_kind": "claim_ineligible",
                        "source_ir_id": claim["id"],
                        "details": requirement_failures,
                    }
                )
                continue
            derivation_failures = claim_derivation_errors(
                claim,
                derivations_by_target,
                rules,
            )
            if derivation_failures:
                plan.append(
                    f"{module_id}: omit_claim {claim['id']} "
                    f"({'; '.join(derivation_failures)})"
                )
                items.append(
                    {
                        "item_kind": "degradation",
                        "module_id": module_id,
                        "action": "omit_claim",
                        "reason_kind": "derivation_invalid",
                        "source_ir_id": claim["id"],
                        "details": derivation_failures,
                    }
                )
                continue
            eligible_claims.append(claim)

        if not eligible_claims:
            errors.append(f"profile module {module_id}: no eligible IR claims")
            continue

        for claim in eligible_claims:
            claim_errors: list[str] = []
            evidence_key = (
                claim["claim_status"]
                if claim["claim_status"] is not None
                else "null"
            )
            requirement = module["evidence_requirements"][evidence_key]
            for evidence_error in profile_evidence_errors(
                claim,
                requirement,
                artifacts,
                certificates,
            ):
                claim_errors.append(evidence_error)

            forbidden = set(module["forbidden_promotion_ids"])
            for derivation in derivations_by_target.get(claim["id"], []):
                rule = rules.get(derivation["rule_id"])
                if rule and rule["promotion_id"] in forbidden:
                    claim_errors.append(
                        f"target claim {claim['id']} uses forbidden promotion "
                        f"{rule['promotion_id']}"
                    )

            if claim_errors:
                errors.extend(
                    f"profile module {module_id}: {claim_error}"
                    for claim_error in claim_errors
                )
                continue

            derivation_ids = [
                derivation["id"]
                for derivation in derivations_by_target.get(claim["id"], [])
            ]
            items.append(
                {
                    "item_kind": "claim",
                    "module_id": module_id,
                    "claim_id": claim["id"],
                    "source_ir_kind": "claim",
                    "source_ir_id": claim["id"],
                    "claim_status": claim["claim_status"],
                    "result_state": claim["result_state"],
                    "carrier_ids": claim["carrier_ids"],
                    "derivation_ids": derivation_ids,
                }
            )

        if not module["forbidden_promotion_ids"]:
            errors.append(
                f"profile module {module_id}: forbidden_promotion_ids must be explicit"
            )
        plan.append(f"{module_id}: enabled ({len(eligible_claims)} claim(s))")

    output = {
        "compiler_output_version": "1.0",
        "compiler_id": "sofcompiler.compile_v1",
        "manifest_id": manifest["manifest_id"],
        "ir_record_id": ir["record_id"],
        "profile_id": profile["profile_id"],
        "item_type": "ClaimItem_v1 | DegradationItem_v1",
        "items": items,
    }
    return errors, plan, output


def compile_v1(
    manifest: dict,
    ir: dict,
    profile: dict,
    rule_registry: dict,
) -> list[dict]:
    """Return the ordered CompilerItem_v1 list for a valid contract triple."""
    errors, _, output = _compiler_run(manifest, ir, profile, rule_registry)
    if errors:
        raise ValueError("Compile_v1 rejected the contract triple: " + "; ".join(errors))
    return output["items"]


def compile_output_v1(
    manifest: dict,
    ir: dict,
    profile: dict,
    rule_registry: dict,
) -> dict:
    """Return the complete typed CompilerOutput v1.0 envelope."""
    errors, _, output = _compiler_run(manifest, ir, profile, rule_registry)
    if errors:
        raise ValueError("Compile_v1 rejected the contract triple: " + "; ".join(errors))
    output_schema = load_json(COMPILER_OUTPUT_SCHEMA)
    output_errors = schema_errors(output, output_schema)
    if output_errors:
        raise ValueError(
            "Compile_v1 produced an invalid CompilerOutput: "
            + "; ".join(output_errors)
        )
    return output


def profile_errors(
    manifest: dict,
    ir: dict,
    profile: dict,
    rule_registry: dict,
) -> tuple[list[str], list[str]]:
    """Compatibility view used by downstream SOFRS validators."""
    errors, plan, _ = _compiler_run(manifest, ir, profile, rule_registry)
    return errors, plan


def compiler_output_errors(output: dict, expected: dict) -> list[str]:
    if output == expected:
        return []
    return ["Compile_v1 output differs from the committed regression fixture"]


def boundary_regression_errors(
    manifest: dict,
    manifest_schema: dict,
    ir: dict,
    profile: dict,
) -> list[str]:
    errors: list[str] = []

    invalid_space = json.loads(json.dumps(manifest))
    invalid_space["space"]["dimension"] = None
    if not schema_errors(invalid_space, manifest_schema):
        errors.append("strict-space regression: null dimension passed schema")

    invalid_kind = json.loads(json.dumps(manifest))
    invalid_kind["capabilities"]["diagnostic_analogue"] = {
        "availability": "DECLARED",
        "description": "Invalid mixed record.",
        "configuration": {"analogue_mapping_id": "invalid"},
    }
    if not schema_errors(invalid_kind, manifest_schema):
        errors.append("strict-kind regression: diagnostic analogue passed schema")

    closure_module = next(
        module for module in profile["modules"] if module["id"] == "closure"
    )
    closure_only = {"observable_star_closure"}
    if expression_errors(
        closure_only,
        closure_module["capability_requirements"],
    ):
        errors.append("closure any_of regression: one declared closure should admit module")

    if "Theorem" in RESULT_STATUS_MATRIX["CERTIFIED"]:
        errors.append("state matrix regression: CERTIFIED must not admit Theorem")
    if "Theorem" not in RESULT_STATUS_MATRIX["ESTABLISHED"]:
        errors.append("state matrix regression: ESTABLISHED must admit Theorem")

    if not derivation_state_errors("VALID", "Theorem", ["NOT_CHECKED"]):
        errors.append("derivation regression: VALID accepted an unchecked condition")

    associative_module = next(
        module for module in profile["modules"] if module["id"] == "associative"
    )
    route_claim = next(
        claim for claim in ir["claims"] if claim["id"] == "claim.route-audit"
    )
    missing_policy_claim = json.loads(json.dumps(route_claim))
    missing_policy_claim["run_policy_ids"] = []
    capabilities = manifest["capabilities"]
    objects = {obj["id"]: obj for obj in ir["objects"]}
    conventions = {
        convention["id"]: convention for convention in ir["semantic_conventions"]
    }
    policies = {policy["id"]: policy for policy in ir["run_policies"]}
    if not claim_module_requirement_errors(
        missing_policy_claim,
        associative_module,
        capabilities,
        objects,
        conventions,
        policies,
    ):
        errors.append(
            "claim-local policy regression: a claim borrowed global run policies"
        )

    derived_claim = next(
        claim
        for claim in ir["claims"]
        if claim["id"] == "claim.word-in-positive-closure"
    )
    unresolved = json.loads(json.dumps(ir["derivations"][0]))
    unresolved["derivation_state"] = "UNRESOLVED"
    unresolved["condition_checks"][0]["status"] = "NOT_CHECKED"
    if not claim_derivation_errors(
        derived_claim,
        {derived_claim["id"]: [unresolved]},
        {
            rule["id"]: rule
            for rule in load_json(DEFAULT_RULE_REGISTRY)["rules"]
        },
    ):
        errors.append(
            "claim-local derivation regression: unresolved derivation was emitted"
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--ir", type=Path, default=DEFAULT_IR)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument(
        "--rule-registry",
        type=Path,
        default=DEFAULT_RULE_REGISTRY,
    )
    parser.add_argument(
        "--compiler-output",
        type=Path,
        default=DEFAULT_COMPILER_OUTPUT,
    )
    parser.add_argument(
        "--write-compiler-output",
        action="store_true",
        help="write the compiled output fixture instead of comparing it",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payloads = {
        "manifest": load_json(args.manifest),
        "ir": load_json(args.ir),
        "profile": load_json(args.profile),
    }
    rule_registry = load_json(args.rule_registry)
    loaded_schemas = {
        contract_name: load_json(schema_path)
        for contract_name, schema_path in SCHEMAS.items()
    }
    compiler_output_schema = load_json(COMPILER_OUTPUT_SCHEMA)
    errors: list[str] = []

    for contract_name, schema_path in SCHEMAS.items():
        schema = loaded_schemas[contract_name]
        Draft202012Validator.check_schema(schema)
        current_errors = schema_errors(payloads[contract_name], schema)
        if current_errors:
            errors.extend(
                f"{contract_name} schema: {error}" for error in current_errors
            )
        else:
            print(f"PASS {contract_name} schema: {schema_path.name}")
    Draft202012Validator.check_schema(compiler_output_schema)
    print(f"PASS compiler output schema: {COMPILER_OUTPUT_SCHEMA.name}")

    if not errors:
        errors.extend(manifest_errors(payloads["manifest"]))
        errors.extend(
            ir_reference_errors(
                payloads["manifest"],
                payloads["ir"],
                rule_registry,
            )
        )
        profile_validation_errors, plan, compiler_output = _compiler_run(
            payloads["manifest"],
            payloads["ir"],
            payloads["profile"],
            rule_registry,
        )
        errors.extend(profile_validation_errors)
        if not profile_validation_errors:
            errors.extend(
                f"compiler output schema: {error}"
                for error in schema_errors(compiler_output, compiler_output_schema)
            )
            if args.write_compiler_output:
                args.compiler_output.write_text(
                    json.dumps(compiler_output, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                print(f"WROTE compiler output: {args.compiler_output}")
            elif not args.compiler_output.exists():
                errors.append(
                    f"compiler output fixture is missing: {args.compiler_output}"
                )
            else:
                fixture = load_json(args.compiler_output)
                errors.extend(
                    f"compiler output fixture schema: {error}"
                    for error in schema_errors(fixture, compiler_output_schema)
                )
                errors.extend(
                    compiler_output_errors(
                        compiler_output,
                        fixture,
                    )
                )
        errors.extend(
            boundary_regression_errors(
                payloads["manifest"],
                loaded_schemas["manifest"],
                payloads["ir"],
                payloads["profile"],
            )
        )
        for item in plan:
            print(f"PROFILE {item}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        raise SystemExit(f"{len(errors)} SOF compiler contract error(s).")

    print("PASS cross-contract references, evidence, and semantic admission")
    print("PASS Boolean profile gates and boundary regressions")
    print("PASS typed Compile_v1 output regression")
    print(
        "Validated Capability Manifest, Typed SOF IR, Report Profile, and "
        "Compiler Output v1.0."
    )


if __name__ == "__main__":
    main()
