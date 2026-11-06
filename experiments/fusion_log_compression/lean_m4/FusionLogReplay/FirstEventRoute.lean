import FusionLogReplay.FusionStage

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

theorem eventTrace_adjacentFusionWord (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (holes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    eventTrace F s (adjacentFusionWord qLeft qRight f) = [⟨A, B, A ∪ B⟩] := by
  obtain ⟨free, left, right, _, _, _, _⟩ :=
    adjacentFusionWord_spec F s qLeft qRight A B f hn hfn hgap hA hB holes
  change eventTrace F s (adjacentRoutePrefix qLeft qRight f ++ [.d]) = _
  rw [eventTrace_append, (eventTrace_eq_nil_iff F s _).mpr free]
  simp [eventTrace, effectiveEvent, left, right]

/-- The first event of a reference execution can be routed from a different
actual source-ordered representative with the same packet partition. -/
theorem firstEvent_route
    (F : Finset (ZMod n)) (reference current : Execution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n)
    (orderedReference : SourceOrdered reference.placed)
    (orderedCurrent : SourceOrdered current.placed)
    (same : packetSet current.placed = packetSet reference.placed)
    (nonempty : eventTrace F reference word ≠ []) :
    ∃ u v : List Letter, ∃ A B : Finset (ZMod n),
      ∃ qLeft qRight : ZMod n, ∃ f : ℕ,
      word = u ++ (.d :: v) ∧
      FusionFree F reference u ∧
      (run F reference u).placed 0 = some A ∧
      (run F reference u).placed 1 = some B ∧
      eventTrace F reference word =
        [⟨A, B, A ∪ B⟩] ++ eventTrace F (step F (run F reference u) .d) v ∧
      current.placed qLeft = some A ∧ current.placed qRight = some B ∧
      qRight = qLeft + 1 + (f : ZMod n) ∧ f ≤ n - 2 ∧
      (∀ i : ℕ, 1 ≤ i → i ≤ f →
        current.placed (qRight - (i : ZMod n)) = none) ∧
      eventTrace F current (adjacentFusionWord qLeft qRight f) = [⟨A, B, A ∪ B⟩] ∧
      (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f := by
  obtain ⟨u, v, A, B, hw, free, left, right, trace⟩ :=
    firstFusion_split F reference word nonempty
  have beforeOrdered : SourceOrdered (run F reference u).placed :=
    run_ordered F reference u (by omega) orderedReference
  obtain ⟨_, _, distinct, boundary⟩ :=
    sourceAtomAdjacent_of_actual_fusion (run F reference u) A B beforeOrdered hn left right
  have beforeSame : packetSet current.placed = packetSet (run F reference u).placed :=
    same.trans (packetSet_run_of_fusionFree F reference u free).symm
  have presentA : ∃ q, current.placed q = some A := by
    apply (mem_packetSet current.placed A).mp
    rw [beforeSame]
    exact (mem_packetSet (run F reference u).placed A).mpr ⟨0, left⟩
  have presentB : ∃ q, current.placed q = some B := by
    apply (mem_packetSet current.placed B).mp
    rw [beforeSame]
    exact (mem_packetSet (run F reference u).placed B).mpr ⟨1, right⟩
  obtain ⟨qLeft, qRight, f, hA, hB, gap, small, holes, spec⟩ :=
    sourceAtomAdjacentFusionWord_spec F current A B distinct orderedCurrent
      presentA presentB boundary hn
  exact ⟨u, v, A, B, qLeft, qRight, f, hw, free, left, right, trace, hA, hB, gap, small, holes,
    eventTrace_adjacentFusionWord F current qLeft qRight A B f hn small gap hA hB holes,
    spec.2.2.2.2.2.2⟩

/-- One replayed event supplies the actual representative for the next event:
the ordered log head agrees and both successor packet partitions agree. -/
theorem firstEvent_replay_step
    (F : Finset (ZMod n)) (reference current : Execution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n)
    (orderedReference : SourceOrdered reference.placed)
    (orderedCurrent : SourceOrdered current.placed)
    (same : packetSet current.placed = packetSet reference.placed)
    (nonempty : eventTrace F reference word ≠ []) :
    ∃ u v : List Letter, ∃ stage : FusionStage F current,
      word = u ++ (.d :: v) ∧
      FusionFree F reference u ∧
      eventTrace F reference word =
        [stage.event] ++ eventTrace F (step F (run F reference u) .d) v ∧
      eventTrace F current stage.word = [stage.event] ∧
      SourceOrdered stage.next.placed ∧
      packetSet stage.next.placed =
        packetSet (step F (run F reference u) .d).placed ∧
      stage.gap ≤ n - packetRank current.placed ∧
      stage.word.length ≤ 3 * n + stage.gap ∧
      stage.budget.batches ≤ 1 ∧ stage.budget.holeTransfers = stage.gap ∧
      (stage.gap = 0 → stage.budget.batches = 0) := by
  obtain ⟨u, v, A, B, qLeft, qRight, f, hw, free, refLeft, refRight, trace,
      hA, hB, gap, small, holes, actualTrace, cost⟩ :=
    firstEvent_route F reference current word hn orderedReference orderedCurrent same nonempty
  let stage : FusionStage F current :=
    ⟨qLeft, qRight, A, B, f, hn, orderedCurrent, small, gap, hA, hB, holes⟩
  let headWord := adjacentRoutePrefix qLeft qRight f
  let mid := run F current headWord
  obtain ⟨prefixFree, midLeft, midRight, executed, _, _, _⟩ :=
    adjacentFusionWord_spec F current qLeft qRight A B f hn small gap hA hB holes
  have beforeSame : packetSet mid.placed = packetSet (run F reference u).placed := by
    exact (packetSet_run_of_fusionFree F current headWord prefixFree).trans
      (same.trans (packetSet_run_of_fusionFree F reference u free).symm)
  have beforeOrdered : SourceOrdered (run F reference u).placed :=
    run_ordered F reference u (by omega) orderedReference
  have midOrdered : SourceOrdered mid.placed :=
    run_ordered F current headWord (by omega) orderedCurrent
  refine ⟨u, v, stage, hw, free, trace, actualTrace,
    stage.next_ordered, ?_, stage.gap_le_holes, stage.cost.2.2,
    stage.cost.1, stage.cost.2.1, stage.no_batch_of_zero_gap⟩
  change packetSet (run F current (adjacentFusionWord qLeft qRight f)).placed =
    packetSet (stepDefect F (run F reference u)).placed
  rw [executed, stepDefect_placed_eq, stepDefect_placed_eq]
  rw [packetSet_fusion _ A B (sourceOrdered_uniquePackets _ midOrdered)
    midLeft midRight]
  rw [packetSet_fusion _ A B (sourceOrdered_uniquePackets _ beforeOrdered)
    refLeft refRight, beforeSame]

end FusionLogReplay
