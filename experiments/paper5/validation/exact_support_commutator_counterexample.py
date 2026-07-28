"""Paper V exact certificate: Boolean support does not determine R2 or D.

Status: exact integer-matrix verification.

The two labelled skew-Hermitian systems have the same generator-indexed direct
support. In the first system the generators are proportional, so the 3 -> 1
channel is absent from the full Lie algebra. In the second system the same
direct support produces a nonzero commutator block on that channel.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import numpy as np


X = np.array(
    [
        [0, 1, 0],
        [-1, 0, 1],
        [0, -1, 0],
    ],
    dtype=np.int64,
)
Y0 = 2 * X
Y1 = np.array(
    [
        [0, 2, 0],
        [-2, 0, 3],
        [0, -3, 0],
    ],
    dtype=np.int64,
)


def direct_support(generators: tuple[np.ndarray, ...]) -> np.ndarray:
    """Return generator-indexed entry support for one-dimensional sectors."""
    return np.stack([generator != 0 for generator in generators])


def main() -> None:
    system0 = (X, Y0)
    system1 = (X, Y1)
    support0 = direct_support(system0)
    support1 = direct_support(system1)
    comm0 = X @ Y0 - Y0 @ X
    comm1 = X @ Y1 - Y1 @ X

    expected_comm1 = np.array(
        [
            [0, 0, 1],
            [0, 0, 0],
            [-1, 0, 0],
        ],
        dtype=np.int64,
    )

    assert np.array_equal(X.T, -X)
    assert np.array_equal(Y0.T, -Y0)
    assert np.array_equal(Y1.T, -Y1)
    assert np.array_equal(support0, support1)
    assert X[0, 2] == Y0[0, 2] == Y1[0, 2] == 0
    assert np.array_equal(comm0, np.zeros((3, 3), dtype=np.int64))
    assert np.array_equal(comm1, expected_comm1)

    left0 = X[0, 1] * Y0[1, 2]
    right0 = Y0[0, 1] * X[1, 2]
    left1 = X[0, 1] * Y1[1, 2]
    right1 = Y1[0, 1] * X[1, 2]
    assert left0 == right0 == 2
    assert left1 == 3 and right1 == 2

    print("=" * 72)
    print("Paper V: Exact Same-Support Commutator Counterexample")
    print("=" * 72)
    print("Generator-indexed R1 tensors are identical: yes")
    print(f"System 0 associative terms on 3 -> 1: {left0} and {right0}")
    print(f"System 0 commutator block: {comm0[0, 2]}")
    print(f"System 1 associative terms on 3 -> 1: {left1} and {right1}")
    print(f"System 1 commutator block: {comm1[0, 2]}")
    print("System 0 exact Lie algebra: span{X}; channel 3 -> 1 absent")
    print("System 1 exact first channel depth: 1")
    print("\n[exact certificate OK: same R1, different R2 and D]")


if __name__ == "__main__":
    main()
