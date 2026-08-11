"""Validate the checked-in Paper XIV SOFAction v2 artifact set."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "sofaction" / "v2.0.schema.json"
RESULTS = ROOT / "experiments" / "paper14" / "results"

spec = importlib.util.spec_from_file_location(
    "paper14_checked_artifact_validator",
    ROOT / "experiments" / "paper14" / "validate_sofaction.py",
)
assert spec is not None and spec.loader is not None
validate_sofaction = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validate_sofaction
spec.loader.exec_module(validate_sofaction)


schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
paths = sorted(RESULTS.glob("*.sofaction"))
assert len(paths) == 29, f"expected 29 SOFAction artifacts, found {len(paths)}"
expected_summary = []

for path in paths:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = (
        validate_sofaction.validation_errors(payload, schema)
        + validate_sofaction.contract_errors(payload)
    )
    assert not errors, f"{path}: {'; '.join(errors)}"
    context = payload.get("action_context") or {}
    actions = payload["candidate_action_set"]["actions"]
    interpretations = payload["interpretation_records"]
    expected_summary.append(
        {
            "case": payload["source_audit"]["audit_id"],
            "source_kind": (
                "native"
                if payload["source_audit"]["audit_id"] == "gridworld-f4-native-v2"
                else "migration"
            ),
            "context_role": context.get("comparison_role", "inconclusive"),
            "context_admission": payload["context_admission"]["status"],
            "policy_admission": payload["policy_admission"]["status"],
            "interpretations": sorted(
                {item["assessment_kind"] for item in interpretations}
            ),
            "candidate_count": len(actions),
            "dispositions": sorted({item["disposition"] for item in actions}),
        }
    )

summary = json.loads((RESULTS / "action_summary.json").read_text(encoding="utf-8"))
assert sorted(summary["records"], key=lambda row: row["case"]) == sorted(
    expected_summary, key=lambda row: row["case"]
)

receipt_paths = sorted((RESULTS / "receipts").glob("*.validation-receipt.json"))
assert len(receipt_paths) == len(paths)
for receipt_path in receipt_paths:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    errors = validate_sofaction.validation_receipt_errors(receipt)
    assert not errors, f"{receipt_path}: {'; '.join(errors)}"

print("test_sofaction_v2.py: OK")
