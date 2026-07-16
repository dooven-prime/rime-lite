"""T-blind negative control for computational-basis gate-log SOF probes.

The Clifford gate set {H, S, CNOT} and universal gate set {H, T, CNOT}
produce identical R1/R2/depth shadows in this realization. Both S and T are
diagonal in the computational basis, so their logarithmic generators add no
off-diagonal sector support.

Claim status: negative_control. This is realization-specific and is not a
statement that the T gate is physically or computationally irrelevant.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import logm

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    compute_direct_support,
    compute_length_two_support,
    compute_word_depth_matrix,
    offdiag_count,
)


TOL = 1e-6
MAX_DEPTH = 4
FROZEN = 999

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.diag([1, 1j]).astype(complex)
T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
CNOT = np.eye(4, dtype=complex)
CNOT[2:, 2:] = X


def basis_sectors() -> list[np.ndarray]:
    eye = np.eye(4, dtype=complex)
    return [eye[:, [index]] for index in range(4)]


def generator(unitary: np.ndarray) -> np.ndarray:
    value = logm(unitary)
    return (value - value.conj().T) / 2.0


def audit(gates: list[np.ndarray]) -> dict[str, object]:
    sectors = basis_sectors()
    observables = [generator(gate) for gate in gates]
    engine = AccessibilityEngine(
        sectors,
        observables,
        tol=TOL,
        max_depth=MAX_DEPTH,
    )
    frozen = engine.frozen_pairs()
    _, lie_support, _ = engine.support()
    r1 = compute_direct_support(sectors, observables, tol=TOL)
    r2_word = compute_length_two_support(sectors, observables, tol=TOL)
    depth_word = compute_word_depth_matrix(
        sectors,
        observables,
        max_depth=MAX_DEPTH,
        tol=TOL,
        frozen=FROZEN,
    )
    r2_lie = np.any(lie_support, axis=0)
    frozen_word = sum(
        1
        for i in range(4)
        for j in range(4)
        if i != j and depth_word[i, j] == FROZEN
    )
    return {
        "R1": r1,
        "R2_word": r2_word,
        "R2_lie": r2_lie,
        "D_word": depth_word,
        "R1_offdiag": offdiag_count(r1),
        "R2_word_offdiag": offdiag_count(r2_word),
        "R2_lie_offdiag": offdiag_count(r2_lie),
        "frozen_R1": frozen["frozen_R1"],
        "frozen_D_word": frozen_word,
    }


def main() -> None:
    clifford = audit([np.kron(H, I2), np.kron(S, I2), CNOT])
    universal = audit([np.kron(H, I2), np.kron(T, I2), CNOT])

    for field in ("R1", "R2_word", "R2_lie", "D_word"):
        assert np.array_equal(clifford[field], universal[field]), field

    t_response = compute_direct_support(
        basis_sectors(), [generator(np.kron(T, I2))], tol=TOL
    )
    s_response = compute_direct_support(
        basis_sectors(), [generator(np.kron(S, I2))], tol=TOL
    )
    assert offdiag_count(t_response) == 0
    assert offdiag_count(s_response) == 0

    print("Quantum gate-log T-blind control")
    print("  sectors: computational-basis projectors")
    print("  observables: skew-Hermitian gate logarithms")
    print()
    print("  diagnostic             Clifford    Universal")
    for key in (
        "R1_offdiag",
        "frozen_R1",
        "R2_word_offdiag",
        "R2_lie_offdiag",
        "frozen_D_word",
    ):
        print(f"  {key:<22s} {clifford[key]:>8d} {universal[key]:>12d}")
    print()
    print("  All support, bridge, and word-depth shadows are identical.")
    print("  T and S each contribute zero off-diagonal support in this basis.")
    print("  claim_status: negative_control")


if __name__ == "__main__":
    main()
