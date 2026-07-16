"""Validate Paper XII artifacts against the frozen SOFRS v1.0 envelope."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE.parents[1] / "schemas" / "sofrs" / "v1.0.schema.json"
DEFAULT_PAPER = HERE.parents[1] / "papers" / "paper12" / "Paper XII.md"
APPENDIX_HEADING = "## Appendix A: SOF Report Specification v1.0"
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


def extract_appendix_schema(path: Path) -> dict:
    markdown = path.read_text(encoding="utf-8")
    if APPENDIX_HEADING not in markdown:
        raise ValueError(f"missing heading: {APPENDIX_HEADING}")
    appendix = markdown.split(APPENDIX_HEADING, maxsplit=1)[1]
    match = re.search(r"```json\s*(\{.*?\})\s*```", appendix, flags=re.DOTALL)
    if match is None:
        raise ValueError("Appendix A does not contain a fenced JSON schema")
    return json.loads(match.group(1))


def schema_drift_errors(paper_path: Path, schema: dict) -> list[str]:
    try:
        embedded = extract_appendix_schema(paper_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [str(error)]
    if embedded == schema:
        return []

    embedded_text = json.dumps(embedded, indent=2, sort_keys=True).splitlines()
    canonical_text = json.dumps(schema, indent=2, sort_keys=True).splitlines()
    diff = list(
        difflib.unified_diff(
            embedded_text,
            canonical_text,
            fromfile="Paper XII Appendix A",
            tofile="schemas/sofrs/v1.0.schema.json",
            lineterm="",
        )
    )
    return ["Appendix A schema differs from the canonical SOFRS v1.0 schema", *diff]


def validate(path: Path, schema: dict) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    messages = [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]
    reserved = sorted(DOWNSTREAM_TOP_LEVEL_FIELDS.intersection(payload))
    if reserved:
        messages.append(
            "downstream Paper XIII/XIV fields are not valid at SOFRS top level: "
            + ", ".join(reserved)
        )
    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Reports to validate.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    drift_errors = schema_drift_errors(args.paper, schema)
    if drift_errors:
        print(f"FAIL {args.paper}")
        for error in drift_errors:
            print(f"  {error}")
        raise SystemExit("Paper XII Appendix A schema drift detected.")
    print(f"PASS {args.paper} Appendix A matches {args.schema}")

    paths = args.paths or sorted((HERE / "results").glob("*.sofreport"))
    if not paths:
        raise SystemExit("No .sofreport artifacts found.")

    failures = 0
    for path in paths:
        errors = validate(path, schema)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS envelope {path}")

    if failures:
        raise SystemExit(f"{failures} report(s) failed validation.")
    print(f"Envelope-validated {len(paths)} SOF Diagnostic Report(s).")


if __name__ == "__main__":
    main()
