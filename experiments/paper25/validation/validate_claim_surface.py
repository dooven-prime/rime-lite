"""Validate the Paper XXV manuscript/evidence claim map."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAP = HERE.parent / "claim-surface-map.json"

OBSERVATION_STATUSES = {
    "BOUNDED_NUMERICAL_OBSERVATION",
    "MIXED_EXACT_AND_BOUNDED_NUMERICAL_CONTROL",
    "EXACT_FINITE_CERTIFICATE_AND_BOUNDED_NUMERICAL_OBSERVATION",
}


def main() -> int:
    spec = json.loads(MAP.read_text(encoding="utf-8"))
    errors: list[str] = []
    if spec.get("schema") != "rime.paper25.claim-surface-map.v2":
        errors.append("claim-map schema mismatch")
    if spec.get("map_id") != "PAPER25-CLAIM-SURFACE-V2":
        errors.append("claim-map identity mismatch")
    if spec.get("evidence_layers") != [
        "EXACT_INTEGER_FRACTION_CERTIFICATE",
        "BOUNDED_FLOAT64_OBSERVATION",
    ]:
        errors.append("evidence-layer registry mismatch")

    manuscript_path = ROOT / spec.get("manuscript", "")
    if not manuscript_path.is_file():
        errors.append("canonical manuscript is missing")
        manuscript = ""
    else:
        manuscript = manuscript_path.read_text(encoding="utf-8")

    seen_claims: set[str] = set()
    seen_support: set[str] = set()
    support_bindings = 0
    for claim in spec.get("claims", []):
        claim_id = claim.get("claim_id", "")
        if not claim_id or claim_id in seen_claims:
            errors.append(f"duplicate or missing claim id: {claim_id!r}")
        seen_claims.add(claim_id)
        if claim.get("authority") != "manuscript proof":
            errors.append(f"{claim_id}: theorem authority drift")
        for marker in claim.get("manuscript_markers", []):
            if marker not in manuscript:
                errors.append(f"{claim_id}: missing manuscript marker {marker!r}")

        for support in claim.get("support", []):
            support_bindings += 1
            path_text = support.get("path", "")
            component = support.get("component")
            level = support.get("evidence_layer")
            if "receipt" in Path(path_text).name:
                errors.append(f"{claim_id}: receipt used as claim premise")
            path = ROOT / path_text
            if not path.is_file():
                errors.append(f"{claim_id}: missing support {path_text}")
                continue
            seen_support.add(path_text)
            payload = json.loads(path.read_text(encoding="utf-8"))
            status = payload.get("claim_status")
            if component != "whole_artifact" and component not in payload:
                errors.append(f"{claim_id}: missing registered component {component!r}")
            if level == "EXACT_INTEGER_FRACTION_CERTIFICATE":
                if status not in {
                    "EXACT_FINITE_CERTIFICATE",
                    "EXACT_FINITE_CERTIFICATE_AND_BOUNDED_NUMERICAL_OBSERVATION",
                }:
                    errors.append(f"{claim_id}: exact support status drift")
            elif level == "BOUNDED_FLOAT64_OBSERVATION":
                if status not in OBSERVATION_STATUSES:
                    errors.append(f"{claim_id}: observation status drift")
            else:
                errors.append(f"{claim_id}: unsupported evidence level {level!r}")

    if seen_claims != {"C1", "C2", "C3", "C4"}:
        errors.append("claim registry mismatch")
    if len(seen_support) != 6 or support_bindings != 7:
        errors.append("support registry mismatch")

    claims = {claim["claim_id"]: claim for claim in spec.get("claims", [])}
    c2_paths = {row["path"] for row in claims.get("C2", {}).get("support", [])}
    if c2_paths != {
        "experiments/paper25/results/rubik_perturbation_sweep_v1.json"
    }:
        errors.append("Rubik perturbation scope drift")
    else:
        rubik = json.loads((ROOT / next(iter(c2_paths))).read_text(encoding="utf-8"))
        axis_labels = {
            "OPERATOR_ONLY": "operator",
            "SECTORIZATION_ONLY": "sector",
            "COUPLED": "coupled",
        }
        final_records = {
            row.get("sweep_axis"): row
            for row in rubik.get("records", [])
            if row.get("level_index") == 5
        }
        for axis, label in axis_labels.items():
            row = final_records.get(axis, {})
            summary = row.get("localized_to_global_summary", {})
            median = summary.get("median", 0.0)
            if median == 0.0:
                median_text = "$0$"
            elif median < 1e-15:
                median_text = "$<10^{-15}$"
            else:
                median_text = f"${median:.5f}$"
            expected_ratio_row = (
                f"| {label} | ${summary.get('positive_global_coordinate_count')}$ | "
                f"${summary.get('zero_ratio_count')}$ | {median_text} | "
                f"${summary.get('mean', 0.0):.5f}$ | "
                f"${summary.get('maximum', 0.0):.5f}$ |"
            )
            expected_bound_row = (
                f"| {label} | "
                f"${row.get('maximum_declared_bound', 0.0):.5f}$ | "
                f"${row.get('localized_bound', {}).get('maximum', 0.0):.5f}$ | "
                f"${row.get('aggregate_undirected_margin_counts', {}).get('UNRESOLVED')}"
                f"\\to{row.get('localized_bound', {}).get('aggregate_undirected_margin_counts', {}).get('UNRESOLVED')}$ |"
            )
            if expected_ratio_row not in manuscript:
                errors.append(f"Rubik ratio table differs from retained evidence: {axis}")
            if expected_bound_row not in manuscript:
                errors.append(f"Rubik bound table differs from retained evidence: {axis}")
    c4_paths = {row["path"] for row in claims.get("C4", {}).get("support", [])}
    if c4_paths != {
        "experiments/paper25/results/nonnormal_markov_stability_v1.json",
        "experiments/paper25/results/markov_probability_alignment_v1.json",
    }:
        errors.append("Markov portability scope drift")

    if errors:
        print("FAIL Paper XXV claim-surface map")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"PASS {spec['map_id']}: {len(seen_claims)} claim groups, "
        f"{support_bindings} layered evidence bindings over {len(seen_support)} artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
