"""Paper XI post-v1 robustness audit for the four added wall profiles.

The audit calls the canonical profile implementations. It tests local order
and endpoint controls for the constructed collision, seed/ensemble sensitivity
for percolation and Kuramoto, and matched-method plus deterministic basin-loss
controls for the GRN. It does not claim universality or modify the frozen v1.0
census.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from degenerate_endpoint_collision import run_audit as run_goe  # noqa: E402
from grn_toggle_wall import (  # noqa: E402
    edge_deformation_audit,
    noise_method_control,
)
from kuramoto_wall import run_audit as run_kuramoto  # noqa: E402
from percolation_wall import run_audit as run_percolation  # noqa: E402


def goe_robustness() -> dict:
    rows = []
    for seed in (42, 43, 44, 45):
        audit = run_goe(seed=seed, robustness_draws=16)
        orders = [item["fitted_order"] for item in audit["collisions"]]
        rows.append(
            {
                "seed": seed,
                "collision_count": audit["collision_count"],
                "minimum_order": min(orders),
                "maximum_order": max(orders),
                "minimum_non_target_gap": audit[
                    "minimum_non_target_gap_on_local_interval"
                ],
                "endpoint_lifting_passed": all(
                    not item["collisions_retained"]
                    for item in audit["endpoint_lifting_negative_control"]
                ),
            }
        )
    passed = all(
        row["collision_count"] == 2
        and 0.98 <= row["minimum_order"] <= row["maximum_order"] <= 1.02
        and row["minimum_non_target_gap"] > 0.5
        and row["endpoint_lifting_passed"]
        for row in rows
    )
    if not passed:
        raise AssertionError("GOE constructed-endpoint robustness control failed")
    return {"status": "pass", "rows": rows}


def percolation_robustness() -> dict:
    rows = []
    for ensemble in (8, 16, 32):
        for seed in (42, 142):
            audit = run_percolation(ensemble_size=ensemble, seed=seed)
            rows.append(
                {
                    "ensemble": ensemble,
                    "seed": seed,
                    "wall_p": audit["wall_p"],
                    "variance_peak_p": audit["variance_peak_p"],
                    "wall_drop": audit["wall_drop"],
                    "monotone_support_verified": audit[
                        "monotone_support_verified"
                    ],
                }
            )
    passed = all(
        row["monotone_support_verified"]
        and 0.04 <= row["wall_p"] <= 0.14
        and row["wall_drop"] < 0
        for row in rows
    )
    if not passed:
        raise AssertionError("percolation nested-path robustness control failed")
    return {
        "status": "pass",
        "rows": rows,
        "wall_p_range": [min(row["wall_p"] for row in rows), max(row["wall_p"] for row in rows)],
        "variance_peak_p_range": [
            min(row["variance_peak_p"] for row in rows),
            max(row["variance_peak_p"] for row in rows),
        ],
    }


def kuramoto_robustness() -> dict:
    rows = []
    for seed in (42, 142):
        audit = run_kuramoto(ensemble_size=4, seed=seed)
        rows.append(
            {
                "seed": seed,
                "wall_K": audit["wall_K"],
                "wall_increase": audit["wall_increase"],
                "paired_change_mean": audit["paired_frozen_depth_change_mean"],
                "paired_change_std": audit["paired_frozen_depth_change_std"],
                "freezing_fraction": audit["freezing_fraction"],
            }
        )
    passed = all(
        row["wall_increase"] > 0
        and row["paired_change_mean"] > 0
        and row["freezing_fraction"] >= 0.75
        for row in rows
    )
    if not passed:
        raise AssertionError("Kuramoto freezing-direction robustness control failed")
    return {
        "status": "pass",
        "rows": rows,
        "wall_K_range": [min(row["wall_K"] for row in rows), max(row["wall_K"] for row in rows)],
    }


def grn_robustness(full: bool) -> dict:
    if full:
        method = noise_method_control(ensemble_size=3, trajectories=12, seed=42)
        protocol = "3 seeds x 12 trajectories"
    else:
        method = noise_method_control(ensemble_size=1, trajectories=2, seed=42)
        protocol = "smoke: 1 seed x 2 trajectories"
    edge = edge_deformation_audit()
    passed = (
        not method["noise_wall_admitted"]
        and edge["reference"]["attractor_count"] == 2
        and edge["edge_deleted"]["attractor_count"] == 1
        and len(edge["removed_terminal_sectors"]) >= 1
    )
    if not passed:
        raise AssertionError("GRN method/basin-loss robustness control failed")
    return {
        "status": "pass",
        "protocol": protocol,
        "CLE_relative_range": method["CLE_relative_range"],
        "SSA_relative_range": method["SSA_relative_range"],
        "maximum_method_gap": method["maximum_method_gap"],
        "SSA_basin_switches": [
            row["SSA_basin_switches_per_trajectory_mean"] for row in method["rows"]
        ],
        "coarse_wall_bracket": edge["wall_bracket"],
        "refined_controlled_grid_bracket": edge["refined_controlled_grid_bracket"],
        "removed_terminal_sectors": edge["removed_terminal_sectors"],
    }


def run_audit(full_grn: bool = False) -> dict:
    result = {
        "claim_status": "post_v1_profile_robustness",
        "GOE": goe_robustness(),
        "percolation": percolation_robustness(),
        "Kuramoto": kuramoto_robustness(),
        "GRN": grn_robustness(full=full_grn),
    }
    result["all_passed"] = all(
        result[name]["status"] == "pass"
        for name in ("GOE", "percolation", "Kuramoto", "GRN")
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-grn",
        action="store_true",
        help="run the 3 x 12 exact-SSA validation instead of the smoke protocol",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_audit(full_grn=args.full_grn)
    print("=" * 72)
    print("  Paper XI post-v1 profile robustness audit")
    print("=" * 72)
    print(f"GOE: pass across {len(result['GOE']['rows'])} splitting directions")
    print(
        "Percolation: wall p range "
        f"{result['percolation']['wall_p_range']}, variance-peak range "
        f"{result['percolation']['variance_peak_p_range']}"
    )
    print(
        "Kuramoto: wall K range "
        f"{result['Kuramoto']['wall_K_range']}; freezing direction passed"
    )
    print(
        f"GRN ({result['GRN']['protocol']}): basin-loss bracket "
        f"{result['GRN']['refined_controlled_grid_bracket']}; "
        f"terminal sectors removed {result['GRN']['removed_terminal_sectors']}"
    )
    print(f"All profile controls passed: {result['all_passed']}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
