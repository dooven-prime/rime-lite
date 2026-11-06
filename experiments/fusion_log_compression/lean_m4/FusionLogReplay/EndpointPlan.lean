import FusionLogReplay.EndpointAlignment

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n r : ℕ} [NeZero n]

/-- Retain the actual M3 batch plan and its final charged rotation. -/
structure EndpointPlan (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n))) (r : ℕ) where
  mid : Placement n (Finset (ZMod n))
  flow : BatchPlacementPlan F s mid
  phase : ZMod n
  aligned : rotate phase mid = target
  batch_bound : flow.batches ≤ r - 1
  transfer_bound : flow.transfers ≤ (n - r) * (r - 1)

namespace EndpointPlan

variable {F : Finset (ZMod n)} {s : Execution n (ZMod n)}
variable {target : Placement n (Finset (ZMod n))}

def word (plan : EndpointPlan F s target r) : List Letter :=
  plan.flow.word ++ pWord plan.phase.val

theorem execute (plan : EndpointPlan F s target r) (rank_le : r ≤ n) :
    FusionFree F s plan.word ∧ run F s plan.word = {s with placed := target} ∧
      plan.word.length ≤ (3 * n - r) * (r - 1) + (n - 1) := by
  obtain ⟨free, executed, cost⟩ := batchPlan_gap_budget_with_phase F s plan.mid r
    plan.flow plan.phase rank_le plan.batch_bound plan.transfer_bound
  exact ⟨free, by rwa [plan.aligned] at executed, cost⟩

end EndpointPlan

theorem sameOrderPlacement_plan [NeZero r]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (first second : NamedCyclicPlacement n r (ZMod n)) (hn : 3 ≤ n)
    (source : s.placed = first.placed) (blocks : first.block = second.block) :
    Nonempty (EndpointPlan F s second.placed r) := by
  have hsource : s.placed = first.toGapFrame.decode := by
    rwa [first.toGapFrame_decode]
  have hblocks : first.toGapFrame.block = second.toGapFrame.block := blocks
  by_cases hone : r = 1
  · subst r
    have oneGap (frame : GapFrame n 1 (ZMod n)) : frame.gap 0 = n - 1 := by
      calc
        _ = ∑ j : ZMod 1, frame.gap j := by
          calc
            _ = ∑ _j : ZMod 1, frame.gap 0 := by simp
            _ = _ := Finset.sum_congr rfl (fun j _ =>
              congrArg frame.gap (Subsingleton.elim 0 j))
        _ = n - 1 := frame.gap_total
    have gaps : first.toGapFrame.gap = second.toGapFrame.gap := by
      funext i
      have hi : i = 0 := Subsingleton.elim _ _
      subst i
      exact (oneGap _).trans (oneGap _).symm
    obtain ⟨flow, hK, hM⟩ := BatchPlacementPlan.done_at F s first.toGapFrame.decode hsource
    refine ⟨⟨first.toGapFrame.decode, flow,
      second.toGapFrame.anchor - first.toGapFrame.anchor, ?_, ?_, ?_⟩⟩
    · rw [← second.toGapFrame_decode]
      exact first.toGapFrame.decode_phase second.toGapFrame gaps hblocks
    · simp [hK]
    · simp [hM]
  · have hr : 2 ≤ r := by have := NeZero.pos r; omega
    obtain ⟨mid, flow, gaps, names, hK, hM⟩ :=
      gapFramePlacement_plan F s first.toGapFrame second.toGapFrame hn hr hsource
    refine ⟨⟨mid.decode, flow, second.toGapFrame.anchor - mid.anchor, ?_, hK, hM⟩⟩
    rw [← second.toGapFrame_decode]
    exact mid.decode_phase second.toGapFrame gaps (names.trans hblocks)

theorem align_sourceOrdered_endpoint_plan
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n))) (hn : 3 ≤ n)
    (orderedSource : SourceOrdered s.placed) (orderedTarget : SourceOrdered target)
    (same : packetSet s.placed = packetSet target) :
    Nonempty (EndpointPlan F s target (packetRank target)) := by
  have sameFrozen : placedBlocks s.placed = placedBlocks target := by
    rw [← packetSet_eq_placedBlocks s.placed orderedSource,
      ← packetSet_eq_placedBlocks target orderedTarget]
    exact same
  letI : NeZero (placedBlocks s.placed).card :=
    ⟨Nat.ne_of_gt (sourceOrdered_blocks_card_pos s.placed orderedSource)⟩
  obtain ⟨a, b, ha, hb, blocks⟩ :=
    admit_same_oriented_block_cycle s.placed target
      (sourceOrdered_same_blocks_admit s.placed target orderedSource orderedTarget sameFrozen)
  have card : (placedBlocks s.placed).card = packetRank target := by
    rw [← packetSet_eq_placedBlocks s.placed orderedSource, same]
    rfl
  have plan := sameOrderPlacement_plan F s a b hn ha.symm blocks
  simpa only [hb, card] using plan

end FusionLogReplay
