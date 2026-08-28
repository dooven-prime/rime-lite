# Finite Typed Context Descent
### Semantic Visibility, Relational Acyclicity, and Comparison Reconstruction

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper is Paper XXIV of the RIME program. It develops a finite
local-to-global theory for typed section and relation data and applies
object-appropriate reconstruction gates to fixed-alignment comparison.*

## Abstract

**Problem.** Finite structural records are often observed through overlapping typed
contexts. Equality on every local context need not imply global equality when
the contexts cover labels but omit relational coordinates. Even after all
coordinates are covered, local admissibility checks may fail to imply global
admissibility when the visible constraints do not semantically entail the full
constraint package. Relation-valued local data introduce a different
obstruction: pairwise-consistent local relations need not admit a global
relation when the context hypergraph is cyclic.

**Approach.** A context is modeled as a finite typed atom set with
definedness-sensitive partial sections. The construction separates label
coverage, relation-coordinate coverage, type and convention guards, and
overlap compatibility. For a global constraint package $Q_C$, the visible
package $Q_{\mathcal U}$ records exactly the constraints whose scopes occur in
some patch. Relation-valued descent is treated as a different local object
type and is composed with the classical Beeri--Fagin--Maier--Yannakakis
acyclicity characterization.

**Results.** Free sections are separated exactly when every admissible
difference support meets the observed coordinates, and a full coordinate
cover gives unique gluing. The equalizer of locally admissible sections is the
global model space of $Q_{\mathcal U}$, so full constrained descent holds
exactly when $Q_{\mathcal U}\models_{A_C}Q_C$. Under universal quantification
over independently interpreted scope predicates, full admissible descent is
equivalent to visibility of every declared scope.
For relation-valued local data, universal admissible descent holds exactly
when scope visibility is combined with an $\alpha$-acyclic context hypergraph.
These object-appropriate gates yield a fixed-alignment comparison
reconstruction theorem. Exact `UNSEEN_SCOPE` and `CYCLIC_CONTEXT_CORE`
fixtures separate the two failure modes.

**Boundary.** The standard separatedness, free-equalizer, and relational
acyclicity results are not claimed as new. The contribution is the typed
semantic-visibility interface, its composition with the imported relational
obstruction, and its propagation into comparison reconstruction. No
Grothendieck topology, arbitrary-presheaf descent theorem, causal inference,
or universal comparison theorem is claimed.

## Notation Table

| Symbol | Meaning |
|---|---|
| $C=(A_C,\tau_C,\theta_C)$ | finite typed context |
| $u_i:C_i\to C$ | canonical restriction |
| $A_i$ | ambient image of the atoms retained by patch $i$ |
| $O_{\mathcal U}$ | union of all observed atom sets $A_i$ |
| $F_{\mathrm{free}}(C)$ | definedness-sensitive free typed sections on $C$ |
| $G$ | declared class of global sections |
| $Q_C$ | global constraint package |
| $Q_{\mathcal U}$ | constraints visible in at least one patch |
| $H_{\mathcal U}$ | context hypergraph with edges $A_i$ |
| $R_i$ | relation-valued local object on $A_i$ |
| $\bowtie_iR_i$ | natural join of the local relations |
| $\Phi,\Theta$ | fixed alignment and comparison-semantics packages |

## Introduction

This paper proves finite statements about explicit typed coordinate sets. It
does not claim a Grothendieck topology, a topos-level result, descent for
arbitrary presheaves, or a universal comparison theorem. In particular,

$$
\begin{aligned}
\text{label coverage}&\ne\text{relation-coordinate coverage},\\
\text{separatedness}&\ne\text{existence},\\
\text{free gluing}&\ne\text{constrained gluing},\\
\text{section-valued descent}&\ne\text{relation-valued descent},\\
\text{local comparison compatibility}&\ne\text{causal attribution}.
\end{aligned}
$$

Theorems 3 and 4 instantiate standard mathematical patterns: joint monicity
of restriction families and equalizer gluing for finite coordinate products.
They are not claimed as new universal sheaf theorems. The contribution lies
in the following combined interface:

1. signatures are typed partial maps whose definedness is part of equality;
2. relation-coordinate coverage is checked independently of label coverage;
3. fixed-package section descent is characterized by semantic entailment from
   the visible constraint package;
4. uniform section descent is separated from the imported $\alpha$-acyclic
   criterion for relation-valued local objects;
5. two `AB`/`BC`/`AC` controls isolate semantic-visibility and cyclic-relation
   failures;
6. the resulting object-appropriate descent gates are exposed for contextual
   comparison and finite audit reconstruction without importing causal or
   action semantics.

The main theorem spine is

$$
\boxed{
\begin{aligned}
&\text{Free Section Gluing}\\
&\to \text{Exact Admissible-Section Characterization}\\
&\to \text{Universal Scope-Visibility Corollary}\\
&\to \text{Imported Relational Acyclicity Theorem}\\
&\to \text{Typed Relational Admissible-Descent Characterization}\\
&\to \text{Comparison Reconstruction}.
\end{aligned}}
$$

### Scope and Positioning

This paper studies finite local-to-global conditions for restriction,
separatedness, and gluing. Paper XIII supplies the motivating comparison
interface \cite{paper13}, but is an application source rather than a premise
of the theorems below. Conversely, these descent theorems do not validate or
promote a Paper XIII comparison.

This line isolates a recurring structural question. Given an operation
$T:X\to X$ and a lossy map $q:X\to Y$, an operation on $Y$ represents $T$ only
when some well-defined $\bar T:Y\to Y$ makes

$$
q\circ T=\bar T\circ q.
$$

Failure of injectivity alone neither proves nor disproves such descent; the
issue is whether the structure is compatible with the information identified
by $q$. Here the maps are finite contextual restrictions, and the theorems
state explicit coordinate-coverage and constraint-scope conditions under
which separation, gluing, or comparison reconstruction is justified.

## Typed Contexts and Signatures

### Contexts

Fix a universe of typed atoms. A finite typed context is

$$
C=(A_C,\tau_C,\theta_C),
$$

where $A_C$ is a finite set of declaration atoms, $\tau_C(a)$ is the payload
type of atom $a$, and $\theta_C$ is a fixed convention package. Atoms may
represent sector values, observable values, typed incidences, word-support
coordinates, or convention guards when those guards vary as section data.
Guards fixed by $\theta_C$ index the context and are not duplicated as
section coordinates.

A canonical restriction $u:C'\to C$ is an injective type-preserving atom map

$$
u_\#:A_{C'}\hookrightarrow A_C
$$

that preserves the declared convention package. Identity and composition are
the corresponding identity and composite injections.

> **Theorem 1 (Finite Typed-Context Category).** Finite typed contexts and
> canonical restrictions form a category $\mathcal C_{\mathrm{tctx}}$.

*Proof.* Identity atom maps are injective and preserve types and conventions.
Composites of injective type-preserving maps have the same properties.
Associativity and the identity laws follow from function composition.
$\square$

### Free Typed Signatures

Let $V_a$ be the payload set declared by $\tau_C(a)$. A free typed signature
section on $C$ is a dependent partial map

$$
s\in F_{\mathrm{free}}(C)
  :=\prod_{a\in A_C}\operatorname{Option}(V_a).
$$

The value `none` means that the coordinate is not defined in the section; it
is not a numerical zero. Restriction along $u:C'\to C$ is precomposition with
$u_\#$:

$$
F_{\mathrm{free}}(u)(s)(a)=s(u_\#a).
$$

> **Theorem 2 (Restriction Functor).** The assignment
> $F_{\mathrm{free}}:\mathcal C_{\mathrm{tctx}}^{op}\to\mathbf{Set}$ is a
> contravariant functor.

*Proof.* Precomposition by an identity atom map is the identity. Precomposition
by a composite equals successive precomposition in reverse order. Payload
types and convention guards are preserved by the morphism obligations.
$\square$

This theorem is specific to canonical restriction. Resolution refinement,
aggregation, alignment, and convention conversion require separately typed
maps and are not silently admitted as context morphisms.

## Separating Covers

Let

$$
\mathcal U=\{u_i:C_i\to C\}_{i=1}^m
$$

be a nonempty finite family of canonical restrictions, with $m\ge 1$. Its
observed atom set is

$$
O_{\mathcal U}=\bigcup_{i=1}^m (u_i)_\#A_{C_i}\subseteq A_C.
$$

For two sections define their difference support, including defined/undefined
differences, by

$$
\Delta(s,t)=\{a\in A_C:s(a)\neq t(a)\}.
$$

Four checks must remain distinct for any theorem application:

1. **label coverage:** the underlying sector/observable labels are jointly
   retained;
2. **relation-coordinate coverage:** $O_{\mathcal U}$ contains every typed
   atom on which the relevant global section class may differ;
3. **type/convention guards:** every $u_i$ preserves payload types and the
   declared convention package, as required by a canonical restriction;
4. **overlap compatibility:** the particular local family agrees in both
   payload and definedness on every $A_i\cap A_j$.

The first and third properties concern the declared context family, the second
concerns its section-separating power, and the fourth concerns a supplied local
family. None is inferred from another.

For a declared global section class $G\subseteq F_{\mathrm{free}}(C)$, call
$\mathcal U$ **$G$-separating** when the restriction map

$$
\rho_{\mathcal U}:G\longrightarrow\prod_iF_{\mathrm{free}}(C_i)
$$

is injective.

> **Theorem 3 (Separating-Cover Characterization).** A finite context family
> $\mathcal U$ is $G$-separating if and only if
> $$
> \forall s\neq t\in G,\qquad
> \Delta(s,t)\cap O_{\mathcal U}\neq\varnothing.
> $$

*Proof.* If the intersection contains $a$, choose a patch containing $a$.
The two restrictions differ at its local representative, so
$\rho_{\mathcal U}(s)\neq\rho_{\mathcal U}(t)$. Conversely, if a distinct pair
has difference support disjoint from $O_{\mathcal U}$, the pair agrees on
every atom retained by every patch and therefore has identical restrictions.
$\square$

This is the necessary-and-sufficient finite criterion for a constrained or
candidate-relative section space. Pure coordinate coverage is a stronger
criterion that becomes exact for the unrestricted free presheaf.

> **Corollary 3.1 (Universal Coordinate Criterion).** Assume each declared
> payload type $V_a$ is inhabited. The restriction family is separating on all
> of $F_{\mathrm{free}}(C)$ if and only if
> $$
> O_{\mathcal U}=A_C.
> $$

*Proof.* Coverage implies that every difference is seen by some patch. If an
atom $a$ is uncovered, compare the everywhere-undefined section with the
section that has one declared value only at $a$. They are distinct globally
and equal on every patch. $\square$

Thus “sector labels cover the ambient sector set” is insufficient unless it
also implies coverage of every typed relation coordinate on which global
sections may differ.

## Free Finite Gluing

For $A_i=(u_i)_\#A_{C_i}$, a local family $(s_i)$ is **exactly matching** when
for every $i,j$ its ambiently reindexed partial maps agree on $A_i\cap A_j$.
Agreement is equality in `Option` payloads: both values and definedness must
agree. Merely agreeing where both sides happen to be defined is weaker and
does not constitute a matching family for this theorem.

All overlaps in this paper are ambient typed-atom intersections. Write

$$
A_{ij}:=A_i\cap A_j,
$$

with payload types inherited from $A_C$, and define

$$
F_{\mathrm{free}}(A_i)
:=
\prod_{a\in A_i}\operatorname{Option}(V_a).
$$

No categorical pullback $C_i\times_C C_j$ is assumed or used. In particular,
the notation below concerns restrictions to $A_{ij}$, not the existence of an
unproved pullback object in $\mathcal C_{\mathrm{tctx}}$.

> **Theorem 4 (Finite Free Gluing).** If
> $O_{\mathcal U}=A_C$, every exactly matching family
> $s_i\in F_{\mathrm{free}}(A_i)$ has a unique global extension
> $s\in F_{\mathrm{free}}(A_C)$.

*Proof.* For $a\in A_C$, choose a patch $i$ containing $a$ and define $s(a)$
to be the corresponding value of $s_i$. Exact overlap compatibility makes the
definition independent of the chosen patch. The resulting section restricts
to every $s_i$. If $t$ is another extension, coordinate coverage supplies a
patch containing each $a$, and both $s(a)$ and $t(a)$ equal its local value.
Hence $s=t$. $\square$

Writing every overlap as the declared ambient intersection $A_{ij}$, Theorem 4
gives

$$
F_{\mathrm{free}}(A_C)
\cong
\operatorname{Eq}\!\left(
\prod_iF_{\mathrm{free}}(A_i)
\rightrightarrows
\prod_{i,j}F_{\mathrm{free}}(A_{ij})
\right).
$$

No separate “local constraint completeness” is needed for the free partial-map
presheaf. That obligation appears only after an admissible subspace is imposed.

## Exact Admissible-Section Descent

A finite constraint package $Q_C$ consists of constraints $q$, each with a
finite atom scope

$$
\operatorname{supp}(q)\subseteq A_C
$$

and a predicate depending only on the restriction of a section to that scope.
For every atom subset $D\subseteq A_C$, define the induced local constraint
package

$$
Q_C|_D
=
\{q\in Q_C:\operatorname{supp}(q)\subseteq D\}.
$$

Because each $q$ depends only on its declared scope, it can be evaluated on a
section over $D$ whenever $q\in Q_C|_D$. Define the local admissible section
space with the constraint package visible on $D$ by

$$
F_{Q|D}(D)
=
\left\{
s\in F_{\mathrm{free}}(D):
q(s)=\mathrm{true}\text{ for every }q\in Q_C|_D
\right\}.
$$

In particular,

$$
F_{Q_C}(A_C)
=
\left\{
s\in F_{\mathrm{free}}(C):
q(s)=\mathrm{true}\text{ for every }q\in Q_C
\right\}.
$$

For $D'\subseteq D$, restriction sends $F_{Q|D}(D)$ into
$F_{Q|D'}(D')$: every
$q\in Q_C|_{D'}$ also lies in $Q_C|_D$, and its value depends only on the
unchanged coordinates in $\operatorname{supp}(q)$. Hence the induced local
admissible spaces form a
restriction-stable admissible subpresheaf of $F_{\mathrm{free}}$ on the finite
atom-subset category generated by $A_C$. The explicit notation
$F_{Q|A_i}(A_i)$ prevents a local validator from being mistaken for a checker
of the full package $Q_C$.

For a fixed cover $\mathcal U$, define the **visible constraint package**

$$
Q_{\mathcal U}
=
\bigcup_i Q_C|_{A_i}
=
\{q\in Q_C:\exists i,\ \operatorname{supp}(q)\subseteq A_i\}.
$$

The corresponding global model space is

$$
F_{Q_{\mathcal U}}(A_C)
=
\{s\in F_{\mathrm{free}}(C):q(s)=\mathrm{true}
\text{ for every }q\in Q_{\mathcal U}\}.
$$

For constraint packages $P,Q$ over the fixed typed atom set $A_C$, write

$$
P\models_{A_C}Q
$$

when every global typed partial assignment satisfying every predicate in $P$
also satisfies every predicate in $Q$. This is semantic entailment in the
fixed typed domains and convention profile; it is not a claim about a chosen
syntactic proof calculus.

Equivalently,

$$
Q_{\mathcal U}\not\models_{A_C}Q_C
$$

means that some global typed partial assignment satisfies every visible
constraint in $Q_{\mathcal U}$ while violating at least one constraint in the
full package $Q_C$.

A cover is **scope-complete** for $Q_C$ when

$$
\forall q\in Q_C,\quad
\exists i,\quad
\operatorname{supp}(q)\subseteq A_i.
$$

> **Theorem 5 (Exact Admissible-Section Characterization).** Assume
> $O_{\mathcal U}=A_C$. Canonical restriction and free gluing induce a
> bijection
> $$
> \operatorname{Eq}\!\left(
> \prod_iF_{Q|A_i}(A_i)
> \rightrightarrows
> \prod_{i,j}F_{Q|A_i\cap A_j}(A_i\cap A_j)
> \right)
> \cong
> F_{Q_{\mathcal U}}(A_C).
> $$
> Consequently, full constrained section descent holds exactly when
> $$
> Q_{\mathcal U}\models_{A_C}Q_C.
> $$

*Proof.* An element of the equalizer is an exactly matching family
$(s_i)$ with each $s_i\in F_{Q|A_i}(A_i)$. Theorem 4 supplies its unique free
gluing $s$. If $q\in Q_{\mathcal U}$, then
$\operatorname{supp}(q)\subseteq A_i$ for some $i$. Local admissibility gives
$q(s_i)=\mathrm{true}$, and scope locality gives
$q(s)=q(s_i)=\mathrm{true}$. Hence $s\in F_{Q_{\mathcal U}}(A_C)$.

Conversely, let $s\in F_{Q_{\mathcal U}}(A_C)$. Its restrictions exactly
match. If $q\in Q_C|_{A_i}$, then $q\in Q_{\mathcal U}$, so the restriction
$s|_{A_i}$ satisfies $q$. Thus every restriction lies in
$F_{Q|A_i}(A_i)$. Restriction and free gluing are inverse by Theorem 4, proving
the displayed bijection.

Because $Q_{\mathcal U}\subseteq Q_C$, one always has
$F_{Q_C}(A_C)\subseteq F_{Q_{\mathcal U}}(A_C)$. The full constrained
restriction map is onto the equalizer exactly when these model spaces are
equal, which is exactly the semantic entailment
$Q_{\mathcal U}\models_{A_C}Q_C$. $\square$

Thus scope completeness is sufficient but not necessary for a fixed package:
an unseen constraint may still be semantically implied by the visible ones.
The syntactic condition becomes exact only after the predicate interpretations
are universally quantified.

> **Corollary 5.1 (Universal Scope-Visibility Characterization).** Assume each
> payload type $V_a$ is inhabited and predicates on the declared scopes can be
> interpreted independently. The following are equivalent:
>
> 1. for every interpretation of the declared scope predicates, every exactly
>    matching locally admissible section family has a globally admissible
>    gluing;
> 2. $\mathcal U$ is scope-complete for $Q_C$.

*Proof.* Scope completeness gives $Q_{\mathcal U}=Q_C$, so Theorem 5 proves
sufficiency. Conversely, suppose a declared constraint $q_*$ has nonempty
scope $S_*$ not contained in any patch. Choose a global partial assignment
$s_*$. Interpret every other predicate as a tautology, and interpret $q_*$ as
a proper predicate that rejects $s_*|_{S_*}$ and accepts at least one other
scope assignment. Such a second assignment exists because $S_*$ is nonempty
and each $\operatorname{Option}(V_a)$ contains both `none` and a declared
value. The restrictions of $s_*$ are exactly matching and locally admissible,
since no patch can evaluate $q_*$. Their unique free gluing is $s_*$, which
violates $q_*$. Universal admissible descent therefore fails. An empty scope
cannot be invisible because the nonempty cover has a patch and the empty set
is contained in every patch. $\square$

## Relation-Valued Descent

Section-valued descent glues one compatible local assignment. Context cycles
do not obstruct that operation: Theorem 4 works for every finite coordinate
cover. A different criterion appears only after the local object type changes
to a set of assignments.

A **typed local relation** on $A_i$ is a subset

$$
R_i\subseteq F_{\mathrm{free}}(A_i).
$$

For $D\subseteq A_i$, write

$$
\pi_D(R_i)=\{s|_D:s\in R_i\}.
$$

A family $(R_i)$ is **pairwise consistent** when

$$
\pi_{A_i\cap A_j}(R_i)=\pi_{A_i\cap A_j}(R_j)
\qquad\text{for all }i,j.
$$

It is **globally consistent** when some relation
$R\subseteq F_{\mathrm{free}}(A_C)$ has exact projections
$\pi_{A_i}(R)=R_i$ for every $i$. The natural join

$$
\mathop{\bowtie}_iR_i
=
\{s\in F_{\mathrm{free}}(A_C):s|_{A_i}\in R_i
\text{ for every }i\}
$$

is a canonical candidate. It is the largest relation satisfying all local
membership conditions, but global relations with the same exact projections
need not be unique.

Let $H_{\mathcal U}$ be the context hypergraph with vertex set $A_C$ and
hyperedges $A_i$. It is **$\alpha$-acyclic** when it admits a join tree: a tree on
the context edges such that, for every atom $a$, the nodes whose edges contain
$a$ form a connected subtree. Equivalently, the hypergraph has an empty GYO
reduction.

> **Imported Theorem 6 (Relational Acyclicity Characterization).** The
> following are equivalent:
>
> 1. $H_{\mathcal U}$ is $\alpha$-acyclic;
> 2. for every choice of finite attribute domains, every pairwise-consistent
>    family of relations on the edges $A_i$ is globally consistent.
>
> Under these conditions, the natural join has exact projections onto every
> $A_i$.

This is the classical local-to-global characterization of acyclic database
schemes due to Beeri, Fagin, Maier, and Yannakakis
\cite{beeriFaginMaierYannakakis1983}. Atserias and Kolaitis extend the same
characterization to relations over positive semirings and use a generalized
Tseitin construction for the cyclic direction
\cite{atseriasKolaitis2023}. The present typed partial-map statement is a
direct specialization obtained by taking the ordinary attribute domain at
$a$ to be $\operatorname{Option}(V_a)$. It is imported mathematical structure,
not a novelty claim here.

A local relation is **locally admissible** when

$$
R_i\subseteq F_{Q|A_i}(A_i).
$$

A global relation is **globally admissible** when
$R\subseteq F_{Q_C}(A_C)$.

> **Theorem 7 (Typed Relational Admissible-Descent Characterization).** Assume
> $O_{\mathcal U}=A_C$ and fix a finite registry of declared constraint scopes.
> The following are equivalent:
>
> 1. $H_{\mathcal U}$ is $\alpha$-acyclic and $\mathcal U$ is scope-complete;
> 2. for every choice of inhabited finite payload types, every independent
>    interpretation of the declared scope predicates, and every
>    pairwise-consistent locally admissible relation family $(R_i)$, there is a
>    globally admissible relation $R$ satisfying
>    $\pi_{A_i}(R)=R_i$ for all $i$.
>
> When these conditions hold, the natural join $\mathop{\bowtie}_iR_i$ is one canonical
> such global relation.

*Proof.* Suppose condition 1 holds. Imported Theorem 6 shows that
$R^{\bowtie}=\mathop{\bowtie}_iR_i$ has exact projection $R_i$ on every patch. Let
$s\in R^{\bowtie}$ and $q\in Q_C$. Scope completeness supplies $i$ with
$\operatorname{supp}(q)\subseteq A_i$. Since $s|_{A_i}\in R_i$ and $R_i$ is
locally admissible, $q(s|_{A_i})=\mathrm{true}$. Scope locality gives
$q(s)=\mathrm{true}$. Thus every tuple of $R^{\bowtie}$ satisfies every global
constraint, so $R^{\bowtie}\subseteq F_{Q_C}(A_C)$.

Conversely, suppose the universal property in condition 2 holds. If
$H_{\mathcal U}$ were not $\alpha$-acyclic, interpret every declared predicate as
a tautology. The converse direction of Imported Theorem 6 supplies finite
domains and a pairwise-consistent relation family with no global relation,
contradicting condition 2.

If scope completeness failed, choose an invisible nonempty scope $S_*$ and a
global assignment $s_*$. Interpret all other predicates as tautologies and
let the predicate on $S_*$ reject $s_*|_{S_*}$ while accepting another scope
assignment. Set $R_i=\{s_*|_{A_i}\}$ for every $i$. These singleton relations
are pairwise consistent and locally admissible. Coordinate coverage forces
every tuple in any relation with exact projections $R_i$ to equal $s_*$, while
exact nonempty projections require that tuple to occur. Such a relation cannot
be globally admissible. Hence condition 2 implies scope completeness as well
as $\alpha$-acyclicity. $\square$

The two theorem layers must not be collapsed:

| Local object and quantifier | Fixed-instance exact criterion | Uniform structural criterion |
|---|---|---|
| one section with constraints | $Q_{\mathcal U}\models_{A_C}Q_C$ | every declared constraint scope is visible |
| one local relation per patch | the supplied family is globally consistent/joinable | $H_{\mathcal U}$ is $\alpha$-acyclic |

For universal constrained relation descent, the two right-hand criteria occur
together. For section-valued descent, hypergraph cyclicity is not an
obstruction.

## Sharp Three-Label Controls

Let the sector labels be $A,B,C$ and let the global relation atoms be

$$
A_C=\{AB,BC,AC\},
$$

with Boolean payloads.

### Label Coverage Without Separatedness

Take patches retaining the relations $AB$ and $BC$. Their underlying sector
labels jointly cover $\{A,B,C\}$, but $AC$ is unseen. The sections

$$
s_0=(AB=1,BC=1,AC=0),\qquad
s_1=(AB=1,BC=1,AC=1)
$$

have identical restrictions and are globally distinct. This is a
separatedness failure, not an existence failure.

Adding an $AC$ patch gives $O_{\mathcal U}=A_C$. Theorems 3 and 4 then give
universal separatedness and unique free gluing, without enumerating a global
candidate set.

### `UNSEEN_SCOPE`: Section-Valued Semantic Invisibility

Now impose the ternary even-parity constraint

$$
AB\oplus BC\oplus AC=0.
$$

The three relation-coordinate patches retaining $AB$, $BC$, and $AC$ cover
every relation atom, but no patch contains the full constraint scope. The local
assignment

$$
AB=BC=AC=1
$$

is overlap-compatible and has a unique free gluing. Its parity is odd, so it
has no admissible global extension in $F_{Q_C}(A_C)$. This is an existence failure,
not a separatedness failure.

The construction is minimal within the three-coordinate, three-singleton-patch
pattern: all coordinates are covered, while one ternary scope crosses every
patch. It is not claimed to be minimal among arbitrary presheaves or arbitrary
constraint languages. Its conclusion is exactly

$$
Q_{\mathcal U}\not\models_{A_C}Q_C.
$$

### `CYCLIC_CONTEXT_CORE`: Relation-Valued Nonjoinability

Here $AB$, $BC$, and $AC$ denote two-attribute context edges, whereas in the
preceding section they denote individual relation-coordinate atoms. The two
hostile controls therefore live in different local-object types.

Let the global attribute set be $\{A,B,C\}$, with Boolean domains, and take
context edges $AB$, $BC$, and $AC$. Define

$$
R_{AB}=\{(0,0),(1,1)\},\qquad
R_{BC}=\{(0,0),(1,1)\},
$$

and

$$
R_{AC}=\{(0,1),(1,0)\}.
$$

Every projection onto a unary overlap is the full relation $\{0,1\}$, so the
three local relations are pairwise consistent. A global tuple would have to
satisfy

$$
A=B,\qquad B=C,\qquad A\ne C,
$$

which is impossible. Hence the family is not globally consistent. This is the
minimal three-edge cyclic illustration of Imported Theorem 6; it is not the
general counterexample construction for an arbitrary non-alpha-acyclic GYO
residual core.

The two hostile controls have different types and cannot substitute for one
another:

| Control | Local object | Exact failure |
|---|---|---|
| unseen scope | one exactly matching local assignment family | a unique free section exists but global admissibility fails |
| cyclic context | one pairwise-consistent local relation family | no global relation exists |

## Comparison Reconstruction

Let $X_R$ be a declared report-object system with canonical restrictions. It
may be section-valued or relation-valued, but the object type is fixed for a
given comparison. An **$\mathcal U$-reconstruction gate** is a declared map

$$
\operatorname{Rec}_{\mathcal U}:
\{\text{admissible compatible local }X_R\text{-families}\}
\longrightarrow X_R(C)
$$

whose result restricts exactly to the supplied local objects. In the
section-valued case, Theorem 5 supplies this gate when its semantic-entailment
condition holds, and the reconstruction is the unique free gluing. In the
relation-valued universal case, Theorem 7 supplies the natural join as a
canonical gate. The latter does not claim that no other global relation has
the same local projections.

Let $F_A\subseteq F_{\mathrm{free}}^A$ be a restriction-stable admissible
audit-signature subpresheaf. Fix a carrier, an alignment $\Phi$, and a
comparison-semantics package $\Theta$. A coordinate-local comparator is a
family

$$
\operatorname{Comp}^{\Phi,\Theta}_C:
X_R(C)\times X_R(C)\to F_A(C)
$$

that is restriction-natural:

$$
F_A(u)\operatorname{Comp}_C(r,t)
=
\operatorname{Comp}_{C'}(X_R(u)r,X_R(u)t).
$$

> **Theorem 8 (Finite Comparison Reconstruction).** Let $\mathcal U$ be a finite
> typed context family. Assume:
>
> 1. **typed report reconstruction:** declared reconstruction gates produce
>    global reference and target objects $(r,t)\in X_R(C)^2$ with exact local
>    restrictions;
> 2. **audit separatedness:**
>    $F_A(C)\to\prod_iF_A(C_i)$ is injective;
> 3. **comparison naturality:** the fixed-$\Phi$, fixed-$\Theta$ comparator
>    commutes with every restriction leg in $\mathcal U$.
>
> Then the local comparisons are the restrictions of the unique global audit
> comparison
> $\operatorname{Comp}^{\Phi,\Theta}_C(r,t)$.

*Proof.* The declared reconstruction gates supply $r$ and $t$ with the required
local restrictions. Comparison naturality shows that
$\operatorname{Comp}^{\Phi,\Theta}_C(r,t)$ restricts to every declared local
comparison. If another element of $F_A(C)$ has the same local restrictions,
audit separatedness identifies it with that global comparison. $\square$

Theorem 5 and Theorem 7 therefore supply different report-reconstruction
gates for different local object types. Theorem 3 supplies one finite criterion
for audit separatedness when the audit difference supports are hit by the
observed coordinates. None of these results automatically supplies a
comparator on a new object type: a relation-valued application must separately
declare its restriction-natural comparison rule.

This is a fixed-fiber reconstruction statement. It does not infer alignment,
choose $\Theta$, identify a defect, or attribute a cause.

## Finite Decision Criteria

All active conditions are decidable for explicitly finite inputs.

1. **Universal separatedness:** compute $O_{\mathcal U}$ and test
   $O_{\mathcal U}=A_C$.
2. **$G$-relative separatedness:** for each distinct $s,t\in G$, test whether
   $\Delta(s,t)\cap O_{\mathcal U}$ is nonempty.
3. **Exact matching:** compare `Option` payloads on every pairwise atom
   intersection, including domains of definition.
4. **Visible package:** compute $Q_{\mathcal U}$ by finite scope containment.
5. **Fixed-package admissible descent:** when the typed domains and predicates
   are finite and executable, enumerate global assignments or invoke the
   declared finite solver to decide
   $Q_{\mathcal U}\models_{A_C}Q_C$.
6. **Uniform scope visibility:** for every declared scope, test containment in
   at least one patch.
7. **Relation consistency:** compare exact projections of every pair of finite
   local relations.
8. **Relational structural gate:** run GYO reduction on $H_{\mathcal U}$; an
   empty reduction yields a join-tree certificate, while a nonempty residual
   yields a structural cyclic-core certificate.
9. **Canonical reconstruction:** use coordinate union for matching sections
   and natural join for relation families that pass the relevant gate.

For $n=|A_C|$, $m$ patches, $q$ constraint scopes, and a finite candidate
space of size $g$, the universal cover and constraint-scope checks are finite
set-containment computations. Candidate-relative separation requires at most
$\binom g2$ difference-support checks. Semantic-entailment complexity depends
on how predicates are represented; no representation-independent complexity
class is claimed here.

A GYO residual core is a certificate of non-alpha-acyclicity, but it is not by
itself the concrete Boolean triangle witness of Section 7.3. Automatically
constructing pairwise-consistent relations that are globally inconsistent for
an arbitrary residual core requires the general classical counterexample
construction. This paper keeps the structural certificate and the minimal
three-edge hostile fixture distinct.

## Related Work and Novelty Boundary

### Sheaf Separatedness and Gluing

In sheaf theory, injectivity into a product of restrictions is the familiar
separatedness or uniqueness half of the sheaf condition, while the equalizer
diagram expresses compatible-family gluing \cite{maclaneMoerdijk1992}. Theorems
3 and 4 are finite-coordinate instances of that standard structure. This paper
does not claim those abstract patterns as new, and it does not declare the
active context families to be a Grothendieck topology.

### Database Lossless Joins and Acyclicity

Relational database theory studies lossless decomposition, join dependencies,
and the recovery of a global relation from projections
\cite{fagin1977multivalued,maier1983relational}. Beeri, Fagin, Maier, and
Yannakakis proved that every pairwise-consistent relation family is globally
consistent exactly for acyclic database schemes
\cite{beeriFaginMaierYannakakis1983}. Atserias and Kolaitis later established a
common positive-semiring generalization of the database and probabilistic
local-to-global results \cite{atseriasKolaitis2023}. Imported Theorem 6 is the
ordinary-relation specialization of that classical line. This paper does not
claim $\alpha$-acyclicity, join trees, GYO reduction, or the general cyclic
counterexample construction as new.

The section-valued equalizers of Theorems 4 and 5 are a different object:
their elements are matching tuples of individual assignments, not compatible
families of relations. The typed presentation makes payload types, partial
definedness, convention guards, and the change of local object type explicit.

### Constraint Satisfaction and Local Consistency

Constraint-satisfaction methods distinguish local consistency checks from
global satisfiability \cite{dechter2003constraint}. For a fixed finite
constraint package, Theorem 5 identifies the exact condition as semantic
entailment $Q_{\mathcal U}\models_{A_C}Q_C$, not syntactic scope containment.
Scope completeness becomes necessary only under the corollary's universal and
independent predicate-interpretation quantifiers. Thus two constraint packages
with the same scope hypergraph may have different fixed-instance descent
behavior because an unseen predicate may or may not be entailed by the visible
ones.

### Contextuality and Finite Relational Structures

Sheaf-theoretic contextuality also organizes local sections, compatibility,
and obstructions to global sections \cite{abramskyBrandenburger2011}. Finite
model theory supplies the broader language of finite relational signatures and
local/global definability \cite{libkin2004finite}. The present paper does not
identify an audit mismatch with physical or quantum contextuality, nor does it
take the event-sheaf or empirical-model semantics as its report object. Its
narrower object is a typed partial report/audit signature with source-declared
relation coordinates and convention guards.

### Novelty Allocation

Relative to these adjacent theories, the contribution is not a new
abstract separatedness theorem or a rediscovery of relational acyclicity. It
is the interface-level package consisting of:

- typed partial-map carriers with exact definedness-sensitive overlaps;
- an explicit `label-cover / relation-cover / type-convention-cover`
  separation;
- the exact visible-package equalizer and fixed-package criterion
  $Q_{\mathcal U}\models_{A_C}Q_C$;
- a strict quantifier boundary between fixed semantic entailment and uniform
  syntactic scope visibility;
- typed composition of that visibility gate with the imported relational
  acyclicity obstruction;
- separate unseen-scope and cyclic-context controls;
- propagation of object-appropriate reconstruction gates into comparison
  under fixed alignment and semantics.

## Computational Evidence

Two exact finite controls and a pinned Lean companion accompany the manuscript.
The Lean source covers free coordinate coverage, separatedness, free gluing,
and the three-label missing-coordinate witness. The Python replay checks the
`UNSEEN_SCOPE` and `CYCLIC_CONTEXT_CORE` fixtures as distinct typed objects.

These computations do not prove the general relational acyclicity theorem,
the visible-package theorem, or the comparison-reconstruction theorem. The
imported BFMY result is supported by its cited proof, not by the three-edge
replay. Conversely, the manuscript theorems do not validate a concrete SOF
adapter or promote a Paper XIII audit. An application must separately bind the
relevant coordinate, scope, relation, and convention registries.

## Evidence Boundary

The manuscript, Lean companion, exact fixtures, imported literature, and
release receipt establish different claim surfaces. They must not be promoted
across rows of the following table.

| Claim surface | Evidence status | Explicit boundary |
|---|---|---|
| Theorem 3 and Corollary 3.1: free coverage/separatedness | Lean formalized and locally compiled under the pinned closure | The Lean model uses `Option`-valued finite signatures; it does not formalize every manuscript convention field |
| Theorem 4: free finite gluing | Lean formalized and locally compiled | Covers exactly matching free local sections; no constraints or relation-valued families |
| Section 7.1: three-label nonseparation witness | Lean formalized | Covers the missing-`AC` section witness only |
| Theorem 5 and Corollary 5.1: exact admissible-section and universal scope visibility | Manuscript proofs | Not Lean formalized; the exact theorem is relative to fixed typed domains and the corollary requires independent predicate interpretations |
| Imported Theorem 6: relational acyclicity | Imported published theorem | Not reproved by Lean or by the paper-owned three-edge fixture |
| Theorem 7: typed relational admissible descent | Manuscript proof plus exact hostile control | The Python fixture verifies one minimal cyclic family, not the general BFMY cyclic construction |
| Section 7.2 and Section 7.3 hostile controls | Exact finite Python replay | Establish only the declared finite fixtures |
| Theorem 8: comparison reconstruction | Manuscript conditional theorem | No comparator implementation or Paper XIII audit is validated |
| Release receipt | Source-addressed local closure verification | Binds declared bytes and replay status; it does not independently validate its own implementation |

## Claim Status and Boundary

| Claim | Status |
|---|---|
| finite typed-context category | Theorem |
| restriction functor | Theorem |
| $G$-relative separating-cover characterization | Theorem; standard injectivity pattern, typed finite specialization |
| universal coordinate-cover characterization | Theorem; finite free-coordinate specialization |
| free finite gluing and equalizer representation | Theorem; standard gluing pattern, definedness-sensitive specialization |
| exact admissible-section equalizer | Theorem; semantic-visibility core |
| fixed-package criterion $Q_{\mathcal U}\models_{A_C}Q_C$ | Theorem |
| universal scope-visibility characterization | Theorem under explicit independent-interpretation quantifiers |
| relation local-to-global iff $\alpha$-acyclic | Imported classical theorem; not novelty |
| typed universal admissible-relation descent | Theorem; typed composition with imported relation theorem |
| fixed-$\Phi$, fixed-$\Theta$ comparison reconstruction | Theorem under an object-appropriate reconstruction gate |
| finite decision procedures | Theorem; constructive consequence of the finite definitions |
| `UNSEEN_SCOPE` and `CYCLIC_CONTEXT_CORE` | Computational Certificate; exact finite hostile witnesses |
| arbitrary-core relation witness generation | Research Program; not supplied by GYO residue alone |
| natural Grothendieck topology for application contexts | Research Program |
| descent under refinement, aggregation, or convention change | Research Program |

## Conclusion

Finite typed context descent has different exact gates for different local
object types. For section-valued data, observed difference supports determine
separatedness, full coordinate coverage gives unique free gluing, and the
visible constraint package determines whether local admissibility descends.
For relation-valued data, pairwise consistency additionally requires the
classical $\alpha$-acyclicity gate for a universal local-to-global guarantee.

These distinctions propagate directly into comparison reconstruction. A
fixed-alignment comparator descends only after the report objects have an
object-appropriate reconstruction gate and the audit signature is separating.
Local agreement alone does not supply missing relation coordinates, global
admissibility, alignment, defect attribution, or causal interpretation.

## Outlook

Open problems include formalizing the visible-package equalizer, producing
constructive witnesses from arbitrary cyclic GYO cores, and characterizing
which derived-summary maps preserve separatedness. Minimum semantic-descent
covers and sharp complexity bounds depend on the chosen predicate
representation. These questions remain within local-to-global mathematics and
do not require action, authorization, or causal semantics.

## Appendix A: Computational Artifacts

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite) under
`experiments/paper24/`; paths below are relative to that directory.

| Artifact | Role | Short path |
|---|---|---|
| formal source and closure | finite theorem surface with pinned Lean/Mathlib inputs | `lean/` |
| exact fixture records | section- and relation-valued controls | `results/` |
| validators | deterministic replay and local closure verification | `validation/` |
| release manifest | declared acyclic artifact closure | `release-manifest.json` |

From the repository root, run:

```bash
python experiments/paper24/validation/validate_release.py
```

The receipt is excluded from its own closure. A passing local validator binds
the declared bytes and replay results; it is not independent mathematical
validation.
