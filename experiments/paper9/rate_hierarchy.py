"""Exploratory diagnostics for Paper IX observable dynamics.

This script records three Paper IX diagnostics:

    A. Rubik flat-region sweep for observable first-jump thresholds.
    E. Degenerate rate-collapse sanity check.
    J. Sectorization sensitivity under QT-probe / HT-probe / mixed sectors.

Claim status:
    - Exploratory support for Paper IX language only.
    - Diagnostic support, not a standalone theorem source.
    - Exp A is currently a negative/flat-region diagnostic on Rubik, not a
      validation of tau(R1) < tau(R2) < tau(D).

Default mode runs only the cheap degenerate sanity check. Use --rubik-sweep
and/or --sectorization to run the expensive Rubik diagnostics. Large
sectorizations are skipped unless --max-sectors is raised.
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
from rime.accessibility import AccessibilityEngine  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
LOG_PATH = DATA_DIR / "_paper9_rate_hierarchy.txt"
TOL = 1e-8
MAX_DEPTH = 4


def log(message: str = "") -> None:
    print(message, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def section(title: str) -> None:
    log("=" * 72)
    log(f"  {title}")
    log("=" * 72)


def normalize(X: np.ndarray) -> np.ndarray:
    nrm = np.linalg.norm(X, "fro")
    return X / nrm if nrm > 1e-12 else X


def skew_part(A: np.ndarray) -> np.ndarray:
    return normalize((A - A.conj().T) / 2.0)


def rubik_data() -> tuple[list[np.ndarray], list[np.ndarray], list[int], list[int]]:
    """Return canonical Rubik sectors, skew generators, and QT/HT indices."""
    op = CubieSpectralOperator()
    decomp = op.center_decomposition()
    Vs = decomp["sector_bases"]

    # rho_matrices() is the public matrix API. The key order follows
    # CubieSpectralOperator.rho_moves(18), used only here for QT/HT labels.
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    keys = list(CubieSpectralOperator.rho_moves(18).keys())
    Xs = [skew_part(rho) for rho in rhos]
    qt_idx = [i for i, key in enumerate(keys) if key[2] != 2]
    ht_idx = [i for i, key in enumerate(keys) if key[2] == 2]
    return Vs, Xs, qt_idx, ht_idx


def state_counts(Vs: list[np.ndarray], Xs: list[np.ndarray], *, include_depth: bool) -> dict:
    engine = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=MAX_DEPTH)
    R1, R2_arr, _ = engine.support()
    result = {
        "R1_tensor": int(np.sum(R1)),
        "R2_tensor": int(np.sum(R2_arr)),
        "D_frozen": None,
    }
    if include_depth:
        D, _ = engine.depth()
        n_sec = len(Vs)
        result["D_frozen"] = sum(
            1 for i in range(n_sec) for j in range(n_sec)
            if i != j and D[i, j] >= MAX_DEPTH
        )
    return result


def exp_rubik_flat_sweep() -> None:
    section("Exp A: Rubik Flat-Region Sweep")
    log("Purpose: measure first-jump thresholds for R1/R2/D under generator weights.")
    log("Claim status: exploratory; no hierarchy is claimed if no jumps occur.")

    Vs, Xs0, qt_idx, ht_idx = rubik_data()
    n_gen = len(Xs0)
    log(f"Rubik: {len(Vs)} sectors, {n_gen} generators (QT={len(qt_idx)}, HT={len(ht_idx)})")

    epsilons = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
    n_dirs = 8
    rng = np.random.RandomState(42)
    baseline = state_counts(Vs, Xs0, include_depth=True)

    tau_R1: list[float] = []
    tau_R2: list[float] = []
    tau_D: list[float] = []

    for d_idx in range(n_dirs):
        v = np.zeros(n_gen)
        active = qt_idx if d_idx < n_dirs // 2 else ht_idx
        coeff = rng.randn(len(active))
        coeff /= np.linalg.norm(coeff)
        for local_idx, gen_idx in enumerate(active):
            v[gen_idx] = coeff[local_idx]

        first_R1 = None
        first_R2 = None
        first_D = None
        for eps in epsilons[1:]:
            weights = np.clip(np.ones(n_gen) + eps * v, 0.0, 2.0)
            Xs = [weights[i] * Xs0[i] for i in range(n_gen)]
            current = state_counts(Vs, Xs, include_depth=True)
            if first_R1 is None and current["R1_tensor"] != baseline["R1_tensor"]:
                first_R1 = eps
            if first_R2 is None and current["R2_tensor"] != baseline["R2_tensor"]:
                first_R2 = eps
            if first_D is None and current["D_frozen"] != baseline["D_frozen"]:
                first_D = eps

        if first_R1 is not None:
            tau_R1.append(first_R1)
        if first_R2 is not None:
            tau_R2.append(first_R2)
        if first_D is not None:
            tau_D.append(first_D)

    log(f"Baseline: R1={baseline['R1_tensor']}, R2={baseline['R2_tensor']}, "
        f"D_frozen={baseline['D_frozen']}")
    log(f"First jumps over {n_dirs} directions and eps<=0.1:")
    log(f"  R1 jumps: {tau_R1 if tau_R1 else 'none'}")
    log(f"  R2 jumps: {tau_R2 if tau_R2 else 'none'}")
    log(f"  D jumps:  {tau_D if tau_D else 'none'}")

    if tau_R1 and tau_R2 and tau_D:
        log(f"Mean tau(R1)={np.mean(tau_R1):.4f}, "
            f"tau(R2)={np.mean(tau_R2):.4f}, tau(D)={np.mean(tau_D):.4f}")
    else:
        log("Conclusion: Rubik is flat on this tested local region; use larger "
            "perturbations or smaller SOFs to measure a rate hierarchy.")


def exp_rate_collapse() -> None:
    section("Exp E: Degenerate Rate-Collapse Sanity Check")
    log("Purpose: show that observable rate separation needs nontrivial sectorization.")

    Vs = [np.eye(4, dtype=complex)]
    X = np.zeros((4, 4), dtype=complex)
    X[0, 1] = 1.0
    X[1, 0] = -1.0
    engine = AccessibilityEngine(Vs, [X], tol=TOL, max_depth=MAX_DEPTH)
    audit = engine.audit()

    log(f"1-sector SOF: sectors={audit['n_sec']}, generators={audit['n_gen']}")
    log(f"  R1_pct={audit['R1_pct']:.1f}%, R2_pct={audit['R2_pct']:.1f}%, "
        f"D_max={audit['D_max']}")
    log("Conclusion: no cross-sector observables exist, so no R1/R2/D "
        "time-scale hierarchy can be measured.")


def sectorize_from_operators(operators: list[np.ndarray], seed: int = 42) -> list[np.ndarray]:
    """Build a simple spectral sectorization from a random Hermitian probe."""
    rng = np.random.RandomState(seed)
    dim = operators[0].shape[0]
    probe = np.zeros((dim, dim), dtype=complex)
    for op in operators:
        H = (op + op.conj().T) / 2.0
        probe += rng.randn() * H
    probe = (probe + probe.conj().T) / 2.0

    evals, evecs = np.linalg.eigh(probe)
    order = np.argsort(evals)[::-1]
    clusters: list[list[int]] = []
    current = [int(order[0])]
    current_val = evals[order[0]]
    for idx in order[1:]:
        idx = int(idx)
        if abs(evals[idx] - current_val) < 1e-6:
            current.append(idx)
        else:
            clusters.append(current)
            current = [idx]
            current_val = evals[idx]
    clusters.append(current)

    Vs = []
    for cluster in clusters:
        V, _ = np.linalg.qr(evecs[:, cluster])
        Vs.append(V)
    Vs.sort(key=lambda V: V.shape[1], reverse=True)
    return Vs


def exp_sectorization_sensitivity(include_depth: bool, max_sectors: int) -> None:
    section("Exp J: Sectorization Sensitivity")
    log("Purpose: same generators, different sectorizations, different observables.")
    log("QT/HT sectorizations here are random spectral probes, not theorem-level "
        "joint-sector constructions.")
    if include_depth:
        log("Depth enabled: this may be slow for large sectorizations.")

    Vs_mixed, Xs, qt_idx, ht_idx = rubik_data()
    op = CubieSpectralOperator()
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    sectorizations = {
        "QT-probe": sectorize_from_operators([rhos[i] for i in qt_idx], seed=42),
        "HT-probe": sectorize_from_operators([rhos[i] for i in ht_idx], seed=43),
        "Mixed canonical": Vs_mixed,
    }

    log(f"Large sectorizations with more than {max_sectors} sectors are skipped.")

    header = f"{'sectorization':<18s} {'sec':>4s} {'top dims':<24s} {'R1':>8s} {'R2':>8s}"
    if include_depth:
        header += f" {'D_frozen':>9s}"
    log(header)
    log("-" * len(header))

    for label, Vs in sectorizations.items():
        if len(Vs) > max_sectors:
            log(
                f"{label:<18s} {len(Vs):4d} {str([V.shape[1] for V in Vs[:5]]):<24s} "
                f"{'skipped':>8s} {'skipped':>8s}"
                + (f" {'skipped':>9s}" if include_depth else "")
            )
            continue
        counts = state_counts(Vs, Xs, include_depth=include_depth)
        top_dims = [V.shape[1] for V in Vs[:5]]
        row = (
            f"{label:<18s} {len(Vs):4d} {str(top_dims):<24s} "
            f"{counts['R1_tensor']:8d} {counts['R2_tensor']:8d}"
        )
        if include_depth:
            row += f" {counts['D_frozen']:9d}"
        log(row)

    log("Conclusion: SOF is an interface. The sectorization is input data, and "
        "changing it changes R1/R2/D shadows.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubik-sweep", action="store_true",
                        help="run expensive Rubik local perturbation sweep")
    parser.add_argument("--sectorization", action="store_true",
                        help="run Rubik QT/HT/mixed sectorization sensitivity")
    parser.add_argument("--include-depth", action="store_true",
                        help="include expensive D computation in sectorization sensitivity")
    parser.add_argument("--max-sectors", type=int, default=20,
                        help="skip sectorization audits above this sector count")
    return parser.parse_args()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    section("Paper IX Observable Dynamics Diagnostics")
    log("Claim status: exploratory diagnostic, not a standalone theorem source.")
    log(f"Log path: {LOG_PATH}")

    args = parse_args()
    exp_rate_collapse()
    if args.rubik_sweep:
        exp_rubik_flat_sweep()
    else:
        log()
        log("Skipped Exp A Rubik sweep. Use --rubik-sweep to run it.")
    if args.sectorization:
        exp_sectorization_sensitivity(
            include_depth=args.include_depth,
            max_sectors=args.max_sectors,
        )
    else:
        log("Skipped Exp J sectorization sensitivity. Use --sectorization to run it.")

    log()
    log("Done.")


if __name__ == "__main__":
    main()
