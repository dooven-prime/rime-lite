import analysis.WallisAsymptotics
import FutureEvent.ClosedQuotientCount

namespace FutureEventAnalysis

open Filter
open scoped Topology Real Nat

/-- Actual quotient sizes on the cofinal horizons n=m+3; no artificial
value for a zero-size environment is introduced. -/
noncomputable def futureCardReal (m : ℕ) : ℝ := by
  letI : NeZero (m + 3) := ⟨by omega⟩
  exact (Nat.card (FutureEvent.FutureQuotient (m + 3)) : ℝ)

theorem futureCardReal_formula (m : ℕ) :
    futureCardReal m =
      (5 * ((m : ℝ) + 1) + 3 - 1 / (m + 2)) * ((2 * (m + 1)).choose (m + 1) : ℝ) -
        (m + 3) * (m + 2) + 1 := by
  haveI : NeZero (m + 3) := ⟨by omega⟩
  have hclosed := FutureEvent.card_futureQuotient_closed (n := m + 3) (by omega)
  have hadd := FutureEvent.card_futureQuotient_additive (n := m + 3) (by omega)
  have hbound : (m + 3) * (m + 3 - 1) ≤
      1 + (m + 3) * (2 * (m + 3) - 4).choose (m + 3 - 3) +
        2 * (2 * (m + 3) - 3) * (2 * (m + 3) - 4).choose (m + 3 - 2) := by omega
  have ha : 2 * (m + 3) - 4 = 2 * (m + 1) := by omega
  have hb : m + 3 - 3 = m := by omega
  have hc : 2 * (m + 3) - 3 = 2 * m + 3 := by omega
  have hd : m + 3 - 2 = m + 1 := by omega
  have he : m + 3 - 1 = m + 2 := by omega
  change (Nat.card (FutureEvent.FutureQuotient (m + 3)) : ℝ) = _
  rw [hclosed, Nat.cast_sub hbound, ha, hb, hc, hd, he]
  push_cast
  have hadj := Nat.choose_succ_right_eq (2 * (m + 1)) m
  rw [show 2 * (m + 1) - m = m + 2 by omega] at hadj
  have hreal : ((2 * (m + 1)).choose m : ℝ) =
      ((2 * (m + 1)).choose (m + 1) : ℝ) * (m + 1) / (m + 2) := by
    apply (eq_div_iff (by positivity : (m : ℝ) + 2 ≠ 0)).mpr
    exact_mod_cast hadj.symm
  rw [hreal]
  field_simp
  ring

theorem tendsto_leading_coefficient :
    Tendsto (fun m : ℕ => (5 * (m : ℝ) + 3 - 1 / (m + 1)) / (m + 2))
      atTop (𝓝 5) := by
  have h1 : Tendsto (fun m : ℕ => (1 : ℝ) / ((m : ℝ) + 1)) atTop (𝓝 0) := by
    simpa only [Function.comp_def, Nat.cast_add, Nat.cast_one] using
      (tendsto_const_div_atTop_nhds_zero_nat (1 : ℝ)).comp (tendsto_add_atTop_nat 1)
  have h2 : Tendsto (fun m : ℕ => (1 : ℝ) / ((m : ℝ) + 2)) atTop (𝓝 0) := by
    simpa only [Function.comp_def, Nat.cast_add, Nat.cast_ofNat] using
      (tendsto_const_div_atTop_nhds_zero_nat (1 : ℝ)).comp (tendsto_add_atTop_nat 2)
  have h := ((tendsto_const_nhds : Tendsto (fun _ : ℕ => (5 : ℝ)) atTop (𝓝 5)).sub
    (h2.const_mul 7)).sub (h1.mul h2)
  simp only [mul_zero, sub_zero] at h
  apply h.congr'
  filter_upwards [] with m
  field_simp
  ring

theorem tendsto_sqrt_shift_ratio :
    Tendsto (fun m : ℕ => Real.sqrt (((m : ℝ) + 2) / m)) atTop (𝓝 1) := by
  have h := ((tendsto_const_div_atTop_nhds_zero_nat (2 : ℝ)).const_add 1).sqrt
  simp only [add_zero, Real.sqrt_one] at h
  apply h.congr'
  filter_upwards [eventually_atTop.mpr ⟨1, fun m hm => hm⟩] with m hm
  congr 1
  have hne : (m : ℝ) ≠ 0 := by exact_mod_cast (by omega : m ≠ 0)
  field_simp

theorem tendsto_normalized_leading :
    Tendsto (fun m : ℕ =>
      (1 / 16 : ℝ) * ((5 * (m : ℝ) + 3 - 1 / (m + 1)) / (m + 2)) *
        Real.sqrt (((m : ℝ) + 2) / m) *
        (Real.sqrt m * ((2 * m).choose m : ℝ) / (4 : ℝ) ^ m))
      atTop (𝓝 (5 / (16 * Real.sqrt Real.pi))) := by
  have h := (((tendsto_const_nhds : Tendsto (fun _ : ℕ => (1 / 16 : ℝ)) atTop (𝓝 (1 / 16))).mul
    tendsto_leading_coefficient).mul tendsto_sqrt_shift_ratio).mul tendsto_scaled_central_binomial
  have hc : (1 / 16 : ℝ) * 5 * 1 * (1 / Real.sqrt Real.pi) = 5 / (16 * Real.sqrt Real.pi) := by ring
  simpa only [hc] using h

theorem normalized_count_decomposition (m : ℕ) (hm : 1 ≤ m) :
    ((5 * (m : ℝ) + 3 - 1 / (m + 1)) * ((2 * m).choose m : ℝ) -
        (m + 2) * (m + 1) + 1) / (Real.sqrt ((m : ℝ) + 2) * (4 : ℝ) ^ (m + 2)) =
      (1 / 16 : ℝ) * ((5 * (m : ℝ) + 3 - 1 / (m + 1)) / (m + 2)) *
        Real.sqrt (((m : ℝ) + 2) / m) *
        (Real.sqrt m * ((2 * m).choose m : ℝ) / (4 : ℝ) ^ m) +
      (1 - ((m : ℝ) + 2) * (m + 1)) / (Real.sqrt ((m : ℝ) + 2) * (4 : ℝ) ^ (m + 2)) := by
  have hmpos : (0 : ℝ) < m := by exact_mod_cast hm
  rw [Real.sqrt_div (by positivity : (0 : ℝ) ≤ (m : ℝ) + 2)]
  have hs := Real.sq_sqrt (by positivity : (0 : ℝ) ≤ (m : ℝ) + 2)
  have hsm : Real.sqrt (m : ℝ) ≠ 0 := by positivity
  have hs2 : Real.sqrt ((m : ℝ) + 2) ≠ 0 := by positivity
  simp only [pow_add]
  norm_num
  field_simp
  rw [hs]
  ring

/-- Final ratio limit for the actual quotient on every cofinal horizon n=m+3. -/
theorem tendsto_futureQuotient_normalized :
    Tendsto (fun m : ℕ => futureCardReal m /
      (Real.sqrt ((m : ℝ) + 3) * (4 : ℝ) ^ (m + 3)))
      atTop (𝓝 (5 / (16 * Real.sqrt Real.pi))) := by
  have h := (tendsto_normalized_leading.add tendsto_normalized_remainder).comp
    (tendsto_add_atTop_nat 1)
  simp only [add_zero] at h
  apply h.congr'
  filter_upwards [] with m
  rw [futureCardReal_formula]
  have he := normalized_count_decomposition (m + 1) (by omega)
  rw [Real.sqrt_div (by positivity : (0 : ℝ) ≤ ((m + 1 : ℕ) : ℝ) + 2)] at he
  norm_num only [Nat.cast_add, Nat.cast_one, add_assoc] at he
  convert he.symm using 1
  norm_num [Function.comp_def, add_assoc]

end FutureEventAnalysis
