"""Reference helpers for source-addressed SOFRS validation receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from schemas.contract_api import (
    artifact_reference_errors,
    file_digest,
    load_json,
    resolve_artifact_path,
    schema_errors,
)
from schemas.release_snapshot import resolve_release_reference


ROOT = Path(__file__).resolve().parents[2]
V1_SCHEMA_PATH = ROOT / "schemas" / "sofrs" / "v1.0.schema.json"
V2_SCHEMA_PATH = ROOT / "schemas" / "sofrs" / "v2.0.schema.json"
RECEIPT_SCHEMA_PATH = (
    ROOT / "schemas" / "sofrs" / "report-validation-receipt-v1.0.schema.json"
)
V2_RECEIPT_SCHEMA_PATH = (
    ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.0.schema.json"
)
SOFRS_V2_RELEASE_COMMIT = "c58633494257757e3316f31d8a7cfedc2e75af4e"
DOWNSTREAM_TOP_LEVEL_FIELDS = {
    "reference",
    "candidate",
    "alignment",
    "signature",
    "comparison_role",
    "transformation_contract",
    "contract_evaluation",
    "action_semantics",
    "action_set",
    "selection",
}
REQUIRED_CHECK_IDS = {
    "schema-validation",
    "protocol-ownership-boundary",
    "record-kind-admission",
}
V2_REQUIRED_CHECK_IDS = {
    "artifact-closure",
    "claim-compatibility",
    "claim-external-basis-binding",
    "compiler-output-recompilation",
    "cutoff-provenance",
    "record-kind-boundary",
    "report-assembly-recomputation",
    "schema-validation",
}
V2_CLOSURE_ROLES = (
    "report",
    "capability_manifest",
    "typed_sof_ir",
    "compiler_profile",
    "compiler_output",
    "assembly_profile",
    "assembly_implementation",
)


def _artifact_reference(path: Path, uri: str) -> dict[str, Any]:
    return {
        "uri": uri,
        "digest": {"algorithm": "sha256", "value": file_digest(path)},
    }


def _closure_digest(ordered_artifacts: list[dict[str, Any]]) -> dict[str, str]:
    payload = json.dumps(
        ordered_artifacts,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {"algorithm": "sha256", "value": hashlib.sha256(payload).hexdigest()}


def _v1_report_errors(report: dict[str, Any]) -> list[str]:
    errors = schema_errors(report, load_json(V1_SCHEMA_PATH))
    reserved = sorted(DOWNSTREAM_TOP_LEVEL_FIELDS.intersection(report))
    if reserved:
        errors.append(
            "downstream Paper XIII/XIV fields appear at SOFRS top level: "
            + ", ".join(reserved)
        )
    if not report.get("sectorization", {}).get("strict_sof_realization"):
        errors.append("frozen SOFRS v1 report lacks strict compatibility marker")
    return errors


def build_v1_report_validation_receipt(
    report_path: str | Path,
    *,
    report_uri: str,
    contract_uri: str = "schemas/sofrs/v1.0.schema.json",
) -> dict[str, Any]:
    path = Path(report_path)
    report = load_json(path)
    errors = _v1_report_errors(report)
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))
    report_id = report.get("report_id")
    if not isinstance(report_id, str) or not report_id:
        raise ValueError(f"{path}: report_id is required for a validation receipt")
    return {
        "receipt_version": "1.0",
        "artifact_type": "sofrs_report_validation_receipt",
        "receipt_id": f"receipt.{report_id}.sofrs-v1",
        "report": {
            "report_id": report_id,
            "sofrs_version": "1.0",
            "record_kind": "strict_sof",
            "artifact": _artifact_reference(path, report_uri),
        },
        "validator": {
            "validator_id": "sofrs.report-validator.v1",
            "validator_version": "1.0",
            "contract": _artifact_reference(V1_SCHEMA_PATH, contract_uri),
        },
        "status": "PASS",
        "checks": [
            {"check_id": check_id, "status": "PASS"}
            for check_id in sorted(REQUIRED_CHECK_IDS)
        ],
        "negative_boundaries": [
            "This receipt validates the frozen SOFRS v1 envelope, ownership boundary, and legacy strict-admission marker; it does not reconstruct native SOFRS v2 compiler contracts or establish adapter adequacy."
        ],
    }


def build_v2_report_validation_receipt(
    report_path: str | Path,
    *,
    report_uri: str,
    validator_path: str | Path,
    validator_uri: str,
    receipt_contract_uri: str = (
        "schemas/sofrs/report-validation-receipt-v2.0.schema.json"
    ),
) -> dict[str, Any]:
    path = Path(report_path)
    validator = Path(validator_path)
    report = load_json(path)
    errors = schema_errors(report, load_json(V2_SCHEMA_PATH))
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))

    contracts = report["compiler_contracts"]
    ordered_artifacts = [
        {"role": "report", "artifact": _artifact_reference(path, report_uri)},
        {"role": "capability_manifest", "artifact": contracts["capability_manifest"]},
        {"role": "typed_sof_ir", "artifact": contracts["typed_sof_ir"]},
        {"role": "compiler_profile", "artifact": contracts["compiler_profile"]},
        {"role": "compiler_output", "artifact": contracts["compiler_output"]},
        {
            "role": "assembly_profile",
            "artifact": report["assembly_contract"]["assembly_profile"],
        },
        {
            "role": "assembly_implementation",
            "artifact": report["assembly_contract"]["implementation"],
        },
    ]
    return {
        "receipt_version": "2.0",
        "artifact_type": "sofrs_report_validation_receipt",
        "receipt_id": f"receipt.{report['report_id']}.sofrs-v2",
        "report": {
            "report_id": report["report_id"],
            "sofrs_version": "2.0",
            "record_kind": report["record_kind"],
            "artifact": ordered_artifacts[0]["artifact"],
        },
        "validator": {
            "validator_id": "sofrs.report-validator.v2",
            "validator_version": "2.0",
            "implementation": _artifact_reference(validator, validator_uri),
            "receipt_contract": _artifact_reference(
                V2_RECEIPT_SCHEMA_PATH, receipt_contract_uri
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
            for check_id in sorted(V2_REQUIRED_CHECK_IDS)
        ],
        "negative_boundaries": [
            "This receipt validates the bound SOFRS v2 report and compiler-contract closure; it does not establish adapter scientific adequacy, cross-report alignment, or downstream interpretation."
        ],
    }


def v2_report_validation_receipt_errors(
    receipt: dict[str, Any],
    *,
    repository_root: str | Path,
    expected_report_reference: dict[str, Any] | None = None,
    expected_report_base_directory: str | Path | None = None,
    historical_commit: str | None = SOFRS_V2_RELEASE_COMMIT,
) -> list[str]:
    root = Path(repository_root).resolve()
    errors = schema_errors(receipt, load_json(V2_RECEIPT_SCHEMA_PATH))
    if errors:
        return errors

    checks = [item["check_id"] for item in receipt["checks"]]
    if len(checks) != len(set(checks)) or set(checks) != V2_REQUIRED_CHECK_IDS:
        errors.append("v2 receipt checks must contain each required check exactly once")

    closure = receipt["artifact_closure"]
    ordered = closure["ordered_artifacts"]
    if [item["role"] for item in ordered] != list(V2_CLOSURE_ROLES):
        errors.append("v2 receipt artifact closure roles are not canonical")
    if closure["artifact_count"] != len(ordered):
        errors.append("v2 receipt artifact_count differs from its closure")
    if closure["closure_digest"] != _closure_digest(ordered):
        errors.append("v2 receipt artifact closure digest mismatch")

    references = [item["artifact"] for item in ordered]
    references.extend(
        [
            receipt["validator"]["implementation"],
            receipt["validator"]["receipt_contract"],
        ]
    )
    for index, reference in enumerate(references):
        reference_errors = artifact_reference_errors(
            reference,
            label=f"v2 receipt artifact[{index}]",
            repository_root=root,
        )
        errors.extend(reference_errors)

    report_ref = receipt["report"]["artifact"]
    if report_ref != ordered[0]["artifact"]:
        errors.append("v2 receipt report reference differs from closure report")
    if receipt["validator"]["implementation"]["uri"] != (
        "experiments/paper12/validation/validate_sofrs_v2.py"
    ):
        errors.append("v2 receipt does not bind the canonical Paper XII validator")
    if receipt["validator"]["receipt_contract"]["uri"] != (
        "schemas/sofrs/report-validation-receipt-v2.0.schema.json"
    ):
        errors.append("v2 receipt does not bind the canonical receipt contract")

    try:
        report_path = resolve_release_reference(
            report_ref, repository_root=root
        )
    except (KeyError, ValueError):
        report_path = None
    if report_path is not None and report_path.is_file():
        report = load_json(report_path)
        errors.extend(schema_errors(report, load_json(V2_SCHEMA_PATH)))
        for field in ("report_id", "sofrs_version", "record_kind"):
            if report.get(field) != receipt["report"][field]:
                errors.append(f"v2 receipt {field} differs from bound report")
        if report.get("source_mapping", {}).get("status") == "heuristic":
            errors.append("heuristic source mapping cannot enter a validated report")
        expected_contracts = [
            report["compiler_contracts"]["capability_manifest"],
            report["compiler_contracts"]["typed_sof_ir"],
            report["compiler_contracts"]["compiler_profile"],
            report["compiler_contracts"]["compiler_output"],
            report["assembly_contract"]["assembly_profile"],
            report["assembly_contract"]["implementation"],
        ]
        if references[1:7] != expected_contracts:
            errors.append("v2 receipt closure differs from report assembly inputs")

    if expected_report_reference is not None:
        expected_artifact = expected_report_reference["artifact"]
        try:
            expected_path = resolve_release_reference(
                expected_artifact,
                repository_root=root,
                base_directory=expected_report_base_directory,
            )
        except (KeyError, ValueError):
            expected_path = None
        if expected_path is not None and report_path is not None:
            if expected_path != report_path:
                errors.append("v2 receipt binds a different report artifact")
        if expected_artifact.get("digest") != report_ref["digest"]:
            errors.append("v2 receipt report digest differs from source report reference")
        for field in ("report_id", "sofrs_version", "record_kind"):
            if expected_report_reference.get(field) != receipt["report"][field]:
                errors.append(f"v2 receipt {field} differs from source report reference")
    return errors


def report_validation_receipt_errors(
    receipt: dict[str, Any],
    *,
    repository_root: str | Path,
    expected_report_reference: dict[str, Any] | None = None,
    expected_report_base_directory: str | Path | None = None,
) -> list[str]:
    if receipt.get("receipt_version") == "2.0":
        return v2_report_validation_receipt_errors(
            receipt,
            repository_root=repository_root,
            expected_report_reference=expected_report_reference,
            expected_report_base_directory=expected_report_base_directory,
        )
    root = Path(repository_root).resolve()
    errors = schema_errors(receipt, load_json(RECEIPT_SCHEMA_PATH))
    if errors:
        return errors

    checks = [item["check_id"] for item in receipt["checks"]]
    if len(checks) != len(set(checks)) or set(checks) != REQUIRED_CHECK_IDS:
        errors.append("receipt checks must contain each required check exactly once")

    report_ref = receipt["report"]["artifact"]
    contract_ref = receipt["validator"]["contract"]
    errors.extend(
        artifact_reference_errors(
            report_ref,
            label="receipt report artifact",
            repository_root=root,
        )
    )
    errors.extend(
        artifact_reference_errors(
            contract_ref,
            label="receipt validator contract",
            repository_root=root,
        )
    )
    if contract_ref["uri"] != "schemas/sofrs/v1.0.schema.json":
        errors.append("SOFRS v1 receipt must bind the canonical v1.0 schema")

    try:
        report_path = resolve_release_reference(
            report_ref, repository_root=root
        )
    except (KeyError, ValueError):
        report_path = None
    if report_path is not None and report_path.is_file():
        report = load_json(report_path)
        errors.extend(_v1_report_errors(report))
        if report.get("report_id") != receipt["report"]["report_id"]:
            errors.append("receipt report_id differs from bound report")
        if report.get("sofrs_version") != receipt["report"]["sofrs_version"]:
            errors.append("receipt SOFRS version differs from bound report")

    if expected_report_reference is not None:
        expected_artifact = expected_report_reference["artifact"]
        try:
            expected_path = resolve_release_reference(
                expected_artifact,
                repository_root=root,
                base_directory=expected_report_base_directory,
            )
        except (KeyError, ValueError):
            expected_path = None
        if expected_path is not None and report_path is not None:
            if expected_path != report_path:
                errors.append("receipt binds a different report artifact")
        if expected_artifact.get("digest") != report_ref["digest"]:
            errors.append("receipt report digest differs from source report reference")
        for field in ("report_id", "sofrs_version", "record_kind"):
            if expected_report_reference.get(field) != receipt["report"][field]:
                errors.append(f"receipt {field} differs from source report reference")
    return errors
