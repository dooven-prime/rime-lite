import RSR2History.EventResourceLedger

/-!
Arithmetic for reserved-site replay, separate from the physical construction.
The final theorem has an explicit replay cost premise, discharged by
`QuadraticHistoryCompression.history_fiber_reservation_bound`. This module
alone does not construct a witness.
-/
namespace RSR2History
open RSR2.Parametric

theorem layerBudget_le_linear_rank (n rank : Nat) (hr : 0 < rank) :
    layerBudget n rank ≤ 4*n*(rank-1)+(n-1) := by
  unfold layerBudget
  rw [if_neg (by omega)]
  exact Nat.add_le_add_right
    (Nat.mul_le_mul_right (rank-1) (show 3*n-rank ≤ 4*n by omega)) _

/-- A single terminal rank budget covers both layers; empty layers cost zero. -/
theorem layerBudget_pair_le (n r0 r1 : Nat) (hn : 0 < n) (hr : 0 < r0+r1) :
    layerBudget n r0 + layerBudget n r1 ≤ 4*n*(r0+r1-1)+(n-1) := by
  by_cases hz0 : r0 = 0
  · subst r0
    simpa [layerBudget] using layerBudget_le_linear_rank n r1 (by omega)
  by_cases hz1 : r1 = 0
  · subst r1
    simpa [layerBudget] using layerBudget_le_linear_rank n r0 (by omega)
  have h0 := layerBudget_le_linear_rank n r0 (by omega)
  have h1 := layerBudget_le_linear_rank n r1 (by omega)
  have he : r0+r1-1 = (r0-1)+(r1-1)+1 := by omega
  rw [he, Nat.mul_add, Nat.mul_add, Nat.mul_one]
  omega

/-- This is a resource-coupled sum, not a new geometric assumption. -/
theorem reservation_budget_le_uniform (n F V r0 r1 : Nat)
    (hn : 0 < n) (hr : 0 < r0+r1) (hF : F+(r0+r1) = n) (hV : V ≤ n) :
    4*n*F+(2*n+1)*V+layerBudget n r0+layerBudget n r1 ≤ 6*n*n-2*n-1 := by
  have htail := layerBudget_pair_le n r0 r1 hn hr
  have hsum : F+(r0+r1-1) = n-1 := by omega
  calc
    _ ≤ 4*n*F+(2*n+1)*V+(4*n*(r0+r1-1)+(n-1)) := by omega
    _ = 4*n*(F+(r0+r1-1))+(2*n+1)*V+(n-1) := by ring
    _ ≤ 4*n*(n-1)+(2*n+1)*n+(n-1) := by
      rw [hsum]
      exact Nat.add_le_add_right (Nat.add_le_add_left
        (Nat.mul_le_mul_left (2*n+1) hV) _) _
    _ = 6*n*n-2*n-1 := by
      have he : n-1+1 = n := by omega
      have hm := congrArg (fun k => 4*n*k) he
      simp only [Nat.mul_add, Nat.mul_one] at hm
      have hc : 4*n*(n-1)+(2*n+1)*n+(n-1)+2*n+1 = 6*n*n := by nlinarith
      omega

/-- Conditional arithmetic consequence for an attained observation. The
reserved-site physical replay must still supply `hcost` for an actual word. -/
theorem reservation_replay_length_le_uniform (n : Nat) (hn : 1 < n)
    {word replay : List Letter} {Q : Placement n} {events}
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hcost : replay.length ≤ 4*n*logFusionCount events +
      (2*n+1)*logTransferCount events+silentBudget n Q) :
    replay.length ≤ 6*n*n-2*n-1 := by
  classical
  obtain ⟨hf, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  rw [seed_totalPacketCount] at hf
  have hmass := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hmass
  have hV : logTransferCount events ≤ n := by omega
  have hrank : 0 < layerRank Q false + layerRank Q true := by
    let a : Fin n := ⟨0, by omega⟩
    have hoc : occupiedAt Q (Q a).1 (Q a).2 := ⟨a, rfl⟩
    have hr : 1 ≤ layerRank Q (Q a).1 := by
      rw [rank_countP]
      exact List.one_le_countP_iff.mpr ⟨(Q a).2, List.mem_finRange _, by simp [hoc]⟩
    cases h : (Q a).1 <;> simp only [h] at hr <;> omega
  have hF : logFusionCount events + (layerRank Q false + layerRank Q true) = n := by
    simp only [layerRank_lower, layerRank_upper]
    simpa only [totalPacketCount, Nat.add_comm] using hf
  have hbudget := reservation_budget_le_uniform n (logFusionCount events)
    (logTransferCount events) (layerRank Q false) (layerRank Q true) (by omega) hrank hF hV
  exact hcost.trans (by simpa only [silentBudget, Nat.add_assoc] using hbudget)

end RSR2History
