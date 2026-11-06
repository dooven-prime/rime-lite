import FusionLogReplay.ReplayInduction
import RegisteredAbsorptionChains.CanonicalBlockNaming

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

theorem packetSet_eq_placedBlocks
    (P : Placement n (Finset (ZMod n))) (ordered : SourceOrdered P) :
    packetSet P = placedBlocks P := by
  ext B
  rw [mem_packetSet, mem_placedBlocks]
  constructor
  · rintro ⟨q, hq⟩
    obtain ⟨lift, hp⟩ := ordered
    have nonempty := (placementOfMap_some_iff lift.position q B).mp (hp ▸ hq)
    exact ⟨nonempty.2, q, hq⟩
  · rintro ⟨_, q, hq⟩
    exact ⟨q, hq⟩

/-- Apply M3 to two actual source-ordered placements with the same packets. -/
theorem align_sourceOrdered_endpoint
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n))) (hn : 3 ≤ n)
    (orderedSource : SourceOrdered s.placed)
    (orderedTarget : SourceOrdered target)
    (same : packetSet s.placed = packetSet target) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = {s with placed := target} ∧
      word.length ≤
        (3 * n - (packetSet target).card) * ((packetSet target).card - 1) + (n - 1) := by
  have sameFrozen : placedBlocks s.placed = placedBlocks target := by
    rw [← packetSet_eq_placedBlocks s.placed orderedSource,
      ← packetSet_eq_placedBlocks target orderedTarget]
    exact same
  letI : NeZero (placedBlocks s.placed).card :=
    ⟨Nat.ne_of_gt (sourceOrdered_blocks_card_pos s.placed orderedSource)⟩
  obtain ⟨a, b, ha, hb, blocks⟩ :=
    admit_same_oriented_block_cycle s.placed target
      (sourceOrdered_same_blocks_admit s.placed target orderedSource orderedTarget sameFrozen)
  obtain ⟨word, free, executed, cost⟩ :=
    sameOrderPlacement_short F s a b hn ha.symm blocks
  have card : (placedBlocks s.placed).card = (packetSet target).card := by
    rw [← packetSet_eq_placedBlocks s.placed orderedSource, same]
  refine ⟨word, free, ?_, ?_⟩
  · rwa [hb] at executed
  · rwa [card] at cost

/-- A complete-log/endpoint representative on the frozen source-ordered
domain. This preliminary budget is not the manuscript's sharp B(n,t,s). -/
theorem sourceOrdered_log_endpoint_representative
    (F : Finset (ZMod n)) (s : LoggedExecution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.state.placed) :
    ∃ representative : List Letter,
      (runLogged F s representative).fullLog = (runLogged F s word).fullLog ∧
      (runLogged F s representative).state.placed = (runLogged F s word).state.placed ∧
      representative.length ≤
        (4 * n - 2) * (eventTrace F s.state word).length +
        (3 * n - (packetSet (run F s.state word).placed).card) *
          ((packetSet (run F s.state word).placed).card - 1) + (n - 1) := by
  obtain ⟨route, trace, routeOrdered, same, cost⟩ :=
    replay_complete_events F s.state s.state word hn ordered ordered rfl
  have targetOrdered := run_ordered F s.state word (by omega) ordered
  obtain ⟨align, free, aligned, alignCost⟩ :=
    align_sourceOrdered_endpoint F (run F s.state route)
      (run F s.state word).placed hn routeOrdered targetOrdered same
  refine ⟨route ++ align, ?_, ?_, ?_⟩
  · rw [runLogged_fullLog, runLogged_fullLog, eventTrace_append, trace,
      (eventTrace_eq_nil_iff F (run F s.state route) align).mpr free, List.append_nil]
  · rw [runLogged_state, runLogged_state, run_append, aligned]
  · rw [List.length_append]
    omega

end FusionLogReplay
