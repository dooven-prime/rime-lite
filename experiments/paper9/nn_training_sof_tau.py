"""Training-coupled SOF audit for neural-network observable time scales.

This is an exploratory Paper IX diagnostic. It couples a small neural network
training loop to SOF observables and measures whether first-layer support,
commutator survival, and nested-commutator depth proxies respond on different
time scales.

Claim status:
  - Paper IX diagnostic for observable dynamics.
  - Diagnostic support, not a standalone theorem source.
  - Uses raw block-norm proxies K0/K1/K2 rather than a binary depth field,
    because thresholded support removes scale information.
  - Binary counts are pointwise cutoff audits. Sector labels are not continued
    across training time, so this script does not measure a repair event.

Observable proxies:
  K0(t): max off-diagonal ||Q_i X_g Q_j||              (R1 proxy)
  K1(t): max off-diagonal ||Q_i [X_g, X_h] Q_j||       (R2 proxy)
  K2(t): max off-diagonal ||Q_i [[X_g,X_h],X_a] Q_j||  (D-depth proxy)

The expected structured-dynamics pattern is:

  tau(K0) <= tau(K1) <= tau(K2)

when training creates fast visible channels first and deeper Lie channels only
later. The script reports the measured ratios; it does not force the pattern.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402
from rime.rep_utils import basis_from_indices  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
LOG_PATH = DATA_DIR / "_paper9_nn_training_sof_tau.txt"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULT_PATH = RESULTS_DIR / "nn_training_sof_tau.json"
SCHEMA_VERSION = "paper9-nn-training-v2.0"
SEED = 42
TOL = 1e-8


def log(message: str = "") -> None:
    print(message, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def gelu(x: np.ndarray) -> np.ndarray:
    return x * 0.5 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x**3)))


def quantile_sectorization(score: np.ndarray, n_bins: int) -> list[np.ndarray]:
    dim = len(score)
    order = np.argsort(score)
    chunks = np.array_split(order, n_bins)
    Vs = []
    for chunk in chunks:
        if len(chunk) > 0:
            Vs.append(basis_from_indices(dim, np.array(chunk, dtype=int)))
    return Vs if Vs else [np.eye(dim, dtype=complex)]


def activation_sectorization(H: np.ndarray, activation_name: str) -> list[np.ndarray]:
    dim = H.shape[0]
    if activation_name == "None":
        return [np.eye(dim, dtype=complex)]
    if activation_name == "ReLU":
        return quantile_sectorization(np.mean(H > 0.0, axis=1), n_bins=2)
    if activation_name == "GeLU":
        return quantile_sectorization(np.mean(np.abs(gelu(H)), axis=1), n_bins=3)
    raise ValueError(f"unsupported activation sectorization: {activation_name}")


def activation_forward(H: np.ndarray, name: str) -> np.ndarray:
    if name == "ReLU":
        return relu(H)
    if name == "GeLU":
        return gelu(H)
    if name == "None":
        return H
    raise ValueError(f"unsupported activation for training: {name}")


def activation_derivative(H: np.ndarray, name: str) -> np.ndarray:
    if name == "ReLU":
        return (H > 0.0).astype(float)
    if name == "None":
        return np.ones_like(H)
    if name == "GeLU":
        # Numerical derivative is sufficient for this small diagnostic and
        # avoids a brittle closed-form approximation.
        eps = 1e-4
        return (gelu(H + eps) - gelu(H - eps)) / (2 * eps)
    raise ValueError(f"unsupported activation for training: {name}")


def fixed_skew(dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    A = rng.randn(dim, dim)
    X = A - A.T
    nrm = np.linalg.norm(X, "fro")
    return X / nrm if nrm > 1e-12 else X


def unnormalized_hidden_generators(W1: np.ndarray, W2: np.ndarray) -> list[np.ndarray]:
    """Weight-derived hidden operators retaining scale for tau measurement."""
    s_in = fixed_skew(W1.shape[1], seed=101)
    s_out = fixed_skew(W2.shape[0], seed=202)
    X1 = (W1 @ s_in @ W1.T)
    X2 = (W2.T @ s_out @ W2)

    # A third generator makes K2 less degenerate without adding random dynamics.
    diag = np.diag(np.linspace(-1.0, 1.0, W1.shape[0]))
    X3 = (diag @ X1 - X1 @ diag)

    Xs = []
    for X in (X1, X2, X3):
        X = (X - X.T) / 2.0
        Xs.append(X.astype(complex))
    return Xs


def offdiag_mask(n: int) -> np.ndarray:
    return ~np.eye(n, dtype=bool)


def max_offdiag_block(Vs: list[np.ndarray], M: np.ndarray) -> float:
    n = len(Vs)
    best = 0.0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            val = np.linalg.norm(Vs[i].conj().T @ M @ Vs[j], "fro")
            if val > best:
                best = float(val)
    return best


def raw_kappa_levels(Vs: list[np.ndarray], Xs: list[np.ndarray]) -> tuple[float, float, float]:
    if len(Vs) <= 1:
        return 0.0, 0.0, 0.0

    k0 = max(max_offdiag_block(Vs, X) for X in Xs)

    comms = []
    for g in range(len(Xs)):
        for h in range(g + 1, len(Xs)):
            comms.append(Xs[g] @ Xs[h] - Xs[h] @ Xs[g])
    k1 = max((max_offdiag_block(Vs, C) for C in comms), default=0.0)

    nested = []
    for C in comms:
        for X in Xs:
            nested.append(C @ X - X @ C)
    k2 = max((max_offdiag_block(Vs, N) for N in nested), default=0.0)
    return k0, k1, k2


def binary_audit(Vs: list[np.ndarray], Xs: list[np.ndarray], tol: float) -> dict:
    engine = AccessibilityEngine(Vs, Xs, tol=tol, max_depth=3)
    audit = engine.audit()
    cutoff = engine.cutoff_summary()
    return {
        "n_sectors": len(Vs),
        "sector_dims": [int(V.shape[1]) for V in Vs],
        "R1_lie_count": int(audit["R1_count"]),
        "R2_lie_count": int(audit["R2_count"]),
        "unsupported_direct_pairs": int(cutoff["unsupported_direct_pairs"]),
        "lie_emergent_pairs": int(cutoff["lie_emergent_pairs"]),
        "unreached_lie_pairs": int(cutoff["unreached_lie_pairs"]),
    }


def tau_half(times: list[int], values: list[float]) -> int | None:
    """First time reaching halfway from initial to final value."""
    if not values:
        return None
    start = values[0]
    end = values[-1]
    delta = end - start
    if abs(delta) < 1e-12:
        return None
    target = start + 0.5 * delta
    if delta > 0:
        for t, v in zip(times, values):
            if v >= target:
                return t
    else:
        for t, v in zip(times, values):
            if v <= target:
                return t
    return None


def train_one(
    activation: str,
    *,
    steps: int,
    audit_every: int,
    eta: float,
    weight_decay: float,
    hidden: int,
    batch: int,
) -> dict:
    rng = np.random.RandomState(SEED)
    d_in, d_out = 8, 4

    X = rng.randn(d_in, batch)
    W1_teacher = rng.randn(hidden, d_in) * 0.8
    W2_teacher = rng.randn(d_out, hidden) * 0.8
    Y = W2_teacher @ activation_forward(W1_teacher @ X, activation)

    # Small initialization makes block-norm growth measurable.
    W1 = rng.randn(hidden, d_in) * 0.03
    W2 = rng.randn(d_out, hidden) * 0.03

    times: list[int] = []
    losses: list[float] = []
    k0s: list[float] = []
    k1s: list[float] = []
    k2s: list[float] = []
    binary_rows: list[dict] = []

    for step in range(steps + 1):
        if step % audit_every == 0:
            H = W1 @ X
            Vs = activation_sectorization(H, activation)
            Xs = unnormalized_hidden_generators(W1, W2)
            k0, k1, k2 = raw_kappa_levels(Vs, Xs)
            pred = W2 @ activation_forward(H, activation)
            loss = float(np.mean((pred - Y) ** 2))

            times.append(step)
            losses.append(loss)
            k0s.append(k0)
            k1s.append(k1)
            k2s.append(k2)
            binary_rows.append(binary_audit(Vs, Xs, tol=TOL))

        if step == steps:
            break

        H = W1 @ X
        A = activation_forward(H, activation)
        pred = W2 @ A
        err = pred - Y

        dY = 2.0 * err / err.size
        dW2 = dY @ A.T + weight_decay * W2
        dA = W2.T @ dY
        dH = dA * activation_derivative(H, activation)
        dW1 = dH @ X.T + weight_decay * W1

        W2 -= eta * dW2
        W1 -= eta * dW1

    return {
        "activation": activation,
        "times": times,
        "loss": losses,
        "K0": k0s,
        "K1": k1s,
        "K2": k2s,
        "tau_K0": tau_half(times, k0s),
        "tau_K1": tau_half(times, k1s),
        "tau_K2": tau_half(times, k2s),
        "binary": binary_rows,
    }


def format_tau(tau: int | None) -> str:
    return "flat" if tau is None else str(tau)


def print_summary(result: dict) -> None:
    act = result["activation"]
    log(f"\nActivation: {act}")
    log(
        "  tau50: "
        f"K0={format_tau(result['tau_K0'])}, "
        f"K1={format_tau(result['tau_K1'])}, "
        f"K2={format_tau(result['tau_K2'])}"
    )
    log(
        "  start -> final: "
        f"loss {result['loss'][0]:.4e}->{result['loss'][-1]:.4e}, "
        f"K0 {result['K0'][0]:.3e}->{result['K0'][-1]:.3e}, "
        f"K1 {result['K1'][0]:.3e}->{result['K1'][-1]:.3e}, "
        f"K2 {result['K2'][0]:.3e}->{result['K2'][-1]:.3e}"
    )
    last = result["binary"][-1]
    log(
        "  final pointwise cutoff audit: "
        f"R1^Lie={last['R1_lie_count']}, R2^Lie={last['R2_lie_count']}, "
        f"unsupported_direct={last['unsupported_direct_pairs']}, "
        f"Lie-emergent={last['lie_emergent_pairs']}, "
        f"unreached_Lie={last['unreached_lie_pairs']}"
    )

    rows = list(zip(result["times"], result["binary"]))
    step = max(1, len(rows) // 6)
    log("  sampled pointwise cutoff counts:")
    for idx in range(0, len(rows), step):
        t, row = rows[idx]
        log(
            f"    step {t:>5d}: R1^Lie={row['R1_lie_count']}, "
            f"R2^Lie={row['R2_lie_count']}, "
            f"Lie-emergent={row['lie_emergent_pairs']}, "
            f"unreached_Lie={row['unreached_lie_pairs']}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--audit-every", type=int, default=20)
    parser.add_argument("--eta", type=float, default=0.08)
    parser.add_argument("--weight-decay", type=float, default=2e-3)
    parser.add_argument("--hidden", type=int, default=8)
    parser.add_argument("--batch", type=int, default=128)
    return parser.parse_args()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    args = parse_args()

    log("=" * 88)
    log("  Training-Coupled NN SOF Tau Diagnostic")
    log("=" * 88)
    log("Claim status: exploratory Paper IX diagnostic.")
    log("K0/K1/K2 are direct, simple-commutator, and nested-commutator norms.")
    log(
        f"steps={args.steps}, audit_every={args.audit_every}, eta={args.eta}, "
        f"weight_decay={args.weight_decay}, hidden={args.hidden}, batch={args.batch}"
    )

    results = []
    for activation in ["ReLU", "GeLU"]:
        result = train_one(
            activation,
            steps=args.steps,
            audit_every=args.audit_every,
            eta=args.eta,
            weight_decay=args.weight_decay,
            hidden=args.hidden,
            batch=args.batch,
        )
        results.append(result)
        print_summary(result)

    record = {
        "schema_version": SCHEMA_VERSION,
        "claim_status": "Computational Observation",
        "numpy_version": np.__version__,
        "seed": SEED,
        "parameters": {
            "steps": args.steps,
            "audit_every": args.audit_every,
            "eta": args.eta,
            "weight_decay": args.weight_decay,
            "hidden": args.hidden,
            "batch": args.batch,
            "binary_tolerance": TOL,
            "binary_max_depth": 3,
        },
        "semantics": {
            "continuous_fields": [
                "K0: maximum direct skew-generator block norm",
                "K1: maximum simple-commutator block norm",
                "K2: maximum nested-commutator block norm",
            ],
            "binary_counts": "pointwise cutoff-relative Lie/Hall audit",
            "coherent_sector_tracking": False,
            "temporal_repair_claimed": False,
        },
        "runs": results,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    log("\nTau-ratio check:")
    for result in results:
        taus = [result["tau_K0"], result["tau_K1"], result["tau_K2"]]
        ok = all(t is not None for t in taus) and taus[0] <= taus[1] <= taus[2]
        log(f"  {result['activation']:<5s}: "
            f"K0<=K1<=K2? {'yes' if ok else 'no/flat'} "
            f"({format_tau(taus[0])}, {format_tau(taus[1])}, {format_tau(taus[2])})")

    log("\nInterpretation:")
    log("  A positive result supports observable time-scale separation under a")
    log("  specified training dynamics. A flat or inverted result indicates that")
    log("  the activation, threshold, or training model has not isolated slow modes.")
    log("  The pointwise binary rows do not define a temporal repair event because")
    log("  this diagnostic does not continue sector labels across training time.")
    log(f"Versioned result: {RESULT_PATH}")
    log(f"\nFull log: {LOG_PATH}")
    log("Done.")


if __name__ == "__main__":
    main()
