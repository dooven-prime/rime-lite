import RSR2History.PackedLowerAmortization

/-! Scalar comparisons for an all-upper packed replay with multiple terminal roots. -/

namespace RSR2History

private theorem twice_choose_two_int (a : Nat) :
    (2 : Int) * (a.choose 2 : Int) = (a : Int) * ((a : Int)-1) := by
  by_cases ha : a = 0
  · subst a
    norm_num
  · obtain ⟨q,hq⟩ := Nat.even_mul_pred_self a
    have h : 2*a.choose 2 = a*(a-1) := by
      rw [Nat.choose_two_right, hq]
      omega
    have h := congrArg (fun a : Nat => (a : Int)) h
    push_cast [Nat.cast_sub (show 1 ≤ a by omega)] at h
    exact h

private theorem terminal_square_le {n r : Nat} (hr : 1 ≤ r) (hrn : r ≤ n) :
    (n-r)^2 ≤ n*(n-1) := by
  simpa only [pow_two] using
    Nat.mul_le_mul (show n-r ≤ n by omega) (show n-r ≤ n-1 by omega)

/-- For a packed replay with upper fusions, the extra lower cost is offset
by the reduction in the number of upper events and in their fusion debt. -/
theorem packedForest_fused_budget_identity {n t r : Nat}
    (hr : 2 ≤ r) (hrt : r < t) (htn : t ≤ n) :
    (2*n-1)*(n-t) + (2*t-r) + (t-r).choose 2 + n*(2*t-r-2) +
      (n*(n-1)-(n-r)^2) + (r-1).choose 2 + 3*(n-t) +
      ((n-r).choose 2 - (t-r).choose 2) + (2*n-3) =
      (2*(n-r)-1) + packedUpperBudget n n + (n-1) := by
  have hn : 2 ≤ n := by omega
  have hchoose : (t-r).choose 2 ≤ (n-r).choose 2 :=
    Nat.choose_le_choose 2 (by omega)
  have hsq := terminal_square_le (show 1 ≤ r by omega) (show r ≤ n by omega)
  rw [packedUpperBudget_self hn]
  zify
  push_cast [Nat.cast_sub hchoose, Nat.cast_sub hsq,
    Nat.cast_sub (show t ≤ n by omega), Nat.cast_sub (show r ≤ n by omega),
    Nat.cast_sub (show r ≤ 2*t by omega), Nat.cast_sub (show 2 ≤ 2*t-r by omega),
    Nat.cast_sub (show 1 ≤ n by omega), Nat.cast_sub (show 1 ≤ r by omega),
    Nat.cast_sub (show 1 ≤ 2*n by omega), Nat.cast_sub (show 3 ≤ 2*n by omega),
    Nat.cast_sub (show 1 ≤ 2*(n-r) by omega)]
  have hb := twice_choose_two_int n
  have hg := twice_choose_two_int (n-r)
  have hr' := twice_choose_two_int (r-1)
  push_cast [Nat.cast_sub (show r ≤ n by omega), Nat.cast_sub (show 1 ≤ r by omega)] at hg hr'
  nlinarith only [hg, hr', hb]

/-- The additive replay budget retains the rank margin and all reductions
in the fused upper and terminal replay bounds. -/
theorem packedForest_fused_budget {n t r lowerCost upperCost finishCost lowerMax
    partitionCost fusionSaving terminalSaving : Nat}
    (hr : 2 ≤ r) (hrt : r < t) (htn : t ≤ n)
    (hlower : lowerCost ≤ lowerMax + (2*n-1)*(n-t))
    (hupper : upperCost + fusionSaving ≤ (2*t-r) + (t-r).choose 2 + n*(2*t-r-2))
    (hfinish : finishCost + terminalSaving ≤ n*(n-1)-(n-r)^2)
    (hpartition : 2*(n-r)-1 ≤ partitionCost) :
    lowerCost + upperCost + finishCost + fusionSaving + terminalSaving +
      (r-1).choose 2 + 3*(n-t) + ((n-r).choose 2 - (t-r).choose 2) + (2*n-3) ≤
      partitionCost + lowerMax + packedUpperBudget n n + (n-1) := by
  have hscalar := packedForest_fused_budget_identity hr hrt htn
  omega

/-- Without upper fusions the rank is exactly the number of transfers.
The cap for the winding charge is n*(t-1) in this case. -/
theorem packedForest_unfused_budget_identity {n t : Nat}
    (ht : 2 ≤ t) (htn : t < n) :
    (2*n-1)*(n-t) + t + n*(t-1) + (n*(n-1)-(n-t)^2) + (2*n-3) +
      (t-2).choose 2 + (n-t).choose 2 + 2*(n-t) =
      (2*(n-t)-1) + packedUpperBudget n n + (n-1) + 2 := by
  have hn : 2 ≤ n := by omega
  have hsq := terminal_square_le (show 1 ≤ t by omega) htn.le
  rw [packedUpperBudget_self hn]
  zify
  push_cast [Nat.cast_sub hsq, Nat.cast_sub htn.le,
    Nat.cast_sub (show 1 ≤ n by omega), Nat.cast_sub (show 1 ≤ t by omega),
    Nat.cast_sub (show 1 ≤ 2*n by omega), Nat.cast_sub (show 3 ≤ 2*n by omega),
    Nat.cast_sub (show 1 ≤ 2*(n-t) by omega)]
  have hb := twice_choose_two_int n
  have ht' := twice_choose_two_int (t-2)
  have hp := twice_choose_two_int (n-t)
  push_cast [Nat.cast_sub ht, Nat.cast_sub htn.le] at ht' hp
  nlinarith only [ht', hp, hb]

/-- Any winding saving enters additively in the case with no upper fusions.
The proof only needs one lower prefusion to cover the constant term. -/
theorem packedForest_unfused_budget {n t lowerCost upperCost finishCost lowerMax
    partitionCost phaseSaving : Nat}
    (ht : 2 ≤ t) (htn : t < n)
    (hlower : lowerCost ≤ lowerMax + (2*n-1)*(n-t))
    (hupper : upperCost + phaseSaving ≤ t + n*(t-1))
    (hfinish : finishCost ≤ n*(n-1)-(n-t)^2)
    (hpartition : 2*(n-t)-1 ≤ partitionCost) :
    lowerCost + upperCost + finishCost + phaseSaving +
      ((t-2).choose 2 + (n-t).choose 2 + 2*(n-t)-2) + (2*n-3) ≤
      partitionCost + lowerMax + packedUpperBudget n n + (n-1) := by
  have hscalar := packedForest_unfused_budget_identity ht htn
  omega

end RSR2History
