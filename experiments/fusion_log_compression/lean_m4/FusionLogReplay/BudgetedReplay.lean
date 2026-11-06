import FusionLogReplay.FirstEventRoute
import FusionLogReplay.ReplayPlan

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

/-- The replay certificate retains the routed gap and actual successor at
every step, rather than charging every event a fresh full-size gap. -/
theorem replay_complete_events_plan
    (F : Finset (ZMod n)) (reference current : Execution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n)
    (orderedReference : SourceOrdered reference.placed)
    (orderedCurrent : SourceOrdered current.placed)
    (same : packetSet current.placed = packetSet reference.placed) :
    ∃ last : Execution n (ZMod n), ∃ plan : FusionReplayPlan F current last,
      plan.events = eventTrace F reference word ∧ SourceOrdered last.placed ∧
      packetSet last.placed = packetSet (run F reference word).placed := by
  by_cases empty : eventTrace F reference word = []
  · refine ⟨current, .done current, empty.symm, orderedCurrent, ?_⟩
    exact same.trans (packetSet_run_of_fusionFree F reference word
      ((eventTrace_eq_nil_iff F reference word).mp empty)).symm
  · obtain ⟨u, v, stage, hw, _, splitTrace, _, headOrdered, sameNext, _⟩ :=
      firstEvent_replay_step F reference current word hn
        orderedReference orderedCurrent same empty
    let nextReference := step F (run F reference u) .d
    have nextOrdered : SourceOrdered nextReference.placed :=
      step_ordered F (run F reference u) .d (by omega)
        (run_ordered F reference u (by omega) orderedReference)
    obtain ⟨last, tail, tailTrace, tailOrdered, tailSame⟩ :=
      replay_complete_events_plan F nextReference stage.next v hn
        nextOrdered headOrdered sameNext
    have referenceEnd : run F reference word = run F nextReference v := by
      rw [hw, run_append]
      rfl
    refine ⟨last, .step stage tail, ?_, tailOrdered, ?_⟩
    · change stage.event :: tail.events = _
      rw [tailTrace]
      exact splitTrace.symm
    · rwa [referenceEnd]
termination_by word.length
decreasing_by
  have lengths := congrArg List.length hw
  simp only [List.length_append, List.length_cons] at lengths
  omega

end FusionLogReplay
