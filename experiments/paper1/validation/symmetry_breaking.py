"""Registered generator-family contrast for Paper I.

This script computes a finite census for five declared generator families. It
recognizes the two non-rational-ladder values in the n=8 and n=16 families as
Q(√5) candidates and supplies the data summarized in Figure 4. It does not
establish a theorem for arbitrary symmetry-broken generator families.

Tested generator families:
  - n=18: full face-turn group → 6 rational layers, field Q
  - n=16: remove R2/L2 half-turns → 9 layers, 2 Q(√5) candidates
  - n=12: quarter-turn only → 6 rational layers (symmetry preserved)
  - n=8:  remove axis-1 + half-turns → 7 layers, 2 Q(√5) candidates
  - n=6:  half-turn only → 3 rational layers

The recognized Q(√5) values occur in the EP and EO blocks for the registered
n=8 and n=16 families.

Paper: Paper I, Computational Observation 7.1
"""
import _bootstrap  # noqa: F401
import numpy as np
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import BLOCK_RANGES
from rime.helpers import find_qsqrt5_form

np.random.seed(42)
TOL = 1e-6
TOL_RAT = 1e-4  # Rationality check (must handle SPECTRAL_DECIMALS=6 rounding)


def check(condition, msg):
    assert condition, msg


def matches_rational_ladder(lam):
    """Operationally test λ = 1-k/m for integers k and 3 <= m <= 20."""
    for m in range(3, 21):
        k = m * (1 - lam)
        if abs(k - round(k)) < TOL_RAT:
            return True, int(round(k)), m
    return False, None, None


# ═══════════════════════════════════════════════════════════════════════
# 1. Compute spectra for all generator families
# ═══════════════════════════════════════════════════════════════════════

print("=" * 72)
print("  Paper I — Registered Generator-Family Spectral Contrast")
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
    rationalities = [matches_rational_ladder(layer_centers[lam]) for lam in layers]

    print(f"  {'λ (true)':>12s}  {'λ (key)':>10s}  {'dim':>4s}  {'ladder?':>10s}  {'form'}")
    print(f"  {'—'*12}  {'—'*10}  {'—'*4}  {'—'*10}  {'—'*20}")
    for i, lam in enumerate(layers):
        is_rat, k, m = rationalities[i]
        if is_rat:
            form = f'1 - {k}/{m}'
        else:
            form = 'NON-LADDER'
        print(f"  {layer_centers[lam]:12.8f}  {lam:10.8f}  {dims[i]:4d}  "
              f"{str(is_rat):>10s}  {form}")

    n_rat = sum(1 for r, _, _ in rationalities if r)
    n_irr = len(layers) - n_rat
    print(f"  → {n_rat} rational-ladder matches + {n_irr} non-ladder values")

    family_data[name] = {
        'n': n, 'desc': desc,
        'layers': layers, 'dims': dims,
        'centers': layer_centers,
        'rationalities': rationalities,
        'n_irr': n_irr, 'n_total': len(layers),
    }

# ═══════════════════════════════════════════════════════════════════════
# 2. Verify the registered finite-family observations
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'=' * 72}")
print("  Registered Family Checks")
print(f"{'=' * 72}")

# Check 1: registered n in {18, 12, 6} match rational ladders.
for name in ['18-full', '12-qtr', '6-half']:
    fd = family_data[name]
    check(fd['n_irr'] == 0,
          f"{name}: expected 0 irrational, got {fd['n_irr']}")
    print(f"  {name}: all values match a rational ladder — [OK]")

# Check 2: registered n in {16, 8} have two Q(√5) candidates.
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

# Trace the recognized Q(√5) candidates to the registered blocks.
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
            is_rat, k, m = matches_rational_ladder(eig)
            if not is_rat:
                form = find_qsqrt5_form(eig,TOL_RAT)
                if form:
                    a, b, c = form
                    sign = '+' if b > 0 else '-'
                    print(f"    {bname}[{blk_slice.start}:{blk_slice.stop}]  λ={eig:.8f}  "
                          f"= ({a} {sign} {abs(b)}√5)/{c}")
    print()

# ═══════════════════════════════════════════════════════════════════════
# 3. Claim-status-aware interpretation
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'=' * 72}")
print("  Interpretation")
print(f"{'=' * 72}")
print(f"  The registered 18-full face-turn family has the computed rational")
print(f"  ladder λ = 1-k/9, k in {{0,1,2,3,4,6}}.")
print(f"")
print(f"  In the registered n=8 and n=16 controls, removing generators changes")
print(f"  the computed block spectra and yields values recognized in Q(sqrt(5)):")
print(f"    n=8:  lambda = (5 +/- sqrt5)/8  ~ 0.904508, 0.345492")
print(f"    n=16: lambda = (11 +/- sqrt5)/16 ~ 0.827254, 0.547746")
print(f"")
print(f"  This finite contrast shows that the group and representation dimension")
print(f"  alone do not determine rationality. It does not prove that generator-set")
print(f"  completeness is necessary or sufficient in general.")
print("  In these registered controls, the recognized values occur in EP and EO.")
print(f"")
print(f"  Paper I records this as a computational observation and negative control,")
print(f"  separate from the conditional partition-integrality theorem.")

print(f"\n{'=' * 72}")
print("  Registered n=8/n=16 Q(sqrt(5)) candidates reproduced.")
print(f"{'=' * 72}")
print("\nDone.")
