"""Paper IV support script: exact explicit nine-point collision census.

Status: exact finite-point verification.

This script starts from the independent rational set P_9 and verifies the
collision geometry used in Paper IV:

  - 36 sector pairs split as 2 parallel, 10 interior, 15 endpoint, 9 exterior;
  - every interior collision is visible as a layer-count drop;
  - alpha=2/3 is the unique interior parameter with maximal collapse;
  - the six exact weighted classes are the L_{2/3} quotient;
  - endpoint quotient classes and open-chamber branch orders on [0,1].

The script intentionally works from the exact rational table, not from the
228-dimensional matrices. It does not prove that this table is the exact Rubik
joint spectrum. The separate numerical registration is
experiments/paper4/rubik_joint_spectrum_registration.py.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

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

CRITICALS = [
    Fraction(0, 1),
    Fraction(2, 7),
    Fraction(2, 5),
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(4, 5),
    Fraction(1, 1),
]

EXPECTED_CHAMBER_ORDERS = [
    ["S1", "S2", "S4", "S5", "S8", "S3", "S6", "S7", "S9"],
    ["S1", "S2", "S4", "S5", "S3", "S8", "S6", "S7", "S9"],
    ["S1", "S2", "S4", "S3", "S5", "S6", "S8", "S7", "S9"],
    ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"],
    ["S1", "S2", "S3", "S4", "S7", "S6", "S5", "S9", "S8"],
    ["S1", "S2", "S3", "S7", "S4", "S6", "S5", "S9", "S8"],
]


def branch_value(point: tuple[str, int, Fraction, Fraction], alpha: Fraction) -> Fraction:
    _, _, q, h = point
    return alpha * q + (1 - alpha) * h


def pair_collision(
    left: tuple[str, int, Fraction, Fraction],
    right: tuple[str, int, Fraction, Fraction],
) -> tuple[str, Fraction | None]:
    _, _, q_i, h_i = left
    _, _, q_j, h_j = right
    denominator = (q_i - h_i) - (q_j - h_j)
    if denominator == 0:
        return "parallel", None
    alpha = (h_j - h_i) / denominator
    if 0 < alpha < 1:
        return "interior", alpha
    if alpha == 0 or alpha == 1:
        return "endpoint", alpha
    return "exterior", alpha


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


def quotient_classes(alpha: Fraction) -> list[list[str]]:
    by_value: dict[Fraction, list[str]] = defaultdict(list)
    for point in POINTS:
        by_value[branch_value(point, alpha)].append(point[0])
    return sorted(
        (labels for labels in by_value.values() if len(labels) > 1),
        key=lambda labels: int(labels[0][1:]),
    )


def pair_multiplicity(classes: list[list[str]]) -> int:
    return sum(len(labels) * (len(labels) - 1) // 2 for labels in classes)


def main() -> None:
    labels = [point[0] for point in POINTS]
    by_alpha: dict[Fraction, list[tuple[str, str]]] = defaultdict(list)
    counts = {key: 0 for key in EXPECTED_COUNTS}
    parallel = []
    certificate = []

    for i, left in enumerate(POINTS):
        label_i = left[0]
        for right in POINTS[i + 1 :]:
            label_j = right[0]
            classification, alpha = pair_collision(left, right)
            counts[classification] += 1
            certificate.append((label_i, label_j, alpha, classification))
            if classification == "parallel":
                parallel.append((label_i, label_j))
                continue

            assert alpha is not None
            by_alpha[alpha].append((label_i, label_j))

    interior = {alpha: by_alpha[alpha] for alpha in by_alpha if 0 < alpha < 1}

    print("=" * 72)
    print("Paper IV: Exact Explicit Nine-Point Collision Census")
    print("=" * 72)
    print("Pair classification:")
    for key in ["parallel", "interior", "endpoint", "exterior"]:
        print(f"  {key}: {counts[key]}")
    assert counts == EXPECTED_COUNTS
    assert interior == EXPECTED_INTERIOR
    assert parallel == [("S1", "S9"), ("S2", "S6")]
    print()

    print("Complete 36-pair certificate:")
    for classification in ["parallel", "interior", "endpoint", "exterior"]:
        print(f"  [{classification}]")
        for left, right, alpha, pair_class in certificate:
            if pair_class == classification:
                alpha_text = "--" if alpha is None else str(alpha)
                print(f"    {left}-{right}: alpha={alpha_text}")
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

    print("Critical quotient classes on [0,1]:")
    for alpha in CRITICALS:
        classes = quotient_classes(alpha)
        values = {branch_value(point, alpha) for point in POINTS}
        drop = len(POINTS) - len(values)
        multiplicity = pair_multiplicity(classes)
        print(
            f"  alpha={alpha}: layers={len(values)}, drop={drop}, "
            f"pair_multiplicity={multiplicity}, classes={classes}"
        )
    assert quotient_classes(Fraction(0)) == [
        ["S1", "S2", "S4", "S5", "S8"],
        ["S3", "S6"],
        ["S7", "S9"],
    ]
    assert quotient_classes(Fraction(1)) == [
        ["S2", "S3"], ["S4", "S6"], ["S5", "S9"]
    ]
    assert pair_multiplicity(quotient_classes(Fraction(2, 3))) == 4
    print()

    print("Open-chamber branch orders (descending):")
    chamber_orders = []
    for left, right in zip(CRITICALS, CRITICALS[1:]):
        sample = (left + right) / 2
        order = [
            point[0]
            for point in sorted(
                POINTS,
                key=lambda point: (branch_value(point, sample), point[0]),
                reverse=True,
            )
        ]
        chamber_orders.append(order)
        assert len({branch_value(point, sample) for point in POINTS}) == 9
        print(f"  ({left},{right}): {' > '.join(order)}")
    assert chamber_orders == EXPECTED_CHAMBER_ORDERS
    print()

    layer_map: dict[Fraction, list[str]] = defaultdict(list)
    dim_map: dict[Fraction, int] = defaultdict(int)
    for point in POINTS:
        label, dim, _, _ = point
        value = branch_value(point, Fraction(2, 3))
        layer_map[value].append(label)
        dim_map[value] += dim

    print("Exact P_9 weighted quotient at alpha=2/3:")
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

    print("\n[snapshot OK: exact explicit arrangement census on [0,1]]")


if __name__ == "__main__":
    main()
