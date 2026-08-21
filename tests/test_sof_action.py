"""Regression and hostile-fixture tests for Paper XIV SOF Action Objects."""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
V2_SNAPSHOT_ROOT = ROOT / "release-snapshots" / "rime-lite-v2.0" / "files"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


engine = load_module("paper14_action_engine", ROOT / "experiments" / "paper14" / "action_engine.py")
workbench = load_module("paper14_action_workbench", ROOT / "experiments" / "paper14" / "action_workbench.py")
selector = load_module("paper14_policy_selector", ROOT / "experiments" / "paper14" / "policy_selector.py")
validator = load_module("paper14_sofaction_validator", ROOT / "experiments" / "paper14" / "validate_sofaction.py")


def audit(stem: str) -> dict:
    path = V2_SNAPSHOT_ROOT / "experiments" / "paper13" / "results" / "audits" / f"{stem}.sofaudit.json"
    return json.loads(path.read_text(encoding="utf-8"))


def native_audit() -> dict:
    path = V2_SNAPSHOT_ROOT / "experiments" / "paper13" / "results" / "native" / "gridworld-f4" / "audits" / "gridworld-f4-native-v2.sofaudit.json"
    return json.loads(path.read_text(encoding="utf-8"))


def source_path(audit_payload: dict) -> str:
    if audit_payload["audit_id"] == "gridworld-f4-native-v2":
        path = V2_SNAPSHOT_ROOT / "experiments" / "paper13" / "results" / "native" / "gridworld-f4" / "audits" / "gridworld-f4-native-v2.sofaudit.json"
    else:
        path = V2_SNAPSHOT_ROOT / "experiments" / "paper13" / "results" / "audits" / f"{audit_payload['audit_id']}.sofaudit.json"
    return path.relative_to(ROOT).as_posix()


def context_for(payload: dict) -> dict:
    return workbench.declared_action_context(payload)


def policy() -> dict:
    return deepcopy(engine.DEFAULT_POLICY_PROFILE)


def action_schema() -> dict:
    return json.loads((ROOT / "schemas" / "sofaction" / "v2.0.schema.json").read_text(encoding="utf-8"))


def record_for(payload: dict, *, context: dict | None = None, profile: dict | None = None) -> dict:
    return engine.build_action_record(
        action_record_id=f"test:{payload['audit_id']}",
        audit=payload,
        source_artifact=source_path(payload),
        action_context=context if context is not None else context_for(payload),
        policy_profile=profile if profile is not None else policy(),
    )


def test_no_raw_audit_enters_candidate_generator():
    payload = native_audit()
    try:
        engine.generate_candidate_actions(payload, policy(), context_for(payload), {})
    except ValueError as exc:
        assert "InterpretationRecord" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("raw SOFAUDIT unexpectedly admitted by candidate generator")


def test_migrated_unresolved_coordinates_produce_no_candidates():
    record = record_for(audit("gridworld_f4"))
    assert record["candidate_action_set"] == {"count": 0, "actions": []}
    assert record["disposition_result"]["kind"] == "unresolved_disposition"
    assert {item["assessment_kind"] for item in record["interpretation_records"]} == {"evidence_insufficient"}
    assert record["audit_projection"]["signature"] == audit("gridworld_f4")["coordinates"]


def test_native_f4_produces_only_review_candidates():
    record = record_for(native_audit())
    assert {item["disposition"] for item in record["candidate_action_set"]["actions"]} == {
        "Investigate",
        "RequestEvidence",
    }
    assert all(item["authorization_state"] == "not_requested" for item in record["candidate_action_set"]["actions"])
    assert all(item["intended_diagnostic_consequence"]["status"] == "intended_diagnostic_consequence" for item in record["candidate_action_set"]["actions"])
    assert record["record_class"] == "decision_trace_certificate"
    assert record["disposition_result"]["kind"] == "candidate_action_set"


def test_explicit_no_action_is_not_an_empty_or_unresolved_result():
    payload = deepcopy(native_audit())
    for coordinate in payload["coordinates"].values():
        coordinate["comparison_state"] = "ALIGNED"
    record = engine.build_action_record(
        action_record_id="test:no-action",
        audit=payload,
        source_artifact=source_path(native_audit()),
        action_context=context_for(native_audit()),
        policy_profile=policy(),
    )
    assert record["candidate_action_set"] == {"count": 0, "actions": []}
    assert record["disposition_result"]["kind"] == "no_action_disposition"


def test_interpretation_relativity_is_policy_and_context_relative():
    payload = native_audit()
    failure_context = context_for(payload)
    licensed_context = deepcopy(failure_context)
    licensed_context.update(
        {
            "context_id": "paper14:licensed-context",
            "comparison_role": "legitimate_transformation_control",
            "contract_status": "conforming",
            "evaluator_qualification_note": "declared transformation contract",
        }
    )
    contract_ref = deepcopy(engine.POLICY_SOURCE_REF)
    contract_ref["artifact_id"] = "licensed-transformation-contract"
    contract_ref["role"] = "transformation_contract"
    licensed_context["transformation_contract_refs"] = [contract_ref]
    failure = engine.interpret_signature(payload, failure_context, policy())
    licensed = engine.interpret_signature(payload, licensed_context, policy())
    failure_assessments = {item["assessment_kind"] for item in failure}
    licensed_assessments = {item["assessment_kind"] for item in licensed}
    assert "defect_candidate" in failure_assessments
    assert "licensed_change" in licensed_assessments
    assert failure_assessments != licensed_assessments


def test_candidate_generation_does_not_reinterpret_policy_predicates():
    payload = native_audit()
    context = context_for(payload)
    semantic_policy = policy()
    interpretations = engine.interpret_signature(payload, context, semantic_policy)
    audit_ref = {
        "artifact_id": "audit",
        "role": "audit",
        "uri": "artifact://audit",
        "digest": {"algorithm": "sha256", "value": "0" * 64},
        "producer": "test",
        "contract_version": "2.0",
    }
    baseline = engine.generate_candidate_actions(
        interpretations, semantic_policy, context, audit_ref
    )

    generation_profile = deepcopy(semantic_policy)
    for rule in generation_profile["rules"]:
        rule["assessment_note"] = "changed after interpretation"
        rule["when"] = {
            "predicate_version": "1.0",
            "op": "coordinate_exists",
            "coordinate_id": "operator.support.summary",
        }
    replayed = engine.generate_candidate_actions(
        interpretations, generation_profile, context, audit_ref
    )
    assert replayed == baseline


def test_missing_context_or_policy_is_inconclusive_without_actions():
    payload = native_audit()
    record = engine.build_action_record(
        action_record_id="test:missing-context",
        audit=payload,
        source_artifact=source_path(payload),
        action_context=None,
        policy_profile=None,
    )
    assert record["context_admission"]["status"] == "inconclusive"
    assert record["policy_admission"]["status"] == "inconclusive"
    assert record["action_context"] is None
    assert record["policy_profile"] is None
    assert record["candidate_action_set"] == {"count": 0, "actions": []}
    assert record["disposition_result"]["kind"] == "no_disposition"


def test_hostile_unresolved_coordinate_is_rejected():
    record = record_for(audit("gridworld_f4"))
    record["interpretation_records"][0]["supported_dispositions"] = ["Mitigate"]
    assert any("unresolved coordinate supports a disposition" in item for item in validator.contract_errors(record))


def test_hostile_unresolved_cannot_be_relabelled_no_action():
    record = record_for(audit("gridworld_f4"))
    record["disposition_result"]["kind"] = "no_action_disposition"
    assert any("no_action_disposition requires" in item for item in validator.contract_errors(record))


def test_hostile_admitted_interpretations_cannot_be_relabelled_no_disposition():
    record = record_for(native_audit())
    record["candidate_action_set"] = {"count": 0, "actions": []}
    record["disposition_result"] = {
        "kind": "no_disposition",
        "reason": "producer removed the candidates",
        "interpretation_ids": [],
        "candidate_action_ids": [],
    }
    assert any("no_disposition requires empty" in item for item in validator.contract_errors(record))


def test_hostile_projection_rewrite_is_rejected():
    record = record_for(native_audit())
    record["audit_projection"]["signature"].pop("operator.support.summary")
    assert any("does not preserve" in item for item in validator.contract_errors(record))


def test_hostile_unknown_policy_rule_is_rejected():
    record = record_for(native_audit())
    record["candidate_action_set"]["actions"][0]["policy_rule_refs"] = ["missing-rule"]
    assert any("unknown policy rule" in item for item in validator.contract_errors(record))


def test_hostile_policy_applicability_is_rejected():
    record = record_for(native_audit())
    record["policy_profile"]["applicability"]["regimes"] = ["analogue_vs_analogue"]
    assert any("not applicable" in item for item in validator.contract_errors(record))


def test_hostile_precedence_cycle_is_rejected():
    record = record_for(native_audit())
    record["policy_profile"]["precedence_edges"].append(
        {"before": "aligned-coordinate-no-action", "after": "unresolved-coordinate-no-action"}
    )
    assert any("cycle" in item for item in validator.contract_errors(record))


def test_hostile_conflicting_policy_rules_are_rejected():
    record = record_for(native_audit())
    original = deepcopy(record["policy_profile"]["rules"][2])
    original["rule_id"] = "conflicting-mismatch-rule"
    original["assessment_kind"] = "policy_conflict"
    record["policy_profile"]["rules"].append(original)
    record["policy_profile"]["precedence_edges"].append(
        {"before": "certified-mismatch-requires-review", "after": original["rule_id"]}
    )
    assert any("conflicting rules" in item for item in validator.contract_errors(record))


def test_hostile_exception_without_rule_coverage_is_rejected():
    record = record_for(native_audit())
    record["policy_profile"]["exceptions"].append(
        {
            "exception_id": "uncovered-exception",
            "when": deepcopy(record["policy_profile"]["rules"][2]["when"]),
            "overrides_rule_ids": [],
            "negative_boundary": ["An exception must explicitly name every rule it suppresses."],
        }
    )
    assert any("exception" in item and "cover" in item for item in validator.contract_errors(record))


def test_typed_exception_suppresses_only_its_declared_rule():
    profile = policy()
    mismatch_rule = profile["rules"][2]
    profile["exceptions"] = [
        {
            "exception_id": "hold-mismatch-review",
            "when": deepcopy(mismatch_rule["when"]),
            "overrides_rule_ids": [mismatch_rule["rule_id"]],
            "negative_boundary": ["This exception suppresses review generation only for its declared predicate."],
        }
    ]
    record = record_for(native_audit(), profile=profile)
    mismatch = next(
        item for item in record["interpretation_records"]
        if item["audit_coordinate_refs"][0]["comparison_state"] == "MISMATCH"
    )
    assert mismatch["assessment_kind"] == "inconclusive"
    assert record["candidate_action_set"]["actions"] == []
    assert validator.validation_errors(record, action_schema()) == []
    assert validator.contract_errors(record) == []


def test_hostile_authorized_action_without_receipt_is_rejected():
    record = record_for(native_audit())
    action = record["candidate_action_set"]["actions"][0]
    action["authorization_state"] = "authorized"
    assert validator.validation_errors(record, action_schema())


def test_hostile_outcome_observation_cannot_be_action_effect_certificate():
    record = record_for(native_audit())
    record["record_class"] = "outcome_observation"
    assert validator.validation_errors(record, action_schema())
    assert any("reserves outcome" in item for item in validator.contract_errors(record))


def test_hostile_arbitrary_policy_predicate_is_rejected():
    record = record_for(native_audit())
    record["policy_profile"]["rules"][0]["when"] = {
        "predicate_version": "1.0",
        "op": "whatever_the_engine_decides",
        "trust_producer_interpretation": True,
    }
    assert validator.validation_errors(record, action_schema())


def test_uncertainty_policy_is_a_closed_replay_object():
    record = record_for(native_audit())
    assert record["policy_profile"]["uncertainty_policy"]["version"] == "1.0"
    hostile = deepcopy(record)
    hostile["policy_profile"]["uncertainty_policy"]["producer_hint"] = "cautious"
    assert validator.validation_errors(hostile, action_schema())


def test_predicate_three_valued_truth_table_is_explicit():
    payload = audit("gridworld_f4")
    context = context_for(payload)
    policy_profile = policy()
    missing = {
        "predicate_version": "1.0",
        "op": "coordinate_carrier_is",
        "coordinate_id": "support",
        "value": "word",
    }
    assert engine._predicate_matches(
        missing,
        audit=payload,
        coordinate_id="support",
        coordinate=payload["coordinates"]["support"],
        context=context,
        policy=policy_profile,
    ) == engine.TruthValue.UNRESOLVED
    assert validator._evaluate_predicate(
        missing,
        payload,
        "support",
        payload["coordinates"]["support"],
        context,
        policy_profile,
    ) == validator._TruthValue.UNRESOLVED


def test_validator_independently_recomputes_interpretation():
    record = record_for(native_audit())
    interpretation = next(
        item for item in record["interpretation_records"]
        if item["assessment_kind"] == "defect_candidate"
    )
    interpretation["assessment_kind"] = "no_action_indicated"
    assert any("assessment kind does not match" in item for item in validator.contract_errors(record))


def test_bare_string_evidence_is_rejected():
    record = record_for(native_audit())
    record["record_basis"]["evidence_refs"] = ["experiment passed"]
    assert validator.validation_errors(record, action_schema())


def test_source_audit_requires_validation_receipt():
    record = record_for(native_audit())
    del record["source_audit"]["validation_receipt"]
    assert validator.validation_errors(record, action_schema())


def test_single_rule_no_action_policy_needs_no_precedence_or_candidate_family():
    profile = policy()
    profile["rules"] = [deepcopy(profile["rules"][-1])]
    profile["precedence_edges"] = []
    profile["candidate_families"] = []
    admission, admitted = engine.admit_policy_profile(profile, native_audit(), context_for(native_audit()))
    assert admission["status"] == "admitted"
    assert admitted is not None


def test_admission_cross_fields_are_closed_by_schema():
    record = record_for(native_audit())
    record["context_admission"]["missing_fields"] = ["authority"]
    assert validator.validation_errors(record, action_schema())
    record = record_for(native_audit())
    record["context_admission"] = {
        "status": "inconclusive",
        "contract_validation": "rejected",
        "applicability": "unresolved",
        "completeness": "incomplete",
        "missing_fields": [],
        "rationale": "incomplete",
    }
    assert validator.validation_errors(record, action_schema())


def test_machine_record_claim_status_matrix_rejects_theorem():
    record = record_for(native_audit())
    record["claim_status"] = "Theorem"
    assert validator.validation_errors(record, action_schema())


def test_hostile_candidate_carrier_mismatch_is_rejected():
    record = record_for(native_audit())
    action = record["candidate_action_set"]["actions"][0]
    original = action["carrier"]
    action["carrier"] = "word" if original != "word" else "lie"
    assert any("carrier" in item for item in validator.contract_errors(record))


def test_downstream_selection_does_not_change_candidate_set():
    record = record_for(native_audit())
    actions = record["candidate_action_set"]["actions"]
    selected = selector.select_action_plan(actions, selector.ActionSelectionPolicy(policy_id="test", max_actions=1))
    assert len(selected["selected_action_ids"]) == 1
    assert selector.validate_selected_action_plan(actions, selected) == []
    assert {item["action_id"] for item in actions} != set()


def test_hostile_selector_action_outside_candidate_set_is_rejected():
    record = record_for(native_audit())
    plan = {"selected_action_ids": ["not-in-candidate-set"]}
    assert selector.validate_selected_action_plan(record["candidate_action_set"]["actions"], plan)


def test_canonical_action_object_rejects_embedded_selection():
    record = record_for(native_audit())
    record["selection"] = {"selected_action_ids": []}
    schema = json.loads((ROOT / "schemas" / "sofaction" / "v2.0.schema.json").read_text(encoding="utf-8"))
    assert any("selection" in item for item in validator.validation_errors(record, schema))


def test_hostile_actor_outside_authority_scope_is_rejected():
    record = record_for(native_audit())
    record["action_context"]["actor"]["actor_id"] = "unlisted-actor"
    assert any("actor is outside" in item for item in validator.contract_errors(record))


def test_hostile_post_action_observation_cannot_rewrite_audit():
    record = record_for(native_audit())
    record["post_action_observation"] = {"status": "observed"}
    assert any("post-action" in item for item in validator.contract_errors(record))


def test_v2_schema_and_contract_pass_for_native_record():
    payload = record_for(native_audit())
    schema = json.loads((ROOT / "schemas" / "sofaction" / "v2.0.schema.json").read_text(encoding="utf-8"))
    assert validator.validation_errors(payload, schema) == []
    assert validator.contract_errors(payload) == []


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("test_sof_action.py: OK")
