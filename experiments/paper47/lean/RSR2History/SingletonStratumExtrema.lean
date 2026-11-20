import RSR2History.SingleBlockSingletonCursor

/-! The exact maximum over the entire actual n-transfer one-block stratum. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer

noncomputable def singletonStratumObservations (n : Nat) (hn : 1 < n) :
    Finset (AttainableObservation n hn) := by
  classical
  exact Finset.univ.filter (fun o =>
    unorderedPacketBlocks n o.val.1 = {Finset.univ} ∧ logTransferCount o.val.2 = n)

noncomputable def singletonStratumTotalPremiumMaximum (n : Nat) (hn : 1 < n) : Nat :=
  (singletonStratumObservations n hn).sup (totalObservationPremium n hn)

theorem mem_singletonStratumObservations (o : AttainableObservation n hn) :
    o ∈ singletonStratumObservations n hn ↔
      unorderedPacketBlocks n o.val.1 = {Finset.univ} ∧ logTransferCount o.val.2 = n := by
  classical
  simp [singletonStratumObservations]

theorem singletonStratumTotalPremiumMaximum_le_delayed {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    singletonStratumTotalPremiumMaximum n (by omega) ≤ delayedChainTotalPremiumMaximum n hn := by
  apply Finset.sup_le
  intro o ho
  obtain ⟨hb, ht⟩ := (mem_singletonStratumObservations o).mp ho
  obtain ⟨word, hw⟩ := o.property
  exact singleBlock_nTransfer_delayed_domination hn word hw hb ht

theorem singletonStratum_delayed_maximum_attained {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    ∃ o : AttainableObservation n (Nat.lt_of_lt_of_le (by decide : 1 < 3) hn),
      o ∈ singletonStratumObservations n (Nat.lt_of_lt_of_le (by decide : 1 < 3) hn) ∧
      totalObservationPremium n (Nat.lt_of_lt_of_le (by decide : 1 < 3) hn) o =
        delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := delayedChainTotalPremiumMaximum_attained hn
  let o : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint ⟨n-1, by omega⟩, delayedUpperChainLog z),
      delayedChain_attainable hn hlen hnodup ⟨n-1, by omega⟩⟩
  refine ⟨o, (mem_singletonStratumObservations o).mpr ⟨?_, ?_⟩, hmax⟩
  · exact unorderedPacketBlocks_constant n (by omega) _
  · simpa only [o, delayedUpperChainLog_transfer_count] using hlen

theorem singletonStratumTotalPremiumMaximum_eq_delayed {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    singletonStratumTotalPremiumMaximum n (by omega) = delayedChainTotalPremiumMaximum n hn := by
  apply le_antisymm (singletonStratumTotalPremiumMaximum_le_delayed hn)
  obtain ⟨o, ho, he⟩ := singletonStratum_delayed_maximum_attained hn
  rw [← he]
  exact Finset.le_sup ho

theorem singletonStratumTotalPremiumMaximum_eq {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    singletonStratumTotalPremiumMaximum n (by omega) =
      (5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) - n + 2 := by
  rw [singletonStratumTotalPremiumMaximum_eq_delayed hn, delayedChainTotalPremiumMaximum_eq n hn]

end RSR2History
