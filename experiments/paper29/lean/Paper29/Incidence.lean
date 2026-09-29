import Std

/-!
# Boundary incidence decomposition

The manuscript splits an attained boundary map into one fused source pair and
the placement of the three survivors.  This file checks the extensional core:
once the fused fiber is fixed and maps to the root, equality on all survivors
determines the whole incidence map.
-/

namespace Rime.Paper29

abbrev Incidence (Lineage : Type u) (Coord : Type v) := Lineage → Coord

/-- A fixed fused fiber and the survivor restriction determine incidence. -/
theorem incidence_ext_of_fused_and_survivors
    {Lineage : Type u} {Coord : Type v}
    (root : Coord) (fused : Lineage → Prop)
    (left right : Incidence Lineage Coord)
    (left_fused : ∀ q, fused q → left q = root)
    (right_fused : ∀ q, fused q → right q = root)
    (survivors : ∀ q, ¬ fused q → left q = right q) :
    left = right := by
  funext q
  by_cases hq : fused q
  · exact (left_fused q hq).trans (right_fused q hq).symm
  · exact survivors q hq

/-- The fused fiber can be read back from an incidence map and a root. -/
def FusedFiber (root : Coord) (incidence : Incidence Lineage Coord) :
    Lineage → Prop :=
  fun q => incidence q = root

theorem fusedFiber_ext
    {Lineage : Type u} {Coord : Type v}
    (root : Coord) (left right : Incidence Lineage Coord)
    (h : left = right) :
    FusedFiber root left = FusedFiber root right := by
  cases h
  rfl

end Rime.Paper29
