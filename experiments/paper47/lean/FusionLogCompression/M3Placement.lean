import FusionLogCompression.M3CyclicSchedule
import FusionLogCompression.FullFusionLog

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]
variable {α : Type*} [DecidableEq α]

theorem gapFramePlacement_phase (F : Finset α) (s : Execution n α)
    (start target : GapFrame n r α) (source : s.placed = start.decode)
    (gaps : start.gap = target.gap) (blocks : start.block = target.block) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = {s with placed := target.decode} ∧ word.length ≤ n - 1 := by
  let phase := target.anchor - start.anchor
  refine ⟨pWord phase.val, fusionFree_pWord F s _, ?_, ?_⟩
  · rw [run_rotation, source]
    have h := start.decode_phase target gaps blocks
    change {s with placed := rotate phase start.decode} = _
    rw [h]
  · rw [pWord_length]
    have h := ZMod.val_lt phase
    omega

/-- M3: the plan is followed by one charged rotation to the literal target. -/
theorem gapFramePlacement_short (F : Finset α) (s : Execution n α)
    (start target : GapFrame n r α) (hn : 3 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = start.decode) (blocks : start.block = target.block) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = {s with placed := target.decode} ∧
      word.length ≤ (3 * n - r) * (r - 1) + (n - 1) := by
  obtain ⟨mid, plan, gaps, names, hK, hM⟩ :=
    gapFramePlacement_plan F s start target hn hr source
  have hrn : r ≤ n := by
    have h := Fintype.card_le_of_injective start.position start.position_injective
    simpa using h
  let phase := target.anchor - mid.anchor
  obtain ⟨free, executed, cost⟩ :=
    batchPlan_gap_budget_with_phase F s mid.decode r plan phase hrn hK hM
  refine ⟨plan.word ++ pWord phase.val, free, ?_, cost⟩
  have hrotate := mid.decode_phase target gaps (names.trans blocks)
  change rotate phase mid.decode = target.decode at hrotate
  rwa [hrotate] at executed

/-- Uniform same-order placement, including the independent rank-one case. -/
theorem sameOrderPlacement_short (F : Finset α) (s : Execution n α)
    (first second : NamedCyclicPlacement n r α) (hn : 3 ≤ n)
    (source : s.placed = first.placed) (blocks : first.block = second.block) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = {s with placed := second.placed} ∧
      word.length ≤ (3 * n - r) * (r - 1) + (n - 1) := by
  have hsource : s.placed = first.toGapFrame.decode := by
    rwa [first.toGapFrame_decode]
  have hblocks : first.toGapFrame.block = second.toGapFrame.block := by
    simpa using blocks
  by_cases hone : r = 1
  · subst r
    have gaps : first.toGapFrame.gap = second.toGapFrame.gap := by
      funext i
      have hi : i = 0 := Subsingleton.elim _ _
      subst i
      have hfirst : first.toGapFrame.gap 0 = n - 1 := by
        calc
          _ = ∑ j : ZMod 1, first.toGapFrame.gap j := by
            calc
              _ = ∑ _j : ZMod 1, first.toGapFrame.gap 0 := by simp
              _ = _ := Finset.sum_congr rfl (fun j _ =>
                congrArg first.toGapFrame.gap (Subsingleton.elim 0 j))
          _ = n - 1 := first.toGapFrame.gap_total
      have hsecond : second.toGapFrame.gap 0 = n - 1 := by
        calc
          _ = ∑ j : ZMod 1, second.toGapFrame.gap j := by
            calc
              _ = ∑ _j : ZMod 1, second.toGapFrame.gap 0 := by simp
              _ = _ := Finset.sum_congr rfl (fun j _ =>
                congrArg second.toGapFrame.gap (Subsingleton.elim 0 j))
          _ = n - 1 := second.toGapFrame.gap_total
      exact hfirst.trans hsecond.symm
    obtain ⟨word, free, executed, cost⟩ :=
      gapFramePlacement_phase F s first.toGapFrame second.toGapFrame hsource gaps hblocks
    refine ⟨word, free, ?_, ?_⟩
    · rwa [second.toGapFrame_decode] at executed
    · simpa using cost
  · have hr : 2 ≤ r := by have := NeZero.pos r; omega
    obtain ⟨word, free, executed, cost⟩ :=
      gapFramePlacement_short F s first.toGapFrame second.toGapFrame hn hr hsource hblocks
    exact ⟨word, free, by rwa [second.toGapFrame_decode] at executed, cost⟩

/-- The same M3 word preserves every event in the complete ordered log. -/
theorem sameOrderPlacement_logged (F : Finset α) (s : LoggedExecution n α)
    (first second : NamedCyclicPlacement n r α) (hn : 3 ≤ n)
    (source : s.state.placed = first.placed) (blocks : first.block = second.block) :
    ∃ word : List Letter,
      FusionFree F s.state word ∧
      (runLogged F s word).state = {s.state with placed := second.placed} ∧
      (runLogged F s word).fullLog = s.fullLog ∧
      word.length ≤ (3 * n - r) * (r - 1) + (n - 1) := by
  obtain ⟨word, free, executed, cost⟩ :=
    sameOrderPlacement_short F s.state first second hn source blocks
  refine ⟨word, free, ?_, runLogged_log_eq_of_fusionFree F s word free, cost⟩
  rw [runLogged_state, executed]

end FusionLogCompression
