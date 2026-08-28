#!/usr/bin/env python3
"""Validate and replay pair-hitting certificates and audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import resolve_repository_reference
from audit_pair_hitting import build_audit
from pair_hitting import pair_hitting_certificate
from registry import payload_digest


def _digest_errors(payload: dict) -> list[str]:
    unsigned = dict(payload)
    digest = unsigned.pop("content_sha256", None)
    return [] if digest == payload_digest(unsigned) else ["content digest mismatch"]


def _validate_result(result: dict) -> list[str]:
    errors: list[str] = []
    if result.get("identity_failures"):
        errors.append("pair-hitting identity failures recorded")
    if result.get("identity_row_count") != len(result.get("identity_rows", [])):
        errors.append("identity row count mismatch")
    infinite_rows = sum(
        row.get("omega") is None for row in result.get("identity_rows", [])
    )
    if result.get("infinite_identity_row_count") != infinite_rows:
        errors.append("infinite identity row count mismatch")
    for row in result.get("identity_rows", []):
        if row.get("omega") != row.get("nearest_pair_distance"):
            errors.append(f"identity mismatch at subset {row.get('subset')}")
        witness = row.get("selected_escape")
        if witness is not None and not witness.get("injective_prefix_verified"):
            errors.append(f"noninjective selected prefix at subset {row.get('subset')}")
        if witness is not None and witness.get("terminal_fiber_excess") == 1:
            if not witness.get("unit_defect_unique_pair"):
                errors.append(f"unit terminal edge lacks unique pair at {row.get('subset')}")
        corridor = row.get("kernel_corridor", {})
        if not corridor.get("reached_subset_verified"):
            errors.append(f"reaching word mismatch at subset {row.get('subset')}")
        if not corridor.get("selected_prefix_plateau_verified"):
            errors.append(f"kernel plateau failed at subset {row.get('subset')}")
        if corridor.get("all_shortest_exits_unit"):
            if not corridor.get("unit_first_exit_cover_verified"):
                errors.append(f"unit kernel cover failed at subset {row.get('subset')}")
    for row in result.get("rank_profile", []):
        has_infinity = row.get("infinite_escape_subset_count", 0) > 0
        if has_infinity != (row.get("Omega_r_exact") is None):
            errors.append(f"Omega infinity mismatch at rank {row.get('rank')}")
        threshold = row.get("packing_threshold")
        if threshold is not None and not row.get("packing_bound_holds"):
            errors.append(f"packing implication failed at rank {row.get('rank')}")
    packing_profile = result.get("packing_profile", {})
    if not packing_profile.get("all_monotonicity_checks_passed"):
        errors.append("packing profile is not monotone")
    if not packing_profile.get("all_common_transversal_rank_bounds_passed"):
        errors.append("common-transversal rank bound failed")
    previous = None
    for row in packing_profile.get("rows", []):
        if row.get("P_A_L", 0) > row.get(
            "minimum_transformation_rank_through_L", -1
        ):
            errors.append(f"single-kernel rank bound failed at L={row.get('L')}")
        if previous is not None and row.get("P_A_L", 0) > previous:
            errors.append(f"packing monotonicity failed at L={row.get('L')}")
        previous = row.get("P_A_L")
    if any(
        not row.get("bound_holds")
        for row in result.get("pin_frankl_packing_checkpoints", [])
    ):
        errors.append("Pin--Frankl packing checkpoint failed")
    unit_profile = result.get("unit_reachable_packing_profile", {})
    if not unit_profile.get("all_packing_inversion_checks_passed"):
        errors.append("reachable-unit packing inversion failed")
    for row in unit_profile.get("packing_inversion_rows", []):
        if row.get("packing_inverse_threshold") != row.get(
            "unit_wait_tail_u_bar_j"
        ):
            errors.append(f"packing inverse mismatch at j={row.get('j')}")
    unit_wait_tail_area = sum(
        unit_profile.get("unit_wait_tail_by_index", {}).values()
    )
    reachable_unit_packing_area = sum(
        max(row.get("P_A_U_reachable_L", 0) - 1, 0)
        for row in unit_profile.get("rows", [])
    )
    if unit_profile.get("unit_wait_tail_area") != unit_wait_tail_area:
        errors.append("unit waiting-tail area mismatch")
    if (
        unit_profile.get("reachable_unit_packing_area")
        != reachable_unit_packing_area
    ):
        errors.append("reachable-unit packing area mismatch")
    if not unit_profile.get("packing_area_identity_holds"):
        errors.append("reachable-unit packing area identity failed")
    if unit_wait_tail_area != reachable_unit_packing_area:
        errors.append("recomputed packing area identity failed")
    return errors


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = _digest_errors(payload)
    schema = payload.get("schema")
    if schema == "rime.synchronizing-automata.pair-hitting-packing.v1":
        errors.extend(_validate_result(payload.get("result", {})))
        if payload.get("transition_family") == "Cerny":
            state_count = max(
                state for row in payload["result"].get("pair_distances", [])
                for state in row["pair"]
            ) + 1
            from path_potential import cerny_transition

            expected = pair_hitting_certificate(cerny_transition(state_count))
            if expected != payload.get("result"):
                errors.append("Cerny certificate replay mismatch")
    elif schema == "rime.synchronizing-automata.pair-hitting-audit.v1":
        paths = [
            resolve_repository_reference(item["path"])
            for item in payload.get("source_artifacts", [])
        ]
        missing = [str(source) for source in paths if not source.is_file()]
        if missing:
            errors.append("missing source artifacts: " + ", ".join(missing))
        else:
            expected = build_audit(paths)
            if expected != payload:
                errors.append("audit replay mismatch")
        if any(row.get("identity_failure_count") for row in payload.get("rows", [])):
            errors.append("audit contains identity failures")
        if any(
            row.get("kernel_corridor_failure_count")
            for row in payload.get("rows", [])
        ):
            errors.append("audit contains kernel-corridor failures")
        if any(
            row.get("packing_inversion_failure_count")
            for row in payload.get("rows", [])
        ):
            errors.append("audit contains packing-inversion failures")
        if any(
            row.get("packing_area_identity_failure_count")
            for row in payload.get("rows", [])
        ):
            errors.append("audit contains packing-area identity failures")
        for summary in payload.get("summaries", []):
            if summary.get("kernel_corridor_failure_count"):
                errors.append(
                    "audit summary contains kernel-corridor failures at "
                    f"n={summary.get('state_count')}"
                )
            if summary.get("packing_inversion_failure_count"):
                errors.append(
                    "audit summary contains packing-inversion failures at "
                    f"n={summary.get('state_count')}"
                )
            if summary.get("packing_area_identity_failure_count"):
                errors.append(
                    "audit summary contains packing-area identity failures at "
                    f"n={summary.get('state_count')}"
                )
    else:
        errors.append("schema mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    errors = validate(args.artifact)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS PAIR-HITTING: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
