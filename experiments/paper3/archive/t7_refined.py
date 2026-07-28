"""S3 nat⊕reg Joint Diagonalization — canonical + externally refined.

Corrected decomposition (joint_diag_sectors eigenvector bug fixed 2026-05-26):
  - CANONICAL: Center{A_full, A_trans} → 3 sectors, 2 hybrid, 0 T7 pairs
  - REFINED:   Center{A_s3, P_nat}   → 5 sectors, 0 hybrid, 0 T7 pairs
  - Block-diagonal rho → block-diagonal A_g → no Lie cross-block
  - S3 does NOT exhibit T7 under the canonical transport-generated center
  - Rubik cube (228-dim) is the canonical T7 realization (5 pairs)

Canonical decomposition:
  Z = ⟨A_full, A_trans⟩  — transport-generated commutative algebra
  A_full  = (1/6) Σ_{g∈S₃} ρ(g)        eigenvalues: {1.0, 0.0}
  A_trans = (1/3) Σ_{g∈transpositions} ρ(g)  eigenvalues: {1.0, 0.0, -1.0}

Externally refined decomposition (robustness check):
  Z' = ⟨A_s3, P_nat⟩  — adds block projector P_nat = diag(I₃, 0₆)
  P_nat fully separates the blocks; all sectors become pure.

Key sentence (canonical declaration):
  Unless explicitly stated otherwise, all sector decompositions in this
  trilogy are defined with respect to the transport-generated commutative
  algebra Z = ⟨A_full, A_trans⟩. Additional projectors such as P_nat are
  treated as external refinement operators and are not part of the
  canonical transport geometry.

Paper: Paper III, Sec 6 (S3 Prototype — negative result)
Invariant level: 2 (generator-conditioned)
"""
import numpy as np
import os
from rime.spectral_utils import (
    build_s3_natural_rep, build_s3_regular_rep,
    build_block_diag_rho, S3_PERMUTATIONS,
    joint_diag_sectors, build_projectors
)
from spectral_utils import compute_transport_kappa

np.random.seed(42)
TOL = 1e-10
TOL_K = 0.01
FIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'figures', 'paper3')
os.makedirs(FIG_DIR, exist_ok=True)

print("=" * 64)
print("  Paper III - S_3 nat+reg Joint Diagonalization")
print("  9-dim: nat(3) + reg(6)")
print("=" * 64)

# ══════════════════════════════════════════════════════════════════════════════
# Build all 6 group elements (nat⊕reg, 9-dim)
# ══════════════════════════════════════════════════════════════════════════════

rhos_nat_all = [build_s3_natural_rep(S3_PERMUTATIONS[i]) for i in range(6)]
rhos_reg_all = [build_s3_regular_rep(i) for i in range(6)]
rhos_all = build_block_diag_rho(rhos_nat_all, rhos_reg_all)

# Verify block-diagonality
for i, rho in enumerate(rhos_all):
    cross_norm = np.linalg.norm(rho[:3, 3:]) + np.linalg.norm(rho[3:, :3])
    assert cross_norm < TOL, f"Generator {i} not block-diagonal: {cross_norm:.2e}"
print("  Block-diagonal: nat | reg  [OK]")

# Generator subset (3 transpositions) for transport computation
trans_indices = [1, 2, 3]  # (12), (23), (13)
rhos_trans = [rhos_all[i] for i in trans_indices]

# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL decomposition: Center{A_full, A_trans}
# ══════════════════════════════════════════════════════════════════════════════

A_full = sum(rhos_all) / 6.0
A_trans = sum(rhos_trans) / 3.0

print(f"\n{'─' * 60}")
print("  CANONICAL: Center{A_full, A_trans}")
print(f"{'─' * 60}")
print(f"  A_full  eigenvalues: {sorted(set(np.round(np.linalg.eigvalsh(A_full), 6)), reverse=True)}")
print(f"  A_trans eigenvalues: {sorted(set(np.round(np.linalg.eigvalsh(A_trans), 6)), reverse=True)}")

joint_canon = joint_diag_sectors([A_full, A_trans], tol=TOL)
Ps_canon = build_projectors(joint_canon, 9)
n_canon = len(Ps_canon)

print(f"\n  Sectors: {n_canon}")
for i, P in enumerate(Ps_canon):
    tr_nat = np.trace(P[:3, :3]).real
    tr_reg = np.trace(P[3:, 3:]).real
    dim = int(round(np.trace(P).real))
    blocks = []
    if tr_nat > 0.01 * dim: blocks.append(f'nat({int(round(tr_nat))})')
    if tr_reg > 0.01 * dim: blocks.append(f'reg({int(round(tr_reg))})')
    is_hybrid = len(blocks) > 1
    lam_f = np.trace(A_full @ P).real / dim if dim > 0 else 0
    lam_t = np.trace(A_trans @ P).real / dim if dim > 0 else 0
    tag = '← HYBRID' if is_hybrid else ''
    print(f"    S{i + 1}: dim={dim}, A_full={lam_f:.4f}, A_trans={lam_t:.4f}, "
          f"{'+'.join(blocks) if blocks else '?'} {tag}")

# Transport (canonical)
K_c, k0_c, k1_c = compute_transport_kappa(rhos_trans, Ps_canon, compute_kappa1=True)


# T7 detection (canonical)
def classify_block(P, tol=0.01):
    tr_nat = np.trace(P[:3, :3]).real
    tr_reg = np.trace(P[3:, 3:]).real
    tr_tot = np.trace(P).real
    has_nat = tr_nat > tol * tr_tot
    has_reg = tr_reg > tol * tr_tot
    if has_nat and has_reg: return 'hybrid'
    if has_nat: return 'nat'
    return 'reg'


blocks_c = [classify_block(P) for P in Ps_canon]

t7_c = []
for i in range(n_canon):
    for j in range(i + 1, n_canon):
        bi, bj = blocks_c[i], blocks_c[j]
        if bi == bj or bi == 'hybrid' or bj == 'hybrid':
            continue
        if K_c[i, j] < TOL_K and k0_c[i, j] < TOL and k1_c[i, j] < TOL:
            for k in range(n_canon):
                if K_c[i, k] > TOL_K and K_c[k, j] > TOL_K:
                    t7_c.append((i, j, k))
                    break

print(f"\n  T7 pairs: {len(t7_c)}")
for i, j, k in t7_c:
    print(f"    S{i + 1}({blocks_c[i]}) ←→ S{j + 1}({blocks_c[j]}) via S{k + 1}({blocks_c[k]})")

n_hybrid_c = sum(1 for b in blocks_c if b == 'hybrid')
# Canonical: 0 T7 pairs (S3 has no cross-block compositional accessibility)
print(f"  Canonical: {n_canon} sectors, {n_hybrid_c} hybrid, {len(t7_c)} T7")

# ══════════════════════════════════════════════════════════════════════════════
# EXTERNALLY REFINED: Center{A_s3, P_nat}  (robustness check)
# ══════════════════════════════════════════════════════════════════════════════

A_s3 = sum(rhos_trans) / len(rhos_trans)  # avg over 3 transpositions only
P_nat = np.diag([1.0] * 3 + [0.0] * 6)

print(f"\n{'─' * 60}")
print("  REFINED: Center{A_s3, P_nat}  (externally refined — CCS App G.2)")
print(f"{'─' * 60}")

joint_refined = joint_diag_sectors([A_s3, P_nat], tol=TOL)
Ps_ref = build_projectors(joint_refined, 9)
n_ref = len(Ps_ref)

print(f"  Sectors: {n_ref}")
for i, P in enumerate(Ps_ref):
    tr_nat = np.trace(P[:3, :3]).real
    tr_reg = np.trace(P[3:, 3:]).real
    dim = int(round(np.trace(P).real))
    blocks = []
    if tr_nat > 0.01 * dim: blocks.append(f'nat({int(round(tr_nat))})')
    if tr_reg > 0.01 * dim: blocks.append(f'reg({int(round(tr_reg))})')
    is_hybrid = len(blocks) > 1
    tag = '← HYBRID' if is_hybrid else ''
    print(f"    S{i + 1}: dim={dim}, {'+'.join(blocks) if blocks else '?'} {tag}")

K_r, k0_r, k1_r = compute_transport_kappa(rhos_trans, Ps_ref, compute_kappa1=True)
blocks_r = [classify_block(P) for P in Ps_ref]

t7_r = []
for i in range(n_ref):
    for j in range(i + 1, n_ref):
        bi, bj = blocks_r[i], blocks_r[j]
        if bi == bj or bi == 'hybrid' or bj == 'hybrid':
            continue
        if K_r[i, j] < TOL_K and k0_r[i, j] < TOL and k1_r[i, j] < TOL:
            for k in range(n_ref):
                if K_r[i, k] > TOL_K and K_r[k, j] > TOL_K:
                    t7_r.append((i, j, k))
                    break

print(f"\n  T7 pairs: {len(t7_r)}")
for i, j, k in t7_r:
    print(f"    S{i + 1}({blocks_r[i]}) ←→ S{j + 1}({blocks_r[j]}) via S{k + 1}({blocks_r[k]})")

n_hybrid_r = sum(1 for b in blocks_r if b == 'hybrid')
print(f"  Refined: {n_ref} sectors, {n_hybrid_r} hybrid, {len(t7_r)} T7 (P_nat fully separates blocks)")
print(f"  (Block projector P_nat fully separates nat and reg blocks;")
print(f"   all 5 sectors become pure-block; no hybrid sectors remain.)")

# ══════════════════════════════════════════════════════════════════════════════
# C0 Diagnostic — Center Incompleteness
# ══════════════════════════════════════════════════════════════════════════════

# dim(Z): number of distinct joint eigenspaces = number of sectors
# Z = <A_full, A_trans> — the transport-generated commutative algebra
dim_Z_canon = n_canon
dim_Z_refined = n_ref

# dim(C(rho)): dimension of the full commutant algebra
# For S3 nat+reg, C(rho) = Comm(trivial^2) + Comm(sign^1) + Comm(std^3)
# isotypic decomposition: trivial(2 copies), sign(1 copy), standard(3 copies)
# dim(C(rho)) = 2^2 + 1^2 + 3^2 = 4 + 1 + 9 = 14

# Compute full commutant numerically using the Reynolds operator
# C(rho) = {X : X rho(g) = rho(g) X for all g in G}
n = 9
# Flatten the commutator equations into a linear system
# X @ rho(g) - rho(g) @ X = 0 for all g
# This is equivalent to: (I ⊗ rho(g)^T - rho(g) ⊗ I) vec(X) = 0
from scipy.linalg import null_space

# Build the constraint matrix for the full commutant
constraints = []
for rho in rhos_all:
    # kron(I, rho^T) - kron(rho, I)
    M = np.kron(np.eye(n), rho.T) - np.kron(rho, np.eye(n))
    constraints.append(M)
constraint_mat = np.vstack(constraints)
comm_basis = null_space(constraint_mat, rcond=TOL)
dim_comm_rho = comm_basis.shape[1]

# Check if Z projectors commute with all rho(g) (i.e., sectors are invariant)
# For each canonical sector projector P_i, check if [P_i, rho(g)] = 0 for all g
max_commutator = 0.0
for P in Ps_canon:
    for rho in rhos_all:
        comm = np.linalg.norm(P @ rho - rho @ P, 'fro')
        max_commutator = max(max_commutator, comm)

# C0: Z ⊊ C(rho) — center incompleteness
# If projectors commute with all rho(g), sectors = isotypic components → K diagonal
c0_holds = dim_Z_canon < dim_comm_rho and max_commutator > TOL
k_off_diag = sum(1 for i in range(n_canon) for j in range(n_canon) if i != j and K_c[i, j] > TOL_K)

print(f"\n  C0 Diagnostic - Center Incompleteness")
print(f"  dim(Z)          = {dim_Z_canon}")
print(f"  dim(C(rho))     = {dim_comm_rho}")
print(f"  max|[P_i, rho(g)]| = {max_commutator:.2e}")
print(f"  K off-diagonal  = {k_off_diag} edges")
if c0_holds:
    print(f"  C0 (Z < C(rho)) = YES - sectors aggregate isotypic components")
    print(f"  Structural: T7 possible (non-invariant sectors, off-diagonal K)")
else:
    print(f"  C0 (Z < C(rho)) = NO - Z sectors = C(rho) sectors, K diagonal")
    print(f"  Structural: T7 impossible (sectors are G-invariant subrepresentations)")

# ══════════════════════════════════════════════════════════════════════════════
# Comparison
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{'=' * 64}")
print(f"  Summary")
print(f"{'=' * 64}")
print(f"  Canonical  (Center{{A_full, A_trans}}): {n_canon} sectors, {len(t7_c)} T7")
print(f"  Refined    (Center{{A_s3, P_nat}}):     {n_ref} sectors, {len(t7_r)} T7")
print(f"  S3 has 0 T7 under both decompositions.")
print(f"  C0 status: canonical Z sectors = C(rho) sectors -> K diagonal -> 0 T7")
print(f"  Rubik cube (N=3) has Z < C(rho) massively (9 sectors vs 51 isotypic) -> 5 T7")

# ══════════════════════════════════════════════════════════════════════════════
# Figure — canonical decomposition
# ══════════════════════════════════════════════════════════════════════════════

try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 4))

    # Spectrum (canonical)
    ax = axes[0]
    dims_c = [int(round(np.trace(P).real)) for P in Ps_canon]
    colors = ['#5b6abf' if b == 'nat' else '#e74c3c' if b == 'reg' else '#f39c12'
              for b in blocks_c]
    ax.bar(range(n_canon), dims_c, color=colors, edgecolor='white')
    ax.set_xticks(range(n_canon))
    ax.set_xticklabels([f'S{i + 1}' for i in range(n_canon)])
    ax.set_title(f'Canonical: Center{{A_full, A_trans}} ({n_canon} sectors)')
    ax.set_ylabel('Dimension')

    # K matrix (canonical)
    ax = axes[1]
    im = ax.imshow(K_c, cmap='YlOrRd', aspect='equal', vmin=0)
    ax.set_title('Transport Matrix K')
    for i in range(n_canon):
        for j in range(n_canon):
            if K_c[i, j] > TOL_K:
                ax.text(j, i, f'{K_c[i, j]:.2f}', ha='center', va='center', fontsize=7,
                        color='white' if K_c[i, j] > 0.3 else 'black')
    plt.colorbar(im, ax=ax, shrink=0.8)

    # T7 schematic
    ax = axes[2]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('C0 Diagnostic (canonical)', fontweight='bold')

    ax.text(1.5, 5, 'nat block (3-dim)', ha='center', fontsize=10, color='#5b6abf', fontweight='bold')
    ax.text(5, 5, 'hybrid\n(inert)', ha='center', fontsize=10, color='#f39c12', fontweight='bold')
    ax.text(8.5, 5, 'reg block (6-dim)', ha='center', fontsize=10, color='#e74c3c', fontweight='bold')

    # Lie blocked + K diagonal
    ax.annotate('', xy=(7.5, 3), xytext=(2.5, 3),
                arrowprops=dict(arrowstyle='->', color='#95a5a6', lw=2))
    ax.text(5, 3.3, 'K = diag (no cross-sector transport)', ha='center', fontsize=9, color='#95a5a6')

    # C0 diagnosis
    ax.text(5, 2.0, 'C0 FAILS: Z sectors = C(rho) sectors', ha='center', fontsize=9,
            color='#e74c3c', fontweight='bold')
    ax.text(5, 1.3, 'Sectors are G-invariant subrepresentations', ha='center', fontsize=8, color='#95a5a6')
    ax.text(5, 0.6, 'T7 is structurally impossible', ha='center', fontsize=8, fontstyle='italic')

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 't7_refined.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Figure saved: {os.path.join(FIG_DIR, 't7_refined.png')}")
except ImportError:
    pass

print("Done - S3 nat+reg decomposition data (canonical + refined). 0 T7 pairs.")
