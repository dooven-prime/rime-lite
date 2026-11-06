# M4: budgeted source-ordered complete-log replay

This extension imports the unchanged M1-M3 baseline through a local Lake
dependency. Lean and Mathlib remain pinned to the same versions. It is
outside the frozen HAL reader closure.

## Interfaces

| Owner | Declaration |
| --- | --- |
| `EventTrace.lean` | `eventTrace_eq_nil_iff`, `runLogged_fullLog`, `firstFusion_split` |
| `PacketSet.lean` | `packetSet_run_of_fusionFree`, `packetSet_fusion` |
| `RankLedger.lean` | `packetRank_eq_occupied`, `packetRank_run_ledger`, `prefix_rank_and_holes` |
| `FusionStage.lean` | `gap_le_holes`, `rank_drop`, `cost`, `no_batch_of_zero_gap` |
| `FirstEventRoute.lean` | `firstEvent_route`, `firstEvent_replay_step` |
| `ReplayPlan.lean` | `rank_ledger`, `transfer_bound`, `sharp_length_bound` |
| `BudgetedReplay.lean` | `replay_complete_events_plan` |
| `EndpointPlan.lean` | `align_sourceOrdered_endpoint_plan` |
| `SharpBudget.lean` | `sourceOrdered_log_endpoint_budget` |

Module paths in this table are relative to `FusionLogReplay/`.
`FusionRecord` retains both ordered parent sets and their result.
The letter, ports and collision target are fixed environment constants.

The packet-set and trace lemmas are generic in the atom type. Routing and
the replay induction currently use the frozen `SourceOrdered` interface:
atoms are `ZMod n` and the placement admits an oriented source lift.
The two replay states can have different physical placements, but start
with the same literal packet partition. They are not interchanged during
the construction: each routed successor is passed to the next induction
step.

For `n >= 3`, one joint plan retains the entire added effective-event list
and the exact endpoint, with the manuscript's specified upper bounds:

```text
B(n,t,s) = 3*n*d + (n-t)*d + choose(d,2)
           + (3*n-s)*(s-1) + (n-1),     d = t-s
K <= t-1
M <= (n-t)*d + choose(d,2) + (n-s)*(s-1).
```

Here `t,s` are initial and final packet ranks. `K,M` are computed from the
actual fusion-stage and M3 batch-plan certificates, not free witnesses or
counts of all `d` letters. At a fusion stage with gap `f`, the certificate
uses at most one batch (zero if `f=0`), exactly `f` hole transfers, and at
most `3*n+f` letters. Rank drops by one, so the holes before event `j` are
`n-t+j`. The result is an upper bound, not a shortest-word theorem.

Rank-one endpoints use a phase-only M3 plan; zero-event reference words
use an empty fusion plan. The earlier coarse interfaces remain available
in `ReplayInduction.lean` and `EndpointAlignment.lean`.

[M4_BUDGET_THEOREM_MAP.md](../M4_BUDGET_THEOREM_MAP.md) gives the theorem
owners and exact semantic boundary.

## Reproduce

From the parent directory:

```text
python -B validation/replay_m4.py
```

For a first dependency download, add `--cache`. The launcher uses the
canonical pinned toolchain, checks M3 and M4 source identities, builds the
extension and checks 34 targeted transitive axiom sets. A new receipt can be
saved with `--report results/my-m4-replay.json`; existing files are not
overwritten. Local testing used copied warm dependencies, not an independent
cold replay.

The equivalent direct commands, from this directory, are:

```text
lake exe cache get
lake build
lake env lean FusionLogReplay/AxiomAudit.lean
```

## Remaining M4 obligations

This stage does not yet close M4 on the full manuscript domain. The next
mathematical interface is:

1. Transport arbitrary finite atom labels and arbitrary eligible initial
   packet cycles into the routing/admission argument, without assuming the
   original atoms already carry the canonical `ZMod n` source order.

The converse from formal admissible schedules, Section 5's joint counts,
and the all-R optimum are separate formalization targets. Nothing in this
stage relabels them as already machine-proved.
