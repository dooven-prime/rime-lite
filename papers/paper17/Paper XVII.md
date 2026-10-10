# Exact Post-Transient Coarse Factorization in a Reduced Male Drosophila CNS Model
### Reached-Set Restriction, Drive-Off Fibers, and Internal Transition-Layer Contrast

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XVII**

*This paper is Paper XVII of the RIME program. It studies post-transient coarse
factorization on a reduced domain of Paper XVI's signed MaleCNS model. Its
claims are finite and model-relative.*

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
An exact cache audit covers every member of all ten non-singleton fibers:
their clipped network drive is zero, so common linear leakage suffices to
preserve their one-step coarse equality.

**Boundary.** The result is an exact finite Computational Certificate on a
reduced domain and horizon $T=4$. It establishes neither a coarse endomap nor
minimal memory, full-domain closure, a cause of the initial split, or
physiological brain-state dynamics. The noninjective factorization does not
demonstrate active compensation or nonzero-drive dynamic compression.

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
| $\Omega_h$ | order-specific source-time window domain |
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

One possible response is to add memory. For a coarse history

$$
H_h(x,t)=\bigl(O(F^t x),O(F^{t-1}x),\ldots,O(F^{t-h}x)\bigr),
\tag{1.1}
$$

one asks whether equal histories have equal observed successors. An
order-specific comparison evaluated $h=0,1,2$ over a four-step exact orbit.
It appeared to give the transition:

$$
h=0,1:\ \text{failure},
\qquad
h=2:\ \text{historically labelled exact closed noninjective}.
\tag{1.2}
$$

This contrast does not establish a memory effect. The three orders in (1.2)
were evaluated on different left boundaries. Order zero included $t=0$,
order one began at $t=1$, and order two began at $t=2$. On the common
source-time support $t\in\{2,3\}$, all three induce the same
successor-compatible partition. The past two observations add no distinction
there.

The actual result is more structural than finite-memory restoration. The
initial coarse equivalence relation contains classes that are incompatible
with the dynamics. After the registered transient, those unsafe classes are
absent from the reached-set slices. A different, disjoint family of
non-singleton classes remains, and those classes are successor-compatible.
Thus an exact one-step quotient factorization becomes valid by restriction to
a post-transient reached set rather than by enrichment with lag coordinates.
The terminal image does not return to the verified coarse image, so this is
not an endomap or an indefinitely iterable quotient system.

The noninjective part also has a simple model-relative explanation. An exact
audit of all five persistent cohorts finds zero clipped network drive at
every saved current time $t=1,2,3$. On the common support, their updates are
therefore pure leakage. The factorization remains exact and noninjective,
but its identified windows do not demonstrate compensation between nonzero
effective drives. This distinction separates a valid finite factorization
from a stronger interpretation of the dynamics that realizes it.

An exact pair census distinguishes the two fiber fates at later transition
layers. At $2\to3$ and $3\to4$, two registered clipping-sensitive predicates
hold for every transient-obstruction pair and for no persistent-safe pair in
each shared-stratum comparison cell. Neither predicate identifies the cause
of the defining $1\to2$ split.

### 1.1 Contributions

This paper makes five bounded contributions.

1. It corrects the original history-order interpretation by comparing all
   orders on one support and proving an exact noninjective one-step
   factorization on the registered $t\in\{2,3\}$ slices.
2. It distinguishes separation of the 51 obstruction sources from five
   disjoint persistent non-singleton cohorts.
3. It shows that the terminal image leaves the verified coarse image, so the
   factorization is not a coarse endomap.
4. It gives an exact 6,975-record pair census and a post-separation
   transition-layer contrast without assigning a cause to the initial split.
5. It audits the entire noninjective part of the common-support partition
   and shows that common linear leakage suffices to preserve its one-step
   equality, without a demonstrated nonzero-drive compensation mechanism.

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

The case-specific contribution is an exact finite certificate for
post-transient, noninjective factorization under a fixed observation, together
with a decomposition of the unsafe and persistent fibers. The pair census
locates a later internal contrast, while the persistent-cohort audit supplies
a common-leak explanation for the retained equality. These results provide
neither a general eventual-lumpability theorem nor a causal mechanism,
learning process, or biological account of forgetting.

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

The model uses the node basis and signed known-transmitter proxy carrier of
Paper XVI \cite{paper16}: 211,577 nodes and 26,028,386 directed edges in the
full support, of which 25,214,058 have the registered known-sign labels.
These signs are not receptor-validated physiological effects. If $W$ is the
frozen signed-weight matrix, its absolute outgoing-row-$L^1$ normalization is

$$
s_v=\sum_w|W_{vw}|,
\qquad
Y_{vw}=\begin{cases}
W_{vw}/s_v,&s_v>0,\\
0,&s_v=0.
\end{cases}
$$

The stored carrier uses source rows and target columns; state propagation
uses the registered incoming action $Y^{\mathsf T}x$. The exact deterministic
update is

$$
F_Y(x)=(1-\alpha)x+\alpha\,\phi(\gamma Y^{\mathsf T}x),
\qquad
\phi(u)_v=\min\{1,\max\{0,u_v\}\},
\tag{4.1}
$$

with $\alpha=1/5$, $\gamma=1$, zero external input, and no stochastic noise.
Write $C=\phi$ for this clipping map below. All registered coefficients and
states are represented as reduced rationals.

The observation $O$ is the superclass-mean vector. For the declared partition
$V=\bigsqcup_iV_i$,

$$
O_i(x)=\frac{1}{|V_i|}\sum_{v\in V_i}x_v.
\tag{4.2}
$$

The observation has 28 superclass coordinates. It is an operational annotation
aggregate, not an assumed biological state. The computational evidence starts
from the retained exact orbit sidecar; microscopic orbit generation is not
replayed by this package.

### 4.2 Reduced Domain and Selection

Of the 28 observation coordinates, 25 have eligible unit-state sources. The
complete eligible source universe contains 163,439 rows across those 25
strata. A declared resource model selected 711 sources.
One source was first assigned to every nonempty stratum; the
remaining seats used largest-remainder apportionment on remaining stratum
capacity, and SHA-256 rank selected members within each stratum. The declared
selection rule does not read trajectories, factorization, or candidate
outcomes.

The reduced domain is a declared computational domain, not a random sample or
a prevalence estimator.

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

---

## 5. Order-Specific Baseline

The order-specific classification is:

| order $h$ | source-time support | $(N_h,K_h,M_h)$ | successor-fiber test |
| ---: | --- | --- | --- |
| 0 | $0\le t\le3$ | $(2844,1819,406)$ | 16 conflicts |
| 1 | $1\le t\le3$ | $(2133,1797,51)$ | 6 conflicts |
| 2 | $2\le t\le3$ | $(1422,1228,51)$ | exact, noninjective |

Read alone, the table suggests that order two is the first successful history
order. But its left boundary moves with $h$: all six order-one failure fibers
occur at $t=1$, which the order-two domain omits. The table therefore mixes
two changes:

$$
\text{history representation}
\qquad\text{and}\qquad
\text{source-time support}.
\tag{5.1}
$$

Section 6 compares the orders on one support.

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

Third, the factorization remains genuinely lossy at the microscopic-state
level. The count

$$
K_0=1228<1422=N_0,
\tag{6.5}
$$

shows that distinct source-time addresses share observations, but does not
alone prove that their microscopic states differ. That follows directly from
(4.1). Put $\beta=1-\alpha=4/5$. Clipping keeps every coordinate in $[0,1]$;
for distinct unit-state sources $a\ne b$ and either $t=2$ or $t=3$,

$$
(x_{a,t})_a\ge\beta^t>\frac12,
\qquad
(x_{b,t})_a\le 1-\beta^t<\frac12,
\quad
\beta^2=\frac{16}{25},\quad\beta^3=\frac{64}{125}.
\tag{6.5a}
$$

Thus $x_{a,t}\ne x_{b,t}$ at each of those times. The registered non-singleton
cohorts in Certificate 7.2 contain distinct sources with equal observations
on each slice, so $O|_{R_{\{2,3\}}(D_0)}$ is noninjective. This concerns the
observation restricted to the reached set, not injectivity of the factor map
$\overline F$. The finite-domain window-count reduction is

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
Here "safe forgetting" denotes only the retention of a successor-compatible,
noninjective observation on those slices. It does not name a learned or
actively corrective process; Section 7.4 identifies its effective-drive
boundary in the registered model.

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

![Exact finite fiber evolution. The six unsafe $t=1$ fibers separate into singleton observations at $t=2$, while five disjoint cohorts retain membership and successor compatibility from $t=2$ to $t=3$. On the audited $t=2,3$ slices, persistent fibers have zero clipped drive. The terminal $t=4$ image leaves the verified coarse image. Arrows denote only registered finite transitions.](../../figures/paper17/fig1_transient_separation_and_safe_forgetting.png)

### 7.4 Effective-Drive Boundary

A source-addressed audit covers 306 saved caches of the five persistent
cohorts: 102 sources at $t=1,2,3$. Its exact cache replay checks clipping from
the retained raw-drive payloads; it does not regenerate $Y^{\mathsf T}x_t$
or microscopic orbits.

> **Computational Certificate 7.3 (persistent effective-drive boundary).**
> Every saved raw drive is nonzero and coordinatewise nonpositive; every
> clipped drive is zero. Thus all 204 members of the ten non-singleton fibers
> on $t\in\{2,3\}$ have zero clipped drive. These fibers account for all 194
> redundant windows.

The update in (4.1) is therefore

$$
F_Y(x_{a,t})=\frac45x_{a,t},
\qquad C(Y^{\mathsf T}x_{a,t})=0.
\tag{7.7}
$$

For cohort members $a,b$, linearity of $O$ gives

$$
\begin{aligned}
O(F_Yx_{a,t})-O(F_Yx_{b,t})
&=\frac45\bigl(O(x_{a,t})-O(x_{b,t})\bigr)\\
&=0.
\end{aligned}
\tag{7.8}
$$

Thus common leakage is a sufficient explanation of one-step equality on
the entire noninjective part. No member there has a nonzero effective
network drive, and no unequal nonzero clipped drives are being hidden by
the observation map. The microscopic states themselves need not be equal:
their differences are multiplied by $4/5$, not erased.

The $t=1$ caches concern the same 102 sources but do not extend the
common-support factorization to all $t=1$ fibers. Nor is this a pure-leak
classification of all 711 sources. Nonpositivity of the total drive does
not establish nonpositivity of every individual source-block contribution
or arbitrary block-subset robustness. The cache audit and (7.7)--(7.8) also
do not make the finite coarse image forward invariant or certify an
indefinitely iterable quotient.

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
$d_u$ for the exact microscopic-state and raw-drive $L^1$ differences. A raw
coordinate $u$ has clipping fate $\mathrm{LOWER}$ when $u\le0$,
$\mathrm{INTERIOR}$ when $0<u<1$, and $\mathrm{UPPER}$ when $u\ge1$.
Let $N_{\rm offdiag}^{\rm fate}$ count coordinates with differing fate labels
in an oriented pair. In the registered bit order, the predicates are:

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
quadrant alone nor the identity relating $r_{\rm clip}$ to the observed
successor establishes the finite contrast below.

### 8.2 Exact Finite Contrast

> **Computational Certificate 8.1 (complete registered contrast).** In each
> of the 15 predeclared comparison cells, the transient-obstruction and
> persistent-safe pair sets have different exact normalized histograms of the
> ordered seven-bit joint-predicate signature. Each cell retains the
> transition, both cohort identities, and their shared initial stratum.
> Histogram equality is checked by integer cross multiplication, without
> pooling across cells. No floating tolerance, prevalence threshold,
> majority rule, or hypothesis test is used.

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

Certificate 7.3 explains the persistent side of this contrast. At the
audited current times $t=2,3$, both members of every persistent pair have
zero clipped drive, forcing $r_{\rm clip}=0$ and $P_{\rm mod}$ to be false.
Their coordinatewise nonpositive raw drives also put every clipping fate in
$\mathrm{LOWER}$, so $N_{\rm offdiag}^{\rm fate}=0$ and $P_{\rm fate}$ is
false. The exact transition-layer contrast on the two audited later
transitions therefore compares the transient signatures with a drive-off
persistent family; it does not show compensation between nonzero effective
drives. This is a finite pair-universe statement, not a population or causal
claim.

![Exact registered transition-layer contrast. At $2\to3$ and $3\to4$, clipping modification of a nonzero coarse residual and fate disagreement with nonzero clipping correction hold for every transient-obstruction pair and no persistent-safe pair. The persistent side has zero clipped drive at current times $t=2,3$; the contrast does not show nonzero-drive compensation. At $1\to2$, no single registered primary predicate separates the cohorts, so later signatures do not identify the initial trigger.](../../figures/paper17/fig2_internal_transition_layer_contrast.png)

### 8.3 Initial-Trigger Boundary

No primary predicate is an all-versus-none separator at $1\to2$, although all
five registered comparison-cell histograms differ there. The two later
separators do not explain the original split. A heterogeneous initial trigger
is possible, but this census does not establish one.

---

## 9. Claim Status and Boundary

| result | status | scope |
| --- | --- | --- |
| Proposition 3.1: fiber criterion | Proposition | A declared finite domain and observation |
| Certificates 6.1--6.2: common-support correction | Computational Certificate | 711 sources, $t=2,3$, $h=0,1,2$ |
| Certificate 6.3: terminal-image boundary | Computational Certificate | Saved $t=2,3,4$ observation sets |
| Certificates 7.1--7.2: two fiber fates | Computational Certificate | 51 obstruction sources and five disjoint cohorts |
| Certificate 7.3: effective-drive boundary | Computational Certificate | 102 sources; saved $t=1,2,3$ caches |
| Certificates 8.1--8.2: transition-layer contrast | Computational Certificate | Registered pair census and global tally |
| Cause of the defining initial split | Research Program | Not established by the retained contrast |

These certificates concern 711 selected sources and a horizon through $t=4$.
The 194-window reduction counts finite source-time identifications, not
information bits. The later predicates distinguish two declared pair
families, not the cause of the initial $1\to2$ split. On the common-support
non-singleton fibers, (7.7)--(7.8) give a sufficient common-leak explanation;
they do not demonstrate active compensation or nonzero-drive compression.

Neither the $t=1$ drive readout nor separate intervention studies enlarge the
factorization domain. No full-domain closure, coarse endomap, minimal memory
order, eventual invariance, microscopic convergence, or physiological state
claim follows. Local validation is not independent replication, and the
retained record does not independently authenticate the scope record's
temporal precedence.

---

## 10. Conclusion

The registered superclass mean fails one-step factorization during the initial
transient but supports exact noninjective factorization on later reached-set
slices. Zero-, one-, and two-lag histories induce the same common-support
partition: the change comes from domain restriction, not demonstrated memory
restoration. The 51 sources in unsafe $t=1$ fibers become coarsely singleton,
while five disjoint cohorts remain non-singleton and successor-compatible.
The terminal $t=4$ image leaves the verified coarse image, so the certificate
supplies one internal shift rather than an autonomous coarse endomap.

The pair census finds a later clipping-sensitive contrast, but not the cause
of the defining $1\to2$ split. Every member of the persistent non-singleton
fibers has zero clipped network drive; common leakage suffices to preserve
their one-step equality. The result is a finite, model-relative example of
reached-set factorization, not evidence of active compensation or sustained
coarse dynamics.

---

\newpage

## Appendix A: Computational Artifacts

The paper-owned evidence package is under `experiments/paper17/` in the
[RIME repository](https://github.com/dooven-prime/rime-lite). Its
`00_START_HERE.md` gives exact paths and replay instructions.
The MTS-1 sidecar has a separate [data-deposit DOI](https://doi.org/10.5281/zenodo.23234143);
that DOI does not identify this manuscript.

| role | short path |
| --- | --- |
| Exact orbit and finite-history audits | `results/` |
| Pair census and effective-drive audit | `mechanism/` |
| Claim map and versioned manifest | package root |
| Primary local receipts | `results/` |
| Mechanism local receipts | `mechanism/` |

The default gate checks retained finite-history results and compact MTS-1 and
drive-audit bindings; it does not open the deposited pair shards or regenerate
microscopic orbits. Optional full sidecar replay checks exact pair and cache
payloads without recomputing the operator action. Neither mode establishes
independent replication or authenticates the temporal precedence of the
declared scope record; the deposit binding is not a remote full-byte download.
