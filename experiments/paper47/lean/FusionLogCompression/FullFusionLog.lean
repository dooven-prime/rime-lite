import FusionLogCompression.SourceAdjacentGap

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n : ℕ} {α : Type*} [NeZero n] [DecidableEq α]

/-- The frozen `Execution` records only the selected registration and carrier
chain. This wrapper separately accumulates every effective ordered fusion. -/
structure LoggedExecution (n : ℕ) (α : Type*) where
  state : Execution n α
  fullLog : List (FusionRecord α)

/-- A defect step appends an event exactly when both physical ports are
occupied, independently of whether that event is selected by the consumer. -/
def loggedStep (F : Finset α) (s : LoggedExecution n α) : Letter → LoggedExecution n α
  | .p => ⟨step F s.state .p, s.fullLog⟩
  | .d =>
      match s.state.placed 0, s.state.placed 1 with
      | some A, some B =>
          ⟨step F s.state .d,
            s.fullLog ++ [⟨A, B, A ∪ B⟩]⟩
      | _, _ => ⟨step F s.state .d, s.fullLog⟩

/-- Chronological execution in the full-log extension of the frozen model. -/
def runLogged (F : Finset α) (s : LoggedExecution n α) (word : List Letter) :
    LoggedExecution n α :=
  word.foldl (loggedStep F) s

theorem loggedStep_state (F : Finset α) (s : LoggedExecution n α) (a : Letter) :
    (loggedStep F s a).state = step F s.state a := by
  cases a
  · rfl
  · cases h0 : s.state.placed 0 <;> cases h1 : s.state.placed 1 <;>
      simp [loggedStep, stepDefect, h0, h1]

theorem runLogged_state (F : Finset α) (s : LoggedExecution n α)
    (word : List Letter) :
    (runLogged F s word).state = run F s.state word := by
  induction word generalizing s with
  | nil => rfl
  | cons a rest ih =>
      calc
        (runLogged F s (a :: rest)).state =
            (runLogged F (loggedStep F s a) rest).state := rfl
        _ = run F (loggedStep F s a).state rest := ih _
        _ = run F (step F s.state a) rest := by rw [loggedStep_state]
        _ = run F s.state (a :: rest) := rfl

theorem runLogged_append (F : Finset α) (s : LoggedExecution n α)
    (u v : List Letter) :
    runLogged F s (u ++ v) = runLogged F (runLogged F s u) v := by
  simp [runLogged, List.foldl_append]

theorem runLogged_log_eq_of_fusionFree (F : Finset α)
    (s : LoggedExecution n α) (word : List Letter)
    (hfree : FusionFree F s.state word) :
    (runLogged F s word).fullLog = s.fullLog := by
  induction word generalizing s with
  | nil => rfl
  | cons a rest ih =>
      cases a with
      | p =>
          simp only [FusionFree] at hfree
          calc
            (runLogged F s (.p :: rest)).fullLog =
                (runLogged F (loggedStep F s .p) rest).fullLog := rfl
            _ = (loggedStep F s .p).fullLog := ih _ hfree
            _ = s.fullLog := rfl
      | d =>
          simp only [FusionFree] at hfree
          rcases hfree with ⟨hempty, hrest⟩
          have hlog : (loggedStep F s .d).fullLog = s.fullLog := by
            cases h0 : s.state.placed 0 <;> cases h1 : s.state.placed 1 <;>
              simp [loggedStep, h0, h1] at hempty ⊢
          calc
            (runLogged F s (.d :: rest)).fullLog =
                (runLogged F (loggedStep F s .d) rest).fullLog := rfl
            _ = (loggedStep F s .d).fullLog :=
                ih _ (by simpa [loggedStep_state] using hrest)
            _ = s.fullLog := hlog

/-- On a fusion-free route, the full ordered log is untouched. -/
theorem loggedAdjacentFusionWord_fullLog (F : Finset α)
    (s : Execution n α) (initialLog : List (FusionRecord α))
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    let route := adjacentRoutePrefix qLeft qRight f
    let word := adjacentFusionWord qLeft qRight f
    let logged : LoggedExecution n α := ⟨s, initialLog⟩
    (runLogged F logged word).fullLog =
      initialLog ++ [⟨A, B, A ∪ B⟩] := by
  let route := adjacentRoutePrefix qLeft qRight f
  let word := adjacentFusionWord qLeft qRight f
  let logged : LoggedExecution n α := ⟨s, initialLog⟩
  have hspec := adjacentFusionWord_spec F s qLeft qRight A B f
    hn hfn hgap hA hB hholes
  rcases hspec with ⟨hfree, hleft, hright, hrun, _, _, _⟩
  have hprefixLog :
      (runLogged F logged route).fullLog = initialLog :=
    runLogged_log_eq_of_fusionFree F logged route hfree
  have hmid : (runLogged F logged route).state = run F s route := by
    simpa [logged] using runLogged_state F logged route
  have hports0 : (runLogged F logged route).state.placed 0 = some A := by
    rw [hmid]
    exact hleft
  have hports1 : (runLogged F logged route).state.placed 1 = some B := by
    rw [hmid]
    exact hright
  have hword : word = route ++ [.d] := by rfl
  change (runLogged F logged word).fullLog = initialLog ++ [⟨A, B, A ∪ B⟩]
  rw [hword, runLogged_append]
  have hlastLog :
      (loggedStep F (runLogged F logged route) .d).fullLog =
        initialLog ++ [⟨A, B, A ∪ B⟩] := by
    simp [loggedStep, hprefixLog, hports0, hports1]
  simpa [runLogged] using hlastLog

end FusionLogCompression
