# From Support to State
### Auditing Structural and Dynamic Descent in the Male Drosophila CNS

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XVI**

*This paper is Paper XVI of the RIME program, an independently scoped
computational connectome case study. It does not extend or reopen the SOF
protocol line closed by Paper XV.*

---

## Abstract

**Problem.** Large connectomes are commonly compressed into sector-level
support graphs, signed operators, coarse state variables, and low-dimensional
readouts. These representations answer different questions. A path in a
quotient support graph need not lift to a nonzero microscopic composition, and
a reproducible coarse observable need not determine its own future.

**Approach.** The analysis separates three descent problems on the MaleCNS v1.0
connectome: structural support-to-route descent, operator-to-observation
visibility, and microscopic-to-coarse dynamic closure. Exact finite route
audits are combined with source-bound numerical dynamics on a frozen signed,
normalized carrier. Deterministic fiber criteria distinguish descriptive
observability, predictive fit, and exact closure.

**Results.** At depth two, the typed-core, relay-strict, and
coverage-inclusive sectorizations lift 4,970 of 6,237, 5,751 of 7,019, and
6,125 of 7,831 quotient-supported triples, respectively. The first nested
increment lifts 781 of 782 newly admitted triples, whereas the second lifts
374 of 812. Matched-support transmitter-proxy sign assignments produce much
larger registered response changes than the corresponding coverage loss, and
the visibility of a fixed perturbation varies strongly with the observation
functional. For dynamic descent, both superclass-mean and somaSide-mean
observations fail the registered first-order fiber criterion; one coarse lag
also fails, including an exact witness in the named `cb_intrinsic` sector. On
the same signed carrier used by the dynamic test, somaSide has exact complete
liftability at depths two and three, yet its first-order coarse dynamics do not
close. This is a bounded same-carrier computational counterexample to the
promotion from finite static liftability to deterministic dynamic closure.

**Boundary.** The paper reports exact finite certificates and bounded
computational observations. It does not establish physiological
excitation/inhibition, causal signal propagation, biological competence,
partition superiority, all-depth liftability, or closure at higher memory
orders.

**Keywords.** connectome; coarse-graining; quotient support; routed
composition; lumpability; dynamic closure; representation loss; MaleCNS

---

## Notation Table {.unnumbered}

| symbol | meaning |
| --- | --- |
| $V$ | finite node set of the registered carrier |
| $V=\bigsqcup_{i\in I}V_i$ | declared sectorization |
| $Q_i$ | coordinate projector onto sector $V_i$ |
| $Y$ | registered microscopic operator or carrier matrix |
| $\operatorname{Path}^{\rm quot}_d$ | depth-$d$ paths admitted by consecutive quotient support |
| $\operatorname{Route}_d[Y]$ | depth-$d$ sector words with nonzero projected product |
| $F_Y$ | registered deterministic microscopic update under carrier $Y$ |
| $O$ | declared coarse observation map |
| $\overline F$ | putative deterministic coarse update |
| $\Psi_1(x)$ | one-lag coarse history $(O(F_Yx),O(x))$ |
| $\mathrm{LP}_d$ | finite depth-$d$ liftability proportion |
| $Y_{\rm known+}$ | known-sign support with positive weights |
| $Y_{\rm known\pm}$ | signed, normalized transmitter-proxy carrier |
| `superclass`, `somaSide` | registered MaleCNS sectorizations |

---

## 1. Introduction

A connectome is simultaneously a graph, a weighted operator, a source of
candidate routes, and a substrate for dynamical models. These roles are often
compressed into one informal statement: if two coarse regions are connected,
information can flow between them, and if their aggregate activity can be
observed, that activity can be evolved as a coarse state. Neither promotion is
automatic.

The first issue is compositional. A quotient support graph forgets which
microscopic relay realizes each adjacent sector transition. Consecutive
quotient edges can therefore be supported by incompatible relays. Even when a
microscopic route exists, signed route families may cancel in the projected
operator product. The correct object is not merely a graph path but a
carrier-qualified routed product.

The second issue is dynamical. An observation $O(x)$ may be well-defined,
reproducible, and useful for description while failing to determine
$O(F_Yx)$. In that case the observation is not a deterministic state for the
registered dynamics. Prediction quality and exact factorization are also
different: a fitted predictor may approximate an output without making the
microscopic update constant on observation fibers.

This paper audits these distinctions on the MaleCNS v1.0 connectome
\cite{berg2026malecns}. The dataset provides a whole adult male central nervous
system spanning brain and nerve cord. Its scale makes representation loss
unavoidable, but scale alone does not determine which representations preserve
which structures. This leads to one controlled question:

> **Which structural information survives successive coarse representations
> strongly enough to remain compositional, dynamically consequential,
> observable, and state-sufficient?**

The audit follows the chain

$$
\boxed{
\begin{gathered}
\text{support}\longrightarrow\text{routed composition}
\longrightarrow\text{signed operator}\\
\longrightarrow\text{dynamics}\longrightarrow\text{observation}
\longrightarrow\text{dynamic closure}
\end{gathered}}
\tag{1.1}
$$

Each arrow requires its own certificate. Failure at one arrow does not erase
validity at an earlier layer, and success at an earlier layer does not certify
a later one. Figure 1 summarizes the typed audit.

![The six-layer descent stack audited in this paper. Each arrow requires an
explicit descent certificate; no arrow is automatic.](../../figures/paper16/fig1_descent_stack.png)

### 1.1 Contributions

The paper makes four contributions.

1. **A common descent language.** Three elementary propositions formalize
   route-to-path inclusion, deterministic fiber closure, and one-lag history
   closure. They provide exact gates for the empirical audits.
2. **A structural support audit.** Three MaleCNS sectorization policies show
   that coverage admission and relay admission are distinct. The strongest
   nested contrast is 781/782 versus 374/812 lifted additions.
3. **A signed dynamic and observation audit.** Matched-support sign changes and
   alternative observation functionals are shown to affect different layers
   of the registered response.
4. **A same-carrier counterexample.** On $Y_{\rm known\pm}$, somaSide has
   complete exact liftability at depths two and three while failing
   deterministic first-order dynamic closure. Static liftability and dynamic
   state sufficiency therefore require separate certificates even on the same
   carrier and partition.

### 1.2 Nonclaims

The analysis does not infer physiological excitation or inhibition from the
transmitter proxy, does not identify causal biological circuits, and does not
model living-fly behavior. It does not rank sectorizations by the magnitude of
their raw closure defects. It does not claim all-depth liftability, closure or
nonclosure at memory order $k\ge2$, or a universal theorem about biological
coarse-graining.

---

## 2. Related Work and Novelty Boundary

State aggregation and lumpability ask when a projected process retains a
closed stochastic description. Classical finite-state treatments formulate
first-order lumpability through consistency of transition probabilities on
partition blocks \cite{kemenySnell1976}. Higher-order lumpability separates
first-order Markov closure from closure after retaining a finite observation
history \cite{geigerTemmel2014}. The deterministic fiber criteria used below are
the corresponding elementary factorization statements for a fixed map and a
declared observation domain. This paper does not claim lumpability theory as
new.

Exact coarse-graining can also be recovered by choosing collective variables
designed to preserve particular dynamical quantities. Lu and Vanden-Eijnden,
for example, construct collective variables that preserve transition-order
and first-passage information without assuming time-scale separation
\cite{luVandenEijnden2014}. The question here is different: the observation maps are
fixed biological annotations, and the audit asks whether those already
declared maps satisfy exact finite factorization criteria.

Network quotient constructions likewise require compatibility between graph
structure and dynamics. Graph fibrations can induce exact maps between
networked dynamical systems under declared structural hypotheses
\cite{devilleLerman2015}, while connectome coarse-graining studies typically
test which dynamical features survive a selected aggregation
\cite{koraSimon2024}. These results motivate, but do not replace, the
carrier-specific route and fiber checks performed here.

The MaleCNS release supplies the anatomical substrate and annotation surface
\cite{berg2026malecns,maleCNSdownload}. Neurotransmitter labels derived from
electron microscopy are valuable connectomic annotations, but their status is
predictive and does not by itself determine receptor-specific postsynaptic
effect \cite{eckstein2024}. Accordingly, $Y_{\rm known\pm}$ is called a
transmitter-proxy signed carrier, not a physiological excitation/inhibition
matrix.

Within the RIME program, Paper VIII distinguishes labelled operator carriers
from quotient support and closure objects \cite{paper8}, Paper XX develops
all-depth carrierwise route criteria \cite{paper20}, and Paper XXIV states the
general discipline that structure descends through a lossy map only under an
explicit compatibility condition \cite{paper24}. The present paper contributes a
large-connectome case study with two features not supplied by those abstract
interfaces: source-bound MaleCNS computations and a same-carrier separation
between complete finite static liftability and failed deterministic dynamic
closure.

The novelty claim is therefore deliberately narrow. It is not a new general
theory of lumpability, graph quotienting, or connectome dynamics. The
contribution is a typed, source-addressed audit that keeps structural support,
routed composition, signed dynamics, observation visibility, and state closure
from being silently identified.

---

## 3. Typed Descent Criteria

### 3.1 Quotient Paths and Routed Products

Let $V=\bigsqcup_{i\in I}V_i$ be a finite partition with coordinate
projectors $Q_i$, and let $Y\in\operatorname{End}(\mathbb K^V)$. A sector word
$\mathbf i=(i_0,\ldots,i_d)$ is quotient-supported when every consecutive
block is nonzero:

$$
Q_{i_r}YQ_{i_{r-1}}\ne0,
\qquad 1\le r\le d.
$$

It is routed-active when the full projected product is nonzero:

$$
Q_{i_d}YQ_{i_{d-1}}Y\cdots YQ_{i_0}\ne0.
$$

Write the corresponding sets as $\operatorname{Path}^{\rm quot}_d$ and
$\operatorname{Route}_d[Y]$.

> **Proposition 3.1 (Route-to-path inclusion).** For every finite declared
> sectorization and operator $Y$,
> $$
> \operatorname{Route}_d[Y]\subseteq
> \operatorname{Path}^{\rm quot}_d.
> $$
> Equality requires an additional carrier-qualified lifting condition.

*Proof.* If one consecutive factor $Q_{i_r}YQ_{i_{r-1}}$ vanishes, then the
full product containing that factor vanishes. Hence every active routed word
is quotient-supported. The reverse implication can fail because the images
and kernels of adjacent blocks need not align. Over signed carriers, distinct
microscopic contributions can also cancel. $\square$

For nonnegative adjacency data, nonzero matrix entries can be interpreted as
microscopic chains, so failure typically comes from incompatible relays. For
signed operators, Boolean route existence is only an intermediate check:
exact projected accumulation is still required.

### 3.2 Deterministic Dynamic Closure

Let $X$ be a microscopic state set, $F:X\to X$ a deterministic update, and
$O:X\to Z$ an observation map. The map $O$ closes at first order on a
declared domain $D\subseteq X$ when there is a map
$\overline F:O(D)\to Z$ such that

$$
O(Fx)=\overline F(Ox),\qquad x\in D.
\tag{3.1}
$$

> **Proposition 3.2 (Deterministic fiber criterion).** A map
> $\overline F$ satisfying (3.1) exists if and only if
> $$
> O(x)=O(y)\Longrightarrow O(Fx)=O(Fy)
> \qquad (x,y\in D).
> \tag{3.2}
> $$

*Proof.* If $\overline F$ exists, (3.2) follows by applying it to the common
observation. Conversely, define $\overline F(z)=O(Fx)$ for any $x\in D$ with
$O(x)=z$. Condition (3.2) makes this definition independent of the chosen
representative. $\square$

A pair violating (3.2) is an exact obstruction to deterministic first-order
closure on the declared domain. It is not merely a prediction error. A small
numerical discrepancy may still require tolerance analysis, but once the
source states are exactly co-observed and their successors differ under the
registered arithmetic, no deterministic factorization exists on that domain.

### 3.3 One-Lag Closure

Define the one-lag history map and its target by

$$
\Psi_1(x)=\bigl(O(Fx),O(x)\bigr),
\qquad
T_2(x)=O(F^2x).
$$

> **Proposition 3.3 (One-lag history-fiber criterion).** There exists a map
> $G:\Psi_1(D)\to Z$ satisfying $T_2=G\circ\Psi_1$ on $D$ if and only if
> $$
> \Psi_1(x)=\Psi_1(y)\Longrightarrow T_2(x)=T_2(y)
> \qquad (x,y\in D).
> \tag{3.3}
> $$

*Proof.* This is Proposition 3.2 applied to the source map $\Psi_1$ and target
$T_2$. $\square$

Failure of (3.3) proves only that one retained lag is insufficient on the
declared domain. It says nothing about closure at order $k\ge2$, stochastic
closure, or approximate predictive adequacy.

The three propositions separate the paper's object types:

$$
\boxed{
\text{quotient visibility}
\ne \text{routed composition}
\ne \text{dynamic state sufficiency}.}
\tag{3.4}
$$

---

## 4. MaleCNS Data and Registered Objects

### 4.1 Dataset and Provenance

The source dataset is MaleCNS v1.0, released as a complete adult male
Drosophila central nervous system connectome with brain and nerve cord
annotations \cite{berg2026malecns,maleCNSdownload}. Its registered neuPrint
identifier is `male-cns:v1.0`. The paper-owned
provenance record binds the annotation table, neurotransmitter table, and
directed table of body-pair connection counts by exact file size and SHA-256. The
dataset license is recorded separately from the repository code license.

The computations use body-pair detected-connection counts rather than a claim
of biological synaptic efficacy. Annotation values, including `<missing>`, are
data values in a declared operational partition. They are not silently
imputed. The named-sector follow-up in Section 7 explicitly separates a
biologically named superclass from the missing-label bucket.

### 4.2 Static and Dynamic Carriers

The initial static audit uses a nonnegative MaleCNS adjacency carrier to test
whether quotient-supported sector words have microscopic relay realizations.
The dynamic line constructs a node-level carrier and then a normalized signed
operator $Y_{\rm known\pm}$ from the registered known-sign subset. The signed
labels are transmitter proxies. They do not encode receptor composition,
co-transmission, or postsynaptic physiological sign.

The stored operator uses source rows and target columns. State propagation is
therefore the incoming-action convention $x\mapsto Y_{\rm known\pm}^{\mathsf
T}x$; routed products retain the corresponding source-to-target order. This
orientation is part of the registered carrier and is not interchangeable with
left multiplication by the stored matrix.

**Registered dynamics.** Let $W$ denote the frozen signed known-transmitter
matrix and set

$$
s_u=\sum_v|W_{uv}|,
\qquad
Y_{uv}=\begin{cases}
W_{uv}/s_u,&s_u>0,\\
0,&s_u=0.
\end{cases}
$$

The deterministic update used in the dynamic audits is

$$
F_Y(x)=(1-\alpha)x+\alpha\,\phi(\gamma Y^{\mathsf T}x),
\qquad
\phi(z)_v=\min\{x_{\max},\max\{0,z_v\}\}.
\tag{4.1}
$$

The registered values are $\alpha=0.2$, $\gamma=1$, and $x_{\max}=1$, with
zero external input and no stochastic noise. For a declared partition
$V=\bigsqcup_iV_i$, the observation is the sector-mean vector

$$
O_i(x)=\frac{1}{|V_i|}\sum_{v\in V_i}x_v.
\tag{4.2}
$$

The dynamic carrier admits 211,577 nodes and 26,028,386 directed edges in its
full support. The known-sign support used by $Y_{\rm known\pm}$ contains
25,214,058 directed edges, or 96.871385% of admitted edges, and covers
97.929437% of raw-weight mass. The matched-support positive control
$Y_{\rm known+}$ retains the same support and
absolute edge magnitudes while removing the registered sign assignment.

### 4.3 Sectorizations and Observations

Two partitions are central:

- `superclass`, a 28-dimensional operational annotation partition in the
  dynamic comparison;
- `somaSide`, a four-dimensional side-based partition.

For a partition $V=\bigsqcup_iV_i$, the dynamic observation is the vector of
sector means. These means are descriptive estimands. Their existence and
reproducibility do not imply Proposition 3.2.

### 4.4 Evidence Classes

The exact route audits and the named-sector finite history witness are
Computational Certificates: finite enumerations bound to declared inputs and
exact arithmetic checks. The signed dynamics, observation-resolution ratios,
and registered closure defects are Computational Observations. The release
validator performs local closure verification; it does not constitute an
independent validation of the scientific model.

---

## 5. Static Structural Descent

### 5.1 Coverage Admission Is Not Relay Admission

The depth-two audit compares three nested sector-universe policies. A
quotient-supported triple is counted as lifted only when the declared
microscopic relay condition is satisfied.

| policy | quotient-supported triples | lifted triples | liftability |
| --- | ---: | ---: | ---: |
| typed-core | 6,237 | 4,970 | 0.7969 |
| relay-strict | 7,019 | 5,751 | 0.8193 |
| coverage-inclusive | 7,831 | 6,125 | 0.7821 |

The nested additions are more informative than comparing the three ratios as
if they were estimates on a common denominator:

| enlargement | newly supported | newly lifted | conditional liftability |
| --- | ---: | ---: | ---: |
| typed-core to relay-strict | 782 | 781 | 99.87% |
| relay-strict to coverage-inclusive | 812 | 374 | 46.06% |

The first enlargement almost always contributes usable relays. The second
adds many labels that increase coverage without supplying compatible
microscopic composition. Thus

$$
\boxed{\text{coverage-admissible}\ne\text{relay-admissible}.}
\tag{5.1}
$$

This is a finite audit of the registered carrier and policies. It is not a
universal statement about annotation systems, and the observed percentages
are not biological transmission probabilities.

### 5.2 Exact Signed Liftability on the Dynamic Carrier

The static/dynamic comparison must use the same carrier. The follow-up audit
therefore recomputes route activity directly on $Y_{\rm known\pm}$ rather
than importing nonnegative relay existence. Its decision hierarchy is:

1. a unique microscopic route gives exact nonzero activity;
2. a sign-homogeneous route family gives exact nonzero activity;
3. otherwise exact rational accumulation and modular checks decide the
   projected product;
4. absence of a microscopic route is recorded separately from cancellation.

For somaSide, every quotient-supported word is active:

| depth | quotient-supported words | exact nonzero routes | $\mathrm{LP}_d$ |
| --- | ---: | ---: | ---: |
| 2 | 64 | 64 | 1 |
| 3 | 256 | 256 | 1 |

For superclass, the corresponding counts are 3,667/4,783 at depth two and
41,247/67,562 at depth three. Every zero in the superclass audit is classified
as absence of a microscopic route; no unresolved or cancellation zero remains
in the registered result.

The somaSide statement is complete only at the two audited depths. It does not
imply $\mathrm{LP}_d=1$ for arbitrary $d$.

---

## 6. Signed Semantics and Observation Resolution

### 6.1 Matched Support, Different Signed Dynamics

The signed-dynamics control separates support loss from sign assignment:

$$
Y_{\rm full+}\longrightarrow Y_{\rm known+}
\longrightarrow Y_{\rm known\pm}.
$$

The second transition preserves support and absolute magnitudes, changing only
the registered transmitter-proxy signs. Across the frozen gain grid, the
cosine distances between $Y_{\rm known+}$ and $Y_{\rm known\pm}$ responses
are 0.84668, 0.87846, and 0.90458 for $\gamma=0.9,1.0,1.1$. The corresponding
coverage-reference distances between $Y_{\rm full+}$ and $Y_{\rm known+}$ are
0.00416, 0.00598, and 0.00770.

This establishes a model-relative separation: on the registered grid, the
matched-support sign assignment changes response allocation much more than
the registered coverage loss. It does not validate the proxy as physiological
excitation/inhibition, nor does it identify a causal circuit.

### 6.2 The Observation Functional Changes Visibility

The observation-resolution audit retains the registered node-level paired
trajectory and changes only the readout. Mean, RMS, 95th-quantile, and local
observations expose substantially different magnitudes of the same
model-relative perturbation.

| source stratum | RMS / mean | q95 / mean | local / mean |
| --- | ---: | ---: | ---: |
| small | 8.7141 | 2.0207 | 24.0335 |
| medium | 7.0140 | 1.5190 | 3.8780 |
| large | 8.7840 | 2.2083 | 36.4267 |

The comparison does not privilege one observation as biologically correct.
It shows that effect visibility is a property of the pair

$$
(\text{registered dynamics},\text{observation functional}),
$$

not of the microscopic perturbation alone. Figure 2 collects the principal
registered contrasts.

![Principal frozen contrasts. Values are descriptive coordinates from the
declared audits; bars across different panels do not share a scientific unit
or denominator.](../../figures/paper16/fig2_registered_contrasts.png)

---

## 7. Dynamic Closure and Memory

### 7.1 First-Order Fiber Failure

The D2.1 protocol fixes $Y_{\rm known\pm}$, the superclass-mean observation,
$\gamma=1$, $\alpha=0.2$, zero input, and a unit-state first-reference domain.
It then tests Proposition 3.2 directly. The result is

$$
\texttt{FAILED\_FIRST\_ORDER\_MARKOV\_CLOSURE}.
$$

More explicitly, with $e_a$ the unit state at node $a$ and $s_a$ the absolute
outgoing-row mass defined in Section 4.2, the declared domain is

$$
D=\{e_a:s_a>0\}.
\tag{7.1}
$$

The fiber key is the superclass containing $a$, since all unit states in the
same sector have the same $O(e_a)$. Within each sector, candidate nodes are
scanned in increasing registered node index; the first candidate is retained
as the reference and every later candidate is compared only with that
reference. Consequently the witness count below is a count of detected
first-reference inconsistencies, not a count of all hostile pairs.

The finite scan records 141,296 first-reference inconsistency witnesses and a
primary reference L1 defect of 0.005651574473947287. The count is not an
obstruction prevalence estimate, and the defect is a witnessed lower bound,
not a complete fiber diameter.

The conclusion is exact at the logical level of the registered witness:
superclass mean is not a deterministic first-order state on the declared
domain. The numerical magnitude is not a measure of biological importance.

### 7.2 One Coarse Lag Still Fails

The D2.2 protocol tests Proposition 3.3 with

$$
\Psi_1(x_0)=(z_1,z_0),
\qquad
T_2(x_0)=z_2.
$$

The history equality gate is exact. For $e_a\in D$, define the positive mass
sent from $a$ into target sector $V_j$ by

$$
p_{aj}=\sum_{v\in V_j:\,W_{av}>0}W_{av},
\qquad
g_a=\gcd(s_a,p_{a1},\ldots,p_{am}).
$$

If $i(a)$ is the source-sector index, the canonical history signature is the
integer tuple

$$
h(a)=\left(i(a),\frac{s_a}{g_a},
\frac{p_{a1}}{g_a},\ldots,\frac{p_{am}}{g_a}\right).
\tag{7.2}
$$

Thus equality is tested by reduced integers, without floating-point
tolerance; the computed trajectories are used only as a numerical
cross-check and to test successor separation. This signature produces 119,138
groups, of which 5,745
contain collisions, comprising 50,046 states. The frozen first witness has a
history cross-check error of $2.117582368135751\times10^{-22}$ and a successor
L1 separation of $2.567412844075076\times10^{-7}$.

That first witness lies in the operational `<missing>` superclass bucket. To
separate closure failure from a missing-annotation artifact, an additive
hostile follow-up preserves the original receipt and searches only named
sectors in deterministic order. It finds an exact history-fiber witness in
`cb_intrinsic` after examining 5,367 ordered candidate pairs. The two source
states have identical registered one-lag histories and differ in nine exact
coordinates of the next observation.

The follow-up strengthens the partition-level obstruction. It remains an
operational annotation result, not a biological mechanism claim. No test of
$k\ge2$ is reported.

### 7.3 Representation-Relative Failure

The D2.3 protocol repeats the first-order test on the same carrier and dynamic
settings for superclass mean and somaSide mean.

| observation | dimension | collision fibers | witnesses | reference L1 defect |
| --- | ---: | ---: | ---: | ---: |
| superclass mean | 28 | 22 / 25 | 141,296 | 0.005651574473947287 |
| somaSide mean | 4 | 4 / 4 | 163,435 | 0.0004874856094383272 |

The collision fibers contain 163,436 and 163,439 states, respectively. Both
observations fail first-order closure. The raw defect magnitudes cannot
rank the partitions: their dimensions, sector-size profiles, compression
ratios, and fiber geometries differ. A no-witness result under either scan
would have meant only that no obstruction was found on the registered domain,
not a proof of closure.

---

## 8. Same-Carrier Static and Dynamic Separation

The strongest cross-layer result combines Sections 5.2 and 7.3 without
changing the carrier or partition:

$$
\begin{aligned}
Y&=Y_{\rm known\pm},\\
\mathrm{LP}_2(\text{somaSide};Y)&=64/64=1,\\
\mathrm{LP}_3(\text{somaSide};Y)&=256/256=1,\\
\text{somaSide first-order closure under }F_Y&=\texttt{FAILED}.
\end{aligned}
\tag{8.1}
$$

Here ``same carrier'' means the same frozen node basis, edge weights, signs,
and outgoing-row normalization. Routed products use the registered
source-row/target-column storage convention for $Y$, whereas $F_Y$ uses the
registered transpose action in (4.1). These are two declared uses of the same
operator bytes, not different carriers.

> **Computational Certificate 8.1 (Signed liftability).** On the frozen
> signed, normalized $Y_{\rm known\pm}$ carrier, every somaSide
> quotient-supported word of depths two and three has an exact nonzero
> projected product.

> **Computational Observation 8.2 (Dynamic fiber obstruction).** On the same
> carrier and somaSide partition, the registered first-order dynamic map is not
> constant on observation fibers.

Together they yield the bounded same-carrier statement:

$$
\boxed{
\text{perfect static liftability at depths 2 and 3}
\not\Rightarrow
\text{deterministic first-order dynamic closure}.}
\tag{8.2}
$$

The antecedent is finite-depth and the consequent is domain-qualified. Thus
(8.2) is a computational counterexample to a particular promotion, not a
general theorem that static liftability and dynamic closure are unrelated.
The two properties can coexist under stronger hypotheses; they simply do not
follow from one another here.

The reason is structural. Static liftability asks whether declared finite
sector words have nonzero microscopic realization. Dynamic closure asks
whether all microscopic states identified by an observation have identical
observed successors. The latter depends on amplitudes within observation
fibers, not only on the existence of short inter-sector routes.

---

## 9. Discussion

### 9.1 Observability, Predictability, and Closure

The case study supports a three-way distinction:

$$
\boxed{\text{observability}\ne\text{predictability}\ne\text{closure}.}
\tag{9.1}
$$

Observability means that a declared statistic can be computed from the state.
Predictability concerns the performance of a model under a declared loss and
distribution. Closure is an exact factorization statement. A predictive model
may be useful in the absence of closure, while a closure theorem requires the
fiber condition regardless of empirical fit.

This distinction matters for connectome-scale modeling because annotations
are often designed for biological description rather than dynamical
sufficiency. The failure of superclass or somaSide mean to close does not make
those annotations invalid. It states only that additional state, memory,
stochasticity, or approximation is needed if they are used as autonomous
dynamic variables.

### 9.2 Static Support Is an Observation, Not a Dynamics

A quotient graph is a valuable summary of possible adjacency. Its paths are
not automatically compositional routes, and compositional routes are not
automatically a closed coarse dynamics. The MaleCNS audits display both gaps:
coverage-inclusive support admits many nonlifting triples, while complete
somaSide lifting at two finite depths does not repair the dynamic fiber
obstruction.

The general methodological rule is:

> **Never infer preservation of a structure through a lossy representation
> without a descent theorem or a carrier-qualified certificate.**

This rule is not anti-compression. It identifies what must accompany a
compression if a particular downstream operation is to remain meaningful.

### 9.3 Sign and Readout Are Separate Modeling Choices

The matched-support sign control shows that identical graph support and edge
magnitudes do not determine the registered dynamic response. The observation
audit then shows that one node-level response does not determine its measured
visibility independently of the readout. These are separate modeling layers:

$$
\text{support}\quad|\quad\text{operator semantics}
\quad|\quad\text{observation semantics}.
$$

The vertical bars are type boundaries, not an order relation. Each layer can
be varied while holding part of the others fixed.

### 9.4 Limitations

The study uses one connectome release, registered annotation partitions, one
family of deterministic dynamics, and finite test domains. Transmitter labels
are proxies; receptor-specific sign and neuromodulatory effects are absent.
The closure scans are not prevalence estimators. The finite route certificate
stops at depth three, and the memory audit stops at one lag. The paper makes no
claim that the tested dynamics are a faithful behavioral model of the fly.

The strongest result is therefore methodological and object-relative: static
liftability, signed response, observation visibility, and deterministic
closure are distinct properties, and the registered MaleCNS carrier supplies
explicit controls separating them.

---

## 10. Claim Status and Boundary

| ID | statement | evidence level | boundary |
| --- | --- | --- | --- |
| C1 | Quotient support can overstate compositional realizability. | Computational Certificate | Registered finite carrier and depths only. |
| C2 | Coverage admission and relay admission differ. | Computational Certificate | No causal or physiological interpretation. |
| C3 | Matched-support transmitter-proxy signs alter the registered response. | Computational Observation | Not receptor-validated E/I. |
| C4 | Observation functional changes visibility of a fixed model-relative effect. | Computational Observation | No universally privileged readout. |
| C5 | Registered superclass mean fails deterministic first-order closure. | Computational Observation | Declared domain and tolerance only. |
| C6 | One lag does not restore closure; a named-sector exact witness exists. | Computational Certificate | No claim for $k\ge2$ or all finite memory. |
| C7 | Both tested mean representations fail first-order closure. | Computational Observation | Raw defects do not rank partitions. |
| C8 | On $Y_{\rm known\pm}$, somaSide has exact $\mathrm{LP}_2=\mathrm{LP}_3=1$ while first-order closure fails. | Computational Observation | Finite-depth, same-carrier counterexample only. |

The overall paper remains a **Computational Observation** because its main
cross-layer conclusion consumes both exact finite certificates and
model-relative numerical dynamics.

No result establishes physiological excitation/inhibition, biological signal
propagation, causal necessity, behavior, learning, intelligence,
consciousness, partition optimality, or a universal coarse-graining theorem.

---

## 11. Conclusion

The MaleCNS case study separates five objects that are easy to conflate:
quotient support, microscopic routed composition, signed operator semantics,
observed response, and closed coarse state. Exact path lifting and deterministic
fiber factorization provide different gates because they preserve different
structures.

The finite audits show that coverage can exceed compositional relay support,
matched support can conceal large signed dynamic differences, and a fixed
node-level effect can appear very different under alternative readouts. Most
decisively, somaSide is perfectly liftable through depths two and three on the
same signed carrier for which its first-order observed dynamics fail to close.

The resulting principle is simple: a lossy representation may remain valid
for one purpose and fail for another. The correct response is neither to reject
coarse representations nor to treat them as autonomous by default, but to
state the structure being preserved and require the corresponding descent
certificate.

---

## Appendix A: Computational Artifacts

The paper-owned release closure is under
[`experiments/paper16/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper16)
in the [RIME repository](https://github.com/dooven-prime/rime-lite). The exact
source and producer subset consumed by this paper is
published under `source/`; unrelated exploratory work is not part of the
release identity. The three upstream MaleCNS tables remain external official
inputs bound by URL, byte size, and SHA-256. Large derived carrier arrays are
rebuilt in scratch and compared with their registered byte identities.

| role | short path |
| --- | --- |
| selected source and producers | `source/` |
| portable scientific artifacts | `source/**/results/` |
| static-audit replay receipt | `results/static-audits-replay.v1.receipt.json` |
| dynamic-descent replay receipt | `results/dynamic-descent-replay.v1.receipt.json` |
| exact A1/A2 replay receipt | `results/a1-a2-exact-replay.v1.receipt.json` |
| upstream dataset provenance | `upstream-provenance.v1.json` |
| release manifest | `release-manifest.v1.json` |

The release manifest binds exact paths, byte sizes, SHA-256 digests, roles,
and claim ownership. Large carrier outputs are referenced through a
clean-clone producer-replay receipt. Portable artifact regeneration replaces
machine-local locator strings with paper-owned relative paths without changing
the scientific payload.

The validation graph is acyclic:

$$
\text{source and producer}
\longrightarrow \text{artifact}
\longrightarrow \text{receipt}
\longrightarrow \text{release manifest}
\longrightarrow \text{external anchor}.
$$

The release-closure receipt performs local closure verification. Separate
paper-owned receipts record clean scratch replay and exact-byte agreement for
the six static artifacts, six v0.1--v0.2 dynamic-descent artifacts, and the
corrected A1/A2 producers. None of these receipts independently validates the
scientific semantics, and no receipt occurs in its own transitive closure.
Embodied finite-null results and inverse-identifiability experiments are
outside this paper's release identity.
