"""Paper X audit: wild Type III/IV mechanisms in Rubik QT/HT sectors.

Scope:
    Counts naturally occurring Type III cancellation and Type IV incidence
    mechanisms in the canonical Rubik QT/HT sectorization.  This is not a
    synthetic construction: the sectors are the nine QT/HT joint sectors and
    the generators are the 18 Rubik face-turn representation matrices.

Claim status:
    - Registry evidence for Paper X and Paper VII.
    - Confirms wild Type III and bridge-level Type IV incidence mechanisms in
      the Rubik QT/HT sectorization.
    - Type IV is counted at the bridge-product/incidence level; this should not
      be overstated as a completed global accessibility-obstruction theorem.
"""

from __future__ import annotations

import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import compute_R1, compute_R2  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


TOL = 1e-8


def audit() -> dict[str, int]:
    op = CubieSpectralOperator()
    Vs = op.center_decomposition()["sector_bases"]
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    Xs = [(rho - rho.conj().T) / 2 for rho in rhos]

    n_sectors = len(Vs)
    n_generators = len(Xs)
    R1 = compute_R1(Vs, Xs, tol=TOL)
    R2_arr, R2_pairs = compute_R2(Vs, Xs, tol=TOL)

    pair_to_cp: dict[tuple[int, int], int] = {}
    for cp, (g, h) in enumerate(R2_pairs):
        pair_to_cp[(g, h)] = cp
        pair_to_cp[(h, g)] = cp

    type_iii = 0
    type_iv = 0

    for i in range(n_sectors):
        for j in range(n_sectors):
            if i == j:
                continue
            for g in range(n_generators):
                for h in range(n_generators):
                    if g == h:
                        continue

                    has_bridge = any(R1[g, i, k] and R1[h, k, j] for k in range(n_sectors))
                    if not has_bridge:
                        continue

                    cp = pair_to_cp.get((g, h))
                    if cp is None or R2_arr[cp, i, j]:
                        continue

                    all_products_zero = True
                    for k in range(n_sectors):
                        if not (R1[g, i, k] and R1[h, k, j]):
                            continue
                        A = Vs[i].conj().T @ Xs[g] @ Vs[k]
                        B = Vs[k].conj().T @ Xs[h] @ Vs[j]
                        if np.linalg.norm(A @ B, "fro") > TOL:
                            all_products_zero = False
                            break

                    if all_products_zero:
                        type_iv += 1
                    else:
                        type_iii += 1

    return {
        "n_sectors": n_sectors,
        "n_generators": n_generators,
        "type_iii": type_iii,
        "type_iv": type_iv,
    }


def main() -> None:
    result = audit()
    print("=" * 72)
    print("  Paper X: Rubik Wild Type III/IV Audit")
    print("=" * 72)
    print(f"Rubik QT/HT sectors: {result['n_sectors']}")
    print(f"Rubik generators:    {result['n_generators']}")
    print(f"Wild Type III cancellation mechanisms:       {result['type_iii']}")
    print(f"Wild Type IV bridge-level incidence products: {result['type_iv']}")
    print()
    if result["type_iii"] > 0:
        print("  Wild Type III confirmed in Rubik QT/HT sectorization.")
    if result["type_iv"] > 0:
        print("  Wild Type IV incidence confirmed at bridge-product level.")
    print()
    print("Claim boundary: Type IV is bridge-level incidence evidence,")
    print("not a global accessibility-obstruction theorem by itself.")
    print("Done.")


if __name__ == "__main__":
    main()
