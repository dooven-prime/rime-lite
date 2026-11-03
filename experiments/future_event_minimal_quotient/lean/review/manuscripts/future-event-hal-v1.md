# Future-Event Minimal Quotients for a Circular Registered Absorption System

**WuJun Chen**

Independent Researcher | 2026

## Abstract

We give an exact, observation-contract-dependent state minimization with
explicit distinguishing certificates for a circular packet system generated
by rotation and one adjacent collapse. Starting from identity-placed
singletons, we register the fusion that creates the source pair
$F=\{0,1\}$. The full-summary observer reads the current placement and the
registered absorption history; the future-event observer reads only the
complete selected events emitted by subsequent letters. These contracts
induce different right congruences on the same reachable state space.

For every $n\ge3$, we classify the future-event congruence: all states from
which no selected event remains possible form one class; each registerable
pre-registration placement is a class; and registered nonterminal states
are equivalent exactly when their current placed partitions agree. Explicit
raw words distinguish every inequivalent pair within $6n-10$ letters. The
proof combines an outside-anchored sweep for registered placements with an
atomwise gap probe whose entire coalescence fiber is characterized.

Writing $R_n$ for registerable pre-registration placements, $A_n$ for
registered nonterminal placements, and $s_n$ for complete registered
summaries, the two minimal state counts are

$$
Q_n^{\mathrm{future}}=1+R_n+A_n,
\qquad Q_n^{\mathrm{full}}=1+R_n+s_n.
$$

Their exponential growth bases are $4$ and $9/2$, respectively. These are
model- and observer-relative state counts, not reset thresholds or generic
memory lower bounds.

**Keywords:** Mealy right congruence; circular packet dynamics; event
registration; state minimization; constructive distinguishing word

## 1. Introduction

A state sufficient to continue an execution need not retain every event that
led to it. Conversely, whether an old event can be forgotten depends on the
observer. The event-anchored model of [@chenPaper39v1] follows one selected
fusion and its subsequent carrier. A separate counting result
[@chenAbsorption2026] enumerates its complete registered summaries for the
circular adjacent-collapse action. Neither count is automatically the number
of states needed to predict only *future* selected events.

Here we fix the same raw action and registered pair, but compare two precise
observation contracts. A Moore observer displays the complete current
registered summary. A Mealy observer emits, letter by letter, only newly
occurring selected registration or absorption records. Right
indistinguishability for these contracts follows the classical sequential
machine viewpoint [@mealy1955; @moore1956; @nerode1958]. Our contribution is
an explicit classification and count of the classes of these two minimal
right congruences, together with constructive distinguishing words that
establish minimality independently of finite enumeration.

The key asymmetry is that a registered selected chain is never emitted
again. Once registered, its current placement determines all future selected
events. Already for $n=5$, the two actual words

$$
\begin{aligned}
w_1&=d\,p^3d\,(pdp^4)p^2d,\\
w_2&=d\,(p^4dp)d\,(p^3dp^2)(p^4dp)d
\end{aligned}
$$

both reach $P(0)=\{0,1,2,3\}$ and $P(4)=\{4\}$. Their registration
origins agree, but $w_1$ first assembles $\{2,3\}$ away from the carrier
and then absorbs it in one selected event, whereas $w_2$ absorbs $\{2\}$
and $\{3\}$ in two selected events. The full-summary observer separates
these old chains immediately; every future selected-event trace agrees.
Before registration, however, distinct placements remain distinguishable.
A gap probe can coalesce with a different starting placement, so its target
must be chosen carefully. An exact description of that probe's coalescence
fiber yields a strictly decreasing gap and resolves the pairwise separation
problem.

The mathematical scope is fixed throughout: $n\ge3$, the identity singleton
seed on $Q=\mathbb Z/n\mathbb Z$, raw letters $p$ and $d$, the ordered
collapse ports $(0,1)$, selected source pair $F=\{0,1\}$, complete event
records, all reachable histories, and no word-length budget. Section 2
fixes the two contracts. Sections 3--5 prove placement control and the two
probe lemmas. Section 6 proves the quotient and depth theorems. Section 7
counts the classes and the explicit probe-coalescence graph.

## 2. Model and observation contracts

Let $\Omega$ be a set of $n$ source atoms and $Q=\mathbb Z/n\mathbb Z$ a
set of physical sites. We identify their labels only at the singleton seed
$P_0(q)=\{q\}$. A **placed partition** $P$ assigns to each occupied site
$q\in Q$ a nonempty packet $P(q)\subseteq\Omega$. Its packets are disjoint
and cover $\Omega$; unoccupied sites are holes.

The raw letter $p$ acts by $p(q)=q+1$. The letter $d$ acts by

$$
d(1)=0,\qquad d(q)=q\quad(q\ne1).
$$

Packets follow the site maps and packets with the same image merge by
union. Each letter therefore defines a total deterministic update of placed
partitions. A word is executed chronologically, from left to right.

We select $F=\{0,1\}\subseteq\Omega$. A **registration** occurs when an
actual $d$-fusion first creates a packet whose source set is exactly $F$.
Its record contains the letter, both ordered kernel ports, the two actual
parent packets, and the collision site. Since packets never split, a
registration can occur at most once. After registration, a **selected
absorption** is an actual fusion involving the packet containing $F$; its
record again retains the ordered parent packets and ports. Unrelated fusions
may occur, but emit no selected event.

The retained execution state is $x=(P,o,A)$: current placed partition,
registration origin $o$ (or $\bot$ before registration), and the ordered
selected absorption chain $A$. Let $X_n$ be the set of such states reachable
from $(P_0,\bot,())$ by actual $p,d$ words. The selected event output
$\epsilon(x,a)$ is null unless letter $a$ creates the registration or a
selected absorption, when it is the complete new record. For $w=a_1\cdots
a_m$, let $\operatorname{Trace}(x,w)$ be the length-$m$ sequence of these
outputs. Define the future-event right congruence

$$
x\equiv_{\mathrm{future}}y
\quad\Longleftrightarrow\quad
\operatorname{Trace}(x,w)=\operatorname{Trace}(y,w)
\text{ for every }w\in\{p,d\}^{*}.
\tag{2.1}
$$

The **full-summary** observer instead displays $\bot$ before registration
and the entire current $(P,F,o,A)$ afterwards. Its Moore right congruence
$\equiv_{\mathrm{full}}$ compares the displayed output after every common word,
including the empty word. Write $Q_n^{\mathrm{future}}$ and $Q_n^{\mathrm{full}}$ for
the numbers of equivalence classes on $X_n$.

There are three useful semantic regions. Let $\mathcal R_n$ consist of
unregistered states from which registration of $F$ remains possible. Let
$\mathcal Z_n$ consist of the other unregistered states together with
registered rank-one states. Finally, registered states with at least one
packet outside the $F$-carrier are called **registered nonterminal**. Let
$R_n=|\mathcal R_n|$, let $A_n$ count their distinct current placed
partitions, and let $s_n$ count *all* registered complete summaries,
including rank one.

## 3. Source order, placement control, and counts

**Lemma 3.1 (source order and nonfusion control).** Every reachable packet is
a consecutive source arc, and the occupied packets occur in the positive
cyclic source order. If two placed partitions have the same packet blocks in
that order, one is reachable from the other by an actual word with no fusion.

**Proof.** Both statements hold at the seed. Rotation preserves packet
order. A $d$-fusion joins packets at physical sites $0,1$, adjacent in the
occupied cyclic order, so it joins consecutive source arcs without changing
the order of the remaining packets. If site $0$ is empty and site $1$
occupied, $d$ instead moves that packet into the hole at $0$ without fusion
or a change of cyclic packet order; the other nonfusion cases leave the order
unchanged. For placement control, use the fusion-free placement-control
lemma of [@chenAbsorption2026, Lemma 2.2]. Its elementary guarded move is

$$
E_j=p^{[-j]_n}dp^{[j]_n}.
$$

When site $j$ is a hole and $j+1$ is occupied, this actual word moves only
that packet from $j+1$ to $j$ at its end; its middle $d$ does not fuse.
Let $r$ be the number of blocks. If $r=1$, a rotation aligns the sole
block even when holes remain. Assume $r\ge2$ for the gap transfers. Name
the blocks in their
common cyclic order
$B_0,\ldots,B_{r-1}$ and let $h_i$ count the holes after $B_i$ and before
$B_{i+1}$, cyclically. The total $\sum_i h_i=n-r$ is fixed. Applying $E_j$
at the hole immediately before $B_{i+1}$, when $h_i>0$, changes exactly

$$
(h_i,h_{i+1})\longmapsto(h_i-1,h_{i+1}+1)
\qquad(r\ge2,\ h_i>0).
$$

The packet crosses that hole but no other packet, so the block order and
every packet's source set are unchanged. If $g$ is the target gap vector,
choose $e$ with $h_e>g_e$ and $f$ with $h_f<g_f$. Route one hole from gap
$e$ to gap $f$ through consecutive gap indices. The first transfer is
legal because $h_e>0$; each subsequent donor has just received that hole.
The intermediate gaps have zero net change, so this route replaces $h$ by
$h-e_e+e_f$ and decreases $\sum_i(h_i-g_i)_+$ by one. Finitely many actual
routes reach $g$. A final power of $p$ aligns $B_0$ and therefore all
blocks. If there are no holes, rotation alone suffices. At each crossing
the guard is checked on the concrete state produced by the preceding word.
$\square$

**Lemma 3.2 (registration criterion).** An unregistered reachable state is
in $\mathcal R_n$ if and only if source atoms $0$ and $1$ remain separate
singleton packets. In such a state, if their sites are $a,b$, then the
positive arc from $a$ to $b$ contains only holes between them and
$1\le[b-a]_n\le n-2$.

**Proof.** If either atom has already fused with an outside atom, no future
fusion can create exactly $F$; if they had fused with each other, that
fusion would already have registered $F$. Conversely, when both are
singleton packets, they are consecutive in source order by Lemma 3.1.
Nonfusion placement control puts them at ports $0,1$ in that order, after
which one $d$ registers $F$. An outside packet remains because $n\ge3$,
giving a nonempty complementary arc and the stated gap range. $\square$

**Proposition 3.3 (placement counts).** For $n\ge3$,

$$
\begin{aligned}
R_n&=n\binom{2n-4}{n-3},\\
A_n&=n\sum_{k=1}^{n-2}(n-1-k)\binom{n+k-2}{k}\\
&=2(2n-3)\binom{2n-4}{n-2}-n(n-1).
\end{aligned}
\tag{3.1}
$$

**Proof.** Partition the $n-2$ outside atoms into $t\ge1$ nonempty
consecutive packets. There are $\binom{n-3}{t-1}$ cuts. The $t+2$ named
packets have $(t+2)\binom n{t+2}=n\binom{n-1}{t+1}$ source-ordered
physical placements. These are actually reachable without registering
$F$: assemble each outside interval from singleton packets by adjacent
fusions, keeping sources $0,1$ separate, and use Lemma 3.1 to place the
result. Thus

$$
R_n=n\sum_{t=1}^{n-2}\binom{n-3}{t-1}\binom{n-1}{t+1}
=n\binom{2n-4}{n-3}.
$$

For the second count, fix a proper source-arc carrier containing $F$ and
leave $k\ge1$ outside atoms. Its left and right extensions from $F$ have
sum $n-2-k$, so there are $n-1-k$ such carriers. For each, partition the
$k$ outside atoms into $t$ nonempty consecutive packets and place those
$t$ packets and the carrier in cyclic order. Summing over $t$ gives
$n\binom{n+k-2}{k}$ placements. They are actual registered placements:
register $F$, extend its carrier by adjacent singleton absorptions to the
fixed source arc, assemble outside packets by fusions not involving the
carrier, then use Lemma 3.1 to reach any target placement. This is also a
direct consequence of the constructive fixed-carrier fiber theorem in
[@chenAbsorption2026]; only placement existence, not its history count, is
used here. The carrier is read from the packet containing $F$, so different
carriers do not overlap in the count.

For the closed form, put $m=n-2$ and use
$\sum_{k=0}^{m}\binom{m+k}{k}=\binom{2m+1}{m}$ and
$\sum_{k=0}^{m}k\binom{m+k}{k}=(m+1)\binom{2m+1}{m-1}$.
Substitution and elementary binomial ratios give (3.1). $\square$

## 4. Registered-placement probes

For a site $q$, define the raw word

$$
W_q=p^{[-q]_n}d(pd)^{n-2},
\qquad |W_q|\le3n-4.
\tag{4.1}
$$

The rotation in this word is an actual nonnegative power of $p$.

**Lemma 4.1 (aligned sweep).** If two registered nonterminal states have
their $F$-carriers at the same site $q$ but different placed partitions,
$W_q$ gives different future-event traces.

**Proof.** Rotate the common carrier to site $0$. Name the packet initially
at site $j$ by $B_j$, using an empty symbol at holes. The first $d$ records
$B_1$ if present and leaves the carrier at $0$. In the $i$th following
$pd$ pair, the $p$ moves the carrier to $1$ and brings the packet initially
at site $n-i$ to $0$; the $d$ records that packet if present and returns the
carrier to $0$. The output positions therefore read

$$
B_1, B_{n-1}, B_{n-2},\ldots,B_2
$$

with null exactly at holes. The first nonnull record also gives the
original carrier packet. Such a record exists because the state is
nonterminal. Hence the complete trace recovers the normalized placed
partition and separates different placements. $\square$

**Lemma 4.2 (first-event orientation decoder).** Fix a site $q$ and a
registered nonterminal state $z$. After the initial rotation
$p^{[-q]_n}$ in $W_q$, let $r$ be the carrier site. If the first selected
event in the remaining word $d(pd)^{n-2}$ occurs at its initial $d$ with
the carrier as right parent, then $r=1$. If it occurs at the $d$ of the
$k$th $pd$ pair with the carrier as left parent, then $r=n-k$. An event
at the initial $d$ with the carrier as left parent instead gives $r=0$.

**Proof.** An event at the initial $d$ with the carrier as right parent
puts it at port $1$; the left-parent case puts it at port $0$. For a
first event with the carrier as left parent in the $k$th $pd$ pair,
consider all earlier $d$ letters. If one had left the carrier at site
$0$, the next $p$ would put it at site $1$. Each subsequent nonselected
$d$ would move it back to $0$, while any selected $d$ would use it as
the right parent. The same applies if an earlier nonselected $d$ moved
the carrier from site $1$ into an empty site $0$. Neither history permits
the stated first left-parent event. Thus the carrier has been fixed by
each earlier $d$ and moved only by the $k$ rotations in the $pd$ pairs.
It reaches port $0$ when $r+k=0$ modulo $n$, giving $r=n-k$. These are
implications for the specified first-event types; no assertion is made
about traces with no selected event. $\square$

**Lemma 4.3 (outside-anchored phase).** Let $x$ be registered nonterminal,
with carrier site $c$, and choose the site $q\ne c$ of any outside packet.
For every registered nonterminal comparison state $y$,

$$
\operatorname{Trace}(x,W_q)=\operatorname{Trace}(y,W_q)
\quad\Longrightarrow\quad
\operatorname{carrierSite}(y)=c.
\tag{4.2}
$$

**Proof.** After the initial rotation, the outside anchor of $x$ is at
$0$. Put $j=[q-c]_n$, so the carrier begins at $r=[c-q]_n=n-j$.
If $j=n-1$, the first $d$ has the carrier at port $1$ and the anchor at
port $0$, producing an immediate selected event with the carrier as right
parent. If $1\le j\le n-2$, the first $d$ leaves the anchor packet at
site $0$, possibly after an unrelated fusion. Until it meets the carrier,
each following $pd$ pair moves that packet from $0$ to $1$ and back to
$0$; it may absorb further outside packets but cannot lose its anchored
source atoms. The first selected event is
the $d$ in the $j$th $pd$ pair: the carrier reaches port $0$ and the anchor
is at port $1$, so the carrier is left parent.

| Offset $j=[q-c]_n$ | First selected event | Carrier parent | Initial normalized site $r$ |
|:--|:--|:--|:--|
| $n-1$ | Initial $d$ | Right, at port $1$ | $1$ |
| $1\le j\le n-2$ | $d$ in the $j$th $pd$ pair | Left, at port $0$ | $n-j$ |

The same first-event position and parent role occur in $y$ when the
complete traces agree. Lemma 4.2 decodes its initial normalized carrier
site without assuming that its packet at site $0$ matches the anchor
packet of $x$. Both normalized carrier sites are therefore $r$; undoing
the common rotation gives the claim. $\square$

**Corollary 4.4 (registered separation).** Every two registered
nonterminal states with different current placements are separated by one
$W_q$. If the carrier sites differ, choose an outside site $q$ of the first
state and apply Lemma 4.3. If they agree, choose $q$ to be the common
carrier site and apply Lemma 4.1. In either case the same raw word is run
from both states.

## 5. Pre-registration gap probes

For a placed partition $P$, let $\operatorname{site}_P(z)$ be the site of
the packet containing source atom $z$. For a chronological word
$w=a_1\cdots a_m$ let
$\phi_w=f_{a_m}\circ\cdots\circ f_{a_1}$, where $f_p=p$ and $f_d=d$.

**Lemma 5.1 (atomwise execution).** For any actual placed partition, word
$w$, and source atom $z$,

$$
\operatorname{site}_{\delta_w(P)}(z)
=\phi_w(\operatorname{site}_P(z)).
\tag{5.1}
$$

Furthermore, the entire final placed partition is recovered from these
sites: its packet at $q$ is the nonempty fiber
$\{z:\operatorname{site}_P(z)=q\}$.

**Proof.** Under one letter every atom in a packet moves to the image of
its packet's site. When images coincide, their atom sets merge at that
image. This proves (5.1) for a letter even through fusion. Induction on the
word proves the formula, and the fiber identity recovers the partition.
$\square$

For $x\in\mathcal R_n$, let $a,b$ be the sites of singleton sources $0,1$
and set $g=[b-a]_n$. By Lemma 3.2, $1\le g\le n-2$ and sites
$a+1,\ldots,a+g-1$ are holes. Define

$$
V_x=p^{[1-b]_n}(dp)^{g-1}d,
\qquad |V_x|\le3n-6.
\tag{5.2}
$$

**Lemma 5.2 (site fibers and first registration).** Write $V_x=v_xd$ and
let $\Phi_x=\phi_{v_x}$. Then

$$
\Phi_x^{-1}(0)=\{a\},\qquad
\Phi_x^{-1}(1)=\{a+1,\ldots,a+g\}.
\tag{5.3}
$$

$\Phi_x$ is injective on the complement of
$\{a,a+1,\ldots,a+g\}$ and maps that complement away from ports $0,1$.
The word $V_x$ first registers exactly $F$ on its last letter.

**Proof.** The initial rotation sends $a$ to $1-g$ and $b$ to $1$.
One chronological $dp$ block has site map $T(0)=T(1)=1$ and
$T(j)=j+1$ otherwise. Use integer representatives for the interval
$\{1-k,\ldots,1\}$ and reduce their sites modulo $n$. For
$0\le k\le g-1\le n-3$, the stronger induction statement is

$$
T^k(j)=
\begin{cases}
0,&j=-k,\\
1,&j\in\{1-k,\ldots,1\},\\
j+k,&j\notin\{-k,1-k,\ldots,1\}.
\end{cases}
\tag{5.3a}
$$

At $k=0$ this is the identity map. Suppose it holds at $k$. The old
fiber over $1$ stays there, while its neighboring site $-k$, whose
image was $0$, also moves to $1$ under the next $T$. The site
$-(k+1)$ previously mapped to $-1$, and now maps to $0$. Every other
site is still translated by one. The displayed cases are disjoint in
the stated range, so this proves the induction and, in particular,

$$
(T^k)^{-1}(0)=\{-k\},\qquad
(T^k)^{-1}(1)=\{1-k,\ldots,1\};
$$

the remaining nonempty fibers are singletons. With $k=g-1$, the initial
rotation takes $a$ to $-k$ and takes the sites $a+1,\ldots,a+g$ to
$1-k,\ldots,1$, proving (5.3). The source-$0$ atom thus reaches port
$0$, and source $1$ reaches port $1$. The open arc between them was empty
in $x$; every other initially occupied site lies outside the displayed
fiber, where $\Phi_x$ is injective and avoids both ports.

For completeness, a fusion between two *distinct initial packets* at any
earlier prefix would make their atom sites equal at every later prefix:
site maps never split a packet. Their $\Phi_x$-images would then coincide,
contradicting injectivity on the initially occupied sites just described.
This does not rule out packets already fused before the probe, nor does it
need to. Thus the prefix $v_x$ has no new fusion, and its final $d$
creates exactly $F$ with ordered parents $\{0\},\{1\}$. $\square$

For each $1\le h\le g$, let $x^{(h)}$ retain every packet and site of $x$
except that singleton $\{1\}$ is moved from $b=a+g$ to $a+h$; thus
$x^{(g)}=x$. Choose integer lifts $\widetilde b=\widetilde a+g$ and read
every subscript modulo $n$. For $h<g$, the actual word

$$
E_{\widetilde b-1}E_{\widetilde b-2}\cdots E_{\widetilde a+h}
\tag{5.4}
$$

moves $\{1\}$ successively into holes without a fusion. For $h=g$ the
word is empty. Hence all $x^{(h)}$ belong to the same generated
registerable domain.

**Lemma 5.3 (exact probe-coalescence fiber).** For $x,y\in\mathcal R_n$,

$$
\begin{aligned}
&\operatorname{Trace}(x,V_x)=\operatorname{Trace}(y,V_x)
\text{ and }P(\delta_{V_x}x)=P(\delta_{V_x}y)\\
&\hspace{25mm}\Longleftrightarrow\quad
y=x^{(h)}\text{ for a unique }1\le h\le g(x).
\end{aligned}
\tag{5.5}
$$

The case $h=g(x)$ is the identity comparison. For a distinct coalescing
$y$, necessarily $g(y)=h<g(x)$.

**Proof.** Equal complete traces force the same ordered singleton parents
at the last $d$. Let $\Psi_x=d\circ\Phi_x$ be the full site map of
$V_x$. Since $d^{-1}(0)=\{0,1\}$, (5.3) gives its entire zero fiber:

$$
\Psi_x^{-1}(0)=\{a,a+1,\ldots,a+g\}.
\tag{5.6}
$$

Every nonzero image fiber is a singleton, lying outside this interval:
$d$ fixes the other sites and $\Phi_x$ is injective on their preimages.
The ordered final registration record says that, immediately before its
$d$, source $0$ is the singleton parent at port $0$ and source $1$ is
the singleton parent at port $1$. Equation (5.3) therefore forces the
initial site of source $0$ in $y$ to be $a$, and that of source $1$ to be
$a+h$ for a unique $1\le h\le g$.

Now fix an outside atom $z\notin F$. In the execution from $x$ it starts
outside $\{a,\ldots,a+g\}$, so its final site $q_z=\Psi_x(\operatorname{site}_{P_x}(z))$
is nonzero. Equal final placed partitions make its final site from $y$
the same $q_z$. By atomwise execution (5.1), its initial site in $y$ lies
in $\Psi_x^{-1}(q_z)$; that fiber consists solely of its initial site in
$x$. This holds for each outside atom, even when several already share
one initial packet. Along with the recovered sites of sources $0,1$,
atom-site recovery gives exactly $y=x^{(h)}$, with unique $h$.

Conversely, take $y=x^{(h)}$. Its occupied sites consist of $a$, the
new site $a+h$ of singleton $\{1\}$, and the unchanged outside sites.
By (5.3), $\Phi_x$ sends these to port $0$, port $1$, and pairwise
distinct sites away from both ports, respectively. Hence no two distinct
packets of $y$ can fuse in the prefix: if they did, they would still have
the same site after $v_x$. The same reasoning applied above shows this
for $x$. Both complete traces are therefore null before the last letter,
where the same ordered singleton parents register $F$. Finally (5.6)
sends both possible initial sites $b$ and $a+h$ of source $1$ to site
$0$; every other atom starts at the same site in $x$ and $y$. Their
final atom-site functions, hence their complete placed partitions, are
equal. $\square$

**Example (six-site gap probe).** Let $n=6$ and take the reachable
unregistered placements

$$
\begin{aligned}
x:&\quad 0:\{0\},\quad 3:\{1\},\quad
4:\{2,3\},\quad 5:\{4,5\},\\
y=x^{(2)}:&\quad 0:\{0\},\quad 2:\{1\},\quad
4:\{2,3\},\quad 5:\{4,5\}.
\end{aligned}
$$

The omitted sites are holes; the actual fusion-free word $E_2$ moves
$x$ to $y$. Their gaps are $3$ and $2$. The probe
$V_x=p^4(dp)^2d$ maps source $0$ to port $0$, either initial site $2$
or $3$ of source $1$ to port $1$, and the two outside packets to sites
$4,5$ before its final $d$. Both runs have null output until the same
registration of $F$, and both finish at
$0:\{0,1\},\ 4:\{2,3\},\ 5:\{4,5\}$. In the other direction,
$V_y=p^5(dp)d$ has pre-final port-$1$ fiber $\{1,2\}$, which excludes
source $1$'s site $3$ in $x$. Thus $y$ registers under $V_y$, whereas
$x$ emits only null. Probing from the smaller gap prevents this
coalescence.

**Corollary 5.4 (pre-registration separation).** Distinct states in
$\mathcal R_n$ have a common distinguishing raw suffix of length at most
$6n-10$.

**Proof.** Choose a state of smaller gap as $x$, so $g(x)\le g(y)$. If the
traces under $V_x$ differ, stop. Otherwise (5.5) rules out equal final
placements: a distinct coalescing $y$ would have strictly smaller gap.
Both endpoints registered exactly $F$ on the final letter and are
nonterminal, because $n\ge3$ leaves at least one outside source atom.
Corollary 4.4 supplies a word $W_q$ separating their endpoint placements.
For the *same* concatenated word from either initial state,

$$
\operatorname{Trace}(z,V_xW_q)
=\operatorname{Trace}(z,V_x)
\mathbin{+\!+}\operatorname{Trace}(\delta_{V_x}z,W_q).
$$

Thus $V_xW_q$ separates $x,y$, and its length is at most
$(3n-6)+(3n-4)=6n-10$. $\square$

## 6. The exact quotient and a uniform distinguishing depth

**Theorem 1 (future-event minimal quotient).** For $n\ge3$ and reachable
states $x,y\in X_n$,

$$
x\equiv_{\mathrm{future}}y
\quad\Longleftrightarrow\quad
\begin{cases}
x,y\in\mathcal Z_n,\quad\text{or}\\
x,y\in\mathcal R_n\text{ and }P_x=P_y,\quad\text{or}\\
x,y\text{ are registered nonterminal and }P_x=P_y.
\end{cases}
\tag{6.1}
$$

Consequently the minimal future-event machine has
$Q_n^{\mathrm{future}}=1+R_n+A_n$ states.

**Proof.** All states in $\mathcal Z_n$ emit null on every future letter:
an unregistered state unable to register can never acquire an origin, and
a rank-one registered state cannot absorb another packet. Equal current
placements within $\mathcal R_n$ have the same unregistered state and
deterministic continuation. Equal current placements in the registered
nonterminal region also have identical future outputs: a selected event
depends on the current packets and the carrier containing $F$, not on the
earlier origin or chain, neither of which is re-emitted. These observations
show that the stated classification defines a right congruence.

Distinct registered nonterminal placements are separated by Corollary 4.4;
distinct members of $\mathcal R_n$ by Corollary 5.4. For cross-region
pairs, $V_x$ emits a registration event from $x\in\mathcal R_n$, while a
sink emits only null and an already registered state can emit no *new*
registration event. A registered nonterminal state has a selected
absorption along some $W_q$, while a sink emits only null. Registration and
absorption have distinct output tags. Thus no two different keys are
equivalent. $\square$

**Theorem 2 (constructive uniform separation).** If reachable states
$x,y$ satisfy $x\not\equiv_{\mathrm{future}}y$, they have a common distinguishing
suffix of length at most $6n-10$. It can be chosen as a $V_x$, a $W_q$,
or a concatenation $V_xW_q$. In particular, agreement on all future-event
traces of words of length at most $6n-10$ implies equivalence.

**Proof.** The cross-region and registered cases in Theorem 1 use one
probe. Corollary 5.4 handles distinct registerable pre-registration
placements and is the only case requiring a concatenation. All words are
actual words over $\{p,d\}$, with nonnegative rotation exponents. The
probe bounds (4.1) and (5.2) give the stated cap. $\square$

**Lemma 6.1 (event-to-summary prefix detection).** Let $x,y$ be reachable
unregistered states. If a common word $w$ gives different complete
selected-event traces, then at some prefix $v$ of $w$ the full-summary
Moore outputs of $\delta_vx$ and $\delta_vy$ differ.

**Proof.** Both starts have origin $\bot$ and empty selected chain. Up to
the first letter at which the traces differ, equal selected-event outputs
make the origin and chain updates identical. At that letter, differing
complete records, or a record on only one side, make the updated origins
or chains differ: registration sets the origin, and each later selected
absorption appends its record. If just one side is registered, its displayed
summary differs from $\bot$; if both are registered, their displayed
summaries include the differing origin or chain. Either way, the prefix
ending at that letter distinguishes the Moore outputs. $\square$

For the full-summary observer, the empty word separates unequal registered
summaries. Corollary 5.4 and Lemma 6.1 separate distinct members of
$\mathcal R_n$ under this observer as well. All permanently unregistered
states display $\bot$ under every continuation. A member of
$\mathcal R_n$ is distinguished from them by a registration probe; a
registered state is displayed distinctly from $\bot$ already at the empty
word. Hence

$$
\boxed{Q_n^{\mathrm{full}}=s_n+R_n+1.}
\tag{6.2}
$$

The registered rank-one states are *not* merged into the full-summary
sink: their current summaries are displayed. The distinction between
(6.1) and (6.2) is entirely due to the declared observation contracts.

## 7. Counts, asymptotics, and the explicit coalescence graph

Substituting Proposition 3.3 into Theorem 1 gives

$$
\boxed{
Q_n^{\mathrm{future}}
=1+n\binom{2n-4}{n-3}
 +2(2n-3)\binom{2n-4}{n-2}-n(n-1).}
\tag{7.1}
$$

For the first growth base, put $m=n-2$ and write

$$
R_n=n\binom{2m}{m-1}
=n\frac{m}{m+1}\binom{2m}{m},
\qquad
A_n=2(2m+1)\binom{2m}{m}-n(n-1).
$$

Since $\binom{2m}{m}\sim4^m/\sqrt{\pi m}$, the polynomial term in
$A_n$ is negligible and the two contributions are, separately,

$$
R_n\sim\frac{1}{16\sqrt\pi}\sqrt n\,4^n,
\qquad
A_n\sim\frac{1}{4\sqrt\pi}\sqrt n\,4^n.
$$

Their sum gives

$$
Q_n^{\mathrm{future}}
\sim\frac{5}{16\sqrt\pi}\sqrt n\,4^n.
\tag{7.2}
$$

The upstream complete-summary theorem [@chenAbsorption2026] gives, with
$m=n-2$,

$$
s_n=n\left[\binom{2m}{m}
 +2\sum_{b=1}^{m}3^{b-1}\binom{2m-b}{m-b}\right]
\tag{7.3}
$$

The $9/2$ base and its constant can be read directly from this exact
formula. Let $B_m$ be the bracket in (7.3), defined also at $m=0$
by that expression. For $m\ge1$ it equals $s_{m+2}/(m+2)$. Set
$C(z)=(1-\sqrt{1-4z})/(2z)$. The standard identity
$\sum_{j\ge0}\binom{2j+b}{j}z^j=C(z)^b/\sqrt{1-4z}$ evaluates each
fixed-$b$ part of the sum.

$$
\begin{aligned}
\sum_{m\ge0}B_mz^m
&=\frac{1}{\sqrt{1-4z}}
  \left(1+2\sum_{b\ge1}3^{b-1}(zC(z))^b\right)\\
&=\frac{1}{\sqrt{1-4z}}
  \frac{1-zC(z)}{1-3zC(z)}.
\end{aligned}
\tag{7.3a}
$$

Inside $|z|<1/4$, the denominator has a single zero at $z=2/9$.
At that point $\sqrt{1-4z}=1/3$ and $zC(z)=1/3$, so the principal
part of (7.3a) is $(1-\tfrac92z)^{-1}$. Subtracting it leaves a
function analytic on $|z|<1/4$; Cauchy's estimate on any circle with
$2/9<|z|<1/4$ shows $B_m\sim(9/2)^m$. Hence

$$
s_n\sim n\left(\frac92\right)^{n-2}
=\frac{4n}{81}\left(\frac92\right)^n.
\tag{7.3b}
$$

It follows from (6.2) and the smaller exponential base of $R_n$ that

$$
Q_n^{\mathrm{full}}\sim s_n,
\qquad
\boxed{
\frac{Q_n^{\mathrm{full}}}{Q_n^{\mathrm{future}}}
\sim\frac{64\sqrt\pi}{405}\sqrt n
\left(\frac98\right)^n.}
\tag{7.4}
$$

Thus the two minimal right congruences on one generated state space have
different growth bases. This is not a lower bound on an arbitrary
implementation of either observation contract.

The gap probe also has a precise directed coalescence graph. Draw
$x\to y$ for distinct $x,y\in\mathcal R_n$ when their $V_x$ traces and
final placements agree. By Lemma 5.3,

$$
x\to y\quad\Longleftrightarrow\quad
y=x^{(h)}\text{ for a unique }1\le h<g(x).
\tag{7.5}
$$

It is acyclic because $g$ strictly decreases. Let $D_n(g)$ count
registerable placements of gap $g$ and $C_n$ count the directed edges of
this *specified probe* graph. To count $D_n(g)$, choose the site of
$\{0\}$ in $n$ ways. The $g-1$ sites before $\{1\}$ are holes; after
$\{1\}$ there are $n-g-1$ available sites for $t$ outside packets.
Cutting the $n-2$ outside atoms into $t$ nonempty source intervals gives
$\binom{n-3}{t-1}$ choices, and placing them in positive order gives
$\binom{n-g-1}{t}$ choices. Vandermonde's identity yields

$$
D_n(g)
=n\sum_{t=1}^{n-g-1}
\binom{n-3}{t-1}\binom{n-g-1}{t}
=n\binom{2n-g-4}{n-g-2},
\qquad 1\le g\le n-2.
\tag{7.6}
$$

Each source vertex of gap $g$ has exactly $g-1$ distinct outgoing
comparison states. Therefore

$$
\begin{aligned}
C_n
&=\sum_{g=1}^{n-2}(g-1)D_n(g)\\
&=n\binom{2n-4}{n-4}
=\frac{n-3}{n}R_n,
\end{aligned}
\tag{7.7}
$$

with $C_3=0$.

For the weighted step, put $m=n-2$ and $j=m-g$.
Hockey-stick summation and
$j\binom{m+j}{j}=(m+1)\binom{m+j}{j-1}$ give, for $m\ge2$,

$$
\begin{aligned}
\frac{C_n}{n}
&=\sum_{j=0}^{m-1}(m-1-j)\binom{m+j}{j}\\
&=(m-1)\binom{2m}{m-1}
  -(m+1)\binom{2m}{m-2}\\
&=\binom{2m}{m-2}.
\end{aligned}
\tag{7.7a}
$$

Because $R_n/n=\binom{2m}{m-1}$ and
$\binom{2m}{m-2}/\binom{2m}{m-1}=(m-1)/(m+2)$, this is precisely
the ratio $(n-3)/n$ in (7.7). Equivalently, the mean nonidentity
outdegree of a uniformly chosen $x\in\mathcal R_n$ is $(n-3)/n<1$.
For each fixed positive integer $g$,

$$
\frac{D_n(1)}{R_n}=\frac{n-1}{2n-4},
\qquad
\frac{D_n(g+1)}{D_n(g)}
=\frac{n-g-2}{2n-g-4},
$$

so $D_n(g)/R_n\to2^{-g}$. Since $\sum_{g\ge1}2^{-g}=1$, the gap
distribution converges to the geometric law of parameter $1/2$. These
statements concern $V_x$ and do not classify coalescence under other words.

## 8. Finite-state checks and scope

The accompanying finite-state control package computes both right congruences
for $n=3,4,5$, verifies the placement counts and normal-form classification,
and executes a distinguishing word for one representative of every pair of
distinct quotient keys. An independently implemented packet update checks
every raw transition. These computations are finite consistency checks; the
all-parameter results follow from the proofs above. The complete-summary
count $s_n$ is imported from [@chenAbsorption2026].

The theorem concerns the fixed adjacent pair, the complete selected-event
alphabet, and unrestricted future words. It does not identify a quotient
for truncated event records, other selected source sets, arbitrary defects,
shortest distinguishing words, reset bounds, or typed transfer semantics.

## 9. Conclusion

The future-event and full-summary observers induce different minimal right
congruences on the same generated packet system, with respective exponential
growth bases $4$ and $9/2$. The exact gap-probe coalescence fiber identifies
which registerable starts share its terminal event and placement; together
with the registered sweep, it yields distinguishing words of length at most
$6n-10$ for every inequivalent future-event pair. Thus the minimal-state cost
of retaining complete registered histories separates from the state
sufficient to predict future selected events, even as pairwise separation
remains constructive and linear in $n$.

## References
