import FusionLogAllR.RawAllRCertificate

namespace FusionLogAllR

open FusionLogCompression RegisteredAbsorptionChains
open scoped BigOperators

/-! # Exact raw-word surplus identity

This module exports manuscript (6.9), including its rank-one term.  The
backslide profile is read from the actual execution: its level starts at
`n - 1` and decreases by one at every effective fusion.  On the extracted
post-registration physical trace it equals the number of noncarrier packets,
namely the length of the carrier-anchored gap vector minus one.
-/

/-- The level of every backslide in one gap rewrite.  A rank-one return is
retained at level zero rather than discarded with its zero potential weight. -/
def HoleTransition.backslideLevels {g h : List ℤ} : HoleTransition g h → List ℕ
  | .backslide _ middle _ => [middle.length + 1]
  | .rankOneBackslide _ => [0]
  | _ => []

def ExecutionTrace.backslideLevels {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → List ℕ
  | .nil _ => []
  | .p rest => rest.backslideLevels
  | .d transition rest => transition.backslideLevels ++ rest.backslideLevels

theorem HoleTransition.backslideLevels_length {g h : List ℤ}
    (transition : HoleTransition g h) :
    transition.backslideLevels.length = transition.ledger.backslides := by
  cases transition <;> rfl

theorem HoleTransition.backslideLevels_sum {g h : List ℤ}
    (transition : HoleTransition g h) :
    transition.backslideLevels.sum = transition.ledger.weightedBack := by
  cases transition <;> simp [HoleTransition.backslideLevels, HoleTransition.ledger]

theorem HoleTransition.length_le {g h : List ℤ}
    (transition : HoleTransition g h) : h.length ≤ g.length := by
  cases transition <;>
    simp [slideSource, slideTarget, carrierBackslideSource,
      carrierBackslideTarget, fusionSource, fusionTarget]

theorem HoleTransition.external_count_update {g h : List ℤ}
    (transition : HoleTransition g h) :
    h.length - 1 = g.length - 1 - transition.fusionStep := by
  cases transition <;>
    simp [HoleTransition.fusionStep, slideSource, slideTarget,
      carrierBackslideSource, carrierBackslideTarget, fusionSource, fusionTarget]

theorem HoleTransition.backslideLevels_eq {g h : List ℤ}
    (transition : HoleTransition g h) :
    transition.backslideLevels =
      if transition.ledger.backslides = 1 then [g.length - 1] else [] := by
  cases transition <;>
    simp [HoleTransition.backslideLevels, HoleTransition.ledger,
      carrierBackslideSource]

theorem ExecutionTrace.backslideLevels_length {word : List Letter}
    {g h : List ℤ} (trace : ExecutionTrace word g h) :
    trace.backslideLevels.length = trace.holeTrace.ledger.backslides := by
  induction trace with
  | nil g => rfl
  | p rest ih => exact ih
  | d transition rest ih =>
      simp [ExecutionTrace.backslideLevels, ExecutionTrace.holeTrace,
        HoleTrace.ledger, HoleLedger.add, transition.backslideLevels_length, ih]

theorem ExecutionTrace.backslideLevels_sum {word : List Letter}
    {g h : List ℤ} (trace : ExecutionTrace word g h) :
    trace.backslideLevels.sum = trace.holeTrace.ledger.weightedBack := by
  induction trace with
  | nil g => rfl
  | p rest ih => exact ih
  | d transition rest ih =>
      simp [ExecutionTrace.backslideLevels, ExecutionTrace.holeTrace,
        HoleTrace.ledger, HoleLedger.add, transition.backslideLevels_sum, ih]

theorem ExecutionTrace.backslideLevels_lt {word : List Letter}
    {g h : List ℤ} (trace : ExecutionTrace word g h)
    {m : ℕ} (hm : m ∈ trace.backslideLevels) : m < g.length := by
  induction trace with
  | nil g => simp [ExecutionTrace.backslideLevels] at hm
  | p rest ih => exact ih hm
  | d transition rest ih =>
      rcases List.mem_append.mp hm with hm | hm
      · cases transition <;>
          simp_all [HoleTransition.backslideLevels, carrierBackslideSource]
      · exact lt_of_lt_of_le (ih hm) transition.length_le

private theorem sum_count_profile (levels : List ℕ) (bound : ℕ)
    (hbound : ∀ m ∈ levels, m < bound) (weight : ℕ → ℕ) :
    (∑ m ∈ Finset.range bound, weight m * levels.count m) =
      (levels.map weight).sum := by
  induction levels with
  | nil => simp
  | cons a rest ih =>
      have ha : a < bound := hbound a (by simp)
      have hr : ∀ m ∈ rest, m < bound := fun m hm => hbound m (by simp [hm])
      simp only [List.count_cons, Nat.mul_add, Finset.sum_add_distrib,
        List.map_cons, List.sum_cons]
      rw [ih hr]
      simp [ha, Nat.add_comm]

private theorem sum_map_add_two (levels : List ℕ) :
    (levels.map (fun m => m + 2)).sum = levels.sum + 2 * levels.length := by
  induction levels with
  | nil => rfl
  | cons a rest ih => simp only [List.map_cons, List.sum_cons, List.length_cons]; omega

/-- Actual chronological backslide levels.  The level counter counts packets
other than the carrier, not rotations or potential weight. -/
def executionBackslideLevels {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (a : ZMod n)
    (external : ℕ) : List Letter → List ℕ
  | [] => []
  | .p :: rest => executionBackslideLevels F (step F s .p) a external rest
  | .d :: rest =>
      (if a ∈ (s.placed 1).getD ∅ then [external] else []) ++
        executionBackslideLevels F (step F s .d) a
          (external - if s.placed 0 ≠ none ∧ s.placed 1 ≠ none then 1 else 0) rest

/-- Unchanged actual defect letters, including any such letters at rank one. -/
def executionIdleDefects {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) : List Letter → ℕ
  | [] => 0
  | .p :: rest => executionIdleDefects F (step F s .p) rest
  | .d :: rest => (if s.placed 1 = none then 1 else 0) +
      executionIdleDefects F (step F s .d) rest

theorem PhysicalTrace.backslideLevels_eq_execution {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter} {g h : List ℤ}
    (trace : PhysicalTrace F a s word t g h) :
    trace.toExecutionTrace.backslideLevels =
      executionBackslideLevels F s a (g.length - 1) word := by
  induction trace with
  | nil hrep => rfl
  | p hrep rest ih => exact ih
  | d hrep transition hnext hmatch rest ih =>
      simp only [PhysicalTrace.toExecutionTrace, ExecutionTrace.backslideLevels,
        executionBackslideLevels]
      rw [transition.backslideLevels_eq, hmatch.backslides, ih,
        transition.external_count_update, hmatch.fusion]
      split_ifs <;> simp_all

theorem PhysicalTrace.idleSteps_eq_execution {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter} {g h : List ℤ}
    (trace : PhysicalTrace F a s word t g h) :
    trace.toExecutionTrace.idleSteps = executionIdleDefects F s word := by
  induction trace with
  | nil hrep => rfl
  | p hrep rest ih => exact ih
  | d hrep transition hnext hmatch rest ih =>
      change transition.idleStep + rest.toExecutionTrace.idleSteps = _
      rw [hmatch.idle, ih]
      rfl

theorem executionBackslideLevels_length_eq_returns {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (a : ZMod n) (external : ℕ) (word : List Letter) :
    (executionBackslideLevels F s a external word).length =
      executionCarrierReturns F s a word := by
  induction word generalizing s external with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => exact ih _ external
      | d =>
          simp only [executionBackslideLevels, List.length_append,
            executionCarrierReturns, ih]
          split_ifs <;> rfl

/-- The manuscript's `B_m`, computed from the raw word and actual states. -/
def allRBackslidesAt (n : ℕ) [NeZero n] (word : List Letter) (m : ℕ) : ℕ :=
  (executionBackslideLevels (allRSelectedPair n) (singletonExecution n)
    0 (n - 1) word).count m

/-- The manuscript's `Z`, computed from the raw word and actual states. -/
def allRIdleDefects (n : ℕ) [NeZero n] (word : List Letter) : ℕ :=
  executionIdleDefects (allRSelectedPair n) (singletonExecution n) word

/-- The nonnegative rotation excess `R = N_p - P_min - B`. -/
def allRRotationExcess (n : ℕ) [NeZero n] (word : List Letter) : ℕ :=
  word.count .p - pMin n -
    executionCarrierReturns (allRSelectedPair n) (singletonExecution n) 0 word

private theorem backslideLevels_after_rotations {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) (a : ZMod n)
    (external : ℕ) (pre post : List Letter) (hd : pre.count .d = 0) :
    executionBackslideLevels F s a external (pre ++ post) =
      executionBackslideLevels F (run F s pre) a external post := by
  induction pre generalizing s with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => exact ih (step F s .p) (by simpa using hd)
      | d => simp at hd

private theorem idleDefects_after_rotations {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (pre post : List Letter) (hd : pre.count .d = 0) :
    executionIdleDefects F s (pre ++ post) =
      executionIdleDefects F (run F s pre) post := by
  induction pre generalizing s with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => exact ih (step F s .p) (by simpa using hd)
      | d => simp at hd

private theorem post_rotation_lower_bound_with_returns {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (post : List Letter)
    (hlog : completeFusionLog (allRSelectedPair n) allRRegistered post = allRPostLog n)
    (hend : (run (allRSelectedPair n) allRRegistered post).placed = allREndpoint) :
    pMin n + executionCarrierReturns (allRSelectedPair n) allRRegistered 0 post ≤
      post.count .p := by
  have hmarked : (0 : ZMod n) ∈ ((allRRegistered (n := n)).placed 0).getD ∅ := by
    simp [allRRegistered_zero, allRSelectedPair]
  obtain ⟨inter, tail, afterInter, hpost, intervals, hafter, _⟩ :=
    rightFusionIntervals_of_completeFusionLog (allRSelectedPair n) 0 (by omega)
      (allRPostLog n) allRRegistered post hmarked
      (defect_port_one_empty _ _ (by omega)) hlog
      (rightFusionLog_left_mem (allRSelectedPair n) (allRPartners n) 0
        (by simp [allRSelectedPair]))
  rw [allRPostLog_length] at intervals
  obtain ⟨C, hC, haC⟩ : ∃ C, afterInter.placed 0 = some C ∧ (0 : ZMod n) ∈ C := by
    cases h0 : afterInter.placed 0 with
    | none => simp [h0] at hafter
    | some C => exact ⟨C, rfl, by simpa [h0] using hafter⟩
  have htail : (run (allRSelectedPair n) afterInter tail).placed = allREndpoint := by
    rw [hpost, run_append, intervals.run_eq] at hend
    exact hend
  have hD : (run (allRSelectedPair n) afterInter tail).placed
      ((n - 1 : ℕ) : ZMod n) = some Finset.univ := by
    simp [htail, allREndpoint]
  simpa [hpost] using actual_allR_rotation_lower_bound intervals hn
    (allRRegistered_gapRep hn).1 tail C Finset.univ hC haC hD (by simp)

/-- The exact operational ledgers underlying (6.9).  In particular the
rotation inequality is proved before natural-number subtraction defines `R`.
The profile's levels are bounded by `n - 2` by the physical gap simulation. -/
theorem RealizesAllR.surplus_ledgers {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    let levels := executionBackslideLevels (allRSelectedPair n)
      (singletonExecution n) 0 (n - 1) word
    pMin n + levels.length ≤ word.count .p ∧
      word.count .d = (n - 1) + allRSlides n + levels.sum + levels.length +
        allRIdleDefects n word ∧
      (∀ m ∈ levels, m < n - 1) := by
  obtain ⟨pre, post, hword, hpre, _, _, hseed, hlog⟩ := h.registration_prefix
  have hpreD : pre.count .d = 0 := by rw [hpre, pWord_count_d]
  have hregistered : run (allRSelectedPair n) (singletonExecution n) (pre ++ [.d]) =
      allRRegistered := by rw [run_append, hseed]; rfl
  rw [hregistered] at hlog
  have hrun : run (allRSelectedPair n) allRRegistered post =
      run (allRSelectedPair n) (singletonExecution n) word := by
    rw [hword, run_append, run_append, hseed]
    rfl
  have hend : (run (allRSelectedPair n) allRRegistered post).placed = allREndpoint := by
    rw [hrun, h.endpoint_eq]
  have hright := rightCarrierRun_of_completeFusionLog_left (allRSelectedPair n)
    0 allRRegistered post (by
      rw [hlog]
      exact rightFusionLog_left_mem (allRSelectedPair n) (allRPartners n) 0
        (by simp [allRSelectedPair]))
  obtain ⟨gap, ⟨physical⟩⟩ := physicalTrace_exists (allRSelectedPair n)
    (by omega) (allRRegistered_gapRep hn) post hright
  have hterminal := allREndpoint_gapRep _ physical.end_rep.1 hend
  have hgap : gap = [((n - 1 : ℕ) : ℤ)] :=
    gapRep_unique physical.end_rep hterminal
  rw [hgap] at physical
  have hlevels : executionBackslideLevels (allRSelectedPair n)
      (singletonExecution n) 0 (n - 1) word =
        physical.toExecutionTrace.backslideLevels := by
    rw [hword, List.append_assoc,
      backslideLevels_after_rotations _ _ _ _ pre _ hpreD, hseed]
    have h01 : (0 : ZMod n) ≠ 1 := by
      intro heq
      have := ZMod.one_eq_zero_iff.mp heq.symm
      omega
    simpa [executionBackslideLevels, singletonExecution, allRRegistered,
      h01, initialGaps, Nat.sub_sub] using physical.backslideLevels_eq_execution.symm
  have hidle : allRIdleDefects n word =
      physical.toExecutionTrace.idleSteps := by
    unfold allRIdleDefects
    rw [hword, List.append_assoc,
      idleDefects_after_rotations _ _ pre _ hpreD, hseed]
    simpa [executionIdleDefects, singletonExecution, allRRegistered] using
      physical.idleSteps_eq_execution.symm
  have hfusion : physical.toExecutionTrace.fusionSteps = n - 2 := by
    rw [physical.fusionSteps_eq_completeFusionLog_length, hlog, allRPostLog_length]
  have hslides := HoleTrace.allR_slide_identity hn (n - 1 : ℕ)
    physical.toExecutionTrace.holeTrace
  have hdefects := physical.toExecutionTrace.defect_accounting
  have hdcount := physical.toExecutionTrace.dLetters_eq_count
  have hlength := physical.toExecutionTrace.backslideLevels_length
  have hsum := physical.toExecutionTrace.backslideLevels_sum
  have hrot := post_rotation_lower_bound_with_returns hn post hlog hend
  have hreturns := physical.backslides_eq_returns
  have hpword : word.count .p = pre.count .p + post.count .p := by simp [hword]
  have hdword : word.count .d = post.count .d + 1 := by simp [hword, hpreD]
  dsimp only
  rw [hlevels]
  refine ⟨?_, ?_, ?_⟩
  · omega
  · omega
  · intro m hm
    have hm' := physical.toExecutionTrace.backslideLevels_lt hm
    simp only [initialGaps, List.length_cons, List.length_replicate] at hm'
    omega

/-- Summing the bounded `B_m` profile gives exactly the physical carrier
return count, including all rank-one returns. -/
theorem RealizesAllR.backslide_profile_total {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    (∑ m ∈ Finset.range (n - 1), allRBackslidesAt n word m) =
      executionCarrierReturns (allRSelectedPair n) (singletonExecution n) 0 word := by
  obtain ⟨_, _, hbound⟩ := h.surplus_ledgers hn
  have hsum := sum_count_profile _ (n - 1) hbound (fun _ => 1)
  simp only [allRBackslidesAt, one_mul, List.map_const', List.sum_replicate,
    smul_eq_mul, mul_one] at hsum ⊢
  rw [hsum, executionBackslideLevels_length_eq_returns]

/-- The definition of `R` is genuine nonnegative slack: no truncated
natural subtraction is hidden in the excess-cost identity. -/
theorem RealizesAllR.rotation_excess_accounting {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    word.count .p = pMin n +
      (∑ m ∈ Finset.range (n - 1), allRBackslidesAt n word m) +
        allRRotationExcess n word := by
  obtain ⟨hp, _, _⟩ := h.surplus_ledgers hn
  rw [h.backslide_profile_total hn]
  unfold allRRotationExcess
  rw [executionBackslideLevels_length_eq_returns] at hp
  omega

/-- Manuscript (6.9), as an equality for every actual raw realization.
`B_m`, `Z`, and `R` are the operational functions above, not caller-supplied
charges.  The explicit `2 * B_0` preserves the zero-potential rank-one cost. -/
theorem RealizesAllR.word_length_surplus_identity {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    word.length - ((3 * n * (n - 1)) / 2 - 1) =
      allRRotationExcess n word + 2 * allRBackslidesAt n word 0 +
        (∑ m ∈ Finset.Icc 1 (n - 2), (m + 2) * allRBackslidesAt n word m) +
          allRIdleDefects n word := by
  obtain ⟨hp, hd, hbound⟩ := h.surplus_ledgers hn
  let levels := executionBackslideLevels (allRSelectedPair n)
    (singletonExecution n) 0 (n - 1) word
  have hprofile :
      (∑ m ∈ Finset.range (n - 1), (m + 2) * allRBackslidesAt n word m) =
        levels.sum + 2 * levels.length := by
    change (∑ m ∈ Finset.range (n - 1), (m + 2) * levels.count m) = _
    rw [sum_count_profile levels (n - 1) hbound, sum_map_add_two]
  have hrange : Finset.range (n - 1) = insert 0 (Finset.Icc 1 (n - 2)) := by
    ext m
    simp only [Finset.mem_range, Finset.mem_insert, Finset.mem_Icc]
    omega
  have hsplit :
      2 * allRBackslidesAt n word 0 +
          (∑ m ∈ Finset.Icc 1 (n - 2), (m + 2) * allRBackslidesAt n word m) =
        levels.sum + 2 * levels.length := by
    rw [hrange, Finset.sum_insert (by simp)] at hprofile
    simpa using hprofile
  have hreturns : levels.length =
      executionCarrierReturns (allRSelectedPair n) (singletonExecution n) 0 word :=
    executionBackslideLevels_length_eq_returns _ _ _ _ _
  have hcounts := count_p_add_count_d word
  have hbase := allRMinimumLength_eq n hn
  have hp_exact : word.count .p =
      pMin n + levels.length + allRRotationExcess n word := by
    have hrot := h.rotation_excess_accounting hn
    rw [h.backslide_profile_total hn, ← hreturns] at hrot
    exact hrot
  dsimp only [levels] at hp_exact hsplit
  have hcost : word.length = (pMin n + (n - 1) + allRSlides n) +
      allRRotationExcess n word + 2 * allRBackslidesAt n word 0 +
        (∑ m ∈ Finset.Icc 1 (n - 2), (m + 2) * allRBackslidesAt n word m) +
          allRIdleDefects n word := by
    omega
  rw [hbase] at hcost
  omega

end FusionLogAllR
