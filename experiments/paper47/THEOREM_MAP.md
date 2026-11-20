# Paper XLVII theorem-to-source map

All declarations below are in namespace `RSR2History`. Links resolve into
the selected standalone Lake root. Exact types are printed by the four
signature menus and retained in the full local replay receipt.

| Manuscript | Exact declarations | Source owner |
|---|---|---|
| Lemma 3.1 / Theorem 3.2 | `silent_reachable_iff_cyclic_signatures`; `cyclic_event_path_iff_joint_realizable` | [SilentPreparation](lean/RSR2History/SilentPreparation.lean), [CyclicEventPath](lean/RSR2History/CyclicEventPath.lean) |
| Proposition 3.3 | `history_fiber_guarded_quadratic_bound`; `history_compression_quadratic_length_le_min` | [QuadraticHistoryCompression](lean/RSR2History/QuadraticHistoryCompression.lean) |
| Lemma 4.2 | `singleBlockPartitionDistance_exact` | [SingleBlockPartitionCost](lean/RSR2History/SingleBlockPartitionCost.lean) |
| Theorem 4.3 | `delayedChain_history_distance_exact`; dependency `delayedChain_exact_cost` gives the actual attaining word and matching lower bound | [DelayedChainExactCost](lean/RSR2History/DelayedChainExactCost.lean) |
| Equation (4.5) and attainment | `delayedChainTotalPremiumMaximum_eq`; `delayedChainTotalPremiumMaximum_attained` | [DelayedFamilyPremium](lean/RSR2History/DelayedFamilyPremium.lean) |
| Theorem 5.4 | `singleBlock_packed_minimum_historyDistance`; dependency `singleBlock_packed_minimum_replay_exact` retains the actual word and cost split | [PackedLowerMinimum](lean/RSR2History/PackedLowerMinimum.lean) |
| Theorem 6.3 | `packedLowerCost_le_extraction_add_fusions`; `packedLowerCost_le_max_add_fusions` | [PackedLowerFusionElimination](lean/RSR2History/PackedLowerFusionElimination.lean) |
| Theorem 7.2 | `singleBlock_partitionTotalPremiumMaximum_eq_delayed`; `singleBlock_totalPremium_le_delayed`; `singleBlock_prefusion_delayed_slack`; `singleBlock_prefusion_delayed_gap` | [SingleBlockFusionElimination](lean/RSR2History/SingleBlockFusionElimination.lean) |
| Theorem 7.3 | `singleBlock_delayed_extremal_conditions`; `singleBlock_nTransfer_extraction_slack` | [SingleBlockFusionElimination](lean/RSR2History/SingleBlockFusionElimination.lean), [SingletonExtractionDefect](lean/RSR2History/SingletonExtractionDefect.lean) |
| Lemma 8.1 / Lemma A.1 | `ForestTerminalSource.terminal_route_moment`; `UpperReservedReplay.gapMoment_eq_root`; `forest_terminal_moment_account_of_trace` | [ForestGapMomentRouting](lean/RSR2History/ForestGapMomentRouting.lean), [ForestRootGapBridge](lean/RSR2History/ForestRootGapBridge.lean) |
| Lemma 8.2 | `forestStructuralDefect_eq_zero_iff`; `forestStructuralDefect_lower_bound`; `ForestReplayAccount.structural_replay_winding_budget`; actual existence via `forest_structural_replay_account_of_trace` | [ForestStructuralDefect](lean/RSR2History/ForestStructuralDefect.lean), [ForestStructuralReplay](lean/RSR2History/ForestStructuralReplay.lean) |
| Lemma 8.3 | `UpperCursorSchedule.forest_windings_add_two_le_events`; `UpperCursorSchedule.forest_final_phase_ge_of_max_windings`; `UpperCursorSchedule.forest_winding_phase_payment` | [ForestWindingBudget](lean/RSR2History/ForestWindingBudget.lean), [ForestWindingReplay](lean/RSR2History/ForestWindingReplay.lean) |
| Theorem 8.4, fused rank and full-rank branches | `allUpper_singleton_fused_forest_delayed_replay`; `ForestReplayAccount.replay_length_lt_delayed_of_full_rank`; `allUpper_singleton_extraction_slack` | [ForestWindingReplay](lean/RSR2History/ForestWindingReplay.lean), [ForestFullRankReplay](lean/RSR2History/ForestFullRankReplay.lean), [ForestRelativeReplay](lean/RSR2History/ForestRelativeReplay.lean) |
| Theorem 8.4, maximum across all ranks | `allUpperSingleton_delayed_maximum_attained`; `allUpperSingletonTotalPremiumMaximum_eq_delayed` | [AllUpperSingletonExtrema](lean/RSR2History/AllUpperSingletonExtrema.lean) |
| Theorem 8.5, actual packed witness and scalar comparison | `allUpper_packed_forest_replay_account`; `packedForest_fused_budget`; `packedForest_unfused_budget`; `PackedForestReplayAccount.length_le_partition_add_delayed` | [PackedForestReplay](lean/RSR2History/PackedForestReplay.lean), [PackedForestBudget](lean/RSR2History/PackedForestBudget.lean), [PackedForestRelativeReplay](lean/RSR2History/PackedForestRelativeReplay.lean) |
| Theorem 8.5, exact all-upper maximum | `allUpper_totalPremium_le_delayed`; `allUpperTotalPremiumMaximum_eq_delayed`; `allUpperTotalPremiumMaximum_eq` | [PackedForestRelativeReplay](lean/RSR2History/PackedForestRelativeReplay.lean) |
| Corollary 9.1 | `delayed_counterexample_has_lower_survivor` | [PackedForestRelativeReplay](lean/RSR2History/PackedForestRelativeReplay.lean) |

## Proof spine

```text
actual guarded executor + complete ordered events
  -> cyclic realization / quadratic execution foundations
  -> exact delayed family                    [lower bound]
  -> upper reservation/cursor + packed lower simulation
  -> first-fusion erasure/shadow elimination  [upper bound]
  -> exact entire one-block amplitude and necessary extremal structure
actual terminal forest + surviving cursor anchor
  -> named physical source + common dominating cut
  -> displacement-sensitive silent route + physical root-gap moment
  -> joint structural defect + phase-aware shared winding charge
  -> singleton forest relative replay across all terminal ranks
  -> exact all-upper singleton maximum
  -> packed actual replay + lower fusion elimination
  -> exact all-upper maximum for arbitrary transferred packets
  -> any larger global premium has multiple blocks and a lower survivor
```

The forest comparison uses the terminal route, joint winding payment and
`partitionDistance_lower_bound_of_rank_drop` in
[FusionSourceRefill](lean/RSR2History/FusionSourceRefill.lean) on the same
partition. The all-upper exact maxima range across ranks; they do not
assert equality at each fixed rank or each individual partition. Equation
(9.3) is the manuscript's finite-maximum restatement of the audited
counterexample localization and attained delayed lower bound.

The lift-window argument is supported by
`ActualUpperBirthTrace.common_window` and
`DelayedUpperLoadingPrefix.loading_rotations_lower_bound` in
[UpperLoadingWindow](lean/RSR2History/UpperLoadingWindow.lean).
The lower simulation's exact state/log round trip is in
[PackedLowerShadow](lean/RSR2History/PackedLowerShadow.lean), used by
`firstFusionRefinedLog_lift`. The actual forest route derives its inputs;
it does not expose an unexplained coordinate or `hbudget` premise.

## Audit menus and identity

- [25 one-block targets](lean/ClosedAudit.lean) and [signatures](lean/ClosedSignatures.lean).
- [57 moment-route targets](lean/RSR2History/ForestGapMomentAudit.lean) and [signatures](lean/RSR2History/ForestGapMomentSignatures.lean).
- [34 joint-forest targets](lean/RSR2History/ForestRelativeReplayAudit.lean) and [signatures](lean/RSR2History/ForestRelativeReplaySignatures.lean).
- [25 all-upper targets](lean/RSR2History/AllUpperExtremaAudit.lean) and [signatures](lean/RSR2History/AllUpperExtremaSignatures.lean).

These are owning declaration menus, not four independent proofs of the
same result. They contain helper and conditional interface statements as
well as the final theorem entries. The manifest reports both the 141 menu
occurrences and the deduplicated declaration count; neither is a count of
independent mathematical contributions or of all transitive dependency nodes.

The selected-input manifest binds this map, the reader and its build receipt,
all 196 Lean files, the pinned toolchain/lock and the reproduction scripts.
The original one-block candidate's proof bytes are retained unchanged;
the new combined candidate adds the all-upper closure instead of rewriting
the old acceptance record. Candidate branch commits identify source snapshots;
no publication tag or archive identity is asserted here.
