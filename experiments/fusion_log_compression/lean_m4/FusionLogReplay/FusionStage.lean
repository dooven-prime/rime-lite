import FusionLogReplay.RankLedger

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

/-- An actual adjacent-parent route, including the gap it really crosses.
The batch and transfer counts are those of this word's M2 construction. -/
structure FusionStage (F : Finset (ZMod n)) (s : Execution n (ZMod n)) where
  qLeft : ZMod n
  qRight : ZMod n
  left : Finset (ZMod n)
  right : Finset (ZMod n)
  gap : ℕ
  three_le : 3 ≤ n
  ordered : SourceOrdered s.placed
  gap_small : gap ≤ n - 2
  sites : qRight = qLeft + 1 + (gap : ZMod n)
  at_left : s.placed qLeft = some left
  at_right : s.placed qRight = some right
  holes : ∀ i : ℕ, 1 ≤ i → i ≤ gap →
    s.placed (qRight - (i : ZMod n)) = none

namespace FusionStage

variable {F : Finset (ZMod n)} {s : Execution n (ZMod n)}

def word (stage : FusionStage F s) : List Letter :=
  adjacentFusionWord stage.qLeft stage.qRight stage.gap

def event (stage : FusionStage F s) : FusionRecord (ZMod n) :=
  ⟨stage.left, stage.right, stage.left ∪ stage.right⟩

def budget (stage : FusionStage F s) : RouteBudget :=
  adjacentFusionBudget stage.qLeft stage.qRight stage.gap

def next (stage : FusionStage F s) : Execution n (ZMod n) := run F s stage.word

theorem trace (stage : FusionStage F s) :
    eventTrace F s stage.word = [stage.event] := by
  obtain ⟨free, left, right, _, _, _, _⟩ :=
    adjacentFusionWord_spec F s stage.qLeft stage.qRight stage.left stage.right stage.gap
      stage.three_le stage.gap_small stage.sites stage.at_left stage.at_right stage.holes
  change eventTrace F s (adjacentRoutePrefix _ _ _ ++ [.d]) = _
  rw [eventTrace_append, (eventTrace_eq_nil_iff F s _).mpr free]
  simp [eventTrace, effectiveEvent, left, right, event]

theorem next_ordered (stage : FusionStage F s) : SourceOrdered stage.next.placed :=
  run_ordered F s stage.word (by have := stage.three_le; omega) stage.ordered

theorem gap_le_holes (stage : FusionStage F s) :
    stage.gap ≤ n - packetRank s.placed :=
  gap_le_hole_count s.placed stage.qRight stage.gap
    (by have := stage.gap_small; have := stage.three_le; omega)
    (sourceOrdered_uniquePackets _ stage.ordered) stage.holes

theorem rank_drop (stage : FusionStage F s) :
    packetRank stage.next.placed + 1 = packetRank s.placed := by
  have ledger := packetRank_run_ledger F s stage.word stage.three_le stage.ordered
  simpa only [next, stage.trace, List.length_singleton] using ledger

theorem cost (stage : FusionStage F s) :
    stage.budget.batches ≤ 1 ∧ stage.budget.holeTransfers = stage.gap ∧
      stage.word.length ≤ 3 * n + stage.gap :=
  adjacentFusionWord_budget F s stage.qLeft stage.qRight stage.left stage.right stage.gap
    stage.three_le stage.gap_small stage.sites stage.at_left stage.at_right stage.holes

theorem no_batch_of_zero_gap (stage : FusionStage F s) (zero : stage.gap = 0) :
    stage.budget.batches = 0 := by
  simp [budget, adjacentFusionBudget, zero]

end FusionStage
end FusionLogReplay
