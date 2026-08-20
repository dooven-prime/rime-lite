"""Validate explicitly migrated SOFRS v2.1 reports and their receipts."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper12.validation.validate_sofrs_v2 import standalone_report_errors
from schemas.non_intervention import (
    SOFRS_FORBIDDEN_KEYS,
    SOFRS_OBJECT_TRANSITION_BOUNDARY,
    artifact_reference,
    closure_digest,
    exact_check_set_errors,
    file_digest,
    forbidden_key_errors,
    resolve_reference,
    write_json,
)
from schemas.sofrs.api import v2_report_validation_receipt_errors


REPORT_SCHEMA = ROOT / "schemas" / "sofrs" / "v2.1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.1.schema.json"
MIGRATOR = HERE / "migrate_sofrs_v2_to_v2_1.py"
LEGACY_V2_VALIDATOR = HERE / "validate_sofrs_v2.py"
LEGACY_V2_REPORT_SCHEMA = ROOT / "schemas" / "sofrs" / "v2.0.schema.json"
LEGACY_V2_RECEIPT_SCHEMA = ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.0.schema.json"
V2_RECEIPT_API = ROOT / "schemas" / "sofrs" / "api.py"
BOUNDARY_HELPER = ROOT / "schemas" / "non_intervention.py"
DEFAULT_DIR = PAPER_DIR / "results" / "v2.1" / "reports"
DEFAULT_RECEIPT_DIR = PAPER_DIR / "results" / "v2.1" / "report-validation-receipts"

COMMON_CHECKS = {
    "artifact-closure",
    "assembly-faithfulness",
    "claim-compatibility",
    "degradation-semantics",
    "forbidden-semantic-role-scan",
    "report-non-intervention",
    "schema-validation",
}
MIGRATION_CHECKS = COMMON_CHECKS | {
    "explicit-v2.0-to-v2.1-migration",
    "v2.0-source-validation",
}
NATIVE_CHECKS = COMMON_CHECKS | {
    "generation-input-closure",
    "native-v2.1-generation",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(payload: dict[str, Any], schema_path: Path) -> list[str]:
    validator = Draft202012Validator(load_json(schema_path))
    return sorted(error.message for error in validator.iter_errors(payload))


def _reference_errors(reference: dict[str, Any], label: str) -> tuple[Path | None, list[str]]:
    return resolve_reference(reference, root=ROOT, label=label)


def _source_receipt_errors(
    source_path: Path,
    source_reference: dict[str, Any],
    receipt_reference: dict[str, Any],
) -> list[str]:
    receipt_path, errors = _reference_errors(
        receipt_reference, "v2.0 source validation receipt"
    )
    if receipt_path is None:
        return errors
    stem = source_path.name.removesuffix(".sofreport.json")
    expected_paths = {
        PAPER_DIR
        / "results"
        / "report-validation-receipts"
        / "paper12-v2"
        / f"{stem}.validation-receipt.json"
    }
    # Paper-owned source-report bundles keep their receipts beside the bundle,
    # while native Paper XII reports use the historical paper12-v2 directory.
    if source_path.parent.name == "reports" and source_path.parent.parent.name == "source-reports":
        expected_paths.add(
            source_path.parent.parent / "receipts" / f"{stem}.validation-receipt.json"
        )
    if receipt_path not in expected_paths:
        errors.append("v2.1 migration binds a non-canonical v2.0 source receipt")
    receipt = load_json(receipt_path)
    source = load_json(source_path)
    expected_report_reference = {
        "report_id": source["report_id"],
        "sofrs_version": source["sofrs_version"],
        "record_kind": source["record_kind"],
        "artifact": source_reference,
    }
    errors.extend(
        f"v2.0 source receipt: {error}"
        for error in v2_report_validation_receipt_errors(
            receipt,
            repository_root=ROOT,
            expected_report_reference=expected_report_reference,
        )
    )
    return errors


def _native_body_errors(payload: dict[str, Any]) -> list[str]:
    projection = deepcopy(payload)
    projection["sofrs_version"] = "2.0"
    projection.pop("revision_provenance", None)
    projection.pop("object_transition_boundary", None)
    with tempfile.TemporaryDirectory(prefix="sofrs-v2_1-") as directory:
        path = Path(directory) / "native-v2-projection.sofreport.json"
        write_json(path, projection)
        return standalone_report_errors(path)


def report_errors(report_path: Path) -> list[str]:
    payload = load_json(report_path)
    errors = schema_errors(payload, REPORT_SCHEMA)
    if errors:
        return errors

    errors.extend(forbidden_key_errors(payload, SOFRS_FORBIDDEN_KEYS, label="SOFRS v2.1 report"))
    if payload["object_transition_boundary"] != SOFRS_OBJECT_TRANSITION_BOUNDARY:
        errors.append("SOFRS object_transition_boundary is not the v2.1 fixed non-intervention boundary")

    revision = payload["revision_provenance"]
    if revision["kind"] == "native_v2_1_generation":
        _, implementation_errors = _reference_errors(
            revision["generation_implementation"], "native generation implementation"
        )
        errors.extend(implementation_errors)
        for index, reference in enumerate(revision["generation_inputs"]):
            _, input_errors = _reference_errors(reference, f"native generation input {index}")
            errors.extend(input_errors)
        errors.extend(f"native v2.1 body: {error}" for error in _native_body_errors(payload))
        return errors

    source_path, source_errors = _reference_errors(
        revision["source_artifact"], "revision source report"
    )
    errors.extend(source_errors)
    migrator_path, migrator_errors = _reference_errors(
        revision["migration_implementation"], "revision migration implementation"
    )
    errors.extend(migrator_errors)
    if migrator_path != MIGRATOR:
        errors.append("revision provenance does not bind the canonical SOFRS v2.1 migrator")
    if source_path is None:
        return errors

    source = load_json(source_path)
    if source.get("sofrs_version") != "2.0":
        errors.append("revision source report is not SOFRS v2.0")
        return errors
    errors.extend(f"v2.0 source: {error}" for error in standalone_report_errors(source_path))
    errors.extend(
        _source_receipt_errors(
            source_path,
            revision["source_artifact"],
            revision["source_validation_receipt"],
        )
    )

    expected = deepcopy(source)
    expected["sofrs_version"] = "2.1"
    expected["revision_provenance"] = revision
    expected["object_transition_boundary"] = SOFRS_OBJECT_TRANSITION_BOUNDARY
    if payload != expected:
        errors.append("v2.1 report differs from its exact v2.0 migration projection")
    return errors


def _ordered_artifacts(report_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    revision = payload["revision_provenance"]
    contracts = payload["compiler_contracts"]
    ordered = [{"role": "report", "artifact": artifact_reference(report_path, ROOT)}]
    if revision["kind"] == "explicit_v2_0_to_v2_1_migration":
        ordered.extend([
            {"role": "revision-source-report-v2.0", "artifact": revision["source_artifact"]},
            {
                "role": "source-validation-receipt-v2.0",
                "artifact": revision["source_validation_receipt"],
            },
            {"role": "migration-implementation", "artifact": revision["migration_implementation"]},
            {"role": "legacy-v2-validator", "artifact": artifact_reference(LEGACY_V2_VALIDATOR, ROOT)},
            {"role": "legacy-v2-report-contract", "artifact": artifact_reference(LEGACY_V2_REPORT_SCHEMA, ROOT)},
            {"role": "legacy-v2-receipt-contract", "artifact": artifact_reference(LEGACY_V2_RECEIPT_SCHEMA, ROOT)},
            {"role": "v2-receipt-api", "artifact": artifact_reference(V2_RECEIPT_API, ROOT)},
        ])
    else:
        ordered.append(
            {"role": "generation-implementation", "artifact": revision["generation_implementation"]}
        )
        ordered.extend(
            {"role": f"generation-input-{index}", "artifact": reference}
            for index, reference in enumerate(revision["generation_inputs"])
        )
    ordered.append({"role": "boundary-helper", "artifact": artifact_reference(BOUNDARY_HELPER, ROOT)})
    ordered.extend([
        {"role": "report-contract", "artifact": artifact_reference(REPORT_SCHEMA, ROOT)},
        {"role": "capability-manifest", "artifact": contracts["capability_manifest"]},
        {"role": "typed-sof-ir", "artifact": contracts["typed_sof_ir"]},
        {"role": "compiler-profile", "artifact": contracts["compiler_profile"]},
        {"role": "compiler-output", "artifact": contracts["compiler_output"]},
        {"role": "assembly-profile", "artifact": payload["assembly_contract"]["assembly_profile"]},
        {"role": "assembly-implementation", "artifact": payload["assembly_contract"]["implementation"]},
        {"role": "validator-implementation", "artifact": artifact_reference(Path(__file__), ROOT)},
        {"role": "validation-receipt-contract", "artifact": artifact_reference(RECEIPT_SCHEMA, ROOT)},
    ])
    return ordered


def _receipt_generation(payload: dict[str, Any]) -> dict[str, Any]:
    revision = payload["revision_provenance"]
    if revision["kind"] == "explicit_v2_0_to_v2_1_migration":
        return {
            "kind": "migration",
            "class": "boundary_annotation",
            "source_version": "2.0",
            "source_artifact": revision["source_artifact"],
            "source_validation_receipt": revision["source_validation_receipt"],
            "implementation": revision["migration_implementation"],
        }
    return {
        "kind": "native",
        "implementation": revision["generation_implementation"],
        "input_artifacts": revision["generation_inputs"],
    }


def build_validation_receipt(report_path: Path) -> dict[str, Any]:
    errors = report_errors(report_path)
    if errors:
        raise ValueError(f"{report_path}: " + "; ".join(errors))
    payload = load_json(report_path)
    ordered = _ordered_artifacts(report_path, payload)
    role_map = {item["role"]: item["artifact"] for item in ordered}
    checks = MIGRATION_CHECKS if payload["revision_provenance"]["kind"].startswith("explicit_") else NATIVE_CHECKS
    return {
        "receipt_version": "2.1",
        "artifact_type": "sofrs_report_validation_receipt",
        "receipt_kind": "SOFRS_VALIDATION_RECEIPT",
        "receipt_scope": "SOFRS_PROTOCOL_CONFORMANCE_ONLY",
        "receipt_id": f"receipt.{payload['report_id']}.sofrs-v2_1",
        "report": {
            "report_id": payload["report_id"],
            "sofrs_version": "2.1",
            "record_kind": payload["record_kind"],
            "artifact": ordered[0]["artifact"],
        },
        "validator": {
            "validator_id": "sofrs.report-validator.v2_1",
            "validator_version": "2.1",
            "implementation": role_map["validator-implementation"],
            "report_contract": role_map["report-contract"],
            "receipt_contract": role_map["validation-receipt-contract"],
        },
        "generation": _receipt_generation(payload),
        "artifact_closure": {
            "artifact_count": len(ordered),
            "ordered_artifacts": ordered,
            "closure_digest": closure_digest(ordered),
        },
        "status": "PASS",
        "checks": [
            {"check_id": check_id, "status": "PASS"}
            for check_id in sorted(checks)
        ],
        "object_transition_boundary": {
            "intervention_semantics": "NONE",
            "source_state_transition_authority": "NONE",
            "implementation_purity_status": "NOT_ESTABLISHED_BY_SOFRS",
        },
        "negative_boundaries": [
            "This receipt establishes SOFRS protocol conformance only; it neither induces nor authorizes an object-state transition, and it does not establish implementation purity."
        ],
    }


def receipt_errors(receipt: dict[str, Any]) -> list[str]:
    errors = schema_errors(receipt, RECEIPT_SCHEMA)
    if errors:
        return errors
    expected_checks = MIGRATION_CHECKS if receipt["generation"]["kind"] == "migration" else NATIVE_CHECKS
    errors.extend(exact_check_set_errors(receipt["checks"], expected_checks, label="SOFRS v2.1 receipt"))
    if receipt["object_transition_boundary"] != {
        "intervention_semantics": "NONE",
        "source_state_transition_authority": "NONE",
        "implementation_purity_status": "NOT_ESTABLISHED_BY_SOFRS",
    }:
        errors.append("receipt object-transition boundary is not fixed")

    ordered = receipt["artifact_closure"]["ordered_artifacts"]
    if receipt["artifact_closure"]["artifact_count"] != len(ordered):
        errors.append("receipt artifact_count differs from ordered artifact count")
    if receipt["artifact_closure"]["closure_digest"] != closure_digest(ordered):
        errors.append("receipt closure digest is incorrect")
    roles = [item["role"] for item in ordered]
    if len(roles) != len(set(roles)):
        errors.append("receipt artifact closure roles are not unique")
    for item in ordered:
        _, reference_errors = _reference_errors(item["artifact"], f"receipt role {item['role']}")
        errors.extend(reference_errors)

    report_ref = receipt["report"]["artifact"]
    report_path, report_reference_errors = _reference_errors(report_ref, "receipt report")
    errors.extend(report_reference_errors)
    if ordered and report_ref != ordered[0]["artifact"]:
        errors.append("receipt report reference differs from closure")
    if report_path is None:
        return errors
    errors.extend(report_errors(report_path))
    payload = load_json(report_path)
    if receipt["report"]["report_id"] != payload["report_id"]:
        errors.append("receipt report_id differs from report")
    if receipt["generation"] != _receipt_generation(payload):
        errors.append("receipt generation provenance differs from report revision provenance")
    if receipt["validator"]["implementation"] != artifact_reference(Path(__file__), ROOT):
        errors.append("receipt validator implementation differs from canonical validator")
    if receipt["validator"]["report_contract"] != artifact_reference(REPORT_SCHEMA, ROOT):
        errors.append("receipt report contract differs from canonical v2.1 schema")
    if receipt["validator"]["receipt_contract"] != artifact_reference(RECEIPT_SCHEMA, ROOT):
        errors.append("receipt contract differs from canonical v2.1 receipt schema")
    expected = _ordered_artifacts(report_path, payload)
    if ordered != expected:
        errors.append("receipt closure differs from report revision closure")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--write-receipts", action="store_true")
    parser.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = args.paths or sorted(DEFAULT_DIR.glob("*.sofreport.json"))
    if not paths:
        raise SystemExit("No SOFRS v2.1 reports found.")
    failures = 0
    for path in paths:
        errors = report_errors(path)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
            continue
        print(f"PASS {path}")
        if args.write_receipts:
            receipt_path = args.receipt_dir / path.name.replace(".sofreport.json", ".validation-receipt.json")
            receipt = build_validation_receipt(path)
            receipt_validation_errors = receipt_errors(receipt)
            if receipt_validation_errors:
                failures += 1
                print(f"FAIL {receipt_path}")
                for error in receipt_validation_errors:
                    print(f"  - {error}")
            else:
                write_json(receipt_path, receipt)
                print(f"PASS {receipt_path}")
    if failures:
        raise SystemExit(f"{failures} SOFRS v2.1 item(s) failed validation.")


if __name__ == "__main__":
    main()
