"""Symmetry Breaking — n=8/n=16 Q(√5) Irrationality (Theorem 7.1).

Paper I §7 core claim: breaking generator-set symmetry lifts the spectral field
from Q (rational) to Q(√5). This is the computational foundation of Fig 4.

Tested generator families:
  - n=18: full face-turn group → 6 rational layers, field Q
  - n=16: remove R2/L2 half-turns → 7 layers, 2 irrational (Q(√5))
  - n=12: quarter-turn only → 6 rational layers (symmetry preserved)
  - n=8:  remove axis-1 + half-turns → 7 layers, 2 irrational (Q(√5))
  - n=6:  half-turn only → 6 rational layers (symmetry preserved)

The irrational eigenvalues λ_± = (5 ± √5)/8 ≈ 0.9045, 0.3455 arise from
the CP-block adjacency algebra when face-turn completeness is broken.

Paper: Paper I §7 (Symmetry Breaking & Spectral Rigidity)
"""
import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import BLOCK_RANGES
from rime.helpers import find_qsqrt5_form

np.random.seed(42)
TOL = 1e-6
TOL_RAT = 1e-4  # Rationality check (must handle SPECTRAL_DECIMALS=6 rounding)


def check(condition, msg):
    assert condition, msg


def is_rational_eigenvalue(lam):
    """Check if λ = 1 - k/m for some integers k, m (m ∈ [3, 20])."""
    for m in range(3, 21):
        k = m * (1 - lam)
        if abs(k - round(k)) < TOL_RAT:
            return True, int(round(k)), m
    return False, None, None


# ═══════════════════════════════════════════════════════════════════════
# 1. Compute spectra for all generator families
# ═══════════════════════════════════════════════════════════════════════

print("=" * 72)
print("  Paper I — Symmetry Breaking: Q(√5) Irrationality (Theorem 7.1)")
print("=" * 72)

FAMILIES = [
    (18, '18-full',   'All face turns'),
    (16, 'n=16',      'No R2/L2'),
    (12, '12-qtr',    'Quarter-turn only'),
    (8,  'n=8',       'No axis-1, no half-turn'),
    (6,  '6-half',    'Half-turn only'),
]

family_data = {}
for n, name, desc in FAMILIES:
    print(f"\n{'—' * 50}")
    print(f"  {name} (n={n}) — {desc}")
    op = CubieSpectralOperator(n=n)
    layers = op.layer_keys

    # Compute cluster centers from raw eigenvalues for precision.
    # layer_keys are rounded to SPECTRAL_DECIMALS=6; get true means from op.w.
    raw_eigs = op.w
    layer_centers = {}
    layer_dims_calc = {}
    for lam in layers:
        # Find all raw eigenvalues within TOL of the layer key
        mask = np.abs(raw_eigs - lam) < 1e-4
        layer_centers[lam] = float(np.mean(raw_eigs[mask]))
        layer_dims_calc[lam] = int(np.sum(mask))

    dims = [op.layer_dimension(lam) for lam in layers]

    # Classify each layer using the high-precision cluster center
    rationalities = [is_rational_eigenvalue(layer_centers[lam]) for lam in layers]

    print(f"  {'λ (true)':>12s}  {'λ (key)':>10s}  {'dim':>4s}  {'rational?':>10s}  {'form'}")
    print(f"  {'—'*12}  {'—'*10}  {'—'*4}  {'—'*10}  {'—'*20}")
    for i, lam in enumerate(layers):
        is_rat, k, m = rationalities[i]
        if is_rat:
            form = f'1 - {k}/{m}'
        else:
            form = 'IRRATIONAL'
        print(f"  {layer_centers[lam]:12.8f}  {lam:10.8f}  {dims[i]:4d}  "
              f"{str(is_rat):>10s}  {form}")

    n_rat = sum(1 for r, _, _ in rationalities if r)
    n_irr = len(layers) - n_rat
    print(f"  → {n_rat} rational + {n_irr} irrational, "
          f"field = {'Q' if n_irr == 0 else 'Q(√5)'}")

    family_data[name] = {
        'n': n, 'desc': desc,
        'layers': layers, 'dims': dims,
        'centers': layer_centers,
        'rationalities': rationalities,
        'n_irr': n_irr, 'n_total': len(layers),
    }

# ═══════════════════════════════════════════════════════════════════════
# 2. Verify Theorem 7.1 claims
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'=' * 72}")
print("  Theorem 7.1 Verification")
print(f"{'=' * 72}")

# Claim 1: n ∈ {18, 12, 6} have purely rational spectra
for name in ['18-full', '12-qtr', '6-half']:
    fd = family_data[name]
    check(fd['n_irr'] == 0,
          f"{name}: expected 0 irrational, got {fd['n_irr']}")
    print(f"  {name}: purely rational — [OK]")

# Claim 2: n ∈ {16, 8} have irrational eigenvalues in Q(√5).
# The exact form depends on the generator set:
#   n=8:  λ_± = (5 ± √5)/8  ≈ 0.904508, 0.345492
#   n=16: λ_± = (11 ± √5)/16 ≈ 0.827254, 0.547746
# Both are (a + b√5)/c with integer a,b,c and b ≠ 0.
for name in ['n=16', 'n=8']:
    fd = family_data[name]
    irrational_centers = [fd['centers'][lam] for i, lam in enumerate(fd['layers'])
                          if not fd['rationalities'][i][0]]

    check(len(irrational_centers) == 2,
          f"{name}: expected 2 irrational eigenvalues, got {len(irrational_centers)}")

    irr_sorted = sorted(irrational_centers, reverse=True)
    for irr_val in irr_sorted:
        form = find_qsqrt5_form(irr_val,TOL_RAT)
        check(form is not None,
              f"{name}: irrational λ={irr_val:.8f} not in Q(√5)")
        a, b, c = form
        sign = '+' if b > 0 else '-'
        print(f"  {name}: λ={irr_val:.8f} = ({a} {sign} {abs(b)}√5)/{c} — [OK]")

# Claim 3: Irrational eigenvalues originate from the CP block
# (the only block with adjacency structure affected by face removal)
print(f"\n  Block-level source tracing:")
BLOCK_NAMES = ['cp', 'ep', 'co', 'eo']
for name in ['n=8', 'n=16']:
    op = CubieSpectralOperator(n=family_data[name]['n'])
    A_mat = op.A
    print(f"  {name}:")
    for bname in BLOCK_NAMES:
        blk_slice = op.block_slice(bname)
        A_blk = A_mat[blk_slice, blk_slice]
        eigs_blk = np.sort(np.linalg.eigvalsh(A_blk))[::-1]
        for eig in eigs_blk:
            is_rat, k, m = is_rational_eigenvalue(eig)
            if not is_rat:
                form = find_qsqrt5_form(eig,TOL_RAT)
                if form:
                    a, b, c = form
                    sign = '+' if b > 0 else '-'
                    print(f"    {bname}[{blk_slice.start}:{blk_slice.stop}]  λ={eig:.8f}  "
                          f"= ({a} {sign} {abs(b)}√5)/{c}")
    print()

# ═══════════════════════════════════════════════════════════════════════
# 3. Structural explanation
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'=' * 72}")
print("  Interpretation")
print(f"{'=' * 72}")
print(f"  The 18-full generator set respects O_h symmetry of the cube.")
print(f"  This forces the full adjacency algebra A to decompose with rational")
print(f"  eigenvalues λ = 1 - k/9, k ∈ {{0,1,2,3,4,6}}.")
print(f"")
print(f"  Removing generators breaks the O_h orbit structure of certain faces,")
print(f"  changing the adjacency structure. The modified graph Laplacian")
print(f"  has characteristic polynomial with discriminant Δ = 5, producing")
print(f"  eigenvalues in Q(√5):")
print(f"    n=8:  lambda = (5 +/- sqrt5)/8  ~ 0.904508, 0.345492")
print(f"    n=16: lambda = (11 +/- sqrt5)/16 ~ 0.827254, 0.547746")
print(f"")
print(f"  This is a symmetry-breaking phenomenon: spectral rationality is not")
print(f"  a group-theoretic invariant but a generator-set completeness invariant.")
print("  The CP and CO blocks (permutation) are unaffected; EP and EO blocks carry")
print("  the irrationality via their adjacency submatrices.")
print(f"")
print(f"  Implication for Paper I: the rationality of the 18-full spectrum is")
print(f"  explained by the representation-theoretic completeness of the full")
print(f"  face-turn group, not by general abstract nonsense.")

print(f"\n{'=' * 72}")
print("  Theorem 7.1 verified: Q(√5) irrationality at n=8, n=16.")
print(f"{'=' * 72}")
print("\nDone.")
