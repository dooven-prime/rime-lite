# Fusion Elimination and Exact History-Cost Extrema on Stacked Rings

**WuJun Chen**

Independent Researcher | November 20, 2026

**Paper XLVII | Version 1.0**

*RIME Paper XLVII, version 1.0. This paper determines complete-history cost
extrema for one-block and all-upper observations in a guarded two-ring system.*

## Abstract

We study a guarded packet system on two directed rings, with independent
rotations, adjacent fusion and a one-way transfer port. An observation
retains the complete ordered fusion and whole-packet transfer log together
with the literal endpoint. Its total premium is the minimum realizing word
length minus the minimum cost of the same unordered partition. For $n\ge3$,
the maximum premium in the entire one-block fibre and the maximum over all
observations ending wholly in the upper layer both equal
$5\binom n2+K_n-n+2$, where $K_n$ is an attained auxiliary
singleton-extraction maximum. The all-upper result permits arbitrary packet
masses, ordered fusion forests and legal event interleavings. A rotating
reservation cursor controls the upper replay; an erasure-shadow simulation
eliminates each lower fusion at cost at most $2n-1$. For singleton transfers,
a cyclic gap moment and a joint structural defect retain explicit savings
in the same physical replay. The cyclic realization and quadratic replay
foundations are proved here. Any larger global premium must come from a
multiblock endpoint with at least one lower-layer survivor.

**Keywords:** fusion history; guarded packet system; circular order;
word length; simulation; observation fibre

## 1. Introduction

Prescribing a final partition and prescribing how it was assembled are
different optimization problems. A single packet may be formed cheaply
if its merger history is free. The same packet can require a much longer
word when every ordered merger, transfer and final physical coordinate is
specified. The difference is naturally measured within one observation
fibre: compare the largest minimum cost of a complete observation with
the minimum cost after forgetting to its unordered partition.

We consider the two-ring packet machine of Paper XLVI
[@chen2026stackedRings]. Positive rotations and adjacent fusions act on
each layer, and one guarded port transfers a whole lower packet to an
empty upper site. Here the target includes the complete effective log,
not only the endpoint. Silent routing is omitted from that log but paid
in the raw-word metric.

Let $\lambda_n(H,Q)$ be the minimum length realizing a complete log $H$
and literal placement $Q$, and let $\ell_n(\pi)$ be the minimum length
realizing an unordered partition $\pi$. Write

$$
 \Lambda_n^{\mathrm{part}}(\pi)
 =\max_{\operatorname{Part}(Q)=\pi}\lambda_n(H,Q),
 \qquad
 M_n(\pi)=\Lambda_n^{\mathrm{part}}(\pi)-\ell_n(\pi),
 \tag{1.1}
$$

where the maximum ranges over actual observations. Our central result is

$$
 \boxed{M_n(\mathbf1_n)=5\binom n2+K_n-n+2,\qquad n\ge3.}
 \tag{1.2}
$$

Here $\mathbf1_n=\{\Omega\}$, and $K_n$ is the maximum minimum cost
of extracting all lower singletons in a prescribed permutation. It is a
finite, attained optimization parameter.

There is a second exact extremum. Let $\mathcal U_n$ be all attainable
observations ending with every atom in the upper layer, and let
$\mathcal A_n\subseteq\mathcal U_n$ restrict transfers to singletons.
Across all terminal ranks,

$$
 \max_{(H,Q)\in\mathcal A_n}D_{\mathrm{tot}}(H,Q)
 =\max_{(H,Q)\in\mathcal U_n}D_{\mathrm{tot}}(H,Q)
 =M_n(\mathbf1_n).
 \tag{1.3}
$$

The same delayed observation attains all three quantities. The maxima in
(1.3) range over complete observations, each charged relative to its own
partition minimum; they are not the maxima at every fixed terminal rank.

The upper bound combines two constructions. A shared reservation cursor
replays the ordered upper fusion forest in chronological order, with a
telescoping payment for gap routing. An erasure-shadow simulation replaces
lower fusions by auxiliary extractions at bounded cost; the upper budget
released by having fewer transfers covers this charge.

The reverse inequality comes from a delayed family: all singleton
transfers occur first, followed by an ordered left-comb of upper fusions.
We prove its exact cost for each extraction permutation and terminal
phase. At the full one-block maximum, the retained defects force no lower
prefusion, a left-comb upper tree, a specified initial cursor position,
and an extraction order attaining $K_n$.

Section 3 proves the cyclic realization and quadratic replay foundations
used below. The all-upper extension couples cyclic gap moments, structural
defects and cursor phases to handle arbitrary transferred packets and legal
event interleavings. The residual global case has multiple terminal blocks
and lower-layer survivors.

### Relation to earlier work

Paper XLV gives joint fusion-log/endpoint realization and quadratic normal
forms on one ring [@chen2026fusionLog]. We use its fusion-free placement
bound and its exact all-right example. Paper XLVI studies reachability,
retention and selected endpoint costs on the present two-ring machine
[@chen2026stackedRings]. The new problem is the cost range of the complete
history observation over an entire fixed partition fibre. The upper
cursor and lower shadow constructions handle all transfer strata rather
than only a prescribed history family.

The lower-layer cyclic-order constraint is adjacent to the theory of
orientation-preserving transformations of finite circular orders; Levi and
Mitchell study rank and idempotent generation in that setting
[@leviMitchell2006]. Transformation-semigroup word length provides a related
but different metric. Cameron et al. take the arcs of a digraph as unit-cost defect-one
generators and minimize words expressing a terminal transformation
[@cameronEtAl2017, Section 1]. Here the five letters are fixed, rotations
have unit cost, and transfers have state-dependent guards. In addition,
the target retains the complete ordered effective log. The cyclic routing
arguments below supply execution witnesses for this observation contract.

Section 2 fixes the observation and cost conventions. Sections 3--6 establish
realization, the attaining family, and the two replay bounds. Sections 7--9
give the exact extrema and localize any larger global premium. Section 10
identifies the companion source; Appendix A proves the terminal routing bound.

## 2. The guarded machine and its observation fibres

Fix $n\ge2$, $\Omega=\{0,\ldots,n-1\}$ and
$C_n=\mathbb Z/n\mathbb Z$. Write $[x]_n$ for the representative in
$\{0,\ldots,n-1\}$. A literal placement is a function

$$
 P:\Omega\longrightarrow\{0,1\}\times C_n.
 \tag{2.1}
$$

The packet $P_\ell(q)$ is its fibre at layer $\ell$, site $q$; it may
be empty. Nonempty packets are disjoint and cover $\Omega$. The seed is
$P_{\mathrm{seed}}(a)=(0,a)$.

Words in $\Sigma=\{p_0,p_1,d_0,d_1,v\}$ are chronological: the leftmost
letter executes first. The action $p_\ell$ increases every site on its
layer by one. The action $d_\ell$ sends site 1 to site 0 and fixes all
other sites. It fuses the two port packets when both are nonempty, slides
the site-1 packet when site 0 is empty, and otherwise does nothing.
The letter $v$ is enabled precisely when $P_0(0)$ is nonempty and $P_1(0)$
is empty; it moves the entire lower port packet to upper site 0. Each
letter costs one. An illegal transfer makes the word undefined.

At a pre-step placement, an effective fusion emits the full record

$$
 F_\ell(U,V)=
 (d_\ell,(0,U),(1,V),0,U\cup V),
 \tag{2.2}
$$

with $U=P_\ell(0)$ and $V=P_\ell(1)$ nonempty. A successful transfer
emits $V(B)$, recording the whole packet $B$ and its move from lower
port 0 to upper port 0. Rotations and nonfusing defects emit nothing.
For a legal word $w$, let $H(w)$ be the chronological concatenation of
all emitted records and define

$$
 \Phi_n(w)=(H(w),\operatorname{run}(P_{\mathrm{seed}},w)).
 \tag{2.3}
$$

The observation contains no silent-letter positions or timestamps.
Parent order and all terminal coordinates remain literal.

Write $F_\ell(H)$ for the number of layer-$\ell$ fusions, $t=V(H)$
for the transfer count, and $r_\ell(Q)$ for the terminal layer ranks.
Packet conservation gives

$$
 F_0+t=n-r_0(Q),\qquad F_1=t-r_1(Q),\qquad
 F_0+F_1=n-r_0(Q)-r_1(Q).
 \tag{2.4}
$$

Every atom moves upward at most once, so $t\le n$. Consequently
$|H|\le2n-1$. There are only finitely many literal placements and event
records, hence finitely many attainable observations. Their shortest
costs and all maxima used below are attained.

For an attainable partition, define $\lambda_n$, $\ell_n$ and
$\Lambda_n^{\mathrm{part}}$ as in Section 1. Also put

$$
 D_{\mathrm{tot}}(H,Q)
   =\lambda_n(H,Q)-\ell_n(\operatorname{Part}(Q)).
 \tag{2.5}
$$

Every difference in this paper is an ordinary integer difference.
The inequality $\ell_n(\operatorname{Part}(Q))\le\lambda_n(H,Q)$
ensures that (2.5) is nonnegative.

### Lemma 2.1. The minimum within a partition fibre

For every attainable $\pi$,

$$
 \min_{\operatorname{Part}(Q)=\pi}\lambda_n(H,Q)=\ell_n(\pi).
 \tag{2.6}
$$

**Proof.** Each realizing word for a joint observation is also a witness
for its partition, giving one inequality. A word of length $\ell_n(\pi)$
has some complete observation $(H,Q)$ with that partition. Its joint
minimum is at most its length, giving the reverse inequality. $\square$

Thus the partition amplitude and the per-observation premium satisfy

$$
 M_n(\pi)=\max_{\operatorname{Part}(Q)=\pi}D_{\mathrm{tot}}(H,Q),
 \tag{2.7}
$$

where the maximum again ranges over attainable complete observations.
Thus $M_n(\pi)$ is the range of minimum joint costs within the partition
fibre. Write $J_n^{\mathrm{del}}$ for the delayed-family maximum defined in
Section 4; Theorem 7.2 identifies it with $M_n(\mathbf1_n)$.

## 3. Cyclic realizability and complete-history compression

For a placement $P$, let $\mathcal C_\ell(P)$ be the positive cyclic
word of its nonempty layer-$\ell$ packets, up to rotation. This retains
literal packet identities and their layer. Write $P\sim Q$ when both
layer cycles agree. A word is silent if its effective log is empty.

### Lemma 3.1. Silent preparation

Two placements on the same atom set are connected by a silent word if and
only if $P\sim Q$.

**Proof.** Rotations preserve each packet cycle. A silent defect either
does nothing or moves one packet into the preceding hole, passing no other
packet. This proves necessity.

For sufficiency, work on one layer. Empty layers require no action. A
one-packet layer is aligned by rotation, and a fully occupied layer with
the same cycle also differs only by rotation. Otherwise name its $r\ge2$
packets cyclically and let $g_i$ be the hole count after packet $i$.
Moving packet $i+1$ backward through one preceding hole changes
$(g_i,g_{i+1})$ to $(g_i-1,g_{i+1}+1)$. The localized chronological word
$p_\ell^{[-j]_n}d_\ell p_\ell^{[j]_n}$ realizes such a move from
site $j+1$ to the vacant site $j$, restoring every other site.
Circulate holes through the directed gap cycle to reach the target gap
vector; for example, gather them in one gap and then distribute them to
the required gaps in reverse order along the cycle. A final rotation
aligns one named packet, hence the entire layer. Repeat independently on
the other layer. Every intermediate defect is a slide, not a fusion.
$\square$

An abstract cyclic event has one of two forms. A fusion replaces two
distinct cyclic neighbors $(U,V)$ on its declared layer by $U\cup V$.
A transfer removes a named lower packet and inserts it in a chosen upper
cyclic gap, with upper rank strictly less than $n$ before insertion.
The empty upper cycle has its unique insertion choice. With two packets,
both ordered cyclic neighbor bindings are allowed and remain distinct
fusion records.

### Theorem 3.2. Joint log/endpoint criterion

For typed initial and final placements $P,Q$, a complete record list $H$
is realized by a legal word from $P$ to $Q$ if and only if there is a
cyclic event path with labels $H$ from $\mathcal C(P)$ to
$\mathcal C(Q)$.

**Proof.** A real event has exactly the stated effect on the packet
cycles, while silent intervals preserve them. This gives the forward
path. Conversely, fix one such path, including every transfer's insertion
choice. Before its next event, use Lemma 3.1 to prepare the current actual
placement with the required ordered parents at ports 0 and 1, or with
the transferred packet at lower 0 and its chosen upper gap containing
empty site 0. The rank condition supplies that vacancy. One actual letter
then emits the specified complete record. Its endpoint has the next
path cycle, so induction continues from this same representative.
After the last event, Lemma 3.1 reaches the requested literal $Q$.
$\square$

The path quantifier is essential: a transfer record names its packet,
but does not itself specify the upper insertion gap.

### Proposition 3.3. Quadratic complete-observation representatives

Every attainable singleton-seed observation $(H,Q)$ has a legal witness
$w'$ satisfying

$$
 |w'|\le4n(F_0+F_1)+(2n+1)t+h_n(r_0(Q))+h_n(r_1(Q))
       \le6n^2-2n-1,
 \tag{3.1}
$$

where $h_n(0)=0$ and
$h_n(r)=(3n-r)(r-1)+(n-1)$ for $1\le r\le n$.
Any realizing input word $w$ therefore has an equal-observation replacement
of length at most $\min\{|w|,6n^2-2n-1\}$.

**Proof.** Annotate transfers by chronological occurrence labels. An upper
fusion joins its two ordered parent trees. Order the terminal roots by
their physical cycle in $Q$, expand their ordered leaf words, and reserve
consecutive upper sites for those transfer occurrences. There are at most
$n$ leaves. At each event boundary, put a live upper packet at its subtree's
first reserved site. Its internal leaf sites and every future leaf site
are vacant. This invariant follows backward from the same actual ordered
forest: reversing a fusion splits its result into its recorded parents,
and reversing a transfer removes its leaf.

An ordered neighbor fusion can slide its right packet through the
intervening holes, fuse it with the left, and restore the phase of all
other packets in at most $4n$ letters. Indeed, for $f>0$ holes the
single-ring batch costs at most $2n+f$, while the phase-restored final
fusion costs at most $n+1$; use $f\le n-2$. For $f=0$ that final
fusion alone suffices. The two-packet case uses the recorded direction.
For a transfer from lower site $q$ to vacant reserved
upper site $a$, use

$$
 p_0^{[-q]_n}p_1^{[-a]_n}v p_1^a p_0^q.
 \tag{3.2}
$$

The guard succeeds, and all other literal sites are restored. The cost
is at most $2n+1$. Lower fusions preserve the residual lower packet cycle;
upper fusions preserve the reservation invariant. Induction therefore
replays all events continuously. The terminal layer cycles agree with
$Q$. The batched single-ring placement bound of Paper XLV, Proposition 3.3
[@chen2026fusionLog], costs at most $h_n(r)$ on each nonempty layer and
fixes the other layer. For $n=2$ the same bound follows directly by rotation.
This proves the first inequality, including empty and rank-one layers.

Put $r=r_0+r_1\ge1$. For each nonempty layer,
$h_n(r_i)\le4n(r_i-1)+(n-1)$, and hence their sum is at most
$4n(r-1)+(n-1)$, whether one or both layers are nonempty. Now use
$F_0+F_1=n-r$ and $t\le n$ in (3.1). Finally retain the input word
when it is shorter than the constructed representative. $\square$

## 4. Extraction cost and an exact attaining family

### 4.1. The independent lower problem

A lower configuration assigns an atom a site or absence. A packed lower
path may rotate, slide into an empty port, fuse the two nonempty port
packets, or extract the whole packet at port 0. The first three operations
cost one; extraction costs zero. Its effective log $h$ records all
ordered lower fusions and all whole-packet extractions. Call $h$ fully
extracting feasible when such a path goes from the singleton seed to the
empty configuration. Its attained minimum is $\mu_n(h)$.

When fusions are excluded, an extraction order $z$ is a permutation of
$\Omega$. Write $\kappa_n(z)$ for its minimum and

$$
 K_n=\max_{z\in\operatorname{Sym}(\Omega)}\kappa_n(z).
 \tag{4.1}
$$

Every such order is feasible: rotate its next live singleton to port 0
and extract it. Thus $K_n$ exists and is attained. Zero-cost extraction
is only auxiliary accounting; the real transfer letter will be paid once
by the upper construction.

### Lemma 4.1. A triangular extraction lower bound

For $n\ge2$, $K_n\ge\binom n2$.

**Proof.** Read the nonempty lower packets in increasing physical site
order, starting at port 0 and skipping holes. A silent slide leaves this
linear list unchanged. A positive rotation either leaves it unchanged or
moves its last entry to the front. If the list has $r\ge2$ entries,
bringing its second entry to the extraction port therefore needs at least
$r-1$ such unit list turns, and hence at least $r-1$ preparation letters.
Extra full turns cannot reduce the bound. After that extraction, a list
$(x,y,\mathrm{tail})$ becomes $(\mathrm{tail},x)$.

Specify the extraction permutation recursively by always choosing that
second entry, then continuing from the resulting list. Starting from
$(0,1,\ldots,n-1)$, the successive debts are $n-1,n-2,\ldots,1$.
Their sum is $\binom n2$, proving the bound for one permutation and hence
for $K_n$. $\square$

This uses the second-live, or step-two Josephus, order only as a lower-bound
witness. No assertion that it maximizes $\kappa_n$ is needed.

### Lemma 4.2. The one-block partition minimum

For $n\ge2$,

$$
 \ell_n(\mathbf1_n)=2n-3.
 \tag{4.2}
$$

**Proof.** The lower word $d_0(p_0d_0)^{n-2}$ forms one packet at lower
site 0 and has length $2n-3$.

For the lower bound, let $R_0$ count lower rotations and $N_0$ nonfusing
lower defects in any one-block realization. When $n\ge3$, atom 2 must
either participate in a lower merger or leave the lower layer. Before
its first such service, any movement of it other than rotation would
already require its presence at port 1. Reaching either active port from
site 2 therefore requires at least $n-2$ lower rotations before the first
service or such a slide. In particular $R_0+N_0\ge n-2$.
The lower packet balance requires $F_0+t=n-r_0(Q)\ge n-1$ further
productive letters, disjoint from those nonfusing preparations. Thus
$|w|\ge(R_0+N_0)+(F_0+t)\ge2n-3$. For $n=2$ the seed is not a
one-block placement, so at least one letter is required. $\square$

### 4.2. Delayed singleton loading and the ordered chain

For a permutation $z=(z_0,\ldots,z_{n-1})$, set
$C_i=\{z_0,\ldots,z_i\}$ and prescribe

$$
 H_z^{\mathrm{del}}
 =V(\{z_0\})\cdots V(\{z_{n-1}\})
  F_1(\{z_0\},\{z_1\})F_1(C_1,\{z_2\})\cdots
  F_1(C_{n-2},\{z_{n-1}\}).
 \tag{4.3}
$$

Let $Q_q$ put the full packet at upper site $q\in\{0,\ldots,n-1\}$.

### Theorem 4.3. Exact delayed-chain cost

For $n\ge3$, every permutation $z$ and every $q$,

$$
 \lambda_n(H_z^{\mathrm{del}},Q_q)
   =\kappa_n(z)+5\binom n2+q.
 \tag{4.4}
$$

**Proof.** First construct a witness. Take a minimum auxiliary extraction
path for $z$. At each extraction marker execute $v p_1^{n-1}$. After
$i$ arrivals they occupy consecutive upper sites $n-i,\ldots,n-1$
in their arrival order, so port 0 is empty until the next arrival.
All transfers are guarded. The loading cost is $\kappa_n(z)+n^2$;
after the last upper rotation, $z_i$ is at site $i$.

The one-ring all-right core of Paper XLV, Section 6
[@chen2026fusionLog], realizes the specified ordered chain from this
packed placement, ending at site 0 with length $3\binom n2-n$.
Its atom names are reindexed by $z$ and its letters act on the upper layer.
Appending $p_1^q$ gives cost $\kappa_n(z)+5\binom n2+q$.

For the reverse inequality, split any realizing word immediately before
its first effective upper fusion. The upper layer at this cut is full.
Undoing the remaining ordered chain shows that its cycle is the transfer
order $z$. The first fusion places $z_0,z_1$ at ports 0,1; full occupation
therefore fixes $z_i$ at site $i$ for every $i$.

We next prove that the loading prefix pays at least $n(n-1)$ upper
rotations. All upper packets remain singleton before the cut, so they
can be tracked individually through the actual silent steps.

**Lift-window invariant.** After $k\ge1$ arrivals, give $z_i$ a current
integer lift $x_i$ and a fixed birth lift $\beta_i$, for $0\le i<k$.
The lift $x_i$ represents its actual upper site modulo $n$. We maintain

$$
 \begin{gathered}
 \beta_i\in n\mathbb Z,\qquad x_i\ge\beta_i,\qquad \beta_0=0,\\
 x_0\le x_{k-1}<x_0+n,\qquad
 \beta_{i+1}\ge\beta_i+n\quad(0\le i<k-1).
 \end{gathered}
$$

The window compares the first and latest arrivals in the same integer
frame; their physical residues alone would not determine that frame.

**Establishment.** At the first transfer set $x_0=\beta_0=0$.
The invariant is immediate. Subsequent upper rotations add one to every
live lift. A silent upper defect applies the nondecreasing map
$x\mapsto x-\mathbf1_{[x]_n=1}$; all lower actions leave these lifts
unchanged.

**Preservation.** Rotations preserve the window. A silent defect could
increase its width from $n-1$ to $n$ only if the first lift had residue
1 and the last residue 0. For distinct packets this would place two
occupied packets at the fusion ports, making that defect an effective
fusion. Such an event is excluded before the chosen cut. For $k=1$
both endpoints are the same tracked packet. Also no defect lowers $x_i$
below its birth multiple: it cannot decrement at $x_i=\beta_i$, and
otherwise subtracting one leaves $x_i\ge\beta_i$.

At the next transfer, choose $\beta_k$ as the multiple of $n$ immediately
ahead of the previous latest lift $x_{k-1}$. Receiver vacancy gives

$$
 x_{k-1}<\beta_k<x_{k-1}+n.
$$

The required insertion gap also gives $\beta_k<x_0+n$. To see this,
undo the prescribed future chain and later arrivals: after this birth
the upper cycle must be $(z_0,\ldots,z_k)$. Since $z_k$ is inserted
at physical site 0, the literal old list just before birth is
$(z_0,\ldots,z_{k-1})$, with all its sites nonzero. In particular
$0<[x_0]_n\le[x_{k-1}]_n$. Together with the old window, this says
the two endpoint lifts cross no period boundary between their residues.
Their next multiple of $n$ consequently lies strictly below $x_0+n$.
Set $x_k=\beta_k$. The new window holds, and
$\beta_k>x_{k-1}\ge\beta_{k-1}$ implies
$\beta_k\ge\beta_{k-1}+n$ because both births are multiples of $n$.
This completes the invariant induction, including every intervening
silent slide.

**Rotation charge at the cut.** The birth chain gives
$\beta_{n-1}\ge n(n-1)$. The literal packed placement already recovered
at the cut has first site 0 and last site $n-1$. The window therefore
forces $x_{n-1}=x_0+n-1$. Since $x_{n-1}\ge\beta_{n-1}$, we have
$x_0\ge(n-1)^2=n(n-2)+1$. The lift $x_0$ is a multiple of $n$ at
this cut, hence $x_0\ge n(n-1)$. Starting from its birth value zero,
$x_0$ increases only on upper rotations and decreases on slides hitting
that packet. Thus the number of upper rotations in the loading prefix
is at least $x_0\ge n(n-1)$, regardless of its silent slides.

Projecting all lower letters and replacing transfers by zero-cost deletions
gives a singleton extraction path of order $z$. Thus the lower letters
cost at least $\kappa_n(z)$. The $n$ transfer letters are paid separately.
Finally the upper-letter suffix, beginning with its first fusion, is a
one-ring all-right realization from the packed seed to phase $q$. Its
length is at least $3\binom n2-n+q$: append $n-1-q$ rotations and
apply the exact all-right bound at phase $n-1$ in Paper XLV, Theorem 6.4.
These are disjoint charges in the same raw word. Their sum is the right
side of (4.4). $\square$

Define $J_n^{\mathrm{del}}$ as the maximum total premium in this delayed
family. Equations (4.2)--(4.4), a permutation attaining $K_n$, and phase
$q=n-1$ give

$$
 J_n^{\mathrm{del}}=5\binom n2+K_n-n+2,
 \tag{4.5}
$$

with an actual attaining observation. It remains to bound every other
one-block history by this same value.

## 5. A shared cursor for arbitrary upper fusion trees

Fix an actual one-block observation with $2\le t\le n$ transfers.
Its final packet is upper by (2.4). Label the transfer occurrences
chronologically by $0,\ldots,t-1$. The original ordered upper fusions
form a binary tree $T$ whose leaves are those occurrences. Leaf size below
counts transfer occurrences, not atoms; a leaf may be a prefused packet.

### Lemma 5.1. Ordered reservation intervals

Let $\omega$ be the ordered leaf word of $T$, indexed by
$0,\ldots,t-1$. At every event prefix, each live upper subtree has a
consecutive interval of $\omega$. Distinct live intervals are disjoint.
If the next fusion has ordered children $A,B$, with first indices $a,b$
and $u=|A|$, then $b=a+u$.

**Proof.** Reverse the actual upper event sequence from its root. A
reversed fusion replaces a tree by its recorded ordered children; a
reversed transfer removes its leaf. Silent and lower events preserve the
upper cycle. At every prefix the expansion of the current forest is the
restriction of the final ordered expansion to arrived leaves, up to
cyclic rotation. Each current subtree is an interval of the final tree
word. The children of one node have consecutive intervals in their given
order. This also treats the last two packets: their ordered record fixes
which child comes first. $\square$

Reserve site $j$ for leaf index $j$. For an internal node $(A,B)$ define
its gap debt $|A|-1$ and its defect $|A|(|B|-1)$. Set

$$
 \mathscr D(T)=\sum_{(A,B)}(|A|-1),\qquad
 E(T)=\sum_{(A,B)}|A|(|B|-1).
 \tag{5.1}
$$

### Lemma 5.2. Debt and tree defect

For a tree with $t$ leaves,

$$
 \mathscr D(T)+E(T)=\binom{t-1}{2}.
 \tag{5.2}
$$

Moreover $E(T)=0$ exactly when every internal node's right child is a
single leaf, that is, when $T$ is an ordered left-comb.

**Proof.** At a node with child sizes $u,v$, the new debt plus defect is
$(u-1)+u(v-1)=uv-1$. Adding the inductive child identities gives
$\binom{u-1}{2}+\binom{v-1}{2}+uv-1=\binom{u+v-1}{2}$.
All defect summands are nonnegative, and each vanishes exactly when its
right child has size one. $\square$

For example, the three-leaf left-comb has debt 1 and defect 0; the right-
comb has debt 0 and defect 1. The invariant measures the difference
without requiring a classification of larger tree shapes.

Maintain a cursor $c\in\{0,\ldots,n-1\}$. An upper subtree anchored
at first leaf index $a$ occupies physical site $[a-c]_n$. Its internal
reservation sites and all future leaf reservations are empty. Initially
take $c=j_0$, where $j_0$ is the position of chronological transfer leaf
0 in $\omega$. The upper layer is empty then, so this selects a frame,
not a free rotation of an occupied placement.

For a transfer whose position in $\omega$ is $j$, after its lower packet
is ready use

$$
 p_1^{[c-j]_n}v,\qquad c'=j.
 \tag{5.3}
$$

Its reserved receiver is genuinely empty. For a fusion of children anchored
at $a,b=a+u$, put $f=u-1$ and use

$$
 p_1^{[c-a-f]_n}d_1(p_1d_1)^f,\qquad c'=a.
 \tag{5.4}
$$

The first $f$ defects slide the right child through the internal vacant
reservations of the left child; the last defect gives exactly the
specified ordered fusion. For $f=0$ there is just the final fusion.
The result and all other live anchors satisfy the new cursor frame.

### Lemma 5.3. Cursor budget with retained defects

The upper letters and actual transfers in this construction have total
cost $C_{\mathrm{up}}$ satisfying

$$
 C_{\mathrm{up}}+E(T)+S(T)\le U_n(t),
 \qquad
 U_n(t)=2t-1+\binom{t-1}{2}+n(2t-3),
 \tag{5.5}
$$

where

$$
 S(T)=\begin{cases}0,&j_0=0,\\n-j_0,&j_0>0.\end{cases}
 \tag{5.6}
$$

The root finishes at upper site 0.

**Proof.** Each event has a threshold $x$: it is $j$ for a transfer
and $a+f$ for a fusion. Put $w=\mathbf1_{c<x}$. The exact payments are

$$
 \begin{aligned}
 |w_{\mathrm{tr}}|+c'-c&=1+nw,\\
 |w_{\mathrm{fus}}|+c'-c&=f+1+nw.
 \end{aligned}
 \tag{5.7}
$$

There are $2t-1$ events. The root has first index zero, so the last
cursor is zero. If $W$ is the number of winding events, summation gives

$$
 C_{\mathrm{up}}=2t-1+\mathscr D(T)+nW+j_0.
 \tag{5.8}
$$

At least two events do not wind. The first transfer has threshold equal
to its initial cursor. Also, consider the first fusion involving the
leftmost leaf of $T$. Until then that leaf is a singleton subtree; it is
the left child, so this fusion has threshold zero. If $j_0>0$, the birth
of that leftmost leaf is a third, distinct threshold-zero event. Therefore

$$
 W\le2t-3\quad(j_0=0),\qquad
 W\le2t-4\quad(j_0>0).
 \tag{5.9}
$$

Use (5.2) in (5.8). In the second case the saved winding costs $n$,
while the initial cursor adds only $j_0$, leaving $n-j_0$. This proves
(5.5). $\square$

### Theorem 5.4. Asynchronous packed replay

Let $h$ be the lower projection of the original log $H$, retaining lower
fusions and transfer packets. For an actual one-block observation with
$t\ge2$, there is one legal word with the same complete $H$ and the
same literal $Q$, of length at most

$$
 \mu_n(h)+U_n(t)+(n-1)-E(T)-S(T).
 \tag{5.10}
$$

In particular the same bound holds for $\lambda_n(H,Q)$.

**Proof.** Projection of the actual run supplies a feasible fully
extracting packed lower path for $h$. Choose a minimum such path. Follow
the original mixed event order, maintaining its residual lower path and
the actual cursor reservation on the same placement.

At a lower fusion, run the path's silent lower prefix and its next
effective defect; all upper coordinates are unchanged. At a transfer,
run its lower preparation to the named whole packet at port 0, then
execute (5.3). Vacancy follows from the upper reservation, and the
remaining lower configuration is exactly the auxiliary successor after
extraction. At an upper fusion use (5.4), leaving the entire residual
lower configuration unchanged. This gives an induction through all
effective events, not merely separate witnesses for the two projections.

Lower preparation costs $\mu_n(h)$. Actual transfers are paid in
$C_{\mathrm{up}}$, not in the zero-cost lower extraction markers. The
last event leaves the lower layer empty and the full upper packet at
site 0. Append at most $n-1$ upper rotations to reach the given literal
endpoint. Lemma 5.3 gives (5.10). $\square$

## 6. Lower fusion elimination by exact shadow simulation

Theorem 5.4 leaves one independent problem: bound the minimum preparation
cost of a fully extracting packed lower log, allowing prefusion.

### Lemma 6.1. Directed adjacency before the first fusion

Before the first effective lower fusion, the cyclic order of surviving
singletons is the original source cycle with the already extracted atoms
deleted. If that first fusion has parents $\{a\},\{b\}$ in this order,
then in any realization of the same extraction prefix, with $b$ at site
0 and $a$ at site $q$, one has $1\le q<n$ and sites
$q+1,\ldots,n-1$ are empty.

**Proof.** A rotation or nonfusing slide preserves positive cyclic order;
extraction deletes one entry. The supplied feasible fusion places $a,b$
at ports 0,1, so they are directed cyclic neighbors. Every realization
of the same singleton extraction prefix has that same restricted cycle.
The positive arc from $a$ to $b$ consequently has no other packet.
With two live packets, either directed binding is allowed, and the
particular record selects the corresponding empty arc. $\square$

### Lemma 6.2. A phase-restoring fusion and a shadow lift

Under the geometry of Lemma 6.1, the word

$$
 M_q=(p_0d_0)^{n-q}p_0^q
 \tag{6.1}
$$

has exactly one effective event, with ordered parents $(\{a\},\{b\})$.
Its union ends at the old site $q$ of $a$, every other packet returns to
its original site, and

$$
 |M_q|=n+(n-q)\le2n-1.
 \tag{6.2}
$$

For distinct atoms $a,b$, if $b$ is absent in a lower configuration $c$,
define $\operatorname{sh}_{a,b}(c)(b)=c(a)$ and leave all other atoms
unchanged. Write the corresponding packet-field substitution as

$$
 \sigma_{a,b}(B)=
 \begin{cases}B\cup\{b\},&a\in B,\\B,&a\notin B.\end{cases}
 \tag{6.3}
$$

The simulation invariant is that $b$ remains absent in the base path and
the lifted configuration is exactly $\operatorname{sh}_{a,b}(c)$.
Its packet at every site is $\sigma_{a,b}$ of the base packet, so the
two configurations have exactly the same occupied sites. In particular,
every packed lower path lifts with the same cost:

$$
 c\xrightarrow{h\,;\,C}d
 \quad\Longrightarrow\quad
 \operatorname{sh}_{a,b}(c)
   \xrightarrow{\sigma_{a,b}(h)\,;\,C}
 \operatorname{sh}_{a,b}(d).
$$

Here $\sigma_{a,b}(h)$ applies (6.3) to each ordered parent, fusion
result and whole-packet extraction field; it changes neither event order
nor event sort.

**Proof.** In each pair $p_0d_0$, the right packet is rotated from 0
to 1. For the first $n-q-1$ pairs the new port 0 is a site on the empty
arc, so the defect slides it back. On the last pair $a$ reaches port 0,
and exactly the declared ordered fusion occurs. All other packets receive
$n$ rotations in total, including the final $p_0^q$. The union ends at
site $q$. The case $q=n-1$ has no preliminary slides.

For the simulation, absence is preserved by every base operation: no
lower operation recreates an extracted atom. The four operation cases
preserve the stated invariant as follows.

1. **Rotation.** Apply the same rotation to both configurations. Copying
   the coordinate of $a$ to $b$ commutes with the site permutation.
   Both steps have empty event output and cost one.
2. **Silent slide.** The empty port 0 and nonempty port 1 are identical
   occupancy conditions in the base and shadow. The same defect moves
   the base packet $B$ and its lifted packet $\sigma_{a,b}(B)$ from
   1 to 0, respectively. The successor is again the exact shadow, with
   empty output and cost one.
3. **Effective fusion.** Both occupied-port guards are preserved. For
   base ordered parents $(U,V)$, the lifted ordered parents are
   $(\sigma_{a,b}(U),\sigma_{a,b}(V))$, without exchanging their ports.
   They remain nonempty and disjoint: at most one contains $a$, and
   neither base parent contains the absent $b$. The result field is
   exact because
   $\sigma_{a,b}(U\cup V)=\sigma_{a,b}(U)\cup\sigma_{a,b}(V)$.
   Thus the same defect costs one and emits the full substituted fusion
   record, not merely a union with the correct mass.
4. **Whole-packet extraction.** The occupied-port guard is preserved.
   Extract $\sigma_{a,b}(B)$ in the lifted path when the base extracts
   $B$. If $a\in B$, both $a$ and its shadow $b$ become absent; if
   $a\notin B$, the extraction does not affect their shared coordinate.
   The successor is exactly the shadow of the base successor. Both
   auxiliary extractions cost zero and their recorded packets are
   related by (6.3).

Induction over the path gives the displayed same-cost simulation with
the complete substituted log. In the reverse direction, once $a,b$
cohabit, all four operations keep them together or remove both. Erasing
$b$ then preserves the occupied sites and every nonempty recorded packet:
any packet containing $b$ also contains $a$. The same operation cases
give an equal-cost erased path. On such cohabiting tails,
$\operatorname{sh}_{a,b}(\operatorname{erase}_b(c))=c$ and
$\sigma_{a,b}(\operatorname{erase}_b(h))=h$ field by field. These are
the inverse identities needed below. $\square$

### Theorem 6.3. Lower fusion elimination

For $n\ge2$ and every fully extracting feasible lower log $h$, there is
a full singleton extraction permutation $z_h$ such that

$$
 \boxed{\mu_n(h)\le\kappa_n(z_h)+(2n-1)F_0(h)
                    \le K_n+(2n-1)F_0(h).}
 \tag{6.4}
$$

**Proof.** If there is a fusion, write the log at its first one as
$h=uF_0(\{a\},\{b\})v$, where $u$ consists only of singleton
extractions. Form the auxiliary log

$$
 h'=uV(\{b\})\operatorname{erase}_b(v).
 \tag{6.5}
$$

First prove its feasibility. At the original first-fusion checkpoint,
$a,b$ occupy sites 0,1. Replace that fusion by
$p_0^{n-1}$, extraction of $b$, and $p_0$. This restores all remaining
literal sites, with $b$ erased from the original post-fusion packet.
Erase $b$ from the original tail. Lemma 6.2 validates this tail, including
every nonempty parent and extracted packet. Thus $h'$ is feasible before
its minimum is invoked. It has one fewer fusion and one more extraction.

Now take any realization of $h'$, and split it at the inserted extraction
of $b$. Its extraction-only prefix fixes the restricted source cycle.
Lemma 6.1 therefore supplies the directed empty arc with $b$ at port 0.
Replace that zero-cost extraction by $M_q$. The new successor is exactly
the shadow of the old extraction successor, which establishes Lemma 6.2's
simulation invariant at this checkpoint. Lift the remaining path with
that invariant. Its log is
$\sigma_{a,b}(\operatorname{erase}_b(v))=v$, including the ordered
parents, result and extraction fields, and its endpoint is again empty.
The tail cost is unchanged. Only the macro adds cost, at most $2n-1$, so

$$
 \mu_n(h)\le\mu_n(h')+2n-1.
 \tag{6.6}
$$

Iterate at the first remaining fusion. Each refined log is feasible and
has the same singleton start and empty endpoint. After $F_0(h)$ steps
the log is fusion-free and extracts each atom exactly once. Its order
$z_h$ is a full permutation and its minimum is $\kappa_n(z_h)$.
Summing (6.6) proves (6.4). The refined logs are comparison objects;
the lifted path supplied to Theorem 5.4 has the original $h$.
$\square$

## 7. The exact one-block amplitude and equality restrictions

We now compare the delayed-family benchmark with the maximum over all
actual one-block observations. By (2.7), the identity to be proved is
$M_n(\mathbf1_n)=\max_{\operatorname{Part}(Q)=\mathbf1_n}
D_{\mathrm{tot}}(H,Q)=J_n^{\mathrm{del}}$.

### Lemma 7.1. Zero and one transfer

For an actual one-block observation with $n\ge3$, put
$\delta_n=K_n-\binom n2\ge0$. Then

$$
 \begin{array}{c|c|c}
 t&\lambda_n(H,Q)\text{ is at most}
   &J_n^{\mathrm{del}}-D_{\mathrm{tot}}(H,Q)\text{ is at least}\\ \hline
 0&3(n-1)^2&4n-4+\delta_n\\
 1&3(n-1)^2+1&4n-5+\delta_n.
 \end{array}
 \tag{7.1}
$$

**Proof.** For an ordered cyclic-neighbor fusion with left and right
sites $x,y$ and $f=[y-x-1]_n$ holes between them, the word
$p_\ell^{[1-y]_n}d_\ell(p_\ell d_\ell)^f$ realizes exactly that
fusion. It leaves its result at port 0 and carries a common residual
phase on the other packets. Its length is at most $3n-4$. Thus a
fusion-only event path can be replayed successively without restoring
phase after each event.

If $t=0$, the upper layer stays empty. Replay the $n-1$ lower fusions,
then rotate the full packet by at most $n-1$ letters to the requested
site. This costs at most $(3n-4)(n-1)+(n-1)=3(n-1)^2$.

If $t=1$, the unique transfer must carry $\Omega$: no lower atoms
could otherwise reach the final upper packet. All $n-1$ lower fusions
precede that transfer, and there is no upper fusion. The phase-free
replay ends with $\Omega$ at lower port 0, so execute $v$ immediately,
then align above by at most $n-1$ rotations. The cost is at most
$(3n-4)(n-1)+n=3(n-1)^2+1$.
Subtract (4.2) and compare with (4.5), using Lemma 4.1. This gives the
two stated gaps. $\square$

### Theorem 7.2. Exact amplitude of the entire one-block fibre

For every $n\ge3$,

$$
 \boxed{M_n(\mathbf1_n)=J_n^{\mathrm{del}}
                   =5\binom n2+K_n-n+2.}
 \tag{7.2}
$$

More precisely, for any actual one-block observation with $t\ge2$,
its original upper tree $T$ satisfies, with $r=n-t$,

$$
 D_{\mathrm{tot}}(H,Q)+E(T)+S(T)
       +(n+1)r-\binom r2\le J_n^{\mathrm{del}}.
 \tag{7.3}
$$

If $2\le t<n$, its gap is at least $n+1$.

**Proof.** The lower projection has $F_0=n-t=r$ by (2.4). Combine
Theorem 5.4 with Theorem 6.3 to obtain

$$
 \lambda_n(H,Q)+E(T)+S(T)
 \le K_n+(2n-1)r+U_n(t)+(n-1).
 \tag{7.4}
$$

The release from having $t$ rather than $n$ transfer leaves is exact:

$$
 \begin{aligned}
 U_n(n)&=5\binom n2,\\
 \underbrace{U_n(n)-U_n(t)}_{\text{upper cursor release}}
              &=3nr-\binom r2\\
              &=\underbrace{(2n-1)r}_{\text{lower fusion elimination}}
                +\underbrace{\left((n+1)r-\binom r2\right)}_{\text{strict margin}}.
 \end{aligned}
 \tag{7.5}
$$

Every lower prefusion reduces the number of upper transfer leaves, and
the resulting cursor-budget release pays for eliminating that prefusion
in the auxiliary lower problem.
Subtract $\ell_n(\mathbf1_n)=2n-3$ from (7.4) to obtain (7.3).
For $r\ge1$ and $r\le n$, the remaining term is at least $n+1$:
after subtracting $n+1$ it is
$(r-1)(n+1-r/2)\ge0$. The zero and one-transfer strata have the
strict gaps in Lemma 7.1. These cases exhaust every actual one-block
observation. They prove the upper bound in (7.2). The actual observation
in (4.3), with an order attaining $K_n$ and phase $n-1$, attains it by
Theorem 4.3. $\square$

### Theorem 7.3. Necessary structure of an extremal history

If an actual one-block observation attains (7.2), then it has no lower
fusion and exactly $n$ singleton transfers. Its original upper tree is
an ordered left-comb, the chronological first transfer has leaf index
zero in that tree's ordered leaf word, and its original transfer order
$z(H)$ satisfies $\kappa_n(z(H))=K_n$.

**Proof.** The strict gaps in Lemma 7.1 and Theorem 7.2 exclude every
$t<n$. Equation (2.4) then gives $F_0=0$. Since $n$ nonempty disjoint
transfers cover the $n$ atoms, all are singleton and their original order
is a permutation.

For this class, the lower optimum in Theorem 5.4 is exactly
$\kappa_n(z(H))$. Retain that value instead of replacing it by $K_n$.
The same budget gives

$$
 D_{\mathrm{tot}}(H,Q)+E(T)+S(T)
           +(K_n-\kappa_n(z(H)))\le J_n^{\mathrm{del}}.
 \tag{7.6}
$$

At the maximum every added term is zero. Lemma 5.2 identifies the
left-comb. Since $j_0<n$, equation (5.6) gives $j_0=0$, and the last
term gives the extraction equality. All conditions concern the original
log, not a separately selected maximal-cost history. $\square$

These conditions are not sufficient: an ordered left-comb may have cheaper
phases or interleavings. The theorem does not identify every maximizing log
with the transfer-first delayed family.

## 8. Forest replay and the all-upper extrema

Throughout this section $n\ge3$ and $U=U_n(n)=5\binom n2$. All bounds below
use the same $\ell_n(\pi)$ for $\pi=\operatorname{Part}(Q)$ and the
benchmark $J_n^{\mathrm{del}}=K_n+U-n+2$.

### 8.1. The gap moment and the joint structural defect

For a nonnegative cyclic hole profile $h=(h_0,\ldots,h_{r-1})$, define

$$
 \operatorname{mom}(h)=
   \min_{c\in\mathbb Z/r\mathbb Z}\sum_{i=0}^{r-1}i\,h_{c+i}.
 \tag{8.1}
$$

The minimum is attained and invariant under cyclic reindexing. It is zero
exactly when at most one entry is positive, and
$\operatorname{mom}(h)\ge\sum_i h_i-\max_i h_i$.
Indeed, each weighted sum pays every entry except its index-zero entry
at least once; it can vanish only if all other entries vanish.

### Lemma 8.1. Moment-sensitive terminal routing

For all-upper placements $P,Q$ with the same named positive packet cycle,
rank $r\ge2$, and occupied upper port 0 in $P$, there is a silent word
to the literal $Q$ with

$$
 C_{\mathrm{finish}}+\operatorname{mom}(h)
       \le n(n-1)-(n-r)^2,
 \tag{8.2}
$$

where $h$ is the actual source hole profile. In the full singleton
reservation replay, this profile is, up to one common cyclic cut,
$h_i=|T_i|-1$ for its original terminal roots $T_i$.

**Proof.** Appendix A constructs the physical route and proves (8.2).
For the reservation identification, each root occupies the anchor of its
consecutive leaf interval. All other sites of that interval are released
and vacant. At full transfer capacity these intervals partition all $n$
reserved sites, so the gap after root $T_i$ is exactly $|T_i|-1$.
Subtracting the retained cursor is one common physical phase; it changes
neither named cyclic order nor gap counts. Thus the moment of the actual
source equals that of the retained forest profile. $\square$

For a full-capacity terminal forest $\mathcal F=(T_0,\ldots,T_{r-1})$,
put $g=n-r$, $m_i=|T_i|-1$, and define

$$
 \begin{aligned}
 D_\Sigma&=\sum_i\mathscr D(T_i),&
 E_\Sigma&=\sum_i E(T_i),&
 E_{\mathrm{cross}}&=\sum_{i<j}m_i m_j,\\
 \mathcal E(\mathcal F)&=E_\Sigma+E_{\mathrm{cross}}
                         +\operatorname{mom}(m).
 \end{aligned}
 \tag{8.3}
$$

### Lemma 8.2. A common structural account

For the same actual singleton-transfer replay, with shared cursor charge
$\Theta=nW+c_0-c_f$,

$$
 \begin{aligned}
 D_\Sigma+E_\Sigma+E_{\mathrm{cross}}&=\binom g2,\\
 C_{\mathrm{cursor}}+C_{\mathrm{finish}}+\mathcal E(\mathcal F)
 &\le(2n-r)+n(n-1)-\frac{g(g+1)}2+\Theta.
 \end{aligned}
 \tag{8.4}
$$

Moreover $\mathcal E(\mathcal F)\ge2(g-\max_i m_i)$.
It vanishes exactly when every root but possibly one is a leaf and the
exceptional root is an ordered left-comb.

**Proof.** Lemma 5.2 gives
$\mathscr D(T_i)+E(T_i)=\binom{m_i}{2}$. Summing and expanding
$\binom{\sum_i m_i}{2}$ proves the first identity, since $\sum_i m_i=g$.
The event replay has $2n-r$ upper events and exact cost
$(2n-r)+D_\Sigma+\Theta$. Add (8.2) and use
$g^2-\binom g2=g(g+1)/2$ to obtain the second line of (8.4).
These costs belong to one prefix and its own terminal word.

The cross defect pays at least $g-\max_i m_i$: if some $m_q>0$, its
products with the other entries already pay their sum, and a largest
entry may be chosen for $q$. The moment has the same lower bound by
(8.1), giving the factor two. For zero defect, zero moment forces all
positive mass into one root, and zero within-root defect makes that root
a left-comb by Lemma 5.2. Conversely such a forest has zero cross defect,
zero moment and zero within-root defects. $\square$

### 8.2. The shared winding and phase payment

### Lemma 8.3. Two nonwinding events with their phases

For a canonical full-singleton reservation schedule containing a fusion,

$$
 \Theta=nW+c_0-c_f\le n(|H|-2)=n(2n-r-2).
 \tag{8.5}
$$

**Proof.** The first birth does not wind. Before the first fusion, either
another birth does not wind, or every subsequent birth winds. In the latter
case the cursor is at or above all live anchors; the roots are still leaves,
so the first fusion cannot wind. Thus $W\le|H|-2$.

The cursor phases must also be paid. If $W\le|H|-3$, the spare period
absorbs $c_0\le n-1$. If $W=|H|-2$ and $c_0=0$, there is no initial
phase to absorb. It remains to show $c_f\ge c_0$ when exactly two events
do not wind and $c_0>0$.

Canonical reservations include site zero. Before its birth, winding births
keep every live anchor between $c_0$ and the cursor. A fusion there would
be another nonwinding event, in addition to the later site-zero birth.
Hence the second nonwinding event must be that birth, before any fusion.
After it every event winds. The following invariant holds: a live root
anchored below $c_0$ is still a leaf at or behind the cursor. Winding births
preserve it; a fusion using such a leaf on the left could not wind, so every
winding fusion has its left anchor at or above $c_0$. The first fusion
therefore sets the cursor at or above $c_0$, and the invariant keeps it
there through the remaining events. This proves $c_f\ge c_0$ and (8.5).
$\square$

### 8.3. Singleton transfers across all terminal ranks

### Theorem 8.4. The singleton forest budget and its exact maximum

For any actual $(H,Q)\in\mathcal A_n$ with $2\le r<n$, one word with
the same complete log and literal endpoint satisfies

$$
 |w'|+(K_n-\kappa_n(z(H)))+\mathcal E(\mathcal F)+\binom{r-1}{2}
       \le\ell_n(\pi)+J_n^{\mathrm{del}}.
 \tag{8.6}
$$

Across all terminal ranks,

$$
 D_{\mathrm{tot}}(H,Q)+(K_n-\kappa_n(z(H)))\le J_n^{\mathrm{del}},
 \qquad \max_{\mathcal A_n}D_{\mathrm{tot}}=J_n^{\mathrm{del}}.
 \tag{8.7}
$$

**Proof.** In this class all $n$ atoms transfer separately, so there is no
lower fusion. The lower cost is the attained $\kappa_n(z(H))$ for the
original order. Select the moment-sensitive finish of Lemma 8.1 for the
actual reserved forest. Lemmas 8.2 and 8.3 give the event and finish budget
on that same witness.

For any partition of rank $r<n$, the site-1 source-credit argument gives
$\ell_n(\pi)\ge2(n-r)-1$: its $n-r$ effective fusions consume that many
occupied source ports, initially just one is occupied, and only rotations
replenish them, by at most one per letter. Set $g=n-r$. The exact scalar
identity

$$
 \begin{aligned}
 &(2g-1)+U-n+2\\
 &\quad-\left[(2n-r)+n(n-1)-\frac{g(g+1)}2+n(2n-r-2)\right]
       =\binom{r-1}{2}
 \end{aligned}
 \tag{8.8}
$$

then proves (8.6).

For $r=1$, use the retained extraction-defect bound (7.6).
For $r=n$, no fusion occurs. The source and target are full singleton
cycles, so the final silent word is a whole-layer rotation of at most
$n-1$ letters. The cursor payment bounds a realizing word by
$\kappa_n(z(H))+n+n(n-1)+2(n-1)$. For $n\ge3$ this length plus
$K_n-\kappa_n(z(H))$ is strictly below $J_n^{\mathrm{del}}$, by
$n+n(n-1)+2(n-1)+n<U+2$.
The minimum joint cost is no larger than these actual word lengths;
subtract the same $\ell_n(\pi)$ to obtain (8.7).
The delayed observation from Theorem 4.3 attains $J_n^{\mathrm{del}}$ and belongs to
$\mathcal A_n$. $\square$

In the fused multiroot case, at least three roots or two nontrivial roots
force a strict gap in (8.6). This rank-sensitive information is stronger
than just the common maximum over their union.

### 8.4. Whole-packet transfers

### Theorem 8.5. Exact all-upper extremum

Every attainable observation with all atoms finally upper satisfies
$D_{\mathrm{tot}}(H,Q)\le J_n^{\mathrm{del}}$, allowing arbitrary lower prefusions,
whole-packet transfers, ordered upper forests and legal event interleavings.
Consequently

$$
 \boxed{\max_{\mathcal U_n}D_{\mathrm{tot}}(H,Q)
       =\max_{\mathcal A_n}D_{\mathrm{tot}}(H,Q)
       =5\binom n2+K_n-n+2.}
 \tag{8.9}
$$

**Proof.** Put $t=V(H)$ and let $r$ be the final rank. Resource balance
gives $F_0=n-t$, $F_1=t-r$ and $1\le r\le t\le n$.
If $r=1$, use Theorem 7.2. If $t=n$, the $n$ disjoint nonempty transferred
packets cover $n$ atoms, hence all are singletons; use Theorem 8.4.
It remains to treat $2\le r\le t<n$.

Take the original actual forest, reserve its transfer-occurrence leaves,
and minimize the packed lower path independently. The physical induction
from Theorem 5.4 works for a forest as follows. Pause that lower path at
each extraction checkpoint. The upper reservation supplies a vacant
receiver, so an actual guarded $v$ transfers exactly the ready lower port
packet. Between checkpoints execute the original upper fusion records in
their prescribed order. Each retains its complete ordered parents and
result; upper preparations leave the lower checkpoint unchanged. This
continues along one actual representative, not separately chosen edge
witnesses. The last cursor is a surviving root anchor. The actual terminal
source therefore has occupied upper port 0, and Lemma 8.1, dropping its
nonnegative moment, supplies one final silent route to the specified $Q$.
Thus

$$
 |w'|=\mu_n(h)+C_{\mathrm{cursor}}+C_{\mathrm{finish}},\qquad
 C_{\mathrm{finish}}\le n(n-1)-(n-r)^2,
 \tag{8.10}
$$

where $h$ is the original packed lower log. Theorem 6.3 gives
$\mu_n(h)\le K_n+(2n-1)(n-t)$; its comparison permutation is supplied
by fusion elimination, not by treating the original packet order as an
atom permutation.

For the upper cursor only, omit the lower fusion records from the event
count and read each transferred packet as one occurrence leaf. This
preserves anchors and winding charges. It does not omit any record from
the physical replay. If $r<t$, Lemma 8.3's phase argument applies to this
upper skeleton, while the tree-debt identity bounds debt by
$\binom{t-r}{2}$. If $r=t$, only births remain and the first one does
not wind. The resulting bounds are

$$
 C_{\mathrm{cursor}}\le
 \begin{cases}
  (2t-r)+\binom{t-r}{2}+n(2t-r-2),&r<t,\\
  t+n(t-1),&r=t.
 \end{cases}
 \tag{8.11}
$$

Use again $\ell_n(\pi)\ge2(n-r)-1$. Substituting (8.10)--(8.11)
and the lower fusion bound leaves the following nonnegative margins
between $\ell_n(\pi)+J_n^{\mathrm{del}}$ and the replay upper bound:

$$
 \begin{cases}
  \displaystyle\binom{r-1}{2}+3(n-t)
      +\binom{n-r}{2}-\binom{t-r}{2},&r<t,\\[2mm]
  \displaystyle\binom{t-2}{2}+\binom{n-t}{2}+2(n-t)-2,&r=t<n.
 \end{cases}
 \tag{8.12}
$$

The first is nonnegative since $t\le n$; the second since $n-t\ge1$.
This is the same-partition comparison and proves delayed domination in
all remaining cases. Finally the attaining delayed observation lies in
$\mathcal A_n\subseteq\mathcal U_n$, proving (8.9). $\square$

## 9. Localization of excess premium

Define the global total premium and the residual observation class by

$$
 \begin{aligned}
 J_n&=\max_{\pi\text{ attainable}}M_n(\pi),\\
 \mathcal L_n&=\{(H,Q)\text{ attainable}:|\operatorname{Part}(Q)|\ge2,
                  \ \exists a,\ Q(a).\mathrm{layer}=0\}.
 \end{aligned}
 \tag{9.1}
$$

### Corollary 9.1. Localization of a global counterexample

For $n\ge3$,

$$
 D_{\mathrm{tot}}(H,Q)>J_n^{\mathrm{del}}
 \quad\Longrightarrow\quad
 |\operatorname{Part}(Q)|\ge2
 \ \text{and}\ \exists a,\ Q(a).\mathrm{layer}=0.
 \tag{9.2}
$$

**Proof.** A one-block observation is bounded by Theorem 7.2. An all-upper
observation is bounded by Theorem 8.5. Any larger premium must therefore
have multiple blocks and at least one atom still lower. $\square$

The restriction is on complete observations, not on partitions alone: the
same unordered partition can have both all-upper and lower-surviving
realizations. Since the delayed maximum is attained, the outstanding global
comparison is exactly

$$
 J_n=J_n^{\mathrm{del}}
 \quad\Longleftrightarrow\quad
 D_{\mathrm{tot}}(H,Q)\le J_n^{\mathrm{del}}
       \quad\text{for every }(H,Q)\in\mathcal L_n.
 \tag{9.3}
$$

## 10. Computational Artifacts

The Lean companion, theorem-to-source map and reproduction instructions are
organized under `experiments/paper47/` in the
[RIME Lite repository](https://github.com/dooven-prime/rime-lite).

## 11. Conclusion

The same delayed history attains the exact maximum
$5\binom n2+K_n-n+2$ both in the complete one-block fibre and over all
all-upper observations. The cursor, moment and erasure-shadow bounds cover
arbitrary ordered forests, packet masses and legal interleavings; any larger
unrestricted premium must involve multiple terminal blocks and a
lower-layer survivor.

## Appendix A: Displacement-sensitive terminal routing

### Lemma A.1. A common-cut physical route

Let $P,Q$ be all-upper placements with the same named positive packet
cycle of rank $2\le r\le n$. If upper port 0 is occupied in $P$, then
there is an actual silent word $W$ from $P$ to the literal $Q$ with

$$
 |W|+\operatorname{mom}(h)\le n(n-1)-(n-r)^2,
 \tag{A.1}
$$

where $h$ is the actual source hole profile.

**Proof.** Put $g=n-r$. Read both packet cycles at a common cut, and let
$h_i,q_i$ be the source and target hole counts after packet $i$.
Their sums are both $g$. Cut at a minimum of the partial sums of
$h_i-q_i$. In the resulting coordinates,
$0=x_0<\cdots<x_{r-1}<n$ and $0=y_0<\cdots<y_{r-1}<n$ satisfy
$x_j-y_j=\sum_{i<j}(h_i-q_i)\ge0$.
This cuts the two named cycles together; it is not a physical rotation.
If the actual source anchor is at $p$, retain the initial cursor
$c_0=[-p]_n$. Let the target anchor's actual site be $b$.

Process $j=1,\ldots,r-1$ in increasing order. A root with
$d_j=x_j-y_j=0$ needs no slide. Otherwise the arc $[y_j,x_j)$ is empty:
earlier roots are at smaller target coordinates and later roots remain at
larger source coordinates. With retained cursor $c$, the actual word

$$
 p_1^{[c-(x_j-1)]_n}d_1(p_1d_1)^{d_j-1}
 \tag{A.2}
$$

moves just this root backward to $y_j$, while preserving the other lifted
coordinates. Every defect slides into a hole. Its new cursor is $y_j$,
and the exact payment is $|u_j|+y_j=c+nw_j+d_j$ with
$w_j=\mathbf1_{c<x_j-1}$. Thus, if $a$ roots move and $D=\sum d_j$,

$$
 |u|+c_f=c_0+nN+D,\qquad c_f\ge a,
 \tag{A.3}
$$

Here $N$ is the sum of winding indicators. The nonzero initial cursor is
paid as follows. If $c_0=0$, use $N\le a$.
If $c_0>0$ and the first root moves, the source's occupied physical port 0
has normalized coordinate $c_0$, so $x_1\le c_0$. The first turn does not
wind and $N\le a-1$. If $c_0>0$ and the first root does not move, then
$a\le r-2$, and that unused root allocation pays $c_0\le n-1$.
In all three cases (A.3) gives $|u|\le(r-1)(n-1)+D$.
Append the actual rotation $p_1^{[c_f+b]_n}$ to restore the target phase.
Its total cost is at most $r(n-1)+D$.

At this same cut, summing the coordinate prefix differences gives

$$
 D+\sum_{i=0}^{r-1}i h_i=\sum_{i=0}^{r-1}i q_i
       \le(r-1)g.
 \tag{A.4}
$$

Since $\operatorname{mom}(h)\le\sum_i i h_i$, it follows that
$D+\operatorname{mom}(h)\le(r-1)g$. Combining this with the actual
route cost gives
$|W|+\operatorname{mom}(h)\le r(n-1)+(r-1)g=n(n-1)-g^2$.
The cut is common to the source, target and displacement identity;
no independent moment-minimizing reordering or free physical phase was used.
$\square$

## References
