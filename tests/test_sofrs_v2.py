"""Regression checks for SOFRS v2 migration and compiler-output binding."""

from __future__ import annotations

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if os.environ.get("RIME_VERIFICATION_SCRATCH") != "1":
    if __name__ == "__main__":
        from verification_state import run_script_in_isolation

        raise SystemExit(run_script_in_isolation(ROOT, Path(__file__)))
    raise RuntimeError("generative SOFRS regression requires verification scratch")

MIGRATOR = (
    ROOT / "experiments" / "paper12" / "validation" / "migrate_sofrs_v1_to_v2.py"
)
VALIDATOR = ROOT / "experiments" / "paper12" / "validation" / "validate_sofrs_v2.py"
INDEX = ROOT / "experiments" / "paper12" / "results" / "migration-index.json"
RECEIPT_DIR = (
    ROOT
    / "experiments"
    / "paper12"
    / "results"
    / "report-validation-receipts"
    / "paper12-v2"
)


def _load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

for script in (MIGRATOR, VALIDATOR):
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    assert result.returncode == 0, f"{script.name} failed"

index = json.loads(INDEX.read_text(encoding="utf-8"))
assert len(index["records"]) == 9
assert sum(entry["record_kind"] == "strict_sof" for entry in index["records"]) == 0
assert sum(entry["record_kind"] == "diagnostic_analogue" for entry in index["records"]) == 9
assert sum(
    entry["strict_reconstruction"]["candidate_status"] == "yes"
    for entry in index["records"]
) == 4
expected_cutoffs = {"qwen": 3, "recommender": 8, "transformer_batch": 4}
for entry in index["records"]:
    output_path = ROOT / entry["compiler_output"]
    report_path = ROOT / entry["report"]
    assert output_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["source_mapping"]["status"] == "migrated"
    assert report["source_mapping"]["status"] != "heuristic"
    assert (
        report["compiler_contracts"]["compiler_output"]["uri"]
        == entry["compiler_output"]
    )
    assert entry["producer"] in {
        reference["uri"] for reference in report["source_artifacts"]
    }
    registry = report["external_basis_registry"]
    assert registry["basis_status"] == "PARTIAL"
    packages = {item["basis_id"]: item for item in registry["packages"]}
    assert packages["basis.source.identity"]["status"] == "SATISFIED"
    assert packages["basis.object.recomputation"]["status"] == "NOT_ASSESSED"
    assert packages["basis.semantic.adequacy"]["status"] == "NOT_ASSESSED"
    for claim in report["claims"]:
        assert claim["claim_target"] == "representation_interface"
        assert claim["certificate_class"] is None
        assert claim["classification_source"] == "migration_adapter"
        assert claim["external_basis_refs"] == ["basis.source.identity"]
        assert claim["external_constraint_ids"] == ["source-snapshot-pinned"]
    source_name = Path(entry["source"]).stem
    if source_name in expected_cutoffs:
        ir = json.loads((ROOT / entry["ir"]).read_text(encoding="utf-8"))
        cutoff_policies = [
            policy for policy in ir["run_policies"] if policy["kind"] == "cutoff"
        ]
        assert len(cutoff_policies) == 1
        assert (
            cutoff_policies[0]["specification"]["maximum_depth"]
            == expected_cutoffs[source_name]
        )

validator_module = _load_module("paper12_sofrs_v2_validator", VALIDATOR)
migrator_module = _load_module("paper12_sofrs_v2_migrator", MIGRATOR)
identity_module = _load_module(
    "paper12_canonical_identity",
    ROOT / "experiments" / "paper12" / "validation" / "canonical_identity.py",
)
strict_reconstruction = migrator_module.reconstruction_assessment(
    {
        "record_kind": "strict_sof",
        "enumerable_reconstruction_obligations": False,
    }
)
assert strict_reconstruction["candidate_status"] == "not_applicable"
receipt_paths = sorted(RECEIPT_DIR.glob("*.validation-receipt.json"))
assert len(receipt_paths) == 9
for receipt_path in receipt_paths:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert not validator_module.v2_report_validation_receipt_errors(
        receipt,
        repository_root=ROOT,
    )

tampered_receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8"))
tampered_receipt = deepcopy(tampered_receipt)
tampered_receipt["artifact_closure"]["ordered_artifacts"][0]["artifact"][
    "digest"
]["value"] = "0" * 64
assert any(
    "closure digest mismatch" in error
    for error in validator_module.v2_report_validation_receipt_errors(
        tampered_receipt,
        repository_root=ROOT,
    )
)

entry = index["records"][0]
manifest = validator_module.load_json(ROOT / entry["manifest"])
ir = validator_module.load_json(ROOT / entry["ir"])
report = validator_module.load_json(ROOT / entry["report"])
compiler_output = validator_module.load_json(ROOT / entry["compiler_output"])
profile_path = (
    validator_module.STRICT_COMPILER_PROFILE
    if report["record_kind"] == "strict_sof"
    else validator_module.ANALOGUE_COMPILER_PROFILE
)
profile = validator_module.load_json(profile_path)
rules = validator_module.load_json(validator_module.RULE_REGISTRY_PATH)

presentation_only_variant = deepcopy(report)
presentation_only_variant["failure_modes"] = ["presentation-only rendering note"]
presentation_only_variant["provenance"] = {"presentation_only": True}
assembly_profile = validator_module.load_json(
    validator_module.ANALOGUE_ASSEMBLY_PROFILE
)
assert identity_module.semantic_report_equal(
    report, presentation_only_variant, assembly_profile
)
assert identity_module.canonical_artifact_digest(report) != identity_module.canonical_artifact_digest(
    presentation_only_variant
)
assert identity_module.canonical_artifact_digest(report) == identity_module.canonical_artifact_digest(
    deepcopy(report)
)

tampered = deepcopy(compiler_output)
tampered["items"][0]["module_id"] = "module.tampered"
assert any(
    "differs from canonical" in error
    for error in validator_module.compiler_output_errors(
        manifest, ir, profile, tampered, rules
    )
)

assembly_profile_path = (
    validator_module.STRICT_ASSEMBLY_PROFILE
    if report["record_kind"] == "strict_sof"
    else validator_module.ANALOGUE_ASSEMBLY_PROFILE
)
assembly_profile = validator_module.load_json(assembly_profile_path)
tampered_report = deepcopy(report)
tampered_report["claims"] = []
assert any(
    "not faithful" in error
    or "adds or removes" in error
    or "lacks an assembly classification" in error
    or "do not cover exactly the report normative items" in error
    for error in validator_module.assembly_faithfulness_errors(
        tampered_report,
        compiler_output,
        ir,
        profile,
        assembly_profile,
    )
)

tampered_binding = deepcopy(report)
tampered_binding["item_bindings"].append(
    deepcopy(tampered_binding["item_bindings"][0])
)
assert any(
    "duplicates" in error or "bijection" in error
    for error in validator_module.assembly_faithfulness_errors(
        tampered_binding,
        compiler_output,
        ir,
        profile,
        assembly_profile,
    )
)

cutoff_entry = next(
    item for item in index["records"] if Path(item["source"]).stem == "transformer_batch"
)
cutoff_ir = validator_module.load_json(ROOT / cutoff_entry["ir"])
tampered_cutoff_ir = deepcopy(cutoff_ir)
cutoff_policy = next(
    policy for policy in tampered_cutoff_ir["run_policies"] if policy["kind"] == "cutoff"
)
del cutoff_policy["specification"]["maximum_depth"]
assert any(
    "positive maximum_depth" in error
    for error in validator_module.cutoff_errors(tampered_cutoff_ir)
)

tampered_source_mapping = deepcopy(report)
tampered_source_mapping["source_mapping"]["status"] = "heuristic"
assert validator_module.source_mapping_errors(tampered_source_mapping, manifest)

tampered_target = deepcopy(report)
tampered_target["claims"][0]["claim_target"] = "external_mathematical_object"
assert any(
    "target and certificate class" in error
    for error in validator_module.epistemic_classification_errors(tampered_target)
)

tampered_source = deepcopy(report)
tampered_source["claims"][0]["classification_source"] = "assembly_profile"
assert any(
    "classification source" in error
    for error in validator_module.epistemic_classification_errors(tampered_source)
)

tampered_pairing = deepcopy(report)
tampered_pairing["claims"][0]["result_state"] = "CERTIFIED"
assert any(
    "must pair with Computational Certificate" in error
    for error in validator_module.epistemic_classification_errors(tampered_pairing)
)

tampered_object_source = deepcopy(report)
tampered_object_source["claims"][0].update(
    {
        "result_state": "CERTIFIED",
        "claim_status": "Computational Certificate",
        "claim_target": "external_mathematical_object",
        "certificate_class": "object",
        "classification_source": "assembly_profile",
    }
)
assert any(
    "classification source assembly_profile cannot establish" in error
    for error in validator_module.epistemic_classification_errors(tampered_object_source)
)

tampered_claim_basis = deepcopy(report)
tampered_claim_basis["claims"][0]["external_basis_refs"] = [
    "basis.object.recomputation"
]
assert any(
    "does not bind the basis package" in error
    for error in validator_module.external_basis_errors(tampered_claim_basis)
)

tampered_complete_basis = deepcopy(report)
tampered_complete_basis["external_basis_registry"]["basis_status"] = "COMPLETE"
assert any(
    "COMPLETE external basis" in error
    for error in validator_module.external_basis_errors(tampered_complete_basis)
)

tampered_object_claim = deepcopy(report)
tampered_object_claim["claims"][0]["claim_status"] = "Computational Certificate"
tampered_object_claim["claims"][0]["claim_target"] = "external_mathematical_object"
tampered_object_claim["claims"][0]["certificate_class"] = "object"
tampered_object_claim["claims"][0]["external_basis_refs"] = [
    "basis.object.recomputation"
]
tampered_object_claim["claims"][0]["external_constraint_ids"] = [
    "object-level-recomputation"
]
assert any(
    "Object Certificate lacks a satisfied external object basis" in error
    for error in validator_module.external_basis_errors(tampered_object_claim)
)

tampered_external_digest = deepcopy(report)
tampered_external_digest["external_basis_registry"]["packages"][0][
    "evidence_artifacts"
][0]["digest"]["value"] = "0" * 64
assert any(
    "external source identity evidence" in error
    for error in validator_module.external_basis_errors(tampered_external_digest)
)

tampered_digest_shape = deepcopy(report)
tampered_digest_shape["source_artifacts"][0]["digest"]["value"] = "x"
report_schema = validator_module.load_json(validator_module.REPORT_SCHEMA_PATH)
assert validator_module.schema_errors(tampered_digest_shape, report_schema)

tampered_carrier = deepcopy(report)
tampered_carrier["claims"][0]["carrier_kinds"] = ["operator"]
assert any(
    "summary differs from IR" in error
    for error in validator_module.summary_errors(tampered_carrier, ir)
)

synthetic_degradation_output = {
    "items": [
        {
            "item_kind": "degradation",
            "module_id": "associative",
            "action": "emit_unavailable",
            "reason_kind": "missing_capability",
            "details": ["word carrier is not declared"],
        }
    ]
}
synthetic_claims, synthetic_degradations, synthetic_bindings = (
    validator_module.assemble_normative_items(synthetic_degradation_output, ir)
)
assert synthetic_claims == []
assert len(synthetic_degradations) == 1
assert synthetic_degradations[0]["source_output_item_id"] == "compiler.item.0000"
assert synthetic_bindings[0]["item_kind"] == "degradation"

print("test_sofrs_v2.py: OK")
