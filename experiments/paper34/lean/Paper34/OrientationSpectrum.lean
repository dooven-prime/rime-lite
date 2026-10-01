import Mathlib.Data.Finset.Card
import Mathlib.Data.Nat.Choose.Basic

/-!
# Orientation spectra and pair-level non-descent

The manuscript's geometric theorem supplies two disjoint survivor families.
This file checks the exact finite-set consequences and the logical statement
that two branches with equal pair data but unequal survivor data cannot factor
through the pair-level observable.
-/

namespace Rime.Paper34

structure DihedralSpectrum (Survivor : Type*) [DecidableEq Survivor] where
  positive : Finset Survivor
  negative : Finset Survivor
  disjoint : Disjoint positive negative
  negative_nonempty : negative.Nonempty
  equal_card : negative.card = positive.card

namespace DihedralSpectrum

variable {Survivor : Type*} [DecidableEq Survivor]

def rotation (spectrum : DihedralSpectrum Survivor) : Finset Survivor :=
  spectrum.positive

def reflection (spectrum : DihedralSpectrum Survivor) : Finset Survivor :=
  spectrum.positive ∪ spectrum.negative

theorem rotation_card (spectrum : DihedralSpectrum Survivor) :
    spectrum.rotation.card = spectrum.positive.card := by
  rfl

theorem reflection_card (spectrum : DihedralSpectrum Survivor) :
    spectrum.reflection.card = 2 * spectrum.positive.card := by
  rw [reflection, Finset.card_union_of_disjoint spectrum.disjoint]
  rw [spectrum.equal_card]
  omega

theorem rotation_ne_reflection (spectrum : DihedralSpectrum Survivor) :
    spectrum.rotation ≠ spectrum.reflection := by
  obtain ⟨q, hqneg⟩ := spectrum.negative_nonempty
  intro heq
  have hqrefl : q ∈ spectrum.reflection := by
    simp [reflection, hqneg]
  have hqpos : q ∈ spectrum.positive := by
    rw [← rotation, heq]
    exact hqrefl
  exact (Finset.disjoint_left.mp spectrum.disjoint) hqpos hqneg

theorem rotation_card_choose
    (spectrum : DihedralSpectrum Survivor) {n : Nat}
    (hcard : spectrum.positive.card = Nat.choose (n - 2) 3) :
    spectrum.rotation.card = Nat.choose (n - 2) 3 := by
  simpa [rotation] using hcard

theorem reflection_card_choose
    (spectrum : DihedralSpectrum Survivor) {n : Nat}
    (hcard : spectrum.positive.card = Nat.choose (n - 2) 3) :
    spectrum.reflection.card = 2 * Nat.choose (n - 2) 3 := by
  rw [spectrum.reflection_card, hcard]

end DihedralSpectrum

/-- Equal quotient data together with unequal outputs forbid functional
descent through that quotient. -/
theorem no_descent_of_equal_view_ne_output
    {Branch View Output : Type*}
    (view : Branch → View) (output : Branch → Output)
    {left right : Branch}
    (hview : view left = view right)
    (houtput : output left ≠ output right) :
    ¬ ∃ descend : View → Output, output = descend ∘ view := by
  rintro ⟨descend, hfactor⟩
  apply houtput
  calc
    output left = descend (view left) := congrFun hfactor left
    _ = descend (view right) := congrArg descend hview
    _ = output right := (congrFun hfactor right).symm

inductive DihedralBranch
  | rotation
  | reflection
  deriving DecidableEq

def pairView (_ : DihedralBranch) : Unit := ()

variable {Survivor : Type*} [DecidableEq Survivor]

def survivorView (spectrum : DihedralSpectrum Survivor) :
    DihedralBranch → Finset Survivor
  | .rotation => spectrum.rotation
  | .reflection => spectrum.reflection

/-- The rotation/reflection control has identical pair data but no survivor
map can descend through that pair-level view. -/
theorem no_pair_level_survivor_descent
    (spectrum : DihedralSpectrum Survivor) :
    ¬ ∃ descend : Unit → Finset Survivor,
      survivorView spectrum = descend ∘ pairView := by
  apply no_descent_of_equal_view_ne_output
      pairView (survivorView spectrum)
      (left := DihedralBranch.rotation)
      (right := DihedralBranch.reflection)
  · rfl
  · exact spectrum.rotation_ne_reflection

end Rime.Paper34
