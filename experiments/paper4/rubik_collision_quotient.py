"""Paper IV support script: exact Rubik QT/HT collision quotient.

Status: exact finite-point verification.

This script starts from the nine rational QT/HT joint-spectral points and
verifies the collision geometry used in Paper IV:

  - 36 sector pairs split as 2 parallel, 10 interior, 15 endpoint, 9 exterior;
  - every interior collision is visible as a layer-count drop;
  - alpha=2/3 is the unique interior parameter with maximal collapse;
  - the canonical six A_18 layers are the L_{2/3} quotient.

The script intentionally works from the exact rational table, not from the
228-dimensional matrices. The matrix-derived verification of this table lives
in experiments/paper2/joint_spectral_geometry.py.
"""

from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction


POINTS = [
    ("S1", 20, Fraction(1, 1), Fraction(1, 1)),
    ("S2", 2, Fraction(5, 6), Fraction(1, 1)),
    ("S3", 39, Fraction(5, 6), Fraction(2, 3)),
    ("S4", 26, Fraction(1, 2), Fraction(1, 1)),
    ("S5", 1, Fraction(1, 3), Fraction(1, 1)),
    ("S6", 39, Fraction(1, 2), Fraction(2, 3)),
    ("S7", 66, Fraction(2, 3), Fraction(1, 3)),
    ("S8", 8, Fraction(0, 1), Fraction(1, 1)),
    ("S9", 27, Fraction(1, 3), Fraction(1, 3)),
]

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
    Fraction(2, 3): [("S5", "S6"), ("S5", "S7"), ("S6", "S7"), ("S8", "S9")],
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


def branch_value(point: tuple[str, int, Fraction, Fraction], alpha: Fraction) -> Fraction:
    _, _, q, h = point
    return alpha * q + (1 - alpha) * h


def components(labels: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    adj = {label: set() for label in labels}
    for left, right in edges:
        adj[left].add(right)
        adj[right].add(left)

    out = []
    seen = set()
    for start in labels:
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        comp = []
        while queue:
            current = queue.popleft()
            comp.append(current)
            for nxt in adj[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        if len(comp) > 1:
            out.append(sorted(comp, key=lambda label: int(label[1:])))
    return out


def main() -> None:
    labels = [point[0] for point in POINTS]
    by_alpha: dict[Fraction, list[tuple[str, str]]] = defaultdict(list)
    counts = {key: 0 for key in EXPECTED_COUNTS}
    parallel = []

    for i, left in enumerate(POINTS):
        label_i, _, q_i, h_i = left
        slope_i = q_i - h_i
        for right in POINTS[i + 1 :]:
            label_j, _, q_j, h_j = right
            slope_j = q_j - h_j
            denominator = slope_i - slope_j

            if denominator == 0:
                counts["parallel"] += 1
                parallel.append((label_i, label_j))
                continue

            alpha = (h_j - h_i) / denominator
            by_alpha[alpha].append((label_i, label_j))
            if 0 < alpha < 1:
                counts["interior"] += 1
            elif alpha == 0 or alpha == 1:
                counts["endpoint"] += 1
            else:
                counts["exterior"] += 1

    interior = {alpha: by_alpha[alpha] for alpha in by_alpha if 0 < alpha < 1}

    print("=" * 72)
    print("Paper IV: Exact Rubik Collision Quotient")
    print("=" * 72)
    print("Pair classification:")
    for key in ["parallel", "interior", "endpoint", "exterior"]:
        print(f"  {key}: {counts[key]}")
    assert counts == EXPECTED_COUNTS
    assert interior == EXPECTED_INTERIOR
    assert parallel == [("S1", "S9"), ("S2", "S6")]
    print()

    max_drop = -1
    max_alphas = []
    print("Interior critical values:")
    for alpha in sorted(interior):
        values = [branch_value(point, alpha) for point in POINTS]
        layer_count = len(set(values))
        drop = len(POINTS) - layer_count
        comps = components(labels, interior[alpha])
        print(
            f"  alpha={alpha}: layers={layer_count}, drop={drop}, "
            f"components={['+'.join(comp) for comp in comps]}"
        )
        assert EXPECTED_LAYER_COUNTS[alpha] == layer_count
        assert drop > 0
        if drop > max_drop:
            max_drop = drop
            max_alphas = [alpha]
        elif drop == max_drop:
            max_alphas.append(alpha)

    assert max_alphas == [Fraction(2, 3)]
    assert max_drop == 3
    print()

    layer_map: dict[Fraction, list[str]] = defaultdict(list)
    dim_map: dict[Fraction, int] = defaultdict(int)
    for point in POINTS:
        label, dim, _, _ = point
        value = branch_value(point, Fraction(2, 3))
        layer_map[value].append(label)
        dim_map[value] += dim

    print("Canonical quotient at alpha=2/3:")
    for value in sorted(layer_map, reverse=True):
        members = layer_map[value]
        print(f"  {value}: {members}, dim={dim_map[value]}")

    assert layer_map[Fraction(5, 9)] == ["S5", "S6", "S7"]
    assert dim_map[Fraction(5, 9)] == 106
    assert layer_map[Fraction(1, 3)] == ["S8", "S9"]
    assert dim_map[Fraction(1, 3)] == 35
    assert len(layer_map) == 6

    for alpha in [Fraction(0, 1), Fraction(1, 1)]:
        assert len({branch_value(point, alpha) for point in POINTS}) == EXPECTED_LAYER_COUNTS[alpha]

    print("\n[snapshot OK: no shadow collisions; alpha=2/3 uniquely maximal]")


if __name__ == "__main__":
    main()
