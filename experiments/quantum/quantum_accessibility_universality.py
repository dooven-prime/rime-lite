"""Quantum SOF R1/R2/D audit on small gate systems.

This is a non-Rubik sanity check for the Sectorized Observable Framework language.
It uses computational-basis projectors as sectors and logarithmic/skew
generators derived from small gate sets.

Status:
    Exploratory support for SOF universality language, not theorem support for
    Papers I--VII.
"""

from __future__ import annotations

import os
import sys

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
    """Computational-basis one-dimensional sector bases."""
    dim = 2**n_qubits
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [b]] for b in range(dim)]


def gate_generators(
    gate_list: list[tuple[object, str]], n_qubits: int
) -> tuple[list[np.ndarray], list[str]]:
    """Embed gates on the first qubit(s) and return skew-Hermitian generators."""
    eye_1 = np.eye(2, dtype=complex)
    rest_2 = np.eye(2 ** (n_qubits - 2), dtype=complex) if n_qubits >= 2 else np.eye(1)
    generators: list[np.ndarray] = []
    labels: list[str] = []

    for gate, label in gate_list:
        if gate.num_qubits() == 1:
            U = cirq.unitary(gate)
            for _ in range(n_qubits - 1):
                U = np.kron(U, eye_1)
        elif gate.num_qubits() == 2 and n_qubits >= 2:
            U2 = cirq.unitary(gate)
            U = np.kron(U2, rest_2) if n_qubits > 2 else U2
        else:
            continue

        try:
            X = logm(U)
        except Exception:
            X = (U - U.conj().T) / 2.0
        generators.append((X - X.conj().T) / 2.0)
        labels.append(label)

    return generators, labels


def audit(name: str, gate_list: list[tuple[object, str]], n_qubits: int) -> dict:
    Vs = sector_bases(n_qubits)
    Xs, labels = gate_generators(gate_list, n_qubits)
    engine = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=MAX_DEPTH)
    summary = engine.audit()

    return {
        "name": name,
        "qubits": n_qubits,
        "dim": 2**n_qubits,
        "labels": labels,
        "entangling": any(label in {"CNOT", "CZ"} for label in labels),
        **summary,
    }


def print_table(results: list[dict]) -> None:
    print("=" * 98)
    print("  Quantum SOF - R1/R2/D Universality Table")
    print("=" * 98)
    print("  Sectors = computational-basis projectors |b><b|")
    print("  R1 = generator support, R2 = commutator survival")
    print("  D  = first Lie-depth matrix; 999 denotes unreached within max depth")
    print()

    header = (
        f"  {'Gate set':<24s} {'q':>2s} {'sec':>3s} "
        f"{'R1off':>6s} {'R2off':>6s} {'frzR1':>5s} {'frzD':>5s} "
        f"{'D-rep':>5s} {'Dmax':>4s} {'per_depth':>18s} {'note'}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in results:
        note = "entangling" if r["entangling"] else "product"
        print(
            f"  {r['name']:<24s} {r['qubits']:>2d} {r['n_sec']:>3d} "
            f"{r['R1_pct']:>5.1f}% {r['R2_pct']:>5.1f}% "
            f"{r['frozen_R1']:>5d} {r['frozen_D']:>5d} {r['D_repaired']:>5d} "
            f"{r['D_max']:>4d} {str(r['per_depth_sizes']):>18s} {note}"
        )


def print_registry(results: list[dict]) -> None:
    print()
    print("=" * 98)
    print("  SOF Registry - Quantum Instances")
    print("=" * 98)
    for r in results:
        labels = ", ".join(r["labels"])
        print(
            f"  {r['name']} ({r['qubits']}q): "
            f"Q=computational basis, X={{{labels}}}, "
            f"R1off={r['R1_offdiag_pct']:.1f}%, R2off={r['R2_offdiag_pct']:.1f}%, "
            f"R1tensor={r['R1_tensor_pct']:.1f}%, R2tensor={r['R2_tensor_pct']:.1f}%, "
            f"frozen_R1={r['frozen_R1']}, frozen_D={r['frozen_D']}, "
            f"D_repaired={r['D_repaired']}, D_max={r['D_max']}, "
            f"per_depth={r['per_depth_sizes']}"
        )


def main() -> None:
    H, X, Y, Z = (cirq.H, "H"), (cirq.X, "X"), (cirq.Y, "Y"), (cirq.Z, "Z")
    S, T = (cirq.S, "S"), (cirq.T, "T")
    CNOT, CZ = (cirq.CNOT, "CNOT"), (cirq.CZ, "CZ")

    systems = [
        ("Pauli {X,Z}", [X, Z], 2),
        ("Pauli {X,Y,Z}", [X, Y, Z], 2),
        ("Clifford {H,S,CNOT}", [H, S, CNOT], 2),
        ("Clifford {H,S,CZ}", [H, S, CZ], 2),
        ("Universal {H,T,CNOT}", [H, T, CNOT], 2),
        ("Pauli {X,Z}", [X, Z], 3),
        ("Clifford {H,S,CNOT}", [H, S, CNOT], 3),
        ("Universal {H,T,CNOT}", [H, T, CNOT], 3),
    ]

    results = [audit(name, gates, nq) for name, gates, nq in systems]
    print_table(results)

    print()
    print("  Observations:")
    print("  1. CNOT systems repair R1-frozen pairs at Lie depth in the tested range.")
    print("  2. CZ is not equivalent to CNOT for this sectorization and generator set.")
    print("  3. Clifford+CNOT and Universal+CNOT have identical R1/R2/D summaries here.")
    print("  4. Product-only Pauli systems remain D-frozen in the tested depth range.")

    print_registry(results)
    print("\nDone.")


if __name__ == "__main__":
    main()
