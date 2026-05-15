# OPEN Algebraic Questions

**Date**: 2026-05-12
**Status**: POST-RHO-FIX. Tier 1 (paper-ready, corrected for 6 layers/9 sectors). Tier 2 (ALL CLOSED except B5). Tier 3 (dead, synced with ARTIFACT.md).

---

## Tier 1 — Paper-Ready ("unless disproven by theorem-level contradiction, 默认成立")

These are theorem-grade or exact-numerical. Already entered Paper I/II/III main text.

| Claim | Why closed | Paper |
|-------|-----------|-------|
| λ = 1−k/9, 6 canonical layers, block support | Face-sum averaging + inverse-closure + block algebra. k∈{0,1,2,3,4,6}, k=5 genuinely absent. [CORRECTED 2026-05-12: was 5 layers] | I |
| 9 primitive sectors from Center{A_18, QT_all, HT_all} | Joint diagonalization; 9→6 fusion relation verified. [CORRECTED 2026-05-12: was 8 sectors] | I |
| canonical ≠ primitive | 6-layer = symmetry-fused canonical; primitive = S₁,…,S₉ | I |
| Refinement semilattice L | Compatible decompositions, refinement relation, meet structure, Center minimum, commuting-core / noncommuting-boundary | I |
| EP-dominated noncommutativity: ‖[QTⁱ, QTʲ]‖=2.92 total: 93.9% in EP(144), 21.0% in CO(8), 27.1% in EO(12); CP exactly 0. [CORRECTED 2026-05-12: was "100% EP"] | cp=0, ep=2.74, co=0.61, eo=0.79 per block; CO/EO weak sidebands from perm@phase structure | II |
| Transport topology: S1(V₁) isolated, S6 primary hub (deg=5), S7 secondary (deg=3). 10 direct edges (9 Type I noncommutative + 1 Type II CP commutative permutation), all block-preserving. | Block-support overlap; M₂ incidence; CP permutation channel | II |
| κ symmetry: max‖κ_ij − κ_ji‖ ≈ 10⁻¹⁵ | No directed transport barrier | III |
| Lie accessibility: Class I (S1/V₁ only), Class II (gradient via κ₀), Class III (curvature via κ₁, within-block only) | Krawtchouk order mixing; all curvature block-preserving | III |
| T7: cross-block composition-only accessibility, 5 pairs | Lie preserves blocks; spectral sectors transverse blocks; minimal prototype S₃ at 9-dim | III |

**Status**: These are NOT "experimental observations" — they are structural consequences of the representation. No further discovery needed; formal writeup only. T7 now has a minimal prototype (S₃ at 9-dim) confirming it's a generic algebraic phenomenon, not Rubik-specific.

---

## Tier 2 — ALL CLOSED except B5 (Genuinely Open)

B1 (EP Algebra), B2 (Transport Category), B3 (Lie Hierarchy), B4 (Refinement Obstruction) are all CLOSED and promoted to Tier 1 / theorem docs. The only genuinely open item is B5 (Categorical Completion).

### B1 — EP Algebra Identification → CLOSED (2026-05-11)

**Status**: RESOLVED. The EP algebra is now a **characterized object**, not an open question.

**Definitive structure**:
- A_EP = ⟨Q₀, Q₁, Q₂⟩ ⊂ End(ℂ¹⁴⁴), dim = 20, closes at degree 3
- **Semisimple**: J(A) = {0}, trace pairing non-degenerate
- **Z(A) = 8**: from structure constant nullspace; ker(Killing) = Z(A) exactly
- **AW decomposition**: A ≅ **M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴** (unique 8-component solution, Σ n_i² = 4×4 + 4×1 = 20)
- **Killing signature**: (8+, 4−, 8 zero), degeneracy = Z(A)
- **Isotypic components on EP(144)**: 4×24 + 4×12 = 144
  - 4 M₂ (multiplicity 12): 3 active (‖[Q₀,Q₁]‖≠0), 1 trivialized (Q_i simultaneously scalarize)
  - 4 M₁ (multiplicity 12): spectator scalar sectors

**What this explains** (previously phenomenological claims, now structurally derived):
| Phenomenon | Algebraic origin |
|-----------|-----------------|
| EP-dominated noncommutativity | EP carries 3 active M₂ simple components (93.9%); CO/EO carry weak sidebands from perm@phase structure; CP is exactly commutative |
| Refinement only forms semilattice | M₂(ℂ) cannot be simultaneously diagonalized → no global common eigenbasis |
| Center commutative core | Z(A) ≅ ℂ⁸ — abelian subalgebra that refines globally |
| 8 primitive sectors = 8 central eigenvalues | Common eigenspaces of Z(A) on EP(144) = isotypic decomposition |
| 3-of-4 M₂ active | Q_i generators fail to span full M₂ on one component — a "blind spot" in the per-axis averaging basis |
| 12 dynamical directions | [A,A] dimension = 20 − 8 = 12; derives from 3 active M₂ (3×3=9) + other non-central directions |
| V₂/₃ unique primitive | Single sector where the active M₂ structures align to prevent splitting |

**What was wrong** (errata):
- "16 Hermitian + 4 nilpotent, A = S ⋉ N" — spurious signal from Gram-Schmidt on a non-*-aligned SVD basis
- "Non-semisimple, new exotic object" — incorrect; algebra is standard semisimple M₂⁴ ⊕ ℂ⁴
- "Radical dim = 4" — Killing nullspace = Z(A) = 8, not a nilpotent radical

**Remaining (lower priority)**:
- Explicit 2×2 matrices for Q_i in each M₂ component — optional
- ~~Map 8 EP isotypic components ↔ 8 primitive sectors~~ — DONE (2026-05-11), see 260511.md §EP Sector Correspondence

### B2 — Transport Category → **CLOSED 2026-05-11**

Full formalization: `260511_theorem_b2.md`.
- Transport Support Category T_S: objects, generating morphisms, composition — §B2.1
- Transport Selection Theorem (isotypic + primitive levels) — §B2.4.3, §B2.4.5
- Mediation-Curvature Decomposition Theorem — §B2.5.2
- Triple unification (refinement/transport/curvature = M₂) — §B2.5.5

### B3 — Lie Accessibility Hierarchy → **CLOSED 2026-05-11**

Absorbed into B2.5 (`260511_theorem_b2.md`).
- κ₀, κ₁, κ₂ at 8-sector primitive level: `test/canonical/_exp_transport_9sector.py` §9
- Mediation decomposes into curvature-mediated (within-block, κ₁>0) and path-mediated (cross-block, κ₁=0)
- S₀ truly frozen at ALL Lie depths (trivial representation)

### B5 — Categorical Completion (GENUINELY OPEN)

**Status (2026-05-12)**: Now grounded by T7 minimal mechanism. The decomposition mismatch obstruction (spectral sectors transverse to representation blocks) provides a concrete algebraic substrate for what was previously an abstract "categorical obstruction" language.

**WARNING — Language temptation zone.** The following are NOT verified and should NOT be claimed:

| NOT verified | Why it's premature |
|-------------|-------------------|
| Ext¹ obstruction class | Projector interleaving ≠ cohomology. The correct formulation: transport support graph is not transitively closed under composition. |
| Derived category interpretation | No derived functors, no triangulated structure identified |
| Frobenius algebra structure | Trace pairing exists on End(V_i) but the Frobenius property (nondegenerate bilinear form + coassociativity) has not been established for the transport Hom spaces |
| 2-category / bicategory | Only one level of morphism composition verified. No 2-morphism structure. |
| Lie-2 obstruction | Jacobi obstruction exists (numerical) but not categorically characterized |

**What IS verified (and safe to build on):**

1. **Transport support graph non-transitivity**: A_direct² strictly larger than A_direct. 11 mediation pairs vs 10 direct edges at 9-sector level. This is the correct language: "non-transitive support graph," NOT "Ext¹ obstruction."

2. **Projector interleaving**: P_α ρ(g) P_β ρ(h) P_γ ≠ P_α ρ(gh) P_γ. This is the obstruction — the projector P_β blocks the group multiplication. This is a concrete matrix fact, not an abstract cohomology class.

3. **Path category structure**: T_S is naturally a path category: objects = sectors, generating morphisms = T_αβ(g), Path₂(α,γ) = {T_αβ(g)∘T_βγ(h)}. Composition is string concatenation with projector interleaving.

**What would need to be proven (NOT to be claimed now):**

- Does the projector interleaving obstruction correspond to a 2-cocycle in some cohomology theory?
- Is Hom(α, β) a Frobenius algebra for the correct trace pairing?
- Does the transport category admit a derived completion?
- Is the Jacobi obstruction a Lie-2-algebra structure?

These are genuine research questions — they require new axioms, new computational verification, or both. They do NOT belong in theorem documents until verified.

---

## Tier 3 — Artifact Graveyard (Do Not Touch)

These are dead. Do not reinvestigate. See ARTIFACT.md for full failure records.

| Dead Claim | Failure Mechanism |
|-----------|-------------------|
| Onsager breaking / entropy production | Coarse-graining artifact; equilibrium under uniform sampling |
| Universal NESS | Detailed balance restored; current unstable; direction flips |
| One-way transport barriers | Broken logm artifact; κ_ij symmetric to 10⁻¹⁵ |
| Universal common eigenbasis | EP noncommutativity negates it |
| V₂/₃ freezing in continuous limit | Correct logm: κ₀(V₂/₃, V₅/₉) = 5.44 |
| Discrete-continuous singularity | Same artifact |
| Universal 5-layer primacy | canonical ≠ primitive |
| A_avg global commutativity | Only Center commutes |
| **5 canonical layers** (A7) | rho() CO/EO were diagonal-only (no permutation); ρ fix reveals 6 layers (k∈{0,1,2,3,4,6}) |
| **8 primitive sectors** (A8) | Same rho bug; diagonal CO/EO flattened structure → now 9 sectors |
| **100% EP-localized noncommutativity** (A9) | Diagonal CO/EO commute trivially; corrected ρ gives CO/EO sidebands (~6%) |
| **S₂ (EO) transport isolation** (A8) | Frozen EO made S₂ appear isolated; now degree=2, connected to S5,S6 |
| **T7 is Rubik-specific** (A10, implicit) | T7 now has minimal prototype at S₃ 9-dim — generic algebraic mechanism, not Rubik artifact |

---

## Computational (lower priority, blocked)

| # | Item | Status |
|---|------|--------|
| F1 | Full central idempotent basis (~99 isotypic components) | Blocked by memory |
| F2 | Isotypic-level transport tensor (~99×99) | Blocked by F1 |
| F3 | Multiplicity-fibre tracking | Open |

---

## Cross-Group Universality (direction, not active)

| # | Item |
|---|------|
| G1 | Prove star S₃ topology universal for face-symmetric, inverse-closed S |
| G2 | Minimal condition for non-trivial stratification in general (G, V, S) |

---

## Rules

1. **Tier 1 is PAPER-READY.** Formal writeup only; no more discovery.
2. **Tier 2 is CLOSED.** B1 (EP Algebra), B2 (Transport Category), B3 (Lie Hierarchy), B4 (Refinement Obstruction) all complete.
3. **Tier 3 is DEAD.** Do not reopen without a counterexample.
4. **B5 (Categorical Completion) is GENUINELY OPEN.** Language temptation zone — do NOT claim Ext¹, Frobenius, 2-category, derived, or Lie-2 without verification.
5. **Extract relations, then identify. Never guess algebra names first.**
6. **The correct formulation**: "transport support graph is not transitively closed" — NOT "Ext¹ obstruction." Projector interleaving, not cohomology.
