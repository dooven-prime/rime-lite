"""Stability sweep — tolerance and random seed sensitivity analysis.

Verifies that the canonical structural quantities (sector count, T7, Comm)
are stable under:
  - Tolerance variation: tol in {1e-5, 1e-6, 1e-7}
  - Random seed variation: seed in {1, 42, 123}

Paper: Paper III (supplementary validation).
Invariant level: 2 (generator-conditioned).
"""
import numpy as np
from rime.cubieoperator import CubieSpectralOperator, TOL_KAPPA
from rime.spectral_utils import count_t7_pairs

TOLERANCES = [1e-5, 1e-6, 1e-7]
SEEDS = [1, 42, 123]

# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  Stability Sweep — Paper III Supplementary Validation")
print("=" * 80)


def compute_structural(op):
    """Compute key structural quantities for a given operator."""
    sec = op.center_decomposition()
    n_sec = sec['n_sectors']
    P = sec['projectors']

    K, k0, k1 = op.transport_kappa(P, compute_kappa1=True)
    bs = op.sector_block_support(P)
    t7, _ = count_t7_pairs(K, k0, k1, bs, tol_kappa=TOL_KAPPA)
    n_edges = int(np.sum(K > 0.05) - n_sec) // 2

    return {
        'n_layers': len(op._layers),
        'n_sectors': n_sec,
        't7': t7,
        'n_edges': n_edges,
        'layers': [round(lam, 6) for lam in sorted(op._layers, reverse=True)],
    }


# ═══════════════════════════════════════════════════════════════════
# Tolerance sweep
# ═══════════════════════════════════════════════════════════════════
print("\n─── Tolerance Sweep ───")
print(f"  {'tol':<10} {'layers':<8} {'sectors':<8} {'edges':<8} {'T7':<5} {'layers stable?'}")
print(f"  {'─'*10} {'─'*8} {'─'*8} {'─'*8} {'─'*5} {'─'*18}")

baseline = None
tol_results = {}
for tol in TOLERANCES:
    op = CubieSpectralOperator(tol=tol)
    r = compute_structural(op)
    tol_results[tol] = r
    if baseline is None:
        baseline = r
        stable = "—"
    else:
        same_layers = r['layers'] == baseline['layers']
        same_sectors = r['n_sectors'] == baseline['n_sectors']
        stable = "YES" if (same_layers and same_sectors) else "CHANGED"
    print(f"  {tol:<10} {r['n_layers']:<8} {r['n_sectors']:<8} {r['n_edges']:<8} {r['t7']:<5} {stable}")

# ═══════════════════════════════════════════════════════════════════
# Random seed sweep
# ═══════════════════════════════════════════════════════════════════
print(f"\n─── Random Seed Sweep ───")
print(f"  {'seed':<8} {'layers':<8} {'sectors':<8} {'edges':<8} {'T7':<5}")
print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*5}")

seed_results = {}
for seed in SEEDS:
    op = CubieSpectralOperator(seed=seed)
    r = compute_structural(op)
    seed_results[seed] = r
    print(f"  {seed:<8} {r['n_layers']:<8} {r['n_sectors']:<8} {r['n_edges']:<8} {r['t7']:<5}")

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════
print(f"\n─── Summary ───")

# Tolerance stability
all_same_tol = all(
    r['n_sectors'] == baseline['n_sectors'] and r['t7'] == baseline['t7']
    for r in tol_results.values()
)
print(f"  Tolerance sweep: sectors={baseline['n_sectors']}, T7={baseline['t7']} — "
      + ("STABLE across {1e-5, 1e-6, 1e-7}" if all_same_tol else "VARIATION DETECTED"))

# Seed stability
all_same_seed = all(
    r['n_sectors'] == seed_results[42]['n_sectors'] and r['t7'] == seed_results[42]['t7']
    for r in seed_results.values()
)
print(f"  Seed sweep:       sectors={seed_results[42]['n_sectors']}, T7={seed_results[42]['t7']} — "
      + ("STABLE across 3 seeds" if all_same_seed else "VARIATION DETECTED"))

print(f"\n  Canonical: layers={baseline['n_layers']}, sectors={baseline['n_sectors']}, "
      f"edges={baseline['n_edges']}, T7={baseline['t7']}")
print(f"{'=' * 80}")
print("  Done — stability sweep complete.")
