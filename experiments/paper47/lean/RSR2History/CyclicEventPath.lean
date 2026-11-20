import RSR2History.CyclicEventRealization

namespace RSR2History

open RSR2.Parametric

/-- Paths in the typed cyclic event system. The zero-event case is equality
of the two cyclic signatures, so no physical coordinates are retained. -/
inductive CyclicEventPath : Placement n → List (EffectiveEvent n) → Placement n → Prop
  | nil {P Q : Placement n} (same : SameCyclicSignatures P Q) : CyclicEventPath P [] Q
  | cons {P R Q : Placement n} {event : EffectiveEvent n} {events : List (EffectiveEvent n)}
      (edge : CyclicEventEdge P event R) (tail : CyclicEventPath R events Q) :
      CyclicEventPath P (event :: events) Q

theorem CyclicEventPath.congr {P Q P' Q' : Placement n} {events : List (EffectiveEvent n)}
    (h : CyclicEventPath P events Q)
    (hP : SameCyclicSignatures P' P) (hQ : SameCyclicSignatures Q' Q) :
    CyclicEventPath P' events Q' := by
  induction h generalizing P' Q' with
  | nil same => exact .nil ((hP.trans same).trans hQ.symm)
  | cons edge tail ih =>
      exact .cons (edge.congr hP (.refl _)) (ih (.refl _) hQ)

/-- H2-B sufficiency: concatenate one-event witnesses on one actual state
chain; finish at the specified literal target via H1. -/
theorem CyclicEventPath.realize {n : Nat} (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)} (h : CyclicEventPath P events Q) :
    ∃ word, runLogged n hn P word = some (Q, events) := by
  induction h with
  | nil same => exact same.silentReachable hn
  | cons edge tail ih =>
      obtain ⟨u, hu⟩ := edge.realize hn
      obtain ⟨v, hv⟩ := ih
      exact ⟨u ++ v, by simp [runLogged_append, hu, hv]⟩

theorem emittedEvents_nil_or_singleton (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    emittedEvents n hn P letter = [] ∨
      ∃ event, emittedEvents n hn P letter = [event] := by
  classical
  cases letter with
  | p layer => exact Or.inl rfl
  | d layer =>
      by_cases hb : occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn)
      · exact Or.inr ⟨.fusion layer (packetAt P layer (site0 n (by omega)))
          (packetAt P layer (site1 n hn))
          (packetAt P layer (site0 n (by omega)) ∪ packetAt P layer (site1 n hn)),
          by simp [emittedEvents, hb]⟩
      · exact Or.inl (by simp [emittedEvents, hb])
  | v => exact Or.inr ⟨_, rfl⟩

/-- H2 necessity: erase silent letters from the same actual guarded run. -/
theorem runLogged_cyclicEventPath (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (h : runLogged n hn P word = some (Q, events)) : CyclicEventPath P events Q := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using h
      rcases he with ⟨rfl, rfl⟩
      exact .nil (.refl _)
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at h
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at h
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using h
              have ht : CyclicEventPath R later Q := ih (by simpa [he.1] using hr)
              rcases emittedEvents_nil_or_singleton n hn P letter with hsilent | ⟨event, hevent⟩
              · have hsame : SameCyclicSignatures P R :=
                  (show SilentStep n hn P R letter from ⟨hs, hsilent⟩).sameCyclicSignatures
                have hlog : events = later := by simpa [hsilent] using he.2.symm
                subst events
                exact ht.congr hsame (.refl _)
              · have hstep : EventStep n hn P R letter event := ⟨hs, hevent⟩
                have hlog : events = event :: later := by simpa [hevent] using he.2.symm
                subst events
                exact .cons hstep.cyclicEventEdge ht

/-- H2, for arbitrary literal starts and targets, hence in particular for the
singleton seed. The abstract side has only typed cyclic-list event rewrites. -/
theorem cyclic_event_path_iff_joint_realizable (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (events : List (EffectiveEvent n)) :
    CyclicEventPath P events Q ↔ ∃ word, runLogged n hn P word = some (Q, events) :=
  ⟨fun h => h.realize hn, fun ⟨word, hw⟩ => runLogged_cyclicEventPath n hn word hw⟩

/-- The single-event cyclic rule is exact even with arbitrary silent work
before and after the observable letter. -/
theorem cyclicEventEdge_iff_one_event_word (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (event : EffectiveEvent n) :
    CyclicEventEdge P event Q ↔ ∃ word, runLogged n hn P word = some (Q, [event]) := by
  refine ⟨fun h => h.realize hn, ?_⟩
  rintro ⟨word, hw⟩
  have hp := runLogged_cyclicEventPath n hn word hw
  cases hp with
  | cons edge tail =>
      cases tail with
      | nil same => exact edge.congr (.refl _) same.symm

/-- A literal guarded endpoint accompanies the same exact effective log. -/
theorem CyclicEventPath.guarded_witness {n : Nat} (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)} (h : CyclicEventPath P events Q) :
    ∃ word, run n hn P word = some Q ∧ runLogged n hn P word = some (Q, events) := by
  obtain ⟨word, hw⟩ := h.realize hn
  exact ⟨word, by simpa [hw] using (runLogged_project n hn P word).symm, hw⟩

end RSR2History
