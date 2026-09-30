# Five-Token Dynamics Beyond Lane-Order Symmetry
### Local Dihedral Closure and a Complete Single-Lane Permutation Dichotomy

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXII | Version 1.0**

*This paper (Paper XXXII of the RIME program) studies intrinsic raw
spectator-safe return dynamics beyond lane-order symmetry. It imports the
normalized partial-return system and exact path simulation of Paper XXXI, but
no typed transfer, projectability, recursive-return, credit-settlement, or
reset-bound conclusion.*

---

## Abstract

**Problem.** Paper XXXI reduces a binary-kernel single-defect return system to
a partial system on two marked tokens, three spectators, and the remaining
holes, with an arbitrary branch permutation $a\in\operatorname{Sym}(E)$.
For normalizer branches, lane adjacency is sufficient for Safe-Hit and
same-lane incidence is necessary. The unresolved region consists of
same-lane configurations whose marked tokens are not adjacent after holes
are deleted.

**Approach.** We first isolate the exact geometric condition used by the
negative direction: the branch permutation must carry every arithmetic lane
to a lane by a cycle-graph isomorphism. We then restrict to the one-lane regime
$\gcd(n,\Delta)=1$. A state with fixed hole-deleted token order is encoded by
a weak composition

$$
 (h_0,\ldots,h_4),
 \qquad
 h_i\ge0,
 \qquad
 \sum_i h_i=n-6.
$$

A guarded identity-branch return transfers one hole from a gap to the
preceding gap. These directed transfers are strongly connected on every fixed
weak-composition fiber.

**Results.** Lane-wise cycle-graph isomorphisms introduce no new Safe-Hit
states. This includes affine normalizer branches with mixed
Chinese-remainder signs not covered by one global $\pm1$ congruence. In the
one-lane regime, identity-branch dynamics is transitive on every
hole-deleted five-token order fiber. Let $C_L$ be the physical lane cycle,
with $L=n-1$. For every branch permutation $a\in\operatorname{Sym}(E)$,

$$
 \operatorname{Hit}(a)=
 \begin{cases}
  \operatorname{Adj},&a\in\operatorname{Aut}(C_L),\\
  \mathcal Z_\Delta,&a\notin\operatorname{Aut}(C_L).
 \end{cases}
$$

Thus every non-dihedral single-lane branch permutation makes all marked
five-token configurations spectator-safely target-reachable.

**Boundary.** The theorem does not classify the multi-lane regime. For a
branch preserving the arithmetic lane partition, order breaking may occur on
only one lane, and a proof would need a lane-type-sensitive mobility theorem.
The paper also does not classify survivor placement or lift raw Safe-Hit to
typed transfer semantics.

**Keywords.** synchronizing automata; single-defect automata; partial
dynamics; branch permutations; cycle automorphisms; Safe-Hit; guarded
reachability

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/n\mathbb Z$ | labelled circular carrier, $n\ge6$ |
| $p(q)=q+1$ | fixed full cycle |
| $\Delta$ | oriented kernel separation |
| $g=\gcd(n,\Delta)$ | number of arithmetic lanes before puncturing |
| $\ell=n/g$ | full lane length |
| $E=Q\setminus\{0\}$ | normalized branch carrier |
| $\widehat\Sigma=\operatorname{Conf}_{2,3}(E)$ | two marked tokens and three spectators |
| $\psi_\Delta$ | punctured rotation on $E$ |
| $H_\Delta=\langle\psi_\Delta\rangle$ | globally enabled cyclic return subgroup |
| $\mathcal Z_\Delta=\widehat\Sigma/H_\Delta$ | punctured-rotation orbit space |
| $R_r^{(0)}$ | identity-branch relation-valued quotient edge |
| $W_\Delta=N_{\operatorname{Sym}(E)}(H_\Delta)/H_\Delta$ | affine twist quotient |
| $\mathcal C_\Delta$ | arithmetic-lane partition of $E$ |
| $\operatorname{Stab}(\mathcal C_\Delta)$ | permutations carrying each lane to a lane |
| $\mathsf{Adj}_\Delta$ | lane-adjacent orbit set |
| $\mathsf{Same}_\Delta$ | same-lane orbit set |
| $\mathsf{Hit}(a)$ | orbit-wise Safe-Hit truth set for branch $a$ |
| $\Omega(x)$ | hole-deleted cyclic $\mathsf P/\mathsf S$ word |
| $L=n-1$ | unique lane length when $g=1$ |
| $C_L$ | physical cycle graph induced by $\psi_\Delta$ in the one-lane regime |

## Introduction

Paper XXXI normalizes every labelled partial return of a binary-kernel
rank-$(n-1)$ defect into the point map

$$
 \phi_r=\varepsilon_\Delta p^ra
 \tag{1.1}
$$

on a carrier with two marked tokens, three spectators, and holes
[@paper31]. The formula transports the collision guard, the normalized exit
target, and labelled paths exactly. When the branch permutation $a$
normalizes the punctured-rotation group

$$
 H_\Delta=\langle\psi_\Delta\rangle,
 \tag{1.2}
$$

the quotient dynamics is a finite relation-valued skew system. Paper XXXI
proves the general sandwich

$$
 \operatorname{LaneAdj}_\Delta(x)
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \Longrightarrow
 \operatorname{SameLane}_\Delta(x).
 \tag{1.3}
$$

It also closes multipliers satisfying one global congruence
$u\equiv\pm1$ modulo the order of $\psi_\Delta$.

Two questions remain hidden inside that formulation.

First, normalizer membership is stronger than the geometric condition used
by the negative proof. It is enough that a branch permutation carry every
arithmetic lane to a lane by a cycle-graph isomorphism. For affine normalizer
branches this includes mixed Chinese-remainder signs that preserve order on
one lane length and reverse it on the other.

Second, a branch permutation that is not an automorphism of the physical lane
cycle sends some nonedge to an edge. The smallest regime in which the guarded
consequence can be isolated is the one-lane case

$$
 g=\gcd(n,\Delta)=1.
 \tag{1.4}
$$

There every state is same-lane. The entire open part of (1.3) is therefore
the nonadjacent token-order class.

The paper proves that this class is completely promoted by every
non-dihedral branch permutation. The dynamical ingredient is a
source-preserving mobility theorem. For a fixed cyclic order of the five
occupied tokens, record the numbers of holes in the five intervening gaps.
A guarded return moves one hole one step around the gap cycle. Since the
reverse unit move is a four-step forward circuit, the resulting directed
weak-composition graph is strongly connected. This turns the elementary
nonedge-to-edge witness into an actual guarded path.

The theorem spine is:

1. Section 2 freezes the exact branch system inherited from Paper XXXI.
2. Section 3 closes every branch that is dihedral on each arithmetic lane.
3. Section 4 proves single-lane order-fiber transitivity by guarded hole
   transfers.
4. Section 5 combines that mobility with cycle-edge conversion to classify
   every single-lane branch permutation.
5. Section 6 records the lane-stabilizer sandwich and the precise multi-lane
   boundary.

The work remains intrinsic and raw. It does not reconstruct a defect,
classify survivor placement, or import downstream typed authority.

### Related Work and Novelty Boundary

The Černý conjecture and the broader theory of synchronizing automata concern
short reset words [@cerny1964; @volkov2008; @volkov2022survey]. Circular
automata and almost-group automata provide nearby structural settings
[@dubuc1998; @berlinkovNicaud2020; @casasTorres2024]. This paper proves no
reset bound and no classification of general almost-group automata.

Monotonic automata, subset synchronization, careful synchronization, and
dynamic word constraints study related order or partiality phenomena
[@eppstein1990; @ryzhikovShemyakov2018; @wolf2020]. Complete reachability asks
which unlabelled subsets can occur as images
[@don2016; @gonzeJungers2018; @ferensSzykula2026]. The present condition is
different: one guarded path must preserve injectivity of the marked pair and
all three spectators at every step and must hit a source-marked target.

Within the RIME line, Paper XXIX proves the canonical raw rank-five frontier
classification, Paper XXX identifies the universal return group and free
branch parameter, and Paper XXXI derives the normalized partial system and
the multi-lane cyclic-branch classification
[@paper29; @paper30; @paper31]. The present paper begins at the remaining
branch-permutation frontier. Its new claims are lane-wise dihedral closure and
a complete one-lane permutation Safe-Hit theorem.

## The Inherited Branch System

Fix $n\ge6$ and $1\le\Delta\le n-1$. Put

$$
 g=\gcd(n,\Delta),
 \qquad
 \ell=\frac ng,
 \qquad
 E=\mathbb Z/n\mathbb Z\setminus\{0\}.
 \tag{2.1}
$$

Let

$$
 \widehat\Sigma=\operatorname{Conf}_{2,3}(E)
 \tag{2.2}
$$

be the states $x=(A,R)$ with $|A|=2$, $|R|=3$, and $A\cap R=\varnothing$.
The points of $A$ carry color $\mathsf P$, the points of $R$ carry color
$\mathsf S$, and all remaining points of $E$ are holes.

Paper XXXI defines

$$
 \psi_\Delta=\varepsilon_\Delta p^\Delta|_E,
 \qquad
 H_\Delta=\langle\psi_\Delta\rangle,
 \qquad
 \mathcal Z_\Delta=\widehat\Sigma/H_\Delta.
 \tag{2.3}
$$

The cycles of $\psi_\Delta$ are one punctured lane of length $\ell-1$ and,
when $g>1$, $g-1$ ordinary lanes of length $\ell$.

Lane adjacency and same-lane incidence are constant on $H_\Delta$-orbits and
therefore define

$$
 \mathsf{Adj}_\Delta
 \subseteq
 \mathsf{Same}_\Delta
 \subseteq
 \mathcal Z_\Delta.
 \tag{2.4}
$$

### Arbitrary branch permutations

For every $a\in\operatorname{Sym}(E)$, the inherited normalized partial
returns have point maps

$$
 \phi_r^{(a)}=\varepsilon_\Delta p^ra,
 \qquad
 \widehat{\mathcal T}_{\Delta,a}
 =a_\#^{-1}\widehat{\mathcal T}_{\Delta,\operatorname{id}},
 \tag{2.5}
$$

with the collision guard transported exactly as in Paper XXXI. The branch
need not normalize $H_\Delta$.

We use the following consequence of Paper XXXI repeatedly.

**Lemma 2.1 (pathwise identity simulation).** Let
$a\in\operatorname{Sym}(E)$. Every finite guarded identity-branch path

$$
 x\xrightarrow{r_1,\ldots,r_k}_{\operatorname{id}}y
 \tag{2.6}
$$

has a finite guarded realization from $x$ to the same state $y$ in the
$a$-system.

**Proof.** Let $m=\operatorname{ord}(a)$. The label-zero return in the
$a$-system is the globally enabled permutation $a_\#$. Before simulating an
identity edge with label $r$, apply the block $0^{m-1}$ and then $r$. At the
point-map level this is

$$
 (\varepsilon_\Delta p^ra)_\#
 (a^{-1})_\#
 =
 (\varepsilon_\Delta p^r)_\#.
 \tag{2.7}
$$

Its guard is exactly the guard of the identity edge being simulated.
Concatenating these blocks realizes the complete path. This is the pathwise
content of the identity-branch simulation theorem of Paper XXXI.

If $y\in\widehat{\mathcal T}_{\Delta,\operatorname{id}}$, append one more
block $0^{m-1}$. It reaches
$a_\#^{-1}y\in\widehat{\mathcal T}_{\Delta,a}$, so

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,\operatorname{id}}(x)
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x).}
 \tag{2.8}
$$

$\square$

Powers of $\psi_\Delta$ give mutual identity-branch paths between all
representatives of one $H_\Delta$-orbit. Applying the lemma in both directions
shows that Safe-Hit truth for arbitrary $a$ is constant on each such orbit.
Thus the primary truth sets of this paper are

$$
 \boxed{
 \mathsf{Hit}(a)
 =\{\pi_H(x):
   \operatorname{SafeHit}_{n,\Delta,a}(x)\},
 \qquad
 \mathsf{Prom}(a)
 =\mathsf{Hit}(a)\cap
  (\mathsf{Same}_\Delta\setminus\mathsf{Adj}_\Delta).}
 \tag{2.9}
$$

Definition (2.9) does not assert that $a$ induces a deterministic map on
$\mathcal Z_\Delta$. It records orbit-wise truth only.

### Normalizer specialization

For a normalizer branch

$$
 a\in N_{\operatorname{Sym}(E)}(H_\Delta),
 \tag{2.10}
$$

write $\bar a$ for its induced permutation of $\mathcal Z_\Delta$. If
$R_r^{(0)}$ is the relation-valued identity-branch quotient edge, the exact
skew edge is

$$
 \boxed{
 O\xrightarrow{r}_a O'
 \iff
 \bar a(O)\,R_r^{(0)}\,O'.}
 \tag{2.11}
$$

The target-orbit set satisfies

$$
 \mathcal T_a=\bar a^{-1}\mathcal T_0,
 \tag{2.12}
$$

and quotient reachability lifts exactly:

$$
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \pi_H(x)\leadsto_a\mathcal T_a.
 \tag{2.13}
$$

No deterministic quotient map is asserted in (2.11). Put

$$
 W_\Delta
 =N_{\operatorname{Sym}(E)}(H_\Delta)/H_\Delta.
 \tag{2.14}
$$

Paper XXXI's cyclic-branch exponent-elimination theorem shows that quotient
Safe-Hit depends only on $w\in W_\Delta$. For any representative $a$ of $w$,
define

$$
 \mathsf{Hit}(w)
 =\{O\in\mathcal Z_\Delta:O\leadsto_w\mathcal T_w\}
 =\mathsf{Hit}(a).
 \tag{2.15}
$$

The inherited normalizer sandwich is

$$
 \boxed{
 \mathsf{Adj}_\Delta
 \subseteq
 \mathsf{Hit}(w)
 \subseteq
 \mathsf{Same}_\Delta.}
 \tag{2.16}
$$

## Lane-Wise Dihedral Closure

In the affine lane coordinates of Paper XXXI, a normalizer representative has
the form

$$
 \begin{aligned}
 a(*,t)&=(*,ut+\beta_*)&&\pmod{\ell-1},\\
 a(j,t)&=(\sigma(j),ut+\beta_j)&&\pmod\ell.
 \end{aligned}
 \tag{3.1}
$$

The global modulus used to encode the multiplier is

$$
 M=
 \begin{cases}
  \ell-1,&g=1,\\
  \ell(\ell-1),&g>1.
 \end{cases}
 \tag{3.2}
$$

The condition $u\equiv\pm1\pmod M$ is sufficient for preserving or reversing
all lane orders, but it is not necessary when two lane lengths occur.

Let $\mathcal C_\Delta$ be the set of $\psi_\Delta$-cycles and define its
setwise stabilizer

$$
 \operatorname{Stab}(\mathcal C_\Delta)
 =\{a\in\operatorname{Sym}(E):
     a(C)\in\mathcal C_\Delta
     \text{ for every }C\in\mathcal C_\Delta\}.
 \tag{3.3}
$$

Each lane carries the cycle graph induced by its $\psi_\Delta$ order. Put

$$
 \operatorname{LocalDih}_\Delta(a)
 \iff
 a\in\operatorname{Stab}(\mathcal C_\Delta)
 \text{ and every }
 a|_C:C\longrightarrow a(C)
 \text{ is a cycle-graph isomorphism}.
 \tag{3.4}
$$

For a normalizer representative in (3.1), condition (3.4) says that
$t\mapsto ut$ preserves or reverses cyclic order modulo every lane length
that occurs. For lengths at least three this is $u\equiv\pm1$ at that length;
for lengths at most two it is automatic. The signs on the punctured and
ordinary lane lengths may differ.

**Proposition 3.1 (lane-wise dihedral classification).** Let
$a\in\operatorname{Sym}(E)$. If
$\operatorname{LocalDih}_\Delta(a)$, then for every
$x\in\widehat\Sigma$,

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.}
 \tag{3.5}
$$

**Proof.** The branch permutation $a$ maps lanes to lanes and preserves or
reverses their cyclic orders, so it preserves lane adjacency. Every guarded
identity-branch return preserves the same observable. Since an $a$-return is
an identity-branch point map preceded by $a_\#$, every guarded $a$-return
preserves lane adjacency. The target
$\widehat{\mathcal T}_{\Delta,a}
=a_\#^{-1}\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ is lane-adjacent,
so adjacency is necessary. Conversely, the identity-branch classification
of Paper XXXI makes every lane-adjacent state identity-hittable, and (2.8)
simulates that witness in the $a$-system. $\square$

Proposition 3.1 is strictly broader than the affine normalizer statement. In
that subfamily it removes a false dichotomy: a multiplier may fail the single
global congruence $u\equiv\pm1\pmod M$ while remaining dihedral on each lane
length by mixed Chinese-remainder signs. Such a branch creates no new
Safe-Hit state.

## Single-Lane Order-Fiber Transitivity

Assume for the rest of Sections 4 and 5 that

$$
 g=1,
 \qquad
 L=n-1.
 \tag{4.1}
$$

There is one $\psi_\Delta$-lane, of length $L$. Since $n\ge6$, we have
$L\ge5$. Every configuration is same-lane.

For $x\in\widehat\Sigma$, read the five occupied tokens cyclically along the
$\psi_\Delta$-lane and delete all holes. Denote the resulting cyclic
$\mathsf P/\mathsf S$ word by $\Omega(x)$. Temporarily distinguish the
occupied positions in that cyclic order as

$$
 T_0,T_1,T_2,T_3,T_4.
 \tag{4.2}
$$

Let $h_i$ be the number of holes after $T_i$ and before $T_{i+1}$, with
indices modulo $5$. Then

$$
 h_i\ge0,
 \qquad
 \sum_{i=0}^4h_i=L-5=n-6.
 \tag{4.3}
$$

### The local gap transfer

**Lemma 4.1 (guarded unit gap transfer).** If $h_i>0$, there is a guarded
identity-branch path preserving $\Omega(x)$ and changing only

$$
 \boxed{
 (h_{i-1},h_i)
 \longmapsto
 (h_{i-1}+1,h_i-1).}
 \tag{4.4}
$$

**Proof.** A power of the globally enabled return $\psi_\Delta$ places
$T_i$ at $\Delta$. Since $h_i>0$, the next lane position $2\Delta$ is a
hole. Apply the identity-branch return with label $r=-\Delta$.

The potential collision pair is occupied at $\Delta$ and empty at
$2\Delta$, so the return is guarded. It fixes $T_i$, shifts the later
positions of the following gap one $\Delta$-step toward $T_i$, removes the
first hole after $T_i$, and creates the compensating hole at the preceding
lane position $-\Delta$. Explicitly, since $g=1$, the points of $E$ are
$j\Delta$ for $1\le j\le n-1$, and

$$
 \phi_{-\Delta}(\Delta)=\Delta,
 \qquad
 \phi_{-\Delta}(j\Delta)=(j-1)\Delta
 \quad(2\le j\le n-1).
$$

The second preimage of $\Delta$, namely $2\Delta$, is the required hole, and
$-\Delta$ is absent from the image support. Hence (4.4) holds. The
lane-order preservation
theorem of Paper XXXI shows that no occupied tokens cross. The token color is
irrelevant to the guard and to the transfer. $\square$

Let

$$
 \mathcal H_N
 =\{(h_0,\ldots,h_4)\in\mathbb Z_{\ge0}^5:
   h_0+\cdots+h_4=N\}
 \tag{4.5}
$$

with $N=L-5$.

**Lemma 4.2 (directed gap connectivity).** The directed moves

$$
 h\longmapsto h+e_{i-1}-e_i
 \qquad(h_i>0)
 \tag{4.6}
$$

make $\mathcal H_N$ strongly connected.

**Proof.** Each move transports one unit one step around the directed
five-cycle of gap indices. Its apparent reverse, from gap $i-1$ to gap $i$,
is realized by transporting the same unit through the other four directed
edges:

$$
 i-1\longrightarrow i-2\longrightarrow i-3
 \longrightarrow i-4\longrightarrow i
 \pmod5.
 \tag{4.7}
$$

At every intermediate stage the gap currently carrying that unit is
positive. Thus every elementary transfer between adjacent parts is
reversible by a directed path. The ordinary graph of weak compositions with
fixed total $N$ is connected under adjacent unit transfers, so the directed
graph is strongly connected. The case $N=0$ is the single-vertex case.
$\square$

**Theorem 4.3 (single-lane order-fiber transitivity).** If
$\Omega(x)=\Omega(y)$, then

$$
 x\leftrightsquigarrow_{\operatorname{id}}y
 \tag{4.8}
$$

by guarded identity-branch returns.

**Proof.** Choose a cyclic identification of the five temporary token labels
that respects the common color word. Lemmas 4.1 and 4.2 transform the source
gap vector into the target gap vector without changing that cyclic token
order. Once the gap vectors agree, a power of the regular cyclic return
$\psi_\Delta$ aligns $T_0$ with its target coordinate. All other occupied
coordinates and colors then agree automatically. Strong connectivity gives
the reverse path. $\square$

The theorem is stronger than the hole-slide used in Paper XXXI. That argument
decreased one selected marked-pair gap. Here every occupied token may serve
as the transfer site, so the complete order fiber is connected.

## The Single-Lane Permutation Dichotomy

Let $C_L$ be the physical cycle graph on $E$ induced by the regular
$\psi_\Delta$ action. Its edge set is

$$
 \mathcal E_L
 =\bigl\{\{q,\psi_\Delta(q)\}:q\in E\bigr\}.
 \tag{5.1}
$$

The group $\operatorname{Aut}(C_L)$ is the set of branch permutations that
preserve $\mathcal E_L$. We use this notation instead of $D_L$ or $D_{2L}$
to avoid dihedral-order conventions.

There are exactly two cyclic color-order classes:

$$
 [\mathsf{PPSSS}]
 \qquad\text{and}\qquad
 [\mathsf{PSPSS}].
 \tag{5.2}
$$

The first is lane-adjacent; the second is nonadjacent. By (2.9),
$\mathsf{Hit}(a)$ and $\mathsf{Prom}(a)$ are defined on
$\mathcal Z_\Delta$ for every $a\in\operatorname{Sym}(E)$, even when $a$
does not normalize $H_\Delta$.

### Cycle-edge conversion

For a permutation $a$ of $E$,

$$
 a\in\operatorname{Aut}(C_L)
 \iff
 a(\mathcal E_L)=\mathcal E_L.
 \tag{5.3}
$$

If $a\notin\operatorname{Aut}(C_L)$, then $a(\mathcal E_L)$ and
$\mathcal E_L$ are distinct sets of the same cardinality $L$. Hence some
edge is missing from $a(\mathcal E_L)$. Taking its inverse image gives a
two-set $B\subset E$ such that

$$
 \boxed{
 B\notin\mathcal E_L,
 \qquad
 a(B)\in\mathcal E_L.}
 \tag{5.4}
$$

Both open arcs of $C_L\setminus B$ are nonempty. Since $L\ge5$, the three
spectators can be placed with at least one on each arc. Thus there is a state
$y$ with

$$
 A_y=B,
 \qquad
 \Omega(y)=[\mathsf{PSPSS}],
 \tag{5.5}
$$

while the globally enabled label-zero return $a_\#$ sends its marked pair to
the physical edge $a(B)$. As before, the placement (5.5) is not itself a
reachability proof; Theorem 4.3 supplies the actual guarded path to it.

**Theorem 5.1 (single-lane permutation dichotomy).** Let $g=1$ and
$L=n-1$. For every $a\in\operatorname{Sym}(E)$,

$$
 \boxed{
 \mathsf{Hit}(a)=
 \begin{cases}
  \mathsf{Adj}_\Delta,
    &a\in\operatorname{Aut}(C_L),\\[1mm]
  \mathcal Z_\Delta,
    &a\notin\operatorname{Aut}(C_L).
 \end{cases}}
 \tag{5.6}
$$

**Proof.** If $a\in\operatorname{Aut}(C_L)$, there is one lane and $a$ is
lane-wise dihedral. Proposition 3.1 gives the first line.

Now suppose $a\notin\operatorname{Aut}(C_L)$. Every adjacent orbit lies in
$\mathsf{Hit}(a)$ by (2.8) and the identity-branch classification. Let $x$
be nonadjacent. Its token order is $[\mathsf{PSPSS}]$. Choose $B$ and $y$ as
in (5.4)--(5.5). Theorem 4.3 gives a guarded identity-branch path from $x$ to
$y$, and Lemma 2.1 simulates that path in the $a$-system, ending at the same
state $y$.

Apply the globally enabled label-zero return. The resulting marked pair is
the physical edge $a(B)$ and is therefore lane-adjacent. The
identity-branch Safe-Hit theorem together with (2.8) supplies a guarded
continuation to the $a$-target. Thus every nonadjacent orbit also lies in
$\mathsf{Hit}(a)$, proving the second line. $\square$

**Corollary 5.2 (exact promotion set).** In the one-lane regime,

$$
 \mathsf{Prom}(a)=
 \begin{cases}
  \varnothing,&a\in\operatorname{Aut}(C_L),\\
  \mathcal Z_\Delta\setminus\mathsf{Adj}_\Delta,
    &a\notin\operatorname{Aut}(C_L).
 \end{cases}
 \tag{5.7}
$$

**Proof.** Subtract $\mathsf{Adj}_\Delta$ from the two cases of
Theorem 5.1 and use (2.9). $\square$

The theorem compares truth predicates. It does not assert equality of
labelled path languages, equality of shortest witnesses, or a deterministic
quotient of every partial return. In particular, the affine normalizer
dichotomy is now only a specialization: an affine map
$t\mapsto ut+\beta$ belongs to $\operatorname{Aut}(C_L)$ exactly when
$u\equiv\pm1\pmod L$.

## Multi-Lane Boundary

When $g>1$, the punctured lane has length $\ell-1$ and ordinary lanes have
length $\ell$. The full lane-partition stabilizer has the natural form

$$
 \operatorname{Stab}(\mathcal C_\Delta)
 \cong
 S_{\ell-1}
 \times
 \left(S_\ell^{\,g-1}\rtimes S_{g-1}\right).
 \tag{6.1}
$$

The first factor acts on the unique punctured lane; the wreath-product factor
acts independently inside the ordinary lanes and permutes those lanes. The
normalizer $N_{\operatorname{Sym}(E)}(H_\Delta)$ is the thinner subfamily in
which all lane restrictions share one multiplier.

For $a\in\operatorname{Stab}(\mathcal C_\Delta)$, define

$$
 \operatorname{Break}_\Delta(a)
 =\{C\in\mathcal C_\Delta:
      a|_C:C\to a(C)
      \text{ is not a cycle-graph isomorphism}\}.
 \tag{6.2}
$$

Proposition 3.1 closes the case
$\operatorname{Break}_\Delta(a)=\varnothing$. The full stabilizer also
satisfies the same intrinsic sandwich.

**Corollary 6.1 (lane-stabilizer Safe-Hit sandwich).** For every
$a\in\operatorname{Stab}(\mathcal C_\Delta)$ and
$x\in\widehat\Sigma$,

$$
 \boxed{
 \operatorname{LaneAdj}_\Delta(x)=1
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \Longrightarrow
 \operatorname{SameLane}_\Delta(x)=1.}
 \tag{6.3}
$$

**Proof.** The first implication is the identity-branch classification of
Paper XXXI followed by (2.8). For the second, $a$ carries each complete lane
to a lane, while every guarded identity-branch point map preserves same-lane
incidence. Hence every guarded $a$-return preserves that incidence. The
target $a_\#^{-1}
\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ is same-lane, so a state
with marked tokens in different lanes cannot reach it. $\square$

It is tempting to conjecture

$$
 \operatorname{Break}_\Delta(a)\ne\varnothing
 \quad\Longrightarrow\quad
 \mathsf{Hit}(a)=\mathsf{Same}_\Delta.
 \tag{6.4}
$$

Theorem 5.1 does not prove (6.4). A same-lane source may occupy a lane on
which $a$ is dihedral, while order breaking occurs only on another lane.
Moving the complete five-token context between those lanes is a new guarded
lane-mobility problem. An arbitrary placement cannot replace an actual path.

Inside the narrower affine normalizer family, the hostile descent question
remains sharper than multiplier classification. One must test whether there
exist

$$
 w,w'\in W_\Delta
 \quad\text{with}\quad
 \mu(w)=\mu(w')
 \quad\text{but}\quad
 \mathsf{Prom}(w)\ne\mathsf{Prom}(w').
 \tag{6.5}
$$

Such a pair would prove that phases or lane permutations are part of the
smallest Safe-Hit observable within that subfamily. A failed search or an
undefined branch would not prove non-descent.

Accordingly, the following remain open:

1. a lane-type-sensitive mobility theorem;
2. the full lane-stabilizer promotion dichotomy;
3. multiplier-only descent across affine phases and ordinary-lane
   permutations;
4. survivor-placement classification after the marked pair hits the target.

These questions are not needed for Theorem 5.1.

## Computational Artifacts

The paper-owned evidence package is available under
[`experiments/paper32/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper32)
in the RIME repository. It has no dependency on the broader exploratory
source tree.

| Surface | Paper-owned path | Role |
|---|---|---|
| Bounded finite controls | `affine_five_token_audit.py` and `results/` | Replays the retained affine, arbitrary-permutation, and multi-lane hostile domains |
| Development validation | `development-manifest.json` and `validation/` | Binds and replays the eight-artifact paper-owned evidence closure |
| Release validation | `release-manifest.json` and the public receipt under `results/` | Binds the manuscript, reader PDF, bibliography, nested development closure, environment, and validators |

The single-lane affine control covers $6\le n\le12$, every coprime kernel
separation, every unit affine multiplier, every marked five-token state,
every hole-deleted order fiber, and every applicable local gap transfer. This
affine domain is a proper subfamily of the permutation theorem. A
second control checks all $4{,}560$ branch permutations in the one-lane
domains $n=6,7$: $92$ cycle automorphisms and $4{,}468$ nonautomorphisms. A
separate $6\le n\le9$ multi-lane scan enumerates all affine normalizer phases
and ordinary-lane permutations in that bounded domain.

The finite audits are bounded consistency controls. They are not proofs of
the all-$n$ theorems and are not promoted as independent Computational
Certificates. In particular, the multi-lane scan is a hostile search for
multiplier non-descent; a bounded
absence of variation is not an all-$n$ descent theorem or a full-stabilizer
result. The public receipt records performed replay and local closure
verification, is excluded from its own closure, and is not an independent
mathematical validation.

## Claim Status and Boundary

All positive claims below have direct mathematical proofs in the manuscript.
No finite census is a theorem premise.

| Claim | Status | Scope |
|---|---|---|
| Exact skew quotient and target lifting | Imported | Paper XXXI normalizer interface |
| Pathwise identity simulation | Imported and restated as Lemma 2.1 | Every branch permutation |
| Lane-wise dihedral classification | Proposition 3.1 | Every lane-partition stabilizer branch whose lane restrictions are cycle-graph isomorphisms |
| Guarded unit gap transfer | Lemma 4.1 | One-lane identity branch |
| Directed gap connectivity | Lemma 4.2 | Every fixed weak-composition fiber |
| Order-fiber transitivity | Theorem 4.3 | One-lane identity branch |
| Single-lane permutation dichotomy | Theorem 5.1 | Every $a\in\operatorname{Sym}(E)$ |
| Lane-stabilizer Safe-Hit sandwich | Corollary 6.1 | Every $a\in\operatorname{Stab}(\mathcal C_\Delta)$ |
| Bounded affine controls | Finite consistency control | $6\le n\le12$; proper affine subfamily only |
| Bounded arbitrary-permutation control | Finite consistency control | All $4{,}560$ one-lane branches for $n=6,7$ |
| Multi-lane hostile search | Finite consistency control | Affine normalizer branches for $6\le n\le9$ |
| Full lane-stabilizer promotion classification | Open | Requires new mobility or obstruction |
| Survivor incidence | Not claimed | Marked-pair reachability is insufficient |
| Raw-to-typed transfer bridge | Not claimed | No new semantic fields or authority |

The following implications are explicitly forbidden:

$$
 u\not\equiv\pm1\pmod M
 \not\Longrightarrow
 \mathsf{Prom}(w)\ne\varnothing,
 \tag{8.1}
$$

because mixed-sign lane-wise dihedral multipliers need not create any
promotion;

$$
 \operatorname{Break}_\Delta(a)\ne\varnothing
 \not\Longrightarrow
 \mathsf{Hit}(a)=\mathsf{Same}_\Delta
 \tag{8.2}
$$

without a multi-lane mobility theorem; and

$$
 \text{raw Safe-Hit}
 \not\Longrightarrow
 \text{typed transfer membership or projectability}.
 \tag{8.3}
$$

## Conclusion

The branch-permutation frontier has two distinct thresholds.

The first is lane-local, not group-global: a branch creates no new Safe-Hit
state whenever it carries each arithmetic lane to a lane by a cycle-graph
isomorphism. For affine normalizer branches this includes mixed
Chinese-remainder signs excluded by the shorthand
$u\equiv\pm1\pmod M$.

The second threshold is exact in the one-lane regime. There the guarded
identity dynamics is transitive on every hole-deleted token-order fiber. A
branch permutation outside $\operatorname{Aut}(C_L)$ necessarily sends some
physical nonedge to an edge. Mobility reaches a compatible nonadjacent
five-token state, the globally enabled branch twist creates adjacency, and
the identity simulation completes the target witness. Hence every state
becomes target-reachable.

In compressed form,

$$
 \boxed{
 \text{guarded gap mobility}
 +
 \text{cycle-edge conversion}
 \Longrightarrow
 \text{complete one-lane Safe-Hit}.}
 \tag{9.1}
$$

The remaining multi-lane problem is now sharply separated. It is not another
defect-classification problem. It asks whether a five-token spectator context
can be moved, by actual guarded relations, to a lane on which the branch
restriction breaks cyclic order. The affine multiplier question survives as
one narrower descent problem inside the larger lane-stabilizer dynamics.

## References {.unnumbered}
