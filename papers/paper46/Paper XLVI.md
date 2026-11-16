# Single-Port Stacked Rings: Bell Universality, Retention Geometry, and Sharp Endpoint Costs

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XLVI | Version 1.0**

*RIME Paper XLVI, version 1.0. This paper studies reachability, retention,
and primitive-word cost in a guarded two-ring packet system.*

## Abstract

We study two directed rings with independent rotations, adjacent fusion,
and one guarded transfer port. A target block family can remain on the
lower ring exactly when its blocks are intervals in the source order
restricted to the retained atoms; this criterion also determines the minimum
transferred atom mass. Every set partition is reachable. For a partition
with $b$ blocks, an explicit construction realizes a specified stacked
placement in at most $n^2+2n-b-1$ primitive letters. Endpoint requirements
produce different sharp costs: a single-vacancy literal endpoint has a
unique shortest word of length $n(n-1)$, while an all-upper singleton
endpoint has minimum length $3n-2$ and $2^{n-1}$ shortest words for $n\ge3$.
The antipodal perfect matching on $2m$ atoms admits a partition-realization
length between $7m-7$ and $9m-2$. For the general unordered partition diameter, we obtain
$\Omega(n\log n)$ and $O(n^2)$ bounds.

**Keywords:** circular order; packet fusion; guarded transition system;
set partition; word length; retention criterion

## 1. Introduction

A circular fusion system preserves more than the set of surviving atoms.
Positive rotation and an adjacent collapse preserve cyclic source order:
packets remain source intervals, with the same physical packet order.
Adding a second ring and a single one-way transfer port changes this
restriction. Atoms may leave the lower source cycle in a chosen order and
be assembled upstairs in another order. The resulting mixed endpoint
partition can cross the original source order, even though every fusion
occurs within one ring.

We ask three questions. Which partitions become attainable? Which blocks
can be required to remain on the original ring? Which endpoint requirements
force expensive synchronization? These are distinct questions because an
endpoint partition forgets physical coordinates and layer allocation.
A costly literal placement can project to a partition already present at
the initial state.

The central result is the retention equivalence of Theorem 4.3: a chosen
family of target blocks can remain below exactly when its blocks are
intervals in the restricted source cycle. A constructive realization of
every partition (Section 3) supplies the complementary upper blocks. The
criterion then determines minimum transferred mass. Resource balances turn
this geometry into two sharp literal-endpoint costs (Sections 5--6), whereas
antipodal crossing partitions admit linear-length realizations (Section 7).

### Related models

These questions are related to orientation-preserving transformations of
finite circular orders. Mitchell and Levi study generating ranks and
idempotent generation for such transformation semigroups
[@leviMitchell2006]. Cameron et al. study word length when each digraph arc
is a defect-one generator [@cameronEtAl2017]. The present raw metric instead
charges rotations and collapse separately in a fixed five-letter alphabet.

Rearrangement through restricted storage is also classical. Tarjan studies
sortability through networks of queues and stacks [@tarjan1972], and Biedl
et al. establish permutation sorting and quadratic costs for certain
two-node data-structure networks [@biedlEtAl2010]. Thus permutation
universality and quadratic rearrangement cost already occur in small storage
networks. Wu and Grumbach study directed motion through a vacant site
[@wuGrumbach2009]. Here irreversible packet fusion and one guarded transfer
port lead to a classification of which target blocks can remain on the
lower ring.

### Relation to Paper XLV

Paper XLV preserves a complete ordered fusion log and literal endpoint in
a one-ring system [@chen2026fusionLog]. Here the two-ring guarded action
classifies endpoint partitions and layer allocations, and studies selected
literal costs without prescribing a fusion log.

## 2. Guarded two-ring semantics

Fix $n\ge2$, the atom set $\Omega=\{0,\ldots,n-1\}$, and the site
cycle $C_n=\mathbb Z/n\mathbb Z$. Write $[x]_n$ for the representative of
$x$ in $\{0,\ldots,n-1\}$. A placement is a function

$$
 P:\Omega\longrightarrow\{0,1\}\times C_n.
 \tag{2.1}
$$

Its nonempty fibres are packets. Thus packets are nonempty, disjoint, and
cover $\Omega$ by definition. We write $P_\ell(q)$ for the packet at
layer $\ell$, site $q$, allowing an empty value. The singleton seed is
$P_{\rm seed}(a)=(0,a)$.

The alphabet is $\Sigma=\{p_0,p_1,d_0,d_1,v\}$, with chronological
concatenation: the leftmost letter executes first.

- $p_\ell$ sends every location $(\ell,q)$ to $(\ell,q+1)$ and fixes
  the other layer.
- $d_\ell$ sends $(\ell,1)$ to $(\ell,0)$ and fixes all other
  locations. If both ports are occupied, their packets fuse. If only site 1
  is occupied, its packet slides into site 0. If site 1 is empty, nothing
  changes.
- $v$ is enabled exactly when $P_0(0)\ne\varnothing$ and
  $P_1(0)=\varnothing$. It moves the whole packet $P_0(0)$ to upper
  site 0 and leaves lower site 0 empty.

Each letter costs one, including a slide or ineffective collapse. Powers
always expand into primitive letters. The partial executor is
$\operatorname{run}(P,W)$; it returns a placement exactly when every
transfer guard succeeds. A word is legal from $P$ when this value is defined.

Rotations preserve the packet partition, and a successful transfer preserves
it because its receiver is empty. Effective collapses merge two packets.
There is no splitting operation. Consequently packet equality is
irreversible:

$$
 P(a)=P(b),\quad \operatorname{run}(P,W)=Q
 \quad\Longrightarrow\quad Q(a)=Q(b).
 \tag{2.2}
$$

Layer transfer is also irreversible. An atom that reaches the upper ring
never returns below. In particular, if $W$ realizes a target partition
$\pi$, every packet at every prefix is contained in one block of $\pi$.
We call this property target purity.

We distinguish two optimization problems. For a reachable literal placement
$Q$, and an unordered partition $\pi$, put

$$
 \begin{aligned}
 \ell_{\rm lit}(Q)
   &=\min\{|W|:\operatorname{run}(P_{\rm seed},W)=Q\},\\
 \ell_n(\pi)
   &=\min\{|W|:W\text{ is legal from }P_{\rm seed},\quad
                   \operatorname{Part}(\operatorname{run}(P_{\rm seed},W))
                       =\pi\}.
 \end{aligned}
 \tag{2.3}
$$

Write $\Pi_n$ for the unordered partitions of $\Omega$.
Here $\operatorname{Part}$ forgets sites and layers. These definitions
prescribe no event history. Section 3 makes the second minimum nonempty for
every $\pi$; natural-number well-ordering then gives a minimum.

For example, when $n=4$ the legal eight-letter word

$$
 vp_1d_0p_0d_0p_0vd_1
 \tag{2.4}
$$

ends with $\{1,3\}$ at lower site 1 and $\{0,2\}$ at upper site 0.
Its partition crosses the original source order.

## 3. Bell universality and a canonical literal representative

### 3.1. Source alignment and permutation loading

Suppose the lower ring has used only rotations and transfers. Every
untransferred atom remains a singleton. If the cumulative lower rotation
count is $r$, its site is $[a+r]_n$. A chosen remaining atom at site $q$
can therefore be brought to the source port by $p_0^{[-q]_n}$, using at
most $n-1$ letters and no fusion.

**Lemma 3.1 (permutation loading).** For every permutation
$(a_0,\ldots,a_{n-1})$ of $\Omega$, there is a legal fusion-free word
ending with lower ring empty and $P_1(i)=\{a_i\}$ for all $i$. Its
length is at most $n^2+n-1$.

**Proof.** Transfer atoms in reverse order, aligning each below. Between
successive transfers apply one $p_1$. After $k$ transfers, the upper
singletons occupy sites $0,\ldots,k-1$ in the appropriate suffix order.
If $k<n$, the next upper rotation moves that support to $1,\ldots,k$,
so its receiver is empty. This proves every guard. The word has $n$
transfers, $n-1$ upper rotations, and at most $n(n-1)$ lower rotations. $\square$

### 3.2. Interleaved construction

Choose an ordered presentation $(B_0,\ldots,B_{b-1})$ of a target
partition, and an order of the atoms within each block. Process blocks in
reverse order and each block's atoms in reverse order. For every new atom,
perform these instructions:

1. Except at the first transfer, rotate the upper ring once.
2. Align the atom below and transfer it upward.
3. If it continues the current block, apply $d_1$; if it starts a new
   block, omit that collapse.

After $k$ transfers, all upper occupied sites are in $0,\ldots,k-1$.
The processed suffix of the current block is one packet at site 0, and all
completed earlier blocks are separate. Before transfer $k+1$, the upper
rotation clears site 0 and sends the current suffix to site 1. A continuation
therefore fuses exactly the new singleton at 0 with its own suffix at 1.
A new block instead remains a new packet. This proves the invariant by
induction, including the receiver guard. Since the next transfer is used
only for $k<n$, no wraparound invalidates the support bound.

**Theorem 3.2 (canonical stacked placement).** Let $\pi$ have $b$ blocks,
with ordered presentation $(B_0,\ldots,B_{b-1})$, and set
$s_i=\sum_{h<i}|B_h|$. The interleaved construction produces a legal word
$W_\pi$ with

$$
 P_0\equiv\varnothing,\qquad P_1(s_i)=B_i,
 \tag{3.1}
$$

all other upper sites empty. Its exact primitive counts satisfy

$$
 \#v=n,\quad \#p_1=n-1,\quad \#d_1=n-b,\quad \#d_0=0,
 \qquad |W_\pi|=R_0(W_\pi)+3n-b-1,
 \tag{3.2}
$$

where $R_0=\#p_0$. In particular,

$$
 |W_\pi|\le n^2+2n-b-1.
 \tag{3.3}
$$

**Proof.** The invariant proves legality and the identities of all packets.
When block $B_i$ is completed, it is at site 0 and exactly $s_i$ transfers
remain. Each remaining transfer is preceded by one upper rotation; none of
its later fusions uses $B_i$. Its final site is therefore $s_i<n$.
These coordinates are distinct because all blocks are nonempty.

There is one transfer for every atom and one upper rotation between
successive transfers. Block $B_i$ uses $|B_i|-1$ collapses, all effective.
This gives (3.2). Each lower alignment costs at most $n-1$, so
$R_0\le n(n-1)$ and (3.3) follows. More precisely, if the transfer order
is $a_1,\ldots,a_n$, then

$$
 R_0(W_\pi)=[-a_1]_n+
                \sum_{i=2}^n[a_{i-1}-a_i]_n.
 \tag{3.4}
$$

Indeed the lower phase immediately after transferring $a_{i-1}$ is
$-a_{i-1}$ modulo $n$, giving the next alignment increment. $\square$

**Corollary 3.3 (Bell endpoint universality).** The reachable endpoint
partitions are exactly all partitions of $\Omega$, and hence number
$B_n$ [@dlmfBell]. Every such partition has a representative of length at most
$n^2+2n-2$.

**Proof.** Every placement determines a partition. Conversely, choose an
ordered presentation of any partition and apply Theorem 3.2. Since $b\ge1$,
its bound gives the uniform claim. $\square$

The endpoint (3.1) is canonical relative to the chosen block order;
the realizing word also depends on the atom order within each block.

## 4. The exact retention criterion

Let $U(P)$ be the atoms currently below. Delete every other atom from the
source cycle $0,\ldots,n-1$. Label the remaining atoms by their lower
packets. A packet is a cyclic interval when its label occupies one cyclic
run, including the one-packet case. Empty retained families impose no
interval condition.

**Lemma 4.1 (lower restricted source order).** At every prefix of every
legal seed execution, each lower packet is a cyclic interval in the source
cycle restricted to $U(P)$. The cyclic sequence of these packets agrees
with their positive physical cyclic order.

**Proof.** At each prefix, construct a nondecreasing map
$f:\mathbb Z\to\mathbb Z$ satisfying

$$
 f(x+n)=f(x)+n,\qquad
 [f(x)]_n=\operatorname{site}_P([x]_n)
       \quad\text{if }[x]_n\in U(P).
 \tag{4.1}
$$

At the seed take $f(x)=x$. A lower rotation replaces $f$ by $f+1$.
A lower collapse composes it with

$$
 D_n(z)=\begin{cases}z-1,&[z]_n=1,\\z,&\text{otherwise}.
                  \end{cases}
 \tag{4.2}
$$

For $n>1$, $D_n$ is nondecreasing and degree one. Upper actions keep $f$;
transfer removes a whole lower packet and only drops matching obligations
in (4.1). Hence the lift persists through every legal prefix, including
prefusion and deletion of atoms whose lift coordinates remain as ghosts.

To obtain the packet assertion, assume at least two lower packets and cut
the source cycle at a retained atom $a$. In the source turn from $a$ to
$a+n$, all lift values lie between $f(a)$ and $f(a)+n$. Each occupied
physical site other than the site of $a$ has a unique integer representative
strictly between these bounds. All retained atoms at that site therefore
share one lift value. Monotonicity makes them consecutive among retained
source atoms, and orders the distinct packet sites by increasing lift value.
The packet containing $a$ may meet both ends of the cut, which form one
cyclic interval. The empty and one-packet cases are immediate. $\square$

For a target partition $\pi$ and a proposed lower block family
$\mathcal L\subseteq\pi$, write
$U_{\mathcal L}=\bigcup_{B\in\mathcal L}B$. Call $\mathcal L$
retention-admissible when each of its blocks is a cyclic interval in the
source cycle restricted to $U_{\mathcal L}$.

**Lemma 4.2 (adjacent lower fusion).** Any two ordered consecutive lower
packets can be fused using lower letters only, with no other effective
fusion.

**Proof.** Choose the positively oriented arc from the first packet's site
to the second packet's site, with no occupied site in its interior. Choose
an integer lift $q$ of the first site; the unique lift of the second site in
$\{q+1,\ldots,q+n-1\}$ is $q+1+f$, where $0\le f\le n-2$.
Thus the interior sites $q+1,\ldots,q+f$ are empty. The chronological macro

$$
 E_j=p_0^{[-j]_n}d_0p_0^{[j]_n}
 \tag{4.3}
$$

sends site $[j+1]_n$ to $[j]_n$ and fixes every other site after restoring
the coordinate frame. Apply it at the decreasing integer indices
$j=q+f,q+f-1,\ldots,q+1$, taking no such step when $f=0$.
Each step slides only the second packet backwards along the chosen positive
empty arc. If the arc crosses the original zero, its lifted indices still
decrease in this order; only the physical sites and rotation exponents are
reduced modulo $n$. Rotate the resulting adjacent pair to ports
0 and 1 and apply $d_0$. With two packets either ordered choice has an
empty intervening arc, so the same argument applies. The upper ring is
unchanged throughout. $\square$

**Theorem 4.3 (retention equivalence).** There is a legal execution from
$P_{\rm seed}$ with
endpoint partition $\pi$, lower packet family exactly $\mathcal L$, and
upper packet family $\pi\setminus\mathcal L$ if and only if
$\mathcal L$ is retention-admissible.

**Proof.** Necessity follows from Lemma 4.1 at the endpoint. For sufficiency,
apply the interleaved construction to only the complementary blocks.
Its upper support after $k$ transfers is still contained in
$0,\ldots,k-1$, so every required guard succeeds. The untransferred
atoms remain lower singletons in restricted source order.

Every current lower packet is now contained in a target retained block.
If a retained block has more than one current packet, its interval property
provides consecutive packets within that block. Apply Lemma 4.2. It does
not merge different targets or change the upper ring. The nonnegative
integer

$$
 \mu=\#\{\text{current lower packets}\}-|\mathcal L|
 \tag{4.4}
$$

decreases by one at each such fusion. At zero, the lower packet family is
exactly $\mathcal L$. If that family is empty no lower assembly is needed;
if the upper family is empty no loading is needed. The two parts
concatenate into one legal word. $\square$

Define transferred atom mass by

$$
 T(W)=\sum_{\text{successful transfers }e}|\operatorname{packet}(e)|.
 \tag{4.5}
$$

Every atom crosses at most once. Thus from any initial placement $P$ to $Q$,
upper atom mass satisfies

$$
 \operatorname{UpperMass}(P)+T(W)=\operatorname{UpperMass}(Q).
 \tag{4.6}
$$

In particular seed executions satisfy $T(W)=n-|U(Q)|$.

**Corollary 4.4 (minimum transferred mass).** Let

$$
 M(\pi)=\max_{\mathcal L\text{ retention-admissible}}
                  \sum_{B\in\mathcal L}|B|.
 \tag{4.7}
$$

Then the minimum transferred atom mass among all realizations of $\pi$ is

$$
 T_{\min}(\pi)=n-M(\pi).
 \tag{4.8}
$$

**Proof.** The finite maximum exists because the empty retained family is
admissible. Theorem 4.3 constrains every actual lower family to be admissible,
so (4.6) gives the lower bound. The theorem also realizes a maximizing
family and hence attains it. $\square$

This resource is atom mass, independently of elevator-letter count or raw
length. One elevator may transfer many atoms together. Retention can also
have higher-order obstructions: for
$\{\{0,5\},\{1,4\},\{2,3\}\}$, every two-block family is
admissible, while all three are not. Its restricted label cycle is
$ABCCBA$, with four cyclic runs after compression. A pairwise conflict
graph therefore does not determine retention admissibility.

## 5. Resource ledgers and a linear optimum with commuting multiplicity

For a successful seed word, write $R_\ell=\#p_\ell$, $D_\ell=\#d_\ell$,
and $V=\#v$. Let $F_\ell$ count actual effective fusions on layer
$\ell$, $N_0=D_0-F_0$ count all other lower collapses, and $K_\ell(Q)$
count occupied terminal sites on that layer. Define lower control-letter cost

$$
 C_{\rm port}(W)=R_0+D_0+V.
 \tag{5.1}
$$

The name is a control-letter accounting convention: it is not a count of
physical visits to site zero. Every ineffective lower collapse is charged.

**Lemma 5.1 (packet and port balances).** Every successful seed word obeys

$$
 \begin{aligned}
 K_0(Q)+V+F_0&=n,\\
 K_0(Q)+K_1(Q)+F_0+F_1&=n,\\
 C_{\rm port}(W)+K_0(Q)&=n+R_0+N_0,\\
 |W|&=C_{\rm port}(W)+R_1+D_1.
 \end{aligned}
 \tag{5.2}
$$

**Proof.** A transfer reduces lower rank by one and increases upper rank by
one. An effective fusion reduces only its layer's rank by one. All remaining
steps preserve these counts. Telescope from the seed, use $D_0=F_0+N_0$,
and partition the five letter classes. $\square$

Put $c_0(P)=[P_0(0)\ne\varnothing]$ and
$e_1(P)=[P_1(0)=\varnothing]$, where brackets denote an indicator.

**Lemma 5.2 (source and receiver credits).** From any placement $P$ to $Q$,

$$
 \begin{aligned}
 c_0(Q)+V&\le c_0(P)+R_0+N_0,\\
 e_1(Q)+V&\le e_1(P)+R_1.
 \end{aligned}
 \tag{5.3}
$$

**Proof.** Each transfer consumes an occupied lower source and an empty
upper receiver. Refilling an empty lower source requires a lower rotation
or a nonfusing lower collapse. Clearing an occupied upper receiver requires
an upper rotation: $d_1$ moves into site 0 and cannot clear it. Check these
inequalities on each actual successful step and telescope. $\square$

We will also use a geometric rotation bound. For a distinguished atom $a$,
put $A_a(P)=n-q$ if $P(a)=(0,q)$ with $2\le q<n$, and zero otherwise.
For another atom $b$, put $S_{a,b}(P)=0$ if they share a packet, and
$S_{a,b}(P)=A_a(P)$ otherwise. Each satisfies the single-step inequality

$$
 X(P)\le[\alpha=p_0]+X(Q).
 \tag{5.4}
$$

For $A_a$, only rotation can reduce a positive value. For $S_{a,b}$, a
first fusion can erase the separation only at active lower sites 0 and 1,
or above, where the approach value is already zero. This proves (5.4)
also at the first merger. Consequently, for $2\le a<n$,

$$
 a\text{ ends upper or shares a packet with another atom}
 \quad\Longrightarrow\quad R_0\ge n-a.
 \tag{5.5}
$$

These inequalities are combined by maximum when they charge the same
rotations. They are not summed over atoms.

Consider the literal all-upper singleton endpoint

$$
 S_n(a)=(1,[a-1]_n).
 \tag{5.6}
$$

**Theorem 5.3 (linear optimum and complete shortest-word family).** For
$n\ge2$, $\ell_{\rm lit}(S_n)=3n-2$, and its minimum lower control cost
is $2n-1$. For $n\ge3$, the shortest words are exactly

$$
 v\,r_1v\,r_2v\cdots r_{n-1}v,
 \qquad r_i\in\{p_0p_1,p_1p_0\}.
 \tag{5.7}
$$

There are $2^{n-1}$ such literal words. For $n=2$ there are four:
$vp_0p_1v$, $vp_1p_0v$, $vd_0p_1v$, and $vp_1d_0v$.

**Proof.** Terminal injectivity and (2.2) exclude every effective fusion.
All $n$ atoms must transfer, so $V=n$. The source credit gives
$R_0+N_0\ge n-1$ and hence $C_{\rm port}\ge2n-1$; the receiver credit
gives $R_1\ge n-1$. Their disjoint letter classes yield $|W|\ge3n-2$.
Taking $r_i=p_0p_1$ in (5.7) gives the legal word
$V_n=v(p_0p_1v)^{n-1}$, attaining both bounds. After each transfer the next two rotations refill the
source and clear the receiver. Tracking transferred atoms gives (5.6).

At equality, $V=n$, $R_1=n-1$, $D_1=0$, and $R_0+D_0=n-1$.
Each of the $n-1$ inter-transfer intervals must contain a lower control
letter and an upper rotation. Equality leaves exactly one of each and no
prefix or suffix letters. Thus an interval is initially one of
$p_0p_1,p_1p_0,d_0p_1,p_1d_0$.

If the first lower letter were $d_0$, the second transfer would carry
atom 1. The remaining $n-2$ upper rotations would leave it at upper
site $n-2$, whereas (5.6) requires site 0. For $n\ge3$ this is impossible.
After a $p_0$ interval and its transfer, lower sites 0 and 1 are both
empty. A $d_0$ in the next interval cannot prepare the next transfer.
Induction forces every lower letter to be $p_0$. Independent layer
rotations commute, so all choices in (5.7) execute to $S_n$. Their distinct
two-letter intervals give an injective Boolean encoding and the count.
For $n=2$ both lower controls prepare the second transfer, and the four
displayed skeletons are exhaustive. $\square$

Modulo the word congruence generated by $p_0p_1\sim p_1p_0$, there is
one shortest-word class for $n\ge3$. At $n=2$ that rotation-only
congruence has three classes;
also allowing $d_0p_1\sim p_1d_0$ reduces the count to two.

For comparison, the literal endpoint consisting of one full packet at upper
site 0 has exact minimum raw and lower control costs $2n-2$ for $n\ge3$.
The all-upper bound from (5.2) and (5.5) is attained by
$d_0(p_0d_0)^{n-2}v$.

## 6. Endpoint-forced quadratic cost and literal rigidity

Let $\mathcal V_n$ consist of injective placements with only atom 1 upper,
atom 0 at lower site 1, and lower site 0 empty. The other retained atoms'
coordinates and atom 1's upper coordinate are not prescribed in this class.

**Theorem 6.1 (single-vacancy geometric obstruction).** For $n\ge3$, every
seed execution ending in $\mathcal V_n$ satisfies

$$
 R_0(W)\ge(n-1)^2,\qquad
 C_{\rm port}(W)\ge n(n-1),\qquad |W|\ge n(n-1).
 \tag{6.1}
$$

**Proof.** Injectivity excludes every effective fusion. One-way transfer
then forces exactly one transfer, of atom 1 alone. Before it all lower
sites are occupied, so no lower collapse is possible in a successful
realization of the target. Write $b$ for atom 1's lower site before this
transfer. It occurs at $b=0$, with atom 0 at $n-1$; immediately afterwards
the vacancy is $h=0$. After transfer let $q$ be atom 0's lower site and put

$$
 k=[q-h]_n\in\{1,\ldots,n-1\}.
 \tag{6.2}
$$

Geometrically, a productive slide requires $h=0$ and leaves $h=1$; the
next slide, or the terminal vacancy at 0, needs a fresh return around the
lower ring. Rotation preserves $k$, while a slide decreases it by one
cyclically in $\{1,\ldots,n-1\}$. Starting at $k=n-1$ and ending at
$k=1$ requires at least $n-2$ such slides. The following state potential
accounts for these successive debts without selecting intervals.

For $A(x)=[-x]_n$, define the before- and after-transfer potentials by

$$
 \begin{aligned}
 \Psi_{\rm full}(b)&=(n-2)(n-1)+A(b),\\
 \Psi_{\rm deleted}(h,q)&=(k-1)(n-1)+A(h).
 \end{aligned}
 \tag{6.3}
$$

At transfer these agree: $b=0$ before and $(h,k)=(0,n-1)$ after.
For a lower rotation, $A$ decreases by one unless its argument is 0,
when it increases to $n-1$; after transfer $k$ is unchanged. A productive
slide has $h=0$. If $k>1$, it gives $(h',k')=(1,k-1)$ and preserves
$\Psi$; if $k=1$, it gives $(h',k')=(1,n-1)$ and increases it.
At $h=1$ a lower collapse is ineffective; at other nonzero vacancy sites
it would fuse and is excluded. Upper letters do not change this potential.
Thus, writing $\Psi$ for the appropriate branch, every actual step
$P\xrightarrow{\alpha}P'$ satisfies

$$
 \Psi(P)-\Psi(P')\le[\alpha=p_0],\qquad
 \Psi(P_{\rm seed})=(n-1)^2,\qquad \Psi(Q)=0
       \quad(Q\in\mathcal V_n).
 \tag{6.4}
$$

Telescoping proves the rotation bound. For lower control and raw cost, use
the work potential

$$
 \begin{aligned}
 \mathcal W_{\rm full}(b)&=\Psi_{\rm full}(b)+(n-2)+1,\\
 \mathcal W_{\rm deleted}(h,q)&=\Psi_{\rm deleted}(h,q)+(k-1)
                              =n(k-1)+A(h).
 \end{aligned}
 \tag{6.5}
$$

\newpage

For any successful execution ending in $\mathcal V_n$, effective fusion is
excluded. With $\Delta\mathcal W=\mathcal W(P)-\mathcal W(P')$, the permitted
action cases are:

| Letter and case | $\Delta\mathcal W$ |
| :--- | :---: |
| $v$ | $1$ |
| $p_0$, with $b\ne0$ before transfer or $h\ne0$ after | $1$ |
| $p_0$, with $b=0$ or $h=0$ | $-(n-1)$ |
| $d_0$ at $h=0$ (slide), with $k>1$ | $1$ |
| $d_0$ at $h=0$ (slide), with $k=1$ | $<0$ |
| Ineffective $d_0$, $p_1$, or ineffective $d_1$ | $0$ |

Here a $d_0$ at $h=1$ is ineffective; at any other nonzero vacancy it
would fuse and is excluded. The table gives

$$
 \mathcal W(P)-\mathcal W(P')
   \le[\alpha\in\{p_0,d_0,v\}],\qquad
 \mathcal W(P_{\rm seed})=n(n-1),\qquad \mathcal W(Q)=0.
 \tag{6.6}
$$

Summing along the actual word yields
$n(n-1)\le C_{\rm port}(W)\le|W|$. The same work function will force
the letter choices at equality in Theorem 6.2. $\square$

Define the particular endpoint

$$
 Q_n(1)=(1,0),\qquad Q_n(0)=(0,1),\qquad
 Q_n(a)=(0,a)\quad(2\le a<n).
 \tag{6.7}
$$

**Theorem 6.2 (sharp optimum and unique shortest raw word).** For $n\ge3$,

$$
 \ell_{\rm lit}(Q_n)=\min_{W\text{ realizes }Q_n}C_{\rm port}(W)
                      =n(n-1).
 \tag{6.8}
$$

The unique word attaining the raw minimum is

$$
 Z_n=p_0^{n-1}v(d_0p_0^{n-1})^{n-2}.
 \tag{6.9}
$$

**Proof.** After $p_0^{n-1}v$, the lower vacancy is 0, atom 0 is at
$n-1$, and atom 1 is upper at 0. A cycle $d_0p_0^{n-1}$ leaves the
vacancy at 0 and maps a retained site $q$ to $n-1$ if $q=1$, and to
$q-1$ otherwise. Its $n-2$ repetitions give exactly (6.7).
The word has $(n-1)^2$ lower rotations, $n-2$ lower defects, one transfer,
and no upper letters. It attains Theorem 6.1.

At raw equality every letter must decrease $\mathcal W$ by exactly one.
Before transfer, this forces $p_0$ while $b\ne0$, then $v$ at $b=0$.
After transfer, it forces $p_0$ when $h\ne0$, and $d_0$ when $h=0$
and $k>1$. No upper letter or ineffective collapse pays a unit. At
$h=0,k=1$ the remaining work is zero and the word ends. Starting from the
seed, these forced choices are precisely (6.9), proving literal list
uniqueness. $\square$

The lower bound holds on the broader terminal class $\mathcal V_n$;
the endpoint (6.7) attains it. Its projection is the initial singleton
partition, so
$\ell_{\rm lit}(Q_n)=n(n-1)$ while
$\ell_n(\operatorname{Part}(Q_n))=0$.

## 7. Antipodal matchings admit shared linear preparation

Let $n=2m$, $m\ge2$, and consider

$$
 B_i=\{i,i+m\},\qquad
 \pi_m=\{B_i:0\le i<m\}.
 \tag{7.1}
$$

Any two pairs alternate around the source circle. They cannot both be
intervals after restricting to their four atoms. At most one target block
may remain below. Any one pair can remain, so Corollary 4.4 gives
$M(\pi_m)=2$ and $T_{\min}(\pi_m)=2m-2$. This mass statement alone
does not price the rotations.

### 7.1. A fusion gate for arbitrary histories

**Lemma 7.1 (antipodal lower fusion gate).** Every actual implementation of
$\pi_m$ has at most one effective lower fusion.

**Proof.** Target purity makes each effective fusion join the singleton
members of one target pair. By restricted source order, when such a pair
fuses, one of the two open source semicircles between its atoms has no atom
remaining below. This can equivalently be read immediately after fusion
from the interval property of its new packet. Each other antipodal pair
has an atom in that semicircle and hence already has an atom above. None
can subsequently fuse below. Applying this argument to the first lower
fusion excludes a second one. The case of two remaining lower packets is
included; both open arcs then lack other lower atoms. $\square$

**Proposition 7.2 (unrestricted raw lower bound).** Every legal word whose
endpoint partition is $\pi_m$ satisfies

$$
 |W|\ge7m-7,\qquad C_{\rm port}(W)\ge4m-3.
 \tag{7.2}
$$

**Proof.** Retention gives $K_0\le1$ and Lemma 7.1 gives $F_0\le1$.
The lower packet balance implies $V\ge2m-2$. Source atom 2 must merge
with its distinct antipodal mate, so (5.5) gives $R_0\ge2m-2$.
The port balance now gives
$C_{\rm port}\ge2m-1+R_0\ge4m-3$.

The receiver credit yields $R_1\ge V-1\ge2m-3$.
Terminal rank is $m$, so the two-layer rank balance gives $F_0+F_1=m$;
hence $D_1\ge F_1\ge m-1$. These are disjoint primitive letter costs:

$$
 |W|=C_{\rm port}+R_1+D_1
       \ge(4m-3)+(2m-3)+(m-1)=7m-7.
 \tag{7.3}
$$

This proves (7.2). $\square$

### 7.2. An actual two-pass upper bound

Define the raw word

$$
 Y_m=v(p_0p_1^2v)^{m-1}\,
          p_0p_1^3vd_1\,
          (p_0p_1^2vd_1)^{m-1}.
 \tag{7.4}
$$

**Lemma 7.3 (spaced two-pass witness).** The word $Y_m$ is legal and ends
with lower ring empty and

$$
 P_1\bigl(2[i-1]_m\bigr)=B_i\quad(0\le i<m),
 \tag{7.5}
$$

all odd upper sites empty. Its primitive counts are

$$
 \begin{aligned}
 R_0&=2m-1,&R_1&=4m-1,&V&=2m,\\
 D_0&=0,&D_1&=m,&|Y_m|&=9m-2,
 \end{aligned}
 \qquad C_{\rm port}(Y_m)=4m-1.
 \tag{7.6}
$$

**Proof.** Write $a_j=[-j]_{2m}$. After the first pass has transferred
$k$ atoms, $1\le k\le m$, its entire upper support is

$$
 P_1\bigl(2(k-1-j)\bigr)=\{a_j\},\qquad 0\le j<k.
 \tag{7.7}
$$

Every untransferred atom $a$ is lower at $[a+k-1]_{2m}$. For $k<m$,
two upper rotations shift old support to $2,\ldots,2k$, leaving 0
empty. One lower rotation supplies the next atom $a_k$. This proves the
first-pass guards and coordinates by induction.

At $k=m$, atom 0 is upper at $2m-2$, and the lower atoms are $1,\ldots,m$.
The middle lower rotation brings $m$ to the source. Three upper rotations
place atom 0 at site 1 and leave site 0 empty: the preceding support was
even and the ring has even length. The next $vd_1$ creates $B_0$.

All upper-site coordinates in the following identities are interpreted
modulo $2m$. After $k$ second-pass fusions, $1\le k\le m$, the complete
upper support is

$$
 \begin{aligned}
 P_1\bigl(2(k-1-j)\bigr)&=B_{[-j]_m},&&0\le j<k,\\
 P_1(2m+2k-1-2j)&=\{a_j\},&&k\le j<m.
 \end{aligned}
 \tag{7.8}
$$

The remaining lower atoms are $1\le a\le m-k$, at sites $a+m+k-1$.
Completed upper pairs are even and at most $2k-2$; pending singletons
are odd, from $2k+1$ to $2m-1$. If $k<m$, the next lower rotation
brings $m-k$ to 0. Its mate $a_k$ is at upper site $2m-1$, so two
upper rotations put it at 1. The upper receiver is empty because its
predecessor $2m-2$ was empty. The next $vd_1$ is legal and produces
$B_{m-k}$ at 0, giving (7.8) for $k+1$.

At $k=m$ no pending singleton or lower atom remains. Substitution in the
completed coordinates gives (7.5). Counting the expanded letters in (7.4)
gives (7.6). $\square$

**Theorem 7.4 (linear antipodal partition cost).** Minimizing over all
literal endpoints and layer allocations,

$$
 7m-7\le\ell_{2m}(\pi_m)\le9m-2,\qquad m\ge2.
 \tag{7.9}
$$

Moreover,

$$
 4m-3\le\min_{\operatorname{Part}(W)=\pi_m}C_{\rm port}(W)\le4m-1.
 \tag{7.10}
$$

**Proof.** Proposition 7.2 applies to every feasible word; Lemma 7.3
supplies a feasible upper-bound word. The feasible length set is nonempty,
so its least natural number satisfies (7.9). The identical argument applies
to lower control cost. $\square$

Thus $\ell_{2m}(\pi_m)=\Theta(m)$, although all pairs mutually cross
and almost every atom must transfer. The construction reserves upper
receiver vacancies between pending partners and shares their preparation
across two extraction passes.

## 8. Bounds for the Unordered Partition Diameter

Define

$$
 D_n^{\rm partition}=\max_{\pi\in\Pi_n}\ell_n(\pi).
 \tag{8.1}
$$

This is a seed-rooted realization diameter for partitions, not the
diameter of the directed graph of all placements.

Theorem 3.2 gives $D_n^{\rm partition}\le n^2+2n-2$. A five-letter
count provides an elementary lower bound:

$$
 B_n\le\sum_{k=0}^{D_n^{\rm partition}}5^k
       =\frac{5^{D_n^{\rm partition}+1}-1}{4},\qquad
 D_n^{\rm partition}\ge
       \left\lceil\log_5(4B_n+1)\right\rceil-1.
 \tag{8.2}
$$

There are at most $5^k$ words of length $k$, including illegal ones,
and a legal word from the fixed seed has at most one endpoint partition.
Universality therefore requires at least $B_n$ such words in the diameter
ball. This proves (8.2).

An elementary count proves the superlinear order without a Bell
asymptotic formula. For $1\le k\le n$, every function from $n$
atoms to $k$ labels defines its partition into nonempty fibres. A partition
with $b\le k$ blocks has at most $k!/(k-b)!\le k!$ such labelings.
Consequently

$$
 B_n\ge\frac{k^n}{k!}\ge k^{n-k},\qquad
 D_n^{\rm partition}\ge(n-k)\log_5 k-1.
 \tag{8.3}
$$

Choosing $k=\lfloor n/\ln n\rfloor$ for sufficiently large $n$ gives

$$
 \liminf_{n\to\infty}
       \frac{D_n^{\rm partition}}{n\ln n}\ge\frac1{\ln5}.
 \tag{8.4}
$$

Indeed $k/n\to0$ and $\ln k/\ln n\to1$.

Together, the bounds give

$$
 \Omega(n\log n)\le D_n^{\rm partition}\le O(n^2).
 \tag{8.5}
$$

## 9. Computational Artifacts

The companion package contains a Lean 4.33.0 formalization of the guarded
placement model, including Bell realization, the retention criterion,
transfer mass, and the stated literal and antipodal cost bounds. It also
contains finite-state controls for small instances and a theorem-to-source
map. The paper's mathematical arguments are given above; the companion
provides a separate check of the formalized declarations and bounded
examples. The source location and replay command are specified in the
companion README.

## 10. Conclusion

The guarded transfer port makes every endpoint partition reachable while
Theorem 4.3 identifies precisely which blocks may remain below. The same
five-letter system has a unique quadratic shortest word for one literal
endpoint, a commuting family of linear optima for another, and linear
partition cost for antipodal matchings. The diameter bounds in (8.4)--(8.5)
measure the remaining gap for unordered partitions.
