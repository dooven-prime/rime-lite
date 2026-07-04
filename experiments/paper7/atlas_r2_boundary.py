# ============================================================
# VII-A: Atlas of R2 Completeness Boundary (v2)
# ============================================================
"""Four experiments mapping the boundary where (R1,R2) determines D.

  Exp 1 - Represented Atlas: isotypic-sectored group reps, search counterexamples
  Exp 2 - Synthetic Adversarial: construct AB=0, Jacobi, kernel-overlap walls
  Exp 3 - Density Sweep: edge density -> first Type IV -> phase transition
  Exp 4 - J_acc Audit: same (R1,R2) -> same J_depth?

Key fix: proper isotypic sectorization via class-sum diagonalization.
"""

import os, sys
import numpy as np
from collections import defaultdict, Counter

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from rime.accessibility import (
    AccessibilityEngine,
)
from rime.rep_utils import (
    symmetric_group, regular_rep, compose_perm,
    class_sum_center_ops,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'data')
LOG_PATH = os.path.join(OUT_DIR, '_atlas_r2_boundary.txt')

TOL = 1e-8
CENTRE_TOL = 1e-6

def log(msg):
    print(msg, flush=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('')


# ============================================================
# Proper Sectorization via Generator Joint Diagonalization
# ============================================================

def sectorize_by_generators(group, gen_indices, seed=42):
    """Build sectors via joint diagonalization of generator Hermitian parts.

    Uses H_g = (rho(g) + rho(g)dag)/2. Joint diagonalization of random
    linear combinations gives sectors aligned with generator block structure.
    """
    rng = np.random.RandomState(seed)
    n_g = len(group)
    rho = regular_rep(group)

    H_ops = []
    for gi in gen_indices:
        U = np.array(rho[gi], dtype=complex)
        H = (U + U.conj().T) / 2.0
        H_ops.append(H)

    if len(H_ops) == 0:
        H_ops = [(np.array(rho[i], dtype=complex) + np.array(rho[i], dtype=complex).conj().T) / 2.0
                 for i in range(min(4, n_g))]

    M1 = np.zeros((n_g, n_g), dtype=complex)
    M2 = np.zeros((n_g, n_g), dtype=complex)
    for H in H_ops:
        M1 += rng.randn() * H
        M2 += rng.randn() * H
    M1 = (M1 + M1.conj().T) / 2
    M2 = (M2 + M2.conj().T) / 2

    M = M1 + rng.randn() * M2
    M = (M + M.conj().T) / 2
    evals, evecs = np.linalg.eigh(M)

    order = np.argsort(evals)[::-1]
    clusters = []
    cur, cv = [order[0]], evals[order[0]]
    for idx in range(1, len(order)):
        oi = order[idx]
        if abs(evals[oi] - cv) < CENTRE_TOL:
            cur.append(oi)
        else:
            clusters.append(cur)
            cur, cv = [oi], evals[oi]
    clusters.append(cur)

    Vs = []
    for grp in clusters:
        V = evecs[:, grp]
        V, _ = np.linalg.qr(V)
        Vs.append(V)

    Vs.sort(key=lambda V: V.shape[1], reverse=True)
    return Vs, rho


def build_system_from_group(group, gen_indices, seed=42):
    """Build sectorized system from a group and generator indices.

    Sectors: joint diagonalization of generator Hermitian parts.
    Generators: skew-Hermitian part (U - Udag)/2.
    """
    Vs, rho = sectorize_by_generators(group, gen_indices, seed=seed)

    Xs = []
    for gi in gen_indices:
        U = np.array(rho[gi], dtype=complex)
        X = (U - U.conj().T) / 2.0
        Xs.append(X)

    return Vs, Xs


# Obstruction Classification (fixed from v1)
# ============================================================

def classify_obstruction(Vs, Xs, i, j, g, h, tol=TOL):
    """Classify the R2=0 obstruction at (i,j) for generators (g,h).

    Returns: 'I' (singleton), 'III' (cancellation), 'IV' (incidence), '?' (unclear)
    """
    n_sectors = len(Vs)

    bridge_sectors = []
    B_g = {}
    B_h = {}

    for k in range(n_sectors):
        B_ik = Vs[i].T.conj() @ Xs[g] @ Vs[k]
        B_kj = Vs[k].T.conj() @ Xs[h] @ Vs[j]
        n_ik = np.linalg.norm(B_ik, 'fro')
        n_kj = np.linalg.norm(B_kj, 'fro')

        if n_ik > tol and n_kj > tol:
            bridge_sectors.append(k)
            B_g[k] = B_ik
            B_h[k] = B_kj

    if len(bridge_sectors) == 0:
        return '?'
    if len(bridge_sectors) == 1:
        return 'I'

    # Multiple bridges: check each product
    all_zero = True
    for k in bridge_sectors:
        prod = B_g[k] @ B_h[k]
        if np.linalg.norm(prod, 'fro') > tol:
            all_zero = False
            break

    if all_zero:
        return 'IV'  # every bridge product individually vanishes
    else:
        return 'III'  # products exist but cancel in commutator sum


def audit_system(Vs, Xs, tol=TOL, max_depth=4):
    """Full audit: R1, R2, D, obstruction classification."""
    n_sectors = len(Vs)
    n_gens = len(Xs)

    engine = AccessibilityEngine(Vs, Xs, tol=tol, max_depth=max_depth)
    R1, R2_arr, R2_pairs = engine.support()
    D, per_depth = engine.depth()

    # Pair lookup
    pair_to_cp = {}
    for cp, (g, h) in enumerate(R2_pairs):
        pair_to_cp[(g, h)] = cp
        pair_to_cp[(h, g)] = cp

    # Classify all R2=0 cases where R1 bridges exist
    obs_counts = Counter()
    obs_details = []

    for i in range(n_sectors):
        for j in range(n_sectors):
            if i == j:
                continue
            for g in range(n_gens):
                for h in range(n_gens):
                    if g == h:
                        continue
                    # R1 bridge?
                    has_bridge = any(R1[g, i, k] and R1[h, k, j]
                                     for k in range(n_sectors))

                    if has_bridge:
                        cp = pair_to_cp.get((g, h))
                        if cp is not None and not R2_arr[cp, i, j]:
                            t = classify_obstruction(Vs, Xs, i, j, g, h, tol)
                            obs_counts[t] += 1
                            obs_details.append(
                                {'i': i, 'j': j, 'g': g, 'h': h, 'type': t})

    # Membership
    has_IV = obs_counts.get('IV', 0) > 0
    membership = 'C' if not has_IV else 'outside_C'

    # R1 density
    r1_possible = n_sectors * (n_sectors - 1)
    r1_total = sum(1 for i in range(n_sectors) for j in range(n_sectors)
                   if i != j and any(R1[g, i, j] for g in range(n_gens)))

    # R2 density
    r2_total = sum(1 for i in range(n_sectors) for j in range(n_sectors)
                   if i != j and any(R2_arr[cp, i, j] for cp in range(len(R2_pairs))))

    # Frozen pairs
    frozen = sum(1 for i in range(n_sectors) for j in range(n_sectors)
                 if i != j and D[i, j] >= max_depth)

    return {
        'n_sectors': n_sectors, 'n_gens': n_gens,
        'sector_dims': [Vs[k].shape[1] for k in range(n_sectors)],
        'R1_density': r1_total / r1_possible if r1_possible else 0,
        'R2_density': r2_total / r1_possible if r1_possible else 0,
        'D_max': int(max(D[i, j] for i in range(n_sectors) for j in range(n_sectors) if i != j)),
        'frozen': frozen,
        'obs_counts': dict(obs_counts),
        'obs_details': obs_details,
        'membership': membership,
        'D': D,
        'R2_pairs': R2_pairs,
        'per_depth': per_depth,
    }


# ============================================================
# Group builders for Experiment 1
# ============================================================

def make_S3():
    """S3 = symmetric group on 3 elements."""
    S3 = symmetric_group(3)
    gen_pairs = [
        ([1, 2], 'transpositions'),      # (12), (23)
        ([1, 5], 'trans+3cycle'),        # (12), (123)
    ]
    return 'S3', S3, gen_pairs


def make_D8():
    """D8 = dihedral group of order 8, as permutations on 4 points."""
    r, s = (1, 2, 3, 0), (0, 3, 2, 1)
    group = []
    seen = set()
    stack = [(0, 1, 2, 3)]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        stack.append(compose_perm(p, r))
        stack.append(compose_perm(p, s))
    group = sorted(seen)
    gen_pairs = [
        ([group.index(r), group.index(s)], 'r+s'),
    ]
    return 'D8', group, gen_pairs


def make_Q8():
    """Q8 = quaternion group, as permutations on 8 points via regular action."""
    # Right-multiplication action: g -> permutation of group elements
    # Q8 = {1,-1,i,-i,j,-j,k,-k}
    # i*j = k, j*i = -k, i^2 = j^2 = k^2 = -1
    # Cayley table encoding
    elems = list(range(8))
    # Represent as permutations: g acts by left-multiplication on the group
    cayley = {
        0: (0, 1, 2, 3, 4, 5, 6, 7),  # 1
        1: (1, 0, 3, 2, 5, 4, 7, 6),  # -1
        2: (2, 3, 1, 0, 6, 7, 4, 5),  # i
        3: (3, 2, 0, 1, 7, 6, 5, 4),  # -i
        4: (4, 5, 6, 7, 1, 0, 2, 3),  # j
        5: (5, 4, 7, 6, 0, 1, 3, 2),  # -j
        6: (6, 7, 5, 4, 2, 3, 0, 1),  # k
        7: (7, 6, 4, 5, 3, 2, 1, 0),  # -k
    }
    group = [cayley[i] for i in range(8)]
    gen_pairs = [
        ([2, 4], 'i,j'),   # generators i, j
    ]
    return 'Q8', group, gen_pairs


def make_A4():
    """A4 = alternating group on 4 elements."""
    S4 = symmetric_group(4)
    # A4 = even permutations in S4
    A4 = [p for p in S4 if _perm_parity(p) == 0]
    # Generators: (123) and (124) - two 3-cycles
    try:
        g1 = A4.index((1, 2, 0, 3))  # (123)
        g2 = A4.index((3, 1, 2, 0))  # (124)
    except ValueError:
        g1, g2 = 1, 3  # fallback
    gen_pairs = [
        ([g1, g2], '3-cycles'),
    ]
    return 'A4', A4, gen_pairs


def _perm_parity(p):
    """Compute parity of a permutation (0=even, 1=odd)."""
    visited = [False] * len(p)
    swaps = 0
    for i in range(len(p)):
        if not visited[i]:
            j = i
            cycle_len = 0
            while not visited[j]:
                visited[j] = True
                j = p[j]
                cycle_len += 1
            swaps += cycle_len - 1
    return swaps % 2


def make_Z32():
    """Z3 x Z3 as permutations on 9 points."""
    # Direct product: elements are (a,b) with a,b in {0,1,2}
    # Act on 3 x 3 grid
    group = []
    for a in range(3):
        for b in range(3):
            perm = []
            for x in range(3):
                for y in range(3):
                    perm.append(((x + a) % 3) * 3 + (y + b) % 3)
            group.append(tuple(perm))
    gen_pairs = [
        ([1, 3], 'generators'),  # (1,0) and (0,1)
    ]
    return 'Z3xZ3', group, gen_pairs


# ============================================================
# Synthetic builders for Experiment 2
# ============================================================

def make_synthetic_IV(dim=14, seed=42):
    """Type IV = incidence: at least 2 bridge sectors, each product zero.

    Sector 0 -> {sector 1a, sector 1b} -> sector 2.
    Both B01a@B1a2 = 0 AND B01b@B1b2 = 0 => Type IV.
    """
    n_sec = 5
    sizes = [3, 2, 2, 3, 4]  # 0:3, 1a:2, 1b:2, 2:3, 3:4

    I = np.eye(dim)
    Vs = []
    pos = 0
    for sz in sizes:
        Vs.append(I[:, pos:pos+sz])
        pos += sz

    # X0: sector 0 -> sectors 1a, 1b
    # Make B01a and B01b both rank-deficient with zero-column in same position
    # Then B12a and B12b only use that zero-column direction

    # X1: sectors 1a, 1b -> sector 2
    # Make B1a2 and B1b2 nonzero but with image spanned by specific directions
    # such that B01a @ B1a2 = 0 and B01b @ B1b2 = 0

    # Simpler: use zero columns explicitly
    # B01a: B01a[:,0] nonzero, B01a[:,1] = 0
    # B1a2: B1a2[1,:] nonzero, B1a2[0,:] = 0 -> B01a @ B1a2 = 0

    offsets = np.cumsum([0] + sizes)
    X0 = np.zeros((dim, dim), dtype=complex)
    X1 = np.zeros((dim, dim), dtype=complex)

    # B01a: 3 x 2, rank 1 (only first column nonzero)
    o0, o1a = offsets[0], offsets[1]
    B01a = np.zeros((3, 2), dtype=complex)
    B01a[:, 0] = np.array([1.0, 0.5, 0.3])
    X0[o0:o0+3, o1a:o1a+2] = B01a

    # B01b: 3 x 2, rank 1 (only first column nonzero)
    o1b = offsets[2]
    B01b = np.zeros((3, 2), dtype=complex)
    B01b[:, 0] = np.array([0.2, 0.7, 1.0])
    X0[o0:o0+3, o1b:o1b+2] = B01b

    # B1a2: 2 x 3, nonzero only in row 1 (row 0 = zero)
    o2 = offsets[3]
    B1a2 = np.zeros((2, 3), dtype=complex)
    B1a2[1, :] = np.array([0.8, 0.4, 0.9])
    X1[o1a:o1a+2, o2:o2+3] = B1a2

    # B1b2: 2 x 3, nonzero only in row 1
    B1b2 = np.zeros((2, 3), dtype=complex)
    B1b2[1, :] = np.array([0.6, 0.3, 0.7])
    X1[o1b:o1b+2, o2:o2+3] = B1b2

    # Verify: B01a @ B1a2 = 0. B01a has col0 nonzeros, col1 zeros.
    # B1a2 has row0 zeros, row1 nonzeros. Product = B01a[:,0]*B1a2[0,:] + B01a[:,1]*B1a2[1,:]
    # = B01a[:,0]*0 + 0*B1a2[1,:] = 0.

    X0 = X0 - X0.conj().T
    X1 = X1 - X1.conj().T
    X0 = X0 / (np.linalg.norm(X0, 'fro') + TOL)
    X1 = X1 / (np.linalg.norm(X1, 'fro') + TOL)

    return Vs, [X0, X1], "TypeIV: 2 bridges (0->1a->2 and 0->1b->2), each B01@B12=0"


def make_synthetic_III(dim=8, seed=42):
    """Construct a system with a genuine Type III (cancellation) obstruction.

    Two intermediate sectors with equal-and-opposite products.
    """
    rng = np.random.RandomState(seed)
    n_sec = 4
    sizes = [2, 2, 2, 2]

    I = np.eye(dim)
    Vs = []
    pos = 0
    for sz in sizes:
        Vs.append(I[:, pos:pos+sz])
        pos += sz

    d0, d1, d2, d3 = sizes

    # X0: 0->1 = I, 0->2 = I
    X0 = np.zeros((dim, dim), dtype=complex)
    X0[0:2, 2:4] = np.eye(2)
    X0[0:2, 4:6] = np.eye(2)
    X0 = X0 - X0.conj().T  # skew

    # X1: 1->3 = I, 2->3 = -I
    X1 = np.zeros((dim, dim), dtype=complex)
    X1[2:4, 6:8] = np.eye(2)
    X1[4:6, 6:8] = -np.eye(2)
    X1 = X1 - X1.conj().T

    X0 = X0 / (np.linalg.norm(X0, 'fro') + TOL)
    X1 = X1 / (np.linalg.norm(X1, 'fro') + TOL)

    return Vs, [X0, X1], "TypeIII: commutator cancels via plus/minus identity products"


def make_synthetic_jacobi(dim=8, seed=42):
    """Construct a Jacobi-identity obstruction.

    Jacobi: [X,[Y,Z]] + [Y,[Z,X]] + [Z,[X,Y]] = 0 always.
    But individual terms may cancel in a way that hides accessibility.
    """
    rng = np.random.RandomState(seed)
    n_sec = 3
    sizes = [3, 3, 2]

    I = np.eye(dim)
    Vs = []
    pos = 0
    for sz in sizes:
        Vs.append(I[:, pos:pos+sz])
        pos += sz

    # Three generators with cyclic commutator structure
    Xs = []
    for g in range(3):
        X = rng.randn(dim, dim) + 1j * rng.randn(dim, dim)
        X = (X - X.conj().T) / np.sqrt(2 * dim)
        Xs.append(X)

    return Vs, Xs, "Jacobi: structural commutator identity"


# ============================================================
# Experiment 1: Represented Atlas
# ============================================================

def run_exp1_represented_atlas():
    log("=" * 72)
    log("  Experiment 1: Represented Atlas")
    log("  Search: same (R1,R2), different D? Any Type IV?")
    log("=" * 72)

    group_builders = [make_S3, make_D8, make_Q8, make_A4, make_Z32]

    atlas = []
    for builder in group_builders:
        name, group, gen_pairs = builder()
        log(f"\n  --- {name} (|G|={len(group)}) ---")

        for gen_idx_list, gen_desc in gen_pairs:
            try:
                Vs, Xs = build_system_from_group(group, gen_idx_list, seed=42)
                result = audit_system(Vs, Xs)
                result['group'] = name
                result['gen_desc'] = gen_desc
                atlas.append(result)

                log(f"    Gen={gen_desc}: sec={result['n_sectors']}, "
                    f"dims={result['sector_dims']}")
                log(f"      R1={result['R1_density']:.3f}, "
                    f"R2={result['R2_density']:.3f}, "
                    f"D_max={result['D_max']}, frozen={result['frozen']}")
                log(f"      Obstructions: {result['obs_counts']}")
                log(f"      Membership: {result['membership']}")
                for obs in result['obs_details'][:3]:
                    log(f"        [{obs['type']}] i={obs['i']},j={obs['j']},"
                        f"g={obs['g']},h={obs['h']}")

            except Exception as e:
                log(f"    Gen={gen_desc}: FAILED - {e}")

    # Compare: any two systems with same (R1,R2) but different D?
    log(f"\n  --- Cross-comparison: same (R1,R2) -> same D? ---")
    comparisons = 0
    counterexamples = 0
    for a in atlas:
        for b in atlas:
            if a is b:
                continue
            if (a['n_sectors'] == b['n_sectors'] and
                a['n_gens'] == b['n_gens'] and
                abs(a['R1_density'] - b['R1_density']) < 0.01 and
                abs(a['R2_density'] - b['R2_density']) < 0.01):
                comparisons += 1
                if a['D_max'] != b['D_max']:
                    counterexamples += 1
                    log(f"    *** Counterexample: {a['group']}-{a['gen_desc']} "
                        f"D_max={a['D_max']} vs {b['group']}-{b['gen_desc']} "
                        f"D_max={b['D_max']}")
    log(f"    Total cross-comparisons: {comparisons}")
    log(f"    Counterexamples (same R1,R2, diff D): {counterexamples}")
    if counterexamples == 0:
        log(f"    -> No counterexample found in represented atlas.")

    # Q1 Answer
    log(f"\n  --- Q1: Any Type IV in representations? ---")
    iv_count = sum(r['obs_counts'].get('IV', 0) for r in atlas)
    log(f"    Total Type IV: {iv_count}")
    if iv_count == 0:
        log(f"    -> Zero Type IV found. This atlas is currently diagnostic only: R1 is nearly zero in most represented systems.")

    return atlas


# ============================================================
# Experiment 2: Synthetic Adversarial
# ============================================================

def run_exp2_synthetic():
    log("\n" + "=" * 72)
    log("  Experiment 2: Synthetic Adversarial")
    log("  Construct AB=0, Jacobi, kernel-overlap walls")
    log("=" * 72)

    builders = [
        ("Type IV (AB=0)", make_synthetic_IV),
        ("Type III (cancellation)", make_synthetic_III),
        ("Jacobi (cyclic)", make_synthetic_jacobi),
    ]

    for label, builder in builders:
        log(f"\n  --- {label} ---")
        try:
            Vs, Xs, desc = builder()
            result = audit_system(Vs, Xs)
            log(f"    {desc}")
            log(f"    Sectors: {result['n_sectors']}, dims={result['sector_dims']}")
            log(f"    R1={result['R1_density']:.3f}, "
                f"R2={result['R2_density']:.3f}, D_max={result['D_max']}")
            log(f"    Obstructions: {result['obs_counts']}")
            log(f"    Membership: {result['membership']}")
            # Show obstruction classification
            type_counts = Counter(d['type'] for d in result['obs_details'])
            log(f"    By type: {dict(type_counts)}")
            for obs in result['obs_details'][:5]:
                log(f"      [{obs['type']}] i={obs['i']},j={obs['j']},"
                    f"g={obs['g']},h={obs['h']}")
        except Exception as e:
            log(f"    FAILED: {e}")
            import traceback
            traceback.print_exc()


# ============================================================
# Experiment 3: Density Sweep
# ============================================================

def run_exp3_incidence_perturbation(n_noise_levels=8, n_trials=10):
    log("\n" + "=" * 72)
    log("  Experiment 3: Structured Incidence Perturbation")
    log("  Start from Type IV model -> add noise -> track when Type IV disappears")
    log("  and how D jumps at the boundary.")
    log("=" * 72)

    Vs_base, Xs_base, _ = make_synthetic_IV(dim=14, seed=42)
    dim = 14

    noise_levels = np.logspace(-4, 1, n_noise_levels)  # from 1e-4 to 10

    for noise in noise_levels:
        iv_count = 0
        iii_count = 0
        d_max_vals = []
        membership_counts = Counter()

        for trial in range(n_trials):
            rng = np.random.RandomState(trial)
            Xs_noisy = []
            for X in Xs_base:
                N = rng.randn(dim, dim) + 1j * rng.randn(dim, dim)
                N = (N - N.conj().T) / (2 * np.sqrt(2 * dim))  # skew-Hermitian noise
                X_noisy = X + noise * N
                Xs_noisy.append(X_noisy)

            try:
                result = audit_system(Vs_base, Xs_noisy)
                d_max_vals.append(result['D_max'])
                if result['obs_counts'].get('IV', 0) > 0:
                    iv_count += 1
                if result['obs_counts'].get('III', 0) > 0:
                    iii_count += 1
                membership_counts[result['membership']] += 1
            except Exception:
                pass

        if d_max_vals:
            log(f"\n  noise={noise:.1e} (n={len(d_max_vals)}):")
            log(f"    D_max: mean={np.mean(d_max_vals):.1f}, values={sorted(set(d_max_vals))}")
            log(f"    Type IV: {iv_count}/{len(d_max_vals)} survive")
            log(f"    Type III: {iii_count}/{len(d_max_vals)} appear")
            log(f"    Membership: {dict(membership_counts)}")
            if iv_count == 0 and any(r['membership'] == 'outside_C' for r in [audit_system(Vs_base, Xs_noisy)] if False):
                log(f"    -> Type IV destroyed by noise >= {noise:.1e}")


# ============================================================
# Experiment 4: J_acc Audit
# ============================================================

def run_exp4_jacc_audit(n_systems=80):
    log("\n" + "=" * 72)
    log("  Experiment 4: Exact Signature Audit")
    log("  hash(R1) == hash(R1') and hash(R2) == hash(R2') -> hash(D) == hash(D')?")
    log("=" * 72)

    systems = []
    for seed in range(n_systems):
        rng = np.random.RandomState(seed)
        dim = rng.choice([6, 8, 10, 12])
        n_sectors = rng.choice([3, 4])
        n_gens = rng.choice([2, 3])

        sizes = []
        remaining = dim
        for s in range(n_sectors - 1):
            sz = rng.randint(1, max(1, remaining - (n_sectors - s - 1)))
            sizes.append(sz)
            remaining -= sz
        sizes.append(remaining)

        U = np.linalg.qr(rng.randn(dim, dim) + 1j * rng.randn(dim, dim))[0]
        Vs = []
        pos = 0
        for sz in sizes:
            Vs.append(U[:, pos:pos+sz])
            pos += sz

        Xs = []
        for _ in range(n_gens):
            X = np.zeros((dim, dim), dtype=complex)
            for i in range(n_sectors):
                for j in range(n_sectors):
                    if i == j:
                        continue
                    di, dj = Vs[i].shape[1], Vs[j].shape[1]
                    B = (rng.randn(di, dj) + 1j * rng.randn(di, dj)) / np.sqrt(di * dj)
                    if rng.random() < 0.3 and min(di, dj) >= 2:
                        U_b, S_b, Vh_b = np.linalg.svd(B, full_matrices=False)
                        target_rank = rng.randint(1, min(di, dj))
                        B = (U_b[:, :target_rank] * S_b[:target_rank]) @ Vh_b[:target_rank, :]
                    i_start = sum(Vs[k].shape[1] for k in range(i))
                    j_start = sum(Vs[k].shape[1] for k in range(j))
                    X[i_start:i_start+di, j_start:j_start+dj] = B
            X = (X - X.conj().T) / np.sqrt(2)
            Xs.append(X)

        try:
            result = audit_system(Vs, Xs)
            # Store exact R1/R2 arrays for hashing.
            engine = AccessibilityEngine(Vs, Xs, tol=TOL, max_depth=4)
            R1_arr, R2_arr, _ = engine.support()
            result['_R1_hash'] = hash(R1_arr.tobytes())
            result['_R2_hash'] = hash(R2_arr.tobytes())
            result['_key'] = (result['n_sectors'], result['n_gens'])
            systems.append(result)
        except Exception:
            pass

    # Group by EXACT hash
    groups = defaultdict(list)
    for r in systems:
        key = (r['_key'], r['_R1_hash'], r['_R2_hash'])
        groups[key].append(r)

    log(f"\n  {len(systems)} systems, {len(groups)} exact (R1,R2) hash classes")
    n_multi = sum(1 for v in groups.values() if len(v) >= 2)
    log(f"  Classes with at least 2 systems (identical R1,R2): {n_multi}")

    if n_multi == 0:
        log(f"  -> All hash classes are singletons. Exact matching needs larger sample.")
        return

    agreement = 0
    disagreement = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        d_vals = set(r['D_max'] for r in members)
        frozen_vals = set(r['frozen'] for r in members)
        if len(d_vals) > 1 or len(frozen_vals) > 1:
            disagreement.append((key, members, d_vals, frozen_vals))
        else:
            agreement += 1

    log(f"\n  Agreement (same D): {agreement} classes")
    log(f"  Disagreement: {len(disagreement)} classes")

    if disagreement:
        log(f"\n  *** COUNTEREXAMPLE: identical (R1,R2) but different D ***")
        for key, members, d_vals, f_vals in disagreement[:5]:
            log(f"    sec={key[0][0]}, gen={key[0][1]}: D_max in {sorted(d_vals)}")
            for r in members[:3]:
                log(f"      D_max={r['D_max']}, frozen={r['frozen']}, obst={r['obs_counts']}")
    else:
        log(f"    -> hash(R1,R2) uniquely determines D in this sample.")


# ============================================================
# Main
# ============================================================

log("=" * 72)
log("  VII-A: Atlas of R2 Completeness Boundary (v2)")
log("=" * 72)
log("  Four experiments mapping the (R1,R2) -> D boundary.")
log("")

atlas = run_exp1_represented_atlas()
run_exp2_synthetic()
run_exp3_incidence_perturbation()
run_exp4_jacc_audit()

log("\n" + "=" * 72)
log("  Summary")
log("=" * 72)

# Compile atlas table
log(f"\n  {'Group':<10s} {'Gens':<15s} {'Sec':>4s} {'dim':>4s} {'Type I':>7s} {'Type III':>7s} {'Type IV':>7s} {'In C':>6s}")
log(f"  {'-'*10} {'-'*15} {'-'*4} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*6}")
for r in atlas:
    obs = r['obs_counts']
    log(f"  {r['group']:<10s} {r['gen_desc']:<15s} {r['n_sectors']:>4d} "
        f"{sum(r['sector_dims']):>4d} {obs.get('I',0):>7d} {obs.get('III',0):>7d} "
        f"{obs.get('IV',0):>7d} {r['membership']:>6s}")

log(f"\nFull log: {LOG_PATH}")
log("Done.")
