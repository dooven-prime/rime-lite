"""Finite-representation adapters for the carrier accessibility engine."""

from __future__ import annotations

from itertools import permutations

import numpy as np

from .engine import CarrierAccessibility


def z2_double_regular_engine() -> CarrierAccessibility:
    """Build a 4-dimensional regular-plus-regular Z2 control model.

    The three sectors are A-only, A+B hybrid, and B-only. The support graph
    has an A--hybrid--B path, while every routed product between the pure
    endpoints vanishes because the representation preserves A and B.
    """
    identity = np.eye(4, dtype=np.complex128)
    swap = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    generator = np.block([[swap, np.zeros((2, 2))], [np.zeros((2, 2)), swap]])
    sectors = []
    for coordinates in ((0,), (1, 2), (3,)):
        projector = np.zeros((4, 4), dtype=np.complex128)
        for coordinate in coordinates:
            projector[coordinate, coordinate] = 1
        sectors.append(projector)
    carriers = [
        np.diag([1, 1, 0, 0]).astype(np.complex128),
        np.diag([0, 0, 1, 1]).astype(np.complex128),
    ]
    return CarrierAccessibility([identity, generator], sectors, carriers)


def rubik_engine(*, max_depth_tolerance: float = 1e-10) -> CarrierAccessibility:
    """Build the canonical 228-dimensional Rubik realization."""
    from rime.cubie import BLOCK_RANGES, CubieMove, TOTAL_DIM
    from rime.cubieoperator import CubieSpectralOperator

    operator = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    sectors = operator.center_decomposition()["projectors"]
    transports = list(operator.rho_matrices())
    carriers = []
    for start, end in BLOCK_RANGES.values():
        carrier = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.complex128)
        carrier[start:end, start:end] = np.eye(end - start)
        carriers.append(carrier)
    return CarrierAccessibility(
        transports,
        sectors,
        carriers,
        tolerance=max_depth_tolerance,
        support_tolerance=0.05,
    )


def s3_natural_regular_engine() -> CarrierAccessibility:
    """Build a 9-dimensional S3 natural-plus-regular finite model.

    The two summands are declared as separate physical carriers. Sectors are
    coordinate projectors, so this adapter is a small control model for the
    carrier theorem rather than a claim about a canonical S3 sectorization.
    """
    perms = list(permutations(range(3)))
    index = {p: i for i, p in enumerate(perms)}
    natural = []
    regular = []
    for permutation in perms:
        matrix = np.zeros((3, 3), dtype=np.complex128)
        for j, image in enumerate(permutation):
            matrix[image, j] = 1
        natural.append(matrix)
        reg = np.zeros((6, 6), dtype=np.complex128)
        for j, word in enumerate(perms):
            product_perm = tuple(permutation[word[k]] for k in range(3))
            reg[index[product_perm], j] = 1
        regular.append(reg)
    transports = [
        np.block([[a, np.zeros((3, 6))], [np.zeros((6, 3)), b]])
        for a, b in zip(natural, regular)
    ]
    # Deliberately group coordinates across the two invariant carriers. This
    # creates an A-only endpoint, an A+B hybrid intermediate, and B-only
    # endpoints, which is the smallest useful control for the theorem.
    sector_coordinates = [
        (0, 2),          # A-only: natural coordinates 0 and 2
        (1, 3),          # hybrid: natural coordinate 1 and regular coordinate 0
        (4, 5),          # B-only: regular coordinates 1 and 2
        (6,),
        (7,),
        (8,),
    ]
    sectors = []
    for coordinates in sector_coordinates:
        q = np.zeros((9, 9), dtype=np.complex128)
        for coordinate in coordinates:
            q[coordinate, coordinate] = 1
        sectors.append(q)
    carriers = []
    for start, end in ((0, 3), (3, 9)):
        p = np.zeros((9, 9), dtype=np.complex128)
        p[start:end, start:end] = np.eye(end - start)
        carriers.append(p)
    return CarrierAccessibility(transports, sectors, carriers)
