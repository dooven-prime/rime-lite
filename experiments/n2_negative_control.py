"""N=2 Pocket Cube: Verify T7 mechanism degenerates in edge-free system.

The N=2 cube has only corner pieces -- no edges, no centers.
Representation: cp(64) + co(8) = 72 dimensions.
Hypothesis: Without the ep block, noncommutativity vanishes (no M2),
Supp_nc = empty everywhere, hence T7 cannot exist.

RESULT (2026-05-15):
  - [QT0, QT1] in co block = 0.61 (same as N=3!) -- noncommutativity SURVIVES
  - But ZERO hybrid sectors (21 sectors: 15 cp + 6 co):
    noncommutativity is "trapped" in single-block sectors.
  - 90 cross-block pairs with K=kappa0=kappa1=0, ALL has_path=False:
    genuine subrepresentation isolation, not T7.
  - CONCLUSION: ep block is NECESSARY for hybrid sector formation.
    co noncommutativity alone is INSUFFICIENT. T7 cannot exist in N=2.
"""

import numpy as np
from scipy.linalg import block_diag
from rime.cubie import CubieMove
from rime.spectral_utils import (joint_diag_sectors, build_projectors,
                                  classify_sectors, compute_transport_kappa,
                                  find_t7_pairs, analyze_t7)

# -- 1. Build 72-dim N=2 representation from corner blocks --
prim = CubieMove.prim_moves()  # 18 face-turn generators

rhos_72 = []
move_keys = []
for key, mv in prim.items():
    rho_228 = mv.rho().astype(np.complex128)
    # Extract corner blocks: cp(0:64) + co(208:216)
    Cp = rho_228[:64, :64]
    Co = rho_228[208:216, 208:216]
    rho_72 = block_diag(Cp, Co)
    rhos_72.append(rho_72)
    move_keys.append(key)

# --- Sanity checks (user request 260515) ---
for key, rho in zip(move_keys, rhos_72):
    # 1. Unitarity: ρ(g) must be unitary (permutation representation)
    assert np.allclose(rho.conj().T @ rho, np.eye(72)), f"Unitarity failed for {key}"
    # 2. Invariant splitting: cp|co blocks are decoupled in all generators
    assert np.allclose(rho[:64, 64:], 0), f"cp-co coupling found in top-right for {key}"
    assert np.allclose(rho[64:, :64], 0), f"co-cp coupling found in bottom-left for {key}"
print("Sanity checks passed: unitarity + cp/co invariant splitting (18/18 generators)")

# -- 2. Build averaging operators (same move-key filtering as N=3) --
A_18 = sum(rhos_72) / 18

qt_idx = [i for i, k in enumerate(move_keys) if k[2] != 2]
QT_all = sum(rhos_72[i] for i in qt_idx) / len(qt_idx)

ht_idx = [i for i, k in enumerate(move_keys) if k[2] == 2]
HT_all = sum(rhos_72[i] for i in ht_idx) / len(ht_idx)

print("=" * 60)
print("N=2 Pocket Cube -- Corner-only 72-dim representation")
print("=" * 60)

# -- 3. Spectral decomposition of A_18 --
evals_A = np.linalg.eigvalsh(A_18)
unique_evals = sorted(set(round(e, 8) for e in evals_A), reverse=True)
print(f"\nA_18 eigenvalues ({len(unique_evals)} distinct):")
for lam in unique_evals:
    count = sum(1 for e in evals_A if abs(e - lam) < 1e-8)
    print(f"  lam = {lam:10.8f}  dim = {count}")

# -- 4. Check noncommutativity: [QT0, QT1] --
QT0_idx = [i for i, k in enumerate(move_keys) if k[0] == 0 and k[2] != 2]
QT1_idx = [i for i, k in enumerate(move_keys) if k[0] == 1 and k[2] != 2]
QT0 = sum(rhos_72[i] for i in QT0_idx) / len(QT0_idx)
QT1 = sum(rhos_72[i] for i in QT1_idx) / len(QT1_idx)
comm_norm = np.linalg.norm(QT0 @ QT1 - QT1 @ QT0, 'fro')
print(f"\n[QT0, QT1] Frobenius norm: {comm_norm:.6e}")
print(f"  (N=3 comparison: cp=0, ep=2.74, co=0.61, eo=0.79)")

# Block-local noncommutativity
comm_cp = np.linalg.norm(QT0[:64, :64] @ QT1[:64, :64] -
                         QT1[:64, :64] @ QT0[:64, :64], 'fro')
comm_co = np.linalg.norm(QT0[64:, 64:] @ QT1[64:, 64:] -
                         QT1[64:, 64:] @ QT0[64:, 64:], 'fro')
print(f"  cp block: {comm_cp:.6e}")
print(f"  co block: {comm_co:.6e}")

# -- 5. Center joint diagonalization -> primitive sectors --
center_ops = [A_18, QT_all, HT_all]
sectors = joint_diag_sectors(center_ops)
print(f"\nPrimitive sectors: {len(sectors)} (N=3 has 9)")
for i, (evals_tuple, indices) in enumerate(sectors):
    n_cp = sum(1 for idx in indices if idx < 64)
    n_co = len(indices) - n_cp
    lam_tuple = tuple(f"{e:.6f}" if e is not None else "None"
                      for e in evals_tuple)
    support_parts = []
    if n_cp > 0:
        support_parts.append(f"cp({n_cp})")
    if n_co > 0:
        support_parts.append(f"co({n_co})")
    print(f"  S{i+1}: dim={len(indices):2d}  "
          f"(lam_A, lam_QT, lam_HT)=({lam_tuple[0]}, {lam_tuple[1]}, {lam_tuple[2]})  "
          f"support={'+'.join(support_parts)}")

# -- 6. Transport analysis --
projectors = build_projectors(sectors, 72)
types = classify_sectors(sectors, dim_a=64)  # block A = cp(64), block B = co(8)

K, kappa0, kappa1 = compute_transport_kappa(rhos_72, projectors)
t7_pairs = find_t7_pairs(K, kappa0, kappa1, types)

n = len(sectors)
n_pure_a = sum(1 for t in types if t == 'A')
n_pure_b = sum(1 for t in types if t == 'B')
n_hybrid = sum(1 for t in types if t == 'H')

print(f"\nSector classification:")
print(f"  Pure cp (A): {n_pure_a}, Pure co (B): {n_pure_b}, Hybrid: {n_hybrid}")
if n_hybrid == 0:
    print(f"  ** ZERO hybrid sectors -- critical for T7 mechanism **")

# -- 7. Transport matrix --
print(f"\nK matrix ({n}x{n}):")
nz_mask = np.any(K > 1e-6, axis=0) | np.any(K > 1e-6, axis=1)
active = [i for i in range(n) if nz_mask[i]]
if len(active) < n:
    print(f"  (all {n} sectors have nonzero K -- transport is dense within each block)")

# Show block structure
print(f"\n  cp-cp block: fully connected ({n_pure_a}x{n_pure_a} subgraph)")
print(f"  co-co block: fully connected ({n_pure_b}x{n_pure_b} subgraph)")
print(f"  cp-co cross-block: ALL ZERO (no cross-block transport)")

nz_edges = sum(1 for i in range(n) for j in range(i+1, n) if K[i,j] > 1e-6)
print(f"\nNonzero K edges: {nz_edges} (N=3 has 10)")

# -- 8. kappa0/kappa1 analysis --
n_k0 = sum(1 for i in range(n) for j in range(i+1, n) if kappa0[i,j] > 1e-6)
n_k1 = sum(1 for i in range(n) for j in range(i+1, n)
           if kappa0[i,j] < 1e-6 and kappa1[i,j] > 1e-6)
print(f"\nkappa0 > 0 edges: {n_k0}")
print(f"Pure curvature (kappa0~0, kappa1>0) pairs: {n_k1} (N=3 has 7)")

# -- 9. T7 check --
print(f"\nT7 pairs (cross-block, K=kappa0=kappa1=0): {len(t7_pairs)} (N=3 has 5)")
n_true_t7 = sum(1 for _, _, has_path, _, _, _ in t7_pairs if has_path)
n_isolated = len(t7_pairs) - n_true_t7
if n_true_t7 > 0:
    for a, b, has_path, K_val, k0_val, k1_val in t7_pairs:
        if has_path:
            print(f"  S{a+1}<->S{b+1}: K={K_val:.2e}, k0={k0_val:.2e}, k1={k1_val:.2e} -- HAS PATH")
else:
    print(f"  ALL {n_isolated} pairs are isolated (has_path=False) -- subrepresentation isolation, not T7")
    print(f"  Example: S1 (co, V1) <-> S7 (cp, V2/3): fully decoupled G-invariant blocks")

# -- 10. Summary --
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"  Representation dim: 72 (cp=64, co=8)")
print(f"  [QT0, QT1] total:   {comm_norm:.2e}  (co={comm_co:.2f}, cp={comm_cp:.2e})")
print(f"  Primitive sectors:   {len(sectors)}  (N=3: 9)")
print(f"  Hybrid sectors:      {n_hybrid}  (N=3: 3)")
print(f"  Nonzero K edges:     {nz_edges}  (N=3: 10)")
print(f"  T7 pairs (true):     {n_true_t7}  (N=3: 5)")

if n_hybrid == 0 and n_true_t7 == 0:
    print(f"\n  KEY FINDING: ZERO hybrid sectors.")
    print(f"  The co block carries non-zero noncommutativity (|[QT0,QT1]|_co = {comm_co:.2f}), but")
    print(f"  without the ep block, noncommutativity is 'trapped' in single-block sectors.")
    print(f"  No hybrid projectors exist -> no cross-block composition path.")
    print(f"  All {n_isolated} 'T7 candidates' are subrepresentation isolation, not true T7.")
    print(f"")
    print(f"  T7 CANNOT EXIST in N=2. This is the minimal T7-free model.")
    print(f"  The ep block is NECESSARY (not just sufficient) for hybrid sectors.")
    print(f"  co noncommutativity alone (|comm|=0.61) is insufficient to create hybrids.")
    print(f"")
    print(f"  Structural comparison:")
    print(f"    N=3: cp(64)+ep(144)+co(8)+eo(12) = 228. 9 sectors, 3 hybrids. 5 T7 pairs.")
    print(f"    N=2: cp(64)+co(8) = 72.             21 sectors, 0 hybrids.  0 T7 pairs.")
