import FusionLogAllR.RawAllRBridge

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! The first registration and the subsequent fusion intervals are extracted
from the same chronological word. No numerical cost certificate is assumed. -/

theorem fusionFree_full_only_rotations {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (word : List Letter) (hfull : ∀ q, s.placed q ≠ none)
    (hfree : FusionFree F s word) : word = pWord word.length := by
  induction word generalizing s with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p =>
          have hnext : ∀ q, (step F s .p).placed q ≠ none := by
            intro q
            exact hfull (q - 1)
          have hr := ih (step F s .p) hnext hfree
          have hp : ∀ k, pWord (k + 1) = .p :: pWord k := by
            intro k
            induction k with
            | zero => rfl
            | succ k hk =>
                change pWord (k + 1) ++ [.p] = .p :: (pWord k ++ [.p])
                rw [hk]
                rfl
          simpa only [List.length_cons, hp] using congrArg (List.cons .p) hr
      | d =>
          rcases hfree.1 with h0 | h1
          · exact (hfull 0 h0).elim
          · exact (hfull 1 h1).elim

theorem pWord_count_d (k : ℕ) : (pWord k).count .d = 0 := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pWord, ih]

/-- A full turn before the first defect may be redundant, but the specified
ordered registration forces its rotation residue to be zero. -/
theorem RealizesAllR.registration_prefix {n : ℕ} [NeZero n]
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    ∃ (pre post : List Letter), word = pre ++ [.d] ++ post ∧
      pre = pWord pre.length ∧
      (pre.length : ZMod n) = 0 ∧
      (pre ++ [Letter.d]).count Letter.d = 1 ∧
      run (allRSelectedPair n) (singletonExecution n) pre = singletonExecution n ∧
      completeFusionLog (allRSelectedPair n)
        (run (allRSelectedPair n) (singletonExecution n) (pre ++ [.d])) post =
          allRPostLog n := by
  obtain ⟨pre, post, hw, hf, h0, _, _, hl⟩ :=
    completeFusionLog_first (allRSelectedPair n) (singletonExecution n)
      word (allRRegistration n) (allRPostLog n) h.log_eq
  have hp : pre = pWord pre.length :=
    fusionFree_full_only_rotations (allRSelectedPair n) (singletonExecution n)
      pre (by intro q; simp [singletonExecution]) hf
  have hrotate := run_pWord (allRSelectedPair n) (singletonExecution n) pre.length
  let rotated : Execution n (ZMod n) :=
    { placed := rotate (pre.length : ZMod n) (singletonExecution n).placed
      origin := (singletonExecution n).origin
      chain := (singletonExecution n).chain }
  have hr : run (allRSelectedPair n) (singletonExecution n) pre = rotated := by
    conv_lhs => rw [hp]
    simpa [rotated] using hrotate
  have hzero : (pre.length : ZMod n) = 0 := by
    rw [hr] at h0
    have hsingle : ({-(pre.length : ZMod n)} : Finset (ZMod n)) = {0} := by
      simpa [rotated, rotate, singletonExecution, allRRegistration] using h0
    have hneg : -(pre.length : ZMod n) = 0 := Finset.singleton_injective hsingle
    simpa using hneg
  have hseed : run (allRSelectedPair n) (singletonExecution n) pre =
      singletonExecution n := by
    rw [hr]
    dsimp [rotated]
    rw [hzero, rotate_zero]
  refine ⟨pre, post, ?_, hp, hzero, ?_, hseed, ?_⟩
  · simpa using hw
  · have hc := congrArg (List.count Letter.d) hp
    rw [pWord_count_d] at hc
    simp [List.count_append, hc]
  · simpa [run_append, run] using hl

def allRRegistered {n : ℕ} [NeZero n] : Execution n (ZMod n) :=
  step (allRSelectedPair n) (singletonExecution n) .d

theorem allRRegistered_zero {n : ℕ} [NeZero n] :
    (allRRegistered (n := n)).placed 0 = some (allRSelectedPair n) := by
  simp [allRRegistered, step, stepDefect, fusionPlacement, singletonExecution,
    allRSelectedPair]

theorem allRRegistered_other {n : ℕ} [NeZero n]
    (q : ZMod n) (hq0 : q ≠ 0) (hq1 : q ≠ 1) :
    (allRRegistered (n := n)).placed q = some {q} := by
  simp [allRRegistered, step, stepDefect, fusionPlacement, singletonExecution,
    allRSelectedPair, hq0, hq1]

/-- The extracted state is literally the result of running the extracted
registration prefix. All allowed initial full rotations give this same state. -/
theorem RealizesAllR.registered_suffix {n : ℕ} [NeZero n]
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    ∃ registrationPrefix post,
      word = registrationPrefix ++ post ∧
      registrationPrefix.count .d = 1 ∧
      run (allRSelectedPair n) (singletonExecution n) registrationPrefix =
        allRRegistered ∧
      completeFusionLog (allRSelectedPair n) allRRegistered post = allRPostLog n ∧
      RightCarrierRun (allRSelectedPair n) 0 allRRegistered post := by
  obtain ⟨pre, post, hw, _, _, hd, hseed, hl⟩ := h.registration_prefix
  have hstart : run (allRSelectedPair n) (singletonExecution n) (pre ++ [.d]) =
      allRRegistered := by
    rw [run_append, hseed]
    rfl
  refine ⟨pre ++ [.d], post, hw, hd, hstart, ?_, ?_⟩
  · simpa [hstart] using hl
  · simpa [hstart] using h.post_rightCarrierRun hw

theorem RealizesAllR.fusion_intervals {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} (h : RealizesAllR (n := n) word) :
    ∃ registrationPrefix inter tail afterInter,
      word = registrationPrefix ++ (inter ++ tail) ∧
      registrationPrefix.count .d = 1 ∧
      run (allRSelectedPair n) (singletonExecution n) registrationPrefix =
        allRRegistered ∧
      RightFusionIntervals (allRSelectedPair n) 0 (n - 2)
        allRRegistered afterInter inter ∧
      completeFusionLog (allRSelectedPair n) allRRegistered (inter ++ tail) =
        allRPostLog n ∧
      (0 : ZMod n) ∈ (afterInter.placed 0).getD ∅ ∧
      FusionFree (allRSelectedPair n) afterInter tail ∧
      RightCarrierRun (allRSelectedPair n) 0 allRRegistered (inter ++ tail) := by
  obtain ⟨reg, post, hw, hd, hs, hl, hr⟩ := h.registered_suffix
  have hmarked : (0 : ZMod n) ∈ ((allRRegistered (n := n)).placed 0).getD ∅ := by
    simp [allRRegistered_zero, allRSelectedPair]
  have hhole : (allRRegistered (n := n)).placed 1 = none :=
    defect_port_one_empty (allRSelectedPair n) (singletonExecution n) (by omega)
  obtain ⟨inter, tail, afterInter, hpost, hi, ha, hf⟩ :=
    rightFusionIntervals_of_completeFusionLog (allRSelectedPair n) 0 (by omega)
      (allRPostLog n) allRRegistered post hmarked hhole hl
      (rightFusionLog_left_mem (allRSelectedPair n) (allRPartners n) 0
        (by simp [allRSelectedPair]))
  refine ⟨reg, inter, tail, afterInter, ?_, hd, hs, ?_, ?_, ha, hf, ?_⟩
  · exact hw.trans (congrArg (reg ++ ·) hpost)
  · simpa only [allRPostLog_length] using hi
  · rw [← hpost]
    exact hl
  · simpa only [hpost] using hr

end FusionLogAllR
