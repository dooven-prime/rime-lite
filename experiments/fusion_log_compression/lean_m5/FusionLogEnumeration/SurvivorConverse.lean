import FusionLogEnumeration.SurvivorRecovery

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

namespace MarkedCircle

/-- Every packet is contained in one equivalence class of `E`. -/
def Homogeneous (E : α → α → Prop) (C : MarkedCircle α) : Prop :=
  ∀ p ∈ C.packets, ∀ a ∈ p.atoms, ∀ b ∈ p.atoms, E a b

theorem homogeneous_rotate_iff (E : α → α → Prop) (C : MarkedCircle α) (k : ℕ) :
    Homogeneous E (C.rotate k) ↔ Homogeneous E C := by
  constructor <;> intro h p hp
  · exact h p ((C.packets.rotate_perm k).mem_iff.mpr hp)
  · exact h p ((C.packets.rotate_perm k).mem_iff.mp hp)

/-- Merging two packets adds exactly one equivalence constraint between
any chosen representative of the left packet and one of the right packet. -/
theorem homogeneous_mergeFront_iff (E : α → α → Prop) (equiv : Equivalence E)
    (C : MarkedCircle α) (f : FrontSplit C) {a b : α}
    (left : a ∈ f.left.atoms) (right : b ∈ f.right.atoms) :
    Homogeneous E (C.mergeFront f) ↔ Homogeneous E C ∧ E a b := by
  let merged : MarkedPacket α := ⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
    Finset.mem_union_right _ f.right.boundary_mem⟩
  constructor
  · intro h
    have hm := h merged (by simp [merged, MarkedCircle.mergeFront])
    refine ⟨?_, hm a (Finset.mem_union_left _ left) b (Finset.mem_union_right _ right)⟩
    intro p hp x hx y hy
    rw [f.eq] at hp
    rcases List.mem_cons.mp hp with rfl | hp
    · exact hm x (Finset.mem_union_left _ hx) y (Finset.mem_union_left _ hy)
    · rcases List.mem_cons.mp hp with rfl | hp
      · exact hm x (Finset.mem_union_right _ hx) y (Finset.mem_union_right _ hy)
      · exact h p (by simp [MarkedCircle.mergeFront, hp]) x hx y hy
  · rintro ⟨h, hab⟩ p hp x hx y hy
    have hl := h f.left (by rw [f.eq]; simp)
    have hr := h f.right (by rw [f.eq]; simp)
    change p ∈ merged :: f.rest at hp
    rcases List.mem_cons.mp hp with rfl | hp
    · rcases Finset.mem_union.mp hx with hx | hx <;>
        rcases Finset.mem_union.mp hy with hy | hy
      · exact hl x hx y hy
      · exact equiv.trans (hl x hx a left) (equiv.trans hab (hr b right y hy))
      · exact equiv.symm (equiv.trans (hl y hy a left) (equiv.trans hab (hr b right x hx)))
      · exact hr x hx y hy
    · exact h p (by rw [f.eq]; simp [hp]) x hx y hy

theorem BoundarySuccessorInvariant.homogeneous_contract_iff
    {labels : Finset α} {next : α → α} {C : MarkedCircle α}
    (inv : BoundarySuccessorInvariant labels next C)
    (E : α → α → Prop) (equiv : Equivalence E)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    Homogeneous E (C.contract i hr) ↔
      Homogeneous E C ∧ E (C.deleted i hr) (next (C.deleted i hr)) := by
  let R := C.rotate i.val
  let f := C.frontAt i hr
  have positive : 0 < R.rank := R.rank_pos
  have large : 1 < R.rank := by change 1 < (C.rotate i.val).rank; simp; omega
  have splitEq : R.packets = f.left :: f.right :: f.rest := f.eq
  have out : next f.left.boundary ∈ f.right.atoms := by
    have h := (inv.rotate i.val).outgoing ⟨0, positive⟩
    change next (R.packets[0]'positive).boundary ∈
      (R.packets[1 % R.rank]'(Nat.mod_lt _ R.rank_pos)).atoms at h
    simpa only [Nat.mod_eq_of_lt large,
      splitEq, List.getElem_cons_zero, List.getElem_cons_succ] using h
  exact (homogeneous_mergeFront_iff E equiv R f f.left.boundary_mem out).trans
    (and_congr_left (fun _ => homogeneous_rotate_iff E C i.val))

theorem packet_eq_of_shared_atom (C : MarkedCircle α)
    {p q : MarkedPacket α} (hp : p ∈ C.packets) (hq : q ∈ C.packets)
    {a : α} (ha : a ∈ p.atoms) (hqa : a ∈ q.atoms) : p = q := by
  obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp hp
  obtain ⟨j, hj, rfl⟩ := List.mem_iff_getElem.mp hq
  have indices : (⟨i, hi⟩ : Fin C.rank) = ⟨j, hj⟩ := by
    by_contra different
    exact (Finset.disjoint_left.mp (C.packet_disjoint different)) ha hqa
  exact congrArg (fun k : Fin C.rank => C.packets[k]) indices

/-- Equality of membership profiles is an equivalence relation even for
atoms outside the represented support; no quotient or choice is needed. -/
def PacketProfileEq (C : MarkedCircle α) (a b : α) : Prop :=
  ∀ p ∈ C.packets, a ∈ p.atoms ↔ b ∈ p.atoms

theorem packetProfileEq_equivalence (C : MarkedCircle α) :
    Equivalence C.PacketProfileEq := by
  refine ⟨?_, ?_, ?_⟩
  · intro a p hp; exact Iff.rfl
  · intro a b h p hp; exact (h p hp).symm
  · intro a b c hab hbc p hp; exact (hab p hp).trans (hbc p hp)

theorem homogeneous_packetProfileEq (C : MarkedCircle α) :
    Homogeneous C.PacketProfileEq C := by
  intro p hp a ha b hb q hq
  constructor
  · intro hqa
    exact (C.packet_eq_of_shared_atom hp hq ha hqa) ▸ hb
  · intro hqb
    exact (C.packet_eq_of_shared_atom hp hq hb hqb) ▸ ha

theorem atomUnion_contract (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.contract i hr).atomUnion = C.atomUnion := by
  let f := C.frontAt i hr
  have rotated : (C.rotate i.val).atomUnion = C.atomUnion := by
    ext a
    simp [atomUnion, MarkedCircle.rotate]
  rw [← rotated]
  ext a
  simp [contract, MarkedCircle.mergeFront, atomUnion, f.eq, f]

/-- Mutual homogeneity and equal support determine the same literal blocks.
The proof uses an atom of each nonempty packet, not its boundary marker. -/
theorem packetAtoms_eq_of_mutual_homogeneous (C D : MarkedCircle α)
    (support : C.atomUnion = D.atomUnion)
    (first : Homogeneous D.PacketProfileEq C)
    (second : Homogeneous C.PacketProfileEq D) : C.packetAtoms = D.packetAtoms := by
  have subset : ∀ (S T : MarkedCircle α), S.atomUnion = T.atomUnion →
      Homogeneous T.PacketProfileEq S → Homogeneous S.PacketProfileEq T →
      S.packetAtoms ⊆ T.packetAtoms := by
    intro S T support hs ht A hA
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp hA)
    have member : p.boundary ∈ T.atomUnion := by
      rw [← support]
      exact Finset.mem_biUnion.mpr ⟨p, List.mem_toFinset.mpr hp, p.boundary_mem⟩
    obtain ⟨q, hq, hqa⟩ := T.atomUnion_covers p.boundary member
    have same : p.atoms = q.atoms := by
      apply Finset.Subset.antisymm
      · intro b hb
        exact (hs p hp p.boundary p.boundary_mem b hb q hq).mp hqa
      · intro b hb
        exact (ht q hq p.boundary hqa b hb p hp).mp p.boundary_mem
    rw [same]
    exact List.mem_toFinset.mpr (List.mem_map.mpr ⟨q, hq, rfl⟩)
  exact Finset.Subset.antisymm (subset C D support first second)
    (subset D C support.symm second first)

end MarkedCircle

namespace Schedule

theorem terminalCircle_atomUnion {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    path.terminalCircle.atomUnion = C.atomUnion := by
  induction path with
  | stop C => rfl
  | @step C d hr i tail ih => exact ih.trans (C.atomUnion_contract i hr)

/-- A schedule adds exactly the original-successor equivalence constraints
at its deleted boundaries. Thus their order cannot affect terminal blocks. -/
theorem homogeneous_terminalCircle_iff {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) {labels : Finset α} {next : α → α}
    (inv : MarkedCircle.BoundarySuccessorInvariant labels next C)
    (visible : 2 ≤ path.terminalCircle.rank)
    (E : α → α → Prop) (equiv : Equivalence E) :
    MarkedCircle.Homogeneous E path.terminalCircle ↔
      MarkedCircle.Homogeneous E C ∧ ∀ a ∈ path.deletions, E a (next a) := by
  induction path with
  | stop C => simp [terminalCircle, deletions]
  | @step C d hr i tail ih =>
    have rank_eq := tail.terminalCircle_rank
    have contract_eq := C.rank_contract i hr
    have large : 3 ≤ C.rank := by change 2 ≤ tail.terminalCircle.rank at visible; omega
    rw [terminalCircle, ih (inv.contract i hr large) visible,
      inv.homogeneous_contract_iff E equiv i hr]
    simp only [deletions, List.mem_cons, forall_eq_or_imp, and_assoc]

theorem terminalCircle_packetAtoms_eq_of_same_survivors
    {C : MarkedCircle α} {d₁ d₂ : ℕ} (first : Schedule C d₁) (second : Schedule C d₂)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank)
    (same : C.boundaries \ first.deletions.toFinset =
      C.boundaries \ second.deletions.toFinset) :
    first.terminalCircle.packetAtoms = second.terminalCircle.packetAtoms := by
  have deletions : ∀ a, a ∈ first.deletions ↔ a ∈ second.deletions := by
    intro a
    have eq := Finset.ext_iff.mp same a
    simp only [Finset.mem_sdiff, List.mem_toFinset] at eq
    have left := first.deletions_mem a
    have right := second.deletions_mem a
    tauto
  have constraints : ∀ (E : α → α → Prop) (equiv : Equivalence E),
      MarkedCircle.Homogeneous E first.terminalCircle ↔
        MarkedCircle.Homogeneous E second.terminalCircle := by
    intro E equiv
    rw [first.homogeneous_terminalCircle_iff C.boundarySuccessorInvariant_initial visible₁ E equiv,
      second.homogeneous_terminalCircle_iff C.boundarySuccessorInvariant_initial visible₂ E equiv]
    simp only [deletions]
  apply MarkedCircle.packetAtoms_eq_of_mutual_homogeneous
    first.terminalCircle second.terminalCircle
    (first.terminalCircle_atomUnion.trans second.terminalCircle_atomUnion.symm)
  · exact (constraints _ second.terminalCircle.packetProfileEq_equivalence).mpr
      second.terminalCircle.homogeneous_packetProfileEq
  · exact (constraints _ first.terminalCircle.packetProfileEq_equivalence).mp
      first.terminalCircle.homogeneous_packetProfileEq

/-- At visible rank, survivors and literal terminal packet contents determine
one another. Rotation of the indexed circle is deliberately not equated. -/
theorem terminalCircle_packetAtoms_eq_iff_same_survivors
    {C : MarkedCircle α} {d₁ d₂ : ℕ} (first : Schedule C d₁) (second : Schedule C d₂)
    (visible₁ : 2 ≤ first.terminalCircle.rank) (visible₂ : 2 ≤ second.terminalCircle.rank) :
    first.terminalCircle.packetAtoms = second.terminalCircle.packetAtoms ↔
      C.boundaries \ first.deletions.toFinset = C.boundaries \ second.deletions.toFinset :=
  ⟨first.terminalCircle_survivors_eq_of_packetAtoms_eq second visible₁ visible₂,
    first.terminalCircle_packetAtoms_eq_of_same_survivors second visible₁ visible₂⟩

end Schedule

end FusionLogEnumeration
