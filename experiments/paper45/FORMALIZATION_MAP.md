# Paper XLV: Source Provenance and Formalization Map

## Source Identity

An earlier source-frozen draft is retained in
[`papers/unnumbered/fusion_log_compression/`](../../papers/unnumbered/fusion_log_compression/);
it was not publicly released through HAL. Its source tag is
`fusion-log-compression-source-v1.0`, content commit is
`41cf746a095ecd06d85cb3d1184d58e7bfdd5979`, and source SHA-256 is:

```text
790188c21e075e37cb2f85a837721c5b1f2be4a913d942e228f63ab97db1b6e3
```

## Proof Development from the Retained C1 Draft

| Location | Retained C1 draft | Paper XLV candidate |
| --- | --- | --- |
| Abstract and introduction | Mathematical classification, counts and exact all-R optimum | Foregrounds the actual joint-object bijection and zero-surplus rigidity without a proof-inventory narrative |
| Corollary 4.2 | B/K/M construction bounds | Adds the singleton-start transfer identity and the exact rank-dependent budget gap |
| Theorem 5.2 | Bijection argument followed by product count | Explicit dependent sum over actual logs and actual literal endpoints, with literal-data inverse obligations |
| Proposition 5.3 | Literal-endpoint fibres | Separates them explicitly from coordinate-only fibres; keeps the rank-one exception |
| Corollary 6.5 | Unique shortest word, referring to Appendix A | Also exports a unique-existence formulation over raw words |
| Equation (6.9) | Displayed excess-cost identity from the manuscript ledgers | Also exports the complete identity as a named Lean theorem with operational `R`, `B_m` and `Z` |
| Appendix A | Slide-forcing argument | Local active-defect stage theorem, actual-log induction and independent rank-one tail, matching the Lean proof |
| Sections 8--9 | Registered observations and finite controls | Keeps the mathematical registration projection in Section 8; moves finite counts and source mapping to this index, with a short artifact entry in Section 9 |

This table records proof and presentation development within the manuscript's
source lineage. No general shortest-word formula, improved `7/2` coefficient,
or global all-R farthest-target theorem is added.

## Main Theorem Interfaces

All paths below are relative to the repository root. The public declaration
signatures determine their hypotheses; the table is navigation.

| Paper statement | Source and declaration | Scope |
| --- | --- | --- |
| Proposition 3.3 | `experiments/fusion_log_compression/lean/FusionLogCompression/M3Placement.lean`: `sameOrderPlacement_short`, `sameOrderPlacement_logged` | Eligible same-order named placements, actual fusion-free word and length budget |
| Theorem 4.1 | `lean_m4d/FusionLogSchedule/LiteralClassification.lean`: `abstract_schedule_endpoint_iff`, `abstract_schedule_bounded_realization` | Actual chronological log/endpoint pair from a legal nonempty initial placement; arbitrary atom type with decidable equality |
| Corollaries 4.2--4.3 | `lean_m4c/FusionLogInterpretation/ArbitraryInitialReplay.lean`: `arbitrary_initial_log_endpoint_budget`, `arbitrary_initial_log_endpoint_representative` | Same actual word retains the complete log and literal endpoint, with B/K/M ledgers |
| Lemma 5.1 | `lean_m5/FusionLogEnumeration/BoundaryBijection.lean`: `admissibleLogsEquivBoundaryDeletions`, `card_admissibleLogs_rank` | Ordered boundary-deletion lists; final rank-two parent order retained |
| Fixed-log literal endpoint equivalence | `lean_m5/FusionLogEnumeration/FixedScheduleEquiv.lean`: `fixedScheduleLiteralEndpointEquiv`, `card_actualLiteralEndpointFiber` | Initial literal placement fixed; actual literal endpoint count is `s * choose n s` |
| Theorem 5.2 | `lean_m5/FusionLogEnumeration/ActualJointCounting.lean`: `rawJointEquivSigma`, `card_rawJoint` | `RawJoint` stores only log and literal endpoint; execution words are not counted |
| Proposition 5.3 | `lean_m5/FusionLogEnumeration/RawLogFiber.lean`: `card_rawActualLogFiber_of_reachable` | All actual complete logs at a reachable literal endpoint; piecewise factorial count |
| Proposition 5.3, distinct endpoints | `lean_m5/FusionLogEnumeration/ActualJointCounting.lean`: `card_rawLiteralEndpoints`, `card_rawLiteralEndpoints_rankOne` | Visible survivors at rank at least two; separate `n`-endpoint rank-one branch |
| Lemma 6.1 | `lean_all_r/FusionLogAllR/RawAllRUpperExecution.lean`: `allRCanonicalWord_realizes`; `RawAllRUpperWitness.lean`: `allRCanonicalWord_length` | Actual specified complete log, literal endpoint and exact raw-list length |
| Theorem 6.4, exact minimum | `lean_all_r/FusionLogAllR/RawAllRLowerBound.lean`: `RealizesAllR.word_length_lower_bound`; `RawAllRUpperExecution.lean`: `allRCanonicalWord_is_shortest` | Raw realization, with no caller-supplied trace or segmentation |
| Theorem 6.4, equation (6.9) | `lean_all_r/FusionLogAllR/AllRSurplusIdentity.lean`: `RealizesAllR.word_length_surplus_identity`, `RealizesAllR.rotation_excess_accounting` | Exact raw-word surplus with actual backslide-level and idle-defect counts, including rank-one `B_0`; `n >= 3` |
| Corollary 6.5 | `lean_all_r/FusionLogAllR/RawAllRUniqueness.lean`: `RealizesAllR.eq_canonical_of_minimum_length`, `allR_existsUnique_minimum_word` | Unique literal `List Letter` at length `(3*n*(n-1))/2 - 1` |

For the rows abbreviated as `lean_m4c`, `lean_m4d`, `lean_m5`, or `lean_all_r`,
the omitted prefix is `experiments/fusion_log_compression/`.
The counted M5 interface fixes a legal positive `LiteralPacketStart`,
`n >= 3`, and `1 <= s <= t <= n`. The arbitrary-start classification uses
the initial physical packet order, not an assumed numerical order on atoms.

## All-R Uniqueness Chain

The input `RealizesAllR word` has exactly two fields: equality of the
complete ordered all-R fusion log and equality of the literal full-carrier
endpoint at site `n-1`. No optimality, segmentation, or stage invariant is
hidden in that definition.

1. `allRTraceExtraction_of_realizes` in `RawAllRCertificate.lean` extracts
   actual registration, intervals, physical gap trace and cost alignment
   from that raw input.
2. `RealizesAllR.minimal_starts_with_defect` and
   `RealizesAllR.minimal_rotation_count` derive the initial `[d]` and the
   total exact rotation budget.
3. `RealizesAllR.minimal_activeDefectsRun` independently excludes an idle
   defect by deleting it and contradicting the already proved raw lower bound.
4. `allRStage_word_unique_of_active` in `StageSlideRigidity.lean` forces
   the stage `p^(n-j) d (pd)^j` from actual
   canonical start, fusion-free prefix, next parent and exact one-turn budget.
   It assumes neither a defect count nor the next canonical endpoint.
5. `allRRemainingWord_unique` extracts each next actual fusion, forces its
   exact budget, applies local rigidity, and obtains the next canonical
   boundary from `allRStage_execution` before continuing the induction.
6. `allR_tail_word_unique` handles the full-carrier tail separately, including
   the zero-potential but positive-letter-cost rank-one backslide.
7. `RealizesAllR.eq_canonical_of_minimum_length` proves raw literal equality.
   `allR_existsUnique_minimum_word` packages it with actual existence and
   exact length, without a new mathematical hypothesis.

All declarations in this chain have namespace `FusionLogAllR`.

## Certification Boundaries

- The displayed surplus identity (6.9) is exported as
  `RealizesAllR.word_length_surplus_identity`. Its `B_m` counts actual carrier
  returns at each remaining-packet level, including level zero; `Z` counts
  actual defects with empty port 1. Physical simulation identifies these
  counts with the trace ledger. `rotation_excess_accounting` proves that
  `R = N_p - P_min - B` is exact nonnegative slack, rather than relying on
  truncated subtraction. The scope remains the specified all-R log and
  literal endpoint.
- The endpoint-only linear witness and the registered-observation projection
  remain manuscript arguments. The generic compression theorem preserves
  any observation which factors through its complete-log/endpoint target;
  it does not preserve letter-indexed null outputs.
- M5 has its own archived source and replay identity. The later All-R layer
  is currently a local independently built development; an aggregate Paper
  XLV companion archive and cold replay have not been created here.
- Finite Python controls retain their existing bounded scope. A new Lean
  proof does not turn their implementation into an independent semantics.

## Validation Routes

The [All-R README](../fusion_log_compression/lean_all_r/README.md)
owns the focused build and transitive axiom audit. Its audit now includes
`FusionLogAllR.allR_existsUnique_minimum_word` and
`FusionLogAllR.RealizesAllR.word_length_surplus_identity`.
The explicit audit list has 69 distinct declarations: the earlier 63 targets
plus the following six declarations in `AllRSurplusIdentity.lean` (all in
namespace `FusionLogAllR`):

- `PhysicalTrace.backslideLevels_eq_execution`
- `PhysicalTrace.idleSteps_eq_execution`
- `RealizesAllR.surplus_ledgers`
- `RealizesAllR.backslide_profile_total`
- `RealizesAllR.rotation_excess_accounting`
- `RealizesAllR.word_length_surplus_identity`

This counts named audit targets rather than all transitive declarations.
The [M4-D map](../fusion_log_compression/M4D_THEOREM_MAP.md)
and [M5 map](../fusion_log_compression/M5_THEOREM_MAP.md)
record their separate pins, theorem scopes and replay gates. No historical
manifest or saved receipt is regenerated for this numbered manuscript.
