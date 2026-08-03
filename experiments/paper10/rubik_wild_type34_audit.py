"""Paper X audit: typed cancellation and incidence counts in Rubik sectors.

Scope:
    Counts commutator cancellations and routed image--kernel incidences in the
    canonical Rubik QT/HT sectorization. This is not a synthetic construction:
    the sectors are the nine QT/HT joint sectors and the registered Lie family
    consists of the anti-Hermitian parts of the 18 face-turn matrices.

Claim status:
    - Computational Certificate for the declared finite Lie-family audit.
    - The routed incidence count is bridge-level evidence, not a global
      accessibility or completion theorem.

The filename is retained for source-path compatibility with Registry v1. The
active result keys and reader-facing output use typed v2 vocabulary.
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

    commutator_cancellations = 0
    routed_image_kernel_incidences = 0

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
                        routed_image_kernel_incidences += 1
                    else:
                        commutator_cancellations += 1

    return {
        "n_sectors": n_sectors,
        "n_generators": n_generators,
        "commutator_cancellation_count": commutator_cancellations,
        "routed_image_kernel_incidence_count": routed_image_kernel_incidences,
    }


def main() -> None:
    result = audit()
    print("=" * 72)
    print("  Paper X: Rubik Typed Cancellation / Incidence Audit")
    print("=" * 72)
    print(f"Rubik QT/HT sectors: {result['n_sectors']}")
    print(f"Rubik generators:    {result['n_generators']}")
    print(
        "Commutator cancellations:             "
        f"{result['commutator_cancellation_count']}"
    )
    print(
        "Routed image-kernel incidences:        "
        f"{result['routed_image_kernel_incidence_count']}"
    )
    print()
    print("Claim status: Computational Certificate for the declared family.")
    print("Boundary: incidence is counted at the routed bridge-product level;")
    print("it is not a global accessibility or completion theorem.")
    print("Done.")


if __name__ == "__main__":
    main()
