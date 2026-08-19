"""Refinement, cross-cut partitions, and common-refinement controls.

A one-way report pushforward is canonical when a fine partition refines a
coarse partition. Cross-cut partitions have no such map in either direction.
Their intersection partition supplies a common comparison space, but lifting
coarse report data to that refinement requires source-level observables or an
additional disintegration rule.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPER13 = ROOT / "experiments" / "paper13"
STRUCTURAL = ROOT / "experiments" / "exploratory" / "structural_functionals" / "sof_coarse_graining"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PAPER13))
sys.path.insert(0, str(STRUCTURAL))

from bridge_energy import bridge_energy, pushforward_energy  # noqa: E402
from gridworld_reference_sof import GridWorld, build_observables  # noqa: E402
from rime.accessibility import compute_direct_support, offdiag_count  # noqa: E402


Partition = list[frozenset[int]]


def singleton_partition(size: int) -> Partition:
    return [frozenset({i}) for i in range(size)]


def row_partition(side: int) -> Partition:
    return [frozenset(range(r * side, (r + 1) * side)) for r in range(side)]


def distance_partition(side: int, obstacle: tuple[int, int]) -> Partition:
    zones: dict[int, set[int]] = {0: set(), 1: set(), 2: set()}
    for r in range(side):
        for c in range(side):
            distance = abs(r - obstacle[0]) + abs(c - obstacle[1])
            zone = 0 if distance <= 1 else (1 if distance == 2 else 2)
            zones[zone].add(r * side + c)
    return [frozenset(zones[k]) for k in sorted(zones)]


def refinement_map(fine: Partition, coarse: Partition) -> list[int] | None:
    """Return phi when every fine block lies in exactly one coarse block."""

    mapping: list[int] = []
    for block in fine:
        containers = [j for j, target in enumerate(coarse) if block <= target]
        if len(containers) != 1:
            return None
        mapping.append(containers[0])
    return mapping


def common_refinement(left: Partition, right: Partition) -> Partition:
    """Return all nonempty intersections of two partitions."""

    return [
        frozenset(a & b)
        for a in left
        for b in right
        if a & b
    ]


def sector_bases(partition: Partition, ambient: int) -> list[np.ndarray]:
    eye = np.eye(ambient, dtype=complex)
    return [eye[:, sorted(block)] for block in partition]


def support_summary(sectors: Sequence[np.ndarray], observables: Sequence[np.ndarray]) -> tuple[int, int]:
    support = compute_direct_support(sectors, observables, tol=1e-12)
    direct = offdiag_count(support)
    pairs = len(sectors) * (len(sectors) - 1)
    return direct, pairs - direct


def run() -> None:
    side = 5
    ambient = side * side
    obstacle = (2, 2)
    system = GridWorld(obstacles=[obstacle])
    observables, _ = build_observables(system.action_matrices())

    cells = singleton_partition(ambient)
    rows = row_partition(side)
    distances = distance_partition(side, obstacle)

    phi_cells_rows = refinement_map(cells, rows)
    assert phi_cells_rows is not None
    assert refinement_map(rows, distances) is None
    assert refinement_map(distances, rows) is None

    refinement = common_refinement(rows, distances)
    assert len(refinement) == 12
    phi_ref_rows = refinement_map(refinement, rows)
    phi_ref_dist = refinement_map(refinement, distances)
    assert phi_ref_rows is not None and phi_ref_dist is not None

    metric = np.eye(len(observables), dtype=complex)
    E_refinement = bridge_energy(sector_bases(refinement, ambient), observables, metric)
    E_rows = bridge_energy(sector_bases(rows, ambient), observables, metric)
    E_dist = bridge_energy(sector_bases(distances, ambient), observables, metric)
    row_error = float(np.max(np.abs(pushforward_energy(E_refinement, phi_ref_rows) - E_rows)))
    dist_error = float(np.max(np.abs(pushforward_energy(E_refinement, phi_ref_dist) - E_dist)))
    assert row_error < 1e-10 and dist_error < 1e-10

    # A coarse energy does not determine a unique lift to a refinement.
    lift_a = np.array([1.0, 0.0])
    lift_b = np.array([0.5, 0.5])
    assert lift_a.sum() == lift_b.sum() and not np.array_equal(lift_a, lift_b)

    print("SOF cross-fiber structural controls")
    print(f"  cells -> rows phi exists:       {phi_cells_rows is not None}")
    print("  rows -> distance phi exists:    False")
    print("  distance -> rows phi exists:    False")
    print(f"  nonempty common-refinement sectors: {len(refinement)}")
    print(f"  refinement -> rows error:       {row_error:.3e}")
    print(f"  refinement -> distance error:   {dist_error:.3e}")
    for name, partition in (("rows", rows), ("distance", distances), ("refinement", refinement)):
        direct, frozen = support_summary(sector_bases(partition, ambient), observables)
        print(f"  {name:10s} R1={direct:3d}, frozen={frozen:3d}")
    print("Claim boundary: the common refinement uses source-level observables;")
    print("coarse report data alone has no canonical lift.")


if __name__ == "__main__":
    run()
