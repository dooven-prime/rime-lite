import FusionLogEnumeration.InitialCycleIndexing

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation
  FusionLogSchedule

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

namespace MarkedCircle

omit [NeZero n]

/-- A static interpretation of the current positive packet circle in the
fixed initial source-site coordinates. No execution word is part of the data. -/
structure IndexedCircle (encode : Finset α → Finset (ZMod n))
    (labels : ZMod n → Finset α) (C : MarkedCircle α) : Prop where
  decodes : ∀ p ∈ C.packets, expandBlock labels (encode p.atoms) = p.atoms
  adjacent : ∀ i : Fin C.rank,
    SourceAtomAdjacent (encode C.packets[i].atoms) (encode C.packets[C.nextIndex i].atoms)

theorem IndexedCircle.rotate {encode : Finset α → Finset (ZMod n)}
    {labels : ZMod n → Finset α} {C : MarkedCircle α}
    (model : IndexedCircle encode labels C) (k : ℕ) :
    IndexedCircle encode labels (C.rotate k) := by
  constructor
  · intro p hp
    exact model.decodes p ((C.packets.rotate_perm k).mem_iff.mp hp)
  · intro i
    let old : Fin C.rank := ⟨(i.val + k) % C.rank, Nat.mod_lt _ C.rank_pos⟩
    have indices : (((i.val + 1) % C.rank + k) % C.rank) =
        (((i.val + k) % C.rank + 1) % C.rank) := by
      rw [Nat.mod_add_mod, Nat.mod_add_mod]
      congr 1
      omega
    have out := model.adjacent old
    change SourceAtomAdjacent (encode C.packets[old.val].atoms) _ at out
    change SourceAtomAdjacent (encode (C.packets.rotate k)[i.val].atoms) _
    simp only [MarkedCircle.rotate, nextIndex, Fin.getElem_fin, rank,
      List.length_rotate, List.getElem_rotate] at *
    simpa only [old, rank, indices] using out

private theorem adjacent_mono {A B U V : Finset (ZMod n)}
    (edge : SourceAtomAdjacent A B) (left : A ⊆ U) (right : B ⊆ V) :
    SourceAtomAdjacent U V := by
  obtain ⟨a, ha, hb⟩ := edge
  exact ⟨a, left ha, right hb⟩

theorem IndexedCircle.mergeFront {encode : Finset α → Finset (ZMod n)}
    {labels : ZMod n → Finset α} {C : MarkedCircle α}
    (model : IndexedCircle encode labels C)
    (union : ∀ A B, encode (A ∪ B) = encode A ∪ encode B) (f : FrontSplit C) :
    IndexedCircle encode labels (C.mergeFront f) := by
  have length : C.rank = f.rest.length + 2 := by simp [rank, f.eq]
  have listLength : C.packets.length = f.rest.length + 2 := length
  have leftNext : SourceAtomAdjacent (encode f.left.atoms) (encode f.right.atoms) := by
    have out := model.adjacent ⟨0, by omega⟩
    change SourceAtomAdjacent (encode (C.packets[0]'(by omega)).atoms)
      (encode (C.packets[1 % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms) at out
    simpa only [Nat.mod_eq_of_lt (show 1 < C.rank by omega), f.eq,
      List.getElem_cons_zero, List.getElem_cons_succ] using out
  constructor
  · intro p hp
    simp only [MarkedCircle.mergeFront, List.mem_cons] at hp
    rcases hp with rfl | hp
    · rw [union, expandBlock_union, model.decodes f.left (by rw [f.eq]; simp),
        model.decodes f.right (by rw [f.eq]; simp)]
    · exact model.decodes p (by rw [f.eq]; simp [hp])
  · rintro ⟨i, hi⟩
    let merged : MarkedPacket α := ⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
      Finset.mem_union_right _ f.right.boundary_mem⟩
    have irange : i < f.rest.length + 1 := hi
    change SourceAtomAdjacent (encode (merged :: f.rest)[i].atoms)
      (encode ((merged :: f.rest)[(i + 1) % (f.rest.length + 1)]'
        (Nat.mod_lt _ (by omega))).atoms)
    by_cases empty : f.rest = []
    · have zero : i = 0 := by simp [empty] at irange; omega
      subst i
      simp only [empty, List.length_nil, Nat.zero_add, Nat.mod_self,
        List.getElem_cons_zero, merged, union]
      exact adjacent_mono leftNext Finset.subset_union_left Finset.subset_union_right
    · have hrest : 0 < f.rest.length := List.length_pos_iff.mpr empty
      cases i with
      | zero =>
        have out := model.adjacent ⟨1, by omega⟩
        change SourceAtomAdjacent (encode (C.packets[1]'(by omega)).atoms)
          (encode (C.packets[2 % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms) at out
        simp only [Nat.mod_eq_of_lt (show 2 < C.rank by omega), f.eq,
          List.getElem_cons_zero, List.getElem_cons_succ] at out
        simp only [Nat.mod_eq_of_lt (show 0 + 1 < f.rest.length + 1 by omega),
          List.getElem_cons_zero, List.getElem_cons_succ, merged, union]
        exact adjacent_mono out Finset.subset_union_right (Finset.Subset.refl _)
      | succ k =>
        have out := model.adjacent ⟨k + 2, by omega⟩
        change SourceAtomAdjacent (encode (C.packets[k + 2]'(by omega)).atoms)
          (encode (C.packets[(k + 3) % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms) at out
        by_cases last : k + 2 = f.rest.length + 1
        · have oldNext : (k + 3) % C.rank = 0 := by
            have same : k + 3 = C.rank := by omega
            rw [same, Nat.mod_self]
          have newNext : (k + 1 + 1) % (f.rest.length + 1) = 0 := by
            rw [last, Nat.mod_self]
          simp only [oldNext, f.eq, List.getElem_cons_zero, List.getElem_cons_succ] at out
          simp only [newNext, List.getElem_cons_zero, List.getElem_cons_succ, merged, union]
          exact adjacent_mono out (Finset.Subset.refl _) Finset.subset_union_left
        · have oldNext : (k + 3) % C.rank = k + 3 := Nat.mod_eq_of_lt (by omega)
          have newNext : (k + 1 + 1) % (f.rest.length + 1) = k + 2 :=
            Nat.mod_eq_of_lt (by omega)
          simp only [oldNext, f.eq, List.getElem_cons_succ] at out
          simpa only [newNext, List.getElem_cons_succ] using out

theorem IndexedCircle.contract {encode : Finset α → Finset (ZMod n)}
    {labels : ZMod n → Finset α} {C : MarkedCircle α}
    (model : IndexedCircle encode labels C)
    (union : ∀ A B, encode (A ∪ B) = encode A ∪ encode B)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    IndexedCircle encode labels (C.contract i hr) :=
  (model.rotate i.val).mergeFront union (C.frontAt i hr)

theorem IndexedCircle.encode_injective {encode : Finset α → Finset (ZMod n)}
    {labels : ZMod n → Finset α} {C : MarkedCircle α}
    (model : IndexedCircle encode labels C) : Set.InjOn encode (↑C.packetAtoms : Set (Finset α)) := by
  intro A hA B hB same
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp hA)
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp hB)
  exact (model.decodes p hp).symm.trans ((congrArg (expandBlock labels) same).trans
    (model.decodes q hq))

private theorem image_erase_on {ι β : Type*} [DecidableEq ι] [DecidableEq β]
    (f : ι → β) (S : Finset ι) (a : ι) (ha : a ∈ S)
    (injective : Set.InjOn f (↑S : Set ι)) :
    (S.erase a).image f = (S.image f).erase (f a) := by
  ext b
  simp only [Finset.mem_image, Finset.mem_erase]
  constructor
  · rintro ⟨x, ⟨different, hx⟩, rfl⟩
    exact ⟨fun same => different (injective hx ha same), x, hx, rfl⟩
  · rintro ⟨different, x, hx, rfl⟩
    exact ⟨x, ⟨fun same => different (congrArg f same), hx⟩, rfl⟩

theorem IndexedCircle.contract_indexPackets {encode : Finset α → Finset (ZMod n)}
    {labels : ZMod n → Finset α} {C : MarkedCircle α}
    (model : IndexedCircle encode labels C)
    (union : ∀ A B, encode (A ∪ B) = encode A ∪ encode B)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.contract i hr).packetAtoms.image encode =
      mergePackets (C.packetAtoms.image encode)
        (encode (C.event i hr).left) (encode (C.event i hr).right) := by
  let R := C.rotate i.val
  let f := C.frontAt i hr
  have disjoint := R.disjoint
  rw [f.eq, List.pairwise_cons, List.pairwise_cons] at disjoint
  have distinct : f.left.atoms ≠ f.right.atoms := by
    intro same
    exact (Finset.disjoint_left.mp (disjoint.1 f.right (by simp)))
      f.left.boundary_mem (same ▸ f.left.boundary_mem)
  have left : f.left.atoms ∈ C.packetAtoms := by
    rw [← C.packetAtoms_rotate i.val]
    simp [packetAtoms, f.eq]
  have right : f.right.atoms ∈ C.packetAtoms := by
    rw [← C.packetAtoms_rotate i.val]
    simp [packetAtoms, f.eq]
  rw [C.packetAtoms_contract i hr]
  change (insert (f.left.atoms ∪ f.right.atoms)
    ((C.packetAtoms.erase f.left.atoms).erase f.right.atoms)).image encode = _
  rw [Finset.image_insert, union,
    image_erase_on encode _ f.right.atoms (Finset.mem_erase.mpr ⟨distinct.symm, right⟩)
      (model.encode_injective.mono (by intro A hA; exact Finset.mem_of_mem_erase hA)),
    image_erase_on encode _ f.left.atoms left model.encode_injective]
  rfl

end MarkedCircle

/-- Encoding applies to the full ordered event tuple, including its result. -/
def encodeFusionRecord (encode : Finset α → Finset (ZMod n))
    (record : FusionRecord α) : FusionRecord (ZMod n) :=
  ⟨encode record.left, encode record.right, encode record.result⟩

namespace Schedule

omit [NeZero n]

/-- Induction on the M5 schedule builds a static M4-D trace, with no raw
word or intermediate physical placement assumed. -/
theorem indexed_abstractTrace {C : MarkedCircle α} {d : ℕ} (path : Schedule C d)
    (encode : Finset α → Finset (ZMod n)) (labels : ZMod n → Finset α)
    (union : ∀ A B, encode (A ∪ B) = encode A ∪ encode B)
    (model : MarkedCircle.IndexedCircle encode labels C) :
    AbstractTrace (C.packetAtoms.image encode)
      (path.records.map (encodeFusionRecord encode))
      (path.terminalCircle.packetAtoms.image encode) := by
  induction path with
  | stop C => exact .nil _
  | @step C d hr i tail ih =>
    let R := C.rotate i.val
    let f := C.frontAt i hr
    have left : f.left.atoms ∈ C.packetAtoms := by
      rw [← C.packetAtoms_rotate i.val]; simp [MarkedCircle.packetAtoms, f.eq]
    have right : f.right.atoms ∈ C.packetAtoms := by
      rw [← C.packetAtoms_rotate i.val]; simp [MarkedCircle.packetAtoms, f.eq]
    have distinct : f.left.atoms ≠ f.right.atoms := by
      have h := R.disjoint
      rw [f.eq, List.pairwise_cons] at h
      intro same
      exact (Finset.disjoint_left.mp (h.1 f.right (by simp)))
        f.left.boundary_mem (same ▸ f.left.boundary_mem)
    have different : encode f.left.atoms ≠ encode f.right.atoms :=
      fun same => distinct (model.encode_injective left right same)
    have boundary : SourceAtomAdjacent (encode f.left.atoms) (encode f.right.atoms) := by
      have out := (model.rotate i.val).adjacent ⟨0, R.rank_pos⟩
      have splitEq : R.packets = f.left :: f.right :: f.rest := f.eq
      have large : 1 < R.rank := by simp [R]; omega
      change SourceAtomAdjacent (encode (R.packets[0]'R.rank_pos).atoms)
        (encode (R.packets[1 % R.rank]'(Nat.mod_lt _ R.rank_pos)).atoms) at out
      simpa only [Nat.mod_eq_of_lt large, splitEq,
        List.getElem_cons_zero, List.getElem_cons_succ] using out
    have next := ih (model.contract union i hr)
    rw [model.contract_indexPackets union i hr] at next
    simpa only [records, List.map_cons, encodeFusionRecord, MarkedCircle.event,
      union, terminalCircle] using
      (AbstractTrace.cons (Finset.mem_image.mpr ⟨_, left, rfl⟩)
        (Finset.mem_image.mpr ⟨_, right, rfl⟩) different boundary next)

theorem indexed_records_expand {C : MarkedCircle α} {d : ℕ} (path : Schedule C d)
    (encode : Finset α → Finset (ZMod n)) (labels : ZMod n → Finset α)
    (union : ∀ A B, encode (A ∪ B) = encode A ∪ encode B)
    (model : MarkedCircle.IndexedCircle encode labels C) :
    (path.records.map (encodeFusionRecord encode)).map (expandRecord labels) = path.records := by
  induction path with
  | stop C => rfl
  | @step C d hr i tail ih =>
    let f := C.frontAt i hr
    have left : f.left ∈ C.packets :=
      (C.packets.rotate_perm i.val).mem_iff.mp (by
        change f.left ∈ (C.rotate i.val).packets
        rw [f.eq]; simp)
    have right : f.right ∈ C.packets :=
      (C.packets.rotate_perm i.val).mem_iff.mp (by
        change f.right ∈ (C.rotate i.val).packets
        rw [f.eq]; simp)
    simp only [records, List.map_cons]
    rw [ih (model.contract union i hr)]
    congr 1
    change expandRecord labels (encodeFusionRecord encode
      ⟨f.left.atoms, f.right.atoms, f.left.atoms ∪ f.right.atoms⟩) =
        ⟨f.left.atoms, f.right.atoms, f.left.atoms ∪ f.right.atoms⟩
    simp only [encodeFusionRecord, expandRecord, union, expandBlock_union,
      model.decodes f.left left, model.decodes f.right right]

end Schedule

namespace LiteralPacketStart

variable {C : MarkedCircle α} [NeZero C.rank]

theorem indexedCircle (start : LiteralPacketStart C n) :
    MarkedCircle.IndexedCircle start.indexBlock (siteLabels start.initial) C := by
  constructor
  · intro p hp
    have mem : p.atoms ∈ packetSet start.initial := by
      rw [start.packetSet_initial]
      exact List.mem_toFinset.mpr (List.mem_map.mpr ⟨p, hp, rfl⟩)
    obtain ⟨q, atSite⟩ := (mem_packetSet _ _).mp mem
    exact start.expand_indexBlock_of_initial_at atSite
  · intro i
    have castNext : ((C.nextIndex i).val : ZMod C.rank) = (i.val : ZMod C.rank) + 1 := by
      simp [MarkedCircle.nextIndex, Nat.cast_add]
    rw [← start.circleBlocks i, ← start.circleBlocks (C.nextIndex i), castNext]
    exact start.initial_indexBlocks_adjacent (i.val : ZMod C.rank)

theorem initial_indexPacketSet (start : LiteralPacketStart C n) :
    C.packetAtoms.image start.indexBlock =
      packetSet (canonicalPlacement start.initial start.occupied_nonempty) := by
  ext I
  constructor
  · intro member
    obtain ⟨B, hB, rfl⟩ := Finset.mem_image.mp member
    rw [← start.packetSet_initial] at hB
    obtain ⟨q, atSite⟩ := (mem_packetSet _ _).mp hB
    rw [start.indexBlock_of_initial_at atSite]
    have present : q ∈ occupiedSites start.initial := by simp [occupiedSites, atSite]
    have fixed := occupiedRounding_fixed (occupiedSites start.initial) start.occupied_nonempty q present
    exact (mem_packetSet _ _).mpr ⟨q, (placementOfMap_some_iff _ q _).mpr
      ⟨rfl, q, (mem_sourceFiber _ _ _).mpr fixed⟩⟩
  · intro member
    obtain ⟨q, atSite⟩ := (mem_packetSet _ _).mp member
    have decoded := congrFun (initial_placement_interprets start.initial start.occupied_nonempty) q
    change start.initial q = (canonicalPlacement start.initial _ q).map _ at decoded
    rw [atSite] at decoded
    let B := expandBlock (siteLabels start.initial) I
    have literal : start.initial q = some B := decoded
    refine Finset.mem_image.mpr ⟨B, ?_, ?_⟩
    · rw [← start.packetSet_initial]
      exact (mem_packetSet _ _).mpr ⟨q, literal⟩
    · rw [start.indexBlock_of_initial_at literal]
      exact ((placementOfMap_some_iff _ q I).mp atSite).1

end LiteralPacketStart

/-- Every M5 boundary-contraction schedule is M4-D admissible for its given
literal start. This constructs indexed event data and a static AbstractTrace;
it does not invoke joint realization or any raw execution word. -/
def schedule_admissible_of_literalStart {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d) :
    AdmissibleSchedule start.initial start.occupied_nonempty path.records where
  indexEvents := path.records.map (encodeFusionRecord start.indexBlock)
  last := path.terminalCircle.packetAtoms.image start.indexBlock
  abstractTrace := by
    rw [← start.initial_indexPacketSet]
    exact path.indexed_abstractTrace start.indexBlock (siteLabels start.initial)
      start.indexBlock_union start.indexedCircle
  records := path.indexed_records_expand start.indexBlock (siteLabels start.initial)
    start.indexBlock_union start.indexedCircle

@[simp] theorem schedule_admissible_of_literalStart_records
    {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d) :
    (schedule_admissible_of_literalStart start path).indexEvents.map
      (expandRecord (siteLabels start.initial)) = path.records :=
  (schedule_admissible_of_literalStart start path).records

@[simp] theorem schedule_admissible_of_literalStart_last
    {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d) :
    (schedule_admissible_of_literalStart start path).last =
      path.terminalCircle.packetAtoms.image start.indexBlock := rfl

/-- Propositional existence wrapper for callers that do not need the
explicit indexed event and terminal-packet data. -/
theorem schedule_admissible_of_literalStart_nonempty
    {C : MarkedCircle α} [NeZero C.rank]
    (start : LiteralPacketStart C n) {d : ℕ} (path : Schedule C d) :
    Nonempty (AdmissibleSchedule start.initial start.occupied_nonempty path.records) :=
  ⟨schedule_admissible_of_literalStart start path⟩

end FusionLogEnumeration
