"""Paper XIV action semantics.

The executable object language is deliberately explicit:

    (AuditSignature, ActionContext, PolicyProfile)
        -> InterpretationRecord -> CandidateAction

The engine preserves the Paper XIII audit projection and never treats a
nonzero coordinate, an unresolved coordinate, or a reference role as an action
instruction. Candidate actions are bounded records, not execution commands.
"""

from __future__ import annotations

from copy import deepcopy
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOFACTION_VERSION = "2.0"
ACTION_CONTEXT_CONTRACT_VERSION = "2.0"
ACTION_CONTEXT_REVISION = "2026-08-07.1"
POLICY_PROFILE_CONTRACT_VERSION = "2.0"
POLICY_PROFILE_REVISION = "paper14-diagnostic-review-r1"
INTERPRETATION_VERSION = "2.0"
CANDIDATE_RULEBOOK_VERSION = "2.0"

# Policy sources are source-addressed artifacts, not free-text authority.
_MANUSCRIPT_PATH = ROOT / "papers" / "paper14" / "Paper XIV.md"
_MANUSCRIPT_DIGEST = hashlib.sha256(_MANUSCRIPT_PATH.read_bytes()).hexdigest()
POLICY_SOURCE_REF = {
    "artifact_id": "paper14-manuscript",
    "role": "policy_source",
    "uri": "artifact://papers/paper14/Paper%20XIV.md",
    "digest": {"algorithm": "sha256", "value": _MANUSCRIPT_DIGEST},
    "producer": "RIME Paper XIV",
    "contract_version": "2.0",
}

DISPOSITIONS = (
    "NoAction",
    "Investigate",
    "RequestEvidence",
    "Mitigate",
    "Rollback",
    "Escalate",
    "Unresolved",
)
CANDIDATE_DISPOSITIONS = (
    "Investigate",
    "RequestEvidence",
    "Mitigate",
    "Rollback",
    "Escalate",
)

REQUIRED_CONTEXT_FIELDS = (
    "context_id",
    "context_contract_version",
    "context_revision",
    "actor",
    "scope",
    "objective",
    "constraints",
    "time",
    "authority",
    "uncertainty_conditions",
    "comparison_role",
    "mismatch_direction",
    "contract_status",
    "evaluator_qualification_note",
    "transformation_contract_refs",
)

DEFAULT_POLICY_PROFILE: dict[str, Any] = {
    "policy_id": "paper14-diagnostic-review",
    "policy_contract_version": POLICY_PROFILE_CONTRACT_VERSION,
    "policy_revision": POLICY_PROFILE_REVISION,
    "applicability": {
        "regimes": ["strict_vs_strict", "strict_vs_analogue", "analogue_vs_analogue"],
        "comparison_roles": [
            "failure_mode_control",
            "legitimate_transformation_control",
            "model_comparison",
            "diagnostic_comparison",
        ],
    },
    "normative_basis": [
        {
            "basis_id": "difference-is-not-defect",
            "statement": "An audit difference is not by itself a defect, severity, or action.",
            "source_ref": deepcopy(POLICY_SOURCE_REF),
        },
        {
            "basis_id": "unresolved-blocks-action",
            "statement": "UNRESOLVED and NOT_DECLARED coordinates cannot support affirmative actions.",
            "source_ref": deepcopy(POLICY_SOURCE_REF),
        },
    ],
    "rules": [
        {
            "rule_id": "unresolved-coordinate-no-action",
            "when": {"predicate_version": "1.0", "op": "any", "args": [
                {"predicate_version": "1.0", "op": "coordinate_state_is", "coordinate_id": "*", "value": state}
                for state in ("UNRESOLVED", "NOT_DECLARED", "INCOMPARABLE", "NOT_APPLICABLE")
            ]},
            "assessment_kind": "evidence_insufficient",
            "assessment_note": "Unavailable comparison coordinates cannot support affirmative action.",
            "uncertainty_status": "unresolved",
            "allowed_dispositions": [],
            "negative_boundary": [
                "Missing or unresolved comparison evidence cannot support an affirmative action."
            ],
        },
        {
            "rule_id": "licensed-change-is-not-defect",
            "when": {"predicate_version": "1.0", "op": "all", "args": [
                {"predicate_version": "1.0", "op": "any", "args": [
                    {"predicate_version": "1.0", "op": "coordinate_state_is", "coordinate_id": "*", "value": state}
                    for state in ("ALIGNED", "MISMATCH")
                ]},
                {"predicate_version": "1.0", "op": "comparison_role_is", "value": "legitimate_transformation_control"},
                {"predicate_version": "1.0", "op": "contract_status_is", "value": "conforming"},
                {"predicate_version": "1.0", "op": "transformation_contract_present"}
            ]},
            "assessment_kind": "licensed_change",
            "assessment_note": "The declared transformation contract licenses the retained change.",
            "uncertainty_status": "bounded",
            "allowed_dispositions": ["NoAction", "Investigate"],
            "negative_boundary": [
                "Conformance licenses the declared change but does not establish domain-wide correctness."
            ],
        },
        {
            "rule_id": "certified-mismatch-requires-review",
            "when": {"predicate_version": "1.0", "op": "coordinate_state_is", "coordinate_id": "*", "value": "MISMATCH"},
            "assessment_kind": "defect_candidate",
            "assessment_note": "A mismatch is a policy-relative review status, not a certified defect.",
            "uncertainty_status": "bounded",
            "allowed_dispositions": ["Investigate", "RequestEvidence"],
            "negative_boundary": [
                "A defect candidate is a policy-relative review status, not a certified defect."
            ],
        },
        {
            "rule_id": "aligned-coordinate-no-action",
            "when": {"predicate_version": "1.0", "op": "coordinate_state_is", "coordinate_id": "*", "value": "ALIGNED"},
            "assessment_kind": "no_action_indicated",
            "assessment_note": "Equality on the requested coordinate indicates no action under this policy.",
            "uncertainty_status": "bounded",
            "allowed_dispositions": ["NoAction"],
            "negative_boundary": [
                "Equality on the requested coordinate does not establish global equivalence or safety."
            ],
        },
    ],
    "exceptions": [],
    "precedence_edges": [
        {"before": "unresolved-coordinate-no-action", "after": "licensed-change-is-not-defect"},
        {"before": "licensed-change-is-not-defect", "after": "certified-mismatch-requires-review"},
        {"before": "certified-mismatch-requires-review", "after": "aligned-coordinate-no-action"},
    ],
    "uncertainty_policy": {
        "version": "1.0",
        "unresolved_predicate": "propagate_unresolved",
        "unavailable_coordinate": "non_satisfying",
        "not_declared": "propagate_unresolved",
        "incomparable": "propagate_unresolved",
        "rule_conflict": "unresolved_disposition",
        "no_applicable_rule": "no_disposition",
    },
    "candidate_families": list(CANDIDATE_DISPOSITIONS),
    "selection_status": "downstream",
}


def _nonempty(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def admit_action_context(context: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    supplied = context if isinstance(context, dict) else {}
    empty_allowed = {"transformation_contract_refs"}
    missing = [
        field for field in REQUIRED_CONTEXT_FIELDS
        if field not in supplied or (field not in empty_allowed and not _nonempty(supplied.get(field)))
    ]
    if supplied.get("context_contract_version") not in {None, ACTION_CONTEXT_CONTRACT_VERSION}:
        missing.append("supported_context_version")
    if missing:
        return (
            {
                "status": "inconclusive",
                "contract_validation": "rejected",
                "applicability": "unresolved",
                "completeness": "incomplete",
                "missing_fields": sorted(set(missing)),
                "rationale": "ActionContext is incomplete or uses an unsupported version.",
            },
            None,
        )
    return (
        {
            "status": "admitted",
            "contract_validation": "admitted",
            "applicability": "applicable",
            "completeness": "complete",
            "missing_fields": [],
            "rationale": "All required ActionContext fields were explicitly declared.",
        },
        deepcopy(supplied),
    )


def admit_policy_profile(
    policy: dict[str, Any] | None,
    audit: dict[str, Any],
    context: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    supplied = policy if isinstance(policy, dict) else {}
    required = (
        "policy_id", "policy_contract_version", "policy_revision", "applicability", "normative_basis",
        "rules", "exceptions", "precedence_edges", "uncertainty_policy", "candidate_families", "selection_status",
    )
    empty_allowed = {"exceptions", "precedence_edges", "candidate_families"}
    missing = [
        field
        for field in required
        if field not in supplied or (field not in empty_allowed and not _nonempty(supplied.get(field)))
    ]
    if supplied.get("policy_contract_version") not in {None, POLICY_PROFILE_CONTRACT_VERSION}:
        missing.append("supported_policy_version")
    applicability = supplied.get("applicability") if isinstance(supplied.get("applicability"), dict) else {}
    regime = audit.get("regime")
    role = context.get("comparison_role") if isinstance(context, dict) else None
    not_applicable: list[str] = []
    if regime not in applicability.get("regimes", []):
        not_applicable.append("applicable_regime")
    if role not in applicability.get("comparison_roles", []):
        not_applicable.append("applicable_comparison_role")
    if missing:
        return (
            {
                "status": "inconclusive",
                "contract_validation": "rejected",
                "applicability": "unresolved",
                "completeness": "incomplete",
                "missing_fields": sorted(set(missing)),
                "rationale": "PolicyProfile is incomplete, unsupported, or not applicable.",
            },
            None,
        )
    if not_applicable:
        return (
            {
                "status": "inconclusive",
                "contract_validation": "admitted",
                "applicability": "not_applicable",
                "completeness": "complete",
                "missing_fields": sorted(set(not_applicable)),
                "rationale": "PolicyProfile is valid but does not apply to the declared audit context.",
            },
            None,
        )
    rule_ids = [rule.get("rule_id") for rule in supplied.get("rules", []) if isinstance(rule, dict)]
    rule_id_set = set(rule_ids)
    edges = supplied.get("precedence_edges", [])
    if len(rule_ids) != len(rule_id_set):
        missing.append("unique_rule_ids")
    edge_pairs = {(edge.get("before"), edge.get("after")) for edge in edges if isinstance(edge, dict)}
    if any(before == after for before, after in edge_pairs):
        missing.append("precedence_self_cycle")
    graph = {rule_id: [] for rule_id in rule_id_set}
    for before, after in edge_pairs:
        if before not in rule_id_set or after not in rule_id_set:
            missing.append("precedence_unknown_edge")
        elif after not in graph[before]:
            graph[before].append(after)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(rule_id: str) -> bool:
        if rule_id in visiting:
            return False
        if rule_id in visited:
            return True
        visiting.add(rule_id)
        if any(not visit(child) for child in graph.get(rule_id, [])):
            return False
        visiting.remove(rule_id)
        visited.add(rule_id)
        return True

    if any(not visit(rule_id) for rule_id in rule_id_set):
        missing.append("precedence_cycle")
    exceptions = supplied.get("exceptions", [])
    for exception in exceptions:
        covered = exception.get("overrides_rule_ids", []) if isinstance(exception, dict) else []
        if not covered or not set(covered) <= rule_id_set:
            missing.append("exception_rule_coverage")
    for index, first in enumerate(supplied.get("rules", [])):
        for second in supplied.get("rules", [])[index + 1:]:
            if not isinstance(first, dict) or not isinstance(second, dict):
                continue
            if first.get("when") == second.get("when") and (
                first.get("assessment_kind") != second.get("assessment_kind")
                or set(first.get("allowed_dispositions", [])) != set(second.get("allowed_dispositions", []))
            ):
                missing.append("conflicting_rules")
    candidate_families = set(supplied.get("candidate_families", []))
    for rule in supplied.get("rules", []):
        positive = set(rule.get("allowed_dispositions", [])) & set(CANDIDATE_DISPOSITIONS)
        if not positive <= candidate_families:
            missing.append("rule_disposition_outside_candidate_families")
    if missing:
        return (
            {
                "status": "inconclusive",
                "contract_validation": "rejected",
                "applicability": "unresolved",
                "completeness": "incomplete",
                "missing_fields": sorted(set(missing)),
                "rationale": "PolicyProfile is incomplete, unsupported, or not applicable.",
            },
            None,
        )
    return (
        {
            "status": "admitted",
            "contract_validation": "admitted",
            "applicability": "applicable",
            "completeness": "complete",
            "missing_fields": [],
            "rationale": "PolicyProfile is versioned and applicable to the declared audit context.",
        },
        deepcopy(supplied),
    )


def audit_signature(audit: dict[str, Any]) -> dict[str, Any]:
    """Return the v2 sparse coordinate map, with legacy support for tests."""

    if isinstance(audit.get("coordinates"), dict):
        return audit["coordinates"]
    return audit.get("signature", {})


def _coordinate_state(coordinate: dict[str, Any]) -> str:
    state = coordinate.get("comparison_state")
    if isinstance(state, str):
        return state
    if coordinate.get("wall_record_mismatch") is None:
        return "NOT_DECLARED"
    return "MISMATCH"


class TruthValue(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNRESOLVED = "UNRESOLVED"


def _policy_truth(policy: dict[str, Any], key: str) -> TruthValue:
    setting = policy.get("uncertainty_policy", {}).get(key)
    return (
        TruthValue.FALSE
        if setting == "non_satisfying"
        else TruthValue.UNRESOLVED
    )


def _all(values: list[TruthValue]) -> TruthValue:
    if TruthValue.FALSE in values:
        return TruthValue.FALSE
    if TruthValue.UNRESOLVED in values:
        return TruthValue.UNRESOLVED
    return TruthValue.TRUE


def _any(values: list[TruthValue]) -> TruthValue:
    if TruthValue.TRUE in values:
        return TruthValue.TRUE
    if TruthValue.UNRESOLVED in values:
        return TruthValue.UNRESOLVED
    return TruthValue.FALSE


def _predicate_matches(
    predicate: dict[str, Any],
    *,
    audit: dict[str, Any],
    coordinate_id: str,
    coordinate: dict[str, Any],
    context: dict[str, Any],
    policy: dict[str, Any],
) -> TruthValue:
    """Evaluate the closed Policy Predicate Language v1.0."""

    if predicate.get("predicate_version") != "1.0":
        return TruthValue.UNRESOLVED
    op = predicate.get("op")
    if op == "all":
        return _all([
            _predicate_matches(
                item,
                audit=audit,
                coordinate_id=coordinate_id,
                coordinate=coordinate,
                context=context,
                policy=policy,
            )
            for item in predicate.get("args", [])
        ])
    if op == "any":
        return _any([
            _predicate_matches(
                item,
                audit=audit,
                coordinate_id=coordinate_id,
                coordinate=coordinate,
                context=context,
                policy=policy,
            )
            for item in predicate.get("args", [])
        ])
    if op == "not":
        value = _predicate_matches(
            predicate["args"][0], audit=audit, coordinate_id=coordinate_id,
            coordinate=coordinate, context=context, policy=policy
        )
        if value == TruthValue.UNRESOLVED:
            return value
        return TruthValue.FALSE if value == TruthValue.TRUE else TruthValue.TRUE
    target_id = predicate.get("coordinate_id")
    target = coordinate if target_id == "*" else audit_signature(audit).get(target_id)
    if op == "coordinate_exists":
        return TruthValue.TRUE if target is not None else TruthValue.FALSE
    if op == "coordinate_state_is":
        state = _coordinate_state(target) if isinstance(target, dict) else None
        expected = predicate.get("value")
        if target is None:
            return _policy_truth(policy, "unavailable_coordinate")
        return TruthValue.TRUE if state == expected else TruthValue.FALSE
    if isinstance(target, dict):
        state = _coordinate_state(target)
        policy_key = {
            "NOT_DECLARED": "not_declared",
            "INCOMPARABLE": "incomparable",
            "NOT_APPLICABLE": "unavailable_coordinate",
            "UNRESOLVED": "unresolved_predicate",
        }.get(state)
        if policy_key is not None:
            return _policy_truth(policy, policy_key)
    elif op.startswith("coordinate_"):
        return _policy_truth(policy, "unavailable_coordinate")
    if op == "coordinate_carrier_is":
        matches = isinstance(target, dict) and target.get("carrier", target.get("coordinate_family")) == predicate.get("value")
        return TruthValue.TRUE if matches else TruthValue.FALSE
    if op == "coordinate_relation_is":
        matches = isinstance(target, dict) and (
            target.get("relation") or target.get("value", {}).get("relation")
        ) == predicate.get("value")
        return TruthValue.TRUE if matches else TruthValue.FALSE
    if op == "comparison_role_is":
        return TruthValue.TRUE if context.get("comparison_role") == predicate.get("value") else TruthValue.FALSE
    if op == "contract_status_is":
        return TruthValue.TRUE if context.get("contract_status") == predicate.get("value") else TruthValue.FALSE
    if op == "authority_status_in":
        return TruthValue.TRUE if context.get("authority", {}).get("status") in predicate.get("values", []) else TruthValue.FALSE
    if op == "uncertainty_status_is":
        if "uncertainty_status" not in context:
            return TruthValue.UNRESOLVED
        return TruthValue.TRUE if context.get("uncertainty_status") == predicate.get("value") else TruthValue.FALSE
    if op == "transformation_contract_present":
        return TruthValue.TRUE if context.get("transformation_contract_refs") else TruthValue.FALSE
    if op == "context_constraint_has_status":
        return TruthValue.TRUE if any(
            item.get("constraint_id") == predicate.get("constraint_id")
            and item.get("status") == predicate.get("value")
            for item in context.get("constraints", [])
        ) else TruthValue.FALSE
    if op == "policy_basis_present":
        return TruthValue.TRUE if policy.get("normative_basis") else TruthValue.FALSE
    return TruthValue.UNRESOLVED


def _select_rule(
    policy: dict[str, Any],
    audit: dict[str, Any],
    coordinate_id: str,
    coordinate: dict[str, Any],
    context: dict[str, Any],
) -> tuple[dict[str, Any] | None, bool]:
    rules = {rule.get("rule_id"): rule for rule in policy.get("rules", [])}
    suppressed: set[str] = set()
    for exception in policy.get("exceptions", []):
        if _predicate_matches(
            exception.get("when", {}), audit=audit, coordinate_id=coordinate_id,
            coordinate=coordinate, context=context, policy=policy
        ) == TruthValue.TRUE:
            suppressed.update(exception.get("overrides_rule_ids", []))
    matching = {
        rule_id for rule_id, rule in rules.items()
        if rule_id not in suppressed and isinstance(rule, dict) and _predicate_matches(
            rule.get("when", {}), audit=audit, coordinate_id=coordinate_id,
            coordinate=coordinate, context=context, policy=policy
        ) == TruthValue.TRUE
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


def interpret_signature(
    audit: dict[str, Any],
    action_context: dict[str, Any],
    policy_profile: dict[str, Any],
    evidence_ref: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    context_admission, admitted_context = admit_action_context(action_context)
    policy_admission, admitted_policy = admit_policy_profile(policy_profile, audit, action_context)
    if admitted_context is None or admitted_policy is None:
        raise ValueError(
            "interpretation requires admitted ActionContext and PolicyProfile: "
            + ", ".join(context_admission["missing_fields"] + policy_admission["missing_fields"])
        )

    records: list[dict[str, Any]] = []
    for coordinate_id, coordinate in audit_signature(audit).items():
        if not isinstance(coordinate, dict):
            continue
        state = _coordinate_state(coordinate)
        rule, policy_conflict = _select_rule(admitted_policy, audit, coordinate_id, coordinate, admitted_context)
        if rule is None:
            assessment_kind = "policy_conflict" if policy_conflict else "inconclusive"
            assessment_note = (
                "Multiple matching rules lack a unique precedence-dominant rule."
                if policy_conflict
                else "The declared policy does not authorize an interpretation for this state."
            )
            uncertainty_status = "unresolved"
            dispositions: list[str] = []
            rule_refs: list[str] = []
            negative_boundary = [
                "A policy conflict cannot be resolved by producer declaration order."
                if policy_conflict
                else "No applicable policy rule was found for this coordinate."
            ]
        else:
            assessment_kind = rule["assessment_kind"]
            assessment_note = rule["assessment_note"]
            uncertainty_status = rule["uncertainty_status"]
            dispositions = list(rule.get("allowed_dispositions", []))
            rule_refs = [rule["rule_id"]]
            negative_boundary = list(rule.get("negative_boundary", []))
        carrier = coordinate.get("carrier", coordinate.get("coordinate_family", "unknown"))
        records.append(
            {
                "interpretation_id": f"interp:{audit['audit_id']}:{coordinate_id}",
                "audit_coordinate_refs": [
                    {
                        "coordinate_id": coordinate_id,
                        "comparison_state": state,
                        "carrier": carrier,
                    }
                ],
                "context_refs": [admitted_context["context_id"]],
                "policy_rule_refs": rule_refs,
                "assessment_kind": assessment_kind,
                "assessment_note": assessment_note,
                "uncertainty": {
                    "status": uncertainty_status,
                    "reasons": [] if state in {"ALIGNED", "MISMATCH"} else [
                        f"source comparison state is {state}"
                    ],
                },
                "rationale": assessment_note,
                "supported_dispositions": dispositions,
                "evidence_refs": [deepcopy(evidence_ref)] if evidence_ref is not None else [],
                "negative_boundary": negative_boundary,
            }
        )
    return records


def generate_candidate_actions(
    interpretations: list[dict[str, Any]],
    policy_profile: dict[str, Any],
    action_context: dict[str, Any],
    audit_ref: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(interpretations, list):
        raise ValueError("CandidateAction generation requires InterpretationRecord objects")
    rule_ids = {rule.get("rule_id") for rule in policy_profile.get("rules", [])}
    actions: list[dict[str, Any]] = []
    for interpretation in interpretations:
        for disposition in interpretation.get("supported_dispositions", []):
            if disposition not in CANDIDATE_DISPOSITIONS:
                continue
            coordinate_refs = interpretation["audit_coordinate_refs"]
            coordinate_ids = [ref["coordinate_id"] for ref in coordinate_refs]
            carriers = {ref.get("carrier", "unknown") for ref in coordinate_refs}
            rule_refs = interpretation.get("policy_rule_refs", [])
            if not rule_refs or not set(rule_refs) <= rule_ids:
                raise ValueError("candidate action requires existing policy rule references")
            action_id = f"{disposition.lower()}:{coordinate_ids[0]}"
            if any(item["action_id"] == action_id for item in actions):
                continue
            actions.append(
                {
                    "action_id": action_id,
                    "disposition": disposition,
                    "target": coordinate_ids[0],
                    "carrier": next(iter(carriers)) if len(carriers) == 1 else "mixed",
                    "supported_by_interpretations": [interpretation["interpretation_id"]],
                    "audit_coordinate_refs": coordinate_refs,
                    "context_ref": action_context["context_id"],
                    "policy_rule_refs": rule_refs,
                    "preconditions": [
                        "the source audit projection and coordinate state remain unchanged",
                        "a domain owner confirms the candidate is applicable",
                    ],
                    "intended_diagnostic_consequence": {
                        "status": "intended_diagnostic_consequence",
                        "statements": [
                            "obtain evidence relevant to the declared comparison coordinate"
                        ],
                    },
                    "declared_risk_considerations": [
                        "the candidate may be irrelevant after context or policy review",
                        "an observed post-action change would require a new Paper XIII audit",
                    ],
                    "reversibility": "unknown",
                    "evidence_refs": [audit_ref, *interpretation.get("evidence_refs", [])],
                    "authorization_state": "not_requested",
                    "negative_boundary": [
                        "This is a candidate disposition, not an execution command or correctness claim."
                    ],
                }
            )
    return actions


def build_action_record(
    *,
    action_record_id: str,
    audit: dict[str, Any],
    source_artifact: str,
    action_context: dict[str, Any] | None,
    policy_profile: dict[str, Any] | None,
    claim_note: str = "Policy-relative interpretation with bounded candidate actions",
) -> dict[str, Any]:
    source_path = ROOT / source_artifact
    source_digest = _sha256(source_path) if source_path.is_file() else None
    receipt_ref = _validation_receipt_ref(audit, source_path)
    if receipt_ref is None:
        raise ValueError(f"Paper XIII audit has no source-addressed validation receipt: {audit['audit_id']}")
    audit_ref = {
        "audit_id": audit["audit_id"],
        "artifact": source_artifact.replace("\\", "/"),
        "sofaudit_version": audit.get("sofaudit_version"),
        "digest": {"algorithm": "sha256", "value": source_digest},
        "validation_receipt": receipt_ref,
    }
    context_admission, admitted_context = admit_action_context(action_context)
    policy_admission, admitted_policy = admit_policy_profile(policy_profile, audit, action_context)
    chain_admitted = admitted_context is not None and admitted_policy is not None
    if chain_admitted:
        interpretations = interpret_signature(audit, admitted_context, admitted_policy, audit_ref)
        actions = generate_candidate_actions(interpretations, admitted_policy, admitted_context, audit_ref)
    else:
        interpretations = []
        actions = []

    record: dict[str, Any] = {
        "sofaction_version": SOFACTION_VERSION,
        "record_type": "sofaction",
        "action_record_id": action_record_id,
        "claim_status": "Computational Certificate",
        "record_class": "decision_trace_certificate",
        "claim_note": claim_note,
        "source_audit": audit_ref,
        "audit_projection": {
            "audit_id": audit["audit_id"],
            "signature": deepcopy(audit_signature(audit)),
        },
        "context_admission": context_admission,
        "policy_admission": policy_admission,
        "action_context": admitted_context,
        "policy_profile": admitted_policy,
        "interpretation_records": interpretations,
        "candidate_action_set": {"count": len(actions), "actions": actions},
        "disposition_result": disposition_result(interpretations, actions, chain_admitted),
        "record_basis": {
            "basis_kind": "protocol_trace",
            "evidence_refs": [audit_ref],
            "causal_status": "not_claimed",
            "negative_boundary": [
                "Protocol trace completeness does not establish policy validity or action effectiveness."
            ],
        },
        "failure_modes": [
            "difference is not defect, severity, or action without policy-relative interpretation",
            "candidate actions are not feasibility, causal-effect, safety, or authorization claims",
            "post-action facts require a new Paper XIII audit and cannot rewrite this projection",
        ],
    }
    return record


def disposition_result(
    interpretations: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    chain_admitted: bool,
) -> dict[str, Any]:
    """Keep no disposition, unresolved, no action, and candidate actions distinct."""

    if not chain_admitted:
        return {
            "kind": "no_disposition",
            "reason": "Context or policy admission did not complete.",
            "interpretation_ids": [],
            "candidate_action_ids": [],
        }
    if not interpretations:
        return {
            "kind": "no_disposition",
            "reason": "No audit coordinates were retained for interpretation.",
            "interpretation_ids": [],
            "candidate_action_ids": [],
        }
    unresolved = any(
        ref.get("comparison_state") in {"UNRESOLVED", "NOT_DECLARED", "INCOMPARABLE", "NOT_APPLICABLE"}
        for item in interpretations
        for ref in item.get("audit_coordinate_refs", [])
    ) or any(item.get("assessment_kind") in {"evidence_insufficient", "policy_conflict", "inconclusive"} for item in interpretations)
    if unresolved:
        return {
            "kind": "unresolved_disposition",
            "reason": "At least one retained coordinate is unavailable for affirmative disposition.",
            "interpretation_ids": [item["interpretation_id"] for item in interpretations],
            "candidate_action_ids": [],
        }
    no_action_ids = [
        item["interpretation_id"]
        for item in interpretations
        if "NoAction" in item.get("supported_dispositions", [])
    ]
    if not actions and no_action_ids:
        return {
            "kind": "no_action_disposition",
            "reason": "The applicable policy explicitly supports no action for the retained coordinates.",
            "interpretation_ids": no_action_ids,
            "candidate_action_ids": [],
        }
    if actions:
        return {
            "kind": "candidate_action_set",
            "reason": "The admitted policy supports one or more bounded candidate dispositions.",
            "interpretation_ids": [item["interpretation_id"] for item in interpretations],
            "candidate_action_ids": [item["action_id"] for item in actions],
        }
    return {
        "kind": "unresolved_disposition",
        "reason": "Admitted interpretations did not establish a legal disposition.",
        "interpretation_ids": [item["interpretation_id"] for item in interpretations],
        "candidate_action_ids": [],
    }


def _validation_receipt_ref(audit: dict[str, Any], audit_path: Path) -> dict[str, Any] | None:
    candidates = [
        audit_path.parent / ".." / "receipts" / f"{audit.get('audit_id')}.validation-receipt.json",
        ROOT / "experiments" / "paper13" / "results" / "receipts" / f"{audit.get('audit_id')}.validation-receipt.json",
    ]
    for candidate in candidates:
        candidate = candidate.resolve()
        if not candidate.is_file():
            continue
        receipt = json.loads(candidate.read_text(encoding="utf-8"))
        validator = receipt.get("validator", {})
        return {
            "receipt_id": receipt.get("receipt_id"),
            "artifact": candidate.relative_to(ROOT).as_posix(),
            "digest": {"algorithm": "sha256", "value": _sha256(candidate)},
            "validator_id": validator.get("validator_id"),
            "validator_version": validator.get("validator_version"),
        }
    return None


def signature_summary(audit: dict[str, Any]) -> dict[str, Any]:
    states: dict[str, int] = {}
    for coordinate in audit_signature(audit).values():
        if isinstance(coordinate, dict):
            state = _coordinate_state(coordinate)
            states[state] = states.get(state, 0) + 1
    return {
        "coordinate_count": sum(states.values()),
        "comparison_state_counts": states,
        "audit_id": audit.get("audit_id"),
        "provenance_kind": audit.get("provenance", {}).get("kind", "unknown"),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
