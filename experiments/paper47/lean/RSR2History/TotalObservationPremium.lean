import RSR2History.ObservationForgettingCosts
import RSR2History.JosephusDelayedChainPremium

/-! The worst total cost of forgetting both history and literal geometry.
The optimization is over actual seed-reachable joint observations. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- Total cost lost when only the unordered packet partition is observed:
`lambda_n(H,Q) - ell_n(Part(Q))`. -/
noncomputable def totalObservationPremium (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) : Nat :=
  historyDistance n hn observation.val.1 observation.val.2 observation.property -
    partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
      (partition_attainable_of_endpoint n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property))

/-- `J_n`: maximum total forgetting cost over actual joint observations. -/
noncomputable def globalTotalObservationPremium (n : Nat) (hn : 1 < n) : Nat :=
  Finset.univ.sup (totalObservationPremium n hn)

/-- The total observation premium is exactly the sum of the two premiums
from the successive forgetting maps. -/
theorem totalObservationPremium_eq_premiums (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    totalObservationPremium n hn observation =
      historyPremium n hn observation.val.1 observation.val.2 observation.property +
        (endpointDistance n hn observation.val.1
          (endpoint_attainable_of_logged hn observation.property) -
          partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
            (partition_attainable_of_endpoint n hn observation.val.1
              (endpoint_attainable_of_logged hn observation.property))) := by
  exact forgetting_cost_decomposition n hn observation.val.1 observation.val.2
    observation.property

theorem totalObservationPremium_le_global (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    totalObservationPremium n hn observation ≤ globalTotalObservationPremium n hn :=
  Finset.le_sup (Finset.mem_univ observation)

/-- The finite observation maximum is attained by an actual joint
observation; its realizing execution remains a propositional witness. -/
theorem globalTotalObservationPremium_attained (n : Nat) (hn : 1 < n) :
    ∃ observation : AttainableObservation n hn,
      totalObservationPremium n hn observation =
        globalTotalObservationPremium n hn := by
  have := attainableObservation_nonempty n hn
  obtain ⟨observation, _, h⟩ := Finset.exists_mem_eq_sup
    Finset.univ Finset.univ_nonempty (totalObservationPremium n hn)
  exact ⟨observation, h.symm⟩

/-- The quadratic history-fiber representative bound gives the global upper
bound for total observation forgetting, since partition distance is nonnegative. -/
theorem globalTotalObservationPremium_le_quadratic (n : Nat) (hn : 1 < n) :
    globalTotalObservationPremium n hn ≤ 6 * n * n - 2 * n - 1 := by
  apply Finset.sup_le
  intro observation _
  unfold totalObservationPremium
  exact (Nat.sub_le _ _).trans
    (historyDistance_le_quadratic n hn observation.val.1 observation.val.2
      observation.property)

theorem unorderedPacketBlocks_constant (n : Nat) (hn : 0 < n)
    (coord : Bool × Fin n) :
    unorderedPacketBlocks n (fun _ => coord) = {Finset.univ} := by
  classical
  unfold unorderedPacketBlocks
  ext B
  simp only [Finset.mem_image, Finset.mem_univ, true_and, Finset.mem_singleton]
  constructor
  · rintro ⟨a, rfl⟩
    ext b
    simp
  · intro h
    subst B
    exact ⟨⟨0, hn⟩, by
      ext b
      simp⟩

/-- A single full packet, with its layer and site forgotten, has a
lower-only witness of length `2*n-3`. The supplied attainment proof is
irrelevant to the bound. -/
theorem fullPacket_partitionDistance_le (n : Nat) (hn : 1 < n)
    (coord : Bool × Fin n)
    (attain : ∃ word, RealizesUnorderedPartition n hn
      (unorderedPacketBlocks n (fun _ => coord)) word) :
    partitionDistance n hn (unorderedPacketBlocks n (fun _ => coord)) attain ≤
      2 * n - 3 := by
  let lowerBlock : Placement n := fun _ => (false, site0 n (by omega))
  have hprefix : run n hn (seed n) (lowerCoalescencePrefix (n - 2)) =
      some lowerBlock := by
    rw [lowerCoalescencePrefix_run n hn (n - 2)]
    rw [lowerCoalescenceStage_terminal n hn]
  have hprefixLen : (lowerCoalescencePrefix (n - 2)).length = 2 * n - 3 := by
    have h := (lowerCoalescencePrefix_counts (n - 2)).2.2.2
    omega
  have hpartWitness : RealizesUnorderedPartition n hn
      (unorderedPacketBlocks n (fun _ => coord))
      (lowerCoalescencePrefix (n - 2)) := by
    refine ⟨lowerBlock, hprefix, ?_⟩
    change unorderedPacketBlocks n (fun _ => (false, site0 n (by omega))) = _
    rw [unorderedPacketBlocks_constant n (by omega),
      unorderedPacketBlocks_constant n (by omega)]
  have hmin := minimumWordLength_le
    (RealizesUnorderedPartition n hn (unorderedPacketBlocks n (fun _ => coord)))
    attain hpartWitness
  simpa [partitionDistance, hprefixLen] using hmin

/-- The Josephus delayed chain, at the last phase, witnesses a quadratic
lower bound for the total cost of forgetting both its log and endpoint.
The partition comparison uses a lower-only one-block word of length `2*n-3`. -/
theorem josephus_totalObservationPremium_lower_bound
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    (n - 1) * (3 * n - 1) + 1 ≤
      totalObservationPremium n (by omega)
        ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩,
          delayedUpperChainLog (josephusExtractionOrder n)),
          delayedChain_attainable hn (josephusExtractionOrder_length n)
            (josephusExtractionOrder_nodup n) ⟨n - 1, by omega⟩⟩ := by
  let q : Fin n := ⟨n - 1, by omega⟩
  let z := josephusExtractionOrder n
  let attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint q, delayedUpperChainLog z) :=
    delayedChain_attainable hn (josephusExtractionOrder_length n)
      (josephusExtractionOrder_nodup n) q
  let observation : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint q, delayedUpperChainLog z), attain⟩
  let partAttain := partition_attainable_of_endpoint n (by omega)
    (delayedChainEndpoint q) (endpoint_attainable_of_logged (by omega) attain)
  have hpartLe :
      partitionDistance n (by omega) (unorderedPacketBlocks n (delayedChainEndpoint q))
        partAttain ≤ 2 * n - 3 := by
    exact fullPacket_partitionDistance_le n (by omega) (true, q) partAttain
  have hhistory := delayedChain_history_distance_exact hn
    (josephusExtractionOrder_length n) (josephusExtractionOrder_nodup n) q attain
  have hextraction := josephusExtractionCost_lower_bound n (by omega)
  have hhalfDiv : 2 ∣ 5 * n * (n - 1) := by
    rw [show 5 * n * (n - 1) = 5 * (n * (n - 1)) by ring]
    exact dvd_mul_of_dvd_right n.even_mul_pred_self.two_dvd 5
  have hhalf : 2 * (5 * n * (n - 1) / 2) = 5 * n * (n - 1) :=
    Nat.mul_div_cancel' hhalfDiv
  have hndiv : 2 ∣ n * (n - 1) := n.even_mul_pred_self.two_dvd
  have hhalf_eq : 5 * (n * (n - 1) / 2) = 5 * n * (n - 1) / 2 := by
    calc
      5 * (n * (n - 1) / 2) = 5 * (n * (n - 1)) / 2 :=
        (Nat.mul_div_assoc 5 hndiv).symm
      _ = 5 * n * (n - 1) / 2 := by rw [Nat.mul_assoc]
  have hq : q.val = n - 1 := by rfl
  have hnhalf : 2 * (n * (n - 1) / 2) = n * (n - 1) :=
    Nat.mul_div_cancel' hndiv
  have hkappa : n * (n - 1) / 2 ≤
      lowerExtractionCost n (by omega) (josephusExtractionOrder n) := by
    omega
  have htarget :
      ((n - 1) * (3 * n - 1) + 1) + (2 * n - 3) =
        3 * (n * (n - 1)) + (n - 1) := by
    have htarget_old :
        (n - 1) * (3 * n - 1) + (2 * n - 2) =
          3 * (n * (n - 1)) + (n - 1) := by
      let r := n - 1
      have hn_r : n = r + 1 := by
        dsimp [r]
        omega
      have h1 : r + 1 - 1 = r := by omega
      have h2 : 3 * (r + 1) - 1 = 3 * r + 2 := by omega
      have h3 : 2 * (r + 1) - 2 = 2 * r := by omega
      rw [hn_r, h1, h2, h3]
      ring
    omega
  have hhistoryLower :
      ((n - 1) * (3 * n - 1) + 1) + (2 * n - 3) ≤
        historyDistance n (by omega) (delayedChainEndpoint q)
          (delayedUpperChainLog z) attain := by
    rw [hhistory, hq, htarget]
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
  have hresult :
      (n - 1) * (3 * n - 1) + 1 ≤
        totalObservationPremium n (by omega) observation := by
    rw [hdecomp] at hhistoryLower
    omega
  simpa [observation, attain, z, q] using hresult

/-- The total forgetting cost has a certified quadratic lower and upper
bound for every `n >= 3`. This states the order `J_n = Theta(n^2)` without
claiming an optimal leading constant or a Pareto-frontier classification. -/
theorem global_total_observation_premium_bounds (n : Nat) (hn : 3 ≤ n) :
    (n - 1) * (3 * n - 1) + 1 ≤ globalTotalObservationPremium n (by omega) ∧
      globalTotalObservationPremium n (by omega) ≤ 6 * n * n - 2 * n - 1 := by
  have : NeZero n := ⟨by omega⟩
  have hobs := josephus_totalObservationPremium_lower_bound hn
  let observation : AttainableObservation n (by omega) :=
    ⟨(delayedChainEndpoint ⟨n - 1, by omega⟩,
      delayedUpperChainLog (josephusExtractionOrder n)),
      delayedChain_attainable hn (josephusExtractionOrder_length n)
        (josephusExtractionOrder_nodup n) ⟨n - 1, by omega⟩⟩
  have hglobal := totalObservationPremium_le_global n (by omega) observation
  exact ⟨hobs.trans hglobal,
    globalTotalObservationPremium_le_quadratic n (by omega)⟩

end RSR2History
