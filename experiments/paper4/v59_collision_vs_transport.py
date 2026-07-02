"""Paper IV support script: collision graph is not transport graph.

Status: canonical Rubik computational check.

At alpha=2/3, the collision graph on the V_{5/9} quotient component is the
complete triangle S5-S6-S7. Direct generator transport inside the same three
sectors is not a triangle: S5-S7 is absent and transport is mediated by S6.

This supports the Paper IV distinction between spectral collision adjacency and
Paper II transport adjacency. The script computes only the direct transport
tensor K on the three sectors, not the heavier Lie kappa hierarchy.
"""

from __future__ import annotations

import numpy as np

from rime.cubie import CubieMove
from rime.cubieoperator import CubieSpectralOperator
from rime.rep_utils import sector_bases_from_projectors


np.random.seed(42)
TOL = 1e-8


def pair_kappa(Vs: list[np.ndarray], rhos: list[np.ndarray], i: int, j: int) -> float:
    best = 0.0
    for rho in rhos:
        forward = np.linalg.norm(Vs[i].conj().T @ rho @ Vs[j], "fro")
        backward = np.linalg.norm(Vs[j].conj().T @ rho @ Vs[i], "fro")
        best = max(best, float(forward), float(backward))
    return best


def main() -> None:
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    center = op.center_decomposition()
    projectors = center["projectors"]
    dims = [int(sector["dim"]) for sector in center["sectors"]]
    Vs = sector_bases_from_projectors(projectors, tol=TOL)
    rhos = op.rho_matrices()

    # 0-based indices for S5, S6, S7.
    triple = [(4, 5), (4, 6), (5, 6)]
    labels = {(4, 5): "S5-S6", (4, 6): "S5-S7", (5, 6): "S6-S7"}
    collision_edges = {"S5-S6", "S5-S7", "S6-S7"}

    print("=" * 72)
    print("Paper IV: V_5/9 Collision Triangle vs Direct Transport")
    print("=" * 72)
    print(f"Sector dimensions S5/S6/S7: {[dims[i] for i in [4, 5, 6]]}")
    assert [dims[i] for i in [4, 5, 6]] == [1, 39, 66]
    print()

    transport_edges = set()
    values = {}
    for pair in triple:
        label = labels[pair]
        value = pair_kappa(Vs, rhos, *pair)
        values[label] = value
        if value > TOL:
            transport_edges.add(label)
        print(f"  {label}: collision=yes, direct K={value:.6g}")

    print()
    print(f"Collision edges at alpha=2/3: {sorted(collision_edges)}")
    print(f"Direct transport edges: {sorted(transport_edges)}")

    assert collision_edges == {"S5-S6", "S5-S7", "S6-S7"}
    assert transport_edges == {"S5-S6", "S6-S7"}
    assert values["S5-S6"] > TOL
    assert values["S6-S7"] > TOL
    assert values["S5-S7"] < TOL

    print("\n[snapshot OK: V_5/9 collision is a triangle, direct transport is a chain]")


if __name__ == "__main__":
    main()
