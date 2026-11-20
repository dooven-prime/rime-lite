import RSR2History.TotalObservationPremium

/-!
The delayed-chain lower bound parameterized by the auxiliary extraction
problem.  The finite maximum below ranges over the explicit permutation list
of `Fin n`; it does not assert that a particular permutation family (such as
Josephus) is extremal.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- All duplicate-free extraction orders on `Fin n`, as a finite set. -/
def extractionPermutationOrders (n : Nat) : Finset (List (Fin n)) :=
  (List.finRange n).permutations.toFinset

/-- The maximum auxiliary lower-extraction cost over all permutations. -/
noncomputable def maxLowerExtractionCost (n : Nat) (hn : 1 < n) : Nat :=
  (extractionPermutationOrders n).sup (lowerExtractionCost n hn)

theorem extractionPermutationOrders_nonempty (n : Nat) :
    (extractionPermutationOrders n).Nonempty := by
  classical
  refine ⟨List.finRange n, ?_⟩
  simp [extractionPermutationOrders]

theorem mem_extractionPermutationOrders_of_full_order
    {n : Nat} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup) :
    z ∈ extractionPermutationOrders n := by
  classical
  have hzset : z.toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  have hrange : (List.finRange n).toFinset = Finset.univ := by
    simp
  have hperm : List.Perm z (List.finRange n) := by
    exact List.perm_of_nodup_nodup_toFinset_eq hnodup
      (List.nodup_finRange n) (hzset.trans hrange.symm)
  simpa [extractionPermutationOrders] using
    (List.mem_permutations.mpr hperm)

theorem lowerExtractionCost_le_max
    {n : Nat} {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup) :
    lowerExtractionCost n hn z ≤ maxLowerExtractionCost n hn := by
  unfold maxLowerExtractionCost
  exact Finset.le_sup
    (mem_extractionPermutationOrders_of_full_order hlen hnodup)

/-- `K_n` is attained by a full duplicate-free order, with no assumed
agreement between the auxiliary minimum and an external optimizer. -/
theorem maxLowerExtractionCost_attained (n : Nat) (hn : 1 < n) :
    ∃ z : List (Fin n), z.length = n ∧ z.Nodup ∧
      lowerExtractionCost n hn z = maxLowerExtractionCost n hn := by
  classical
  obtain ⟨z, hz, hsup⟩ := Finset.exists_mem_eq_sup
    (extractionPermutationOrders n) (extractionPermutationOrders_nonempty n)
    (lowerExtractionCost n hn)
  have hp : List.Perm z (List.finRange n) := by
    apply List.perm_of_mem_permutations
    simpa [extractionPermutationOrders] using hz
  exact ⟨z, by simpa using hp.length_eq,
    hp.nodup_iff.mpr (List.nodup_finRange n), hsup.symm⟩

/-- Every full extraction order gives a total-observation lower bound.  The
partition comparison uses the lower-only one-block witness, so this theorem
does not depend on how costly the chosen order is in the Python optimizer.
-/
theorem totalObservationPremium_lower_bound_of_order
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup) :
    (5 * n * (n - 1)) / 2 + lowerExtractionCost n (by omega) z - n + 2 ≤
      totalObservationPremium n (by omega)
        ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩,
          delayedUpperChainLog z),
          delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩ := by
  let q : Fin n := ⟨n - 1, by omega⟩
  let attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint q, delayedUpperChainLog z) :=
    delayedChain_attainable hn hlen hnodup q
  let observation : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint q, delayedUpperChainLog z), attain⟩
  let partAttain := partition_attainable_of_endpoint n (by omega)
    (delayedChainEndpoint q) (endpoint_attainable_of_logged (by omega) attain)
  have hpartLe :
      partitionDistance n (by omega) (unorderedPacketBlocks n (delayedChainEndpoint q))
        partAttain ≤ 2 * n - 3 := by
    exact fullPacket_partitionDistance_le n (by omega) (true, q) partAttain
  have hhistory := delayedChain_history_distance_exact hn hlen hnodup q attain
  have hq : q.val = n - 1 := by rfl
  have hbase : n ≤ (5 * n * (n - 1)) / 2 := by
    have hpred : 2 ≤ n - 1 := by omega
    have hproduct : 2 * n ≤ 5 * n * (n - 1) := by nlinarith
    omega
  have hhistoryLower :
      ((5 * n * (n - 1)) / 2 + lowerExtractionCost n (by omega) z - n + 2)
          + (2 * n - 3) ≤
        historyDistance n (by omega) (delayedChainEndpoint q)
          (delayedUpperChainLog z) attain := by
    rw [hhistory, hq]
    omega
  have hdecomp :
      historyDistance n (by omega) (delayedChainEndpoint q)
          (delayedUpperChainLog z) attain =
        totalObservationPremium n (by omega) observation +
          partitionDistance n (by omega)
            (unorderedPacketBlocks n (delayedChainEndpoint q)) partAttain := by
    have htotal : totalObservationPremium n (by omega) observation =
        historyDistance n (by omega) (delayedChainEndpoint q)
            (delayedUpperChainLog z) attain -
          partitionDistance n (by omega)
            (unorderedPacketBlocks n (delayedChainEndpoint q)) partAttain := by
      rfl
    rw [htotal]
    have hchain := observationDistance_chain n (by omega)
      (delayedChainEndpoint q) (delayedUpperChainLog z) attain
    omega
  rw [hdecomp] at hhistoryLower
  change (5 * n * (n - 1)) / 2 + lowerExtractionCost n (by omega) z - n + 2 ≤
    totalObservationPremium n (by omega) observation
  omega

/-- The K_n-sensitive lower bound for the global total observation premium. -/
theorem globalTotalObservationPremium_lower_bound_of_max_extraction
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    (5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) - n + 2 ≤
      globalTotalObservationPremium n (by omega) := by
  obtain ⟨z, hlen, hnodup, hmax⟩ := maxLowerExtractionCost_attained n (by omega)
  let observation : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩,
      delayedUpperChainLog z),
      delayedChain_attainable hn hlen hnodup ⟨n - 1, by omega⟩⟩
  have horder := totalObservationPremium_lower_bound_of_order hn hlen hnodup
  have hglobal := totalObservationPremium_le_global n (by omega) observation
  simpa [hmax] using horder.trans hglobal

end RSR2History
