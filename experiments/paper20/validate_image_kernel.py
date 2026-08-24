#!/usr/bin/env python3
"""Validate and optionally replay the Rubik depth-2 image-kernel audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_ARTIFACT = HERE / "results" / "image_kernel" / "rubik_depth2_shared_carrier_v1.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.census import content_digest  # noqa: E402
from experiments.paper20.image_kernel_census import (  # noqa: E402
    ARTIFACT_ID,
    CATEGORY_KEYS,
    SCHEMA,
    build_payload,
)


EXPECTED_PAIRS = {
    (2, 0), (3, 0), (5, 0), (6, 0), (7, 0), (8, 0),
    (0, 2), (0, 3), (0, 5), (0, 6), (0, 7), (0, 8),
}
EXPECTED_ROUTE_COUNTS = {
    "both_factors_zero": 19008,
    "prefix_zero_only": 7992,
    "suffix_zero_only": 7992,
    "nontrivial_image_kernel_annihilation": 0,
    "active_product": 0,
}
EXPECTED_CARRIER_COUNTS = {
    "both_factors_zero": 25272,
    "prefix_zero_only": 7776,
    "suffix_zero_only": 7776,
    "nontrivial_image_kernel_annihilation": 0,
    "active_product": 0,
}


def validate(path: Path = DEFAULT_ARTIFACT, *, recompute: bool = False) -> list[str]:
    errors: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("content_sha256") != content_digest(payload):
        errors.append("content digest mismatch")
    if payload.get("schema_version") != SCHEMA or payload.get("artifact_id") != ARTIFACT_ID:
        errors.append("schema or artifact identity mismatch")
    if payload.get("claim_status") != "mixed_evidence_bundle":
        errors.append("claim status changed")
    expected_component_status = {
        "finite_route_space_enumeration": "Computational Certificate",
        "factor_and_product_norms": "Computational Observation",
        "exact_projected_factor_zero": "Not Established",
        "exact_all_depth_zero": "Not Established",
    }
    if payload.get("claim_status_by_component") != expected_component_status:
        errors.append("component claim-status boundary changed")
    layers = payload.get("evidence_layers", {})
    enumeration = layers.get("enumeration_certificate", {})
    numerical = layers.get("numerical_observation", {})
    exact_zero = layers.get("exact_zero_status", {})
    if enumeration.get("status") != "EXACT_FINITE_ENUMERATION_CERTIFICATE":
        errors.append("finite enumeration certificate status changed")
    if enumeration.get("selection_basis") != "BOUNDED_NUMERICAL_SOURCE_CENSUS":
        errors.append("enumeration selection basis was overpromoted")
    if enumeration.get("pair_count") != 12:
        errors.append("enumeration certificate pair count changed")
    if enumeration.get("route_count_per_pair_formula") != "9 * 18^2 = 2916":
        errors.append("route-space formula changed")
    if enumeration.get("route_audit_count_formula") != "12 * 2916 = 34992":
        errors.append("aggregate route-space formula changed")
    if enumeration.get("shared_carrier_route_audit_count") != 40824:
        errors.append("carrierwise enumeration certificate changed")
    if numerical.get("status") != "BOUNDED_NUMERICAL_OBSERVATION":
        errors.append("numerical evidence was not kept observational")
    if numerical.get("coefficient_backend") != "complex128":
        errors.append("numerical coefficient backend changed")
    expected_exact_zero = {
        "status": "NOT_ESTABLISHED",
        "projected_factor_zero": "NOT_ESTABLISHED",
        "nontrivial_image_kernel_absence": "NOT_ESTABLISHED_AS_EXACT",
        "all_depth_zero": "NOT_ESTABLISHED",
    }
    if exact_zero != expected_exact_zero:
        errors.append("exact-zero status was overpromoted")
    if payload.get("audited_depth") != 2 or payload.get("cut_after_transport") != 1:
        errors.append("audit depth or cut changed")
    if payload.get("route_count_per_pair") != 2916:
        errors.append("route count per pair changed")
    selection = payload.get("selection", {})
    pairs = {tuple(pair) for pair in selection.get("pairs", [])}
    if selection.get("pair_count") != 12 or pairs != EXPECTED_PAIRS:
        errors.append("shared-carrier null-pair selection changed")
    support = payload.get("thresholded_support_graph", {})
    if 0 not in support.get("isolated_self_loop_sectors", []):
        errors.append("sector 0 is not registered as an isolated self-loop")
    if support.get("all_selected_pairs_absent_from_transitive_closure") is not True:
        errors.append("selected pairs entered the thresholded support closure")
    aggregate = payload.get("aggregate", {})
    if aggregate.get("pair_count") != 12 or aggregate.get("route_audit_count") != 34992:
        errors.append("aggregate pair or route count changed")
    if aggregate.get("shared_carrier_route_audit_count") != 40824:
        errors.append("shared-carrier route count changed")
    if aggregate.get("route_categories") != EXPECTED_ROUTE_COUNTS:
        errors.append("route obstruction histogram changed")
    if aggregate.get("shared_carrier_route_categories") != EXPECTED_CARRIER_COUNTS:
        errors.append("carrierwise obstruction histogram changed")
    if aggregate.get("nontrivial_image_kernel_annihilation_count") != 0:
        errors.append("nontrivial image-kernel count changed")
    if aggregate.get("conclusion") != "ALL_DEPTH_TWO_ROUTES_FACTOR_ZERO_WITHIN_TOLERANCE":
        errors.append("bounded conclusion changed")
    if aggregate.get("all_depth_exact_status") != "NOT_ESTABLISHED":
        errors.append("all-depth exact status was overpromoted")
    tolerance = payload.get("tolerance")
    if not isinstance(tolerance, (int, float)) or tolerance <= 0:
        errors.append("invalid numerical tolerance")
    else:
        if aggregate.get("max_product_norm", float("inf")) > tolerance:
            errors.append("a depth-two product exceeds tolerance")
        if aggregate.get("max_min_factor_norm", float("inf")) > tolerance:
            errors.append("a route has two factors above tolerance")
    for row in payload.get("pair_audits", []):
        counts = row.get("route_categories", {})
        if set(counts) != set(CATEGORY_KEYS) or sum(counts.values()) != 2916:
            errors.append("pair route-category partition is invalid")
            break
        if counts["nontrivial_image_kernel_annihilation"] or counts["active_product"]:
            errors.append("pair contains a non-factor-zero route")
            break
        if row.get("depth_two_status") != "BOUNDED_FACTOR_ZERO_OBSERVATION":
            errors.append("pair-level numerical status was overpromoted")
            break
    for reference in payload.get("source_artifacts", []):
        source = ROOT / reference["uri"]
        if not source.is_file() or source_reference_hash(source) != reference.get("sha256"):
            errors.append(f"stale or missing source: {reference.get('uri')}")
    if recompute:
        rebuilt = build_payload(ROOT / payload["source_census"]["artifact"]["uri"])
        if json.loads(json.dumps(rebuilt)) != payload:
            errors.append("image-kernel producer replay mismatch")
    return errors


def source_reference_hash(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--recompute", action="store_true")
    args = parser.parse_args()
    errors = validate(args.artifact, recompute=args.recompute)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    replay = " with producer replay" if args.recompute else ""
    print(f"PASS {ARTIFACT_ID}{replay}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
