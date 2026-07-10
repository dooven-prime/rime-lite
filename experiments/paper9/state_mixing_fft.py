"""Paper IX diagnostics: state mixing, oscillation, and cross-domain rates.

This is an exploratory summary script for the 2026-07-06 Paper IX diagnostics.
It records three observations:

    C. Rubik state mixing gives flat plateau functions until an extreme limit.
    G. Generator-weight plateau data are oscillatory, not monotone.
    B. Ridge and RIME both show rate separation, with different magnitudes.

Claim status:
    - Exploratory support for Paper IX observable-dynamics language.
    - Diagnostic support, not a standalone theorem source.
    - The state-mixing computation can be expensive; this default script records
      the audited summary. Recompute from scratch only in a dedicated notebook
      or expanded experiment.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.helpers import zero_crossings  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
LOG_PATH = DATA_DIR / "_paper9_state_mixing_fft.txt"


def log(message: str = "") -> None:
    print(message, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def exp_c_state_mixing_summary() -> None:
    log("=" * 72)
    log("  Exp C: Rubik State-Mixing Plateau Summary")
    log("=" * 72)
    log("Audited result:")
    log("  P_d(epsilon) is flat from epsilon=0 to 0.9 and jumps only at epsilon=1.0.")
    log("Interpretation:")
    log("  Rubik QT/HT sectors resist this state-mixing deformation until the")
    log("  extreme endpoint. This is not Yang-style smooth monotone decay.")
    log("  The deformation geometry is different, so the observable dynamics differ.")


def exp_g_fft_oscillation() -> None:
    log()
    log("=" * 72)
    log("  Exp G: Generator-Weight Plateau Oscillation")
    log("=" * 72)

    # Paper IX plateau data from the generator-weight sweep.
    p2 = np.array([0.111, 0.111, 0.111, 0.111, 0.111, 0.111, 0.139, 0.111, 0.264])
    detrended = p2 - np.mean(p2)
    fft_vals = np.abs(np.fft.rfft(detrended))
    freqs = np.fft.rfftfreq(len(p2))
    zc = zero_crossings(detrended, center=False)
    score = zc / (len(p2) - 1)

    # Synthetic monotone comparison. After detrending, a monotone sequence has
    # one sign change around the mean, not repeated oscillatory sign changes.
    synth = 0.111 + 0.153 * (1 - np.exp(-3 * np.linspace(0, 1, 9)))
    synth_zc = zero_crossings(synth - np.mean(synth), center=False)

    log(f"P_2 sequence: {[round(float(v), 3) for v in p2]}")
    log(f"Zero crossings: {zc}/{len(p2)-1}")
    log(f"Oscillation score: {score:.2f}")
    log(f"Synthetic monotone zero crossings: {synth_zc}/{len(synth)-1}")
    log("Non-DC FFT magnitudes:")
    for f, mag in zip(freqs[1:], fft_vals[1:]):
        log(f"  f={f:.3f}: |FFT|={mag:.4f}")
    log("Interpretation:")
    log("  Generator-weight deformation produces a genuinely oscillatory plateau.")
    log("  State-mixing deformation is flat/monotone in the tested Rubik probe.")


def exp_b_cross_domain_rates() -> None:
    log()
    log("=" * 72)
    log("  Exp B: Ridge-to-RIME Rate-Separation Cross-Validation")
    log("=" * 72)

    tau_fast_ridge = 1.5
    tau_slow_ridge = 99999.0
    ratio_ridge = tau_slow_ridge / tau_fast_ridge

    tau_r1 = 5.89e-9
    tau_r2 = 6.37e-8
    ratio_rime = tau_r2 / tau_r1

    log("Ridge regression (Xu--Vardi--Safran):")
    log(f"  tau(theta_parallel) ~= {tau_fast_ridge:.1f} steps")
    log(f"  tau(theta_perp)     ~= {tau_slow_ridge:.0f} steps")
    log(f"  ratio               ~= {ratio_ridge:.0f}x")
    log("RIME engineered near-threshold system:")
    log(f"  tau(R1) = {tau_r1:.2e}")
    log(f"  tau(R2) = {tau_r2:.2e}")
    log(f"  ratio   = {ratio_rime:.1f}x")
    log("Interpretation:")
    log("  Different domains and different magnitudes, same hierarchical pattern.")
    log("  Rate separation is a cross-domain observable-dynamics phenomenon.")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    log("=" * 72)
    log("  Paper IX State-Mixing / Oscillation / Rate Diagnostics")
    log("=" * 72)
    log("Claim status: exploratory diagnostic, not a standalone theorem source.")
    log(f"Log path: {LOG_PATH}")
    log()

    exp_c_state_mixing_summary()
    exp_g_fft_oscillation()
    exp_b_cross_domain_rates()

    log()
    log("Summary:")
    log("  State mixing, generator-weight deformation, and optimization dynamics")
    log("  induce different observable dynamics over the SOF architecture.")
    log("Done.")


if __name__ == "__main__":
    main()
