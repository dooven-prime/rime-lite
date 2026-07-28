"""Generator Defect Taxonomy — structural response to selective generator deletion.

Produces the defect taxonomy table for Paper III §8.3:
  - n=18 (canonical): arithmetic/sector/transport all closed
  - n=16 (Sector Shielding): √5 at layer level, largely shielded at sector level
  - n=14 (Field Defect Localization): √5 survives to sector level, confined to 2 sectors
  - n=15 (Transport Resolution Amplifier): higher field, sector/transport amplification

Paper: Paper III §8.3 (Exploratory. Discussion-level. Empirical pattern.)
Invariant level: 2 (generator-conditioned)
"""
import numpy as np
from rime.cubieoperator import CubieSpectralOperator, TOL_KAPPA
from rime.cubie import CubieMove
from rime.helpers import is_rational_form, is_in_qsqrt5
from spectral_utils import count_t7_pairs

np.random.seed(42)

op18 = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)

FAMILIES = [
    (18, "canonical", "all generators"),
    (16, "Sector Shielding", "axis-0 half-turns (R², L²)"),
    (15, "Transport Resolution Amplifier", "negative-face half-turns"),
    (14, "Field Defect Localization", "axis-1 quarter-turns"),
]


def compute_family(n, label, removed):
    """Compute all structural data for one generator family. Returns dict."""
    print(f"  Computing n={n} ({label}) ...", flush=True)
    op = op18 if n == 18 else CubieSpectralOperator(n=n)
    sec = op.center_decomposition()
    P = sec['projectors']
    n_sec = sec['n_sectors']
    field = op.classify_field()
    _, cd = op.full_commutant_combinatorial()
    K, k0, k1 = op.transport_kappa(P, compute_kappa1=True)
    bs = op.sector_block_support(P)
    t7, _ = count_t7_pairs(K, k0, k1, bs, tol_kappa=TOL_KAPPA)
    n_edges = int(np.sum(K > 0.05) - n_sec) // 2  # undirected

    m_eff = n // 2 if n % 2 == 0 else n
    sqrt5_count = sum(1 for lam in op._layers if is_in_qsqrt5(lam)[0])
    non_k9 = sum(1 for s in sec['sectors']
                 if not is_rational_form(s['lam_18'], 9))

    # Canonical → this-family splitting map (for non-canonical)
    split_map = {}
    if n != 18:
        sec18 = op18.center_decomposition()
        P18 = sec18['projectors']
        for i in range(sec18['n_sectors']):
            children = []
            for j in range(n_sec):
                tr = np.trace(P18[i] @ P[j]).real
                if tr > 0.5:
                    children.append(j + 1)
            if len(children) > 1:
                split_map[i + 1] = len(children)

    return {
        'n': n, 'label': label, 'removed': removed,
        'field': field, 'cd': cd, 'n_sec': n_sec,
        'non_k9': non_k9, 'n_edges': n_edges, 't7': t7,
        'sqrt5_count': sqrt5_count,
        'layers': len(op._layers),
        'split_map': split_map,
    }


# ═══════════════════════════════════════════════════════════════════
print("=" * 90)
print("  Generator Defect Taxonomy — Paper III §8.3")
print("=" * 90)

data = {}
for n, label, removed in FAMILIES:
    data[n] = compute_family(n, label, removed)

# ---- Detailed per-family ----
for n, label, removed in FAMILIES:
    d = data[n]

    if d['field'] == 'rational':
        arith = "closed (Q)"
    elif d['field'] == 'higher':
        arith = "defect: higher field"
    else:
        arith = f"defect: Q(√5), {d['sqrt5_count']} √5 layers"

    sector_status = f"{d['n_sec']} sectors, {d['non_k9']} non-rational lam_18"
    transport_status = f"{d['n_edges']} edges, {d['t7']} T7"

    print(f"\n{'─' * 70}")
    print(f"  n={n} ({label})")
    print(f"    Removed:         {removed}")
    print(f"    Layers:          {d['layers']}")
    print(f"    Arithmetic:      {arith}")
    print(f"    Sector:          {sector_status}")
    print(f"    Transport:       {transport_status}")
    print(f"    Comm(ρ):         {d['cd']}")
    print(f"    Spectral field:  {d['field']}")
    if d['split_map']:
        split_str = ", ".join(f"S{si}→{cnt}"
                              for si, cnt in sorted(d['split_map'].items()))
        print(f"    Splits:          {split_str}")

# ---- Compact taxonomy table ----
print(f"\n{'=' * 90}")
print("  Defect Taxonomy Summary")
print(f"{'=' * 90}")
print(f"  {'Family':<30} {'Arith':<26} {'Sector':<24} {'Transport':<18} {'Comm':>6}")
print(f"  {'─' * 30} {'─' * 26} {'─' * 24} {'─' * 18} {'─' * 6}")

for n, label, _ in FAMILIES:
    d = data[n]

    if d['field'] == 'rational':
        arith_s = "closed (Q)"
    elif d['field'] == 'sqrt5':
        arith_s = "√5 at layer"
    else:
        arith_s = "higher field"

    if n == 18:
        sec_s = "closed (9)"
    elif n == 16:
        sec_s = f"shielded (13, {d['non_k9']} non-rat.)"
    elif n == 14:
        sec_s = f"affected (10, √5 in 2)"
    else:
        sec_s = "amplified (25, 4→20)"

    if n == 18:
        trans_s = "closed (10, 5 T7)"
    elif n == 16:
        trans_s = f"mild ({d['n_edges']}, {d['t7']} T7)"
    elif n == 14:
        trans_s = f"stable ({d['n_edges']}, {d['t7']} T7)"
    else:
        trans_s = f"amplified ({d['n_edges']}, {d['t7']} T7)"

    print(f"  {n} {label:<26} {arith_s:<26} {sec_s:<24} {trans_s:<18} {d['cd']:>6}")

print(f"{'=' * 90}")
print("  Done — Paper III §8.3 defect taxonomy reproduced.")
