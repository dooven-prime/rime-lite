# Observable Classification Theory for SOFs

### Wall Records, Observable Invariants, Taxonomy, and Smooth Local Models

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part XI of the RIME program. Paper VII isolates generic
accessibility completion; Paper VIII fixes the static SOF object layer; Paper IX
studies observable dynamics over SOFs; and Paper X isolates the Universal
Observable Pipeline together with a five-layer SOF Registry. Paper XI turns
that registry into an observable classification layer: given registered SOFs,
what feature space classifies their observable behavior?*

***

## Abstract

**Problem.** The SOF Registry records species, SOF objects, observable
ladders, dynamics, and diagnostics. This makes cross-species comparison
possible, but it does not yet say what type a registered SOF has at the
observable level. The next question is not whether every wall belongs to a
known singularity class. The question is which observable signatures and
invariants classify the behavior of registered SOFs.

**Approach.** We introduce a four-layer organization. First, **wall records**
collect where observable changes occur: rank jumps, support jumps,
accessibility jumps, plateau intervals, collision loci, terminal boundaries,
and related discriminants. Second, **wall signatures** upgrade a wall from an
event to an observable signature: rank type, support type, repair type,
oscillation type, plateau type, or equivalently changes such as
$(\Delta R_1,\Delta R_2,\Delta D,\Delta\tau,\Delta P_d)$. Third, the ordered
sequence of signatures along a deformation is an **observable wall record**,
and the multiset of such signatures is the **wall spectrum**
$\mathrm{Spec}_W(\mathcal F)$. Fourth, the **Observable Wall Taxonomy** groups
wall spectra into collision, repair, terminal-side, plateau/rate,
nonsmooth/discrete, and bridge/incidence wall families. Smooth ADE models
enter only afterward as candidate local
normal forms for sufficiently smooth discriminant branches.

**Results.** The main result is an observable classification schema, not a
complete classification theorem. It turns wall records into computable
features such as crossing count, wall-cell count, repair index, oscillation index, depth index,
rate ratio, spectral gap, and codimension. The schema is supported by
cross-species and spectral audits: Rubik spectral
snapshots, a Rubik spectral-deformation audit with 16 pairwise $A_1$-type
collision candidates and simultaneous pair-gap response diagnostics,
a 2D commutativity-discriminant slice with one hit on the chosen
$20\times20$ evaluation grid, activation-wall diagnostics,
quantum accessibility contrasts, Markov frozen-pair diagnostics, graph
Laplacian spectral-gap sensitivity, a barrier-option stopping-sector
diagnostic, and a transformer activation-sector diagnostic. The audits show
that registered species expose distinct wall types and that several important
cases are discrete, piecewise-smooth, degenerate, stochastic, activation-based,
or mechanism-specific rather than smooth ADE-type singularities.
A separate 24-record coverage census contains 15 initially eligible records.
Classes B--F meet the provisional three-record, two-species, two-deformation
curation target; Class A remains a single-species Rubik gap.
An observable-status trajectory audit records 190 sampled pair-status changes
for a three-step GridWorld obstacle path, 4 changes at the isolated SIR
$\beta=0$ boundary, and 6 changes at the terminal point of a graph edge-weight
path. A definition-compatible redundancy audit over 166 configurations finds
that 3 empirical principal components explain both 90% and 95% of snapshot
variance for the tested ensemble; this PCA summary is
ensemble-composition dependent and does not produce a six-invariant basis theorem. Finally, a
block-restricted eigenbranch-continuation audit finds no
$A_2\to A_1+A_1$ split candidate on the tested Rubik slices.

**Implications.** Paper XI narrows the classification problem and supplies the
feature-extraction layer for later diagnostics. ADE-type local
models may be useful for spectral collision or smooth discriminant maps, but
they cannot be the default language for all SOF walls. RIME at this stage controls
wall location and observable diagnostics; it does not yet provide general
wall-crossing transformation laws. A full taxonomy must first distinguish
wall records, wall signatures, taxonomy classes, and smooth local models.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $\mathcal F=(V,\{Q_i\},\mathcal X)$ | Sectorized Observable Framework |
| $\mathcal F_t$ | SOF deformation |
| $O(t)$ | observable trajectory or shadow |
| $\Sigma_O$ | wall or discriminant locus of $O$ |
| $\Sigma_{\mathrm{comm}}$ | commutativity locus in generator-weight moduli |
| $\Delta_O$ | target discriminant in observable space |
| $\mathcal W(\mathcal F,\mathcal L,\Gamma)$ | wall record for a SOF object, observable ladder, and deformation geometry |
| $W_i$ | one observable wall signature event in a deformation record |
| $\mathrm{Sig}_W(\mathcal F)$ | computable wall signature |
| $\mathrm{Spec}_W(\mathcal F)$ | multiset of wall signatures |
| $\mathrm{WallAssign}$ | record-producing assignment $(\mathcal F,\mathcal L,\Gamma)\mapsto \mathcal W$ |
| $N_{\mathrm{cross}},N_{\mathrm{cell}}$ | crossing count and wall-cell count |
| $R_W,p_W,O_W,P_W$ | repair, persistence, oscillation, and plateau indices |
| $\bar D,\rho_W,\gamma_W,c_W,\delta_W$ | depth, rate-ratio, spectral-gap, codimension, and density diagnostics |
| $R_1,R_2,D$ | accessibility observable ladder |
| $\tau(O)$ | characteristic time scale when defined |
| $P_d(t)$ | plateau function |
| $A_k,D_k,E_k$ | Arnold ADE singularity families |

***

## Introduction

The post-Paper-VII SOF arc has three layers:

| Paper | Role |
|-------|------|
| Paper VIII | SOF object layer |
| Paper IX | observable trajectories over SOFs |
| Paper X | Universal Observable Pipeline and five-layer SOF Registry |

Paper XI asks what comes after the registry.

The registry is a taxonomy input:

species $\to$ SOF object $\to$ observable ladder $\to$ dynamics $\to$
diagnostics.

Paper X records which SOFs exist and how they enter the observable pipeline.
Paper XI asks what observable type those SOFs have. In other words, the
registry is a list of realized species, while Paper XI extracts the observable
features by which those species can be compared.

Paper XI asks whether registered wall records can be grouped into classes. The
answer is not yet a complete classification. The safe claim is that the
classification problem splits into observable signatures, wall spectra,
invariants, normal forms, and smooth local models.

This paper is deliberately conservative. It does not claim that Arnold ADE
classification applies to all SOF walls. It treats ADE as one candidate local
model for sufficiently smooth discriminant-like wall records and records where
that language does not apply. The organizing object is the wall record, not an
ADE class.

The RIME papers up to this point mostly control **wall location**: where support,
rank, accessibility, plateau, or collision behavior changes. They do not yet
give a general wall-crossing law for how all invariants transform across every
wall. Paper XI therefore asks a prior organizational question: what kinds of
observable walls have been registered, and how should they be organized before
any transformation law is attempted?

The answer has four layers:

| Layer | Object | Question |
|-------|--------|----------|
| Wall Records | loci and observable changes | Where do walls occur? |
| Wall Signatures | computable invariants of records | What does the wall look like? |
| Observable Wall Taxonomy | classes of signatures | What type of wall is it? |
| Smooth Wall Models | local smooth-discriminant models | When can ADE-like tools apply? |

For later diagnostic reports, the same layer becomes a feature extractor. An
application-facing SOF report need not use theorem proofs directly. It can
emit quantities such as crossing count, wall-cell count, repair index, plateau or oscillation
index, and depth index, then interpret them as observable diagnostics.

This also extends the categorical architecture begun in Paper VIII:

$$
\begin{aligned}
\text{Source}
&\to \mathsf{SOF}_{\mathrm{str}}
\to \text{Observable ladder}
\to \text{Observable dynamics}\\
&\to \text{Wall records}
\to \text{Observable invariants}
\to \text{Wall taxonomy}.
\end{aligned}
$$

Paper XI does not prove that this last passage is a categorical invariant of
SOFs. It introduces the record-producing layer needed to make the passage
explicit once the observable ladder and deformation geometry have been chosen.

***

## Wall Records

### Definition

A **wall record** for a SOF deformation is the data

$$
\mathcal W(\mathcal F_t,O)
=
(\mathcal F_t,\ O(t),\ \Sigma_O,\ \Delta_O,\ \mathcal D_O),
$$

where:

1. $\mathcal F_t$ is a specified SOF deformation;
2. $O(t)$ is an observable shadow or continuous observable field;
3. $\Sigma_O$ is the locus where the observable changes qualitative type;
4. $\Delta_O$ is the target discriminant when a pullback description exists;
5. $\mathcal D_O$ is the measured diagnostic package, such as $\tau(O)$,
   repair, plateau, frozen-pair count, or spectral-gap change.

The wall record is the object that Paper XI attempts to classify.

### Wall Assignment

Paper VIII defines strict SOF morphisms and the category
$\mathsf{SOF}_{\mathrm{str}}$. Paper XI adds a record-producing construction

$$
\mathrm{WallAssign}:(\mathcal F,\mathcal L,\Gamma)
\longmapsto
\mathcal W(\mathcal F,\mathcal L,\Gamma),
$$

read as: a realized SOF $\mathcal F$, together with a chosen observable ladder
$\mathcal L$ and deformation geometry or sampled path $\Gamma$, determines the
wall records observed by that ladder along that geometry.

This notation is intentionally modest. It is a bookkeeping assignment, not a
claim that wall records form a categorical morphism out of
$\mathsf{SOF}_{\mathrm{str}}$. The present paper does not prove invariance
under every weak SOF comparison. It only asserts that wall records are naturally
recorded after SOF realization, observable extraction, and deformation choice.

![Observable wall-record pipeline. A realized SOF, observable ladder,
deformation geometry, and change locus produce a wall record. Wall signatures,
wall spectra, and computable invariants then feed the Observable Wall Taxonomy.
ADE is only a candidate local model on sufficiently smooth discriminant
branches.](../../figures/paper11/fig1_wall_record_pipeline.png)

### Aggregate Wall Record

For a realized SOF deformation, the aggregate wall record is the collection of
observable change loci that have been registered:

$$
\mathcal W(\mathcal F,\mathcal L,\Gamma)
=
\{\text{rank jumps},\ \text{support jumps},\ \text{accessibility jumps},
\ \text{plateau intervals},\ \text{collision loci},\ldots\}.
$$

For a one-parameter deformation, the observable wall record is more usefully
viewed as an ordered sequence

$$
\mathcal W_{\mathrm{obs}}(\mathcal F_t)
=
(W_1,W_2,\ldots,W_k),
$$

where each $W_i$ is an observable wall signature event encountered along the
path. This sequence is analogous in spirit to a critical sequence in Morse
theory, a bifurcation diagram, a persistence barcode, or an RG-flow history,
but it is not identified with any of these objects. It is the SOF-native
record of observable changes along a chosen deformation.

The ellipsis is important: the registry is open. A new wall type may enter
only after its SOF object, observable ladder, deformation geometry, jump or
discriminant locus, and diagnostic package are explicit.

### What Is Not Being Classified

Paper XI does not classify native systems directly. Rubik, quantum gates,
Markov chains, graphs, neural networks, and Yang-like systems are not compared
through their native coordinates.

The classification target is the wall record after SOF realization.

***

## Wall Signatures

Wall records say where an observable changes. A **wall signature** records
what the wall looks like in computable terms.

The basic object is an observable signature event

$$
W_i
=
(\mathrm{rank\ type},\ \mathrm{support\ type},\ \mathrm{repair\ type},
\ \mathrm{oscillation\ type},\ \mathrm{plateau\ type}).
$$

For accessibility and trajectory diagnostics, the same information can be
recorded as an observable-difference vector

$$
W_i
=
(\Delta R_1,\Delta R_2,\Delta D,\Delta\tau,\Delta P_d).
$$

The first notation records qualitative type; the second records measured
observable change. Paper XI classifies these observable signatures, not bare
wall events.

A typical signature has the form

$$
\mathrm{Sig}_W(\mathcal F_t,O)
=
(c,\ k,\ p,\ m,\ r,\ b,\ldots),
$$

where:

1. $c$ records the number of detected components or cells;
2. $k$ records codimension when a meaningful ambient geometry is known;
3. $p$ records persistence: persistent, transient, terminal, or degenerate;
4. $m$ records temporal profile: monotone, oscillatory, plateau, flat, or
   discontinuous;
5. $r$ records repair status: repairable, unrepaired, terminal, or not
   applicable;
6. $b$ records boundary type: collision, rank/support jump, absorbing
   boundary, activation kink, stopping boundary, or filtration degeneration.

This is not yet a complete invariant. It is a computable signature schema for
comparing wall records without pretending that all walls belong to one smooth
classification theory.

### Wall Spectrum

The **wall spectrum** of a realized SOF deformation is the multiset of wall
signatures observed across the chosen observable ladder:

$$
\mathrm{Spec}_W(\mathcal F_t)
=
\{\!\{\mathrm{Sig}_W(\mathcal F_t,O_a):O_a\in\mathcal L(\mathcal F_t)\}\!\},
$$

where $\mathcal L(\mathcal F_t)$ denotes the observable ladder under audit.
Equivalently, one may write schematically

$$
\mathrm{Spec}_W(\mathcal F_t)
=
\{\!\{\text{rank wall},\ \text{accessibility wall},\ \text{plateau wall},
\ldots\}\!\}.
$$

The multiset notation allows repeated wall types. A species may exhibit two
distinct repair walls, or both a collision wall and a plateau wall, and these
should not be collapsed into a single label.

### Observable Wall Invariants

Observable signatures produce numerical invariants. These invariants are not
claimed to be complete; they are the first stable coordinates for comparing
wall spectra and for passing diagnostic summaries to later SOF reports.

| Invariant | Definition | Example audited value |
|-----------|------------|-----------------------|
| Crossing count $N_{\mathrm{cross}}$ | number of sampled wall crossings or adjacent observable-status changes along a declared deformation path | GridWorld obstacle path: 190 sampled pair-status changes |
| Wall-cell count $N_{\mathrm{cell}}$ | number of sampled cells or points on an evaluation grid satisfying a declared wall predicate | Rubik 2D slice: one $\Sigma_{\mathrm{comm}}$ hit on the chosen $20\times20$ evaluation grid |
| Repair index $R_W$ | $D_{\mathrm{repaired}}/\mathrm{frozen}_{R_1}$ when both are defined | Clifford+CNOT: $6/6=1.0$; Pauli: $0/8=0$ |
| Repair persistence $p_W$ | parameter-range length, measured relative to the normalized deformation parameter, for which a repaired channel remains accessible after activation | CNOT-strength interpolation: threshold $0.55$, $p_W=0.45$, stability $100\%$ |
| Oscillation index $O_W$ | number of sign changes or oscillatory reversals in a plateau diagnostic | Rubik generator-weight plateau: $3$; Yang-like state mixing: $0$ |
| Plateau index $P_W$ | number, length, or collapse profile of plateau intervals in $P_d(t)$ | Yang-like and training-coupled diagnostics supply initial plateau profiles |
| Depth index $\bar D$ | maximum recorded $D$ over sector pairs, with frozen entries marked separately | graph/Rubik-style frozen entries may use $999$ as a sentinel; transformer diagnostic has $\bar D=2$ |
| Rate ratio $\rho_W$ | slow observable time divided by fast observable time | NN GD+WD proxy: about $2\times$; ridge row/null diagnostic: about $68553\times$ |
| Spectral gap $\gamma_W$ | normalized second-gap or transition-gap diagnostic for a registered species | Clifford+CNOT registry example: about $0.73$; Pauli control: $0$ |
| Codimension $c_W$ | local or computational codimension when an ambient geometry is available | $\Sigma_{\mathrm{comm}}$: $11$; $A_1$: $1$; $A_2$: $2$ |
| Wall density $\delta_W$ | fraction of species in the Paper XI wall-density taxonomy sample exhibiting a given wall type | 15-entry sample shown below |

These quantities make the taxonomy operational. A later SOF diagnostic report
can emit a wall spectrum together with $N_{\mathrm{cross}}$, $N_{\mathrm{cell}}$, $R_W$, $P_W$, $O_W$, $\bar D$,
$\rho_W$, $\gamma_W$, $c_W$, $p_W$, and $\delta_W$ whenever the corresponding
observable layer is defined. For example, a transformer diagnostic need not
prove a wall theorem; it may report crossing count, wall-cell count, repair index, plateau or
oscillation index, and depth index as observable features of the model under
the chosen sectorization.

### Wall-Density Taxonomy Sample

In the 15-entry Paper XI wall-density taxonomy sample, wall density is computed as

$$
\delta_W(\mathrm{type})
=
\frac{\#\{\text{taxonomy-sample species carrying that wall type}\}}{15}.
$$

The table below is generated by the wall-density support artifact listed in
Appendix C.

The resulting initial density table is:

| Wall type | Density | Dominant source |
|-----------|---------|-----------------|
| B repair | $33.3\%$ | 5 species; the most common wall type |
| F bridge/incidence | $20.0\%$ | Rubik naturally carries bridge and incidence walls |
| C terminal-side | $13.3\%$ | barrier option and absorbing Markov examples |
| D plateau/rate | $13.3\%$ | Xu ridge and mechanism-separated dynamics |
| E nonsmooth/discrete | $13.3\%$ | graph rewiring and ReLU kink diagnostics |
| A spectral collision | $6.7\%$ | Rubik spectral collision branch; rarest in this sample |
| no registered wall type | $20.0\%$ | 3 of 15 entries are static or structural species |

![Wall-density and repair-persistence evidence. The left panel reports A--F
wall densities in the 15-entry Paper XI taxonomy sample, which is distinct
from the frozen 16-entry Paper X Registry release snapshot. The right panel
shows the CNOT-strength repair threshold at $0.55$, persistence
$p_W=0.45$, and $100\%$ post-activation stability on the tested grid.](../../figures/paper11/fig3_density_and_repair_persistence.png)

The snapshot is not a theorem and should not be read as a population estimate
for all possible SOFs. It is a taxonomy-sample statistic. Its immediate interpretation
is useful: repair walls are the most common in the taxonomy sample, echoing
the Paper VII focus on generic completion and repair; spectral collision walls
are the rarest, suggesting that Paper XI requires more continuous deformation
models before spectral-collision taxonomy can be considered representative.

### Wall-Record Coverage Census

Species prevalence alone does not measure whether each taxonomy class has
enough independent wall records. We therefore maintain a second computational
census whose unit is a wall record, not a species. A record may carry multiple class labels when one
deformation has several observable features, but repeated records do not create
new species in the prevalence denominator.

For this initial audit, a record is **eligible** when it has an explicit
deformation, an explicit change locus, a measured signature, and an existing
evidence file. The provisional coverage target for each class is at least
three eligible records, two distinct species, and two deformation origins.
This is a curation threshold, not a classification theorem criterion.

The census contains 24 records, 32 class memberships, and 15 eligible
records:

| Class | Registered records | Eligible records | Eligible species | Deformation origins | Coverage |
|-------|-------------------:|-----------------:|-----------------:|--------------------:|----------|
| A collision/spectral | 3 | 2 | 1 | 2 | gap |
| B repair | 9 | 5 | 5 | 5 | pass |
| C terminal-side/absorbing | 4 | 3 | 3 | 3 | pass |
| D plateau/rate | 4 | 4 | 4 | 4 | pass |
| E nonsmooth/discrete | 4 | 3 | 3 | 3 | pass |
| F bridge/incidence | 8 | 3 | 3 | 3 | pass |

The result isolates the remaining sampling problem: Class A has multiple
Rubik records and two deformation origins, but still only one eligible
species. Additional non-Rubik continuous spectral-collision models are needed.
The other five classes meet the provisional record/species/deformation target,
but this does not make the six-class taxonomy complete or statistically
representative. Full generated tables and record provenance are stored in
the repository artifacts listed in Appendix C.

### Definition-Compatible Redundancy Audit

The ten wall invariants listed above do not share one sampling unit.
Codimension requires an ambient geometric model, $\delta_W$ is a cross-species
statistic, and $O_W$, $P_W$, and $p_W$ require trajectories. They therefore
must not be inserted into one snapshot correlation matrix by replacing them
with unrelated proxies.

The definition-compatible redundancy audit instead computes eight snapshot
diagnostics on the same 166 controlled configurations:
direct-frozen fraction, Lie-terminal fraction, repair index, word-bridge
only fraction, Lie-bridge-only fraction, mean and maximum word depth, and log observable
norm ratio. The strongest empirical correlations are:

| Pair | Correlation $r$ |
|------|:---:|
| direct-frozen fraction / mean word depth | $+0.932$ |
| mean / maximum word depth | $+0.938$ |
| direct-frozen fraction / maximum word depth | $+0.923$ |
| direct-frozen / Lie-terminal fraction | $+0.886$ |
| Lie-terminal fraction / mean word depth | $+0.856$ |

The Lie-bridge-only fraction has zero variance on this ensemble and is removed
before standardization. PCA on the seven retained diagnostics gives three
components for both 90% and 95% of the observed variance.
The leading axis is a reachability/depth scale; later axes separate repair,
bridge-channel, and observable-rate effects. This is an empirical dimension
estimate for the tested ensemble, not a proof of a minimal, complete, or
orthogonal invariant basis. It is also ensemble-composition dependent: changing
the relative mix of GridWorld, SIR, random-graph, and random-skew configurations
can change the explained-variance percentages.

Trajectory diagnostics are reported separately. The present three trajectory
controls are insufficient for a trajectory-invariant PCA, so no independence
claim is made for oscillation, plateau, or persistence coordinates.

### Example Signatures

| Species / probe | Informal signature |
|-----------------|--------------------|
| Rubik spectral deformation | finite, collision-like, smooth-branch candidate, higher-order endpoint |
| Rubik $\Sigma_{\mathrm{comm}}$ slice | sparse, high-codimension, persistent commutativity anchor, not an accessibility map |
| Rubik accessibility repair | repairable, finite, incidence/support-driven |
| Absorbing Markov chain | terminal-side, absorbing, monotone/frozen, unrepaired |
| Yang-like state mixing | monotone degeneration or plateau degeneration, comparison branch |
| Transformer activation SOF | sparse repair, activation-induced, diagnostic token-sector influence |
| Barrier-option SOF | stochastic stopping boundary, cross-barrier support, hitting-time diagnostic |

***

## Observable Wall Taxonomy

Paper XI organizes signatures into a taxonomy before attempting any local
smooth model.

### Taxonomy Classes

| Class | Name | Diagnostic pattern | Typical examples |
|-------|------|--------------------|------------------|
| A | Collision walls | spectral or discriminant branches collide or merge | Rubik spectral deformation, smooth spectral probes, NCG spectral-block diagnostics |
| B | Repair walls | an inaccessible or frozen channel becomes accessible at a higher observable layer | Rubik repair, quantum $D$-repair, transformer sparse repair |
| C | Terminal-side walls | trajectories enter a temporarily terminal, dead, or absorbing side of a deformation; record whether repair occurs | absorbing Markov chains, pre-repair quantum or MoE diagnostics, barrier boundaries |
| D | Plateau walls | observables remain flat, delayed, oscillatory, or degenerate over intervals | Yang-like degeneration, training plateaus, grokking-style delayed rates |
| E | Nonsmooth or discrete walls | wall is induced by a discrete jump, rank selection, or piecewise-smooth kink | graph rewiring, ReLU kinks, Top-k activation selection |
| F | Bridge or incidence walls | bridge products, rank incidence, or algebraic association controls wall behavior | Rubik Type III/IV mechanisms, incidence products, bridge-level audits |

![Observable Wall Taxonomy. The six registered signature classes are
collision, repair, terminal-side, plateau, nonsmooth/discrete, and bridge/incidence
walls. The classes precede smooth, stratified, or algebraic local-model
choices and do not classify native systems directly.](../../figures/paper11/fig2_observable_wall_taxonomy.png)

### Observable Normal Forms

Before invoking smooth singularity theory, wall signatures can be grouped into
SOF-native observable normal forms. These are descriptive normal forms for
observable signatures, not theorem-level ADE classes.

| Normal form | Signature pattern | Typical diagnostic |
|-------------|-------------------|--------------------|
| NF-1: single rank collision | one spectral/rank component collides or merges | one $A_1$-like gap closure or one rank jump |
| NF-2: bridge creation | a previously frozen pair becomes accessible at $R_2$ or $D$ | positive $D_{\mathrm{repaired}}$ or bridge support |
| NF-3: oscillatory repair | repair or plateau observable alternates before stabilizing | nonzero oscillation index $O_W$ |
| NF-4: plateau collapse | plateau interval degenerates, flattens, or terminates | monotone degeneration or endpoint collapse |
| NF-5: terminal absorption | a state, sector, or channel enters an absorbing/frozen terminal regime | frozen pairs with no repair |
| NF-6: bridge/incidence association | a bridge product, image-kernel relation, or algebraic incidence controls the wall | Rubik Type III/IV and rank-protected bridge audits |

Observable wall records are first sorted by five axes.

### Smoothness Type

| Type | Description | Classification status |
|------|-------------|-----------------------|
| Smooth discriminant | $O(t)$ is smooth and $\Sigma_O$ is a discriminant pullback | ADE may apply locally |
| Piecewise-smooth wall | $O(t)$ is continuous but not smooth across strata | needs stratified or piecewise theory |
| Discontinuous jump | $O(t)$ changes by a discrete event or rank jump | outside classical ADE |
| Degenerate/nonresponsive | trajectory is flat, decreasing, zero, or not a response curve | not a wall class by itself |
| Incidence mechanism | wall is defined by algebraic product/rank incidence | algebraic-geometry classification needed |

### Observable Layer

| Layer | Typical observable | Typical wall type |
|-------|--------------------|-------------------|
| Spectral | eigenvalues, collision quotients | spectral collision/discriminant |
| Accessibility | $R_1/R_2/D$, $\mathcal J_{\mathrm{acc}}$ | rank/support/accessibility discriminant |
| Filtration | plateau functions $P_d(t)$ | degeneration or plateau transition |
| Markov | communicating-class or transition support | absorbing/frozen boundary |
| Graph | Laplacian gap, adjacency transport | discrete rewiring or spectral sensitivity |
| Quantum | gate-log accessibility, controllability | channel/accessibility transition |
| Neural-network | activation sectors, $K_0/K_1/K_2$ | training-coupled or activation-induced wall |

### Deformation Geometry

The same observable ladder can produce different wall behavior depending on
what changes:

generator weights, state mixing, gate interpolation, edge rewiring, training
dynamics, or rate-matrix perturbation.

Therefore wall classification must be attached to a deformation geometry, not
only to the SOF object.

***

## Smooth Wall Models

Smooth wall models are the final layer, not the starting point. Arnold ADE
classification is a plausible local model only for sufficiently smooth
discriminant branches. A typical admissible situation would have:

$$
O:T\to E,\qquad
\Sigma_O=O^{-1}(\Delta),
$$

with $O$ smooth and $\Delta$ a stable local singularity.

In this restricted setting, the local wall may fall into an $A_k$, $D_k$, or
$E_{6,7,8}$ class.

This paper does not assert such a classification globally. In particular:

1. graph rewiring is discrete;
2. Top-k and step activations are discontinuous;
3. ReLU-type walls are piecewise-smooth;
4. accessibility incidence can be algebraic rather than ADE-like;
5. flat or decreasing trajectories are not rate-response walls.

ADE is therefore a local smooth-branch model, not the SOF classification
framework.

The branch-aware $A_n$ adjacency falsification audit is recorded in Appendix A.
Its role in the main text is only to prevent a false promotion of sorted-index
pair-gap responses into an ADE adjacency claim.

***

## Cross-Species Audit

The computational audit combines cross-species wall diagnostics, smooth
spectral pair-gap responses, record coverage, snapshot redundancy,
branch-aware adjacency falsification, sampled trajectory events, and two
registry-handoff diagnostics. The artifact map is collected in Appendix C.
The discriminant-bifurcation scan is an auxiliary 2D-slice diagnostic; it is
not a full map of $\Sigma_{\mathrm{access}}$.

### Rubik Spectral Snapshot

The Rubik $A_{18}$ audit reports six spectral layers with eigenvalues

$$
1,\ 8/9,\ 7/9,\ 2/3,\ 5/9,\ 1/3,
$$

and $k$-set $\{0,1,2,3,4,6\}$. This is a fixed spectral snapshot. It is not,
by itself, a moving wall.

### Rubik Spectral Pair-Gap Local-Model Audit

The spectral-deformation audit varies one QT generator weight and tracks the
eigenvalues of a fixed separating Hermitian probe

$$
M(\alpha)=QT(\alpha)+\beta HT(\alpha),\qquad \beta=0.314159.
$$

The audit detects 16 pairwise adjacent-gap closures at the canonical endpoint.
Each closure is recorded as an $A_1$/fold candidate in the smooth spectral
branch. The endpoint itself is higher order: the regular QT/HT sector point is
a simultaneous multi-branch collapse rather than a single isolated fold.

The same audit also runs a two-weight diagonal search and records simultaneous
pair-gap responses. The observed count ranges from one to three across tested
sampling resolutions, so the integer is not promoted to a stable invariant. The
two gaps need not share an eigenvalue branch, and the audit does not perform
eigenbranch continuation. These observations therefore remain pair-gap response
diagnostics; they are not identified as $A_2$/cusp unfoldings and do not prove
an ADE classification theorem for SOF walls.

### Rubik 2D $\Sigma_{\mathrm{comm}}$ Slice

The discriminant-bifurcation audit scans a two-dimensional plane of QT
generator weights and tests the Frobenius norm of

$$
[QT(w),HT(w)].
$$

On the $20\times20$ slice varying two QT generator weights, the audit reports
one hit on the chosen $20\times20$ evaluation grid. The single commutative cell
has 9 spectral points, and the audit records no spectral point-count
bifurcations inside the commutative cells. This is not a proof of the
codimension-$11$ commutativity theorem from Paper VI and not a map of
$\Sigma_{\mathrm{access}}$. Its role in Paper XI is narrower: it gives a
sampling anchor showing that arbitrary two-dimensional generator-weight slices
meet the high-codimension commutativity locus sparsely. Spectral and
accessibility wall taxonomy should therefore be computed on normal spectral
charts or on deformation models chosen for that purpose, not inferred from a
generic 2D scan alone.

### Quantum Accessibility Contrast

The quantum audit compares Pauli, Clifford+CNOT, and Universal+CNOT
gate-sector SOFs. Clifford+CNOT and Universal+CNOT show $D$-repair, while the
Pauli control does not. This is an accessibility contrast outside Rubik, not
a claim that quantum systems obey Rubik wall theory.

A separate repair-persistence audit interpolates CNOT strength in matrix space
from a product endpoint to the Clifford+CNOT gate-log SOF. On the 21-point
grid $0,0.05,\ldots,1$, $D_{\mathrm{repaired}}$ is zero through strength
$0.50$ and jumps to $6$ at strength $0.55$. The repair then persists through
strength $1.00$ with no reversal. Thus the initial repair-persistence
signature is threshold $0.55$, $p_W=0.45$ over the unit interpolation range,
and post-activation stability $100\%$. In grid-count terms this corresponds
to $10$ active samples out of $21$; $p_W$ records the continuous parameter
range, not the sample fraction.

### Markov Frozen-Pair Contrast

The Markov audit separates complete/strongly connected examples from an
absorbing-state example. The absorbing case has true frozen pairs. This is a
communicating-class or absorbing-boundary diagnostic, not an ADE
classification.

### Graph Spectral-Gap Sensitivity

The graph audit records Laplacian-gap changes under edge removal. This is a
discrete perturbation diagnostic. It is not a smooth codimension-one wall
without a separate continuous edge-weight model and discriminant calculation.

### Piecewise-Smooth Activation Wall Boundary

The activation-wall audit compares ReLU, GeLU, and Top-k sector diagnostics.
In the default finite test, the ReLU sector diagnostic has distinct left and
right slopes, producing a piecewise-smooth kink.  GeLU is smooth in the same
test and does not define a kink wall.  Top-k is a rank-selection diagnostic
and is treated as a discontinuous or discrete wall record.

This audit supports the negative boundary for ADE usage: activation-induced
SOF walls may require piecewise-smooth, stratified, or discrete wall theory
rather than classical smooth ADE singularity theory.

### Barrier-Option Stopping Boundary

The barrier-option SOF uses a finite log-price grid with below-barrier and
above-barrier sectors. The default audit reports cross-barrier generator
support with $R_1=75.0\%$, $R_2=0.0\%$, no $D$-repair, and mean first-hit time
$6.5915$ from the chosen initial grid point to the barrier sector. This is a
stochastic stopping-region wall record. The first-hitting time is a native
stochastic diagnostic, not the SOF depth $D$, and the entry is not an
option-pricing theorem.

### Transformer Activation-Sector Diagnostic

The transformer diagnostic constructs a token-space SOF from activation-count
clusters in a tiny transformer-like block. Attention top-k and FFN
activation-similarity operators give $R_1=58.3\%$, $R_2=66.7\%$,
$D_{\mathrm{repaired}}=2$, and $D_{\max}=2$ in the default audit. This is an
activation-induced diagnostic wall record: it shows how token-sector
decompositions can expose cross-sector influence, but it is not a theorem
about all transformers or LLM explainability.

***

## Boundary Audit Notes

Two boundary audits are deferred to the appendices. Appendix A records the
branch-aware adjacency falsification audit for Rubik spectral pair responses.
Appendix B records the observable-status trajectory audit. Their shared
main-text role is cautionary: sorted gaps should not be promoted to ADE
adjacency without branch continuation, and static inaccessible pairs should not
be relabeled as walls without a change along a declared deformation path.

***

## Working Taxonomy Table

The table below is a first finite approximation to
$\mathrm{Spec}_W$ across the registered examples. Each row records one wall
signature or wall-spectrum entry; a single species may contribute more than
one row in future registry versions.

| Species / probe | Class | Wall signature | Smooth-model status | Claim status |
|-----------------|-------|----------------|---------------------|--------------|
| Rubik spectral snapshot | A pre-wall reference | fixed finite spectral arrangement | not a moving wall by itself | exact snapshot |
| Rubik spectral deformation | A collision wall | higher-order endpoint; 16 $A_1$-type pairwise closures and simultaneous pair-gap responses | branch-aware audit finds no $A_2\to A_1+A_1$ split candidate | smooth-branch diagnostic, not full classification |
| Rubik $\Sigma_{\mathrm{comm}}$ 2D slice | A/B boundary anchor | sparse high-codimension intersection; one hit on the chosen $20\times20$ evaluation grid | sampling anchor; codimension-$11$ belongs to the Paper VI tangent theorem | boundary diagnostic, not a full discriminant map |
| Accessibility $R_1/R_2/D$ | B repair wall | rank/support/accessibility jump; repairable or unrepaired depending on species | possible smooth branch on $\Sigma_{\mathrm{spec}}$ | conditional |
| Rubik Type III/IV bridge mechanisms | F bridge/incidence wall | bridge products, cancellation, and rank-incidence structure; naturally carried by Rubik | algebraic/incidence normal form, not ADE by default | Paper V--VII and Paper X registry evidence |
| Quantum accessibility | B repair wall | accessibility-channel contrast; $D$-repair appears for entangling gate sets | not classified | diagnostic evidence |
| Markov absorbing boundary | C terminal-side wall | absorbing, frozen, terminal-side, unrepaired | not ADE by default | diagnostic evidence |
| Graph edge rewiring | E discrete wall | discrete spectral-gap sensitivity under edge removal | outside smooth ADE | diagnostic evidence |
| Barrier-option stopping sector | C/D stochastic boundary | cross-barrier support with first-hitting diagnostic; hitting time is not SOF depth | not ADE by default | registry diagnostic evidence |
| NN training dynamics | D plateau/rate wall | delayed or ordered proxy response; rate hierarchy is not a wall class by itself | smooth only with explicit training model | Paper IX/X evidence |
| ReLU / Top-k activations | E nonsmooth wall | piecewise kink or rank-selection jump | requires nonsmooth or stratified extension | boundary diagnostic evidence |
| Transformer activation sectors | B/E activation repair wall | sparse token-sector repair; $D_{\mathrm{repaired}}=2$ in default audit | activation-induced; requires diagnostic/stratified theory | diagnostic handoff evidence |
| Yang-like state mixing | D plateau wall | monotone degeneration or plateau degeneration | smooth candidate only with explicit model | comparison branch |

***

## What This Paper Does Not Claim

Paper XI does not claim:

1. a complete classification of all SOF trajectories;
2. that Arnold ADE applies to all SOF branches;
3. that graph rewiring is a smooth codimension-one wall;
4. that activation-induced walls fit into ADE without extension;
5. that the mechanism-separation principle of Paper X is a
   universal theorem;
6. that rate hierarchy alone determines wall class;
7. that Paper XI supplies general transformation laws for observables across
   walls;
8. that the wall assignment is full, faithful, or invariant under all weak SOF
   comparisons;
9. that the listed observable invariants form a complete invariant system;
10. that observable normal forms are already classification theorems;
11. that the tested Rubik spectral slices exhibit $A_n$ adjacency.

The stable claim is narrower:

SOF wall behavior is first organized by observable wall records, wall
signatures, wall spectra, and computable observable invariants. The Observable
Wall Taxonomy groups those signatures into collision, repair, terminal-side,
plateau, nonsmooth/discrete, and bridge/incidence classes. Observable normal
forms organize the registered signatures before any smooth singularity model
is invoked. ADE-type local modeling is one candidate subtheory for
sufficiently smooth wall records, not the whole theory. In this sense, Paper
XI is the observable feature extractor between the Paper X Registry and later
SOF diagnostic workflows.

***

## Conclusion

Paper XI turns SOF wall phenomena into a record-level classification problem.
Its basic output is not a universal wall-crossing law, but a sequence of
observable records, signatures, wall spectra, and diagnostic invariants that can
be compared across registered SOF species. Smooth ADE-style normal forms remain
candidate local models only on sufficiently smooth discriminant branches; the
taxonomy itself also admits repair, terminal-side, plateau/rate,
nonsmooth/discrete, and bridge/incidence records. This paper classifies
observable wall records rather than wall evolution laws.

***

## Outlook

Paper XI supplies a record-level taxonomy, not a classification theorem. The
next stage is to decide which parts of the taxonomy are invariant under
comparison of SOF presentations, which parts depend on the chosen ladder or
sampling path, and which parts admit local geometric normal forms.

The remaining classification program has five parts:

1. formalize comparison and equivariance conditions for
   $\mathrm{WallAssign}(\mathcal F,\mathcal L,\Gamma)$: defining compatible
   comparison data is straightforward, but proving invariance under weak SOF
   comparisons, path reparametrizations, and sampling refinements is a separate
   theorem-level problem;
2. build continuous graph and Markov deformation models where smooth
   discriminants can be computed;
3. compute local codimensions for accessibility discriminants and higher-order
   spectral endpoints;
4. separate incidence varieties from smooth singularity classes;
5. develop or import piecewise-smooth and stratified wall theory for
   activation-induced and rank-selection SOFs.

Only after these ingredients and additional registered examples are available
can the taxonomy be promoted toward classification theorems.

***

## Appendix A: Branch-Aware Adjacency Falsification Audit

Simultaneous small gaps in a sorted full-spectrum list are not enough to
establish $A_n$ adjacency. Such gaps may belong to different invariant blocks,
may exchange order, or may be symmetry-protected degeneracies rather than
isolated collision branches.

The branch-aware audit therefore separates the Rubik representation into its
$cp$, $ep$, $co$, and $eo$ blocks and continues
eigenbranches by maximizing eigenvector overlap between adjacent parameter
samples. A candidate $A_2\to A_1+A_1$ split requires two isolated pair-gap
minima at separated parameter values whose union involves all three branches.
Persistent degeneracies, endpoint-only closures, and cross-block equalities are
rejected.

| Block | Dimension | Endpoint cluster sizes | Tested triples | Split candidates |
|-------|----------:|------------------------|---------------:|-----------------:|
| $cp$ | 64 | $8,24,24,8$ | 0 | 0 |
| $ep$ | 144 | $12,36,24,36,36$ | 0 | 0 |
| $co$ | 8 | $3,3$ | 2 | 0 |
| $eo$ | 12 | $3,3,3$ | 0 | 0 |

On the tested diagonal and asymmetric slices, no branch-aware
$A_2\to A_1+A_1$ split candidate is detected. The earlier sorted-index
pair-gap responses remain useful spectral diagnostics, but they do not support
an $A_n$ adjacency claim. Even a future positive candidate would still require
local normal-form and versality analysis before becoming an ADE statement.

***

## Appendix B: Observable-Status Wall Trajectories

Given audit snapshots at parameters $t_0,\ldots,t_K$, assign each ordered pair
one observable status:

$$
S_{ij}(t)
\in
\{\mathrm{direct},\mathrm{word\ bridge},\mathrm{Lie\ bridge},
\mathrm{deeper},\mathrm{terminal}\}.
$$

A sampled wall event occurs only when

$$
S_{ij}(t_{k-1})\neq S_{ij}(t_k).
$$

The trajectory implementation records every adjacent-step change, including
repeated changes of the same pair. Events are labeled as
repair, terminalization, support gain, support loss, or layer change. Stable
terminal pairs remain trajectory metadata and are not counted as walls.

Three controlled paths are implemented:

| Control | Steps | Ordered pairs | Events | Changed pairs | Event steps |
|---------|------:|--------------:|-------:|--------------:|-------------|
| GridWorld obstacle path | 3 | 600 | 190 | 140 | 1, 2 |
| SIR $\beta$ sweep | 21 | 6 | 4 | 4 | 1 |
| Graph edge-weight endpoint | 11 | 12 | 6 | 6 | 10 |

The SIR result isolates all changes at the first sampled step
$\beta=0\to0.025$. The graph control is constant for $t<1$ and changes only
when the weakened edges vanish at $t=1$. GridWorld records two discrete
topology replacements and therefore has events at both steps.

These are sampled-path wall records. They do not establish ambient codimension,
continuous-time wall flow, or a bifurcation theorem. Their role is narrower:
they provide a correct dynamic record layer between Paper IX deformations and
the Paper XI taxonomy without relabeling every frozen pair as a wall.

***

## Appendix C: Computational Artifacts

The following repository artifacts provide the reproducible support layer for
the audits reported in this paper. The main text refers to audit roles rather
than file paths; this appendix records the exact implementation and generated
tables. Unless a prefix is shown, files are located under
`experiments/paper11/`.

| Artifact | Role in Paper XI | File |
|----------|------------------|------|
| C1 | cross-species wall diagnostics | `cross_species_wall_audit.py` |
| C2 | smooth spectral pair-gap local-model audit | `spectral_ade_collision.py` |
| C3 | auxiliary 2D commutativity-discriminant slice | `discriminant_bifurcation_map.py` |
| C4 | wall-density taxonomy sample | `wall_density_registry.py` |
| C5 | wall-record coverage census | `wall_record_census.py` |
| C6 | generated wall-record census tables | `results/wall_record_census.md`, `.json` |
| C7 | definition-compatible redundancy audit | `invariant_redundancy.py` |
| C8 | branch-aware adjacency falsification | `an_adjacency.py` |
| C9 | observable-status trajectory records | `wall_trajectory.py` |
| C10 | CNOT-strength repair persistence | `repair_persistence_quantum.py` |
| C11 | piecewise-smooth activation boundary | `piecewise_smooth_activation_wall.py` |
| C12 | barrier-option registry handoff | `paper10/barrier_option_sof.py` |
| C13 | transformer activation-sector handoff | `paper12/transformer_activation_sof.py` |

***

## References

**Program lineage.** Paper XI depends on Papers VII--X. Paper VII supplies the
generic completion and repair boundary \cite{paper7}; Paper VIII supplies the
SOF object layer \cite{paper8}; Paper IX supplies observable trajectories and
wall pullbacks \cite{paper9}; Paper X supplies the Universal Observable
Pipeline and five-layer SOF Registry \cite{paper10}.

**Smooth singularities.** Arnold's catastrophe and ADE singularity theory is
relevant only to the smooth-discriminant branch. Useful background includes
Arnold's *Catastrophe Theory*, the work of Arnold, Gusein-Zade, and Varchenko
in *Singularities of Differentiable Maps*, and Golubitsky and Guillemin's
*Stable Mappings and Their Singularities*.

**Stratified and nonsmooth walls.** Piecewise smooth, discontinuous, and
multi-stratum SOF walls require different tools. Relevant background includes
Whitney and Thom--Mather stratification, Goresky and MacPherson's *Stratified
Morse Theory*, the work on piecewise smooth dynamical systems by di Bernardo,
Budd, Champneys, and Kowalczyk, and Filippov's discontinuous differential
equations.

**Spectral and finite-state diagnostics.** Graph and Markov wall records
are compared against spectral perturbation theory, spectral graph theory, and
Markov chain perturbation and mixing theory before any singularity classification
is claimed.
