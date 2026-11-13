# All-R optimality: independent Lean module

This is an independent development layer for the specified all-right
fusion-log target. It does not modify the frozen M1--M3 package.

## Proved interfaces

- `AllROptimality.lean` contains the local list-potential identities and the
  original certificate-based arithmetic interfaces. `rotation_lower_bound`
  explicitly requires `3 ≤ n`.
- `CarrierRotation.lean` follows a marked atom through actual chronological
  execution, including effective fusions. Its nonnegative height satisfies
  `height + downwardSteps = initialHeight + count p`, and its residue is the
  atom's actual physical site. `executionCarrierReturns` counts literal `d`
  steps whose predecessor has the atom at port 1; it agrees with the height
  counter. In an all-R inter-fusion interval these returns are precisely
  nonfusion carrier backslides; this interpretation is not asserted for
  unrestricted histories.
- `actual_interFusion_rotation_lower_bound` derives `n + returns ≤ count p`
  from actual start/end port conditions and source order, without assuming
  a numerical interval lower bound. `actual_tail_rotation_lower_bound`
  derives `n - 1 + returns ≤ count p` for the terminal tail.
- `RightFusionIntervals` records an actual decomposition into successive
  right fusions, with port membership facts. Its inductive rotation theorem
  and `actual_allR_rotation_lower_bound` sum the local bounds, including
  terminal-tail returns. The decomposition does not assume any cost bound.
- `HoleTrace.lean` represents stationary, external-slide, carrier-backslide,
  rank-one backslide and right-fusion gap rewrites. `potential_balance` and
  `fusion_budget` are derived by induction rather than supplied as balance
  assumptions. `allR_slide_identity` proves
  `slides = (n-1)*(n-2)/2 + weightedBack` for a trace from the initial
  post-registration gap vector to rank one. Rank-one backslides have weight
  zero but are still counted.
- `AllRTraceExtraction.lean` adds the literal execution-to-trace interface.
  Once an execution annotation is supplied, `ExecutionTrace` binds every `d`
  letter to one gap rewrite and every `p` letter to a stationary step. Its
  induction proves the exact `d`-ledger equation, including explicit counts
  for backslides and stationary defect letters. An
  `AllRTraceExtraction` certificate combines this simulation with the actual
  interval rotation theorem and derives the closed all-R lower bound
  `(3*n*(n-1))/2 - 1`. Its corrected surplus separates unweighted carrier
  returns from the weighted potential correction.
- `MinimalTraceRigidity.lean` proves that a minimum-length annotated witness
  has no stationary, ordinary-backslide, or rank-one-backslide `d` step, and
  that the actual carrier-return counter vanishes. The ordering of the
  remaining steps is proved separately by the stage and raw-word modules below.
- `PhysicalGapSimulation.lean` links an unwrapped physical support ring to a
  real source-ordered execution. It proves letter-level rotation invariance,
  actual stationary-`d` invariance, and transports occupied support through
  the source-order defect map. It also proves the local external-slide,
  backslide and fusion gap-list identities. The complete physical `d`
  transition classification and state-indexed trace construction are proved
  under `RightCarrierDefect` / `RightCarrierRun`. The state-indexed trace
  equates unweighted backslides with the physical carrier-return counter.
- `RawAllRBridge.lean` defines the target by its complete ordered fusion log
  and literal endpoint, proves agreement with the frozen `runLogged`
  semantics, and derives `RealizesAllR.rightCarrierRun` from the actual log.
  Directionality is not inferred from the rank-one endpoint alone.
- `RawAllRSegmentation.lean` extracts the first registration prefix from the
  same chronological complete log and recursively decomposes the post-
  registration word into actual right-fusion intervals and a fusion-free tail.
- `RawAllRLowerBound.lean` exports the raw-word consequence directly at the
  declared target interface:
  `RealizesAllR word -> (3*n*(n-1))/2 - 1 <= word.length`. This is a
  lower-bound theorem for the complete ordered log and literal endpoint; it
  does not assert an attaining word or uniqueness.
- `AllRSurplusIdentity.lean` exports the full manuscript excess-cost identity
  (6.9) as `RealizesAllR.word_length_surplus_identity` for every raw realization
  at `n >= 3`. The functions `allRBackslidesAt`, `allRIdleDefects` and
  `allRRotationExcess` compute `B_m`, `Z` and `R` from the actual word and
  chronological states. Physical-trace induction identifies the backslide
  levels and idle counts with the gap ledger, and
  `RealizesAllR.rotation_excess_accounting` proves that the natural-number
  definition of `R` is exact nonnegative slack. The identity retains the
  separate `2 * B_0` term for rank-one backslides and sums `(m + 2) * B_m`
  over `1 <= m <= n - 2`; no caller-supplied annotation is required.
- `RawAllRUpperWitness.lean` defines the manuscript's explicit all-right
  candidate word and proves its exact length is
  `(3*n*(n-1))/2 - 1`. The actual execution theorem for that candidate is
  proved separately by `RawAllRUpperExecution.lean`: each stage has the
  specified literal placement and appends exactly one ordered fusion record,
  and the final rotation reaches the literal rank-one endpoint.
- `RawAllRUpperExecution.lean` proves
  `RealizesAllR (allRCanonicalWord n)` for every `n >= 3`. Together with
  `RawAllRLowerBound.lean`, `allRCanonicalWord_is_shortest` proves the exact
  minimum length for the specified complete ordered log and literal endpoint:
  `(3*n*(n-1))/2 - 1`.
- `MinimalWordRigidity.lean` proves the first equality-case consequences:
  the registration prefix is exactly `[d]`, and every right-fusion interval
  uses exactly `n` rotations while the terminal tail uses exactly `n - 1`.
  `RealizesAllR.minimal_rotation_decomposition` exports this decomposition
  directly for a raw realization attaining the lower bound.
  This module supplies the equality-case budgets; the subsequent modules
  prove slide ordering and literal word uniqueness.
- `StageSlideRigidity.lean` proves a literal local equality-case theorem. From
  a canonical all-R boundary, a fusion-free prefix, active defect letters,
  and the exact one-turn rotation budget, the next specified fusion stage is
  forced to be `p^(n-j) d (p d)^j`. The proof follows the marked singleton's
  actual lifted height and uses the source-order map to exclude background
  packets from port 1. Its strongest interface assumes neither a stage defect
  count nor a canonical terminal placement: both follow from the physical
  constraints.
- `RawAllRUniqueness.lean` proves that a raw all-R realization attaining the
  exact lower bound has no inactive (port-1-empty) defect letter: deleting one
  would preserve both the complete log and literal endpoint and contradict
  the raw lower bound. It then derives each interval's exact rotation budget,
  applies local stage rigidity, and obtains the next canonical boundary from
  the actual execution theorem. A separate rank-one tail proof excludes all
  remaining defect letters. `RealizesAllR.eq_canonical_of_minimum_length`
  proves literal raw-word uniqueness directly from the target and minimum
  length, without requiring a caller-supplied decomposition or gap trace.
  `allR_existsUnique_minimum_word` combines the actual attaining word, its
  length formula, and uniqueness into one `ExistsUnique` theorem.

## Raw certificate extraction

`RawAllRCertificate.lean` now assembles the complete state-indexed certificate
from an arbitrary word satisfying the declared `RealizesAllR` target:
registration prefix, `RightCarrierRun`, right-fusion intervals, the initial
and terminal `GapRep` witnesses, physical trace, fusion-count alignment, and
the carrier-return ledger. Thus the previously separate directional and gap
trace obligations are closed under the stated target interface. The target
remains the specified complete ordered fusion log and literal endpoint.
No frozen M1--M5 source or manuscript is changed by this development.

## Exact minimum and literal word uniqueness

The manuscript's explicit word
`d (p^(n-j) d (p d)^j)_{j=1,...,n-2} p^(n-1)` is checked by the bounded
Python controls for `n=3,...,6`, including its target log, literal endpoint,
length and observed uniqueness. The all-parameter Lean development now proves
that this word realizes the target, is shortest, and is the unique literal
word attaining the minimum. For every `n >= 3`, the exported interface is:

```text
RealizesAllR word ->
  word.length = (3*n*(n-1))/2 - 1 ->
  word = allRCanonicalWord n
```

The paper-facing summary `allR_existsUnique_minimum_word` states:

```text
∃! word : List Letter,
  RealizesAllR word ∧ word.length = (3*n*(n-1))/2 - 1
```

The proof first forces registration to be `[d]` and removes the possibility
of any inactive defect. The remaining rotation lower bounds force exactly
one turn per fusion interval. In each interval the first active slide fixes
the initial rotation; physical exclusion of all background packets from port
1 then forces the marked singleton's remaining moves to alternate `p, d`.
Induction restores the canonical boundary after every fusion. At rank one,
the minimum tail rotation budget and literal endpoint force `p^(n-1)`.

This is a local all-parameter Lean milestone for the specified complete
ordered all-R fusion log and literal endpoint. It does not identify a
globally farthest target or determine the state-space diameter, and it does
not change the identity of any frozen package or manuscript. The bounded
Python controls remain separate evidence from the all-parameter Lean proof.

## Validation

Use the pinned Lean 4.33.0 and the inherited Mathlib lock. If the local
shared-cache helper is available, first validate reuse from the repository
root with `rime-lean-cache experiments/fusion_log_compression/lean_all_r`.
From this directory:

```text
lake --no-cache build
lake env lean FusionLogAllR/AxiomAudit.lean
```

On a fresh environment obtain the pinned dependencies and Mathlib artifacts
first. Reusing local shared artifacts is a warm build, not independent
cold-start reproduction. The explicit axiom audit must contain no
`sorryAx`; its only permitted foundational axioms are `propext`,
`Classical.choice` and `Quot.sound`.

`AxiomAudit.lean` currently names 69 distinct declarations: the earlier 63
targets and six added for the surplus identity, physical ledger alignment,
and exact rotation slack. This is an explicit audit-target count, not a count
of all transitive proof declarations or a new release/cold-replay identity.
