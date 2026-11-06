import FusionLogSchedule.CanonicalRealization

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n r : ℕ} [NeZero n] [NeZero r]

/-- The static source-lift endpoint interface is exactly the established
common positive named packet-cycle interface on the canonical alphabet. -/
theorem index_compatible_iff_named_cycle
    (source target : Placement n (Finset (ZMod n))) (hn : 3 ≤ n)
    (ordered : SourceOrdered source) (rank : (placedBlocks source).card = r) :
    IndexCompatible (packetSet source) target ↔
      SameOrientedBlockCycle (r := r) source target := by
  subst r
  constructor
  · intro compatible
    have same : placedBlocks source = placedBlocks target := by
      rw [← packetSet_eq_placedBlocks source ordered,
        ← packetSet_eq_placedBlocks target compatible.1]
      exact compatible.2.symm
    have common := sourceOrdered_same_blocks_admit source target ordered compatible.1 same
    exact common
  · intro common
    obtain ⟨a, b, ha, hb, blocks⟩ := admit_same_oriented_block_cycle source target common
    let initial : Execution n (ZMod n) := ⟨source, none, []⟩
    obtain ⟨word, free, endEq, _⟩ := sameOrderPlacement_short ∅ initial a b hn ha.symm blocks
    have endpoint : (run ∅ initial word).placed = target := by
      rw [endEq, hb]
    have targetOrdered := run_ordered ∅ initial word (by omega) ordered
    have same := packetSet_run_of_fusionFree ∅ initial word free
    rw [endpoint] at targetOrdered same
    exact ⟨targetOrdered, same⟩

end FusionLogSchedule
