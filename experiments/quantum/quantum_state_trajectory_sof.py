"""Magic-sensitive state-trajectory SOF control for T-gate detection.

Circuit outputs are coarse-grained into STAB and MAGIC state classes. These
classes are not orthogonal linear subspaces of the qubit Hilbert space. The
result is therefore a trajectory-induced two-state Markov realization, not a
strict projector sectorization of C^2.

The control demonstrates report relativity: a computational-basis gate-log
probe is T-blind, while a magic-sensitive trajectory probe converts the same
phase resource into complete off-diagonal support in a two-state audit.
"""

from __future__ import annotations

import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import (  # noqa: E402
    AccessibilityEngine,
    compute_direct_support,
    compute_word_depth_matrix,
    offdiag_count,
)


TOL = 1e-8
MAX_DEPTH = 4
FROZEN = 999
N_CIRCUITS = 500
GATES_PER_CIRCUIT = 4
STAB_TOL = 0.999
SEED = 42

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.diag([1, 1j]).astype(complex)
T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)

PROBE_STAB = np.array([1, 1], dtype=complex) / np.sqrt(2)
PROBE_MAGIC = T @ PROBE_STAB
STAB = 0
MAGIC = 1


def is_stabilizer(state: np.ndarray) -> bool:
    return any(
        abs(np.vdot(state, pauli @ state)) > STAB_TOL
        for pauli in (SX, SY, SZ)
    )


def random_circuit(
    rng: np.random.RandomState,
    second_gate: np.ndarray,
) -> np.ndarray:
    unitary = I2.copy()
    for _ in range(GATES_PER_CIRCUIT):
        gate = H if rng.randint(0, 2) == 0 else second_gate
        unitary = gate @ unitary
    return unitary


def transition_matrix(second_gate: np.ndarray, seed: int = SEED) -> np.ndarray:
    rng = np.random.RandomState(seed)
    counts = np.zeros((2, 2), dtype=float)
    for source, probe in ((STAB, PROBE_STAB), (MAGIC, PROBE_MAGIC)):
        for _ in range(N_CIRCUITS):
            final = random_circuit(rng, second_gate) @ probe
            target = STAB if is_stabilizer(final) else MAGIC
            counts[target, source] += 1.0
    return counts / counts.sum(axis=0, keepdims=True)


def skew(matrix: np.ndarray) -> np.ndarray:
    return ((matrix - matrix.T) / 2.0).astype(complex)


def audit(matrix: np.ndarray) -> dict[str, object]:
    sectors = [np.eye(2, dtype=complex)[:, [index]] for index in range(2)]
    observable = skew(matrix)
    engine = AccessibilityEngine(
        sectors,
        [observable],
        tol=TOL,
        max_depth=MAX_DEPTH,
    )
    frozen = engine.frozen_pairs()
    r1 = compute_direct_support(sectors, [observable], tol=TOL)
    depth = compute_word_depth_matrix(
        sectors,
        [observable],
        max_depth=MAX_DEPTH,
        tol=TOL,
        frozen=FROZEN,
    )
    frozen_word = sum(
        1
        for i in range(2)
        for j in range(2)
        if i != j and depth[i, j] == FROZEN
    )
    return {
        "R1": r1,
        "R1_offdiag": offdiag_count(r1),
        "frozen_R1": frozen["frozen_R1"],
        "frozen_D_word": frozen_word,
        "skew_offdiag": float(np.real(observable[MAGIC, STAB])),
    }


def main() -> None:
    clifford_transition = transition_matrix(S)
    universal_transition = transition_matrix(T)
    clifford = audit(clifford_transition)
    universal = audit(universal_transition)

    assert np.allclose(clifford_transition, np.eye(2))
    assert clifford["R1_offdiag"] == 0
    assert universal["R1_offdiag"] == 2
    assert clifford["frozen_R1"] == 2
    assert universal["frozen_R1"] == 0

    print("Quantum state-trajectory T-gate control")
    print("  coarse states: STAB, MAGIC")
    print("  status: trajectory-induced Markov realization, not strict C^2 sectors")
    print()
    print("  Clifford {H,S} transition matrix:")
    print(clifford_transition)
    print("  Universal {H,T} transition matrix:")
    print(universal_transition)
    print()
    print(
        "  skew off-diagonal: "
        f"{clifford['skew_offdiag']:.3f} -> {universal['skew_offdiag']:.3f}"
    )
    print(
        "  R1_offdiag: "
        f"{clifford['R1_offdiag']} -> {universal['R1_offdiag']}"
    )
    print(
        "  frozen_R1: "
        f"{clifford['frozen_R1']} -> {universal['frozen_R1']}"
    )
    print(
        "  frozen_D_word: "
        f"{clifford['frozen_D_word']} -> {universal['frozen_D_word']}"
    )
    print()
    print("  signal: absent -> complete off-diagonal support in the two-state audit")
    print("  claim_status: diagnostic")


if __name__ == "__main__":
    main()
