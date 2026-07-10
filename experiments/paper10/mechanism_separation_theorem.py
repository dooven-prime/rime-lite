"""Paper X constructive control: calibrated mechanism separation gives proxy-rate separation.

Scope:
    This script gives an explicit SOF-internal positive control for H3
    structured dynamics plus ordered response calibration.  It is not a
    universal theorem for all SOF
    deformations.  It constructs a finite sectorized observable framework with
    two independently driven channels:

        X_fast(t): gradient-driven growth, half-response tau = 30
        X_slow(t): regularization/decay-driven relaxation, half-decay tau = 1380

    The point is causal rather than statistical: the rates are fixed by the
    two mechanisms and their ordered response constants before any fitting is
    performed.

Claim status:
    - Constructive support for the Paper X Calibrated Mechanism-Separation
      Principle.
    - Proxy-layer evidence only.  It does not prove a K_i -> R_i/D bridge and
      does not measure tau(D).
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import projector_block_norm  # noqa: E402


SECTOR_DIM = 2
N_SECTORS = 3
DIM = SECTOR_DIM * N_SECTORS
TAU_FAST = 30
TAU_SLOW = 1380
STEP = 10
T_MAX = 2500


def sector_projectors() -> list[np.ndarray]:
    projectors = []
    for i in range(N_SECTORS):
        q = np.zeros((DIM, DIM), dtype=float)
        a = i * SECTOR_DIM
        b = a + SECTOR_DIM
        q[a:b, a:b] = np.eye(SECTOR_DIM)
        projectors.append(q)
    return projectors


def skew_block(i: int, j: int, scale: float) -> np.ndarray:
    """Skew-symmetric observable with one sector-to-sector block."""
    x = np.zeros((DIM, DIM), dtype=float)
    a = i * SECTOR_DIM
    b = a + SECTOR_DIM
    c = j * SECTOR_DIM
    d = c + SECTOR_DIM
    block = np.array([[1.0, -0.25], [0.5, 0.75]], dtype=float) * scale
    x[a:b, c:d] = block
    x[c:d, a:b] = -block.T
    return x


def gradient_growth(t: float) -> float:
    """Fast gradient-driven channel: 1-exp(-gamma t)."""
    gamma = math.log(2.0) / TAU_FAST
    return 1.0 - math.exp(-gamma * t)


def regularization_decay(t: float) -> float:
    """Slow regularization-only channel: exp(-lambda t)."""
    lam = math.log(2.0) / TAU_SLOW
    return math.exp(-lam * t)


def first_time(values: list[float], times: list[int], predicate) -> int | None:
    for t, value in zip(times, values):
        if predicate(value):
            return t
    return None


def audit() -> dict:
    qs = sector_projectors()
    times = list(range(0, T_MAX + STEP, STEP))

    k0_grow = []
    k1_decay = []
    k_comm = []

    initial_slow_norm = None
    final_fast_norm = None

    for t in times:
        x_fast = skew_block(0, 1, gradient_growth(t))
        x_slow = skew_block(1, 2, regularization_decay(t))
        comm = x_fast @ x_slow - x_slow @ x_fast

        fast_norm = projector_block_norm(qs, x_fast, 0, 1)
        slow_norm = projector_block_norm(qs, x_slow, 1, 2)
        comm_norm = projector_block_norm(qs, comm, 0, 2)

        if initial_slow_norm is None:
            initial_slow_norm = slow_norm
        final_fast_norm = fast_norm

        k0_grow.append(fast_norm)
        k1_decay.append(slow_norm)
        k_comm.append(comm_norm)

    assert initial_slow_norm is not None
    assert final_fast_norm is not None

    tol = 1e-10
    tau_k0 = first_time(k0_grow, times, lambda v: v + tol >= 0.5 * final_fast_norm)
    tau_k1 = first_time(k1_decay, times, lambda v: v <= 0.5 * initial_slow_norm + tol)

    theorem_prediction = TAU_FAST < TAU_SLOW
    measured_separation = tau_k0 is not None and tau_k1 is not None and tau_k0 < tau_k1

    return {
        "times": times,
        "k0_grow": k0_grow,
        "k1_decay": k1_decay,
        "k_comm": k_comm,
        "tau_k0_grow": tau_k0,
        "tau_k1_decay": tau_k1,
        "tau_fast_exact": TAU_FAST,
        "tau_slow_exact": TAU_SLOW,
        "theorem_prediction": theorem_prediction,
        "measured_separation": measured_separation,
        "ratio": (tau_k1 / tau_k0) if tau_k0 and tau_k1 else None,
    }


def main() -> None:
    result = audit()

    print("=" * 72)
    print("  Paper X Gap 3: Calibrated Mechanism Separation -> Proxy Rate Separation")
    print("=" * 72)
    print("Constructed SOF:")
    print("  sectors: 3 sectors, dimension 2 each")
    print("  X_fast: Q0 -> Q1 block, gradient-driven growth")
    print("  X_slow: Q1 -> Q2 block, regularization-only decay")
    print()
    print("Exact mechanism times:")
    print(f"  tau_fast = {result['tau_fast_exact']}")
    print(f"  tau_slow = {result['tau_slow_exact']}")
    print()
    print("Measured half-response audit:")
    print(f"  tau(K0_grow)  = {result['tau_k0_grow']}")
    print(f"  tau(K1_decay) = {result['tau_k1_decay']}")
    print(f"  ratio          = {result['ratio']:.1f}x")
    print()
    print("Conclusion:")
    print(f"  calibrated separation confirmed: {result['measured_separation']}")
    print("  causal form: distinct mechanisms + ordered constants imply distinct proxy rates")
    print("  claim status: constructive support for Paper X H3/H3'")
    print("  boundary: proxy-layer result only; no K_i -> R_i/D theorem is claimed")
    print("Done.")


if __name__ == "__main__":
    main()
