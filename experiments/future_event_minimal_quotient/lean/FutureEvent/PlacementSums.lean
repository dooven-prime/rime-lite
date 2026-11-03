import FutureEvent.PlacementParameters
import Mathlib.Data.Nat.Choose.Sum

namespace FutureEvent

theorem diagonal_hockey (r m : ℕ) :
    ∑ i ∈ Finset.range (m + 1), (r + i).choose i = (r + m + 1).choose m := by
  calc
    ∑ i ∈ Finset.range (m + 1), (r + i).choose i =
        ∑ i ∈ Finset.range (m + 1), (i + r).choose r := by
      apply Finset.sum_congr rfl
      intro i _
      rw [Nat.add_comm r i]
      apply Nat.choose_symm_of_eq_add
      omega
    _ = (m + r + 1).choose (r + 1) := Nat.sum_range_add_choose m r
    _ = (r + m + 1).choose m := by
      rw [Nat.add_comm m r]
      apply Nat.choose_symm_of_eq_add
      omega

theorem weighted_hockey (r m : ℕ) :
    ∑ i ∈ Finset.range (m + 1), (m + 1 - i) * (r + i).choose i =
      (r + m + 2).choose m := by
  induction m with
  | zero => simp
  | succ m ih =>
      have hinner : ∑ i ∈ Finset.range (m + 1), (m + 1 + 1 - i) * (r + i).choose i =
          (∑ i ∈ Finset.range (m + 1), (m + 1 - i) * (r + i).choose i) +
            ∑ i ∈ Finset.range (m + 1), (r + i).choose i := by
        rw [← Finset.sum_add_distrib]
        apply Finset.sum_congr rfl
        intro i hi
        have hib := Finset.mem_range.mp hi
        have he : m + 1 + 1 - i = (m + 1 - i) + 1 := by omega
        rw [he]
        ring
      rw [Finset.sum_range_succ, hinner, ih, diagonal_hockey]
      simp only [Nat.add_sub_cancel_left, Nat.one_mul]
      have hp1 := Nat.choose_succ_succ (r + m + 1) m
      have hp2 := Nat.choose_succ_succ (r + m + 2) m
      simpa only [Nat.add_assoc] using
        (show (r + m + 2).choose m + (r + m + 1).choose m +
            (r + (m + 1)).choose (m + 1) = (r + (m + 1) + 2).choose (m + 1) by
          have h1 : (r + m + 1).choose m + (r + (m + 1)).choose (m + 1) =
              (r + m + 2).choose (m + 1) := by simpa [Nat.add_assoc] using hp1.symm
          have h2 : (r + m + 2).choose m + (r + m + 2).choose (m + 1) =
              (r + (m + 1) + 2).choose (m + 1) := by simpa [Nat.add_assoc] using hp2.symm
          omega)

theorem positive_weighted_hockey (m : ℕ) :
    (∑ i ∈ Finset.range m, (m - i) * (m + i + 1).choose (i + 1)) + (m + 1) =
      (2 * m + 2).choose m := by
  have h := weighted_hockey m m
  rw [Finset.sum_range_succ'] at h
  simpa [Nat.add_assoc, Nat.add_sub_add_right, two_mul] using h

theorem central_binomial_scale (m : ℕ) :
    (m + 2) * (2 * m + 2).choose m = 2 * (2 * m + 1) * (2 * m).choose m := by
  have h1 := Nat.choose_mul_succ_eq (2 * m + 1) m
  have h2 := Nat.choose_mul_succ_eq (2 * m) m
  have ha : 2 * m + 1 + 1 = 2 * m + 2 := by omega
  have hb : 2 * m + 2 - m = m + 2 := by omega
  have hc : 2 * m + 1 - m = m + 1 := by omega
  rw [ha, hb] at h1
  rw [hc] at h2
  nlinarith

theorem registered_sum_additive (m : ℕ) :
    (m + 2) * (∑ i ∈ Finset.range m, (m - i) * (m + i + 1).choose (i + 1)) +
        (m + 2) * (m + 1) = 2 * (2 * m + 1) * (2 * m).choose m := by
  calc
    _ = (m + 2) * ((∑ i ∈ Finset.range m, (m - i) *
        (m + i + 1).choose (i + 1)) + (m + 1)) := by ring
    _ = (m + 2) * (2 * m + 2).choose m := by rw [positive_weighted_hockey]
    _ = _ := central_binomial_scale m

theorem card_registeredPlacementParams_additive (n : ℕ) (hn : 3 ≤ n) :
    Fintype.card (RegisteredPlacementParams n) + n * (n - 1) =
      2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) := by
  rw [card_registeredPlacementParams_sum n hn]
  have h := registered_sum_additive (n - 2)
  have ha : n - 2 + 2 = n := by omega
  have hb : n - 2 + 1 = n - 1 := by omega
  have hc : 2 * (n - 2) + 1 = 2 * n - 3 := by omega
  have hd : 2 * (n - 2) = 2 * n - 4 := by omega
  have he : 2 * n - 4 + 1 = 2 * n - 3 := by omega
  have hi (i : ℕ) : n - 2 + i + 1 = n + (i + 1) - 2 := by omega
  simpa only [ha, hb, hc, hd, he, hi] using h

theorem card_registeredPlacementParams_closed (n : ℕ) (hn : 3 ≤ n) :
    Fintype.card (RegisteredPlacementParams n) =
      2 * (2 * n - 3) * (2 * n - 4).choose (n - 2) - n * (n - 1) := by
  have h := card_registeredPlacementParams_additive n hn
  omega

end FutureEvent
