import FusionLogSchedule.AbstractTrace

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n : ℕ} [NeZero n]

theorem abstract_step_realizable (F : Finset (ZMod n)) (source : Execution n (ZMod n))
    (C : IndexPackets n) (A B : Finset (ZMod n)) (hn : 3 ≤ n)
    (ordered : SourceOrdered source.placed) (same : packetSet source.placed = C)
    (left : A ∈ C) (right : B ∈ C) (distinct : A ≠ B)
    (boundary : SourceAtomAdjacent A B) :
    ∃ stage : FusionStage F source, stage.event = ⟨A, B, A ∪ B⟩ ∧
      packetSet stage.next.placed = mergePackets C A B := by
  have presentA := (mem_packetSet source.placed A).mp (same.symm ▸ left)
  have presentB := (mem_packetSet source.placed B).mp (same.symm ▸ right)
  obtain ⟨qLeft, qRight, f, atLeft, atRight, gap, small, holes, spec⟩ :=
    sourceAtomAdjacentFusionWord_spec F source A B distinct ordered presentA presentB boundary hn
  let stage : FusionStage F source :=
    ⟨qLeft, qRight, A, B, f, hn, ordered, small, gap, atLeft, atRight, holes⟩
  obtain ⟨free, midLeft, midRight, executed, _, _, _⟩ := spec
  have midOrdered := run_ordered F source (adjacentRoutePrefix qLeft qRight f) (by omega) ordered
  refine ⟨stage, rfl, ?_⟩
  change packetSet (run F source (adjacentFusionWord qLeft qRight f)).placed = _
  rw [executed, stepDefect_placed_eq,
    packetSet_fusion _ A B (sourceOrdered_uniquePackets _ midOrdered) midLeft midRight,
    packetSet_run_of_fusionFree F source _ free, same]
  rfl

theorem AbstractTrace.realize {C last : IndexPackets n}
    {events : List (FusionRecord (ZMod n))} (trace : AbstractTrace C events last)
    (F : Finset (ZMod n)) (source : Execution n (ZMod n)) (hn : 3 ≤ n)
    (ordered : SourceOrdered source.placed) (same : packetSet source.placed = C) :
    ∃ word : List Letter,
      eventTrace F source word = events ∧ SourceOrdered (run F source word).placed ∧
      packetSet (run F source word).placed = last := by
  induction trace generalizing source with
  | nil C => exact ⟨[], rfl, ordered, same⟩
  | @cons C last A B rest left right distinct boundary tail ih =>
      obtain ⟨stage, eventEq, next⟩ :=
        abstract_step_realizable F source C A B hn ordered same left right distinct boundary
      obtain ⟨word, logs, finalOrdered, finalPackets⟩ :=
        ih stage.next stage.next_ordered next
      refine ⟨stage.word ++ word, ?_, ?_, ?_⟩
      · rw [eventTrace_append, stage.trace]
        change [stage.event] ++ eventTrace F stage.next word = _
        rw [logs, eventEq]
        rfl
      · simpa only [run_append, FusionStage.next] using finalOrdered
      · simpa only [run_append, FusionStage.next] using finalPackets

theorem actual_trace_admissible (F : Finset (ZMod n))
    (source : Execution n (ZMod n)) (word : List Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered source.placed) :
    AbstractTrace (packetSet source.placed) (eventTrace F source word)
      (packetSet (run F source word).placed) := by
  induction word generalizing source with
  | nil => exact .nil _
  | cons a rest ih =>
      have nextOrdered := step_ordered F source a (by omega) ordered
      have tail := ih (step F source a) nextOrdered
      cases he : effectiveEvent source a with
      | none =>
          have same := packetSet_step_of_noEvent F source a he
          rw [same] at tail
          simpa only [eventTrace, he, Option.toList_none, List.nil_append, run,
            List.foldl_cons] using tail
      | some event =>
          cases a with
          | p => simp [effectiveEvent] at he
          | d =>
              cases h0 : source.placed 0 with
              | none => simp [effectiveEvent, h0] at he
              | some A =>
                  cases h1 : source.placed 1 with
                  | none => simp [effectiveEvent, h1] at he
                  | some B =>
                      have eventEq : event = ⟨A, B, A ∪ B⟩ := by
                        simpa [effectiveEvent, h0, h1] using he.symm
                      obtain ⟨_, _, distinct, boundary⟩ :=
                        sourceAtomAdjacent_of_actual_fusion source A B ordered hn h0 h1
                      have next : packetSet (step F source .d).placed =
                          mergePackets (packetSet source.placed) A B := by
                        change packetSet (stepDefect F source).placed = _
                        rw [stepDefect_placed_eq,
                          packetSet_fusion _ A B (sourceOrdered_uniquePackets _ ordered) h0 h1]
                        rfl
                      rw [next] at tail
                      have formal := AbstractTrace.cons
                        ((mem_packetSet _ A).mpr ⟨0, h0⟩)
                        ((mem_packetSet _ B).mpr ⟨1, h1⟩) distinct boundary tail
                      simpa only [eventTrace, he, Option.toList_some, List.singleton_append,
                        eventEq, run, List.foldl_cons] using formal

theorem realize_index_joint (F : Finset (ZMod n)) (source : Execution n (ZMod n))
    (events : List (FusionRecord (ZMod n))) (last : IndexPackets n)
    (target : Placement n (Finset (ZMod n))) (hn : 3 ≤ n)
    (ordered : SourceOrdered source.placed)
    (trace : AbstractTrace (packetSet source.placed) events last)
    (compatible : IndexCompatible last target) :
    ∃ word : List Letter, eventTrace F source word = events ∧ (run F source word).placed = target := by
  obtain ⟨route, logs, finalOrdered, finalPackets⟩ := trace.realize F source hn ordered rfl
  obtain ⟨suffix, free, placed, _⟩ := align_sourceOrdered_endpoint F (run F source route)
    target hn finalOrdered compatible.1 (finalPackets.trans compatible.2.symm)
  refine ⟨route ++ suffix, ?_, ?_⟩
  · rw [eventTrace_append, logs,
      (eventTrace_eq_nil_iff F (run F source route) suffix).mpr free, List.append_nil]
  · rw [run_append, placed]

theorem index_joint_iff (F : Finset (ZMod n)) (source : Execution n (ZMod n))
    (events : List (FusionRecord (ZMod n))) (target : Placement n (Finset (ZMod n)))
    (hn : 3 ≤ n) (ordered : SourceOrdered source.placed) :
    (∃ word : List Letter, eventTrace F source word = events ∧ (run F source word).placed = target) ↔
      ∃ last : IndexPackets n, AbstractTrace (packetSet source.placed) events last ∧
        IndexCompatible last target := by
  constructor
  · rintro ⟨word, logs, placed⟩
    refine ⟨packetSet target, ?_, ?_⟩
    · have trace := actual_trace_admissible F source word hn ordered
      rwa [logs, placed] at trace
    · exact ⟨placed ▸ run_ordered F source word (by omega) ordered, rfl⟩
  · rintro ⟨last, trace, compatible⟩
    exact realize_index_joint F source events last target hn ordered trace compatible

end FusionLogSchedule
