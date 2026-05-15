# VERIFIED Registry

**Date**: 2026-05-12
**Status**: **POST-RHO-FIX** — 2026-05-12: ρ(g) corrected to proper group homomorphism on CO/EO blocks (diag→permutation@phase). Three representation-dependent claims demoted (5→6 layers, 8→9 sectors, 100%→94% EP noncommutativity). Core structural claims (rational spectral law, A_EP, T7 discrete/continuous split) survive and are strengthened.

Claims that have been definitively verified. Organized by **invariant level** — the degree to which the claim is independent of generator choice, sampling, coarse-graining, normalization, and trajectory length.

**Central organizing object**: A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴ — all Level 0–1 claims derive from this single algebraic fact. **Stable under ρ correction** — EP block was already correct.

---

## Level 0 — Categorical Invariants

Independent of Rubik's cube specifics. These are structures that arise for **any family of averaging ensembles** on a finite group orbit.

| # | Claim | Signature | Verification |
|---|-------|-----------|-------------|
| C0.1 | **Refinement POSET exists** — D₁ ≤ D₂ ⇔ every projector of D₂ is a sum of projectors of D₁ ⇔ A_D₂ ∈ ⟨A_D₁⟩ | Exact projector overlap matrices = integer (0 or dim), never fractional | _exp_spectral_lattice.py: test_refinement_as_algebraic_inclusion |
| C0.2 | **Refinement requires commutativity** — D₁ ≤ D₂ ⇒ [A_D₁, A_D₂] = 0 | All 10 decompositions in L satisfy this | _exp_spectral_lattice.py, 260511.md §3 |
| C0.3 | **Commutative core C is a ∧-semilattice** — universal meet = Center{18, QT, HT}; joins do not always exist within C | Center(9) = 18-gen(6) ∧ QT(6) = QT(6) ∧ HTM(3) = 18-gen(6) ∧ HTM(3) | _exp_spectral_lattice.py: test_lattice_structure |
| C0.4 | **Noncommutative boundary** — per-axis decompositions on different axes are incompatible (cannot be placed in the same refinement hierarchy) | ‖[QT^0, QT^1]‖ = 2.74; physical analogue: L_x and L_y in angular momentum | _exp_primitive_sectors.py: TEST 2 |
| C0.5 | **Compatible family of decompositions** — across S, every D(A_S) is a coarsening or refinement of D(A_18); no rotation | Projector overlaps are exact integers, no continuous interpolation between decompositions | _exp_spectral_stability.py |
| C0.6 | **Transport bimodules** — T_ij(g) = P_i ρ(g) P_j form (End(V_i), End(V_j))-bimodules | End(V_i) are symmetric Frobenius *-algebras; Hom spaces have bounded dimensions | _exp_categorical_transport.py, 260511.md §5 |
| C0.7 | **Simultaneous measurability** − The Center {A_18, QT_all, HT_all} admits joint diagonalization because all three pairs commute | ‖[·,·]‖ < 10⁻¹⁵ for all three pairs | _exp_primitive_sectors.py: TEST 1 |
| C0.8 | **Transversal transport theorem** — Nontrivial cross-sector transport (K_ij > 0 for i≠j) emerges iff the averaging eigenspaces {P_i} are transverse to the isotypic decomposition of the full group algebra. Equivalently: [P_i, ρ(g)] ≠ 0 for some i,g. | S₃ regular rep: ⟨A_S⟩ = ℂ[S₃] → isotypic = irreducible → K_ij=0 ∀i≠j. Rubik: ⟨A_18⟩ is proper subalgebra → eigenspaces cut across irreducibles → K_ij > 0 | _exp_small_groups.py (S₃ control), _exp_averaging_algebra_minimal.py, _exp_ep_sector_correspondence.py |

---

## Level 1 — Group Algebra Invariants

Rubik's group specific but **generator-independent**. These are the representation fingerprint.

| # | Claim | Signature | Verification |
|---|-------|-----------|-------------|
| G1.1 | **6 spectral layers** — D(A_18) = {V₁(20), V₈/₉(2), V₇/₉(39), V₂/₃(26), V₅/₉(106), V₁/₃(35)} — [CORRECTED 2026-05-12: was 5 layers; ρ fix revealed λ=8/9 in EO block. k∈{0,1,2,3,4,6}, k=5 genuinely absent.] | Eigenvalues {1, 8/9, 7/9, 2/3, 5/9, 1/3}, dims sum 228 | CubieSpectralOperator._compute_spectral_layers(), all generator sets |
| G1.2 | **Block decomposition cp⊕ep⊕co⊕eo** — 64⊕144⊕8⊕12 = 228 | Exact projector decomposition, block sums verified | block_projectors() from spectralstructure.py |
| G1.3 | **cp = Q₃ Hamming scheme H(3,2)** — Bose-Mesner algebra ≅ Hecke algebra H(S₂≀S₃, S₃) | Krawtchouk eigenvalues k=0,1,2,3 → λ = 1−k/m for m=3 face types | Paper I §3.5, SpectralOrigin analysis |
| G1.4 | **ep = face-incidence commutative algebra** — 3-dim from JJ^T adjacency | Non-classical association scheme, 3 primitive idempotents | _exp_block_compatibility.py |
| G1.5 | **co = Z₃ phase cancellation** — ω+ω²+1=0 | 1-dim diagonal, coronal block | Paper I Lemma 4.1 |
| G1.6 | **eo = Z₂ phase split** — FB/non-FB classification | 2-dim diagonal, edge orientation | Paper I Lemma 4.0 |
| G1.7 | **EP-dominated noncommutativity** — ‖[QT^i, QT^j]‖ = 2.92 total: 93.9% in EP(144), 21.0% in CO(8), 27.1% in EO(12); CP exactly 0. [CORRECTED 2026-05-12: was "100% EP-localized"; ρ fix gives CO/EO permutation@phase structure → weak sidebands.] | cp=0, ep=2.74, co=0.61, eo=0.79 per block | _exp_primitive_sectors.py: TEST 2 |
| G1.8 | **Commutative center** {A_18, QT_all, HT_all} — all pairs commute | ‖[·,·]‖ < 10⁻¹⁵ | _exp_primitive_sectors.py: TEST 1 |
| G1.9 | **A_18 = (12 QT_all + 6 HT_all) / 18** — fundamental algebraic identity | Verified to machine precision: ‖A_18 − (12QT+6HT)/18‖ = 0 | _exp_primitive_sectors.py: TEST 3 |
| G1.10 | **9 primitive sectors** from Center{A_18, QT_all, HT_all} joint diagonalization [CORRECTED 2026-05-12: was 8 sectors; ρ fix reveals finer CO/EO structure] | S₁(20,cp+ep,k=0)…S₉(27,cp+co,k=6), dims sum 228 | center_decomposition() (updated), verified 2026-05-12 |
| G1.11 | **V₁ (S1, 20-dim) is the unique fully isolated primitive sector** — K=0, κ₀=0, κ₁=0 with ALL other 8 sectors. Truly G-invariant subrepresentation. [UPDATED 2026-05-12: was "V₂/₃ unique primitive"; 9-sector structure clarifies S1 as the unique isolated sector] | (λ_A=1, λ_QT=1, λ_HT=1), cp(8)+ep(12), no co/eo | verified 2026-05-12 |
| G1.12 | **Canonical ≠ Primitive** — V₁=20 vs S1+S2+...; V₇/₉=39 vs S3; V₂/₃=26 vs S4; V₅/₉=106 vs S5+S6+S7; V₁/₃=35 vs S8+S9. Every canonical layer except V₇/₉ and V₂/₃ resolves into multiple primitive sectors under the Center. [UPDATED 2026-05-12] | 6 canonical layers → 9 primitive sectors | center_decomposition() + _compute_spectral_layers() |
| G1.13 | **Transport star topology survives ρ fix** — S6(ep+eo, k=4, degree=5) is the hub; S7(mixed, k=4, degree=3) secondary hub; S1(V1) isolated. All 10 direct edges are block-preserving. Cross-block transport requires composition. [UPDATED 2026-05-12] | K_ij = max_g ‖P_i ρ(g) P_j‖_F, 9-sector level | verified 2026-05-12 |
| G1.14 | **Block-preserving direct transport** — all 10 direct edges share ≥1 block; 0 cross-block direct edges. Cross-block pairs require composition (length-2 paths). [UPDATED 2026-05-12] | 10 direct edges, all block-preserving; block-incidence from sector composition | verified 2026-05-12 |
| G1.15 | **κ_ij symmetry** — max|κ_ij − κ_ji| ≈ 10⁻¹⁵ | No directed transport barrier exists | _exp_lie_directed.py: test_kappa_symmetry |
| G1.16 | **ℤ-level integrality** — χ_λ(s) ∈ ℤ | Lemma 9.1: Bose-Mesner trace pairing | Paper I §9.1 |
| G1.17 | **Rational spectral law λ = 1−k/m** — from blockwise Bose-Mesner eigenvalue formula; symmetry-restricted, not universal (n=8, n=16 counterexamples) | k from Krawtchouk/adjacency eigenvalues; m from face-type count | Paper I Theorem 6.1, 6.4 |
| G1.18 | **Spectral origin closure** — 6 global eigenvalues = product merging of 4 block-level algebras; no global Gelfand pair; blockwise Hecke algebra. [CORRECTED 2026-05-12: was 5] | k-value resonance table: global λ ↔ block k-values | Paper I §3.5, §14 |
| G1.19 | **Generator-set universality of spectral layers** — same 6-layer structure across ALL inverse-closed S (verified 9 sets including n=3 single-face). [CORRECTED 2026-05-12: was 5 layers] | Number of layers may differ (±split/merge), but eigenspaces are same invariant subspaces | _exp_universality.py, _exp_structural_stability.py |
| G1.20 | **Weight perturbation breaks degeneracy** — 2% random weight perturbation splits 5-fold degeneracy into 25 distinct eigenvalues | Confirms eigenvalue coincidence depends on uniform averaging (symmetric group average) | _exp_structural_stability.py: Exp 6 |
| G1.21 | **EP algebra dimension** — dim⟨Q₀, Q₁, Q₂⟩ = 20 over ℂ, closes at degree 3 (13→20→20) | SVD iterative closure; ALL n×n basis pairs multiplied each iteration | canonical/_exp_ep_radical.py, archive/_exp_ep_algebra.py §7 |
| G1.22 | **EP algebra semisimple** — J(A_EP) = {0}, trace pairing Tr(ab) non-degenerate (condition number = 1.00) | Orthonormal SVD basis → Gram = I; no nilpotent ideal exists | _exp_ep_radical.py §1 |
| G1.23 | **EP algebra center** — Z(A_EP) = 8-dim; generic center element has 8 distinct eigenvalues on ℂ¹⁴⁴ | Structure constant nullspace: 12 non-zero SVs (=0.577), 8 zero SVs (<10⁻¹⁵) | _exp_ep_radical.py §2 |
| G1.24 | **EP algebra AW decomposition** — A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴ (unique 8-component solution, Σ n_i² = 4×4 + 4×1 = 20) | Center dim = 8 = number of simple components; only integer solution with 8 terms | _exp_ep_radical.py §5 |
| G1.25 | **EP algebra Killing form** — K(a,b) = Tr(ad(a)ad(b)), signature (8+, 4−, 8 zero), rank 12/20 | ker(K) = Z(A) verified to machine precision (‖proj_nonnull‖ < 10⁻¹⁵ for all z ∈ Z(A)) | _exp_ep_radical.py §3 |
| G1.26 | **EP isotypic decomposition** — 8 components on ℂ¹⁴⁴: 4×24 + 4×12 = 144 | Common eigenspaces of generic center element; M₂ components = dim 24 (multiplicity 12 each), M₁ components = dim 12 (multiplicity 12 each) | _exp_ep_radical.py §4 |
| G1.27 | **3 of 4 M₂ components active** — [Q₀, Q₁] ≠ 0 on 3 M₂ components, [Q₀, Q₁] = 0 on 1 M₂ component | Q_i generators simultaneously scalarize on one M₂ block — "trivialized noncommutative block" | _exp_ep_radical.py §7 |
| G1.28 | **Noncommutativity = M₂-dominated** — 93.9% from EP's M₂ simple components; CO/EO carry weak sidebands (‖[QT⁰,QT¹]‖_co=0.61, ‖[QT⁰,QT¹]‖_eo=0.79); CP is exactly commutative | EP is the dominant obstruction to global lattice completion; CO/EO are minor secondary obstructions | _exp_ep_radical.py §7, _exp_primitive_sectors.py |
| G1.29 | **Primitive sector ↔ isotypic mapping on EP** — 5 EP primitive sectors → 8 isotypic components; S₁|_EP→Iso2(M₁ iso), S₂→Iso1+Iso4+Iso5 (M₂+mix), S₄→Iso0+Iso3+Iso7 (3×M₁), S₅→Iso6 (pure M₂ act), S₆→Iso1+Iso4+Iso5 (same as S₂!) | Clean overlap matrix with exact integer overlaps (0 or 12); S₂/S₆ degenerate in Z(A_EP) | _exp_ep_sector_correspondence.py §3 |
| G1.30 | **S₂/S₆ Z(A_EP) degeneracy** — QT_all ∉ Z(A_EP) (projection residual = 4.24); S₂(λ_QT=5/6) and S₆(λ_QT=1/2) share identical isotypic decomposition {Iso1(12), Iso4(12), Iso5(12)} | QT_all distinguishes S₂/S₆ in Z(A_avg) but QT_all cannot be expressed as a linear combination of Z(A_EP) center elements | _exp_ep_sector_correspondence.py §8 |
| G1.31 | **Iso2 transport isolation** — S₁|_EP (12-dim, λ_18=1) has K=0 with ALL other isotypic components; complete transport decoupling | Analogous to V₁(24) for the full 228-dim space — the "solved state" component in EP | _exp_ep_sector_correspondence.py §5 |
| G1.32 | **Iso6 (V₂/₃) selective coupling** — K > 0 only with M₂ components (Iso1,4,5); K = 0 with all M₁ components (Iso0,2,3,7) | V₂/₃'s active M₂ core couples to other M₂ blocks but is transport-decoupled from M₁ scalar sectors | _exp_ep_sector_correspondence.py §5–6 |
| G1.33 | **Uniform multiplicity 12 — double commutant** — all 8 simple components appear with the same multiplicity 12 on EP(144); 4×24(M₂) + 4×12(M₁) = 144 | Suggests Comm(A_EP) ≅ M₁₂(ℂ)⁸ and representation structure V ⊗ W with A_EP acting on V and commutant on W ≅ ℂ¹² | _exp_ep_sector_correspondence.py §9, _exp_ep_radical.py §4 |
| G1.34 | **Double-commutant verified** — End_{Comm(A)}(EP) = A_EP, Comm(A) ≅ M₁₂(ℂ)⁸, dim(Comm(A)) = 1152 | Cross-component algebra action = 0; AW double-centralizer: M₂ comps → alg=4(M₂⊗1), M₁ comps → alg=1(scalar⊗1) | _exp_double_commutant.py |
| G1.35 | **4-level hierarchy frozen** — canonical(6) → center(9) → AW(8 isotypic) → Lie-active(3 M₂). [CORRECTED 2026-05-12: was 5→8] | S3/S6 Z(A_EP) degeneracy = canonical ≠ center; transport = M₂ block incidence; Lie accessibility = noncentral M₂ curvature | 260511_hierarchy.md |
| G1.36 | **Block-preserving direct transport** — all 10 direct edges share ≥1 block; no cross-block direct transport at primitive sector level. Transport preserves block type at Center resolution; cross-block reachability requires composition. [UPDATED 2026-05-12: 9-sector re-verification] | 10 direct edges, 0 cross-block | verified 2026-05-12 |
| G1.37 | **S₂ (EO, 2-dim, λ=8/9) is NOT transport-isolated** — K>0 with S5(eo) and S6(ep+eo). [CORRECTED 2026-05-12: old S₂ isolation was artifact of diagonal-only EO — the old "pure EO" sector was frozen.] | S2 degree=2, connects to S5(K=0.5) and S6(K=0.6) | verified 2026-05-12 |
| G1.38 | **Transport graph non-transitivity survives ρ fix** — 10 direct edges, 11 length-2 mediated pairs. Direct support ≠ categorical reachability; composition strictly enlarges accessibility. [UPDATED 2026-05-12] | 22 total reachable pairs; 11 require composition | verified 2026-05-12 |
| G1.39 | **S6 (ep+eo, k=4, degree=5) is the primary hub**; S7 (mixed, k=4, degree=3) secondary. Together they mediate all length-2 paths. The two k=4 EP-dominant sectors form the hub pair. [UPDATED 2026-05-12: was "V₅/₉ dual-hub" in 8-sector picture] | S6 degree=5, S7 degree=3, total mediation coverage = 11/11 pairs | verified 2026-05-12 |
| G1.40 | **T7: Discrete/Continuous Split survives ρ fix** — 5 cross-block pairs (S2↔S4, S3↔S9, S4↔S5, S4↔S8, S6↔S9) have K=0, κ₀=0, κ₁=0, yet are reachable via length-2 composition. Lie generators preserve block type; commutators cannot bridge CP↔EP, CO↔EO, etc. [NEW 2026-05-12 — stronger than before: no "buggy CO/EO" excuse] | 5 cross-block composition-only pairs, 0 cross-block κ₁>0 | verified 2026-05-12 |
| G1.41 | **Curvature is block-preserving** — all 6 pure curvature channels (κ₀≈0, κ₁>0) are within-block: ep↔ep or eo↔eo. Commutators [A_g, A_h] can create new channels within a block but cannot bridge blocks. [NEW 2026-05-12] | 6 curvature channels, all block-preserving | verified 2026-05-12 |
| G1.42 | **ρ is a group homomorphism on all blocks** — ρ(g)ρ(h)=ρ(gh) verified for CO/EO blocks after fix (was: diagonal-only, ρ broken). ‖ρ(g)ρ(h)−ρ(gh)‖ < 3×10⁻⁸ (complex64 precision). [NEW 2026-05-12] | Homomorphism property, unitarity, inverse all verified | test_representation, test_matrix_roundtrip |
| G1.43 | **T7 minimal system: S₃ nat(3)⊕reg(6), 9-dim** — 5 sectors (S5=hybrid bridge), 3 cross-block T7 pairs (S1↔S3, S2↔S3, S3↔S4). Block-diagonal ρ → A_g block-diagonal → [A_g, A_h] block-diagonal → no Lie cross-block. Hybrid S5 (nat:2+reg:2) enables discrete composition across blocks. [NEW 2026-05-12] | 9-dim, Center{A_full, A_trans}, eigenvalue resonance at λ=0 (standard irrep in both blocks) | test/canonical/_exp_minimal_t7.py Approach B/I |
| G1.44 | **T7 full hierarchy system: S₃ reg(6)⊕reg(6), 12-dim** — 10 sectors, 30 within-block gradient edges (κ₀>0), 10 within-block curvature pairs (κ₀=0,κ₁>0), 9 cross-block T7 pairs (K=κ₀=κ₁=0). PERFECT SEPARATION: curvature strictly block-preserving, T7 strictly cross-block. [NEW 2026-05-12] | 12-dim, Center{A₃, A₂}, 3 transposition gens | test/canonical/_exp_minimal_t7.py Approach A |
| G1.45 | **T7 = decomposition mismatch, not M₂** — T7 arises from spectral/projector decomposition being transverse to representation block decomposition, NOT from noncommutative simple components. M₂ ⇒ curvature; hybrid sector resonance ⇒ T7. Two distinct obstruction types. [NEW 2026-05-12] | 9-dim system has T7 but NO M₂ (no curvature). 12-dim system has BOTH, strictly separated. | test/canonical/_exp_minimal_t7.py |
| G1.46 | **Minimal T7 conditions** — (1) block-diagonal ρ with Lie closure preserving blocks; (2) cross-block eigenvalue resonance (shared irrep); (3) ≥2 commuting Center operators to split degeneracy into pure+hybrid sectors; (4) hybrid sector overlap graph enabling 2-step composition. S₃ (smallest non-abelian group) is sufficient. [NEW 2026-05-12] | Verified on 20+ systems; only S₃ with shared-irrep blocks works | test/canonical/_exp_minimal_t7.py |
| G1.47 | **N1 necessity — shared irrep is necessary for T7** (Center ⊂ ℂ[G]). Systematic search over abelian (Z₂×Z₂, Z₃, Z₄) and non-abelian (S₃ with disjoint irreps) groups: T7 tripartite (pure-A + hybrid + pure-B) never observed without shared irrep. "False T7" in S₃ std+(triv+sign) confirms: eigenvalue coincidence without shared irrep produces transport-inert spectral hybrids (has_path=False). Mechanism: Center acts as O_τ ⊗ I_{m_τ} per isotypic component — without shared irrep, eigenvalue matching is all-or-nothing, never partial splitting. Only shared irrep creates multiplicity-space hybrids that are transport-active bridges. [NEW 2026-05-13] | 5+ systems, 0 counterexamples; abelian + isotypic cases proved | test/canonical/_exp_abelian_t7.py |
| G1.48 | **Combinatorial commutant: full 228-dim = 610** — Comm(ρ(G)) dimension computed via index-pair orbit decomposition (BFS on 228² pairs under (i,j)→(π_g(i),π_g(j))). For monomial ρ(g) = D_g Π_g, the commutant constraint ρ(g)X = Xρ(g) reduces to orbit consistency of X entries with phase ratios. Each consistent orbit = one commutant basis matrix. 0.7s, exact to machine precision. [NEW 2026-05-14] | Self-consistent: Σ per-layer comm_dim = 966 > 610 (overcomplete projection) | rime/cubieoperator.py:_full_commutant_combinatorial |
| G1.49 | **51 isotypic components across 6 spectral layers** — from Center(Comm_G(V_λ)) joint diagonalization within each layer. V₁: 1D×20 (1), V₈/₉: 2D×1 (1), V₇/₉: 3D×1 ×13 (13), V₂/₃: 2D×1 ×13 (13), V₅/₉: 6D×1×10 + 7D×1 + 3D×1 + **3D×11** + 3D×1 (14), V₁/₃: 4D×1×8 + 3D×1 (9). Total 59 irreducible summands (copies). [UPDATED 2026-05-15: was 12 components from coarser pre-center-idempotent method] | 51 ≠ 9 observable-algebra sectors — different objects (representation-theoretic atom ≠ observable-algebra atom). Per-layer commutant sum 966 > full-space 610 (overcomplete). | test/canonical/_exp_isotypic_decomposition.py |
| G1.50 | **Isotypic transport confirms sector-level topology** — 51×51 isotypic transport tensor: 619 nonzero connections, all block-preserving. No new topological features beyond 9-sector resolution. The null result is the result: finer representation-theoretic resolution adds no new transport topology. [UPDATED 2026-05-15: was 12×12 with 28 nonzero] | Consistent with 9-sector transport graph (10 direct edges, all block-preserving) | test/canonical/_exp_isotypic_decomposition.py |
| G1.51 | **Representation is almost multiplicity-free** — 50 of 51 isotypic components have multiplicity m=1. Only V₅/₉ d=3×11 has m>1. The unique multiplicity reservoir. [NEW 2026-05-15] | m=1:50, m=11:1; stark histogram confirms near-total absence of internal multiplicity structure | test/canonical/_exp_isotypic_decomposition.py, figures/f3_multiplicity_histogram.png |
| G1.52 | **Multiplicity reservoir** — V₅/₉^(3,11): 11×11 multiplicity transfer matrix, eff_rank=11, entropy=2.18, isotropy=0.74. Non-Schur intra-isotypic copy coupling (ortho_max=0.6) — copies are dynamically coupled, not algebraically decoupled. Transport complexity concentrates into this single reservoir. [NEW 2026-05-15] | Full-rank multiplicity transfer; all 11 copies independently active; smooth SV decay 2.21→0.39 | test/canonical/_exp_isotypic_decomposition.py, figures/f3_reservoir_svd.png |

---

## Level 2 — Generator-Conditioned Invariants

Depend on which generators are activated but are **robust** — not sampling artifacts, not trajectory-length dependent.

| # | Claim | Signature | Verification |
|---|-------|-----------|-------------|
| S2.1 | **Lie closure hierarchy exists** — three accessibility classes at gradient order: I (subrep-isolated: V₁ only), II (gradient-coupled: V₅/₉ hub, V₁/₃), III (curvature-coupled: V₇/₉↔V₂/₃) | Class I: P₁ A_g P_j = 0 ∀g,j≠1; Class II: κ₀(V₅/₉,·) > 0, κ₀(V₁/₃,V₅/₉)=6.28; Class III: κ₀≈10⁻¹⁴, κ₁=4.27 | _exp_closure_pass.py, kappa_depth(0), kappa_depth(1) |
| S2.1a | **V₁/₃ is gradient-coupled to V₅/₉** — κ₀(V₁/₃, V₅/₉) = 6.28, not Class I (corrected 2026-05-11) | Isotypically pure does NOT guarantee Lie isolation — cp-only sectors can couple through A_g | _exp_closure_pass.py: R4 diagnostic |
| S2.2 | **κ₀(V₅/₉, V₂/₃) = 5.44** — substantial gradient coupling | Symmetric both directions, verified via scipy.linalg.logm (expm fidelity 10⁻¹⁵) | _exp_lie_directed.py, infinitesimal_transport() |
| S2.3 | **κ₀(V₇/₉, V₂/₃) ≈ 10⁻¹⁴** — gradient-decoupled (Krawtchouk order orthogonality) | Individual A_g preserve Krawtchouk order; k=2 vs k=3 orthogonal | kappa_depth(0), _exp_lie_closure_transport.py |
| S2.4 | **κ₁(V₇/₉, V₂/₃) = 4.27** — curvature-coupled (commutators mix Krawtchouk orders) | Enhancement ratio κ₁/κ₀ ~ 10¹⁴ — largest depth-gated channel in the system | kappa_depth(1), _exp_lie_closure_transport.py |
| S2.5 | **κ₂(V₇/₉, V₂/₃) = 13.4** — nested commutators amplify | κ depth hierarchy: 10⁻¹⁴ → 4.27 → 13.4 | kappa_depth(2), _exp_lie_closure_transport.py |
| S2.6 | **Lie depth accessibility is symmetric** — κ_d matrix symmetric at all depths (max asymmetry ~10⁻¹⁵) | No directed accessibility at any Lie depth | _exp_lie_closure_transport.py |
| S2.7 | **expm(A_g) = ρ(g) at ε=1** — fidelity ~10⁻¹⁵ for all 18 generators | Correct logm produces exact Lie group embedding; earlier cycle-decomposition log was wrong | compute_lie_generators(), _exp_lie_directed.py: test_lie_vs_discrete_amplitude |
| S2.8 | **No discrete-continuous transport annihilation** — κ₀ > 0 wherever K > 0 | All discrete transport channels persist at gradient Lie order | _exp_lie_directed.py |
| S2.9 | **Jacobi obstruction** — mean ‖[A,[B,C]] + [B,[C,A]] + [C,[A,B]]‖ ≈ 47 (full), ≈ 7.9 (projected) | Structure is a Lie 2-algebra, not a strict Lie algebra | _exp_lie_closure.py |
| S2.10 | **Controllability rank signature** — rank(G_i) varies by phase: 18/18(V₅/₉) → 7/18(V₂/₃) | Each spectral sector inherits different generator responsiveness from blockwise structure | _exp_controllability.py |
| S2.11 | **Effective equilibrium under uniform sampling** — Ṡ ≈ 2×10⁻⁶ per step, all edge currents within noise | No NESS; transport is effectively undirected at equilibrium | _exp_nonequilibrium_transport.py |
| S2.12 | **Small groups have diagonal transport** — Q₃, S₄, S₃⊗S₃, S₃ regular: K_ij=0 for i≠j | A-eigenspaces are subrepresentations when no cross-block eigenvalue resonance exists | _exp_small_groups.py |

---

## Level 3 — Structural Closures

Problems that were previously OPEN and are now definitively resolved.

| # | Closure | Resolution |
|---|---------|-----------|
| CL1 | **Spectral origin** — why 6 layers? | Product structure: C[A] ⊂ A_Q3 × A_JJT × A_Z3 × A_Z2, with resonance merging across blocks. Blockwise Bose-Mesner/Hecke algebras, not a single global algebra. k∈{0,1,2,3,4,6}, k=5 genuinely absent. [CORRECTED 2026-05-12: was 5 layers, k=1 now filled by EO block] (Paper I §3.5, §14) |
| CL2 | **Induced/permutation reconstruction** | ‖χ_perm − χ_A‖ ≠ 0 — A is not a pure permutation character. Induced model consistent with doubly transitive action (⟨χ_perm, χ_perm⟩ ≈ 2). (Paper II §6.6) |
| CL3 | **Transport selection rule** | T_ij ≠ 0 ⇔ P_i and P_j share non-orthogonal primitive components within the same block. V₇/₉↔V₂/₃ decoupling = orthogonal Krawtchouk eigenspaces. (Paper II) |
| CL4 | **Spectral-vs-isotypic transversality** | Gap Δ_comm = 1052 − 628 = 424 = 2 Σ‖T_ij‖². Quantitative measure of ‖[P_i, ρ]‖. (Paper II) |
| CL5 | **ℤ-level integrality (P1)** | Closed. Lemma 9.1: Bose-Mesner trace pairing → character values are ℤ-valued. (Paper I §9.1) |
| CL6 | **λ=2/3 boundary (P3)** | Corrected: co-block support cutoff (Lemma 4.1), not G₁-invariance. (Paper I) |
| CL7 | **EP Algebra Identification (Gap B)** | A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴. Semisimple, Z(A)=8, AW decomposition complete. "Non-semisimple S ⋉ N" was spurious (Gram-Schmidt artifact). Noncommutativity derives entirely from 3 active M₂ blocks. (2026-05-11) |
| CL8 | **Algebra × Spectral Lattice connection (Q1-Q4)** | 8 primitive sectors ↔ 8 isotypic components fully mapped. S₂/S₆ degeneracy explained (QT_all ∉ Z(A_EP)). Transport = semisimple block incidence. Lie accessibility = M₂ curvature. Double-commutant ≅ M₁₂(ℂ)⁸. (2026-05-11) |
| CL9 | **Refinement Obstruction = M₂** — noncommutative simple components (M₂) are the sole obstructions preventing the refinement lattice from being globally completable. Refinement failure = noncommutative curvature. Triple unification: M₂ obstructs refinement, carries transport, generates Lie curvature. | Per-axis QT decompositions are pairwise incomparable; obstruction 100% localized in 3 active M₂ EP components. Commutative blocks (cp/co/eo, pure M₁) permit unrestricted refinement. Theorem B4.3 in `260511_theorem_b.md`. (2026-05-11) |

---

## Verification Protocols

Each VERIFIED claim is backed by at least one of:

| Protocol | Tool | Invariant Level |
|----------|------|----------------|
| **Exact algebraic identity** — SVD zero, norm equality, projector overlap = integer | CubieSpectralOperator, numpy.linalg | Level 0, 1 |
| **Machine-precision numerical** — tolerance < 10⁻¹⁰ for matrix operations (228×228 scale) | scipy.linalg.logm, expm, eigh | Level 1, 2 |
| **Cross-generator-set stability** — confirmed across 9+ inverse-closed generator families | _exp_universality.py, _exp_structural_stability.py | Level 1 |
| **Small-group control** — confirmed on Q₃, S₄, S₃⊗S₃, S₃ regular | _exp_small_groups.py | Level 1 |
| **Robust numerical** — reproducible across random seeds, parameter ranges | All _exp_*.py files | Level 2 |

---

## Rules

1. **New claims must pass cross-generator-set stability before Level 1 registration.** Anything that holds only for the 18-gen set is Level 2 unless proven otherwise.
2. **Level 3 (phenomenology) entries are NOT registered here.** Entropy production rates, phase automaton transition probabilities, metastability durations — these are coarse-grained shadows, not invariants.
3. **A claim stays VERIFIED until a counterexample is found.** When a counterexample is found, move the claim to ARTIFACT.md with the failure reason.
4. **No claim may be added without a specific verification protocol and invariant level assignment.**
