import comparison.SummarySeries
import full_summary.CountBridge
import analysis.FutureCountAsymptotics

namespace ObserverComparison

open Filter
open scoped Topology

/-- Literal actual full-summary quotient sizes, on the same cofinal horizons
as the frozen future-event analytic milestone. -/
noncomputable def fullCardReal (m : ℕ) : ℝ := by
  letI : NeZero (m + 3) := ⟨by omega⟩
  exact (Nat.card (FullSummary.FullQuotient (m + 3)) : ℝ)

theorem fullCardReal_formula (m : ℕ) :
    fullCardReal m = 1 + (m + 3 : ℝ) * ((2 * (m + 1)).choose m : ℝ) +
      (m + 3) * summaryBracket (m + 1) := by
  have : NeZero (m + 3) := ⟨by omega⟩
  have h := FullSummary.card_fullQuotient_closed (n := m + 3) (by omega)
  change (Nat.card (FullSummary.FullQuotient (m + 3)) : ℝ) = _
  rw [h]
  norm_num only [show m + 3 - 2 = m + 1 by omega,
    show 2 * (m + 3) - 4 = 2 * (m + 1) by omega,
    show m + 3 - 3 = m by omega, Nat.cast_add, Nat.cast_mul, Nat.cast_one,
    Nat.cast_ofNat, Nat.cast_sum, Nat.cast_pow]
  rw [summaryBracket, ← Fin.sum_univ_eq_sum_range]
  rfl

theorem normalized_extra_bound (m : ℕ) :
    0 ≤ (1 + (m + 3 : ℝ) * ((2 * (m + 1)).choose m : ℝ)) /
        ((m + 3) * (9 / 2 : ℝ) ^ (m + 3)) ∧
    (1 + (m + 3 : ℝ) * ((2 * (m + 1)).choose m : ℝ)) /
        ((m + 3) * (9 / 2 : ℝ) ^ (m + 3)) ≤ 2 * (8 / 9 : ℝ) ^ (m + 3) := by
  have hb : ((2 * (m + 1)).choose m : ℝ) ≤ (4 : ℝ) ^ (m + 3) := by
    calc
      _ ≤ (2 : ℝ) ^ (2 * (m + 1)) := by exact_mod_cast Nat.choose_le_two_pow _ _
      _ = (4 : ℝ) ^ (m + 1) := by rw [pow_mul]; norm_num
      _ ≤ (4 : ℝ) ^ (m + 3) := by gcongr <;> norm_num
  have hpow : (1 : ℝ) ≤ (4 : ℝ) ^ (m + 3) := one_le_pow₀ (by norm_num)
  have hn : (1 : ℝ) ≤ (m : ℝ) + 3 := by
    have hm : (0 : ℝ) ≤ m := Nat.cast_nonneg m
    linarith
  refine ⟨by positivity, ?_⟩
  calc
    _ ≤ (2 * ((m : ℝ) + 3) * (4 : ℝ) ^ (m + 3)) /
        (((m : ℝ) + 3) * (9 / 2 : ℝ) ^ (m + 3)) := by
      apply div_le_div_of_nonneg_right _ (by positivity)
      nlinarith
    _ = _ := by
      rw [show (8 / 9 : ℝ) ^ (m + 3) = (4 : ℝ) ^ (m + 3) /
          (9 / 2 : ℝ) ^ (m + 3) by rw [← div_pow]; norm_num]
      field_simp

theorem tendsto_normalized_extra :
    Tendsto (fun m : ℕ => (1 + (m + 3 : ℝ) * ((2 * (m + 1)).choose m : ℝ)) /
      ((m + 3) * (9 / 2 : ℝ) ^ (m + 3))) atTop (𝓝 0) := by
  have h := ((tendsto_pow_atTop_nhds_zero_of_lt_one
    (by norm_num : (0 : ℝ) ≤ 8 / 9) (by norm_num : (8 / 9 : ℝ) < 1)).comp
    (tendsto_add_atTop_nat 3)).const_mul 2
  simp only [mul_zero] at h
  exact squeeze_zero (fun m => (normalized_extra_bound m).1)
    (fun m => (normalized_extra_bound m).2) h

theorem full_normalized_decomposition (m : ℕ) :
    fullCardReal m / (((m : ℝ) + 3) * (9 / 2 : ℝ) ^ (m + 3)) =
      (4 / 81 : ℝ) * (summaryBracket (m + 1) / (9 / 2 : ℝ) ^ (m + 1)) +
      (1 + (m + 3 : ℝ) * ((2 * (m + 1)).choose m : ℝ)) /
        (((m : ℝ) + 3) * (9 / 2 : ℝ) ^ (m + 3)) := by
  rw [fullCardReal_formula, show m + 3 = (m + 1) + 2 by omega, pow_add]
  norm_num
  field_simp
  ring

theorem tendsto_fullQuotient_normalized :
    Tendsto (fun m : ℕ => fullCardReal m /
      (((m : ℝ) + 3) * (9 / 2 : ℝ) ^ (m + 3))) atTop (𝓝 (4 / 81)) := by
  have h := (tendsto_summaryBracket_normalized.const_mul (4 / 81 : ℝ)).add
    tendsto_normalized_extra
  simp only [mul_one, add_zero] at h
  exact h.congr (fun m => (full_normalized_decomposition m).symm)

theorem observer_ratio_identity (m : ℕ) :
    (fullCardReal m / FutureEventAnalysis.futureCardReal m) /
        (Real.sqrt ((m : ℝ) + 3) * (9 / 8 : ℝ) ^ (m + 3)) =
      (fullCardReal m / (((m : ℝ) + 3) * (9 / 2 : ℝ) ^ (m + 3))) /
        (FutureEventAnalysis.futureCardReal m /
          (Real.sqrt ((m : ℝ) + 3) * (4 : ℝ) ^ (m + 3))) := by
  by_cases hf : FutureEventAnalysis.futureCardReal m = 0
  · simp [hf]
  have hs : Real.sqrt ((m : ℝ) + 3) ≠ 0 := by positivity
  have hsq := Real.sq_sqrt (by positivity : (0 : ℝ) ≤ (m : ℝ) + 3)
  have hp : (9 / 2 : ℝ) ^ (m + 3) = (9 / 8 : ℝ) ^ (m + 3) * (4 : ℝ) ^ (m + 3) := by
    rw [← mul_pow]
    norm_num
  rw [hp]
  field_simp
  rw [hsq]

/-- Exponential separation of two observer contracts on the same generated
`p,d` system; neither quotient is replaced by a formal counting proxy. -/
theorem tendsto_full_div_future_normalized :
    Tendsto (fun m : ℕ => (fullCardReal m / FutureEventAnalysis.futureCardReal m) /
      (Real.sqrt ((m : ℝ) + 3) * (9 / 8 : ℝ) ^ (m + 3)))
      atTop (𝓝 (64 * Real.sqrt Real.pi / 405)) := by
  have h := tendsto_fullQuotient_normalized.div
    FutureEventAnalysis.tendsto_futureQuotient_normalized
    (by positivity : (5 : ℝ) / (16 * Real.sqrt Real.pi) ≠ 0)
  have hc : (4 / 81 : ℝ) / (5 / (16 * Real.sqrt Real.pi)) =
      64 * Real.sqrt Real.pi / 405 := by
    field_simp
    ring
  rw [hc] at h
  exact h.congr (fun m => (observer_ratio_identity m).symm)

theorem tendsto_full_div_future_atTop :
    Tendsto (fun m : ℕ => fullCardReal m / FutureEventAnalysis.futureCardReal m)
      atTop atTop := by
  have hs : Tendsto (fun m : ℕ => Real.sqrt ((m : ℝ) + 3)) atTop atTop :=
    Real.tendsto_sqrt_atTop.comp (tendsto_natCast_atTop_atTop.atTop_add tendsto_const_nhds)
  have hp := (tendsto_pow_atTop_atTop_of_one_lt (by norm_num : (1 : ℝ) < 9 / 8)).comp
    (tendsto_add_atTop_nat 3)
  have hscale := hs.atTop_mul_atTop₀ hp
  have h := tendsto_full_div_future_normalized.pos_mul_atTop
    (by positivity : (0 : ℝ) < 64 * Real.sqrt Real.pi / 405) hscale
  apply h.congr
  intro m
  exact div_mul_cancel₀ _ (by positivity)

end ObserverComparison
