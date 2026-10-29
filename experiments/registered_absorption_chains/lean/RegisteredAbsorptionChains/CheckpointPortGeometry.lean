import RegisteredAbsorptionChains.GapNamedPlacement
import RegisteredAbsorptionChains.CleanCheckpointStep
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]

/-- The R orientation needs no gap relocation: carrier and first outside
partner occupy the first two packed sites. -/
theorem packed_R_ports
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (hr : 2 ≤ r)
    (C B : Finset (ZMod n))
    (hC : first.block 0 = C) (hB : first.block 1 = B) :
    CheckpointPorts true (packedLegalNamed first hrn 0).placed C B := by
  have h := packed_adjacent_ports first hrn 0 (by omega)
  simpa [CheckpointPorts, hC, hB] using h

/-- The L orientation puts the last outside partner before the carrier
across the physical seam, with the spare sites after the carrier. -/
theorem gap_L_ports
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (hr : 2 ≤ r)
    (C B : Finset (ZMod n))
    (hC : first.block 0 = C)
    (hB : first.block ((r - 1 : ℕ) : ZMod r) = B) :
    CheckpointPorts false (gapLegalNamed first hrn).placed C B := by
  have h := gap_ports first hrn hr
  simpa [CheckpointPorts, hC, hB] using h

/-- Given one actual assembly schedule, the R checkpoint has a constructed
same-order target at the kernel ports. -/
theorem realize_packed_R_checkpoint
    (F C B : Finset (ZMod n))
    (start assembled : Execution n (ZMod n))
    (schedule : OutsideAssemblySchedule F C start assembled)
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F start)
    (source : assembled.placed = first.placed)
    (hC : first.block 0 = C) (hB : first.block 1 = B)
    (registered : start.origin.isSome = true)
    (inside : F ⊆ C)
    (hinvariant : PartnerAssemblyInvariant C B assembled) :
    ∃ word : List Letter,
      ReachableExecution F (run F start word) ∧
      (run F start word).origin = start.origin ∧
      (run F start word).chain =
        start.chain ++ [checkpointRecord true C B] ∧
      CleanOutside (C ∪ B) (run F start word) := by
  have hn : 2 ≤ n := le_trans hr hrn
  exact realize_clean_checkpoint_from_finished_partner F C B true start assembled
    schedule first (packedLegalNamed first hrn 0) hn hr reachable source
    (packedLegalNamed_same_order first ordered hrn 0)
    (packed_R_ports first hrn hr C B hC hB)
    registered inside hinvariant

/-- The same actual schedule supports an L checkpoint without reordering the
partner and carrier in the source-addressed absorption record. -/
theorem realize_gap_L_checkpoint
    (F C B : Finset (ZMod n))
    (start assembled : Execution n (ZMod n))
    (schedule : OutsideAssemblySchedule F C start assembled)
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F start)
    (source : assembled.placed = first.placed)
    (hC : first.block 0 = C)
    (hB : first.block ((r - 1 : ℕ) : ZMod r) = B)
    (registered : start.origin.isSome = true)
    (inside : F ⊆ C)
    (hinvariant : PartnerAssemblyInvariant C B assembled) :
    ∃ word : List Letter,
      ReachableExecution F (run F start word) ∧
      (run F start word).origin = start.origin ∧
      (run F start word).chain =
        start.chain ++ [checkpointRecord false C B] ∧
      CleanOutside (C ∪ B) (run F start word) := by
  have hn : 2 ≤ n := le_trans hr hrn
  exact realize_clean_checkpoint_from_finished_partner F C B false start assembled
    schedule first (gapLegalNamed first hrn) hn hr reachable source
    (gapLegalNamed_same_order first ordered hrn hr)
    (gap_L_ports first hrn hr C B hC hB)
    registered inside hinvariant

end RegisteredAbsorptionChains
