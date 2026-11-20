import RSR2History.SilentPreparation

namespace RSR2History

open RSR2.Parametric

theorem SameCyclicSignatures.refl (P : Placement n) : SameCyclicSignatures P P :=
  fun _ => .refl _

theorem SameCyclicSignatures.symm {P Q : Placement n}
    (h : SameCyclicSignatures P Q) : SameCyclicSignatures Q P :=
  fun layer => (h layer).symm

theorem SameCyclicSignatures.trans {P Q R : Placement n}
    (hPQ : SameCyclicSignatures P Q) (hQR : SameCyclicSignatures Q R) :
    SameCyclicSignatures P R := fun layer => (hPQ layer).trans (hQR layer)

/-- A successful primitive carrying exactly one declared effective event. -/
def EventStep (n : Nat) (hn : 1 < n) (P R : Placement n)
    (letter : Letter) (event : EffectiveEvent n) : Prop :=
  step n hn P letter = some R ∧ emittedEvents n hn P letter = [event]

theorem EventStep.runLogged {n : Nat} {hn : 1 < n} {P R : Placement n}
    {letter : Letter} {event : EffectiveEvent n}
    (h : EventStep n hn P R letter event) :
    runLogged n hn P [letter] = some (R, [event]) := by
  simp [RSR2History.runLogged, h.1, h.2]

/-- Replace both physical representatives by silent preparation, preserving
exactly the same ordered event tuple and literal target. -/
theorem event_transport {n : Nat} (hn : 1 < n)
    {P R P' R' : Placement n} {letter : Letter} {event : EffectiveEvent n}
    (h : EventStep n hn P R letter event)
    (hpre : SameCyclicSignatures P' P)
    (hpost : SameCyclicSignatures R' R) :
    ∃ word, runLogged n hn P' word = some (R', [event]) := by
  obtain ⟨before, hbefore⟩ := hpre.silentReachable hn
  obtain ⟨after, hafter⟩ := hpost.symm.silentReachable hn
  refine ⟨before ++ [letter] ++ after, ?_⟩
  rw [runLogged_append, runLogged_append, hbefore]
  simp [h.runLogged, hafter]

/-- The same transport principle for any already realized effective log. -/
theorem logged_history_transport {n : Nat} (hn : 1 < n)
    {P R P' R' : Placement n} {word : List Letter} {events : List (EffectiveEvent n)}
    (h : runLogged n hn P word = some (R, events))
    (hpre : SameCyclicSignatures P' P)
    (hpost : SameCyclicSignatures R' R) :
    ∃ replacement, runLogged n hn P' replacement = some (R', events) := by
  obtain ⟨before, hbefore⟩ := hpre.silentReachable hn
  obtain ⟨after, hafter⟩ := hpost.symm.silentReachable hn
  refine ⟨before ++ word ++ after, ?_⟩
  simp [runLogged_append, hbefore, h, hafter]

end RSR2History
