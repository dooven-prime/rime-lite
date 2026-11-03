import FutureEvent.QuotientCardinality
import RegisteredAbsorptionChains.FiberParameters

namespace FutureEvent

open RegisteredAbsorptionChains

/-- Outside cuts, the singleton-zero site, and the other occupied offsets.
No reachability witness is included in these finite combinatorial inputs. -/
abbrev RegisterableParam (n t : ℕ) :=
  Fin n × Select (n - 3) (t - 1) × Select (n - 1) (t + 1)

abbrev RegisterableParams (n : ℕ) :=
  (i : Fin (n - 2)) × RegisterableParam n (i.val + 1)

/-- The carrier is selected by its left boundary index, followed by the
complete outside-cut/phase/occupied-offset tuple. -/
abbrev RegisteredPlacementParam (n k : ℕ) :=
  Fin (n - 1 - k) × FiberParams n k

abbrev RegisteredPlacementParams (n : ℕ) :=
  (i : Fin (n - 2)) × RegisteredPlacementParam n (i.val + 1)

theorem card_registerableParam (n t : ℕ) :
    Fintype.card (RegisterableParam n t) =
      n * (n - 3).choose (t - 1) * (n - 1).choose (t + 1) := by
  simp [RegisterableParam, Fintype.card_prod, mul_assoc]

theorem registerable_vandermonde (n : ℕ) (hn : 3 ≤ n) :
    ∑ i ∈ Finset.range (n - 2),
      (n - 3).choose i * (n - 1).choose (i + 2) = (2 * n - 4).choose (n - 3) := by
  have hsum := Nat.add_choose_eq (n - 3) (n - 1) (n - 3)
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hsum
  calc
    ∑ i ∈ Finset.range (n - 2), (n - 3).choose i * (n - 1).choose (i + 2) =
        ∑ i ∈ Finset.range ((n - 3) + 1),
          (n - 3).choose i * (n - 1).choose ((n - 3) - i) := by
      apply Finset.sum_congr (by congr 1; omega)
      intro i hi
      have hib : i < (n - 3) + 1 := Finset.mem_range.mp hi
      congr 1
      apply Nat.choose_symm_of_eq_add
      omega
    _ = ((n - 3) + (n - 1)).choose (n - 3) := hsum.symm
    _ = (2 * n - 4).choose (n - 3) := by congr 1; omega

/-- This counts the input parameter type only. Applying it to actual
placements additionally requires the placement equivalence. -/
theorem card_registerableParams (n : ℕ) (hn : 3 ≤ n) :
    Fintype.card (RegisterableParams n) = n * (2 * n - 4).choose (n - 3) := by
  classical
  rw [Fintype.card_sigma]
  simp_rw [card_registerableParam, Nat.add_sub_cancel_right]
  calc
    ∑ i : Fin (n - 2), n * (n - 3).choose i.val * (n - 1).choose (i.val + 1 + 1) =
        n * ∑ i : Fin (n - 2), (n - 3).choose i.val * (n - 1).choose (i.val + 2) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      simp [mul_assoc, Nat.add_assoc]
    _ = n * ∑ i ∈ Finset.range (n - 2),
        (n - 3).choose i * (n - 1).choose (i + 2) := by
      rw [← Fin.sum_univ_eq_sum_range]
    _ = n * (2 * n - 4).choose (n - 3) := by rw [registerable_vandermonde n hn]

theorem card_registeredPlacementParam (n k : ℕ) (hn : 1 ≤ n) (hk : 1 ≤ k) :
    Fintype.card (RegisteredPlacementParam n k) =
      (n - 1 - k) * (n * (n + k - 2).choose k) := by
  rw [Fintype.card_prod, card_fiberParams n k hn hk]
  simp

theorem card_registeredPlacementParams_sum (n : ℕ) (hn : 3 ≤ n) :
    Fintype.card (RegisteredPlacementParams n) =
      n * ∑ i ∈ Finset.range (n - 2),
        (n - 2 - i) * (n + (i + 1) - 2).choose (i + 1) := by
  classical
  rw [Fintype.card_sigma]
  simp_rw [card_registeredPlacementParam n _ (by omega : 1 ≤ n) (Nat.succ_le_succ (Nat.zero_le _))]
  calc
    ∑ i : Fin (n - 2), (n - 1 - (i.val + 1)) *
        (n * (n + (i.val + 1) - 2).choose (i.val + 1)) =
      n * ∑ i : Fin (n - 2), (n - 2 - i.val) *
        (n + (i.val + 1) - 2).choose (i.val + 1) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      have he : n - 1 - (i.val + 1) = n - 2 - i.val := by omega
      rw [he]
      ac_rfl
    _ = _ := by rw [← Fin.sum_univ_eq_sum_range]

end FutureEvent
