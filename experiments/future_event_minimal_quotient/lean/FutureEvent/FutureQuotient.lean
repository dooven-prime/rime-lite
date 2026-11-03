import FutureEvent.FutureClassification
import Mathlib.SetTheory.Cardinal.Finite

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- A full execution with an actual singleton-seed provenance, without a
cutoff on its history word. -/
abbrev GeneratedState (n : ℕ) [NeZero n] :=
  {s : Execution n (ZMod n) // PairGenerated s}

def futureSetoid (n : ℕ) [NeZero n] : Setoid (GeneratedState n) where
  r x y := FutureEquivalent {0, 1} x.val y.val
  iseqv := ⟨fun x => futureEquivalent_refl {0, 1} x.val,
    fun h word => (h word).symm, fun hxy hyz word => (hxy word).trans (hyz word)⟩

abbrev FutureQuotient (n : ℕ) [NeZero n] := Quotient (futureSetoid n)

def generatedRun (x : GeneratedState n) (word : List Letter) : GeneratedState n :=
  ⟨run {0, 1} x.val word, pairGenerated_run x.val word x.property⟩

def quotientRun (word : List Letter) : FutureQuotient n → FutureQuotient n :=
  Quotient.map (fun x => generatedRun x word) (fun x y h =>
    futureEquivalent_right_congruent {0, 1} x.val y.val h word)

theorem quotientRun_mk (word : List Letter) (x : GeneratedState n) :
    quotientRun word (Quotient.mk (futureSetoid n) x) =
      Quotient.mk (futureSetoid n) (generatedRun x word) := rfl

theorem quotientRun_append (u v : List Letter) (x : FutureQuotient n) :
    quotientRun (u ++ v) x = quotientRun v (quotientRun u x) := by
  refine Quotient.inductionOn x ?_
  intro s
  rw [quotientRun_mk, quotientRun_mk, quotientRun_mk]
  apply congrArg (Quotient.mk (futureSetoid n))
  exact Subtype.ext (run_append {0, 1} s.val u v)

abbrev RegisterablePlacements (n : ℕ) [NeZero n] :=
  {P : Placement n (Finset (ZMod n)) //
    ∃ s : Execution n (ZMod n), PairGenerated s ∧ PairRegisterable s ∧ s.placed = P}

abbrev RegisteredNonterminalPlacements (n : ℕ) [NeZero n] :=
  {P : Placement n (Finset (ZMod n)) //
    ∃ s : Execution n (ZMod n), PairGenerated s ∧ RegisteredNonterminal s ∧ s.placed = P}

abbrev FutureNormalForms (n : ℕ) [NeZero n] :=
  Unit ⊕ (RegisterablePlacements n ⊕ RegisteredNonterminalPlacements n)

noncomputable def futureNormalKey (x : GeneratedState n) : FutureNormalForms n := by
  classical
  exact if hz : SilentRegion x.val then Sum.inl PUnit.unit
    else if hr : PairRegisterable x.val then
      Sum.inr (Sum.inl ⟨x.val.placed, x.val, x.property, hr, rfl⟩)
    else Sum.inr (Sum.inr ⟨x.val.placed, x.val, x.property,
      (region_trichotomy x.val).resolve_left hz |>.resolve_left hr, rfl⟩)

theorem futureNormalKey_of_silent (x : GeneratedState n) (h : SilentRegion x.val) :
    futureNormalKey x = Sum.inl PUnit.unit := by
  classical
  simp [futureNormalKey, h]

theorem futureNormalKey_of_registerable (x : GeneratedState n) (h : PairRegisterable x.val) :
    futureNormalKey x = Sum.inr (Sum.inl
      ⟨x.val.placed, x.val, x.property, h, rfl⟩) := by
  classical
  have hz : ¬ SilentRegion x.val := fun hs => silentRegion_not_registerable x.val hs h
  simp [futureNormalKey, hz, h]

theorem futureNormalKey_of_registered (x : GeneratedState n) (h : RegisteredNonterminal x.val) :
    futureNormalKey x = Sum.inr (Sum.inr
      ⟨x.val.placed, x.val, x.property, h, rfl⟩) := by
  classical
  have hz : ¬ SilentRegion x.val := fun hs => silentRegion_not_registeredNonterminal x.val hs h
  have hr : ¬ PairRegisterable x.val := fun hs => registerable_not_registered x.val hs h.1
  simp [futureNormalKey, hz, hr]

theorem futureNormalKey_eq_iff (x y : GeneratedState n) :
    futureNormalKey x = futureNormalKey y ↔ FutureNormalFormEq x.val y.val := by
  constructor
  · intro hkey
    rcases region_trichotomy x.val with hx | hx | hx
    · rw [futureNormalKey_of_silent x hx] at hkey
      rcases region_trichotomy y.val with hy | hy | hy
      · exact Or.inl ⟨hx, hy⟩
      · rw [futureNormalKey_of_registerable y hy] at hkey
        cases hkey
      · rw [futureNormalKey_of_registered y hy] at hkey
        cases hkey
    · rw [futureNormalKey_of_registerable x hx] at hkey
      rcases region_trichotomy y.val with hy | hy | hy
      · rw [futureNormalKey_of_silent y hy] at hkey
        cases hkey
      · rw [futureNormalKey_of_registerable y hy] at hkey
        exact Or.inr (Or.inl ⟨hx, hy,
          congrArg Subtype.val (Sum.inl.inj (Sum.inr.inj hkey))⟩)
      · rw [futureNormalKey_of_registered y hy] at hkey
        cases hkey
    · rw [futureNormalKey_of_registered x hx] at hkey
      rcases region_trichotomy y.val with hy | hy | hy
      · rw [futureNormalKey_of_silent y hy] at hkey
        cases hkey
      · rw [futureNormalKey_of_registerable y hy] at hkey
        cases hkey
      · rw [futureNormalKey_of_registered y hy] at hkey
        exact Or.inr (Or.inr ⟨hx, hy,
          congrArg Subtype.val (Sum.inr.inj (Sum.inr.inj hkey))⟩)
  · rintro (⟨hx, hy⟩ | ⟨hx, hy, hp⟩ | ⟨hx, hy, hp⟩)
    · rw [futureNormalKey_of_silent x hx, futureNormalKey_of_silent y hy]
    · rw [futureNormalKey_of_registerable x hx, futureNormalKey_of_registerable y hy]
      exact congrArg (fun P => Sum.inr (Sum.inl P)) (Subtype.ext hp)
    · rw [futureNormalKey_of_registered x hx, futureNormalKey_of_registered y hy]
      exact congrArg (fun P => Sum.inr (Sum.inr P)) (Subtype.ext hp)

/-- A concrete history realizes the otherwise constant silent key. -/
theorem seed_sweep_silent (hn : 3 ≤ n) :
    let s := run {0, 1} (singletonExecution n) (sweepCore (n - 2))
    PairGenerated s ∧ RankOnePlacement s ∧ SilentRegion s := by
  let s := run {0, 1} (singletonExecution n) (sweepCore (n - 2))
  have hg : PairGenerated s := ⟨sweepCore (n - 2), rfl⟩
  obtain ⟨lift, hp⟩ := (singletonExecution_ordered (n := n))
  have hsplaced := atomSite_run {0, 1} (singletonExecution n) lift.position
    (sweepCore (n - 2)) (by omega) hp
  have hmap : siteWord (sweepCore (n - 2)) ∘ lift.position =
      (fun _ : ZMod n => (0 : ZMod n)) := by
    funext atom
    exact sweepCore_final_site (lift.position atom) (by omega)
  have ht : RankOnePlacement s := ⟨0, hsplaced.trans (congrArg placementOfMap hmap)⟩
  exact ⟨hg, ht, (generated_alwaysSilent_iff s hn hg).mp (rankOne_trace_null s (by omega) ht)⟩

theorem futureNormalKey_surjective (hn : 3 ≤ n) :
    Function.Surjective (futureNormalKey (n := n)) := by
  intro key
  rcases key with ⟨⟩ | (P | P)
  · let s := run {0, 1} (singletonExecution n) (sweepCore (n - 2))
    obtain ⟨hg, _, hz⟩ := seed_sweep_silent (n := n) hn
    exact ⟨⟨s, hg⟩, futureNormalKey_of_silent ⟨s, hg⟩ hz⟩
  · obtain ⟨s, hg, hr, hp⟩ := P.property
    refine ⟨⟨s, hg⟩, ?_⟩
    rw [futureNormalKey_of_registerable ⟨s, hg⟩ hr]
    exact congrArg (fun R => Sum.inr (Sum.inl R)) (Subtype.ext hp)
  · obtain ⟨s, hg, hr, hp⟩ := P.property
    refine ⟨⟨s, hg⟩, ?_⟩
    rw [futureNormalKey_of_registered ⟨s, hg⟩ hr]
    exact congrArg (fun A => Sum.inr (Sum.inr A)) (Subtype.ext hp)

noncomputable def quotientNormalKey (hn : 3 ≤ n) :
    FutureQuotient n → FutureNormalForms n :=
  Quotient.lift futureNormalKey (fun x y h => (futureNormalKey_eq_iff x y).mpr
    ((futureEquivalent_iff_normalForm x.val y.val hn x.property y.property).mp h))

theorem quotientNormalKey_mk (hn : 3 ≤ n) (x : GeneratedState n) :
    quotientNormalKey hn (Quotient.mk (futureSetoid n) x) = futureNormalKey x := rfl

theorem quotientNormalKey_run_mk (hn : 3 ≤ n) (word : List Letter) (x : GeneratedState n) :
    quotientNormalKey hn (quotientRun word (Quotient.mk (futureSetoid n) x)) =
      futureNormalKey (generatedRun x word) := rfl

theorem quotientNormalKey_injective (hn : 3 ≤ n) :
    Function.Injective (quotientNormalKey (n := n) hn) := by
  intro x y
  refine Quotient.inductionOn₂ x y ?_
  intro sx sy hkey
  apply Quotient.sound
  exact (futureEquivalent_iff_normalForm sx.val sy.val hn sx.property sy.property).mpr
    ((futureNormalKey_eq_iff sx sy).mp hkey)

theorem quotientNormalKey_surjective (hn : 3 ≤ n) :
    Function.Surjective (quotientNormalKey (n := n) hn) := by
  intro key
  obtain ⟨x, hx⟩ := futureNormalKey_surjective (n := n) hn key
  exact ⟨Quotient.mk (futureSetoid n) x, hx⟩

/-- The quotient is of actual generated states under all-word future
equivalence. Its normal forms retain actual-placement provenance. -/
noncomputable def futureQuotientEquivNormalForms (hn : 3 ≤ n) :
    FutureQuotient n ≃ FutureNormalForms n :=
  Equiv.ofBijective (quotientNormalKey hn)
    ⟨quotientNormalKey_injective hn, quotientNormalKey_surjective hn⟩

theorem futureQuotientEquivNormalForms_mk (hn : 3 ≤ n) (x : GeneratedState n) :
    futureQuotientEquivNormalForms hn (Quotient.mk (futureSetoid n) x) = futureNormalKey x := rfl

theorem finite_futureNormalForms : Finite (FutureNormalForms n) := by infer_instance

/-- Finiteness is obtained from the actual quotient equivalence, not from
a bounded history enumeration or an assumption that all logs are short. -/
theorem finite_futureQuotient (hn : 3 ≤ n) : Finite (FutureQuotient n) :=
  Finite.of_injective (quotientNormalKey hn) (quotientNormalKey_injective hn)

theorem card_futureQuotient (hn : 3 ≤ n) :
    Nat.card (FutureQuotient n) =
      1 + Nat.card (RegisterablePlacements n) + Nat.card (RegisteredNonterminalPlacements n) := by
  rw [Nat.card_congr (futureQuotientEquivNormalForms hn)]
  simp [FutureNormalForms, Nat.card_sum, add_assoc]

end FutureEvent
