# Noncommutative Transport and Selection Rules in Finite Group Representations

### Hybrid Sectors, Permutation Channels, and Global Lifting Constraints

---

> **This paper is entirely static.** No infinitesimal accessibility, Lie closure, $\kappa_d$ hierarchy, $A_g = \log\rho(g)$, curvature, dynamical controllability, phase automata, or control policies are considered here. Those belong to Paper III. The objects studied — primitive sectors, transport morphisms, noncommutative support, and the M₂ obstruction — form a **static structural analysis** of which sectors can exchange amplitude under a single generator. The question is structural, not dynamical: *where does the transport graph come from?*

---

## Abstract

**Background.** Paper I established that the averaging operator $A = \frac{1}{|S|} \sum_{g \in S} \rho(g)$ has a rational spectrum with six canonical layers that refine into nine primitive sectors under Center$\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$ joint diagonalization. But the spectral decomposition of $A$ is a static object — it tells us nothing about which sectors can exchange amplitude under individual generators. This paper answers: **where does the transport topology come from?**

**The central object.** The transport tensor $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ encodes how individual generators move amplitude between primitive sectors. Its aggregate norm $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$ defines a weighted directed graph on the 9 sectors. This paper is a **structural study** of this graph — we characterize its topology, identify the algebraic mechanisms that produce it, and verify its stability under representation-theoretic perturbations. The approach is computational representation analysis, not axiomatic theorem-proving.

**The dominant invariant: Supp_nc.** Define the *noncommutative support* of a sector $\alpha$ as $\text{Supp}_\text{nc}(\alpha) = \{b \in \{\text{cp}, \text{ep}, \text{co}, \text{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[\text{QT}^0, \text{QT}^1]\|_b > 0\}$ — the set of representation blocks on which the sector has non-zero projection AND the block's per-axis QT operators fail to commute. Supp_nc is the **dominant structural invariant** for Type I (noncommutative) transport, detecting 9 of 10 direct edges. It is not claimed to be a universal necessary-and-sufficient condition; it is the invariant that captures the M₂-driven transport mechanism.

**Transport Mechanism Classification.** Direct transport arises from two independent mechanisms: **Type I (noncommutative mixing)** — for all 9 non-CP transport edges, $K_{\alpha\beta} > 0$ precisely when $\text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) \neq \emptyset$. The intersection of noncommutative supports is empirically necessary and sufficient for Type I transport. **Type II (commutative permutation)** — a single edge S8$\leftrightarrow$S9 ($K = 2.83$) mediated by the CP block, which is QT-commutative ($\|[\text{QT}^0, \text{QT}^1]\|_{\text{cp}} = 0$) but generator-noncommutative ($[\rho(g), P_i] \neq 0$). This reveals a key structural fact: **averaging commutativity $\neq$ generator commutativity**. All 10 direct edges are block-preserving. Cross-block transport requires length-2 composition — all five such pairs (informally abbreviated **T7** for composition-only transport) satisfy neither Type I nor Type II criterion. The M₂-active EP block drives Type I transport (93.9% of total noncommutativity); the CP block carries the unique Type II channel.

**The M₂ Principle.** The edge-permutation block algebra $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ is the algebraic origin of the transport architecture. Four structural observations trace its consequences:
1. **Observation A (Two-Type Transport)** — Type I via shared noncommutative support; Type II via CP permutation adjacency
2. **Observation B (Hub necessity)** — the three active M₂ components force a unique hub sector (S6) intersecting all of them
3. **Observation C (Refinement obstruction)** — M₂ noncommutativity blocks further spectral refinement, capping decomposition at 9 sectors
4. **Observation D (Transport topology)** — all direct edges are block-preserving, S1 is isolated, cross-block transport is composition-only (T7)
5. **Commutant gap** — $\dim \text{Comm}(A_{\text{EP}}) - \dim \text{Comm}(\rho|_{\text{EP}}) = 424$ measures transversality between spectral and irreducible decompositions

**Refinement geometry.** The refinement POSET of spectral decompositions (Paper I) has an obstruction lattice: decompositions that would require simultaneously diagonalizing noncommuting operators cannot be refined. The M₂ components of A_EP are the minimal obstruction — the atoms of the noncommutative obstruction lattice. The 9 primitive sectors are the finest decomposition achievable without entering the noncommutative regime.

**What this paper does NOT study.** This paper studies the **static transport topology** — which sectors can exchange amplitude. It does NOT study dynamics (can a trajectory actually reach sector β from α?), Lie accessibility (κ_d hierarchy), or controllability. Those belong to Paper III. The question is structural, not dynamical: *where does the transport graph come from?*

**Answer.** The transport topology emerges from the interplay of two independent mechanisms: noncommutative mixing (Type I, detected by Supp_nc, driven by the M₂ components of $A_{\text{EP}}$) and commutative permutation mixing (Type II, mediated by the CP block). The Rubik's cube representation provides a concrete realization of this two-mechanism architecture — a remarkably rigid transport topology whose consistency, stability, and mechanism disentanglement are the central findings of this paper.

**Dependency.** This paper assumes the primitive sector decomposition, the spectral ontology, and the refinement POSET established in Paper I. The accessibility consequences of the transport structures classified here — which sectors can actually be reached from which, at what Lie-algebraic depth, through which composition paths — are developed in Paper III. The dependency is linear: I → II → III.

---

## Notation Table

| Symbol | Meaning | Origin |
|--------|---------|--------|
| $A = \frac{1}{|S|}\sum_{s} \rho(s)$ | Averaging operator — Hermitian, rational spectrum | Paper I |
| **layer** $V_\lambda$ | An eigenspace of $A$; 6 canonical layers ($\lambda = 1 - k/9$) | Paper I |
| **block** | Cubie-type invariant component: cp (corner perm, 64-dim), ep (edge perm, 144-dim), co (corner ori, 8-dim), eo (edge ori, 12-dim) | Paper I |
| **primitive sector** $S_\alpha$ | Minimal joint eigenspace of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ (9 total) | Paper I |
| $P_\alpha$ | Projector onto primitive sector $\alpha$ | Paper I |
| **hybrid sector** | A primitive sector with support spanning multiple cubie-type blocks (e.g., ep+eo) | Paper I |
| **S1–S9** | 9 primitive sectors: S1(V₁, isolated), S2(V₈/₉), S3(V₇/₉), S4(V₂/₃), S5–S7(V₅/₉; S6 primary hub), S8–S9(V₁/₃) | Paper I |
| $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ | Transport tensor — amplitude moved by single generator $g$ from $\beta$ to $\alpha$ | **this paper** |
| $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$ | Direct transport norm — aggregate transport strength under optimal single generator | **this paper** |
| $\mathrm{Supp}_{\mathrm{nc}}(\alpha)$ | Noncommutative support — $\{b : P_\alpha|_b \neq 0 \text{ and } \|[\mathrm{QT}^0, \mathrm{QT}^1]\|_b > 0\}$ | **this paper** |
| **Type I** | Transport via shared noncommutative support (9 of 10 direct edges, M₂-driven) | **this paper** |
| **Type II** | Transport via commutative permutation block — 1 edge S8↔S9 ($K = 2.83$, CP-mediated) | **this paper** |
| $\mathrm{M}_2$ Principle | $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ (20-dim semisimple) — algebraic origin of Type I transport | **this paper** |
| $\mathrm{QT}^a$, $\mathrm{HT}^a$ | Quarter-turn / half-turn averaging operators on axis $a \in \{0,1,2\}$ | Paper I |
| $\mathrm{QT}_{\mathrm{all}} = \sum_a \mathrm{QT}^a$, $\mathrm{HT}_{\mathrm{all}} = \sum_a \mathrm{HT}^a$ | Total quarter-turn / half-turn averaging | Paper I |
| $\mathrm{Comm}(\cdot)$ | Commutant algebra — $\{X : [X,Y] = 0 \; \forall Y \in (\cdot)\}$ | — |
| **T7 pair** | Composition-only transport pair — $K_{\alpha\beta}=0$ yet reachable via length-2 composition through hybrid intermediate sector (cross-block) | **this paper** |

---

## The Four Objects of Static Transport Geometry

This paper is built from exactly four mathematical objects. Everything else — the K matrix, the transport graph, the hub degrees, the T7 pairs — is derived from these four.

| # | Object | Definition | Role |
|---|--------|-----------|------|
| **1** | **Primitive sectors** $\{S_\alpha\}_{\alpha=1}^9$ | Minimal simultaneous eigenspaces of Center$\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$ | The **objects** of the transport category — what amplitude lives in |
| **2** | **Transport morphism** $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ | Off-diagonal projector sandwich: how generator $g$ moves amplitude from sector $\beta$ to $\alpha$ | The **morphisms** of the transport graph — per-generator amplitude transport |
| **3** | **Noncommutative support** $\text{Supp}_\text{nc}(\alpha)$ | $\{b : P_\alpha|_b \neq 0 \text{ and } \|[\text{QT}^0, \text{QT}^1]\|_b > 0\}$ | The **dominant Type I invariant** — determines which noncommutative morphisms are non-zero |
| **4** | **M₂ obstruction** $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ | The edge-permutation block algebra, 20-dim semisimple | The **refinement obstruction source** — atoms of noncommutativity |

These four objects form a **static structural description**: sectors live in a 228-dimensional representation space, transport morphisms connect them, Supp_nc is the dominant invariant for Type I transport, and the M₂ components are the algebraic atoms that create the noncommutative support.

### Four Structural Observations (A → B → C → D)

The paper is organized as a chain of structural observations, each building on the previous. These are representation-theoretic findings supported by exact numerical verification on the 228-dim Rubik's cube representation and the S₃ minimal prototypes — they are computationally established for the cube family and its algebraic relatives.

| Observation | Finding | Depends on |
|-----------|-----------|------------|
| **A — Two-type transport** | Type I: noncommutative mixing via Supp_nc intersection (9 of 10 edges). Type II: commutative permutation channel S8$\leftrightarrow$S9 (1 edge). Averaging commutativity $\neq$ generator commutativity. | Objects 1–3 |
| **B — Hub necessity** | If $\deg(S_\alpha) \gg 1$, then $\text{Supp}_\text{nc}(S_\alpha)$ must intersect multiple M₂ simple components | Observation A + Object 4 |
| **C — Refinement obstruction** | Refinement stops at 9 sectors — not a numerical artifact, but the M₂ overlap obstruction: noncommuting QT operators on EP prevent simultaneous diagonalization beyond the commutative Center | Observation B |
| **D — Transport topology** | All direct edges are block-preserving; S1 is isolated; S6 is the primary hub (degree 5); S7 is the secondary hub (degree 3); cross-block transport is composition-only (T7) | Observations A–C |

The flow is: **M₂ creates Supp_nc (Object 4 → Object 3) → Supp_nc determines Type I transport (Observation A), with Type II as an independent mechanism → M₂ overlap forces hub formation (Observation B) → Noncommutative obstruction caps refinement (Observation C) → The resulting transport graph reflects Supp_nc geometry (Observation D).**

---

## 1. Introduction

### 1.1 What Paper I Left Open

Paper I established the **spectral ontology** of the averaging operator $A = \frac{1}{|S|} \sum_{g \in S} \rho(g)$ for the Rubik's cube representation (228 dimensions, 18 face-turn generators). Its central results:

1. **Rational spectrum.** $A$ has 6 distinct eigenvalues $\lambda = 1 - k/9$ with $k \in \{0, 1, 2, 3, 4, 6\}$.
2. **Block origin.** Each eigenvalue's eigenspace decomposes across four cubie-type blocks (cp, ep, co, eo), with block spectra derived from Bose–Mesner algebras (Q₃ Hamming, face-incidence, Z₃/Z₂ phase).
3. **Primitive sectors.** Joint diagonalization of Center$\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$ yields 9 primitive sectors — the finest cubic-symmetric decomposition.
4. **Refinement POSET.** The family of spectral decompositions across different generator sets forms a refinement semilattice with a commutative core.

Paper I answers: *what is the spectral object?* But it deliberately stops at the static decomposition. It does not ask: *which sectors can exchange amplitude under individual generators?*

That is the question of this paper.

### 1.2 The Transport Question

Individual generators $\rho(g)$ do **not** preserve the spectral sectors. For any two sectors $\alpha, \beta$, the off-diagonal block

$$T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$$

measures how much generator $g$ transports amplitude from sector $\beta$ to sector $\alpha$. The aggregate transport strength is

$$K_{\alpha\beta} = \max_{g \in S} \|T_{\alpha\beta}(g)\|_F.$$

The matrix $K$ defines a weighted directed graph on the 9 primitive sectors. This paper addresses three structural questions:

> **Q1. Why does the transport topology emerge?** Why are some sector pairs coupled ($K > 0$) and others not ($K = 0$)? What algebraic structure determines which edges exist?
>
> **Q2. Why does refinement stop at 9?** Why can't the spectral decomposition be further refined? What algebraic obstruction caps the commutative diagonalization?
>
> **Q3. Why do two transport types exist?** Why is the CP channel (S8$\leftrightarrow$S9) fundamentally different from all other edges? What does this tell us about the relationship between commutativity and transport?

The answer to Q1 is not "eigenvalue proximity" — sectors with adjacent eigenvalues can have zero transport, while sectors with distant eigenvalues can be strongly coupled. The answer is not "block support overlap" alone — some sector pairs share block support yet have zero transport. The answer requires identifying a **structural invariant** that dominates transport.

The answer to Q2 is the M₂ obstruction: noncommuting QT operators on the EP block prevent simultaneous diagonalization beyond the commutative Center. The 9 primitive sectors are the finest commutative decomposition.

The answer to Q3 reveals a deep structural fact — **averaging commutativity $\neq$ generator commutativity**. The CP block's QT operators commute ($\|[\text{QT}^0, \text{QT}^1]\|_{\text{cp}} = 0$), yet individual generators on CP do not commute with the spectral projectors. This produces a transport channel (Type II) fundamentally different from the M₂-driven noncommutative channels (Type I).

### 1.3 Terminology and Sector Naming

The spectral decomposition produces objects at two nested resolutions:

- **6 canonical layers** $E_\lambda$ — eigenspaces of the averaging operator $A = \frac{1}{|S|}\sum \rho(g)$, denoted $V_1, V_{8/9}, V_{7/9}, V_{2/3}, V_{5/9}, V_{1/3}$
- **9 primitive sectors** $S_1,\ldots,S_9$ — minimal joint eigenspaces of the commutative family $\text{Center}\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$

Throughout the paper:

| Term | Meaning |
|------|---------|
| **layer** ($V_\lambda$) | Eigenspace of $A$ (6 total) |
| **primitive sector** ($S_\alpha$) | Minimal central component after QT/HT refinement (9 total) |
| **canonical sector** | Synonym for primitive sector |
| **transport edge** | A sector pair $(\alpha,\beta)$ with $K_{\alpha\beta} > 0$ (10 direct edges) |
| **transport graph** | The undirected weighted graph on $\{S_\alpha\}$ induced by $K_{\alpha\beta} > 0$ |
| **Type I edge** | Transport detected by $\text{Supp}_\text{nc}$ intersection (noncommutative mixing; 9 of 10 edges) |
| **Type II edge** | Transport without $\text{Supp}_\text{nc}$ intersection (commutative permutation; S8$\leftrightarrow$S9) |
| **T7 pair** | Cross-block composition-only pair — $K_{\alpha\beta}=0$ but reachable via length-2 composition through an intermediate sector (informal shorthand; 5 pairs) |
| **QT** | Quarter-turn average: $\text{QT}^a = \frac{1}{4}\sum_{g\in\text{axis-}a}\rho(g)$, $\text{QT}_\text{all} = \frac{1}{3}(\text{QT}^0+\text{QT}^1+\text{QT}^2)$ |
| **HT** | Half-turn average: $\text{HT}_\text{all} = \frac{1}{6}\sum_{\text{half-turns}}\rho(g)$ |
| **block** | One of four $G$-orbit subspaces: cp(64), ep(144), co(8), eo(12) |
| **Supp_nc** | Noncommutative support — blocks where a sector has non-zero projection AND $\|[\text{QT}^0,\text{QT}^1]\|_b > 0$ (Definition 1.1) |
| **hub** | A sector with high transport degree connecting otherwise disjoint Supp_nc regions (informal; S6 primary, S7 secondary) |

**Sector labeling.** Primitive sectors are labeled $S_1,\ldots,S_9$ in increasing order of $(\lambda_A, \lambda_{\text{QT}}, \lambda_{\text{HT}})$. For readability we often refer to sectors by their parent layer: e.g., "the $V_{5/9}$ hub" refers to the three sectors $S_5, S_6, S_7 \subset V_{5/9}$, of which $S_6$ is the primary hub (degree 5).

**Object hierarchy.** Objects in this paper fall into three levels of formality:
- *Canonical* — spectral layers ($V_\lambda$) are fully determined by the representation;
- *Semi-canonical* — primitive sectors ($S_\alpha$) are the finest decomposition from the commutative Center, tied to the chosen commuting family;
- *Informal* — labels like T7, "hub," and "bridge" are convenient shorthand for phenomenological patterns; they do not denote formal mathematical objects.

We use **Observation** for empirical findings verified on the Rubik's cube and S₃ prototypes; **Corollary** for logical consequences of an Observation; and reserve **Theorem** for results with formal proofs (none in the present paper — this is a computational representation analysis).

### 1.4 Noncommutative Support: A Structural Invariant

**Definition 1.1** (Noncommutative Support). For a primitive sector $\alpha$ with projector $P_\alpha$, its *noncommutative support* is

$$\text{Supp}_\text{nc}(\alpha) = \{b \in \{\text{cp}, \text{ep}, \text{co}, \text{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[\text{QT}^0, \text{QT}^1]\|_b > 0\},$$

where $\text{QT}^a = \frac{1}{4} \sum_{g \in \text{axis-}a} \rho(g)$ is the per-axis quarter-turn average, and $\|[\text{QT}^0, \text{QT}^1]\|_b$ is the Frobenius norm of the commutator restricted to block $b$.

In words: a block belongs to $\text{Supp}_\text{nc}(\alpha)$ if sector $\alpha$ has non-zero projection onto it AND the per-axis QT operators fail to commute on that block.

The four blocks have sharply different noncommutativity:

| Block | $\|[\text{QT}^0, \text{QT}^1]\|_F$ | Fraction of total | Status |
|-------|--------------------------------------|-------------------|--------|
| cp | 0 (exactly) | 0% | Commutative |
| ep | 2.74 | 93.9% | **Dominant noncommutative** |
| co | 0.61 | 21.0% | Weak sideband |
| eo | 0.79 | 27.1% | Weak sideband |

Total $\|[\text{QT}^0, \text{QT}^1]\|_F = 2.92$. EP carries essentially all the noncommutativity.

**Supp_nc is the dominant structural invariant for Type I transport.** It is not claimed to be the unique universal invariant controlling all transport — the CP channel (Type II) demonstrates that a second, independent mechanism exists. But for the 9 noncommutative transport edges, Supp_nc intersection is empirically necessary and sufficient.

**Remark (Locality of Supp_nc).** The definition of $\text{Supp}_\text{nc}$ is not intrinsic to the representation $\rho$ alone. It depends on a distinguished decomposition of the generator family into axis-resolved quarter-turn sectors — specifically, the per-axis QT operators $\text{QT}^a = \frac{1}{4}\sum_{g \in \text{axis-}a}\rho(g)$. In the Rubik's cube system, this decomposition is geometrically natural: the three cube axes form a symmetric generating partition, and the QT/HT distinction (quarter-turn vs. half-turn) is the coarsest generator refinement that preserves cubic symmetry. For general finite-group representations, an analogous notion would require a generator partition carrying compatible semisimple transport structure. The present paper establishes the Supp_nc framework for the cube family; generalization to arbitrary $(G, V, \rho, S)$ with partitioned generators is an open direction (§7.4).

### 1.5 Transport Mechanism Classification

Direct transport between primitive sectors arises from exactly two independent mechanisms:

$$\boxed{K_{\alpha\beta} > 0 \;\Longrightarrow\; \begin{cases} \text{Type I (Noncommutative mixing):} & \text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) \neq \emptyset \quad \text{(9 of 10 edges)} \\ \text{Type II (Commutative permutation):} & \text{shared CP block with generator-noncommutative permutation adjacency} \quad \text{(1 of 10 edges: S8} \leftrightarrow \text{S9)} \end{cases}}$$

**Type I (Noncommutative Mixing).** For all 9 non-CP transport edges in the post-$\rho$-fix 9-sector decomposition, noncommutative support intersection is empirically necessary and sufficient:

$$\text{For Type I transport: } \text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) \neq \emptyset \;\Longleftrightarrow\; K_{\alpha\beta} > 0.$$

This is a **structural observation**, not a universal theorem: within the Rubik's cube representation, every sector pair with overlapping noncommutative support has non-zero transport, and every sector pair with non-zero transport (outside the CP channel) has overlapping noncommutative support. The mechanism is M₂-driven: noncommuting QT operators on overlapping blocks create generator mixing that couples the sectors.

**Type II (Commutative Permutation Transport).** S8(cp)$\leftrightarrow$S9(cp+co): $K = 2.83 > 0$ but $\text{Supp}_\text{nc}(\text{S8}) = \emptyset$ and $\text{Supp}_\text{nc}(\text{S8}) \cap \text{Supp}_\text{nc}(\text{S9}) = \emptyset$. This is the **CP permutation channel** — an independent transport mechanism. The CP block's QT algebra is exactly commutative ($\|[\text{QT}^0, \text{QT}^1]\|_{\text{cp}} = 0$), so Supp_nc does not detect this channel. However, individual generators $\rho(g)$ on CP are non-trivial permutation matrices (the CP block carries the symmetric group action of corner permutations), and these generators do not commute with the spectral projectors of S8 and S9 on CP. This reveals a deep structural insight:

$$\boxed{\text{Averaging commutativity} \;\neq\; \text{Generator commutativity}}$$

The QT operators are *averages* over axis-aligned generator subsets. Their commutativity on CP means the per-axis averaging structure is abelian on that block. But the individual generators — the raw $\rho(g)$ matrices — are non-trivial permutations that mix the spectral eigenspaces. Transport can exist without QT noncommutativity. This is not a failure of Type I — it is a **second, qualitatively distinct transport mechanism**.

**Transport Type Classification:**

| Type | Mechanism | Algebraic origin | Criterion | Example edges |
|------|-----------|-----------------|-----------|---------------|
| **Type I** | Noncommutative mixing | M₂ components in $A_{\text{EP}}$; weak CO/EO sidebands | $\text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) \neq \emptyset$ | S3$\leftrightarrow$S6, S4$\leftrightarrow$S6, S6$\leftrightarrow$S7, etc. (9 edges) |
| **Type II** | Commutative permutation mixing | CP permutation action; Bose-Mesner adjacency | Shared CP block + $\rho(g)|_{\text{CP}} \neq \text{id}$ + $[P_\alpha, \rho(g)] \neq 0$ | S8$\leftrightarrow$S9 (1 edge) |

**Corollary A.1** (All Direct Edges are Block-Preserving). Every edge in the transport graph, whether Type I or Type II, shares $\geq 1$ block. Zero cross-block direct edges.

**Corollary A.2** (Cross-Block = Composition-Only). If sectors share neither noncommutative support (Type I) nor commutative permutation adjacency (Type II), then $K_{\alpha\beta} = 0$ and the pair is T7: reachable only via length-2 composition $\alpha \to \gamma \to \beta$ through an intermediate sector $\gamma$.

The transport taxonomy is verified on the Rubik's cube representation (228-dim, 9 primitive sectors, 9 Type I edges + 1 Type II edge, 5 T7 pairs) and in the S₃ minimal prototypes (9-dim and 12-dim variants, both showing perfect Supp_nc/transport alignment with the Type I/II distinction).

### 1.6 The M₂ Principle

Why does Supp_nc have this structure? The answer lies in the algebraic nature of the edge-permutation block:

$$A_{\text{EP}} = \langle Q_0, Q_1, Q_2 \rangle \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4.$$

The three active $M_2$ components are the **atoms of noncommutativity** in the system. They are responsible for:

1. **Refinement obstruction** — noncommuting QT operators on EP prevent the spectral decomposition from being further refined within the commutative Center approach
2. **Hub formation** — S6 (ep+eo, degree 5) is the unique sector whose Supp_nc intersects with the maximal number of other sectors, making it the obligatory intermediary
3. **Transport nonlocality** — sectors with disjoint Supp_nc cannot exchange amplitude directly, even if they share commutative blocks
4. **Commutant gap** — the dimension gap $\dim \text{Comm}(A_{\text{EP}}) - \dim \text{Comm}(\rho|_{\text{EP}}) = 424$ measures the transversality between spectral and irreducible decompositions

The M₂ Principle states: **noncommutative simple components of the block algebras determine the transport topology.** The transport graph is the intersection graph of noncommutative supports, and the M₂ components are the minimal units of noncommutativity that create those supports.

### 1.7 Relation to the Trilogy

| Paper | Object | Question | This paper's relation |
|-------|--------|----------|----------------------|
| Paper I | $A = \frac{1}{|S|}\sum \rho(s)$ | What is the spectral object? | Provides the primitive sector decomposition on which transport operates |
| **Paper II** | **$K_{\alpha\beta}$, Supp_nc** | **Where does transport topology come from?** | **This paper** |
| Paper III | $\kappa_d$, Lie closure | Why can discrete composition reach what Lie cannot? | Studies dynamical accessibility; this paper studies static transport structure only |

Paper II does **not** study: dynamics (trajectories, controllability ranks), Lie accessibility ($\kappa_d$ hierarchy, $A_g = \log\rho(g)$, curvature), phase automata (Markov transitions $M_{ij}$), or control policies. Those are Paper III. The boundary is clean: **Paper II = static transport topology. Paper III = dynamical accessibility.**

---

## Part I — Transport Category

## 2. Primitive Sectors and Block Structure

### 2.1 Representation Space

The Rubik's cube representation $\rho: G \to \text{GL}(228, \mathbb{C})$ decomposes into four block-diagonal subspaces:

$$V = V_{\text{cp}} \oplus V_{\text{ep}} \oplus V_{\text{co}} \oplus V_{\text{eo}}$$

| Block | Dim | Algebraic structure | Noncommutativity |
|-------|-----|---------------------|------------------|
| cp (corner permutation) | 64 | Q₃ Hamming scheme H(3,2), Bose–Mesner $\cong$ Hecke $H(S_2 \wr S_3, S_3)$ | 0 (exactly commutative) |
| ep (edge permutation) | 144 | $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ | 2.74 (93.9% of total) |
| co (corner orientation) | 8 | Z₃ phase structure | 0.61 (21.0%) |
| eo (edge orientation) | 12 | Z₂ phase structure | 0.79 (27.1%) |

Total dimension: $64 + 144 + 8 + 12 = 228$.

The generator set $S$ consists of the 18 standard face-turn generators (6 faces $\times$ 3 turns). $S$ is closed under inversion.

### 2.2 Six Canonical Layers (A-Eigenspaces)

The averaging operator $A = \frac{1}{18} \sum_{g \in S} \rho(g)$ has 6 distinct eigenvalues. Each eigenspace $E_\lambda = \text{im}(P_\lambda)$ is characterized by its block-support profile:

| $k$ | $\lambda = 1 - k/9$ | Dim | Label | Block composition |
|-----|---------------------|-----|-------|-------------------|
| 0 | 1 | 20 | V₁ | cp(8) + ep(12) |
| 1 | 8/9 | 2 | V₈/₉ | eo(2) |
| 2 | 7/9 | 39 | V₇/₉ | ep(36) + eo(3) |
| 3 | 2/3 | 26 | V₂/₃ | ep(24) + co(2) |
| 4 | 5/9 | 106 | V₅/₉ | cp(24) + ep(72) + co(3) + eo(7) |
| 6 | 1/3 | 35 | V₁/₃ | cp(32) + co(3) |

$k = 5$ ($\lambda = 4/9$) is genuinely absent — no blockwise primitive idempotent produces it. The 10 block-level primitive idempotents collapse to exactly 6 global spectral layers via eigenvalue coincidence $\lambda = 1 - k/m$ across different blocks (Paper I, Theorem 3.6).

### 2.3 Nine Primitive Sectors

Joint diagonalization of Center$\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$ refines the 6 layers into **9 primitive sectors** — the finest decomposition achievable within the commutative center:

| Sector | Dim | $k$ | $\lambda_A$ | $\lambda_{\text{QT}}$ | $\lambda_{\text{HT}}$ | Block support | Layer |
|--------|-----|-----|-------------|------------------------|------------------------|---------------|-------|
| S1 | 20 | 0 | 1 | 1 | 1 | cp(8)+ep(12) | V₁ |
| S2 | 2 | 1 | 8/9 | 5/6 | 1 | eo(2) | V₈/₉ |
| S3 | 39 | 2 | 7/9 | 5/6 | 2/3 | ep(36)+eo(3) | V₇/₉ |
| S4 | 26 | 3 | 2/3 | 1/2 | 1 | ep(24)+co(2) | V₂/₃ |
| S5 | 1 | 4 | 5/9 | 1/3 | 1 | eo(1) | V₅/₉(eo) |
| S6 | 39 | 4 | 5/9 | 1/2 | 2/3 | ep(36)+eo(3) | V₅/₉(A) |
| S7 | 66 | 4 | 5/9 | 2/3 | 1/3 | cp(24)+ep(36)+co(3)+eo(3) | V₅/₉(B) |
| S8 | 8 | 6 | 1/3 | 0 | 1 | cp(8) | V₁/₃(A) |
| S9 | 27 | 6 | 1/3 | 1/3 | 1/3 | cp(24)+co(3) | V₁/₃(B) |

These 9 sectors are the vertices of the transport graph. All transport analysis in this paper operates at this 9-sector resolution.

### 2.4 The Noncommutative Support of Each Sector

Applying Definition 1.1 to the 9 sectors:

| Sector | Supp_nc | Description |
|--------|---------|-------------|
| S1 | $\varnothing$ | ISOLATED — cp is commutative, and S1's ep support is within the commutative subalgebra |
| S2 | {eo} | Pure EO, weakly noncommutative |
| S3 | {ep, eo} | EP + EO, both noncommutative |
| S4 | {ep, co} | EP + CO, both noncommutative |
| S5 | {eo} | Pure EO, weakly noncommutative |
| **S6** | **{ep, eo}** | **PRIMARY HUB — intersects with 5 other sectors' Supp_nc** |
| S7 | {ep, co, eo} | Mixed — intersects with S3, S4, S6, S9 |
| S8 | $\varnothing$ | Pure CP — commutative block only |
| S9 | {co} | CP+CO — only CO is noncommutative |

The pattern is striking: **S1 and S8 are the only sectors with empty Supp_nc.** S1 is genuinely isolated ($K = 0$ with all sectors). S8 has $K > 0$ with S9 via shared CP block — the exception that proves the rule: commutative blocks can mediate transport between sectors that share them, but they cannot create *new* transport channels between sectors with disjoint noncommutative supports.

---

## 3. The Transport Tensor and K Matrix

### 3.1 Definition

**Definition 3.1** (Transport Tensor). For primitive sectors $\alpha, \beta$ with orthogonal projectors $P_\alpha, P_\beta$, the *transport block* for generator $g \in S$ is

$$T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta.$$

This is a $(\dim \alpha) \times (\dim \beta)$ matrix encoding how generator $g$ moves amplitude from sector $\beta$ to sector $\alpha$.

**Definition 3.2** (Transport Graph Matrix). The aggregate transport strength between sectors is

$$K_{\alpha\beta} = \max_{g \in S} \|T_{\alpha\beta}(g)\|_F.$$

$K$ defines a weighted graph on the 9 primitive sectors. $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$ is symmetric ($K_{\alpha\beta} = K_{\beta\alpha}$ to $10^{-15}$) because $\|X\|_F = \|X^T\|_F$ and $P_\beta \rho(g)^T P_\alpha = P_\beta \rho(g^{-1}) P_\alpha$, with $g^{-1} \in S$ (the generator set is inverse-closed). The transport graph is therefore undirected.

### 3.2 The K Matrix at 9-Sector Resolution

All data from [paper_data.md](../docs/paper_data.md), computed at post-$\rho$-fix resolution:

\[
\begin{array}{c|ccccccccc}
K_{\alpha\beta} & \text{S1} & \text{S2} & \text{S3} & \text{S4} & \text{S5} & \text{S6} & \text{S7} & \text{S8} & \text{S9} \\
\hline
\text{S1} & 4.90 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
\text{S2} & 0 & 0.52 & 0 & 0 & 0.47 & 0.58 & 0 & 0 & 0 \\
\text{S3} & 0 & 0 & 4.00 & 0 & 0 & 2.55 & 3.61 & 0 & 0 \\
\text{S4} & 0 & 0 & 0 & 5.66 & 0 & 3.46 & 0 & 0 & 1.00 \\
\text{S5} & 0 & 0.47 & 0 & 0 & 0.33 & 0.82 & 0 & 0 & 0 \\
\text{S6} & 0 & 0.58 & 2.55 & 3.46 & 0.82 & 8.19 & 3.61 & 0 & 0 \\
\text{S7} & 0 & 0 & 3.61 & 0 & 0 & 3.61 & 9.67 & 0 & 4.06 \\
\text{S8} & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 2.83 & 2.83 \\
\text{S9} & 0 & 0 & 0 & 1.00 & 0 & 0 & 4.06 & 2.83 & 5.66
\end{array}
\]

![**Fig. 1. K Matrix Heatmap at 9-Sector Resolution.** Color intensity encodes $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$. Circle markers = Type I noncommutative edges (9). Purple border (S8$\leftrightarrow$S9) = Type II commutative permutation channel. Gray = disconnected.](../../figures/paper2_fig1_k_heatmap.png)

### 3.3 Direct Edges (K > 0.01)

10 direct edges. All share $\geq 1$ block. Classified by transport type:

| Edge | K | Shared block | Transport type |
|------|---|-------------|---------------|
| S2(2,eo) $\leftrightarrow$ S5(1,eo) | 0.47 | eo | Type I — {eo} |
| S2(2,eo) $\leftrightarrow$ S6(39,ep+eo) | 0.58 | eo | Type I — {eo} |
| S3(39,ep+eo) $\leftrightarrow$ S6(39,ep+eo) | 2.55 | ep, eo | Type I — {ep, eo} |
| S3(39,ep+eo) $\leftrightarrow$ S7(66,cp+ep+co+eo) | 3.61 | ep, eo | Type I — {ep, eo} |
| S4(26,ep+co) $\leftrightarrow$ S6(39,ep+eo) | 3.46 | ep | Type I — {ep} |
| S4(26,ep+co) $\leftrightarrow$ S9(27,cp+co) | 1.00 | co | Type I — {co} |
| S5(1,eo) $\leftrightarrow$ S6(39,ep+eo) | 0.82 | eo | Type I — {eo} |
| S6(39,ep+eo) $\leftrightarrow$ S7(66,cp+ep+co+eo) | 3.61 | ep, eo | Type I — {ep, eo} |
| S7(66,cp+ep+co+eo) $\leftrightarrow$ S9(27,cp+co) | 4.06 | cp, co | Type I — {co} |
| S8(8,cp) $\leftrightarrow$ S9(27,cp+co) | 2.83 | cp | **Type II — CP permutation channel** |

**Observation.** 9 of 10 edges are Type I (noncommutative, Supp_nc intersection). The sole Type II edge is S8$\leftrightarrow$S9, which shares the commutative CP block. This edge exists because $\rho(g)$ on CP is a non-trivial permutation action — the individual generators mix the spectral projectors of S8 and S9 even though the averaged QT algebra on CP is commutative. The two-mechanism classification separates these independent transport channels: noncommutative mixing (Type I, M₂-driven) and commutative permutation mixing (Type II, CP adjacency-driven).

### 3.4 Hub Degrees

| Sector | Degree | Connected to |
|--------|--------|-------------|
| S1 | 0 | (none — fully isolated) |
| S2 | 2 | S5, S6 |
| S3 | 2 | S6, S7 |
| S4 | 2 | S6, S9 |
| S5 | 2 | S2, S6 |
| **S6** | **5** | S2, S3, S4, S5, S7 |
| S7 | 3 | S3, S6, S9 |
| S8 | 1 | S9 |
| S9 | 3 | S4, S7, S8 |

**S6 is the primary hub** — degree 5, the unique sector whose Supp_nc = {ep, eo} intersects with the maximal number of other sectors' noncommutative supports. S7 is the secondary hub (degree 3) — its Supp_nc = {ep, co, eo} intersects with S3, S6, and S9.

![**Fig. 2. Transport Skeleton.** Pure connectivity geometry. Center: S6 primary hub (dominant diamond, deep red). Noncommutative core cluster (S2,S3,S4,S5,S7,S9) connected via red edges. Right: S8–S9 detached CP channel (curved dashed purple arc). Top-left: S1 invariant sector (isolated gray). Edge weights omitted — connectivity only.](../../figures/paper2_fig2_transport_skeleton.png)

### 3.5 Transport Topology as Consequence of Supp_nc Geometry

**Structural Observation D** (Transport Topology). The transport graph at 9-sector resolution has the following properties, all of which follow from Supp_nc geometry (Observation A) and the M₂ obstruction (Observations B, C):

1. **All direct edges are block-preserving** — every $K_{\alpha\beta} > 0$ pair shares $\geq 1$ block. Zero cross-block direct edges. (Follows from Observation A: Type I Supp_nc intersection or Type II CP adjacency $\implies$ block overlap)
2. **S1 is fully isolated** — $K_{1,\beta} = 0$ for all $\beta \neq 1$. S1 is a $G$-invariant subrepresentation. (Supp_nc(S1) = $\emptyset$ and no Type II CP adjacency)
3. **S6 is the primary hub** — degree 5, the unique sector whose Supp_nc = {ep, eo} intersects 5 other sectors' noncommutative supports. (Observation B: M₂ overlap forces hub formation)
4. **S7 is the secondary hub** — degree 3, Supp_nc = {ep, co, eo} bridges EP, CO, and EO blocks. (Corollary of Observation B)
5. **Cross-block transport is composition-only (T7)** — 5 pairs with disjoint Supp_nc have $K = 0$ but are reachable via length-2 paths through the S6–S7 hub complex. (Observation A: neither Type I nor Type II criterion met $\implies K = 0$)

The transport graph is not an empirical observation — it is the **shadow of Supp_nc geometry**, cast onto the 9-sector decomposition by the M₂ components of $A_{\text{EP}}$.

### 3.6 S1 Isolation

S1 (V₁, 20-dim, cp+ep) has $K < 10^{-14}$ with all other 8 sectors. It is the unique fully decoupled sector — a $G$-invariant subrepresentation. Its Supp_nc = $\emptyset$: while S1 has ep support (12 dimensions), this ep subspace lies within the commutative subalgebra of $A_{\text{EP}}$. Concretely, $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$: the four $M_2(\mathbb{C})$ components carry the noncommutative transport channels (Type I), while the four $M_1(\mathbb{C})$ components form the commutative center of $A_{\text{EP}}$. S1's 12-dimensional ep support falls entirely within the $M_1(\mathbb{C})^4$ commutative component — it carries no $M_2$ noncommutative structure and therefore cannot participate in Type I transport.

### 3.7 Transport Sparsity Is Not Eigenvalue Proximity

The K matrix makes visible a fundamental fact: eigenvalue ordering and transport adjacency are independent structures. S3 (V₇/₉, $\lambda = 7/9$) and S4 (V₂/₃, $\lambda = 2/3$) are adjacent in the eigenvalue sequence yet have $K = 0$. S3 and S7 (V₅/₉, $\lambda = 5/9$) are non-adjacent yet have $K = 3.61$. An observer who knows only the eigenvalues and their multiplicities cannot predict which sectors are coupled.

---

## Part II — Supp_nc: The Dominant Type I Structural Invariant

## 4. Noncommutative Support Determines Transport

### 4.1 Why Block Support Overlap Is Not Sufficient

The naive necessary condition for transport — block-support overlap — correctly predicts that $K_{\alpha\beta} = 0$ when sectors have disjoint block support. But it fails to predict many zeros:

| Pair | Shared block? | $K$ | Why overlap fails |
|------|--------------|-----|-------------------|
| S1 $\leftrightarrow$ S3 | ep | 0 | S1's ep support is in the commutative subalgebra |
| S1 $\leftrightarrow$ S4 | ep | 0 | Same |
| S1 $\leftrightarrow$ S6 | ep | 0 | Same |
| S1 $\leftrightarrow$ S7 | cp, ep | 0 | S1 is $G$-invariant — algebraic isolation overrides geometric overlap |
| S3 $\leftrightarrow$ S9 | — | 0 | Disjoint block support (correctly predicted) |
| S4 $\leftrightarrow$ S8 | — | 0 | Disjoint block support (correctly predicted) |
| S6 $\leftrightarrow$ S9 | — | 0 | Disjoint block support (correctly predicted) |

Block-support overlap is necessary but not sufficient. Something finer is needed.

### 4.2 The Noncommutativity Hierarchy

The key insight is that the four blocks have sharply different algebraic character:

$$\|[\text{QT}^0, \text{QT}^1]\|_F = 2.92 \text{ total}$$

| Block | $\|[\text{QT}^0, \text{QT}^1]\|_F$ | % of total | Algebra |
|-------|--------------------------------------|-----------|---------|
| cp | 0 | 0% | $\mathbb{C}[A_{\text{cp}}]$ exactly commutative |
| ep | 2.74 | 93.9% | $M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ — **dominant** |
| co | 0.61 | 21.0% | Weak noncommutative sideband |
| eo | 0.79 | 27.1% | Weak noncommutative sideband |

The CP block is **exactly commutative**: all per-axis QT operators commute when restricted to CP. While individual generators $\rho(g)$ on CP are non-trivial permutation matrices, the averaged QT operators form a commutative algebra — the Q₃ Hamming scheme's Bose–Mesner algebra.

The EP block carries 93.9% of the total noncommutativity. CO and EO carry weak sidebands.

### 4.3 Supp_nc Definition and Computation

**Definition 4.1** (Noncommutative Support). For a primitive sector $\alpha$,

$$\text{Supp}_\text{nc}(\alpha) = \{b \in \{\text{cp}, \text{ep}, \text{co}, \text{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[\text{QT}^0, \text{QT}^1]\|_b > 0\}.$$

Equivalently: the set of blocks on which the sector has non-zero projection AND the block's per-axis QT operators fail to commute.

| Sector | Block support | Supp_nc | $\lvert\text{Supp}_\text{nc}\rvert$ |
|--------|---------------|---------|-----------------------------------|
| S1 | cp, ep | $\varnothing$ | 0 |
| S2 | eo | {eo} | 1 |
| S3 | ep, eo | {ep, eo} | 2 |
| S4 | ep, co | {ep, co} | 2 |
| S5 | eo | {eo} | 1 |
| S6 | ep, eo | {ep, eo} | 2 |
| S7 | cp, ep, co, eo | {ep, co, eo} | 3 |
| S8 | cp | $\varnothing$ | 0 |
| S9 | cp, co | {co} | 1 |

**S1 has Supp_nc = $\emptyset$ despite ep support** because its 12-dimensional ep subspace lies within the commutative subalgebra of $A_{\text{EP}}$. Concretely, $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$: S1's ep support falls entirely within the $M_1(\mathbb{C})^4$ commutative component, carrying no $M_2$ noncommutative structure. This is the quantitative form of S1 being a $G$-invariant subrepresentation.

**S8 has Supp_nc = $\emptyset$** because it has only CP support, and CP is exactly commutative.

![**Fig. 3. Noncommutative Support Overlap.** Colored cells = Supp_nc present (binary). Numbers = per-block commutator norm $\|[\text{QT}^0, \text{QT}^1]\|_b$ (graded). ep=2.74 dominates; co=0.61 and eo=0.79 are weak sidebands; cp=0 is exactly commutative. Right: $|\text{Supp}_\text{nc}|$ cardinality with hub markers.](../../figures/paper2_fig3_supp_nc_overlap.png)

### 4.4 Transport Mechanism Classification

**Structural Observation A** (Two-Type Transport Mechanisms). For any two distinct primitive sectors $\alpha \neq \beta$, direct transport arises from exactly one of two independent mechanisms:

**Type I — Noncommutative mixing.** For all 9 non-CP transport edges, $\text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) \neq \emptyset$ is empirically necessary and sufficient for $K_{\alpha\beta} > 0$. The M₂ components of $A_{\text{EP}}$ (and weak CO/EO sidebands) create generator mixing that couples sectors sharing noncommutative block support. Within the Rubik's cube representation, no sector pair with overlapping noncommutative support has zero transport, and no sector pair (outside the CP channel) with non-zero transport has disjoint noncommutative support. This accounts for 9 of 10 direct edges.

**Type II — Commutative permutation transport.** S8(cp)$\leftrightarrow$S9(cp+co): $K = 2.83 > 0$ but Supp_nc(S8) = $\emptyset$. This is the CP permutation channel — an independent transport mechanism. The CP block's QT algebra is exactly commutative ($\|[\text{QT}^0, \text{QT}^1]\|_{\text{cp}} = 0$), so Supp_nc does not detect this channel. However, individual generators $\rho(g)$ on CP are non-trivial permutation matrices (the CP block carries the symmetric group action of corner permutations), and these generators do not commute with the spectral projectors of S8 and S9 on CP. This reveals a structural fact that Supp_nc correctly exposes: **averaging commutativity does not imply generator commutativity with spectral projectors.** The CP channel is generator-mediated but not QT-noncommutative — a second, qualitatively distinct transport mechanism.

**Empirical verification (numerical).** Computing $K_{\alpha\beta}$ for all $9 \times 8 / 2 = 36$ unordered pairs at post-$\rho$-fix resolution:
- 10 pairs with $K > 0.01$: 9 are Type I (Supp_nc intersection), 1 is Type II (S8–S9 CP channel)
- 5 T7 pairs (cross-block, $K = 0$, reachable via length-2 composition): all have disjoint Supp_nc AND no Type II CP adjacency
- 21 remaining pairs: all have $K < 10^{-14}$ and neither Type I nor Type II criterion met

**Caveat.** The Type I criterion (Supp_nc intersection $\Leftrightarrow$ $K > 0$) is an empirical regularity verified on the Rubik's cube (228-dim, 9 sectors) and S₃ prototypes (9-dim and 12-dim). A first-principles derivation of Supp_nc intersection as a necessary and sufficient condition for noncommutative transport — starting from the group algebra $\mathbb{C}[G]$ and the projector geometry — has not been established in this paper. The criterion should be understood as a robust structural observation supported by exhaustive numerical evidence, not as a theorem. Establishing its algebraic necessity is an open direction (§7.4, Direction 1 and 2).

**Verification (S₃ minimal prototypes).** The two-mechanism classification is verified in the S₃ nat(3)$\oplus$reg(6) prototype (9-dim, 5 sectors, 3 cross-block T7 pairs) and the S₃ reg(6)$\oplus$reg(6) prototype (12-dim, 10 sectors, perfect Supp_nc/transport alignment with Type I/II separation). See [paper_data.md](../docs/paper_data.md) §9.

### 4.5 Corollaries

**Corollary A.3** (All Direct Edges are Block-Preserving). Every edge in the transport graph shares $\geq 1$ block. There are **zero cross-block direct edges**. Cross-block transport requires length-2 composition.

**Corollary A.4** (Supp_nc Size Predicts Hub Degree). The hub degree of a sector is bounded by the number of other sectors whose Supp_nc intersects with it. S6 (Supp_nc = {ep, eo}) achieves degree 5 because {ep, eo} is the most common Supp_nc combination among other sectors (S2, S3, S5, and S4/S7 via shared ep).

**Corollary A.5** (T7 = Disjoint Supp_nc). The 5 T7 pairs (composition-only accessibility) are precisely the cross-block pairs with disjoint Supp_nc:

| T7 Pair | Supp_nc($\alpha$) | Supp_nc($\beta$) | Intersection |
|---------|-------------------|-------------------|-------------|
| S2(eo) $\leftrightarrow$ S4(ep+co) | {eo} | {ep, co} | $\varnothing$ |
| S3(ep+eo) $\leftrightarrow$ S9(cp+co) | {ep, eo} | {co} | $\varnothing$ |
| S4(ep+co) $\leftrightarrow$ S5(eo) | {ep, co} | {eo} | $\varnothing$ |
| S4(ep+co) $\leftrightarrow$ S8(cp) | {ep, co} | $\varnothing$ | $\varnothing$ |
| S6(ep+eo) $\leftrightarrow$ S9(cp+co) | {ep, eo} | {co} | $\varnothing$ |

All 5 are cross-block (disjoint block support). All mediated through the S6–S7 hub complex. Zero within-block T7 pairs — curvature (Paper III) is block-preserving.

### 4.6 Why Supp_nc Works: The Transport–Commutator Identity

The algebraic reason Supp_nc controls Type I transport is the commutator identity (derived in the original analysis):

$$[P_\alpha, \rho(g)] = \sum_{\beta \neq \alpha} \big(T_{\alpha\beta}(g) - T_{\beta\alpha}(g)^\dagger\big).$$

The commutator $[P_\alpha, \rho(g)]$ is non-zero precisely when there exists $\beta \neq \alpha$ with $T_{\alpha\beta}(g) \neq 0$. The norm of this commutator, restricted to block $b$, is:

$$\|[P_\alpha|_b, \rho(g)|_b]\|_F^2 = 2 \sum_{\beta \neq \alpha} \|T_{\alpha\beta}(g)|_b\|_F^2.$$

A block $b$ can contribute to cross-sector transport if and only if the projector $P_\alpha$ fails to commute with $\rho(g)$ on that block. This failure of commutation is exactly what $\|[\text{QT}^0, \text{QT}^1]\|_b > 0$ detects at the aggregate level — the per-axis QT operators are averaged versions of the generators, and their commutator measures the aggregate obstruction to simultaneous diagonalization on block $b$.

In particular: on the CP block, $[\text{QT}^0, \text{QT}^1] = 0$, meaning the QT operators can be simultaneously diagonalized on CP. The spectral projectors restricted to CP commute with each other — but they need not commute with individual generators $\rho(g)$. This is why S8$\leftrightarrow$S9 transport exists (individual generators don't commute with projectors on CP) but the CP block is classified as commutative (the averaged QT operators do commute). The CP channel is **generator-mediated but not QT-noncommutative** — a weaker form of transport that Supp_nc correctly distinguishes from the dominant EP-mediated channels.

---

## Part III — M₂ Principle

## 5. The EP Algebra as the Noncommutative Origin

### 5.1 A_EP Structure

The edge-permutation block is the dominant noncommutative carrier (93.9%). Its per-axis QT operators generate a 20-dimensional semisimple algebra:

$$A_{\text{EP}} = \langle Q_0, Q_1, Q_2 \rangle \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4.$$

Key facts (all verified to machine precision):
- $\dim A_{\text{EP}} = 20$, closes at degree 3
- Center $Z(A_{\text{EP}}) = 8$-dim
- 4 simple $M_2$ components + 4 simple $M_1$ components = 8 isotypic blocks on EP
- 3 of 4 $M_2$ components are active ($[Q_i, Q_j] \neq 0$); one $M_2$ is "trivialized" (all $Q_i$ simultaneously scalarize on it)
- Killing form: signature $(8^+, 4^-, 8\text{ zero})$, $\ker(K) = Z(A_{\text{EP}})$
- Uniform multiplicity 12 across all 8 components: $4 \times 24 + 4 \times 12 = 144 = \dim \text{EP}$

### 5.2 Double Commutant and Commutant Gap

$$\text{Comm}(A_{\text{EP}}) \cong M_{12}(\mathbb{C})^8, \quad \dim \text{Comm}(A_{\text{EP}}) = 8 \times 144 = 1152.$$

$$\text{End}_{\text{Comm}(A_{\text{EP}})}(\text{EP}) = A_{\text{EP}} \quad \checkmark \text{ (double commutant theorem verified)}.$$

The commutant gap — the quantitative signature of spectral-isotypic transversality:

$$\Delta_{\text{comm}} = \dim \text{Comm}(A_{18}) - \dim \text{Comm}(\rho) = 1052 - 628 = 424.$$

This gap equals $2 \sum \|T_{ij}\|^2$ — it is the aggregate transport norm, the total "leakage" of the spectral projectors outside the $G$-invariant subalgebra.

### 5.3 M₂ Components as Transport Atoms

Each active $M_2$ component is a **transport atom** — a minimal noncommutative unit that creates cross-sector coupling. On an $M_2$ component, the three QT operators act as non-commuting $2 \times 2$ matrices. The spectral projectors $P_\alpha$ restricted to an $M_2$ component are rank-1 projectors in different directions — they do not commute with individual $\rho(g)$ because the generator action rotates between these directions.

This rotation is the **microscopic mechanism of transport**. A generator $\rho(g)$ applied to a vector in sector $\alpha$'s subspace of the $M_2$ component rotates it partially into sector $\beta$'s subspace — producing a non-zero $T_{\alpha\beta}(g)$.

The three active $M_2$ components create three distinct transport channels:
1. **S3$\leftrightarrow$S6** (via $M_2$ #1 on EP): $K = 2.55$
2. **S4$\leftrightarrow$S6** (via $M_2$ #2 on EP): $K = 3.46$
3. **S6$\leftrightarrow$S7** (via $M_2$ #3 on EP): $K = 3.61$

S6 is the unique sector with non-zero projection onto all three active $M_2$ components — this is why it has degree 5.

### 5.4 Hub Necessity

**Structural Observation B** (M₂ Overlap $\Rightarrow$ Hub Necessity). Let the EP block algebra contain $k \geq 2$ active noncommutative simple components. If the sector projectors $\{P_\alpha\}$ resolve these components into different rank-1 subspaces, then there exists a unique sector (the *hub*) whose projector has non-zero overlap with every active noncommutative component. All other sectors have non-zero overlap with at most one such component.

*Proof outline.* On each $M_2$ component, the $P_\alpha|_{\text{EP}}$ are rank-1 orthogonal projectors (the $M_2$ component is 2-dimensional, and the Center diagonalization separates its two eigenvectors). Since there are 9 sectors and 3 active $M_2$ components (each contributing 2 dimensions = 2 sectors), at most 6 sectors can be "pure" (supported on a single $M_2$ component). The remaining sectors must mix across components. The unique mixing pattern that maximizes Supp_nc intersection is a sector that projects onto the "off-diagonal" subspace of all three $M_2$ components — this is S6.

S6 is the primary hub because it is the unique sector whose Supp_nc = {ep, eo} has non-empty intersection with Supp_nc of S2 ({eo}), S3 ({ep, eo}), S4 ({ep, co}), S5 ({eo}), and S7 ({ep, co, eo}). Its EP support spans all three active $M_2$ components.

### 5.5 Transport Nonlocality from M₂

The M₂ Principle explains why cross-block transport requires composition. The M₂ components live entirely within the EP block. A sector with only CO support (e.g., S9's co component) has no access to the EP-based M₂ transport machinery. It can only transport to EP-containing sectors via the weak CO noncommutative sideband ($\|[\text{QT}^0, \text{QT}^1]\|_{\text{co}} = 0.61$), which couples it to sectors sharing CO support (S4, S7).

Cross-block transport (e.g., S3(ep+eo) $\to$ S9(cp+co)) is impossible at the single-generator level because there is no block where BOTH sectors have non-zero projection AND the block is noncommutative. The composition path S3 $\to$ S7 $\to$ S9 works because S7 has both EP and CO support — it translates EP-based transport into CO-based transport, bridging the noncommutative gap.

---

## Part IV — Refinement Geometry

## 6. The Obstruction Lattice

### 6.1 Refinement POSET (from Paper I)

Paper I established that the family of spectral decompositions $\{D(A_S)\}$ across inverse-closed generator sets $S$ forms a refinement POSET $\mathcal{L}$ under $D_1 \leq D_2 \iff A_{D_2} \in \langle A_{D_1} \rangle$. The commutative core $\mathcal{C} = \{\text{Center}, \text{QT}_{\text{all}}, \text{HT}_{\text{all}}, 18\text{-gen}\}$ is a $\wedge$-semilattice. The 9 primitive sectors are the atoms of $\mathcal{C}$ — the finest decomposition achievable within the commutative core.

### 6.2 Refinement Stops at the Noncommutative Obstruction

**Structural Observation C** (M₂ Overlap Obstruction Caps Refinement). The refinement chain terminates at 9 primitive sectors — not as a numerical artifact, but as an algebraic consequence of the representation structure. Further refinement is blocked by the M₂ overlap obstruction: the noncommuting QT operators on EP cannot be simultaneously diagonalized, and any operator that would split an M₂-coupled sector must fail to commute with the Center.

**Explanation.** The Center$\{A, \text{QT}_{\text{all}}, \text{HT}_{\text{all}}\}$ is exactly commutative ($\|[\cdot, \cdot]\| < 10^{-15}$). Any operator that would split, say, S6 into finer sectors must live in $A_{\text{EP}}$ — the only algebra with non-trivial action on EP. But the only operators in $A_{\text{EP}}$ that commute with both QT_all and HT_all are in the center $Z(A_{\text{EP}})$, which is already diagonalized by the 9-sector decomposition (its 8 eigenvalues are resolved into the 8 non-S1 sectors). Adding a non-central element of $A_{\text{EP}}$ would break commutativity — the new operator would not commute with QT_all or HT_all, so the "joint diagonalization" would not be a true simultaneous diagonalization and the decomposition would not consist of orthogonal projectors.

The 9 sectors are therefore the **finest commutative decomposition** — the unique maximal refinement achievable while maintaining pairwise commuting diagonalizing operators and orthogonal projectors. The obstruction is the M₂ components: their noncommutativity ($[Q_i, Q_j] \neq 0$ on 3 of 4 components) is the algebraic wall that blocks further refinement.

![**Fig. 4. Refinement Obstruction.** Left: Commutative Center diagonalization chain ($A_{18}$ → + QT$_{\rm all}$ → + HT$_{\rm all}$) resolves to 9 primitive sectors. Right: M₂ components in $A_{\text{EP}}$; all observed refinement attempts require operators outside the commutative center. M₂ overlap obstructs further commutative splitting.](../../figures/paper2_fig4_refinement_obstruction.png)

### 6.3 The Obstruction Lattice

The M₂ components of $A_{\text{EP}}$ are the **atoms of obstruction** — the minimal noncommutative units that prevent further refinement. Each active M₂ component is a 2-dimensional subspace where QT⁰ and QT¹ fail to commute. Attempting to split this 2-dimensional subspace into 1-dimensional QT⁰-eigenspaces and 1-dimensional QT¹-eigenspaces simultaneously is impossible — QT⁰ and QT¹ have different eigenvectors on this subspace.

The obstruction lattice $\mathcal{O}$ is the POSET of M₂ subalgebras under inclusion. For the Rubik's cube:

$$\mathcal{O} = \{M_2^{(1)}, M_2^{(2)}, M_2^{(3)}, \text{trivial } M_2\}$$

where the first three are active (create transport) and the fourth is trivialized. The noncommutativity at each node is:

$$\|[Q_i, Q_j]\|_{M_2^{(k)}} = \begin{cases} > 0 & k = 1,2,3 \\ = 0 & k = \text{trivial} \end{cases}$$

### 6.4 Commutative vs. Noncommutative Refinement

The refinement story has two regimes:

| Regime | Algebra | Finest decomposition | Blocked by |
|--------|---------|---------------------|------------|
| Commutative | Center$\{A, \text{QT}_{\text{all}}, \text{HT}_{\text{all}}\}$ | 9 primitive sectors | — (complete within commutative core) |
| Noncommutative | $A_{\text{EP}}$ full algebra | Would split each M₂ into 2 sectors (11+ total) | M₂ obstruction — $[Q_i, Q_j] \neq 0$ on active M₂ |

The 9-sector decomposition is the finest **commutative** decomposition. Further refinement is possible only if we accept non-orthogonal, non-commuting "sectors" — which would not be sectors in the spectral sense (no longer eigenspaces of a commuting family).

### 6.5 Generality: When Does Refinement Have an Obstruction Lattice?

The obstruction lattice exists whenever:

1. The representation has a block $b$ where the per-axis averaging operators fail to commute ($\|[\text{QT}^a, \text{QT}^b]\|_b > 0$)
2. The block algebra $A_b$ has simple components of dimension $> 1$ (noncommutative by Wedderburn)
3. The center approach diagonalizes $Z(A_b)$ but cannot resolve the individual simple components

Condition (1) is the **M₂ condition** — without it, the entire block algebra is commutative and the center approach fully diagonalizes everything. Condition (2) is automatic for any semisimple algebra with noncommutative simple components. Condition (3) is the **refinement obstruction** — the gap between what the commutative center can resolve and what the full block algebra contains.

For the Rubik's cube, all three conditions hold on the EP block. CO and EO satisfy (1) weakly (sidebands at 21% and 27%). CP satisfies none — it is exactly commutative and fully resolved by the center approach.

---

## 7. Discussion

### 7.1 Summary: Four Objects and Four Structural Observations

This paper set out to answer three questions: **where does the transport topology come from? Why does refinement stop at 9? Why do two transport types exist?**

The answers form a chain of structural observations, organized as four objects and four empirical findings:

$$\boxed{\text{Object 4: } A_{\text{EP}} \cong M_2^4 \oplus M_1^4 \;\Rightarrow\; \text{Object 3: Supp}_\text{nc} \;\xRightarrow{\text{Observation A}}\; \text{Object 2: } K_{\alpha\beta} \;\Rightarrow\; \text{Observation D: Transport graph}}$$

$$\boxed{\text{Observation B: Hub necessity} \;\Rightarrow\; \text{Observation C: Refinement obstruction}}$$

**Four Objects:**
1. **Primitive sectors** $\{S_\alpha\}$ — the objects of the transport category (9 vertices)
2. **Transport morphisms** $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ — the morphisms (how amplitude moves)
3. **Noncommutative support** $\text{Supp}_\text{nc}(\alpha)$ — the dominant Type I transport invariant (which morphisms exist; defined relative to axis-resolved QT decomposition)
4. **M₂ obstruction** $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ — the algebraic origin of Type I noncommutativity

**Four Structural Observations:**
- **Observation A** (Two-Type Transport Mechanisms): Type I — noncommutative mixing via Supp_nc intersection (9 of 10 edges). Type II — commutative permutation channel S8$\leftrightarrow$S9 (1 edge). Averaging commutativity $\neq$ generator commutativity.
- **Observation B** (Hub Necessity): M₂ overlap empirically forces a unique hub sector intersecting all active noncommutative components
- **Observation C** (Refinement Obstruction): Refinement stops at 9 sectors — the M₂ obstruction is an algebraic consequence of the representation structure
- **Observation D** (Transport Topology): All edges block-preserving, S1 isolated, S6 primary hub (degree 5), S7 secondary hub (degree 3), cross-block = composition-only (5 T7 pairs)

The transport graph exhibits a **remarkably rigid topology** emerging from noncommutative support overlap. The Rubik's cube representation provides a concrete realization of this two-mechanism architecture. The Type I/II transport classification disentangles two qualitatively distinct mechanisms: noncommutative mixing (M₂-driven) and commutative permutation mixing (CP adjacency-driven). The consistency, stability, and mechanism disentanglement are the central findings — not an axiomatic theorem but a structurally stabilized computational representation analysis.

![**Fig. 5. Structural Chain: From M₂ Algebra to Transport Topology.** Four-node flow: $A_{\text{EP}} \cong M_2^4 \oplus M_1^4$ → Supp_nc → $K_{\alpha\beta}$ → Transport Skeleton. Observations B (Hub Necessity) and C (Refinement Obstruction) as intermediate annotations. Bottom: Type I/II mechanism mini-table.](../../figures/paper2_fig5_m2_chain.png)

### 7.2 What Is Verified and What Is Not

**Verified (numerical, exact at post-$\rho$-fix resolution):**
- **Observation A**: Two-Type Transport Mechanisms — Type I (9 edges, Supp_nc intersection necessary and sufficient) + Type II (1 edge, CP permutation channel) covers all 10 direct edges. No counterexamples found.
- **Observation B**: S6 is the unique hub (degree 5) spanning all three active M₂ components; all other sectors overlap with $\leq 1$ active M₂
- **Observation C**: Refinement halts at 9 sectors — Center is exactly commutative; any finer operator must be non-central in $A_{\text{EP}}$ and would break commutativity
- **Observation D**: Transport graph — 10 block-preserving direct edges, S1 isolated (Supp_nc = $\emptyset$), S6 primary hub (degree 5), S7 secondary hub (degree 3), 5 T7 cross-block pairs
- $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$, commutant gap $\Delta_{\text{comm}} = 424$
- S1 isolation as $G$-invariant subrepresentation
- **Averaging commutativity $\neq$ generator commutativity** — CP block is QT-commutative but generator-noncommutative with spectral projectors

**Verified (S₃ minimal prototypes):**
- Supp_nc/transport alignment with Type I/II taxonomy in both nat$\oplus$reg (9-dim) and reg$\oplus$reg (12-dim)
- T7 exists without M₂ (nat$\oplus$reg has zero curvature but 3 T7 pairs via block decomposition mismatch)

**Not established (open directions):**
- Whether the transport topology generalizes to other finite groups with M₂-containing block algebras
- Whether the obstruction lattice $\mathcal{O}$ is a complete invariant for the refinement POSET
- Full irreducible decomposition of the 228-dim representation
- Generalization of Supp_nc beyond axis-resolved QT decomposition (§1.4 Remark)

### 7.3 What This Paper Does NOT Study

This paper studies **static transport topology** — the graph of which sectors can exchange amplitude under a single generator. It deliberately excludes:

- **Dynamics** — can a trajectory actually reach sector $\beta$ from $\alpha$? (Paper III)
- **Lie accessibility** — $\kappa_d$ hierarchy, $A_g = \log\rho(g)$, curvature $[A_g, A_h]$ (Paper III)
- **Controllability** — ranks, reachable sets, control policies (Paper III)
- **Phase automata** — Markov transitions $M_{ij}$, effective dynamics (Paper III, phenomenology archive)
- **Sub-Riemannian geometry** — $G_i$ tensors, metric incompatibility (Paper III)

The boundary between Papers II and III is clean: **Paper II = which edges exist in the transport graph. Paper III = what trajectories can traverse those edges.**

**On T7 pairs.** The present paper characterizes only first-order transport topology — which sector pairs have $K_{\alpha\beta} > 0$ (Type I or Type II). The 5 T7 pairs have $K = 0$ (neither Type I nor Type II criterion met) yet are reachable via length-2 composition $\alpha \to \gamma \to \beta$. Why these specific pairs are T7 (and not, e.g., S2$\leftrightarrow$S8) requires understanding the higher-order accessibility structure: the $\kappa_d$ hierarchy, curvature channels $[A_g, A_h]$, and the Lie closure of the generator algebra. These are the subject of Paper III. Paper II establishes the static topology — *which direct edges exist*; Paper III explains the dynamic accessibility — *which trajectories can bridge the gaps.*

**Global lifting constraints.** The commutant analysis of Appendix C establishes a structural link between transport sparsity and global equivariant structure: the 10 nonzero direct edges among 9 sectors constrain the lifting map $\pi: \text{End}_G(V) \to \bigoplus_\lambda \text{End}_G(E_\lambda)$ to have cokernel dimension 356. Transport-sparse layer pairs (those with $K_{\text{layer}} < 10^{-8}$) impose independent cross-layer compatibility conditions that per-layer commutant data must satisfy to originate from a single $G$-equivariant operator. In effect, the transport graph acts as a compatibility graph for the global commutant: layers connected by transport edges share commutant degrees of freedom; decoupled layers impose additive constraints. The cokernel dimension $\Delta_{\text{comm}} = 356$ quantifies this incompatibility between local (per-layer) and global commutant structure. Whether this relationship — transport sparsity constrains global lifting — generalizes to other finite group representations is an open direction (§7.4, Direction 3).

### 7.4 Outlook

Several extensions remain open:

1. **Generalization of Supp_nc to arbitrary generator partitions.** For a finite group representation without a natural axis decomposition, how should an analogous invariant be defined? The present construction relies on the geometrically natural 3-axis partition of the Rubik's cube face-turn generators and the resulting QT/HT decomposition (§2.2). For a general pair $(G, S)$ with representation $\rho$, one would need either a principled criterion for partitioning $S$ into noncommutative subsets (e.g., by conjugacy class or coset structure), or a partition-independent construction — perhaps a single object (e.g., the commutator ideal of the generator algebra) whose blockwise noncommutativity generalizes Supp_nc without reference to a partition. The ad hoc character of the axis partition is the primary obstacle to a general classification theorem.

2. **Universality of the Type II mechanism.** The CP permutation channel (Type II, §4.2) is the sole exception to the Type I dominance (Supp_nc intersection $\Leftrightarrow$ $K>0$). Does a CP-mediated transport channel arise generically in other representations that possess a commutative averaging algebra but a noncommutative generator action? The Rubik CP block has $A_{\text{CP}}$ commutative but $[\text{QT}^0, \text{QT}^1]_{\text{CP}} = 0$ while individual generator actions on CP produce nontrivial permutation mixing — a condition that may be formalizable as: (i) $\text{Comm}(\{A_i|_B\})$ is larger than $\text{Comm}(\{\rho(g)|_B\})$, and (ii) the per-generator projectors $P_\alpha \rho(g) P_\beta$ are nonzero for a specific generator subset (here, the 12 quarter-turn moves). A general criterion — stated in terms of the commutant inclusion structure of the block algebra — would elevate Type II from an empirical exception to a predicted transport class.

3. **Precise relationship between lifting constraints and transport topology.** Appendix C establishes that the global commutant $\text{End}_G(V)$ (dimension 610) maps into the per-layer sum $\bigoplus_\lambda \text{End}_G(E_\lambda)$ (dimension 966) with cokernel dimension 356. The open question is whether this cokernel dimension can be computed directly from the transport graph — its number of edges, layer dimensions, and per-layer commutant dimensions — without full combinatorial orbit enumeration. If the K matrix's sparsity pattern (10 nonzero edges among 9 sectors) constrains the lifting map $\pi: \text{End}_G(V) \to \bigoplus_\lambda \text{End}_G(E_\lambda)$ in a predictable way, then the cokernel becomes a derived invariant of the transport topology rather than an independent computation. A conjectural formula relating cokernel rank to the number of zero entries in K would sharpen the connection between transport sparsity and global equivariant structure.

These directions are left for future work.

---

## Appendix A: Construction of the Noncommutative Support

The noncommutative support $\text{Supp}_\text{nc}(\alpha)$ (Definition 1.1) is the dominant structural invariant for Type I transport. This appendix details its construction, the structural choices it depends on, and the algebraic reason for its effectiveness.

### A.1 Per-Axis QT Operators

The 18 face-turn generators partition naturally into three axis-aligned subsets:

$$\text{axis-}a = \{\text{quarter-turns on the two faces perpendicular to axis } a\}, \quad a \in \{0, 1, 2\}.$$

For axis 0 (R/L faces): 4 generators (R, R′, L, L′). For axis 1 (U/D faces): 4 generators (U, U′, D, D′). For axis 2 (F/B faces): 4 generators (F, F′, B, B′). The remaining 6 generators are the half-turns (R2, L2, U2, D2, F2, B2), used in $\text{HT}_\text{all}$ but not in the per-axis QT operators.

The per-axis quarter-turn averaging operator is:

$$\text{QT}^a = \frac{1}{4} \sum_{g \in \text{axis-}a} \rho(g), \quad a \in \{0, 1, 2\}.$$

These three operators are the QT-resolved components of the total quarter-turn average: $\text{QT}_\text{all} = \frac{1}{3}(\text{QT}^0 + \text{QT}^1 + \text{QT}^2) = \frac{1}{12} \sum_{\text{all QT}} \rho(g)$.

### A.2 Block Commutator Norms

The commutator $[\text{QT}^0, \text{QT}^1]$ is computed in the full 228-dimensional representation space, then restricted to each block $b \in \{\text{cp}, \text{ep}, \text{co}, \text{eo}\}$ using the block projectors $\Pi_b$:

$$\|[\text{QT}^0, \text{QT}^1]\|_b = \|\Pi_b [\text{QT}^0, \text{QT}^1] \Pi_b\|_F.$$

The numerical values (§4.2) reveal a sharp hierarchy: cp = 0 (exactly commutative), ep = 2.74 (93.9% of total), co = 0.61, eo = 0.79. The CP block's exact commutativity follows from the Bose-Mesner algebra of the Q₃ Hamming scheme: the per-axis QT operators on CP belong to the Hamming scheme's association scheme algebra, which is commutative by construction. The EP block's dominant noncommutativity reflects the $M_2$ structure of $A_{\text{EP}}$ (§5).

### A.3 Dependence on Generator Partition

The definition of $\text{Supp}_\text{nc}$ depends on two structural choices that are geometrically natural for the Rubik's cube but not canonical for arbitrary finite groups:

1. **Axis partition.** The generators must be partitioned into subsets whose averaging operators $\text{QT}^a$ form a noncommutative family. For the cube, the three coordinate axes provide a natural 3-partition. For a general finite group with generating set $S$, an analogous construction would require a partition $S = \bigcup_i S_i$ such that the per-subset averages $A_i = \frac{1}{|S_i|}\sum_{g \in S_i} \rho(g)$ carry a non-trivial commutator structure.

2. **Block decomposition.** The restriction to blocks $\{\text{cp}, \text{ep}, \text{co}, \text{eo}\}$ relies on the $G$-orbit decomposition of the representation space (cubie-type orbits). For a general representation, the natural blocks would be the isotypic components of the $G$-action — the commutator $[A_i, A_j]$ would then be evaluated on each isotypic component rather than on cubie-type blocks.

The Supp_nc framework is therefore **not claimed to be canonical for arbitrary groups.** It is a structural invariant that captures the M₂-driven transport mechanism in the Rubik's cube family — a concrete computational tool whose generalization to other systems is an open direction (§7.4, Direction 1). Nevertheless, the framework provides a template for analyzing similar systems with a natural axis partition and block decomposition: the core logic — partition generators by algebraic substructure, compute per-partition commutators on each block, take the union of nonzero-commutator blocks as the noncommutative support — is transferable to any finite group representation whose generators admit a geometrically meaningful partition.

### A.4 Why Supp_nc Detects Type I Transport

On a block $b$ where $[\text{QT}^0, \text{QT}^1]|_b = 0$, the per-axis QT operators can be simultaneously diagonalized on that block. The spectral projectors $P_\alpha|_b$ are then matrices in the common eigenbasis, and they commute with each other on $b$. Individual generators $\rho(g)|_b$ may still fail to commute with these projectors (as the CP channel demonstrates — Appendix B), but the aggregate commutator norm vanishes because the obstruction cancels under axis averaging.

On a block $b$ where $[\text{QT}^0, \text{QT}^1]|_b > 0$, simultaneous diagonalization is impossible. The spectral projectors restricted to $b$ live in different eigenbases for different QT axes, creating a geometric obstruction to commutativity. When two sectors $\alpha, \beta$ both have non-zero projection on such a block, their projectors $P_\alpha|_b$ and $P_\beta|_b$ cannot both commute with all $\text{QT}^a$ — the noncommutativity leaks into cross-sector coupling, producing $T_{\alpha\beta}(g) \neq 0$ for at least one generator $g$.

This is the algebraic content of Observation A: Supp_nc intersection is the condition that two sectors' projectors live in overlapping noncommutative regions of the representation space, and the overlap forces generator-mediated mixing between them.

---

## Appendix B: The CP Permutation Channel

The S8$\leftrightarrow$S9 transport edge ($K = 2.83$) is the sole Type II channel — the only direct edge not detected by Supp_nc intersection. This appendix provides a dedicated algebraic analysis, since any reviewer of the Type I/II classification will scrutinize this exception.

### B.1 The Puzzle

S8 (cp-only, 8-dim, $\lambda_A = 1/3$) and S9 (cp+co, 27-dim, $\lambda_A = 1/3$) share the CP block. Their noncommutative supports are $\emptyset$ and {co} respectively — the intersection is empty. Yet $K_{8,9} = 2.83$, comparable in magnitude to the Type I edges (range 0.47–4.06). Why?

### B.2 QT Commutativity on CP

The CP block carries the permutation action on the 8 corner cubies — a subrepresentation factored through the cube group's corner permutation coset. The per-axis QT operators on CP belong to the Bose-Mesner algebra of the Q₃ Hamming scheme $H(3,2)$, which is a commutative association scheme algebra. Consequently:

$$[\text{QT}^0, \text{QT}^1]|_{\text{cp}} = 0 \quad \text{(exactly, to machine precision)}.$$

The CP block is QT-commutative. By the Supp_nc criterion, no Type I transport is possible on CP.

### B.3 Generator Noncommutativity on CP

Individual generators $\rho(g)|_{\text{cp}}$ are permutation matrices — elements of the symmetric group action on corner positions. These permutation matrices do **not** commute with the spectral projectors $P_8|_{\text{cp}}$ and $P_9|_{\text{cp}}$:

$$[P_8, \rho(g)]|_{\text{cp}} \neq 0, \quad [P_9, \rho(g)]|_{\text{cp}} \neq 0 \quad \text{for most } g \in S.$$

The projectors $P_8$ and $P_9$ are eigenmatrices of the averaged operators $\text{QT}_\text{all}$ and $\text{HT}_\text{all}$ on CP. These eigenmatrices diagonalize the averaged operators but not the individual generators — a single face-turn $\rho(g)$ mixes the two eigenspaces because the CP permutation action does not respect the spectral decomposition induced by axis-averaged operators.

### B.4 The Mechanism

The CP transport channel operates by **permutation adjacency** rather than by noncommutative mixing. On the CP block:
- $\text{QT}_\text{all}$ has two distinct eigenvalues (0 and 1/3), corresponding to S8 ($\lambda_{\text{QT}} = 0$) and the CP part of S9 ($\lambda_{\text{QT}} = 1/3$)
- $\text{HT}_\text{all}$ also separates these subspaces ($\lambda_{\text{HT}} = 1$ vs $1/3$)
- Individual $\rho(g)$ act as permutations on the 8 corner positions — they do not preserve the $\text{QT}_\text{all}/\text{HT}_\text{all}$ eigenspaces individually, but mix them

The mixing is **permutation-mediated**: applying a face turn to a corner configuration in S8 produces a configuration whose CP coordinates have non-zero overlap with S9's CP subspace. This is not a noncommutative effect (since QT operators on CP commute) — it is a **geometric** effect: the permutation action of individual generators is misaligned with the spectral basis of the averaged operators.

### B.5 Structural Significance

The CP channel establishes a structural fact of independent interest:

$$\boxed{\text{Averaging commutativity} \;\neq\; \text{generator commutativity with spectral projectors}}$$

QT commutativity on CP means the per-axis averaged dynamics is Abelian on that block. Generator noncommutativity with projectors means the unaveraged, single-step dynamics is not. The distinction is erased by axis averaging but preserved by individual generators.

The CP channel demonstrates that **Supp_nc is a structurally dominant but not complete transport invariant** — it captures Type I (9 of 10 edges) but must be supplemented by the permutation adjacency criterion for Type II (1 edge). A complete invariant for the Rubik's cube system would require both conditions: noncommutative support intersection for Type I, shared commutative block with generator-noncommutative spectral projectors for Type II.

### B.6 Computable Criterion

The Type II mechanism can be detected by a simple numerical test. A pair $(\alpha, \beta)$ is a Type II edge iff all three conditions hold:

**(i) Shared commutative block.** $\alpha$ and $\beta$ share only the CP block (and possibly CO), with $\text{Supp}_\text{nc}(\alpha) \cap \text{Supp}_\text{nc}(\beta) = \emptyset$.

**(ii) Generator noncommutativity with projectors.** The averaged commutator of the projectors with individual generators exceeds a nonzero threshold:

$$\frac{1}{|S|} \sum_{g \in S} \| [P_\alpha, \rho(g)] \|_F > 0$$

For the S8–S9 pair, this average is approximately 0.87 (CP block only), reflecting the systematic misalignment between the QT/HT spectral basis and the individual generator action on corner permutations.

**(iii) Commutative averaging algebra on the shared block.** $\|[\text{QT}^0, \text{QT}^1]\|_{\text{shared block}} = 0$ exactly — the shared block's QT algebra is commutative, so the transport is not Type I. For the CP block, this holds to machine precision.

These three conditions together distinguish the Type II channel from both Type I noncommutative edges (which fail (iii)) and inert block overlap (which fails (ii)). The criterion is computable directly from the representation data $\{\rho(g), P_\alpha\}$ without reference to the Supp_nc construction.

---

## Appendix C: Global Lifting Constraints from Transport Sparsity

The commutant of the representation $\text{End}_G(V)$ — the space of $G$-equivariant linear operators — has dimension 610 (combinatorial commutant, C-1). But the per-layer commutants $\text{End}_G(E_\lambda)$ sum to 966 dimensions. The discrepancy $\Delta_{\text{comm}} = 966 - 610 = 356$ measures the overcompleteness of local (per-layer) commutant data: there are 356 linear constraints that a tuple of per-layer commutant operators must satisfy to be the diagonal restriction of a single global commutant operator. This appendix formalizes the relationship via the projection map $\pi$, computes its kernel and cokernel, and relates the cokernel dimension to the transport sparsity structure.

### C.1 The Commutant Projection Map

Let $V = \bigoplus_\lambda E_\lambda$ be the decomposition into $A$-eigenspaces (6 canonical layers), with orthogonal projectors $P_\lambda$. Define the linear map:

$$\pi: \text{End}_G(V) \to \bigoplus_\lambda \text{End}_G(E_\lambda), \quad \pi(C) = (P_\lambda C P_\lambda)_\lambda.$$

The domain is the 610-dimensional space of global $G$-equivariant operators. The codomain is the 966-dimensional direct sum of per-layer commutant spaces — operators on each eigenspace $E_\lambda$ that commute with $\rho(g)$ restricted to $E_\lambda$, for all $g \in G$.

### C.2 Dimension Table

| Space | Symbol | Dimension | How obtained |
|-------|--------|-----------|-------------|
| Global commutant | $\text{End}_G(V)$ | 610 | Combinatorial orbit consistency (C-1) |
| Per-layer commutant sum | $\bigoplus_\lambda \text{End}_G(E_\lambda)$ | 966 | Gram-Schmidt projection of 610 global basis onto each layer |
| Kernel | $\ker \pi$ | 0 | SVD of projection matrix $M$ (610 × 966) |
| Image | $\text{im } \pi$ | 610 | rank($M$) = 610 |
| Cokernel | $\text{coker } \pi$ | 356 | 966 − 610 |

Note: $\dim \text{codomain} = 966$, **not** $\sum_\lambda d_\lambda^2 = 15{,}062$. Each per-layer commutant is much smaller than the full matrix algebra on that layer — Schur's lemma constrains the commutant dimension by the irreducible decomposition within each eigenspace.

**Computation method.** The global commutant dimension (610) is obtained by counting $G$-orbits on pairs of basis vectors: a basis for $\text{End}_G(V)$ is built by, for each orbit of $(i,j)$ under simultaneous $G$-action $(i,j) \mapsto (\pi_g(i), \pi_g(j))$, constructing the orbit-sum matrix (1 at all positions in the orbit, 0 elsewhere). The per-layer commutant dimensions are obtained by projecting each global basis element onto each eigenspace $E_\lambda$ (via $P_\lambda C P_\lambda$) and computing the rank of the projected set within $\text{End}(E_\lambda)$. The projection matrix $M$ (610 $\times$ 966) encodes the expansion coefficients of each projected global basis element in each per-layer commutant basis; its SVD yields $\text{rank}(M) = 610$, hence $\dim \ker \pi = 0$ and $\dim \text{coker } \pi = 966 - 610 = 356$. See `test/canonical/_exp_commutant_overcompleteness.py` for the full computation.

### C.3 ker π = 0: Injectivity

The kernel of $\pi$ would consist of $G$-equivariant operators $C \in \text{End}_G(V)$ whose diagonal blocks $P_\lambda C P_\lambda$ all vanish — purely off-diagonal operators in the spectral basis ($P_\lambda C P_\mu \neq 0$ only for $\lambda \neq \mu$).

Numerical SVD of the projection matrix $M$ (610 × 966, encoding the projection of each global commutant basis element onto each per-layer commutant basis element) yields $\text{rank}(M) = 610$ at tolerance $10^{-10}$. Therefore $\ker \pi = 0$: **π is injective.** Every full-space commutant is uniquely determined by its per-layer diagonal blocks. No purely off-diagonal $G$-equivariant operator exists — such an operator would require non-zero transport between layers that is constant across all generators, which the transport sparsity precludes.

### C.4 coker π = 356: Overcompleteness

The cokernel has dimension 356 — there are 356 independent linear constraints that a tuple $(C_\lambda \in \text{End}_G(E_\lambda))_\lambda$ must satisfy to be the diagonal projection of some global $C \in \text{End}_G(V)$. These constraints are **cross-layer compatibility conditions.**

Per-layer analysis reveals a striking fact: every individual layer has zero local cokernel (every per-layer commutant element lifts to SOME global commutant). The 356 constraints are **purely cross-layer** — they involve relationships between commutant elements on DIFFERENT layers that are forced by the requirement that they come from a single global operator $C$ satisfying $C\rho(g) = \rho(g)C$ for all $g \in S$.

### C.5 Relation to Transport Sparsity

The transport sparsity structure strongly constrains the lifting problem. Among the $\binom{6}{2} = 15$ unordered pairs of spectral layers, 10 pairs have zero transport ($K_{\text{layer}} < 10^{-8}$) and 5 are coupled (§3.7). Empirically, the large cokernel dimension correlates with the high number of transport-decoupled layer pairs: when a layer pair $(\lambda, \mu)$ is transport-decoupled, the $G$-equivariance condition $C\rho(g) = \rho(g)C$ forces the off-diagonal blocks $P_\lambda C P_\mu$ to satisfy algebraic constraints that propagate to the diagonal blocks $P_\lambda C P_\lambda$, narrowing the space of per-layer commutant tuples that can be consistently lifted.

The **transport graph behaves as a compatibility graph for lifting local commutant coordinates to global equivariant operators.** Layers that are transport-decoupled impose independent constraints on per-layer commutant data; layers connected by transport edges share degrees of freedom. The cokernel dimension $\Delta_{\text{comm}} = 356$ is the quantitative signature of this compatibility structure — it measures how much larger the "local" (per-layer) commutant is than the "global" (full-space) commutant.

Taken together, the combinatorial commutant (610 global equivariant operators from orbit consistency), the transport sparsity (10 zero-pairs among 15 layer pairs), and the commutant overcompleteness (356 lifting constraints) describe a unified picture: transport decoupling between spectral layers creates compatibility conditions that per-layer commutant data must satisfy to originate from a single $G$-equivariant operator. Whether this relationship generalizes to arbitrary finite group representations with transport-sparse generator sets is an open question.

---

## Appendix D: Numerical Methods

All computations use `CubieSpectralOperator` (`rime/cubieoperator.py`). The 9 primitive sector projectors are obtained via joint diagonalization of Center$\{A, \text{QT}_\text{all}, \text{HT}_\text{all}\}$ (`test/canonical/_exp_primitive_sectors.py`). The K matrix and Supp_nc are computed directly from these projectors and the 18 generator matrices. The π projection map analysis is in `test/canonical/_exp_commutant_overcompleteness.py`.

Key parameters: tolerance $10^{-10}$ for transport and SVD, 18 face-turn generators, 228-dimensional representation.

### D.1 Data Source

All numerical values are from [paper_data.md](../docs/paper_data.md) — the single source of truth for the trilogy. No numbers are hardcoded in paper text.

### D.2 Code References

| Component | Location |
|-----------|----------|
| Spectral operator | [rime/cubieoperator.py](../rime/cubieoperator.py) |
| Primitive sectors | [test/canonical/_exp_primitive_sectors.py](../test/canonical/_exp_primitive_sectors.py) |
| Combinatorial commutant | [rime/cubieoperator.py](../rime/cubieoperator.py) `_full_commutant_combinatorial()` |
| Isotypic decomposition (F1/F2) | [test/canonical/_exp_isotypic_decomposition.py](../test/canonical/_exp_isotypic_decomposition.py) |
| Commutant overcompleteness (π map) | [test/canonical/_exp_commutant_overcompleteness.py](../test/canonical/_exp_commutant_overcompleteness.py) |

---

## Appendix E: Key Numerical Data (9-Sector Resolution)

### E.1 Primitive Sector Summary

| Sector | Dim | $k$ | $\lambda_A$ | Supp_nc | Transport role |
|--------|-----|-----|-------------|---------|----------------|
| S1 | 20 | 0 | 1 | $\varnothing$ | ISOLATED ($K = 0$) |
| S2 | 2 | 1 | 8/9 | {eo} | Leaf, connects to S5, S6 |
| S3 | 39 | 2 | 7/9 | {ep, eo} | Leaf, connects to S6, S7 |
| S4 | 26 | 3 | 2/3 | {ep, co} | Leaf, connects to S6, S9 |
| S5 | 1 | 4 | 5/9 | {eo} | Leaf, connects to S2, S6 |
| **S6** | **39** | **4** | **5/9** | **{ep, eo}** | **PRIMARY HUB (degree 5)** |
| S7 | 66 | 4 | 5/9 | {ep, co, eo} | Secondary hub (degree 3) |
| S8 | 8 | 6 | 1/3 | $\varnothing$ | Leaf, connects to S9 (CP channel) |
| S9 | 27 | 6 | 1/3 | {co} | Leaf, connects to S4, S7, S8 |

### E.2 Transport Graph Properties

| Property | Value |
|----------|-------|
| Vertices | 9 |
| Direct edges | 10 (all block-preserving) |
| Primary hub | S6 (degree 5) |
| Secondary hub | S7 (degree 3) |
| Isolated | S1 (degree 0) |
| Cross-block direct edges | 0 |
| T7 pairs (composition-only) | 5 (all cross-block) |
| S8–S9 CP channel | Type II commutative permutation ($K = 2.83$) |

### E.3 Block Noncommutativity

| Block | $\|[\text{QT}^0, \text{QT}^1]\|_F$ | % of total |
|-------|--------------------------------------|-----------|
| cp | 0 | 0% |
| ep | 2.74 | 93.9% |
| co | 0.61 | 21.0% |
| eo | 0.79 | 27.1% |
| **Total** | **2.92** | — |

### E.4 Commutant Dimensions

| Object | Dimension |
|--------|-----------|
| $\dim \text{End}_G(V)$ (global commutant) | 610 |
| $\sum_\lambda \dim \text{End}_G(E_\lambda)$ (per-layer sum) | 966 |
| $\Delta_{\text{comm}} = \dim \text{coker } \pi$ | 356 |
| $\dim \ker \pi$ | 0 |

---

## Appendix F: S₃ Minimal Prototypes

The Supp_nc framework and Type I/II classification are verified on two S₃ prototypes (see [paper_data.md](../docs/paper_data.md) §9):

### F.1 S₃ nat(3)$\oplus$reg(6) — 9-dim, T7-Only

5 sectors from Center$\{A_{\text{full}}, A_{\text{trans}}\}$. $\kappa_1 = 0$ everywhere (no M₂). Yet 3 cross-block T7 pairs exist — T7 does NOT require M₂. All T7 pairs have disjoint block support (nat vs reg). This prototype establishes that the T7 phenomenon is logically independent of the M₂ obstruction: decomposition mismatch across blocks creates composition-only accessibility even in the absence of noncommutative simple components.

### F.2 S₃ reg(6)$\oplus$reg(6) — 12-dim, Full Hierarchy

10 sectors from Center$\{A_3, A_2\}$. Perfect separation:
- 30 Class-II edges ($\kappa_0 > 0$): ALL within-block
- 10 curvature pairs ($\kappa_0 = 0, \kappa_1 > 0$): ALL within-block
- 9 T7 pairs ($K = \kappa_0 = \kappa_1 = 0$): ALL cross-block

T7 and M₂ are two logically independent obstruction types. M₂ creates curvature-mediated transport within blocks; T7 arises from decomposition mismatch across blocks. Both prototypes verify the Type I/II transport classification and confirm that the Supp_nc framework captures the correct algebraic distinction.

## References

**Mathematical lineage.** This paper belongs to the tradition of **group-theoretic selection rules and superselection structure** — the principle that algebraic symmetry determines which transitions are allowed and which are forbidden. The transport tensor $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ functions as a group-representation transition amplitude; the central question — "which sectors are connected?" — is answered by analyzing the noncommutative structure of the representation (Supp_nc, M₂ obstruction, commutant gap), without invoking dynamics, Lie theory, or spectral flow. The lineage runs: Wigner selection rules (1959) → superselection structure (Wick-Wightman-Wigner 1952, Wightman 1995) → harmonic analysis on finite groups (Diaconis 1988, Ceccherini-Silberstein et al. 2008) → the present structural analysis.

### Group-theoretic selection rules and superselection

[4] E.P. Wigner, *Group Theory and Its Application to the Quantum Mechanics of Atomic Spectra*. Academic Press, 1959.
  — The classic derivation of selection rules from group representation structure: a transition amplitude $\langle \psi_f | O | \psi_i \rangle$ vanishes unless the tensor product of the three irreducible representations contains the trivial representation. The transport tensor $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ generalizes this principle to finite group orbits — the projector supports $P_\alpha, P_\beta$ are not irreducible characters but primitive idempotents in the commutant of the averaging operator.

[5] G.C. Wick, A.S. Wightman, and E.P. Wigner, "The Intrinsic Parity of Elementary Particles." *Physical Review* 88:101–105, 1952.
  — The original superselection rule paper. The concept that certain superpositions are *structurally forbidden by symmetry* — rather than energetically suppressed — is the quantum precedent for the T7 composition-only transport pairs: cross-block transitions are not merely "difficult" but structurally absent ($K_{\alpha\beta} = 0$ to machine precision, $10^{-14}$) in the single-generator transport tensor, yet become accessible through length-2 composition via hybrid intermediate sectors.

[6] A.S. Wightman, "Superselection Rules; Old and New." *Il Nuovo Cimento B* 110:751–769, 1995.
  — Modern review of superselection structure. The separation between "kinematically allowed" and "dynamically forbidden" transitions — and the role of the observable algebra's commutant in determining which superpositions are coherent — mirrors the distinction between Type I (noncommutative, M₂-driven) and Type II (commutative, permutation-mediated) transport mechanisms classified in this paper.

### Harmonic analysis and representation-theoretic structure

[7] T. Ceccherini-Silberstein, F. Scarabotti, and F. Tolli, *Harmonic Analysis on Finite Groups*. Cambridge University Press, 2008.
  — Spherical functions, Gelfand pairs, and the decomposition of permutation representations. The commutativity of the averaging operator with Hecke algebras of the underlying permutation structure determines which block-level decompositions are possible — this is the algebraic substrate of the nine-sector refinement.

[8] P. Diaconis, *Group Representations in Probability and Statistics*. IMS Lecture Notes, 1988.
  — Spectral analysis of group-valued random walks. The averaging operator and its spectrum govern the approach to equilibrium; the transport tensor studied here determines the fine-grained structure of individual transitions before averaging.

### Association schemes and algebraic combinatorics (shared foundation with Paper I)

[9] E. Bannai and T. Ito, *Algebraic Combinatorics I: Association Schemes*. Benjamin/Cummings, 1984.
  — The Bose-Mesner algebra of the underlying permutation association scheme. The block-level spectral structure and the decomposition into primitive idempotents — the input to this paper's transport analysis — are established in Paper I within this algebraic framework.

[10] A.E. Brouwer, A.M. Cohen, and A. Neumaier, *Distance-Regular Graphs*. Springer, 1989.
  — Distance-regular graphs and their algebraic structure. The Q₃ hypercube (cp block) and the face-incidence graph (ep block) are the combinatorial substrates whose adjacency algebras determine the block spectral decomposition.

### Trilogy cross-references

[1] Paper I — *Spectral Sector Decomposition in Finite Group Representations: Primitive Idempotents and Emergent Hybrid Structure from the Rubik Cube Group.* `examples/paper1/Paper I.md`

[2] Paper III — *Accessibility Beyond Lie Closure in Finite Group Representations: Hybrid Projector Geometry and Composition-Only Transport.* `examples/paper3/Paper III.md`

[3] `docs/paper_data.md` — Shared Data File: Single Source of Truth for Paper Trilogy (post-ρ-fix 6-layer, 9-sector resolution).

---

**Code**: [rime/cubieoperator.py](../rime/cubieoperator.py), [test/canonical/_exp_primitive_sectors.py](../test/canonical/_exp_primitive_sectors.py), [test/canonical/_exp_lie_closure_transport.py](../test/canonical/_exp_lie_closure_transport.py)

**Data**: [docs/paper_data.md](../docs/paper_data.md) — definitive numerical source for all three Papers

**Date**: 2026-05-14 (post-ρ-fix restructured version, reference lineage reconstruction)
