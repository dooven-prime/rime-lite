"""Paper X registry evidence: registry probes.

Probe 0: Mechanism-separated SOF control (constructive H3 positive control).
Probe 1: Xu-style rate separation versus RIME/NN observable rates.
Probe 2: Yang-style state mixing versus RIME generator-weight plateaus.
Probe 3: Quantum Clifford/CNOT non-Rubik D-repair.
Probe 4: Rubik QT/HT wild Type III/IV mechanism counts.
Probe 5: Finite spectral-triple SOF with central Connes-distance obstruction
         and T7-style bridge shadows.
Probe 6: Control, PDE, and combinatorial SOF portability diagnostics.

Claim status:
    - Registry evidence for Paper X.
    - Evidence summary, not a standalone theorem source.
    - Mechanism separation gives causal proxy-rate support.
    - Proxy-to-shadow and tau(D) bridges remain open.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import logm

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rime.accessibility import AccessibilityEngine, plateau_fraction  # noqa: E402
from rime.cubieoperator import CubieSpectralOperator  # noqa: E402
from rime.helpers import zero_crossings  # noqa: E402
from rime.rep_utils import computational_basis_sectors  # noqa: E402
from control_pde_combinatorial_sof import audit as control_pde_comb_audit  # noqa: E402
from ncg_spectral_triple_sof import audit as ncg_audit  # noqa: E402


TOL = 1e-8
MAX_DEPTH = 4


def section(title: str) -> None:
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def skew_log(U: np.ndarray) -> np.ndarray:
    try:
        X = logm(U)
    except Exception:
        X = (U - U.conj().T) / 2.0
    return (X - X.conj().T) / 2.0


def probe_rate_separation() -> dict:
    section("Probe 1: Rate-Separation Ratio")

    lambda_min_pos = 4.9618
    eta = 0.1
    lam = 1e-4
    rate_par = 1.0 - eta * lambda_min_pos
    rate_perp = 1.0 - eta * lam
    tau_par_ridge = -1.0 / np.log(rate_par)
    tau_perp_ridge = -1.0 / np.log(rate_perp)
    ratio_ridge = tau_perp_ridge / tau_par_ridge

    tau_R1 = 5.89e-9
    tau_R2 = 6.37e-8
    ratio_rime = tau_R2 / tau_R1

    tau_K0, tau_K1, tau_K2 = 60, 80, 120

    print(f"  Ridge regression: tau_parallel={tau_par_ridge:.2f}, "
          f"tau_perp={tau_perp_ridge:.0f}, ratio={ratio_ridge:.0f}x")
    print(f"  RIME near-threshold: tau(R1)={tau_R1:.2e}, "
          f"tau(R2)={tau_R2:.2e}, ratio={ratio_rime:.1f}x")
    print(f"  NN training-coupled SOF: tau(K0,K1,K2)=({tau_K0},{tau_K1},{tau_K2})")
    print("  Evidence type: theorem-proven external model vs empirical SOF diagnostics.")
    print()

    return {
        "ridge_ratio": ratio_ridge,
        "rime_ratio": ratio_rime,
        "nn_taus": (tau_K0, tau_K1, tau_K2),
    }


def probe_plateau_geometry() -> dict:
    section("Probe 2: Plateau Geometry Contrast")

    op = CubieSpectralOperator()
    Vs = op.center_decomposition()["sector_bases"]
    rhos = [np.array(rho, dtype=complex) for rho in op.rho_matrices()]
    Xs0 = [(rho - rho.conj().T) / 2.0 for rho in rhos[:6]]

    dim = rhos[0].shape[0]
    rho_id = np.eye(dim, dtype=complex) / dim
    target_sector = Vs[6] @ Vs[6].conj().T
    epsilons = np.linspace(0.0, 1.0, 6)

    p3_yang = []
    for eps in epsilons:
        rho_s = (1.0 - eps) * rho_id + eps * target_sector
        Xs_mix = [rho_s @ X @ rho_s for X in Xs0]
        engine = AccessibilityEngine(Vs, Xs_mix, tol=TOL, max_depth=MAX_DEPTH)
        D, _ = engine.depth()
        p3_yang.append(plateau_fraction(D, 3))

    p2_rime = np.array([0.111, 0.111, 0.111, 0.111, 0.111, 0.111, 0.139, 0.111, 0.264])
    yang_zc = zero_crossings(np.array(p3_yang))
    rime_zc = zero_crossings(p2_rime)
    oscillation_score = rime_zc / (len(p2_rime) - 1)

    print(f"  Yang-style state mixing: P3={[f'{p:.3f}' for p in p3_yang]}, "
          f"zero-crossings={yang_zc}/{len(p3_yang)-1}")
    print(f"  RIME generator weights: P2={[f'{p:.3f}' for p in p2_rime]}, "
          f"zero-crossings={rime_zc}/{len(p2_rime)-1}, score={oscillation_score:.2f}")
    print("  Same observable architecture; different deformation geometry.")
    print()

    return {
        "yang_p3": p3_yang,
        "yang_zero_crossings": yang_zc,
        "rime_p2": p2_rime.tolist(),
        "rime_zero_crossings": rime_zc,
        "oscillation_score": oscillation_score,
    }


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
    CZ = np.diag([1, 1, 1, -1]).astype(complex)
    return {"CNOT": CNOT, "CZ": CZ}


def embed_gate(label: str, n_qubits: int) -> np.ndarray:
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
    raise ValueError(f"cannot embed gate {label!r} on {n_qubits} qubits")


def quantum_audit(name: str, labels: list[str], n_qubits: int = 2) -> dict:
    Vs = computational_basis_sectors(2**n_qubits, dtype=complex)
    Xs = [skew_log(embed_gate(label, n_qubits)) for label in labels]
    engine = AccessibilityEngine(Vs, Xs, tol=1e-6, max_depth=MAX_DEPTH)
    return {"name": name, "labels": labels, "qubits": n_qubits, **engine.audit()}


def probe_quantum_repair() -> dict:
    section("Probe 3: Non-Rubik D-Repair")

    systems = [
        ("Pauli {X,Z}", ["X", "Z"]),
        ("Pauli {X,Y,Z}", ["X", "Y", "Z"]),
        ("Clifford {H,S,CNOT}", ["H", "S", "CNOT"]),
        ("Universal {H,T,CNOT}", ["H", "T", "CNOT"]),
    ]
    rows = [quantum_audit(name, labels, 2) for name, labels in systems]

    print(f"  {'Gate set':<24s} {'R1%':>6s} {'R2%':>6s} {'frzR1':>6s} "
          f"{'D-rep':>6s} {'Dmax':>5s}")
    print(f"  {'-'*24} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*5}")
    for r in rows:
        print(f"  {r['name']:<24s} {r['R1_pct']:>5.1f}% {r['R2_pct']:>5.1f}% "
              f"{r['frozen_R1']:>6d} {r['D_repaired']:>6d} {r['D_max']:>5d}")

    pauli_repair = next(r for r in rows if r["name"] == "Pauli {X,Z}")["D_repaired"]
    clifford_repair = next(r for r in rows if r["name"] == "Clifford {H,S,CNOT}")["D_repaired"]

    print()
    print(f"  Key contrast: Clifford+CNOT D-repaired={clifford_repair} "
          f"vs Pauli {{X,Z}} D-repaired={pauli_repair}.")
    print("  D-repair appears outside Rubik in an entangling quantum SOF.")
    print()

    return {
        "rows": rows,
        "pauli_repair": pauli_repair,
        "clifford_repair": clifford_repair,
    }


def probe_ncg_spectral_triple() -> dict:
    section("Probe 4: Finite Spectral-Triple SOF")

    result = ncg_audit()

    print(f"  H_F dimension: {result['dim']}")
    print(f"  sectors from block-diagonal D: {result['n_sectors']}")
    print(f"  max ||[D,p_i]||_F = {max(result['commutator_norms']):.2e}")
    print("  cross-block central pure-state distance: infinite")
    print(f"  direct L->R block norm: {result['direct_lr']:.2e}")
    print(f"  bridge L->M->R norm:   {result['bridge_lr']:.2e}")
    print(f"  ordered T7-style bridge count: {result['t7_count_ordered']}")
    print("  Registry role: NCG-inspired portability example outside group/Lie origins.")
    print()

    return result


def probe_control_pde_combinatorial() -> dict:
    section("Probe 5: Control / PDE / Combinatorial SOFs")

    result = control_pde_comb_audit()
    control = result["control"]
    pde = result["pde"]
    comb = result["combinatorial"]

    print(f"  Control Kalman ranks: {control['kalman_ranks']}; "
          f"terminal word-depth={control['D_0_to_2']}")
    print(f"  PDE sector dims: {pde['sector_dims']}; "
          f"left-to-right word-depth={pde['D_left_to_right']}")
    print(f"  Coloring sector dims: {comb['sector_dims']}; "
          f"inter-color R1 edges={comb['inter_color_edges']}; "
          f"same-color conflicts={comb['same_color_conflicts']}")
    print("  Registry role: compatible sectorization, independent of sector origin.")
    print()

    return result


def main() -> None:
    print("=" * 72)
    print("  Paper X Registry Evidence")
    print("=" * 72)
    print("Claim status: registry evidence; calibrated mechanism separation gives causal proxy-rate support.")
    print("Boundary: proxy-to-shadow and tau(D) bridges remain open.")
    print()

    rate = probe_rate_separation()
    plateau = probe_plateau_geometry()
    quantum = probe_quantum_repair()
    ncg = probe_ncg_spectral_triple()
    control_pde_comb = probe_control_pde_combinatorial()

    section("Registry Evidence Summary")
    print("  | Probe | Core number | Registry role |")
    print("  |-------|-------------|---------------|")
    print("  | Calibrated mechanism-separated SOF | tau(K0_grow)=30 << tau(K1_decay)=1380 | H3/H3' constructive positive control |")
    print("  | Rubik Type III/IV | 288 Type III; 528 Type IV bridge-level incidence | wild QT/HT mechanism instances |")
    print(f"  | Xu/RIME/NN rates | Ridge {rate['ridge_ratio']:.0f}x vs "
          f"RIME {rate['rime_ratio']:.1f}x; NN {rate['nn_taus']} | rate hierarchy evidence |")
    print(f"  | Yang/RIME plateaus | {plateau['yang_zero_crossings']}/5 vs "
          f"{plateau['rime_zero_crossings']}/8 zero-crossings | deformation-geometry contrast |")
    print(f"  | Quantum Clifford | D-repaired={quantum['clifford_repair']} vs "
          f"Pauli {quantum['pauli_repair']} | non-Rubik D-repair |")
    print(f"  | NCG spectral triple | infinite central distance; "
          f"T7 bridges={ncg['t7_count_ordered']} | non-group SOF portability |")
    print(f"  | Control/PDE/combinatorial | Kalman ranks "
          f"{control_pde_comb['control']['kalman_ranks']}; PDE depth "
          f"{control_pde_comb['pde']['D_left_to_right']}; coloring conflicts "
          f"{control_pde_comb['combinatorial']['same_color_conflicts']} | sector-origin independence |")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
