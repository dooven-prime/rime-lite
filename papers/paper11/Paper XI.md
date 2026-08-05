# Typed Wall Morphology for Sectorized Observable Frameworks

### Sparse Wall Records, Coordinate Profiles, Multi-Label Taxonomy, and Local-Model Eligibility

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper is Paper XI of the RIME program. It develops wall-record
morphology, profile-relative coordinates, multi-label curation, and
local-model eligibility over the typed interfaces of Papers VIII--X. Strict
records require upstream wall admission; analogue morphology does not.*

***

## Abstract

**Problem.** A typed wall and a source-addressed finding do not yet determine
how the observed change should be recorded or organized. Fixed vectors
such as $(\Delta R_1,\Delta R_2,\Delta D,\Delta\tau,\Delta P_d)$ conflate
distinct carriers, force absent coordinates to look like zeros, and can promote
static findings or trajectory diagnostics into wall events.

**Approach.** For the strict branch, starting from an admissible wall datum
supplied by the typed deformation interface, this paper defines an ordinary
record construction
$\operatorname{RecordWall}_{P_W}(\mathfrak D_\kappa)$. A separate analogue
construction records included morphology without claiming wall admission. The corpus separates
morphology-record bundles from non-wall context records and distinguishes
strict wall records from included analogue morphology. Each morphology bundle
contains atoms that are either oriented trajectory events
with sparse before/after maps or domain-level locus samples with
incident-stratum germs. In the strict branch, one primary field carries the
record's upstream wall admission; in the analogue branch, it anchors morphology without
asserting strict admission. Separately registered context fields remain
co-observations. A Wall Profile $P_W$ selects fields and policies, while six
structured coordinate families record morphology and evidence. The declared
mechanism labels serve only as nonexclusive curation tags. A separate
eligibility gate determines whether a sufficiently smooth local branch may be
compared with an ADE-type model.

**Results.** The resulting architecture is

$$
\begin{aligned}
\text{Typed Wall Records}
&\longrightarrow \text{Wall Coordinate Profiles}\\
&\longrightarrow \text{Multi-Label Taxonomy}\\
&\longrightarrow \text{Local-Model Eligibility}.
\end{aligned}
$$

The finite census reads a source-pinned 28-row census, of which 27 rows remain
active. A versioned corpus-inclusion and upstream-admission reference ledger
places 5 strict wall bundles in the strict wall spectrum and retains 2
analogue morphology bundles in a separate analogue morphology set.
The remaining active rows are 5 static boundary witnesses, 2 pre-wall
references, and 13 trajectory diagnostics. The 27 active records carry 34
recomputed nonexclusive curation-tag memberships. Three anchors exhibit the
intended range: spectral pair-gap morphology with a branch-aware
$A_2\to A_1+A_1$ falsification audit, a paired affine/unitary CNOT
path-admissibility audit excluded from wall admission, and a discrete
graph endpoint.

**Boundary.** The construction is not a functor and no category of deformation
records is asserted. Wall coordinates are relative to the declared carrier,
chart, path, threshold, cutoff, normalization, sampling, and profile. Static
repair findings, plateau intervals, and rate separation are not walls without
a declared change locus. The census is not a complete classification, and ADE
terminology is restricted to eligible smooth local-model candidates.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $\mathcal F=(V,Q,Y;X,\mathcal H)$ | typed Sectorized Observable Framework (SOF), with optional independently declared Lie/Hall data |
| $\mathfrak D_\kappa$ | admissible wall datum for a selected typed field $\kappa$ |
| $P_W$ | Wall Profile declaring fields, conventions, and policies |
| $\operatorname{RecordWall}_{P_W}(\mathfrak D_\kappa)$ | ordinary wall-record construction |
| $e$ | one morphology atom |
| $\mathrm{WallCorpusEntry}$ | disjoint union of morphology-record bundles and wall context records; morphology bundles split into strict wall and analogue morphology records |
| $\mathcal C$ | a finite corpus of $\mathrm{WallCorpusEntry}$ values |
| $\mathrm{MorphologyAtom}$ | disjoint union of trajectory events and locus samples |
| $K_e$ | finite set containing the primary field and any registered context fields |
| $\delta_e^\gamma$ | oriented sparse before/after map for a trajectory event |
| $\delta_e^{\mathrm{loc}}$ | incident-stratum germ for a locus sample |
| $\operatorname{Prof}^{P_W}_W(e)$ | structured wall coordinate profile |
| $\operatorname{MorphSig}^{P_W}_W(e)$ | curation-independent morphology signature |
| $\operatorname{CuratedSig}^{P_W,v}_W(e)$ | versioned pairing of a morphology signature with a curation assignment |
| $\operatorname{Spec}^{P_W}_{W,\mathrm{str}}(\mathcal F,\mathcal C;\chi)$ | profile-relative multiset of admitted strict-SOF morphology signatures in context $\chi$ |
| $A_Y^+$ | positive-word algebra $\operatorname{alg}_{\mathbb C}(I,Y)$ |
| $A_Y^*$ | observable star-closure $C^*(Y)$ |
| $A_{Q,Y}^*$ | sector-enriched star-closure $C^*(D_Q\cup Y)$ |
| $R_1[Y]$ | aggregate direct operator support |
| $\operatorname{Route}_d[Y],W_d[Y]$ | routed-product and full-word support at length $d$ |
| $R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}}$ | direct and simple-commutator support on a registered Lie/Hall carrier |
| $D_\kappa$ | exact first-hit depth, when certified |
| $D_\kappa^{(\leq d_{\max})}$ | truncated first-hit depth with an explicit cutoff |
| `UNREACHED_AT_CUTOFF` | finite-audit state; never mathematical infinity |
| $A_k,D_k,E_k$ | Arnold singularity families, used only after local-model eligibility |

Arrows in diagrams denote construction or audit order unless a theorem
explicitly states otherwise.

***

## Introduction

The static object language supplies marked sectors, labelled observables,
distinct closure layers, and separate operator/word and Lie/Hall branches
\cite{paper8}. The deformation language supplies typed charts, comparison
maps, trajectories, selected fields, discriminants, walls, and policy-relative
response quantities \cite{paper9}. Capability declarations and evidence
routing are supplied by the compilation and Registry interface
\cite{paper10}. None of those layers needs a universal wall taxonomy.

This paper addresses the next, narrower question: once a typed wall datum or a
wall-related finding is available, what record role does it have, which
coordinates may be extracted, and which mechanism and regularity labels may be
attached without conflating carriers?

Paper IX determines when a typed observable change qualifies as a wall. This
paper does not redefine that wall; it records its typed changes, assigns a
profile-relative morphology, and organizes eligible records into a multi-label
taxonomy. Paper X supplies capability and evidence guards. This paper applies
those guards to source-addressed records without rebuilding either upstream
interface.

The stable division of responsibility is:

| Paper | Owning object |
|-------|---------------|
| VIII | static carriers, closures, and filtrations |
| IX | charts, trajectories, walls, pullbacks, and response policies |
| X | capability/evidence guards and Registry findings |
| XI | wall morphology, coordinate profiles, taxonomy, and local-model eligibility |
| XII | single-report protocol and presentation |
| XIII | two-report alignment and comparison |

The input to this paper is therefore not a bare static SOF. A wall depends at
least on a declared realization, a typed chart, a selected field, a policy, and
a parameter domain or trajectory. Moreover, the deformation-record interface
is not a category \cite{paper9}. These facts rule out a pseudo-functor

$$
\mathrm{SOF}_{\mathrm{str}}\longrightarrow\mathrm{WallRecord}.
$$

The construction introduced below is deliberately ordinary and
profile-relative.

***

## Related Work and Novelty Boundary

**Program interfaces.** Paper VII supplies static image--kernel incidence
geometry and promotion limits \cite{paper7}. Papers VIII--X supply the static
SOF object language, typed deformation and wall data, and capability-aware
evidence guards used here \cite{paper8,paper9,paper10}. Downstream, Paper XII
defines the single-report protocol \cite{paper12}, while Paper XIII defines
aligned cross-report comparison \cite{paper13}; neither supplies upstream wall
evidence.

**Local-model background.** Relevant external background includes Arnold's
catastrophe and singularity theory
\cite{arnold1992catastrophe,arnoldGuseinVarchenko1985singularities}, stable
mappings \cite{golubitskyGuillemin1973stable}, stratified Morse theory
\cite{goreskyMacPherson1988stratified}, piecewise-smooth systems
\cite{dibernardo2008piecewise}, and discontinuous differential equations
\cite{filippov1988discontinuous}.

**Domain precedents.** Spectral and finite-state diagnostics are compared with
spectral perturbation theory \cite{kato1995perturbation}, spectral graph theory
\cite{chung1997spectral}, and Markov perturbation theory
\cite{seneta2006nonnegative}. Additional bounded observations use
Erdos--Renyi random-graph connectivity \cite{erdosRenyi1960evolution}, finite
Kuramoto dynamics \cite{kuramoto1975selfentrainment}, and Gillespie simulation
\cite{gillespie1977exact} as domain precedents rather than SOF taxonomy
theorems.

**Novelty boundary.** This paper begins with wall data admitted under the
upstream deformation and evidence interfaces. Its contribution is the sparse
record structure, profile-relative morphology, nonexclusive curation, and
local-model eligibility layer. It does not redefine static SOF objects, wall
admissibility, compiler emission, report serialization, cross-report
alignment, or any downstream comparison result.

***

## Admissible Wall Data

### Upstream Input

**Definition 1 (Admissible Wall Datum).** An admissible wall datum
$\mathfrak D_\kappa$ consists of the data needed to
invoke one declared wall notion from the deformation interface:

1. a typed local chart with fixed labels, ranks, alphabet conventions, and
   comparison data;
2. a selected carrier-qualified field $O_\kappa$;
3. its declared discriminant or threshold policy;
4. a parameter domain or a selected trajectory $\gamma$;
5. a source-addressed evidence record and claim status;
6. any cutoff, saturation, norm, normalization, censoring, or sampling policy
   used by that field.

Changing labels, ranks, alphabets, or filtration schemas is a chart or schema
transition unless an additional comparison construction has been supplied. It
is not silently recorded as a fixed-chart wall.

A wall event or locus is recorded only after its corresponding upstream
admissibility conditions have been satisfied.

### Realization Kind, Record Role, and Field Family

Three independent fields prevent admission, function, and mathematical carrier
from being conflated:

| Field | Controlled values | Function |
|-------|-------------------|----------|
| `realization_kind` | `strict_sof`, `diagnostic_analogue` | states whether the source instantiates the strict SOF interface |
| `record_role` | `wall_event`, `wall_locus_sample`, `pre_wall_reference`, `static_boundary_witness`, `trajectory_diagnostic`, `retired_provenance` | states what the record does |
| `field_family` | spectral, operator, route, word, Lie-Hall, closure, state, graph, stochastic, proxy, or another declared family | identifies the typed field being observed |

Every source row receives exactly one realization kind and record role. Every
primary or context field receives its own field family and carrier identifier.
Only upstream-admitted, corpus-included `strict_sof` records with role
`wall_event` or `wall_locus_sample` enter the strict wall spectrum. A
corpus-included `diagnostic_analogue` may retain event or locus morphology, but it
remains in a separate analogue morphology set. Thus `diagnostic_analogue` is
neither a record role nor a field family.

This gate enforces

$$
\text{static repair finding}\neq\text{repair wall}.
$$

A plateau interval is a regime; its onset, exit, or collapse may be a wall
event. Rate separation is a trajectory diagnostic; a declared response-order
crossing may be a wall event. A cutoff-unreached pair is a state; a typed
transition into or out of that state may be an event.

***

## Typed Wall Records

### Wall Profile

**Definition 2 (Wall Profile).** A Wall Profile $P_W$ declares the interface
used for one wall-record construction. It contains:

1. enabled typed field keys;
2. carrier, alphabet, adjoint, route, word, and Hall conventions;
3. exact or truncated depth semantics and any cutoff;
4. chart, path, orientation, and event-segmentation rules;
5. norm, threshold, normalization, censoring, and sampling policies;
6. the evidence requirements and references to any applicable upstream
   promotion permissions for each retained coordinate.

Missing fields are omitted or marked unavailable. They are never manufactured
from a nearby carrier.

### Construction 1 (Profile-Relative Wall Corpus)

The corpus type is

$$
\mathrm{WallCorpusEntry}
=
\mathrm{MorphologyRecordBundle}
\sqcup
\mathrm{WallContextRecord}.
$$

The morphology-bundle type is

$$
\mathrm{MorphologyRecordBundle}
=
\mathrm{StrictWallRecord}
\sqcup
\mathrm{AnalogueMorphologyRecord}.
$$

A morphology record bundle contains a finite collection of morphology atoms.
A `StrictWallRecord` has an upstream-admitted primary wall field. An
`AnalogueMorphologyRecord` is included by the Paper XI corpus construction
without asserting upstream strict-wall admission. A wall context record
carries a pre-wall reference, static boundary witness, trajectory diagnostic,
or retired provenance entry and contains no morphology atom.

For an admissible datum
$\mathfrak D_\kappa$, define

$$
\begin{aligned}
\operatorname{RecordWall}_{P_W}(\mathfrak D_\kappa)
&\in \mathrm{StrictWallRecord},\\
\operatorname{RecordWall}_{P_W}(\mathfrak D_\kappa)
&=
(\operatorname{Addr},\operatorname{Role},\operatorname{Scope},\\
&\qquad
\operatorname{Policy},\operatorname{Events},\operatorname{Evidence}).
\end{aligned}
$$

where `Addr` is the source address and `Events` is a finite collection of
morphology atoms, ordered only when its declared context supplies an order. This is a
record-producing construction. No functor arrow, naturality law, or
weak-morphism transport is asserted.

Analogue morphology enters through a separate corpus-inclusion construction,
denoted $\operatorname{RecordAnalogueMorphology}_{P_W}$ when a name is
needed. It does not consume an upstream-admitted wall datum and does not
produce a `StrictWallRecord`.

For a morphology atom $e$ in a morphology bundle, the atom record is

$$
\begin{aligned}
W_e=
(&\operatorname{id},\operatorname{realization\_kind},
\operatorname{record\_role},\kappa_0,
\operatorname{primary\_carrier\_id},\\
&\operatorname{context\_field\_keys},
\operatorname{context\_carrier\_ids},
\operatorname{atom},\operatorname{policy\_refs},
\operatorname{evidence\_refs}).
\end{aligned}
$$

The atom type is the disjoint union

$$
\mathrm{MorphologyAtom}
=
\mathrm{TrajectoryEvent}
\sqcup
\mathrm{LocusSample}.
$$

The two summands are fully typed as

$$
\begin{aligned}
\mathrm{TrajectoryEvent}=
(&\operatorname{id},\operatorname{realization\_kind},
\operatorname{trajectory\_ref},\operatorname{orientation},\\
&\operatorname{event\_interval},\operatorname{sampling\_rule},
\operatorname{primary\_field},\\
&\operatorname{context\_fields},\operatorname{field\_registrations},
\delta_e^\gamma,\\
&\operatorname{policy\_refs},\operatorname{evidence\_refs}),
\end{aligned}
$$

and

$$
\begin{aligned}
\mathrm{LocusSample}=
(&\operatorname{id},\operatorname{realization\_kind},
\operatorname{domain\_context\_ref},\operatorname{event\_locus},
\operatorname{primary\_field},\\
&\operatorname{context\_fields},\operatorname{field\_registrations},
\delta_e^{\mathrm{loc}},\operatorname{probe\_path\_ref?},\\
&\operatorname{probe\_orientation?},
\operatorname{order\_semantics},\\
&\operatorname{policy\_refs},\operatorname{evidence\_refs}).
\end{aligned}
$$

For an oriented trajectory event, the sparse change map is

$$
\delta_e^\gamma
=
\left\{
q\longmapsto
\bigl(v_q^-,v_q^+,\operatorname{change}_q\bigr)
\right\}_{q\in K_e}.
$$

Its record must declare a trajectory reference, orientation, left/right
sampling rule, and event parameter or interval. The superscripts $-$ and $+$
refer to that declared orientation; they are not intrinsic labels on an
ambient wall locus. The primary field of a `wall_event` must contain present,
typed, and distinct endpoint values. `NOT_RECORDED` is therefore forbidden for
either primary endpoint.

For a domain-level locus sample, the change data instead form an
incident-stratum germ:

$$
\delta_e^{\mathrm{loc}}
=
\left\{
q\longmapsto
\left\{
\bigl(C_\alpha,v_{q,\alpha}\bigr)
\right\}_{\alpha\in A_e}
\right\}_{q\in K_e}.
$$

Here the $C_\alpha$ are incident local strata. There need not be a unique
before/after pair: a multiparameter bifurcation may have three or more
incident strata. If a transverse probe path supplies two-sided samples, the
record must retain its path and orientation and set `order_semantics` to
`probe_relative`. Without such a probe it uses `intrinsic_none`; an oriented
trajectory event uses `trajectory_oriented`.

The distinguished schema key
$\kappa_0=\operatorname{primary\_wall\_field}$ names the primary field. In a
`StrictWallRecord`, that field's upstream admissibility establishes the wall
atom. In an `AnalogueMorphologyRecord`, it anchors the recorded morphology but
does not assert wall admission. Other
keys in $K_e$ are `context_field_keys`. Each context field must carry its own
chart, comparison map, evidence reference, and every threshold, tolerance, or
cutoff policy applicable to that field. Inapplicable policy slots are
explicitly `not_applicable`.
Thus the record has the typed form

$$
\mathfrak D_{\kappa_0}
\rightsquigarrow
\left(
\delta_{\kappa_0},
\{\delta_q^{\mathrm{context}}\}_{q\in K_e\setminus\{\kappa_0\}}
\right).
$$

A context-field change is a co-observation only. It does not become a second
strict wall atom without independent wall admission, or a second analogue atom
without separate corpus inclusion. A constant context field
does not disprove the primary wall. In particular, recording a Lie/Hall wall
beside a word-field change does not identify the two carriers.

Each key $q$ is a typed tuple

$$
q=(f_q,n_q,c_q),
$$

where $f_q$ is its field family, $n_q$ is its registered field name, and
$c_q$ is the convention map containing the applicable carrier, alphabet,
depth, pair-scope, reduction, and policy parameters. Representative
registrations are:

| Field family | Registered field name | Convention parameters |
|--------------|-----------------------|-----------------------|
| operator | `operator.direct_support[Y]` | labelled alphabet $Y$ |
| route | `route.support[Y,d=2]` | route length $d=2$ |
| word | `word.support[Y,d=2]` | word length $d=2$ |
| word | `word.depth_truncated[Y]` | cutoff $6$ |
| Lie-Hall | `lie.simple_commutator_support[X]` | registered Lie family $X$ |
| Lie-Hall | `lie.depth_truncated[X,H]` | Hall convention $H$, cutoff $4$ |
| closure | `closure.observable_star.marked_corner_dimension[Y,i,j]` | off-diagonal pair scope |
| closure | `closure.observable_star.marked_corner_dimension[Y,i,i]` | Hilbert--Schmidt scalar-complement reduction |
| closure | `closure.sector_star.marked_corner_type[Q,Y,i,j]` | marked sectors $Q$ and alphabet $Y$ |
| spectral | `spectral.gap` | declared normalization and gap policy |
| proxy | `proxy.response_time[policy]` | declared response policy |
| state | `state.first_hit_time[policy]` | declared first-hit policy |

Raw diagonal unital corners are not compared without a declared reduction
convention. An unrecorded endpoint may carry the record-field presence marker
`NOT_RECORDED` only on non-admitting context or reference fields; an absent
capability is typed as unavailable.
`NOT_RECORDED` is neither a Paper X IR result state nor a Paper XIII
comparison state. Neither marker is numerical zero.

#### Directional Semantics

Every trajectory delta also carries the direction tuple

$$
\operatorname{Dir}_e(q)
=
\left(
d_n(q),d_a(q),d_s(q)
\right),
$$

whose components have distinct meanings:

| Component | Meaning |
|-----------|---------|
| $d_n$ | direction of the recorded numerical value |
| $d_a$ | direction of accessibility under the field's declared order |
| $d_s$ | event-relative meaning, such as gain, loss, repair, or terminalization |

For example, an endpoint repair may decrease a depth or unreached-pair count
while increasing accessibility. Direction without this qualifier is not a
valid wall coordinate.

![**Figure 1:** Profile-relative wall-record construction. Paper IX supplies
wall-admissibility conditions and deformation data, while Paper X supplies
capability and evidence guards. Paper XI records a discriminated morphology atom: an oriented
trajectory event has a sparse before/after map, whereas a domain-level locus
sample has an incident-stratum germ without intrinsic two-sided order. The
primary field and context co-observations remain separately registered, and
strict-SOF signatures remain separate from diagnostic-analogue
morphology.](../../figures/paper11/fig1_wall_record_pipeline.png)

### Independent Pair States

For a fixed-schema pair audit, the state is a bundle rather than a ladder:

$$
S_{ij}(t)=
\left(
s_{\mathrm{op}},
s_{\mathrm{route}},
s_{\mathrm{word}},
s_{\mathrm{Lie}},
d_{\mathrm{word}}^{(\leq m)},
d_{\mathrm{Lie}}^{(\leq n)},
s_{\mathrm{terminal}}
\right),
$$

with only declared components retained. Direct support, a word witness, and a
Lie witness may coexist. Terminality is not a competing transport layer.
Adjacent samples produce the sparse component change

$$
\delta S_{ij}(t_k)
=
S_{ij}(t_{k-1})\rightsquigarrow S_{ij}(t_k),
$$

where the arrow denotes a recorded before/after transition, not subtraction in
a common vector space.

### Closure Fields

The three closure layers remain distinct:

$$
A_Y^+,\qquad A_Y^*,\qquad A_{Q,Y}^*.
$$

The record schema may include dimension or corner-dimension changes for the
positive algebra. Observable-star and sector-star records may separately track
marked corners, abstract algebra type, and concrete embedding. An unchanged
abstract star-algebra type does not imply unchanged marked corners or concrete
embedding.

Finite-dimensional $C^*$-algebras admit standard Wedderburn decomposition,
but $A_Y^+$ is not automatically a $C^*$-algebra or semisimple. A
positive-algebra field may use Wedderburn terminology only when a separate
semisimplicity certificate is declared.

***

## Wall Coordinate Profiles

### Six Structured Coordinate Families

The derived coordinate profile is

$$
\operatorname{Prof}^{P_W}_W(e)
=
\bigl(
\operatorname{FieldFamilies},
\operatorname{EventKinds},
\operatorname{Regularity},
\operatorname{PersistenceProfile},
\operatorname{Geometry},
\operatorname{Evidence}
\bigr).
$$

These families use the following controlled vocabulary:

| Family | Values |
|--------|--------|
| Field families | operator, route, word, Lie-Hall, closure, spectral, state, graph, stochastic, proxy, or another declared typed family |
| Event kinds | any declared subset of support gain/loss, rank jump, first-hit change, collision, repair, terminalization, plateau onset/exit, response-order crossing, boundary hit |
| Regularity | smooth, stratified, piecewise smooth, discrete, stochastic, unknown |
| Persistence profile | any declared subset of transient, persistent, oscillatory, plateau, terminal, unresolved |
| Geometry | location: interior/boundary/endpoint; crossing: transverse/tangent/unresolved; codimension status: certified/unresolved |
| Evidence | Theorem, Computational Certificate, Computational Observation, Research Program |

Event kinds and persistence entries need not be single-valued, and geometry is
a structured object rather than one categorical coordinate. Censoring and
sampling remain observation policies in $P_W$, not regularity types. These
entries are wall coordinates or diagnostics, not automatically
invariants. Crossing counts depend on sampling; lengths and response times
depend on parameterization and policy; truncated depth depends on cutoff;
spectral gaps depend on normalization; codimension depends on the ambient
chart; and census prevalence depends on the selected sample.

### Wall-Profile Relativity Principle

> **Principle (Wall-Profile Relativity).** A source system does not determine a
> unique wall record or wall spectrum. The result is indexed by its typed
> realization, chart, selected field, parameter domain or trajectory, and Wall
> Profile.

Accordingly, morphology identity is defined without curation metadata:

$$
\begin{aligned}
\operatorname{MorphSig}^{P_W}_W(e)
=
\left(
\operatorname{RealizationKind}(e),
\operatorname{Role}(e),
\operatorname{AtomKind}(e),
\operatorname{PrimaryFieldFamily}(e),\right.\\
\left.
\operatorname{PrimaryCarrierId}(e),
\delta_e,
\operatorname{Prof}^{P_W}_W(e)
\right).
\end{aligned}
$$

where $\delta_e$ denotes $\delta_e^\gamma$ or
$\delta_e^{\mathrm{loc}}$ according to the atom type. A versioned curated
view is the separate object

$$
\operatorname{CuratedSig}^{P_W,v}_W(e)
=
\left(
\operatorname{MorphSig}^{P_W}_W(e),
\operatorname{Curate}_v(e)
\right).
$$

Changing a curation rulebook may therefore change a curated view without
changing the morphology identity. For a finite corpus $\mathcal C$ of
$\mathrm{WallCorpusEntry}$ values, the profile-relative strict wall spectrum
of $\mathcal F$ is

$$
\operatorname{Spec}^{P_W}_{W,\mathrm{str}}(\mathcal F,\mathcal C;\chi)
=
\left\{\!\left\{
\operatorname{MorphSig}^{P_W}_W(e):
\substack{
e\in\mathcal C,\\
e\text{ is attached to }\mathcal F,\\
e\text{ is upstream-admitted}\\
\text{and is a strict-SOF morphology atom}
}
\right\}\!\right\}.
$$

Corpus-included diagnostic analogues define a separate set
$\operatorname{Morph}^{P_W}_{W,\mathrm{an}}(\mathcal C;\chi)$; they are not
members of $\operatorname{Spec}^{P_W}_{W,\mathrm{str}}$. Record role alone
therefore never promotes an analogue into the strict wall spectrum.

The context $\chi$ is either a trajectory context, including its orientation
and sampling rule, or a domain context, including its incident-stratum
convention and any probe. Different choices of sectorization, alphabet,
closure, filtration, path or domain, threshold, cutoff, or profile may yield
different spectra. This is a definition-level relativity statement, not a
theorem that two profiles are equivalent or comparable. Cross-profile and
cross-report alignment belongs to the comparison interface of Paper XIII.

![**Figure 2:** Structured wall coordinates and nonexclusive curation. The six
coordinate families form a typed morphology profile; sampling, censoring,
threshold, normalization, and cutoff remain policies in the Wall Profile.
The versioned curation tags are multi-label assignments rather than partition
classes, and neither coordinates nor tags promote a record into the strict
wall spectrum.](../../figures/paper11/fig2_observable_wall_taxonomy.png)

***

## Multi-Label Taxonomy

The six mechanism families are retained as full curation tags:

| Curation tag | Typical use |
|--------------|-------------|
| Collision | spectral or observable branches meet under a declared collision policy |
| Repair | a previously absent or cutoff-unreached typed field witness, support state, or finite-filtration reachability state becomes present |
| Terminal | a terminal component, stopping region, or endpoint structure changes |
| Plateau / rate | plateau or response-order morphology is recorded |
| Nonsmooth / discrete | piecewise-smooth, rank-selection, discrete, or censored behavior occurs |
| Bridge / incidence | route, word, commutator, or image-kernel mechanism is implicated |

The tags are not a partition and do not replace the structured coordinate
families. One event may be simultaneously `REPAIR`, `NONSMOOTH_DISCRETE`, and
`BRIDGE_INCIDENCE`. Conversely, a static `REPAIR`-tagged finding may remain a
`static_boundary_witness` and therefore stay outside the wall spectrum.
The slash-separated display names map to the corresponding
underscore-separated keys in the machine-readable census.

Each assignment is a versioned object

$$
\operatorname{Curate}_{v}(e)
=
(\operatorname{rulebook\_version},\operatorname{assignment\_source},
\operatorname{tags},\operatorname{override\_reason?}),
$$

not an untracked list copied from a source letter label. The active rulebook is
`paper11-curation-tags-v1.0`; it declares nonexclusive membership and records
any typed override to an inherited assignment.

Letter names are not used for the active tags because they suggest a partition
and conflict visually with Arnold's $A_k,D_k,E_k$ notation.

***

## Local-Model Eligibility

For any proposed local-model family $\mathcal M$ and local branch $B$ of a
declared discriminant, define the general eligibility predicate

$$
\operatorname{Eligible}_{\mathcal M}(B;P_W)
\in\{\mathrm{yes},\mathrm{no},\mathrm{unresolved}\}.
$$

The predicate asks whether the branch, evidence, and declared equivalence
notion satisfy the hypotheses of $\mathcal M$; it does not assign a model.
ADE terminology enters only as the smooth-singularity specialization

$$
\operatorname{Eligible}_{\mathrm{ADE}}(B;P_W)
:=
\operatorname{Eligible}_{\mathcal M_{\mathrm{ADE}}}(B;P_W).
$$

ADE eligibility requires all of the following:

1. a smooth finite-dimensional ambient chart near the point;
2. a locally defined smooth discriminant branch;
3. fixed carrier, labels, ranks, and field conventions;
4. sufficient differentiability for the proposed normal-form comparison;
5. a declared local equivalence notion and ambient dimension;
6. source-addressed evidence for transversality, tangency, or the relevant jet
   data;
7. explicit isolation of, or accounting for, unrelated invariant blocks and
   symmetry-protected degeneracies.

The machine record retains the legacy Boolean under
`compatibility.historical_census_eligible`. It does not reuse that field for
`local_model_eligibility`. Its `status` is `no`
only when at least one necessary condition is certified false; missing or
unchecked evidence yields `unresolved`.

An affirmative value means only that an ADE comparison is mathematically
meaningful. The local-model branch must first be identified:

| Branch | Required treatment |
|--------|--------------------|
| smooth discriminant | smooth local equivalence and jet analysis |
| stratified | stratum and incidence data |
| piecewise smooth | side-specific smooth data and switching rule |
| discrete | combinatorial event description |
| algebraic incidence | ambient algebraic variety and rank conditions |
| stochastic | stochastic model together with its declared sampling, censoring, and uncertainty policy |

These branches require distinct tools
\cite{goreskyMacPherson1988stratified,dibernardo2008piecewise,filippov1988discontinuous}.

The branch-aware audit in Appendix A is a negative eligibility control:
simultaneous small sorted eigenvalue gaps do not establish
$A_2\to A_1+A_1$ adjacency.

***

## Evidence Anchors

### Smooth-candidate Spectral Branch

A constructed real-symmetric endpoint has two isolated adjacent pair-gap
closures. Degenerate perturbation theory supports recording them as
first-order pair-gap closure candidates under the declared perturbation audit,
subject to the real-symmetric crossing
boundary \cite{vonNeumannWigner1929}. The independent branch-aware Rubik audit
continues eigenbranches within the $cp$, $ep$, $co$, and $eo$ invariant blocks
and detects no tested $A_2\to A_1+A_1$ split candidate. Thus pair-gap
morphology is retained while an unsupported ADE adjacency is rejected.

**Claim status.** Computational Certificate for the declared matrices,
parameter slices, and branch-matching rule. No generic ADE classification is
claimed.

### CNOT Path-Admissibility Diagnostic

Let $U_C=U_{\mathrm{CNOT}}$. Since $U_C=U_C^*=U_C^{-1}$, define its spectral
projectors

$$
P_- = \frac{I-U_C}{2},
\qquad
P_+ = I-P_-.
$$

The previously used strength interpolation is the affine path

$$
U_{\mathrm{aff}}(s)
=I+s(U_C-I)
=P_+ +(1-2s)P_-.
$$

It is singular at $s=1/2$: its rank is $3$, its determinant is zero, and no
finite matrix logarithm exists. Away from that point, the samplewise scalar
convention $\operatorname{Arg}(-x)=\pi$ gives

$$
L_{\mathrm{aff}}(s)
=
\begin{cases}
\log(1-2s)P_-, & 0\leq s<1/2,\\
\bigl(\log|1-2s|+i\pi\bigr)P_-, & 1/2<s\leq1.
\end{cases}
$$

Thus the skew-adjoint part is zero on the left component and $i\pi P_-$ on
the right component. The corresponding $0/12\to6/12$ side difference is tied
to a singular logarithm-domain crossing and a samplewise branch convention;
it cannot be promoted to an ordinary Lie/Hall trajectory wall.

The control replaces the affine interpolation by the fractional-CNOT path

$$
U_{\mathrm{uni}}(s)
=P_+ +e^{i\pi s}P_-,
\qquad
L_{\mathrm{uni}}(s)=i\pi sP_-.
$$

Here $U_{\mathrm{uni}}(s)=\exp L_{\mathrm{uni}}(s)$ is unitary and invertible
for every $s\in[0,1]$, with $U_{\mathrm{uni}}(0)=I$ and
$U_{\mathrm{uni}}(1)=U_C$. The $H$ and $S$ logarithms are held fixed using
explicit anti-Hermitian branches. On the declared 21-point grid, the bounded
support tuple

$$
\left(
N_{\mathrm{direct,unreached}},
N_{\mathrm{Lie,unreached}}^{(\leq4)},
N_{\mathrm{Lie,reached\ without\ direct}}^{(\leq4)}
\right)
$$

equals $(8,8,0)$ at $s=0$ and $(6,0,6)$ at every sampled $s>0$. Hence the
admissible control exhibits one-sided endpoint activation but no sampled
interior transition near $s=0.55$. The previously reported repair bracket
$(0.50,0.55]$ is withdrawn rather than repaired by reparameterization.

**Claim status.** The projector and path formulas are exact finite-dimensional
identities. The thresholded 21-point support census is a Computational
Observation. The retained record role is `trajectory_diagnostic`, with
`wall_admission=not_admitted`; no physical Hamiltonian mechanism or interior
repair wall is claimed.

### Nonsmooth/Discrete Branch

In the graph edge-weight control, the typed state bundle is constant for
$t<1$ and changes only when the weakened edges vanish at the endpoint. The
certificate records 6 pair events and 12 independent field changes at that
step. This is a discrete endpoint wall record; it is not assigned a smooth
codimension or ADE type.

**Claim status.** Computational Certificate for the declared 11-sample path.

The nested-percolation audit records the statistical field
`word.unreached_pair_count_at_cutoff[Y,cutoff=6,aggregation=ensemble_mean]`.
Its value is an ensemble mean of integer pair counts, not an individual
truncated word depth. The largest adjacent sampled drop occurs in the declared
probability sweep, but no threshold discriminant was fixed upstream. It is
therefore a `trajectory_diagnostic`, not a strict wall event.

**Claim status.** Computational Observation for the seeded 32-member ensemble
and cutoff $6$.

***

## Census Certificate

The typed census is generated from a SHA-256-pinned 28-row source census.
Corpus inclusion, record roles, and upstream admission references are read
from the versioned `results/wall_record_inclusion_ledger_v1.json` rather than
inferred from source identifiers. This ledger is not a wall-admission
authority.

| Record role | Count |
|-------------|------:|
| `pre_wall_reference` | 2 |
| `retired_provenance` | 1 |
| `static_boundary_witness` | 5 |
| `trajectory_diagnostic` | 13 |
| `wall_event` | 5 |
| `wall_locus_sample` | 2 |

The independent realization-kind census contains 19 `strict_sof` and 9
`diagnostic_analogue` rows. Seven morphology record bundles contain seven
morphology atoms: 5 strict bundles enter the strict wall spectrum and 2 analogue
bundles enter only the analogue morphology set. In this snapshot every
morphology bundle contains exactly one morphology atom, so bundle and atom
counts coincide; the schema does not identify these notions. The seven atoms
contain 10 registered atom-field entries: 8 trajectory-change entries and 2
locus-germ entries. Four entries are pair-scoped. These
entry counts are not counts of changed ordered pairs inside an aggregate
field.

In the compact table below, `CC` and `CO` abbreviate the controlled statuses
Computational Certificate and Computational Observation, respectively.

| Record | Corpus status | Primary field | Evidence |
|--------|-----------|---------------|--------|
| Rubik collision quotient | strict locus | `spectral.joint_sector_count` | `CC` |
| Rubik endpoint closures | strict event | `spectral.adjacent_gap` | `CC` |
| constructed route incidence | strict locus | `route.support[Y,d=2]` | `CC` |
| graph edge endpoint | strict event | `operator.direct_support[Y]` | `CC` |
| constructed GOE endpoint | strict event | `spectral.adjacent_gap` | `CC` |
| dynamic maze split | analogue morphology | `graph.component_count` | `CO` |
| GRN basin loss | analogue morphology | `state.terminal_component_count` | `CO` |

Every trajectory event in this table has present, typed, and distinct primary
endpoint values. The CNOT logarithm boundary, nested percolation sampled drop,
and barrier first-hit proxy are `trajectory_diagnostic` records rather than
admitted events. Among 27 active records, the regenerated nonexclusive
curation assignments have 34 memberships:

| Tag | Active records | Strict-wall records |
|-----|---------------:|------------------:|
| `COLLISION` | 4 | 3 |
| `REPAIR` | 9 | 0 |
| `TERMINAL` | 3 | 0 |
| `PLATEAU_RATE` | 4 | 0 |
| `NONSMOOTH_DISCRETE` | 7 | 1 |
| `BRIDGE_INCIDENCE` | 7 | 1 |

The zeros in the strict-wall column are intentional. Plateau/rate rows
remain diagnostics, while included terminal morphology is presently analogue
rather than strict. No coverage target requires every tag to appear in the
strict wall spectrum.

This finite source-addressed census has Computational Certificate status. Its
counts do not estimate population prevalence, prove tag independence, or
establish taxonomy completeness.

![**Figure 3:** Typed census and CNOT path-admissibility diagnostic. The left
panel shows the 27 active records by role and separately states the 5 strict
wall bundles, 2 analogue morphology bundles, and 34 regenerated nonexclusive
tag memberships. The right panel compares the singular affine interpolation
with the unitary fractional-CNOT control. The affine path changes across an excluded
logarithm-domain point; the latter has one sampled signature for every $s>0$
and no interior repair threshold.](../../figures/paper11/fig3_census_and_cnot_log_domain.png)

***

## Discussion and Ownership

The logical center is one-record morphology: upstream-admitted strict wall
records and separately included analogue morphology. Paper IX owns wall
admission, and Paper X owns capability and evidence guards. Paper XI neither
infers a wall from a static SOF nor fills missing upstream data.

The discriminated morphology-atom model resolves the orientation ambiguity:
trajectory events carry declared before/after order, whereas locus samples
carry incident-stratum germs. The realization/role/field-family split prevents
analogue status from being mistaken for event function or mathematical
carrier. Exact operator, route, word, Lie/Hall, closure, spectral, state, and
proxy fields can coexist as separately registered observations without being
promoted into one carrier or projected into a mandatory vector. The same
principle rules out a mutually exclusive pair-status ladder: independent
components may be simultaneously true, and the cutoff-unreached marker remains
a finite-audit state.

The profile-relative terminology also explains why many quantities sometimes
called "invariants" are only coordinates here. Their values remain useful, but
only relative to the declared
parameterization, cutoff, threshold, normalization, ambient chart, or sample.
An invariance claim requires a separate equivalence relation and proof.

The evidence anchors align with this boundary. The spectral audit tests local
smooth-model eligibility; the CNOT audit exposes a logarithm-domain boundary
and uses an admissible unitary control to reject the reported interior
threshold; and the graph endpoint exhibits admitted discrete morphology. The
finite census then shows that one record may carry multiple mechanism tags
while retaining one explicit record role.

The ownership boundary is equally important. Paper XII may present these
records in a single report, and Paper XIII may align coordinates from two
reports. Neither downstream operation changes a wall record or supplies
missing upstream evidence.

***

## Claim Status and Boundary

Definitions of record structure, coordinate families, record roles, curation
tags, and eligibility predicates are not additional evidence levels.
Reader-facing claims use exactly four levels:

| Claim | Status |
|-------|--------|
| imported wall-pullback and calibrated response results | Theorem |
| typed census, sampled trajectory audit, independently validated collision/incidence records, and branch-aware spectral audit | Computational Certificate |
| CNOT domain diagnostic and bounded percolation, Kuramoto, GRN, neural, and application-specific records | Computational Observation |
| wall-record functoriality, complete taxonomy, stable metrics, and universal local models | Research Program |

The theorem row remains owned by the cited upstream paper. Certificates are
finite and source-addressed; observations remain bounded by their declared
realizations and policies. Source artifacts retain their original ownership.
This paper owns only the derived wall records, coordinate profiles, curation
tags, eligibility decisions, and the finite census certificate.

### Excluded Claims

This paper does not claim:

1. a functor from a static or deformation category to wall records;
2. that a static finding, plateau interval, response hierarchy, or proxy is
   automatically a wall;
3. that operator, route, word, and Lie/Hall support or depth are interchangeable;
4. that positive-word, observable-star, and sector-enriched star closures have
   the same wall coordinates;
5. that `UNREACHED_AT_CUTOFF` or any legacy numeric sentinel means infinity;
6. that the Paper VI rank $11$/nullity $7$ linearization is a nonlinear
   codimension theorem \cite{paper6};
7. that sampled hit fractions are locus cardinalities or measures;
8. that wall coordinates are intrinsic invariants;
9. that the finite census is complete or prevalence-estimating;
10. that ADE types classify all SOF walls.

The exact response theorem and calibrated rate certificates remain owned by
Paper IX. This paper may register their morphology as diagnostic context, but
it does not turn a contraction-deficit ratio or response-time ordering into a
wall-rate invariant.

***

## Conclusion

This paper defines the morphology layer of the Sectorized Observable Framework
program. In the strict branch, an admissible wall datum is converted by an
ordinary, profile-relative construction into a bundle of oriented trajectory
events or incident-stratum locus samples. The analogue branch uses a separate
corpus-inclusion construction and makes no wall-admission claim. In both
branches, the primary field and separately registered context fields retain
their own carriers and policies. Realization kind, record role, and field
family remain independent coordinates. Derived morphology uses structured
field-family, event-kind, regularity, persistence, geometry, and evidence
families. Mechanism labels are versioned nonexclusive curation assignments,
and ADE comparison is a special case of a general local-model eligibility
test.

The finite evidence supports this architecture without promoting it to a
classification theorem. Five strict wall bundles enter the strict wall spectrum;
two included analogue morphology bundles remain in a separate analogue
morphology set, and static, pre-wall, diagnostic, and retired rows remain
outside the strict wall spectrum. Spectral morphology, the excluded CNOT wall
candidate with its admissible-path control, and the discrete
graph endpoint demonstrate the intended separation of local-model eligibility,
event morphology, diagnostic context, and evidence status.

***

## Outlook

The open program is to define admissible equivalences and reparameterizations
under which selected wall coordinates become invariant, to develop local
models for stratified and nonsmooth branches, and to study transport between
wall records only after an actual category of comparison data is defined.

Wall-record functoriality and naturality remain Research Programs. They must
not be inferred from the strict categories of Paper VIII or from the
record-only deformation interface of Paper IX.

***

## Appendix A: Branch-Aware Adjacency Falsification

The audit separates the Rubik representation into its invariant blocks and
continues eigenbranches by maximum adjacent-sample eigenvector overlap. A
candidate $A_2\to A_1+A_1$ split requires two isolated pair-gap minima at
separated parameter values whose union involves three branches. Persistent
degeneracies, endpoint-only closures, and cross-block equalities are rejected.

| Block | Dimension | Endpoint cluster sizes | Tested triples | Split candidates |
|-------|----------:|------------------------|---------------:|-----------------:|
| $cp$ | 64 | $8,24,24,8$ | 0 | 0 |
| $ep$ | 144 | $12,36,24,36,36$ | 0 | 0 |
| $co$ | 8 | $3,3$ | 2 | 0 |
| $eo$ | 12 | $3,3,3$ | 0 | 0 |

No branch-aware split candidate is detected on the tested diagonal and
asymmetric slices. A future positive candidate would still require local
normal-form and versality analysis.

***

## Appendix B: Sampled Typed-State Trajectories

The controlled trajectory artifact declares four independent typed fields:

$$
D_W^{(6)}[Y]:=D_{\mathrm{word}}^{(\leq6)}[Y],
\qquad
R_2^L[X]:=R_2^{\mathrm{Lie}}[X],
$$

where the abbreviated symbols are used only in the following compact table.

| Carrier | Typed field | Convention |
|---------|-------------|------------|
| operator | $R_1[Y]$ | labelled alphabet $Y$ |
| word | $W_2[Y]$ | exact word length $2$ |
| word | $D_W^{(6)}[Y]$ | truncated word depth at cutoff $6$ |
| Lie-Hall | $R_2^L[X]$ | simple-commutator support on the independently registered Lie family $X$ |

Every adjacent pair event retains all changed fields. The generated summary is:

| Control | Pair events | Field changes | Changed pairs | Change steps |
|---------|------------:|--------------:|--------------:|-------------:|
| GridWorld obstacle path | 236 | 314 | 174 | 1, 2 |
| SIR $\beta$ sweep | 4 | 10 | 4 | 1 |
| Graph edge-weight endpoint | 6 | 12 | 6 | 10 |

The counts are sampled-path coordinates. They do not establish continuous-time
wall flow or ambient codimension.

***

## Appendix C: Computational Artifacts

The following repository artifacts support the typed census, included
morphology records, finite robustness checks, and bounded observations used
above.
Unless another base directory is stated, short paths are relative to
`experiments/paper11/`.

### C.1 Census and Corpus Inclusion

| Artifact | Role | Short path |
|----------|------|------------|
| C1 | typed census producer and validator | \path{validation/typed_wall_record_census.py} |
| C2 | versioned corpus-inclusion and upstream-admission reference ledger producer and result | \path{validation/build_wall_record_inclusion_ledger.py}; \path{results/wall_record_inclusion_ledger_v1.json} |
| C3 | generated 28-row typed census and ownership summary | \path{results/wall_record_census_typed_v3.json}; \path{results/wall_record_census_typed_v3.md} |

C1 verifies the SHA-256-pinned source census, the inclusion ledger,
and every ledger evidence contract before generating C3. C2 separates upstream
wall admission from Paper XI corpus inclusion and binds each included entry to
its realization kind, record role, primary field, evidence schema, artifact
SHA-256, producer SHA-256, and reader-facing claim status.
The resulting census is a Computational Certificate for this finite
source-addressed curation; it is not a completeness or prevalence theorem.

### C.2 Wall Records and Bounded Audits

| Artifact | Role | Short path |
|----------|------|------------|
| C4 | typed pair-state trajectory producer and result | \path{wall_trajectory.py}; \path{results/wall_trajectory.json} |
| C5 | CNOT affine-path failure and unitary-path control producer and record | \path{cnot_logarithm_boundary.py}; \path{results/cnot_logarithm_boundary_v1.json} |
| C6a | Rubik spectral-endpoint producer and record | \path{spectral_ade_collision.py}; \path{results/rubik_spectral_endpoint_v1.json} |
| C6b | constructed GOE endpoint producer and record | \path{validation/degenerate_endpoint_collision.py}; \path{results/constructed_goe_endpoint_v1.json} |
| C6c | Rubik collision-quotient producer, result, independent validator, and certificate | \path{validation/produce_collision_quotient_result.py}; \path{results/rubik_collision_quotient_result_v1.json}; \path{validation/validate_collision_quotient_result.py}; \path{results/rubik_collision_quotient_validation_v1.json} |
| C6d | route-incidence producer, result, independent validator, and certificate | \path{validation/produce_route_incidence_result.py}; \path{results/route_incidence_result_v1.json}; \path{validation/validate_route_incidence_result.py}; \path{results/route_incidence_validation_v1.json} |
| C7 | nested-percolation producer and trajectory diagnostic | \path{validation/percolation_diagnostic.py}; \path{results/percolation_diagnostic_v1.json} |
| C8 | GRN terminal-basin producer and wall record | \path{validation/grn_toggle_wall.py}; \path{results/grn_terminal_basin_loss_v1.json} |
| C9 | bounded profile-robustness producer and record | \path{validation/wall_robustness_audit.py}; \path{results/wall_robustness_v1.json} |
| C10 | branch-aware $A_n$ falsification producer and results | \path{an_adjacency.py}; \path{results/an_adjacency.json}; \path{results/an_adjacency.md} |
| C11 | bounded Markov producer and source-hashed observation | \path{cross_species_wall_audit.py}; \path{results/markov_boundary.observation.json} |
| C12 | bounded Kuramoto producer and source-hashed observation | \path{validation/kuramoto_wall.py}; \path{results/kuramoto_freezing.observation.json} |

From the repository root, run an executable artifact as
`python experiments/paper11/<short path>`. C4--C10 support only the finite
records and claim boundaries stated in their result artifacts. In
particular, C10 is a negative adjacency control and does not establish a
positive ADE classification. C5 and C7 are Computational Observations and do
not enter the strict wall spectrum. C11 and C12 are Computational Observations
cached through `experiments/observation.py`; stale source hashes block reuse,
and the cached records do not enter the strict wall spectrum.

Imported evidence remains owned by its source manuscript and is bound through
C2 and C3 rather than duplicated here. Paper
XII may later serialize or present the resulting Paper XI records but supplies
no upstream wall evidence here. A downstream Paper XII artifact retained as
analogue corpus provenance does not constitute upstream wall admission.
All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).
