import FusionLogEnumeration.Schedules
import FusionLogEnumeration.EndpointGeometry

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

namespace MarkedCircle

/-- The union of the atom sets carried by the current marked packets. -/
def atomUnion (C : MarkedCircle α) : Finset α :=
  C.packets.toFinset.biUnion MarkedPacket.atoms

/-- Every atom in `U` belongs to one of the circle's current packets. -/
def Covers (C : MarkedCircle α) (U : Finset α) : Prop :=
  ∀ a, a ∈ U → ∃ p ∈ C.packets, a ∈ p.atoms

/-- Every atom of the ambient type is represented by a current packet. -/
def CoversAll (C : MarkedCircle α) : Prop :=
  ∀ a, ∃ p ∈ C.packets, a ∈ p.atoms

theorem atomUnion_covers (C : MarkedCircle α) : C.Covers C.atomUnion := by
  intro a ha
  obtain ⟨p, hp, hpa⟩ := Finset.mem_biUnion.mp ha
  exact ⟨p, List.mem_toFinset.mp hp, hpa⟩

theorem covers_contract (C : MarkedCircle α) (U : Finset α)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) (covers : C.Covers U) :
    (C.contract i hr).Covers U := by
  intro a ha
  obtain ⟨p, hp, hpa⟩ := covers a ha
  let f := C.frontAt i hr
  have hpRot : p ∈ (C.rotate i.val).packets :=
    (C.packets.rotate_perm i.val).mem_iff.mpr hp
  rw [f.eq] at hpRot
  rcases List.mem_cons.mp hpRot with hleft | htail
  · subst p
    refine ⟨⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
      Finset.mem_union_right _ f.right.boundary_mem⟩, ?_, ?_⟩
    · simp [MarkedCircle.contract, MarkedCircle.mergeFront, f]
    · exact Finset.mem_union_left _ hpa
  · rcases List.mem_cons.mp htail with hright | hrest
    · subst p
      refine ⟨⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
        Finset.mem_union_right _ f.right.boundary_mem⟩, ?_, ?_⟩
      · simp [MarkedCircle.contract, MarkedCircle.mergeFront, f]
      · exact Finset.mem_union_right _ hpa
    · exact ⟨p, by
        simp [MarkedCircle.contract, MarkedCircle.mergeFront, f, hrest], hpa⟩

theorem coversAll_contract (C : MarkedCircle α)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) (covers : C.CoversAll) :
    (C.contract i hr).CoversAll := by
  intro a
  obtain ⟨p, hp, hpa⟩ := covers a
  let f := C.frontAt i hr
  have hpRot : p ∈ (C.rotate i.val).packets :=
    (C.packets.rotate_perm i.val).mem_iff.mpr hp
  rw [f.eq] at hpRot
  rcases List.mem_cons.mp hpRot with hleft | htail
  · subst p
    refine ⟨⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
      Finset.mem_union_right _ f.right.boundary_mem⟩, ?_, ?_⟩
    · simp [MarkedCircle.contract, MarkedCircle.mergeFront, f]
    · exact Finset.mem_union_left _ hpa
  · rcases List.mem_cons.mp htail with hright | hrest
    · subst p
      refine ⟨⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
        Finset.mem_union_right _ f.right.boundary_mem⟩, ?_, ?_⟩
      · simp [MarkedCircle.contract, MarkedCircle.mergeFront, f]
      · exact Finset.mem_union_right _ hpa
    · exact ⟨p, by
        simp [MarkedCircle.contract, MarkedCircle.mergeFront, f, hrest], hpa⟩

end MarkedCircle

namespace Schedule

/-- The deterministic terminal packet circle of a contraction schedule. -/
def terminalCircle : {C : MarkedCircle α} → {d : ℕ} →
    Schedule C d → MarkedCircle α
  | _, _, .stop C => C
  | _, _, .step _ _ tail => tail.terminalCircle

instance terminalCircle_rank_neZero {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) : NeZero path.terminalCircle.rank :=
  ⟨Nat.ne_of_gt path.terminalCircle.rank_pos⟩

theorem terminalCircle_rank {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) : path.terminalCircle.rank + d = C.rank := by
  induction path with
  | stop C => rfl
  | @step C d hr i tail ih =>
      have hc := C.rank_contract i hr
      simp only [terminalCircle]
      omega

/-- The terminal circle exposes exactly the original boundary labels not
deleted by the schedule. This is the schedule-side survivor identity; it does
not yet assert that a literal endpoint can recover those labels. -/
theorem terminalCircle_boundaries_eq_survivors {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) :
    path.terminalCircle.boundaries = C.boundaries \ path.deletions.toFinset := by
  induction path with
  | stop C => simp [terminalCircle, Schedule.deletions]
  | @step C d hr i tail ih =>
      rw [terminalCircle, ih, C.boundaries_contract]
      ext a
      simp [Schedule.deletions, Finset.mem_sdiff, Finset.mem_erase,
        Finset.mem_insert, and_assoc, and_left_comm, and_comm]

theorem terminalCircle_covers {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) (U : Finset α) (covers : C.Covers U) :
    path.terminalCircle.Covers U := by
  induction path with
  | stop C => exact covers
  | @step C d hr i tail ih =>
      exact ih (C.covers_contract U i hr covers)

theorem terminalCircle_coversAll {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) (covers : C.CoversAll) :
    path.terminalCircle.CoversAll := by
  induction path with
  | stop C => exact covers
  | @step C d hr i tail ih =>
      exact ih (C.coversAll_contract i hr covers)

/-- The M5 terminal packet list, indexed by its positive cyclic order, is a
literal packet cycle on exactly the atoms present in the initial circle. -/
noncomputable def terminalLiteralCycle {C : MarkedCircle α} {d : ℕ}
    (path : Schedule C d) (covers : C.CoversAll) :
    LiteralPacketCycle path.terminalCircle.rank α := by
  classical
  let T := path.terminalCircle
  letI : NeZero T.rank := ⟨Nat.ne_of_gt T.rank_pos⟩
  let blocks : ZMod T.rank → Finset α :=
    fun i => T.packets[(ZMod.finEquiv T.rank).symm i].atoms
  refine ⟨blocks, ?_, ?_, ?_⟩
  · intro i
    exact ⟨_, (T.packets[(ZMod.finEquiv T.rank).symm i]).boundary_mem⟩
  · intro i j hij
    let fi := (ZMod.finEquiv T.rank).symm i
    let fj := (ZMod.finEquiv T.rank).symm j
    have hne : fi ≠ fj := by
      intro h
      apply hij
      exact (ZMod.finEquiv T.rank).symm.injective h
    have disjoint : Disjoint T.packets[fi].atoms T.packets[fj].atoms := by
      rcases lt_or_gt_of_ne (Fin.val_ne_of_ne hne) with hlt | hgt
      · exact List.pairwise_iff_getElem.mp T.disjoint
          fi.val fj.val fi.isLt fj.isLt hlt
      · exact (List.pairwise_iff_getElem.mp T.disjoint
          fj.val fi.val fj.isLt fi.isLt hgt).symm
    exact disjoint
  · intro a
    obtain ⟨p, hp, ha⟩ := path.terminalCircle_coversAll covers a
    obtain ⟨k, hk, rfl⟩ := List.mem_iff_getElem.mp hp
    let fk : Fin T.rank := ⟨k, by simpa [T, MarkedCircle.rank] using hk⟩
    refine ⟨ZMod.finEquiv T.rank fk, ?_⟩
    simpa [blocks, fk] using ha

end Schedule

end FusionLogEnumeration
