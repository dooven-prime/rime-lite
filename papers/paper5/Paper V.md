# Boolean Support Does Not Determine Commutator Accessibility

### Direct Support, Exact Cancellation, and Low-Depth Hall Bridges

**WuJun Chen**

Independent Researcher | RIME Project | 2026

***

## Abstract

**Problem.** A generator-labelled support graph records which projected blocks
$Q_iX_gQ_j$ are nonzero, but it does not record whether two-step matrix
products survive or whether their signed difference survives in a commutator.
Consequently, direct support need not determine bracket accessibility or full
Lie depth.

**Approach.** For a fixed orthogonal sectorization and a declared family of
skew-Hermitian generators, we separate five object layers: generator support
$R_1$, routed projected-composition support, full-word support, commutator
support $R_2$, and cutoff-relative Lie depth $D^{(d_{\max})}$. We give an exact
$3\times3$ counterexample in which two systems have identical
generator-indexed Boolean support but differ in commutator support and exact
Lie depth. We then classify ordered sector pairs by the Boolean pair
$(R_1,R_2)$ and separate signed cancellation from image--kernel incidence.

**Results.** Boolean support does not determine commutator accessibility. In a
centered one-dimensional model, explicit hypotheses imply a local
bracket-emergent bridge, namely $R_1(i,j)=0$ and $R_2(i,j)=1$. For matrix
blocks, this conclusion requires actual product survival, rank protection, or a
separate nondegeneracy certificate. A computational $S_4$ case study exhibits
ten direct channels, two bracket-emergent channels, two channels with both
routed-product and full-word support but cancelled simple commutators, and
seventy-six channels unreached through the declared cutoff. Its machine-zero
cancellations are computational evidence, not exact equalities.

**Boundary.** The stable contribution is a local classification of direct
and bracket-emergent support together with exact cancellation and incidence
mechanisms. It is not a global repair or completion theorem. A general
word-level promotion theorem, full Lie-depth completion, and
moving-family promotion are not established here.

***

## Notation and Claim Layers {.unnumbered}

| Symbol | Meaning |
|--------|---------|
| $V$ | finite-dimensional complex Hilbert space |
| $Q_i$ | orthogonal sector projector, $\sum_iQ_i=I$ |
| $X_g$ | declared skew-Hermitian generator |
| $R_1^g(i,j)$ | direct support of generator $g$ from sector $j$ to sector $i$ |
| $R_1(i,j)$ | aggregate direct support over generators |
| $C_2^{g,h,k}(i,j)$ | Boolean support of the routed projected two-step term through sector $k$ |
| $C_2^X(i,j)$ | aggregate routed-product support over $g,h,k$ |
| $W_2^{g,h}(i,j)$ | full two-letter word support |
| $W_2^X(i,j)$ | aggregate full-word support over $g,h$ |
| $R_2^{g,h}(i,j)$ | projected commutator support |
| $R_2(i,j)$ | aggregate commutator support |
| $D^{(d_{\max})}_{ij}$ | first detected Lie depth up to the declared cutoff |
| $D_{ij}$ | exact first Lie depth, used only when the full Lie closure is certified |

The direction convention is fixed throughout:

$$
Q_iX_gQ_j\ne0
\quad\Longleftrightarrow\quad
j\longrightarrow i.
$$

Within this paper, the unqualified aliases are local to the declared Lie
family $\mathcal X=\{X_g\}$:

$$
R_1:=R_1^{\mathrm{Lie}}[\mathcal X],
\qquad
R_2:=R_2^{\mathrm{Lie}}[\mathcal X],
\qquad
D:=D_{\mathrm{Lie}}[\mathcal X]
$$

once the relevant Lie filtration has been declared. The associative supports
$C_2^X$ and $W_2^X$ remain separate diagnostics.

The paper uses four claim-status levels:

1. **Theorem:** finite-dimensional algebraic statements with exact matrices;
2. **Computational Certificate:** declared $S_4$ registrations and closure
   audits with reproducible thresholds and cutoffs;
3. **Computational Observation:** finite patterns without a promotion
   certificate, including the direct-channel product audit;
4. **Research Program:** statements explicitly identified as open and not used
   in the proofs.

***

## Introduction

Once a sectorization has been fixed, several different notions of
accessibility become available. They must not be collapsed into a single graph:

$$
\begin{gathered}
\text{direct support}
\ne
\text{projected composition}
\ne
\text{word support},
\\
\text{word support}
\ne
\text{commutator support}
\ne
\text{full Lie depth}.
\end{gathered}
$$

For represented group elements, support-graph paths can fail to survive
projected matrix composition \cite{paper3}. Here the operator family is
different: the inputs are declared skew-Hermitian matrices $X_g$, and the
first question is
whether direct generator support determines projected commutator support.

The answer is no. This obstruction already appears in an exact three-sector
counterexample. Two associative products may be individually nonzero yet
equal, so their signed difference vanishes. Changing one coefficient preserves
every generator support bit while making the commutator nonzero.

The contributions are:

1. a formal separation of $R_1$, projected two-step terms, word support,
   $R_2$, cutoff depth, and exact Lie depth;
2. an exact same-support counterexample for commutator accessibility and depth;
3. a neutral four-class partition by $(R_1,R_2)$;
4. a centered scalar proposition that produces a local bracket-emergent bridge;
5. a matrix-level incidence and rank boundary;
6. a claim-separated $S_4$ computational case study.

No result in this paper implies that $R_2$ restores general operator
propagation or that $(R_1,R_2)$ determines full depth; those remain separate
completion questions. The low-order taxonomy can serve as input to a full
Lie-depth audit, but such an audit still requires a declared filtration and
closure certificate.

***

## Fixed Sectorized Skew-Hermitian Systems

**Definition 2.1 (Static sectorized system).**

A static sectorized skew-Hermitian system is a triple

$$
\mathcal S=(V,\{Q_i\}_{i\in I},\{X_g\}_{g\in G}),
$$

where $V$ is finite-dimensional,

$$
Q_i=Q_i^\ast,
\qquad
Q_iQ_j=\delta_{ij}Q_i,
\qquad
\sum_iQ_i=I,
$$

and every $X_g$ is skew-Hermitian:

$$
X_g^\ast=-X_g.
$$

The generators are declared input data. If they are constructed from unitary
matrices $\rho(g)$, the logarithm branch and any numerical skew-Hermitian
projection are part of the realization and must be reported. No invariant in
this paper is inferred directly from $\rho(g)$ without first fixing $X_g$.

### Direct support

**Definition 2.2 (Generator-indexed and aggregate direct support).**

Define

$$
R_1^g(i,j)
=
\mathbf 1[Q_iX_gQ_j\ne0],
$$

and

$$
R_1(i,j)
=
\max_{g\in G}R_1^g(i,j).
$$

Because the generators are skew-Hermitian, support is symmetric for each
generator:

$$
R_1^g(i,j)=R_1^g(j,i).
$$

We nevertheless retain the ordered-pair convention because products are
composed from right to left.

### Projected products and word support

For an intermediate sector $k$, define the projected two-step term

$$
T_{g,h,k}(i,j)
=
Q_iX_gQ_kX_hQ_j.
$$

Its Boolean support is

$$
C_2^{g,h,k}(i,j)
=
\mathbf 1[T_{g,h,k}(i,j)\ne0].
$$

The aggregate routed-product support is

$$
C_2^X(i,j)=\max_{g,h,k}C_2^{g,h,k}(i,j).
$$

The full two-letter word block is

$$
Q_iX_gX_hQ_j
=
\sum_kT_{g,h,k}(i,j),
$$

and its support is

$$
W_2^{g,h}(i,j)
=
\mathbf 1[Q_iX_gX_hQ_j\ne0].
$$

Its aggregate support is

$$
W_2^X(i,j)=\max_{g,h}W_2^{g,h}(i,j).
$$

Thus a Boolean path in $R_1$ is only a candidate for $C_2$; a nonzero
$C_2$ term does not by itself determine $W_2$, because different intermediate
terms may cancel.

### Commutator support

**Definition 2.3 (Generator-pair and aggregate commutator support).**

Fix an ordering of the finite generator labels. For $g<h$, define

$$
R_2^{g,h}(i,j)
=
\mathbf 1[Q_i[X_g,X_h]Q_j\ne0],
$$

and

$$
R_2(i,j)
=
\max_{g<h}R_2^{g,h}(i,j).
$$

The exact expansion is

$$
Q_i[X_g,X_h]Q_j
=
\sum_k\big(T_{g,h,k}(i,j)-T_{h,g,k}(i,j)\big).
$$

Consequently, $R_2$ is not a Boolean function of $R_1$. It is also not the
same object as word support: it records the signed difference of two word
orders.

### Cutoff depth and exact depth

Let

$$
\mathcal L_{\le0}=\operatorname{span}\{X_g:g\in G\},
$$

and recursively

$$
\mathcal L_{\le d}
=
\mathcal L_{\le d-1}
+
\operatorname{span}\{[X_g,Y]:g\in G,\ Y\in\mathcal L_{\le d-1}\}.
$$

**Definition 2.4 (Cutoff-relative Lie depth).**

For a declared cutoff $d_{\max}$, define

$$
D^{(d_{\max})}_{ij}
=
\min\{d\le d_{\max}:Q_iYQ_j\ne0
\text{ for some }Y\in\mathcal L_{\le d}\}.
$$

If no such $d$ is found, write

$$
D^{(d_{\max})}_{ij}=\mathrm{unreached}.
$$

The implementation may serialize this state as `999`; that integer is not
mathematical infinity.

If an exact or separately certified closure $\mathcal L=\operatorname{Lie}
\langle X_g\rangle$ is available, define the exact depth $D_{ij}$ by the same
minimum over the full filtration and set $D_{ij}=\infty$ only when

$$
Q_i\mathcal LQ_j=\{0\}.
$$

***

## Low-Order Support Partition

**Theorem 3.1 (Four low-order support classes).**

Every ordered off-diagonal sector pair belongs to exactly one of the following
classes:

| Class | $R_1(i,j)$ | $R_2(i,j)$ | Meaning |
|-------|--------------|--------------|---------|
| direct-and-bracket supported | 1 | 1 | visible at both declared low-order layers |
| direct-only at bracket layer | 1 | 0 | directly visible; no projected commutator survives |
| bracket-emergent | 0 | 1 | absent from direct support and visible in a commutator |
| unresolved at layers 1--2 | 0 | 0 | absent from both low-order support layers |

**Proof.** The ordered pair $(R_1(i,j),R_2(i,j))$ belongs to
$\{0,1\}^2$, whose four elements are disjoint and exhaustive. $\square$

This theorem is a classification of low-order support status, not a depth or
completion theorem. In particular,

$$
R_1(i,j)=R_2(i,j)=0
$$

does not imply that $(i,j)$ is frozen, inaccessible, or invisible to higher
Hall layers.

### Mechanisms inside the partition

The Boolean pair does not identify why a commutator vanishes. Two mechanisms
must be separated.

**Cancellation mechanism.** At least one projected product term is nonzero,
but every relevant signed commutator sum vanishes.

**Incidence mechanism.** A support path has nonzero block factors

$$
A=Q_iX_gQ_k\ne0,
\qquad
B=Q_kX_hQ_j\ne0,
$$

while the product is zero:

$$
AB=0.
$$

Equivalently,

$$
\operatorname{im}(B)\subseteq\ker(A).
$$

A third possibility is absence of any two-step support candidate. These are
mechanism labels, not additional values of $(R_1,R_2)$ and not moving-wall
categories.

***

## Exact Same-Support Counterexample

Let $V=\mathbb C^3$ with coordinate projectors $Q_1,Q_2,Q_3$. Define the real
skew-symmetric, hence skew-Hermitian, matrices

$$
X=
\begin{pmatrix}
0&1&0\\
-1&0&1\\
0&-1&0
\end{pmatrix},
\qquad
Y_0=2X,
$$

and

$$
Y_1=
\begin{pmatrix}
0&2&0\\
-2&0&3\\
0&-3&0
\end{pmatrix}.
$$

**Theorem 4.1 (Boolean support does not determine commutator accessibility).**

The systems

$$
\mathcal S_0=(\mathbb C^3,\{Q_i\},\{X,Y_0\}),
\qquad
\mathcal S_1=(\mathbb C^3,\{Q_i\},\{X,Y_1\})
$$

have identical generator-indexed direct support, but their commutator support
differs. More precisely,

$$
Q_1[X,Y_0]Q_3=0,
\qquad
Q_1[X,Y_1]Q_3\ne0.
$$

The exact Lie depth of the channel $3\to1$ is infinite in $\mathcal S_0$ and
$1$ in $\mathcal S_1$.

**Proof.** The matrices $Y_0$ and $Y_1$ have the same zero pattern as $X$:
both connect sectors $1$ and $2$, and sectors $2$ and $3$, with no direct
$1$--$3$ block. Hence the labelled $R_1$ tensors agree in the two systems.

Since $Y_0=2X$,

$$
[X,Y_0]=0.
$$

Moreover, the Lie algebra generated by $X$ and $Y_0$ is the one-dimensional
space $\operatorname{span}\{X\}$, whose $Q_1$--$Q_3$ block is zero. Thus the
exact channel $3\to1$ is absent at every Lie depth.

Direct multiplication gives

$$
[X,Y_1]
=
\begin{pmatrix}
0&0&1\\
0&0&0\\
-1&0&0
\end{pmatrix}.
$$

Therefore $Q_1[X,Y_1]Q_3\ne0$, while the direct $Q_1XQ_3$ and
$Q_1Y_1Q_3$ blocks remain zero. The channel is bracket-emergent at depth $1$.
$\square$

At the intermediate sector $2$, the cancellation in $\mathcal S_0$ is visible
termwise:

$$
Q_1XQ_2Y_0Q_3
=
Q_1Y_0Q_2XQ_3
\ne0.
$$

This exact counterexample establishes the general negative result without
relying on floating-point reconstruction or a specific group realization.

![The exact same-support counterexample. The two systems have identical generator-indexed direct support, but the two projected product orders cancel for $Y_0$ and leave a nonzero commutator block for $Y_1$. The figure summarizes the displayed integer matrices and does not introduce a numerical claim.](../../figures/paper5/fig1_same_support_counterexample.png)

***

## Centered Scalar Bracket Emergence

The following statement isolates a sufficient condition for a local
bracket-emergent bridge.

**Proposition 5.1 (Centered scalar bracket-emergence).**

Assume all sectors are one-dimensional. Fix distinct generators $g,h$, a
source sector $j$, a target sector $i$, and an intermediate sector $k$. Suppose:

1. $R_1(i,j)=0$;
2. $Q_iX_gQ_k\ne0$ and $Q_kX_hQ_j\ne0$;
3. $Q_iX_hQ_k=0$;
4. for every $\ell\ne k$, both
   $Q_iX_gQ_\ell X_hQ_j$ and $Q_iX_hQ_\ell X_gQ_j$ vanish;

Then

$$
Q_i[X_g,X_h]Q_j\ne0,
$$

so $(i,j)$ is bracket-emergent:

$$
R_1(i,j)=0,
\qquad
R_2(i,j)=1.
$$

**Proof.** The sector expansion and hypotheses give

$$
Q_i[X_g,X_h]Q_j
=
Q_iX_gQ_kX_hQ_j.
$$

In one dimension the two displayed factors are nonzero scalars, so their
product is nonzero. $\square$

This proposition proves emergence at the commutator layer only. It does not
assert global propagation, operator-word completion, or the recovery of full
Lie depth.

### Support-set mechanism

One way to produce the hypotheses is to fix a distinguished center sector
$0$ and define

$$
A_g=\{u:Q_uX_gQ_0\ne0\},
\qquad
B_g=\{u:Q_1X_gQ_u\ne0\}.
$$

The conditions

$$
A_g\cap B_g=\varnothing,
\qquad
A_g\cap B_h\ne\varnothing\quad(g\ne h)
$$

imply $A_g\not\subseteq A_h$ for every ordered pair $g\ne h$: otherwise a
point of $A_g\cap B_h$ would lie in $A_h\cap B_h$. Under the additional
centered-support and direct-absence hypotheses of Proposition 5.1, these set
relations identify candidate bracket-emergent pairs. They do not by themselves
prove matrix-product survival.

***

## Matrix Products and Incidence

For higher-dimensional sectors, individually nonzero factors do not imply a
nonzero product:

$$
A\ne0,
\quad
B\ne0
\quad\not\Longrightarrow\quad
AB\ne0.
$$

**Lemma 6.1 (Image--kernel criterion).**

For composable finite-dimensional linear maps $A$ and $B$,

$$
AB=0
\quad\Longleftrightarrow\quad
\operatorname{im}(B)\subseteq\ker(A).
$$

**Proof.** The equality $AB=0$ holds exactly when $A$ annihilates every vector
in the image of $B$. $\square$

**Lemma 6.2 (Rank protection).**

If $A$ has full column rank and $B\ne0$, then $AB\ne0$. Dually, if $B$ has
full row rank and $A\ne0$, then $AB\ne0$.

**Proof.** Full column rank gives $\ker A=\{0\}$, so Lemma 6.1 would force
$B=0$ if $AB=0$. Full row rank gives $\operatorname{im}B$ equal to the entire
intermediate space, so $AB=0$ would force $A=0$. $\square$

### Free block model versus skew-Hermitian locus

Let $\mathcal M_{\mathrm{free}}(G,\mathbf d)$ be the affine space in which
allowed complex blocks vary independently and forbidden blocks are zero. Its
open support stratum requires every allowed block to be nonzero.

**Proposition 6.3 (Conditional exceptional sets in the free block model).**

Fix a projected commutator channel in
$\mathcal M_{\mathrm{free}}(G,\mathbf d)$. If its matrix-valued polynomial is
not identically zero, its vanishing set is a proper algebraic subset. The region
where at least one projected product survives but the commutator cancels is a
constructible subset of that zero set. Similarly, the region where specified
nonzero factors satisfy $AB=0$ is an incidence subset defined by polynomial
product equations alongside open nonzero conditions.

**Proof.** Matrix products and commutators have polynomial entries in the free
block coordinates. A nonzero polynomial cannot vanish on the entire affine
space. Adding nonvanishing conditions removes algebraic subvarieties and hence
produces constructible subsets. $\square$

This proposition applies only to the free complex-block model. Define the
skew-Hermitian realization locus by

$$
\mathcal M_{\mathrm{skew}}
\subset
\mathcal M_{\mathrm{free}}.
$$

This locus has adjoint constraints coupling opposite blocks and is naturally a
real algebraic locus. Genericity or codimension after intersection with
$\mathcal M_{\mathrm{skew}}$ requires a separate argument. Standard matrix and
incidence background is given in
\cite{hornJohnson2013,harris1992,fulton1998}.

***

## Computational S4 Case Study

The $S_4$ realization supplies evidence for the low-order mechanisms and is
not used in the exact proofs. It is constructed from the regular representation using
three declared permutations. The numerical generators are

$$
X_g
=
\frac{\operatorname{logm}(\rho(g))
-\operatorname{logm}(\rho(g))^\ast}{2},
$$

with SciPy's numerical matrix logarithm. This branch-dependent construction is
part of the declared computational realization.

For this section only, the short symbols mean

$$
R_1:=R_1^{\mathrm{Lie}}[X],\qquad
R_2:=R_2^{\mathrm{Lie}}[X],\qquad
C_2:=C_2^X,\qquad
W_2:=W_2^X,\qquad
D:=D_{\mathrm{Lie}}[X].
$$

The ten sectors are produced numerically in the $24$-dimensional regular
representation by an ordered compression procedure. Central class sums are
applied first, followed by three generator-derived Hermitian operators in the
declared order. The latter do not commute: the maximum pairwise
commutator norm in the seven-operator registration family is approximately
$26.319$. Thus this procedure defines an order-dependent orthogonal carrier
decomposition, not a joint spectral resolution. The compression clustering
tolerance is $10^{-8}$, and the resulting projectors are fixed throughout the
case study. Their registration audit is:

| Registration quantity | Result |
|-----------------------|--------|
| numerical dtype | `complex128` |
| projector ranks | $(1,1,3,3,3,3,3,3,2,2)$ |
| maximum idempotence residual | $3.127\times10^{-15}$ |
| maximum Hermiticity residual | $1.335\times10^{-16}$ |
| maximum pairwise-orthogonality residual | $2.105\times10^{-15}$ |
| completeness residual | $8.697\times10^{-15}$ |

All residuals use the Frobenius norm. This is a numerical orthogonal-complete
sector registration, not an exact representation-theoretic decomposition.

The support threshold is $10^{-8}$. With ten numerical sectors, the ordered
off-diagonal census is:

| Low-order status | Count |
|------------------|-------|
| direct, $R_1^{\mathrm{Lie}}=1$ | 10 |
| bracket-emergent, $R_1^{\mathrm{Lie}}=0,R_2^{\mathrm{Lie}}=1$ | 2 |
| $C_2^X=W_2^X=1$ but $R_1^{\mathrm{Lie}}=R_2^{\mathrm{Lie}}=0$ | 2 |
| $C_2^X=W_2^X=R_2^{\mathrm{Lie}}=0$ among $R_1^{\mathrm{Lie}}=0$ pairs | 76 |

![Low-order object separation in the declared $S_4$ realization. The arrows indicate audit order only: direct support, routed products, full words, commutator support, and cutoff depth are distinct typed objects. The bar census partitions the 80 aggregate-$R_1$-zero ordered pairs at threshold $10^{-8}$ and does not assert low-order-to-depth completion.](../../figures/paper5/fig2_low_order_channel_separation.png)

The two routed- and full-word-supported pairs are $S_4\to S_3$ and
$S_3\to S_4$.
For each one, the audit finds both $C_2^X=1$ and $W_2^X=1$, while
$R_2^{\mathrm{Lie}}=0$. Their two word-order norms are approximately
$2.01462$, while the projected commutator residuals are approximately
$6.1\times10^{-15}$. These are machine-zero observations under the declared
tolerance, not exact identities.

For cutoff $d_{\max}=3$, the numerical depth census is

$$
(A_0,A_1,A_2,A_{\mathrm{unreached}})=(10,2,2,76).
$$

Here `unreached` means no block was detected through depth $3$. The filtration
uses generators at Lie depth $0$, simple commutators at depth $1$, and nested
commutators at depth $2$ and above. The two entries counted by $A_2$ are
exactly the two cancellation channels $S_4\leftrightarrow S_3$; they first
appear through nested commutators, not through simple-commutator support.

The numerical filtration and saturation audit gives:

| Lie round | new dimension | cumulative dimension |
|-----------|---------------|----------------------|
| 0 | 3 | 3 |
| 1 | 3 | 6 |
| 2 | 7 | 13 |
| 3 | 8 | 21 |
| 4 | 0 | 21 |
| 5 | 0 | 21 |

At absolute rank threshold $10^{-8}$, the matrix augmented by the $21$
retained basis vectors and all $[X_g,L_a]$ columns has numerical rank $21$.
Its minimum retained singular value is $1.000$, its maximum discarded singular
value is $1.400\times10^{-13}$, the orthonormal-basis Gram residual is
$2.133\times10^{-14}$, and

$$
\max_{g,a}\operatorname{dist}
\big([X_g,L_a],\operatorname{span}\mathcal L\big)
=1.344\times10^{-13}.
$$

This supports numerical Lie-span saturation for the declared realization. It
remains a computational closure certificate rather than an exact symbolic
proof.

### Direct-channel product audit

The 48-product matrix audit covers only target pairs with $R_1(i,j)=1$. In
those already-direct channels:

| Quantity | Result |
|----------|--------|
| tested single-term two-step products | 48 |
| targets with direct $R_1$ support | 48/48 |
| targets with $R_1=0$ | 0/48 |
| zero products at tolerance $10^{-8}$ | 0/48 |
| rank-protected products | 48/48 |
| left-protected, $\operatorname{rank}(A)=d_k$ | 48/48 |
| right-protected, $\operatorname{rank}(B)=d_k$ | 48/48 |
| protected on both sides | 48/48 |
| sampled perturbation trials with a zero product | 0/100 |

Here $A:V_k\to V_i$ and $B:V_j\to V_k$. The implemented criterion is

$$
\operatorname{rank}(A)=d_k
\quad\text{or}\quad
\operatorname{rank}(B)=d_k,
$$

which is exactly the full-column/full-row condition of Lemma 6.2. It is not
the insufficient condition that only the smaller matrix dimension be attained.

This is a **Direct-Channel Product Nondegeneracy Audit**. It does not certify
matrix-level bracket emergence, absence of incidence on $R_1=0$ pairs, or
$(R_1,R_2)\to D$ completion.

***

## Claim Status and Boundary

The object distinctions in Section 2 are definitions, not an evidence level.
The table uses the four claim-status levels; proposition and lemma are
result types inside the Theorem level.

| Claim | Status |
|-------|--------|
| Four classes partition ordered pairs by $(R_1,R_2)$ | Theorem |
| Boolean generator support does not determine commutator support | Theorem |
| Boolean generator support does not determine exact Lie depth | Theorem |
| Centered one-dimensional hypotheses imply a bracket-emergent bridge | Theorem |
| $AB=0$ iff $\operatorname{im}B\subseteq\ker A$ | Theorem |
| Specified cancellation/incidence conditions define constructible free-model loci; cancellation is proper when its polynomial is nonzero | Theorem |
| S4 low-order census and cancellation residuals | Computational Certificate |
| S4 numerical Lie-span closure under the declared closure audit | Computational Certificate |
| 48 tested direct-channel products are nondegenerate | Computational Observation |
| Matrix-level emergence for general $R_1=0$ channels | Research Program |
| $(R_1,R_2)$ determines full $D$ in represented or dense systems | Research Program |
| Moving accessibility-wall hierarchy | Research Program |

The principal failure boundaries are:

$$
\text{Boolean path}
\not\Longrightarrow
\text{nonzero projected product},
$$

$$
\text{nonzero words}
\not\Longrightarrow
\text{nonzero commutator},
$$

and

$$
R_1=R_2=0
\not\Longrightarrow
D=\infty.
$$

***

## Research Boundary

### Matrix-level bracket emergence

A matrix-level emergence audit should begin with

$$
\mathcal O_{R_1}
=
\{(i,j):i\ne j,\ R_1(i,j)=0\}
$$

and separately classify:

1. $R_2(i,j)=1$ bracket-emergent channels;
2. $R_2(i,j)=0$ with nonzero projected products or words;
3. support paths whose products vanish by image--kernel incidence;
4. pairs with no tested two-step candidate.

Only the first class is a local commutator-layer emergence statement.

### Full Lie depth

Recovering exact $D$ requires either symbolic Lie closure or a certified
finite-dimensional closure argument. A numerical certificate should report the
filtration ranks, singular values, rank tolerance, and residuals of

$$
[X_g,L_a]\in\operatorname{span}\mathcal L
$$

for every generator and retained Lie-basis element. Cutoff stability alone is
not exact closure.

### Represented genericity and completion

Whether $(R_1,R_2)$ determines $D$ on a checkable represented or dense class
is open. Image--kernel incidence geometry, rectangular rank protection, and
conditional low-order promotion questions are studied separately
\cite{paper7}. The associated computational atlas and incidence candidates are
separate evidence and are not
used in the proofs here. In particular, a bridge-level incidence
candidate is not automatically a certified accessibility obstruction.

### Moving systems

Linearized commutativity and normality constraints, together with pointwise
typed registrations on certified commutative-normal samples, are studied in
\cite{paper6}. Moving accessibility fields remain a research problem. Any
hierarchy involving $\Sigma_{R_1}$, $\Sigma_{R_2}$, or
$\Sigma_D$ belongs to that separate deformation problem. No such hierarchy is
proved or assumed here. Cancellation and incidence are
static mechanisms, not wall labels.

### Higher Hall layers

Jacobi relations and higher Hall monomials can create or remove channels not
seen by $R_2$. Claims about Jacobi latency, dense-system completion, or a
universal finite truncation require independent certificates and are not
claimed here.

***

## Related Work and Novelty Boundary

Hall bases and free Lie algebras provide the standard organization of
commutators and nested commutators \cite{hall1950,reutenauer1993}. Geometric
control theory and structural controllability supply broader Lie-accessibility
and graph-generic settings \cite{jurdjevic1997,lin1974structural}. Zero-pattern
and combinatorial matrix theory study which matrix properties are visible from
support data \cite{brualdiRyser1991}. Quivers and path algebras provide a
standard language for labelled paths and their algebraic evaluation
\cite{schiffler2014}. Matrix-product survival and rank protection are elementary
finite-dimensional linear algebra \cite{hornJohnson2013}; incidence language
uses standard algebraic geometry \cite{harris1992,fulton1998}.

These structural theories motivate the Boolean and path shadows used here, but
they do not identify a support path with its value under a concrete matrix or
Hall evaluation. The present contribution isolates that evaluation gap through
exact signed cancellation, routed/full-word separation, and a local
commutator-support boundary.

Support graphs and projected products for represented group elements are
separated in \cite{paper3}. Those products are not identified here with the
logarithmic-generator products. The contribution is
the exact same-support commutator counterexample, the explicit low-order object
separation, and the local bracket-emergence/incidence boundary.

***

## Conclusion

Direct support does not determine commutator support. A Boolean two-step path
is not a matrix product, a matrix product is not a word sum, a word sum is not
a commutator, and low-order absence does not imply infinite-depth
inaccessibility.

The exact $3\times3$ example proves that identical generator-indexed support can
produce different commutator support and different full Lie depth. The
centered scalar proposition identifies one precise local emergence mechanism:

$$
R_1(i,j)=0,
\qquad
R_2(i,j)=1.
$$

For matrix blocks, image--kernel incidence is the missing product datum. The
$S_4$ realization supplies a computational case study of direct,
bracket-emergent, cancellation, and cutoff-unreached channels, whereas the
48-product audit is explicitly restricted to already-direct channels.

The resulting scope is deliberately local. General matrix emergence and exact
closure in representation-derived systems remain open. Completion from
$(R_1,R_2)$ to $D$, and moving accessibility walls, remain research programs.

***

## Appendix A: Computational Artifacts

The following repository artifacts support the exact counterexample and the
computational $S_4$ case study. The default directory is
`experiments/paper5/`; paths are relative to that directory.

| Artifact | Role | Short path |
|----------|-----------------|------------|
| A1 | exact same-support commutator counterexample | \path{validation/exact_support_commutator_counterexample.py} |
| A2 | typed $R_1/R_2/C_2^X/W_2^X$ low-order census | \path{validation/low_order_channel_audit.py} |
| A3 | cutoff Lie-depth and closure audit | \path{validation/s4_r1_r2_depth.py} |
| A4 | projected-product cancellation residuals | \path{validation/path_commutator_cancellation.py} |
| A5 | centered scalar bracket-emergence example | \path{validation/complement_explosion.py} |
| A6 | support-set enumeration control | \path{validation/noncomplement_obstruction_enumeration.py} |
| A7 | direct-channel product nondegeneracy audit | \path{validation/matrix_nondegeneracy.py} |

From the repository root, run an artifact as
`python experiments/paper5/<short path>`. A1 uses exact integer arithmetic.
The $S_4$ and matrix-logarithm artifacts are numerical and must declare dtype,
tolerance, generator family, logarithm branch, and cutoff. A passing assertion
supports only the claim mapped to that artifact.

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).
