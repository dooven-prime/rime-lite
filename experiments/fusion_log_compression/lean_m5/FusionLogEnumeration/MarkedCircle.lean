import RegisteredAbsorptionChains.Execution
import Mathlib.Data.List.Rotate
import Mathlib.Data.Fintype.CardEmbedding
import Mathlib.Tactic

namespace FusionLogEnumeration

open RegisteredAbsorptionChains

variable {α : Type*} [DecidableEq α]

/-- A packet carries its last original boundary label. The list is a chosen
linear representative of its positive cyclic order, not a physical placement. -/
structure MarkedPacket (α : Type*) where
  boundary : α
  atoms : Finset α
  boundary_mem : boundary ∈ atoms

deriving instance DecidableEq for MarkedPacket

structure MarkedCircle (α : Type*) [DecidableEq α] where
  packets : List (MarkedPacket α)
  nonempty : packets ≠ []
  disjoint : packets.Pairwise (fun p q => Disjoint p.atoms q.atoms)

namespace MarkedCircle

def rank (C : MarkedCircle α) : ℕ := C.packets.length

def boundaries (C : MarkedCircle α) : Finset α := (C.packets.map (·.boundary)).toFinset

theorem rank_pos (C : MarkedCircle α) : 0 < C.rank := List.length_pos_iff.mpr C.nonempty

theorem atoms_injective (C : MarkedCircle α) :
    Function.Injective (fun i : Fin C.rank => C.packets[i].atoms) := by
  intro i j same
  by_contra ne
  have dij : Disjoint C.packets[i].atoms C.packets[j].atoms := by
    rcases lt_or_gt_of_ne (Fin.val_ne_of_ne ne) with h | h
    · exact List.pairwise_iff_getElem.mp C.disjoint i.val j.val i.isLt j.isLt h
    · exact (List.pairwise_iff_getElem.mp C.disjoint j.val i.val j.isLt i.isLt h).symm
  have member := C.packets[i].boundary_mem
  exact (Finset.disjoint_left.mp dij) member (by simpa only [same] using member)

theorem boundary_injective (C : MarkedCircle α) :
    Function.Injective (fun i : Fin C.rank => C.packets[i].boundary) := by
  intro i j same
  by_contra ne
  have dij : Disjoint C.packets[i].atoms C.packets[j].atoms := by
    rcases lt_or_gt_of_ne (Fin.val_ne_of_ne ne) with h | h
    · exact List.pairwise_iff_getElem.mp C.disjoint i.val j.val i.isLt j.isLt h
    · exact (List.pairwise_iff_getElem.mp C.disjoint j.val i.val j.isLt i.isLt h).symm
  exact (Finset.disjoint_left.mp dij) C.packets[i].boundary_mem
    (by simpa only [same] using C.packets[j].boundary_mem)

theorem boundary_nodup (C : MarkedCircle α) : (C.packets.map (·.boundary)).Nodup := by
  rw [List.nodup_iff_injective_get]
  intro i j eq
  have h : (⟨i.val, by simpa [rank] using i.isLt⟩ : Fin C.rank) =
      ⟨j.val, by simpa [rank] using j.isLt⟩ := C.boundary_injective (by simpa using eq)
  exact Fin.ext (congrArg (fun k : Fin C.rank => k.val) h)

theorem card_boundaries (C : MarkedCircle α) : C.boundaries.card = C.rank := by
  rw [boundaries, List.toFinset_card_of_nodup C.boundary_nodup, List.length_map]
  rfl

noncomputable def boundaryEquiv (C : MarkedCircle α) : Fin C.rank ≃ C.boundaries := by
  apply Equiv.ofBijective (fun i => ⟨C.packets[i].boundary, by
    simp only [boundaries, List.mem_toFinset, List.mem_map]
    exact ⟨C.packets[i], List.getElem_mem i.isLt, rfl⟩⟩)
  constructor
  · intro i j eq
    exact C.boundary_injective (congrArg Subtype.val eq)
  · intro a
    obtain ⟨p, member, same⟩ := List.mem_map.mp (List.mem_toFinset.mp a.property)
    obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp member
    exact ⟨⟨i, hi⟩, Subtype.ext same⟩

def rotate (C : MarkedCircle α) (i : ℕ) : MarkedCircle α where
  packets := C.packets.rotate i
  nonempty := by simpa using C.nonempty
  disjoint := (C.packets.rotate_perm i).pairwise_iff (by
    intro p q h
    exact h.symm) |>.mpr C.disjoint

@[simp] theorem rank_rotate (C : MarkedCircle α) (i : ℕ) : (C.rotate i).rank = C.rank := by
  simp [rank, rotate]

@[simp] theorem boundaries_rotate (C : MarkedCircle α) (i : ℕ) :
    (C.rotate i).boundaries = C.boundaries := by
  ext a
  simp [boundaries, rotate, List.mem_map]

end MarkedCircle

end FusionLogEnumeration
