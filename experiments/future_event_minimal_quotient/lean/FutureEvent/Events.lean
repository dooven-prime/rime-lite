import RegisteredAbsorptionChains.Execution

namespace FutureEvent

open RegisteredAbsorptionChains

inductive SelectedEvent (α : Type*) where
  | registration (record : FusionRecord α)
  | absorption (record : FusionRecord α)

variable {n : ℕ} {α : Type*} [DecidableEq α]

/-- The new event emitted by this actual letter, not the stored old chain. -/
def selectedOutput (F : Finset α) (s : Execution n α) :
    Letter → Option (SelectedEvent α)
  | .p => none
  | .d =>
      match s.placed 0, s.placed 1 with
      | some u, some v =>
          let record : FusionRecord α := ⟨u, v, u ∪ v⟩
          if s.origin.isSome then
            if F ⊆ u || F ⊆ v then some (.absorption record) else none
          else if u ∪ v = F then some (.registration record) else none
      | _, _ => none

def eventTrace (F : Finset α) (s : Execution n α) :
    List Letter → List (Option (SelectedEvent α))
  | [] => []
  | a :: rest => selectedOutput F s a :: eventTrace F (step F s a) rest

theorem eventTrace_append (F : Finset α) (s : Execution n α)
    (u v : List Letter) :
    eventTrace F s (u ++ v) =
      eventTrace F s u ++ eventTrace F (run F s u) v := by
  induction u generalizing s with
  | nil => rfl
  | cons a rest ih =>
      change selectedOutput F s a :: eventTrace F (step F s a) (rest ++ v) = _
      rw [ih]
      rfl

theorem fusionFree_records_and_trace (F : Finset α) (s : Execution n α)
    (word : List Letter) (hfree : FusionFree F s word) :
    (run F s word).origin = s.origin ∧
    (run F s word).chain = s.chain ∧
    eventTrace F s word = List.replicate word.length none := by
  induction word generalizing s with
  | nil => exact ⟨rfl, rfl, rfl⟩
  | cons a rest ih =>
      have hstep : (step F s a).origin = s.origin ∧
          (step F s a).chain = s.chain ∧ selectedOutput F s a = none := by
        cases a with
        | p => exact ⟨rfl, rfl, rfl⟩
        | d =>
            rcases hfree.1 with h | h
            · simp [step, stepDefect, selectedOutput, h]
            · simp [step, stepDefect, selectedOutput, h]
      have htail : FusionFree F (step F s a) rest := by
        cases a with
        | p => exact hfree
        | d => exact hfree.2
      obtain ⟨ho, hc, ht⟩ := ih (step F s a) htail
      exact ⟨ho.trans hstep.1, hc.trans hstep.2.1,
        by simp [eventTrace, hstep.2.2, ht, List.replicate_succ]⟩

def FutureEquivalent (F : Finset α) (s t : Execution n α) : Prop :=
  ∀ word, eventTrace F s word = eventTrace F t word

theorem futureEquivalent_refl (F : Finset α) (s : Execution n α) :
    FutureEquivalent F s s := fun _ => rfl

theorem futureEquivalent_right_congruent (F : Finset α) (s t : Execution n α)
    (h : FutureEquivalent F s t) (lead : List Letter) :
    FutureEquivalent F (run F s lead) (run F t lead) := by
  intro suffix
  have heq := h (lead ++ suffix)
  rw [eventTrace_append, eventTrace_append, h lead] at heq
  exact List.append_cancel_left heq

theorem step_placed_eq (F : Finset α) (s t : Execution n α) (a : Letter)
    (h : s.placed = t.placed) : (step F s a).placed = (step F t a).placed := by
  cases a with
  | p => exact congrArg (rotate 1) h
  | d =>
      unfold step stepDefect
      rw [h]
      cases t.placed 0 <;> cases t.placed 1 <;> rfl

theorem step_registered (F : Finset α) (s : Execution n α) (a : Letter)
    (h : s.origin.isSome = true) : (step F s a).origin.isSome = true := by
  cases a with
  | p => exact h
  | d =>
      unfold step stepDefect
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
        cases hor : s.origin <;> simp_all

theorem selectedOutput_registered_eq (F : Finset α) (s t : Execution n α)
    (a : Letter) (hs : s.origin.isSome = true) (ht : t.origin.isSome = true)
    (h : s.placed = t.placed) : selectedOutput F s a = selectedOutput F t a := by
  cases a with
  | p => rfl
  | d => simp [selectedOutput, h, hs, ht]

/-- Registered old origins and chains can be forgotten for this observer. -/
theorem registered_same_placement_futureEquivalent
    (F : Finset α) (s t : Execution n α)
    (hs : s.origin.isSome = true) (ht : t.origin.isSome = true)
    (h : s.placed = t.placed) : FutureEquivalent F s t := by
  intro word
  induction word generalizing s t with
  | nil => rfl
  | cons a rest ih =>
      change selectedOutput F s a :: eventTrace F (step F s a) rest =
        selectedOutput F t a :: eventTrace F (step F t a) rest
      rw [selectedOutput_registered_eq F s t a hs ht h,
        ih (step F s a) (step F t a) (step_registered F s a hs)
          (step_registered F t a ht) (step_placed_eq F s t a h)]

end FutureEvent
