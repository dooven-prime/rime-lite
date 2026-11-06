# M3 theorem-to-source map

Status: local checked development milestone, 2026-11-05.

## Public Statement

With `n >= 3`, `r >= 1`, `[NeZero n]`, `[NeZero r]` and
`[DecidableEq alpha]`, let `first second : NamedCyclicPlacement n r alpha`.
Assume `s.placed = first.placed` and `first.block = second.block`.
The named-placement type includes nonempty, disjoint, covering packets,
injective occupied positions and positive cyclic order. In particular it
implies `r <= n`; actual reachability is not an added premise.

`FusionLogCompression.sameOrderPlacement_short` proves:

```text
exists word : List Letter,
  FusionFree F s word /\
  run F s word = {s with placed := second.placed} /\
  word.length <= (3 * n - r) * (r - 1) + (n - 1)
```

This display is ASCII shorthand; the complete elaborated signature is printed
by `AxiomAudit.lean` and saved in the replay report. Updating only
`placed` preserves `origin` and `chain` literally.

`sameOrderPlacement_logged` additionally proves
`(runLogged F s word).fullLog = s.fullLog` for the same word and
the same starting invocation.

## Owners and Correspondence

| Paper / proof obligation | Owning local declaration | Source |
| --- | --- | --- |
| Lemma 3.1, hole batch | `batchWord_spec` | `M1Batch.lean` |
| Lemma 3.2, ordered merger | `adjacentFusionWord_spec` | `M2AdjacentFusion.lean` |
| Complete one-event log append | `loggedAdjacentFusionWord_fullLog` | `FullFusionLog.lean` |
| Proposition 3.3, normalized flow | `gapFlow_exists_normalized`, `frameGapFlow_exists` | `M3GapFlow.lean`, `M3CyclicSchedule.lean` |
| Same actual representative at every prefix | `cutSchedule_prefix` | `M3CyclicSchedule.lean` |
| Batch and transfer bounds | `gapFramePlacement_plan` | `M3CyclicSchedule.lean` |
| Literal endpoint and raw-letter budget | `sameOrderPlacement_short` | `M3Placement.lean` |
| Complete-log preservation for M3 | `sameOrderPlacement_logged` | `M3Placement.lean` |
| Rank-one / full-rank checks | `oneBlock_phase_only`, `fullRank_phase_only` | `M3BatchPlacement.lean` |

Paths in the table are relative to `lean/FusionLogCompression/`.
The manuscript correspondence refers to the unnumbered Fusion-log
candidate's Proposition 3.3; its source bytes are not changed or promoted
by this milestone.

## Construction

1. Gap conservation gives a nonnegative flow with one zero edge and
   every edge at most `n-r`.
2. Reindex cyclic edges starting immediately after that zero edge.
   The linear schedule proves donor capacity before every transfer.
3. Skip zero transfers. Compile each positive transfer using one legal
   actual batch, retaining its updated gap frame, packet names and exact
   successor execution in the indexed plan.
4. After at most `r-1` batches all target gaps agree. Total transferred
   hole mass is at most `(n-r)*(r-1)`.
5. Append one charged rotation to match the literal target phase.
   The cost is `2*n*K + M + phase <= (3*n-r)*(r-1)+(n-1)`.
   For rank one the separate phase argument uses at most `n-1` letters.

Thus an abstract vector identity is not being substituted for actual
path composition.

## Dependency and Audit Boundary

The local chain is
`M1Batch -> M3BatchPlacement/M3GapBatch -> M3CyclicSchedule ->
M3Placement`, with arithmetic inputs from `M3GapFlow` and
`M3LinearSchedule`. The logged corollary also imports `FullFusionLog`.

The vendored owner supplies `Execution`, `FusionFree`, `GapFrame`,
`NamedCyclicPlacement`, frame decoding and phase alignment. Its 51
source hashes and Git identity are fixed separately in
`upstream-pin.v1.json`. Local sources and the complete external lock
are fixed in `proof-manifest.v1.json`.

`AxiomAudit.lean` prints transitive axioms for 18 selected declarations,
including M1/M2, M3's schedule, its final endpoints and the degenerate
phase cases. Only `propext`, `Classical.choice` and `Quot.sound`
are accepted. The lexical placeholder check is supplemental; the kernel
build and transitive axiom output supply the proof evidence.

M4's complete-log replay induction, generic initialization of M2's
source-order interface, joint log/endpoint counting and shortest-word
optimality are not endpoints of this milestone.
