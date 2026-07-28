"""Numerical separation of k=5 from the registered canonical spectrum.

Computationally verified:
  - k=5 corresponds to λ = 1 − 5/9 = 4/9 ≈ 0.444...
  - The computed eigenvalues of A₁₈ do not contain λ=4/9
  - The nearest computed eigenvalue is separated by the asserted tolerance

Paper: Paper I, Computational Proposition 3.5
Claim status: numerical check for the registered matrix
"""
import _bootstrap  # noqa: F401
import numpy as np
import sys
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove

np.random.seed(42)

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
A = op.A
layers = op.layer_keys

print("=" * 60)
print("  Paper I — Registered k=5 Absence Check")
print("=" * 60)

# 1. Direct spectral check
k_vals = sorted([op.lam_to_k(lam) for lam in layers])
print(f"\n  Observed k-values: {k_vals}")
print(f"  k=5 present: {5 in k_vals}")
all_k = set(range(10))
forbidden = all_k - set(k_vals)
print(f"  Unobserved k in 0..9: {sorted(forbidden)}")

# 2. Verify λ=4/9 is NOT an eigenvalue
lam_4_9 = 1 - 5/9  # = 4/9 ≈ 0.444444
evals = np.linalg.eigvalsh(A)
dist = np.min(np.abs(evals - lam_4_9))
print(f"\n  Distance from λ=4/9 to nearest eigenvalue: {dist:.2e}")
assert dist > 1e-3, f"λ=4/9 too close to spectrum: {dist:.2e}"

# 3. Non-zero residual: confirm k=4 and k=6 layers exist
k4_lam = 1 - 4/9  # = 5/9
k6_lam = 1 - 6/9  # = 1/3
d4 = np.min(np.abs(evals - k4_lam))
d6 = np.min(np.abs(evals - k6_lam))
sep4 = abs(k4_lam - lam_4_9)
sep6 = abs(k6_lam - lam_4_9)
print(f"  Presence residual for k=4 (λ=5/9): {d4:.2e}")
print(f"  Presence residual for k=6 (λ=1/3): {d6:.2e}")
print(f"  Separation |λ(k=4)-λ(k=5)|: {sep4:.2e}")
print(f"  Separation |λ(k=6)-λ(k=5)|: {sep6:.2e}")
assert d4 < 1e-6, "k=4 layer missing!"
assert d6 < 1e-6, "k=6 layer missing!"

# 4. Rational-ladder parametrization check
from rime.helpers import is_rational_form
k4_rational = is_rational_form(k4_lam, 9)
k6_rational = is_rational_form(k6_lam, 9)
k5_rational = is_rational_form(lam_4_9, 9)
print(f"\n  Rational form check (denom=9):")
print(f"    k=4 (λ=5/9): {k4_rational}")
print(f"    k=6 (λ=1/3): {k6_rational}")
print(f"    k=5 (λ=4/9): {k5_rational} (present in ℚ but absent in spectrum)")

# 5. Spectrum gaps
gaps = []
sorted_evals = sorted(set(np.round(evals, 6)))
for i in range(len(sorted_evals) - 1):
    gap = sorted_evals[i+1] - sorted_evals[i]
    if gap > 0.05:
        gaps.append((sorted_evals[i], sorted_evals[i+1], gap))
print(f"\n  Large spectral gaps (>0.05):")
for lo, hi, gap in gaps:
    print(f"    {lo:.4f} → {hi:.4f}  (gap = {gap:.4f})")

print(f"\n  ✓ k=5 is absent from the computed spectrum at the declared tolerance")
print(f"  ✓ Adjacent layers k=4 and k=6 confirmed present")
print(f"  ✓ The registered k=5 value lies between the computed k=4 and k=6 layers")
