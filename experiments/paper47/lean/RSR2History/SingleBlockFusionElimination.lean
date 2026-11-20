import RSR2History.PackedLowerFusionElimination
import RSR2History.PackedLowerAmortization
import RSR2History.SingleBlockStrictGaps
import RSR2History.SingletonExtractionDefect
import RSR2History.PartitionSlackExtrema

/-!
First-fusion elimination closes the packed lower amortization estimate.
Combined with the existing same-observation cursor replay, lower prefusion
strictly reduces the one-block history benchmark. No event order is exchanged
and no external word-budget hypothesis is used.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

private theorem twice_choose_two (r : Nat) : 2*r.choose 2 = r*(r-1) := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self r
  rw [Nat.choose_two_right]
  omega

/-- The upper budget saved by prefusion pays for fusion elimination and
leaves this additional nonnegative gap. -/
theorem packedFusionElimination_budget_balance {n t : Nat}
    (ht : 2 ≤ t) (htn : t ≤ n) :
    (n-t)*(5*n+t+1)/2 = (2*n-1)*(n-t) +
      ((n-t)*(n+1) - (n-t).choose 2) := by
  have hrn : n-t ≤ n := by omega
  have hc := twice_choose_two (n-t)
  have hsmall : (n-t).choose 2 ≤ (n-t)*(n+1) := by
    have hpred : n-t-1 ≤ n := by omega
    nlinarith
  have hsub := Nat.sub_add_cancel hsmall
  have hrelease := packedUpperBudget_release_prefusions ht htn
  have hpaid : 1 ≤ 2*n := by omega
  have hpaid := Nat.sub_add_cancel hpaid
  have hreleaseSub : (n-t).choose 2 ≤ 3*n*(n-t) := by nlinarith
  have hreleaseSub := Nat.sub_add_cancel hreleaseSub
  rw [hrelease]
  nlinarith

/-- A genuine lower prefusion leaves at least `n+1` units of strict margin.
This is a budget consequence of the proved `2*n-1` elimination cost. -/
theorem packedFusionElimination_gap_lower_bound {n t : Nat}
    (ht : 2 ≤ t) (hlt : t < n) :
    n+1 ≤ (n-t)*(n+1) - (n-t).choose 2 := by
  have hr : 1 ≤ n-t := by omega
  have hrn : n-t ≤ n := by omega
  have hp := Nat.sub_add_cancel hr
  have hc := twice_choose_two (n-t)
  have hchoose : (n-t).choose 2 ≤ (n-t-1)*(n+1) := by nlinarith
  have hmul : (n-t)*(n+1) = (n+1)+(n-t-1)*(n+1) := by nlinarith
  omega

@[simp] theorem logFusionCount_packedLowerLog (H : List (EffectiveEvent n)) :
    logFusionCount (packedLowerLog H) = logLayerFusionCount false H := by
  induction H with
  | nil => rfl
  | cons e H ih =>
      cases e with
      | fusion layer A B C => cases layer <;> simpa [logFusionCount, logLayerFusionCount] using ih
      | transfer B => simpa [logFusionCount, logLayerFusionCount] using ih

section ActualHistory
variable {n : Nat} [NeZero n]

omit [NeZero n] in
/-- The independent packed minimum of this actual one-block history is
bounded solely by its number of lower effective fusions. -/
theorem singleBlock_packedLowerCost_fusion_bound
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 0 < logTransferCount H) :
    packedLowerCost n (by omega) (packedLowerLog H) ≤
      maxLowerExtractionCost n (by omega) + (2*n-1)*(n-logTransferCount H) := by
  have path := singleBlock_packedLowerCost_attained n (by omega) word hexec hblocks ht
  have bound := packedLowerCost_le_max_add_fusions path
  have hcount := (singleBlock_positiveTransfer_shape n (by omega) word hexec hblocks ht).2.2.1
  simpa only [logFusionCount_packedLowerLog, hcount] using bound

/-- Complete-log replay and lower fusion elimination leave a quantitative
gap below the delayed-family benchmark. The tree is the original history's
actual upper forest, rather than a newly chosen history. -/
theorem singleBlock_prefusion_delayed_slack
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ T : UpperFusionTree n,
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ +
        T.leftBranchDefect + T.initialCursorSlack +
        ((n-logTransferCount H)*(n+1) - (n-logTransferCount H).choose 2) ≤
          delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, trace, hdist⟩ :=
    singleBlock_packed_minimum_historyDistance (by omega) word hexec hblocks ht
  have hlower := singleBlock_packedLowerCost_fusion_bound hn word hexec hblocks (by omega)
  have htn := singleton_transfer_count_le n (by omega) hexec
  have hrelease := packedUpperBudget_release ht htn
  have hbalance := packedFusionElimination_budget_balance ht htn
  have hpremium := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hmaximum := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn
  exact ⟨T, trace, by omega⟩

/-- Every actual prefused one-block history with at least two transfers is
strictly below the delayed benchmark, by at least `n+1`. -/
theorem singleBlock_prefusion_delayed_gap
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) (hlt : logTransferCount H < n) :
    totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ + (n+1) ≤
      delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, trace, bound⟩ := singleBlock_prefusion_delayed_slack hn word hexec hblocks ht
  have hgap := packedFusionElimination_gap_lower_bound ht hlt
  omega

/-- All transfer strata of a final single packet are now dominated by the
same delayed-family maximum. -/
theorem singleBlock_totalPremium_le_delayed
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ ≤
      delayedChainTotalPremiumMaximum n hn := by
  by_cases hzero : logTransferCount H = 0
  · exact singleBlock_noTransfer_totalPremium_le_delayed hn word hexec hblocks hzero
  by_cases hone : logTransferCount H = 1
  · exact (singleBlock_oneTransfer_delayed_gap hn word hexec hblocks hone).2.le
  obtain ⟨T, trace, bound⟩ :=
    singleBlock_prefusion_delayed_slack hn word hexec hblocks (by omega)
  omega

/-- The complete one-block partition fiber has exactly the delayed-family
cost amplitude, including every lower prefusion and transfer interleaving. -/
theorem singleBlock_partitionTotalPremiumMaximum_eq_delayed
    (hn : 3 ≤ n) :
    partitionTotalPremiumMaximum n (by omega)
      (singleBlockAttainablePartition n (by omega)) =
        delayedChainTotalPremiumMaximum n hn := by
  apply le_antisymm
  · obtain ⟨observation, hmax⟩ := partitionHistoryMaximum_attained n (by omega)
      (singleBlockAttainablePartition n (by omega))
    obtain ⟨word, hexec⟩ := observation.val.property
    have hblocks : unorderedPacketBlocks n observation.val.val.1 = {Finset.univ} :=
      observation.property
    have bound := singleBlock_totalPremium_le_delayed hn word hexec hblocks
    have balance := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
    have hpart := singleBlock_partitionDistance_exact n (by omega)
      (singleBlockAttainablePartition n (by omega)).property
    have hpart' : partitionDistance n (by omega)
        (singleBlockAttainablePartition n (by omega)).val
        (singleBlockAttainablePartition n (by omega)).property = 2*n-3 := hpart
    rw [hmax] at balance
    unfold partitionTotalPremiumMaximum
    rw [hpart']
    omega
  · exact delayedMaximum_le_singleBlockAmplitude hn

/-- The signed one-block slack is zero. This establishes only the one-block
fiber, not the corresponding open upper bound on all packet partitions. -/
theorem singleBlock_delayedSlack_zero (hn : 3 ≤ n) :
    partitionRelativeSlack n (by omega) (delayedChainTotalPremiumMaximum n hn)
      (singleBlockAttainablePartition n (by omega)) = 0 := by
  rw [partitionRelativeSlack_eq_budget_sub_amplitude,
    singleBlock_partitionTotalPremiumMaximum_eq_delayed hn]
  simp

/-- A benchmark-attaining one-block history cannot contain a lower fusion.
All singleton transfer, tree and extraction conditions refer to the same log. -/
theorem singleBlock_delayed_extremal_conditions
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hmax : totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ =
      delayedChainTotalPremiumMaximum n hn) :
    logTransferCount H = n ∧
      (∃ T : UpperFusionTree n, UpperForestTrace (seed n) 0 [] H Q n [T] ∧
        T.IsLeftComb ∧ T.leaves.idxOf 0 = 0) ∧
      lowerExtractionCost n (by omega) (singletonTransferOrder H) =
        maxLowerExtractionCost n (by omega) := by
  have htn := singleton_transfer_count_le n (by omega) hexec
  have ht : logTransferCount H = n := by
    by_cases hzero : logTransferCount H = 0
    · have gap := (singleBlock_noTransfer_delayed_gap hn word hexec hblocks hzero).2
      omega
    by_cases hone : logTransferCount H = 1
    · have gap := (singleBlock_oneTransfer_delayed_gap hn word hexec hblocks hone).2
      omega
    by_contra hne
    have gap := singleBlock_prefusion_delayed_gap hn word hexec hblocks (by omega) (by omega)
    omega
  exact ⟨ht, singleBlock_nTransfer_extremal_extraction hn word hexec hblocks ht hmax⟩

end ActualHistory
end RSR2History
