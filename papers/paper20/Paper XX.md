# All-Depth Carrier Accessibility for Routed Composition
### Factorization, Survivor Recursion, and Image--Kernel Obstructions

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*Paper XX of the RIME program. This independently scoped theorem paper begins
the post-protocol carrier/route line; it does not continue or reopen the SOF
protocol sequence closed by Paper XV.*

***

## Abstract

**Problem.** Boolean support paths generally overapproximate nonzero routed
operator compositions: consecutive supported blocks may lie on different
invariant carriers, or a routed prefix may land in the kernel of the remaining
suffix.

**Approach.** We consider a finite-dimensional vector space with a declared
finite direct-sum carrier decomposition, a complete family of sector
idempotents, and transport maps and sector projectors that preserve every
carrier. Routed products are resolved carrierwise at every finite depth and at
every internal cut.

**Results.** Every finite routed product factors over the declared carriers.
Routed reachability therefore lies inside carrier-resolved support-path
reachability; images and ranks decompose over common endpoint carriers; and
disjoint endpoint carrier support forces exact vanishing at every finite
depth. Vanishing at a cut is equivalent to carrierwise image--kernel
containment, while a survivor recursion gives the complementary exact activity
criterion. An exact four-dimensional $Z_2$ construction separates support from
composition, and a complete one-carrier depth-two census records eight strict
within-carrier obstructions among 24 supported candidates.

**Boundary.** Carrier factorization and image--kernel equivalence are standard
linear algebra, and the all-length disjoint-carrier obstruction already appears
in Paper III. Shared carrier support is necessary for possible activity but is
not sufficient for a nonzero composition. The accompanying Rubik calculations
are bounded numerical observations, not theorem premises, exact-zero
certificates, or an all-depth classification.

**Keywords:** invariant direct sums; routed operator products; carrier
support; image--kernel obstruction; Boolean reachability; sector projectors.

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $K$, $V$ | coefficient field and finite-dimensional vector space |
| $B$, $V_b$, $\Pi_b$ | carrier labels, carrier summands, and carrier projections |
| $I$, $Q_i$ | sector labels and complete sector idempotents |
| $G$, $R_g$ | declared transport labels and carrier-preserving maps |
| $\operatorname{Supp}_B(i)$ | carrier support of sector $i$ |
| $T_{i\leftarrow j}(\mathbf g;\mathbf k)$ | one labelled routed operator product |
| $\mathcal C_d(i,j)$ | span of depth-$d$ routed products with endpoints $(j,i)$ |
| $\mathcal P_d^{(b)}$, $\mathcal P_d$, $\mathcal R_d$ | carrier paths, aggregate support paths, and active routed pairs |
| $A_r$, $B_r$ | suffix and prefix at an internal route cut |
| $W_r^{(b)}$ | carrier-local propagated survivor subspace at step $r$ |
| $D_{\mathrm{act}}(i,j)$ | minimum finite active depth, or $\infty$ |

## Introduction

This paper develops a carrier-resolved formulation of finite-depth routed
composition on a vector space with a declared direct-sum carrier decomposition,
carrier-preserving transport maps, and carrier-preserving sector projectors.

The intended lift is

$$
\text{two-step obstruction}
+\text{carrier-resolved incidence}
\quad\Longrightarrow\quad
\text{all-depth carrier accessibility}.
$$

Here *accessibility* means exact activity of declared routed products, not
Boolean graph reachability. It requires a carrier-local survival or
image--kernel test after support admission.

The main theorem factors every finite routed product carrierwise. This
separates support admission from exact activity: disjoint endpoint carrier
support gives an all-depth zero obstruction, whereas carrier overlap leaves an
exact image--kernel or survivor test inside each common carrier.

No Rubik-specific numerical fact or search convention enters the theorem. The
contribution is the unified depth-indexed carrier formulation and its explicit
separation of aggregate support paths, carrier-resolved paths, and routed
operator products.

## Related Work and Novelty Boundary

Paper III \cite{paper3} already proves that a common block decomposition preserved by every
transport and sector projector prevents any finite routed sequence from
connecting sectors with disjoint endpoint block support (Theorem 4.2 and
Corollary 4.4). It also gives the two-factor image--kernel criterion and a
recursive longer-path test. Paper VII \cite{paper7} develops the corresponding
carrier-resolved zero-product locus, rank strata, and represented incidence
profiles in its Section 6.

This paper does not reclaim those results. It places them in one
depth-indexed routed-composition object and makes four additional pieces
explicit:

1. the blockwise factorization of each complete routed product;
2. the containment from operator activity to carrier-resolved path support to
   aggregate support-path reachability;
3. the image--kernel criterion and survivor recursion at every internal cut,
   carrier by carrier; and
4. exact four-dimensional disjoint- and shared-carrier controls with a finite
   reproducibility package.

Thus Paper XX is a consolidation and extension of the Paper III--VII
carrier/route line, not a replacement proof or a new claim to the underlying
block-diagonal and zero-product facts.

Two ingredients are standard linear algebra: products of maps preserving a
common finite direct-sum decomposition remain block diagonal, and $AB=0$ if
and only if $\operatorname{im}B\subseteq\ker A$. This paper does not claim
either ingredient as a new general theorem, nor does it claim that invariant
carriers or sectorizations are canonical.

Standard treatments of invariant subspaces, direct-sum decompositions, and
block matrices are given by Horn and Johnson \cite{hornJohnson2013}. The
relation between matrix support patterns and directed graph structure belongs
to combinatorial matrix theory \cite{brualdiRyser1991}. Those backgrounds do
not supply the depth-indexed typed route interface or the exact finite controls
given here.

The contribution is the combined depth-indexed interface. Routed
products retain one carrier through every factor; carrier-resolved path
support remains distinct from operator activity and aggregate graph support;
the inherited endpoint obstruction becomes a direct factorization corollary;
and shared-carrier activity is decided by an exact survivor recursion and
cutwise image--kernel test. The exact finite controls exhibit both disjoint-
carrier and strict within-carrier obstruction.

## Carrier data

Let $V$ be a finite-dimensional vector space over a field $K$. Fix a finite
carrier index set $B$ and a direct-sum decomposition

$$
V=\bigoplus_{b\in B}V_b.
$$

Write $\Pi_b:V\to V_b\hookrightarrow V$ for the associated projection. Thus

$$
\Pi_b\Pi_c=\delta_{bc}\Pi_b,
\qquad
\sum_{b\in B}\Pi_b=I_V.
$$

Let $G$ be a set of declared transport labels. For each $g\in G$, let
$R_g\in\operatorname{End}_K(V)$ satisfy

$$
[R_g,\Pi_b]=0 \quad\text{for every }b\in B.
$$

Let $I$ be a finite sector index set. A sectorization is a family of
idempotents $Q_i\in\operatorname{End}_K(V)$ satisfying

$$
Q_iQ_j=0\ (i\ne j),
\qquad \sum_{i\in I}Q_i=I_V,
$$

and the carrier-preservation condition

$$
[Q_i,\Pi_b]=0 \quad\text{for every }i\in I,\ b\in B.
$$

Orthogonality or self-adjointness of the $Q_i$ is not needed for the
algebraic theorem. If the data are Hilbert-space projections, the same proof
applies with orthogonal direct sums.

Define the carrier component of an operator by

$$
R_g^{(b)}=\left.\Pi_bR_g\Pi_b\right|_{V_b}\in\operatorname{End}_K(V_b),
\qquad
Q_i^{(b)}=\Pi_bQ_i\Pi_b\big|_{V_b}\in\operatorname{End}_K(V_b).
$$

The carrier support of sector $i$ is

$$
\operatorname{Supp}_B(i)
 :=\{b\in B:Q_i^{(b)}\ne0\}.
$$

This is an operator support label, not a statement that every vector in
$V_b$ belongs to sector $i$.

We identify

$$
\bigoplus_{b\in B}\operatorname{End}_K(V_b)
$$

with the corresponding block-diagonal subalgebra of
$\operatorname{End}_K(V)$.

## Routed products and depth spaces

For depth $d\ge 1$, choose transport labels

$$
(g_1,\ldots,g_d)\in G^d
$$

and intermediate sectors $(k_1,\ldots,k_{d-1})\in I^{d-1}$. For endpoints
$j,i\in I$, set

$$
i_0=j,\qquad i_r=k_r\ (1\le r<d),\qquad i_d=i,
$$

and define the routed product

$$
T_{i\leftarrow j}(\mathbf g;\mathbf k)
 =Q_{i_d}R_{g_d}Q_{i_{d-1}}R_{g_{d-1}}\cdots
   Q_{i_1}R_{g_1}Q_{i_0}.
$$

For $d=1$, the middle string is empty. For $d=0$, define

$$
T_{i\leftarrow j}(\varnothing)=Q_iQ_j.
$$

The depth-$d$ routed composition space is the finite-dimensional subspace

$$
\mathcal C_d(i,j)
 =\operatorname{span}_K\{T_{i\leftarrow j}(\mathbf g;\mathbf k)\}.
$$

The definition records actual operator products. A Boolean support path is
only a candidate indexing a member of this family; it is not itself a
nonzero composition witness.

Define the direct support relation by

$$
j\longrightarrow i
\quad\Longleftrightarrow\quad
Q_iR_gQ_j\ne0\text{ for some }g\in G.
$$

Let $\mathcal P_d$ be the ordered endpoint relation defined by length-$d$
paths in this support graph. Let $\mathcal R_d$ be the routed-composition
relation

$$
(j,i)\in\mathcal R_d
\quad\Longleftrightarrow\quad
\mathcal C_d(i,j)\ne\{0\}.
$$

> **Proposition 1 (Support Overapproximation).** For every $d\ge1$,
>
> $$
> \mathcal R_d\subseteq\mathcal P_d.
> $$

### Proof

If one routed product is nonzero, none of its adjacent projected factors

$$
Q_{k_r}R_{g_r}Q_{k_{r-1}}
$$

can be zero. Each factor therefore supplies the corresponding edge of a
length-$d$ support path. $\square$

For each carrier $b$, define the carrier-restricted direct support relation by

$$
j\longrightarrow_b i
\quad\Longleftrightarrow\quad
Q_i^{(b)}R_g^{(b)}Q_j^{(b)}\ne0
\text{ for some }g\in G,
$$

and let $\mathcal P_d^{(b)}$ be its length-$d$ path relation. The carrier
factorization below gives the sharper three-level containment

$$
\mathcal R_d\subseteq\bigcup_{b\in B}\mathcal P_d^{(b)}
\subseteq\mathcal P_d.
$$

The first inclusion is an all-depth operator statement; the second forgets
the carrier label. A path in $\mathcal P_d$ can therefore be stitched from
edges on different carriers and fail to represent one block-diagonal routed
product.

The inclusion need not be equality. Theorem 2 below gives a structural
sufficient condition for strictness: a support path whose endpoints have
disjoint carrier support belongs to $\mathcal P_d\setminus\mathcal R_d$.

## All-depth carrier factorization theorem

> **Theorem 2 (All-Depth Carrier Factorization).**
> Under the carrier data above, every routed product has the blockwise
> decomposition
>
> $$
> T_{i\leftarrow j}(\mathbf g;\mathbf k)
> =\bigoplus_{b\in B}
> T^{(b)}_{i\leftarrow j}(\mathbf g;\mathbf k),
> $$
>
> where
>
> $$
> T^{(b)}_{i\leftarrow j}(\mathbf g;\mathbf k)
> =Q_i^{(b)}R_{g_d}^{(b)}Q_{k_{d-1}}^{(b)}\cdots
> Q_{k_1}^{(b)}R_{g_1}^{(b)}Q_j^{(b)}
> \in\operatorname{End}_K(V_b).
> $$
>
> Consequently,
>
> $$
> \mathcal C_d(i,j)
> \subseteq
> \bigoplus_{b\in
> \operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)}
> \operatorname{End}_K(V_b).
> $$
>
> In particular, if
>
> $$
> \operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)=\varnothing,
> $$
>
> then
>
> $$
> T_{i\leftarrow j}(\mathbf g;\mathbf k)=0
> \quad\text{for every finite depth }d\ge0,
> $$
>
> and hence $\mathcal C_d(i,j)=\{0\}$ for every $d$.

### Proof

The commutation hypotheses imply that every transport and every sector
projector is block diagonal for the direct sum $V=\bigoplus_bV_b$:

$$
R_g=\bigoplus_{b\in B}R_g^{(b)},
\qquad
Q_\ell=\bigoplus_{b\in B}Q_\ell^{(b)}.
$$

Products of block-diagonal operators are block diagonal, and multiplication
of direct sums is componentwise. Substituting these decompositions into the
definition of $T_{i\leftarrow j}$ gives

$$
T_{i\leftarrow j}
 =\bigoplus_{b\in B}
 \left(Q_i^{(b)}R_{g_d}^{(b)}Q_{k_{d-1}}^{(b)}\cdots
 Q_{k_1}^{(b)}R_{g_1}^{(b)}Q_j^{(b)}\right),
$$

which is the asserted factorization.

The same blockwise calculation proves the sharper inclusion above: if a
routed product is nonzero, at least one carrier component is nonzero, and
that component supplies a path in $\mathcal P_d^{(b)}$.

If $b\notin\operatorname{Supp}_B(i)$, then $Q_i^{(b)}=0$; if
$b\notin\operatorname{Supp}_B(j)$, then $Q_j^{(b)}=0$. Therefore a component
can be nonzero only when $b$ lies in the intersection of the endpoint
supports. This proves the containment and, when the intersection is empty,
the all-depth zero conclusion. The depth-zero case is the same calculation
with $T_{i\leftarrow j}=Q_iQ_j$. $\square$

> **Corollary 2.1 (Strict Support--Composition Separation).** If a length-$d$
> support path joins endpoints $j,i$ with
> $\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)=\varnothing$, then
>
> $$
> (j,i)\in\mathcal P_d\setminus\mathcal R_d.
> $$

### Proof

The path gives membership in $\mathcal P_d$. Theorem 2 makes every routed
product with those endpoints zero, so the pair is absent from
$\mathcal R_d$. $\square$

## Rank and image consequences

The factorization gives more than a zero test.

> **Corollary 2.2 (Carrierwise Image Bound).** For every routed product,
>
> $$
> \operatorname{im}T_{i\leftarrow j}
> \subseteq
> \bigoplus_{b\in\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)}V_b.
> $$

> **Corollary 2.3 (Rank Additivity).** Over the declared field $K$,
>
> $$
> \operatorname{rank}T_{i\leftarrow j}
> =\sum_{b\in B}\operatorname{rank}
> T^{(b)}_{i\leftarrow j}.
> $$

### Proof

The image of a block-diagonal map is the direct sum of the images of its
carrier components. Dimensions of finite direct sums add, giving both claims.
$\square$

For the depth spaces, define the carrier projection

$$
\operatorname{pr}_b:\mathcal C_d(i,j)\to\operatorname{End}_K(V_b)
$$

by taking the $b$-th block. Theorem 2 implies

$$
\mathcal C_d(i,j)\subseteq
\bigoplus_{b\in\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)}
\operatorname{pr}_b(\mathcal C_d(i,j)).
$$

This is a carrierwise support envelope for routed composition. The block
resolution of each operator is exact, but the displayed inclusion does not
assert that every combination of carrierwise components is realized by one
common route.

### Carrier profiles and minimum active depth

The **carrier profile** of sector $i$ is the finite rank vector

$$
\mathbf p_i
=\left(\operatorname{rank}Q_i^{(b)}\right)_{b\in B}.
$$

Its nonzero coordinates recover $\operatorname{Supp}_B(i)$. This vector
distinguishes pure sectors, supported on one carrier, from hybrid sectors,
supported on more than one carrier, while retaining the carrierwise sector
dimensions discarded by a Boolean label.

Define the minimum active depth

$$
D_{\mathrm{act}}(i,j)
=\inf\{d\ge1:\mathcal C_d(i,j)\ne\{0\}\},
$$

with value $\infty$ when no finite active depth exists.
This is the minimum **positive** active depth; the depth-zero identity-sector
case is intentionally excluded.

> **Corollary 2.4 (Carrier and Graph Lower Gates).** If
> $D_{\mathrm{act}}(i,j)<\infty$, then
>
> $$
> \operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)\ne\varnothing
> $$
>
> and
>
> $$
> \operatorname{dist}_{\mathcal G}(j,i)
> \le D_{\mathrm{act}}(i,j).
> $$

### Proof

The first condition is the contrapositive of Theorem 2. The second follows
from Proposition 1 at the first active depth. $\square$

Neither gate is sufficient. Shared carrier support can still fail the
image--kernel criterion, and a shortest graph path can be operator-inactive.
A finite census through depth $N$ therefore records only
$D_{\mathrm{act}}(i,j)\le N$ or "not observed through $N$"; it cannot replace
$\infty$ by a finite-search null value.

## Arbitrary-depth image--kernel obstruction

Every internal cut of a route supplies an exact obstruction criterion. For a
depth-$d$ route and $1\le r<d$, write

$$
B_r
=Q_{i_r}R_{g_r}Q_{i_{r-1}}\cdots Q_{i_1}R_{g_1}Q_{i_0}
$$

for the routed prefix, and write

$$
A_r
=Q_{i_d}R_{g_d}Q_{i_{d-1}}\cdots R_{g_{r+1}}Q_{i_r}
$$

for the routed suffix. Then the full routed product is $A_rB_r$. Under the
carrier hypotheses, both factors preserve every $V_b$; define their carrier
blocks by

$$
A_r^{(b)}:=A_r\big|_{V_b}\in\operatorname{End}_K(V_b),
\qquad
B_r^{(b)}:=B_r\big|_{V_b}\in\operatorname{End}_K(V_b).
$$

> **Theorem 3 (Arbitrary-Depth Image--Kernel Criterion).** At every internal
> cut $r$,
>
> $$
> T_{i\leftarrow j}(\mathbf g;\mathbf k)=0
> \quad\Longleftrightarrow\quad
> \operatorname{im}B_r\subseteq\ker A_r.
> $$
>
> Under the carrier hypotheses of Theorem 2, this is equivalent to
>
> $$
> \operatorname{im}B_r^{(b)}\subseteq\ker A_r^{(b)}
> \quad\text{for every }b\in B.
> $$

### Proof

For arbitrary linear maps $A_r$ and $B_r$, the product $A_rB_r$ is zero
exactly when $A_r$ annihilates every vector in the image of $B_r$. This proves
the first equivalence. Theorem 2 makes both prefix and suffix block diagonal,
so $A_rB_r=\bigoplus_b A_r^{(b)}B_r^{(b)}$. A direct-sum operator is zero
exactly when every component is zero; applying the first equivalence on each
$V_b$ gives the carrierwise statement. $\square$

### Carrierwise survivor recursion and promotion

The cut criterion separates the structural obstruction from the
within-carrier promotion problem. For every carrier $b$, define

$$
W_0^{(b)}=\operatorname{im}Q_j^{(b)},
\qquad
W_r^{(b)}=Q_{i_r}^{(b)}R_{g_r}^{(b)}W_{r-1}^{(b)}
\quad(1\le r\le d).
$$

> **Theorem 4 (Carrierwise Survivor Recursion and Promotion).** For every
> declared route,
>
> $$
> \operatorname{im}T_{i\leftarrow j}(\mathbf g;\mathbf k)
> =\bigoplus_{b\in B}W_d^{(b)}.
> $$
>
> Consequently,
>
> $$
> T_{i\leftarrow j}(\mathbf g;\mathbf k)\ne0
> \quad\Longleftrightarrow\quad
> W_d^{(b)}\ne\{0\}\text{ for at least one }b\in B.
> $$

### Proof

The restriction of the routed product to $V_b$ is the carrier-local product
from Theorem 2. Its image is obtained by starting with
$\operatorname{im}Q_j^{(b)}$ and applying the carrier-local factors in route
order, which is precisely the recursion defining $W_d^{(b)}$. The full product
is the direct sum of these restrictions, so its image is the direct sum of
their images. A finite direct sum is nonzero exactly when at least one summand
is nonzero. $\square$

At each step this gives the exact local survival gate

$$
W_r^{(b)}\ne\{0\}
\quad\Longleftrightarrow\quad
W_{r-1}^{(b)}\not\subseteq
\ker\!\left(Q_{i_r}^{(b)}R_{g_r}^{(b)}\right).
$$

Equivalently, fix one route, cut, and carrier $b$. Set

$$
A_b=A_r^{(b)},
\qquad B_b=B_r^{(b)}.
$$

Then

$$
T^{(b)}_{i\leftarrow j}=A_bB_b=0
\quad\Longleftrightarrow\quad
\operatorname{im}B_b\subseteq\ker A_b.
$$

Thus the all-depth theory has the precise boundary:

$$
\begin{aligned}
\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)=\varnothing
&\quad\Longrightarrow\quad
T_{i\leftarrow j}=0\text{ at every finite depth},\\
\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)\ne\varnothing
&\quad\Longrightarrow\quad
\text{an exact survivor/image--kernel test is still required}.
\end{aligned}
$$

![Endpoint carrier support supplies an exact all-depth obstruction only in the
disjoint case. Carrier overlap admits a route to the carrier-local survivor or
image--kernel test; it does not establish a nonzero composition.](../../figures/paper20/fig1_carrier_survivor_gate.png)

An intermediate sector can carry edges incident to different carriers. That
incidence does not mix carriers, because every inserted operator is block
diagonal. A graph route may therefore exist while every carrier component of
the routed product vanishes.

The shared-carrier promotion condition is strict rather than heuristic: the
full route is active exactly when at least one carrier violates the
image--kernel containment. In particular, it is sufficient that, for one
carrier $b$, $B_b\ne0$ and $A_b$ is injective on
$\operatorname{im}B_b$. It is also sufficient that
$\operatorname{im}B_b=\operatorname{im}Q_{k_r}^{(b)}$ and $A_b\ne0$.

## Sharpness and examples

At the level of endpoint carrier support alone, disjointness gives the
strongest unconditional vanishing conclusion available here.
If the endpoints share a carrier $b$, the theorem only says that the product
may live on $V_b$; it does not force it to vanish. For example, with one
carrier $B=\{b\}$ and $Q_i=Q_j=R_g=I$, every depth product is $I$.

Conversely, shared carrier support is not sufficient for nonzero composition.
Take $V_b=K^2$, let $Q_j$ project onto the first coordinate and let the
leftmost factor in a route project onto the second coordinate. The endpoint
supports both equal $\{b\}$, but the routed product is zero by
image--kernel containment.

The theorem is therefore sharp at the level claimed: endpoint carrier
disjointness is sufficient for all-depth vanishing, while carrier overlap is
only a necessary gate for possible activity.

> **Proposition 5 (Exact Four-Dimensional Z2 Witness).** There is a
> four-dimensional representation of $Z_2$ and a three-sector decomposition
> for which $\mathcal R_2\subsetneq\mathcal P_2$, while the missing endpoint
> pair is inactive at every finite depth.

### Construction and proof

Let $V=A\oplus B$ with ordered basis $(a_0,a_1,b_0,b_1)$ and let the
nonidentity element $s\in Z_2$ act by

$$
R_s(a_0)=a_1,\quad R_s(a_1)=a_0,
\qquad
R_s(b_0)=b_1,\quad R_s(b_1)=b_0.
$$

Let $Q_0,Q_1,Q_2$ be the coordinate projectors onto the sectors

$$
\operatorname{im}Q_0=\operatorname{span}\{a_0\},\qquad
\operatorname{im}Q_1=\operatorname{span}\{a_1,b_0\},\qquad
\operatorname{im}Q_2=\operatorname{span}\{b_1\}.
$$

Then

$$
Q_1R_sQ_0\ne0,
\qquad
Q_2R_sQ_1\ne0,
$$

so the support graph contains $0\to1\to2$. However,

$$
Q_2R_sQ_1R_sQ_0=0.
$$

Indeed, the first step lands in $Ka_1\subset A$, and every later factor
preserves $A\oplus B$, while $Q_2$ is supported only on $B$. More strongly,
Theorem 2 gives $\mathcal C_d(2,0)=\{0\}$ for every $d$. This is an exact
finite witness of strict support--composition inclusion; no numerical
tolerance is involved in the statement or proof.

### Exact shared-carrier obstruction census

A second four-dimensional control uses one carrier $V_b=K^4$, three coordinate
sectors of dimensions $(1,2,1)$, and two permutation transports

$$
g=(0\ 1),\qquad h=(2\ 3).
$$

Every nonzero sector has the same carrier support $\{b\}$. Nevertheless,

$$
Q_1R_gQ_0\ne0,
\qquad
Q_2R_hQ_1\ne0,
\qquad
Q_2R_hQ_1R_gQ_0=0.
$$

The incoming image is $Ke_1$, whereas the outgoing factor is supported on the
$e_2$ direction inside the same intermediate sector. This is strict
within-carrier image--kernel containment, not a disjoint-endpoint obstruction.

The exact census enumerates all $3^3\cdot2^2=108$ depth-two labelled routes in
this model. It finds 24 routes with two nonzero adjacent
factors, of which 16 have nonzero products and eight are strict
shared-carrier obstructions. Every matrix entry and rank is evaluated over
integers; no tolerance is used. This finite result is a **Computational
Certificate** for the declared model, not a frequency or genericity theorem.

## Finite Evidence Scope and Cross-Paper Boundary

A finite census is interpretable only after separately declaring:

1. the carrier decomposition and exact carrier-support rule;
2. the finite generator and sector sets;
3. the routed depth range and route enumeration policy;
4. the within-carrier product or image--kernel test;
5. the coefficient domain, numerical tolerance, and exactness status.

The theorem does not validate a numerical sector registration. It only says
what follows once the carrier-preservation hypotheses and the carrier labels
are established.

**Relation to Paper XXI.** Paper XXI studies a specific marked projective
finite-field route family by pole/preimage arithmetic. The two papers belong
to the same carrier/route research line, but no theorem dependency is claimed
at present. In particular, Paper XXI is not a corollary of the carrier
factorization proved here: it does not currently register a decomposition
$V=\bigoplus_b V_b$ and verify that
its labelled generators and marked-sector projectors preserve every declared
carrier. No cross-paper implication follows without those data and explicit
verification of the carrier hypotheses.

## Claim Status and Boundary

The accompanying evidence consists of an exact shared-carrier census, finite
control censuses, and a Rubik depth-two image--kernel audit. The shared-carrier
census uses integer permutation and projector matrices. Statements obtained
from `complex128` norms remain bounded numerical
observations, including the observation that the audited Rubik products lie
below the declared tolerance. They do not establish exact projected zero or
an all-depth Rubik classification. The exact $Z_2$ all-depth conclusion follows
from the displayed construction and Theorem 2, not from its floating-point
replay.

No claim is made that a carrier decomposition is canonical, that Boolean graph
support implies an active routed composition, that a bounded null establishes
all-depth vanishing, or that shared carrier support alone guarantees a nonzero
product.

| Statement | Status | Provenance or role |
|---|---|---|
| Carrierwise factorization of every finite routed product | Theorem | explicit all-depth routed formulation of the common-block argument |
| All-depth zero for disjoint endpoint carrier support | Theorem | antecedent in Paper III; recovered here as a factorization corollary |
| Routed activity lies inside carrier-path and support-path reachability | Proposition | depth-indexed three-level containment |
| Disjoint-carrier graph path gives strict inclusion | Corollary | consequence of factorization plus a declared support path |
| Cutwise carrier image--kernel criterion | Theorem | arbitrary-cut formulation of the standard zero-product test |
| Carrierwise survivor recursion and exact promotion | Theorem | all-depth shared-carrier activity criterion |
| Exact four-dimensional Z2 separation witness | Proposition | new exact finite witness in this paper |
| Exact one-carrier obstruction census | Computational Certificate | 8 strict obstructions among 24 supported candidates |
| Carrierwise image bound | Corollary | direct factorization consequence |
| Rank additivity across carriers | Corollary | standard direct-sum consequence |
| Carrier profile and minimum active depth | Definition | paper-local typed summary |
| Shared carriers imply nonzero routed composition | False in general | excluded converse |
| Graph path implies nonzero routed composition | False in general | excluded promotion |
| Rubik 228-dimensional census | Computational Observation | bounded evidence; not theorem proof |
| Higher-depth Rubik accessibility classification | Research Program | open application problem |

## Conclusion

A declared carrier decomposition resolves each routed sector composition into
within-carrier products. In the Paper III--VII line this recovers the exact
all-depth zero obstruction for disjoint endpoint carriers, while the present
depth-indexed formulation also exposes carrier-resolved path containment,
survivor recursion, and the image--kernel test at every cut. Shared carrier
support is not a conclusion but an admission gate: exact activity occurs only
when at least one carrier-local propagated image survives.
Boolean support paths are therefore candidate routes rather than composition
witnesses. Exact applications must establish carrier preservation and zero
tests in their declared coefficient domain; bounded numerical applications
must retain their tolerance and evidence status.

## Appendix A: Computational Artifacts

The default directory is `experiments/paper20/`. The A7 receipt records exact
artifact paths and digests; its exact receipt and closure digests and validation
boundary are indexed in `README.md`. The listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite). They support the
finite evidence surfaces and bind the local release closure; they do not
replace the manuscript proofs.

| Artifact | Role | Short path |
|---|---|---|
| A1 | exact shared-carrier producer | `within_carrier_census.py` |
| A2 | exact shared-carrier result | `results/within_carrier_obstruction_v1.json` |
| A3 | exact shared-carrier validator | `validate_within_carrier_census.py` |
| A4 | bounded carrier census producer and validator | `census.py`, `validate_results.py` |
| A5 | Rubik depth-two image--kernel bundle | `image_kernel_census.py`, `results/image_kernel/` |
| A6 | Rubik image--kernel validator | `validate_image_kernel.py` |
| A7 | release manifest and local closure receipt | `release-manifest.json`, `results/carrier_accessibility_v1.release-receipt.json` |

The A7 receipt performs **local closure verification**, not independent
validation. Its ordered artifact closure excludes the receipt itself. The
manifest is an upstream closure declaration and therefore does not contain the
receipt digest; the exact receipt SHA-256 is recorded only in the downstream
README index. Thus no artifact in the receipt closure depends on the receipt
as a premise.
