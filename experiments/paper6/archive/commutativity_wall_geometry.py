"""Paper VI support script: local geometry of Sigma_comm.

Status: exploratory computational evidence only.

This script studies the commutator map near the canonical full-generator point.
It does not compute the ideal or variety decomposition of Sigma_comm. It records
local numerical patterns that guide that algebraic task:

1. local scaling of ||[QT(w), HT(w)]|| under small perturbations;
2. symmetry directions that remain in Sigma_comm to numerical precision;
3. rank and singular-value patterns of the commutator matrix.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

import numpy as np

if __package__ in (None, ""):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    sys.path.insert(0, SCRIPT_DIR)
    sys.path.insert(0, REPO_ROOT)

from phase_utils import commutator_matrix, move_label, numerical_rank, prim_data  # noqa: E402


np.random.seed(42)

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
)
LOG_PATH = os.path.join(OUT_DIR, "_paper6_commutativity_wall_geometry.txt")

TOL_ZERO = 1e-10
EPS_VALUES = [1e-4, 1e-3, 1e-2, 1e-1]


def log(msg: str) -> None:
    print(msg, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def normalized_direction(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm <= 1e-15:
        return v.copy()
    return v / norm


def direction_norms(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    direction: np.ndarray,
) -> list[float]:
    base = np.ones(len(keys))
    values = []
    for eps in EPS_VALUES:
        weights = base + eps * normalized_direction(direction)
        comm = commutator_matrix(keys, rhos, weights)
        values.append(float(np.linalg.norm(comm, ord="fro")))
    return values


def log_slope(values: list[float]) -> float:
    xs = np.log(np.array(EPS_VALUES, dtype=float))
    ys = np.log(np.maximum(np.array(values, dtype=float), 1e-300))
    return float(np.polyfit(xs, ys, 1)[0])


def direction_for_index(n: int, idx: int) -> np.ndarray:
    v = np.zeros(n)
    v[idx] = -1.0
    return v


def axis_symmetric_directions(keys: list[tuple[int, int, int]]) -> list[tuple[str, np.ndarray]]:
    out = []
    for axis in range(3):
        qt = np.array([1.0 if key[0] == axis and key[2] != 2 else 0.0 for key in keys])
        ht = np.array([1.0 if key[0] == axis and key[2] == 2 else 0.0 for key in keys])
        out.append((f"axis-{axis} QT symmetric", -qt))
        out.append((f"axis-{axis} HT symmetric", -ht))
    return out


def turn_class_directions(keys: list[tuple[int, int, int]]) -> list[tuple[str, np.ndarray]]:
    qt = np.array([1.0 if key[2] != 2 else 0.0 for key in keys])
    ht = np.array([1.0 if key[2] == 2 else 0.0 for key in keys])
    return [
        ("all QT symmetric", -qt),
        ("all HT symmetric", -ht),
    ]


def rank_signature(mat: np.ndarray) -> dict:
    s = np.linalg.svd(mat, compute_uv=False)
    rank = numerical_rank(mat, tol=1e-10)
    nonzero = s[s > 1e-10 * max(s[0], 1.0)] if len(s) else np.array([])
    return {
        "rank": rank,
        "top_sv": float(s[0]) if len(s) else 0.0,
        "min_nonzero_sv": float(nonzero[-1]) if len(nonzero) else 0.0,
        "tail_sv": float(s[rank]) if rank < len(s) else 0.0,
    }


def summarize_direction(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    name: str,
    direction: np.ndarray,
) -> dict:
    values = direction_norms(keys, rhos, direction)
    weights = np.ones(len(keys)) + EPS_VALUES[-1] * normalized_direction(direction)
    sig = rank_signature(commutator_matrix(keys, rhos, weights))
    return {
        "name": name,
        "norms": values,
        "slope": log_slope(values),
        **sig,
    }


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("")

    keys, rhos = prim_data()
    n = len(keys)
    assert n == 18

    log("=" * 72)
    log("Paper VI: Commutativity Wall Geometry")
    log("=" * 72)
    log("Status: local numerical evidence, not an algebraic characterization.")

    base_comm = commutator_matrix(keys, rhos, np.ones(n))
    base_norm = float(np.linalg.norm(base_comm, ord="fro"))
    log(f"\nCanonical point ||C_comm(1)||_F = {base_norm:.3e}")
    assert base_norm < TOL_ZERO

    log("\nSingle-coordinate deletion directions near w=1:")
    deletion_rows = []
    for idx, key in enumerate(keys):
        row = summarize_direction(keys, rhos, f"-{move_label(key)}", direction_for_index(n, idx))
        deletion_rows.append(row)
        log(
            f"  {row['name']:>4s}: slope={row['slope']:.2f}, "
            f"norm(eps=1e-2)={row['norms'][2]:.3e}, rank={row['rank']}, "
            f"top_sv={row['top_sv']:.3e}"
        )

    rank_counts = Counter(row["rank"] for row in deletion_rows)
    slope_range = (min(row["slope"] for row in deletion_rows), max(row["slope"] for row in deletion_rows))
    log(f"  rank counts: {dict(sorted(rank_counts.items()))}")
    log(f"  slope range: [{slope_range[0]:.2f}, {slope_range[1]:.2f}]")
    assert dict(sorted(rank_counts.items())) == {88: 6, 96: 12}
    assert 0.99 < slope_range[0] < 1.01 and 0.99 < slope_range[1] < 1.01

    log("\nSymmetry-preserving directions near w=1:")
    symmetry_rows = []
    for name, direction in turn_class_directions(keys) + axis_symmetric_directions(keys):
        row = summarize_direction(keys, rhos, name, direction)
        symmetry_rows.append(row)
        status = "inside Sigma_comm" if row["norms"][-1] < TOL_ZERO else "leaves Sigma_comm"
        log(
            f"  {name:<24s}: {status:<18s} "
            f"norm(eps=1e-1)={row['norms'][-1]:.3e}, rank={row['rank']}"
        )

    inside = [row["name"] for row in symmetry_rows if row["norms"][-1] < TOL_ZERO]
    log(f"  symmetry directions inside Sigma_comm: {inside}")
    assert inside == [
        "all QT symmetric",
        "all HT symmetric",
        "axis-0 QT symmetric",
        "axis-1 QT symmetric",
        "axis-2 QT symmetric",
    ]
    assert all(row["rank"] == 52 for row in symmetry_rows if row["name"].endswith("HT symmetric") and row["name"].startswith("axis"))

    log("\nAsymptotic local pattern:")
    log("  generic one-coordinate perturbations leave Sigma_comm linearly")
    log("  selected symmetric turn-class directions remain in Sigma_comm")
    log("  commutator ranks distinguish QT and HT deletion directions")
    log("\n[snapshot OK: commutativity-wall local geometry recorded]")


if __name__ == "__main__":
    main()
