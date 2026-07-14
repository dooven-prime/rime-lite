# Cross-Reference Diagnostic: Grokking Rate Separation
# ====================================================
"""Diagnostic for Xu--Vardi--Safran-style ridge-regression rate separation.

Claim status:
  - This is a related-work positioning diagnostic, not a standalone theorem
    source.
  - It verifies the elementary row-space / null-space rate separation in an
    overparameterized ridge-regression model.
  - The RIME analogy is only structural: fast row-space convergence is compared
    with first-layer accessible data, while slow null-space decay is compared
    with delayed repair or higher-depth accessibility.

Reference:
  Xu, Vardi, Safran, "To Grok Grokking: Provable Grokking in Ridge Regression",
  arXiv:2601.19791.
"""

from __future__ import annotations

import os
import sys

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data")
LOG_PATH = os.path.join(OUT_DIR, "_cross_ref_grokking_rate_separation.txt")

RNG_SEED = 42
TOL = 1e-12


def log(msg: str = "") -> None:
    print(msg, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")


def section(title: str) -> None:
    log("=" * 72)
    log(f"  {title}")
    log("=" * 72)


def ridge_state_at(
    t: int,
    *,
    v_basis: np.ndarray,
    eigvals: np.ndarray,
    theta0_row: np.ndarray,
    theta_inf_row: np.ndarray,
    theta0_perp: np.ndarray,
    eta: float,
    lam: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return theta(t), row-space component, and null-space component."""
    row_rates = 1.0 - eta * (eigvals + lam)
    perp_rate = 1.0 - eta * lam

    theta_row_coeff = theta_inf_row + (row_rates**t) * (theta0_row - theta_inf_row)
    theta_row = v_basis.T @ theta_row_coeff
    theta_perp = (perp_rate**t) * theta0_perp
    theta = theta_row + theta_perp
    return theta, theta_row, theta_perp


def main() -> None:
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

    rng = np.random.RandomState(RNG_SEED)

    # Overparameterized feature model: m >> n.
    m = 400
    n = 50
    d_true = 5
    eta = 0.2
    lam = 1e-4
    init_scale = 1e-2
    t_max = 5000
    sample_steps = np.array([0, 50, 100, 250, 500, 1000, 2500, 5000])

    phi = rng.randn(n, m) / np.sqrt(n)
    theta_star = np.zeros(m)
    theta_star[:d_true] = rng.randn(d_true)
    y = phi @ theta_star

    theta0 = rng.randn(m) * init_scale

    # Gradient of (1/2n)||Phi theta - y||^2 + (lambda/2)||theta||^2.
    gram = phi.T @ phi / n
    rhs = phi.T @ y / n

    # Row-space basis and closed-form GD trajectory.
    u, singular, vt = np.linalg.svd(phi, full_matrices=False)
    del u
    eigvals = singular**2 / n
    v_basis = vt

    theta0_row = v_basis @ theta0
    theta0_perp = theta0 - v_basis.T @ theta0_row
    rhs_row = v_basis @ rhs
    theta_inf_row = rhs_row / (eigvals + lam)

    lambda_min_pos = float(np.min(eigvals))
    fast_rate = 1.0 - eta * (lambda_min_pos + lam)
    slow_rate = 1.0 - eta * lam
    fast_decay = 1.0 - fast_rate
    slow_decay = 1.0 - slow_rate

    assert 0.0 < fast_rate < slow_rate < 1.0
    assert fast_decay / slow_decay > 10.0

    n_test = 500
    phi_test = rng.randn(n_test, m) / np.sqrt(n_test)
    y_test = phi_test @ theta_star

    section("Grokking Rate Separation - Cross-Reference Diagnostic")
    log("Reference: Xu, Vardi, Safran, arXiv:2601.19791")
    log("Claim status: related-work diagnostic, not RIME theorem support.")
    log()
    log(f"m={m}, n={n}, d_true={d_true}, eta={eta}, lambda={lam}, seed={RNG_SEED}")
    log(f"row-space dimension={n}, null-space dimension={m - n}")
    log()
    log("Theoretical contraction rates:")
    log(f"  slow null-space rate      = 1 - eta*lambda = {slow_rate:.8f}")
    log(
        "  fastest guaranteed row fit = "
        f"1 - eta*(lambda_min^+ + lambda) = {fast_rate:.8f}"
    )
    log(f"  decay-speed ratio          = {fast_decay / slow_decay:.1f}x")
    log()
    log("Sampled trajectory:")
    log(
        f"{'step':>6s}  {'train_mse':>11s}  {'test_mse':>11s}  "
        f"{'||theta_row||':>13s}  {'||theta_perp||':>14s}"
    )

    first_train_step = None
    train_threshold = 1e-4

    for t in sample_steps:
        theta, theta_row, theta_perp = ridge_state_at(
            int(t),
            v_basis=v_basis,
            eigvals=eigvals,
            theta0_row=theta0_row,
            theta_inf_row=theta_inf_row,
            theta0_perp=theta0_perp,
            eta=eta,
            lam=lam,
        )
        train_mse = float(np.mean((phi @ theta - y) ** 2))
        test_mse = float(np.mean((phi_test @ theta - y_test) ** 2))
        if first_train_step is None and train_mse < train_threshold:
            first_train_step = int(t)
        log(
            f"{int(t):6d}  {train_mse:11.6e}  {test_mse:11.6e}  "
            f"{np.linalg.norm(theta_row):13.6e}  {np.linalg.norm(theta_perp):14.6e}"
        )

    theta_end, _, theta_perp_end = ridge_state_at(
        t_max,
        v_basis=v_basis,
        eigvals=eigvals,
        theta0_row=theta0_row,
        theta_inf_row=theta_inf_row,
        theta0_perp=theta0_perp,
        eta=eta,
        lam=lam,
    )
    grad_end = gram @ theta_end - rhs + lam * theta_end

    log()
    log("Diagnostics:")
    log(f"  first sampled train_mse < {train_threshold:g}: {first_train_step}")
    log(f"  null component remaining at T={t_max}: "
        f"{np.linalg.norm(theta_perp_end) / max(np.linalg.norm(theta0_perp), TOL):.3f}")
    log(f"  terminal ridge-gradient norm: {np.linalg.norm(grad_end):.3e}")
    log()
    log("RIME reading:")
    log("  row-space component  -> fast observable/data-visible channel")
    log("  null-space component -> slow hidden channel controlled only by decay")
    log("  analogy              -> rate separation, not SOF theorem support")
    log()
    log("Done.")


if __name__ == "__main__":
    main()
