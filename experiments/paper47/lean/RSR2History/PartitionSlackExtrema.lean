import RSR2History.PartitionRelativeCompression

/-!
Exact signed slack minima, and the one-block subproblem of delayed-family
domination. No reverse bound on arbitrary event histories is assumed here.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

theorem partitionDistance_le_partitionHistoryMaximum
    (n : Nat) (hn : 1 < n) (π : AttainablePartition n hn) :
    partitionDistance n hn π.val π.property ≤ partitionHistoryMaximum n hn π := by
  obtain ⟨Q, H, attain, hπ, hcost⟩ :=
    partitionDistance_historyCost_attained n hn π.val π.property
  exact hcost ▸ historyDistance_le_partitionHistoryMaximum n hn π ⟨⟨(Q, H), attain⟩, hπ⟩

/-- There is no truncated subtraction in the integer slack formula. -/
theorem partitionRelativeSlack_eq_budget_sub_amplitude
    (n : Nat) (hn : 1 < n) (budget : Nat) (π : AttainablePartition n hn) :
    partitionRelativeSlack n hn budget π =
      (budget : Int) - (partitionTotalPremiumMaximum n hn π : Int) := by
  have hle := partitionDistance_le_partitionHistoryMaximum n hn π
  unfold partitionRelativeSlack partitionTotalPremiumMaximum
  rw [Int.ofNat_sub hle]
  omega

/-- The actual finite, nonempty set of signed partition slacks. -/
noncomputable def partitionSlackValues (n : Nat) (hn : 1 < n) (budget : Nat) :
    Finset Int := by
  classical
  exact Finset.univ.image (partitionRelativeSlack n hn budget)

theorem partitionSlackValues_nonempty (n : Nat) (hn : 1 < n) (budget : Nat) :
    (partitionSlackValues n hn budget).Nonempty := by
  classical
  obtain ⟨π⟩ := attainablePartition_nonempty n hn
  exact ⟨_, Finset.mem_image.mpr ⟨π, Finset.mem_univ _, rfl⟩⟩

/-- Integer minimum over reachable partition fibers, including negative
values when the proposed budget underestimates the true global maximum. -/
noncomputable def minimumPartitionSlack (n : Nat) (hn : 1 < n) (budget : Nat) : Int :=
  (partitionSlackValues n hn budget).min' (partitionSlackValues_nonempty n hn budget)

theorem minimumPartitionSlack_le (n : Nat) (hn : 1 < n) (budget : Nat)
    (π : AttainablePartition n hn) :
    minimumPartitionSlack n hn budget ≤ partitionRelativeSlack n hn budget π := by
  classical
  exact Finset.min'_le _ _ (Finset.mem_image.mpr ⟨π, Finset.mem_univ _, rfl⟩)

/-- Exact minimum, for budgets below, at, or above `J_n`. -/
theorem minimumPartitionSlack_eq (n : Nat) (hn : 1 < n) (budget : Nat) :
    minimumPartitionSlack n hn budget =
      (budget : Int) - (globalTotalObservationPremium n hn : Int) := by
  classical
  apply le_antisymm
  · obtain ⟨π, hmax⟩ := globalTotalObservationPremium_partition_attained n hn
    have hle := minimumPartitionSlack_le n hn budget π
    rwa [partitionRelativeSlack_eq_budget_sub_amplitude, hmax] at hle
  · apply Finset.le_min'
    intro value hvalue
    obtain ⟨π, _, rfl⟩ := Finset.mem_image.mp hvalue
    rw [partitionRelativeSlack_eq_budget_sub_amplitude]
    have hle := partitionTotalPremiumMaximum_le_global n hn π
    omega

theorem minimumPartitionSlack_attained (n : Nat) (hn : 1 < n) (budget : Nat) :
    ∃ π : AttainablePartition n hn,
      partitionRelativeSlack n hn budget π = minimumPartitionSlack n hn budget := by
  classical
  obtain ⟨π, _, hπ⟩ := Finset.mem_image.mp
    (Finset.min'_mem (partitionSlackValues n hn budget)
      (partitionSlackValues_nonempty n hn budget))
  exact ⟨π, hπ⟩

/-- Slack minimizers are exactly the partitions attaining the global cost
amplitude. This equivalence is independent of the chosen budget. -/
theorem partitionRelativeSlack_eq_minimum_iff
    (n : Nat) (hn : 1 < n) (budget : Nat) (π : AttainablePartition n hn) :
    partitionRelativeSlack n hn budget π = minimumPartitionSlack n hn budget ↔
      partitionTotalPremiumMaximum n hn π = globalTotalObservationPremium n hn := by
  rw [partitionRelativeSlack_eq_budget_sub_amplitude, minimumPartitionSlack_eq]
  omega

/-- The reachable one-block partition, with no layer or site retained. -/
def singleBlockAttainablePartition (n : Nat) (hn : 1 < n) : AttainablePartition n hn :=
  ⟨{Finset.univ}, singleBlockPartition_attainable n hn⟩

/-- An attaining delayed chain already lies in the one-block fiber. Thus
that fiber's amplitude is at least the restricted delayed maximum. -/
theorem delayedMaximum_le_singleBlockAmplitude
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn ≤
      partitionTotalPremiumMaximum n (by omega)
        (singleBlockAttainablePartition n (by omega)) := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := delayedChainTotalPremiumMaximum_attained hn
  let obs : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩, delayedUpperChainLog z),
      delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩
  have hpart : unorderedPacketBlocks n obs.val.1 = {Finset.univ} :=
    unorderedPacketBlocks_constant n (by omega) _
  have hle := totalObservationPremium_le_partitionMaximum n (by omega) obs
  rw [hmax] at hle
  simpa [singleBlockAttainablePartition, hpart] using hle

theorem singleBlock_delayedSlack_nonpos
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    partitionRelativeSlack n (by omega) (delayedChainTotalPremiumMaximum n hn)
      (singleBlockAttainablePartition n (by omega)) ≤ 0 := by
  rw [partitionRelativeSlack_eq_budget_sub_amplitude]
  have hle := delayedMaximum_le_singleBlockAmplitude hn
  omega

theorem minimumPartitionSlack_delayed_nonpos
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    minimumPartitionSlack n (by omega) (delayedChainTotalPremiumMaximum n hn) ≤ 0 := by
  exact (minimumPartitionSlack_le _ _ _ _).trans (singleBlock_delayedSlack_nonpos hn)

/-- Single-block domination is precisely the sharp upper bound posed for
all one-block histories. This equivalence does not prove that bound. -/
theorem singleBlock_delayedSlack_zero_iff_upper_bound
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    partitionRelativeSlack n (by omega) (delayedChainTotalPremiumMaximum n hn)
        (singleBlockAttainablePartition n (by omega)) = 0 ↔
      partitionHistoryMaximum n (by omega) (singleBlockAttainablePartition n (by omega)) ≤
        (2 * n - 3) + delayedChainTotalPremiumMaximum n hn := by
  have hnonpos := singleBlock_delayedSlack_nonpos hn
  have he := singleBlock_partitionDistance_exact n (by omega)
    (singleBlockPartition_attainable n (by omega))
  have he' : partitionDistance n (by omega)
      (singleBlockAttainablePartition n (by omega)).val
      (singleBlockAttainablePartition n (by omega)).property = 2 * n - 3 := he
  rw [← he', ← partitionRelativeSlack_nonneg_iff]
  omega

end RSR2History
