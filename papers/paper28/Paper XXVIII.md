# Finite Mechanism Structure
## Recursive Return in Single-Defect Circular Automata

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXVIII**

*This paper (Paper XXVIII of the RIME program) develops finite mechanism
structure, exact credit composition, and fixed-scope recursive return in
single-defect circular automata. It inherits the typed entry and completion
interface of Paper XXVII without enlarging or re-owning the theorem scope
established there.*

---

## Abstract

**Problem.** Exact descent relations contain more information than a mechanism
label. Packet identities, typed boundaries, ancestry, and the allocation of
maturity credit can all affect semantic composition and recursive return.

**Approach.** We retain exact realization fibers on declared finite carriers of
single-defect circular automata, separate interaction skeletons from accounting
refinements, and compare five independently constructed return surfaces through
typed handoff and provenance-sensitive mechanism predicates.

**Results.** On a closure of four rank-four contexts at $n=6$ and thirty-five
at $n=7$, the accounting and skeleton quotients fail to be semantic
composition congruences. A boundary-relational description factors 11,252 exact
receipts into transport, return, and fusion operations. The credit identity
$B(C)=L(x)+S(x)+B(C')$ composes on exact typed lifts and holds on all 13,054
compatible receipt pairs. Five declared $n=7$ carriers support existential
return from rank five through rank four to the exact low-rank base. Their 165
tagged rank-four contexts admit a sufficient GFPC/PEC mechanism cover, and all
26,995 macro lifts align with canonical one- or two-segment first-exit paths.

**Boundary.** These are finite-structure results, not an all-rank constructor,
a uniform mechanism selector, or a reset bound. Projectable-Origin Supply--the
existence of a projectable member in every admitted inherited transfer
fiber--remains open at arbitrary ambient size.

**Keywords.** synchronizing automata; single-defect circular automata; typed
descent; exact realization fibers; credit composition; recursive return;
computational certificate

\newpage

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/n\mathbb Z$, $p$, $d$ | state set, labelled cycle, and binary-kernel rank-$(n-1)$ defect |
| $C=(A,d,\mu_r,\chi_r)$ | certified rank-$r$ source context |
| $\operatorname{Lift}_r(C,m)$ | complete exact realization fiber of declared menu channel $m$ |
| $\widehat{\partial^+x}$ | theorem-facing typed endpoint after verified handoff |
| $P_{\le3}$ | exact nonrecursive low-rank base |
| $B,L,S$ | credit budget, exact word length, and corridor surplus |
| $\mathrm{GFPC},\mathrm{PEC}$ | Generalized Fresh-Pair Carry and Pair-Extension Carry |
| $\mathcal T_{5\to4}(z)$ | complete declared transfer fiber of inherited pair $z$ |
| $\mathcal T_{5\to4}^{\rm proj}(z)$ | projectable subfiber, not a chosen transfer |

## Introduction

A recursive descent argument needs both a legal proof state and a realization
that reaches another legal proof state. The first requirement does not
determine the second. Two paths can share their fusion pattern and numerical
credit data while exposing different typed successor relations. Conversely,
distinct exact paths can support the same finite return theorem without
sharing a shortest word, a surplus value, or a literal target serialization.

This paper studies the finite structure between these two levels. We use the
source-addressed proof interface of Paper XXVII [@paper27] and retain three
objects separately:

$$
 \boxed{
 \text{interaction skeleton}
 +\text{accounting refinement}
 +\text{exact typed realization fiber}.
 }
$$

Our contributions are organized by their mathematical dependencies.

1. On a declared $4+35$ seed closure, we locate the failure of quotient-level
   semantic composition and give an exact boundary-generator cover.
2. We prove the exact credit telescope and record its finite,
   relation-valued accounting composition.
3. We combine five fixed-$n=7$ return surfaces into one existential
   section-to-section-to-base statement, retaining unsuccessful channels.
4. We give a reduced sufficient GFPC/PEC cover of 165 tagged rank-four
   contexts and transport it through canonical first-exit path alignment.

The finite domains are part of the statements. The $4+35$ closure used for
composition is not the 165-context domain used for the five returns. Nor is
either domain an enumeration of all admitted contexts at arbitrary ambient
size. The computational certificates retain complete tied fibers within
their declared constructions; they are not lists of selected winners.

The final question concerns the origin of a recursive input rather than a
new finite realization: what all-$n$ structure forces an admitted inherited
pair to have a projectable origin? The finite results below do not depend on
a solution to that question.

![Finite proof architecture. Solid arrows denote construction dependencies
within the declared finite scopes. The dashed boundary records an open
all-$n$ supply problem, not an implication from the finite certificates.](../../figures/paper28/fig1_finite_mechanism_structure.png){width=76%}

### Related Work and Novelty Boundary

For circular automata, Dubuc proved the Černý bound in a broader circular
class [@dubuc1998]. One-cluster arguments provide a different route under
their own cycle hypotheses [@steinberg2011onecluster]. Neither result is
reproved or improved here: our scope is a finite collection of typed
rank-descent relations, not a uniform reset-length theorem.

The alphabet of a permutation together with a rank-$(n-1)$ merging letter
also occurs in work on randomized construction of slowly synchronizing
automata [@catalanoJungers2018]. Completely reachable automata ask whether
every nonempty subset can arise as an image [@bondarVolkov2016]. We assume
neither that reachability property nor a randomized generator model. Packet
identity, proof-context certification, and tied exact realizations are retained
because the recursive return question reads them.

Within this series, Paper XXIII supplies deterministic pair-hitting and
marked-kernel corridor geometry [@paper23], whereas Paper XXVI treats
stochastic pair transfer and waiting [@paper26]. Paper XXVII owns the
fixed-scope entry section and source-addressed completion interface used
here [@paper27]. The present contribution is the finite mechanism quotient
obstruction, exact credit composition, five relation-valued recursive
returns, a reduced sufficient tagged cover, and canonical path alignment.
Paper XXVII asks which proof information must be retained; this paper asks how
exact descent propagates within that retained interface.
These results neither re-own the imported interface nor establish
Projectable-Origin Supply at arbitrary $n$.

## Imported Proof Interface

Let $Q=\mathbb Z/n\mathbb Z$, let $p$ be the labelled cyclic permutation,
and let $d$ be a labelled rank-$(n-1)$ defect with a binary kernel. Words
act from left to right. An exact state retains source-addressed atom packets
and their occupied coordinates, not only the packet masses.

A certified rank-$r$ context is written
$$
 C=(A,d,\mu_r,\chi_r).
$$
Here the characteristic $\chi_r$ carries the distinguished and ancestry
data required by the owning theorem. A legal checkpoint, an internal replay
state, and a certified lower target are different types of objects.
Paper XXVII supplies the checkpoint interface, source-addressed completion
relations, and endpoint-normalization and accounting gates. Those objects are
imported without reproof. The typed handoffs used below are declared and
validated by the five return constructions of this paper.

An exact lift $x$ has source $\partial^-x$, actual endpoint
$\partial^+x$, and theorem-facing target
$$
 \widehat{\partial^+x}=\eta_x(\partial^+x).
$$
The notation includes the declared normalization semantics. The handoff may
be identity or a verified typed atom bijection, but it must preserve every
observable used by the lower theorem. Equality of mass partitions alone
does not provide a handoff.

For a declared source $C$, a finite menu $\mathfrak M_r(C)$ has
relation-valued exact fibers $\operatorname{Lift}_r(C,m)$. We retain the
following construction requirements from the paper-owned return schema:

- **F1, future-free construction.** The menu, channel keys, and lift relation
  are constructed without access to lower-section membership, low-rank
  success, winning labels, or reset coaccessibility.
- **F2, source typing.** Every lift in $\operatorname{Lift}_r(C,m)$ has
  source $C$.
- **F3, exact soundness.** Replay, packet roles, ancestry, normalization,
  handoff, and accounting satisfy the declared typed equations.
- **F4, checkpoint typing.** Internal replay states are not exported as
  recursive checkpoints without independent certification.

For a separately certified lower destination class $\mathfrak D_{<r}$,
define
$$
 \operatorname{Good}_r(C,m)
 \iff
 \exists x\in\operatorname{Lift}_r(C,m):
 \widehat{\partial^+x}\in\mathfrak D_{<r}.
 \tag{2.1}
$$
Thus success is evaluated on the constructed relation; it is not part of
its construction. The return assertion, F5, is
$$
 \forall C\in\operatorname{Sec}_r\quad
 \exists m\in\mathfrak M_r(C):\operatorname{Good}_r(C,m).
 \tag{2.2}
$$
F1--F4 do not imply F5. Sections 5 and 6 establish finite instances, not an
all-rank realization of these contracts. Per-context finiteness of a menu
also does not imply a rank-controlled or an absolute uniform size bound.

## Mechanism Quotients and Boundary Generators

### The exact finite relation

Let $\mathcal R_{\rm seed}$ be the exact relation reconstructed from the
four declared $n=6$ rank-four contexts and the thirty-five declared
extremal $n=7$ contexts, together with their strictly descending rank-three
and rank-two closure. The construction retains every tied endpoint-shortest
admissible receipt in its declared Type-I/II relation. Type I uses one
corridor with nonnegative surplus; Type II uses two corridors with
$S_1<0$ and $S_1+S_2\ge0$. These are local accounting conditions, not
membership tests in the lower success set.

The paper-owned seed certificate has the following scope.

| Object | Count |
|---|---:|
| Rank-four seed contexts | 39 |
| Seed receipts | 4,250 |
| Lower-rank closure receipts | 7,002 |
| All exact receipts | 11,252 |
| Exact compatible receipt pairs | 13,054 |
| Type-I receipts | 1,634 |
| Type-II receipts | 9,618 |

An exact receipt retains its source, word, corridor boundaries, fusion packet
identities, endpoint, and ancestry update. Source, endpoint, and total length
alone are not an exact-receipt identity.

The accounting quotient $q_{\rm acct}$ retains the interaction skeleton,
rank drops, maturity gains, corridor lengths and surpluses, debt profile,
target partition, and residual budget. The skeleton quotient $q_{\rm skel}$
forgets the numerical allocation while retaining the declared source/target
partitions, fusion pattern, and interaction/ancestry-participation type.
Write $q_{\rm skel}$ also for its composite with $q_{\rm acct}$.
The complete key definitions are retained in the paper-owned evidence package.

For a quotient $q$, an observable $O$ descends if
$$
 q(x)=q(x')\Longrightarrow O(x)=O(x').
$$
For set-valued observables this is equality of the full images, not agreement
of one chosen representative.

### Failure of semantic composition congruence

Exact compatibility $\operatorname{Comp}(x,y)$ requires equality of the
typed target of $x$ and source of $y$, including the required ancestry.
Define
$$
 \operatorname{Succ}_q(x)=
 \{q(y):\operatorname{Comp}(x,y)\}.
$$
A semantic composition congruence would require
$$
 q(x)=q(x')\Longrightarrow
 \operatorname{Succ}_q(x)=\operatorname{Succ}_q(x').
 \tag{3.1}
$$

**Proposition 3.1 (Finite quotient obstruction; computational certificate).**
On $\mathcal R_{\rm seed}$, neither the accounting quotient nor the
skeleton quotient satisfies (3.1). Even nonemptiness of the successor image
fails to descend.

| Quotient | Source fibers | Noncongruent fibers | Successor-nonemptiness mismatches |
|---|---:|---:|---:|
| Accounting | 250 | 103 | 69 |
| Skeleton | 30 | 9 | 8 |

**Certificate proof.** The seed reconstruction forms compatibility edges
from exact typed boundary equality and compares the complete successor-class
sets in each quotient fiber. The displayed noncongruent fibers contain
explicit unequal images; the last column records unequal emptiness status.
The same certificate separates the unary observables: ranks, partitions,
fusion mass patterns, and the residual budget descend to the skeleton;
lengths, surpluses, and debt require accounting; exact packet identities,
ancestry updates, and target channels still require the exact relation.
Neither quotient uses downstream success as a key.

The boundary audit verifies, on this same finite closure, that
the labelled action and normalized target mass placement support
fiber-uniform accounting/skeleton successor classes. This is a finite
liftability result, not an all-rank boundary congruence. In particular,
the obstruction does not justify replacing exact compatibility by equality
of accounting tuples.

### A boundary-relational generator cover

For each exactly replayed operation use a row
$$
 b^-\xrightarrow{\,g,a\,}b^+.
$$
The abstract boundaries retain the action and normalized mass placement;
$a$ records length, maturity gain, surplus, debt, and budgets. Its
realization fiber retains the exact packet placement, distinguished packet,
word segment, and receipt/corridor/operation addresses. Composition still
requires a compatible exact intermediate state.

Split each stored corridor at maximal nonempty permutation blocks and defect
letters:

| Generator | Segment | Rank behavior |
|---|---|---|
| $\mathrm{TRANSPORT}$ | $p^a,\ a>0$, maximal within the corridor | Rank preserving |
| $\mathrm{RETURN}$ | $d$ | Rank preserving |
| $\mathrm{FUSION}$ | Terminal $d$ | One binary strict drop |

**Proposition 3.2 (Exact generator cover; computational certificate).**
Every receipt of $\mathcal R_{\rm seed}$ is covered by these typed
operation rows, with its endpoint and accounting recovered by exact replay.
There are 123,240 operation occurrences:
$$
 49,656\ \mathrm{TRANSPORT}
 +52,714\ \mathrm{RETURN}
 +20,870\ \mathrm{FUSION}.
$$
Grouping by $(b^-,g,a,b^+)$ gives 24,355 rows, each with a nonempty exact
realization fiber.

| Generator | Relation rows | Largest exact fiber |
|---|---:|---:|
| TRANSPORT | 12,053 | 200 |
| RETURN | 8,113 | 336 |
| FUSION | 4,189 | 192 |

**Certificate proof.** Split each stored exact word as above and replay
every segment from its source-addressed state. Each corridor has one terminal
fusion; the recomposed word, endpoint, length, surplus, and credit allocation
agree with its receipt. Every row is populated by its recorded occurrences,
and the uncovered receipt set is empty.

The split is canonical for a fixed word, not unique among tied exact words.
Nor does nonemptiness of these rows assert realizability of every formally
writable row outside this finite relation.

This description separates interaction operations from path predicates.
Repayment records a credit condition; a heavy chain records consumption of
the first fresh packet by the second fusion. There are 9,618 repayment
receipts but only 9,608 repeated-fusion heavy chains. Fallback is a
target/allocation choice, not a fourth interaction operation. The resulting
object is a typed compatibility graph with accounting decoration and exact
fibers, not an algebra on three bare generator names.

## Exact Credit Composition

### Maturity and the telescope

For a mass state $\mu$ of total mass $n$, let
$$
 r(\mu)=|\operatorname{supp}\mu|,
 \qquad M(\mu)=\sum_q\binom{\mu(q)}2.
$$
Use the maturity potential of Paper XXVII:
$$
 \tau(\mu)=\|\mu\|_2^2+(r-1)(n-r)-2n+1
$$
for nonuniform states, with the separate initial convention
$\tau(\mathbf 1)=0$. Write $\tau(n)$ for the rank-one reset maturity.
For a typed context $C$, set
$$
 B(C)=\tau(n)-\tau(\mu(C)).
$$
If an exact corridor has length $\ell$ and endpoints of ranks $r,r-q$,
its surplus is
$$
 S=\tau(\mu')-\tau(\mu)-\ell
   =2\Delta M+q(2r-q-n-1)-\ell.
 \tag{4.1}
$$
The second expression uses the nonuniform-state formula on the corridor's
endpoints. For an exact receipt $x:C\to C'$, sum its corridor lengths and
surpluses to obtain $L(x)$ and $S(x)$.
When $C'=\widehat{\partial^+x}$, the declared handoff is either the identity
or a mass-preserving typed atom bijection. Hence the target mass state is only
relabelled and
$$
 \tau\bigl(\mu(C')\bigr)
 =\tau\bigl(\mu(\partial^+x)\bigr).
 \tag{4.2}
$$

**Proposition 4.1 (Exact credit composition).**
Every such receipt satisfies
$$
 \boxed{B(C)=L(x)+S(x)+B(C').}
 \tag{4.3}
$$
For exact compatible receipts $x:C_0\to C_1$ and $y:C_1\to C_2$,
$$
 \begin{aligned}
 L(y\circ x)&=L(x)+L(y),\\
 S(y\circ x)&=S(x)+S(y),\\
 B(C_0)&=L(y\circ x)+S(y\circ x)+B(C_2).
 \end{aligned}
 \tag{4.4}
$$

**Proof.** Summing (4.1) cancels the intermediate maturity values, so
$S(x)=\tau(\mu(C'))-\tau(\mu(C))-L(x)$, which is (4.3).
Exact compatibility supplies the same middle context to both identities.
Adding them cancels $B(C_1)$ and proves (4.4). This proves the numerical
identity on an existing exact composition; it does not produce that
composition or assert membership of the concatenation in a shortest fiber.

### Accounting fibers and allocation

**Proposition 4.2 (Finite accounting composition; computational certificate).**
All 11,252 receipts and all 13,054 exact compatible pairs in the seed closure
satisfy (4.3)--(4.4). There are 569 accounting-label pairs admitting an exact
compatible lift. Within each such pair fiber, the composite accounting
summary is constant: partition chain, gross credit, length and surplus
vectors, tail budgets, debt profile and peak debt, and final allocation.

**Certificate proof.** For each compatible exact pair, compute both middle
budgets independently and form the composite summary. Group these summaries
by the accounting-label pair and test constancy of the full image. Of the
569 pair fibers, 507 have more than one exact lift, and one has 616.
Thus constancy is not uniqueness of the concrete path. The
paper-owned credit certificate reconstructs these identities and fibers.

This defines a partial, exact-lift-supported accounting composition:
$$
 (a_1,a_2)\ \overset{\exists\text{ compatible exact lift}}{\longmapsto}\
 A_{21}.
$$
It is neither a total product nor an inverse test for lift existence.
Proposition 3.1 explains why the accounting result cannot determine
semantic composability.

The 26 realized skeleton-label pairs provide a sharper contrast.

| Composite observable | Skeleton pair fibers where it varies |
|---|---:|
| Partition chain, gross credit, or tail-budget vector | 0 |
| Length or surplus allocation | 23 |
| Debt profile or peak debt | 15 |

The skeleton retains gross geometry, but not its allocation. For example,
the extremal rank-four source has budget 27. Its zero-surplus subfamilies
include 1,020 exact heavy-target receipts with prefix/tail allocation
$20+7$, and 87 fallback receipts with allocation $12+15$:
$$
 20+7=12+15=27.
$$
The fallback creates no credit. It changes where the existing credit is
spent. Neither this equality nor the additive telescope decides whether a
candidate word belongs to an admissible lift relation.

## Five Fixed-Scope Recursive Return Surfaces

### Carriers and future-free relations

Let $i\in I=\{\mathrm{ext},2,3,4,5\}$. The symbols
$\operatorname{Sec}_{5,i}^{(7)}$ and
$\operatorname{Sec}_{4,i}^{(7)}$ denote the five separately declared
finite carriers and their certified checkpoint status. The first
rank-five carrier, called $\operatorname{Sec}_{5,\mathrm{cand}}^{(7)}$
in its certificate, is indexed here by $\mathrm{ext}$ to match its
rank-four destination. Tags are retained. Contexts with equal projections
remain distinct across carriers.

Each carrier is specified by its source-local selector and complete
candidate payload, not by its successful lifts or by the descriptive table
below. The five declaration/result pairs are denoted ext, cand2, cand3, cand4,
and cand5. Appendix A identifies the paper-owned evidence package; its index
binds each pair to the corresponding rank-four and rank-five records.

For each declared source the construction forms the complete tied exact
relation in its stated scope, groups it into future-free channels, and
retains all accounting refinements and exact lifts. It has no access to
lower-section membership. Target certification applies to this fixed
relation. Consequently unsuccessful lifts and whole failed channels remain
part of the mathematical object.

The successful rank-five transfers have the following anatomy. The two tables
separate carrier size and accounting from provenance-sensitive transport.

| Realization | $\lvert\operatorname{Sec}_5\rvert$ | $\lvert\operatorname{Sec}_4\rvert$ | Terminal fusion | Surplus | Length |
|---|---:|---:|---|---:|---:|
| ext | 35 | 35 | $1+1$ | 0 | 3 |
| cand2 | 48 | 48 | $1+1$ | 0 | 3 |
| cand3 | 36 | 36 | $1+2$ | 2 | 3 |
| cand4 | 36 | 36 | $1+2$ | 2 | 3 |
| cand5 | 10 | 10 | $1+2$ | 0 | 5 |

| Realization | Incoming distinguished packet | Typed handoff |
|---|---|---|
| ext | Not consumed | Verified atom bijection |
| cand2 | Not consumed | Identity |
| cand3 | Not consumed | Identity |
| cand4 | Consumed | Identity |
| cand5 | Consumed | Identity |

The ext source/target mass partitions are $(2,2,1,1,1)$ and
$(2,2,2,1)$. For cand2 they are $(3,1,1,1,1)$ and $(3,2,1,1)$;
for cand3--5 they are $(2,2,1,1,1)$ and $(3,2,1,1)$.
These partitions do not by themselves define the carriers.

### The finite return theorem

**Theorem 5.1 (Five fixed-scope return chains; computational certificates).**
For every $i\in I$, the declared future-free menu/lift constructions
satisfy F1--F4 and the following existential return statements:
$$
 \begin{aligned}
 \forall C_5\in\operatorname{Sec}_{5,i}^{(7)}\
 &\exists m_5\in\mathfrak M_{5,i}(C_5)\
 \exists x\in\operatorname{Lift}_{5,i}(C_5,m_5):
 \widehat{\partial^+x}\in\operatorname{Sec}_{4,i}^{(7)},\\
 \forall C_4\in\operatorname{Sec}_{4,i}^{(7)}\
 &\exists m_4\in\mathfrak M_{4,i}(C_4)\
 \exists y\in\operatorname{Lift}_{4,i}(C_4,m_4):
 \widehat{\partial^+y}\in P_{\le3}^{(7)}.
 \end{aligned}
 \tag{5.1}
$$
Here $P_{\le3}^{(7)}$ is the imported exact low-rank base. Hence, with
arrows interpreted existentially through typed handoff,
$$
 \boxed{
 \operatorname{Sec}_{5,i}^{(7)}
 \longrightarrow\operatorname{Sec}_{4,i}^{(7)}
 \longrightarrow P_{\le3}^{(7)}.
 }
 \tag{5.2}
$$

**Certificate proof.** The source declarations and relation constructors
fix each candidate domain independently of its return evaluator. Exact
replay validates the source, fusion, ancestry, normalization and handoff
fields of each lift. The rank-four certificates establish a successful
channel for every declared rank-four source. The rank-five certificates
establish a lift into that independently certified lower carrier for every
declared rank-five source. Compose these existential statements using the
same certified handoff of the chosen rank-five lift. Intermediate replay
states do not acquire checkpoint status. The complete finite
counts are as follows.

| Realization | Rank-five channels | Rank-five lifts | Returning channels | Returning lifts |
|---|---:|---:|---:|---:|
| ext | 87 | 214 | 35 | 35 |
| cand2 | 96 | 195 | 48 | 48 |
| cand3 | 70 | 209 | 36 | 36 |
| cand4 | 107 | 252 | 36 | 36 |
| cand5 | 28 | 62 | 10 | 10 |

| Realization | Rank-four channels | Rank-four lifts | Returning channels | Returning lifts |
|---|---:|---:|---:|---:|
| ext | 173 | 4,182 | 169 | 2,329 |
| cand2 | 401 | 9,600 | 401 | 9,498 |
| cand3 | 172 | 5,239 | 171 | 4,208 |
| cand4 | 252 | 6,498 | 252 | 5,937 |
| cand5 | 53 | 1,476 | 53 | 1,205 |
| **Tagged total** | **1,051** | **26,995** | **1,046** | **23,177** |

A returning channel means one with at least one returning lift, not a
channel all of whose lifts return. At rank four the relation retains
3,818 unsuccessful lifts, five entirely unsuccessful channels, and
186 mixed channels. The ext handoffs are all verified nonidentity atom
bijections; the other four surfaces use identity handoffs. These checks
establish (5.1) on the stated carriers and preserve its existential
quantifiers. See the paired source and evaluation certificates in Appendix A.

### Common structure and non-necessary anatomy

**Corollary 5.2 (Limits of a common finite normal form).**
None of the following is a necessary feature shared by the five declared
successful rank-five return surfaces: $1+1$ fusion, zero surplus, length
three, avoidance of the incoming distinguished packet, or literal identity
of the handoff.

**Proof.** Cand3--5 use $1+2$ fusion; cand3 and cand4 have surplus two;
cand5 has successful length five; cand4 and cand5 consume the incoming
distinguished packet; ext uses nonidentity handoffs. Each statement is
witnessed within Theorem 5.1's independently declared finite domains.

The invariant requirements are typed, source-addressed realization and
valid credit/handoff, not these particular anatomical values. This
corollary does not assert that every alternative anatomy is realizable.
Length and surplus also obey the same credit equation: the cand4/cand5
comparison is not an experiment varying them independently.

The scope is intentionally narrower than universal return. Theorem 5.1
does not prove success of every lift, maximality of any carrier, a
rank-controlled menu bound, or a constructor on arbitrary $n,r$.

## Reduced Mechanism Cover and Canonical Alignment

### Two provenance-sensitive mechanism families

A mechanism support predicate reads an exact selected-entry provenance
$\kappa_4^{\rm ISE}$, not only the final mass partition. It includes the
upstream packets $\Pi^\uparrow$, selected entry $e$, its terminal fresh
packet $F_{\rm ent}$, source certification, ancestry update, and typed
handoff $\eta$ into the rank-four context $C$.

The two sufficient families have the following source-addressed meanings.

**Generalized Fresh-Pair Carry (GFPC).** There are five upstream packets
and four target packets. Two singleton packets $x,y$ undergo the terminal
strict fusion $x\sqcup y=F_{\rm ent}$. The three other packets carry
atomwise, including the incoming distinguished packet, and
$$
 \eta(F_{\rm ent})=\operatorname{Dist}(\chi_4),\qquad
 \Pi_C=\eta\bigl((\Pi^\uparrow\setminus\{x,y\})\cup\{F_{\rm ent}\}\bigr).
 \tag{6.1}
$$
The branch does not fix the background mass partition or require a literal
identity handoff.

**Pair-Extension Carry (PEC).** There are distinct upstream packets
$P,Q,x$, with $|P|=|Q|=2$ and $|x|=1$. The terminal strict fusion
is $P\sqcup x=F_{\rm ent}$, the other pair $Q$ carries atomwise, and
$$
 \eta(F_{\rm ent})=\operatorname{Dist}(\chi_4),\qquad
 \Pi_C=\eta\bigl((\Pi^\uparrow\setminus\{P,x\})\cup\{F_{\rm ent}\}\bigr).
 \tag{6.2}
$$
The incoming distinguished packet is either $P$ or $Q$, with its
consumed-or-carried update certified exactly. The handoff preserves the
fresh, carried-pair, and spectator roles.

Both predicates retain their role witnesses relationally. Neither reads
the selected word, length, surplus, lower success, or a winner. The
historical Fresh-Pair Carry predicate is a specialization of GFPC at the
branch-domain level; this inclusion does not transfer a completion theorem
to the larger domain.

### Reduced finite mechanism cover

Let $\mathcal D_4^{(7)}$ be the tagged disjoint union of the admitted
rank-four context/certificate pairs of the five carriers. Thus
$$
 |\mathcal D_4^{(7)}|=35+48+36+36+10=165.
$$
For $g\in\{\mathrm{GFPC},\mathrm{PEC}\}$, let
$\mathcal G_g^{\rm fs}(z)$ be the declared fixed-scope relation of
supported provenance and exact local-return witnesses for $z$. A support
witness and a component-completion witness are both required; they are not
the same predicate.

**Theorem 6.1 (Reduced finite mechanism cover; computational certificate).**
For every $z\in\mathcal D_4^{(7)}$,
$$
 \boxed{
 \bigl(\{\mathrm{GFPC}\}\times\mathcal G_{\rm GFPC}^{\rm fs}(z)\bigr)
 \sqcup
 \bigl(\{\mathrm{PEC}\}\times\mathcal G_{\rm PEC}^{\rm fs}(z)\bigr)
 \ne\varnothing.
 }
 \tag{6.3}
$$
GFPC supplies ext and cand2; PEC supplies cand3, cand4, and cand5.

**Certificate proof.** The exact provenance records validate (6.1) on
$35+48=83$ tagged contexts and (6.2) on $36+36+10=82$. The separate
GFPC and PEC component certificates verify
generic LocalReturn on their respective complete finite adapters, retaining
failed and mixed channels. Their tagged composition covers all 165 contexts.
Its counts are the rank-four totals in Theorem 5.1, with 3,162 distinct
certified tagged targets. No new return evaluation or winner choice enters
this composition.

This is a reduced **sufficient** cover. It is not a proof that two families
are minimal or unique, that support alone implies completion, or that the
same families cover every admitted all-$n$ context.

### Alignment with canonical first-exit paths

For a typed context $C$, the canonical relation
$\Lambda_4^{\rm complete}(C)$ uses the declared rank-four plateau and
first strict exit, complete typed endpoint normalization, endpoint-shortest
distance, and all tied shortest realizations. Its construction does not
read lower success. The analogous rank-three relation is
$\Lambda_3^{\rm complete}$.

The finite adapter $\Lambda_4^{\rm fs}(C)$ is a different relation type:
it contains Type-I/II macro receipts. A Type-I receipt has one strict-exit
segment. A Type-II receipt has two, with the intervening debt compatibility.
Removing artifact-only identities from a receipt does not remove its words,
packet identities, corridor boundaries, ancestry, or accounting.

**Theorem 6.2 (Canonical alignment; computational certificate).**
On $\mathcal D_4^{(7)}$, every finite adapter macro lift has an explicit
canonical first-exit path image:
$$
 \boxed{
 \Lambda_4^{\rm fs}(C)\hookrightarrow
 \operatorname{Path}_{1,2}
 \bigl(\Lambda_4^{\rm complete},\Lambda_3^{\rm complete}\bigr).
 }
 \tag{6.4}
$$
The alignment preserves typed boundary, ancestry, normalization, exact
observables, and ISE provenance. It transports Theorem 6.1's supported
return witnesses to canonical certificates. The path-image map is injective
on each declared tagged adapter relation: no two distinct typed macro lifts
have the same typed one- or two-segment path image.

| Carrier | Sources / transfers | Canonical $\Lambda_4$ rows | Adapter macro paths |
|---|---:|---:|---:|
| ext | 35 / 35 | 1,537 | 4,182 |
| cand2 | 48 / 48 | 4,178 | 9,600 |
| cand3 | 36 / 36 | 3,511 | 5,239 |
| cand4 | 36 / 36 | 3,284 | 6,498 |
| cand5 | 10 / 10 | 939 | 1,476 |
| **Total** | **165 / 165** | **13,449** | **26,995** |

**Certificate proof.** Reconstruct the canonical first-exit relations
independently of the macro adapters. Exact replay identifies each adapter
receipt with its one-segment or debt-compatible two-segment image, retaining
all theorem-facing fields. There are 1,528 Type-I and 25,467 Type-II images.
The source-boundary and provenance checks hold on all 165 contexts.
Support transports by the same ISE provenance records; LocalReturn
transports by the exact path image. The 23,177 already certified returning
macro lifts therefore supply canonical returning paths. The
alignment certificate binds the construction independently
of the component-success data.

The conclusion is alignment, not
$\Lambda_4^{\rm fs}(C)=\Lambda_4^{\rm complete}(C)$.
A two-segment macro is not a single first exit, and neither mathematical
relation equality nor raw serialization equality follows from (6.4).
This distinction permits semantic transport without erasing the types of
the compared objects.

## Boundaries and Projectable-Origin Supply

### The finite boundary

The quotient obstruction, generator cover, and finite accounting constancy
refer to the $4+35$ closure. The return, reduced-cover, and alignment
theorems refer to the five tagged $n=7$ carriers. The algebraic telescope
applies whenever its exact typed composition premises hold, but it supplies
neither admissibility nor recursive checkpoint status.

### The remaining origin question

Fix the declared canonical, unrefined interfaces and an admitted pair
$z=(C,\kappa_4^{\rm ret})$, where
$$
 \kappa_4^{\rm ret}
 =(b_4,\chi_4,\Lambda_4^{\rm complete}(C),\nu_4).
$$
Its complete transfer fiber is
$$
 \mathcal T_{5\to4}(z)
 =\{\tau:\operatorname{TransferRecord}_5(\tau),\
       \operatorname{tgt}(\tau)=C,\
       \operatorname{ret}(\tau)=\kappa_4^{\rm ret}\}.
$$
Completeness is relative to this declared relation. It means neither
arbitrary exact-valid words nor a producer-selected sublist. Let
$$
 \begin{aligned}
 \operatorname{Sec}_4^{\rm inh}
 &=\{z\in\operatorname{Sec}_4:
             \mathcal T_{5\to4}(z)\ne\varnothing\},\\
 \mathcal T_{5\to4}^{\rm proj}(z)
 &=\{\tau\in\mathcal T_{5\to4}(z):
       \exists\kappa_4^{\rm ISE}\
       \operatorname{Proj}_{\rm ISE}(\tau,\kappa_4^{\rm ISE})\}.
 \end{aligned}
 \tag{7.1}
$$
Projection requires an actual compatible selected-entry provenance, exact
replay, ancestry update, and typed target handoff on the same transfer.
The inherited domain is not defined by projectability.

**Open Problem 7.1 (Projectable-Origin Supply).**
Under the declared relation semantics and their applicability premises,
does
$$
 \boxed{
 \forall z\in\operatorname{Sec}_4^{\rm inh},\qquad
 \mathcal T_{5\to4}^{\rm proj}(z)\ne\varnothing
 }
 \tag{7.2}
$$
hold at arbitrary ambient size?

The 165 finite fibers audited above are projectable singletons. They
establish (7.2) on that finite domain, but cannot distinguish existential
supply from the stronger Uniform Projection assertion
$\mathcal T^{\rm proj}(z)=\mathcal T(z)$.
Uniform Projection is not needed in (7.2).

An entry-evidence condition together with projection soundness for the same
$(\tau,e,\mathsf{sel})$ would be a sufficient factorization of this goal.
Neither all-$n$ premise is established here. In particular, entry evidence
alone is not a projection witness.
Equation (7.1) fixes the complete fiber and (7.2) fixes the existential
quantifier. Both the entry and the projection must be witnessed by the same
transfer; an entry witness for one transfer cannot be combined with a
projection calculation for another.

A counterexample to (7.2) must give an admitted $z$ with
$$
 \varnothing\ne\mathcal T_{5\to4}(z),
 \qquad \mathcal T_{5\to4}^{\rm proj}(z)=\varnothing.
$$
It must exclude every projection of every member of that fixed complete
fiber. One unsuccessful transfer, a failed proof route, or an unspecified
predicate does not meet this standard. No qualified whole-fiber
counterexample is established here.

A proof of (7.2) would still not supply a uniform menu, an all-rank
cover/admission theorem, or an all-rank recursive selector. Those are separate
open structural problems, not conclusions of the finite certificates.

The finite mechanism structure, credit calculus, five recursive returns,
reduced cover, and canonical alignment constitute the finite results. The
unresolved all-$n$ question is which additional structure forces a
projectable recursive origin.

## Claim Status and Boundary

| Claim surface | Evidence level | Bound |
|---|---|---|
| Credit telescope and formal composition identity | Theorem | Exact typed lifts under the stated accounting equations |
| Seed quotient obstruction, finite generator cover, five returns, GFPC/PEC cover, and canonical alignment | Computational Certificate | The declared $n=6$/$n=7$ source relations and their receipt-bound finite closure |
| Projectable-origin supply, uniform menus, all-rank cover/admission, and an all-rank recursive selector | Research Program | No all-$n$ proof or qualified whole-fiber counterexample |

The finite certificates are reproducible checks of declared complete
relations, not statistical observations. They do not certify unenumerated
sources, a minimum mechanism family, equality of macro and first-exit
relations, a universal reset bound, or independent implementation agreement.
The paper-owned evidence package preserves the original artifacts and
receipts byte-for-byte; its separate validation receipt certifies local
release-copy closure only.

## Conclusion

Exact realization fibers cannot in general be replaced by bare mechanism
labels or accounting tuples. On the declared finite carriers, the relevant
structure is instead a typed relation: boundary operations retain concrete
realizations, credit composes only along compatible lifts, and recursive return
is existential over independently constructed finite menus.

The five return surfaces nevertheless admit a common sufficient description.
GFPC and PEC cover all 165 tagged rank-four contexts, and their 26,995 macro
lifts align with canonical one- or two-segment first-exit paths. This closes the
finite mechanism analysis without promoting the cover to a universal selector.
The remaining all-$n$ problem is Projectable-Origin Supply.

## Appendix A: Computational Artifacts and Certificate Scope

The finite claims above use exact replay and source-addressed finite
relations, not statistical sampling. Algebraic Proposition 4.1 has a direct
proof; a supplementary Lean spine checks its conditional credit algebra and
the data-independent composition and transport implications used by Theorems
5.1 and 6.2. The finite counts, fiber constancy, return coverage, and alignment
statements retain their separate computational certificates. No claim of an
independent second implementation is made.

The manuscript is self-contained at its stated claim levels. The accompanying
source-addressed evidence package is available in the
[RIME repository](https://github.com/dooven-prime/rime-lite) under
`experiments/paper28/`; these paths are reproducibility pointers, not premises
needed to read the proofs.

| Artifact surface | Role | Repository-relative short path |
|---|---|---|
| Theorem-facing records | finite relations, return surfaces, cover, and alignment | `artifacts/`, `results/` |
| Producers | exact finite construction and replay | `*.py` |
| Validators | scientific checks and receipt validation | `validation/` |
| Dependency manifest | ordered frozen mirror and exact input graph | `dependency-manifest.json` |
| Finite validation receipt | replay of the 20 finite roots; downstream of the historical receipts | `validation/` |
| Supplementary Lean spine | conditional algebra, composition, and transport implications | `lean/`, `results/` |
| Release manifest | manuscript/build roots and the two nested evidence closures | `release-manifest.json` |
| Public package receipt | outer local closure verification; excluded from every upstream closure | `results/` |

Each result package supplies its exact source declarations, relation
constructor, artifact, receipt, and validator. The package README lists the
file-level bindings and validation commands. Candidate payloads define the
finite domains; the anatomy table in the main text is not a replacement for
those declarations.

The evidence index records exact digests, producers, validators, commands,
and the two primary immutable artifact hashes. The paper-owned local
validation receipt checks the frozen mirror and replays the 20
manuscript-level finite validators without an external source tree.
It is downstream of the original receipts and does not re-sign them or supply
independent implementation agreement. The
construction/evaluation separation preserves failed rows and prevents lower
success from becoming a hidden channel key.

The outer release manifest binds the manuscript, reader PDF, bibliography,
figure sources, finite mirror, Lean receipt, and public-package validator. Its
downstream public receipt is not a member of the manifest, either nested
closure, release identity, or package inventory.


::: {#refs}
:::
