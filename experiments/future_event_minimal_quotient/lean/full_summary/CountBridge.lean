import full_summary.Quotient
import FutureEvent.ClosedQuotientCount
import RegisteredAbsorptionChains.TotalCountFormula

namespace FullSummary

open RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

/-- The observer's registered normal form and the counting owner's actual
summary type retain the identical execution, with the same seed provenance. -/
def registeredStatesEquivActualSummaries :
    RegisteredGeneratedStates n ≃ ActualRegisteredSummaries n where
  toFun x := ⟨x.val.val, x.val.property, x.property⟩
  invFun x := ⟨⟨x.val, x.property.1⟩, x.property.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

noncomputable def fullQuotientEquivSummaries (hn : 3 ≤ n) :
    FullQuotient n ≃ Unit ⊕ (RegisterablePlacements n ⊕ ActualRegisteredSummaries n) :=
  (fullQuotientEquivNormalForms hn).trans
    (Equiv.sumCongr (Equiv.refl _) (Equiv.sumCongr (Equiv.refl _)
      registeredStatesEquivActualSummaries))

theorem finite_fullQuotient (hn : 3 ≤ n) : Finite (FullQuotient n) := by
  haveI : Fact (3 ≤ n) := ⟨hn⟩
  exact Finite.of_injective (fullQuotientEquivSummaries hn) (fullQuotientEquivSummaries hn).injective

theorem card_fullQuotient_actual_counts (hn : 3 ≤ n) :
    Nat.card (FullQuotient n) =
      1 + Nat.card (RegisterableGeneratedStates n) + Nat.card (ActualRegisteredSummaries n) := by
  haveI : Fact (3 ≤ n) := ⟨hn⟩
  rw [Nat.card_congr (fullQuotientEquivSummaries hn), card_registerableGeneratedStates]
  simp only [Nat.card_sum, Nat.card_eq_fintype_card, Fintype.card_unit, add_assoc]

/-- Exact full-summary count, using the pinned actual-summary theorem.
No full-summary asymptotic or comparison-ratio estimate is used. -/
theorem card_fullQuotient_closed (hn : 3 ≤ n) :
    Nat.card (FullQuotient n) = 1 + n * (2 * n - 4).choose (n - 3) +
      n * ((2 * (n - 2)).choose (n - 2) + 2 * ∑ b : Fin (n - 2),
        3 ^ b.val * (2 * (n - 2) - (b.val + 1)).choose ((n - 2) - (b.val + 1))) := by
  haveI : Fact (3 ≤ n) := ⟨hn⟩
  rw [card_fullQuotient_actual_counts hn, card_actual_registerable_states hn,
    Nat.card_eq_fintype_card, card_actualRegisteredSummaries_closed]

theorem card_future_le_full (hn : 3 ≤ n) :
    Nat.card (FutureQuotient n) ≤ Nat.card (FullQuotient n) := by
  haveI : Finite (FullQuotient n) := finite_fullQuotient hn
  exact Nat.card_le_card_of_surjective forgetToFuture forgetToFuture_surjective

end FullSummary
