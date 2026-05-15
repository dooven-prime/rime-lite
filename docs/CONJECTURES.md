# CONJECTURES — Structural Propositions

**Date**: 2026-05-12
**Status**: RESTRUCTURED — Three types: I (falsified, → ARTIFACT), II (presentation-dependent, empirical at current resolution), III (mechanism-level, genuinely open).

> **Conjecture = still plausible but unproven.** NOT "something we once guessed." Falsified historical hypotheses belong in ARTIFACT.md, not here.

---

## Type III — Mechanism-Level Conjectures (GENUINELY IMPORTANT)

These do NOT depend on exact layer count, sector count, λ values, or Rubik geometry. They are structural propositions about the mechanism. Survive ρ-fix, survive sector renaming, survive resolution changes.

### C.1 — Refinement Incompleteness from Noncommutative Simple Components

**Statement**: In the refinement POSET of averaging algebras, the non-existence of joins (lattice incompleteness) is a consequence of noncommutative simple components (M_{n>1}) in the AW decomposition. Specifically: per-axis decompositions are pairwise incomparable because their generating operators have non-zero commutator, which is carried entirely by M₂ components. Commutative blocks (pure M₁) permit unrestricted refinement; M₂ blocks obstruct it.

**Evidence**: Rubik's cube EP block (A_EP ≅ M₂⁴⊕M₁⁴): 3 active M₂ → per-axis QT decompositions pairwise incomparable. CP block (purely commutative): all Krawtchouk refinements compatible. S₃ reg⊕reg (12-dim): M₂ curvature pairs are strictly within-block; refinement obstruction localizes to M₂ components.

**What would disprove it**: A system with M₂ components where per-axis decompositions from noncommuting operators are nevertheless refinable (common eigenbasis exists).

**Significance**: If true, "refinement failure = noncommutative curvature" is a general theorem, not a Rubik observation.

### C.2 — Hybrid-Sector-Mediated Composition-Only Accessibility (T7)

**Statement**: T7 — cross-block composition-only accessibility — arises whenever three structural conditions hold: (C1) shared noncommutative isotypic support across blocks (bridgeability), (C2) a hybrid projector P_γ spanning both blocks (composition path), (C3) block-diagonal ρ(g) making all Lie operations block-preserving (Lie inaccessibility). This is a decomposition mismatch phenomenon: spectral sectors transverse to representation blocks, the projector interleaving P_α ρ(g) P_γ ρ(h) P_β bridges what no single ρ(g) or Lie monomial can.

**Evidence**: Rubik's cube (228-dim): 4 cross-block T7 pairs. S₃ nat⊕reg (9-dim): 3 T7 pairs, zero curvature — pure decomposition mismatch. S₃ reg⊕reg (12-dim): 9 T7 pairs (all cross-block) perfectly separated from 10 curvature pairs (all within-block). NOT a single counterexample.

**What would disprove it**: A block-diagonal system where κ₁ > 0 for a cross-block pair, or T7 exists for a within-block pair.

**Significance**: If true, this is a new obstruction type distinct from M₂ — "infinitesimalization forgets projector history." The continuous limit preserves intra-block propagation but collapses cross-block hybrid mediation chains.

### C.3 — Support-Overlap Transport Principle

**Statement**: In any averaging algebra framework, transport between spectral sectors (K_αβ > 0) is governed by support overlap: two sectors can be directly coupled by generators iff they share non-orthogonal support within some simple component of the averaging algebra. M₁ components are transport spectators unless coupled through an M₂ bridge.

**Evidence**: Rubik's cube: S1 (Iso2, M₁ spectator) has K=0 with ALL other sectors. S4 (V₂/₃, pure Iso6/M₂) couples only to M₂ components. Iso1 (trivialized M₂) is the universal bridge. S₃ systems show same pattern: pure-block sectors couple to hybrid, hybrid couples to everything.

**What would disprove it**: K > 0 between two sectors with disjoint support across all simple components (no shared M₂, no shared commutative block structure).

**Significance**: If true, transport topology is computable from AW decomposition alone — no group structure needed beyond the averaging algebra.

### C.4 — Hub = Maximal Noncommutative Support Intersection

**Statement**: Transport hubs (sectors with maximal degree in the transport graph) are exactly the sectors whose noncommutative support profile spans the maximal set of active M₂ components. The hub is a support-theoretic property, not a graph-theoretic one.

**Evidence**: Rubik's cube: S6 (ep+eo, deg=5) and S7 (mixed, deg=4) span all 3 active M₂ between them. S₃ reg⊕reg: S10 (hybrid, spans both blocks) mediates all 9 T7 pairs. S₃ nat⊕reg: S5 (hybrid) mediates all 3 T7 pairs.

**What would disprove it**: A sector with maximal transport degree whose Supp_nc is a strict subset of some lower-degree sector's Supp_nc.

**Significance**: If true, hub identification is algebraic, not empirical — read off from AW decomposition support profiles.

### C.5 — Finite Lie Depth Saturation

**Statement**: For any finite-dimensional representation, the κ_d accessibility hierarchy saturates at finite depth: there exists d_max such that κ_d(i,j) = κ_{d_max}(i,j) for all d ≥ d_max. The Lie algebra generated by {A_g} has finite solvability length on spectral projectors.

**Evidence**: Rubik's cube: κ₀ → κ₁ → κ₂ for Class III: 10⁻¹⁴ → 4.27 → 13.4, growth slowing. Finite dimensionality of End(V) = 228² bounds the structure.

**What would disprove it**: κ_d continuing to grow without bound, or new sector pairs becoming coupled at arbitrarily high d.

### C.6 — Refinement POSET Universality

**Statement**: For ANY finite group G, unitary representation ρ, and family of inverse-closed generator subsets {S_α}, the averaging operators {A_{S_α}} induce spectral decompositions forming a refinement POSET under algebraic inclusion. The commutative sub-POSET is always a ∧-semilattice.

**Evidence**: Verified on Rubik's cube (10 decompositions). S₃ systems confirm the pattern at small scale. Underlying math (commutative subalgebras → refinement) is general.

**What would disprove it**: Two decompositions with fractional projector overlaps (rotated eigenspaces) from inverse-closed generator subsets on the same representation.

---

## Type II — Presentation-Dependent Empirical Structure

These are structural facts at the CURRENT resolution (9 primitive sectors from Center{A_18, QT_all, HT_all}). They may change if the Center definition changes, but are robust within the current framework.

### E.1 — 9-Sector Transport Topology

**Under the current 9-sector Center decomposition:**

- S1 (V₁, 20-dim, cp+ep) is completely transport-isolated: K=κ₀=κ₁=0 with ALL other 8 sectors
- S6 (ep+eo, k=4, deg=5) is the primary hub; S7 (mixed, k=4, deg=4) secondary
- 11 direct edges, ALL block-preserving (0 cross-block)
- 4 cross-block pairs (S2↔S4, S3↔S9, S4↔S8, S6↔S9) reachable only via length-2 composition

**Stability**: The HUB STRUCTURE (S6 primary, S7 secondary) and the ISOLATION of S1 survive across generator sets. The exact edge count and degree values are S-conditioned. Cross-block freezing (0 direct edges) is robust.

### E.2 — 9-Sector Curvature Structure

- 6 pure curvature channels (κ₀≈0, κ₁>0), ALL within-block (ep↔ep or eo↔eo)
- 0 cross-block curvature channels
- Curvature is strictly block-preserving at the 9-sector Center resolution

**Stability**: Block-preservation of κ₁ is a structural consequence of block-diagonal ρ. The exact channel count depends on sector granularity but the block-preserving property is resolution-stable.

### E.3 — 6-Layer Canonical Structure

- λ = 1−k/9, k∈{0,1,2,3,4,6}, 6 layers
- k=5 (λ=4/9) genuinely absent
- k=1 (λ=8/9, V₈/₉, 2-dim, pure eo) was masked by diagonal-only CO/EO ρ (ARTIFACT A7)

**Stability**: The rational form λ=1−k/9 is proved (Bose-Mesner trace pairing). The k-set {0,1,2,3,4,6} is representation-dependent but empirically stable. k=5 absence is explained by block algebra structure.

### E.4 — Noncommutativity Hierarchy

- ‖[QT⁰, QT¹]‖_F = 2.92 total
- Per block: cp=0 (exact), ep=2.74 (93.9%), co=0.61 (21.0%), eo=0.79 (27.1%)
- EP-dominant, not EP-exclusive

**Stability**: The hierarchy (EP ≫ CO ≈ EO ≫ CP = 0) is ρ-stable. Exact percentages are S-conditioned but the dominance order is representation-stable.

---

## Type I — Falsified (Historical Hypotheses)

These are NOT conjectures. They were once guessed, then disproven. Preserved here for reference only. Full failure records in ARTIFACT.md.

| # | Historical Hypothesis | Failure | Date |
|---|----------------------|---------|------|
| H1 | EP Algebra ≅ Hecke H(S₂≀S₃, S₃) or BMW/TL | A_EP ≅ M₂⁴⊕M₁⁴, standard semisimple, braid fails | 2026-05-11 |
| H2 | 8 primitive sectors from Center | ρ-fix → 9 sectors (CO/EO were diagonal-only, ARTIFACT A8) | 2026-05-12 |
| H3 | 5-layer transport star S₃ topology | ρ-fix → 6 layers (λ=8/9 in EO, ARTIFACT A7) | 2026-05-12 |
| H4 | 100% EP-localized noncommutativity | CO/EO carry weak sidebands (ARTIFACT A9) | 2026-05-12 |
| H5 | S₂ (EO) is transport-isolated | Frozen EO artifact; S2 now degree=2 | 2026-05-12 |
| H6 | T7 is Rubik-specific / requires 228-dim | Minimal prototype: S₃ at 9-dim | 2026-05-12 |
| H7 | M₂ ⇒ T7 | S₃ nat⊕reg (9-dim) has T7 but zero curvature (no M₂). M₂ is NEITHER necessary NOR sufficient for T7. | 2026-05-12 |
| H8 | V₁/₃ is Class I (Lie-isolated) | κ₀(V₁/₃, V₅/₉) = 6.28 | 2026-05-11 |
| H9 | 5 spectral layers are primitive | Only V₈/₉ and V₂/₃ are single-sector canonical layers | 2026-05-11 |
| H10 | A_avg is globally commutative | Only Center{A_18, QT_all, HT_all} commutes | 2026-05-11 |

---

## Rules

1. **Type III conjectures** are the only ones worth proving. They are mechanism-level and resolution-independent.
2. **Type II empirical structures** should be presented as "at the current Center resolution" — never as universal theorems.
3. **Type I falsified hypotheses** belong in ARTIFACT.md. They appear here only as a quick-reference index.
4. **Before proposing a new conjecture**, check: does it depend on 8 vs 9 sectors? 5 vs 6 layers? If yes, it's Type II, not Type III.
5. **A conjecture graduates to VERIFIED when**: (a) the mechanism is proven at the algebraic level, AND (b) it survives at least one resolution change or minimal prototype reduction.
