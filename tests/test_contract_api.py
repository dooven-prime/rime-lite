"""Regression tests for shared cross-paper contract mechanics."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas.contract_api import (
    artifact_reference_errors,
    file_digest,
    resolve_artifact_path,
    result_claim_status_error,
    schema_errors,
)
from schemas.sofcompiler.api import compile_output_v1


def test_result_claim_status_matrix() -> None:
    assert result_claim_status_error(
        "CERTIFIED",
        "Computational Certificate",
        label="finding",
    ) is None
    error = result_claim_status_error(
        "ESTABLISHED",
        "Computational Observation",
        label="finding",
    )
    assert error is not None and "illegal result/claim status pair" in error


def test_repository_bounded_artifact_resolution() -> None:
    schema_path = ROOT / "schemas" / "sofrs" / "v2.0.schema.json"
    reference = {
        "uri": "schemas/sofrs/v2.0.schema.json",
        "digest": {
            "algorithm": "sha256",
            "value": file_digest(schema_path),
        },
    }
    assert artifact_reference_errors(
        reference,
        label="schema",
        repository_root=ROOT,
    ) == []
    try:
        resolve_artifact_path(
            "../../outside.json",
            repository_root=ROOT,
        )
    except ValueError as error:
        assert "escapes repository root" in str(error)
    else:
        raise AssertionError("repository-escaping artifact URI was accepted")


def test_compiler_output_fixture_has_a_public_schema() -> None:
    schema_path = (
        ROOT / "schemas" / "sofcompiler" / "compiler-output-v1.0.schema.json"
    )
    fixture_path = (
        ROOT
        / "schemas"
        / "sofcompiler"
        / "examples"
        / "strict-associative-compiler-output-v1.0.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema_errors(fixture, schema) == []

    compiler_root = ROOT / "schemas" / "sofcompiler"
    examples = compiler_root / "examples"
    generated = compile_output_v1(
        json.loads(
            (examples / "strict-associative-capabilities-v1.0.json").read_text(
                encoding="utf-8"
            )
        ),
        json.loads(
            (examples / "strict-associative-ir-v1.0.json").read_text(
                encoding="utf-8"
            )
        ),
        json.loads(
            (examples / "basic-associative-closure-profile-v1.0.json").read_text(
                encoding="utf-8"
            )
        ),
        json.loads(
            (compiler_root / "rule-registry-v1.0.json").read_text(encoding="utf-8")
        ),
    )
    assert generated == fixture


if __name__ == "__main__":
    for name in sorted(key for key in globals() if key.startswith("test_")):
        globals()[name]()
    print("test_contract_api.py: OK")
