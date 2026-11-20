import RSR2History.ForestGapMomentRouting
import RSR2History.ForestStructuralDefect

/-! The tree, cross-root and terminal moment savings in one guarded replay account. -/

namespace RSR2History
open RSR2.Parametric

private theorem square_eq_choose_add_triangle (g : Nat) :
    g^2 = g.choose 2 + g*(g+1)/2 := by
  have hchoose : 2*g.choose 2 = g*(g-1) := by
    obtain ⟨q,hq⟩ := Nat.even_mul_pred_self g
    rw [Nat.choose_two_right]
    omega
  have hprod : g*(g-1) + g*(g+1) = 2*g^2 := by
    cases g with
    | zero => simp
    | succ g =>
        rw [Nat.add_sub_cancel]
        ring
  omega

namespace ForestReplayAccount

variable {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}

/-- Shared winding charge with the two endpoint cursor phases retained.
The charge is signed because the final phase is subtracted. -/
def windingCharge (r : ForestReplayAccount n hn Q H) : Int :=
  (n : Int)*r.schedule.windings + (r.site 0).val - r.finalCursor.val

/-- Combine the cross-root debt identity and the moment saving of this
account's own silent finish. -/
theorem structural_replay_budget (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length]
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2) :
    r.schedule.cost + r.finish.length + forestStructuralDefect r.terminal +
        r.finalCursor.val + (n-r.terminal.length)*(n-r.terminal.length+1)/2 ≤
      (2*n-r.terminal.length) + n*(n-1) + n*r.schedule.windings + (r.site 0).val := by
  have hp := r.schedule.forest_payment
  have he := r.schedule.forest_event_count
  have hc := r.cross_defect_account
  have hs := square_eq_choose_add_triangle (n-r.terminal.length)
  have hr : r.terminal.length ≤ n := by
    have hm := forestMergeMass_balance r.terminal
    rw [r.leaf_count] at hm
    omega
  have hsq : (n-r.terminal.length)^2 ≤ n*(n-1) := by
    have hg : n-r.terminal.length ≤ n-1 := by
      have hnz := NeZero.ne r.terminal.length
      omega
    calc
      (n-r.terminal.length)^2 =
          (n-r.terminal.length)*(n-r.terminal.length) := pow_two _
      _ ≤ n*(n-1) := Nat.mul_le_mul (by omega) hg
  unfold forestStructuralDefect
  omega

/-- The same budget in integers, with the full signed winding charge on
the right. -/
theorem structural_replay_winding_budget (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length]
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2) :
    (r.schedule.cost : Int) + r.finish.length + forestStructuralDefect r.terminal ≤
      ((2*n-r.terminal.length : Nat) : Int) + (n*(n-1) : Nat) -
        ((n-r.terminal.length)*(n-r.terminal.length+1)/2 : Nat) + r.windingCharge := by
  have h := r.structural_replay_budget hfinish
  have hz := Int.ofNat_le.mpr h
  push_cast at hz
  unfold windingCharge
  omega

/-- A bound on the combined winding charge and structural savings suffices
for the relative budget after retaining the actual extraction cost. -/
theorem structural_winding_charge_sufficient (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length] (hn3 : 3 ≤ n)
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2)
    (hcharge : r.windingCharge - (forestStructuralDefect r.terminal : Int) ≤
      r.relativeBase - ((maxLowerExtractionCost n hn-r.extractionCost : Nat) : Int) -
        ((n-r.terminal.length).choose 2 : Nat) -
        ((n*(n-1)-(n-r.terminal.length)^2 : Nat) : Int)) :
    r.premium + (maxLowerExtractionCost n hn-r.extractionCost) ≤
      delayedChainTotalPremiumMaximum n hn3 := by
  have hs := r.relative_slack_with_cross_defect hn3
  have hnonneg : (0 : Int) ≤ (r.replayExcess : Int) := Int.natCast_nonneg _
  have hfd : (r.finish.length : Int) + forestGapMoment (forestRootGapProfile r.terminal) ≤
      ((n*(n-1)-(n-r.terminal.length)^2 : Nat) : Int) := by exact_mod_cast hfinish
  unfold defectJointCharge at hs
  unfold windingCharge forestStructuralDefect at hcharge
  simp only [Nat.cast_add] at hcharge
  omega

end ForestReplayAccount

/-- A single actual account pays the complete event replay and its chosen
silent terminal route, retaining all three structural savings. -/
theorem forest_structural_replay_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (rank : 2 ≤ terminal.length) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal ∧
      (∀ a ∈ forestLeaves terminal,
        (account.site a).val = (forestLeaves terminal).idxOf a) ∧
      (account.schedule.cost : Int) + account.finish.length + forestStructuralDefect terminal ≤
        ((2*n-terminal.length : Nat) : Int) + (n*(n-1) : Nat) -
          ((n-terminal.length)*(n-terminal.length+1)/2 : Nat) + account.windingCharge := by
  obtain ⟨account, hterminal, hsite, hfinish⟩ :=
    forest_terminal_moment_account_of_trace hn word run upper singletons trace rank
  refine ⟨account,hterminal,hsite,?_⟩
  have hrank : 2 ≤ account.terminal.length := by rwa [hterminal]
  let : NeZero account.terminal.length := ⟨by omega⟩
  have hm : forestGapMoment (forestRootGapProfile account.terminal) =
      forestGapMoment (forestRootGapProfile terminal) := by
    cases hterminal
    rfl
  have hd : forestStructuralDefect account.terminal = forestStructuralDefect terminal := by
    cases hterminal
    rfl
  have hfinish' : account.finish.length +
      forestGapMoment (forestRootGapProfile account.terminal) ≤
        n*(n-1)-(n-account.terminal.length)^2 := by
    rw [hm, hterminal]
    exact hfinish
  have h := account.structural_replay_winding_budget hfinish'
  simpa only [hd,hterminal] using h

end RSR2History
