import RSR2History.ObservationForgettingCosts
import RSR2.BellProjection

/-! The partition-distance branch uses finite packet blocks, while Paper XLVI
uses a Setoid. This module identifies both encodings on actual placements and
transfers their realization predicate and minimum cost. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

/-- The Paper XLVI representation of the partition induced by a placement. -/
@[instance_reducible] def placementPartitionSetoid (n : Nat) (Q : Placement n) :
    RSR2.UnorderedPartition n where
  r := fun a b => samePacket Q a b
  iseqv := ⟨by intro a; rfl,
    by intro a b h; exact h.symm,
    by intro a b c hab hbc; exact hab.trans hbc⟩

/-- Encode a Setoid partition as its finite family of equivalence classes. -/
noncomputable def setoidPacketBlocks (n : Nat)
    (π : RSR2.UnorderedPartition n) : Finset (Finset (Fin n)) := by
  classical
  exact Finset.univ.image
    (fun a : Fin n => Finset.univ.filter (fun b : Fin n => π.r b a))

/-- Two atoms share an actual packet iff they lie in one encoded block. -/
theorem samePacket_iff_common_unorderedPacketBlock (n : Nat) (Q : Placement n)
    (a b : Fin n) :
    samePacket Q a b ↔
      ∃ B ∈ unorderedPacketBlocks n Q, a ∈ B ∧ b ∈ B := by
  classical
  constructor
  · intro hab
    refine ⟨Finset.univ.filter (fun x : Fin n => Q x = Q a), ?_, ?_, ?_⟩
    · apply Finset.mem_image.mpr
      exact ⟨a, Finset.mem_univ a, rfl⟩
    · simp
    · have h : Q b = Q a := by simpa [samePacket] using hab.symm
      simp [h]
  · rintro ⟨B, hB, ha, hb⟩
    obtain ⟨c, -, rfl⟩ := Finset.mem_image.mp hB
    have ha' : Q a = Q c := (Finset.mem_filter.mp ha).2
    have hb' : Q b = Q c := (Finset.mem_filter.mp hb).2
    change Q a = Q b
    exact ha'.trans hb'.symm

/-- Setoid membership is equivalent to sharing one encoded equivalence class. -/
theorem setoid_iff_common_setoidPacketBlock (n : Nat)
    (π : RSR2.UnorderedPartition n) (a b : Fin n) :
    π.r a b ↔ ∃ B ∈ setoidPacketBlocks n π, a ∈ B ∧ b ∈ B := by
  classical
  constructor
  · intro hab
    refine ⟨Finset.univ.filter (fun x : Fin n => π.r x a), ?_, ?_, ?_⟩
    · apply Finset.mem_image.mpr
      exact ⟨a, Finset.mem_univ a, rfl⟩
    · simp
    · simp [π.iseqv.symm hab]
  · rintro ⟨B, hB, ha, hb⟩
    obtain ⟨c, -, rfl⟩ := Finset.mem_image.mp hB
    have hac : π.r a c := (Finset.mem_filter.mp ha).2
    have hbc : π.r b c := (Finset.mem_filter.mp hb).2
    exact π.iseqv.trans hac (π.iseqv.symm hbc)

/-- A placement's finite blocks are precisely the classes of its Setoid. -/
theorem unorderedPacketBlocks_eq_setoidPacketBlocks (n : Nat)
    (Q : Placement n) :
    unorderedPacketBlocks n Q =
      setoidPacketBlocks n (placementPartitionSetoid n Q) := by
  classical
  unfold unorderedPacketBlocks setoidPacketBlocks
  apply congrArg (fun f : Fin n → Finset (Fin n) => Finset.univ.image f)
  funext a
  apply Finset.ext
  intro b
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  change (Q b = Q a ↔ Q b = Q a)
  rfl

/-- Equality of finite block encodings is equivalent to equality of their
same-packet relations. -/
theorem unorderedPacketBlocks_eq_iff_samePacket (n : Nat)
    (Q R : Placement n) :
    unorderedPacketBlocks n Q = unorderedPacketBlocks n R ↔
      ∀ a b, samePacket Q a b ↔ samePacket R a b := by
  constructor
  · intro h a b
    rw [samePacket_iff_common_unorderedPacketBlock n Q a b,
      samePacket_iff_common_unorderedPacketBlock n R a b, h]
  · intro h
    classical
    unfold unorderedPacketBlocks
    apply congrArg (fun f : Fin n → Finset (Fin n) => Finset.univ.image f)
    funext a
    apply Finset.ext
    intro b
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact h b a

/-- The actual finite blocks represent a Setoid precisely when the
same-packet relation is its equivalence relation. -/
theorem unorderedPacketBlocks_eq_setoid_iff (n : Nat) (Q : Placement n)
    (π : RSR2.UnorderedPartition n) :
    unorderedPacketBlocks n Q = setoidPacketBlocks n π ↔
      ∀ a b, samePacket Q a b ↔ π.r a b := by
  constructor
  · intro h a b
    rw [samePacket_iff_common_unorderedPacketBlock n Q a b,
      setoid_iff_common_setoidPacketBlock n π a b, h]
  · intro h
    classical
    unfold unorderedPacketBlocks setoidPacketBlocks
    apply congrArg (fun f : Fin n → Finset (Fin n) => Finset.univ.image f)
    funext a
    apply Finset.ext
    intro b
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact h b a

/-- Endpoint realizability using the Setoid partition representation from
Paper XLVI's unordered Bell endpoint theorem. -/
def RealizesSetoidPartition (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (word : List Letter) : Prop :=
  ∃ Q : Placement n, run n hn (seed n) word = some Q ∧
    ∀ a b, samePacket Q a b ↔ π.r a b

/-- The finite-block and Paper XLVI Setoid realization predicates accept
exactly the same actual guarded words. -/
theorem realizesUnorderedPartition_iff_setoid (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (word : List Letter) :
    RealizesUnorderedPartition n hn (setoidPacketBlocks n π) word ↔
      RealizesSetoidPartition n hn π word := by
  simp only [RealizesUnorderedPartition, RealizesSetoidPartition,
    unorderedPacketBlocks_eq_setoid_iff]

/-- Attainability is unchanged by switching partition representations. -/
theorem partition_attainable_iff_setoid (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) :
    (∃ word, RealizesUnorderedPartition n hn (setoidPacketBlocks n π) word) ↔
      ∃ word, RealizesSetoidPartition n hn π word := by
  constructor
  · rintro ⟨word, hword⟩
    exact ⟨word, (realizesUnorderedPartition_iff_setoid n hn π word).mp hword⟩
  · rintro ⟨word, hword⟩
    exact ⟨word, (realizesUnorderedPartition_iff_setoid n hn π word).mpr hword⟩

/-- Paper XLVI's Bell theorem supplies an inhabited fiber for every
unordered Setoid partition in this same executor. -/
theorem setoidPartition_attainable (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) :
    ∃ word, RealizesSetoidPartition n hn π word := by
  obtain ⟨word, Q, hrun, hrel, -⟩ := unorderedPartition_bell_realization n hn π
  exact ⟨word, Q, hrun, hrel⟩

/-- The minimum actual guarded word length is independent of the partition
encoding, given the respective nonempty-fiber witnesses. -/
theorem partitionDistance_eq_setoidMinimum (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n)
    (attain : ∃ word, RealizesUnorderedPartition n hn (setoidPacketBlocks n π) word)
    (setoidAttain : ∃ word, RealizesSetoidPartition n hn π word) :
    partitionDistance n hn (setoidPacketBlocks n π) attain =
      minimumWordLength (RealizesSetoidPartition n hn π) setoidAttain := by
  symm
  apply minimumWordLength_eq
    (RealizesSetoidPartition n hn π) setoidAttain _
  · obtain ⟨word, hword, hlen⟩ := minimumWordLength_spec
      (RealizesUnorderedPartition n hn (setoidPacketBlocks n π)) attain
    exact ⟨word,
      (realizesUnorderedPartition_iff_setoid n hn π word).mp hword,
      by simpa [partitionDistance] using hlen⟩
  · intro word hword
    exact minimumWordLength_le
      (RealizesUnorderedPartition n hn (setoidPacketBlocks n π)) attain
      ((realizesUnorderedPartition_iff_setoid n hn π word).mpr hword)

end RSR2History
