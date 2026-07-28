# Sectorized Observable Framework

### A Sectorized Observable Architecture for Spectral Accessibility

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part VIII of the RIME program. Papers IV--VII form an
accessibility cycle: fixed spectral geometry, accessibility
calculus, accessibility deformation, and composition incidence. Paper VIII begins
the object layer. Its purpose is to identify the mathematical object on which
the RIME observables naturally live.*

***

## Abstract

**Problem.** Papers IV--VII repeatedly introduce structures of the same form:
sectors, observable families, projected blocks, support shadows, commutator
shadows, accessibility depth, jets, walls, and promotion limits. The
structural question is therefore not only what these objects do, but what
object they are attached to.

**Approach.** We define the **Sectorized Observable Framework** (SOF) as an
analysis paradigm and language for sectorized observables derived from a
chosen space, sectorization, and observable family. A finite SOF is a triple

$$
\mathcal F=(V,\{Q_i\}_{i\in I},\mathcal X),
$$

where $V$ is a finite-dimensional Hilbert space, $\{Q_i\}$ is a finite
orthogonal sector decomposition, and $\mathcal X$ is a finite observable
family. We then define strict SOF morphisms, the category
$\mathsf{SOF}_{\mathrm{str}}$, and the natural accessibility constructions
$R_1$, $R_2$, $D$, and $\mathcal J_{\mathrm{acc}}$.

**Results.** The main result is a naturality theorem: the RIME accessibility
observables are canonical constructions on SOF data. Under strict SOF
equivalences they are preserved exactly. Under strict embeddings they are
preserved on the embedded image, with first-depth accessibility satisfying the
expected monotonicity. Spectral charts and accessibility walls are likewise
natural once the corresponding smooth spectral SOF family has been specified.

**Implications.** Paper VIII marks the transition from result-oriented papers
to object-oriented theory. Papers IV--VII discovered and tested the
observable ladder. Paper VIII identifies the object on which the ladder is
natural. Rubik, quantum gates, Markov systems, graph systems, and Yang-like
filtration systems are then different instances of the same sectorized
observable architecture rather than separate theories. The principal contribution
of this paper is not a new accessibility invariant, but the identification of
a common analysis paradigm in which the accessibility observables of the
previous papers arise as natural constructions.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $V$ | finite-dimensional complex Hilbert space |
| $Q_i$ | orthogonal sector projector |
| $\{Q_i\}_{i\in I}$ | finite sector decomposition, $\sum_i Q_i=I$ |
| $\mathcal X=\{X_a\}_{a\in A}$ | finite observable family |
| $\mathcal F=(V,\{Q_i\},\mathcal X)$ | Sectorized Observable Framework |
| $B^a_{ij}=Q_iX_aQ_j$ | projected block field |
| $C^{a,b}_{ij}=Q_i[X_a,X_b]Q_j$ | projected commutator field |
| $R_1$ | projected support shadow |
| $R_2$ | projected commutator-survival shadow |
| $D$ | first-depth accessibility shadow |
| $\mathcal J_{\mathrm{acc}}$ | accessibility jet package |
| $\Sigma_{\mathrm{spec}}$ | normal spectral chart where spectral projectors vary coherently |
| $\Sigma_{\mathrm{access}}$ | accessibility discriminant where the discrete shadow changes |
| $\mathsf{SOF}_{\mathrm{str}}$ | category of finite SOFs with strict morphisms |

***

## Introduction

What is the mathematical object studied by the RIME program?

The Papers IV--VII accessibility cycle has now closed:

| Paper | Layer | Question |
|-------|-------|----------|
| Paper IV | fixed spectral geometry | How are spectral layers formed by projection? |
| Paper V | accessibility calculus | How is accessibility computed once sectors exist? |
| Paper VI | accessibility deformation | How do sectors and accessibility data move? |
| Paper VII | incidence geometry | When do projected factors compose? |

These papers follow a common pattern:

discover a structure $\to$ define an observable $\to$ compute examples
$\to$ isolate a conjecture or theorem layer.

Paper VIII changes the direction. It starts from the object:

define SOF $\to$ define morphisms $\to$ define observable functors
$\to$ reinterpret previous RIME structures as natural constructions.

The answer is not "Rubik." Rubik is the finite laboratory. The answer is not
"semisimple representation theory." Wedderburn-Artin decomposition and
standard finite representation theory supply the structural layer
\cite{curtisReiner1962,serre1977,lam2001}, but RIME studies what happens
above that layer. The object is the **sectorized observable architecture** obtained
after one has chosen sectors and observables.

The guiding invariant is:

Spectral geometry determines the objects. Compatible sectorization is the
interface. Observable geometry is the invariant. Accessibility geometry
determines their behavior. Genericity determines why the behavior is stable.

The conceptual architecture is:

| Layer | Role |
|-------|------|
| Structural Unity | Wedderburn--Artin block decomposition |
| Compatible sectorization | interface from source data to SOF data |
| Transport Unity | natural RIME observables on SOF data |

Paper VIII develops the third line as an object theory. It does not introduce
a new physical model; it fixes the analysis paradigm in which different
sectorized systems can be compared. The categorical language used below is
standard \cite{macLane1998}; the new point is the SOF-specific choice of
objects, morphisms, and accessibility observables.

### Applicability Boundary

Paper VIII distinguishes two applicability levels at the formal object layer.
**Definitional applicability** means that an explicit finite triple
$\mathcal F=(V,\{Q_i\},\mathcal X)$ satisfying the SOF axioms has been supplied.
**Realizational applicability** means that a source system has been mapped to
such a triple by an explicit and reproducible choice of finite space,
sectorization, and observable family. The second level must state whether the
realization is canonical, constructed, truncated, or non-unique.
Different realizations of the same source system need not be equivalent as
SOF objects, and any equivalence claim requires a separate morphism-level
argument.

These levels describe proximity to the formal SOF core; they do not determine
the strength of a claim. A definitionally valid SOF may still support only a
computational diagnostic, while a realization theorem requires a separate
proof. Report-level and heuristic uses lie outside the theorem layer of Paper
VIII. Paper XII extends this boundary to diagnostic applicability, where
stable probe sectors and measurable outputs can support a qualified report
without a strict projector realization, and to analogical applicability,
where only heuristic language is permitted.

***

## Sectorized Observable Framework

### SOF Definition

A finite **Sectorized Observable Framework** is a triple

$$
\mathcal F=(V,\{Q_i\}_{i\in I},\mathcal X),
$$

where:

1. $V$ is a finite-dimensional complex Hilbert space;
2. $\{Q_i\}_{i\in I}$ is a finite orthogonal projector decomposition,

$$
Q_iQ_j=\delta_{ij}Q_i,\qquad \sum_{i\in I}Q_i=I;
$$

3. $\mathcal X=\{X_a\}_{a\in A}$ is a finite observable family on $V$.

The observables may be logarithmic generators, unitary representation
operators, averaged operators, transfer operators, adjacency or Laplacian
operators, rate operators, or filtration observables. Their origin is not part
of the definition.

![SOF object. A Sectorized Observable Framework is the realized triple
$(V,\{Q_i\},\mathcal X)$ obtained after choosing a space, sector projectors,
and observable family. Once this data is fixed, projected blocks,
commutator blocks, and accessibility shadows are SOF-intrinsic constructions.](../../figures/paper8/fig1_sof_definition.png)

**Remark (Origin of the sectorization).** The source of the projectors is also
not part of the SOF definition. A sectorization may be representation-derived,
geometry-derived, filtration-derived, activation-derived, or externally chosen.
Examples include Wedderburn--Artin blocks, joint spectral projectors,
block-diagonal Dirac sectors, mesh or interface partitions, reachable-state
flags, color-class projectors, and activation regions. SOF begins after such a
compatible sectorization has been supplied. Its constructions depend on the
projectors and observables, not on the origin of the projectors.

The basic block field is

$$
B^a_{ij}=Q_iX_aQ_j.
$$

The SOF is therefore the data needed to talk about projected observable
transport.

### Why Sectorization Is Necessary

One may ask why the pipeline is not simply

representation $\to$ observable family.

The reason is that the RIME observables are not global observables of
$\mathcal X$ alone. They are **projected** observables. Their basic unit is the
sector-to-sector block

$$
Q_iX_aQ_j.
$$

Without the projectors $\{Q_i\}$, there is no intrinsic meaning to:

1. support from sector $i$ to sector $j$;
2. a bridge through an intermediate sector;
3. a frozen pair that can later be repaired;
4. a first-depth matrix $D(i,j)$;
5. an accessibility wall where one of these sector shadows changes.

Thus sectorization is not decoration. It is the interface that makes the
observable shadows visible.

![Sectorization necessity. Without sector projectors there are global
observables but no sector-indexed support, bridge, repair, or wall shadows.
With sectors, the projected blocks $Q_iX_aQ_j$ define the observable architecture
used by $R_1$, $R_2$, $D$, and $\mathcal J_{\mathrm{acc}}$.](../../figures/paper8/fig2_no_sector_no_shadow.png)

### Proposition 1 (No-Sector No-Shadow Principle)

Let $V$ be a finite-dimensional space with an observable family
$\mathcal X=\{X_a\}$.  If no sectorization $\{Q_i\}$ is specified, then the
sector-indexed RIME shadows $R_1$, $R_2$, $D$, and
$\mathcal J_{\mathrm{acc}}$ are not defined.  If the only sectorization is the
trivial one $\{I\}$, then the off-diagonal sector-to-sector shadows are
degenerate: there are no distinct sector pairs, no bridge products, and no
nontrivial frozen-to-accessible repair.

### Proof

Each construction uses the projected blocks $Q_iX_aQ_j$ as input. Without
projectors there are no indices $i,j$ and no projected blocks. With the trivial
one-sector projector $I$, all blocks have source and target equal to the single
sector, so the cross-sector support, bridge, repair, and wall shadows collapse.
The claim is therefore a definitional necessity statement, not an additional
classification theorem.

### Compatible Sectorization Realization

A source system enters the SOF language only after the following data have
been specified:

1. a finite-dimensional space $V$;
2. a compatible sectorization $\{Q_i\}$;
3. a source of observables, such as a representation, generator family,
   averaging family, transition operator, graph operator, Dirac operator,
   control operator, mesh operator, or filtration observable;
4. a chosen extraction rule producing $\mathcal X$.

Represented systems are the main RIME source, but they are not the only
possible source.  The same realization step applies to sectorizations coming
from geometry, state filtrations, activation regions, control flags, mesh
partitions, graph colorings, or externally chosen coarse coordinates.

### Theorem 1 (Sectorized Realization Theorem)

Every finite source system endowed with a compatible sectorization and a
chosen observable extraction rule induces an SOF

$$
\mathcal F=(V,\{Q_i\},\mathcal X),
$$

canonical relative to those choices.

Moreover, every static algebraic construction formed from the projectors,
observables, and finite algebraic operations on them is an SOF-intrinsic
construction after realization. Depth, wall, rate, repair, and plateau
diagnostics are relative constructions: they become intrinsic only after the
relevant filtration, deformation, threshold, or diagnostic rule has also been
specified.

### Proof

The chosen sectorization supplies the projectors $\{Q_i\}$ and the extraction
rule supplies the observable family $\mathcal X$. Together with $V$, these are
exactly the SOF data. Any block, commutator block, word block, Lie block, jet,
or rank/support condition built from them depends only on
$(V,\{Q_i\},\mathcal X)$ after realization, together with the explicitly
supplied filtration or smooth-family data when such data are required. It no
longer depends on the native coordinates or origin of the source species.

### Morphisms

Let

$$
\mathcal F=(V,\{Q_i\}_{i\in I},\{X_a\}_{a\in A})
$$

and

$$
\mathcal F'=(V',\{Q'_{i'}\}_{i'\in I'},\{X'_{a'}\}_{a'\in A'}).
$$

A **strict SOF morphism**

$$
\Phi:\mathcal F\to\mathcal F'
$$

consists of:

1. an isometric linear embedding $U:V\to V'$;
2. an injective sector map $f:I\to I'$ satisfying

$$
UQ_i=Q'_{f(i)}U;
$$

3. an injective observable-label map $\phi:A\to A'$ satisfying

$$
UX_a=X'_{\phi(a)}U
\qquad \text{for all }a\in A.
$$

A strict SOF morphism is a **strict SOF equivalence** if $U$ is unitary and
$f,\phi$ are bijections.

This is intentionally a strong notion. Weaker comparison notions, such as
support-preserving maps or depth-equivalences, are useful but do not preserve
all natural constructions strictly.

![Strict SOF morphism. A strict morphism consists of a linear embedding,
sector map, and observable-label map satisfying the corresponding intertwining
relations. Naturality of the accessibility ladder follows because projected
blocks and shadows are preserved on the image.](../../figures/paper8/fig3_strict_morphism.png)

### Category $\mathsf{SOF}_{\mathrm{str}}$

Finite SOFs with strict SOF morphisms form a category
$\mathsf{SOF}_{\mathrm{str}}$.

The identity morphism is $(I_V,\mathrm{id}_I,\mathrm{id}_A)$. Composition is
given by composing the linear embeddings, sector maps, and observable-label
maps. The intertwining equations are stable under composition, so the result
is again a strict SOF morphism.

The equivalences in this category are precisely the strict SOF equivalences.

### Claim-Status Boundary

This paper uses the strict category to make naturality precise. It does not
claim that every meaningful comparison of SOF objects is strict. Later work
in the applications/universality layer requires weaker morphisms, quotient
morphisms, transport morphisms, and functorial comparison classes.

In particular, the deformation maps used in the dynamic layer are not strict
SOF morphisms in general. A generator-weight path, a state-mixing path, or a
training trajectory may preserve only the observable diagnostics, not an
isometric embedding together with sector and observable-label injections. The
appropriate home for such arrows is a weaker deformation category, denoted
provisionally by $\mathsf{SOF}_{\mathrm{def}}$, whose morphisms are
parameterized SOF families equipped with enough comparison data to evaluate
observable trajectories. Paper VIII does not develop this category; it fixes
the strict static category against which the later weak theory can be
measured.

The status of the main constructions is:

| Item | Claim status |
|------|--------------|
| SOF definition | definition |
| No-Sector No-Shadow Principle | definitional necessity: sector-indexed shadows require projectors |
| sectorized realization theorem | formal realization relative to chosen sectorization and extraction rule |
| strict morphisms and $\mathsf{SOF}_{\mathrm{str}}$ | structural bookkeeping category |
| weak/deformation morphisms $\mathsf{SOF}_{\mathrm{def}}$ | named dynamic gap, developed only provisionally in Paper IX |
| $R_1/R_2/D/\mathcal J_{\mathrm{acc}}$ | natural constructions on SOF data once a filtration or smooth family is fixed |
| cross-species examples | illustrative examples, not new computational evidence |
| low-order promotion | open typed problem; Paper VII proves only matrix-pair incidence and rank protection |

***

## Natural Accessibility Objects

The natural accessibility ladder of an SOF is:

$$
\mathcal F
\longrightarrow B
\longrightarrow R_1
\longrightarrow R_2
\longrightarrow D
\longrightarrow \mathcal J_{\mathrm{acc}},
$$

with $\Sigma_{\mathrm{spec}}$ and $\Sigma_{\mathrm{access}}$ added when a
smooth spectral family is supplied.

### R1 Support Shadow

Define

$$
R_1(i,j;a)=1
\quad\Longleftrightarrow\quad
Q_iX_aQ_j\ne0.
$$

This is the generator-labelled support graph of the SOF.

### R2 Commutator-Survival Shadow

Define

$$
R_2(i,j;a,b)=1
\quad\Longleftrightarrow\quad
Q_i[X_a,X_b]Q_j\ne0.
$$

This records projected relation-level survival. Paper V shows that $R_2$ is
not determined by $R_1$ in general \cite{paper5}.

### Depth Shadow D

Choose a filtration $\mathcal H^{(d)}(\mathcal X)$: Lie monomials, PBW
monomials, word monomials, transfer iterates, or another specified
depth-producing family. Define

$$
D(i,j)=\min\{d:Q_iYQ_j\ne0
\text{ for some }Y\in\mathcal H^{(d)}(\mathcal X)\},
$$

with $D(i,j)=\infty$ if no such $d$ exists.

Depth is therefore filtration-relative. The SOF supplies the object layer; the
filtration supplies the depth convention.

### Accessibility Jet

For a smooth SOF family

$$
\mathcal F(w)=(V,\{Q_i(w)\},\mathcal X(w)),
$$

the accessibility jet is the package

$$
\mathcal J_{\mathrm{acc}}(w)
=
(J_{\mathrm{block}},J_{\mathrm{comm}},J_{\mathrm{depth}}),
$$

where these components record first-order variation of projected blocks,
projected commutators, and depth-producing propagation data.

This definition becomes theorem-level only after the admissible smooth family,
projector chart, and filtration rule are specified. Paper VI supplies the
Rubik generator-set instance on normal spectral charts \cite{paper6}.

### Spectral and Accessibility Discriminants

For a smooth spectral SOF family, the spectral chart
$\Sigma_{\mathrm{spec}}$ is the domain where the sector projectors and
spectral arrangement vary coherently. The accessibility discriminant
$\Sigma_{\mathrm{access}}$ is the locus where the discrete shadow of the
accessibility jet changes.

In Paper VI language:

$$
\Sigma_{\mathrm{access}}
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}.
$$

These loci are not part of every SOF. They are natural objects of SOF families
with the required spectral and smooth structure.

***

## Functoriality

### Observable Functors

On $\mathsf{SOF}_{\mathrm{str}}$, the support construction gives a functor

$$
\mathsf R_1:\mathsf{SOF}_{\mathrm{str}}\to
\mathsf{Graph}_{\mathrm{lab}},
$$

where vertices are sectors and labelled edges record nonzero projected blocks.

Similarly, the commutator-survival construction gives a labelled hypergraph
or tensor-valued shadow

$$
\mathsf R_2:\mathsf{SOF}_{\mathrm{str}}\to
\mathsf{Rel}_{\mathrm{comm}}.
$$

After choosing a filtration class, the depth construction gives a partial
functor or pseudofunctor to extended distance matrices:

$$
\mathsf D:\mathsf{SOF}_{\mathrm{str}}^{\mathcal H}\to
\mathsf{Mat}_{\mathbb N\cup\{\infty\}}.
$$

For smooth families, the jet construction gives

$$
\mathsf J_{\mathrm{acc}}:
\mathsf{SOF}_{\mathrm{str}}^{\mathrm{sm}}
\to
\mathsf{Jet}_{\mathrm{acc}}.
$$

The targets are intentionally schematic. Their full functorial formalization
belongs to later SOF theory; Paper VIII uses them only to identify the natural
output types of the strict object theory.

### Main Theorem

### Theorem 2 (Naturality of Accessibility Observables)

Let $\Phi=(U,f,\phi):\mathcal F\to\mathcal F'$ be a strict SOF morphism.
Then:

1. $R_1$ is preserved on the image:

$$
R_1(i,j;a)=1
\quad\Longrightarrow\quad
R'_1(f(i),f(j);\phi(a))=1.
$$

2. $R_2$ is preserved on the image:

$$
R_2(i,j;a,b)=1
\quad\Longrightarrow\quad
R'_2(f(i),f(j);\phi(a),\phi(b))=1.
$$

3. For any compatible filtration $\mathcal H$, first-depth accessibility is
monotone on the image:

$$
D'(f(i),f(j))\le D(i,j),
$$

provided the target filtration contains the image of the source filtration
under $\phi$.

4. If $\Phi$ is a strict SOF equivalence, then all implications above are
equivalences and

$$
D'(f(i),f(j))=D(i,j).
$$

5. For smooth strict equivalences of SOF families, the accessibility jet is
natural:

$$
\mathcal J'_{\mathrm{acc}}(f(i),f(j))
=
U\,\mathcal J_{\mathrm{acc}}(i,j)\,U^{-1}
$$

in the corresponding sector and observable labels. Consequently
$\Sigma_{\mathrm{spec}}$ and $\Sigma_{\mathrm{access}}$ are carried to the
corresponding discriminants of the equivalent family.

### Proof

The intertwining relations give

$$
UQ_iX_aQ_j
=
Q'_{f(i)}X'_{\phi(a)}Q'_{f(j)}U.
$$

Since $U$ is injective, a nonzero source block maps to a nonzero target block
on the embedded image. This proves preservation of $R_1$.

For commutators,

$$
U[X_a,X_b]=[X'_{\phi(a)},X'_{\phi(b)}]U,
$$

so the same block-intertwining argument proves preservation of $R_2$.

For depth, every source filtration element $Y\in\mathcal H^{(d)}(\mathcal X)$
maps to the corresponding target filtration element $Y'$ of depth at most
$d$. Hence a source witness of depth $d$ gives a target witness of depth at
most $d$. This proves monotonicity.

If $\Phi$ is a strict equivalence, the inverse morphism gives the reverse
implications and the reverse depth inequality, hence equality.

For smooth families, differentiating the block and commutator intertwining
relations gives the jet identity. Rank/support discriminants are defined by
failure of local constancy of these shadows, so strict equivalence carries
them to the corresponding discriminants.

### Boundary of the Theorem

The theorem is a naturality statement, not a generic completion theorem. It
does not say that $(R_1,R_2)$ determines $D$ for all SOFs. It says that
$R_1$, $R_2$, $D$, jets, and the corresponding discriminants are natural
constructions once the SOF and the relevant filtration or smooth family are
fixed.

***

## Examples

### Rubik

The Rubik laboratory gives the motivating SOF. The sectors are the nine QT/HT
joint-spectral sectors. The observable families include face-turn logarithmic
generators, QT/HT averages, and the canonical averaging operator. This single
SOF instance supports several independent Rubik papers and the Papers IV--VII
accessibility cycle.

### Quantum Gate Systems

For a small quantum gate system, $V=(\mathbb C^2)^{\otimes q}$ and the
sectors may be computational-basis projectors. Observable families are
obtained from logarithmic gate generators. The Pauli, Clifford, and
Universal+CNOT diagnostics show that $R_1/R_2/D$ are sectorized observables,
not Rubik-specific quantities. These are worked examples for the SOF language;
the computational evidence itself belongs to Paper VII and later diagnostic
notes, not to the theorem layer of Paper VIII.

### Markov Systems

For a Markov chain, $V$ is a finite state space, sectors may be state
projectors or communicating-class projectors, and observables may be rate
operators, logarithmic transition operators, or transfer operators. These
examples test portability of the SOF audit interface, not generic completion.

### Graph Systems

For a graph, $V$ is a vertex or edge space. Sectors may be vertex sectors,
spectral sectors, or symmetry-adapted sectors. Observables may include
adjacency matrices, Laplacians, directed-edge operators, or walk operators.
The graph examples demonstrate that the SOF language is not restricted to
group representations.

### Yang-Like Filtration Systems

Yang-like systems are naturally treated as Filtration SOF examples. Their
deformation variable is state mixing or coherence variation. This produces
filtration degeneration rather than the generator-weight accessibility walls
of Paper VI. The shared feature is a common observable architecture, not a
shared wall geometry.

***

## Previous RIME Papers Revisited

### Paper IV

Paper IV studies a spectral SOF shadow \cite{paper4}. The QT/HT joint spectrum is a finite
sectorized spectral arrangement, and the six canonical spectral layers arise
as a collision quotient under affine projection. In SOF language, Paper IV is
the fixed spectral geometry of one sectorized observable family.

### Paper V

Paper V studies accessibility calculus on a fixed SOF \cite{paper5}. The objects $R_1$,
$R_2$, and $D$ are natural shadows of projected block data. Commutator
cancellation and image--kernel incidence are local mechanisms inside this
fixed SOF calculus, not universal accessibility types.

### Paper VI

Paper VI studies smooth SOF families on normal spectral charts \cite{paper6}. The
accessibility jet $\mathcal J_{\mathrm{acc}}$ is the continuous object behind
the discrete shadows $R_1$, $R_2$, and $D$. The walls are discriminants of
these shadows under generator-set deformation.

### Paper VII

Paper VII studies image--kernel incidence and rank protection for projected
operator composition \cite{paper7}. It separates routed-product geometry from
stronger word, commutator, and Lie-depth promotion questions.

Thus the earlier papers are not patches of one another. They are examples of
natural SOF structures at different levels: spectral shadow, accessibility
calculus, deformation, and incidence geometry.

***

## Outlook

### Low-Order Promotion

The typed promotion problem remains a theorem program:

When does $(R_1,R_2)$ determine $D$?

Paper VII does not answer this question. It identifies image--kernel incidence
and rank protection at the routed-product layer, while route-to-word,
word-to-commutator, and low-order-to-depth promotions remain open. Paper VIII
provides the observable architecture in which typed versions of those questions
can be asked.

### Wall Theory

SOF does not prescribe a universal wall theory. It provides the sectorized
observable architecture in which different deformation geometries produce
different walls:

| Branch | Deformation variable | Wall or degeneration |
|--------|----------------------|----------------------|
| Spectral SOF | affine projection / spectral parameter | collision and spectral walls |
| Accessibility SOF | generator weights / observable-family deformation | accessibility walls |
| Filtration SOF | state mixing / coherence variation | filtration degeneration |

### Future SOF Program

The next program stages are:

| Paper | Program stage |
|-------|---------------|
| Paper IX | observable dynamics, deformation geometries, wall discriminants |
| Paper X | SOF registry, cross-species observable diagnostics, and universality |

Paper VIII fixes the object architecture. Paper IX studies how SOF observables
evolve after a deformation geometry is chosen. The bridge between the two is
not the strict category $\mathsf{SOF}_{\mathrm{str}}$, but the weaker
deformation-category viewpoint $\mathsf{SOF}_{\mathrm{def}}$: a deformation is
an arrow only after one specifies the comparison data by which observables are
tracked along the path. Paper X tests the architecture through the SOF Registry
and cross-species observable diagnostics.

### What This Paper Does Not Claim

This paper does not claim:

1. a complete theory of weak SOF morphisms;
2. a universal wall theory for all SOFs;
3. unconditional $(R_1,R_2)\to D$ completion;
4. uniqueness of natural sectorization for every source system;
5. equivalence between Yang-like filtration walls and RIME accessibility
   walls.

The stable claim is narrower and foundational: the RIME observables are
natural constructions on SOF data.

***

## References

**Program lineage.** Paper VIII depends on Papers IV--VII. Paper IV supplies
the fixed spectral shadow \cite{paper4}; Paper V supplies the accessibility
calculus \cite{paper5}; Paper VI supplies deformation and jets \cite{paper6};
Paper VII supplies incidence geometry and promotion limits \cite{paper7}.

**External background.** Many RIME examples use standard finite-dimensional
representation theory and Wedderburn-Artin decomposition
\cite{curtisReiner1962,serre1977,lam2001}. SOF is not a replacement for that
decomposition. It is the sectorized observable architecture built once a
compatible sectorization and observable family have been supplied. The strict
morphism language is categorical bookkeeping in the standard sense
\cite{macLane1998}.
