# Transformation Laws and Localized Stability of Generator-Resolved Diagnostics
### Exact Transport Covariance, Carrier-Localized Perturbation, and Minimax Information Bounds

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*Paper XXV of the RIME program. This paper develops a finite-dimensional
methods layer for aligned generator-resolved diagnostics, separating exact
transport covariance, carrier-local perturbation, and application-specific
semantics.*

## Abstract

**Problem.** A generator-resolved block $Q_iY_aQ_j$ depends on the labelled
operator, the marked source and target carriers, and the frame in which those
data are compared. Global norm budgets remain portable but can erase exactly
the localization information needed to decide whether a thresholded block is
stable.

**Approach.** A typed finite-dimensional diagnostic instance separates
representation-intrinsic, labelled-generator-relative, and
marked-sectorization-relative data. After two instances are aligned by a
unitary, each block difference resolves into left-carrier motion, additive
operator error, and right-carrier motion. Global, semi-local, and local error
summaries are ordered by an explicit information lattice.

**Results.** Simultaneous unitary transport preserves weighted averages,
commutants, labelled block norms, and thresholded activity relations. The
aligned block difference has an exact three-term decomposition with a portable
global bound and a sharper carrier-localized bound. All three one-axis global
constants are sharp. In the fixed-projector additive-error submodel, global
norms cannot detect localization, and every node of the carrier-information
lattice has an exact minimax envelope. Additive error has
an exact conditional completion for fixed carrier motion, and the localized
triangle bound has a complete equality criterion. Margin theorems
separate stable activity, stable inactivity, and an information-theoretically
complete unresolved interval. The algebra and localized bound extend to
bounded oblique carrier resolutions, with explicit projector-conditioning
factors. Exact rational controls and bounded float64 observations are kept
distinct: Rubik supplies the simultaneous-transport hostile control, while the
two-state Markov construction supplies a portability example.

**Boundary.** The elementary conjugation and telescoping identities are not
claimed as new in isolation. The results control declared finite-dimensional
blocks; they do not reconstruct a representation, decide survival of an
arbitrary routed product, estimate distance to the incidence locus $AB=0$, or
establish general spectral, pseudospectral, Markov-mixing, continuum, or
open-quantum-channel stability.

**Keywords:** operator perturbation; sector projectors; localized matrix
blocks; minimax bounds; oblique projections; threshold stability; typed
diagnostics.

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $V$ | finite-dimensional complex Hilbert space |
| $A$, $I$ | labelled generator and sector index sets |
| $Y_a$, $Q_i$ | represented operator and marked sector projector |
| $\mu_a$, $M_\mu(Y)$ | labelled weight and weighted generator average |
| $B_a(i,j)=Q_iY_aQ_j$ | generator-resolved block |
| $\mathcal R_\tau(a;i,j)$ | thresholded labelled activity predicate |
| $U$, $\bar Y_a$, $\bar Q_i$ | alignment unitary and transported reference data |
| $E_a$, $\Delta_i$ | operator and carrier perturbations |
| $D_a(i,j)$ | aligned generator-resolved block difference |
| $b_{\rm loc}$, $b_{\rm glob}$, $b_{\rm obl}$ | localized, global, and oblique-carrier bounds |
| $\mathcal I_G,\mathcal I_L,\mathcal I_R,\mathcal I_{LR},\mathcal I_{\rm loc}$ | cumulative carrier-information levels |
| $U_G,U_L,U_R,U_{LR},U_{\rm loc}$ | exact minimax envelopes at those levels |
| $\tau$, $b$ | activity threshold and certified error radius |

## Introduction

This paper studies one concrete comparison question: which properties of a
labelled operator-block diagnostic survive aligned change of frame, and what
is the sharpest block-stability statement justified by a declared level of
global or carrier-local information?

The basic coordinate is

$$
B_a(i,j)=Q_iY_aQ_j.
$$

It has three owners. The represented family controls $Y_a$; the labelled
generator or measure policy controls which operators are retained and how they
are averaged; and the marked sectorization controls the source and target
carriers. A comparison that transports only one owner is not an aligned
comparison. A bound that retains only $\lVert Y_a\rVert$ and
$\lVert E_a\rVert$ is valid but may
discard whether the perturbation reaches the selected carriers at all.

The theorem spine follows this distinction. Section 2 introduces the typed
diagnostic instance, proves simultaneous-transport covariance, and states its
fixed-frame and similarity boundaries. Section 3 proves the exact
three-term perturbation identity, global and localized bounds, the bounded
oblique extension, sharpness, the carrier-information lattice, exact minimax
envelopes in the fixed-projector additive-error submodel, conditional additive
completion for fixed carrier geometry, and the equality criterion.
Section 4 converts certified block radii into a complete threshold trichotomy.
Section 5 gives a deliberately narrow two-state Markov portability lift.
Section 6 separates exact certificates from bounded observations and states
their frozen numerical protocols.

The central distinction is

$$
\text{portable global control}
\ne \text{carrier-local information}
\ne \text{application-specific semantics}.
$$

The first inequality creates the minimax information problem. The second
prevents a Hilbert-space block estimate from being renamed a probability,
support, reconstruction, or routed-composition theorem without additional
hypotheses.

## Related Work and Novelty Boundary {.unnumbered}

Norm inequalities, invariant subspaces, oblique projections, and matrix
perturbation theory are standard background
\cite{hornJohnson2013,stewartSun1990,kato1995perturbation}. Finite Markov-chain
hitting times, regeneration, and stationary distributions are standard tools
\cite{kemenySnell1960,norris1997,levinPeresWilmer2017}; the narrow lift in
Section 5 is stated only under its explicit two-state hypotheses. The ideal-property
estimate for the Frobenius norm, unitary invariance, and the algebraic
telescoping of a three-factor difference are standard ingredients; the
telescoping inequality alone is not the principal novelty. The contribution is
their typed ownership interface: transformation laws for labelled diagnostics,
localized evidence resolution, exact minimax envelopes, sharpness and equality
theorems, and a complete threshold-uncertainty boundary.

Within the RIME program, Paper II introduced the direct sector block
$Q_iY_aQ_j$ as the carrier of generator transport and related off-diagonal
Frobenius mass to sector non-invariance \cite{paper2}. Paper III separated
direct support from projected composition and isolated the static obstruction

$$
AB=0
\quad\Longleftrightarrow\quad
\operatorname{im}B\subseteq\ker A
$$

for a two-block route \cite{paper3}. Paper VII developed that obstruction into
rank-stratified, carrier-resolved incidence geometry; its transported-frame
covariance proposition also records covariance of routed products, Frobenius
norms, and profile counts under simultaneous transport of operators, sectors,
and carriers \cite{paper7}. Paper XX organizes the fixed-carrier geometry at
every finite route depth through carrierwise factorization, cutwise
image--kernel tests, and survivor recursion \cite{paper20}.

Theorem 2.1 packages the covariance of Paper II's direct block at the typed
diagnostic level, including labelled weights, weighted averages, commutants,
unitarily invariant block norms, and thresholded labelled activity. Its
elementary block-conjugation identity is not reclaimed as a new fact.
Theorem 3.1 has a different role: it compares one block in two aligned frames
and resolves its finite difference into motion of the left carrier, operator,
and right carrier. It is a metric finite-difference counterpart of the earlier
static block-incidence geometry, not a derivation from the image--kernel
criterion.

The perturbation theorem therefore does not decide survival of a routed
product, estimate distance to $\{(A,B):AB=0\}$, or propagate error through Paper
XX's all-depth survivor recursion. Those extensions require productwise,
transversality, or carrier-preservation hypotheses not assumed here.

## Typed Unitary Transport

### Typed diagnostic instances

Let $V$ be a finite-dimensional complex Hilbert space. Let $A$ and $I$ be
finite label sets. A typed generator-resolved diagnostic instance consists of

$$
\mathcal D=(V,A,I,Y,Q,\mu,\lVert\cdot\rVert_F,\mathsf{zero}),
$$

where

$$
Y:A\longrightarrow\operatorname{End}(V),\quad a\longmapsto Y_a,
\qquad
Q:I\longrightarrow\operatorname{End}(V),\quad i\longmapsto Q_i,
$$

the $Q_i$ are nonzero mutually orthogonal projectors with
$\sum_iQ_i=I_V$, and $\mu$
is a declared labelled weight family. Labels are part of the data: equal
represented operators do not identify distinct source labels.

Define the weighted generator average and labelled blocks by

$$
M_\mu(Y)=\sum_{a\in A}\mu_aY_a,
\qquad
B_a(i,j)=Q_iY_aQ_j.
$$

For a declared threshold $\tau\ge0$, define the generator-resolved activity
predicate

$$
\mathcal R_\tau(a;i,j)
\quad\Longleftrightarrow\quad
\lVert B_a(i,j)\rVert_F>\tau.
$$

At $\tau=0$, this is exact operator nonvanishing. At positive $\tau$, it is a
strength policy and must not be renamed exact support.

### Typed Unitary Transport Theorem

**Theorem 2.1 (Typed Unitary Transport).** Let

$$
\begin{aligned}
\mathcal D&=(V,A,I,Y,Q,\mu,\lVert\cdot\rVert_F,\mathsf{zero}),\\
\mathcal D'&=(V',A,I,Y',Q',\mu,\lVert\cdot\rVert_F,\mathsf{zero})
\end{aligned}
$$

have the same generator labels, sector labels, labelled weights, and zero
policy. Suppose $U:V\to V'$ is unitary and, for every $a\in A$ and $i\in I$,

$$
Y'_a=UY_aU^\ast,
\qquad
Q'_i=UQ_iU^\ast.
$$

Then:

1. $Q'$ is again a complete orthogonal sectorization with the same labelled
   sector dimensions.
2. The weighted averages satisfy

   $$
   M_\mu(Y')=UM_\mu(Y)U^\ast.
   $$

   Consequently their characteristic polynomials, spectra with algebraic
   multiplicity, and trace moments agree.

3. Every labelled block satisfies

   $$
   Q'_iY'_aQ'_j=U(Q_iY_aQ_j)U^\ast.
   $$

4. For every unitarily invariant matrix norm
   $\lVert\!\lvert\cdot\rvert\!\rVert$,

   $$
   \lVert\!\lvert Q'_iY'_aQ'_j\rvert\!\rVert
   =\lVert\!\lvert Q_iY_aQ_j\rvert\!\rVert.
   $$

   In particular, the full Frobenius block profile and every thresholded
   labelled activity relation $\mathcal R_\tau$ are preserved.
5. Conjugation by $U$ is a vector-space isomorphism

   $$
   \operatorname{Comm}(Y)\longrightarrow\operatorname{Comm}(Y'),
   \qquad T\longmapsto UTU^\ast,
   $$

   so the simultaneous commutant dimensions agree. If the declared family is
   accompanied by a completeness witness for a represented action, this also
   preserves the corresponding representation-intrinsic commutant dimension.

**Proof.** Unitary conjugation preserves adjoints, products, sums, identity,
rank, and orthogonality. Therefore

$$
Q'_iQ'_j=UQ_iQ_jU^\ast,
\qquad
\sum_iQ'_i=U\left(\sum_iQ_i\right)U^\ast=I_{V'}.
$$

Linearity gives the weighted-average identity. Associativity and $U^\ast U=I$
give

$$
Q'_iY'_aQ'_j
=UQ_iU^\ast UY_aU^\ast UQ_jU^\ast
=U(Q_iY_aQ_j)U^\ast.
$$

Unitary invariance gives the norm equality. Hence zero/nonzero and any common
threshold comparison are preserved coordinatewise. Finally,

$$
TY_a=Y_aT
\quad\Longleftrightarrow\quad
(UTU^\ast)Y'_a=Y'_a(UTU^\ast)
$$

for every label $a$, and the inverse commutant map is conjugation by $U^\ast$.
This proves all claims. $\square$

**Corollary 2.2 (Aggregate activity covariance).** Any aggregate relation
formed from the labelled predicates by fixed Boolean operations, including

$$
(i,j)\in\mathcal R_\tau^{\rm agg}
\quad\Longleftrightarrow\quad
\exists a\in A:\ \mathcal R_\tau(a;i,j),
$$

is preserved under the simultaneous transport in Theorem 2.1.

**Boundary 2.3 (Fixed-frame hostile control).** If the operators are
transported but the projectors are held fixed, the hypotheses of Theorem 2.1
are not satisfied. No block-profile or activity invariance follows. This is an
alignment failure, not a counterexample to the theorem.

**Boundary 2.4 (General similarity is algebraic, not metric).** If $S$ is only
invertible, the algebraic identities still hold with $S^{-1}$ in place of
$U^\ast$:

$$
Y'_a=SY_aS^{-1},
\qquad
Q'_i=SQ_iS^{-1},
\qquad
B'_a(i,j)=SB_a(i,j)S^{-1}.
$$

But the transported idempotents need not be self-adjoint, and Frobenius block
norms need not be preserved. Thus general similarity does not inhabit the
metric conclusion of Theorem 2.1 without an additional transported metric.

## Carrier-Localized Perturbation Theorem

Transport the reference instance into one common Hilbert space and write

$$
\bar Y_a=UY_aU^\ast,
\qquad
\bar Q_i=UQ_iU^\ast.
$$

Let the observed operators and projectors be

$$
Y'_a=\bar Y_a+E_a,
\qquad
Q'_i=\bar Q_i+\Delta_i,
$$

where both $\bar Q$ and $Q'$ are complete orthogonal sectorizations. No
normality or unitarity assumption is imposed on $Y_a$ or $Y'_a$.

**Theorem 3.1 (Carrier-Localized Perturbation Bound).** For every $a\in A$ and
$i,j\in I$, define

$$
D_a(i,j)=Q'_iY'_aQ'_j-\bar Q_i\bar Y_a\bar Q_j.
$$

Then the exact three-term identity

$$
D_a(i,j)
=\Delta_i\bar Y_aQ'_j
+Q'_iE_aQ'_j
+\bar Q_i\bar Y_a\Delta_j
$$

holds. Consequently,

$$
\lVert D_a(i,j)\rVert_F\le b_{\rm loc}(a;i,j),
$$

where

$$
\begin{aligned}
b_{\rm loc}(a;i,j)
={}&\lVert\Delta_i\bar Y_aQ'_j\rVert_F
+\lVert Q'_iE_aQ'_j\rVert_F\\
&+\lVert\bar Q_i\bar Y_a\Delta_j\rVert_F.
\end{aligned}
$$

If declared bounds satisfy

$$
\lVert\Delta_k\rVert_F\le\delta_k,
\qquad
\lVert E_a\rVert_F\le\varepsilon_{a,F},
$$

then also

$$
\lVert D_a(i,j)\rVert_F\le b_{\rm glob}(a;i,j),
$$

with

$$
b_{\rm glob}(a;i,j)
=\lVert Y_a\rVert_2(\delta_i+\delta_j)+\varepsilon_{a,F}.
$$

Moreover, when the right-hand quantities are evaluated from the same exact
operators and declared upper bounds,

$$
b_{\rm loc}(a;i,j)\le b_{\rm glob}(a;i,j).
$$

**Proof.** First separate the additive error:

$$
\begin{aligned}
Q'_iY'_aQ'_j-\bar Q_i\bar Y_a\bar Q_j
={}&\bigl[Q'_i\bar Y_aQ'_j-\bar Q_i\bar Y_a\bar Q_j\bigr]
+Q'_iE_aQ'_j.
\end{aligned}
$$

Insert and subtract $\bar Q_i\bar Y_aQ'_j$ in the bracket. The three
differences are exactly the displayed terms. The triangle inequality gives
$b_{\rm loc}$.

For the global estimate, orthogonal projectors have operator norm at most one,
unitary transport preserves $\lVert Y_a\rVert_2$, and compression by two orthogonal
projectors cannot increase Frobenius norm. Using
$\lVert AB\rVert_F\le\lVert A\rVert_F\lVert B\rVert_2$ and
$\lVert AB\rVert_F\le\lVert A\rVert_2\lVert B\rVert_F$ bounds the three localized terms respectively by

$$
\delta_i\lVert Y_a\rVert_2,
\qquad
\varepsilon_{a,F},
\qquad
\lVert Y_a\rVert_2\delta_j.
$$

Their sum is $b_{\rm glob}$, and the same termwise estimates prove
$b_{\rm loc}\le b_{\rm glob}$. $\square$

**Extension 3.1a (Bounded oblique carriers).** The exact three-term identity
and the inequality

$$
\lVert D_a(i,j)\rVert_F\le b_{\rm loc}(a;i,j)
$$

do not require self-adjointness, mutual orthogonality, or idempotence. They
only use

$$
Q'_k=\bar Q_k+\Delta_k,
\qquad
Y'_a=\bar Y_a+E_a.
$$

To retain carrier semantics, suppose now that $\bar Q_k$ and $Q'_k$ are
bounded, possibly oblique idempotents belonging to two declared resolutions
of the identity. Put

$$
\bar q_k=\lVert\bar Q_k\rVert_2,
\qquad q'_k=\lVert Q'_k\rVert_2,
\qquad \eta_k=\lVert\Delta_k\rVert_2,
\qquad F_a=\lVert\bar Y_a\rVert_F,
\qquad \varepsilon_{a,F}=\lVert E_a\rVert_F.
$$

Then the same identity gives the portable oblique estimate

$$
\begin{aligned}
\lVert D_a(i,j)\rVert_F
\le b_{\rm obl}(a;i,j)
={}&\eta_iF_aq'_j
+q'_i\varepsilon_{a,F}q'_j
+\bar q_iF_a\eta_j.
\end{aligned}
$$

In particular, if all four relevant carrier idempotents have operator norm at
most $K$, then

$$
b_{\rm obl}(a;i,j)
\le KF_a(\eta_i+\eta_j)+K^2\varepsilon_{a,F}.
$$

If the reference carriers are orthogonal, then
$\bar q_i=\bar q_j=1$ and $q'_k\le1+\eta_k$, which gives the fully
delta-controlled specialization

$$
b_{\rm obl}(a;i,j)
\le F_a\bigl[\eta_i(1+\eta_j)+\eta_j\bigr]
+(1+\eta_i)(1+\eta_j)\varepsilon_{a,F}.
$$

**Proof.** The algebraic decomposition and triangle inequality are unchanged.
Apply the ideal-property estimate

$$
\lVert ABC\rVert_F
\le\lVert A\rVert_2\lVert B\rVert_F\lVert C\rVert_2
$$

to the three summands. This gives, in order,

$$
\eta_iF_aq'_j,
\qquad q'_i\varepsilon_{a,F}q'_j,
\qquad \bar q_iF_a\eta_j.
$$

The two specializations follow by substitution and by
$\lVert\bar Q_k+\Delta_k\rVert_2\le1+\eta_k$ in the orthogonal-reference case.
$\square$

This extension is a stability statement, not a similarity invariance
statement: unlike Theorem 2.1, it does not assert preservation of Frobenius
block norms. The factors $\bar q_k,q'_k$ explicitly record the conditioning
cost of passing from orthogonal sectors to oblique carrier coordinates.

**Remark 3.2 (Why the additive error must be combined first).** The alternative
split

$$
\Delta_iY'_aQ'_j+\bar Q_iE_aQ'_j
$$

is algebraically valid, but separately bounding its two terms double-counts
the part $\Delta_iE_aQ'_j$. It yields the weaker global expression

$$
\delta_i(\lVert Y_a\rVert_2+\varepsilon_{a,2})
+\varepsilon_{a,F}+\lVert Y_a\rVert_2\delta_j.
$$

Theorem 3.1 combines those terms as $Q'_iE_aQ'_j$ and removes the spurious
$\delta_i\varepsilon_{a,2}$ contribution. The weaker expression is therefore not
minimax optimal under the stated global information.

**Theorem 3.3 (One-Axis Sharpness of the Global Constants).** Each of the three
coefficients in

$$
b_{\rm glob}
=\lVert Y_a\rVert_2\delta_i+\varepsilon_{a,F}
+\lVert Y_a\rVert_2\delta_j
$$

is best possible when the other two perturbation axes are zero. More precisely:

1. for every $\varepsilon\ge0$, there is a fixed-sectorization additive
   perturbation with $\lVert E_a\rVert_F=\varepsilon$ and block difference exactly
   $\varepsilon$;
2. for every $M\ge0$ and $\delta\ge0$, there is a finite-dimensional
   left-projector perturbation with $\lVert Y_a\rVert_2=M$,
   $\lVert\Delta_i\rVert_F=\delta$, and block difference exactly $M\delta$;
3. the analogous statement holds for a right-projector perturbation.

Consequently no one of the constants $1,1,1$ can be uniformly decreased in a
global-budget theorem, even though no claim is made that the sum is the exact
joint minimax value when several axes are simultaneously nonzero.

**Proof.** For the additive axis, take fixed coordinate projectors onto
$\mathbb C e_1$ and $\mathbb C e_2$, let $\bar Y_a=0$, and set
$E_a=\varepsilon\lvert e_1\rangle\langle e_2\rvert$.

For the left-projector axis, choose an integer $r$ with
$\delta\le\sqrt{2r}$. Let $A,B,C$ be mutually orthogonal subspaces with
dimensions $r,r,2r$. Let $\bar Q_i$ project onto $A$, let an auxiliary sector
project onto $B$, and let $\bar Q_j=Q'_j$ project onto $C$. Rotate each paired
coordinate plane of $A\oplus B$ through an angle $\theta$ satisfying

$$
\sin\theta=\frac{\delta}{\sqrt{2r}}.
$$

The resulting rank-$r$ projector $Q'_i$ satisfies
$\lVert Q'_i-\bar Q_i\rVert_F=\sqrt{2r}\sin\theta=\delta$. The self-adjoint
projector difference has $2r$ singular values equal to $\sin\theta$. Choose
$\bar Y_a$ to be $M$ times an isometry from $C$ onto a complete right-singular
basis of that difference and zero on $C^\perp$. Then

$$
\lVert(Q'_i-\bar Q_i)\bar Y_aQ'_j\rVert_F=M\delta.
$$

Completing $Q'_i$ by the rotated auxiliary projector gives a valid complete
orthogonal sectorization. Taking adjoints gives the right-projector example.
This proves all three assertions. $\square$

**Theorem 3.4 (Global Information Cannot Detect Carrier Localization).** Fix
coordinate projectors $Q_i=\lvert e_1\rangle\langle e_1\rvert$ and
$Q_j=\lvert e_2\rangle\langle e_2\rvert$ in a carrier of dimension at least
three, and set $\bar Y_a=0$. For $\alpha\in[0,1]$, define

$$
u_\alpha=\alpha e_1+\sqrt{1-\alpha^2}\,e_3,
\qquad
E_\alpha=\varepsilon\lvert u_\alpha\rangle\langle e_2\rvert.
$$

All members of this family have exactly the same global data

$$
\lVert E_\alpha\rVert_2=\lVert E_\alpha\rVert_F=\varepsilon,
\qquad
\lVert Y_a\rVert_2=\delta_i=\delta_j=0,
$$

but

$$
\lVert Q_iE_\alpha Q_j\rVert_F=\alpha\varepsilon,
\qquad
\frac{b_{\rm loc}}{b_{\rm glob}}=\alpha
\quad(\varepsilon>0).
$$

Thus $b_{\rm loc}/b_{\rm glob}$ can be arbitrarily small and can equal zero. In the
fixed-projector additive-error submodel, the single localized seminorm

$$
\lambda_{ij}(E_a)=\lVert Q_iE_aQ_j\rVert_F
$$

is an exact certificate for the block error. Conversely, any information
summary that certifies a bound smaller than $\varepsilon$ for $E_0$ must distinguish
$E_0$ from $E_1$; the two global norms alone cannot do so.

**Proof.** $E_\alpha$ is rank one with its two displayed global norms equal to
$\varepsilon$. Its marked compression is
$\alpha\varepsilon\lvert e_1\rangle\langle e_2\rvert$. Since the projectors are fixed and the reference
operator vanishes, this compression is the complete block difference and is
also the sole nonzero term in $b_{\rm loc}$. At $\alpha=0$ and $\alpha=1$ the global
records are identical while the exact local errors are respectively zero and
$\varepsilon$. $\square$

**Remark 3.5 (Information ownership).** $b_{\rm glob}$ needs only global norms.
$b_{\rm loc}$ needs the three carrier-restricted actions in Theorem 3.1, or just
their three Frobenius norms if the actions have already been evaluated. Theorem
3.4 proves a necessity statement in the operator-only submodel: some statistic
that separates on-carrier from off-carrier perturbations is required for a
strict localized improvement. It does not claim that one unique data structure
is minimal among all equivalent encodings.

**Definition 3.6 (Cumulative Carrier-Information Lattice).** In the
fixed-projector additive-error submodel, put $P=Q_i$, $Q=Q_j$,
$p=\operatorname{rank}P$, $q=\operatorname{rank}Q$, and $k=\min(p,q)$.
Consider certified upper budgets

$$
\lVert E\rVert_2\le\varepsilon_2,
\quad \lVert E\rVert_F\le\varepsilon_F,
\quad \lVert PE\rVert_F\le\ell,
\quad \lVert EQ\rVert_F\le r,
\quad \lambda=\lVert PEQ\rVert_F.
$$

The cumulative information levels are

$$
\begin{aligned}
I_G&=(\varepsilon_2,\varepsilon_F),\\
I_L&=(I_G,\ell),& I_R&=(I_G,r),\\
I_{LR}&=(I_G,\ell,r),\\
I_{\rm loc}&=(I_G,\ell,r,\lambda).
\end{aligned}
$$

They form the refinement lattice

$$
\begin{array}{ccccc}
&&I_{\rm loc}&&\\
&&\downarrow&&\\
&&I_{LR}&&\\
&\swarrow&&\searrow&\\
I_L&&&&I_R\\
&\searrow&&\swarrow&\\
&&I_G&&
\end{array}
$$

The two semi-local nodes are incomparable: one resolves the target carrier of
the perturbation and the other resolves its source carrier.

![The aligned block difference separates into left-carrier motion, additive
operator error, and right-carrier motion. Global and semi-local summaries form
an information-refinement lattice whose local node retains the marked block
quantity.](../../figures/paper25/fig1_transport_information_lattice.png)

**Theorem 3.7 (Exact Minimax Envelope at Every Information Level).** Among all
operators satisfying the budgets visible at the declared node, the best
possible universal upper bounds for $\lambda=\lVert PEQ\rVert_F$ are

$$
\begin{aligned}
U_G&=\min(\varepsilon_F,\sqrt{k}\,\varepsilon_2),\\
U_L&=\min(U_G,\ell),&U_R&=\min(U_G,r),\\
U_{LR}&=\min(U_G,\ell,r),\\
U_{\rm loc}&=\lambda.
\end{aligned}
$$

Every displayed envelope is minimax sharp. When $\dim V\ge2$ and the marked
carriers and their complements are nontrivial, every edge is strict as an
information refinement: the statistic added at the upper node is not
determined by the lower node. The nodes $I_L$ and $I_R$ are incomparable, and
even $I_{LR}$ does not determine $\lambda$. This information-theoretic
strictness does not assert a strict pointwise inequality between the two
envelope values for every numerical budget tuple.

**Proof.** Compression gives

$$
\lambda\le\lVert E\rVert_F,
\qquad
\lambda\le\lVert PE\rVert_F,
\qquad
\lambda\le\lVert EQ\rVert_F.
$$

The block $PEQ$ has rank at most $k$, so

$$
\lambda\le\sqrt{k}\,\lVert PEQ\rVert_2
\le\sqrt{k}\,\lVert E\rVert_2.
$$

Taking the minimum of the inequalities available at each node proves the
upper bounds. For sharpness, let $m$ be the displayed minimum and choose
orthonormal vectors $p_1,\ldots,p_k$ in $\operatorname{ran}P$ and
$q_1,\ldots,q_k$ in $\operatorname{ran}Q$.
Then

$$
E=\frac{m}{\sqrt{k}}\sum_{t=1}^k
\lvert p_t\rangle\langle q_t\rvert
$$

has $\lVert E\rVert_F=\lambda=m$, $\lVert E\rVert_2=m/\sqrt{k}$, and both
semi-local norms equal to $m$. It therefore satisfies every visible upper budget and attains the
corresponding envelope.

For strictness, choose unit vectors
$p_1\in\operatorname{ran}P$, $p_0\in\ker P$,
$q_1\in\operatorname{ran}Q$, and $q_0\in\ker Q$. The rank-one operators

$$
E_{11}=\lvert p_1\rangle\langle q_1\rvert,
\qquad E_{10}=\lvert p_1\rangle\langle q_0\rvert,
\qquad E_{01}=\lvert p_0\rangle\langle q_1\rvert
$$

all have global operator and Frobenius norms one, while their left and right
semi-local norms distinguish the two directions independently. Finally, put

$$
E_{\rm diag}=E_{11}+\lvert p_0\rangle\langle q_0\rvert,
\qquad
E_{\rm cross}=E_{10}+E_{01}.
$$

These two operators have the same exact statistics

$$
\lVert E\rVert_2=1,
\qquad \lVert E\rVert_F=\sqrt2,
\qquad \lVert PE\rVert_F=\lVert EQ\rVert_F=1,
$$

but their local block norms are respectively $1$ and $0$. Hence every claimed
strictness and incomparability already occurs inside the declared nontrivial
carrier and complement directions. In particular, the two
semi-local statistics together still do not determine $\lambda$; the local
node is a genuine strict refinement. $\square$

**Theorem 3.8 (Exact Additive Completion of Fixed Carrier Motion).** Fix
orthogonal projectors $\bar Q_i,Q'_i,\bar Q_j,Q'_j$ and a reference operator
$\bar Y_a$. Put

$$
A=Q'_i\bar Y_aQ'_j-\bar Q_i\bar Y_a\bar Q_j
$$

and let

$$
\mathcal S'_{ij}=\{Q'_iXQ'_j:X\in\operatorname{End}(V)\}.
$$

Write the Hilbert--Schmidt orthogonal decomposition

$$
A_\parallel=Q'_iAQ'_j,
\qquad
A_\perp=A-A_\parallel.
$$

Then, for every $\varepsilon\ge0$, the exact worst-case block error over additive
perturbations with $\lVert E_a\rVert_F\le\varepsilon$ is

$$
\sup_{\lVert E_a\rVert_F\le\varepsilon}
\bigl\lVert Q'_i(\bar Y_a+E_a)Q'_j
-\bar Q_i\bar Y_a\bar Q_j\bigr\rVert_F
=\sqrt{\lVert A_\perp\rVert_F^2
+(\lVert A_\parallel\rVert_F+\varepsilon)^2}.
$$

Thus the additive budget combines linearly only with the component of the
carrier-motion error already lying in the final block space. It combines
orthogonally with the remaining component.

**Proof.** The map

$$
\Pi'_{ij}(X)=Q'_iXQ'_j
$$

is the Hilbert--Schmidt orthogonal projector onto $\mathcal S'_{ij}$. Moreover,
the set of compressed additive errors with $\lVert E_a\rVert_F\le\varepsilon$
is exactly the closed Frobenius ball of radius $\varepsilon$ in
$\mathcal S'_{ij}$: compression cannot increase the norm, while every
$C\in\mathcal S'_{ij}$ is realized by taking $E_a=C$. Therefore, for
$C=Q'_iE_aQ'_j$, orthogonality gives

$$
\lVert A+C\rVert_F^2
=\lVert A_\perp\rVert_F^2+\lVert A_\parallel+C\rVert_F^2.
$$

The second term is maximized by choosing $C$ parallel to $A_\parallel$; if that
component vanishes, any $C\in\mathcal S'_{ij}$ of norm $\varepsilon$ attains the
same value. This proves the formula. $\square$

**Corollary 3.9 (Explicit Three-Axis Strictness).** The three-term localized
sum and the scalar global sum are not, in general, the exact joint optimum for
a fixed carrier geometry. Let $e_1,e_2,e_3,e_4$ be orthonormal, choose
$c,s\in(0,1)$ with $c^2+s^2=1$, and set

$$
\begin{aligned}
\bar Q_i&=\lvert e_1\rangle\langle e_1\rvert,
&Q'_i&=\lvert u\rangle\langle u\rvert,
&u&=ce_1+se_3,\\
\bar Q_j&=\lvert e_2\rangle\langle e_2\rvert,
&Q'_j&=\lvert v\rangle\langle v\rvert,
&v&=ce_2+se_4,\\
\bar Y_a&=\lvert e_1\rangle\langle e_2\rvert.
\end{aligned}
$$

Complete both pairs to orthogonal sectorizations using their orthogonal
rotated complements. Then

$$
\lVert\Delta_i\rVert_F=\lVert\Delta_j\rVert_F=\sqrt2\,s,
\qquad
\lVert\bar Y_a\rVert_2=1.
$$

For the carrier-motion error $A$ of Theorem 3.8,

$$
A_\parallel=0,
\qquad
\lVert A\rVert_F^2=1-c^4=s^2(1+c^2).
$$

Hence, with any $\varepsilon>0$, all three perturbation axes are nonzero and the
true additive worst case is

$$
\sqrt{s^2(1+c^2)+\varepsilon^2}.
$$

By contrast, the three-term localized and global bounds are respectively

$$
b_{\rm loc}=cs+s+\varepsilon,
\qquad
b_{\rm glob}=2\sqrt2\,s+\varepsilon.
$$

Both inequalities are strict. In particular, the sum in Theorem 3.1 is a
portable certificate, not a claim of joint minimax optimality.

**Proof.** Direct multiplication gives
$Q'_i\bar Y_aQ'_j=c^2\lvert u\rangle\langle v\rvert$. Its projection against
the final block space cancels the projection of
$\lvert e_1\rangle\langle e_2\rvert$, so $A_\parallel=0$. The two rank-one
operators have Hilbert--Schmidt inner product $c^2$, giving

$$
\lVert A\rVert_F^2=c^4+1-2c^4=1-c^4.
$$

Theorem 3.8 gives the exact supremum. The first and third localized terms have
norms $cs$ and $s$, and the additive term can have norm $\varepsilon$. Finally,
$\sqrt{x^2+y^2}<x+y$ for positive $x,y$, while
$\sqrt{1+c^2}<1+c<2\sqrt2$. This proves both strict comparisons. $\square$

**Theorem 3.10 (Equality Criterion for the Localized Bound).** Write the three
terms in Theorem 3.1 as

$$
T_L=\Delta_i\bar Y_aQ'_j,
\qquad
T_E=Q'_iE_aQ'_j,
\qquad
T_R=\bar Q_i\bar Y_a\Delta_j.
$$

Then

$$
\lVert D_a(i,j)\rVert_F=b_{\rm loc}(a;i,j)
$$

if and only if there are a matrix $H$ with $\lVert H\rVert_F=1$ and nonnegative
real numbers $\alpha_L,\alpha_E,\alpha_R$ such that

$$
T_L=\alpha_LH,
\qquad T_E=\alpha_EH,
\qquad T_R=\alpha_RH.
$$

Zero terms correspond to zero coefficients. Equivalently, every two nonzero
terms have Hilbert--Schmidt inner product equal to the product of their norms,
with positive real phase.

For differences of orthogonal projectors, this condition forces

$$
\alpha_L\alpha_E\alpha_R=0.
$$

Thus all three localized terms can never be simultaneously nonzero at an
equality point. Equality is possible with one active term, or with two active
terms that lie on the same nonnegative ray.

**Proof.** The Frobenius norm is the Hilbert-space norm associated with the
Hilbert--Schmidt inner product. Equality in its finite triangle inequality
holds exactly when all nonzero summands lie on one nonnegative ray. This proves
the first equivalence.

It remains to use projector geometry. Suppose all three coefficients were
positive. Because $T_E=Q'_iT_EQ'_j$, the range of $H$ lies in
$\operatorname{ran}Q'_i$. Because $T_R=\bar Q_iT_R$, it also lies in
$\operatorname{ran}\bar Q_i$. Hence

$$
\operatorname{ran}H
\subseteq\operatorname{ran}Q'_i\cap\operatorname{ran}\bar Q_i.
$$

The self-adjoint difference $\Delta_i=Q'_i-\bar Q_i$ annihilates this
intersection. Consequently its range is orthogonal to the intersection:

$$
\langle h,\Delta_i x\rangle=\langle\Delta_i h,x\rangle=0
$$

for every $h$ in the intersection. But the range of $T_L$ lies in the range of
$\Delta_i$, while $T_L=\alpha_LH$ would put the same nonzero range inside the
intersection, a contradiction. Therefore at least one coefficient is zero.
The converse follows immediately from the common-ray condition. $\square$

**Remark 3.11 (When the global bound is also attained).** Equality
$\lVert D_a(i,j)\rVert_F=b_{\rm loc}=b_{\rm glob}$ additionally requires equality in every active
submultiplicative estimate used in Theorem 3.1, and requires every declared
upper budget appearing in $b_{\rm glob}$ to be saturated:

$$
\begin{aligned}
\lVert\Delta_i\bar Y_aQ'_j\rVert_F
&=\lVert\Delta_i\rVert_F\lVert Y_a\rVert_2,\\
\lVert Q'_iE_aQ'_j\rVert_F&=\lVert E_a\rVert_F,\\
\lVert\bar Q_i\bar Y_a\Delta_j\rVert_F
&=\lVert Y_a\rVert_2\lVert\Delta_j\rVert_F,
\end{aligned}
$$

together with the common-ray criterion above. Theorem 3.10 shows that the
three displayed equalities cannot all contribute positively to one joint
equality point.

## Margin consequences

**Corollary 4.1 (Typed activity margin).** Let

$$
n=\lVert\bar Q_i\bar Y_a\bar Q_j\rVert_F,
\qquad
n'=\lVert Q'_iY'_aQ'_j\rVert_F,
$$

and let $b$ be either valid bound from Theorem 3.1. Then

$$
\lvert n'-n\rvert\le b.
$$

For a declared threshold $\tau\ge0$:

$$
\begin{array}{rcll}
n-b>\tau&\Longrightarrow&n'>\tau
& (\mathsf{STABLE\_ACTIVE}),\\
n+b\le\tau&\Longrightarrow&n'\le\tau
& (\mathsf{STABLE\_INACTIVE}),\\
\text{otherwise}&&&(\mathsf{UNRESOLVED}).
\end{array}
$$

$\mathsf{UNRESOLVED}$ is a proof-status outcome. It is not evidence that the perturbed
block is zero, nonzero, active, or inactive.

**Theorem 4.2 (Completeness of the Unresolved Interval).** For $n,b,\tau\ge0$,
let the only available scalar error information be

$$
n'\ge0,
\qquad
\lvert n'-n\rvert\le b.
$$

Then the margin policy of Corollary 4.1 returns $\mathsf{UNRESOLVED}$ if and only if the
admissible interval contains both an inactive value and an active value:

$$
\begin{aligned}
&\exists x_-:\quad \lvert x_--n\rvert\le b,\quad x_-\le\tau,\\
&\exists x_+:\quad \lvert x_+-n\rvert\le b,\quad x_+>\tau.
\end{aligned}
$$

Both alternatives are realized by finite-dimensional operator-only
perturbations with fixed coordinate projectors. Hence no sound classifier
using only $n$, $b$, and $\tau$ can refine $\mathsf{UNRESOLVED}$ to either stable status.

**Proof.** The policy is unresolved exactly when

$$
n-b\le\tau<n+b.
$$

In that case $x_-=\max(0,n-b)$ is admissible and inactive, while any
$x_+$ strictly between $\tau$ and $n+b$, for example their midpoint, is
admissible and active. Conversely, the existence of an admissible inactive
value rules out $n-b>\tau$, and the existence of an admissible active value
rules out $n+b\le\tau$.

For realization, use fixed projectors onto $\mathbb C e_1$ and $\mathbb C e_2$,
take $\bar Y_a=n\lvert e_1\rangle\langle e_2\rvert$, and set
$Y'_a=x\lvert e_1\rangle\langle e_2\rvert$. Then
$E_a=(x-n)\lvert e_1\rangle\langle e_2\rvert$ has Frobenius norm at most $b$
and the perturbed block norm is exactly $x$. Applying this once with $x=x_-$
and once with $x=x_+$ gives the two hostile realizations. $\square$

**Corollary 4.3 (Finite aggregate margin).** For a finite coordinate family
$K$, suppose $\lvert n'_k-n_k\rvert\le b_k$ for every $k\in K$. Then

$$
\max_{k\in K}\max(0,n_k-b_k)
\le\max_{k\in K}n'_k
\le\max_{k\in K}(n_k+b_k).
$$

The same threshold trichotomy therefore applies to an aggregate coordinate
using these lower and upper bounds. Section 6.2 applies this aggregate policy
to the Rubik observation; the Markov example in Section 6.3 remains a
coordinatewise semantic lift.

## Two-state Markov probability lift

The following is an application with additional structure, not a conclusion
about arbitrary Markov systems.

**Corollary 5.1 (Singleton Markov Lift).** Let

$$
P=\begin{pmatrix}1-a&a\\ \kappa&1-\kappa\end{pmatrix}
$$

be row-stochastic with $a,\kappa>0$, and let $Q_0,Q_1$ be the coordinate singleton
projectors. Under the convention $P[\mathrm{source},\mathrm{target}]$,

$$
\lVert Q_0PQ_1\rVert_F=a,
\qquad
\lVert Q_1PQ_0\rVert_F=\kappa.
$$

Suppose a perturbation preserves this two-state form and the reverse
probability $\kappa$, while Theorem 3.1 gives

$$
a'\in[\ell,u],
\qquad
\ell=\max(0,a-\beta),
\qquad
u=\min(1,a+\beta).
$$

If $\ell>0$, then throughout the admitted interval:

$$
\begin{aligned}
&\text{the positive edge }0\to1\text{ persists},\\
&\Pr_0(T_1<\infty)=1,\\
&\mathbb E_0[T_1]\in[1/u,1/\ell],\\
&\pi_1\in\left[\frac{\ell}{\ell+\kappa},\frac{u}{u+\kappa}\right],\\
&\operatorname{sep}_1=\lvert1-\lambda_2\rvert
\in[\kappa+\ell,\kappa+u].
\end{aligned}
$$

**Proof.** The coordinate block is $a e_0e_1^\ast$, whose Frobenius norm is $a$
because $a\ge0$. For $a'>0$, the first transition from state $0$ to state $1$
has a geometric waiting time with parameter $a'$, hence eventual hit
probability one and expectation $1/a'$. Solving $\pi P=\pi$ gives
$\pi_1=a'/(a'+\kappa)$. The eigenvalues are $1$ and $\lambda_2=1-a'-\kappa$, so the
separation from the stationary eigenvalue is $\lvert1-\lambda_2\rvert=a'+\kappa$. All
displayed functions are monotone on the admitted interval, yielding the
endpoint bounds. $\square$

If $\ell=0$, the block theorem alone does not certify edge persistence,
almost-sure hitting, or a finite upper hitting-time bound. A localized bound
may make $\ell$ positive when the global bound does not, as in the two-state
control registered in Section 6.3.

**Boundary 5.2 (Partition and threshold discipline).** Corollary 5.1 is not
available after continuously rotating the coordinate projectors: the result
is still an orthogonal Hilbert frame but no longer a set-valued partition of
the Markov states. Extension 3.1a remains algebraically and metrically valid
for a bounded oblique carrier resolution, but such a resolution is even
further from a state partition and therefore does not restore the Markov
probability interpretation. Also, for any positive threshold $\tau$,

$$
0<a\le\tau
$$

is a positive Markov edge that remains inactive under the block-strength
policy. Positive support and thresholded block activity are different types.

### Supplementary Technical Note S1

The separately packaged note proves one nontrivial proportional-row
preservation contract for finite chains: expected
hitting time decreases and stationary target mass increases as the direct
target probability grows, while the absolute spectral gap need not be
monotone. The classification of general preservation contracts remains open.

## Exact Controls and Bounded Realizations

The manuscript proofs are theorem authority. The computational records are
registered in two distinct layers. The exact layer uses integer and
\texttt{Fraction} arithmetic and literal exact-zero semantics. The bounded
layer uses the frozen Python/NumPy float64/complex128 protocols stated below;
its records are observations for declared fixtures, not proofs of the general
theorems.

### Exact rational controls

The exact certificate records one-axis equality witnesses for all three
global constants, the fixed-global-data localization family of Theorem 3.4,
the carrier-information lattice and its strict hostile pairs, an exact
three-axis witness for Corollary 3.9, a localized-bound equality witness, and
two-sided realizations of the unresolved interval. All matrix entries are
rational, and the registry records the integer/Fraction backend, norm protocol,
threshold policy, and exact-zero policy. It is a finite certificate for the
declared fixtures, not a second proof of the general theorems.

The frozen exact protocol uses Python $3.13.0$, Python integers and
\texttt{fractions.Fraction}, exact Frobenius norms through squared entries, and
exact witness identities for the operator-norm fields. Its threshold fixture
uses $n=b=\tau=1$, with
$\mathsf{UNRESOLVED}$ defined by $n-b\le\tau<n+b$. Zero means literal rational
equality to $0$; no numerical tolerance or near-zero substitution is admitted.

### Rubik simultaneous-transport hostile control

The Rubik control uses the canonical $228$-dimensional cubie carrier, all $18$
labelled generators, and $9\times9$ ordered sector coordinates. It tests
simultaneous transport of operators and labelled carriers against the hostile
fixed-frame control. It does not serve as a general perturbation distribution
or Markov example. The frozen bounded protocol uses Python $3.13.0$, NumPy
$2.1.3$, SciPy $1.18.0$, complex128/float64 arithmetic, Frobenius block norms, spectral
operator norms, Frobenius projector deltas, support thresholds $10^{-10}$,
$10^{-6}$, and $0.05$, activity threshold $0.05$, transport residual tolerance
$10^{-10}$, and perturbation comparison tolerance $2\times10^{-10}$. A
localized/global ratio at most the latter tolerance is reported as zero; a
threshold-inactive coordinate is not thereby an exact-zero certificate. The
generic near-zero control uses a separately declared error radius $10^{-9}$.

At the largest declared perturbation level, $\varepsilon=\eta=0.05$, the
following table reports the coordinatewise ratio $b_{\rm loc}/b_{\rm glob}$
only where $b_{\rm glob}>0$. The two bound maxima are separate maxima over all
coordinates; their quotient is not used as a coordinatewise statistic.

| axis | positive-global coordinates | zero ratio | median ratio | mean ratio | maximum ratio |
|---|---:|---:|---:|---:|---:|
| operator | $1458$ | $1440$ | $0$ | $0.01235$ | $1.00000$ |
| sector | $576$ | $408$ | $<10^{-15}$ | $0.11972$ | $0.70711$ |
| coupled | $1458$ | $1290$ | $0$ | $0.03553$ | $0.77006$ |

The corresponding bound maxima and aggregate margin transitions are:

| axis | $\max b_{\rm glob}$ | $\max b_{\rm loc}$ | aggregate unresolved, global $\to$ local |
|---|---:|---:|---:|
| operator | $0.05000$ | $0.05000$ | $24\to1$ |
| sector | $0.14136$ | $0.09996$ | $13\to1$ |
| coupled | $0.19490$ | $0.15008$ | $24\to1$ |

Thus the localized theorem is not merely a modest improvement of the largest
global scalar. In the operator-only control, only the $18$ coordinates hit by
the rank-one generator errors retain ratio one; $1440$ other coordinates have
the same positive global budget but localized bound reported as zero under the
frozen comparison tolerance. On the coupled
axis every coordinate is strictly improved, and the aggregate unresolved
census drops from $24$ to $1$. These are bounded float64 observations for the
declared carrier and perturbation family, not universal distribution laws.

### Markov portability and cross-layer example

The Markov record is deliberately narrower. It uses the two-state singleton
partition to illustrate how a certified block interval lifts to positive-edge,
hitting-time, stationary-mass, and eigenvalue-separation statements under the
additional hypotheses of Corollary 5.1. Rotated Hilbert frames appear only as
a cross-layer boundary: they are not state partitions, so no Markov probability
conclusion is admitted. The frozen bounded protocol uses Python $3.13.0$,
NumPy $2.1.3$, float64/complex128 arithmetic, block-activity threshold $0.15$,
positive-support threshold $10^{-12}$, and comparison tolerance
$2\times10^{-12}$. Positive support and thresholded block activity remain
distinct policies; $\mathsf{UNRESOLVED}$ is not an exact-zero status.

## Claim Status and Boundary

The theorem and evidence levels are:

| Surface | Claim level | Registered control |
|---|---|---|
| Theorem 2.1, Corollary 2.2, and Boundary 2.3 | Theorem/boundary | exact integer/Fraction transport fixture and Rubik simultaneous-transport hostile control |
| Theorem 3.1 and Extension 3.1a | Theorem | Rubik orthogonal-specialization observation; Extension 3.1a is proof-only |
| Theorems 3.3--3.4 | Theorem | exact rational sharpness and separation controls |
| Definition 3.6 and Theorem 3.7 | Theorem | exact rational lattice grid and hostile pairs |
| Theorem 3.8 and Corollary 3.9 | Theorem | exact rational conditional-minimax and three-axis controls |
| Theorem 3.10 | Theorem | exact rational equality witness |
| Corollary 4.1, Theorem 4.2, and Corollary 4.3 | Theorem | exact two-sided hostile realizations and bounded Rubik aggregate sweep |
| Corollary 5.1 | Theorem under its stated two-state hypotheses | bounded Markov portability example |

Supplementary Technical Note S1 has its own theorem/boundary ledger and local
validator under `experiments/paper25/notes/`. It is part of the Paper XXV
release package but not part of the main theorem numbering above.

No claim is made that aggregate block profiles reconstruct the labelled
operator family or its representation; that global norms determine carrier
localization; that thresholded activity equals exact support; that an
orthogonal Hilbert frame or oblique carrier resolution is a set-valued state
partition; or that a one-block perturbation estimate controls arbitrary-depth
routed composition. Theorem 3.8 is conditional on fixed carrier geometry and
does not determine the joint minimax envelope from
$\delta_i,\delta_j,\varepsilon_{a,F},\lVert Y_a\rVert_2$ alone across all
sectorizations. The Rubik table is a bounded float64 observation for one
declared carrier and perturbation family, not a universal distribution law;
the Markov observation is confined to the stated two-state model.

## Conclusion

Aligned unitary transport preserves the complete typed block profile because
the represented operators and marked carriers move together. After alignment,
the change of one generator-resolved block separates exactly into left-carrier
motion, additive operator error, and right-carrier motion. The resulting
localized bound retains information that every portable global norm budget
forgets.

These results make that information loss quantitative. The global coefficients
are sharp one axis at a time. In the fixed-projector additive-error submodel,
global norms cannot detect localization and the global/semi-local/local
information lattice has an exact minimax envelope at every node. For fixed
carrier motion, additive error admits an exact
conditional completion, while the localized triangle bound has a complete
equality criterion. The threshold interval left unresolved by a certified
radius is complete: the admitted information genuinely permits realizations
on both sides of the threshold.

The algebra extends beyond orthogonal sectors to bounded oblique carrier
resolutions, with explicit conditioning factors. Application semantics do not
extend automatically. In particular, the two-state Markov lift requires a
genuine singleton state partition, and the one-block theorem does not replace
the image--kernel or survivor tests needed for routed composition.

Supplementary Technical Note S1 supplies one positive n-state preservation
contract for hitting time and stationary mass together with a negative
absolute-gap boundary. It does not close the broader classification problem.

## Open Problems

The established boundary leaves the following questions open:

1. **Joint oblique minimax geometry.** Determine the exact information lattice
   and minimax envelopes when both carrier resolutions are oblique and only
   projector-condition and operator-norm budgets are declared.
2. **Incidence-locus stability.** Relate principal angles, small singular
   values, and carrier perturbations to quantitative distance from
   $\{(A,B):AB=0\}$ without identifying near incidence with exact route failure.
3. **Productwise propagation.** Establish conditions under which one-block
   bounds compose along a finite routed product or Paper XX survivor recursion
   without exponential loss.
4. **Semantic lifts.** Supplementary Technical Note S1 establishes one
   proportional-row contract for hitting time and stationary mass. Classify
   broader preservation contracts under which block intervals imply
   probability, mixing, or channel statements for finite Markov partitions
   and open quantum channels.

## Appendix A: Computational Artifacts {.unnumbered}

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite) under
\path{experiments/paper25/}; short paths below are relative to that directory.

| Surface | Role | Short path |
|---|---|---|
| diagnostic sources | transport, localized perturbation, and two-state Markov controls | \path{*.py} |
| retained evidence | exact certificates, bounded observations, and receipts | \path{results/} |
| validators | exact replay, producer replay, claim alignment, and release closure | \path{validation/} |
| evidence metadata | claim/evidence alignment and exact release inventory | \path{claim-surface-map.json}; \path{release-manifest.json} |
| Supplement S1 | proportional-row Markov theorems, hostile matrices, and bounded audit | \path{notes/proportional_markov_semantic_lift/} |
| partial Lean surface | typed transport and scalar-margin declarations | \path{lean/} |

The exact and bounded-observation receipts have separate scopes and neither
occurs in its own transitive closure. They record local closure verification,
not independent validation or proof of the manuscript theorems. Reproduction
commands and exact artifact paths are maintained in the experiment README and
release manifest.
