import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Data.Nat.Choose.Bounds
import Mathlib.Tactic

namespace ObserverComparison

open Finset Filter
open scoped Topology

/-- The fixed-pair summary bracket, before multiplication by the site count. -/
def summaryBracket (m : ℕ) : ℝ :=
  ((2 * m).choose m : ℝ) + 2 * ∑ b ∈ range m,
    (3 : ℝ) ^ b * ((2 * m - (b + 1)).choose (m - (b + 1)) : ℝ)

theorem weighted_choose_sum (a d : ℕ) :
    (∑ k ∈ range (d + 1), (3 : ℝ) ^ (d - k) * ((a + k).choose k : ℝ)) =
      ((a + d + 1).choose d : ℝ) +
        2 * ∑ k ∈ range d, (3 : ℝ) ^ (d - 1 - k) * ((a + k + 1).choose k : ℝ) := by
  induction d with
  | zero => simp
  | succ d ih =>
    have hsum : (∑ k ∈ range (d + 1),
        (3 : ℝ) ^ (d + 1 - k) * ((a + k).choose k : ℝ)) =
        3 * ∑ k ∈ range (d + 1), (3 : ℝ) ^ (d - k) * ((a + k).choose k : ℝ) := by
      rw [mul_sum]
      apply sum_congr rfl
      intro k hk
      rw [show d + 1 - k = (d - k) + 1 by simp only [mem_range] at hk; omega,
        pow_succ]
      ring
    have htail : (∑ k ∈ range d,
        (3 : ℝ) ^ (d - k) * ((a + k + 1).choose k : ℝ)) =
        3 * ∑ k ∈ range d, (3 : ℝ) ^ (d - 1 - k) * ((a + k + 1).choose k : ℝ) := by
      rw [mul_sum]
      apply sum_congr rfl
      intro k hk
      rw [show d - k = (d - 1 - k) + 1 by simp only [mem_range] at hk; omega,
        pow_succ]
      ring
    rw [sum_range_succ, hsum, ih, sum_range_succ]
    simp only [Nat.add_sub_cancel] at *
    rw [htail]
    have hp := Nat.choose_succ_succ (a + d + 1) d
    have hpr : ((a + (d + 1) + 1).choose (d + 1) : ℝ) =
        ((a + d + 1).choose d : ℝ) + ((a + d + 1).choose (d + 1) : ℝ) := by
      exact_mod_cast hp
    rw [hpr]
    simp only [Nat.sub_self, pow_zero, one_mul]
    ring

theorem summaryBracket_truncated (m : ℕ) :
    summaryBracket (m + 1) =
      (3 : ℝ) ^ (m + 1) * ∑ k ∈ range (m + 2),
        ((m + k).choose k : ℝ) * (1 / 3 : ℝ) ^ k := by
  have h := weighted_choose_sum m (m + 1)
  have hreverse : (∑ b ∈ range (m + 1), (3 : ℝ) ^ b *
      ((2 * (m + 1) - (b + 1)).choose ((m + 1) - (b + 1)) : ℝ)) =
      ∑ k ∈ range (m + 1), (3 : ℝ) ^ (m - k) * ((m + k + 1).choose k : ℝ) := by
    rw [← sum_range_reflect]
    apply sum_congr rfl
    intro k hk
    have hk' : k ≤ m := by simp only [mem_range] at hk; omega
    rw [show m + 1 - 1 - k = m - k by omega,
      show 2 * (m + 1) - (m - k + 1) = m + k + 1 by omega,
      show m + 1 - (m - k + 1) = k by omega]
  unfold summaryBracket
  rw [hreverse]
  rw [show 2 * (m + 1) = m + (m + 1) + 1 by omega]
  simp only [Nat.add_sub_cancel] at h
  rw [← h]
  rw [mul_sum]
  apply sum_congr rfl
  intro k hk
  have hk' : k ≤ m + 1 := by simp only [mem_range] at hk; omega
  rw [one_div, inv_pow]
  rw [pow_sub₀ (3 : ℝ) (by norm_num) hk']
  ring

theorem negative_binomial_hasSum (m : ℕ) :
    HasSum (fun k : ℕ => ((m + k).choose k : ℝ) * (1 / 3 : ℝ) ^ k)
      (1 / (2 / 3 : ℝ) ^ (m + 1)) := by
  have h := hasSum_choose_mul_geometric_of_norm_lt_one m
    (by norm_num : ‖(1 / 3 : ℝ)‖ < 1)
  have he : (fun k : ℕ => ((k + m).choose m : ℝ) * (1 / 3 : ℝ) ^ k) =
      fun k : ℕ => ((m + k).choose k : ℝ) * (1 / 3 : ℝ) ^ k := by
    funext k
    rw [Nat.add_comm k m, Nat.choose_symm_add]
  rw [he] at h
  simpa only [show (1 : ℝ) - 1 / 3 = 2 / 3 by norm_num] using h

/-- The omitted negative-binomial tail, with the shape parameter varying
with the truncation. -/
noncomputable def summaryTail (m : ℕ) : ℝ :=
  ∑' k : ℕ, ((m + (k + (m + 2))).choose (k + (m + 2)) : ℝ) *
    (1 / 3 : ℝ) ^ (k + (m + 2))

theorem summaryTail_identity (m : ℕ) :
    1 - summaryBracket (m + 1) / (9 / 2 : ℝ) ^ (m + 1) =
      (2 / 3 : ℝ) ^ (m + 1) * summaryTail m := by
  have hsum := negative_binomial_hasSum m
  have hsplit := hsum.summable.sum_add_tsum_nat_add (m + 2)
  rw [hsum.tsum_eq] at hsplit
  rw [summaryBracket_truncated]
  change 1 - _ = (2 / 3 : ℝ) ^ (m + 1) *
    (∑' k : ℕ, ((m + (k + (m + 2))).choose (k + (m + 2)) : ℝ) *
      (1 / 3 : ℝ) ^ (k + (m + 2)))
  have hp : (3 : ℝ) ^ (m + 1) / (9 / 2 : ℝ) ^ (m + 1) =
      (2 / 3 : ℝ) ^ (m + 1) := by rw [← div_pow]; norm_num
  rw [mul_div_right_comm, hp]
  have hnonzero : (2 / 3 : ℝ) ^ (m + 1) ≠ 0 := by positivity
  have hscale := congrArg (fun x : ℝ => (2 / 3 : ℝ) ^ (m + 1) * x) hsplit
  rw [mul_one_div_cancel hnonzero] at hscale
  linarith

theorem summaryTail_nonneg (m : ℕ) : 0 ≤ summaryTail m :=
  tsum_nonneg (fun _ => by positivity)

theorem summaryTail_le (m : ℕ) :
    summaryTail m ≤ (2 : ℝ) ^ m * 3 * (2 / 3 : ℝ) ^ (m + 2) := by
  have hsum := (negative_binomial_hasSum m).summable
  have hgeom := hasSum_geometric_of_lt_one (by norm_num : (0 : ℝ) ≤ 2 / 3)
    (by norm_num : (2 / 3 : ℝ) < 1)
  have hmajor : Summable (fun k : ℕ => (2 : ℝ) ^ m * (2 / 3 : ℝ) ^ (k + (m + 2))) := by
    exact (hgeom.summable.comp_injective (fun _ _ h => Nat.add_right_cancel h)).mul_left _
  calc
    summaryTail m ≤ ∑' k : ℕ, (2 : ℝ) ^ m * (2 / 3 : ℝ) ^ (k + (m + 2)) := by
      unfold summaryTail
      apply Summable.tsum_le_tsum _
        (hsum.comp_injective (fun _ _ h => Nat.add_right_cancel h)) hmajor
      intro k
      have hb : ((m + (k + (m + 2))).choose (k + (m + 2)) : ℝ) ≤
          (2 : ℝ) ^ (m + (k + (m + 2))) := by exact_mod_cast Nat.choose_le_two_pow _ _
      calc
        _ ≤ (2 : ℝ) ^ (m + (k + (m + 2))) * (1 / 3 : ℝ) ^ (k + (m + 2)) :=
          mul_le_mul_of_nonneg_right hb (by positivity)
        _ = _ := by rw [pow_add, mul_assoc, ← mul_pow]; norm_num
    _ = _ := by
      simp_rw [pow_add, mul_left_comm ((2 : ℝ) ^ m), mul_assoc]
      rw [tsum_mul_right, hgeom.tsum_eq]
      norm_num
      ring

theorem summaryBracket_error (m : ℕ) :
    0 ≤ 1 - summaryBracket (m + 1) / (9 / 2 : ℝ) ^ (m + 1) ∧
    1 - summaryBracket (m + 1) / (9 / 2 : ℝ) ^ (m + 1) ≤ (8 / 9 : ℝ) ^ (m + 1) := by
  rw [summaryTail_identity]
  refine ⟨mul_nonneg (by positivity) (summaryTail_nonneg m), ?_⟩
  calc
    _ ≤ (2 / 3 : ℝ) ^ (m + 1) * ((2 : ℝ) ^ m * 3 * (2 / 3 : ℝ) ^ (m + 2)) :=
      mul_le_mul_of_nonneg_left (summaryTail_le m) (by positivity)
    _ = _ := by
      have hp : (2 / 3 : ℝ) ^ m * (2 : ℝ) ^ m * (2 / 3 : ℝ) ^ m = (8 / 9 : ℝ) ^ m := by
        rw [← mul_pow, ← mul_pow]
        norm_num
      simp only [pow_succ]
      nlinarith [hp]

theorem tendsto_summaryBracket_normalized :
    Tendsto (fun m : ℕ => summaryBracket (m + 1) / (9 / 2 : ℝ) ^ (m + 1))
      atTop (𝓝 1) := by
  have hzero := (tendsto_pow_atTop_nhds_zero_of_lt_one
    (by norm_num : (0 : ℝ) ≤ 8 / 9) (by norm_num : (8 / 9 : ℝ) < 1)).comp
    (tendsto_add_atTop_nat 1)
  have h := squeeze_zero (fun m => (summaryBracket_error m).1)
    (fun m => (summaryBracket_error m).2) hzero
  have hsub := (tendsto_const_nhds (x := (1 : ℝ))).sub h
  simpa only [sub_sub_cancel, sub_zero] using hsub

end ObserverComparison
