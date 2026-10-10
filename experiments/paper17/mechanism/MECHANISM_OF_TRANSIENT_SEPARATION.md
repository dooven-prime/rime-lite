# Mechanism of Transient Separation

## 1. Scope

Paper XVII established a finite-horizon decomposition on a declared reduced
domain. Six unsafe fibers at `t=1` contain 51 sources; every source becomes
globally singleton under the coarse observation at `t=2`. A disjoint set of
five cohorts, with sizes `51, 25, 19, 4, 3`, remains non-singleton with the
same membership at `t=2` and `t=3` and has equal registered successors.

Those facts identify two fiber fates but no mechanism. This registration asks:

> Why are the unsafe fibers separated by the registered transition, while the
> persistent cohorts can remain microscopically distinct but coarsely
> successor-compatible?

This is a model-relative exact transition audit. It is not a biological causal
experiment, an intervention study, or a claim about the full MaleCNS source
universe.

### 1.1 System boundary

The registered model has no environment state, sensory world, action loop, or
external feedback term. The carrier is fixed, the update is deterministic,
external input is exactly zero, and stochastic noise is absent. Consequently,
MTS-1 studies

\[
  \boxed{\text{system-internal equivalence remodeling}}
\]

rather than world-mediated correction. Its strongest allowed interpretation
is:

> The registered internal dynamics transforms microscopic distinctions into
> different coarse equivalence fates.

Terms such as `world correction`, `environmental adjudication`, and
`externally induced separation` are outside the MTS-1 claim surface.

## 2. Frozen source and pair universes

Let `C_TO,i`, `i=1,...,6`, denote the six transient-obstruction fibers and let
`C_PS,j`, `j=1,...,5`, denote the five persistent-safe cohorts. Their exact
source membership is frozen by the cohort registry.

The primary transient pair universe is

\[
  P_{\rm TO}=\bigcup_{i=1}^{6}\binom{C_{{\rm TO},i}}{2}.
\]

It contains 570 unordered pairs. Exact sidecar replay verifies that every pair
has the same `t=0` and `t=1` coarse observations and a different `t=2` coarse
successor.

The persistent-safe pair universe is

\[
  P_{\rm PS}=\bigcup_{j=1}^{5}\binom{C_{{\rm PS},j}}{2}.
\]

It contains 1,755 unordered pairs. Every pair has equal exact coarse
observations at `t=2`, `t=3`, and `t=4`.

The five persistent cohorts remain separate analysis blocks. The six transient
fibers also remain separate. Counts over their unions are finite-census
descriptions, not iid sample sizes.

## 3. Exact transition decomposition

The frozen dynamics is

\[
  x_{t+1}=\frac45x_t+\frac15 C(u_t),
  \qquad u_t=Y_{\rm known\_pm}^{\mathsf T}x_t,
\]

where `C(q)=min(1,max(0,q))` is applied coordinatewise and `O` is the declared
superclass-mean observation. Every unordered pair `p={a,b}` receives the
canonical orientation

\[
  a=\min p,\qquad b=\max p.
\]

All signed differences and coordinatewise difference payloads use `a-b`, and
the clipping-fate table records rows for the fate of `a` and columns for the
fate of `b`. Define

\[
  \delta x_t=x_t^a-x_t^b,
  \quad \delta u_t=u_t^a-u_t^b,
  \quad \delta c_t=C(u_t^a)-C(u_t^b).
\]

Then

\[
  \delta z_{t+1}
  =O(x_{t+1}^a)-O(x_{t+1}^b)
  =\frac45O(\delta x_t)+\frac15O(\delta c_t).
\]

On a current-observation fiber, `O(delta x_t)=0`, so the exact successor fate
is localized to the clipped-drive residual:

\[
  \delta z_{t+1}=\frac15O(\delta c_t).
\]

To distinguish raw transport from nonlinear clipping, define

\[
  r_{\rm raw}=O(\delta u_t),\qquad
  r_{\rm clip}=O(\delta c_t),\qquad
  r_{\rm corr}=r_{\rm clip}-r_{\rm raw}.
\]

All three are exact rational vectors. The producer must verify the displayed
identities for every registered pair-transition record. These identities
localize a difference within the declared model; they do not by themselves
identify a biological mechanism.

In particular, on an observation fiber,

\[
  r_{\rm clip}=5\,\delta z_{t+1}.
\]

Replaying this identity is an implementation and certificate condition named
`IDENTITY_LAYER_REPLAY`. It is algebraically determined by the frozen update
and the already known successor relation. It is not a scientific outcome and
cannot by itself award `EXACT_TRANSITION_LAYER_LOCALIZATION`.

## 4. Registered feature families

Only the following feature families may enter the first mechanism audit.

1. **Microscopic state geometry.** Exact state-support intersection, union,
   symmetric difference, exact `L1` difference, and their target-sector
   decomposition.
2. **Raw signed-drive geometry.** Exact raw-drive support relations, exact
   `L1` difference, and `r_raw`.
3. **Clipping-fate geometry.** The exact `lower/interior/upper` fate of every
   touched target, the pairwise `3 x 3` fate-transition table, `r_clip`, and
   `r_corr`.
4. **Coarse pushforward geometry.** Exact current and successor observations,
   differing-coordinate support, and exact successor residual.
5. **Source-local carrier descriptors.** This family is closed to the fields
   `initial_sector_label`, `known_sign_out_degree`,
   `known_sign_positive_out_degree`, `known_sign_negative_out_degree`,
   `known_sign_outgoing_positive_mass`,
   `known_sign_outgoing_negative_absolute_mass`, and
   `known_sign_outgoing_absolute_mass`. These are descriptive covariates, not
   causal explanations. No additional carrier field is permitted in v1.

Floating tolerances are forbidden for equality, sign, clipping branch, or
residual classification. Hashes may index canonical payloads but may not
replace exact payload comparison.

No field or feature family may be added after mechanism execution begins. A
later field or family requires a versioned registration.

The first exact residual classification is frozen as the four possibilities

\[
  (r_{\rm raw}=0,\ r_{\rm clip}=0),\quad
  (r_{\rm raw}=0,\ r_{\rm clip}\ne0),\quad
  (r_{\rm raw}\ne0,\ r_{\rm clip}=0),\quad
  (r_{\rm raw}\ne0,\ r_{\rm clip}\ne0).
\]

This classification distinguishes raw carrier transport from the effect of
the state-dependent clipping layer only at the level of an exact phenotype.
There is no one-to-one map from the four quadrant labels to four mechanism
readings. The clipped residual remains tied to the known successor fate, so
scientific interpretation must use a preregistered conjunction involving
`r_raw`, `r_corr`, or nontrivial registered geometry rather than a quadrant
label alone.

## 5. Producer architecture

The Paper XVII canonical sidecar contains `O(x_t)` records and source metadata;
it does not contain the microscopic states `x_t`. MTS-1 therefore cannot use
that sidecar as a microscopic-state input.

The future exact producer must replay each of the 153 registered sources once
from its frozen unit-basis initial condition through `t=4`. At every time it
must require both:

1. byte equality of the canonical exact observation with the Paper XVII
   sidecar record; and
2. equality of the recomputed Paper XVII legacy sparse-state hash with the
   state hash recorded by Paper XVII source metadata.

The second check is a compatibility gate under the historical Paper XVII
serialization, not a new canonical MTS-1 state identity. MTS-1 additionally
serializes every replayed microscopic state under the domain-tagged
`RIME-MTS-MICROSTATE-V1` binary contract. That contract fixes the dimension,
strictly increasing coordinate order, zero omission, reduced rational form,
positive denominator, integer byte order, and digest algorithm. The canonical
payload bytes define semantic identity; SHA-256 binds and indexes those bytes
but does not replace exact payload comparison or exact replay.

The theorem-facing encoder accepts only Python `int`, `gmpy2.mpz`, and
`gmpy2.mpq` scalar values. It rejects `bool`, floating-point values, NumPy
scalars, strings, and other merely convertible objects. Its public v1 API
rejects every dimension other than `211577`. The strict decoder independently
checks the domain tag, version, dimension, declared nonzero count, coordinate
order, sign code, nonzero and minimally encoded integer magnitudes, reduced
rationals, and absence of trailing bytes.

Only after these checks may it create the source-transition cache. For each of
the 153 sources and current times `t=1,2,3`, the cache contains:

```text
x_t
u_t = Y^T x_t
C(u_t)
O(x_t)
O(u_t)
O(C(u_t))
per-target clipping fate
exact payload digests
```

Thus the producer performs 459 source-transition computations. It then derives
all

\[
  (570+1755)\times3=6975
\]

pair-transition records from the immutable cache. Recomputing the operator
action separately for each pair is forbidden.

## 6. Time and stratum firewalls

Fiber role and time are confounded in the defining Paper XVII observations:
the obstruction is observed at `1->2`, while persistence is observed at
`2->3` and `3->4`. The mechanism producer must therefore evaluate both source
roles on the common transition grid

\[
  1\to2,\qquad 2\to3,\qquad 3\to4.
\]

Every record carries `current_observation_equal`; transition-layer identities
that require current equality are asserted only when that flag is true.
Defining and hostile-control transitions remain separately labelled.

Initial anatomical strata also remain explicit. Direct cross-role summaries
are allowed only within shared strata (`cb_intrinsic` and `ol_intrinsic`).
The `ol_sensory`, `vnc_intrinsic`, `ascending_neuron`, and
`visual_centrifugal` blocks are reported without an invented matched contrast.

## 7. Outcome ontology

The first audit has four possible outcomes.

- `EXACT_TRANSITION_LAYER_LOCALIZATION`: all registered records are complete,
  every exact dynamics identity replays, and at least one explicitly named
  registered contrast involving `r_raw`, `r_corr`, state geometry, raw-drive
  geometry, or the clipping-fate table localizes the defining pair fates. The
  contrast must not be algebraically equivalent to `r_clip`,
  `delta_z_(t+1)`, or the known successor label. Any predicate, threshold, or
  finite classification used for this outcome must be frozen in the scoped
  execution amendment before mechanism payload generation.
- `PARTIAL_REGISTERED_FEATURE_CONTRAST`: the audit is complete, but the
  registered features give only cohort- or transition-limited contrasts that
  do not provide a uniform layer localization.
- `NO_CONTRAST_IN_DECLARED_FEATURE_FAMILIES`: the audit is complete and the
  registered feature families do not distinguish the two fiber fates beyond
  the already known coarse successor relation.
- `UNRESOLVED`: exact generation, resource closure, or required artifact
  validation is incomplete.

`EXACT_TRANSITION_LAYER_LOCALIZATION` is not a causal-mechanism claim. A
feature may be algebraically responsible inside the frozen model without being
biologically necessary, sufficient under intervention, or explanatory in the
real nervous system.

The scoped execution amendment may name only conjunctive model-layer
statements. For example, `RAW_NONZERO__CLIP_NONZERO` does not by itself imply
carrier-mediated separation: when `r_corr` is nonzero, clipping also changes
the residual. Likewise, `RAW_ZERO__CLIP_ZERO` does not establish coarse
pushforward annihilation unless registered geometry independently records a
nonzero microscopic or raw-drive difference. Precise predicates may describe
clipping creation, elimination, modification, or unchanged persistence of a
coarse residual. Calling a persistent-safe record safe forgetting additionally
requires the registered current-observation and successor-compatibility
conditions plus nontrivial geometry. These are exact statements inside the
frozen model, not claims about neural function in the organism.

The execution amendment must report two separate fields:

```text
IDENTITY_LAYER_REPLAY
    required certificate condition for every applicable record

NONTRIVIAL_REGISTERED_CONTRAST
    scientific classification using only predeclared non-tautological fields
```

## 8. Registration status

This is a post-result registration. The Paper XVII fiber fates and existing
aggregate support/clipping summaries were visible before registration. The new
registration freezes the pair universes, exact transition equations,
time-matched controls, allowed feature families, and outcome ontology before
new pair-resolved mechanism payloads are generated.

Execution remains unauthorized until a source-addressed producer, runtime and
resource preflight, output schema, result validator, and receipt contract are
bound in a scoped execution amendment. Cohort-registry validation alone does
not grant that authority.

## 9. Negative boundaries

The first audit must not claim:

- microscopic convergence or erasure of microscopic differences;
- clipping as a biological cause;
- recurrent-input, slow-mode, transmitter, receptor, or neuromodulatory
  mechanism;
- prevalence over the full source universe;
- indefinite persistence beyond the registered horizon;
- statistical significance, classifier generalization, or independent
  replication;
- repair or reopening of Paper XVII.

## 10. Deferred external-adjudication line

`MTS-2: External Adjudication of Equivalence` is a possible later experiment,
not part of this registration. It would require matched autonomous and
externally driven dynamics on the same initial fibers and would ask whether an
external input changes obstruction disappearance or persistent-safe cohort
membership. MTS-2 has status `NOT_REGISTERED` and execution authority `NONE`.
