"""Validate Paper XII protocol admission beyond the frozen SOFRS envelope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
ROOT = PAPER_DIR.parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "sofrs" / "v1.0.schema.json"
DEFAULT_PROFILE = ROOT / "schemas" / "sofrs" / "paper12-protocol-profile-v1.0.json"
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


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def envelope_errors(payload: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    ]
    reserved = sorted(DOWNSTREAM_TOP_LEVEL_FIELDS.intersection(payload))
    if reserved:
        errors.append(
            "downstream Paper XIII/XIV fields are not valid at SOFRS top level: "
            + ", ".join(reserved)
        )
    return errors


def is_level_iii(payload: dict, profile: dict) -> bool:
    triggers = profile["level_iii_triggers"]
    if payload.get("diagnostic_regime") in triggers.get("diagnostic_regime", []):
        return True
    return (
        "strict_sof_realization" in payload
        and payload["strict_sof_realization"] is False
        and triggers.get("strict_sof_realization") is False
    )


def admission_errors(payload: dict, profile: dict) -> list[str]:
    errors: list[str] = []

    for field in profile["required_metadata"]:
        if not _nonempty_string(payload.get(field)):
            errors.append(f"{field}: non-empty string required by the Paper XII profile")

    for field in profile["required_nonempty_fields"]:
        if not _nonempty(payload.get(field)):
            errors.append(f"{field}: non-empty value required by the Paper XII profile")

    wall_record = payload.get("wall_record")
    if not isinstance(wall_record, dict) or not wall_record:
        errors.append("wall_record: an object must state the wall result or why no path exists")

    shadow_fields = ("support_matrix", "bridge_matrix", "repair_matrix")
    if all(payload.get(field) is None for field in shadow_fields):
        policy = profile["all_null_shadow_policy"]
        if payload.get("claim_status") not in policy["allowed_claim_status"]:
            errors.append("all support/bridge/repair fields are null without a boundary/failure claim")
        boundary = payload.get(policy["required_metadata_field"])
        if not isinstance(boundary, dict):
            errors.append(
                f"{policy['required_metadata_field']}: required when all shadow fields are null"
            )
        else:
            for field in policy["required_metadata_keys"]:
                if not _nonempty(boundary.get(field)):
                    errors.append(
                        f"{policy['required_metadata_field']}.{field}: required when all shadows are null"
                    )

    if is_level_iii(payload, profile):
        provenance = payload.get("provenance")
        if not isinstance(provenance, dict):
            errors.append("provenance: required for a Level III behavioral report")
        else:
            for field in profile["level_iii_required_provenance"]:
                if not _nonempty(provenance.get(field)):
                    errors.append(f"provenance.{field}: required for a Level III behavioral report")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    paths = args.paths or [
        *sorted((PAPER_DIR / "archive" / "results").glob("*.sofreport")),
        *sorted((PAPER_DIR / "archive" / "results").glob("*.fixture.json")),
    ]
    if not paths:
        raise SystemExit("No Paper XII artifacts found.")

    failures = 0
    excluded_roles = set(profile["excluded_artifact_roles"])
    admitted = 0
    fixtures = 0
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = envelope_errors(payload, schema)
        if errors:
            failures += 1
            print(f"FAIL envelope {path}")
            for error in errors:
                print(f"  - {error}")
            continue

        if payload.get("artifact_role") in excluded_roles:
            fixtures += 1
            print(f"FIXTURE {path} (envelope-valid; excluded from protocol admission)")
            continue

        errors = admission_errors(payload, profile)
        if errors:
            failures += 1
            print(f"FAIL admission {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            admitted += 1
            print(f"PASS admission {path}")

    if failures:
        raise SystemExit(f"{failures} artifact(s) failed Paper XII protocol admission.")
    print(f"Admitted {admitted} report(s); identified {fixtures} validator fixture(s).")


if __name__ == "__main__":
    main()
