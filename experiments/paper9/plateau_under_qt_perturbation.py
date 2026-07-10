"""Paper IX plateau postprocess/compute script for QT perturbations.

Goal:
    Convert depth matrices D(epsilon) into plateau functions

        P_d(epsilon) = fraction of off-diagonal sector pairs with D(i,j) <= d

    and test whether a degeneration law

        P_d(0) - P_d(epsilon) ~= C epsilon^alpha

    is meaningful for RIME operator-weight perturbations.  Yang-like
    state-space mixing gives monotone degeneration; RIME operator-weight
    redistribution may instead preserve, oscillate, or improve accessibility.

Default mode is postprocess-only. Use ``--compute`` to recompute the expensive
Rubik depth data and cache the plateau arrays. This script is a Paper IX
deformation-dynamics diagnostic, not a standalone theorem source.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine, plateau_fraction  # noqa: E402
from rime.cubie import CubieMove  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


TOL = 1e-8
MAX_DEPTH = 4
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CACHE_PATH = DATA_DIR / "paper9_qt_plateaus.npz"
LOG_PATH = DATA_DIR / "_paper9_plateau_under_qt_perturbation.txt"


def log(message: str = "") -> None:
    print(message, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def epsilon_grid(full: bool) -> np.ndarray:
    if full:
        return np.concatenate([[0.0], np.logspace(-4, -1, 8), np.linspace(0.15, 0.5, 8)])
    return np.array([0.0, 1e-4, 1e-3, 1e-2, 0.1, 0.5])


def qt_directions(n_gen: int, qt_idx: list[int], n_dirs: int) -> list[np.ndarray]:
    rng = np.random.RandomState(42)
    directions = []
    for _ in range(n_dirs):
        v = np.zeros(n_gen)
        vq = rng.randn(len(qt_idx))
        vq /= np.linalg.norm(vq)
        for k, idx in enumerate(qt_idx):
            v[idx] = vq[k]
        directions.append(v)
    return directions


def save_cache(epsilons: np.ndarray, plateaus: np.ndarray, completed: int) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(
        CACHE_PATH,
        epsilons=epsilons,
        plateaus=plateaus,
        completed=np.array([completed], dtype=int),
        max_depth=np.array([MAX_DEPTH], dtype=int),
    )


def compute_plateaus(n_dirs: int, full_grid: bool) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    log("=" * 72)
    log("  Paper IX: Plateau Functions under QT Perturbation")
    log("=" * 72)
    log("  Mode: compute expensive D(epsilon) data and cache plateaus")

    op = CubieSpectralOperator()
    decomp = op.center_decomposition()
    Vs = decomp["sector_bases"]
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    move_keys = list(CubieMove.prim_moves().keys())
    if len(move_keys) != len(rhos):
        raise RuntimeError("canonical move-key order does not match rho_matrices()")
    qt_idx = [i for i, key in enumerate(move_keys) if key[2] != 2]
    Xs0 = [(rho - rho.conj().T) / 2.0 for rho in rhos]

    epsilons = epsilon_grid(full_grid)
    directions = qt_directions(len(rhos), qt_idx, n_dirs)
    plateaus = np.full((len(directions), MAX_DEPTH + 1, len(epsilons)), np.nan)
    save_cache(epsilons, plateaus, completed=0)

    log(f"  sectors={len(Vs)}, generators={len(rhos)}, directions={len(directions)}")
    log(f"  epsilon grid={list(map(float, epsilons))}")
    log(f"  cache={CACHE_PATH}")

    for dir_idx, direction in enumerate(directions):
        log()
        log(f"  Direction {dir_idx + 1}/{len(directions)}")
        for eps_idx, eps in enumerate(epsilons):
            weights = np.clip(np.ones(len(rhos)) + eps * direction, 0.0, 2.0)
            Xs = [weights[i] * Xs0[i] for i in range(len(rhos))]
            engine = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=MAX_DEPTH)
            D, _ = engine.depth()
            for depth in range(MAX_DEPTH + 1):
                plateaus[dir_idx, depth, eps_idx] = plateau_fraction(D, depth)
            log(f"    eps={eps:.4g}: P={plateaus[dir_idx, :, eps_idx].round(4).tolist()}")
            save_cache(epsilons, plateaus, completed=dir_idx)

        save_cache(epsilons, plateaus, completed=dir_idx + 1)

    postprocess()


def fit_decay(epsilons: np.ndarray, values: np.ndarray, max_eps: float = 0.02):
    p0 = values[0]
    mask = (epsilons > 0) & (epsilons <= max_eps) & np.isfinite(values)
    eps_fit = epsilons[mask]
    gaps = p0 - values[mask]
    positive = gaps > 1e-12
    eps_fit = eps_fit[positive]
    gaps = gaps[positive]
    if len(eps_fit) < 3:
        return None

    A = np.column_stack([np.ones(len(eps_fit)), np.log(eps_fit)])
    b = np.log(gaps)
    coeffs, *_ = np.linalg.lstsq(A, b, rcond=None)
    log_c, alpha = coeffs
    pred = A @ coeffs
    ss_res = float(np.sum((b - pred) ** 2))
    ss_tot = float(np.sum((b - np.mean(b)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0
    return float(np.exp(log_c)), float(alpha), r2, len(eps_fit)


def classify_delta(delta: float, tol: float = 1e-12) -> str:
    if delta < -tol:
        return "decay"
    if delta > tol:
        return "improvement"
    return "stable"


def postprocess() -> None:
    if not CACHE_PATH.exists():
        print(f"No cache found at {CACHE_PATH}.")
        print("Run with --compute to generate plateau data; default mode only postprocesses the cache.")
        return

    data = np.load(CACHE_PATH)
    epsilons = data["epsilons"]
    plateaus = data["plateaus"]
    completed = int(data["completed"][0])

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    log("=" * 72)
    log("  Paper IX: Plateau Postprocess")
    log("=" * 72)
    log(f"  cache={CACHE_PATH}")
    log(f"  completed directions={completed}/{plateaus.shape[0]}")
    log(f"  epsilons={list(map(float, epsilons))}")

    for dir_idx in range(min(completed, plateaus.shape[0])):
        log()
        log(f"  Direction {dir_idx + 1}")
        for depth in range(plateaus.shape[1]):
            values = plateaus[dir_idx, depth]
            if not np.isfinite(values).all():
                continue
            delta = values[-1] - values[0]
            status = classify_delta(delta)
            log(
                f"    P_{depth}: P(0)={values[0]:.4f}, "
                f"P({epsilons[-1]:.3g})={values[-1]:.4f}, "
                f"Delta={delta:+.4f} [{status}]"
            )

        values = plateaus[dir_idx, 3]
        fit = fit_decay(epsilons, values)
        if fit is None:
            log("    alpha(P_3): no positive small-epsilon decay to fit")
        else:
            c, alpha, r2, n = fit
            log(f"    alpha(P_3): C={c:.4g}, alpha={alpha:.4f}, R2={r2:.4f}, n={n}")

    log()
    log("  Interpretation:")
    log("  P_d decay supports Yang-like state-space degeneration.")
    log("  Stable or improving P_d means RIME operator-weight redistribution is")
    log("  a different geometric object from monotone filtration degeneration.")
    log("  This is evidence for distinct SOF deformation modalities, not a")
    log("  current theorem claim.")
    log("Done.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compute", action="store_true", help="recompute expensive plateau cache")
    parser.add_argument("--full-grid", action="store_true", help="use the full 17-point epsilon grid")
    parser.add_argument("--directions", type=int, default=3, help="number of QT directions for --compute")
    args = parser.parse_args()

    if args.compute:
        compute_plateaus(n_dirs=args.directions, full_grid=args.full_grid)
    else:
        postprocess()


if __name__ == "__main__":
    main()
