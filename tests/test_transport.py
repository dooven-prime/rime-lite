"""Theorem verification:
  - K_ij symmetry: transport tensor is undirected
  - S6 ≡ primary transport hub (deg ≥ 4); S1 ≡ isolated
  - T7 Theorem: existence of cross-block sector pairs with
    K = κ₀ = κ₁ = 0 yet reachable via 2-step discrete composition
    → discrete/continuous accessibility split
  - N=2 negative control: zero T7 pairs, zero hybrid sectors
    → T7 is N=3-specific, not a generic artifact

Paper: Paper II Sec 6 / Paper III (Transport topology & T7)
Invariant level: 2 (generator-conditioned)
"""

import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES
from rime.spectral_utils import compute_transport_kappa, find_t7_pairs

TOL = 1e-10
TOL_K = 0.05   # threshold for "nonzero" transport
# NOTE: No TOL_KAPPA — T7 uses structural isdisjoint test. See test_transport.py §3.

block_slices_228 = [slice(0, 64), slice(64, 208), slice(208, 216), slice(216, 228)]

def check(condition, msg):
    assert condition, msg

# ═══════════════════════════════════════════════════════════════════════════════
# Setup: N=3 system
# ═══════════════════════════════════════════════════════════════════════════════

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
sec = op.center_decomposition()
n = sec['n_sectors']
Ps = sec['projectors']

rho_list = [m.toarray() if hasattr(m, 'toarray') else np.array(m)
            for m in op.rho_matrices()]

# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: K_ij symmetry
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: K_ij symmetry ...")
K = np.zeros((n, n))
for rho_m in rho_list:
    for i in range(n):
        Pi_rho = Ps[i] @ rho_m
        for j in range(n):
            K[i, j] = max(K[i, j], np.linalg.norm(Pi_rho @ Ps[j], 'fro'))

asym = np.max(np.abs(K - K.T))
check(asym < TOL, f"K asymmetry too large: {asym:.2e}")
print(f"  OK — max |K_ij - K_ji| = {asym:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Transport sparsity
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: Transport sparsity ...")
nz = int(np.sum(K > TOL_K))
# Undirected edges (i<j only)
edges = [(i, j) for i in range(n) for j in range(i+1, n) if K[i, j] > TOL_K]
print(f"  {nz}/81 entries nonzero")
print(f"  {len(edges)} undirected edges")

# S6 hub
s6_deg = int(np.sum(K[5, :] > TOL_K))
check(s6_deg >= 4, f"S6 degree too low: {s6_deg}")
print(f"  S6 degree = {s6_deg} (hub)")

# S1 isolation (no off-diagonal connections)
s1_in = int(np.sum(K[1:, 0] > TOL_K))
s1_out = int(np.sum(K[0, 1:] > TOL_K))
check(s1_in == 0 and s1_out == 0, f"S1 not isolated: in={s1_in}, out={s1_out}")
print(f"  S1 degree = 0 (isolated)")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: T7 pair count (N=3)
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: T7 pairs (N=3) ...")

# Classify sectors by block support (set-based — structural, not numerical)
def _block_set(P):
    blocks = set()
    for bn, (s, e) in BLOCK_RANGES.items():
        fn2 = np.linalg.norm(P[s:e, s:e], 'fro')**2
        if fn2 > 0.01 * np.trace(P).real:
            blocks.add(bn)
    return blocks

block_sets = [_block_set(Ps[i]) for i in range(n)]
for i in range(n):
    lam = sec['sectors'][i]['lam_18']
    k = round((1 - lam) * 9)
    print(f"  S{i+1}: V({k}/9), dim={sec['sectors'][i]['dim']}, blocks={block_sets[i]}")

# Compute kappa (returns K, kappa0, kappa1)
K_kappa, kappa0_arr, kappa1_arr = compute_transport_kappa(rho_list, Ps, compute_kappa1=True, cso=op)
K_arr = np.array(K)

# T7 detection: structural obstruction test.
# Lemma 1 → Lie closure is block-diagonal → if block_sets are disjoint,
# then κ_d = 0 for ALL d (exact, structural). No numerical κ threshold.
def reachable_2step(i, j, K_arr, tol=TOL_K):
    for k in range(n):
        if k != i and k != j:
            if K_arr[i, k] > tol and K_arr[k, j] > tol:
                return True
    return False

t7_pairs = []
for i in range(n):
    for j in range(i+1, n):
        if not block_sets[i].isdisjoint(block_sets[j]):
            continue  # structural Lie obstruction absent
        if K_arr[i, j] >= TOL_K:
            continue  # has direct transport
        # κ_d = 0 structurally (Lemma 1); check 2-step reachability
        if reachable_2step(i, j, K_arr):
            t7_pairs.append((i+1, j+1))

n_t7 = len(t7_pairs)
for pair in t7_pairs:
    print(f"    T7: S{pair[0]} ↔ S{pair[1]}")

check(n_t7 >= 1,
      f"No T7 pairs found — discrete/continuous split not confirmed: {n_t7}")
check(n_t7 == 5,
      f"Expected 5 T7 pairs, got {n_t7}")
print(f"  OK — {n_t7} T7 pair(s) detected (discrete/continuous split confirmed)")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: N=2 negative control
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 4: N=2 negative control (pocket cube) ...")

# N=2: corners only — filter generators
n2_gens = {k: mv for k, mv in CubieMove.prim_moves.items()
           if k[2] != 2}  # remove half-turns for N=2... actually use all

# For N=2, the pocket cube is corners-only (72-dim)
# Build rho restricted to cp+co blocks
cp_slice = slice(0, 64)
co_slice = slice(208, 216)
n2_mask = np.zeros(228, dtype=bool)
n2_mask[:64] = True
n2_mask[208:216] = True
n2_dim = 72

rhos_n2 = []
for mv in CubieMove.prim_moves.values():
    rho_full = mv.rho()
    rho_dense = rho_full.toarray() if hasattr(rho_full, 'toarray') else np.array(rho_full)
    # Extract corners-only: cp(64) + co(8)
    rho_n2 = rho_dense[n2_mask][:, n2_mask]
    rhos_n2.append(rho_n2)

A_n2 = sum(rhos_n2) / len(rhos_n2)
evals_n2, evecs_n2 = np.linalg.eigh(A_n2)
# Count distinct eigenvalues
unique_evals = sorted(set(np.round(evals_n2, 6)), reverse=True)
print(f"  N=2 spectrum: {len(unique_evals)} eigenvalues")

# Build projectors for N=2
Ps_n2 = []
for lam in unique_evals:
    mask = np.abs(evals_n2 - lam) < TOL
    V = evecs_n2[:, mask]
    P = V @ V.T.conj()
    Ps_n2.append(P)

# Check for hybrid sectors
n2_blocks = [slice(0, 64), slice(64, 72)]  # cp(64), co(8) within 72-dim
n2_hybrid = 0
for P in Ps_n2:
    blocks = 0
    if np.linalg.norm(P[:64, :64], 'fro')**2 > 0.01 * np.trace(P):
        blocks += 1
    if np.linalg.norm(P[64:, 64:], 'fro')**2 > 0.01 * np.trace(P):
        blocks += 1
    if blocks > 1:
        n2_hybrid += 1

check(n2_hybrid == 0,
      f"N=2 has {n2_hybrid} hybrid sectors (expected 0)")
print(f"  OK — N=2 has 0 hybrid sectors")

# Check for T7 in N=2
# Use the already-computed eigenspace projectors from A_n2
n2_s = len(Ps_n2)
Ps_n2_sec = Ps_n2

# Compute K for N=2
K_n2 = np.zeros((n2_s, n2_s))
for rho in rhos_n2:
    for i in range(n2_s):
        Pi_rho = Ps_n2_sec[i] @ rho
        for j in range(n2_s):
            K_n2[i, j] = max(K_n2[i, j], np.linalg.norm(Pi_rho @ Ps_n2_sec[j], 'fro'))

# N2 block classification: cp=0:64, co=64:72
def n2_predominant_block(P):
    tr_cp = np.trace(P[:64, :64]).real
    tr_co = np.trace(P[64:, 64:]).real
    return 'cp' if tr_cp >= tr_co else 'co'

n2_sector_block = [n2_predominant_block(Ps_n2_sec[i]) for i in range(n2_s)]

K_n2_kappa, kappa0_n2, kappa1_n2 = compute_transport_kappa(rhos_n2, Ps_n2_sec, compute_kappa1=True)

# Simple T7 detection for N=2
n2_t7 = 0
for i in range(n2_s):
    for j in range(i+1, n2_s):
        if K_n2[i, j] < TOL_K and K_n2[j, i] < TOL_K:
            if n2_sector_block[i] == n2_sector_block[j]:
                continue  # same block, not T7
            if kappa0_n2[i, j] < TOL and kappa0_n2[j, i] < TOL:
                if kappa1_n2[i, j] < TOL and kappa1_n2[j, i] < TOL:
                    # Check reachable via 2-step
                    for k in range(n2_s):
                        if K_n2[i, k] > TOL_K and K_n2[k, j] > TOL_K:
                            n2_t7 += 1
                            break

check(n2_t7 == 0,
      f"N=2 has {n2_t7} T7 pairs (expected 0)")
print(f"  OK — N=2 has 0 T7 pairs")

print(f"\nAll transport tests passed.")
print(f"  N=3: {n_t7} T7 pair(s)")
print(f"  N=2: 0 T7 pairs (negative control)")
