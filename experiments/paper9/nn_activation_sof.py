"""Neural-network activations as SOF design knobs.

This diagnostic tests the Paper IX idea that an architecture choice can change
the sectorized observable profile before any theorem-level training dynamics is
claimed.

Claim status:
  - Paper IX diagnostic for observable dynamics.
  - Diagnostic support, not a standalone theorem source.
  - The fixed-weight audit shows that activation-induced sectorization changes
    pointwise direct/simple-commutator support profiles.
  - A full tau-ratio experiment requires a coupled training/deformation model;
    static random weights are not enough.

SOF reading:
  activation + batch statistics -> sectorization {Q_i}
  weights                       -> observable family X
  R1^Lie/R2^Lie                -> pointwise sectorized shadows
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import compute_R1, compute_R2  # noqa: E402
from rime.rep_utils import basis_from_indices  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
LOG_PATH = DATA_DIR / "_paper9_nn_activation_sof.txt"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULT_PATH = RESULTS_DIR / "nn_activation_sof.json"
SCHEMA_VERSION = "paper9-nn-activation-v2.0"
TOL = 1e-6
SEED = 42


def log(message: str = "") -> None:
    print(message, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def gelu(x: np.ndarray) -> np.ndarray:
    return x * 0.5 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x**3)))


def topk(x: np.ndarray, k: int = 2) -> np.ndarray:
    y = np.zeros_like(x)
    for col in range(x.shape[1]):
        idx = np.argpartition(-np.abs(x[:, col]), k)[:k]
        y[idx, col] = x[idx, col]
    return y


def quantile_sectorization(score: np.ndarray, n_bins: int) -> list[np.ndarray]:
    """Build coordinate sectors from score quantiles."""
    dim = len(score)
    order = np.argsort(score)
    chunks = np.array_split(order, n_bins)
    Vs = []
    for chunk in chunks:
        if len(chunk) > 0:
            Vs.append(basis_from_indices(dim, np.array(chunk, dtype=int)))
    return Vs if Vs else [np.eye(dim, dtype=complex)]


def activation_sectorization(H: np.ndarray, activation_name: str) -> list[np.ndarray]:
    """Return hidden-unit coordinate sectors induced by an activation rule."""
    dim = H.shape[0]
    if activation_name == "None":
        return [np.eye(dim, dtype=complex)]

    if activation_name == "ReLU":
        # Hard sectors from activation frequency on the batch. Quantile split
        # avoids the all-active fallback that occurs when using "ever positive".
        active_fraction = np.mean(H > 0.0, axis=1)
        return quantile_sectorization(active_fraction, n_bins=2)

    if activation_name == "GeLU":
        # Smooth sectors from GeLU response strength.
        response = np.mean(np.abs(gelu(H)), axis=1)
        return quantile_sectorization(response, n_bins=3)

    if activation_name == "Top-2":
        winners = np.zeros(dim, dtype=bool)
        for col in range(H.shape[1]):
            idx = np.argpartition(-np.abs(H[:, col]), 2)[:2]
            winners[idx] = True
        top = np.flatnonzero(winners)
        rest = np.flatnonzero(~winners)
        Vs = []
        for idx in (top, rest):
            if len(idx) > 0:
                Vs.append(basis_from_indices(dim, idx))
        return Vs if Vs else [np.eye(dim, dtype=complex)]

    raise ValueError(f"unknown activation: {activation_name}")


def fixed_skew(dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    A = rng.randn(dim, dim)
    X = A - A.T
    nrm = np.linalg.norm(X, "fro")
    return X / nrm if nrm > 1e-12 else X


def hidden_generators(W1: np.ndarray, W2: np.ndarray) -> list[np.ndarray]:
    """Construct deterministic weight-derived skew operators on hidden space."""
    s_in = fixed_skew(W1.shape[1], seed=101)
    s_out = fixed_skew(W2.shape[0], seed=202)

    X1 = W1 @ s_in @ W1.T
    X2 = W2.T @ s_out @ W2
    Xs = []
    for X in (X1, X2):
        X = (X - X.T) / 2.0
        nrm = np.linalg.norm(X, "fro")
        Xs.append((X / nrm if nrm > 1e-12 else X).astype(complex))
    return Xs


def sof_from_activation(
    W1: np.ndarray,
    W2: np.ndarray,
    X_batch: np.ndarray,
    activation_name: str,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    H = W1 @ X_batch
    Vs = activation_sectorization(H, activation_name)
    Xs = hidden_generators(W1, W2)
    return Vs, Xs


def audit(Vs: list[np.ndarray], Xs: list[np.ndarray]) -> dict:
    R1 = compute_R1(Vs, Xs, tol=TOL)
    R2_arr, _ = compute_R2(Vs, Xs, tol=TOL)
    ns = len(Vs)
    offdiag = ~np.eye(ns, dtype=bool)
    r1_graph = np.any(R1, axis=0)

    return {
        "n_sec": ns,
        "dims": [int(V.shape[1]) for V in Vs],
        "R1_lie_tensor": int(np.sum(R1)),
        "R2_lie_tensor": int(np.sum(R2_arr)),
        "R1_lie_offdiag": int(np.sum(R1[:, offdiag])),
        "R2_lie_offdiag": int(np.sum(R2_arr[:, offdiag])),
        "unsupported_direct_pairs": int(
            ns * (ns - 1) - np.sum(r1_graph & offdiag)
        ),
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")

    rng = np.random.RandomState(SEED)
    d_in, d_hid, d_out = 10, 24, 5
    batch = 256

    W1 = rng.randn(d_hid, d_in) * 0.5
    W2 = rng.randn(d_out, d_hid) * 0.5
    X_batch = rng.randn(d_in, batch)

    log("=" * 88)
    log("  NN Activation as SOF Design Knob")
    log("=" * 88)
    log("Claim status: Paper IX diagnostic, not a standalone theorem source.")
    log("Same weights and batch; only activation-induced sectorization changes.")
    log()

    rows = []
    for name in ["None", "ReLU", "GeLU", "Top-2"]:
        Vs, Xs = sof_from_activation(W1, W2, X_batch, name)
        row = {"activation": name, **audit(Vs, Xs)}
        rows.append(row)

    header = (
        f"{'activation':<10s} {'sec':>3s} {'dims':<18s} "
        f"{'R1L':>4s} {'R2L':>4s} {'R1off':>6s} {'R2off':>6s} {'no-R1':>6s}"
    )
    log(header)
    log("-" * len(header))
    for row in rows:
        log(
            f"{row['activation']:<10s} {row['n_sec']:3d} "
            f"{str(row['dims']):<18s} {row['R1_lie_tensor']:4d} "
            f"{row['R2_lie_tensor']:4d} {row['R1_lie_offdiag']:6d} "
            f"{row['R2_lie_offdiag']:6d} "
            f"{row['unsupported_direct_pairs']:6d}"
        )

    record = {
        "schema_version": SCHEMA_VERSION,
        "claim_status": "Computational Observation",
        "numpy_version": np.__version__,
        "seed": SEED,
        "binary_tolerance": TOL,
        "semantics": {
            "carrier": "declared skew-Hermitian family",
            "counts": "pointwise generator-indexed support counts",
            "temporal_claim": False,
        },
        "rows": rows,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    log()
    log("Interpretation:")
    log("  activation choice changes the SOF sectorization and therefore the")
    log("  R1^Lie/R2^Lie profile, even with fixed weights.")
    log("  Full tau-ratio tests require a coupled training/deformation model.")
    log()
    log(f"Versioned result: {RESULT_PATH}")
    log()
    log("Paper IX prediction:")
    log("  activation families should systematically change observable time-scale")
    log("  ratios once weights, training dynamics, and sectorization are coupled.")
    log()
    log(f"Full log: {LOG_PATH}")
    log("Done.")


if __name__ == "__main__":
    main()
