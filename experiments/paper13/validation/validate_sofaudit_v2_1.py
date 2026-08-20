"""Validate SOFAUDIT v2.1 boundary migrations and validation receipts."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper12.validation.validate_sofrs_v2_1 import (
    receipt_errors as report_receipt_errors,
    report_errors,
)
from experiments.paper13.validation import validate_sofaudit_v2 as v2_validator
from schemas.non_intervention import (
    SOFAUDIT_ATTRIBUTION_BOUNDARY,
    SOFAUDIT_FORBIDDEN_KEYS,
    artifact_reference,
    closure_digest,
    exact_check_set_errors,
    forbidden_key_errors,
    resolve_reference,
    write_json,
)


AUDIT_SCHEMA = ROOT / "schemas" / "sofaudit" / "v2.1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "sofaudit" / "validation-receipt-v2.1.schema.json"
MIGRATOR = HERE / "migrate_sofaudit_v2_to_v2_1.py"
DEFAULT_DIR = PAPER_DIR / "results" / "v2.1" / "audits"
DEFAULT_RECEIPT_DIR = PAPER_DIR / "results" / "v2.1" / "receipts"

COMMON_CHECKS = {
    "aligned-difference-without-attribution",
    "artifact-digest-closure",
    "forbidden-semantic-role-scan",
    "reference-role-boundary",
    "schema-validation",
    "source-report-receipt-validation",
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
    return sorted(
        error.message
        for error in Draft202012Validator(load_json(schema_path)).iter_errors(payload)
    )


def _resolve_from_audit(path: Path, reference: dict[str, Any]) -> tuple[Path, list[str]]:
    uri = reference.get("uri")
    if isinstance(uri, str):
        root_relative = (ROOT / uri).resolve()
        if root_relative.is_file():
            _, errors = resolve_reference(
                reference,
                root=ROOT,
                label=f"artifact {uri}",
            )
            return root_relative, errors
    return v2_validator.resolve_artifact(path.parent, reference)


def _linked_report_errors(
    payload: dict[str, Any],
    target_path: Path,
    source: dict[str, Any],
    source_path: Path,
) -> list[str]:
    errors: list[str] = []
    for side in ("reference", "target"):
        target_ref = payload["source_reports"][side]
        source_ref = source["source_reports"][side]
        target_report_path, resolve_errors = _resolve_from_audit(target_path, target_ref["artifact"])
        errors.extend(resolve_errors)
        target_receipt_path, receipt_resolve_errors = _resolve_from_audit(
            target_path, target_ref["validation_receipt"]
        )
        errors.extend(receipt_resolve_errors)
        source_report_path, source_resolve_errors = v2_validator.resolve_artifact(
            source_path.parent, source_ref["artifact"]
        )
        errors.extend(source_resolve_errors)
        if resolve_errors or receipt_resolve_errors or source_resolve_errors:
            continue

        errors.extend(f"{side} v2.1 report: {error}" for error in report_errors(target_report_path))
        receipt = load_json(target_receipt_path)
        errors.extend(
            f"{side} v2.1 report receipt: {error}"
            for error in report_receipt_errors(receipt)
        )
        report = load_json(target_report_path)
        provenance = report.get("revision_provenance", {})
        if provenance.get("source_artifact") != artifact_reference(source_report_path, ROOT):
            errors.append(f"{side} v2.1 report does not migrate the v2.0 report bound by the source audit")
        if receipt.get("report", {}).get("artifact") != target_ref["artifact"]:
            errors.append(f"{side} report receipt does not bind the report referenced by the audit")
        if target_ref["report_id"] != source_ref["report_id"]:
            errors.append(f"{side} report_id changed during v2.1 migration")
        expected_ref = deepcopy(source_ref)
        expected_ref["artifact"] = target_ref["artifact"]
        expected_ref["validation_receipt"] = target_ref["validation_receipt"]
        expected_ref["sofrs_version"] = "2.1"
        expected_ref["admission_basis"] = "native_sofrs_v2_1"
        if target_ref != expected_ref:
            errors.append(f"{side} source-report metadata changed beyond the v2.1 migration boundary")
    return errors


def _expected_projection(
    source: dict[str, Any],
    source_path: Path,
    target: dict[str, Any],
) -> dict[str, Any]:
    expected = deepcopy(source)
    expected["source_reports"] = deepcopy(target["source_reports"])
    report_roles = {
        "reference-report": target["source_reports"]["reference"]["artifact"],
        "reference-report-validation-receipt": target["source_reports"]["reference"]["validation_receipt"],
        "target-report": target["source_reports"]["target"]["artifact"],
        "target-report-validation-receipt": target["source_reports"]["target"]["validation_receipt"],
    }
    normalized = []
    for artifact in source["source_artifacts"]:
        item = deepcopy(artifact)
        if artifact["role"] in report_roles:
            replacement = report_roles[artifact["role"]]
        else:
            resolved, _ = v2_validator.resolve_artifact(source_path.parent, artifact)
            replacement = artifact_reference(resolved, ROOT)
        item["uri"] = replacement["uri"]
        item["digest"] = replacement["digest"]
        normalized.append(item)
    expected["source_artifacts"] = normalized
    for coordinate in expected["coordinates"].values():
        binding = coordinate.get("report_item_binding", {})
        for side in ("reference", "target"):
            item_ref = binding.get(f"{side}_item_ref")
            if item_ref is not None:
                item_ref["artifact_digest"] = expected["source_reports"][side]["artifact"]["digest"]
    expected["sofaudit_version"] = "2.1"
    expected["revision_provenance"] = target["revision_provenance"]
    expected["attribution_boundary"] = SOFAUDIT_ATTRIBUTION_BOUNDARY
    return expected


def audit_errors(audit_path: Path) -> list[str]:
    payload = load_json(audit_path)
    errors = schema_errors(payload, AUDIT_SCHEMA)
    if errors:
        return errors
    errors.extend(forbidden_key_errors(payload, SOFAUDIT_FORBIDDEN_KEYS, label="SOFAUDIT v2.1"))
    if payload["attribution_boundary"] != SOFAUDIT_ATTRIBUTION_BOUNDARY:
        errors.append("SOFAUDIT attribution boundary is not fixed")

    revision = payload["revision_provenance"]
    if revision["kind"] == "native_v2_1_generation":
        _, implementation_errors = resolve_reference(
            revision["generation_implementation"],
            root=ROOT,
            label="native audit generation implementation",
        )
        errors.extend(implementation_errors)
        for index, reference in enumerate(revision["generation_inputs"]):
            _, input_errors = resolve_reference(
                reference,
                root=ROOT,
                label=f"native audit generation input {index}",
            )
            errors.extend(input_errors)
        errors.extend(
            v2_validator.semantic_errors(
                payload,
                audit_path,
                expected_sofrs_version="2.1",
                report_validator=report_errors,
                report_receipt_validator=report_receipt_errors,
            )
        )
        return errors
    source_path, source_errors = resolve_reference(
        revision["source_artifact"], root=ROOT, label="revision source audit"
    )
    errors.extend(source_errors)
    migrator_path, migrator_errors = resolve_reference(
        revision["migration_implementation"], root=ROOT, label="audit migration implementation"
    )
    errors.extend(migrator_errors)
    if migrator_path != MIGRATOR:
        errors.append("revision provenance does not bind the canonical SOFAUDIT v2.1 migrator")
    if source_path is None:
        return errors
    source = load_json(source_path)
    if source.get("sofaudit_version") != "2.0":
        errors.append("revision source audit is not SOFAUDIT v2.0")
        return errors
    errors.extend(
        f"v2.0 source schema: {error}"
        for error in v2_validator.schema_errors(source, v2_validator.load_json(v2_validator.DEFAULT_SCHEMA))
    )
    errors.extend(f"v2.0 source: {error}" for error in v2_validator.semantic_errors(source, source_path))
    errors.extend(_linked_report_errors(payload, audit_path, source, source_path))
    expected = _expected_projection(source, source_path, payload)
    if payload != expected:
        errors.append("v2.1 audit differs from its exact boundary-annotation migration projection")
    return errors


def _ordered_artifacts(audit_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    revision = payload["revision_provenance"]
    ordered = [{"role": "audit", "artifact": artifact_reference(audit_path, ROOT)}]
    if revision["kind"] == "explicit_v2_0_to_v2_1_migration":
        ordered.extend([
            {"role": "revision-source-audit-v2.0", "artifact": revision["source_artifact"]},
            {"role": "migration-implementation", "artifact": revision["migration_implementation"]},
        ])
    else:
        ordered.append(
            {"role": "generation-implementation", "artifact": revision["generation_implementation"]}
        )
        ordered.extend(
            {"role": f"generation-input-{index}", "artifact": reference}
            for index, reference in enumerate(revision["generation_inputs"])
        )
    ordered.append({"role": "audit-contract", "artifact": artifact_reference(AUDIT_SCHEMA, ROOT)})
    for artifact in payload["source_artifacts"]:
        resolved, resolve_errors = _resolve_from_audit(audit_path, artifact)
        if resolve_errors:
            raise ValueError("; ".join(resolve_errors))
        ordered.append({"role": artifact["role"], "artifact": artifact_reference(resolved, ROOT)})
    ordered.extend(
        [
            {"role": "validator-implementation", "artifact": artifact_reference(Path(__file__), ROOT)},
            {"role": "validation-receipt-contract", "artifact": artifact_reference(RECEIPT_SCHEMA, ROOT)},
        ]
    )
    return ordered


def _receipt_generation(payload: dict[str, Any]) -> dict[str, Any]:
    revision = payload["revision_provenance"]
    if revision["kind"] == "explicit_v2_0_to_v2_1_migration":
        return {
            "kind": "migration",
            "class": "boundary_annotation",
            "source_version": "2.0",
            "source_artifact": revision["source_artifact"],
            "implementation": revision["migration_implementation"],
        }
    return {
        "kind": "native",
        "implementation": revision["generation_implementation"],
        "input_artifacts": revision["generation_inputs"],
    }


def build_validation_receipt(audit_path: Path) -> dict[str, Any]:
    errors = audit_errors(audit_path)
    if errors:
        raise ValueError(f"{audit_path}: " + "; ".join(errors))
    payload = load_json(audit_path)
    ordered = _ordered_artifacts(audit_path, payload)
    role_map = {item["role"]: item["artifact"] for item in ordered}
    checks = MIGRATION_CHECKS if payload["revision_provenance"]["kind"].startswith("explicit_") else NATIVE_CHECKS
    return {
        "receipt_version": "2.1",
        "artifact_type": "sofaudit_validation_receipt",
        "receipt_kind": "SOFAUDIT_VALIDATION_RECEIPT",
        "receipt_scope": "SOFAUDIT_PROTOCOL_CONFORMANCE_ONLY",
        "receipt_id": f"receipt.{payload['audit_id']}.sofaudit-v2_1",
        "audit": {
            "audit_id": payload["audit_id"],
            "sofaudit_version": "2.1",
            "artifact": ordered[0]["artifact"],
        },
        "validator": {
            "validator_id": "sofaudit.semantic-validator.v2_1",
            "validator_version": "2.1",
            "implementation": role_map["validator-implementation"],
            "audit_contract": role_map["audit-contract"],
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
        "attribution_boundary": {
            "causal_status": "OUT_OF_SCOPE_FOR_SOFAUDIT",
            "defect_attribution_status": "OUT_OF_SCOPE_FOR_SOFAUDIT",
            "reference_causal_role": "NOT_A_CAUSAL_BASELINE",
        },
        "negative_boundaries": [
            "This receipt establishes aligned-comparison protocol conformance only; localization is not defect or causal attribution, and the reference is not a causal baseline."
        ],
    }


def receipt_errors(receipt: dict[str, Any]) -> list[str]:
    errors = schema_errors(receipt, RECEIPT_SCHEMA)
    if errors:
        return errors
    expected_checks = MIGRATION_CHECKS if receipt["generation"]["kind"] == "migration" else NATIVE_CHECKS
    errors.extend(exact_check_set_errors(receipt["checks"], expected_checks, label="SOFAUDIT v2.1 receipt"))
    ordered = receipt["artifact_closure"]["ordered_artifacts"]
    closure = receipt["artifact_closure"]
    if closure["artifact_count"] != len(ordered):
        errors.append("receipt artifact_count differs from ordered artifact count")
    if closure["closure_digest"] != closure_digest(ordered):
        errors.append("receipt closure digest is incorrect")
    roles = [item["role"] for item in ordered]
    if len(roles) != len(set(roles)):
        errors.append("receipt artifact roles are not unique")
    for item in ordered:
        _, reference_errors = resolve_reference(
            item["artifact"], root=ROOT, label=f"receipt role {item['role']}"
        )
        errors.extend(reference_errors)
    audit_path, audit_reference_errors = resolve_reference(
        receipt["audit"]["artifact"], root=ROOT, label="receipt audit"
    )
    errors.extend(audit_reference_errors)
    if audit_path is None:
        return errors
    errors.extend(audit_errors(audit_path))
    payload = load_json(audit_path)
    if receipt["audit"]["artifact"] != ordered[0]["artifact"]:
        errors.append("receipt audit reference differs from closure")
    if receipt["generation"] != _receipt_generation(payload):
        errors.append("receipt generation provenance differs from audit")
    if receipt["validator"]["implementation"] != artifact_reference(Path(__file__), ROOT):
        errors.append("receipt validator implementation differs from canonical validator")
    if receipt["validator"]["audit_contract"] != artifact_reference(AUDIT_SCHEMA, ROOT):
        errors.append("receipt audit contract differs from canonical v2.1 schema")
    if receipt["validator"]["receipt_contract"] != artifact_reference(RECEIPT_SCHEMA, ROOT):
        errors.append("receipt contract differs from canonical v2.1 receipt schema")
    if ordered != _ordered_artifacts(audit_path, payload):
        errors.append("receipt closure differs from audit source closure")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--write-receipts", action="store_true")
    parser.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = args.paths or sorted(DEFAULT_DIR.glob("*.sofaudit.json"))
    if not paths:
        raise SystemExit("No SOFAUDIT v2.1 artifacts found.")
    failures = 0
    for path in paths:
        errors = audit_errors(path)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
            continue
        print(f"PASS {path}")
        if args.write_receipts:
            receipt_path = args.receipt_dir / path.name.replace(".sofaudit.json", ".validation-receipt.json")
            receipt = build_validation_receipt(path)
            write_json(receipt_path, receipt)
            receipt_validation_errors = receipt_errors(receipt)
            if receipt_validation_errors:
                failures += 1
                print(f"FAIL {receipt_path}")
                for error in receipt_validation_errors:
                    print(f"  - {error}")
            else:
                print(f"PASS {receipt_path}")
    if failures:
        raise SystemExit(f"{failures} SOFAUDIT v2.1 item(s) failed validation.")


if __name__ == "__main__":
    main()
