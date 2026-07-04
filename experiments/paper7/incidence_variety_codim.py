# ============================================================
# Codimension of the Incidence Variety I = {(A,B) : AB = 0}
# ============================================================
"""Compute and verify the codimension of I = {(A,B): AB = 0, A != 0, B != 0}
in the space of matrix pairs (A in C^{m x n}, B in C^{n x p}).

This quantifies WHY Type IV (incidence) obstructions are so rare:
they require hitting a high-codimension algebraic variety.

Key formula:
  For A of rank r, the fiber {B : AB = 0} has dimension np - p*r.
  The set of rank-r A has dimension r(m + n - r).
  So dim I_r = r(m+n-r) + np - pr = r(m+n-r-p) + np.
  Ambient dim = mn + np.
  codim I_r = mn + np - dim I_r = mn - r(m+n-r-p) - np + pr
            = mn - r(m+n-r) + pr

For the dominant (largest-dim) component at generic rank r*:
  r* = argmax_r dim I_r (subject to r < min(m,n) for A != 0, B != 0)
  codim I = min_{r < min(m,n)} [mn - r(m+n-r-p) + pr]

In particular, for square blocks (m=n=p=d):
  codim I_r = (d-r)^2 + dr = d^2 - dr + r^2.
  The optimal rank r* is near d/2, giving codim I approximately 3d^2/4.
"""

import os, sys
import numpy as np
from itertools import product

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'data')
LOG_PATH = os.path.join(OUT_DIR, '_incidence_codim.txt')

def log(msg):
    print(msg, flush=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('')


# ============================================================
# Formula derivation
# ============================================================

def incidence_dimension(m, n, p, r):
    """Dimension of I_r = {(A,B): AB=0, rank(A)=r}.

    A in C^{m x n}, B in C^{n x p}.

    dim{rank(A)=r} = r(m + n - r)   (determinantal variety)
    For fixed A of rank r: {B : AB=0} has dim = np - p*r   (kernel of A tensor I_p)
    Total: r(m+n-r) + np - pr = r(m+n-r-p) + np
    """
    return r * (m + n - r - p) + n * p


def incidence_codimension(m, n, p, r):
    """Codimension of I_r in the ambient space C^{m x n} x C^{n x p}."""
    ambient = m * n + n * p
    return ambient - incidence_dimension(m, n, p, r)


def type_iv_codimension(m, n, p):
    """Codimension of the Type IV locus: union over r < min(m,n) of I_r.

    For Type IV we need A != 0 (r >= 1) and B != 0 (requires r < min(m,n)
    so that ker(A) is nontrivial). The dominant component is at the r
    maximizing dim I_r (minimizing codim).

    Returns:
        min_codim: codimension of the largest component
        r_optimal: the rank achieving this codimension
        all_codims: dict r -> codim
    """
    best_r = None
    min_codim = float('inf')
    all_codims = {}
    for r in range(1, min(m, n)):  # r >= 1 (A != 0), r < min(m,n) (B != 0 possible)
        codim = incidence_codimension(m, n, p, r)
        all_codims[r] = codim
        if codim < min_codim:
            min_codim = codim
            best_r = r
    return min_codim, best_r, all_codims


# ============================================================
# Main analysis
# ============================================================

log("=" * 72)
log("  Codimension of the Incidence Variety I = {(A,B) : AB = 0}")
log("=" * 72)

log("""
  For A in C^{m x n}, B in C^{n x p}:

  I_r = {(A,B) : AB = 0, rank(A) = r}

  dim I_r = r(m + n - r - p) + np
  ambient dim = mn + np
  codim I_r = mn - r(m + n - r) + pr

  Type IV requires A != 0, B != 0:
    - A != 0 -> r >= 1
    - B != 0 possible -> r < min(m,n) (so ker(A) nontrivial)
""")

# ============================================================
# Case 1: Square blocks (most common for sectorized systems)
# ============================================================

log("\n" + "=" * 72)
log("  Case 1: Square blocks (m = n = p = d)")
log("=" * 72)

for d in [2, 3, 4, 5, 6, 8, 10]:
    codim, r_opt, all_codims = type_iv_codimension(d, d, d)
    ambient = 2 * d * d

    log(f"\n  d = {d}: ambient = {ambient}")
    log(f"    Optimal rank r* = {r_opt}: codim I = {codim}  ({codim/ambient:.1%} of ambient)")
    log(f"    All codims: { {r: c for r, c in sorted(all_codims.items())} }")

    # Sanity check: for full-rank A (r=d), B must be 0
    # dim I_d = dim{rank d A} + dim{B: AB=0 when rank=d}
    # For rank d: {B: AB=0} has dim dp - p*d = 0 (only B=0)
    # So I_d has only B=0, which is excluded for Type IV
    codim_full_rank = incidence_codimension(d, d, d, d)
    log(f"    Full-rank A (r={d}): dim fiber = 0 (only B=0), codim = {codim_full_rank}")

# ============================================================
# Case 2: Synthetic Type IV dimensions (m=3, n=2, p=3 for bridge 0->1->2)
# ============================================================

log("\n" + "=" * 72)
log("  Case 2: Synthetic Type IV (m=3, n=2, p=3)")
log("=" * 72)

m, n, p = 3, 2, 3
codim, r_opt, all_codims = type_iv_codimension(m, n, p)
ambient = m*n + n*p
log(f"  Ambient dim = {ambient}")
log(f"  Optimal rank r* = {r_opt}: codim I = {codim}  ({codim/ambient:.1%} of ambient)")
log(f"  All codims: { {r: c for r, c in sorted(all_codims.items())} }")

log(f"\n  Interpretation:")
log(f"    For r=1: A has rank 1 (out of max 2).")
log(f"    dim{{rank(A)=1}} = 1(3+2-1) = 4")
log(f"    For fixed rank-1 A: dim{{B: AB=0}} = 2*3 - 3*1 = 3")
log(f"    dim I_1 = 4 + 3 = 7")
log(f"    codim = (6+6) - 7 = 5")
log(f"    -> 5 complex equations must be satisfied.")

# ============================================================
# Case 3: General formula for d_i x d_k, d_k x d_j blocks
# ============================================================

log("\n" + "=" * 72)
log("  Case 3: General sector dimensions (d_i, d_k, d_j)")
log("=" * 72)

sector_configs = [
    (2, 3, 2, "small asymmetric"),
    (3, 4, 3, "medium asymmetric"),
    (5, 6, 5, "large asymmetric"),
    (4, 2, 4, "narrow bridge (thin k)"),
    (2, 5, 2, "wide bridge (thick k)"),
]

for di, dk, dj, desc in sector_configs:
    codim, r_opt, _ = type_iv_codimension(di, dk, dj)
    ambient = di*dk + dk*dj
    log(f"\n  ({di},{dk},{dj}) {desc}: ambient={ambient}, r*={r_opt}, codim={codim} ({codim/ambient:.1%})")
    # Rank deficiency also imposes additional codim
    # For A to have rank r < min(di,dk), the determinantal condition adds
    # (di-r)(dk-r) to the codimension
    full_rank = min(di, dk)
    det_codim = (di - r_opt) * (dk - r_opt) if r_opt < full_rank else 0
    log(f"    Full rank={full_rank}, rank deficiency codim={det_codim}")
    log(f"    Total effective codim >= {codim}")

# ============================================================
# Case 4: Why representations avoid Type IV
# ============================================================

log("\n" + "=" * 72)
log("  Case 4: Why representations generically avoid Type IV")
log("=" * 72)

log("""
  For a representation-derived system, projected blocks A = Q_i rho(g) Q_k
  and B = Q_k rho(h) Q_j are NOT generic matrices. They satisfy additional
  constraints:

  1. Block-rank preservation in rank-protected bridge products:
     In Wedderburn-coordinate sectors, nonzero blocks have full rank.
     Full-rank A implies ker(A) = {0}; B = 0 is the only solution to AB=0.
     So Type IV CANNOT occur with full-rank blocks.

  2. Even for rank-deficient blocks (outside Wedderburn coordinates):
     The blocks are correlated through the representation; A and B are
     not independent. The incidence variety I intersects the
     representation locus in a lower-dimensional subvariety.

  3. Mixed sectorization requirement:
     For Type IV to be possible, the sectorization must produce blocks
     that are simultaneously:
       - rank-deficient (to allow nontrivial ker(A))
       - nonzero (for R1 bridges)
       - exactly aligned so im(B) is contained in ker(A)
     This is a triple intersection of low-dimensional varieties.

  Quantitatively:
    Random matrices: P(AB=0 | A!=0, B!=0) = 0 (codim >= 1)
    Random d x d blocks: dominant codim I approximately 3d^2/4
    Representation-derived blocks: additional constraints push codim higher

  This explains:
    - Why earlier represented Type IV searches found 0 Type IV in 49,000+ element pairs
    - Why our represented atlas found 0 Type IV
    - Why Type IV is destroyed by epsilon = 10^{-4} perturbation
""")

# ============================================================
# Empirical verification: random matrix pairs
# ============================================================

log("\n" + "=" * 72)
log("  Empirical: AB=0 in random matrix pairs")
log("=" * 72)

for d in [2, 3, 4, 5]:
    n_samples = 100000
    hits = 0
    rng = np.random.RandomState(42)
    for _ in range(n_samples):
        A = rng.randn(d, d) + 1j * rng.randn(d, d)
        B = rng.randn(d, d) + 1j * rng.randn(d, d)
        # Check if AB is approximately 0 (with tolerance)
        prod_norm = np.linalg.norm(A @ B, 'fro')
        a_norm = np.linalg.norm(A, 'fro')
        b_norm = np.linalg.norm(B, 'fro')
        if prod_norm < 1e-10 * a_norm * b_norm and a_norm > 1e-10 and b_norm > 1e-10:
            hits += 1
    log(f"  d={d}: {hits}/{n_samples} random pairs have AB approximately 0 (A,B != 0)")

# ============================================================
# Perturbation experiment: how fast does AB=0 break?
# ============================================================

log("\n" + "=" * 72)
log("  Perturbation: AB=0 -> AB!=0 under noise")
log("=" * 72)

for d in [2, 3, 4]:
    rng = np.random.RandomState(42)
    # Construct a rank-deficient A with nontrivial kernel
    A = rng.randn(d, d) + 1j * rng.randn(d, d)
    A[:, -1] = 0  # make last column zero -> rank <= d-1
    # B: put nonzero entries only in the last row -> AB = 0
    B = np.zeros((d, d), dtype=complex)
    B[-1, :] = rng.randn(d) + 1j * rng.randn(d)

    # Verify AB = 0
    assert np.linalg.norm(A @ B, 'fro') < 1e-12
    log(f"\n  d={d}: constructed rank(A)={np.linalg.matrix_rank(A)}, AB=0 verified")

    # Perturb and check
    epsilons = np.logspace(-6, -1, 6)
    for eps in epsilons:
        breakdowns = 0
        n_trials = 100
        for _ in range(n_trials):
            N = rng.randn(d, d) + 1j * rng.randn(d, d)
            N = N / np.linalg.norm(N, 'fro')
            A_pert = A + eps * N
            prod = np.linalg.norm(A_pert @ B, 'fro')
            if prod > 1e-10:
                breakdowns += 1
        log(f"    epsilon={eps:.1e}: AB=0 broken in {breakdowns}/{n_trials} trials")

log(f"\nFull log: {LOG_PATH}")
log("Done.")
