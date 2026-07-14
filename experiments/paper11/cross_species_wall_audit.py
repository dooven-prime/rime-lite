"""Paper XI cross-species wall taxonomy audit.

Claim status:
    - Registry/taxonomy evidence for Paper XI.
    - Not a proof of an ADE classification.
    - Horizon diagnostic, not part of the Papers I--X release claim set.

The script records four real SOF diagnostics:
    L. Rubik spectral snapshot.
    M. Quantum accessibility contrast.
    N. Markov communicating/frozen-pair contrast.
    O. Graph Laplacian spectral-gap sensitivity.

The output is intentionally conservative: it reports observed wall/taxonomy
features and avoids codimension or smooth-wall claims unless directly proved.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import logm

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402


TOL = 1e-8
MAX_DEPTH = 4


def section(title: str) -> None:
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def normalize(X: np.ndarray) -> np.ndarray:
    nrm = np.linalg.norm(X, "fro")
    return X / nrm if nrm > 1e-12 else X


def skew_log(U: np.ndarray) -> np.ndarray:
    try:
        X = logm(U)
    except Exception:
        X = (U - U.conj().T) / 2.0
    return (X - X.conj().T) / 2.0


def sector_bases(dim: int) -> list[np.ndarray]:
    eye = np.eye(dim, dtype=complex)
    return [eye[:, [i]] for i in range(dim)]


def probe_rubik_spectral() -> dict:
    section("Exp L: Rubik Spectral Snapshot")
    op = CubieSpectralOperator()
    rhos = [np.asarray(rho, dtype=complex) for rho in op.rho_matrices()]
    A18 = sum(rhos) / len(rhos)
    A18 = (A18 + A18.conj().T) / 2.0
    evals = np.linalg.eigvalsh(A18)

    sorted_evals = sorted(evals, reverse=True)
    clusters: list[list[float]] = []
    for value in sorted_evals:
        if not clusters or abs(value - clusters[-1][0]) > 1e-6:
            clusters.append([float(value)])
        else:
            clusters[-1].append(float(value))

    layer_evals = [round(float(np.mean(c)), 6) for c in clusters]
    dims = [len(c) for c in clusters]
    k_values = sorted({round(9 * (1.0 - lam)) for lam in layer_evals})

    print(f"  A18 spectral layers: {len(clusters)}")
    print(f"  Dimensions: {dims}")
    print(f"  Eigenvalues: {layer_evals}")
    print(f"  k-set: {k_values}")
    print("  Taxonomy: fixed spectral snapshot; not a moving wall by itself.")
    print()
    return {"layers": len(clusters), "dims": dims, "eigenvalues": layer_evals, "k_values": k_values}


def one_qubit_gates() -> dict[str, np.ndarray]:
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    S = np.array([[1, 0], [0, 1j]], dtype=complex)
    T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)
    return {"X": X, "Y": Y, "Z": Z, "H": H, "S": S, "T": T}


def two_qubit_gates() -> dict[str, np.ndarray]:
    CNOT = np.array(
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1],
         [0, 0, 1, 0]],
        dtype=complex,
    )
    return {"CNOT": CNOT}


def embed_gate(label: str, n_qubits: int = 2) -> np.ndarray:
    one = one_qubit_gates()
    two = two_qubit_gates()
    eye_1 = np.eye(2, dtype=complex)
    if label in one:
        U = one[label]
        for _ in range(n_qubits - 1):
            U = np.kron(U, eye_1)
        return U
    if label in two and n_qubits >= 2:
        rest = np.eye(2 ** (n_qubits - 2), dtype=complex) if n_qubits > 2 else np.eye(1)
        return np.kron(two[label], rest) if n_qubits > 2 else two[label]
    raise ValueError(f"cannot embed gate {label!r}")


def quantum_audit(name: str, labels: list[str]) -> dict:
    Vs = sector_bases(4)
    Xs = [skew_log(embed_gate(label, 2)) for label in labels]
    engine = AccessibilityEngine(Vs, Xs, tol=1e-6, max_depth=MAX_DEPTH)
    return {"name": name, **engine.audit()}


def probe_quantum_accessibility() -> list[dict]:
    section("Exp M: Quantum Accessibility Contrast")
    systems = [
        ("Pauli {X,Z}", ["X", "Z"]),
        ("Clifford {H,S,CNOT}", ["H", "S", "CNOT"]),
        ("Universal {H,T,CNOT}", ["H", "T", "CNOT"]),
    ]
    rows = [quantum_audit(name, labels) for name, labels in systems]
    print(f"  {'System':<24s} {'R1%':>6s} {'R2%':>6s} {'frzR1':>6s} {'Drep':>5s} {'Dmax':>5s}")
    for row in rows:
        print(f"  {row['name']:<24s} {row['R1_pct']:>5.1f}% {row['R2_pct']:>5.1f}% "
              f"{row['frozen_R1']:>6d} {row['D_repaired']:>5d} {row['D_max']:>5d}")
    print("  Taxonomy: accessibility contrast; not a Rubik-specific phenomenon.")
    print()
    return rows


def markov_sof(P: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n = P.shape[0]
    Vs = sector_bases(n)
    try:
        Q = logm(P)
    except Exception:
        Q = P - np.eye(n)
    X = normalize((Q - Q.conj().T) / 2.0)
    return Vs, [X]


def probe_markov_frozen_pairs() -> list[dict]:
    section("Exp N: Markov Communicating/Frozen-Pair Contrast")
    systems = [
        ("complete cycle", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)),
        ("absorbing state", np.array([[1, 0, 0], [0.3, 0.4, 0.3], [0, 0, 1]], dtype=float)),
        ("random dense", np.array([[0.3, 0.3, 0.4], [0.2, 0.5, 0.3], [0.4, 0.1, 0.5]], dtype=float)),
    ]
    rows = []
    print(f"  {'System':<16s} {'R1%':>6s} {'frzR1':>6s} {'frzD':>5s} {'Drep':>5s} {'Dmax':>5s}")
    for name, P in systems:
        Vs, Xs = markov_sof(P)
        audit = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=MAX_DEPTH).audit()
        rows.append({"name": name, **audit})
        print(f"  {name:<16s} {audit['R1_pct']:>5.1f}% {audit['frozen_R1']:>6d} "
              f"{audit['frozen_D']:>5d} {audit['D_repaired']:>5d} {audit['D_max']:>5d}")
    print("  Taxonomy: communicating-class / frozen-pair boundary diagnostics.")
    print()
    return rows


def graph_gap(A: np.ndarray) -> float:
    degree = np.diag(np.sum(A, axis=1))
    L = degree - A
    evals = np.linalg.eigvalsh(L)
    ordered = sorted(float(x) for x in evals)
    return ordered[1] - ordered[0] if len(ordered) > 1 else 0.0


def probe_graph_gap_sensitivity() -> list[dict]:
    section("Exp O: Graph Laplacian Gap Sensitivity")
    systems = [
        ("K3 complete", np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)),
        ("P3 path", np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)),
        ("C4 cycle", np.array([[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]], dtype=float)),
    ]
    rows = []
    print(f"  {'Graph':<14s} {'gap':>8s} {'max |delta gap|':>16s} {'tested edges':>12s}")
    for name, A in systems:
        base_gap = graph_gap(A)
        edges = [(i, j) for i in range(A.shape[0]) for j in range(i + 1, A.shape[0]) if A[i, j] == 1]
        changes = []
        for i, j in edges:
            Ap = A.copy()
            Ap[i, j] = Ap[j, i] = 0.0
            changes.append(graph_gap(Ap) - base_gap)
        max_change = max((abs(x) for x in changes), default=0.0)
        rows.append({"name": name, "gap": base_gap, "max_delta": max_change, "edges": len(edges)})
        print(f"  {name:<14s} {base_gap:>8.3f} {max_change:>16.3f} {len(edges):>12d}")
    print("  Taxonomy: discrete graph perturbation / spectral-gap sensitivity, not a smooth codimension theorem.")
    print()
    return rows


def main() -> None:
    section("Paper XI Cross-Species Wall Taxonomy Audit")
    print("Claim status: taxonomy evidence; no ADE classification theorem is claimed.")
    print()

    rubik = probe_rubik_spectral()
    quantum = probe_quantum_accessibility()
    markov = probe_markov_frozen_pairs()
    graph = probe_graph_gap_sensitivity()

    section("Summary")
    print(f"  Rubik: {rubik['layers']} A18 spectral layers; fixed spectral snapshot.")
    clifford = next(row for row in quantum if row["name"] == "Clifford {H,S,CNOT}")
    pauli = next(row for row in quantum if row["name"] == "Pauli {X,Z}")
    print(f"  Quantum: Clifford+CNOT D_repaired={clifford['D_repaired']} vs "
          f"Pauli D_repaired={pauli['D_repaired']}.")
    absorbing = next(row for row in markov if row["name"] == "absorbing state")
    print(f"  Markov: absorbing example has frozen_D={absorbing['frozen_D']}.")
    max_graph_delta = max(row["max_delta"] for row in graph)
    print(f"  Graph: max tested Laplacian-gap change={max_graph_delta:.3f}.")
    print()
    print("Conclusion: registered species expose distinct wall/taxonomy types.")
    print("ADE classification, if used, should be restricted to smooth discriminant maps.")
    print("Done.")


if __name__ == "__main__":
    main()
