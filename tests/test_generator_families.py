"""Theorem verification:
  - n=14: sqrt5 field, 10 sectors, T7=5 (canonical), Comm(ρ)=675
  - n=14: √5 localized in 2 sectors (S3, S8), both EP+EO blocks
  - n=15: higher field, 25 sectors, T7=24 (amplified), Comm(ρ)=610
  - n=15: Transport Resolution Amplifier — 4 canonical sectors split
  - n=16: sqrt5 field, 13 sectors, T7=11, Comm(ρ)=610
  - n=16: Sector Shielding — layer-level √5 filtered at sector level
  - Multiplicity structure: Comm(ρ)=610 allocation across n=18/16/15

Paper: Paper III (Transport topology, symmetry breaking)
Invariant level: 2 (generator-conditioned)
"""

import numpy as np
from rime.cubieoperator import CubieSpectralOperator,TOL_KAPPA
from rime.cubie import CubieMove, BLOCK_RANGES
from rime.helpers import is_rational_form, is_in_qsqrt5
from rime.spectral_utils import block_set, count_t7_pairs

TOL = 1e-10
TOL_K = 0.05

op18 = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)


def check(condition, msg):
    assert condition, msg


# ═══════════════════════════════════════════════════════════════════════════════
# Setup: n=14, n=15, n=16
# ═══════════════════════════════════════════════════════════════════════════════

op14 = CubieSpectralOperator(n=14)
op15 = CubieSpectralOperator(n=15)
op16 = CubieSpectralOperator(n=16)

sec18 = op18.center_decomposition()
P18 = sec18['projectors']
n18 = sec18['n_sectors']

sec14 = op14.center_decomposition()
P14 = sec14['projectors']
n14 = sec14['n_sectors']

sec15 = op15.center_decomposition()
P15 = sec15['projectors']
n15 = sec15['n_sectors']

sec16 = op16.center_decomposition()
P16 = sec16['projectors']
n16 = sec16['n_sectors']


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Generator counts
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 1: Generator counts ...")
check(len(op14.rho_moves) == 14,
      f"n=14 should have 14 generators, got {len(op14.rho_moves)}")
check(len(op15.rho_moves) == 15,
      f"n=15 should have 15 generators, got {len(op15.rho_moves)}")
check(len(op16.rho_moves) == 16,
      f"n=16 should have 16 generators, got {len(op16.rho_moves)}")

# n=14: removed axis-1 quarter-turns — verify no (1, *, [1,-1]) keys
for key in op14.rho_moves:
    check(not (key[0] == 1 and key[2] != 2),
          f"n=14 should NOT have axis-1 QT: {key}")

# n=15: removed negative-face half-turns — verify no (*, -1, 2) keys
for key in op15.rho_moves:
    check(not (key[1] == -1 and key[2] == 2),
          f"n=15 should NOT have negative-face HT: {key}")

# n=16: removed axis-0 half-turns — verify no (0, *, 2) keys
for key in op16.rho_moves:
    check(not (key[0] == 0 and key[2] == 2),
          f"n=16 should NOT have axis-0 HT: {key}")

print(f"  OK — n=14: {len(op14.rho_moves)}, n=15: {len(op15.rho_moves)}, n=16: {len(op16.rho_moves)}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Spectral fields
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 2: Spectral field classification ...")
field14 = op14.classify_field()
field15 = op15.classify_field()
field16 = op16.classify_field()
print(f"  n=14: {field14}")
print(f"  n=15: {field15}")
print(f"  n=16: {field16}")
check(field14 == 'sqrt5', f"n=14 field should be sqrt5, got {field14}")
check(field15 == 'higher', f"n=15 field should be higher, got {field15}")
check(field16 == 'sqrt5', f"n=16 field should be sqrt5, got {field16}")
print("  OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Commutant dimensions
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 3: Commutant dimensions ...")
_, cd14 = op14.full_commutant_combinatorial()
_, cd15 = op15.full_commutant_combinatorial()
_, cd16 = op16.full_commutant_combinatorial()
print(f"  n=14: {cd14}")
print(f"  n=15: {cd15}")
print(f"  n=16: {cd16}")
check(cd14 == 675, f"n=14 Comm(ρ) should be 675, got {cd14}")
check(cd15 == 610, f"n=15 Comm(ρ) should be 610 (same as canonical), got {cd15}")
check(cd16 == 610, f"n=16 Comm(ρ) should be 610 (same as canonical), got {cd16}")
print("  OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Sector counts
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 4: Sector counts ...")
print(f"  n=14: {n14} sectors")
print(f"  n=15: {n15} sectors")
print(f"  n=16: {n16} sectors")
check(n14 == 10, f"n=14 should have 10 sectors, got {n14}")
check(n15 == 25, f"n=15 should have 25 sectors, got {n15}")
check(n16 == 13, f"n=16 should have 13 sectors, got {n16}")
print("  OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: T7 pairs
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 5: T7 pairs ...")
K14, k0_14, k1_14 = op14.transport_kappa(P14, compute_kappa1=True)
bs14 = op14.sector_block_support(P14)
t7_14, _ = count_t7_pairs(K14, k0_14, k1_14, bs14, tol_kappa=TOL_KAPPA)

K15, k0_15, k1_15 = op15.transport_kappa(P15, compute_kappa1=True)
bs15 = op15.sector_block_support(P15)
t7_15, _ = count_t7_pairs(K15, k0_15, k1_15, bs15, tol_kappa=TOL_KAPPA)

K16, k0_16, k1_16 = op16.transport_kappa(P16, compute_kappa1=True)
bs16 = op16.sector_block_support(P16)
t7_16, _ = count_t7_pairs(K16, k0_16, k1_16, bs16, tol_kappa=TOL_KAPPA)

print(f"  n=14: {t7_14} T7 pairs")
print(f"  n=15: {t7_15} T7 pairs")
print(f"  n=16: {t7_16} T7 pairs")
check(t7_14 == 5, f"n=14 T7 should be 5 (canonical), got {t7_14}")
check(t7_15 == 24, f"n=15 T7 should be 24 (amplified), got {t7_15}")
check(t7_16 == 11, f"n=16 T7 should be 11, got {t7_16}")
print("  OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: n=14 sqrt5 localization — only S3 and S8 carry √5
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 6: n=14 sqrt5 localization ...")
m14 = op14.n // 2  # = 7
sqrt5_sectors = []
for i, s in enumerate(sec14['sectors']):
    lam = s['lam_18']
    is_s5, _ = is_in_qsqrt5(lam)
    if is_s5 and not is_rational_form(lam, m14):
        sqrt5_sectors.append(i + 1)

print(f"  sqrt5 sectors: {sqrt5_sectors}")
check(len(sqrt5_sectors) == 2,
      f"Expected 2 sqrt5 sectors, got {len(sqrt5_sectors)}")
check(set(sqrt5_sectors) == {3, 8},
      f"sqrt5 sectors should be S3 and S8, got {sqrt5_sectors}")

# Both S3 and S8 must be in EP+EO blocks
for si in sqrt5_sectors:
    blocks = op14.sector_block_support([P14[si - 1]])[0]
    check('ep' in blocks and 'eo' in blocks,
          f"S{si} should be in ep+eo blocks, got {sorted(blocks)}")
print("  OK — sqrt5 confined to S3, S8 in EP+EO")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: n=15 Transport Resolution Amplifier — sector splitting pattern
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 7: n=15 sector splitting pattern ...")

# Build mapping: canonical sector → n=15 children (trace > 0.5)
intact_15 = []
split_15 = {}
for i in range(n18):
    children = []
    for j in range(n15):
        tr = np.trace(P18[i] @ P15[j]).real
        if tr > 0.5:
            children.append((j + 1, int(round(tr))))
    if len(children) == 1:
        intact_15.append(i + 1)
    else:
        split_15[i + 1] = children

print(f"  Intact sectors: {intact_15}")
print(f"  Split sectors: {sorted(split_15.keys())}")

# S1, S2, S4, S5, S8 should be intact
expected_intact = {1, 2, 4, 5, 8}
check(set(intact_15) == expected_intact,
      f"Intact sectors should be {expected_intact}, got {set(intact_15)}")

# S3, S6, S7, S9 should split
expected_split = {3, 6, 7, 9}
check(set(split_15.keys()) == expected_split,
      f"Split sectors should be {expected_split}, got {set(split_15.keys())}")

# S3 and S6 should have identical split pattern (1, 2, 12, 24)
s3_dims = sorted([c[1] for c in split_15[3]])
s6_dims = sorted([c[1] for c in split_15[6]])
check(s3_dims == [1, 2, 12, 24],
      f"S3 split dims should be [1,2,12,24], got {s3_dims}")
check(s6_dims == s3_dims,
      f"S3 and S6 should have identical split patterns: {s3_dims} vs {s6_dims}")

# S9 pattern: (1, 1, 8, 17)
s9_dims = sorted([c[1] for c in split_15[9]])
check(s9_dims == [1, 1, 8, 17],
      f"S9 split dims should be [1,1,8,17], got {s9_dims}")

# S7 pattern: (1, 1, 1, 1, 2, 8, 12, 17, 24) — union of S3/S6/S9 patterns
s7_dims = sorted([c[1] for c in split_15[7]])
check(len(split_15[7]) == 8, f"S7 should split into 8 children, got {len(split_15[7])}")

print(f"  S3 → dims {s3_dims}")
print(f"  S6 → dims {s6_dims}")
print(f"  S7 → {len(split_15[7])} children: dims {s7_dims}")
print(f"  S9 → dims {s9_dims}")
print("  OK — splitting pattern verified")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 8: n=16 Sector Shielding — sector splitting pattern
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 8: n=16 sector splitting pattern ...")

intact_16 = []
split_16 = {}
for i in range(n18):
    children = []
    for j in range(n16):
        tr = np.trace(P18[i] @ P16[j]).real
        if tr > 0.5:
            children.append((j + 1, int(round(tr))))
    if len(children) == 1:
        intact_16.append(i + 1)
    else:
        split_16[i + 1] = children

print(f"  Intact sectors: {intact_16}")
print(f"  Split sectors: {sorted(split_16.keys())}")

# Same 4 canonical sectors split (S3, S6, S7, S9), but each only 2-fold
check(set(split_16.keys()) == {3, 6, 7, 9},
      f"Split sectors should be {{3,6,7,9}}, got {set(split_16.keys())}")
check(set(intact_16) == {1, 2, 4, 5, 8},
      f"Intact sectors should be {{1,2,4,5,8}}, got {set(intact_16)}")

# Each split is 2-fold (not 4-fold like n=15, not 8-fold like n=15 S7)
for si in split_16:
    check(len(split_16[si]) == 2,
          f"S{si} should split 2-fold, got {len(split_16[si])}-fold: {split_16[si]}")

# S3: 26 + 13 = 39 (preserves total dim)
check(sorted([c[1] for c in split_16[3]]) == [13, 26],
      f"S3 split dims should be [13,26], got {sorted([c[1] for c in split_16[3]])}")
# S7: 44 + 22 = 66
check(sorted([c[1] for c in split_16[7]]) == [22, 44],
      f"S7 split dims should be [22,44], got {sorted([c[1] for c in split_16[7]])}")

for si, children in split_16.items():
    print(f"  S{si} → {children}")
print("  OK — n=16 binary splitting verified (mild, 2-fold each)")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 9: n=16 Sector Shielding — layer-level √5 filtered at sector level
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 9: n=16 Sector Shielding ...")

# Layer level: verify two √5 layers exist
m16 = op16.n // 2  # = 8
sqrt5_layers = []
for lam in op16._layers:
    is_s5, s5_str = is_in_qsqrt5(lam)
    if is_s5:
        sqrt5_layers.append((lam, s5_str))
print(f"  √5 layers: {sqrt5_layers}")
check(len(sqrt5_layers) == 2,
      f"n=16 should have 2 sqrt5 layers, got {len(sqrt5_layers)}")

# Sector level: count how many sectors have non-k/9 rational lam_18
non_k9_sectors = []
for i, s in enumerate(sec16['sectors']):
    lam = s['lam_18']
    if not is_rational_form(lam, 9):
        non_k9_sectors.append(i + 1)
        blocks = op16.sector_block_support([P16[i]])[0]
        print(f"  S{i+1}: lam_18={lam:.8f} (non-k/9), blocks={sorted(blocks)}")

# Most sectors should be k/9 rational — the √5 is SHIELDED
n_k9_rational = n16 - len(non_k9_sectors)
print(f"  k/9 rational sectors: {n_k9_rational}/{n16}")
check(n_k9_rational >= 11,
      f"At least 11/13 sectors should have k/9 rational lam_18, got {n_k9_rational}")

# S3 and S10 are the only non-k/9 sectors (both in EP+EO)
check(set(non_k9_sectors) == {3, 10},
      f"Non-k/9 sectors should be {{3,10}}, got {set(non_k9_sectors)}")

# S3 and S10 must be in EP+EO blocks
for si in non_k9_sectors:
    blocks = op16.sector_block_support([P16[si - 1]])[0]
    check('ep' in blocks and 'eo' in blocks,
          f"S{si} should be in ep+eo blocks, got {sorted(blocks)}")

print("  OK — Sector Shielding: √5 at layer level, only 2/13 sectors non-rational")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 10: n=14/15/16 sector projectors are idempotent and orthogonal
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 10: Sector projector algebra (idempotence, orthogonality) ...")
for name, Ps, n_sec in [("n=14", P14, n14), ("n=15", P15, n15), ("n=16", P16, n16)]:
    # Idempotence
    for i in range(n_sec):
        err = np.linalg.norm(Ps[i] @ Ps[i] - Ps[i], 'fro')
        check(err < TOL, f"{name} P[{i}] not idempotent: ||P²-P||={err:.2e}")

    # Orthogonality
    for i in range(n_sec):
        for j in range(i + 1, n_sec):
            err = np.linalg.norm(Ps[i] @ Ps[j], 'fro')
            check(err < TOL, f"{name} P[{i}]·P[{j}] not orthogonal: ||PᵢPⱼ||={err:.2e}")

    # Completeness
    P_sum = sum(Ps)
    err = np.linalg.norm(P_sum - np.eye(P_sum.shape[0]), 'fro')
    check(err < TOL, f"{name} ΣPᵢ ≠ I: ||ΣPᵢ-I||={err:.2e}")

print("  OK — all projectors idempotent, orthogonal, complete")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 11: n=14/15/16 transport K is symmetric
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 11: K symmetry ...")
for name, K in [("n=14", K14), ("n=15", K15), ("n=16", K16)]:
    err = np.linalg.norm(K - K.T, 'fro')
    check(err < TOL, f"{name} K not symmetric: ||K-Kᵀ||={err:.2e}")
print("  OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 12: Multiplicity Structure — Comm(ρ)=610 allocation under same commutant
# ═══════════════════════════════════════════════════════════════════════════════

print("Test 12: Multiplicity structure — Comm(ρ)=610 allocation ...")

# Compute per-sector commutant block rank for n=18, n=15, n=16 (all Comm=610)
def sector_commutant_ranks(op, Ps, n_sec):
    """Return list of dim(P_i Comm(ρ) P_i) for each sector."""
    comm_basis, _ = op.full_commutant_combinatorial()
    ranks = []
    for i in range(n_sec):
        projected = []
        for X in comm_basis:
            block = Ps[i] @ X @ Ps[i]
            projected.append(block.ravel())
        projected = np.array(projected)
        _, s, _ = np.linalg.svd(projected, full_matrices=False)
        rank = int(np.sum(s > 5e-8))
        ranks.append(rank)
    return ranks

ranks18 = sector_commutant_ranks(op18, P18, n18)
ranks16 = sector_commutant_ranks(op16, P16, n16)
ranks15 = sector_commutant_ranks(op15, P15, n15)
ranks14 = sector_commutant_ranks(op14, P14, n14)

print(f"  n=18 (Comm=610, {n18} sectors): {sorted(ranks18, reverse=True)}")
print(f"  n=16 (Comm=610, {n16} sectors): {sorted(ranks16, reverse=True)}")
print(f"  n=15 (Comm=610, {n15} sectors): {sorted(ranks15, reverse=True)}")
print(f"  n=14 (Comm=675, {n14} sectors): {sorted(ranks14, reverse=True)}")

# n=18 allocation: dominant 400 block (S1), 210 (S7), 145×3, 65, 64, 1×2
check(400 in ranks18, f"n=18 should have a 400-block, got {sorted(ranks18, reverse=True)}")
check(210 in ranks18, f"n=18 should have a 210-block (S7 hybrid)")
check(ranks18.count(145) == 3, f"n=18 should have 3×145 blocks, got {ranks18.count(145)}×145")

# n=16 allocation: 400 persists, 210→210×2, 145→145×5
check(400 in ranks16, f"n=16 should have a 400-block (S1 intact)")
check(ranks16.count(210) == 2, f"n=16 should have 2×210 blocks, got {ranks16.count(210)}×210")
check(ranks16.count(145) == 5, f"n=16 should have 5×145 blocks, got {ranks16.count(145)}×145")

# n=15 allocation: 400 persists, 144×7 (fragmented from 145×3), many 1s
check(400 in ranks15, f"n=15 should have a 400-block (S1 intact)")
check(ranks15.count(1) >= 8, f"n=15 should have ≥8 singleton blocks, got {ranks15.count(1)}")

# n=14 has DIFFERENT Comm(675): 441 replaces 400 (enlarged commutant)
check(441 in ranks14, f"n=14 should have a 441-block (enlarged Comm), got {sorted(ranks14, reverse=True)}")
check(sorted(ranks18, reverse=True) != sorted(ranks14, reverse=True),
      "n=14 allocation should differ from n=18 (Comm changed)")

# Cross-check: n=18, n=16, n=15 all share the 400 invariant block
# but n=14's dominant block is 441 (Comm grew by 65)
for name, ranks in [("n=18", ranks18), ("n=16", ranks16), ("n=15", ranks15)]:
    check(400 in ranks, f"{name} should have invariant 400-block")

print("  OK — multiplicity structure verified under same Comm(ρ)=610")


print(f"\n{'=' * 60}")
print("  ALL GENERATOR FAMILY TESTS PASSED")
print(f"{'=' * 60}")
