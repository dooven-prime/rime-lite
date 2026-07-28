"""Validate versioned SOF Registry snapshots and their local evidence links."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_SCHEMA = ROOT / "schemas" / "registry" / "v1.0.schema.json"
DEFAULT_SNAPSHOTS = [HERE / "paper10-release-v1.0.registry.json"]

# The release snapshot is immutable; resolve repository-only path migrations
# when checking whether its historical evidence still exists in the active tree.
RELOCATED_EVIDENCE_PATHS = {
    "experiments/paper5/path_commutator_cancellation.py": (
        "experiments/paper5/validation/path_commutator_cancellation.py"
    ),
    "experiments/paper7/incidence_variety_codim.py": (
        "experiments/paper7/validation/incidence_variety_codim.py"
    ),
    "experiments/paper7/markov_graph_sof.py": (
        "experiments/paper7/archive/markov_graph_sof.py"
    ),
}


def repository_path(value: str) -> Path:
    return ROOT / RELOCATED_EVIDENCE_PATHS.get(value, value)


def schema_errors(payload: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def contract_errors(payload: dict) -> list[str]:
    errors: list[str] = []
    entries = payload.get("entries", [])
    snapshot = payload.get("snapshot", {})

    declared_count = snapshot.get("entry_count")
    if declared_count != len(entries):
        errors.append(
            f"snapshot.entry_count is {declared_count}, but {len(entries)} entries exist"
        )

    ids = [entry.get("id") for entry in entries]
    duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
    if duplicates:
        errors.append(f"duplicate entry IDs: {', '.join(duplicates)}")

    source = snapshot.get("source")
    if source and not (ROOT / source).is_file():
        errors.append(f"snapshot source does not exist: {source}")

    for entry in entries:
        entry_id = entry.get("id", "<unknown>")
        metadata = entry.get("metadata", {})
        for field in ("evidence_scripts", "reports"):
            for value in metadata.get(field, []):
                if not repository_path(value).is_file():
                    errors.append(f"{entry_id}: missing {field} path: {value}")

    if snapshot.get("id") == "paper10-release-v1.0":
        for entry in entries:
            entry_id = entry.get("id", "<unknown>")
            metadata = entry.get("metadata", {})
            later_paths = [
                path
                for path in metadata.get("evidence_scripts", [])
                if "experiments/paper11/" in path or "experiments/paper12/" in path
            ]
            if later_paths:
                errors.append(
                    f"{entry_id}: post-Paper-X evidence leaked into release snapshot: "
                    + ", ".join(later_paths)
                )
            if metadata.get("reports"):
                errors.append(
                    f"{entry_id}: Paper X release snapshot must not backfill later SOFRS reports"
                )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Registry snapshots.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    paths = args.paths or DEFAULT_SNAPSHOTS
    failures = 0

    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = schema_errors(payload, schema) + contract_errors(payload)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(
                f"PASS {path} "
                f"({payload['snapshot']['entry_count']} entries, "
                f"schema v{payload['registry_schema_version']})"
            )

    if failures:
        raise SystemExit(f"{failures} Registry snapshot(s) failed validation.")
    print(f"Validated {len(paths)} SOF Registry snapshot(s).")


if __name__ == "__main__":
    main()
