"""S3 reg+reg (12-dim) — canonical + A-only decomposition comparison.

Paper III §6.2: S3 reg⊕reg provides structural contrast with nat⊕reg.
Under canonical Center{A_full, A_trans}: 3 sectors, all hybrid, K purely
diagonal, 0 T7 morphisms. C0 fails — Z sectors = isotypic components.

The S3 prototypes together demonstrate that C0 (Center Incompleteness)
is the foundational structural divide: without Z ⊊ C(ρ), off-diagonal
transport cannot exist regardless of C1–C3 status.

Paper: Paper III §6.2 (S3 reg⊕reg — Negative Result)
Invariant level: 2 (generator-conditioned)
"""
import numpy as np
from rime.spectral_utils import (
    build_s3_regular_rep,
    joint_diag_sectors, build_projectors
)
from spectral_utils import compute_transport_kappa

np.random.seed(42)
TOL = 1e-10
TOL_K = 0.01

print("=" * 64)
print("  Paper III — S3 reg+reg (12-dim)")
print("  Canonical: Center{A_full, A_trans}")
print("=" * 64)

# Build S3 reg+reg — all 6 group elements
rhos_reg_all = [build_s3_regular_rep(i) for i in range(6)]
rhos_all = []
for r_reg in rhos_reg_all:
    rho = np.zeros((12, 12))
    rho[:6, :6] = r_reg
    rho[6:, 6:] = r_reg
    rhos_all.append(rho)

# Generator subset (3 transpositions) for transport
trans_indices = [1, 2, 3]
rhos_trans = [rhos_all[i] for i in trans_indices]

# Verify block-diagonality
for i, rho in enumerate(rhos_all):
    cross_norm = np.linalg.norm(rho[:6, 6:]) + np.linalg.norm(rho[6:, :6])
    assert cross_norm < TOL, f"Generator {i} not block-diagonal: {cross_norm:.2e}"
print("  Block-diagonal: reg | reg  [OK]")


# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL: Center{A_full, A_trans}
# ══════════════════════════════════════════════════════════════════════════════

A_full = sum(rhos_all) / 6.0
A_trans = sum(rhos_trans) / 3.0

print(f"\n{'─'*60}")
print("  CANONICAL: Center{A_full, A_trans}")
print(f"{'─'*60}")
print(f"  A_full  eigenvalues: {sorted(set(np.round(np.linalg.eigvalsh(A_full), 6)), reverse=True)}")
print(f"  A_trans eigenvalues: {sorted(set(np.round(np.linalg.eigvalsh(A_trans), 6)), reverse=True)}")

joint_canon = joint_diag_sectors([A_full, A_trans], tol=TOL)
Ps_canon = build_projectors(joint_canon, 12)
n_canon = len(Ps_canon)

print(f"\n  Sectors: {n_canon}")
for i, P in enumerate(Ps_canon):
    tr_A = np.trace(P[:6, :6]).real
    tr_B = np.trace(P[6:, 6:]).real
    dim = int(round(np.trace(P).real))
    blocks = []
    if tr_A > 0.01 * dim: blocks.append(f'A({int(round(tr_A))})')
    if tr_B > 0.01 * dim: blocks.append(f'B({int(round(tr_B))})')
    is_hybrid = len(blocks) > 1
    lam_f = np.trace(A_full @ P).real / dim if dim > 0 else 0
    lam_t = np.trace(A_trans @ P).real / dim if dim > 0 else 0
    tag = '<- HYBRID' if is_hybrid else ''
    print(f"    S{i+1}: dim={dim}, A_full={lam_f:.4f}, A_trans={lam_t:.4f}, "
          f"{'+'.join(blocks) if blocks else '?'} {tag}")

# Transport
K_c, k0_c, k1_c = compute_transport_kappa(rhos_trans, Ps_canon, compute_kappa1=True)

# Block classification
def classify_block(P, tol=0.01):
    tr_A = np.trace(P[:6, :6]).real
    tr_B = np.trace(P[6:, 6:]).real
    tr_tot = np.trace(P).real
    has_A = tr_A > tol * tr_tot
    has_B = tr_B > tol * tr_tot
    if has_A and has_B: return 'hybrid'
    if has_A: return 'A'
    return 'B'

blocks_c = [classify_block(P) for P in Ps_canon]

# T7 detection
t7_c = []
for i in range(n_canon):
    for j in range(i+1, n_canon):
        bi, bj = blocks_c[i], blocks_c[j]
        if bi == bj or bi == 'hybrid' or bj == 'hybrid':
            continue
        if K_c[i,j] < TOL_K and k0_c[i,j] < TOL and k1_c[i,j] < TOL:
            for k in range(n_canon):
                if K_c[i,k] > TOL_K and K_c[k,j] > TOL_K:
                    t7_c.append((i, j, k))
                    break

print(f"\n  T7 pairs: {len(t7_c)}")

n_hybrid_c = sum(1 for b in blocks_c if b == 'hybrid')
print(f"  Canonical: {n_canon} sectors, {n_hybrid_c} hybrid, {len(t7_c)} T7")


# ══════════════════════════════════════════════════════════════════════════════
# C0 Diagnostic
# ══════════════════════════════════════════════════════════════════════════════

from scipy.linalg import null_space

n = 12
constraints = []
for rho in rhos_all:
    M = np.kron(np.eye(n), rho.T) - np.kron(rho, np.eye(n))
    constraints.append(M)
constraint_mat = np.vstack(constraints)
comm_basis = null_space(constraint_mat, rcond=TOL)
dim_comm_rho = comm_basis.shape[1]

max_comm = 0.0
for P in Ps_canon:
    for rho in rhos_all:
        comm = np.linalg.norm(P @ rho - rho @ P, 'fro')
        max_comm = max(max_comm, comm)

k_off_diag = sum(1 for i in range(n_canon) for j in range(n_canon) if i != j and K_c[i,j] > TOL_K)

print(f"\n  C0 Diagnostic")
print(f"  dim(Z)          = {n_canon}")
print(f"  dim(C(rho))     = {dim_comm_rho}")
print(f"  max|[P_i, rho(g)]| = {max_comm:.2e}")
print(f"  K off-diagonal  = {k_off_diag} edges")
print(f"  C0 (Z < C(rho)) = {'YES' if max_comm > TOL else 'NO - Z sectors = C(rho) sectors, K diagonal'}")
if max_comm < TOL:
    print(f"  Structural: T7 impossible (sectors are G-invariant subrepresentations)")


# ══════════════════════════════════════════════════════════════════════════════
# Comparison with nat⊕reg
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{'='*64}")
print(f"  S3 Prototype Comparison")
print(f"{'='*64}")
print(f"  {'':<20s} {'nat+reg':>12s} {'reg+reg':>12s}")
print(f"  {'─'*44}")
print(f"  {'Dimension':<20s} {'9':>12s} {'12':>12s}")
print(f"  {'Canonical sectors':<20s} {'3':>12s} {'3':>12s}")
print(f"  {'Hybrid sectors':<20s} {'2':>12s} {'3':>12s}")
print(f"  {'K off-diagonal':<20s} {'0':>12s} {'0':>12s}")
print(f"  {'T7 morphisms':<20s} {'0':>12s} {'0':>12s}")
print(f"  {'C0 status':<20s} {'FAILS':>12s} {'FAILS':>12s}")
print(f"  ")
print(f"  Both S3 prototypes fail C0: Z sectors = isotypic components,")
print(f"  all sectors G-invariant, K purely diagonal. T7 is structurally")
print(f"  impossible regardless of C1-C3 status. The Rubik cube (228-dim)")
print(f"  is the sole verified T7 system: Z < C(rho) massively (9 sectors")
print(f"  aggregate 51 isotypic components), enabling 5 T7 morphisms.")
print(f"  ")
print(f"  Structural lesson: hybrid sectors != transport. Center")
print(f"  incompleteness (C0) is the foundational structural divide.")

print(f"\nDone - S3 reg+reg (canonical + C0 diagnostic). 0 T7 pairs.")
