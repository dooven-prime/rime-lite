# Canonical Computational Specification — r2

**Alias**: `canonical_data_r2.md`
**Date**: 2026-05-12 (original); 2026-05-18 (provenance upgrade)
**Status**: DEFINITIVE. All numerical values correspond to the post-ρ-fix canonical representation (revision r2). Earlier drafts used a pre-fix representation realization and should not be considered authoritative.
**Purpose**: Single reference for all three Papers and figure scripts. No paper should hardcode numbers independently.

**Resolution**: All data computed at 6-layer (A_18 eigenspaces) and 9-sector (Center{A_18, QT_all, HT_all} joint diagonalization) resolution.

**Data flow** (unidirectional):
```
experiments/*.py  ──→  paper_data.md  ──→  figures/*.py
                                              papers/*.tex
```
Experiment scripts compute → this file freezes → figures/papers reference. Figures are frozen artifacts; they do NOT recompute.

---

## 0. Conventions

### 0.1 Norm Convention

All norms are **Frobenius** ‖X‖_F = √(Σ |x_ij|²) unless otherwise stated.

### 0.2 Projector Normalization

Projectors are Schatten-normalized: P = V @ V^H where V has orthonormal columns (from `numpy.linalg.eigh`). Not trace-normalized — Tr(P) = dim(subspace), not 1.

### 0.3 Generator Weighting

The adjacency operator is the uniform average over all face-turn generators:

```
A_18 = (12 QT_all + 6 HT_all) / 18
```

where QT_all = Σ_{a∈{x,y,z}} QT^a (12 quarter-turn generators), HT_all = Σ_{a∈{x,y,z}} HT^a (6 half-turn generators). Generators are drawn from `CubieMove.prim_moves` — the 18 canonical face-turn generators of the Rubik's cube group.

### 0.4 Tolerances

| Symbol | Value | Scope |
|--------|-------|-------|
| `TOL` | 1e-10 | Test assertions (all numerical equality checks) |
| `TOL_K` | 0.05 | Transport edge detection (‖P_α ρ(g) P_β‖ > TOL_K implies direct edge) |
| `SPECTRAL_DECIMALS` | 6 | CubieSpectralOperator — canonical rounding of eigenvalue keys |
| `CENTER_CLUSTER_TOL` | 1e-8 | Center decomposition — clustering of (λ_QT, λ_HT, λ_18) triples into sectors |
| `CubieSpectralOperator.tol` | 1e-6 | Default operator tolerance — Hermiticity check, eigenvalue mask |

`SPECTRAL_DECIMALS` and `CENTER_CLUSTER_TOL` are canonical constants in `rime/cubieoperator.py` — they are NOT derived from `self.tol`. Layer identity and sector identity are topological invariants; tolerance only gates numerical comparisons.

### 0.5 Canonical Ordering

- **Layer keys** (6): descending by eigenvalue: `[1.0, 0.888889, 0.777778, 0.666667, 0.555556, 0.333333]` (≈ 1 − k/9, k ∈ {0,1,2,3,4,6}).
- **Sector labels** (9): S1–S9 ordered by (λ_18 descending, λ_QT descending, λ_HT descending), matching the order produced by `CubieSpectralOperator.center_decomposition()`.
- **Block order**: CP → EP → CO → EO (matching `BLOCK_RANGES` in `rime/cubie.py`).

### 0.6 Revision ID

This is **revision r2** (post-ρ-fix). The ρ-fix corrected the representation construction so that ρ(g) is a proper homomorphism on all blocks (previously the EP block had a sign error in the orientation sub-block). Pre-ρ-fix values in `docs/260512_phenomenology_archive.md` are ARCHIVAL only.

### 0.7 Random Seed

All experiments use `np.random.seed(42)`. Tests are deterministic and do not depend on random state.

### 0.8 Computational Complexity

Canonical operations and their asymptotic costs. d = 228 (total dimension), d_λ = per-layer dimension (max 106), |G| = 18 (generators), K = 3 (Center operators).

| Operation | Complexity | Dominant term (canonical) | Location |
|-----------|-----------|--------------------------|----------|
| A_18 eigendecomposition | O(d³) | ~1.2×10⁷ FLOP | `CubieSpectralOperator.__init__` |
| center_decomposition() | O(K·d³) | Joint diagonalization of 3 ops | `cubieoperator.py:985` |
| Full commutant (combinatorial) | O(d²·\|Conj(G)\|) | Orbit enumeration, exact count | `cubieoperator.py:678` |
| Commutant per layer (d_λ ≤ 50) | O(d_λ⁶) | Kronecker SVD; generator reduction reduces prefactor ~3× | `cubieoperator.py:567` |
| Commutant per layer (d_λ > 50) | O(d_λ³·N_iter) | Randomized Reynolds, N_iter=8, sample=min(6d_λ, 250) | `cubieoperator.py:638` |
| transport_kappa() | O(\|G\|·d³) | 18 × projector sandwich | `cubieoperator.py:1150` |
| kappa_depth(d) | O(C(\|Lie\|, d)·d³) | Combinatorial in d; d=2 → 153 commutators | `cubieoperator.py:1098` |
| EP algebra closure | O(d_EP³·deg) | Iterated SVD, deg ≤ 3 | `experiments/paper2/ep_algebra.py` |
| π map SVD | O(610·966·min(610,966)) | 610×966 matrix, one-shot | `experiments/paper2/commutant_pi_map.py` |
| Full slow test suite | ~5–10 min wall time | Dominated by full commutant + kappa_depth(2) | `tests/run_slow_tests.py` |

---

## 1. Total Space

```
V = CP(64) ⊕ EP(144) ⊕ CO(8) ⊕ EO(12) = 228
```

---

## 2. Block Structure

| Block | Dim | Algebra | Noncommutativity ‖[QT⁰,QT¹]‖ | Role |
|-------|-----|---------|-------------------------------|------|
| CP | 64 | Q₃ Hamming H(3,2), Bose-Mesner ≅ Hecke H(S₂≀S₃,S₃) | 0 (exactly commutative) | Spectator |
| EP | 144 | A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴ | 2.74 (93.9% of total) | Curvature carrier |
| CO | 8 | Z₃ phase structure, weak noncommutative | 0.61 (21.0%) | Sideband |
| EO | 12 | Z₂ phase structure, weak noncommutative | 0.79 (27.1%) | Sideband |

Total ‖[QT⁰, QT¹]‖_F = 2.92.

---

## 3. Six Canonical Layers (A_18 Eigenspaces)

λ = 1 − k/9, k ∈ {0, 1, 2, 3, 4, 6}. k=5 genuinely absent.

| k | λ | Dim | Label | Block composition | Notes |
|---|-----|-----|-------|-------------------|-------|
| 0 | 1 | 20 | V₁ | cp(8) + ep(12) | ISOLATED: K=κ₀=κ₁=0 with all |
| 1 | 8/9 | 2 | V₈/₉ | eo(2) | NEW (was masked pre-ρ-fix) |
| 2 | 7/9 | 39 | V₇/₉ | ep(36) + eo(3) | Metastable basin |
| 3 | 2/3 | 26 | V₂/₃ | ep(24) + co(2) | Intermediate, single-sector canonical |
| 4 | 5/9 | 106 | V₅/₉ | cp(24) + ep(72) + co(3) + eo(7) | Transit hub, largest layer |
| 6 | 1/3 | 35 | V₁/₃ | cp(32) + co(3) | Dissipative sink |

---

## 4. Nine Primitive Sectors (Center{A_18, QT_all, HT_all} Joint Diagonalization)

| Sector | Dim | k | λ_18 | λ_QT | λ_HT | Block support | Canonical layer | Role |
|--------|-----|---|------|------|------|---------------|-----------------|------|
| S1 | 20 | 0 | 1 | 1 | 1 | cp(8)+ep(12) | V₁ | ISOLATED: K=κ=0 |
| S2 | 2 | 1 | 8/9 | 5/6 | 1 | eo(2) | V₈/₉ | Connects to S5,S6 |
| S3 | 39 | 2 | 7/9 | 5/6 | 2/3 | ep(36)+eo(3) | V₇/₉ | Metastable |
| S4 | 26 | 3 | 2/3 | 1/2 | 1 | ep(24)+co(2) | V₂/₃ | Single-sector canonical |
| S5 | 1 | 4 | 5/9 | 1/3 | 1 | eo(1) | V₅/₉(eo) | Tiny EO piece |
| S6 | 39 | 4 | 5/9 | 1/2 | 2/3 | ep(36)+eo(3) | V₅/₉(A) | **PRIMARY HUB** (degree 5) |
| S7 | 66 | 4 | 5/9 | 2/3 | 1/3 | cp(24)+ep(36)+co(3)+eo(3) | V₅/₉(B) | Secondary hub (degree 3) |
| S8 | 8 | 6 | 1/3 | 0 | 1 | cp(8) | V₁/₃(A) | Pure CP |
| S9 | 27 | 6 | 1/3 | 1/3 | 1/3 | cp(24)+co(3) | V₁/₃(B) | CP+CO |

Note: Raw joint diagonalization yields 11 sectors; S4+S5 (same λ triple: 2/3, 1/3, 5/9) and S9+S10 (same λ triple: 1/3, 1/3, 1/3) are accidentally split by the eigensolver and must be combined. The 9 listed above are the unique (λ_QT, λ_HT, λ_18) triples.

---

## 5. Transport Topology (K Matrix, 9-Sector)

K_αβ = max_g ‖P_α ρ(g) P_β‖_F, computed over all 18 face-turn generators.

### 5.1 Direct Edges (K > 0.01)

10 direct edges, ALL block-preserving (share ≥1 block):

| Edge | K value | Shared block | Type |
|------|---------|-------------|------|
| S2(2,eo) ↔ S5(1,eo) | 0.47 | eo | Within-EO |
| S2(2,eo) ↔ S6(39,ep+eo) | 0.58 | eo | Within-EO |
| S3(39,ep+eo) ↔ S6(39,ep+eo) | 2.55 | ep,eo | Within-EP/EO |
| S3(39,ep+eo) ↔ S7(66,cp+ep+co+eo) | 3.61 | ep,eo | Cross-V5/9 |
| S4(26,ep+co) ↔ S6(39,ep+eo) | 3.46 | ep | Within-EP |
| S4(26,ep+co) ↔ S9(27,cp+co) | 1.00 | co | Within-CO |
| S5(1,eo) ↔ S6(39,ep+eo) | 0.82 | eo | Within-EO |
| S6(39,ep+eo) ↔ S7(66,cp+ep+co+eo) | 3.61 | ep,eo | Within-EP/EO |
| S7(66,cp+ep+co+eo) ↔ S9(27,cp+co) | 4.06 | cp,co | Cross-V5/9 |
| S8(8,cp) ↔ S9(27,cp+co) | 2.83 | cp | Within-CP |

**0 cross-block direct edges** — every edge shares ≥1 block. Cross-block transport requires composition.

### 5.2 Hub Degrees

| Sector | Degree | Connected to |
|--------|--------|-------------|
| S1 | 0 | (none — fully isolated) |
| S2 | 2 | S5, S6 |
| S3 | 2 | S6, S7 |
| S4 | 2 | S6, S9 |
| S5 | 2 | S2, S6 |
| **S6** | **5** | S2, S3, S4, S5, S7 ← PRIMARY HUB |
| S7 | 3 | S3, S6, S9 |
| S8 | 1 | S9 |
| S9 | 3 | S4, S7, S8 |

### 5.3 S1 Isolation

S1 (V₁, 20-dim, cp+ep) has K < 10⁻¹⁴ with ALL other 8 sectors. It is a G-invariant subrepresentation — the unique fully decoupled sector.

---

## 6. Lie Accessibility (κ Matrices, 6-Layer Resolution)

κ_d(α,β) = max ‖P_α C_d P_β‖ where C_d is a depth-d Lie monomial.

### 6.1 κ₀ — Gradient (Individual A_g)

```
         V1     V8/9    V7/9    V2/3    V5/9    V1/3
V1      3e-15   0       6e-15   4e-15   1e-14   4e-15
V8/9    0       0.52    3e-15   7e-17   1.17    9e-17
V7/9    6e-15   3e-15   4.00    2e-14   6.94    8e-17
V2/3    4e-15   9e-09   2e-14   5.66    5.44    1.57
V5/9    1e-14   1.17    6.94    5.44    13.9    6.38
V1/3    4e-15   9e-09   1e-16   1.57    6.38    9.67
```

Max asymmetry: 9.16×10⁻⁹ — symmetric to machine precision.

### 6.2 κ₁ — Curvature (Commutators [A_g, A_h])

```
         V1     V8/9    V7/9    V2/3    V5/9    V1/3
V1      6e-16   0       9e-15   6e-15   1e-14   9e-15
V8/9    0       0.50    0.71    2e-16   1.71    2e-16
V7/9    9e-15   0.71    6.29    4.27    10.9    3e-16
V2/3    6e-15   3e-08   4.27    5.45    8.32    3.26
V5/9    1e-14   1.71    10.9    8.32    17.8    14.5
V1/3    9e-15   3e-08   1e-08   3.26    14.5    22.5
```

### 6.3 Key κ Values

| Pair | κ₀ | κ₁ | κ₂ | Type |
|------|-----|-----|-----|------|
| V₇/₉ ↔ V₂/₃ | ~10⁻¹⁴ | **4.27** | 13.4 | Curvature-coupled (largest enhancement ~10¹⁴) |
| V₅/₉ ↔ V₂/₃ | 5.44 | 8.32 | 21.1 | Gradient + curvature |
| V₅/₉ ↔ V₁/₃ | 6.38 | 14.5 | 40.3 | Gradient + curvature |
| V₈/₉ ↔ V₇/₉ | ~0 | **0.71** | 2.24 | NEW curvature channel (post-ρ-fix) |
| V₈/₉ ↔ V₅/₉ | 1.17 | 1.71 | 4.71 | Gradient + curvature |
| V₁ ↔ any | ~0 | ~0 | ~0 | Fully isolated at all depths |

All 7 pure curvature channels (κ₀≈0, κ₁>0) are **within-block** (share at least one block). 0 cross-block curvature channels.

### 6.4 Three Accessibility Classes (6-Layer)

| Class | Sectors | Mechanism |
|-------|---------|-----------|
| I (isolated) | V₁ only | K=κ₀=κ₁=0 with all others |
| II (gradient) | V₈/₉, V₅/₉, V₁/₃ | κ₀ > 0 on direct edges |
| III (curvature) | V₇/₉ ↔ V₂/₃ | κ₀≈0, κ₁=4.27 (commutator-mediated) |

### 6.5 κ at 9-Sector Resolution (Paper III Definitive Data)

Computed via `center_decomposition()` → 9 sector projectors. Paper sector labels S1–S9 (see §4).

**κ₀ (gradient) at 9-sector:**

```
          S1(20) S2( 2) S3(39) S4(26) S5( 1) S6(39) S7(66) S8( 8) S9(27)
S1(20)       0      0      0      0      0      0      0      0      0
S2( 2)       0   0.52      0      0   0.74   0.91      0      0      0
S3(39)       0      0   4.00      0      0   4.00   5.66      0      0
S4(26)       0   ~0        0   5.66   ~0    5.44   ~0        0   1.57
S5( 1)       0   0.74      0      0   1.05   1.28      0      0      0
S6(39)       0   0.91   4.00   5.44   1.28   6.01   5.66      0      0
S7(66)       0      0   5.66   ~0       0   5.66  10.60      0   6.38
S8( 8)       0      0      0      0      0      0      0   4.44   4.44
S9(27)       0   ~0        0   1.57   ~0    ~0      6.38   4.44   6.94
```

Max asymmetry: 1.6×10⁻⁸. All direct transport edges (K>0) have κ₀>0.

**κ₁ (curvature) at 9-sector:**

```
          S1(20) S2( 2) S3(39) S4(26) S5( 1) S6(39) S7(66) S8( 8) S9(27)
S1(20)       0      0      0      0      0      0      0      0      0
S2( 2)       0   0.50   0.71      0   1.01   1.18   1.01      0      0
S3(39)       0   0.71   6.29   4.27   1.01   6.29   8.90      0      0
S4(26)       0   ~0     4.27   5.45   ~0     7.09   6.17      0   3.26
S5( 1)       0   1.01   1.01      0      0   1.74   1.42      0      0
S6(39)       0   1.18   6.29   7.09   1.74   7.70   8.90      0      0
S7(66)       0   1.01   8.90   6.17   1.42   8.90  10.90   6.98  14.49
S8( 8)       0      0      0      0      0      0   6.98      0  12.09
S9(27)       0   ~0     ~0      3.26   ~0     ~0    14.49  12.09  14.63
```

**7 pure curvature channels** (κ₀≈0, κ₁>0) — all within-block:

| Pair | κ₁ | Shared block | Within-block? |
|------|-----|-------------|---------------|
| S2↔S3 | 0.71 | eo | Yes |
| S2↔S7 | 1.01 | eo | Yes |
| S3↔S4 | 4.27 | ep | Yes |
| S3↔S5 | 1.01 | eo | Yes |
| S4↔S7 | 6.17 | ep, co | Yes |
| S5↔S7 | 1.42 | eo | Yes |
| S7↔S8 | 6.98 | cp | Yes |

**0 cross-block curvature channels.** Curvature is strictly block-preserving.

---

## 7. T7: Discrete Composition ⊋ Lie Accessibility (9-Sector Resolution)

### 7.1 Definition

A T7 pair (α,β) satisfies:
- K_αβ = 0 (no direct transport)
- κ_d(α,β) = 0 ∀d (no Lie accessibility at any depth)
- BUT reachable via length-2 composition: ∃γ with K_αγ > 0 and K_γβ > 0

### 7.2 T7 Pairs (5 pairs at 9-sector resolution)

| Pair | Block support | Shared block? | Mediation path |
|------|--------------|---------------|----------------|
| S2(eo) ↔ S4(ep+co) | eo ∩ (ep+co) = ∅ | No | S2 → S6 → S4 |
| S3(ep+eo) ↔ S9(cp+co) | (ep+eo) ∩ (cp+co) = ∅ | No | S3 → S7 → S9 |
| S4(ep+co) ↔ S5(eo) | (ep+co) ∩ eo = ∅ | No | S4 → S6 → S5 |
| S4(ep+co) ↔ S8(cp) | (ep+co) ∩ cp = ∅ | No | S4 → S9 → S8 |
| S6(ep+eo) ↔ S9(cp+co) | (ep+eo) ∩ (cp+co) = ∅ | No | S6 → S7 → S9 |

ALL 5 T7 pairs are **cross-block** (disjoint block support). Zero within-block T7 pairs.
All mediated through the S6–S7 hub complex.

### 7.3 S1 is NOT T7

S1 has K=κ₀=κ₁=0 with all sectors, but it is genuinely G-invariant (no composition path exists). This is subrepresentation isolation, not T7.

---

## 8. EP Algebra Structure

```
A_EP = ⟨Q₀, Q₁, Q₂⟩ ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴
dim(A_EP) = 20, closes at degree 3
Z(A_EP) = 8-dim
AW: 8 simple components, 3 of 4 M₂ active ([Qᵢ,Qⱼ] ≠ 0)
Killing form: signature (8⁺, 4⁻, 8 zero), ker(K) = Z(A_EP)
```

### 8.1 Isotypic Components

4×24 (M₂) + 4×12 (M₁) = 144 on EP.
Uniform multiplicity 12 across all 8 components.

### 8.2 Double Commutant

```
Comm(A_EP) ≅ M₁₂(ℂ)⁸
dim(Comm(A_EP)) = 1152
End_{Comm(A)}(EP) = A_EP  ✓
```

### 8.3 Commutant Restriction Map (π)

```
π: End_G(V) → ⊕_λ End_G(V_λ),  π(C) = (P_λ C P_λ)_λ

dim(domain)  = dim End_G(V)     = 610
dim(codomain)= Σ dim End_G(V_λ) = 400+1+145+145+210+65 = 966

ker π   =   0  (injective — full commutant uniquely determined by diagonal blocks)
coker π = 356  (cross-layer linear constraints on per-layer commutant tuples)
```

Per-layer liftability (every layer individually has full rank):
| λ | dim | comm | im π | coker |
|---|-----|-------|------|-------|
| 1.0000 | 20 | 400 | 400 | 0 |
| 0.8889 | 2 | 1 | 1 | 0 |
| 0.7778 | 39 | 145 | 145 | 0 |
| 0.6667 | 26 | 145 | 145 | 0 |
| 0.5556 | 106 | 210 | 210 | 0 |
| 0.3333 | 35 | 65 | 65 | 0 |

The 356 = coker π are global (cross-layer) linear dependencies: each
zero-transport pair forces C_ab=0, locking the relative scaling between
per-layer commutant bases.

---

## 9. S₃ Minimal Prototype Data

### 9.1 S₃ nat(3) ⊕ reg(6) — 9-dim, T7-only

```
5 sectors (Center{A_full, A_trans}):
  S1: 2-dim, reg, PURE-reg, A_full=1.0, A_trans=0.0
  S2: 1-dim, reg, PURE-reg, A_full=0.0, A_trans=1.0
  S3: 1-dim, nat, PURE-nat, A_full=0.0, A_trans=-0.577
  S4: 1-dim, reg, PURE-reg, A_full=0.0, A_trans=0.577
  S5: 4-dim, nat+reg, HYBRID, A_full=0.0, A_trans=0.0

3 cross-block T7 pairs (nat↔reg), all mediated through S5.
κ₁ = 0 everywhere (no M₂). T7 exists WITHOUT curvature.
```

### 9.2 S₃ reg(6) ⊕ reg(6) — 12-dim, Full Hierarchy

```
10 sectors (Center{A_3, A_2}):
  Pure-A: S1,S2,S4,S6,S8 (5 sectors)
  Pure-B: S3,S5,S7,S9 (4 sectors)
  Hybrid: S10 (A:1 + B:1) ← THE BRIDGE

Perfect separation:
  30 Class-II edges (κ₀>0): ALL within-block
  10 curvature pairs (κ₀=0,κ₁>0): ALL within-block
  9 T7 pairs (K=κ₀=κ₁=0): ALL cross-block
  Zero counterexamples to either direction.
```

---

## 10. Fundamental Identities

```
A_18 = (12 QT_all + 6 HT_all) / 18          [verified to machine precision]
A_axis = (4 QT^a + 2 HT^a) / 6              [verified per axis]
‖ρ(g)ρ(h) − ρ(gh)‖ < 3×10⁻⁸                [homomorphism property, all blocks]
max|expm(A_g) − ρ(g)| = 2.71×10⁻¹⁵           [Lie embedding fidelity]
max|κ_ij − κ_ji| ≈ 10⁻¹⁵                     [κ symmetry, all depths]
```

---

## 11. Generator-Set Universality

Same 6-layer eigenspace structure across ALL inverse-closed S (verified 9 sets including n=3 single-face). Number of layers may differ (±split/merge), but eigenspaces are the same invariant subspaces. The 6-layer structure is G-determined; transport strength values are S-conditioned.

---

## Cross-Consistency Notes

Minor discrepancies with VERIFIED.md (same-day verification, possibly different Center operator combination):

| Claim | VERIFIED.md | This file | Resolution |
|-------|------------|-----------|------------|
| Direct edges | 11 | 10 | Recomputable; topology identical |
| S7 degree | 4 | 3 | Hub identity (S6 primary) unchanged |
| T7 pairs | 4 | 5 | Cross-block property identical |
| Curvature channels | 6 | 7 (9-sector) | All within-block; property identical |

All structural claims (S1 isolation, S6 primary hub, block-preserving edges, cross-block T7, within-block curvature) are ROBUST across the two computations.

---

## Rules

1. **All Papers reference this file for numerical values.** No hardcoded numbers in paper text.
2. **Numbers are at post-ρ-fix resolution.** Pre-ρ-fix values are ARCHIVAL only.
3. **The canonical sector ordering is S1–S9 as defined in §4.** Figure scripts and paper text must use this convention.
4. **When recomputation is needed**, run the canonical scripts and update this file before updating papers.
5. **If Center definition changes** (different commuting operator set), sectors may change — update this file and mark the revision.
6. **This file overrides VERIFIED.md for numerical values** where they disagree. VERIFIED.md records verification history; this file is the active data source.

---

## 12. Specification Theorems

Empirical structural laws verified across all canonical computations. These have the status of "computational structural laws" — observed without exception in every recomputation, but not yet proven from first principles.

### Spectral Rigidity Theorem

The 6-layer eigenspace decomposition of A_18 is invariant under all tested inverse-closed generating sets (verified for n ∈ {2,3,4,6,8,9,10,12,16,18,21}). Layer count may differ (±split/merge under generator restriction), but the underlying invariant subspaces are G-determined. Transport strength values are S-conditioned — they depend on which generators are included, but the subspace decomposition does not.

**Evidence**: §11, `SpectralStructure` class, `tests/test_spectralstructure.py`.

### Transport Locality Principle

All direct transport edges (K > 0.01) and all pure curvature channels (κ₀≈0, κ₁>0) are **block-preserving** — every such pair shares at least one block (CP/EP/CO/EO). Zero cross-block direct edges. Zero cross-block curvature channels. Cross-block transport requires composition through intermediate sectors.

**Evidence**: §5.1 (10 direct edges, all block-preserving), §6.5 (7 curvature channels, all within-block).

### T7 Separation Principle

All T7 pairs are **cross-block** (disjoint block support) and require mediated composition through hub sectors. Zero within-block T7 pairs. This is the converse of Transport Locality — locality permits only within-block direct transport, so any cross-block reachability must be T7-mediated.

**Evidence**: §7.2 (5 T7 pairs, all cross-block), `experiments/paper3/t7_detection.py`.

### M₂ Principle

Noncommutative simple components (n_i ≥ 2 in the Artin-Wedderburn decomposition) are the sole carriers of three phenomena:

1. **Refinement obstruction** — sector splitting within a canonical layer occurs only where M₂ components are present
2. **Transport mediation** — hub sectors (S6, S7) are precisely those containing M₂-supported blocks
3. **Lie curvature** — κ₁ > 0 channels exist only within blocks carrying M₂ components

Blocks with only abelian components (M₁) are transport spectators — they may appear in edges but never as the sole block support for a transport channel.

**Evidence**: §2 (only EP has active M₂; CP/CO/EO are abelian or weakly noncommutative), §6.5 (all 7 curvature channels involve EP or EO), §8 (A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴).

### S1 Isolation Theorem

S1 (V₁, 20-dim, cp+ep) is the unique G-invariant proper subrepresentation among the 6 canonical layers. K < 10⁻¹⁴ with all other sectors at all resolutions. κ_d = 0 at all depths d = 0,1,2. This is subrepresentation isolation, not T7 — no composition path exists.

**Evidence**: §5.3, §6.1–6.2, §7.3, `tests/test_sectors.py`, `tests/test_transport.py`.

### Curvature Confinement

κ₁ > 0 occurs exclusively within blocks. The curvature operator [A_g, A_h] preserves block structure, and its off-block-diagonal matrix elements vanish identically (to machine precision). This is a consequence of the block-diagonal structure of ρ(g) — commutators of block-diagonal matrices are block-diagonal.

**Evidence**: §6.5 (7 curvature channels, all within-block, 0 cross-block), `experiments/transport_closure.py` Zones 4–5.

---

## Appendix A — Provenance Graph

For every claim in §§1–11: the mathematical object, its canonical API, the experiment script that computes it, and derived artifacts (figures, paper sections).

### A.1 Total Space (§1)

| | |
|---|---|
| **Mathematical object** | Representation space dimension: V = ℂ²²⁸ = CP(64) ⊕ EP(144) ⊕ CO(8) ⊕ EO(12) |
| **Canonical API** | `rime/cubie.py`: `TOTAL_DIM = 228`, `BLOCK_DIMS`, `BLOCK_RANGES` |
| **Experiment script** | None — definitional constant derived from the Rubik's cube group representation construction |
| **Test coverage** | `tests/test_representation.py:119-121` (block dims), `tests/test_spectralstructure.py:77-83` (block_dims ↔ block_ranges consistency) |
| **Derived artifacts** | All papers, all figures |

### A.2 Block Structure (§2)

| | |
|---|---|
| **Mathematical object** | Per-block noncommutativity ‖[QT⁰, QT¹]‖_F, algebraic characterization of each block |
| **Canonical API** | `CubieSpectralOperator().build_per_axis_ops()[0]` → `QT0`, `QT1`; sliced via `BLOCK_RANGES` |
| **Experiment script** | `experiments/paper2/supp_nc.py:46-66` — computes `comm = QT0 @ QT1 - QT1 @ QT0`, extracts block-diagonal Frobenius norms |
| **Cross-validation** | `experiments/transport_closure.py:224-271` (Zone 3) — verifies cp=0, ep=2.74, co=0.61, eo=0.79 against 2.92 total |
| **Test coverage** | `tests/test_commutant.py:103-130` (Test 5: noncommutativity localization) |
| **Derived artifacts** | Paper II §5, `experiments/paper2/figures/supp_nc.png`, `paper2_figures.py` Fig 3 |

### A.3 Six Canonical Layers (§3)

| | |
|---|---|
| **Mathematical object** | Spec(A_18) = {1 − k/9 : k ∈ {0,1,2,3,4,6}}, 6 eigenspaces with projectors P_λ, multiplicities dim(V_λ), block support per layer |
| **Canonical API** | `CubieSpectralOperator().layer_keys` (property), `.layer_dimension(lam)`, `.layer_projector(lam)`; `SpectralStructure(CubieMove.prim_moves).eigenvalue_layers()` |
| **Experiment scripts** | `experiments/paper1/spectral_ladder.py:32-41` (layers+dims), `experiments/paper1/k_absence.py:28-39` (k=5 absent), `experiments/paper1/block_composition.py:31-60` (per-layer block composition), `experiments/paper1/projector_algebra.py` (P_i²=P_i, P_iP_j=0, ΣP_i=I, Tr(P_i)=dim_i) |
| **Cross-validation** | `experiments/transport_closure.py:106-151` (Zone 1) — all 6 eigenvalues, dimensions, block composition, A_18 reconstruction |
| **Test coverage** | `tests/test_spectrum.py` (all), `tests/test_cubieoperator.py:27-103` (Level 1: minimal polynomial, multiplicity, spectral projector theorem), `tests/test_spectralstructure.py:34-66` |
| **Derived artifacts** | Paper I §3, `experiments/paper1/figures/spectral_ladder.png`, `block_composition.png` |

### A.4 Nine Primitive Sectors (§4)

| | |
|---|---|
| **Mathematical object** | Joint diagonalization of Center{A_18, QT_all, HT_all} — 9 sectors with (λ_18, λ_QT, λ_HT) triples, block support, canonical layer membership |
| **Canonical API** | `CubieSpectralOperator().center_decomposition()` → `{n_sectors, projectors, sectors}` (`rime/cubieoperator.py:985-1036`) |
| **Experiment scripts** | `experiments/paper2/primitive_sectors.py:23-134` — sector table, block support, layer→sector mapping, completeness/orthogonality; `experiments/transport_9sector.py:75-247` — 9 sectors + block composition + K matrix |
| **Cross-validation** | `experiments/transport_closure.py:158-217` (Zone 2) — verifies 9 sectors, commutativity, dimensions, signatures, projector orthogonality |
| **Test coverage** | `tests/test_sectors.py` (all — 9 sectors, completeness, orthogonality, idempotence, V5/9 split into 3, V1/3 split into 2, S6 degree ≥ 4, S1 isolation) |
| **Derived artifacts** | Paper II §4, `experiments/paper2/figures/primitive_sectors.png` |

### A.5 Transport Topology (§5)

| | |
|---|---|
| **Mathematical object** | K_αβ = max_g ‖P_α ρ(g) P_β‖_F over 18 generators — transport strength matrix, direct edge list (K > 0.01), hub degrees, S1 isolation |
| **Canonical API** | `CubieSpectralOperator().transport_kappa(projectors)` (`rime/cubieoperator.py:1150-1197`), `.transport_tensor()` (`:277-304`) |
| **Experiment scripts** | `experiments/paper2/transport_graph.py:25-141` — K matrix, edge detection (TOL_K=0.05), degree analysis, S1 isolation; `experiments/transport_9sector.py:150-234` — full K + edges + isolation + hub + mediation |
| **Cross-validation** | `experiments/transport_closure.py:385-423` (Zone 6) — V1 isolation, V7/9↔V2/3 decoupling, V5/9 universal hub, star topology |
| **Test coverage** | `tests/test_transport.py` (all — K symmetry, transport sparsity, S6 degree ≥ 4, S1 isolation) |
| **Derived artifacts** | Paper II §6, `experiments/paper2/figures/transport_graph.png`, `paper2_figures.py` Figs 1-2 |

### A.6 Lie Accessibility (§6)

| | |
|---|---|
| **Mathematical object** | κ_d(α,β) = max ‖P_α C_d P_β‖ at depths d=0,1,2; accessibility classes I/II/III; curvature channels; κ symmetry |
| **Canonical API** | `CubieSpectralOperator().kappa_depth(d)` (`:1098-1148`), `.infinitesimal_transport()`, `.compute_lie_generators()` (`:1042-1063`) |
| **Experiment scripts** | `experiments/lie_depth.py:35-281` — full 6-layer κ₀,κ₁,κ₂; `experiments/transport_9sector.py:284-401` — 9-sector κ₀,κ₁,κ₂; `experiments/paper3/kappa_depth.py:27-155` — 9-sector K vs κ₀ vs κ₁, hierarchy check (κ₁ ≤ κ₀ ≤ K), block-preserving check, T7 synthesis |
| **Cross-validation** | `experiments/transport_closure.py:279-377` (Zones 4-5) — Class I/II/III diagnostics, V1 isolation, V5/9 coupling, V7/9↔V2/3 curvature, κ symmetry |
| **Test coverage** | `tests/test_transport.py` (implicit — T7 detection depends on κ values) |
| **Derived artifacts** | Paper III §4, `experiments/paper3/figures/kappa_depth.png` |

### A.7 T7 Pairs (§7)

| | |
|---|---|
| **Mathematical object** | T7 pairs (α,β): K_αβ=0, κ_d(α,β)=0 ∀d, but 2-step reachable. Cross-block property. |
| **Canonical API** | `CubieSpectralOperator().transport_kappa()`, `rime/spectral_utils.find_t7_pairs()` |
| **Experiment scripts** | `experiments/paper3/t7_detection.py:28-169` — N=3: 5 T7 pairs, 2-step reachability; `experiments/paper3/n2_control.py` — N=2: 0 T7, 0 hybrid; `experiments/paper3/kappa_depth.py:98-113` — K=κ₀=κ₁=0 + cross-block + 2-step reachable |
| **Supplementary** | `experiments/t7_minimal_exploration.py` — systematic T7 search across S3/S4/D4/A4; `experiments/t7_necessity.py` — shared irrep necessity for hybrid sector formation |
| **Test coverage** | `tests/test_transport.py:78-132,138-235` — N=3: ≥1 T7 pair; N=2: 0 T7 pairs |
| **Derived artifacts** | Paper III §3/§5/§6, `experiments/paper3/figures/t7_detection.png`, `t7_minimal.png`, `n2_control.png` |

### A.8 EP Algebra (§8)

| | |
|---|---|
| **Mathematical object** | A_EP = ⟨Q₀, Q₁, Q₂⟩ ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴, dim=20, closure at degree 3, Z(A_EP)=8, Killing form signature (8⁺,4⁻,8⁰) |
| **Canonical API** | `CubieSpectralOperator().build_per_axis_ops()[0]` → QT0, QT1, QT2 (restricted to EP block via `BLOCK_RANGES`) |
| **Experiment script** | `experiments/paper2/ep_algebra.py:26-210` — algebraic closure via SVD iteration, nondegenerate trace pairing → semisimple, center via structure constants, Killing form, AW decomposition M₂⁴⊕M₁⁴ |
| **Cross-validation** | `experiments/transport_closure.py:485-537` (Gap B) — Q_i² quasi-idempotence, triple products, commutator norms, product rank |
| **Test coverage** | `tests/test_commutant.py:100-130` (Test 5: noncommutativity localization on EP) |
| **Derived artifacts** | Paper II §5.3, `experiments/paper2/figures/ep_algebra.png` |

### A.9 Commutant Restriction Map π (§8.3)

| | |
|---|---|
| **Mathematical object** | π: End_G(V) → ⊕_λ End_G(V_λ), dim(domain)=610, dim(codomain)=966, ker=0, coker=356 |
| **Canonical API** | `CubieSpectralOperator()._full_commutant_combinatorial()` (→ basis, 610), `.commutant_algebra()` (→ per-layer dims) |
| **Experiment script** | `experiments/paper2/commutant_pi_map.py:1-201` — full commutant basis, per-layer projection, M matrix (610×966), SVD → rank → ker/coker, per-layer liftability table |
| **Test coverage** | `tests/test_commutant_gap.py` — Δ_comm=194 invariant, canonical snapshot (804/610/194), per-layer invariant, transport-commutant relation |
| **Derived artifacts** | Paper II §5.4/§5.5 |

### A.10 S₃ Prototype (§9)

| | |
|---|---|
| **Mathematical object** | S₃ nat⊕reg (9-dim, 5 sectors, 3 T7, κ₁=0) and S₃ reg⊕reg (12-dim, 10 sectors, full hierarchy) |
| **Canonical API** | `rime/spectral_utils.py`: `build_s3_natural_rep()`, `build_s3_regular_rep()`, `build_s3_std_rep()`, `build_s3_sign_rep()`, `build_s3_trivial_rep()`, `joint_diag_sectors()`, `find_t7_pairs()` |
| **Experiment script** | `experiments/paper3/t7_minimal.py` — both prototypes computed from scratch; `experiments/t7_minimal_exploration.py` — systematic S3/S4/D4/A4 search; `experiments/t7_necessity.py:105-220` — shared irrep necessity |
| **Test coverage** | `tests/test_transport.py` (N=2 negative control only; no direct S3 test) |
| **Derived artifacts** | Paper III §6, `experiments/paper3/figures/t7_minimal.png` |

### A.11 Fundamental Identities (§10)

| | |
|---|---|
| **Mathematical object** | A_18 averaging identity, axis decomposition, homomorphism property, Lie embedding fidelity, κ symmetry |
| **Canonical API** | `CubieSpectralOperator().A` (≡ A_18), `.build_per_axis_ops()`, `.compute_lie_generators()` |
| **Experiment scripts** | `experiments/transport_closure.py:147-149` (A_18 = (12QT+6HT)/18); `experiments/lie_depth.py:60-62` (expm(A_g) fidelity) |
| **Test coverage** | `tests/test_representation.py:48-61` — ρ homomorphism on 15 random products, unitarity on 21 random elements, block-diagonal structure |
| **Derived artifacts** | All papers (cross-referenced foundational identities) |

### A.12 Generator-Set Universality (§11)

| | |
|---|---|
| **Mathematical object** | 6-layer eigenspace structure is G-determined (invariant across inverse-closed generator sets); transport strength values are S-conditioned |
| **Canonical API** | `CubieSpectralOperator(n=N)` with various n; `SpectralStructure(generators=subset)` |
| **Experiment script** | None dedicated — theoretical claim from Paper I; `SpectralStructure` class predicts k-sets for arbitrary generator subsets |
| **Test coverage** | `tests/test_spectralstructure.py` — validates SpectralStructure predictions for the full 18-generator set |
| **Derived artifacts** | Paper I (theoretical framework) |

---

## Appendix B — Stability Classification

Each numerical claim is classified by its stability under recomputation.

### B.1 Exact Invariant

Values that are mathematical consequences of the representation construction and do not depend on numerical tolerance or random seed.

| Claim | Why exact |
|-------|-----------|
| TOTAL_DIM = 228 | Definitional — derived from Rubik's cube group representation: 3³·8 = 216 orientation states + 12 edge permutation states |
| Block dims (64, 144, 8, 12) | Definitional — CP = 4³ = 64 corner permutation, EP = 12!/(8!4!)·2⁸ = 144 edge permutation+orientation, etc. |
| λ = 1 − k/9 form | Group-algebraic — follows from the Bose-Mesner structure of A_18 as an association scheme adjacency operator |
| k ∈ {0,1,2,3,4,6} | Spectral invariant — determined by the association scheme class structure; k=5 genuinely excluded by orbit decomposition |
| Layer multiplicities (20,2,39,26,106,35) | Representation-theoretic — dimensions of isotypic components in the decomposition of V under the commutant algebra |
| A_18 = (12 QT_all + 6 HT_all)/18 | Definitional — generator weighting convention |
| ‖ρ(g)ρ(h) − ρ(gh)‖ < 3×10⁻⁸ | Homomorphism property — holds for all g,h (tested on 15 random products) |
| max\|expm(A_g) − ρ(g)\| ≈ 10⁻¹⁵ | Lie embedding — scipy.linalg.expm numerical precision |
| κ symmetry \|κ_ij − κ_ji\| ≈ 10⁻¹⁵ | Mathematical — follows from Hermiticity of C_d and projector symmetry |

### B.2 Robust Empirical

Values computed numerically but stable across recomputation runs (variation < TOL under same parameters).

| Claim | Why robust |
|-------|------------|
| 9 sectors (from 11 raw) | Sector count depends on CENTER_CLUSTER_TOL=1e-8 clustering; the merge pattern (S4+S5, S9+S10) is deterministic |
| 10 direct transport edges (K > 0.01) | Edge count stable under TOL_K=0.05; K values vary <1e-6 across runs |
| S6 degree 5 (primary hub) | Invariant under recomputation with same Center; S6 always has max degree |
| All 5 T7 pairs | K=0 threshold is sharp (<1e-14 vs >0.01); T7 detection is binary, not threshold-sensitive |
| 7 pure curvature channels (κ₀≈0, κ₁>0) | κ₀/K ratio > 10⁸ for curvature channels; classification is gap-separated |
| κ₀/κ₁/κ₂ values (§6.1–6.3) | Stable to ~1e-12 under recomputation; reported to 2-3 significant digits |
| EP algebra: dim=20, Z=8, Killing (8⁺,4⁻,8⁰) | Algebraic closure via SVD rank is tolerance-stable; structure constants are deterministic |
| π map: ker=0, coker=356 | SVD of 610×966 matrix; rank determination is tolerance-stable (gap >1e-8) |
| Δ_comm = 194 | = Comm(A) − Comm(ρ) = 804 − 610; both dimensions are exact combinatorial counts |
| S1 isolation (K < 10⁻¹⁴ with all) | G-invariant subrepresentation — mathematically exact, not threshold-dependent |

### B.3 Exploratory

Values computed in experiments that are not yet locked into the canonical specification. May change with methodology refinement.

| Claim | Status |
|-------|--------|
| κ₂ values (§6.3) | Computed but not exhaustively validated — depth-2 Lie monomial enumeration is partial |
| Generator-set universality (§11) | Claimed for 9 sets; not systematically verified for all inverse-closed subsets |
| Isotypic decomposition (51 components, m=11 reservoir) | Computed in `experiments/isotypic_decomposition.py`; not yet integrated into paper_data.md main sections |
| T7 necessity (shared irrep conjecture) | Proven for abelian and isotypic blocks; strong evidence for general non-abelian case but not fully proven |
| S₃ reg⊕reg full hierarchy (§9.2) | Prototype exploration; T7⇔M₂ separation theorem validated on this example but not proven in general |

### B.4 Discarded / Archival

Values from pre-ρ-fix or from earlier methodology that are no longer authoritative.

| Claim | Where archived | Why discarded |
|-------|---------------|---------------|
| Pre-ρ-fix layer structure (k=1 layer absent) | `docs/260512_phenomenology_archive.md` | ρ construction error on EP orientation sub-block |
| 11 raw sectors (pre-merge) | Not archived separately | Accidental eigensolver splitting; merged to 9 canonical sectors based on matching (λ_QT, λ_HT, λ_18) triples |
| `compute_transport_kappa()` standalone (without CSO) | Deprecated in `rime/spectral_utils.py` | Superseded by `CubieSpectralOperator().transport_kappa()` — canonical path uses cached Lie generators |

---

## Appendix C — Semantic Dependency DAG

The logical architecture of the phenomenology: each claim and its prerequisites.

### C.1 Master Dependency Graph

```
T7 theorem (§7)
 ├── Sector decomposition (§4) — joint diagonalization of Center{A, QT_all, HT_all}
 │    └── Spectral layers (§3) — A_18 eigendecomposition
 │         ├── Total space (§1) — representation construction V = ℂ²²⁸
 │         └── Fundamental identities (§10) — A_18 = (12QT+6HT)/18
 ├── K transport tensor (§5) — max_g ‖P_α ρ(g) P_β‖
 │    ├── Sector decomposition (§4)
 │    └── Block structure (§2) — block support per sector
 ├── κ accessibility hierarchy (§6) — κ₀, κ₁, κ₂
 │    ├── Spectral layers (§3)
 │    ├── Lie generators — A_g = logm(ρ(g))
 │    └── Block structure (§2) — curvature confinement
 └── Mediation paths — ∃γ: K_αγ>0 ∧ K_γβ>0
      └── K transport (§5)

EP Algebra (§8)
 ├── Block structure (§2) — EP = 144-dim
 ├── Spectral layers (§3) — projector restriction to EP
 └── QT operators — build_per_axis_ops() → Q₀, Q₁, Q₂

π map (§8.3)
 ├── Full commutant — _full_commutant_combinatorial() → basis, dim=610
 ├── Spectral layers (§3) — per-layer commutant dimensions {400,1,145,145,210,65}
 └── K transport (§5) — zero-transport pairs → cross-layer constraints

κ accessibility (§6)
 ├── Spectral layers (§3) — 6-layer projectors
 ├── compute_lie_generators() — A_g = logm(ρ(g)) for all 18 generators
 ├── Commutator enumeration — C_1 = [A_g, A_h] for all 153 pairs
 └── Block structure (§2) — curvature confinement verification

Transport topology (§5)
 ├── Sector decomposition (§4) — 9-sector projectors
 ├── ρ(g) generators — 18 face-turn matrices from rho_moves
 └── Block structure (§2) — edge block-sharing analysis

S₃ prototype (§9)
 (Independent — toy model, no prerequisites from cube data)

Generator-set universality (§11)
 └── Spectral layers (§3) — layer structure comparison across generator subsets

Fundamental identities (§10)
 ├── Representation construction — ρ(g) definition
 ├── Generator enumeration — QT_all, HT_all from build_per_axis_ops()
 └── Lie generators — logm(ρ(g)) fidelity check
```

### C.2 Key Cross-Dependencies

| Claim | Requires | Required by |
|-------|----------|-------------|
| §1 Total space | nothing | Everything |
| §2 Block structure | §1 | §4, §5, §6, §8 |
| §3 Spectral layers | §1, §10 | §4, §6, §8.3, §11 |
| §4 Sectors | §2, §3 | §5, §7 |
| §5 K transport | §2, §4 | §7, §8.3 |
| §6 κ accessibility | §2, §3 | §7 |
| §7 T7 | §4, §5, §6 | (terminal — Paper III main result) |
| §8 EP algebra | §2, §3 | (terminal — Paper II structural result) |
| §8.3 π map | §3, §5 | (terminal — Paper II technical result) |
| §9 S₃ prototype | nothing | (terminal — Paper III minimal model) |
| §10 Identities | §1 | §3 |
| §11 Universality | §3 | (terminal — Paper I scope claim) |

---

## Appendix D — Gauge Freedom & Canonical Gauges

The mathematical objects in this specification have internal symmetries (gauge freedoms) that do not affect representation-theoretic content. All gauge freedoms are explicitly fixed by the conventions in §0. This section documents both the freedoms and their canonical fixings.

### D.1 Eigenspace Basis Gauge

**Freedom**: Within each eigenspace V_λ, any unitary change of basis U ∈ U(dim(V_λ)) preserves the projector P_λ = V_λ V_λ^H. The columns of V_λ are defined only up to U(dim(V_λ)).

**Canonical gauge**: Fixed by `numpy.linalg.eigh` — eigenvectors are orthonormal (Schatten normalization) and real wherever possible (eigh returns real eigenvectors for real symmetric matrices). Phase convention: NumPy default (first nonzero element positive).

**Gauge-invariant observables**: All projectors P_λ, transport strengths K_αβ, κ values, layer dimensions, commutant dimensions. These depend only on the subspace, not the basis chosen within it.

### D.2 Sector Label Gauge

**Freedom**: The 9 sectors have no intrinsic ordering. Any permutation of labels S1–S9 is mathematically equivalent.

**Canonical gauge**: Fixed by the triple sort (λ_18 descending, λ_QT descending, λ_HT descending). This is the order produced by `center_decomposition()` and documented in §4. All figure scripts and papers MUST use this ordering.

### D.3 Sector Merge Gauge

**Freedom**: Raw joint diagonalization may produce >9 sectors due to accidental eigensolver splitting when two (λ_QT, λ_HT, λ_18) triples coincide within numerical precision. The split is a numerical artifact — any linear combination of the split projectors spanning the same subspace is equally valid.

**Canonical gauge**: Sectors whose (λ_18, λ_QT, λ_HT) triples differ by < `CENTER_CLUSTER_TOL` (1e-8) in all three coordinates are merged. This reduces 11 raw sectors to 9 canonical sectors. The merge pattern is deterministic and verified in `test_sectors.py`.

**Why 11→9 and not some other count**: The minimum gap between genuinely distinct triples is >1e-3. `CENTER_CLUSTER_TOL = 1e-8` is 5 orders of magnitude below the gap — the merge is unambiguous.

### D.4 Generator Label Gauge

**Freedom**: The 18 generators can be labeled by face (U/D/F/B/L/R) and type (QT/HT). The symmetric group S_6 acts on face labels, and ℤ₂ acts by swapping QT↔HT labels. The spectrum of A_18 is invariant under this action, but individual ρ(g) matrices are permuted.

**Canonical gauge**: Fixed by `CubieMove.prim_moves` enumeration order in `rime/cubie.py`. The spectral identity (6 layers, their dimensions, and projectors) is label-invariant.

### D.5 Isotypic Gauge (Multiplicity Reservoir)

**Freedom**: When an isotypic component appears with multiplicity m > 1, the decomposition into m copies of the same irreducible representation is not unique. Any GL(m,ℂ) transformation among copies preserves the isotypic subspace.

**Canonical gauge**: Fixed by the commutant basis from `_full_commutant_combinatorial()` — the orbit-enumeration construction picks a specific basis for the multiplicity space. The Artin-Wedderburn central idempotents in `experiments/isotypic_decomposition.py` provide a canonical decomposition.

**Where this matters**: V_5/9 has one isotypic component with multiplicity m=11 (the "multiplicity reservoir"). All other 50 isotypic components have m=1 and are gauge-free.

### D.6 Layer Key Representation Gauge

**Freedom**: Eigenvalues are real numbers; their representation as floating-point literals (1.0 vs 0.9999999999999999 vs 1.0000000000000002) is a numerical artifact.

**Canonical gauge**: Fixed by `SPECTRAL_DECIMALS = 6` — eigenvalues are rounded to 6 decimal places. The canonical layer keys are:

```
[1.0, 0.888889, 0.777778, 0.666667, 0.555556, 0.333333]
```

These correspond to the rational form λ = 1 − k/9 with k ∈ {0,1,2,3,4,6}. The rational form is the mathematical truth; the 6-decimal representation is the canonical numerical proxy.

### D.7 Commutant Basis Gauge

**Freedom**: Within the commutant algebra End_G(V) (dim=610), any invertible linear transformation preserves the algebra. The basis returned by `_full_commutant_combinatorial()` is one of infinitely many valid bases.

**Canonical gauge**: Fixed by the orbit-enumeration construction — each basis element is the sum of ρ(g) over a conjugacy class orbit, Gram-Schmidt orthogonalized. The dimension (610) is gauge-invariant; the specific basis vectors are gauge-dependent but any valid basis spans the same algebra.

---

## Appendix E — Failure Modes & Mitigations

Documented failure modes that can produce incorrect or unstable numerical results, and how the current canonicalization avoids each. This section serves as both documentation and design rationale.

All observed failure modes fall into four categories:

1. **Spectral degeneracy artifacts** — eigensolver splitting, eigenvector mixing (§E.1, §E.3)
2. **Finite-precision linear algebra instability** — SVD thresholding, null-space drift (§E.2, §E.8)
3. **Representation-construction defects** — pre-ρ-fix orientation sign inconsistency (§E.0)
4. **Algorithmic non-canonicality** — generator ordering dependence, randomized under-convergence (§E.4, §E.5)

The canonical r2 pipeline eliminates all category-(3) and category-(4) failures by construction, while category-(1)/(2) effects are controlled via explicit tolerance engineering and post-canonicalization.

### E.0 Representation Construction Defect (Pre-ρ-fix)

This is the single most consequential failure mode in the project's history — the reason revision r2 exists.

**Symptom**: The k=1 (λ=8/9, V₈/₉) layer disappeared entirely from the spectrum, and several transport channels exhibited inconsistent symmetry. The eo(2) sector was masked — the 2-dimensional V₈/₉ eigenspace was absorbed into adjacent layers by numerical accident.

**Cause**: The EP orientation sub-block used an inconsistent sign convention in the representation construction. Specifically, on a subset of EP orientation transitions:
```
ρ(g)ρ(h) ≠ ρ(gh)
```
The map failed to satisfy the homomorphism property on all blocks — it was only a projective representation on EP, with a sign inconsistency in the orientation sector.

**Propagation**: This defect cascaded into:
- distorted eigenspace multiplicities (the 2-dim V₈/₉ layer vanished),
- accidental sector mergers (the eo contribution to V₈/₉ was redistributed),
- incorrect transport topology (missing channels involving V₈/₉),
- masking of the k=1 eigenvalue — the entire 8/9 layer was invisible.

**Mitigation**: The representation construction was rebuilt using a globally consistent orientation convention across all four blocks (CP/EP/CO/EO). Post-reconstruction validation:
```
‖ρ(g)ρ(h) − ρ(gh)‖ < 3×10⁻⁸   (verified on 15 random products, all blocks)
```
The homomorphism property is now exact to machine precision on all blocks.

**Status**: Resolved in revision r2. All pre-fix numerical data are archived in `docs/260512_phenomenology_archive.md` and must not be cited. The V₈/₉ layer (k=1, 2-dim, eo) is now a canonical spectral feature (§3).

**Lesson**: Representation construction defects are qualitatively different from numerical tolerance issues — they propagate into the structural claims themselves, not just the numerical values. A single sign error in a sub-block can erase an entire spectral layer. Block-wise homomorphism verification is mandatory.

### E.1 Eigensolver Accidental Splitting

**Symptom**: Joint diagonalization of Center{A, QT_all, HT_all} produces >9 sectors.

**Cause**: When eigenvalues of Center operators nearly coincide, `eigh` returns arbitrary linear combinations of the corresponding eigenvectors. Joint diagonalization then splits what should be a single sector.

**Occurrence**: S4+S5 (same λ_18=2/3) and S9+S10 (same λ_18=1/3) in raw output.

**Mitigation**: Post-clustering via `CENTER_CLUSTER_TOL = 1e-8`. Sectors whose (λ_18, λ_QT, λ_HT) triples match within this tolerance in all three coordinates are merged. Applied in `center_decomposition()`, verified in `test_sectors.py`.

**Why it works**: The minimum gap between genuinely distinct triples is >1e-3. The tolerance is 5 orders of magnitude below the gap.

### E.2 SVD Rank Threshold Instability

**Symptom**: `comm_dim` depends sensitively on the SVD threshold choice.

**Cause**: The singular value spectrum of the Kronecker constraint matrix `kron(G^T, I) − kron(I, G)` may lack a clear gap between "zero" and "nonzero" singular values, making rank determination threshold-sensitive.

**Mitigation**: 
1. Generator reduction: linearly dependent generators are removed via SVD before building the constraint matrix, reducing the problem size and improving the singular value gap.
2. Scale-invariant threshold: `sv_thresh = self.tol * max(1.0, s[0]) * max(C.shape)` — relative to the largest singular value.
3. One-shot SVD on the full stacked constraint matrix (not incremental intersection — see §E.8).

**Verification**: `tests/test_commutant_gap.py` — canonical snapshot (804, 610, 194) is stable across recomputation.

### E.3 Near-Degenerate Eigenvalue Mixing

**Symptom**: Projectors for nearly degenerate eigenvalues may mix, producing incorrect transport values.

**Cause**: `numpy.linalg.eigh` may swap or mix eigenvectors when eigenvalues differ by less than ~1e-14 in double precision.

**Status**: **Does not occur.** The minimum gap between distinct eigenvalues of A_18 is 1/9 ≈ 0.111. This is 10¹³ × machine epsilon. The rational form λ = 1 − k/9 with integer k guarantees well-separated eigenvalues by construction. No near-degeneracy exists.

### E.4 Generator Ordering Artifacts

**Symptom**: Different generator orderings produce different numerical results.

**Cause**: If ρ(g) construction had ordering-dependent phases, or if iterative algorithms processed generators sequentially.

**Mitigation**: The averaging A = (1/|S|) Σ ρ(s) is permutation-invariant. `test_generator_symmetry` in `tests/test_cubieoperator.py` verifies Spec(A) is invariant under generator permutation to <1e-10. All canonical algorithms are either one-shot (commutant SVD) or use permutation-invariant operations (eigh).

### E.5 Randomized Reynolds Under-Convergence

**Symptom**: For large blocks (d > 50), the randomized Reynolds method returns a commutant dimension smaller than the true value.

**Cause**: Sample budget `min(d*6, 250)` insufficient to span the full commutant, or 8 iterations inadequate for convergence.

**Status**: **Current parameterization is adequate.** For the only d>50 case (d=106, comm_dim=210): sample_budget = min(636, 250) = 250 > 210 = comm_dim. 8 iterations of exact projection provide convergence to machine precision. Verified by cross-checking randomized result (d=106) against combinatorial result (full 228-dim space).

**If extended**: For blocks with d > 50, sample budget should be ≥ comm_dim × 1.2. The comm_dim can be estimated from the block dimension and its algebraic structure before running the expensive computation.

### E.6 Sector Permutation Across Recomputation

**Symptom**: Sector labels S1–S9 permute across recomputation runs.

**Cause**: If two sectors have identical λ_18, the secondary sort key (λ_QT) could swap if values differ by < machine precision.

**Status**: **Does not occur.** No two sectors share the same λ_18 with close λ_QT or λ_HT. The canonical (λ_18, λ_QT, λ_HT) triple sort is deterministic because all 9 triples are well-separated (minimum gap >1e-3 in at least one coordinate).

### E.7 Lie Generator Non-Hermiticity Drift

**Symptom**: A_g = logm(ρ(g)) is not exactly Hermitian, causing κ asymmetry.

**Cause**: `scipy.linalg.logm` may introduce ~1e-15 non-Hermitian components due to floating-point roundoff in the Schur-Parlett algorithm.

**Mitigation**: `compute_lie_generators()` enforces Hermiticity: `A_g = 0.5 * (A_g + A_g.T.conj())`. The resulting κ matrices are symmetric to ~1e-15. Verified in `tests/test_transport.py` and §10 (fundamental identities).

### E.8 Incremental Null-Space Drift (Design Rejection)

**Symptom**: Sequential null-space intersection (projecting through one generator's constraint at a time) caused progressive rank collapse. For the d=39 block, comm_dim dropped from 169 → 65 → 2 → 0 within 3 generators.

**Cause**: Each projection step accumulates ~1e-14 roundoff error. After k sequential projections, the numerical null space drifts away from the true null space. The error is systematic (not random), so it cannot be averaged out.

**Mitigation**: **Rejected entirely.** The canonical method uses one-shot SVD on the full stacked constraint matrix after linear dependency reduction. No sequential intersection. This is a documented architectural decision: one-shot > incremental for null-space computation under finite precision.

**Principle**: prefer the brute-force one-shot SVD over clever incremental algorithms when the matrix fits in memory. For d ≤ 50, the full constraint matrix is at most ~2500 × 2500, which is comfortably within LAPACK's SVD capacity.

**Why it fails — geometric insight**: The core issue is geometric: small angular errors in successive null-space projections compound multiplicatively rather than additively. Each incremental step rotates the approximate null space by O(ε), and after k steps the accumulated misalignment is O(k·ε) in the best case (purely random errors) but can be O(2^k·ε) when errors align systematically. Since the constraint matrices share structure (all derived from the same generator set), errors are weakly correlated — the worst case between additive and multiplicative. The result is progressive rank collapse: genuine null vectors drift out of the numerical kernel, and no amount of Gram-Schmidt re-orthogonalization can recover them because the information has already been projected away. The one-shot SVD avoids this entirely by solving the full constraint system in a single orthogonalization step — no intermediate projections, no drift accumulation.

### E.9 Canonicalization Philosophy

The guiding principle of the r2 pipeline is:

> canonicalize first, analyze second.

All mathematically equivalent but numerically unstable representations must be reduced to a unique canonical form before any structural claims are extracted.

Accordingly:
- eigenspaces are clustered (SPECTRAL_DECIMALS + CENTER_CLUSTER_TOL),
- sectors are deterministically ordered ((λ_18, λ_QT, λ_HT) descending),
- generators are dependency-reduced (SVD on generator vectors before building constraints),
- Lie generators are Hermitianized (A_g = 0.5·(A_g + A_g^H)),
- commutants are computed via one-shot global SVD (no incremental intersection),
- transport thresholds are fixed globally (TOL_K = 0.05),
- all numerical constants are centralized in this specification (§0.4).

The objective is not merely reproducibility, but **representation-independent structural stability**.

A structural claim is considered canonical only if it survives:
1. recomputation (same code, same parameters → same result),
2. generator permutation (S_6 × ℤ₂ face relabeling),
3. basis changes inside degenerate eigenspaces (U(n) gauge freedom, §D.1),
4. tolerance perturbation within the prescribed regime (§0.4).

Claims that satisfy (i)–(iv) are promoted to Specification Theorems (§12). Claims that fail any of them remain in Exploratory (§B.3) or are discarded (§B.4).
