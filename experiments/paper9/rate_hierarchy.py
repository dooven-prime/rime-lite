"""Validate an exact scale-separated threshold construction for Paper IX.

The declared three-sector skew-Hermitian family is

    X_12(t) = t (E_12 - E_21),
    X_23(t) = t (E_23 - E_32).

For the coordinate sector projectors, the selected direct and simple-
commutator block norms are

    K_dir(t)  = ||Q_1 X_12(t) Q_2||_F = t,
    K_comm(t) = ||Q_1 [X_12(t), X_23(t)] Q_3||_F = t^2.

At a common threshold 0 < eta < 1, their first crossing parameters are eta
and sqrt(eta). This is one exact finite construction relative to the declared
trajectory, normalization, norm, and threshold policy. It is not an intrinsic
rate invariant, a universal rate law, or a Lie-depth computation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULT_PATH = RESULTS_DIR / "rate_hierarchy.json"
SCHEMA_VERSION = "paper9-rate-hierarchy-v3.0"
DEFAULT_THRESHOLD = 1.0e-6


def coordinate_projectors(dim: int = 3) -> list[np.ndarray]:
    projectors = []
    for index in range(dim):
        projector = np.zeros((dim, dim), dtype=complex)
        projector[index, index] = 1.0
        projectors.append(projector)
    return projectors


def skew_edge(dim: int, left: int, right: int, scale: float) -> np.ndarray:
    matrix = np.zeros((dim, dim), dtype=complex)
    matrix[left, right] = scale
    matrix[right, left] = -scale
    return matrix


def evaluate_family(t: float) -> dict[str, float]:
    q1, q2, q3 = coordinate_projectors()
    x12 = skew_edge(3, 0, 1, t)
    x23 = skew_edge(3, 1, 2, t)
    commutator = x12 @ x23 - x23 @ x12

    direct_norm = float(np.linalg.norm(q1 @ x12 @ q2, "fro"))
    commutator_norm = float(np.linalg.norm(q1 @ commutator @ q3, "fro"))
    return {
        "t": float(t),
        "direct_norm": direct_norm,
        "commutator_norm": commutator_norm,
        "direct_formula_residual": abs(direct_norm - t),
        "commutator_formula_residual": abs(commutator_norm - t * t),
        "x12_skew_residual": float(np.linalg.norm(x12 + x12.conj().T, "fro")),
        "x23_skew_residual": float(np.linalg.norm(x23 + x23.conj().T, "fro")),
    }


def build_result(threshold: float) -> dict:
    if not 0 < threshold < 1:
        raise ValueError("threshold must satisfy 0 < eta < 1")

    tau_direct = threshold
    tau_commutator = math.sqrt(threshold)
    samples = [
        evaluate_family(0.0),
        evaluate_family(0.5 * tau_direct),
        evaluate_family(tau_direct),
        evaluate_family(0.5 * tau_commutator),
        evaluate_family(tau_commutator),
        evaluate_family(2.0 * tau_commutator),
    ]
    max_residual = max(
        max(
            sample["direct_formula_residual"],
            sample["commutator_formula_residual"],
            sample["x12_skew_residual"],
            sample["x23_skew_residual"],
        )
        for sample in samples
    )

    result = {
        "schema_version": SCHEMA_VERSION,
        "claim_status": "Theorem",
        "validation_role": "deterministic finite-matrix check",
        "numpy_version": np.__version__,
        "construction": {
            "space": "C^3",
            "sectorization": "three labelled coordinate projectors",
            "lie_family": [
                "X_12(t)=t(E_12-E_21)",
                "X_23(t)=t(E_23-E_32)",
            ],
            "trajectory": "gamma(t)=t for t>=0",
            "normalization": "both generators have Frobenius norm sqrt(2) at t=1",
            "selected_direct_block": "Q_1 X_12(t) Q_2",
            "selected_commutator_block": "Q_1 [X_12(t),X_23(t)] Q_3",
        },
        "threshold_policy": {
            "type": "common first-crossing threshold",
            "comparison": "norm >= eta",
            "eta": threshold,
        },
        "exact_formulas": {
            "direct_norm": "t",
            "commutator_norm": "t^2",
            "tau_direct": "eta",
            "tau_commutator": "sqrt(eta)",
            "ratio": "eta^(-1/2)",
        },
        "observed": {
            "tau_direct": tau_direct,
            "tau_commutator": tau_commutator,
            "ratio": tau_commutator / tau_direct,
            "max_validation_residual": max_residual,
        },
        "samples": samples,
        "boundaries": [
            "selected continuous block norms, not Boolean support times",
            "simple commutator only, not Lie depth",
            "one engineered family, not a universal hierarchy",
            "response times depend on trajectory parameterization",
            "response times depend on observable normalization, norm, and threshold",
        ],
    }
    return result


def validate_result(result: dict, tolerance: float = 1.0e-14) -> None:
    observed = result["observed"]
    eta = result["threshold_policy"]["eta"]
    expected_ratio = eta ** -0.5
    if abs(observed["ratio"] - expected_ratio) > tolerance * expected_ratio:
        raise AssertionError("unexpected first-crossing ratio")
    if observed["max_validation_residual"] > tolerance:
        raise AssertionError("matrix validation residual exceeds tolerance")

    if abs(observed["tau_direct"] - eta) > tolerance:
        raise AssertionError("direct first-crossing parameter is inconsistent")
    if abs(observed["tau_commutator"] - math.sqrt(eta)) > tolerance:
        raise AssertionError("commutator first-crossing parameter is inconsistent")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_result(args.threshold)
    validate_result(result)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    observed = result["observed"]
    print("Paper IX exact scale-separated threshold validation")
    print(f"  threshold eta:       {args.threshold:.6g}")
    print(f"  tau(K_dir):          {observed['tau_direct']:.6g}")
    print(f"  tau(K_comm):         {observed['tau_commutator']:.6g}")
    print(f"  ratio:               {observed['ratio']:.6g}")
    print(f"  max residual:        {observed['max_validation_residual']:.3e}")
    print(f"  result:              {RESULT_PATH}")


if __name__ == "__main__":
    main()
