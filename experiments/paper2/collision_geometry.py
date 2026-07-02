"""Collision geometry of the QT/HT joint spectrum for Paper II.

Starting from the nine exact joint-spectrum points (q_i, h_i), each sector
defines an affine branch

    lambda_i(alpha) = alpha q_i + (1-alpha) h_i.

This experiment computes all C(9,2)=36 pairwise branch intersections by exact
Fraction arithmetic. It verifies:

  - 2 parallel pairs, 10 interior crossings, 15 endpoint crossings, 9 exterior
    crossings;
  - every interior crossing is visible as a layer-count drop;
  - alpha=2/3 is the unique interior parameter with maximal collapse.
"""

from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction

from rime.cubie import CubieMove
from rime.cubieoperator import CubieSpectralOperator


EXPECTED_COUNTS = {
    "parallel": 2,
    "interior": 10,
    "endpoint": 15,
    "exterior": 9,
}

EXPECTED_INTERIOR = {
    Fraction(2, 7): [("S3", "S8")],
    Fraction(2, 5): [("S3", "S5"), ("S6", "S8")],
    Fraction(1, 2): [("S3", "S4"), ("S7", "S8")],
    Fraction(2, 3): [
        ("S5", "S6"),
        ("S5", "S7"),
        ("S6", "S7"),
        ("S8", "S9"),
    ],
    Fraction(4, 5): [("S4", "S7")],
}

EXPECTED_LAYER_COUNTS = {
    Fraction(0, 1): 3,
    Fraction(2, 7): 8,
    Fraction(2, 5): 7,
    Fraction(1, 2): 7,
    Fraction(2, 3): 6,
    Fraction(4, 5): 8,
    Fraction(1, 1): 6,
}


def rat(x: float, max_denominator: int = 18) -> Fraction:
    return Fraction(float(x)).limit_denominator(max_denominator)


def branch_value(point: tuple[Fraction, Fraction], alpha: Fraction) -> Fraction:
    q, h = point
    return alpha * q + (1 - alpha) * h


def components(vertices: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    seen: set[str] = set()
    out: list[list[str]] = []
    for start in vertices:
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        out.append(sorted(comp, key=lambda s: int(s[1:])))
    return [c for c in out if len(c) > 1]


def main() -> None:
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    sec = op.center_decomposition()

    labels = [f"S{i}" for i in range(1, sec["n_sectors"] + 1)]
    points = [
        (rat(s["lam_QT"], 6), rat(s["lam_HT"], 6))
        for s in sec["sectors"]
    ]
    assert len(points) == 9
    assert len(set(points)) == 9

    by_alpha: dict[Fraction, list[tuple[str, str]]] = defaultdict(list)
    counts = {k: 0 for k in EXPECTED_COUNTS}
    parallel_pairs: list[tuple[str, str]] = []

    for i in range(len(points)):
        q_i, h_i = points[i]
        slope_i = q_i - h_i
        for j in range(i + 1, len(points)):
            q_j, h_j = points[j]
            slope_j = q_j - h_j
            denominator = slope_i - slope_j

            if denominator == 0:
                counts["parallel"] += 1
                parallel_pairs.append((labels[i], labels[j]))
                continue

            alpha = (h_j - h_i) / denominator
            by_alpha[alpha].append((labels[i], labels[j]))

            if 0 < alpha < 1:
                counts["interior"] += 1
            elif alpha == 0 or alpha == 1:
                counts["endpoint"] += 1
            else:
                counts["exterior"] += 1

    print("=" * 72)
    print("Paper II: QT/HT Collision Geometry")
    print("=" * 72)
    print("\nPair classification:")
    for name in ["parallel", "interior", "endpoint", "exterior"]:
        print(f"  {name:<9}: {counts[name]}")
    assert counts == EXPECTED_COUNTS

    interior = {a: by_alpha[a] for a in by_alpha if 0 < a < 1}
    assert interior == EXPECTED_INTERIOR

    print("\nInterior critical alpha values:")
    max_collapse = -1
    max_alphas: list[Fraction] = []
    for alpha in sorted(interior):
        values = [branch_value(point, alpha) for point in points]
        layer_count = len(set(values))
        collapse = 9 - layer_count
        comps = components(labels, interior[alpha])

        assert EXPECTED_LAYER_COUNTS[alpha] == layer_count
        assert collapse > 0

        if collapse > max_collapse:
            max_collapse = collapse
            max_alphas = [alpha]
        elif collapse == max_collapse:
            max_alphas.append(alpha)

        pair_text = ", ".join(f"{u}-{v}" for u, v in interior[alpha])
        comp_text = ", ".join("+".join(c) for c in comps)
        print(
            f"  alpha={str(alpha):>3}: layers={layer_count}, "
            f"collapse={collapse}, pairs={pair_text}, components={comp_text}"
        )

    assert max_alphas == [Fraction(2, 3)]
    assert max_collapse == 3

    print("\nEndpoint checks:")
    for alpha in [Fraction(0, 1), Fraction(1, 1)]:
        values = [branch_value(point, alpha) for point in points]
        layer_count = len(set(values))
        print(f"  alpha={alpha}: layers={layer_count}")
        assert EXPECTED_LAYER_COUNTS[alpha] == layer_count

    print("\nParallel pairs:")
    for u, v in parallel_pairs:
        print(f"  {u} || {v}")
    assert parallel_pairs == [("S1", "S9"), ("S2", "S6")]

    # No shadow collisions: every interior alpha creates fewer than 9 layers.
    for alpha in interior:
        assert len({branch_value(point, alpha) for point in points}) < 9

    print("\nDone: no shadow collisions; alpha=2/3 is uniquely maximal.")


if __name__ == "__main__":
    main()
