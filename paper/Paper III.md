# Accessibility Beyond Lie Closure in Finite Group Representations

### Hybrid Projector Geometry and Composition-Only Transport

---

## Abstract

**Discrete group composition can traverse where Lie algebra cannot.** Given a finite group $G$ acting on a representation $V = V_A \oplus V_B$, the logarithmic embedding $A_g = \log\rho(g)$ defines a continuous Lie algebra $\mathcal{L} = \mathrm{Lie}\{A_g\}$. But this continuous limit is structurally blind to cross-block transport: every Lie monomial is block-diagonal (Lemma 1), so $\kappa_d(\alpha,\beta) = 0$ for all depths $d$ whenever sectors $\alpha,\beta$ are supported in disjoint blocks. Discrete composition — $P_\alpha \rho(g) P_\gamma \rho(h) P_\beta$ through a hybrid sector $\gamma$ spanning both blocks — has no such constraint.

This paper proves the **Composition-Only Transport Theorem (informally the T7 Theorem,** §5.1) as the trilogy climax: discrete composition is strictly richer than Lie accessibility ($\text{Composition} \supsetneq \text{Lie}$). The phenomenon is not merely a failure of Lie closure — it is a structural mismatch between infinitesimal generation (tangent geometry, block-preserving) and compositional reachability (projector geometry, cross-block enabled). The paper formalizes this as a categorical distinction between the Lie-generated accessibility subcategory and the compositional completion (§7). A composition-only (T7) transport pair is one where $K_{\alpha\beta}=0$, $\kappa_d(\alpha,\beta)=0$ for all Lie depths $d$, yet the pair is reachable via length-2 discrete composition through an intermediate sector. The theorem's three structural conditions — shared noncommutative support (C1), transport-active hybrid projector (C2), block-preserving dynamics (C3) — are proved sufficient. Necessity: C1 proved for abelian and isotypic cases; the characterization conjecture (T7 $\iff$ C1–C3) remains open for general non-abelian groups. T7 and the M$_2$ Principle are established as logically independent obstruction types: S$_3$ nat$\oplus$reg (9-dim) has T7 with zero curvature.

**The narrative flips from previous versions.** S$_3$ — the smallest non-abelian group — is the protagonist; the Rubik's cube (228-dim) is the largest explicit realization of the same mechanism. The S$_3$ reg$\oplus$reg system (12-dim) achieves perfect separation: 30 gradient edges within-block, 10 curvature pairs within-block, 9 T7 pairs cross-block — zero counterexamples.

The supporting structure is the **κ_d accessibility hierarchy**: direct transport (K), gradient transport (κ₀ via individual $A_g$), curvature transport (κ₁ via commutators $[A_g, A_h]$), and composition-only transport (T7). The first three are block-preserving; only composition bridges blocks. Seven pure curvature channels exist in the Rubik cube — all within-block, none cross-block — confirming that Lie curvature creates new within-block channels but never crosses the block boundary.

**This paper studies κ_d.** Paper I studies A (the spectral object). Paper II studies K_αβ (transport topology). Paper III studies κ_d (Lie accessibility) and proves that what lies beyond all κ_d — composition — is strictly richer. The three papers together establish: **spectral origin → transport topology → Lie accessibility → composition transcendence.**

**Keywords:** Lie accessibility, discrete/continuous split, T7 theorem, κ_d hierarchy, composition-only transport, S₃ minimal prototype, block-preserving Lie algebra, curvature channels, transport category, compositional completion

---

## Notation Table

| Symbol | Meaning | Origin |
|--------|---------|--------|
| $G$ | Finite group | — |
| $S \subset G$ | Symmetric generating set ($S = S^{-1}$) | — |
| $\rho: G \to \mathrm{GL}(V)$ | Finite-dimensional orthogonal representation | — |
| $V = V_A \oplus V_B$ | Block decomposition into group-invariant subspaces (cubie-type blocks) | — |
| **block** | A cubie-type invariant component: cp (corner perm, 64-dim), ep (edge perm, 144-dim), co (corner ori, 8-dim), eo (edge ori, 12-dim) | Paper I |
| $A = \frac{1}{|S|}\sum_{s} \rho(s)$ | Averaging operator — Hermitian, rational spectrum | Paper I |
| **layer** $V_\lambda$ | An eigenspace of the averaging operator $A$ | Paper I |
| **primitive sector** $S_\alpha$ | Minimal joint eigenspace of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ — indivisible spectral unit | Paper I |
| $P_\alpha$ | Projector onto primitive sector $\alpha$ | Paper I |
| **hybrid sector** | A primitive sector with support spanning multiple cubie-type blocks (e.g., ep+eo) | Paper I |
| **S1–S9** | 9 primitive sectors: S1(V₁, isolated), S2(V₈/₉), S3(V₇/₉), S4(V₂/₃), S5–S7(V₅/₉; S6 primary hub, deg 5), S8–S9(V₁/₃) | Paper I |
| $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ | Transport tensor — single-generator amplitude transport from $\beta$ to $\alpha$ | Paper II |
| $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$ | Direct transport norm — static transport graph edge weight | Paper II |
| $\mathrm{Supp}_{\mathrm{nc}}(\alpha)$ | Noncommutative support — blocks where $\alpha$ has projection AND $\|[\mathrm{QT}^0, \mathrm{QT}^1]\| > 0$ | Paper II |
| $\mathrm{M}_2$ Principle | $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ — algebraic source of Type I (noncommutative) transport | Paper II |
| $A_g = \log \rho(g)$ | Infinitesimal generator — logarithmic embedding of discrete generator | **this paper** |
| $\mathcal{L} = \mathrm{Lie}\{A_g\}$ | Lie algebra generated by $\{A_g\}_{g \in S}$ under commutator bracket $[X,Y] = XY - YX$ | **this paper** |
| $\kappa_0(\alpha,\beta) = \max_g \|P_\alpha A_g P_\beta\|$ | **Gradient transport** — single-generator Lie accessibility ($\kappa_0 > 0$ but $K = 0$: transport invisible to direct but visible to gradient) | **this paper** |
| $\kappa_1(\alpha,\beta) = \max_{g,h} \|P_\alpha [A_g, A_h] P_\beta\|$ | **Curvature transport** — commutator-mediated Lie accessibility ($\kappa_0 = 0$ but $\kappa_1 > 0$: pure curvature channel) | **this paper** |
| $\kappa_d(\alpha,\beta)$ | Lie accessibility at depth $d$ — reachable via $d$-fold commutators of $\{A_g\}$ | **this paper** |
| **Lemma 0** | Isotypic support necessity: $\text{Supp}(E_\alpha) \cap \text{Supp}(E_\beta) = \emptyset \Rightarrow T_{\alpha\beta}(g) = 0$ for all $g$ | **this paper** (§2.6) |
| **Lemma 1** | Every Lie monomial in $\{A_g\}$ is block-diagonal: $P_\alpha \mathcal{L} P_\beta = 0$ when $\alpha, \beta$ have disjoint block support | **this paper** (§4.1) |
| **T7 pair** | **Composition-only transport**: $K_{\alpha\beta} = 0$, $\kappa_d(\alpha,\beta) = 0$ for all $d$, yet $\alpha \leadsto \beta$ via length-2 composition $P_\alpha \rho(g) P_\gamma \rho(h) P_\beta$ through hybrid $\gamma$ | **this paper** |
| C1, C2, C3 | T7 sufficient conditions: (C1) shared noncommutative support, (C2) transport-active hybrid projector, (C3) block-preserving dynamics | **this paper** |
| $\mathcal{T}$ | Transport category — objects = primitive sectors, morphisms = nonzero $\{T_{\alpha\beta}(g)\}_{g\in S}$ | **this paper** |
| $\mathbf{L}$ | Lie sublayer — block-preserving accessibility via $\cup_d \{\kappa_d > 0\}$ | **this paper** |
| $\bar{\mathcal{T}}$ | Compositional completion — closure of $\mathcal{T}$ under finite-length composition paths | **this paper** |
| **discrete-to-continuous singularity** | $P_\alpha \rho(g) P_\beta \neq 0$ but $P_\alpha A_g P_\beta = 0$ identically — the continuous limit annihilates a channel that exists in the discrete system | **this paper** |

---

## 1. Introduction

### 1.1 Where Papers I and II Left Off

Paper I established what the spectral object **is**: the averaging operator $A = \frac{1}{|S|}\sum\rho(s)$ has 6 rational eigenvalues ($\lambda = 1 - k/9$, $k \in \{0,1,2,3,4,6\}$), decomposes into 9 primitive sectors under the Center $\{A_{18}, QT_{\text{all}}, HT_{\text{all}}\}$, and is organized by a refinement semilattice with a commutative core. Paper I studies **A only** — no transport, no dynamics, no Lie.

Paper II established **why** the transport topology has the structure it does: $K_{\alpha\beta} = \max_g\|P_\alpha \rho(g) P_\beta\|_F > 0$ if and only if $\text{Supp}_{\text{nc}}(\alpha) \cap \text{Supp}_{\text{nc}}(\beta) \neq \emptyset$ (the noncommutative support intersection theorem, with one CP-mediated exception). The transport graph is a star: S6 (ep+eo, k=4) is the primary hub (degree 5), S1 (20-dim, cp+ep) is fully isolated ($K < 10^{-14}$ with all others). Paper II studies **K_αβ only** — no Lie, no κ_d, no accessibility hierarchy.

Paper III takes the next step. Given the transport topology (Paper II), **what can actually reach what** — and at what Lie-algebraic depth?

**Dependency.** This paper assumes the primitive sector decomposition (§2.2) and the transport topology classification ($K_{\alpha\beta}$, $\text{Supp}_{\text{nc}}$, the star topology, the M₂ principle) established in Papers I–II. These results are used — the transport graph is the input to the accessibility hierarchy — but not re-derived. The dependency is linear: Paper I defines the objects; Paper II classifies the static transport channels; Paper III studies which of those channels are dynamically accessible, at what Lie-algebraic depth, and where composition transcends the Lie closure entirely.

### 1.2 The Central Question

Take two primitive sectors $\alpha$ and $\beta$ supported in disjoint blocks of the representation $V = V_A \oplus V_B$. Can amplitude be transported from $\alpha$ to $\beta$?

| Mechanism | Object | Cross-block? |
|-----------|--------|-------------|
| **Direct** | $K_{\alpha\beta} = \max_g\|P_\alpha \rho(g) P_\beta\|$ | No — requires shared Supp_nc |
| **Gradient** | $\kappa_0(\alpha,\beta) = \max_g\|P_\alpha A_g P_\beta\|$ | No — $A_g$ is block-diagonal |
| **Curvature** | $\kappa_1(\alpha,\beta) = \max\|P_\alpha [A_g, A_h] P_\beta\|$ | No — $[A_g,A_h]$ is block-diagonal |
| **Composition** | $P_\alpha \rho(g) P_\gamma \rho(h) P_\beta$ | **Yes** — hybrid $\gamma$ bridges blocks |

### 1.2.1 Formal Definition — Composition-Only (T7) Pair

**Definition (Composition-Only / T7 Pair).** A pair of primitive sectors $(\alpha, \beta)$ is called a **T7 pair** if:

1. $K_{\alpha\beta} = 0$ — no direct transport under any single generator
2. $\kappa_d(\alpha,\beta) = 0$ for all $d \geq 0$ — inaccessible to all Lie-generated infinitesimal transport at **every** depth
3. **Yet** there exists a finite composition path

$$P_\alpha \rho(g_1) P_{\gamma_1} \cdots P_{\gamma_n} \rho(g_{n+1}) P_\beta \neq 0$$

mediated through hybrid sectors $\{\gamma_k\}$ that span both blocks.

That is, the pair is *composition-only*: unreachable by any element of the Lie algebra $\mathcal{L} = \text{Lie}\{A_g\}_{g \in S}$ (including all iterated commutators), but reachable through discrete group composition — the concatenation of generator actions whose intermediate amplitude passes through hybrid sectors bridging the two blocks.

The terminology "T7" originated as informal shorthand in the project's internal classification — the seventh structural transport pattern identified in the Rubik's cube enumeration, following six within-block transport types — and is retained as a convenient label. The formal mathematical object is the **composition-only pair**; "T7" designates its structural role.

**Theorem–Phenomenon relationship.** The *T7 Theorem* (§5.1) is the mathematical statement that composition-only pairs must exist whenever structural conditions C1–C3 hold, and that these pairs constitute the sole Lie-inaccessible-but-composition-accessible transport channel. Each individual T7 pair is a *phenomenon* — a concrete instance of the theorem, verified in a specific system. The theorem is universal (any finite group with block-diagonal $\rho$ and shared noncommutative support); the pair count and identity are system-specific.

**Accessibility Hierarchy.** The transport mechanisms form a strict nesting — each level strictly extends the previous in reach, and the final level (composition) is strictly richer than all preceding levels:

```
Level 0 — Direct transport:
    K_{αβ} = max_g ‖P_α ρ(g) P_β‖ > 0
        ↓                              ← within-block only
Level 1 — Gradient accessibility:
    κ₀(α,β) = max_g ‖P_α A_g P_β‖ > 0
        ↓                              ← within-block only
Level 2 — Curvature accessibility:
    κ₁(α,β) = max ‖P_α [A_g, A_h] P_β‖ > 0
        ↓                              ← within-block only
   ...
Level ∞ — Lie closure:
    ∃ d ≥ 0 : κ_d(α,β) > 0
        ↓                              ← within-block only
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Beyond — Composition accessibility (T7):
    discrete paths via hybrid sectors  ← cross-block enabled
```

**Lie accessibility $\subsetneq$ Composition accessibility.** Levels 0–∞ constitute *Lie accessibility* — all channels realizable by elements of the Lie algebra $\mathcal{L} = \text{Lie}\{A_g\}$ applied to gap vectors. The composition level is **strictly richer**: it contains every Lie-accessible channel *plus* cross-block channels with no Lie counterpart. Formally:

$$\text{LieAcc}(\alpha,\beta) \implies \text{CompAcc}(\alpha,\beta), \qquad \text{but} \qquad \exists(\alpha,\beta): \text{CompAcc}(\alpha,\beta) \land \neg\text{LieAcc}(\alpha,\beta)$$

**Cross-block transport lives ONLY in the composition layer.** All Lie-generated transport (direct, gradient, curvature, and all higher commutators) is block-preserving (Lemma 1, §4.1). Any transport between sectors supported in disjoint blocks requires discrete composition through a hybrid bridge — it has **no** Lie-algebraic realization at any depth. This is the central structural fact of the paper.

---

The first three rows of the table above are theorems, not observations. $A_g = \log\rho(g)$ inherits the block-diagonal structure of $\rho(g)$ (Lemma 1). Commutators of block-diagonal matrices are block-diagonal. By induction, **every Lie monomial at every depth is block-diagonal.** The continuous limit — the standard mathematical tool for "smooth" control — is structurally blind to cross-block composition paths.

The fourth row — discrete composition — is not blocked. A hybrid sector $\gamma$ whose projector $P_\gamma$ spans both $V_A$ and $V_B$ can route transport: $\alpha \to \gamma \to \beta$. The discrete group action preserves this path; the continuous limit collapses it.

**This is the discrete/continuous split.** It is the deepest structural fact in the trilogy.

The obstruction is not algebraic noncommutativity alone, but the mismatch between two fundamentally different access modes: **Lie closure probes infinitesimal tangent geometry inside blocks; discrete composition probes global projector geometry across blocks.** The Lie algebra only sees what is tangent to the group orbit within each invariant subspace — it is structurally blind to the projector-mediated bridge that a hybrid sector provides. This mismatch between tangent accessibility and projector geometry is the conceptual core of the paper.

### 1.3 The S₃ Narrative Flip

Previous versions of this paper positioned the Rubik's cube (228-dim) as the primary object. That was backwards. **S₃ — the smallest non-abelian group (order 6) — is the true protagonist.** It exhibits the complete T7 mechanism at 9 dimensions (nat$\oplus$reg) with zero M₂ curvature — proving that T7 and M₂ are independent. At 12 dimensions (reg$\oplus$reg), it achieves perfect separation of all three accessibility types with zero counterexamples.

The Rubik's cube is the *largest explicit realization*. It demonstrates the same C1–C3 mechanism at scale, not a different phenomenon. The narrative arc is:

$$\text{S}_3\text{ (9-dim)} \xrightarrow{\text{minimal prototype}} \text{S}_3\text{ (12-dim)} \xrightarrow{\text{perfect separation}} \text{Rubik (228-dim)} \xrightarrow{\text{full-scale realization}}$$

### 1.4 Structure of This Paper

| Part | Content | Question |
|------|---------|----------|
| **I** (§2–3) | Accessibility hierarchy: K, κ₀, κ₁, κ₂ | What can reach what, at what depth? |
| **II** (§4) | Lie freezing: Lemma 1, block-preserving closure | Why can't Lie cross blocks? |
| **III** (§5) | **T7 Theorem** — composition ⊋ Lie | When does composition transcend Lie? |
| **IV** (§6) | Realizations: S₃ prototypes → Rubik at scale | How does this manifest? |
| **V** (§7) | **Categorical interpretation** — transport category, Lie subcategory, compositional completion | What structure does T7 reveal? |
| **VI** (§8) | Discussion, limitations, open directions | |
| **VII** (§9) | **Concluding perspective** — why the continuous limit is structurally incomplete | |

![Figure 0: Accessibility Hierarchy Collapse — Lie World vs Compositional World](../../figures/fig0_pipeline.png)
*Figure 0: The accessibility hierarchy collapse in three panels. (a) Lie/Continuous World: Lie generators $\{A_g\}$ and their commutators $[A_g, A_h]$ rotate within each block but are block-diagonal (Lemma 1) — every arrow stops at the block boundary (×). Cold colors, rigid structure. (b) Spectral Decomposition: pure sectors (circles) occupy each block; hybrid sectors (amber diamonds) sit directly on the block boundary — cracks, tunneling nodes, junction states bridging both sides. (c) Compositional World: finite composition $\rho(g_1) P_\gamma \rho(g_2)$ routes through a hybrid bridge, bypassing the wall. The composition path (red) traverses where no Lie-generated channel can. Slogan: Continuous dynamics freezes at the block boundary; composition bypasses it.*

---

## 2. Setup and Prerequisites

### 2.1 Representation and Generators

We work with the 228-dimensional representation $\rho: G \to \text{GL}(228, \mathbb{R})$ of the Rubik's cube group, decomposing into four blocks:

$$V = \text{CP}(64) \oplus \text{EP}(144) \oplus \text{CO}(8) \oplus \text{EO}(12) = 228$$

The generator set $S$ consists of the 18 face-turn generators (6 faces $\times$ 3 turns: CW, CCW, 180°).

All numerical data in this paper are at **post-ρ-fix resolution**: 6 canonical layers ($k \in \{0,1,2,3,4,6\}$, $\lambda = 1 - k/9$) and 9 primitive sectors from the Center $\{A_{18}, QT_{\text{all}}, HT_{\text{all}}\}$ joint diagonalization. The single source of truth is [`paper_data.md`](paper_data.md).

### 2.2 Spectral Decomposition

The averaging operator $A = \frac{1}{18}\sum_{s \in S} \rho(s)$ has eigendecomposition:

$$A = \sum_{i} \lambda_i P_i, \quad P_i P_j = \delta_{ij} P_i, \quad \sum_i P_i = I_{228}$$

with 6 distinct eigenvalues and 9 primitive sectors (Center joint diagonalization). Full tables in [`paper_data.md`](paper_data.md) §3–4.

### 2.3 Block Decomposition and Supp_nc

Each sector has well-defined block support. The noncommutativity hierarchy (from Paper II):

$$\|[QT^0, QT^1]\|_F = 2.92 \text{ total}; \quad \text{cp}=0,\; \text{ep}=2.74\;(93.9\%),\; \text{co}=0.61,\; \text{eo}=0.79$$

$\text{Supp}_{\text{nc}}(\alpha) = \{b \in \{\text{cp},\text{ep},\text{co},\text{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[QT^0,QT^1]\|_b > 0\}$.

### 2.4 Lie Generators

The Lie generators are computed via the principal matrix logarithm:

$$A_g = \log \rho(g)$$

using `scipy.linalg.logm`. Fidelity: $\max_g \|\exp(A_g) - \rho(g)\| < 3 \times 10^{-8}$. The $A_g$ are skew-Hermitian to numerical precision. The full Lie algebra is $\mathcal{L} = \text{Lie}\{A_g\}_{g \in S}$, generated by iterated commutators.

### 2.5 Hybrid Sectors — A Formal Definition

The term "hybrid sector" has been used informally throughout the trilogy to designate primitive sectors whose projectors span multiple invariant blocks. It is now formalized as a mathematical object.

**Definition (Hybrid Sector).** Let $V = V_A \oplus V_B \oplus \cdots$ be the block decomposition of the representation. A primitive sector $E_\gamma$ with projector $P_\gamma$ is called **hybrid** if its projector has nonzero restriction to more than one invariant block:

$$P_\gamma|_{V_A} \neq 0 \quad\text{and}\quad P_\gamma|_{V_B} \neq 0$$

for at least two distinct blocks $A \neq B$.

A hybrid sector is **transport-active** if it participates in nonzero transport morphisms to sectors in both blocks:

$$\exists \alpha \subset V_A,\; \beta \subset V_B : K_{\alpha\gamma} > 0 \;\text{and}\; K_{\gamma\beta} > 0$$

Equivalently (computable criterion): $\text{Supp}(E_\gamma) \cap \text{Supp}(E_\alpha) \neq \emptyset$ and $\text{Supp}(E_\gamma) \cap \text{Supp}(E_\beta) \neq \emptyset$, where $\text{Supp}(E) = \{\tau \in \hat{G} : \text{Tr}(P \Pi_\tau) > 0\}$ is the isotypic support.

A hybrid sector that fails the transport-active criterion — hybrid by block support but sharing no irreducible content with sectors in both blocks — is called **inert**. Inert hybrids arise from eigenvalue coincidence in the commutative center $Z$ without shared irrep geometry, and provide no composition path (confirmed by the S$_3$ "false T7" counterexample, `has_path=False`).

**Examples (Rubik's cube, 9-sector resolution):**

| Sector | Blocks | Transport-active? | Role |
|--------|--------|-------------------|------|
| S1 (V$_1$, 20-dim) | cp+ep | No — isolated | $G$-invariant subrepresentation |
| S3 (V$_{7/9}$, 39-dim) | ep+eo | Yes | Hub connector |
| S4 (V$_{2/3}$, 26-dim) | ep+co | Yes | Hub connector |
| S6 (V$_{5/9}$, 39-dim) | ep+eo | **Yes** | Primary hub (degree 5) |
| S7 (V$_{5/9}$, 66-dim) | cp+ep+co+eo | **Yes** | Secondary hub (degree 4) |
| S9 (V$_{1/3}$, 27-dim) | cp+co | Yes | CP-mediated channel to S8 |

S6 and S7 are the two transport-active hybrids that mediate all 5 T7 pairs (§6.3). S1 is hybrid by block support (cp+ep) but transport-inert — it is a $G$-invariant subrepresentation with $K < 10^{-14}$ to all other sectors.

This definition makes precise the C2 condition in the T7 Theorem (§5.2): "transport-active hybrid projector" is now a fully defined mathematical object.

### 2.6 Lemma 0 — Isotypic Support Necessity

A preparatory lemma, used throughout the paper.

**Lemma 0 (Isotypic Support Necessity).** For a primitive sector $E_\alpha$ with projector $P_\alpha$, define its isotypic support $\text{Supp}(E_\alpha) = \{\tau \in \hat{G} : \text{Tr}(P_\alpha \Pi_\tau) > 0\}$, where $\Pi_\tau$ is the projector onto the $\tau$-isotypic component of $V$.

If $\text{Supp}(E_\alpha) \cap \text{Supp}(E_\beta) = \emptyset$, then for all $g \in G$:

$$T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta = 0$$

*Proof.* Take $v \in E_\beta$. Decompose by isotypic components: $v = \sum_{\tau \in \text{Supp}(E_\beta)} v_\tau$. By Schur's lemma, $\rho(g)$ preserves each isotypic component: $\rho(g)v_\tau$ stays in the $\tau$-isotypic component. $P_\alpha$ annihilates all $\tau \notin \text{Supp}(E_\alpha)$. Since $\text{Supp}(E_\alpha) \cap \text{Supp}(E_\beta) = \emptyset$, $P_\alpha \rho(g)v = 0$. ∎

**Corollary (Composition can bridge disjoint support).** $P_\alpha \rho(g) P_\gamma \rho(h) P_\beta$ can be nonzero even when $\text{Supp}(E_\alpha) \cap \text{Supp}(E_\beta) = \emptyset$, provided an intermediate hybrid sector $\gamma$ shares isotypic support with both. The hybrid projector $P_\gamma$ acts as a support bridge: its $V_A$ component catches $\rho(h)v$ and its $V_B$ component passes the result to $P_\alpha$.

This proves that **zero cross-block direct edges is a theorem, not an observation.**

---

## 3. Part I — The Accessibility Hierarchy

**Question:** At what Lie-algebraic depth can sector $\alpha$ reach sector $\beta$?

![Figure 1: Four-Level Accessibility Hierarchy](../../figures/fig1_hierarchy.png)
*Figure 1: The four-level accessibility hierarchy. Direct transport (K) → Gradient accessibility (κ₀) → Curvature accessibility (κ₁) → Lie closure (all depths). The pyramid narrows as accessibility becomes more constrained — all Lie levels are within-block only. Below the Lie Barrier wall, discrete composition resurrects accessibility: cross-block transport lives ONLY in the composition layer. $\mathrm{Direct} \subset \mathrm{Gradient} \subset \mathrm{Curvature} \subset \mathrm{Lie\ Closure} \subsetneq \mathrm{Composition}$.*

### 3.1 Level 0 — Direct Transport: K

$$K_{\alpha\beta} = \max_{g \in S} \|P_\alpha \rho(g) P_\beta\|_F$$

At 9-sector resolution ([`paper_data.md`](paper_data.md) §5): 20 directed edges (10 undirected pairs), **all block-preserving** — zero cross-block direct edges. S1 (V₁, 20-dim, cp+ep) has $K < 10^{-14}$ with all other sectors — a G-invariant subrepresentation. S6 (39-dim, ep+eo, V₅/₉) is the primary hub (degree 5). S7 (66-dim, all blocks, V₅/₉) is the secondary hub (degree 4).

**Theorem (Paper II):** $K_{\alpha\beta} > 0 \iff \text{Supp}_{\text{nc}}(\alpha) \cap \text{Supp}_{\text{nc}}(\beta) \neq \emptyset$, with the sole exception of S8 (pure CP) $\leftrightarrow$ S9 (CP+CO) where K = 2.83 despite both having empty Supp_nc — the commutative CP-mediated channel.

### 3.2 Level 1 — Gradient Transport: κ₀

$$\kappa_0(\alpha,\beta) = \max_{g \in S} \|P_\alpha A_g P_\beta\|_F$$

Computed over all 18 $A_g$. At 9-sector resolution ([`paper_data.md`](paper_data.md) §6.1):

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

Max asymmetry: $1.6 \times 10^{-8}$ — symmetric to machine precision. Gradient transport preserves all K > 0 channels: if $K_{\alpha\beta} > 0$ then $\kappa_0(\alpha,\beta) > 0$. The 9-sector resolution reveals intra-V₅/₉ structure invisible at 6-layer: S5 (1-dim, pure EO), S6 (39-dim, ep+eo, primary hub), and S7 (66-dim, all-block, secondary hub) are distinct sectors with distinct κ₀ profiles.

### 3.3 Level 2 — Curvature Transport: κ₁

$$\kappa_1(\alpha,\beta) = \max_{g,h \in S} \|P_\alpha [A_g, A_h] P_\beta\|_F$$

![Figure 3: Curvature Emergence — First-Order Frozen, Second-Order Accessible](../../figures/fig3_curvature_emergence.png)
*Figure 3: Geometric mechanism of curvature emergence. Left: Direct transport fails (K=0, no shared Supp_nc). Center: Gradient fails (κ₀=0, A_g is block-diagonal, tangent cone empty). Right: Curvature succeeds (κ₁>0, commutator $[A_g, A_h]$ bends trajectory into connection). Enhancement $\kappa_1/\kappa_0 \sim 10^{14}$ — all curvature channels are within-block; cross-block transport requires composition (T7).*

At 9-sector resolution ([`paper_data.md`](paper_data.md) §6.2):

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

**Seven pure curvature channels** at 9-sector — pairs with $\kappa_0 \approx 0$ but $\kappa_1 > 0$: S2↔S3 (κ₁=0.71, shared EO), S2↔S7 (κ₁=1.01, shared EO), S3↔S4 (κ₁=4.27, shared EP), S3↔S5 (κ₁=1.01, shared EO), S4↔S7 (κ₁=6.17, shared EP+CO), S5↔S7 (κ₁=1.42, shared EO), S7↔S8 (κ₁=6.98, shared CP). The largest curvature-only channel at 9-sector is S7↔S8 with $\kappa_0 \sim 10^{-14}$ and $\kappa_1 = 6.98$ (enhancement $\sim 5 \times 10^{14}$).

**All 7 pure curvature channels are within-block** — every pair shares at least one block (EP, EO, CO, or CP). Zero cross-block curvature channels at any resolution. This is the central structural fact: **Lie curvature creates new within-block channels but cannot bridge blocks.** The 6-layer analysis identified 6 such channels; the 9-sector refinement resolves one more (S2↔S7 distinguishing intra-V₅/₉ EO coupling from the broader S2↔S6/S7 pairing at 6-layer).

### 3.4 Higher Depth: κ₂ and Beyond

$\kappa_2$ (nested commutators $[[A_g, A_h], A_k]$) further amplifies all channels but creates no new cross-block ones. The pattern is stable: $\kappa_d$ grows with $d$ within blocks, stays zero across blocks. The Lie algebra is block-preserving at **all** depths (Lemma 1, §4.1).

### 3.5 Three Accessibility Classes

The κ hierarchy partitions sectors into three classes:

| Class | Sectors | κ₀ (gradient) | κ₁ (curvature) | Mechanism |
|-------|---------|--------------|----------------|-----------|
| **I** | S1 (V₁) | 0 | 0 | G-invariant subrepresentation |
| **II** | Most non-S1 pairs | $>0$ | $>0$ | Gradient + curvature coupled |
| **III** | S3↔S4, S7↔S8, etc. | $\approx 0$ | **> 0** | Pure curvature (Krawtchouk-order mismatch) |

Class I is subrepresentation isolation — the sector is an actual $G$-subrepresentation, hence invariant under all $\rho(g)$ and $A_g$.

Class II is the generic case — individual Lie generators already couple the sectors, curvature amplifies.

Class III is the Krawtchouk-order mismatch mechanism: sectors in different Krawtchouk eigenspaces (e.g., $k=2$ vs $k=3$) that share block support. Individual $A_g$ preserve Krawtchouk order (they live in the Bose-Mesner algebra); commutators $[A_g, A_h]$ mix across orders. The enhancement ratio $\kappa_1/\kappa_0 \sim 10^{14}$ is the signature of pure curvature coupling. At 9-sector resolution, 7 pure curvature channels are identified — all within-block, zero cross-block.

**These three classes are the Lie-accessible channels.** What lies beyond them — composition — is the subject of Parts II–III.

**Connection to classical controllability.** The κ_d hierarchy mirrors the Lie bracket accessibility test in nonlinear control [4,5,6]: κ₀ corresponds to the Lie algebra generated by {A_g}, κ₁ to the first-order bracket $[A_g, A_h]$, and higher κ_d to iterated brackets. The key difference is that classical controllability concerns the Lie algebra generated by vector fields on a manifold, while here the Lie generators A_g act linearly on the fixed representation space V. The block-preserving Lemma 1 (§4.1) is the finite-group analogue of the fact that the accessibility distribution respects invariant foliations [6, Ch.5].

---

## 4. Part II — Lie Freezing: Why the Continuous Limit Cannot Cross Blocks

![Figure 2: Lie Barrier & Discrete Escape — The Central Visual Metaphor](../../figures/fig2_lie_barrier.png)
*Figure 2: The Lie Barrier — the signature visual of Paper III. Left: Continuous Lie flow ($A_g$, $[A_g,A_h]$, and all higher commutators) is blocked — κ_d = 0 for all d — because every Lie monomial is block-diagonal (Lemma 1). Right: Discrete composition escape (T7) — the path α → H1 → H2 → β bypasses the Lie barrier through hybrid sectors bridging the two blocks. Composition ⊋ Lie: the discrete group action can traverse where the continuous limit cannot.*

### 4.1 Lemma 1 — Block-Diagonal Lie Closure

**Lemma 1.** If $\rho(g) = \rho_A(g) \oplus \rho_B(g)$ for all $g \in G$, then every Lie monomial in $\{A_g : g \in G\}$ is block-diagonal.

*Proof.* For each $g$, $A_g = \log\rho(g) = \log(\rho_A(g)) \oplus \log(\rho_B(g)) = A_g^A \oplus A_g^B$ — the matrix logarithm preserves block structure. The commutator of block-diagonal matrices is block-diagonal:

$$[X_A \oplus X_B,\; Y_A \oplus Y_B] = [X_A, Y_A] \oplus [X_B, Y_B]$$

By induction, any depth-$d$ monomial (iterated commutators and linear combinations) is block-diagonal. ∎

This is a structural theorem, not a numerical observation. The Rubik's cube representation $\rho = \rho_{\text{cp}} \oplus \rho_{\text{ep}} \oplus \rho_{\text{co}} \oplus \rho_{\text{eo}}$ is block-diagonal by construction — each of the four cubie-type blocks transforms independently. Hence **every** element of $\mathcal{L} = \text{Lie}\{A_g\}$ is block-diagonal.

### 4.2 Cross-Block Lie Freezing

For a pure-A sector $\alpha$ (projector supported entirely in $V_A$) and a pure-B sector $\beta$ (supported entirely in $V_B$), and any block-diagonal operator $C = C_A \oplus C_B$:

$$P_\alpha C P_\beta = (P_\alpha \Pi_A)(C_A \oplus C_B)(\Pi_B P_\beta) = P_\alpha \cdot (\Pi_A (C_A \oplus C_B) \Pi_B) \cdot P_\beta = P_\alpha \cdot 0 \cdot P_\beta = 0$$

By Lemma 1, every $C_d$ at any Lie depth $d$ is block-diagonal. Therefore:

$$\kappa_d(\alpha, \beta) = 0 \quad \forall d \geq 0$$

**Cross-block transport is Lie-inaccessible at all depths.** The continuous limit, no matter how many commutator levels are included, cannot couple sectors supported in disjoint blocks.

### 4.3 Within-Block Curvature Channels

In contrast, **within** a block, commutators create genuinely new transport. The 6 pure curvature channels ($\kappa_0 \approx 0$, $\kappa_1 > 0$) all share block support. The Krawtchouk-order mixing mechanism (§3.5) operates entirely within the cp/EP blocks — it cannot cross the block boundary.

This separation is absolute:
- **Within-block**: gradient + curvature + higher depth — rich Lie accessibility
- **Cross-block**: identically zero at all Lie depths — composition is the sole channel

---

## 5. Part III — The T7 Theorem: Composition ⊋ Lie

**This is the climactic theorem of the trilogy.**

### 5.1 Definition: Composition-Only Transport (T7)

A **composition-only transport pair** — informally abbreviated **T7** (for "transport type 7," the seventh structural pattern identified in the Rubik's cube spectral enumeration, following six within-block transport types) — between sectors $(\alpha, \beta)$ satisfies three conditions:

1. **K$_{\alpha\beta}$ = 0** — no direct transport (single generator)
2. **κ$_d(\alpha,\beta)$ = 0 for all $d$** — no Lie accessibility at any depth
3. **$\exists \gamma$ with K$_{\alpha\gamma} > 0$ and K$_{\gamma\beta} > 0$** — reachable via length-2 discrete composition

The pair is *composition-only*: discrete group action can bridge it; the continuous Lie limit cannot — at any order of commutators. The nomenclature "T7" is informal shorthand and designates the structural role (composition-only, cross-block), not a mathematical type.

### 5.2 The Minimal T7 Theorem

**Setup.** Let:
- $G$ be a finite group
- $(V, \rho)$ a finite-dimensional unitary representation: $\rho(g) = \rho_A(g) \oplus \rho_B(g)$, $V = V_A \oplus V_B$
- $S \subset G$ an inverse-closed generator subset
- $Z = \langle A_{S_1}, \ldots, A_{S_k}\rangle$ a commutative subalgebra of the averaging algebra ($k \geq 1$), containing $A_S$
- $\{E_\alpha\}$ the primitive sectors from joint diagonalization of $Z$
- A sector $E_\alpha$ is **pure-A** if $P_\alpha V_B = \{0\}$, **pure-B** if $P_\alpha V_A = \{0\}$, **hybrid** otherwise

**Structural Conditions.**

**(C1) Shared noncommutative support.** There exists an irreducible representation $\tau$ of $G$ appearing in both $\rho_A$ and $\rho_B$ with multiplicity $\geq 1$ in each.

Equivalently: $\text{Supp}_{\text{nc}}(V_A) \cap \text{Supp}_{\text{nc}}(V_B) \neq \emptyset$.

**(C2) Transport-active hybrid projector.** There exists a primitive sector $E_\gamma$ (a joint eigenspace of $Z$) whose projector $P_\gamma$ satisfies both:

(i) **Hybrid block support:** $P_\gamma V_A \neq \{0\}$ and $P_\gamma V_B \neq \{0\}$ — the projector spans both blocks.

(ii) **Transport-active (computable criterion):** Define the isotypic support $\text{Supp}(E_\alpha) = \{\tau \in \hat{G} : \text{Tr}(P_\alpha \Pi_\tau) > 0\}$ where $\Pi_\tau$ is the projector onto the $\tau$-isotypic component of $V$. Then $E_\gamma$ is *transport-active* if and only if:

$$\text{Supp}(E_\alpha) \cap \text{Supp}(E_\gamma) \neq \emptyset \quad\text{and}\quad \text{Supp}(E_\gamma) \cap \text{Supp}(E_\beta) \neq \emptyset$$

for some pure-A sector $\alpha$ and pure-B sector $\beta$. Equivalently, there exists an irreducible representation $\tau$ common to all three isotypic supports, and within each block the $\tau$-multiplicity spaces of $P_\alpha$ and $P_\gamma$ (in $V_A$) and of $P_\gamma$ and $P_\beta$ (in $V_B$) have nonzero overlap under $\rho(g)$. This is computable: given the isotypic projectors $\Pi_\tau$ — obtained by diagonalizing the full commutant algebra $\text{Comm}(\rho(G))$, which for this representation is a 610-dimensional commutative algebra computed via index-pair orbit decomposition (see `test/canonical/_exp_isotypic_decomposition.py`) — verify $\text{Tr}(P_\alpha \Pi_\tau) > 0$, $\text{Tr}(P_\gamma \Pi_\tau) > 0$, $\text{Tr}(P_\beta \Pi_\tau) > 0$ for at least one $\tau \in \hat{G}$. For the S$_3$ prototypes, the isotypic decomposition is explicit in Appendix C.

A *spectral hybrid* — a joint eigenspace spanning both blocks but arising from eigenvalue coincidence in the commutative center $Z$ without shared $\tau$-multiplicity geometry — satisfies (i) but not (ii). Such sectors are transport-inert: they provide no composition path, as confirmed by the S₃ "false T7" counterexample (standard vs. trivial$\oplus$sign, `has_path=False`).

**(C3) Block-preserving dynamics.** $\rho(g) = \rho_A(g) \oplus \rho_B(g)$ for all $g \in G$.

**Theorem (T7).** Under C1–C3:

**(a) Lie freezing.** For any pure-A sector $\alpha$ and pure-B sector $\beta$:

$$\kappa_d(\alpha, \beta) = 0 \quad \forall d \geq 0$$

No finite-depth Lie bracket sequence can couple them.

**(b) Discrete composition accessibility.** There exists a transport-active hybrid sector $\gamma$ and group elements $g, h \in G$ such that:

$$P_\alpha \rho(g) P_\gamma \neq 0 \quad\text{and}\quad P_\gamma \rho(h) P_\beta \neq 0$$

Hence the composition path $\alpha \to \gamma \to \beta$ is accessible in the discrete transport category.

**(c) Composition ⊋ Lie.**

$$\text{discrete accessibility}(\alpha, \beta) = \text{true}, \quad \text{Lie accessibility}(\alpha, \beta) = \text{false (at all depths)}$$

### 5.3 Proof

The proof relies on Lemma 0 (§2.6) and Lemma 1 (§4.1).

**(a) Cross-block κ_d = 0.** Let $\alpha$ be pure-A ($P_\alpha V_B = \{0\}$), $\beta$ pure-B ($P_\beta V_A = \{0\}$). For any block-diagonal $C = C_A \oplus C_B$:

$$P_\alpha C P_\beta = P_\alpha \Pi_A (C_A \oplus C_B) \Pi_B P_\beta = P_\alpha \cdot 0 \cdot P_\beta = 0$$

By Lemma 1, every $C_d$ is block-diagonal. Hence $\kappa_d(\alpha,\beta) = 0$ for all $d$. ∎

**(b) Discrete composition path exists.** By C1, shared irrep $\tau \subset \rho_A \cap \rho_B$. By C2, transport-active hybrid $\gamma$ has $\tau \in \text{Supp}(E_\gamma)$ and the multiplicity-space geometry places distinct A-copies and B-copies into different sectors connected through $\gamma$. By Lemma 0, $\text{Supp}(E_\alpha) \cap \text{Supp}(E_\gamma) \neq \emptyset$ (both carry $\tau$ in $V_A$) and $\text{Supp}(E_\gamma) \cap \text{Supp}(E_\beta) \neq \emptyset$ (both carry $\tau$ in $V_B$). Hence $\exists g, h$ with $T_{\alpha\gamma}(g) \neq 0$ and $T_{\gamma\beta}(h) \neq 0$. ∎

**(c) Composition ⊋ Lie.** Immediate from (a) and (b): discrete path exists, Lie accessibility is identically zero at all depths. ∎

### 5.4 Necessity

| Condition | Structural Role | Necessity Status |
|-----------|----------------|-----------------|
| **C1** Shared noncommutative support | Algebraic substrate — bridgeability (Lemma 0) | **Conjectured** for general case; proved for abelian groups + isotypic representations; exhaustive search passed on all small-group systems tested (see below) |
| **C2** Transport-active hybrid projector | Geometric bridge — composition path exists | Definitional — follows from the computable criterion (§5.2); the distinction from inert spectral hybrids is verified |
| **C3** Block-preserving dynamics | Dynamic separation — Lie inaccessibility | Proved (contrapositive of T7 definition; Lemma 1 guarantees all Lie monomials are block-diagonal) |

**N1 (C1 necessity — why the general proof is hard).** Without shared noncommutative support, C1 asserts that no T7 pair exists. In the abelian case, all irreps are 1-dimensional; the center $Z$ acts as simultaneous eigenvalues on each irrep, making the sector partition a refinement of the irrep decomposition. Disjoint irreps yield sectors with disjoint isotypic support — Lemma 0 then forces K=0, blocking the composition path. For the isotypic case (both blocks carry only one irrep type), the shared support is automatic.

The difficulty in the general non-abelian case is that the center $Z$ can mix distinct irreps within the same eigenspace (eigenvalue coincidence), producing spectral hybrids that carry disjoint irreps — a "not shared" scenario that could, in principle, circumvent C1. The question is whether such a spectral hybrid can ever be transport-active. All small-group systems tested to date — S₃ (all representation pairs: nat⊕reg, reg⊕reg, nat⊕nat, std⊕sign, etc.), Q₃ (quaternion, 8 elements), S₄ (24 elements), and Z₂×Z₂ — satisfy C1 necessity: no T7 pair arises without a shared irrep. The S₃ "false T7" (standard vs. trivial⊕sign) confirms the mechanism: eigenvalue coincidence creates a hybrid projector spanning both blocks, but without a shared irrep the hybrid fails the computable C2 criterion (Tr(P_α Π_τ) = 0 for all τ common to α and β), and `has_path=False`.

**N3 (C3 necessity).** If cross-block $\kappa_d(\alpha,\beta) > 0$ for some $d$, the pair is Lie-accessible and not a T7 pair. The contrapositive is the T7 definition. Block-diagonal $\rho$ is the natural sufficient condition; it is conjectured necessary for *systematic* cross-block T7 (a single non-block-diagonal generator would provide a Lie-accessible cross-block channel).

**The Characterization Conjecture.** T7 $\iff$ C1–C3. The three conditions are sufficient (proved in §5.3). C2 and C3 are necessary (proved). C1 is proved necessary for abelian and isotypic cases, supported by exhaustive search on all small-group systems tested, and conjectured necessary for all finite groups. A proof for general non-abelian groups would require showing that eigenvalue coincidence across disjoint irreps (in the commutative center $Z$) can never produce a transport-active hybrid — i.e., that the computable C2 criterion cannot be satisfied without shared isotypic support.

### 5.5 T7 and M₂ Are Independent Obstruction Types

The T7 mechanism is often conflated with the M₂ principle (Paper II — noncommutative AW simple components as transport atoms). They are logically distinct:

| Property | M₂ Obstruction | T7 Obstruction |
|----------|---------------|----------------|
| **Origin** | Noncommutative AW components ($n_i \geq 2$) | Block-diagonal $\rho$ + shared irrep + hybrid bridge |
| **Effect** | Refinement failure, curvature transport | Cross-block composition-only accessibility |
| **Lie consequence** | $\kappa_1 > 0$ within shared M₂ | $\kappa_d = 0$ across blocks |
| **Minimal system** | Any noncommutative AW component | S₃ nat$\oplus$reg (9-dim, T7 only, **zero M₂**) |
| **Within/cross block** | Within-block | Cross-block |

**Co-occurrence:** Rubik's cube and S₃ reg$\oplus$reg exhibit both. **Independence:** S₃ nat$\oplus$reg has T7 without any M₂ curvature ($\kappa_1 = 0$ everywhere) — proving that the two mechanisms are structurally orthogonal. The minimal prototype for T7 requires only a non-abelian group with block-diagonal representation and shared irreps, not noncommutative AW components.

---

## 6. Part IV — From S₃ Prototypes to Rubik Realization

### 6.1 S₃ nat⊕reg — 9-dim, T7 Without Curvature

The minimal working T7 system. $G = S_3$ (order 6, smallest non-abelian group), $\rho = \rho_{\text{nat}} \oplus \rho_{\text{reg}}$ (3-dim natural + 6-dim regular), $S =$ all 6 group elements, $Z = \langle A_{\text{full}}, A_{\text{trans}}\rangle$.

![Figure 4: S₃ Minimal Prototype — 9-dim, T7 Without Curvature](../../figures/fig4_s3_prototype.png)
*Figure 4: S₃ nat⊕reg (9-dim) — the minimal T7 prototype. Left: 5-node graph with dual-color hybrid S5 (nat+reg) as the sole bridge. Direct edges (solid blue) are all within-block or pure↔hybrid. Three T7 pairs (dashed red) are all cross-block nat↔reg, mediated through S5. Right: System properties — zero curvature channels (no M₂), κ₁=0 everywhere, proving T7 and M₂ are logically independent obstruction types.*

**5 primitive sectors** ([`paper_data.md`](paper_data.md) §9.1):

| Sector | Dim | Type | A_full | A_trans |
|--------|-----|------|--------|---------|
| S1 | 2 | Pure-reg | 1.0 | 0.0 |
| S2 | 1 | Pure-reg | 0.0 | 1.0 |
| S3 | 1 | Pure-nat | 0.0 | −0.577 |
| S4 | 1 | Pure-reg | 0.0 | 0.577 |
| S5 | 4 | **Hybrid** (nat+reg) | 0.0 | 0.0 |

**Results:**
- 14 direct edges — all within-block or pure↔hybrid
- Curvature pairs ($\kappa_0=0, \kappa_1>0$): **0** — no M₂ in this system
- **T7 pairs: 3** — all cross-block nat↔reg, mediated through S5 (hybrid)
  - S1(reg) ↔ S3(nat), S2(reg) ↔ S3(nat), S3(nat) ↔ S4(reg)
- C1: S₃ standard 2-dim irrep appears in nat (×1) and reg (×2). ✓
- C2: S5 is a transport-active hybrid — carries the standard irrep from both blocks. ✓
- C3: $\rho$ is block-diagonal by construction. ✓
- κ₁ = 0 everywhere — **T7 exists without curvature.**

**This 9-dimensional system is the minimal T7 prototype.** It isolates the core algebraic structure without geometric overhead.

### 6.2 S₃ reg⊕reg — 12-dim, Perfect Separation

$G = S_3$, $\rho = \rho_{\text{reg}} \oplus \rho_{\text{reg}}$, $S =$ {3 transpositions}, $Z = \langle A_3, A_2\rangle$.

**10 primitive sectors** ([`paper_data.md`](paper_data.md) §9.2): 5 pure-A + 4 pure-B + 1 hybrid (S10 = A:1 + B:1).

**Perfect separation — zero counterexamples:**

| Type | Count | Location |
|------|-------|----------|
| Gradient edges (κ₀ > 0) | 30 | **All** within-block |
| Curvature pairs (κ₀=0, κ₁>0) | 10 | **All** within-block |
| T7 pairs (K=κ₀=κ₁=0) | 9 | **All** cross-block |

This is the full hierarchy in a 12-dimensional system. The three accessibility types are perfectly aligned with the block structure. The hybrid sector S10 is the sole bridge — all 9 T7 paths go through it.

### 6.3 Rubik's Cube — 228-dim, Same Mechanism at Scale

The Rubik's cube realizes the identical C1–C3 mechanism.

**C1 — Shared noncommutative support.** The EP block (144-dim, $\|[QT^0, QT^1]\| = 2.74$) carries the $M_2(\mathbb{C})^4$ noncommutative AW components. Multiple sectors share EP support (S3, S4, S6, S7), with $M_2$ components distributed across them.

**C2 — Hybrid projectors.** S6 (ep+eo, 39-dim, k=4) and S7 (cp+ep+co+eo, 66-dim, k=4) span multiple blocks. S6 is the primary hub (degree 5), S7 the secondary (degree 3). Both are transport-active — they route composition paths between pure-EP, pure-EO, pure-CP, and pure-CO sectors.

**C3 — Block-preserving dynamics.** $\rho = \rho_{\text{cp}} \oplus \rho_{\text{ep}} \oplus \rho_{\text{co}} \oplus \rho_{\text{eo}}$ is block-diagonal by construction. Lemma 1 applies.

**5 T7 pairs** ([`paper_data.md`](paper_data.md) §7.2):

| Pair | Block support | Mediation path |
|------|--------------|----------------|
| S2(eo) ↔ S4(ep+co) | eo $\cap$ (ep+co) = $\emptyset$ | S2 → S6 → S4 |
| S3(ep+eo) ↔ S9(cp+co) | (ep+eo) $\cap$ (cp+co) = $\emptyset$ | S3 → S7 → S9 |
| S4(ep+co) ↔ S5(eo) | (ep+co) $\cap$ eo = $\emptyset$ | S4 → S6 → S5 |
| S4(ep+co) ↔ S8(cp) | (ep+co) $\cap$ cp = $\emptyset$ | S4 → S9 → S8 |
| S6(ep+eo) ↔ S9(cp+co) | (ep+eo) $\cap$ (cp+co) = $\emptyset$ | S6 → S7 → S9 |

All 5 T7 pairs are **cross-block** (disjoint block support). All are mediated through the S6–S7 hub complex. Zero within-block T7 pairs.

**7 curvature channels** — all **within-block** (share at least one block). Zero cross-block curvature channels. Curvature is block-preserving at scale, exactly as the S₃ prototypes predict.

**S1 is NOT T7.** S1 (V₁, 20-dim, cp+ep) has K = κ₀ = κ₁ = 0 with all other sectors, but it is a genuine $G$-invariant subrepresentation — no composition path exists. This is subrepresentation isolation, not T7.

![Figure 5: Hybrid Bridge Topology — Cross-Block Accessibility Exists ONLY Through Hybrids](../../figures/fig5_hybrid_bridge.png)
*Figure 5: Hybrid bridge topology at 9-sector resolution. Block ambient fields (EP: red glow left, CP: indigo glow right, EO: teal top, CO: amber bottom). The Lie Barrier wall (center) separates blocks — direct edges (thin gray-blue) are sparse and block-preserving. T7 pairs (thick glowing red arcs) are all cross-block, mediated through the S6/S7 hub complex. Pie-chart nodes = hybrid sectors (multi-block support). Inset (right): removing S6 and S7 disconnects the graph into 3 isolated components — all cross-block paths vanish. Hybrid sectors are the sole bridges between blocks.*

### 6.4 Scale Comparison

| Property | S₃ nat⊕reg | S₃ reg⊕reg | Rubik |
|----------|-----------|-----------|-------|
| Dimension | 9 | 12 | 228 |
| Sectors | 5 | 10 | 9 |
| Blocks | 2 (nat, reg) | 2 (reg, reg) | 4 (CP, EP, CO, EO) |
| Curvature (κ₁ > 0) | 0 (no M₂) | 10 (within-block) | 7 (within-block) |
| T7 pairs | 3 (cross-block) | 9 (cross-block) | 5 (cross-block) |
| Perfect separation? | T7-only | Yes | Yes (0 cross-block curvature) |
| M₂ present? | No | Yes | Yes (A_EP ≅ M₂⁴ ⊕ M₁⁴) |

The structural identity across three orders of magnitude of dimension is the evidence that C1–C3 capture the essential mechanism. The Rubik's cube is not a new phenomenon — it is the S₃ mechanism realized at scale with richer block structure and richer curvature.

---

## 7. Part V — The Structure Behind T7: Two Accessibility Principles

The preceding sections established the T7 phenomenon at three scales. This section steps back and asks: **what kind of mathematical structure does T7 reveal?**

The answer emerges from the data the paper has already assembled. The primitive sectors with their transport channels (§3) form a natural compositional structure. The Lie accessibility hierarchy (§3–4) forms a parallel, but strictly poorer, structure. The gap between them — exactly the T7 pairs — is not an isolated curiosity. It is a structural mismatch between two fundamentally different ways of generating accessibility.

### 7.1 Two Generation Principles

The paper's data organizes around a central dichotomy — not in the group, not in the representation, but in **how accessibility is generated:**

| | Infinitesimal accessibility | Compositional accessibility |
|---|---|---|
| **Generators** | $A_g = \log\rho(g)$ | $\rho(g)$ |
| **Operation** | Lie bracket $[A_g, A_h]$ | Concatenation through sector projectors $P_\gamma$ |
| **Geometry it probes** | Tangent space of group orbit | Global projector geometry |
| **Block crossing** | Forbidden (Lemma 1) | Enabled (hybrid bridge, C2) |
| **Increasing reach** | Iterated commutators ($d = 0, 1, 2, \ldots$) | Path length ($n = 1, 2, \ldots$) |
| **What it sees** | Infinitesimal structure **inside** blocks | Projector-mediated composition **across** blocks |

The continuous limit — the standard mathematical tool for smooth control — replaces $\rho(g)$ with its logarithm $A_g$. This collapses projector-mediated bridges into block-diagonal operators. Infinitesimal accessibility is structurally blind to cross-block composition. **Compositional accessibility restores the channels that the continuous limit annihilates.**

This is not a failure of the Lie algebra — infinitesimal accessibility is perfectly adequate for within-block transport. It is a mismatch between two generation principles, neither fully reducible to the other.

### 7.2 The Data Naturally Forms a Transport Category

The objects and morphisms studied throughout this paper satisfy the axioms of a category — a fact that is not imposed but observed:

- **Objects** are the primitive sectors $\{E_\alpha\}$ (§2.2). These have been the paper's basic entities from the start.
- **Morphisms** are nonzero transport channels: a morphism $\alpha \to \beta$ exists when $\max_g \|P_\alpha \rho(g) P_\beta\|_F > 0$ (§3.1). This is exactly the transport tensor $K_{\alpha\beta}$ — the data Paper II computed.
- **Composition** is concatenation: applying $\rho(g_1)$, projecting onto an intermediate sector $P_\gamma$, then applying $\rho(g_2)$ (§5.1). The resulting operator $P_\alpha \rho(g_1) P_\gamma \rho(g_2) P_\beta$ is a morphism of length 2.

Call this category $\mathcal{T}$ — the **transport category.** It is the natural algebraic structure whose objects are spectral sectors and whose morphisms are the transport channels between them. The star topology (S6/S7 as hubs, S1 isolated), the block grading ($V = \bigoplus_b V_b$ inherited by every object), and the distinction between pure and hybrid objects — all of these are properties of $\mathcal{T}$ established in §§2–6.

### 7.3 The Lie Sublayer

The Lie accessibility data (§3–4) forms a sub-structure within $\mathcal{T}$. Consider only those transport channels realizable by Lie algebraic operations:

- A Lie channel $\alpha \to \beta$ exists when $P_\alpha C P_\beta \neq 0$ for some $C$ in the span of iterated commutators of the $A_g$.
- These channels are exactly the union of direct ($K$), gradient ($\kappa_0$), curvature ($\kappa_1$), and all higher-depth $\kappa_d$ edges.

Call this sub-structure $\mathcal{L}$ — the **Lie sublayer** of $\mathcal{T}$. It has the same objects but fewer morphisms. Lemma 1 (§4.1) acquires its structural meaning here: **$\mathcal{L}$ is block-preserving.** Every morphism in $\mathcal{L}$ connects objects that share at least one block.

### 7.4 Composition Beyond Lie: The Compositional Completion

The Lie sublayer $\mathcal{L}$ does not exhaust $\mathcal{T}$. Consider all channels reachable by finite-length composition paths through intermediate sectors — the **compositional completion**, denoted $\overline{\mathcal{T}}$:

$$\alpha \xrightarrow{g_1} \gamma_1 \xrightarrow{g_2} \cdots \xrightarrow{g_n} \beta$$

A channel $\alpha \to \beta$ exists in $\overline{\mathcal{T}}$ if at least one such path, of any length, yields a nonzero operator. The Lie sublayer is contained in the compositional completion:

$$\mathcal{L} \;\subset\; \overline{\mathcal{T}}$$

Any Lie monomial $C$ can be approximated by group compositions via the exponential map, so every Lie channel is a composition channel. But the containment is strict: $\overline{\mathcal{T}}$ contains channels that no element of the Lie algebra can realize — the cross-block composition paths through hybrid sectors.

**The mediating role of hybrid objects.** Every cross-block composition path must pass through a hybrid object — a sector whose projector has nonzero restriction to multiple blocks (§2.5). Hybrid objects are the bridges: they carry irreducible content from both blocks, enabling paths where $\mathcal{L}$ sees only a block boundary and terminates.

### 7.5 T7 as the Structural Gap

The T7 phenomenon is the gap between $\mathcal{L}$ and $\overline{\mathcal{T}}$:

$$\text{T7 pairs} = \{\text{channels present in } \overline{\mathcal{T}} \text{ but absent in } \mathcal{L}\}$$

Every T7 pair is a cross-block composition channel with no Lie counterpart — at any commutator depth. Concretely: S2(eo) can reach S4(ep+co) through S6, but no element of the Lie algebra, no iterated commutator, no finite sum of Lie monomials can couple them directly.

The inclusion $\mathcal{L} \subset \overline{\mathcal{T}}$ decomposes cleanly:

$$\overline{\mathcal{T}} = \bigoplus_b \overline{\mathcal{T}}|_b \;\oplus\; \text{T7}(\overline{\mathcal{T}})$$

Within each block, $\mathcal{L}$ and $\overline{\mathcal{T}}$ coincide — Lie accessibility equals compositional accessibility. The entire gap is cross-block. T7 pairs are the sole structural difference between infinitesimal and compositional generation.

**S₁ is not T7.** The $G$-invariant subrepresentation (V₁, 20-dim) has no transport channels — in $\mathcal{L}$ or $\overline{\mathcal{T}}$ — to any other sector. It is genuinely disconnected, not a Lie-vs-composition gap.

### 7.6 Connection to Classical Controllability

This structure reframes a classical result. The Lie algebraic rank condition (Brockett 1973, Sussmann-Jurdjevic 1972) tests controllability via iterated Lie brackets of vector fields — exactly the Lie sublayer $\mathcal{L}$. The compositional completion $\overline{\mathcal{T}}$ tests accessibility via finite group composition — the concatenation of generator actions through sector projectors.

For block-diagonal representations, the Lie rank condition is necessary but not sufficient for full accessibility. T7 pairs are the channels that pass the compositional test but fail the Lie test — invisible to the standard controllability criterion. **The compositional completion $\overline{\mathcal{T}}$, not the Lie sublayer $\mathcal{L}$, is the correct accessibility structure.**

---
## 8. Discussion

### 8.1 Summary

1. **Accessibility hierarchy.** Four layers — direct (K), gradient (κ₀), curvature (κ₁), composition (T7) — with strictly increasing reach. The first three are Lie-accessible (via $A_g$, $[A_g, A_h]$, and higher commutators); the fourth transcends Lie.

2. **Lie is block-preserving (Lemma 1).** Every Lie monomial inherits the block-diagonal structure of $\rho(g)$. Cross-block Lie transport is identically zero at all depths — a structural theorem, not a numerical observation.

3. **Curvature freezes at the block boundary.** Seven pure curvature channels ($\kappa_0 \approx 0$, $\kappa_1 > 0$) — all share block support. Commutators generate curvature within block interiors but are annihilated at the block boundary: every Lie monomial is block-diagonal (Lemma 1). Curvature enriches within-block accessibility; it cannot breach the wall.

4. **T7 = composition-only cross-block accessibility.** Five T7 pairs in the Rubik cube, three in S₃ nat⊕reg, nine in S₃ reg⊕reg — all cross-block, all composition-mediated through hybrid sectors.

5. **S₃ is the minimal prototype.** T7 exists at 9 dimensions with zero M₂ curvature, proving T7 and M₂ are independent. S₃ reg⊕reg achieves perfect separation at 12 dimensions.

6. **The Rubik cube is the large realization.** Same C1–C3 mechanism, verified at 9-sector resolution. Richer block structure and richer curvature, but the fundamental logic is identical.

### 8.2 What Is NOT Claimed

| Claim | Status |
|-------|--------|
| The continuous limit is computationally useful | **Not claimed.** The κ_d hierarchy is a structural diagnostic, not an algorithm. |
| T7 is universal for all finite groups | **Not claimed.** Proved for systems satisfying C1–C3. Generality conditions are open. |
| The four-level hierarchy applies to all control systems | **Not claimed.** It applies to finite group representations with symmetric generator sets and block structure. |
| Phase-conditioned policies outperform existing solvers | **Not claimed.** This is a structural theorem paper, not a solver competition. |
| There is a "directed transport barrier" | **Disproved** — κ is symmetric to $10^{-15}$. Earlier claims of one-way barriers were state-preparation artifacts. |

### 8.3 Open Directions

1. **C1 necessity — Conjecture.** For a block-diagonal representation $\rho = \rho_A \oplus \rho_B$, if there is no irreducible representation $\tau$ appearing in both $\rho_A$ and $\rho_B$, then no composition-only transport exists across the two blocks. Equivalently: every spectral hybrid (a primitive sector spanning both blocks arising from eigenvalue coincidence in the commutative center $Z$) is transport-inert. This is proved for abelian and isotypic cases, and verified on all small-group examples tested (S$_3$, Q$_8$, S$_4$, Z$_2\times$Z$_2$), but a general proof would require a deep representation-theoretic rigidity argument (bicommutant structure, Jacobson density) that lies beyond the scope of this paper. The characterization conjecture (T7 $\iff$ C1–C3) is conditional on C1 necessity; C2 and C3 are proved necessary (§5.4).

2. **Generator-set universality of T7.** T7 pair count may vary with generator set, but the cross-block structural property is conjectured $S$-invariant. Verified for 3 $S$ choices on Rubik; general proof open.

3. **Categorical connections.** The transport category $\mathcal{T}$ (§7) and its block-stratified inclusion $\mathcal{L} \hookrightarrow \overline{\mathcal{T}}$ suggest natural connections to fusion categories (Frobenius-Perron dimension on morphism spaces), $\mathbb{C}[G]$-bimodule categories, and obstruction theory for inclusion functors. The compositional completion $\overline{\mathcal{T}}$ may correspond to well-known categorical constructions under appropriate conditions.

4. **Beyond two blocks.** The current theorem assumes two blocks (A, B). Multi-block representations (Rubik has 4) create a richer T7 graph — each cross-block pair is a T7 candidate. The generalization is straightforward but unformalized.

5. **Connection to quantum superselection.** The block-preserving Lie closure is structurally analogous to superselection rules: observables (Lie generators) cannot couple distinct superselection sectors (blocks). The discrete composition exception (T7) — a finite-group analogue of ancilla-mediated operations — suggests that projector geometry can bypass tangent-space restrictions. This connection is noted as structural analogy only; no quantum-mechanical claim is made.

---

## 9. Concluding Perspective

Classical geometric control theory studies accessibility through the tangent structure of the system: Lie brackets of vector fields generate reachable directions, and the Lie algebraic rank condition is the standard test for controllability. This paper has shown that for finite group representations with block-diagonal structure, the tangent picture is systematically incomplete.

The reason is structural, not technical. The Lie algebra $\mathcal{L} = \text{Lie}\{A_g\}$ captures the infinitesimal geometry of the group orbit — what the dynamics can achieve through smooth, continuous deformation. But a finite group action also possesses **projector geometry**: the way sector projectors $\{P_\alpha\}$ partition the representation into subspaces that the group elements map between. This projector geometry is invisible to the tangent structure. The logarithm $A_g = \log\rho(g)$ erases it: block-diagonal projectors are collapsed, hybrid projectors are annihilated, and the cross-block composition paths that hybrid sectors mediate are frozen out of the Lie algebra entirely.

Accessibility is therefore not purely infinitesimal. The compositional completion $\overline{\mathcal{T}}$ — reached by concatenating $\rho(g)$ actions through sector projectors — contains morphisms that no element of the universal enveloping algebra $\mathcal{U}(\mathcal{L})$ can realize. These are the T7 pairs: cross-block channels that exist in the discrete transport category but are absent from the Lie sublayer at every commutator depth. They are not an edge case, not a numerical artifact, and not specific to the Rubik's cube. They arise in S$_3$ nat$\oplus$reg (9 dimensions), S$_3$ reg$\oplus$reg (12 dimensions), and the Rubik cube (228 dimensions) — three systems spanning two orders of magnitude — governed by the identical structural conditions C1–C3.

The general lesson is that **composition introduces genuinely new morphisms.** The Lie algebra is the tangent approximation to the group; the compositional completion is the group itself, measured through the projector geometry of its spectral decomposition. The two coincide within each invariant block, where the logarithm faithfully captures the connectivity. They diverge at the block boundary, where only finite composition — concatenating group elements through hybrid projectors — can bridge what the continuous limit freezes.

**The continuous limit is structurally incomplete.** Not approximately — structurally. For any system satisfying C1–C3, the Lie algebraic accessibility test will declare certain reachable states unreachable, because the test operates in the tangent category $\mathcal{L}$ while the true accessibility lives in the compositional completion $\overline{\mathcal{T}}$. The gap between them — the T7 pairs — is the measure of the continuous limit's blindness to projector geometry.

---

## Appendix A. Terminology and Accessibility Classes

This appendix collects the formal definitions of all accessibility types and structural objects introduced in the paper. Each term is a defined mathematical object, not an informal label.

### A.1 Accessibility Edges

**Direct edge.** An ordered pair of primitive sectors $(\alpha, \beta)$ with $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F > 0$. Direct edges are the transport graph (Paper II); all are within-block (Lemma 0).

**Gradient edge.** A pair $(\alpha, \beta)$ with $\kappa_0(\alpha,\beta) = \max_g \|P_\alpha A_g P_\beta\|_F > 0$. Gradient edges are the first Lie-accessible layer; they always include all direct edges ($K > 0 \implies \kappa_0 > 0$). All are within-block.

**Curvature edge.** A pair $(\alpha, \beta)$ with $\kappa_0(\alpha,\beta) \approx 0$ but $\kappa_1(\alpha,\beta) = \max \|P_\alpha [A_g, A_h] P_\beta\|_F > 0$. Curvature edges are *pure* Lie phenomena — channels created by commutators that individual generators cannot open. All are within-block.

**Lie-accessible pair.** A pair $(\alpha, \beta)$ with $\kappa_d(\alpha,\beta) > 0$ for some finite depth $d \geq 0$. The union of all direct, gradient, curvature, and higher-depth edges.

### A.2 Composition-Only Transport

**T7 pair (Composition-Only).** A pair $(\alpha, \beta)$ satisfying:
1. $K_{\alpha\beta} = 0$
2. $\kappa_d(\alpha,\beta) = 0$ for all $d \geq 0$
3. $\exists$ a finite composition path $P_\alpha \rho(g_1) P_{\gamma_1} \cdots P_{\gamma_n} \rho(g_{n+1}) P_\beta \neq 0$

T7 pairs are Lie-inaccessible at all depths but reachable via discrete composition through hybrid sectors. All T7 pairs are cross-block. "T7" is retained as shorthand; the formal object is the composition-only pair (§1.2.1).

### A.3 Sector Types

**Pure sector.** A primitive sector $E_\alpha$ with projector supported in exactly one invariant block: $P_\alpha|_{V_A} \neq 0$ and $P_\alpha|_{V_B} = 0$ for all $B \neq A$.

**Hybrid sector.** A primitive sector $E_\gamma$ with projector having nonzero restriction to more than one invariant block: $P_\gamma|_{V_A} \neq 0$ and $P_\gamma|_{V_B} \neq 0$ for at least two distinct blocks $A \neq B$ (§2.5).

**Transport-active hybrid.** A hybrid sector $\gamma$ satisfying $\exists \alpha \subset V_A, \beta \subset V_B : K_{\alpha\gamma} > 0$ and $K_{\gamma\beta} > 0$. Equivalently: $\text{Supp}(E_\gamma) \cap \text{Supp}(E_\alpha) \neq \emptyset$ and $\text{Supp}(E_\gamma) \cap \text{Supp}(E_\beta) \neq \emptyset$.

**Inert hybrid.** A hybrid sector that fails the transport-active criterion — hybrid by block support but sharing no irreducible content with sectors in both blocks. Arises from eigenvalue coincidence without shared irrep geometry.

### A.4 Accessibility Hierarchy

$$\text{Direct} \subset \text{Gradient} \subset \text{Curvature} \subset \text{Lie closure} \subsetneq \text{Composition}$$

All Lie levels (direct through closure) are block-preserving (Lemma 1). Only composition (T7) bridges blocks. Cross-block transport lives exclusively in the composition layer.

### A.5 Key Structural Objects

| Object | Definition | Reference |
|--------|-----------|-----------|
| $A$ | $A = \frac{1}{|S|}\sum\rho(s)$ | Paper I |
| $P_\alpha$ | Primitive sector projector (Center joint diagonalization) | §2.2 |
| $A_g$ | $A_g = \log\rho(g)$ (principal matrix logarithm) | §2.4 |
| $K_{\alpha\beta}$ | $\max_g\|P_\alpha \rho(g) P_\beta\|_F$ | Paper II, §3.1 |
| $\kappa_0(\alpha,\beta)$ | $\max_g\|P_\alpha A_g P_\beta\|_F$ | §3.2 |
| $\kappa_1(\alpha,\beta)$ | $\max_{g,h}\|P_\alpha [A_g, A_h] P_\beta\|_F$ | §3.3 |
| $\kappa_d(\alpha,\beta)$ | $\max\|P_\alpha C_d P_\beta\|$ for depth-$d$ Lie monomials $C_d$ | §3.4 |
| $\text{Supp}_{\text{nc}}(\alpha)$ | $\{b : P_\alpha|_b \neq 0 \land \|[QT^0,QT^1]\|_b > 0\}$ | Paper II, §2.3 |
| $\text{Supp}(E_\alpha)$ | $\{\tau \in \hat{G} : \text{Tr}(P_\alpha \Pi_\tau) > 0\}$ | §5.2 |
| $\mathcal{L}$ | $\mathcal{L} = \text{Lie}\{A_g\}_{g \in S}$ (Lie algebra); also denotes the Lie subcategory (§7.2) | §2.4, §7.2 |
| $\mathcal{T}$ | Transport category: objects = primitive sectors, morphisms = nonzero transport | §7.1 |
| $\overline{\mathcal{T}}$ | Compositional completion: morphisms via finite composition paths through hybrid objects | §7.3 |

---

## Appendix B. Numerical Data Reference

All numerical values in this paper are sourced from [`paper_data.md`](paper_data.md) — the single source of truth for the trilogy. Key sections referenced:

| § in paper_data.md | Content |
|-------------------|---------|
| §1 | Total space (228 = CP64 + EP144 + CO8 + EO12) |
| §2 | Block structure and noncommutativity |
| §3 | 6 canonical layers (A_18 eigenspaces) |
| §4 | 9 primitive sectors (Center joint diagonalization) |
| §5 | Transport topology (K matrix, 10 direct edges, hub degrees) |
| §6 | Lie accessibility (κ₀, κ₁, κ₂ matrices; 3 classes) |
| §7 | T7 pairs (5 cross-block, S1 isolation) |
| §8 | EP algebra (A_EP ≅ M₂(ℂ)⁴ ⊕ M₁(ℂ)⁴) |
| §9 | S₃ prototypes (nat⊕reg: T7-only; reg⊕reg: perfect separation) |
| §10 | Fundamental identities (expm fidelity, κ symmetry) |
| §11 | Generator-set universality |

## Appendix C. Minimal S₃ Prototypes

This appendix collects the complete numerical data for the S₃ prototype systems — the minimal working realizations of the T7 mechanism. These are the most important sanity checks in the trilogy: every structural claim (C1–C3, Lie freezing, T7 existence, T7/M₂ independence) is verified in at least one of these systems.

### C.1 S₃ nat⊕reg — 9-dim, T7 Without Curvature

$G = S_3$ (order 6), $\rho = \rho_{\text{nat}} \oplus \rho_{\text{reg}}$ (3-dim natural + 6-dim regular), $S =$ all 6 group elements, $Z = \langle A_{\text{full}}, A_{\text{trans}}\rangle$.

**5 primitive sectors:**

| Sector | Dim | Type | Block support | A_full | A_trans |
|--------|-----|------|--------------|--------|---------|
| S1 | 2 | Pure-reg | reg | 1.0 | 0.0 |
| S2 | 1 | Pure-reg | reg | 0.0 | 1.0 |
| S3 | 1 | Pure-nat | nat | 0.0 | −0.577 |
| S4 | 1 | Pure-reg | reg | 0.0 | 0.577 |
| S5 | 4 | **Hybrid** | nat+reg | 0.0 | 0.0 |

**Key results:**
- 14 direct edges — all within-block or pure↔hybrid
- Curvature pairs ($\kappa_0=0, \kappa_1>0$): **0** — no M₂ in this system
- **T7 pairs: 3** — S1↔S3, S2↔S3, S3↔S4 (all cross-block nat↔reg, mediated through S5)
- C1: S₃ standard 2-dim irrep appears in nat (×1) and reg (×2). ✓
- C2: S5 is a transport-active hybrid — carries the standard irrep from both blocks. ✓
- C3: $\rho$ is block-diagonal by construction. ✓
- **κ₁ = 0 everywhere** — T7 exists without curvature, proving T7/M₂ independence.

### C.2 S₃ reg⊕reg — 12-dim, Perfect Separation

$G = S_3$, $\rho = \rho_{\text{reg}} \oplus \rho_{\text{reg}}$, $S =$ {3 transpositions}, $Z = \langle A_3, A_2\rangle$.

**10 primitive sectors:** 5 pure-A + 4 pure-B + 1 hybrid (S10 = A:1 + B:1).

**Perfect separation — zero counterexamples:**

| Type | Count | Location |
|------|-------|----------|
| Gradient edges (κ₀ > 0) | 30 | **All** within-block |
| Curvature pairs (κ₀=0, κ₁>0) | 10 | **All** within-block |
| T7 pairs (K=κ₀=κ₁=0) | 9 | **All** cross-block |

The three accessibility types are perfectly aligned with block structure. The hybrid sector S10 is the sole bridge — all 9 T7 paths go through it.

### C.3 S₃ "False T7" — Inert Hybrid Counterexample

Standard vs. trivial$\oplus$sign representation pair: eigenvalue coincidence creates a hybrid projector spanning both blocks, but without a shared irrep the hybrid fails the computable C2 criterion ($\text{Tr}(P_\alpha \Pi_\tau) = 0$ for all $\tau$ common to $\alpha$ and $\beta$). `has_path=False`. This confirms that C1 (shared noncommutative support) is necessary — hybrid block support alone is insufficient.

---

## Appendix D. The N=2 Pocket Cube as a T7-Free Negative Control

The N=2 pocket cube (2x2x2) has only corner pieces — no edges, no centers. Its state space is the subgroup $G_2 = (S_8 \wr \mathbb{Z}_3^7) \subset G_3$ (corners only, no edge subsystem). The corresponding group representation decomposes as:

$$\rho_{\text{N=2}} = \rho_{\text{cp}} \oplus \rho_{\text{co}}, \quad \dim V = 64 + 8 = 72$$

with no ep or eo blocks. Since the ep block is the primary carrier of noncommutativity in N=3 ($\|[QT^0, QT^1]\|_{\text{ep}} = 2.74$, 93.9% of total), removing it tests whether the co block's residual noncommutativity ($\|[QT^0, QT^1]\|_{\text{co}} = 0.61$) is sufficient to generate hybrid sectors and T7 pairs.

The representation is constructed by extracting the cp (0:64) and co (208:216) diagonal blocks from the N=3 228-dimensional $\rho(g)$ matrices. This yields a faithful restricted representation of $G_2$: block-diagonal by construction (C3 satisfied), unitary for all 18 face-turn generators, and with invariant cp/co splitting ($\rho[:64,64:] = 0$ exactly for all $g$). The same 18 face-turn generators and the same Center$\{A_{18}, QT_{\text{all}}, HT_{\text{all}}\}$ joint diagonalization are used, ensuring direct comparability with the N=3 analysis.

### Results

**Spectral structure.** $A_{18}$ has 5 distinct eigenvalues, all rational: $\lambda = 1$ (8), $2/3$ (2), $5/9$ (27+27, two eigenspaces with degenerate QT/HT split), $1/3$ (35). The $k=2$ eigenvalue layer ($\lambda = 7/9$), which in N=3 comes from edge structure, is absent. Spectral rationality — the arithmetic phenomenon established in Paper I — survives.

**Noncommutativity.** $\|[QT^0, QT^1]\|_{\text{total}} = 0.61$, entirely from the co block ($\|[QT^0, QT^1]\|_{\text{cp}} = 0$ exactly, $\|[QT^0, QT^1]\|_{\text{co}} = 0.61$). The co noncommutativity is identical to N=3's co block value — the corner system's group algebra retains the same noncommutative component. **Noncommutativity survives but is trapped in the co block.**

**Primitive sectors: 21 total, zero hybrid.** Center$\{A_{18}, QT_{\text{all}}, HT_{\text{all}}\}$ joint diagonalization yields 21 primitive sectors: 15 pure-cp and 6 pure-co. **No sector spans both blocks.** Compare N=3: 9 sectors, 3 hybrid (S6: ep+eo, S7: cp+ep+co+eo, S1: cp+ep). The ep block is the structural ingredient that enables joint eigenspaces of the center operators to cross cubie-type boundaries.

**Transport.** The K matrix has 75 nonzero edges — dense within each block (15 cp sectors fully connected, 6 co sectors fully connected) — but **zero cross-block transport** ($K_{ij} = 0$ for all cp×co index pairs). $\kappa_0$ edges: 75 (all within-block). Pure curvature pairs ($\kappa_0 \approx 0$, $\kappa_1 > 0$): 4 (N=3: 7).

**T7 candidates: 90, all isolated.** The 15 cp $\times$ 6 co = 90 cross-block pairs all satisfy $K = \kappa_0 = \kappa_1 = 0$. All 90 have has_path=False: no composition path exists because no hybrid sector can serve as an intermediate bridge. These 90 pairs are genuine $G$-invariant subrepresentation isolation (structurally analogous to S1 in N=3 — a decoupled commutative subspace), not T7.

### The C1–C3 diagnostic

| Condition | N=2 Status | N=3 Status |
|-----------|-----------|-----------|
| C1 (shared noncommutative support) | **Partial** — co block has $|[QT^0,QT^1]| = 0.61$, but only one block has non-zero noncommutativity | cp: 0, ep: 2.74, co: 0.61, eo: 0.79 |
| C2 (transport-active hybrid projector) | **FAILS** — 0 hybrid sectors | **Satisfied** — S6, S7 hybrid hubs |
| C3 (block-preserving dynamics) | **Satisfied** — $\rho$ block-diagonal by construction | **Satisfied** — $\rho$ block-diagonal by construction |

The N=2 system satisfies C3 and partially satisfies C1, but fails C2 decisively: there are zero hybrid projectors. The failure mechanism is instructive: noncommutativity exists (in the co block), but without the ep block's $M_2(\mathbb{C})^4$ structure, this noncommutativity cannot generate joint eigenspaces of the center operators that span across cubie-type boundaries.

**The N=2 negative control demonstrates that noncommutativity alone is not sufficient for hybridization. The decisive ingredient is whether the noncommutative structure can generate joint eigenspaces crossing invariant block boundaries.**

### Interpretation

**The ep block is necessary (not just sufficient) for transport-active hybrid formation.** The co block alone carries non-zero noncommutativity ($\|[QT^0,QT^1]\| = 0.61$) but this is insufficient to create hybrid projectors. Removing the ep block removes all hybrid sectors. Removing the co block (leaving cp+ep+eo) would preserve hybrid sectors — the cp+ep+eo subsystem has the same 3 hybrid sectors as the full N=3 system (since S6 is ep+eo and S7 is cp+ep+co+eo). The ep block's $M_2$-active noncommutativity is the "glue" that mixes across cubie-type boundaries.

**C1 strength matters.** The co block's noncommutativity (0.61) is non-zero but structurally weaker than the ep block's (2.74). The $M_2(\mathbb{C})$ simple components of the ep Artin-Wedderburn decomposition provide the algebraic mechanism for boundary-crossing joint eigenspaces. C1 is not a binary yes/no condition — it has internal structure (which irreps appear, at what multiplicity, with what noncommutativity strength). The N=2 negative control shows that the specific irreps and multiplicities of the ep block are the relevant structure for satisfying C2.

**N=2 is the minimal T7-free model.** It is the smallest group representation (within the Rubik's cube family) where the entire framework — spectral decomposition, primitive sector decomposition, K matrix, $\kappa$ hierarchy — is well-defined but T7 = 0. This provides a clean negative control: T7 is not an automatic consequence of the representation formalism, but requires the specific algebraic structure supplied by multi-block noncommutative support.

**Qualitative emergence between N=2 and N=3.** The transition from N=2 to N=3 is not quantitative but structural: hybrid sectors (0 $\to$ 3) and T7 pairs (0 $\to$ 5) emerge discontinuously once the edge subsystem is present. In N=2, the co block's noncommutativity is algebraically isolated — it deforms the QT/HT eigenspaces within the co block but cannot connect across the cp/co boundary. Adding the ep block (144 dimensions of $M_2(\mathbb{C})^4$ noncommutative structure) does not merely "add more noncommutativity" — it introduces a qualitatively new algebraic object (the ep-co hybrid projector S7, and the ep-eo hybrid projector S6) that bridges the block boundary. This is a discrete analogue of a phase transition in the projector geometry: below the threshold (no $M_2$-active block), the center's joint eigenspaces respect block boundaries exactly; above the threshold, boundary-crossing joint eigenspaces emerge.

This unification — Lie failure, curvature, and T7 all rest on projector geometry — is the paper's central structural claim.

**Corollary for the T7 Theorem.** C2 (transport-active hybrid projector) requires at least one $M_2$-active block — noncommutativity confined to a single block, even if non-zero, cannot satisfy C2. This strengthens the C1 $\rightarrow$ C2 $\rightarrow$ C3 logical chain by specifying what kind of C1 is needed.

### Comparison with N=3

| Property | N=2 (72-dim) | N=3 (228-dim) |
|----------|-------------|--------------|
| $A_{18}$ eigenvalues | 5 (all rational) | 6 (all rational) |
| Primitive sectors | 21 | 9 |
| Hybrid sectors | **0** | 3 |
| $K$ edges (nonzero) | 75 (within-block only) | 10 (sparse) |
| Cross-block $K$ | 0 | 0 |
| $\kappa_0$ edges | 75 | 10 |
| Pure curvature ($\kappa_1 > 0$, $\kappa_0 = 0$) | 4 | 7 |
| T7 pairs (true) | **0** | 5 |
| $\|[QT^0, QT^1]\|_{\text{co}}$ | 0.61 | 0.61 |
| $\|[QT^0, QT^1]\|_{\text{ep}}$ | N/A | 2.74 |

**Code**: [test/exploratory/_exp_n2_pocket_cube.py](../test/exploratory/_exp_n2_pocket_cube.py)

---

## References

**Mathematical lineage.** This paper belongs to the tradition of **Lie algebraic controllability and geometric accessibility theory** — the Brockett-Jurdjevic-Sussmann program of understanding nonlinear controllability through Lie brackets of the accessibility algebra. The κ_d hierarchy (§4) is a discrete-group analogue of the sequence of accessibility distributions; the Composition-Only Transport Theorem (T7, §5) establishes that discrete composition transcends the continuous accessibility algebra — a structural mismatch that has no analogue in the classical (continuous) theory. The lineage runs: Lie algebraic controllability (Brockett 1973, Sussmann-Jurdjevic 1972) → geometric control on Lie groups (Jurdjevic 1997, Bullo-Lewis 2005) → discrete event and sampled-data controllability (Sastry 1999) → compositional accessibility in finite group representations (this paper).

### Trilogy cross-references

[1] Paper I — *Spectral Sector Decomposition in Finite Group Representations: Primitive Idempotents and Emergent Hybrid Structure from the Rubik Cube Group.* `examples/paper1/Paper I.md`

[2] Paper II — *Noncommutative Transport and Selection Rules in Finite Group Representations: Hybrid Sectors, Permutation Channels, and Global Lifting Constraints.* `examples/paper2/Paper II.md`

[3] `docs/paper_data.md` — Shared Data File: Single Source of Truth for Paper Trilogy (post-ρ-fix 6-layer, 9-sector resolution).

### Lie algebraic controllability and geometric accessibility

[4] R.W. Brockett, "Lie Theory and Control Systems Defined on Spheres." *SIAM Journal on Applied Mathematics* 25(2):213–225, 1973.
  — The foundational paper establishing that Lie brackets of the drift and control vector fields generate the accessibility algebra. The κ_d hierarchy (§4) is a discrete-group analogue: κ₀ = single-generator transport (analogue of the control vector fields), κ₁ = commutator transport (analogue of the first Lie bracket), κ₂ = double-commutator transport (second bracket), and so on. The block-preserving Lemma 1 mirrors the fact that the accessibility distribution respects invariant subspaces under the group action.

[5] H.J. Sussmann and V. Jurdjevic, "Controllability of Nonlinear Systems." *Journal of Differential Equations* 12:95–116, 1972.
  — The orbit theorem: the reachable set from a point is a submanifold whose tangent space is the accessibility algebra evaluated at that point. The central question of this paper — "what can reach what?" — is the discrete-group version of the same question. The answer is structurally different: in the continuous theory, accessibility at all depths is block-preserving; in the discrete theory, composition through hybrid intermediate sectors creates cross-block channels that are invisible to the accessibility algebra.

[6] V. Jurdjevic, *Geometric Control Theory*. Cambridge University Press, 1997.
  — Comprehensive treatment of Lie-algebraic controllability on Lie groups. The structure theory of invariant control systems on Lie groups — drift vector fields, control vector fields, accessibility Lie algebras, and the Chow-Rashevskii theorem — provides the continuous-control framework against which the discrete composition phenomenon (T7) is measured and shown to be strictly richer.

[7] S. Sastry, *Nonlinear Systems: Analysis, Stability, and Control*. Springer, 1999.
  — Sampled-data and discrete-time controllability. The gap between sampled-data controllability and continuous controllability — where sampling can destroy accessibility because the sampling period may alias certain Lie bracket directions — is a known discrete/continuous dichotomy. The T7 phenomenon is a stronger, structure-level version: not merely a sampling artifact but a fundamental mismatch between the algebraic structures of continuous (Lie) and discrete (composition) accessibility.

[8] F. Bullo and A.D. Lewis, *Geometric Control of Mechanical Systems*. Springer, 2005.
  — Lie group representations in geometric control. The connection between group representation structure and accessibility — invariant connections, curvature, and holonomy on configuration manifolds — is the geometric framework from which the κ₁ pure curvature channels (§4.3) draw their conceptual vocabulary.

[9] H. Nijmeijer and A.J. van der Schaft, *Nonlinear Dynamical Control Systems*. Springer, 1990.
  — Accessibility distributions, the Lie algebraic rank condition, and the structure of the reachable set for nonlinear control systems. The iterative construction of the accessibility algebra through Lie bracket closure is the continuous ancestor of the κ_d depth hierarchy.

### Discrete-event and sampled-data control

[10] P.J. Ramadge and W.M. Wonham, "Supervisory Control of a Class of Discrete Event Processes." *SIAM Journal on Control and Optimization* 25(1):206–230, 1987.
  — Foundational paper on supervisory control of discrete event systems. The compositional closure T̄ (§7) — the closure of the transport graph under finite sequences of generator actions, yielding cross-block reachability through hybrid intermediate sectors — is structurally analogous to the supremal controllable sublanguage: both are closures under finite composition of permitted discrete operations that exceed the corresponding continuous approximation.

### Category theory

[11] S. Mac Lane, *Categories for the Working Mathematician*, 2nd ed. Springer, 1998.
  — Standard reference for category theory. The transport category construction in §7 — objects = primitive sectors, morphisms = nonzero transport channels, Lie sublayer as faithful but not full inclusion — uses only the elementary notions of category, functor, and natural transformation. The compositional completion is the categorical closure of the Lie sublayer under finite composition of available morphisms.

### Finite group representations and association schemes

[12] C.W. Curtis and I. Reiner, *Representation Theory of Finite Groups and Associative Algebras*. AMS Chelsea, 1962.
  — Standard reference for Schur's Lemma, isotypic decomposition, commutant algebras, and the Artin-Wedderburn structure theorem. The block decomposition V = V_A ⊕ V_B and the block-preserving property of the Lie algebra (Lemma 1) are consequences of the semisimple structure of the group algebra.

[13] E. Bannai and T. Ito, *Algebraic Combinatorics I: Association Schemes*. Benjamin/Cummings, 1984.
  — Bose-Mesner algebra structure. The primitive sector decomposition (defined in Paper I, used throughout this paper) and the appearance of Krawtchouk-order mixing in the κ₁ pure curvature channels are rooted in the Bose-Mesner algebra of the underlying permutation association schemes.

---

**Code**: [rime/cubieoperator.py](../rime/cubieoperator.py), [test/canonical/_exp_lie_closure_transport.py](../test/canonical/_exp_lie_closure_transport.py), [test/canonical/_exp_minimal_t7.py](../test/canonical/_exp_minimal_t7.py), [test/_exp_paper3_figures.py](../test/_exp_paper3_figures.py), [test/exploratory/_exp_n2_pocket_cube.py](../test/exploratory/_exp_n2_pocket_cube.py)

**Data**: [docs/paper_data.md](../docs/paper_data.md) — definitive numerical source for all three Papers

**Date**: 2026-05-15 (appendices cleaned to A–D: terms, data, S₃ prototypes, N=2 negative control)
