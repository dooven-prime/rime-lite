# Phase Transition Geometry on the Generator-Set Moduli Space

### Global Stratification, Local Commutativity Geometry, and Accessibility Walls

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part VI of the RIME program. Papers I--V study static structures
at fixed generator sets. Paper VI opens the deformation line: what happens when
the generator set itself varies? The paper studies the deformation geometry of
the generator-set moduli space and the wall structure of accessibility phase
transitions.*

***

## Abstract

**Problem.** Why do sectors and accessibility observables move? Paper IV treats
a fixed joint arrangement $P$ and varies only the projection. Under
generator-set perturbation the arrangement itself becomes $P(w)$, and it is
defined only where $Q_T(w)$ and $H_T(w)$ form a commuting normal pair. The problem is to separate
the spectral walls of this moving arrangement from the accessibility walls of
the induced sectorized system.

**Approach.** We introduce the generator-set moduli space
$\mathcal{M}=[0,1]^m$ and distinguish two observables. The collision quotient
is defined on normal spectral charts
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$, where
$\Sigma_{\mathrm{comm}}=\{w:[Q_T(w),H_T(w)]=0\}$ and a QT/HT joint
arrangement exists. The A-spectrum of the global average $A(w)$ is defined on
all of $\mathcal M$. Locally, we linearize the commutator map at the canonical
point $w=\mathbf 1$ and compute the tangent model of
$\Sigma_{\mathrm{comm}}$. On normal charts of this base we define the moving
sectorized system, its block fields, the accessibility jet, and the discrete
shadows $R_1(w),R_2(w),D(w)$.

**Results.** The global scans separate the collision quotient from the
A-spectrum and organize internal events as $\mathrm{SPLIT}$,
$\mathrm{MERGE}$, and $\mathrm{FIELD}$. At the canonical Rubik point, the
linearized commutator map has rank $11$ and a $7$-dimensional kernel,
decomposing as $1(\mathrm{HT})+6(\mathrm{QT})$. In the tested local model,
rank stability and nonlinear-kernel searches support a computational
$7$-dimensional tangent-local scaffold for $\Sigma_{\mathrm{comm}}$ near
$w=\mathbf 1$. On normal charts of this base, fragmentation of joint sectors produces jumps in the observable
shadows $R_1,R_2,D$.

**Implications.** Spectral walls and accessibility walls are different
discriminant structures. $\Sigma_L$ and $\Sigma_{\mathrm{field}}$ describe
movement and arithmetic of the joint arrangement; $\Sigma_{\mathrm{access}}$
records rank/support failures of the accessibility jet. This turns
generator-set variation into the moduli-space form of the gap between
Lie-generated and composition-generated accessibility.

***

## Structure of the Paper

Why do sectors move? Because a generator-set perturbation changes the averaged
operators from which the joint arrangement is computed. On normal spectral
charts $\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$, that moving
arrangement produces moving sector projectors; the observables $R_1,R_2,D$ are
discrete shadows of their block and commutator fields. The paper studies where
these shadows remain stable and where they jump.

The paper has five structural layers. First, the commutativity locus
$\Sigma_{\mathrm{comm}}$ is treated through local smooth models on which the
QT/HT joint arrangement is defined. Second, the accessibility fields over this
local base are introduced: generator blocks, projected commutator blocks, and
Hall projection blocks. Third, the discrete observables $R_1,R_2,D$ are
recovered as rank/support shadows of these fields, and accessibility walls are
defined as failures of local continuation of this shadow. Fourth, the spectral
walls $\Sigma_L,\Sigma_{\mathrm{field}}$ and the accessibility wall
$\Sigma_{\mathrm{access}}$ are separated as different discriminant structures
inside $\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$. Finally, the resulting wall picture is
interpreted as the moduli-space form of the gap between Lie-generated and
composition-generated accessibility.

The central organizing point is that, within the tested tangent-local model, the spectral
arrangement moves smoothly, while the associated accessibility data are
discrete shadows of smooth matrix fields and can jump across rank/support
walls.

![Paper VI architecture. The generator-set moduli space contains the
commutativity locus, where the QT/HT joint arrangement and its collision
quotient are defined. Spectral walls and accessibility walls are different
observable shadows of the moving sectorized system.](../../figures/paper6/fig1_program_architecture.png)

***

## Notation

| Symbol | Meaning |
|--------|---------|
| $\mathcal{M}$ | generator-set moduli space $[0,1]^m$; $m=18$ for Rubik |
| $w=(w_1,\ldots,w_m)$ | generator weight vector |
| $Q_T(w)$ | weighted quarter-turn average |
| $H_T(w)$ | weighted half-turn average |
| $A(w)$ | weighted full generator average |
| $P(w)$ | QT/HT joint spectral arrangement when defined |
| $L_\alpha(q,h)$ | affine projection $\alpha q+(1-\alpha)h$ |
| $C_{\mathrm{comm}}(w)$ | commutator map $[Q_T(w),H_T(w)]$ |
| $J_k$ | Jacobian matrix $\partial C_{\mathrm{comm}}/\partial w_k|_{\mathbf{1}}$ |
| $I_{\mathrm{comm}}$ | ideal generated by entries of $C_{\mathrm{comm}}(w)$ |
| $\Sigma_{\mathrm{comm}}$ | commutativity locus $\{w:[Q_T(w),H_T(w)]=0\}$ |
| $\Sigma_{\mathrm{spec}}$ | normal commutative spectral domain where QT/HT joint sectors and orthogonal projectors are used |
| $\Sigma_L$ | layer-count wall inside $\Sigma_{\mathrm{spec}}$ |
| $\Sigma_{\mathrm{field}}$ | field-extension wall inside $\Sigma_{\mathrm{spec}}$ |
| $\mathrm{SPLIT},\mathrm{MERGE},\mathrm{FIELD}$ | internal bifurcation events on normal spectral charts |
| $X_g$ | skew-Hermitian accessibility generator, usually $X_g=\log\rho(g)$ as in Paper V |
| $\mathcal S(w)$ | sectorized observable framework $(V,\{Q_i(w)\},\{X_g\}_{g\in S})$ |
| $Q_i(w)$ | orthogonal joint-sector projector on $\Sigma_{\mathrm{spec}}$ |
| $B^g_{ij}(w)$ | block map $Q_i(w)X_gQ_j(w)$ |
| $\mathcal{J}_{\mathrm{acc}}(w)$ | accessibility jet: first-order data of block, commutator, and Hall projection fields |
| $\Delta_{\mathrm{access}}$ | accessibility discriminant read from the rank/support profile of the accessibility jet |
| $\Sigma_{\mathrm{access}}$ | accessibility wall locus when $\Delta_{\mathrm{access}}$ is taken as the exact accessibility discriminant |
| $R_1(w)$ | generator-labelled directed support graph computed from block-field support |
| $R_2(w)$ | repair graph computed from projected commutator survival |
| $D(w)$ | minimal accessibility depth data |

***

## Theorem-Layer Overview

Spectral walls describe how the joint arrangement moves. Accessibility walls
describe when the moved arrangement changes the gap between Lie-generated and
composition-generated accessibility.

This distinction is structural. The walls
$\Sigma_L$ and $\Sigma_{\mathrm{field}}$ are spectral stratification walls:
they record layer jumps and field changes of the QT/HT joint arrangement. They
are not, by definition, accessibility walls. Accessibility walls are detected
by changes in the accessibility jet and in its discrete shadows
$R_1(w)$, $R_2(w)$, and $D(w)$ on normal spectral charts of the commutative
locus.

The theorem-layer hierarchy is

$$
\Sigma_{\mathrm{comm}}
\longrightarrow
\mathcal{J}_{\mathrm{acc}}
\longrightarrow
\Sigma_{R_1}
\longrightarrow
\Sigma_{R_2}
\longrightarrow
\Sigma_D.
$$

The continuous object is the accessibility jet

$$
\mathcal{J}_{\mathrm{acc}}
=(J_{\mathrm{block}},J_{\mathrm{comm}},J_{\mathrm{depth}}).
$$

The observables $R_1,R_2,D$ are discrete projections of this jet, not
continuous invariants themselves.

## Part I -- Global Stratification {-}

## From Fixed Collision Geometry to Moduli

Paper IV studies a fixed finite arrangement \cite{paper4}:

$$
P=\{(q_i,h_i)\}\subset\mathbb{R}^2.
$$

For a fixed commuting pair $(Q,H)$, the interpolation

$$
A(\alpha)=\alpha Q+(1-\alpha)H
$$

changes layers by changing the projection

$$
L_\alpha(q,h)=\alpha q+(1-\alpha)h.
$$

Thus Paper IV is a fixed-arrangement theory:

$$
P\ \mathrm{fixed},\qquad L_\alpha\ \mathrm{varies}.
$$

In the Rubik laboratory, QT/HT are the canonical commuting averaged operators.
The theory is formulated for arbitrary commuting averaged operators; QT/HT are
the canonical Rubik instance used to compute and test the deformation picture.

Paper VI studies the next problem:

$$
P=P(w).
$$

The arrangement itself moves because the generator-set weights change the
averaging operators from which the arrangement is computed.

## Generator-Set Moduli Space

### Definition 1 (Generator-Set Moduli Space)

Let $\rho:G\to U(V)$ be a fixed finite-dimensional unitary representation, and
let

$$
S=\{g_1,\ldots,g_m\}
$$

be a fixed ordered generator list. The generator-set moduli space is

$$
\mathcal{M}=[0,1]^m.
$$

A point $w=(w_1,\ldots,w_m)$ assigns a continuous inclusion weight to each
generator. The vertices $\{0,1\}^m$ correspond to ordinary generator subsets.
The finite-group representation setting follows the standard semisimple
background \cite{serre1977}; for the Rubik group instance we use the usual
group-theoretic presentation and generator conventions \cite{joyner2008}.

For the Rubik system, $m=18$: twelve quarter-turn generators and six half-turn
generators.

### Definition 2 (Weighted QT/HT Averages)

Let $\mathrm{QT}$ and $\mathrm{HT}$ denote the quarter-turn and half-turn
subsets of $S$. Define

$$
Q_T(w)
=
\frac{\sum_{g_i\in\mathrm{QT}}w_i\rho(g_i)}
{\sum_{g_i\in\mathrm{QT}}w_i},
\qquad
H_T(w)
=
\frac{\sum_{g_i\in\mathrm{HT}}w_i\rho(g_i)}
{\sum_{g_i\in\mathrm{HT}}w_i},
$$

when the denominators are nonzero. If all weights in one class vanish, the
corresponding average is treated as a degenerate boundary operator.

For arbitrary independent weights, these averages need not be Hermitian or
normal: inverse-pair symmetry can be broken. The commutator equation alone
therefore does not justify orthogonal joint-sector projectors. Whenever this
paper uses QT/HT joint spectral sectors and orthogonal projectors, it is
working on a normal chart of the commutative locus. In inverse-symmetric
submoduli this normality is automatic; outside such charts, generalized
nonnormal joint decompositions are not used here.

Thus the joint-spectral and accessibility-wall statements below are read on
inverse-symmetric generator-weight charts, under which $Q_T(w)$ and $H_T(w)$
remain Hermitian.

### Definition 3 (Collision Quotient on the Commutative Locus)

The QT/HT joint spectral arrangement at $w$ is used in this paper only on the
normal commutative spectral domain

$$
\Sigma_{\mathrm{spec}}
=
\{w: [Q_T(w),H_T(w)]=0,\ Q_T(w),H_T(w)\ \text{normal}\}.
$$

On that domain, the commuting normal pair is simultaneously unitarily
diagonalizable, and the joint spectrum is a finite weighted point set

$$
P(w)=\{(q_i(w),h_i(w),d_i(w))\}.
$$

Equivalently, the joint sectors are orthogonal primitive eigenspace sectors of
the finite-dimensional commutative spectral algebra generated by $Q_T(w)$ and
$H_T(w)$ on this normal chart.
This is the same finite semisimple algebraic setting that underlies
Bose--Mesner algebras and association schemes, used here as comparison
classes rather than as an asserted identification
\cite{bannaiIto1984,godsil1993,godsilMartin1995quotients}.

For fixed $\alpha$, the collision quotient is induced by

$$
L_\alpha(q,h)=\alpha q+(1-\alpha)h.
$$

The layer count $N_L(w)$ is the number of distinct values of
$L_\alpha(P(w))$.

### Definition 4 (Global A-Spectrum)

The global averaged operator is

$$
A(w)=\frac{\sum_i w_i\rho(g_i)}{\sum_i w_i},
$$

for nonzero total weight. Its spectrum is defined on all of
$\mathcal{M}$ away from the zero-weight vertex. This observable does not
require QT/HT commutativity.

## The Primary Commutativity Locus

The primary object of Paper VI is the commutativity locus. It is the
algebraic wall controlling where QT/HT commutation holds. The QT/HT joint
spectral arrangement and collision quotient are then used on its normal
spectral charts $\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$.

### Definition 5 (Commutativity Locus)

The commutativity locus is

$$
\Sigma_{\mathrm{comm}}
=
\{w\in\mathcal{M}:[Q_T(w),H_T(w)]=0\}.
$$

For collision-quotient geometry, Paper VI further restricts to normal charts
inside this locus. Outside $\Sigma_{\mathrm{comm}}$, the QT/HT joint spectral
arrangement is not defined in this framework; inside
$\Sigma_{\mathrm{comm}}$ but outside normal charts, this paper does not invoke
orthogonal joint-sector projectors.

On any chart where the total QT and HT weights are nonzero, the condition is
equivalent to the vanishing of the polynomial commutator map

$$
C_{\mathrm{comm}}(w)
=
\sum_{i\in\mathrm{QT}}\sum_{j\in\mathrm{HT}}
w_iw_j[\rho(g_i),\rho(g_j)].
$$

The algebraic study of $\Sigma_{\mathrm{comm}}$ begins with the ideal
generated by the entries of $C_{\mathrm{comm}}(w)$:

$$
I_{\mathrm{comm}}
=
\langle (C_{\mathrm{comm}}(w))_{ab}\rangle.
$$

Part II (Section 4) gives the first algebraic data at the canonical point:
$\dim T_{\mathbf{1}}\Sigma_{\mathrm{comm}}=7$, $\operatorname{codim}=11$,
the kernel decomposition, and a computational tangent-local scaffold.

### Remark 1 (Sparse Slices versus the Commutativity Locus)

Early two-dimensional scans found very few commutative sample points. Those
experiments should be interpreted as transverse-slice evidence, not as a claim
that $\Sigma_{\mathrm{comm}}$ is a sparse set in the full moduli space. The
canonical point has a $7$-dimensional computational tangent-local scaffold inside
$\mathcal M=[0,1]^{18}$. This distinction matters because the collision
quotient and the accessibility jet are defined only on normal spectral charts
inside $\Sigma_{\mathrm{comm}}$, while the global A-spectrum remains defined
even when a transverse path exits that locus.

![The commutativity locus is the algebraic domain controlling the QT/HT collision quotient. The
global averaged spectrum is defined on the ambient weight space, while the
joint arrangement and collision quotient are used only on normal commutative
charts. Sparse transverse slices are evidence about crossings, not evidence
that the commutative locus itself is sparse.](../../figures/paper6/fig2_commutativity_locus.png)

### Definition 6 (Layer Wall)

Within the normal spectral domain, the layer wall is the locus where the
collision quotient layer count is not locally constant:

$$
\Sigma_L
=
\{w\in\Sigma_{\mathrm{spec}}:N_L(w)\ \mathrm{jumps}\}.
$$

Experimentally this is detected by `SPLIT` and `MERGE` events in $P(w)$.

### Definition 7 (Field Wall)

Within the normal spectral domain, the field wall is the locus where the
spectral field of the collision quotient changes:

$$
\Sigma_{\mathrm{field}}
=
\{w\in\Sigma_{\mathrm{spec}}:
\mathbb{Q}(L_\alpha(P(w)))\ \mathrm{changes}\}.
$$

Experimentally this is detected when rational spectral data enter a mixed or
$\mathbb{Q}(\sqrt{5})$ phase.

### Conjecture 1 (Collision-Quotient Stratification)

For the collision-quotient observable, the expected internal hierarchy is

$$
\Sigma_{\mathrm{field}}
\subseteq
\Sigma_L
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}.
$$

Here $\Sigma_{\mathrm{comm}}$ is the primary commutator object, while
$\Sigma_L$ and $\Sigma_{\mathrm{field}}$ are spectral loci on normal charts
inside it. The nesting is the organizing hierarchy for the algebraic theory.
On the normal commutative spectral domain,
field changes have been observed coincident with joint-spectrum bifurcations,
supporting $\Sigma_{\mathrm{field}}\subseteq\Sigma_L$.

This conjecture is specific to the collision quotient. The A-spectrum is a
different global observable, and its field behavior can differ from the
collision-quotient field behavior.

***

## Part II -- Local Geometry at the Canonical Point {-}

## Tangent Space of the Commutativity Locus

The commutativity locus is the zero set $C_{\mathrm{comm}}(w)=0$. At
$w=\mathbf{1}=(1,\ldots,1)$, we have $C_{\mathrm{comm}}(\mathbf{1})=0$ to
machine precision ($\|[Q_T(\mathbf{1}),H_T(\mathbf{1})]\|_F=3.77\times
10^{-16}$). The first algebraic datum is the derivative
$DC_{\mathrm{comm}}|_{\mathbf{1}}$, giving the tangent space
$T_{\mathbf{1}}\Sigma_{\mathrm{comm}}=\ker DC_{\mathrm{comm}}|_{\mathbf{1}}$.

### Linearized Commutator Map

At $w=\mathbf{1}$:

$$
Q_T(\mathbf{1})=\frac{1}{12}\sum_{g\in\mathrm{QT}}\rho(g),\qquad
H_T(\mathbf{1})=\frac{1}{6}\sum_{g\in\mathrm{HT}}\rho(g),
$$

with $[Q_T(\mathbf{1}),H_T(\mathbf{1})]=0$.

**Lemma 1 (Jacobian at the canonical point).** For $g_k\in\mathrm{QT}$:

$$
J_k=\frac{\partial C_{\mathrm{comm}}}{\partial w_k}\Big|_{\mathbf{1}}
  =[\rho(g_k),H_T(\mathbf{1})]/12.
$$

For $g_k\in\mathrm{HT}$:

$$
J_k=\frac{\partial C_{\mathrm{comm}}}{\partial w_k}\Big|_{\mathbf{1}}
  =[Q_T(\mathbf{1}),\rho(g_k)]/6.
$$

**Proof.** For a weighted average $A(w)=\sum_i w_i M_i/\sum_i w_i$, the
derivative at $w=\mathbf{1}$ is $\partial A/\partial w_k|_{\mathbf{1}}=
(M_k-A(\mathbf{1}))/|S|$ where $|S|$ is the number of terms. Applying this
to $Q_T$ (12 terms) and $H_T$ (6 terms) and using
$[Q_T(\mathbf{1}),H_T(\mathbf{1})]=0$ gives the stated formulas. $\square$

The tangent map sends $\delta w\in\mathbb{R}^{18}$ to the skew-Hermitian
matrix $\sum_{k=1}^{18}\delta w_k J_k$. The tangent space is its kernel:

$$
T_{\mathbf{1}}\Sigma_{\mathrm{comm}}=\ker(\delta w\mapsto\sum_k\delta w_k J_k).
$$

### Tangent Space Dimension

Each $J_k$ is a $228\times 228$ skew-Hermitian matrix. A skew-Hermitian
$N\times N$ matrix has $N(N-1)$ real degrees of freedom (the strictly upper
triangular entries). For $N=228$, this is $228\cdot 227=51756$ real
dimensions. Flattening each $J_k$ to a real vector of length $51756$ and
assembling the 18 columns gives the $51756\times 18$ real Jacobian matrix
$\mathcal{J}$. Its singular value decomposition determines the rank and
kernel, using the standard matrix-analysis interpretation of rank and singular
values \cite{hornJohnson2013}.

### Theorem 1 (Computational Tangent Decomposition at the Canonical Point)

At $w=\mathbf{1}$, the tangent space $T_{\mathbf{1}}\Sigma_{\mathrm{comm}}=
\ker\mathcal{J}$ has the following properties.

**(i) Dimension.**

$$
\dim T_{\mathbf{1}}\Sigma_{\mathrm{comm}}=7,\qquad
\operatorname{codim}=11.
$$

**(ii) Singular value spectrum.** The 18 singular values of $\mathcal{J}$ form
four nonzero groups and a zero group:

$$
\begin{aligned}
s_{0,1,2} &= 0.413880 \quad\text{(multiplicity 3)}\\
s_{3,4,5} &= 0.376796 \quad\text{(multiplicity 3)}\\
s_{6,7}   &= 0.245327 \quad\text{(multiplicity 2)}\\
s_{8,9,10} &= 0.141639 \quad\text{(multiplicity 3)}\\
s_{11,\ldots,17} &= 0 \quad\text{(multiplicity 7)}.
\end{aligned}
$$

**(iii) Turn-class symmetry.** All 12 QT Jacobians have identical Frobenius
norm $\|J_k\|_F=0.309320$. All 6 HT Jacobians have identical norm
$0.426730$. This uniformity reflects the $O_h$ (octahedral) conjugation
symmetry of the full generator set.

**(iv) Kernel decomposition.** The $7$-dimensional kernel splits by turn class:

$$
\ker\mathcal{J}=K_{\mathrm{HT}}\oplus K_{\mathrm{QT}},\qquad
\dim K_{\mathrm{HT}}=1,\quad\dim K_{\mathrm{QT}}=6.
$$

$K_{\mathrm{HT}}$ is the uniform half-turn direction: all six HT weights
scaled equally. $K_{\mathrm{QT}}$ is a $6$-dimensional subspace of the
$12$-dimensional QT weight space. The subspace $K_{\mathrm{QT}}$ contains the
three per-axis QT directions ($\{R,R',L,L'\}$ on axis $0$, $\{U,U',D,D'\}$ on
axis $1$, $\{F,F',B,B'\}$ on axis $2$) and their linear combinations
(including uniform QT scaling).

**(v) Tested finite-amplitude tangency.** All seven kernel directions remain
inside the commutative locus in the tested one-parameter families.
Writing $w(\varepsilon)=\mathbf{1}+\varepsilon v$ for each unit kernel vector
$v$, the full commutator norm satisfies

$$
\|[Q_T(w(\varepsilon)),H_T(w(\varepsilon))]\|_F < 10^{-15}
$$

for all tested $\varepsilon\in\{10^{-4},10^{-3},10^{-2},10^{-1},1\}$. No
kernel direction shows an observed $\varepsilon^2$ or higher-order departure
within this tested range.

**(vi) First-order prediction.** For any weight direction $v$, the first-order
approximation $\|\sum_k v_k J_k\|\cdot\varepsilon$ matches the true commutator
norm to relative error $<10^{-3}$ at $\varepsilon=10^{-2}$ across all tested
directions. At $\varepsilon=0.1$, the ratio remains within $1\%$
(actual/predicted $\in[0.990,1.007]$ for the strongest transverse
directions). The commutator map is nearly linear over a substantial
neighborhood of $\mathbf{1}$.

**(vii) Local rank stability.** The Jacobian rank was recomputed at points
$w=\mathbf{1}+\varepsilon v$ for random linear combinations $v$ of the
seven kernel basis vectors, at $\varepsilon\in\{0.01,0.1,0.5,1.0\}$. In all
tested cases the rank remains exactly $11$ -- the same as at $\mathbf{1}$.
No rank increase is observed anywhere on the tested kernel family. This
gives no evidence for hidden constraints that would increase the codimension of
$\Sigma_{\mathrm{comm}}$ near $\mathbf{1}$ within the tested local model.

**(viii) Absence of nonlinear kernel contributions.** A systematic search
tested $200$ random directions in $\mathbb{R}^{18}$ (including directions
with substantial transverse component, trans\_frac $>0.5$), each on a grid
of $500$ $\varepsilon$-steps from $10^{-6}$ to $0.5$. For every direction,
the commutator norm minimum occurs at the smallest $\varepsilon$ and scales
linearly with the transverse component. Zero directions with non-negligible
transverse component achieved $\|[Q_T,H_T]\|_F<10^{-13}$. This search found no
evidence of hidden nonlinear kernel elements -- points on
$\Sigma_{\mathrm{comm}}$ that are not tangent to the first-order kernel.

**Together, (v)--(viii) establish a computational tangent-local scaffold for a
$7$-dimensional model of $\Sigma_{\mathrm{comm}}$ near the canonical point.**
The Jacobian has rank $11$ at $\mathbf{1}$, the tested kernel families show
rank stability, no nonlinear constraints are observed in the random searches,
and the commutator map is approximately linear over the tested neighborhood.
Thus the commutator ideal $I_{\mathrm{comm}}$ has $11$ observed independent
first-order constraints at $\mathbf{1}$, with no observed higher-order
degeneracy in the tested families. A proof of algebraic smoothness or a
complete set of defining equations for $\Sigma_{\mathrm{comm}}$ is not claimed
here. The constant-rank viewpoint \cite{lee2013} and the local ideal language
from commutative algebra and algebraic geometry
\cite{eisenbud1995,harris1992} provide the background for this scaffold.

![Computational tangent decomposition at the canonical point. The linearized
commutator map has rank $11$ and a $7$-dimensional kernel, splitting in the
tested local model into one uniform HT direction and six QT kernel
directions.](../../figures/paper6/fig3_tangent_decomposition.png)

### Agreement with Numerical Slices

The tangent space classification perfectly predicts the commutator rank strata
observed in transverse and symmetric one-parameter slices:

| Direction class | In $T_{\mathbf{1}}\Sigma_{\mathrm{comm}}$? | $\|[Q_T,H_T]\|_F$ at $\varepsilon=1$ |
|-----------------|-------------------------------------------|--------------------------------------|
| All QT symmetric | Yes | $<10^{-16}$ (exact) |
| All HT symmetric | Yes | $<10^{-16}$ (exact) |
| Per-axis QT symmetric ($\times 3$) | Yes | $<10^{-16}$ (exact) |
| Per-axis HT symmetric ($\times 3$) | No (projection $0.577$, residual $0.816$) | $\sim 0.37$ (rank $52$) |
| Single QT deletion ($\times 12$) | No (projection $0.707$, residual $0.707$) | $\sim 0.31$ (rank $96$) |
| Single HT deletion ($\times 6$) | No (projection $0.408$, residual $0.913$) | $\sim 0.43$ (rank $88$) |

### Consequences for the Global Picture

The tangent space theorem corrects the interpretation of sparse two-dimensional
slices.
The $(w_{F_2},w_{B_2})$ plane -- both coordinates are axis-0 HT weights -- is
completely transverse to $\Sigma_{\mathrm{comm}}$. The intersection
$\Sigma_{\mathrm{comm}}\cap\{\text{2D plane}\}$ is the single point
$w=\mathbf{1}$. The "extreme sparsity" ($1/961$ cells) is an artifact of
transverse slicing: the 2D plane cuts through the moduli space in a direction
transverse to the $7$-dimensional $\Sigma_{\mathrm{comm}}$.

Conversely, the verified symmetry slices contained in
$K_{\mathrm{QT}}\oplus K_{\mathrm{HT}}$ (for example, varying all QT and HT
weights uniformly) lie inside the tested normal spectral subfamilies of
$\Sigma_{\mathrm{comm}}$ and have a well-defined collision quotient at every
tested point. A global algebraic description of this local family would
require deriving the defining equations of
$I_{\mathrm{comm}}$ beyond the tangent model.

### Fragmentation Theorem: The Wall Origin Principle

Theorem 1 supplies a computational $7$-dimensional tangent-local scaffold for
$\Sigma_{\mathrm{comm}}$ at $\mathbf{1}$. A natural next question is whether
the sector decomposition itself, namely the joint eigenspace projectors
$P_i(w)$ of $(Q_T(w),H_T(w))$, is stable along the kernel directions. The
answer is sharply negative, and this negation contains the mechanism behind
all subsequent accessibility walls.

**Theorem 2 (Computational Fragmentation at the Canonical Point).** At $w=\mathbf{1}$, the
joint spectral decomposition has $9$ sectors with dimensions
$(20,2,39,66,26,39,1,27,8)$. The following statement is computational and
local to the seven tested SVD kernel-basis directions:

**(i) Normalized HT gauge versus SVD kernel direction.** The true gauge is
uniform HT scaling after the QT/HT operators are normalized: it leaves
$H_T(w)$ and $Q_T(w)$ invariant, so the $9$-sector decomposition is preserved.
The SVD basis vector labelled `kernel[0]` is tangent to this HT-scaling
direction at $\mathbf{1}$, but it is not itself the normalized gauge curve at
finite amplitude. Consequently it preserves the $9$ sectors at
$\varepsilon=10^{-6}$ but fragments at larger $\varepsilon$ in the table below.

**(ii) Immediate fragmentation.** All six QT kernel-basis directions
($1$--$6$) fragment the $9$-sector decomposition at all tested small
$\varepsilon$ values. The fragmentation is hierarchical:

| Kernel direction | Sector count at $\varepsilon=10^{-6}$ | Sector count at $\varepsilon=0.1$ |
|------------------|---------------------------------------|-----------------------------------|
| kernel[0] (HT-tangent basis direction) | $9$ (tested gauge tangent) | $35$ |
| kernel[1] (axis-2 QT prime) | $24$ | $35$ |
| kernel[2] (axis-0 QT prime) | $25$ | $35$ |
| kernel[3] (axis-1 QT prime) | $31$ | $35$ |
| kernel[4] (QT mixed) | $32$ | $35$ |
| kernel[5] (QT mixed) | $34$ | $35$ |
| kernel[6] (QT mixed) | $24$ | $35$ |

Each kernel direction produces a distinct intermediate sector count at small
$\varepsilon$, revealing a fine stratification of fragmentation types within
$\Sigma_{\mathrm{comm}}$. At larger $\varepsilon$ ($\geq 0.1$), most directions
converge to $35$ sectors -- the generic count in the tested kernel families.

**(iii) Block-rank jumps.** The fragmentation directly causes accessibility
wall crossings. At $\varepsilon=0.01$ along a generic kernel direction, the
sector count jumps $9\to 35$. In the directed support graph
$E_1^{\mathrm{dir}}$, the edge count jumps from $29$ to $391$; in the
generator-labelled directed graph $E_1^{\mathrm{gen}}$, the edge count jumps
from $438$ to $6334$. After the initial fragmentation, the block-rank
structure is stable until the next wall crossing.

**Wall Origin Principle.** Accessibility walls are not caused by
nonlinearity of $\Sigma_{\mathrm{comm}}$. They are caused by combinatorial
instability of the sector decomposition under linear motion of the joint
spectral points $(q_i(w),h_i(w))$. The mechanism is:

1. $\Sigma_{\mathrm{comm}}$ has a computational $7$-dimensional tangent-local
   model at $\mathbf{1}$ (Theorem 1).
2. On normal spectral charts $\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$, the joint spectral points move linearly with $w$
   (to first order, verified to $<1\%$ at $\varepsilon=0.01$).
3. The sector decomposition -- the assignment of joint eigenspaces to distinct
   $(q,h)$ points -- undergoes discrete combinatorial changes when spectral
   points cross, merge, or split.
4. These discrete changes in the sector decomposition cause discrete changes in
   $R_1$, $R_2$, and $D$.

Thus the accessibility phase diagram on $\Sigma_{\mathrm{spec}}$ is a
**piecewise-constant structure on a smooth linear background.** The walls are
the loci where the joint spectral point arrangement undergoes a combinatorial
transition.

**(iv) The canonical point as a fragmentation intersection.** The point
$w=\mathbf{1}$ is special: it sits at the intersection of fragmentation walls
for all six QT kernel directions and along finite-amplitude continuations of
the HT-tangent SVD basis direction. The $9$-sector coarse decomposition exists
only at the canonical point in the tested QT kernel families, except along the
exact normalized HT gauge curve. Every tested small QT kernel perturbation
resolves the $9$ sectors into finer sectors. The canonical Rubik spectrum is therefore a
**maximally coarse point** on the normal spectral chart inside
$\Sigma_{\mathrm{comm}}$ -- the point where the
largest number of joint spectral points have coincident $L_{2/3}$ values,
producing the $6$-layer collision quotient.

![Fragmentation and the Wall Origin Principle. Along tested kernel directions,
the commutativity base has a tested tangent-local model while the sector decomposition
and projected accessibility data jump discretely.](../../figures/paper6/fig4_fragmentation_wall_origin.png)

***

## Part III -- Accessibility Theorem Layer {-}

The preceding sections describe the spectral geometry of the generator-set
moduli space. We now fix the objects needed for the accessibility theorem
layer. Throughout this part, $w$ lies in a normal chart of
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$, so the QT/HT joint
spectral arrangement and its orthogonal sector projectors are defined.

## Sectorized Systems and Accessibility Data

### Definition 8 (Sectorized System over the Commutativity Locus)

Let $w\in\Sigma_{\mathrm{spec}}$. The commuting normal pair
$(Q_T(w),H_T(w))$ has an orthogonal joint spectral decomposition

$$
V=\bigoplus_i V_i(w),
\qquad
Q_i(w):V\to V_i(w),
$$

where $Q_i(w)$ denotes the orthogonal projector onto the $i$th joint sector.
Let

$$
X_g=\log \rho(g)
$$

denote the skew-Hermitian accessibility generator used in the Paper V
Lie-depth calculus. The sectorized system at $w$ is the data
The sectorized system at $w$ is the data

$$
\mathcal{S}(w)=\bigl(V,\{Q_i(w)\}_i,\{X_g\}_{g\in S}\bigr).
$$

This definition is only made on normal spectral charts. Outside
$\Sigma_{\mathrm{comm}}$, the QT/HT joint sectors are not defined; inside
$\Sigma_{\mathrm{comm}}$ but outside the normal spectral domain, the present
paper does not use orthogonal projector-valued sectorized accessibility data.

### Definition 9 (Generator Block Maps)

For $w\in\Sigma_{\mathrm{spec}}$, sectors $i,j$, and generator $g\in S$, define
the sector block map

$$
B^g_{ij}(w)=Q_i(w)X_gQ_j(w).
$$

These blocks are the local matrix entries of the Lie accessibility generator
with respect to the moving joint-sector decomposition. They are the Paper VI
moving-sector analogue of the Paper V block maps.

### Definition 10 (R-One Support Graph)

The first accessibility observable is the colored generator-support graph
$R_1(w)$. Its vertices are the joint sectors $i$. For each generator $g\in S$,
there is a colored directed edge

$$
i \xrightarrow{g} j
$$

if and only if

$$
B^g_{ij}(w)=Q_i(w)X_gQ_j(w)\ne 0.
$$

Thus $R_1(w)$ records the sector pairs directly touched by individual
generators. It is a support-level object; it does not record cancellations in
commutators or higher words.

We use three related edge-count conventions:

$$
E_1^{\mathrm{gen}}(w)
=\{(g,i,j):B^g_{ij}(w)\ne 0\},
$$

the **generator-labelled directed graph**. Forgetting the generator label gives
the **directed support graph**

$$
E_1^{\mathrm{dir}}(w)
=\{(i,j):\exists g,\ B^g_{ij}(w)\ne 0\}.
$$

For display only, forgetting orientation gives the simple **support graph**

$$
E_1^{\mathrm{supp}}(w)
=\{\{i,j\}:\exists g,\ B^g_{ij}(w)\ne 0\}.
$$

The observable $R_1(w)$ itself is the generator-labelled directed graph
$E_1^{\mathrm{gen}}(w)$. Whenever a numerical edge count is quoted, the
convention is stated explicitly.

### Definition 11 (R-Two Repair Graph)

The second accessibility observable is the projected commutator-survival graph
$R_2(w)$. For generators $g,h\in S$, define

$$
C^{g,h}_{ij}(w)
=
Q_i(w)[X_g,X_h]Q_j(w).
$$

The $R_2$ graph records the labeled pair $(g,h)$ from sector $j$ to sector $i$
when

$$
C^{g,h}_{ij}(w)\ne 0.
$$

Equivalently, $R_2(w)$ records which length-two commutator candidates survive
after projection to the moving joint-sector decomposition. This is the first
repair layer beyond the support graph $R_1(w)$.

### Definition 12 (Minimal Accessibility Depth)

The minimal accessibility depth data $D(w)$ records, for each ordered sector
pair $(i,j)$, the least depth at which the pair becomes accessible under the
chosen accessibility calculus. In the present theorem layer, depth $0$ means
direct generator support ($R_1$), depth $1$ means first commutator survival
($R_2$), and larger depths belong to the higher Lie/PBW/word towers discussed
in the accessibility framework.

We write

$$
D(w)=(D_{ij}(w))_{i,j}.
$$

The precise depth convention must be kept fixed within any theorem statement.
For Paper VI, the role of $D(w)$ is to detect whether the moving sectorized
system changes the gap between Lie-generated accessibility and
composition-generated accessibility.

## Accessibility Fields and Jets

The objects $R_1(w)$, $R_2(w)$, and $D(w)$ are discrete-valued functions on a
tested local base. Their discontinuities are therefore not explained by
ordinary differentiability of the functions themselves. The geometric object
that mediates between the tested local commutativity model and the discrete
accessibility data is the collection of matrix fields from which those
discrete data are read.

### Definition 13 (Accessibility Fields)

On a neighborhood $U\subset\Sigma_{\mathrm{spec}}$ where the joint-sector
projectors $Q_i(w)$ vary smoothly, define the accessibility fields:

$$
B^g_{ij}(w)=Q_i(w)X_gQ_j(w),
$$

$$
C^{g,h}_{ij}(w)=Q_i(w)[X_g,X_h]Q_j(w),
$$

and, for each Hall monomial $M$ used in the finite-depth accessibility
calculus,

$$
H^M_{ij}(w)=Q_i(w)M Q_j(w).
$$

The Hall monomial language is the finite-depth Lie algebra background inherited
from Paper V \cite{paper5}, using Hall bases and free-Lie-algebra conventions
\cite{hall1950,reutenauer1993}. The Lie-generated accessibility viewpoint is
aligned with the standard control-theoretic use of Lie brackets
\cite{jurdjevic1997}; the basic Lie identities are those of the standard
finite-dimensional Lie algebra setting \cite{humphreys1972}.

The discrete observables are the support, commutator-survival, and first-depth
shadows of these fields:

$$
R_1(w)=\operatorname{supp}(B(w)),\qquad
R_2(w)=\operatorname{supp}(C(w)),\qquad
D(w)=\operatorname{firstdepth}(H(w)).
$$

Thus $R_1,R_2,D$ are not fixed invariants attached once and for all to the
representation. They are functions on normal spectral charts
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$, obtained by applying
rank/support thresholds to smooth matrix fields.

It is convenient to bundle the first-order responses of these fields into the
accessibility jet components

$$
\mathcal{J}_{\mathrm{acc}}(w)
=
\bigl(J_{\mathrm{block}}(w),J_{\mathrm{comm}}(w),J_{\mathrm{depth}}(w)\bigr),
$$

where

$$
J_{\mathrm{block}}=j^1B,\qquad
J_{\mathrm{comm}}=j^1C,\qquad
J_{\mathrm{depth}}=j^1H.
$$

Thus $J_{\mathrm{block}}$ is the generator-support response,
$J_{\mathrm{comm}}$ is the Lie-defect tensor, and $J_{\mathrm{depth}}$ is the
composition-propagation kernel.

### Definition 14 (Accessibility Jet Bundle)

The accessibility jet at $w\in\Sigma_{\mathrm{spec}}\subseteq
\Sigma_{\mathrm{comm}}$ is the first-order data

$$
\mathcal{J}_{\mathrm{acc}}(w)
=
j^1_w\bigl(B,C,H\bigr),
$$

where $B,C,H$ denote the block, projected-commutator, and Hall projection
fields above. For a tangent vector $v\in T_w\Sigma_{\mathrm{comm}}$ represented
by a local curve in $\Sigma_{\mathrm{spec}}$, the
accessibility jet gives the directional first variations

$$
\nabla_v B^g_{ij},\qquad
\nabla_v C^{g,h}_{ij},\qquad
\nabla_v H^M_{ij}.
$$

The discrete data $R_1,R_2,D$ are shadows of these three jet components. They
are locally constant precisely where the relevant matrix fields keep the same
support and rank profile. Accessibility walls are therefore rank/support
discriminants of the accessibility jet bundle.
This terminology is intentionally geometric: it uses only first-order jet data
of the underlying matrix fields, in the standard sense of jet-bundle geometry
\cite{saunders1989}.

### Theorem 3 (Jet-to-Accessibility Reduction)

Let $w_0\in\Sigma_{\mathrm{spec}}$ be a point where the commutator map has
stable Jacobian rank, no hidden kernel emergence, first-order linearization
accuracy, and a normal spectral chart in a neighborhood of $w_0$. Let
$v\in T_{w_0}\Sigma_{\mathrm{comm}}$ be represented by a local curve
$w(\varepsilon)\subset\Sigma_{\mathrm{spec}}$ with $w(0)=w_0$ and
$w'(0)=v$. Then the jet bundle
$\mathcal{J}_{\mathrm{acc}}$ is well defined in that neighborhood, and the
QT/HT pair has a first-order expansion

$$
(Q_T(w(\varepsilon)),H_T(w(\varepsilon)))
=
(Q_T(w_0),H_T(w_0))
+\varepsilon\,J(v)+O(\varepsilon^2),
$$

and the accessibility fields have first-order expansions

$$
B(w(\varepsilon))=B(w_0)+\varepsilon\,\nabla_v B+O(\varepsilon^2),
$$

$$
C(w(\varepsilon))=C(w_0)+\varepsilon\,\nabla_v C+O(\varepsilon^2),
$$

$$
H(w(\varepsilon))=H(w_0)+\varepsilon\,\nabla_v H+O(\varepsilon^2).
$$

Consequently, the accessibility jet $\mathcal{J}_{\mathrm{acc}}(w_0)$ gives
the first-order continuation of the matrix data from which $R_1,R_2,D$ are
read.

Moreover,

$$
R_1=\Pi_1(\mathcal{J}_{\mathrm{acc}}),\qquad
R_2=\Pi_2(\mathcal{J}_{\mathrm{acc}}),\qquad
D=\Pi_D(\mathcal{J}_{\mathrm{acc}})
$$

for the support, commutator-survival, and first-depth projection maps
$\Pi_1,\Pi_2,\Pi_D$. These projection maps are measurable and discrete-valued:
they forget the continuous matrix entries and retain only the rank/support
data relevant to accessibility.

**Interpretation.** The discrete observables themselves do not have linear
Taylor expansions. Instead, their defining matrix fields do. On any region
where these fields preserve rank and support, the discrete shadow
$(R_1,R_2,D)$ is locally constant. An accessibility wall is the locus where
this first-order continuation fails to preserve the rank/support profile.

## Spectral Walls and Accessibility Walls

The spectral wall hierarchy is

$$
\Sigma_{\mathrm{field}}
\subseteq
\Sigma_L
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}.
$$

Here $\Sigma_{\mathrm{comm}}$ is the commutator wall, while
$\Sigma_{\mathrm{spec}}$ is the normal commutative spectral domain on which the
collision quotient and orthogonal sector projectors are used. $\Sigma_L$
records layer-count jumps, and
$\Sigma_{\mathrm{field}}$ records field changes. These are spectral
stratification walls. They describe how the joint arrangement $P(w)$ moves,
splits, merges, and changes arithmetic field.

They are not accessibility walls by definition.

### Definition 15 (Accessibility Wall)

An accessibility wall is a locus inside a normal spectral chart
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$ where the
accessibility discriminant

$$
\Delta_{\mathrm{access}}(w)
$$

detects a failure of local continuation of the rank/support profile of
$\mathcal{J}_{\mathrm{acc}}(w)$. When $\Delta_{\mathrm{access}}$ is taken as
the exact accessibility discriminant, one has

$$
w\in\Sigma_{\mathrm{access}}
\iff
\text{the rank/support profile of }\mathcal{J}_{\mathrm{acc}}(w)
\text{ is not locally constant}.
$$

Equivalently, at least one of the discrete accessibility observables is not
locally constant. We write

$$
\Sigma_{\mathrm{access}}
=
\{w\in\Sigma_{\mathrm{spec}}:(R_1,R_2,D)\ \text{is not locally constant}\}.
$$

Under this exact-discriminant convention, $\Sigma_{\mathrm{access}}$ is the
union of the rank/support discriminants for the block, projected-commutator,
and Hall projection fields. The three visible components are

$$
\Sigma_{R_1}
=
\{w\in\Sigma_{\mathrm{spec}}:R_1(w)\ \text{is not locally constant}\},
$$

$$
\Sigma_{R_2}
=
\{w\in\Sigma_{\mathrm{spec}}:R_2(w)\ \text{is not locally constant}\},
$$

and

$$
\Sigma_D
=
\{w\in\Sigma_{\mathrm{spec}}:D(w)\ \text{is not locally constant}\}.
$$

At the support level, again under the exact-discriminant convention,

$$
\Sigma_{\mathrm{access}}
=
\Sigma_{R_1}\cup\Sigma_{R_2}\cup\Sigma_D.
$$

The cumulative and residual wall convention used below refines this union by
separating walls that occur after lower-level data have been held fixed. The
main accessibility-theoretic problem is to understand the relationship between
this accessibility discriminant and the spectral walls $\Sigma_L$ and
$\Sigma_{\mathrm{field}}$ inside $\Sigma_{\mathrm{spec}}$.

### Remark 2 (Spectral Walls Are Not Accessibility Walls)

A field change in the collision quotient is a spectral event. It may indicate
that the arithmetic form of the moving arrangement has changed, and it may be
correlated with accessibility changes. But this correlation is not a
definition. The accessibility wall is detected only when $R_1(w)$, $R_2(w)$,
or $D(w)$ changes.

This separation is essential for Paper VI. It prevents the theorem layer from
identifying an arithmetic spectral transition with a Lie/composition
accessibility transition before the corresponding $R_1/R_2/D$ data have been
computed.

## Accessibility Stratification

The central structural claim of Paper VI is not merely that
$\Sigma_{\mathrm{comm}}$ admits a computational tangent-local scaffold (Theorem 1)
or that sectors fragment (Theorem 2). It is that the accessibility data
$R_1,R_2,D$ form a **discrete stratification** of this local model, and that
this stratification is combinatorial in origin -- governed by block-rank jumps,
not by nonlinearity of the local base.

### Local Constancy Lemma (Computational)

Let $w_0\in\Sigma_{\mathrm{spec}}$ and let $v$ be a tangent direction in
$T_{w_0}\Sigma_{\mathrm{comm}}$ represented by a local curve
$w(\varepsilon)\subset\Sigma_{\mathrm{spec}}$ with
$w(0)=w_0$ and $w'(0)=v$. In the tested kernel families below, this curve is
given by the verified finite-amplitude continuation used in the support
scripts. A generic straight line $w_0+\varepsilon v$ is not assumed to remain
inside the commutativity locus.

**Lemma 2 (Sector Projector Smoothness).** For sufficiently small
$\varepsilon$, the joint-spectral projectors $Q_i(w(\varepsilon))$ vary
smoothly (to first order, linearly) with $\varepsilon$. The joint spectral
points $(q_i(\varepsilon),h_i(\varepsilon))$ satisfy
$\|(q_i(\varepsilon),h_i(\varepsilon))-(q_i(0),h_i(0))\|\propto\varepsilon$.

This is verified numerically: along kernel direction $1$ at $w=\mathbf{1}$,
the $(q,h)$-point drift satisfies $\mathrm{drift}/\varepsilon\approx 0.07$ for
all $9$ points up to the fragmentation threshold ($\varepsilon\approx
3\times 10^{-7}$).

**Lemma 3 (Block-Rank Piecewise Constancy).** For a fixed sector pair $(i,j)$
and generator $g$, the block map $B^g_{ij}(w)=Q_i(w)X_gQ_j(w)$ has a rank
that is piecewise constant in $\varepsilon$. Rank jumps occur at discrete values
of $\varepsilon$ where the joint spectral geometry undergoes a combinatorial
transition (sector count change, eigenvalue crossing, or subspace alignment).

This is verified numerically: along a generic kernel direction, the total
generator-labelled edge count $|E_1^{\mathrm{gen}}|$ jumps from $438$ to
$5346$ at the first fragmentation threshold, then remains piecewise constant
with additional discrete jumps at larger $\varepsilon$.

### Accessibility Stratification Theorem

**Theorem 4 (Accessibility Stratification on a Normal Commutative Chart).**
Let $w_0\in\Sigma_{\mathrm{spec}}$ be a point where the joint-spectral sector
projectors $Q_i(w)$ depend smoothly on $w$ in a neighborhood
$U\subset\Sigma_{\mathrm{spec}}$. Then on $U$:

**(i) $R_1$ wall.** $R_1(w)$ is locally constant on the open set where all
block ranks $\operatorname{rank}(B^g_{ij}(w))$ are constant. A change in
$R_1(w)$ occurs only when at least one block rank changes -- that is, at the
locus

$$
\Sigma_{R_1}=\{w\in\Sigma_{\mathrm{spec}}:
\exists\, i,j,g:\ \operatorname{rank}(B^g_{ij}(w))\ \text{jumps}\}.
$$

**(ii) $R_2$ wall.** $R_2(w)$ is not determined by $R_1(w)$. Both are
different discrete projections of the accessibility jet
$\mathcal{J}_{\mathrm{acc}}$: $R_1$ is read from the block-field support, while
$R_2$ is read from projected commutator survival. With $R_1(w)$ fixed, the
projected commutator blocks $Q_i(w)[X_g,X_h]Q_j(w)$ are computed from the
accessibility fields, specifically the block fields and their projected
commutators. $R_2(w)$ is locally constant on the open subset of the
$R_1$-stratum where all projected commutator block ranks are constant. A change
in $R_2(w)$ while $R_1(w)$ is fixed occurs at the locus

$$
\Sigma_{R_2}^{\circ}=\{w\in\Sigma_{\mathrm{spec}}\setminus\Sigma_{R_1}:
\exists\, i,j,g,h:\ \operatorname{rank}(Q_i(w)[X_g,X_h]Q_j(w))\ \text{jumps}\}.
$$

**(iii) $D$ wall.** With $R_1(w)$ and $R_2(w)$ fixed, the Lie-depth matrix
$D(w)$ is determined by the weighted Hall coefficients (Paper V). $D(w)$ is
locally constant on the open subset of the $(R_1,R_2)$-stratum where all
relevant Hall monomial projections have constant rank. A change in $D(w)$
while $R_1,R_2$ are fixed occurs at

$$
\Sigma_D^{\circ}=\{w\in\Sigma_{\mathrm{spec}}\setminus(\Sigma_{R_1}\cup\Sigma_{R_2}^{\circ}):
D(w)\ \text{jumps}\}.
$$

**(iv) Hierarchy.** The residual walls
$\Sigma_{R_2}^{\circ}$ and $\Sigma_D^{\circ}$ record changes that occur after
lower-level data are held fixed. The corresponding cumulative wall sets are

$$
\widehat{\Sigma}_{R_1}=\Sigma_{R_1},\qquad
\widehat{\Sigma}_{R_2}=\Sigma_{R_1}\cup\Sigma_{R_2}^{\circ},\qquad
\widehat{\Sigma}_{D}=\Sigma_{R_1}\cup\Sigma_{R_2}^{\circ}\cup\Sigma_D^{\circ}.
$$

Thus the accessibility observables have the cumulative hierarchy

$$
\boxed{\widehat{\Sigma}_{R_1}\ \subseteq\ \widehat{\Sigma}_{R_2}\ \subseteq\ \widehat{\Sigma}_{D}
=\Sigma_{\mathrm{access}}\ \subseteq\ \Sigma_{\mathrm{spec}}\ \subseteq\ \Sigma_{\mathrm{comm}}.}
$$

On the local domain $U\subset\Sigma_{\mathrm{spec}}$, outside
$\widehat{\Sigma}_{D}\cap U$, the full accessibility triple $(R_1,R_2,D)$ is
locally constant. Thus $U$ carries a local stratification by the level sets of
$(R_1,R_2,D)$, and these strata are separated by the cumulative wall loci. This
is a local stratification on a normal chart of the commutativity locus; extending it to the
ambient moduli space $\mathcal{M}=[0,1]^{18}$ would require a separate theory.

![Accessibility wall hierarchy. The accessibility jet projects to the discrete
observables $R_1$, $R_2$, and $D$; the cumulative wall sets record where these
rank/support shadows fail to continue locally.](../../figures/paper6/fig5_accessibility_wall_hierarchy.png)

**(v) Wall origin.** The residual and cumulative accessibility walls are not
caused by nonlinearity of $\Sigma_{\mathrm{comm}}$. They are caused by
combinatorial instability of block projections under smooth (to first order,
linear) deformation of the joint spectral points on $\Sigma_{\mathrm{spec}}$.
The mechanism is:

$$
\text{smooth motion of }(q_i,h_i)
\ \longrightarrow\ 
\text{discrete jump in block rank}
\ \longrightarrow\ 
\text{discrete change in }R_1/R_2/D.
$$

This is the **Accessibility Wall Mechanism**: accessibility walls describe
where the projection of spectral geometry onto the sector decomposition ceases
to be structurally invariant.

### Lie-versus-Composition Phase Transition

The accessibility wall formalism is designed to detect changes in the gap
between Lie-generated and composition-generated accessibility. Away from
$\Sigma_{\mathrm{access}}$, the local accessibility jet has constant
rank/support profile, so the triple $(R_1,R_2,D)$ is locally constant. In that
region the comparison between Lie-generated accessibility and compositional
accessibility is stable under small generator-set perturbations.

Crossing $\Sigma_{\mathrm{access}}$ changes this comparison. A jump in $R_1$
changes direct generator support. A residual jump in $R_2$ changes which
length-two commutator candidates survive after projection while direct support
is held fixed. A jump in $D$ changes the minimal depth at which a sector pair
becomes accessible. Thus accessibility walls are phase-transition loci for the
Lie-versus-composition gap.

### Computational Support

The stratification pattern is supported by three probes:

**Rubik cube (18 generators, moving sectors).** Along a generic kernel
direction in the tested normal spectral chart:

| $\varepsilon$ | Sectors | $|E_1^{\mathrm{gen}}|$ | Event |
|---------------|---------|--------------------------|-------|
| $0$ (canonical) | $9$ | $438$ | maximally coarse point |
| $\sim 10^{-7}$ | $24$ | $4520$ | **sector fragmentation** |
| $\sim 10^{-5}$ | $24$ | $4520$ | stable |
| $\sim 10^{-4}$ | $34$ | $6264$ | **secondary fragmentation** |
| $10^{-2}$ | $35$ | $6334$ | **tertiary wall** |
| $0.1$--$1.0$ | $35$ | $6334$ | **piecewise constant** |

Five distinct walls detected. The canonical point is a maximally coarse
configuration: every tested small QT kernel perturbation triggers
sector fragmentation.

**S4-3gen-B (3 generators, fixed sectors).** Varying the weight of generator
$c$ from $0$ to $1$:

| Weight $c$ | $|E_1^{\mathrm{gen}}|$ | Event |
|------------|--------------------------|-------|
| $0$ | $15$ | degenerate (c-blocks vanish) |
| $10^{-8}$ | $32$ | **first $R_1$ jump** |
| $10^{-6}$ | $33$ | **second $R_1$ jump** |
| $10^{-4}$--$1.0$ | $33$ | **piecewise constant** |

**A5-3gen (3 generators, 15 sectors).** Identical pattern:

| Path | $|E_1^{\mathrm{gen}}|$ at $t=0$ | $|E_1^{\mathrm{gen}}|$ at $t>0$ | Jump at |
|------|----------------------------------|------------------------------------|---------|
| c-weight scan | $48$ | $86$ | $t=10^{-8}$ |
| a-weight scan | $76$ | $86$ | $t=10^{-8}$ |
| uniform scan | $0$ | $86$ | $t=10^{-8}$ |

**Common pattern in tested systems.** Across all three systems, regardless of
mechanism (sector fragmentation in Rubik vs. block-norm crossing in S4/A5), the
same structural pattern is observed: degenerate weight configurations at
isolated or low-dimensional points in the tested scans reduce $R_1$; small
perturbations trigger discrete $R_1$ jump(s); after the jump, $R_1$ is piecewise constant; walls form a nested
hierarchy. This tested pattern suggests a general wall phenomenon -- a
combinatorial bifurcation on a continuous background, not a Rubik-specific
accident.

***

## Computational Reproducibility

The computational claims in this paper are supported by the following
repository scripts, listed by role:

| Label | Role |
|-------|------|
| Moduli scan | global generator-set scans, collision quotient versus A-spectrum, and stabilized bifurcation tables |
| Tangent map | tangent model for $T_{\mathbf{1}}\Sigma_{\mathrm{comm}}$ and tested nonlinear-kernel searches |
| Fragmentation audit | sector fragmentation and $R_1$ wall formation along kernel directions |
| Wall-crossing summary | compact mechanism-level accessibility wall-crossing support table |

The corresponding scripts live in `experiments/paper6/`, with a shared utility
layer for phase tables. Exploratory searches and verbose demonstrations are
retained in the repository for provenance, but the manuscript relies only on
the summarized tables above.

## Generator-Set Probes

The following tables are not separate theoretical inputs. They are finite
probes of the wall picture developed above. Single-generator deletions test
transverse directions in the ambient weight space: they show how easily one
leaves $\Sigma_{\mathrm{comm}}$, so the collision quotient becomes undefined
even though the global $A$-spectrum continues to vary. The selected generator
families test special lower-dimensional faces and slices: some remain inside
the normal commutative spectral domain, while others cross the commutativity wall. Together
they display the two-observable distinction that motivates Paper VI:

$$
\begin{aligned}
\text{collision quotient} &:\ \Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}},\\
A(w)\text{-spectrum} &:\ \text{ambient weight space}.
\end{aligned}
$$

These probes also locate the spectral part of the wall hierarchy before the
accessibility jet is applied. Once a path lies in a normal spectral chart
$\Sigma_{\mathrm{spec}}$, the moving sector projectors give accessibility
fields and the question becomes whether the associated jet crosses
$\Sigma_{\mathrm{access}}$.

### Single-Generator Deletions

All 18 single-generator deletions exit $\Sigma_{\mathrm{comm}}$. The A-spectrum
shows 14 layers (HT deletion) or 21 layers (QT deletion), all with mixed field.
This is now understood via Theorem 1: single-coordinate directions have
residual $0.707$ (QT) or $0.913$ (HT) outside the kernel.

### Selected Generator Families

| Family | CQ status | CQ layers | CQ field | A-layers | A-field |
|--------|-----------|-----------|----------|----------|---------|
| $n=18$ full | defined | 6 | $\mathbb{Q}$ | 6 | $\mathbb{Q}$ |
| $n=16$ drop axis-0 HT | blocked | -- | undefined | 9 | mixed |
| $n=15$ drop negative-face HT | blocked | -- | undefined | 23 | mixed |
| $n=14$ drop axis-1 QT | defined | 10 | mixed | 8 | mixed |
| $n=12$ QT only | defined | 6 | $\mathbb{Q}$ | 6 | $\mathbb{Q}$ |
| $n=6$ HT only | defined | 3 | $\mathbb{Q}$ | 3 | $\mathbb{Q}$ |

## Outlook

The present paper establishes the geometric framework and the computational
local model at the canonical point. Several algebraic questions remain open.
First, the global ideal $I_{\mathrm{comm}}$ should be reduced to explicit
defining equations for the commutativity wall. Second, the rank strata of the
commutator map should be characterized algebraically, rather than only through
numerical signatures such as the observed ranks $0,52,88,96$. Third, the
accessibility walls associated with $R_2$ and $D$ should be computed on
selected normal spectral strata
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$.

The cancellation and incidence mechanism examples inherited from Paper V show
that $R_1$ can remain fixed while $R_2$ or $D$ changes under perturbation.
These examples motivate, but do not yet constitute, a general classification
theorem for accessibility walls. Such a theorem would require combining the
commutator ideal of $\Sigma_{\mathrm{comm}}$ with the weighted Hall path data
controlling finite-depth accessibility.

Paper VII \cite{paper7} continues this same structure in the static direction.
It treats the accessibility jet as the candidate completion object and
identifies Type IV incidence as a high-codimension algebraic degeneration.
Thus the three papers should be read as different projections of one framework:
Paper V classifies the local mechanisms, Paper VI studies how their observable
shadows move on normal spectral charts inside $\Sigma_{\mathrm{comm}}$, and
Paper VII isolates the generic completion boundary.

## Conclusion

Paper IV studies collision quotients of a fixed joint arrangement. Paper VI
shows what changes when the generator set itself varies: the arrangement
becomes $P=P(w)$, the collision quotient is defined only on the normal
commutative spectral domain, and the accessibility data carried by the moving
sectors become piecewise-constant observables with their own walls.

At the canonical Rubik point, the commutativity wall has a computationally
verified $7$-dimensional tangent model with codimension $11$. Along the tested
kernel-family spectral charts, the canonical nine-sector decomposition is maximally
coarse: tested QT kernel directions fragment the sectors and trigger discrete
changes in $R_1$. Spectral walls describe how the arrangement moves;
accessibility walls describe when that motion changes the gap between
Lie-generated and composition-generated accessibility.

This gives a common observable architecture for the later papers. A point of
$\Sigma_{\mathrm{spec}}$ determines a sectorized observable framework

$$
\mathcal S(w)=\bigl(V,\{Q_i(w)\},\{X_g\}_{g\in S}\bigr),
$$

and $R_1(w)$, $R_2(w)$, $D(w)$, and
$\mathcal J_{\mathrm{acc}}(w)$ are derived fields of this sectorized block
geometry. Paper V studies these fields for a fixed sectorized framework. Paper VI
studies their variation over the commutative deformation base. Paper VII
\cite{paper7} studies generic completion away from the incidence strata where
the block geometry becomes nongeneric.

## References

**Program lineage.** Paper VI depends internally on Papers I--V and the CCS:
Papers I--III define the canonical Rubik spectral, sector, transport, and
accessibility data \cite{paper1,paper2,paper3,ccs}; Paper IV supplies the
fixed-arrangement collision-quotient viewpoint \cite{paper4}; Paper V supplies
the local $R_1/R_2/D$ repair calculus and weighted Hall path language
\cite{paper5}. The reproducibility scripts are listed explicitly in the
Computational Support section.

**External background.** Finite-group representations and the Rubik group
setting use the standard references \cite{serre1977,joyner2008}. The
fixed/moving joint-spectrum side is closest to finite-dimensional spectral
algebra and algebraic combinatorics, with association-scheme and
Bose--Mesner algebras serving as comparison classes rather than asserted
identifications \cite{bannaiIto1984,godsil1993}. Quotients of association
schemes and modern Bose--Mesner computational tools provide neighboring
formalisms for quotient structures in commutative semisimple matrix algebras
\cite{godsilMartin1995quotients,martin2021scaffolds}; here they are cited as
background, not as an identification of the QT/HT algebra with an association
scheme. The local geometry of $\Sigma_{\mathrm{comm}}$ uses smooth-manifold,
jet-bundle, and local algebraic-geometry language \cite{lee2013,saunders1989,
harris1992,eisenbud1995}. The accessibility layer uses Hall bases, free Lie
algebras, standard Lie algebra identities, and geometric-control accessibility
language \cite{hall1950,reutenauer1993,humphreys1972,
jurdjevic1997,agrachevSachkov2004}. Matrix-rank and rank-stability arguments
are interpreted in the standard matrix-analysis setting
\cite{hornJohnson2013}.

**Computational provenance.** The Paper VI support suite consists of the moduli
scan, tangent map, fragmentation audit, wall-crossing summary, and shared
phase-table utilities.
Exploratory searches and verbose demonstrations remain in the repository for
provenance, but the manuscript relies only on those summarized tables.

