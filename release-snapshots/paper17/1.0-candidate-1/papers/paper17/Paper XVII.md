# Exact Post-Transient Coarse Factorization in a Reduced Male Drosophila CNS Model
### Reached-Set Restriction, Safe Forgetting, and Internal Transition-Layer Contrast

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XVII**

*This paper is Paper XVII of the RIME program, an independently scoped
computational follow-up to Paper XVI. It does not extend the SOF protocol line
and does not reopen Paper XVI's published claim surface.*

---

## Abstract

**Problem.** A lossy observation may fail to determine even one observed
successor on an initial microscopic domain. It may nevertheless support an
exact one-step factorization on states reached later by the dynamics.
Memory restoration and reached-set restriction must be distinguished on a
common source-time support.

**Approach.** We study the exact rational dynamics and superclass-mean
observation used in Paper XVI. A declared 711-source domain spans all 25
nonempty source strata, with a four-step horizon. Exact audits compare history
orders on the common support $t\in\{2,3\}$, decompose its non-singleton
fibers, and test the terminal image. A separate pair census records raw
signed-drive, clipping, and coarse-residual differences under zero input and
noise.

**Results.** The apparent order-two closure in the order-specific output is a
left-boundary effect. On the common support, orders zero, one, and two induce
the same noninjective, successor-compatible partition of 1,422 windows into
1,228 values. All 51 sources in the six unsafe $t=1$ fibers become coarsely
singleton at $t=2$; five disjoint cohorts of sizes $51,25,19,4,3$ remain
non-singleton and successor-compatible. The terminal $t=4$ image lies outside
the verified common coarse image, so the certificate gives one internal shift,
not an endomap. In 6,975 exact pair transitions, two clipping-sensitive
predicates separate all 570 transient-obstruction pairs from all 1,755
persistent-safe pairs at both $2\to3$ and $3\to4$. No single registered
predicate separates the classes at the defining $1\to2$ transition.

**Boundary.** The result is an exact finite Computational Certificate on a
reduced domain and horizon $T=4$. It does not establish a coarse endomap,
minimal memory, full-domain closure, a causal trigger for the initial split,
or physiological brain-state dynamics. Validation is local exact replay, not
independent replication.

**Keywords.** connectome; coarse-graining; coarse factorization; reached set;
quotient dynamics; exact rational computation; transient separation; clipping;
MaleCNS

---

## Notation Table {.unnumbered}

| symbol | meaning |
| --- | --- |
| $X$ | microscopic state space of the registered deterministic model |
| $F_Y:X\to X$ | registered exact microscopic update induced by the signed carrier $Y$ |
| $D_0$ | declared reduced set of 711 unit-state sources |
| $x_{a,t}=F_Y^t(e_a)$ | microscopic state from source $a\in D_0$ at time $t$ |
| $O:X\to Z$ | registered superclass-mean observation |
| $z_{a,t}=O(x_{a,t})$ | exact coarse observation |
| $H_h(a,t)$ | newest-first history $(z_{a,t},\ldots,z_{a,t-h})$ |
| $S(a,t)$ | exact successor observation $z_{a,t+1}$ |
| $\Omega_h$ | original order-specific source-time window domain |
| $\Omega^{\rm com}$ | common support $D_0\times\{2,3\}$ |
| $\Pi_h$ | partition of the selected source-time support into equal-$H_h$ fibers |
| $N_h$ | number of registered windows |
| $K_h$ | number of distinct exact history values |
| $M_h$ | largest exact history-fiber cardinality |
| $R_{2,3}$ | registered post-transient reached-set slices at $t=2,3$ |
| $\mathcal Z_{2,3}=O(R_{2,3})$ | verified common coarse image |
| $u_{a,t}=Y^{\mathsf T}x_{a,t}$ | exact raw signed drive before clipping |
| $C(u)$ | coordinatewise clipping $\min\{1,\max\{0,u\}\}$ |
| $r_{\rm raw}$ | coarse residual $O(u^a)-O(u^b)$ for an oriented source pair |
| $r_{\rm clip}$ | coarse residual $O(C(u^a))-O(C(u^b))$ after clipping |
| $r_{\rm corr}$ | exact clipping correction $r_{\rm clip}-r_{\rm raw}$ |

---

## 1. Introduction

A coarse observation does not automatically support a closed dynamical state.
Given microscopic dynamics $F:X\to X$ and an observation $O:X\to Z$, a
one-step coarse factorization exists on a declared domain only when $O(Fx)$ is
constant on every fiber of $O$.
Paper XVI applied this elementary criterion to a signed MaleCNS connectome
model and found exact first-order and one-lag obstructions on its registered
historical domains \cite{paper16}. That result established a negative boundary:
an anatomically meaningful and reproducible observation need not determine its
own future.

The natural constructive response is to add memory. For a coarse history

$$
H_h(x,t)=\bigl(O(F^t x),O(F^{t-1}x),\ldots,O(F^{t-h}x)\bigr),
\tag{1.1}
$$

one asks whether equal histories have equal observed successors. The first
registered experiment in this line evaluated orders $h=0,1,2$ over a four-step
exact orbit. Its frozen output appeared to give the desired transition:

$$
h=0,1:\ \text{failure},
\qquad
h=2:\ \text{historically labelled exact closed noninjective}.
\tag{1.2}
$$

That interpretation was wrong. The three orders in (1.2) were evaluated on
different left boundaries. Order zero included $t=0$, order one began at
$t=1$, and order two began at $t=2$. A hostile common-support audit showed
that, once all orders are restricted to the same source-time points
$t\in\{2,3\}$, they induce exactly the same successor-compatible partition. The past two
observations add no distinction on that support.

The actual result is more structural than finite-memory restoration. The
initial coarse equivalence relation contains classes that are incompatible
with the dynamics. After the registered transient, those unsafe classes are
absent from the reached-set slices. A different, disjoint family of
non-singleton classes remains, and those classes are successor-compatible.
Thus an exact one-step quotient factorization becomes valid by restriction to
a post-transient reached set rather than by enrichment with lag coordinates.
The terminal image does not return to the verified coarse image, so this is
not an endomap or an indefinitely iterable quotient system.

A second registered computation asks what exact internal transition-layer
features distinguish the two fiber fates. It does not recover one universal
trigger at the defining $1\to2$ transition. It does find a stable exact regime
contrast afterward: at $2\to3$ and $3\to4$, two predeclared clipping-sensitive
predicates hold for every transient-obstruction pair and for no
persistent-safe pair in every shared-stratum comparison cell. The result
therefore separates an unresolved, potentially heterogeneous initial trigger
from a sharply different post-separation internal signature.

The two fiber fates can be stated together:

> **The transient does not repair the original ambiguous fibers. It
> eliminates them. Exact noninjective coarse factorization is then carried by a
> disjoint family of persistent successor-consistent fibers.**

Here elimination is fiber-relative. It means that the original unsafe
equivalence classes do not survive as equivalence classes on the later
registered slices because their members become coarsely distinguishable. It
does not mean that microscopic states disappear or converge.

### 1.1 Contributions

This paper makes four bounded contributions.

1. It corrects the original history-order interpretation by comparing all
   orders on one support and proving an exact noninjective one-step
   factorization on the registered $t\in\{2,3\}$ slices.
2. It distinguishes separation of the 51 obstruction sources from five
   disjoint persistent non-singleton cohorts.
3. It shows that the terminal image leaves the verified coarse image, so the
   factorization is not a coarse endomap.
4. It gives an exact 6,975-record pair census and a post-separation
   transition-layer contrast without assigning a cause to the initial split.

---

## 2. Related Work and Novelty Boundary

Classical lumpability asks when a coarse partition of a Markov process retains
a closed transition law \cite{kemenySnell1976}. Higher-order lumpability
separates first-order closure from closure after retaining observation history
\cite{geigerTemmel2014}. The present system is deterministic and evaluated on
a declared finite orbit-window domain, but the governing fiber condition is
the same factorization principle: equal retained descriptions must have equal
retained successors. This paper does not claim lumpability theory as new.

Exact dynamical coarse-graining can be obtained by constructing collective
variables that preserve selected dynamical quantities
\cite{luVandenEijnden2014}. Network quotient and graph-fibration approaches
likewise require compatibility between the microscopic dynamics and the
chosen network partition \cite{devilleLerman2015}. Here the coarse observation
is not optimized to guarantee closure. It is the fixed superclass-mean map
used in the source-addressed MaleCNS case study.

Connectome coarse-graining is often motivated by the need to obtain tractable
mesoscopic descriptions from very large anatomical networks
\cite{koraSimon2024}. The MaleCNS data provide the anatomical and annotation
surface for the present model \cite{berg2026malecns,maleCNSdownload}. The
registered dynamics remain a computational model on that source, not a claim
that the coarse quotient is a physiological brain state.

Paper XVI supplies the immediate negative precursor. It separates structural
liftability, signed operator semantics, observation visibility, and dynamic
closure, and it gives exact witnesses showing that the registered coarse
observation does not close on its initial historical domains \cite{paper16}.
The present paper does not modify those results. Its new object is the exact
fiber geometry after restricting the same registered observation to later
reached-set slices, together with an exact internal transition-layer census of
the two resulting fiber fates.

The novelty boundary is consequently narrow:

> This paper provides a source-addressed exact finite certificate that a
> lossy coarse observation, invalid as a one-step factor during an initial
> transient, supports an exact noninjective factorization after restriction to
> declared later reached-set slices, and it decomposes that transition into
> transient separation and disjoint persistent safe forgetting. It further
> gives an exact post-separation layer contrast between the two declared pair
> families without identifying a universal trigger for the initial split.

It does not provide a general eventual-lumpability theorem, a causal mechanism,
or an explanation of why all registered fibers first separate or persist.

---

## 3. Finite Dynamic Descent

### 3.1 Fiber Criterion

Let $D\subseteq X$ be finite. The observation $O$ descends the microscopic
update $F$ on $D$ when there is a map

$$
\overline F:O(D)\longrightarrow Z
\qquad\text{such that}\qquad
O\circ F=\overline F\circ O\quad\text{on }D.
\tag{3.1}
$$

**Proposition 3.1 (finite one-step fiber criterion).** Such a map $\overline F$ exists
if and only if

$$
O(x)=O(y)\Longrightarrow O(Fx)=O(Fy),
\qquad x,y\in D.
\tag{3.2}
$$

*Proof.* Necessity follows by applying $\overline F$ to the common observation.
For sufficiency, define $\overline F(z)=O(Fx)$ using any $x\in D$ with
$O(x)=z$; condition (3.2) makes the value independent of the representative.
$\square$

The factorization is noninjective when at least one fiber of $O|_D$ has more
than one microscopic representative. Factorization and reconstruction are
therefore different requirements. Proposition 3.1 does not make $\overline F$
an endomap of $O(D)$; that stronger conclusion additionally requires
$\overline F(O(D))\subseteq O(D)$.

### 3.2 Orbit-Window Domains

For source $a\in D_0$, let

$$
x_{a,0}=e_a,
\qquad
x_{a,t+1}=F_Y(x_{a,t}),
\qquad
z_{a,t}=O(x_{a,t}).
\tag{3.3}
$$

The order-$h$ history and successor are

$$
H_h(a,t)=(z_{a,t},z_{a,t-1},\ldots,z_{a,t-h}),
\qquad
S(a,t)=z_{a,t+1}.
\tag{3.4}
$$

For a source-time universe $\Omega$, exact order-$h$ successor factorization means

$$
H_h(a,t)=H_h(b,s)
\Longrightarrow
S(a,t)=S(b,s)
\tag{3.5}
$$

for all $(a,t),(b,s)\in\Omega$. Equality in (3.5) is canonical rational
identity, not floating tolerance or hash equality.

### 3.3 Reached-Set Restriction

For time indices $I$, define the sampled reached set

$$
R_I(D_0)=\{x_{a,t}:a\in D_0,\ t\in I\}.
\tag{3.6}
$$

The observation equivalence relation is

$$
x\sim_O y\quad\Longleftrightarrow\quad O(x)=O(y).
\tag{3.7}
$$

The quotient supports a one-step factorization on $R_I(D_0)$ precisely when
$\sim_O$ is successor-compatible there. A quotient may therefore fail on the
initial domain while succeeding after restriction to a later reached set.
This is a source-domain statement; it does not imply that the successor lies
in the same coarse image or that the quotient can be iterated indefinitely.

### 3.4 Common-Support Requirement

Suppose multiple history orders are compared. If order $h$ is evaluated on

$$
\Omega_h=\{(a,t):a\in D_0,\ h\le t<T\},
\tag{3.8}
$$

then changing $h$ changes both the representation and the source-time domain.
An apparent order effect may therefore be a left-boundary effect. A valid
memory comparison fixes $H_{\max}$ and evaluates every $h\le H_{\max}$ on

$$
\Omega^{\rm com}_{H_{\max},T}
=\{(a,t):a\in D_0,\ H_{\max}\le t<T\}.
\tag{3.9}
$$

This requirement is central to the correction below.

---

## 4. Finite Model and Exact Domain

### 4.1 Signed Dynamics and Observation

The model uses the same node basis and signed normalized
$Y_{\rm known\pm}$ carrier as the dynamic line of Paper XVI. The stored carrier
uses source rows and target columns; state propagation uses the registered
incoming action $Y^{\mathsf T}x$. The exact deterministic update is

$$
F_Y(x)=(1-\alpha)x+\alpha\,\phi(\gamma Y^{\mathsf T}x),
\qquad
\phi(u)_v=\min\{1,\max\{0,u_v\}\},
\tag{4.1}
$$

with $\alpha=1/5$, $\gamma=1$, zero external input, and no stochastic noise.
All registered coefficients and states are represented as reduced rationals.

The observation $O$ is the superclass-mean vector. For the declared partition
$V=\bigsqcup_iV_i$,

$$
O_i(x)=\frac{1}{|V_i|}\sum_{v\in V_i}x_v.
\tag{4.2}
$$

The observation is an operational annotation aggregate, not an assumed
biological state. The computational evidence starts from the retained exact
orbit sidecar; microscopic orbit generation is not replayed by this package.

### 4.2 Reduced Domain and Selection

The complete eligible source universe contains 163,439 rows across 25
nonempty superclass strata. A declared resource model selected 711 sources.
One source was first assigned to every nonempty stratum; the
remaining seats used largest-remainder apportionment on remaining stratum
capacity, and SHA-256 rank selected members within each stratum. The declared
selection rule does not read trajectories, factorization, or candidate
outcomes.

The reduced domain is a declared computational domain, not a random sample or
a prevalence estimator. The retained immutable record does not independently
establish that the scope record preceded the computed outcome.

### 4.3 Exact Horizon

The registered rectangle is

$$
|D_0|=711,
\qquad
H=2,
\qquad
T=4.
\tag{4.3}
$$

Each source contributes one exact orbit $z_{a,0},\ldots,z_{a,4}$, from which
orders $0,1,2$ are derived. Rational values are serialized canonically with
positive reduced denominators. SHA-256 is an index and integrity mechanism;
every potential equality is resolved by canonical payload comparison.

The resource gates were satisfied by the completed run. The scope, exact
sidecar, and subsequent audits are bound in the paper-owned evidence package
described in Appendix A.

---

## 5. Frozen Primary Result

The original order-specific classification is:

| order $h$ | source-time support | $(N_h,K_h,M_h)$ | successor-fiber test |
| ---: | --- | --- | --- |
| 0 | $0\le t\le3$ | $(2844,1819,406)$ | 16 conflicts |
| 1 | $1\le t\le3$ | $(2133,1797,51)$ | 6 conflicts |
| 2 | $2\le t\le3$ | $(1422,1228,51)$ | exact, noninjective |

The original classification called order two minimal on these
order-specific domains. The next section tests whether that interpretation
survives a common source-time support.

The left boundary moves with $h$. In particular, all six order-one failure
fibers occur at $t=1$, a time omitted from the order-two domain. The frozen
table therefore mixes two changes:

$$
\text{history representation}
\qquad\text{and}\qquad
\text{source-time support}.
\tag{5.1}
$$

The next section separates them.

---

## 6. Common-Support Correction

Fix

$$
\Omega^{\rm com}=D_0\times\{2,3\}.
\tag{6.1}
$$

For each $h\in\{0,1,2\}$, build the exact fiber partition $\Pi_h$ on this
same set of 1,422 source-time points.

> **Computational Certificate 6.1 (common-support factorization).** On
> $\Omega^{\rm com}$, orders $h=0,1,2$ all satisfy the exact successor-fiber
> criterion. Each order has
> $$
> N_h=1422,
> \qquad K_h=1228,
> \qquad M_h=51,
> \tag{6.2}
> $$
> ten non-singleton fibers, and zero failure fibers.

> **Computational Certificate 6.2 (partition identity).** The three induced
> partitions are exactly identical:
> $$
> \Pi_0=\Pi_1=\Pi_2.
> \tag{6.3}
> $$

The common partition digest is bound in the paper-owned exact audit.
Equality in (6.3) is equality of source-time blocks after exact payload
comparison, not equality of hash labels alone.

### 6.1 Consequences

First, current observation already determines the registered successor on
the common support:

$$
z_{a,t}=z_{b,s}
\Longrightarrow
z_{a,t+1}=z_{b,s+1},
\qquad
(a,t),(b,s)\in\Omega^{\rm com}.
\tag{6.4}
$$

Second, the lag coordinates add no partition refinement there. On this finite
support, equal current observations already force equal one- and two-lag
history tuples. The past coordinates are redundant for discrimination on the
registered points.

Third, the factorization remains genuinely lossy. Since

$$
K_0=1228<1422=N_0,
\tag{6.5}
$$

factorization is not obtained by assigning a unique code to every source-time
point. The finite-domain window-count reduction is

$$
\frac{N_0-K_0}{N_0}
=\frac{194}{1422}
\approx 0.1364.
\tag{6.6}
$$

This is a count of identified registered windows, not a bit-level compression
ratio.

Certificates 6.1 and 6.2 therefore rule out the intended minimal-memory
conclusion: the positive result is already present at order zero on the common
support, while the original order effect is confounded with the moving left
boundary.

### 6.2 Terminal-Image Boundary

Let $\mathcal Z_{2,3}=O(R_{\{2,3\}}(D_0))$. The factor map in Proposition 3.1
has source $\mathcal Z_{2,3}$ and target $Z$. To obtain an autonomous coarse
system on the same image, one would additionally need the registered
successors to remain in $\mathcal Z_{2,3}$.

> **Computational Certificate 6.3 (terminal-image boundary).** The exact
> observation sets at $t=2$, $t=3$, and $t=4$ each contain 614 values. The
> $t=2$ and $t=3$ sets are disjoint, so $|\mathcal Z_{2,3}|=1228$. All $t=2$
> successors lie in $\mathcal Z_{2,3}$, giving one registered internal shift.
> All 614 $t=3$ successors lie outside $\mathcal Z_{2,3}$.

Consequently, the certificate establishes a horizon-bounded one-step
factorization with one internal shift. It does not establish an endomap
$\mathcal Z_{2,3}\to\mathcal Z_{2,3}$ or sustained coarse iteration.

---

## 7. Transient-Fiber Decomposition

The common-support result identifies where factorization holds but not how the
initial obstruction disappears. A second result-owned audit compares the
$t=1$ obstruction sources with the non-singleton fibers at $t=2$ and $t=3$.

### 7.1 Transient Separation

The six order-one failure fibers contain respectively

$$
9,\ 33,\ 2,\ 2,\ 2,\ 3
\tag{7.1}
$$

sources, for a total of 51. Within each failure fiber, the sources have equal
registered one-lag histories at $t=1$ but distinct successors.

> **Computational Certificate 7.1 (transient separation).** Every source in
> the six $t=1$ failure fibers has a globally singleton coarse observation at
> $t=2$ among all 711 registered sources.

Thus none of the 51 obstruction sources enters a post-transient
non-singleton cohort. The obstruction is not repaired by appending a lag on
the common support. The offending classes cease to exist as coarse classes
because their members become distinguishable under $O$.

### 7.2 Persistent Safe Forgetting

The noninjectivity at $t=2$ has a different source. Exactly five
non-singleton source cohorts occur, with sizes

$$
51,\ 25,\ 19,\ 4,\ 3.
\tag{7.2}
$$

> **Computational Certificate 7.2 (persistent successor-compatible
> cohorts).** The five source membership sets in (7.2) are identical at
> $t=2$ and $t=3$. Each cohort has one exact coarse observation at each time,
> and its registered next observation is common to all members. The cohorts
> are disjoint from the 51 transient-obstruction sources.

Their redundancy on each time slice is

$$
(51-1)+(25-1)+(19-1)+(4-1)+(3-1)=97.
\tag{7.3}
$$

The two registered slices therefore account for all

$$
2\times97=194
\tag{7.4}
$$

redundant windows in the common-support partition. The ten non-singleton
fibers are precisely two time slices of five persistent source cohorts.

### 7.3 Exact Decomposition

The finite registered transition can now be expressed as

$$
\boxed{
\begin{array}{c}
\text{51 sources in unsafe }t=1\text{ fibers}
\\[2pt]\downarrow\\[-2pt]
\text{51 globally singleton coarse observations at }t=2
\end{array}}
\tag{7.5}
$$

together with the disjoint branch

$$
\boxed{
\begin{array}{c}
\text{five non-singleton cohorts at }t=2
\\[2pt]\downarrow\\[-2pt]
\text{the same five successor-compatible cohorts at }t=3.
\end{array}}
\tag{7.6}
$$

Equations (7.5) and (7.6) distinguish transient separation from persistent
safe forgetting.

![Exact finite fiber evolution. The six unsafe $t=1$ fibers separate into singleton observations at $t=2$, while five disjoint cohorts retain membership and successor compatibility from $t=2$ to $t=3$. The common-support partitions agree, but the terminal $t=4$ image leaves the verified coarse image. Arrows denote only registered finite transitions.](../../figures/paper17/fig1_transient_separation_and_safe_forgetting.png)

---

## 8. Internal Transition-Layer Contrast

The fiber decomposition establishes two different coarse fates but does not
identify their internal transition signatures. The transition-layer comparison
uses the 51 transient-obstruction sources and 102 persistent-safe sources.
External input and stochastic noise remain zero.

### 8.1 Exact Pair Census

Every unordered source pair is oriented canonically by source identifier,
with $a<b$ and all signed differences defined as value$(a)-$value$(b)$. For
one registered transition, write

$$
\delta x=x^a-x^b,
\qquad
\delta u=u^a-u^b,
\qquad
u^a=Y^{\mathsf T}x^a,
\quad
u^b=Y^{\mathsf T}x^b.
\tag{8.1}
$$

The exact coarse residuals are

$$
\begin{aligned}
r_{\rm raw}&=O(u^a)-O(u^b),\\
r_{\rm clip}&=O(C(u^a))-O(C(u^b)),\\
r_{\rm corr}&=r_{\rm clip}-r_{\rm raw}.
\end{aligned}
\tag{8.2}
$$

The census contains all 570 unordered pairs within the six frozen
transient-obstruction fibers and all 1,755 unordered pairs within the five
persistent-safe cohorts. Each pair is evaluated at $1\to2$, $2\to3$, and
$3\to4$, giving

$$
3(570+1755)=6975
\tag{8.3}
$$

pair-transition records, derived from 459 exact source-transition records for
153 distinct sources. The comparison design keeps transition time,
transient cohort, persistent cohort, and shared initial anatomical stratum
explicit, producing 15 nonpooled comparison cells.

The comparison uses seven fixed exact predicates. Write $d_x$ and
$d_u$ for the exact microscopic-state and raw-drive $L^1$ differences, and
$N_{\rm offdiag}^{\rm fate}$ for the number of coordinates with differing
clipping-fate labels. In the registered bit order, its predicates are:

| bit | predicate | exact condition |
| ---: | --- | --- |
| 1 | clipping creates a coarse residual | $r_{\rm raw}=0$, $r_{\rm clip}\ne0$, $r_{\rm corr}=r_{\rm clip}$ |
| 2 | clipping eliminates a coarse raw residual | $r_{\rm raw}\ne0$, $r_{\rm clip}=0$, $r_{\rm corr}=-r_{\rm raw}$ |
| 3 | clipping modifies a nonzero coarse residual | $r_{\rm raw}\ne0$, $r_{\rm clip}\ne0$, $r_{\rm corr}\ne0$ |
| 4 | raw residual persists unchanged | $r_{\rm raw}\ne0$, $r_{\rm clip}=r_{\rm raw}$, $r_{\rm corr}=0$ |
| 5 | raw-drive difference is coarsely annihilated | $d_u\ne0$, $r_{\rm raw}=0$ |
| 6 | microscopic difference has identical raw drive | $d_x\ne0$, $d_u=0$ |
| 7 | fate disagreement with nonzero correction | $N_{\rm offdiag}^{\rm fate}\ne0$, $r_{\rm corr}\ne0$ |

The exact conditions are evaluated on one oriented pair record; no coordinate
is selected after observing a result. Bits 3 and 7 are decisive below:

$$
\begin{aligned}
P_{\rm mod}
&:\quad r_{\rm raw}\ne0,
\quad r_{\rm clip}\ne0,
\quad r_{\rm corr}\ne0,\\
P_{\rm fate}
&:\quad N_{\rm offdiag}^{\rm fate}\ne0,
\quad r_{\rm corr}\ne0,
\end{aligned}
\tag{8.4}
$$

These are conjunctions of registered exact quantities. Neither a residual
quadrant alone nor the identity relating
$r_{\rm clip}$ to the observed successor can award the mechanism outcome.

### 8.2 Exact Finite Contrast

> **Computational Certificate 8.1 (complete registered contrast).** The 15
> cells, indexed by transition and stratum, have distinct exact normalized
> histograms of the seven predicates. Equality is checked by integer cross
> multiplication. No floating tolerance, prevalence threshold, majority rule,
> or hypothesis test is used.

> **Computational Certificate 8.2 (post-separation layer localization).** At
> each of $2\to3$ and $3\to4$, both $P_{\rm mod}$ and $P_{\rm fate}$ hold for
> every transient-obstruction pair and for no persistent-safe pair in every
> shared-stratum comparison cell. These give four exact separators: two
> predicates across two transitions, always in the same direction.

The cellwise comparison does not cover pairs outside shared initial strata.
An exact full-cohort tally gives the global counts:

| transition | predicate | transient true / total | persistent true / total |
| --- | --- | ---: | ---: |
| $2\to3$ | $P_{\rm mod}$ | 570 / 570 | 0 / 1,755 |
| $2\to3$ | $P_{\rm fate}$ | 570 / 570 | 0 / 1,755 |
| $3\to4$ | $P_{\rm mod}$ | 570 / 570 | 0 / 1,755 |
| $3\to4$ | $P_{\rm fate}$ | 570 / 570 | 0 / 1,755 |

The global tally also includes three transient and 180 persistent pairs outside
the shared-stratum cells.

The result is a stable exact internal regime contrast. The former obstruction
pairs continue to exhibit clipping modification of a nonzero coarse residual
and clipping-fate disagreement with nonzero correction. The persistent-safe
pairs exhibit neither registered predicate on those two transitions. This
statement is relative to the declared finite pair universes and exact feature
families; it is not a population or causal claim.

![Exact registered transition-layer contrast. At $2\to3$ and $3\to4$, clipping modification of a nonzero coarse residual and fate disagreement with nonzero clipping correction hold for every transient-obstruction pair and no persistent-safe pair. The $1\to2$ histograms differ, but no single registered predicate separates the cohorts there; later signatures do not identify the initial trigger.](../../figures/paper17/fig2_internal_transition_layer_contrast.png)

### 8.3 Initial-Trigger Boundary

No primary predicate is an all-versus-none separator at $1\to2$, although all
five registered comparison-cell histograms differ there. The two later
separators do not explain the original split. A heterogeneous initial trigger
is possible, but this census does not establish one.

---

## 9. Claim Boundary

The factorization, fiber decomposition, and transition-layer contrast are
local exact computational certificates. They concern 711 selected sources and
the registered horizon through $t=4$; the 194-window reduction counts finite
source-time identifications, not information bits. The later transition-layer
separators identify a contrast between two declared pair families, not the
cause of the initial $1\to2$ split.

No full-domain closure, coarse endomap, minimal memory order, eventual
invariance, microscopic convergence, or physiological state claim follows.
Local exact replay is not independent replication, and the retained record
does not independently authenticate the scope record's temporal precedence.
Appendix A identifies the source-addressed claim and evidence closure.

---

## 10. Conclusion

The registered superclass mean fails one-step factorization during the initial
transient but supports an exact noninjective factorization on the later
registered slices. This is not a demonstrated memory effect: zero-, one-, and
two-lag representations induce the same common-support partition. The six
unsafe $t=1$ classes disappear by coarse separation of their 51 members,
whereas a disjoint family of five cohorts remains non-singleton and
successor-compatible. The terminal $t=4$ image leaves the verified common
coarse image, so the certificate supplies one internal shift rather than a
closed autonomous system.

The quotient thus becomes successor-compatible only after restriction to the
registered reached set; neither history augmentation nor recovery of
microscopic identity establishes this finite factorization. Its domain is part
of the claim, not an incidental choice of sample.

The pair census adds a second exact result. All 15 comparison-cell histograms
differ. At both later transitions, two clipping predicates hold for every
obstruction pair and no persistent-safe pair. This establishes a stable
internal contrast after separation. Neither predicate uniformly separates
these families at $1\to2$, so the initial split remains unexplained. The
remaining question is which internal routes first expose unsafe distinctions
while leaving persistent cohorts indistinguishable.

---

## Appendix A: Computational Artifacts

The paper-owned evidence package is indexed at
[RIME Lite, experiments/paper17](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper17).
It binds the reduced-domain scope, exact orbit sidecar, common-support and
fiber audits, transition-layer census, manuscript claim table, release manifest,
and local validation receipts. The exact MTS-1 sidecar is deposited separately
at [Zenodo DOI 10.5281/zenodo.23234143](https://doi.org/10.5281/zenodo.23234143);
this is a data-deposit DOI, not a DOI for the manuscript.

The validators replay the finite classifications from retained exact bytes;
the MTS-1 validator also rederives all pair records and compares predicted
successors with historical exact observations. They do not rerun microscopic
orbit generation, independently replicate the study, or authenticate the
temporal precedence of the declared scope record. The Zenodo binding checks
deposit metadata and local reconstruction, not a remote full-byte download.
