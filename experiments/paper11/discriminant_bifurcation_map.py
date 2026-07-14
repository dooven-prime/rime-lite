"""Paper XI audit: 2D discriminant and bifurcation slice.

Claim status:
    - Auxiliary wall-taxonomy diagnostic for Paper XI.
    - Consistency check for the high codimension of the Rubik commutativity
      locus on arbitrary two-dimensional generator-weight slices.
    - Not a full discriminant map and not a proof of
      Sigma_access subset Sigma_spec subset Sigma_comm.

The script scans a small 2D plane of QT generator weights.  It records:
    - commutative cells where [QT(w), HT(w)] is numerically zero;
    - spectral point counts only on those commutative cells;

The default grid is intentionally small.  Accessibility-wall mapping is not
computed here; that requires a separate optimized audit on normal spectral
charts.
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


BETA = 0.314159
TOL_COMM = 1e-8


def qt_ht_indices(n_gens: int) -> tuple[list[int], list[int]]:
    qt_idx = [idx for idx in range(n_gens) if idx % 3 != 2]
    ht_idx = [idx for idx in range(n_gens) if idx % 3 == 2]
    return qt_idx, ht_idx


def spectral_point_count(evals: np.ndarray, tol: float = 1e-6) -> int:
    ordered = sorted((float(x) for x in evals), reverse=True)
    n_points = 1
    current = ordered[0]
    for value in ordered[1:]:
        if abs(value - current) > tol:
            n_points += 1
            current = value
    return n_points


def weighted_qt_ht(
    rhos: list[np.ndarray],
    weights: np.ndarray,
    qt_idx: list[int],
    ht_idx: list[int],
) -> tuple[np.ndarray, np.ndarray]:
    QT = sum(weights[idx] * rhos[idx] for idx in qt_idx) / sum(weights[idx] for idx in qt_idx)
    HT = sum(weights[idx] * rhos[idx] for idx in ht_idx) / sum(weights[idx] for idx in ht_idx)
    return QT, HT


def run(grid: int) -> dict:
    op = CubieSpectralOperator()
    rhos = [np.asarray(rho, dtype=complex) for rho in op.rho_matrices()]
    qt_idx, ht_idx = qt_ht_indices(len(rhos))
    g1, g2 = qt_idx[0], qt_idx[1]

    alphas = np.linspace(0.02, 1.0, grid)
    comm_map = np.zeros((grid, grid), dtype=bool)
    spec_map = np.zeros((grid, grid), dtype=int)

    for i, a1 in enumerate(alphas):
        for j, a2 in enumerate(alphas):
            weights = np.ones(len(rhos))
            weights[g1] = a1
            weights[g2] = a2
            QT, HT = weighted_qt_ht(rhos, weights, qt_idx, ht_idx)

            comm_norm = np.linalg.norm(QT @ HT - HT @ QT, "fro")
            comm_map[i, j] = comm_norm < TOL_COMM
            if comm_map[i, j]:
                M = QT + BETA * HT
                M = (M + M.conj().T) / 2.0
                spec_map[i, j] = spectral_point_count(np.linalg.eigvalsh(M))
            else:
                spec_map[i, j] = -1

    spec_values = sorted({int(x) for x in spec_map[comm_map] if x > 0})
    bifurcations = 0
    for i in range(1, grid):
        for j in range(grid):
            if comm_map[i, j] and comm_map[i - 1, j] and spec_map[i, j] != spec_map[i - 1, j]:
                bifurcations += 1
    for i in range(grid):
        for j in range(1, grid):
            if comm_map[i, j] and comm_map[i, j - 1] and spec_map[i, j] != spec_map[i, j - 1]:
                bifurcations += 1

    n_comm = int(np.sum(comm_map))
    return {
        "grid": grid,
        "g1": g1,
        "g2": g2,
        "n_comm": n_comm,
        "n_total": grid * grid,
        "spec_values": spec_values,
        "bifurcations": bifurcations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small Paper XI 2D discriminant slice.")
    parser.add_argument("--grid", type=int, default=8, help="number of samples per axis")
    args = parser.parse_args()

    result = run(args.grid)
    print("=" * 72)
    print("  Paper XI: 2D Discriminant and Bifurcation Slice")
    print("=" * 72)
    print(f"Grid: {result['grid']}x{result['grid']}")
    print(f"Varying QT generator indices: {result['g1']} and {result['g2']}")
    print()
    print(f"Commutative cells: {result['n_comm']}/{result['n_total']}")
    print(f"Spectral point counts on commutative cells: {result['spec_values']}")
    print(f"Spectral point-count bifurcations inside commutative cells: {result['bifurcations']}")
    print("Accessibility-wall cells: not computed by this script")
    print()
    print("Interpretation:")
    print("  - arbitrary 2D generator-weight slices see Sigma_comm sparsely;")
    print("  - spectral diagnostics are only interpreted on commutative cells;")
    print("  - accessibility-wall mapping is deferred to a separate optimized audit;")
    print("  - this is boundary evidence for Paper XI, not a full discriminant map.")
    print("Done.")


if __name__ == "__main__":
    main()
