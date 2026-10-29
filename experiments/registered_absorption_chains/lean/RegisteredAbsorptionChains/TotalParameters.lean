import RegisteredAbsorptionChains.CheckpointCounts
import RegisteredAbsorptionChains.FiberParameters
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace RegisteredAbsorptionChains

/-- The empty-chain term: phase and a choice among formal placements. -/
abbrev EmptyParams (n m : ℕ) := Fin n × Select (2 * m) m

/-- The term whose final selected checkpoint has zero-based index `b`. -/
abbrev LastParams (n m : ℕ) (b : Fin m) :=
  EndNonzero b.1 × Fin n ×
    Select (2 * m - (b.1 + 1)) (m - (b.1 + 1))

/-- Disjoint formal parameters for the terms on the right of equation (5.1). -/
abbrev TotalParams (n m : ℕ) :=
  EmptyParams n m ⊕ ((b : Fin m) × LastParams n m b)

theorem card_emptyParams (n m : ℕ) :
    Fintype.card (EmptyParams n m) = n * (2 * m).choose m := by
  simp [EmptyParams, Fintype.card_prod]

theorem card_lastParams (n m : ℕ) (b : Fin m) :
    Fintype.card (LastParams n m b) =
      2 * 3 ^ b.1 * n *
        (2 * m - (b.1 + 1)).choose (m - (b.1 + 1)) := by
  simp only [Fintype.card_prod, Fintype.card_fin]
  rw [card_endNonzero, card_select]
  ac_rfl

/-- The arithmetic of Theorem 5.1, for the explicitly defined formal parameter sum. -/
theorem card_totalParams (n m : ℕ) :
    Fintype.card (TotalParams n m) =
      n * ((2 * m).choose m +
        2 * ∑ b : Fin m,
          3 ^ b.1 *
            (2 * m - (b.1 + 1)).choose (m - (b.1 + 1))) := by
  classical
  rw [show Fintype.card (TotalParams n m) =
      Fintype.card (EmptyParams n m) +
        ∑ b : Fin m, Fintype.card (LastParams n m b) by
      simp [TotalParams, Fintype.card_sum, Fintype.card_sigma]]
  rw [card_emptyParams]
  simp_rw [card_lastParams]
  calc
    n * (2 * m).choose m +
        ∑ b : Fin m, 2 * 3 ^ b.1 * n *
          (2 * m - (b.1 + 1)).choose (m - (b.1 + 1)) =
      n * (2 * m).choose m + n * (2 * ∑ b : Fin m,
        3 ^ b.1 * (2 * m - (b.1 + 1)).choose (m - (b.1 + 1))) := by
          rw [Finset.mul_sum, Finset.mul_sum]
          congr 1
          apply Finset.sum_congr rfl
          intro b _
          ac_rfl
    _ = _ := by rw [mul_add]

end RegisteredAbsorptionChains
