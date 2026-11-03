import RegisteredAbsorptionChains.NoSplitting

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def siteLetter : Letter → ZMod n → ZMod n
  | .p, q => q + 1
  | .d, q => collapsePosition q

/-- A chronological site action, including collisions. -/
def siteWord : List Letter → ZMod n → ZMod n
  | [], q => q
  | a :: rest, q => siteWord rest (siteLetter a q)

omit [NeZero n] in
@[simp] theorem siteWord_nil (q : ZMod n) : siteWord [] q = q := rfl

omit [NeZero n] in
theorem siteWord_append (u v : List Letter) (q : ZMod n) :
    siteWord (u ++ v) q = siteWord v (siteWord u q) := by
  induction u generalizing q with
  | nil => rfl
  | cons a rest ih => exact ih (siteLetter a q)

omit [NeZero n] in
theorem forwardMapRun_eq_siteWord (f : ZMod n → ZMod n)
    (word : List Letter) (atom : ZMod n) :
    forwardMapRun f word atom = siteWord word (f atom) := by
  induction word generalizing f with
  | nil => rfl
  | cons a rest ih =>
      change forwardMapRun (forwardMapStep f a) rest atom = _
      rw [ih]
      cases a <;> rfl

/-- Lemma 5.1: every actual atom follows the same site word through fusion. -/
theorem atomSite_run (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) :
    (run F s word).placed = placementOfMap (siteWord word ∘ f) := by
  rw [run_placementOfMap F s f word hn hplaced]
  congr 1
  funext atom
  exact forwardMapRun_eq_siteWord f word atom

/-- A literal placement determines the site of every atom, not just its block. -/
theorem placementOfMap_injective :
    Function.Injective (placementOfMap (n := n)) := by
  intro f g h
  funext atom
  have hx : atom ∈ sourceFiber f (f atom) := by simp
  have hne : (sourceFiber f (f atom)).Nonempty := ⟨atom, hx⟩
  have hp := (placementOfMap_some_iff f (f atom) _).mpr ⟨rfl, hne⟩
  rw [h] at hp
  have heq := (placementOfMap_some_iff g (f atom) _).mp hp
  exact ((mem_sourceFiber g atom (f atom)).mp (heq.1.symm ▸ hx)).symm

theorem run_placed_eq_iff_atomSites (F : Finset (ZMod n))
    (s t : Execution n (ZMod n)) (f g : ZMod n → ZMod n)
    (word : List Letter) (hn : 2 ≤ n)
    (hs : s.placed = placementOfMap f) (ht : t.placed = placementOfMap g) :
    (run F s word).placed = (run F t word).placed ↔
      ∀ atom, siteWord word (f atom) = siteWord word (g atom) := by
  rw [atomSite_run F s f word hn hs, atomSite_run F t g word hn ht]
  constructor
  · intro h atom
    exact congrFun (placementOfMap_injective h) atom
  · intro h
    exact congrArg placementOfMap (funext h)

/-- Final injectivity on initially occupied sites excludes every earlier
fusion, not just a collision at the final prefix endpoint. -/
theorem fusionFree_of_final_site_injective (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f)
    (hinj : ∀ x y, siteWord word (f x) = siteWord word (f y) → f x = f y) :
    FusionFree F s word := by
  induction word generalizing s f with
  | nil => trivial
  | cons a rest ih =>
      have hnext : FusionFree F (step F s a) rest := by
        refine ih (step F s a) (forwardMapStep f a)
          (step_placementOfMap F s f a hn hplaced) ?_
        intro x y heq
        have hfull : siteWord (a :: rest) (f x) =
            siteWord (a :: rest) (f y) := by
          cases a <;> exact heq
        have hsame := hinj x y hfull
        cases a <;> simp [forwardMapStep, hsame]
      cases a with
      | p => exact hnext
      | d =>
          refine ⟨?_, hnext⟩
          cases h0 : s.placed 0 with
          | none => exact Or.inl rfl
          | some u =>
              cases h1 : s.placed 1 with
              | none => exact Or.inr rfl
              | some v =>
                  obtain ⟨x, hx⟩ := ((placementOfMap_some_iff f 0 u).mp (hplaced ▸ h0)).2
                  obtain ⟨y, hy⟩ := ((placementOfMap_some_iff f 1 v).mp (hplaced ▸ h1)).2
                  have hfx : f x = 0 := (mem_sourceFiber f x 0).mp
                    (((placementOfMap_some_iff f 0 u).mp (hplaced ▸ h0)).1.symm ▸ hx)
                  have hfy : f y = 1 := (mem_sourceFiber f y 1).mp
                    (((placementOfMap_some_iff f 1 v).mp (hplaced ▸ h1)).1.symm ▸ hy)
                  have h01 : (0 : ZMod n) ≠ 1 := by
                    intro h
                    have := ZMod.one_eq_zero_iff.mp h.symm
                    omega
                  have heq : siteWord (.d :: rest) (f x) =
                      siteWord (.d :: rest) (f y) := by
                    simp [siteWord, siteLetter, collapsePosition, hfx, hfy, h01]
                  exact False.elim (h01 (hfx.symm.trans ((hinj x y heq).trans hfy)))

end FutureEvent
