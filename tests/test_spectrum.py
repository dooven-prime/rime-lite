"""Computational registration checks:
  - Six eigenvalues match the displayed rational labels 1 - k/9
  - k=5 is absent from the registered census
  - Multiplicities: [20, 2, 39, 26, 106, 35]
  - Projector completeness: Σ P_λ = I
  - Trace consistency: Tr(A) = Σ λᵢ·dᵢ

Paper: Paper I, Sec 3 (Spectral decomposition)
Claim status: computational certificate
"""

import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM

TOL_EVAL = 1e-6
TOL_ORTHO = 1e-10
TOL_COMPLETE = 1e-10

# Registered rational labels: lambda = 1 - k/9
EXPECTED_K = {0, 1, 2, 3, 4, 6}
EXPECTED_DIMS = [20, 2, 39, 26, 106, 35]  # in decreasing λ order
K_ABSENT = 5

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
layers = op.layer_keys  # decreasing λ
n_layers = len(layers)

def check(condition, msg):
    assert condition, msg

# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Correct number of layers
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: Six spectral layers ...")
check(n_layers == 6, f"Expected 6 layers, got {n_layers}")
print(f"  OK — {n_layers} layers")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Numerical matching to displayed rational labels
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: Eigenvalues registered against λ = 1 - k/9 ...")
k_vals = []
for lam in layers:
    k = round((1 - lam) * 9)
    k_vals.append(k)
    lam_expected = 1 - k / 9
    check(abs(lam - lam_expected) < TOL_EVAL,
          f"Eigenvalue {lam:.6f} does not match λ=1-{k}/9={lam_expected:.6f}")
    print(f"  λ = {lam:.10f}  →  k = {k}")

k_set = set(k_vals)
check(k_set == EXPECTED_K,
      f"k-set mismatch: expected {EXPECTED_K}, got {k_set}")
print(f"  OK — k ∈ {sorted(k_set)}")

# k=5 absence in the registered census
check(K_ABSENT not in k_set,
      f"k={K_ABSENT} is present in the registered census")
print(f"  OK — k={K_ABSENT} absent from the registered census")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Multiplicities
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: Layer dimensions (multiplicities) ...")
dims_actual = [op.layer_dim[i] for i in range(n_layers)]
check(dims_actual == EXPECTED_DIMS,
      f"Dimension mismatch: expected {EXPECTED_DIMS}, got {dims_actual}")
print(f"  OK — dims = {dims_actual}")

total_dim = sum(dims_actual)
check(total_dim == TOTAL_DIM,
      f"Total dimension mismatch: {total_dim} != {TOTAL_DIM}")
print(f"  OK — Σ dims = {total_dim} = {TOTAL_DIM}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Projector idempotence
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 4: Projector idempotence P_i^2 = P_i ...")
for i, lam in enumerate(layers):
    P = op.projector(lam)
    err = np.linalg.norm(P @ P - P, 'fro')
    check(err < TOL_ORTHO,
          f"P_{{{round((1-lam)*9)}/9}} not idempotent: ||P^2-P|| = {err:.2e}")
    # Trace = dimension
    tr = np.trace(P)
    check(abs(tr - dims_actual[i]) < TOL_ORTHO,
          f"P_{{{round((1-lam)*9)}/9}} trace={tr:.1f} != dim={dims_actual[i]}")
print(f"  OK — all {n_layers} projectors are idempotent with correct trace")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Projector orthogonality
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 5: Projector orthogonality P_i @ P_j = 0 (i != j) ...")
ortho_max = 0.0
for i in range(n_layers):
    Pi = op.projector(layers[i])
    for j in range(i + 1, n_layers):
        Pj = op.projector(layers[j])
        err = np.linalg.norm(Pi @ Pj, 'fro')
        if err > ortho_max:
            ortho_max = err
        if err > TOL_ORTHO:
            ki = round((1 - layers[i]) * 9)
            kj = round((1 - layers[j]) * 9)
            print(f"  WARNING: ||P_{{{ki}/9}} @ P_{{{kj}/9}}|| = {err:.2e}")
check(ortho_max < TOL_ORTHO,
      f"Projector orthogonality violated: max={ortho_max:.2e}")
print(f"  OK — max cross-projector product = {ortho_max:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Completeness Σ P_i = I
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 6: Completeness Σ P_i = I ...")
P_sum = sum(op.projector(lam) for lam in layers)
err = np.linalg.norm(P_sum - np.eye(TOTAL_DIM), 'fro')
check(err < TOL_COMPLETE,
      f"Completeness violated: ||ΣP_i - I|| = {err:.2e}")
print(f"  OK — ||Σ P_i - I|| = {err:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: Trace of A equals Σ λ_i * dim_i
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 7: Trace consistency Tr(A) = Σ λ_i · dim_i ...")
A = op.A
tr_A = np.trace(A)
tr_expected = sum(lam * dims_actual[i] for i, lam in enumerate(layers))
check(abs(tr_A - tr_expected) < TOL_EVAL * TOTAL_DIM,
      f"Trace mismatch: Tr(A)={tr_A:.6f}, Σλ_i·d_i={tr_expected:.6f}")
print(f"  OK — Tr(A) = {tr_A:.6f} = Σ λ_i·d_i")

print(f"\nAll spectral tests passed.")
