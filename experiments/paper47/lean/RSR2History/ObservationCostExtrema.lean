import RSR2History.TotalObservationPremium
import RSR2History.HistoryCostExtrema
import RSR2History.ObservationPartitionBridge

/-! Finite extrema and equality conditions for the two observation premiums.
All maxima range over actual seed-reachable fibers. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

private theorem partitionDistance_proof_irrel (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain₁ attain₂ : ∃ word, RealizesUnorderedPartition n hn π word) :
    partitionDistance n hn π attain₁ = partitionDistance n hn π attain₂ := by
  have hproof : attain₁ = attain₂ := Subsingleton.elim _ _
  rw [hproof]

private theorem partitionDistance_congr (n : Nat) (hn : 1 < n)
    {π π' : Finset (Finset (Fin n))} (hπ : π = π')
    (attain : ∃ word, RealizesUnorderedPartition n hn π word)
    (attain' : ∃ word, RealizesUnorderedPartition n hn π' word) :
    partitionDistance n hn π attain = partitionDistance n hn π' attain' := by
  cases hπ
  exact partitionDistance_proof_irrel n hn π attain attain'

theorem attainableEndpoint_nonempty (n : Nat) (hn : 1 < n) :
    Nonempty (AttainableEndpoint n hn) :=
  ⟨⟨seed n, ⟨[], rfl⟩⟩⟩

/-- The literal-placement cost premium at a reachable endpoint, after
forgetting to its unordered packet partition. -/
noncomputable def endpointLiteralPremium (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) : Nat :=
  endpointDistance n hn Q.1 Q.2 -
    partitionDistance n hn (unorderedPacketBlocks n Q.1)
      (partition_attainable_of_endpoint n hn Q.1 Q.2)

/-- `A_n`: maximum literal-placement premium over reachable endpoints. -/
noncomputable def globalLiteralPremium (n : Nat) (hn : 1 < n) : Nat :=
  Finset.univ.sup (endpointLiteralPremium n hn)

theorem endpointLiteralPremium_le_global (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointLiteralPremium n hn Q ≤ globalLiteralPremium n hn :=
  Finset.le_sup (Finset.mem_univ Q)

theorem globalLiteralPremium_attained (n : Nat) (hn : 1 < n) :
    ∃ Q : AttainableEndpoint n hn,
      endpointLiteralPremium n hn Q = globalLiteralPremium n hn := by
  have := attainableEndpoint_nonempty n hn
  obtain ⟨Q, _, h⟩ := Finset.exists_mem_eq_sup
    Finset.univ Finset.univ_nonempty (endpointLiteralPremium n hn)
  exact ⟨Q, h.symm⟩

private theorem singleVacancy_partition_eq_seed (n : Nat) (hn : 3 ≤ n) :
    unorderedPacketBlocks n (singleVacancyEndpoint n (by omega)) =
      unorderedPacketBlocks n (seed n) := by
  apply (unorderedPacketBlocks_eq_iff_samePacket n _ _).2
  intro a b
  constructor
  · intro hab
    have hab' : a = b := (singleVacancyEndpoint_terminal n (by omega)).injective hab
    subst b
    rfl
  · intro hab
    change (false, a) = (false, b) at hab
    have hab' : a = b := by simpa using hab
    subst b
    rfl

private theorem seed_partitionDistance_zero (n : Nat) (hn : 1 < n) :
    partitionDistance n hn (unorderedPacketBlocks n (seed n))
      (⟨[], seed n, rfl, rfl⟩ :
        ∃ word, RealizesUnorderedPartition n hn
          (unorderedPacketBlocks n (seed n)) word) = 0 := by
  unfold partitionDistance
  apply minimumWordLength_eq
  · exact ⟨[], ⟨seed n, rfl, rfl⟩, rfl⟩
  · intro word _
    simp

/-- The single-vacancy literal endpoint still observes the seed's singleton
partition, so its entire quadratic endpoint cost is a literal-placement
premium. -/
theorem singleVacancyPartition_cost_witness (n : Nat) (hn : 3 ≤ n) :
    n * (n - 1) ≤ globalLiteralPremium n (by omega) := by
  let endpoint : AttainableEndpoint n (by omega) :=
    ⟨singleVacancyEndpoint n (by omega),
      ⟨singleVacancyWord n, singleVacancyWord_run n hn⟩⟩
  have hblocks := singleVacancy_partition_eq_seed n hn
  have hseed : ∃ word, RealizesUnorderedPartition n (by omega)
      (unorderedPacketBlocks n (seed n)) word :=
    ⟨[], ⟨seed n, rfl, rfl⟩⟩
  have hpart : partitionDistance n (by omega)
      (unorderedPacketBlocks n endpoint.1)
      (partition_attainable_of_endpoint n (by omega) endpoint.1 endpoint.2) = 0 := by
    calc
      _ = partitionDistance n (by omega) (unorderedPacketBlocks n (seed n)) hseed :=
        partitionDistance_congr n (by omega) hblocks
          (partition_attainable_of_endpoint n (by omega) endpoint.1 endpoint.2) hseed
      _ = 0 := seed_partitionDistance_zero n (by omega)
  obtain ⟨word, hrun, hlen⟩ := minimumWordLength_spec
    (fun word => run n (by omega) (seed n) word = some endpoint.1) endpoint.2
  have hendpoint := singleVacancyEndpoint_length_lower_bound n hn word hrun
  have hdistance : n * (n - 1) ≤ endpointDistance n (by omega) endpoint.1 endpoint.2 := by
    simpa [endpointDistance, hlen] using hendpoint
  have hpremium : n * (n - 1) ≤ endpointLiteralPremium n (by omega) endpoint := by
    rw [endpointLiteralPremium, hpart]
    simpa using hdistance
  exact hpremium.trans (endpointLiteralPremium_le_global n (by omega) endpoint)

/-- The endpoint component in the exact decomposition agrees with the
endpoint-only premium at the same actual placement. -/
theorem observation_literalPremium_eq_endpoint (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    endpointDistance n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property) -
      partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
        (partition_attainable_of_endpoint n hn observation.val.1
          (endpoint_attainable_of_logged hn observation.property)) =
      endpointLiteralPremium n hn
        ⟨observation.val.1, endpoint_attainable_of_logged hn observation.property⟩ := by
  rfl

theorem observation_historyPremium_le_global (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    historyPremium n hn observation.val.1 observation.val.2 observation.property ≤
      globalHistoryPremium n hn :=
  historyPremium_le_global n hn observation.val.1 observation.val.2 observation.property

theorem observation_literalPremium_le_global (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    endpointDistance n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property) -
      partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
        (partition_attainable_of_endpoint n hn observation.val.1
          (endpoint_attainable_of_logged hn observation.property)) ≤
      globalLiteralPremium n hn := by
  rw [observation_literalPremium_eq_endpoint]
  exact endpointLiteralPremium_le_global n hn
    ⟨observation.val.1, endpoint_attainable_of_logged hn observation.property⟩

theorem totalObservationPremium_le_sum_of_global (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    totalObservationPremium n hn observation ≤
      globalHistoryPremium n hn + globalLiteralPremium n hn := by
  rw [totalObservationPremium_eq_premiums]
  exact Nat.add_le_add
    (observation_historyPremium_le_global n hn observation)
    (observation_literalPremium_le_global n hn observation)

theorem globalTotalObservationPremium_le_sum (n : Nat) (hn : 1 < n) :
    globalTotalObservationPremium n hn ≤
      globalHistoryPremium n hn + globalLiteralPremium n hn := by
  apply Finset.sup_le
  intro observation _
  exact totalObservationPremium_le_sum_of_global n hn observation

theorem historyPremium_le_totalObservationPremium (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    historyPremium n hn observation.val.1 observation.val.2 observation.property ≤
      totalObservationPremium n hn observation := by
  rw [totalObservationPremium_eq_premiums]
  have hnonneg := (observationDistance_chain n hn observation.val.1
    observation.val.2 observation.property).1
  omega

theorem endpointLiteralPremium_le_totalObservationPremium
    (n : Nat) (hn : 1 < n) (observation : AttainableObservation n hn) :
    endpointDistance n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property) -
      partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
        (partition_attainable_of_endpoint n hn observation.val.1
          (endpoint_attainable_of_logged hn observation.property)) ≤
      totalObservationPremium n hn observation := by
  rw [totalObservationPremium_eq_premiums]
  have hnonneg := historyPremium_balance n hn observation.val.1
    observation.val.2 observation.property
  omega

theorem globalHistoryPremium_le_globalTotalObservationPremium
    (n : Nat) (hn : 1 < n) :
    globalHistoryPremium n hn ≤ globalTotalObservationPremium n hn := by
  obtain ⟨Q, events, attain, hmax⟩ := globalHistoryPremium_realized n hn
  let observation : AttainableObservation n hn := ⟨(Q, events), attain⟩
  have hle := historyPremium_le_totalObservationPremium n hn observation
  have htotal := totalObservationPremium_le_global n hn observation
  rw [hmax] at hle
  exact hle.trans htotal

theorem globalLiteralPremium_le_globalTotalObservationPremium
    (n : Nat) (hn : 1 < n) :
    globalLiteralPremium n hn ≤ globalTotalObservationPremium n hn := by
  obtain ⟨Q, hmax⟩ := globalLiteralPremium_attained n hn
  obtain ⟨events, attain, _⟩ := endpointDistance_historyCost_attained
    n hn Q.1 Q.2
  let observation : AttainableObservation n hn := ⟨(Q.1, events), attain⟩
  have hle := endpointLiteralPremium_le_totalObservationPremium n hn observation
  have htotal := totalObservationPremium_le_global n hn observation
  have hcomponent :
      endpointDistance n hn Q.1 Q.2 -
        partitionDistance n hn (unorderedPacketBlocks n Q.1)
          (partition_attainable_of_endpoint n hn Q.1 Q.2) =
        endpointLiteralPremium n hn Q := by
    rfl
  rw [hcomponent, hmax] at hle
  exact hle.trans htotal

/-- The maximum literal-placement premium has quadratic order, witnessed by
the single-vacancy endpoint and bounded by the complete-history compressor. -/
theorem global_literal_observation_premium_bounds (n : Nat) (hn : 3 ≤ n) :
    n * (n - 1) ≤ globalLiteralPremium n (by omega) ∧
      globalLiteralPremium n (by omega) ≤ 6 * n * n - 2 * n - 1 := by
  refine ⟨singleVacancyPartition_cost_witness n hn, ?_⟩
  exact (globalLiteralPremium_le_globalTotalObservationPremium n (by omega)).trans
    (globalTotalObservationPremium_le_quadratic n (by omega))

theorem globalObservationPremium_max_bounds (n : Nat) (hn : 1 < n) :
    max (globalHistoryPremium n hn) (globalLiteralPremium n hn) ≤
      globalTotalObservationPremium n hn ∧
    globalTotalObservationPremium n hn ≤
      globalHistoryPremium n hn + globalLiteralPremium n hn := by
  constructor
  · exact max_le
      (globalHistoryPremium_le_globalTotalObservationPremium n hn)
      (globalLiteralPremium_le_globalTotalObservationPremium n hn)
  · exact globalTotalObservationPremium_le_sum n hn

theorem globalTotalObservationPremium_eq_sum_iff (n : Nat) (hn : 1 < n) :
    globalTotalObservationPremium n hn =
        globalHistoryPremium n hn + globalLiteralPremium n hn ↔
      ∃ observation : AttainableObservation n hn,
        historyPremium n hn observation.val.1 observation.val.2 observation.property =
          globalHistoryPremium n hn ∧
        endpointDistance n hn observation.val.1
            (endpoint_attainable_of_logged hn observation.property) -
          partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
            (partition_attainable_of_endpoint n hn observation.val.1
              (endpoint_attainable_of_logged hn observation.property)) =
          globalLiteralPremium n hn := by
  constructor
  · intro hsum
    obtain ⟨observation, htotal⟩ := globalTotalObservationPremium_attained n hn
    have hdecomp := totalObservationPremium_eq_premiums n hn observation
    have hhist := observation_historyPremium_le_global n hn observation
    have hlit := observation_literalPremium_le_global n hn observation
    have htotalGlobal : totalObservationPremium n hn observation =
        globalHistoryPremium n hn + globalLiteralPremium n hn := by
      rw [← hsum]
      exact htotal
    refine ⟨observation, ?_, ?_⟩
    · rw [hdecomp] at htotalGlobal
      omega
    · rw [hdecomp] at htotalGlobal
      omega
  · rintro ⟨observation, hhist, hlit⟩
    have hdecomp := totalObservationPremium_eq_premiums n hn observation
    have htotal : totalObservationPremium n hn observation =
        globalHistoryPremium n hn + globalLiteralPremium n hn := by
      rw [hdecomp, hhist, hlit]
    apply Nat.le_antisymm
    · exact globalTotalObservationPremium_le_sum n hn
    · exact htotal ▸ totalObservationPremium_le_global n hn observation

/-- The finite family of actually reachable unordered packet partitions. -/
def attainablePartitions (n : Nat) (hn : 1 < n) :
    Set (Finset (Finset (Fin n))) :=
  {π | ∃ word, RealizesUnorderedPartition n hn π word}

abbrev AttainablePartition (n : Nat) (hn : 1 < n) :=
  {π : Finset (Finset (Fin n)) // π ∈ attainablePartitions n hn}

theorem attainablePartitions_finite (n : Nat) (hn : 1 < n) :
    (attainablePartitions n hn).Finite := Set.toFinite _

noncomputable instance attainablePartitionFintype (n : Nat) (hn : 1 < n) :
    Fintype (AttainablePartition n hn) :=
  (attainablePartitions_finite n hn).fintype

theorem attainablePartition_nonempty (n : Nat) (hn : 1 < n) :
    Nonempty (AttainablePartition n hn) := by
  refine ⟨⟨unorderedPacketBlocks n (seed n), ?_⟩⟩
  exact ⟨[], seed n, rfl, rfl⟩

abbrev ObservationsAtPartition (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) :=
  {observation : AttainableObservation n hn //
    unorderedPacketBlocks n observation.val.1 = π.1}

theorem observationsAtPartition_nonempty (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) : Nonempty (ObservationsAtPartition n hn π) := by
  obtain ⟨word, Q, hrun, hblocks⟩ := π.2
  obtain ⟨events, hlog⟩ := runLogged_exists_of_run n hn hrun
  refine ⟨⟨⟨(Q, events), ⟨word, hlog⟩⟩, ?_⟩⟩
  exact hblocks

/-- `Lambda_n^part(pi)`: maximum history-preserving distance among all
actual joint observations whose endpoint has partition `pi`. -/
noncomputable def partitionHistoryMaximum (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) : Nat :=
  Finset.univ.sup (fun observation : ObservationsAtPartition n hn π =>
    historyDistance n hn observation.1.val.1 observation.1.val.2 observation.1.property)

theorem historyDistance_le_partitionHistoryMaximum (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) (observation : ObservationsAtPartition n hn π) :
    historyDistance n hn observation.1.val.1 observation.1.val.2 observation.1.property ≤
      partitionHistoryMaximum n hn π := by
  unfold partitionHistoryMaximum
  exact Finset.le_sup (α := Nat)
    (f := fun observation : ObservationsAtPartition n hn π =>
      historyDistance n hn observation.1.val.1 observation.1.val.2 observation.1.property)
    (Finset.mem_univ observation)

theorem partitionHistoryMaximum_attained (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) :
    ∃ observation : ObservationsAtPartition n hn π,
      historyDistance n hn observation.1.val.1 observation.1.val.2 observation.1.property =
        partitionHistoryMaximum n hn π := by
  have := observationsAtPartition_nonempty n hn π
  obtain ⟨observation, _, h⟩ := Finset.exists_mem_eq_sup
    Finset.univ Finset.univ_nonempty
    (fun observation : ObservationsAtPartition n hn π =>
      historyDistance n hn observation.1.val.1 observation.1.val.2 observation.1.property)
  exact ⟨observation, h.symm⟩

noncomputable def partitionTotalPremiumMaximum (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) : Nat :=
  partitionHistoryMaximum n hn π -
    partitionDistance n hn π.1 π.2

/-- A literal-endpoint fiber's cost amplitude is its largest history cost
minus its smallest history cost. The latter is the endpoint-only distance. -/
theorem endpointPremiumMaximum_eq_cost_amplitude (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointPremiumMaximum n hn Q =
      endpointHistoryMaximum n hn Q - sInf (historyCostSpectrumAt n hn Q.1) := by
  unfold endpointPremiumMaximum
  rw [endpointDistance_eq_min_historyCost n hn Q.1 Q.2]

/-- A partition fiber's cost amplitude is its largest joint-history cost
minus its smallest one, which is exactly the partition-only distance. -/
theorem partitionTotalPremiumMaximum_eq_cost_amplitude (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) :
    partitionTotalPremiumMaximum n hn π =
      partitionHistoryMaximum n hn π -
        sInf (historyCostSpectrumOfPartition n hn π.1) := by
  unfold partitionTotalPremiumMaximum
  rw [partitionDistance_eq_min_historyCost n hn π.1 π.2]

theorem totalObservationPremium_le_partitionMaximum (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    totalObservationPremium n hn observation ≤
      partitionTotalPremiumMaximum n hn
        ⟨unorderedPacketBlocks n observation.val.1,
          partition_attainable_of_endpoint n hn observation.val.1
            (endpoint_attainable_of_logged hn observation.property)⟩ := by
  let π : AttainablePartition n hn :=
    ⟨unorderedPacketBlocks n observation.val.1,
      partition_attainable_of_endpoint n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property)⟩
  let fiberObservation : ObservationsAtPartition n hn π := ⟨observation, rfl⟩
  have hmax := historyDistance_le_partitionHistoryMaximum n hn π fiberObservation
  have hdist := (observationDistance_chain n hn observation.val.1
    observation.val.2 observation.property).1
  have hpart : partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
      (partition_attainable_of_endpoint n hn observation.val.1
        (endpoint_attainable_of_logged hn observation.property)) =
      partitionDistance n hn π.1 π.2 := by
    exact partitionDistance_proof_irrel n hn π.1 _ _
  have htotal : totalObservationPremium n hn observation =
      historyDistance n hn observation.val.1 observation.val.2 observation.property -
        partitionDistance n hn π.1 π.2 := by
    unfold totalObservationPremium
    rw [hpart]
  rw [htotal]
  unfold partitionTotalPremiumMaximum
  exact Nat.sub_le_sub_right hmax _

theorem partitionTotalPremiumMaximum_le_global (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) :
    partitionTotalPremiumMaximum n hn π ≤ globalTotalObservationPremium n hn := by
  obtain ⟨observation, hmax⟩ := partitionHistoryMaximum_attained n hn π
  let actual : AttainableObservation n hn := observation.1
  have hblocks : unorderedPacketBlocks n actual.val.1 = π.1 := observation.2
  have hpart := partitionDistance_congr n hn hblocks
    (partition_attainable_of_endpoint n hn actual.val.1
      (endpoint_attainable_of_logged hn actual.property)) π.2
  have htotal : totalObservationPremium n hn actual =
      partitionTotalPremiumMaximum n hn π := by
    unfold totalObservationPremium partitionTotalPremiumMaximum
    calc
      historyDistance n hn actual.val.1 actual.val.2 actual.property -
          partitionDistance n hn (unorderedPacketBlocks n actual.val.1)
            (partition_attainable_of_endpoint n hn actual.val.1
              (endpoint_attainable_of_logged hn actual.property)) =
          historyDistance n hn actual.val.1 actual.val.2 actual.property -
            partitionDistance n hn π.1 π.2 := by rw [hpart]
      _ = partitionHistoryMaximum n hn π - partitionDistance n hn π.1 π.2 := by
        rw [hmax]
  rw [← htotal]
  exact totalObservationPremium_le_global n hn actual

theorem globalTotalObservationPremium_eq_partition_sup (n : Nat) (hn : 1 < n) :
    globalTotalObservationPremium n hn =
      Finset.univ.sup (partitionTotalPremiumMaximum n hn) := by
  apply Nat.le_antisymm
  · apply Finset.sup_le
    intro observation _
    let π : AttainablePartition n hn :=
      ⟨unorderedPacketBlocks n observation.val.1,
        partition_attainable_of_endpoint n hn observation.val.1
          (endpoint_attainable_of_logged hn observation.property)⟩
    exact (totalObservationPremium_le_partitionMaximum n hn observation).trans
      (Finset.le_sup (α := Nat) (f := partitionTotalPremiumMaximum n hn)
        (Finset.mem_univ π))
  · apply Finset.sup_le
    intro π _
    exact partitionTotalPremiumMaximum_le_global n hn π

theorem globalTotalObservationPremium_partition_attained
    (n : Nat) (hn : 1 < n) :
    ∃ π : AttainablePartition n hn,
      partitionTotalPremiumMaximum n hn π = globalTotalObservationPremium n hn := by
  have := attainablePartition_nonempty n hn
  obtain ⟨π, _, h⟩ := Finset.exists_mem_eq_sup Finset.univ Finset.univ_nonempty
    (partitionTotalPremiumMaximum n hn)
  exact ⟨π, (globalTotalObservationPremium_eq_partition_sup n hn).symm ▸ h.symm⟩

/-- The global history premium is the maximum cost amplitude of a literal
endpoint fiber. -/
theorem globalHistoryPremium_eq_endpoint_fiber_amplitude_sup
    (n : Nat) (hn : 1 < n) :
    globalHistoryPremium n hn = Finset.univ.sup (endpointPremiumMaximum n hn) :=
  globalHistoryPremium_eq_endpoint_sup n hn

/-- The global total premium is the maximum cost amplitude of a reachable
unordered-partition fiber. -/
theorem globalTotalObservationPremium_eq_partition_fiber_amplitude_sup
    (n : Nat) (hn : 1 < n) :
    globalTotalObservationPremium n hn =
      Finset.univ.sup (partitionTotalPremiumMaximum n hn) :=
  globalTotalObservationPremium_eq_partition_sup n hn

end RSR2History
