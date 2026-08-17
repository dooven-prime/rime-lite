"""Focused assert-based tests for the incidence-profile demo."""
from fractions import Fraction

import numpy as np

from incidence_profiles import (
    Qsqrt5,
    axis_balanced_families,
    axis_conjugacy_certificate,
    canonical_family,
    cube_rotations,
    lagrange_projector_certificate,
    named_family,
    rotate_family,
    sector_alignment,
)
from exact_canonical_carriers import (
    audited_pair_matmul,
    conservative_pair_matmul_bound,
    pair_preserves_block_decomposition,
)
from exact_n8_spectrum import pair_matmul_preoperation_bound


assert len(cube_rotations()) == 24

drop0 = named_family("drop_axis0_ht")
drop2 = named_family("drop_axis2_ht")
certificate = axis_conjugacy_certificate(drop0, drop2)
assert certificate["verified"]
assert canonical_family(drop0) == canonical_family(drop2)

for rotation in cube_rotations():
    assert canonical_family(rotate_family(drop0, rotation)) == canonical_family(drop0)

family_index = axis_balanced_families()
canonical_keys = [tuple(tuple(key) for key in row["generator_keys"]) for row in family_index]
assert len(canonical_keys) == len(set(canonical_keys))
assert all(row["operator_count"] > 0 for row in family_index)

sqrt5_values = [
    Qsqrt5(Fraction(0)),
    Qsqrt5(Fraction(1, 2)),
    Qsqrt5(Fraction(5, 8), Fraction(1, 8)),
]
projectors = lagrange_projector_certificate(sqrt5_values)
assert projectors["verified_interpolation_identity"]

identity = np.eye(3)
coarse = {"sector_bases": [identity[:, :2], identity[:, 2:]]}
fine = {"sector_bases": [identity[:, :1], identity[:, 1:2], identity[:, 2:]]}
alignment = sector_alignment(coarse, fine)
assert alignment["relation"] == "target_refines_reference"
reverse = sector_alignment(fine, coarse)
assert reverse["relation"] == "reference_refines_target"

whole = {"sector_bases": [identity]}
tied = sector_alignment(fine, whole)
assert tied["maximizing_reference_sectors_for_target"] == [[0, 1, 2]]
assert tied["target_in_reference_containment"][0]["minimizing_reference_sectors"] == [0, 1, 2]

# Sector reduction alone does not admit the carrier-forced theorem. Here the
# diagonal carrier supports are empty while cross-carrier operator blocks make
# the routed product nonzero.
blocks_2d = {"left": (0, 1), "right": (1, 2)}
zero = np.zeros((2, 2), dtype=np.int64)
x = np.array([[0, 1], [0, 0]], dtype=np.int64)
y = np.array([[0, 0], [1, 0]], dtype=np.int64)
p0 = np.diag([1, 0]).astype(np.int64)
p1 = np.diag([0, 1]).astype(np.int64)
a = p0 @ x @ p1
b = p1 @ y @ p0
assert not pair_preserves_block_decomposition((x, zero), blocks_2d)
assert not pair_preserves_block_decomposition((y, zero), blocks_2d)
assert not np.any(np.diag(a)) and not np.any(np.diag(b))
assert np.array_equal(a @ b, p0)

safe_left = (np.full((2, 3), 4, dtype=np.int64), np.full((2, 3), 2, dtype=np.int64))
safe_right = (np.full((3, 2), 5, dtype=np.int64), np.full((3, 2), 3, dtype=np.int64))
assert conservative_pair_matmul_bound(safe_left, safe_right) == 84
assert pair_matmul_preoperation_bound(safe_left, safe_right) == 84

unsafe_left = (np.array([[2**62]], dtype=np.int64), np.zeros((1, 1), dtype=np.int64))
unsafe_right = (np.array([[3]], dtype=np.int64), np.zeros((1, 1), dtype=np.int64))
try:
    audited_pair_matmul(unsafe_left, unsafe_right, [], "expected-overflow")
except OverflowError:
    pass
else:
    raise AssertionError("unsafe int64 multiplication was not rejected before execution")

print(f"incidence profile tests passed; {len(family_index)} axis-balanced rotation orbits")
