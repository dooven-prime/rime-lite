"""Finite representation-construction regression:
  - Group homomorphism: ρ(g₁·g₂) = ρ(g₁) ρ(g₂)
  - Unitary consistency: ρ(g)† ρ(g) = I
  - Block decomposition: ρ(g) = diag(cp, ep, co, eo)
  - Cross-block coupling: identically zero

Paper: Paper I, Sec 2 (Representation construction)
Invariant level: 1 (group algebra)
"""

import numpy as np
from rime.cubie import CubieMove, CubieState, TOTAL_DIM, BLOCK_RANGES

SEED = 42
N_TESTS = 50
TOL = 1e-7        # float64 accumulation in 228×228 matrices
TOL_STRICT = 1e-12  # for integer permutation blocks

rng = np.random.default_rng(SEED)
prim = list(CubieMove.prim_moves.values())
n_gen = len(prim)
assert n_gen == 18, f"Expected 18 generators, got {n_gen}"

# ── helpers ──

def random_group_element(length=8):
    """Build a random group element as a word of length `length`."""
    g = CubieMove.identity()
    for _ in range(length):
        g = g.compose(prim[rng.integers(0, n_gen)])
    return g


def rho_of(move):
    """Dense 228x228 representation matrix."""
    r = move.rho()
    return r.toarray() if hasattr(r, 'toarray') else np.array(r)


def check(condition, msg):
    assert condition, msg


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Group homomorphism
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: Group homomorphism rho(g1 @ g2) == rho(g1) @ rho(g2) ...")
hom_fail = 0
for i in range(N_TESTS):
    g1 = random_group_element(rng.integers(1, 6))
    g2 = random_group_element(rng.integers(1, 6))
    lhs = rho_of(g1.compose(g2))
    rhs = rho_of(g1) @ rho_of(g2)
    err = np.linalg.norm(lhs - rhs, 'fro')
    if err > TOL:
        hom_fail += 1
        if hom_fail <= 3:
            print(f"  FAIL {i}: ||rho(g1@g2) - rho(g1)@rho(g2)|| = {err:.2e}")
assert hom_fail == 0, f"Homomorphism violated in {hom_fail}/{N_TESTS} tests"
print(f"  OK — {N_TESTS}/{N_TESTS} passed")

# Also verify rho(identity) = I
I_rho = rho_of(CubieMove.identity())
check(np.linalg.norm(I_rho - np.eye(TOTAL_DIM), 'fro') < TOL,
      f"rho(identity) != I: error={np.linalg.norm(I_rho - np.eye(TOTAL_DIM), 'fro'):.2e}")
print("  OK — rho(identity) == I")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Unitary consistency
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: Unitary consistency rho(g)^H @ rho(g) == I ...")
uni_fail = 0
for i in range(N_TESTS):
    g = random_group_element(rng.integers(1, 10))
    R = rho_of(g)
    err = np.linalg.norm(R.T.conj() @ R - np.eye(TOTAL_DIM), 'fro')
    if err > TOL:
        uni_fail += 1
        if uni_fail <= 3:
            print(f"  FAIL {i}: ||rho(g)^H @ rho(g) - I|| = {err:.2e}")
assert uni_fail == 0, f"Unitarity violated in {uni_fail}/{N_TESTS} tests"
print(f"  OK — {N_TESTS}/{N_TESTS} passed")

# Also verify all 18 generators are unitary
for key, mv in CubieMove.prim_moves.items():
    R = rho_of(mv)
    err = np.linalg.norm(R.T.conj() @ R - np.eye(TOTAL_DIM), 'fro')
    check(err < TOL, f"Generator {key} not unitary: error={err:.2e}")
print("  OK — all 18 generators are unitary")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Block decomposition
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: Block decomposition rho = diag(cp(64), ep(144), co(8), eo(12)) ...")

slices = {name: slice(start, end) for name, (start, end) in BLOCK_RANGES.items()}
block_names = list(slices.keys())

# Test 3a: All generators are block-diagonal
cross_max = 0.0
for key, mv in CubieMove.prim_moves.items():
    R = rho_of(mv)
    for i, bi in enumerate(block_names):
        for j, bj in enumerate(block_names):
            if i != j:
                si, sj = slices[bi], slices[bj]
                cross = np.linalg.norm(R[si][:, sj], 'fro')
                if cross > cross_max:
                    cross_max = cross

check(cross_max < TOL,
      f"Non-zero cross-block coupling in generators: max={cross_max:.2e}")
print(f"  OK — max cross-block coupling = {cross_max:.2e}")

# Test 3b: Verify block dimensions
for name, (start, end) in BLOCK_RANGES.items():
    check(end - start == {'cp': 64, 'ep': 144, 'co': 8, 'eo': 12}[name],
          f"Wrong block dim for {name}: {end-start}")

# Test 3c: Random products also block-diagonal
prod_cross_max = 0.0
for i in range(20):
    g = random_group_element(rng.integers(2, 8))
    R = rho_of(g)
    for bi in block_names:
        for bj in block_names:
            if bi != bj:
                si, sj = slices[bi], slices[bj]
                cross = np.linalg.norm(R[si][:, sj], 'fro')
                if cross > prod_cross_max:
                    prod_cross_max = cross
check(prod_cross_max < TOL,
      f"Non-zero cross-block coupling in random products: max={prod_cross_max:.2e}")
print(f"  OK — max cross-block coupling in random products = {prod_cross_max:.2e}")

print(f"  Block decomposition: rho = diag(cp, ep, co, eo) VERIFIED")

# ═══════════════════════════════════════════════════════════════════════════════

print(f"\nAll representation tests passed ({3 + N_TESTS*2 + 18 + 20} checks).")
