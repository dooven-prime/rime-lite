# Registered Absorption Chains and Placement Fibers for a Circular Action with an Adjacent Idempotent

**WuJun Chen**

Independent Researcher | 2026

*Unnumbered short-article draft.*

## Abstract

We study a deterministic action starting with one labelled atom at each
position of an $n$-cycle. Its letters are cyclic rotation and the adjacent
idempotent collapse that moves position $1$ to $0$ and fixes every other
position. Packets merge when their positions coincide.
Register the event that first creates the packet $F=\{0,1\}$, and retain
its ordered parent blocks, every subsequent absorption involving its
carrier, and the complete current placed partition. We count these
registered summaries over all finite executions, without a word-length
budget.

The complete selected absorption chains are in bijection with
$\{0,L,R\}^{n-2}$: nonzero positions specify cumulative absorbed sizes,
and their signs specify the carrier's collision port. For $n\ge3$, a fixed
chain leaving $k$ atoms outside its carrier has exactly
$n\binom{n+k-2}{k}$ summaries. The key step is constructive reachability:
every encoded chain has an actual execution, and every placed partition
satisfying the fixed-chain carrier, interval, and source-order conditions
is reached without changing that selected chain.
Summing the disjoint fibers then gives an exact total $s_n$ and the estimate
$s_n=n(9/2)^{n-2}(1+\epsilon_n)$ with
$|\epsilon_n|\le(8/9)^{n-2}$. In particular,
$\lim_{n\to\infty}s_n^{1/n}=9/2$.

The objects counted are event-anchored summaries, not execution words,
endpoint transformations, or minimal predictive equivalence classes.
The statements concern this fixed action and registered pair; they give
neither shortest words nor a lower bound for consumer-checking algorithms.

**Keywords:** circular adjacent collapse; absorption chain; cyclic order;
event-anchored state; exact enumeration

## 1. Introduction

An endpoint partition does not record the event that created a selected
packet or its later absorptions. An event-anchored consumer instead follows
the carrier from registration onward [@chenPaper39v1]. Even on a finite
position set, counting the resulting summaries requires knowing which
event chains and current placements occur together along an actual history.

We solve this counting problem for one explicit circular action. The
initial state consists of $n$ singleton packets in their identity
positions. The two letters are a cyclic rotation $p$ and the adjacent
idempotent collapse $d:1\mapsto0$. We register exactly the freshly created
source block $F=\{0,1\}$, retaining its origin and complete subsequent
absorption chain. Already for $n=4$, the words $dpdpd$ and $dppdpdpd$
send every atom to position $0$, but the first carrier absorbs $\{3\}$
and then $\{2\}$, whereas the second absorbs $\{2,3\}$ in one event.
Thus one endpoint is compatible with different selected chains; Section 2.2
gives the port-ordered records. We enumerate jointly realizable registered
absorption chains and their complete placement fibers, rather than
endpoints or histories separately. An execution may be arbitrarily long;
no word-length bound is imposed. The number of fusions is nevertheless
bounded by the number of source atoms.

The proof's main step is constructive reachability. A local nonfusion move
controls all placements with a prescribed cyclic block order. It realizes
every ternary checkpoint code as a selected chain and, for each fixed
chain, every compatible placed partition without altering that chain.
Only then does a binomial sum determine the total and its growth. A
formally compatible partition is not assumed to have a generating history.

### 1.1. Related work and the counting object

In phylogenetic labelled histories, a rooted leaf-labelled tree is equipped
with an ancestry-compatible order of its internal nodes. Dickey and
Rosenberg count such orders both for fixed topologies and, in Proposition 1,
in total over all labelled topologies with at most $r$ children per internal
node [@dickeyRosenberg2026]. The unrestricted non-simultaneous total obeys
$H(1)=1$ and $H(n)=\sum_{j=2}^{n}\binom nj H(n-j+1)$, beginning
$1,1,4,29,336$ [@wirtz2024; @dickeyRosenberg2026]. Simultaneous-event
variants give other histories [@dickeyRosenberg2025]. None of these objects
distinguishes a carrier followed from a registered adjacent-port event, or
retains its current placement in a deterministic $p,d$ execution. Tree-pair
coalescent histories instead assign gene-tree coalescences to compatible
species-tree branches [@alimpievRosenberg2021]. Here each executed fusion
joins two packets at adjacent ports. Fusions not involving the selected
carrier may assemble a later partner, but are omitted from its chain.

Orientation-preserving transformation monoids provide a separate endpoint
baseline [@catarinoHiggins1999; @higginsVernitski2022]. For full maps of
rank $r>1$, Catarino and Higgins' formula is $r\binom nr^2$; Umar recovers
it as Corollary 15 within a broader width/height/waist enumeration of
partial maps, using convex kernel cuts, image choices and cyclic bindings
[@catarinoHiggins1999; @umar2011, Proposition 5 and Corollary 15].
Dagdeviren and Ayik enumerate idempotents by rank and fixed-point
data, and order-decreasing or nilpotent endpoint subclasses
[@dagdevirenAyik2024]. These outputs classify transformations, not an
ordered post-registration chain paired with a reachable placement. Our
fiber count uses classical cuts and cyclic binding with a fixed carrier;
its additional obligation is joint reachability without changing the
selected chain. Cycle-graph endomorphism monoids impose another adjacency
condition: for $n\ge4$, our $d$ sends the edge $\{1,2\}$ to the nonedge
$\{0,2\}$ [@dimitrovaEtAl2023].

Coalescing-particle systems can instead ask for probabilities of specified
merger patterns under stochastic motion [@sniadyUrban2026]. That question
does not impose the present deterministic $p,d$ action or count jointly
attainable selected-chain and current-placement pairs.

The object here is a current placement together with a registered origin
and an ordered selected absorption chain. Distinct chains remain distinct
even if they reach the same endpoint. Lemma 2.2 gives nonfusion placement
control; Theorem 3.1 constructs every encoded chain; and Theorem 4.2
constructs every compatible placement within each fixed-chain fiber.
Theorem 5.1 then sums these disjoint fibers. Thus the substantive step is
actual joint attainability, not a new binomial counting identity. Paper
XXXIX supplies the event-anchored interpretation [@chenPaper39v1]; the
definitions and combinatorial proofs needed here are given below.

## 2. Circular Actions and Actual Placement Control

### 2.1. Executions, registration and summaries

Fix $n\ge2$ and distinguish the atom set $\Omega$ from the position set
$Q$, although both are identified with $\mathbb Z/n\mathbb Z$. A placed
partition $P$ assigns a nonempty atom block to each occupied position.
Its assigned blocks are disjoint and have union $\Omega$. Empty positions
are holes. Its rank is the number of occupied positions. The singleton
seed is $P_{\varnothing}(q)=\{q\}$ for every $q\in Q$.

The letters act on positions by

$$
p(q)=q+1\pmod n,\qquad
d(1)=0,\qquad d(q)=q\quad(q\ne1).
\tag{2.1}
$$

For $a\in\{p,d\}$ the partition update is pushforward union:

$$
(a_\#P)(y)=\bigcup_{q:\,a(q)=y}P(q),
\tag{2.2}
$$

omitting empty values. A fusion occurs exactly when $d$ is applied with
both ports $0,1$ occupied. Every such event has two nonempty disjoint
parents, in the ordered ports $(0,1)$, and target $0$. A chronological
word $h=a_1\cdots a_t$ executes $a_1$ first; its current partition is
$P_h$. All negative rotation exponents below mean their nonnegative
representatives $[j]_n\in\{0,\ldots,n-1\}$, not additional letters.

Fix $F=\{0,1\}\subseteq\Omega$. Registration requires an actual fusion
whose fresh block is exactly $F$. A history is used only at or after such
registration. The origin snapshot of that event is

$$
o_F=(d,(0,U_0),(1,V_0),0),\qquad U_0\sqcup V_0=F.
\tag{2.3}
$$

After registration there is a unique current block containing $F$, called
its carrier. Record, in order, every later fusion involving that carrier,
and no unrelated fusion. We use the full port-ordered record

$$
\rho=(d,(0,U),(1,V),0,U\cup V).
\tag{2.4}
$$

Exactly one of $U,V$ contains $F$, so the record also determines which
parent was the carrier. This is equivalent to recording the carrier
first together with its port and the partner's port. Let $A_F(h)$ be
this selected chain, possibly empty. Define

$$
\Gamma(h,F)=(P_h,F,o_F,A_F(h)),\qquad
S_n=\{\Gamma(h,F):h\text{ registers }F\},\qquad s_n=|S_n|.
\tag{2.5}
$$

Equality is literal equality of all four components. There are no
timestamps, unrelated-event records or execution words in a summary.
Coalescence prevents $F$ from being freshly created a second time.

### 2.2. Endpoint maps, histories, chains and summaries

These are different objects, even though all arise from one word $h$:

- The **endpoint transformation** $T_h:Q\to Q$ records the final image of
  each starting position. From the fixed singleton seed it is equivalent
  to the current placed partition $P_h$.
- The **full execution word** $h$ records every chronological $p$ and $d$,
  including rotations and nonfusion steps.
- The **full fusion (merger) history** records every actual two-parent fusion,
  including events unrelated to $F$, but omits nonfusion letters.
- The **selected absorption chain** $A_F(h)$ records only the ordered
  post-registration fusions involving the carrier of $F$.
- The **registered summary** $\Gamma(h,F)$ retains the current placement,
  fixed $F$, its origin and its selected chain, as in (2.5).

For example, take $n=4$ and $F=\{0,1\}$. The chronological words
$h_1=dpdpd$ and $h_2=dppdpdpd$ both register $F$ at their first $d$.
Both send every starting position to $0$, so they have the same endpoint
transformation and the same final placement $\Omega$ at $0$. But $h_1$
first absorbs $\{3\}$ and then $\{2\}$ into the carrier: at both selected
fusions the carrier is at port $1$. In $h_2$, an unrelated fusion first
assembles $\{2,3\}$; the sole selected fusion then absorbs this partner
with the carrier at port $0$. Thus $A_F(h_1)\ne A_F(h_2)$ and
$\Gamma(h_1,F)\ne\Gamma(h_2,F)$, despite equality of endpoint maps.
The count below concerns these registered summaries. It does not assert
that they are minimal predictive states for an unspecified future task.

### 2.3. Source order and nonfusion moves

An atom arc is a nonempty consecutive subset of the positive source
circle, including $\Omega$ as the full arc. The occupied block order is
the positive cyclic order of packets read at their current positions.

**Lemma 2.1 (source-order preservation).** Every generated packet is an
atom arc. Its occupied block order is a cyclic coarsening of the original
source order.

**Proof.** The assertion holds at the singleton seed. A $p$ step rotates
the occupied order. A $d$ step either fixes all occupied positions, moves
the packet at $1$ into the empty position $0$, or merges the packets at
$0,1$. In the last case these are consecutive occupied blocks, so their
union is an arc and the cyclic order is coarsened by that one merge.
This proves the assertion by induction, also when only two blocks remain.
$\square$

For $j\in Q$ consider the actual chronological word

$$
E_j=p^{[-j]_n}\,d\,p^{[j]_n}.
\tag{2.6}
$$

At the ends of this word, its position map sends $j+1$ to $j$ and fixes
all other positions. If $j$ is a hole and a packet occupies $j+1$, the
whole word produces no fusion: its rotation prefix is injective; its
middle $d$ sees a hole at $0$ and the packet at $1$; and its rotation
suffix is injective. Thus it moves that packet one position backward
without changing any event record. Intermediate occupancy of both kernel
ports during a rotation is harmless, since the executed letter is then
$p$, not $d$.

**Lemma 2.2 (placement control).** Two placements of the same distinct
blocks in the same oriented cyclic block order are connected by an actual
$p,d$ word with no fusion at any step.

**Proof.** For one block a rotation suffices. Otherwise fix the common
cyclic block order $B_0,\ldots,B_{r-1}$. Let $h_i$ count the holes after
$B_i$ and before $B_{i+1}$, with indices modulo $r$. Their sum is $n-r$.
If $h_i>0$, apply (2.6) at the hole immediately before the currently
placed $B_{i+1}$. The change in gaps is exactly

$$
h\longmapsto h-e_i+e_{i+1}.
\tag{2.7}
$$

Let $g$ be the desired gap vector. If $h\ne g$, choose an excess index
$e$ and a deficit index $f$. Route one hole along the forward simple path
from $e$ to $f$ on the gap cycle. The first donor has a hole; each later
donor has just received one. Hence every move is legal at its actual
predecessor. Intermediate coordinates have zero net change, and the route
changes $h$ to $h-e_e+e_f$. Consequently
$\sum_i(h_i-g_i)_+$ decreases by one. Finitely many such routes give $g$.
A rotation aligning $B_0$ then aligns every block. If $r=n$, all gaps
are already zero and only the rotation is required. Every local word
acts on the preceding concrete partition. $\square$

**Corollary 2.3 (prescribed consecutive merge).** Any consecutive ordered
pair of blocks can be placed at ports $0,1$ in that order and merged by
one further $d$. With two blocks either port assignment is possible.

**Proof.** Choose a target placement putting that pair at $0,1$ and the
other blocks consecutively at $2,\ldots,r-1$, respecting the cyclic
order. Apply Lemma 2.2, then $d$. For two blocks both assignments have
the same cyclic order. $\square$

In particular, a consecutive group of noncarrier singleton atoms can be
assembled into one specified partner block. No atom outside that group
need be merged, and the selected carrier need not participate.

## 3. A Canonical Encoding of Complete Absorption Chains

Let $\mathcal C_n$ be the set of chains $A_F(h)$ occurring in (2.5),
including the empty chain, and put $m=n-2$. The atoms outside $F$ start
in the positive linear source order

$$
B_0=(2,3,\ldots,n-1).
\tag{3.1}
$$

For a ternary word $v\in\{0,L,R\}^{\{1,\ldots,m\}}$, let
$b_1<\cdots<b_t$ be its nonzero positions and let their signs be
$\epsilon_1,\ldots,\epsilon_t$. Set $b_0=0$ and
$\ell_i=b_i-b_{i-1}$. Decode from the initial carrier $C_0=F$ and list
$B_0$. At step $i$, take a partner of size $\ell_i$ from the first
remaining atoms if $\epsilon_i=R$, and from the last remaining atoms if
$\epsilon_i=L$. Delete that partner from the list and add it to the
carrier. For $R$ put the old carrier at port $0$ and the partner at
port $1$; for $L$ reverse these roles. Record (2.4). Denote the chain
obtained by $D_n(v)$.

The word positions label cumulative absorbed sizes, not particular atoms.
If the last partner is the entire complement, its $L$ and $R$ records
remain different because their parent-to-port bindings differ.

**Theorem 3.1 (chain bijection).** For every $n\ge2$, decoding is a
bijection

$$
D_n:\{0,L,R\}^{n-2}\overset{\sim}{\longrightarrow}\mathcal C_n.
\tag{3.2}
$$

Thus

$$
|\mathcal C_n|=3^{n-2},\qquad
|\{A\in\mathcal C_n:|A|=t\}|=2^t\binom{n-2}{t}.
\tag{3.3}
$$

**Proof.** Until its carrier is $\Omega$, that carrier is an arc
containing $F$ by Lemma 2.1, and its remaining complement is a linear
interval of (3.1). Each selected absorption joins an adjacent packet.
The partner is therefore a prefix or a suffix of that remaining interval.
The carrier's port fixes the choice: port $0$ gives $R$ and port $1$
gives $L$. This port also distinguishes the choices when the partner is
the entire complement.

From an actual chain recover

$$
b_i=|C_i|-2,\qquad
\epsilon_i=
\begin{cases}
R,&\text{the previous carrier occupies port }0,\\
L,&\text{the previous carrier occupies port }1.
\end{cases}
\tag{3.4}
$$

The $b_i$ strictly increase in $\{1,\ldots,m\}$, since every partner
is nonempty and disjoint from its carrier. Insert these signs at these
checkpoints and zeros elsewhere. Decoding recovers each actual parent
block and its port; encoding a decoded parameter recovers the parameter.
This proves both inverse identities for all occurring chains.

To realize any parameter, first execute $d$ at the seed, creating and
registering $F$ while leaving all outside atoms singleton. For each
prescribed partner, assemble exactly that consecutive group by Corollary
2.3, without merging the carrier or any unconsumed atom. Use Lemma 2.2
to place carrier and partner at the prescribed ports, and execute $d$.
Continue from that actual successor. This realizes the decoded chain
and leaves every unconsumed atom singleton. The same argument includes
the empty parameter and $n=2$. Hence the inverse identities apply to
the whole parameter set, proving (3.2). Choosing the $t$ nonzero
positions and their signs proves (3.3). $\square$

It will be useful to refine by the last checkpoint $b$. The empty chain
has $b=0$. The number of chains with last checkpoint $b$ and length $t$ is

$$
d_m(b,t)=
\begin{cases}
1,&b=t=0,\\
2^t\binom{b-1}{t-1},&1\le t\le b\le m,\\
0,&\text{otherwise}.
\end{cases}
\tag{3.5}
$$

Summing over $t$ gives $d_m(0)=1$ and
$d_m(b)=2\cdot3^{b-1}$ for $1\le b\le m$: the symbol at $b$ is nonzero,
earlier symbols are arbitrary, and later symbols are zero.

## 4. Exact Fibers of the Registered Summary

**Lemma 4.1 (forced origin).** If $n\ge3$, every registration of $F$
has origin

$$
o_F=(d,(0,\{0\}),(1,\{1\}),0).
\tag{4.1}
$$

**Proof.** The two parents of a freshly created two-atom block must be
its singletons. At least one outside packet is still present, so the
pre-fusion state has at least three blocks. Source order makes $\{0\}$
immediately precede $\{1\}$, not conversely. Their occupied adjacent
ports must have this positive order. For $n=2$ there is no outside block;
both assignments occur, by the histories $d$ and $pd$. $\square$

Fix $A\in\mathcal C_n$, write $C(A)$ for its last carrier, or $F$ if
$A$ is empty, and put $k=n-|C(A)|$. Its summary fiber is

$$
\mathcal W_n(A)=\{\Gamma(h,F):A_F(h)=A\},\qquad
w_n(A)=|\mathcal W_n(A)|.
\tag{4.2}
$$

Write $w_n(A;r)$ for its part of current rank $r$.

**Theorem 4.2 (complete summary fibers).** For $n\ge3$, the fiber
$\mathcal W_n(A)$ consists exactly of the placed partitions containing
$C(A)$ as a block, with the other blocks an interval partition of its
linear source complement and placed in the source cyclic order. Its
origin is (4.1), and its chain is $A$. In particular,

$$
w_n(A)=n\binom{n+k-2}{k}.
\tag{4.3}
$$

More precisely,

$$
w_n(A;r)=
\begin{cases}
n,&k=0,\ r=1,\\
r\binom{k-1}{r-2}\binom nr,&k\ge1,\ 2\le r\le k+1,\\
0,&\text{otherwise}.
\end{cases}
\tag{4.4}
$$

**Proof.** A further carrier fusion would add a selected record, so the
carrier in a summary with chain $A$ is exactly $C(A)$. Lemma 2.1 makes
each other block an interval of its complementary source path, with the
required placement order. The origin is fixed by Lemma 4.1. Hence the
placed partition determines the summary once $A$ is fixed.

Conversely, the construction in Theorem 3.1 reaches $C(A)$ with all
unconsumed atoms singleton. For any partition of its source complement
into consecutive blocks, assemble precisely those blocks by Corollary
2.3. None of these fusions involves the carrier. Apply Lemma 2.2 to
reach the desired placement without fusion. Thus the resulting actual
continuation preserves both the origin and the complete selected chain.
It realizes the specified summary, not just its separate components.

For an explicit count when $k\ge1$, write the positive linear complement
of $C(A)$ as $(a_1,\ldots,a_k)$. If there are $t$ outside blocks, set
$r=t+1$ and use parameters

$$
\begin{gathered}
D\subseteq\{1,\ldots,k-1\},\quad |D|=t-1,\\
Z\subseteq Q,\quad |Z|=r,\quad q\in Z.
\end{gathered}
\tag{4.5}
$$

Cut the complement at $D$ into its ordered nonempty blocks
$I_1,\ldots,I_t$. List $Z$ clockwise starting at $q$ as
$z_0=q,z_1,\ldots,z_t$. Place $C(A)$ at $q$ and $I_i$ at $z_i$.
This decodes a parameter to one summary in the fiber.

In the reverse direction recover $Z$ as the occupied set and $q$ as
the unique carrier position. Read the outside packets clockwise after
$q$ as $I_1,\ldots,I_t$, and recover

$$
D=\{|I_1|,\ |I_1|+|I_2|,\ldots,|I_1|+\cdots+|I_{t-1}|\}.
\tag{4.6}
$$

Source order makes these exactly the consecutive cuts of the fixed
complement. The two constructions are inverse: the support, carrier
coordinate and consecutive blocks are all recovered. Consequently the
rank-$r$ count is $r\binom{k-1}{t-1}\binom nr$. There is no factorial
factor, because block order is fixed, and no division by $r$, because
the carrier position distinguishes the phase. For $k=0$ there is one
packet with $n$ possible positions.

For $k\ge1$, sum the rank counts using ordinary binomial convolution:

$$
\begin{aligned}
w_n(A)
&=n\sum_{t=1}^{k}\binom{k-1}{t-1}\binom{n-1}{t}\\
&=n\binom{n+k-2}{n-2}
=n\binom{n+k-2}{k}.
\end{aligned}
\tag{4.7}
$$

The same final expression gives $n$ when $k=0$. $\square$

The identity of the fiber depends on the whole chain, but its size
depends only on the final carrier size. It does not depend just on chain
length. For example, when $n=4$ the codes $R0$ and $0R$ both have one
selected event. Their carriers have sizes $3$ and $4$, so their summary
weights are $12$ and $4$, respectively.

For $n=2$ the only chain is empty. Its two origins from Lemma 4.1 and
two current positions give

$$
s_2=w_2(())=4.
\tag{4.8}
$$

This exception is essential: applying (4.3) to the full two-atom source
would incorrectly remove one of its two possible origins.

## 5. Total Count and Exponential Growth

**Theorem 5.1 (exact total).** For $n\ge3$ and $m=n-2$,

$$
\begin{aligned}
s_n
&=\sum_{A\in\mathcal C_n}w_n(A)\\
&=n\left[\binom{2m}{m}
+2\sum_{b=1}^{m}3^{b-1}\binom{2m-b}{m-b}\right].
\end{aligned}
\tag{5.1}
$$

**Proof.** The fibers in (4.2) are disjoint and cover $S_n$. The empty
chain leaves $m$ outside atoms and has weight $n\binom{2m}{m}$. A
nonempty chain with last checkpoint $b$ leaves $k=m-b$ outside atoms.
There are $2\cdot3^{b-1}$ such chains by (3.5), each of weight
$n\binom{2m-b}{m-b}$ by (4.3). Summing proves the formula. $\square$

For rank $r$ and chain length $t$, the same disjoint decomposition gives
the refined count

$$
b_n(r,t)=\sum_{b=0}^{m}d_m(b,t)\,w_{n,m-b}(r),
\tag{5.2}
$$

where $w_{n,k}(r)$ denotes the right side of (4.4). The exceptional
two-atom count is $b_2(1,0)=4$.

**Corollary 5.2 (growth with an explicit error).** For $n\ge3$,

$$
\left|\frac{s_n}{n(9/2)^{n-2}}-1\right|
\le(8/9)^{n-2},\qquad
\lim_{n\to\infty}s_n^{1/n}=\frac92.
\tag{5.3}
$$

**Proof.** Put $B_m=\binom{2m}{m}$ and $Z_m=s_n/n$. Reindex (5.1) by
$k=m-b$ to obtain

$$
Z_m=B_m+\frac23\,3^m
\sum_{k=0}^{m-1}\binom{m+k}{k}3^{-k}.
\tag{5.4}
$$

Multiplying $m+1$ absolutely convergent geometric series gives

$$
\sum_{k=0}^{\infty}\binom{m+k}{k}3^{-k}=(3/2)^{m+1}.
\tag{5.5}
$$

Let $T_m$ be this series' tail starting at $k=m$. Its first term is
$a_m=3^{-m}B_m$, and for $k\ge m$ the ratio of successive terms is

$$
\frac{m+k+1}{3(k+1)}\le\frac23.
\tag{5.6}
$$

Thus $a_m\le T_m\le3a_m$. Subtracting this tail from (5.5) in (5.4)
gives

$$
\begin{aligned}
Z_m&=(9/2)^m+E_m,\\
E_m&=B_m-\frac23\,3^mT_m,\qquad
-B_m\le E_m\le B_m/3.
\end{aligned}
\tag{5.7}
$$

In particular $|E_m|\le B_m\le4^m$, proving the relative bound in
(5.3). Taking $n$th roots with $m=n-2$ now gives the limit, since
$n^{1/n}\to1$ and the relative error tends to zero. $\square$

These formulas count all summaries in the declared family, not an
extrapolation from observed values. For orientation, the first few values
are

| $n$ | $|\mathcal C_n|$ | $s_n$ |
|---|---:|---:|
| 2 | 1 | 4 |
| 3 | 3 | 12 |
| 4 | 9 | 72 |
| 5 | 27 | 410 |
| 6 | 81 | 2,244 |
| 7 | 243 | 11,928 |

## 6. Computational Controls and Scope

An independently implemented breadth-first search starts from the singleton
seed and applies the literal $p,d$ updates to the placed partition, origin
and selected absorption chain. Unregistered states are retained until an
actual fusion first creates $F$. For $2\le n\le7$, the complete chain and
registered-summary counts are those in the table above. Each observed
fixed-chain fiber matches (4.3), with the two-origin exception at $n=2$.
This is a bounded consistency check, not a proof of the all-$n$
classification; no result in Sections 3--5 uses it as a premise.

The scope fixes both the action and the registration. The off-kernel
identity in (2.1), the identity singleton seed, and the actual fresh block
$F=\{0,1\}$ are part of every theorem. Counting merely a tracked pair
inside a larger registered block would be a different problem. Nor do
the formulas assert counts for arbitrary defects, sparse seeds, other
registered block sizes or budgeted histories.

The number $s_n$ is the size of this particular registered-summary set. Its
growth does not prove a minimal representation theorem or a time or
space lower bound for every consumer-specific checker. Such a checker
may need fewer reads than the whole summary. Actual word constructions
here establish reachability without controlling word length; they are
not shortest-word classifications or global reset estimates.

## 7. Conclusion

For this deterministic circular adjacent-collapse action, the selected
event history has a canonical finite encoding even though executions
have no length bound.
Checkpoint sizes and port roles determine the entire absorption chain.
Actual nonfusion placement control then makes every allowed partition
in its fiber attainable along the same selected history. The exact
summary count and growth rate follow from this joint classification.

The distinction between a chain and its current-placement fiber is
essential. Chain length alone determines neither the last carrier size
nor the number of summaries. Keeping those two levels separate turns
the enumeration into a disjoint-fiber calculation with explicit inverse
maps and generating executions.

## References
