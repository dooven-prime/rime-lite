import RSR2History.ForestRelativeReplay
import RSR2History.MultiBlockPartitionExtrema

/-! The exact maximum over all upper singleton-transfer observations, including
every terminal rank, and localization of any violation of delayed domination. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

def IsAllUpperSingleton {n : Nat} {hn : 1 < n}
    (o : AttainableObservation n hn) : Prop :=
  (∀ a, (o.val.1 a).1 = true) ∧
    ∀ B, .transfer B ∈ o.val.2 → B.card = 1

noncomputable def allUpperSingletonObservations (n : Nat) (hn : 1 < n) :
    Finset (AttainableObservation n hn) := by
  classical
  exact Finset.univ.filter IsAllUpperSingleton

@[simp] theorem mem_allUpperSingletonObservations (o : AttainableObservation n hn) :
    o ∈ allUpperSingletonObservations n hn ↔ IsAllUpperSingleton o := by
  classical
  simp [allUpperSingletonObservations]

noncomputable def allUpperSingletonTotalPremiumMaximum (n : Nat) (hn : 1 < n) : Nat :=
  (allUpperSingletonObservations n hn).sup (totalObservationPremium n hn)

theorem allUpperSingleton_totalPremium_le_delayed {n : Nat} [NeZero n]
    (hn : 3 ≤ n) (o : AttainableObservation n (by omega))
    (h : IsAllUpperSingleton o) :
    totalObservationPremium n (by omega) o ≤ delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨word, hw⟩ := o.property
  exact (Nat.le_add_right _ _).trans
    (allUpper_singleton_extraction_slack hn (by omega) word hw h.1 h.2)

private theorem not_transfer_mem_orderedUpperFusionLog {n : Nat}
    (B carrier : Finset (Fin n)) (z : List (Fin n)) :
    EffectiveEvent.transfer B ∉ orderedUpperFusionLog carrier z := by
  induction z generalizing carrier with
  | nil => simp [orderedUpperFusionLog]
  | cons a z ih => simp [orderedUpperFusionLog, ih]

theorem delayedUpperChainLog_transfer_card {n : Nat} (z : List (Fin n))
    {B : Finset (Fin n)} (h : EffectiveEvent.transfer B ∈ delayedUpperChainLog z) :
    B.card = 1 := by
  rcases List.mem_append.mp h with h | h
  · obtain ⟨a, _, he⟩ := List.mem_map.mp h
    simpa using congrArg Finset.card (EffectiveEvent.transfer.inj he).symm
  · cases z with
    | nil => simp [delayedUpperFusionLog] at h
    | cons a z => exact (not_transfer_mem_orderedUpperFusionLog B {a} z h).elim

theorem allUpperSingleton_delayed_maximum_attained {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    ∃ o : AttainableObservation n (by omega), IsAllUpperSingleton o ∧
      totalObservationPremium n (by omega) o = delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := delayedChainTotalPremiumMaximum_attained hn
  let o : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint ⟨n-1, by omega⟩, delayedUpperChainLog z),
      delayedChain_attainable hn hlen hnodup ⟨n-1, by omega⟩⟩
  exact ⟨o, ⟨fun _ => rfl, fun _ => delayedUpperChainLog_transfer_card z⟩, hmax⟩

theorem allUpperSingletonTotalPremiumMaximum_eq_delayed {n : Nat} [NeZero n]
    (hn : 3 ≤ n) :
    allUpperSingletonTotalPremiumMaximum n (by omega) = delayedChainTotalPremiumMaximum n hn := by
  apply le_antisymm
  · exact Finset.sup_le fun o ho =>
      allUpperSingleton_totalPremium_le_delayed hn o ((mem_allUpperSingletonObservations o).mp ho)
  · obtain ⟨o, ho, hmax⟩ := allUpperSingleton_delayed_maximum_attained hn
    rw [← hmax]
    exact Finset.le_sup ((mem_allUpperSingletonObservations o).mpr ho)

theorem allUpperSingletonTotalPremiumMaximum_eq {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    allUpperSingletonTotalPremiumMaximum n (by omega) =
      (5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) - n + 2 := by
  rw [allUpperSingletonTotalPremiumMaximum_eq_delayed hn, delayedChainTotalPremiumMaximum_eq n hn]

/-- A counterexample must be multiblock and must either have a lower survivor
or record an actual transfer of at least two atoms. -/
theorem delayed_counterexample_has_lower_survivor_or_packed_transfer
    {n : Nat} [NeZero n] (hn : 3 ≤ n) (o : AttainableObservation n (by omega))
    (hbad : delayedChainTotalPremiumMaximum n hn < totalObservationPremium n (by omega) o) :
    2 ≤ (unorderedPacketBlocks n o.val.1).card ∧
      ((∃ a, (o.val.1 a).1 = false) ∨
        ∃ B, .transfer B ∈ o.val.2 ∧ 2 ≤ B.card) := by
  classical
  refine ⟨delayed_counterexample_has_multiblock_endpoint hn o hbad, ?_⟩
  by_cases hlow : ∃ a, (o.val.1 a).1 = false
  · exact Or.inl hlow
  · right
    by_contra hpacked
    obtain ⟨word, hw⟩ := o.property
    have hu : ∀ a, (o.val.1 a).1 = true := by
      intro a
      cases ha : (o.val.1 a).1
      · exact (hlow ⟨a, ha⟩).elim
      · rfl
    have hs : ∀ B, .transfer B ∈ o.val.2 → B.card = 1 := by
      intro B hB
      have hpos := Finset.card_pos.mpr (runLogged_transfer_nonempty n (by omega) word hw B hB)
      have hsmall : ¬ 2 ≤ B.card := fun h => hpacked ⟨B, hB, h⟩
      omega
    exact (not_lt_of_ge (allUpperSingleton_totalPremium_le_delayed hn o ⟨hu, hs⟩)) hbad

end RSR2History
