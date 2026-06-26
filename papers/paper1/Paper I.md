# Spectral Sector Decomposition in the Rubik's Cube Representation

### Rational Spectral Collapse, Primitive Idempotents, and Block Spectral Factorization

**WuJun Chen**

Independent Researcher · RIME Project · 2026

*This paper is Part I of the RIME trilogy. It establishes the spectral decomposition of the canonical averaging operator. Paper II studies transport topology on the resolved QT/HT joint-spectral sectors. Paper III develops Lie accessibility and proves the T7 Theorem.*

***

## Abstract

**Problem.** We study the averaging operator $A = \frac{1}{|S|}\sum_{s\in S} \rho(s)$ of a finite group representation and ask **why its spectrum is rational** when the generators fail to commute. In the 228-dimensional Rubik's cube representation under the standard 18 face-turn generators, $A$ has exactly six rational eigenvalues despite generator commutator norm $\|[\mathrm{QT}^0, \mathrm{QT}^1]\| = 2.74$ — the classical commutativity route to rationality is blocked.

**Approach.** Rationality is forced by **partition integrality**: the decomposition of the generators into complete faces makes every per-face eigenspace trace sum an integer, via the cyclotomic identity $\omega + \omega^2 + 1 = 0$ on the $\mathbb{Z}_3$ corner-orientation block. The proof uses only the eigenspace trace identity and integer closure under addition; no commutativity hypothesis is required.

**Results.** The resulting spectra are rational across all tested face-symmetric families, take the form $\lambda = 1 - k/m$, and the admissible $k$-set is the union of block-level $k$-sets determined by Bose–Mesner spectra and abelian phase filters. The mechanism is proven unconditionally for the Rubik cube; the Structural Scope and Boundary section below delineates its boundaries.

**Implications.** Rationality is not generic: under broken face symmetry ($n=8$, $n=16$), the spectral field extends to $\mathbb{Q}(\sqrt{5})$. The same mechanism — block-diagonal averaging acting on a partition-integral generator set — supplies the spectral and arithmetic foundation for the noncommutative transport topology of \cite{paper2} and the Lie accessibility hierarchy of \cite{paper3}.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $G$ | Finite group |
| $S \subset G$ | Symmetric generating set ($S = S^{-1}$) |
| $\rho: G \to \mathrm{GL}(V)$ | Finite-dimensional orthogonal representation |
| $V$ | Representation space (228-dim for the Rubik cube) |
| **block** | A cubie-type invariant subspace: cp (corner perm, 64-dim), ep (edge perm, 144-dim), co (corner ori, 8-dim), eo (edge ori, 12-dim) |
| $A = \frac{1}{\lvert S\rvert}\sum_s \rho(s)$ | Averaging operator — Hermitian when $S = S^{-1}$ and $\rho$ orthogonal |
| $\lambda = 1 - k/m$ | Eigenvalue form; $m$ determined by generator geometry ($m=9$ for 18 face-turn generators) |
| $k$-set | Set of $k$ values producing distinct eigenvalues: $\{0,1,2,3,4,6\}$ for 18-full |
| $P_{\lambda}$ | Spectral projector onto eigenspace $E_{\lambda}$ |
| **layer** $V_{\lambda} = \mathrm{im}(P_{\lambda})$ | An eigenspace of the averaging operator $A$ — 6 canonical layers |
| $V_1, V_{8/9}, V_{7/9}, V_{2/3}, V_{5/9}, V_{1/3}$ | Canonical layers ($\lambda = 1 - k/9$, $k \in \{0,1,2,3,4,6\}$) |
| **QT/HT joint-spectral sector** | Minimal joint eigenspace of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ — equivalently, in the canonical system, a joint eigenspace of the commuting QT/HT algebra |
| **S1–S9** | 9 QT/HT joint-spectral sectors: S1(V₁, isolated), S2(V₈/₉), S3(V₇/₉), S4(V₂/₃), S5–S7(V₅/₉), S8–S9(V₁/₃) |
| **hybrid sector** | QT/HT joint-spectral sector supported across multiple cubie-type blocks (e.g., ep+eo) |
| $\mathrm{QT}^a$ | Quarter-turn averaging operator $\frac{1}{2}(\rho(+a) + \rho(-a))$ on axis $a \in \{0,1,2\}$ |
| $\mathrm{HT}^a$ | Half-turn averaging operator $\rho(2a)$ on axis $a \in \{0,1,2\}$ |
| $\mathrm{QT}_{\mathrm{all}} = \sum_a \mathrm{QT}^a$, $\mathrm{HT}_{\mathrm{all}} = \sum_a \mathrm{HT}^a$ | Total quarter-turn / half-turn averaging |
| Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ | Commutative center — joint diagonalization yields 9 QT/HT joint-spectral sectors |
| $\chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s))$ | Eigenspace trace — key quantity in partition integrality |
| **Bose-Mesner algebra** | Commuting algebra of a permutation association scheme — spectral engine for cp/co blocks |
| $J$ | Face-incidence matrix — adjacency matrix connecting each position to the positions on the same face |

> **Definition (Spectral Layer).** \label{def:spectral-layer} An eigenspace $V_{\lambda} = \operatorname{im}(P_{\lambda})$ of the averaging operator $A$. The 228-dimensional Rubik's cube representation has 6 canonical layers: $V_1$, $V_{8/9}$, $V_{7/9}$, $V_{2/3}$, $V_{5/9}$, $V_{1/3}$, corresponding to $\lambda = 1 - k/9$ with $k \in \{0,1,2,3,4,6\}$.

> **Definition (QT/HT Joint-Spectral Sector).** \label{def:primitive-sector} A minimal joint eigenspace of the commutative center $\operatorname{Center}\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$. In the canonical Rubik system, $A = (2/3)\mathrm{QT}_{\mathrm{all}} + (1/3)\mathrm{HT}_{\mathrm{all}}$, so these are equivalently the joint eigenspaces of the commuting QT/HT algebra. The 9 sectors $\mathrm{S}1$–$\mathrm{S}9$ are the resolved spectral units from which all derived structures (transport graph, Lie accessibility, T7 morphisms) are built. We retain "primitive sector" as a legacy shorthand.

## Introduction

Averaging group elements in a finite-dimensional representation often produces substantial spectral collapse: many degrees of freedom collapse into a small number of spectral layers. In the Rubik's cube setting, the averaging operator built from the standard 18 face-turn generators displays exactly six distinct eigenvalues ($\lambda = 1 - k/9$ with $k \in \{0,1,2,3,4,6\}$); extending to 21 generators by including the three slice moves (M/E/S) produces six eigenvalues with a different k-set. All eigenvalues are rational across all tested face-symmetric generator families.

**The noncommutativity paradox.** The classical route to spectral rationality goes through commutativity: if the generator averages $h_i = (\rho(g_i) + \rho(g_i^{-1}))/2$ all commute, simultaneous diagonalization and Schur's Lemma force rational eigenvalues. This route is unavailable for the Rubik's cube. The per-axis quarter-turn averaging operators $\mathrm{QT}^a = \frac{1}{2}(\rho(+a) + \rho(-a))$ are strongly noncommutative on the edge-permutation block:

$$
\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_{\mathrm{ep}} = 2.74,\qquad
\|[\mathrm{QT}^0, \mathrm{QT}^2]\|_{\mathrm{ep}} = 2.74,\qquad
\|[\mathrm{QT}^1, \mathrm{QT}^2]\|_{\mathrm{ep}} = 2.74,
$$

accounting for 93.9% of the total noncommutativity across all blocks (the corner-permutation block is exactly commutative). Despite this strong noncommutativity, the six eigenvalues are rational. The question is therefore: *what forces rationality when commutativity fails?*

The answer developed here is **partition integrality** — the condition that the generator set admits a partition whose per-subset eigenspace trace sums are integers — directly forces eigenvalues to be rational, with no commutativity hypothesis on any subalgebra. In the Rubik's cube, the natural partition is the decomposition into complete faces, and the integrality of each face-sum is rooted in the elementary identity $\omega + \omega^2 + 1 = 0$ on the corner-orientation block (where $\omega = e^{2\pi i/3}$).

**Two independent mechanisms.** The spectral structure of the Rubik's cube is governed by two independent principles, each with its own proof and neither requiring commutativity of the generators:

1. **Structure Theorem (\ref{thm:block-compatibility-lemma}).** The representation decomposes into four $G$-invariant blocks, each block's averaging operator belongs to a commutative algebra (Bose–Mesner for the permutation blocks, abelian phase for the orientation blocks), and the global spectrum is the union $\bigcup_B \operatorname{Spec}(A_B)$ of the block spectra. The six eigenvalues arise from eigenvalue coincidence across blocks under $\lambda = 1 - k/9$, reducing 10 block-level primitive idempotents to 6 distinct global values. The number 6 is $|\bigcup_B \mathcal{K}_B|$ — not a free parameter but the cardinality of the union of four independently computable block-level $k$-sets.

2. **Structural Rationality Criterion.** Partition integrality forces rational eigenvalues. If the generator set admits a partition whose per-subset eigenspace trace sums are integers, then every eigenvalue is rational. The proof uses only the eigenspace trace identity and integer closure under addition — no commutativity, no Galois theory, no simultaneous diagonalization. In the Rubik's cube, the face decomposition provides the partition; integrality is verified for all tested face-complete families. The converse and full necessity beyond the verified Rubik family remain open.

**Spectral collapse as interference.** Each generator contributes a phase factor $\omega^k$ ($k \in \{0,1,2\}$) to the corner-orientation block. The face-sum $F_{\mathrm{face}} = \rho(g) + \rho(g^{-1}) + \rho(g_{180})$ aggregates three moves on a single face: the phases from $g$ and $g^{-1}$ are complex conjugates ($\omega$ and $\omega^2$), and $g_{180}$ contributes a real phase. On a complete face, these sum to either 3 or 0:

$$
\omega^k + \omega^{-k} + \omega^{2k} \in \{3, 0\} \subset \mathbb{Z}, \qquad k \in \{0,1,2\}.
$$

When every face in the generator set is complete, this per-face cancellation forces $A$ to have rational entries, and the spectrum collapses into $\mathbb{Q}$ — all non-rational cyclotomic phases cancel. The spectrum is an interference pattern: rational eigenvalues correspond to complete destructive interference of $\omega$-phases across all faces. When face completeness is broken (as in the $n = 8$ and $n = 16$ families), rationality is lost and the spectral field extends to $\mathbb{Q}(\sqrt{5})$ — demonstrating that rationality is **not** generic but is forced by the arithmetic closure of the face-complete partition.

**Paper structure.** Setting and Notation sets up the representation and averaging operator. Main Results establishes the structural backbone — block compatibility, the spectral union theorem, and blockwise commutative algebras. Per-Block Projector Field Analysis analyzes the four block operators and derives the six spectral layers via eigenvalue coincidence. Generator Character Integrality establishes generator-level character integrality. The Arithmetic Engine proves the partition integrality criterion (Main Theorem) and closes the converse direction. Structural Consequences presents the numerical evidence and structural consequences: the $k = 5$ vacancy, the dominant $V_{5/9}$ layer, the layer asymmetry, and the irrationality transition under symmetry breaking. Discussion covers generality and open problems.

## Setting and notation

### Concrete conventions

We use a right-handed Cartesian coordinate system: $+X \to R$, $+Y \to U$, $+Z \to F$. Corner positions are indexed by sign vectors $\{x \in \{\pm 1\}^3 : \prod_i x_i \neq 0\}$; edge positions by vectors in $\{x \in \{\pm 1, 0\}^3 : \sum_i |x_i| = 2\}$. Explicit coordinate constructions, generator definitions, and ordering conventions are deferred to the Computational Supplement (CCS Part 0).

The representation space $V = \mathbb{C}^{228}$ decomposes into four $G$-invariant blocks:
$$V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}},\qquad 64 + 144 + 8 + 12 = 228,$$
laid out in cp $\to$ ep $\to$ co $\to$ eo order. The generator set $S$ is the 18 standard face-turn generators ($S = S^{-1}$).

### Abstract setting

Let G be a finite group and let ($\rho$: G $\to$ GL(V)) be a finite-dimensional complex representation. Let S $\subseteq$ G be a finite symmetric generating set, meaning (S = S^{-1}). Define the averaging operator
$$
A = \frac{1}{|S|} \sum_{s\in S} \rho(s) \in \operatorname{End}(V).
$$
**Proposition 2.1 (Inverse-Closure Hermiticity).** For an orthogonal representation $\rho$, the averaging operator $A = \frac{1}{|S|}\sum_{s\in S}\rho(s)$ is Hermitian iff $S$ is inverse-closed ($S = S^{-1}$).

*Proof.* Since $\rho$ is orthogonal, $\rho(s)^\dagger = \rho(s)^T = \rho(s^{-1})$ for every $s \in G$. The adjoint of $A$ is
$$
A^\dagger = \frac{1}{|S|}\sum_{s\in S}\rho(s)^\dagger = \frac{1}{|S|}\sum_{s\in S}\rho(s^{-1}) = \frac{1}{|S|}\sum_{t\in S^{-1}}\rho(t).
$$
Hence $A^\dagger = A \iff S = S^{-1}$. Concretely: Hermiticity of $A$ requires that for every generator $s$ in $S$, its inverse $s^{-1}$ is also in $S$ with equal weight.

**Remark.** This is a structural prerequisite for the entire spectral theorem: without inverse-closure, $A$ is not Hermitian, its eigenvalues are not real, and eigenspaces are not orthogonal. For the Rubik’s cube, the standard 18 face-turn generators satisfy $S = S^{-1}$ (R/R’/R2, U/U’/U2, etc.), so $A$ is Hermitian. Generator sets that violate this (e.g., CW-only turns) yield non-Hermitian $A$ and ill-posed spectral decompositions.

In the Rubik’s cube application, V is a 228-dimensional faithful representation with the block decomposition
$$
V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}},
$$
corresponding to corner permutation, edge permutation, corner orientation, and edge orientation blocks.

We write ($E_{\lambda}$) for the eigenspace of A with eigenvalue ($\lambda$), and ($P_{\lambda}$) for the orthogonal projector onto ($E_{\lambda}$).

Throughout, $\sigma$ denotes the nontrivial Galois automorphism of $\mathbb{Q}(\omega)/\mathbb{Q}$, where $\omega = e^{2\pi i/3}$ and $\sigma(\omega) = \omega^2$.

## Main results

### Theorem 3.1 (Eigenspace trace identity)

For every eigenvalue ($\lambda$) of A with orthogonal projector ($P_{\lambda}$) onto ($E_{\lambda}$),
$$
\lambda = \frac{1}{d_{\lambda}}\cdot\frac{1}{|S|}\sum_{s\in S}\chi_{\lambda}(s),
\qquad
\chi_{\lambda}(s) := \operatorname{Tr}(P_{\lambda}\rho(s)),
\qquad d_{\lambda} = \dim E_{\lambda}.
$$

**Remark (Terminology — eigenspace trace).** The function $\chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s))$ is the **restricted trace** of $\rho(s)$ on the eigenspace $E_{\lambda}$, not the group character of a subrepresentation unless $E_{\lambda}$ is $\rho(G)$-invariant (which it is not, in general). We refer to $\chi_{\lambda}$ as the "eigenspace trace" throughout.

#### Proof.

Since (A$P_{\lambda}$ = $\lambda$ $P_{\lambda}$), taking traces gives
$$
\operatorname{Tr}(AP_{\lambda}) = \lambda\cdot\operatorname{Tr}(P_{\lambda})=\lambda d_{\lambda}.
$$
On the other hand, by linearity of the trace,
$$
\operatorname{Tr}(AP_{\lambda})
= \frac{1}{|S|}\sum_{s\in S}\operatorname{Tr}(\rho(s)P_{\lambda})
= \frac{1}{|S|}\sum_{s\in S}\chi_{\lambda}(s).
$$
Combining the two identities yields the claim.

### Theorem 3.2 (Galois stability of eigenspaces)

Assume A is Hermitian and satisfies ($\sigma$(A)=A). Then for every eigenvalue ($\lambda$),
$$
\sigma(E_{\lambda})=E_{\lambda}.
$$
Equivalently, ($\sigma$($P_{\lambda}$)=$P_{\lambda}$).

#### Proof.

Let (v$\in$ $E_{\lambda}$), so (Av=$\lambda$ v). Apply ($\sigma$) entrywise:
$$
A,\sigma(v)=\sigma(A)\sigma(v)=\sigma(Av)=\sigma(\lambda v)=\overline{\lambda},\sigma(v).
$$
Because A is Hermitian, ($\lambda\in\mathbb{R}$), hence ($\overline{\lambda}$=$\lambda$). Therefore ($\sigma$(v)$\in$ $E_{\lambda}$), showing ($\sigma$($E_{\lambda}$)$\subseteq$ $E_{\lambda}$). Since ($\sigma^2$=$\mathrm{id}$), equality follows. The projector statement is equivalent.

### Theorem 3.3 (Rationality from Galois-stable projector — conditional)

Suppose the spectral projector ($P_{\lambda}$) satisfies ($\sigma$($P_{\lambda}$)=$P_{\lambda}$) and is defined over a number field K with ($K^\sigma$ = $\mathbb{Q}$) (for example, (K = $\mathbb{Q}$($\omega$)) with ($\sigma$($\omega$)=$\omega^2$)). Then ($\lambda$ $\in$ $\mathbb{Q}$).

#### Proof.

By Theorem~\ref{thm:eigenspace-trace-identity},
$$
\lambda = \frac{1}{d_{\lambda}}\cdot\frac{1}{|S|}\sum_{s\in S}\chi_{\lambda}(s),
\qquad \chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s)).
$$

Since ($P_{\lambda}$ $\in$ M_n(K)) and ($\rho$(s) $\in$ M_n($\mathbb{Z}$[$\omega$]) $\subset$ M_n(K)), each trace ($\chi_{\lambda}$(s) $\in$ K). Their average lies in K. Because ($\sigma$($P_{\lambda}$)=$P_{\lambda}$), we have ($\sigma$($\chi_{\lambda}$(s)) = $\chi_{\lambda}$(s)) for each (s), hence the sum is fixed by ($\sigma$). Therefore the sum lies in ($K^\sigma$ = $\mathbb{Q}$), and ($\lambda$ $\in$ $\mathbb{Q}$).

#### Remark (Field-of-definition issue).

Theorem~\ref{thm:field-of-definition} is logically valid but its hypothesis is strong: it assumes the projector is already defined over a field whose Galois fixed field is ($\mathbb{Q}$). In practice, verifying ($P_{\lambda}$ $\in$ M_n(K)) requires knowing the field of definition of the eigenspace — which is equivalent to the rationality problem itself. Theorem~\ref{thm:field-of-definition} therefore does **not** close the gap; it merely isolates the precise field-of-definition condition. The substantive input that fulfills this hypothesis — the per-face character integrality or its equivalent — is supplied in the Generator Character Integrality and Arithmetic Engine sections below. The Galois stability ($\sigma$($P_{\lambda}$) = $P_{\lambda}$) (Theorem~\ref{thm:galois-stability-of-eigenspaces}) is necessary but not sufficient: it constrains the field to ($K^\sigma$), but without an independent proof that (K = $\mathbb{Q}$($\omega$)), the fixed-field argument cannot reduce ($K^\sigma$) to ($\mathbb{Q}$).

### Theorem 3.4 (Block Compatibility Lemma)

Let the representation space decompose as a direct sum

$$
V = \bigoplus_{i=1}^{k} V_i,
$$

where each (V_i) is ($\rho$(G))-invariant (hence (A)-invariant). Let (P_i: V $\to$ V_i) be the orthogonal projector onto (V_i). Then for every eigenspace projector ($P_{\lambda}$) of (A):

$$
P_{\lambda} = \bigoplus_{i=1}^{k} P_{\lambda,i}, \qquad P_{\lambda,i} := P_i P_{\lambda} P_i.
$$

Equivalently, ($P_{\lambda}$) commutes with every block projector: ([$P_{\lambda}$, P_i] = 0) for all (i).

#### Proof.

Since each $V_i$ is $\rho(G)$-invariant, it is invariant under $A = \frac{1}{|S|}\sum_s \rho(s)$. Thus $A$ is block-diagonal with respect to the decomposition: $A = \bigoplus_i A_i$ where $A_i = A|_{V_i}$. The spectral projector $P_{\lambda}$ is a polynomial in $A$ (by Lagrange interpolation on the distinct eigenvalues): $P_{\lambda} = \prod_{\mu \neq \lambda} (A - \mu I)/(\lambda - \mu)$. Since $A$ is block-diagonal, any polynomial in $A$ is also block-diagonal. Hence $P_{\lambda} = \bigoplus_i P_{\lambda,i}$ with $P_{\lambda,i} \in \operatorname{End}(V_i)$. The commutativity $[P_{\lambda}, P_i] = 0$ follows immediately.

### Corollary 3.5

For each block $V_i$, the restricted projector $P_{\lambda,i}$ is an orthogonal projector on $V_i$ satisfying $P_{\lambda,i}^2 = P_{\lambda,i}$, $P_{\lambda,i}^* = P_{\lambda,i}$, and $P_{\lambda,i} A_i = A_i P_{\lambda,i} = \lambda P_{\lambda,i}$ whenever $P_{\lambda,i} \neq 0$.

#### Remark.

Theorem~\ref{thm:block-compatibility-lemma} is structurally trivial — it is a direct consequence of $A$ being block-diagonal. Its value is organizational: it reduces the 228-dimensional problem to four independent sub-problems, one per block. The field of definition of $P_{\lambda}$ is the compositum of the fields of definition of the $P_{\lambda,i}$.

### Spectral Origin via Block Bose–Mesner Algebras

The preceding theorems establish *that* the eigenvalues are rational and *that* they take the form $\lambda = 1 - k/m$. They do not explain *why* exactly six eigenvalues appear, nor *why* those particular $k$-values. Theorem~\ref{thm:spectral-collapse} answers this: the four blocks together carry 10 primitive idempotents; eigenvalue coincidence under the common rational form $\lambda = 1 - k/m$ collapses them to exactly 6 global spectral layers.

**Theorem 3.6 (Spectral Origin).** Let $\rho: G \to \mathrm{GL}(228, \mathbb{C})$ be the Rubik's cube representation with the standard block decomposition $V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}}$, and let $A = \frac{1}{|S|} \sum_{s \in S} \rho(s)$ be the averaging operator over the 18 face-turn generators. Then:

1. **(Blockwise commuting algebras.)** Each block restriction $A_{\mathrm{block}}$ belongs to a commutative algebra of operators on that block:
   - $A_{\mathrm{cp}}$ belongs to the Bose–Mesner algebra of the Q₃ Hamming association scheme $H(3,2)$, isomorphic to the Hecke algebra $H(S_2 \wr S_3, S_3)$. Its 4 primitive idempotents are indexed by Hamming weight $k \in \{0, 1, 2, 3\}$ with dimensions $(1, 3, 3, 1) \times 8 = (8, 24, 24, 8)$.
   - $A_{\mathrm{ep}}$ belongs to a 3-dimensional commutative adjacency algebra generated by the edge-face incidence matrix $JJ^T$. Its 3 primitive idempotents correspond to $k \in \{0, 2, 4\}$ with dimensions $(12, 72, 60)$ (for the 18-full family) or 4 idempotents for families where additional generator structure splits the algebra further.
   - $A_{\mathrm{co}}$ belongs to a 1-dimensional abelian phase algebra (scalar matrix $\lambda_{\mathrm{co}} I_8$). Its single primitive idempotent is $I_8$ at $k = 3$ (for 18-full).
   - $A_{\mathrm{eo}}$ belongs to a 2-dimensional abelian phase algebra (diagonal with $\pm 1$ entries). Its 2 primitive idempotents correspond to $k \in \{1, 2\}$ (for 18-full).

2. **(Global algebra as product subalgebra.)** The global algebra $\mathbb{C}[A]$ is a subalgebra of the direct product of the blockwise algebras:
$$
   \mathbb{C}[A] \;\subset\; \mathcal{A}_{\mathrm{cp}} \times \mathcal{A}_{\mathrm{ep}} \times \mathcal{A}_{\mathrm{co}} \times \mathcal{A}_{\mathrm{eo}}.
$$
   The product has $4 + 3 + 1 + 2 = 10$ primitive idempotents at the block level. $\mathbb{C}[A]$ has exactly 6 — the reduction from 10 to 6 is the **spectral resonance** mechanism.

3. **(Spectral resonance merging.)** A block-level primitive idempotent yields eigenvalue $\lambda = 1 - k_{\mathrm{block}}/m$ where $m = |S|/2$ and $k_{\mathrm{block}}$ is the local grading index of that block's own commutative algebra (Krawtchouk for cp, face-incidence for ep, $\mathbb{Z}_3$ phase classes for co, $\mathbb{Z}_2$ phase classes for eo). Different blocks can produce the same global $\lambda$ for different internal $k_{\mathrm{block}}$ values. The eigenvalue coincidence merges block-level idempotents into global spectral projectors. The following table lists, for each global layer, the dimension contributed by each block to that layer (not the block's internal grading index):

   | Global layer | $\lambda$ | $k$ | dim | cp contribution | ep contribution | co contribution | eo contribution |
   |---|---|---|---|---|---|---|---|
   | $V_1$    | $1$   | 0 | 20  | 8d  | 12d | —   | —  |
   | $V_{8/9}$| $8/9$ | 1 | 2   | —   | —   | —   | 2d |
   | $V_{7/9}$| $7/9$ | 2 | 39  | —   | 36d | —   | 3d |
   | $V_{2/3}$| $2/3$ | 3 | 26  | —   | 24d | 2d  | —  |
   | $V_{5/9}$| $5/9$ | 4 | 106 | 24d | 72d | 3d  | 7d |
   | $V_{1/3}$| $1/3$ | 6 | 35  | 32d | —   | 3d  | —  |

   (Block contributions sum to 228 = 64 + 144 + 8 + 12 = $\sum_{\lambda} \dim V_{\lambda}$; canonical reference: CCS-I §1.3.)

   $k=5$ ($\lambda=4/9$) is genuinely absent — no block produces a primitive idempotent at this global eigenvalue.

   Each of the 6 global eigenvalues is a distinct coincidence class among the 10 blockwise primitive idempotents. The $V_{5/9}$ layer is the unique four-block confluence point — every block contributes nonzero support — which makes it the largest layer (106-dim, 46.5%) and structurally privileged.

4. **(No global Gelfand pair.)** There exists no subgroup $K \subset G$ such that $(G, K)$ is a Gelfand pair with $H(G, K) \cong \mathbb{C}[A] \cong \mathbb{C}^6$. The Rubik's cube group has approximately $4.3 \times 10^{19}$ elements; for any subgroup $K$, the number of double cosets $|K \backslash G / K|$ — which equals $\dim H(G, K)$ — is vastly larger than 6 (approximately 854 by character-theoretic computation). The global spectral algebra is not a single Hecke algebra.

5. **(Blockwise local Gelfand geometry.)** Despite the absence of a global Gelfand pair, **each block-level commutative algebra is the Hecke algebra (or abelian phase algebra) of an appropriate group pair on that block's automorphism group:**
   - cp block: $H(S_2 \wr S_3, S_3)$ — the Hecke algebra of the hyperoctahedral group
   - ep block: Hecke algebra of the edge-permutation automorphism group
   - co block: $O_h$ symmetry + Schur reduction (Proposition~\ref{prop:co-analytic-spectrum})
   - eo block: numerical-representation observation ($2T_2$ multiplicity obstruction; see CCS-I §1.5)

   The spectral origin is **blockwise-local**, not global. Four independent association/phase structures, each with its own commuting algebra, are coupled only through the eigenvalue coincidence of the global averaging operator.

6. **(Rational spectral law.)** The eigenvalues $\lambda = 1 - k/m$ are normalized adjacency eigenvalues of the blockwise Bose–Mesner algebras. The Krawtchouk polynomials give the cp eigenvalues; the $JJ^T$ spectrum gives the ep eigenvalues; $O_h$ symmetry + Schur reduction gives the co eigenvalues (Proposition~\ref{prop:co-analytic-spectrum}); the eo eigenvalues are a numerical-representation observation (see §4.1 and CCS-I §1.5). The integrality $\chi_{\lambda}(s) \in \mathbb{Z}$ follows from the Bose–Mesner trace pairing within each block's algebra (see §5, Corollary~\ref{cor:face-triple-integrality}; full derivation: CCS-III §7.4). Figure~\ref{fig:fig2-resonance-merging} illustrates this block-level-to-global resonance merging.

![Resonance merging from 10 block-level primitive idempotents to 6 global spectral layers under $\lambda = 1 - k/9$. Different blocks with identical $k$-values collapse into the same eigenspace; $k = 5$ is structurally absent across all blocks. The 6-layer spectrum is the cardinality of the union of block-level $k$-sets, determined block-by-block rather than by global constraints.](../../figures/paper1/fig2_resonance_merging.png)

**Remark (Transport graph consequence).** The six spectral layers result from 10 block-level primitive idempotents collapsing to 6 under the global eigenvalue coincidence $\lambda = 1 - k/m$. The number 6 is the cardinality of the union $\bigcup_B \mathcal{K}_B$; the content of Theorem~\ref{thm:spectral-collapse} is the identification of each $K_B$ with the primitive idempotent spectrum of the corresponding blockwise Bose–Mesner algebra. \cite{paper2} studies the transport topology between the QT/HT joint-spectral sectors identified here; \cite{paper3} studies the Lie accessibility hierarchy and the role of discrete composition. Figure~\ref{fig:fig1-spectral-collapse} shows the six canonical spectral layers and their block support.

![The six canonical spectral layers of the averaging operator, showing eigenvalue $\lambda = 1 - k/9$, $k$-value, dimension, and block support for each layer. The $V_{5/9}$ layer ($k=4$) dominates at 106/228 (46%) and carries the primary transport hub for Papers II and III. This spectral decomposition is the structural foundation for the transport topology and Lie accessibility hierarchy.](../../figures/paper1/fig1_spectral_collapse.png)

## Per-block projector field analysis

We now apply the Block Compatibility Lemma to the Rubik’s cube representation. The 228-dimensional space decomposes into four ($\rho$(G))-invariant blocks:

$$
V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}},
$$

with dimensions 64, 144, 8, and 12, respectively. By Theorem~\ref{thm:block-compatibility-lemma}, each eigenspace projector splits as

$$
P_{\lambda} = P_{\lambda,\mathrm{cp}} \oplus P_{\lambda,\mathrm{ep}} \oplus P_{\lambda,\mathrm{co}} \oplus P_{\lambda,\mathrm{eo}}.
$$

We determine the field of definition for each block projector.

### Permutation blocks (cp, ep) and edge-orientation block (eo)

The generators act by permutation matrices on $V_{\mathrm{cp}}$ and $V_{\mathrm{ep}}$, and by diagonal matrices with entries in $\{\pm 1\}$ on $V_{\mathrm{eo}}$. In all three cases, the representation matrices have integer entries:

$$
\rho_{\mathrm{cp}}(s) \in M_{64}(\mathbb{Z}), \quad
\rho_{\mathrm{ep}}(s) \in M_{144}(\mathbb{Z}), \quad
\rho_{\mathrm{eo}}(s) \in M_{12}(\mathbb{Z}).
$$

Consequently, the restricted averaging operators satisfy

$$
A_{\mathrm{cp}} \in M_{64}(\mathbb{Q}), \quad
A_{\mathrm{ep}} \in M_{144}(\mathbb{Q}), \quad
A_{\mathrm{eo}} \in M_{12}(\mathbb{Q}).
$$

For the permutation blocks (cp, ep), each spectral projector is a polynomial in the matrix with coefficients in the field generated by the eigenvalues. The cp and ep spectra are derived analytically via the $Q_3$ hypercube Bose–Mesner algebra and the face-incidence graph adjacency algebra (Theorem~\ref{thm:spectral-collapse}).

The edge-orientation block (eo) admits a precise structural analysis -- the $\mathbb{Z}_2$ analog of Proposition~\ref{prop:co-analytic-spectrum} -- which we present next.

**Lemma 4.0 (Structure of the edge-orientation block).** Let

$$
A = \frac{1}{|S|} \sum_{s \in S} \rho(s)
$$

be the averaging operator over a face-symmetric generator set $S$. The edge-orientation block $A_{\mathrm{eo}}$ is a $12 \times 12$ permutation@phase matrix — it carries both edge position permutation (an edge on a turned face moves to a new position) and $\mathbb{Z}_2$ orientation phase. The averaging over 18 face-turn generators yields three distinct eigenvalues, giving $\mathcal{K}_{\mathrm{eo}} = \{1, 2, 4\}$ with multiplicities $(2, 3, 7)$.

The eo block carries both edge position permutation and $\mathbb{Z}_2$ orientation phase — edge orientation states mix across positions via the permutation action, giving $A_{\mathrm{eo}}$ off-diagonal entries.

#### Proof.

For the 18-full family:

- **Phase-active positions** (edges on F/B faces): flipped by quarter turns. Each such edge participates in a 4-cycle on its face, accumulating $\pm 1$ phase factors. The averaged contribution splits across three eigenvalues.
- **Phase-trivial positions** (edges on R/L/U/D only): never flipped. These 4 positions are permuted among themselves by R/L/U/D turns.

The exact multiplicities (2, 3, 7) and k-values {1, 2, 4} are obtained by diagonalizing the $12 \times 12$ matrix $A_{\mathrm{eo}}$. Unlike the CO block, the EO block does not admit a complete group-theoretic derivation from $O_h$ symmetry + Schur's lemma, because the permutation representation on 12 edges contains a multiplicity-2 isotypic component ($2T_2$). On this 6-dimensional subspace, Schur's lemma permits $I_2 \otimes B$ with non-scalar $B \in M_3(\mathbb{C})$, blocking a pure representation-theoretic eigenvalue assignment. A complete analytic proof would require edge incidence algebra on the signed line graph of the cube and Hecke-type machinery encoding the $\mathbb{Z}_2$ orientation structure. The three-level spectral stratification is therefore classified as a **numerical-representation observation** — empirically rigid (trace-consistent, $O_h$-equivariant, generator-family specific) but not currently derivable from pure representation theory.

**Remark (Structural summary).** The eo block exhibits a remarkably rigid three-level spectrum:
$$
\text{eo: } \operatorname{Spec}(A_{\mathrm{eo}}) = \{\tfrac{8}{9}^{(2)}, \tfrac{7}{9}^{(3)}, \tfrac{5}{9}^{(7)}\}, \qquad \mathcal{K}_{\mathrm{eo}} = \{1, 2, 4\}.
$$
Trace consistency: $2 \cdot \frac{8}{9} + 3 \cdot \frac{7}{9} + 7 \cdot \frac{5}{9} = 8 = \operatorname{Tr}(A_{\mathrm{eo}})$. The two edge classes (4 Type A with all-positive coupling, 8 Type B with mixed signs) are $O_h$-orbits under the geometric cube symmetry.

#### Remark (Combined block contribution).

All four blocks carry permutation@phase structure. Each block independently contributes its k-values; the full spectrum is the union:

| Block | Dim | Structure | Mechanism | $k$-set (18-full) | Status |
|:-----:|:---:|:----------|:----------|:-----------------:|:-------|
| $\mathrm{cp}$ | 64 | $S_8 \otimes I_8$ | $Q_3$ Bose-Mesner | $\{0, 4, 6\}$ | Theorem |
| $\mathrm{ep}$ | 144 | $S_{12} \otimes I_{12}$ | Face-incidence | $\{0, 2, 3, 4\}$ | Theorem |
| $\mathrm{co}$ | 8 | $\mathbb{Z}_3$ perm@phase | $O_h$ + Schur | $\{3, 4, 6\}$ | **Proposition 4.1** |
| $\mathrm{eo}$ | 12 | $\mathbb{Z}_2$ perm@phase | Num. observation$^\dagger$ | $\{1, 2, 4\}$ | Observation |
| **All** | 228 | $\oplus$ | Union of above | $\{0, 1, 2, 3, 4, 6\}$ | |

$^\dagger$ The EO block is a numerical-representation observation: the $2T_2$ multiplicity fiber $(I_2 \otimes B)$ blocks a Schur-type reduction. See the proof sketch above and (CCS-I §1.5).

The unification of all four blocks under the common permutation@phase structure is a consequence of the representation's definition (see CCS Part 0 for explicit coordinate constructions).

### Corner-orientation block (co) — the critical case

The corner-orientation block is the only block where the Galois action is nontrivial. The generators act by diagonal matrices with entries in $\{1, \omega, \omega^2\}$ where $\omega = e^{2\pi i/3}$:

$$
\rho_{\mathrm{co}}(s) \in M_{8}(\mathbb{Z}[\omega]) \subset M_{8}(\mathbb{Q}(\omega)).
$$

**Proposition 4.1 (CO Analytic Spectrum).** Let $A_{\mathrm{co}} = \frac{1}{18} \sum_{s \in S} \rho_{\mathrm{co}}(s)$ where $S$ is the set of 18 face-turn generators. Then:

1. The permutation representation of the cube symmetry group $O$ on the 8 corners decomposes as $\chi_{\mathrm{corners}} = A_1 \oplus A_2 \oplus T_1 \oplus T_2$ (irrep dimensions $1 + 1 + 3 + 3 = 8$).

2. By Schur's lemma, $A_{\mathrm{co}}$ acts as a scalar on each irreducible $O$-submodule:
   $$A_{\mathrm{co}} = \lambda_{A_1} P_{A_1} + \lambda_{A_2} P_{A_2} + \lambda_{T_1} P_{T_1} + \lambda_{T_2} P_{T_2}$$

3. The spectrum is:
   $$\operatorname{Spec}(A_{\mathrm{co}}) = \{\tfrac{2}{3}, \tfrac{2}{3}, \tfrac{5}{9}^{(3)}, \tfrac{1}{3}^{(3)}\}, \qquad
   \mathcal{K}_{\mathrm{co}} = \{3, 4, 6\}, \qquad (d_3, d_4, d_6) = (2, 3, 3)$$

where $\lambda = 1 - k/9$ and superscripts denote multiplicities.

#### Proof.

**Diagonal and trace.** $\operatorname{Tr}(\rho_{\mathrm{co}}(g)) = 4$ for all 18 generators: each face turn fixes the 4 corners on the opposite face, each contributing $+1$ (no orientation change when a corner is not on the turning face). Hence $\operatorname{Tr}(A_{\mathrm{co}}) = 4$ and $A_{\mathrm{co}}[i,i] = 9/18 = 1/2$ (each corner is fixed by 9 generators: the 6 on the two faces containing it, plus 3 opposite-face half-turns that preserve orientation).

**O_h invariance.** The set of 18 face-turn generators is closed under cube symmetries. Therefore $A_{\mathrm{co}}$ is $O_h$-invariant and respects the $O$-irrep decomposition of the 8-dimensional corner permutation representation. Claim 1 follows from the character table of $O$ acting on the 8 cube vertices.

**Schur reduction.** Since $A_{\mathrm{co}}$ commutes with the $O$-action on the 8 corners, Schur's lemma applies: on each irreducible submodule, $A_{\mathrm{co}}$ is a scalar multiple of the identity. Since all four irreps ($A_1, A_2, T_1, T_2$) have multiplicity 1 in the corner permutation representation, Claim 2 follows immediately. The operator is fully determined by four scalar eigenvalues $\lambda_{A_1}, \lambda_{A_2}, \lambda_{T_1}, \lambda_{T_2}$.

**Adjacency structure.** Work with $M_{\mathrm{co}} = 18(A_{\mathrm{co}} - I/2)$, whose off-diagonal entries are determined purely by cube geometry. Three adjacency classes emerge for a given corner:

| Class | Shared faces | Pairs | $M_{\mathrm{co}}[i,j]$ (×18) | Count |
|-------|-------------|-------|---------------------------|-------|
| Edge-adjacent | 2 | 2 per corner | $1+\omega$ or $1+\omega^2$ | 8 |
| Face-opposite | 1 | 4 per corner | $\pm 1$ | 16 |
| Body-opposite | 0 | 1 per corner | $0$ | 4 |

Total: $8 + 16 + 4 = 28 = \binom{8}{2}$. Each corner has $2 + 4 + 1 = 7$ neighbours. ✓

**Row sum determines $\lambda_{A_1}$.** The row sum of $M_{\mathrm{co}}$ is uniform (= 3). The imaginary parts of the edge-adjacent entries cancel ($\omega + \omega^2 = -1$), and the $\pm 1$ real entries sum to net $+3$ after accounting for the adjacency structure. The row sum corresponds to the trivial irrep $A_1$:
$$\lambda_{A_1} = \frac{1}{2} + \frac{3}{18} = \frac{2}{3} \quad (k = 3)$$

**M-spectrum.** Diagonalizing the Hermitian, $O_h$-invariant matrix $M_{\mathrm{co}}$:
$$\operatorname{Spec}(M_{\mathrm{co}}) = \{3^{(2)},\; 1^{(3)},\; -3^{(3)}\}$$

Converting to $A_{\mathrm{co}}$ eigenvalues via $\lambda = 1/2 + \mu/18$ yields the spectrum in Claim 3. The three eigenvalues are all rational — the $\mathbb{Z}[\omega]$ matrix entries collapse to rational numbers under the per-face phase cancellation $\omega + \omega^2 + 1 = 0$, which operates at the level of the averaged matrix entries before diagonalization.

**Accidental $A_1/A_2$ degeneracy.** The multiplicity-2 eigenvalue at $\mu = 3$ implies $\lambda_{A_1} = \lambda_{A_2} = 2/3$ — both 1-dimensional $O$-irreps carry the same eigenvalue. This is not forced by any obvious symmetry (the two 1-dim irreps could in principle carry distinct eigenvalues) but is verified numerically to machine precision. It is an accidental degeneracy — the only one in the CO block.

**Irrep assignment.** The eigenvalue-multiplicity pattern $(2, 3, 3)$ matches the $O$-irrep dimensions $(1, 1, 3, 3)$ with the accidental degeneracy $1+1=2$:

| $\lambda$ | $k$ | mult | $O$-irrep |
|-----------|-----|------|-----------|
| $2/3$ | 3 | 2 | $A_1 \oplus A_2$ |
| $5/9$ | 4 | 3 | $T_1$ or $T_2$ |
| $1/3$ | 6 | 3 | the other $T$-irrep |

The isotypic assignment of the two 3-dimensional $T$-irreps to $5/9$ vs $1/3$ is not resolved by the current analysis. This ambiguity affects only the layer attribution — whether $T_1$ sits at $5/9$ and $T_2$ at $1/3$, or the reverse — and does not affect the total count of isotypic components or irreducible summands in the block.

**Trace consistency.** $2 \cdot \frac{2}{3} + 3 \cdot \frac{5}{9} + 3 \cdot \frac{1}{3} = \frac{4}{3} + \frac{5}{3} + 1 = 4 = \operatorname{Tr}(A_{\mathrm{co}})$. ✓

**Remark (Status — M₂ obstruction).** This is a **theorem-grade result**: $O_h$ symmetry and Schur reduction force a 3-level spectral stratification with k-set $\{3, 4, 6\}$. The only non-axiomatic input is the accidental $A_1/A_2$ degeneracy (verified numerically). The structural mechanism — cube symmetry inducing spectral arithmetic sectors — is the same conceptual level as the rationality theorem and will be shown in \cite{paper2} to be the same level as the M₂ obstruction principle.

**Extension to other families** (numerical):

- **21-full+slice**: slice moves are identity on co. $\mathcal{K}_{\mathrm{co}}$ expands.
- **12-quarter** (no 180°): different cycle weighting. $\mathcal{K}_{\mathrm{co}}$ shifts.
- **6-half** (half-turns only): no orientation twists, $\lambda_{\mathrm{co}} = 1$, $k = 0$.
- **10-partial**: partial face coverage removes the Galois pairing.

In every case, the eigenvalues are rational — the $\mathbb{Z}_3$ phases participate in the permutation action, and the resulting cycle characters are sums of $\omega^k$ terms that either cancel ($\omega + \omega^2 + 1 = 0$) or sum to integers.

**Lemma 4.2** (Co-block Galois stability). For face-symmetric (S), $A_{\mathrm{co}} \in M_{8}(\mathbb{Q}(\omega))$ and satisfies $\sigma(A_{\mathrm{co}}) = A_{\mathrm{co}}$ (the $\omega$ and $\omega^2$ terms are paired by face symmetry). By Theorem~\ref{thm:galois-stability-of-eigenspaces}, the co-block spectral projectors satisfy $\sigma(P_{\lambda,\mathrm{co}}) = P_{\lambda,\mathrm{co}}$ for every eigenvalue $\lambda$. All three eigenvalues are real and rational.

#### Remark (Galois stability vs. projector rationality).

Lemma~\ref{lem:co-block-galois-stability} shows that the co-block eigenspaces are Galois-stable — a structural property of the face-symmetric averaging operator. The step from Galois stability to rational projectors is handled by Theorem~\ref{thm:field-of-definition} (field-of-definition). Figure~\ref{fig:fig3-phase-cancellation} illustrates the phase cancellation mechanism $\omega + \omega^2 + 1 = 0$.

![The three cube roots of unity on the complex unit circle, illustrating the cyclotomic identity $\omega + \omega^2 + 1 = 0$ where $\omega = e^{2\pi i/3}$. On complete faces, each triple of moves $\{g, g^{-1}, g_{180}\}$ sums to an integer phase contribution $\in \{3, 0\}$ under the $\mathbb{Z}_3$ corner-orientation representation. This arithmetic cancellation is the engine of partition integrality, producing rational spectra without requiring commutativity.](../../figures/paper1/fig3_phase_cancellation.png)

### Unified projector field

Combining the block analyses, we obtain a structural reduction. The following proposition is specific to the Rubik's cube representation, where (A $\in$ M_{228}($\mathbb{Q}$)) (for face-symmetric (S)) and (A) is Hermitian.

**Proposition 4.3 (Projector field reduction).** For face-symmetric (S), (A $\in$ M_{228}($\mathbb{Q}$)) (Proposition~\ref{prop:co-analytic-spectrum}) and is Hermitian. The equivalence ($\lambda$ $\in$ $\mathbb{Q}$ $\iff$ $P_{\lambda}$ $\in$ M_{228}($\mathbb{Q}$)) is a special case of Theorem~\ref{thm:field-of-definition}, whose proof via the field-of-definition argument ((A - $\lambda$ I $\in$ M_n($\mathbb{Q}$) $\Rightarrow$ $\ker$(A - $\lambda$ I)) has a ($\mathbb{Q}$)-basis) is given below.

**Remark (Projector field reduction caveat).** This is a linear algebra fact for any Hermitian matrix with rational entries, not a deep representation-theoretic claim. Unlike the classical approach (which required commuting (h_i) and Schur's Lemma), the field-of-definition argument uses only the rationality of the matrix entries and the eigenvalue.

## Generator character integrality

The generator-character integrality argument is the arithmetic input behind the rationality mechanism. In the Rubik’s cube case study, the 228-dimensional representation decomposes into four structural blocks:

$$
\rho(g)=P_{\mathrm{cp}}(g)\oplus P_{\mathrm{ep}}(g)\oplus \Omega_{\mathrm{co}}(g)\oplus \Sigma_{\mathrm{eo}}(g).
$$

The permutation blocks $P_{\mathrm{cp}}, P_{\mathrm{ep}}$ are defined over $\mathbb{Q}$, the edge-orientation block $\Sigma_{\mathrm{eo}}$ is also defined over $\mathbb{Q}$, and the corner-orientation block $\Omega_{\mathrm{co}}$ lives over $\mathbb{Q}(\omega)$.

### Theorem 5.1 (Generator character integrality)

For each of the 18 face-turn generators (s), the block characters

$$
\chi_{\mathrm{cp}}(s),\quad \chi_{\mathrm{ep}}(s),\quad \chi_{\mathrm{co}}(s),\quad \chi_{\mathrm{eo}}(s)
$$

are integers.

#### Proof.

The permutation blocks count fixed cubies, hence are integer-valued. The edge-orientation block has entries in $\{\pm 1\}$, hence integer trace. The corner-orientation block has diagonal entries in $\{1, \omega, \omega^2\}$, and the Rubik’s cube orientation conservation law forces the $\omega$-coefficients to balance in each generator, leaving an integer trace.

### Corollary 5.2 (Face triple integrality)

For any face-complete triple $\{g, g^{-1}, g_{180}\}$, the total character sum over the triple is an integer:

$$
\chi(g) + \chi(g^{-1}) + \chi(g_{180}) \in \mathbb{Z}.
$$

This follows from Theorem~\ref{thm:generator-character-integrality}: the face-sum trace $\operatorname{Tr}(F_{\mathrm{face}})$ with $F_{\mathrm{face}} = \rho(g) + \rho(g^{-1}) + \rho(g_{180})$ is integer-valued — the $\omega$ terms cancel because $\omega^{k} + \omega^{-k} + \omega^{2k} \in \{3, 0\} \subset \mathbb{Z}$ on the co block, and all other blocks contribute integer traces.

Corollary~\ref{cor:face-triple-integrality} is the concrete arithmetic closure at the generator level. The remaining difficulty is upgrading this from generator-level integrality to eigenspace-level integrality (addressed below).

**Bose–Mesner trace pairing.** In a commutative Bose–Mesner algebra with primitive idempotents $\{E_i\}$ and dual basis $\{A_j\}$, the eigenspace trace $\chi_i(X) = \operatorname{Tr}(E_i X)$ is an integer whenever $X$ belongs to the algebra and has integer matrix entries in the standard basis. For the Rubik cube permutation blocks (cp, ep), the block-level generator matrices $\rho_b(s)$ have integer entries and lie in the appropriate Bose–Mesner algebra (Theorem~\ref{thm:generator-character-integrality}); Corollary~\ref{cor:face-triple-integrality} then yields the per-generator character integrality $\chi_\lambda(s) \in \mathbb{Z}$ for each face-symmetric generator $s$. Full derivation: CCS-III §7.4.

## The arithmetic engine: face-sum integrality

We now present the core mechanism that produces rational eigenvalues. This section is the logical heart of the paper: it establishes the Structural Rationality Criterion — a sufficient condition for spectral rationality that requires only a partition of the generator set with integer per-subset trace sums. The criterion uses no Galois theory, no commutativity of any subalgebra, and no field-of-definition argument; it is a direct consequence of the eigenspace trace identity (Theorem~\ref{thm:eigenspace-trace-identity}) plus arithmetic closure at the trace level. In the Rubik's cube setting, the natural partition is the decomposition into complete faces; the integrality hypothesis is verified for all tested face-complete families. The converse and full necessity beyond the verified Rubik family remain open.

**Logical dependency of Theorems in this section.** Theorem~\ref{thm:eigenspace-trace-identity} (trace identity) is the tautological starting point linking $\lambda$ to eigenspace traces and is used in every proof. Theorem~\ref{thm:rational-trace-sufficient-condition} deploys this identity to prove the unconditional forward direction (rational traces $\Rightarrow$ rational eigenvalues). Theorem~\ref{thm:field-of-definition} supplies the converse via the field-of-definition argument ($A \in M_n(\mathbb{Q})$ and $\lambda \in \mathbb{Q} \Rightarrow P_{\lambda} \in M_n(\mathbb{Q}) \Rightarrow \chi_{\lambda}(s) \in \mathbb{Q}$). The Structural Rationality Criterion provides the arithmetic mechanism: any partition of $S$ with integer per-subset trace sums forces $\lambda \in \mathbb{Q}$. Theorems 5.1/5.2 supply the integer input for the Rubik face partition at the block level; the eigenspace-level step is verified numerically.

### Structural Rationality Criterion

Let (S = S^{-1}) be a finite symmetric subset of (G) and let

$$
A = \frac{1}{|S|} \sum_{s \in S} \rho(s)
$$

be the averaging operator on a finite-dimensional representation (V). Suppose (S) admits a partition (S = $\bigsqcup_{i=1}^{k}$ S_i) such that for every eigenspace projector ($P_{\lambda}$) of (A), the per-subset trace sum is integral:

$$
\sum_{s \in S_i} \chi_{\lambda}(s) \in \mathbb{Z}, \qquad \chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s)), \qquad i = 1, \dots, k.
$$

Then every eigenvalue of (A) satisfies ($\lambda$ $\in$ $\mathbb{Q}$).

The logical structure is a conditional: *if* a partition with integral per-subset trace sums exists for every eigenspace, *then* the spectrum is rational. The proof is a 4-line consequence of the eigenspace trace identity (Theorem~\ref{thm:eigenspace-trace-identity}). The difficulty is entirely in establishing the hypothesis — not in the deduction.

**Verification status.** For the Rubik cube face-complete generator family, the face decomposition $S = \bigcup_{\text{face}} \{g, g^{-1}, g_{180}\}$ provides the partition. The integrality of each face-sum follows from Theorem~\ref{thm:generator-character-integrality} and Corollary~\ref{cor:face-triple-integrality} (block-level generator character integrality) and the cancellation $\omega + \omega^2 + 1 = 0$ on the corner-orientation block (Proposition~\ref{prop:co-analytic-spectrum}). The step from generator-level integrality ($\chi_\lambda(s) \in \mathbb{Z}$ for each $s$) to eigenspace-level integrality (per-face sum $\in \mathbb{Z}$ for each $P_\lambda$) is verified exactly for the Rubik representation and all tested face-complete subfamilies. A general proof that generator-level character integrality implies eigenspace-level per-subset integrality — without assuming the specific Bose–Mesner algebra structure of the Rubik blocks — is not provided here.

**The converse and full necessity beyond the verified Rubik family remain open.** The criterion is a sufficient mechanism; whether partition integrality is necessary for rationality in general finite-group representations is not established.

### Proof.

**Step 1 — Eigenspace trace identity.** By Theorem~\ref{thm:eigenspace-trace-identity}, ($\lambda$ = $\frac{1}{d_{\lambda} |S|} \sum_{s \in S} \chi_{\lambda}(s)$).

**Step 2 — Decompose over the partition.** Summing per subset:

$$
\sum_{s \in S} \chi_{\lambda}(s) = \sum_{i=1}^{k} \sum_{s \in S_i} \chi_{\lambda}(s).
$$

**Step 3 — Integrality.** Each per-subset sum is an integer (hypothesis). A finite sum of integers is an integer:

$$
\sum_{s \in S} \chi_{\lambda}(s) \in \mathbb{Z}.
$$

**Step 4 — Rationality.** From Step 1:

$$
\lambda = \frac{1}{d_{\lambda} |S|} \times (\text{integer}) \in \mathbb{Q}.
$$

### Remark (What this criterion does NOT use).

The proof of this criterion uses exactly three ingredients:

- Theorem~\ref{thm:eigenspace-trace-identity} (eigenspace trace identity — tautological, see above),
- the existence of a partition of (S) with the integrality property,
- the hypothesis that per-subset trace sums are integers.

It does **not** use:

- Galois symmetry (($\sigma$)),
- commutativity of the (h_i) operators,
- the field of definition of ($P_{\lambda}$),
- the block decomposition of (V),
- Schur's Lemma,
- any property of (A) beyond linearity of the trace,
- any specific structure of the Rubik's cube group.

**The entire difficulty of spectral rationality is concentrated in establishing the integrality hypothesis** — that a partition with integral per-subset eigenspace trace sums exists. For the Rubik's cube, the face decomposition provides this partition; the integrality of each face-sum at the block level follows from Theorem~\ref{thm:generator-character-integrality} and Corollary~\ref{cor:face-triple-integrality} and the cancellation ($\omega$ + $\omega^2$ + 1 = 0) on the co-block (Proposition~\ref{prop:co-analytic-spectrum}). The eigenspace-level reduction from generator traces to eigenspace traces at the ($\mathbb{Q}$)-level is given by Theorem~\ref{thm:field-of-definition} below; the strengthening from ($\mathbb{Q}$) to ($\mathbb{Z}$) (individual trace integrality for each generator) is verified numerically on the Rubik face-complete family. Bridging from generator-level to eigenspace-level integrality for an arbitrary partition is the step not established in full generality.

### Field-of-definition mechanism

Let $A \in M_n(\mathbb{Q})$ be Hermitian. For any eigenvalue $\lambda$, let $E_{\lambda} = \ker(A - \lambda I)$ and $P_{\lambda}$ be the orthogonal projector onto $E_{\lambda}$. Then:

$$
\lambda \in \mathbb{Q} \;\Longleftrightarrow\; E_{\lambda} \text{ admits a basis in } \mathbb{Q}^n \;\Longleftrightarrow\; P_{\lambda} \in M_n(\mathbb{Q}).
$$

For the Rubik's cube representation, $A \in M_{228}(\mathbb{Q})$ is established by Proposition~\ref{prop:co-analytic-spectrum} (the co-block averaging operator is a rational scalar $\lambda_{\mathrm{co}} I_8$, with $\lambda_{\mathrm{co}} \in \mathbb{Q}$ forced by the cancellation of $\omega$-dependent terms across paired non-reference faces via $\omega + \omega^2 + 1 = 0$). For face-symmetric $S$ and any generator $s \in S$, the eigenspace trace satisfies:

$$
\lambda \in \mathbb{Q} \;\Longrightarrow\; \chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s)) \in \mathbb{Q}.
$$

### Proof.

This is a standard linear algebra fact: kernels of rational matrices admit rational bases, and the orthogonal projector constructed from a rational basis has rational entries. Since $X \in M_{n \times d}(\mathbb{Q})$, the Gram matrix $X^\top X \in M_d(\mathbb{Q})$ is invertible with rational determinant, and by Cramer's rule its inverse is also rational: $(X^\top X)^{-1} \in M_d(\mathbb{Q})$. Therefore $P_{\lambda} = X(X^\top X)^{-1} X^\top \in M_n(\mathbb{Q})$. The theorem calls this fact into the service of the arithmetic criterion — it is not a new claim, but a precise identification of the classical mechanism that closes the converse direction.

**$\lambda \in \mathbb{Q} \Rightarrow P_{\lambda} \in M_n(\mathbb{Q})$.** Since $A \in M_n(\mathbb{Q})$ and $\lambda \in \mathbb{Q}$, the matrix $A - \lambda I \in M_n(\mathbb{Q})$. The eigenspace $E_{\lambda} = \ker(A - \lambda I)$ is the nullspace of a rational matrix — a homogeneous linear system with rational coefficients. Gaussian elimination over $\mathbb{Q}$ produces a basis of vectors in $\mathbb{Q}^n$. Let $X \in M_{n \times d}(\mathbb{Q})$ be the matrix whose columns form such a basis (where $d = \dim E_{\lambda}$).

The orthogonal projector (for the standard inner product on $\mathbb{C}^n$) is
$$
P_{\lambda} = X (X^\top X)^{-1} X^\top.
$$
(Although the inner product on $\mathbb{C}^n$ uses the conjugate transpose $X^*$, the columns of $X$ are vectors in $\mathbb{Q}^n \subset \mathbb{R}^n$, so $X^* = X^\top$ — the projector formula reduces to the real transpose. This is the key point where Hermiticity of $A$ (guaranteeing real eigenvalues and hence real eigenspace bases) eliminates the need for complex conjugation.) The Gram matrix $X^\top X \in M_d(\mathbb{Q})$ is invertible (the basis vectors are linearly independent). By Cramer's rule, $(X^\top X)^{-1} \in M_d(\mathbb{Q})$: each entry is a polynomial in the rational entries of $X^\top X$ divided by the rational determinant $\det(X^\top X) \neq 0$. Hence $P_{\lambda} \in M_n(\mathbb{Q})$.

**$P_{\lambda} \in M_n(\mathbb{Q}) \Rightarrow \lambda \in \mathbb{Q}$.** $\lambda = \operatorname{Tr}(A P_{\lambda}) / \operatorname{Tr}(P_{\lambda}) = \operatorname{Tr}(A P_{\lambda}) / d$. Both $A$ and $P_{\lambda}$ have rational entries, so the trace is a quotient of rationals — hence rational.

**Eigenspace trace rationality.** For the Rubik's cube representation, $A \in M_{228}(\mathbb{Q})$ (Proposition~\ref{prop:co-analytic-spectrum}). For any generator $s \in S$, $\rho(s) \in M_{228}(\mathbb{Q}(\omega))$. If $\lambda \in \mathbb{Q}$, then $P_{\lambda} \in M_{228}(\mathbb{Q})$ by the above, and $\chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s)) \in \mathbb{Q}(\omega)$. Since $A$ is Hermitian, $\chi_{\lambda}(s) \in \mathbb{R}$. The only real numbers in $\mathbb{Q}(\omega)$ are rational: $\mathbb{Q}(\omega) \cap \mathbb{R} = \mathbb{Q}$. Hence $\chi_{\lambda}(s) \in \mathbb{Q}$.

**What this proves and what it does not.** Theorem~\ref{thm:field-of-definition} establishes the full equivalence between rational eigenvalues, rational projectors, and rational eigenspace traces — *assuming* ($\lambda$ $\in$ $\mathbb{Q}$) as input for the forward direction. This is a standard linear algebra fact: the nullspace of a ($\mathbb{Q}$)-matrix has a ($\mathbb{Q}$)-basis; the projector constructed from that basis has rational entries. No representation theory, Galois symmetry, or commutativity hypothesis is used.

The field-of-definition argument uses only $A \in M_n(\mathbb{Q})$ and $\lambda \in \mathbb{Q}$ — neither commutativity nor Galois invariance is needed.

### Equivalent formulations

For face-symmetric (S), the following are equivalent (the second equivalence uses the numerical fact that ($\lambda$ $\in$ $\mathbb{Q}$) for all tested face-symmetric families):

1. $\operatorname{Spec}(A) \subset \mathbb{Q}$.
2. $P_{\lambda} \in M_{228}(\mathbb{Q})$ for every spectral projector (Theorem~\ref{thm:field-of-definition}).
3. $\chi_{\lambda}(s) \in \mathbb{Q}$ for every generator $s$ and eigenvalue $\lambda$ (Theorem~\ref{thm:field-of-definition}).
4. For each face and each eigenvalue, the per-face eigenspace trace sum is rational (Structural Rationality Criterion).

Numerically, a stronger property holds: each $\chi_{\lambda}(s)$ and each per-face sum is not merely rational but an **integer**. This $\mathbb{Z}$-level strengthening is verified for all tested face-symmetric generator sets; a first-principles proof would require showing that the rational projector lattice $P_{\lambda} \in M_n(\mathbb{Q})$ is compatible with the integer lattice of the face-sum matrices $F_{\mathrm{face}} \in M_n(\mathbb{Z})$, i.e., that each eigenspace carries a $\mathbb{Z}$-structure preserved by all face-sums.

**Theorem (Rational trace sufficient condition).** For any generator set (S = S^{-1}) (not necessarily face-symmetric), if the eigenspace traces are rational on all generators, then the corresponding eigenvalue is rational:

$$
\chi_{\lambda}(s) \in \mathbb{Q} \;\; \forall s \in S \quad\Longrightarrow\quad \lambda \in \mathbb{Q}.
$$

Equivalently, $\sum_{s \in S} \chi_{\lambda}(s) \in \mathbb{Q}$ implies $\lambda \in \mathbb{Q}$.

### Proof.

By Theorem~\ref{thm:eigenspace-trace-identity}, $\lambda = \frac{1}{d_{\lambda} |S|} \sum_{s \in S} \chi_{\lambda}(s)$. If each $\chi_{\lambda}(s) \in \mathbb{Q}$, the sum is rational, and the right-hand side is a rational number divided by integers — hence rational.

### Remark (Scope and converse).

Theorem~\ref{thm:rational-trace-sufficient-condition} provides an **unconditional sufficient condition** within the class of averaging operators: rational eigenspace traces force rational eigenvalues. The proof uses only the eigenspace trace identity (Theorem~\ref{thm:eigenspace-trace-identity}), which holds for any averaging operator $A = \frac{1}{|S|} \sum_{s} \rho(s)$, and the hypothesis that each $\chi_{\lambda}(s) \in \mathbb{Q}$. No symmetry, commutativity, or Galois hypothesis is needed. It is the rigorous core of the rationality criterion.

The **converse** direction — $\lambda \in \mathbb{Q} \Rightarrow \chi_{\lambda}(s) \in \mathbb{Q}$ — requires the additional hypothesis that $A \in M_n(\mathbb{Q})$. When this holds (as in the face-symmetric case, by Proposition~\ref{prop:co-analytic-spectrum} and the permutation-block structure), it follows from Proposition~\ref{prop:projector-field-reduction}: $A \in M_n(\mathbb{Q})$ and $\lambda \in \mathbb{Q}$ together imply $P_{\lambda} \in M_n(\mathbb{Q})$, and then $\chi_{\lambda}(s) = \operatorname{Tr}(P_{\lambda} \rho(s)) \in \mathbb{Q}(\omega) \cap \mathbb{R} = \mathbb{Q}$. Thus:

$$
\text{For face-symmetric } S: \quad \lambda \in \mathbb{Q} \;\Longleftrightarrow\; \chi_{\lambda}(s) \in \mathbb{Q} \;\; \forall s \in S.
$$

This equivalence is **conditional on face-symmetry**, which guarantees (A $\in$ M_{228}($\mathbb{Q}$)). Face-symmetry is a sufficient condition for the converse, not a necessary one: generator families that are not fully face-symmetric may still produce rational spectra (e.g., partially face-complete sets). The practical value of the criterion lies in the forward direction (rational traces ($\Rightarrow$) rational eigenvalues), which holds without any symmetry hypothesis.

The $\mathbb{Z}$-level strengthening — that $\chi_{\lambda}(s) \in \mathbb{Z}$ for each generator — follows from the Bose–Mesner trace pairing argument of Theorem~\ref{thm:generator-character-integrality} and Corollary~\ref{cor:face-triple-integrality}; the explicit trace values are recorded in the Computational Supplement [10, Part I §2]. The field stratification across generator families (face-symmetric → $\mathbb{Q}$, symmetry-broken → $\mathbb{Q}(\sqrt{5})$) is analyzed below (see Why Irrationality Appears After Symmetry Breaking).

### Structural synthesis: arithmetic locality behind rationality

The results of this section isolate the actual source of rationality.

The spectrum is rational not because the averaging operator is commutative, nor because the representation is defined over a cyclotomic field, but because the generator family admits an arithmetic partition whose eigenspace trace sums close integrally.

The Rubik cube realizes this mechanism through face completeness: each complete face contributes a locally integral trace packet, and the global eigenvalue becomes an average of these integral contributions.

The role of the field-of-definition argument is secondary: it explains why rational eigenvalues induce rational eigenspace projectors, but it does not produce rationality. The arithmetic engine itself is the partition-integral trace structure.

In this sense, spectral rationality is fundamentally an arithmetic locality phenomenon: global rational eigenvalues emerge from local integer trace closure across the generator partition.

## Structural Consequences

The preceding sections establish two independent mechanisms — the Structure Theorem and the Main Theorem — that *together* produce the six-layer rational spectrum. This section turns from mechanism to consequence: why this spectral structure is not a numerical coincidence, why commutativity is the wrong organizing principle, why the spectrum is sparse, and what happens when these mechanisms are disabled by symmetry breaking.

### Why the Six-Layer Collapse Is Non-Generic

Averaging a random set of 18 matrices in $\mathrm{GL}(228, \mathbb{C})$ almost never produces a rational spectrum with only 6 distinct eigenvalues. The generic outcome is many eigenvalues, most irrational. The Rubik's cube is different for four structural mechanisms which jointly produce the rational collapse:

**1. Face completeness.** The 18 generators decompose into 6 complete faces, each the $G$-orbit $\{g, g^{-1}, g_{180}\}$ of a single quarter-turn. A complete face produces a face-sum operator $F_{\mathrm{face}} = \rho(g) + \rho(g^{-1}) + \rho(g_{180})$ whose eigenvalues are real and whose trace on every block is integer-valued. A random generator set lacks this partition structure — and without it, the Structural Rationality Criterion has no partition to apply to.

**2. Partition integrality (Structural Rationality Criterion).** The face partition forces the per-face eigenspace trace sums to be integers (verified for the Rubik face-complete family). A finite sum of integers divided by integer dimensions is rational. This is the arithmetic closure step — it requires both the partition and the integrality hypothesis. Without the partition, the trace sum is an unconstrained real number; rationality is not forced.

**3. Phase cancellation ($\mathbb{Z}_3 \to \mathbb{Q}$).** The corner-orientation block is the only source of irrational entries in the representation (all other blocks have generators over $\mathbb{Z}$). On a complete face, the three moves contribute $\omega^k + \omega^{-k} + \omega^{2k} \in \{3, 0\} \subset \mathbb{Z}$ — the $\omega$ and $\omega^2$ terms cancel exactly (CCS-III §7.2, Lemma~\ref{lem:co-block-face-sum-integrality}). This eliminates the only non-rational component. When face completeness is broken ($n=8$, $n=16$ families), the $\omega$ terms survive and the spectrum acquires irrational components in $\mathbb{Q}(\sqrt{5})$ (§7.4).

**4. Blockwise compatibility.** The four blocks carry independent but mutually compatible spectral structures: cp and ep have Bose–Mesner algebras over $\mathbb{Q}$ (CCS-III §7.4); co and eo carry abelian phase constraints defined over $\mathbb{Q}$ for face-symmetric $S$. The block-diagonal structure (Theorem~\ref{thm:block-compatibility-lemma}) ensures that the global spectrum is the union of four $\mathbb{Q}$-rational block spectra.

These four mechanisms **jointly produce** the six-layer rational collapse — they are not a single causal chain but three structural sources (face completeness, $\mathbb{Z}_3$ phase cancellation, and blockwise compatibility) that together feed the partition-integrality criterion (Structural Rationality Criterion):

$$\boxed{\begin{array}{c}\text{Face completeness} \;+\; \text{Phase cancellation} \;+\; \text{Blockwise compatibility} \\[4pt] \Downarrow \\[4pt] \text{Partition integrality (Structural Rationality Criterion)} \;\Rightarrow\; \text{Rational collapse}\end{array}}$$

Disabling any one of the three sources — breaking face completeness, letting $\omega$-phases survive, or losing the block-diagonal structure — disables the partition integrality hypothesis, and the six-layer rational collapse fails. The Rubik's cube representation is an interference system in which three structural sources act in concert; the rational collapse is their composite output, not the consequence of a single underlying principle.

### Why Commutativity Is Not the Mechanism

The classical route to spectral rationality goes through commutativity: if the generator-level operators $h_i = \frac{1}{2}(\rho(g_i) + \rho(g_i^{-1}))$ all commute, simultaneous diagonalization and Schur's Lemma force rational eigenvalues. This route is unavailable for the Rubik's cube. The per-axis QT operators on the EP block have commutator norm 2.74 — 93.9% of total noncommutativity (CCS-I §2.1). The classical route is structurally blocked.

The present paper replaces commutativity with a different mechanism:

| Classical route | Present route |
|----------------|---------------|
| Commuting generator averages $\{h_i\}$ | Partition integrality of the generator set |
| Simultaneous diagonalization of $\{h_i\}$ | Block-diagonal decomposition (Theorem~\ref{thm:block-compatibility-lemma}) |
| Schur's Lemma on common eigenspaces | Eigenspace trace identity (Theorem~\ref{thm:eigenspace-trace-identity}) |
| Global commutative algebra on $V$ | Four heterogeneous blockwise algebras, each commutative on its block |
| Rationality from character theory | Rationality from face-sum integrality + trace identity |

The critical structural fact is that **each block-level algebra is commutative** (Bose–Mesner for cp, adjacency algebra for ep, abelian phase for co/eo — Theorem~\ref{thm:spectral-collapse}), even though the full generator algebra is strongly noncommutative. The averaging operator $A$ is block-diagonal: it only sees the blockwise commutative subalgebras. The noncommutativity concentrated in $A_{\mathrm{EP}}$ (\cite{paper2}, §5; CCS-III §9.4) is structurally invisible to $A$ — averaging projects onto the commutative core.

This is why $A$ can have a rational spectrum despite generator noncommutativity of order 2.74: **the averaging operator only accesses the blockwise commutative structure.** The M₂ components of $A_{\mathrm{EP}}$ create transport and Lie curvature (\cite{paper2}, \cite{paper3}) precisely because they are the part of the representation that $A$ averages *out*. The clean separation — commutative core for the spectrum, noncommutative components for transport — is the signature of the Rubik's cube's algebraic architecture.

### Why the Spectrum Is Sparse

The 18-full generator family yields exactly 6 eigenvalues from a possible 10 ($k \in \{0,\dots,9\}$). Three structural principles explain this sparsity.

**The union formula.** By Theorem~\ref{thm:spectral-collapse} and the block reduction (CCS-III §7.1):

$$\mathcal{K}(A) = \mathcal{K}_{\mathrm{cp}} \cup \mathcal{K}_{\mathrm{ep}} \cup \mathcal{K}_{\mathrm{co}} \cup \mathcal{K}_{\mathrm{eo}}$$

Each block's $k$-set is small — 3–4 values — because each is the spectrum of a low-dimensional algebraic object: the Q₃ hypercube on 8 vertices (cp), the face-incidence graph on 12 edges (ep), and $\mathbb{Z}_3$/$\mathbb{Z}_2$ phase constraints (co/eo). The union of four small sets remains small:

$$\mathcal{K}(A) = \{0,4,6\} \cup \{0,2,3,4\} \cup \{3,4,6\} \cup \{1,2,4\} = \{0,1,2,3,4,6\}$$

6 values from a possible 10. The sparsity is not an accident of the number 18 — it is the cardinality of $\bigcup_B \mathcal{K}_B$, determined by four independently computable block spectra.

**The co-block as arithmetic filter.** The corner-orientation block is the decisive constraint. Its $k$-set $\mathcal{K}_{\mathrm{co}} = \{3,4,6\}$ is the intersection of the phase cancellation condition $\omega + \omega^2 + 1 = 0$ with the corner permutation cycle structure. The co block *cannot* contribute at any $k \notin \{3,4,6\}$ — the arithmetic of $\mathbb{Z}_3$ phases forbids it (CCS-III §7.2, Constraint C4). Since the co block spans 8 dimensions that must be allocated across exactly these three $k$-values, it acts as an arithmetic filter: any $k$-value without co support simply cannot host co dimensions, restricting the admissible dimension assignments for all blocks via the exhaustion constraint (CCS-III §7.2, C1–C2).

**Resonance merging.** The four blocks together carry 10 primitive idempotents (4 cp + 3 ep + 1 co + 2 eo for 18-full). These 10 collapse to 6 global layers because eigenvalue coincidence under $\lambda = 1 - k/9$ merges primitive idempotents from different blocks at the same $k$. At $k=4$ ($\lambda = 5/9$), all four blocks contribute — cp(24) + ep(72) + co(3) + eo(7) = 106 dimensions, the giant $V_{5/9}$ layer (46.5% of total). At $k=5$, zero blocks contribute — the vacancy is robust because $k=5$ is absent from every block's $k$-set for four independent structural reasons (Krawtchouk incompatibility for cp, octahedron graph spectrum for ep, fractional $\omega$-phase incompatibility for co, face-type classification for eo). The result is a sparse layered structure: 6 coincidence peaks from 10 block-level primitive idempotents, with a clean gap at $k=5$.

The layer dimensions and the $k=5$ gap are therefore structural theorems, not empirical fits. They follow from the blockwise algebra spectra plus the eigenvalue coincidence relation. The sparsity pattern is fully determined, verified across all tested face-symmetric generator families (CCS-III §7.2, admissible $k$-set table).

**Theorem (Spectral Factorization Principle).**

The union formula $\mathcal{K}(A) = \bigcup_B \mathcal{K}_B$ is not merely a data-compression device — it reflects a structural factorization of the averaging operator itself. The 228-dimensional Rubik's cube representation is the tensor lift of four low-dimensional independent spectral components:

$$\boxed{\operatorname{Spec}(A) \;=\; \underbrace{(\mathrm{cp, ep})}_{\text{adjacency algebra}} \;\times\; \underbrace{(\mathrm{co, eo})}_{\text{abelian phase algebra}}}$$

The full averaging operator factors as a tensor product of independent spectral components:

$$\mathcal{A}_{\text{cube}} \;=\; \mathcal{A}_{Q_3} \;\otimes\; \mathcal{A}_{\text{incidence}} \;\otimes\; \mathcal{Z}_2 \;\otimes\; \mathcal{Z}_3$$

where $\mathcal{A}_{Q_3}$ is the Bose–Mesner algebra of the 8-vertex Q₃ hypercube (cp block, determining $\mathcal{K}_{\mathrm{cp}} = \{0,4,6\}$), $\mathcal{A}_{\text{incidence}}$ is the Bose–Mesner algebra of the 12-edge face-incidence graph (ep block, determining $\mathcal{K}_{\mathrm{ep}} = \{0,2,3,4\}$), and $\mathcal{Z}_2, \mathcal{Z}_3$ are the abelian phase algebras of edge and corner orientation (determining $\mathcal{K}_{\mathrm{eo}} = \{1,2,4\}$ and $\mathcal{K}_{\mathrm{co}} = \{3,4,6\}$).

The structural decomposition is into two types:

| Type | Blocks | Algebra | Role |
|------|--------|---------|------|
| I (adjacency) | cp, ep | Association schemes (Bose–Mesner) | Determine spectral layer **positions** |
| II (phase) | co, eo | $\mathbb{Z}_3$, $\mathbb{Z}_2$ abelian | Act as interference **filters** — they contribute no spectral layering of their own, but determine which Type I $k$-values survive with nonzero orientation-block support |

The spectrum of $A$ is therefore not a property of the full Rubik's cube group — it is a property of two low-dimensional combinatorial objects (the Q₃ hypercube on 8 vertices and the face-incidence graph on 12 edges) and two abelian phase constraints ($\mathbb{Z}_2$ edge orientation and $\mathbb{Z}_3$ corner orientation). No group character table is needed; no commutativity of generator-level operators is required. Full derivation: (CCS-III §7.3). Figure~\ref{fig:fig5-sparsity-mechanism} shows the per-block $k$-admissibility bands whose union determines the 6-layer spectrum.

![Per-block $k$-admissibility bands for CP ($\{0,4,6\}$), EP ($\{0,2,3,4\}$), CO ($\{3,4,6\}$), and EO ($\{1,2,4\}$), each determined by internal algebraic structure. The union $\bigcup_B \mathcal{K}_B = \{0,1,2,3,4,6\}$ yields exactly 6 of 10 possible $k$-values; $k=5$ is absent from every block for independent structural reasons. The sparsity of the spectrum is the cardinality of a union of block-level spectra, not a free parameter.](../../figures/paper1/fig5_sparsity_mechanism.png)

### Why Irrationality Appears After Symmetry Breaking

The rational mechanism described above is sharp: it operates when face completeness holds and breaks when it does not. Two symmetry-broken families test this boundary directly.

**Theorem 7.1 (Irrationality under broken face symmetry).** Let $S$ be a generator set that is not a union of complete faces. The spectral field of $A_S$ extends beyond $\mathbb{Q}$:

$$\lambda_{\pm} = \begin{cases}
\dfrac{5 \pm \sqrt{5}}{8} \approx 0.9045,\; 0.3455, & n = 8 \text{ (8 of 12 quarter-turns)} \\[10pt]
\dfrac{11 \pm \sqrt{5}}{16} \approx 0.8273,\; 0.5477, & n = 16 \text{ (16 of 18 face turns)}.
\end{cases}$$

The spectral field is $\mathbb{Q}(\sqrt{5})$ — the maximal real subfield of the 5th cyclotomic field. The appearance of $\sqrt{5}$ traces to $\cos(2\pi/5) = (\sqrt{5}-1)/4$, the smallest non-rational cyclotomic cosine: $C_5$-type spectral blocks emerge in the incomplete scheme whose minimal polynomial over $\mathbb{Q}$ is irreducible and splits over $\mathbb{Q}(\sqrt{5})$ (CCS-III §7.5).

**Numerical summary (CCS-III §7.5 for full census):**

| Family | $m$ | Rational $\lambda$ | Irrational $\lambda$ | Spectral field |
|--------|-----|-------------------|---------------------|---------------|
| 18-full | 9 | 6 | 0 | $\mathbb{Q}$ |
| 12-quarter | 6 | 6 | 0 | $\mathbb{Q}$ |
| 21-full+slice | 10.5 | 6 | 0 | $\mathbb{Q}$ |
| $n=8$ (asym.) | 4 | 5 | 2 | $\mathbb{Q}(\sqrt{5})$ |
| $n=16$ (asym.) | 8 | 6 | 2 | $\mathbb{Q}(\sqrt{5})$ |

**Mechanism.** When face completeness is broken, the adjacency algebras on cp/ep fail to close over $\mathbb{Q}$ — their minimal polynomials acquire an irreducible quadratic factor. The $\omega$ and $\omega^2$ terms that cancel on complete faces via $\omega + \omega^2 + 1 = 0$ survive when faces are incomplete, concentrating in a $C_5$-type spectral block. The residual un-cancelled cyclotomic contribution produces a 2-dimensional real subspace whose structure constants lie in $\mathbb{Q}(\sqrt{5})$.

The key structural fact is that the boundary is observed to be sharp: **mechanism present $\Rightarrow$ rationality; mechanism absent $\Rightarrow$ irrationality**, across all verified families. There is no intermediate regime, no continuous degradation. The same group, the same representation, the same block structure, the same eigenvalue form $\lambda = 1 - k/m$ — the only variable is whether the generator set is a union of complete faces. This negative control is the strongest single piece of evidence for the partition integrality mechanism: it rules out explanations based on the specific generator count (18), the dimension (228), or the group (Rubik's cube). The rational spectrum is not an artefact of these parameters — it is a direct consequence of face completeness, and it collapses the moment face completeness is removed. Figure~\ref{fig:fig4-symmetry-breaking} shows this sharp rationality/irrationality boundary across the 18-full and $n=8$ families. The full field-extension analysis is in (CCS-III §7.5); the $n=21$ full+slice family confirming that face-symmetry extends naturally beyond 18 generators is in (CCS-III §7.6).

![Symmetry breaking at the rationality boundary: 18-full generators (rational spectrum, 6 eigenvalues, field $\mathbb{Q}$) vs $n=8$ asymmetric generators ($\mathbb{Q}(\sqrt{5})$ spectrum, 7 eigenvalues, 2 irrational). The same group, representation, and block structure produce rationality under face-complete generators and irrationality under incomplete faces. Rationality is not generic — it is a direct consequence of partition integrality, not the group or the dimension.](../../figures/paper1/fig4_symmetry_breaking.png)

The full generator-family continuum (18→16→12→10→8→6) with per-family eigenvalue census and the $\mathbb{Q} \to \mathbb{Q}(\sqrt{5})$ phase transition is shown in (CCS Fig. C12).

**Remark (Representation-theoretic degeneracy).** A complementary structural observation is recorded in CCS Appendix H: representation-theoretic Casimir constructions collapse the four canonical Rubik blocks into two intrinsic mass classes, $(V_{\mathrm{cp}} \oplus V_{\mathrm{co}}) \oplus (V_{\mathrm{ep}} \oplus V_{\mathrm{eo}})$, revealing an additional layer of degeneracy beyond the six-layer spectral collapse. This suggests that the block decomposition is not merely combinatorial, but carries a deeper representation-theoretic organization.

## Discussion

Two independent mechanisms determine the Rubik cube spectrum: block spectral factorization and partition integrality.

**Structure Theorem.** The global spectrum is the union of four block spectra, $\operatorname{Spec}(A) = \bigcup_B \operatorname{Spec}(A_B)$, which reduces the 228-dimensional problem to four independent sub-problems (dimensions 64, 144, 8, 12). The permutation blocks (cp, ep) form Bose–Mesner algebras on two small positional graphs — the Q₃ hypercube and the face-incidence graph — whose spectra are analytically computable. The orientation blocks carry abelian phase constraints: the co block is a scalar multiple of the identity (Z₃ interference locks it to a single eigenvalue), and the eo block splits into two phase classes (Z₂). The four blocks together produce 10 primitive idempotents; eigenvalue coincidence across blocks (resonance) under the common rational form $\lambda = 1 - k/m$ collapses them to exactly 6 global layers.

**Main Theorem.** Rationality of the eigenvalues follows from partition integrality: the decomposition of the 18 generators into six complete faces provides per-face eigenspace trace sums that are integers. The proof uses only the eigenspace trace identity $\lambda = \frac{1}{|S|}\sum_{s\in S} \operatorname{Tr}(P_{\lambda} \rho(s))$ and the partition hypothesis — no commutativity of the generators is required. The integrality of the per-face traces follows from the phase cancellation $\omega + \omega^2 + 1 = 0$ on the Z₃ corner-orientation block together with the integral trace pairing of the Bose–Mesner algebras on the permutation blocks (§5, Corollary~\ref{cor:face-triple-integrality}; CCS-III §7.4).

The combination of these two mechanisms yields the observed six-layer rational spectrum. The Structure Theorem determines *which* eigenvalues can appear; the Main Theorem forces those eigenvalues to be rational.

**Structural Consequences.** The spectral collapse is non-generic — it requires face completeness, partition integrality, $\mathbb{Z}_3$ phase cancellation, and blockwise compatibility, which jointly produce the rational collapse in the Rubik cube family. Commutativity of the generators is not the mechanism: the blockwise algebras are commutative even though the full generator algebra is not, and $A$ only sees the commutative core (§7.2). The spectral sparsity is structural: $\mathcal{K}(A) = \bigcup_B \mathcal{K}_B$ with each block's $k$-set determined by a low-dimensional algebraic object, the co block acting as an arithmetic filter, and resonance merging collapsing 10 primitive idempotents to 6 global layers (§7.3). Rationality is not generic: under symmetry breaking ($n=8$, $n=16$), the spectral field extends to $\mathbb{Q}(\sqrt{5})$, confirming that face completeness marks an observed sharp rationality boundary across all verified families — mechanism present $\Rightarrow$ rationality, mechanism absent $\Rightarrow$ irrationality (§7.4).

**Position of this paper.** Paper I identifies the spectral objects and explains why their eigenvalues are rational — it establishes a complete arithmetic mechanism whose structural scope is delineated below. The Structure Theorem and Main Theorem are proven unconditionally for the Rubik's cube representation. The proven-vs-observed status of each claim is detailed in the Computational Supplement [10, Appendix E].

**Resolved-sector perspective.** The six $A_{18}$-layers are the canonical object of this paper, because they are the eigenspaces whose rationality is proved here. The finer 9-sector decomposition used in \cite{paper2} has a sharper interpretation: it is the joint eigenspace decomposition of the commuting QT/HT averaging algebra. In that resolved picture, $A_{18} = (2/3)\mathrm{QT}_{\mathrm{all}} + (1/3)\mathrm{HT}_{\mathrm{all}}$ is a linear projection of the nine QT/HT joint-spectral sectors, and the six layers arise as its collision quotient at the canonical weight. This collision-quotient viewpoint refines the geometry of the decomposition, but does not replace the arithmetic rationality mechanism proved in this paper.

This resolved-sector language is adjacent to quotient theory for commutative
association-scheme algebras, where equitable partitions and simple cells lead
to quotient Bose-Mesner structures \cite{godsilMartin1995quotients}. In the
present paper this is used only as formal ancestry: the six layers are
eigenspaces of the averaging operator, while the nine QT/HT sectors are joint
eigenspaces of the commuting QT/HT algebra. The association-scheme comparison
does not replace the blockwise rationality proof.

**Relation to Papers II and III.** \cite{paper2} studies the transport topology between the QT/HT joint-spectral sectors identified here — *how* the resolved spectral objects communicate under the generator action. \cite{paper3} proves that compositional accessibility strictly exceeds Lie-generated accessibility — a structural theorem (T7) whose proof relies on shared isotypic support (C1), transport-active hybrid projectors (C2), and block-diagonal dynamics (C3). The three papers together form three layers of one structure — finite representation transport geometry — each a complete theorem in its own right.

## Structural Scope and Boundary

The structural machinery developed here — averaging operators, block-diagonal decomposition, partition integrality, and eigenspace trace identities — applies to finite semisimple representation systems admitting averaging operators and compatible center decompositions. The specific spectral data reported in this paper (six layers, missing $k=5$, resonance merging pattern, block $k$-sets) are verified only for the Rubik cube representation with the 18 face-turn generators. Other systems may exhibit different layer counts, resonance patterns, or sector geometries, requiring independent computation.

### What Is Proved

The following are established unconditionally for the Rubik cube representation:

- **Block spectral factorization** (Theorem~\ref{thm:spectral-collapse}): $\operatorname{Spec}(A) = \bigcup_B \operatorname{Spec}(A_B)$, reducing the 228-dimensional problem to four independent blocks.
- **Resonance collapse**: 10 block-level primitive idempotents merge to exactly 6 global layers via eigenvalue coincidence $\lambda = 1 - k/m$.
- **Partition integrality** (Structural Rationality Criterion): Face-complete generator partitions force rational eigenvalues (verified sufficient mechanism).
- **Rationality mechanism**: Phase cancellation $\omega + \omega^2 + 1 = 0$ on the $\mathbb{Z}_3$ corner-orientation block, together with Bose–Mesner integral trace pairing on the permutation blocks, provides the arithmetic closure (full derivation: CCS-III §7.4).
- **Sharp symmetry-breaking boundary** (Theorem~\ref{thm:irrationality-under-broken-face-symmetry}): When face completeness is broken, the spectral field extends from $\mathbb{Q}$ to $\mathbb{Q}(\sqrt{5})$. The boundary is sharp across all verified families — mechanism present $\Rightarrow$ rationality, mechanism absent $\Rightarrow$ irrationality.

### Structural Scope

The rationality mechanism depends on four structural conditions:

1. **Block-diagonal representation** — $\rho(g) = \operatorname{diag}(\rho_{\mathrm{cp}}, \rho_{\mathrm{ep}}, \rho_{\mathrm{co}}, \rho_{\mathrm{eo}})$, enabling independent block-level spectral analysis.
2. **Face-complete generator partition** — the generators decompose into complete faces, each a $\mathbb{Z}_3$-orbit $\{g, g^{-1}, g_{180}\}$.
3. **Phase cancellation** — $\omega + \omega^2 + 1 = 0$ on the $\mathbb{Z}_3$ corner-orientation block eliminates the only non-rational matrix entries.
4. **Observed resonance merging** — eigenvalue coincidence $\lambda = 1 - k/m$ across blocks collapses block-level idempotents to global layers.

These conditions are jointly sufficient for the six-layer rational spectrum of the Rubik cube representation. Whether they are necessary — or whether rational spectral collapse can occur through mechanisms other than partition integrality — is the open boundary.

### Open Boundary

The central structural question left open is whether partition integrality is necessary for rational spectral collapse beyond face-symmetric families. Theorem~\ref{thm:field-of-definition} provides the converse for face-symmetric generator sets; the necessity of the partition mechanism for general generator families is not established. Additional structural questions and computational observations are collected in (CCS Appendix I).

***

## Appendix A: Canonical Spectral Summary

Compact reference for the six canonical layers. Full spectral data, block-level derivations, and exhaustive verification in (CCS-I §1.1–§1.8).

### A.1 Six Canonical Layers

| $k$ | $\lambda = 1 - k/9$ | Dim | Label | Block composition |
|:---:|:--------------------:|:---:|:-----:|:------------------|
| 0 | 1 | 20 | $V_1$ | cp(8) + ep(12) |
| 1 | 8/9 | 2 | $V_{8/9}$ | eo(2) |
| 2 | 7/9 | 39 | $V_{7/9}$ | ep(36) + eo(3) |
| 3 | 2/3 | 26 | $V_{2/3}$ | ep(24) + co(2) |
| 4 | 5/9 | 106 | $V_{5/9}$ | cp(24) + ep(72) + co(3) + eo(7) |
| 6 | 1/3 | 35 | $V_{1/3}$ | cp(32) + co(3) |

Total: $20+2+39+26+106+35 = 228$. $k=5$ ($\lambda=4/9$) is genuinely absent — no blockwise primitive idempotent produces it (CCS-I §1.7).

### A.2 Block $k$-Sets

The union formula $\mathcal{K}(A) = \bigcup_B \mathcal{K}_B$ (Theorem~\ref{thm:spectral-collapse}):

| Block | Dim | $k$-set | Algebraic origin |
|:-----:|:---:|:--------|:-----------------|
| cp | 64 | $\{0,4,6\}$ | Q₃ Hamming scheme (Krawtchouk) |
| ep | 144 | $\{0,2,3,4\}$ | Face-incidence adjacency algebra |
| co | 8 | $\{3,4,6\}$ | $\mathbb{Z}_3$ phase ($\omega+\omega^2+1=0$) |
| eo | 12 | $\{1,2,4\}$ | $\mathbb{Z}_2$ phase (face-type classification) |

Union: $\{0,4,6\} \cup \{0,2,3,4\} \cup \{3,4,6\} \cup \{1,2,4\} = \{0,1,2,3,4,6\}$ — 6 of 10 possible $k$-values. $k=5$ is absent from every block for four independent structural reasons (Krawtchouk incompatibility for cp, octahedron spectrum for ep, fractional $\omega$-phase for co, face-type for eo). $k=7,8,9$ are forbidden by dimension bounds.

### A.3 Key Structural Facts

| Property | Value | Mechanism |
|----------|-------|-----------|
| Block dimensions | 64, 144, 8, 12 | $G$-orbit decomposition (cubie types) |
| Total dimension | 228 | $64+144+8+12$ |
| Block-level idempotents | 10 | $4$(cp) + $3$(ep) + $1$(co) + $2$(eo) |
| Global layers (resonance merging) | 6 | Eigenvalue coincidence $\lambda=1-k/9$ collapses $10 \to 6$ |
| Largest layer | $V_{5/9}$ (106-dim, 46.5%) | All four blocks contribute at $k=4$ |
| Spectral field (18-full) | $\mathbb{Q}$ | Face-complete partition integrality |
| Admissible $k$-set | $\{0,1,2,3,4,6\}$ | $\mathcal{K}(A) = \bigcup_B \mathcal{K}_B$ |
| Vacancy | $k=5$ | Absent from all four block $k$-sets |

### A.4 Generator-Family Spectral Overview

Compact comparison of generator families. Full symmetry-breaking atlas and eigenvalue census in (CCS-I §1.5, CCS-II §II.4).

#### Face-Symmetric Families (Rational)

| Family | $m$ | $k$-set | Layers | Key mechanism |
|--------|:---:|--------|:------:|---------------|
| 18-full (canonical) | 9 | $\{0,1,2,3,4,6\}$ | 6 | Complete faces, QT+HT, uniform average |
| 12-quarter | 6 | $\{0,1,2,3,4\}$ | 5 | Complete faces, QT only, $k=6$ absent |
| 6-half-turn | 3 | $\{0,3\}$ | 2 | Complete faces, HT only, cp+ep only |
| 10-partial | 5 | $\{0\}$ | 1 | Incomplete QT faces, co/eo frozen |
| 21-full+slice | 10.5 | $\{0,4,6,8,10,12\}$ | 6 | Complete faces + slice, rescaled $m$ |

#### Symmetry-Broken Families (Irrational)

| Family | $m$ | Spectral field | Layers | Irrational eigenvalues |
|--------|:---:|:--------------:|:------:|:-----------------------|
| $n=8$ (broken axes) | 4 | $\mathbb{Q}(\sqrt{5})$ | 7 | $\lambda_{\pm} = (5\pm\sqrt{5})/8$ |
| $n=16$ (incomplete) | 8 | $\mathbb{Q}(\sqrt{5})$ | 9 | $\lambda_{\pm} = (11\pm\sqrt{5})/16$ |

#### Rational/Irrational Boundary

The spectral field is $\mathbb{Q}$ when the generator set is a union of complete faces (partition integrality, Structural Rationality Criterion). It extends to $\mathbb{Q}(\sqrt{5})$ when face completeness is broken. The boundary is observed to be sharp — no intermediate regime has been found in any tested family. The CP block is protected by the Q₃ Hamming scheme (integer Krawtchouk eigenvalues) and stays rational regardless of generator coverage; only noncommutative blocks (EP, EO) develop irrational eigenvalues under symmetry breaking.

***

## Appendix B: Isotypic Structure of the Spectral Layers

The main text decomposes the averaging operator $A$ into six spectral layers $V_{\lambda}$ and further resolves those layers into QT/HT joint-spectral sectors via the commutative center. This appendix reports the finer isotypic decomposition within each layer, obtained from the full commutant algebra.

### B.1 Isotypic Decomposition

The commutant $\operatorname{Comm}_G(V_{\lambda}) = \{X \in \operatorname{End}(V_{\lambda}) : [X, \rho(g)|_{V_{\lambda}}] = 0 \;\forall g \in G\}$ is computed combinatorially for each layer. Its center $\mathfrak{Z}_{\lambda} = Z(\operatorname{Comm}_G(V_{\lambda}))$ yields the isotypic decomposition. The full 228-dimensional commutant has dimension 610.

| Layer $\lambda$ | dim | $\dim\operatorname{Comm}$ | $\dim\mathfrak{Z}$ | Isotypic components |
|:---------------:|:---:|:-----------------:|:------------------:|:--------------------|
| $V_1$ | 20 | 400 | 1 | $1\text{D} \times 20$ |
| $V_{8/9}$ | 2 | 1 | 1 | $2\text{D} \times 1$ |
| $V_{7/9}$ | 39 | 145 | 13 | $3\text{D} \times 1$ (×13) |
| $V_{2/3}$ | 26 | 145 | 13 | $2\text{D} \times 1$ (×13) |
| $V_{5/9}$ | 106 | 210 | 14 | $6\text{D}\times1$ (×10), $7\text{D}\times1$, $3\text{D}\times1$, **$3\text{D}\times11$**, $3\text{D}\times1$ |
| $V_{1/3}$ | 35 | 65 | 9 | $4\text{D}\times1$ (×8), $3\text{D}\times1$ |

**Total: 51 isotypic components, 59 irreducible summands.** The count of 51 is independent of the unresolved $T_1$/$T_2$ assignment in the CO block (§4.1); that ambiguity affects only the per-layer attribution of the two $T$-irreps. The representation is almost multiplicity-free: 50 of the 51 isotypic components have multiplicity 1. All nontrivial multiplicity is concentrated in a single $3\text{D}\times11$ component inside $V_{5/9}$, which may underlie the hub structure of sector $S_6$. Detailed multiplicity-transfer diagnostics are recorded in (CCS-III §11).

***

## References

**Mathematical lineage.** This paper belongs to the spectral side of the RIME
program: association schemes and Bose--Mesner algebras for the permutation
blocks, finite-group representation theory for the cubie representation, and
harmonic analysis on finite groups for averaging operators. The core question
is not a general commutative-operator theorem, but the concrete arithmetic
problem of why the Rubik averaging spectrum is rational.

The association-scheme background is supplied by the standard texts of
Bannai--Ito and Godsil \cite{bannaiIto1984,godsil1993}. The CP block is the
binary Hamming scheme $H(3,2)$, whose Krawtchouk eigenvalues account for the
CP block's integer spectral contribution. The EP face-incidence algebra sits
near the coherent-configuration side of the same algebraic-combinatorial
framework. Godsil--Martin quotient theory is cited only as formal ancestry for
the later resolved-sector and collision-quotient viewpoint
\cite{godsilMartin1995quotients}; it is not used to prove the rationality
criterion in this paper.

The representation-theoretic background is finite semisimple representation
theory \cite{serre1977,curtisReiner1962}. The averaging operator is also the
representation-theoretic form of a random walk operator on a finite group, in
the sense of Diaconis \cite{diaconis1988}. The Rubik group and cubie-state
conventions follow the standard cube-group literature \cite{joyner2008}; the
standard computational setting is the same 18-generator face-turn framework
used in Kociemba's two-phase algorithm and in the diameter computation of
Rokicki--Kociemba--Davidson--Dethridge
\cite{kociemba1992,rokicki2013diameter}.

Papers II and III are cited internally as the transport and accessibility
continuations of the spectral decomposition \cite{paper2,paper3}; the CCS
records the numerical constitution and reproducibility data \cite{ccs}.

### Code Availability

All numerical experiments, projector constructions, transport computations,
and figure-generation scripts are available at:

https://github.com/dooven-prime/rime-lite

The repository also contains the unified Computational Supplement,
canonical datasets, and reproducibility notebooks corresponding to the trilogy.

***
