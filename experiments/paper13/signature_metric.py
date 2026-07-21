"""Fixed-fiber structural pseudometric for Paper XIII.

The comparison is defined only after sector/observable alignment, normalization,
threshold, and depth semantics are fixed. It applies to the structural
sub-signature, not to directional constraint, response, or wall coordinates.
Inputs are aligned structural representations, not unaligned SOF Reports.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np


MATRIX_CHANNELS = ("R1", "R2_word", "R2_lie", "D_word")
FROZEN_CHANNELS = ("frozen_R1", "frozen_D_word", "frozen_D_lie")
STRUCTURAL_CHANNELS = MATRIX_CHANNELS + FROZEN_CHANNELS


def _validate_signature(signature: Mapping[str, object]) -> int:
    missing = [name for name in STRUCTURAL_CHANNELS if name not in signature]
    if missing:
        raise ValueError(f"missing structural channels: {missing}")

    shape: tuple[int, int] | None = None
    for name in MATRIX_CHANNELS:
        matrix = np.asarray(signature[name])
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"{name} must be a square matrix")
        if shape is None:
            shape = matrix.shape
        elif matrix.shape != shape:
            raise ValueError("all structural matrices must share one aligned shape")

    for name in FROZEN_CHANNELS:
        value = signature[name]
        if not isinstance(value, (int, np.integer)) or int(value) < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    assert shape is not None
    return shape[0]


def _validate_fixed_fiber(
    left: Mapping[str, object], right: Mapping[str, object]
) -> int:
    n_left = _validate_signature(left)
    n_right = _validate_signature(right)
    if n_left != n_right:
        raise ValueError("signatures lie in different aligned sector fibers")
    return n_left


def structural_pseudometric(
    left: Mapping[str, object],
    right: Mapping[str, object],
    weights: Mapping[str, float] | None = None,
) -> float:
    """Return the weighted structural mismatch on one fixed alignment fiber.

    Matrix channels use off-diagonal entrywise Hamming distance. Frozen-count
    coordinates use the discrete metric: zero when equal and one otherwise.
    Non-negative weights yield a pseudometric; strictly positive weights yield
    a metric on structural signatures modulo ignored diagonal entries. The
    caller must have transported both signatures into the same declared
    (Phi, Theta) coordinates; equal shape is necessary but does not prove that
    scientific alignment condition.
    """

    n = _validate_fixed_fiber(left, right)
    channel_weights = {name: 1.0 for name in STRUCTURAL_CHANNELS}
    if weights is not None:
        unknown = set(weights) - set(STRUCTURAL_CHANNELS)
        if unknown:
            raise ValueError(f"unknown structural weights: {sorted(unknown)}")
        channel_weights.update({name: float(value) for name, value in weights.items()})
    if any(value < 0 for value in channel_weights.values()):
        raise ValueError("pseudometric weights must be non-negative")

    offdiag = ~np.eye(n, dtype=bool)
    distance = 0.0
    for name in MATRIX_CHANNELS:
        lhs = np.asarray(left[name])
        rhs = np.asarray(right[name])
        distance += channel_weights[name] * float(np.count_nonzero((lhs != rhs) & offdiag))
    for name in FROZEN_CHANNELS:
        distance += channel_weights[name] * float(left[name] != right[name])
    return distance


def _random_signature(rng: np.random.Generator, n: int) -> dict[str, object]:
    signature: dict[str, object] = {}
    for name in MATRIX_CHANNELS:
        if name == "D_word":
            matrix = rng.integers(0, 5, size=(n, n))
        else:
            matrix = rng.integers(0, 2, size=(n, n), dtype=np.int8)
        np.fill_diagonal(matrix, 0)
        signature[name] = matrix
    for name in FROZEN_CHANNELS:
        signature[name] = int(rng.integers(0, n * (n - 1) + 1))
    return signature


def run_checks(seed: int = 13, trials: int = 100) -> dict[str, bool]:
    rng = np.random.default_rng(seed)
    triangle = True
    symmetry = True
    nonnegative = True
    for _ in range(trials):
        n = int(rng.integers(2, 7))
        a = _random_signature(rng, n)
        b = _random_signature(rng, n)
        c = _random_signature(rng, n)
        d_ab = structural_pseudometric(a, b)
        d_ba = structural_pseudometric(b, a)
        d_ac = structural_pseudometric(a, c)
        d_bc = structural_pseudometric(b, c)
        nonnegative &= d_ab >= 0
        symmetry &= d_ab == d_ba
        triangle &= d_ac <= d_ab + d_bc

    a = _random_signature(rng, 4)
    b = {name: np.array(value, copy=True) if name in MATRIX_CHANNELS else value
         for name, value in a.items()}
    b["R2_lie"][0, 1] = 1 - b["R2_lie"][0, 1]
    positive_identity = structural_pseudometric(a, b) > 0
    zero_weight_pseudometric = structural_pseudometric(
        a, b, weights={"R2_lie": 0.0}
    ) == 0

    return {
        "nonnegative": bool(nonnegative),
        "symmetric": bool(symmetry),
        "triangle": bool(triangle),
        "positive_weight_identity": bool(positive_identity),
        "zero_weight_pseudometric": bool(zero_weight_pseudometric),
    }


def main() -> None:
    checks = run_checks()
    print("Paper XIII fixed-fiber structural pseudometric")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    print("Boundary: the full eight-dimensional audit signature is not claimed metric.")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
