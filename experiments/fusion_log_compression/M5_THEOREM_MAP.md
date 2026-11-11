# M5 Theorem-to-Source Map

## Owner and Domain

The manuscript owner is Section 5 of the Fusion-log mathematical reader,
frozen at `fusion-log-compression-source-v1.0`. The M5 Lean owner is the
independent Lake project `lean_m5/`, extending the unchanged M4-D source
tag `fusion-log-m4d-source-v1.0` at content commit
`0c6bbebf19bca9d1bedc0fe63b23821b8b913d0f`.

M4-D manifest SHA-256:
`8a62981066908a78a4085c2977636cd4ffec83c283b5fd38997cc67ba31dc275`.
M5's exact inputs are bound by `m5-development-manifest.v1.json`.
Public tag and hosted-run facts are recorded separately from that input
manifest and the historical local receipts.

The actual-object theorems have a fixed `LiteralPacketStart C n`, with
`alpha : Type*`, decidable equality, `NeZero n`, `NeZero C.rank`, and
`3 <= n`. The start supplies a concrete initial placement and a matching
legal positively ordered naming of the circle's packets. The existing legal
naming includes nonempty packets, disjointness, distinct sites and atom
coverage. Put `t = C.rank`; the named-site injection implies `t <= n`.
The rank-refined theorem assumes `1 <= s <= t`.

## Actual Types

`RawActualLogFiber F start target` is the subtype of full event lists with
`JointlyAttainable F start.execution events target`. No schedule, deletion
list, or event-count premise is part of this definition.

`RawJoint F start d` consists only of `(events, target)` with actual joint
reachability and `events.length = d`. The theorem
`jointlyAttainable_length_add_rank` gives `d + packetRank target = t`, so
`d=t-s` is exactly the manuscript's rank-s joint class. Multiple words or
different reachability proofs do not add elements to either type.

`RawLiteralEndpoints F start s` stores only a literal target with rank s
and reachability proofs, not a log, an anchor representative, or a raw word.

## Main Correspondence

All declarations below have namespace `FusionLogEnumeration`.

| Manuscript / proof role | Lean declaration | Source in `lean_m5/FusionLogEnumeration/` |
| --- | --- | --- |
| Lemma 5.1, record-only schedules versus boundary deletion orders | `admissibleLogsEquivBoundaryDeletions` | `BoundaryBijection.lean` |
| Full ordered records distinguish paths, including rank two | `Schedule.records_injective` | `Schedules.lean` |
| Log count `t! / s!` | `card_admissibleLogs_rank` | `BoundaryBijection.lean` |
| Site/anchor coordinate count | `card_endpointChoices` | `EndpointCounting.lean` |
| Every M5 schedule has an M4-D admissibility certificate | `schedule_admissible_of_literalStart` | `ScheduleAdmission.lean` |
| Every actual log lies in the M5 family | `LiteralPacketStart.jointlyAttainable_logRun` | `LogCompleteness.lean` |
| One log, all actual literal endpoints | `fixedScheduleLiteralEndpointEquiv`, `card_actualLiteralEndpointFiber` | `FixedScheduleEquiv.lean` |
| Literal packet data determine visible survivors | `survivorsOfLiteralEndpoint_eq`, `actualLiteralEndpoint_same_survivors` | `LiteralSurvivorRecovery.lean` |
| Same survivors give compatibility with the very same target | `jointlyAttainable_iff_same_survivors` | `LiteralSurvivorConverse.lean` |
| Visible endpoint's unrestricted actual log fibre | `rawActualLogFiberEquivFixedSurvivorDeletionOrders` | `RawLogFiber.lean` |
| Rank-one endpoint's unrestricted actual log fibre | `rawActualLogFiberRankOneEquiv` | `RawLogFiber.lean` |
| Proposition 5.3, full piecewise fixed-target formula | `card_rawActualLogFiber_of_reachable` | `RawLogFiber.lean` |
| Actual joint data versus dependent fixed-log endpoint fibres | `rawJointEquivSigma` | `ActualJointCounting.lean` |
| Both data-preserving inverse interfaces | `rawJointEquivSigma_data`, `rawJointEquivSigma_symm_data` | `ActualJointCounting.lean` |
| Theorem 5.2, actual joint count | `card_rawJoint` | `ActualJointCounting.lean` |
| Reverse decomposition over actual endpoints and actual logs | `rawJointEquivEndpointLogs` | `ActualJointCounting.lean` |
| Distinct actual endpoint counts, visible and rank-one | `card_rawLiteralEndpoints`, `card_rawLiteralEndpoints_rankOne` | `ActualJointCounting.lean` |

`Signatures.lean` prints the complete final signatures and the underlying
actual type definitions into each replay receipt. The source theorem names,
not this explanatory table, determine their hypotheses.

## Final Formulas

```text
card (RawJoint F start (t-s)) = (t! / s!) * (s * choose n s)

card (RawActualLogFiber F start target) =
  if packetRank target = 1 then t! else (t - packetRank target)!
```

The second formula assumes that the literal target is actually reachable.
No designated reference schedule is required in its public signature.

For `2 <= s <= t`, the distinct endpoint count is
`choose t s * (s * choose n s)`; for rank one it is `n`. The reverse fibre
decomposition recovers the independently proved actual joint total using
these endpoint counts and the fixed-target log-fibre cardinalities.

The last rank-two event retains its ordered parents even when both parent
orders yield the same full atom union. At rank one the last surviving
boundary is absent from the endpoint but remains recoverable from a full
deletion log. Zero-event schedules, `s=t`, and `t=s=1` are included.

## Dependency Chain

```text
record injectivity + exact contraction/deletion update
 -> schedule/boundary-order equivalence and factorial count
 -> static source-index admission into M4-D
 -> reverse admission for every actual complete log
 -> fixed-log coordinate/literal endpoint equivalence
 -> visible-survivor necessity and sufficiency
 -> separate rank-one same-phase compatibility
 -> unrestricted actual log fibres
 -> actual joint dependent equivalence
 -> exact joint and endpoint counts
```

The rank-one branch uses the full initial atom union, not a recovered last
boundary. The coordinate-only log fibre and the literal endpoint log fibre
are different observations and are never substituted for each other.

## Reproduction and Audit

Lean is `leanprover/lean4:v4.33.0`, runtime commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`; Mathlib is
`db584cd6d46c92f209a44c0f1c829460d327499d`.
From this experiment directory:

```text
python -B validation/replay_m5.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m5.py
python -B validation/replay_m5.py --report results/my-m5-replay.json
```

The launcher verifies the unchanged ancestor closure and every M5 source
input, builds the library, replays the exact 64-target axiom inventory and
captures the elaborated signatures. Only `propext`, `Classical.choice` and
`Quot.sound` are allowed. Qualified uses of the inherited `named.admit`
method are ordinary proven API calls, not tactic placeholders.

Local receipts, GitHub-hosted Ubuntu receipts and source/deposit identities
are distinct records. The axiom sets are transitive for the declared targets;
they are not an independent mathematical review. All-R optimality and
shortest-word uniqueness remain outside M5.
