import RSR2History.UpperCursorAccounting

/-!
Scalar comparison of upper cursor budgets at different transfer counts.
The final implication retains both replay and independent lower-cost bounds
as explicit hypotheses. It does not prove a packed lower amortized bound.
-/
namespace RSR2History

def packedUpperBudget (n t : Nat) : Nat :=
  2*t-1+(t-1).choose 2+n*(2*t-3)

private theorem twice_choose_two (k : Nat) : 2*k.choose 2 = k*(k-1) := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self k
  rw [Nat.choose_two_right]
  omega

theorem packedUpperBudget_eq_choose {n t : Nat} (ht : 2 ≤ t) :
    packedUpperBudget n t = (t+1).choose 2+n*(2*t-3) := by
  have hbefore := twice_choose_two (t-1)
  have hafter := twice_choose_two (t+1)
  have ht1 := Nat.sub_add_cancel (show 1 ≤ t by omega)
  have ht2 := Nat.sub_add_cancel (show 1 ≤ t-1 by omega)
  have ht3 := Nat.sub_add_cancel (show 1 ≤ 2*t by omega)
  simp only [Nat.add_sub_cancel] at hafter
  unfold packedUpperBudget
  nlinarith

theorem packedUpperBudget_self {n : Nat} (hn : 2 ≤ n) :
    packedUpperBudget n n = 5*n.choose 2 :=
  singleton_upper_budget_identity hn

theorem packedUpperBudget_release {n t : Nat} (ht : 2 ≤ t) (htn : t ≤ n) :
    packedUpperBudget n n = packedUpperBudget n t + (n-t)*(5*n+t+1)/2 := by
  have hn : 2 ≤ n := le_trans ht htn
  have hcn := twice_choose_two (n+1)
  have hct := twice_choose_two (t+1)
  have hnt := Nat.sub_add_cancel htn
  have h3n := Nat.sub_add_cancel (show 3 ≤ 2*n by omega)
  have h3t := Nat.sub_add_cancel (show 3 ≤ 2*t by omega)
  simp only [Nat.add_sub_cancel] at hcn hct
  have hd : 2*packedUpperBudget n n =
      2*packedUpperBudget n t + (n-t)*(5*n+t+1) := by
    rw [packedUpperBudget_eq_choose hn, packedUpperBudget_eq_choose ht]
    nlinarith
  omega

theorem packedUpperBudget_release_one {n : Nat} (hn : 3 ≤ n) :
    packedUpperBudget n n = packedUpperBudget n (n-1)+3*n := by
  have h := packedUpperBudget_release (n := n) (t := n-1) (by omega) (by omega)
  have he : (n-(n-1))*(5*n+(n-1)+1)/2 = 3*n := by
    have hp := Nat.sub_add_cancel (show 1 ≤ n by omega)
    have hs : n-(n-1) = 1 := by omega
    rw [hs, Nat.one_mul]
    omega
  simpa only [he] using h

theorem packedUpperBudget_release_two {n : Nat} (hn : 4 ≤ n) :
    packedUpperBudget n n = packedUpperBudget n (n-2)+(6*n-1) := by
  have h := packedUpperBudget_release (n := n) (t := n-2) (by omega) (by omega)
  have he : (n-(n-2))*(5*n+(n-2)+1)/2 = 6*n-1 := by
    have hp := Nat.sub_add_cancel (show 2 ≤ n by omega)
    have hs : n-(n-2) = 2 := by omega
    rw [hs]
    omega
  simpa only [he] using h

/-- A sufficient scalar criterion only. The physical replay and packed lower
amortization are independent hypotheses, not consequences of this identity. -/
theorem packed_replay_budget_of_lower_bound {n t cost lower K : Nat}
    (ht : 2 ≤ t) (htn : t ≤ n)
    (hreplay : cost ≤ lower+packedUpperBudget n t+(n-1))
    (hlower : lower ≤ K+(n-t)*(5*n+t+1)/2) :
    cost ≤ K+5*n.choose 2+(n-1) := by
  have hn : 2 ≤ n := le_trans ht htn
  have hrelease := packedUpperBudget_release ht htn
  rw [packedUpperBudget_self hn] at hrelease
  omega

end RSR2History
