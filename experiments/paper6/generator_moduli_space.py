"""Paper VI support script: generator-set moduli and Sigma_comm.

Status: computational observation for Paper VI, not a theorem.

This script stabilizes the first Paper VI experimental table layer:

1. Single-generator deletions leave the QT/HT collision quotient blocked.
2. Selected generator families separate collision quotient behavior from the
   globally defined A(w)-spectrum.
3. A two-weight plane gives a transverse slice through Sigma_comm, while A(w)
   varies across the full sampled plane.
"""

from __future__ import annotations

import os
import sys

import numpy as np

if __package__ in (None, ""):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    sys.path.insert(0, SCRIPT_DIR)
    sys.path.insert(0, REPO_ROOT)

from phase_utils import (  # noqa: E402
    assert_stable_snapshot,
    move_label,
    prim_data,
    scan_axis0_ht_plane,
    selected_family_rows,
    single_deletion_rows,
    summarize_single_deletions,
)


np.random.seed(42)

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
)
BIFURCATION_LOG_PATH = os.path.join(OUT_DIR, "_paper6_bifurcation_log.txt")


def write_bifurcation_log(
    deletion_rows: list[dict],
    family_rows: list[dict],
    plane_summary: dict,
) -> None:
    """Write the stabilized Part I table snapshot."""
    single_summary = summarize_single_deletions(deletion_rows)
    lines = [
        "=" * 72,
        "Paper VI: Bifurcation Table Snapshot",
        "=" * 72,
        "This is an experimental support table, not a paper theorem source.",
        "",
        "Single-generator deletions:",
    ]
    for row in deletion_rows:
        lines.append(
            f"  -{row['label']:>3s}: "
            f"CQ={row['cq_status']} "
            f"(comm={row['comm_norm']:.2e}), "
            f"A-layers={row['a_layers']}, A-field={row['a_field']}"
        )
    lines.extend(
        [
            (
                f"  [OK] {single_summary['cq_blocked']}/{single_summary['total']} "
                "deletions leave the QT/HT collision quotient blocked."
            ),
            f"  A-layer counts: {single_summary['a_layer_counts']}",
            f"  A-field counts: {single_summary['a_field_counts']}",
            "",
            "Selected families:",
        ]
    )
    for row in family_rows:
        lines.append(
            f"  {row['family']:<28s} "
            f"CQ={row['cq_status']:>7s} "
            f"CQ-layers={str(row['cq_layers']):>4s} CQ-field={row['cq_field']:<10s} "
            f"A-layers={row['a_layers']:>3d} A-field={row['a_field']}"
        )
    lines.extend(
        [
            "",
            "2D weight scan (axis-0 half-turn weights):",
            f"  Grid: {plane_summary['grid']} x {plane_summary['grid']}",
            f"  CQ commutative cells: {plane_summary['cq_commutative']}/{plane_summary['total']}",
            f"  CQ layer counts on commutative cells: {plane_summary['cq_layers']}",
            f"  A-spectrum layer counts: {plane_summary['a_layers']}",
            "",
            "Observed internal hierarchy inside Sigma_comm:",
            "  Sigma_field -> Sigma_L",
            "  Sigma_comm is the primary object; its global ideal/equations remain open.",
            "  The canonical tangent model is handled by tangent_commutator_map.py.",
            "  A(w)-spectrum is globally defined on the full weight space.",
            "",
            "[snapshot OK: Sigma_comm primary object and internal events recorded]",
        ]
    )
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(BIFURCATION_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def print_single_deletions(rows: list[dict]) -> None:
    print("\nSingle-generator deletion audit:")
    for row in rows:
        print(
            f"  -{row['label']:>3s}: "
            f"CQ={row['cq_status']} "
            f"(comm={row['comm_norm']:.2e}), "
            f"A-layers={row['a_layers']}, A-field={row['a_field']}"
        )

    summary = summarize_single_deletions(rows)
    print(
        f"  [OK] {summary['cq_blocked']}/{summary['total']} single deletions leave "
        "the QT/HT collision quotient blocked."
    )
    print(f"  A-layer counts: {summary['a_layer_counts']}")
    print(f"  A-field counts: {summary['a_field_counts']}")


def print_family_rows(rows: list[dict]) -> None:
    print("\nSelected deletion families:")
    for row in rows:
        print(
            f"  {row['family']:<28s} "
            f"CQ={row['cq_status']:>7s} "
            f"CQ-layers={str(row['cq_layers']):>4s} CQ-field={row['cq_field']:<10s} "
            f"A-layers={row['a_layers']:>3d} A-field={row['a_field']}"
        )


def print_plane_summary(summary: dict) -> None:
    print("\n2D weight scan over the two axis-0 half-turn weights:")
    print(f"  Grid: {summary['grid']} x {summary['grid']}")
    print(f"  CQ commutative cells: {summary['cq_commutative']}/{summary['total']}")
    print(f"  CQ layer counts on commutative cells: {summary['cq_layers']}")
    print(f"  A-spectrum layer counts on full grid: {summary['a_layers']}")


def main() -> None:
    keys, rhos = prim_data()
    assert len(keys) == 18

    print("=" * 72)
    print("Paper VI: Generator-Set Moduli Space")
    print("=" * 72)
    print("Generator order:")
    for idx, key in enumerate(keys):
        kind = "HT" if key[2] == 2 else "QT"
        print(f"  [{idx:02d}] {move_label(key):>3s}  key={key}  {kind}")

    deletion_rows = single_deletion_rows(keys, rhos)
    family_rows = selected_family_rows(keys, rhos)
    plane_summary = scan_axis0_ht_plane(keys, rhos, grid=11)

    print_single_deletions(deletion_rows)
    print_family_rows(family_rows)
    print_plane_summary(plane_summary)

    assert_stable_snapshot(summarize_single_deletions(deletion_rows), family_rows, plane_summary)
    write_bifurcation_log(deletion_rows, family_rows, plane_summary)

    print("\nObserved internal hierarchy inside Sigma_comm:")
    print("  Sigma_field -> Sigma_L")
    print("  Sigma_comm is the primary object; its global ideal/equations remain open.")
    print("  The canonical tangent model is handled by tangent_commutator_map.py.")
    print("  A(w)-spectrum is defined on the full weight space.")
    print(f"  Wrote table snapshot: {BIFURCATION_LOG_PATH}")
    print("\n[snapshot OK: Sigma_comm is the primary CQ domain; A(w) is global]")


if __name__ == "__main__":
    main()
