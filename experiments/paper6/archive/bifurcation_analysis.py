"""Paper VI support script: bifurcation table snapshot.

Status: computational observation only.

This retired script writes a legacy snapshot to an ignored internal ``data/``
directory. It is retained for provenance only. The active validation script
``../validation/generator_moduli_space.py`` writes the public review record to
``../results/_paper6_bifurcation_log.txt``.
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
LOG_PATH = os.path.join(OUT_DIR, "_paper6_bifurcation_log.txt")


def log(msg: str) -> None:
    print(msg, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("")

    keys, rhos = prim_data()
    assert len(keys) == 18

    deletion_rows = single_deletion_rows(keys, rhos)
    family_rows = selected_family_rows(keys, rhos)
    plane_summary = scan_axis0_ht_plane(keys, rhos, grid=11)
    single_summary = summarize_single_deletions(deletion_rows)

    log("=" * 72)
    log("Paper VI: Bifurcation Table Snapshot")
    log("=" * 72)
    log("This is an experimental support script, not a paper theorem source.")

    log("\nSingle-generator deletions:")
    for row in deletion_rows:
        log(
            f"  -{row['label']:>3s}: "
            f"CQ={row['cq_status']} "
            f"(comm={row['comm_norm']:.2e}), "
            f"A-layers={row['a_layers']}, A-field={row['a_field']}"
        )
    log(
        f"  [OK] {single_summary['cq_blocked']}/{single_summary['total']} deletions leave "
        "the QT/HT collision quotient blocked."
    )
    log(f"  A-layer counts: {single_summary['a_layer_counts']}")
    log(f"  A-field counts: {single_summary['a_field_counts']}")

    log("\nSelected families:")
    for row in family_rows:
        log(
            f"  {row['family']:<28s} "
            f"CQ={row['cq_status']:>7s} "
            f"CQ-layers={str(row['cq_layers']):>4s} CQ-field={row['cq_field']:<10s} "
            f"A-layers={row['a_layers']:>3d} A-field={row['a_field']}"
        )

    log("\n2D weight scan (axis-0 half-turn weights):")
    log(f"  Grid: {plane_summary['grid']} x {plane_summary['grid']}")
    log(f"  CQ commutative cells: {plane_summary['cq_commutative']}/{plane_summary['total']}")
    log(f"  CQ layer counts on commutative cells: {plane_summary['cq_layers']}")
    log(f"  A-spectrum layer counts: {plane_summary['a_layers']}")

    assert_stable_snapshot(single_summary, family_rows, plane_summary)

    log("\nObserved internal hierarchy inside Sigma_comm:")
    log("  Sigma_field -> Sigma_L")
    log("  Sigma_comm is the primary object; its global ideal/equations remain open.")
    log("  The canonical tangent model is handled by tangent_commutator_map.py.")
    log("  A(w)-spectrum is globally defined on the full weight space.")
    log("")
    log("[snapshot OK: Sigma_comm primary object and internal events recorded]")


if __name__ == "__main__":
    main()
