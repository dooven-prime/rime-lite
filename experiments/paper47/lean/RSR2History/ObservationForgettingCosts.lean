import RSR2History.HistoryPremiumExtrema

/-!
# Observation forgetting and exact cost decomposition (seed-based RSR-2)

The three observations of one successful actual guarded word are:
  (effective log, literal placement) -> literal placement -> unordered packet blocks.
No fresh execution semantics are postulated.

The infima below are of nonempty, attained sets of natural-number costs.
The existing quadratic history bound can additionally turn each into a bounded
finite search; no executable BFS refinement is claimed here.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- The unordered atom blocks of a placement, forgetting layer, site and
the choice of a representative atom for each packet. -/
noncomputable def unorderedPacketBlocks (n : Nat) (Q : Placement n) :
    Finset (Finset (Fin n)) := by
  classical
  exact Finset.univ.image
    (fun a : Fin n => Finset.univ.filter (fun b : Fin n => Q b = Q a))

/-- A partition observation of the actual guarded endpoint. -/
def RealizesUnorderedPartition (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n))) (word : List Letter) : Prop :=
  ∃ Q : Placement n, run n hn (seed n) word = some Q ∧
    unorderedPacketBlocks n Q = π

/-- Minimum raw length, defined only for an inhabited partition fiber. -/
noncomputable def partitionDistance (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word) : Nat :=
  minimumWordLength (RealizesUnorderedPartition n hn π) attain

/-- The partition minimum is attained by a successful actual word. -/
theorem partitionDistance_attained (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word) :
    ∃ word, RealizesUnorderedPartition n hn π word ∧
      word.length = partitionDistance n hn π attain :=
  minimumWordLength_spec (RealizesUnorderedPartition n hn π) attain

theorem partition_attainable_of_endpoint (n : Nat) (hn : 1 < n)
    (Q : Placement n)
    (attain : ∃ word, run n hn (seed n) word = some Q) :
    ∃ word, RealizesUnorderedPartition n hn (unorderedPacketBlocks n Q) word := by
  obtain ⟨word, hword⟩ := attain
  exact ⟨word, Q, hword, rfl⟩

theorem partitionDistance_le_endpointDistance (n : Nat) (hn : 1 < n)
    (Q : Placement n)
    (attain : ∃ word, run n hn (seed n) word = some Q) :
    partitionDistance n hn (unorderedPacketBlocks n Q)
      (partition_attainable_of_endpoint n hn Q attain) ≤
      endpointDistance n hn Q attain := by
  obtain ⟨word, hrun, hlen⟩ := minimumWordLength_spec
    (fun word => run n hn (seed n) word = some Q) attain
  have hpart : RealizesUnorderedPartition n hn
      (unorderedPacketBlocks n Q) word := ⟨Q, hrun, rfl⟩
  have hmin := minimumWordLength_le
    (RealizesUnorderedPartition n hn (unorderedPacketBlocks n Q))
    (partition_attainable_of_endpoint n hn Q attain) hpart
  simpa [partitionDistance, endpointDistance, hlen] using hmin

/-- Successive forgetting gives the chain `partition ≤ endpoint ≤ history`. -/
theorem observationDistance_chain (n : Nat) (hn : 1 < n)
    (Q : Placement n) (H : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, H)) :
    partitionDistance n hn (unorderedPacketBlocks n Q)
      (partition_attainable_of_endpoint n hn Q
        (endpoint_attainable_of_logged hn attain)) ≤
      endpointDistance n hn Q (endpoint_attainable_of_logged hn attain) ∧
    endpointDistance n hn Q (endpoint_attainable_of_logged hn attain) ≤
      historyDistance n hn Q H attain := by
  exact ⟨partitionDistance_le_endpointDistance n hn Q
    (endpoint_attainable_of_logged hn attain),
    endpointDistance_le_historyDistance n hn Q H attain⟩

/-- Neither natural subtraction truncates an unknown negative quantity:
the distance chain gives exact nonnegative history and literal premiums. -/
theorem forgetting_cost_decomposition (n : Nat) (hn : 1 < n)
    (Q : Placement n) (H : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, H)) :
    historyDistance n hn Q H attain -
      partitionDistance n hn (unorderedPacketBlocks n Q)
        (partition_attainable_of_endpoint n hn Q
          (endpoint_attainable_of_logged hn attain)) =
    historyPremium n hn Q H attain +
      (endpointDistance n hn Q (endpoint_attainable_of_logged hn attain) -
        partitionDistance n hn (unorderedPacketBlocks n Q)
          (partition_attainable_of_endpoint n hn Q
            (endpoint_attainable_of_logged hn attain))) := by
  obtain ⟨hpart, hhist⟩ := observationDistance_chain n hn Q H attain
  unfold historyPremium
  omega

/-- History-fiber minimum costs above one literal endpoint. -/
def historyCostSpectrumAt (n : Nat) (hn : 1 < n) (Q : Placement n) : Set Nat :=
  { k | ∃ (H : List (EffectiveEvent n))
      (attain : ∃ word, runLogged n hn (seed n) word = some (Q, H)),
      k = historyDistance n hn Q H attain }

/-- Forgetting the log takes the exact minimum over compatible histories. -/
theorem endpointDistance_eq_min_historyCost (n : Nat) (hn : 1 < n)
    (Q : Placement n)
    (attain : ∃ word, run n hn (seed n) word = some Q) :
    endpointDistance n hn Q attain = sInf (historyCostSpectrumAt n hn Q) := by
  obtain ⟨word, hrun, hlen⟩ := minimumWordLength_spec
    (fun word => run n hn (seed n) word = some Q) attain
  obtain ⟨H, hlog⟩ := runLogged_exists_of_run n hn hrun
  let hobs : ∃ w, runLogged n hn (seed n) w = some (Q, H) := ⟨word, hlog⟩
  have hhist_le : historyDistance n hn Q H hobs ≤ endpointDistance n hn Q attain := by
    have h := minimumWordLength_le
      (fun w => runLogged n hn (seed n) w = some (Q, H)) hobs hlog
    simpa [historyDistance, endpointDistance, hlen] using h
  have hend_le := endpointDistance_le_historyDistance n hn Q H hobs
  have hcost_eq : historyDistance n hn Q H hobs = endpointDistance n hn Q attain :=
    Nat.le_antisymm hhist_le hend_le
  have hmember : endpointDistance n hn Q attain ∈ historyCostSpectrumAt n hn Q :=
    ⟨H, hobs, hcost_eq.symm⟩
  have hnonempty : ∃ k, k ∈ historyCostSpectrumAt n hn Q := ⟨_, hmember⟩
  have hleast := Nat.sInf_mem hnonempty
  obtain ⟨H', hobs', hcost'⟩ := hleast
  have hlower := endpointDistance_le_historyDistance n hn Q H' hobs'
  have hleft : endpointDistance n hn Q attain ≤ sInf (historyCostSpectrumAt n hn Q) := by
    simpa [hcost'] using hlower
  exact Nat.le_antisymm hleft (Nat.sInf_le hmember)

/-- The minimum over histories is realized by a particular compatible log. -/
theorem endpointDistance_historyCost_attained (n : Nat) (hn : 1 < n)
    (Q : Placement n)
    (attain : ∃ word, run n hn (seed n) word = some Q) :
    ∃ (H : List (EffectiveEvent n))
      (hobs : ∃ word, runLogged n hn (seed n) word = some (Q, H)),
      historyDistance n hn Q H hobs = endpointDistance n hn Q attain := by
  have hnonempty : (historyCostSpectrumAt n hn Q).Nonempty := by
    obtain ⟨word, hrun⟩ := attain
    obtain ⟨H, hlog⟩ := runLogged_exists_of_run n hn hrun
    exact ⟨_, H, ⟨word, hlog⟩, rfl⟩
  obtain ⟨H, hobs, hcost⟩ := Nat.sInf_mem hnonempty
  exact ⟨H, hobs, hcost.symm.trans
    (endpointDistance_eq_min_historyCost n hn Q attain).symm⟩

/-- Joint-history minimum costs above a fixed partition. -/
def historyCostSpectrumOfPartition (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n))) : Set Nat :=
  { k | ∃ (Q : Placement n) (H : List (EffectiveEvent n))
      (attain : ∃ word, runLogged n hn (seed n) word = some (Q, H)),
      unorderedPacketBlocks n Q = π ∧ k = historyDistance n hn Q H attain }

/-- Forgetting both log and literal coordinates takes the exact minimum over
all compatible joint observations. -/
theorem partitionDistance_eq_min_historyCost (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word) :
    partitionDistance n hn π attain = sInf (historyCostSpectrumOfPartition n hn π) := by
  obtain ⟨word, hpart, hlen⟩ := minimumWordLength_spec
    (RealizesUnorderedPartition n hn π) attain
  obtain ⟨Q, hrun, hπ⟩ := hpart
  obtain ⟨H, hlog⟩ := runLogged_exists_of_run n hn hrun
  let hobs : ∃ w, runLogged n hn (seed n) w = some (Q, H) := ⟨word, hlog⟩
  have hhist_le : historyDistance n hn Q H hobs ≤ partitionDistance n hn π attain := by
    have h := minimumWordLength_le
      (fun w => runLogged n hn (seed n) w = some (Q, H)) hobs hlog
    simpa [historyDistance, partitionDistance, hlen] using h
  have hpart_le : partitionDistance n hn π attain ≤ historyDistance n hn Q H hobs := by
    obtain ⟨w, hw, hwlen⟩ := minimumWordLength_spec
      (fun w => runLogged n hn (seed n) w = some (Q, H)) hobs
    have hrun' : run n hn (seed n) w = some Q := by
      simpa [hw] using (runLogged_project n hn (seed n) w).symm
    have hp : RealizesUnorderedPartition n hn π w := ⟨Q, hrun', hπ⟩
    have h := minimumWordLength_le
      (RealizesUnorderedPartition n hn π) attain hp
    simpa [historyDistance, partitionDistance, hwlen] using h
  have hcost_eq : historyDistance n hn Q H hobs = partitionDistance n hn π attain :=
    Nat.le_antisymm hhist_le hpart_le
  have hmember : partitionDistance n hn π attain ∈
      historyCostSpectrumOfPartition n hn π :=
    ⟨Q, H, hobs, hπ, hcost_eq.symm⟩
  have hnonempty : ∃ k, k ∈ historyCostSpectrumOfPartition n hn π := ⟨_, hmember⟩
  have hleast := Nat.sInf_mem hnonempty
  obtain ⟨Q', H', hobs', hπ', hcost'⟩ := hleast
  obtain ⟨w, hw, hwlen⟩ := minimumWordLength_spec
    (fun w => runLogged n hn (seed n) w = some (Q', H')) hobs'
  have hrun' : run n hn (seed n) w = some Q' := by
    simpa [hw] using (runLogged_project n hn (seed n) w).symm
  have hp : RealizesUnorderedPartition n hn π w := ⟨Q', hrun', hπ'⟩
  have h := minimumWordLength_le (RealizesUnorderedPartition n hn π) attain hp
  have hleft : partitionDistance n hn π attain ≤
      sInf (historyCostSpectrumOfPartition n hn π) := by
    simpa [historyDistance, partitionDistance, hwlen, hcost'] using h
  exact Nat.le_antisymm hleft (Nat.sInf_le hmember)

/-- A compatible literal endpoint and log attain the partition minimum. -/
theorem partitionDistance_historyCost_attained (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word) :
    ∃ (Q : Placement n) (H : List (EffectiveEvent n))
      (hobs : ∃ word, runLogged n hn (seed n) word = some (Q, H)),
      unorderedPacketBlocks n Q = π ∧
        historyDistance n hn Q H hobs = partitionDistance n hn π attain := by
  have hnonempty : (historyCostSpectrumOfPartition n hn π).Nonempty := by
    obtain ⟨word, Q, hrun, hπ⟩ := attain
    obtain ⟨H, hlog⟩ := runLogged_exists_of_run n hn hrun
    exact ⟨_, Q, H, ⟨word, hlog⟩, hπ, rfl⟩
  obtain ⟨Q, H, hobs, hπ, hcost⟩ := Nat.sInf_mem hnonempty
  exact ⟨Q, H, hobs, hπ, hcost.symm.trans
    (partitionDistance_eq_min_historyCost n hn π attain).symm⟩

/-! Finiteness follows separately from the proved quadratic fiber bound;
the exact forgetting identities above require no routing construction. -/

theorem historyCostSpectrumAt_finite (n : Nat) (hn : 1 < n)
    (Q : Placement n) : (historyCostSpectrumAt n hn Q).Finite := by
  apply (Set.finite_Iic (quadraticHistoryBudget n)).subset
  rintro k ⟨H, hobs, rfl⟩
  exact historyDistance_le_quadratic n hn Q H hobs

theorem historyCostSpectrumOfPartition_finite (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n))) :
    (historyCostSpectrumOfPartition n hn π).Finite := by
  apply (Set.finite_Iic (quadraticHistoryBudget n)).subset
  rintro k ⟨Q, H, hobs, -, rfl⟩
  exact historyDistance_le_quadratic n hn Q H hobs

end RSR2History
