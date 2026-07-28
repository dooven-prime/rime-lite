# RIME Program Map

**Date**: 2026-07-28
**Status**: public narrative architecture map for Papers I--XIII, with a
Paper XIV horizon.

This document summarizes the program-level organization. It is not a proof
document and does not replace the manuscripts. Its purpose is to make the
language, layers, claim status, and Rubik/general-theory boundary visible to
readers of the paper series.

For the guiding philosophy behind the Rubik-to-general-theory transition, see
[PROGRAM_PHILOSOPHY.md](PROGRAM_PHILOSOPHY.md).

For the public post-Paper VII SOF arc, see [SOF_OBJECTS.md](SOF_OBJECTS.md),
[SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md), and
[SOF_REGISTRY.md](SOF_REGISTRY.md).

The active repository versions of Papers I--VII are maintained as independent
version-2 papers. This map may summarize their typed interfaces but cannot
reinterpret their theorem hypotheses, operator families, or claim status.
Release identities and DOIs are maintained once in the root
[Public Release table](../README.md#public-release).

---

## Active Accessibility Typing Rule

The current cross-paper middle architecture is:

```text
spectral admissibility gates, where applicable
  -> typed sector fields
  -> operator / routed-composition / full-word branch
     and a separate Lie / Hall branch
  -> branch-specific promotion or comparison certificates
```

In particular, Boolean graph paths, routed projected products, full ordered
words, commutator support, and Hall/Lie depth are distinct objects. Bare
`R_1`, `R_2`, `D`, `J_acc`, and `Sigma_access` names below are retained only
when describing a release-local manuscript convention. They must not be used
to infer a cross-channel theorem. Frozen papers retain their locally audited
semantics; any versioned reopening and all later-paper work must use typed
names without global search-and-replace migration.

The Paper VI and VII descriptions in this map are bounded summaries of their
frozen v2 manuscripts. They do not promote pointwise certificates into moving
field theorems or local incidence results into global accessibility claims.

Cross-paper connections are **typed interfaces, not a dependency chain**. A
paper may reuse the output type of a neighboring result, but it must redeclare
the actual object, hypotheses, realization, and claim status used locally. A
bibliographic citation identifies the neighboring result; it does not import
its theorem hypotheses or promote its output to a stronger object.

---

## 1. Core Architecture

The program has the following stable role summary:

```text
Papers I--III: independent Rubik-centered papers
Paper IV:      fixed finite collision arrangements and conditional spectral quotients
Paper V:       local direct-support and commutator-accessibility theory
Paper VI:      normality-gated point samples and moving-field research boundary
Paper VII:     incidence geometry, rank protection, and promotion limits
Paper VIII:    SOF object layer and strict morphisms
Paper IX:      SOF deformation geometry and observable trajectories
Paper X:       Universal Observable Pipeline and registry evidence
```

Program invariant / slogan:

```text
Spectral geometry determines the objects.
Compatible sectorization is the interface.
Observable geometry is the invariant.
Accessibility geometry determines their behavior.
Genericity tests when the behavior is stable.
```

The governing distinction is:

```text
Paper IV: fixed arrangement P, varying projection L_alpha
Paper VI v2: linearized constraints and normality-gated point registrations
Paper VI research target: moving P(w), defined only on certified spectral charts
                          Sigma_spec subset Sigma_normal subset Sigma_comm
```

Important distinction:

```text
Paper V cancellation/incidence = static low-order mechanisms.
Paper VI typed wall loci       = moving-field research program after all gates.
```

Historical drafts used the same bare `R_1` and `R_2` names across these layers.
The active architecture requires carrier-qualified names.

---

## 2. Public Paper Arc

| Paper | Role | Core object | Main question |
|-------|------|-------------|---------------|
| I | Block spectral census | `A_18` and reducing blocks | What is the canonical block spectrum, and which conditional arithmetic criteria apply? |
| II | Sector non-invariance and direct transport | registered QT/HT sectors, projected blocks, and `K` | When does direct off-diagonal transport occur, and how does it encode sector non-invariance? |
| III | Graph/operator separation | support graph, projected composition, image--kernel obstruction | When does graph reachability survive matrix composition? |
| IV | Collision geometry | fixed finite arrangement `P={(q_i,h_i)}` and linear projections | How do affine-branch collisions form quotient layers, and when may a numerical realization inherit that quotient? |
| V | Local support/commutator theory | `R_1^Lie`, routed `X`-products, `X`-word support, `R_2^Lie`, and `D_Lie` | Why does Boolean support fail to determine commutator accessibility? |
| VI | Linearized commutativity geometry | weighted QT/HT pairs, linearized constraints, and normality-gated point registrations | Which linearized directions preserve the declared constraints, and which samples pass the spectral registration gates? |
| VII | Projected-composition incidence | composable projected factors and fixed-rank incidence strata | When do nonzero factors compose, and what does local incidence fail to promote? |
| VIII | SOF object theory | finite SOF data, strict morphisms, naturality | What is the sectorized observable object? |
| IX | Observable dynamics | SOF deformations, trajectories, wall pullbacks, rate separation | How do SOF observables evolve under deformation? |
| X | Observable pipeline | source systems, sectorization origins, registry evidence | Why do different species share one observable pipeline? |

### Interface Connections, Not a Reading Order

| Paper | Self-declared input | Output interface | Missing promotion |
|-------|---------------------|------------------|-------------------|
| I | inverse-closed averaging family and reducing blocks | block census, compression-trace identity, conditional arithmetic criteria | no exact QT/HT registration or collision quotient |
| II | complete orthogonal sectors and declared transport family `rho(S)` | direct blocks, `K`, non-invariance, and block-local transport labels | support paths do not imply nonzero composition |
| III | declared projectors and transport maps | routed projected products and image--kernel obstruction criteria | no route-to-word, commutator, or Lie-depth promotion |
| IV | fixed finite `P` and `L_alpha`, or an exactly commuting Hermitian pair | collision classes and fixed-arrangement quotient census | numerical Rubik registration does not imply an exact joint spectrum |
| V | fixed sectors, declared skew-Hermitian family, and declared Lie filtration | `R_1^Lie`, routed `X`-products, `X`-word support, `R_2^Lie`, and cutoff/exact `D_Lie` | low-order support does not determine full Lie depth |
| VI | weighted QT/HT family plus commutativity, normality, and chart gates | full-matrix Jacobian certificates and pointwise typed registrations | no coherent moving projector field or wall theorem |
| VII | composable factors `A:E_k->E_i` and `B:E_j->E_k` | image--kernel incidence geometry and rectangular rank protection | no automatic route-to-word, commutator, Lie-depth, or represented-genericity promotion |

The useful neighboring interfaces are therefore limited and explicit:

- Paper II output may instantiate Paper III, but Paper III redeclares arbitrary
  sectors and transport maps.
- Paper III's local image--kernel criterion is compatible with Paper VII's
  matrix-pair input; Paper VII restates the factors and rank hypotheses.
- Paper IV's theorem applies pointwise only when an exact finite arrangement
  or exactly commuting Hermitian pair is supplied. A gated Paper VI numerical
  sample supports only a pointwise computational comparison unless that exact
  promotion is certified separately.
- Paper V supplies typed distinctions for Paper VI and Paper VII audits, not
  theorem premises for their stronger questions.
- Paper VII supplies a routed-product survival gate, not a global
  accessibility or completion theorem.

Papers I--III are independent Rubik-centered papers. Papers IV--VII address
compatible but self-contained general structures: fixed projection geometry,
typed low-order accessibility, linearized constraints, and composition
incidence. In Paper IV,
the finite-arrangement theorem and the exact census of the displayed rational
nine-point set are unconditional; identification of that set with the exact
Rubik QT/HT joint spectrum is a separate numerical registration and yields an
exact Rubik quotient only conditionally.
Papers VIII--X then package the sectorized observable object, deformation
dynamics, and cross-species observable pipeline.

Papers IV--VII form a neighboring family of compatible, self-contained
interfaces:

```text
Paper IV    fixed spectral geometry
Paper V     fixed typed accessibility objects
Paper VI    linearized constraints and pointwise typed registrations
Paper VII   routed-product incidence and promotion limits
```

The post-Paper VII SOF papers are organized around their own declared objects:

```text
Paper VIII  SOF object layer, strict morphisms, and naturality
Paper IX    SOF deformation geometry and wall dynamics
Paper X     Universal Observable Pipeline and registry evidence
Paper XI    Observable Wall Taxonomy
Paper XII   SOF Diagnostic Protocol and SOF Report Specification
Paper XIII  SOF Report Alignment and induced comparison signatures
Paper XIV   context-indexed interpretation and action semantics (horizon)
```

The descriptions of Papers VIII--XIII below report their published,
release-local objects. Their bare ladder, repair, and wall terminology is not a
cross-paper identification of operator support, routed composition, full-word
support, commutator support, and Lie depth. Migrating those papers to the
branched typed architecture requires an explicit versioned reopening, updated
artifacts and figures, and a new Registry version; the frozen Paper X Registry
v1 snapshot remains unchanged.

Published Paper VIII asks what the object is and proves its release-local
naturality statements on strict SOF data. Its carrier and depth semantics must
remain explicit. Paper IX asks how SOF objects deform
and why different deformation spaces generate different wall geometries. Paper
X asks why broad external species can enter one observable pipeline. Paper XI
classifies observable wall records, signatures, spectra, and taxonomy while
keeping ADE as a smooth-branch local model only. Paper XII introduces the
eight-field SOF Report Specification (SOFRS) v1.0 for one declared realization
or diagnostic probe system. It separates envelope validity from scientific
protocol admission, makes report relativity explicit, and distinguishes
white-box, trajectory-based, and API-level behavioral reports. Three
representative reports establish the reading protocol; a cross-domain
validation section then tests portability without identifying native
mechanisms. Its Black-Box SOF Diagnostic Principle states that a white-box
realization is sufficient but not necessary: stable probe sectors, measurable
outputs, evaluator provenance, and a weak claim boundary can support a
behavioral report. The slogan **No weights required. Only observables.** is a
protocol-level statement; white-box realizations may still use internal
weights or operators.

The protocol boundary is explicit: Paper XII is the single-system report
language, Paper XIII is the aligned comparison language, and Paper XIV is the
context-indexed action-semantics language. A `Repair Matrix` in SOFRS records
observed repair; it is not an intervention instruction. Common report syntax
does not itself supply sector alignment, observable alignment, normalization,
or a cross-report difference.

Paper XI keeps three computational boundaries explicit. Its trajectory
audit counts only adjacent observable-status changes, so a static frozen pair
is not a wall event. Its 166-configuration redundancy audit excludes
codimension, cross-species density, and trajectory-only quantities from the
snapshot PCA; the resulting three-component 95% summary is empirical, not an
orthogonal invariant-basis theorem. Its invariant-block eigenbranch audit finds
no $A_2\to A_1+A_1$ split candidate on the tested Rubik slices, so sorted
pair-gap responses are not promoted to $A_n$ adjacency evidence.

Paper XIII begins only after two single-system reports exist. Its primary object
is the alignment $(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}})$ consisting of a reference report, a
target report, and explicit sector and observable alignments. The comparison
specification $\Theta$ records normalization, metric, depth semantics, thresholds,
parameter synchronization, and aggregation. For fixed $\Theta$, the typed operator
$\operatorname{Compare}_{\Theta}:\mathsf{SOFReportAlign}\to\mathsf{AuditSignature}$
maps the alignment to the eight-dimensional comparison signature
$\Delta_{\mathrm{audit}}$, serialized inside a `.sofaudit` artifact. GridWorld,
SIR, Traffic, and Compiler IR are controlled-reference protocol validations;
latent and black-box World Model alignments remain potential deployment regimes,
not Paper XIII contributions or current evidence. The regimes describe increasing
uncertainty in constructing the alignment object, not increasingly powerful
algorithms. Three additional Compiler, Traffic, and GridWorld
before/after controls show that a nonzero alignment signature records change, not
failure: their raw signatures are retained while a declared transformation
contract produces a separate zero-residual evaluation.

Paper XIV remains a development horizon. Its intended question is how a
declared context interprets a nonzero comparison coordinate before any
candidate action or policy selection is considered. This horizon does not alter
the published Paper XIII comparison object: $\Delta_{\mathrm{audit}}$ records
difference, not defect, and Paper XIII itself supplies no intervention rule.

The common architecture behind Papers V--VII begins with sector projectors and
registered families, but it is not one untyped data ladder:

```text
(Q,Y)     -> operator support, routed composition, full words
(Q,X,H)   -> Lie support, commutators, Hall/Lie depth
```

Here `Y` is a registered operator family, while `X` and `H` specify a
registered Lie family and filtration. The shared problem is to determine what
information survives projection, composition, route summation, and
antisymmetrization. The theorem layers and promotion claims remain local to
their declared branches.

---

## 3. Two Interface Families

The following groupings indicate compatible input and output signatures. They
do not prescribe a reading order, build order, or theorem dependency.

### Route A: Spectral / Sector Geometry

```text
Paper I:   (rho,S,reducing blocks) -> block spectral census
Paper II:  (Q,H,{Q_i},rho(S))      -> registered sectors and direct transport
Paper IV:  (P,L_alpha)             -> fixed collision quotient
Paper VI:  (w,Q_T,H_T,gates)       -> linearized and pointwise certificates
```

These signatures overlap without identifying their claims. Paper I does not
produce the exact QT/HT joint resolution required by an operator application
of Paper IV. Paper II registers a numerical sectorization for its own direct
transport census. Paper IV redeclares the exact rational arrangement `P_9`
before using it. A Paper VI point supplies theorem-level input to Paper IV only
if the pair or arrangement is exact; passing numerical commutativity,
normality, projector, and chart gates supports a computational pointwise
comparison, not that exact promotion.

Rubik starting point:

```text
A_18 = (2/3) QT_all + (1/3) HT_all
```

Paper IV fixed-arrangement statement:

```text
The displayed rational nine-point arrangement has a six-class collision
quotient at alpha = 2/3. Its identification with the exact Rubik spectrum is
conditional on exact operator registration.
```

Paper VI compatibility boundary:

```text
If a moving normal spectral chart is certified, each point supplies a finite
arrangement P(w). Exact fixed-arrangement theorems require exact point data;
numerically registered points retain computational claim status.
```

This pointwise compatibility does not establish coherent labels, projector
continuation, a nonlinear atlas, or collision walls along a parameter path.

### Route B: Accessibility Theory

Compatible signatures:

```text
admissible sector fields
  +-- registered operators Y
  |     -> direct blocks R_1[Y]
  |     -> routed products C_d[Y]
  |     -> full words W_d[Y]
  |     -> D_route[Y] and D_word[Y]
  |
  +-- registered Lie family (X,H)
        -> R_1^Lie and R_2^Lie
        -> D_Lie in the declared filtration

each attempted promotion -> its own nondegeneracy, cancellation,
                             saturation, or comparison certificate
```

Paper III uses arbitrary declared transport maps and studies one routed
composition. Paper V uses a separately declared skew-Hermitian family and Lie
filtration. Paper VI registers pointwise typed shadows only after its spectral
gates. Paper VII takes an abstract composable matrix pair. None of these input
families is imported from another paper without being declared again.

Rubik starting point:

```text
The canonical five pairs are the first explicit graph/operator separation:
two-step support paths exist while all projected products vanish.
```

General static objects:

```text
operator branch: (Q,Y), R_1[Y], C_d[Y], W_d[Y], typed depths
Lie branch:      (Q,X,H), R_1^Lie, R_2^Lie, D_Lie
```

Paper V boundary:

```text
(G, chi, Lambda) -> D is false.
```

Binary support is insufficient, but there is no single replacement object.
Routed composition, full words, and Lie brackets retain different information.

Paper VI research target:

```text
on certified normal spectral charts:
  operator/word fields and Lie/Hall fields move separately
```

They are functions on a declared admissibility domain, not fixed invariants
attached once and for all to a single sectorization. Existing fragmentation
samples do not yet certify this target because normality and carrier alignment
must first be re-established.

Paper VII promotion boundary:

```text
image--kernel incidence: AB=0 with A!=0 and B!=0
fixed-rank codimension formulas
correct rectangular rank-protection conditions
separate graph->routed, routed->word, and low-order-Lie->depth questions
```

The incidence geometry is relevant to routed products. It does not by itself
prove a full-word or Lie-depth completion theorem. Any such conclusion would
require separately declared depth data, saturation, per-depth support, and
noncircular promotion hypotheses.

Compact interface synthesis:

```text
Paper II may supply direct-block data to a Paper III realization.
Paper III and Paper VII share the local image--kernel matrix interface.
Paper V fixes the typed distinctions used when formulating later audits.
Paper VI currently supplies pointwise registrations, not moving fields.
Every stronger promotion requires a local certificate in the receiving paper.
```

---

## 4. Layer Vocabulary

Use these layers consistently.

### Layer A: Spectral Language

Objects:

- representation space `V`,
- block decomposition,
- averaging operators,
- commutative averaging algebra,
- joint spectrum,
- spectral layers,
- joint eigenspace sectors,
- collision quotients.

Typical notation:

```text
A_18, QT_all, HT_all
P={(q_i,h_i)}
lambda_i(alpha)=alpha q_i + (1-alpha)h_i
```

Main question:

```text
What are the spectral sectors, and how do coarse layers arise from them?
```

Papers:

```text
Paper I, Paper IV
```

Paper II independently declares a registered spectral carrier before computing
direct transport. Paper VI independently declares a weighted spectral family
and applies commutativity and normality gates before any pointwise
registration.

### Layer B: Transport Language

Objects:

- sector projectors,
- generator-resolved transport,
- transport tensor `K`,
- noncommutative support,
- direct transport graph,
- hubs and block-preserving edges.

Typical notation:

```text
K_ij = max_g ||Q_i rho(g) Q_j||
Supp_nc
direct transport edges
```

Main question:

```text
Which resolved sectors exchange amplitude under one generator?
```

Papers:

```text
Paper II
```

Layer B is still Rubik-facing in Paper II, although its language can
later be abstracted.

### Layer C1: Graph-to-Operator Composition

Objects:

- direct blocks `Q_i rho(g) Q_j`,
- direct support graph,
- ordered projected products,
- image--kernel obstruction,
- graph-to-composition promotion criteria.

Main question:

```text
When does a Boolean support path survive as a nonzero projected product?
```

Paper:

```text
Paper III
```

This layer is representation-operator composition. It does not identify
support paths with word accessibility and does not use logarithms or Lie
brackets.

### Layer C2: Static Lie-Accessibility Language

Objects:

- Lie generators,
- Lie filtration,
- projected generator blocks,
- `R_1^Lie` support,
- `R_2^Lie` projected commutator survival,
- projected Hall coefficient data,
- typed Lie-depth matrix `D_Lie`,
- accessibility signature `Sig`.

Typical notation:

```text
X_g = log rho(g)
W(i,g,j)=Q_i X_g Q_j
R_1^Lie(i,j;g) = 1 iff Q_i X_g Q_j != 0
R_2^Lie(i,j;g,h) = 1 iff Q_i [X_g,X_h] Q_j != 0
D_Lie = first nonzero depth in the declared Hall/Lie filtration
cutoff census=(A_0,A_1,A_2,A_unreached)
```

The logarithm branch, skew-Hermitian registration, normalization, filtration,
threshold, and cutoff are part of the object. Associative products of the
same `X_g` belong to the separate operator/word branch.

Main question:

```text
What determines the first depth at which sector-to-sector accessibility appears?
```

Papers:

```text
Paper V
```

Paper III and Paper V share a sector-projector interface but declare different
operator families. Paper III studies represented transport composition;
Paper V studies skew-Hermitian direct support, words, commutators, and a
declared Lie filtration. Neither object's support census is imported into the
other.

### Layer D: Deformation / Wall Language

Objects:

- local differential domain `M_>0=(0,infinity)^m`, with `M_+` reserved for nonnegative boundary probes,
- commutativity locus `Sigma_comm`,
- commuting-normal locus `Sigma_normal`,
- certified normal spectral charts `Sigma_spec`,
- moving joint arrangement `P(w)`,
- spectral walls `Sigma_L` and `Sigma_field`,
- typed jets `J_op`, `J_comp`, `J_word`, and `J_Lie`,
- typed support, composition, word, commutator, and depth walls.

Typical notation:

```text
Q_T(w), H_T(w), A(w)
C_comm(w)=[Q_T(w),H_T(w)]
Sigma_comm={w:[Q_T(w),H_T(w)]=0}
Sigma_spec subset Sigma_normal subset Sigma_comm
J_acc=(J_op,J_comp,J_word,J_Lie) only as an explicitly declared package
```

Main question:

```text
Which linearized directions preserve commutativity and normality, which samples
pass the spectral gates, and what remains necessary for a moving-field theory?
```

Paper:

```text
Paper VI
```

---

## 5. Paper IV: Fixed Collision Geometry

Paper IV is organized around four claim layers:

```text
general fixed-arrangement theorem
-> exact census of an explicitly declared rational P_9
-> computational Rubik registration
-> conditional exact Rubik interpretation
```

The finite-point object is:

```text
P={(q_i,h_i)} subset R^2
L_alpha(q,h)=alpha q+(1-alpha)h
A(alpha)=alpha Q+(1-alpha)H
```

The layer changes come from the collision quotient induced by `L_alpha`:

```text
fixed point set, changing projection direction.
```

The general theory is independent of the Rubik registration. The operator
realization enters only after the exact finite-point census.

Exact facts for the declared arrangement `P_9`:

```text
36 sector pairs = 2 parallel + 10 interior + 15 endpoint + 9 exterior
interior collision values = {2/7, 2/5, 1/2, 2/3, 4/5}
alpha = 2/3 is the unique maximal interior collapse
S5-S6-S7 collapse to V_5/9
S8-S9 collapse to V_1/3
```

Rubik claim boundary:

```text
complex128 diagnostics register nine QT/HT clusters near P_9
numerical table agreement does not prove exact rational joint spectral data
if exact registration holds, the six A18 layers are the alpha=2/3 quotient
```

---

## 6. Paper V: Local Support and Commutator Accessibility

Paper V studies a fixed sectorized system:

```text
(V, {Q_i}, {X_g})
```

It does not move the generator set. It asks which low-order support,
composition, word, commutator, and Lie-depth data remain distinct on fixed
sectors.

Stable theorem layer:

```text
R_1^Lie, routed X-products, X-word support, R_2^Lie, and D_Lie are distinct.
Identical generator-indexed R_1^Lie can yield different R_2^Lie and depth.
The pair (R_1^Lie,R_2^Lie) gives a neutral four-class low-order partition.
Centered scalar hypotheses can certify a local bracket-emergent channel.
```

The retired Type I--IV labels are not the primary Paper V taxonomy. The live
mechanism names are:

| Mechanism | Meaning |
|-----------|---------|
| direct/bracket status | the four Boolean classes determined by `(R_1^Lie,R_2^Lie)` |
| cancellation | nonzero projected terms or words cancel in a commutator |
| incidence | nonzero factors compose to zero by `im(B) subset ker(A)` |

This mechanism taxonomy is distinct from the candidate typed moving loci in
Paper VI's research program; no Paper VI moduli-wall hierarchy is currently a
theorem.

Claim-status discipline:

```text
The exact same-support counterexample and scalar bracket-emergence proposition
are the theorem layer. Matrix emergence, full represented/dense
low-order-Lie-to-`D_Lie` completion, and moving walls remain research questions.
```

The compatible Paper VI interface begins only after a normal spectral chart is
certified. Paper V's low-order/depth question is static; coherent motion of
the corresponding typed fields remains part of Paper VI's research program.

---

## 7. Paper VI: Linearized Geometry and Typed Deformation Program

Paper VI v2 separates a certified linearized geometry layer from a conditional
moving-field research program.

### Admissibility Domain

For a declared moving spectral family, the required gates are

```text
Sigma_spec subseteq Sigma_normal subseteq Sigma_comm subseteq M
  -> {Q_i(w)}.
```

`Sigma_comm` records pairwise commutativity. `Sigma_normal` additionally
requires normality of each spectral operator. `Sigma_spec` is a chart on which
joint spectral clusters have coherent labels, constant ranks, and enough
separation or contour data to define projector fields with the claimed
regularity. Moving accessibility fields are defined only after these gates.

The corrected full real/imaginary Jacobian recomputation at the canonical
point gives

```text
commutator derivative:                     rank = 11, nullity = 7
commutator + QT/HT normality derivative:   rank = 14, nullity = 4
commutator gap:   sigma_11 = 2.003084e-1, sigma_12 = 2.415461e-15
combined gap:     sigma_14 = 2.003084e-1, sigma_15 = 2.238468e-15
```

The first line is a linearized commutativity-kernel certificate at a
numerically registered near-zero point, not a Zariski-tangent or
seven-dimensional smooth-manifold theorem. The second kernel is spanned
numerically by uniform HT gauge motion and three inverse-pair-symmetric QT-axis
directions; uniform QT motion is the sum of the three QT-axis directions.
Both uniform QT and uniform HT scaling are exact class-scaling gauge families;
one point on each QT-axis parameterization passes the numerical
commutativity/normality gates.
This does not prove interval-wide commutation, constant rank, or a nonlinear
atlas theorem.

### Normality-Gated Pointwise Registration

At the canonical point and at QT-axis weight `1.1`, the active computational
records are

```text
canonical: sectors=9,  R1^op=438,  R1^Lie=408
QT axis 0: sectors=15, R1^op=1006, R1^Lie=832
QT axis 1: sectors=15, R1^op=1006, R1^Lie=832
QT axis 2: sectors=15, R1^op=1006, R1^Lie=832
```

All four records pass commutativity, Hermiticity/normality, orthogonality,
idempotence, completeness, and projector checks at the declared complex128
tolerances; the maximum reported projector residual is `2.390e-14`.
`R1^Lie` uses a declared finite-order principal logarithm and is
branch-sensitive. These are pointwise registrations, not evidence of coherent
projector continuation along the connecting parameter intervals.

### Withdrawn Promotion

The first-version fragmentation samples generally remain in `Sigma_comm`
numerically but fail normality. In addition, the manuscript's historical
`R_1` uses registered `X_g`, while the fragmentation scripts count raw
`rho(g)` blocks. Therefore the reported `9 -> 24...35` sector fragmentation
and associated support jumps are not active certificates for
`Sigma_spec`, moving Lie support, word depth, or a common accessibility wall.

The old Wall Origin Principle, single `R1/R2/D` hierarchy, and `438 -> 6334`
support claim are retired from current authority.

### Typed Deformation Target

On a certified chart, future Paper VI work must carry separate trajectories:

```text
operator branch: R_1[Y](w), C_d[Y](w), W_d[Y](w), typed word depths
Lie branch:      R_1^Lie(w), R_2^Lie(w), D_Lie(w)
```

Corresponding jets and walls must also be typed. `J_acc` and `Sigma_access`
may be used only as explicit packages of named components. No active Paper VI
ordered-word, routed-depth, `R2^Lie`, or `D_Lie` moving certificate exists,
and no inclusion hierarchy between the typed wall loci is assumed.

---

## 8. Paper VII: Incidence Geometry and Promotion Limits

Paper VII is a self-contained static paper on fixed sectorizations. It studies
the image--kernel incidence condition for one routed projected product:

```text
Z={(A,B): AB=0},
Z^x=Z intersect {A!=0, B!=0}.
```

The closed object is `Z`; `Z^x` is constructible. On
`rank(A)=r` and `(rank(A),rank(B))=(r,s)` strata, the theorem layer is

```text
dim I_r = r(m+n-r)+p(n-r)
codim I_r = (m-r)(n-r)+pr
dim I_(r,s) = r(m+n-r)+s(n-r+p-s)
relative codim inside the rank-(r,s) pair stratum = rs
```

This incidence geometry belongs first to routed projected composition. It is
not automatically a full-word cancellation theorem or a Lie-depth
obstruction theorem.

### Rank Protection

For rectangular composable blocks `A:m x n` and `B:n x p`, the elementary
rank-protection conditions are:

```text
A has full column rank n  -> AB=0 implies B=0;
B has full row rank n     -> AB=0 implies A=0.
```

The v2 implementation uses the middle dimension: left protection is
`rank(A)=n` and right protection is `rank(B)=n`. It still evaluates every
product and asserts that protected nonzero factors do not produce a numerical
zero.

### Promotion Boundary

The active questions are separate:

1. When does a Boolean path promote to a nonzero routed product?
2. When do routed terms survive their sum as a full word?
3. When do low-order Lie supports constrain or determine `D_Lie`?

The former Generic Completion Principle is withdrawn. The finite v2 atlas
stores and compares complete `R1^Lie`, `R2^Lie`, `D_Lie`, per-depth support,
cumulative support, and saturation records. Agreement in four finite mask
families is a computational observation, not a low-order-to-depth theorem.
Paper VII proves local incidence geometry and rank protection; all stronger
promotions remain branch-specific research questions.

---

## 9. Vocabulary Policy

### Spectral Vocabulary

Prefer:

- joint eigenspace sector,
- QT/HT joint-spectral sector,
- sector of the QT/HT algebra,
- collision quotient,
- joint spectral point,
- affine branch arrangement,
- collision graph.

Use with care:

- primitive sector.

Use `registered QT/HT cluster` for the numerical realization. Reserve `joint
eigenspace sector` and `primitive idempotent of C[Q,H]` for an exact commuting
normal setting with certified joint projectors. When writing for
association-scheme readers, compare with Bose--Mesner / coherent-configuration
language when useful, but do not identify the object with a quotient algebra
unless that equivalence has been derived.

### Transport Vocabulary

Prefer:

- transport tensor,
- direct transport edge,
- generator-resolved transport,
- noncommutative support,
- block-preserving transport,
- transport hub.

Avoid turning transport into accessibility. One-step transport `K` is not the
same object as Lie depth or composition depth.

### Accessibility Vocabulary

Prefer:

- operator direct support `R_1[Y]`,
- routed projected composition `C_d[Y]`,
- full-word support `W_d[Y]`,
- word depth `D_word[Y]`,
- Lie direct support `R_1^Lie`,
- projected commutator support `R_2^Lie`,
- Hall/Lie depth `D_Lie`,
- projected Hall coefficient data,
- typed accessibility signature,
- typed accessibility jet,
- typed accessibility wall.

Use **graph-only two-step pair** for the five canonical Rubik paths and
**Image--Kernel Criterion** for the matrix obstruction theorem. Revision
history is kept in `HISTORY.md`.

Historical Type I--IV labels are not active cross-paper vocabulary. Use
`cancellation` and `image--kernel incidence`, and state whether the affected
object is a routed product, full word, commutator, or depth certificate.

---

## 10. Rubik vs General Theory

### Rubik-Specific or Rubik-Facing

These belong primarily to Papers I--III and CCS:

- 228-dimensional cubie representation,
- standard 18 face-turn generators,
- six canonical `A_18` layers,
- nine QT/HT sectors in the Rubik system,
- `V_{5/9}` giant layer,
- S6 hub,
- 10 direct transport edges,
- 5 graph-only two-step obstruction pairs,
- EP `M_2` transport mechanism.

These are not defects. They are the concrete laboratory.

### Generalizable Objects

These are the general program objects:

- finite commutative averaging algebras,
- joint spectral point sets,
- affine branch arrangements,
- collision graphs and collision quotients,
- sectorized observable frameworks,
- registered operator and Lie/Hall families,
- direct operator and Lie supports,
- routed projected products and full ordered words,
- projected commutator support,
- projected Hall coefficient data,
- typed route, word, and Lie-depth matrices,
- incidence varieties,
- rank-protected bridge products,
- branch-specific promotion principles,
- generator-set moduli spaces,
- commutativity loci,
- spectral walls and typed accessibility-wall candidates.

### Boundary Rule

When a claim uses Rubik numerics, state it as Rubik-facing. When a claim uses
only joint-spectrum, projected-block, Hall-path, or moduli data, state the
abstract object explicitly.

```text
Rubik provides a structured example motivating the minimal-data problem for
sectorized observable frameworks.
```

---

## 11. Claim Boundaries

### Paper IV Boundary

Paper IV is a fixed-arrangement paper:

```text
finite joint spectrum P
affine branches
visible collisions
collision quotients
Rubik as motivating example
```

Generator-set deformation is not part of Paper IV; it belongs to Paper VI.

### Paper V Boundary

Paper V is a static local support/commutator paper:

```text
Lie direct support R_1^Lie
routed X-products and X-word support
commutator support R_2^Lie
cutoff-relative versus exact D_Lie
cancellation and incidence mechanisms
```

Historical Type I--IV labels are retired from the primary classification.
Cancellation and incidence are static mechanisms, not Paper VI wall labels.

### Paper VI Boundary

Paper VI v2 is organized around admissibility gates, corrected linearized
commutativity/normality certificates, pointwise normality-gated registrations,
and a conditional typed moving-field program.

The algebraic characterization of `Sigma_comm` remains open:

```text
global ideal
component structure
minimal equations
full algebraic classification
```

The paper uses computational tangent-local models. It does not claim a smooth
seven-dimensional commutativity manifold, a four-dimensional nonlinear
commutative-normal manifold, or a complete global algebraic classification of
`Sigma_comm`.

The active pointwise sector-count records (`9` versus `15`) pass the normality
and projector gates,
but no coherent projector continuation between those points is claimed. The
older `9 -> 24...35` fragmentation samples are archived provenance: they fail
normality and use a raw-operator support family that is not the manuscript's
registered Lie family.

### Paper VII Boundary

Paper VII v2 is fixed around:

```text
closed zero-product locus and constructible nonzero-factor locus
fixed-rank and fixed-double-rank incidence strata
correct rectangular rank protection
explicit graph/route/word/commutator/Lie promotion boundaries
```

The current claim-status split is:

```text
incidence and rank-protection theorem spine: proved
corrected Rubik routed census: computational observation
full-array finite Lie atlas: computational observation
ambient-to-represented and low-order-to-depth promotion: open
```

### Relation to Papers I--III

Papers I--III are independent Rubik-centered papers. Later structure can be
read back into them only as bounded discussion-level context:

- Paper I: the six registered layers admit a conditional collision-quotient
  interpretation after an exact QT/HT registration is supplied.
- Paper II: its registered QT/HT clusters can be matched to the independently
  declared nine-point arrangement; this does not promote the numerical
  clusters to an exact joint spectrum.
- Paper III: support-graph reachability overapproximates projected matrix
  composition; graph-to-composition promotion requires nondegeneracy data.
- CCS: records Paper I--II reproducibility data and the historical combined
  release; revised Paper III carries its own matrix certificate.

---

## 12. One-Sentence Program Summary

The RIME program starts from the Rubik representation as a finite reproducible
laboratory, extracts spectral and accessibility geometry, studies how those
geometries deform across generator-set moduli spaces, and develops typed
certificates for when support information survives projection, composition,
summation, and Lie antisymmetrization.
