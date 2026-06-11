# Noncommutative Transport Topology in the Rubik's Cube Representation

### Hybrid Sectors, Permutation Channels, and Refinement Obstructions

**WuJun Chen**

Independent Researcher · RIME Project · 2026

*This paper is Part II of the RIME trilogy. Paper I established the spectral decomposition and primitive sector structure. The present paper studies transport topology and the M₂ Principle. Paper III develops Lie accessibility and proves the T7 Theorem.*

***

## Abstract

**Problem.** Previous work established that the averaging operator $A$ decomposes the 228-dimensional Rubik's cube representation into nine primitive sectors (minimal center-joint eigenspaces, not primitive idempotents or irreducible components). However, the resulting spectral decomposition is static: it identifies the sectors but does not characterize which sectors can exchange amplitude under a single generator. This paper studies the resulting transport topology.

**Approach.** Direct transport between sectors is governed by **noncommutative support** — the set of representation blocks on which a sector projects and on which the per-axis quarter-turns fail to commute. The intersection of noncommutative supports of two sectors is observed as an exact criterion for noncommutative (Type I) direct transport across all verified Rubik sectors. A single commutative-permutation (Type II) channel arises separately from CP block adjacency.

**Results.** All 10 direct edges of the transport graph are block-preserving: 9 noncommutative edges driven by the M₂ components of $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$, and one commutative-permutation edge S8↔S9. Cross-block transport in the Rubik system requires length-2 composition (T7 morphisms), satisfying neither Type I nor Type II criterion at depth 1.

**Implications.** The transport topology is not automatic — it requires center incompleteness ($Z \subsetneq C(\rho)$). The M₂ algebra of $A_{\mathrm{EP}}$ forces hub formation (S6), caps refinement at 9 sectors, and explains the absence of direct cross-block edges. \cite{paper3} develops the Lie-accessibility consequences of this transport topology and proves that cross-block compositional accessibility strictly exceeds Lie-generated accessibility: $\mathcal{L} \subsetneq \overline{\mathcal{T}}$.

***

## Notation Table

| Symbol | Meaning | Origin |
|--------|---------|--------|
| $A = \frac{1}{\|S\|}\sum_{s} \rho(s)$ | Averaging operator — Hermitian, rational spectrum | Paper I |
| **layer** $V_\lambda$ | An eigenspace of $A$; 6 canonical layers ($\lambda = 1 - k/9$) | Paper I |
| **block** | Cubie-type invariant component: cp (corner perm, 64-dim), ep (edge perm, 144-dim), co (corner ori, 8-dim), eo (edge ori, 12-dim) | Paper I |
| **primitive sector** $S_\alpha$ | Minimal joint eigenspace of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ (9 total) | Paper I |
| $P_\alpha$ | Projector onto primitive sector $\alpha$ | Paper I |
| **hybrid sector** | A primitive sector with support spanning multiple cubie-type blocks (e.g., ep+eo) | Paper I |
| **S1–S9** | 9 primitive sectors: S1(V₁, isolated), S2(V₈/₉), S3(V₇/₉), S4(V₂/₃), S5–S7(V₅/₉; S6 primary hub), S8–S9(V₁/₃) | Paper I |
| $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ | Transport tensor — amplitude moved by single generator $g$ from $\beta$ to $\alpha$ | **this paper** |
| $K_{\alpha\beta} = \max_g \lVert P_\alpha \rho(g) P_\beta\rVert_F$ | Direct transport norm — aggregate transport strength under optimal single generator | **this paper** |
| $\operatorname{Supp}_{\mathrm{nc}}(\alpha)$ | Noncommutative support — $\{b : P_\alpha\vert_b \neq 0 \text{ and } \lVert[\mathrm{QT}^0, \mathrm{QT}^1]\rVert_b > 0\}$ | **this paper** |
| **Type I** | Transport via shared noncommutative support (9 of 10 direct edges, M₂-driven) | **this paper** |
| **Type II** | Transport via commutative permutation block — 1 edge S8↔S9 ($K = 2.83$, CP-mediated) | **this paper** |
| $\mathrm{M}_2$ Principle | $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ (20-dim semisimple) — algebraic origin of Type I transport | **this paper** |
| $\mathrm{QT}^a$, $\mathrm{HT}^a$ | Quarter-turn / half-turn averaging operators on axis $a \in \{0,1,2\}$ | Paper I |
| $\mathrm{QT}_{\mathrm{all}} = \sum_a \mathrm{QT}^a$, $\mathrm{HT}_{\mathrm{all}} = \sum_a \mathrm{HT}^a$ | Total quarter-turn / half-turn averaging | Paper I |
| $Z = \langle A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}} \rangle$ | Transport center — the commuting algebra that jointly diagonalizes to yield 9 primitive sectors | Paper I |
| $C(\rho)$ | Full commutant of the representation — $\{X : [X, \rho(g)] = 0 \; \forall g \in G\}$ | — |
| $\operatorname{Comm}(\cdot)$ | Commutant algebra — $\{X : [X,Y] = 0 \; \forall Y \in (\cdot)\}$ | — |
| **C0** (Center Incompleteness) | $Z \subsetneq C(\rho)$ — the structural precondition for off-diagonal transport; when equality holds, $K$ is purely diagonal | **this paper** |
| **T7 morphism** | Cross-block morphism outside Lie-generated accessibility — $K_{\alpha\beta}=0$ yet reachable via length-2 composition through a hybrid sector | Paper III |

Full notation glossary: `docs/conventions.md` and (CCS Part 0).

***

## Introduction

**Conventions.** We use a right-handed Cartesian coordinate system ($+X \to R$, $+Y \to U$, $+Z \to F$). The representation space $V = \mathbb{C}^{228}$ decomposes as $V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}}$ ($64 + 144 + 8 + 12$) in cp $\to$ ep $\to$ co $\to$ eo order. The generator set $S$ is the 18 standard face-turn generators ($S = S^{-1}$), partitioned naturally by coordinate axis: $\mathrm{QT}^a = \frac{1}{2}(\rho(+a) + \rho(-a))$ for $a \in \{0,1,2\}$. Full conventions: `docs/conventions.md`. All numerical values: (CCS-I §2).

### What Paper I Left Open

\cite{paper1} established the spectral ontology of the averaging operator $A = \frac{1}{|S|} \sum_{g \in S} \rho(g)$. Its central deliverables: (i) the rational 6-layer spectrum $\lambda = 1 - k/9$, $k \in \{0, 1, 2, 3, 4, 6\}$; (ii) the block origin of each layer via Bose–Mesner algebras on four cubie-type blocks; (iii) the refinement to 9 primitive sectors under Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$.

\cite{paper1} answers: *what is the spectral object?* But the spectral decomposition of $A$ is a static object — it tells us nothing about which sectors can exchange amplitude under individual generators.

That is the question of this paper.

### The Transport Question

Individual generators $\rho(g)$ do **not** preserve the spectral sectors. For any two sectors $\alpha, \beta$, the off-diagonal block

$$T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$$

measures how much generator $g$ transports amplitude from sector $\beta$ to sector $\alpha$. The aggregate transport strength

$$K_{\alpha\beta} = \max_{g \in S} \|T_{\alpha\beta}(g)\|_F$$

defines a weighted undirected graph on the 9 primitive sectors. The paper addresses three structural questions:

> **Q1. Why does the transport topology emerge?** Why are some pairs coupled ($K > 0$) and others not ($K = 0$)? The answer is not eigenvalue proximity, and not block support overlap alone — it requires identifying a structural invariant.
>
> **Q2. Why does refinement stop at 9?** The 9 primitive sectors are the finest decomposition achievable within the commutative center. What algebraic obstruction blocks further refinement?
>
> **Q3. Why do two transport types exist?** The S8$\leftrightarrow$S9 edge is fundamentally different from all others — it reveals that averaging commutativity $\neq$ generator commutativity.

### The Central Objects

This paper is built from four mathematical objects. The transport tensor $T_{\alpha\beta}(g)$, its aggregate norm $K_{\alpha\beta}$, the noncommutative support $\operatorname{Supp}_{\mathrm{nc}}$, and the EP block algebra $A_{\text{EP}}$:

$$\boxed{A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4 \;\Rightarrow\; \operatorname{Supp}_{\mathrm{nc}} \;\Rightarrow\; K_{\alpha\beta} \;\Rightarrow\; \text{Transport graph}}$$

The chain is structural: the M₂ components of $A_{\text{EP}}$ create noncommutative supports on sectors; $\operatorname{Supp}_{\mathrm{nc}}$ (the set of transport-active noncommutative blocks) determines which pairs have Type I transport (9 of 10 edges); the K matrix records the resulting transport strengths; the transport graph is the shadow of Supp_nc geometry cast onto the 9-sector decomposition.

**Noncommutative support** (Definition~\ref{def:noncommutative-support}) is the dominant structural invariant for Type I transport:

$$\operatorname{Supp}_{\mathrm{nc}}(\alpha) = \{b \in \{\mathrm{cp}, \mathrm{ep}, \mathrm{co}, \mathrm{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[\mathrm{QT}^0, \mathrm{QT}^1]\|_b > 0\}.$$

The four blocks have sharply different noncommutativity: cp is exactly commutative, ep carries 93.9% of the total, co and eo carry weak sidebands (CCS-I §2.1). Supp_nc detects transport because on a block where per-axis QT operators fail to commute, simultaneous diagonalization is impossible — the noncommutativity leaks into cross-sector coupling.

**Two independent transport mechanisms** emerge:

| Type | Mechanism | Criterion | Count |
|------|-----------|-----------|-------|
| **Type I** | Noncommutative mixing (M₂-driven) | $\operatorname{Supp}_{\mathrm{nc}}(\alpha) \cap \operatorname{Supp}_{\mathrm{nc}}(\beta) \neq \emptyset$ | 9 edges |
| **Type II** | Commutative permutation (CP adjacency) | Shared CP + generator-noncommutative projectors | 1 edge (S8$\leftrightarrow$S9) |

Type II reveals a structural fact: **averaging commutativity $\neq$ generator commutativity**. The CP block's QT algebra is exactly commutative, yet individual generators are non-trivial permutation matrices that mix spectral projectors. Transport can exist without QT noncommutativity — a second, qualitatively distinct mechanism.

Both types are block-preserving. Cross-block transport requires length-2 composition. The five such pairs (T7) satisfy neither Type I nor Type II criterion (CCS-I §2.5). The Type I/II taxonomy is verified on the Rubik's cube (228-dim). The S₃ negative controls (CCS-I §2.11, Appendix G) confirm: their transport center coincides with the full commutant (Z = C(ρ)), forcing purely diagonal K and zero cross-block transport — demonstrating that hybrid sectors alone are insufficient for nontrivial transport topology.

**Theorem (M₂ Principle).** The edge-permutation block algebra $A_{\text{EP}} = \langle Q_0, Q_1, Q_2 \rangle \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ (20-dim semisimple) is the algebraic origin of the transport architecture. Its consequences form four structural observations:

1. **Observation A (Two-Type Transport)** — Type I via Supp_nc intersection; Type II via CP permutation adjacency
2. **Observation B (Hub Necessity)** — the three active M₂ components force a unique hub sector (S6) intersecting all of them
3. **Observation C (Refinement Obstruction)** — M₂ noncommutativity blocks further spectral refinement, capping decomposition at 9 sectors
4. **Observation D (Transport Topology)** — all direct edges block-preserving, S1 isolated, S6 primary hub (deg 5), cross-block requires T7 morphisms (\cite{paper3})

A **transport hub** is a sector with high transport degree and concentrated noncommutative overlap geometry — it sits at the intersection of multiple $\operatorname{Supp}_{\mathrm{nc}}$ regions, routing transport between sectors that would otherwise be disconnected.

### Relation to the Trilogy

| Paper | Object | Question |
|-------|--------|----------|
| Paper I | $A = \frac{1}{\|S\|}\sum \rho(s)$ | What is the spectral object? |
| **Paper II** | $K_{\alpha\beta}$, $\operatorname{Supp}_{\mathrm{nc}}$, $A_{\mathrm{EP}}$ | **Where does the transport topology come from?** |
| Paper III | $\kappa_d$, T7 morphisms | Why does compositional accessibility exceed Lie-generated accessibility? |

This paper studies **static transport topology** — which edges exist, and why. \cite{paper3} studies **dynamical accessibility** — what trajectories can traverse those edges. The boundary is clean: this paper identifies the transport graph; \cite{paper3} proves that compositional accessibility exceeds Lie-generated accessibility. No Lie-generated accessibility, $\kappa_d$ hierarchy, $A_g = \log\rho(g)$, or curvature belong to this paper. The question is structural, not dynamical: *where does the transport graph come from?*

***

## Part I — Transport Category {-}

## Primitive Sectors and Block Structure

### Representation Space

The Rubik's cube representation $\rho: G \to \text{GL}(228, \mathbb{C})$ decomposes into four block-diagonal subspaces:

$$V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}}$$

| Block | Dim | Algebraic structure |
|-------|-----|---------------------|
| cp (corner permutation) | 64 | Q₃ Hamming scheme H(3,2), Bose–Mesner $\cong$ Hecke $H(S_2 \wr S_3, S_3)$ |
| ep (edge permutation) | 144 | $A_{\text{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ |
| co (corner orientation) | 8 | Z₃ phase structure |
| eo (edge orientation) | 12 | Z₂ phase structure |

Per-block noncommutativity hierarchy: see below (The Noncommutativity Hierarchy).

Total dimension: $64 + 144 + 8 + 12 = 228$.

The generator set $S$ consists of the 18 standard face-turn generators (6 faces $\times$ 3 turns). $S$ is closed under inversion.

### Six Canonical Layers (A-Eigenspaces)

The averaging operator $A = \frac{1}{18} \sum_{g \in S} \rho(g)$ has 6 distinct eigenvalues. Each eigenspace $E_\lambda = \text{im}(P_\lambda)$ is characterized by its block-support profile:

| $k$ | $\lambda = 1 - k/9$ | Dim | Label | Block composition |
|-----|---------------------|-----|-------|-------------------|
| 0 | 1 | 20 | V₁ | cp(8) + ep(12) |
| 1 | 8/9 | 2 | V₈/₉ | eo(2) |
| 2 | 7/9 | 39 | V₇/₉ | ep(36) + eo(3) |
| 3 | 2/3 | 26 | V₂/₃ | ep(24) + co(2) |
| 4 | 5/9 | 106 | V₅/₉ | cp(24) + ep(72) + co(3) + eo(7) |
| 6 | 1/3 | 35 | V₁/₃ | cp(32) + co(3) |

$k = 5$ ($\lambda = 4/9$) is genuinely absent — no blockwise primitive idempotent produces it. The 10 block-level primitive idempotents collapse to exactly 6 global spectral layers via eigenvalue coincidence $\lambda = 1 - k/m$ across different blocks (Paper I, Theorem~\ref{thm:block-compatibility-lemma}).

### Nine Primitive Sectors

Joint diagonalization of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ refines the 6 layers into **9 primitive sectors** — the finest decomposition achievable within the commutative center:

| Sector | Dim | $k$ | $\lambda_A$ | $\lambda_{\mathrm{QT}}$ | $\lambda_{\mathrm{HT}}$ | Block support | Layer |
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

### The Noncommutative Support of Each Sector

Applying Definition~\ref{def:noncommutative-support} to the 9 sectors:

| Sector | Supp_nc | Description |
|--------|---------|-------------|
| S1 | $\varnothing$ | ISOLATED — ep support falls in commutative $M_1$ subalgebra (see Supp_nc Definition below) |
| S2 | {eo} | Pure EO, weakly noncommutative |
| S3 | {ep, eo} | EP + EO, both noncommutative |
| S4 | {ep, co} | EP + CO, both noncommutative |
| S5 | {eo} | Pure EO, weakly noncommutative |
| **S6** | **{ep, eo}** | **PRIMARY HUB — intersects with 5 other sectors' Supp_nc** |
| S7 | {ep, co, eo} | Mixed — intersects with S3, S4, S6, S9 |
| S8 | $\varnothing$ | Pure CP — commutative block only |
| S9 | {co} | CP+CO — only CO is noncommutative |

The pattern is striking: **S1 and S8 are the only sectors with empty Supp_nc.** S1 is genuinely isolated ($K = 0$ with all sectors). S8 has $K > 0$ with S9 via shared CP block — the exception that proves the rule: commutative blocks can mediate transport between sectors that share them, but they cannot create *new* transport channels between sectors with disjoint noncommutative supports.

The Block→Sector→Transport alluvial diagram (three panels: block algebra → spectral decomposition → transport topology) is in the Unified Computational Supplement (CCS Fig. C17; formerly Fig. C8).

***

## The Transport Tensor and K Matrix

### Definition

**Definition 3.1** (Transport Tensor). For primitive sectors $\alpha, \beta$ with orthogonal projectors $P_\alpha, P_\beta$, the *transport block* for generator $g \in S$ is

$$T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta.$$

This is a $(\dim \alpha) \times (\dim \beta)$ matrix encoding how generator $g$ moves amplitude from sector $\beta$ to sector $\alpha$.

**Definition 3.2** (Transport Graph Matrix). The aggregate transport strength between sectors is

$$K_{\alpha\beta} = \max_{g \in S} \|T_{\alpha\beta}(g)\|_F.$$

$K$ defines a weighted graph on the 9 primitive sectors. $K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F$ is symmetric ($K_{\alpha\beta} = K_{\beta\alpha}$ to $10^{-15}$) because $\|X\|_F = \| X^T\|_F$ and $P_\beta \rho(g)^T P_\alpha = P_\beta \rho(g^{-1}) P_\alpha$, with $g^{-1} \in S$ (the generator set is inverse-closed). The transport graph is therefore undirected.

### The K Matrix at 9-Sector Resolution

The complete $K_{\alpha\beta}$ matrix at 9-sector resolution is tabulated in (CCS-I §2.2). The matrix is symmetric to $10^{-15}$, has 10 off-diagonal entries with $K > 0.01$, and exhibits the sparsity pattern shown in Fig.~\ref{fig:fig1-k-heatmap}. The diagonal entries $K_{\alpha\alpha} = \max_g \|P_\alpha \rho(g) P_\alpha\|_F$ measure intra-sector transport strength.

![The $9 \times 9$ transport matrix heatmap at 9-sector resolution: color encodes $K_{\alpha\beta}$, circle markers mark 9 Type I noncommutative edges, and the purple border marks the lone Type II CP permutation channel S8$\leftrightarrow$S9. Of 36 sector pairs, exactly 10 have $K_{\alpha\beta} > 0$; all remaining pairs are disconnected. The transport topology is the shadow of the M$_2$ components in $A_{\mathrm{EP}}$, not an empirical observation.](../../figures/paper2/fig1_k_heatmap.png)

### Direct Edges (K > 0.01)

10 direct edges. All share $\geq 1$ block. K values canonical to 2 decimal places; full precision in (CCS-I §2.2).

| Edge | $K$ | Shared block | Supp_nc intersection | Type |
|------|-----|-------------|---------------------|------|
| S2(eo)$\leftrightarrow$S5(eo) | 0.47 | eo | {eo} | Type I |
| S2(eo)$\leftrightarrow$S6(ep+eo) | 0.58 | eo | {eo} | Type I |
| S3(ep+eo)$\leftrightarrow$S6(ep+eo) | 2.55 | ep, eo | {ep, eo} | Type I |
| S3(ep+eo)$\leftrightarrow$S7(ep+co+eo) | 3.61 | ep, eo | {ep, eo} | Type I |
| S4(ep+co)$\leftrightarrow$S6(ep+eo) | 3.46 | ep | {ep} | Type I |
| S4(ep+co)$\leftrightarrow$S9(cp+co) | 1.00 | co | {co} | Type I |
| S5(eo)$\leftrightarrow$S6(ep+eo) | 0.82 | eo | {eo} | Type I |
| S6(ep+eo)$\leftrightarrow$S7(ep+co+eo) | 3.61 | ep, eo | {ep, eo} | Type I |
| S7(ep+co+eo)$\leftrightarrow$S9(cp+co) | 4.06 | cp, co | {co} | Type I |
| S8(cp)$\leftrightarrow$S9(cp+co) | 2.83 | cp | $\emptyset$ | **Type II** |

All 10 edges are block-preserving (share $\geq 1$ block). Each edge is mediated by one or more blocks; the per-block participation counts below are overlap counts — edges with multiple shared blocks appear in multiple lists. EP participates in 4 edges (S3–S6, S3–S7, S4–S6, S6–S7); EO participates in 6 edges (S2–S5, S2–S6, S3–S6, S3–S7, S5–S6, S6–S7); CO participates in 2 edges (S4–S9, S7–S9); CP participates in 2 edges (S7–S9, S8–S9). For S7–S9, both CP and CO are present; transport is associated with the CO channel, while CP appears only as a commutative sideband. The S8–S9 edge is the unique Type II channel. The S6 hub (Supp_nc = {ep, eo}) appears in 5 of 10 edges.

The sole Type II edge is S8$\leftrightarrow$S9 ($K = 2.83$, CP permutation channel, see Appendix B). 9 of 10 edges are Type I (Supp_nc intersection).

### Hub Degrees

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

The Transport Skeleton diagram (pure connectivity geometry with S6 primary hub, noncommutative core cluster, S8–S9 CP channel, and S1 isolation) is in the Unified Computational Supplement (CCS Fig. C16; formerly Fig. C3).

### Transport Topology as Consequence of Supp_nc Geometry

**Theorem (Transport Topology).** The transport graph at 9-sector resolution has the following properties, all of which follow from Supp_nc geometry (Observation A) and the M₂ obstruction (Observations B, C):

1. **All direct edges are block-preserving** — every $K_{\alpha\beta} > 0$ pair shares $\geq 1$ block. Zero cross-block direct edges. (Direct corollary of Paper~III, Lemma~\ref{lem:pure-sector-obstruction}, applying Schur's lemma to the block-diagonal $\rho$: $T_{\alpha\beta}(g) = 0$ whenever $\alpha, \beta$ share no block. Type I Supp_nc intersection and Type II CP adjacency both respect this block-locality.)
2. **S1 is fully isolated** — $K_{1,\beta} = 0$ for all $\beta \neq 1$. S1 is a $G$-invariant subrepresentation. (Supp_nc(S1) = $\emptyset$ and no Type II CP adjacency)
3. **S6 is the primary hub** — degree 5, the unique sector whose Supp_nc = {ep, eo} intersects 5 other sectors' noncommutative supports. (Observation B: M₂ overlap forces hub formation)
4. **S7 is the secondary hub** — degree 3, Supp_nc = {ep, co, eo} bridges EP, CO, and EO blocks. (Corollary of Observation B)
5. **Cross-block T7 morphisms** — 5 sector pairs with disjoint Supp_nc have $K = 0$ but are reachable via length-2 paths through the S6–S7–S9 hub complex. (Observation A: neither Type I nor Type II criterion met $\implies K = 0$)

Figure~\ref{fig:fig5-s6-hub-signature} shows the full transport graph with hub structure, Type I/II edges, and T7 cross-block pairs.

![The 9-sector transport graph with Type I edges (noncommutative, 9), Type II edge (CP permutation, S8--S9), and T7 cross-block pairs (dashed, 5), weighted by transport strength. S6 is the primary hub (degree 5) with noncommutative support {ep, eo} intersecting 5 other sectors; S7 is the secondary hub (degree 3) bridging EP, CO, and EO blocks; S1 is fully isolated. The hub structure is forced by the M$_2$ algebra of $A_{\mathrm{EP}}$, not by parameter tuning.](../../figures/paper2/fig5_s6_hub_signature.png)

The transport graph is not an empirical observation — it is the **shadow of Supp_nc geometry**, cast onto the 9-sector decomposition by the M₂ components of $A_{\text{EP}}$.

### S1 Isolation

S1 (V₁, 20-dim, cp+ep) has $K < 10^{-14}$ with all other 8 sectors — the unique fully decoupled, $G$-invariant subrepresentation. Its Supp_nc = $\emptyset$ because its 12-dimensional ep support lies entirely within the $M_1(\mathbb{C})^4$ commutative component of $A_{\text{EP}}$, carrying no $M_2$ structure (detailed in Supp_nc Definition and Computation below).

### Transport Sparsity Is Not Eigenvalue Proximity

The K matrix makes visible a fundamental fact: eigenvalue ordering and transport adjacency are independent structures. S3 (V₇/₉, $\lambda = 7/9$) and S4 (V₂/₃, $\lambda = 2/3$) are adjacent in the eigenvalue sequence yet have $K = 0$. S3 and S7 (V₅/₉, $\lambda = 5/9$) are non-adjacent yet have $K = 3.61$. An observer who knows only the eigenvalues and their multiplicities cannot predict which sectors are coupled.

***

## Part II — Supp_nc: The Dominant Type I Structural Invariant {-}

## Noncommutative Support Determines Transport

**Why the Rubik transport topology is nontrivial.** The transport graph acquires off-diagonal edges only because the sector-decomposing center $Z = \langle A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\rangle$ is a proper subalgebra of the full commutant $C(\rho)$. When $Z = C(\rho)$ — center completeness — sectors equal isotypic components, $P_i\rho(g)P_j = 0$ for all $i \neq j$, and $K$ is purely diagonal. The S₃ negative controls (CCS Appendix G) provide negative control: both have $Z = C(\rho)$ and purely diagonal $K$, despite carrying noncommutative support. The Rubik cube satisfies $Z \subsetneq C(\rho)$ massively: 9 sectors aggregate 51 isotypic components, creating non-invariant sectors whose off-diagonal transport is structurally possible. Center incompleteness (C0) is the structural precondition for the transport topology studied in this Part.

### Why Block Support Overlap Is Not Sufficient

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

### The Noncommutativity Hierarchy

The key insight is that the four blocks have sharply different algebraic character:

$$\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_F = 2.92 \text{ total}$$

| Block | $\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_F$ | % of total | Algebra |
|-------|--------------------------------------|-----------|---------|
| cp | 0 | 0% | $\mathbb{C}[A_{\mathrm{cp}}]$ exactly commutative |
| ep | 2.74 | 93.9% | $M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ — **dominant** |
| co | 0.61 | 21.0% | Weak noncommutative sideband |
| eo | 0.79 | 27.1% | Weak noncommutative sideband |

*Percentages are per-block Frobenius norm ratios $\|[\mathrm{QT}^0,\mathrm{QT}^1]\|_b / \|[\mathrm{QT}^0,\mathrm{QT}^1]\|_F$, not additive fractions; they do not sum to 100% because the per-block norms add in quadrature ($0^2 + 2.74^2 + 0.61^2 + 0.79^2 = 2.92^2$).*

The CP block is **exactly commutative**: all per-axis QT operators commute when restricted to CP. While individual generators $\rho(g)$ on CP are non-trivial permutation matrices, the averaged QT operators form a commutative algebra — the Q₃ Hamming scheme's Bose–Mesner algebra.

The EP block carries 93.9% of the total noncommutativity (by Frobenius-norm ratio). CO and EO carry weak sidebands.

### Supp_nc Definition and Computation

**Definition 4.1** (Noncommutative Support). For a primitive sector $\alpha$,

$$\operatorname{Supp}_{\mathrm{nc}}(\alpha) = \{b \in \{\mathrm{cp}, \mathrm{ep}, \mathrm{co}, \mathrm{eo}\} : P_\alpha|_b \neq 0 \text{ and } \|[\mathrm{QT}^0, \mathrm{QT}^1]\|_b > 0\}.$$

Equivalently: the set of blocks on which the sector has non-zero projection AND the block's per-axis QT operators fail to commute.

| Sector | Block support | Supp_nc | $\|\operatorname{Supp}_{\mathrm{nc}}\|$ |
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

**S8 has Supp_nc = $\emptyset$** because it has only CP support, and CP is exactly commutative. Figure~\ref{fig:fig2-supp-nc-mechanism} classifies all 36 sector pairs by transport mechanism.

![Transport mechanism classification for all 36 sector pairs: Type I (noncommutative overlap, 9 edges, $K = 0.47$--$4.06$), Type II (CP permutation adjacency, 1 edge, S8$\leftrightarrow$S9 $K = 2.83$), T7 (cross-block composition-only, 5 pairs, $K = 0$), and Inert (21 pairs, no transport). Three criteria — block overlap, noncommutative support intersection, and CP adjacency — classify all 36 pairs without ambiguity. Supp$_{\mathrm{nc}}$ intersection is the exact criterion for Type I transport across all verified Rubik sectors.](../../figures/paper2/fig2_supp_nc_mechanism.png)

### Transport Mechanism Classification

**Proposition (Two-Type Transport Mechanisms).** For any two distinct primitive sectors $\alpha \neq \beta$, direct transport arises from exactly one of two independent mechanisms:

**Type I — Noncommutative mixing.** For all 9 non-CP transport edges, $\operatorname{Supp}_{\mathrm{nc}}(\alpha) \cap \operatorname{Supp}_{\mathrm{nc}}(\beta) \neq \emptyset$ is observed as an exact criterion for direct transport: $K_{\alpha\beta} > 0$.
The M₂ components of $A_{\text{EP}}$ (and weak CO/EO sidebands) create generator mixing that couples sectors sharing noncommutative block support.
Within the Rubik's cube representation, no sector pair with overlapping noncommutative support has zero transport, and no sector pair (outside the CP channel) with non-zero transport has disjoint noncommutative support.
This accounts for 9 of 10 direct edges.

**Type II — Commutative permutation transport.** S8(cp)$\leftrightarrow$S9(cp+co): $K = 2.83 > 0$ but Supp_nc(S8) = $\emptyset$.
This is the CP permutation channel — an independent transport mechanism.
The CP block's QT algebra is exactly commutative ($\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_{\mathrm{cp}} = 0$), so Supp_nc does not detect this channel.
However, individual generators $\rho(g)$ on CP are non-trivial permutation matrices (the CP block carries the symmetric group action of corner permutations), and these generators do not commute with the spectral projectors of S8 and S9 on CP.
This reveals a structural fact that Supp_nc correctly exposes: **averaging commutativity does not imply generator commutativity with spectral projectors.**
The CP channel is generator-mediated but not QT-noncommutative — a second, qualitatively distinct transport mechanism.

**Remark (Numerical verification).** Computing $K_{\alpha\beta}$ for all $9 \times 8 / 2 = 36$ unordered pairs at post-$\rho$-fix resolution:

- 10 pairs with $K > 0.01$: 9 are Type I (Supp_nc intersection), 1 is Type II (S8–S9 CP channel)
- 5 T7 morphisms (cross-block, $K = 0$, reachable via length-2 composition): all have disjoint Supp_nc AND no Type II CP adjacency
- 21 remaining pairs: all have $K < 10^{-14}$ and neither Type I nor Type II criterion met

**Remark (Caveat — K symmetric).** The Type I criterion (Supp_nc intersection $\Leftrightarrow$ $K > 0$) is an empirical regularity verified on the Rubik's cube (228-dim, 9 sectors). A first-principles derivation of Supp_nc intersection as a necessary and sufficient condition for noncommutative transport — starting from the group algebra $\mathbb{C}[G]$ and the projector geometry — has not been established in this paper. The criterion should be understood as a robust structural observation supported by exhaustive numerical evidence, not as a theorem. Establishing its algebraic necessity is an open direction (future work).

**S₃ negative control.** The S₃ systems (nat⊕reg, reg⊕reg) provide structural negative control: Z = C(ρ) forces purely diagonal K despite nontrivial noncommutative support, confirming hybrid sectors alone are insufficient for nontrivial transport topology. Full data: CCS Appendix \ref{sec:ccs-kappa0-barrier} and (CCS-I §2.11, Appendix G).

### Corollaries

**Corollary A.1** (All Direct Edges are Block-Preserving). Every edge in the transport graph shares $\geq 1$ block. There are **zero cross-block direct edges**. Cross-block transport requires length-2 composition.

**Corollary A.2** (Supp_nc Size Predicts Hub Degree). The hub degree of a sector is bounded by the number of other sectors whose Supp_nc intersects with it. S6 (Supp_nc = {ep, eo}) achieves degree 5 because {ep, eo} is the most common Supp_nc combination among other sectors (S2, S3, S5, and S4/S7 via shared ep).

**Corollary A.3** (T7 = Disjoint Supp_nc). The 5 T7 morphisms form a distinguished subset of the cross-block pairs with disjoint Supp_nc — they are exactly those admitting a compositional length-2 path through a hybrid sector:

| T7 Morphism | Supp_nc($\alpha$) | Supp_nc($\beta$) | Intersection |
|---------|-------------------|-------------------|-------------|
| S2(eo) $\leftrightarrow$ S4(ep+co) | {eo} | {ep, co} | $\varnothing$ |
| S3(ep+eo) $\leftrightarrow$ S9(cp+co) | {ep, eo} | {co} | $\varnothing$ |
| S4(ep+co) $\leftrightarrow$ S5(eo) | {ep, co} | {eo} | $\varnothing$ |
| S4(ep+co) $\leftrightarrow$ S8(cp) | {ep, co} | $\varnothing$ | $\varnothing$ |
| S6(ep+eo) $\leftrightarrow$ S9(cp+co) | {ep, eo} | {co} | $\varnothing$ |

All 5 are cross-block (disjoint block support). All mediated through the S6–S7–S9 hub complex (canonical mediation statistics: S6:2, S7:2, S9:1). Zero within-block T7 morphisms — Lie curvature (\cite{paper3}) is block-preserving.

### Why Supp_nc Works: The Transport–Commutator Identity

The algebraic reason Supp_nc controls Type I transport is the commutator identity (derived in the original analysis):

$$[P_\alpha, \rho(g)] = \sum_{\beta \neq \alpha} \big(T_{\alpha\beta}(g) - T_{\beta\alpha}(g)^\dagger\big).$$

The commutator $[P_\alpha, \rho(g)]$ is non-zero precisely when there exists $\beta \neq \alpha$ with $T_{\alpha\beta}(g) \neq 0$. The norm of this commutator, restricted to block $b$, is:

$$\|[P_\alpha|_b, \rho(g)|_b]\|_F^2 = 2 \sum_{\beta \neq \alpha} \|T_{\alpha\beta}(g)|_b\|_F^2.$$

A block $b$ can contribute to cross-sector transport if and only if the projector $P_\alpha$ fails to commute with $\rho(g)$ on that block. This failure of commutation is exactly what $\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_b > 0$ detects at the aggregate level — the per-axis QT operators are averaged versions of the generators, and their commutator measures the aggregate obstruction to simultaneous diagonalization on block $b$.

The CP channel is the canonical case: $[\mathrm{QT}^0, \mathrm{QT}^1]|_{\mathrm{cp}} = 0$ yet individual generators mix spectral projectors, producing $K_{8,9} = 2.83$. This is **generator-mediated but not QT-noncommutative** transport — a second mechanism that Supp_nc correctly distinguishes from the dominant EP-mediated channels.

***

## Part III — M₂ Principle {-}

## The EP Algebra as the Noncommutative Origin

### A_EP Structure

The edge-permutation block is the dominant noncommutative carrier (93.9%). Its per-axis QT operators generate a 20-dimensional semisimple algebra:

$$A_{\text{EP}} = \langle Q_0, Q_1, Q_2 \rangle \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4.$$

Key facts (all verified to machine precision):

- $\dim A_{\text{EP}} = 20$, closes at degree 3
- Center $Z(A_{\text{EP}}) = 8$-dim
- 4 simple $M_2$ components + 4 simple $M_1$ components = 8 isotypic blocks on EP
- 3 of 4 $M_2$ components are active ($[Q_i, Q_j] \neq 0$); one $M_2$ is "trivialized" (all $Q_i$ simultaneously scalarize on it)
- Killing form: signature $(8^+, 4^-, 8\text{ zero})$, $\ker(K) = Z(A_{\text{EP}})$
- Uniform multiplicity 12 across all 8 components: $4 \times 24 + 4 \times 12 = 144 = \dim \text{EP}$

Figure~\ref{fig:fig4-m2-chain} illustrates the algebraic cascade from $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ to the 10 direct transport edges.

![The algebraic source-to-transport cascade: $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ is a 20-dimensional semisimple algebra whose active M$_2$ components (3 of 4) rotate between sector subspaces under generator action. The resulting 10 direct edges — 9 Type I via M$_2$ mixing and 1 Type II CP channel — are the shadow of this atomic noncommutative structure. Transport topology originates in the M$_2$ components of a single block, not in global spectral coincidences.](../../figures/paper2/fig4_m2_chain.png)

### Double Commutant and Commutant Restriction Map

**Double commutant (EP block).**

$$\operatorname{Comm}(A_{\text{EP}}) \cong M_{12}(\mathbb{C})^8, \quad \dim \operatorname{Comm}(A_{\text{EP}}) = 8 \times 144 = 1152.$$

$$\operatorname{End}_{\operatorname{Comm}(A_{\text{EP}})}(\text{EP}) = A_{\text{EP}} \quad \checkmark \text{ (double commutant theorem verified)}.$$

**Commutant restriction map (full space).** Consider the restriction map from the full $G$-invariant commutant to the direct sum of per-layer commutants:

$$\pi: \operatorname{End}_G(V) \to \bigoplus_{\lambda} \operatorname{End}_G(V_\lambda), \quad \pi(C) = (P_\lambda C P_\lambda)_\lambda.$$

With $\dim \operatorname{End}_G(V) = 610$ (exact 228-dim commutant, computed via index-pair orbit decomposition) and $\dim \bigoplus_\lambda \operatorname{End}_G(V_\lambda) = 400 + 1 + 145 + 145 + 210 + 65 = 966$ (sum of per-layer commutant dimensions):

$$\ker \pi = 0 \quad \text{(injective)}, \qquad \operatorname{coker} \pi = 356.$$

The injectivity establishes that every $G$-invariant operator $C$ is **uniquely determined by its per-layer diagonal blocks** — there is no purely off-diagonal commutant; the full commutant is faithfully represented on the spectral layers.

The 356-dimensional cokernel measures the **overcompleteness of per-layer commutant data**: a tuple of per-layer commutant matrices $(C_\lambda \in \operatorname{End}_G(V_\lambda))$ lifts to a full commutant $C \in \operatorname{End}_G(V)$ if and only if it satisfies 356 independent linear constraints. Notably, every individual layer has zero local cokernel (each per-layer commutant basis element is individually liftable); the 356 constraints are global (cross-layer) — they arise from the transport sparsity pattern. Each zero-transport pair ($K_{\alpha\beta} = 0$) forces $C_{\alpha\beta} = 0$ on any $C \in \operatorname{End}_G(V)$, locking the relative scaling between the per-layer commutant bases.

See (CCS-I §2.9) and `experiments/paper2/commutant_pi_map.py`.

### M₂ Components as Transport Atoms

Each active $M_2$ component is a **transport atom** — a minimal noncommutative unit that creates cross-sector coupling. On an $M_2$ component, the three QT operators act as non-commuting $2 \times 2$ matrices. The spectral projectors $P_\alpha$ restricted to an $M_2$ component are rank-1 projectors in different directions — they do not commute with individual $\rho(g)$ because the generator action rotates between these directions.

This rotation is the **microscopic mechanism of transport**. A generator $\rho(g)$ applied to a vector in sector $\alpha$'s subspace of the $M_2$ component rotates it partially into sector $\beta$'s subspace — producing a non-zero $T_{\alpha\beta}(g)$.

The three active $M_2$ components create three distinct transport channels:

1. **S3$\leftrightarrow$S6** (via $M_2$ #1 on EP): $K = 2.55$
2. **S4$\leftrightarrow$S6** (via $M_2$ #2 on EP): $K = 3.46$
3. **S6$\leftrightarrow$S7** (via $M_2$ #3 on EP): $K = 3.61$

S6 is the unique sector with non-zero projection onto all three active $M_2$ components — this is why it has degree 5.

**Remark (Origin of M₂ components).** The $M_2(\mathbb{C})$ components arise from multiplicity-two isotypic sectors inside the edge-permutation subsystem. The underlying source of this multiplicity is the additional $\mathbb{Z}_2$ orientation-parity structure present in the edge system: each edge carries a binary orientation label ($\pm 1$), enriching the permutation representation with an additional $\mathbb{Z}_2$ orientation structure and producing multiplicity-two isotypic sectors. These multiplicity-two isotypic components induce the corresponding $M_2(\mathbb{C})$ commutant blocks inside $A_{\mathrm{EP}}$ — the noncommutative units that drive all Type I transport.

### Hub Necessity

**Proposition (M₂ Overlap ⇒ Hub Necessity).** Let the EP block algebra contain $k \geq 2$ active noncommutative simple components. If the sector projectors $\{P_\alpha\}$ resolve these components into different rank-1 subspaces, then there exists a unique sector (the *hub*) whose projector has non-zero overlap with every active noncommutative component. All other sectors have non-zero overlap with at most one such component.

*Proof outline.* On each $M_2$ component, the $P_\alpha|_{\text{EP}}$ are rank-1 orthogonal projectors (the $M_2$ component is 2-dimensional, and the Center diagonalization separates its two eigenvectors). Since there are 9 sectors and 3 active $M_2$ components — each resolved $M_2$ component contributes two orthogonal rank-1 eigendirections under center diagonalization, hence 2 sectors per component — at most 6 sectors can be "pure" (supported on a single $M_2$ component). The remaining sectors must mix across components. The unique mixing pattern that maximizes Supp_nc intersection is a sector that projects onto the "off-diagonal" subspace of all three $M_2$ components — this is S6.

S6 is the primary hub because it is the unique sector whose Supp_nc = {ep, eo} has non-empty intersection with Supp_nc of S2 ({eo}), S3 ({ep, eo}), S4 ({ep, co}), S5 ({eo}), and S7 ({ep, co, eo}). Its EP support spans all three active $M_2$ components.

### Transport Nonlocality from M₂

The M₂ Principle explains why cross-block transport requires composition. The M₂ components live entirely within the EP block. A sector with only CO support (e.g., S9's co component) has no access to the EP-based M₂ transport machinery. It can only transport to EP-containing sectors via the weak CO noncommutative sideband ($\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_{\mathrm{co}} = 0.61$), which couples it to sectors sharing CO support (S4, S7).

Cross-block transport (e.g., S3(ep+eo) $\to$ S9(cp+co)) is impossible at the single-generator level because there is no block where BOTH sectors have non-zero projection AND the block is noncommutative. The composition path S3 $\to$ S7 $\to$ S9 works because S7 has both EP and CO support — it translates EP-based transport into CO-based transport, bridging a multiplicity-mediated transport gap.

***

## Part IV — Refinement Geometry {-}

## The Obstruction Lattice

### Refinement POSET (from \cite{paper1})

\cite{paper1} established that the family of spectral decompositions $\{D(A_S)\}$ across inverse-closed generator sets $S$ forms a refinement POSET $\mathcal{L}$ under $D_1 \leq D_2 \iff A_{D_2} \in \langle A_{D_1} \rangle$. The commutative core $\mathcal{C} = \{\operatorname{Center}, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}, 18\text{-gen}\}$ is a $\wedge$-semilattice. The 9 primitive sectors are the atoms of $\mathcal{C}$ — the finest decomposition achievable within the commutative core.

### Refinement Stops at the Noncommutative Obstruction

**Proposition (M₂ Overlap Obstruction Caps Refinement).** The refinement chain terminates at 9 primitive sectors — not as a numerical artifact, but as an algebraic consequence of the representation structure. Further refinement is blocked by the M₂ overlap obstruction: the noncommuting QT operators on EP cannot be simultaneously diagonalized, and any operator that would split an M₂-coupled sector must fail to commute with the Center.

**Explanation.** The Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ is exactly commutative ($\|[\cdot, \cdot]\| < 10^{-15}$). Any operator that would split, say, S6 into finer sectors must live in $A_{\text{EP}}$ — the only algebra with non-trivial action on EP. But the only operators in $A_{\text{EP}}$ that commute with both QT_all and HT_all are in the center $Z(A_{\text{EP}})$, which is already diagonalized by the 9-sector decomposition (its 8 eigenvalues are resolved into the 8 non-S1 sectors). Adding a non-central element of $A_{\text{EP}}$ would break commutativity — the new operator would not commute with QT_all or HT_all, so the "joint diagonalization" would not be a true simultaneous diagonalization and the decomposition would not consist of orthogonal projectors.

The 9 sectors are therefore the **finest commutative decomposition** — the unique maximal refinement achievable while maintaining pairwise commuting diagonalizing operators and orthogonal projectors. The obstruction is the M₂ components: their noncommutativity ($[Q_i, Q_j] \neq 0$ on 3 of 4 components) is the primary algebraic obstruction that blocks further refinement. Figure~\ref{fig:fig3-refinement-obstruction} shows the refinement obstruction: the commutative center chain saturates at exactly 9 primitive sectors.

![Refinement obstruction: the commutative center chain ($A_{18} \to A_{18} + \mathrm{QT}_{\mathrm{all}} \to A_{18} + \mathrm{QT}_{\mathrm{all}} + \mathrm{HT}_{\mathrm{all}}$) resolves to a maximum of 9 primitive sectors. The M$_2$ components in $A_{\mathrm{EP}}$ prevent further commutative splitting; any further refinement would require operators outside the commutative center. The 9-sector decomposition is a ceiling imposed by algebraic noncommutativity, not an arbitrary choice.](../../figures/paper2/fig3_refinement_obstruction.png)

### The Obstruction POSET

The M₂ components of $A_{\text{EP}}$ are the **atoms of obstruction** — the minimal noncommutative units that prevent further refinement. Each active M₂ component is a 2-dimensional subspace where QT⁰ and QT¹ fail to commute. Attempting to split this 2-dimensional subspace into 1-dimensional QT⁰-eigenspaces and 1-dimensional QT¹-eigenspaces simultaneously is impossible — QT⁰ and QT¹ have different eigenvectors on this subspace.

The obstruction lattice $\mathcal{O}$ is the POSET of M₂ subalgebras under inclusion. For the Rubik's cube:

$$\mathcal{O} = \{M_2^{(1)}, M_2^{(2)}, M_2^{(3)}, \text{trivial } M_2\}$$

where the first three are active (create transport) and the fourth is trivialized. The noncommutativity at each node is:

$$\|[Q_i, Q_j]\|_{M_2^{(k)}} = \begin{cases} > 0 & k = 1,2,3 \\ = 0 & k = \text{trivial} \end{cases}$$

### Commutative vs. Noncommutative Refinement

The refinement story has two regimes:

| Regime | Algebra | Finest decomposition | Blocked by |
|--------|---------|---------------------|------------|
| Commutative | Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ | 9 primitive sectors | — (complete within commutative core) |
| Noncommutative | $A_{\text{EP}}$ full algebra | Would split each M₂ into 2 sectors (11+ total) | M₂ obstruction — $[Q_i, Q_j] \neq 0$ on active M₂ |

The 9-sector decomposition is the finest **commutative** decomposition. Further refinement is possible only if we accept non-orthogonal, non-commuting "sectors" — which would not be sectors in the spectral sense (no longer eigenspaces of a commuting family).

The obstruction lattice is characterized for the Rubik cube; a general theory of refinement obstruction for semisimple block algebras is open (future work).

## Part V — Generator-Family Universality {-}

## The G-Determined / S-Conditioned Boundary

Parts I–IV analyzed the canonical 18-generator family. A natural question — one any reader will ask — is: *which of these results are specific to the 18 face turns, and which are structural features of the representation itself?*

To answer this, we systematically vary the generator set $S$ while holding the representation $\rho: G \to \mathrm{GL}(228, \mathbb{C})$ fixed. Six families are studied: the full 18 face turns, subsets at $n = 16, 12, 10, 8, 6$ generators, and the 12-generator face-symmetric set. The results reveal a sharp boundary between three invariance levels.

### The Invariance Hierarchy

| Level | Determined by | Examples | Mechanism |
|-------|--------------|----------|-----------|
| **G-determined** | The representation $\rho(G)$ | $\dim \operatorname{Comm}(\rho) = 610$, block decomposition $V = \mathrm{cp} \oplus \mathrm{ep} \oplus \mathrm{co} \oplus \mathrm{eo}$, $\dim \mathrm{EP} = 144$, $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$, cross-block $K = 0$ | These are properties of $\rho$ as a $G$-module — independent of which $S \subset G$ generates the averaging operator |
| **Center-determined** | The commutative subalgebra $\langle A_S, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}} \rangle$ | Primitive sector count, hub identity, star topology presence, Supp_nc profiles | Stable across large generator families that preserve the per-axis QT/HT structure |
| **S-conditioned** | The specific generator subset $S$ | Layer count, rationality of eigenvalues, layer dimensions, noncommutativity magnitude | Vary with generator coverage — the detailed spectral architecture depends on which symmetries are present |

### G-Determined Invariants

Three structural features are verified to be invariant across all six generator families ($n = 18, 16, 12, 10, 8, 6$) and additional continuum points:

1. **Cross-block transport prohibition.** $K_{\alpha\beta} = 0$ whenever $\alpha$ and $\beta$ have disjoint block support. This follows from $\rho(g)$ being block-diagonal for all $g \in G$ — a property of the representation, not of $S$. The block-diagonal structure of $\rho$ is a $G$-categorical invariant.

2. **Commutant is G-determined.** $\dim \operatorname{Comm}(\rho(\langle S \rangle))$ depends only on the subgroup $\langle S \rangle$ generated by $S$, not on the specific choice of generators within that subgroup. Families generating the full Rubik group all yield $\dim \operatorname{Comm} = 610$; the half-turn-only family ($n = 6$) generates a proper subgroup with $\dim \operatorname{Comm} = 3918$. The commutant is invariant within each $\langle S \rangle$-equivalence class — the value is a function of the generated group, not the generating set.

3. **EP algebra structure.** $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ and $\dim \mathrm{EP} = 144$ are representation-theoretic identities — they hold for any $S \subset G$ because the EP block itself is a $G$-submodule.

### Center-Determined Invariants

Hub identity and Supp_nc profiles are stable across generator families that preserve the per-axis quarter-turn / half-turn partition. The S6 hub (degree 5 in the 18-full case) persists as the maximal-degree node at $n = 12$ (quarter-turns only) and $n = 8$ (symmetry-broken) — the hub is a structural feature of how spectral projectors intersect the AW decomposition, not a fragile numerical coincidence.

### S-Conditioned Features

The features that vary across generator families — layer count, eigenvalue rationality, layer dimensions — are precisely those that depend on the detailed algebraic closure of the generator set. The next section analyzes the most striking S-conditioned phenomenon: the rational-to-irrational phase transition.

***

## Symmetry Breaking and the Rational-to-Irrational Phase Transition

\cite{paper1} established that incomplete face coverage drives a spectral field extension from $\mathbb{Q}$ to $\mathbb{Q}(\sqrt{5})$: the per-face cyclotomic cancellation ($\omega + \omega^2 + 1 = 0$) fails when a face pair is missing, and the spectral field jumps sharply. The full mechanism and theorem statement are in \cite{paper1}; we summarize the transport-relevant facts and develop three deeper analyses not in \cite{paper1} (§8.2 phase boundary, §8.4 $\sqrt{5}$ origin via $S_5$, §8.5 CP protection theorem).

### The Generator Coverage Continuum

Six families span the coverage continuum (\cite{paper1} for full census; CCS-III §7.5):

| Family | Generators | Layers | Rational? | Spectral field |
|--------|-----------|--------|-----------|----------------|
| $n=18$ (canonical) | Full face turns | 6 | Yes | $\mathbb{Q}$ |
| $n=16$ | Remove F2, B2 | 9 | **No** | $\mathbb{Q}(\sqrt{5})$ |
| $n=12$ | Quarter-turns only | 8 | Yes | $\mathbb{Q}$ |
| $n=10$ | QT, no F/B axis | 5 | Yes | $\mathbb{Q}$ |
| $n=8$ | QT, axes 0+2 only | 7 | **No** | $\mathbb{Q}(\sqrt{5})$ |
| $n=6$ | Half-turns only | 3 | Yes | $\mathbb{Q}$ |

The irrational field $\mathbb{Q}(\sqrt{5})$ appears at $n = 16$ and $n = 8$; the common condition is incomplete face coverage.

### Phase Boundary Conditions

The transition occurs when two conditions are simultaneously satisfied — a sharper criterion than the single-condition statement in \cite{paper1}:

1. **Incomplete face coverage.** Not all six faces are represented.
2. **Noncommutative generators present.** The set includes quarter-turns.

When either fails, the spectrum stays rational. The $n = 8$ family is the cleanest demonstration: axes 0 and 2 quarter-turns, axis 1 (U/D) entirely absent, producing two Galois-conjugate irrational eigenvalues $\lambda_\pm = (3 \pm \sqrt{5})/4$.

### Block-Selective Irrationality

The field extension is **block-selective**. Decomposing the $n = 8$ averaging operator by block (CCS-III §7.5):

| Block | Spectrum | Field | Mechanism |
|-------|----------|-------|-----------|
| CP (64D) | 5 eigenvalues, all $\in \mathbb{Q}$ | $\mathbb{Q}$ | Bose-Mesner $H(3,2)$ — integer Krawtchouk eigenvalues |
| EP (144D) | 6 eigenvalues, contains $\lambda_\pm$ | $\mathbb{Q}(\sqrt{5})$ | Incomplete face-incidence algebra |
| CO (8D) | 3 eigenvalues, all $\in \mathbb{Q}$ | $\mathbb{Q}$ | $\mathbb{Z}_3$ phase — cyclotomic cancellation holds |
| EO (12D) | 6 eigenvalues, contains $\lambda_\pm$ | $\mathbb{Q}(\sqrt{5})$ | Mirrors EP — shares edge-indexed structure |

**Selection rule.** Only noncommutative blocks (EP, EO) develop irrational eigenvalues. Commutative blocks (CP, CO) retain rational spectra regardless of generator coverage. For this paper, the significance is that the irrationality carriers (EP, EO) are precisely the blocks that carry Supp_nc-driven Type I transport — the same noncommutative structure mediates both transport (§4) and spectral instability. The mechanisms are analyzed in §8.4 ($\sqrt{5}$ origin) and §8.5 (CP rationality protection).

### Origin of $\sqrt{5}$

The appearance of $\sqrt{5}$ specifically traces to the representation theory of $S_5$: the golden ratio $\varphi = (1 + \sqrt{5})/2$ appears as a character value. When a face axis is missing ($n = 8$), the reduced symmetry group is isomorphic to $S_5$, and the adjacency matrix of the reduced face-incidence graph acquires $\varphi$ in its spectrum. Full derivation in (CCS-III §7.5).

### The CP Block: Rationality Protection

The CP block's immunity to the field extension is a structural theorem. The CP block carries the $Q_3$ Hamming scheme $H(3,2)$, a classical distance-regular graph whose Bose-Mesner algebra has integer Krawtchouk eigenvalues. For *any* generator subset that respects the Hamming graph structure (i.e., that acts as a subgraph of the 3-cube), the adjacency algebra remains a subalgebra of the Hamming scheme's Bose-Mesner algebra — and all eigenvalues stay in $\mathbb{Q}$.

The reason is fundamental: the Hamming scheme's eigenmatrix has integer entries. Any subalgebra of a commutative algebra with an integer eigenmatrix inherits the integrality property. CP rationality is therefore a **theorem**, not an observation: it follows from the classification of the CP block as a $Q_3$ Hamming scheme.

### Why the 18 Face-Turn Generators Are Special

The symmetry-breaking analysis provides the answer to a question the trilogy's architecture demands: *why 18 generators?*

The 18 face-turn generators are the unique set (up to the $S_6 \times \mathbb{Z}_2$ face-relabeling symmetry, among inverse-closed face-turn families) that simultaneously satisfies:

1. **Complete face coverage.** All six faces participate, with all three turn types $\{+1, -1, 2\}$ represented on every face.
2. **Algebraic closure.** The per-face phase sum $\omega + \omega^2 + 1 = 0$ forces $\mathbb{Z}_3$ cyclotomic cancellation on the CO block.
3. **Bose-Mesner integrity.** The full Hamming scheme on CP and the complete face-incidence algebra on EP produce integer adjacency characters.

Any deviation from these conditions — removing a face, dropping half-turns, restricting to a subset of axes — either preserves rationality through a different mechanism (e.g., $n = 6$ half-turns are fully commutative) or breaks it (e.g., $n = 8$ incomplete coverage yields $\mathbb{Q}(\sqrt{5})$). The 18-generator set is the **maximal inverse-closed generator family with complete face coverage** — and it is the completeness, not the maximality, that guarantees the rational spectrum.

This result transforms \cite{paper1}'s central observation ("the spectrum is rational") from an empirical fact about one specific generator set into a **structural theorem about face-complete generator families**: rationality is observed to coincide with complete-face arithmetic closure across all verified families (the converse proof remains open).

### Transport Topology Under Symmetry Breaking

The transport graph deforms under generator removal, but key structural features persist:

| Family | Sectors | Direct edges | Hub (deg) | Cross-block $K$ |
|--------|---------|-------------|-----------|-----------------|
| $n = 18$ (canonical) | 9 | 10 | S6 (5) | 0 |
| $n = 8$ (symmetry-broken) | 7 | 28 | S6 (5) | 0 |
| $n = 6$ (half-turns) | 3 | 3 | S2 (2) | 0 |

Three structural invariances are observed:

1. **Hub persistence.** S6 remains the primary hub (degree 5) even at $n = 8$, despite the spectral field extension and layer count change. The hub structure is empirically consistent with a Supp_nc-driven mechanism — it tracks the intersection of noncommutative supports, which is stable under generator variation across all verified families.

2. **Cross-block prohibition.** $K_{\alpha\beta} = 0$ for disjoint-block pairs at every $n$. This is G-determined — it follows from $\rho(g)$ being block-diagonal, independent of $S$.

3. **Star topology.** When a hub exists, the transport graph organizes as a star centered on that hub. The star topology is a robust organizational principle, not a fragile coincidence of the 18-generator family.

The deformation is in the *density* of edges: $n = 8$ has 28 edges (hyper-connected, due to irrational eigenvalue splitting creating more sectors and denser Supp_nc overlaps), while $n = 6$ has only 3 (the commutative limit, where transport reduces to diagonal coupling). The architecture deforms but does not collapse — the underlying Supp_nc logic governs all cases.

***

## Discussion

The structural notions developed here — noncommutative support $\operatorname{Supp}_{\mathrm{nc}}$, the transport norm $K_{\alpha\beta}$, the M₂ mechanism, and the Type I/II classification — are general diagnostic tools for finite representation transport geometry. The specific transport topology reported in this paper (10 direct edges, S6 primary hub, Type I/II split) is the Rubik realization at 9-sector resolution. The transport topology described here should therefore be understood as a verified realization of the general transport framework, rather than a universal finite-group classification.

The transport topology on 9 primitive sectors is driven by the M₂ principle: noncommutative simple components of the block algebras determine the Type I transport graph (9 of 10 direct edges via Supp_nc intersection). The single Type II exception (S8↔S9) reveals that averaging commutativity does not imply generator commutativity. The 18 face-turn generators are distinguished by complete-face arithmetic closure — the only generator family observed in the Rubik representation for which all four blocks participate in a cyclotomic phase cancellation that forces eigenvalue rationality.

This paper establishes that noncommutative curvature exists within projector geometry: the M₂-driven transport topology, the 9-sector refinement boundary, and the G-determined/Center-determined/S-conditioned invariance hierarchy. All open problems are recorded in (CCS Appendix I).

The one structural question left open is whether alternative transport mechanisms beyond the M₂ principle exist.

***

## Appendix A: Noncommutative Support Construction

The noncommutative support $\operatorname{Supp}_{\mathrm{nc}}(\alpha)$ (Definition~\ref{def:noncommutative-support}) is the dominant structural invariant for Type I transport. This appendix details its construction, the structural choices it depends on, and the algebraic reason for its effectiveness. Figure~\ref{fig:figa1-pipeline} provides the full structural pipeline from generators to transport and commutant analysis.

![The structural pipeline from generators $\rho(g)$ to the averaging operator $A$ to spectral layers $\{E_\lambda\}$, forking into transport (left: $K_{\alpha\beta}$, Type I/II classification, T7 detection) and commutant (right: $\operatorname{Comm}(\rho) = 610$, $\operatorname{Comm}(A) = 804$, $\Delta_{\mathrm{comm}} = 194$). The two branches are structurally independent in general but linked only through the EP block's M$_2$ structure in this system. This cascade contextualizes the full structural relationship between spectral decomposition, transport topology, and commutant structure.](../../figures/paper2/figa1_pipeline.png)

### A.1 Per-Axis QT Operators

The 18 face-turn generators partition naturally into three axis-aligned subsets:

$$\text{axis-}a = \{\text{quarter-turns on the two faces perpendicular to axis } a\}, \quad a \in \{0, 1, 2\}.$$

For axis 0 (R/L faces): 4 generators (R, R′, L, L′). For axis 1 (U/D faces): 4 generators (U, U′, D, D′). For axis 2 (F/B faces): 4 generators (F, F′, B, B′). The remaining 6 generators are the half-turns (R2, L2, U2, D2, F2, B2), used in $\mathrm{HT}_{\mathrm{all}}$ but not in the per-axis QT operators.

The per-axis quarter-turn averaging operator is:

$$\mathrm{QT}^a = \frac{1}{4} \sum_{g \in \text{axis-}a} \rho(g), \quad a \in \{0, 1, 2\}.$$

These three operators are the QT-resolved components of the total quarter-turn average: $\mathrm{QT}_{\mathrm{all}} = \frac{1}{3}(\mathrm{QT}^0 + \mathrm{QT}^1 + \mathrm{QT}^2) = \frac{1}{12} \sum_{\text{all QT}} \rho(g)$.

### A.2 Block Commutator Norms

The commutator $[\mathrm{QT}^0, \mathrm{QT}^1]$ is computed in the full 228-dimensional representation space, then restricted to each block $b \in \{\mathrm{cp}, \mathrm{ep}, \mathrm{co}, \mathrm{eo}\}$ using the block projectors $\Pi_b$:

$$\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_b = \|\Pi_b [\mathrm{QT}^0, \mathrm{QT}^1] \Pi_b\|_F.$$

The numerical values (CCS-I §2.1) reveal a sharp hierarchy: cp = 0 (exactly commutative), ep = 2.74 (93.9% of total), co = 0.61, eo = 0.79. The CP block's exact commutativity follows from the Bose-Mesner algebra of the Q₃ Hamming scheme: the per-axis QT operators on CP belong to the Hamming scheme's association scheme algebra, which is commutative by construction. The EP block's dominant noncommutativity reflects the $M_2$ structure of $A_{\text{EP}}$ (see the EP Algebra section).

### A.3 Dependence on Generator Partition

The definition of $\operatorname{Supp}_{\mathrm{nc}}$ depends on two structural choices that are geometrically natural for the Rubik's cube but not canonical for arbitrary finite groups:

1. **Axis partition.** The generators must be partitioned into subsets whose averaging operators $\mathrm{QT}^a$ form a noncommutative family. For the cube, the three coordinate axes provide a natural 3-partition. For a general finite group with generating set $S$, an analogous construction would require a partition $S = \bigcup_i S_i$ such that the per-subset averages $A_i = \frac{1}{|S_i|}\sum_{g \in S_i} \rho(g)$ carry a non-trivial commutator structure.

2. **Block decomposition.** The restriction to blocks $\{\mathrm{cp}, \mathrm{ep}, \mathrm{co}, \mathrm{eo}\}$ relies on the $G$-orbit decomposition of the representation space (cubie-type orbits). For a general representation, the natural blocks would be the isotypic components of the $G$-action — the commutator $[A_i, A_j]$ would then be evaluated on each isotypic component rather than on cubie-type blocks.

The Supp_nc framework is therefore **not claimed to be canonical for arbitrary groups.** It is a structural invariant that captures the M₂-driven transport mechanism in the Rubik's cube family — a concrete computational tool whose generalization to other systems is an open direction (future work). Nevertheless, the framework provides a template for analyzing similar systems with a natural axis partition and block decomposition: the core logic — partition generators by algebraic substructure, compute per-partition commutators on each block, take the union of nonzero-commutator blocks as the noncommutative support — is transferable to any finite group representation whose generators admit a geometrically meaningful partition.

### A.4 Why Supp_nc Detects Type I Transport

On a block $b$ where $[\mathrm{QT}^0, \mathrm{QT}^1]|_b = 0$, the per-axis QT operators can be simultaneously diagonalized on that block. The spectral projectors $P_\alpha|_b$ are then matrices in the common eigenbasis, and they commute with each other on $b$. Individual generators $\rho(g)|_b$ may still fail to commute with these projectors (as the CP channel demonstrates — Appendix C), but the aggregate commutator norm vanishes because the obstruction cancels under axis averaging.

On a block $b$ where $[\mathrm{QT}^0, \mathrm{QT}^1]|_b > 0$, simultaneous diagonalization is impossible. The spectral projectors restricted to $b$ live in different eigenbases for different QT axes, creating a geometric obstruction to commutativity. When two sectors $\alpha, \beta$ both have non-zero projection on such a block, their projectors $P_\alpha|_b$ and $P_\beta|_b$ cannot both commute with all $\mathrm{QT}^a$ — the noncommutativity leaks into cross-sector coupling, producing $T_{\alpha\beta}(g) \neq 0$ for at least one generator $g$.

This is the algebraic content of Observation A: Supp_nc intersection is the condition that two sectors' projectors live in overlapping noncommutative regions of the representation space, and the overlap forces generator-mediated mixing between them.

***

## Appendix B: The CP Permutation Channel (Type II)

The S8$\leftrightarrow$S9 transport edge ($K = 2.83$) is the sole Type II channel — the only direct edge not detected by Supp_nc intersection. This appendix provides a dedicated algebraic analysis, since any reviewer of the Type I/II classification will scrutinize this exception.

### B.1 The Puzzle

S8 (cp-only, 8-dim, $\lambda_A = 1/3$) and S9 (cp+co, 27-dim, $\lambda_A = 1/3$) share the CP block. Their noncommutative supports are $\emptyset$ and {co} respectively — the intersection is empty. Yet $K_{8,9} = 2.83$, comparable in magnitude to the Type I edges (range 0.47–4.06). Why?

### B.2 QT Commutativity on CP

The CP block carries the permutation action on the 8 corner cubies — a subrepresentation factored through the cube group's corner permutation coset. The per-axis QT operators on CP belong to the Bose-Mesner algebra of the Q₃ Hamming scheme $H(3,2)$, which is a commutative association scheme algebra. Consequently:

$$[\mathrm{QT}^0, \mathrm{QT}^1]|_{\mathrm{cp}} = 0 \quad \text{(exactly, to machine precision)}.$$

The CP block is QT-commutative. By the Supp_nc criterion, no Type I transport is possible on CP.

### B.3 Generator Noncommutativity on CP

Individual generators $\rho(g)|_{\mathrm{cp}}$ are permutation matrices — elements of the symmetric group action on corner positions. These permutation matrices do **not** commute with the spectral projectors $P_8|_{\mathrm{cp}}$ and $P_9|_{\mathrm{cp}}$:

$$[P_8, \rho(g)]|_{\mathrm{cp}} \neq 0, \quad [P_9, \rho(g)]|_{\mathrm{cp}} \neq 0 \quad \text{for most } g \in S.$$

The projectors $P_8$ and $P_9$ are eigenmatrices of the averaged operators $\mathrm{QT}_{\mathrm{all}}$ and $\mathrm{HT}_{\mathrm{all}}$ on CP. These eigenmatrices diagonalize the averaged operators but not the individual generators — a single face-turn $\rho(g)$ mixes the two eigenspaces because the CP permutation action does not respect the spectral decomposition induced by axis-averaged operators.

### B.4 The Mechanism

The CP transport channel operates by **permutation adjacency** rather than by noncommutative mixing. On the CP block:

- $\mathrm{QT}_{\mathrm{all}}$ has two distinct eigenvalues (0 and 1/3), corresponding to S8 ($\lambda_{\mathrm{QT}} = 0$) and the CP part of S9 ($\lambda_{\mathrm{QT}} = 1/3$)
- $\mathrm{HT}_{\mathrm{all}}$ also separates these subspaces ($\lambda_{\mathrm{HT}} = 1$ vs $1/3$)
- Individual $\rho(g)$ act as permutations on the 8 corner positions — they do not preserve the $\mathrm{QT}_{\mathrm{all}}/\mathrm{HT}_{\mathrm{all}}$ eigenspaces individually, but mix them

The mixing is **permutation-mediated**: applying a face turn to a corner configuration in S8 produces a configuration whose CP coordinates have non-zero overlap with S9's CP subspace. This is not a noncommutative effect (since QT operators on CP commute) — it is a **geometric** effect: the permutation action of individual generators is misaligned with the spectral basis of the averaged operators.

### B.5 Structural Significance

The CP channel establishes a structural fact of independent interest:

$$\boxed{\text{Averaging commutativity} \;\neq\; \text{generator commutativity with spectral projectors}}$$

QT commutativity on CP means the per-axis averaged dynamics is Abelian on that block. Generator noncommutativity with projectors means the unaveraged, single-step dynamics is not. The distinction is erased by axis averaging but preserved by individual generators.

The CP channel demonstrates that **Supp_nc is a structurally dominant but not complete transport invariant** — it captures Type I (9 of 10 edges) but must be supplemented by the permutation adjacency criterion for Type II (1 edge). A complete invariant for the Rubik's cube system would require both conditions: noncommutative support intersection for Type I, shared commutative block with generator-noncommutative spectral projectors for Type II.

### B.6 Computable Criterion

The Type II mechanism can be detected by a simple numerical test. A pair $(\alpha, \beta)$ is a Type II edge iff all three conditions hold:

**(i) Shared commutative block.** $\alpha$ and $\beta$ share only the CP block (and possibly CO), with $\operatorname{Supp}_{\mathrm{nc}}(\alpha) \cap \operatorname{Supp}_{\mathrm{nc}}(\beta) = \emptyset$.

**(ii) Generator noncommutativity with projectors.** $\frac{1}{|S|} \sum_{g \in S} \|[P_\alpha, \rho(g)] \|_F > 0$. For the S8–S9 pair, this average is approximately 0.87 (CP block only).

**(iii) Commutative averaging algebra on the shared block.** $\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_{\text{shared block}} = 0$ exactly — the shared block's QT algebra is commutative, so the transport is not Type I. For the CP block, this holds to machine precision.

These three conditions together distinguish the Type II channel from both Type I noncommutative edges (which fail (iii)) and inert block overlap (which fails (ii)). The criterion is computable directly from the representation data $\{\rho(g), P_\alpha\}$ without reference to the Supp_nc construction.

***

## Appendix C: T7 Edge Tables

The 5 T7 morphisms — $K = 0$, $\kappa_d = 0$ for all $d$ (structural, by Paper~III, Lemma~\ref{lem:lie-generated-support-invariance}), yet reachable via length-2 compositional accessibility through a hybrid sector. Full verification in (CCS-I §2.5).

| T7 Morphism | Block support | Supp_nc intersection | Mediation path | Hub |
|---------|--------------|---------------------|----------------|-----|
| S2(eo) $\leftrightarrow$ S4(ep+co) | eo $\cap$ (ep+co) = $\emptyset$ | {eo} $\cap$ {ep, co} = $\emptyset$ | S2 $\to$ S6 $\to$ S4 | S6 |
| S3(ep+eo) $\leftrightarrow$ S9(cp+co) | (ep+eo) $\cap$ (cp+co) = $\emptyset$ | {ep, eo} $\cap$ {co} = $\emptyset$ | S3 $\to$ S7 $\to$ S9 | S7 |
| S4(ep+co) $\leftrightarrow$ S5(eo) | (ep+co) $\cap$ eo = $\emptyset$ | {ep, co} $\cap$ {eo} = $\emptyset$ | S4 $\to$ S6 $\to$ S5 | S6 |
| S4(ep+co) $\leftrightarrow$ S8(cp) | (ep+co) $\cap$ cp = $\emptyset$ | {ep, co} $\cap$ $\emptyset$ = $\emptyset$ | S4 $\to$ S9 $\to$ S8 | S9 |
| S6(ep+eo) $\leftrightarrow$ S9(cp+co) | (ep+eo) $\cap$ (cp+co) = $\emptyset$ | {ep, eo} $\cap$ {co} = $\emptyset$ | S6 $\to$ S7 $\to$ S9 | S7 |

**Structural properties:**

- All 5 are **cross-block** (disjoint block support). Zero within-block T7 morphisms.
- All 5 are mediated through the S6–S7–S9 hub complex (canonical mediation statistics: S6:2, S7:2, S9:1).
- T7 detection is structural — $\text{BlockSupp}(\alpha) \cap \text{BlockSupp}(\beta) = \emptyset$ implies $\kappa_d = 0$ for all $d$ by Paper~III, Lemma~\ref{lem:lie-generated-support-invariance}.

\noindent\textbf{Corollary C.1 (T7 = Disjoint Supp\_nc).} The 5 T7 morphisms are a distinguished subset of the cross-block pairs with disjoint Supp_nc — exactly those admitting a compositional length-2 path through a hybrid sector. Cross-block pairs with disjoint Supp_nc satisfy neither the Type I (Supp_nc intersection) nor Type II (shared CP) transport criterion, forcing $K = 0$; the 5 T7 pairs are those among them that are reachable via compositional accessibility through a hybrid intermediate sector.

***

## Appendix D: Canonical Transport Summary

Compact summary of transport graph properties at 9-sector resolution. Full K matrix and exhaustive verification in (CCS-I §2.2).

### D.1 Sector Summary

Supp_nc values are tabulated in the Noncommutative Support of Each Sector and Supp_nc Definition sections.

| Sector | Dim | $k$ | $\lambda_A$ | Degree | Role |
|--------|-----|-----|-------------|--------|------|
| S1 | 20 | 0 | 1 | 0 | Isolated ($G$-invariant) |
| S2 | 2 | 1 | 8/9 | 2 | Leaf (S5, S6) |
| S3 | 39 | 2 | 7/9 | 2 | Leaf (S6, S7) |
| S4 | 26 | 3 | 2/3 | 2 | Leaf (S6, S9) |
| S5 | 1 | 4 | 5/9 | 2 | Leaf (S2, S6) |
| **S6** | **39** | **4** | **5/9** | **5** | **Primary hub** |
| S7 | 66 | 4 | 5/9 | 3 | Secondary hub |
| S8 | 8 | 6 | 1/3 | 1 | Leaf (S9, CP channel) |
| S9 | 27 | 6 | 1/3 | 3 | Leaf (S4, S7, S8) |

### D.2 Transport Graph Properties

| Property | Value | Type |
|----------|-------|------|
| Vertices | 9 | Structural |
| Direct edges ($K > 0.05$) | 10 | S-conditioned |
| Type I (Supp_nc) | 9 | Structural |
| Type II (CP permutation) | 1 (S8$\leftrightarrow$S9) | Structural |
| Cross-block direct edges | 0 | G-determined |
| T7 morphisms | 5 (all cross-block) | Center-determined |
| Primary hub | S6 (degree 5) | Center-determined |
| Secondary hub | S7 (degree 3) | Center-determined |
| Isolated | S1 (degree 0) | G-determined |

Block noncommutativity values are tabulated in the Noncommutativity Hierarchy section.

***

## Appendix E: Generator-Family Universality

Which transport properties survive generator-set variation? Compact comparison across the six families studied in Part V (Generator-Family Universality). Full atlas in (CCS-II §II.4).

### E.1 Invariance Hierarchy

| Property | n=18 | n=16 | n=12 | n=10 | n=8 | n=6 | Level |
|----------|------|------|------|------|-----|-----|-------|
| Cross-block $K = 0$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | G-determined |
| Commutant is G-determined | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | G-determined |
| $A_{\text{EP}} \cong M_2^4 \oplus M_1^4$ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | G-determined |
| S6 as primary hub | ✓ | ✓ | ✓ | — | ✓ | — | Center-determined |
| Star topology | ✓ | ✓ | ✓ | — | ✓ | — | Center-determined |
| Layer count | 6 | 9 | 8 | 5 | 7 | 3 | S-conditioned |
| Rational spectrum | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | S-conditioned |

### E.2 Transport Topology Deformation

The transport topology deformation across generator families is tabulated in §8.7. Cross-block $K = 0$ holds for every generator family — it is G-determined by the block-diagonal structure of $\rho(g)$. Hub persistence: S6 remains the primary hub whenever the QT/HT partition is preserved, confirming it as a Center-determined structural feature. T7 morphism counts vary with $n$: 5 at $n=18$ (canonical), 0 at $n=6$ (HT only); the $n=8$ case falls outside the T7 detection framework (sector count and spectral field differ from canonical).

***

## Appendix F: Numerical Methods and S₃ Verification

### F.1 Computational Methods

All computations use `CubieSpectralOperator` (`rime/cubieoperator.py`). The 9 primitive sector projectors are obtained via joint diagonalization of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$. The K matrix and Supp_nc are computed directly from these projectors and the 18 generator matrices. Key parameters: tolerance $10^{-10}$ for transport and SVD; 18 face-turn generators; 228-dimensional representation.

A previously observed empirical correlation between commutant dimension differences and aggregate transport energy did not remain stable under the post-$\rho$-fix canonical representation revision, and is therefore omitted from the invariant hierarchy.

### F.2 S₃ Negative Control — Center Completeness

The S₃ negative controls (CCS-I §2.11, Appendix G) provide structural negative control for the transport framework. Under the canonical Center{A_full, A_trans} decomposition:

**S₃ nat⊕reg (9-dim).** 3 sectors (2 hybrid, 1 pure-reg). K is purely diagonal — all cross-sector K_ij = 0 for i ≠ j. Despite having hybrid sectors (S1, S3 span both nat and reg blocks) and nontrivial noncommutative support (the standard 2-dimensional irrep appears with multiplicity ≥ 2), off-diagonal transport is structurally absent. The reason is C0 (§4): Z = ⟨A_full, A_trans⟩ yields sectors coinciding with isotypic components — all sector projectors are G-invariant (max‖[P_i, ρ(g)]‖ ≈ 10⁻¹⁵). Without center incompleteness, K is forced diagonal.

**S₃ reg⊕reg (12-dim).** 3 sectors, all hybrid. Same mechanism: Z sectors = isotypic components → K diagonal → 0 off-diagonal transport edges.

**Structural lesson.** Hybrid sectors ≠ transport. The existence of multi-block joint eigenspaces is not sufficient for nontrivial transport topology. Systems whose transport center coincides with the full commutant decompose into G-invariant isotypic components with diagonal K. The Rubik system is nontrivial precisely because its transport center is incomplete: Z ⊊ C(ρ) massively (9 sectors vs 51 isotypic components), enabling 10 direct edges and 5 T7 morphisms.

All numerical values, exhaustive tables, and computational details are the authoritative domain of the Unified Computational Supplement (CCS-r2, `ccs/canonical_specification.md`). The present paper reports the structural conclusions; CCS certifies the numbers.

The transport graph developed here identifies the static compositional architecture of the representation. The dynamical accessibility consequences — including Lie-generated accessibility, compositional accessibility, and the formal definition of T7 morphisms — are deferred to \cite{paper3}.

***

## References

**Mathematical lineage.** This paper belongs to the tradition of **structure theory of finite-dimensional semisimple algebras and their commutants** — the Artin-Wedderburn decomposition of $\mathbb{C}[G]$-modules, the double commutant theorem, and the resulting block / isotypic stratification of intertwiners. The transport tensor $T_{\alpha\beta}(g) = P_\alpha \rho(g) P_\beta$ is a matrix coefficient of $\rho$ projected onto primitive idempotents in the commutant of the averaging operator; its sparsity pattern is governed by the noncommutative simple components of $A_{\mathrm{EP}}$. The lineage runs: representation theory of finite groups (Serre 1977) → semisimple algebras and Artin-Wedderburn (Curtis-Reiner 1962, Lam 2001) → double commutant theory for finite-dimensional $\mathbb{C}$-algebras (Goodman-de la Harpe-Jones 1989) → the present structural analysis. Association-scheme references shared with \cite{paper1} are repeated below for self-containedness.

### Semisimple algebras, double commutant, and Artin-Wedderburn

[1] C.W. Curtis and I. Reiner, *Representation Theory of Finite Groups and Associative Algebras*. Interscience, New York, 1962. (Reprinted: AMS Chelsea, 2006.)
  — Semisimple algebras, the Artin-Wedderburn structure theorem ($\mathbb{C}[G] \cong \bigoplus_i M_{n_i}(\mathbb{C})$), and the double commutant theorem $\operatorname{End}_{\operatorname{Comm}(A)}(V) = A$ for semisimple $A$. The decomposition $A_{\mathrm{EP}} \cong M_2(\mathbb{C})^4 \oplus M_1(\mathbb{C})^4$ and the double-commutant identity (verified in the Double Commutant section) are direct applications.

[2] T.Y. Lam, *A First Course in Noncommutative Rings*, 2nd ed. Graduate Texts in Mathematics 131, Springer, 2001.
  — Semisimple rings, the Jacobson density theorem, and the structure of finite-dimensional simple algebras over $\mathbb{C}$. The $M_2(\mathbb{C})$ components of $A_{\mathrm{EP}}$ are the minimal noncommutative simple ideals; their overlap geometry under the primitive sector projectors drives the hub-necessity argument (see Hub Necessity).

[3] F. Goodman, P. de la Harpe, and V.F.R. Jones, *Coxeter Graphs and Towers of Algebras*. Mathematical Sciences Research Institute Publications 14, Springer, 1989.
  — Towers of finite-dimensional $\mathbb{C}$-algebras and their commutants. The refinement POSET of commuting subalgebras and the obstruction to further refinement by noncommuting elements — the algebraic mechanism behind the 9-sector cap (see the Obstruction Lattice section) — is the finite-dimensional analogue of the inclusion-lattice structure developed here.

### Representation theory of finite groups

[4] J.-P. Serre, *Linear Representations of Finite Groups*. Graduate Texts in Mathematics 42, Springer, 1977.
  — Canonical reference. Schur's Lemma and isotypic decomposition supply the block-diagonal structure of $\rho$; the vanishing of $T_{\alpha\beta}(g)$ on disjoint isotypic components (Paper~III, Lemma~\ref{lem:pure-sector-obstruction}) is a direct corollary.

[5] P. Diaconis, *Group Representations in Probability and Statistics*. IMS Lecture Notes, 1988.
  — Spectral analysis of group-valued random walks. The averaging operator $A$ governs equilibrium; this paper studies the per-generator transport before averaging — the matrix coefficients $T_{\alpha\beta}(g)$ whose spectral pattern $A$ averages out.

### Association schemes (shared foundation with \cite{paper1})

[6] E. Bannai and T. Ito, *Algebraic Combinatorics I: Association Schemes*. Benjamin/Cummings, 1984.
  — Bose-Mesner algebra of the underlying permutation association scheme. The block-level spectral structure and primitive-idempotent decomposition — the input to this paper's transport analysis — are established in \cite{paper1} within this framework.

[7] C.D. Godsil, *Algebraic Combinatorics*. Chapman & Hall, 1993.
  — Coherent configurations and their commuting algebras. The Type II CP-permutation channel arises from the Bose-Mesner algebra of the Q₃ Hamming scheme acting on the corner-permutation block — the simplest example of commutative-permutation transport disjoint from the noncommutative Type I mechanism.

### Trilogy cross-references

\cite{paper1}, \cite{paper3}, and \cite{ccs} are defined in `papers/tex/trilogy.bib`.

### Code Availability

All numerical experiments, projector constructions, transport computations,
and figure-generation scripts are available at:

https://github.com/dooven-prime/rime-lite

The repository also contains the Unified Computational Supplement (CCS),
canonical datasets, and reproducibility notebooks corresponding to the trilogy.

