# STRUCTURE — Project Ontology

**Date**: 2026-05-12
**Status**: POST-RHO-FIX — updated for 6 canonical layers, 9 primitive sectors, CO/EO noncommutativity sidebands

> **谱层不是 object。分解之间的关系才是 object。**

---

## Primary Objects

### 1. Averaging Operators — A_S

```
A_S = (1/|S|) Σ_{g∈S} ρ(g)
```

The input to everything. For any inverse-closed generator subset S ⊂ {18 face turns}. Hermitian (Proposition 2.1, Paper I).

**Key instances** (in descending symmetry):

| Operator | S | |S| | Commutes with |
|----------|---|-----|--------------|
| A_18 | all 18 face turns | 18 | Everything |
| QT_all | CW+CCW only (direction ≠ 2) | 12 | Everything |
| HT_all | 180° only (direction = 2) | 6 | Everything |
| QT^a | CW+CCW on axis a | 4 | HT^a, QT^a, HT_all |

**Fundamental identity**: A_18 = (12 QT_all + 6 HT_all) / 18

**Noncommutativity**: ‖[QT^i, QT^j]‖ = 2.92 total. Per block: cp=0 (exact), ep=2.74 (93.9%), co=0.61 (21.0%), eo=0.79 (27.1%). EP-dominant hierarchy.

**Commutative center**: {A_18, QT_all, HT_all} — M = {A_18, QT_all, HT_all} is a commuting triple (‖[·,·]‖ < 10⁻¹⁵). These generate the commutative core of the refinement lattice.

---

### 2. Spectral Decompositions — D(A_S)

Each A_S induces a decomposition by its eigenspaces:

```
D(A_S) = {Eigenspace projectors of A_S}
```

**Key decompositions**:

| Decomposition | Layers | Dims |
|--------------|--------|------|
| 18-gen (A_18) | 6 | 20, 2, 39, 26, 106, 35 |
| QT (12) | 6 | 20, 36, 68, 68, 28, 8 |
| HTM (6) | 3 | 72, 72, 84 |
| Center {A_18, QT_all, HT_all} | 9 | 20, 2, 39, 26, 1, 39, 66, 8, 27 |
| Axis-0 (R/L, 6) | 3 | 100, 8, 120 |
| Axis-1 (U/D, 6) | 2 | 108, 120 |
| Axis-2 (F/B, 6) | 3 | 92, 8, 128 |
| QT^a (per-axis, 4) | 3–4 | varies |

**Compatibility**: Every D(A_S) is a coarsening or refinement of D(A_18). Projector overlaps are exact integers — no continuous rotation between decompositions. The set of all compatible decompositions is:

```
D = {D(A_S) : S ⊂ {18 face turns}, S inverse-closed}
```

**G-universal**: The eigenspaces (invariant subspaces) are G-determined. Different S only change how they aggregate — they never rotate the subspace basis.

---

### 3. Refinement Semilattice — L

D forms a POSET under refinement:

```
D₁ ≤ D₂  ⇔  every projector of D₂ is a sum of projectors of D₁
         ⇔  A_D₂ ∈ ⟨A_D₁⟩  (algebraic inclusion)
```

**Theorem**: D₁ ≤ D₂ ⇒ [A_D₁, A_D₂] = 0. Refinement requires commutativity.

**Commutative core C** — decompositions from global (cubic-symmetric) operators:

```
           Center (9)    ← universal meet
          ↙    ↓    ↘
        QT    18-gen   HTM
       (6)     (6)     (3)
```

C is a **∧-semilattice**: meets exist for all pairs (Center is universal meet). Joins do not always exist within C.

**Noncommutative boundary** — per-axis decompositions:

```
QT^0 → Axis₀    QT^1 → Axis₁    QT^2 → Axis₂
```

Per-axis operators on different axes do NOT commute → their decompositions are **incompatible** — cannot be placed in the same refinement hierarchy. Physical analogue: L_x and L_y cannot be simultaneously diagonalized. But L² = L_x²+L_y²+L_z² (analogue: QT_all) commutes with everything.

**EP is the dominant obstruction to global lattice completion** (93.9% of total noncommutativity). CO and EO carry weak sidebands (‖[QT⁰,QT¹]‖_co=0.61, ‖[QT⁰,QT¹]‖_eo=0.79) — minor secondary obstructions from the perm@phase structure. If all blocks were commutative, all per-axis decompositions would mutually refine, and L would be a global distributive lattice.

---

### 4. Primitive Sectors — Minimal Simultaneous Eigenspaces

The **Center** = {A_18, QT_all, HT_all}. Since these three mutually commute, they admit joint diagonalization → 9 primitive sectors:

| Sector | dim | λ_18 | λ_QT | λ_HT | Block support | k | Role |
|--------|-----|------|------|------|-------------|---|------|
| S1 | 20 | 1 | 1 | 1 | cp(8)+ep(12) | 0 | **ISOLATED**: K=κ₀=κ₁=0 with all |
| S2 | 2 | 8/9 | 5/6 | 1 | eo(2) | 1 | NEW (was masked pre-ρ-fix) |
| S3 | 39 | 7/9 | 5/6 | 2/3 | ep(36)+eo(3) | 2 | Metastable basin |
| S4 | 26 | 2/3 | 1/2 | 1 | ep(24)+co(2) | 3 | **Unique primitive canonical layer** |
| S5 | 1 | 5/9 | 1/3 | 1 | eo(1) | 4 | Tiny EO piece |
| **S6** | **39** | **5/9** | **1/2** | **2/3** | **ep(36)+eo(3)** | **4** | **PRIMARY HUB** (degree 5) |
| S7 | 66 | 5/9 | 2/3 | 1/3 | cp(24)+ep(36)+co(3)+eo(3) | 4 | Secondary hub (degree 3) |
| S8 | 8 | 1/3 | 0 | 1 | cp(8) | 6 | Pure CP |
| S9 | 27 | 1/3 | 1/3 | 1/3 | cp(24)+co(3) | 6 | CP+CO |

**Only V₈/₉ (k=1) and V₂/₃ (k=3) are single-sector canonical layers.** All other canonical layers merge 2–3 primitive sectors. k=5 (λ=4/9) is genuinely absent from the spectrum.

**Transport topology (9-sector):**
- S6 (ep+eo, k=4, degree=5) = primary hub; S7 (mixed, k=4, degree=3) = secondary
- 10 direct edges, ALL block-preserving (0 cross-block)
- S1 (V₁, 20-dim) completely isolated at all levels (K=κ₀=κ₁=0)

---

### 5. Transport Morphisms — P_i ρ(g) P_j

For projectors P_i, P_j onto spectral sectors (at any resolution):

```
T_ij(g) = P_i ρ(g) P_j        (operator-level transport)
K_ij = max_g ‖T_ij(g)‖_F      (transport coefficient)
κ_ij = max_g ‖P_i A_g P_j‖_F  (infinitesimal transport)
```

**9-sector transport graph** (star with dual hub):
```
S1 (isolated, 20-dim)

S2(eo) ──┐
          ├── S6(ep+eo, PRIMARY HUB, deg=5) ──┬── S4(ep+co)
S3(ep+eo)─┘                                   ├── S5(eo)
                                              └── S7(cp+ep+co+eo, SECONDARY, deg=3) ── S9(cp+co)
                                                                                        ── S8(cp)
```
All 10 direct edges are block-preserving. S1 fully isolated (K=κ₀=κ₁=0). Cross-block transport requires length-2 composition through the S6–S7 hub complex.

**Algebraic selection rule**: Two-type transport taxonomy (Paper II Structural Principle A). Type I: K_αβ > 0 ⇔ Supp_nc(α) ∩ Supp_nc(β) ≠ ∅ (9 of 10 edges, M₂-driven noncommutative mixing). Type II: K_αβ > 0 via shared CP block + permutation adjacency (S8↔S9, 1 edge, commutative permutation channel). QT averaging commutativity ≠ individual generator commutativity — the CP block is exactly commutative under QT averaging (‖[QT⁰,QT¹]‖_cp=0) yet dynamically active under individual ρ(g). V₇/₉↔V₂/₃ decoupling = orthogonal Krawtchouk eigenspaces (k=2 vs k=3) in cp Bose-Mesner algebra.

**κ_ij symmetry**: max|κ_ij − κ_ji| ≈ 10⁻¹⁵. No directed transport barrier.

**Hom-space structure** (at 9-sector resolution):
```
End(S1)=1, End(S6)=15, End(S7)=15, ...
Hom(S3, S6)=10, Hom(S4, S6)=3, Hom(S4, S9)=1, ...
Hom(cross-block pairs without shared Supp_nc) = 0
```
Each End(V_i) is a symmetric Frobenius *-algebra. Hom(V_j, V_i) are (End(V_i), End(V_j))-bimodules.

**Composition mediation**: Direct Hom(cross-block) = 0 but composition through hybrid sectors (S6, S7) provides length-2 paths — categorical form of T7.

---

### 6. Lie Closure Hierarchy — span{A_g}, [A_g, A_h], ...

```
A_g = log ρ(g)              (via scipy.linalg.logm, fidelity 10⁻¹⁵)
κ_d(i,j) = max ‖P_i C_d P_j‖_F   (C_d = depth-d Lie monomial)
```

**Three accessibility classes** (at depth 0–1):

| Class | Sectors | Mechanism |
|-------|---------|-----------|
| **I** (subrep-isolated) | S1 (V₁) only | P₁ A_g P_j = 0 ∀g, ∀j≠1. Truly G-invariant subspace. |
| **II** (gradient-coupled) | Most non-V₁ pairs | κ₀ > 0 — individual A_g couple them |
| **III** (curvature-coupled) | V₇/₉↔V₂/₃ | κ₀ ≈ 10⁻¹⁴, κ₁ = 4.27, κ₂ = 13.4 |

**Note (2026-05-11, survives ρ-fix)**: V₁/₃ is gradient-coupled to V₅/₉ (κ₀ = 6.38). Isotypically pure ≠ Lie-isolated — cp-only sectors can couple through individual A_g. Only S1 (V₁) is truly subrepresentation-isolated.

**Class III mechanism**: Individual A_g preserve Krawtchouk order (k=2 vs k=3 orthogonal in cp). Commutators [A_g, A_h] mix across orders → curvature restores coupling. Enhancement κ₁/κ₀ ~ 10¹⁴.

**6 pure curvature channels** (κ₀≈0, κ₁>0) — all **within-block** (share EP or EO support). 0 cross-block curvature channels. Curvature is strictly block-preserving.

**T7 (Composition ⊋ Lie)**: 5 cross-block pairs (S2↔S4, S3↔S9, S4↔S5, S4↔S8, S6↔S9) have K=κ₀=κ₁=0 but are reachable via length-2 discrete composition through the S6–S7 hub complex. Lie is block-preserving at ALL depths (Lemma 1); composition bridges through hybrid sectors.

**Jacobi obstruction**: A_g do NOT satisfy Jacobi identity. Mean residual ‖[A,[B,C]]+[B,[C,A]]+[C,[A,B]]‖ ≈ 47 (full), ≈ 7.9 (projected). Structure is a **Lie 2-algebra**, not a Lie algebra.

---

## Block Decomposition

The 228-dimensional representation decomposes into four blocks:

| Block | Dim | Algebraic structure | Dynamical role |
|-------|-----|--------------------|----------------|
| **cp** (corner permutation) | 64 | Q₃ Hamming scheme H(3,2) → Bose-Mesner algebra ≅ Hecke H(S₂≀S₃, S₃) | Passive — fully commutative |
| **ep** (edge permutation) | 144 | Face-incidence commutative algebra (3-dim JJ^T) | **Dynamical core** — dominant carrier of noncommutativity (93.9%) |
| **co** (corner orientation) | 8 | Z₃ phase structure, weak noncommutative | Weak curvature sideband (‖[QT⁰,QT¹]‖=0.61) |
| **eo** (edge orientation) | 12 | Z₂ phase structure, FB/non-FB classification | Weak curvature sideband (‖[QT⁰,QT¹]‖=0.79); carries λ=8/9 |

---

## G-Universal vs S-Conditioned

| Object | Determined by |
|--------|--------------|
| A_S | S (by definition) |
| D(A_S) — the eigenspaces themselves | **G** (same invariant subspaces; only aggregation changes) |
| L — the refinement POSET | **G** (POSET structure is G-determined) |
| Primitive sectors (9) | **G** (Center of A_avg is G-determined) |
| P_i ρ(g) P_j — transport topology (K_ij > 0?) | **G** (topology), S (strength values) |
| P_i ρ(g) P_j — transport strengths | S |
| Lie closure hierarchy — generators {A_g} | S (which generators exist) |
| Lie closure hierarchy — algebraic relations | **G** (representation determines Krawtchouk orders, block structure) |

---

## Relationships Between Primary Objects

```
Object 1 (A_S)
    │
    ├── Object 2 (D(A_S)) ── each A_S gives a spectral decomposition
    │       │
    │       └── Object 3 (L) ── all D(A_S) together form the refinement POSET
    │               │
    │               └── Object 4 (9 primitive sectors) ── Center meet = finest decomposition
    │
    └── Object 5 (T_ij) ── transport morphisms between sectors of any D(A_S)
            │
            └── Object 6 (Lie closure) ── infinitesimal structure of T_ij
                    │
                    └── Accessibility classes (I/II/III) by Lie depth
```

**Key insight**: Objects 2–4 describe *structure* (what decompositions exist and how they relate). Objects 5–6 describe *dynamics* (how amplitude moves between sectors). The two are linked: the refinement lattice constrains which transport channels can exist (refinement requires commutativity; noncommutativity blocks lattice completion).

---

## Object Dependency Graph

Direction: A → B means "B is constructed from A" or "B's definition requires A."

```
                         ┌─────────────────────────────┐
                         │  Group G, rep ρ, gens S      │
                         │  (external input)            │
                         └──────────┬──────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │  A_S     │   │  ρ(g)    │   │ A_g=     │
              │  Obj 1   │   │  (raw)   │   │ log ρ(g) │
              └────┬─────┘   └────┬─────┘   └────┬─────┘
                   │              │              │
                   ▼              │              │
             ┌──────────┐        │              │
             │ D(A_S)   │        │              │
             │  Obj 2   │        │              │
             └────┬─────┘        │              │
                  │              │              │
                  ▼              ▼              │
            ┌──────────┐  ┌──────────────┐     │
            │    L     │  │ T_ij =       │     │
            │  Obj 3   │  │ P_i ρ(g) P_j │     │
            └────┬─────┘  │   Obj 5      │     │
                 │        └──────┬───────┘     │
                 ▼               │              │
          ┌────────────┐        │              │
          │ Primitive  │        │              │
          │ sectors (9)│        │              │
          │   Obj 4    │        │              │
          └────────────┘        │              │
                                │              │
                    ┌───────────┼──────────────┘
                    │           │
                    ▼           ▼
              ┌──────────────────────┐
              │  L = Lie{A_g}        │
              │  + [A_g, A_h], ...   │
              │       Obj 6          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Accessibility classes │
              │ I / II / III          │
              │ (κ_d depth hierarchy) │
              └──────────────────────┘
```

**Two parallel chains, one joint closure:**

| Chain | Objects | Nature | Paper |
|-------|---------|--------|-------|
| **Structural** (left) | 1 → 2 → 3 → 4 | Static: decompositions, refinement, primitive sectors | I |
| **Dynamical** (center/right) | 5 → 6 | Dynamic: transport morphisms → Lie accessibility | II, III |

The chains are NOT independent. The structural chain constrains the dynamical chain:
- Refinement requires commutativity → L constrains which D(A_S) can jointly diagonalize
- EP noncommutativity blocks global lattice completion → transport topology is star S₃, not complete graph
- Primitive sector composition determines which κ_d channels are gradient vs. curvature-mediated

---

## Invariant Hierarchy Map

Each object's status in the Level 0/1/2/3 hierarchy (see VERIFIED.md):

| Object | Dependence | Level | Closure Status |
|--------|-----------|-------|----------------|
| A_S | S (by definition) | — | **Input** — not derived |
| D(A_S) eigenspaces | **G** | 0 (categorical) | **Closed** — G-determined invariant subspaces |
| D(A_S) aggregation | S | 2 | **Closed** — only eigenvalue merging depends on S |
| L (refinement POSET) | **G** | 0 (categorical) | **Closed** — POSET structure is G-universal |
| L (∧-semilattice) | **G** | 1 (group algebra) | **Theorem-grade** — commutativity⇒compatibility |
| L (join failure) | **G** (EP noncomm) | 1 | **Needs formalization** — boundary obstruction theorem |
| Primitive sectors (9) | **G** (Center) | 1 | **Closed** — Center{A_18, QT_all, HT_all} |
| T_ij topology (K_ij > 0?) | **G** | 1 | **Closed** — Supp_nc intersection (Paper II central theorem) |
| T_ij strength values | S | 2 | **Not invariant** — S-conditioned |
| κ_ij symmetry | **G** | 1 | **Closed** — ‖[QT^i, QT^j]‖ symmetry |
| Lie generators {A_g} | S | 2 | **Not invariant** — which generators exist |
| Lie accessibility classes | **G** | 1 | **Closed** — isotypic purity determines class |
| κ_d depth values | **G** + S | 1/2 | **Mostly closed** — topology is G, magnitudes are S |
| EP algebra type | **G** | 1 | **A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴ — semisimple, AW decomposition complete** |

**Reading the closure column:**
- **Closed** = theorem-grade or exact numerical (no further discovery needed)
- **Theorem-grade** = correct structure known, formal theorem statement needed
- **Needs formalization** = mechanism understood, rigorous proof pending
- **OPEN** = algebraic identity not yet determined
- **Not invariant** = S-conditioned; value depends on generator choice

---

## Survival Map — Primary vs. Derived vs. Dead

```
PRIMARY (6 objects)
├── A_S                         ← input, not derived
├── D(A_S)                      ← spectral decomposition
├── L                           ← refinement POSET
├── Primitive sectors (9)       ← Center meet
├── T_ij = P_i ρ(g) P_j         ← transport morphisms
└── L = Lie{A_g}                ← Lie closure hierarchy

DERIVED (phenomenology, NOT primary)
├── 6 spectral layers           ← one node in L (D(A_18))
├── 9 primitive sectors         ← Center meet (finest resolution)
├── Star transport graph        ← from T_ij topology (S6 primary hub)
├── Charge types O/A/B/AB/R     ← interpretive classification
├── Phase automaton M_ij        ← from T_ij + generator sampling [ARCHIVED]
├── Controllability ranks G_i   ← from T_ij [ARCHIVED]
├── Persistence times τ_i       ← empirical from M_ij [ARCHIVED]
├── Curvature channels κ₁>0     ← from [A_g, A_h]
├── Spectral energy V(Δ)        ← from τ_i + projectors [ARCHIVED]
└── Annealing phase structure   ← from V(Δ) + Lie depth [ARCHIVED]

DEAD (ARTIFACT graveyard)
├── One-way barriers            ← broken logm (A1)
├── Discrete-continuous singularity ← same (A2)
├── V₂/₃ freezing               ← same (A3)
├── Universal 5-layer primacy   ← 5→6 layers (A7)
├── 8 primitive sectors         ← 8→9 sectors (A8)
├── 100% EP noncommutativity    ← CO/EO sidebands (A9)
├── S₂ transport isolation      ← frozen EO artifact (A8)
├── A_avg global commutativity  ← only Center commutes (B2)
├── NESS under uniform sampling ← coarse-graining artifact (B4)
└── Universal common eigenbasis ← EP noncommutativity (C1)
```

---

## What is NOT a Primary Object

The following are **secondary phenomenology** — derived from the six primary objects, not independent structures:

- Spectral layers {V₁, V₈/₉, V₇/₉, V₂/₃, V₅/₉, V₁/₃} — one node in L (D(A_18))
- Primitive sectors {S1,…,S9} — Center meet, also one node in L
- Phase automaton M_ij — derived from Object 5 + generator sampling [ARCHIVED]
- Entropy production — derived from M_ij [ARCHIVED]
- Controllability ranks G_i — derived from Object 5 [ARCHIVED]
- Curvature κ₁ channels — derived from Object 6
- Charge types O/A/B/AB/R — interpretive classification of transport patterns
- Persistence times τ_i — empirical from M_ij [ARCHIVED]
