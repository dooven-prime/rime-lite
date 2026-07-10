# Generic Accessibility Completion

### Incidence Varieties, Rank-Protected Bridges, and the Generic Completion Principle

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part VII of the RIME program. Paper IV gives the collision
geometry, Paper V gives the local repair calculus, and Paper VI gives the
deformation geometry of accessibility walls. Paper VII isolates the generic
completion boundary: outside high-codimension incidence, rank-protected bridge
products are expected to survive, giving the conjectural route from
$(R_1,R_2)$ to the first-depth invariant $D$.*

***

## Abstract

**Problem.** Why is accessibility generically stable? Paper V identifies local
length-two obstruction mechanisms, and Paper VI places the corresponding
accessibility data over a deformation base. The remaining static question is
the completion problem: when does the accessibility jet

$$
\mathcal J_{\mathrm{acc}}
=
(J_{\mathrm{block}},J_{\mathrm{comm}},J_{\mathrm{depth}})
$$

determine the accessibility depth matrix $D$?

**Approach.** The paper combines three blocks. Paper V supplies the local
mechanism taxonomy. Paper VI supplies the wall hierarchy

$$
\widehat{\Sigma}_{R_1}
\subseteq
\widehat{\Sigma}_{R_2}
\subseteq
\widehat{\Sigma}_D
=
\Sigma_{\mathrm{access}}
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}
$$

and interprets $R_1,R_2,D$ as discrete shadows of
$\mathcal J_{\mathrm{acc}}$. The new input developed here identifies Type IV
incidence as a high-codimension algebraic degeneration:

$$
I=\{(A,B):AB=0,\ A\ne0,\ B\ne0\}.
$$

For $A\in\mathbb C^{m\times n}$, $B\in\mathbb C^{n\times p}$, and
$\operatorname{rank}A=r$, the fixed-rank incidence stratum has

$$
\operatorname{codim} I_r=(m-r)(n-r)+pr.
$$

For square $d\times d$ blocks, the dominant incidence component has
$r\approx d/2$ and codimension asymptotic to $3d^2/4$, or about $37.5\%$ of
the ambient dimension $2d^2$.

**Results.** The theorem-level result is the codimension calculation for the
Type IV incidence variety. The completion statement is formulated as a
conjectural theorem program:

> **Conjecture 1 (Completion Away from Incidence).** Under the stated richness
> and nondegeneracy assumptions, on the generic non-incidence locus where all
> bridge products avoid $AB=0$, the accessibility jet
> $\mathcal J_{\mathrm{acc}}$ has a locally constant discrete shadow, and that
> shadow determines the accessibility depth matrix $D$.

Computational support is consistent with this program. Synthetic Type III
systems lie inside the candidate completeness class; synthetic Type IV systems
lie outside it; perturbation at $\varepsilon=10^{-6}$ destroys Type IV in
$100/100$ trials for the tested incidence models; $0/400000$ random matrix
pairs satisfy $AB=0$ with $A,B\ne0$; and exact-hash audits on $80$ diverse
random systems found zero disagreements among systems with identical
$(R_1,R_2)$. A claim-status-metadata bridge audit further separates
the generic and structured regimes: five fixed-seed random systems give
$1080/1080$ safe bridge products and zero incidence candidates, while the Rubik
system has $528$ bridge-level incidence candidates concentrated in a small
family of sector triples. An exploratory ablation over dimension, rank-deficient fraction, and
generator count found zero incidence candidates across $75$ random runs and
$23400$ audited bridge products.

**Implications.** Paper V identifies local exceptional mechanisms. Paper VI
places those mechanisms on the generator-set moduli space. Paper VII explains
why the hardest mechanism, Type IV incidence, is nongeneric: it lies on a
high-codimension algebraic variety. The resulting principle is conditional but
sharp: away from incidence and under richness/nondegeneracy hypotheses, the
accessibility jet is expected to complete the first-depth calculation. Rubik
is therefore not a random-generic system; it is a stable carrier of
high-codimension algebraic structure.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $V$ | finite-dimensional complex Hilbert space |
| $\mathcal S=(V,\{Q_i\},\mathcal X)$ | sectorized observable framework |
| $Q_i$ | orthogonal sector projector, $\sum_iQ_i=I$ |
| $X_g$ | skew-Hermitian generator |
| $B^g_{ij}=Q_iX_gQ_j$ | projected generator block |
| $R_1(i,j;g)$ | generator support: $1$ iff $B^g_{ij}\ne0$ |
| $R_2(i,j;g,h)$ | projected commutator survival: $1$ iff $Q_i[X_g,X_h]Q_j\ne0$ |
| $D(i,j)$ | minimal Lie depth connecting sector $j$ to sector $i$ |
| $\mathcal J_{\mathrm{acc}}$ | accessibility jet $(J_{\mathrm{block}},J_{\mathrm{comm}},J_{\mathrm{depth}})$ |
| $\Sigma_{\mathrm{comm}}$ | outer commutativity locus $\{w:[Q_T(w),H_T(w)]=0\}$ |
| $\Sigma_{\mathrm{spec}}$ | normal spectral chart inside $\Sigma_{\mathrm{comm}}$ where joint projectors and accessibility fields are used |
| $\Sigma_{\mathrm{IV}}$ | Type IV incidence locus |
| $C$ | candidate generic completeness class, excluding Type IV incidence |

Depth convention: depth $0$ means a direct generator block, depth $1$ means a
projected commutator block, depth $2$ means a nested commutator, and
$D(i,j)=\infty$ means frozen in the tested Lie filtration.

***

## Completion Problem

Why is accessibility generically stable? The answer proposed here is that the
hard local obstruction, Type IV incidence, is a high-codimension algebraic
condition. Away from this incidence locus, rank-protected bridge products
survive in the generic matrix model, so the accessibility jet is expected to
complete the first-depth calculation under the stated richness hypotheses.

Paper V established the local accessibility calculus for a fixed sectorized
observable framework

$$
(V,\{Q_i\},\{X_g\}).
$$

The first layer $R_1$ records which generator blocks are nonzero. The second
layer $R_2$ records which projected commutators survive. Paper V showed that
$R_1$ is not enough: binary support sees possible paths, but it does not see
whether projected matrix products cancel.

Paper VI then moved the same observables over normal spectral charts
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$. There, $R_1(w)$,
$R_2(w)$, and $D(w)$ are discrete rank/support shadows of smooth matrix
fields. The accessibility wall hierarchy records where these shadows fail to
continue locally.

The remaining question is whether the accessibility jet determines $D$.

Equivalently, when is the data visible through $R_1$, $R_2$, and the
Hall-propagation component of $\mathcal J_{\mathrm{acc}}$ complete for the
first-depth matrix?

This paper does not claim an unconditional theorem that $(R_1,R_2)$ determines
$D$. That statement is false without hypotheses. Instead, it isolates the
generic obstruction boundary and formulates the completion theorem on the
non-incidence locus.

![Paper VII overview. The Generic Completion Principle predicts completion
away from high-codimension incidence, supported by rank-protected bridge
survival. Rubik sits in a structured exceptional region that is described by
incidence geometry and connected back to the deformation theory of Paper VI.](../../figures/paper7/fig1_generic_completion_overview.png)

***

## Local Mechanisms

Paper V gives a length-two mechanism taxonomy. For sector pair $(i,j)$ and
generators $g,h$, expand

$$
Q_i[X_g,X_h]Q_j
=
\sum_k
\left(
Q_iX_gQ_kX_hQ_j
-
Q_iX_hQ_kX_gQ_j
\right).
$$

The local mechanisms are:

| Type | Mechanism | Status |
|------|-----------|--------|
| Type I | singleton-color degeneracy | no depth-one repair |
| Type II | projected commutator survives | repaired at $R_2$ |
| Type III | signed cancellation among nonzero products | exceptional but soft |
| Type IV | termwise vanishing by image-kernel incidence | exceptional and hard |

Type III is a relation among products that exist. Type IV is different: the
candidate products vanish before signed cancellation can occur. For a single
bridge product this means

$$
A=Q_iX_gQ_k,\qquad B=Q_kX_hQ_j,\qquad AB=0
$$

with $A\ne0$ and $B\ne0$, equivalently

$$
\operatorname{im}B\subseteq\ker A.
$$

Thus Type IV is an incidence condition, not merely a cancellation condition.

### Definition 1 (Candidate Completeness Class)

Let $C$ denote the class of sectorized systems whose length-two
$R_2=0$ obstructions are Type I or Type III, with no Type IV incidence
obstruction.

This is a candidate generic completeness class, not a universal theorem class.
The generic completion conjecture below states that, after excluding incidence
and assuming the usual nondegeneracy/richness hypotheses, the accessibility jet
should determine $D$.

***

## Type IV Incidence Variety

The main algebraic input of Paper VII is the codimension of the Type IV
incidence condition.

### Theorem 1 (Incidence Codimension)

Let

$$
A\in\mathbb C^{m\times n},\qquad
B\in\mathbb C^{n\times p},
$$

and let

$$
I_r=\{(A,B):AB=0,\ \operatorname{rank}A=r\}.
$$

Then

$$
\dim I_r=r(m+n-r)+np-pr
$$

and the codimension of $I_r$ in the ambient space
$\mathbb C^{m\times n}\times\mathbb C^{n\times p}$ is

$$
\operatorname{codim}I_r
=
(m-r)(n-r)+pr.
$$

**Proof.** The variety of $m\times n$ matrices of rank $r$ has dimension
$r(m+n-r)$. For fixed rank-$r$ matrix $A$, the equation $AB=0$ forces the
columns of $B$ to lie in $\ker A$, whose dimension is $n-r$. Hence the fiber
over $A$ has dimension $p(n-r)=np-pr$. Adding base and fiber dimensions gives
the stated dimension. Subtracting from the ambient dimension $mn+np$ gives

$$
mn+np-\big(r(m+n-r)+np-pr\big)
=
(m-r)(n-r)+pr.
$$

This proves the formula. $\square$

### Corollary 1 (Square Blocks)

For square blocks $m=n=p=d$,

$$
\operatorname{codim} I_r=(d-r)^2+dr.
$$

For the Type IV locus, the nonzero/non-rank-protected square ranks are
$1\le r\le d-1$. The dominant component among these strata minimizes this
expression at $r\approx d/2$, so

$$
\operatorname{codim} I\sim \frac{3d^2}{4}.
$$

Since the ambient dimension is $2d^2$, the incidence locus occupies codimension
about $37.5\%$ of the ambient dimension.

For the tested dimensions:

| $d$ | ambient dimension | $\operatorname{codim} I$ | percentage |
|-----|-------------------|--------------------------|------------|
| $2$ | $8$ | $3$ | $37.5\%$ |
| $3$ | $18$ | $7$ | $38.9\%$ |
| $4$ | $32$ | $12$ | $37.5\%$ |
| $6$ | $72$ | $27$ | $37.5\%$ |
| $10$ | $200$ | $75$ | $37.5\%$ |

### Corollary 2 (Rank-Protected Type IV Exclusion)

If $A$ has full column rank, then $\ker A=0$ and $AB=0$ implies $B=0$.
Therefore Type IV cannot occur on full-column-rank block strata. Dually, if
$B$ has full row rank, then $AB=0$ implies $A=0$.

Thus Type IV is structurally impossible on rank-protected projected block
strata -- namely when $A$ has full column rank or $B$ has full row rank -- but
constructible on rank-deficient sectorized matrix systems.

![Incidence codimension growth. For square blocks, the dominant Type IV
incidence locus has codimension asymptotic to $3d^2/4$, placing it in a
high-codimension region rather than in the generic block stratum.](../../figures/paper7/fig2_incidence_codimension_growth.png)

***

## Generic Completion Roadmap

The codimension theorem turns Type IV from an unexplained obstruction into a
geometric boundary. It is a proper algebraic degeneracy in the space of bridge
products.

### Remark 1 (Generic Completion Principle)

Outside a high-codimension incidence variety, rank-protected bridge products
generically survive. Consequently, the observable pair $(R_1,R_2)$ is expected
to determine the first-depth invariant $D$.

This principle is the conceptual bridge from Paper V to Paper VII. Paper V
shows why $R_1$ alone fails and identifies Type IV as the hard local
exception. Paper VII identifies that exception as an incidence variety of
quadratic codimension growth and formulates the generic completion statement
away from it.

The resulting theorem layer separates into three steps:

$$
\text{rank protection}
\quad\Longrightarrow\quad
\text{generic nonincidence}
\quad\Longrightarrow\quad
\text{completion away from incidence}.
$$

The first two steps are algebraic consequences of the incidence calculation.
The third step is the remaining completion conjecture.

### Corollary 3 (Rank-Protected Product Survival)

Let

$$
A\in\mathbb C^{m\times n},
\qquad
B\in\mathbb C^{n\times p}.
$$

If $A$ has full column rank and $B\ne0$, then $AB\ne0$. Dually, if $B$ has
full row rank and $A\ne0$, then $AB\ne0$.

**Proof.** If $A$ has full column rank, then $\ker A=0$. Hence $AB=0$ forces
every column of $B$ to lie in $\ker A$, so $B=0$. The dual statement follows
from applying the same argument to adjoints. $\square$

### Proposition 1 (Generic Nonincidence)

Fix block dimensions $(m,n,p)$. The Type IV bridge-failure locus

$$
I=\{(A,B):AB=0,\ A\ne0,\ B\ne0\}
\subset
\mathbb C^{m\times n}\times\mathbb C^{n\times p}
$$

is contained in a finite union of proper algebraic strata. On the stratum
$\operatorname{rank}A=r$, its codimension is

$$
\operatorname{codim} I_r=(m-r)(n-r)+pr.
$$

In particular, for square block scale $m=n=p=d$, the dominant incidence
codimension grows quadratically, asymptotic to $3d^2/4$.

**Proof.** This is Theorem 1 applied over all admissible ranks. In the square
case used for the asymptotic, the Type IV strata have
$1\le r\le d-1$, excluding $r=0$ and the rank-protected case $r=d$. In a
general rectangular system, full row rank of $A$ is not by itself
rank-protecting when $m<n$; nonzero $B$ may still land in $\ker A$. The
rank-protected exclusions are exactly those in Corollary 2. The square-block
asymptotic is Corollary 1. $\square$

### Conjecture 1 (Completion Away from Incidence)

Let $(V,\{Q_i\},\{X_g\})$ be a sectorized observable framework satisfying the usual
nondegeneracy and commutant-richness hypotheses needed to repair Type I and
Type III obstructions. Assume further that every relevant bridge product avoids
the Type IV incidence variety:

$$
Q_iX_gQ_kX_hQ_j\ne0
$$

whenever the two factors are nonzero and the product is required as a bridge
candidate.

Then the accessibility jet $\mathcal J_{\mathrm{acc}}$ determines the
accessibility depth matrix $D$. Equivalently, under these richness and
nondegeneracy hypotheses, on the generic non-incidence locus the discrete
shadow of $\mathcal J_{\mathrm{acc}}$ is complete for first-depth
accessibility.

Equivalently, under these hypotheses, the observable pair $(R_1,R_2)$ together
with the first-depth shadow of $\mathcal J_{\mathrm{acc}}$ determines $D$.

### Interpretation

The conjecture separates the fate of exceptional mechanisms. Type III
cancellation is a soft exceptional locus, repairable by higher-depth fields.
Type IV incidence is a hard exceptional locus, but it has high codimension and
measure zero in the ambient Lebesgue, equivalently Zariski-generic, matrix-pair
space.

Thus generic completion does not say that exceptions do not exist. It says that
the only hard local obstruction is algebraically nongeneric.

***

## Relation to Paper VI

Paper VI studies moving sectorized systems on normal spectral charts
$\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}$. The accessibility jet
varies as a smooth matrix-field object, while $R_1$, $R_2$, and $D$ are
discrete projections of it. The accessibility wall hierarchy is

$$
\widehat{\Sigma}_{R_1}
\subseteq
\widehat{\Sigma}_{R_2}
\subseteq
\widehat{\Sigma}_D
=
\Sigma_{\mathrm{access}}
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}.
$$

Paper VII refines the residual $R_2/D$ boundary by identifying the Type IV
component:

$$
\Sigma_{\mathrm{IV}}
\subseteq
\Sigma_{R_2}^{\circ}\cup\Sigma_D^{\circ}.
$$

Type III and Type IV are not Paper VI wall-hierarchy labels, and they should
not be read as wall classification labels. They are local mechanisms that can occur inside
the static fibers over those walls. Paper VI
answers where the observables jump in moduli space; Paper VII asks when the
accessibility jet has enough information to complete the depth calculation in
one fixed sectorized system.

This gives the closing line: Paper V says that exceptional mechanisms exist;
Paper VI says that exceptional mechanisms move on the moduli space; Paper VII
says that, generically, exceptional mechanisms either repair or disappear.

***

## Computational Proposition

The computational support for the completion theory is concentrated in three
Paper VII support scripts, abbreviated below by role:

| Label | Role |
|-------|------|
| VII-A atlas | Type III/IV synthetic systems, represented-atlas limitation, exact $(R_1,R_2)\to D$ hash audit |
| VII-B codimension | incidence codimension table, random-pair check, perturbation instability |
| VII-C bridge audit | bridge-level rank-protection and nonincidence audit for Rubik, synthetic, and random systems |

The corresponding repository scripts are `atlas_r2_boundary.py`,
`incidence_variety_codim.py`, and `rank_protected_bridge_audit.py` in
`experiments/paper7/`.

The stable support table is organized by claim-status metadata:

| Claim supported | Source | Observed result | Status |
|-----------------|--------|-----------------|--------|
| Rank-protected bridge survival | VII-C | Corollary 3 checked for constructed rank-protected blocks in dimensions $2,3,4$; no violation | theorem-support gate |
| Type IV incidence has high codimension | VII-B | square-block codimension is asymptotic to $3d^2/4$; tested values give about $37.5\%$ of ambient dimension | theorem-support computation |
| Random matrix pairs avoid $AB=0$ | VII-B | $0/400000$ tested nonzero square matrix pairs satisfy $AB=0$ | empirical sanity check |
| Type IV incidence is perturbatively unstable | VII-B | perturbation at $\varepsilon=10^{-6}$ breaks constructed $AB=0$ in $100/100$ trials for $d=2,3,4$ | empirical stability check |
| Tested random bridge products avoid incidence | VII-C | five fixed-seed random systems give $1080/1080$ safe bridge products and zero incidence candidates | computational evidence |
| Type III/IV boundary is sharp at bridge level | VII-C | synthetic Type III has $4/4$ rank-protected bridges; synthetic Type IV has $4/4$ incidence candidates | constructed boundary check |
| Rubik is structured rather than random-generic | VII-C | Rubik has $2376$ bridge products, $1848$ generic nonincidence products, and $528$ bridge-level incidence candidates concentrated in four sector triples | structured-laboratory evidence |
| Tested ablations keep missing incidence | VII-C | dimension $6$--$16$, rank-deficient fraction $0$--$0.8$, generator count $2$--$6$: $75$ random runs, $23400$ audited bridge products, zero incidence candidates | exploratory only |
| Type III and Type IV separate the candidate class | VII-A | synthetic Type III lies in $C$; synthetic Type IV lies outside $C$ | constructed examples |
| Exact $(R_1,R_2)$ signatures showed no $D$ disagreement | VII-A | $80$ systems produced $4$ exact-hash classes with identical $(R_1,R_2)$; all had identical $D$ structure | computational evidence |
| Represented atlas is currently diagnostic | VII-A | regular-representation sectorizations produced nearly zero $R_1$ in most systems and no Type IV example | limitation, not negative theorem |

### Computational Proposition 1 (VII-A Completion Evidence)

The Paper VII support suite verifies the following finite statements.

**(i) Type III versus Type IV.** A synthetic Type III cancellation system lies
inside the candidate completeness class $C$. A synthetic Type IV incidence
system lies outside $C$.

**(ii) Incidence instability.** Starting from constructed Type IV systems,
generic perturbation at $\varepsilon=10^{-6}$ breaks $AB=0$ in $100/100$
trials for $d=2,3,4$.

**(iii) Random-pair absence.** Across $400000$ random square matrix pairs in
the tested dimensions, no nonzero pair satisfied $AB=0$.

**(iv) Exact signature audit.** In $80$ diverse random sectorized systems,
there were $4$ exact-hash equivalence classes with identical $R_1$ and $R_2$
arrays. All $4$ classes had identical $D_{\max}$ and identical per-depth
structure. No $D$ disagreement was found.

**(v) Claim-status-metadata bridge audit.** The rank-protected bridge audit is
split into five gates. Gate A is theorem-support: Corollary 3 was checked on
constructed rank-protected blocks in dimensions $2,3,4$, with no violation. Gate B
checks the Type III/IV boundary: the synthetic Type III model has $4/4$
rank-protected bridge products and zero incidence candidates, while the
synthetic Type IV model has $4/4$ incidence candidates. Gate C is computational
evidence for generic nonincidence: five fixed-seed random systems
($42,\ldots,46$) give $1080/1080$ safe bridge products and zero incidence
candidates.

Gate D is diagnostic. The Rubik system behaves differently: among $2376$
bridge products, $1848$ are generic nonincidence products and $528$ are
bridge-level incidence candidates. These are candidate products in the audit,
not certified Type IV accessibility obstructions. They are concentrated in
four sector triples, in zero-based sector indices
$(2,6,8)$, $(5,6,8)$, $(8,6,2)$, and $(8,6,5)$.

Equivalently, in the RIME sector labels, they involve the triples
$(S3,S7,S9)$ and $(S6,S7,S9)$ together with their reversed orientations.

Gate E is exploratory. It varies total dimension $6$--$16$, rank-deficient
fraction $0$--$0.8$, and generator count $2$--$6$. Across $75$ random runs and
$23400$ audited bridge products, no incidence candidate appears. This ablation
is evidence for the genericity picture, not a theorem.

These computations do not prove Conjecture 1. They support the claim that Type
IV is the hard boundary and that, away from this boundary and under the tested
nondegeneracy/richness conditions, the accessibility jet behaves as a complete
object in the tested families.

![Rank-protected bridge audit. The tested random families show no audited
incidence candidates; the synthetic Type IV boundary is sharp; Rubik
concentrates bridge-level incidence candidates, not certified Type IV
accessibility obstructions, in a small structured subset of sector triples.](../../figures/paper7/fig3_rank_protected_bridge_audit.png)

The Rubik bridge audit should not be read as a contradiction to generic
nonincidence. It shows that Rubik lies in a structured, rank-deficient region
of the sectorized-system space. This is precisely why the Rubik laboratory is
useful: it is rich enough to expose nongeneric incidence geometry that random
systems did not hit in the tested audits.

![Rubik incidence concentration. In the bridge audit, all observed bridge-level
incidence candidates cluster in four oriented sector triples through the $S7$
hub. This locates Rubik in a structured exceptional region rather than in the
tested random-generic regime.](../../figures/paper7/fig4_rubik_incidence_concentration.png)

**Remark 2 (Transport-to-Incidence Hub Recurrence).** The four Rubik incidence
candidate triples are
$(S3,S7,S9)$ and $(S6,S7,S9)$, together with their reversed orientations. Thus
$S7$ is the bridge-level incidence hub in the Paper VII audit. This echoes the
Paper II transport geometry, where $S7$ lies at the end of the
$S5$--$S6$--$S7$ transport chain and next to the unique Type II edge
$S8$--$S9$ \cite{paper2}. No theorem-level relation between the transport hub
and the incidence hub is claimed here. Hub recurrence may indicate a later
notion of sector centrality linking transport, incidence, and accessibility.

![Generic sampling landscape. Across the audited products in the tested random
families, incidence candidates remain absent. The final panel points back to Paper VI: structured
exceptional carriers require a moduli-space and wall-crossing description.](../../figures/paper7/fig5_generic_sampling_landscape.png)

### Represented Atlas Limitation

The represented-atlas component is currently diagnostic rather than decisive.
Regular-representation sectorizations produced nearly zero $R_1$ in most
tested systems, meaning they do not yet probe rich cross-sector Type IV
behavior. This is a known limitation of the current atlas.

The lesson is useful: Type IV requires mixed sectorizations where cross-sector
blocks exist and products nevertheless vanish by incidence. Regular
representation sectorizations tend to suppress the first condition.

The rank-protected bridge audit adds the opposite lesson. Tested random
sectorized systems miss the incidence variety in the audited bridge products,
whereas Rubik hits it in a structured and repeatable way. Thus Rubik is not a
generic point of the sectorized-system space. It is a stable carrier of
high-codimension algebraic structure, which is exactly why it functions as a
useful laboratory for the RIME program.

***

## Scope and Open Problems

### What This Paper Establishes

- Type IV incidence is the algebraic variety $I=\{(A,B):AB=0,\ A,B\ne0\}$.
- On fixed-rank strata, $\operatorname{codim}I_r=(m-r)(n-r)+pr$.
- For square blocks, the dominant incidence codimension is asymptotic to
  $3d^2/4$.
- Rank-protected projected block strata exclude Type IV.
- Random bridge products in the tested families are fully safe from incidence,
  while Rubik exhibits a structured incidence sublocus concentrated in a small
  set of sector triples.
- Computational evidence separates Type III from Type IV and supports
  generic completion away from incidence.

### What This Paper Does Not Establish

- It does not prove a universal theorem that $(R_1,R_2)$ determines $D$.
- It does not prove that all Type IV incidence conditions remain stable under
  arbitrary Lie bracketing at all depths.
- It does not classify higher-depth walls $R_3,R_4,\ldots$.
- It does not yet construct a rich representation-derived Type IV accessibility
  obstruction; Rubik currently supplies bridge-level incidence candidates.

### Open Problems

1. **Generic completion theorem.** Prove Conjecture 1 or find the minimal
   non-incidence counterexample.

2. **Algebraic richness.** Express the commutant-richness condition needed to
   repair Type III cancellations in terms of the representation and the
   accessibility jet.

3. **Incidence in represented systems.** Determine the intersection of
   $\Sigma_{\mathrm{IV}}$ with representation-derived sectorization loci.

4. **Higher-depth completion.** Extend the incidence/cancellation analysis from
   length-two witnesses to higher Hall layers.

## Appendix A --- Perturbation Check

The Type IV boundary is perturbatively unstable in the tested models.

![Type IV perturbation instability. In the synthetic incidence families, every
tested perturbation amplitude breaks the constructed $AB=0$ relation.](../../figures/paper7/figA1_type_iv_perturbation_instability.png)

## Appendix B --- Claim-Status Metadata

The support suite is intentionally tiered: theorem support, computational
evidence, diagnostics, and exploratory scans are kept distinct.

![Paper VII claim-status metadata. The codimension and rank-protection statements
are theorem-level; random-family audits are computational evidence; the
completion principle remains conjectural.](../../figures/paper7/figA2_claim_status_metadata.png)

## Appendix C --- Cross-Species SOF Diagnostics

The main body of this paper is about generic completion and the Type IV
incidence boundary. The following diagnostics are not part of the proof of
Conjecture 1. They record a separate sanity check: the observables $R_1$,
$R_2$, and $D$ are not specific to the Rubik representation.

### Note on the Sectorized Observable Framework (SOF)

The objects appearing throughout Papers V--VII naturally admit a common
description, which we refer to as a Sectorized Observable Framework (SOF). We
describe an SOF by

$$
\mathcal F=(V,\{Q_i\},\mathcal X),
$$

where $V$ is a finite-dimensional representation space, $\{Q_i\}$ is a
distinguished family of sector projectors, and $\mathcal X$ is a chosen
observable family, typically generators, transfer operators, or related
observables.

Throughout this appendix we use the term "Sectorized Observable Framework
(SOF)" as a neutral observable architecture for the sectorized systems
appearing in the RIME program. It is intended as static object terminology
only; no deformation theory, registry theorem, or universal wall theory beyond
$(V,\{Q_i\},\mathcal X)$ is assumed here.

The quantities $R_1$, $R_2$, and $D$ are defined relative to this triple rather
than to any particular Rubik representation. The Rubik cube, quantum gate
systems, Markov systems, and graph systems considered below are therefore
interpreted as different realizations of the same observable architecture.

The unifying object is not a particular wall theory, but the sectorization.
Different systems may pass through the same observable architecture while
exhibiting different deformation geometries.

A systematic development of the SOF architecture lies beyond the scope of the
present paper and is left for future work.

### C.1 Quantum Gate Systems

For the quantum diagnostic, $V=(\mathbb C^2)^{\otimes q}$, the sectors are
computational-basis projectors $|b\rangle\langle b|$, and the operator family
is obtained from skew-Hermitian logarithmic gate generators.  The audit uses
the same convention as the main paper: $R_1$ records projected generator
support, $R_2$ records projected commutator survival, and $D$ records first
Lie-depth accessibility up to the tested depth.

The diagnostic table is:

| Gate set | $q$ | $R_1$ offdiag | $R_2$ offdiag | frozen $R_1$ | frozen $D$ | $D$-repaired | $D_{\max}$ |
|----------|-----|---------------|---------------|--------------|------------|--------------|------------|
| Pauli $\{X,Z\}$ | 2 | 16.7% | 33.3% | 8 | 8 | 0 | $\infty$ |
| Pauli $\{X,Y,Z\}$ | 2 | 22.2% | 22.2% | 8 | 8 | 0 | $\infty$ |
| Clifford $\{H,S,\mathrm{CNOT}\}$ | 2 | 16.7% | 33.3% | 6 | 0 | 6 | 2 |
| Clifford $\{H,S,\mathrm{CZ}\}$ | 2 | 11.1% | 16.7% | 8 | 8 | 0 | $\infty$ |
| Universal $\{H,T,\mathrm{CNOT}\}$ | 2 | 16.7% | 33.3% | 6 | 0 | 6 | 2 |
| Pauli $\{X,Z\}$ | 3 | 7.1% | 14.3% | 48 | 48 | 0 | $\infty$ |
| Clifford $\{H,S,\mathrm{CNOT}\}$ | 3 | 7.1% | 14.3% | 44 | 32 | 12 | $\infty$ |
| Universal $\{H,T,\mathrm{CNOT}\}$ | 3 | 7.1% | 14.3% | 44 | 32 | 12 | $\infty$ |

Here $\infty$ means unreached within the tested finite Lie-depth cutoff.

The observations are:

**Observation C.1 (Entangling generators create additional accessibility
channels).** In the tested computational-basis sectorization, CNOT opens
channels that are absent in product-only Pauli systems and in the tested CZ
variant.  The ordering observed in the diagnostic is

$$
\mathrm{CNOT}\;>\;\mathrm{CZ}\;>\;\text{product-only}
$$

with respect to $D$-repair in the tested gate families.

**Observation C.2 (Lie-depth repairs accessibility beyond first-order
transport).** $R_1$-frozen does not imply $D$-frozen.  In the two-qubit
Clifford+CNOT and Universal+CNOT systems, $6$ sector pairs frozen at the
first support layer become accessible at higher Lie depth.  In the three-qubit
versions, $12$ such repairs are observed within the tested depth range.

**Observation C.3 (Universality alone does not enrich low-order
accessibility).** Adding the $T$ gate does not change the audited
$R_1/R_2/D$ summary relative to Clifford+CNOT in the tested $2$- and
$3$-qubit systems.  Thus computational universality of the gate set and
low-order sector accessibility are different notions.

### C.2 Markov and Graph Systems

Markov and graph systems provide a second diagnostic layer.  For Markov
systems, $V$ is a finite state space, sectors are state projectors, and the
operator is a rate or logarithmic transition operator.  For graph systems,
$V$ is a vertex space, sectors are vertex or spectral sectors, and operators
may include adjacency, Laplacian, walk, or directed-edge data.

The current diagnostic results are:

| System | Species | Sectors | Generators | $R_1$ offdiag | frozen $R_1$ | frozen $D$ | $D$-repaired | $D_{\max}$ |
|--------|---------|---------|------------|---------------|--------------|------------|--------------|------------|
| Markov chain | Markov | 3 | 1 | 100.0% | 0 | 0 | 0 | 0 |
| Absorbing Markov | Markov | 3 | 1 | 66.7% | 2 | 2 | 0 | $\infty$ |
| Graph $K_3$ | Graph | 3 | 2 | 50.0% | 0 | 0 | 0 | 0 |
| Graph $P_3$ | Graph | 3 | 2 | 33.3% | 2 | 2 | 0 | $\infty$ |
| Graph $C_4$ | Graph | 4 | 2 | 33.3% | 4 | 4 | 0 | $\infty$ |

These examples show that the audit interface is portable, but they do not
establish a generic completion theorem.  Complete or strongly connected
examples may have $D=0$ without any repair phenomenon, while sparse examples
may remain frozen for the chosen operator family.

Unlike Rubik or CNOT-generated systems, these examples employ only a single
effective transport generator or an already-complete connectivity pattern,
leaving no opportunity for higher-order Lie repair.

### C.3 Cross-Species Observations

Across the quantum, Markov, and graph diagnostics, the same audit interface
applies once the sectorized data $(V,\{Q_i\},\mathcal X)$ are fixed.  The
results support the SOF hypothesis that $R_1$, $R_2$, and $D$ are sectorized
observables rather than Rubik-specific quantities.

The diagnostics also separate three regimes:

1. product-only or single-effective-generator systems, where higher-order Lie
   repair is absent in the tested range;
2. already-complete systems, where $D=0$ leaves no repair problem;
3. sufficiently rich noncommuting systems, such as CNOT-generated examples,
   where $R_1$-frozen pairs can be repaired at higher Lie depth.

### C.4 Empirical SOF Principle

Across the tested SOF species, nontrivial $D$-repair has appeared only in
systems equipped with sufficiently rich noncommuting transport generators,
visible to the chosen sectorization.  Tested single-generator or effectively
degenerate systems either are already connected at first depth, or remain
frozen in the tested Lie filtration.

This principle is empirical.  It should be read as a routing rule for future
SOF examples, not as a theorem.  To promote it, one would need a precise
definition of sufficient noncommutative transport richness and a proof that it
is necessary or generic for $D$-repair.

The scripts supporting this appendix are the quantum SOF audit in
`experiments/quantum/` and the Markov/graph SOF audit in
`experiments/paper7/`.

***

## References

**Program lineage.** Paper VII depends directly on Papers IV--VI. Paper IV
supplies the fixed-arrangement collision quotient \cite{paper4}; Paper V
supplies the local length-2 repair calculus and the Type III/IV mechanism
taxonomy \cite{paper5}; Paper VI supplies the deformation geometry of the
commutativity locus, accessibility jets, and accessibility walls
\cite{paper6}. Thus Paper VII is the static completion layer after collision
geometry, repair calculus, and wall geometry have been separated.

**External background.** The matrix and rank arguments use standard finite-dimensional linear algebra \cite{hornJohnson2013}. The representation-theoretic background is standard finite-group representation theory \cite{serre1977}, while the generic-accessibility vocabulary is anchored in geometric control theory \cite{jurdjevic1997,agrachevSachkov2004}. The Type IV boundary is an incidence/Schubert condition, so the algebraic-geometry background is the usual one for determinantal and incidence loci \cite{fulton1998,harris1992}. Hall words and weighted Lie-depth language continue the free-Lie-algebra framework already used in Paper V \cite{hall1950,reutenauer1993}. Paper VII does not use the association-scheme quotient story as its main background; that belongs with the fixed collision geometry of Paper IV.

**Computational provenance.** The support suite is organized as the VII-A atlas
experiment, the VII-B incidence codimension experiment, and the VII-C
rank-protected bridge audit. The manuscript-level reproducibility notes remain
attached to the support scripts in `experiments/paper7/`, while the repository
stores the full logs and tables used to check the claim-status metadata.

***

*Program status.* Paper V identifies local exceptional mechanisms. Paper VI
places those mechanisms on the generator-set moduli space. Paper VII identifies
the hard mechanism, Type IV incidence, as a high-codimension algebraic
degeneration. Within the SOF language
$\mathcal S=(V,\{Q_i\},\mathcal X)$, Type IV is an incidence stratum in the
block geometry of $\mathcal S$, not a Rubik anomaly. The resulting completion
theory is the current static closure framework: under the stated richness and
nondegeneracy hypotheses, and outside the relevant Type IV incidence variety,
the Generic Completion Principle predicts that $(R_1,R_2)$ determines the
first-depth invariant $D$. Deformation of the exceptional incidence locus
belongs to the moduli-space line opened by Paper VI.
