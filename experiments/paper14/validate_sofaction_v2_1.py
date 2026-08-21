"""Validate SOFAction v2.1 non-execution migrations and receipts."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper13.validation.validate_sofaudit_v2_1 import (
    audit_errors,
    receipt_errors as audit_receipt_errors,
)
from experiments.paper14 import validate_sofaction as v2_validator
from schemas.non_intervention import (
    SOFACTION_EXECUTION_BOUNDARY,
    artifact_reference,
    closure_digest,
    downstream_role_errors,
    exact_check_set_errors,
    resolve_reference,
    write_json,
)


ACTION_SCHEMA = ROOT / "schemas" / "sofaction" / "v2.1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "sofaction" / "validation-receipt-v2.1.schema.json"
MIGRATOR = HERE / "migrate_sofaction_v2_to_v2_1.py"
DEFAULT_DIR = HERE / "results" / "v2.1" / "actions"
DEFAULT_RECEIPT_DIR = HERE / "results" / "v2.1" / "receipts"

COMMON_CHECKS = {
    "artifact-digest-closure",
    "audit-projection-preservation",
    "candidate-non-execution",
    "candidate-set-regeneration",
    "downstream-artifact-role-isolation",
    "schema-validation",
    "verified-authority-non-authorization",
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


def _replace_audit_references(value: Any, old_audit_id: str, replacement: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        if (
            value.get("audit_id") == old_audit_id
            and "sofaudit_version" in value
            and "validation_receipt" in value
        ):
            return deepcopy(replacement)
        return {
            key: _replace_audit_references(child, old_audit_id, replacement)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            _replace_audit_references(child, old_audit_id, replacement)
            for child in value
        ]
    return value


def _audit_reference_errors(reference: dict[str, Any]) -> tuple[Path | None, Path | None, list[str]]:
    errors: list[str] = []
    audit_path = (ROOT / reference.get("artifact", "")).resolve()
    receipt_path = (ROOT / reference.get("validation_receipt", {}).get("artifact", "")).resolve()
    for label, path, digest in (
        ("source audit", audit_path, reference.get("digest", {}).get("value")),
        (
            "source audit receipt",
            receipt_path,
            reference.get("validation_receipt", {}).get("digest", {}).get("value"),
        ),
    ):
        if not path.is_file():
            errors.append(f"{label} does not exist")
        else:
            actual = artifact_reference(path, ROOT)["digest"]["value"]
            if actual != digest:
                errors.append(f"{label} digest does not match")
    if errors:
        return None, None, errors
    errors.extend(audit_errors(audit_path))
    receipt = load_json(receipt_path)
    errors.extend(audit_receipt_errors(receipt))
    audit = load_json(audit_path)
    if reference.get("audit_id") != audit.get("audit_id"):
        errors.append("source audit ID differs from linked artifact")
    if receipt.get("audit", {}).get("artifact", {}).get("digest") != reference.get("digest"):
        errors.append("source audit receipt binds a different audit digest")
    validation_ref = reference.get("validation_receipt", {})
    if receipt.get("receipt_id") != validation_ref.get("receipt_id"):
        errors.append("source audit receipt ID differs from linked receipt")
    if receipt.get("validator", {}).get("validator_id") != validation_ref.get("validator_id"):
        errors.append("source audit validator ID differs from linked receipt")
    if receipt.get("validator", {}).get("validator_version") != validation_ref.get("validator_version"):
        errors.append("source audit validator version differs from linked receipt")
    return audit_path, receipt_path, errors


def action_errors(action_path: Path) -> list[str]:
    payload = load_json(action_path)
    errors = schema_errors(payload, ACTION_SCHEMA)
    if errors:
        return errors
    if payload["execution_boundary"] != SOFACTION_EXECUTION_BOUNDARY:
        errors.append("SOFAction execution boundary is not fixed")
    if payload["record_basis"]["causal_status"] != "OUT_OF_SCOPE_FOR_SOFACTION":
        errors.append("SOFAction causal status is not fixed out of scope")
    errors.extend(downstream_role_errors(payload, label="SOFAction v2.1"))

    revision = payload["revision_provenance"]
    if revision["kind"] == "native_v2_1_generation":
        _, implementation_errors = resolve_reference(
            revision["generation_implementation"],
            root=ROOT,
            label="native action generation implementation",
        )
        errors.extend(implementation_errors)
        for index, reference in enumerate(revision["generation_inputs"]):
            _, input_errors = resolve_reference(
                reference,
                root=ROOT,
                label=f"native action generation input {index}",
            )
            errors.extend(input_errors)
        _, _, audit_reference_validation_errors = _audit_reference_errors(payload["source_audit"])
        errors.extend(audit_reference_validation_errors)
        errors.extend(
            v2_validator.contract_errors(
                payload, expected_sofaudit_version="2.1"
            )
        )
        for action in payload["candidate_action_set"]["actions"]:
            if action["authorization_state"] not in {"not_requested", "required", "pending", "denied"}:
                errors.append("candidate authorization_state is not a non-authorizing process state")
        return errors
    source_path, source_errors = resolve_reference(
        revision["source_artifact"], root=ROOT, label="revision source action"
    )
    errors.extend(source_errors)
    migrator_path, migrator_errors = resolve_reference(
        revision["migration_implementation"], root=ROOT, label="action migration implementation"
    )
    errors.extend(migrator_errors)
    if migrator_path != MIGRATOR:
        errors.append("revision provenance does not bind the canonical SOFAction v2.1 migrator")
    if source_path is None:
        return errors
    source = load_json(source_path)
    if source.get("sofaction_version") != "2.0":
        errors.append("revision source action is not SOFAction v2.0")
        return errors
    errors.extend(
        f"v2.0 source schema: {error}"
        for error in v2_validator.validation_errors(source, load_json(v2_validator.DEFAULT_SCHEMA))
    )
    errors.extend(f"v2.0 source: {error}" for error in v2_validator.contract_errors(source))

    audit_path, _, audit_reference_validation_errors = _audit_reference_errors(payload["source_audit"])
    errors.extend(audit_reference_validation_errors)
    linked_audit: dict[str, Any] | None = None
    if audit_path is not None:
        audit = load_json(audit_path)
        linked_audit = audit
        old_audit_path = v2_validator._audit_path(source)
        if old_audit_path is None:
            errors.append("v2.0 source audit cannot be resolved from its declared closure")
            return errors
        if audit.get("revision_provenance", {}).get("source_artifact") != artifact_reference(old_audit_path, ROOT):
            errors.append("v2.1 source audit does not migrate the v2.0 audit bound by the source action")
        if payload["audit_projection"]["signature"] != audit["coordinates"]:
            errors.append("v2.1 AuditProjection does not preserve the linked audit coordinates")

    expected = _replace_audit_references(
        source,
        source["source_audit"]["audit_id"],
        payload["source_audit"],
    )
    if linked_audit is not None:
        expected["audit_projection"]["signature"] = linked_audit["coordinates"]
    expected["sofaction_version"] = "2.1"
    expected["revision_provenance"] = revision
    expected["execution_boundary"] = SOFACTION_EXECUTION_BOUNDARY
    expected["record_basis"]["causal_status"] = "OUT_OF_SCOPE_FOR_SOFACTION"
    if payload != expected:
        errors.append("v2.1 action differs from its exact boundary-annotation migration projection")

    for action in payload["candidate_action_set"]["actions"]:
        if action["authorization_state"] not in {"not_requested", "required", "pending", "denied"}:
            errors.append("candidate authorization_state is not a non-authorizing process state")
    return errors


def _normative_basis_paths(payload: dict[str, Any]) -> list[Path]:
    policy = payload.get("policy_profile") or {}
    paths = []
    for basis in policy.get("normative_basis", []):
        uri = basis["source_ref"]["uri"]
        path = ROOT / unquote(uri.removeprefix("artifact://"))
        paths.append(path)
    return paths


def _ordered_artifacts(action_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    source_audit = ROOT / payload["source_audit"]["artifact"]
    source_receipt = ROOT / payload["source_audit"]["validation_receipt"]["artifact"]
    revision = payload["revision_provenance"]
    ordered = [{"role": "action", "artifact": artifact_reference(action_path, ROOT)}]
    if revision["kind"] == "explicit_v2_0_to_v2_1_migration":
        ordered.extend([
            {"role": "revision-source-action-v2.0", "artifact": revision["source_artifact"]},
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
    ordered.extend([
        {"role": "action-contract", "artifact": artifact_reference(ACTION_SCHEMA, ROOT)},
        {"role": "source-audit", "artifact": artifact_reference(source_audit, ROOT)},
        {"role": "source-audit-validation-receipt", "artifact": artifact_reference(source_receipt, ROOT)},
    ])
    for index, basis_path in enumerate(_normative_basis_paths(payload)):
        ordered.append(
            {"role": f"normative-basis-{index}", "artifact": artifact_reference(basis_path, ROOT)}
        )
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


def build_validation_receipt(action_path: Path) -> dict[str, Any]:
    errors = action_errors(action_path)
    if errors:
        raise ValueError(f"{action_path}: " + "; ".join(errors))
    payload = load_json(action_path)
    ordered = _ordered_artifacts(action_path, payload)
    role_map = {item["role"]: item["artifact"] for item in ordered}
    checks = MIGRATION_CHECKS if payload["revision_provenance"]["kind"].startswith("explicit_") else NATIVE_CHECKS
    return {
        "receipt_version": "2.1",
        "artifact_type": "sofaction_validation_receipt",
        "receipt_kind": "SOFACTION_VALIDATION_RECEIPT",
        "receipt_scope": "SOFACTION_PROTOCOL_CONFORMANCE_ONLY",
        "receipt_id": f"receipt.{payload['action_record_id']}.sofaction-v2_1",
        "action": {
            "action_record_id": payload["action_record_id"],
            "sofaction_version": "2.1",
            "artifact": ordered[0]["artifact"],
        },
        "validator": {
            "validator_id": "paper14.sofaction-validator.v2_1",
            "validator_version": "2.1",
            "implementation": role_map["validator-implementation"],
            "action_contract": role_map["action-contract"],
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
        "authorization_semantics": "NONE",
        "execution_semantics": "NONE",
        "outcome_semantics": "NONE",
        "effect_semantics": "NONE",
        "negative_boundaries": [
            "PASS certifies SOFAction candidate-protocol conformance only; it is not selection, authorization, execution, outcome, or effect evidence."
        ],
    }


def receipt_errors(receipt: dict[str, Any]) -> list[str]:
    errors = schema_errors(receipt, RECEIPT_SCHEMA)
    if errors:
        return errors
    expected_checks = MIGRATION_CHECKS if receipt["generation"]["kind"] == "migration" else NATIVE_CHECKS
    errors.extend(exact_check_set_errors(receipt["checks"], expected_checks, label="SOFAction v2.1 receipt"))
    errors.extend(downstream_role_errors(receipt["artifact_closure"], label="SOFAction v2.1 receipt"))
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
    action_path, action_reference_errors = resolve_reference(
        receipt["action"]["artifact"], root=ROOT, label="receipt action"
    )
    errors.extend(action_reference_errors)
    if action_path is None:
        return errors
    errors.extend(action_errors(action_path))
    payload = load_json(action_path)
    if receipt["action"]["artifact"] != ordered[0]["artifact"]:
        errors.append("receipt action reference differs from closure")
    if receipt["generation"] != _receipt_generation(payload):
        errors.append("receipt generation provenance differs from action")
    if receipt["validator"]["implementation"] != artifact_reference(Path(__file__), ROOT):
        errors.append("receipt validator implementation differs from canonical validator")
    if receipt["validator"]["action_contract"] != artifact_reference(ACTION_SCHEMA, ROOT):
        errors.append("receipt action contract differs from canonical v2.1 schema")
    if receipt["validator"]["receipt_contract"] != artifact_reference(RECEIPT_SCHEMA, ROOT):
        errors.append("receipt contract differs from canonical v2.1 receipt schema")
    if ordered != _ordered_artifacts(action_path, payload):
        errors.append("receipt closure differs from action source closure")
    return errors


def receipt_role_errors(receipt: dict[str, Any], expected_kind: str) -> list[str]:
    """Fail closed when a conformance receipt is substituted for another role."""

    actual = receipt.get("receipt_kind")
    if actual != expected_kind:
        return [f"receipt kind {actual!r} cannot satisfy required role {expected_kind!r}"]
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--write-receipts", action="store_true")
    parser.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = args.paths or sorted(DEFAULT_DIR.glob("*.sofaction"))
    if not paths:
        raise SystemExit("No SOFAction v2.1 artifacts found.")
    failures = 0
    for path in paths:
        errors = action_errors(path)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
            continue
        print(f"PASS {path}")
        if args.write_receipts:
            receipt_path = args.receipt_dir / f"{path.stem}.validation-receipt.json"
            receipt = build_validation_receipt(path)
            write_json(receipt_path, receipt)
            validation_errors = receipt_errors(receipt)
            if validation_errors:
                failures += 1
                print(f"FAIL {receipt_path}")
                for error in validation_errors:
                    print(f"  - {error}")
            else:
                print(f"PASS {receipt_path}")
    if failures:
        raise SystemExit(f"{failures} SOFAction v2.1 item(s) failed validation.")


if __name__ == "__main__":
    main()
