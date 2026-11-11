import FusionLogEnumeration.TerminalCycle

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

namespace MarkedCircle

def nextIndex (C : MarkedCircle α) (i : Fin C.rank) : Fin C.rank :=
  ⟨(i.val + 1) % C.rank, Nat.mod_lt _ C.rank_pos⟩

theorem packet_disjoint (C : MarkedCircle α) {i j : Fin C.rank} (different : i ≠ j) :
    Disjoint C.packets[i].atoms C.packets[j].atoms := by
  rcases lt_or_gt_of_ne (Fin.val_ne_of_ne different) with h | h
  · exact List.pairwise_iff_getElem.mp C.disjoint _ _ i.isLt j.isLt h
  · exact (List.pairwise_iff_getElem.mp C.disjoint _ _ j.isLt i.isLt h).symm

theorem nextIndex_ne (C : MarkedCircle α) (visible : 2 ≤ C.rank) (i : Fin C.rank) :
    C.nextIndex i ≠ i := by
  intro same
  have h := congrArg Fin.val same
  change (i.val + 1) % C.rank = i.val at h
  by_cases hi : i.val + 1 < C.rank
  · rw [Nat.mod_eq_of_lt hi] at h
    omega
  · have hi' : i.val + 1 = C.rank := by omega
    rw [hi', Nat.mod_self] at h
    omega

/-- The next original boundary representative, extended by the identity away
from the finite set of original labels. No physical coordinates are used. -/
noncomputable def boundarySuccessor (C : MarkedCircle α) (a : α) : α :=
  if h : a ∈ C.boundaries then
    C.packets[C.nextIndex (C.boundaryEquiv.symm ⟨a, h⟩)].boundary
  else a

theorem boundarySuccessor_at (C : MarkedCircle α) (i : Fin C.rank) :
    C.boundarySuccessor C.packets[i].boundary = C.packets[C.nextIndex i].boundary := by
  have member : C.packets[i].boundary ∈ C.boundaries := (C.boundaryEquiv i).property
  have inverse : C.boundaryEquiv.symm ⟨C.packets[i].boundary, member⟩ = i := by
    exact C.boundaryEquiv.symm_apply_apply i
  unfold boundarySuccessor
  split
  · exact congrArg (fun j : Fin C.rank => C.packets[C.nextIndex j].boundary) inverse
  · rename_i absent
    exact False.elim (absent member)

/-- Every original representative other than a packet's outgoing boundary
has its successor inside that packet. The outgoing representative points
into the next packet in the positive cycle. This invariant is maintained only
while at least two packets remain. -/
structure BoundarySuccessorInvariant (labels : Finset α) (next : α → α)
    (C : MarkedCircle α) : Prop where
  internal : ∀ p ∈ C.packets, ∀ a ∈ labels,
    a ∈ p.atoms → a ≠ p.boundary → next a ∈ p.atoms
  outgoing : ∀ i : Fin C.rank,
    next C.packets[i].boundary ∈ C.packets[C.nextIndex i].atoms

theorem boundarySuccessorInvariant_initial (C : MarkedCircle α) :
    BoundarySuccessorInvariant C.boundaries C.boundarySuccessor C := by
  constructor
  · intro p hp a ha hpa different
    obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp hp
    obtain ⟨j, hj⟩ := C.boundaryEquiv.surjective ⟨a, ha⟩
    have label : C.packets[j].boundary = a := congrArg Subtype.val hj
    have indices : (⟨i, hi⟩ : Fin C.rank) ≠ j := by
      intro eq
      apply different
      calc
        a = C.packets[j].boundary := label.symm
        _ = C.packets[(⟨i, hi⟩ : Fin C.rank)].boundary := by rw [← eq]
    exact False.elim ((Finset.disjoint_left.mp (C.packet_disjoint indices)) hpa
      (label ▸ C.packets[j].boundary_mem))
  · intro i
    rw [C.boundarySuccessor_at]
    exact C.packets[C.nextIndex i].boundary_mem

theorem BoundarySuccessorInvariant.rotate {labels : Finset α} {next : α → α}
    {C : MarkedCircle α} (inv : BoundarySuccessorInvariant labels next C) (k : ℕ) :
    BoundarySuccessorInvariant labels next (C.rotate k) := by
  constructor
  · intro p hp
    exact inv.internal p ((C.packets.rotate_perm k).mem_iff.mp hp)
  · intro i
    let old : Fin C.rank := ⟨(i.val + k) % C.rank, Nat.mod_lt _ C.rank_pos⟩
    have indices : (((i.val + 1) % C.rank + k) % C.rank) =
        (((i.val + k) % C.rank + 1) % C.rank) := by
      rw [Nat.mod_add_mod, Nat.mod_add_mod]
      congr 1
      omega
    have out := inv.outgoing old
    change next C.packets[old.val].boundary ∈ _ at out
    change next (C.packets.rotate k)[i.val].boundary ∈ _
    simp only [MarkedCircle.rotate, nextIndex, Fin.getElem_fin, rank,
      List.length_rotate, List.getElem_rotate] at *
    simpa only [old, rank, indices] using out

theorem BoundarySuccessorInvariant.mergeFront {labels : Finset α} {next : α → α}
    {C : MarkedCircle α} (inv : BoundarySuccessorInvariant labels next C)
    (f : FrontSplit C) (visible : 3 ≤ C.rank) :
    BoundarySuccessorInvariant labels next (C.mergeFront f) := by
  have length : C.rank = f.rest.length + 2 := by
    simp [rank, f.eq]
  have listLength : C.packets.length = f.rest.length + 2 := length
  have leftNext : next f.left.boundary ∈ f.right.atoms := by
    have out := inv.outgoing ⟨0, by omega⟩
    change next (C.packets[0]'(by omega)).boundary ∈
      (C.packets[1 % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms at out
    simpa only [Nat.mod_eq_of_lt (show 1 < C.rank by omega),
      f.eq, List.getElem_cons_zero, List.getElem_cons_succ] using out
  constructor
  · intro p hp a ha hpa different
    simp only [MarkedCircle.mergeFront, List.mem_cons] at hp
    rcases hp with rfl | hp
    · rcases Finset.mem_union.mp hpa with hl | hr
      · by_cases same : a = f.left.boundary
        · exact Finset.mem_union_right _ (same ▸ leftNext)
        · exact Finset.mem_union_left _
            (inv.internal f.left (by rw [f.eq]; simp) a ha hl same)
      · exact Finset.mem_union_right _
          (inv.internal f.right (by rw [f.eq]; simp) a ha hr different)
    · exact inv.internal p (by rw [f.eq]; simp [hp]) a ha hpa different
  · rintro ⟨i, hi⟩
    have hrest : 0 < f.rest.length := by omega
    have irange : i < f.rest.length + 1 := hi
    let merged : MarkedPacket α := ⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
      Finset.mem_union_right _ f.right.boundary_mem⟩
    change next (merged :: f.rest)[i].boundary ∈
      ((merged :: f.rest)[(i + 1) % (f.rest.length + 1)]'(Nat.mod_lt _ (by omega))).atoms
    cases i with
    | zero =>
      have out := inv.outgoing ⟨1, by omega⟩
      change next (C.packets[1]'(by omega)).boundary ∈
        (C.packets[2 % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms at out
      simp only [Nat.mod_eq_of_lt (show 0 + 1 < f.rest.length + 1 by omega)]
      simpa only [Nat.mod_eq_of_lt (show 2 < C.rank by omega),
        f.eq, merged, List.getElem_cons_zero, List.getElem_cons_succ] using out
    | succ k =>
      let old : Fin C.rank := ⟨k + 2, by omega⟩
      have out := inv.outgoing old
      change next (C.packets[k + 2]'(by omega)).boundary ∈
        (C.packets[(k + 3) % C.rank]'(Nat.mod_lt _ C.rank_pos)).atoms at out
      by_cases last : k + 2 = f.rest.length + 1
      · have oldNext : (k + 3) % C.rank = 0 := by
          have equal : k + 3 = C.rank := by omega
          rw [equal, Nat.mod_self]
        have newNext : (k + 1 + 1) % (f.rest.length + 1) = 0 := by
          rw [last, Nat.mod_self]
        simp only [oldNext, f.eq, List.getElem_cons_zero, List.getElem_cons_succ] at out
        simp only [newNext, List.getElem_cons_zero, List.getElem_cons_succ]
        exact Finset.mem_union_left _ (by simpa using out)
      · have oldNext : (k + 3) % C.rank = k + 3 :=
          Nat.mod_eq_of_lt (by omega)
        have newNext : (k + 1 + 1) % (f.rest.length + 1) = k + 2 :=
          Nat.mod_eq_of_lt (by omega)
        simp only [oldNext, f.eq, List.getElem_cons_succ] at out
        simp only [newNext, List.getElem_cons_succ]
        simpa only [List.getElem_cons_succ] using out

theorem BoundarySuccessorInvariant.contract {labels : Finset α} {next : α → α}
    {C : MarkedCircle α} (inv : BoundarySuccessorInvariant labels next C)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) (visible : 3 ≤ C.rank) :
    BoundarySuccessorInvariant labels next (C.contract i hr) :=
  (inv.rotate i.val).mergeFront (C.frontAt i hr) (by simpa using visible)

/-- Recover boundary labels from the packet contents and the original
successor map. A boundary is visible precisely when its representative and
its original successor lie in different terminal packets. -/
def visibleBoundaries (labels : Finset α) (next : α → α)
    (packets : Finset (Finset α)) : Finset α :=
  labels.filter (fun a => ∃ B ∈ packets, a ∈ B ∧ next a ∉ B)

def packetAtoms (C : MarkedCircle α) : Finset (Finset α) :=
  (C.packets.map MarkedPacket.atoms).toFinset

theorem card_packetAtoms (C : MarkedCircle α) : C.packetAtoms.card = C.rank := by
  have nodup : (C.packets.map MarkedPacket.atoms).Nodup := by
    rw [List.nodup_iff_injective_get]
    intro i j same
    have indices : (⟨i.val, by simpa [rank] using i.isLt⟩ : Fin C.rank) =
        ⟨j.val, by simpa [rank] using j.isLt⟩ := C.atoms_injective (by simpa using same)
    exact Fin.ext (congrArg (fun k : Fin C.rank => k.val) indices)
  rw [packetAtoms, List.toFinset_card_of_nodup nodup, List.length_map]
  rfl

@[simp] theorem packetAtoms_rotate (C : MarkedCircle α) (k : ℕ) :
    (C.rotate k).packetAtoms = C.packetAtoms := by
  ext A
  simp [packetAtoms, MarkedCircle.rotate, List.mem_map]

/-- One complete ordered record updates only the source-block partition. -/
def advancePacketAtoms (packets : Finset (Finset α))
    (event : RegisteredAbsorptionChains.FusionRecord α) : Finset (Finset α) :=
  insert (event.left ∪ event.right) ((packets.erase event.left).erase event.right)

theorem packetAtoms_contract (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.contract i hr).packetAtoms = advancePacketAtoms C.packetAtoms (C.event i hr) := by
  let R := C.rotate i.val
  let f := C.frontAt i hr
  have disjoint := R.disjoint
  rw [f.eq, List.pairwise_cons, List.pairwise_cons] at disjoint
  have distinct : f.left.atoms ≠ f.right.atoms := by
    intro same
    exact (Finset.disjoint_left.mp (disjoint.1 f.right (by simp)))
      f.left.boundary_mem (same ▸ f.left.boundary_mem)
  have absentLeft : f.left.atoms ∉ (f.rest.map MarkedPacket.atoms).toFinset := by
    intro member
    obtain ⟨p, hp, same⟩ := List.mem_map.mp (List.mem_toFinset.mp member)
    exact (Finset.disjoint_left.mp (disjoint.1 p (by simp [hp])))
      f.left.boundary_mem (same ▸ f.left.boundary_mem)
  have absentRight : f.right.atoms ∉ (f.rest.map MarkedPacket.atoms).toFinset := by
    intro member
    obtain ⟨p, hp, same⟩ := List.mem_map.mp (List.mem_toFinset.mp member)
    exact (Finset.disjoint_left.mp (disjoint.2.1 p hp))
      f.right.boundary_mem (same ▸ f.right.boundary_mem)
  have old : C.packetAtoms =
      insert f.left.atoms (insert f.right.atoms (f.rest.map MarkedPacket.atoms).toFinset) := by
    rw [← C.packetAtoms_rotate i.val]
    simp only [packetAtoms, f.eq, List.map_cons, List.toFinset_cons]
  rw [old]
  simp [contract, MarkedCircle.mergeFront, packetAtoms, advancePacketAtoms,
    event, f, distinct, absentLeft, absentRight]

theorem BoundarySuccessorInvariant.visibleBoundaries_eq
    {labels : Finset α} {next : α → α} {C : MarkedCircle α}
    (inv : BoundarySuccessorInvariant labels next C) (visible : 2 ≤ C.rank)
    (inside : C.boundaries ⊆ labels) :
    visibleBoundaries labels next C.packetAtoms = C.boundaries := by
  ext a
  simp only [visibleBoundaries, Finset.mem_filter]
  constructor
  · rintro ⟨ha, B, hB, hba, hnext⟩
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp hB)
    have same : a = p.boundary := by
      by_contra different
      exact hnext (inv.internal p hp a ha hba different)
    subst a
    exact List.mem_toFinset.mpr (List.mem_map.mpr ⟨p, hp, rfl⟩)
  · intro ha
    obtain ⟨i, hi⟩ := C.boundaryEquiv.surjective ⟨a, ha⟩
    have label : C.packets[i].boundary = a := congrArg Subtype.val hi
    refine ⟨inside ha, C.packets[i].atoms, ?_, label ▸ C.packets[i].boundary_mem, ?_⟩
    · exact List.mem_toFinset.mpr (List.mem_map.mpr ⟨_, List.getElem_mem i.isLt, rfl⟩)
    · intro member
      have outside := inv.outgoing i
      rw [label] at outside
      exact (Finset.disjoint_left.mp (C.packet_disjoint (C.nextIndex_ne visible i).symm))
        member outside

end MarkedCircle

namespace Schedule

theorem terminalCircle_packetAtoms_eq_fold {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) :
    path.terminalCircle.packetAtoms =
      path.records.foldl MarkedCircle.advancePacketAtoms C.packetAtoms := by
  induction path with
  | stop C => rfl
  | @step C d hr i tail ih =>
      simpa only [terminalCircle, records, List.foldl_cons, C.packetAtoms_contract i hr]
        using ih

theorem terminalCircle_boundarySuccessorInvariant {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) {labels : Finset α} {next : α → α}
    (inv : MarkedCircle.BoundarySuccessorInvariant labels next C)
    (visible : 2 ≤ path.terminalCircle.rank) :
    MarkedCircle.BoundarySuccessorInvariant labels next path.terminalCircle := by
  induction path with
  | stop C => exact inv
  | @step C d hr i tail ih =>
      have rank_eq := tail.terminalCircle_rank
      have contract_eq := C.rank_contract i hr
      exact ih (inv.contract i hr (by change 2 ≤ tail.terminalCircle.rank at visible; omega)) visible

/-- At visible terminal rank the literal terminal packet partition determines
the surviving original boundary labels. The terminal marker fields are not
inputs to the recovery function. -/
theorem terminalCircle_survivors_recover {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) (visible : 2 ≤ path.terminalCircle.rank) :
    MarkedCircle.visibleBoundaries C.boundaries C.boundarySuccessor
      path.terminalCircle.packetAtoms = C.boundaries \ path.deletions.toFinset := by
  rw [← path.terminalCircle_boundaries_eq_survivors]
  apply (path.terminalCircle_boundarySuccessorInvariant
    C.boundarySuccessorInvariant_initial visible).visibleBoundaries_eq visible
  rw [path.terminalCircle_boundaries_eq_survivors]
  exact Finset.sdiff_subset

theorem terminalCircle_survivors_eq_of_packetAtoms_eq
    {C : MarkedCircle α} {d₁ d₂ : ℕ} (first : Schedule C d₁) (second : Schedule C d₂)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank)
    (same : first.terminalCircle.packetAtoms = second.terminalCircle.packetAtoms) :
    C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset := by
  rw [← first.terminalCircle_survivors_recover visible₁,
    ← second.terminalCircle_survivors_recover visible₂, same]

end Schedule

end FusionLogEnumeration
