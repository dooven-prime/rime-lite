# Support-Graph Reachability and Matrix-Composition Obstructions

### Image--Kernel Mismatch with a Rubik-Cube Case Study

**WuJun Chen**

Independent Researcher | RIME Project | 2026

ORCID: 0009-0007-9561-2892

***

## Abstract

**Problem.** A sector transport graph records whether a projected generator block $Q_i\rho(g)Q_j$ is nonzero. One might infer that a graph path $j\to k\to i$ guarantees a nonzero projected composition $Q_i\rho(g_2)Q_k\rho(g_1)Q_j$. That inference is false in general: nonzero adjacent factors can have a zero product.

**Approach.** We distinguish three objects. The **support graph** records nonzero direct blocks. The **two-step composition graph** records nonzero projected products. The **obstruction set** consists of support-graph paths that disappear under matrix composition. For two adjacent factors $A=Q_i\rho(g_2)Q_k$ and $B=Q_k\rho(g_1)Q_j$, the exact obstruction is $\operatorname{im}B\subseteq\ker A$. We then specialize to representations and sector projectors respecting a common physical-block decomposition.

**Results.** We prove that the two-step composition graph is a subgraph of the square of the support graph, with equality requiring an additional image--kernel nondegeneracy condition. If the group action and all sector projectors preserve the same physical blocks, projected composition cannot cross between sectors with disjoint block support at any finite length. In the canonical 228-dimensional Rubik realization, five distinguished pairs selected from two-step support paths all satisfy this block obstruction. Their adjacent factor norms are order one, while exhaustive products over the $18^2$ ordered generator pairs have Frobenius norms between $1.10\times10^{-16}$ and $3.02\times10^{-15}$.

**Boundary.** Graph reachability and projected-composition reachability are distinct invariants. A hybrid sector may be incident to edges carried by different physical-block components without transferring amplitude between those components. The canonical five pairs are therefore not compositional morphisms; they are finite witnesses of support-graph overapproximation. Image--kernel compatibility is the missing promotion datum.

***

## Introduction

Sectorized operator analysis frequently begins with a family of orthogonal projectors

$$
I=\sum_{i\in\mathcal I}Q_i,
\qquad
Q_iQ_j=\delta_{ij}Q_i,
$$

and a unitary action $\rho:G\to U(V)$. For every declared generator $g$, define the transport blocks

$$
T_{ij}(g)=Q_i\rho(g)Q_j.
$$

The direct support relation $j\to i$ is present when one of these blocks is nonzero. This relation is useful: it records exactly where a single generator fails to preserve the chosen sectorization. It does not, however, retain the images and kernels of the nonzero blocks.

This loss of information matters under composition. Given nonzero blocks

$$
Q_k\rho(g_1)Q_j\ne0,
\qquad
Q_i\rho(g_2)Q_k\ne0,
$$

the graph contains a path $j\to k\to i$. The corresponding operator is

$$
Q_i\rho(g_2)Q_k\rho(g_1)Q_j.
$$

The product can vanish if the first step lands entirely within directions
annihilated by the second. Thus, for a fixed sectorization and declared
generator set, Boolean support-graph reachability overapproximates
projected-composition reachability defined by compatible ordered generator
tuples.

This paper makes that distinction formal through named definitions, exact
obstruction theorems, local promotion criteria, and a promotion problem.

### Scope

The general theorems concern finite-dimensional Hilbert spaces, orthogonal sector projectors, and unitary or linear transport maps. The Rubik's cube representation supplies one finite realization. Claims about its nine sectors, ten direct edges, and five graph-only pairs are computational certificates for the declared representation and generator set.

This paper does not claim that every support path is obstructed. It identifies
the missing datum and provides exact local criteria for both obstruction and
promotion.
Higher-depth accessibility theories require additional declared objects and
are not considered here. The criterion supplied here can be used as the local
survival gate in any later routed-composition analysis.

## Notation {.unnumbered}

| Symbol | Meaning |
|---|---|
| $V$ | finite-dimensional complex Hilbert space |
| $\rho:G\to U(V)$ | declared transport representation |
| $S\subset G$ | finite generator set; inverse-closed in the canonical audit |
| $Q_i$ | orthogonal projector onto sector $V_i=\operatorname{im}Q_i$ |
| $T_{ij}(g)$ | direct transport block $Q_i\rho(g)Q_j$ |
| $K^S_{ij}$ | $\max_{g\in S}\lVert T_{ij}(g)\rVert_F$ |
| $\mathcal G_S$ | directed support graph of the direct blocks |
| $C_{ikj}(g_2,g_1)$ | projected two-step composition $Q_i\rho(g_2)Q_k\rho(g_1)Q_j$ |
| $\mathcal G^{(2)}_{\mathrm{comp}}$ | two-step composition graph |
| $\mathcal O^{(2)}_{\mathrm{wit}}$ | witness-level image--kernel obstruction tuples |
| $\mathcal O^{(2)}_{\mathrm{path}}$ | path-level triples whose every declared two-step product vanishes |
| $\Pi_b$ | orthogonal projector onto physical block $V_b$ |
| $\operatorname{BlockSupp}(Q_i)$ | blocks on which $Q_i$ has nonzero restriction |

***

## Sector Transport and the Support Graph

### Sectorization

Let $V$ be finite dimensional and let $\{Q_i\}_{i\in\mathcal I}$ be a complete orthogonal sectorization:

$$
Q_i=Q_i^\dagger=Q_i^2,
\qquad
Q_iQ_j=0\ (i\ne j),
\qquad
\sum_iQ_i=I.
$$

We do not assume that $Q_i$ commutes with $\rho(G)$. Indeed, non-invariance is
the source of off-diagonal direct transport.

### Support Graph

**Definition 2.1 (Direct support graph).** \label{def:paper3-support-graph}
For a declared generator set $S$, the directed support graph $\mathcal G_S$ has vertex set $\mathcal I$ and edge

$$
j\longrightarrow i
\quad\Longleftrightarrow\quad
T_{ij}(g)=Q_i\rho(g)Q_j\ne0
\text{ for some }g\in S.
$$

The associated weighted support matrix is

$$
K^S_{ij}=\max_{g\in S}\lVert Q_i\rho(g)Q_j\rVert_F.
$$

When $S=S^{-1}$ and $\rho$ is unitary, $K^S$ is symmetric, although the block-level definition remains directed.

### Transport--Non-Invariance Identity

The support graph has the following exact operator interpretation.

**Theorem 2.2 (Transport--Non-Invariance Identity).** \label{prop:paper3-transport-noninvariance}
For a unitary $U$ and an orthogonal projector $Q_j$ in a complete sectorization,

$$
\sum_{i\ne j}\lVert Q_iUQ_j\rVert_F^2
=\lVert(I-Q_j)UQ_j\rVert_F^2
=\frac12\lVert[U,Q_j]\rVert_F^2.
$$

*Proof.* Orthogonality gives $I-Q_j=\sum_{i\ne j}Q_i$, so the first equality is the Pythagorean decomposition of the outgoing block. Put $Q=Q_j$. Relative to $V=\operatorname{im}Q\oplus\ker Q$, the commutator has off-diagonal blocks $(I-Q)UQ$ and $-QU(I-Q)$. Unitarity gives $\lVert(I-Q)UQ\rVert_F^2=\operatorname{tr}(Q)-\lVert QUQ\rVert_F^2$ and $\lVert QU(I-Q)\rVert_F^2=\operatorname{tr}(Q)-\lVert QU^\dagger Q\rVert_F^2$. The two compressed operators are adjoints, so
$\lVert QUQ\rVert_F=\lVert QU^\dagger Q\rVert_F$. Hence the two off-diagonal blocks have equal Frobenius mass, and their squared norms sum to $\lVert[U,Q]\rVert_F^2$. $\square$

**Corollary 2.3.** Vertex $j$ has no outgoing off-diagonal edge for $U$ if and only if $[U,Q_j]=0$.

This result is local to one generator. It does not assert that paths in the resulting support graph compose nontrivially.

***

## Projected Matrix Composition

### Composition Operator

**Definition 3.1 (Two-step composition operator).** \label{def:paper3-composition-operator}
For sectors $j,k,i$ and generators $g_1,g_2\in S$, define

$$
C_{ikj}(g_2,g_1)
=Q_i\rho(g_2)Q_k\rho(g_1)Q_j.
$$

The ordered triple $(j,k,i)$ is **composition-active** if this operator is nonzero for at least one ordered pair $(g_1,g_2)$.

**Definition 3.2 (Two-step composition graph).**
The graph $\mathcal G^{(2)}_{\mathrm{comp}}$ contains $j\Rightarrow i$ when there are $k\in\mathcal I$ and $g_1,g_2\in S$ such that $C_{ikj}(g_2,g_1)\ne0$.

The graph square $\mathcal G_S^2$ contains $j\leadsto i$ when there is an intermediate $k$ with edges $j\to k$ and $k\to i$. The two relations are deliberately different.

### Composition-to-Path Inclusion

**Theorem 3.3 (Composition-to-Path Inclusion).** \label{prop:paper3-composition-implies-path}
If $C_{ikj}(g_2,g_1)\ne0$, then

$$
Q_k\rho(g_1)Q_j\ne0
\quad\text{and}\quad
Q_i\rho(g_2)Q_k\ne0.
$$

Consequently,

$$
\mathcal G^{(2)}_{\mathrm{comp}}\subseteq\mathcal G_S^2.
$$

*Proof.* A product with a zero factor is zero. $\square$

The converse fails. This is not a numerical artifact but a direct consequence
of ordinary matrix algebra.

**Definition 3.4 (Witness-level obstruction set).** \label{def:paper3-witness-obstruction-set}
The witnessed obstruction set is

$$
\mathcal O^{(2)}_{\mathrm{wit}}
=\left\{(j,k,i,g_2,g_1):
Q_k\rho(g_1)Q_j\ne0,
\ Q_i\rho(g_2)Q_k\ne0,
\ C_{ikj}(g_2,g_1)=0
\right\}.
$$

**Definition 3.5 (Path-level obstruction set).** \label{def:paper3-path-obstruction-set}
The graph-only path obstruction set is

$$
\mathcal O^{(2)}_{\mathrm{path}}
=\left\{(j,k,i):
j\to k\to i\text{ in }\mathcal G_S,
\ C_{ikj}(g_2,g_1)=0\ \forall g_1,g_2\in S
\right\}.
$$

The Image--Kernel Criterion acts on a fixed witness tuple in
$\mathcal O^{(2)}_{\mathrm{wit}}$. The canonical five-pair census is a
path-level statement in $\mathcal O^{(2)}_{\mathrm{path}}$.

***

## Exact Obstruction Theorems

### Image--Kernel Criterion

**Theorem 4.1 (Image--Kernel Criterion).** \label{thm:paper3-image-kernel}
Fix $i,k,j$ and $g_1,g_2$. Set

$$
A=Q_i\rho(g_2)Q_k,
\qquad
B=Q_k\rho(g_1)Q_j.
$$

Then

$$
C_{ikj}(g_2,g_1)=AB=0
\quad\Longleftrightarrow\quad
\operatorname{im}B\subseteq\ker A.
$$

In particular, $A\ne0$ and $B\ne0$ do not imply $AB\ne0$.

*Proof.* The product $AB$ vanishes exactly when $A(Bv)=0$ for every $v$, which is equivalent to every vector in $\operatorname{im}B$ belonging to $\ker A$. $\square$

This theorem identifies the information discarded by the support graph. A tuple
belongs to $\mathcal O^{(2)}_{\mathrm{wit}}$ exactly when both factors are
nonzero and the displayed image--kernel inclusion holds. An edge records only
that a block is nonzero; it does not record its image subspace or the kernel of
the next block.

### Composition Mass and Efficiency

For a fixed path and generator pair, define

$$
M_{ikj}(g_2,g_1)=\lVert C_{ikj}(g_2,g_1)\rVert_F
$$

and, when both factors are nonzero,

$$
\eta_{ikj}(g_2,g_1)
=\frac{\lVert AB\rVert_F}
{\lVert A\rVert_F\lVert B\rVert_F}.
$$

Submultiplicativity gives $0\le\eta\le1$. While the support graph records only
that the denominator is nonzero, the quantity $\eta$ measures the extent to
which the two incident blocks are compositionally aligned.

### Disjoint Endpoint Block-Support Obstruction

Suppose now that

$$
V=\bigoplus_{b\in\mathcal B}V_b,
\qquad
I=\sum_b\Pi_b,
$$

and that both the action and sectorization respect this decomposition:

$$
[\rho(g),\Pi_b]=0,
\qquad
[Q_i,\Pi_b]=0
$$

for every $g,i,b$. Write

$$
Q_i=\bigoplus_bQ_i^{(b)},
\qquad
\operatorname{BlockSupp}(Q_i)
=\{b:Q_i^{(b)}\ne0\}.
$$

**Theorem 4.2 (Disjoint Endpoint Block-Support Obstruction).** \label{thm:paper3-block-composition}
If

$$
\operatorname{BlockSupp}(Q_i)
\cap
\operatorname{BlockSupp}(Q_j)
=\varnothing,
$$

then for every finite sequence of intermediate sectors and group elements,

$$
Q_i\rho(g_n)Q_{k_{n-1}}\cdots
Q_{k_1}\rho(g_1)Q_j=0.
$$

*Proof.* Every factor is block diagonal, so the full product is block diagonal. Its restriction to block $b$ contains $Q_i^{(b)}$ on the left and $Q_j^{(b)}$ on the right. For every $b$, at least one of these endpoint restrictions is zero. Hence every block of the product vanishes. $\square$

**Corollary 4.3 (Hybrid sectors do not switch blocks).**
With the convention $T_{ij}=Q_i\rho(g)Q_j$, vertex $j$ is the source and
vertex $i$ is the target. A hybrid intermediate $k$ can have an incoming edge
$j\to k$ supported on one physical-block component and an outgoing edge
$k\to i$ supported on another. Because
$Q_k=\bigoplus_bQ_k^{(b)}$ contains no off-diagonal map between these
components, such incidence does not promote the path to a cross-block
composition.

**Corollary 4.4 (All-length obstruction).**
Under the hypotheses of Theorem~\ref{thm:paper3-block-composition}, graph paths of arbitrary length between disjoint-block endpoints remain operator-inactive after inserting the corresponding sector projectors.

### Local Promotion Criteria

The obstruction theorem gives an exact criterion and two convenient sufficient
certificates.

**Proposition 4.5 (Exact local promotion criterion).**
For $A=Q_i\rho(g_2)Q_k$ and $B=Q_k\rho(g_1)Q_j$,

$$
AB\ne0
\quad\Longleftrightarrow\quad
\exists v\in\operatorname{im}B\text{ such that }Av\ne0.
$$

Two useful sufficient certificates are:

1. $B\ne0$ and $A$ is injective on $\operatorname{im}B$;
2. $\operatorname{im}B=\operatorname{im}Q_k$ and $A\ne0$.

*Proof.* The equivalence is the negation of Theorem~\ref{thm:paper3-image-kernel}.
For (1), any nonzero vector in $\operatorname{im}B$ survives $A$. For (2),
$A=Q_i\rho(g_2)Q_k$ is nonzero on some vector of
$\operatorname{im}Q_k=\operatorname{im}B$. $\square$

***

## The Canonical Rubik Realization

### Declared System

The canonical realization uses

$$
V=V_{\mathrm{cp}}\oplus V_{\mathrm{ep}}
\oplus V_{\mathrm{co}}\oplus V_{\mathrm{eo}},
$$

with dimensions $64+144+8+12=228$. Every standard face-turn matrix preserves these four cubie-type blocks. The nine QH projectors $Q_1,\ldots,Q_9$ are obtained from the registered simultaneous spectral resolution of the numerically commuting operators $\mathrm{QT}_{\mathrm{all}}$ and $\mathrm{HT}_{\mathrm{all}}$. Since those operators are block diagonal, their registered projectors are block diagonal to the declared numerical tolerance.

The registration audit uses the complex128 root-of-unity realization and
reports the following maximum Frobenius residuals:

| Registration check | Maximum residual |
|---|---:|
| Pairwise commutators of $A_{18},\mathrm{QT}_{\mathrm{all}},\mathrm{HT}_{\mathrm{all}}$ | $3.77\times10^{-16}$ |
| Projector idempotence | $4.19\times10^{-15}$ |
| Projector Hermiticity | $8.03\times10^{-17}$ |
| Pairwise projector orthogonality | $3.21\times10^{-15}$ |
| Completeness $\lVert\sum_iQ_i-I\rVert_F$ | $1.32\times10^{-14}$ |
| Joint invariance under the three QH operators | $3.58\times10^{-14}$ |
| Cross-physical-block projector mass | $1.44\times10^{-15}$ |

Independent iterative joint diagonalization returns nine sectors with sorted
dimensions

$$
[1,2,8,20,26,27,39,39,66]
$$

at clustering tolerances $10^{-6},10^{-8},10^{-10}$, and $10^{-12}$. Although
these data certify the registered numerical sectorization, they do not promote
it to an exact algebraic joint-spectrum theorem.

The direct transport graph uses the 18 standard face-turn generators. The
computational certificate declares three distinct numerical controls:

| Control | Value |
|---|---:|
| Direct-edge threshold | $5\times10^{-2}$ |
| Registration and composition-zero tolerance | $10^{-10}$ |
| Joint-sector clustering sweep | $10^{-6},10^{-8},10^{-10},10^{-12}$ |

At the declared direct-edge threshold, the graph has ten undirected
off-diagonal edges. All ten edges join sectors sharing at least one physical
block. The general definitions above remain exact nonzero statements; the
threshold is part of this finite numerical realization.

### The Five Graph-Only Pairs

The square of the support graph contains five distinguished two-step paths whose endpoints have disjoint physical-block support:

| Endpoints | Endpoint block support | Canonical intermediate |
|---|---|---:|
| S2--S4 | eo vs. ep+co | S6 |
| S3--S9 | ep+eo vs. cp+co | S7 |
| S4--S5 | ep+co vs. eo | S6 |
| S4--S8 | ep+co vs. cp | S9 |
| S6--S9 | ep+eo vs. cp+co | S7 |

These are support-graph statements: they show that the intermediate sector is
incident to both endpoint edges, not that it transfers amplitude between the
endpoint block components.

### Canonical Composition Audit

**Computational Proposition 5.1 (Canonical five obstruction witnesses).** \label{prop:paper3-canonical-five}
In the declared complex128 realization, exhaustive evaluation over all $18^2$ ordered generator pairs gives:

| Endpoints | Intermediate | Max left edge | Max right edge | Max product ($S^2$) |
|---|---:|---:|---:|---:|
| S2--S4 | S6 | 0.577350 | 3.464102 | $1.098\times10^{-16}$ |
| S3--S9 | S7 | 3.605551 | 4.062019 | $3.017\times10^{-15}$ |
| S4--S5 | S6 | 3.464102 | 0.816497 | $1.553\times10^{-16}$ |
| S4--S8 | S9 | 1.000000 | 2.828427 | $1.060\times10^{-15}$ |
| S6--S9 | S7 | 3.605551 | 4.062019 | $2.937\times10^{-15}$ |

The left and right columns are independently maximized over $g_2\in S$ and
$g_1\in S$. They summarize the individual edge strengths and need not arise
from the same ordered generator pair. The final column is the maximum over all
$(g_2,g_1)\in S^2$. The edge maxima are order one, while the composition
maxima are machine-zero. Theorem~\ref{thm:paper3-block-composition} explains
the pattern structurally: the two incident edges use different physical-block
components of the intermediate sector.

![The exact local image--kernel obstruction and the five registered Rubik witnesses. The two factor columns are independently maximized, while the product column is exhaustive over all $18^2$ ordered generator pairs. Machine-zero product norms are computational data; exact vanishing uses the stated block-preserving hypothesis.](../../figures/paper3/fig1_composition_obstruction.png)

**Claim boundary.** The nonzero factor norms and machine-zero products are computational certificates for the declared matrices. Exact vanishing follows conditionally from the exact block-preserving construction and exact block support. No conclusion here depends on a full-$G$ commutant decomposition, a layer-wise isotypic decomposition, or the candidate value $\dim\operatorname{End}_G(V)=610$.

### Graph-Only Detection Boundary

The graph-level detector applies three tests:

1. the endpoints had disjoint block-support labels;
2. the direct endpoint block was zero;
3. the weighted support graph contained a two-step path.

Although these tests identify the five rows above as graph paths, they do not
evaluate projected matrix products. The exhaustive matrix audit supplies the
additional conclusion: every declared two-step product for these five path
triples is machine-zero and satisfies the structural block obstruction.

***

## Support Graphs as Overapproximations

### Boolean Support Forgets Linear Geometry

Replacing each transport block by the Boolean value $\mathbf 1[T_{ij}(g)\ne0]$ forgets rank, image, kernel, singular directions, phase, and cancellation. Boolean matrix multiplication therefore computes possible support paths rather than guaranteed nonzero operator products.

This distinction is familiar in sparse linear algebra: the structural pattern of a matrix product can contain entries that cancel or vanish because the corresponding row and column subspaces are orthogonal. Here the loss is stronger because each graph edge aggregates over generators and discards the witness-specific subspace geometry.

### Witness Compatibility

A path $j\to k\to i$ may use one generator to establish the first edge and another to establish the second. Even after those witnesses are fixed, composition requires

$$
\operatorname{im}\bigl(Q_k\rho(g_1)Q_j\bigr)
\not\subseteq
\ker\bigl(Q_i\rho(g_2)Q_k\bigr).
$$

Consequently, a composition-aware data structure must retain more information
than $K^S_{ij}$. Possible choices include:

- the family of block maps $T_{ij}(g)$;
- their image and kernel projectors;
- singular-value data;
- the composition mass tensor $M_{ikj}(g_2,g_1)$;
- normalized composition efficiency $\eta_{ikj}(g_2,g_1)$.

The scalar maximum $K^S$ is sufficient for direct support and insufficient for compositional reachability.

***

## Related Work and Novelty Boundary

The support graph is a Boolean abstraction of a family of linear maps. Boolean
zero-pattern calculus and combinatorial matrix theory record possible product
support, but they do not retain cancellation, image, kernel, or singular-direction
data \cite{brualdiRyser1991,hornJohnson2013}. The inclusion
$\mathcal G^{(2)}_{\mathrm{comp}}\subseteq\mathcal G_S^2$ is the corresponding
one-sided abstraction statement for projected sector blocks.

Products selected from a declared family also occur in switched linear systems
\cite{liberzon2003}. The present result is
narrower: it does not study asymptotic stability or semigroup growth, but asks
when a Boolean path in a sector support graph is realized by a nonzero ordered
product. The image--kernel criterion supplies the exact local obstruction, and
the block-support theorem supplies an all-length structural obstruction.

Linear representations of free monoids and noncommutative rational series
provide a direct comparison for word-indexed matrix products
\cite{berstelReutenauer2011}. In this context, the additional sector projectors select a
fixed route and can annihilate an otherwise admissible product. The resulting
image--kernel condition is also the local matrix incidence underlying the
rank-stratified treatment in \cite{paper7}; that broader incidence geometry is
not needed for the criterion proved here.

The underlying image, kernel, singular-value, and block-matrix language is
standard matrix analysis \cite{hornJohnson2013}. The ambient finite-group
language is standard representation theory \cite{serre1977,curtisReiner1962}.

***

## Graph-to-Composition Promotion Problem

The promotion question is open:

> **When does a support-graph path force a nonzero projected matrix composition?**

In the shared typed notation, the direct relation studied here is
$R_1^{\mathrm{op}}=R_1[\rho(S)]$. It is a Boolean overapproximation and cannot
be substituted for routed-composition support $C_d^{\mathrm{op}}$, full-word
support $W_d^{\mathrm{op}}$, or either associated depth.

For length two, Theorem~\ref{thm:paper3-image-kernel} gives the exact answer for fixed witnesses: promotion occurs precisely when the incoming image is not contained in the outgoing kernel. The broader problem is to derive useful hypotheses from coarser data.

Candidate directions include:

1. **Rank conditions.** Determine when ranks of the two incident blocks force nontrivial image overlap inside $Q_kV$.
2. **Generic transversality.** On a declared parameter space, identify when image--kernel incidence is exceptional rather than persistent.
3. **Witness compatibility.** Distinguish paths assembled from unrelated edge-maximizing generators from paths admitting a compatible generator tuple.
4. **Higher length.** Develop recursive image propagation rather than Boolean graph powers.
5. **Compression bounds.** Determine which singular-value or principal-angle summaries are sufficient to certify nonzero composition without storing every block matrix.

Any theorem promoting graph reachability to projected-composition reachability
must state one of these nondegeneracy mechanisms explicitly. Graph incidence
alone is insufficient.

***

## Discussion

The obstruction clarifies the role of hybrid sectors. A hybrid sector remains
an important spectral object with nonzero components in several physical
blocks, and it may be incident to direct transport edges carried by those
components. However, a block-diagonal hybrid projector is not a switch between
them; its multiple components coexist as a direct sum.

The canonical five pairs expose this distinction cleanly. Each has two
order-one adjacent support edges, while the registered audit finds every
projected two-step product to be machine-zero. The block-support theorem
explains the vanishing under its exact hypotheses. The support graph therefore
describes potential incidence, while operator composition describes compatible
amplitude propagation.

This separation gives the logical audit order:

$$
\text{spectral sectors}
\longrightarrow
\text{direct transport blocks}
\longrightarrow
\text{support graph}
\longrightarrow
\text{composition audit}.
$$

The arrows indicate construction and audit order, not implication or
functional determination. Replacing the direct blocks by their Boolean support
discards image--kernel data. Theorem~\ref{prop:paper3-transport-noninvariance}
characterizes the direct off-diagonal mass, while the passage from graph paths
to matrix composition has no unconditional converse.

***

## Claim Status and Boundary

The table uses the four claim levels. Refuted implications are
listed separately as failure boundaries.

| Claim | Status |
|---|---|
| Transport--Non-Invariance Identity | Theorem |
| Nonzero projected composition implies a support-graph path | Theorem |
| Image--Kernel Criterion | Theorem |
| Disjoint Endpoint Block-Support Obstruction | Theorem |
| Canonical ten-edge direct support graph | Computational Certificate |
| Canonical five two-step graph-only pairs | Computational Certificate |
| Canonical five projected products are machine-zero, with a structural block explanation | Computational Certificate |
| Generic graph-to-composition promotion | Research Program |

The paper's principal failure boundary is explicit: a support-graph path does
not imply nonzero composition. Support data are Boolean incidence data and
cannot certify matrix composition without image--kernel or equivalent
nondegeneracy information.

***

## Conclusion

The support graph and the matrix-composition graph are distinct mathematical
objects. For projected blocks

$$
A=Q_i\rho(g_2)Q_k,
\qquad
B=Q_k\rho(g_1)Q_j,
$$

the exact missing condition is

$$
\operatorname{im}B\not\subseteq\ker A.
$$

In block-preserving systems, this becomes a structural obstruction: a hybrid intermediate sector cannot transfer amplitude between its distinct physical-block components. The five canonical Rubik paths are finite witnesses of that obstruction. They are visible in the square of the support graph but absent from the projected composition graph.

For the fixed sectorization, generator set, and projected-product semantics used
throughout this paper, the central principle is therefore:

$$
\boxed{\text{Boolean support-graph reachability overapproximates projected-composition reachability}.}
$$

The next problem is to identify nondegeneracy conditions under which that overapproximation becomes exact.

***

## Appendix A: Basis-Level Composition Certificate

Let $B_i$ be an orthonormal basis matrix for $Q_iV$, so $Q_i=B_iB_i^\dagger$. Then

$$
Q_i\rho(g_2)Q_k\rho(g_1)Q_j
=B_i\left(B_i^\dagger\rho(g_2)B_k\right)
\left(B_k^\dagger\rho(g_1)B_j\right)B_j^\dagger.
$$

Because left multiplication by $B_i$ and right multiplication by
$B_j^\dagger$ preserve nonzero status and Frobenius norm,

$$
\left\lVert Q_i\rho(g_2)Q_k\rho(g_1)Q_j\right\rVert_F
=
\left\lVert
\left(B_i^\dagger\rho(g_2)B_k\right)
\left(B_k^\dagger\rho(g_1)B_j\right)
\right\rVert_F.
$$

The implementation evaluates these reduced matrices. This avoids repeated dense $228\times228$ products without changing the certificate.

***

## Appendix B: Longer Paths

For a path $i_0\to i_1\to\cdots\to i_n$, define recursively

$$
W_0=Q_{i_0}V,
\qquad
W_r=Q_{i_r}\rho(g_r)W_{r-1}.
$$

The projected composition is nonzero exactly when $W_n\ne\{0\}$. A Boolean support path verifies only that each isolated block map is nonzero on some input; it does not verify that the propagated subspace $W_{r-1}$ avoids the next kernel. This recursion is the natural higher-length replacement for graph powers.

Under the hypotheses of Theorem~\ref{thm:paper3-block-composition}, every $W_r$ remains inside the physical blocks present at the source. Therefore no sequence of block-respecting projectors and group elements can connect disjoint-block endpoints.

***

## Appendix C: Computational Artifacts

The following repository artifacts support the canonical Rubik certificate.
The default directory for C1--C2 is `experiments/paper3/`; C3 is relative to
the repository root.

| Artifact | Role | Short path |
|----------|-------------------|------------|
| C1 | exhaustive graph-versus-composition certificate | \path{validation/composition_obstruction.py} |
| C2 | source-addressed completed-run observation | \path{results/composition_obstruction.observation.json} |
| C3 | direct graph and composition regression | \path{tests/test_transport.py} |

C1 reconstructs the nine QH projectors and 18 standard generator matrices,
reports commutation, projector, and physical-block residuals, checks the
nine-sector census across clustering tolerances $10^{-6}$ through $10^{-12}$,
and evaluates all $18^2$ ordered products for each canonical triple. From the
repository root, run it as `python experiments/paper3/<C1 short path>`; append
`--check-result` to verify C2 against its declared source hashes without
repeating the matrix calculation.

C2 records parameters, runtime, package versions, Git state, and explicit
source hashes. It is a source-addressed run record, not an independent
certificate; reproducing the certificate requires a clean full run of C1. C1 supports
Proposition~\ref{prop:paper3-canonical-five}.

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).

***
