# RIME Program Map

**Date**: 2026-07-16
**Status**: public narrative architecture map for Papers I--XII, with a
Paper XIII--XIV horizon.

This document summarizes the program-level organization. It is not a proof
document and does not replace the manuscripts. Its purpose is to make the
language, layers, claim status, and Rubik/general-theory boundary visible to
readers of the paper series.

For the guiding philosophy behind the Rubik-to-general-theory transition, see
[PROGRAM_PHILOSOPHY.md](PROGRAM_PHILOSOPHY.md).

For the public post-Paper VII SOF arc, see [SOF_OBJECTS.md](SOF_OBJECTS.md),
[SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md), and
[SOF_REGISTRY.md](SOF_REGISTRY.md).

---

## 1. Core Architecture

The program now has three stable phases:

```text
Papers I--III: Rubik-centered static trilogy
Paper IV:      projection geometry of spectral layers
Paper V:       static repair calculus for accessibility on fixed sectors
Paper VI:      deformation geometry of spectral and accessibility walls
Paper VII:     generic completeness away from high-codimension incidence
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
Genericity determines why the behavior is stable.
```

The governing distinction is:

```text
Paper IV: fixed arrangement P, varying projection L_alpha
Paper VI: moving arrangement P(w), defined on normal spectral charts
          Sigma_spec subset Sigma_comm
```

Important distinction:

```text
Paper V Type I--IV = static length-2 mechanism taxonomy.
Paper VI walls     = moduli loci where R1(w), R2(w), or D(w) changes.
```

Both use the words `R_1` and `R_2`, but they answer different questions.

---

## 2. Public Paper Arc

| Paper | Role | Core object | Main question |
|-------|------|-------------|---------------|
| I | Spectral formation | `A_18` | Why does the canonical Rubik spectrum have six rational layers? |
| II | Sector transport | QT/HT joint-spectral sectors and `K` | Why does the resolved transport graph have its topology? |
| III | Accessibility separation | Lie vs composition accessibility | Why can composition see channels Lie generation misses? |
| IV | Collision geometry | finite joint spectrum `P={(q_i,h_i)}` | Why are the six layers a collision quotient? |
| V | Static repair calculus | length-2 witnesses, `R_1`, `R_2`, weighted Hall paths | What repairs binary support after path-commutator cancellation? |
| VI | Deformation theory | generator-set moduli space, `Sigma_comm`, accessibility jets | How do spectral phases and accessibility data bifurcate under generator variation? |
| VII | Completion theory | incidence variety, rank-protected bridges, generic completion | Why is accessibility generically stable? |
| VIII | SOF object theory | finite SOF data, strict morphisms, naturality | What is the sectorized observable object? |
| IX | Observable dynamics | SOF deformations, trajectories, wall pullbacks, rate separation | How do SOF observables evolve under deformation? |
| X | Observable pipeline | source systems, sectorization origins, registry evidence | Why do different species share one observable pipeline? |

Short form:

```text
Paper IV:  How spectral layers are geometrically formed.
Paper V:   How accessibility is computed on fixed sectors.
Paper VI:  How sectors and observables deform.
Paper VII: Why the geometry is generically complete.
Paper VIII: What the SOF object is.
Paper IX:  How SOF observables evolve under deformation.
Paper X:   Why cross-species diagnostics share one observable pipeline.
```

Representation-to-accessibility route:

```text
Finite Representation
  -> sector decomposition and projected block operators
  -> Projection / Collision Geometry       -> Paper IV
  -> Transport / Accessibility             -> Paper V
  -> Generator deformation / Wall hierarchy -> Paper VI
  -> Generic completion                    -> Paper VII
  -> SOF objects and morphisms             -> Paper VIII
  -> SOF observable dynamics               -> Paper IX
  -> Universal observable pipeline         -> Paper X
```

This map uses only the stable interface: finite sectors, projected blocks,
observable shadows, and wall discriminants.

Four-Why form:

```text
Paper IV:  Why do spectral layers appear as projections?
Paper V:   How is accessibility computed once sectors exist?
Paper VI:  Why do sectors move and walls appear?
Paper VII: Why is the resulting geometry generically complete?
Paper VIII: What is the sectorized observable object?
Paper IX:  How do observable shadows evolve?
Paper X:   Which diagnostics persist across species?
```

Papers I--III are the Rubik laboratory. Papers IV--VII extract the general
theory: projection geometry, weighted Hall accessibility, deformation
geometry, and generic completion away from incidence.
Papers VIII--X then package the sectorized observable object, deformation
dynamics, and cross-species observable pipeline.

Papers IV--VII close the first post-trilogy accessibility cycle:

```text
Paper IV    fixed spectral geometry
Paper V     accessibility calculus
Paper VI    accessibility deformation
Paper VII   generic completion
```

The next cycle is SOF-oriented:

```text
Paper VIII  SOF object layer, strict morphisms, and naturality
Paper IX    SOF deformation geometry and wall dynamics
Paper X     Universal Observable Pipeline and registry evidence
Paper XI    Observable Wall Taxonomy
Paper XII   SOF Diagnostic Protocol and SOF Report Specification
Paper XIII  SOF Report Alignment and induced comparison signatures
Paper XIV   SOF Action Semantics and candidate intervention sets
```

Paper VIII asks what the object is and proves that the RIME observables are
natural constructions on strict SOF data. Paper IX asks how SOF objects deform
and why different deformation spaces generate different wall geometries. Paper
X asks why broad external species can enter one observable pipeline. Paper XI
classifies observable wall records, signatures, spectra, and taxonomy while
keeping ADE as a smooth-branch local model only. Paper XII asks how SOF
is deployed in practice: diagnostics become SOF Reports, with automatic sector
audits and application sections organized as AI Systems, Dynamic Systems, and
Industrial Diagnostics. Paper XII separates white-box reports, whose internal
finite realization is visible, from API-level Behavioral SOF Reports, whose
probe sectors and observables come from externally visible interfaces. Its Black-Box SOF
Diagnostic Principle states that a white-box realization is sufficient but not
necessary: compatible sectors or stable probe sectors plus measurable outputs
can support a claim-status-aware report without internal access. This is why
SOF is an observable framework rather than a weight framework. Stable slogan:
No weights required. Only observables.

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

Paper XIV defines context-indexed signature semantics
$\operatorname{Sem}_{\Gamma,i}:\Delta_i\to\mathcal I_i$. A nonzero coordinate
records difference, not defect; legitimate-transformation controls map active
coordinates to `licensed_change`. The candidate Action Set is the derived union
of coordinate-level consequences under
$\operatorname{GenerateActions}_{\Gamma}:\mathsf{AuditSignature}\to
\mathsf{ActionSet}$. Repair, observation, containment, and validation candidates
follow from these interpretations. A downstream policy
$\pi:\mathsf{ActionSet}\times\mathsf{PolicyContext}\to
\mathsf{SelectedActionPlan}$ may select from that set, but policy selection is
not the Paper XIV mathematical contribution. The legacy `.sofdecision` rule
engine remains a compatibility control.

The common observable architecture behind Papers V--VII is the
SOF data package

$$
(V,\{Q_i\},\mathcal X).
$$

Here $\{Q_i\}$ is a finite projector decomposition and $\mathcal X$ is an
observable family. The observables $R_1$, $R_2$, $D$, and
$\mathcal J_{\mathrm{acc}}$ are derived fields of this sectorized block
geometry. This is program language, not an additional theorem claim: the
current theorem layers remain the fixed-system repair calculus of Paper V, the
local commutativity-wall/accessibility-wall geometry of Paper VI, and the
generic nonincidence completion program of Paper VII.

---

## 3. Two Main Routes

### Route A: Spectral / Sector Geometry

```text
Paper I
  -> Paper II
  -> Paper IV
  -> Paper VI, Part I
```

Conceptual chain:

```text
representation
  -> averaging algebra
  -> joint spectrum
  -> sector decomposition
  -> affine branch arrangement
  -> collision quotient
  -> deformation of the arrangement
```

Rubik starting point:

```text
A_18 = (2/3) QT_all + (1/3) HT_all
```

Paper IV statement:

```text
The canonical six-layer spectrum is the collision quotient of the nine-point
QT/HT joint spectrum at alpha = 2/3.
```

Paper VI extension:

```text
Generator-set perturbation changes the arrangement itself:
P fixed in Paper IV becomes P(w) in Paper VI.
```

Thus:

```text
Collision Geometry studies fixed arrangements with varying projections.
Generator-Set Deformation studies varying arrangements together with their
induced collision quotients.
```

### Route B: Accessibility Theory

```text
Paper III
  -> Paper V
  -> Paper VI, Part III
  -> Paper VII
```

Conceptual chain:

```text
generator
  -> Lie accessibility
  -> composition accessibility
  -> R1 support
  -> length-2 witnesses
  -> R2 projected commutator survival
  -> weighted Hall path algebra
  -> D first-depth data
  -> accessibility walls
  -> incidence varieties
  -> generic completion
```

Rubik starting point:

```text
T7 is the first explicit separation example:
composition-generated accessibility exceeds Lie-generated accessibility.
```

General static object:

```text
sector projectors Q_i
skew generators X_g
edge weights W(i,g,j)=Q_i X_g Q_j
projected Hall coefficients
first depth matrix D
```

Paper V correction:

```text
(G, chi, Lambda) -> D is false.
```

Binary support is insufficient. The live static object is a weighted Hall path
algebra, with `R_2` as the first repair layer.

Paper VI deformation:

```text
R_1(w), R_2(w), and D(w) are discrete shadows of smooth matrix fields on
normal spectral charts Sigma_spec subset Sigma_comm.
```

They are functions on a deformation domain, not fixed invariants attached once
and for all to a single sectorization.

Paper VII completion:

```text
Type IV = incidence variety I={(A,B): AB=0, A!=0, B!=0}
codim I_r = (m-r)(n-r)+pr
rank-protected bridges survive
generic nonincidence supports (R_1,R_2)->D completion
```

The Generic Completion Principle is:

```text
Outside a high-codimension incidence variety, rank-protected bridge products
generically survive, so the observable pair (R_1,R_2) determines the
first-depth invariant D under the stated richness hypotheses.
```

Compact synthesis:

```text
Papers IV--VI describe the geometry.
Paper VII explains why that geometry is generically complete.
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

Paper II uses Layer A as input. Paper VI deforms Layer A by moving the
generator weights.

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

Layer B is still Rubik-facing in the current trilogy, although its language can
later be abstracted.

### Layer C: Static Accessibility Language

Objects:

- Lie generators,
- Lie filtration,
- word/composition filtration,
- projected generator blocks,
- `R_1` support,
- `R_2` projected commutator survival,
- weighted Hall path algebra,
- first depth matrix `D`,
- accessibility signature `Sig`.

Typical notation:

```text
X_g = log rho(g)
W(i,g,j)=Q_i X_g Q_j
R_1(i,j;g) = 1 iff Q_i X_g Q_j != 0
R_2(i,j;g,h) = 1 iff Q_i [X_g,X_h] Q_j != 0
D = first nonzero Lie-depth matrix
Sig=(A_0,A_1,A_2,A_inf)
```

Main question:

```text
What determines the first depth at which sector-to-sector accessibility appears?
```

Papers:

```text
Paper III, Paper V
```

Paper III is the separation example. Paper V is the static length-2 repair
calculus and minimal-data program.

### Layer D: Deformation / Wall Language

Objects:

- generator-set moduli space `M=[0,1]^m`,
- commutativity locus `Sigma_comm`,
- moving joint arrangement `P(w)`,
- spectral walls `Sigma_L` and `Sigma_field`,
- accessibility jet `J_acc(w)`,
- accessibility wall `Sigma_access`,
- residual accessibility walls `Sigma_R1`, `Sigma_R2^circ`, `Sigma_D^circ`.

Typical notation:

```text
Q_T(w), H_T(w), A(w)
C_comm(w)=[Q_T(w),H_T(w)]
Sigma_comm={w:[Q_T(w),H_T(w)]=0}
J_acc(w)=(J_block,J_comm,J_depth)
```

Main question:

```text
How do spectral layers and accessibility observables bifurcate when the
generator set varies?
```

Paper:

```text
Paper VI
```

---

## 5. Paper IV: Fixed Collision Geometry

Paper IV is closed around one central theorem:

```text
six Rubik spectral layers = collision quotient of a nine-point QT/HT joint
spectrum at alpha = 2/3.
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

The Rubik system provides the motivating example, then the paper immediately
returns to the general finite-point setting.

Important Rubik facts:

```text
36 sector pairs = 2 parallel + 10 interior + 15 endpoint + 9 exterior
interior collision values = {2/7, 2/5, 1/2, 2/3, 4/5}
alpha = 2/3 is the unique maximal interior collapse
S5-S6-S7 collapse to V_5/9
S8-S9 collapse to V_1/3
```

Program-level meaning:

```text
The old question "why these six layers?" is answered:
because the nine-point joint spectrum has its maximal interior collision at
alpha = 2/3.
```

---

## 6. Paper V: Static Repair Calculus

Paper V studies a fixed sectorized system:

```text
(V, {Q_i}, {X_g})
```

It does not move the generator set. It asks what information is needed to
compute accessibility on the fixed sectors.

Stable core:

```text
R_1 is insufficient.
R_2 is the first repair layer.
Weighted Hall path algebra is the right object.
Length-2 witnesses admit a local obstruction calculus.
```

The Type I--IV names are a mechanism taxonomy:

| Mechanism | Meaning |
|-----------|---------|
| Type I | singleton-color degeneracy |
| Type II | projected commutator survives |
| Type III | cancellation mechanism: signed products cancel |
| Type IV | incidence mechanism: image-kernel coincidence makes products vanish |

This mechanism taxonomy is distinct from the Paper VI moduli-wall hierarchy.

Claim-status discipline:

```text
The local length-2 calculus is the theorem layer.
Full represented/dense (R_1,R_2)->D completeness remains a program-level
conjecture, not a proved theorem.
```

Paper VI does not contradict this. Paper VI gives local stratification on
normal spectral charts inside `Sigma_comm`; Paper V's completeness question is
static/global.

---

## 7. Paper VI: Commutativity Walls and Spectral Phase Transitions

Paper VI opens the deformation-theory line of the program.

### Part I: Global Stratification

The moduli space is:

```text
M=[0,1]^m
```

For Rubik, `m=18`. Define weighted averages:

```text
Q_T(w), H_T(w), A(w)
```

The commutativity locus is the primary object:

```text
Sigma_comm = {w : [Q_T(w),H_T(w)] = 0}.
```

Inside normal spectral charts `Sigma_spec subset Sigma_comm`, the QT/HT joint
arrangement, orthogonal joint-sector projectors, collision quotient, and
accessibility jet are defined. Outside `Sigma_comm`, the collision quotient is
undefined; inside `Sigma_comm` but outside `Sigma_spec`, the present
orthogonal-projector formalism is not used. The global `A(w)`-spectrum
continues to vary on the ambient weight space.

Spectral wall hierarchy:

```text
Sigma_field subset Sigma_L subset Sigma_spec subset Sigma_comm
```

Interpretation:

| Layer | Meaning |
|-------|---------|
| `Sigma_comm` | outer algebraic commutativity wall |
| `Sigma_spec` | normal spectral chart where joint sectors/projectors are used |
| `Sigma_L` | once defined, whether the collision quotient changes layer count |
| `Sigma_field` | once the quotient exists, whether the number field changes |

`Sigma_comm` is the outer commutativity wall, not merely an empirical sparse
set. Earlier sparse 2D scans are transverse-slice evidence; the current local
model treats `Sigma_comm` as a smooth commutativity wall at the canonical
point.

### Part II: Local Geometry at the Canonical Point

Theorem 1:

```text
dim T_1 Sigma_comm = 7
codim = 11
kernel split = 1(HT) + 6(QT)
```

The computational tangent model verifies local rank stability and finds no
hidden nonlinear kernel emergence in the tested regime.

Theorem 2:

```text
w=1 is maximally coarse.
Uniform HT is a gauge direction.
QT kernel directions fragment the sector decomposition immediately.
Fragmentation causes R1 jumps.
```

Wall Origin Principle:

```text
Accessibility walls are not caused by bending of Sigma_comm.
They are caused by combinatorial instability of the sector decomposition under
smooth first-order motion of joint spectral points.
```

### Part III: Accessibility Theorem Layer

On normal spectral charts `Sigma_spec subset Sigma_comm`, define:

```text
sectorized system Q_i(w)
block maps Q_i(w) rho(g) Q_j(w)
R_1(w): support graph
R_2(w): repair graph
D(w): minimal accessibility depth
```

The bridge object is the accessibility jet:

```text
J_acc(w)=(J_block,J_comm,J_depth)
```

with:

```text
J_block = generator-support response
J_comm  = Lie-defect / projected-commutator tensor
J_depth = composition-propagation / Hall projection kernel
```

The discrete observables are rank/support/first-depth projections of smooth
fields:

```text
R_1, R_2, D are functions on Sigma_spec.
They are not continuous invariants; they are discrete shadows.
```

Accessibility walls:

```text
Sigma_access = locus where the rank/support structure of J_acc is not locally
constant.
```

Residual wall hierarchy:

```text
Sigma_R1
Sigma_R2^circ
Sigma_D^circ
```

Cumulative hierarchy:

```text
hat(Sigma_R1) subset hat(Sigma_R2) subset hat(Sigma_D)
= Sigma_access subset Sigma_spec subset Sigma_comm.
```

Spectral walls and accessibility walls are different:

```text
Sigma_L and Sigma_field describe movement/arithmetic of the joint arrangement.
Sigma_access describes jumps in R_1(w), R_2(w), or D(w).
```

---

## 8. Paper VII: Generic Accessibility Completion

Paper VII closes the static completion line opened by Paper V.

Main question:

```text
Does (R_1,R_2) determine D?
```

Claim-status answer:

```text
unconditionally: no;
generically: conjecturally yes;
hard boundary: Type IV incidence AB=0.
```

The algebraic object is the Type IV incidence variety:

```text
I={(A,B): AB=0, A!=0, B!=0}.
```

On the fixed-rank stratum `rank(A)=r`,

```text
codim I_r = (m-r)(n-r)+pr.
```

For square block scale, the dominant incidence codimension is asymptotic to
`3d^2/4`. Thus Type IV is not merely a counterexample; it is a
high-codimension algebraic degeneracy.

The theorem roadmap is:

```text
Corollary: rank-protected bridges survive.
Proposition: Type IV incidence is nongeneric.
Conjecture: away from incidence and under richness hypotheses, (R_1,R_2)
            completes the first-depth invariant D.
```

Generic Completion Principle:

```text
Outside a high-codimension incidence variety, rank-protected bridge products
generically survive, so the observable pair (R_1,R_2) determines the
first-depth invariant D.
```

Rubik interpretation:

```text
Rubik is not a generic point of the sectorized-observable framework space.
It is a stable carrier of high-codimension algebraic structure.
```

This is why Paper VII does not patch Paper V. It answers the question Paper V
left open: whether the `R_2` repair layer is generically complete.

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

When writing for association-scheme readers, explain that the sectors are
joint eigenspace sectors of a finite commutative algebra. Compare with
Bose--Mesner / coherent-configuration language when useful, but do not identify
the object with a quotient algebra unless that equivalence has been derived.

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

- Lie-generated accessibility,
- composition-generated accessibility,
- projected generator support,
- projected commutator survival,
- weighted Hall path algebra,
- first depth,
- accessibility signature,
- accessibility jet,
- accessibility wall.

Use T7 as a named Rubik/trilogy phenomenon, not as the general name for all
post-trilogy accessibility behavior.

Terminology note:

```text
Type III wall
Type IV wall
```

should be used only when the surrounding text makes clear that these are Paper
V mechanism examples. In Paper VI, the preferred language is:

```text
cancellation mechanism
incidence mechanism
mechanism-level wall-crossing support
```

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
- 5 T7 morphisms,
- EP `M_2` transport mechanism.

These are not defects. They are the concrete laboratory.

### Generalizable Objects

These are the post-trilogy objects:

- finite commutative averaging algebras,
- joint spectral point sets,
- affine branch arrangements,
- collision graphs and collision quotients,
- sectorized observable frameworks,
- projected generator weights,
- `R_1` support,
- `R_2` commutator survival,
- weighted Hall path algebra,
- accessibility depth matrix,
- incidence varieties,
- rank-protected bridge products,
- generic completion principles,
- generator-set moduli spaces,
- commutativity loci,
- spectral and accessibility walls.

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

Paper V is a static accessibility-repair paper:

```text
R_1 failure
R_2 repair
length-2 witness taxonomy
cancellation and incidence exceptional loci
weighted Hall path algebra
```

Paper V's Type I--IV taxonomy is a local mechanism classification. It is not
the Paper VI moduli-wall hierarchy.

### Paper VI Boundary

Paper VI is organized as:

```text
Part I:  global stratification on generator-set moduli
Part II: local geometry of Sigma_comm at the canonical point
Part III: accessibility theorem layer via J_acc
```

The algebraic characterization of `Sigma_comm` remains open:

```text
global ideal
component structure
minimal equations
full algebraic classification
```

The paper uses a computational tangent-local model and observed stratification.
It does not claim a complete global algebraic classification of
`Sigma_comm`.

### Paper VII Boundary

Paper VII is organized around:

```text
Type IV incidence variety
rank-protected bridge survival
generic nonincidence
completion away from incidence
Rubik as structured non-generic carrier
```

Generic Completion is not an unconditional theorem for all sectorized systems.
The claim-status split is:

```text
codimension theorem: proved
rank-protection corollary: proved
generic nonincidence proposition: algebraic consequence
completion away from incidence: conjectural theorem program
```

### Relation to the Trilogy

Papers I--III remain the Rubik-centered trilogy. Later structure can be read
back into them as bounded discussion-level context:

- Paper I: the rational spectral layers later acquire a collision-quotient
  interpretation.
- Paper II: the transport sectors are QT/HT joint-spectral sectors, and the six
  layers appear as their collision quotient at `alpha=2/3`.
- Paper III: T7 is the first accessibility-separation example, not the final
  theory.
- CCS: records canonical computational data and bridge notes without importing
  unproved completeness claims.

---

## 12. One-Sentence Program Summary

The RIME program starts from the Rubik representation as a finite reproducible
laboratory, extracts spectral and accessibility geometry, studies how those
geometries deform across generator-set moduli spaces, and explains why the
resulting behavior is generically complete away from high-codimension
incidence degeneracies.
