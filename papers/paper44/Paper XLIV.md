# Prefix Memory and the Growth Spectrum of Event Observers

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XLIV | Version 1.0**

*This paper is Paper XLIV (version 1.0) of the RIME program. It classifies
prefix-memory event observers on the fixed circular action and determines
their exact finite quotients and asymptotic growth spectrum.*

## Abstract {.unnumbered}

We study how retaining an initial segment of an event history changes
the minimal predictive state of a circular coalescence system. The raw
actions are rotation and one adjacent collapse, started from placed
singletons, with registration of a fixed source pair. A depth-$j$
observer retains the registration origin and the first $j$ complete
selected absorption records, and observes every subsequent selected
event. Using the actual chain and placement-fibre classification, we
give the exact minimal quotient for every positive depth. The finite
classification and exact quotient cardinalities are formalized in
Lean 4; the asymptotic results are proved separately. For fixed
$j$, its state count is asymptotic to
$5\,2^j\sqrt n\,4^n/(16\sqrt\pi)$. For
$j=\lfloor\theta n\rfloor$, the exponential rate increases strictly
from $4$ to $9/2$ on $0<\theta<1/3$ and equals $9/2$ for
$1/3\le\theta<1$. A uniform comparison with a truncated binomial sum
proves the growth limit, including the threshold and integer rounding.
Every positive sublinear depth has base $4$. Above the critical density,
the prefix and complete-summary state counts are asymptotically equal,
with an exponentially vanishing relative deficit. At the critical density,
a square-root window has a Gaussian transition profile, and the quotient
ratio at depth $\lfloor n/3\rfloor$ tends to $1/2$. Thus the same actual
dynamics supports strictly intermediate observer-state growth rates,
with a resolved critical transition, and the full exponential rate can
occur before the observer retains the full history.

**Keywords:** event history; prefix memory; observer-relative state
minimization; circular coalescence; exponential growth spectrum

## 1. Introduction

How much of an old event history must a predictive observer retain?
The answer depends on the report being requested. In a circular
registered absorption system, the future selected-event observer can
forget the old selected chain once the current placement is known,
whereas a complete-summary observer reports that chain. Their exact
minimal state counts have exponential bases $4$ and $9/2$, respectively
[@chenPaper43v1]. We investigate the observations between these two
contracts by retaining a prefix of the old chain.

The retained data are complete source-addressed events, not only their
number or a sequence of left/right signs. A depth-$j$ observer reads
the origin, the first $j$ selected records, and whether the retained
prefix is still shorter than $j$. It also observes all future selected
events under every common raw continuation. For fixed $j$, this extra
memory changes a leading constant but not the growth base. At linear
depth the rate changes: for $j=\lfloor\theta n\rfloor$ it is

$$
\lambda(\theta)=
\begin{cases}
\displaystyle\frac{2^{2+\theta}}
 {(1+\theta)^{1+\theta}(1-\theta)^{1-\theta}},
 &0<\theta\le1/3,\\[2mm]
9/2,&1/3\le\theta<1.
\end{cases}
\tag{1.1}
$$

In particular the open interval $(4,9/2)$ consists of actual growth
rates of declared observers on the same dynamics. The plateau at
$1/3$ is a rate statement, not equality of the underlying state
quotients. Even full selected-history memory in our contract does not
observe the physical phase of a rank-one packet.

For strictly supercritical depth we prove more than equality of growth
bases: $Q_n^{[\lfloor\theta n\rfloor]}/Q_n^{\rm full}\to1$.
The proof counts complete summaries by selected-chain length and bounds
the loss caused by long chains and forgotten terminal phases separately.
At critical density the same chain-length profile gives a central-limit
transition when the retained depth is shifted by order $\sqrt n$.

The mechanism has two parts. The exact quotient separates future
behaviour from retained reports. Counting the reports requires
distinguishing a saturated prefix, which may have an unobserved past
continuation, from a short prefix that is the entire current chain.
A uniform reduction then replaces the resulting coefficients by a
truncated binomial sum up to polynomial factors. Its entropy maximum
gives the rate in (1.1).

Sequential-machine equivalence supplies the general language of right
indistinguishability [@mealy1955; @moore1956; @nerode1958]. We use,
rather than reprove, the actual source-addressed chain and fibre
classification of [@chenPaper41v1] and the constructive future
separation theorem of [@chenPaper43v1, Theorem 6.2]. The new problem here is the
prefix-indexed family of observation contracts, its exact count for
every depth, and its uniform growth spectrum. The state numbers concern
this model and these observers; the parameter $j$ is a retained-event
depth, not a raw-word budget.

## 2. Dynamics, Observers and Imported Structure

Fix $n\ge3$, $Q=\mathbb Z/n\mathbb Z$, and source atoms
$\Omega=\{0,\ldots,n-1\}$. A placement $P$ assigns disjoint nonempty
atom packets to occupied sites, covering $\Omega$. The singleton seed
is $P_0(q)=\{q\}$. The site actions are

$$
p(q)=q+1,\qquad d(1)=0,\quad d(q)=q\quad(q\ne1).
\tag{2.1}
$$

Packets follow these maps and merge by union when their images coincide.
Words are chronological. An effective fusion has complete ordered record

$$
\rho=(d,0,1,U,V,0,U\cup V),
\tag{2.2}
$$

where $U,V$ occupied ports $0,1$ just before the fusion.

Set $F=\{0,1\}$. The first fusion that creates exactly $F$ is its
registration, with origin $o$. Once registered, a selected absorption
is an effective fusion involving the current packet containing $F$,
called the carrier. Unrelated mergers do not append a selected record.
We use the full registration record (2.2) as the semantic origin $o$.
The compact origin $(d,(0,U),(1,V),0)$ used in the prior representation
and control code is a lossless projection: its omitted result is the
fixed set $F=U\cup V$. Reinserting that field recovers $o$.
Write $x=(P,o,A)$ for the current placement, origin and selected chain.
Let $X_n$ be the set of all such states reached from the singleton seed
by finite actual words. The visible output alphabet contains
$\mathsf{null}$, registration outputs $\mathsf{reg}(\rho)$ and
selected-absorption outputs $\mathsf{abs}(\rho)$, where $\rho$ is a
complete record (2.2). On a letter $a$, the output $\epsilon(x,a)$ is
$\mathsf{reg}(\rho)$ when that letter first creates $F$,
$\mathsf{abs}(\rho)$ when it fuses an already registered carrier with
another packet, and $\mathsf{null}$ otherwise. In particular, registration
itself is visible; rotations, nonfusing defects and unrelated fusions
emit null. Registration has result $F$, whereas a selected absorption
has result strictly containing $F$, so the two event kinds are also
recoverable from their full records. Write $\delta_a x$ for the actual
successor. The trace $\operatorname{Trace}(x,w)$ retains one tagged
output, including nulls, per letter of the common raw word $w$.

For $j\ge1$ define the retained label

$$
L_j(x)=
\begin{cases}
\bot,&x\text{ unregistered},\\
(o,\operatorname{take}_j A,\mathsf{short}),&|A|<j,\\
(o,\operatorname{take}_j A,\mathsf{saturated}),&|A|\ge j.
\end{cases}
\tag{2.3}
$$

The short marker reports the current chain length, not that future
absorptions have ceased. The registration origin is unique for this
pair when $n\ge3$.

For completeness, define the label update $\mathsf U_j$ on reachable
label/output pairs. Let $\mathsf{flag}_j(k)$ be $\mathsf{short}$ for
$k<j$ and $\mathsf{saturated}$ for $k\ge j$. Then

$$
\begin{aligned}
\mathsf U_j(z,\mathsf{null})&=z,\\
\mathsf U_j(\bot,\mathsf{reg}(\rho))&=(\rho,(),\mathsf{short}),\\
\mathsf U_j((o,B,\mathsf{short}),\mathsf{abs}(\rho))
  &=(o,B\mathbin{\|}[\rho],\mathsf{flag}_j(|B|+1)),\\
\mathsf U_j((o,B,\mathsf{saturated}),\mathsf{abs}(\rho))
  &=(o,B,\mathsf{saturated}).
\end{aligned}
$$

Here $B\mathbin{\|}[\rho]$ appends one record. Registration initializes
the origin but does not enter the absorption chain; its new chain is
empty and hence short because $j\ge1$. These cases cover every actual
transition, and the definitions give
$L_j(\delta_a x)=\mathsf U_j(L_j(x),\epsilon(x,a))$.

Two states are equivalent for this observer if, under every common raw
word, their selected-event traces and all retained-label reports agree,
including the label at the empty prefix.
Equivalently,

$$
x\equiv_j y
\quad\Longleftrightarrow\quad
x\equiv_{\rm future}y\ \text{ and }\ L_j(x)=L_j(y).
\tag{2.4}
$$

For the right-to-left implication, assume equal initial labels and
equal future traces. At each letter the outputs agree, so the displayed
update rule gives equal successor labels. Induction keeps the labels
equal at every prefix of every common continuation. For the converse,
the empty prefix gives equal current labels and agreement of all
selected-event traces is exactly future equivalence. Let $Q_n^{[j]}$ count these
classes on $X_n$, and let $Q_{n,\rm reg}^{[j]}$ count them on the
successor-closed registered subset.

We record precisely the inherited structural results used below. Put
$N=n-2$.

1. **Actual chains and fibres** [@chenPaper41v1, Theorems 3.1 and 4.2]. A selected chain
   is uniquely encoded by nonzero checkpoints among $1,\ldots,N$ and
   their L/R port bindings. If its final carrier adds $r<N$ atoms to
   $F$, that carrier is one of the $r+1$ proper arcs extending $F$.
   For a proper carrier $C$, list its source complement in the positive
   linear order starting immediately after $C$ and ending just before it.
   Partition that list into nonempty consecutive intervals. The blocks
   $C$ and those outside intervals must occur at their occupied physical
   sites in the induced positive cyclic block order. For each fixed
   compatible complete chain, every placement satisfying these two
   conditions is actually reachable. The number of these placements is
   $n\binom{2N-r}{N-r}$, independent of the chain. At a full carrier
   each complete chain has $n$ actual physical phases. These are
   statements about actual words, not arbitrary record lists.
2. **Future equivalence** [@chenPaper43v1, Theorem 6.1 and Proposition 3.3]. All permanently
   unregistrable states and registered rank-one states are silent and
   form one future class. Every registerable unregistered placement
   is its own class. Registered nonterminal states are equivalent
   exactly when their current placements agree. The number of
   registerable placements is
   $R_n=n\binom{2N}{N-1}$. Constructive common-suffix probes establish
   the separation of these classes.

The comparator is the **complete-summary Moore observer**, whose current
report is $\bot$ before registration and $(P,o,A)$ afterwards. Write
$s_n$ for the number of actual complete registered summaries, including
terminal phase. Its minimal quotient count is
$Q_n^{\rm full}=1+R_n+s_n$ [@chenPaper43v1]: registered summaries
are separated by their current report, while the unregistered region
has the same dead and registerable placement classes as above.

Here a checkpoint is the cumulative number $b=|C'|-2$ of atoms
absorbed beyond $F$, read from that record's result $C'$. If the
preceding carrier is at port $0$, the record has binding R and
absorbs a prefix of the positive ordered complement; at port $1$
it has binding L and absorbs a suffix. The checkpoint increment
is the size of that partner. Starting at $F$, these increments and
bindings recover the complete ordered records. When only two
packets remain the possible partner sets coincide, but the two
port bindings still give different records.

Only the positive-depth contracts (2.3) are used in the main theorems.
At depth zero we use the separate future-only convention, without a
registration label. If that label were kept at depth zero, it would
split the silent class in two, changing the whole-domain count by one.

## 3. Exact Prefix Classes

The extension of a proper carrier has $a$ added atoms on its left and
$b$ on its right, with $a+b=r<N$. Complete ordered records recover
these additions and the parent-to-port binding at each checkpoint.
They therefore distinguish L and R even when the last two packets
have identical possible partner sets.

### Lemma 3.1. Proper-Carrier Prefix Labels

Sum the number of compatible retained labels over all $r+1$ carrier
arcs of extension $r$. The result is

$$
c_{0,j}=1,\qquad
c_{r,j}=2^j\binom{r+1}{j+1}
       +\sum_{\ell=1}^{j-1}2^\ell\binom{r-1}{\ell-1}
       \quad(r\ge1).
\tag{3.1}
$$

Binomial coefficients with an index outside their range are zero.

**Proof.** First count saturated prefixes for a fixed arc $(a,b)$.
If $u$ of the $j$ records are left absorptions, their order has
$\binom ju$ possibilities. Their cumulative endpoints on the left
form a $u$-element subset of $\{1,\ldots,a\}$; the right endpoints
form a $(j-u)$-element subset of $\{1,\ldots,b\}$. These data recover
every ordered record. Conversely every such choice is a legal prefix,
which may leave some of either side for unobserved past absorptions.
The fixed-arc count is

$$
\sum_{u=0}^j\binom ju\binom au\binom b{j-u}.
\tag{3.2}
$$

For each $u$, sum over $a+b=r$. The convolution is

$$
\sum_{a=0}^r\binom au\binom{r-a}{j-u}
    =\binom{r+1}{j+1}.
\tag{3.3}
$$

One proof chooses a $(j+1)$-subset of $\{0,\ldots,r\}$ and
designates its $(u+1)$st element as $a$. Choosing the smaller and
larger elements gives the summand. Summing $\binom ju$ yields the
first term of (3.1).

For a short prefix of length $\ell<j$, the retained list is the whole
current chain, so its last checkpoint is exactly $r$. For $r>0$,
choose $\ell-1$ earlier checkpoints and one of two port bindings
at each event. This gives $2^\ell\binom{r-1}{\ell-1}$. Its side
increments determine one carrier arc; summing across arcs therefore
counts it once. The empty chain occurs only at $r=0$.

Every counted prefix is actual at every placement compatible with its
fixed carrier arc. For a saturated prefix, append its remaining
nonempty left and right increments in any fixed order, then apply
the inherited complete-chain fibre theorem. For a short prefix, use
its complete chain directly. Conversely an actual chain determines
all the chosen endpoints and bindings. This proves both counting
and attainability. $\square$

### Lemma 3.2. Terminal Prefix Labels

At a full carrier the number of retained labels is

$$
T_{N,j}=2^j\binom Nj
       +\sum_{\ell=1}^{j-1}2^\ell\binom{N-1}{\ell-1}.
\tag{3.4}
$$

**Proof.** A saturated prefix chooses $j$ checkpoints from
$1,\ldots,N$ and their $j$ bindings. It can be completed to the
full carrier if it does not already end there. A short chain must
end at $N$, giving the second term. The actual chain theorem
realizes these choices. With two packets left, absorbing the whole
complement in port direction L or R produces different ordered
records, so both choices remain in the count. Physical terminal
phase is not part of the retained label. $\square$

### Theorem 3.3. Exact Minimal Quotient at Every Positive Depth

Define

$$
A_n^{[j]}=n\sum_{r=0}^{N-1}c_{r,j}\binom{2N-r}{N-r}.
\tag{3.5}
$$

For every $n\ge3$ and $j\ge1$,

$$
Q_n^{[j]}=1+R_n+T_{N,j}+A_n^{[j]},\qquad
Q_{n,\rm reg}^{[j]}=T_{N,j}+A_n^{[j]}.
\tag{3.6}
$$

The normal-form keys are: one key for permanently unregistrable
states; $P$ for registerable unregistered states; $(P,L_j)$ for
registered nonterminal states; and $L_j$ for registered terminals.

More explicitly, let $\mathscr R_n$ be the actual registerable
unregistered placements, $\mathscr T_{N,j}$ the actual terminal
label image, and $\mathscr P(C,L)$ the actual placements compatible
with a proper carrier $C$ and retained label $L$. There is an
equivalence

$$
X_n/{\equiv_j}\ \simeq\
\{\star\}\ \sqcup\ \mathscr R_n\ \sqcup\ \mathscr T_{N,j}\
\sqcup\!
\coprod_{C\ {\rm proper}}\ \coprod_{L\ {\rm compatible\ with}\ C}
\mathscr P(C,L).
$$

The parameter spaces use actual attainable labels and literal
placements. Equality in this normal form is equivalent to the
all-word observer equivalence, and the two encoding/decoding
composites are identities. Decoding chooses a realizing history
but returns its observer class; no uniqueness of the raw word
is required.

**Proof.** Apply (2.4) to the inherited future classes. In registered
nonterminal classes, different placements remain separated by a
future suffix, and different labels are separated by the current
report. Equal placement and label give both equal future behaviour
and equal current reports. At rank one there are no future selected
events, so equality is exactly equality of labels. Registered labels
differ from $\bot$, separating these terminal classes from the dead
unregistered class. The inherited preregistration classification
is unchanged.

For a fixed proper carrier and compatible label, Lemma 3.1 supplies
exactly the entire placement fibre of size
$n\binom{2N-r}{N-r}$. This counts placements over a label, not
histories over one placement. Summing labels over carrier arcs gives
(3.5). Lemma 3.2 supplies the terminal count, and the other two
regions give $R_n$ and one. Restricting to the registered domain
removes just those two regions. $\square$

For $r\ge1$, the first two depths give

$$
c_{r,1}=r(r+1),\qquad
c_{r,2}=2+\frac23r(r^2-1),
\tag{3.7}
$$

whereas $c_{0,j}=1$ at every depth. The terminal counts are
$T_{N,1}=2N$ and $T_{N,2}=2+2N(N-1)$.

### Corollary 3.4. Full Prefix Memory Still Forgets Terminal Phase

Let $s_n$ be the complete registered-summary count. For $j\ge N$,

$$
Q_n^{[j]}=1+R_n+s_n-(n-1)\,2\,3^{N-1}.
\tag{3.8}
$$

**Proof.** Every chain is now retained in full. There are
$2\,3^{N-1}$ complete chains ending at checkpoint $N$. Each has
$n$ phases in a complete summary and one terminal prefix key here.
All nonterminal placements remain literal. The only subtraction
is therefore $n-1$ per full-carrier chain. $\square$

### Corollary 3.5. Depth Refinement and Stabilization

For $1\le j<k$, the identity on actual states induces a surjection
$X_n/{\equiv_k}\twoheadrightarrow X_n/{\equiv_j}$. Both the
whole-domain and registered-domain counts strictly increase from
depth $j$ to $j+1$ whenever $1\le j<N$. Their equivalence
relations stabilize for $j\ge N$.

**Proof.** The depth-$j$ label is recovered from the depth-$k$
label by truncating the records and recomputing the short/saturated
marker. The future-event contract is unchanged, so (2.4) gives
$x\equiv_k y\Rightarrow x\equiv_j y$.

For strictness, take the same first $j$ singleton R absorptions,
then absorb the entire remaining complement with final port binding
L or R. Since $j<N$, the carrier before that last event is proper.
The inherited chain realization theorem supplies both actual terminal
states. Their depth-$j$ labels agree and their futures are silent,
but their depth-$(j+1)$ labels contain different complete final
records. They therefore give two distinct finer classes inside one
coarser class, in either state domain.

Every chain has length at most $N$. For $j\ge N$ its label
determines the whole chain, and the marker is determined by that
chain and $j$. Equality of labels consequently has the same
meaning at every such depth. Equation (2.4) proves stabilization.
$\square$

## 4. Fixed-Depth Asymptotics

### Lemma 4.1. A Weighted Label Sum

For each fixed $j\ge1$,

$$
\sum_{r\ge0}c_{r,j}2^{-r}=5\,2^j-1.
\tag{4.1}
$$

**Proof.** For $|x|<1$ the two relevant sums are

$$
\sum_{r\ge1}\binom{r+1}{j+1}x^r
 =\frac{x^j}{(1-x)^{j+2}},\qquad
\sum_{r\ge\ell}\binom{r-1}{\ell-1}x^r
 =\left(\frac{x}{1-x}\right)^\ell.
\tag{4.2}
$$

They follow by differentiating the geometric series, or by the
ordinary generating function for compositions. At $x=1/2$, the
empty-chain contribution is $1$, the saturated contribution is
$2^{j+2}$, and the short contributions sum to $2^j-2$. $\square$

### Theorem 4.2. Every Fixed Positive Depth Has Base Four

For fixed $j\ge1$, as $n\to\infty$,

$$
Q_n^{[j]}\sim\frac{5\,2^j}{16\sqrt\pi}\sqrt n\,4^n,
\qquad
Q_{n,\rm reg}^{[j]}\sim
\frac{5\,2^j-1}{16\sqrt\pi}\sqrt n\,4^n.
\tag{4.3}
$$

**Proof.** Put $B_N=\binom{2N}{N}$. For $0\le r\le N$,

$$
\frac{\binom{2N-r}{N-r}}{B_N}
 =\prod_{i=0}^{r-1}\frac{N-i}{2N-i}\le2^{-r},
\tag{4.4}
$$

and for fixed $r$ this tends to $2^{-r}$. The coefficients $c_{r,j}$
have polynomial growth in $r$ for fixed $j$. Extending the summand
by zero for $r\ge N$, (4.4) gives a summable bound, so dominated
convergence and Lemma 4.1 imply

$$
\frac{A_n^{[j]}}{nB_N}\longrightarrow5\,2^j-1.
\tag{4.5}
$$

The terminal contribution is polynomial in $N$ at fixed depth and
is negligible on this scale. Moreover
$R_n/(nB_N)=N/(N+1)\to1$. Stirling's formula [@nistDLMF] gives the
central-binomial asymptotic $B_N\sim4^N/\sqrt{\pi N}$, so

$$
nB_N\sim\frac{\sqrt n\,4^n}{16\sqrt\pi},
\tag{4.6}
$$

since $N=n-2$. Combining the contributions proves (4.3). $\square$

For example the registered coefficients are $9$ and $19$ at depths
one and two, while the whole-domain coefficients are $10$ and $20$.
The fixed-depth result does not supply a uniform estimate for growing
$j$; that requires a separate argument.

## 5. A Uniform Truncated-Binomial Reduction

Set

$$
S_{r,j}=\sum_{\ell=0}^{\min(j,r)}2^\ell\binom r\ell,
\qquad
Z_{N,j}=\sum_{r=0}^{N-1}\binom{2N-r}{N-r}S_{r,j}.
\tag{5.1}
$$

### Lemma 5.1. Uniform Polynomial Comparison

For every $r\ge0$ and $j\ge1$,

$$
\frac{S_{r,j}}{r+1}\le c_{r,j}\le(r+2)S_{r,j}.
\tag{5.2}
$$

Consequently

$$
\frac{Z_{N,j}}{N}\le\frac{A_n^{[j]}}n
                     \le(N+1)Z_{N,j}.
\tag{5.3}
$$

**Proof.** At $r=0$ both coefficients are one. For $r\ge1$,
the saturated term in (3.1) is at most
$(r+1)2^j\binom rj$ when $j\le r$, and is zero otherwise.
Every short term is at most its corresponding term in $S_{r,j}$.
This gives the upper bound.

For $1\le\ell<j$ use
$\binom{r-1}{\ell-1}=(\ell/r)\binom r\ell$.
When $j\le r$, also use
$\binom{r+1}{j+1}\ge\binom rj$. Together these give
$S_{r,j}-1\le r c_{r,j}$, including $j>r$.
There is at least one compatible label, so $c_{r,j}\ge1$ and
$S_{r,j}\le(r+1)c_{r,j}$. Multiplying by the placement weight
and using $r+1\le N$, $r+2\le N+1$ proves (5.3).
$\square$

### Lemma 5.2. One-Dimensional Summation

For all $N\ge1$ and $j\ge1$,

$$
Z_{N,j}=\sum_{\ell=0}^{\min(j,N)}2^\ell
 \left[\binom{2N+1}{N-\ell}-\binom N\ell\right].
\tag{5.4}
$$

**Proof.** Exchange the two finite sums in (5.1). For fixed $\ell$,
append the term $r=N$ and apply the convolution

$$
\sum_{r=\ell}^{N}\binom r\ell\binom{2N-r}{N}
 =\binom{2N+1}{N-\ell}.
\tag{5.5}
$$

To prove (5.5), choose an $(N+\ell+1)$-element subset of a
$(2N+1)$-element ordered set, and let its $(\ell+1)$st member be
at position $r+1$. Choose $\ell$ members before it and $N$ after
it. Complementing the chosen subset gives the right-hand binomial
coefficient. The appended term is $\binom N\ell$.
$\square$

Write $\mathcal U_{N,j}=\sum_{\ell\le\min(j,N)}
2^\ell\binom{2N+1}{N-\ell}$. The subtracted sum in (5.4) is
at most $3^N$, whereas $\mathcal U_{N,j}$ contains
$\binom{2N+1}N\ge B_N\ge4^N/(2N+1)$. Therefore

$$
0\le1-\frac{Z_{N,j}}{\mathcal U_{N,j}}
 \le(2N+1)\left(\frac34\right)^N=o(1)
\tag{5.6}
$$

uniformly in positive $j$. Also $T_{N,j}\le3^N$ and
$R_n\le nB_N$. Since $Z_{N,j}\ge B_N$, equations (3.6),
(5.3) and (5.6) show that $\mathcal U_{N,j}$ determines the exponential
rate of both observer counts, with only polynomial factors and an
exponentially negligible subtraction.

## 6. The Linear-Memory Growth Spectrum

Let $H(x)=-x\log x-(1-x)\log(1-x)$, with $0\log0=0$.
We use the elementary bounds

$$
\frac{e^{M H(k/M)}}{M+1}\le\binom Mk\le e^{M H(k/M)}
\qquad(0\le k\le M).
\tag{6.1}
$$

For $0<k<M$, take success probability $k/M$ in the binomial
distribution. Its $k$th probability is a mode, at least $1/(M+1)$
and at most one. Writing that probability explicitly gives (6.1).
The endpoint cases are immediate.

### Theorem 6.1. Exact Exponential Growth Spectrum

Fix $0<\theta<1$ and put $j_n=\lfloor\theta n\rfloor$ on the
cofinite range where $j_n\ge1$. Then both limits exist, and

$$
\lim_{n\to\infty}(Q_n^{[j_n]})^{1/n}
 =\lim_{n\to\infty}(Q_{n,\rm reg}^{[j_n]})^{1/n}
 =\lambda(\theta),
\tag{6.2}
$$

where $\lambda$ is given by (1.1). In particular
$4<\lambda(\theta)<9/2$ for $0<\theta<1/3$.

**Proof.** With $N=n-2$ and $\ell/N\to\beta$, the rate of the
summand in $\mathcal U_{N,j}$ is

$$
G(\beta)=\beta\log2+2H\left(\frac{1-\beta}{2}\right)
 =(2+\beta)\log2
 -(1+\beta)\log(1+\beta)-(1-\beta)\log(1-\beta).
\tag{6.3}
$$

Indeed (6.1) bounds its logarithm by
$\ell\log2+(2N+1)H((N-\ell)/(2N+1))$, with error at most
$\log(2N+2)$. After division by $N$ this expression converges
uniformly to $G(\ell/N)$: entropy is uniformly continuous on
$[0,1]$, and the change in its argument is uniformly $O(1/N)$.
There are at most $N+1$ summands. The logarithm of their sum differs
from that of the largest by at most $\log(N+1)$.

Since $j_n/N\to\theta$, compactness gives the upper rate
$\max_{0\le\beta\le\theta}G(\beta)$. Conversely every
$0\le\beta<\theta$ can be approached by an admissible integer
$\ell_N$; continuity supplies the endpoint by approximation.
Thus upper and lower rates agree. More explicitly at the threshold
$\theta=1/3$, $\ell_N=\lfloor N/3\rfloor\le
\lfloor n/3\rfloor$ is admissible and $\ell_N/N\to1/3$.

Differentiation in the interior gives

$$
G'(\beta)=\log\frac{2(1-\beta)}{1+\beta}.
\tag{6.4}
$$

Hence $G$ increases strictly from $G(0)=\log4$ up to
$\beta=1/3$, where $G(1/3)=\log(9/2)$, and decreases after
that point. The constrained maximum is at
$\beta=\min(\theta,1/3)$. Exponentiation gives (1.1), and the
uniform comparison of Section 5 transfers it to both quotients.
Finally $N/n\to1$, so the same limit uses the exponent $1/n$.
$\square$

### Corollary 6.2. Positive Sublinear Memory

If $j_n\ge1$ eventually and $j_n=o(n)$, both observer counts have
exponential base $4$.

**Proof.** In the same uniform estimate every admissible
$0\le\ell/N\le j_n/N$ tends uniformly to zero. The maximum
rate is therefore $G(0)=\log4$, and the central summand gives
the matching lower bound. $\square$

The full rate is attained at memory density $1/3$, even though many
longer histories remain unidentified by that prefix. The next result
separately establishes asymptotic equality of counts above that density.

### Lemma 6.3. Complete Summaries by Selected-Chain Length

Let $h_{n,\ell}$ count complete registered summaries whose selected
chain has length $\ell$. For $0\le\ell\le N$,

$$
h_{n,\ell}=n\,2^\ell\binom{2N}{N-\ell},\qquad
s_n=n\sum_{\ell=0}^{N}2^\ell\binom{2N}{N-\ell}.
\tag{6.5}
$$

**Proof.** At $\ell=0$ the carrier is $F$, and its placement fibre
has size $n\binom{2N}N$. For $\ell\ge1$, group complete chains
by their last checkpoint $r$. There are
$2^\ell\binom{r-1}{\ell-1}$ chains, each with
$n\binom{2N-r}{N-r}$ placements. This includes $r=N$, where
the fibre is the $n$ full-carrier phases. The required convolution is

$$
\sum_{r=\ell}^{N}\binom{r-1}{\ell-1}\binom{2N-r}{N-r}
 =\binom{2N}{N-\ell}.
\tag{6.6}
$$

Choose an $(N+\ell)$-element subset of a $2N$-element ordered set
and designate its $\ell$th member as position $r$. Choose $\ell-1$
members before it and $N$ after it. Complementation gives the
right-hand side. The inherited actual chain/fibre classification
therefore proves (6.5) for actual summaries. $\square$

There is a useful exact reweighting. If $K$ has the auxiliary binomial
distribution $\operatorname{Bin}(2N,1/3)$, then

$$
\frac{h_{n,\ell}}{n(9/2)^N}=\Pr(K=N-\ell),\qquad
\frac{s_n}{n(9/2)^N}=\Pr(K\le N).
\tag{6.7}
$$

These identities describe a finite counting sum, not a random choice of
execution actions. Since

$$
\Pr(K>N)\le 2^{-N}\mathbb E[2^K]
 =2^{-N}(4/3)^{2N}=(8/9)^N,
\tag{6.8}
$$

we obtain the explicit lower bound
$s_n\ge n(9/2)^N[1-(8/9)^N]$.

### Corollary 6.4. Asymptotic Equality Above the Critical Density

Fix $1/3<\theta<1$ and $j_n=\lfloor\theta n\rfloor$. Then

$$
\frac{Q_n^{[j_n]}}{Q_n^{\rm full}}\longrightarrow1,
\qquad
\frac{Q_{n,\rm reg}^{[j_n]}}{s_n}\longrightarrow1.
\tag{6.9}
$$

More explicitly, fix any $\rho$ with $1/3<\rho<\theta$ and put
$\delta_\rho=\log(9/2)-G(\rho)>0$. For all sufficiently large $n$,
each relative deficit in (6.9) is nonnegative and at most

$$
\frac{(N+1)e^{-N\delta_\rho}
       +\frac23(2/3)^N}{1-(8/9)^N}.
\tag{6.10}
$$

**Proof.** Let $Q_n^{[\infty]}$ denote the full-prefix quotient of
Corollary 3.4. The map from full-summary classes to full-prefix
classes forgets only terminal phase. Its exact loss is

$$
D_n=(n-1)\,2\,3^{N-1}.
\tag{6.11}
$$

Under the further map to depth-$j$ classes, every full-prefix class
with chain length at most $j$ has a singleton fibre. Below depth $j$
the short label recovers the whole chain. At length exactly $j$,
the last retained record already gives the current carrier. A longer
chain with that prefix would strictly enlarge the carrier, so it
cannot have the same nonterminal placement; at a full carrier no
further absorption is possible. Thus these classes do not merge
with each other or with any longer-history class.

Set $L_{n,>j}=\sum_{\ell=j+1}^N h_{n,\ell}$, with an empty sum
equal to zero. The number of remaining full-prefix classes is at
most $L_{n,>j}$. Consequently

$$
0\le Q_n^{\rm full}-Q_n^{[j]}
 \le D_n+L_{n,>j}.
\tag{6.12}
$$

The same loss equals $s_n-Q_{n,\rm reg}^{[j]}$, because both
whole-domain counts contain the identical $1+R_n$ contribution.

Eventually $j_n\ge\rho N$. By (6.1), for
$\beta=\ell/N$,
$2^\ell\binom{2N}{N-\ell}\le e^{NG(\beta)}$.
The function $G$ decreases strictly on $(1/3,1]$, so

$$
L_{n,>j_n}\le n(N+1)e^{NG(\rho)}.
\tag{6.13}
$$

Divide (6.12) by $Q_n^{\rm full}\ge s_n$, or by $s_n$ for
the registered ratio. Use (6.8) and
$D_n/[n(9/2)^N]\le\frac23(2/3)^N$ to get (6.10).
Both terms in its numerator decay exponentially, proving (6.9).
$\square$

Distinct finite quotients can thus have asymptotically equal cardinality.
For $0<\theta<1/3$, Theorem 6.1 and (6.7)--(6.8) instead give
$Q_n^{[\lfloor\theta n\rfloor]}/Q_n^{\rm full}\to0$, by their
strictly different exponential bases. At the boundary, where the entropy
gap in (6.13) vanishes, the exact prefix count gives a Gaussian transition.

### Theorem 6.5. Critical Window for Prefix Depth

Fix $u\in\mathbb R$ and put

$$
j_n=\left\lfloor\frac n3+u\sqrt n\right\rfloor.
$$

For all sufficiently large $n$, $1\le j_n\le N$. Then

$$
\boxed{
\frac{Q_n^{[j_n]}}{Q_n^{\rm full}}\longrightarrow\Phi(3u/2),
\qquad
\frac{Q_{n,\rm reg}^{[j_n]}}{s_n}\longrightarrow\Phi(3u/2),
}
\tag{6.14}
$$

where $\Phi$ is the standard normal distribution function. In particular,

$$
\boxed{
\frac{Q_n^{[\lfloor n/3\rfloor]}}{Q_n^{\rm full}}
\longrightarrow\frac12.
}
\tag{6.15}
$$

Moreover, for every fixed $A>0$, with
$j_n(u)=\lfloor n/3+u\sqrt n\rfloor$, both limits hold uniformly at
Berry--Esseen rate; for all sufficiently large $n$, the indices satisfy
$1\le j_n(u)\le N$ simultaneously for $|u|\le A$:

$$
\boxed{
\begin{aligned}
\sup_{|u|\le A}\left|
\frac{Q_n^{[j_n(u)]}}{Q_n^{\rm full}}-\Phi(3u/2)\right|
&=O_A(n^{-1/2}),\\
\sup_{|u|\le A}\left|
\frac{Q_{n,\rm reg}^{[j_n(u)]}}{s_n}-\Phi(3u/2)\right|
&=O_A(n^{-1/2}).
\end{aligned}}
\tag{6.16}
$$

**Proof.** Fix $A>0$ and let $|u|\le A$ throughout. All estimates below
are uniform over this interval. Write

$$
H_{<j}=\sum_{\ell=0}^{j-1}h_{n,\ell},\qquad
U^{\rm short}_{N,j}=\sum_{\ell=1}^{j-1}2^\ell\binom{N-1}{\ell-1},
$$

and

$$
V_{N,j}=\binom{2N+1}{N-j}+\binom{2N+1}{N-j-1}
-\binom Nj-\binom N{j+1}.
$$

Splitting the coefficient $c_{r,j}$ in (3.1) into its stopped and
saturated-prefix terms, and applying (6.6), (5.5), and Pascal's identity,
gives the exact identity for $1\le j\le N$:

$$
Q_{n,\rm reg}^{[j]}
=H_{<j}-(n-1)U^{\rm short}_{N,j}+n2^jV_{N,j}+2^j\binom Nj.
\tag{6.17}
$$

For the stopped terms, the convolution is (6.6); the terminal stopped
labels restore one copy of $U^{\rm short}_{N,j}$. For the saturated terms, use
$\binom{r+1}{j+1}=\binom r{j+1}+\binom rj$ in (5.5), append the
$r=N$ terms, and subtract those two endpoint terms. This yields exactly
$V_{N,j}$.

In the window $j=N/3+O_A(\sqrt N)$, the binomial local estimate gives,
uniformly,
\[
2^j\binom{2N+1}{N-j}
+2^j\binom{2N+1}{N-j-1}
=O_A\!\left(\frac{(9/2)^N}{\sqrt N}\right).
\]
Indeed, with $x=(N-j)/(2N+1)$, Taylor expansion at $x=1/3$ gives
$j\log 2+(2N+1)H(x)=N\log(9/2)+O_A(1)$: the order-$\sqrt N$
terms cancel because $H'(1/3)=\log 2$. Stirling's local prefactor
then contributes $O(N^{-1/2})$. The adjacent binomial coefficient has
the same estimate, since its argument shifts by only $O(N^{-1})$.
Also $U^{\rm short}_{N,j}\le2\,3^{N-1}$ and both endpoint terms
$2^j\binom Nj$ and $2^j\binom N{j+1}$ are at most $3^N$.
After multiplication by their coefficients in (6.17), these terms divided
by $s_n$ are $O((2/3)^N)$.
Since $s_n\sim n(9/2)^N$, (6.17) implies
\[
\frac{Q_{n,\rm reg}^{[j]}}{s_n}
=\frac{H_{<j}}{s_n}+O_A(N^{-1/2}).
\]
The denominator replacement is valid at this rate: (6.7)--(6.8) give
$s_n/[n(9/2)^N]=1+O((8/9)^N)$. The whole-domain ratio differs from the
registered-domain ratio by $O((R_n+1)/s_n)$, uniformly in $u$, because
$0\le Q_{n,\rm reg}^{[j]}\le s_n$. The exact formula
$R_n=n\binom{2N}{N-1}$ and Stirling's estimate give
$R_n/s_n=O(N^{-1/2}(8/9)^N)$.

Let $K\sim\operatorname{Bin}(2N,1/3)$. By (6.7),
$H_{<j}/s_n=\Pr(K>N-j\mid K\le N)$. The complement of the conditioning
event has probability at most $(8/9)^N$ by (6.8), so conditioning changes
this tail by an exponentially small amount. The Berry--Esseen inequality
[@berry1941; @esseen1942]
for the standardized binomial variable gives a uniform $O(N^{-1/2})$
error. Its threshold satisfies
\[
\frac{N-j_n(u)-2N/3}{(2/3)\sqrt N}
=-\frac{3u}{2}+O_A(N^{-1/2}),
\]
where the error includes the floor in $j_n(u)$ and
$\sqrt n-\sqrt N=O(N^{-1/2})$. Since $\Phi$ is Lipschitz, this proves
$H_{<j_n(u)}/s_n=\Phi(3u/2)+O_A(N^{-1/2})$. Combining with the prefix
correction proves (6.14) and (6.16); setting $u=0$ gives (6.15).
$\square$

## 7. Formal Verification and Local Controls

### 7.1. Finite Structure and Counting

The separate Lean 4 companion in `experiments/paper44/lean`
formalizes the concrete singleton-seed observer and its actual
normal forms, including all-parameter reachability and inverse
identities. Its principal manuscript interfaces are:

| Manuscript result | Lean interface |
| --- | --- |
| Equation (2.4) and region classification | `circular_prefix_classification` |
| Lemma 3.1, including $r=0$ | `card_actualProperLabelsAt_all` |
| Lemma 3.2 on actual terminal labels | `terminalPrefixActualEquiv`, `card_actualTerminalLabel_paper` |
| Fixed-carrier/label placement fibres | `properPrefixPlacementEquiv`, `card_actualProperPlacements_paper` |
| Theorem 3.3, actual full and registered normal forms | `prefixObserverNormalEquiv`, `registeredPrefixObserverNormalEquiv` |
| Theorem 3.3, both cardinality formulas | `paperTheorem33` |

These results hold for every $n\ge3$ and $j\ge1$ and use the
complete ordered records and null-preserving per-letter traces of
Section 2. The companion reuses Paper XL's abstract observer API
and the fixed-pair and future-event companions' execution and
classification theorems. The new finite work concerns actual
prefix-label images, their compatible placement fibres, and their
assembly into the minimal quotient.

The normal-form equivalences are noncomputable and use classical
choice. They neither require a unique realizing raw word nor
extract an executable minimizer. The axiom audit records only the
standard dependencies `propext`, `Classical.choice` and
`Quot.sound`, with no custom axioms or proof placeholders.

The project pins Lean 4.33.0 and Mathlib revision `db584cd6` (the full
pin is in the companion's Lake manifest). With the declared
sibling source dependencies present, its validation commands are:

```text
lake --no-cache build
lake env lean Checks.lean
lake env lean AxiomAudit.lean
```

The local structure-and-counting milestone records exact proof-source
hashes and dependency identity separately from this evolving
manuscript. Its scope stops at the finite classification and
Theorem 3.3. Corollaries 3.4--3.5 and the analytic results in
Sections 4--6 remain paper proofs; the growth spectrum and
Gaussian window are not claimed as Lean-certified. Reusing a
local dependency cache is not independent cold-start reproduction.

### 7.2. Bounded Computational Controls

The local control first generates the complete finite actual state
graph, then independently of the counting formulas minimizes it for
each declared prefix depth. It compares the entire equivalence
partition with the keys in Theorem 3.3, not just the total number.
For $3\le n\le7$ and $1\le j\le n-1$ all 20 cases agree.

| $n$ | Reachable states | Minimal counts at depths $1,\ldots,n-1$ |
| --- | ---: | --- |
| 3 | 30 | 12, 12 |
| 4 | 176 | 69, 71, 71 |
| 5 | 920 | 402, 410, 414, 414 |
| 6 | 4,566 | 2,085, 2,283, 2,303, 2,311, 2,311 |
| 7 | 22,134 | 9,965, 11,803, 12,363, 12,411, 12,427, 12,427 |

The saved controls also check recovery of the earlier depth-one,
depth-two and full-prefix formulas, and finite evaluations of the
rate formula. These calculations share the local consumer transition
code and serve as bounded consistency controls. The all-parameter
count and limits are proved in Sections 3--6 using the two imported
structural classifications.

Separate exact-arithmetic tests check (6.5)--(6.8), the finite
deficit inequality (6.12), and the decomposition (6.17). They do not extend the earlier saved
generated-domain replay or supply the asymptotic argument.

## 8. Conclusion

Retained prefix memory gives an exact family of minimal observers,
with actual history labels and placement fibres. Fixed and sublinear
depth preserve exponential base $4$, whereas linear depth produces
strictly intermediate rates before the base reaches $9/2$. At the
threshold, the state-count ratio follows the Gaussian profile
$\Phi(3u/2)$ across a window of width $\sqrt n$; at its center the ratio
tends to $1/2$. The threshold concerns the growth of the minimal state
space, rather than recovery of every historical record. Strictly above
the threshold, the prefix quotient has asymptotically the full-summary
state count, despite continuing to identify some distinct complete
summaries.

## References {.unnumbered}
