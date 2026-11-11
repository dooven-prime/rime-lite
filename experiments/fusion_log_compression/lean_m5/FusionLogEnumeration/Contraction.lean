import FusionLogEnumeration.MarkedCircle

namespace FusionLogEnumeration

open RegisteredAbsorptionChains

variable {α : Type*} [DecidableEq α]

namespace MarkedCircle

structure FrontSplit (C : MarkedCircle α) where
  left : MarkedPacket α
  right : MarkedPacket α
  rest : List (MarkedPacket α)
  eq : C.packets = left :: right :: rest

def frontSplit (C : MarkedCircle α) (hr : 2 ≤ C.rank) : FrontSplit C := by
  cases eq : C.packets with
  | nil => simp [rank, eq] at hr
  | cons A tail =>
      cases tail with
      | nil => simp [rank, eq] at hr
      | cons B rest => exact ⟨A, B, rest, eq⟩

def frontAt (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    FrontSplit (C.rotate i.val) := frontSplit _ (by simpa using hr)

theorem frontAt_left (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.frontAt i hr).left = C.packets[i] := by
  have iLt : i.val < C.packets.length := by
    simpa [rank] using i.isLt
  have eq := (C.frontAt i hr).eq
  change C.packets.rotate i.val = _ at eq
  have head := congrArg List.head? eq
  have rotated := List.head?_rotate (l := C.packets) (n := i.val) iLt
  apply Option.some.inj
  change some (C.frontAt i hr).left = some (C.packets.get ⟨i.val, iLt⟩)
  rw [List.get_eq_getElem, ← List.getElem?_eq_getElem iLt]
  exact head.symm.trans rotated

def mergeFront (C : MarkedCircle α) (f : FrontSplit C) : MarkedCircle α where
  packets := ⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
    Finset.mem_union_right _ f.right.boundary_mem⟩ :: f.rest
  nonempty := List.cons_ne_nil _ _
  disjoint := by
    have old := C.disjoint
    rw [f.eq, List.pairwise_cons, List.pairwise_cons] at old
    rw [List.pairwise_cons]
    refine ⟨?_, old.2.2⟩
    intro p member
    exact Finset.disjoint_union_left.mpr
      ⟨old.1 p (by simp [member]), old.2.1 p member⟩

def contract (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) : MarkedCircle α :=
  mergeFront (C.rotate i.val) (C.frontAt i hr)

def event (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) : FusionRecord α :=
  let f := C.frontAt i hr
  ⟨f.left.atoms, f.right.atoms, f.left.atoms ∪ f.right.atoms⟩

def deleted (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) : α :=
  (C.frontAt i hr).left.boundary

theorem deleted_eq_get (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    C.deleted i hr = C.packets[i].boundary := by
  simp only [deleted, frontAt_left]

theorem event_left (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.event i hr).left = C.packets[i].atoms := by
  simp only [event, frontAt_left]

theorem deleted_mem (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    C.deleted i hr ∈ C.boundaries := by
  rw [deleted_eq_get]
  exact (C.boundaryEquiv i).property

theorem deleted_injective (C : MarkedCircle α) (hr : 2 ≤ C.rank) :
    Function.Injective (fun i : Fin C.rank => C.deleted i hr) := by
  simpa only [deleted_eq_get] using C.boundary_injective

theorem event_injective (C : MarkedCircle α) (hr : 2 ≤ C.rank) :
    Function.Injective (fun i : Fin C.rank => C.event i hr) := by
  intro i j eq
  apply C.atoms_injective
  simpa only [event_left] using congrArg FusionRecord.left eq

theorem rank_contract (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.contract i hr).rank + 1 = C.rank := by
  have eq := congrArg List.length (C.frontAt i hr).eq
  simp only [rotate, List.length_rotate, List.length_cons] at eq
  change (C.frontAt i hr).rest.length + 1 + 1 = C.packets.length
  omega

theorem boundaries_contract (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.contract i hr).boundaries = C.boundaries.erase (C.deleted i hr) := by
  let f := C.frontAt i hr
  have noDup := (C.rotate i.val).boundary_nodup
  rw [f.eq] at noDup
  simp only [List.map_cons, List.nodup_cons] at noDup
  have unchanged : C.boundaries =
      insert f.left.boundary (f.right.boundary :: f.rest.map (·.boundary)).toFinset := by
    rw [← C.boundaries_rotate i.val]
    simp only [boundaries, f.eq, List.map_cons, List.toFinset_cons]
  rw [unchanged]
  change (f.right.boundary :: f.rest.map (·.boundary)).toFinset =
    (insert f.left.boundary
      (f.right.boundary :: f.rest.map (·.boundary)).toFinset).erase f.left.boundary
  rw [Finset.erase_insert]
  simpa using noDup.1

end MarkedCircle

end FusionLogEnumeration
