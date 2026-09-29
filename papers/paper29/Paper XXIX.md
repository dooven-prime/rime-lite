# Cyclic Lineage Dynamics and Rank-Five First-Exit Frontiers
## An All-$n$ Classification for the Canonical Single-Defect Circular Family

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXIX | Version 1.0**

*This paper (Paper XXIX of the RIME program) develops an intrinsic raw-geometry
theory for rank-five packet frontiers in single-defect circular automata. It
is independently scoped from the typed transfer and recursive-return
contracts of Paper XXVIII. Those contracts motivate an open bridge but are
not premises of the theorems proved here.*

---

## Abstract

**Problem.** A rank-$(n-1)$ defect merges one pair of coordinates, but a
rank-five first exit depends on more than the five-point support or the pair
that eventually meets the kernel. The three surviving source packets retain
their own placement, and every earlier defect step must remain injective on
all five packets.

**Approach.** We encode raw packet states in defect-anchored cyclic
coordinates, factor each defect as one marked collapse followed by a
permutation, and lift the plateau graph to source-packet lineages. For a
candidate fused pair, quotienting internal pair and spectator labels gives an
exact $2+3$ spectator-safe configuration system. In the canonical family

$$
 d_n(0)=d_n(1)=0,\qquad d_n(q)=q-1\quad(2\le q\le n-1),
$$

this system admits a missing-image section, a universal cyclic return, and a
constructive hole-slide normal form.

**Results.** For every $n\ge5$, a candidate source pair can become the first
fused pair if and only if its two lineages are consecutive in the positive
cyclic order of the five source packets. Every cyclic-order-preserving
placement of the five lineages is plateau-reachable. Consequently, for a
reachable fused pair $F=\{f_0,f_1\}$ with remaining source order
$(r_1,r_2,r_3)$, the survivor spectrum is exactly

$$
 1\le s(r_1)<s(r_2)<s(r_3)\le n-2.
$$

The complete source-addressed raw first-exit frontier therefore has

$$
 5\binom{n-2}{3}
$$

endpoints. Its incidence type depends on source packets only through their
labels and cyclic order, not their masses or internal atom composition.

**Boundary.** The classification is a raw first-exit theorem. It does not
establish transfer membership, entry authorization, typed handoff,
projectability, recursive return, credit settlement, or a reset bound. The
extension from raw incidence to the declared projectable transfer fibers of
Paper XXVIII remains open.

**Keywords.** synchronizing automata; circular automata; rank defect; packet
lineage; first-exit frontier; spectator-safe reachability; cyclic order

\newpage

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/n\mathbb Z$ | labelled cyclic state set, with $n\ge5$ |
| $p(q)=q+1$ | positive labelled cycle on $Q$ |
| $d:Q\to Q$ | labelled rank-$(n-1)$ defect with binary kernel |
| $K_d=\{k_0,k_1\}$, $c_d$, $m_d$ | kernel, collision image, and missing image of $d$ |
| $P=(T,\Pi)$ | raw packet state with occupied support $T$ and source-addressed blocks $\Pi$ |
| $\mathcal A$ | fixed labelled atom carrier partitioned by the packets |
| $P_0=(T_0,\Pi_0)$ | fixed raw rank-five source |
| $\lambda:T_0\hookrightarrow Q$ | current placement of the five source-packet lineages |
| $\mathcal L_5(d;P_0)$ | plateau-reachable lineage injections |
| $\mathfrak B_d(P_0)$ | boundary-incidence spectrum $\{d\circ\lambda\}$ |
| $\mathfrak F_d(P_0)$ | reachable fused source-pair spectrum |
| $\mathfrak S_d(P_0;F)$ | survivor-placement spectrum over $F$ |
| $\operatorname{Conf}_{2,3}(Q)$ | marked pair plus spectator-triple configurations |
| $(A,H)$ | marked-pair and hole presentation of a $2+3$ configuration |
| $\Omega(A,H)$ | cyclic order of the five non-hole tokens |
| $d_n$ | canonical defect $0,1\mapsto0$ and $q\mapsto q-1$ for $q\ge2$ |

## Introduction

A synchronizing automaton acts simultaneously on states, subsets, and fibers
of source labels. Those levels coincide only in special circumstances. A
five-point support may reveal where a rank drop occurs, while failing to
record which source packets fuse or where the surviving packets land. For a
first-exit argument, that omitted incidence is part of the result.

This paper isolates the intrinsic geometry of the first rank drop in a
single-defect circular automaton. Let $p$ be a labelled cycle and let $d$ have
rank $n-1$ with one binary kernel. Starting from five source-addressed
packets, we follow words for which every intermediate step preserves rank
five. The next $d$-step is then strict and produces a rank-four endpoint. Our
question is:

$$
 \boxed{
 \text{Which source-addressed rank-four endpoints can occur at that first exit?}
 }
$$

The answer is complete for the canonical family $d_n$. Its short form is as
follows.

**Main Theorem.** Fix $n\ge5$ and a raw rank-five source whose packet
lineages have positive cyclic order $(q_0,q_1,q_2,q_3,q_4)$. Under the
canonical defect $d_n$:

1. the possible fused source pairs are exactly the five consecutive pairs
   $\{q_i,q_{i+1}\}$;
2. after writing a fused pair as $(f_0,f_1)$ in positive order and the three
   survivors as $(r_1,r_2,r_3)$, its possible output placements are exactly
   the increasing injections
   $$
    1\le s(r_1)<s(r_2)<s(r_3)\le n-2;
   $$
3. the complete raw frontier contains $5\binom{n-2}{3}$ endpoints.

The proof requires more than ordinary pair hitting. The three other packets
act as spectators: every internal $d$-step must be injective on the entire
five-point support. We therefore pass through the exact quotient

$$
 \text{five labelled lineages}
 \twoheadrightarrow
 \operatorname{Conf}_{2,3}(Q),
$$

which forgets identities inside the candidate pair and inside the spectator
triple while retaining the complete collision guard. In token/hole form, the
canonical dynamics preserve the cyclic order of the five non-hole tokens.
Conversely, an explicit section return slides holes across adjacent tokens.
This turns token-order adjacency into a necessary and sufficient, path-free
criterion for fused-pair reachability.

The paper contributes five linked pieces.

1. A defect-anchored coordinate system faithfully encodes raw packet states
   and their first-exit frontiers.
2. A matched control proves that kernel, root, missing image, support gaps,
   and source blocks do not determine the source-addressed frontier for a
   general labelled defect.
3. The factorization $d=\rho_d\circ e_K$ separates one marked collapse from
   the off-kernel permutation transport, and the packet-lineage lift records
   exactly the missing incidence.
4. The $2+3$ spectator-safe quotient is exact for fused-pair reachability,
   whereas the further pair-only quotient is not.
5. For $d_n$, a missing-image section, cyclic return symmetry, and hole-slide
   normal form give the fused-pair criterion and the complete survivor
   spectrum above.

The result is deliberately below the typed transfer layer. Paper XXVIII
established finite projectable transfer fibers and left their all-$n$ supply
open [@paper28]. The present theorem classifies raw first exits without
assuming that every raw endpoint belongs to a declared transfer fiber or
carries a projection witness. Section 7 records that bridge as an open
problem rather than importing the missing semantics into the raw object.

### Related Work and Novelty Boundary

For the canonical family, let $b$ be the standard Cerny defect letter,
$b(n-1)=0$ and $b(q)=q$ for $0\le q\le n-2$
[@cerny1964; @ferensSzykula2026]. Then

$$
 b=d_n\circ p,
 \qquad
 d_n=b\circ p^{-1}.
 \tag{1.1}
$$

Since $p^{-1}=p^{n-1}$, the alphabets $\{p,d_n\}$ and $\{p,b\}$ generate
the same transition monoid. The canonical theorem therefore concerns a finer
observable inside the standard Cerny transition system, not a new monoid.

The Cerny conjecture asks for a quadratic reset bound for synchronizing
automata [@cerny1964; @volkov2008; @volkov2022survey]. Circular automata admit
stronger uniform results under hypotheses different from those used here
[@dubuc1998]. Almost-group automata, consisting of permutation letters and a
letter with one nontrivial kernel class, provide a nearby structural setting
[@berlinkovNicaud2020]. This paper does not prove a reset bound or classify
general almost-group automata. It fixes one cyclic permutation, one labelled
binary-kernel defect, and one rank-five first-exit problem.

Eppstein's monotonic setting studies automata whose letters preserve a fixed
cyclic order and gives algorithms and bounds for reset sequences
[@eppstein1990]. Subset and complete reachability ask which unlabelled subsets
occur as images of the full state set. Don proves complete subset reachability
for an aperiodically $1$-contracting class and develops the circular special
case [@don2016]. Gonze and Jungers exhibit obstructions and long witnesses for
subset reachability and refine the structural theory of completely reachable
automata [@gonzeJungers2018]. Ferens and Szykula give a quadratic-time
recognition algorithm and reaching-threshold bounds for completely reachable
automata, a class that includes the Cerny automata
[@ferensSzykula2026]. These results establish cyclic-order, support, or subset
reachability statements. They do not by themselves classify paths that must
remain rank-five at every proper prefix while retaining source-packet
lineages, the three-spectator collision guard, and the complete terminal
incidence map. Those plateau-constrained, source-addressed observables are the
additional claims of this paper.

Within the RIME synchronizing-automata line, Paper XXIII studies pair hitting,
marked-kernel corridors, and Schreier waiting [@paper23]. Its pair-hitting
language motivates the present comparison, but ordinary two-point
reachability is too coarse here: three spectator lineages determine whether
an internal defect step is legal. Paper XXVIII studies finite typed transfer
and return relations [@paper28]. The novelty here is an all-$n$ raw theorem:
the exact spectator-safe quotient, the canonical token-order normal form, and
the complete source-addressed rank-five frontier classification. No theorem
of the cited papers is restated as this classification.

## Raw Packet Dynamics and First Exit

Let $Q=\mathbb Z/n\mathbb Z$, $n\ge5$, and let $p(q)=q+1$. A labelled defect
$d:Q\to Q$ has rank $n-1$. Hence it has one non-singleton fiber

$$
 K_d=\{k_0,k_1\},\qquad d(k_0)=d(k_1)=c_d,
$$

and one missing image $m_d\notin\operatorname{im}(d)$. All other fibers are
singletons.

A raw rank-$r$ packet state is a pair $P=(T,\Pi)$ with
$T\subseteq Q$, $|T|=r$, and nonempty, pairwise disjoint atom blocks
$\Pi(q)$, $q\in T$, whose union is a fixed labelled atom carrier
$\mathcal A$ with $|\mathcal A|=n$. A letter acts by push-forward:

$$
 a_*P
 =\left(aT, b\longmapsto
   \bigcup_{\substack{q\in T\\a(q)=b}}\Pi(q)\right),
 \qquad a\in\{p,d\}.
 \tag{2.1}
$$

Thus letters move packet coordinates and union packets with a common image;
they do not rename atoms. We suppress the subscript $*$ when no ambiguity is
possible.

Fix a raw rank-five source $P_0=(T_0,\Pi_0)$. A word
$w=a_1\cdots a_k$ is a **plateau word** from $P_0$ if every prefix acts with
rank five. Words act from left to right, so the corresponding coordinate map
after the prefix $a_1\cdots a_i$ is $a_i\circ\cdots\circ a_1$. A first-exit
endpoint has the form

$$
 d(wP_0),
$$

where $w$ is a plateau word and the final $d$ drops the rank from five to
four. The complete raw frontier is

$$
 \operatorname{Fr}^{\rm raw}_{5\to4,d}(P_0)
 =\{d(wP_0):w\text{ is plateau-admissible and the final }d\text{ is strict}\}.
 \tag{2.2}
$$

Because $K_d$ is the unique non-singleton fiber,

$$
 |dT|=|T|-1\iff K_d\subseteq T.
 \tag{2.3}
$$

Hence a $d$-step is plateau-admissible exactly when the current support does
not contain both kernel points, and the terminal $d$-step is strict exactly
when it does.

The canonical family studied in Sections 5 and 6 is

$$
 d_n(0)=d_n(1)=0,\qquad d_n(q)=q-1\quad(2\le q\le n-1).
 \tag{2.4}
$$

It has kernel $K=\{0,1\}$, collision root $c=0$, and missing image
$m=n-1$.

## Faithful Coordinates and a Coarse Obstruction

### Defect-anchored cyclic coordinates

For a general labelled pair $(p,d)$, use the collision root to identify $Q$
with $\mathbb Z/n\mathbb Z$ by

$$
 \iota_d(p^j(c_d))=j.
$$

Retain the full labelled map

$$
 \delta_d=\iota_d\circ d\circ\iota_d^{-1}.
$$

Let $P=(T,\Pi)$ have occupied indices
$j_0<\cdots<j_{r-1}$. Put

$$
 B_i=\Pi(\iota_d^{-1}(j_i)),\qquad
 g_i=j_{i+1}-j_i\quad(i<r-1),\qquad
 g_{r-1}=n+j_0-j_{r-1},
$$

and define

$$
 \mathfrak G_r(P)
 =\bigl(j_0,(g_0,\ldots,g_{r-1}),(B_0,\ldots,B_{r-1})\bigr).
 \tag{3.1}
$$

An admissible encoded state has $g_i>0$, $\sum_i g_i=n$,
$0\le j_0<g_{r-1}$, and ordered nonempty blocks $B_i$ partitioning
$\mathcal A$.
The phase condition reconstructs ordinary sorted indices
$j_i=j_0+\sum_{h<i}g_h<n$; gaps alone would leave a cyclic reindexing
ambiguity.

Encoded moves act on the pairs $(j,B)$. The $p$-move sends them to
$(j+1\bmod n,B)$; the $d$-move sends them to $(\delta_d(j),B)$ and unions
blocks with equal images. In both cases, sort the resulting pairs by their
new indices, carry the blocks through the same reindexing, and recompute phase
and gaps. Denote these operations by $\widehat p$ and $\widehat d$.

**Proposition 3.1 (faithful raw encoding).** For $1\le r\le n$,
$\mathfrak G_r$ is a bijection between raw rank-$r$ packet states and the
admissible encoded states above. If $a\in\{p,d\}$ sends $P$ from rank $r$ to
rank $r'$, then

$$
 \mathfrak G_{r'}(aP)=\widehat a\bigl(\mathfrak G_r(P)\bigr).
 \tag{3.2}
$$

Consequently, $\mathfrak G_4$ maps the raw first-exit frontier bijectively to
the frontier obtained by the encoded transitions and the same rank-profile
rule.

**Proof.** From an admissible tuple, reconstruct
$j_i=j_0+\sum_{h<i}g_h$. Positivity orders the indices strictly, and
$j_{r-1}=j_0+n-g_{r-1}<n$ by the phase condition. Place $B_i$ at
$\iota_d^{-1}(j_i)$. This decodes the tuple, while encoding the decoded state
returns it. Conversely, every sorted support satisfies
$g_{r-1}=n+j_0-j_{r-1}>j_0$, so its encoding is admissible.

The identities
$\iota_d(p(q))=\iota_d(q)+1\bmod n$ and
$\iota_d(d(q))=\delta_d(\iota_d(q))$ give (3.2), including the required
block reindexing when an occupied coordinate crosses $n-1\to0$. Equation
(2.3) gives the rank test. Induction over a plateau word preserves the full
raw state and the rank of every prefix; the terminal step is strict on one
side exactly when it is strict on the other. This proves frontier
faithfulness. $\square$

The full map $\delta_d$ is essential in this statement. Kernel, collision
root, and missing image do not determine off-kernel transport.

### A quotient through which the frontier does not descend

**Proposition 3.2 (coarse frontier non-descent).** Let
$Q=\mathcal A=\mathbb Z/5\mathbb Z$,
let $P_\ast$ place the singleton packet $\{q\}$ at $q$, and define

$$
 d=(0,0,1,2,3),\qquad d'=(0,0,2,1,3),
 \tag{3.3}
$$

where the lists give images at inputs $0,1,2,3,4$. The two defects have the
same cycle, kernel $\{0,1\}$, collision root $0$, missing image $4$, and
initial gap/block data, but

$$
 \operatorname{Fr}^{\rm raw}_{5\to4,d}(P_\ast)
 \cap
 \operatorname{Fr}^{\rm raw}_{5\to4,d'}(P_\ast)
 =\varnothing.
 \tag{3.4}
$$

**Proof.** Every rank-five support is all of $Q$, so no $d$-letter is allowed
on the plateau. A candidate endpoint is therefore $d(p^tP_\ast)$ or
$d'(p^tP_\ast)$, with $t$ modulo five. In either endpoint the collision-root
packet is $\{-t,1-t\}$. These five unordered pairs are distinct, so equality
of endpoints would force the same $t$. For that $t$, however, the packet at
coordinate $1$ is $\{2-t\}$ for $d$ and $\{3-t\}$ for $d'$. The endpoints
are unequal. $\square$

Thus the source-addressed frontier is not a function of the cycle, kernel,
root, missing image, and initial gap/block data. The example does not prove
that the entire defect table is irreducible; it rules out this particular
coarse quotient. It also proves a sharper warning used later: output support
and the fused source pair need not determine the surviving packet placement.

### One marked collapse and one permutation

Choose an orientation $K_d=\{k_0,k_1\}$ and define

$$
 e_K(k_1)=k_0,\qquad e_K(q)=q\quad(q\ne k_1).
$$

**Proposition 3.3 (permutation-plus-collapse factorization).** There is a
unique permutation $\rho_d$ with

$$
 \rho_d(q)=d(q)\quad(q\ne k_1),\qquad \rho_d(k_1)=m_d,
 \tag{3.5}
$$

and

$$
 \boxed{d=\rho_d\circ e_K.}
 \tag{3.6}
$$

For every raw packet state,

$$
 d_*P=(\rho_d)_*\bigl((e_K)_*P\bigr).
 \tag{3.7}
$$

The only possible union in $(e_K)_*P$ is the packet pair occupying $K_d$.

**Proof.** The restriction

$$
 d|_{Q\setminus\{k_1\}}:
 Q\setminus\{k_1\}\xrightarrow{\sim}\operatorname{im}(d)
$$

is bijective: it is injective because the only collision of $d$ is $K_d$,
and its domain and codomain both have $n-1$ elements. Assigning the remaining
input $k_1$ to the remaining output $m_d$ gives the unique permutation.
Equation (3.6) follows at every input, and push-forward under a composite map
gives (3.7). $\square$

The rank-five plateau is therefore a system of five labelled particles under
permutation transport and one marked substitution. A strict exit occurs when
both marked kernel coordinates are occupied. The next section records the
particle lineages that support data alone forgets.

## Packet Lineages and the Exact Spectator Quotient

### The lineage lift and boundary incidence

Fix $P_0=(T_0,\Pi_0)$. Before the first strict exit there is no packet fusion
or splitting. Every current packet is therefore one unique source packet.
Record this by an injection

$$
 \lambda:T_0\hookrightarrow Q,
$$

where the source block $\Pi_0(q)$ currently occupies $\lambda(q)$. Its image
is the current support. A letter $a\in\{p,d\}$ is a legal plateau step exactly
when $a$ is injective on $\operatorname{im}\lambda$, and then

$$
 \lambda\xrightarrow{a}a\circ\lambda.
 \tag{4.1}
$$

Let $\mathcal L_5(d;P_0)$ be the least set of injections containing the
inclusion $T_0\hookrightarrow Q$ and closed under (4.1) whenever the step is
legal. Let

$$
 \mathcal L_5^\partial(d;P_0)
 =\{\lambda\in\mathcal L_5(d;P_0):K_d\subseteq\operatorname{im}\lambda\}.
 \tag{4.2}
$$

**Theorem 4.1 (packet-lineage lift).** The map

$$
 \lambda\longmapsto
 \left(\operatorname{im}\lambda,
 q\longmapsto\Pi_0(\lambda^{-1}(q))\right)
 \tag{4.3}
$$

is a bijection from $\mathcal L_5(d;P_0)$ to the raw rank-five packet states
plateau-reachable from $P_0$. It intertwines every legal $p$- or $d$-step.
For $\lambda\in\mathcal L_5^\partial(d;P_0)$, put

$$
 \beta=d\circ\lambda:T_0\to d(\operatorname{im}\lambda).
 \tag{4.4}
$$

The corresponding strict-exit endpoint is

$$
 \Theta_{P_0}(\beta)
 =\left(\operatorname{im}\beta,
 b\longmapsto
 \bigcup_{\substack{q\in T_0\\\beta(q)=b}}\Pi_0(q)\right).
 \tag{4.5}
$$

Moreover, $\Theta_{P_0}$ is a bijection from the boundary-incidence spectrum

$$
 \mathfrak B_d(P_0)
 =\{d\circ\lambda:\lambda\in\mathcal L_5^\partial(d;P_0)\}
 \tag{4.6}
$$

onto $\operatorname{Fr}^{\rm raw}_{5\to4,d}(P_0)$.

**Proof.** Initially (4.3) is $P_0$. If $a$ is injective on the current
support, push-forward moves the block at $\lambda(q)$ to
$a(\lambda(q))$ without union or splitting. This is exactly the state decoded
from $a\circ\lambda$. Induction gives surjectivity onto the plateau-reachable
states. Since the source blocks are nonempty and disjoint, each current block
identifies its unique source block, so the state recovers $\lambda$.

At a terminal support containing $K_d$, the only non-singleton fiber of
$d$ is the kernel pair. Formula (4.5) is therefore precisely the strict
push-forward. Every source block occurs in exactly one output block, whose
coordinate recovers $\beta(q)$. Thus $\Theta_{P_0}$ is both surjective and
injective. $\square$

Every $\beta\in\mathfrak B_d(P_0)$ has a unique decomposition

$$
 F=\beta^{-1}(c_d),\qquad
 s=\beta|_{T_0\setminus F}.
 \tag{4.7}
$$

Here $F$ is the fused source pair and $s$ is the placement of the three
surviving lineages. Define

$$
 \mathfrak F_d(P_0)
 =\{\beta^{-1}(c_d):\beta\in\mathfrak B_d(P_0)\}
 \tag{4.8}
$$

and, for $F\in\mathfrak F_d(P_0)$,

$$
 \mathfrak S_d(P_0;F)
 =\{\beta|_{T_0\setminus F}:
   \beta\in\mathfrak B_d(P_0),\ \beta^{-1}(c_d)=F\}.
 \tag{4.9}
$$

Then

$$
 \mathfrak B_d(P_0)
 \cong
 \bigsqcup_{F\in\mathfrak F_d(P_0)}
 \{F\}\times\mathfrak S_d(P_0;F).
 \tag{4.10}
$$

Equation (4.10) is a decomposition of attained incidences, not a claim that
all formal pairs $(F,s)$ occur. Proposition 3.2 shows why both coordinates
matter: its two defects have the same support and fused source pair but
different survivor placements.

If source and current supports are sorted in defect-anchored coordinates,
the injection $\lambda$ is represented by a permutation in $S_5$. Each legal
plateau edge induces an $S_5$-valued reindexing $\alpha_{a,T}$. Along a
composable path its ordered product is the total lineage permutation. This
edge cocycle records plateau transport; the terminal map $d\circ\lambda$ is
additional boundary data. In particular, Proposition 3.2 has the same
plateau cocycle on both sides and differs only at the terminal survivor map.

### Pair steering with three spectators

Fix a candidate pair $F\subset T_0$, $|F|=2$, and put
$R_0=T_0\setminus F$. Define

$$
 \operatorname{Conf}_{2,3}(Q)
 =\{(A,R):|A|=2,\ |R|=3,\ A\cap R=\varnothing\}.
 \tag{4.11}
$$

The $p$-transition is always defined and sends $(A,R)$ to $(pA,pR)$. The
$d$-transition is defined precisely when

$$
 K_d\not\subseteq A\cup R,
 \tag{4.12}
$$

and then sends $(A,R)$ to $(dA,dR)$. The target set is

$$
 \mathcal K_d
 =\{(K_d,R):|R|=3,\ R\cap K_d=\varnothing\}.
 \tag{4.13}
$$

The guard (4.12) requires the defect to remain injective on both the marked
pair and all three spectators. This is the information ordinary pair hitting
omits.

**Theorem 4.2 (exact spectator-safe quotient).** The map

$$
 q_F(\lambda)=\bigl(\lambda(F),\lambda(R_0)\bigr)
 \tag{4.14}
$$

is the quotient of the full lineage state space by independent relabelling
inside $F$ and inside $R_0$. It intertwines the partial $p,d$ transitions,
maps reachable lineage states onto the reachable subgraph of
$\operatorname{Conf}_{2,3}(Q)$, and satisfies

$$
 \boxed{
 F\in\mathfrak F_d(P_0)
 \iff
 (F,R_0)\leadsto\mathcal K_d
 \text{ in }\operatorname{Conf}_{2,3}(Q).}
 \tag{4.15}
$$

**Proof.** Every $(A,R)$ has a preimage under $q_F$: combine arbitrary
bijections $F\to A$ and $R_0\to R$. Two injections have the same image
exactly when their restrictions differ by precomposition with an element of
$S_2\times S_3$. If $a$ is injective on the five-point support, then

$$
 q_F(a\circ\lambda)
 =(a\lambda(F),a\lambda(R_0))
 =a\,q_F(\lambda).
$$

For $d$, injectivity is exactly (4.12); for $p$ it is automatic. Hence every
lineage path projects. Conversely, applying the labels of a quotient path to
the initial inclusion produces an injection at every stage because each
quotient edge satisfies the same guard. The final state lies in
$\mathcal K_d$ exactly when the lifted injection sends $F$ onto $K_d$.
Equations (4.6) and (4.8) now give (4.15). $\square$

The quotient has

$$
 |\operatorname{Conf}_{2,3}(Q)|
 =\binom n2\binom{n-2}3
 =10\binom n5
 \tag{4.16}
$$

states. It forgets only internal $S_2\times S_3$ labels. The further map
$(A,R)\mapsto A$ is not an exact quotient for target reachability: the
spectator triple determines whether $d$ is enabled. Thus

$$
 \text{full lineage lift}
 \twoheadrightarrow
 \operatorname{Conf}_{2,3}(Q)
 \not\twoheadrightarrow
 \binom Q2
 \tag{4.17}
$$

is the relevant descent boundary.

### Token and hole form

Color the coordinates by $\mathsf P$, $\mathsf S$, and $\mathsf H$, with
multiplicities $2$, $3$, and $n-5$. The marked pair is
$A=c^{-1}(\mathsf P)$, the spectators are $R=c^{-1}(\mathsf S)$, and the
holes are

$$
 H=Q\setminus(A\cup R)=c^{-1}(\mathsf H).
$$

Equivalently, retain $(A,H)$, since $R$ is its complement. Under the
factorization $d=\rho_d\circ e_K$, define

$$
 \bar e_K(H)=Q\setminus e_K(Q\setminus H).
$$

The exact partial transitions become

$$
 p:(A,H)\mapsto(pA,pH),
$$

$$
 d:(A,H)\mapsto
 \bigl(\rho_d(e_K(A)),\rho_d(\bar e_K(H))\bigr),
 \qquad H\cap K_d\ne\varnothing.
 \tag{4.18}
$$

The target condition is $A=K_d$. Formula (4.18) turns the spectator guard
into a hole-shield rule: every internal $d$-step requires at least one hole on
the kernel, while the terminal configuration places the two marked tokens on
both kernel points.

## Canonical Spectator-Safe Reachability

From now on $d=d_n$ is the canonical defect (2.4), with
$K=\{0,1\}$ and $m=n-1$.

### The missing-image section

For a general rank-$(n-1)$ defect, every guarded $d$-output omits $m_d$.
This gives the section

$$
 \Sigma_{m_d}=\{(A,H):m_d\in H\}.
 \tag{5.1}
$$

For $t\in\mathbb Z/n\mathbb Z$, define the partial return

$$
 R_t=d\circ p^t,\qquad
 \operatorname{Dom}(R_t)
 =\{(A,H)\in\Sigma_{m_d}:p^tH\cap K_d\ne\varnothing\}.
 \tag{5.2}
$$

Here $R_t$ acts on the whole token/hole state. Every $R_t$ returns to
$\Sigma_{m_d}$.

**Proposition 5.1 (canonical section symmetry).** Let $n\ge6$ and identify
$D=Q\setminus\{m\}$ with $\mathbb Z/(n-1)\mathbb Z$. On
$\Sigma_n:=\Sigma_m$, the returns $R_1$ and $R_2$ are defined everywhere and

$$
 \boxed{R_1=\operatorname{id}},
 \qquad
 \boxed{R_2=\tau},
 \qquad
 \tau(r)=r+1\pmod{n-1}\quad(r\in D),
 \tag{5.3}
$$

where $R_2$ fixes the missing hole $m$ and rotates all colors on $D$.

**Proof.** A guarded defect output has support in
$\operatorname{im}(d)=Q\setminus\{m_d\}$, proving section entry. In the
canonical section, $m$ is a hole. Since $p(m)=0$ and $p^2(m)=1$, both returns
are guarded. For every $r\in D$,

$$
 d_n(p(r))=r,\qquad d_n(p^2(r))=r+1\pmod{n-1}.
$$

These identities hold simultaneously for every token and every extra hole,
which proves (5.3). $\square$

Thus $R_2$ gives a universal $C_{n-1}$ symmetry on the section. The quotient
$\Sigma_n/\langle R_2\rangle$ consists of cyclic necklaces on $D$ with two
$\mathsf P$ tokens, three $\mathsf S$ tokens, and $n-6$ extra holes.

### The token-order invariant

For any token/hole state, read colors cyclically around $Q$ and delete every
$\mathsf H$. The resulting length-five cyclic word is the **hole-deleted token
order** $\Omega(A,H)$. It has two possible types:

$$
 [\mathsf{PPSSS}]
 \qquad\text{or}\qquad
 [\mathsf{PSPSS}].
 \tag{5.4}
$$

Let $\operatorname{Adj}_\Omega(A,H)$ be $1$ in the first case and $0$ in the
second.

**Lemma 5.2 (order preservation).** Every $p$-step preserves $\Omega$. Every
guarded canonical $d_n$-step also preserves $\Omega$.

**Proof.** The cycle rotates the complete coloring. For a guarded defect
step, at least one of $0,1$ is a hole. If $0$ is a hole, $d_n$ is strictly
order-preserving on the occupied subset of $\{1,\ldots,n-1\}$. If $1$ is a
hole, it is strictly order-preserving on the occupied subset of
$\{0,2,\ldots,n-1\}$. The case in which both are holes satisfies both
descriptions. Deleting holes therefore gives the same cyclic token word.
$\square$

**Lemma 5.3 (hole slide).** Assume $n\ge7$ and $(A,H)\in\Sigma_n$. In the
necklace quotient, a local block $\mathsf H X$, with
$X\in\{\mathsf P,\mathsf S\}$, can be replaced by $X\mathsf H$ without
changing the cyclic order of the other colors.

**Proof.** Use a power of the universal return $R_2$ to place the chosen
block at coordinates $n-3,n-2$. The return $R_3=d_n\circ p^3$ is guarded
because the selected hole moves to kernel coordinate $0$. If $W$ is the
remaining linear word on $D$, direct evaluation gives

$$
 W\,\mathsf H X
 \xrightarrow{R_3}
 X\,\mathsf H W
 \sim_{R_2}
 W\,X\mathsf H.
 \tag{5.5}
$$

The final equivalence is another power of $R_2$. The selected hole crosses
exactly the adjacent token $X$. $\square$

The lemma is constructive: extra holes can move through the fixed cyclic
order of the five non-hole tokens. They change physical gaps but not
$\Omega$.

**Labelled-lift consequence.** The word constructed in Lemma 5.3 also acts on
a fully labelled lineage state. After the same final $R_2$ phase alignment,
it exchanges the selected hole with the selected adjacent lineage and
preserves the cyclic order and identities of every other labelled lineage.
Indeed, the construction selects a coordinate hole and applies the fixed
coordinate maps $R_2$ and $R_3$; it never branches on whether the adjacent
non-hole token has color $\mathsf P$ or $\mathsf S$, nor on its lineage label.
Thus forgetting lineage labels before the move gives exactly the color move
of Lemma 5.3.

### The path-free fused-pair criterion

**Theorem 5.4 (all-$n$ canonical spectator-safe classification).** For every
$n\ge5$ and every $(A,R)\in\operatorname{Conf}_{2,3}(Q)$, with
$H=Q\setminus(A\cup R)$,

$$
 \boxed{
 (A,R)\leadsto\mathcal K_{d_n}
 \iff
 \operatorname{Adj}_\Omega(A,H)=1.}
 \tag{5.6}
$$

Equivalently, for a fixed raw source $P_0$ and $F\subset T_0$, $|F|=2$,

$$
 \boxed{
 F\in\mathfrak F_{d_n}(P_0)
 \iff
 \text{the members of }F\text{ are consecutive in the cyclic order of }T_0.}
 \tag{5.7}
$$

**Proof.** Lemma 5.2 makes $\operatorname{Adj}_\Omega$ invariant along every
spectator-safe path. At the target the marked pair is $K=\{0,1\}$, so its
tokens are adjacent. This proves necessity.

For sufficiency, first let $n=5$. There are no holes, and a power of $p$ sends
any adjacent marked pair to $K$. Let $n\ge6$. If the state is not in
$\Sigma_n$, choose a hole, rotate it to $0$, and apply $d_n$. This guarded
step enters the section and preserves $\Omega$.

When $n=6$, there are no extra holes on $D$. Marked tokens adjacent in
$\Omega$ are physically adjacent on the five-cycle $D$, and a power of $R_2$
sends them to $K$. Let $n\ge7$. Choose the two consecutive marked tokens in
$\Omega$. If their physical gap contains holes, apply Lemma 5.3 to the last
hole before the second marked token. Each slide removes one hole from that
gap and introduces none. Repetition makes the marked tokens physically
adjacent, after which a power of $R_2$ sends them to $K$. This proves (5.6).

At the initial lineage state, $\Omega$ is exactly the cyclic order of $T_0$
with the members of $F$ marked. The exact quotient theorem (4.15) therefore
turns (5.6) into (5.7). $\square$

The bit $\operatorname{Adj}_\Omega$ is complete for this target-reachability
predicate. We do not claim that $\Omega$ is a deterministic transition
congruence, that equal $\Omega$-states have equal shortest words, or that they
are all mutually reachable. The stronger lineage statement needed for the
full frontier is proved next.

## Complete Canonical First-Exit Frontier

Give $T_0$ and $Q$ their positive cyclic orders induced by $p$. An injection
$\lambda:T_0\hookrightarrow Q$ is **cyclic-order preserving** if it preserves
the oriented cyclic order of all five source lineages.

### Reachability of the complete order fiber

**Theorem 6.1 (canonical plateau order-fiber transitivity).** For every
$n\ge5$ and every fixed raw rank-five source $P_0$,

$$
 \boxed{
 \mathcal L_5(d_n;P_0)
 =\{\lambda:T_0\hookrightarrow Q:
   \lambda\text{ preserves cyclic order}\}.}
 \tag{6.1}
$$

The partial plateau graph induced on this set is strongly connected.

**Proof.** Lemma 5.2 remains valid when the five source lineages are given
distinct labels. Hence every plateau transition preserves their oriented
cyclic order, proving the forward inclusion.

For $n=5$, every cyclic-order-preserving bijection of the five-cycle is a
power of $p$. Assume $n\ge6$. Every five-lineage injection has a hole.
Rotating a hole to $0$ and applying $d_n$ gives a guarded entry to the
missing-image section without changing lineage order.

Fix the positive source order $q_0,\ldots,q_4$. For a section injection, let
$g_i$ be the number of extra holes on $D=\{0,\ldots,n-2\}$ after
$\lambda(q_i)$ and before $\lambda(q_{i+1})$, cyclically. Then

$$
 g_i\ge0,\qquad \sum_{i=0}^4g_i=n-6.
 \tag{6.2}
$$

The universal return $R_2$ changes only the common phase. By the labelled-lift
consequence of Lemma 5.3, a hole slide across $q_i$ realizes

$$
 (g_{i-1},g_i)\longmapsto(g_{i-1}-1,g_i+1)
 \qquad(g_{i-1}>0).
 \tag{6.3}
$$

These directed transfers strongly connect all weak compositions of $n-6$
into five parts. To reverse one transfer, move the same hole forward across
the other four tokens; ordinary adjacent transfers then connect every pair
of weak compositions. A power of $R_2$ aligns the remaining phase. Therefore
any two section injections with the same labelled cyclic order are mutually
reachable.

Now let $\lambda^\ast:T_0\hookrightarrow Q$ be any cyclic-order-preserving
target injection. Choose a hole
$h^\ast\notin\operatorname{im}(\lambda^\ast)$ and a power $p^u$ with
$p^u(m)=h^\ast$. Then $p^{-u}\circ\lambda^\ast$, with $p^{-u}$ represented
by a nonnegative power of the cycle, lies in the section. Reach it by the
preceding paragraph and finish with $p^u$. The same argument starts from any
cyclic-order-preserving injection, proving both (6.1) and strong
connectivity. $\square$

Theorem 6.1 is stronger than the target predicate in Theorem 5.4. It
describes the entire plateau-reachable lineage fiber, not only which marked
pairs can occupy the kernel.

### Survivor placements and frontier count

Let $F\in\mathfrak F_{d_n}(P_0)$. By Theorem 5.4, $F$ is a consecutive
source pair. Write the positive source order uniquely as

$$
 (f_0,f_1,r_1,r_2,r_3),\qquad F=\{f_0,f_1\},
 \tag{6.4}
$$

where $f_1$ immediately follows $f_0$.

**Theorem 6.2 (canonical survivor and frontier classification).** In the
notation (6.4),

$$
 \boxed{
 \mathfrak S_{d_n}(P_0;F)
 =\left\{
 s:\{r_1,r_2,r_3\}\hookrightarrow\{1,\ldots,n-2\}:
 1\le s(r_1)<s(r_2)<s(r_3)\le n-2
 \right\}.}
 \tag{6.5}
$$

Consequently,

$$
 \boxed{
 |\mathfrak B_{d_n}(P_0)|
 =|\operatorname{Fr}^{\rm raw}_{5\to4,d_n}(P_0)|
 =5\binom{n-2}{3}.}
 \tag{6.6}
$$

**Proof.** Let $\lambda$ be terminal with $\lambda(F)=K=\{0,1\}$.
Cyclic-order preservation forces

$$
 \lambda(f_0)=0,\qquad \lambda(f_1)=1,\qquad
 2\le\lambda(r_1)<\lambda(r_2)<\lambda(r_3)\le n-1.
 \tag{6.7}
$$

The strict $d_n$-step sends each survivor to

$$
 s(r_i)=d_n(\lambda(r_i))=\lambda(r_i)-1,
$$

giving the inequalities in (6.5).

Conversely, choose any
$1\le u_1<u_2<u_3\le n-2$ and define

$$
 \lambda^\ast(f_0)=0,\qquad
 \lambda^\ast(f_1)=1,\qquad
 \lambda^\ast(r_i)=u_i+1.
 \tag{6.8}
$$

This injection preserves the source cyclic order. Theorem 6.1 supplies a
plateau path to it. The next $d_n$-step is strict and has survivor placement
$s(r_i)=u_i$. This proves (6.5).

There are five consecutive source pairs and $\binom{n-2}{3}$ increasing
survivor triples for each. Different pairs have different two-element fibers
over the collision root. Theorem 4.1 identifies boundary-incidence maps with
raw endpoints, proving (6.6). $\square$

Equations (5.7) and (6.5) give a path-free membership test for the full
canonical incidence spectrum. A map $\beta:T_0\to\{0,\ldots,n-2\}$ belongs
to $\mathfrak B_{d_n}(P_0)$ exactly when:

1. $\beta^{-1}(0)$ is a consecutive pair in the cyclic order of $T_0$;
2. $\beta$ is injective on the other three source lineages; and
3. after orienting the fused pair as in (6.4), the survivor coordinates are
   strictly increasing in the remaining positive source order.

No path search occurs in this criterion.

### Independence from packet masses and atom composition

The dynamics above use source packets as distinguishable lineage labels.
Their sizes and internal atom structure never enter the reachability proofs.

**Corollary 6.3 (source-block independence of the raw incidence frontier).**
Let $P_0=(T_0,\Pi_0)$ and $P_0'=(T_0',\Pi_0')$ be raw rank-five sources for
the same canonical automaton, possibly on different labelled atom carriers.
Let $\theta:T_0\to T_0'$ preserve positive cyclic order. Then

$$
 \beta\longmapsto\beta\circ\theta^{-1}
 \tag{6.9}
$$

is a bijection

$$
 \mathfrak B_{d_n}(P_0)
 \overset{\sim}{\longrightarrow}
 \mathfrak B_{d_n}(P_0').
 \tag{6.10}
$$

After replacing each source block $\Pi_0(q)$ by
$\Pi_0'(\theta(q))$, formula (4.5) transports this bijection to an incidence
isomorphism of the two raw first-exit frontiers. Hence the canonical raw
frontier depends on source blocks only through their five lineage labels and
positive cyclic order, not through packet masses or internal atom
composition.

**Proof.** Theorem 5.4 characterizes fused pairs by cyclic adjacency, which
$\theta$ preserves. For each such pair, Theorem 6.2 characterizes survivor
placements solely by the induced positive order. Precomposition with
$\theta^{-1}$ therefore preserves and reflects all conditions in (6.5),
giving (6.10). The decoding formula (4.5) then replaces lineage labels by the
corresponding packet blocks. $\square$

This is a raw incidence statement. It is not a descent theorem for typed
roles, ancestry, target normalization, or any other semantics carried by a
packet beyond its identity in the raw source partition.

## Boundary to Typed Transfer and Projectability

The preceding classification answers the intrinsic first-exit question. It
does not by itself answer whether an endpoint is present in a separately
declared transfer relation.

Paper XXVIII fixes, for an inherited pair $z$, a complete transfer fiber
$\mathcal T_{5\to4}(z)$ and a projectable subfiber
$\mathcal T_{5\to4}^{\rm proj}(z)$ [@paper28]. Its open supply problem is

$$
 \forall z\in\operatorname{Sec}_4^{\rm inh},\qquad
 \mathcal T_{5\to4}^{\rm proj}(z)\ne\varnothing.
 \tag{7.1}
$$

Theorem 6.2 cannot be substituted for (7.1). The two statements read
different objects:

| Raw theorem provides | Typed bridge would additionally require |
|---|---|
| exact five-packet plateau and strict-exit replay | membership in the fixed complete transfer fiber |
| fused source pair and survivor placement | source authorization and rooted role/ancestry reads |
| source-addressed rank-four packet endpoint | declared target incidence and normalized typed handoff |
| one raw path witnessing the endpoint | a projection witness on that same transfer and entry |

The first attempted promotion already reaches data absent from the raw state:
authorization reads a typed source graph with rooted roles and ancestry, while
projectability reads the fixed transfer binding, exact update, and handoff.
This is an interface gap, not a counterexample. The raw theorem neither proves
nor disproves any one of those predicates.

A future bridge may take the following conditional form. If a declared
transfer relation is proved complete with respect to the canonical raw
incidences of Theorem 6.2, and if one attained incidence carries the required
same-witness authorization and projection data, then it supplies a
projectable origin. Neither premise is established here. In particular:

$$
 \text{raw frontier nonempty}
 \not\Rightarrow
 \text{declared transfer incidence}
 \not\Rightarrow
 \text{projectability}.
 \tag{7.2}
$$

No new semantic field or refined constructor is introduced to force this
bridge. Projectable-Origin Supply remains motivation and future work rather
than a promised conclusion of the raw classification.

## Computational Artifacts

The paper-owned evidence package is available under
[`experiments/paper29/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper29)
in the RIME repository.

| Surface | Paper-owned path | Role |
|---|---|---|
| Finite exact control | `canonical_frontier.py` and `results/` | Replays the intrinsic definitions for $5\le n\le12$ |
| Partial formalization | `lean/` | Checks the data-independent incidence, quotient, counting, and boundary spine |
| Release validation | `release-manifest.json` and the public receipt under `results/` | Binds the manuscript, reader PDF, bibliography, development closure, and validators |

The finite audit is not the proof of the all-$n$ theorem, and the Lean
development does not formalize the geometric hole-slide argument. The public
receipt records local closure verification and performed replay; it is not an
independent mathematical validation.

## Claim Status and Boundary

| Claim surface | Status | Scope |
|---|---|---|
| Faithful defect-anchored packet encoding | Proposition 3.1 | Every labelled binary-kernel rank-$(n-1)$ defect, $n\ge5$ |
| Coarse quotient non-descent | Proposition 3.2 | Explicit five-state matched control |
| Permutation-plus-collapse factorization | Proposition 3.3 | Every rank-$(n-1)$ defect after choosing a kernel orientation |
| Lineage lift and boundary-incidence spectrum | Theorem 4.1 | Every fixed raw rank-five source and labelled defect |
| Exact $2+3$ spectator-safe quotient | Theorem 4.2 | Fused-pair reachability for every labelled defect |
| Canonical fused-pair criterion | Theorem 5.4 | All $n\ge5$ for $d_n$ |
| Canonical order-fiber transitivity | Theorem 6.1 | All $n\ge5$ for $d_n$ |
| Complete survivor spectrum and frontier count | Theorem 6.2 | All $n\ge5$ for $d_n$ |
| Source-block independence of the incidence frontier | Corollary 6.3 | Sources with the same labelled cyclic-order skeleton |
| General-defect path-free classification | Open | Off-kernel transport may alter token order and survivor placement |
| Typed transfer incidence and Projectable-Origin Supply | Open bridge | Not decided by raw packet geometry alone |

All positive claims above have direct mathematical proofs in the manuscript.
Finite graph searches used during development are sanity checks, not premises,
certificates, or an additional evidence level. The paper claims no shortest
safe-word formula, path-length bound, reset threshold, credit settlement,
uniform recursive menu, or all-rank descent theorem.

## Conclusion

Rank-five first exit is neither a support-only event nor an ordinary pair-hit.
The correct raw object retains source-packet lineages until the first strict
defect step. For fused-pair reachability, those lineages admit an exact
$S_2\times S_3$ quotient: a marked pair moving with three spectators under a
partial token/hole dynamics.

For the canonical single-defect circular family, that dynamics has a complete
normal form. Guarded moves preserve the cyclic order of the five non-hole
tokens, while section returns slide holes through that order. A pair reaches
the kernel exactly when its source lineages are consecutive. The entire
cyclic-order fiber is plateau-reachable, which then makes every increasing
survivor placement attainable. The resulting raw frontier has exactly
$5\binom{n-2}{3}$ endpoints and is independent of packet masses and internal
atom composition at the incidence level.

Two natural problems remain. For a general defect
$d=\rho_d\circ e_K$, one may ask which quotient of the off-kernel transport
$\rho_d$ determines spectator-safe reachability and survivor placement. At
the typed level, one may ask when the canonical raw incidences are realized
inside a declared transfer fiber with a same-witness projection. The first is
a generalization of the intrinsic geometry developed here. The second is the
open bridge to Projectable-Origin Supply. Neither is needed for the complete
canonical raw classification proved in this paper.

::: {#refs}
:::
