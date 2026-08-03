"""Paper X registry probe: barrier-option SOF.

Claim status:
    - Registry evidence for a stochastic-finance SOF species.
    - Hitting-time diagnostic for a barrier sectorization.
    - Not an option-pricing theorem and not a zeta/trace-formula claim.

The SOF is built from a finite log-price grid:

    V      = C^n on grid points x = log S
    Q_i    = below-barrier / above-barrier sector projectors
    X      = drift and diffusion finite-difference observables
    Q      = CTMC log-GBM generator used for first-hitting-time diagnostics

The operator diagnostic records labelled direct blocks across the barrier. The
stochastic first-hitting time is a separate proxy diagnostic computed from the
absorbing CTMC subgenerator. No Lie/Hall carrier or depth field is declared.
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import compute_R1  # noqa: E402


def sector_bases_from_masks(masks: list[np.ndarray]) -> list[np.ndarray]:
    eye = np.eye(len(masks[0]), dtype=complex)
    bases = []
    for mask in masks:
        V = eye[:, mask]
        if V.shape[1] > 0:
            V, _ = np.linalg.qr(V)
        bases.append(V)
    return bases


def log_gbm_components(
    n: int,
    s_min: float,
    s_max: float,
    r: float,
    sigma: float,
    q: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return price grid, CTMC generator, drift observable, diffusion observable."""

    x = np.linspace(np.log(s_min), np.log(s_max), n)
    dx = x[1] - x[0]
    prices = np.exp(x)
    mu_x = r - q - 0.5 * sigma**2

    up_rate = 0.5 * sigma**2 / dx**2 + max(mu_x, 0.0) / dx
    down_rate = 0.5 * sigma**2 / dx**2 + max(-mu_x, 0.0) / dx

    Q = np.zeros((n, n), dtype=float)
    for i in range(n):
        if i > 0:
            Q[i, i - 1] = down_rate
        if i < n - 1:
            Q[i, i + 1] = up_rate
        Q[i, i] = -np.sum(Q[i])

    drift = np.zeros((n, n), dtype=float)
    diff = np.zeros((n, n), dtype=float)
    for i in range(1, n - 1):
        drift[i, i + 1] = max(mu_x, 0.0) / dx
        drift[i, i - 1] = max(-mu_x, 0.0) / dx
        drift[i, i] = -np.sum(drift[i])
        diff[i, i - 1] = 0.5 * sigma**2 / dx**2
        diff[i, i + 1] = 0.5 * sigma**2 / dx**2
        diff[i, i] = -np.sum(diff[i])

    return prices, Q, drift, diff


def mean_first_hit_time(Q: np.ndarray, start_idx: int, target_mask: np.ndarray) -> float:
    """Mean time to first hit target_mask for a finite CTMC generator."""

    transient = ~target_mask
    transient_indices = np.flatnonzero(transient)
    if target_mask[start_idx]:
        return 0.0
    local_start = int(np.where(transient_indices == start_idx)[0][0])
    Q_tt = Q[np.ix_(transient, transient)]
    rhs = -np.ones(Q_tt.shape[0])
    tau = np.linalg.solve(Q_tt, rhs)
    return float(tau[local_start])


def audit(
    n: int = 31,
    s_min: float = 20.0,
    s_max: float = 200.0,
    s0: float = 70.0,
    barrier: float = 80.0,
    r: float = 0.05,
    sigma: float = 0.20,
    q: float = 0.0,
) -> dict:
    prices, Q, drift, diff = log_gbm_components(n, s_min, s_max, r, sigma, q)
    below = prices < barrier
    above = ~below
    Vs = sector_bases_from_masks([below, above])

    # Use drift/diffusion pieces as observable-family data; use Q for hitting time.
    Xs = [drift.astype(complex), diff.astype(complex)]
    r1 = compute_R1(Vs, Xs, tol=1e-10)
    offdiag = ~np.eye(len(Vs), dtype=bool)
    labelled_count = int(np.sum(r1[:, offdiag]))
    labelled_possible = len(Xs) * len(Vs) * (len(Vs) - 1)
    labelled_pct = 100.0 * labelled_count / labelled_possible

    start_idx = int(np.argmin(np.abs(prices - s0)))
    tau_hit = mean_first_hit_time(Q, start_idx, above)

    block_norm = float(np.linalg.norm(Vs[0].conj().T @ Q @ Vs[1], "fro"))
    reverse_norm = float(np.linalg.norm(Vs[1].conj().T @ Q @ Vs[0], "fro"))

    return {
        "n": n,
        "s_min": s_min,
        "s_max": s_max,
        "s0": float(prices[start_idx]),
        "barrier": barrier,
        "below_dim": int(Vs[0].shape[1]),
        "above_dim": int(Vs[1].shape[1]),
        "tau_hit": tau_hit,
        "below_to_above_norm": block_norm,
        "above_to_below_norm": reverse_norm,
        "labelled_direct_support_count": labelled_count,
        "labelled_direct_support_possible": labelled_possible,
        "labelled_direct_support_pct": labelled_pct,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Paper X barrier-option SOF registry probe.")
    parser.add_argument("--n", type=int, default=31, help="log-price grid size")
    parser.add_argument("--s0", type=float, default=70.0, help="initial spot used for hitting-time diagnostic")
    parser.add_argument("--barrier", type=float, default=80.0, help="up-barrier level")
    parser.add_argument("--sigma", type=float, default=0.20, help="volatility")
    args = parser.parse_args()

    result = audit(n=args.n, s0=args.s0, barrier=args.barrier, sigma=args.sigma)

    print("=" * 72)
    print("  Paper X: Barrier-Option SOF Registry Probe")
    print("=" * 72)
    print(f"Grid: {result['n']} log-price states")
    print(f"S0 grid point: {result['s0']:.4f}; barrier: {result['barrier']:.4f}")
    print(f"Sectors: below-barrier dim={result['below_dim']}, above-barrier dim={result['above_dim']}")
    print()
    print("Declared operator-carrier audit:")
    print(
        "  labelled direct off-diagonal support: "
        f"{result['labelled_direct_support_count']}/"
        f"{result['labelled_direct_support_possible']} "
        f"({result['labelled_direct_support_pct']:.1f}%)"
    )
    print("  Lie/Hall carrier: not declared")
    print()
    print("Barrier diagnostics:")
    print(f"  ||Q_below Q Q_above||_F = {result['below_to_above_norm']:.4e}")
    print(f"  ||Q_above Q Q_below||_F = {result['above_to_below_norm']:.4e}")
    print(f"  mean first-hit time from S0 to barrier sector: {result['tau_hit']:.4f}")
    print()
    print("Interpretation:")
    print("  - the barrier defines a source-dependent sectorization of the price grid;")
    print("  - cross-barrier labelled blocks form the operator support finding;")
    print("  - mean first-hit time is a separate stochastic proxy diagnostic;")
    print("  - this is a registry/application entry, not an option-pricing theorem.")
    print("Done.")


if __name__ == "__main__":
    main()
