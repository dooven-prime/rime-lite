import FutureEvent.RegisterablePlacementEquiv
import FutureEvent.RegisteredPlacementEquiv
import FutureEvent.PlacementSums

namespace FutureEvent

open RegisteredAbsorptionChains
open scoped BigOperators

variable {n : ℕ} [NeZero n]

theorem card_actual_registerable_placements (hn : 3 ≤ n) :
    Nat.card (RegisterablePlacements n) = n * (2 * n - 4).choose (n - 3) := by
  calc
    _ = Nat.card (RegisterableParams n) := (Nat.card_congr (registerablePlacementParamsEquiv hn)).symm
    _ = Fintype.card (RegisterableParams n) := Nat.card_eq_fintype_card
    _ = _ := card_registerableParams n hn

theorem card_actual_registerable_states (hn : 3 ≤ n) :
    Nat.card (RegisterableGeneratedStates n) = n * (2 * n - 4).choose (n - 3) := by
  rw [card_registerableGeneratedStates, card_actual_registerable_placements hn]

theorem card_actual_registered_placements_sum (hn : 3 ≤ n) :
    Nat.card (RegisteredNonterminalPlacements n) =
      n * ∑ i ∈ Finset.range (n - 2), (n - 2 - i) * (n + (i + 1) - 2).choose (i + 1) := by
  calc
    _ = Nat.card (RegisteredPlacementParams n) := (Nat.card_congr (registeredPlacementParamsEquiv hn)).symm
    _ = Fintype.card (RegisteredPlacementParams n) := Nat.card_eq_fintype_card
    _ = _ := card_registeredPlacementParams_sum n hn

theorem card_actual_registered_placements_additive (hn : 3 ≤ n) :
    Nat.card (RegisteredNonterminalPlacements n) + n * (n - 1) =
      2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) := by
  have hcard := Nat.card_congr (registeredPlacementParamsEquiv hn)
  rw [Nat.card_eq_fintype_card] at hcard
  rw [← hcard]
  exact card_registeredPlacementParams_additive n hn

theorem card_actual_registered_placements_paper_sum (hn : 3 ≤ n) :
    Nat.card (RegisteredNonterminalPlacements n) =
      n * ∑ k ∈ Finset.Icc 1 (n - 2), (n - 1 - k) * (n + k - 2).choose k := by
  rw [card_actual_registered_placements_sum hn, ← Finset.Ico_add_one_right_eq_Icc,
    Finset.sum_Ico_eq_sum_range]
  simp only [Nat.add_sub_cancel_right]
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  have ha : 1 + i = i + 1 := by omega
  have hb : n - 1 - (i + 1) = n - 2 - i := by omega
  rw [ha, hb]

theorem card_actual_registered_placements_closed (hn : 3 ≤ n) :
    Nat.card (RegisteredNonterminalPlacements n) =
      2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) - n * (n - 1) := by
  have h := card_actual_registered_placements_additive hn
  omega

theorem card_futureQuotient_additive (hn : 3 ≤ n) :
    Nat.card (FutureQuotient n) + n * (n - 1) =
      1 + n * (2 * n - 4).choose (n - 3) +
        2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) := by
  rw [card_futureQuotient_actual_regions hn, card_actual_registerable_states hn]
  have h := card_actual_registered_placements_additive hn
  omega

/-- The closed count concerns the all-word behavioral quotient of actual
generated states; its normal-form equivalence remains noncomputable. -/
theorem card_futureQuotient_closed (hn : 3 ≤ n) :
    Nat.card (FutureQuotient n) =
      1 + n * (2 * n - 4).choose (n - 3) +
        2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) - n * (n - 1) := by
  have h := card_futureQuotient_additive hn
  omega

end FutureEvent
