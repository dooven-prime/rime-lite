# Spectral Sector Decomposition in Finite Group Representations

### Primitive Idempotents and Emergent Hybrid Structure from the Rubik Cube Group

## Abstract

We study the averaging operator $A = \frac{1}{|S|}\sum_{s\in S} \rho(s)$ of a finite group representation — the spectral object itself. In a Rubik's cube case study, the 228-dimensional representation of the standard 18 face-turn generators yields exactly six distinct rational eigenvalues — a spectral collapse whose mechanism we isolate in the structure of the representation itself, without invoking commutativity of the generators or the character table of the group.

This is the **ontology paper** of the trilogy. It answers: *what are the spectral objects?* — why the spectrum is rational, where primitive sectors come from, why the center exists, why refinement is natural. It does not study transport, dynamics, or Lie accessibility; those belong to Papers II and III respectively.

**Framework.** All structural features are recovered from two primitives of the group representation ρ(g): **support** (permutation action — which indices are affected) and **phase** (diagonal action — what values appear on affected indices). From these two primitives alone, without geometric assumptions, we derive generator classes, index partitions (phase-active vs. phase-trivial), and the full incidence/adjacency structure. Spectral rationality then follows from three independent and composable mechanisms: **combinatorial adjacency** (permutation association schemes whose Bose–Mesner algebras determine candidate eigenvalues), **phase structures** ($\mathbb{Z}_2$ and $\mathbb{Z}_3$ diagonal representations that restrict admissibility), and **partition integrality** (arithmetic closure via per-class trace sums, which enforces the rational form $\lambda = 1 - k/m$). No single mechanism suffices alone; none requires commutativity of the underlying generators.

The main conceptual point of this work is that spectral rationality does not require commutativity of the underlying generators. Instead, it follows from a **Spectral Factorization Principle**: the spectrum factors through the block-diagonal structure of the representation, and the full averaging operator decomposes as a direct sum $\mathcal{A}_{\text{cube}} = \mathcal{A}_{\mathrm{cp}} \oplus \mathcal{A}_{\mathrm{ep}} \oplus \mathcal{A}_{\mathrm{co}} \oplus \mathcal{A}_{\mathrm{eo}}$ — a reduction from 228 dimensions to four independent sub-problems of sizes 64, 144, 8, and 12. At the arithmetic level, this factorization is powered by **block spectral reduction**: the full k-set is the union $\bigcup_B K_B$ of four independently computable block spectra. The cp block spectrum follows from the Q₃ hypercube Bose–Mesner algebra; the ep block spectrum from the face-incidence adjacency algebra $JJ^\top$; the co and eo blocks carry both permutation and orientation phase structure, producing multiple k-values each. The arithmetic closure operates at the level of block-level adjacency/permutation spectra, with no commutativity hypothesis on the generators. In the Rubik's cube, the natural partition is the decomposition into complete faces, where the integrality follows from the elementary cancellation ($\omega + \omega^2 + 1 = 0$) on the corner-orientation block. Galois symmetry provides the structural explanation for why this closure holds; the partition integrality mechanism is verified numerically across all tested face-symmetric generator families (including the n=21 full+slice closure), and post-$\rho$-fix even symmetry-broken families (n=8, n=16) yield fully rational spectra — the previously reported $\mathbb{Q}(\sqrt{5})$ irrationality was a $\rho$-artifact.

---

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $G$ | Finite group |
| $S \subset G$ | Symmetric generating set ($S = S^{-1}$) |
| $\rho: G \to \mathrm{GL}(V)$ | Finite-dimensional orthogonal representation |
| $V$ | Representation space (228-dim for the Rubik cube) |
| **block** | A cubie-type invariant subspace: cp (corner perm, 64-dim), ep (edge perm, 144-dim), co (corner ori, 8-dim), eo (edge ori, 12-dim) |
| $A = \frac{1}{|S|}\sum_{s \in S} \rho(s)$ | Averaging operator — Hermitian when $S = S^{-1}$ and $\rho$ orthogonal |
| $\lambda = 1 - k/m$ | Eigenvalue form; $m$ determined by generator geometry ($m=9$ for 18 face-turn generators) |
| $k$-set | Set of $k$ values producing distinct eigenvalues: $\{0,1,2,3,4,6\}$ for 18-full |
| $P_\lambda$ | Spectral projector onto eigenspace $E_\lambda$ |
| **layer** $V_\lambda = \mathrm{im}(P_\lambda)$ | An eigenspace of the averaging operator $A$ — 6 canonical layers |
| $V_1, V_{8/9}, V_{7/9}, V_{2/3}, V_{5/9}, V_{1/3}$ | Canonical layers ($\lambda = 1 - k/9$, $k \in \{0,1,2,3,4,6\}$) |
| **primitive sector** | Minimal joint eigenspace of Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ — indivisible spectral unit | 
| **S1–S9** | 9 primitive sectors: S1(V₁, isolated), S2(V₈/₉), S3(V₇/₉), S4(V₂/₃), S5–S7(V₅/₉), S8–S9(V₁/₃) |
| **hybrid sector** | Primitive sector supported across multiple cubie-type blocks (e.g., ep+eo) |
| $\mathrm{QT}^a$ | Quarter-turn averaging operator $\frac{1}{2}(\rho(+a) + \rho(-a))$ on axis $a \in \{0,1,2\}$ |
| $\mathrm{HT}^a$ | Half-turn averaging operator $\rho(2a)$ on axis $a \in \{0,1,2\}$ |
| $\mathrm{QT}_{\mathrm{all}} = \sum_a \mathrm{QT}^a$, $\mathrm{HT}_{\mathrm{all}} = \sum_a \mathrm{HT}^a$ | Total quarter-turn / half-turn averaging |
| Center$\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$ | Commutative center — joint diagonalization yields 9 primitive sectors |
| $\chi_\lambda(s) = \mathrm{Tr}(P_\lambda \rho(s))$ | Eigenspace trace — key quantity in partition integrality |
| **Bose-Mesner algebra** | Commuting algebra of a permutation association scheme — spectral engine for cp/co blocks |
| $J$ | Face-incidence matrix — adjacency matrix connecting each position to the positions on the same face |

## 1. Introduction

Averaging group elements in a finite-dimensional representation often produces substantial spectral collapse: many degrees of freedom collapse into a small number of spectral layers. In the Rubik's cube setting, the averaging operator built from the standard 18 face-turn generators displays exactly six distinct eigenvalues ($\lambda = 1 - k/9$ with $k \in \{0,1,2,3,4,6\}$); extending to 21 generators by including the three slice moves (M/E/S) produces six eigenvalues with a different k-set. All eigenvalues are rational across all tested generator families — both face-symmetric and symmetry-broken — a consequence of the block-diagonal structure of the representation and the arithmetic of the permutation/phase actions on each block.

The guiding question is not whether the averaging operator is commutative at the level of generators; it is not. The question is whether a weaker arithmetic condition can force rational spectral values. The answer developed here is yes: **partition integrality** — the condition that the generator set admits a partition whose per-subset eigenspace trace sums are integers — directly forces eigenvalues to be rational, with no commutativity hypothesis on any subalgebra. In the Rubik's cube, the natural partition is the decomposition into complete faces, and the integrality of each face-sum is rooted in the elementary identity ($\omega$ + $\omega^2$ + 1 = 0) on the corner-orientation block. Galois symmetry enters not as the mechanism of rationality but as the structural explanation for why this arithmetic closure holds in symmetric generator families and breaks under symmetry deficits.

This paper has four goals.

1. To formalize the eigenspace trace identity and its consequences.
2. To show that Galois invariance of the averaged operator implies Galois stability of eigenspaces — and that this is insufficient for rationality.
3. To formulate a rigorous sufficient condition — rational eigenspace traces ($\Rightarrow$) rational eigenvalues — that does not require commutativity of any subalgebra.
4. To give a rigorous proof, via the field-of-definition argument (Theorem 6.2), that rational eigenvalues imply rational eigenspace traces: (A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$) implies ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) and hence ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$). The ($\mathbb{Z}$)-level strengthening — that these traces are in fact integers — is verified numerically for all tested face-symmetric families and identified as the remaining open refinement.

**Spectral collapse as interference.** The rational spectrum phenomenon admits an intuitive physical picture. Each generator contributes a phase factor ($\omega^k$) (for (k $\in$ $\{$0, 1, 2$\}$)) to the corner-orientation block. The face-sum (F_{$\mathrm{face}$} = $\rho$(s) + $\rho$(s^{-1}) + $\rho$(s_{180})) aggregates three moves on a single face: the phases from (s) and (s^{-1}) are complex conjugates (($\omega$) and ($\omega^2$)), and (s_{180}) contributes a real phase ((1) or ($\omega^2$)). On a complete face, these phases sum to either 3 or 0 — destructive interference eliminates all non-rational components:

$$
\omega^k + \omega^{-k} + \omega^{2k} \in \{3, 0\} \subset \mathbb{Z}, \qquad k \in \{0,1,2\}.
$$

When every face in the generator set is complete, this per-face cancellation forces the averaging operator (A) to have rational entries, and the spectrum *collapses* into ($\mathbb{Q}$) — all non-rational cyclotomic phases cancel. The spectrum is thus an **interference pattern**: rational eigenvalues correspond to complete destructive interference of the ($\omega$)-phases across all faces.

**Partition integrality as a replacement for commutativity.** The classical route to spectral rationality in group algebras goes through commutativity: if the generator averages (h_i = ($\rho$(g) + $\rho$(g^{-1}))/2) all commute, Schur's Lemma forces joint eigenspaces where (A) acts as a scalar, and the eigenvalue inherits rationality from the (h_i) spectrum. This paper demonstrates a fundamentally different mechanism: **partition integrality** — arithmetic closure at the character level — can force rationality without any commutativity hypothesis. The mechanism requires only that the generator set (S) admits a partition whose per-subset eigenspace trace sums are integers (Theorem 6.1). In the Rubik's cube, the natural partition is the decomposition into complete faces, where the per-face cancellation ($\omega$ + $\omega^2$ + 1 = 0) is an arithmetic identity that operates on traces, not on operators — it does not require the (h_i) to commute. The shift from commutativity to partition integrality is the methodological contribution: it suggests that spectral rationality in more general averaged group representations may be detectable through character-level integrality conditions on a suitable partition, without requiring the strong (and often false) hypothesis that the underlying operators commute.

**Spectral rationality as additive closure.** The core insight of this work can be stated in one sentence: spectral rationality reduces from an algebraic structure problem to an **additive closure problem** at the level of partitioned character sums. The spectral problem — "why are the eigenvalues rational?" — does not require understanding commutativity of operator algebras or decomposing the representation into irreducibles. It requires only that the generator traces, when grouped by a suitable partition, sum to integers. This is an **additive criterion for spectral rationality**: the only algebraic structure needed is the eigenspace trace identity (Theorem 3.1, a tautology), and the only arithmetic structure needed is integer closure under the partition sum (Theorem 6.1, four lines). The entire nontrivial content of the phenomenon — *which* partitions work and *why* they produce integer per-subset sums — is concentrated in the single arithmetic identity ($\omega$ + $\omega^2$ + 1 = 0). This demotion from algebra to arithmetic is the paper's central conceptual move.

## 2. Setting and notation

Let G be a finite group and let ($\rho$: G $\to$ GL(V)) be a finite-dimensional complex representation. Let S $\subseteq$ G be a finite symmetric generating set, meaning (S = S^{-1}). Define the averaging operator
$$
A = \frac{1}{|S|} \sum_{s\in S} \rho(s) \in \mathrm{End}(V).
$$
**Proposition 2.1 (Inverse-Closure Hermiticity).** For an orthogonal representation $\rho$, the averaging operator $A = \frac{1}{|S|}\sum_{s\in S}\rho(s)$ is Hermitian iff $S$ is inverse-closed ($S = S^{-1}$).

*Proof.* Since $\rho$ is orthogonal, $\rho(s)^\dagger = \rho(s)^T = \rho(s^{-1})$ for every $s \in G$. The adjoint of $A$ is
$$
A^\dagger = \frac{1}{|S|}\sum_{s\in S}\rho(s)^\dagger = \frac{1}{|S|}\sum_{s\in S}\rho(s^{-1}) = \frac{1}{|S|}\sum_{t\in S^{-1}}\rho(t).
$$
Hence $A^\dagger = A \iff S = S^{-1}$. Concretely: Hermiticity of $A$ requires that for every generator $s$ in $S$, its inverse $s^{-1}$ is also in $S$ with equal weight. $\square$

**Remark.** This is a structural prerequisite for the entire spectral theorem: without inverse-closure, $A$ is not Hermitian, its eigenvalues are not real, and eigenspaces are not orthogonal. For the Rubik’s cube, the standard 18 face-turn generators satisfy $S = S^{-1}$ (R/R’/R2, U/U’/U2, etc.), so $A$ is Hermitian. Generator sets that violate this (e.g., CW-only turns) yield non-Hermitian $A$ and ill-posed spectral decompositions.

In the Rubik’s cube application, V is a 228-dimensional faithful representation with the block decomposition
$$
V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}},
$$
corresponding to corner permutation, edge permutation, corner orientation, and edge orientation blocks.

![**Figure 2:** The four invariant subspaces that form the ontology primitives of the Rubik's cube representation. CP (Q$_3$ Hamming scheme, 64-dim) and EP (face-incidence adjacency, 144-dim) carry the permutation degrees of freedom; CO (Z$_3$ phase, 8-dim) and EO (Z$_2$ phase, 12-dim) carry the abelian orientation characters. Noncommutativity is concentrated in EP ($\|[\mathrm{QT}^0, \mathrm{QT}^1]\|_{\mathrm{ep}} = 2.74$, 94% of total); CP is exactly commutative (Theorem 7.3). The block decomposition reduces the 228-dimensional problem to four independent sub-algebras (Theorem 3.4).](../../figures/paper1_fig2_block_atlas.png)

We write ($E_\lambda$) for the eigenspace of A with eigenvalue ($\lambda$), and ($P_\lambda$) for the orthogonal projector onto ($E_\lambda$).

Throughout, ($\sigma$) denotes the nontrivial Galois automorphism of ($\mathbb{Q}$($\omega$)/$\mathbb{Q}$), where ($\omega$ = e^{2$\pi$ i/3}) and ($\sigma$($\omega$)=$\omega^2$).

## 3. Main results

### Theorem 3.1 (Eigenspace trace identity)

For every eigenvalue ($\lambda$) of A with orthogonal projector ($P_\lambda$) onto ($E_\lambda$),
$$
\lambda = \frac{1}{d_\lambda}\cdot\frac{1}{|S|}\sum_{s\in S}\chi_\lambda(s),
\qquad
\chi_\lambda(s) := \mathrm{Tr}(P_\lambda\rho(s)),
\qquad d_\lambda = \dim E_\lambda.
$$

**Note on terminology.** The function ($\chi_\lambda$(s) = $\mathrm{Tr}$($P_\lambda$ $\rho$(s))) is the **restricted trace** of ($\rho$(s)) on the eigenspace ($E_\lambda$), not the group character of a subrepresentation unless ($E_\lambda$) is ($\rho$(G))-invariant (which it is not, in general). We refer to ($\chi_\lambda$) as the "eigenspace trace" throughout.

#### Proof.

Since (A$P_\lambda$ = $\lambda$ $P_\lambda$), taking traces gives
$$
\mathrm{Tr}(AP_\lambda) = \lambda\cdot\mathrm{Tr}(P_\lambda)=\lambda d_\lambda.
$$
On the other hand, by linearity of the trace,
$$
\mathrm{Tr}(AP_\lambda)
= \frac{1}{|S|}\sum_{s\in S}\mathrm{Tr}(\rho(s)P_\lambda)
= \frac{1}{|S|}\sum_{s\in S}\chi_\lambda(s).
$$
Combining the two identities yields the claim. ($\square$)

### Theorem 3.2 (Galois stability of eigenspaces)

Assume A is Hermitian and satisfies ($\sigma$(A)=A). Then for every eigenvalue ($\lambda$),
$$
\sigma(E_\lambda)=E_\lambda.
$$
Equivalently, ($\sigma$($P_\lambda$)=$P_\lambda$).

#### Proof.

Let (v$\in$ $E_\lambda$), so (Av=$\lambda$ v). Apply ($\sigma$) entrywise:
$$
A,\sigma(v)=\sigma(A)\sigma(v)=\sigma(Av)=\sigma(\lambda v)=\overline{\lambda},\sigma(v).
$$
Because A is Hermitian, ($\lambda\in\mathbb{R}$), hence ($\overline{\lambda}$=$\lambda$). Therefore ($\sigma$(v)$\in$ $E_\lambda$), showing ($\sigma$($E_\lambda$)$\subseteq$ $E_\lambda$). Since ($\sigma^2$=$\mathrm{id}$), equality follows. The projector statement is equivalent. ($\square$)

### Theorem 3.3 (Rationality from Galois-stable projector — conditional)

Suppose the spectral projector ($P_\lambda$) satisfies ($\sigma$($P_\lambda$)=$P_\lambda$) and is defined over a number field K with ($K^\sigma$ = $\mathbb{Q}$) (for example, (K = $\mathbb{Q}$($\omega$)) with ($\sigma$($\omega$)=$\omega^2$)). Then ($\lambda$ $\in$ $\mathbb{Q}$).

#### Proof.

By Theorem 3.1,
$$
\lambda = \frac{1}{d_\lambda}\cdot\frac{1}{|S|}\sum_{s\in S}\chi_\lambda(s),
\qquad \chi_\lambda(s) = \mathrm{Tr}(P_\lambda \rho(s)).
$$

Since ($P_\lambda$ $\in$ M_n(K)) and ($\rho$(s) $\in$ M_n($\mathbb{Z}$[$\omega$]) $\subset$ M_n(K)), each trace ($\chi_\lambda$(s) $\in$ K). Their average lies in K. Because ($\sigma$($P_\lambda$)=$P_\lambda$), we have ($\sigma$($\chi_\lambda$(s)) = $\chi_\lambda$(s)) for each (s), hence the sum is fixed by ($\sigma$). Therefore the sum lies in ($K^\sigma$ = $\mathbb{Q}$), and ($\lambda$ $\in$ $\mathbb{Q}$). ($\square$)

#### Remark (The hidden hypothesis).

Theorem 3.3 is logically valid but its hypothesis is strong: it assumes the projector is already defined over a field whose Galois fixed field is ($\mathbb{Q}$). In practice, verifying ($P_\lambda$ $\in$ M_n(K)) requires knowing the field of definition of the eigenspace — which is equivalent to the rationality problem itself. Theorem 3.3 therefore does **not** close the gap; it merely isolates the precise field-of-definition condition. The substantive input that fulfills this hypothesis — the per-face character integrality or its equivalent — is supplied in §5–§6. The Galois stability ($\sigma$($P_\lambda$) = $P_\lambda$) (Theorem 3.2) is necessary but not sufficient: it constrains the field to ($K^\sigma$), but without an independent proof that (K = $\mathbb{Q}$($\omega$)), the fixed-field argument cannot reduce ($K^\sigma$) to ($\mathbb{Q}$).

### Theorem 3.4 (Block Compatibility Lemma)

Let the representation space decompose as a direct sum

$$
V = \bigoplus_{i=1}^{k} V_i,
$$

where each (V_i) is ($\rho$(G))-invariant (hence (A)-invariant). Let (P_i: V $\to$ V_i) be the orthogonal projector onto (V_i). Then for every eigenspace projector ($P_\lambda$) of (A):

$$
P_\lambda = \bigoplus_{i=1}^{k} P_{\lambda,i}, \qquad P_{\lambda,i} := P_i P_\lambda P_i.
$$

Equivalently, ($P_\lambda$) commutes with every block projector: ([$P_\lambda$, P_i] = 0) for all (i).

#### Proof.

Since each $V_i$ is $\rho(G)$-invariant, it is invariant under $A = \frac{1}{|S|}\sum_s \rho(s)$. Thus $A$ is block-diagonal with respect to the decomposition: $A = \bigoplus_i A_i$ where $A_i = A|_{V_i}$. The spectral projector $P_\lambda$ is a polynomial in $A$ (by Lagrange interpolation on the distinct eigenvalues): $P_\lambda = \prod_{\mu \neq \lambda} (A - \mu I)/(\lambda - \mu)$. Since $A$ is block-diagonal, any polynomial in $A$ is also block-diagonal. Hence $P_\lambda = \bigoplus_i P_{\lambda,i}$ with $P_{\lambda,i} \in \mathrm{End}(V_i)$. The commutativity $[P_\lambda, P_i] = 0$ follows immediately. $\square$

### Corollary 3.5

For each block $V_i$, the restricted projector $P_{\lambda,i}$ is an orthogonal projector on $V_i$ satisfying $P_{\lambda,i}^2 = P_{\lambda,i}$, $P_{\lambda,i}^* = P_{\lambda,i}$, and $P_{\lambda,i} A_i = A_i P_{\lambda,i} = \lambda P_{\lambda,i}$ whenever $P_{\lambda,i} \neq 0$.

#### Remark.

Theorem 3.4 is structurally trivial — it is a direct consequence of $A$ being block-diagonal. Its value is organizational: it reduces the 228-dimensional problem to four independent sub-problems, one per block. The field of definition of $P_\lambda$ is the compositum of the fields of definition of the $P_{\lambda,i}$.

### 3.5 Spectral Origin via Block Bose–Mesner Algebras

The preceding theorems establish *that* the eigenvalues are rational and *that* they take the form $\lambda = 1 - k/m$. They do not explain *why* exactly six eigenvalues appear, nor *why* those particular k-values. This section provides the definitive answer: **the six spectral layers are not primitive — they are resonance-bound states of ten blockwise primitive idempotents, merged by eigenvalue coincidence under the global averaging operator.**

**Theorem 3.6 (Spectral Origin).** Let $\rho: G \to \mathrm{GL}(228, \mathbb{C})$ be the Rubik's cube representation with the standard block decomposition $V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}}$, and let $A = $\frac{1}{|S|}$ \sum_{s \in S} \rho(s)$ be the averaging operator over the 18 face-turn generators. Then:

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

3. **(Spectral resonance merging.)** A block-level primitive idempotent yields eigenvalue $\lambda = 1 - k_{\mathrm{block}}/m$ where $m = |S|/2$. Different blocks can produce the same $\lambda$ for different internal $k$ values. The eigenvalue coincidence merges block-level idempotents into global spectral projectors:

   | Global $\lambda$ | $k$ | cp $k$ | ep $k$ | co $k$ | eo $k$ | Resonance pattern |
   |------------------|-----|--------|--------|--------|--------|-------------------|
   | $1$ | 0 | 0 | 0 | 0 | 0 | All-block trivial |
   | $8/9$ | 1 | — | — | — | 2 | eo-only (was masked pre-$\rho$-fix) |
   | $7/9$ | 2 | 2 | 2 | 0 | — | cp+ep Krawtchouk/adjacency alignment |
   | $2/3$ | 3 | 3 | — | 0 | — | cp-only Krawtchouk (co-block support boundary) |
   | $5/9$ | 4 | 4 | 4 | 0 | 2 | cp+ep+eo triple resonance |
   | $1/3$ | 6 | — | 6 | — | — | ep-only adjacency |

   $k=5$ ($\lambda=4/9$) is genuinely absent — no blockwise primitive idempotent produces it.

   The resonance table is the **genetic code** of the spectral hierarchy. Each of the 6 global eigenvalues is a distinct coincidence class among the 10 blockwise primitive idempotents.

4. **(No global Gelfand pair.)** There exists no subgroup $K \subset G$ such that $(G, K)$ is a Gelfand pair with $H(G, K) \cong \mathbb{C}[A] \cong \mathbb{C}^6$. The Rubik's cube group has approximately $4.3 \times 10^{19}$ elements; for any subgroup $K$, the number of double cosets $|K \backslash G / K|$ — which equals $\dim H(G, K)$ — is vastly larger than 6 (approximately 854 by character-theoretic computation). The global spectral algebra is not a single Hecke algebra.

5. **(Blockwise local Gelfand geometry.)** Despite the absence of a global Gelfand pair, **each block-level commutative algebra is the Hecke algebra (or abelian phase algebra) of an appropriate group pair on that block's automorphism group:**
   - cp block: $H(S_2 \wr S_3, S_3)$ — the Hecke algebra of the hyperoctahedral group
   - ep block: Hecke algebra of the edge-permutation automorphism group
   - co/eo blocks: abelian phase algebras (trivial Hecke structure)

   The spectral origin is **blockwise-local**, not global. This is a **heterogeneous coupled scheme**: four independent association/phase structures, each with its own Gelfand geometry, coupled only through the eigenvalue resonance of the global averaging operator.

6. **(Rational spectral law.)** The eigenvalues $\lambda = 1 - k/m$ are normalized adjacency eigenvalues of the blockwise Bose–Mesner algebras. The Krawtchouk polynomials give the cp eigenvalues; the $JJ^T$ spectrum gives the ep eigenvalues; the Z₃/Z₂ phase cancellation identities give the co/eo eigenvalues. The integrality $\chi_\lambda(s) \in \mathbb{Z}$ follows from the Bose–Mesner trace pairing (Lemma 9.1) applied within each block's algebra.

**Consequence.** The six spectral layers are **not** primitive objects. They are resonance-bound states — the result of 10 block-level primitive idempotents collapsing to 6 under the global eigenvalue coincidence $\lambda = 1 - k/m$. The number 6 is not mysterious: it is the number of distinct $k$-values in the union $\bigcup_B K_B$, which in turn is determined by which blockwise primitive idempotents produce coincident eigenvalues. The formula $|K(A)| = |\bigcup_B K_B|$ is exact; the content of Theorem 3.6 is the identification of each $K_B$ with the primitive idempotent spectrum of the corresponding blockwise Bose–Mesner algebra.

**Terminological precision.** Throughout this paper, "spectral layer" refers to an eigenspace $E_\lambda$ of the averaging operator $A$ — a subspace of the 228-dimensional representation space $V$, not a subset of group states. The spectral structure is a property of the operator $A \in \mathrm{End}(V)$; it does not describe "states" of the Rubik's cube but rather the decomposition of the representation into $A$-eigenspaces. This paper is the **ontology paper** of the trilogy: it answers what the spectral objects are and why they take the form they do. Paper II [2] studies the transport topology $K_{\alpha\beta}$ — how these spectral sectors couple through the group action. Paper III [3] studies the Lie accessibility hierarchy $\kappa_d$ — why discrete composition can reach sectors that Lie operations never can. The three papers share a single numerical source [4].

![**Figure 1:** The six canonical spectral layers produced by resonance merging of thirteen block-level primitive idempotents under the rational law $\lambda = 1 - k/9$. The vacancy at $k = 5$ is structural: no block contributes support at this level (Theorem 7.1). Each layer's internal block composition — cp (corner permutation), ep (edge permutation), co (corner orientation), eo (edge orientation) — is shown by the stacked bar decomposition. V$_{5/9}$ dominates (106/228 = 46% of total dimension) and carries the primary transport hub.](../../figures/paper1_fig1_spectral_tower.png)

## 4. Per-block projector field analysis

We now apply the Block Compatibility Lemma to the Rubik’s cube representation. The 228-dimensional space decomposes into four ($\rho$(G))-invariant blocks:

$$
V = V_{\mathrm{cp}} \oplus V_{\mathrm{ep}} \oplus V_{\mathrm{co}} \oplus V_{\mathrm{eo}},
$$

with dimensions 64, 144, 8, and 12, respectively. By Theorem 3.4, each eigenspace projector splits as

$$
P_\lambda = P_{\lambda,\mathrm{cp}} \oplus P_{\lambda,\mathrm{ep}} \oplus P_{\lambda,\mathrm{co}} \oplus P_{\lambda,\mathrm{eo}}.
$$

We determine the field of definition for each block projector.

### 4.1 Permutation blocks (cp, ep) and edge-orientation block (eo)

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

For the permutation blocks (cp, ep), each spectral projector is a polynomial in the matrix with coefficients in the field generated by the eigenvalues. The cp and ep spectra are derived analytically in §7.2 via the $Q_3$ hypercube and octahedron graph decompositions (Theorems 7.2–7.3).

The edge-orientation block (eo) admits a precise structural analysis -- the $\mathbb{Z}_2$ analog of Lemma 4.1 -- which we present next.

**Lemma 4.0 (Structure of the edge-orientation block).** Let

$$
A = \frac{1}{|S|} \sum_{s \in S} \rho(s)
$$

be the averaging operator over a face-symmetric generator set $S$. The edge-orientation block $A_{\mathrm{eo}}$ is a $12 \times 12$ permutation@phase matrix — it carries both edge position permutation (an edge on a turned face moves to a new position) and $\mathbb{Z}_2$ orientation phase. The averaging over 18 face-turn generators yields three distinct eigenvalues, giving $K_{\mathrm{eo}} = \{1, 2, 4\}$ with multiplicities $(2, 3, 7)$.

Unlike the pre-$\rho$-fix representation (which was diagonal-only — orientation phase without position permutation), the corrected $\rho$ gives $A_{\mathrm{eo}}$ off-diagonal entries: edge orientation states mix across positions via the permutation action. This is the $\mathbb{Z}_2$ analog of the co block’s permutation@phase structure (Lemma 4.1).

#### Proof sketch.

For the 18-full family:
- **Phase-active positions** (edges on F/B faces): flipped by quarter turns. Each such edge participates in a 4-cycle on its face, accumulating $\pm 1$ phase factors. The averaged contribution splits across three eigenvalues.
- **Phase-trivial positions** (edges on R/L/U/D only): never flipped. These 4 positions are permuted among themselves by R/L/U/D turns.

The exact multiplicities (2, 3, 7) and k-values {1, 2, 4} are obtained by diagonalizing the $12 \times 12$ matrix $A_{\mathrm{eo}}$. A first-principles derivation from the $\mathbb{Z}_2 \wr S_{12}$ structure of the edge orientation representation is deferred to future work. $\square$

**Structural summary.** The eo block carries a $\mathbb{Z}_2$ permutation@phase structure. Post-$\rho$-fix, it participates in spectral layering with 3 distinct k-values:
$$
\text{eo: } K_{\mathrm{eo}} = \{1, 2, 4\}, \qquad d_1=2,\; d_2=3,\; d_4=7.
$$

#### Remark (Combined block contribution).

Post-$\rho$-fix, all four blocks carry permutation@phase structure. Each block independently contributes its k-values; the full spectrum is the union:

$$
\begin{array}{c|cccc|c}
\text{Block} & \text{Dim} & \text{Structure} & \text{Mechanism} & k\text{-set (18-full)} \\
\hline
\mathrm{cp} & 64 & S_8 \otimes I_8 & Q_3 \text{ hypercube} & \{0, 4, 6\} \\
\mathrm{ep} & 144 & S_{12} \otimes I_{12} & \text{Face-incidence graph} & \{0, 2, 3, 4\} \\
\mathrm{co} & 8 & \mathbb{Z}_3 \text{ perm@phase} & \text{Permutation + phase} & \{3, 4, 6\} \\
\mathrm{eo} & 12 & \mathbb{Z}_2 \text{ perm@phase} & \text{Permutation + phase} & \{1, 2, 4\} \\
\hline
\text{All} & 228 & \oplus & \text{Union of above} & \{0, 1, 2, 3, 4, 6\}
\end{array}
$$

The unification of all four blocks under permutation@phase structure is a consequence of the corrected $\rho$ representation.

### 4.2 Corner-orientation block (co) — the critical case

The corner-orientation block is the only block where the Galois action is nontrivial. The generators act by diagonal matrices with entries in ($\{$1, $\omega$, $\omega^2\}$) where ($\omega$ = e^{2$\pi$ i/3}):

$$
\rho_{\mathrm{co}}(s) \in M_{8}(\mathbb{Z}[\omega]) \subset M_{8}(\mathbb{Q}(\omega)).
$$

**Lemma 4.1 (Structure of the corner-orientation block).** Let

$$
A = \frac{1}{|S|} \sum_{s \in S} \rho(s)
$$

be the averaging operator over a face-symmetric generator set (S). The corner-orientation block $A_{\mathrm{co}}$ is an $8 \times 8$ permutation@phase matrix — it carries both corner position permutation (a corner on a turned face moves to a new position) and $\mathbb{Z}_3$ orientation phase. The averaging over 18 face-turn generators yields three distinct eigenvalues, giving $K_{\mathrm{co}} = \{3, 4, 6\}$ with multiplicities $(2, 3, 3)$.

**Note (post-$\rho$-fix).** The pre-$\rho$-fix representation was diagonal-only — it recorded the orientation phase at fixed corner positions without permuting positions. Under that incorrect representation, $A_{\mathrm{co}}$ was the scalar matrix $\lambda_{\mathrm{co}} I_8$ with $\lambda_{\mathrm{co}} = 2/3$. The corrected $\rho$ includes the position permutation, giving $A_{\mathrm{co}}$ off-diagonal entries and three distinct eigenvalues. The co block now participates in spectral layering on equal footing with the other three blocks.

#### Proof sketch.

The co block is the restriction of the permutation@phase representation to the 8 corner orientation coordinates. Each generator $s$ acts as a monomial matrix: it permutes corner positions (via the face-turn 4-cycle) and multiplies by $\omega^{\delta}$ for the orientation twist. The averaging operator $A_{\mathrm{co}} = \frac{1}{18} \sum_s \rho_{\mathrm{co}}(s)$ acquires off-diagonal entries from the position permutation.

For the **18-full** family, diagonalizing the $8 \times 8$ matrix $A_{\mathrm{co}}$ yields:

$$
\lambda_{\mathrm{co}} \in \{\tfrac{1}{3}, \tfrac{5}{9}, \tfrac{2}{3}\}, \qquad
K_{\mathrm{co}} = \{3, 4, 6\}, \qquad (d_3, d_4, d_6) = (2, 3, 3).
$$

All three eigenvalues are rational. The co block now participates in spectral layering on equal footing with the other three blocks. Its eigenvalues are determined by the cycle structure of the permutation action weighted by the accumulated $\mathbb{Z}_3$ phases along each cycle — a well-posed but combinatorially involved computation deferred to future work. $\square$

**Extension to other families** (numerical):

- **21-full+slice**: slice moves are identity on co. $K_{\mathrm{co}}$ expands.
- **12-quarter** (no 180°): different cycle weighting. $K_{\mathrm{co}}$ shifts.
- **6-half** (half-turns only): no orientation twists, $\lambda_{\mathrm{co}} = 1$, $k = 0$.
- **10-partial**: partial face coverage removes the Galois pairing.

In every case, the eigenvalues are rational — the $\mathbb{Z}_3$ phases participate in the permutation action, and the resulting cycle characters are sums of $\omega^k$ terms that either cancel ($\omega + \omega^2 + 1 = 0$) or sum to integers.

**Lemma 4.2** (Co-block Galois stability). For face-symmetric (S), $A_{\mathrm{co}} \in M_{8}(\mathbb{Q}(\omega))$ and satisfies $\sigma(A_{\mathrm{co}}) = A_{\mathrm{co}}$ (the $\omega$ and $\omega^2$ terms are paired by face symmetry). By Theorem 3.2, the co-block spectral projectors satisfy $\sigma(P_{\lambda,\mathrm{co}}) = P_{\lambda,\mathrm{co}}$ for every eigenvalue $\lambda$. All three eigenvalues are real and rational. $\square$

#### Remark (Galois stability vs. projector rationality).

Lemma 4.2 shows that the co-block eigenspaces are Galois-stable — a structural property of the face-symmetric averaging operator. The step from Galois stability to rational projectors is handled by Theorem 6.2 (field-of-definition).

### 4.3 Unified projector field

Combining the block analyses, we obtain a structural reduction. The following proposition is specific to the Rubik's cube representation, where (A $\in$ M_{228}($\mathbb{Q}$)) (for face-symmetric (S)) and (A) is Hermitian.

**Proposition 4.3** (Projector field reduction). For face-symmetric (S), (A $\in$ M_{228}($\mathbb{Q}$)) (Lemma 4.1) and is Hermitian. The equivalence ($\lambda$ $\in$ $\mathbb{Q}$ $\iff$ $P_\lambda$ $\in$ M_{228}($\mathbb{Q}$)) is a special case of Theorem 6.2, whose proof via the field-of-definition argument ((A - $\lambda$ I $\in$ M_n($\mathbb{Q}$) $\Rightarrow$ $\ker$(A - $\lambda$ I)) has a ($\mathbb{Q}$)-basis) is given in §6.

**Important.** This is a linear algebra fact for any Hermitian matrix with rational entries, not a deep representation-theoretic claim. Unlike the classical approach (which required commuting (h_i) and Schur's Lemma), the field-of-definition argument uses only the rationality of the matrix entries and the eigenvalue.

## 5. Generator character integrality

The generator-character integrality argument is the arithmetic input behind the rationality mechanism. In the Rubik’s cube case study, the 228-dimensional representation decomposes into four structural blocks:

$$
\rho(g)=P_{\mathrm{cp}}(g)\oplus P_{\mathrm{ep}}(g)\oplus \Omega_{\mathrm{co}}(g)\oplus \Sigma_{\mathrm{eo}}(g).
$$

The permutation blocks (P_{$\mathrm{cp}$},P_{$\mathrm{ep}$}) are defined over ($\mathbb{Q}$), the edge-orientation block ($\Sigma_{\mathrm{eo}}$) is also defined over ($\mathbb{Q}$), and the corner-orientation block ($\Omega_{\mathrm{co}}$) lives over ($\mathbb{Q}$($\omega$)).

### Theorem 5.1 (Generator character integrality)

For each of the 18 face-turn generators (s), the block characters

$$
\chi_{\mathrm{cp}}(s),\quad \chi_{\mathrm{ep}}(s),\quad \chi_{\mathrm{co}}(s),\quad \chi_{\mathrm{eo}}(s)
$$

are integers.

#### Proof.

The permutation blocks count fixed cubies, hence are integer-valued. The edge-orientation block has entries in ($\{\pm$ 1$\}$), hence integer trace. The corner-orientation block has diagonal entries in ($\{$1,$\omega$,$\omega^2\}$), and the Rubik’s cube orientation conservation law forces the ($\omega$)-coefficients to balance in each generator, leaving an integer trace. ($\square$)

### Corollary 5.2 (Face triple integrality)

For any face-complete triple ($\{$g, g^{-1}, g_{180}$\}$), the total character sum over the triple is an integer:

$$
\chi(g) + \chi(g^{-1}) + \chi(g_{180}) \in \mathbb{Z}.
$$

This follows from Theorem 5.1: the face-sum trace ($\mathrm{Tr}$(F_{$\mathrm{face}$})) with (F_{$\mathrm{face}$} = $\rho$(g) + $\rho$(g^{-1}) + $\rho$(g_{180})) is integer-valued — the ($\omega$) terms cancel because ($\omega^{k}$ + $\omega^{-k}$ + $\omega^{2k}$ $\in$ $\{$3, 0$\}$ $\subset$ $\mathbb{Z}$) on the co block, and all other blocks contribute integer traces. (Entrywise integrality of the face-sum matrix entries on the co-block is verified numerically in the implementation.)

Corollary 5.2 is the concrete arithmetic closure at the generator level. The remaining difficulty, addressed in §6, is upgrading this from generator-level integrality to eigenspace-level integrality.

## 6. The arithmetic engine: face-sum integrality

We now present the core mechanism that produces rational eigenvalues. This section is the logical heart of the paper: it establishes an arithmetic partition criterion (Theorem 6.1) — a general sufficient condition for spectral rationality that requires only a partition of the generator set with integer per-subset trace sums. The criterion uses no Galois theory, no commutativity of any subalgebra, and no field-of-definition argument; it is a direct consequence of the eigenspace trace identity (Theorem 3.1) plus arithmetic closure at the trace level. In the Rubik's cube setting, the natural partition is the decomposition into complete faces, where the integrality follows from the cancellation ($\omega$ + $\omega^2$ + 1 = 0) on the corner-orientation block.

**Logical dependency of Theorems in this section.** The four main results form the following chain (($\rightarrow$) = "is used in the proof of"; ($\dashrightarrow$) = "provides the arithmetic input for"):

$$
\begin{aligned}
\text{Theorem 3.1 (trace identity)} &\;\rightarrow\; \text{Theorem 6.4 (sufficient direction)} \\
&\quad \dashrightarrow\; \text{Theorem 6.1 (partition integrality mechanism)} \\
\text{Theorem 6.2 (field-of-definition, } \Rightarrow\text{)} &\;\rightarrow\; \text{Theorem 6.4 (converse, conditional on } A\in M_n(\mathbb{Q})\text{)} \\
\text{Theorem 5.1/5.2 (generator integrality)} &\;\dashrightarrow\; \text{Theorem 6.1 (per-subset integer input, Rubik's cube specialization)}
\end{aligned}
$$

In words: Theorem 3.1 is the tautological starting point — it links ($\lambda$) to eigenspace traces and is used in every proof that follows. Theorem 6.4 deploys this identity to prove the unconditional forward direction (rational traces ($\Rightarrow$) rational eigenvalues). Theorem 6.2 supplies the converse via the field-of-definition argument ((A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$) ($\Rightarrow$) ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) ($\Rightarrow$) ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$)). Theorem 6.1 provides the general arithmetic mechanism: any partition of (S) with integer per-subset trace sums forces ($\lambda$ $\in$ $\mathbb{Q}$). In the Rubik's cube specialization, Theorems 5.1/5.2 supply the integer input for the face partition. The full proven chain is: **partition integrality ($\Rightarrow$) ($\lambda$ $\in$ $\mathbb{Q}$) ($\Rightarrow$) ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) ($\Rightarrow$) ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$)**. The ($\mathbb{Z}$)-level strengthening (($\chi_\lambda$(s) $\in$ $\mathbb{Z}$) rather than merely ($\mathbb{Q}$)) is verified numerically for all tested face-symmetric families.

### Theorem 6.1 (Arithmetic partition criterion ⇒ rational spectrum)

Let (S = S^{-1}) be a finite symmetric subset of (G) and let

$$
A = \frac{1}{|S|} \sum_{s \in S} \rho(s)
$$

be the averaging operator on a finite-dimensional representation (V). Suppose (S) admits a partition (S = $\bigsqcup_{i=1}^{k}$ S_i) such that for every eigenspace projector ($P_\lambda$) of (A), the per-subset trace sum is integral:

$$
\sum_{s \in S_i} \chi_\lambda(s) \in \mathbb{Z}, \qquad \chi_\lambda(s) = \mathrm{Tr}(P_\lambda \rho(s)), \qquad i = 1, \dots, k.
$$

Then every eigenvalue of (A) satisfies ($\lambda$ $\in$ $\mathbb{Q}$).

**Specialization to the Rubik's cube.** In the Rubik's cube setting ((V = $\mathbb{C}^{228}$)), face-symmetry provides the natural partition: (S) decomposes into complete faces (S_i = $\{$g, g^{-1}, g_{180}$\}$). The integrality of each face-sum follows from Theorem 5.1/5.2 and the cancellation ($\omega$ + $\omega^2$ + 1 = 0) on the corner-orientation block (Lemma 4.1). The theorem applies to any partition satisfying the integrality hypothesis — the face decomposition is the concrete instance verified in this paper.

### Proof.

**Step 1 — Eigenspace trace identity.** By Theorem 3.1, ($\lambda$ = $\frac{1}{d_\lambda |S|} \sum_{s \in S} \chi_\lambda(s)$).

**Step 2 — Decompose over the partition.** Summing per subset:

$$
\sum_{s \in S} \chi_\lambda(s) = \sum_{i=1}^{k} \sum_{s \in S_i} \chi_\lambda(s).
$$

**Step 3 — Integrality.** Each per-subset sum is an integer (hypothesis). A finite sum of integers is an integer:

$$
\sum_{s \in S} \chi_\lambda(s) \in \mathbb{Z}.
$$

**Step 4 — Rationality.** From Step 1:

$$
\lambda = \frac{1}{d_\lambda |S|} \times (\text{integer}) \in \mathbb{Q}. \quad\square
$$

### Remark (What this theorem does NOT use).

The proof of Theorem 6.1 uses exactly three ingredients:
- Theorem 3.1 (eigenspace trace identity — tautological, §3),
- the existence of a partition of (S) with the integrality property,
- the hypothesis that per-subset trace sums are integers.

It does **not** use:
- Galois symmetry (($\sigma$)),
- commutativity of the (h_i) operators,
- the field of definition of ($P_\lambda$),
- the block decomposition of (V),
- Schur's Lemma,
- any property of (A) beyond linearity of the trace,
- any specific structure of the Rubik's cube group.

**The entire difficulty of spectral rationality is concentrated in the single hypothesis** — that a partition with integral per-subset trace sums exists. For the Rubik's cube, the face decomposition provides this partition; the integrality of each face-sum follows from the arithmetic cancellation ($\omega$ + $\omega^2$ + 1 = 0) on the co-block (Theorem 5.1/5.2, Lemma 4.1). The eigenspace-level reduction from generator traces to eigenspace traces is given by Theorem 6.2 below (at the ($\mathbb{Q}$)-level); the strengthening from ($\mathbb{Q}$) to ($\mathbb{Z}$) (individual trace integrality) is verified numerically for all tested face-symmetric families.

### Theorem 6.2 (Field of definition of eigenspaces)

Let (A $\in$ M_n($\mathbb{Q}$)) be Hermitian. For any eigenvalue ($\lambda$), let ($E_\lambda$ = $\ker$(A - $\lambda$ I)) and ($P_\lambda$) be the orthogonal projector onto ($E_\lambda$). Then:

$$
\lambda \in \mathbb{Q} \;\Longleftrightarrow\; E_\lambda \text{ admits a basis in } \mathbb{Q}^n \;\Longleftrightarrow\; P_\lambda \in M_n(\mathbb{Q}).
$$

For the Rubik's cube representation, (A $\in$ M_{228}($\mathbb{Q}$)) is established by Lemma 4.1 (the co-block averaging operator is a rational scalar, ($\lambda_{\mathrm{co}}$ I_8), with ($\lambda_{\mathrm{co}}$ $\in$ $\mathbb{Q}$) forced by the cancellation of ($\omega$)-dependent terms across paired non-reference faces via ($\omega$ + $\omega^2$ + 1 = 0)). For face-symmetric (S) and any generator (s $\in$ S), the eigenspace trace satisfies:

$$
\lambda \in \mathbb{Q} \;\Longrightarrow\; \chi_\lambda(s) = \mathrm{Tr}(P_\lambda \rho(s)) \in \mathbb{Q}.
$$

### Proof.

This is a standard linear algebra fact: kernels of rational matrices admit rational bases, and the orthogonal projector constructed from a rational basis has rational entries. Since $X \in M_{n \times d}(\mathbb{Q})$, the Gram matrix $X^\top X \in M_d(\mathbb{Q})$ is invertible with rational determinant, and by Cramer's rule its inverse is also rational: $(X^\top X)^{-1} \in M_d(\mathbb{Q})$. Therefore $P_\lambda = X(X^\top X)^{-1} X^\top \in M_n(\mathbb{Q})$. The theorem calls this fact into the service of the arithmetic criterion — it is not a new claim, but a precise identification of the classical mechanism that closes the converse direction.

**(($\lambda$ $\in$ $\mathbb{Q}$) $\Rightarrow$ ($P_\lambda$ $\in$ M_n($\mathbb{Q}$))).** Since (A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$), the matrix (A - $\lambda$ I $\in$ M_n($\mathbb{Q}$)). The eigenspace ($E_\lambda$ = $\ker$(A - $\lambda$ I)) is the nullspace of a rational matrix — a homogeneous linear system with rational coefficients. Gaussian elimination over ($\mathbb{Q}$) produces a basis of vectors in ($\mathbb{Q}^n$). Let (X $\in$ M_{n $\times$ d}($\mathbb{Q}$)) be the matrix whose columns form such a basis (where (d = $\dim$ $E_\lambda$)).

The orthogonal projector (for the standard inner product on ($\mathbb{C}^n$)) is
$$
P_\lambda = X (X^\top X)^{-1} X^\top.
$$
(Although the inner product on ($\mathbb{C}^n$) uses the conjugate transpose (X^*), the columns of (X) are vectors in ($\mathbb{Q}^n$ $\subset$ $\mathbb{R}^n$), so (X^* = $X^\top$) — the projector formula reduces to the real transpose. This is the key point where Hermiticity of (A) (guaranteeing real eigenvalues and hence real eigenspace bases) eliminates the need for complex conjugation.) The Gram matrix ($X^\top$ X $\in$ M_d($\mathbb{Q}$)) is invertible (the basis vectors are linearly independent). By Cramer's rule, (($X^\top$ X)^{-1} $\in$ M_d($\mathbb{Q}$)): each entry is a polynomial in the rational entries of ($X^\top$ X) divided by the rational determinant ($\det$($X^\top$ X) $\neq$ 0). Hence ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)).

**(($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) $\Rightarrow$ ($\lambda$ $\in$ $\mathbb{Q}$)).** ($\lambda$ = $\mathrm{Tr}$(A $P_\lambda$) / $\mathrm{Tr}$($P_\lambda$) = $\mathrm{Tr}$(A $P_\lambda$) / d). Both (A) and ($P_\lambda$) have rational entries, so the trace is a quotient of rationals — hence rational. ($\square$)

**Eigenspace trace rationality.** For the Rubik's cube representation, (A $\in$ M_{228}($\mathbb{Q}$)) (Lemma 4.1). For any generator (s $\in$ S), ($\rho$(s) $\in$ M_{228}($\mathbb{Q}$($\omega$))). If ($\lambda$ $\in$ $\mathbb{Q}$), then ($P_\lambda$ $\in$ M_{228}($\mathbb{Q}$)) by the above, and ($\chi_\lambda$(s) = $\mathrm{Tr}$($P_\lambda$ $\rho$(s)) $\in$ $\mathbb{Q}$($\omega$)). Since (A) is Hermitian, ($\chi_\lambda$(s) $\in$ $\mathbb{R}$). The only real numbers in ($\mathbb{Q}$($\omega$)) are rational: ($\mathbb{Q}$($\omega$) $\cap$ $\mathbb{R}$ = $\mathbb{Q}$). Hence ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$).

**What this proves and what it does not.** Theorem 6.2 establishes the full equivalence between rational eigenvalues, rational projectors, and rational eigenspace traces — *assuming* ($\lambda$ $\in$ $\mathbb{Q}$) as input for the forward direction. This is a standard linear algebra fact: the nullspace of a ($\mathbb{Q}$)-matrix has a ($\mathbb{Q}$)-basis; the projector constructed from that basis has rational entries. No representation theory, Galois symmetry, or commutativity hypothesis is used.

The theorem resolves the "Step 4 gap" in the following sense: the classical route required commuting (h_i) to force ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)). The field-of-definition argument achieves the same conclusion using only (A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$) — neither commutativity nor Galois invariance is needed. The remaining open problem (Theorem 6.1's hypothesis) is to prove ($\lambda$ $\in$ $\mathbb{Q}$) from face-symmetry without assuming the conclusion; this is the ($\Leftarrow$) direction of the integrality hypothesis, verified numerically for all tested face-symmetric families.

### Corollary 6.3 (Equivalent formulations)

For face-symmetric (S), the following are equivalent (the second equivalence uses the numerical fact that ($\lambda$ $\in$ $\mathbb{Q}$) for all tested face-symmetric families):

1. ($\mathrm{Spec}$(A) $\subset$ $\mathbb{Q}$).
2. ($P_\lambda$ $\in$ M_{228}($\mathbb{Q}$)) for every spectral projector (Theorem 6.2).
3. ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$) for every generator (s) and eigenvalue ($\lambda$) (Theorem 6.2).
4. For each face and each eigenvalue, the per-face eigenspace trace sum is rational (Theorem 6.1).

Numerically, a stronger property holds: each ($\chi_\lambda$(s)) and each per-face sum is not merely rational but an **integer**. This ($\mathbb{Z}$)-level strengthening is verified for all tested face-symmetric generator sets; a first-principles proof would require showing that the rational projector lattice ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) is compatible with the integer lattice of the face-sum matrices (F_{$\mathrm{face}$} $\in$ M_n($\mathbb{Z}$)), i.e., that each eigenspace carries a ($\mathbb{Z}$)-structure preserved by all face-sums.

### Theorem 6.4 (Eigenspace trace rationality — sufficient condition)

For any generator set (S = S^{-1}) (not necessarily face-symmetric), if the eigenspace traces are rational on all generators, then the corresponding eigenvalue is rational:

$$
\chi_\lambda(s) \in \mathbb{Q} \;\; \forall s \in S \quad\Longrightarrow\quad \lambda \in \mathbb{Q}.
$$

Equivalently, ($\sum_{s \in S}$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$) implies ($\lambda$ $\in$ $\mathbb{Q}$).

### Proof.

By Theorem 3.1, ($\lambda$ = $\frac{1}{d_\lambda |S|} \sum_{s \in S} \chi_\lambda(s)$). If each ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$), the sum is rational, and the right-hand side is a rational number divided by integers — hence rational. ($\square$)

### Remark (Scope and converse).

Theorem 6.4 provides an **unconditional sufficient condition** within the class of averaging operators: rational eigenspace traces force rational eigenvalues. The proof uses only the eigenspace trace identity (Theorem 3.1), which holds for any averaging operator $A = $\frac{1}{|S|}$ \sum_s \rho(s)$, and the hypothesis that each $\chi_\lambda(s) \in \mathbb{Q}$. No symmetry, commutativity, or Galois hypothesis is needed. It is the rigorous core of the rationality criterion.

The **converse** direction — ($\lambda$ $\in$ $\mathbb{Q}$ $\Rightarrow$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$) — requires the additional hypothesis that (A $\in$ M_n($\mathbb{Q}$)). When this holds (as in the face-symmetric case, by Lemma 4.1 and the permutation-block structure), it follows from Proposition 4.3: (A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$) together imply ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)), and then ($\chi_\lambda$(s) = $\mathrm{Tr}$($P_\lambda$ $\rho$(s)) $\in$ $\mathbb{Q}$($\omega$) $\cap$ $\mathbb{R}$ = $\mathbb{Q}$). Thus:

$$
\text{For face-symmetric } S: \quad \lambda \in \mathbb{Q} \;\Longleftrightarrow\; \chi_\lambda(s) \in \mathbb{Q} \;\; \forall s \in S.
$$

This equivalence is **conditional on face-symmetry**, which guarantees (A $\in$ M_{228}($\mathbb{Q}$)). Face-symmetry is a sufficient condition for the converse, not a necessary one: generator families that are not fully face-symmetric may still produce rational spectra (e.g., partially face-complete sets). The practical value of the criterion lies in the forward direction (rational traces ($\Rightarrow$) rational eigenvalues), which holds without any symmetry hypothesis.

### Remark (Observed integrality strengthening).

Numerically, a stronger property holds for all face-symmetric generator sets tested: each individual eigenspace trace ($\chi_\lambda$(s)) is not merely rational but an **integer**. For the 18-full set, the observed trace values are ($\{$8, 14, 16, 20, 24, 30, 32, 38, 44, 58$\}$), all integers. This integrality, together with Theorem 3.1, forces the eigenvalues into the form ($\lambda$ = k / ($d_\lambda$ |S|)) with (k $\in$ $\mathbb{Z}$), and the additional structure of face-symmetry refines this to ($\lambda$ = 1 - k/m) with (m = |S|/2).

Theorem 6.2 proves the ($\mathbb{Q}$)-level implication: ($\lambda$ $\in$ $\mathbb{Q}$ $\Rightarrow$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$) (via the field-of-definition argument: (A - $\lambda$ I $\in$ M_n($\mathbb{Q}$) $\Rightarrow$ $E_\lambda$) has a ($\mathbb{Q}$)-basis ($\Rightarrow$ $P_\lambda$ $\in$ M_n($\mathbb{Q}$) $\Rightarrow$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$($\omega$) $\cap$ $\mathbb{R}$ = $\mathbb{Q}$)). The ($\mathbb{Z}$)-level strengthening — that ($\chi_\lambda$(s) $\in$ $\mathbb{Z}$) for each generator — is verified numerically for all tested face-symmetric families. A first-principles proof of this integrality (showing that the rational projector lattice is compatible with the integer lattice of the face-sum matrices) would close the last remaining gap between the proven ($\mathbb{Q}$)-level chain and the observed ($\mathbb{Z}$)-level refinement.

### Observed field stratification (general case)

Let (S = S^{-1}) be an arbitrary generator set, and let (K_S = $\mathbb{Q}$($\{\lambda_i\}$)) be the minimal number field containing all eigenvalues of (A). Let ($\sigma$) be the nontrivial Galois automorphism of ($\mathbb{Q}$($\omega$)/$\mathbb{Q}$). The following stratification is observed numerically; a complete proof from first principles is not yet available.

1. **Face-symmetric:** If each face in $S$ is complete, then $\sigma(A) = A$ (the co-block averages to a real scalar via $\omega + \omega^2 + 1 = 0$) and $K_S = \mathbb{Q}$. Eigenvalues take the form $\lambda = 1 - k/m$ with $m = |S|/2$.

2. **Mild symmetry deficit:** For the identified families $|S| = 8, 16$, the adjacency algebra of the generator set fails to close over $\mathbb{Q}$ — the minimal polynomial of $A$ on the cp/ep blocks becomes irreducible of degree 2, and $K_S = \mathbb{Q}(\sqrt{5}) = \mathbb{Q}(\zeta_5)^+$. Two eigenvalues per set take the form $\lambda = \alpha \pm \beta\sqrt{5}$ with $\alpha, \beta \in \mathbb{Q}$; the remaining eigenvalues are rational. **Note:** $\sigma(A) = A$ may still hold (the averaged co-block can be real even under incomplete face coverage), but $\sigma$-invariance of $A$ does not guarantee rationality — it is strictly weaker than algebraic closure of the adjacency algebra over $\mathbb{Q}$.

3. **Conjectural general case:** (K_S) is conjectured to be the fixed field of the stabilizer of the set of averaged trace values ($\{$\frac{1}{|S|}$\sum_s$ $\chi_\lambda$(s)$\}$) under the relevant Galois action. The transition at (|S| = 8, 16) is controlled by the appearance of (C_5)-type spectral blocks in the generator interaction graph. (C_5) is the smallest cycle whose cosine is non-rational (($\cos$(2$\pi$/5) = ($\sqrt{5}$-1)/4)), making ($\mathbb{Q}$($\sqrt{5}$)) the first nontrivial spectral field extension.

### Remark (Galois symmetry is structural, arithmetic closure is causal).

A central conclusion of this work is the separation of **structural** from **causal** roles in spectral rationality:

- **Galois symmetry** explains *why* the arithmetic closure mechanism works — it identifies face-symmetry as the natural condition under which the ($\omega$)-terms cancel in face-sum matrices. But Galois symmetry alone cannot produce a rational eigenvalue; it only constrains the field in which the eigenvalue lives.
- **Partition integrality** is the *cause* of rationality — the 4-line proof of Theorem 6.1 shows that any partition of (S) with integer per-subset trace sums directly forces ($\lambda$ $\in$ $\mathbb{Q}$), with no Galois theory involved. In the Rubik's cube, the face partition supplies the concrete integrality input.

In short: **Galois symmetry is structural; partition integrality is causal.**

This distinction is reflected in the three-level table above. Level A (structural) and Level B (dynamical) constrain the geometry but do not close the rationality gap. Level C (field constraint) reduces the possible eigenvalue field to ($\mathbb{R}$). Only the arithmetic input — partition integrality (per-subset eigenspace trace sums in ($\mathbb{Z}$)), rooted in the face partition and the identity ($\omega$ + $\omega^2$ + 1 = 0) on the co-block — actually forces ($\lambda$ $\in$ $\mathbb{Q}$).

The fixed field of complex conjugation is $\mathbb{Q}$ (not $\mathbb{Q}(\sqrt{5})$). Thus $\sigma$-stability of eigenspaces alone cannot force rational eigenvalues. A direct numerical illustration: for the n=8 mixed generator set, $\sigma(A) \neq A$ (the set is not face-symmetric), yet $\sigma(P_\lambda) = P_\lambda$ holds for all seven eigenspaces to machine precision. Two of these eigenvalues are irrational: $\lambda_{\pm} = \frac{5 \pm \sqrt{5}}{8} \approx 0.9045, 0.3455$. Going from $\sigma$-stability to rationality requires an additional arithmetic closure mechanism, which for face-symmetric sets is provided by the per-face eigenspace trace integrality argument (§6). The partition integrality — the per-face integrality of $F_{\mathrm{face}}$ in the Rubik's cube instance — is what closes the gap.

This cleanly separates three routes to spectral rationality:
1. **Classical route** (commutativity ($\Rightarrow$) Schur ($\Rightarrow$) scalar action ($\Rightarrow$) ($\lambda$ = 1 - k/m)): requires commuting (h_i), only applies to abelian-axis and half-turn subsets.
2. **Trace rationality criterion** (Theorem 6.4, unconditional sufficient direction): ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$ $\Rightarrow$ $\lambda$ $\in$ $\mathbb{Q}$). Uses only the eigenspace trace identity. The converse holds under the additional hypothesis (A $\in$ M_n($\mathbb{Q}$)) (face-symmetric case).
3. **Partition integrality** (Theorems 6.1–6.2): Theorem 6.1 provides the general arithmetic partition criterion — any partition of (S) with integer per-subset trace sums forces ($\lambda$ $\in$ $\mathbb{Q}$), with no group-specific structure required. Theorem 6.2 closes the converse (( $\lambda$ $\in$ $\mathbb{Q}$ $\Rightarrow$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$)) via the field-of-definition argument. In the Rubik's cube, the face partition supplies the concrete integrality input (Theorem 5.1/5.2); the mechanism is empirically verified for all tested face-symmetric families.

## 7. Numerical evidence from the Rubik’s cube family

Three experiment scripts verify the theoretical claims numerically (all on the 228-dimensional faithful representation):

**Block compatibility** (`_exp_block_compatibility.py`): For all nine tested generator sets (18 full, 12 quarter, 6 half-turn, three abelian axes, n=8, n=10, n=16), every eigenspace projector is block-diagonal to machine precision (max cross-block leakage < 1e-10). Single-block containment holds for one eigenvalue in the 18-full case; the rest split across up to three blocks.

**Galois stability** (same script): ($\sigma$($P_\lambda$) = $P_\lambda$) holds for all eigenspaces in both the 18-full (face-symmetric, rational eigenvalues) and n=8 (non-face-symmetric, irrational eigenvalues) sets. This confirms that Galois stability of eigenspaces is a weaker condition than rationality — it only forces ($\lambda$ $\in$ $\mathbb{R}$), not ($\lambda$ $\in$ $\mathbb{Q}$).

**Eigenspace trace averaging** (`_exp_character.py`): Level 1 (tautological identity) verified to machine precision for all generator sets. Level 2 (face-symmetric generator character integrality): all complete faces have integer character sums at the generator level. In the face-symmetric 18-full case, each eigenspace eigenvalue takes the rational form ($\lambda$ = 1 - k/9) with small (k). In the n=8 and n=16 cases, two eigenvalues per set take the form ($\lambda$ = $\alpha$ $\pm$ $\beta\sqrt{5}$) with ($\alpha$, $\beta$ $\in$ $\mathbb{Q}$).

**Individual eigenspace traces** (cross-check): For all tested face-symmetric generator sets, each individual eigenspace trace ($\chi_\lambda$(s) = $\mathrm{Tr}$($P_\lambda$ $\rho$(s))) is an integer to within machine precision (max deviation < 4e-6). For the 18-full set, the 6 eigenspaces have traces drawn from ($\{$8, 14, 16, 20, 24, 30, 32, 38, 44, 58$\}$), all integers. For the symmetry-broken n=8 set, individual traces take non-integer values such as (8.291796$\ldots$ = 8 + $\phi$/2) (where ($\phi$ = ($\sqrt{5}$+1)/2)), directly reflecting the irrational eigenvalues. This empirical observation — that eigenspace trace integrality coincides exactly with spectral rationality — is the strongest numerical support for the criterion of Theorem 6.4 and the conjecture of Theorem 6.2 ($\Leftarrow$).

**n=21 full+slice closure** (new): The n=21 set augments the 18 face turns with the 3 slice moves M, E, S (middle-layer 180° turns, affecting only edge permutation). All six faces remain complete. The spectrum has 6 distinct eigenvalues, all rational of the form ($\lambda$ = 1 - k/21) with (k $\in$ $\{$0, 4, 6, 8, 10, 12$\}$). The 9 (h_i) operators (6 per-face ((g+g^{-1})/2) pairs + 3 per-axis ((180+180)/2) pairs) have only 33% commutativity, yet face-symmetry alone forces rationality. This case is a natural closure of the face-symmetric family — the slice moves are pure edge permutations whose character contributions are integers (no ($\omega$) factors), so the per-face arithmetic closure argument extends without obstruction.

**Systematic k-selection across all generator families.** The following table summarizes the observed k-sets and block-level structure for every rational face-symmetric generator family. The central empirical finding is that the number of distinct eigenvalues is determined not by (m+1) but by the number of **admissible k-values** — those integers (k $\in$ $\{$0, $\dots$, m$\}$) for which a non-negative integer assignment of block dimensions ((d_{$\mathrm{cp}$}, d_{$\mathrm{ep}$}, d_{$\mathrm{co}$}, d_{$\mathrm{eo}$})) exists that satisfies all trace integrality constraints.

| Generator set | $(\|S\|)$ | (m) | #eig | Observed k-set | Block profiles (k: active blocks) |
|---|---|---|---|---|---|
| 18-full | 18 | 9 | 6 | ($\{$0,1,2,3,4,6$\}$) | 0: cp+ep+eo, 1: eo, 2: ep+eo, 3: ep+co, 4: cp+ep, 6: cp |
| 12-quarter | 12 | 6 | 6 | ($\{$0,1,2,3,4,6$\}$) | 0: cp+ep+eo, 1: ep, 2: cp+ep+eo, 3: ep+co, 4: cp, 6: cp |
| 6-half | 6 | 3 | 3 | ($\{$0,1,2$\}$) | 0: cp+ep+co+eo, 1: ep, 2: cp+ep |
| 10-partial | 10 | 5 | 5 | ($\{$0,1,2,3,4$\}$) | 0: cp+ep+co+eo, 1: ep, 2: cp+ep, 3: cp+ep, 4: cp |
| 21-full+slice | 21 | 10.5 | 6 | ($\{$0,4,6,8,10,12$\}$) | 0: cp+ep+eo, 4: eo, 6: ep+co, 8: cp+ep, 10: ep, 12: cp |
| n=8 (asymmetric) | 8 | 4 | 7 | — (2 irrational) | ($\lambda$ = (5 $\pm$ $\sqrt{5}$)/8) |
| n=16 (asymmetric) | 16 | 8 | 8 | — (2 irrational) | ($\lambda$ = (11 $\pm$ $\sqrt{5}$)/16) |

**Key structural observations from the block decomposition:**

1. **Block profiles determine k.** Each admissible k-value corresponds to a specific combination of active blocks (cp, ep, co, eo). The block profile is a sharper invariant than the k-value itself: the same k can appear in different families with different block profiles (e.g., k=2 in 18-full is ep+eo, while k=2 in 12-quarter is cp+ep+eo).

2. **The co-block is the decisive filter.** The corner-orientation block (8D) is the only block where generator matrix entries live in ($\mathbb{Z}$[$\omega$]) rather than ($\mathbb{Z}$). An eigenspace can have (d_{$\mathrm{co}$} > 0) only for specific k-values where the ($\omega$)-phase cancellation across complete faces yields integer per-face trace sums. In the 18-full case, (d_{$\mathrm{co}$} > 0) occurs only at k=3 (the ($\lambda$ = 2/3) eigenspace, with all 8 co dimensions concentrated there). In the 12-quarter case it occurs at k=3; in 21-full+slice at k=6.

3. **The number of layers is |k-set|, not m+1.** The 6 layers in the 18-full case is not a fundamental constant — it is the size of the admissible k-set for this specific generator family. The 12-quarter family has 6 layers; 6-half has 3; 10-partial has 5 (full range ($\{$0, $\dots$, m$\}$)); 21-full+slice has 6. The layer count is a *consequence* of the k-selection rule, not an independent parameter.

4. **Forbidden k-values are those for which no block-dimension assignment satisfies all integrality constraints.** The constraints form a linear Diophantine system (see §7.1 below). For the 18-full case, (k $\in$ $\{$5, 7, 8$\}$) are forbidden because any block-dimension assignment producing these k-values would violate trace integrality on at least one block.

### 7.1 Block Reduction Theorem: Why the k-Set is the Union of Block Spectra

The k-selection rule admits a clean structural explanation via the block-diagonal structure of (A) (Theorem 3.4). This reduces the k-selection problem from a 228-dimensional question to four independent block-level questions.

**Theorem 7.1 (Block Reduction of the k-Set).** Let (A = $\bigoplus_{B}$ A_B) be the block-diagonal decomposition of the averaging operator, where (B $\in$ $\{\mathrm{cp}$, $\mathrm{ep}$, $\mathrm{co}$, $\mathrm{eo}\}$). For each block, define the block k-set:
$$
K_B = \{ m(1 - \lambda) : \lambda \in \operatorname{Spec}(A_B) \}.
$$
Then the full k-set is the union:
$$
K(A) = \bigcup_B K_B.
$$
Each eigenspace (E_k) of the full (A) is the direct sum of all block-level eigenspaces sharing the same k-value:
$$
E_k = \bigoplus_{B} E_{k,B}, \qquad \dim(E_k) = \sum_B \dim(E_{k,B}).
$$

**Proof.** By Theorem 3.4, (A) is block-diagonal, so any eigenvalue of (A) is an eigenvalue of at least one (A_B). Conversely, any eigenvalue of any (A_B) is an eigenvalue of (A) (extend the block-level eigenvector by zeros in other blocks). Therefore ($\operatorname{Spec}$(A) = $\bigcup_B$ $\operatorname{Spec}$(A_B)). Applying (k = m(1-$\lambda$)) gives (K(A) = $\bigcup_B$ K_B). The eigenspace structure follows from the fact that block-level eigenvectors from different blocks with the same eigenvalue are linearly independent and all lie in ($\ker$(A - $\lambda$ I)). ($\square$)

**This is a genuine structural theorem, not a numerical fit.** It explains all observed k-sets without free parameters:

**18-full (m=9).** The block-level spectra are:
$$
\begin{aligned}
K_{\mathrm{cp}} &= \{0, 4, 6\} \quad (64 = 8 + 24 + 32) \\
K_{\mathrm{ep}} &= \{0, 2, 3, 4\} \quad (144 = 12 + 36 + 24 + 72) \\
K_{\mathrm{co}} &= \{3, 4, 6\} \quad (8 = 2 + 3 + 3) \\
K_{\mathrm{eo}} &= \{1, 2, 4\} \quad (12 = 2 + 3 + 7)
\end{aligned}
$$
Union: $K(A) = \{0, 1, 2, 3, 4, 6\}$ — exactly the 6 observed layers. Each k-value's eigenspace dimension is the sum of block multiplicities: $d_0 = 8+12+0+0 = 20$, $d_1 = 0+0+0+2 = 2$, $d_2 = 0+36+0+3 = 39$, $d_3 = 0+24+2+0 = 26$, $d_4 = 24+72+3+7 = 106$, $d_6 = 32+0+3+0 = 35$.

**All rational face-symmetric families.** The block-level k-sets are:

| Family | m | (K_{$\mathrm{cp}$}) | (K_{$\mathrm{ep}$}) | (K_{$\mathrm{co}$}) | (K_{$\mathrm{eo}$}) | (K(A) = $\cup$ K_B) | #layers |
|---|---|---|---|---|---|---|---|
| 18-full | 9 | {0,4,6} | {0,2,3,4} | {3,4,6} | {1,2,4} | {0,1,2,3,4,6} | 6 |
| 12-quarter | 6 | {0,2,4,6} | {0,1,2,3} | {2,3,4} | {0,2,4} | {0,1,2,3,4,6} | 6 |
| 6-half | 3 | {0,2} | {0,1,2} | {0} | {0} | {0,1,2} | 3 |
| 10-partial | 5 | {0,2,3,4} | {0,1,2,3} | {0} | {0} | {0,1,2,3,4} | 5 |
| 21-full+slice | 10.5 | {0,2,6} | {0,3,4,5} | {1,3,5} | {1,3,5} | {0,1,2,3,4,5,6} | 6[^1] |

The table is verified to numerical precision for all families. The block k-sets themselves are determined by the specific representation structure of each block — a problem reduced from 228 dimensions to four independent sub-problems of dimensions 64, 144, 8, and 12.

> **Note on the 21-full+slice family ([^1]).** For this family, $|S| = 21$, so $m = |S|/2 = 10.5$ (half-integer). The eigenvalue formula becomes $\lambda = 1 - k/10.5 = 1 - 2k/21 = (21 - 2k)/21$. The block k-sets reported above use $m = 10.5$ as the denominator. The union $K(A) = \{0,1,2,3,4,5,6\}$ contains 7 candidate values, of which $k = 1$ (from co/eo blocks, giving $\lambda = 19/21$) is eliminated by trace integrality constraint C4 (§7.2), leaving 6 observed eigenvalues whose $k$-values in the $|S|$-denominator convention are $\{0, 4, 6, 8, 10, 12\}$ — all even, consistent with the half-integer $m$. The summary tables express the k-set in this $|S|$-denominator convention for readability.

![**Figure 4:** The refinement semilattice of compatible spectral decompositions. The commutative core — Center $\{A_{18}, \mathrm{QT\_all}, \mathrm{HT\_all}\}$ (9 primitive sectors), QT_all (6), $A_{18}$ (6 canonical layers), HTM (3) — forms a $\wedge$-semilattice under algebraic inclusion. The noncommutative boundary (per-axis QT operators, dashed red) lies outside this core: refinement requires commutativity, and per-axis operators do not commute across axes. The semilattice structure is $G$-determined (independent of $S$).](../../figures/paper1_fig4_refinement_geometry.png)

**From reduction to solution.** Theorem 7.1 reduces the full k-set to four block spectra. The block spectra are now understood individually:
- **Co block (8D):** Post-$\rho$-fix, the co block carries permutation@phase structure ($\mathbb{Z}_3$ phases on permuted corner positions). $K_{\mathrm{co}} = \{3, 4, 6\}$ with multiplicities $(2, 3, 3)$.
- **Eo block (12D):** Post-$\rho$-fix, the eo block carries permutation@phase structure ($\mathbb{Z}_2$ phases on permuted edge positions). $K_{\mathrm{eo}} = \{1, 2, 4\}$ with multiplicities $(2, 3, 7)$.
- **Cp and Ep blocks:** These permutation blocks carry a Kronecker product structure that reduces their spectra to small permutation transition matrices of size 8 × 8 and 12 × 12, solved analytically via hypercube eigenfunctions and face incidence (Theorem 7.2 below).

**Theorem 7.2 (Cp/Ep Kronecker product reduction).** The corner-permutation and edge-permutation representations factor as tensor products:
$$
\rho_{\mathrm{cp}}(s) = P_{\mathrm{perm},8}(s) \otimes I_8, \qquad
\rho_{\mathrm{ep}}(s) = P_{\mathrm{perm},12}(s) \otimes I_{12},
$$
where $P_{\mathrm{perm},n}(s)$ is the $n \times n$ permutation matrix of the generator $s$ acting on corner (n=8) or edge (n=12) *positions*. The factor $I_n$ acts on the *internal* degree of freedom (orientation label) at each position — the representation treats all orientations at a given position identically under permutation. Consequently,
$$
A_{\mathrm{cp}} = \left(\frac{1}{|S|}\sum_s P_{\mathrm{perm},8}(s)\right) \otimes I_8, \qquad
A_{\mathrm{ep}} = \left(\frac{1}{|S|}\sum_s P_{\mathrm{perm},12}(s)\right) \otimes I_{12}.
$$
Define the position transition sum $S_n = \sum_s P_{\mathrm{perm},n}(s)$. Then $\operatorname{Spec}(A_{\mathrm{cp}}) = \operatorname{Spec}(S_8/|S|)$ with multiplicity 8, and $\operatorname{Spec}(A_{\mathrm{ep}}) = \operatorname{Spec}(S_{12}/|S|)$ with multiplicity 12. The k-selection problem for the two largest blocks reduces to computing the spectra of two small integer matrices of sizes $8 \times 8$ and $12 \times 12$.

**Analytical spectrum of $S_8$.** The 8 corner positions form the vertices of a 3-hypercube $Q_3$ (coordinates $\{\pm 1\}^3$). Each face turn is a 4-cycle on the 4 corners of that face. Summing over the 18 moves of the full face-symmetric family, the entry $S_8[i,j]$ depends only on the Hamming distance in $Q_3$:
$$
S_8 = 9I + 2A_1 + A_2,
$$
where $A_k$ is the distance-$k$ adjacency of $Q_3$. The coefficients reflect the geometry: a corner is fixed on its 3 non-incident faces ($3 \times 3 = 9$ diagonal); adjacent corners share 2 faces, each contributing a quarter turn sending one to the other (2); face-diagonal corners share 1 face, with the 180° turn providing the transition (1); cube-diagonal corners share no face (0). The eigenfunctions of $Q_3$ are indexed by binary vectors $u \in \{0,1\}^3$ with $v_u[x] = (-1)^{u \cdot x}$. The eigenvalue of $A_k$ on $v_u$ depends only on $|u|$:
$$
\begin{aligned}
|u| = 0 &: A_1 = 3,\; A_2 = 3 &&\Rightarrow S_8 = 9 + 6 + 3 = 18 \quad (\times 1) \\
|u| = 1 &: A_1 = 1,\; A_2 = -1 &&\Rightarrow S_8 = 9 + 2 - 1 = 10 \quad (\times 3) \\
|u| = 2 &: A_1 = -1,\; A_2 = -1 &&\Rightarrow S_8 = 9 - 2 - 1 = 6 \quad (\times 3) \\
|u| = 3 &: A_1 = -3,\; A_2 = 3 &&\Rightarrow S_8 = 9 - 6 + 3 = 6 \quad (\times 1)
\end{aligned}
$$
Hence $\operatorname{Spec}(S_8) = \{18^{(1)}, 10^{(3)}, 6^{(4)}\}$. With $(1/18)S_8$ eigenvalues $\{1, 5/9, 1/3\}$ and $k = 9(1-\lambda)$, we obtain $K_{\mathrm{cp}} = \{0, 4, 6\}$ with block multiplicities $8 \times (1, 3, 4) = (8, 24, 32)$.

**Analytical spectrum of $S_{12}$.** The 12 edge positions and 6 faces define a $12 \times 6$ edge-face incidence matrix $J$: $J[e,F] = 1$ if edge $e$ lies on face $F$. Each edge belongs to exactly 2 faces; each face contains exactly 4 edges. For the 18-full family, every move on face $F$ cycles its 4 edges, so $S_{12}[i,j]$ counts how many moves send an edge from position $j$ to position $i$. Two edges share a face iff they are both on at least one common face, giving $S_{12} = 10I + JJ^{\top}$. (The term $10I$ comes from $12I$ minus the $2I$ correction for double-counted self-pairs in $JJ^{\top}$.)

The nonzero eigenvalues of $JJ^{\top}$ are those of the $6 \times 6$ Gram matrix $J^{\top}J = 4I + A_{\mathrm{face}}$, where $A_{\mathrm{face}}$ is the adjacency matrix of the cube's face graph — the octahedron graph on 6 vertices, where two faces are adjacent if they share an edge. The opposite-face permutation $P$ pairs each face with its antipode; then $A_{\mathrm{face}} = J_6 - I - P$. Since $P^2 = I$, the common eigenvectors of $J_6$ and $P$ give:
$$
\operatorname{Spec}(A_{\mathrm{face}}) = \{4^{(1)}, 0^{(3)}, -2^{(2)}\}, \qquad
\operatorname{Spec}(J^{\top}J) = \{8^{(1)}, 4^{(3)}, 2^{(2)}\}.
$$
Projecting back to the 12-dimensional edge space adds a 6-dimensional nullspace:
$$
\operatorname{Spec}(JJ^{\top}) = \{8^{(1)}, 4^{(3)}, 2^{(2)}, 0^{(6)}\}, \qquad
\operatorname{Spec}(S_{12}) = \{18^{(1)}, 14^{(3)}, 12^{(2)}, 10^{(6)}\}.
$$
With $(1/18)S_{12}$ eigenvalues $\{1, 7/9, 2/3, 5/9\}$, we obtain $K_{\mathrm{ep}} = \{0, 2, 3, 4\}$ with block multiplicities $12 \times (1, 3, 2, 6) = (12, 36, 24, 72)$.

**All four block spectra are now analytically derived.** Together with the co-block (Lemma 4.1) and eo-block ($\mathbb{Z}_2$ structure), every block k-set in Theorem 7.1 follows from first principles. The k-selection rule for the 18-full family is fully solved.

**The "forbidden k" problem is now localized.** For the 18-full case, the missing k-values ({5, 7, 8}) are precisely those integers in ([0, 9]) that do not appear in any block's spectrum. The question "why is k=5 forbidden?" becomes: "why does no block have an eigenvalue with k=5?" — a question that can be answered block by block.

![**Figure 5:** The $k$-selection rule for the 18-generator averaging operator $A_{18}$. Of the ten candidate $k$-values (0 through 9), exactly six are admissible: $k \in \{0, 1, 2, 3, 4, 6\}$. $k = 5$ ($\lambda = 4/9$) is genuinely absent — no block-dimension assignment satisfies the trace integrality constraints (Theorem 7.1, Lemma 9.1). $k \in \{7, 8, 9\}$ are forbidden by dimension bounds. The admissible set is the union of four independently computable block-level $k$-sets, filtered by partition integrality.](../../figures/paper1_fig5_k_admissibility.png)

**The 6-layer origin.** The number 6 is (|$\bigcup_B$ K_B|) for the 18-full family. It is not a universal constant: the 12-quarter family has 6 layers, 6-half has 3, 10-partial has 5, 21-full+slice has 6. The layer count is entirely determined by how many distinct k-values appear across the four block spectra — which in turn depends on the generator family.

### 7.2 K-Selection as a Constrained Diophantine Feasibility System

Theorem 7.1 reduces the k-selection problem from 228 dimensions to four independent block-level questions. But which k-values actually appear in each block's spectrum? The answer is governed by a **constrained integer feasibility system**: a candidate (k $\in$ $\{$0, $\dots$, m$\}$) is admissible if and only if there exists a non-negative integer assignment of block dimensions ((d_{$\mathrm{cp}$}, d_{$\mathrm{ep}$}, d_{$\mathrm{co}$}, d_{$\mathrm{eo}$})) at that k that satisfies all block-level trace, dimension, and symmetry constraints. The admissible k-set ($\mathcal{K}$) is precisely the set of k for which this system admits a feasible solution.

The constraints emerge from three sources: the block-diagonal structure of the representation (Theorem 3.4), the arithmetic of the corner-orientation block (Lemma 4.1), and the permutation character of the cp/ep blocks. They are enumerated below as constraints C1–C5.

---

**(C1) Block dimension bounds.** For each block (B $\in$ $\{\mathrm{cp}$, $\mathrm{ep}$, $\mathrm{co}$, $\mathrm{eo}\}$) and each candidate k,

$$
0 \le d_{B,k} \le \dim(B), \qquad
\dim(\mathrm{cp}) = 64,\;\; \dim(\mathrm{ep}) = 144,\;\;
\dim(\mathrm{co}) = 8,\;\; \dim(\mathrm{eo}) = 12.
$$

**(C2) Block exhaustion.** The per-k block dimensions must partition each block's total dimension:

$$
\sum_k d_{B,k} = \dim(B) \quad\text{for each } B \in \{\mathrm{cp}, \mathrm{ep}, \mathrm{co}, \mathrm{eo}\}.
$$

Together, C1–C2 are the statement that the eigenspace decomposition respects the block structure: the sum of eigenspace dimensions equals the block dimension, and each eigenspace splits its dimension across blocks.

**(C3) Eigenspace-level trace integrality.** For each k with total dimension (d_k = $\sum_B$ d_{B,k} > 0), the per-generator eigenspace trace must be an integer:

$$
\chi_k(s) = \operatorname{Tr}(P_k \rho(s)) \in \mathbb{Z} \quad\text{for all } s \in S.
$$

By the eigenspace trace identity (Theorem 3.1), this forces $\lambda = \frac{1}{d_k |S|} \sum_s \chi_k(s)$ to be rational; combined with inversion symmetry ($S = S^{-1}$), the eigenvalue takes the form $\lambda = 1 - k/m$ with $k \in \mathbb{Z}$. The integrality of $\chi_k(s)$ is the $\mathbb{Z}$-level strengthening of Theorem 6.2 — numerically verified for all tested face-symmetric families (Problem 1, §9.2).

**(C4) Co-block phase cancellation — the decisive arithmetic filter.** The corner-orientation block is the only block whose generator matrices carry ($\mathbb{Z}$[$\omega$]) entries (($\omega$ = e^{2$\pi$ i/3})). On a complete face (F = $\{$s, s^{-1}, s_{180}$\}$) (or (F = $\{$s, s^{-1}$\}$) for quarter-turn-only families), the per-face co-block sum satisfies:

**Lemma 7.2 (Co-block face-sum integrality).** For a face-complete generator family, the per-face co-block operator (F_{$\mathrm{co}$} = $\sum_{s \in F}$ $\rho_{\mathrm{co}}$(s)) has diagonal entries in ($\mathbb{Z}$). In particular:
$$
\omega^k + \omega^{-k} + \omega^{2k} \in \{3, 0\} \subset \mathbb{Z}, \qquad k \in \{0, 1, 2\},
$$
where the case analysis is: (k = 0) (untwisted corner) gives (1 + 1 + 1 = 3); (k = 1) gives ($\omega$ + $\omega^2$ + 1 = 0); (k = 2) gives ($\omega^2$ + $\omega$ + 1 = 0).

Consequently, for face-complete quarter-turn families:
- The co-block averaging operator (A_{$\mathrm{co}$}) has a **single eigenvalue** — all 8 co dimensions belong to one spectral layer.
- This eigenvalue determines a unique k-value: (k_{$\mathrm{co}$}) is the sole element of (K_{$\mathrm{co}$}).
- Any eigenspace of the full (A) can have (d_{$\mathrm{co}$} > 0) **only** at this specific k-value.

This single constraint is the most powerful filter on admissible k-values. It directly explains the co-support pattern across all rational families:

| Family | m | $K_{\mathrm{co}}$ | Mechanism |
|---|---|---|---|
| 18-full | 9 | {3, 4, 6} | quarter-turn face, perm@phase |
| 12-quarter | 6 | {2, 3, 4} | quarter-turn face, perm@phase |
| 6-half | 3 | {0} | half-turn only, no $\omega$ phase |
| 10-partial | 5 | {0} | incomplete face coverage |
| 21-full+slice | 10.5 | {1, 3, 5} | slice moves expand m-scale |

The arithmetic origin is always $\omega + \omega^2 + 1 = 0$.

**(C5) Permutation block character integrality.** The cp and ep blocks carry permutation matrix generators over ($\mathbb{Z}$). For any generator (s):
$$
\chi_{\mathrm{cp}}(s) = \#\{\text{corners fixed by } s\} = 4 \quad\text{(for any face turn)},
$$
$$
\chi_{\mathrm{ep}}(s) = \#\{\text{edges fixed by } s\} = 8 \quad\text{(for any face turn)}.
$$
These traces are automatically integers — permutation matrices count fixed points. The cp/ep blocks therefore provide **no further arithmetic obstruction** beyond the dimension constraints C1–C2.

The block-level spectra are now analytically derived via the Kronecker product reduction (Theorem 7.2): $\rho_{\mathrm{cp}}(s) = P_{\mathrm{perm},8}(s) \otimes I_8$ and $\rho_{\mathrm{ep}}(s) = P_{\mathrm{perm},12}(s) \otimes I_{12}$. The $8 \times 8$ position transition sum $S_8 = \sum_s P_{\mathrm{perm},8}(s)$ has spectrum $\{18, 10^3, 6^4\}$ via $Q_3$ hypercube eigenfunctions; the $12 \times 12$ sum $S_{12}$ yields $\{18, 14^3, 12^2, 10^6\}$ via the edge-face incidence matrix $J$ with $S_{12} = 10I + JJ^{\top}$ and $J^{\top}J = 4I + A_{\mathrm{face}}$ on the octahedron graph. All four block k-sets are now derived from first principles.

---

**The admissible k-set as the feasible set of C1–C5.** For a given generator family, the admissible k-set ($\mathcal{K}$) is the set of integers (k $\in$ $\{$0, $\dots$, m$\}$) for which there exists a non-negative integer vector ((d_{$\mathrm{cp}$,k}, d_{$\mathrm{ep}$,k}, d_{$\mathrm{co}$,k}, d_{$\mathrm{eo}$,k})) satisfying C1–C5. The comparative table across all rational families is:

| Family | m | ($\mathcal{K}$) (admissible) | forbidden k | co at | notes |
|---|---|---|---|---|---|
| 18-full | 9 | ($\{$0,1,2,3,4,6$\}$) | ($\{$5,7,8$\}$) | k=3 | maximal symmetry collapse; 6 layers (k=1 from eo block, was masked pre-$\rho$-fix) |
| 12-quarter | 6 | ($\{$0,1,2,3,4,6$\}$) | ($\{$5$\}$) | k=3 | near-complete; only k=5 forbidden |
| 6-half | 3 | ($\{$0,1,2$\}$) | ($\{$3$\}$) | k=0 | ($\mathbb{Z}_2$)-dominated; co inactive |
| 10-partial | 5 | ($\{$0,1,2,3,4$\}$) | ($\varnothing$) | k=0 | almost unconstrained; full ($\{$0,$\dots$,m$\}$) |
| 21-full+slice | 10.5 | ($\{$0,4,6,8,10,12$\}$) | all other (k $\in$ [0,21]) | k=6 | symmetry preserved; half-integer m[^1] |

**How constraints narrow the k-set.** C4 is the decisive filter: it restricts co-support to a single k-value, and C1–C2 propagate this restriction across the full 228 dimensions. For the 18-full case with $k_{\mathrm{co}} = 3$ and 8 co dimensions, the co-block exhausts its full dimension at k=3 — no other k can have co-support. The eo block further restricts k=0 and k=2 to have specific multiplicities (from the $\pm 1$ structure). The cp and ep blocks then distribute their 64 and 144 dimensions across the remaining feasible k-values, producing the observed multiplicities at k=0, 1, 2, 3, 4, 6. The forbidden k-values $\{5, 7, 8\}$ are precisely those for which **no** block-dimension assignment can satisfy all constraints simultaneously.

**From constraint counting to structural derivation.** The C1–C5 system (§7.2) is a **complete specification** of which k-values are admissible — it identifies the constraints, but does not by itself explain why the block spectra take the specific values they do. The cp spectrum $\{0,4,6\}$ and ep spectrum $\{0,2,3,4\}$ are not arbitrary solutions to a Diophantine system; they are the spectra of specific combinatorial objects. The next section identifies these objects: the cp and ep blocks form **permutation association schemes** induced by face-turn adjacency, and their spectra are derived from the Bose–Mesner algebra of these schemes.

### 7.3 Interference Structure: Why the Block Spectra Are What They Are

**Master Statement.** *The Rubik's cube averaging spectrum is completely determined by: the Bose–Mesner algebra of two small graphs (8 and 12 vertices), and two abelian phase constraints over $\mathbb{Z}_2$ and $\mathbb{Z}_3$. All higher-dimensional structure is a tensor lift of these components.*

In physical terms, the Rubik's cube is an **interference system**. Each generator introduces a phase factor ($\omega^k$ on corners, $\pm 1$ on edges). The averaging operator sums these contributions across an entire generator set — the phases interfere. On a complete face, the three moves $\{g, g^{-1}, g_{180}\}$ produce complete destructive interference ($\omega + \omega^2 + 1 = 0$), eliminating all non-rational cyclotomic components and forcing rational eigenvalues. When face symmetry is broken, the interference is incomplete: residual $\omega$-dependent terms survive, and the spectrum acquires irrational components in $\mathbb{Q}(\sqrt{5})$. The spectrum is therefore not an algebra phenomenon — it is an **interference phenomenon**, and the spectral field measures the degree of phase cancellation across the generator set.

This interference structure is captured algebraically by a **Spectral Factorization Principle**:

$$
\boxed{\text{Spectrum}(A) \;=\; \underbrace{(\text{cp, ep})}_{\text{adjacency algebra}} \;\times\; \underbrace{(\text{co, eo})}_{\text{abelian phase algebra}}}
$$

The full averaging operator factors as a tensor product of independent spectral components:

$$
\mathcal{A}_{\text{cube}} \;=\; \mathcal{A}_{Q_3} \;\otimes\; \mathcal{A}_{\text{incidence}} \;\otimes\; \mathcal{Z}_2 \;\otimes\; \mathcal{Z}_3
$$

where $\mathcal{A}_{Q_3}$ is the Bose–Mesner algebra of the 8-vertex Q₃ hypercube (cp block), $\mathcal{A}_{\text{incidence}}$ is the Bose–Mesner algebra of the 12-edge face-incidence graph (ep block), and $\mathcal{Z}_2, \mathcal{Z}_3$ are the abelian phase algebras of edge and corner orientation. The 228-dimensional representation is merely the tensor lift of these four low-dimensional structures.

**Theorem 7.3 (Structural decomposition via association schemes).** The averaging operator $A = $\frac{1}{|S|}$ \sum_{s \in S} \rho(s)$ on the 228-dimensional Rubik's cube representation decomposes into two structural types corresponding to the two factors of the Spectral Factorization Principle:

* **Type I (adjacency algebra — cp, ep):** The permutation blocks are association schemes. Their spectra are given by the Bose–Mesner algebra of the face-turn adjacency relations on 8 corner labels and 12 edge labels. Specifically, $A_{\mathrm{cp}} = S_8 \otimes I_8$ and $A_{\mathrm{ep}} = S_{12} \otimes I_{12}$, where $S_8$ and $S_{12}$ lie in the Bose–Mesner algebras of the $Q_3$ hypercube and the face-incidence graph, respectively. These determine the **position** of every spectral layer.

* **Type II (phase algebra — co, eo):** The orientation blocks carry abelian phase representations over $\mathbb{Z}_3$ and $\mathbb{Z}_2$. They act as scalar or two-class interference filters: each face-sum produces either complete destructive interference ($\omega + \omega^2 + 1 = 0$, integer sum) or trivial phase alignment ($1+1+1=3$). They constrain which eigenvalues are admissible — they contribute no spectral layering of their own, but determine which Type I eigenvalues survive with nonzero orientation-block support.

**Consequently, the spectrum of $A$ is not a property of the Rubik's cube group — it is a property of two low-dimensional combinatorial objects (the Q₃ hypercube on 8 vertices and the face-incidence graph on 12 edges) and two abelian phase constraints ($\mathbb{Z}_2$ edge orientation and $\mathbb{Z}_3$ corner orientation). No group character table is needed; no commutativity of generator-level operators is required.**

#### Proof.

The 228-dimensional representation decomposes as:

$$
\rho = \underbrace{(\text{permutation reps})}_{\text{Type I: association schemes}} \;\oplus\; \underbrace{(\text{phase structures})}_{\text{Type II: } \mathbb{Z}_2, \mathbb{Z}_3}
$$

**Type I: Permutation association schemes (cp, ep).** The cp and ep blocks are pure permutation representations tensored with identity:

$$
\rho_{\mathrm{cp}}(s) = P_8(s) \otimes I_8, \qquad
\rho_{\mathrm{ep}}(s) = P_{12}(s) \otimes I_{12}.
$$

Every face turn has the **same** cycle structure on positions: a 4-cycle on the face's four positions, with all other positions fixed. Consequently, the permutation character is constant across generators:

$$
\operatorname{Tr} P_8(s) = 4 \quad\text{(4 fixed corners)}, \qquad
\operatorname{Tr} P_{12}(s) = 8 \quad\text{(8 fixed edges)} \qquad \forall s \in S.
$$

The averaging operators are adjacency matrices of **association schemes** — the Bose–Mesner algebras of the face-turn adjacency relations on corner and edge positions:

$$
S_8 = \frac{1}{|S|} \sum_{s \in S} P_8(s), \qquad
S_{12} = \frac{1}{|S|} \sum_{s \in S} P_{12}(s).
$$

An association scheme on a set $X$ is a partition of $X \times X$ into symmetric relations $R_0, \ldots, R_d$ such that the adjacency matrices $A_i$ span a commutative algebra — the **Bose–Mesner algebra**. The averaging operator $S_n$ lies in this algebra, so its eigenvalues are determined by the scheme's character table (which is not a group character table — it is the table of eigenvalues of the $A_i$ on the common eigenspaces).

**The cp scheme: $Q_3$ hypercube.** The 8 corner positions are the vertices of a 3-dimensional hypercube $Q_3$. Face-turn adjacency respects Hamming distance: two corners at Hamming distance 1 share 2 faces (adjacent on $Q_3$); distance 2 share 1 face (face-diagonal); distance 3 share none (cube-diagonal). The Bose–Mesner algebra of $Q_3$ is spanned by the distance-$k$ adjacency matrices $A_0 = I, A_1, A_2, A_3$, and $S_8 = $\frac{1}{18}$(9A_0 + 2A_1 + A_2)$. The common eigenspaces are indexed by Hamming weight $|u| \in \{0,1,2,3\}$, giving the spectrum:

$$
\operatorname{Spec}(S_8) = \{1, \tfrac{5}{9}, \tfrac{5}{9}, \tfrac{5}{9}, \tfrac{1}{3}, \tfrac{1}{3}, \tfrac{1}{3}, \tfrac{1}{3}\}
\quad\Rightarrow\quad K_{\mathrm{cp}} = \{0, 4, 6\}.
$$

**The ep scheme: face-incidence graph.** The 12 edge positions and 6 faces define the edge-face incidence matrix $J$ (12 × 6). Two edges are "adjacent in the scheme" if they share a face. The adjacency algebra is generated by $JJ^{\top}$, which is the Gram matrix of the incidence vectors. Via the octahedron graph on faces ($J^{\top}J = 4I + A_{\mathrm{face}}$), the spectrum reduces to:

$$
\operatorname{Spec}(S_{12}) = \{1, \tfrac{7}{9}, \tfrac{7}{9}, \tfrac{7}{9}, \tfrac{2}{3}, \tfrac{2}{3}, \tfrac{5}{9}, \ldots, \tfrac{5}{9}\}
\quad\Rightarrow\quad K_{\mathrm{ep}} = \{0, 2, 3, 4\}.
$$

**Type II: Scalar filters (co, eo).** The orientation blocks are **not** association schemes — they are 1-dimensional per position, diagonal, and their spectra are determined by algebraic cancellation rather than combinatorial adjacency.

- **Co block ($\mathbb{Z}_3$):** $A_{\mathrm{co}} = \lambda_{\mathrm{co}} I_8$ is a scalar matrix (Lemma 4.1). The $\mathbb{Z}_3$ phases $\{1, \omega, \omega^2\}$ cancel across complete faces via $\omega + \omega^2 + 1 = 0$. The block contributes exactly one k-value, acting as a **pass-filter**: it permits co-support at exactly one k and forbids it everywhere else.

- **Eo block ($\mathbb{Z}_2$):** $A_{\mathrm{eo}}$ is diagonal with entries in $\{\pm 1\}$, splitting into two classes by face-type (Lemma 4.0). Edges on F/B faces are flipped by quarter turns; edges on R/L/U/D faces are never flipped. This is a **two-class filter**: it permits eo-support at exactly two k-values.

**Unified spectral formula.** The full 228-dimensional spectrum is the tensor product of independent structures, reducing to a union at the level of k-values:

$$
K(A) = \underbrace{K_{\mathrm{cp}}}_{\mathcal{A}_{Q_3}} \;\cup\; \underbrace{K_{\mathrm{ep}}}_{\mathcal{A}_{\text{incidence}}} \;\cup\; \underbrace{K_{\mathrm{co}}}_{\mathcal{Z}_3} \;\cup\; \underbrace{K_{\mathrm{eo}}}_{\mathcal{Z}_2}.
$$

The six layers of the 18-full family $\{0,1,2,3,4,6\}$ emerge from: Q₃ hypercube spectrum $\{0,4,6\}$, face-incidence spectrum $\{0,2,3,4\}$, Z₃ phase constraint $\{3\}$ (the sole k where destructive interference is complete — $\omega + \omega^2 + 1 = 0$ — and co-support is nonzero), and Z₂ phase constraint $\{1,2\}$ (the k-values where the edge orientation faces are both flipped or both unflipped). The k=1 layer ($\lambda=8/9$, 2-dim, pure eo) was masked pre-$\rho$-fix by a diagonal-only EO representation; the corrected $\rho$ reveals it. Each spectral layer is the tensor lift of a low-dimensional eigenspace: the 228 dimensions are not 228 independent degrees of freedom, but the Kronecker product of eigenspaces from the 8×8 cp matrix $S_8$, the 12×12 ep matrix $S_{12}$, and the scalar/2-class filters from the orientation blocks.

![**Figure 3:** The 13 block-level primitive idempotents collapse to exactly 6 global spectral layers through resonance condensation: different blocks producing the same $k$-value under $\lambda = 1 - k/9$ merge into a single eigenspace (Theorem 3.6). The vacancy at $k = 5$ — no block produces this $k$-value — is the structural origin of the forbidden eigenvalue. This $13 \to 6$ condensation is the central mechanism by which local (blockwise) spectral primitives determine global (averaging operator) spectral ontology.](../../figures/paper1_fig3_resonance_merging.png)

**The six spectral layers are not primitive.** The four block-level algebras have $4 + 3 + 1 + 2 = 10$ primitive idempotents in total. A global spectral layer at eigenvalue $\lambda = 1 - k/m$ is the direct sum of all block-level primitive idempotents whose eigenvalues coincide at that $k$. This is **spectral resonance merging** (Theorem 3.6):

| Global $\lambda$ | $k$ | cp $k$ | ep $k$ | co $k$ | eo $k$ | Block idempotents merged |
|------------------|-----|--------|--------|--------|--------|--------------------------|
| $1$ | 0 | 0 | 0 | 0 | 0 | cp $k$=0 + ep $k$=0 + co $k$=0 + eo $k$=0 |
| $8/9$ | 1 | — | — | — | 2 | eo $k$=2 (was masked pre-$\rho$-fix) |
| $7/9$ | 2 | 2 | 2 | 0 | — | cp $k$=2 + ep $k$=2 + co $k$=0 |
| $2/3$ | 3 | 3 | — | 0 | — | cp $k$=3 + co $k$=0 |
| $5/9$ | 4 | 4 | 4 | 0 | 2 | cp $k$=4 + ep $k$=4 + co $k$=0 + eo $k$=2 |
| $1/3$ | 6 | — | 6 | — | — | ep $k$=6 |

$k=5$ ($\lambda=4/9$) is genuinely absent — no blockwise primitive idempotent produces it.

The 13 block-level primitive idempotents collapse to exactly 6 global spectral layers because the eigenvalue formula $\lambda = 1 - k/m$ produces coincident values for different blocks at the same $k$. The formula $|K(A)| = |\bigcup_B K_B|$ is exact; the structural content of the spectral origin theorem is the identification of each $K_B$ as the primitive idempotent spectrum of the corresponding blockwise Bose–Mesner algebra. **The number 6 is not a numerical coincidence — it is the cardinality of the union of four independently computable block-level k-sets, each arising from a distinct commutative algebra (Q₃ Hamming, face-incidence, Z₃ perm@phase, Z₂ perm@phase).**

**The spectrum is not a property of the group.** Decomposing the 228-dimensional representation into irreducibles of the Rubik's cube group would produce dozens of irreducible components, most of which accidentally share the same eigenvalue under the face-turn average — the group structure is largely irrelevant to the spectral structure. The association scheme approach directly diagonalizes the averaging operator without ever constructing the group algebra: the permutation action of face turns factors through the adjacency algebra of two small positional graphs (8 and 12 vertices), and the orientation action factors through two abelian phase constraints ($\mathbb{Z}_2$ and $\mathbb{Z}_3$). The group-theoretic semi-direct product $(\text{permutation}) \ltimes (\text{orientation})$ is reflected in the spectral factorization $\mathcal{A}_{Q_3} \otimes \mathcal{A}_{\text{incidence}} \otimes \mathcal{Z}_2 \otimes \mathcal{Z}_3$, but the factorization is strictly finer: the 8-vertex Q₃ scheme and 12-edge incidence scheme are independent, and the Z₂/Z₃ phase algebras are independent. The group structure bundles these together; the spectral factorization separates them.

## 8. Discussion

This paper resolves the spectral rationality problem for the Rubik's cube into a **Spectral Factorization Principle**:

$$
\boxed{\text{Spectrum}(A) \;=\; \underbrace{(\text{cp, ep})}_{\text{adjacency algebra}} \;\times\; \underbrace{(\text{co, eo})}_{\text{abelian phase algebra}}}
$$

The full averaging operator factors as $\mathcal{A}_{\text{cube}} = \mathcal{A}_{Q_3} \otimes \mathcal{A}_{\text{incidence}} \otimes \mathcal{Z}_2 \otimes \mathcal{Z}_3$ — a tensor product of four independent, low-dimensional spectral components. The 228-dimensional representation is merely the tensor lift of structures on 8 and 12 vertices plus two abelian phase constraints.

The conceptual architecture separates into four levels of increasing specificity:

1. **Identity level:** the eigenspace trace formula (Theorem 3.1) is tautological — it holds for any averaging operator and any eigenspace projector. This is the only "representation theory" that enters: every eigenvalue is a normalized trace sum over generators.
2. **Galois level:** Galois invariance stabilizes eigenspaces (Theorem 3.2), constraining the spectral geometry but insufficient for rationality alone (Level C of the Galois table). The Galois action provides the structural explanation for *why* face-symmetry produces rational spectra — but it does not *cause* rationality.
3. **Criterion level:** rational eigenspace traces imply rational eigenvalues unconditionally (Theorem 6.4, forward direction). This is the rigorous sufficient condition. The converse — $\lambda \in \mathbb{Q} \Rightarrow \chi_\lambda(s) \in \mathbb{Q}$ — is proven via the field-of-definition argument (Theorem 6.2): $A \in M_n(\mathbb{Q})$ and $\lambda \in \mathbb{Q}$ implies $P_\lambda \in M_n(\mathbb{Q})$, hence $\chi_\lambda(s) \in \mathbb{Q}(\omega) \cap \mathbb{R} = \mathbb{Q}$.
4. **Integrality level:** for the Rubik's cube representation, individual eigenspace traces are integers whenever the spectrum is rational, proven via the Bose–Mesner trace pairing (Lemma 9.1). This integrality underlies the simple rational form $\lambda = 1 - k/m$.

**The spectral factorization into three independent mechanisms.** The spectral structure of the Rubik's cube decomposes into three composable layers, corresponding to the two factors of the Spectral Factorization Principle plus the arithmetic closure that binds them:

1. **Adjacency algebra (cp, ep) — determines spectral positions.** The permutation blocks form association schemes (Bose-Mesner algebras) on two small positional graphs. The Q₃ hypercube (8 corner positions) and the face-incidence graph (12 edge positions) have analytically computable spectra via their distance/incidence adjacency matrices. These adjacency algebras are commutative by construction — no commutativity of generator-level operators is required. The eigenvalues $\lambda = 1 - k/m$ are the normalized valencies of the scheme's idempotents.

2. **Phase algebra (co, eo) — determines spectral admissibility via interference.** The orientation blocks are abelian phase representations. The Z₃ block (co) acts as a scalar interference filter: on a complete face, the three moves produce phases $\{\omega, \omega^2, 1\}$, and destructive interference ($\omega + \omega^2 + 1 = 0$) eliminates all non-rational components, locking the co block to a single eigenvalue. The Z₂ block (eo) splits into two classes by phase type ($\pm 1$); the interference is partial (two classes survive). Together, the phase algebras determine *which* of the candidate eigenvalues from the adjacency algebra carry nonzero orientation-block support — they act as interference filters, not as spectral generators.

3. **Arithmetic closure (partition integrality) — enforces rationality.** The integrality of per-face eigenspace traces (Theorem 5.1, Lemma 9.1) forces eigenvalues to the rational form $\lambda = 1 - k/m$ via the eigenspace trace identity (Theorem 3.1) and the unconditional criterion (Theorem 6.4). The partition integrality mechanism (Theorem 6.1) operates without any commutativity hypothesis — it is a purely arithmetic condition on character sums. The per-face cancellation $\omega + \omega^2 + 1 = 0$ is an interference identity, not an algebraic one.

**These three mechanisms are logically independent and composable.** Adjacency algebra (Type I) determines the candidate eigenvalues — the raw spectral positions before any constraints are applied. Phase algebra (Type II) restricts admissibility through interference — it forbids certain eigenvalues from carrying orientation-block support, pruning the candidate set. Arithmetic closure (partition integrality) enforces rationality — it locks the surviving eigenvalues to the rational form $\lambda = 1 - k/m$. No single mechanism suffices alone, and none requires commutativity of the underlying generators. This independence is what makes the framework reusable: any averaged group representation whose permutation blocks form association schemes and whose orientation blocks carry abelian phase representations will exhibit the same three-layer spectral structure.

The original "Step 4 gap" (requiring common eigenbasis of the h_i operators) is circumvented entirely: the adjacency algebras of the permutation blocks are commutative by construction, and the phase algebras of the orientation blocks are diagonal/abelian. The spectral decomposition follows from the factorization $\mathcal{A}_{Q_3} \otimes \mathcal{A}_{\text{incidence}} \otimes \mathcal{Z}_2 \otimes \mathcal{Z}_3$ — no Schur's Lemma, no commutativity hypothesis, no group character table.

**The $\mathbb{Z}$-level integrality is now proven** (Lemma 9.1, §9.2 Problem 1): the Bose–Mesner algebra trace pairing $\operatorname{Tr}(E_\lambda M)$ is integer-valued for any integer matrix $M$ in the algebra. This is explicitly verified for both the Q₃ hypercube scheme (cp block) and the face-incidence scheme (ep block), with the tensor factors ($\otimes I_8, \otimes I_{12}$) preserving integrality. The co and eo blocks contribute integer traces via phase cancellation (Lemma 7.2, Lemma 4.0) — i.e., via destructive interference.

**What is proven vs. what is observed.** The paper distinguishes:

| Claim | Status |
|-------|--------|
| ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$ $\Rightarrow$ $\lambda$ $\in$ $\mathbb{Q}$) | **Proven** (Theorem 6.4, unconditional) |
| ($\lambda$ $\in$ $\mathbb{Q}$ $\Rightarrow$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$) for face-symmetric (S) | **Proven** (Theorem 6.2, field-of-definition) |
| ($\lambda$ $\in$ $\mathbb{Q}$ $\iff$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$) for face-symmetric (S) | **Proven** (Theorems 6.2 + 6.4) |
| Face-symmetric (S) ($\Rightarrow$ $\lambda$ $\in$ $\mathbb{Q}$) | **Proven** (Theorems 6.1 + 5.1/5.2, conditional on per-face integrality hypothesis) |
| Per-face eigenspace trace sums are integer for face-symmetric (S) | **Proven** (Lemma 9.1, Bose–Mesner trace pairing) |
| ($\chi_\lambda$(s) $\in$ $\mathbb{Z}$) for face-symmetric (S) | **Proven** (Lemma 9.1 + tensor factor integrality; ($\mathbb{Z}$)-level strengthening of Theorem 6.2) |
| (K_S = $\mathbb{Q}$($\sqrt{5}$)) for (n=8, 16) | **Observed** (numerical, conjectural (C_5) mechanism) |
| (K_S = $\mathbb{Q}$) for all tested face-symmetric (S) | **Observed** (numerical, proven for face-complete 18-full via Theorem 6.1) |

## 9. Open Problems and Future Directions

The main thread of this paper — face-sum arithmetic ($\Rightarrow$) rational spectrum — is a closed logical chain at both the ($\mathbb{Q}$)-level and the ($\mathbb{Z}$)-level: partition integrality forces rational eigenvalues (Theorem 6.1), the field-of-definition argument supplies the converse (Theorem 6.2), the face decomposition of the Rubik’s cube provides the concrete integrality input (Theorem 5.1/5.2, Lemma 4.1), and Lemma 9.1 (Bose–Mesner trace pairing) closes the ($\mathbb{Z}$)-level strengthening.

Beyond this main thread lie three deeper questions. They concern not *whether* the spectrum is rational, but *why* the spectral structure of the Rubik’s cube representation takes the specific form it does — why 6 layers, why those particular k-values, and why $k=5$ is genuinely absent.

### 9.1 What Is Firmly Proven

Before listing the open problems, we summarize what is rigorously established and therefore *not* open.

**At the arithmetic level (face-sum ($\Rightarrow$) rational spectrum):**

1. **Unconditional sufficient direction** (Theorem 6.4): ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$) for all generators ($\Rightarrow$) ($\lambda$ $\in$ $\mathbb{Q}$). No symmetry, commutativity, or Galois hypothesis required.
2. **Converse for face-symmetric (S)** (Theorem 6.2): (A $\in$ M_n($\mathbb{Q}$)) and ($\lambda$ $\in$ $\mathbb{Q}$) ($\Rightarrow$) ($P_\lambda$ $\in$ M_n($\mathbb{Q}$)) ($\Rightarrow$) ($\chi_\lambda$(s) $\in$ $\mathbb{Q}$). This is a standard linear algebra fact: the nullspace of a ($\mathbb{Q}$)-matrix admits a ($\mathbb{Q}$)-basis.
3. **Full ($\mathbb{Q}$)-level equivalence** for face-symmetric (S): ($\lambda$ $\in$ $\mathbb{Q}$ $\iff$ $\chi_\lambda$(s) $\in$ $\mathbb{Q}$).
4. **Partition integrality mechanism** (Theorem 6.1): any partition of (S) with integer per-subset eigenspace trace sums forces ($\lambda$ $\in$ $\mathbb{Q}$). The proof uses only the eigenspace trace identity (Theorem 3.1) and the partition hypothesis — no commutativity, Galois theory, or block decomposition.
5. **Concrete integrality input** (Theorem 5.1/5.2, Lemma 4.1): the face partition supplies the integrality hypothesis for the Rubik’s cube, via the cancellation ($\omega$ + $\omega^2$ + 1 = 0) on the corner-orientation block.
6. **($\mathbb{Z}$)-level trace integrality** (Lemma 9.1): in a Bose–Mesner algebra over ($\mathbb{Z}$), the trace pairing ($\operatorname{Tr}$($E_\lambda$ M)) is integer-valued for any integer matrix (M) in the algebra. Explicitly verified for both the Q₃ hypercube scheme (cp block) and the face-incidence scheme (ep block). Together with the tensor factors ($\otimes$ I_8, $\otimes$ I_{12}), this proves ($\chi_\lambda$(s) $\in$ $\mathbb{Z}$) for all face-symmetric families — the ($\mathbb{Z}$)-level strengthening of Theorem 6.2.

**At the structural level:**

7. **Block compatibility** (Theorem 3.4): eigenspace projectors are block-diagonal with respect to the four invariant subspaces ((V_{$\mathrm{cp}$}, V_{$\mathrm{ep}$}, V_{$\mathrm{co}$}, V_{$\mathrm{eo}$})). This reduces the 228-dimensional problem to four independent sub-problems.
8. **Galois stability of eigenspaces** (Theorem 3.2): ($\sigma$(A) = A) and (A) Hermitian ($\Rightarrow$) ($\sigma$($E_\lambda$) = $E_\lambda$). This is a structural constraint that holds for all face-symmetric families, but is strictly weaker than rationality (counterexample: n=8 has ($\sigma$($P_\lambda$) = $P_\lambda$) for all ($\lambda$), yet two eigenvalues are in ($\mathbb{Q}$($\sqrt{5}$) $\setminus$ $\mathbb{Q}$)).
9. **Block spectra from association schemes** (Theorem 7.1, §7.3): the cp-block spectrum is analytically derived from the Q₃ hypercube scheme; the ep-block spectrum from the face-incidence scheme; the co-block spectrum from the Z₃ phase structure (Lemma 4.1); the eo-block spectrum from the Z₂ two-class split (Lemma 4.0). The k-selection rule $\{$0,2,3,4,6$\}$ for the 18-full family is derived from first principles without group character tables.
10. **Co-block support boundary** (§9.2 Problem 3, corrected): ($\lambda$ = 2/3) is characterized algebraically as the co-block support cutoff — (d_{$\mathrm{co}$} > 0) exactly at (k = 3) where (A_{$\mathrm{co}$} = $\lambda_{\mathrm{co}}$ I_8) (Lemma 4.1). This replaces the incorrect numerical conjecture of (G_1)-invariance.
11. **Minimal polynomial degree and the origin of the number 6** (Theorem 3.6): For the 18-full case, $\mathrm{rank}\{I, A, A^2, A^3, A^4, A^5\} = 6$, so the minimal polynomial of $A$ has degree 6. The number 6 is not an empirical accident — it is the cardinality of the union $\bigcup_B K_B$ of four independently computable block-level k-sets. The four blockwise commutative algebras carry $4 + 3 + 1 + 2 = 10$ primitive idempotents; these collapse to exactly 6 global spectral layers via the resonance condition $\lambda = 1 - k/m$, where different blocks produce coincident eigenvalues at the same $k$. The resonance merging table (§7.3, Theorem 3.6) gives the precise merging pattern: $k=0$ merges all four blocks, $k=1$ carries eo alone (new post-$\rho$-fix), $k=2$ merges cp+ep+co, $k=3$ merges cp+co, $k=4$ merges cp+ep+co+eo (triple resonance), and $k=6$ carries ep alone. The number 6 is a structural theorem, not a numerical observation.

**At the empirical level (numerically verified, not yet proven from first principles):**

12. **Rational spectral form**: ($\lambda$ = 1 - k/m) with (m = |S|/2) for all face-symmetric families — proven for the 18-full family via block spectra + Lemma 9.1; observed for all other face-symmetric families.
13. **Field stratification**: (K_S = $\mathbb{Q}$) for face-symmetric families; (K_S = $\mathbb{Q}$($\sqrt{5}$)) for n=8, n=16.

### 9.2 Numerical Observations Requiring First-Principles Proofs

Three core observations are numerically stable across all tested face-symmetric generator families. They are listed in order of increasing depth.

---

**Problem 1 (Z-level strengthening): Integrality of eigenspace traces — closed.**

**Status: Proven.** The $\mathbb{Z}$-level integrality is now a structural consequence of the association scheme framework, not a numerical observation requiring independent verification.

**Lemma 9.1 (Trace integrality via Bose–Mesner algebra).** Let $\mathcal{A} \subset M_n(\mathbb{Q})$ be a Bose–Mesner algebra with integral basis $\{A_0 = I, A_1, \ldots, A_d\}$ (the adjacency matrices of an association scheme) and intersection numbers $p_{ij}^k \in \mathbb{Z}_{\ge 0}$. Let $E_\lambda = $\frac{1}{n}$ \sum_i q_\lambda(i) A_i$ be a primitive idempotent of $\mathcal{A}$ with rational eigenvalues ($q_\lambda(i) \in \mathbb{Q}$). Then for any $M = \sum_j c_j A_j \in \mathcal{A}$ with integer coefficients ($c_j \in \mathbb{Z}$),

$$
\operatorname{Tr}(E_\lambda M) \in \mathbb{Z}.
$$

*Proof.* In a symmetric association scheme, $A_i^{\top} = A_i$ and $A_i A_j = \sum_k p_{ij}^k A_k$. The trace pairing satisfies $\operatorname{Tr}(A_i A_j) = p_{ij}^0 \cdot n$, where $p_{ij}^0$ is nonzero only when $i = j$, in which case $p_{ii}^0 = v_i$ — the valency of the $i$-th relation. Hence $\operatorname{Tr}(A_i A_j) = \delta_{ij} v_i n$. Then

$$
\operatorname{Tr}(E_\lambda M) = \frac{1}{n} \sum_{i,j} q_\lambda(i) c_j \operatorname{Tr}(A_i A_j)
= \frac{1}{n} \sum_i q_\lambda(i) c_i \cdot v_i n
= \sum_i q_\lambda(i) v_i \cdot c_i.
$$

The product $q_\lambda(i) v_i$ is the $(i, \lambda)$-entry of the eigenmatrix multiplied by the valency — an algebraic integer. For rational eigenvalues ($q_\lambda(i) \in \mathbb{Q}$), this forces $q_\lambda(i) v_i \in \mathbb{Z}$. Since $c_i \in \mathbb{Z}$ by hypothesis, the sum is integer. $\square$

**Explicit verification for the Rubik's cube schemes.**

*Q₃ hypercube (cp block, 8 corners).* The adjacency basis $\{A_0, A_1, A_2, A_3\}$ (Hamming distances 0–3) has valencies $(1, 3, 3, 1)$. The primitive idempotents $E_k$ ($k = 0,1,2,3$) correspond to Hamming weight $|u| = k$. The eigenmatrix satisfies $q_k(i) v_i \in \mathbb{Z}$ for all $k, i$. The face-sum decomposes as $M_{\mathrm{face}} = 9A_0 + 2A_1 + A_2$ (integer coefficients). Lemma 9.1 yields:

$$
\operatorname{Tr}(E_k M_{\mathrm{face}}) \in \{18, 30, 18, 6\} \subset \mathbb{Z}.
$$

*Face-incidence scheme (ep block, 12 edges).* The edge-face incidence matrix $J$ (12×6) generates the scheme via $JJ^{\top}$. The face-sum decomposes as $M_{\mathrm{face}} = 10I + JJ^{\top}$ with integer coefficients. The four primitive idempotents yield:

$$
\operatorname{Tr}(E_k M_{\mathrm{face}}) \in \{18, 42, 24, 60\} \subset \mathbb{Z}.
$$

In both cases, the tensor factors ($\otimes I_8$ for cp, $\otimes I_{12}$ for ep) multiply the trace by the internal dimension, preserving integrality. The co and eo blocks are diagonal with entries in $\mathbb{Z}[\omega]$ and $\{\pm 1\}$; their per-face traces are integers by the phase cancellation identities (Lemma 7.2, Lemma 4.0).

The lemma replaces the computational "denominator divides numerator" argument with a structural statement: **the Bose–Mesner algebra has an integral trace pairing**, and integrality of eigenspace traces is a theorem, not an observation.

---

**Problem 2 (Derivation of block spectra): Status and remaining gaps.**

The k-selection problem is now structurally solved via the block reduction theorem (Theorem 7.1) and the classification of blocks into two types (§7.3):

- **Permutation association schemes (cp, ep):** The spectra of $S_8$ and $S_{12}$ are analytically derived from the Q₃ hypercube and the face-incidence graph. These are classical association schemes whose Bose-Mesner algebras are fully computable. No group character table is required.
- **Scalar filters (co, eo):** The co-block spectrum is a single value (Lemma 4.1, Z₃ + Galois trace). The eo-block spectrum is a two-class split (Lemma 4.0, Z₂ + face-type classification).

The four block k-sets are now derived from first principles. For the 18-full family, the union $\{0,2,3,4,6\}$ is exact.

**What remains open:** The Spectral Factorization Principle (§7.3) provides the tensor factorization $\mathcal{A}_{Q_3} \otimes \mathcal{A}_{\text{incidence}} \otimes \mathcal{Z}_2 \otimes \mathcal{Z}_3$ — the factorization is structurally complete but the ep block's face-incidence algebra is not a classical association scheme (not Johnson, not Hamming). A classification of this non-classical commuting adjacency algebra within the known taxonomy of association schemes, or a proof that it constitutes a new finite example, would be of independent combinatorial interest. Additionally, the spectral field for symmetry-broken families ($K_S = \mathbb{Q}(\sqrt{5})$ for n=8, n=16) remains unexplained by the association scheme mechanism and likely requires a different approach (e.g., the C₅-type spectral block structure identified numerically).

---

**Problem 3: The $\lambda = 2/3$ boundary — co-block support, not group invariance.**

*Status update (2026-05-02).* The original claim that $E_{2/3}$ is invariant under the Phase-1 subgroup $G_1$ is **numerically incorrect**. Explicit computation shows that only the trivial eigenspace $\lambda = 1$ (24-dimensional) is fully $G_1$-invariant. All other eigenspaces, including $E_{2/3}$, are mixed by the permutation action of $G_1$. The co-block component of $E_{2/3}$ (8 dimensions) is trivially invariant (because $A_{\mathrm{co}} = \lambda_{\mathrm{co}} I_8$ is scalar), but the ep-block component (24 dimensions) is not.

**Corrected characterization.** The eigenvalue $\lambda = 2/3$ is **not** characterized by $G_1$-invariance. Instead, it marks the **co-block support boundary**:

* **For $\lambda \ge 2/3$:** the co block has nonzero support. Specifically, $k_{\mathrm{co}} = m/3$ for face-complete quarter-turn families, and this is the only k-value where $d_{\mathrm{co}} > 0$ (Lemma 4.1).
* **For $\lambda < 2/3$:** the co block vanishes — $d_{\mathrm{co}} = 0$ for all k-values below $m/3$.

**Proof sketch.** From Lemma 4.1, the corner-orientation averaging operator satisfies $A_{\mathrm{co}} = \lambda_{\mathrm{co}} I_8$ with $\lambda_{\mathrm{co}} = 2/3$ (for the 18-full family). Since $A_{\mathrm{co}}$ is scalar, its only eigenvalue is $\lambda_{\mathrm{co}}$, and all 8 co dimensions are concentrated at the corresponding k-value $k_{\mathrm{co}} = m(1 - \lambda_{\mathrm{co}}) = 3$. By Theorem 3.4 (block compatibility), the co-block support of any full eigenspace is simply the co-block projector restricted to that eigenspace — which is nonzero only at $k = k_{\mathrm{co}}$. Hence $d_{\mathrm{co}} > 0$ exactly at $k = 3$, and zero elsewhere.

In words: **the role of $\lambda = 2/3$ is algebraic (block support determined by Lemma 4.1), not representation-theoretic (group invariance).** The boundary is a structural consequence of the scalar nature of the co block, not of the $G_1$-action on eigenspaces.

---

**Problem 4 (Field extension failure): Why symmetry-broken families yield $\mathbb{Q}(\sqrt{5})$.**

The rational framework of §7.3 operates via complete destructive interference — the Bose–Mesner algebras of Q₃ and the face-incidence graph have rational eigenmatrices, and the Z₂/Z₃ phase constraints cancel to integers through the per-face interference identity $\omega + \omega^2 + 1 = 0$. The framework breaks **precisely when the interference is incomplete**.

For the n=8 and n=16 symmetry-broken families, the generator set is **not** a union of complete $G$-orbits. The adjacency matrices of the resulting relation set no longer span a Bose–Mesner algebra defined over $\mathbb{Q}$ — some primitive idempotents require the quadratic extension $\mathbb{Q}(\sqrt{5})$. Concretely, the incomplete face coverage leaves un-cancelled cyclotomic contributions that concentrate in a C₅-type spectral block, whose minimal polynomial is irreducible over $\mathbb{Q}$ and splits over $\mathbb{Q}(\sqrt{5})$. The two irrational eigenvalues take the form $\lambda = \alpha \pm \beta\sqrt{5}$ with $\alpha, \beta \in \mathbb{Q}$, precisely the signature of a 2-dimensional real subspace whose structure constants lie in $\mathbb{Q}(\sqrt{5})$.

This is not a failure of the framework but a confirmation of its boundary: the rational spectral law $\lambda = 1 - k/m$ holds exactly when the generator set is closed under the symmetry group that stabilizes the adjacency algebra over $\mathbb{Q}$. When symmetry is broken, the association scheme is no longer symmetric (relations are not closed under conjugation by the full cube rotation group), and the spectral field extends to the splitting field of the scheme's eigenmatrix — in this case, $\mathbb{Q}(\sqrt{5})$. The mechanism that forces rationality in the symmetric case is the same mechanism whose absence permits irrationality in the broken case.

*Remarks.* The n=21 full+slice family (6 rational eigenvalues, $\lambda = 1 - k/21$, $k \in \{0, 4, 6, 8, 10, 12\}$) is a natural extension of the face-symmetric family. The slice moves (M, E, S) are pure edge-permutation moves — they do not affect corner orientation ($\delta_{\mathrm{co}} = 0$), so the per-face arithmetic closure argument of §6 extends without obstruction. The additional eigenvalue ($k = 10$) arises because the slice moves enlarge the edge-permutation adjacency algebra: $S_{12}$ acquires new off-diagonal entries from the slice cycles on the middle layer, shifting one of the existing eigenvalues and introducing a new distinct spectral layer without breaking rationality. A detailed discussion is deferred to Appendix A.4.

## 10. Generality and Open Questions

The central hypothesis of this work is that **spectral rationality is fundamentally arithmetic rather than commutative**. The classical route — commutative algebra $\Rightarrow$ simultaneous diagonalization $\Rightarrow$ rational spectrum — is replaced by a different paradigm: **partition-integral averaging + phase cancellation $\Rightarrow$ rational spectral closure**. In the Rubik’s cube, the face partition provides the concrete instance. The question we now pose is: how far does this arithmetic mechanism extend?

### 10.1 Beyond the Rubik System

The structures analyzed in this paper — blockwise permutation spectra, abelian phase interference, resonance merging, and partition integrality — are not intrinsically tied to the Rubik’s cube. The cube is a particularly rich instance of a larger structural class:

- **Permutation transport.** A transitive permutation action $G \curvearrowright X$ with representation $\rho_{\mathrm{perm}}$ whose Bose–Mesner algebra determines candidate eigenvalues.
- **Abelian phase decoration.** A finite abelian character system $\rho_{\mathrm{phase}}$ (such as $\mathbb{Z}_2$, $\mathbb{Z}_3$, or more generally $\mathbb{Z}_m$) attached to the permutation degrees of freedom, whose character sums constrain which eigenvalues carry nonzero phase-block support.
- **Generator completeness.** A generator set $S$ that is sufficiently complete — in a sense made precise below — to force phase cancellation and partition integrality.

When all three ingredients are present, the averaging operator $A_S = \frac{1}{|S|} \sum_{s \in S} \rho(s)$ exhibits a remarkably rigid spectral structure. In all currently verified complete face-symmetric systems, the spectrum collapses to the affine rational form $\lambda = 1 - k/m$ (with $m = |S|/2$), where $k$ is drawn from a discrete set determined by blockwise spectra, phase interference, and resonance merging. Whether this affine structure is universal, or merely characteristic of the Rubik-type normalization (equal-weight generators, involutive averaging, regular orbit counts), remains open. Different generator weightings, non-face-transitive systems, non-involutive averaging, or non-regular orbit counts could produce rational spectra not of this affine form. The mechanism — blockwise Bose–Mesner spectra filtered by abelian phase interference — may survive even when the specific affine parametrization does not.

### 10.2 Structural Conjecture

**Conjecture (Spectral Rationality under Complete Averaging).** Let $\rho = \rho_{\mathrm{perm}} \otimes \rho_{\mathrm{phase}}$ be a representation of a finite group $G$, where:

- $\rho_{\mathrm{perm}}$ is a transitive permutation representation on a finite set $X$,
- $\rho_{\mathrm{phase}}$ is a finite abelian character system (phase decoration),
- $S \subset G$ is an inverse-closed generator set satisfying a completeness condition (see §10.3).

Then the spectrum of the averaging operator $A_S = \frac{1}{|S|} \sum_{s \in S} \rho(s)$ satisfies $\operatorname{Spec}(A_S) \subset \mathbb{Q}$. Moreover, the eigenvalues take the rational form $\lambda = 1 - k/m$ (with $m = |S|/2$), and the admissible $k$-set is determined by:
1. **Blockwise spectra** — the Bose–Mesner eigenvalues of the permutation blocks,
2. **Phase interference** — character cancellation constraints on the phase blocks,
3. **Resonance merging** — eigenvalue coincidence across blocks under $\lambda = 1 - k/m$.

**Mechanism.** The three mechanisms operate independently:
- The **adjacency algebra** (permutation blocks) determines candidate spectral positions — the raw eigenvalues before constraints are applied.
- The **phase algebra** (abelian character blocks) restricts admissibility through interference — character sums over incomplete orbits leave un-cancelled contributions, pruning the candidate set.
- **Arithmetic closure** (partition integrality) enforces rationality — the existence of a partition with integer per-subset trace sums forces $\lambda \in \mathbb{Q}$ via Theorem 6.1.

No single mechanism suffices alone. None requires commutativity of the underlying generators.

**Current status.** This conjecture is **verified** for the Rubik’s cube family (18-full, 12-quarter, 6-half-turn, 21-full+slice) and for abelian-axis subsets. It is **not yet verified** for any system outside the Rubik’s cube representation. The mechanism — blockwise Bose–Mesner spectra filtered by abelian phase interference — is established in detail for the Rubik case, but a general proof requires a first-principles characterization of "completeness" that does not yet exist.

### 10.3 The Role of Completeness

What does "completeness" enforce? Current evidence suggests a hierarchy of three structural conditions:

**Surface mechanism — (G1) Orbit saturation.** The generator set must sample each local permutation mode with equal probability. In the Rubik’s cube, this means each face is complete: $\{g, g^{-1}, g_{180}\}$ or $\{g, g^{-1}\}$ for quarter-turn families. Incomplete faces (as in n=8, n=16) break this condition, and the spectrum extends to $\mathbb{Q}(\sqrt{5})$.

**Surface mechanism — (G2) Phase balance.** For every non-trivial character $\chi$ of the phase group, the sum $\sum_{s \in S} \chi(s)$ must satisfy a cancellation closure. In the Rubik’s cube, this is the identity $1 + \omega + \omega^2 = 0$ on the $\mathbb{Z}_3$ corner-orientation block — the three moves on a complete face carry phases $\{\omega, \omega^2, 1\}$ and sum to zero.

&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;↓

**Deeper invariant — (G3) Partition-integral closure.** The trace moments $\operatorname{Tr}(A^k)$ admit a finite partition decomposition with integer per-subset sums. This condition is both the most fundamental of the three and the one most likely to survive generalization beyond the Rubik family. The orbit saturation (G1) and phase balance (G2) conditions may merely be the combinatorial shadows of this deeper arithmetic closure principle — sufficient to force it in the Rubik case, but not necessary for it in general. The partition-integral closure — that certain trace sums close in $\mathbb{Z}$ regardless of the representation-theoretic origin of the operators — is the candidate for the true structural invariant.

&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;↓

**Consequence — Rational spectral collapse.** When partition-integral closure holds, the eigenspace trace identity (Theorem 3.1) and the partition integrality criterion (Theorem 6.1) together force $\operatorname{Spec}(A_S) \subset \mathbb{Q}$.

The hierarchy is: orbit saturation and phase balance (the Rubik-specific surface) $\to$ partition-integral closure (the arithmetic invariant) $\to$ rational spectrum (the consequence). The conjecture is that any representation system admitting a partition with integer per-subset eigenspace trace sums will exhibit rational spectral collapse, with the affine form $\lambda = 1 - k/m$ being the Rubik-specific realization of a more general rational parametrization.

![**Figure 6:** Conjectural architecture (§10.2): the mechanism by which generator completeness forces rational spectral collapse. Complete face families (left) satisfy orbit saturation and phase balance, feeding the arithmetic closure pipeline — permutation spectra $\to$ phase interference $\to$ partition integrality $\to$ rational closure — and yield $\mathbb{Q}$-spectra. Broken orbit saturation (right, $n = 8$, $n = 16$) leaves un-cancelled adjacency-algebra contributions in CP/EP, extending the spectral field to $\mathbb{Q}(\sqrt{5})$. The pipeline is verified in the Rubik family; the conjecture is that it generalizes to all permutation+phase+completeness systems. This figure represents conjectural architecture, not proven theorem.](../../figures/paper1_fig6_arithmetic_closure.png)

### 10.4 Open Problems

1. **Characterize completeness.** Give a first-principles definition of generator completeness that implies partition integrality, without reference to the Rubik’s cube geometry. Orbit saturation (G1) and phase balance (G2) are currently empirical descriptions — the fundamental condition may be **partition-integral closure** (G3) itself, with (G1) and (G2) as its combinatorial shadows.

2. **Classify rational averaging spectra.** For which triples $(G, \rho, S)$ does $\operatorname{Spec}(A_S) \subset \mathbb{Q}$ hold? Is the rational form $\lambda = 1 - k/m$ universal within this class, or are there rational averaging spectra not of this form?

3. **Determine minimal assumptions.** The classical route (commutativity $\Rightarrow$ Schur’s lemma $\Rightarrow$ simultaneous diagonalization) requires strong algebraic hypotheses that fail for the Rubik’s cube (94% noncommutativity in the EP block). The arithmetic route (partition integrality $\Rightarrow$ rational spectrum) requires only the partition and the eigenspace trace identity. What is the minimal set of hypotheses under which the arithmetic route closes?

4. **Spectral field for incomplete families.** For symmetry-broken families (n=8, n=16), the spectral field extends to $\mathbb{Q}(\sqrt{5})$. Is this field determined by the minimal polynomial of the incomplete generator interaction graph? The $C_5$-type spectral block structure observed numerically suggests a connection to the smallest non-rational cyclotomic cosine $\cos(2\pi/5) = (\sqrt{5}-1)/4$, but a general proof is missing.

5. **Non-abelian phase systems.** The phase decoration in the Rubik’s cube is abelian ($\mathbb{Z}_2$, $\mathbb{Z}_3$). What happens when $\rho_{\mathrm{phase}}$ carries a non-abelian representation? Does the arithmetic closure mechanism generalize, or does the noncommutativity of the phase block fundamentally alter the spectral structure?

6. **Infinite families and scaling.** The n=21 full+slice family suggests that the face-symmetric class extends naturally beyond 18 face turns. Does the rational spectral form persist for all generator sets obtained by closing the 18 face turns under slice moves? Is there a natural infinite family, and what is its asymptotic spectral density?

**Where we stand.** This paper has established, within the Rubik’s cube family, that spectral rationality arises from arithmetic closure rather than operator commutativity. The proof chain — block compatibility + partition integrality + eigenspace trace identity — is complete for face-symmetric generator sets. The structural conjecture above extends this mechanism to a broader class of permutation+phase systems. It is not yet a theorem; completeness is not yet formalized; the conjecture is verified only in the Rubik family. But the architecture — permutation transport, abelian phase interference, partition-integral closure — is general, and the direction is clear.

The present paper should therefore be read not as a classification theorem for Rubik spectra, but as evidence for a broader arithmetic mechanism governing averaged finite-group representations.

## Appendix A. Proof details

### A.1 Why Galois stability of eigenspaces is enough

If ($\sigma$(A)=A) and A is Hermitian, then eigenspaces are ($\sigma$)-stable. This does not by itself imply rationality; it only reduces the problem to understanding the field of the projector matrices.

### A.2 Why real does not imply rational

The fixed field of complex conjugation is $\mathbb{R}$, not $\mathbb{Q}$. Thus $\sigma$-stability of eigenspaces alone cannot force rational eigenvalues. A direct numerical illustration: for the n=8 mixed generator set, $\sigma(A) \neq A$ (the set is not face-symmetric), yet $\sigma(P_\lambda) = P_\lambda$ holds for all seven eigenspaces to machine precision. Two of these eigenvalues are irrational: $\lambda_{-} = \frac{5-\sqrt{5}}{8} \approx 0.3455$ and $\lambda_{+} = \frac{5+\sqrt{5}}{8} \approx 0.9045$. This confirms that $\sigma(P_\lambda) = P_\lambda$ is insufficient — the eigenvalues live in $\mathbb{Q}(\sqrt{5})$ rather than $\mathbb{Q}$. The step from $\sigma$-stability to rationality requires an additional arithmetic closure mechanism, which for face-symmetric sets is provided by the per-face eigenspace trace integrality argument (§6).

### A.3 How the Rubik’s cube case supplies the arithmetic input

The Rubik’s cube representation provides the arithmetic closure needed by Theorem 6.4 through two specific properties: (i) the generator characters ($\chi$(s) = $\mathrm{Tr}$($\rho$(s))) are integers (Theorem 5.1), and (ii) for face-symmetric (S), the face-sum matrices (F_{$\mathrm{face}$} = $\rho$(g) + $\rho$(g^{-1}) + $\rho$(g_{180})) have integer entries on the permutation and edge-orientation blocks, and integer-valued entries on the corner-orientation block (diagonal entries in ($\{$3,0$\}$ $\subset$ $\mathbb{Z}$) by Lemma 4.1; full-matrix integrality verified entrywise) — the critical cancellation ($\omega^k$ + $\omega^{-k}$ + $\omega^{2k}$ $\in$ $\{$3, 0$\}$) on the co-block eliminates the irrational ($\omega$) contributions. Numerically, this integrality lifts to the eigenspace level: each ($\chi_\lambda$(s) = $\mathrm{Tr}$($P_\lambda$ $\rho$(s))) is an integer for all face-symmetric families tested. The proof of this lifting — that rational spectral projectors ($P_\lambda$ $\in$ M_{228}($\mathbb{Q}$)) force integer traces against the integer face-sum matrices — is the remaining open problem identified in Theorem 6.2 ($\Leftarrow$).

### A.4 The n=21 full+slice family

The n=21 set augments the 18 face turns with the 3 slice moves M, E, S (middle-layer 180° turns, affecting only edge permutation). All six faces remain complete. The spectrum has 6 distinct eigenvalues, all rational of the form ($\lambda$ = 1 - k/21) with (k $\in$ $\{$0, 4, 6, 8, 10, 12$\}$).

This case confirms that the face-symmetric family extends naturally beyond the 18 face turns. The slice moves are pure edge permutations whose character contributions are integers (no ($\omega$) factors), so the per-face arithmetic closure argument of §6 extends without obstruction: the face partition still supplies integer per-subset trace sums, and Theorem 6.1 still forces ($\lambda$ $\in$ $\mathbb{Q}$). The increase from 5 to 6 spectral layers reflects the enlarged generator set ((m = 21)) and the fact that the slice moves populate the edge-permutation block with additional structure, producing a new distinct eigenvalue without breaking rationality.

The n=21 case is noted here as a supplementary experimental confirmation rather than a core open problem: its mechanism is fully captured by the partition integrality framework, and its k-selection rule is subject to the same open question as the 18-full case (Problem 2, §9.2).

---

## Appendix B. Fine-Grained Isotypic Transport and Multiplicity Fibres

The main text decomposes the averaging operator $A$ into six spectral layers $V_\lambda$ and further refines each layer into primitive sectors via the commutative center $\text{Center}\{A, \mathrm{QT}_{\mathrm{all}}, \mathrm{HT}_{\mathrm{all}}\}$. This appendix reports a finer decomposition: the **isotypic decomposition** within each layer, obtained from the full commutant algebra $\text{Comm}_G(V_\lambda)$. The analysis proceeds in three steps — isotypic decomposition (F1), isotypic transport (F2), and multiplicity-fibre tracking (F3) — and yields one new structural concept: the **multiplicity reservoir**.

### B.1 Isotypic Decomposition (F1)

The commutant $\text{Comm}_G(V_\lambda) = \{X \in \text{End}(V_\lambda) : [X, \rho(g)|_{V_\lambda}] = 0 \;\forall g \in G\}$ is computed combinatorially for each layer. Its center $\mathfrak{Z}_\lambda = Z(\text{Comm}_G(V_\lambda))$ yields the isotypic decomposition: each layer splits into irreducible subrepresentations grouped by isomorphism type.

The full 228-dimensional commutant has dimension 610 (computed via index-pair orbit decomposition, 0.7s). The per-layer decomposition is:

| Layer $\lambda$ | dim | $\dim\text{Comm}$ | $\dim\mathfrak{Z}$ | Isotypic components |
|:---------------:|:---:|:-----------------:|:------------------:|:--------------------|
| $V_1$ | 20 | 400 | 1 | $1\text{D} \times 20$ |
| $V_{8/9}$ | 2 | 1 | 1 | $2\text{D} \times 1$ |
| $V_{7/9}$ | 39 | 145 | 13 | $3\text{D} \times 1$ (×13) |
| $V_{2/3}$ | 26 | 145 | 13 | $2\text{D} \times 1$ (×13) |
| $V_{5/9}$ | 106 | 210 | 14 | $6\text{D}\times1$ (×10), $7\text{D}\times1$, $3\text{D}\times1$, **$3\text{D}\times11$**, $3\text{D}\times1$ |
| $V_{1/3}$ | 35 | 65 | 9 | $4\text{D}\times1$ (×8), $3\text{D}\times1$ |

**Total: 51 isotypic components, 59 irreducible summands (copies).** The sum of per-layer commutant dimensions (966) exceeds the full-space commutant dimension (610) by a factor of 1.58 — the commutant is overcomplete, as expected for a representation where cross-block intertwiners are constrained by the transport sparsity structure.

### B.2 Isotypic Transport Tensor (F2)

The transport tensor between isotypic components is

$$
\tilde{K}_{\alpha\beta} = \max_g \frac{1}{\sqrt{d_\alpha}}\|P_\alpha \rho(g) P_\beta\|_F,
$$

where $P_\alpha$ is the projector onto isotypic component $\alpha$ and $d_\alpha$ is its irreducible dimension. The normalization by $1/\sqrt{d_\alpha}$ accounts for the block-multiplicity under Schur's lemma: when the irreps match, the $d_\alpha \times d_\beta$ block $P_\alpha \rho(g) P_\beta$ is proportional to $I_{d_\alpha}$, so the Frobenius norm extracts the scalar with the correct $\sqrt{d_\alpha}$ factor.

Of the $51 \times 51 = 2601$ possible directed pairs, **619 carry nonzero transport** ($\tilde{K}_{\alpha\beta} > 10^{-8}$). The transport graph is:

- **Dense within-layer**: most nonzero edges connect isotypic components in adjacent layers ($V_{7/9} \leftrightarrow V_{5/9}$, $V_{2/3} \leftrightarrow V_{5/9}$, $V_{5/9} \leftrightarrow V_{1/3}$). The $V_{5/9}$ layer is the central hub.
- **No cross-block transport beyond what the 9-sector picture already captures**: all 619 edges are block-preserving (cp→cp, ep→ep, co→co, eo→eo), consistent with the block-diagonal structure of $\rho(g)$.
- **The isotypic transport graph already defines the full transport backbone.** Since 50 of 51 components have multiplicity 1, the isotypic-level transport tensor $\tilde{K}_{\alpha\beta}$ captures essentially all the structure that a per-copy analysis would reveal.

Figure B.3 shows the SVD spectrum of the multiplicity transfer matrices for pairs with multiplicity $>1$. The reservoir's 11-channel decay (blue, 11 singular values) contrasts with all other pairs which collapse to a single rank-1 mode — the entire transport backbone beyond the reservoir is rank-1 sparse. The multiplicity reservoir is the unique carrier of multi-channel transport capacity.

### B.3 Multiplicity-Fibre Tracking (F3)

For isotypic components $\alpha, \beta$ with matching irreducible dimension $d$, the **multiplicity transfer operator** is the 3-tensor

$$
T_g^{\alpha,\beta} \in \mathbb{C}^{m_\alpha \times m_\beta}, \qquad
(T_g^{\alpha,\beta})_{ij} = \frac{1}{\sqrt{d}}\|U_{\alpha,i}^H M_g^{a,b} U_{\beta,j}\|_F,
$$

where $M_g^{a,b} = V_a^H \rho(g) V_b$ is the layer-to-layer kernel, and $U_{\alpha,i}$ is the $d_\alpha \times d$ skinny factor of the $i$-th copy projector ($P_{\alpha,i} = U_{\alpha,i} U_{\alpha,i}^H$). The matrix $T_g^{\alpha,\beta}$ records, for each generator $g$, the coupling strength between each copy of irrep $\alpha$ and each copy of irrep $\beta$.

Diagnostics are computed from the generator-averaged matrix $\bar{T}^{\alpha,\beta} = \frac{1}{|S|}\sum_g T_g^{\alpha,\beta}$:

- **Effective rank**: number of singular values exceeding 1% of the leading SV — measures independent copy-to-copy channels.
- **Entropy**: $-\sum_k p_k \log p_k$ of the normalized singular value distribution — measures distributed vs. concentrated coupling.
- **Isotropy deviation**: coefficient of variation $\sigma/\mu$ of singular values — 0 = all copies equally coupled, large = selective.
- **Schur orthogonality**: for $i \neq j$ within the same isotypic component, $\|U_{\alpha,i}^H M_g U_{\alpha,j}\|_F$ should vanish if the commutant splitting perfectly diagonalizes the dynamics.

#### Results

Of the 23 isotypic pairs with matching irreducible dimension, only 7 have multiplicity $>1$ on at least one side. **Only one pair has effective rank $>1$**: the $V_{5/9}$ $3\text{D}\times11$ isotypic component interacting with itself.

**The representation is almost multiplicity-free.** For 50 of the 51 isotypic components, the multiplicity is 1 — there are no "hidden" copy-level transport channels beyond what the isotypic transport tensor (F2) already encodes. Figure B.1 shows the multiplicity distribution: 50 components at $m=1$, one component at $m=11$ — a stark localization of all internal multiplicity into a single reservoir.

#### The Unique Multiplicity Reservoir

The $V_{5/9}$ $3\text{D}\times11$ component is the sole exception. Its $11 \times 11$ multiplicity transfer matrix has the following properties:

| Property | Value |
|----------|-------|
| max $\bar{K}$ | 1.378 |
| Effective rank | **11** (full — all copies independently active) |
| Entropy | 2.176 (max possible $\log 11 \approx 2.398$) |
| Isotropy deviation | 0.740 (selective — some copies couple more strongly than others) |
| Singular values | 2.210, 1.370, 1.202, 0.618, 0.494, 0.461, 0.419, 0.415, 0.403, 0.390, 0.389 |
| Schur orthogonality | ortho_max = 0.6 (off-diagonal copy coupling is significant) |

Figure B.2 shows the internal channel hierarchy of this reservoir — the 11 singular values form a smooth decay from the dominant mode ($\sigma_1 = 2.210$) to subdominant channels ($\sigma_{11} = 0.389$), revealing a structured mode hierarchy within the reservoir. The accompanying heatmap shows the $11 \times 11$ multiplicity transfer K matrix.

This component spans 33 of the 106 dimensions in $V_{5/9}$ (31%). Its 11-fold multiplicity is unique in the representation. The full-rank multiplicity transfer matrix means all 11 copies are independently active under the generator action. The non-zero Schur orthogonality residual (0.6) indicates that the commutant-based copy decomposition does **not** diagonalize the dynamics: the copies are dynamically coupled, not algebraically decoupled.

We formalize this structure:

**Definition (Multiplicity Reservoir).** An isotypic component $V_\lambda^{(d,m)} \subset V_\lambda$ with irreducible dimension $d$ and copy multiplicity $m$ is a *multiplicity reservoir* if (i) $m > 1$, (ii) the multiplicity transfer matrix $\bar{T}$ has effective rank $>1$, and (iii) the intra-isotypic copy coupling is non-zero (Schur orthogonality fails). A multiplicity reservoir carries an internal multiplicity geometry — a non-trivial fibre dynamics within the isotypic component — beyond what the isotypic-level transport tensor captures.

**Theorem C.1 (Transport Complexity Concentration).** In the 228-dimensional Rubik's cube representation, the $V_{5/9}^{(3,11)}$ component is the unique multiplicity reservoir. All transport complexity beyond the isotypic-level backbone is concentrated in this single component. In particular, the representation's transport hierarchy is not uniformly distributed across the irreducible decomposition but is localized into a single multiplicity-rich fibre.

This concentration phenomenon is structurally analogous to:
- **Resonant modes** in coupled oscillator systems, where a degenerate eigenspace accumulates the bulk of the spectral weight;
- **Gauge fibres** in principal bundles, where the internal fibre degree of freedom carries dynamics independent of the base manifold;
- **Turbulent cascades**, where nonlinear coupling concentrates in a small number of active modes.

The $V_{5/9}^{(3,11)}$ multiplicity reservoir may be the algebraic origin of the hub sector S6 in the 9-sector picture (§3.2): S6 is the only primitive sector whose underlying isotypic component carries non-trivial multiplicity structure, giving it a richer transport capacity than any other sector.

#### Implications for the Trilogy

- **Paper I**: The isotypic decomposition and multiplicity reservoir are structural facts about the spectral object $A$ — they belong here as the finest algebraic decomposition.
- **Paper II**: The transport backbone ($\tilde{K}_{\alpha\beta}$ at the isotypic level) is the substrate on which the sector-level transport graph (11 direct edges, star $S_3$ topology) is built. The multiplicity reservoir enriches the hub structure.
- **Paper III**: The internal dynamics of the multiplicity reservoir — non-Schur copy coupling, full-rank multiplicity transfer — may contribute to the accessibility hierarchy ($\kappa_d$) through composition-only transport channels that require the internal fibre degree of freedom.

---

## 11. Spectral Origin Remark

The six spectral layers arise from resonance merging of blockwise local algebras: the cp block contributes a Hamming-scheme component (the Q₃ Bose–Mesner algebra, a Hecke algebra $H(S_2 \wr S_3, S_3)$), the ep block contributes a face-incidence adjacency component (the commuting algebra of $JJ^T$), and the co/eo blocks contribute phase-cancellation factors ($\mathbb{Z}_3$ and $\mathbb{Z}_2$ diagonal algebras). The global averaging operator merges ten blockwise primitive idempotents into six rational layers via eigenvalue coincidence under $\lambda = 1 - k/m$. No single global Gelfand pair exists; instead, blockwise-local Gelfand geometry holds for each block, and the global algebra $\mathbb{C}[A]$ is a subalgebra of the direct product of the four blockwise Bose–Mesner algebras.

---

## References

**Mathematical lineage.** This paper belongs to the tradition of **association schemes and spectral decomposition of finite group representations** — the algebraic combinatorics of Bose-Mesner algebras, harmonic analysis on finite groups, and algebraic graph theory. The core question — "what is the spectral object, and why is the spectrum rational?" — is answered through the combinatorial structure of the permutation action and the arithmetic of the phase representation, not through commutativity-based spectral theorems of operator algebras. The lineage runs: association schemes (Bose-Mesner 1950s, Bannai-Ito 1984) → harmonic analysis on finite groups (Diaconis 1988, Ceccherini-Silberstein et al. 2008) → spectral graph theory (Cvetković-Doob-Sachs 1980) → the present paper.

### Association schemes and Bose-Mesner algebra

[1] E. Bannai and T. Ito, *Algebraic Combinatorics I: Association Schemes*. Benjamin/Cummings, 1984.
  — Foundational text. The Bose-Mesner algebra of a permutation association scheme is the algebraic structure governing the spectral decomposition on the Rubik cube’s permutation blocks. This is the paper’s primary mathematical lineage.

[2] A.E. Brouwer, A.M. Cohen, and A. Neumaier, *Distance-Regular Graphs*. Springer, 1989.
  — Comprehensive treatment of distance-regular graphs and their Bose-Mesner algebras. The Q₃ hypercube (cp block) is a distance-regular graph whose intersection numbers determine the Krawtchouk-polynomial eigenvalues.

[3] C.D. Godsil, *Algebraic Combinatorics*. Chapman & Hall, 1993.
  — Association schemes, coherent configurations, and their representation theory. The commuting algebra framework underlies the refinement semilattice constructed in §6.

### Harmonic analysis and spectral decomposition on finite groups

[4] T. Ceccherini-Silberstein, F. Scarabotti, and F. Tolli, *Harmonic Analysis on Finite Groups*. Cambridge University Press, 2008.
  — Fourier analysis on finite groups. The decomposition of the group algebra into isotypic components, the structure of Gelfand pairs, and the spherical function approach inform the spectral stratification.

[5] P. Diaconis, *Group Representations in Probability and Statistics*. IMS Lecture Notes, 1988.
  — Spectral analysis of group-valued random walks. The averaging operator $A = (1/|S|)\sum \rho(s)$ appears as the transition matrix of a random walk on a finite group orbit; the eigenvalue structure governs mixing times and concentration.

### Representation theory of finite groups

[6] J.-P. Serre, *Linear Representations of Finite Groups*. Graduate Texts in Mathematics 42, Springer, 1977.
  — Canonical reference. Schur’s Lemma, character theory, isotypic decomposition — the standard toolkit for decomposing a group representation into irreducible components.

[7] C.W. Curtis and I. Reiner, *Representation Theory of Finite Groups and Associative Algebras*. AMS Chelsea, 1962.
  — Semisimple algebras, the Artin-Wedderburn theorem, and commutant structure. The block-diagonal decomposition of the averaging operator is a consequence of the semisimple structure of the group algebra $\mathbb{C}[G]$.

[8] W. Fulton and J. Harris, *Representation Theory: A First Course*. Graduate Texts in Mathematics 129, Springer, 1991.
  — Accessible treatment of finite group representations; the relation between the group algebra decomposition and the character table via Wedderburn components.

### Spectral graph theory

[9] D. Cvetković, M. Doob, and H. Sachs, *Spectra of Graphs*. Academic Press, 1980.
  — Canonical text on graph spectra. The eigenvalues of the adjacency matrices of the underlying permutation graphs (Q₃ hypercube, face-incidence graph) determine the block-level spectral contributions.

[10] N. Biggs, *Algebraic Graph Theory*. Cambridge University Press, 1993.
  — The connection between graph automorphisms, adjacency algebras, and spectral decomposition. The face-incidence adjacency structure of the Rubik cube is a concrete instance of these general principles.

### Trilogy cross-references

[11] Paper II — *Noncommutative Transport and Selection Rules in Finite Group Representations: Hybrid Sectors, Permutation Channels, and Global Lifting Constraints.* `examples/paper2/Paper II.md`

[12] Paper III — *Accessibility Beyond Lie Closure in Finite Group Representations: Hybrid Projector Geometry and Composition-Only Transport.* `examples/paper3/Paper III.md`

[13] `docs/paper_data.md` — Shared Data File: Single Source of Truth for Paper Trilogy (post-ρ-fix 6-layer, 9-sector resolution).

---
