# M4 budgeted source-ordered replay

## Domain and Interface

The final owner is `FusionLogReplay.sourceOrdered_log_endpoint_budget` in
`lean_m4/FusionLogReplay/SharpBudget.lean`. For every `n >= 3`, `F`, logged
execution `s` with `SourceOrdered s.state.placed`, and chronological word
`w`, it returns an actual `JointReplayPlan` whose word has the same complete
ordered fusion log and literal final placement as `w`.

`SourceOrdered` is the fixed source-lift property on `ZMod n` atoms, not
an arbitrary ambient placement or a clean-outside assumption. All events
are actual occupied-port fusions, including outside-only fusions.

Write `t = packetRank s.state.placed` and
`s' = packetRank (run F s.state w).placed`. Then:

```text
plan.word.length <=
  3*n*(t-s') + (n-t)*(t-s') + choose(t-s',2)
  + (3*n-s')*(s'-1) + (n-1)
plan.batches <= t-1
plan.transfers <=
  (n-t)*(t-s') + choose(t-s',2) + (n-s')*(s'-1).
```

These are the manuscript's specific B/K/M upper bounds, not optimum costs.
The counters come from actual M2 stages and an actual M3 batch plan; the
final rotation is charged in the word length, not as a hole transfer.

## Owners and Dependencies

All extension module paths below are under `lean_m4/FusionLogReplay/`.

| Declaration | Owner | Role |
| --- | --- | --- |
| `packetRank_eq_occupied` | `RankLedger.lean` | Named packet cardinality equals occupied-site rank |
| `packetRank_fusion_drop` | `RankLedger.lean` | One actual effective fusion reduces rank by one |
| `packetRank_run_ledger` | `RankLedger.lean` | Final rank + actual event count = initial rank |
| `prefix_rank_and_holes` | `RankLedger.lean` | Prefix rank `t-j` and hole count `n-t+j` |
| `FusionStage.gap_le_holes` | `FusionStage.lean` | Actual gap is bounded by current holes |
| `FusionStage.cost` | `FusionStage.lean` | At most one batch, exactly `f` transfers, at most `3*n+f` letters |
| `FusionStage.no_batch_of_zero_gap` | `FusionStage.lean` | Zero gap causes no nonempty batch |
| `firstEvent_replay_step` | `FirstEventRoute.lean` | Keeps concrete stage and matching successor partition |
| `FusionReplayPlan.transfer_bound` | `ReplayPlan.lean` | Sums evolving gaps to `(n-t)*d + choose(d,2)` |
| `FusionReplayPlan.sharp_length_bound` | `ReplayPlan.lean` | Fusion-phase raw-letter bound |
| `replay_complete_events_plan` | `BudgetedReplay.lean` | Every reference trace has an actual chained replay plan |
| `align_sourceOrdered_endpoint_plan` | `EndpointPlan.lean` | Keeps M3 flow plan plus charged final phase |
| `JointReplayPlan.execute` | `SharpBudget.lean` | Exact event trace and literal endpoint |
| `JointReplayPlan.length_bound`, `batch_bound`, `transfer_bound` | `SharpBudget.lean` | Joint B/K/M accounting |
| `sourceOrdered_log_endpoint_budget` | `SharpBudget.lean` | Final simultaneous semantic and budget theorem |

```text
frozen execution + M1/M2
  -> actual event trace / packet-set invariance
  -> gap-aware first-event stage + exact rank ledger
  -> actual fusion replay plan + triangular hole sum
frozen M3 + canonical block naming
  -> actual endpoint flow/phase plan (including rank one)
both -> JointReplayPlan -> full log + endpoint + B/K/M
```

Each replay tail starts at the actual output of its head stage. There is
no representative switch or free phase insertion. The reference history
is used to extract the next complete ordered event, not to supply a
separate witness for each edge.

The final theorem is independent of `ReplayInduction.lean`'s coarse cost
proof. `EndpointPlan.lean` imports `EndpointAlignment.lean` only to reuse
the packet-set/placed-block interface; its construction calls the frozen
M3 plan theorem, not the coarse complete-replay theorem.

## Version and Replay

Lean: `leanprover/lean4:v4.33.0`, runtime commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`.
Mathlib: `db584cd6d46c92f209a44c0f1c829460d327499d`.

`m4-development-manifest.v2.json` binds the active extension's exact source
bytes and the unchanged M3 manifest. Its owning launcher verifies both
inventories before and after building, then audits 34 declarations with
`#print axioms`. Only `propext`, `Classical.choice`, and `Quot.sound` are
allowed. The saved local receipt also includes the checked signatures;
it is not an independent cold-environment replay.

```text
python -B validation/replay.py --verify-inputs-only
python -B validation/replay_m4.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m4.py
python -B validation/replay_m4.py --report results/my-m4-budget-replay.json
```

Existing receipts cannot be overwritten. M4 v1 is preserved as an exact
standalone source snapshot under `milestones/m4-source-ordered-v1/`.
The mathematical reader, controls, PDF and tag
`fusion-log-compression-source-v1.0` are outside this extension and remain
unchanged. The arbitrary-atom/initial-packet bridge and formal schedule
converse remain separate obligations.
