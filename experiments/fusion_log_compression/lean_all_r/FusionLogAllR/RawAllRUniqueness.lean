import FusionLogAllR.StageSlideRigidity

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # From raw minimum length to literal all-right rigidity

Idle defects can be deleted without changing either the complete event log
or the actual terminal state.  Thus a raw realization attaining the proved
minimum supplies the active-defect premise of the local stage theorem.
Exact rotation budgets then force each literal stage in sequence; the
canonical boundary after each stage is proved by actual execution.  The
rank-one tail is handled separately, yielding raw-word uniqueness directly
from `RealizesAllR` and minimum length.
-/

theorem step_defect_eq_self_of_port_one_empty {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (h1 : s.placed 1 = none) : step F s .d = s := by
  have hplacement : fusionPlacement s.placed = s.placed := by
    funext q
    by_cases hq0 : q = 0
    · subst q
      cases h0 : s.placed 0 <;> simp [fusionPlacement, h0, h1]
    by_cases hq1 : q = 1
    · subst q
      simp [fusionPlacement, hq0, h1]
    · simp [fusionPlacement, hq0, hq1]
  cases h0 : s.placed 0 <;>
    simp [step, stepDefect, h0, h1, hplacement]

/-- A failure of activity exposes a real removable defect, rather than an
independently chosen counterexample state. -/
theorem inactive_defect_decomposition {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (word : List Letter) (hinactive : ¬ActiveDefectsRun F start word) :
    ∃ pre post, word = pre ++ .d :: post ∧
      (run F start pre).placed 1 = none := by
  induction word generalizing start with
  | nil => exact (hinactive trivial).elim
  | cons letter rest ih =>
      cases letter with
      | p =>
          obtain ⟨pre, post, hw, h1⟩ := ih (step F start .p) hinactive
          exact ⟨.p :: pre, post, by simp [hw], h1⟩
      | d =>
          by_cases h1 : start.placed 1 = none
          · exact ⟨[], rest, rfl, h1⟩
          · have hr : ¬ActiveDefectsRun F (step F start .d) rest := by
              intro hrest
              exact hinactive ⟨h1, hrest⟩
            obtain ⟨pre, post, hw, hport⟩ := ih (step F start .d) hr
            exact ⟨.d :: pre, post, by simp [hw], hport⟩

theorem RealizesAllR.minimal_activeDefectsRun {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (3 * n * (n - 1)) / 2 - 1) :
    ActiveDefectsRun (allRSelectedPair n) (singletonExecution n) word := by
  by_contra hinactive
  obtain ⟨pre, post, hword, h1⟩ := inactive_defect_decomposition
    (allRSelectedPair n) (singletonExecution n) word hinactive
  have hstep := step_defect_eq_self_of_port_one_empty
    (allRSelectedPair n) (run (allRSelectedPair n) (singletonExecution n) pre) h1
  have hlog : completeFusionLog (allRSelectedPair n) (singletonExecution n)
      word = completeFusionLog (allRSelectedPair n) (singletonExecution n) (pre ++ post) := by
    rw [hword, completeFusionLog_append, completeFusionLog_append]
    simp [completeFusionLog, h1, hstep]
  have hrun : run (allRSelectedPair n) (singletonExecution n) word =
      run (allRSelectedPair n) (singletonExecution n) (pre ++ post) := by
    rw [hword, run_append, run_append]
    change run _ (step _ _ .d) post = _
    rw [hstep]
  have hshort : RealizesAllR (n := n) (pre ++ post) :=
    ⟨hlog ▸ h.log_eq, by rw [← hrun]; exact h.endpoint_eq⟩
  have hlower := hshort.word_length_lower_bound hn
  have hlength : word.length = pre.length + post.length + 1 := by
    simp [hword]
    omega
  simp only [List.length_append] at hlower
  omega

/-- The same actual interval extraction as in the lower-bound proof, at an
arbitrary remaining chain length.  Only the marked terminal site is used. -/
theorem completeLog_rotation_lower_bound {n : ℕ} [NeZero n]
    (hn : 2 ≤ n) (F : Finset (ZMod n))
    (start : Execution n (ZMod n)) (word : List Letter)
    (records : List (FusionRecord (ZMod n)))
    (ordered : SourceOrdered start.placed)
    (hstart : (0 : ZMod n) ∈ (start.placed 0).getD ∅)
    (hhole : start.placed 1 = none)
    (hlog : completeFusionLog F start word = records)
    (hleft : ∀ rho ∈ records, (0 : ZMod n) ∈ rho.left)
    (hend : ∃ B, (run F start word).placed ((n - 1 : ℕ) : ZMod n) = some B ∧
      (0 : ZMod n) ∈ B) :
    records.length * n + (n - 1) ≤ word.count .p := by
  obtain ⟨inter, tail, afterInter, hw, intervals, hmarked, hfree⟩ :=
    rightFusionIntervals_of_completeFusionLog F 0 hn records start word
      hstart hhole hlog hleft
  have hinter := intervals.rotation_lower_bound hn ordered
  have horder := intervals.run_eq ▸ run_ordered F start inter hn ordered
  obtain ⟨C, hC, haC⟩ : ∃ C, afterInter.placed 0 = some C ∧ (0 : ZMod n) ∈ C := by
    cases h0 : afterInter.placed 0 with
    | none => simp [h0] at hmarked
    | some C => exact ⟨C, rfl, by simpa [h0] using hmarked⟩
  obtain ⟨B, hB, haB⟩ := hend
  have htailRun : run F afterInter tail = run F start word := by
    rw [hw, run_append, intervals.run_eq]
  have htail := actual_tail_rotation_lower_bound F afterInter tail 0 C B hn
    horder hC haC (by simpa [htailRun] using hB) haB
  have hcounts : word.count .p = inter.count .p + tail.count .p := by simp [hw]
  omega

def allRRemainingLog (n : ℕ) [NeZero n] (j : ℕ) : ℕ → List (FusionRecord (ZMod n))
  | 0 => []
  | k + 1 => ⟨allRCarrier n j, {((j + 1 : ℕ) : ZMod n)}, allRCarrier n (j + 1)⟩ ::
      allRRemainingLog n (j + 1) k

def allRRemainingWord (n j : ℕ) : ℕ → List Letter
  | 0 => pWord (n - 1)
  | k + 1 => allRStage n j ++ allRRemainingWord n (j + 1) k

theorem allRRemainingLog_length (n : ℕ) [NeZero n] (j k : ℕ) :
    (allRRemainingLog n j k).length = k := by
  induction k generalizing j with
  | zero => rfl
  | succ k ih => simp [allRRemainingLog, ih]

theorem allRRemainingLog_left_mem (n : ℕ) [NeZero n] (j k : ℕ) :
    ∀ rho ∈ allRRemainingLog n j k, (0 : ZMod n) ∈ rho.left := by
  induction k generalizing j with
  | zero => simp [allRRemainingLog]
  | succ k ih =>
      intro rho hrho
      rcases List.mem_cons.mp hrho with rfl | hrho
      · simp [allRCarrier]
      · exact ih (j + 1) rho hrho

private theorem remainingLog_eq_rightFusionLog {n : ℕ} [NeZero n]
    (j k : ℕ) (hjk : j + k < n) :
    rightFusionLog (allRCarrier n j)
      ((List.range k).map (fun i => ((j + 1 + i : ℕ) : ZMod n))) =
        allRRemainingLog n j k := by
  induction k generalizing j with
  | zero => rfl
  | succ k ih =>
      rw [List.range_succ_eq_map]
      simp only [List.map_cons, List.map_map, rightFusionLog, allRRemainingLog,
        Nat.add_zero]
      rw [allRCarrier_succ (by omega)]
      congr 1
      rw [← ih (j + 1) (by omega)]
      congr 1
      apply List.map_congr_left
      intro i hi
      simp only [Function.comp_apply]
      push_cast
      ring

private theorem remainingWord_eq_flatMap (n j k : ℕ) :
    allRRemainingWord n j k =
      (List.range k).flatMap (fun i => allRStage n (j + i)) ++ pWord (n - 1) := by
  induction k generalizing j with
  | zero => rfl
  | succ k ih =>
      rw [allRRemainingWord, ih, List.range_succ_eq_map]
      simp only [List.flatMap_cons, List.flatMap_map, Nat.add_zero,
        List.append_assoc]
      congr 2
      congr 1
      funext i
      simp [Nat.add_comm, Nat.add_left_comm]

private theorem atomDefectsPaid_of_constant_map {n z : ℕ} [NeZero n]
    (hn : 2 ≤ n) (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (word : List Letter)
    (hplaced : start.placed = placementOfMap f)
    (hconstant : ∀ a, f a = (z : ZMod n))
    (hactive : ActiveDefectsRun F start word) :
    AtomDefectsPaid n z word := by
  induction word generalizing start f z with
  | nil => trivial
  | cons letter rest ih =>
      have hplaced' := step_placementOfMap F start f letter hn hplaced
      cases letter with
      | p =>
          apply ih (z := z + 1) (step F start .p) (forwardMapStep f .p)
            hplaced' _ hactive
          intro a
          simp [forwardMapStep, hconstant]
      | d =>
          have hz : (z : ZMod n) = 1 := by
            by_contra hz
            have hempty : sourceFiber f 1 = ∅ := by
              ext a
              simp [hconstant, hz]
            have hport := hactive.1
            rw [hplaced] at hport
            simp [placementOfMap, hempty] at hport
          refine ⟨hz, ih (step F start .d) (forwardMapStep f .d) hplaced' ?_ hactive.2⟩
          intro a
          have hc := (carrierHeightStep_cast n z hn .d).symm
          simpa [forwardMapStep, hconstant] using hc

/-- At the terminal full-carrier boundary, activity and the minimum tail
rotation budget exclude even zero-potential rank-one backslides. -/
theorem allR_tail_word_unique {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced (n - 1))
    (word : List Letter) (hactive : ActiveDefectsRun F start word)
    (hp : word.count .p = n - 1)
    (hend : ∃ B, (run F start word).placed ((n - 1 : ℕ) : ZMod n) = some B ∧
      (0 : ZMod n) ∈ B) :
    word = pWord (n - 1) := by
  have hfull : allRCarrier n (n - 1) = Finset.univ := by
    ext a
    have hval := ZMod.val_lt a
    simp only [allRCarrier, Finset.mem_filter, Finset.mem_univ, true_and, iff_true]
    omega
  have h0 : start.placed 0 = some Finset.univ := by
    simp [hstart, allRBoundaryPlaced, hfull]
  obtain ⟨lift, hplaced⟩ := ordered
  have hsource := (placementOfMap_some_iff lift.position 0 Finset.univ).mp
    (hplaced ▸ h0)
  have hconstant : ∀ a, lift.position a = (0 : ZMod n) := by
    intro a
    exact (mem_sourceFiber lift.position a 0).mp (hsource.1.symm ▸ Finset.mem_univ a)
  have hpaid := atomDefectsPaid_of_constant_map (z := 0) (by omega) F start lift.position
    word hplaced (by simpa only [Nat.cast_zero] using hconstant) hactive
  obtain ⟨B, hB, haB⟩ := hend
  have hsite := carrierHeightRun_site F start lift.position 0 ((n - 1 : ℕ) : ZMod n)
    0 word B (by omega) hplaced (by simpa only [Nat.cast_zero] using hconstant 0) hB haB
  have hb := carrierHeightRun_balance n 0 (by omega) word
  have hd := hpaid.downSteps_eq_count
  rw [hp] at hb
  have hval := congrArg ZMod.val hsite
  rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_natCast_of_lt (by omega)] at hval
  have hnod : word.count .d = 0 := by omega
  simpa [hp] using word_eq_pWord_of_no_defects word hnod

/-- Stage induction at the raw execution interface.  Only the remaining
complete log, its exact rotation budget, activity, and marked terminal site
are assumed.  Every intermediate canonical boundary is a conclusion of the
local stage theorem and its already proved actual execution. -/
theorem allRRemainingWord_unique {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (j k : ℕ) (hj : 1 ≤ j) (hjk : j + k = n - 1)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    (word : List Letter)
    (hlog : completeFusionLog F start word = allRRemainingLog n j k)
    (hp : word.count .p = k * n + (n - 1))
    (hactive : ActiveDefectsRun F start word)
    (hend : ∃ B, (run F start word).placed ((n - 1 : ℕ) : ZMod n) = some B ∧
      (0 : ZMod n) ∈ B) :
    word = allRRemainingWord n j k := by
  have : Fact (1 < n) := ⟨by omega⟩
  induction k generalizing j start word with
  | zero =>
      have hj' : j = n - 1 := by omega
      subst j
      exact allR_tail_word_unique hn F start ordered hstart word hactive
        (by simpa using hp) hend
  | succ k ih =>
      have hjn : j ≤ n - 2 := by omega
      let rho : FusionRecord (ZMod n) :=
        ⟨allRCarrier n j, {((j + 1 : ℕ) : ZMod n)}, allRCarrier n (j + 1)⟩
      obtain ⟨pre, post, hword, hfree, h0, h1, hunion, hpostlog⟩ :=
        completeFusionLog_first F start word rho (allRRemainingLog n (j + 1) k) hlog
      have hstart0 : start.placed 0 = some (allRCarrier n j) := by
        simp [hstart, allRBoundaryPlaced]
      have hstart1 : start.placed 1 = none := by
        simp [hstart, allRBoundaryPlaced, ZMod.val_one, hj]
      have haC : (0 : ZMod n) ∈ allRCarrier n j := by simp [allRCarrier]
      have hpreBound := actual_interFusion_rotation_lower_bound F start pre 0
        (allRCarrier n j) (allRCarrier n j) (by omega) ordered hstart0 haC hstart1
        h0 haC (by simp [h1])
      let next := step F (run F start pre) .d
      have hnextOrder : SourceOrdered next.placed :=
        step_ordered F _ .d (by omega) (run_ordered F start pre (by omega) ordered)
      have hnext0 : next.placed 0 = some (allRCarrier n (j + 1)) := by
        change (stepDefect F (run F start pre)).placed 0 = _
        rw [stepDefect_placed]
        simpa [fusionPlacement, h0, h1, rho] using
          congrArg some (allRCarrier_succ (n := n) (j := j) (by omega))
      have hnextMarked : (0 : ZMod n) ∈ (next.placed 0).getD ∅ := by
        simp [hnext0, allRCarrier]
      have hpostEnd : ∃ B,
          (run F next post).placed ((n - 1 : ℕ) : ZMod n) = some B ∧
            (0 : ZMod n) ∈ B := by
        simpa [hword, run_append, run, next] using hend
      have hpostBound := completeLog_rotation_lower_bound (by omega) F next post
        (allRRemainingLog n (j + 1) k) hnextOrder hnextMarked
        (defect_port_one_empty F _ (by omega)) hpostlog
        (allRRemainingLog_left_mem n (j + 1) k) hpostEnd
      rw [allRRemainingLog_length] at hpostBound
      have hcounts : pre.count .p + post.count .p = (k + 1) * n + (n - 1) := by
        simpa [hword] using hp
      have hpreP : pre.count .p = n := by
        rw [Nat.succ_mul] at hcounts
        omega
      have hpostP : post.count .p = k * n + (n - 1) := by
        rw [Nat.succ_mul] at hcounts
        omega
      have hsplit : word = (pre ++ [.d]) ++ post := by simp [hword]
      obtain ⟨hpreActive, hpostActive⟩ :=
        (activeDefectsRun_append F start (pre ++ [.d]) post).mp (hsplit ▸ hactive)
      have hstage : pre ++ [.d] = allRStage n j :=
        allRStage_word_unique_of_active hn hj hjn F start ordered hstart pre hfree
          hpreActive hpreP h1
      have hnextRun : run F start (pre ++ [.d]) = next := by
        simp [run, next]
      have hnextPlaced : next.placed = allRBoundaryPlaced (j + 1) := by
        rw [← hnextRun, hstage]
        exact (allRStage_execution hn hj hjn F start hstart).1
      have hpostUnique := ih (j + 1) (by omega) (by omega) next hnextOrder
        hnextPlaced post hpostlog hpostP (by simpa [hnextRun] using hpostActive) hpostEnd
      rw [hsplit, hstage, hpostUnique]
      rfl

theorem RealizesAllR.minimal_rotation_count {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (3 * n * (n - 1)) / 2 - 1) :
    word.count .p = pMin n := by
  obtain ⟨cert, hword⟩ := allRTraceExtraction_of_realizes hn h
  have hcert : cert.word.length = (3 * n * (n - 1)) / 2 - 1 := by
    simpa [hword] using hmin
  obtain ⟨_, hpre, hpost, _⟩ := cert.minimal_length_budget hn hcert
  have hcount : cert.word.count .p = cert.registrationPrefix.count .p +
      (cert.interWord ++ cert.tail).count .p := by simp [cert.word_eq]
  simpa [hword, hpre, hpost] using hcount

theorem allRPostLog_eq_remainingLog {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    allRPostLog n = allRRemainingLog n 1 (n - 2) := by
  rw [allRPostLog, allRPartners, ← allRCarrier_one hn]
  convert remainingLog_eq_rightFusionLog (n := n) 1 (n - 2) (by omega) using 1
  congr 1
  apply List.map_congr_left
  intro i hi
  congr 1
  omega

/-- Literal raw-word uniqueness for the specified complete ordered all-R log
and literal endpoint.  The caller supplies no segmentation, gap annotation,
stage budget, or intermediate placement. -/
theorem RealizesAllR.eq_canonical_of_minimum_length {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (3 * n * (n - 1)) / 2 - 1) :
    word = allRCanonicalWord n := by
  obtain ⟨post, hword⟩ := h.minimal_starts_with_defect hn hmin
  have hactive := h.minimal_activeDefectsRun hn hmin
  have hpostActive : ActiveDefectsRun (allRSelectedPair n) allRRegistered post := by
    rw [hword] at hactive
    exact hactive.2
  have hpostLog : completeFusionLog (allRSelectedPair n) allRRegistered post =
      allRPostLog n := by
    have hl := h.log_eq
    rw [hword] at hl
    exact congrArg List.tail hl
  have hpostP : post.count .p = (n - 2) * n + (n - 1) := by
    have hp := h.minimal_rotation_count hn hmin
    rw [hword] at hp
    have hpoly : pMin n = (n - 2) * n + (n - 1) := by
      unfold pMin
      have h₁ : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
      have h₂ : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
      have heq : n * (n - 1) = (n - 2) * n + n := by nlinarith
      omega
    simpa [hpoly] using hp
  have hrun : run (allRSelectedPair n) allRRegistered post =
      run (allRSelectedPair n) (singletonExecution n) word := by
    rw [hword]
    rfl
  have hend : ∃ B,
      (run (allRSelectedPair n) allRRegistered post).placed
        ((n - 1 : ℕ) : ZMod n) = some B ∧ (0 : ZMod n) ∈ B := by
    refine ⟨Finset.univ, ?_, by simp⟩
    rw [hrun, h.endpoint_eq]
    simp [allREndpoint]
  have hpostUnique := allRRemainingWord_unique hn 1 (n - 2) (by omega) (by omega)
    (allRSelectedPair n) allRRegistered (allRRegistered_gapRep hn).1
    (allRRegistered_boundary hn) post
    (by simpa [allRPostLog_eq_remainingLog hn] using hpostLog) hpostP hpostActive hend
  rw [hword, hpostUnique, remainingWord_eq_flatMap]
  simp [allRCanonicalWord, Nat.add_comm]

theorem RealizesAllR.minimal_word_unique {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (allRCanonicalWord n).length) :
    word = allRCanonicalWord n := by
  apply h.eq_canonical_of_minimum_length hn
  simpa [allRCanonicalWord_length hn] using hmin

/-- A paper-facing summary: the specified complete all-R log and literal
endpoint have exactly one raw word at the exact minimum length. -/
theorem allR_existsUnique_minimum_word {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    ∃! word : List Letter, RealizesAllR (n := n) word ∧
      word.length = (3 * n * (n - 1)) / 2 - 1 := by
  refine ⟨allRCanonicalWord n,
    ⟨allRCanonicalWord_realizes hn, allRCanonicalWord_length hn⟩, ?_⟩
  intro word hword
  exact hword.1.eq_canonical_of_minimum_length hn hword.2

end FusionLogAllR
