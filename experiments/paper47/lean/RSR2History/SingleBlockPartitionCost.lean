import RSR2History.TotalObservationPremium
import RSR2History.ObservationPartitionBridge

/-!
The minimum raw-word cost of the one-block unordered partition. The lower
bound applies to every actual five-letter execution, with arbitrary layer,
phase, prefusion and transfer schedule at the endpoint.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- The full one-block observation forgets all literal endpoint coordinates. -/
theorem unorderedPacketBlocks_eq_singleBlock_iff
    (n : Nat) (hn : 0 < n) (Q : Placement n) :
    unorderedPacketBlocks n Q = {Finset.univ} ↔
      ∃ coord : Bool × Fin n, Q = fun _ => coord := by
  constructor
  · intro hblocks
    have hconst := unorderedPacketBlocks_constant n hn (false, site0 n hn)
    have hsame := (unorderedPacketBlocks_eq_iff_samePacket n Q
      (fun _ => (false, site0 n hn))).mp (hblocks.trans hconst.symm)
    refine ⟨Q (site0 n hn), ?_⟩
    funext a
    exact (hsame a (site0 n hn)).mpr rfl
  · rintro ⟨coord, rfl⟩
    exact unorderedPacketBlocks_constant n hn coord

private theorem constant_lowerPacketCount_le_one
    (n : Nat) (hn : 0 < n) (coord : Bool × Fin n) :
    lowerPacketCount (fun _ : Fin n => coord) ≤ 1 := by
  have hcount : totalPacketCount (fun _ : Fin n => coord) = 1 := by
    apply totalPacketCount_eq_representatives_length _ [coord] (by simp)
    intro loc
    simp only [List.mem_singleton]
    constructor
    · intro h
      exact ⟨site0 n hn, h.symm⟩
    · rintro ⟨_, h⟩
      exact h.symm
  unfold totalPacketCount at hcount
  omega

/-- Even allowing all layers and coordinates, any one-block realization
must pay the atom-2 approach debt and enough productive lower reductions. -/
theorem singleBlock_word_length_lower_bound
    (n : Nat) (hn : 1 < n) (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    2 * n - 3 ≤ word.length := by
  obtain ⟨coord, hQ⟩ := (unorderedPacketBlocks_eq_singleBlock_iff n (by omega) Q).mp hblocks
  by_cases hthree : 3 ≤ n
  · have hmerged : samePacket Q ⟨2, by omega⟩ (site0 n (by omega)) := by
      rw [hQ]
      rfl
    have hcontrol := singleton_run_atomTwo_serviced_control_lower_bound n
      (by omega) Q word hrun (Or.inr ⟨site0 n (by omega), by
        simp [site0, Fin.mk.injEq], hmerged⟩)
    have hcount : lowerPacketCount Q ≤ 1 := by
      rw [hQ]
      exact constant_lowerPacketCount_le_one n (by omega) coord
    have hlength := lowerPortCost_le_length word
    omega
  · have hn2 : n = 2 := by omega
    have hnonempty : word ≠ [] := by
      intro hw
      have hseed : seed n = Q := by simpa [hw, run] using hrun
      have hsame : seed n (site0 n (by omega)) = seed n (site1 n hn) := by
        rw [hseed, hQ]
      have hval := congrArg (fun x : Bool × Fin n => x.2.val) hsame
      simp [seed, site0, site1] at hval
    have hlen := List.length_pos_iff.mpr hnonempty
    omega

/-- The upper witness is independent of the chosen literal coordinate. -/
theorem singleBlockPartition_attainable (n : Nat) (hn : 1 < n) :
    ∃ word, RealizesUnorderedPartition n hn {Finset.univ} word := by
  refine ⟨lowerCoalescencePrefix (n - 2), (fun _ => (false, site0 n (by omega))), ?_, ?_⟩
  · rw [lowerCoalescencePrefix_run n hn, lowerCoalescenceStage_terminal n hn]
  · exact unorderedPacketBlocks_constant n (by omega) _

/-- `e_n`: the inhabited one-block partition fiber's minimum raw cost. -/
noncomputable def singleBlockPartitionDistance (n : Nat) (hn : 1 < n) : Nat :=
  partitionDistance n hn {Finset.univ} (singleBlockPartition_attainable n hn)

/-- Every full-packet literal target projects to the same partition cost.
This equality uses only the observer, independently of the cost lower bound. -/
theorem fullPacket_partitionDistance_eq_singleBlock
    (n : Nat) (hn : 1 < n) (coord : Bool × Fin n)
    (attain : ∃ word, RealizesUnorderedPartition n hn
      (unorderedPacketBlocks n (fun _ => coord)) word) :
    partitionDistance n hn (unorderedPacketBlocks n (fun _ => coord)) attain =
      singleBlockPartitionDistance n hn := by
  have hblocks := unorderedPacketBlocks_constant n (by omega) coord
  unfold singleBlockPartitionDistance
  have hcongr : ∀ (π π' : Finset (Finset (Fin n))) (h : π = π')
      (a : ∃ w, RealizesUnorderedPartition n hn π w)
      (b : ∃ w, RealizesUnorderedPartition n hn π' w),
      partitionDistance n hn π a = partitionDistance n hn π' b := by
    intro π π' h a b
    cases h
    rfl
  exact hcongr _ _ hblocks attain _

/-- Exact minimum for the one-block partition, over all guarded executions. -/
theorem singleBlock_partitionDistance_exact
    (n : Nat) (hn : 1 < n)
    (attain : ∃ word, RealizesUnorderedPartition n (by omega) {Finset.univ} word) :
    partitionDistance n (by omega) {Finset.univ} attain = 2 * n - 3 := by
  have hupper : partitionDistance n (by omega) {Finset.univ} attain ≤ 2 * n - 3 := by
    have h := fullPacket_partitionDistance_le n (by omega)
      (false, site0 n (by omega))
      (by simpa [unorderedPacketBlocks_constant n (by omega)] using attain)
    simpa [unorderedPacketBlocks_constant n (by omega)] using h
  obtain ⟨word, ⟨Q, hrun, hblocks⟩, hlen⟩ := partitionDistance_attained n (by omega)
    {Finset.univ} attain
  have hlower := singleBlock_word_length_lower_bound n hn Q word hrun hblocks
  omega

theorem singleBlockPartitionDistance_exact (n : Nat) (hn : 1 < n) :
    singleBlockPartitionDistance n (by omega) = 2 * n - 3 :=
  singleBlock_partitionDistance_exact n hn _

end RSR2History
