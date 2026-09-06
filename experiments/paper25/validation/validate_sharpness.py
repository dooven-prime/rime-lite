"""Validate and receipt the exact finite sharpness controls."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper25.sharpness_controls import (  # noqa: E402
    RESULT,
    SOURCE_PATHS,
    build_payload,
    content_digest,
)


RECEIPT = RESULT.with_name("diagnostic_sharpness_v1.validation-receipt.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    supplied = payload.get("content_sha256")
    if supplied != content_digest(payload):
        errors.append("content digest mismatch")
    if payload.get("claim_status") != "EXACT_FINITE_CERTIFICATE":
        errors.append("sharpness controls lost exact-certificate status")
    if payload.get("evidence_layer") != "EXACT_INTEGER_FRACTION_CERTIFICATE":
        errors.append("sharpness controls lost exact integer/Fraction layer")
    if payload.get("paper_evidence_status") != "REGISTERED_THEOREM_SUPPORT_NOT_PROOF":
        errors.append("sharpness evidence ownership changed")
    if payload.get("frozen_protocol") != {
        "integer_backend": "Python int",
        "rational_backend": "fractions.Fraction",
        "floating_point": False,
        "norms": {
            "primary": "exact Frobenius norm via squared entries",
            "operator_norm": "exact witness identities; squared values recorded",
        },
        "threshold_policy": {
            "reference_norm": "1/1",
            "error_radius": "1/1",
            "threshold": "1/1",
            "unresolved": "n-b <= tau < n+b",
        },
        "zero_policy": {
            "exact_zero": "literal Fraction(0)",
            "near_zero": "not applicable; no tolerance substitution",
        },
        "numerical_environment": {
            "python": "3.13.0",
            "encoding": "UTF-8",
            "line_endings": "LF",
        },
    }:
        errors.append("exact frozen protocol changed")
    if payload.get("claim_surface") != [
        "Theorem 3.3",
        "Theorem 3.4",
        "Definition 3.6",
        "Theorem 3.7",
        "Theorem 3.8",
        "Corollary 3.9",
        "Theorem 3.10",
        "Theorem 4.2",
    ]:
        errors.append("claim surface mismatch")

    axes = payload.get("one_axis_sharpness", {})
    if set(axes) != {"operator_axis", "left_projector_axis", "right_projector_axis"}:
        errors.append("one-axis registry mismatch")
    for name, row in axes.items():
        if row.get("equality") is not True:
            errors.append(f"{name}: equality witness failed")
        if row.get("actual_difference_squared") != row.get("global_bound_squared"):
            errors.append(f"{name}: sharp equality changed")

    family = payload.get("fixed_global_data_localization_family", [])
    if [row.get("alpha") for row in family] != ["0/1", "3/5", "1/1"]:
        errors.append("localization family registry mismatch")
    global_records = {
        (row.get("operator_norm_squared"), row.get("frobenius_norm_squared"))
        for row in family
    }
    if len(global_records) != 1:
        errors.append("localization family no longer has fixed global data")
    if not family or family[0].get("localized_error_squared") != "0/1":
        errors.append("zero localized-impact witness missing")
    if not family or family[-1].get("localized_to_global_ratio_squared") != "1/1":
        errors.append("global-bound equality witness missing")

    lattice = payload.get("carrier_information_lattice", {})
    grid = lattice.get("rank_one_rational_grid", [])
    if len(grid) != 16:
        errors.append("carrier-information rank-one grid changed")
    for row in grid:
        try:
            values = [
                Fraction(row[key])
                for key in ("U_loc", "U_LR", "U_L", "U_R", "U_G")
            ]
        except (KeyError, ValueError, ZeroDivisionError):
            errors.append("carrier-information grid has invalid rational data")
            continue
        local, bilateral, left, right, global_bound = values
        if local > bilateral or bilateral > left or bilateral > right:
            errors.append("carrier-information lattice order was violated")
        if left > global_bound or right > global_bound:
            errors.append("semi-local envelope exceeded global envelope")
    bilateral_pair = lattice.get("bilateral_semilocal_nonidentifiability", {})
    identity = bilateral_pair.get("identity", {})
    swap = bilateral_pair.get("swap", {})
    for key in ("global_2", "global_F_squared", "left", "right"):
        if identity.get(key) != swap.get(key):
            errors.append("identity/swap hostile pair lost equal semilocal data")
    if identity.get("local") != "1/1" or swap.get("local") != "0/1":
        errors.append("identity/swap hostile pair no longer separates local data")

    joint = payload.get("three_axis_joint_strictness", {})
    if joint.get("carrier_error_parallel_squared") != "0/1":
        errors.append("joint strictness witness lost orthogonal carrier error")
    if joint.get("exact_additive_supremum_squared") != "2101/2500":
        errors.append("joint exact supremum changed")
    if joint.get("strictly_below_localized_sum") is not True:
        errors.append("joint localized strictness witness failed")
    if joint.get("strictly_below_global_sum") is not True:
        errors.append("joint global strictness witness failed")

    equality = payload.get("localized_triangle_equality", {})
    if equality.get("active_term_count") != 2:
        errors.append("localized equality witness must have two active terms")
    if equality.get("actual_difference_squared") != "4/1":
        errors.append("localized equality witness actual norm changed")
    if equality.get("localized_bound") != "2/1" or equality.get("equality") is not True:
        errors.append("localized equality witness failed")

    margin = payload.get("unresolved_two_sided_realization", {})
    if margin.get("policy_status") != "UNRESOLVED":
        errors.append("margin hostile fixture is not unresolved")
    if margin.get("inactive_realization", {}).get("status") != "INACTIVE":
        errors.append("inactive unresolved realization missing")
    if margin.get("active_realization", {}).get("status") != "ACTIVE":
        errors.append("active unresolved realization missing")

    expected_sources = {
        path.as_posix(): sha256(ROOT / path) for path in SOURCE_PATHS
    }
    observed_sources = {
        row.get("path"): row.get("sha256") for row in payload.get("source_artifacts", [])
    }
    if observed_sources != expected_sources:
        errors.append("source closure mismatch")

    replay = build_payload()
    if payload != replay:
        errors.append("retained exact certificate differs from replay")
    return errors


def write_receipt(payload: dict) -> None:
    validator = Path(__file__).resolve()
    receipt = {
        "schema": "rime.paper25.diagnostic-sharpness-receipt.v1",
        "artifact_id": "PAPER25-DIAGNOSTIC-SHARPNESS-V1-VALIDATED",
        "status": "PASS",
        "scope": "local exact replay and source-closure validation; not independent proof",
        "artifact": {
            "path": RESULT.relative_to(ROOT).as_posix(),
            "sha256": sha256(RESULT),
            "content_sha256": payload["content_sha256"],
        },
        "source_closure": {
            Path(__file__).resolve().relative_to(ROOT).as_posix(): sha256(validator),
            **{path.as_posix(): sha256(ROOT / path) for path in SOURCE_PATHS},
        },
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"WROTE {RECEIPT}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        print("FAIL diagnostic sharpness certificate")
        for error in errors:
            print(f"  - {error}")
        return 1
    if args.write_receipt:
        write_receipt(payload)
    print(f"PASS {RESULT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
