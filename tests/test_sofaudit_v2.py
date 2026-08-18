from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.sofrs.api import v2_report_validation_receipt_errors  # noqa: E402


SOURCE_MIGRATOR = (
    ROOT / "experiments" / "paper13" / "validation" / "migrate_sofrs_v1_to_v2.py"
)
AUDIT_MIGRATOR = (
    ROOT / "experiments" / "paper13" / "validation" / "migrate_sofaudit_v1_to_v2.py"
)
OBJECT_CERTIFICATE = (
    ROOT
    / "experiments"
    / "paper13"
    / "validation"
    / "gridworld_f4_object_certificate.py"
)
NATIVE_GENERATOR = (
    ROOT
    / "experiments"
    / "paper13"
    / "validation"
    / "gridworld_f4_native_v2.py"
)
NATIVE_AUDIT = (
    ROOT
    / "experiments"
    / "paper13"
    / "results"
    / "native"
    / "gridworld-f4"
    / "audits"
    / "gridworld-f4-native-v2.sofaudit.json"
)
NATIVE_RECEIPT = (
    ROOT
    / "experiments"
    / "paper13"
    / "results"
    / "native"
    / "gridworld-f4"
    / "receipts"
    / "gridworld-f4-native-v2.validation-receipt.json"
)
SCHEMA_PATH = ROOT / "schemas" / "sofaudit" / "v2.0.schema.json"
AUDIT_DIR = ROOT / "experiments" / "paper13" / "results" / "audits"
INDEX_PATH = AUDIT_DIR.parent / "migration-index.json"


def _load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator_module = _load_module(
    "paper13_sofaudit_v2_validator",
    "experiments/paper13/validation/validate_sofaudit_v2.py",
)


def _payloads():
    return [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(AUDIT_DIR.glob("*.sofaudit.json"))
    ]


def test_sofaudit_v2_schema_and_census():
    assert os.environ.get("RIME_VERIFICATION_SCRATCH") == "1", (
        "generative SOFAUDIT regression requires verification scratch"
    )
    for command in (
        [str(SOURCE_MIGRATOR)],
        [str(AUDIT_MIGRATOR)],
        [str(NATIVE_GENERATOR), "--prepare"],
        [str(OBJECT_CERTIFICATE), "--write"],
        [str(NATIVE_GENERATOR), "--write"],
        [str(OBJECT_CERTIFICATE)],
    ):
        result = subprocess.run(
            [sys.executable, *command],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    payloads = _payloads()
    assert len(payloads) == 28
    for path, payload in payloads:
        assert list(validator.iter_errors(payload)) == [], path.name
        assert validator_module.semantic_errors(payload, path) == [], path.name

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    assert index["record_count"] == 28
    assert index["profile_counts"] == {
        validator_module.STANDARD_PROFILE_ID: 28,
    }
    assert index["normalized_legacy_sentinel_record_count"] == 10
    assert index["unresolved_legacy_coordinate_count"] == 201
    assert index["unresolved_legacy_wall_observation_count"] == 5
    assert index["source_report_receipt_count"] == 36
    assert validator_module.index_errors(
        INDEX_PATH, [path for path, _ in payloads]
    ) == []

    native = json.loads(NATIVE_AUDIT.read_text(encoding="utf-8"))
    assert list(validator.iter_errors(native)) == []
    assert validator_module.semantic_errors(native, NATIVE_AUDIT) == []
    assert validator_module.validation_receipt_errors(NATIVE_RECEIPT) == []


def test_native_gridworld_f4_is_factual_without_promoting_migration():
    migrated = json.loads((AUDIT_DIR / "gridworld_f4.sofaudit.json").read_text(encoding="utf-8"))
    for coordinate_id in ("support", "word_bridge", "lie_bridge"):
        assert migrated["coordinates"][coordinate_id]["comparison_state"] == "UNRESOLVED"
        assert migrated["coordinates"][coordinate_id]["value"] is None

    native = json.loads(NATIVE_AUDIT.read_text(encoding="utf-8"))
    expected = {
        "operator.support.summary": ("ALIGNED", 0),
        "word.support.length-2.summary": ("ALIGNED", 0),
        "lie.simple-commutator-support.summary": ("MISMATCH", 8),
    }
    for coordinate_id, (state, mismatch) in expected.items():
        coordinate = native["coordinates"][coordinate_id]
        assert coordinate["comparison_state"] == state
        assert coordinate["value"]["delta"]["total_mismatch"] == mismatch
        assert coordinate["claim_target"] == "external_mathematical_object"
        assert coordinate["certificate_class"] == "object"
    assert native["comparison_basis"]["basis_status"] == "COMPLETE"
    assert native["comparison_basis"]["object_level_oracle"]["status"] == "SATISFIED"
    assert native["provenance"]["kind"] == "native"


def test_source_reports_bind_validated_receipts():
    receipt_paths = set()
    for path, payload in _payloads():
        for side in ("reference", "target"):
            reference = payload["source_reports"][side]
            receipt_path, errors = validator_module.resolve_artifact(
                path.parent,
                reference["validation_receipt"],
            )
            assert errors == [], path.name
            receipt_paths.add(receipt_path)
            assert any(
                artifact["role"] == f"{side}-report-validation-receipt"
                and {
                    "uri": artifact["uri"],
                    "digest": artifact["digest"],
                }
                == reference["validation_receipt"]
                for artifact in payload["source_artifacts"]
            ), path.name
    assert len(receipt_paths) == 36


def test_sofaudit_v2_consumes_only_sofrs_v2_reports():
    for _, payload in _payloads():
        for side in ("reference", "target"):
            reference = payload["source_reports"][side]
            assert reference["sofrs_version"] == "2.0"
            assert reference["admission_basis"] == "native_sofrs_v2"
            assert reference["comparison_role_basis"]["role"] == side
        assert payload["provenance"]["kind"] == "migration"


def test_migrated_coordinates_are_not_promoted_without_alignment():
    for path, payload in _payloads():
        for coordinate in payload["coordinates"].values():
            assert coordinate["comparison_state"] in {
                "UNRESOLVED",
                "NOT_DECLARED",
            }, path.name
            assert coordinate["value"] is None, path.name
            assert coordinate["claim_status"] is None, path.name


def test_alignment_components_are_typed_contracts():
    path, payload = _payloads()[0]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    hostile = deepcopy(payload)
    hostile["alignment"]["sector_alignment"] = {"note": "looks similar"}
    errors = list(Draft202012Validator(schema).iter_errors(hostile))
    assert errors


def test_comparison_specification_rejects_free_form_rules():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    hostile = deepcopy(_payloads()[0][1])
    hostile["comparison_specification"]["metric"] = {"trust_me": True}
    errors = list(Draft202012Validator(schema).iter_errors(hostile))
    assert errors


def test_comparison_specification_cross_field_rules():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    payload = _payloads()[0][1]

    exact = deepcopy(payload)
    exact["comparison_specification"]["normalization"].update(
        {"numeric_policy": "exact", "equality_tolerance": 0.1}
    )
    assert list(validator.iter_errors(exact))

    declared_map = deepcopy(payload)
    declared_map["comparison_specification"]["parameter_synchronization"].update(
        {
            "kind": "declared-map",
            "map_artifact_id": None,
            "interpolation_method": "declared",
        }
    )
    assert list(validator.iter_errors(declared_map))

    weighted = deepcopy(payload)
    weighted["comparison_specification"]["aggregation"]["scalarization"] = "weighted-hamming"
    assert list(validator.iter_errors(weighted))


def test_native_v2_provenance_does_not_require_migration_fields():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    native = deepcopy(_payloads()[0][1])
    native["provenance"] = {
        "kind": "native",
        "generator_id": "paper13.native-audit-engine",
        "generator_version": "2.0",
        "generation_artifact_ids": ["artifact.source-audit"],
        "generation_notes": ["Native generation fixture."],
    }
    assert list(Draft202012Validator(schema).iter_errors(native)) == []


def test_object_certificate_requires_external_oracle():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["claim"].update(
        {
            "claim_target": "external_mathematical_object",
            "certificate_class": "object",
        }
    )
    errors = validator_module.semantic_errors(hostile, path)
    assert any("independent comparison oracle" in error for error in errors)


def test_object_oracle_cannot_relabel_internal_artifacts_as_independent():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["claim"].update(
        {
            "claim_target": "external_mathematical_object",
            "certificate_class": "object",
            "classification_source": "independent_oracle",
        }
    )
    oracle = hostile["comparison_basis"]["object_level_oracle"]
    oracle.update(
        {
            "status": "SATISFIED",
            "independence": {
                "implementation_relation": "separate_algorithm",
                "producer_relation": "same_producer_disclosed",
                "input_source": "frozen_source_artifacts",
                "producer_cache_used": False,
            },
            "raw_source_artifacts": [
                "artifact.reference-report",
                "artifact.target-report",
            ],
            "independent_recomputation_artifacts": ["artifact.source-audit"],
            "oracle_result_artifact": "artifact.reference-report",
            "audit_result_artifact": "artifact.target-report",
        }
    )
    errors = validator_module.semantic_errors(hostile, path)
    assert any("incompatible artifact roles" in error for error in errors)


def test_comparison_audit_certificate_has_its_own_basis_gate():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["claim"].update(
        {
            "claim_target": "comparison_relation",
            "certificate_class": "comparison_audit",
            "classification_source": "audit_engine",
        }
    )
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(hostile)) == []
    errors = validator_module.semantic_errors(hostile, path)
    assert any("complete alignment-relative basis" in error for error in errors)


def test_declared_reference_is_not_a_truth_oracle():
    _, payload = _payloads()[0]
    basis = payload["source_reports"]["reference"]["comparison_role_basis"]
    assert basis["basis_kind"] == "declared_baseline_only"
    assert basis["authority_status"] == "DECLARED"
    assert any("does not imply ground truth" in text for text in basis["negative_boundary"])


def test_reference_and_target_roles_are_position_bound():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["source_reports"]["reference"]["comparison_role_basis"]["role"] = "target"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("reference comparison role basis has the wrong role" in error for error in errors)


def test_comparison_basis_cannot_drift_from_reference_basis():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["comparison_basis"]["reference_role_basis"]["scope"] = "Different scope."
    errors = validator_module.semantic_errors(hostile, path)
    assert any("differs from the source reference basis" in error for error in errors)


def test_regime_is_recomputed_from_report_kinds():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["regime"] = "strict_vs_strict"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("differs from record-kind recomputation" in error for error in errors)


def test_audit_profile_is_bound_to_recomputed_regime():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["audit_profile"]["applicable_regime"] = "strict_vs_strict"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("Audit Profile applicable_regime" in error for error in errors)


def test_audit_profile_is_bound_to_source_addressed_inputs():
    path, payload = _payloads()[0]

    hostile = deepcopy(payload)
    hostile["audit_profile"]["availability_semantics"]["zero_is_unavailable"] = True
    errors = validator_module.semantic_errors(hostile, path)
    assert any("differs from its source-addressed profile artifact" in error for error in errors)

    hostile = deepcopy(payload)
    hostile["audit_profile"]["profile_artifact_id"] = "artifact.source-audit"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("does not bind the audit-profile artifact role" in error for error in errors)

    hostile = deepcopy(payload)
    registry = next(
        item
        for item in hostile["source_artifacts"]
        if item["role"] == "coordinate-semantics-registry"
    )
    registry["digest"]["value"] = "0" * 64
    errors = validator_module.semantic_errors(hostile, path)
    assert any("digest mismatch" in error for error in errors)


def test_audit_profile_requires_profile_and_registry_source_roles():
    from experiments.paper13.validation.audit_profiles import (
        STANDARD_PROFILE,
        profile_errors,
    )

    hostile = deepcopy(STANDARD_PROFILE)
    hostile["required_evidence_roles"].remove("coordinate-semantics-registry")
    assert any("source-addressed profile and registry" in error for error in profile_errors(hostile))


def test_alignment_properties_are_recomputed_from_report_universes():
    path, payload = _payloads()[0]
    for property_name in (
        "total_on_reference",
        "total_on_target",
        "injective",
        "surjective",
    ):
        hostile = deepcopy(payload)
        properties = hostile["alignment"]["sector_alignment"]["properties"]
        properties[property_name] = not properties[property_name]
        errors = validator_module.semantic_errors(hostile, path)
        assert any(
            "properties differ from validator recomputation" in error
            for error in errors
        ), property_name


def test_alignment_pair_ids_must_exist_in_linked_reports():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    alignment = hostile["alignment"]["sector_alignment"]
    alignment["state"] = "PARTIAL"
    alignment["pairs"] = [{
        "reference_id": "invented-reference",
        "target_id": "invented-target",
        "relation": "equivalent",
        "evidence_artifact_ids": ["artifact.source-audit"],
    }]
    errors = validator_module.semantic_errors(hostile, path)
    assert any("unknown reference ids" in error for error in errors)
    assert any("unknown target ids" in error for error in errors)


def test_profile_request_and_coordinate_keys_are_bijective():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["audit_profile"]["requested_coordinate_ids"].remove("support")
    errors = validator_module.semantic_errors(hostile, path)
    assert any("exactly the Audit Profile request" in error for error in errors)


def test_basis_complete_is_validator_derived():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["comparison_basis"]["basis_status"] = "COMPLETE"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("status differs from validator recomputation" in error for error in errors)


def test_coordinate_value_schema_is_family_bound():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["coordinates"]["support"]["value_schema_id"] = "word.depth.v1"
    errors = validator_module.semantic_errors(hostile, path)
    assert any("value_schema_id does not match coordinate family" in error for error in errors)


def test_claim_target_certificate_and_source_matrix_is_closed():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["claim"].update(
        {
            "result_state": "OBSERVED",
            "claim_status": "Computational Observation",
            "claim_target": "migration_consistency",
            "certificate_class": None,
            "classification_source": "migration_adapter",
        }
    )
    errors = validator_module.semantic_errors(hostile, path)
    assert any("not a permitted combination" in error for error in errors)


def test_semantic_validator_executes_comparison_specification_rules():
    path, payload = _payloads()[0]
    hostile = deepcopy(payload)
    hostile["comparison_specification"]["normalization"].update(
        {"numeric_policy": "exact", "equality_tolerance": 0.1}
    )
    errors = validator_module.semantic_errors(hostile, path)
    assert any("exact numeric policy" in error for error in errors)


def test_receipt_cannot_claim_a_different_report_identity():
    path, payload = _payloads()[0]
    reference = payload["source_reports"]["reference"]
    receipt_path, errors = validator_module.resolve_artifact(
        path.parent,
        reference["validation_receipt"],
    )
    assert errors == []
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["report"]["report_id"] = "different-report"
    errors = v2_report_validation_receipt_errors(
        receipt,
        repository_root=ROOT,
        expected_report_reference=reference,
        expected_report_base_directory=path.parent,
    )
    assert any("report_id" in error for error in errors)


def test_standard_profile_is_sparse_relative_to_universal_contract():
    for path, payload in _payloads():
        requested = set(payload["audit_profile"]["requested_coordinate_ids"])
        assert requested == validator_module.STANDARD_COORDINATES, path.name
        assert set(payload["coordinates"]) == requested, path.name
        assert "comparison_mode" not in payload, path.name
        assert "signature" not in payload, path.name
        assert "admission" not in payload, path.name
        for coordinate in payload["coordinates"].values():
            assert "report_item_binding" in coordinate
            if coordinate["claim_status"] == "Computational Certificate":
                assert coordinate["claim_target"] == "migration_consistency"
                assert coordinate["certificate_class"] == "migration_assembly"


def test_unavailable_coordinate_cannot_be_promoted_to_zero():
    path, payload = next(
        (path, payload)
        for path, payload in _payloads()
        if any(
            item["comparison_state"] == "NOT_DECLARED"
            for item in payload["coordinates"].values()
        )
    )
    field = next(
        field
        for field, item in payload["coordinates"].items()
        if item["comparison_state"] == "NOT_DECLARED"
    )
    promoted = deepcopy(payload)
    promoted["coordinates"][field] = {
        "comparison_state": "ALIGNED",
        "result_state": "CERTIFIED",
        "claim_status": "Computational Certificate",
        "claim_target": "migration_consistency",
        "certificate_class": "migration_assembly",
        "classification_source": "migration_adapter",
        "report_item_binding": {
            "binding_state": "legacy_payload_only",
            "reference_item_ref": None,
            "target_item_ref": None,
            "reason": "hostile promotion",
        },
        "coordinate_family": promoted["coordinates"][field]["coordinate_family"],
        "value": 0,
        "source_artifact_ids": ["artifact.source-audit"],
    }
    promoted["inherited_compiler_guards"]["condition_checks"] = [
        check
        for check in promoted["inherited_compiler_guards"]["condition_checks"]
        if check["condition_id"] != "paper-x-promotion-audit"
    ]
    errors = validator_module.semantic_errors(promoted, path)
    assert any("required compiler" in error for error in errors)


def test_incomparable_coordinate_is_not_numeric_zero():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["coordinates"]["word_bridge"] = {
        "comparison_state": "INCOMPARABLE",
        "result_state": "DECLARED",
        "claim_status": None,
        "claim_target": None,
        "certificate_class": None,
        "classification_source": "migration_adapter",
        "report_item_binding": {
            "binding_state": "incomparable",
            "reference_item_ref": None,
            "target_item_ref": None,
            "reason": "Word conventions are incompatible.",
        },
        "coordinate_family": "word",
        "value": 0,
        "source_artifact_ids": [],
        "reason": "Word conventions are incompatible.",
    }
    errors = validator_module.semantic_errors(modified, path)
    assert any("comparison value must be a typed object" in error for error in errors)


def test_matched_coordinate_uses_the_shared_status_matrix():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    coordinate = modified["coordinates"]["support"]
    coordinate["comparison_state"] = "ALIGNED"
    coordinate["result_state"] = "ESTABLISHED"
    coordinate["claim_status"] = "Computational Observation"
    coordinate["claim_target"] = "representation_interface"
    coordinate["certificate_class"] = None
    coordinate["classification_source"] = "migration_adapter"
    coordinate["value"] = {"equal": True}
    errors = validator_module.semantic_errors(modified, path)
    assert any("illegal result/claim status pair" in error for error in errors)


def test_source_artifact_roles_are_unique():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    duplicate = deepcopy(modified["source_artifacts"][0])
    duplicate["id"] = "artifact.duplicate-source-audit"
    modified["source_artifacts"].append(duplicate)
    errors = validator_module.semantic_errors(modified, path)
    assert any("source_artifacts roles must be unique" in error for error in errors)


def test_source_artifact_ids_are_unique():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    duplicate = deepcopy(modified["source_artifacts"][0])
    duplicate["role"] = "duplicate-role"
    modified["source_artifacts"].append(duplicate)
    errors = validator_module.semantic_errors(modified, path)
    assert any("source_artifacts ids must be unique" in error for error in errors)


def test_artifact_digest_closure_is_recomputed():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["source_artifacts"][0]["digest"]["value"] = "0" * 64
    errors = validator_module.semantic_errors(modified, path)
    assert any("digest mismatch" in error for error in errors)


def test_missing_report_item_binding_is_rejected():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    del modified["coordinates"]["support"]["report_item_binding"]
    errors = validator_module.semantic_errors(modified, path)
    assert errors


def test_paired_binding_requires_both_report_items():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["coordinates"]["support"]["report_item_binding"] = {
        "binding_state": "paired",
        "reference_item_ref": None,
        "target_item_ref": None,
        "reason": None,
    }
    errors = validator_module.semantic_errors(modified, path)
    assert any("paired binding lacks report item refs" in error for error in errors)


def test_legacy_binding_cannot_be_promoted_to_object_certificate():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    coordinate = modified["coordinates"]["support"]
    coordinate["certificate_class"] = "object"
    coordinate["claim_target"] = "external_mathematical_object"
    errors = validator_module.semantic_errors(modified, path)
    assert any("Object Certificate requires paired report items" in error for error in errors)


def test_missing_alignment_is_not_a_comparison_signature():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["alignment"]["sector_alignment"] = None
    coordinate = modified["coordinates"]["support"]
    coordinate.update(
        {
            "comparison_state": "ALIGNED",
            "result_state": "OBSERVED",
            "claim_status": "Computational Observation",
            "claim_target": "comparison_relation",
            "certificate_class": None,
            "classification_source": "audit_engine",
            "value": {
                "reference_value": [],
                "target_value": [],
                "normalized_reference_value": [],
                "normalized_target_value": [],
                "relation": "equal",
                "delta": [],
                "unit": None,
                "metric_result": None,
                "policy_refs": [],
                "oracle_ref": None,
            },
        }
    )
    errors = validator_module.semantic_errors(modified, path)
    assert any("without validated sector and observable alignment" in error for error in errors)


def test_failed_policy_guard_rejects_admitted_audit():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    policy_check = next(
        check
        for check in modified["inherited_compiler_guards"]["condition_checks"]
        if check["condition_id"] == "paper-x-policy-alignment"
    )
    policy_check["status"] = "FAILED"
    errors = validator_module.semantic_errors(modified, path)
    assert any("differs from condition recomputation REJECTED" in error for error in errors)


def test_rejected_guards_allow_only_a_rejection_artifact():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    policy_check = next(
        check
        for check in modified["inherited_compiler_guards"]["condition_checks"]
        if check["condition_id"] == "paper-x-policy-alignment"
    )
    policy_check["status"] = "FAILED"
    modified["inherited_compiler_guards"]["state"] = "REJECTED"
    errors = validator_module.semantic_errors(modified, path)
    assert any("cannot emit an affirmative audit claim" in error for error in errors)


def test_legacy_strict_record_kind_cannot_be_masqueraded():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["source_reports"]["reference"]["record_kind"] = "strict_sof"
    errors = validator_module.semantic_errors(modified, path)
    assert any(
        "record_kind does not match linked SOFRS v2 report" in error
        for error in errors
    )


def test_artifact_uri_cannot_escape_repository_root():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["source_artifacts"][0]["uri"] = "../../../../../../outside.json"
    errors = validator_module.semantic_errors(modified, path)
    assert any("escapes repository root" in error for error in errors)


def test_legacy_sentinel_is_rejected():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["comparison_specification"]["normalization"]["frozen_sentinel"] = 999
    errors = validator_module.semantic_errors(modified, path)
    assert any("legacy integer sentinel 999" in error for error in errors)


def test_legacy_f5_paths_are_not_promoted_to_wall_mismatches():
    unresolved = []
    for path, payload in _payloads():
        wall = payload["coordinates"]["wall_record"]
        binding = wall["wall_input_binding"]
        if "legacy_observation" not in binding:
            continue
        unresolved.append(path.name)
        assert wall["comparison_state"] == "UNRESOLVED", path.name
        assert wall["result_state"] == "DECLARED", path.name
        assert wall["claim_status"] is None, path.name
        assert wall["value"] is None, path.name
        assert binding["reference_wall"]["state"] == "NOT_DECLARED", path.name
        assert binding["target_wall"]["state"] == "NOT_DECLARED", path.name
        assert binding["comparison_context"]["state"] == "UNRESOLVED", path.name
        assert binding["legacy_observation"]["disposition"] == "COMPATIBILITY_ONLY"
    assert len(unresolved) == 5


def test_wall_mismatch_requires_two_retained_inputs_and_ready_context():
    path, payload = next(
        (path, payload)
        for path, payload in _payloads()
        if payload["coordinates"]["wall_record"]["comparison_state"]
        == "UNRESOLVED"
    )
    promoted = deepcopy(payload)
    wall = promoted["coordinates"]["wall_record"]
    wall.update(
        {
            "comparison_state": "MISMATCH",
            "result_state": "CERTIFIED",
            "claim_status": "Computational Certificate",
            "value": {"mismatch_count": 1},
        }
    )
    errors = validator_module.semantic_errors(promoted, path)
    assert any("requires two retained Paper XI wall inputs" in error for error in errors)
    assert any("compatibility-only legacy wall observation" in error for error in errors)


def test_wall_binding_is_reserved_for_wall_record_coordinate():
    path, payload = _payloads()[0]
    modified = deepcopy(payload)
    modified["coordinates"]["support"]["wall_input_binding"] = deepcopy(
        modified["coordinates"]["wall_record"]["wall_input_binding"]
    )
    errors = validator_module.semantic_errors(modified, path)
    assert any("support must not carry a wall_input_binding" in error for error in errors)


def test_retained_wall_input_cannot_reuse_a_generic_audit_artifact():
    path, payload = next(
        (path, payload)
        for path, payload in _payloads()
        if payload["coordinates"]["wall_record"]["comparison_state"]
        == "UNRESOLVED"
    )
    modified = deepcopy(payload)
    wall = modified["coordinates"]["wall_record"]
    wall.update(
        {
            "comparison_state": "MISMATCH",
            "result_state": "CERTIFIED",
            "claim_status": "Computational Certificate",
            "value": {"mismatch_count": 1},
        }
    )
    binding = wall["wall_input_binding"]
    binding.pop("legacy_observation")
    for side in ("reference_wall", "target_wall"):
        binding[side] = {
            "state": "RETAINED",
            "record_ref": f"paper11:{side}:record",
            "signature_ref": f"paper11:{side}:signature",
            "source_artifact_id": "artifact.source-audit",
            "reason": None,
        }
    binding["comparison_context"] = {
        "state": "READY",
        "context_kind": "trajectory",
        "context_alignment_ref": "comparison-specification:parameter-synchronization",
        "orientation_alignment": "same-declared-orientation",
        "field_alignment": "primary-and-context-fields-aligned",
        "reason": None,
    }
    errors = validator_module.semantic_errors(modified, path)
    assert sum("paper-xi-wall-record artifact" in error for error in errors) == 2


if __name__ == "__main__":
    if os.environ.get("RIME_VERIFICATION_SCRATCH") != "1":
        from verification_state import run_script_in_isolation

        raise SystemExit(run_script_in_isolation(ROOT, Path(__file__)))
    test_sofaudit_v2_schema_and_census()
    for name in sorted(
        key
        for key in globals()
        if key.startswith("test_") and key != "test_sofaudit_v2_schema_and_census"
    ):
        globals()[name]()
    print("test_sofaudit_v2.py: OK")
