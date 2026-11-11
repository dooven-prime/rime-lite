# M5 Exact Enumeration Companion

This development package formalizes Section 5's finite enumeration and its
bridges to actual M4-D complete logs and literal endpoints. The actual joint
count is transported through dependent equivalences, as described below.
This is a local Lean development, not a frozen release or independent cold
replay.

## Implemented

- `Schedule` is equivalent to a complete ordered list of distinct initial
  boundary deletions, including the directed rank-two event.
- For a marked circle of rank `t`, the number of schedules ending at rank `s`
  is `t! / s!`.
- A fixed positively ordered packet circle has endpoint coordinates given by
  an `s`-site subset and an anchor packet/site choice; this type has cardinality
  `s * choose n s`.
- The product normal form for complete-log/endpoint coordinates has cardinality
  `(t! / s!) * s * choose n s`.
- `ActualJointCounting.lean` identifies actual full-log/literal-endpoint pairs
  with the dependent sum of fixed-log endpoint fibres, then with that product
  normal form. `card_rawJoint` gives the same exact count for actual jointly
  attainable data from a fixed legal, positively ordered literal start.
- `forgetLogCoordinates` forgets the log and retains only sites plus the
  anchor coordinate. Its `CoordinateLogFiber` has `t! / s!` logs at every
  fixed coordinate.
- For a fixed set of surviving source boundaries, the combinatorial
  `FixedSurvivorDeletionOrders` fibre is an ordering of its complement and has
  cardinality `(t-s)!`. `RawLogFiber.lean` now identifies it with the complete
  actual-log fibre of a reachable literal endpoint in the visible-rank regime
  `2 <= s <= t`.
- `RankedEndpointChoices` therefore carries proofs of `2 <= s` and
  `s <= t`. Rank one is represented separately by `RankOneEndpointChoices`:
  the literal placement records only carrier phase, while the `t!`
  literal log fibre includes every choice of the invisible last surviving
  boundary. Its actual count `t!` is proved separately.

The declarations are in `FusionLogEnumeration/BoundaryBijection.lean`,
`EndpointCounting.lean`, `DeletionFiber.lean`, and
`ActualEndpointBridge.lean`. The visible-rank survivor bridge is in
`SurvivorRecovery.lean`, `LiteralSurvivorRecovery.lean`,
`SurvivorConverse.lean`, and `LiteralSurvivorConverse.lean`.

`LiteralPacketStart` now carries a M5 marked circle together with a concrete
initial `Placement`, a matching `LegalNamedPlacement`, and its positive-order
witness. `ActualJointBridge` then carries an M4-D admissible schedule for the
same event list and a `CompatibleEndpoint` proof for one literal target. Its
nonemptiness is proved equivalent to M4-D `JointlyAttainable` for that start,
schedule log, and target.

The endpoint bridge now also constructs a source-ordered reference endpoint
from the M4-D abstract trace. Its canonical named packet cycle is used to
decode endpoint coordinates, and `terminalCycle_coordinates_compatible`
proves that every occupied-site/anchor choice yields a `CompatibleEndpoint`
for the same schedule. Thus coordinate compatibility is a theorem, not a
field that callers must provide. `decodeFixedScheduleEndpoint` consequently
constructs an actual literal endpoint fibre without an external compatibility
certificate.

`EndpointInverse.lean` proves both coordinate inverse laws at the named
placement level. In particular, decoding coordinates and re-encoding recovers
the occupied sites and anchor, while encoding a positively ordered named
placement and decoding it restores the packet identity at every site.
`FixedScheduleEquiv.lean` then proves, for a fixed M4-D admissible schedule,
the dependent equivalence

```text
EndpointChoices n terminalRank ≃ ActualLiteralEndpointFiber start path
```

The proof factors through the compatible indexed endpoints for that schedule.
The inverse reads coordinates from the literal target by restoring its initial
source fibres; the `Nonempty ActualJointBridge` witness is used only to prove
compatibility and is not inspected for data. The forward map expands the
decoded indexed placement and carries the same fixed schedule as its joint
realization witness. The endpoint inverse restores equality of packet
contents at every physical site, not merely equality of rank, support, or
unordered terminal partition.

The same module transports the finite type structure along this fixed-log
equivalence and proves `card_actualLiteralEndpointFiber`: for the fixed start
and admissible schedule, the number of actual compatible literal endpoints is
`s * choose n s`, where `s` is the rank of the schedule's terminal reference.
This is a per-schedule physical endpoint count. It does not multiply by the
number of schedules. The separate dependent assembly and joint count are in
`ActualJointCounting.lean` below.

`SurvivorRecovery.lean` defines the initial circle's `boundarySuccessor` and
proves a contraction invariant: for each current packet, every original
representative except its outgoing boundary has its successor inside that
packet, while the outgoing representative's successor lies in the next
packet. Rotation preserves this invariant, including the cyclic wrap; a
contraction preserves it whenever at least two packets remain. Consequently,
`Schedule.terminalCircle_survivors_recover` recovers the surviving original
boundaries from the terminal packet contents alone at terminal rank at least
two. It does not inspect terminal boundary markers as recovery data.

`LiteralSurvivorRecovery.lean` connects these packet contents to M4-D
compatibility. The proof uses the injectivity of expansion on saturated
source fibres and induction on the complete ordered records.
`compatibleEndpoint_packetAtoms` identifies the literal endpoint's packet
set with the M5 terminal packet set, and `compatibleEndpoint_packetRank`
identifies their ranks. The recovery function `survivorsOfLiteralEndpoint`
reads only the fixed initial circle and the literal target. Its correctness
and cardinality are proved by `survivorsOfLiteralEndpoint_eq` and
`survivorsOfLiteralEndpoint_card`.

The actual-object corollary `actualLiteralEndpoint_same_survivors` states:
if two schedules have actual joint realizations with the same literal target
of rank at least two, their surviving-boundary sets are equal. The
propositional `Nonempty ActualJointBridge` witnesses are used only in the
proof; the recovery function does not extract data from them. This proves
survivor recovery, rather than the full fixed-target history-fibre count.

The converse is now proved by `SurvivorConverse.lean`. For any equivalence
relation on atoms, a contraction imposes exactly one extra relation: the
deleted original boundary representative and its original successor must be
equivalent. Induction gives `homogeneous_terminalCircle_iff`; hence terminal
packet contents depend on the deleted boundary set, independently of its
order. The proof also preserves the full initial atom support, and does not
assume that initial packets are singletons or cover the ambient type.
`Schedule.terminalCircle_packetAtoms_eq_iff_same_survivors` combines both
directions at terminal rank at least two. It equates packet contents, not
indexed lists whose anchors may differ by a rotation.

`LiteralSurvivorConverse.lean` restores saturated source fibres to show that
equal survivors imply equal M4-D terminal indexed partitions. Thus
`compatibleEndpoint_iff_same_survivors` proves, relative to one compatible
log, that another admissible log is compatible with the **same literal
target** exactly when its survivors agree. In particular,
`actualLiteralEndpointFiberEquivOfSameSurvivors` is an equivalence whose
underlying map preserves the entire literal target, changing only its
log-realization proof. For `n >= 3`,
`jointlyAttainable_iff_same_survivors` states the criterion directly for
actual raw words, with complete ordered event tuples and final placement.

These converse interfaces explicitly require an M4-D `AdmissibleSchedule`
for each comparison log. `ScheduleAdmission.lean` now constructs that
certificate for every abstract M5 `Schedule` from a `LiteralPacketStart`.

## Static Schedule Admission

`schedule_admissible_of_literalStart start path` constructs

```text
AdmissibleSchedule start.initial start.occupied_nonempty path.records
```

It is a `def`, since `AdmissibleSchedule` contains indexed event and packet
data in `Type`; `schedule_admissible_of_literalStart_nonempty` is its
propositional existence theorem. Neither interface assumes an execution word,
a compatible terminal placement, or an externally supplied admissibility
certificate. The construction uses only `NeZero n` and the literal start's
legal, positively ordered naming; no `n >= 3` realization hypothesis is needed
at this static layer.

`InitialCycleIndexing.lean` assigns source-site fibres to each initial atom
block. Its `indexBlock` encoding preserves unions. Positive named order,
through the faithful gap frame, proves an actual source-atom boundary between
each ordered neighbour pair. `start.circleBlocks` identifies these named
blocks with the M5 list. This is where orientation enters the admission
proof; disjointness alone is not used to infer it.

`MarkedCircle.IndexedCircle` records exact decoding of each current packet
and source adjacency of its positive neighbours. Rotation and contraction
preserve this static certificate, including the rank-two contraction to one
packet. Induction on `path` then proves `Schedule.indexed_abstractTrace` and
`Schedule.indexed_records_expand`: the indexed initial packet set is exactly
the canonical source encoding of `start.initial`, and the complete ordered
event tuples expand to exactly `path.records`. Intermediate physical
placements and short raw-word realization are not used in this induction.

The declaration exports the indexed terminal packet set via
`schedule_admissible_of_literalStart_last` and exact event agreement via
`schedule_admissible_of_literalStart_records`. Zero-event schedules and
rank-one terminal schedules are included. The separate rank-one endpoint
argument and actual history-fibre count are now provided below.

## Actual Literal-Endpoint Log Fibres

`LogCompleteness.lean` proves the reverse admission bridge. An arbitrary M4-D
indexed contraction trace decodes to `LogRun` on the initial M5 circle.
The key geometric step is `index_edge_original_boundary`: a source-site edge
between distinct current blocks crosses an original positively ordered named
boundary. The maintained `BoundarySuccessorInvariant` then identifies the
ordered neighbours in the current circle. `contract_allRanks` includes the
last rank-two contraction. Thus `jointlyAttainable_logRun` applies to every
actual raw-word log, not just logs already presented as M5 schedules.

`RawActualLogFiber F start target` is defined solely as complete structured
event lists with an actual joint realization from the fixed literal start
to the exact literal target. Its definition does **not** assume a schedule,
admissibility certificate, deletion list, or event count. Raw execution words
and realization proofs are not counted as additional log elements.

`jointlyAttainable_length_add_rank` proves that every such log has length
`t-s`. Consequently `rawActualLogFiberEquiv` identifies this unrestricted
actual fibre with the intermediate admissible-log fibre, leaving each full
event list unchanged. `SurvivorLogFiber.lean` restricts the existing
record/deletion bijection to one survivor set and explicitly transports raw
boundary labels to the typed initial-boundary complement.

For `n >= 3` and a reachable target of rank `s >= 2`, the resulting equivalence
`rawActualLogFiberEquivFixedSurvivorDeletionOrders` and its cardinality theorem
`card_rawActualLogFiber` give

```text
RawActualLogFiber F start target ≃ FixedSurvivorDeletionOrders C s survivors
card (RawActualLogFiber F start target) = (t-s)!
```

The survivor set used by the equivalence agrees with the set recovered from
the literal target by the earlier recovery theorem. Different deletion
orders remain different complete ordered parent/result event lists, by the
record injectivity in `Schedules.lean` and the boundary-deletion equivalence.

`RankOneEndpoint.lean` instead proves that every complete contraction has
the single terminal atom block equal to the initial atom union. Restoring
saturated source fibres yields the same terminal indexed partition for every
such log. This preserves compatibility with the **same target phase** without
recovering a last survivor. `rawActualLogFiberRankOneEquiv` identifies the
actual rank-one fibre with all complete admissible logs; hence
`card_rawActualLogFiber_rankOne` gives `t!`, retaining both directed final
rank-two parent bindings.

Finally, `card_rawActualLogFiber_of_reachable` uses only reachability of the
literal target and states the full piecewise formula using its physical rank:

```text
card (RawActualLogFiber F start target) =
  if packetRank target = 1 then t! else (t - packetRank target)!
```

The static completeness argument needs the supplied legal positive initial
circle; the raw realization and fibre theorems use `n >= 3` as in M4-D. These
are all-parameter Lean proofs over the actual `p,d` semantics, not finite
enumeration controls. They do not assert shortest-word uniqueness or a
cold-start reproducibility result.

## Actual Joint Objects and Total Count

`ActualJointCounting.lean` defines

```text
RawJoint F start d =
  { (events, target) // events.length = d ∧
      JointlyAttainable F start.execution events target }
```

Only the complete structured event list and the full literal target are
data. Execution words occur solely as witnesses of the reachability
proposition, so neither multiple words nor proof choices inflate the count.
For `n >= 3`, the module proves the two dependent equivalences

```text
RawJoint F start d ≃
  Σ path : Schedule C d, ActualLiteralEndpointFiber start path

(Σ path : Schedule C d, ActualLiteralEndpointFiber start path) ≃
  Schedule C d × EndpointChoices n (t-d)
```

The first is `rawJointEquivSigma`. Its forward-admission map has both
injectivity and surjectivity proved separately. Reverse log admission places
every actual log in `Schedule`; `Schedule.records_injective` makes this
schedule unique. `rawJointEquivSigma_data` and
`rawJointEquivSigma_symm_data` preserve the exact event list and literal
target in both directions. Both inverse identities are provided by the
`Equiv`, rather than assumed from a choice of realization word.

For the second, `fixedScheduleTerminalReference_rank` proves that the
reference rank is always `t-d`, by expanding and restoring terminal source
fibres. `fixedScheduleEndpointChoicesEquiv` then applies the existing
fixed-schedule endpoint equivalence with the statically constructed schedule
admission certificate. `scheduleEndpointSigmaEquivProduct` leaves the
schedule component unchanged and unifies all endpoint factors at rank
`s=t-d`. There is no additional coordinate-compatibility assumption.

Composing these equivalences with the existing finite count model gives
`rawJointEquivCountModel` and, for `1 <= s <= t`,

```text
card_rawJoint : card (RawJoint F start (t-s)) =
  (t! / s!) * (s * choose n s)
```

Here `t = C.rank`; the initial placement is legal, nonempty, and positively
ordered, as carried by `LiteralPacketStart`. The theorem includes zero
events (`s=t`) and rank-one targets (`s=1`), with complete ordered final
parent bindings retained in the log. It counts actual joint objects, not
just coordinate-only observations. It reuses the established schedule
count rather than reproving the factorial identity.

As a separate consistency check after this joint-object equivalence,
`rawJointEquivEndpointLogs` decomposes the same objects in the other
direction, over distinct reachable literal targets and their actual log
fibres. `RawLiteralEndpoints` stores only a target with rank and
reachability proofs. The existing fixed-target log-fibre counts give

```text
card_rawLiteralEndpoints : card (RawLiteralEndpoints F start s) =
  choose t s * (s * choose n s)                 -- 2 <= s <= t

card_rawLiteralEndpoints_rankOne :
  card (RawLiteralEndpoints F start 1) = n
```

`card_rawLiteralEndpoints_mul_logFiber` checks that these endpoint counts
times `(t-s)!` (visible rank) or `t!` (rank one) recover the independently
proved joint count. The rank-one argument does not recover or count a
surviving boundary as endpoint data. No existing survivor proof is changed.

## Observation Boundaries

The fixed-schedule literal endpoint equivalence is now proved. There are
still two distinct maps and hence two distinct fibre claims:

| Observation retained | Fibre over a fixed observation | Status |
|---|---|---|
| occupied sites and anchor coordinate only | all admissible logs, `t! / s!` | proved by `coordinateLogFiberEquiv` |
| one fixed admissible log | actual literal endpoint placements, `s * choose n s` | proved by `fixedScheduleLiteralEndpointEquiv` and `card_actualLiteralEndpointFiber` |
| literal packet placement, with `s >= 2` | deletion orders of the uniquely visible surviving-boundary complement, `(t-s)!` | proved for all actual complete logs by `rawActualLogFiberEquivFixedSurvivorDeletionOrders` and `card_rawActualLogFiber` |
| rank-one literal placement | all complete logs, including the invisible last survivor, `t!` | proved by `rawActualLogFiberRankOneEquiv` and `card_rawActualLogFiber_rankOne` |

Both directions of log admission, the actual fixed-target history-fibre
counts, and the dependent actual joint count are now proved, including the
rank-one exception. These results require the stated legal positive initial
circle and `n >= 3`; they do not assert optimal raw-word costs, arbitrary
initial cyclic orders, or a formalization of other manuscript sections.

## Build

With the pinned Lean toolchain and Mathlib dependencies available:

```text
lake build
lake env lean FusionLogEnumeration/AxiomAudit.lean
```

The explicit axiom audit covers 64 fixed-schedule, survivor-bridge, schedule
admission/completeness, actual history-fibre, and actual joint-count targets;
their transitive axiom sets contain only `propext`, `Classical.choice`, and
`Quot.sound`. These are local pinned-toolchain checks, not an independent
cold-start replay or a frozen release identity.
