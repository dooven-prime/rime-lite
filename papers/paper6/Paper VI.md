# Linearized Commutativity Geometry on the Generator-Set Moduli Space

### Full-Matrix Jacobian Certificates, Normality Gates, and Typed Spectral Registrations

**WuJun Chen**

Independent Researcher | RIME Project | 2026

***

## Abstract

**Problem.** Weighted generator averages define a commutativity locus in the
generator-set moduli space, but commutativity alone does not provide orthogonal
joint-spectral projectors. Normality and coherent projector continuation are
additional gates. A single untyped accessibility ladder would conflate
operator products, words, and Lie brackets, which are distinct mathematical
objects.

**Approach.** We split the paper into two layers. First, we study the
commutator map

$$
C_{\mathrm{comm}}(w)=[Q_T(w),H_T(w)]
$$

at the canonical Rubik point. Every Jacobian matrix is encoded by all real and
imaginary entries; no skew-Hermitian assumption is imposed. We then adjoin the
linearized normality equations for $Q_T$ and $H_T$. Second, only after
commutativity, Hermiticity, normality, and projector checks pass do we register
joint sectors and compare the typed supports
$R_1^{\mathrm{op}}:=R_1[\rho(S)]$ and
$R_1^{\mathrm{Lie}}:=R_1[X]$.

**Results.** The full complex-real commutator Jacobian has numerical rank $11$
and nullity $7$. Its nonzero singular values occur in groups

$$
0.585314^{\times3},\quad
0.532870^{\times3},\quad
0.346944^{\times2},\quad
0.200308^{\times3}.
$$

The combined commutativity-normality derivative has numerical rank $14$ and
nullity $4$. Its kernel is spanned numerically by uniform half-turn scaling and
three inverse-pair-symmetric quarter-turn axis directions. This kernel contains
both exact class-scaling gauges, while the three QT-axis directions have sample
points that pass the declared numerical commutativity and normality gates. At
the canonical point, the validated joint decomposition has $9$ sectors and
typed support counts $438$ and $408$. At quarter-turn axis weight $1.1$, each
tested axis has $15$ sectors; $R_1^{\mathrm{op}}=1006$, while the declared
finite-order logarithm branch gives $R_1^{\mathrm{Lie}}=832$ on each of the
three axes.

**Boundary.** Rank $11$ is a linearized commutativity-kernel certificate,
not a proof of a seven-dimensional smooth zero-set manifold. The pointwise
sector-count change from $9$ to $15$ is a normality-gated computational record,
not a refinement or global wall theorem.
Routed composition, full words, commutators, word depth, and Lie depth require
separate fields and separate certificates. No moving-wall theorem is claimed.

***

## Notation and Claim Layers {.unnumbered}

The paper uses four claim-status levels.

1. **Theorem:** finite-dimensional identities derived from the declared
   formulas, including lemmas and propositions under stated hypotheses.
2. **Computational Certificate:** matrix ranks, singular values, kernel
   directions, residuals, and projector checks with declared dtype and
   tolerance.
3. **Computational Observation:** pointwise sector-count and typed-support
   records without coherent continuation.
4. **Research Program:** statements explicitly identified as open and not used
   in the proved or certified results.

The domain gates are

$$
\mathcal M_{>0}
\supseteq
\Sigma_{\mathrm{comm}}
\supseteq
\Sigma_{\mathrm{normal}}
\supseteq
\Sigma_{\mathrm{spec}}^{(\nu)}.
$$

Here $\Sigma_{\mathrm{spec}}^{(\nu)}$ denotes one normal spectral chart in an
atlas. No global coherent labeling of joint sectors is assumed.

The accessibility objects are branched:

$$
R_1^{\mathrm{op}}
\longrightarrow
C_d^{\mathrm{op}},\ W_d^{\mathrm{op}}
\longrightarrow
D_{\mathrm{route}}^{\mathrm{op}},\ D_{\mathrm{word}}^{\mathrm{op}},
$$

and

$$
R_1^{\mathrm{Lie}}
\longrightarrow
R_2^{\mathrm{Lie}}
\longrightarrow
D_{\mathrm{Lie}}.
$$

No arrow between the two branches is asserted without an explicit bridge
theorem. These arrows denote construction and audit order only; they do not
encode functional determination, logical implication, or completion.

***

## Introduction

For a fixed finite joint arrangement $P$, one may vary only the linear
functional \cite{paper4}. Here a different question is considered: what remains valid when
the generator weights vary and the pair itself becomes

$$
(Q_T,H_T)=(Q_T(w),H_T(w))?
$$

Three logically distinct problems appear.

First, the two weighted averages may fail to commute. The global algebraic
object is therefore the commutativity locus $\Sigma_{\mathrm{comm}}$.

Second, even a commuting pair need not be normal. Orthogonal joint sectors are
available only after a normality gate. Even after that gate, smooth projector
fields are local chart data; collisions, multiplicity changes, and monodromy
can prevent a single global coherent labeling.

Third, once sectors have been registered, several typed accessibility notions
can be computed. A support graph of represented group elements, a routed
projected product, a full word, a projected commutator, and a Lie-depth
certificate are distinct typed objects and are not interchangeable. Papers III
and V establish the corresponding static separations \cite{paper3,paper5}. The
moving theory must preserve those types.

The contributions are deliberately narrower than a universal wall theory:

1. an exact Jacobian formula for the normalized commutator map;
2. a corrected full-matrix rank-$11$ computational certificate;
3. a linearized normality gate with rank $14$ and nullity $4$;
4. two exact class-scaling gauge families and three numerically certified QT-axis sample points;
5. pointwise projector and typed-support registrations at those points;
6. a conditional object language for future moving accessibility audits.

The paper does not claim that the commutativity zero set is a smooth
seven-dimensional manifold. It does not claim a complete
$\Sigma_{R_1}/\Sigma_{R_2}/\Sigma_D$ hierarchy. It does not identify graph
reachability with matrix composition or Lie depth. The pointwise registrations
can serve as endpoints for a moving analysis only after coherent projector
matching and chart regularity are certified.

***

## Weighted Generator Moduli

Let $S=\{g_1,\ldots,g_m\}$ be a fixed finite generator family and let

$$
\rho(g_i)\in U(V)
$$

be its declared finite-dimensional unitary realization. For the local
differential analysis, the generator-weight moduli space is the open positive
cone

$$
\mathcal M_{>0}=(0,\infty)^m.
$$

The larger nonnegative domain

$$
\mathcal M_{+}
=
\left\{w\in\mathbb R_{\ge0}^{m}:
\sum_{i\in\mathrm{QT}}w_i>0,
\ \sum_{i\in\mathrm{HT}}w_i>0\right\}
$$

is available for boundary probes. The canonical point $w_0=\mathbf1$ is an
interior point of $\mathcal M_{>0}$, and the tested weights $1+\varepsilon$
remain in this domain for $\varepsilon>-1$.

For the canonical Rubik realization, $m=18$ and
$V\cong\mathbb C^{228}$. The generators split into twelve quarter turns and
six half turns.

### Weighted QT/HT averages

On the open domain where both class totals are nonzero, define

$$
Q_T(w)
=
\frac{\sum_{i\in\mathrm{QT}}w_i\rho(g_i)}
{\sum_{i\in\mathrm{QT}}w_i},
\qquad
H_T(w)
=
\frac{\sum_{i\in\mathrm{HT}}w_i\rho(g_i)}
{\sum_{i\in\mathrm{HT}}w_i}.
$$

The normalized pair is invariant under independent positive class scalings:

$$
(a,b)\cdot w_i
=
\begin{cases}
aw_i,&i\in\mathrm{QT},\\
bw_i,&i\in\mathrm{HT},
\end{cases}
\qquad a,b>0.
$$

Thus its effective parameter space carries the gauge quotient
$\mathcal M_{>0}/((\mathbb R_{>0})_{\mathrm{QT}}\times
(\mathbb R_{>0})_{\mathrm{HT}})$. We retain redundant positive coordinates for
the Jacobian calculation. This quotient applies to the normalized QT/HT pair;
the global average $A(w)$ below is not invariant under independent class
scalings. Clearing denominators produces polynomial commutativity equations,
but doing so may add excluded boundary components if the positive-total
restriction is forgotten.

The global weighted average

$$
A(w)=\frac{\sum_iw_i\rho(g_i)}{\sum_iw_i}
$$

has a spectrum wherever the total weight is nonzero. Its definition does not
require QT/HT commutativity. The $A(w)$-spectrum and the QT/HT collision
quotient are therefore different observables with different domains.

### Commutativity and normality loci

Define

$$
\Sigma_{\mathrm{comm}}
=
\{w\in\mathcal M_{>0}:[Q_T(w),H_T(w)]=0\}.
$$

For a matrix $M$, write

$$
N(M)=MM^\ast-M^\ast M.
$$

The normal commuting locus is

$$
\Sigma_{\mathrm{normal}}
=
\{w\in\Sigma_{\mathrm{comm}}:
N(Q_T(w))=N(H_T(w))=0\}.
$$

Inverse-pair-symmetric weight families are Hermitian and hence normal. Generic
independent weight changes need not preserve this property.

### Normal spectral charts

A normal spectral chart $\Sigma_{\mathrm{spec}}^{(\nu)}$ is a relatively open
local piece of $\Sigma_{\mathrm{normal}}$ on which the joint multiplicity pattern is
fixed and orthogonal joint projectors can be labeled coherently:

$$
I=\sum_{i\in I_\nu}Q_i(w),
\qquad
Q_i(w)Q_j(w)=\delta_{ij}Q_i(w),
\qquad
Q_i(w)^\ast=Q_i(w).
$$

A moving generator family may require an atlas
$\{\Sigma_{\mathrm{spec}}^{(\nu)}\}_\nu$. Pointwise simultaneous
diagonalization does not by itself prove coherent projector continuation on a
neighborhood. Standard perturbation theory supplies the relevant background
for isolated spectral clusters \cite{kato1995perturbation}.

On one such chart the joint spectrum is a finite weighted arrangement

$$
P(w)=\{(q_i(w),h_i(w),d_i(w))\}_{i\in I_\nu}.
$$

For fixed $\alpha$, the collision quotient uses

$$
L_\alpha(q,h)=\alpha q+(1-\alpha)h.
$$

The fixed-arrangement theorem applies pointwise after $P(w)$ has
been registered; it does not prove that the arrangement or its projectors vary
smoothly with $w$ \cite{paper4}.

***

## Full-Matrix Linearized Commutativity Certificate

Let

$$
w_0=\mathbf1=(1,\ldots,1).
$$

At this point the canonical averages satisfy

$$
\|[Q_T(w_0),H_T(w_0)]\|_F=3.766\times10^{-16}
$$

in the declared `complex128` realization.

### Exact derivative formula

**Lemma 3.1 (Normalized commutator derivative).** At $w_0=\mathbf1$, without
assuming exact QT/HT commutation, the derivative with respect to one QT weight
is

$$
J_k
=
\frac{[\rho(g_k),H_T(w_0)]-[Q_T(w_0),H_T(w_0)]}{12},
\qquad k\in\mathrm{QT},
$$

and the derivative with respect to one HT weight is

$$
J_k
=
\frac{[Q_T(w_0),\rho(g_k)]-[Q_T(w_0),H_T(w_0)]}{6},
\qquad k\in\mathrm{HT}.
$$

**Proof.** For a normalized weighted average

$$
M(w)=\frac{\sum_iw_iM_i}{\sum_iw_i},
$$

the derivative at equal unit weights is

$$
\frac{\partial M}{\partial w_k}
=
\frac{M_k-M(w_0)}{|S|}.
$$

Differentiating $[Q_T,H_T]$ gives the displayed formulas directly. If exact
commutation is separately certified at $w_0$, the final commutator term in
each numerator vanishes and the formulas simplify to the shorter conditional
expressions. $\square$

### Full complex-real encoding

The QT derivatives $J_k$ are not individually skew-Hermitian. Their maximum
skew-Hermitian residual is

$$
\|J_k+J_k^\ast\|_F=0.200308.
$$

Consequently, retaining only a strict upper triangle is not a valid ambient
encoding. We therefore define the full realification

$$
\mathfrak R(M)
=
\begin{pmatrix}
\operatorname{vec}\Re M\\
\operatorname{vec}\Im M
\end{pmatrix}
\in\mathbb R^{2N^2}.
$$

The computational Jacobian is the
$2(228)^2\times18=103968\times18$ real matrix

$$
\mathcal J_{\mathrm{comm}}
=
\bigl[\mathfrak R(J_1)\ \cdots\ \mathfrak R(J_{18})\bigr].
$$

The computation uses the unconditional formulas in Lemma 3.1, including the
machine-scale baseline commutator terms.

**Computational Proposition 3.2 (Linearized commutativity-kernel
certificate).** In the declared realization and at relative singular-value
threshold $10^{-10}$,

$$
\operatorname{rank}\mathcal J_{\mathrm{comm}}=11,
\qquad
\dim\ker\mathcal J_{\mathrm{comm}}=7.
$$

The singular-value groups are

| singular value | multiplicity |
|----------------|--------------|
| $0.585314$ | 3 |
| $0.532870$ | 3 |
| $0.346944$ | 2 |
| $0.200308$ | 3 |
| numerical zero | 7 |

The rank boundary is numerically separated by

$$
\sigma_{11}=2.003084041924\times10^{-1},
\qquad
\sigma_{12}=2.415461205698\times10^{-15},
$$

with retained/discarded ratio $8.293\times10^{13}$.

The twelve QT Jacobians have Frobenius norm $0.309320$ and the six HT
Jacobians have norm $0.426730$.

The kernel contains uniform QT scaling, uniform HT scaling, and three
quarter-turn axis-symmetric directions. Single-coordinate deletions are not in
the kernel. These are statements about the derivative. They do not prove that
every kernel vector integrates to a curve in the exact zero set.

### What rank 11 does not prove

The space

$$
\ker D C_{\mathrm{comm}}|_{w_0}
$$

is the kernel of the linearized commutator constraint at a numerically
registered near-zero point. Because exact commutation at $w_0$ has not been
certified here, this kernel is not unconditionally identified with the Zariski
tangent space of $\Sigma_{\mathrm{comm}}$. If exact membership is later
established, promoting this kernel to the tangent space of a smooth
seven-dimensional local manifold still requires a constant-rank or
implicit-function argument on the actual zero set. The reported finite samples
and random searches do not supply that proof. Smooth-manifold and local
algebraic-geometry language is therefore used only conditionally
\cite{lee2013,eisenbud1995,harris1992}.

***

## The Normality Gate

Commutativity is necessary but insufficient to guarantee the orthogonal
sectorization used later. Therefore, we linearize the combined map

$$
F(w)
=
\bigl(
C_{\mathrm{comm}}(w),
N(Q_T(w)),
N(H_T(w))
\bigr).
$$

For an operator $M$ and variation $\dot M$,

$$
D N_M(\dot M)
=
\dot M M^\ast+M\dot M^\ast
-\dot M^\ast M-M^\ast\dot M.
$$

Every component is again encoded by full real and imaginary entries.

**Computational Proposition 4.1 (Combined linearized constraint kernel).** At
the numerically registered point $w_0=\mathbf1$, the combined derivative has

$$
\operatorname{rank}D F|_{w_0}=14,
\qquad
\dim\ker D F|_{w_0}=4.
$$

Its singular-value groups are

$$
0.585314^{\times3},\quad
0.532870^{\times3},\quad
0.482726^{\times2},\quad
0.346944^{\times2},
$$

$$
0.283279^{\times1},\quad
0.200308^{\times3},\quad
0^{\times4}.
$$

The combined-map rank boundary is

$$
\sigma_{14}=2.003084041924\times10^{-1},
\qquad
\sigma_{15}=2.238468379596\times10^{-15},
$$

with retained/discarded ratio $8.948\times10^{13}$.

Four interpretable vectors span the numerical kernel:

1. uniform scaling of all six HT weights;
2. equal variation of the four QT weights on axis $0$;
3. equal variation of the four QT weights on axis $1$;
4. equal variation of the four QT weights on axis $2$.

The sum of the three QT-axis vectors is uniform QT scaling, the second exact
class-scaling gauge direction.

Their projection residuals onto the numerical kernel are between
$1.0\times10^{-15}$ and $5.8\times10^{-15}$.

Because the baseline commutator is registered only to numerical precision,
this kernel is not identified unconditionally with
$T_{w_0}\Sigma_{\mathrm{normal}}$.

![Full complex-real Jacobian certificates at the canonical point. Adding the linearized normality equations changes the registered rank/nullity from $11/7$ to $14/4$, with a clear retained/discarded singular-value gap. These are pointwise linearized certificates, not a nonlinear integrability or moving-chart theorem.](../../figures/paper6/fig1_linearized_normality_gate.png)

### Exact gauge families and tested sample points

The four kernel vectors do not have the same certification status.

Uniform HT and uniform QT scaling are exact gauges of the normalized pair.
Multiplying all weights in either class by the same positive factor leaves the
corresponding normalized average unchanged. At $\varepsilon=0.1$, the measured
operator drifts are $1.526\times10^{-15}$ for HT scaling and
$5.230\times10^{-16}$ for QT scaling.

For each axis $a\in\{0,1,2\}$, set

$$
w_i(\varepsilon)
=
\begin{cases}
1+\varepsilon,&g_i\text{ is a QT on axis }a,\\
1,&\text{otherwise}.
\end{cases}
$$

The inverse-pair weights remain equal, so $Q_T(w)$ and $H_T(w)$ are Hermitian.
At $\varepsilon=0.1$, all three sampled points satisfy commutator and normality
residuals below $2\times10^{-16}$.

This gives two exact class-scaling gauge families and three certified QT-axis
sample points.
No interval-wide commutativity sweep or exact commutation proof is claimed for
the QT-axis parameterizations. The samples do not classify the nonlinear set
$\Sigma_{\mathrm{normal}}$.

***

## Normality-Gated Spectral Registrations

The sector algorithm is called only after the pair certificate passes:

$$
\|[Q_T,H_T]\|_F,
\quad
\|N(Q_T)\|_F,
\quad
\|N(H_T)\|_F,
\quad
\|Q_T-Q_T^\ast\|_F,
\quad
\|H_T-H_T^\ast\|_F
<10^{-8}.
$$

For the resulting projectors, the audit checks

$$
\max_i\|Q_i^2-Q_i\|_F,\qquad
\max_i\|Q_i-Q_i^\ast\|_F,qquad
\max_{i\ne j}\|Q_iQ_j\|_F,qquad
\left\|\sum_iQ_i-I\right\|_F.
$$

The maximum projector residual in the registered samples is
$2.390\times10^{-14}$.

### Typed support conventions

For represented group elements define

$$
R_{1,g}^{\mathrm{op}}(i,j)
=
\mathbf1[Q_i\rho(g)Q_j\ne0].
$$

For declared skew-Hermitian logarithms define

$$
R_{1,g}^{\mathrm{Lie}}(i,j)
=
\mathbf1[Q_iX_gQ_j\ne0].
$$

The direction convention is always

$$
Q_iYQ_j\ne0
\quad\Longleftrightarrow\quad
j\longrightarrow i.
$$

The reported count is the number of supported labeled blocks
$(g,i,j)$, including diagonal blocks. It is not an unlabelled simple-graph edge
count.

For this audit, $X_g$ is the finite-order principal logarithm determined by the
order-$2$ or order-$4$ spectral projectors, with arguments in
$(-\pi,\pi]$ and $\log(-1)=i\pi$. This branch declaration is part of the
realization. A different logarithm branch can change
$R_1^{\mathrm{Lie}}$ without changing $R_1^{\mathrm{op}}$.

### Registered samples

All computations use `complex128`, support and clustering threshold $10^{-8}$,
and the same 18-generator realization.

| Sample | sectors | $R_1^{\mathrm{op}}$ | $R_1^{\mathrm{Lie}}$ |
|--------|---------|-----------------------|--------------------------|
| canonical $w=\mathbf1$ | 9 | 438 | 408 |
| QT axis 0, $\varepsilon=0.1$ | 15 | 1006 | 832 |
| QT axis 1, $\varepsilon=0.1$ | 15 | 1006 | 832 |
| QT axis 2, $\varepsilon=0.1$ | 15 | 1006 | 832 |

The sorted sector-dimension censuses are

$$
\begin{aligned}
\operatorname{dims}_{\mathrm{canonical}}
&=(1,2,8,20,26,27,39,39,66),\\
\operatorname{dims}_{\mathrm{axis}}
&=(1,1,1,8,9,13,13,13,13,\\
&\qquad 18,20,22,26,26,44).
\end{aligned}
$$

Thus, the pointwise registrations exhibit a sector-count change from $9$ to
$15$ alongside a change in both typed direct-support counts. The operator and
Lie direct-support counts are not equal. The canonical Lie-support gap has
smallest retained block norm $0.5236$ and largest discarded block norm
$1.83\times10^{-14}$; across the three axis samples the smallest retained norm
is $3.53\times10^{-3}$ and the largest discarded norm is
$1.50\times10^{-13}$. The logarithm branch, dtype, and threshold therefore
remain part of the declared numerical registration.

![Normality-gated pointwise registrations. The canonical point has nine sectors, while each of the three tested QT-axis samples has fifteen; the operator-family and Lie-family direct-support counts are displayed separately. All four records pass the declared numerical gates, but the figure does not supply projector continuation along an intervening path.](../../figures/paper6/fig2_pointwise_typed_registrations.png)

These samples do not yet prove a wall location or a smooth projector chart
connecting the endpoints. Such a claim requires coordinate-matched projector
continuation and threshold-stability sweeps along the intervening path.

***

## Conditional Typed Accessibility Fields

This section defines the typed objects conditionally on a normal spectral
chart $U=\Sigma_{\mathrm{spec}}^{(\nu)}$ with declared smooth
projectors $Q_i(w)$.

### Operator and word branch

For $Y_g=\rho(g)$, define direct blocks

$$
B_{ij}^{\mathrm{op},g}(w)
=
Q_i(w)Y_gQ_j(w).
$$

For an intermediate sequence
$i_0=j,i_1,\ldots,i_d=i$, define the routed product

$$
C_{i_d\cdots i_0}^{\mathrm{op},g_d\cdots g_1}(w)
=
Q_{i_d}Y_{g_d}Q_{i_{d-1}}\cdots
Q_{i_1}Y_{g_1}Q_{i_0}.
$$

The full word block is

$$
W_{ij}^{\mathrm{op},g_d\cdots g_1}(w)
=
Q_iY_{g_d}\cdots Y_{g_1}Q_j.
$$

Explicit summation over intermediate sectors demonstrates the separation
between these objects:

$$
W_{ij}^{\mathrm{op},g_d\cdots g_1}
=
\sum_{i_1,\ldots,i_{d-1}}
C_{i\,i_{d-1}\cdots i_1j}^{\mathrm{op},g_d\cdots g_1}.
$$

Different routed terms may cancel. Define routed-composition depth and word
depth separately, with $\inf\varnothing=\infty$ only for exact saturated
objects. Numerical cutoffs use `unreached`, never infinity.

### Lie branch

For declared skew-Hermitian $X_g$, define

$$
B_{ij}^{\mathrm{Lie},g}(w)
=
Q_i(w)X_gQ_j(w),
$$

and

$$
C_{ij}^{\mathrm{Lie},g,h}(w)
=
Q_i(w)[X_g,X_h]Q_j(w).
$$

Their support shadows are $R_1^{\mathrm{Lie}}$ and
$R_2^{\mathrm{Lie}}$. Higher Lie depth $D_{\mathrm{Lie}}$ is defined from a
declared Hall filtration. Exact infinity requires a full Lie-closure
certificate; a finite computation reports cutoff-unreached channels. Hall bases
and geometric control supply the standard background
\cite{hall1950,reutenauer1993,jurdjevic1997,agrachevSachkov2004}.

$R_2^{\mathrm{Lie}}$ is commutator support, not a generic repair theorem.
Static cancellation and image--kernel incidence are mechanisms, not moving-wall
labels.

### Conditional local constancy

**Proposition 6.1 (Finite typed-shadow constancy).** Fix a normal spectral
chart with continuous projector fields and fix a finite declared list of block,
routed-product, word, commutator, or Hall matrices. On any open region where
the ranks of all matrices in that list remain constant, their finite Boolean
support shadows are locally constant.

**Proof.** A matrix has zero support exactly when its rank is zero. Constant
rank therefore fixes every declared zero/nonzero status. $\square$

This proposition is finite and typed. It does not say that
$R_1^{\mathrm{Lie}}$ determines $R_2^{\mathrm{Lie}}$, that support paths
determine routed products, or that a finite cutoff determines exact depth.

***

## Claim Status and Boundary

The table uses the four claim levels. Lemma and exact identity are
result types inside the Theorem level; negative and unestablished implications
are listed separately as boundaries.

| Claim | Status |
|-------|--------|
| derivative formulas for the normalized QT/HT commutator | Theorem |
| full complex commutator Jacobian has rank $11$, nullity $7$ | Computational Certificate |
| combined commutativity-normality derivative has rank $14$, nullity $4$ | Computational Certificate |
| four displayed directions span the numerical combined kernel | Computational Certificate |
| uniform QT/HT gauges leave the normalized pair fixed | Theorem |
| three QT-axis points pass numerical commutator, Hermiticity, and normality audits | Computational Certificate |
| canonical and axis-sample projectors are orthogonal and complete | Computational Certificate |
| registered sector-count change from $9$ to $15$ | Computational Observation |
| typed $R_1^{\mathrm{op}}$ and $R_1^{\mathrm{Lie}}$ counts | Computational Observation |
| coherent projector continuation between registered endpoints | Research Program |
| moving routed/word/Lie depth walls | Research Program |

The boundary is explicit: the rank-$11$ kernel is not a proved
seven-dimensional smooth $\Sigma_{\mathrm{comm}}$ manifold, and no universal
inclusion hierarchy among accessibility walls is claimed.

### Earlier-version correction

An earlier fragmentation calculation incorrectly diagonalized commuting but
nonnormal QT averages using a Hermitian eigensolver. The resulting
$9\to24\text{--}35$ sector counts and $438\to6334$ untyped support count are
invalid because the normality gate was not satisfied, and they are therefore
not used here.

Likewise, statements that fragmentation automatically changes
the untyped $R_2$ or $D$ are withdrawn. No corresponding Rubik typed product,
commutator, or closure certificate was computed.

***

## Research Program

The open problems below are ordered by mathematical dependency.

### Integrability of the commutativity kernel

Determine local defining equations for $\Sigma_{\mathrm{comm}}$, first certify
whether $w_0$ belongs to the exact commutativity zero set, and then decide
which of the seven linearized directions integrate to exact curves. Rank
stability sampled away from the zero set is not a substitute for an
implicit-function or local-algebraic certificate.

### Normal spectral atlas

Determine whether the four-dimensional combined linearized constraint kernel
extends to actual local charts. Required checks include commutativity and
normality along the full path, constant
joint multiplicities away from registered collision points, coordinate-matched
projector overlaps, principal angles, and monodromy around degeneracies.

### Typed moving fields

On certified charts, compute the branches independently:

$$
(R_1^{\mathrm{op}},C_d^{\mathrm{op}},W_d^{\mathrm{op}},
D_{\mathrm{route}}^{\mathrm{op}},D_{\mathrm{word}}^{\mathrm{op}})
$$

and

$$
(R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}},D_{\mathrm{Lie}}).
$$

Only actual matrix products support composition claims. Only projected
commutators and a saturated Lie filtration support Lie-depth claims.

Only after a deformation path or chart and its typed matrix fields have been
certified may one define corresponding rank/support discriminants. Candidate
loci include

$$
\Sigma_{R_1^{\mathrm{op}}},\quad
\Sigma_{D_{\mathrm{route}}^{\mathrm{op}}},\quad
\Sigma_{D_{\mathrm{word}}^{\mathrm{op}}},\quad
\Sigma_{R_1^{\mathrm{Lie}}},\quad
\Sigma_{R_2^{\mathrm{Lie}}},\quad
\Sigma_{D_{\mathrm{Lie}}}.
$$

These loci need not coincide or form one total inclusion chain. First-order
jets may be useful diagnostics, but need not detect every higher-order support
change.

### Spectral collision and field loci

The moving layer and field loci
$\Sigma_L$ and $\Sigma_{\mathrm{field}}$ remain candidate spectral
stratifications inside certified spectral charts. Their definitions require
exact or explicitly registered algebraic coordinates. No universal inclusion
with typed accessibility loci is asserted.

***

## Related Work and Novelty Boundary

Finite-group representations and the Rubik realization use standard
representation-theoretic background \cite{serre1977,joyner2008}. Commuting
normal matrices and isolated spectral-cluster continuation are classical
finite-dimensional perturbation theory \cite{kato1995perturbation}. Matrix
rank and singular-value certificates use standard matrix analysis
\cite{hornJohnson2013}.

The algebraic geometry of commuting matrix pairs is classical
\cite{gerstenhaber1961commuting}. The present parameter family is a structured
pullback of a commuting locus with additional normalization and normality
constraints; no statement about the global components or irreducibility of
that pullback is made here. Numerical simultaneous diagonalization and the
sensitivity of joint diagonalizers provide a second direct comparison class
\cite{bunseGerstnerByersMehrmann1993,afsari2008sensitivity}. Those works concern
diagonalization algorithms and perturbation sensitivity, whereas the present
certificate records linearized constraints and pointwise registered spectral
data without asserting a continuation theorem.

The local zero-set discussion is adjacent to smooth constant-rank theory and
local algebraic geometry \cite{lee2013,eisenbud1995,harris1992}. The present
paper does not introduce a general perturbation theorem for commuting normal
tuples. Its contribution is the corrected full-matrix certificate, the explicit
normality gate, and the typed separation required before moving accessibility
claims can be formulated.

Association schemes and Bose--Mesner algebras provide neighboring examples of
commutative semisimple matrix algebras \cite{bannaiIto1984,godsil1993}. They are
comparison classes, not asserted identifications of the QT/HT algebra.

***

## Conclusion

The generator-set moduli problem has two distinct layers.

The first is commutativity geometry. At the canonical point, the corrected
full complex-real Jacobian has rank $11$ and nullity $7$. This is a linearized
certificate, not a smooth-manifold theorem.

The second is the construction of moving spectral and accessibility fields.
That construction begins only after normality and projector continuation have
been certified. The combined linearized commutativity-normality map has rank
$14$ and nullity $4$. The kernel contains both exact class-scaling gauges, and
the three displayed QT-axis directions have certified sample points. The axis points have
$15$ registered sectors versus $9$ at the canonical point; no projector
refinement relation is asserted. Operator and Lie direct-support counts remain
distinct.

The correct future architecture is therefore

$$
\text{commutativity}
\longrightarrow
\text{normality}
\longrightarrow
\text{spectral charts}
\longrightarrow
\text{typed matrix fields}
\longrightarrow
\text{typed wall audits}.
$$

Skipping any gate in this sequence makes the subsequent accessibility
statement undefined or ambiguous. The results therefore establish pointwise
typed registrations, not a moving-wall theorem.

***

## Appendix A: Computational Artifacts

The following repository artifacts support the linearized certificates and
pointwise registrations. The default directory is `experiments/paper6/`;
paths are relative to that directory.

| Artifact | Role | Short path |
|----------|------------------|------------|
| A1 | full complex-real commutator Jacobian certificate | \path{validation/tangent_commutator_map.py} |
| A2 | normality gate and pointwise typed registration audit | \path{validation/normal_spectral_chart_audit.py} |
| A3 | contextual ambient-moduli probes | \path{validation/generator_moduli_space.py} |
| A4 | tangent-map run summary | \path{results/_paper6_tangent_commutator_map.txt} |
| A5 | ambient-moduli run summary | \path{results/_paper6_bifurcation_log.txt} |

From the repository root, run an executable artifact as
`python experiments/paper6/<short path>`. The numerical reports declare
matrix dtype and norm, absolute and optional relative thresholds, reference
scale, threshold sweep, projector registration, and any logarithm branch,
cutoff, or saturation policy used by the reported object.

A3 is contextual computation rather than a spectral-chart theorem.

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).
