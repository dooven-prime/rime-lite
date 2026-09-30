# Branch-Normalized Partial Returns in Single-Defect Circular Automata
## Multi-Lane Safe-Hit Classification and a Normalizer Extension

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXI | Version 1.0**

*This paper (Paper XXXI of the RIME program) studies intrinsic raw
spectator-safe return dynamics. It imports the missing-image section and
branch freedom proved in Paper XXX, but not any typed transfer,
projectability, recursive-return, or credit-settlement conclusion.*

---

## Abstract

**Problem.** Paper XXX shows that every labelled binary-kernel
rank-$(n-1)$ defect has a universal return group on its missing-image
section, and that after fixing the oriented kernel and missing image the
remaining branch is an arbitrary permutation. The group alone does not
retain the guards of the other partial returns. The resulting Safe-Hit
problem therefore still depends on a partial dynamical system.

**Approach.** We conjugate the entire labelled return system, not only its
two globally enabled generators. For kernel separation $\Delta$ and branch
permutation $a$, every normalized return has point map

$$
 \phi_r=\varepsilon_\Delta\circ p^r\circ a,
$$

with an exact collision guard and an exact normalized exit target. We first
eliminate the exponent in the cyclic branch
$a\in\langle\psi_\Delta\rangle$. We then decompose the punctured rotation
$\psi_\Delta$ into arithmetic lanes and use a guarded hole-slide to classify
target reachability. Finally, we record the part of this classification that
survives for branch permutations normalizing
$\langle\psi_\Delta\rangle$.

**Results.** The branch conjugacy transports guards, targets, and labelled
paths exactly. In the cyclic branch, Safe-Hit truth is independent of the
branch exponent. Put $g=\gcd(n,\Delta)$ and read each
$\psi_\Delta$-lane after deleting holes. A marked pair reaches the section
exit target if and only if its two tokens lie in one lane and are adjacent in
that hole-deleted token order. Thus, for every integer $s$,

$$
 \operatorname{SafeHit}_{n,\Delta,\psi_\Delta^s}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.
$$

For a normalizer branch, the quotient dynamics is an exact relation-valued
skew system: each edge is the identity-branch relation preceded by a
deterministic orbit permutation. Normalizer elements admit an affine lane
form with orientation-compatible multiplier $u\equiv\pm1$ (lane-order
preserving or reversing), for which the same lane-adjacency criterion is
complete. For every normalizer branch we obtain the sandwich

$$
 \operatorname{LaneAdj}_\Delta(x)
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \Longrightarrow
 \operatorname{SameLane}_\Delta(x).
$$

**Boundary.** The paper does not classify multipliers
$u\not\equiv\pm1$, the broader cycle-partition-preserving regime, or terminal
survivor placement. It proves raw marked-pair reachability only. It does not
establish transfer membership, authorization, projectability, recursive
return, credit settlement, or a reset bound.

**Keywords.** synchronizing automata; circular automata; rank defect;
partial dynamics; Safe-Hit; punctured rotation; lane adjacency; normalizer

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/n\mathbb Z$ | labelled circular carrier, $n\ge6$ |
| $p(q)=q+1$ | fixed full cycle |
| $d:Q\to Q$ | rank-$(n-1)$ map with one binary kernel |
| $K_d=\{0,\Delta\}$ | oriented kernel after cyclic relabelling |
| $m$ | unique missing image of $d$ |
| $D=Q\setminus\{m\}$ | missing-image section carrier before normalization |
| $E=Q\setminus\{0\}$ | normalized branch carrier |
| $b=d|_E:E\to D$ | inverse-branch bijection |
| $t_0$ | exponent satisfying $p^{t_0}(m)=0$ |
| $a=p^{t_0}b$ | branch permutation in $\operatorname{Sym}(E)$ |
| $\varepsilon_\Delta$ | marked collapse $0\mapsto\Delta$, fixing $E$ |
| $\widehat\Sigma=\operatorname{Conf}_{2,3}(E)$ | marked pair plus three spectators |
| $U_x$ | five-point occupied support of $x$ |
| $\phi_r=\varepsilon_\Delta p^ra$ | normalized partial return point map |
| $\widehat{\mathcal T}_{\Delta,a}$ | normalized section exit target |
| $\psi_\Delta=\varepsilon_\Delta p^\Delta|_E$ | punctured rotation |
| $H_\Delta=\langle\psi_\Delta\rangle$ | universal relative-return subgroup |
| $C_0,C_1,\ldots,C_{g-1}$ | punctured and ordinary $\psi_\Delta$-lanes |
| $\operatorname{LaneAdj}_\Delta$ | same-lane adjacency after deleting holes |
| $\operatorname{SameLane}_\Delta$ | both marked tokens lie in one lane |

## Introduction

A rank-$(n-1)$ defect has one binary collision fiber, but its return dynamics
need not be local. Away from the kernel, the labelled defect may carry the
occupied coordinates by an arbitrary bijection. Paper XXIX classifies the
complete raw rank-five first-exit frontier for the canonical defect by a
cyclic token order and a constructive hole slide [@paper29]. Paper XXX then
shows that every labelled defect has two globally enabled section returns,
an intrinsic punctured rotation, and a free branch permutation [@paper30].

The latter result changes the natural question. The universal return group
describes globally available symmetry, but it does not determine which of
the remaining return blocks are enabled on a given five-point support. The
next object is therefore the complete partial return system. After orienting
the kernel and conjugating by one inverse branch, this system has the exact
normal form

$$
 \boxed{\phi_r=\varepsilon_\Delta p^ra.}
 \tag{1.1}
$$

Equation (1.1) transports the guard, the section target, and every labelled
path. It reduces the raw problem for an arbitrary labelled defect to the
parameters $(n,\Delta,a)$ without erasing the collision semantics.

The paper's main theorem concerns the structured cyclic branch
$a\in\langle\psi_\Delta\rangle$. The cycles of the punctured rotation form
arithmetic lanes. The guarded maps preserve the hole-deleted token order in
each lane, while a specific partial return moves a hole past the marked pair
and strictly decreases a finite gap count. This proves the path-free
classification

$$
 \boxed{
 a\in\langle\psi_\Delta\rangle
 \quad\Longrightarrow\quad
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.}
 \tag{1.2}
$$

We then ask how far (1.2) survives beyond the cyclic branch. If $a$ normalizes
$H_\Delta=\langle\psi_\Delta\rangle$, it acts by a deterministic twist on
the $H_\Delta$-orbit space. The other returns remain relations on that
quotient. An affine lane normal form isolates a multiplier $u$, a lane
permutation, and phase data. The classification survives exactly as proved
here for the orientation-compatible multipliers $u\equiv\pm1$. For the full
normalizer, lane adjacency is sufficient and same-lane incidence is
necessary. The unresolved region is therefore confined to same-lane,
nonadjacent marked pairs under multipliers $u\not\equiv\pm1$.

The theorem spine is short.

1. Section 2 proves the exact branch-normalized partial system.
2. Section 3 eliminates cyclic-branch exponents at the level of Safe-Hit
   truth.
3. Section 4 proves the multi-lane invariant, the terminating hole slide,
   and the complete cyclic-branch classification.
4. Section 5 gives the normalizer skew quotient and affine lane form.
5. Section 6 closes the multipliers $u\equiv\pm1$ and localizes the open
   full-normalizer frontier.

The work remains at the intrinsic raw level. In particular, a raw Safe-Hit
path is not silently promoted to a typed transfer, an authorized entry, or a
projection witness.

### Related Work and Novelty Boundary

The Černý conjecture asks for a quadratic reset bound for synchronizing
automata [@cerny1964; @volkov2008; @volkov2022survey]. Circular automata admit
stronger reset results under hypotheses different from those used here
[@dubuc1998]. Almost-group automata, built from permutation letters and a
letter with one nontrivial kernel class, form a nearby structural setting
[@berlinkovNicaud2020; @casasTorres2024]. This paper proves no reset bound and
does not classify general almost-group automata.

Monotonic and cyclic-order methods study automata preserving a global order
[@eppstein1990]. Subset and careful synchronization, as well as synchronization
under dynamic constraints, study synchronizing subsets or words subject to
partiality, order, or visitation constraints
[@ryzhikovShemyakov2018; @wolf2020]. Complete reachability studies which
unlabelled subsets arise as images
[@don2016; @gonzeJungers2018; @ferensSzykula2026]. The present observable is
different: one guarded path must preserve injectivity of the marked pair and
all three spectators at every proper return step, and that same path must hit
a source-marked target. The cited results do not supply the lane-adjacency or
normalizer-skew classifications proved here. The novelty is the exact branch
normalization of this partial system and the resulting multi-lane,
source-marked Safe-Hit classification.

Within the RIME line, Paper XXIX supplies the canonical single-lane model and
Paper XXX supplies the missing-image section, universal return group,
punctured rotation, and branch freedom [@paper29; @paper30]. The present paper
does not repeat their frontier or group classifications. It uses their
interfaces to classify a new structured family of partial return systems.

## Branch Normalization and the $(n,\Delta,a)$ System

Let $n\ge6$, let

$$
 Q=\mathbb Z/n\mathbb Z,
 \qquad
 p(q)=q+1\pmod n,
 \tag{2.1}
$$

and let $d:Q\to Q$ have rank $n-1$, one binary kernel, and missing image
$m$. Orient the kernel and relabel cyclically so that

$$
 K_d=\{0,\Delta\},
 \qquad
 1\le\Delta\le n-1.
 \tag{2.2}
$$

Put

$$
 D=Q\setminus\{m\},
 \qquad
 E=Q\setminus\{0\},
 \tag{2.3}
$$

and let $t_0$ be the unique exponent with $p^{t_0}(m)=0$. The restriction

$$
 b=d|_E:E\overset{\sim}{\longrightarrow}D
 \tag{2.4}
$$

is a bijection. Define

$$
 a=p^{t_0}\circ b\in\operatorname{Sym}(E)
 \tag{2.5}
$$

and the marked collapse

$$
 \varepsilon_\Delta(0)=\Delta,
 \qquad
 \varepsilon_\Delta(q)=q\quad(q\ne0).
 \tag{2.6}
$$

Its only non-singleton fiber is $\{0,\Delta\}$, and

$$
 \boxed{b^{-1}d=\varepsilon_\Delta.}
 \tag{2.7}
$$

We use the automata convention that the written block $p^td$ acts first by
$p^t$ and then by $d$, so its point map is $d\circ p^t$.

The normalized configuration space is

$$
 \widehat\Sigma
 =\operatorname{Conf}_{2,3}(E)
 =\{(A,R):|A|=2,\ |R|=3,\ A\cap R=\varnothing\}.
 \tag{2.8}
$$

For $x=(A,R)$ write $U_x=A\cup R$. The branch bijection acts on states by

$$
 \mathbf b(A,R)=(bA,bR),
 \qquad
 \mathbf b:\widehat\Sigma\overset{\sim}{\longrightarrow}\Sigma_m,
 \tag{2.9}
$$

where $\Sigma_m$ is the missing-image section of Paper XXX. If
$\mathscr R_t=d\circ p^t$ is the corresponding partial section return,
re-index its branch conjugate by

$$
 \widetilde{\mathscr R}_r
 =\mathbf b^{-1}\mathscr R_{t_0+r}\mathbf b.
 \tag{2.10}
$$

This notation means conjugation of a partial state map, including its domain.

**Theorem 2.1 (branch-normalized full return dynamics; N1).** Define

$$
 \phi_r=\varepsilon_\Delta\circ p^r\circ a:E\to E.
 \tag{2.11}
$$

Then for every $r\in\mathbb Z/n\mathbb Z$:

1. the conjugated return is
   $$
    \boxed{\widetilde{\mathscr R}_r=(\phi_r)_\#;}
    \tag{2.12}
   $$
2. its exact guard is
   $$
    \boxed{
    x\in\operatorname{Dom}(\widetilde{\mathscr R}_r)
    \iff
    \{0,\Delta\}\nsubseteq p^ra(U_x);}
    \tag{2.13}
   $$
3. under this guard,
   $$
    \widetilde{\mathscr R}_r(A,R)
    =(\phi_r(A),\phi_r(R));
    \tag{2.14}
   $$
4. the normalized inverse image of the section exit set is
   $$
    \boxed{
    \widehat{\mathcal T}_{\Delta,a}
    =\{(A,R)\in\widehat\Sigma:
      \exists u,\ p^ua(A)=\{0,\Delta\}\};}
    \tag{2.15}
   $$
5. after the label translation $r\mapsto t_0+r$, $\mathbf b$ is an
   isomorphism of partial labelled transition systems. In particular,
   $$
    x\xrightarrow{r_1,\ldots,r_j}_{\rm norm}y
    \iff
    \mathbf b(x)
    \xrightarrow{t_0+r_1,\ldots,t_0+r_j}_{\rm section}
    \mathbf b(y).
    \tag{2.16}
   $$

**Proof.** The point map beneath (2.10) is

$$
 \begin{aligned}
 b^{-1}d\,p^{t_0+r}b
 &=\varepsilon_\Delta p^r(p^{t_0}b)\\
 &=\varepsilon_\Delta p^ra.
 \end{aligned}
 \tag{2.17}
$$

Only $\varepsilon_\Delta$ can destroy injectivity. It does so on $U_x$
exactly when the preceding permutation $p^ra$ places two occupied points at
$0$ and $\Delta$. This proves (2.12)--(2.14).

The original section target consists of states whose marked pair can be
rotated onto $K_d$. Thus $\mathbf b(A,R)$ is a target exactly when some $u$
satisfies $p^ub(A)=\{0,\Delta\}$. Replacing $u$ by $u-t_0$ and using
$a=p^{t_0}b$ gives (2.15), reversibly. Equation (2.17) identifies each
single labelled edge, and induction on path length gives (2.16). $\square$

The normalized Safe-Hit predicate is therefore

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \exists r_1,\ldots,r_j:
 x\xrightarrow{r_1,\ldots,r_j}_{\rm norm}
 \widehat{\mathcal T}_{\Delta,a}.}
 \tag{2.18}
$$

All guards and the target are now functions of $(n,\Delta,a)$. Paper XXX
proves that every $a\in\operatorname{Sym}(E)$ occurs in the fixed oriented
kernel and missing-image fiber. Hence Theorem 2.1 classifies the input data
for the complete partial dynamics. It does not yet classify reachability.

Two globally enabled returns are visible immediately. Put

$$
 \psi_\Delta=\varepsilon_\Delta p^\Delta|_E.
 \tag{2.19}
$$

Then

$$
 \widetilde{\mathscr R}_0=a_\#,
 \qquad
 \widetilde{\mathscr R}_\Delta=(\psi_\Delta a)_\#.
 \tag{2.20}
$$

The group skeleton $\langle a,\psi_\Delta\rangle$ is therefore the globally
enabled part of (2.11); the remaining labels retain information that this
group forgets.

## Cyclic-Branch Exponent Elimination

Let

$$
 H_\Delta=\langle\psi_\Delta\rangle,
 \qquad
 \pi_H:\widehat\Sigma\to\widehat\Sigma/H_\Delta.
 \tag{3.1}
$$

For $s\in\mathbb Z$, set $a_s=\psi_\Delta^s$ and write

$$
 F_r^{(s)}
 =(\varepsilon_\Delta p^r\psi_\Delta^s)_\#,
 \qquad
 \widehat{\mathcal T}_s
 =\widehat{\mathcal T}_{\Delta,\psi_\Delta^s}.
 \tag{3.2}
$$

For $H_\Delta$-orbits $O,O'$, define the existential quotient edge

$$
 O\xrightarrow{r}_sO'
 \iff
 \exists x\in O\cap\operatorname{Dom}(F_r^{(s)}),
 \quad F_r^{(s)}(x)\in O'.
 \tag{3.3}
$$

The quotient is relation-valued: no representative-independent partial map
is assumed.

**Theorem 3.1 (cyclic-branch exponent elimination; N2).** For every integer
$s$:

$$
 \boxed{O\xrightarrow{r}_sO'\iff O\xrightarrow{r}_0O'}
 \tag{3.4}
$$

for all $O,O',r$,

$$
 \boxed{
 \pi_H(\widehat{\mathcal T}_s)
 =\pi_H(\widehat{\mathcal T}_0),}
 \tag{3.5}
$$

and, at every fixed starting state,

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,\psi_\Delta^s}(x)
 \iff
 \operatorname{SafeHit}_{n,\Delta,\operatorname{id}}(x).}
 \tag{3.6}
$$

**Proof.** The globally enabled normalized returns are

$$
 F_0^{(s)}=(\psi_\Delta^s)_\#,
 \qquad
 F_\Delta^{(s)}=(\psi_\Delta^{s+1})_\#,
$$

and

$$
 \langle\psi_\Delta^s,\psi_\Delta^{s+1}\rangle
 =H_\Delta.
 \tag{3.7}
$$

Their inverses are positive powers, so every $H_\Delta$-orbit is strongly
connected by actual return blocks in the $s$-system.

For an edge witness $x\in O$, put $y=(\psi_\Delta^s)_\#x$. Then $y\in O$
and

$$
 F_r^{(s)}(x)=F_r^{(0)}(y).
 \tag{3.8}
$$

The two sides have the same guard because they present the same five-point
set to $\varepsilon_\Delta p^r$. The substitution $x\mapsto y$ is a
bijection of $O$, proving (3.4). Similarly,

$$
 x\in\widehat{\mathcal T}_s
 \iff
 (\psi_\Delta^s)_\#x\in\widehat{\mathcal T}_0,
$$

which proves (3.5). Exact orbit lifting, using the internal controllability
from (3.7), identifies each Safe-Hit predicate with reachability in its
relation-valued orbit system. Equations (3.4)--(3.5) make the two quotient
problems identical, proving (3.6). $\square$

The theorem compares truth predicates, not witness words. It does not assert
equality of labelled path languages, shortest words, or deterministic
quotient transitions.

## Multi-Lane Invariant and Hole-Slide

It remains to solve the base system $a=\operatorname{id}$. Put

$$
 g=\gcd(n,\Delta),
 \qquad
 \ell=\frac ng,
 \qquad
 L_c=\{q\in Q:q\equiv c\pmod g\}.
 \tag{4.1}
$$

The cycles of $\psi_\Delta$ on $E$ are the lanes

$$
 C_0=L_0\setminus\{0\},
 \qquad
 C_c=L_c\quad(c\ne0).
 \tag{4.2}
$$

The punctured lane $C_0$ has length $\ell-1$; every ordinary lane has length
$\ell$. Each is read in its $\psi_\Delta$-cyclic order. On $C_0$ this order
contains the shortcut $-\Delta\mapsto\Delta$ that closes the deleted point.

For $x=(A,R)$, color the points of $A$ by $\mathsf P$, the points of $R$ by
$\mathsf S$, and all holes in $E\setminus U_x$ by $\mathsf H$. Read each lane
cyclically and delete the holes. Define

$$
 \operatorname{LaneAdj}_\Delta(x)=1
 \tag{4.3}
$$

if and only if the two $\mathsf P$ tokens lie in one lane and are adjacent in
that lane's hole-deleted cyclic word. Equivalently, one oriented lane arc
between the marked tokens has no occupied point in its interior.

**Lemma 4.1 (lane-order preservation; N3.1).** For every enabled base return
$\phi_r=\varepsilon_\Delta p^r$, all lane indices undergo the same
translation $c\mapsto c+r\pmod g$, and the hole-deleted cyclic
$\mathsf P/\mathsf S$ order in each occupied lane is preserved. Hence

$$
 \boxed{
 \operatorname{LaneAdj}_\Delta((\phi_r)_\#x)
 =\operatorname{LaneAdj}_\Delta(x).}
 \tag{4.4}
$$

**Proof.** Since $g\mid\Delta$,
$\varepsilon_\Delta(q)\equiv q\pmod g$, and therefore
$\phi_r(q)\equiv q+r\pmod g$. On the full $\Delta$-cycles in $Q$, translation
preserves cyclic order. Insert $0$ as a hole when comparing a punctured lane
with a full cycle, translate, and delete it again. The marked collapse closes
the resulting gap. Its guard excludes simultaneous occupancy of $0$ and
$\Delta$, so the insertion, deletion, and shortcut cannot identify or cross
two occupied tokens. Deleting all holes leaves the same cyclic token word.
$\square$

**Lemma 4.2 (lane hole-slide; N3.2).** If
$\operatorname{LaneAdj}_\Delta(x)=1$, then $x$ reaches
$\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ by guarded normalized
returns.

**Proof.** Distinguish the marked tokens temporarily as $P_1,P_2$. Choose an
oriented lane arc from $P_1$ to $P_2$ with no occupied point in its interior,
and let $h$ be the number of holes in that arc.

If the marked lane is ordinary and $P_1=z$, then either $h=0$ and the marked
pair is already a rotation of $\{0,\Delta\}$, or $z+\Delta$ is a hole. In
the latter case, the label $r=-z$ presents the collision pair as
$\{\mathsf P,\mathsf H\}$, so the return is enabled. It moves the marked
lane into $C_0$, removes the first hole from the chosen arc, and creates the
compensating hole in a different lane. Thus $h$ decreases by one.

Now suppose the marked pair lies in $C_0$. A power of the globally enabled
return $\psi_\Delta$ places $P_1$ at $\Delta$ without changing $h$. If
$h>0$, then $2\Delta$ is a hole. The fixed label $r=-\Delta$ is enabled,
fixes $P_1$ at $\Delta$, moves the later points of the selected arc one
$\Delta$-step toward it, and creates the new hole at $-\Delta$, outside the
selected forward arc. Hence

$$
 \boxed{h\longmapsto h-1.}
 \tag{4.5}
$$

Iteration reaches $h=0$. The marked pair is then a physical
$\Delta$-neighbor pair unless it occupies the punctured shortcut
$\{-\Delta,\Delta\}$. In that case one $\psi_\Delta$ step sends it to
$\{\Delta,2\Delta\}$. The resulting pair is a rotation of
$\{0,\Delta\}$, so the state already belongs to the declared target.

If $\ell=2$, the punctured lane has one point and cannot contain both marked
tokens. If $\ell=3$, its two points are already adjacent. Thus the decreasing
step is invoked only when the stated next coordinate exists. $\square$

## Complete Cyclic-Branch Classification

**Theorem 4.3 (multi-lane Safe-Hit classification; N3).** For every $n\ge6$,
$1\le\Delta\le n-1$, and $x\in\widehat\Sigma$,

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,\operatorname{id}}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.}
 \tag{4.6}
$$

**Proof.** Lemma 4.1 makes lane adjacency invariant along every guarded
path. Every target state has a marked pair $\{z,z+\Delta\}$ for some $z$,
so its marked tokens are in one lane and physically adjacent. This proves
necessity. Lemma 4.2 gives a terminating guarded path for every lane-adjacent
state, proving sufficiency. $\square$

**Corollary 4.4 (cyclic-branch classification; N3a).** For every integer $s$,

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,\psi_\Delta^s}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.}
 \tag{4.7}
$$

**Proof.** Theorem 3.1 removes the exponent $s$ from the Safe-Hit truth
predicate, and Theorem 4.3 classifies the resulting base system. $\square$

This is a path-free target-reachability theorem. It does not identify a
common witness word for different exponents, compare shortest paths, or make
$\operatorname{LaneAdj}_\Delta$ a deterministic quotient of the labelled
partial system.

## Normalizer Extension: Skew Quotient and Affine Form

Let

$$
 \mathcal Z_\Delta=\widehat\Sigma/H_\Delta,
 \qquad
 \pi_H:\widehat\Sigma\to\mathcal Z_\Delta.
 \tag{5.1}
$$

Suppose $a$ normalizes $H_\Delta$. It induces a deterministic orbit
permutation

$$
 \bar a([x])=[a_\#x].
 \tag{5.2}
$$

For the identity branch define the relation-valued edge

$$
 O\,R_r^{(0)}\,O'
 \iff
 \exists y\in O\cap\operatorname{Dom}(F_r^{(0)}),
 \quad F_r^{(0)}(y)\in O'.
 \tag{5.3}
$$

**Theorem 5.1 (normalizer skew-orbit reduction; N4.1).** If
$a\in N_{\operatorname{Sym}(E)}(H_\Delta)$, then

$$
 \boxed{
 O\xrightarrow{r}_aO'
 \iff
 \bar a(O)\,R_r^{(0)}\,O',}
 \tag{5.4}
$$

$$
 \boxed{
 \pi_H(\widehat{\mathcal T}_{\Delta,a})
 =\bar a^{-1}
   \pi_H(\widehat{\mathcal T}_{\Delta,\operatorname{id}}),}
 \tag{5.5}
$$

and the quotient is exact for target reachability:

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \pi_H(x)\leadsto_a
 \pi_H(\widehat{\mathcal T}_{\Delta,a}).}
 \tag{5.6}
$$

Here $\leadsto_a$ is generated by the relations (5.4), not by deterministic
quotient maps.

**Proof.** For an edge witness $x\in O$, put $y=a_\#x$. The normalized
return factors as

$$
 F_r^{(a)}(x)=F_r^{(0)}(y),
$$

with exactly the identity-branch guard at $y$. Since
$a_\#:O\to\bar a(O)$ is a bijection, this proves (5.4). The identity
$\widehat{\mathcal T}_{\Delta,a}=a_\#^{-1}
\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ gives (5.5).

Finally, $F_0^{(a)}=a_\#$ and
$F_\Delta^{(a)}=(\psi_\Delta a)_\#$ are globally enabled permutations. Their
positive powers realize inverses, and their relative product realizes
$\psi_\Delta$. Hence every $H_\Delta$-orbit is internally strongly connected
by actual return blocks. The usual relation-valued orbit-lifting argument
proves (5.6). $\square$

The twist $\bar a$ occurs before every base relation in (5.4). The theorem
does not identify the normalizer system with the identity-branch system.

Write

$$
 M=\operatorname{ord}(\psi_\Delta)
 =
 \begin{cases}
  \ell-1,&g=1,\\
  \ell(\ell-1),&g>1.
 \end{cases}
 \tag{5.7}
$$

**Theorem 5.2 (affine-lane normal form; N4.2).** Choose a coordinate
$t\in\mathbb Z/(\ell-1)\mathbb Z$ on the punctured lane $C_*$ and coordinates
$(j,t)$, $t\in\mathbb Z/\ell\mathbb Z$, on the ordinary lanes
$C_j$, $j\in J=\{1,\ldots,g-1\}$. A permutation $a$ normalizes $H_\Delta$ if
and only if there are

$$
 u\in(\mathbb Z/M\mathbb Z)^\times,
 \quad
 \sigma\in\operatorname{Sym}(J),
 \quad
 \beta_*\in\mathbb Z/(\ell-1)\mathbb Z,
 \quad
 \beta_j\in\mathbb Z/\ell\mathbb Z
 \tag{5.8}
$$

such that

$$
 \boxed{
 \begin{aligned}
 a(*,t)&=(*,ut+\beta_*)&&\pmod{\ell-1},\\
 a(j,t)&=(\sigma(j),ut+\beta_j)&&\pmod\ell.
 \end{aligned}}
 \tag{5.9}
$$

When $g=1$, the second line and $\sigma$ are absent.

**Proof.** A normalizer element satisfies
$a\psi_\Delta a^{-1}=\psi_\Delta^u$ for a unique unit
$u\pmod M$. The power $\psi_\Delta^u$ has the same cycle decomposition as
$\psi_\Delta$. Therefore $a$ fixes the unique punctured lane and permutes
the ordinary lanes. In coordinates where $\psi_\Delta$ adds one, the identity
$a\psi_\Delta=\psi_\Delta^ua$ forces (5.9), with one free phase on each lane.
Conversely, every map of the displayed form is bijective and satisfies that
identity. $\square$

## Orientation-Compatible Normalizers and the Sandwich

The following simulation does not require normalizer membership.

**Lemma 6.1 (identity-branch simulation; N4.3).** For every
$a\in\operatorname{Sym}(E)$,

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,\operatorname{id}}(x)
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x).}
 \tag{6.1}
$$

**Proof.** Let $m=\operatorname{ord}(a)$. The label-zero return is the
globally enabled permutation $F_0^{(a)}=a_\#$. Before simulating an enabled
identity-branch edge with label $r$, apply $0^{m-1}$ to reach
$(a^{-1})_\#x$ and then apply $r$. The result is exactly
$F_r^{(0)}(x)$. Repeat this edge by edge. If the identity path ends at
$y\in\widehat{\mathcal T}_{\Delta,\operatorname{id}}$, one final
$0^{m-1}$ block reaches
$(a^{-1})_\#y\in\widehat{\mathcal T}_{\Delta,a}$. $\square$

Let $\operatorname{SameLane}_\Delta(x)$ mean that the two marked points lie
in one $\psi_\Delta$-lane.

**Corollary 6.2 (same-lane obstruction; N4.4).** For every normalizer branch,

$$
 \boxed{
 \neg\operatorname{SameLane}_\Delta(x)
 \Longrightarrow
 \neg\operatorname{SafeHit}_{n,\Delta,a}(x).}
 \tag{6.2}
$$

**Proof.** A normalizer permutes whole lanes, and every guarded base return
translates all lane indices uniformly by Lemma 4.1. Hence every normalized
$a$-return preserves whether the two marked points share a lane. Every point
of $\widehat{\mathcal T}_{\Delta,a}=a_\#^{-1}
\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ has the same-lane property.
$\square$

**Theorem 6.3 (orientation-compatible normalizer classification; N4.5).**
Let $a$ have multiplier $u$ in Theorem 5.2. If

$$
 u\equiv1\pmod M
 \qquad\text{or}\qquad
 u\equiv-1\pmod M,
 \tag{6.3}
$$

then

$$
 \boxed{
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \iff
 \operatorname{LaneAdj}_\Delta(x)=1.}
 \tag{6.4}
$$

**Proof.** Formula (5.9) shows that $a$ preserves or reverses the cyclic
order on every lane, while possibly permuting lanes and changing phases.
Thus $a$ preserves lane adjacency. Lemma 4.1 implies that every guarded
$a$-return preserves the same observable. The target
$a_\#^{-1}\widehat{\mathcal T}_{\Delta,\operatorname{id}}$ is lane-adjacent,
so adjacency is necessary. If the start is lane-adjacent, Theorem 4.3 gives
an identity-branch Safe-Hit path and Lemma 6.1 simulates it in the
$a$-system. $\square$

The full normalizer is nevertheless trapped between two intrinsic
observables.

**Corollary 6.4 (normalizer Safe-Hit sandwich; N4.6).** For every
$a\in N_{\operatorname{Sym}(E)}(H_\Delta)$,

$$
 \boxed{
 \operatorname{LaneAdj}_\Delta(x)=1
 \Longrightarrow
 \operatorname{SafeHit}_{n,\Delta,a}(x)
 \Longrightarrow
 \operatorname{SameLane}_\Delta(x).}
 \tag{6.5}
$$

**Proof.** The first implication is Theorem 4.3 followed by Lemma 6.1. The
second is Corollary 6.2. $\square$

Thus any new Safe-Hit state created by a multiplier
$u\not\equiv\pm1\pmod M$ must already have its marked points in one lane but
not adjacent in the hole-deleted token order. Corollary 6.4 does not assert
that any such state is hittable.

## Boundaries and Open Skew Multipliers

The normalized object has separated three levels that should not be merged.

1. The full parameter $a\in\operatorname{Sym}(E)$ determines a guarded
   partial system, not merely a return group.
2. The cyclic branch admits the complete criterion of Corollary 4.4.
3. Normalizer membership gives the skew quotient of Theorem 5.1, but only
   the multipliers $u\equiv\pm1$ are classified here.

For $u\not\equiv\pm1$, multiplication inside a lane can change the
hole-deleted five-token order. The remaining problem is exactly the skew
dynamics on

$$
 (\mathcal Z_\Delta,\bar a,\{R_r^{(0)}\}),
 \tag{7.1}
$$

restricted by Corollary 6.4 to same-lane, nonadjacent starts. The affine data
$(u,\sigma,\symbf{\beta})$ may affect this reachability. No claim is made
that the multiplier alone determines Safe-Hit truth.

The broader regime in which $a$ merely preserves the
$\psi_\Delta$-cycle partition is also open. There the lane-wise permutations
need not have a common multiplier, and even the normalizer skew form need not
survive.

After pair hitting comes a separate survivor-incidence problem. The present
theorems decide whether the marked source pair can reach the terminal kernel
while all three spectators remain collision free. They do not determine the
three survivor coordinates after the strict defect event.

Finally, raw reachability does not provide the typed observables needed for
transfer membership or projectability. Any raw-to-typed audit must use the
existing interfaces and stop at the first missing all-$n$ clause; this paper
introduces no replacement semantics.

## Computational Artifacts

The paper-owned evidence package is available under
[`experiments/paper31/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper31)
in the RIME repository. It has no dependency on the broader exploratory
source tree.

| Surface | Paper-owned path | Role |
|---|---|---|
| Bounded hostile controls | `partial_return_audit.py` and `results/` | Replays the retained cyclic and normalizer domains |
| Partial formalization | `lean/` | Checks the generic path, quotient, skew-transport, and boundary spine |
| Release validation | `release-manifest.json` and the public receipt under `results/` | Binds the manuscript, reader PDF, bibliography, nested development closure, environment, and validators |

The retained audit covers $93{,}720$ cyclic-branch states, $870{,}540$
enabled labelled edges, $456$ normalizer branches, $70{,}560$ normalizer
starts, $36{,}760$ orientation-compatible cases, and $175{,}216$ quotient
edges. The Lean spine checks only the declarations listed in its README; it
does not formalize the punctured-lane arithmetic or constructive hole-slide.
These are bounded consistency and formalization controls, not proofs of the
all-$n$ theorems or independent Computational Certificates.

The release manifest binds the canonical reader package and its nested
development closure. The public receipt records performed replay and local
closure verification, is excluded from its own closure, and is not an
independent mathematical validation.

## Claim Status and Boundary

| Claim surface | Status | Scope |
|---|---|---|
| Branch-normalized partial-system isomorphism | Theorem 2.1 | Formula, exact guard and target, and label translation for every oriented binary-kernel rank-$(n-1)$ defect, $n\ge6$ |
| Cyclic-branch exponent elimination | Theorem 3.1 | Every $a=\psi_\Delta^s$ and every start state |
| Lane-order preservation | Lemma 4.1 | Every guarded identity-branch return |
| Terminating lane hole-slide | Lemma 4.2 | Every lane-adjacent marked pair |
| Identity-branch Safe-Hit criterion | Theorem 4.3 | All $n\ge6$ and all kernel separations $\Delta$ |
| Complete cyclic-branch classification | Corollary 4.4 | Every $a\in\langle\psi_\Delta\rangle$ |
| Exact normalizer skew quotient | Theorem 5.1 | Relation-valued orbit reduction, not deterministic descent |
| Affine lane normal form | Theorem 5.2 | Every normalizer branch |
| Identity-branch simulation | Lemma 6.1 | Every branch permutation $a$ |
| Same-lane obstruction | Corollary 6.2 | Every normalizer branch |
| Orientation-compatible classification | Theorem 6.3 | Normalizer multipliers $u\equiv\pm1\pmod M$ |
| Normalizer Safe-Hit sandwich | Corollary 6.4 | Every normalizer branch |
| Other normalizer multipliers | Open | Same-lane, nonadjacent frontier only |
| Cycle-partition-preserving regime | Open | No general Safe-Hit criterion claimed |
| Survivor placement | Deferred | Terminal off-kernel incidence not classified here |
| Raw-to-typed bridge | Open | No new semantic fields introduced |
| Projectable origins and recursive return | Deferred | Requires later typed and same-witness theorems |

All positive claims above have direct mathematical proofs in the manuscript.
The bounded finite audit and Lean spine are consistency and formalization
controls; neither is a theorem premise or an independent validation of those
proofs.

The following implications are explicitly excluded:

$$
 a\in N_{\operatorname{Sym}(E)}(H_\Delta)
 \quad\Longrightarrow\quad
 \operatorname{SafeHit}=\operatorname{LaneAdj},
 \tag{7.2}
$$

$$
 \operatorname{SameLane}_\Delta(x)=1
 \quad\Longrightarrow\quad
 \operatorname{SafeHit}_{n,\Delta,a}(x),
 \tag{7.3}
$$

and

$$
 \text{raw Safe-Hit}
 \quad\Longrightarrow\quad
 \text{typed transfer membership or projectability}.
 \tag{7.4}
$$

## Conclusion

The full return dynamics of an arbitrary labelled single-defect circular
automaton admits an exact branch normalization. The formula
$\phi_r=\varepsilon_\Delta p^ra$ carries the collision guard, section exit
target, and labelled paths together, reducing the intrinsic raw problem to
the parameters $(n,\Delta,a)$.

For the cyclic branch, the exponent disappears after relation-valued orbit
reduction. The remaining base dynamics has a complete all-$n$ classification:
the marked pair reaches the exit target exactly when its tokens occupy one
punctured-rotation lane and are adjacent after holes are deleted. A guarded
hole-slide supplies a terminating witness path.

Beyond the cyclic branch, normalizer dynamics is an exact skew system over
the identity-branch relations. Its affine lane multiplier identifies the
orientation-compatible subregime $u\equiv\pm1$, where the same classification
survives. For the full normalizer, the Safe-Hit sandwich confines every open
case to a same-lane, nonadjacent start. The next problem is therefore no
longer an unspecified general defect: it is the arithmetic skew dynamics of
the remaining affine multipliers.
