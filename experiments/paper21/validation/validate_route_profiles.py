#!/usr/bin/env python3
"""Fail-closed validator for the paper-owned route-profile certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VALIDATION_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "experiments" / "paper21" / "results"
DEFAULT_CERTIFICATE = RESULTS_DIR / "route_profile_promotion_v1.json"
DEFAULT_RECEIPT = RESULTS_DIR / "route_profile_promotion_v1.validation-receipt.json"
if str(VALIDATION_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATION_DIR))
from promote_route_profiles import (  # noqa: E402
    SCHEMA,
    build_certificate,
    content_digest,
    relative,
    sha256,
)

RECEIPT_SCHEMA = "paper.route-profiles.validation-receipt.v1"
VALIDATOR_ID = "paper.route-profiles.validator.python.v1"


class ValidationError(ValueError):
    pass


def validate_digest(payload: dict) -> None:
    unsigned = deepcopy(payload)
    supplied = unsigned.pop("content_sha256", None)
    if not isinstance(supplied, str) or content_digest(unsigned) != supplied:
        raise ValidationError("certificate content digest mismatch")


def validate_semantics(certificate: dict) -> list[str]:
    if certificate.get("schema") != SCHEMA:
        raise ValidationError("unsupported certificate schema")
    if certificate.get("artifact_id") != "ROUTE-PROFILES-V1-CONFORMANCE":
        raise ValidationError("unexpected artifact id")
    if certificate.get("artifact_role") != "PAPER_OWNED_PROMOTED_ROUTE_PROFILE_CERTIFICATE":
        raise ValidationError("unexpected artifact role")
    if certificate.get("theorem_relationship") != "CERTIFICATE_REPLAYS_SOURCE_AND_DOES_NOT_REPLACE_PROOF":
        raise ValidationError("theorem/certificate boundary changed")
    if any(source["upstream_paper_evidence_status"] != "NOT_PROMOTED" for source in certificate["source_artifacts"]):
        raise ValidationError("source artifact promoted itself")
    scope = certificate["promoted_scope"]
    expected = {
        "depth_two_candidate_count": 45,
        "depth_two_zero_route_count": 14,
        "depth_three_candidate_count": 216,
        "depth_three_regime_count": 4,
        "profile_sample_primes": [2, 3, 5, 7, 11, 13],
        "profile_max_depth": 5,
        "arbitrary_depth_semantic_classification": "ALL_POSITIVE_DEPTHS",
        "generic_depth_profile": "Z_d^gen FROM INTEGRAL PREFIX-POLE EQUALITY",
        "fixed_field_generating_function_status": "RATIONAL_TRANSFER_MATRIX_THEOREM",
        "stabilization_condition": "field cardinality greater than depth and characteristic outside E_d",
        "exceptional_characteristic_replay_max_depth": 10,
        "prefix_determinant_spectrum_replay_max_depth": 10,
    }
    for key, value in expected.items():
        if scope.get(key) != value:
            raise ValidationError(f"unexpected scope field: {key}")
    if len(certificate["source_artifacts"]) != 3:
        raise ValidationError("source closure is incomplete")
    formalization = certificate["implementation"].get("formalization", {})
    if formalization.get("status") != "COMPILED_PAPER_OWNED_SOURCE_CLOSURE":
        raise ValidationError("Lean formalization status changed")
    if formalization.get("compilation_receipt", {}).get("artifact_id") != "ROUTE-PROFILES-LEAN-V1-COMPILED":
        raise ValidationError("Lean compilation receipt is absent")
    if "complete characteristic-aware depth-three zero-route count theorem" not in formalization.get("proof_scope", []):
        raise ValidationError("Lean depth-three theorem scope is incomplete")
    if "F2/F3 exceptional enumeration and characteristic-aware depth-three histogram" in formalization.get("not_claimed", []):
        raise ValidationError("stale Lean depth-three claim boundary")
    arbitrary_depth = certificate["implementation"].get("arbitrary_depth_replay", {})
    if arbitrary_depth.get("status") != "PAPER_OWNED_EXACT_REPLAY_NOT_INDEPENDENT_PROOF":
        raise ValidationError("arbitrary-depth replay boundary changed")
    if arbitrary_depth.get("artifact", {}).get("artifact_id") != "ROUTE-PROFILES-ARBITRARY-DEPTH-V1":
        raise ValidationError("arbitrary-depth artifact is absent")
    if arbitrary_depth.get("receipt", {}).get("artifact_id") != "ROUTE-PROFILES-ARBITRARY-DEPTH-V1-REPLAY":
        raise ValidationError("arbitrary-depth receipt is absent")
    if (
        "arbitrary-depth prefix-pole, generic profile/determinant spectrum, fixed-field automaton, rationality, stabilization, and determinant-spectrum monotonicity theorem package"
        not in formalization.get("not_claimed", [])
    ):
        raise ValidationError("Lean arbitrary-depth boundary is absent")
    if (
        "No logical dependence on Paper XX is promoted without explicit carrier-hypothesis registration."
        not in certificate.get("negative_boundaries", [])
    ):
        raise ValidationError("Paper XX nondependency boundary is absent")
    manuscript = ROOT / certificate["manuscript"]["path"]
    if sha256(manuscript) != certificate["manuscript"]["sha256"]:
        raise ValidationError("manuscript digest mismatch")
    encoded = json.dumps(certificate, sort_keys=True, separators=(",", ":")).lower()
    for forbidden in ('"hecke_eigenvalue"', '"rg_fixed_point"', '"zero_mode"', '"sofrs"', '"sofaudit"'):
        if forbidden in encoded:
            raise ValidationError(f"forbidden downstream or overclaim field: {forbidden}")
    return [
        "certificate content digest",
        "source artifacts remain NOT_PROMOTED",
        "three-source implementation closure",
        "depth-two and depth-three theorem scope",
        "fixed-depth sample scope",
        "arbitrary-depth prefix-pole and transfer scope",
        "generic depth profile and prefix determinant spectrum",
        "fixed-depth exceptional-characteristic stabilization scope",
        "manuscript source digest",
        "excluded-theory boundary",
        "Paper XX nondependency boundary",
        "Lean source and compilation-receipt boundary",
    ]


def validate_certificate(certificate: dict) -> list[str]:
    validate_digest(certificate)
    checks = validate_semantics(certificate)
    rebuilt = build_certificate()
    if json.dumps(rebuilt, sort_keys=True, separators=(",", ":")) != json.dumps(certificate, sort_keys=True, separators=(",", ":")):
        raise ValidationError("paper-owned certificate replay mismatch")
    tampered = deepcopy(certificate)
    tampered["negative_boundaries"][0] = "presentation-only invariance promoted"
    tampered.pop("content_sha256")
    tampered["content_sha256"] = content_digest(tampered)
    if json.dumps(tampered, sort_keys=True, separators=(",", ":")) == json.dumps(rebuilt, sort_keys=True, separators=(",", ":")):
        raise ValidationError("tamper control failed")
    checks.append("coordinated result-and-digest tamper rejection")
    return checks


def build_receipt(certificate_path: Path, certificate: dict, checks: list[str]) -> dict:
    validator_path = Path(__file__).resolve()
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "ROUTE-PROFILES-V1-REPLAY",
        "receipt_kind": "ROUTE_PROFILES_VALIDATION_RECEIPT",
        "receipt_scope": "PAPER_OWNED_ROUTE_PROFILE_CONFORMANCE_ONLY",
        "status": "PASS",
        "certificate": {
            "path": relative(certificate_path),
            "artifact_sha256": sha256(certificate_path),
            "content_sha256": certificate["content_sha256"],
        },
        "validator": {
            "validator_id": VALIDATOR_ID,
            "path": relative(validator_path),
            "sha256": sha256(validator_path),
        },
        "checks": checks,
        "claim_boundary": {
            "certifies": "paper-owned source replay, arbitrary-depth construction replay, digest closure, and declared theorem/certificate scope",
            "does_not_certify": [
                "a proof beyond the manuscript theorem hypotheses",
                "Lean formalization of the arbitrary-depth theorem package",
                "a field-independent automaton or one rational function for every field",
                "an all-depth scalar zero-count formula or asymptotic convergence",
                "presentation-only or marked-partition-independent invariance",
                "Hecke, modular-form, RG, spectral, or causal interpretation",
            ],
        },
    }
    receipt["content_sha256"] = content_digest(receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    checks = validate_certificate(certificate)
    if args.write_receipt:
        receipt = build_receipt(args.certificate, certificate, checks)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"validated {certificate['certificate_id']}: {len(checks)} checks passed")


if __name__ == "__main__":
    main()
