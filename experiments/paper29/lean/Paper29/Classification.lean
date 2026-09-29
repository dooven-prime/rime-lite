import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.Prod
import Mathlib.Data.Nat.Choose.Basic

/-!
# Classification consequences and claim boundary

The all-n geometric classification is proved in the manuscript.  This file
checks two consequences after an exact classification equivalence is supplied:
the frontier product count and source-block independence through a shared
incidence carrier.  It also records that raw nonemptiness alone cannot create
a typed origin.
-/

namespace Rime.Paper29

variable {n : Nat}
variable {Frontier : Type u} {FusedPair : Type v}
variable {SurvivorPlacement : Type w}

structure FrontierClassification
    (n : Nat) (Frontier : Type u) (FusedPair : Type v)
    (SurvivorPlacement : Type w)
    [Fintype Frontier] [Fintype FusedPair] [Fintype SurvivorPlacement] where
  split : Frontier ≃ FusedPair × SurvivorPlacement
  fused_card : Fintype.card FusedPair = 5
  survivor_card : Fintype.card SurvivorPlacement = Nat.choose (n - 2) 3

/-- The exact fused-pair/survivor classification gives the manuscript count. -/
theorem frontier_card_of_classification
    [Fintype Frontier] [Fintype FusedPair] [Fintype SurvivorPlacement]
    (classification :
      FrontierClassification n Frontier FusedPair SurvivorPlacement) :
    Fintype.card Frontier = 5 * Nat.choose (n - 2) 3 := by
  calc
    Fintype.card Frontier = Fintype.card (FusedPair × SurvivorPlacement) :=
      Fintype.card_congr classification.split
    _ = Fintype.card FusedPair * Fintype.card SurvivorPlacement := by
      simp
    _ = 5 * Nat.choose (n - 2) 3 := by
      rw [classification.fused_card, classification.survivor_card]

/-- Two endpoint types decoded from one incidence type are equivalent. -/
def endpointEquivOfCommonIncidence
    {Incidence : Type u} {LeftEndpoint : Type v} {RightEndpoint : Type w}
    (left : Incidence ≃ LeftEndpoint)
    (right : Incidence ≃ RightEndpoint) :
    LeftEndpoint ≃ RightEndpoint :=
  left.symm.trans right

theorem endpointEquivOfCommonIncidence_apply
    {Incidence : Type u} {LeftEndpoint : Type v} {RightEndpoint : Type w}
    (left : Incidence ≃ LeftEndpoint)
    (right : Incidence ≃ RightEndpoint)
    (endpoint : LeftEndpoint) :
    endpointEquivOfCommonIncidence left right endpoint =
      right (left.symm endpoint) := by
  rfl

/-- There is no unconditional promotion from a raw witness to a typed one. -/
theorem no_unconditional_raw_to_typed :
    ¬ (∀ (Raw Typed : Type), Nonempty Raw → Nonempty Typed) := by
  intro promote
  obtain ⟨typed⟩ := promote Unit Empty ⟨()⟩
  exact nomatch typed

/-- An explicit bridge, rather than raw existence alone, supplies typed data. -/
theorem typed_origin_of_explicit_bridge
    (bridge : Raw → Typed) (raw : Nonempty Raw) :
    Nonempty Typed := by
  obtain ⟨witness⟩ := raw
  exact ⟨bridge witness⟩

end Rime.Paper29
