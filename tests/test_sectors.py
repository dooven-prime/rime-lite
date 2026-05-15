"""Theorem verification:
  - 9 primitive sectors from Center{A₁₈, QT_all, HT_all}
  - Spectral layer refinement: V₅/₉ splits into 3, V₁/₃ splits into 2
  - Sector completeness, orthogonality, idempotence
  - S6 ≡ primary transport hub (deg ≥ 4)
  - S1 ≡ fully isolated sector

Paper: Paper II, Sec 4 (Primitive sector decomposition)
Invariant level: 2 (generator-conditioned)
"""

import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES, BLOCK_DIMS

TOL = 1e-10
TOL_HYBRID = 0.01  # fraction of norm in a block to count as "in that block"

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
sec = op.center_decomposition()
n = sec['n_sectors']
Ps = sec['projectors']
dims = [s['dim'] for s in sec['sectors']]

def check(condition, msg):
    assert condition, msg

# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Exactly 9 sectors
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: Primitive sector count ...")
check(n == 9, f"Expected 9 primitive sectors, got {n}")
print(f"  OK — {n} primitive sectors")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Sector completeness Σ P_s = I
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: Sector completeness ...")
P_sum = sum(Ps)
err = np.linalg.norm(P_sum - np.eye(228), 'fro')
check(err < TOL, f"Sector completeness violated: ||ΣP_s - I|| = {err:.2e}")
print(f"  OK — ||Σ P_s - I|| = {err:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Sector orthogonality
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: Sector orthogonality ...")
ortho_max = 0.0
for i in range(n):
    for j in range(i + 1, n):
        err = np.linalg.norm(Ps[i] @ Ps[j], 'fro')
        if err > ortho_max:
            ortho_max = err
        if err > TOL:
            print(f"  WARNING: ||P_{i+1} @ P_{j+1}|| = {err:.2e}")
check(ortho_max < TOL, f"Sector orthogonality violated: max={ortho_max:.2e}")
print(f"  OK — max cross-sector product = {ortho_max:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Sector idempotence and trace
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 4: Sector idempotence and trace ...")
for i in range(n):
    P = Ps[i]
    err_idem = np.linalg.norm(P @ P - P, 'fro')
    check(err_idem < TOL, f"Sector P_{i+1} not idempotent: {err_idem:.2e}")
    tr = np.trace(P)
    check(abs(tr - dims[i]) < TOL,
          f"Sector P_{i+1} trace={tr:.1f} != dim={dims[i]}")
print(f"  OK — all {n} sectors idempotent with correct trace")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Correct spectral layer splitting
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 5: Spectral layer splitting ...")
# Group sectors by A_18 eigenvalue (match to closest layer)
layer_keys = sorted(op._layers.keys(), reverse=True)
layer_sectors = {lam: [] for lam in layer_keys}
for i, s in enumerate(sec['sectors']):
    lam_s = s['lam_18']
    # Find closest layer eigenvalue
    best_lam = min(layer_keys, key=lambda lk: abs(lk - lam_s))
    layer_sectors[best_lam].append(i + 1)

# Verify dimensional consistency: sum of sector dims per layer = layer dim
v59_count = 0
v13_count = 0
for lam_key, indices in sorted(layer_sectors.items(), reverse=True):
    sector_dim_sum = sum(sec['sectors'][i-1]['dim'] for i in indices)
    layer_dim = op._layers[lam_key]['dim']
    check(sector_dim_sum == layer_dim,
          f"Layer lam={lam_key:.6f}: sector dim sum {sector_dim_sum} != layer dim {layer_dim}")
    k = round((1 - lam_key) * 9)
    if k == 4:
        v59_count = len(indices)
    if k == 6:
        v13_count = len(indices)
    print(f"  V({k}/9) (dim={layer_dim}): sectors {indices}")

# V₅/₉ (k=4) should split into 3 sectors
check(v59_count == 3,
      f"V_5/9 should split into 3 sectors, got {v59_count}")
# V₁/₃ (k=6) should split into 2 sectors
check(v13_count == 2,
      f"V_1/3 should split into 2 sectors, got {v13_count}")

print(f"  OK — 6 spectral layers correctly split into 9 sectors")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: S6 is primary hub with deg >= 4
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 6: S6 hub connectivity ...")
# Compute K matrix at sector resolution
rho_list = []
for _, (_, rho, *_) in op.rho_moves.items():
    rho_list.append(rho.toarray() if hasattr(rho, 'toarray') else np.array(rho))

K_sec = np.zeros((n, n))
for rho_m in rho_list:
    for i in range(n):
        Pi_rho = Ps[i] @ rho_m
        for j in range(n):
            K_sec[i, j] = max(K_sec[i, j], np.linalg.norm(Pi_rho @ Ps[j], 'fro'))

# S6 = index 5 (0-based), expected degree >= 4
s6_deg = int(np.sum(K_sec[5, :] > 0.05))
check(s6_deg >= 4, f"S6 connectivity too low: degree={s6_deg} (expected >= 4)")
print(f"  OK — S6 degree = {s6_deg} (primary hub)")

# S1 = index 0, should be isolated (no off-diagonal connections)
s1_out = int(np.sum(K_sec[0, 1:] > 0.05))
s1_in = int(np.sum(K_sec[1:, 0] > 0.05))
check(s1_in == 0 and s1_out == 0, f"S1 should be isolated, got in={s1_in}, out={s1_out}")
print(f"  OK — S1 isolated (degree=0)")

# Verify total nonzero edges
nz = int(np.sum(K_sec > 0.05))
print(f"  Transport sparsity: {nz}/{n*n} = {nz/(n*n):.1%} edges nonzero")

print(f"\nAll primitive sector tests passed.")
