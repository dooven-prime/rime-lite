import RSR2History.KSensitivePremium
import RSR2History.SingleBlockPartitionCost
import RSR2History.ObservationCostExtrema

/-!
Exact total-premium maximum inside the delayed upper-chain family. The
formula retaining the partition distance is proved independently of its
exact value. This restricted maximum is not asserted to equal the global
maximum over all effective histories and literal endpoints.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- The last-phase delayed-chain score, retaining the one-block partition
minimum. For every full order, it equals the actual total premium. -/
noncomputable def delayedChainPremiumScore (n : Nat) (hn : 3 ≤ n)
    (z : List (Fin n)) : Nat :=
  ((5 * n * (n - 1)) / 2 + lowerExtractionCost n (by omega) z + (n - 1)) -
    singleBlockPartitionDistance n (by omega)

/-- `J_n^delayed`: the maximum actual last-phase delayed-chain premium,
transported by its exact distance formula to the finite full-order set. -/
noncomputable def delayedChainTotalPremiumMaximum (n : Nat) (hn : 3 ≤ n) : Nat :=
  (extractionPermutationOrders n).sup (delayedChainPremiumScore n hn)

/-- The score is the premium of the same actual logged execution contract
used for the delayed-chain distance theorem. No partition-cost lower bound
is needed for this identity. -/
theorem delayedChain_lastPhase_totalPremium_exact
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup) :
    totalObservationPremium n (by omega)
      ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩, delayedUpperChainLog z),
        delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩ =
      delayedChainPremiumScore n hn z := by
  let q : Fin n := ⟨n - 1, by omega⟩
  let attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint q, delayedUpperChainLog z) :=
    delayedChain_attainable hn hlen hnodup q
  let partAttain := partition_attainable_of_endpoint n (by omega)
    (delayedChainEndpoint q) (endpoint_attainable_of_logged (by omega) attain)
  have hhistory := delayedChain_history_distance_exact hn hlen hnodup q attain
  have hpart : partitionDistance n (by omega)
      (unorderedPacketBlocks n (delayedChainEndpoint q)) partAttain =
      singleBlockPartitionDistance n (by omega) :=
    fullPacket_partitionDistance_eq_singleBlock n (by omega) (true, q) partAttain
  change historyDistance n (by omega) (delayedChainEndpoint q)
      (delayedUpperChainLog z) attain -
      partitionDistance n (by omega)
        (unorderedPacketBlocks n (delayedChainEndpoint q)) partAttain = _
  rw [hpart, hhistory]
  simp only [delayedChainPremiumScore]
  have hphase : q.val = n - 1 := rfl
  rw [hphase]
  omega

/-- Exact restricted maximum before substituting the one-block cost. -/
theorem delayedChainTotalPremiumMaximum_eq_partitionDistance
    (n : Nat) (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn =
      ((5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) + (n - 1)) -
        singleBlockPartitionDistance n (by omega) := by
  classical
  unfold delayedChainTotalPremiumMaximum
  apply le_antisymm
  · apply Finset.sup_le
    intro z hz
    have hp : List.Perm z (List.finRange n) := by
      apply List.perm_of_mem_permutations
      simpa [extractionPermutationOrders] using hz
    have hlen : z.length = n := by simpa using hp.length_eq
    have hnodup : z.Nodup := hp.nodup_iff.mpr (List.nodup_finRange n)
    have hk := lowerExtractionCost_le_max (hn := by omega) hlen hnodup
    unfold delayedChainPremiumScore
    omega
  · obtain ⟨z, hlen, hnodup, hmax⟩ :=
      maxLowerExtractionCost_attained n (by omega)
    have hz := mem_extractionPermutationOrders_of_full_order hlen hnodup
    have hk : delayedChainPremiumScore n hn z ≤
        (extractionPermutationOrders n).sup (delayedChainPremiumScore n hn) :=
      Finset.le_sup hz
    simpa [delayedChainPremiumScore, hmax] using hk

/-- Substituting the independently proved partition minimum gives the
numerical formula. Natural subtraction does not truncate its positive base. -/
theorem delayedChainTotalPremiumMaximum_eq
    (n : Nat) (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn =
      (5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) - n + 2 := by
  rw [delayedChainTotalPremiumMaximum_eq_partitionDistance,
    singleBlockPartitionDistance_exact n (by omega)]
  have hbase : n ≤ (5 * n * (n - 1)) / 2 := by
    have hpred : 2 ≤ n - 1 := by omega
    have hmul : 2 * n ≤ 5 * n * (n - 1) := by nlinarith
    omega
  omega

/-- Every actual delayed-chain observation is bounded by this restricted
maximum; the quantification is over all full extraction orders. -/
theorem delayedChain_totalPremium_le_maximum
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup) :
    totalObservationPremium n (by omega)
      ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩, delayedUpperChainLog z),
        delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩ ≤
      delayedChainTotalPremiumMaximum n hn := by
  rw [delayedChain_lastPhase_totalPremium_exact hn hlen hnodup]
  exact Finset.le_sup (mem_extractionPermutationOrders_of_full_order hlen hnodup)

/-- A full order attaining `K_n` gives an actual observation attaining the
restricted maximum. No external enumeration or Josephus optimality is used. -/
theorem delayedChainTotalPremiumMaximum_attained
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    ∃ z : List (Fin n), ∃ hlen : z.length = n, ∃ hnodup : z.Nodup,
      totalObservationPremium n (by omega)
        ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩, delayedUpperChainLog z),
          delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩ =
        delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := maxLowerExtractionCost_attained n (by omega)
  refine ⟨z, hlen, hnodup, ?_⟩
  rw [delayedChain_lastPhase_totalPremium_exact hn hlen hnodup,
    delayedChainTotalPremiumMaximum_eq_partitionDistance]
  simp [delayedChainPremiumScore, hmax]

/-- The restricted maximum is a certified lower bound for the global
maximum. The reverse inequality remains a separate geometric problem. -/
theorem delayedChainTotalPremiumMaximum_le_global
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn ≤
      globalTotalObservationPremium n (by omega) := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := delayedChainTotalPremiumMaximum_attained hn
  rw [← hmax]
  exact totalObservationPremium_le_global n (by omega) _

/-- The still-open global reverse bound is equivalent to a uniform bound on
every actual partition fiber's cost amplitude. This follows from the already
proved finite partition-fiber decomposition of `J_n`; it makes no assumption
that a general history has a singleton-transfer order. -/
theorem globalTotalObservationPremium_le_delayed_iff_partition_fibers
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) ≤ delayedChainTotalPremiumMaximum n hn ↔
      ∀ π : AttainablePartition n (by omega),
        partitionTotalPremiumMaximum n (by omega) π ≤
          delayedChainTotalPremiumMaximum n hn := by
  rw [globalTotalObservationPremium_eq_partition_sup n (by omega)]
  constructor
  · intro h π
    exact (Finset.le_sup (Finset.mem_univ π)).trans h
  · intro h
    apply Finset.sup_le
    intro π _
    exact h π

/-- The original numeric candidate is exactly the same as the global
maximum equaling the restricted last-phase delayed maximum. -/
theorem globalTotalObservationPremium_eq_delayed_iff_partition_fibers
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) = delayedChainTotalPremiumMaximum n hn ↔
      ∀ π : AttainablePartition n (by omega),
        partitionTotalPremiumMaximum n (by omega) π ≤
          delayedChainTotalPremiumMaximum n hn := by
  constructor
  · intro h
    exact (globalTotalObservationPremium_le_delayed_iff_partition_fibers hn).mp
      (le_of_eq h)
  · intro h
    apply le_antisymm
    · exact (globalTotalObservationPremium_le_delayed_iff_partition_fibers hn).mpr h
    · exact delayedChainTotalPremiumMaximum_le_global hn

/-- The `K_n` numerical candidate is equivalent to the uniform partition-fiber
amplitude bound. This does not presume the candidate is true. -/
theorem globalTotalObservationPremium_eq_K_candidate_iff
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) =
        (5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) - n + 2 ↔
      ∀ π : AttainablePartition n (by omega),
        partitionTotalPremiumMaximum n (by omega) π ≤
          delayedChainTotalPremiumMaximum n hn := by
  rw [← delayedChainTotalPremiumMaximum_eq n hn]
  exact globalTotalObservationPremium_eq_delayed_iff_partition_fibers hn

end RSR2History
