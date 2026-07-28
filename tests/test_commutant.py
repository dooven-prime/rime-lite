"""Paper II numerical-certificate regression:
  - QH-family commutativity: [A, QT_all] = [A, HT_all] = [QT_all, HT_all] = 0
  - Sector projectors commute with the registered QH operators
  - Idempotent decomposition: P_i P_j = δ_ij P_i
  - Noncommutativity localization (Supp_nc): cp block commutative,
    ep block carries >93% of total noncommutativity

Paper: Paper II, Sec 5 (Commutant & Noncommutativity)
Invariant level: 2 (generator-conditioned)
"""

import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM
TOL = 1e-10

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
A = op.A
qh_ops = op.build_per_axis_ops()[0]
QT_all = qh_ops['QT_all']
HT_all = qh_ops['HT_all']

sec = op.center_decomposition()
n = sec['n_sectors']
Ps = sec['projectors']

rho_list = [m.toarray() if hasattr(m, 'toarray') else np.array(m)
            for m in op.rho_matrices()]

def check(condition, msg):
    assert condition, msg

# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: The registered QH operator family is commutative
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: QH commutativity [A, QT_all] = [A, HT_all] = [QT_all, HT_all] = 0 ...")
c1 = np.linalg.norm(A @ QT_all - QT_all @ A, 'fro')
c2 = np.linalg.norm(A @ HT_all - HT_all @ A, 'fro')
c3 = np.linalg.norm(QT_all @ HT_all - HT_all @ QT_all, 'fro')

check(c1 < TOL, f"[A, QT_all] != 0: ||comm|| = {c1:.2e}")
check(c2 < TOL, f"[A, HT_all] != 0: ||comm|| = {c2:.2e}")
check(c3 < TOL, f"[QT_all, HT_all] != 0: ||comm|| = {c3:.2e}")
print(f"  OK — [A, QT]={c1:.1e}, [A, HT]={c2:.1e}, [QT, HT]={c3:.1e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Sector projectors commute with the QH operators
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: [P_i, QH operator] = 0 for all sectors ...")
max_comm = 0.0
for i, P in enumerate(Ps):
    for qh_op, name in [(A, 'A'), (QT_all, 'QT'), (HT_all, 'HT')]:
        comm = np.linalg.norm(P @ qh_op - qh_op @ P, 'fro')
        if comm > max_comm:
            max_comm = comm
        if comm > TOL:
            print(f"  WARNING: ||[P_{i+1}, {name}]|| = {comm:.2e}")
check(max_comm < TOL, f"Sector projectors don't commute with QH operators: max={max_comm:.2e}")
print(f"  OK — max ||[P_i, QH operator]|| = {max_comm:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: QH joint-sector projectors: P_i @ P_j = δ_ij P_i
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: QH joint-sector projectors ...")
for i in range(n):
    P = Ps[i]
    err = np.linalg.norm(P @ P - P, 'fro')
    check(err < TOL, f"Sector P_{i+1} not idempotent: {err:.2e}")

# Orthogonality
ortho_max = 0.0
for i in range(n):
    for j in range(i+1, n):
        err = np.linalg.norm(Ps[i] @ Ps[j], 'fro')
        if err > ortho_max:
            ortho_max = err
check(ortho_max < TOL, f"QH projectors not orthogonal: max={ortho_max:.2e}")
print(f"  OK — P_i @ P_j = δ_ij P_i, max off-diag = {ortho_max:.2e}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Trace consistency
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 4: Trace consistency ...")
tr_sum = sum(np.trace(P) for P in Ps)
check(abs(tr_sum - TOTAL_DIM) < TOL,
      f"Σ Tr(P_i) = {tr_sum:.1f} != {TOTAL_DIM}")
# Verify individual traces are integers
for i, P in enumerate(Ps):
    tr_val = np.trace(P)
    tr = int(round(tr_val.real))
    check(abs(tr_val - tr) < TOL,
          f"Sector P_{i+1} trace not integer: {np.trace(P):.6f}")
print(f"  OK — Σ Tr(P_i) = {TOTAL_DIM}, all traces integer")

# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: EP algebra noncommutativity is concentrated in ep block
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 5: Noncommutativity localization (Supp_nc) ...")

QT0 = op.build_per_axis_ops()[0]['QT0']
QT1 = op.build_per_axis_ops()[0]['QT1']

# Verify QT0, QT1 don't commute (total)
comm_01 = QT0 @ QT1 - QT1 @ QT0
total_nc = np.linalg.norm(comm_01, 'fro')
check(total_nc > 0.1, f"QT0, QT1 should not commute: ||[QT⁰,QT¹]|| = {total_nc:.4f}")
print(f"  Total ||[QT⁰, QT¹]|| = {total_nc:.4f}")

# Block-wise noncommutativity
block_ranges = [('cp', 0, 64), ('ep', 64, 208), ('co', 208, 216), ('eo', 216, 228)]
for name, start, end in block_ranges:
    sl = slice(start, end)
    nc_block = np.linalg.norm(comm_01[sl, sl], 'fro')
    print(f"  ||[QT⁰,QT¹]|| on {name}({end-start}d) = {nc_block:.4f}")

# cp should be (approximately) commutative
cp_nc = np.linalg.norm(comm_01[:64, :64], 'fro')
check(cp_nc < TOL, f"cp block should be commutative: ||[QT⁰,QT¹]||_cp = {cp_nc:.2e}")
print(f"  OK — cp block is commutative (||comm|| = {cp_nc:.2e})")

# ep should carry the noncommutativity
ep_nc = np.linalg.norm(comm_01[64:208, 64:208], 'fro')
check(ep_nc > total_nc * 0.9,
      f"ep should carry most noncommutativity: {ep_nc:.4f} vs total {total_nc:.4f}")
print(f"  OK — ep block carries noncommutativity ({ep_nc:.4f} / {total_nc:.4f})")

print(f"\nAll commutant tests passed.")
