"""
Find minimal system exhibiting T7:
discrete composition can cross block boundaries, Lie curvature cannot.

Core mechanism:
  rho(g) = block_diag(rho_A(g), rho_B(g), ...)
  => A_g = log(rho(g)) is block-diagonal
  => [A_g, A_h] is block-diagonal
  => No Lie operation creates cross-block coupling

  But: eigenvalue resonance across blocks produces hybrid sectors
  whose projectors sum over multiple blocks, enabling cross-block
  COMPOSITION (though NOT single-generator transport).

Strategy v2:
  - Use Center{...} joint diagonalization for structurally meaningful sectors
  - Try eigenvalue resonance via same irrep appearing in different blocks
  - Try S3 natural+regular, S4 variants, D4 variants
  - Try manual construction with exact eigenvalue matching
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from scipy.linalg import block_diag

from rime.spectral_utils import *



def analyze_v2(name, rhos, block_slices, center_ops=None):
    """T7 analysis with joint diagonalization support."""
    n = rhos[0].shape[0]
    n_gen = len(rhos)

    A = sum(rhos) / n_gen

    if center_ops is None:
        # Just use A alone
        evals, evecs = np.linalg.eigh(A)
        tol = 1e-9
        groups = []
        used = set()
        for i in range(n):
            if i in used:
                continue
            indices = [j for j in range(n) if abs(evals[j] - evals[i]) < tol]
            used.update(indices)
            groups.append((evals[i].real, indices))
        groups.sort(key=lambda x: -x[0])
        n_sec = len(groups)
        P = []
        for _, indices in groups:
            V = evecs[:, indices]
            P.append(V @ V.conj().T)
    else:
        # Joint diagonalization
        all_ops = [A] + list(center_ops)
        sectors = joint_diag_sectors(all_ops)
        n_sec = len(sectors)
        P = []
        groups = []  # (eigenvalue_of_A, indices)
        for evals_tuple, indices in sectors:
            V = np.zeros((n, len(indices)), dtype=np.complex128)
            for k, idx in enumerate(indices):
                V[idx, k] = 1.0
            P.append(V @ V.conj().T)
            groups.append((evals_tuple[0] if evals_tuple[0] is not None else 0, indices))

    # Block composition of sectors
    blk_info = []
    for s_idx in range(n_sec):
        comps = []
        for blk_name, sl in block_slices:
            c = int(round(np.trace(P[s_idx][sl, sl]).real))
            comps.append(c)
        blk_info.append(comps)

    # Transport K, kappa_0, kappa_1 — delegated to shared utility
    try:
        K, k0, k1 = compute_transport_kappa(rhos, P)
    except Exception:
        K = np.zeros((n_sec, n_sec))
        k0 = np.zeros((n_sec, n_sec))
        k1 = np.zeros((n_sec, n_sec))

    # Composition
    eps = 1e-10
    A_dir = (K > eps).astype(int)
    A2 = (A_dir @ A_dir) > 0

    # T7 candidates: K=0 but reachable via 2-step, and k0=k1=0
    t7 = []
    for i in range(n_sec):
        for j in range(i + 1, n_sec):
            if K[i, j] < eps and k0[i, j] < eps and k1[i, j] < eps:
                if A2[i, j]:
                    meds = [k for k in range(n_sec) if A_dir[i, k] and A_dir[k, j]]
                    shared = sum(1 for ci, cj in zip(blk_info[i], blk_info[j])
                               if ci > 0 and cj > 0)
                    cb = "CROSS-BLOCK" if shared == 0 else f"same-block({shared})"
                    t7.append((i, j, meds, cb))

    # Curvature
    curve = [(i, j) for i in range(n_sec) for j in range(i + 1, n_sec)
             if k0[i, j] < eps and k1[i, j] > eps]

    # Print
    blk_names = [b[0] for b in block_slices]
    print(f"  System: {name}")
    print(f"  Dim={n}, gens={n_gen}, sectors={n_sec}")
    print(f"  Block composition:")
    for s_idx, comps in enumerate(blk_info):
        parts = [f"{bn}({c})" for bn, c in zip(blk_names, comps) if c > 0]
        print(f"    S{s_idx+1} dim={sum(comps)}: {' + '.join(parts)}")

    print(f"  Transport: {int(np.sum(A_dir))} direct edges")
    print(f"  Curvature (k0=0,k1>0): {len(curve)}")
    for ci, cj in curve:
        print(f"    S{ci+1}<->S{cj+1}: k0={k0[ci,cj]:.4f}, k1={k1[ci,cj]:.4f}")
    print(f"  T7 (K=k0=k1=0, reachable via composition): {len(t7)}")
    for i, j, meds, cb in t7:
        med_str = ",".join([f"S{k+1}" for k in meds])
        print(f"    S{i+1}<->S{j+1} via [{med_str}] [{cb}]")

    has_t7_cross = any(cb == "CROSS-BLOCK" for _, _, _, cb in t7)

    # Check block-preservation of k0, k1
    cross_k0 = 0
    cross_k1 = 0
    for i in range(n_sec):
        for j in range(i+1, n_sec):
            shared = sum(1 for ci, cj in zip(blk_info[i], blk_info[j]) if ci > 0 and cj > 0)
            if shared == 0:  # cross-block
                if k0[i, j] > eps:
                    cross_k0 += 1
                if k1[i, j] > eps:
                    cross_k1 += 1

    print(f"  Cross-block k0>0: {cross_k0}, Cross-block k1>0: {cross_k1}")

    return {'has_t7': len(t7) > 0, 'has_t7_cross': has_t7_cross,
            'n_sec': n_sec, 'edges': int(np.sum(A_dir)),
            'curve': len(curve), 't7': len(t7), 'K': K, 'k0': k0, 'k1': k1,
            'blk_info': blk_info, 'P': P}



# ====================================================================
# SYSTEMATIC SEARCH
# ====================================================================

def _s3_idx(g_perm):
    """Find S3_PERMUTATIONS index for a permutation array."""
    return S3_PERMUTATIONS.index(tuple(g_perm))

print("=" * 70)
print("APPROACH A: S3 with Center{A_3, A_2} joint diagonalization")
print("=" * 70)

# A_3 = average of all 3 transpositions (conjugacy class → central in C[G])
# A_2 = average of 2 transpositions (additional commuting structure)
gens_3 = [np.array([1,0,2]), np.array([0,2,1]), np.array([2,1,0])]  # (12),(23),(13)
gens_2 = [np.array([1,0,2]), np.array([0,2,1])]                      # (12),(23)

for name, get_rhos_A, get_rhos_B, blk_slices in [
    ("S3: nat(3) + nat(3), Center{A3,A2}",
     lambda gens: [build_s3_natural_rep(g) for g in gens],
     lambda gens: [build_s3_natural_rep(g) for g in gens],
     [('A', slice(0,3)), ('B', slice(3,6))]),
    ("S3: nat(3) + reg(6), Center{A3,A2}",
     lambda gens: [build_s3_natural_rep(g) for g in gens],
     lambda gens: [build_s3_regular_rep(_s3_idx(g)) for g in gens],
     [('A', slice(0,3)), ('B', slice(3,9))]),
    ("S3: reg(6) + reg(6), Center{A3,A2}",
     lambda gens: [build_s3_regular_rep(_s3_idx(g)) for g in gens],
     lambda gens: [build_s3_regular_rep(_s3_idx(g)) for g in gens],
     [('A', slice(0,6)), ('B', slice(6,12))]),
    ("S3: trivial(1)+sign(1)+nat(3), Center{A3,A2}",
     lambda gens: [np.array([[build_s3_trivial_rep(g)]]) for g in gens],
     lambda gens: [block_diag(np.array([[build_s3_sign_rep(g)]]), build_s3_natural_rep(g)) for g in gens],
     [('triv', slice(0,1)), ('sign', slice(1,2)), ('nat', slice(2,5))]),
]:
    rhos_A_all3 = get_rhos_A(gens_3)
    rhos_B_all3 = get_rhos_B(gens_3)
    rhos_3 = []
    for rA, rB in zip(rhos_A_all3, rhos_B_all3):
        rhos_3.append(block_diag(rA, rB))

    # Build center ops
    A_3 = sum(rhos_3) / 3

    rhos_A_2 = get_rhos_A(gens_2)
    rhos_B_2 = get_rhos_B(gens_2)
    rhos_2_all = []
    for rA, rB in zip(rhos_A_2, rhos_B_2):
        rhos_2_all.append(block_diag(rA, rB))
    A_2 = sum(rhos_2_all) / 2

    # Check commutativity
    comm_norm = np.linalg.norm(A_3 @ A_2 - A_2 @ A_3)
    print(f"\n  [{name}]")
    print(f"  [A_3, A_2] norm = {comm_norm:.2e}")

    analyze_v2(name, rhos_3, blk_slices, center_ops=[A_2])
    print()


print("=" * 70)
print("APPROACH B: S3 nat + reg with SUBSET averages to split degeneracies")
print("=" * 70)

# Full S3 group average (all 6 elements) — this is the "A_infinity"
all_s3 = [
    np.array([0,1,2]), np.array([1,0,2]), np.array([0,2,1]),
    np.array([2,1,0]), np.array([1,2,0]), np.array([2,0,1]),
]
rhos_nat_all6 = [build_s3_natural_rep(g) for g in all_s3]
rhos_reg_all6 = [build_s3_regular_rep(_s3_idx(g)) for g in all_s3]

rhos_6 = []
for rN, rR in zip(rhos_nat_all6, rhos_reg_all6):
    rhos_6.append(block_diag(rN, rR))

A_6 = sum(rhos_6) / 6

# A_transpositions = average of just the 3 transpositions
transpositions = [np.array([1,0,2]), np.array([0,2,1]), np.array([2,1,0])]
rhos_nat_t = [build_s3_natural_rep(g) for g in transpositions]
rhos_reg_t = [build_s3_regular_rep(_s3_idx(g)) for g in transpositions]
rhos_t = []
for rN, rR in zip(rhos_nat_t, rhos_reg_t):
    rhos_t.append(block_diag(rN, rR))
A_t = sum(rhos_t) / 3

# A_3cycles = average of the two 3-cycles
three_cycles = [np.array([1,2,0]), np.array([2,0,1])]
rhos_nat_3c = [build_s3_natural_rep(g) for g in three_cycles]
rhos_reg_3c = [build_s3_regular_rep(_s3_idx(g)) for g in three_cycles]
rhos_3c = []
for rN, rR in zip(rhos_nat_3c, rhos_reg_3c):
    rhos_3c.append(block_diag(rN, rR))
A_3c = sum(rhos_3c) / 2

print("  Using generators = all 6 S3 elements")
print(f"  [A_6, A_t] norm = {np.linalg.norm(A_6 @ A_t - A_t @ A_6):.2e}")
print(f"  [A_6, A_3c] norm = {np.linalg.norm(A_6 @ A_3c - A_3c @ A_6):.2e}")

analyze_v2("S3: nat(3)+reg(6), all 6 elements, Center{A6, At}", rhos_6,
           [('nat', slice(0,3)), ('reg', slice(3,9))], center_ops=[A_t])
print()

analyze_v2("S3: nat(3)+reg(6), all 6 elements, Center{A6, A3c}", rhos_6,
           [('nat', slice(0,3)), ('reg', slice(3,9))], center_ops=[A_3c])
print()


print("=" * 70)
print("APPROACH C: Manual construction with exact eigenvalue resonance")
print("=" * 70)

# We want:
# Block A: 3x3 with eigenvalues {1, 0, 0}
# Block B: 3x3 with eigenvalues {1, 0, -1}
# Resonance at λ=1 and λ=0 → hybrid sectors
# λ=-1 is pure-B

# Constructed from S3 generators acting on different representations
# Block A: natural (trivial + standard)
# Block B: sign + natural (but sign maps both generators to -1)

# Actually let me try: Block A = natural(3), Block B = sign ⊕ standard(2)
# standard is the 2-dim irrep of S3
# ρ_std((12)) = [[-1,0],[0,1]] in some basis, ρ_std((23)) = [[1/2, -√3/2],[-√3/2, -1/2]]

# Simpler: use the fact that regular = trivial ⊕ sign ⊕ 2*standard
# Take Block A = natural = trivial ⊕ standard
# Block B = sign ⊕ standard (3-dim subrep of regular)

# For S3 generators a=(12), b=(23):
gens_ab = [np.array([1,0,2]), np.array([0,2,1])]

# Block A: natural (3-dim)
rhos_A_ab = [build_s3_natural_rep(g) for g in gens_ab]

# Block B: sign ⊕ standard (1+2 = 3-dim)
# We need an explicit basis for the standard representation
# Actually, the orthogonal complement of [1,1,1] in the natural rep IS the standard rep
# So natural = trivial ⊕ standard, where:
#   trivial: span([1,1,1])
#   standard: {v: sum(v)=0}

# For block B = sign ⊕ standard:
# sign: 1-dim, ρ_sign(g) = parity(g) ∈ {±1}
# standard: 2-dim, from the natural rep's complement

# Make the standard rep explicit using natural rep on {0,1,2} minus trivial
# Standard basis vectors (orthogonal to [1,1,1]):
# e1 = [1, -1, 0]/√2
# e2 = [1, 1, -2]/√6

# For a transposition like (12): perm=[1,0,2]
# In the full 3-dim natural basis {|0⟩,|1⟩,|2⟩}: |0⟩→|1⟩, |1⟩→|0⟩, |2⟩→|2⟩
# In {trivial, e1, e2} basis:
# |triv⟩ = [1,1,1]/√3 → stays the same (trivial is invariant)
# e1 = [1,-1,0]/√2 → [-1,1,0]/√2 = -e1
# e2 = [1,1,-2]/√6 → [1,1,-2]/√6 = e2
# So ρ_std((12)) = diag(-1, 1) in {e1, e2} basis

# For transposition (23): perm=[0,2,1]
# e1 = [1,-1,0]/√2 → [1,0,-1]/√2 = (1/2)e1 + (-√3/2)e2
# e2 = [1,1,-2]/√6 → [1,-2,1]/√6 = (-√3/2)e1 + (-1/2)e2
# So ρ_std((23)) = [[1/2, -√3/2], [-√3/2, -1/2]]

# For 3-cycle (123): perm=[1,2,0]
# e1 = [1,-1,0]/√2 → [0,1,-1]/√2 = (-1/2)e1 + (√3/2)e2
# e2 = [1,1,-2]/√6 → [-2,1,1]/√6 = (√3/2)e1 + (-1/2)e2
# So ρ_std((123)) = [[-1/2, -√3/2], [√3/2, -1/2]]

# Let me just construct rho_std directly using numerical computation

# Use build_s3_std_rep from spectral_utils
print("  Standard rep verification:")
rho_std_id = build_s3_std_rep(np.array([0,1,2]))
rho_std_12 = build_s3_std_rep(np.array([1,0,2]))
rho_std_23 = build_s3_std_rep(np.array([0,2,1]))
print(f"    ρ(e)=I: {np.allclose(rho_std_id, np.eye(2))}")
# (12)(23) = (123)
rho_std_123 = build_s3_std_rep(np.array([1,2,0]))
print(f"    ρ((12)(23))=ρ(12)ρ(23): {np.allclose(rho_std_123, rho_std_12 @ rho_std_23, atol=1e-10)}")

# Now construct block-diagonal systems using standard rep
# System C1: Block A = trivial(1) + standard(2) = natural(3)
#            Block B = sign(1) + standard(2), 3-dim
# Resonance at standard eigenvalue → hybrid standard sectors

rhos_C1 = []
for g in gens_ab:
    # Block A: natural = trivial ⊕ standard (3-dim)
    rA = perm_matrix(g, 3)
    # Block B: sign ⊕ standard (1+2 = 3-dim)
    inv_count = 0
    for i in range(3):
        for j in range(i+1, 3):
            if g[i] > g[j]:
                inv_count += 1
    parity = -1.0 if inv_count % 2 == 1 else 1.0
    rB = block_diag(np.array([[parity]]), build_s3_std_rep(g))
    rhos_C1.append(block_diag(rA, rB))

analyze_v2("C1: S3 nat(3)=triv⊕std + sign⊕std(3), gens={a,b}", rhos_C1,
           [('A', slice(0,3)), ('B', slice(3,6))])
print()

# System C2: Use 3 transposition generators to get more structure
gens_3t = [np.array([1,0,2]), np.array([0,2,1]), np.array([2,1,0])]
rhos_C2 = []
for g in gens_3t:
    rA = perm_matrix(g, 3)
    inv_count = 0
    for i in range(3):
        for j in range(i+1, 3):
            if g[i] > g[j]:
                inv_count += 1
    parity = -1.0 if inv_count % 2 == 1 else 1.0
    rB = block_diag(np.array([[parity]]), build_s3_std_rep(g))
    rhos_C2.append(block_diag(rA, rB))

analyze_v2("C2: S3 nat(3)+sign⊕std(3), 3 transposition gens", rhos_C2,
           [('A', slice(0,3)), ('B', slice(3,6))])
print()


print("=" * 70)
print("APPROACH D: S4 with natural embeddings of different dimensions")
print("=" * 70)

# S4 generators: (12), (23), (34)
import itertools as it
S4_elems = [np.array(p) for p in it.permutations([0,1,2,3])]

def s4_perm_rep(gens, n_pts, point_set):
    """Build n_pts-dim permutation rep of S4 on a subset of points."""
    result = []
    for g in gens:
        mapping = {}
        for idx, p in enumerate(point_set):
            target = g[p]
            if target in point_set:
                mapping[idx] = list(point_set).index(target)
            else:
                mapping[idx] = idx
        perm_arr = np.zeros(len(point_set), dtype=int)
        for k, v in mapping.items():
            perm_arr[k] = v
        result.append(perm_matrix(perm_arr, len(point_set)))
    return result

gens_s4 = [np.array([1,0,2,3]), np.array([0,2,1,3]), np.array([0,1,3,2])]

# Block A: action on {0,1} (2-dim), Block B: action on {2,3} (2-dim)
# Block C: action on {0,1,2} (3-dim)
# These have different A-eigenvalues but some might coincide

rhos_D1_A = s4_perm_rep(gens_s4, 2, [0,1])
rhos_D1_B = s4_perm_rep(gens_s4, 2, [2,3])
rhos_D1_C = s4_perm_rep(gens_s4, 3, [0,1,2])

rhos_D1 = []
for rA, rB, rC in zip(rhos_D1_A, rhos_D1_B, rhos_D1_C):
    rhos_D1.append(block_diag(rA, rB, rC))

analyze_v2("D1: S4: 2pt(A:0,1)+2pt(B:2,3)+3pt(C:0,1,2), 3 transposition gens", rhos_D1,
           [('A2', slice(0,2)), ('B2', slice(2,4)), ('C3', slice(4,7))])
print()

# System D2: Block A = action on {0,1,2} (3-dim), Block B = action on {1,2,3} (3-dim)
# These overlap at {1,2}, which creates interesting resonance structure
rhos_D2_A = s4_perm_rep(gens_s4, 3, [0,1,2])
rhos_D2_B = s4_perm_rep(gens_s4, 3, [1,2,3])
rhos_D2 = []
for rA, rB in zip(rhos_D2_A, rhos_D2_B):
    rhos_D2.append(block_diag(rA, rB))

analyze_v2("D2: S4: 3pt(A:0,1,2)+3pt(B:1,2,3), overlapping, 3 gens", rhos_D2,
           [('A3', slice(0,3)), ('B3', slice(3,6))])
print()


print("=" * 70)
print("APPROACH E: D4 (dihedral-8) with 2D irreps")
print("=" * 70)

# D4 = ⟨r,s | r⁴=s²=e, srs=r⁻¹⟩, order 8
# Generators: r (rotation 90°), s (reflection)
# 2D irrep: ρ(r)=[[0,-1],[1,0]], ρ(s)=[[1,0],[0,-1]]

def d4_2d_irrep(gens):
    """2D faithful irrep of D4."""
    r = np.array([[0., -1.], [1., 0.]])
    s = np.array([[1., 0.], [0., -1.]])
    result = []
    for g_name in gens:
        if g_name == 'r':
            result.append(r)
        elif g_name == 's':
            result.append(s)
        elif g_name == 'r2':
            result.append(r @ r)
        elif g_name == 'r3':
            result.append(r @ r @ r)
        elif g_name == 'sr':
            result.append(s @ r)
        elif g_name == 'sr2':
            result.append(s @ r @ r)
        elif g_name == 'sr3':
            result.append(s @ r @ r @ r)
        elif g_name == 'e':
            result.append(np.eye(2))
    return result

# 1D irreps of D4:
# ρ_triv: all → 1
# ρ_det: r → −1, s → −1 (determinant of 2D rep)
# ρ_s: r → 1, s → −1
# ρ_rs: r → −1, s → 1

# Block A: 2D irrep, Block B: 2D irrep (different copy)
rhos_E1 = []
for g_name in ['r', 's']:
    rA = d4_2d_irrep([g_name])[0]
    rB = d4_2d_irrep([g_name])[0]
    rhos_E1.append(block_diag(rA, rB))

analyze_v2("E1: D4: 2D+2D same reps, gens={r,s}", rhos_E1,
           [('A', slice(0,2)), ('B', slice(2,4))])
print()

# Block A: 2D irrep, Block B: direct sum of 1D irreps (det + sign, 2-dim)
rhos_E2 = []
for g_name in ['r', 's']:
    rA = d4_2d_irrep([g_name])[0]
    if g_name == 'r':
        det_val = -1.0
        s_val = 1.0
    else:  # s
        det_val = -1.0
        s_val = -1.0
    rB = np.diag([det_val, s_val])
    rhos_E2.append(block_diag(rA, rB))

analyze_v2("E2: D4: 2D(A)+det⊕sgn(B), gens={r,s}", rhos_E2,
           [('A', slice(0,2)), ('B', slice(2,4))])
print()


print("=" * 70)
print("APPROACH F: Direct eigenvalue engineering — 4x4 block-diagonal")
print("=" * 70)
# Manually construct 2x2 blocks with matching eigenvalues
# Block A uses SO(2) rotations, Block B uses reflections
# Both have A-matrix with eigenvalues {cos(θ), cos(θ)} for symmetry

# Generator 1: block_diag(R(θ), H)  where R is rotation, H is reflection
# Generator 2: block_diag(R(-θ), I)
# Both are orthogonal matrices, so ρ(g) is a group representation (of some group)

theta = np.pi / 3  # 60 degrees
c, s = np.cos(theta), np.sin(theta)
R_p = np.array([[c, -s], [s, c]])   # rotation by +θ
R_m = np.array([[c, s], [-s, c]])   # rotation by -θ = R_p^{-1}
H = np.array([[1., 0.], [0., -1.]])  # reflection
I2 = np.eye(2)

rho_F1_g1 = block_diag(R_p, H)
rho_F1_g2 = block_diag(R_m, I2)

# Check: is this a group representation?
# g1² = block_diag(R_p², H²) = block_diag(R(2θ), I)
# g2² = block_diag(R_m², I) = block_diag(R(-2θ), I)
# g1 g2 = block_diag(R_p R_m, H) = block_diag(I, H)
# etc. This generates a finite group (since θ = π/3 gives R_p order 6)

analyze_v2("F1: Manual: R(π/3)+H, R(-π/3)+I", [rho_F1_g1, rho_F1_g2],
           [('A', slice(0,2)), ('B', slice(2,4))])
print()

# F2: Use θ = π/2 for order-4 behavior
theta2 = np.pi / 2
c2, s2 = 0.0, 1.0
R90 = np.array([[c2, -s2], [s2, c2]])
R270 = np.array([[c2, s2], [-s2, c2]])

rho_F2_g1 = block_diag(R90, H)
rho_F2_g2 = block_diag(R270, I2)

analyze_v2("F2: Manual: R(π/2)+H, R(-π/2)+I", [rho_F2_g1, rho_F2_g2],
           [('A', slice(0,2)), ('B', slice(2,4))])
print()

# F3: Add a third generator for more structure
rho_F3_g1 = block_diag(R_p, H)
rho_F3_g2 = block_diag(R_m, I2)
rho_F3_g3 = block_diag(I2, H)  # only acts on block B

analyze_v2("F3: Manual: R(π/3)+H, R(-π/3)+I, I+H",
           [rho_F3_g1, rho_F3_g2, rho_F3_g3],
           [('A', slice(0,2)), ('B', slice(2,4))])
print()


print("=" * 70)
print("APPROACH G: S3 × S3 with clever block structure")
print("=" * 70)
# S3 × S3 has order 36
# Block A: natural ⊗ trivial (S3 on first factor, 3-dim)
# Block B: trivial ⊗ natural (S3 on second factor, 3-dim)
# Generators: (a,e), (b,e), (e,a), (e,b) — 4 generators
# A = average over 4 generators

gens_s3 = [np.array([1,0,2]), np.array([0,2,1])]  # a=(12), b=(23)

rhos_G1 = []
# Generator (a, e): acts on block A only
rA_a = perm_matrix(gens_s3[0], 3)  # (12) on block A
rB_e = np.eye(3)
rhos_G1.append(block_diag(rA_a, rB_e))

# Generator (b, e): acts on block A only
rA_b = perm_matrix(gens_s3[1], 3)  # (23) on block A
rhos_G1.append(block_diag(rA_b, rB_e))

# Generator (e, a): acts on block B only
rA_e = np.eye(3)
rB_a = perm_matrix(gens_s3[0], 3)  # (12) on block B
rhos_G1.append(block_diag(rA_e, rB_a))

# Generator (e, b): acts on block B only
rB_b = perm_matrix(gens_s3[1], 3)  # (23) on block B
rhos_G1.append(block_diag(rA_e, rB_b))

# A_all = average of 4 generators
# Within each block, only 2 of the 4 generators act nontrivially
A_G1 = sum(rhos_G1) / 4

analyze_v2("G1: S3×S3: nat⊗triv + triv⊗nat, 4 gens", rhos_G1,
           [('A', slice(0,3)), ('B', slice(3,6))])
print()

# G2: Use Center{A_all, A_A, A_B} for joint diagonalization
# A_A = average of generators acting on block A only (first 2 gens)
A_A = (rhos_G1[0] + rhos_G1[1]) / 2
# A_B = average of generators acting on block B only (last 2 gens)
A_B = (rhos_G1[2] + rhos_G1[3]) / 2

analyze_v2("G2: S3×S3 with Center{A_all, A_A, A_B}", rhos_G1,
           [('A', slice(0,3)), ('B', slice(3,6))], center_ops=[A_A, A_B])
print()


print("=" * 70)
print("APPROACH H: S3 with DIFFERENT generator subsets per block")
print("=" * 70)
# Crucial idea: each block uses DIFFERENT generator-to-operator assignment
# This creates different A-eigenvalues per block, but some may coincide
#
# S3 generators: g1=(12), g2=(23), g3=(13)
# Block A: ρA(g1)=perm(12), ρA(g2)=perm(23), ρA(g3)=perm(13) — standard natural
# Block B: ρB(g1)=perm(23), ρB(g2)=perm(13), ρB(g3)=perm(12) — cyclically shifted
#
# A_A = (ρA(g1)+ρA(g2)+ρA(g3))/3 — natural rep average
# A_B = (ρB(g1)+ρB(g2)+ρB(g3))/3 — also natural rep average but with different assignment
#
# Actually in S3 all 3 transpositions are conjugate, so A_A = A_B in any basis.
# The eigenvalue spectrum is the same. Need different reps.

# Try: Block A = standard (2-dim irrep), Block B = natural (3-dim = trivial ⊕ standard)
# Standard lives inside natural. If A_std and A_nat share eigenvalues, we get resonance.

# Build standard rep explicitly for the 3 transpositions
rho_std_12 = build_s3_std_rep(np.array([1,0,2]))
rho_std_23 = build_s3_std_rep(np.array([0,2,1]))
rho_std_13 = build_s3_std_rep(np.array([2,1,0]))

rhos_H1 = []
for g in gens_3t:
    rA = build_s3_std_rep(g)  # standard, 2-dim
    rB = perm_matrix(g, 3)  # natural, 3-dim (trivial ⊕ standard)
    rhos_H1.append(block_diag(rA, rB))

analyze_v2("H1: S3: standard(2) + natural(3), 3 transposition gens", rhos_H1,
           [('std', slice(0,2)), ('nat', slice(2,5))])
print()


print("=" * 70)
print("APPROACH I: Full average over group vs subset average for Center")
print("=" * 70)
# Use S3 FULL GROUP (6 elements) as generators
# Block A: natural (3-dim) — only 3 distinct matrices (identity, 3 transpositions, 2 3-cycles)
# Block B: regular (6-dim) — 6 distinct matrices
#
# The key: use A_full (average over all 6) and A_transpositions (average over 3 transpositions)
# as Center operators. A_full is central in C[G] (it's the group average).
# A_transpositions is also central (transpositions form conjugacy class).

rhos_I_A6 = [build_s3_natural_rep(g) for g in all_s3]  # 6 matrices for natural rep (but only 3 distinct!)
rhos_I_B6 = [build_s3_regular_rep(_s3_idx(g)) for g in all_s3]   # 6 matrices for regular rep

rhos_I = []
for rA, rB in zip(rhos_I_A6, rhos_I_B6):
    rhos_I.append(block_diag(rA, rB))

A_full = sum(rhos_I) / 6

# A_transpositions
rhos_I_At_A = [build_s3_natural_rep(g) for g in transpositions]
rhos_I_At_B = [build_s3_regular_rep(_s3_idx(g)) for g in transpositions]
rhos_I_At = []
for rA, rB in zip(rhos_I_At_A, rhos_I_At_B):
    rhos_I_At.append(block_diag(rA, rB))
A_trans = sum(rhos_I_At) / 3

print(f"  [A_full, A_trans] norm = {np.linalg.norm(A_full @ A_trans - A_trans @ A_full):.2e}")

analyze_v2("I: S3 nat(3)+reg(6), full group gens, Center{A_full, A_trans}", rhos_I,
           [('nat', slice(0,3)), ('reg', slice(3,9))], center_ops=[A_trans])
print()


print("=" * 70)
print("APPROACH J: A4 (alternating group, order 12)")
print("=" * 70)

# A4 = even permutations of S4
# Generators: (123), (124) — two 3-cycles
# Irreps: trivial (1), two nontrivial 1D (ω, ω²), 3D (natural on 4 points minus trivial)

# 3D irrep of A4: natural action on 4 points projected to complement of [1,1,1,1]
# Equivalent to the standard rep of S4 restricted to A4

def a4_3d_irrep(g_perm_4):
    """3D irrep of A4."""
    nat4 = perm_matrix(g_perm_4, 4)
    P_triv = np.ones((4, 4)) / 4
    P_std = np.eye(4) - P_triv
    # Use basis orthogonal to [1,1,1,1]
    e1 = np.array([1, -1, 0, 0]) / np.sqrt(2)
    e2 = np.array([1, 1, -2, 0]) / np.sqrt(6)
    e3 = np.array([1, 1, 1, -3]) / np.sqrt(12)
    B = np.column_stack([e1, e2, e3])
    return B.T @ nat4 @ B

# A4 generators: (123), (124)  — note these are 3-cycles on {1,2,3,4}
a4_g1 = np.array([1,2,0,3])  # (123): 0→1, 1→2, 2→0, 3→3
a4_g2 = np.array([1,3,2,0])  # (124): 0→1, 1→3, 2→2, 3→0

# Also try (123) and (234)
a4_g3 = np.array([0,2,3,1])  # (234): 0→0, 1→2, 2→3, 3→1

# Block A: 3D irrep, Block B: 3D irrep (same)
rhos_J1 = []
for g in [a4_g1, a4_g2]:
    r3 = a4_3d_irrep(g)
    rhos_J1.append(block_diag(r3, r3))

analyze_v2("J1: A4: 3D+3D same irrep, gens={(123),(124)}", rhos_J1,
           [('A', slice(0,3)), ('B', slice(3,6))])
print()


print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Looking for: K=0, κ₀=0, κ₁=0 but reachable via 2-step composition")
print("Key signature: hybrid sectors bridging pure-block sectors")
print("Required: eigenvalue resonance across blocks + noncommutative generators")
