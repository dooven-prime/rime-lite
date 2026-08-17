#!/usr/bin/env python3
"""Replay the Paper VIII v2.1 marked finite-realization certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATION_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "experiments" / "paper8" / "results" / "v2.1"
DEFAULT_CERTIFICATE = RESULTS_DIR / "marked_finite_realization_conformance_v2_1.json"
DEFAULT_RECEIPT = RESULTS_DIR / "marked_finite_realization_conformance_v2_1.validation-receipt.json"

if str(VALIDATION_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATION_DIR))

from promote_marked_finite_realizations_v2_1 import (  # noqa: E402
    SCHEMA,
    build_certificate,
    content_digest,
)


RECEIPT_SCHEMA = "paper8.marked-finite-realization-validation-receipt.v2.1"
VALIDATOR_ID = "paper8.marked-finite-realization-validator.python.v2.1"


class ValidationError(ValueError):
    """Raised when the promoted certificate fails closure or replay."""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def validate_digest(payload: dict) -> None:
    unsigned = deepcopy(payload)
    try:
        supplied = unsigned.pop("content_sha256")
    except KeyError as exc:
        raise ValidationError("content_sha256 is required") from exc
    if not isinstance(supplied, str) or content_digest(unsigned) != supplied:
        raise ValidationError("certificate content digest mismatch")


def validate_semantics(certificate: dict) -> list[str]:
    if certificate.get("schema") != SCHEMA:
        raise ValidationError("unsupported certificate schema")
    if certificate.get("artifact_id") != "P8V2.1-CONFORMANCE":
        raise ValidationError("unexpected certificate artifact ID")
    if certificate.get("artifact_role") != (
        "PAPER_OWNED_PROMOTED_CONFORMANCE_CERTIFICATE"
    ):
        raise ValidationError("unexpected artifact role")
    if certificate.get("claim_status") != "Computational Certificate":
        raise ValidationError("unexpected claim status")
    if certificate.get("theorem_relationship") != (
        "CONFORMANCE_WITNESS_NOT_THEOREM_PREMISE"
    ):
        raise ValidationError("theorem/evidence boundary changed")
    if any(
        source["upstream_paper_evidence_status"] != "NOT_PROMOTED"
        for source in certificate["source_artifacts"]
    ):
        raise ValidationError("an exploratory source promoted itself")

    scope = certificate["promoted_scope"]
    expected_scope = {
        "modular_prime_count": 6,
        "triangle_representation_count": 17,
        "triangle_full_signature_order_count": 12,
        "triangle_proper_order_divisor_count": 5,
        "triangle_marked_sectorization_count": 51,
        "saturation_receipt_count": 57,
        "label_collision_witness_count": 3,
    }
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            raise ValidationError(f"unexpected promoted scope for {field}")

    witness = certificate["path_route_word_hostile_witness"]
    if witness["boolean_path_2_target_by_source"] != [[1, 1], [1, 1]]:
        raise ValidationError("hostile Path_2 witness changed")
    if witness["actual_route_2_target_by_source"] != [[1, 0], [0, 1]]:
        raise ValidationError("hostile Route_2 witness changed")
    if witness["actual_word_2_target_by_source"] != [[1, 0], [0, 1]]:
        raise ValidationError("hostile W_2 witness changed")
    if witness["certified_relation"] != (
        "W_2_EQUALS_ROUTE_2_STRICT_SUBSET_PATH_2"
    ):
        raise ValidationError("hostile relation was promoted or weakened")

    receipts = certificate["finite_saturation_receipts"]
    if len(receipts) != scope["saturation_receipt_count"]:
        raise ValidationError("saturation receipt count mismatch")
    for receipt in receipts:
        if receipt["saturation_status"] != "EXACT_FINITE_POSITIVE_CLOSURE":
            raise ValidationError("finite saturation status changed")
        if not receipt["right_multiplication_closed"]:
            raise ValidationError("represented closure is not right closed")
        if receipt["closure_stabilization_depth"] < 1:
            raise ValidationError("invalid closure stabilization depth")
        if not receipt["closure_trace"]:
            raise ValidationError("missing closure trace")
        if receipt["closure_trace"][-1][
            "cumulative_represented_operators"
        ] != receipt["represented_positive_closure_order"]:
            raise ValidationError("closure trace does not reach represented image")
        if receipt["shortest_nonempty_identity_word_length"] < 1:
            raise ValidationError("empty word entered positive depth")
        if receipt["infinite_after_saturation_count"] != 0:
            raise ValidationError("transitive promoted carrier has an infinite pair")

    collisions = certificate["label_collision_witnesses"]
    if len(collisions) != scope["label_collision_witness_count"]:
        raise ValidationError("label collision witness count mismatch")
    if any(
        not item["labels_distinct"] or not item["represented_operators_equal"]
        for item in collisions
    ):
        raise ValidationError("label/operator distinction was collapsed")

    partition_witness = certificate["marked_partition_witness"]
    if len(set(partition_witness["marked_partition_sha256"].values())) != 3:
        raise ValidationError("marked sectorizations were identified")
    if any(
        item["alignment_status"] != "EXPLICIT_INTERSECTION_TABLE_ONLY"
        for item in partition_witness["pairwise_controls"]
    ):
        raise ValidationError("intersection data was promoted to alignment")

    encoded = canonical_json(certificate).lower()
    forbidden_keys = (
        '"lie_depth"',
        '"sofrs"',
        '"sofaudit"',
        '"selberg_trace"',
        '"hecke_eigenvalue"',
    )
    if any(key in encoded for key in forbidden_keys):
        raise ValidationError("a downstream or excluded carrier field was smuggled")

    return [
        "certificate content digest",
        "exploratory source status and exact scope",
        "full source-bundle replay through installed producer closure",
        "marked partition distinction",
        "noninjective label-map preservation",
        "four-state Path/Route/W hostile relation",
        "57 finite positive-closure saturation receipts",
        "positive first-hit convention d>=1",
        "excluded-carrier field rejection",
    ]


def validate_certificate(certificate: dict) -> list[str]:
    validate_digest(certificate)
    checks = validate_semantics(certificate)
    rebuilt = build_certificate()
    if canonical_json(rebuilt) != canonical_json(certificate):
        raise ValidationError("paper-owned certificate replay mismatch")

    tampered = deepcopy(certificate)
    tampered["path_route_word_hostile_witness"]["certified_relation"] = (
        "PATH_AND_WORD_IDENTIFIED"
    )
    tampered.pop("content_sha256")
    tampered["content_sha256"] = content_digest(tampered)
    if canonical_json(tampered) == canonical_json(rebuilt):
        raise ValidationError("coordinated result tamper escaped replay")
    checks.append("coordinated result-and-digest tamper rejection")
    return checks


def build_receipt(certificate_path: Path, certificate: dict, checks: list[str]) -> dict:
    validator_path = Path(__file__).resolve()
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "artifact_id": "P8V2.1-REPLAY",
        "receipt_kind": "PAPER8_CONFORMANCE_VALIDATION_RECEIPT",
        "receipt_scope": "PAPER8_V2_1_PROMOTION_CONFORMANCE_ONLY",
        "status": "PASS",
        "paper": "Paper VIII",
        "candidate_version": "2.1",
        "certificate": {
            "path": relative(certificate_path),
            "artifact_sha256": file_sha256(certificate_path),
            "content_sha256": certificate["content_sha256"],
        },
        "source_artifacts": certificate["source_artifacts"],
        "producer_implementation": certificate["implementation"],
        "validator": {
            "validator_id": VALIDATOR_ID,
            "path": relative(validator_path),
            "sha256": file_sha256(validator_path),
        },
        "checks": checks,
        "claim_boundary": {
            "certifies": "exact promoted conformance artifact and replay closure",
            "does_not_certify": [
                "a new proof of the abstract SOF object theory",
                "canonical sectorization",
                "Lie/Hall accessibility or Lie depth",
                "surface, automorphic, Hecke, moduli, or Selberg claims",
                "SOFRS or SOFAUDIT admission",
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
        args.receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        f"validated {certificate['certificate_id']}: "
        f"{len(checks)} checks passed"
    )


if __name__ == "__main__":
    main()
