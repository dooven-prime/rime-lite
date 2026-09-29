# Universal Return Groups and Punctured Rotations
## Exact Orbit Reduction for General Single-Defect Circular Automata

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXX | Version 1.0**

*This paper (Paper XXX of the RIME program) studies the intrinsic raw
section dynamics induced by an arbitrary labelled binary-kernel
rank-$(n-1)$ defect. It follows Paper XXIX's canonical rank-five frontier
classification but does not import that paper's canonical order law, finite
audits, or formalization as premises.*

---

## Abstract

**Problem.** For the canonical single-defect circular family, the
missing-image section carries a cyclic return symmetry. For a general
labelled defect, most rotation--defect return blocks are only partially
defined, and quotienting their dynamics as deterministic maps can destroy
the collision guard. The structural source of the canonical symmetry is
therefore not apparent from the canonical case alone.

**Approach.** We work on the rank-five spectator-safe configuration space
consisting of a marked pair and three spectators. Every defect event sends a
guarded configuration into the missing-image section. The two rotations
which move the missing image to the two kernel points produce globally
enabled permutation returns $g_0,g_1$ on that section. Their action defines
the universal return group $G_d$. Partial returns are then projected as
labelled relations between $G_d$-orbits rather than as falsely deterministic
quotient maps.

**Results.** Every labelled binary-kernel rank-$(n-1)$ defect has two
globally enabled section returns and an orientation-independent group

$$
 G_d=\langle g_0,g_1\rangle\le\operatorname{Sym}(Q\setminus\{m_d\}).
$$

The resulting relation-valued orbit system preserves and reflects exact
section reachability. For the relative return $h_d=g_1g_0^{-1}$, let
$\Delta$ be the positive cyclic separation of the two kernel points, put
$g=\gcd(n,\Delta)$, and put $\ell=n/g$. We prove that $h_d$ is conjugate to
rotation by $\Delta$ with one point deleted and the resulting gap closed.
Consequently,

$$
 \operatorname{ctype}(h_d)=(\ell-1,\ell^{\,g-1}).
$$

If $\gcd(n,\Delta)=1$, the section contains an intrinsic regular cyclic
subgroup $C_{n-1}$ and $G_d$ is transitive. In particular, every such defect
at prime ambient size lies in this regime. The canonical cyclic symmetry of
Paper XXIX is recovered as the case $g_0=\operatorname{id}$.

For non-coprime spacing, the remaining branch return has no hidden universal
restriction on the fiber with kernel and missing image fixed: as the defect
varies in that fiber, the conjugate of $g_0$ ranges over every permutation
$a$ of the punctured carrier. The point-orbits of $G_d$ on $D$ are exactly
the connected components of the graph recording which punctured-rotation
cycles are joined by $a$. Every partition of those cycles is realizable by
some labelled defect in the same fiber. Fixing the collision image cuts this
free parameter to a one-point permutation fiber of size $(n-2)!$ and imposes
an exact forced-join, with one singleton forced-isolation exception, on the
realizable point-orbit partitions.

**Boundary.** The paper gives an exact reduction and a general-defect regime
theorem; it does not classify every return group, every guarded quotient
edge, or every spectator-safe frontier. It does not establish survivor
incidence, transfer membership, projectability, recursive return, credit
settlement, or a reset bound. The finite audits are bounded consistency
controls bound into the development closure. They are not proofs of the
all-$n$ theorems and are not promoted as independent Computational
Certificates.

**Keywords.** synchronizing automata; circular automata; rank defect; return
group; missing-image section; relation-valued quotient; punctured rotation;
cycle-gluing graph

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q$ | labelled state set, $|Q|=n\ge6$ |
| $p$ | fixed full cycle on $Q$ |
| $d:Q\to Q$ | labelled rank-$(n-1)$ map with one binary kernel |
| $K_d=\{k_0,k_1\}$ | the unique non-singleton kernel fiber |
| $m_d$ | the unique missing image of $d$ |
| $D=Q\setminus\{m_d\}$ | image of $d$ and carrier of the universal returns |
| $\operatorname{Conf}_{2,3}(Q)$ | marked pair plus disjoint spectator triple |
| $U_x$, $H_x$ | occupied support and hole set of a configuration $x$ |
| $\Sigma_{m_d}$ | missing-image section, consisting of configurations with $m_d$ a hole |
| $\mathscr R_t=d\circ p^t$ | partial rotation--defect return |
| $t_i$ | exponent satisfying $p^{t_i}(m_d)=k_i$ |
| $g_i$ | globally enabled permutation return $d\circ p^{t_i}|_D$ |
| $G_d=\langle g_0,g_1\rangle$ | universal return group |
| $\pi_d$, $\mathcal N_d$ | orbit map and orbit space $\Sigma_{m_d}/G_d$ |
| $\Delta$ | positive cyclic separation with $p^\Delta(k_0)=k_1$ |
| $h_d=g_1g_0^{-1}$ | relative return |
| $H_d=\langle h_d\rangle$ | orientation-independent relative cyclic subgroup |
| $E_0=Q\setminus\{k_0\}$ | branch carrier used to conjugate the return group |
| $\psi_\Delta$ | punctured rotation conjugate to $h_d$ on $E_0$ |
| $a_d$ | free branch-completion parameter conjugate to $g_0$ |
| $\Gamma_\Delta(a)$ | cycle-gluing graph on the $\psi_\Delta$-cycles |
| $\mathscr D(K,m,c)$ | fixed-kernel, fixed-missing-image, fixed-collision defect fiber |

## Introduction

A rank-$(n-1)$ transformation has one local source of noninjectivity: two
kernel points share one image. Its dynamics inside a circular automaton are
nevertheless not local in the same sense. Away from the kernel, the defect
may transport occupied coordinates by an arbitrary labelled bijection. This
global transport affects which rank-preserving paths exist before the first
strict rank drop.

Paper XXIX solved the complete raw rank-five first-exit problem for the
canonical circular family

$$
 \begin{gathered}
 Q_n=\mathbb Z/n\mathbb Z,
 \qquad
 p_n(q)=q+1\pmod n,\\
 d_n(0)=d_n(1)=0,
 \qquad
 d_n(q)=q-1\quad(2\le q\le n-1),
 \end{gathered}
 \tag{1.1}
$$

using a missing-image section, a cyclic return, and a constructive hole-slide
normal form [@paper29]. Its section symmetry could appear to be special
machinery tied to the order-preserving formula (1.1). The present paper asks
for the structure that survives when the labelled defect is arbitrary.

The first answer is universal. Let $K_d=\{k_0,k_1\}$ and let $m_d$ be the
missing image. Rotating $m_d$ into either kernel point guarantees that the
other kernel point is not occupied. The subsequent defect step is therefore
rank-preserving for every state in the missing-image section. Each of these
two return blocks acts by a permutation of

$$
 D=Q\setminus\{m_d\}.
$$

They generate the universal return group

$$
 G_d=\langle g_0,g_1\rangle\le\operatorname{Sym}(D).
$$

The word *universal* refers to global enabledness on the section. It does not
mean that all defects produce isomorphic groups.

The second answer concerns quotienting. The remaining returns
$\mathscr R_t=d\circ p^t$ are partial: their guards can vary among
representatives of a single $G_d$-orbit. They need not descend to functions
on the orbit space. They do, however, descend to existential labelled
relations. Since every $G_d$-orbit is internally controllable by globally
enabled positive return words, this relation-valued quotient preserves and
reflects reachability exactly.

The third answer identifies a defect-independent part of the return group.
For an orientation $(k_0,k_1)$ of the kernel, define

$$
 h_d=g_1g_0^{-1}.
$$

Although the labelled permutation $h_d$ depends on the inverse branch of
$d$, its conjugacy class does not. It is a punctured rotation whose cycle
type is determined only by $n$ and the cyclic kernel separation $\Delta$.
This yields the paper's main structural regime:

$$
 \gcd(n,\Delta)=1
 \quad\Longrightarrow\quad
 C_{n-1}\cong H_d\le G_d,
 \tag{1.2}
$$

where $H_d=\langle h_d\rangle$ acts regularly on $D$. Thus

$$
 \boxed{
 \begin{gathered}
 \text{canonical cyclic symmetry is not exceptional machinery;}\\
 \text{it is the coprime-spacing shadow of a universal relative return.}
 \end{gathered}}
 \tag{1.3}
$$

Here *shadow* is descriptive shorthand for the canonical labelled
realization of the regular relative-return cycle. It does not name an
additional quotient, representation, or theorem premise.

The theorem spine has three parts.

1. Section 3 constructs the universal returns and proves strong connectivity
   inside each $G_d$-orbit.
2. Section 4 proves exact reachability reduction to a relation-valued orbit
   system and records its spectator-safe first-exit form.
3. Section 5 proves the punctured-rotation normal form and the
   coprime-spacing regime. Section 6 proves that the other branch return is a
   free permutation parameter, gives the exact cycle-gluing graph, and
   classifies its fixed-collision point-orbit partitions.
   Section 7 recovers (1.1) as a specialization.

The paper remains entirely at the intrinsic raw level. It does not infer a
typed transfer, authorization, handoff, or projection witness from a raw
path. Those interfaces motivated the all-$n$ question in Paper XXVIII, but
they are neither definitions nor premises here [@paper28].

### Related Work and Novelty Boundary

The Cerny conjecture asks for a quadratic reset bound for synchronizing
automata [@cerny1964; @volkov2008; @volkov2022survey]. Circular automata admit
stronger reset results under hypotheses different from those used here
[@dubuc1998]. Almost-group automata, formed from permutation letters and a
letter with one nontrivial kernel class, provide a nearby general setting
[@berlinkovNicaud2020]. This paper proves no reset bound and does not classify
general almost-group automata.

Recent work on completely reachable almost-group automata studies the nearby
class with exactly one defect-one letter and permutation letters, with
particular attention to transitive imprimitive permutation groups
[@casasTorres2024]. The present paper instead fixes a circular full-cycle
carrier and studies its globally enabled return group, the exact
punctured-rotation cycle type, and branchwise cycle gluing. It does not give a
complete-reachability characterization.

Monotonic and orientable automata isolate order-preserving regimes
[@eppstein1990]. Complete and subset reachability instead ask which unlabelled
subsets occur as images [@don2016; @gonzeJungers2018; @ferensSzykula2026]. The
objects here are different in two respects: a legal internal defect step must
remain injective on a marked pair together with three spectators, and the
quotient retains the marked colors while forgetting only motion internal to
a declared universal-return orbit.

Paper XXIX proves a path-free all-$n$ frontier classification for the
canonical circular family (1.1) [@paper29]. The new contribution here is not another
canonical classification. It is the general-defect construction of $G_d$,
the exact relation-valued reduction supported by its internal controllability,
and the punctured-rotation theorem for $h_d$. The latter explains why the
canonical $C_{n-1}$ appears and identifies a larger coprime-spacing regime in
which the same regular cyclic subgroup is forced, even when the original
$p$-cyclic order is not preserved by the defect.

## Raw Section Dynamics

Assume throughout that $n\ge6$. Let $Q$ be an $n$-element labelled set,
let $p$ be a full cycle on $Q$, and let

$$
 d:Q\longrightarrow Q
$$

have rank $n-1$. Such a map has one binary non-singleton fiber

$$
 K_d=\{k_0,k_1\},
 \qquad
 d(k_0)=d(k_1),
 \tag{2.1}
$$

and one missing image $m_d$. Every other fiber is a singleton. Write

$$
 D:=Q\setminus\{m_d\}=\operatorname{im}(d).
 \tag{2.2}
$$

The temporary orientation $(k_0,k_1)$ will label two returns. Swapping the
kernel points exchanges those returns. The groups and orientation-free
conclusions below do not change.

### Marked pair, spectators, and holes

Define

$$
 \operatorname{Conf}_{2,3}(Q)
 =\{(A,R):A,R\subseteq Q,\ |A|=2,\ |R|=3,\ A\cap R=\varnothing\}.
 \tag{2.3}
$$

The two points of $A$ are the candidate pair for a later strict fusion; the
three points of $R$ are spectators. For $x=(A,R)$ put

$$
 U_x:=A\cup R,
 \qquad
 H_x:=Q\setminus U_x.
 \tag{2.4}
$$

The cycle acts without a guard:

$$
 p(A,R)=(pA,pR).
 \tag{2.5}
$$

The defect acts only when it is injective on the full five-point support:

$$
 d(A,R)=(dA,dR).
 \tag{2.6}
$$

Because (2.1) is the unique non-singleton fiber, the guard is exactly

$$
 K_d\nsubseteq U_x
 \quad\Longleftrightarrow\quad
 H_x\cap K_d\ne\varnothing.
 \tag{2.7}
$$

Thus the spectator triple is part of legality, not an auxiliary decoration.

### Missing-image section and partial returns

The missing-image section is

$$
 \boxed{
 \Sigma_{m_d}
 =\{x\in\operatorname{Conf}_{2,3}(Q):m_d\in H_x\}.}
 \tag{2.8}
$$

Equivalently, both $A$ and $R$ are subsets of $D$. Every guarded defect
output belongs to this section because no occupied image can equal $m_d$.

For $t\in\mathbb Z/n\mathbb Z$, define the partial section return

$$
 \mathscr R_t=d\circ p^t.
 \tag{2.9}
$$

Words act on states from left to right, whereas maps compose from right to
left. Thus the written return block $p^td$ first applies $p^t$ and then $d$,
and its map is exactly $d\circ p^t$ as in (2.9).

Its domain is

$$
 \operatorname{Dom}(\mathscr R_t)
 =\{x\in\Sigma_{m_d}:p^tH_x\cap K_d\ne\varnothing\}.
 \tag{2.10}
$$

Whenever it is defined, $\mathscr R_t(x)$ again belongs to
$\Sigma_{m_d}$.

## Universal Returns and the Group $G_d$

For $i\in\{0,1\}$, let $t_i\in\mathbb Z/n\mathbb Z$ be the unique exponent
such that

$$
 p^{t_i}(m_d)=k_i.
 \tag{3.1}
$$

Define

$$
 g_i:=\left.d\circ p^{t_i}\right|_D.
 \tag{3.2}
$$

**Theorem 3.1 (universal return-group theorem).** For every labelled
binary-kernel rank-$(n-1)$ defect $d$:

1. $\mathscr R_{t_i}$ is defined on every state of $\Sigma_{m_d}$;
2. $g_i\in\operatorname{Sym}(D)$;
3. on the section,
   $$
    \mathscr R_{t_i}(A,R)=(g_iA,g_iR);
    \tag{3.3}
   $$
4. the subgroup
   $$
    \boxed{G_d:=\langle g_0,g_1\rangle\le\operatorname{Sym}(D)}
    \tag{3.4}
   $$
   is independent of the orientation of $K_d$; and
5. each $G_d$-orbit in $\Sigma_{m_d}$ is strongly connected by positive
   words in the two globally enabled return blocks.

**Proof.** Let $x\in\Sigma_{m_d}$. Since $m_d\in H_x$, equation (3.1)
gives $k_i\in p^{t_i}H_x$. The guard (2.7) therefore holds after the
rotation, so $\mathscr R_{t_i}$ is defined for every section state.

The cycle restricts to a bijection

$$
 p^{t_i}:D\overset{\sim}{\longrightarrow}Q\setminus\{k_i\}.
 \tag{3.5}
$$

Since $K_d$ is the only non-singleton fiber of $d$, deletion of either kernel
point leaves a bijection

$$
 d|_{Q\setminus\{k_i\}}:
 Q\setminus\{k_i\}\overset{\sim}{\longrightarrow}D.
 \tag{3.6}
$$

Their composition is the permutation $g_i$, and applying it simultaneously
to $A$ and $R$ gives (3.3).

Swapping $k_0,k_1$ swaps $t_0,t_1$ and hence swaps the two generators, so
$G_d$ is unchanged. Finally, every $g_i$ has finite order. Its inverse is a
positive power of itself. Every word in $g_0^{\pm1},g_1^{\pm1}$ is therefore
realized by a positive word in globally enabled return blocks. Any two states
in one $G_d$-orbit are mutually reachable. $\square$

The theorem does not say that the abstract group or its concrete action is
the same for all defects. It identifies the symmetry that every defect
supplies from its own two kernel branches.

## Exact Relation-Valued Orbit Reduction

Let

$$
 \pi_d:\Sigma_{m_d}\longrightarrow
 \mathcal N_d:=\Sigma_{m_d}/G_d
 \tag{4.1}
$$

be the orbit projection. A partial return $\mathscr R_t$ need not descend to
a function on $\mathcal N_d$. Two representatives in one orbit may have
different guards, and guarded representatives may enter different output
orbits. Requiring a deterministic quotient would add a congruence theorem
that is generally unavailable.

Instead define the labelled relation

$$
 \boxed{
 O\xrightarrow{t}_d O'
 \iff
 \exists x\in O\cap\operatorname{Dom}(\mathscr R_t),
 \quad \mathscr R_t(x)\in O'.}
 \tag{4.2}
$$

For $X\subseteq\Sigma_{m_d}$, write

$$
 x\leadsto_{\Sigma}X
$$

when a finite sequence of defined section returns sends $x$ into $X$. Write

$$
 O\leadsto_{\mathcal N}\pi_d(X)
$$

for reachability through (4.2), where the terminal orbit need only intersect
$X$.

**Theorem 4.1 (exact relation-valued orbit reduction).** For every
$x\in\Sigma_{m_d}$ and every $X\subseteq\Sigma_{m_d}$,

$$
 \boxed{
 x\leadsto_{\Sigma}X
 \iff
 \pi_d(x)\leadsto_{\mathcal N}\pi_d(X).}
 \tag{4.3}
$$

**Proof.** Projecting a section path gives a path in (4.2).

Conversely, take a quotient path. For its first edge, choose a witness $x'$ in
(4.2). The current section state and $x'$ belong to the same $G_d$-orbit.
Theorem 3.1 supplies a positive word in globally enabled returns carrying the
current state to $x'$. Apply the witnessed partial return. Repeat this
procedure edge by edge. In the terminal orbit, use universal returns once
more to reach the chosen representative in $X$. The resulting section path
lifts the whole quotient path. $\square$

The theorem proves preservation and reflection of reachability. It does not
assert that $\pi_d$ is a transition congruence, that an edge in (4.2) has a
unique witness, or that $\mathscr R_t$ has a single-valued quotient action.

### Spectator-safe target reduction

For a section state $x=(A,R)$, define the section exit set

$$
 \mathcal T_d^{\Sigma}
 =\{(A,R)\in\Sigma_{m_d}:
   \exists u\in\mathbb Z/n\mathbb Z,\ p^uA=K_d\}.
 \tag{4.4}
$$

Membership means that a final pure rotation can place the marked pair on the
kernel, after which the next defect step is strict. Let
$\operatorname{SafeHit}_d(x)$ mean that a word preserves injectivity on the
whole marked pair plus spectator triple at every proper defect step and then
performs one strict terminal defect step whose fused lineages are the marked
pair.

**Corollary 4.2 (section Safe-Hit reduction).** For
$x\in\Sigma_{m_d}$,

$$
 \boxed{
 \operatorname{SafeHit}_d(x)
 \iff
 \pi_d(x)\leadsto_{\mathcal N}
 \pi_d(\mathcal T_d^{\Sigma}).}
 \tag{4.5}
$$

**Proof.** Group every plateau word between consecutive defect events into a
return block $p^td$, represented on the section by
$\mathscr R_t=d\circ p^t$. The final pure rotation is exactly condition
(4.4). Apply Theorem 4.1. $\square$

For completeness, the reduction extends to a starting configuration not yet
in the section. Define

$$
 \operatorname{First}_t(x):=\mathscr R_t(x)
 \tag{4.6}
$$

whenever the rotation followed by $d$ is a plateau step, equivalently

$$
 K_d\nsubseteq p^tU_x
 \quad\Longleftrightarrow\quad
 p^tH_x\cap K_d\ne\varnothing.
 \tag{4.7}
$$

Every such output belongs to $\Sigma_{m_d}$.

**Corollary 4.3 (first-entry decomposition).** For every
$x=(A,R)\in\operatorname{Conf}_{2,3}(Q)$,

$$
\begin{aligned}
 \operatorname{SafeHit}_d(x)
 \iff{}&
 \bigl[\exists u,\ p^uA=K_d\bigr]\\
 &\lor
 \bigl[\exists t,\ K_d\nsubseteq p^tU_x
 \text{ and }
 \pi_d(\operatorname{First}_t(x))
 \leadsto_{\mathcal N}
 \pi_d(\mathcal T_d^{\Sigma})\bigr].
\end{aligned}
\tag{4.8}
$$

**Proof.** If a safe word contains no plateau defect event before its terminal
strict step, its preceding letters form a power of $p$, giving the first
branch. Otherwise isolate its first plateau defect event. Its preceding
prefix is $p^t$; condition (4.7) holds, the output enters the section, and
Corollary 4.2 applies to the remaining return blocks. Conversely, either
branch concatenates to a spectator-safe word with the required terminal
fusion. $\square$

Corollaries 4.2 and 4.3 reduce the raw problem. They do not yet characterize
the orbit relation (4.2) for an arbitrary defect.

## Relative Return and Punctured Rotation

Retain the temporary orientation $(k_0,k_1)$. Define

$$
 E_i:=Q\setminus\{k_i\},
 \qquad
 b_i:=d|_{E_i}:E_i\overset{\sim}{\longrightarrow}D.
 \tag{5.1}
$$

Let $\Delta\in\{1,\ldots,n-1\}$ be the positive cyclic separation defined
by

$$
 p^\Delta(k_0)=k_1.
 \tag{5.2}
$$

Equivalently, $\Delta=t_1-t_0\pmod n$. Define the relative return

$$
 \boxed{h_d:=g_1g_0^{-1}\in G_d.}
 \tag{5.3}
$$

**Theorem 5.1 (punctured-rotation normal form).** Put

$$
 g:=\gcd(n,\Delta),
 \qquad
 \ell:=\frac{n}{g}.
 \tag{5.4}
$$

Then:

1. the branch-change bijection
   $$
    \eta:E_1\longrightarrow E_0,
    \qquad
    \eta(k_0)=k_1,
    \qquad
    \eta(q)=q\quad(q\notin K_d)
    \tag{5.5}
   $$
   satisfies
   $$
    \boxed{
    b_0^{-1}h_db_0
    =\eta\circ p^\Delta|_{E_0};}
    \tag{5.6}
   $$
2. in cyclic coordinates with $k_0=0$ and $k_1=\Delta$, this conjugate is
   the punctured rotation
   $$
    \psi_\Delta(x)=
    \begin{cases}
      x+\Delta, & x+\Delta\not\equiv0\pmod n,\\
      \Delta, & x\equiv-\Delta\pmod n,
    \end{cases}
    \qquad x\in Q\setminus\{0\};
    \tag{5.7}
   $$
3. the cycle type of $h_d$ is
   $$
    \boxed{
    \operatorname{ctype}(h_d)
    =(\ell-1,\ell^{\,g-1});}
    \tag{5.8}
   $$
4. the subgroup
   $$
    \boxed{H_d:=\langle h_d\rangle\le G_d}
    \tag{5.9}
   $$
   is independent of the orientation of the kernel; and
5. if $\gcd(n,\Delta)=1$, then $h_d$ is an $(n-1)$-cycle on $D$, so
   $$
    H_d\cong C_{n-1},
    \qquad
    G_d=\langle g_0,h_d\rangle
    \text{ is transitive on }D.
    \tag{5.10}
   $$

**Proof.** From (3.2) and (5.1),

$$
 g_i=b_i\circ p^{t_i}|_D.
 \tag{5.11}
$$

The inverse of $g_0$ is

$$
 g_0^{-1}=p^{-t_0}\circ b_0^{-1},
$$

with domains and codomains fixed by (3.5)--(3.6). Hence

$$
 h_d
 =b_1\circ p^{t_1-t_0}\circ b_0^{-1}
 =b_1\circ p^\Delta\circ b_0^{-1}.
 \tag{5.12}
$$

The maps $b_0^{-1}$ and $b_1^{-1}$ are the two inverse branches of $d$.
They agree away from the collision image. More explicitly,
$b_0^{-1}b_1:E_1\to E_0$ fixes every point of $Q\setminus K_d$ and maps
$k_0$ to $k_1$. Thus

$$
 b_0^{-1}b_1=\eta.
 \tag{5.13}
$$

Conjugating (5.12) by $b_0$ proves (5.6).

Set $k_0=0$ and $k_1=\Delta$. Translation by $\Delta$ maps
$E_0=Q\setminus\{0\}$ to $E_1=Q\setminus\{\Delta\}$. The map $\eta$ fixes
its output unless that output is $0$, in which case it maps $0$ to $\Delta$.
This is (5.7).

Translation by $\Delta$ on $Q$ has $g$ cycles, each of length $\ell$. The
cycle containing $0$ is

$$
 0,\Delta,2\Delta,\ldots,-\Delta.
$$

Deleting $0$ and replacing the arrow $-\Delta\mapsto0$ by
$-\Delta\mapsto\Delta$ produces one cycle of length $\ell-1$. The other
$g-1$ cycles remain cycles of length $\ell$. This proves (5.8), where the
exponent records multiplicity and contributes no $\ell$-cycle when $g=1$.

Swapping $k_0,k_1$ swaps $g_0,g_1$ and replaces $h_d$ by

$$
 g_0g_1^{-1}=h_d^{-1}.
$$

It leaves $H_d$ unchanged. Finally, when $g=1$, equation (5.8) consists of
one cycle of length $n-1$. Thus $H_d$ acts regularly on $D$, and every
overgroup containing it is transitive. Since $g_1=h_dg_0$, one also has
$G_d=\langle g_0,h_d\rangle$. $\square$

Theorem 5.1 removes the off-kernel transport from the conjugacy class of the
relative return, not from the entire defect dynamics. The actual labelled
permutation $h_d$ still depends on the branch labelling $b_0$, and the
remaining return $g_0$ can interact differently with the cycles in (5.8).

**Corollary 5.2 (coprime-spacing regime).** If
$\gcd(n,\Delta)=1$, the missing-image section has an intrinsic regular cyclic
symmetry $H_d\cong C_{n-1}$. In particular, if $n$ is prime, every labelled
binary-kernel rank-$(n-1)$ defect lies in this regime.

Moreover, Theorem 4.1 remains valid with $H_d$ in place of $G_d$: each
$H_d$-orbit is strongly connected by positive words in globally enabled
return blocks, and the relation-valued quotient

$$
 \Sigma_{m_d}/H_d
 \tag{5.14}
$$

preserves and reflects section reachability.

**Proof.** The first statement follows from Theorem 5.1. If $n$ is prime,
every $1\le\Delta\le n-1$ is coprime to $n$. For the quotient statement,
$h_d=g_1g_0^{-1}$ and $h_d^{-1}$ are positive words in $g_0,g_1$ because
those generators have finite order. Hence every $H_d$-orbit is internally
controllable by globally enabled returns, which is the only group-specific
input in the lifting direction of Theorem 4.1. $\square$

The quotient (5.14) is a **relative-return necklace quotient**. Its cyclic
order is the orbit order of $h_d$, not necessarily the original $p$-order.
Corollary 5.2 does not classify the remaining guarded return edges or the
Safe-Hit target in that cyclic order.

## Free Branch Completion and Exact Cycle Gluing

Theorem 5.1 fixes the conjugacy class of $h_d$ but leaves open how the other
generator meets its cycles. That remaining datum is genuinely free.

Fix $p$, an oriented kernel $K=\{k_0,k_1\}$, and a missing image $m$. Let

$$
 E_0:=Q\setminus\{k_0\},
 \qquad
 D:=Q\setminus\{m\},
 \tag{6.1}
$$

and let $t_0$ satisfy $p^{t_0}(m)=k_0$. Write
$\mathscr D(K,m)$ for the set of all rank-$(n-1)$ maps whose unique binary
kernel is $K$ and whose missing image is $m$. For
$d\in\mathscr D(K,m)$, put

$$
 b_0:=d|_{E_0}:E_0\overset{\sim}{\longrightarrow}D,
 \qquad
 \boxed{a_d:=p^{t_0}\circ b_0\in\operatorname{Sym}(E_0).}
 \tag{6.2}
$$

Let $\psi_\Delta$ denote the punctured rotation (5.7) on $E_0$, expressed in
coordinates with $k_0=0$ and $k_1=\Delta$.

**Theorem 6.1 (free branch-completion theorem).** The map

$$
 \Phi_{K,m}:\mathscr D(K,m)\longrightarrow\operatorname{Sym}(E_0),
 \qquad
 d\longmapsto a_d,
 \tag{6.3}
$$

is a bijection. Under conjugation by the branch map $b_0$,

$$
 \boxed{
 b_0^{-1}g_0b_0=a_d,
 \qquad
 b_0^{-1}h_db_0=\psi_\Delta,
 \qquad
 b_0^{-1}G_db_0=\langle a_d,\psi_\Delta\rangle.}
 \tag{6.4}
$$

**Proof.** For a given defect, $b_0:E_0\to D$ is a bijection and
$p^{t_0}:D\to E_0$ is a bijection, so (6.2) defines a permutation.

Conversely, let $a\in\operatorname{Sym}(E_0)$ and set

$$
 b_a:=p^{-t_0}\circ a:E_0\overset{\sim}{\longrightarrow}D.
 \tag{6.5}
$$

Define $d_a:Q\to Q$ by

$$
 d_a(q)=b_a(q)\quad(q\in E_0),
 \qquad
 d_a(k_0)=b_a(k_1).
 \tag{6.6}
$$

The map $b_a$ is injective with image $D$. Equation (6.6) introduces exactly
one repeated fiber, namely $\{k_0,k_1\}$, and introduces no further image.
Thus $d_a\in\mathscr D(K,m)$. Its branch map is $b_a$, and

$$
 p^{t_0}b_a=a.
$$

This construction is inverse to (6.3), because a defect in
$\mathscr D(K,m)$ is determined by its restriction to $E_0$: its omitted
value at $k_0$ must equal the value at $k_1$.

Finally, $g_0=b_0p^{t_0}|_D$, so

$$
 b_0^{-1}g_0b_0=p^{t_0}b_0=a_d.
$$

The middle identity in (6.4) is Theorem 5.1, and the group identity follows
from $G_d=\langle g_0,h_d\rangle$. $\square$

If the collision image $c=d(k_0)=d(k_1)$ is also fixed, the free parameter is
restricted by the single point condition

$$
 a_d(k_1)=p^{t_0}(c).
 \tag{6.7}
$$
The exact fiber and its gluing consequences are classified after the
unrestricted cycle-gluing theorem.

### The cycle-gluing graph

Let $\mathcal C_\Delta$ be the set of cycles of $\psi_\Delta$. By Theorem
5.1 it consists of one cycle of length $\ell-1$ and $g-1$ cycles of length
$\ell$. For $a\in\operatorname{Sym}(E_0)$, define the undirected
**cycle-gluing graph** $\Gamma_\Delta(a)$ by

$$
 V(\Gamma_\Delta(a))=\mathcal C_\Delta,
 \tag{6.8}
$$

with an edge between $C,C'\in\mathcal C_\Delta$ whenever

$$
 \exists x\in C,\qquad a(x)\in C'.
 \tag{6.9}
$$

Loops may be discarded. The graph records incidence, not a deterministic map
on the cycle set: one permutation can send different points of one
$\psi_\Delta$-cycle into several cycles.

**Theorem 6.2 (exact cycle-gluing theorem).** The orbits of
$\langle a,\psi_\Delta\rangle$ on $E_0$ are exactly the unions

$$
 \bigcup_{C\in\mathcal K}C,
 \tag{6.10}
$$

where $\mathcal K$ ranges over the connected components of
$\Gamma_\Delta(a)$. Consequently,

$$
 \boxed{
 G_d\text{ is transitive on }D
 \iff
 \Gamma_\Delta(a_d)\text{ is connected}.}
 \tag{6.11}
$$

**Proof.** A power of $\psi_\Delta$ stays inside one vertex cycle of
$\Gamma_\Delta(a)$. An application of $a$ or $a^{-1}$ crosses one of its
undirected edges. Hence every group orbit is contained in the union attached
to one connected component.

Conversely, suppose $C,C'$ are adjacent. If some $x\in C$ satisfies
$a(x)\in C'$, move inside $C$ to $x$ and apply $a$. Otherwise the edge has a
witness $y\in C'$ with $a(y)\in C$; move inside $C$ to $a(y)$ and apply
$a^{-1}$. In either case one can pass from any point of $C$ into $C'$ and
then reach every point of $C'$ by powers of $\psi_\Delta$. Repeating along a
graph path connects every pair of points in (6.10). This proves the orbit
statement. Conjugation by $b_0$ and (6.4) give (6.11). $\square$

The graph therefore answers exactly how $g_0$ glues the
$(\ell-1,\ell,\ldots,\ell)$ cycles. There is no stronger universal gluing
law on the unrestricted fiber $\mathscr D(K,m)$.

**Corollary 6.3 (realization of every cycle partition).** Fix $p$, the
oriented kernel $K$, and the missing image $m$. For every set partition
$\mathcal P$ of $\mathcal C_\Delta$, there exists
$d\in\mathscr D(K,m)$ whose point-orbit partition on $D$ corresponds under
$b_0$ to

$$
 \left\{
 \bigcup_{C\in\mathcal K}C:
 \mathcal K\in\mathcal P
 \right\}.
 \tag{6.12}
$$

**Proof.** For each block $\mathcal K\in\mathcal P$, choose a cyclic ordering
of all points in $\bigcup_{C\in\mathcal K}C$ and let $a_{\mathcal K}$ be the
corresponding full cycle on that union. Let $a$ be the product of these
disjoint cycles. Its gluing graph has precisely the blocks of $\mathcal P$ as
connected components. Theorem 6.1 realizes $a$ by a defect in
$\mathscr D(K,m)$, and Theorem 6.2 gives (6.12). $\square$

When $g>1$, the discrete partition and the one-block partition in Corollary
6.3 give defects with the same oriented kernel and missing image for which
$G_d$ is respectively nontransitive and transitive. Thus the kernel spacing
fixes the relative-return cycle type but does not fix how those cycles are
joined.

The first constrained fiber is also exact. Fix a collision image $c\in D$
and define

$$
 \mathscr D(K,m,c)
 :=\{d\in\mathscr D(K,m):d(k_0)=d(k_1)=c\},
 \qquad
 y_c:=p^{t_0}(c)\in E_0.
 \tag{6.13}
$$

Put $s:=k_1$, and let $C_s,C_c\in\mathcal C_\Delta$ be the
$\psi_\Delta$-cycles containing $s$ and $y_c$, respectively.

**Corollary 6.4 (fixed-collision branch fiber and exact gluing
constraint).** Restriction of the branch-completion bijection gives

$$
 \boxed{
 \mathscr D(K,m,c)
 \overset{\sim}{\longrightarrow}
 \{a\in\operatorname{Sym}(E_0):a(s)=y_c\},
 \qquad d\longmapsto a_d.}
 \tag{6.14}
$$

In particular,

$$
 \bigl|\mathscr D(K,m,c)\bigr|=(n-2)!.
 \tag{6.15}
$$

A set partition $\mathcal P$ of $\mathcal C_\Delta$ is the point-orbit
partition of some $d\in\mathscr D(K,m,c)$ if and only if

$$
 \boxed{
 \begin{aligned}
 C_s\ne C_c
 &\ \Longrightarrow\
 C_s\text{ and }C_c\text{ lie in the same block of }\mathcal P,\\
 y_c=s\text{ and }C_s=\{s\}
 &\ \Longrightarrow\
 \{C_s\}\text{ is a block of }\mathcal P.
 \end{aligned}}
 \tag{6.16}
$$

**Proof.** Equation (6.7) shows that $\Phi_{K,m}$ maps
$\mathscr D(K,m,c)$ into the right-hand side of (6.14). Conversely, if
$a(s)=y_c$, then the inverse construction (6.5)--(6.6) gives

$$
 d_a(k_0)=d_a(k_1)=p^{-t_0}a(s)=c.
$$

This proves (6.14). Since $|E_0|=n-1$, fixing the image of one point leaves
$(n-2)!$ permutations, proving (6.15).

For necessity in (6.16), if $C_s\ne C_c$, the fixed arrow
$s\mapsto y_c$ is an edge joining those two cycle vertices. If $y_c=s$ and
$C_s=\{s\}$, then $a(s)=s$ and bijectivity prevents every other point from
mapping to $s$; hence $C_s$ is isolated in the gluing graph.

For sufficiency, first treat every block of $\mathcal P$ not containing
$C_s$ as in Corollary 6.3, using one full permutation cycle on the union of
its $\psi_\Delta$-cycles. Let $\mathcal K_s$ be the block containing $C_s$.
If $y_c\ne s$, the first condition places $C_c$ in $\mathcal K_s$ whenever
it is distinct from $C_s$; choose one full cycle on
$\bigcup_{C\in\mathcal K_s}C$ in which $s$ is immediately followed by
$y_c$. If $y_c=s$ and $C_s\ne\{s\}$, fix $s$ and choose one full cycle on

$$
 \left(\bigcup_{C\in\mathcal K_s}C\right)\setminus\{s\}.
$$

This remaining cycle still meets $C_s$ and every other vertex cycle in
$\mathcal K_s$, so its gluing graph is connected there. Finally, if
$y_c=s$ and $C_s=\{s\}$, the second condition gives
$\mathcal K_s=\{C_s\}$; fix $s$. The product of these disjointly supported
permutations satisfies $a(s)=y_c$ and has connected components exactly
$\mathcal P$. Equations (6.14) and Theorem 6.2 realize it by the required
defect and identify its point-orbit partition. $\square$

## Canonical Specialization

For the canonical labelled family $(Q_n,p_n,d_n)$ of (1.1),

$$
 K_{d_n}=\{0,1\},
 \qquad
 m_{d_n}=n-1.
 \tag{7.1}
$$

Orient the kernel as $(0,1)$. Then

$$
 t_0=1,
 \qquad
 t_1=2.
 \tag{7.2}
$$

On $D=\{0,\ldots,n-2\}$, direct substitution gives

$$
 g_0=\operatorname{id},
 \qquad
 g_1(r)=r+1\pmod{n-1}.
 \tag{7.3}
$$

**Proposition 7.1 (canonical return group).** For the circular automaton
$(Q_n,p_n,d_n)$,

$$
 \boxed{G_{d_n}=H_{d_n}\cong C_{n-1}.}
 \tag{7.4}
$$

The orbit order is the ordinary cyclic order on
$D=\mathbb Z/(n-1)\mathbb Z$, and the quotient of Theorem 4.1 is the
necklace reduction used in Paper XXIX.

**Proof.** Equation (7.3) shows that $G_{d_n}=\langle g_1\rangle$. Here
$\Delta=1$, so $h_{d_n}=g_1$ and Theorem 5.1 gives the same regular cyclic
subgroup. $\square$

The proposition is a specialization, not a premise for the general theory.
Conversely, Theorem 5.1 explains the canonical symmetry conceptually: its
regular cycle is the simplest labelled realization of the relative return
forced throughout the coprime-spacing regime. Paper XXIX adds the further
order-preservation and hole-slide arguments needed for a complete canonical
frontier classification; those properties do not follow from (7.4) alone.

## Computational Artifacts

The paper-owned package is available under
[`experiments/paper30/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper30)
in the RIME repository.

| Surface | Paper-owned path | Role |
|---|---|---|
| Bounded consistency control | `return_group_audit.py` and `results/` | Exhaustively replays the branch, relative-return, gluing, and fixed-collision definitions for $6\le n\le8$ |
| Partial formalization | `lean/` | Checks the data-independent quotient, cycle-gluing, and fixed-fiber implication spine |
| Development validation | `development-manifest.json` and `validation/` | Binds and replays the draft paper-owned closure |
| Release validation | `release-manifest.json`, `release-environment.json`, and `validation/` | Binds the reader PDF and nested development closure; records local closure verification |

The retained finite audits are bounded consistency controls bound into the
development closure. They cover $40{,}200$ branch-completion cases and $110$
fixed-collision fibers. They are not proofs of the all-$n$ theorems and are
not promoted as independent Computational Certificates. The Lean development
does not formalize the
punctured-rotation arithmetic or the constructive permutation realizations.
The nested development manifest claims no publication identity. The outer
release receipt records local closure verification, not independent
mathematical validation.

## Claim Status and Boundary

| Surface | Status | Scope |
|---|---|---|
| Globally enabled returns $g_0,g_1$ | Theorem 3.1 | Every labelled binary-kernel rank-$(n-1)$ defect, $n\ge6$ |
| Orientation-independent return group $G_d$ | Theorem 3.1 | Same scope |
| Strong connectivity inside each $G_d$-orbit | Theorem 3.1 | Positive words in the universal return blocks |
| Relation-valued orbit reachability reduction | Theorem 4.1 | Every subset of the missing-image section |
| Section Safe-Hit reduction | Corollary 4.2 | Raw marked-pair plus three-spectator dynamics |
| First-entry decomposition | Corollary 4.3 | Arbitrary raw $2+3$ starting state |
| Punctured-rotation normal form | Theorem 5.1 | Every labelled defect in the declared scope |
| Coprime-spacing regular cyclic subgroup | Corollary 5.2 | $\gcd(n,\Delta)=1$; all defects when $n$ is prime |
| Free branch-completion parameter | Theorem 6.1 | Fixed oriented kernel and missing image; collision image not fixed |
| Exact cycle-gluing graph | Theorem 6.2 | Every labelled defect in the declared scope |
| Realization of every relative-cycle partition | Corollary 6.3 | Fixed oriented kernel and missing image; collision image may vary |
| Fixed-collision branch fiber and cardinality | Corollary 6.4 | Fixed oriented kernel, missing image, and collision image |
| Exact fixed-collision point-orbit partitions | Corollary 6.4 | Forced join, with the stated singleton forced-isolation exception |
| Canonical cyclic specialization | Proposition 7.1 | The circular family $(Q_n,p_n,d_n)$ of (1.1) |
| Classification of abstract groups $G_d$ | Open | Not determined by the point-orbit partition alone |
| General orbit-edge or Safe-Hit characterization | Open | Remaining guarded returns on the concrete orbit quotient |
| Complete survivor-placement frontier | Open | Requires terminal incidence after pair hitting |
| Raw-to-typed transfer/projectability bridge | Open | No new semantic fields are introduced here |

The theorem proofs are data-independent. The finite audits are bounded
consistency controls bound into the development closure. They are not proofs
of the all-$n$ theorems, are not manuscript premises, and are not promoted as
independent Computational Certificates.

The following implications are explicitly excluded:

$$
 G_d\cong G_{d'}
 \quad\Longrightarrow\quad
 \text{equal spectator-safe frontiers},
 \tag{8.1}
$$

$$
 G_d\text{ transitive on }D
 \quad\Longrightarrow\quad
 \text{automatic Safe-Hit},
 \tag{8.2}
$$

and

$$
 \text{raw Safe-Hit}
 \quad\Longrightarrow\quad
 \text{declared transfer membership or projectability}.
 \tag{8.3}
$$

The quotient theorem uses the concrete group action and the concrete
relation (4.2), not merely the abstract isomorphism type of $G_d$.

## Conclusion

Every labelled binary-kernel rank-$(n-1)$ defect induces two globally enabled
permutation returns on its missing-image section. Their group supplies exact
internal controllability, which is precisely what permits partial return
dynamics to be reduced as a relation without pretending that the orbit map
is a deterministic congruence.

The relative return between the two kernel branches has a stronger universal
form. Up to branch conjugacy it is rotation by the kernel separation with one
point deleted and the gap closed. Its cycle type is therefore fixed by
$(n,\Delta)$, and coprime kernel spacing forces a regular cyclic subgroup of
order $n-1$. Outside that regime, and on the fiber with kernel and missing
image fixed, the other branch return is a free permutation parameter: its
incidence graph on the punctured-rotation cycles determines the point-orbits
of $G_d$ on $D$ exactly, and every partition of those cycles is realizable.
Fixing the collision image cuts the free branch to a one-point permutation
fiber and yields the exact forced-join and singleton-isolation rules of
Corollary 6.4. The cyclic mechanism isolated in the canonical family is thus
a special visible case of a general branch-relative symmetry.

### Outlook

The next general-defect questions begin after, not inside, the present
theorem spine. The point-orbit partition on $D$ is now explicit both on the
broad fixed-$(K,m)$ fiber and on its fixed-collision subfibers. The remaining
group-theoretic question is which abstract subgroups
$\langle a,\psi_\Delta\rangle$ and coloring orbits matter under constraints
beyond $(K,m,c)$, such as order-preserving transport, parity, or a prescribed
off-kernel table.
The dynamical question is whether the remaining existential quotient edges
admit path-free normal forms. A full frontier theorem would additionally need
the terminal survivor-incidence map. The separate raw-to-typed bridge remains
an interface theorem: neither group symmetry nor raw reachability supplies it
automatically.
