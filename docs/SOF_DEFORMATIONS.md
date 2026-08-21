# SOF Deformations

**Status:** public dynamic-layer companion to Paper IX. Version 2.0 remains
the published release under DOI
[10.5281/zenodo.21713306](https://doi.org/10.5281/zenodo.21713306); version 2.1
is a release candidate for the Non-Intervention and Attribution Boundary
Revision. Paper IX remains the canonical source for release-local definitions
and theorems. This companion summarizes the typed deformation charts,
trajectories, response policies, wall pullbacks, and claim boundaries of the
current revision candidate.

Paper IX owns typed deformation charts, observable trajectories,
parameterization-relative response diagnostics, and wall pullbacks. It does
not own the static SOF object language, compiler contracts, wall-record
taxonomy, or report serialization.

## Object Deformation and Deformation Record

Paper IX separates a supplied object deformation, its ordered-path
trajectory specialization, and the resulting observation record:

```text
xi: T -> S,  t |-> S_t                 ObjectDeformation
xi_gamma = xi o gamma: I_gamma -> S    ObjectTrajectory on an ordered path
F_t = Observe_(eta,t)(S_t)             SOFObservationRecord
D_eta(xi) = (F_t)_(t in T)             DeformationRecord
```

External dynamics, parameter updates, environmental processes, or
interventions supply `xi`. A general parameter space `T` need not be ordered;
only the pullback along a declared ordered path `gamma` is an
`ObjectTrajectory`. Paper IX studies what the supplied deformation or
trajectory looks like through a declared SOF observation interface. It does
not infer or generate either source-side object.

Formation, differentiation, comparison, or serialization of `D_eta(xi)` has no
object-layer intervention semantics. This is the Deformation-Record
Non-Intervention Principle. It is a protocol and type boundary, not a claim
that arbitrary software implementations are side-effect free.

A mechanism-labelled record is indexed by a declared source-side mechanism
label or partition. The label does not causally identify that mechanism from
the observed response.

The v2.1 migration is therefore a semantic-type migration, not a boundary-only
annotation. Its ledger is validated against
`schemas/sofdeformation/deformation-record-migration-v2.1.schema.json`. A
legacy sampled trajectory may be retained as a `DeformationRecord`, but the
migration records `LEGACY_RECORD_ONLY`, `NOT_DECLARED`, and
`NOT_ESTABLISHED` when the historical evidence does not supply an underlying
`ObjectDeformation`, `ObjectTrajectory`, transition model, or causal
mechanism. Migration never invents those missing objects.

## Typed Deformation Chart

A static SOF object has the form

```text
F = (V, {Q_i}, Y; X, H_Hall),
```

where the Lie/Hall enrichment after the semicolon is optional and independent
of the operator alphabet. On `U subset T`, a typed deformation chart declares:

```text
finite-rank Hermitian bundle V -> U
fixed sector labels I
fixed operator labels A
fixed optional Lie labels G_0
continuous fields Q_i(t), Y_a(t), X_g(t)
fixed word and Hall/depth conventions
comparison map Theta_kappa into one target space E_kappa
```

The associated observed field is

```text
J_kappa(t) = Theta_kappa(fibre data at t).
```

A globally fixed finite-dimensional Hilbert space is the trivial-bundle
special case. Continuity is diagnostic-specific: one chart may support a
continuous block norm while failing to support a coherently labelled depth
field.

Changes in sector rank, label sets, operative alphabets, or Hall conventions
are chart-transition or schema events unless an additional comparison
construction is declared. They are not ordinary walls inside one fixed typed
field.

For spectrally derived sectors, the chart must pass

```text
Sigma_comm -> Sigma_normal -> Sigma_spec -> {Q_i(t)}.
```

Commutativity does not imply normality. Pointwise diagonalization does not
provide coherent projector continuation. Non-spectral sectorizations begin
from their own declared projector fields and do not acquire fictitious
spectral gates.

## Typed Dynamic Fields

Only declared carriers generate dynamic fields:

```text
operator/word:
  R_1[Y](t), Route_d[Y](t), W_d[Y](t)
  D_route^(<=d_max)[Y](t), D_word^(<=d_max)[Y](t)

Lie/Hall:
  R_1^Lie(t), R_2^Lie(t), D_Lie^(<=d_max)(t)

continuous:
  carrier-qualified block norms, ranks, dimensions, residuals, and proxies
```

The branches remain distinct. A support wall, route-rank wall, word-space
dimension wall, star-algebra-type wall, word-depth wall, and Lie-depth wall
are different events even when they occur at the same parameter value.

Exact depth `D_kappa` takes values in `N union {infinity}`. Exact finite depth
`D_kappa=d` requires a level-`d` witness and verified non-hits at every lower
level; a level-`d` witness alone proves only `D_kappa<=d`. Exact infinity
requires the relevant closure or saturation certificate. A finite audit must
distinguish first-hit certified at `d`, hit observed by `d` with minimality
unaudited, and `UNREACHED_AT_CUTOFF`; the last state is not exact infinity.

## Trajectories and Response

A general object deformation and its observed record are not automatically a
time trajectory. Response time is defined only after selecting

```text
gamma: I_gamma -> U,  I_gamma subset R.
```

For a selected observable `O_kappa`, the trajectory is

```text
O_(kappa,gamma)(s) = O_kappa(J_kappa(gamma(s))).
```

Every response statement is relative to:

- trajectory parameterization;
- observable normalization and orientation;
- norm;
- threshold or half-response policy;
- declared comparison domain.

Rescaling an observable or reparameterizing a path can change the crossing
time. Response time is therefore not an intrinsic invariant of the underlying
static SOF without an additional invariance theorem.

Finite non-crossing on a declared observation interval is a right-censored
response measurement, optionally displayed as
`UNREACHED_ON_DECLARED_INTERVAL`. It is not the filtration state
`UNREACHED_AT_CUTOFF`. Under Compiler v1.0 it remains an observed
`response_time` finding with null numerical value and censoring details in a
referenced sampling or trajectory policy.

## Wall Pullback

For a discrete typed feature `O_kappa`, a continuous comparison field
`J_kappa`, and a target discriminant `Delta_kappa`, Paper IX proves the
pullback inclusion

```text
Sigma_(O_kappa) subseteq J_kappa^(-1)(Delta_kappa).
```

Equality requires pullback-exactness: each point of the target pullback must
actually be a local change point of the selected feature. Along a
one-parameter trajectory, transverse crossing of a locally separating smooth
discriminant with different feature values on the two sides is a sufficient
condition. Tangency, motion within the discriminant, or equal features on both
sides need not produce a wall.

The theorem is typed. A discriminant for one carrier cannot establish a wall
for a nearby carrier.

## Current Evidence Boundary

The active Paper IX evidence has three distinct roles:

| Evidence | Status | Boundary |
|----------|--------|----------|
| three-sector direct/commutator threshold construction, with crossings `eta` and `sqrt(eta)` | Theorem with finite validation | parameterization- and threshold-relative; not a Boolean wall or Lie-depth result |
| calibrated exponential response inequality and three-sector realization, with `30 < 1380` | Theorem plus Computational Certificate | ordered calibration supplies the inequality; mechanism labels supply interpretation |
| training-coupled `K_0/K_1/K_2` ordering `60 < 80 < 120` | Computational Observation | endpoint-normalized sampled half-response; continuous proxy ordering only |

The continuous proxies do not imply

```text
R_1^Lie, R_2^Lie, D_Lie^(<=d_max)
```

or any corresponding response-time hierarchy. Such a promotion requires a
proxy-to-shadow theorem with threshold calibration, margin stability,
sectorization stability, and filtration compatibility.

Current executables, generated records, validation commands, and archived v1
provenance are indexed in
[experiments/paper9/README.md](../experiments/paper9/README.md). Archive files
do not support the typed Paper IX claims.

## Ownership Boundary

```text
Paper VIII  static typed SOF objects
Paper IX    typed deformations, trajectories, responses, and wall pullbacks
Paper X     capability-aware compilation and Registry evidence
Paper XI    typed wall morphology, coordinate profiles, and taxonomy
Paper XII   single-system report protocol
Paper XIII  aligned sparse comparison
Paper XIV   policy-relative interpretation and bounded candidate generation
```

Paper X may register a Paper IX finding but does not re-own its theorem or
certificate status. Paper XI may assign a taxonomy profile to a wall record but does not redefine
the deformation chart. Papers XII--XIV consume declared fields through their
own versioned interfaces.

## Claim Boundary

Paper IX does not claim:

- a universal deformation category;
- a primitive universal `Sigma_access`;
- a proxy-to-binary-shadow theorem;
- an intrinsic response-time invariant;
- a universal ordering of operator, commutator, word, or Lie-depth rates;
- coherent moving sectors across a schema transition without comparison data.
- generation of an object trajectory by its deformation record;
- causal identification from a mechanism-labelled observation.

These remain branch-qualified research problems.
