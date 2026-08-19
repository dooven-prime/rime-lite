"""Generate shared digest and artifact/receipt-reference definitions in v2 schemas.

The public schemas are intentionally self-contained because several consumers
instantiate Draft202012Validator from an already-loaded JSON object. This tool
keeps those local definitions synchronized with schemas/common without
requiring consumers to implement a filesystem schema registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


COMMON = Path(__file__).resolve().parent
ROOT = COMMON.parents[1]
TARGETS = {
    ROOT / "schemas" / "sofrs" / "v2.0.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.0.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofrs" / "v2.1.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofrs" / "report-validation-receipt-v2.1.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofaudit" / "v2.0.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofaudit" / "validation-receipt-v2.0.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
    ROOT / "schemas" / "sofaction" / "v2.0.schema.json": {
        "digest": "digest",
        "validationReceiptRef": "validation_receipt_reference",
    },
    ROOT / "schemas" / "sofaction" / "validation-receipt-v2.0.schema.json": {
        "digest": "digest",
        "artifact_reference": "artifact_reference",
    },
}


def _fragment(name: str) -> dict[str, Any]:
    source = json.loads((COMMON / f"{name.replace('_', '-')}-v1.schema.json").read_text(encoding="utf-8"))
    fragment = {
        key: value
        for key, value in source.items()
        if key not in {"$schema", "$id", "title"}
    }

    def rewrite_refs(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: ("#/$defs/digest" if value == {"$ref": "digest-v1.schema.json"} else rewrite_refs(item))
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [rewrite_refs(item) for item in value]
        return value

    return rewrite_refs(fragment)


def _matching_brace(text: str, opening: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unterminated JSON object")


def _replace_definition(text: str, name: str, value: dict[str, Any]) -> str:
    defs_start = text.index('"$defs"')
    marker = f'    "{name}": {{'
    start = text.index(marker, defs_start)
    opening = start + marker.index("{")
    closing = _matching_brace(text, opening)
    rendered = json.dumps(value, indent=2, ensure_ascii=False)
    lines = rendered.splitlines()
    replacement = f'    "{name}": {lines[0]}'
    if len(lines) > 1:
        replacement += "\n" + "\n".join(f"    {line}" for line in lines[1:])
    return text[:start] + replacement + text[closing + 1 :]


def render(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for local_name, common_name in TARGETS[path].items():
        text = _replace_definition(text, local_name, _fragment(common_name))
    json.loads(text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if a schema is out of sync")
    args = parser.parse_args()
    drift = []
    for path in TARGETS:
        rendered = render(path)
        current = path.read_text(encoding="utf-8")
        if rendered != current:
            drift.append(path)
            if not args.check:
                path.write_text(rendered, encoding="utf-8")
    if drift and args.check:
        for path in drift:
            print(f"DRIFT: {path.relative_to(ROOT)}")
        return 1
    print(f"PASS: shared contract fragments {'checked' if args.check else 'generated'} for {len(TARGETS)} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
