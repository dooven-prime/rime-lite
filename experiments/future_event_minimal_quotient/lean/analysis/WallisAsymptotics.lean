import Mathlib.Analysis.Real.Pi.Wallis
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic

namespace FutureEventAnalysis

open Filter
open scoped Topology Real Nat

theorem wallis_central_binomial (m : ℕ) :
    Real.Wallis.W m =
      (4 : ℝ) ^ (2 * m) / (((2 * m).choose m : ℝ) ^ 2 * (2 * m + 1)) := by
  have hfac : ((2 * m).choose m : ℝ) * (m.factorial : ℝ) ^ 2 = (2 * m).factorial := by
    have h := congrArg (Nat.cast : ℕ → ℝ) (Nat.add_choose_mul_factorial_mul_factorial m m)
    push_cast at h
    simpa only [← two_mul m, pow_two, mul_assoc] using h
  have hpow : (2 : ℝ) ^ (4 * m) = (4 : ℝ) ^ (2 * m) := by
    calc
      _ = ((2 : ℝ) ^ 2) ^ (2 * m) := by rw [← pow_mul]; congr 1; omega
      _ = _ := by norm_num
  have hB : 0 < ((2 * m).choose m : ℝ) := by exact_mod_cast Nat.choose_pos (by omega : m ≤ 2 * m)
  rw [Real.Wallis.W_eq_factorial_ratio, ← hfac, hpow]
  field_simp

theorem scaled_central_binomial_sqrt (m : ℕ) :
    Real.sqrt m * ((2 * m).choose m : ℝ) / (4 : ℝ) ^ m =
      Real.sqrt (((m : ℝ) / (2 * m + 1)) / Real.Wallis.W m) := by
  have hB : 0 < ((2 * m).choose m : ℝ) := by exact_mod_cast Nat.choose_pos (by omega : m ≤ 2 * m)
  have hpow : (4 : ℝ) ^ (2 * m) = ((4 : ℝ) ^ m) ^ 2 := by rw [Nat.mul_comm 2 m, pow_mul]
  have hsq : (Real.sqrt m * ((2 * m).choose m : ℝ) / (4 : ℝ) ^ m) ^ 2 =
      ((m : ℝ) / (2 * m + 1)) / Real.Wallis.W m := by
    rw [div_pow, mul_pow, Real.sq_sqrt (by positivity), wallis_central_binomial, hpow]
    field_simp
  rw [← hsq, Real.sqrt_sq (by positivity)]

theorem tendsto_wallis_rational :
    Tendsto (fun m : ℕ => (m : ℝ) / (2 * m + 1)) atTop (𝓝 (1 / 2)) := by
  conv =>
    congr
    · skip
    · skip
    rw [one_div, ← add_zero (2 : ℝ)]
  refine (((tendsto_const_div_atTop_nhds_zero_nat 1).const_add (2 : ℝ)).inv₀
    ((add_zero (2 : ℝ)).symm ▸ two_ne_zero)).congr' (eventually_atTop.mpr ⟨1, fun m hm => ?_⟩)
  rw [add_div' (1 : ℝ) 2 m (Nat.cast_ne_zero.mpr (by omega)), inv_div]

/-- The central-binomial input is obtained from Wallis, without Stirling. -/
theorem tendsto_scaled_central_binomial :
    Tendsto (fun m : ℕ => Real.sqrt m * ((2 * m).choose m : ℝ) / (4 : ℝ) ^ m)
      atTop (𝓝 (1 / Real.sqrt Real.pi)) := by
  have h := (tendsto_wallis_rational.div Real.Wallis.tendsto_W_nhds_pi_div_two
    (by positivity : Real.pi / 2 ≠ 0)).sqrt
  have hval : Real.sqrt (((1 : ℝ) / 2) / (Real.pi / 2)) = 1 / Real.sqrt Real.pi := by
    rw [show ((1 : ℝ) / 2) / (Real.pi / 2) = 1 / Real.pi by field_simp,
      Real.sqrt_div (by norm_num : (0 : ℝ) ≤ 1), Real.sqrt_one]
  change Tendsto (fun m : ℕ => Real.sqrt (((m : ℝ) / (2 * m + 1)) / Real.Wallis.W m))
    atTop (𝓝 (Real.sqrt (((1 : ℝ) / 2) / (Real.pi / 2)))) at h
  simpa only [← scaled_central_binomial_sqrt, hval] using h

theorem tendsto_remainder_polynomial :
    Tendsto (fun m : ℕ => (1 - ((m : ℝ) + 2) * (m + 1)) / (4 : ℝ) ^ (m + 2))
      atTop (𝓝 0) := by
  have h0 := tendsto_pow_const_div_const_pow_of_one_lt 0 (by norm_num : (1 : ℝ) < 4)
  have h1 := tendsto_pow_const_div_const_pow_of_one_lt 1 (by norm_num : (1 : ℝ) < 4)
  have h2 := tendsto_pow_const_div_const_pow_of_one_lt 2 (by norm_num : (1 : ℝ) < 4)
  have h := (((h2.add (h1.const_mul 3)).add h0).neg).div_const 16
  simp only [mul_zero, add_zero, neg_zero, zero_div] at h
  apply h.congr'
  filter_upwards [] with m
  simp only [pow_zero, pow_one, pow_add]
  norm_num
  field_simp
  ring

/-- The polynomial remainder vanishes on the final normalization scale. -/
theorem tendsto_normalized_remainder :
    Tendsto (fun m : ℕ => (1 - ((m : ℝ) + 2) * (m + 1)) /
      (Real.sqrt ((m : ℝ) + 2) * (4 : ℝ) ^ (m + 2))) atTop (𝓝 0) := by
  have hs : Tendsto (fun m : ℕ => Real.sqrt ((m : ℝ) + 2)) atTop atTop :=
    Real.tendsto_sqrt_atTop.comp (tendsto_natCast_atTop_atTop.atTop_add tendsto_const_nhds)
  have hi : Tendsto (fun m : ℕ => (1 : ℝ) / Real.sqrt ((m : ℝ) + 2)) atTop (𝓝 0) :=
    tendsto_const_nhds.div_atTop hs
  have h := tendsto_remainder_polynomial.mul hi
  simp only [mul_zero] at h
  apply h.congr'
  filter_upwards [] with m
  ring

end FutureEventAnalysis
