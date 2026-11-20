import RSR2History.DelayedFamilyPremium

/-!
Partition-relative history compression and signed partition slacks.

The equivalences below reformulate a proposed relative budget in terms of
the same actual guarded words and the existing inhabited minimum costs. They
do not establish the open global delayed-family upper bound or extract an
executable compression algorithm.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- Preserve the complete effective log and literal endpoint, with raw length
bounded by both the input length and the partition optimum plus `budget`.
Every minimum appearing here has the supplied actual realization witness. -/
def PartitionRelativeHistoryCompression (n : Nat) (hn : 1 < n)
    (budget : Nat) : Prop :=
  ∀ (word : List Letter) (Q : Placement n) (H : List (EffectiveEvent n))
    (hrun : runLogged n hn (seed n) word = some (Q, H)),
    ∃ compressed : List Letter,
      runLogged n hn (seed n) compressed = some (Q, H) ∧
      compressed.length ≤ min word.length
        (partitionDistance n hn (unorderedPacketBlocks n Q)
          (partition_attainable_of_endpoint n hn Q
            (endpoint_attainable_of_logged hn ⟨word, hrun⟩)) + budget)

/-- The same compression question restricted to one attainable partition.
No choice of literal endpoint or effective history inside the fiber is fixed. -/
def PartitionRelativeHistoryCompressionAt (n : Nat) (hn : 1 < n)
    (π : AttainablePartition n hn) (budget : Nat) : Prop :=
  ∀ (word : List Letter) (Q : Placement n) (H : List (EffectiveEvent n)),
    runLogged n hn (seed n) word = some (Q, H) →
    unorderedPacketBlocks n Q = π.val →
    ∃ compressed : List Letter,
      runLogged n hn (seed n) compressed = some (Q, H) ∧
      compressed.length ≤ min word.length
        (partitionDistance n hn π.val π.property + budget)

/-- For any budget, compression existence is equivalent to bounding the
maximum total premium. The forward direction uses the actual compressed
word; the reverse direction uses an attained minimum in the same fiber. -/
theorem partitionRelativeHistoryCompression_iff_global_le
    (n : Nat) (hn : 1 < n) (budget : Nat) :
    PartitionRelativeHistoryCompression n hn budget ↔
      globalTotalObservationPremium n hn ≤ budget := by
  constructor
  · intro hcompress
    apply Finset.sup_le
    intro observation _
    obtain ⟨word, hrun⟩ := observation.property
    obtain ⟨compressed, hcompressed, hbound⟩ :=
      hcompress word observation.val.1 observation.val.2 hrun
    have hmin : historyDistance n hn observation.val.1 observation.val.2
        observation.property ≤ compressed.length :=
      minimumWordLength_le _ observation.property hcompressed
    have hbudget : compressed.length ≤
        partitionDistance n hn (unorderedPacketBlocks n observation.val.1)
          (partition_attainable_of_endpoint n hn observation.val.1
            (endpoint_attainable_of_logged hn observation.property)) + budget :=
      (Nat.le_min.mp hbound).2
    unfold totalObservationPremium
    omega
  · intro hglobal word Q H hrun
    let attain : ∃ candidate, runLogged n hn (seed n) candidate = some (Q, H) :=
      ⟨word, hrun⟩
    let observation : AttainableObservation n hn := ⟨(Q, H), attain⟩
    obtain ⟨compressed, hcompressed, hlen⟩ := minimumWordLength_spec
      (fun candidate => runLogged n hn (seed n) candidate = some (Q, H)) attain
    have hmin : historyDistance n hn Q H attain ≤ word.length :=
      minimumWordLength_le _ attain hrun
    have hpremium := (totalObservationPremium_le_global n hn observation).trans hglobal
    change historyDistance n hn Q H attain -
      partitionDistance n hn (unorderedPacketBlocks n Q)
        (partition_attainable_of_endpoint n hn Q
          (endpoint_attainable_of_logged hn attain)) ≤ budget at hpremium
    change compressed.length = historyDistance n hn Q H attain at hlen
    refine ⟨compressed, hcompressed, Nat.le_min.mpr ⟨?_, ?_⟩⟩ <;> omega

/-- The fixed-partition compression existence problem is exactly the relative bound
on that partition's hardest attainable history. -/
theorem partitionRelativeHistoryCompressionAt_iff_maximum_le
    (n : Nat) (hn : 1 < n) (π : AttainablePartition n hn) (budget : Nat) :
    PartitionRelativeHistoryCompressionAt n hn π budget ↔
      partitionHistoryMaximum n hn π ≤ partitionDistance n hn π.val π.property + budget := by
  constructor
  · intro hcompress
    obtain ⟨observation, hmax⟩ := partitionHistoryMaximum_attained n hn π
    obtain ⟨word, hrun⟩ := observation.val.property
    obtain ⟨compressed, hcompressed, hbound⟩ :=
      hcompress word observation.val.val.1 observation.val.val.2 hrun observation.property
    have hmin : historyDistance n hn observation.val.val.1 observation.val.val.2
        observation.val.property ≤ compressed.length :=
      minimumWordLength_le _ observation.val.property hcompressed
    rw [hmax] at hmin
    exact hmin.trans (Nat.le_min.mp hbound).2
  · intro hmax word Q H hrun hπ
    let attain : ∃ candidate, runLogged n hn (seed n) candidate = some (Q, H) :=
      ⟨word, hrun⟩
    let observation : ObservationsAtPartition n hn π := ⟨⟨(Q, H), attain⟩, hπ⟩
    obtain ⟨compressed, hcompressed, hlen⟩ := minimumWordLength_spec
      (fun candidate => runLogged n hn (seed n) candidate = some (Q, H)) attain
    have hmin : historyDistance n hn Q H attain ≤ word.length :=
      minimumWordLength_le _ attain hrun
    have hcost : historyDistance n hn Q H attain ≤
        partitionDistance n hn π.val π.property + budget :=
      (historyDistance_le_partitionHistoryMaximum n hn π observation).trans hmax
    change compressed.length = historyDistance n hn Q H attain at hlen
    refine ⟨compressed, hcompressed, Nat.le_min.mpr ⟨?_, ?_⟩⟩ <;> omega

/-- Signed remainder `budget + ell_n(pi) - Lambda_n^part(pi)`. Integer
subtraction preserves negative counterexamples rather than truncating them. -/
noncomputable def partitionRelativeSlack (n : Nat) (hn : 1 < n)
    (budget : Nat) (π : AttainablePartition n hn) : Int :=
  (budget : Int) + (partitionDistance n hn π.val π.property : Int) -
    (partitionHistoryMaximum n hn π : Int)

theorem partitionRelativeSlack_nonneg_iff
    (n : Nat) (hn : 1 < n) (budget : Nat) (π : AttainablePartition n hn) :
    0 ≤ partitionRelativeSlack n hn budget π ↔
      partitionHistoryMaximum n hn π ≤ partitionDistance n hn π.val π.property + budget := by
  unfold partitionRelativeSlack
  omega

theorem partitionRelativeSlack_neg_iff
    (n : Nat) (hn : 1 < n) (budget : Nat) (π : AttainablePartition n hn) :
    partitionRelativeSlack n hn budget π < 0 ↔
      partitionDistance n hn π.val π.property + budget < partitionHistoryMaximum n hn π := by
  unfold partitionRelativeSlack
  omega

theorem partitionRelativeHistoryCompressionAt_iff_slack_nonneg
    (n : Nat) (hn : 1 < n) (π : AttainablePartition n hn) (budget : Nat) :
    PartitionRelativeHistoryCompressionAt n hn π budget ↔
      0 ≤ partitionRelativeSlack n hn budget π := by
  rw [partitionRelativeHistoryCompressionAt_iff_maximum_le,
    partitionRelativeSlack_nonneg_iff]

/-- The global relative budget is equivalent to nonnegative signed slack in
every attainable partition fiber. -/
theorem partitionRelativeHistoryCompression_iff_slacks_nonneg
    (n : Nat) (hn : 1 < n) (budget : Nat) :
    PartitionRelativeHistoryCompression n hn budget ↔
      ∀ π : AttainablePartition n hn, 0 ≤ partitionRelativeSlack n hn budget π := by
  rw [partitionRelativeHistoryCompression_iff_global_le,
    globalTotalObservationPremium_eq_partition_sup]
  constructor
  · intro h π
    have hbound : partitionTotalPremiumMaximum n hn π ≤ budget :=
      (Finset.le_sup (Finset.mem_univ π)).trans h
    rw [partitionRelativeSlack_nonneg_iff]
    unfold partitionTotalPremiumMaximum at hbound
    omega
  · intro h
    apply Finset.sup_le
    intro π _
    have hbound := (partitionRelativeSlack_nonneg_iff n hn budget π).mp (h π)
    unfold partitionTotalPremiumMaximum
    omega

/-- A negative remainder is equivalent to a genuine global violation of
the proposed budget, since both finite maxima are attained. -/
theorem exists_negative_partitionRelativeSlack_iff_global_gt
    (n : Nat) (hn : 1 < n) (budget : Nat) :
    (∃ π : AttainablePartition n hn, partitionRelativeSlack n hn budget π < 0) ↔
      budget < globalTotalObservationPremium n hn := by
  constructor
  · rintro ⟨π, hneg⟩
    have hmax := (partitionRelativeSlack_neg_iff n hn budget π).mp hneg
    have hglobal := partitionTotalPremiumMaximum_le_global n hn π
    unfold partitionTotalPremiumMaximum at hglobal
    omega
  · intro hglobal
    obtain ⟨π, hmax⟩ := globalTotalObservationPremium_partition_attained n hn
    refine ⟨π, (partitionRelativeSlack_neg_iff n hn budget π).mpr ?_⟩
    unfold partitionTotalPremiumMaximum at hmax
    omega

/-- A single negative partition slack supplies a particular actual logged
observation whose every realization exceeds that partition-relative budget. -/
theorem negative_partitionRelativeSlack_actual_witness
    (n : Nat) (hn : 1 < n) (budget : Nat) (π : AttainablePartition n hn)
    (hneg : partitionRelativeSlack n hn budget π < 0) :
    ∃ observation : ObservationsAtPartition n hn π,
      ∀ word : List Letter,
        runLogged n hn (seed n) word = some observation.val.val →
          partitionDistance n hn π.val π.property + budget < word.length := by
  obtain ⟨observation, hmax⟩ := partitionHistoryMaximum_attained n hn π
  refine ⟨observation, ?_⟩
  intro word hrun
  have hmin : historyDistance n hn observation.val.val.1 observation.val.val.2
      observation.val.property ≤ word.length :=
    minimumWordLength_le _ observation.val.property hrun
  have hcost := (partitionRelativeSlack_neg_iff n hn budget π).mp hneg
  rw [hmax] at hmin
  omega

/-- At the delayed-family budget, compression existence is equivalent to
the open global equality. This theorem does not assume or prove that equality. -/
theorem partitionRelativeHistoryCompression_iff_global_eq_delayed
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    PartitionRelativeHistoryCompression n (by omega)
        (delayedChainTotalPremiumMaximum n hn) ↔
      globalTotalObservationPremium n (by omega) = delayedChainTotalPremiumMaximum n hn := by
  rw [partitionRelativeHistoryCompression_iff_global_le]
  constructor
  · intro h
    exact le_antisymm h (delayedChainTotalPremiumMaximum_le_global hn)
  · exact le_of_eq

theorem partitionRelativeHistoryCompression_iff_K_candidate
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    PartitionRelativeHistoryCompression n (by omega)
        ((5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) - n + 2) ↔
      globalTotalObservationPremium n (by omega) =
        (5 * n * (n - 1)) / 2 + maxLowerExtractionCost n (by omega) - n + 2 := by
  rw [← delayedChainTotalPremiumMaximum_eq n hn]
  exact partitionRelativeHistoryCompression_iff_global_eq_delayed hn

theorem global_eq_delayed_iff_partitionRelativeSlacks_nonneg
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    globalTotalObservationPremium n (by omega) = delayedChainTotalPremiumMaximum n hn ↔
      ∀ π : AttainablePartition n (by omega),
        0 ≤ partitionRelativeSlack n (by omega) (delayedChainTotalPremiumMaximum n hn) π := by
  rw [← partitionRelativeHistoryCompression_iff_global_eq_delayed hn,
    partitionRelativeHistoryCompression_iff_slacks_nonneg]

end RSR2History
