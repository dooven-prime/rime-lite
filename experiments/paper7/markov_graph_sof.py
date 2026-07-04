"""Markov and graph SOF diagnostics.

These examples test whether the R1/R2/D audit interface applies outside
Rubik/group and quantum-gate examples. They are diagnostics, not theorem
support for generic completion.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import logm

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402


TOL = 1e-6
MAX_DEPTH = 4


def state_sector_bases(n: int) -> list[np.ndarray]:
    eye = np.eye(n, dtype=complex)
    return [eye[:, [i]] for i in range(n)]


def normalize(X: np.ndarray) -> np.ndarray:
    nrm = np.linalg.norm(X, "fro")
    return X / nrm if nrm > 1e-12 else X


def markov_sos(P: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    """Build a Markov SOF from a transition matrix."""
    n = P.shape[0]
    Vs = state_sector_bases(n)
    try:
        Q = logm(P)
    except Exception:
        Q = P - np.eye(n)
    X = normalize((Q - Q.conj().T) / 2.0)
    return Vs, [X], ["skew-log(P)"]


def graph_sos(A: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    """Build a graph SOF from adjacency and Laplacian-derived operators."""
    n = A.shape[0]
    Vs = state_sector_bases(n)
    degree = np.diag(np.sum(A, axis=1))
    L = degree - A

    Xs = [
        normalize((A - A.T) / 2.0),
        normalize(1j * L),
    ]
    return Vs, Xs, ["skew(A)", "iL"]


def audit(name: str, species: str, sectors: str, Vs, Xs, labels) -> dict:
    engine = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=MAX_DEPTH)
    summary = engine.audit()
    return {
        "name": name,
        "species": species,
        "sectors": sectors,
        "labels": labels,
        **summary,
    }


def print_table(rows: list[dict]) -> None:
    print("=" * 100)
    print("  Markov + Graph SOF Diagnostics")
    print("=" * 100)
    print("  Counts are off-diagonal sector pairs only.")
    print("  D_max=999 means unreached within the tested max depth.")
    print()

    header = (
        f"  {'System':<24s} {'species':<8s} {'sec':>3s} {'gen':>3s} "
        f"{'R1off':>6s} {'R2off':>6s} {'frzR1':>5s} {'frzD':>5s} "
        f"{'D-rep':>5s} {'Dmax':>4s} {'per_depth':>18s}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in rows:
        print(
            f"  {r['name']:<24s} {r['species']:<8s} {r['n_sec']:>3d} {r['n_gen']:>3d} "
            f"{r['R1_pct']:>5.1f}% {r['R2_pct']:>5.1f}% "
            f"{r['frozen_R1']:>5d} {r['frozen_D']:>5d} {r['D_repaired']:>5d} "
            f"{r['D_max']:>4d} {str(r['per_depth_sizes']):>18s}"
        )


def main() -> None:
    systems = []

    P_chain = np.array(
        [
            [0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
        ],
        dtype=float,
    )
    systems.append(("Markov chain", "Markov", "state basis", *markov_sos(P_chain)))

    P_absorb = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.3, 0.4, 0.3],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    systems.append(("Absorbing Markov", "Markov", "state basis", *markov_sos(P_absorb)))

    A_K3 = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
    systems.append(("Graph K3", "Graph", "vertex basis", *graph_sos(A_K3)))

    A_P3 = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    systems.append(("Graph P3", "Graph", "vertex basis", *graph_sos(A_P3)))

    A_C4 = np.array(
        [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]],
        dtype=float,
    )
    systems.append(("Graph C4", "Graph", "vertex basis", *graph_sos(A_C4)))

    rows = [audit(name, species, sectors, Vs, Xs, labels) for name, species, sectors, Vs, Xs, labels in systems]
    print_table(rows)

    print()
    print("  Interpretation:")
    print("  1. Markov and graph systems fit the SOF audit interface.")
    print("  2. Complete or strongly connected examples can have D=0 without D-repair.")
    print("  3. Sparse graph examples may remain D-frozen with this generator choice.")
    print("  4. These diagnostics test portability, not generic completion.")
    print("\nDone.")


if __name__ == "__main__":
    main()
