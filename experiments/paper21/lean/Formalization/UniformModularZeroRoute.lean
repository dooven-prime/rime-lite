import Mathlib

/-!
# Uniform modular zero-route classification: finite shape core

This file formalizes the combinatorial core of the fixed modular contract:

* nine ordered labels;
* five Boolean-supported two-sector route shapes;
* the labelled zero-route decomposition `4 + 5 + 5 = 14`.

The file deliberately does not identify an abstract group presentation with a
route signature. `UniformModularZeroRouteField.lean` supplies the separate
`P^1(F)` Mobius evaluation and pole-semantics layer.
-/

namespace Formalization

namespace UniformModularZeroRoute

inductive Label where
  | S
  | R
  | RInv
  deriving DecidableEq, Repr

instance : Fintype Label where
  elems := {.S, .R, .RInv}
  complete := by
    intro label
    cases label <;> simp
abbrev Sector := Fin 2
abbrev Shape := Sector × Sector × Sector
abbrev LabelPair := Label × Label
abbrev Route := LabelPair × Shape

def labelS : Label := .S
def labelR : Label := .R
def labelRInv : Label := .RInv

def shapeMiddleInfinity : Shape := (1, 0, 1)
def shapeSourceInfinityTargetInfinity : Shape := (0, 1, 0)
def shapeSourceInfinityTargetFinite : Shape := (1, 1, 0)
def shapeSourceFiniteTargetInfinity : Shape := (0, 1, 1)
def shapeAllFinite : Shape := (1, 1, 1)

def candidateShapes : Finset Shape :=
  {shapeMiddleInfinity,
    shapeSourceInfinityTargetInfinity,
    shapeSourceInfinityTargetFinite,
    shapeSourceFiniteTargetInfinity,
    shapeAllFinite}

def zeroWordsSourceInfinityTargetInfinity : Finset LabelPair :=
  {(labelS, labelR),
    (labelR, labelR),
    (labelRInv, labelS),
    (labelRInv, labelRInv)}

def zeroWordsSourceInfinityTargetFinite : Finset LabelPair :=
  {(labelS, labelS),
    (labelS, labelRInv),
    (labelR, labelS),
    (labelR, labelRInv),
    (labelRInv, labelR)}

def zeroWordsSourceFiniteTargetInfinity : Finset LabelPair :=
  zeroWordsSourceInfinityTargetFinite

def orderedLabelPairs : Finset LabelPair := Finset.univ

def candidateRoutes : Finset Route :=
  (orderedLabelPairs.product candidateShapes)

def zeroRoutes : Finset Route :=
  ((zeroWordsSourceInfinityTargetInfinity.product
      ({shapeSourceInfinityTargetInfinity} : Finset Shape)) ∪
    (zeroWordsSourceInfinityTargetFinite.product
      ({shapeSourceInfinityTargetFinite} : Finset Shape))) ∪
    (zeroWordsSourceFiniteTargetInfinity.product
      ({shapeSourceFiniteTargetInfinity} : Finset Shape))

def nonzeroShapes : Finset Shape :=
  {shapeMiddleInfinity, shapeAllFinite}

def potentiallyZeroShapes : Finset Shape :=
  {shapeSourceInfinityTargetInfinity,
    shapeSourceInfinityTargetFinite,
    shapeSourceFiniteTargetInfinity}

theorem candidate_shapes_are_exact : candidateShapes.card = 5 := by
  native_decide

theorem ordered_label_pairs_are_exact : orderedLabelPairs.card = 9 := by
  native_decide

theorem candidate_route_count : candidateRoutes.card = 45 := by
  native_decide

theorem zero_shape_contribution_source_infinity_target_infinity :
    zeroWordsSourceInfinityTargetInfinity.card = 4 := by
  native_decide

theorem zero_shape_contribution_source_infinity_target_finite :
    zeroWordsSourceInfinityTargetFinite.card = 5 := by
  native_decide

theorem zero_shape_contribution_source_finite_target_infinity :
    zeroWordsSourceFiniteTargetInfinity.card = 5 := by
  native_decide

theorem nonzero_shapes_are_exact : nonzeroShapes.card = 2 := by
  native_decide

theorem potentially_zero_shapes_are_exact : potentiallyZeroShapes.card = 3 := by
  native_decide

theorem zero_route_count : zeroRoutes.card = 14 := by
  native_decide

theorem zero_routes_are_candidates : zeroRoutes ⊆ candidateRoutes := by
  native_decide

theorem zero_count_decomposition :
    zeroWordsSourceInfinityTargetInfinity.card
      + zeroWordsSourceInfinityTargetFinite.card
      + zeroWordsSourceFiniteTargetInfinity.card = 14 := by
  native_decide

structure FixedModularRouteContract (p : Nat) where
  oddPrime : Nat.Prime p
  carrierTag : String
  alphabetOrder : List String
  markedPartitionTag : String
  routeSemanticsTag : String

def fixedContract (p : Nat) (hp : Nat.Prime p) : FixedModularRouteContract p :=
  {
    oddPrime := hp
    carrierTag := "P^1(F_p)"
    alphabetOrder := ["S", "R", "R_inv"]
    markedPartitionTag := "{infinity} disjoint union F_p"
    routeSemanticsTag := "ordered two-step Boolean-supported route semantics"
  }

theorem fixed_contract_has_declared_scope {p : Nat} (hp : Nat.Prime p) :
    (fixedContract p hp).carrierTag = "P^1(F_p)"
      ∧ (fixedContract p hp).alphabetOrder = ["S", "R", "R_inv"]
      ∧ (fixedContract p hp).markedPartitionTag = "{infinity} disjoint union F_p"
      ∧ (fixedContract p hp).routeSemanticsTag =
        "ordered two-step Boolean-supported route semantics" := by
  simp [fixedContract]

theorem uniform_modular_zero_route_shape_core {p : Nat} (hp : Nat.Prime p) :
    Nat.Prime p
      ∧ candidateRoutes.card = 45
      ∧ zeroRoutes.card = 14
      ∧ zeroRoutes ⊆ candidateRoutes := by
  exact ⟨hp, candidate_route_count, zero_route_count, zero_routes_are_candidates⟩

end UniformModularZeroRoute

end Formalization
