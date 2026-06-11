"""Projector Algebra — verify spectral projector properties.

Computationally verified:
  - Idempotence: P_i² = P_i
  - Orthogonality: P_i P_j = 0 (i ≠ j)
  - Completeness: Σ P_i = I
  - Trace-dimension: Tr(P_i) = dim(V_i)
  - Trace consistency: Σ λ_i · dim(V_i) = Tr(A)

Paper: Paper I, Sec 3.1 (Projector Properties)
Invariant level: 1 (group-algebraic)
"""
import numpy as np
import sys
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM

np.random.seed(42)
TOL = 1e-6

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
layers = op.layer_keys
A = op.A

print("=" * 60)
print("  Paper I — Projector Algebra Verification")
print("=" * 60)

n = len(layers)
Ps = [op.projector(lam) for lam in layers]
dims = [op.layer_dimension(lam) for lam in layers]

# 1. Idempotence
print(f"\n  1. Idempotence: P_i² = P_i")
max_idem_err = 0
for i, (lam, P) in enumerate(zip(layers, Ps)):
    err = np.linalg.norm(P @ P - P, 'fro')
    max_idem_err = max(max_idem_err, err)
    k = op.lam_to_k(lam)
    status = "✓" if err < TOL else "✗"
    print(f"     k={k}: ||P²-P|| = {err:.2e}  {status}")
assert max_idem_err < TOL, f"Idempotence violation: {max_idem_err:.2e}"

# 2. Orthogonality
print(f"\n  2. Orthogonality: P_i P_j = 0 (i ≠ j)")
max_ortho_err = 0
for i in range(n):
    for j in range(i + 1, n):
        err = np.linalg.norm(Ps[i] @ Ps[j], 'fro')
        max_ortho_err = max(max_ortho_err, err)
print(f"     max ||P_i P_j|| = {max_ortho_err:.2e}  {'✓' if max_ortho_err < TOL else '✗'}")
assert max_ortho_err < TOL, f"Orthogonality violation: {max_ortho_err:.2e}"

# 3. Completeness
print(f"\n  3. Completeness: Σ P_i = I")
P_sum = sum(Ps)
comp_err = np.linalg.norm(P_sum - np.eye(TOTAL_DIM), 'fro')
print(f"     ||ΣP_i - I|| = {comp_err:.2e}  {'✓' if comp_err < TOL else '✗'}")
assert comp_err < TOL, f"Completeness violation: {comp_err:.2e}"

# 4. Trace-dimension
print(f"\n  4. Trace = Dimension:")
for i, (lam, P) in enumerate(zip(layers, Ps)):
    tr = np.trace(P).real
    k = op.lam_to_k(lam)
    match = abs(tr - dims[i]) < TOL
    print(f"     k={k}: Tr(P) = {tr:.1f}, dim = {dims[i]}  {'✓' if match else '✗'}")
    assert match, f"Trace-dimension mismatch: {tr:.1f} != {dims[i]}"

# 5. Spectral trace identity
print(f"\n  5. Spectral trace identity: Tr(A) = Σ λ_i · dim_i")
tr_A = np.trace(A).real
tr_spectral = sum(lam * dims[i] for i, lam in enumerate(layers))
print(f"     Tr(A) = {tr_A:.6f}")
print(f"     Σ λ_i·dim_i = {tr_spectral:.6f}")
assert abs(tr_A - tr_spectral) < TOL * TOTAL_DIM, "Trace identity violation"

# 6. Spectral radius of fast subspace
print(f"\n  6. Fast subspace spectral radius")
lam_min = min(layers)
print(f"     λ_min = {lam_min:.6f} (k={op.lam_to_k(lam_min)})")
print(f"     Mixing time (ε=1e-6): {np.log(1e6)/(-np.log(lam_min)):.1f} iterations")

print(f"\n  All projector algebra properties verified ✓")
