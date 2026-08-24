#!/usr/bin/env python3
"""Fail-closed validator for the Paper XXI arbitrary-depth replay artifact."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / "experiments" / "paper21"
RESULTS_DIR = EVIDENCE_DIR / "results"
DEFAULT_ARTIFACT = RESULTS_DIR / "arbitrary_depth_semantic_v1.json"
DEFAULT_RECEIPT = RESULTS_DIR / "arbitrary_depth_semantic_v1.validation-receipt.json"
MANUSCRIPT = ROOT / "papers" / "paper21" / "Paper XXI.md"
if str(EVIDENCE_DIR) not in sys.path:
    sys.path.insert(0, str(EVIDENCE_DIR))

from arbitrary_depth_semantic import (  # noqa: E402
    ARTIFACT_ID,
    SCHEMA,
    build_payload,
    canonical_json,
    content_digest,
)


RECEIPT_SCHEMA = "paper.route-profiles.arbitrary-depth-validation-receipt.v1"
VALIDATOR_ID = "paper.route-profiles.arbitrary-depth-validator.python.v1"


class ValidationError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def validate(payload: dict) -> list[str]:
    supplied = payload.get("content_sha256")
    if not isinstance(supplied, str) or content_digest(payload) != supplied:
        raise ValidationError("arbitrary-depth artifact digest mismatch")
    if payload.get("schema") != SCHEMA or payload.get("artifact_id") != ARTIFACT_ID:
        raise ValidationError("unexpected arbitrary-depth artifact identity")
    if payload.get("artifact_role") != "PAPER_OWNED_ARBITRARY_DEPTH_SEMANTIC_REPLAY":
        raise ValidationError("unexpected arbitrary-depth artifact role")

    theorem_contract = payload.get("theorem_contract", {})
    expected_theorems = {
        "prefix_pole_classification",
        "fixed_field_automaton",
        "rational_generating_functions",
        "fixed_depth_stabilization",
        "generic_profile",
    }
    if set(theorem_contract) != expected_theorems:
        raise ValidationError("arbitrary-depth theorem contract is incomplete")

    expected_exceptional = {
        1: [],
        2: [],
        3: [2],
        4: [2],
        5: [2, 3],
        6: [2, 3],
        7: [2, 3, 5],
        8: [2, 3, 5],
        9: [2, 3, 5, 7],
        10: [2, 3, 5, 7],
    }
    observed_exceptional = {
        row["depth"]: row["exceptional_characteristics"]
        for row in payload.get("exceptional_characteristics", [])
    }
    if observed_exceptional != expected_exceptional:
        raise ValidationError("exceptional-characteristic table changed")
    expected_spectra = {
        1: [1],
        2: [1],
        3: [1, 2],
        4: [1, 2],
        5: [1, 2, 3],
        6: [1, 2, 3],
        7: [1, 2, 3, 4, 5],
        8: [1, 2, 3, 4, 5],
        9: [1, 2, 3, 4, 5, 7, 8],
        10: [1, 2, 3, 4, 5, 7, 8],
    }
    observed_spectra = {
        row["depth"]: row["prefix_determinant_spectrum"]
        for row in payload.get("exceptional_characteristics", [])
    }
    if observed_spectra != expected_spectra:
        raise ValidationError("prefix determinant spectrum changed")
    expected_generic_zero_counts = [0, 14, 115, 732, 4094, 21635, 110486, 553550, 2740395, 13468388]
    observed_generic_zero_counts = [
        row["generic_zero_route_count"]
        for row in payload.get("exceptional_characteristics", [])
    ]
    if observed_generic_zero_counts != expected_generic_zero_counts:
        raise ValidationError("generic zero-route counts changed")

    expected_states = {2: 6, 3: 9, 5: 21, 7: 60, 11: 606, 13: 1918, 17: 24518, 19: 85185}
    observed_states = {
        row["prime"]: row["reachable_state_count"]
        for row in payload.get("fixed_field_automata", [])
    }
    if observed_states != expected_states:
        raise ValidationError("reachable automaton state counts changed")
    if any(check.get("status") != "PASS" for check in payload["semantic_replay"]["checks"]):
        raise ValidationError("prefix-pole semantic replay failed")
    signature_bridge = payload.get("fixed_depth_signature_bridge", {})
    if signature_bridge.get("primes") != [2, 3, 5, 7, 11, 13]:
        raise ValidationError("fixed-depth signature bridge prime scope changed")
    if signature_bridge.get("max_depth") != 5:
        raise ValidationError("fixed-depth signature bridge depth changed")
    if any(
        len(record.get("profiles", [])) != 5
        for record in signature_bridge.get("profiles", [])
    ):
        raise ValidationError("fixed-depth signature bridge is incomplete")
    if any(
        not item.get("checked")
        for item in payload.get("generating_function_examples", {}).values()
        if isinstance(item, dict)
    ):
        raise ValidationError("generating-function replay failed")
    if payload["generating_function_examples"].get("coefficient_check_max_depth") != 10:
        raise ValidationError("generating-function replay depth changed")
    if any(
        row["status"] != "PASS_COUNT_SHADOW"
        for row in payload.get("stabilization_count_shadow", [])
    ):
        raise ValidationError("stabilization count shadow is incomplete")
    if any(
        row["generic_zero_count"] != row["common_zero_count"]
        for row in payload.get("stabilization_count_shadow", [])
    ):
        raise ValidationError("generic profile does not match eligible finite fields")

    excluded = payload.get("claim_boundary", {}).get("does_not_certify", [])
    for boundary in (
        "a field-independent finite automaton or uniform state bound",
        "an all-depth closed scalar formula for zero routes",
        "a closed form or recurrence for the prefix determinant spectra",
        "depth-asymptotic convergence or a growth constant",
    ):
        if boundary not in excluded:
            raise ValidationError(f"missing claim boundary: {boundary}")

    manuscript = " ".join(MANUSCRIPT.read_text(encoding="utf-8").split())
    for anchor in (
        "Theorem 5.1: Arbitrary-Depth Prefix-Pole Classification",
        "Corollary 5.2: Fixed-Field Survivor Automaton",
        "Corollary 5.3: Transfer Counts and Rational Generating Functions",
        "Theorem 5.5: Fixed-Depth Large-Field Stabilization",
        "The Lean receipt binds only the formalized surface listed in Section 8",
        "It does not cover the arbitrary-depth prefix-pole theorem, fixed-field automata and rationality, the generic profile, or fixed-depth stabilization and determinant-spectrum monotonicity",
    ):
        if anchor not in manuscript:
            raise ValidationError(f"manuscript theorem anchor is missing: {anchor}")

    rebuilt = build_payload()
    if canonical_json(rebuilt) != canonical_json(payload):
        raise ValidationError("arbitrary-depth artifact replay mismatch")

    tampered = deepcopy(payload)
    tampered["exceptional_characteristics"][6]["exceptional_characteristics"] = [2, 3]
    tampered["exceptional_characteristics"][6]["exceptional_characteristics"].append(7)
    tampered["content_sha256"] = content_digest(tampered)
    if canonical_json(tampered) == canonical_json(rebuilt):
        raise ValidationError("coordinated tamper control failed")

    return [
        "artifact identity and digest",
        "arbitrary-depth theorem contract",
        "prefix-pole semantic replay",
        "legacy fixed-depth zero-route signature bridge",
        "reachable-subset automaton closure",
        "transfer counts and rational-series examples",
        "finite exceptional-characteristic table",
        "prefix determinant spectrum and generic profile",
        "large-field stabilization count shadow",
        "manuscript theorem anchors",
        "nonclaim boundary",
        "full producer replay",
        "coordinated tamper rejection",
    ]


def build_receipt(path: Path, payload: dict, checks: list[str]) -> dict:
    validator = Path(__file__).resolve()
    producer = EVIDENCE_DIR / "arbitrary_depth_semantic.py"
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "ROUTE-PROFILES-ARBITRARY-DEPTH-V1-REPLAY",
        "receipt_kind": "ARBITRARY_DEPTH_SEMANTIC_VALIDATION_RECEIPT",
        "receipt_scope": "PAPER_OWNED_EXACT_REPLAY_NOT_INDEPENDENT_PROOF",
        "status": "PASS",
        "artifact": {
            "path": repo_path(path),
            "artifact_sha256": sha256(path),
            "content_sha256": payload["content_sha256"],
        },
        "source_closure": {
            repo_path(producer): sha256(producer),
            repo_path(validator): sha256(validator),
            repo_path(MANUSCRIPT): sha256(MANUSCRIPT),
        },
        "validator": {"validator_id": VALIDATOR_ID, "path": repo_path(validator)},
        "checks": checks,
        "claim_boundary": {
            "certifies": "exact artifact replay and declared finite construction checks",
            "does_not_certify": [
                "an independent proof of the manuscript theorems",
                "Lean formalization of the arbitrary-depth theorem package",
                "a universal field-independent automaton or rational function",
                "an all-depth scalar zero-count formula or asymptotic growth law",
            ],
        },
    }
    receipt["content_sha256"] = content_digest(receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    payload = json.loads(args.artifact.read_text(encoding="utf-8"))
    checks = validate(payload)
    if args.write_receipt:
        receipt = build_receipt(args.artifact, payload, checks)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(f"validated {payload['artifact_id']}: {len(checks)} checks passed")


if __name__ == "__main__":
    main()
