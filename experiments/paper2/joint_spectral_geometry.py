"""QT/HT joint spectral geometry for Paper II.

This experiment verifies the structural reframing used in Paper II v2:

    QT_all, HT_all commute
      -> 9 QT/HT joint-spectral sectors
      -> A_18 = (2 QT_all + HT_all) / 3 is a collision quotient

The script is intentionally assert-first. It records exact rational sector
signatures and checks that the six A_18 layers are obtained by projecting the
nine (q, h) joint-spectrum points through L_{2/3}(q,h) = (2q+h)/3.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction

import numpy as np

from rime.cubie import CubieMove, TOTAL_DIM
from rime.cubieoperator import CubieSpectralOperator


np.random.seed(42)
TOL = 1e-8


def rat(x: float, max_denominator: int = 18) -> Fraction:
    return Fraction(float(x)).limit_denominator(max_denominator)


def main() -> None:
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    ops, _ = op.build_per_axis_ops()
    qt = ops["QT_all"]
    ht = ops["HT_all"]
    a18 = ops["A_18"]

    print("=" * 72)
    print("Paper II: QT/HT Joint Spectral Geometry")
    print("=" * 72)

    comm_qh = np.linalg.norm(qt @ ht - ht @ qt, "fro")
    recon = np.linalg.norm(a18 - ((2 * qt + ht) / 3), "fro")
    print(f"[QT_all, HT_all] Frobenius norm: {comm_qh:.3e}")
    print(f"||A_18 - (2 QT_all + HT_all)/3||_F: {recon:.3e}")
    assert comm_qh < TOL
    assert recon < TOL

    sec = op.center_decomposition()
    sectors = sec["sectors"]
    projectors = sec["projectors"]
    assert sec["n_sectors"] == 9
    assert len(projectors) == 9

    expected = [
        (20, Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)),
        (2, Fraction(5, 6), Fraction(1, 1), Fraction(8, 9)),
        (39, Fraction(5, 6), Fraction(2, 3), Fraction(7, 9)),
        (26, Fraction(1, 2), Fraction(1, 1), Fraction(2, 3)),
        (1, Fraction(1, 3), Fraction(1, 1), Fraction(5, 9)),
        (39, Fraction(1, 2), Fraction(2, 3), Fraction(5, 9)),
        (66, Fraction(2, 3), Fraction(1, 3), Fraction(5, 9)),
        (8, Fraction(0, 1), Fraction(1, 1), Fraction(1, 3)),
        (27, Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
    ]

    print("\nSector signatures:")
    print("  sector  dim   q       h       slope=q-h  A18=(2q+h)/3")
    print("  " + "-" * 62)

    points: list[tuple[Fraction, Fraction]] = []
    layer_map: dict[Fraction, list[int]] = defaultdict(list)
    total_dim = 0

    for idx, (sector, exp) in enumerate(zip(sectors, expected), start=1):
        dim = int(sector["dim"])
        q = rat(sector["lam_QT"], 6)
        h = rat(sector["lam_HT"], 6)
        a = rat(sector["lam_18"], 9)
        projected = (2 * q + h) / 3
        slope = q - h

        assert (dim, q, h, a) == exp, (idx, dim, q, h, a, exp)
        assert projected == a

        points.append((q, h))
        layer_map[a].append(idx)
        total_dim += dim

        print(
            f"  S{idx:<2}    {dim:>3}   {str(q):>5}   {str(h):>5}"
            f"   {str(slope):>8}   {str(a):>8}"
        )

    assert len(set(points)) == 9
    assert total_dim == TOTAL_DIM
    assert len(layer_map) == 6

    print("\nCollision quotient at alpha=2/3:")
    for layer in sorted(layer_map, reverse=True):
        members = layer_map[layer]
        dim = sum(sectors[i - 1]["dim"] for i in members)
        print(f"  A18={str(layer):>4s}: {members} (dim={dim})")

    assert layer_map[Fraction(5, 9)] == [5, 6, 7]
    assert sum(sectors[i - 1]["dim"] for i in [5, 6, 7]) == 106
    assert layer_map[Fraction(1, 3)] == [8, 9]
    assert sum(sectors[i - 1]["dim"] for i in [8, 9]) == 35

    projector_sum = sum(projectors)
    completeness = np.linalg.norm(projector_sum - np.eye(TOTAL_DIM), "fro")
    max_overlap = max(
        np.linalg.norm(projectors[i] @ projectors[j], "fro")
        for i in range(9)
        for j in range(i + 1, 9)
    )
    print(f"\nProjector completeness: {completeness:.3e}")
    print(f"Max off-sector overlap: {max_overlap:.3e}")
    assert completeness < TOL
    assert max_overlap < TOL

    print("\nDone: 9-point QT/HT joint spectrum verified.")


if __name__ == "__main__":
    main()
