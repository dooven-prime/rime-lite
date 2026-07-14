"""Paper XI audit: quantum repair persistence under CNOT-strength interpolation.

Claim status:
    - Registry/taxonomy evidence for the repair-persistence invariant p_W.
    - A matrix-space interpolation diagnostic between a product endpoint and
      the Clifford+CNOT gate-log SOF.
    - Not a physical Hamiltonian path and not a universal quantum-wall theorem.

The default path keeps H and S fixed and interpolates the CNOT matrix toward
identity.  This reproduces the Paper XI repair-wall transition:
    threshold = 0.55
    p_W = 0.45 over the unit interpolation range
    stability = 100% after activation on the tested grid
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings

import numpy as np
from scipy.linalg import logm

try:
    import cirq
except ImportError as exc:  # pragma: no cover - user-facing dependency error
    raise SystemExit(
        "Missing optional dependency 'cirq'. Run this script inside the project "
        "venv or install cirq in the active interpreter."
    ) from exc

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402


TOL = 1e-6
MAX_DEPTH = 4


def sector_bases(n_qubits: int) -> list[np.ndarray]:
    dim = 2**n_qubits
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [idx]] for idx in range(dim)]


def scaled_cnot(strength: float) -> np.ndarray:
    U2 = cirq.unitary(cirq.CNOT)
    eye = np.eye(4, dtype=complex)
    interpolated = eye + strength * (U2 - eye)
    scale = np.sqrt(np.trace(interpolated @ interpolated.conj().T) / 4.0)
    return interpolated / scale


def skew_log(U: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The logm input matrix may be nearly singular.")
        X = logm(U)
    return (X - X.conj().T) / 2.0


def gate_generators(n_qubits: int, cnot_strength: float) -> list[np.ndarray]:
    eye_1 = np.eye(2, dtype=complex)
    rest_2 = np.eye(2 ** (n_qubits - 2), dtype=complex) if n_qubits >= 2 else np.eye(1)

    generators: list[np.ndarray] = []
    for gate in [cirq.H, cirq.S]:
        U = cirq.unitary(gate)
        for _ in range(n_qubits - 1):
            U = np.kron(U, eye_1)
        generators.append(skew_log(U))

    U2 = scaled_cnot(cnot_strength)
    U = np.kron(U2, rest_2) if n_qubits > 2 else U2
    generators.append(skew_log(U))
    return generators


def audit_strength(strength: float, n_qubits: int = 2) -> dict:
    sectors = sector_bases(n_qubits)
    generators = gate_generators(n_qubits, strength)
    engine = AccessibilityEngine(sectors, generators, tol=TOL, max_depth=MAX_DEPTH)
    summary = engine.audit()
    frozen = engine.frozen_pairs()
    return {"strength": strength, **summary, **frozen}


def run(grid: int = 21, n_qubits: int = 2) -> dict:
    strengths = np.linspace(0.0, 1.0, grid)
    rows = [audit_strength(float(strength), n_qubits=n_qubits) for strength in strengths]

    active_indices = [idx for idx, row in enumerate(rows) if row["D_repaired"] > 0]
    threshold = rows[active_indices[0]]["strength"] if active_indices else None
    activation_index = active_indices[0] if active_indices else None

    if activation_index is None:
        p_range = 0.0
        stability = 0.0
    else:
        p_range = (1.0 - threshold) / (strengths[-1] - strengths[0])
        tail = rows[activation_index:]
        stability = sum(row["D_repaired"] > 0 for row in tail) / len(tail)

    return {
        "grid": grid,
        "n_qubits": n_qubits,
        "rows": rows,
        "threshold": threshold,
        "p_W": p_range,
        "active_samples": len(active_indices),
        "sample_fraction": len(active_indices) / len(rows),
        "stability": stability,
    }


def print_report(result: dict) -> None:
    print("=" * 86)
    print("  Paper XI - Quantum Repair Persistence")
    print("=" * 86)
    print("  Path: fixed H,S plus matrix-space CNOT-strength interpolation")
    print("  Claim status: repair-persistence diagnostic, not a physical gate path theorem")
    print()
    print(f"  {'strength':>8s}  {'D_rep':>6s}  {'frz_R1':>6s}  {'frz_D':>6s}  {'R1_pct':>7s}  marker")
    print(f"  {'-' * 8}  {'-' * 6}  {'-' * 6}  {'-' * 6}  {'-' * 7}  {'-' * 18}")

    first_seen = False
    for row in result["rows"]:
        marker = ""
        if row["D_repaired"] > 0 and not first_seen:
            marker = "first repair"
            first_seen = True
        elif row["D_repaired"] > 0:
            marker = "persistent"
        print(
            f"  {row['strength']:>8.2f}  {row['D_repaired']:>6d}  "
            f"{row['frozen_R1']:>6d}  {row['frozen_D']:>6d}  "
            f"{row['R1_pct']:>6.1f}%  {marker}"
        )

    threshold = result["threshold"]
    threshold_text = "none" if threshold is None else f"{threshold:.2f}"
    print()
    print("  Summary:")
    print(f"    threshold:      {threshold_text}")
    print(f"    p_W:            {result['p_W']:.2f} of the unit interpolation range")
    print(
        f"    active samples: {result['active_samples']}/{result['grid']} "
        f"({result['sample_fraction']:.1%} of grid points)"
    )
    print(f"    stability:      {result['stability']:.1%} after activation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=int, default=21, help="number of strength samples")
    parser.add_argument("--qubits", type=int, default=2, help="number of qubits")
    args = parser.parse_args()

    print_report(run(grid=args.grid, n_qubits=args.qubits))


if __name__ == "__main__":
    main()
