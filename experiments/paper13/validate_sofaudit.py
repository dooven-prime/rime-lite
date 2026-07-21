"""Validate Paper XIII SOF comparison artifacts and linked SOFRS reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "sofaudit" / "v1.0.schema.json"


def validation_errors(payload: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def link_errors(payload: dict, base: Path) -> list[str]:
    errors: list[str] = []
    for field in ("reference", "target"):
        artifact = payload.get(field, {}).get("artifact")
        if artifact and not (base / artifact).is_file():
            errors.append(f"{field}.artifact does not exist: {artifact}")
    return errors


def semantic_contract_errors(payload: dict) -> list[str]:
    """Enforce cross-field semantics not expressed as global v1.0 requirements."""

    errors: list[str] = []
    role = payload.get("comparison_role")
    failure_mode = payload.get("failure_mode")
    has_contract = isinstance(payload.get("transformation_contract"), dict)
    has_evaluation = isinstance(payload.get("contract_evaluation"), dict)
    is_legitimate = (
        role == "legitimate_transformation_control"
        or failure_mode == "legitimate_transformation_control"
    )

    if is_legitimate:
        if role != "legitimate_transformation_control":
            errors.append(
                "legitimate transformations require comparison_role="
                "legitimate_transformation_control"
            )
        if not has_contract:
            errors.append(
                "legitimate transformations require transformation_contract"
            )
        if not has_evaluation:
            errors.append(
                "legitimate transformations require contract_evaluation"
            )
    elif has_contract or has_evaluation:
        errors.append(
            "transformation contract fields require comparison_role="
            "legitimate_transformation_control"
        )

    if has_evaluation and not has_contract:
        errors.append("contract_evaluation requires transformation_contract")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    print(f"PASS canonical schema: {args.schema}")
    paths = args.paths or sorted((HERE / "results").glob("*.sofaudit"))
    if not paths:
        raise SystemExit("No .sofaudit artifacts found.")

    failures = 0
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = (
            validation_errors(payload, schema)
            + link_errors(payload, path.parent)
            + semantic_contract_errors(payload)
        )
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    if failures:
        raise SystemExit(f"{failures} SOF comparison artifact(s) failed validation.")
    print(f"Validated {len(paths)} SOF comparison artifact(s).")


if __name__ == "__main__":
    main()
