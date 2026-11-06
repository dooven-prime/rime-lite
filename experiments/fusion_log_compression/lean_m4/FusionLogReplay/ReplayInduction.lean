import FusionLogReplay.FirstEventRoute

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

/-- Replay every complete event, keeping the actual successor partition as
the invariant. Literal endpoint alignment and the sharp budget are separate. -/
theorem replay_complete_events
    (F : Finset (ZMod n)) (reference current : Execution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n)
    (orderedReference : SourceOrdered reference.placed)
    (orderedCurrent : SourceOrdered current.placed)
    (same : packetSet current.placed = packetSet reference.placed) :
    ∃ route : List Letter,
      eventTrace F current route = eventTrace F reference word ∧
      SourceOrdered (run F current route).placed ∧
      packetSet (run F current route).placed = packetSet (run F reference word).placed ∧
      route.length ≤ (4 * n - 2) * (eventTrace F reference word).length := by
  by_cases empty : eventTrace F reference word = []
  · refine ⟨[], ?_, orderedCurrent, ?_, ?_⟩
    · simpa [eventTrace] using empty.symm
    · exact same.trans
        (packetSet_run_of_fusionFree F reference word
          ((eventTrace_eq_nil_iff F reference word).mp empty)).symm
    · simp [empty]
  · obtain ⟨u, v, stage, hw, free, splitTrace, headTrace,
        headOrdered, sameNext, _, sharpCost, _⟩ :=
      firstEvent_replay_step F reference current word hn
        orderedReference orderedCurrent same empty
    let headRoute := stage.word
    have headCost : headRoute.length ≤ 4 * n - 2 := by
      have := stage.gap_small
      dsimp [headRoute]
      omega
    let nextReference := step F (run F reference u) .d
    let nextCurrent := run F current headRoute
    have nextOrdered : SourceOrdered nextReference.placed :=
      step_ordered F (run F reference u) .d (by omega)
        (run_ordered F reference u (by omega) orderedReference)
    obtain ⟨tailRoute, tailTrace, tailOrdered, tailSame, tailCost⟩ :=
      replay_complete_events F nextReference nextCurrent v hn
        nextOrdered headOrdered sameNext
    have referenceEnd : run F reference word = run F nextReference v := by
      rw [hw, run_append]
      rfl
    refine ⟨headRoute ++ tailRoute, ?_, ?_, ?_, ?_⟩
    · rw [eventTrace_append, headTrace, tailTrace]
      exact splitTrace.symm
    · simpa [run_append, nextCurrent] using tailOrdered
    · simpa [run_append, referenceEnd, nextCurrent] using tailSame
    · have lengths := congrArg List.length splitTrace
      simp only [List.length_append, List.length_singleton] at lengths
      calc
        (headRoute ++ tailRoute).length = headRoute.length + tailRoute.length :=
          List.length_append
        _ ≤ (4 * n - 2) + (4 * n - 2) * (eventTrace F nextReference v).length :=
          Nat.add_le_add headCost tailCost
        _ = (4 * n - 2) * (eventTrace F reference word).length := by
          rw [lengths, Nat.mul_add, Nat.mul_one]
termination_by word.length
decreasing_by
  have lengths := congrArg List.length hw
  simp only [List.length_append, List.length_cons] at lengths
  omega

end FusionLogReplay
