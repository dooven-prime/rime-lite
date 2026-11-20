import RSR2History.SingleBlockFusionElimination

/-! The one-block theorem leaves exactly the reachable multiblock fibers.
The split does not assert that multiblock maximizers are strictly smaller. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer

noncomputable def multiBlockPartitions (n : Nat) (hn : 1 < n) :
    Finset (AttainablePartition n hn) := by
  classical
  exact Finset.univ.filter (fun pi => 2 ≤ pi.val.card)

@[simp] theorem mem_multiBlockPartitions (n : Nat) (hn : 1 < n)
    (pi : AttainablePartition n hn) :
    pi ∈ multiBlockPartitions n hn ↔ 2 ≤ pi.val.card := by
  classical
  simp [multiBlockPartitions]

private theorem seed_blocks_card (n : Nat) :
    (unorderedPacketBlocks n (seed n)).card = n := by
  classical
  have he : unorderedPacketBlocks n (seed n) =
      Finset.univ.image (fun a : Fin n => ({a} : Finset (Fin n))) := by
    unfold unorderedPacketBlocks
    congr 1
    funext a
    ext b
    simp [seed]
  rw [he, Finset.card_image_of_injective]
  · simp
  · intro a b h
    simpa using h

theorem multiBlockPartitions_nonempty (n : Nat) (hn : 1 < n) :
    (multiBlockPartitions n hn).Nonempty := by
  let pi : AttainablePartition n hn :=
    ⟨unorderedPacketBlocks n (seed n), ⟨[], seed n, rfl, rfl⟩⟩
  refine ⟨pi, (mem_multiBlockPartitions n hn pi).mpr ?_⟩
  simpa only [pi, seed_blocks_card] using (show 2 ≤ n by omega)

noncomputable def multiBlockTotalPremiumMaximum (n : Nat) (hn : 1 < n) : Nat :=
  (multiBlockPartitions n hn).sup (partitionTotalPremiumMaximum n hn)

theorem partitionTotalPremiumMaximum_le_multiblock
    (n : Nat) (hn : 1 < n) (pi : AttainablePartition n hn)
    (hmulti : 2 ≤ pi.val.card) :
    partitionTotalPremiumMaximum n hn pi ≤ multiBlockTotalPremiumMaximum n hn :=
  Finset.le_sup ((mem_multiBlockPartitions n hn pi).mpr hmulti)

theorem multiBlockTotalPremiumMaximum_attained (n : Nat) (hn : 1 < n) :
    ∃ pi : AttainablePartition n hn, 2 ≤ pi.val.card ∧
      partitionTotalPremiumMaximum n hn pi = multiBlockTotalPremiumMaximum n hn := by
  classical
  obtain ⟨pi, hpi, he⟩ := Finset.exists_mem_eq_sup
    (multiBlockPartitions n hn) (multiBlockPartitions_nonempty n hn)
    (partitionTotalPremiumMaximum n hn)
  exact ⟨pi, (mem_multiBlockPartitions n hn pi).mp hpi, he.symm⟩

theorem multiBlockTotalPremiumMaximum_le_global (n : Nat) (hn : 1 < n) :
    multiBlockTotalPremiumMaximum n hn ≤ globalTotalObservationPremium n hn := by
  apply Finset.sup_le
  intro pi _
  exact partitionTotalPremiumMaximum_le_global n hn pi

/-- An actually reachable nonempty source partition cannot have zero blocks. -/
theorem attainablePartition_singleBlock_of_not_multiblock
    (n : Nat) (hn : 1 < n) (pi : AttainablePartition n hn)
    (hsmall : ¬ 2 ≤ pi.val.card) :
    pi = singleBlockAttainablePartition n hn := by
  classical
  obtain ⟨word, Q, hrun, hblocks⟩ := pi.property
  have cover : ∀ a : Fin n, ∃ B ∈ pi.val, a ∈ B := by
    intro a
    refine ⟨Finset.univ.filter (fun b => Q b = Q a), ?_, by simp⟩
    rw [← hblocks]
    exact Finset.mem_image.mpr ⟨a, Finset.mem_univ _, rfl⟩
  obtain ⟨B, hB, _⟩ := cover ⟨0, by omega⟩
  have hcard : pi.val.card = 1 := by
    have hp := Finset.card_pos.mpr ⟨B, hB⟩
    omega
  obtain ⟨B, hB⟩ := Finset.card_eq_one.mp hcard
  have hfull : B = Finset.univ := by
    apply Finset.eq_univ_of_forall
    intro a
    obtain ⟨C, hC, ha⟩ := cover a
    have hCB : C = B := by simpa [hB] using hC
    simpa only [hCB] using ha
  apply Subtype.ext
  simpa only [hfull, singleBlockAttainablePartition] using hB

section GlobalSplit
variable {n : Nat} [NeZero n]

theorem globalTotalObservationPremium_eq_delayed_max_multiblock (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) =
      max (delayedChainTotalPremiumMaximum n hn)
        (multiBlockTotalPremiumMaximum n (by omega)) := by
  apply le_antisymm
  · rw [globalTotalObservationPremium_eq_partition_sup]
    apply Finset.sup_le
    intro pi _
    by_cases hmulti : 2 ≤ pi.val.card
    · exact (partitionTotalPremiumMaximum_le_multiblock n (by omega) pi hmulti).trans
        (le_max_right _ _)
    · rw [attainablePartition_singleBlock_of_not_multiblock n (by omega) pi hmulti,
        singleBlock_partitionTotalPremiumMaximum_eq_delayed hn]
      exact le_max_left _ _
  · apply max_le
    · rw [← singleBlock_partitionTotalPremiumMaximum_eq_delayed hn]
      exact partitionTotalPremiumMaximum_le_global n (by omega) _
    · exact multiBlockTotalPremiumMaximum_le_global n (by omega)

theorem globalTotalObservationPremium_eq_delayed_iff_multiblock (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) = delayedChainTotalPremiumMaximum n hn ↔
      multiBlockTotalPremiumMaximum n (by omega) ≤ delayedChainTotalPremiumMaximum n hn := by
  rw [globalTotalObservationPremium_eq_delayed_max_multiblock hn]
  exact max_eq_left_iff

omit [NeZero n] in
theorem multiblock_bound_iff_partition_bounds (hn : 3 ≤ n) :
    multiBlockTotalPremiumMaximum n (by omega) ≤ delayedChainTotalPremiumMaximum n hn ↔
      ∀ pi : AttainablePartition n (by omega), 2 ≤ pi.val.card →
        partitionTotalPremiumMaximum n (by omega) pi ≤ delayedChainTotalPremiumMaximum n hn := by
  constructor
  · intro h pi hpi
    exact (partitionTotalPremiumMaximum_le_multiblock n (by omega) pi hpi).trans h
  · intro h
    apply Finset.sup_le
    intro pi hpi
    exact h pi ((mem_multiBlockPartitions n (by omega) pi).mp hpi)

/-- Any actual counterexample to delayed domination must end in at least two
packets. No strictness claim is made about observations attaining equality. -/
theorem delayed_counterexample_has_multiblock_endpoint
    (hn : 3 ≤ n) (observation : AttainableObservation n (by omega))
    (hbad : delayedChainTotalPremiumMaximum n hn <
      totalObservationPremium n (by omega) observation) :
    2 ≤ (unorderedPacketBlocks n observation.val.1).card := by
  let pi : AttainablePartition n (by omega) :=
    ⟨unorderedPacketBlocks n observation.val.1,
      partition_attainable_of_endpoint n (by omega) observation.val.1
        (endpoint_attainable_of_logged (by omega) observation.property)⟩
  by_contra hsmall
  have hsingle := attainablePartition_singleBlock_of_not_multiblock n (by omega) pi hsmall
  have hle := totalObservationPremium_le_partitionMaximum n (by omega) observation
  change totalObservationPremium n (by omega) observation ≤
    partitionTotalPremiumMaximum n (by omega) pi at hle
  rw [hsingle, singleBlock_partitionTotalPremiumMaximum_eq_delayed hn] at hle
  omega

end GlobalSplit
end RSR2History
