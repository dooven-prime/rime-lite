"""Independent validator for the promoted finite contextual-descent control."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTROL_PATH = ROOT / "experiments" / "paper13" / "results" / "controls" / "paper13-contextual-descent-control-v1.json"


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    fixture = payload["fixture"]
    candidates = fixture["candidate_space"]
    serialized = json.dumps(candidates, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_digest = hashlib.sha256(serialized).hexdigest()
    if payload["descent_basis"]["candidate_digest"] != expected_digest:
        errors.append("candidate digest mismatch")
    by_id = {item["candidate_id"]: item["values"] for item in candidates}
    expected = {
        "minimal.cover.ab-bc": (2, "GLUED_NONUNIQUE"),
        "minimal.cover.ab-bc-ac": (1, "GLUED_UNIQUE"),
    }
    for result in payload["results"]:
        cover_id = result["cover_id"]
        observed = next(item for item in fixture["covers"] if item["cover_id"] == cover_id)
        count = sum(
            all(values.get(label) == value for label, value in observed["local_sections"].items())
            for values in by_id.values()
        )
        if (count, result["state"]) != expected[cover_id]:
            errors.append(f"{cover_id}: independent cardinality/classifier mismatch")
        if result["separatedness_failure"] != (count > 1):
            errors.append(f"{cover_id}: separatedness mismatch")
    return errors


def main() -> None:
    payload = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        raise SystemExit("; ".join(errors))
    print("PASS independent contextual descent validation")


if __name__ == "__main__":
    main()
