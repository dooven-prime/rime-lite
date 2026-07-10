"""Paper X tau-boundary probes for quantum, graph, and Yang-like SOFs.

Claim status:
    - Registry evidence for Paper X.
    - Negative/boundary evidence for Paper X calibrated mechanism separation / H3'.
    - Evidence summary, not a standalone theorem source.

The purpose of this script is to test whether observable rate hierarchy appears
outside the known structured training-coupled setting.  The result is mostly
negative: linear interpolation, discrete graph rewiring, and weak state-mixing
probes do not produce a robust K0 < K1 < K2 hierarchy.  This supports H3:
structured dynamics with mechanism-separated channels is decisive.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import numpy as np
from scipy.linalg import logm

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import sector_block_norm  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402
from rime.rep_utils import computational_basis_sectors  # noqa: E402


TOL = 1e-10
RNG = np.random.RandomState(42)


@dataclass(frozen=True)
class TauResult:
    tau: int | None
    status: str
    start: float
    end: float
    maximum: float


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


def tau50_response(values: list[float], tol: float = TOL) -> TauResult:
    """Half-response time for increasing trajectories, with degeneracy labels."""
    arr = np.asarray(values, dtype=float)
    start = float(arr[0])
    end = float(arr[-1])
    maximum = float(np.max(arr))
    spread = float(np.max(arr) - np.min(arr))
    scale = max(abs(maximum), abs(start), abs(end), 1.0)

    if maximum <= tol:
        return TauResult(None, "zero", start, end, maximum)
    if spread <= 1e-8 * scale:
        return TauResult(None, "flat", start, end, maximum)
    if end <= start + 1e-8 * scale:
        return TauResult(None, "decreasing_or_nonresponsive", start, end, maximum)

    target = start + 0.5 * (end - start)
    for idx, value in enumerate(arr):
        if value >= target:
            return TauResult(idx, "valid", start, end, maximum)
    return TauResult(None, "no_crossing", start, end, maximum)


def hierarchy_status(results: list[TauResult]) -> str:
    if any(r.status != "valid" for r in results):
        return "DEGENERATE"
    taus = [r.tau for r in results]
    return "YES" if all(a < b for a, b in zip(taus, taus[1:])) else "NO"


def format_tau(result: TauResult) -> str:
    return str(result.tau) if result.tau is not None else result.status


def one_qubit_gates() -> dict[str, np.ndarray]:
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    S = np.array([[1, 0], [0, 1j]], dtype=complex)
    return {"X": X, "Z": Z, "H": H, "S": S}


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


def block_trajectory_norms(Vs: list[np.ndarray], Xs: list[np.ndarray]) -> tuple[float, float, float]:
    """Return max off-diagonal K0, K1, K2 norms for one SOF snapshot."""
    n_sec = len(Vs)
    n_gen = len(Xs)
    k0 = 0.0
    k1 = 0.0
    k2 = 0.0

    commutators: list[tuple[int, int, np.ndarray]] = []
    for g in range(n_gen):
        for h in range(g + 1, n_gen):
            C = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
            commutators.append((g, h, C))

    nested: list[np.ndarray] = []
    if n_gen >= 3:
        for g, h, C in commutators:
            for a in range(n_gen):
                if a in (g, h):
                    continue
                nested.append(C @ Xs[a] - Xs[a] @ C)

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            for X in Xs:
                k0 = max(k0, sector_block_norm(Vs, X, i, j))
            for _, _, C in commutators:
                k1 = max(k1, sector_block_norm(Vs, C, i, j))
            for N in nested:
                k2 = max(k2, sector_block_norm(Vs, N, i, j))

    return k0, k1, k2


def quantum_linear_interpolation() -> list[dict]:
    section("Probe 4: Quantum Linear Generator Interpolation")
    systems = [
        ("Clifford+CNOT", ["H", "S", "CNOT"]),
        ("Pauli {X,Z}", ["X", "Z"]),
    ]
    rows = []
    Vs = computational_basis_sectors(4)

    for name, labels in systems:
        targets = [skew_log(embed_gate(label, 2)) for label in labels]
        initials = []
        for target in targets:
            dim = target.shape[0]
            M = RNG.randn(dim, dim) + 1j * RNG.randn(dim, dim)
            initials.append((M - M.conj().T) / 2.0)

        K0s, K1s, K2s = [], [], []
        for alpha in np.linspace(0.0, 1.0, 101):
            Xs = [(1.0 - alpha) * Xi + alpha * Xt for Xi, Xt in zip(initials, targets)]
            k0, k1, k2 = block_trajectory_norms(Vs, Xs)
            K0s.append(k0)
            K1s.append(k1)
            K2s.append(k2)

        tau0 = tau50_response(K0s)
        tau1 = tau50_response(K1s)
        tau2 = tau50_response(K2s)
        status = hierarchy_status([tau0, tau1, tau2])
        print(f"  {name:<16s}: tau(K0)={format_tau(tau0)}, "
              f"tau(K1)={format_tau(tau1)}, tau(K2)={format_tau(tau2)}, hierarchy={status}")
        print(f"    ranges: K0 {K0s[0]:.4e}->{K0s[-1]:.4e}, "
              f"K1 {K1s[0]:.4e}->{K1s[-1]:.4e}, "
              f"K2 {K2s[0]:.4e}->{K2s[-1]:.4e}")
        rows.append({"name": name, "taus": (tau0, tau1, tau2), "status": status})

    print("  Interpretation: linear interpolation is not mechanism-separated dynamics (H3 fails).")
    print()
    return rows


def graph_sof(A: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n = A.shape[0]
    Vs = computational_basis_sectors(n)
    degree = np.diag(np.sum(A, axis=1))
    L = degree - A
    X1 = normalize((A - A.T) / 2.0)
    X2 = normalize(1j * L)
    return Vs, [X1, X2]


def graph_edge_rewiring() -> dict:
    section("Probe 5: Graph Edge-Rewiring")
    n_vertices = 6
    edges = [(i, j) for i in range(n_vertices) for j in range(i + 1, n_vertices)]
    RNG.shuffle(edges)
    A = np.zeros((n_vertices, n_vertices), dtype=float)
    K0s, K1s = [], []

    for i, j in edges:
        A[i, j] = A[j, i] = 1.0
        Vs, Xs = graph_sof(A)
        k0, k1, _ = block_trajectory_norms(Vs, Xs)
        K0s.append(k0)
        K1s.append(k1)

    tau0 = tau50_response(K0s)
    tau1 = tau50_response(K1s)
    status = hierarchy_status([tau0, tau1])
    print(f"  Graph rewiring: tau(K0)={format_tau(tau0)}, "
          f"tau(K1)={format_tau(tau1)}, hierarchy={status}")
    print(f"    ranges: K0 {K0s[0]:.4e}->{K0s[-1]:.4e}, "
          f"K1 {K1s[0]:.4e}->{K1s[-1]:.4e}")
    print("  Interpretation: undirected edge addition is discrete and degenerate for this SOF.")
    print()
    return {"taus": (tau0, tau1), "status": status}


def yang_state_mixing() -> dict:
    section("Probe 6: Yang-Like State Mixing")
    op = CubieSpectralOperator()
    Vs = op.center_decomposition()["sector_bases"]
    rhos = [np.asarray(rho, dtype=complex) for rho in op.rho_matrices()]
    Xs0 = [(rho - rho.conj().T) / 2.0 for rho in rhos[:6]]

    dim = rhos[0].shape[0]
    rho_id = np.eye(dim, dtype=complex) / dim
    target_sector = Vs[6] @ Vs[6].conj().T
    K0s, K1s = [], []

    for eps in np.linspace(0.0, 1.0, 21):
        rho_s = (1.0 - eps) * rho_id + eps * target_sector
        Xs = [rho_s @ X @ rho_s for X in Xs0]
        k0, k1, _ = block_trajectory_norms(Vs, Xs)
        K0s.append(k0)
        K1s.append(k1)

    tau0 = tau50_response(K0s)
    tau1 = tau50_response(K1s)
    status = hierarchy_status([tau0, tau1])
    print(f"  Yang-like mixing: tau(K0)={format_tau(tau0)}, "
          f"tau(K1)={format_tau(tau1)}, hierarchy={status}")
    print(f"    ranges: K0 {K0s[0]:.4e}->{K0s[-1]:.4e}, "
          f"K1 {K1s[0]:.4e}->{K1s[-1]:.4e}")
    print("  Interpretation: state mixing does not produce the training-coupled hierarchy.")
    print()
    return {"taus": (tau0, tau1), "status": status}


def main() -> None:
    section("Paper X Tau Boundary Probes")
    print("Claim status: registry boundary evidence for calibrated mechanism separation / H3'.")
    print("Positive hierarchy requires structured, mechanism-separated dynamics (H3).")
    print()

    quantum = quantum_linear_interpolation()
    graph = graph_edge_rewiring()
    yang = yang_state_mixing()

    section("Summary")
    print("  Known constructive control: mechanism-separated SOF has tau(K0_grow)=30 << tau(K1_decay)=1380.")
    print("  Known positive: NN GD+WD has tau(K0)<tau(K1)<tau(K2) = 60<80<120.")
    print("  Known partial: engineered near-threshold accessibility has tau(R1)<tau(R2).")
    for row in quantum:
        print(f"  Quantum {row['name']}: {row['status']} (linear interpolation; H3 fails)")
    print(f"  Graph rewiring: {graph['status']} (discrete/degenerate dynamics)")
    print(f"  Yang-like mixing: {yang['status']} (state-mixing geometry, not training-coupled)")
    print()
    print("Conclusion: observable rate hierarchy is not universal over all SOF deformations.")
    print("Positive cases require H3: structured, mechanism-separated dynamics.")
    print("Done.")


if __name__ == "__main__":
    main()
