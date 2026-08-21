"""Explicitly migrate SOFAction v2.0 candidate artifacts to v2.1."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


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
    file_digest,
    write_json,
)


DEFAULT_SOURCE_DIR = HERE / "results"
DEFAULT_OUTPUT_DIR = HERE / "results" / "v2.1" / "actions"
DEFAULT_AUDIT_DIR = ROOT / "experiments" / "paper13" / "results" / "v2.1" / "audits"
DEFAULT_AUDIT_RECEIPT_DIR = ROOT / "experiments" / "paper13" / "results" / "v2.1" / "receipts"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _audit_reference(audit_path: Path, receipt_path: Path) -> dict[str, Any]:
    audit = load_json(audit_path)
    receipt = load_json(receipt_path)
    errors = audit_errors(audit_path)
    errors.extend(audit_receipt_errors(receipt))
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "audit_id": audit["audit_id"],
        "artifact": audit_path.relative_to(ROOT).as_posix(),
        "sofaudit_version": "2.1",
        "digest": {"algorithm": "sha256", "value": file_digest(audit_path)},
        "validation_receipt": {
            "receipt_id": receipt["receipt_id"],
            "artifact": receipt_path.relative_to(ROOT).as_posix(),
            "digest": {"algorithm": "sha256", "value": file_digest(receipt_path)},
            "validator_id": receipt["validator"]["validator_id"],
            "validator_version": receipt["validator"]["validator_version"],
        },
    }


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


def migrate_action(
    source_path: Path,
    target_path: Path,
    *,
    audit_dir: Path,
    audit_receipt_dir: Path,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    source = load_json(source_path)
    if source.get("sofaction_version") != "2.0":
        raise ValueError(f"{source_path} is not SOFAction v2.0")
    source_errors = v2_validator.validation_errors(source, load_json(v2_validator.DEFAULT_SCHEMA))
    source_errors.extend(v2_validator.contract_errors(source))
    if source_errors:
        raise ValueError(f"{source_path}: " + "; ".join(source_errors))

    source_audit_path = v2_validator._audit_path(source)
    if source_audit_path is None:
        raise ValueError(f"{source_path}: frozen v2.0 source audit cannot be resolved")
    audit_path = audit_dir / source_audit_path.name
    receipt_path = audit_receipt_dir / source_audit_path.name.replace(
        ".sofaudit.json", ".validation-receipt.json"
    )
    replacement = _audit_reference(audit_path, receipt_path)

    target = _replace_audit_references(source, source["source_audit"]["audit_id"], replacement)
    target["audit_projection"]["signature"] = load_json(audit_path)["coordinates"]
    target["sofaction_version"] = "2.1"
    target["revision_provenance"] = {
        "kind": "explicit_v2_0_to_v2_1_migration",
        "source_version": "2.0",
        "source_artifact": artifact_reference(source_path, ROOT),
        "migration_implementation": artifact_reference(Path(__file__), ROOT),
    }
    target["execution_boundary"] = SOFACTION_EXECUTION_BOUNDARY
    target["record_basis"]["causal_status"] = "OUT_OF_SCOPE_FOR_SOFACTION"
    write_json(target_path, target)
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--audit-receipt-dir", type=Path, default=DEFAULT_AUDIT_RECEIPT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = args.sources or sorted(DEFAULT_SOURCE_DIR.glob("*.sofaction"))
    if not sources:
        raise SystemExit("No SOFAction v2.0 artifacts found.")
    for source_path in sources:
        target_path = args.output_dir / source_path.name
        migrate_action(
            source_path,
            target_path,
            audit_dir=args.audit_dir,
            audit_receipt_dir=args.audit_receipt_dir,
        )
        print(f"MIGRATED {source_path} -> {target_path}")


if __name__ == "__main__":
    main()
