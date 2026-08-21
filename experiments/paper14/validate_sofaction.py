"""Validate Paper XIV SOF Action Objects and their Paper XIII source closure."""

from __future__ import annotations

import argparse
from enum import Enum
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from urllib.parse import unquote

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_SCHEMA = ROOT / "schemas" / "sofaction" / "v2.0.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "sofaction" / "validation-receipt-v2.0.schema.json"
PUBLISHED_RELEASE_COMMIT = "c58633494257757e3316f31d8a7cfedc2e75af4e"

# The current tree may carry successor artifacts at a v2.0 URI. Historical
# SOFAction records therefore resolve their declared digest through the pinned
# release snapshot instead of treating the materialized path as authoritative.
from schemas.release_snapshot import resolve_release_reference


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _repo_reference(path: Path) -> dict[str, Any]:
    return {
        "uri": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "digest": {"algorithm": "sha256", "value": _sha256(path)},
    }


def _closure_digest(ordered_artifacts: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "algorithm": "sha256",
        "value": hashlib.sha256(_canonical_json_bytes(ordered_artifacts)).hexdigest(),
    }


def _release_blob_digest(uri: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{PUBLISHED_RELEASE_COMMIT}:{uri}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return hashlib.sha256(completed.stdout).hexdigest()


def _digest_matches_current_or_release(uri: str, expected: str) -> bool:
    path = ROOT / uri
    if path.is_file() and _sha256(path) == expected:
        return True
    return _release_blob_digest(uri) == expected


def _artifact_reference_errors(reference: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    uri = reference.get("uri", "")
    if not isinstance(uri, str) or not uri.startswith("artifact://"):
        return [f"{label}: artifact URI is not repository-addressable"]
    relative = unquote(uri.removeprefix("artifact://"))
    expected = reference.get("digest", {}).get("value")
    if not _digest_matches_current_or_release(relative, expected):
        errors.append(f"{label}: artifact digest matches neither the current file nor the frozen v2.0 release")
    return errors


def _evidence_reference_errors(
    references: list[dict[str, Any]], source_audit: dict[str, Any], label: str
) -> list[str]:
    errors: list[str] = []
    for index, reference in enumerate(references):
        item_label = f"{label} evidence {index}"
        if "audit_id" in reference:
            if (
                reference.get("audit_id") != source_audit.get("audit_id")
                or reference.get("digest") != source_audit.get("digest")
                or reference.get("validation_receipt") != source_audit.get("validation_receipt")
            ):
                errors.append(f"{item_label}: audit evidence does not bind the source audit closure")
        else:
            errors.extend(_artifact_reference_errors(reference, item_label))
    return errors


def validation_errors(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _source_closure_path(reference: dict[str, Any]) -> Path | None:
    artifact = reference.get("artifact")
    if not isinstance(artifact, str):
        return None
    try:
        return resolve_release_reference(
            {"uri": artifact, "digest": reference.get("digest", {})},
            repository_root=ROOT,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _audit_path(payload: dict[str, Any]) -> Path | None:
    return _source_closure_path(payload.get("source_audit", {}))


def _policy_semantic_errors(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rules = policy.get("rules", [])
    rule_ids = [rule.get("rule_id") for rule in rules]
    rule_id_set = set(rule_ids)
    if len(rule_ids) != len(rule_id_set):
        errors.append("PolicyProfile rule IDs must be unique")
    edges = policy.get("precedence_edges", [])
    graph = {rule_id: [] for rule_id in rule_id_set}
    for edge in edges:
        before, after = edge.get("before"), edge.get("after")
        if before not in rule_id_set or after not in rule_id_set:
            errors.append("PolicyProfile precedence edge references an unknown rule")
        elif before == after:
            errors.append("PolicyProfile precedence contains a self-cycle")
        else:
            graph[before].append(after)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(rule_id: str) -> bool:
        if rule_id in visiting:
            return False
        if rule_id in visited:
            return True
        visiting.add(rule_id)
        ok = all(visit(child) for child in graph.get(rule_id, []))
        visiting.remove(rule_id)
        visited.add(rule_id)
        return ok

    if any(not visit(rule_id) for rule_id in rule_id_set):
        errors.append("PolicyProfile precedence contains a cycle")
    for exception in policy.get("exceptions", []):
        covered = exception.get("overrides_rule_ids", [])
        if not covered:
            errors.append(f"{exception.get('exception_id')}: exception must cover at least one rule")
        elif not set(covered) <= rule_id_set:
            errors.append(f"{exception.get('exception_id')}: exception covers an unknown rule")
    for index, first in enumerate(rules):
        for second in rules[index + 1:]:
            if first.get("when") == second.get("when"):
                if (
                    first.get("assessment_kind") != second.get("assessment_kind")
                    or set(first.get("allowed_dispositions", [])) != set(second.get("allowed_dispositions", []))
                ):
                    errors.append("PolicyProfile contains conflicting rules")
    candidate_families = set(policy.get("candidate_families", []))
    for rule in rules:
        positive = set(rule.get("allowed_dispositions", [])) & {
            "Investigate", "RequestEvidence", "Mitigate", "Rollback", "Escalate"
        }
        if not positive <= candidate_families:
            errors.append("PolicyProfile rule emits a disposition outside candidate_families")
    return errors


class _TruthValue(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNRESOLVED = "UNRESOLVED"


def _uncertain_truth(policy: dict[str, Any], key: str) -> _TruthValue:
    return (
        _TruthValue.FALSE
        if policy.get("uncertainty_policy", {}).get(key) == "non_satisfying"
        else _TruthValue.UNRESOLVED
    )


def _evaluate_predicate(
    predicate: dict[str, Any], audit: dict[str, Any], coordinate_id: str,
    coordinate: dict[str, Any], context: dict[str, Any], policy: dict[str, Any]
) -> _TruthValue:
    """Independent evaluator for Policy Predicate Language v1.0."""

    if predicate.get("predicate_version") != "1.0":
        return _TruthValue.UNRESOLVED
    op = predicate.get("op")
    if op == "all":
        values = [_evaluate_predicate(item, audit, coordinate_id, coordinate, context, policy) for item in predicate.get("args", [])]
        if _TruthValue.FALSE in values:
            return _TruthValue.FALSE
        return _TruthValue.UNRESOLVED if _TruthValue.UNRESOLVED in values else _TruthValue.TRUE
    if op == "any":
        values = [_evaluate_predicate(item, audit, coordinate_id, coordinate, context, policy) for item in predicate.get("args", [])]
        if _TruthValue.TRUE in values:
            return _TruthValue.TRUE
        return _TruthValue.UNRESOLVED if _TruthValue.UNRESOLVED in values else _TruthValue.FALSE
    if op == "not":
        value = _evaluate_predicate(predicate["args"][0], audit, coordinate_id, coordinate, context, policy)
        if value == _TruthValue.UNRESOLVED:
            return value
        return _TruthValue.FALSE if value == _TruthValue.TRUE else _TruthValue.TRUE
    target_id = predicate.get("coordinate_id")
    target = coordinate if target_id == "*" else audit.get("coordinates", {}).get(target_id)
    if op == "coordinate_exists":
        return _TruthValue.TRUE if target is not None else _TruthValue.FALSE
    if op == "coordinate_state_is":
        if target is None:
            return _uncertain_truth(policy, "unavailable_coordinate")
        state = target.get("comparison_state") if isinstance(target, dict) else None
        return _TruthValue.TRUE if state == predicate.get("value") else _TruthValue.FALSE
    if isinstance(target, dict):
        key = {
            "NOT_DECLARED": "not_declared",
            "INCOMPARABLE": "incomparable",
            "NOT_APPLICABLE": "unavailable_coordinate",
            "UNRESOLVED": "unresolved_predicate",
        }.get(target.get("comparison_state"))
        if key is not None:
            return _uncertain_truth(policy, key)
    elif op.startswith("coordinate_"):
        return _uncertain_truth(policy, "unavailable_coordinate")
    if op == "coordinate_carrier_is":
        matches = isinstance(target, dict) and target.get("carrier", target.get("coordinate_family")) == predicate.get("value")
        return _TruthValue.TRUE if matches else _TruthValue.FALSE
    if op == "coordinate_relation_is":
        matches = isinstance(target, dict) and (
            target.get("relation") or target.get("value", {}).get("relation")
        ) == predicate.get("value")
        return _TruthValue.TRUE if matches else _TruthValue.FALSE
    if op == "comparison_role_is":
        return _TruthValue.TRUE if context.get("comparison_role") == predicate.get("value") else _TruthValue.FALSE
    if op == "contract_status_is":
        return _TruthValue.TRUE if context.get("contract_status") == predicate.get("value") else _TruthValue.FALSE
    if op == "authority_status_in":
        return _TruthValue.TRUE if context.get("authority", {}).get("status") in predicate.get("values", []) else _TruthValue.FALSE
    if op == "uncertainty_status_is":
        if "uncertainty_status" not in context:
            return _TruthValue.UNRESOLVED
        return _TruthValue.TRUE if context.get("uncertainty_status") == predicate.get("value") else _TruthValue.FALSE
    if op == "transformation_contract_present":
        return _TruthValue.TRUE if context.get("transformation_contract_refs") else _TruthValue.FALSE
    if op == "context_constraint_has_status":
        matches = any(item.get("constraint_id") == predicate.get("constraint_id") and item.get("status") == predicate.get("value") for item in context.get("constraints", []))
        return _TruthValue.TRUE if matches else _TruthValue.FALSE
    if op == "policy_basis_present":
        return _TruthValue.TRUE if policy.get("normative_basis") else _TruthValue.FALSE
    return _TruthValue.UNRESOLVED


def _select_policy_rule(
    policy: dict[str, Any], audit: dict[str, Any], coordinate_id: str,
    coordinate: dict[str, Any], context: dict[str, Any]
) -> tuple[dict[str, Any] | None, bool]:
    """Independently require one precedence-dominant matching rule."""

    rules = {rule.get("rule_id"): rule for rule in policy.get("rules", [])}
    suppressed: set[str] = set()
    for exception in policy.get("exceptions", []):
        if _evaluate_predicate(exception.get("when", {}), audit, coordinate_id, coordinate, context, policy) == _TruthValue.TRUE:
            suppressed.update(exception.get("overrides_rule_ids", []))
    matching = {
        rule_id for rule_id, rule in rules.items()
        if rule_id not in suppressed
        and _evaluate_predicate(rule.get("when", {}), audit, coordinate_id, coordinate, context, policy) == _TruthValue.TRUE
    }
    if not matching:
        return None, False
    graph = {rule_id: set() for rule_id in rules}
    for edge in policy.get("precedence_edges", []):
        if edge.get("before") in graph and edge.get("after") in graph:
            graph[edge["before"]].add(edge["after"])

    def reaches(start: str, target: str) -> bool:
        pending = list(graph[start])
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current == target:
                return True
            if current not in visited:
                visited.add(current)
                pending.extend(graph[current])
        return False

    dominant = [
        rule_id for rule_id in matching
        if all(rule_id == other or reaches(rule_id, other) for other in matching)
    ]
    if len(dominant) != 1:
        return None, True
    return rules[dominant[0]], False


def _check_disposition_result(
    result: dict[str, Any],
    interpretations: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    chain_admitted: bool,
    errors: list[str],
) -> None:
    kind = result.get("kind")
    action_ids = {action.get("action_id") for action in actions}
    result_action_ids = set(result.get("candidate_action_ids", []))
    if result_action_ids != action_ids:
        errors.append("disposition_result candidate IDs must equal CandidateAction IDs")
    unavailable = any(
        ref.get("comparison_state") in {"UNRESOLVED", "NOT_DECLARED", "INCOMPARABLE", "NOT_APPLICABLE"}
        for item in interpretations
        for ref in item.get("audit_coordinate_refs", [])
    )
    inconclusive = any(
        item.get("assessment_kind") in {"evidence_insufficient", "policy_conflict", "inconclusive"}
        for item in interpretations
    )
    no_action_ids = {
        item.get("interpretation_id")
        for item in interpretations
        if "NoAction" in item.get("supported_dispositions", [])
    }
    result_interpretation_ids = set(result.get("interpretation_ids", []))
    if kind == "no_disposition" and (interpretations or actions):
        errors.append("no_disposition requires empty Interpretation and Candidate Action sets")
    if kind == "unresolved_disposition" and (not chain_admitted or not (unavailable or inconclusive) or actions):
        errors.append("unresolved_disposition requires an admitted chain, inconclusive evidence, and no actions")
    if kind == "no_action_disposition" and (unavailable or actions or not no_action_ids):
        errors.append("no_action_disposition requires explicit policy-supported NoAction without unavailable coordinates")
    if kind == "candidate_action_set" and not actions:
        errors.append("candidate_action_set requires at least one CandidateAction")
    if kind == "no_action_disposition" and not result_interpretation_ids <= no_action_ids:
        errors.append("no_action_disposition references an interpretation without NoAction support")


def contract_errors(
    payload: dict[str, Any], *, expected_sofaudit_version: str = "2.0"
) -> list[str]:
    errors: list[str] = []
    source_ref = payload.get("source_audit", {})
    path = _audit_path(payload)
    if path is None:
        errors.append(f"source audit artifact does not exist: {source_ref.get('artifact')}")
        return errors

    source = json.loads(path.read_text(encoding="utf-8"))
    if source.get("sofaudit_version") != expected_sofaudit_version:
        errors.append(f"source audit must be SOFAUDIT {expected_sofaudit_version}")
    if source_ref.get("audit_id") != source.get("audit_id"):
        errors.append("source_audit.audit_id does not match source artifact")
    actual_digest = _sha256(path)
    if source_ref.get("digest", {}).get("value") != actual_digest:
        errors.append("source_audit digest does not match source artifact")
    receipt_ref = source_ref.get("validation_receipt", {})
    receipt_path = _source_closure_path(receipt_ref)
    if not receipt_ref or receipt_path is None or not receipt_path.is_file():
        errors.append("source_audit must bind an existing Paper XIII validation receipt")
    else:
        receipt_digest = _sha256(receipt_path)
        if receipt_ref.get("digest", {}).get("value") != receipt_digest:
            errors.append("source_audit validation receipt digest does not match artifact")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("receipt_id") != receipt_ref.get("receipt_id"):
            errors.append("source_audit validation receipt ID does not match artifact")
        validator = receipt.get("validator", {})
        if validator.get("validator_id") != receipt_ref.get("validator_id") or validator.get("validator_version") != receipt_ref.get("validator_version"):
            errors.append("source_audit validation receipt validator identity does not match artifact")
        if receipt.get("status") != "PASS":
            errors.append("source_audit validation receipt does not record PASS")
        receipt_audit = receipt.get("audit", {})
        if receipt_audit.get("audit_id") != source.get("audit_id"):
            errors.append("source_audit validation receipt binds a different audit ID")
        if receipt_audit.get("artifact", {}).get("digest", {}).get("value") != actual_digest:
            errors.append("source_audit validation receipt binds a different audit digest")

    projection = payload.get("audit_projection", {})
    if projection.get("audit_id") != source.get("audit_id"):
        errors.append("audit_projection.audit_id does not match source artifact")
    if projection.get("signature") != source.get("coordinates"):
        errors.append("AuditProjection does not preserve the Paper XIII coordinate map under decoded-object equality")
    if _canonical_json_bytes(projection.get("signature")) != _canonical_json_bytes(source.get("coordinates")):
        errors.append("AuditProjection does not preserve the canonical JSON encoding of the Paper XIII coordinate map")
    if "post_action_observation" in payload or "post_action_observations" in payload:
        errors.append("post-action observations cannot be embedded in a canonical SOFActionObject")

    record_class = payload.get("record_class")
    record_basis = payload.get("record_basis", {})
    expected_basis = {
        "policy_conformance_certificate": "protocol_trace",
        "decision_trace_certificate": "protocol_trace",
    }.get(record_class)
    if expected_basis and record_basis.get("basis_kind") != expected_basis:
        errors.append("record_class and record_basis are incompatible")
    if record_class not in {"policy_conformance_certificate", "decision_trace_certificate"}:
        errors.append("SOFAction v2 reserves outcome, effect, authorization, and selected-plan records for separate contracts")
    if payload.get("claim_status") != "Computational Certificate":
        errors.append("current SOFAction v2 record classes require Computational Certificate status")

    context_admission = payload.get("context_admission", {})
    policy_admission = payload.get("policy_admission", {})
    context = payload.get("action_context")
    policy = payload.get("policy_profile")
    interpretations = payload.get("interpretation_records", [])
    actions = payload.get("candidate_action_set", {}).get("actions", [])

    context_admitted = context_admission.get("status") == "admitted"
    policy_admitted = policy_admission.get("status") == "admitted"
    for label, admission in (("context", context_admission), ("policy", policy_admission)):
        if admission.get("status") == "admitted" and (
            admission.get("contract_validation") != "admitted"
            or admission.get("applicability") != "applicable"
            or admission.get("completeness") != "complete"
            or admission.get("missing_fields")
        ):
            errors.append(f"{label} admission status is inconsistent with its validation, applicability, or completeness")
    if context_admitted and not isinstance(context, dict):
        errors.append("admitted context requires ActionContext")
    if policy_admitted and not isinstance(policy, dict):
        errors.append("admitted policy requires PolicyProfile")
    chain_admitted = context_admitted and policy_admitted
    if not chain_admitted:
        if context is not None or policy is not None:
            errors.append("inconclusive context or policy admission must not retain admitted objects")
        if interpretations or actions:
            errors.append("inconclusive context or policy admission must not emit interpretations or actions")
        _check_disposition_result(payload.get("disposition_result", {}), interpretations, actions, False, errors)
        return errors

    if context.get("scope", {}).get("audit_id") != source.get("audit_id"):
        errors.append("ActionContext scope must identify the source audit")
    if source.get("regime") not in policy.get("applicability", {}).get("regimes", []):
        errors.append("PolicyProfile is not applicable to the source audit regime")
    if context.get("comparison_role") not in policy.get("applicability", {}).get("comparison_roles", []):
        errors.append("PolicyProfile is not applicable to the ActionContext comparison role")

    authority = context.get("authority", {})
    actor_id = context.get("actor", {}).get("actor_id")
    scope_id = context.get("scope", {}).get("scope_id")
    if actor_id not in authority.get("actor_ids", []):
        errors.append("ActionContext actor is outside the declared authority scope")
    if scope_id not in authority.get("scope_ids", []):
        errors.append("ActionContext scope is outside the declared authority scope")
    if context.get("mismatch_direction") != "reference_to_target":
        errors.append("ActionContext mismatch direction must preserve the Paper XIII reference-to-target direction")
    provenance_kind = source.get("provenance", {}).get("kind")
    expected_role = "diagnostic_comparison" if provenance_kind == "migration" else "failure_mode_control"
    if context.get("comparison_role") != expected_role:
        errors.append("ActionContext comparison role is inconsistent with the source audit provenance")
    if context.get("comparison_role") == "legitimate_transformation_control":
        if context.get("contract_status") != "conforming" or not context.get("transformation_contract_refs"):
            errors.append("licensed transformation context requires a bound conforming transformation contract")

    errors.extend(_policy_semantic_errors(policy))
    for index, basis in enumerate(policy.get("normative_basis", [])):
        errors.extend(_artifact_reference_errors(basis.get("source_ref", {}), f"normative basis {index}"))
    for index, reference in enumerate(context.get("transformation_contract_refs", [])):
        errors.extend(_artifact_reference_errors(reference, f"transformation contract {index}"))
    errors.extend(_evidence_reference_errors(record_basis.get("evidence_refs", []), source_ref, "record basis"))
    rules = policy.get("rules", [])
    rule_ids = [rule.get("rule_id") for rule in rules]
    if len(rule_ids) != len(set(rule_ids)):
        errors.append("PolicyProfile rule IDs must be unique")
    known_rule_ids = set(rule_ids)

    source_coordinates = source.get("coordinates", {})
    seen_coordinates: list[str] = []
    interpretation_ids = set()
    for interpretation in interpretations:
        interpretation_id = interpretation.get("interpretation_id")
        if interpretation_id in interpretation_ids:
            errors.append(f"duplicate interpretation ID: {interpretation_id}")
        interpretation_ids.add(interpretation_id)
        errors.extend(_evidence_reference_errors(
            interpretation.get("evidence_refs", []), source_ref, str(interpretation_id)
        ))
        if interpretation.get("context_refs") != [context.get("context_id")]:
            errors.append(f"{interpretation_id}: context reference is not the admitted ActionContext")
        missing_rules = set(interpretation.get("policy_rule_refs", [])) - known_rule_ids
        if missing_rules:
            errors.append(f"{interpretation_id}: unknown policy rules {sorted(missing_rules)}")
        for coordinate_ref in interpretation.get("audit_coordinate_refs", []):
            coordinate_id = coordinate_ref.get("coordinate_id")
            seen_coordinates.append(coordinate_id)
            if coordinate_id not in source_coordinates:
                errors.append(f"{interpretation_id}: unknown audit coordinate {coordinate_id}")
                continue
            actual_state = source_coordinates[coordinate_id].get("comparison_state")
            if coordinate_ref.get("comparison_state") != actual_state:
                errors.append(f"{interpretation_id}: coordinate state was changed")
            actual_carrier = source_coordinates[coordinate_id].get(
                "carrier", source_coordinates[coordinate_id].get("coordinate_family", "unknown")
            )
            if coordinate_ref.get("carrier") != actual_carrier:
                errors.append(f"{interpretation_id}: coordinate carrier was changed")
            matching_rule, policy_conflict = _select_policy_rule(
                policy, source, coordinate_id, source_coordinates[coordinate_id], context
            )
            if matching_rule is None:
                if interpretation.get("policy_rule_refs"):
                    errors.append(f"{interpretation_id}: no declared predicate matches its policy rule reference")
                expected_kind = "policy_conflict" if policy_conflict else "inconclusive"
                if interpretation.get("assessment_kind") != expected_kind:
                    errors.append(f"{interpretation_id}: unmatched predicate must be {expected_kind}")
            else:
                if interpretation.get("policy_rule_refs") != [matching_rule.get("rule_id")]:
                    errors.append(f"{interpretation_id}: policy rule reference is not the first matching predicate")
                if interpretation.get("assessment_kind") != matching_rule.get("assessment_kind"):
                    errors.append(f"{interpretation_id}: assessment kind does not match the first matching predicate")
            assessment_kind = interpretation.get("assessment_kind")
            if assessment_kind == "licensed_change" and not context.get("transformation_contract_refs"):
                errors.append(f"{interpretation_id}: licensed_change requires a transformation contract reference")
            if assessment_kind == "defect_candidate":
                reference_basis = source.get("source_reports", {}).get("reference", {}).get("comparison_role_basis", {}).get("basis_kind")
                if context.get("comparison_role") != "failure_mode_control" or reference_basis == "declared_baseline_only":
                    errors.append(f"{interpretation_id}: defect_candidate cannot be derived from a declared baseline role")
            if actual_state in {"UNRESOLVED", "NOT_DECLARED", "INCOMPARABLE", "NOT_APPLICABLE"}:
                if interpretation.get("supported_dispositions"):
                    errors.append(f"{interpretation_id}: unresolved coordinate supports a disposition")
                if interpretation.get("assessment_kind") not in {"evidence_insufficient", "inconclusive"}:
                    errors.append(f"{interpretation_id}: unresolved coordinate must be evidence-insufficient or inconclusive")

    if sorted(seen_coordinates) != sorted(source_coordinates):
        errors.append("interpretation records must cover each source coordinate exactly once")

    if payload.get("candidate_action_set", {}).get("count") != len(actions):
        errors.append("candidate_action_set.count must equal the number of actions")
    action_ids = [action.get("action_id") for action in actions]
    if len(action_ids) != len(set(action_ids)):
        errors.append("candidate action IDs must be unique")
    candidate_dispositions = {"Investigate", "RequestEvidence", "Mitigate", "Rollback", "Escalate"}
    expected_action_ids = {
        f"{disposition.lower()}:{item['audit_coordinate_refs'][0]['coordinate_id']}"
        for item in interpretations
        for disposition in item.get("supported_dispositions", [])
        if disposition in candidate_dispositions and item.get("audit_coordinate_refs")
    }
    if set(action_ids) != expected_action_ids:
        errors.append("Candidate Action Set does not equal the independently regenerated policy-supported set")
    interpretation_by_id = {item.get("interpretation_id"): item for item in interpretations}
    for action in actions:
        action_id = action.get("action_id")
        errors.extend(_evidence_reference_errors(action.get("evidence_refs", []), source_ref, str(action_id)))
        support_ids = set(action.get("supported_by_interpretations", []))
        if not support_ids or not support_ids <= set(interpretation_by_id):
            errors.append(f"{action_id}: action support must reference interpretations")
            continue
        if action.get("context_ref") != context.get("context_id"):
            errors.append(f"{action_id}: action context reference is not the admitted context")
        action_carrier = action.get("carrier")
        for ref in action.get("audit_coordinate_refs", []):
            if ref.get("carrier") != action_carrier:
                errors.append(f"{action_id}: candidate carrier does not match its coordinate carrier")
        if not set(action.get("policy_rule_refs", [])) <= known_rule_ids:
            errors.append(f"{action_id}: action references an unknown policy rule")
        supporting = [interpretation_by_id[item] for item in support_ids]
        allowed = set().union(*(set(item.get("supported_dispositions", [])) for item in supporting))
        if action.get("disposition") not in allowed:
            errors.append(f"{action_id}: disposition is not allowed by its interpretation")
        for interpretation in supporting:
            for ref in interpretation.get("audit_coordinate_refs", []):
                state = ref.get("comparison_state")
                if state in {"UNRESOLVED", "NOT_DECLARED", "INCOMPARABLE", "NOT_APPLICABLE"}:
                    errors.append(f"{action_id}: action is supported by an unavailable coordinate")

    _check_disposition_result(
        payload.get("disposition_result", {}), interpretations, actions, chain_admitted, errors
    )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--write-receipts",
        action="store_true",
        help="disabled for the immutable v2.0 release corpus",
    )
    return parser.parse_args()


def build_validation_receipt(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    errors = validation_errors(payload, schema) + contract_errors(payload)
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))

    source_audit = _audit_path(payload)
    source_receipt = _source_closure_path(
        payload["source_audit"]["validation_receipt"]
    )
    if source_audit is None or source_receipt is None:
        raise ValueError(f"{path}: source audit closure cannot be resolved")
    ordered_artifacts = [
        {"role": "action", "artifact": _repo_reference(path)},
        {"role": "source-audit", "artifact": _repo_reference(source_audit)},
        {
            "role": "source-audit-validation-receipt",
            "artifact": _repo_reference(source_receipt),
        },
    ]
    policy = payload.get("policy_profile") or {}
    for index, basis in enumerate(policy.get("normative_basis", [])):
        uri = basis["source_ref"]["uri"]
        basis_path = ROOT / unquote(uri.removeprefix("artifact://"))
        ordered_artifacts.append(
            {
                "role": f"normative-basis-{index}",
                "artifact": _repo_reference(basis_path),
            }
        )
    ordered_artifacts.extend(
        [
            {"role": "validator-implementation", "artifact": _repo_reference(Path(__file__))},
            {"role": "validation-receipt-contract", "artifact": _repo_reference(RECEIPT_SCHEMA)},
        ]
    )
    receipt = {
        "receipt_version": "2.0",
        "artifact_type": "sofaction_validation_receipt",
        "receipt_id": f"receipt.{payload['action_record_id']}.sofaction-v2",
        "action": {
            "action_record_id": payload["action_record_id"],
            "sofaction_version": "2.0",
            "artifact": ordered_artifacts[0]["artifact"],
        },
        "validator": {
            "validator_id": "paper14.sofaction-validator.v2",
            "validator_version": "2.0",
            "implementation": next(
                item["artifact"]
                for item in ordered_artifacts
                if item["role"] == "validator-implementation"
            ),
            "receipt_contract": next(
                item["artifact"]
                for item in ordered_artifacts
                if item["role"] == "validation-receipt-contract"
            ),
        },
        "artifact_closure": {
            "artifact_count": len(ordered_artifacts),
            "ordered_artifacts": ordered_artifacts,
            "closure_digest": _closure_digest(ordered_artifacts),
        },
        "status": "PASS",
        "checks": [
            {"check_id": check_id, "status": "PASS"}
            for check_id in (
                "schema-validation",
                "artifact-digest-closure",
                "action-context-policy-admission",
                "audit-projection-preservation",
                "predicate-replay",
                "candidate-set-regeneration",
                "disposition-closure",
                "authorization-boundary",
            )
        ],
        "negative_boundaries": [
            "This receipt establishes interpretation and candidate-set protocol conformance only; it does not establish policy correctness, action feasibility, authorization, or causal effect."
        ],
    }
    receipt_errors = validation_errors(
        receipt, json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    )
    if receipt_errors:
        raise ValueError("invalid SOFAction validation receipt: " + "; ".join(receipt_errors))
    return receipt


def validation_receipt_errors(receipt: dict[str, Any]) -> list[str]:
    errors = validation_errors(
        receipt, json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    )
    closure = receipt.get("artifact_closure", {})
    ordered = closure.get("ordered_artifacts", [])
    if closure.get("artifact_count") != len(ordered):
        errors.append("receipt artifact_count differs from ordered_artifacts")
    if closure.get("closure_digest") != _closure_digest(ordered):
        errors.append("receipt closure_digest is incorrect")
    roles = [item.get("role") for item in ordered]
    if len(roles) != len(set(roles)):
        errors.append("receipt artifact roles are not unique")
    for index, item in enumerate(ordered):
        reference = item.get("artifact", {})
        uri = reference.get("uri", "")
        expected = reference.get("digest", {}).get("value")
        if not _digest_matches_current_or_release(uri, expected):
            errors.append(f"receipt artifact {index} digest matches neither current nor frozen release content")
    role_map = {item.get("role"): item.get("artifact") for item in ordered}
    if receipt.get("action", {}).get("artifact") != role_map.get("action"):
        errors.append("receipt action differs from artifact closure")
    if receipt.get("validator", {}).get("implementation") != role_map.get("validator-implementation"):
        errors.append("receipt validator differs from artifact closure")
    if receipt.get("validator", {}).get("receipt_contract") != role_map.get("validation-receipt-contract"):
        errors.append("receipt contract differs from artifact closure")
    return errors


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    paths = args.paths or sorted((HERE / "results").glob("*.sofaction"))
    if not paths:
        raise SystemExit("No .sofaction artifacts found.")

    failures = 0
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = validation_errors(payload, schema) + contract_errors(payload)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    if failures:
        raise SystemExit(f"{failures} SOF action artifact(s) failed validation.")
    if args.write_receipts:
        raise SystemExit(
            "Paper XIV v2.0 receipts are immutable; v2.1 receipts are emitted "
            "by validate_sofaction_v2_1.py"
        )
    print(f"Validated {len(paths)} SOF action artifact(s).")


if __name__ == "__main__":
    main()
