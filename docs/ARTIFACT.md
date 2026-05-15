# ARTIFACT Graveyard

**Date**: 2026-05-11
**Status**: LIVING DOCUMENT — add new failures here, never delete

> **Purpose**: Prevent artifact resurrection. Every claim that was once believed and later disproven goes here, with the exact failure mechanism. Before making any new claim, check this file. If your claim resembles something here, verify it is not the same artifact.

---

## ⛝ Level 1 — Computational Artifacts

Claims disproven by fixing a computation. The most dangerous class — easy to resurrect if code regresses.

| # | Claim | Date Believed | Failure Mechanism | Corrected Value |
|---|-------|--------------|-------------------|-----------------|
| A1 | **One-way barrier V₂/₃ → V₅/₉** — "Lie flow cannot transfer from V2/3 to V5/9" | 2026-05-08 to 2026-05-09 | **Broken cycle-decomposition logm with `.real` truncation** in `compute_lie_generators`. The truncated A_g spuriously showed P_{5/9} A_g P_{2/3} = 0. Correct `scipy.linalg.logm` gives κ₀ = 5.44 both ways. | κ_ij symmetric to 10⁻¹⁵ |
| A2 | **Discrete-continuous singular pairs** — "κ_ij = 0 but K_ij > 0 for some (i,j)" | 2026-05-08 to 2026-05-09 | Same broken logm as A1. Correct logm: **no** κ_ij = 0 where K_ij > 0. All discrete transport channels persist at gradient Lie order. | All K_ij > 0 ⇒ κ₀_ij > 0 |
| A3 | **V₂/₃ "freezing" in continuous Lie limit** — "V2/3 is a sink/ratchet under Lie flow" | 2026-05-08 to 2026-05-09 | Consequences of A1+A2. With correct logm, V₂/₃↔V₅/₉ actively coupled (κ₀=5.44). The genuine fact is that V₂/₃ is the unique primitive 18-gen layer — NOT that it freezes. | V₂/₃ is actively coupled |
| A4 | **"Reach_L ⊊ Reach_G"** — "Lie reachable set is a strict subset of discrete reachable set" | 2026-05-08 to 2026-05-09 | Direct consequence of A2 — false premise that κ = 0 for some transport channels. Correct L4 does not lose channels; it reveals a depth hierarchy. | L4 is richer, not poorer |
| A5 | **"Rank(g_{2/3}) = 0/18"** — "V2/3 infinitesimal controllability rank is zero" | 2026-05-08 to 2026-05-09 | Consequence of A1 — g_i computed from broken A_g. Correct g_i has non-zero rank matching G_i structure. | rank(g_{2/3}) > 0 |
| A6 | **"Structure-selective collapse"** — "logarithm annihilates primitive idempotents" | 2026-05-08 to 2026-05-09 | Consequence of A1+A2. logm does NOT selectively annihilate; the genuine phenomenon is curvature-mediated coupling (creation of new channels by commutators, not destruction by log). | Curvature-mediated emergence |
| A7 | **"5 canonical layers"** — λ∈{1,7/9,2/3,5/9,1/3}, exactly 5 A_18 eigenspaces | 2026-05-08 to 2026-05-12 | **rho() was not a group homomorphism on CO/EO.** CO/EO blocks used `diag(ω^delta)` (diagonal-only, no permutation). This "frozen gauge phase decoration" masked the true orientation representation. Correct `rho_co[new,old]=ω^{delta[old]}` (permutation@phase) reveals λ=8/9 (k=1) in EO block. | λ=1−k/9 with k∈{0,1,2,3,4,6}: **6 layers**. k=5 (λ=4/9) genuinely absent. |
| A8 | **"8 primitive sectors"** from Center{A_18, QT_all, HT_all} joint diagonalization | 2026-05-09 to 2026-05-12 | Same rho() bug as A7. The diagonal-only CO/EO flattened internal structure, producing exactly 8 sectors. With correct permutation@phase CO/EO, the Center resolves **9 sectors** — the additional structure comes from CO/EO's genuine permutation+phase interaction. | 9 primitive sectors |
| A9 | **"100% EP-localized noncommutativity"** — ‖[QT^i, QT^j]‖ = 2.74 completely confined to EP(144), CO=EO=0 exactly | 2026-05-09 to 2026-05-12 | Same rho() bug as A7. Diagonal-only CO/EO trivially commute because diagonal matrices always commute. Correct permutation@phase CO/EO carry genuine cross-axis noncommutativity: ‖[QT⁰,QT¹]‖_co=0.61, ‖[QT⁰,QT¹]‖_eo=0.79. | EP-dominated (~94%), CO/EO weak sidebands (~6%). Hierarchy exists. |

---

## ⛝ Level 2 — Conceptual Overstatements

Claims that contained a kernel of truth but were framed too strongly.

| # | Claim | Date Believed | Failure Mechanism | What Remains True |
|---|-------|--------------|-------------------|-------------------|
| B1 | **"Five spectral layers are primitive"** | 2026-05-01 to 2026-05-11 | V₁ splits into 3 primitive sectors: cp(8)+ep(12)+eo(4); V₇/₉ = S₂+S₃; V₅/₉ = S₄+S₆; V₁/₃ = S₇+S₈. **Only V₂/₃ is both canonical AND primitive.** The 5-layer decomposition is the fused view under full cubic symmetry. | 5 layers correct for D(A_18); they're just not primitive |
| B2 | **"A_avg is commutative"** | 2026-05-01 to 2026-05-11 | Only the **center** {QT_all, HT_all, A_18} is commutative. Per-axis operators QT^i do NOT commute across axes (‖[QT^i, QT^j]‖ = 2.74). ~~Noncommutativity 100% in EP~~ — corrected 2026-05-12: CO/EO carry weak sidebands (‖[QT⁰,QT¹]‖_co=0.61, ‖[QT⁰,QT¹]‖_eo=0.79) due to A7-A9. | Center is commutative; boundary is noncommutative with EP-dominant hierarchy |
| B3 | **"8 sectors from per-axis QT eigenspaces"** | 2026-05-09 to 2026-05-11 | Per-axis QT^i on different axes don't commute → no simultaneous diagonalization. 8 sectors come from **Center{A_18, QT_all, HT_all}** — the global cubic-symmetric operators. | 8 sectors correct; their origin is Center, not per-axis |
| B4 | **"Non-equilibrium steady state"** | 2026-05-08 to 2026-05-10 | Under uniform 18-gen sampling, the system is effectively at equilibrium: Ṡ ≈ 2×10⁻⁶ per step, all edge currents within noise. The earlier NESS signature was from biased generator sampling. | Transport graph topology supports both equilibrium and non-equilibrium regimes depending on S |
| B5 | **"Continuous limit annihilates transport channels"** | 2026-05-08 to 2026-05-09 | Covered by A1-A3. The genuine phenomenon is that the continuous limit **organizes** transport by Lie-algebraic depth — it does not annihilate. | Lie depth hierarchy (Classes I/II/III) |
| B6 | **"Transport subspace T is Frobenius algebra"** | 2026-05-08 to 2026-05-11 | T = span{P_i ρ(g) P_j} is NOT multiplicatively closed. The closure T̄ ⊂ ρ(C[G]) is. Individual End(V_i) ARE symmetric Frobenius *-algebras, but the full transport space is not. | End(V_i) ARE Frobenius; T is a bimodule, not an algebra |

---

## ⛝ Level 3 — Premature Theoretical Identifications

Claims that were "this must be X" before sufficient evidence.

| # | Claim | Date Believed | Failure Mechanism | What to Do Instead |
|---|-------|--------------|-------------------|-------------------|
| C1 | **"Universal common eigenbasis across all S"** | 2026-05-09 to 2026-05-11 | Ignored EP noncommutativity. Per-axis QT on different axes don't commute — their eigenspaces are **incompatible** (rotated relative to each other). No single basis diagonalizes all A_S simultaneously. | Use the refinement lattice L; accept that different S give compatible but not identical decompositions |
| C2 | **"Onsager entropy production breaking"** | 2026-05-10 | Coarse-graining noise. When you project 228D → 5D, apparent cycle currents can emerge from coarse-graining artifacts, not from genuine non-equilibrium fluxes. The full 228D dynamics is effectively equilibrium under uniform sampling. | Always verify NESS claims at the full 228D level before interpreting projected (5D) currents |
| C3 | **"This must be Temperley-Lieb"** or **"This must be BMW"** | Ongoing risk | EP noncommutativity structure has NOT been identified yet. Relations {Q_i Q_j Q_i, [Q_i, Q_j], Q_i², (Q_i Q_j)^k} need to be extracted first. Candidate algebras: Hecke H(S₂≀S₃, S₃), Temperley-Lieb, BMW, Brauer, partition algebra. | Extract relations first, then compare. See OPEN.md §B. |

---

## ⛝ Level 4 — False Numerical "Confirmations"

Results that appeared to confirm a theoretical prediction but were actually artifacts.

| # | "Confirmation" | What It Seemed to Show | Actual Cause |
|---|---------------|----------------------|--------------|
| D1 | **V₂/₃ retention = 1.0000 under Lie flow** (Exp 1, `_exp_spectral_barrier.py`) | "V2/3 amplitude is perfectly conserved — spectral superselection barrier" | The A_g used in Exp 1 were from broken logm (A1). With correct logm, V₂/₃ amplitude is NOT conserved — it actively couples to V₅/₉. The 1.0000 retention was measuring the broken generator's inability to couple, not a genuine algebraic obstruction. |
| D2 | **Lie crossing prob ~0.2% vs discrete ~10.6%** (Exp 2, `_exp_spectral_barrier.py`) | "50x suppression — discrete-continuous singularity" | Same broken A_g (A1). Correct result: Lie and discrete crossing probabilities should be comparable (both use correct ρ(g) structure). |
| D3 | **"V₂/₃ persists at low T because discrete channel stays open"** (Exp 3) | "Experimental signature of discrete-continuous singularity" | The persistence is real but the interpretation was wrong. V₂/₃ persists because the V₅/₉↔V₂/₃ gradient channel (κ₀=5.44) is active in BOTH discrete and continuous dynamics. No singularity needed. |

---

## Rules for the Graveyard

1. **Never delete an entry.** The whole point is that these failures stay visible.
2. **When adding a new failure, include:**
   - Exact claim (what was believed)
   - Date range (when it was believed)
   - Failure mechanism (why it was wrong)
   - What remains true (the kernel, if any)
3. **Before making any new claim, grep this file for similar keywords.** If your claim resembles something here, explicitly rule out the same artifact.
4. **Level 1 artifacts (computational) are the most dangerous.** They can resurrect silently if code regresses. The `compute_lie_generators()` method now has expm verification built in — do not remove it.
5. **Artifact resurrection is a process risk, not a theoretical risk.** It happens when new work builds on old (wrong) conclusions. Always check which version of the code was used to generate a claim.
