"""Appendix-level stability controls for Paper XIII.

M1-M3 are executable validations. Coarse/fine pushforward remains an explicit
open problem and is not reported as PASS.
"""

from __future__ import annotations

import numpy as np

from rime.accessibility import (
    AccessibilityEngine,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
)


TOL = 1e-8
FROZEN = 999
MAX_DEPTH = 4


def one_hot_sectors(dim: int) -> list[np.ndarray]:
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [index]] for index in range(dim)]


def skew(matrix: np.ndarray) -> np.ndarray:
    return ((matrix - matrix.conj().T) / 2.0).astype(complex)


def structural_shadow(
    sectors: list[np.ndarray], observables: list[np.ndarray], tol: float = TOL
) -> dict[str, np.ndarray]:
    engine = AccessibilityEngine(
        sectors,
        observables,
        tol=tol,
        max_depth=MAX_DEPTH,
        require_skew_hermitian=True,
    )
    r1_tensor, r2_lie_tensor, _ = engine.support()
    d_lie, _ = engine.depth()
    return {
        "R1": np.any(r1_tensor, axis=0),
        "R2_word": compute_length_two_support(sectors, observables, tol=tol),
        "R2_lie": np.any(r2_lie_tensor, axis=0),
        "D_word": compute_word_depth_matrix(
            sectors, observables, max_depth=MAX_DEPTH, tol=tol, frozen=FROZEN
        ),
        "D_lie": d_lie,
    }


def check_permutation_equivariance(seed: int = 13) -> bool:
    rng = np.random.default_rng(seed)
    dim = 5
    sectors = one_hot_sectors(dim)
    observables = [skew(rng.normal(size=(dim, dim))) for _ in range(3)]
    reference = structural_shadow(sectors, observables)

    permutation = np.array([2, 4, 0, 3, 1])
    permuted_observables = [
        observable[np.ix_(permutation, permutation)] for observable in observables
    ]
    permuted = structural_shadow(sectors, permuted_observables)

    return all(
        np.array_equal(permuted[name], reference[name][np.ix_(permutation, permutation)])
        for name in reference
    )


def check_rescaling_with_margin() -> bool:
    sectors = one_hot_sectors(4)
    observable = np.zeros((4, 4), dtype=complex)
    observable[1, 0], observable[0, 1] = 0.5, -0.5
    observable[2, 1], observable[1, 2] = 0.2, -0.2
    observable[3, 2], observable[2, 3] = 0.1, -0.1

    reference = structural_shadow(sectors, [observable])
    scaled_up = structural_shadow(sectors, [10.0 * observable])
    scaled_down = structural_shadow(sectors, [0.5 * observable])
    return all(
        np.array_equal(reference[name], scaled_up[name])
        and np.array_equal(reference[name], scaled_down[name])
        for name in reference
    )


def check_threshold_transitions() -> bool:
    sectors = one_hot_sectors(4)
    observable = np.zeros((4, 4), dtype=complex)
    observable[1, 0], observable[0, 1] = 0.5, -0.5
    observable[2, 1], observable[1, 2] = 5e-4, -5e-4
    observable[3, 2], observable[2, 3] = 5e-6, -5e-6
    observable[3, 0], observable[0, 3] = 5e-8, -5e-8

    tolerances = (1e-10, 5e-9, 1e-7, 5e-6, 1e-5, 5e-4, 1e-3)
    counts = [
        int(np.count_nonzero(compute_direct_support(sectors, [observable], tol=tol)))
        for tol in tolerances
    ]
    changes = sum(left != right for left, right in zip(counts, counts[1:]))
    monotone = all(left >= right for left, right in zip(counts, counts[1:]))
    return changes == 3 and monotone


def run_checks() -> dict[str, bool | str]:
    return {
        "matrix_permutation_equivariance": check_permutation_equivariance(),
        "conditional_rescaling_stability": check_rescaling_with_margin(),
        "threshold_transition_control": check_threshold_transitions(),
        "coarse_fine_pushforward": "OPEN",
    }


def main() -> None:
    checks = run_checks()
    print("Paper XIII appendix stability controls")
    for name, status in checks.items():
        label = status if isinstance(status, str) else ("PASS" if status else "FAIL")
        print(f"  {name}: {label}")
    failed = [name for name, status in checks.items() if status is False]
    if failed:
        raise SystemExit(f"failed controls: {failed}")


if __name__ == "__main__":
    main()
