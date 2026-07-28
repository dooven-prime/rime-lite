# Incidence Geometry of Projected Operator Composition

### Rank Protection, Image--Kernel Alignment, and Promotion Limits

**WuJun Chen**

Independent Researcher | RIME Project | 2026

***

## Abstract

**Problem.** Let $A:\mathbb C^n\to\mathbb C^m$ and
$B:\mathbb C^p\to\mathbb C^n$ be nonzero. Their product can nevertheless
vanish. In a sectorized operator setting, this is the basic obstruction to
promoting a Boolean support path through an intermediate sector to a nonzero
projected composition.

**Approach.** We study the closed zero-product locus

$$
Z=\{(A,B):AB=0\}
$$

and its constructible nonzero-factor part. The identity
$AB=0\iff\operatorname{im}B\subseteq\ker A$ turns product failure into an
image--kernel incidence condition. We stratify this condition by
$\operatorname{rank}A=r$ and by the double rank
$(\operatorname{rank}A,\operatorname{rank}B)=(r,s)$.

**Results.** The fixed-$r$ stratum has

$$
\dim I_r=r(m+n-r)+p(n-r),
\qquad
\operatorname{codim}I_r=(m-r)(n-r)+pr.
$$

The fixed-$(r,s)$ incidence stratum has

$$
\dim I_{r,s}
=r(m+n-r)+s(n-r+p-s),
$$

and has relative codimension $rs$ inside the ambient rank-$(r,s)$ matrix-pair
stratum. Full column rank of $A$, or full row rank of $B$, excludes nonzero
zero-products and gives quantitative singular-value lower bounds. A corrected
computational audit distinguishes both-protected, left-only, right-only,
unprotected-nonzero, and unprotected-zero routed products. In the declared
Rubik realization, 2592 nonzero-factor routed records split into 2016
unprotected nonzero products and 576 machine-zero image--kernel alignments.

**Boundary.** These results concern one routed product. They do not identify a
support path with a routed product, a routed product with a full word, a full
word with a commutator, or low-order commutator support with Lie depth.
Likewise, high codimension in the free matrix-pair space does not determine the
pullback incidence geometry of a representation-derived family.

***

## Introduction

The local question is elementary:

> Why can $A\ne0$ and $B\ne0$ coexist with $AB=0$?

The answer is exact:

$$
\operatorname{im}B\subseteq\ker A.
$$

This condition is invisible to Boolean factor support. It depends on the
relative position of two subspaces in the intermediate vector space. For
projected operator blocks, it is therefore the first geometric datum that must
be checked after a support path has been found.

The paper has three goals.

1. Give the rank-stratified geometry of the zero-product condition.
2. State the correct rectangular rank-protection criteria.
3. Separate local incidence from every stronger promotion involving route
   sums, words, commutators, Lie depth, or representation-derived parameter
   families.

The analysis is static: the sector projectors and operator family are fixed.
Moving projectors, normal spectral charts, and parameter-dependent pullbacks
remain research directions.

The image--kernel obstruction is adjacent to two independent questions. First,
Boolean graph paths need not survive projected matrix composition. Second,
nonzero word terms need not survive antisymmetrization into a commutator.
These neighboring failures motivate the promotion table below, but the
corresponding theorems are not assumed here. The incidence and
rank-protection criteria can serve as route-survival gates, but do not promote
routed products to word or Lie accessibility.

***

## Notation and Claim Layers {.unnumbered}

The notation is introduced below in the order required by the routed-product
problem. The claim-status vocabulary is **Theorem** for exact statements under
their stated hypotheses, **Computational Certificate** only when a finite
numerical check is explicitly assigned that status, **Computational
Observation** for the declared Rubik, random-control, perturbation, and
finite-atlas records, and **Research Program** for represented pullback
geometry and all stronger promotion statements that remain open. The complete
status table appears in Section~\ref{sec:claim-status-and-boundary}.

Let $V$ be a finite-dimensional complex Hilbert space with a complete
orthogonal sectorization

$$
V=\bigoplus_{i\in\mathcal I}E_i,
\qquad
I=\sum_{i\in\mathcal I}Q_i,
\qquad
Q_iQ_j=\delta_{ij}Q_i.
$$

Let $\mathcal Y=\{Y_a\}_{a\in\mathcal A}$ be a declared finite operator
family. No commutant assumption is imposed.

For a sector triple $(i,k,j)$ and ordered operator pair $(a,b)$, define

$$
A_{ik}^a
=Q_iY_aQ_k:E_k\to E_i,
\qquad
B_{kj}^b
=Q_kY_bQ_j:E_j\to E_k.
$$

Write

$$
d_i=\dim E_i,\qquad d_k=\dim E_k,\qquad d_j=\dim E_j.
$$

The routed projected composition is

$$
T_{ikj}^{a,b}
=
Q_iY_aQ_kY_bQ_j
=
A_{ik}^aB_{kj}^b.
$$

Our arrow convention is

$$
j\longrightarrow k\longrightarrow i.
$$

A support path records only

$$
A_{ik}^a\ne0,\qquad B_{kj}^b\ne0.
$$

It does not record whether $T_{ikj}^{a,b}$ is nonzero.

The full two-letter word block is a different object:

$$
W_{ij}^{a,b}
=Q_iY_aY_bQ_j
=\sum_{k\in\mathcal I}T_{ikj}^{a,b}.
$$

If the declared family is a skew-Hermitian Lie family
$\mathcal X=\{X_g\}$, then the projected commutator is

$$
C_{ij}^{g,h}
=Q_i[X_g,X_h]Q_j
=W_{ij}^{g,h}-W_{ij}^{h,g}.
$$

These three objects -- routed term, full word, and commutator -- remain
separate throughout the paper.

***

## Image--Kernel Incidence

### Theorem 3.1 (Image--Kernel Criterion)

Let

$$
A:\mathbb C^n\to\mathbb C^m,
\qquad
B:\mathbb C^p\to\mathbb C^n.
$$

Then

$$
AB=0
\quad\Longleftrightarrow\quad
\operatorname{im}B\subseteq\ker A.
$$

**Proof.** If $AB=0$, then $A(Bv)=0$ for every $v\in\mathbb C^p$, so every
vector in $\operatorname{im}B$ lies in $\ker A$. Conversely, if
$\operatorname{im}B\subseteq\ker A$, then $A(Bv)=0$ for every $v$, hence
$AB=0$. $\square$

### Closed and constructible loci

Define

$$
Z_{m,n,p}
=
\{(A,B)\in
\operatorname{Mat}_{m\times n}(\mathbb C)
\times
\operatorname{Mat}_{n\times p}(\mathbb C):AB=0\}.
$$

The entries of $AB$ are polynomial in the entries of $A$ and $B$, so
$Z_{m,n,p}$ is a closed affine algebraic set.

The nonzero-factor incidence locus is

$$
Z_{m,n,p}^{\times}
=
Z_{m,n,p}\cap\{A\ne0\}\cap\{B\ne0\}.
$$

It is constructible, not generally a closed subvariety. Fixed exact-rank
pieces are locally closed strata.

### Proposition 3.2 (Ambient Generic Nonincidence)

The complement of $Z_{m,n,p}$ is a nonempty Zariski-open dense subset of the
free matrix-pair space. Consequently, $Z_{m,n,p}$ and
$Z_{m,n,p}^{\times}$ have Lebesgue measure zero.

**Proof.** The zero-product equations are polynomial, and they do not vanish
identically on the ambient matrix-pair space. Thus their common zero set is a
proper closed algebraic subset. Its complement is nonempty, Zariski open, and
dense; every proper complex algebraic subset has real Lebesgue measure zero.
$\square$

This proposition concerns freely varying matrix pairs. It makes no statement
about a constrained parameter family whose image may lie partly or entirely
inside $Z_{m,n,p}$.

***

## Rank-Stratified Geometry

### Theorem 4.1 (Fixed-A-Rank Incidence Stratum)

For $0\le r\le\min(m,n)$, let

$$
I_r
=
\{(A,B):\operatorname{rank}A=r,\ AB=0\}.
$$

Then $I_r$ is locally closed and

$$
\dim I_r
=
r(m+n-r)+p(n-r).
$$

Its codimension in
$\operatorname{Mat}_{m\times n}\times\operatorname{Mat}_{n\times p}$ is

$$
\operatorname{codim}I_r
=
(m-r)(n-r)+pr.
$$

**Proof.** The rank-$r$ matrices $A$ form a locally closed stratum of
dimension $r(m+n-r)$. For fixed $A$, the condition $AB=0$ requires every
column of $B$ to lie in the $(n-r)$-dimensional space $\ker A$. The fiber has
dimension $p(n-r)$. Adding base and fiber dimensions gives the first formula.
Subtracting from the ambient dimension $mn+np$ gives the codimension formula.
$\square$

For the nonzero-factor locus, the admissible $A$-ranks are exactly

$$
1\le r\le\min(m,n-1).
$$

The upper bound is $r<n$, not $r<\min(m,n)$. In particular, if $m<n$, a
full-row-rank matrix with $r=m$ still has a nontrivial kernel and can
participate in a nonzero zero-product.

### Theorem 4.2 (Fixed Double-Rank Incidence Stratum)

Let

$$
I_{r,s}
=
\{(A,B):
\operatorname{rank}A=r,\qquad
\operatorname{rank}B=s,\qquad
AB=0\}.
$$

This stratum is nonempty exactly when

$$
0\le r\le\min(m,n),
\qquad
0\le s\le\min(n-r,p).
$$

When nonempty,

$$
\dim I_{r,s}
=
r(m+n-r)+s(n-r+p-s).
$$

**Proof.** Choose a rank-$r$ matrix $A$, contributing
$r(m+n-r)$ dimensions. Its kernel has dimension $n-r$. A rank-$s$ map
$B:\mathbb C^p\to\ker A$ exists exactly when
$s\le\min(n-r,p)$ and belongs to a rank-$s$ matrix stratum of dimension
$s(n-r+p-s)$. $\square$

### Corollary 4.3 (Relative Codimension by Rank Product)

Inside the ambient rank-pair stratum

$$
\{(A,B):\operatorname{rank}A=r,\ \operatorname{rank}B=s\},
$$

the incidence condition $AB=0$ has relative codimension

$$
rs.
$$

**Proof.** The ambient rank-pair stratum has dimension

$$
r(m+n-r)+s(n+p-s).
$$

Subtracting the dimension in Theorem 4.2 gives $rs$. $\square$

This formula isolates the alignment cost after the two ranks have already
been fixed. Rank deficiency and image--kernel alignment are distinct
conditions.

### Corollary 4.4 (Square-Block Asymptotics)

For $m=n=p=d$ and $1\le r\le d-1$,

$$
\operatorname{codim}I_r
=(d-r)^2+dr
=d^2-dr+r^2.
$$

The minimum is attained at the integer or integers nearest $d/2$, and equals

$$
\left\lceil\frac{3d^2}{4}\right\rceil.
$$

Thus the dominant nonzero-factor incidence stratum has codimension
asymptotic to $3d^2/4$ in the $2d^2$-dimensional free matrix-pair space.

![Exact fixed-rank codimension values for square blocks. The blue bars show the minimum of $\operatorname{codim}I_r=(d-r)^2+dr$ over admissible nonzero ranks, against the $2d^2$ ambient dimension and the $3d^2/4$ asymptotic. This is an ambient free-matrix calculation, not a represented pullback codimension.](../../figures/paper7/fig1_incidence_codimension.png)

***

## Rank Protection

Return to a sector triple:

$$
A:E_k\to E_i,
\qquad
B:E_j\to E_k,
\qquad
d_k=\dim E_k.
$$

Define

$$
L=[\operatorname{rank}A=d_k],
\qquad
R=[\operatorname{rank}B=d_k].
$$

The condition $L$ means that $A$ has full column rank, which is possible only
when $d_i\ge d_k$. Similarly, the condition $R$ means that $B$ has full row
rank, which is possible only when $d_j\ge d_k$.

### Theorem 5.1 (Rank-Protected Product Survival)

Let $A\ne0$ and $B\ne0$.

1. If $\operatorname{rank}A=d_k$, then $AB\ne0$.
2. If $\operatorname{rank}B=d_k$, then $AB\ne0$.

More quantitatively,

$$
\|AB\|_F
\ge
\sigma_{\min}(A)\|B\|_F
$$

when $A$ has full column rank, and

$$
\|AB\|_F
\ge
\sigma_{\min}(B)\|A\|_F
$$

when $B$ has full row rank.

**Proof.** Full column rank gives $\ker A=0$, so Theorem 3.1 rules out
$AB=0$ for nonzero $B$. Applying the smallest-singular-value inequality to
each column of $B$ gives the first norm bound. For the dual statement, use
$(AB)^\ast=B^\ast A^\ast$ and note that $B^\ast$ has full column rank with
the same positive singular values as $B$. $\square$

The condition

$$
\operatorname{rank}A=\min(d_i,d_k)
$$

is not sufficient for left protection. If $d_i<d_k$, such a matrix has
maximum possible rank but still has a nonzero kernel. The analogous warning
holds for $B$ when $d_j<d_k$.

The five mutually exclusive audit classes are:

| Class | Condition |
|-------|-----------|
| both-protected | $L\wedge R$ |
| left-only | $L\wedge\neg R$ |
| right-only | $\neg L\wedge R$ |
| unprotected-nonzero | $\neg L\wedge\neg R\wedge AB\ne0$ |
| unprotected-zero | $\neg L\wedge\neg R\wedge AB=0$ |

Protected records are still required to evaluate $AB$ numerically. Rank
protection is used as a theorem-level cross-check, not as a branch that skips
the product calculation.

***

## Promotion Limits

The local incidence theorem resolves only the first matrix-composition gate.
For fixed $i,k,j,g,h$, the following implications are invalid without
additional hypotheses:

| Local datum | Stronger conclusion | Missing promotion condition |
|-------------|---------------------|-----------------------------|
| $A\ne0$, $B\ne0$ | $T_{ikj}^{g,h}\ne0$ | image--kernel nonalignment or rank protection |
| some $T_{ikj}^{g,h}\ne0$ | $W_{ij}^{g,h}\ne0$ | no cancellation in the sum over $k$ |
| $W_{ij}^{g,h}\ne0$ and $W_{ij}^{h,g}\ne0$ | $C_{ij}^{g,h}\ne0$ | no antisymmetric cancellation |
| low-order Lie support | finite or exact $D_{\mathrm{Lie}}(i,j)$ | higher Hall data and closure/saturation certificate |
| high ambient codimension | rare represented incidence | nondegenerate pullback or transversality of the parameter map |

Equivalently,

$$
\begin{aligned}
\text{support path}
&\not\Longrightarrow
T_{ikj}^{g,h}\ne0,\\
T_{ikj}^{g,h}\ne0
&\not\Longrightarrow
W_{ij}^{g,h}\ne0,\\
W_{ij}^{g,h},W_{ij}^{h,g}\ne0
&\not\Longrightarrow
C_{ij}^{g,h}\ne0.
\end{aligned}
$$

The first failure is controlled exactly by image--kernel incidence for the
declared route. The second is a sum-over-routes cancellation problem. The
third is an antisymmetrization problem. None is interchangeable with the
others.

### Ambient versus represented incidence

Let a constrained family be parameterized by

$$
\Phi:\Theta
\longrightarrow
\operatorname{Mat}_{m\times n}
\times
\operatorname{Mat}_{n\times p}.
$$

Its incidence locus is

$$
\Phi^{-1}(Z_{m,n,p}).
$$

Ambient codimension does not determine the dimension of this pullback. A
promotion from ambient genericity to a represented family requires, at
minimum, evidence that $\Phi(\Theta)$ is not contained in $Z_{m,n,p}$ and a
suitable transversality or nondegeneracy statement on the relevant rank
strata. Symmetry may force a family into incidence despite the high ambient
codimension.

***

## Exact and Computational Case Studies

The displayed integer examples are exact. All remaining claims in this section
are finite numerical observations and are not used to prove the incidence
theorems.

### Declared numerical policy

The projected-composition audit uses:

| Quantity | Policy |
|----------|--------|
| support | $\|A\|_F,\|B\|_F>10^{-8}$ |
| numerical rank | singular values above $\max(10^{-12},10^{-9}\sigma_{\max})$ |
| product nonzero | $\|AB\|_F>10^{-12}+10^{-10}\|A\|_F\|B\|_F$ |
| normalized product | $\eta(A,B)=\|AB\|_F/(\|A\|_F\|B\|_F)$ |
| image--kernel action | $\|AU_B\|_F$, where $U_B$ spans $\operatorname{im}B$ |
| subspace residual | $\delta_{\mathrm{inc}}(A,B)=\|(I-P_{\ker A})U_B\|_F$ |

Here the columns of $U_B$ are an orthonormal basis of $\operatorname{im}B$ and
$P_{\ker A}$ is the orthogonal projector onto $\ker A$. The reported
$\delta_{\mathrm{inc}}$ is not divided by $\sqrt{\operatorname{rank}B}$.
Small $\eta(A,B)$ is a numerical alignment diagnostic, not an exact incidence
proof. Every protected record is still multiplied, and a numerically protected
zero-product triggers an assertion.

### Exact integer examples

Five explicit integer matrix pairs realize all five audit classes. In the
table, $r_A=\operatorname{rank}A$ and $r_B=\operatorname{rank}B$.

| Example | $(m,n,p)$ | $(r_A,r_B)$ | Outcome |
|---------|-----------|-------------|---------|
| both | $(2,2,2)$ | $(2,2)$ | $AB\ne0$ |
| left only | $(3,2,1)$ | $(2,1)$ | $AB\ne0$ |
| right only | $(1,2,3)$ | $(1,2)$ | $AB\ne0$ |
| unprotected, nonzero | $(2,2,2)$ | $(1,1)$ | $AB\ne0$ |
| unprotected, zero | $(2,2,2)$ | $(1,1)$ | $AB=0$ |

A concrete integer realization is

1. both protected:
   $A=I_2$ and $B=\begin{psmallmatrix}1&2\\3&4\end{psmallmatrix}$;
2. left only:
   $A=\begin{psmallmatrix}1&0\\0&1\\1&1\end{psmallmatrix}$ and
   $B=\begin{psmallmatrix}1\\2\end{psmallmatrix}$;
3. right only:
   $A=\begin{psmallmatrix}1&2\end{psmallmatrix}$ and
   $B=\begin{psmallmatrix}1&0&1\\0&1&1\end{psmallmatrix}$;
4. unprotected and nonzero:
   $A=B=\begin{psmallmatrix}1&0\\0&0\end{psmallmatrix}$;
5. unprotected and zero:
   $A=\begin{psmallmatrix}1&0\\0&0\end{psmallmatrix}$ and
   $B=\begin{psmallmatrix}0&0\\1&0\end{psmallmatrix}$.

Their ranks and products can be checked directly. In particular, the last two
examples demonstrate that a lack of protection is necessary but not sufficient
for incidence.

### Rubik routed-product registration

The computational Rubik case study fixes:

- the nine declared center-decomposition sectors, whose dimensions are

  $$
  (20,2,39,26,1,39,66,8,27);
  $$
- the 18 skew-Hermitian operators
  $X_g=(\rho(g)-\rho(g)^\ast)/2$;
- all ordered operator pairs, including repeated operators;
- all sector triples with off-diagonal factor legs $i\ne k$ and $k\ne j$.

For each order-two half turn, unitarity gives
$\rho(g)^\ast=\rho(g)^{-1}=\rho(g)$, and therefore $X_g=0$. The audit confirms
six zero operators, at zero-based indices $2,5,8,11,14,17$, with maximum norm
exactly zero in the declared realization. Consequently, all nonzero-factor
routed records arise from the twelve quarter-turn operators. This explains the
count $144=12^2$ for each exceptional sector triple, even though the declared
family contains 18 operators and the enumeration initially considers all
ordered pairs.

This anti-Hermitian-part registration is not the numerical matrix-logarithm
family used in Paper V's $S_4$ case study \cite{paper5}. In particular, a half
turn vanishes here but generally has a nonzero logarithmic generator. The two
papers' $R_1^{\mathrm{Lie}}$ and $R_2^{\mathrm{Lie}}$ censuses therefore cannot
be compared without an explicit observable-family alignment.

The corrected census is:

| Class | Count |
|-------|------:|
| both-protected | 0 |
| left-only | 0 |
| right-only | 0 |
| unprotected-nonzero | 2016 |
| unprotected-zero | 576 |
| total nonzero-factor routes | 2592 |

The 576 machine-zero products are concentrated in four zero-based sector
triples:

| $(i,k,j)$ | Count |
|-----------|------:|
| $(2,6,8)$ | 144 |
| $(5,6,8)$ | 144 |
| $(8,6,2)$ | 144 |
| $(8,6,5)$ | 144 |

Across these records,

$$
\max\|AB\|_F=2.467\times10^{-16},
\qquad
\max\eta(A,B)=6.737\times10^{-17}.
$$

The minimum factor norm is $1.803$. The maximum image--kernel action residual
is $1.210\times10^{-15}$ and the maximum subspace distance residual is
$9.485\times10^{-15}$. These are machine-zero image--kernel alignment records
in the declared complex128 realization, not exact symbolic equalities.

![The declared Rubik routed-product census. Six half-turn operators vanish under the anti-Hermitian-part registration, leaving twelve nonzero quarter-turn operators and therefore $144=12^2$ nonzero-factor records in each of four registered image--kernel concentrations. The display is a finite numerical registration and does not determine the codimension of a representation-derived pullback locus.](../../figures/paper7/fig2_rubik_incidence_census.png)

### Random and rank-deficient controls

Five dense random systems contribute 1620 routed records. Every record is
both-protected and has nonzero product.

Five controls with an $80\%$ rank-deficient block-generation probability
contribute another 1620 records:

| Class | Count |
|-------|------:|
| both-protected | 122 |
| left-only | 274 |
| right-only | 274 |
| unprotected-nonzero | 950 |
| unprotected-zero | 0 |

Thus, rank deficiency creates unprotected routes but does not, by itself,
force image--kernel incidence.

For independent dense square matrix pairs, the normalized product audit gives:

| $d$ | $\min\eta$ | $q_{0.001}$ | $q_{0.01}$ | median |
|----:|-----------:|------------:|-----------:|-------:|
| 2 | 0.1068 | 0.2322 | 0.3461 | 0.7070 |
| 3 | 0.2235 | 0.3017 | 0.3678 | 0.5744 |
| 4 | 0.2460 | 0.3144 | 0.3610 | 0.4975 |
| 5 | 0.2444 | 0.3122 | 0.3463 | 0.4455 |

Each dimension uses $100000$ samples. No sample falls below relative
thresholds $10^{-8}$, $10^{-10}$, or $10^{-12}$. This is an implementation and
threshold sanity check consistent with Proposition 3.2; it is not evidence for
operator or Lie completion.

### Perturbation and finite full-array atlas

Constructed incidence pairs in dimensions $2,3,4$ were perturbed at
$\varepsilon=10^{-6},10^{-4},10^{-2}$. All $900/900$ perturbed products became
nonzero at the declared threshold.

A separate finite Lie audit registers 80 eight-dimensional skew-Hermitian
systems in four mask families. It stores complete generator-indexed
$R_1^{\mathrm{Lie}}$ arrays, complete commutator-indexed
$R_2^{\mathrm{Lie}}$ arrays, complete $D_{\mathrm{Lie}}$ matrices, each
per-depth support array, each cumulative support array, and deterministic
SHA-256 hashes.

Each of the four threshold-defined low-order array classes contains 20 systems.
Within
every class:

- the complete $D_{\mathrm{Lie}}$ arrays agree elementwise;
- all per-depth and cumulative support arrays agree elementwise;
- the results are stable at thresholds $10^{-9},10^{-8},10^{-7}$;
- the cumulative generator--commutator basis passes the closure audit described
  below.

At rank tolerance $10^{-8}$, the cumulative dimensions by mask family, listed
through the first empty round, are

1. family 0: $(3,6,14,28,49,63,63)$, first empty round 6;
2. family 1: $(3,5,10,20,40,59,63,63)$, first empty round 7;
3. family 2: $(3,5,10,18,31,43,51,58,61,63,63)$, first empty round 10;
4. family 3: $(3,6,14,32,63,63)$, first empty round 5.

An empty round means that every commutator of a basis element in the newest
layer with every declared generator produces no new vector after projection
against the cumulative basis. The closure audit additionally checks all
generator--basis pairs, not solely those involving the newest layer. If
$\mathcal L=\operatorname{span}\{L_a\}$ is the final numerical basis, it forms

$$
R_{\mathrm{cl}}
=
\left[
(I-P_{\mathcal L})\operatorname{vec}[X_g,L_a]
\right]_{g,a}.
$$

Across all 80 systems, the final dimension is 63, the smallest retained
singular value of the vectorized basis matrix is at least
$0.999999999998$, the largest singular value of $R_{\mathrm{cl}}$ is at most
$7.175\times10^{-13}$, and the largest individual closure residual is
$6.627\times10^{-13}$. Thus all generator--basis commutators lie in the final
span to well below the declared rank tolerance. This is a numerical closure
certificate for the finite atlas, not an exact-arithmetic Lie-algebra theorem.

No disagreement occurs in this finite atlas. This is an observation about the
declared four families, not a theorem that
$(R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}})$ determines
$D_{\mathrm{Lie}}$.

***

## Claim Status and Boundary

The table uses the four claim levels. Corollaries and exact finite
examples belong to the Theorem level; refuted or unclaimed promotions are
listed separately as boundaries.

| Claim | Status |
|-------|--------|
| Image--Kernel Criterion | Theorem |
| $Z=\{AB=0\}$ is closed; $Z^\times$ is constructible | Theorem |
| fixed-$r$ dimension and codimension | Theorem |
| fixed-$(r,s)$ dimension and relative codimension $rs$ | Theorem |
| square-block dominant codimension | Theorem |
| left/right rank protection and norm bounds | Theorem |
| existence of the five displayed exact integer examples | Theorem |
| six half-turn zeros and corrected Rubik routed census | Computational Observation |
| random quantiles and perturbation breakdown | Computational Observation |
| full-array finite Lie atlas agreement and closure residual | Computational Observation |
| low-order Lie support determines Lie depth | Research Program |
| represented pullback incidence and transversality | Research Program |

The boundary is explicit: graph-to-route, route-to-word, and
word-to-commutator promotions are not claimed. Furthermore, ambient codimension
does not determine represented pullback geometry without additional hypotheses.

There is no theorem or conjecture in this paper asserting

$$
(R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}})
\Longrightarrow
D_{\mathrm{Lie}}.
$$

***

## Research Program

### Conditional Low-Order Promotion Problem

A future promotion theorem would need explicit, independently checkable
hypotheses rather than an undefined richness condition. Candidate gates
include:

| Gate | Candidate requirement |
|------|-----------------------|
| H1 low-order coverage | every finite-depth target already appears at the declared $R_1^{\mathrm{Lie}}$ or $R_2^{\mathrm{Lie}}$ layer |
| H2 route survival | every required routed product avoids image--kernel incidence |
| H3 cancellation control | route sums and antisymmetrizations do not erase the required channels, or are repaired in a declared Hall layer |
| H4 closure | the numerical or exact Lie closure is certified saturated |

H1 is an exclusionary hypothesis, not an observed general principle. Indeed,
it fails in the declared S4 numerical realization of Paper V: two registered
channels have $R_1^{\mathrm{Lie}}=R_2^{\mathrm{Lie}}=0$ but first appear at
$D_{\mathrm{Lie}}=2$ \cite{paper5}. The table is a research checklist, not a
theorem statement.

### Pullback incidence

For a representation-derived map $\Phi:\Theta\to\operatorname{Mat}\times
\operatorname{Mat}$, determine:

1. whether $\Phi(\Theta)$ is contained in an incidence stratum;
2. whether $\Phi$ is transverse to the relevant fixed-rank strata;
3. how symmetry changes the pullback codimension;
4. whether ranks remain constant on the declared parameter chart.

The object of interest is the pullback locus $\Phi^{-1}(Z)$, not the ambient
codimension alone.

### Structural stability and moving charts

The reported perturbation audit varies free matrix entries. A structural
stability theorem would instead perturb inside a representation-preserving or
sector-preserving family. Moving projectors require normal spectral charts and
coherent continuation before incidence can be compared across parameters.

### Hub recurrence

The four Rubik zero-product triples share the intermediate sector $k=6$.
Whether such incidence concentration relates to transport centrality remains
open. A formal relation would require aligned operator families and a theorem
connecting graph, routed, and representation-derived data.

***

## Conclusion

Projected factors compose precisely when the image of the right factor is not
contained in the kernel of the left factor. Thus

$$
AB=0
\quad\Longleftrightarrow\quad
\operatorname{im}B\subseteq\ker A
$$

is the local geometric obstruction, while full column rank of $A$ or full row
rank of $B$ protects a nonzero product. On a fixed double-rank stratum, the
incidence condition has relative codimension $rs$, cleanly separating rank
deficiency from the additional image--kernel alignment cost.

In the declared Rubik realization, the finite audit records 2016 unprotected
nonzero products and 576 machine-zero image--kernel alignments among 2592
nonzero-factor routes. This is a Computational Observation, not an exact
represented-incidence theorem.

These conclusions stop at routed matrix composition. They do not identify a
support path with a routed product, a routed product with a full word, a word
with a commutator, or low-order support with finite Lie depth. Rank protection,
image--kernel alignment, and promotion limits are therefore distinct parts of
one static composition problem.

***

## Related Work and Novelty Boundary

The matrix inequalities and singular-value bounds are standard
\cite{hornJohnson2013}. Determinantal and incidence strata are standard
objects in algebraic geometry \cite{harris1992,fulton1998,eisenbud1995}. The
distinction between Boolean zero patterns and evaluated matrix products is
adjacent to qualitative matrix theory and structural controllability
\cite{brualdiRyser1991,lin1974structural}. Routed products may also be viewed
through path and quiver evaluation, although this paper does not construct a
path-algebra quotient \cite{schiffler2014}.

Related work separates support graphs from projected composition and direct
support from words, commutators, and low-depth Lie data
\cite{paper3,paper5}. Those results are not used in the incidence proofs here.

***

## Appendix A: Computational Artifacts

The following repository artifacts support the exact incidence tables and the
computational case studies. The default directory is
`experiments/paper7/`; paths are relative to that directory.

| Artifact | Role | Short path |
|----------|-------------------|------------|
| A1 | exact fixed-rank and fixed-double-rank tables | \path{validation/incidence_variety_codim.py} |
| A2 | routed-product, rank-protection, and incidence audit | \path{validation/rank_protected_bridge_audit.py} |
| A3 | full-array typed low-order and Lie-depth audit | \path{validation/atlas_r2_boundary.py} |
| A4 | generated incidence tables | \path{results/incidence_geometry.json}, \path{.txt} |
| A5 | generated projected-composition witnesses | \path{results/projected_composition_audit.json}, \path{.txt} |
| A6 | generated complete-array Lie atlas | \path{results/full_array_lie_atlas.json}, \path{.txt} |

From the repository root, run an executable artifact as
`python experiments/paper7/<short path>`. A4 contains the fixed-rank tables;
A5 records thresholds, exact examples, the Rubik operator-family declaration,
zero-product witnesses, random controls, and perturbations; A6 records full
arrays, per-layer and cumulative supports, dimensions, closure certificates,
and hashes.

Every zero-product witness records

$$
(d_i,d_k,d_j),\quad
(\operatorname{rank}A,\operatorname{rank}B),\quad
\sigma_{\min}^{+}(A),\quad
\sigma_{\min}^{+}(B),
$$

together with $\|A\|_F$, $\|B\|_F$, $\|AB\|_F$, $\eta(A,B)$,
$\|AU_B\|_F$, the image-to-kernel distance, sector indices, and operator
indices.

The array hashes detect artifact drift. Mathematical equality claims in the
finite atlas use numpy.array_equal on the complete arrays rather than hash
equality alone.

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).
