"""Paper VI support script: linearized commutator map at canonical point.

Status: numerical linearized commutativity-kernel certificate at the
full-generator point w = (1,...,1).

This script computes the Jacobian of the commutator map
    C_comm(w) = [Q_T(w), H_T(w)]
at w = 1, where Q_T(w) and H_T(w) are the weighted QT/HT averages.

Derivation
----------
At w = 1, Q_T(1) = QT_all and H_T(1) = HT_all have a machine-zero
commutator in the declared complex128 realization. Exact commutation is not
used in the derivative formula.

The weighted averages and their derivatives at w = 1:

    Q_T(w) = sum_{g in QT} w_g rho(g) / sum_{g in QT} w_g
    H_T(w) = sum_{g in HT} w_g rho(g) / sum_{g in HT} w_g

For k in QT:
    dQ_T/dw_k |_{w=1} = (rho(g_k) - QT_all) / 12
    dH_T/dw_k |_{w=1} = 0

For k in HT:
    dQ_T/dw_k |_{w=1} = 0
    dH_T/dw_k |_{w=1} = (rho(g_k) - HT_all) / 6

The commutator derivative:
    dC_comm/dw_k = [dQ_T/dw_k, H_T] + [Q_T, dH_T/dw_k]

At w = 1:
    For k in QT:
        J_k = ([rho(g_k), HT_all] - [QT_all, HT_all]) / 12
    For k in HT:
        J_k = ([QT_all, rho(g_k)] - [QT_all, HT_all]) / 6

These expressions simplify to the shorter commutator formulas only if exact
commutation is separately certified.

The linearized commutativity kernel at w=1 is the kernel of the map
    delta_w |-> sum_k delta_w_k * J_k.

Without a separate constant-rank or integrability argument, this kernel is not
identified with the tangent space of a smooth commutativity manifold.

This script:
1. Computes all 18 Jacobian matrices J_k.
2. Encodes every full complex matrix by all real and imaginary entries and
   computes the SVD.
3. Reports the linearized kernel basis. Integrability into the exact zero set
   and preservation of normality are separate audits.
4. Compares kernel directions with the hand-picked symmetry directions
   from archived earlier commutativity-wall scans.
5. Verifies that first-order predictions match numerical norms.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import argparse
import os
import numpy as np

from rime.cubie import CubieMove


np.random.seed(42)
TOL_SVD = 1e-10
EXPECTED_RANK = 11
EXPECTED_NULLITY = 7
EXPECTED_QT_JAC_NORM = 0.309320
EXPECTED_HT_JAC_NORM = 0.426730
EXPECTED_INSIDE = {
    "all QT symmetric",
    "all HT symmetric",
    "axis-0 QT symmetric",
    "axis-1 QT symmetric",
    "axis-2 QT symmetric",
}
EXPECTED_SINGULAR_GROUPS = [
    (0.585314, 3),
    (0.532870, 3),
    (0.346944, 2),
    (0.200308, 3),
    (0.0, 7),
]

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
)
LOG_PATH = os.path.join(OUT_DIR, "_paper6_tangent_commutator_map.txt")


def write_snapshot_log(lines: list[str]) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def singular_group_snapshot(s: np.ndarray) -> list[tuple[float, int]]:
    rounded = [round(float(x), 6) if x > 1e-10 else 0.0 for x in s]
    groups: list[tuple[float, int]] = []
    for value in rounded:
        if not groups or groups[-1][0] != value:
            groups.append((value, 1))
        else:
            groups[-1] = (groups[-1][0], groups[-1][1] + 1)
    return groups


def prim_data() -> tuple[list[tuple[int, int, int]], list[np.ndarray]]:
    keys = list(CubieMove.prim_moves.keys())
    rhos = [CubieMove.prim_moves[key].rho().astype(np.complex128) for key in keys]
    return keys, rhos


def qt_ht_all(rhos: list[np.ndarray], keys: list[tuple[int, int, int]]):
    """Compute QT_all and HT_all at w=1."""
    qt_idx = [i for i, k in enumerate(keys) if k[2] != 2]
    ht_idx = [i for i, k in enumerate(keys) if k[2] == 2]
    QT = sum(rhos[i] for i in qt_idx) / len(qt_idx)
    HT = sum(rhos[i] for i in ht_idx) / len(ht_idx)
    return QT, HT, qt_idx, ht_idx


def jacobian_matrices(
    rhos: list[np.ndarray],
    keys: list[tuple[int, int, int]],
    QT: np.ndarray,
    HT: np.ndarray,
    qt_idx: list[int],
    ht_idx: list[int],
) -> tuple[list[np.ndarray], list[str]]:
    """Compute J_k = dC_comm/dw_k |_{w=1} for each generator.

    For k in QT:
        J_k = ([rho(g_k), HT_all] - [QT_all, HT_all]) / 12
    For k in HT:
        J_k = ([QT_all, rho(g_k)] - [QT_all, HT_all]) / 6
    """
    J = []
    labels = []
    baseline_commutator = QT @ HT - HT @ QT
    for k in range(len(keys)):
        if k in qt_idx:
            dqt = (rhos[k] - QT) / len(qt_idx)
            Jk = dqt @ HT - HT @ dqt
            kind = "QT"
        else:
            dht = (rhos[k] - HT) / len(ht_idx)
            Jk = QT @ dht - dht @ QT
            kind = "HT"
        # This assertion protects the unconditional normalized derivative.
        if k in qt_idx:
            expanded = (
                rhos[k] @ HT - HT @ rhos[k] - baseline_commutator
            ) / len(qt_idx)
        else:
            expanded = (
                QT @ rhos[k] - rhos[k] @ QT - baseline_commutator
            ) / len(ht_idx)
        assert np.linalg.norm(Jk - expanded, "fro") < 1e-14
        J.append(Jk)
        labels.append(f"{CubieMove.move_label(keys[k])}({kind})")
    return J, labels


def flatten_complex_real(matrices: list[np.ndarray]) -> np.ndarray:
    """Encode full complex matrices by all real and imaginary entries."""
    return np.column_stack(
        [np.concatenate([matrix.real.ravel(), matrix.imag.ravel()]) for matrix in matrices]
    )


def kernel_analysis(flat_J: np.ndarray, tol: float = TOL_SVD):
    """SVD analysis: rank, singular values, kernel basis."""
    U, s, Vt = np.linalg.svd(flat_J, full_matrices=False)

    rank = int(np.sum(s > tol * max(s[0], 1.0)))
    nullity = len(s) - rank

    # Kernel basis from rows of Vt corresponding to zero singular values
    kernel_basis = Vt[rank:, :] if nullity > 0 else np.zeros((0, flat_J.shape[1]))

    return {
        "singular_values": s,
        "rank": rank,
        "nullity": nullity,
        "kernel_basis": kernel_basis,
        "Vt": Vt,
    }


def symmetry_directions(keys: list[tuple[int, int, int]]) -> dict[str, np.ndarray]:
    """Build the hand-picked symmetry directions as weight vectors."""
    m = len(keys)
    directions = {}

    # All QT weights moved together (decrease all QT)
    v = np.zeros(m)
    for i, k in enumerate(keys):
        if k[2] != 2:
            v[i] = -1.0
    directions["all QT symmetric"] = v

    # All HT weights moved together
    v = np.zeros(m)
    for i, k in enumerate(keys):
        if k[2] == 2:
            v[i] = -1.0
    directions["all HT symmetric"] = v

    # Per-axis QT symmetric
    for axis in range(3):
        v = np.zeros(m)
        for i, k in enumerate(keys):
            if k[0] == axis and k[2] != 2:
                v[i] = -1.0
        directions[f"axis-{axis} QT symmetric"] = v

    # Per-axis HT symmetric
    for axis in range(3):
        v = np.zeros(m)
        for i, k in enumerate(keys):
            if k[0] == axis and k[2] == 2:
                v[i] = -1.0
        directions[f"axis-{axis} HT symmetric"] = v

    # Single-coordinate deletions
    for i, k in enumerate(keys):
        v = np.zeros(m)
        v[i] = -1.0
        directions[f"delete {CubieMove.move_label(k)}"] = v

    return directions


def project_onto_kernel(direction: np.ndarray, kernel_basis: np.ndarray) -> tuple[float, float]:
    """Compute norm of direction, norm in kernel, and fraction in kernel."""
    v = direction.astype(float)
    v = v / np.linalg.norm(v) if np.linalg.norm(v) > 1e-15 else v
    if kernel_basis.shape[0] == 0:
        return 0.0, 0.0
    # Project onto kernel: P_ker(v) = K^T K v where K has orthonormal rows
    proj = kernel_basis.T @ (kernel_basis @ v)
    in_kernel = np.linalg.norm(proj)
    residual = np.linalg.norm(v - proj)
    return float(in_kernel), float(residual)


def verify_first_order(
    keys: list[tuple[int, int, int]],
    rhos: list[np.ndarray],
    J_list: list[np.ndarray],
    QT: np.ndarray,
    HT: np.ndarray,
    direction: np.ndarray,
    eps: float = 1e-3,
) -> dict:
    """Verify that the first-order approximation matches the actual commutator."""
    base = np.ones(len(keys))
    w = base + eps * direction / np.linalg.norm(direction)

    qt_idx = [i for i, k in enumerate(keys) if k[2] != 2]
    ht_idx = [i for i, k in enumerate(keys) if k[2] == 2]

    qt_w = sum(w[i] * rhos[i] for i in qt_idx) / sum(w[i] for i in qt_idx)
    ht_w = sum(w[i] * rhos[i] for i in ht_idx) / sum(w[i] for i in ht_idx)
    actual = qt_w @ ht_w - ht_w @ qt_w
    actual_norm = float(np.linalg.norm(actual, "fro"))

    # First-order prediction
    v = direction / np.linalg.norm(direction)
    predicted = sum(v[i] * J_list[i] for i in range(len(J_list))) * eps
    predicted_norm = float(np.linalg.norm(predicted, "fro"))

    # Relative error
    if actual_norm > 1e-15:
        rel_error = abs(actual_norm - predicted_norm) / actual_norm
    else:
        rel_error = 0.0 if predicted_norm < 1e-15 else float("inf")

    return {
        "eps": eps,
        "actual_norm": actual_norm,
        "predicted_norm": predicted_norm,
        "rel_error": rel_error,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute the Paper VI linearized commutator-map snapshot."
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help=(
            "Run expensive rank-stability and nonlinear-kernel searches. "
            "The default run is the fast stable snapshot."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    keys, rhos = prim_data()
    QT, HT, qt_idx, ht_idx = qt_ht_all(rhos, keys)
    m = len(keys)
    N = rhos[0].shape[0]

    # Verify baseline commutativity
    base_comm = np.linalg.norm(QT @ HT - HT @ QT, "fro")
    print("=" * 72)
    print("Paper VI: Linearized Commutator Map at Canonical Point")
    print("=" * 72)
    print(f"Representation dimension: {N}")
    print(f"Generators: {m} ({len(qt_idx)} QT + {len(ht_idx)} HT)")
    print(f"Baseline ||[QT_all, HT_all]||_F = {base_comm:.3e}")
    assert base_comm < 1e-10
    print()

    # Step 1: Compute Jacobian matrices
    J_list, labels = jacobian_matrices(rhos, keys, QT, HT, qt_idx, ht_idx)

    print("Individual Jacobian norms ||J_k||_F:")
    jac_norms = []
    for k in range(m):
        norm_k = float(np.linalg.norm(J_list[k], "fro"))
        jac_norms.append(norm_k)
        print(f"  [{k:02d}] {labels[k]:>20s}: {norm_k:.6f}")
    qt_norms = [jac_norms[i] for i in qt_idx]
    ht_norms = [jac_norms[i] for i in ht_idx]
    qt_skew_residuals = [
        float(np.linalg.norm(J_list[i] + J_list[i].conj().T, "fro"))
        for i in qt_idx
    ]
    ht_skew_residuals = [
        float(np.linalg.norm(J_list[i] + J_list[i].conj().T, "fro"))
        for i in ht_idx
    ]
    print(
        "Jacobian skew-Hermitian residuals: "
        f"QT={max(qt_skew_residuals):.6f}, HT={max(ht_skew_residuals):.3e}"
    )
    print("Full complex encoding is required because the QT Jacobians are not skew-Hermitian.")
    print()

    # Step 2: Flatten and SVD
    flat_J = flatten_complex_real(J_list)
    print(f"Flattened Jacobian: {flat_J.shape[0]} real rows x {flat_J.shape[1]} columns")
    svd = kernel_analysis(flat_J)
    print(f"Singular value range: [{svd['singular_values'][-1]:.3e}, {svd['singular_values'][0]:.3f}]")
    print(f"Rank: {svd['rank']}")
    print(f"Nullity (dim ker dC_comm): {svd['nullity']}")
    smallest_retained = float(svd["singular_values"][svd["rank"] - 1])
    largest_discarded = float(svd["singular_values"][svd["rank"]])
    print(f"Smallest retained singular value: {smallest_retained:.12e}")
    print(f"Largest discarded singular value: {largest_discarded:.12e}")
    print(
        "Retained/discarded gap ratio: "
        f"{smallest_retained / max(largest_discarded, np.finfo(float).tiny):.3e}"
    )
    singular_groups = singular_group_snapshot(svd["singular_values"])
    print(f"Singular value groups: {singular_groups}")
    print()

    # Print singular values
    print("Singular values (top 20, bottom 5):")
    for i in range(min(20, len(svd["singular_values"]))):
        print(f"  s[{i:02d}] = {svd['singular_values'][i]:.6f}")
    if len(svd["singular_values"]) > 20:
        print(f"  ...")
        for i in range(max(0, len(svd["singular_values"]) - 5), len(svd["singular_values"])):
            print(f"  s[{i:02d}] = {svd['singular_values'][i]:.3e}")
    print()

    # Step 3: Analyze symmetry directions
    sym_dirs = symmetry_directions(keys)
    kernel = svd["kernel_basis"]

    print("Hand-picked directions projected onto ker dC_comm:")
    print(f"  {'Direction':<30s} {'In kernel':>10s} {'Residual':>10s} {'Status'}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*20}")

    inside = []
    outside = []
    for name, v in sym_dirs.items():
        in_k, res = project_onto_kernel(v, kernel)
        status = "IN kernel" if res < 1e-10 else f"residual={res:.3e}"
        print(f"  {name:<30s} {in_k:>10.6f} {res:>10.6f} {status}")
        if res < 1e-10:
            inside.append(name)
        else:
            outside.append(name)

    print()
    print(f"Directions in ker dC_comm: {inside}")
    print(f"Directions outside ker dC_comm: {outside}")
    print()

    # Step 4: Verify first-order predictions on a few key directions
    print("First-order verification (eps=1e-3):")
    print(f"  {'Direction':<30s} {'Actual':>12s} {'Predicted':>12s} {'Rel err':>10s}")
    print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*10}")

    first_order_checks = {}
    for name in ["all QT symmetric", "all HT symmetric", "delete R", "delete R2"]:
        if name not in sym_dirs:
            continue
        v = sym_dirs[name]
        result = verify_first_order(keys, rhos, J_list, QT, HT, v)
        first_order_checks[name] = result
        print(
            f"  {name:<30s} {result['actual_norm']:>12.6f} "
            f"{result['predicted_norm']:>12.6f} {result['rel_error']:>10.6f}"
        )
    print()

    # Step 5: Characterize the kernel 鈥?which linear combinations?
    if svd["nullity"] > 0:
        print("Kernel basis vectors (rows of K, each is a weight direction):")
        K = svd["kernel_basis"]
        for r in range(K.shape[0]):
            row = K[r, :]
            # Find dominant components
            idx = np.argsort(-np.abs(row))
            components = []
            for i in idx[:6]:
                if abs(row[i]) > 0.01:
                    components.append(f"{labels[i]}={row[i]:+.4f}")
            print(f"  kernel[{r}]: {'  '.join(components)}")
        print()

        # Check which hand-picked directions are linear combinations of kernel vectors
        print("Reconstruction of symmetry directions from kernel basis:")
        for name in inside:
            v = sym_dirs[name]
            v_norm = v / np.linalg.norm(v)
            coeffs = K @ v_norm
            recon = K.T @ coeffs
            recon_err = np.linalg.norm(v_norm - recon)
            print(f"  {name}: reconstruction error = {recon_err:.3e}")
        print()

    # Step 6: Codimension check 鈥?compare with numerical rank from earlier work
    # From archived commutativity-wall scans:
    # - single QT deletion: rank 96
    # - single HT deletion: rank 88
    # Full complex-real encoding has 2*N*N rows. Only the 18-column rank and
    # kernel are interpreted; no skew-Hermitian ambient-space assumption is made.

    print("Linearized summary:")
    print(f"  Total weight space dim: {m}")
    print(f"  dim ker dC_comm: {svd['nullity']}")
    print(f"  rank dC_comm: {svd['rank']}")
    print("  No smooth-manifold or nonlinear-integrability conclusion is inferred.")
    print()

    # Step 7: Cross-check with the known symmetry pattern
    # From earlier experiments:
    # - "all QT symmetric" is inside Sigma_comm on the tested nonlinear family
    # - "all HT symmetric" is inside Sigma_comm on the tested nonlinear family
    # - axis-i QT symmetric: inside
    # - axis-i HT symmetric: leaves Sigma_comm (rank 52)
    # - single deletions: all leave Sigma_comm

    expected_inside = EXPECTED_INSIDE
    found_inside = {name for name in inside if name in expected_inside}
    print(f"Expected inside ker dC_comm: {sorted(expected_inside)}")
    print(f"Found inside ker dC_comm: {sorted(found_inside)}")

    if found_inside == expected_inside:
        print("[OK] All expected symmetry directions confirmed in ker dC_comm.")
    else:
        missing = expected_inside - found_inside
        extra = found_inside - expected_inside
        if missing:
            print(f"[WARN] Missing from kernel: {missing}")
        if extra:
            print(f"[NOTE] Extra in kernel: {extra}")

    # Verify that all single-coordinate deletions leave Sigma_comm
    single_del_inside = [name for name in inside if name.startswith("delete ")]
    if single_del_inside:
        print(f"[WARN] Single deletions in kernel: {single_del_inside}")
    else:
        print("[OK] No single-coordinate deletions are in ker dC_comm.")

    # Assertions for the linearized computational certificate
    assert svd["rank"] == EXPECTED_RANK, svd["rank"]
    assert svd["nullity"] == EXPECTED_NULLITY, svd["nullity"]
    assert smallest_retained > 1e-2
    assert largest_discarded < 1e-12
    assert singular_groups == EXPECTED_SINGULAR_GROUPS, singular_groups
    assert all(abs(norm - EXPECTED_QT_JAC_NORM) < 5e-7 for norm in qt_norms), qt_norms
    assert all(abs(norm - EXPECTED_HT_JAC_NORM) < 5e-7 for norm in ht_norms), ht_norms
    assert all(res < 1e-10 for name, (_, res) in [
        (n, project_onto_kernel(sym_dirs[n], kernel)) for n in expected_inside
    ]), "Expected symmetry directions should be in kernel"
    assert found_inside == expected_inside, found_inside
    assert not single_del_inside, single_del_inside
    assert first_order_checks["delete R"]["rel_error"] < 1e-3
    assert first_order_checks["delete R2"]["rel_error"] < 1e-3

    if args.deep:
        # Gap Closure 1: Local rank stability on Sigma_comm
        print("=" * 72)
        print("Gap Closure 1: Local Rank Stability on Sigma_comm")
        print("=" * 72)

        K = svd["kernel_basis"]
        rank_stable = True
        for trial in range(10):
            coeffs = np.random.randn(K.shape[0])
            v = K.T @ coeffs
            v = v / np.linalg.norm(v)
            for eps in [0.01, 0.1, 0.5, 1.0]:
                w = np.ones(m) + eps * v
                W_QT = sum(w[i] for i in qt_idx)
                W_HT = sum(w[i] for i in ht_idx)
                QT_w = sum(w[i] * rhos[i] for i in qt_idx) / W_QT
                HT_w = sum(w[i] * rhos[i] for i in ht_idx) / W_HT
                Jw = []
                for k in range(m):
                    if k in qt_idx:
                        Jw.append((rhos[k] @ HT_w - HT_w @ rhos[k]) / W_QT)
                    else:
                        Jw.append((QT_w @ rhos[k] - rhos[k] @ QT_w) / W_HT)
                flat_w = flatten_complex_real(Jw)
                _, sw, _ = np.linalg.svd(flat_w, full_matrices=False)
                rank_w = int(np.sum(sw > 1e-10 * sw[0]))
                if rank_w != EXPECTED_RANK:
                    print(f"  RANK JUMP: trial={trial}, eps={eps:.2f}, rank={rank_w}")
                    rank_stable = False

        if rank_stable:
            print(f"  All 10 kernel dirs x 4 eps values: rank = {EXPECTED_RANK}")
            print("  [PASS] Rank stability confirmed")
        assert rank_stable

        # Gap Closure 2: No nonlinear kernel contributions
        print()
        print("=" * 72)
        print("Gap Closure 2: Nonlinear Kernel Search")
        print("=" * 72)

        n_dirs = 200
        eps_grid = np.logspace(-6, np.log10(0.5), 500)
        nonlinear_found = 0

        for _ in range(n_dirs):
            v_raw = np.random.randn(m)
            v_raw = v_raw / np.linalg.norm(v_raw)
            v_trans = v_raw - K.T @ (K @ v_raw)
            trans_frac = np.linalg.norm(v_trans)

            min_norm = float("inf")
            for eps in eps_grid:
                w = np.ones(m) + eps * v_raw
                W_QT = sum(w[i] for i in qt_idx)
                W_HT = sum(w[i] for i in ht_idx)
                QT_w = sum(w[i] * rhos[i] for i in qt_idx) / W_QT
                HT_w = sum(w[i] * rhos[i] for i in ht_idx) / W_HT
                comm = QT_w @ HT_w - HT_w @ QT_w
                c_norm = float(np.linalg.norm(comm, "fro"))
                if c_norm < min_norm:
                    min_norm = c_norm

            if min_norm < 1e-13 and trans_frac > 0.01:
                nonlinear_found += 1

        print(f"  {n_dirs} random directions x 500 eps-steps: {nonlinear_found} nonlinear hits")
        print("  [PASS] No nonlinear kernel emergence")
        assert nonlinear_found == 0

        # Gap Closure 2b: Linearity check
        print()
        print("Linearity check (ratio = actual / linear_prediction at eps=0.01):")
        ratios = []
        for _ in range(50):
            v_raw = np.random.randn(m)
            v_raw = v_raw / np.linalg.norm(v_raw)
            v_trans = v_raw - K.T @ (K @ v_raw)
            if np.linalg.norm(v_trans) < 0.3:
                continue
            Jv = sum(v_raw[i] * J_list[i] for i in range(m))
            pred = 0.01 * float(np.linalg.norm(Jv, "fro"))
            w = np.ones(m) + 0.01 * v_raw
            W_QT = sum(w[i] for i in qt_idx)
            W_HT = sum(w[i] for i in ht_idx)
            QT_w = sum(w[i] * rhos[i] for i in qt_idx) / W_QT
            HT_w = sum(w[i] * rhos[i] for i in ht_idx) / W_HT
            actual = float(np.linalg.norm(QT_w @ HT_w - HT_w @ QT_w, "fro"))
            if actual > 1e-15:
                ratios.append(actual / pred)
        if ratios:
            print(f"  Mean ratio: {np.mean(ratios):.6f}, "
                  f"min: {np.min(ratios):.6f}, max: {np.max(ratios):.6f}")
            assert abs(np.mean(ratios) - 1.0) < 0.01
        print("  [PASS] Commutator map is linear to <1% at eps=0.01")
    else:
        print("[fast snapshot] Deep gap-closure checks skipped; run with --deep.")
    write_snapshot_log([
        "Paper VI linearized commutator map snapshot",
        f"baseline_comm_norm={base_comm:.6e}",
        f"rank={svd['rank']}",
        f"nullity={svd['nullity']}",
        f"smallest_retained={smallest_retained:.12e}",
        f"largest_discarded={largest_discarded:.12e}",
        f"singular_groups={singular_groups}",
        f"qt_jacobian_norm={qt_norms[0]:.6f}",
        f"ht_jacobian_norm={ht_norms[0]:.6f}",
        f"qt_skew_residual={max(qt_skew_residuals):.6e}",
        f"ht_skew_residual={max(ht_skew_residuals):.6e}",
        f"inside_kernel={sorted(inside)}",
        f"outside_count={len(outside)}",
        f"delete_R_rel_error={first_order_checks['delete R']['rel_error']:.6e}",
        f"delete_R2_rel_error={first_order_checks['delete R2']['rel_error']:.6e}",
    ])
    print("\n[snapshot OK: linearized commutativity kernel computed]")


if __name__ == "__main__":
    main()
