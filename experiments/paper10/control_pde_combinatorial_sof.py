"""Paper X registry probe: control, PDE, and combinatorial SOF species.

Scope:
    This script adds three finite operator species to the SOF Registry.
    They are portability diagnostics, not standalone theorem sources.

    1. Control: a Kalman chain.  Sectorization comes from the controllability
       flag increments span(B), span(AB), span(A^2B).
    2. PDE: a finite-difference Laplacian.  Sectorization comes from a
       subdomain/interface mesh partition.
    3. Combinatorial: a graph coloring instance.  Sectorization comes from
       color classes.

Claim status:
    - Registry evidence for capability-aware strict admission.
    - These examples use positive-word support and depth; no Lie/Hall carrier
      or commutator-repair claim is registered.
    - They show that SOF requires compatible sectorization, not a fixed
      representation-theoretic origin for sectors.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rime.accessibility import (
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
    offdiag_count,
)
from rime.rep_utils import basis_from_indices, orthonormal_columns

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOL = 1e-10


def audit_control() -> dict:
    # A is a three-step controllability chain and B injects into the first node.
    a = np.array(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]],
        dtype=float,
    )
    b = np.array([[1.0], [0.0], [0.0]], dtype=float)
    b_op = b @ b.T

    flag0 = b
    flag1 = np.column_stack([b, a @ b])
    flag2 = np.column_stack([b, a @ b, a @ a @ b])
    ranks = [int(np.linalg.matrix_rank(flag)) for flag in (flag0, flag1, flag2)]

    # Use orthogonal increments of the Kalman flag as sector bases.
    vs = [
        orthonormal_columns(b),
        orthonormal_columns(a @ b),
        orthonormal_columns(a @ a @ b),
    ]
    xs = [a, b_op]

    r1 = compute_direct_support(vs, xs, tol=TOL)
    r2_word = compute_length_two_support(vs, xs, tol=TOL)
    d_word = compute_word_depth_matrix(vs, xs, max_depth=3, tol=TOL)

    return {
        "species": "control",
        "kalman_ranks": ranks,
        "controllable": ranks[-1] == 3,
        "r1_edges": offdiag_count(r1),
        "r2_word_edges": offdiag_count(r2_word),
        "D_0_to_2": int(d_word[2, 0]),
        "D_matrix": d_word,
    }


def audit_pde() -> dict:
    n = 7
    lap = (
        np.diag(2.0 * np.ones(n))
        - np.diag(np.ones(n - 1), 1)
        - np.diag(np.ones(n - 1), -1)
    )

    # Disjoint subdomain/interface partition of the mesh.
    vs = [
        basis_from_indices(n, [0, 1]),
        basis_from_indices(n, [2]),
        basis_from_indices(n, [3, 4, 5, 6]),
    ]
    xs = [lap]

    r1 = compute_direct_support(vs, xs, tol=TOL)
    r2_word = compute_length_two_support(vs, xs, tol=TOL)
    d_word = compute_word_depth_matrix(vs, xs, max_depth=4, tol=TOL)

    return {
        "species": "pde",
        "n_grid": n,
        "sector_dims": [v.shape[1] for v in vs],
        "r1_edges": offdiag_count(r1),
        "r2_word_edges": offdiag_count(r2_word),
        "D_left_to_right": int(d_word[2, 0]),
        "D_matrix": d_word,
    }


def audit_combinatorial() -> dict:
    adj = np.array(
        [[0, 1, 0, 0, 0, 0],
         [1, 0, 1, 1, 0, 0],
         [0, 1, 0, 1, 0, 0],
         [0, 1, 1, 0, 1, 0],
         [0, 0, 0, 1, 0, 1],
         [0, 0, 0, 0, 1, 0]],
        dtype=float,
    )
    coloring = np.array([0, 1, 0, 1, 2, 2])
    vs = [basis_from_indices(6, np.where(coloring == c)[0].tolist()) for c in range(3)]
    xs = [adj]

    r1 = compute_direct_support(vs, xs, tol=TOL)
    d_word = compute_word_depth_matrix(vs, xs, max_depth=3, tol=TOL)

    same_color_conflicts = 0
    for c, v in enumerate(vs):
        block = v.T @ adj @ v
        same_color_conflicts += int(np.real(np.sum(block)) // 2)

    return {
        "species": "combinatorial",
        "coloring": coloring.tolist(),
        "sector_dims": [v.shape[1] for v in vs],
        "inter_color_edges": offdiag_count(r1),
        "same_color_conflicts": same_color_conflicts,
        "D_matrix": d_word,
    }


def audit() -> dict:
    return {
        "control": audit_control(),
        "pde": audit_pde(),
        "combinatorial": audit_combinatorial(),
    }


def main() -> None:
    result = audit()

    print("=" * 72)
    print("  Paper X Registry Probe: Control / PDE / Combinatorial SOFs")
    print("=" * 72)
    print("Claim status: typed portability diagnostics for strict SOF admission.")
    print("Boundary: positive-word findings only; no Lie/Hall carrier is declared.")
    print()

    control = result["control"]
    print("1. Control SOF: Kalman chain")
    print(f"  Kalman ranks: {control['kalman_ranks']}")
    print(f"  controllable: {control['controllable']}")
    print(f"  R1 direct edges: {control['r1_edges']}")
    print(f"  W_2 aggregate word-support edges: {control['r2_word_edges']}")
    print(f"  first word-depth from input sector to terminal sector: {control['D_0_to_2']}")
    print()

    pde = result["pde"]
    print("2. PDE SOF: finite-difference Laplacian")
    print(f"  grid size: {pde['n_grid']}")
    print(f"  sector dims left/interface/right: {pde['sector_dims']}")
    print(f"  R1 direct edges: {pde['r1_edges']}")
    print(f"  W_2 aggregate word-support edges: {pde['r2_word_edges']}")
    print(f"  first word-depth left -> right: {pde['D_left_to_right']}")
    print()

    comb = result["combinatorial"]
    print("3. Combinatorial SOF: graph coloring")
    print(f"  coloring: {comb['coloring']}")
    print(f"  sector dims: {comb['sector_dims']}")
    print(f"  inter-color R1 edges: {comb['inter_color_edges']}")
    print(f"  same-color conflicts: {comb['same_color_conflicts']}")
    print()

    print("Conclusion:")
    print("  Control, PDE, and combinatorial examples use different sector origins.")
    print("  Each enters through the same capability-aware interface.")
    print("  Only its declared operator/word findings are reported.")
    print("Done.")


if __name__ == "__main__":
    main()
