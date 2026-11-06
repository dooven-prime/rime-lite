import FusionLogSchedule.JointClassification

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

structure PacketPartition (P : Placement n (Finset α)) : Prop where
  nonempty : ∀ q A, P q = some A → A.Nonempty
  disjoint : ∀ q r A B, q ≠ r → P q = some A → P r = some B → Disjoint A B

def Saturated (f : ZMod n → ZMod n) (A : Finset (ZMod n)) : Prop :=
  ∀ i j, f i = f j → (i ∈ A ↔ j ∈ A)

def AllSaturated (f : ZMod n → ZMod n) (C : IndexPackets n) : Prop :=
  ∀ A ∈ C, Saturated f A

theorem saturated_union {f : ZMod n → ZMod n} {A B : Finset (ZMod n)}
    (first : Saturated f A) (second : Saturated f B) : Saturated f (A ∪ B) := by
  intro i j same
  simp only [Finset.mem_union]
  exact or_congr (first i j same) (second i j same)

theorem initial_packets_saturated (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) :
    AllSaturated (occupiedRounding (occupiedSites P) nonempty).position
      (packetSet (canonicalPlacement P nonempty)) := by
  intro A member
  obtain ⟨q, atSite⟩ := (mem_packetSet _ A).mp member
  have fiber := ((placementOfMap_some_iff
    (occupiedRounding (occupiedSites P) nonempty).position q A).mp atSite).1
  rw [← fiber]
  intro i j same
  simp only [mem_sourceFiber, same]

theorem merge_packets_saturated {f : ZMod n → ZMod n} {C : IndexPackets n}
    {A B : Finset (ZMod n)} (all : AllSaturated f C) (left : A ∈ C) (right : B ∈ C) :
    AllSaturated f (mergePackets C A B) := by
  intro D member
  rcases Finset.mem_insert.mp member with eq | old
  · subst D
    exact saturated_union (all A left) (all B right)
  · exact all D (Finset.mem_of_mem_erase (Finset.mem_of_mem_erase old))

theorem AbstractTrace.preserves_saturation {f : ZMod n → ZMod n}
    {C last : IndexPackets n} {events : List (FusionRecord (ZMod n))}
    (trace : AbstractTrace C events last) (all : AllSaturated f C) : AllSaturated f last := by
  induction trace with
  | nil C => exact all
  | cons left right _ _ _ ih => exact ih (merge_packets_saturated all left right)

theorem siteLabels_disjoint (P : Placement n (Finset α)) (valid : PacketPartition P)
    (q r : ZMod n) (different : q ≠ r) : Disjoint (siteLabels P q) (siteLabels P r) := by
  cases hq : P q <;> cases hr : P r <;> simp only [siteLabels, hq, hr, Option.getD_none,
    Option.getD_some, Finset.disjoint_empty_left, Finset.disjoint_empty_right]
  exact valid.disjoint q r _ _ different hq hr

theorem siteLabels_nonempty (P : Placement n (Finset α)) (valid : PacketPartition P)
    (q : ZMod n) (present : q ∈ occupiedSites P) : (siteLabels P q).Nonempty := by
  cases hq : P q with
  | none => simp [occupiedSites, hq] at present
  | some A => simpa only [siteLabels, hq, Option.getD_some] using valid.nonempty q A hq

/-- Restore whole initial source fibres from literal atom contents. -/
def restoreBlock (P : Placement n (Finset α)) (nonempty : (occupiedSites P).Nonempty)
    (B : Finset α) : Finset (ZMod n) :=
  Finset.univ.filter (fun i => siteLabels P
    ((occupiedRounding (occupiedSites P) nonempty).position i) ⊆ B)

theorem restore_expandBlock (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) (valid : PacketPartition P)
    (A : Finset (ZMod n))
    (saturated : Saturated (occupiedRounding (occupiedSites P) nonempty).position A) :
    restoreBlock P nonempty (expandBlock (siteLabels P) A) = A := by
  let f := (occupiedRounding (occupiedSites P) nonempty).position
  ext i
  simp only [restoreBlock, Finset.mem_filter, Finset.mem_univ, true_and]
  let q := f i
  have present : q ∈ occupiedSites P := occupiedRounding_image _ nonempty i
  have fixed : f q = q := occupiedRounding_fixed _ nonempty q present
  have same : f i = f q := by rw [fixed]
  constructor
  · intro subset
    obtain ⟨a, ha⟩ := siteLabels_nonempty P valid q present
    have inUnion := subset ha
    obtain ⟨j, hj, atom⟩ := Finset.mem_biUnion.mp inUnion
    have eq : q = j := by
      by_contra different
      exact (Finset.disjoint_left.mp (siteLabels_disjoint P valid q j different)) ha atom
    have member : q ∈ A := eq ▸ hj
    exact (saturated i q same).mpr member
  · intro member
    have qMember : q ∈ A := (saturated i q same).mp member
    intro a ha
    exact Finset.mem_biUnion.mpr ⟨q, qMember, ha⟩

def restoreRecord (P : Placement n (Finset α)) (nonempty : (occupiedSites P).Nonempty)
    (event : FusionRecord α) : FusionRecord (ZMod n) :=
  ⟨restoreBlock P nonempty event.left, restoreBlock P nonempty event.right,
    restoreBlock P nonempty event.result⟩

theorem restore_expand_record (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) (valid : PacketPartition P)
    (A B : Finset (ZMod n))
    (left : Saturated (occupiedRounding (occupiedSites P) nonempty).position A)
    (right : Saturated (occupiedRounding (occupiedSites P) nonempty).position B) :
    restoreRecord P nonempty (expandRecord (siteLabels P) ⟨A, B, A ∪ B⟩) = ⟨A, B, A ∪ B⟩ := by
  simp only [restoreRecord, expandRecord]
  rw [restore_expandBlock P nonempty valid A left,
    restore_expandBlock P nonempty valid B right,
    restore_expandBlock P nonempty valid (A ∪ B) (saturated_union left right)]

theorem AbstractTrace.restore_records (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) (valid : PacketPartition P)
    {C last : IndexPackets n} {events : List (FusionRecord (ZMod n))}
    (trace : AbstractTrace C events last)
    (all : AllSaturated (occupiedRounding (occupiedSites P) nonempty).position C) :
    (events.map (expandRecord (siteLabels P))).map (restoreRecord P nonempty) = events := by
  induction trace with
  | nil C => rfl
  | @cons C last A B rest left right _ _ _ ih =>
      simp only [List.map_cons]
      rw [restore_expand_record P nonempty valid A B (all A left) (all B right),
        ih (merge_packets_saturated all left right)]

theorem AdmissibleSchedule.indexEvents_recover {P : Placement n (Finset α)}
    {nonempty : (occupiedSites P).Nonempty} {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule P nonempty events) (valid : PacketPartition P) :
    schedule.indexEvents = events.map (restoreRecord P nonempty) := by
  have recovered := schedule.abstractTrace.restore_records P nonempty valid
    (initial_packets_saturated P nonempty)
  rw [schedule.records] at recovered
  exact recovered.symm

theorem AdmissibleSchedule.indexEvents_unique {P : Placement n (Finset α)}
    {nonempty : (occupiedSites P).Nonempty} {events : List (FusionRecord α)}
    (first second : AdmissibleSchedule P nonempty events) (valid : PacketPartition P) :
    first.indexEvents = second.indexEvents :=
  (first.indexEvents_recover valid).trans (second.indexEvents_recover valid).symm

end FusionLogSchedule
