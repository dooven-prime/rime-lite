import FusionLogCompression

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- A complete effective event read from one actual predecessor. -/
def effectiveEvent (s : Execution n α) : Letter → Option (FusionRecord α)
  | .p => none
  | .d =>
      match s.placed 0, s.placed 1 with
      | some A, some B => some ⟨A, B, A ∪ B⟩
      | _, _ => none

/-- The added event list, independently of any previously stored log. -/
def eventTrace (F : Finset α) (s : Execution n α) : List Letter → List (FusionRecord α)
  | [] => []
  | a :: rest => (effectiveEvent s a).toList ++ eventTrace F (step F s a) rest

theorem fusionFree_cons_iff (F : Finset α) (s : Execution n α)
    (a : Letter) (rest : List Letter) :
    FusionFree F s (a :: rest) ↔
      effectiveEvent s a = none ∧ FusionFree F (step F s a) rest := by
  cases a with
  | p => simp [FusionFree, effectiveEvent]
  | d =>
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
        simp [FusionFree, effectiveEvent, h0, h1]

theorem eventTrace_append (F : Finset α) (s : Execution n α)
    (u v : List Letter) :
    eventTrace F s (u ++ v) =
      eventTrace F s u ++ eventTrace F (run F s u) v := by
  induction u generalizing s with
  | nil => rfl
  | cons a rest ih =>
      change (effectiveEvent s a).toList ++ eventTrace F (step F s a) (rest ++ v) = _
      rw [ih]
      simp [eventTrace, run, List.append_assoc]

theorem eventTrace_eq_nil_iff (F : Finset α) (s : Execution n α)
    (word : List Letter) :
    eventTrace F s word = [] ↔ FusionFree F s word := by
  induction word generalizing s with
  | nil => simp [eventTrace, FusionFree]
  | cons a rest ih =>
      rw [fusionFree_cons_iff]
      cases he : effectiveEvent s a <;> simp [eventTrace, he, ih]

theorem runLogged_fullLog (F : Finset α) (s : LoggedExecution n α)
    (word : List Letter) :
    (runLogged F s word).fullLog = s.fullLog ++ eventTrace F s.state word := by
  induction word generalizing s with
  | nil => simp [runLogged, eventTrace]
  | cons a rest ih =>
      have head : (loggedStep F s a).fullLog =
          s.fullLog ++ (effectiveEvent s.state a).toList := by
        cases a with
        | p => simp [loggedStep, effectiveEvent]
        | d =>
            cases h0 : s.state.placed 0 <;> cases h1 : s.state.placed 1 <;>
              simp [loggedStep, effectiveEvent, h0, h1]
      change (runLogged F (loggedStep F s a) rest).fullLog = _
      rw [ih, head, loggedStep_state]
      simp [eventTrace, List.append_assoc]

/-- The first effective event has a real fusion-free prefix and literal ports. -/
theorem firstFusion_split (F : Finset α) (s : Execution n α)
    (word : List Letter) (nonempty : eventTrace F s word ≠ []) :
    ∃ u v : List Letter, ∃ A B : Finset α,
      word = u ++ (.d :: v) ∧
      FusionFree F s u ∧
      (run F s u).placed 0 = some A ∧
      (run F s u).placed 1 = some B ∧
      eventTrace F s word =
        [⟨A, B, A ∪ B⟩] ++ eventTrace F (step F (run F s u) .d) v := by
  induction word generalizing s with
  | nil => exact (nonempty rfl).elim
  | cons a rest ih =>
      cases he : effectiveEvent s a with
      | none =>
          have tail : eventTrace F (step F s a) rest ≠ [] := by
            simpa [eventTrace, he] using nonempty
          obtain ⟨u, v, A, B, hw, hf, hA, hB, ht⟩ := ih (step F s a) tail
          refine ⟨a :: u, v, A, B, ?_, ?_, hA, hB, ?_⟩
          · simp [hw]
          · exact (fusionFree_cons_iff F s a u).mpr ⟨he, hf⟩
          · simpa [eventTrace, he, run] using ht
      | some event =>
          cases a with
          | p => simp [effectiveEvent] at he
          | d =>
              cases h0 : s.placed 0 with
              | none => simp [effectiveEvent, h0] at he
              | some A =>
                  cases h1 : s.placed 1 with
                  | none => simp [effectiveEvent, h1] at he
                  | some B =>
                      exact ⟨[], rest, A, B, rfl, trivial, h0, h1,
                        by simp [eventTrace, effectiveEvent, h0, h1, run]⟩

end FusionLogReplay
