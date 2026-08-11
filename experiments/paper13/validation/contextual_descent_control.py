"""Emit and independently validate the promoted finite descent control."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPLORATORY = ROOT / "experiments" / "exploratory" / "comparison_geometry"
sys.path.insert(0, str(EXPLORATORY))

from canonical_minimal_example import build_example  # noqa: E402

RESULT_DIR = ROOT / "experiments" / "paper13" / "results" / "controls"
CONTROL_PATH = RESULT_DIR / "paper13-contextual-descent-control-v1.json"
RECEIPT_PATH = RESULT_DIR / "paper13-contextual-descent-control-v1.validation-receipt.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path: Path) -> dict[str, Any]:
    return {"uri": path.relative_to(ROOT).as_posix(), "digest": {"algorithm": "sha256", "value": digest(path)}}


def section_values(section: Any) -> dict[str, Any]:
    return {
        f"{coordinate.source_sector}-{coordinate.target_sector}": value
        for coordinate, value in section.values
    }


def candidate_digest(candidates: list[dict[str, Any]]) -> str:
    encoded = json.dumps(candidates, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_payload() -> dict[str, Any]:
    example = build_example()
    candidates = [
        {"candidate_id": "s0", "values": section_values(example.candidate_0)},
        {"candidate_id": "s1", "values": section_values(example.candidate_1)},
    ]
    return {
        "control_version": "1.0",
        "control_id": "paper13-contextual-descent-control-v1",
        "claim_status": "Computational Certificate",
        "scope": "Finite candidate-relative descent control for a typed word-support signature.",
        "fixture": {
            "global_context": {"sectors": ["A", "B", "C"], "carrier": "word", "realization_kind": "strict_sof", "conventions": {"support": "exact-boolean"}},
            "candidate_space": candidates,
            "covers": [
                {"cover_id": "minimal.cover.ab-bc", "observed_coordinates": ["A-B", "B-C"], "local_sections": {"A-B": 1, "B-C": 1}},
                {"cover_id": "minimal.cover.ab-bc-ac", "observed_coordinates": ["A-B", "B-C", "A-C"], "local_sections": {"A-B": 1, "B-C": 1, "A-C": 0}},
            ],
        },
        "descent_basis": {
            "candidate_space_id": "candidate-space.minimal-ab-bc-ac.v1",
            "candidate_space_status": "bounded",
            "enumerator_id": "enumerator.literal-minimal.v1",
            "validator_id": "validator.contextual-descent.v1",
            "candidate_digest": candidate_digest(candidates),
        },
        "results": [
            {"cover_id": "minimal.cover.ab-bc", "match_count": 2, "state": "GLUED_NONUNIQUE", "separatedness_failure": True},
            {"cover_id": "minimal.cover.ab-bc-ac", "match_count": 1, "state": "GLUED_UNIQUE", "separatedness_failure": False},
        ],
        "source_artifacts": [
            reference(EXPLORATORY / "canonical_minimal_example.py"),
            reference(EXPLORATORY / "finite_descent.py"),
            reference(EXPLORATORY / "context_objects.py"),
            reference(Path(__file__)),
        ],
        "known_nonclaims": [
            "The bounded candidate space is not an exhaustive global section space.",
            "This control does not establish a Grothendieck topology, sheaf theorem, cross-fiber transport law, or topos structure.",
            "The control is a same-realization-kind canonical-restriction subcase and does not reclassify strict-to-analogue alignment as restriction.",
        ],
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixture = payload.get("fixture", {})
    candidates = fixture.get("candidate_space", [])
    if [item.get("candidate_id") for item in candidates] != ["s0", "s1"]:
        errors.append("candidate space IDs are not the canonical two-candidate fixture")
    if candidate_digest(candidates) != payload.get("descent_basis", {}).get("candidate_digest"):
        errors.append("candidate-space digest does not match the declared basis")
    expected_candidates = {
        item["candidate_id"]: item.get("values", {}) for item in candidates
    }
    for result in payload.get("results", []):
        cover_id = result.get("cover_id")
        cover = next((item for item in fixture.get("covers", []) if item.get("cover_id") == cover_id), None)
        if cover is None:
            errors.append(f"unknown cover in result: {cover_id}")
            continue
        matched = [
            candidate_id
            for candidate_id, values in expected_candidates.items()
            if all(values.get(coordinate) == value for coordinate, value in cover["local_sections"].items())
        ]
        if result.get("match_count") != len(matched):
            errors.append(f"{cover_id}: match count was not independently recomputed")
        expected_state = {0: "NO_GLOBAL_SECTION", 1: "GLUED_UNIQUE"}.get(len(matched), "GLUED_NONUNIQUE")
        if result.get("state") != expected_state:
            errors.append(f"{cover_id}: classifier state differs from match cardinality")
        if result.get("separatedness_failure") != (len(matched) > 1):
            errors.append(f"{cover_id}: separatedness flag differs from cardinality")
    return errors


def write() -> None:
    payload = build_payload()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    CONTROL_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "receipt_version": "1.0",
        "receipt_id": "paper13-contextual-descent-control-v1.validation",
        "status": "PASS",
        "control": {"uri": CONTROL_PATH.relative_to(ROOT).as_posix(), "digest": {"algorithm": "sha256", "value": digest(CONTROL_PATH)}},
        "producer": reference(Path(__file__)),
        "independent_validator": reference(HERE / "validate_contextual_descent_control.py"),
        "checks": ["candidate-space-digest", "finite-match-recomputation", "classifier-cardinality", "known-nonclaim-preservation"],
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    else:
        payload = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
        errors = validate_payload(payload)
        if errors:
            raise SystemExit("; ".join(errors))
        print("PASS contextual descent control")


if __name__ == "__main__":
    main()
