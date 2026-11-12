import Paper44.ObserverSemantics
import FutureEvent.Events
import RegisteredAbsorptionChains.SourceOrderInvariant

/-!
# Actual circular prefix observers

The state and raw transition are the frozen circular `Execution` and `step`.
The output is a lossless tagging of `FutureEvent.selectedOutput`; null is
retained once per raw letter. Registration is not an absorption.
The public machine restricts to genuine singleton-seed generated states.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n] {α : Type*} [DecidableEq α]

def retainedLabel (depth : ℕ) (origin : FusionRecord α)
    (chain : List (FusionRecord α)) : PrefixLabel (FusionRecord α) (FusionRecord α) :=
  .registered origin (chain.take depth)
    (if chain.length < depth then .short else .saturated)

omit [DecidableEq α] in
theorem retainedLabel_wellFormed (depth : ℕ) (origin : FusionRecord α)
    (chain : List (FusionRecord α)) :
    PrefixLabel.WellFormed depth (retainedLabel depth origin chain) := by
  by_cases h : chain.length < depth
  · simp [retainedLabel, h, PrefixLabel.WellFormed, List.length_take, Nat.min_eq_right (by omega : chain.length ≤ depth)]
  · simp [retainedLabel, h, PrefixLabel.WellFormed, List.length_take, Nat.min_eq_left (by omega : depth ≤ chain.length)]

omit [DecidableEq α] in
theorem retainedLabel_append (depth : ℕ) (origin record : FusionRecord α)
    (chain : List (FusionRecord α)) :
    retainedLabel depth origin (chain ++ [record]) =
      PrefixLabel.update depth (retainedLabel depth origin chain) (.absorption record) := by
  by_cases h : chain.length < depth
  · have ht : chain.take depth = chain := List.take_of_length_le (by omega)
    have ht' : (chain ++ [record]).take depth = chain ++ [record] :=
      List.take_of_length_le (by simp; omega)
    simp [retainedLabel, PrefixLabel.update, h, ht, ht']
  · have ht : (chain ++ [record]).take depth = chain.take depth :=
      List.take_append_of_le_length (by omega)
    have hlong : depth ≤ chain.length + 1 := by omega
    simp [retainedLabel, PrefixLabel.update, h, hlong, ht]

def circularLabel (depth : ℕ) (s : Execution n α) :
    PrefixLabel (FusionRecord α) (FusionRecord α) :=
  match s.origin with
  | none => .unregistered
  | some origin => retainedLabel depth origin s.chain

omit [NeZero n] [DecidableEq α] in
theorem circularLabel_wellFormed (depth : ℕ) (s : Execution n α) :
    PrefixLabel.WellFormed depth (circularLabel depth s) := by
  cases ho : s.origin with
  | none => simp [circularLabel, ho, PrefixLabel.WellFormed]
  | some origin =>
      simpa [circularLabel, ho] using retainedLabel_wellFormed depth origin s.chain

def selectedEventTag : Option (FutureEvent.SelectedEvent α) →
    PrefixEvent (FusionRecord α) (FusionRecord α)
  | none => .null
  | some (.registration record) => .registration record
  | some (.absorption record) => .absorption record

/-- Tagging preserves the complete record and distinguishes null from events. -/
def selectedEventOfTag : PrefixEvent (FusionRecord α) (FusionRecord α) →
    Option (FutureEvent.SelectedEvent α)
  | .null => none
  | .registration record => some (.registration record)
  | .absorption record => some (.absorption record)

omit [DecidableEq α] in
theorem selectedEventTag_injective :
    Function.Injective (selectedEventTag (α := α)) := by
  apply Function.LeftInverse.injective (g := selectedEventOfTag)
  intro event
  cases event with
  | none => rfl
  | some event => cases event <;> rfl

def circularEmit (F : Finset α) (s : Execution n α) (a : Letter) :
    PrefixEvent (FusionRecord α) (FusionRecord α) :=
  selectedEventTag (FutureEvent.selectedOutput F s a)

/-- This invariant excludes fabricated old chains before registration. -/
def RegistrationConsistent (s : Execution n α) : Prop :=
  s.origin = none → s.chain = []

omit [NeZero n] in
theorem registrationConsistent_step (F : Finset α) (s : Execution n α)
    (hs : RegistrationConsistent s) (a : Letter) :
    RegistrationConsistent (step F s a) := by
  cases a with
  | p => exact hs
  | d =>
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
        cases ho : s.origin <;>
        simp_all [RegistrationConsistent, step, stepDefect]

omit [NeZero n] in
theorem circularLabel_step (F : Finset α) (depth : ℕ) (hj : 0 < depth)
    (s : Execution n α) (hs : RegistrationConsistent s) (a : Letter) :
    circularLabel depth (step F s a) =
      PrefixLabel.update depth (circularLabel depth s) (circularEmit F s a) := by
  cases a with
  | p => cases ho : s.origin <;> simp [circularLabel, circularEmit,
      FutureEvent.selectedOutput, selectedEventTag, step, ho, retainedLabel, PrefixLabel.update]
  | d =>
      cases h0 : s.placed 0 with
      | none => cases ho : s.origin <;> simp [step, stepDefect, h0, ho,
          circularLabel, circularEmit, FutureEvent.selectedOutput, selectedEventTag,
          retainedLabel, PrefixLabel.update]
      | some U =>
          cases h1 : s.placed 1 with
          | none => cases ho : s.origin <;> simp [step, stepDefect, h0, h1, ho,
              circularLabel, circularEmit, FutureEvent.selectedOutput, selectedEventTag,
              retainedLabel, PrefixLabel.update]
          | some V =>
              cases ho : s.origin with
              | none =>
                  have hc := hs ho
                  by_cases he : U ∪ V = F <;>
                    simp [step, stepDefect, h0, h1, ho, he, hc, circularLabel,
                      circularEmit, FutureEvent.selectedOutput, selectedEventTag,
                      retainedLabel, PrefixLabel.update, hj]
              | some origin =>
                  by_cases he : F ⊆ U ∨ F ⊆ V
                  · have hb : (decide (F ⊆ U) || decide (F ⊆ V)) = true := by simp [he]
                    simpa [step, stepDefect, h0, h1, ho, hb, circularLabel,
                      circularEmit, FutureEvent.selectedOutput, selectedEventTag]
                      using retainedLabel_append depth origin ⟨U, V, U ∪ V⟩ s.chain
                  · have hb : (decide (F ⊆ U) || decide (F ⊆ V)) = false := by
                      simp only [Bool.or_eq_false_iff, decide_eq_false_iff_not]
                      exact not_or.mp he
                    simp [step, stepDefect, h0, h1, ho, hb, circularLabel,
                      circularEmit, FutureEvent.selectedOutput, selectedEventTag,
                      retainedLabel, PrefixLabel.update]

def CircularGenerated (s : Execution n (ZMod n)) : Prop :=
  ∃ word, run {0, 1} (singletonExecution n) word = s

abbrev CircularState (n : ℕ) [NeZero n] :=
  {s : Execution n (ZMod n) // CircularGenerated s}

theorem circularGenerated_step (s : Execution n (ZMod n))
    (hs : CircularGenerated s) (a : Letter) : CircularGenerated (step {0, 1} s a) := by
  obtain ⟨w, rfl⟩ := hs
  exact ⟨w ++ [a], by simp [run]⟩

theorem circularGenerated_consistent (s : Execution n (ZMod n))
    (hs : CircularGenerated s) : RegistrationConsistent s := by
  obtain ⟨w, rfl⟩ := hs
  have hrun : ∀ (t : Execution n (ZMod n)), RegistrationConsistent t →
      RegistrationConsistent (run {0, 1} t w) := by
    induction w with
    | nil => intro t ht; exact ht
    | cons a w ih =>
        intro t ht
        exact ih (step {0, 1} t a) (registrationConsistent_step _ t ht a)
  exact hrun _ (by simp [RegistrationConsistent, singletonExecution])

def circularStep (s : CircularState n) (a : Letter) : CircularState n :=
  ⟨step {0, 1} s.val a, circularGenerated_step s.val s.property a⟩

/-- The concrete all-parameter instance; no abstract `label_step` premise. -/
def circularPrefixMachine (_hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth) :
    PrefixObserver (CircularState n) Letter (FusionRecord (ZMod n)) (FusionRecord (ZMod n)) where
  step := circularStep
  emit s a := circularEmit {0, 1} s.val a
  label s := circularLabel depth s.val
  update := PrefixLabel.update depth
  label_step s a := circularLabel_step _ depth hj s.val
    (circularGenerated_consistent s.val s.property) a

theorem circular_trace_eq (hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth)
    (s : CircularState n) (w : List Letter) :
    (circularPrefixMachine hn depth hj).trace s w =
      (FutureEvent.eventTrace {0, 1} s.val w).map selectedEventTag := by
  induction w generalizing s with
  | nil => rfl
  | cons a w ih =>
      change circularEmit {0, 1} s.val a ::
        (circularPrefixMachine hn depth hj).trace (circularStep s a) w = _
      rw [ih]
      rfl

theorem circular_trace_length (hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth)
    (s : CircularState n) (w : List Letter) :
    ((circularPrefixMachine hn depth hj).trace s w).length = w.length := by
  induction w generalizing s with
  | nil => rfl
  | cons a w ih =>
      change (((circularPrefixMachine hn depth hj).trace (circularStep s a) w).length + 1) = w.length + 1
      rw [ih]

/-- Abstract and literal raw execution have the same complete state. -/
theorem circular_run_eq (hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth)
    (s : CircularState n) (w : List Letter) :
    ((circularPrefixMachine hn depth hj).run s w).val =
      run {0, 1} s.val w := by
  induction w generalizing s with
  | nil => rfl
  | cons a w ih =>
      change ((circularPrefixMachine hn depth hj).run (circularStep s a) w).val =
        run {0, 1} (step {0, 1} s.val a) w
      exact ih (circularStep s a)

/-- The retained label is updated from every output, including null slots. -/
theorem circular_label_run (hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth)
    (s : CircularState n) (w : List Letter) :
    circularLabel depth (run {0, 1} s.val w) =
      PrefixLabel.scanFrom depth (circularLabel depth s.val)
        ((FutureEvent.eventTrace {0, 1} s.val w).map selectedEventTag) := by
  have h := LabelledMachine.label_run (circularPrefixMachine hn depth hj) s w
  change circularLabel depth
    (((circularPrefixMachine hn depth hj).run s w).val) = _ at h
  rw [circular_run_eq, circular_trace_eq] at h
  exact h

/-- Manuscript (2.4), now on the actual generated circular state space. -/
theorem circular_observerEq_iff (hn : 3 ≤ n) (depth : ℕ) (hj : 0 < depth)
    (x y : CircularState n) :
    (circularPrefixMachine hn depth hj).ObserverEq x y ↔
      FutureEvent.FutureEquivalent {0, 1} x.val y.val ∧
        circularLabel depth x.val = circularLabel depth y.val := by
  constructor
  · rintro ⟨hfuture, hlabel⟩
    refine ⟨?_, hlabel⟩
    intro w
    have h := hfuture w
    rw [circular_trace_eq, circular_trace_eq] at h
    exact List.map_injective_iff.mpr selectedEventTag_injective h
  · rintro ⟨hfuture, hlabel⟩
    refine ⟨?_, hlabel⟩
    intro w
    rw [circular_trace_eq, circular_trace_eq, hfuture w]

end Paper44
