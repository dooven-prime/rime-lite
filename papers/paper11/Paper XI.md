# Observable Classification Theory for Sectorized Observable Frameworks

### Wall Records, Wall Coordinates, Taxonomy, and Smooth Local Models

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
diagnostics organize the behavior of registered SOFs.

**Approach.** We introduce a five-layer organization. First, a
**per-observable wall record** preserves the observation history of a chosen
observable along a declared deformation: its change locus, discriminant data,
diagnostics, and ordered atomic events $W_{a,1},\ldots,W_{a,k_a}$. The
**aggregate wall record** collects these histories across the declared ladder.
Second, feature extraction derives a **wall signature** from each atomic event:
rank type, support type, repair type, oscillation type, plateau type, or
equivalently changes such as
$(\Delta R_1,\Delta R_2,\Delta D,\Delta\tau,\Delta P_d)$. The multiset of all
atomic-event signatures is the **wall spectrum**
$\mathrm{Spec}_W(\mathcal F,\mathcal L,\Gamma)$. Third, a
**wall-coordinate profile** records
position, observable orientation, regularity, and stochastic status. Fourth,
the **Observable Wall Taxonomy** groups wall spectra into collision, repair,
terminal-structure, plateau/rate, nonsmooth/discrete, and bridge/incidence wall
families. Smooth ADE models enter only afterward as the fifth layer: candidate
local normal forms for sufficiently smooth discriminant branches.

**Results.** The main result is a proto-geometric wall-record schema, not a
complete classification theorem. It separates mechanism labels from geometric
coordinates and turns wall records into computable features such as crossing
count, atomic-event count, wall-cell count, repair index, oscillation index, depth index, rate
ratio, spectral gap, and codimension. Four extended profiles expose four
different geometries: a constructed real-symmetric endpoint gives two isolated
order-one $A_1$-type pair-gap closures; nested Erdos--Renyi percolation gives a
monotone opening window near $p=0.08$--$0.10$; matched Kuramoto ensembles give
a freezing crossover near $K=1.6$--$1.8$; and continuous weakening of one GRN
repression edge gives a two-to-one terminal-basin loss in the controlled
bracket $[0.520,0.525]$. A matched fixed-time CLE/SSA control withdraws the
earlier GRN noise-wall interpretation. The extended census retains the
original 24 records, adds these four records, and contains 28 records, 38
class memberships, and 19 first-pass eligible records. All six classes meet
the predeclared three-record, two-species, two-deformation finite-sample target.
Class A closes that target through a constructed non-Rubik witness; naturally
occurring non-Rubik Class A breadth remains open.

**Implications.** Paper XI develops the zeroth geometric layer of SOF wall
theory. The wall-record language is source-independent, while realized wall
geometry is source-dependent. The resulting wall-coordinate space has
position, orientation, regularity, and stochasticity, but it does not yet have
a metric, curvature, coordinate-change law, or transport structure. ADE-type
local models may be useful for spectral collision or smooth discriminant maps,
but they cannot be the default language for all SOF walls.

**Revision note.** Relative to the initial release, this version adds four
controlled wall profiles, extends the original 24-record census to an
independently generated 28-record census, and withdraws the earlier
low-$\Omega$ GRN noise-wall interpretation after a matched CLE/SSA control. The
A--F taxonomy is retained, while the distinction between observation histories
and derived wall signatures is made explicit.

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
| $\mathcal W_a(\mathcal F,\mathcal L,\Gamma)$ | per-observable wall record for $O_a\in\mathcal L$ |
| $W_{a,j}$ | the $j$th atomic wall event in the record of $O_a$ |
| $\mathcal W(\mathcal F,\mathcal L,\Gamma)$ | aggregate wall record $(\mathcal W_a)_{O_a\in\mathcal L}$ |
| $\operatorname{Feat}_W$ | feature-extraction map from wall records or atomic events to derived wall features |
| $\mathrm{Sig}_W(W_{a,j})$ | computable signature of an atomic wall event |
| $\mathrm{Spec}_W(\mathcal F,\mathcal L,\Gamma)$ | multiset of atomic-event wall signatures |
| $\mathrm{Prof}_W(\mathcal W)$ | wall profile: class together with position, orientation, regularity, and stochasticity |
| $\mathrm{Pos},\mathrm{Ori},\mathrm{Reg},\mathrm{Sto}$ | wall-coordinate components |
| $\mathrm{Term}(\mathcal F_t)$ | terminal decomposition induced by the declared dynamics and observable realization |
| $\mathrm{WallAssign}$ | record-producing assignment (bookkeeping): $(\mathcal F,\mathcal L,\Gamma)\mapsto \mathcal W$ |
| $N_{\mathrm{cross}},N_{\mathrm{evt}},N_{\mathrm{cell}}$ | crossing-step count, atomic-event count, and wall-cell count |
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

Paper XI asks whether registered wall records can be grouped into classes and
compared geometrically. The answer is not yet a complete classification. The
safe claim is that the classification problem splits into observable
signatures, wall spectra, wall coordinates, mechanism classes, normal forms,
and smooth local models.

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

The answer has five layers:

| Layer | Object | Question |
|-------|--------|----------|
| Wall Records | loci and observable changes | Where do walls occur? |
| Wall Signatures | computable diagnostics of events and records | What does the wall look like? |
| Wall Coordinates | position, orientation, regularity, stochasticity | How is the wall realized? |
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
\to \text{Observable ladder}\\
&\to \text{Observable dynamics}
\to \text{Wall records}\\
&\to \text{Feature extraction}
\to \text{Wall signatures and diagnostics}\\
&\to \text{Wall coordinates}
\to \text{Wall taxonomy}.
\end{aligned}
$$

The program invariant of this paper is therefore:

> **Wall-record language is source-independent; realized wall geometry is
> source-dependent.**

The coordinate language does not assert that wall records already form a
manifold or phase space. It supplies a comparison chart before any metric,
curvature, or transport law has been defined.

Paper XI does not prove that this last passage is a categorical invariant of
SOFs. It introduces the record-producing layer needed to make the passage
explicit once the observable ladder and deformation geometry have been chosen.

***

## Boundary Notes

Paper XI is organized by constructive definitions, record audits, and explicit
non-claims rather than by a single classification theorem. Its scope is
deliberately record-level. In particular, it does not claim:

1. a classification of the underlying dynamical systems, phase transitions,
   singularities, or bifurcations that produce the records;
2. a universal wall-crossing or wall-transition law;
3. that the qualitative wall-coordinate space already carries a metric,
   topology, curvature, or coordinate-change structure;
4. that Arnold ADE models apply outside sufficiently smooth
   discriminant-like branches;
5. that $\mathrm{WallAssign}$ is invariant under all weak SOF comparisons,
   path reparametrizations, thresholds, or sampling refinements.

These boundaries are repeated locally where a construction or computational
profile requires a narrower claim. The repeated boundary statements are part
of the taxonomy: they record which conclusions each wall signature licenses
and which native interpretations remain external to SOF.

***

## Wall Records

### Definition

For a declared ladder observable $O_a\in\mathcal L$, its
**per-observable wall record** is the data

$$
\mathcal W_a(\mathcal F,\mathcal L,\Gamma)
=
(\mathcal F_t,\ O_a(t),\ \Sigma_{O_a},\ \Delta_{O_a},\ \mathcal D_{O_a}),
$$

where:

1. $\mathcal F_t$ is a specified SOF deformation;
2. $O_a(t)$ is an observable shadow or continuous observable field;
3. $\Sigma_{O_a}$ is the locus where the observable changes qualitative type;
4. $\Delta_{O_a}$ is the target discriminant when a pullback description exists;
5. $\mathcal D_{O_a}$ is the raw measured diagnostic history, such as
   $\tau(O_a)$, repair, plateau, frozen-pair count, or spectral-gap change.

A wall record is an **observation history** relative to the declared SOF
realization, observable ladder, deformation path, and audit convention. It
retains what was observed, where it changed, and in what path order. It is not
itself a wall signature: signatures arise only after a feature-extraction rule
has been chosen.

If the chosen path order on $\Gamma$ meets $k_a$ registered event components,
the associated event sequence is

$$
\operatorname{Evt}(\mathcal W_a;\Gamma)
=
(W_{a,1},W_{a,2},\ldots,W_{a,k_a}).
$$

The $W_{a,j}$ are atomic wall events. Paper XI classifies their signatures and
the aggregate records built from them; it does not identify the event, the
per-observable record, and the aggregate record as the same object.

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
aggregate family of per-observable wall records along that geometry.

This notation is intentionally modest. It is a bookkeeping assignment, not a
claim that wall records form a categorical morphism out of
$\mathsf{SOF}_{\mathrm{str}}$. The present paper does not prove invariance
under every weak SOF comparison. It only asserts that wall records are naturally
recorded after SOF realization, observable extraction, and deformation choice.

![Observable wall-record pipeline. A realized SOF, observable ladder,
deformation geometry, and change loci produce indexed per-observable histories
and their aggregate wall record. Feature extraction derives atomic signatures,
wall spectra, wall coordinates, and diagnostics; these derived taxonomy
features, rather than the observation history itself, feed the Observable Wall
Taxonomy. ADE is only a candidate local model on sufficiently smooth
discriminant branches.](../../figures/paper11/fig1_wall_record_pipeline.png)

### Aggregate Wall Record

For a realized SOF deformation, the aggregate wall record is the indexed family

$$
\mathcal W(\mathcal F,\mathcal L,\Gamma)
=
\bigl(\mathcal W_a(\mathcal F,\mathcal L,\Gamma)\bigr)_{O_a\in\mathcal L}.
$$

Schematically, its registered change loci may include

$$
\begin{aligned}
\{\Sigma_{O_a}:O_a\in\mathcal L\}
={}&\{\text{rank jumps},\ \text{support jumps},\ \text{accessibility jumps},\\
&\phantom{\{}\text{plateau intervals},\ \text{collision loci},\ldots\}.
\end{aligned}
$$

For a one-parameter deformation, each per-observable record carries the ordered
atomic-event sequence

$$
\operatorname{Evt}(\mathcal W_a;\Gamma)
=
(W_{a,1},W_{a,2},\ldots,W_{a,k_a}),
$$

where each $W_{a,j}$ is an atomic observable event encountered along the path.
This sequence is analogous in spirit to a critical sequence in Morse
theory, a bifurcation diagram, a persistence barcode, or an RG-flow history,
but it is not identified with any of these objects. It is the SOF-native
record of observable changes along a chosen deformation.

The ellipsis is important: the registry is open. A new wall type may enter
only after its SOF object, observable ladder, deformation geometry, jump or
discriminant locus, and diagnostic package are explicit.

***

## Wall Signatures

Wall records preserve what was observed along a deformation. A **wall
signature** is a feature extraction from that history: it records what an
atomic wall event looks like in computable terms. Schematically,

$$
\mathcal W
\xrightarrow{\ \operatorname{Feat}_W\ }
\bigl(\mathrm{Sig}_W,\mathrm{Spec}_W,\mathrm{Prof}_W,\mathcal D_W\bigr).
$$

Wall signatures are therefore derived from wall records and are not primitive
SOF objects. Different admissible feature maps may extract different signatures
from the same observation history, so the extraction convention belongs to the
declared audit semantics.

The basic object is the signature of an atomic observable event

$$
\mathrm{Sig}_W(W_{a,j})
=
(\mathrm{rank\ type},\ \mathrm{support\ type},\ \mathrm{repair\ type},
\ \mathrm{oscillation\ type},\ \mathrm{plateau\ type}).
$$

For accessibility and trajectory diagnostics, the same information can be
recorded as an observable-difference vector

$$
\mathrm{Sig}_W(W_{a,j})
=
(\Delta R_1,\Delta R_2,\Delta D,\Delta\tau,\Delta P_d).
$$

The first notation records qualitative type; the second records measured
observable change. Paper XI classifies these observable signatures, not bare
wall events.

A typical signature has the form

$$
\mathrm{Sig}_W(W_{a,j})
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

This is not a complete invariant. It is a computable signature schema for
comparing wall records without pretending that all walls belong to one smooth
classification theory.

### Wall Spectrum

The **wall spectrum** of a realized SOF deformation is the multiset of all
atomic-event signatures observed across the chosen observable ladder:

$$
\mathrm{Spec}_W(\mathcal F,\mathcal L,\Gamma)
=
\{\!\{\mathrm{Sig}_W(W_{a,j}):O_a\in\mathcal L,\ 1\le j\le k_a\}\!\},
$$

where $k_a$ is the number of registered events in the record of $O_a$.
Equivalently, one may write schematically

$$
\mathrm{Spec}_W(\mathcal F,\mathcal L,\Gamma)
=
\{\!\{\text{rank wall},\ \text{accessibility wall},\ \text{plateau wall},
\ldots\}\!\}.
$$

The multiset notation allows repeated wall types. A species may exhibit two
distinct repair walls, or both a collision wall and a plateau wall, and these
should not be collapsed into a single label.

### Observable Wall Diagnostics

Feature extraction also summarizes the measured history into numerical wall
diagnostics. Their values are relative
to the declared realization, ladder, deformation path, threshold, depth cutoff,
and sampling protocol. Paper XI does not prove invariance under changes of those
choices. Within a fixed audit convention, they provide reproducible coordinates
for comparing wall spectra and for passing summaries to later SOF reports.

| Diagnostic | Definition | Example audited value |
|-----------|------------|-----------------------|
| Crossing count $N_{\mathrm{cross}}$ | number of sampled parameter transitions containing at least one atomic wall event | GridWorld obstacle path: $2$ crossing steps; SIR and graph controls: $1$ each |
| Atomic-event count $N_{\mathrm{evt}}$ | total number of atomic observable-status changes, including simultaneous changes and repeated changes of one pair | GridWorld obstacle path: $190$ pair-status events |
| Wall-cell count $N_{\mathrm{cell}}$ | number of sampled cells or points on an evaluation grid satisfying a declared wall predicate | Rubik 2D slice: one $\Sigma_{\mathrm{comm}}$ hit on the chosen $20\times20$ evaluation grid |
| Repair index $R_W$ | $D_{\mathrm{repaired}}/\mathrm{frozen}_{R_1}$ when both are defined | Clifford+CNOT: $6/6=1.0$; Pauli: $0/8=0$ |
| Repair persistence $p_W$ | parameter-range length, measured relative to the normalized deformation parameter, for which a repaired channel remains accessible after activation | CNOT-strength interpolation: threshold $0.55$, $p_W=0.45$, stability $100\%$ |
| Oscillation index $O_W$ | number of sign changes or oscillatory reversals in a plateau diagnostic | Rubik generator-weight plateau: $3$; Yang-like state mixing: $0$ |
| Plateau index $P_W$ | number, length, or collapse profile of plateau intervals in $P_d(t)$ | Yang-like and training-coupled diagnostics supply initial plateau profiles |
| Depth index $\bar D$ | maximum recorded $D$ over sector pairs, with cutoff-unreached entries marked separately | some audits serialize cutoff-unreached entries as the sentinel $999$; this is not proof of global impossibility; transformer diagnostic has $\bar D=2$ |
| Rate ratio $\rho_W$ | slow observable time divided by fast observable time | NN GD+WD proxy: about $2\times$; ridge row/null diagnostic: about $68553\times$ |
| Spectral gap $\gamma_W$ | normalized second-gap or transition-gap diagnostic for a registered species | Clifford+CNOT registry example: about $0.73$; Pauli control: $0$ |
| Codimension $c_W$ | local or computational codimension when an ambient geometry is available | $\Sigma_{\mathrm{comm}}$: $11$; $A_1$: $1$; $A_2$: $2$ |
| Wall density $\delta_W$ | fraction of species in the Paper XI wall-density taxonomy sample exhibiting a given wall type | 15-entry sample shown below |

These quantities make the taxonomy operational. A later SOF diagnostic report
can emit a wall spectrum together with $N_{\mathrm{cross}}$, $N_{\mathrm{evt}}$, $N_{\mathrm{cell}}$, $R_W$, $P_W$, $O_W$, $\bar D$,
$\rho_W$, $\gamma_W$, $c_W$, $p_W$, and $\delta_W$ whenever the corresponding
observable layer is defined. For example, a transformer diagnostic need not
prove a wall theorem; it may report crossing count, wall-cell count, repair index, plateau or
oscillation index, and depth index as observable features of the model under
the chosen sectorization.

***

## Wall Coordinates

Taxonomy classes record wall mechanism. They do not by themselves record where
the wall lies, which observables increase or decrease, whether the realized
shadow is smooth or discrete, or whether the evidence is deterministic,
ensemble-defined, or pathwise stochastic. Paper XI therefore associates to a
wall record the profile

$$
\mathrm{Prof}_W(\mathcal W)
=
(\mathrm{Class},\mathrm{Pos},\mathrm{Ori},\mathrm{Reg},\mathrm{Sto}).
$$

The five entries have different roles. `Class` is a mechanism label from the
A--F taxonomy. The remaining four entries are realization coordinates.

### Position

$\mathrm{Pos}$ records how the wall sits in the declared deformation domain:

| Position type | Meaning |
|---------------|---------|
| endpoint | the wall is attained only at the endpoint of the sampled path |
| interior | the change locus is bracketed on both sides inside the domain |
| boundary | the wall lies on a stopping, absorbing, or realization boundary |
| transition window | an ensemble or finite-resolution audit localizes an interval rather than a single point |

Position is relative to the declared deformation and sampling protocol. An
endpoint in one restricted path may be an interior point in a larger parameter
space.

### Observable Orientation

$\mathrm{Ori}$ records the dominant observable response. It is generally a
vector rather than a sign:

$$
\mathrm{Ori}(\mathcal W)
=
(\Delta\mathrm{gap},\Delta R_1,\Delta R_2^{\mathrm{word}},
\Delta R_2^{\mathrm{Lie}},\Delta D,\Delta P_d,
\Delta\mathrm{Term},\ldots).
$$

Typical orientations include spectral closure, monotone opening or repair,
freezing or contraction, plateau deformation, and terminal-component loss.
This prevents a spectral gap closure from being mislabeled as negative
accessibility and permits different coordinates to move in different
directions across the same wall.

### Regularity

$\mathrm{Reg}$ records the regularity of the realized wall shadow:

| Regularity | Diagnostic interpretation |
|------------|---------------------------|
| smooth | a smooth observable field meets a local discriminant |
| piecewise smooth | smooth branches meet at kinks or switching surfaces |
| discrete | the native deformation or observed shadow changes by jumps |
| degenerate | the tested trajectory is flat, unresolved, or nontransverse |
| algebraic/incidence | a rank, image-kernel, or bridge-product relation controls the locus |

Regularity belongs to the wall record, not permanently to the source species.
A smooth native flow may produce a thresholded discrete shadow, and a discrete
species may admit a continuous weighting deformation.

### Stochastic Status

$\mathrm{Sto}$ records how randomness enters the evidence:

| Status | Meaning |
|--------|---------|
| deterministic | the declared realization and trajectory are fixed |
| constructed-random | a random direction or instance is sampled and then held fixed |
| ensemble | the wall is defined through a distribution of realizations |
| pathwise stochastic | individual stochastic trajectories define the native record |
| finite-time estimator | the wall is inferred from a sampling-dependent empirical observable |

These labels are claim-status aids. They do not impose a probability geometry
on the wall-coordinate space.

### Class C: Terminal-Structure Walls

Let
$\mathrm{Term}(\mathcal F_t)$ denote the terminal decomposition induced by the
declared dynamics and observable realization. Its components may be attracting
basins, absorbing or recurrent classes, dead components, or stopping regions.

> **Definition (Class C terminal-structure wall).** A Class C wall is a
> deformation locus at which $\mathrm{Term}(\mathcal F_t)$ is not locally
> equivalent: the number, identity, incidence, or persistence of terminal
> components changes.

The compatible sectorization may remain fixed. Class C does not require the
number of projectors or coarse sectors to change. A changing sector count is a
realization change or an additional nonsmooth/discrete coordinate; it is not,
by itself, the Class C mechanism. This definition includes absorbing Markov
classes, barrier/stopping regions, and deterministic GRN basin loss without
identifying their native dynamics.

### Four Canonical Profiles

The four extended profiles give a two-axis spread in orientation and
regularity, together with distinct stochastic status:

| Profile | Class | Position | Orientation | Regularity | Stochasticity |
|-----------|-------|----------|-------------|------------|---------------|
| constructed real-symmetric endpoint | A | endpoint discriminant | two order-one pair-gap closures | smooth conical local model | constructed-random direction |
| nested percolation | B/E | interior transition window | monotone opening and bounded-depth repair | pathwise discrete, ensemble-smoothed | ensemble |
| Kuramoto synchronization | D/E | finite-size interior crossover | freezing and occupancy contraction | smooth flow, thresholded shadow | matched ensemble |
| GRN regulatory-edge weakening | C | interior basin-loss bracket | terminal components $2\to1$; terminal sector loss | smooth deterministic flow, discrete terminal shadow | deterministic; stochastic noise sweep retained only as a negative control |

The four profiles share one record schema while retaining distinct coordinate
profiles, orientations, and regularity types.

The term **wall-coordinate space** is intentional. No equivalence relation,
topology, metric, curvature, coordinate-change law, or transport structure has
yet been imposed. Calling the present object a wall phase space would therefore
be premature.

***

## Observable Wall Taxonomy

Paper XI organizes signatures into a taxonomy before attempting any local
smooth model.

### Taxonomy Classes

| Class | Name | Diagnostic pattern | Typical examples |
|-------|------|--------------------|------------------|
| A | Collision walls | spectral or discriminant branches collide or merge | Rubik spectral deformation, smooth spectral probes, NCG spectral-block diagnostics |
| B | Repair walls | an inaccessible or frozen channel becomes accessible at a higher observable layer | Rubik repair, quantum $D$-repair, transformer sparse repair |
| C | Terminal-structure walls | the number, identity, incidence, or persistence of attracting, absorbing, dead, recurrent, or stopping components changes | GRN basin loss, absorbing Markov classes, barrier/stopping regions |
| D | Plateau walls | observables remain flat, delayed, oscillatory, or degenerate over intervals | Yang-like degeneration, training plateaus, grokking-style delayed rates |
| E | Nonsmooth or discrete walls | wall is induced by a discrete jump, rank selection, or piecewise-smooth kink | graph rewiring, ReLU kinks, Top-k activation selection |
| F | Bridge or incidence walls | bridge products, rank incidence, or algebraic association controls wall behavior | Rubik Type III/IV mechanisms, incidence products, bridge-level audits |

![Wall-coordinate map. The qualitative map places registered
observable morphologies by qualitative orientation and regularity. A--E are
shown on the two morphology axes; F is kept as an orthogonal bridge/incidence
coordinate. Positions record qualitative morphology only. The map is not a
metric, a phase space, or a classification of native
systems.](../../figures/paper11/fig2_observable_wall_taxonomy.png)

***

## Census Evidence

### Wall-Density Taxonomy Sample

In the 15-entry Paper XI wall-density taxonomy sample, wall density is computed as

$$
\delta_W(\mathrm{type})
=
\frac{\#\{\text{taxonomy-sample species carrying that wall type}\}}{15}.
$$

The table below is generated by the wall-density support artifact listed in
Appendix C.

The resulting finite-sample density table is:

| Wall type | Density | Dominant source |
|-----------|---------|-----------------|
| B repair | $33.3\%$ | 5 species; the most common wall type |
| F bridge/incidence | $20.0\%$ | Rubik naturally carries bridge and incidence walls |
| C terminal-structure | $13.3\%$ | barrier option and absorbing Markov examples |
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

For this record-level audit, a record is **eligible** when it has an explicit
deformation, an explicit change locus, a measured signature, and an existing
evidence file. The predeclared coverage target for each class is at least
three eligible records, two distinct species, and two deformation origins.
This is a curation threshold, not a classification theorem criterion.

The original census contains 24 records. The independently generated extended
census retains all 24 records and adds four controlled profiles: the constructed
real-symmetric endpoint, nested percolation, Kuramoto synchronization, and GRN
regulatory-edge weakening. It contains 28 records, 38 class memberships, and
19 eligible records:

| Class | Registered records | Eligible records | Eligible species | Deformation origins | Coverage |
|-------|-------------------:|-----------------:|-----------------:|--------------------:|----------|
| A | 4 | 3 | 2 | 3 | pass |
| B | 10 | 6 | 6 | 6 | pass |
| C | 5 | 4 | 4 | 4 | pass |
| D | 5 | 5 | 5 | 5 | pass |
| E | 6 | 5 | 5 | 5 | pass |
| F | 8 | 3 | 3 | 3 | pass |

All six classes now meet the predeclared record, species, and deformation target.
This is **coverage closure**, not taxonomy completeness. In particular, Class
A closes through a constructed real-symmetric endpoint whose degeneracy is
placed explicitly on the codimension-two discriminant. It is a non-Rubik
species witness, but not a naturally occurring generic GOE crossing.
Naturally occurring non-Rubik Class A breadth remains open. Full generated
tables and record provenance are stored in the repository artifacts listed in
Appendix C.

### Definition-Compatible Redundancy Audit

The listed wall diagnostics do not share one sampling unit.
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

***

## Observable Normal Forms and Wall Layers

### SOF-Native Observable Normal Forms

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
| Incidence mechanism | wall is defined by algebraic product or rank incidence | requires algebraic-geometric tools |

### Observable Layer

| Layer | Typical observable | Typical wall type |
|-------|--------------------|-------------------|
| Spectral | eigenvalues, collision quotients | spectral collision/discriminant |
| Accessibility | $R_1$, $R_2$, $D$, $\mathcal J_{\mathrm{acc}}$ | rank, support, or accessibility discriminant |
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
strength $1.00$ with no reversal. Thus the registered repair-persistence
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
clusters in a small synthetic transformer-like block. Attention top-k and FFN
activation-similarity operators give $R_1=58.3\%$, $R_2=66.7\%$,
$D_{\mathrm{repaired}}=2$, and $D_{\max}=2$ in the default audit. This is an
activation-induced diagnostic wall record: it shows how token-sector
decompositions can expose cross-sector influence, but it is not a theorem
about all transformers or LLM explainability.

### Constructed Real-Symmetric Endpoint

**Setup.** The non-Rubik Class A witness is the family

$$
H(t)=D+tV,
\qquad
D=\operatorname{diag}(1,1,2,3,4,4),
$$

with $V$ a sampled GOE splitting direction. The endpoint $D$ is deliberately
placed on the real-symmetric double-eigenvalue discriminant.

**Observed wall record.** The two isolated target gaps have fitted local orders
$1.000015$ and $0.999968$ in the canonical draw, with first-order splitting
coefficients $0.598557$ and $0.333281$. The minimum non-target gap on the
tested local interval is $0.937503$. Four sampled transverse splitting
directions pass the local-order and endpoint-lifting controls.

For a $2\times2$ degenerate block, the traceless normal coordinates $(x,y)$
give

$$
\operatorname{gap}=2\sqrt{x^2+y^2}.
$$

The one-parameter family follows a ray through this conical normal slice, so
the pair gap opens linearly. Endpoint-preserving changes of the splitting
direction remain transverse in the tested draws, while perturbing $D$ off the
discriminant removes both collisions.

**SOF interpretation.** This is a constructed Class A $A_1$-type endpoint
witness: a smooth local collision record with two order-one pair-gap closures.

**Boundary.** This is not a generic one-parameter GOE crossing and not an
unrestricted structural-stability theorem. It closes the predeclared finite-sample Class A
coverage target through a constructed witness; naturally occurring non-Rubik
Class A breadth remains open.

### Nested Percolation Opening

**Setup.** For each Erdos--Renyi ensemble member, one symmetric threshold
matrix $U=(U_{ij})$ is fixed and

$$
G(p)=\{ij:U_{ij}<p\}.
$$

The path is nested: edges are added but never removed. Raw adjacency is used
as the nonnegative word-transport observable.

**Observed wall record.** In the default 32-member ensemble, the largest mean
bounded-depth frozen-count drop occurs at $p=0.08$, while the largest ensemble
fluctuation occurs at $p=0.10$. Across the robustness audit, the opening
window lies in $p\in[0.08,0.10]$. Direct support and bounded-depth
reachability are verified to be monotone for every nested realization.

**SOF interpretation.** This is a B/E profile: a monotone repair wall in
orientation, with a pathwise discrete record and an ensemble-smoothed
transition window.

**Boundary.** The result is pathwise discrete and ensemble-smoothed only.
Degree normalization followed by skew-symmetrization would permit cancellation
and would destroy the monotone support control. This is not a theorem about
arbitrary percolation processes or a claim that all opening walls have the
same local geometry.

### Kuramoto Freezing Orientation

**Setup.** The Kuramoto control fixes each natural-frequency sample and initial phase
vector across the complete coupling sweep. Frequencies are centered so that
the $(r,\psi)$ sectorization is evaluated in a common co-rotating frame. The
raw directed trajectory transition is the word observable.

**Observed wall record.** In the default eight-member matched ensemble, the largest mean freezing step
occurs at $K=1.6$. Between $K=0.8$ and $K=2.4$, the bounded-depth frozen count
increases by $273.4\pm38.0$, with positive direction in every tested member.
Across the robustness audit the crossover lies in $K\in[1.6,1.8]$. The
continuum Gaussian synchronization scale $K_c\approx1.277$ is only a reference.

**SOF interpretation.** This is a D/E profile and a negative-orientation wall:
stronger coupling produces occupancy contraction and more frozen sector pairs.
Wall orientation therefore cannot be identified universally with repair or
increasing accessibility.

**Boundary.** The SOF wall location depends on finite size, time window,
sector resolution, and depth cutoff. This is not a synchronization theorem,
nor a universal statement about Kuramoto criticality.

### GRN Terminal-Structure Loss

**Setup.** The GRN positive record varies the strength $\lambda$ of one repression edge
$A\dashv B$ continuously from $1$ to $0$ in a deterministic toggle-switch
flow. The compatible $8\times8$ concentration sectorization is fixed.

**Observed wall record.** At $\lambda=1$ the controlled initial grid reaches
two attracting basins; after the edge is removed only one remains. The coarse
scan brackets the basin loss in $[0.50,0.55]$, and the controlled-initial
refinement gives $[0.520,0.525]$. The terminal-sector set changes from
$\{5,40\}$ to $\{5\}$.

**Methodological correction.** The initial-release low-$\Omega$ noise-wall interpretation is
withdrawn. Under a matched fixed-time protocol with the same concentration grid and raw directed
observable, a $3$-seed by $12$-trajectory comparison gives CLE and exact SSA
frozen-depth ranges of $0.94\%$ and $0.89\%$, respectively, a maximum method
gap of $6.7/4032$, and no SSA basin switches for
$\Omega=60,30,15,10$.

**SOF interpretation.** This is the canonical Class C terminal-structure
wall: terminal components change from $2$ to $1$ and one terminal sector is
lost. The positive evidence is deterministic terminal-structure loss, not
stochastic basin merging.

**Boundary.** The refined interval is a numerical diagnostic, not a
saddle-node theorem. The fully deleted edge is a discrete endpoint
intervention, while the primary wall is the interior change in the terminal
decomposition along the continuous $\lambda$ deformation. No stochastic
basin-merging or absorbing-state theorem is claimed. The superseded discrepancy
resulted from mixing event-count sampling with incompatible sector and
observable choices.

### Extended Profile Robustness

The unified extended-profile robustness audit evaluates the same canonical
implementations used for the individual profiles. Four sampled GOE splitting directions pass
the local-order and endpoint-lifting controls; nested percolation gives a wall
window $[0.08,0.10]$; matched Kuramoto controls give a freezing window
$[1.6,1.8]$; and the GRN terminal-component loss remains in the
controlled-initial bracket $[0.520,0.525]$. These are protocol-scoped
robustness statements, not universality results.

***

## Supporting Audit Boundaries

Two boundary audits are deferred to the appendices. Appendix A records the
branch-aware adjacency falsification audit for Rubik spectral pair responses.
Appendix B records the observable-status trajectory audit. Their shared
main-text role is cautionary: sorted gaps should not be promoted to ADE
adjacency without branch continuation, and static inaccessible pairs should not
be relabeled as walls without a change along a declared deformation path.

***

## Taxonomy Registry Summary

This compact registry view records only species or realization, assigned wall
class, and claim boundary. It does not repeat the experimental descriptions or
replace the record-level claim-status data in the five-layer census.

| Species / realization | Wall class | Claim boundary |
|-----------------------|------------|----------------|
| Rubik spectral snapshot | A reference: fixed finite arrangement | Exact snapshot; not a moving wall by itself. |
| Rubik spectral deformation | A: higher-order endpoint with 16 pairwise $A_1$ closures | Smooth-branch diagnostic; no tested $A_2\to A_1+A_1$ split. |
| Rubik $\Sigma_{\mathrm{comm}}$ slice | A/B anchor: sparse sampled intersection | Boundary diagnostic; codimension $11$ belongs to Paper VI. |
| Accessibility $R_1/R_2/D$ | B: support or first-depth repair jump | Conditional on a declared deformation and threshold. |
| Rubik Type III/IV mechanisms | F: cancellation and rank-incidence structure | Algebraic evidence; not ADE by default. |
| Quantum accessibility | B: entangling-gate $D$-repair | Diagnostic evidence; local model unclassified. |
| Markov absorbing boundary | C: unrepaired terminal component | Diagnostic evidence; not ADE by default. |
| Graph edge rewiring | E: discrete gap and support change | Outside smooth ADE. |
| Barrier-option stopping sector | C/D: first-hitting boundary | Registry diagnostic; hitting time is not SOF depth. |
| NN training dynamics | D: delayed or ordered proxy response | Paper IX/X proxy evidence; rate order is not a wall class. |
| ReLU / Top-k activations | E: kink or rank-selection jump | Requires nonsmooth or stratified models. |
| Transformer activation sectors | B/E: sparse token-sector repair | Diagnostic handoff; activation-derived sectorization. |
| Yang-like state mixing | D: plateau degeneration | Comparison branch; model-dependent smoothness. |

***

## Scope and Claim Boundary

Paper XI classifies **observable wall records**. It does not classify the
underlying dynamical systems, phase transitions, singularities, PDE
bifurcations, or catastrophe-theory objects themselves. These native
structures may be related to a wall record, but they are not identified with
it.

Paper XI intentionally avoids introducing a formal wall geometry. The
wall-coordinate map is a qualitative visualization of observable morphology,
not a metric, topology, curvature theory, or coordinate-change structure.

Different systems may generate identical wall records, while the same system
may generate different wall records under different observable families or
sectorizations. The record language is therefore intended for comparison of
observable morphology, not for replacing the native theory of a registered
species.

Accordingly, Paper XI does not claim:

1. a complete classification of all SOF trajectories or their native systems;
2. that Arnold ADE applies to all SOF branches, including graph rewiring or
   activation-induced walls without extension;
3. that the mechanism-separation principle or rate hierarchy alone determines
   wall class;
4. that Paper XI supplies general transformation laws for observables across
   walls;
5. that the wall assignment is full, faithful, or invariant under all weak SOF
   comparisons;
6. that the listed diagnostics form a complete invariant system or that the
   observable normal forms are classification theorems;
7. that the tested Rubik slices exhibit $A_n$ adjacency or that the constructed
   endpoint is a generic GOE crossing;
8. that finite-sample census coverage is taxonomy completeness or a population
   estimate;
9. that the wall-coordinate space already has a metric, topology, curvature,
   coordinate-change law, or transport structure;
10. that the GRN audit establishes a stochastic basin-merging or
    absorbing-state theorem.

The stable claim is narrower:

SOF wall behavior is first organized by observable wall records, wall
signatures, wall spectra, computable observable diagnostics, and wall-coordinate
profiles. The Observable Wall Taxonomy groups those signatures into collision,
repair, terminal-structure, plateau, nonsmooth/discrete, and bridge/incidence
classes. The extended census closes the predeclared record, species, and deformation target
for every class, while retaining explicit constructed-evidence and
natural-occurrence boundaries. Observable normal forms organize the registered
signatures before any smooth singularity model is invoked. ADE-type local
modeling is one candidate subtheory for sufficiently smooth wall records, not
the whole theory.

***

## Conclusion

Paper XI is about **observable wall morphology**, not universal wall dynamics.
Its purpose is to organize observable wall morphology rather than derive
universal wall-transition laws. It turns SOF wall phenomena into a
proto-geometric record-level
classification problem. Its basic output is not a universal wall-crossing law,
but a sequence of observable records, signatures, wall spectra, wall
diagnostics, and wall-coordinate profiles that can be compared across
registered SOF species. Mechanism classes answer what kind of wall occurs;
position, orientation, regularity, and stochasticity answer how that mechanism
is realized. Smooth ADE-style normal forms remain candidate local models only
on sufficiently smooth discriminant branches; the taxonomy itself also admits
repair, terminal-structure, plateau/rate, nonsmooth/discrete, and
bridge/incidence records.

The four extended profiles show why both layers are needed. Spectral gaps may
close, accessibility may open, synchronized dynamics may freeze, and terminal
components may disappear. The record language is common; the realized geometry
is not. The extended census reaches the predeclared finite-sample coverage target for A--F, but
coverage closure is not classification completeness.

***

## Outlook

Paper XI supplies a wall-coordinate taxonomy, not a classification theorem.
The next stage is to determine which coordinates are stable under comparison
of SOF presentations, which depend on the chosen ladder or sampling path, and
which admit local geometric normal forms.

The remaining classification program has seven parts:

1. develop or import piecewise-smooth and stratified wall theory for
   activation-induced and rank-selection SOFs;
2. formalize comparison and equivariance conditions for
   $\mathrm{WallAssign}(\mathcal F,\mathcal L,\Gamma)$: defining compatible
   comparison data is straightforward, but proving invariance under weak SOF
   comparisons, path reparametrizations, and sampling refinements is a separate
   theorem-level problem;
3. define equivalence and admissible coordinate changes for wall profiles;
4. test normalization and sampling stability before introducing any wall metric;
5. build continuous graph and Markov deformation models where smooth
   discriminants can be computed;
6. compute local codimensions for accessibility discriminants and higher-order
   spectral endpoints;
7. separate incidence varieties from smooth singularity classes.

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
$A_2\to A_1+A_1$ split candidate is detected. The sorted-index
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

The trajectory implementation records every change between adjacent samples, including
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

These are wall records on sampled paths. They do not establish ambient codimension,
continuous-time wall flow, or a bifurcation theorem. Their role is narrower:
they provide a correct dynamic record layer between Paper IX deformations and
the Paper XI taxonomy without relabeling every frozen pair as a wall.

***

## Appendix C: Computational Artifacts

The following repository artifacts provide the reproducible support layer for
the audits reported in this paper. The main text refers to audit roles rather
than file paths; this appendix records the exact implementation and generated
tables. Unless a prefix is shown, files are located under
`experiments/paper11/`. The prefixes `validation/` and `results/` are relative
to that directory; `paper10/` and `paper12/` are relative to `experiments/`.

| Artifact | Role in Paper XI | File |
|----------|------------------|------|
| C1 | cross-species wall diagnostics | `cross_species_wall_audit.py` |
| C2 | smooth spectral pair-gap local-model audit | `spectral_ade_collision.py` |
| C3 | auxiliary 2D commutativity-discriminant slice | `discriminant_bifurcation_map.py` |
| C4 | wall-density taxonomy sample | `wall_density_registry.py` |
| C5 | original 24-record wall-record coverage census | `wall_record_census.py` |
| C6 | original generated census tables | `results/wall_record_census.md`, `.json` |
| C7 | definition-compatible redundancy audit | `invariant_redundancy.py` |
| C8 | branch-aware adjacency falsification | `an_adjacency.py` |
| C9 | observable-status trajectory records | `wall_trajectory.py` |
| C10 | CNOT-strength repair persistence | `repair_persistence_quantum.py` |
| C11 | piecewise-smooth activation boundary | `piecewise_smooth_activation_wall.py` |
| C12 | barrier-option registry handoff | `paper10/barrier_option_sof.py` |
| C13 | transformer activation-sector handoff | `paper12/transformer_activation_sof.py` |
| C14 | constructed real-symmetric endpoint collision witness | `validation/degenerate_endpoint_collision.py` |
| C15 | nested percolation opening wall | `validation/percolation_wall.py` |
| C16 | matched Kuramoto freezing control | `validation/kuramoto_wall.py` |
| C17 | GRN CLE/SSA negative control and terminal-basin loss | `validation/grn_toggle_wall.py` |
| C18 | unified extended-profile robustness audit | `validation/wall_robustness_audit.py` |
| C19 | independent extended wall-record coverage census | `validation/wall_record_census_v2.py` |
| C20 | generated extended census tables | `results/wall_record_census_v2.md`, `.json` |

***

## References

**Program lineage.** Paper XI depends on Papers VII--X. Paper VII supplies the
generic completion and repair boundary \cite{paper7}; Paper VIII supplies the
SOF object layer \cite{paper8}; Paper IX supplies observable trajectories and
wall pullbacks \cite{paper9}; Paper X supplies the Universal Observable
Pipeline and five-layer SOF Registry \cite{paper10}.

**Smooth singularities.** Arnold's catastrophe and ADE singularity theory is
relevant only to the smooth-discriminant branch. Useful background includes
Arnold's *Catastrophe Theory* \cite{arnold1992catastrophe}, the work of Arnold,
Gusein-Zade, and Varchenko in *Singularities of Differentiable Maps*
\cite{arnoldGuseinVarchenko1985singularities}, and Golubitsky and Guillemin's
*Stable Mappings and Their Singularities* \cite{golubitskyGuillemin1973stable}.

**Stratified and nonsmooth walls.** Piecewise smooth, discontinuous, and
multi-stratum SOF walls require different tools. Relevant background includes
stratified Morse theory \cite{goreskyMacPherson1988stratified}, piecewise-smooth
dynamical systems \cite{dibernardo2008piecewise}, and differential equations
with discontinuous right-hand sides \cite{filippov1988discontinuous}.

**Spectral and finite-state diagnostics.** Graph and Markov wall records
are compared against spectral perturbation theory \cite{kato1995perturbation},
spectral graph theory \cite{chung1997spectral}, and Markov chain perturbation
and mixing theory \cite{seneta2006nonnegative} before any singularity
classification is claimed.

**Additional-profile precedents.** The constructed endpoint audit uses standard
degenerate perturbation theory and the von Neumann--Wigner codimension boundary
for real-symmetric level crossings \cite{vonNeumannWigner1929}. The percolation profile is interpreted
against Erdos--Renyi random-graph connectivity \cite{erdosRenyi1960evolution},
the synchronization profile against the finite Kuramoto model
\cite{kuramoto1975selfentrainment}, and the GRN method control against
Gillespie's exact stochastic simulation algorithm \cite{gillespie1977exact}.
These external theories
motivate the native deformation diagnostics; they do not supply SOF taxonomy
theorems automatically.
