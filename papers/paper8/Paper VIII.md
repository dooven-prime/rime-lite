# Sectorized Observable Framework

### A Typed Static Object Language with Exact Marked Finite Realizations

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper is Paper VIII of the RIME program. It begins the static typed
object layer by identifying the data on which sectorized observable
constructions are defined. Papers IV--VII provide compatible earlier
interfaces but remain logically independent.*

***

## Abstract

**Problem.** Sectorized analyses repeatedly use projectors, observable
families, projected blocks, routed products, words, commutators, depth
filtrations, and several distinct operator-algebra closures. Treating these
objects as a single accessibility ladder obscures the carrier, labels, word
length, and closure conventions that determine their mathematical meaning.

**Approach.** We define a finite Sectorized Observable Framework (SOF) as a
marked sector realization together with a labelled observable map
$Y:A\to\mathcal B(V)$, which need not be injective. The
static data include the marked sector algebra
$D_Q$, the labelled family $Y$, the observable operator system
$E_{Y}$, and the sector-enriched system $S_{Q,Y}$. We
separate the positive word algebra $A_{Y}^{+}$, the observable
star-closure $A_{Y}^{*}$, and the sector-enriched star-closure
$A_{Q,Y}^{*}$. We then define separate operator/word and Lie/Hall
carriers, their strict morphisms, and their functorial constructions.

**Results.** A declared realization supplies a well-defined operator SOF core.
Strict operator morphisms form a category, as do independently enriched
Lie/Hall morphisms. Exact algebra or $*$-isomorphisms identify the matched
multiplication closures. Two functoriality theorems map labelled operator
blocks, routed products, full words, and registered Lie/Hall witnesses forward,
yielding non-increasing target depths. Equality is asserted under strict
equivalence, not under an arbitrary strict embedding. The two branches are not
identified without an explicit bridge theorem. Positive-word, star-word, and
sector-enriched saturated corners are recorded separately from finite
first-hit filtrations. As an exact realization family, a finite permutation
action together with a declared label map and marked state partition produces
a coordinate-sector SOF. In this family routed and full-word support coincide,
while aggregate Boolean paths can still strictly overestimate them. Finite
represented-image saturation gives exact first-hit word depths, including
certified nonreachability when present. A paper-owned conformance certificate
replays six modular actions, seventeen bounded triangle-group actions, fifty-one
marked sectorizations, and a four-state strict path/word witness.

**Boundary.** The sectorization may be representation-derived,
geometry-derived, filtration-derived, activation-derived, or externally
chosen. The realization construction is formal relative to the declared
choices, not a classification theorem and not a proof that every source has
a unique or canonical SOF realization. A finite representation alone is not
sufficient data for the labelled operative map or marked partition. The
promoted finite family supplies no Lie/Hall carrier and does not establish
generic strict separation of positive and star closures. This paper does not
claim a complete weak deformation category, moving accessibility fields,
universal completion, or an unconditional relation between word and Lie depth.

***

## Notation and Claim Layers {.unnumbered}

| Symbol | Meaning |
|--------|---------|
| $V$ | finite-dimensional complex Hilbert space |
| $Q_i$ | orthogonal sector projector |
| $D_Q=\operatorname{span}_{\mathbb C}\{Q_i\}$ | marked sector algebra |
| $Y:A\to\mathcal B(V)$ | declared labelled operator and word alphabet; the map need not be injective |
| $E_{Y}$ | $\operatorname{span}_{\mathbb C}\{I,Y_a,Y_a^*:a\in A\}$ |
| $S_{Q,Y}$ | $D_Q+E_{Y}$, the sector-enriched operator system |
| $A_{Y}^{+}$ | $\operatorname{alg}_{\mathbb C}(I,Y)$, the positive associative word algebra |
| $A_{Y}^{*}$ | $C^*(Y)$, the observable star-closure |
| $A_{Q,Y}^{*}$ | $C^*(D_Q\cup Y)$, the sector-enriched star-closure |
| $B_{ij}^a$ | $Q_iY_aQ_j$, a labelled operator block |
| $R_1[Y]$ | aggregate direct support of the labelled operator family |
| $\mathscr R_{d,ij}[Y]$ | linear span of length-$d$ routed products from $j$ to $i$ |
| $\mathrm{Route}_d[Y]$ | support of nonzero routed projected products |
| $\mathscr W_d(Y)$ | linear span of full ordered words of length $d$ |
| $W_d[Y]$ | support of nonzero full ordered words of length $d$ |
| $D_{\mathrm{route}}[Y]$ | first routed-product depth |
| $D_{\mathrm{word}}[Y]$ | first full-word depth |
| $X$ | independently registered skew-adjoint Lie family |
| $R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}}$ | direct and simple-commutator Lie shadows |
| $D_{\mathrm{Lie}}$ | depth relative to a declared Hall/Lie filtration |
| $G\curvearrowright\Omega$ | finite action used by the exact marked-permutation realization family |
| $\Pi=\{\Omega_i\}_{i\in I}$ | declared marked partition of the finite state set |
| $C_{\le d}[Y]$ | represented operators reached by positive words of lengths $1$ through $d$ |

The four reader-facing evidence levels are:

1. **Theorem:** an exact result proved from declared hypotheses;
2. **Computational Certificate:** a reproducible finite computation tied to
   declared inputs;
3. **Computational Observation:** a bounded numerical pattern without
   promotion;
4. **Research Program:** an open problem, conjectural bridge, or proposed
   extension.

Definitions are not evidence claims. Arrows in object diagrams denote
construction or audit order unless a theorem explicitly states an implication.

***

## Introduction

### Problem and Scope

The object studied here is not a particular representation, group, or
physical model. Instead, it is a finite sectorized observable realization: a
space, a compatible sectorization, and a declared observable alphabet. The
sectorization is source-dependent. It may arise from representation theory, a Dirac
operator, a mesh or interface geometry, a state filtration, a graph coloring,
an activation rule, a control decomposition, or an external coarse
coordinate choice. The observable language begins after that choice has been
made.

The static object language must preserve distinctions that are frequently
obscured by the shorthand

$$
R_1\longrightarrow R_2\longrightarrow D.
$$

In particular, a labelled operator family is not the same as its linear span,
an operator system is not a word filtration, a routed product is not a full
word, and a simple commutator is not a second associative word layer.
Positive multiplication closure, adjoint closure, and closure under internal
sector markers are also distinct operations. A saturated algebra records
closure, not the first length at which a sector pair is reached.

This paper therefore has five aims:

1. define the marked static SOF data;
2. define typed operator/word and Lie/Hall carriers;
3. define strict static morphisms and their categories;
4. prove carrier-qualified support preservation and depth monotonicity;
5. provide an exact marked finite-permutation realization family with a
   source-addressed conformance certificate and strict Boolean-path control.

This is a realization construction, not a classification theorem. It says
what data are sufficient to enter the SOF object language; it does not say
that all source systems admit the same canonical sectorization.

### Relation to Earlier Work

The fixed spectral arrangements of Paper IV, the typed fixed-family objects
of Paper V, the normality-gated point registrations of Paper VI, and the
projected-composition incidence geometry of Paper VII supply compatible
interfaces for the present static language \cite{paper4,paper5,paper6,paper7}.
They remain independent papers. Paper VI is not used here as a positive
moving SOF instance: the cited evidence consists of linearized
commutativity/normality certificates and pointwise registrations, while
coherent moving projector fields remain open.

***

## Static SOF Objects

### Definition (Operator SOF)

Let $V$ be a finite-dimensional complex Hilbert space and let
$\{Q_i\}_{i\in I}$ be a finite complete orthogonal sectorization:

$$
Q_i^*=Q_i,\qquad Q_i\ne0,\qquad Q_iQ_j=\delta_{ij}Q_i,\qquad
\sum_{i\in I}Q_i=I.
$$

Here compatibility means that the projectors and declared observables act on
the same space and that any source-specific admissibility conditions have
been recorded. It does not mean that the $Q_i$ commute with, or reduce, the
declared observables.

Let $A_0$ be a finite nonempty label set and let

$$
Y_0:A_0\longrightarrow\mathcal B(V),
\qquad a\longmapsto Y_a^{(0)},
$$

be an extracted labelled operator map. It is not required to be injective:
distinct source labels may have the same represented operator. Its operative
word convention is fixed before the SOF
core is declared. A positive-word convention sets
$Y=Y_0$. A star-word convention sets
$A=A_0\times\{+,-\}$ and declares the labelled completion

$$
Y^{\mathrm{adj}}
=
\{Y_{(a,+)}=Y_a^{(0)},\
Y_{(a,-)}=(Y_a^{(0)})^*:a\in A_0\},
$$

with $Y=Y^{\mathrm{adj}}$. Distinct completion labels remain distinct even
when their represented operators agree. After this registration,
$Y:A\to\mathcal B(V)$ denotes the selected operative alphabet
in all direct-support, routed-product, path, word, and depth constructions
below. Sector projectors are not letters of $Y$ unless a realization
explicitly declares them as observables. An **operator SOF core** is the tuple

$$
\mathcal F_{\mathrm{op}}=(V,\{Q_i\}_{i\in I},Y:A\to\mathcal B(V)).
$$

The possibly noninjective label map $a\mapsto Y_a$, including any
adjoint-completion labels, is part of the data. Passing to its image set, a
span, or a generated algebra may forget labels,
multiplicities, order, and word length; therefore those constructions are
recorded separately.

The marked sector algebra, observable operator system, and sector-enriched
operator system are

$$
D_Q=\operatorname{span}_{\mathbb C}\{Q_i:i\in I\},
$$

$$
E_{Y}
 =
\operatorname{span}_{\mathbb C}
\{I,Y_a,Y_a^*:a\in A\},
$$

$$
S_{Q,Y}=D_Q+E_{Y}.
$$

$E_{Y}$ and $S_{Q,Y}$ carry their standard operator-system
meanings. Here SOF abbreviates Sectorized Observable Framework, not operator
system.

Three multiplication closures are recorded separately. The **positive
associative word algebra** is

$$
A_{Y}^{+}
:=
\operatorname{alg}_{\mathbb C}(I,Y).
$$

It uses finite products of the declared operative letters and does not add
undeclared adjoints. It need not be adjoint-closed or semisimple. The
**observable star-closure** is

$$
A_{Y}^{*}:=C^*(Y),
$$

the smallest unital $*$-subalgebra of $\mathcal B(V)$ containing the declared
observables. The **sector-enriched star-closure** is

$$
A_{Q,Y}^{*}
:=
C^*(D_Q\cup Y)
=
C^*(S_{Q,Y}).
$$

The last closure permits sector projectors to occur as internal
multiplicative separators. It therefore contains routed star-words, not only
full words in the operative alphabet. If the operative alphabet is already
adjoint-completed, then $A_{Y}^{+}=A_{Y}^{*}$; this equality
is a consequence of that declared convention, not a default identification.

Finite-dimensional $C^*$-algebras are semisimple by standard theory, so the
two star-closures have Wedderburn decompositions. That background fact does
not automatically apply to $A_{Y}^{+}$, nor does it constitute an SOF theorem.
The marked tuple

$$
(D_Q,Y,E_{Y},S_{Q,Y},
A_{Y}^{+},A_{Y}^{*},A_{Q,Y}^{*})
$$

retains information that the abstract Wedderburn type alone does not retain.

### Optional Lie/Hall Enrichment

An operator SOF does not automatically contain a Lie carrier. A **Lie/Hall
enrichment** consists of an independently registered labelled family

$$
X=\{X_g\}_{g\in G_0},\qquad X_g^*=-X_g,
$$

together with a declared filtration

$$
\mathcal H_0\subseteq\mathcal H_1\subseteq\cdots.
$$

Each $\mathcal H_d$ is a declared linear space of formal Lie expressions in
the registered labels, and $H(X)$ denotes evaluation of
$H\in\mathcal H_d$ on the family $X$. The filtration record must
state whether $d$ denotes Hall length, bracket depth, or a
closure-generation round.

This registration must specify how $X$ is obtained, including any
logarithm branch, skew-adjoint projection, normalization, label map, and
depth convention. An explicit induction rule from $Y$ may provide
such an enrichment, but $X=\operatorname{skew}(E_{Y})$ is
not sufficient unless the labelled selection rule is also declared. In
particular, $iQ_i$ and $iI$ are not automatic Lie generators.

The layered SOF record is therefore one of:

$$
\begin{aligned}
\text{operator core:}\quad
    &(V,Q,Y),\\
\text{operator-system layer:}\quad
    &(V,Q,Y,E_Y,S_{Q,Y}),\\
\text{positive-word closure:}\quad
    &(V,Q,Y,A_Y^+),\\
\text{observable star layer:}\quad
    &(V,Q,Y,A_Y^*),\\
\text{sector-star layer:}\quad
    &(V,Q,Y,A_{Q,Y}^*),\\
\text{Lie/Hall enrichment:}\quad
    &(V,Q,Y;X,\{\mathcal H_d\}_{d\ge0}).
\end{aligned}
$$

The layers are optional enrichments, not an assertion that all SOFs contain
all of them.

### Sectorization Origin

The source of the projectors is not part of the abstract SOF core. A
sectorization may be:

- representation-derived, such as reducing or joint-spectral projectors;
- geometry-derived, such as block-diagonal Dirac or mesh/interface sectors;
- filtration-derived, such as reachable or communicating-state flags;
- graph-derived, such as vertex or color-class sectors;
- activation-derived, such as activation or rank regions;
- externally chosen, when a declared coarse coordinate system is supplied.

The origin must be recorded in a realization, because different origins can
produce different admissibility domains and different observable families.
Once the projectors and labelled alphabet are fixed, the static constructions
below depend on the realized SOF data.

***

## Declared Sectorized Realizations

### No-Sector No-Shadow Principle

Let $V$ carry a finite operator family $Y$. If no sectorization
$\{Q_i\}$ is specified, then sector-indexed blocks and their typed shadows are
not defined. If the only sectorization is the trivial one $\{I\}$, there are
no distinct sector pairs and hence no nontrivial cross-sector support,
routed bridge, or sector-indexed depth.

This is a definitional necessity statement, not a classification theorem. A
global observable or an unsectorized diagnostic may still exist; it simply is
not a sector-indexed SOF shadow.

### Figure and Interface

![Typed SOF object language. The marked sector algebra, labelled operator
alphabet, typed finite filtrations, and saturated closures are distinct
layers. The operator/word and Lie/Hall branches are not identified without a
bridge theorem.](../../figures/paper8/fig1_sof_definition.png)

### Construction (Declared SOF Realization)

Let a finite source system provide:

1. a finite-dimensional complex Hilbert space $V$;
2. a compatible complete sectorization $\{Q_i\}_{i\in I}$;
3. a finite label set $A$ and an observable extraction rule producing a
   possibly noninjective map $Y:A\to\mathcal B(V)$.

Then the data define an operator SOF core

$$
\mathcal F_{\mathrm{op}}=(V,\{Q_i\},Y:A\to\mathcal B(V)).
$$

The realization is uniquely determined relative to the declared space,
sectorization, extraction rule, label set, word convention, and
normalization. If a Lie/Hall enrichment or a finite filtration is also
supplied, the corresponding typed constructions are defined relative to
those additional choices.

### Well-Definedness

The extraction rule supplies the labelled map $Y$, and the
compatible sectorization supplies the mutually orthogonal projectors. These
are exactly the data of the operator SOF core. The definitions of
$D_Q$, $E_{Y}$, $S_{Q,Y}$, and the three closure layers
then use only the realized operators and the declared operative alphabet. A
filtration or Lie/Hall carrier is available only when its additional
registration data have been supplied. Thus, the construction is
source-independent once these choices are fixed; however, it does not
constitute a classification of source systems.

### Realization Boundary

Sectorization may come from representation theory, geometry, a filtration, a
graph, an activation, control/PDE data, or an external choice. All may enter
the SOF language. The realization record must state whether the choice is
canonical, constructed, truncated, or non-unique. Different realizations of
the same source system need not be strictly equivalent.

The construction does not turn a source model into a unique SOF, and it does not
promote a numerical sectorization to an exact one. Report-level or
black-box uses belong to later diagnostic protocols and are not strict SOF
objects by this construction alone.

![Sectorization necessity. Global observables exist without sectors, but
sector-indexed blocks, routes, and typed shadows require the compatible
sectorization.](../../figures/paper8/fig2_no_sector_no_shadow.png)

***

## Typed Static Constructions

### Labelled Blocks and Direct Support

For $i,j\in I$ and $a\in A$, define the labelled block

$$
B_{ij}^a=Q_iY_aQ_j.
$$

The labelled and aggregate direct supports are

$$
R_{1,a}[Y](i,j)
=
\mathbf 1[B_{ij}^a\ne0],
\qquad
R_1[Y](i,j)
=
\max_{a\in A}R_{1,a}[Y](i,j).
$$

The aggregate support forgets the witnessing label; the tensor
$R_{1,a}[Y]$ retains it. The direction convention is

$$
B_{ij}^a\ne0
\quad\Longleftrightarrow\quad
j\longrightarrow i.
$$

For an off-diagonal pair $i\ne j$, the first operator corner

$$
C_{ij}^{(1)}=Q_iE_{Y}Q_j
$$

is an operator-system-derived corner space. For $i\ne j$, it need not itself
be an operator system, nor is it a replacement for the
generator-labelled block tensor. It agrees with aggregate direct support
only when the selected alphabet is adjoint-closed with the declared direction
convention. On the diagonal, $Q_iE_{Y}Q_i$ always contains
$\mathbb C Q_i$ because $I\in E_{Y}$, so it cannot be identified
with observable direct support.

### Aggregate Support Paths

For $d\ge1$, define the exact-length aggregate path shadow by

$$
\operatorname{Path}_d(R_1[Y])(i,j)
:=
\mathbf 1\!\left[
\begin{array}{c}
\text{there exist }k_0=j,k_1,\ldots,k_d=i\\
\text{such that }R_1[Y](k_\ell,k_{\ell-1})=1\\
\text{for every }1\le\ell\le d
\end{array}
\right].
$$

Also set

$$
\operatorname{Path}_0(R_1[Y])(i,j)=\delta_{ij}.
$$

This is a path in the aggregate directed support graph, with direction
$j\to i$. It has exactly $d$ steps, forgets all generator labels, and imposes
no compatibility condition between witnessing labels on adjacent edges.
Repeated vertices are allowed, and a self-loop step is permitted exactly when
the corresponding aggregate diagonal support $R_1[Y](k,k)$ is nonzero.
These conventions are required for comparison with routed products that may
contain nonzero diagonal sector blocks. Off-diagonal accessibility statements
still restrict the endpoint pair to $i\ne j$.

### Routed Products

For labels $a_1,\ldots,a_d$ and intermediate sectors
$\mathbf k=(k_1,\ldots,k_{d-1})$, define

$$
\begin{aligned}
P^{Y}_{i,\mathbf k,j}(a_d,\ldots,a_1)
={}&Q_iY_{a_d}Q_{k_{d-1}}Y_{a_{d-1}}\cdots\\
&\qquad Q_{k_1}Y_{a_1}Q_j.
\end{aligned}
$$

For $d=1$, the intermediate tuple is empty and the routed product is
$P^{Y}_{i,j}(a_1)=Q_iY_{a_1}Q_j$.

The corresponding routed-product space is

$$
\mathscr R_{d,ij}[Y]
:=
\operatorname{span}_{\mathbb C}
\left\{
P^{Y}_{i,\mathbf k,j}(a_d,\ldots,a_1):
\mathbf k\in I^{d-1},\ (a_1,\ldots,a_d)\in A^d
\right\}.
$$

The Boolean routed shadow is

$$
\mathrm{Route}_d[Y](i,j)
:=
\mathbf 1[
\mathscr R_{d,ij}[Y]\ne\{0\}].
$$

Thus the shadow is nonzero exactly when at least one declared label tuple and
intermediate-sector tuple produces a nonzero routed product. The space
$\mathscr R_{d,ij}[Y]$ retains linear routed-product information; its
Boolean shadow is not graph path closure.

### Full Words

Use the same operative alphabet $Y$ that defines $R_1[Y]$
and $\mathrm{Route}_d[Y]$. Define the exact-length word space

$$
\mathscr W_d(Y)
:=
\operatorname{span}_{\mathbb C}
\{Y_{a_d}\cdots Y_{a_1}:(a_1,\ldots,a_d)\in A^d\},
$$

with $\mathscr W_0(Y)=\mathbb C I$, and its sector corner

$$
\mathscr W_{d,ij}[Y]
:=
Q_i\mathscr W_d(Y)Q_j.
$$

The full-word shadow is

$$
W_d[Y](i,j)
:=
\mathbf 1[
\mathscr W_{d,ij}[Y]\ne\{0\}].
$$

Completeness of the sectorization gives

$$
Q_iY_{a_d}\cdots Y_{a_1}Q_j
=
\sum_{\mathbf k}
P^{Y}_{i,\mathbf k,j}(a_d,\ldots,a_1).
$$

Consequently,

$$
\mathscr W_{d,ij}[Y]
\subseteq
\mathscr R_{d,ij}[Y],
\qquad
W_d[Y]
\subseteq
\mathrm{Route}_d[Y]
\subseteq
\operatorname{Path}_d(R_1[Y]).
$$

The reverse inclusions are not available in general. A full word may vanish
by cancellation among routed terms, and a routed product may vanish by
image--kernel alignment even when its Boolean path is present.

The dimensions of $\mathscr W_{d,ij}[Y]$ and
$\mathscr R_{d,ij}[Y]$ are typed static data. Although later deformation
theories may study their rank or dimension walls, this paper makes no
moving-wall claim.

### Typed Depths and Saturation

For exact extended-valued objects define

$$
D_{\mathrm{route}}[Y](i,j)
=
\inf\{d\ge1:\mathrm{Route}_d[Y](i,j)=1\},
$$

$$
D_{\mathrm{word}}[Y](i,j)
=
\inf\{d\ge1:W_d[Y](i,j)=1\}.
$$

Here $\inf\varnothing=\infty$. A finite computation reports
$D^{(\le d_{\max})}=d$ when it witnesses a first hit at
$1\leq d\leq d_{\max}$, and reports
$D^{(\le d_{\max})}=\mathrm{unreached}$ otherwise. Promoting the latter value
to exact mathematical infinity requires the relevant closure or saturation
certificate. The sentinel $999$ is never mathematical infinity.

The three saturated corner spaces are

$$
A_{ij}^{+}
:=
Q_iA_{Y}^{+}Q_j,
\qquad
A_{ij}^{*}
:=
Q_iA_{Y}^{*}Q_j,
$$

and

$$
A_{ij}^{Q,*}
:=
Q_iA_{Q,Y}^{*}Q_j.
$$

Since

$$
A_{Y}^{+}
=
\operatorname{span}_{\mathbb C}
\bigcup_{d\ge0}\mathscr W_d(Y),
$$

The condition $A_{ij}^{+}\ne0$ records positive-word saturation for the
operative alphabet. In finite dimensions, the cumulative spaces
$\sum_{\ell=0}^{d}\mathscr W_\ell(Y)$ stabilize at
$A_{Y}^{+}$; however, the stabilized algebra alone does not retain
the first stabilizing or first-hit length. The corner $A_{ij}^{*}$ records
star-word saturation and may use
adjoints that are absent from a positive operative alphabet. The corner
$A_{ij}^{Q,*}$ records sector-enriched star-saturation and may use projectors
as internal route separators. In particular, a nonzero element such as

$$
Q_iY_aQ_kY_bQ_j
$$

may survive in $A_{ij}^{Q,*}$ even when the corresponding full-word corner
$Q_iY_aY_bQ_j$, which sums over all intermediate routes, vanishes by
cancellation. Thus positive-word, star-word, and routed star-saturation are
not identified.

None of these corner spaces records the first-hit word length, a witnessing
labelled word, or a witnessing route. For $i=j$, all three saturated corners
are automatically nonzero because their defining unital algebras contain
$I$, and hence

$$
Q_iIQ_i=Q_i
\in
A_{ii}^{+}\cap A_{ii}^{*}\cap A_{ii}^{Q,*}.
$$

Saturated Boolean accessibility is therefore informative without
qualification primarily on off-diagonal sector pairs. A nontrivial diagonal
audit must remove the scalar sector identity. For any
$A_{ii}^{\bullet}\in\{A_{ii}^{+},A_{ii}^{*},A_{ii}^{Q,*}\}$, one may use the
Hilbert--Schmidt reduced space

$$
\widetilde A_{ii}^{\bullet}
:=
A_{ii}^{\bullet}
\cap
(\mathbb C Q_i)^{\perp_{\mathrm{HS}}},
$$

or equivalently the vector-space quotient
$A_{ii}^{\bullet}/\mathbb C Q_i$. The quotient is not asserted to be an
algebra quotient. Registry or wall data must state whether a saturated-corner
quantity is off-diagonal or uses this scalar-reduced diagonal convention. The
condition $D_Q\subseteq A_{Y}^{*}$ is required before the observable
star-closure and the sector-enriched star-closure coincide.

### Lie/Hall Branch

Fix a total order on the Lie-label set $G_0$. For a registered Lie family
$X=\{X_g\}_{g\in G_0}$, define

$$
R_{1,g}^{\mathrm{Lie}}(i,j)
=
\mathbf 1[Q_iX_gQ_j\ne0],
\qquad
R_1^{\mathrm{Lie}}(i,j)
=
\max_gR_{1,g}^{\mathrm{Lie}}(i,j),
$$

and

$$
R_{2,g,h}^{\mathrm{Lie}}(i,j)
=
\mathbf 1[Q_i[X_g,X_h]Q_j\ne0],
\qquad
R_2^{\mathrm{Lie}}(i,j)
=
\max_{g<h}R_{2,g,h}^{\mathrm{Lie}}(i,j).
$$

Here $\max\varnothing:=0$; equivalently,
$R_2^{\mathrm{Lie}}(i,j)=0$ when $|G_0|<2$.

Given a declared Hall or Lie filtration $\{\mathcal H_d\}$,

$$
D_{\mathrm{Lie}}(i,j)
=
\inf\{d:\exists H\in\mathcal H_d,\ Q_iH(X)Q_j\ne0\}.
$$

The depth index must state whether it means Hall length, bracket depth, or
closure-generation round. Associative products
$\mathrm{Route}_d[X]$ and $W_d[X]$ are allowed as
diagnostics, but they are not Hall-filtered support and do not define
$D_{\mathrm{Lie}}$.

There is no canonical identification

$$
R_1[Y]\equiv R_1^{\mathrm{Lie}},
\qquad
D_{\mathrm{word}}\equiv D_{\mathrm{Lie}}.
$$

Nor is $W_d[X]$ canonically identified with support at the
corresponding Hall level. Each identification requires a separately declared
bridge theorem and aligned registrations.

***

## Strict Morphisms and Functoriality

### Operator Strict Morphisms

Let

$$
\mathcal F=(V,Q,Y),
\qquad
\mathcal F'=(V',Q',Y')
$$

be operator SOF cores. A **strict operator SOF morphism**
$\Phi=(U,f,\phi):\mathcal F\to\mathcal F'$ consists of:

1. an isometric embedding $U:V\to V'$;
2. an injective sector map $f:I\to I'$;
3. an injective operative-alphabet map $\phi:A\to A'$ that respects any
   explicitly registered adjoint labels;
4. a reducing-image condition for
   $P_f=\sum_{i\in I}Q'_{f(i)}$;
5. the intertwining identities

$$
UQ_iU^*=Q'_{f(i)},
$$

$$
UY_aU^*=P_fY'_{\phi(a)}P_f
\qquad (a\in A).
$$

The reducing-image condition is

$$
[P_f,Y'_{\phi(a)}]=0
\qquad (a\in A).
$$

Completeness and the sector intertwining identities give

$$
P_f
=
\sum_{i\in I}UQ_iU^*
=
UU^*.
$$

The reducing-image condition prevents the matched observable from leaving the
embedded selected sectors and returning through an untracked target sector.
The matched-observable conjugation identity also intertwines adjoints.

The induced marked-sector map sends $Q_i$ to $Q'_{f(i)}$, and the induced
operator-system map sends $E_{Y}$ into $P_fE_{Y'}P_f$.
For the matched target family
$\phi(Y)=\{Y'_{\phi(a)}:a\in A\}$, conjugation by $U$ yields
an algebra isomorphism and a unital $*$-isomorphism, respectively:

$$
\operatorname{Ad}_U:A_{Y}^{+}
\xrightarrow{\cong}
P_fA_{\phi(Y)}^{+\prime}P_f,
\qquad
\operatorname{Ad}_U:A_{Y}^{*}
\xrightarrow{\cong}
P_fA_{\phi(Y)}^{*\prime}P_f.
$$

Here the primed closures are formed in $\mathcal B(V')$ from the matched
target family only. Because $P_f$ reduces every matched observable, both
compressed closures are algebras on $P_fV'$ with unit $P_f$.

For the sector-enriched layer, define the **matched sector-star closure**

$$
A_{f(Q),\phi(Y)}^{*\prime}
:=
C^*_{P_f\mathcal B(V')P_f}
\left(
\{Q'_{f(i)}:i\in I\}
\cup
\{P_fY'_{\phi(a)}P_f:a\in A\}
\right).
$$

Conjugation by $U$ then gives the unital $*$-isomorphism

$$
\operatorname{Ad}_U:A_{Q,Y}^{*}
\xrightarrow{\cong}
A_{f(Q),\phi(Y)}^{*\prime}.
$$

This matched closure satisfies

$$
A_{f(Q),\phi(Y)}^{*\prime}
\subseteq
P_fA_{Q',Y'}^{*}P_f.
$$

Because $P_f\in D_{Q'}\subseteq A_{Q',Y'}^*$, the right-hand side is a
$C^*$-corner rather than merely a linear corner. Equality with the full target
corner is not asserted, because unmatched target observables may contribute
additional corner elements.

A strict equivalence is a strict morphism for which $U$ is unitary and $f$
and $\phi$ are bijections. The optional Lie/Hall enrichment adds an injective
label map $\psi:G_0\to G'_0$. It must satisfy

$$
[P_f,X'_{\psi(g)}]=0,
\qquad
UX_gU^*=P_fX'_{\psi(g)}P_f.
$$

Let $\psi_*$ denote relabelling of formal Lie expressions. Filtration
preservation means

$$
\psi_*(\mathcal H_d)\subseteq\mathcal H'_d
\qquad\text{for every }d,
$$

and, for every $H\in\mathcal H_d$,

$$
UH(X)U^*
=
P_f(\psi_*H)(X')P_f.
$$

A strict Lie/Hall equivalence additionally requires $\psi$ to be bijective
and the filtration-preservation condition to hold in both directions.

### Strict-Category Proposition

**Proposition 1 (Closure of Strict Morphisms).** Finite operator SOF cores and
strict operator morphisms form a category, denoted

$$
\mathsf{SOF}_{\mathrm{op,str}}.
$$

Lie/Hall-enriched SOFs and filtration-preserving strict morphisms form a
separate category over the operator category, denoted

$$
\mathsf{SOF}_{\mathrm{Lie,str}}.
$$

**Proof.** Identity isometries and identity label maps satisfy all defining
conditions. For composition, let

$$
\Phi=(U,f,\phi):\mathcal F\longrightarrow\mathcal F',
\qquad
\Phi'=(U',f',\phi'):\mathcal F'\longrightarrow\mathcal F''.
$$

The composite isometry and label maps are $U'U$, $f'\circ f$, and
$\phi'\circ\phi$. The corresponding selected-sector projection is

$$
P_{f'\circ f}
=
\sum_{i\in I}Q''_{f'(f(i))}
=
U'P_fU'^*.
$$

Write $P_{f'}=U'U'^*$ and
$Z=Y''_{\phi'(\phi(a))}$. Since $P_{f'}$ reduces $Z$ and
$U'^*ZU'=Y'_{\phi(a)}$, the first reducing condition gives

$$
\begin{aligned}
P_{f'\circ f}Z
&=U'P_fY'_{\phi(a)}U'^*\\
&=U'Y'_{\phi(a)}P_fU'^*
=ZP_{f'\circ f}.
\end{aligned}
$$

Moreover,

$$
\begin{aligned}
(U'U)Y_a(U'U)^*
&=U'P_fY'_{\phi(a)}P_fU'^*\\
&=P_{f'\circ f}
Y''_{\phi'(\phi(a))}
P_{f'\circ f}.
\end{aligned}
$$

The sector identities compose in the same way, so the operator composite is
strict. For Lie/Hall enrichments, the composite relabelling is
$(\psi'\circ\psi)_*=\psi'_*\circ\psi_*$. It preserves every filtration level,
and the same calculation proves the reducing and intertwining identities for
each evaluated formal Lie expression. Thus identities and composition are
closed in both categories. Associativity is inherited from composition of
isometries and label maps. $\square$

The existence of a Lie/Hall carrier is not inferred from an operator
morphism.

### Operator/Word Functoriality

**Theorem 2 (Operator/Word Support Preservation and Depth Monotonicity).** Let
$\Phi=(U,f,\phi):\mathcal F\to\mathcal F'$ be a strict operator SOF
morphism. Then for all matched labels and sectors:

$$
B_{ij}^a\ne0
\Longleftrightarrow
Q'_{f(i)}Y'_{\phi(a)}Q'_{f(j)}\ne0.
$$

The same equivalence holds for every matched routed product and every
matched full word. At the linear-space level,

$$
\operatorname{Ad}_U\bigl(
\mathscr R_{d,ij}[Y]\bigr)
\subseteq
\mathscr R'_{d,f(i)f(j)}[Y'],
$$

and

$$
\operatorname{Ad}_U\bigl(
\mathscr W_{d,ij}[Y]\bigr)
\subseteq
\mathscr W'_{d,f(i)f(j)}[Y'].
$$

Therefore

$$
R_1[Y](i,j)
\Longrightarrow
R_1[Y'](f(i),f(j)),
$$

$$
\mathrm{Route}_d[Y](i,j)
\Longrightarrow
\mathrm{Route}_d[Y'](f(i),f(j)),
$$

and

$$
W_d[Y](i,j)
\Longrightarrow
W_d[Y'](f(i),f(j)).
$$

Taking the first-hit infima gives

$$
D_{\mathrm{route}}'(f(i),f(j))
\le D_{\mathrm{route}}(i,j),
\qquad
D_{\mathrm{word}}'(f(i),f(j))
\le D_{\mathrm{word}}(i,j)
$$

whenever the source depths are finite. Under strict equivalence, the
corresponding supports and depths are equal.

**Proof.** The sector and observable intertwining identities give

$$
UQ_iY_aQ_jU^*
=
Q'_{f(i)}Y'_{\phi(a)}Q'_{f(j)}.
$$

Because $P_f$ reduces every matched observable, routed products satisfy

$$
\begin{aligned}
&UQ_iY_{a_d}Q_{k_{d-1}}\cdots Q_{k_1}Y_{a_1}Q_jU^*\\
&\qquad=
Q'_{f(i)}Y'_{\phi(a_d)}Q'_{f(k_{d-1})}\cdots
Q'_{f(k_1)}Y'_{\phi(a_1)}Q'_{f(j)},
\end{aligned}
$$

and full words satisfy

$$
UQ_iY_{a_d}\cdots Y_{a_1}Q_jU^*
=
Q'_{f(i)}Y'_{\phi(a_d)}\cdots
Y'_{\phi(a_1)}Q'_{f(j)}.
$$

Because $U$ is an isometry, nonzero source matrices remain nonzero.
Consequently, a source filtration witness supplies a target witness of no
greater depth. A strict equivalence provides the reverse identities. $\square$

### Lie/Hall Functoriality

**Theorem 3 (Lie/Hall Support Preservation and Depth Monotonicity).** Let
$\Phi$ be a strict morphism between
Lie/Hall-enriched SOFs with the filtration-preserving Lie-label map declared
above. Then

$$
R_1^{\mathrm{Lie}}(i,j)
\Longrightarrow
R_1^{{\mathrm{Lie}}\prime}(f(i),f(j)),
$$

$$
R_2^{\mathrm{Lie}}(i,j)
\Longrightarrow
R_2^{{\mathrm{Lie}}\prime}(f(i),f(j)),
$$

and

$$
D_{\mathrm{Lie}}'(f(i),f(j))
\le D_{\mathrm{Lie}}(i,j)
$$

whenever the source depth is finite. Under strict Lie/Hall equivalence, the
matched supports and depths are equal.

**Proof.** The carrier intertwining gives

$$
UX_gU^*=P_fX'_{\psi(g)}P_f.
$$

Consequently, conjugation by $U$ intertwines every matched commutator. The
formal relabelling $\psi_*$ likewise matches every filtered Lie expression
without increasing its filtration index. Therefore, the same nonzero-block and
filtration-witness argument used in the operator/word functoriality theorem
proves the claims. $\square$

### Functoriality Boundary

The theorems are functorial support and depth statements, not completion
results. They do not
imply that direct support determines routed composition, that routed products
determine full words, or that low-order Lie support determines Lie depth.
Matched multiplication closures are carried by exact isomorphisms, whereas
support in the full target alphabet is preserved by inclusion and first-hit
depth is only non-increasing.
Strict morphisms also do not create a deformation morphism. A generator-weight
path, a state-mixing path, or a training trajectory may fail to be isometric,
label-preserving, or reducing.

A deformation analysis may use a weaker category, provisionally denoted
$\mathsf{SOF}_{\mathrm{def}}$, but this paper does not define its arrows.

![Strict SOF morphism. The operator/word and optional Lie/Hall carriers have
separate label maps and separate functorial outputs. The static morphism is
not a deformation arrow.](../../figures/paper8/fig3_strict_morphism.png)

***

## Exact Marked Finite Permutation Realizations

The abstract static interface does not require a group action. Finite
permutation actions nevertheless provide a useful exact conformance family:
the Hilbert space, projectors, represented letters, routed products, and words
all admit finite combinatorial descriptions, while the marked partition and
source labels remain visible.

### Labelled Action Data

Let a finite group $G$ act on a finite set $\Omega$, let $A$ be a finite
nonempty label set, and let

$$
y:A\longrightarrow G
$$

be a declared source-letter map. Neither $y$ nor the represented map below is
assumed injective. The permutation representation on
$V=\mathbb C^{\Omega}$ is

$$
\rho(g)e_\omega=e_{g\omega},
\qquad
Y_a=\rho(y(a)).
$$

Let

$$
\Pi=\{\Omega_i\}_{i\in I},
\qquad
\Omega=\bigsqcup_{i\in I}\Omega_i,
$$

be a declared marked partition. Define the coordinate projector

$$
Q_i^{\Pi}e_\omega
=
\begin{cases}
e_\omega,&\omega\in\Omega_i,\\
0,&\omega\notin\Omega_i.
\end{cases}
$$

Here $G$ and $y$ retain source provenance, while the static SOF core consumes
the represented labelled map and marked partition. Neither the action nor the
label map is required to be faithful.

**Proposition 4 (Marked Finite Permutation Realization).** The data
$(\Omega,G,\rho,A,y,\Pi)$ define an exact operator SOF core

$$
\mathcal F_{\rho,y,\Pi}
=
\left(
\mathbb C^\Omega,
\{Q_i^\Pi\}_{i\in I},
(Y_a)_{a\in A}
\right).
$$

The operative alphabet is the labelled map
$Y:A\to U(\mathbb C^\Omega)$, not its image set. Thus $a\ne b$ and
$Y_a=Y_b$ are compatible with the realization. The action and labelled
alphabet do not by themselves select $\Pi$; different marked partitions of
the same represented action define different marked SOF data unless an
additional equivalence is supplied.

**Proof.** Every $Y_a$ is a permutation unitary. The coordinate projectors
satisfy

$$
(Q_i^\Pi)^*=Q_i^\Pi,
\qquad
Q_i^\Pi Q_j^\Pi=\delta_{ij}Q_i^\Pi,
\qquad
\sum_iQ_i^\Pi=I.
$$

They act on the same space as the labelled represented family, so the defining
conditions of an operator SOF core hold exactly. Nothing in $\rho$ selects a
partition as part of the SOF data, and replacing $Y:A\to U(V)$ by its image
would identify distinct labels whenever the represented map is noninjective.
$\square$

This gives the **Marked-Realization Principle**:

$$
\text{finite action}
+\text{ labelled operative map}
+\text{ marked partition}
\longrightarrow
\text{exact finite SOF realization}.
$$

The arrow is a construction. It does not assert a canonical partition or a
classification of finite representations.

### Deterministic Route/Word Coincidence

Coordinate partitions and permutation letters have a special property that
does not hold for general operator SOFs.

**Proposition 5 (Permutation Route/Word Coincidence).** For a marked finite
permutation realization and every $d\ge1$,

$$
\mathrm{Route}_d[Y]=W_d[Y].
$$

This is equality of Boolean support relations. It does not identify the linear
spaces $\mathscr R_{d,ij}[Y]$ and $\mathscr W_{d,ij}[Y]$.

**Proof.** Fix a labelled word and a source basis state. Because each letter
is a permutation, the state follows one unique sequence of intermediate
states and therefore one unique sequence of marked sectors. A nonzero full
word corner supplies that routed witness. Conversely, a nonzero routed product
contains a source basis state whose unique permutation trajectory follows the
declared intermediate sectors and ends in the target sector; the corresponding
full-word corner is therefore nonzero. Taking the union over labelled words
and intermediate-sector tuples proves the equality. $\square$

The proposition is carrier-specific. It removes route cancellation inside
this exact realization family, but it does not identify either relation with
aggregate Boolean graph paths.

### Exact Finite Word Saturation

For $d\ge1$, let

$$
C_{\le d}[Y]
=
\left\{
Y_{a_k}\cdots Y_{a_1}:
1\le k\le d,
(a_1,\ldots,a_k)\in A^k
\right\}.
$$

This is a cumulative represented-operator set. It is distinct from the
exact-length word space $\mathscr W_d(Y)$ and from the set of labelled words:
different labelled words may evaluate to the same represented permutation.

**Proposition 6 (Exact Finite Positive-Word Saturation).** For every marked
finite permutation realization, there is a finite $d_{\mathrm{sat}}\ge1$
such that

$$
C_{\le d_{\mathrm{sat}}}[Y]
=
C_{\le d_{\mathrm{sat}}+1}[Y]
=
\langle Y(A)\rangle,
$$

where $\langle Y(A)\rangle$ is the finite represented subgroup generated by
the operative letters. Hence, for every sector pair $(i,j)$, exhaustive
labelled breadth-first search gives either an exact shortest nonempty
first-hit word or an exact certificate that
$D_{\mathrm{word}}[Y](i,j)=\infty$.

**Proof.** All represented words lie in the finite permutation group on
$\Omega$, so the increasing sequence $C_{\le d}[Y]$ stabilizes. Because $A$
is nonempty and each represented letter has finite order, the identity occurs
at a positive length. At stabilization the cumulative set is closed under
right multiplication by every declared letter, so no later positive word can
add a represented operator. Conversely, every generated represented operator
has a finite positive-word witness. Exhaustive labelled breadth-first search
therefore records the minimum positive length of every represented operator.
Testing all saturated operators against $Q_i(\cdot)Q_j$ decides each sector
pair exactly. $\square$

A saturation receipt must bind the label alphabet, the label-to-operator map,
the marked partition, cumulative closure sizes, stabilization depth,
right-multiplication closure, the shortest nonempty identity word, and the
first-hit witnesses. A bounded search without this closure evidence still
reports `unreached`, not infinity.

### Four-State Exact Separation Witness

Let

$$
\Omega=\{0,1,2,3\},
\qquad
\Pi=\bigl\{\{0,1,2\},\{3\}\bigr\},
$$

and declare two labels represented by

$$
Y_a=(2\ 3),
\qquad
Y_b=(0\ 1)(2\ 3).
$$

**Proposition 7 (Boolean Path Overestimate).** With rows indexed by target
sector and columns by source sector,

$$
R_1[Y]
=
\begin{pmatrix}
1&1\\
1&0
\end{pmatrix},
\qquad
\operatorname{Path}_2(R_1[Y])
=
\begin{pmatrix}
1&1\\
1&1
\end{pmatrix},
$$

whereas

$$
\mathrm{Route}_2[Y]
=
W_2[Y]
=
\begin{pmatrix}
1&0\\
0&1
\end{pmatrix}.
$$

Thus

$$
W_2[Y]
=
\mathrm{Route}_2[Y]
\subsetneq
\operatorname{Path}_2(R_1[Y]).
$$

**Proof.** The direct-support matrix follows by applying the two permutations
to the two marked sectors. Boolean squaring gives the displayed full
$\operatorname{Path}_2$ relation. The four labelled words of length two
evaluate to either $I$ or $(0\ 1)$ because

$$
Y_a^2=Y_b^2=I,
\qquad
Y_aY_b=Y_bY_a=(0\ 1).
$$

Both represented operators preserve the two marked sectors, so $W_2[Y]$ is
diagonal. Proposition 5 gives the same relation for
$\mathrm{Route}_2[Y]$. $\square$

All data in this witness are exact: no tolerance, approximate rank, or
asymptotic enters. Thus aggregate support composition can overestimate actual
words even for permutation operators on a complete finite coordinate
partition.

### Promoted Conformance Certificate

The paper-owned certificate promotes only the static realization and
word-filtration claims needed here. Its accepted scope is:

| Family or control | Declared scope | Marked sectorization | Promoted role |
|---|---|---|---|
| modular permutation actions | $\mathbb P^1(\mathbb F_p)$ for $p=3,5,7,11,13,17$ | orbits of the declared $T$ operator | six exact conformance records |
| triangle-group permutation actions | signatures $(2,3,7)$, $(2,4,5)$, $(3,3,4)$ through index $7$ | separate $x$-, $y$-, and $z$-cycle partitions | seventeen actions and fifty-one marked realizations |
| four-state control | two labelled permutations on four states | one declared two-sector partition | strict Boolean-path overestimate witness |

Among the seventeen triangle records, twelve retain all three declared
signature orders and five are explicitly marked as proper-order-divisor
quotients. The bounded census contains three pairs of distinct labels with
equal represented permutation operators. All fifty-seven modular/triangle
marked realization--sectorization records carry complete finite
positive-closure receipts; no sector pair in those records remains
unreachable after saturation. The four-state hostile control carries its own
exact first-hit and finite-closure replay record.

The paper-owned conformance artifact and its validation receipt are
source-addressed in Appendix A. Their artifact IDs are `P8V2.1-CONFORMANCE`
and `P8V2.1-REPLAY`. The two exploratory source bundles remain provenance
inputs; they do not acquire Paper VIII evidence status independently of the
paper-owned promotion artifact and receipt.

This evidence is a **Computational Certificate**. The propositions above are
proved from the declared finite-action hypotheses and do not depend on the
census counts. Graph-Laplacian, spanning-tree, surface, Hecke, moduli, Selberg,
and automorphic fields are outside the promoted claim surface.

***

## Other Realization Classes

The following examples illustrate the broader source boundary. Except for the
promoted finite-permutation family above, they are not new computational
evidence for the theorem layer developed here.

The static object can be interpreted as a marked geometry of coarse-grained
information accessibility. The sectorization supplies source-dependent coarse
coordinates; labelled operator blocks, routed products, words, and any
independently registered Lie/Hall fields describe different forms of
cross-sector propagation. This interpretation does not identify their
carriers or make the sectorization canonical.

### Representation-Derived Sectors

Finite-group representations may supply invariant blocks or joint-spectral
projectors. The exact family above instead uses separately declared marked
state partitions and therefore does not claim that a representation selects
its own canonical SOF sectors. Rubik QT/HT sectors provide a motivating
realization, while their exact numerical status remains owned by the relevant
earlier papers.

### Geometry-Derived Sectors

Finite spectral triples may use block-diagonal Dirac operators to define
sectors. Mesh/interface partitions and other geometric decompositions provide
additional examples. The sectorization need not originate in irreducible
representation theory.

### State, Graph, and Activation Sectors

Finite Markov systems may use communicating classes or state flags. Graph
systems may use vertex, edge, color, or spectral sectors. Neural systems may
use activation or rank regions. In each case the observable family and the
sector provenance must be declared before a typed SOF audit is meaningful.

### External Sectorizations

An externally chosen coarse coordinate system is admissible when the
projectors, completeness, normalization, and observable family are explicit.
Such a choice is not automatically canonical or source-invariant.

***

## Claim Status and Boundary

The No-Sector No-Shadow Principle is a definitional structural principle.
Definitions are not evidence-level claims, so it is not assigned one of the
four statuses in the table.

Background facts used here include finite-dimensional $C^*$-algebra
semisimplicity and Wedderburn decomposition. They are standard results, not
reader-facing claims or contributions of this paper.

| Claim | Status |
|-------|--------|
| strict operator category and carrier-qualified Lie/Hall category | Theorem |
| operator/word support preservation and depth monotonicity | Theorem |
| Lie/Hall support preservation and depth monotonicity | Theorem |
| marked finite permutation realization | Theorem |
| permutation route/word coincidence | Theorem |
| exact finite positive-word saturation | Theorem |
| four-state Boolean path overestimate | Theorem |
| modular and bounded triangle-group conformance census | Computational Certificate |
| source-specific realization and equivalence criteria | Research Program |
| typed bridge criteria between operator/word and Lie/Hall branches | Research Program |
| weak and deformation morphism structures | Research Program |
| conditional low-order promotion and completion criteria | Research Program |

### What This Paper Does Not Claim

This paper does not claim:

1. a classification of all source systems admitting a SOF realization;
2. uniqueness of compatible sectorization;
3. a universal wall or deformation theory;
4. an unconditional relation between word depth and Lie depth;
5. a complete weak morphism category;
6. new numerical evidence for Rubik, quantum, Markov, graph, neural, or other
   application species outside the promoted exact finite-permutation family;
7. a canonical sectorization determined by a finite representation;
8. a Lie/Hall carrier induced from the promoted permutation letters;
9. generic strict separation of $A_Y^+$ and $A_Y^*$ from finite-group data;
10. a surface, Hecke, moduli, Selberg, or automorphic interpretation of the
    finite Schreier diagnostics.

The stable claim is narrower: once a compatible sectorization, a labelled
observable map, and any required filtration or Lie/Hall enrichment have been
declared, the resulting static typed constructions admit a strict object
language and carrier-qualified functoriality statements. Finite permutation
actions provide one exact marked conformance family, not a replacement for the
abstract object language.

***

## Conclusion

This paper fixes the static typed SOF object language. The marked
sectorization, possibly noninjective labelled operative map, observable
operator system, and
three multiplication closures remain distinct data. Routed products and full
words form one finite-filtration branch; an optional Lie/Hall carrier forms an
independently registered branch. Strict morphisms carry matched multiplication
closures by exact algebraic or $*$-isomorphisms, preserve matched witnesses,
and make target first-hit depths non-increasing, with equality reserved for
strict equivalence. For finite coordinate-sector permutation realizations, routed and
full-word support coincide, finite represented-image saturation decides exact
first-hit word depth, and aggregate Boolean paths may nevertheless strictly
overestimate actual words.

These results concern static objects and carrier-qualified functoriality. The
paper-owned modular, triangle-group, and four-state certificates are exact
conformance witnesses; they do not serve as premises for the theorem layer.
No deformation field, wall classification, compiler contract, or downstream
application report is introduced.

***

## Outlook

Paper IX takes a separately supplied object trajectory and studies its typed
SOF observation/deformation record. The underlying dynamics, parameter
update, or intervention supplies each object-state transition; observed
projectors, observables, and derived fields may vary along that trajectory.
Wall loci are typed discriminants of the observation/deformation record over
a declared admissible domain.
Paper VI supplies only a normality-gated spectral interface and pointwise
registrations; it is not a positive moving SOF theorem.

Paper X studies capability-aware compilation and Registry evidence through the
pipeline

$$
\begin{aligned}
\text{source and admission}
&\longrightarrow \text{Capability Manifest}
\longrightarrow \text{Typed SOF IR}\\
&\longrightarrow \text{Report Profile}
\longrightarrow \text{supported report claims}.
\end{aligned}
$$

The strict-admission branch factors through the static realization construction
of the present paper. The resulting pipeline is neither a universal accessibility
ladder nor a universal dynamics theorem. The Capability Manifest, Typed SOF
IR, and Report Profile belong to Paper X rather than to the static object
defined here.

Open promotion problems include proxy/shadow bridges, route/word criteria
beyond deterministic permutation carriers, and saturation certificates for
nonfinite or numerically represented operator families. Word/Lie comparisons
and weaker comparison morphisms are also open. These are future typed results,
not implicit consequences of the static category.

***

## Related Work and Novelty Boundary

Finite-dimensional representation theory and Wedderburn--Artin decomposition
provide the ambient structural background \cite{curtisReiner1962,serre1977,lam2001}.
The finite-dimensional $C^*$-algebra and operator-system terminology is
standard \cite{murphy1990cstar,paulsen2002}. The category language is standard
mathematical bookkeeping \cite{macLane1998}.

Papers IV--VII provide independent compatible interfaces: fixed spectral
arrangements, fixed typed accessibility objects, normality-gated linearized
registrations, and projected-composition incidence \cite{paper4,paper5,paper6,paper7}.
They are not premises that promote one typed carrier into another. In
particular, this paper does not identify a routed product with a full word or
a commutator with Lie depth.

The contribution here is the marked static SOF object language: sector
projectors remain marked, observable labels remain visible even when the
represented operator map is noninjective, finite filtrations remain separate
from positive, star, and sector-enriched closures, and optional Lie/Hall data
are independently registered. The exact finite-permutation family is a
conformance witness for that interface and a strict control against replacing
actual ordered words by aggregate Boolean graph powers.

***

## Appendix A: Computational Artifacts

The following repository artifacts support the finite-permutation conformance
certificate. The default directory is `experiments/paper8/`; paths are
relative to that directory.

| Artifact | Role | Short path |
|----------|-------------------|------------|
| A1 | exact modular finite-carrier source bundle | \path{../exploratory/carrier_realizations/fuchsian_schreier/results/modular_p1_census_v2.json} |
| A2 | exact bounded triangle-group source bundle | \path{../exploratory/carrier_realizations/fuchsian_schreier/results/triangle_low_index_census_v2.json} |
| A3 | paper-owned promotion and saturation replay | \path{validation/promote_marked_finite_realizations_v2_1.py} |
| A4 | conformance artifact, ID `P8V2.1-CONFORMANCE` | \path{results/v2.1/marked_finite_realization_conformance_v2_1.json} |
| A5 | fail-closed paper-owned replay validator | \path{validation/validate_marked_finite_realizations_v2_1.py} |
| A6 | validation receipt, ID `P8V2.1-REPLAY` | \path{results/v2.1/marked_finite_realization_conformance_v2_1.validation-receipt.json} |
| A7 | human-readable projection of A4 | \path{results/v2.1/marked_finite_realization_conformance_v2_1.md} |

From the repository root, run:

```bash
cd experiments/paper8
python validation/promote_marked_finite_realizations_v2_1.py
python validation/validate_marked_finite_realizations_v2_1.py --write-receipt
```

The promotion and validation steps replay the two source bundles, reconstruct
the paper-owned certificate, and bind the resulting receipt to the declared
source and implementation digests.
