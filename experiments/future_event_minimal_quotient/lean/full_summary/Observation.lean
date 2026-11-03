import FutureEvent.QuotientCardinality

namespace FullSummary

open RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} {α : Type*} [DecidableEq α]

/-- F and the raw environment are fixed parameters; an execution contains
exactly the remaining full-summary fields (placement, origin, chain). -/
def output (s : Execution n α) : Option (Execution n α) :=
  if s.origin.isSome then some s else none

omit [DecidableEq α] in
theorem output_eq_none (s : Execution n α) : output s = none ↔ s.origin = none := by
  cases ho : s.origin <;> simp [output, ho]

omit [DecidableEq α] in
theorem output_eq_some (s t : Execution n α) :
    output s = some t ↔ s = t ∧ s.origin.isSome = true := by
  cases ho : s.origin <;> simp [output, ho]

omit [DecidableEq α] in
theorem output_equal_cases (s t : Execution n α) (h : output s = output t) :
    (s.origin = none ∧ t.origin = none) ∨ s = t := by
  cases ho : s.origin with
  | none =>
      exact Or.inl ⟨rfl, (output_eq_none t).mp (h.symm.trans ((output_eq_none s).mpr ho))⟩
  | some r =>
      have hs : output s = some s := (output_eq_some s s).mpr ⟨rfl, by simp [ho]⟩
      exact Or.inr (((output_eq_some t s).mp (h.symm.trans hs)).1.symm)

omit [DecidableEq α] in
theorem output_origin (s : Execution n α) :
    (output s).bind Execution.origin = s.origin := by
  cases ho : s.origin <;> simp [output, ho]

theorem unregistered_event_from_origin (F : Finset α) (s : Execution n α) (a : Letter)
    (ho : s.origin = none) :
    selectedOutput F s a = (step F s a).origin.map SelectedEvent.registration := by
  cases a with
  | p => simp [selectedOutput, step, ho]
  | d =>
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
        simp [selectedOutput, step, stepDefect, ho, h0, h1]

/-- Adjacent Moore readings recover the event of this same actual step. -/
theorem event_eq_of_adjacent_outputs (F : Finset α) (s t : Execution n α) (a : Letter)
    (hnow : output s = output t) (hnext : output (step F s a) = output (step F t a)) :
    selectedOutput F s a = selectedOutput F t a := by
  rcases output_equal_cases s t hnow with ⟨hs, ht⟩ | rfl
  · have ho := congrArg (fun o : Option (Execution n α) => o.bind Execution.origin) hnext
    rw [output_origin, output_origin] at ho
    rw [unregistered_event_from_origin F s a hs, unregistered_event_from_origin F t a ht, ho]
  · rfl

/-- Equality on every literal prefix of one word implies trace equality. -/
theorem events_eq_of_prefix_outputs (F : Finset α) (s t : Execution n α) (word : List Letter)
    (h : ∀ pre suffix, pre ++ suffix = word →
      output (run F s pre) = output (run F t pre)) :
    eventTrace F s word = eventTrace F t word := by
  induction word generalizing s t with
  | nil => rfl
  | cons a rest ih =>
      have hnow : output s = output t := h [] (a :: rest) rfl
      have hnext : output (step F s a) = output (step F t a) := h [a] rest rfl
      have hhead := event_eq_of_adjacent_outputs F s t a hnow hnext
      have htail : eventTrace F (step F s a) rest = eventTrace F (step F t a) rest := by
        apply ih
        intro pre suffix he
        have hh := h (a :: pre) suffix (by simp only [List.cons_append, he])
        exact hh
      simp only [eventTrace, hhead, htail]

/-- A source-addressed prefix certificate for the same given word; no
replacement representative or independent event witness is chosen. -/
theorem event_to_summary_prefix_detection (F : Finset α) (s t : Execution n α)
    (word : List Letter) (hne : eventTrace F s word ≠ eventTrace F t word) :
    ∃ pre suffix, pre ++ suffix = word ∧
      output (run F s pre) ≠ output (run F t pre) := by
  classical
  by_contra hnot
  push Not at hnot
  exact hne (events_eq_of_prefix_outputs F s t word hnot)

/-- The Moore contract compares every common continuation, including []. -/
def Equivalent (F : Finset α) (s t : Execution n α) : Prop :=
  ∀ word, output (run F s word) = output (run F t word)

theorem equivalent_refl (F : Finset α) (s : Execution n α) : Equivalent F s s := fun _ => rfl

theorem equivalent_right_congruent (F : Finset α) (s t : Execution n α)
    (h : Equivalent F s t) (lead : List Letter) :
    Equivalent F (run F s lead) (run F t lead) := by
  intro suffix
  simpa only [← run_append] using h (lead ++ suffix)

theorem equivalent_implies_future (F : Finset α) (s t : Execution n α)
    (h : Equivalent F s t) : FutureEquivalent F s t := by
  intro word
  exact events_eq_of_prefix_outputs F s t word (fun pre _ _ => h pre)

end FullSummary
