import full_summary.NullWitness

namespace FullSummary

open RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

abbrev RegisteredGeneratedStates (n : ℕ) [NeZero n] :=
  {x : GeneratedState n // x.val.origin.isSome = true}

abbrev NormalForms (n : ℕ) [NeZero n] :=
  Unit ⊕ (RegisterablePlacements n ⊕ RegisteredGeneratedStates n)

theorem full_region_cases (s : Execution n (ZMod n)) :
    PermanentlyUnregistered s ∨ PairRegisterable s ∨ s.origin.isSome = true := by
  by_cases ho : s.origin = none
  · by_cases hr : PairRegisterable s
    · exact Or.inr (Or.inl hr)
    · exact Or.inl ⟨ho, hr⟩
  · right; right
    cases he : s.origin <;> simp_all

noncomputable def normalKey (x : GeneratedState n) : NormalForms n := by
  classical
  exact if hr : x.val.origin.isSome = true then Sum.inr (Sum.inr ⟨x, hr⟩)
    else if hp : PairRegisterable x.val then
      Sum.inr (Sum.inl ⟨x.val.placed, x.val, x.property, hp, rfl⟩)
    else Sum.inl ()

theorem normalKey_of_permanent (x : GeneratedState n) (h : PermanentlyUnregistered x.val) :
    normalKey x = Sum.inl () := by
  classical
  simp [normalKey, h.1, h.2]

theorem normalKey_of_registerable (x : GeneratedState n) (h : PairRegisterable x.val) :
    normalKey x = Sum.inr (Sum.inl ⟨x.val.placed, x.val, x.property, h, rfl⟩) := by
  classical
  simp [normalKey, h.1, h]

theorem normalKey_of_registered (x : GeneratedState n) (h : x.val.origin.isSome = true) :
    normalKey x = Sum.inr (Sum.inr ⟨x, h⟩) := by
  classical
  simp [normalKey, h]

theorem normalKey_eq_iff (x y : GeneratedState n) :
    normalKey x = normalKey y ↔
      (PermanentlyUnregistered x.val ∧ PermanentlyUnregistered y.val) ∨ x.val = y.val := by
  constructor
  · intro hkey
    rcases full_region_cases x.val with hx | hx | hx
    · rw [normalKey_of_permanent x hx] at hkey
      rcases full_region_cases y.val with hy | hy | hy
      · exact Or.inl ⟨hx, hy⟩
      · rw [normalKey_of_registerable y hy] at hkey; cases hkey
      · rw [normalKey_of_registered y hy] at hkey; cases hkey
    · rw [normalKey_of_registerable x hx] at hkey
      rcases full_region_cases y.val with hy | hy | hy
      · rw [normalKey_of_permanent y hy] at hkey; cases hkey
      · rw [normalKey_of_registerable y hy] at hkey
        have hp := congrArg Subtype.val (Sum.inl.inj (Sum.inr.inj hkey))
        exact Or.inr (generated_unregistered_same_placement_eq x.val y.val
          x.property y.property hx.1 hy.1 hp)
      · rw [normalKey_of_registered y hy] at hkey; cases hkey
    · rw [normalKey_of_registered x hx] at hkey
      rcases full_region_cases y.val with hy | hy | hy
      · rw [normalKey_of_permanent y hy] at hkey; cases hkey
      · rw [normalKey_of_registerable y hy] at hkey; cases hkey
      · rw [normalKey_of_registered y hy] at hkey
        exact Or.inr (congrArg (fun z : RegisteredGeneratedStates n => z.val.val)
          (Sum.inr.inj (Sum.inr.inj hkey)))
  · rintro (⟨hx, hy⟩ | he)
    · rw [normalKey_of_permanent x hx, normalKey_of_permanent y hy]
    · have hxy : x = y := Subtype.ext he
      rw [hxy]

theorem normalKey_surjective (hn : 3 ≤ n) : Function.Surjective (normalKey (n := n)) := by
  intro key
  rcases key with ⟨⟩ | (P | R)
  · exact ⟨⟨spoiledSeed, spoiledSeed_generated⟩,
      normalKey_of_permanent _ (spoiledSeed_null hn)⟩
  · obtain ⟨s, hg, hr, hp⟩ := P.property
    refine ⟨⟨s, hg⟩, ?_⟩
    rw [normalKey_of_registerable ⟨s, hg⟩ hr]
    exact congrArg (fun p => Sum.inr (Sum.inl p)) (Subtype.ext hp)
  · exact ⟨R.val, normalKey_of_registered R.val R.property⟩

def fullSetoid (n : ℕ) [NeZero n] : Setoid (GeneratedState n) where
  r x y := Equivalent {0, 1} x.val y.val
  iseqv := ⟨fun _ => equivalent_refl _ _, fun h word => (h word).symm,
    fun hxy hyz word => (hxy word).trans (hyz word)⟩

abbrev FullQuotient (n : ℕ) [NeZero n] := Quotient (fullSetoid n)

noncomputable def quotientKey (hn : 3 ≤ n) : FullQuotient n → NormalForms n :=
  Quotient.lift normalKey (fun x y h => (normalKey_eq_iff x y).mpr
    ((equivalent_iff_normalForm x.val y.val hn x.property y.property).mp h))

theorem quotientKey_mk (hn : 3 ≤ n) (x : GeneratedState n) :
    quotientKey hn (Quotient.mk (fullSetoid n) x) = normalKey x := rfl

theorem quotientKey_injective (hn : 3 ≤ n) : Function.Injective (quotientKey (n := n) hn) := by
  intro x y
  refine Quotient.inductionOn₂ x y ?_
  intro sx sy hkey
  apply Quotient.sound
  exact (equivalent_iff_normalForm sx.val sy.val hn sx.property sy.property).mpr
    ((normalKey_eq_iff sx sy).mp hkey)

theorem quotientKey_surjective (hn : 3 ≤ n) : Function.Surjective (quotientKey (n := n) hn) := by
  intro key
  obtain ⟨x, hx⟩ := normalKey_surjective hn key
  exact ⟨Quotient.mk (fullSetoid n) x, hx⟩

/-- The actual Moore quotient, including the empty-word reading. -/
noncomputable def fullQuotientEquivNormalForms (hn : 3 ≤ n) : FullQuotient n ≃ NormalForms n :=
  Equiv.ofBijective (quotientKey hn) ⟨quotientKey_injective hn, quotientKey_surjective hn⟩

def fullQuotientRun (word : List Letter) : FullQuotient n → FullQuotient n :=
  Quotient.map (fun x => generatedRun x word)
    (fun _ _ h => equivalent_right_congruent _ _ _ h word)

theorem fullQuotientRun_mk (word : List Letter) (x : GeneratedState n) :
    fullQuotientRun word (Quotient.mk (fullSetoid n) x) =
      Quotient.mk (fullSetoid n) (generatedRun x word) := rfl

theorem fullQuotientRun_append (u v : List Letter) (x : FullQuotient n) :
    fullQuotientRun (u ++ v) x = fullQuotientRun v (fullQuotientRun u x) := by
  refine Quotient.inductionOn x ?_
  intro s
  rw [fullQuotientRun_mk, fullQuotientRun_mk, fullQuotientRun_mk]
  apply congrArg (Quotient.mk (fullSetoid n))
  exact Subtype.ext (run_append {0, 1} s.val u v)

/-- Observation refinement induces a canonical map of actual quotients. -/
def forgetToFuture : FullQuotient n → FutureQuotient n :=
  Quotient.map id (fun _ _ h => equivalent_implies_future _ _ _ h)

theorem forgetToFuture_surjective : Function.Surjective (forgetToFuture (n := n)) := by
  intro q
  refine Quotient.inductionOn q ?_
  intro s
  exact ⟨Quotient.mk (fullSetoid n) s, rfl⟩

theorem forgetToFuture_run (word : List Letter) (x : FullQuotient n) :
    forgetToFuture (fullQuotientRun word x) =
      FutureEvent.quotientRun word (forgetToFuture x) := by
  refine Quotient.inductionOn x ?_
  intro s
  rfl

end FullSummary
