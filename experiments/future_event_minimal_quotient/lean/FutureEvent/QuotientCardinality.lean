import FutureEvent.FutureQuotient

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

abbrev RegisterableGeneratedStates (n : ℕ) [NeZero n] :=
  {s : GeneratedState n // PairRegisterable s.val}

def registerableStatePlacement (s : RegisterableGeneratedStates n) : RegisterablePlacements n :=
  ⟨s.val.val.placed, s.val.val, s.val.property, s.property, rfl⟩

/-- Before registration, actual generated states have neither an origin nor
an old selected chain, so forgetting to placement loses no state identity. -/
theorem registerableStatePlacement_injective :
    Function.Injective (registerableStatePlacement (n := n)) := by
  intro x y h
  apply Subtype.ext
  apply Subtype.ext
  exact generated_unregistered_same_placement_eq x.val.val y.val.val
    x.val.property y.val.property x.property.1 y.property.1 (congrArg Subtype.val h)

theorem registerableStatePlacement_surjective :
    Function.Surjective (registerableStatePlacement (n := n)) := by
  intro P
  obtain ⟨s, hg, hr, hp⟩ := P.property
  exact ⟨⟨⟨s, hg⟩, hr⟩, Subtype.ext hp⟩

noncomputable def registerableStatesEquivPlacements :
    RegisterableGeneratedStates n ≃ RegisterablePlacements n :=
  Equiv.ofBijective registerableStatePlacement
    ⟨registerableStatePlacement_injective, registerableStatePlacement_surjective⟩

theorem finite_registerableGeneratedStates : Finite (RegisterableGeneratedStates n) :=
  Finite.of_injective registerableStatePlacement registerableStatePlacement_injective

theorem card_registerableGeneratedStates :
    Nat.card (RegisterableGeneratedStates n) = Nat.card (RegisterablePlacements n) :=
  Nat.card_congr registerableStatesEquivPlacements

/-- The paper's structural formula, with R counting actual registerable
states and A counting literal registered nonterminal placements. -/
theorem card_futureQuotient_actual_regions (hn : 3 ≤ n) :
    Nat.card (FutureQuotient n) =
      1 + Nat.card (RegisterableGeneratedStates n) +
        Nat.card (RegisteredNonterminalPlacements n) := by
  rw [card_registerableGeneratedStates]
  exact card_futureQuotient hn

end FutureEvent
