import Mathlib.GroupTheory.Coset.Basic

/-!
# Left-coset type boundary

Paper XXXV uses `K_a^{ord}/C₅` as a left-coset space. This file gives that
notation an explicit Lean type which does not require the subgroup to be
normal and therefore does not silently promote the space to a quotient group.
-/

namespace Rime.Paper35

universe u

/-- Left cosets of `H` in `G`, represented by the left-coset setoid. No
normality hypothesis is present. -/
abbrev LeftCosetSpace (G : Type u) [Group G] (H : Subgroup G) :=
  Quotient (QuotientGroup.leftRel H)

def leftCosetClass {G : Type u} [Group G] (H : Subgroup G) (g : G) :
    LeftCosetSpace G H :=
  Quotient.mk'' g

/-- Equality in the left-coset space is exactly left-coset equivalence. -/
theorem leftCosetClass_eq_iff
    {G : Type u} [Group G] (H : Subgroup G) (x y : G) :
    leftCosetClass H x = leftCosetClass H y ↔ x⁻¹ * y ∈ H := by
  change Quotient.mk'' x = Quotient.mk'' y ↔ _
  rw [Quotient.eq'', QuotientGroup.leftRel_apply]

end Rime.Paper35
