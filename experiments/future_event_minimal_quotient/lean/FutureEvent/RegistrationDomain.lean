import FutureEvent.GapRegistration

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def SingletonSource (f : ZMod n → ZMod n) (atom : ZMod n) : Prop :=
  ∀ other, f other = f atom → other = atom

def SeparateSingletons (f : ZMod n → ZMod n) : Prop :=
  SingletonSource f 0 ∧ SingletonSource f 1

def PairGenerated (s : Execution n (ZMod n)) : Prop :=
  ∃ history, run {0, 1} (singletonExecution n) history = s

/-- Semantic future registration, without assuming a source normal form. -/
def PairRegisterable (s : Execution n (ZMod n)) : Prop :=
  s.origin = none ∧ ∃ word, (run {0, 1} s word).origin.isSome = true

theorem singletonSource_iff_fiber (f : ZMod n → ZMod n) (atom : ZMod n) :
    SingletonSource f atom ↔ sourceFiber f (f atom) = {atom} := by
  constructor
  · intro h
    ext other
    simp only [mem_sourceFiber, Finset.mem_singleton]
    exact ⟨h other, fun heq => congrArg f heq⟩
  · intro h other heq
    have hmem : other ∈ sourceFiber f (f atom) := (mem_sourceFiber _ _ _).mpr heq
    simpa [h] using hmem

omit [NeZero n] in
theorem separateSingletons_distinct (f : ZMod n → ZMod n) (hn : 2 ≤ n)
    (h : SeparateSingletons f) : f 0 ≠ f 1 := by
  intro heq
  have hone : (1 : ZMod n) = 0 := h.1 1 heq.symm
  have := ZMod.one_eq_zero_iff.mp hone
  omega

/-- A genuine two-port fusion creating exactly the pair has singleton parents. -/
theorem pair_fusion_singletons (f : ZMod n → ZMod n) (hn : 2 ≤ n)
    (hleft : (sourceFiber f 0).Nonempty) (hright : (sourceFiber f 1).Nonempty)
    (hunion : sourceFiber f 0 ∪ sourceFiber f 1 = {0, 1}) :
    SeparateSingletons f := by
  have hcovered (atom : ZMod n) :
      (f atom = 0 ∨ f atom = 1) ↔ (atom = 0 ∨ atom = 1) := by
    have h := Finset.ext_iff.mp hunion atom
    simpa only [Finset.mem_union, mem_sourceFiber, Finset.mem_insert,
      Finset.mem_singleton] using h
  have hports0 : f 0 = 0 ∨ f 0 = 1 := (hcovered 0).mpr (Or.inl rfl)
  have hports1 : f 1 = 0 ∨ f 1 = 1 := (hcovered 1).mpr (Or.inr rfl)
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro heq
    have := ZMod.one_eq_zero_iff.mp heq.symm
    omega
  have hsep : f 0 ≠ f 1 := by
    intro heq
    obtain ⟨x, hx⟩ := hleft
    obtain ⟨y, hy⟩ := hright
    have hfx : f x = 0 := (mem_sourceFiber _ _ _).mp hx
    have hfy : f y = 1 := (mem_sourceFiber _ _ _).mp hy
    have hxcases := (hcovered x).mp (Or.inl hfx)
    have hycases := (hcovered y).mp (Or.inr hfy)
    have hxeq : f x = f 0 := by rcases hxcases with h | h <;> simp [h, heq]
    have hyeq : f y = f 0 := by rcases hycases with h | h <;> simp [h, heq]
    exact h01 (hfx.symm.trans (hxeq.trans (hyeq.symm.trans hfy)))
  constructor
  · intro atom heq
    have hport : f atom = 0 ∨ f atom = 1 := by simpa [heq] using hports0
    rcases (hcovered atom).mp hport with h | h
    · exact h
    · exact False.elim (hsep (by simpa [h] using heq.symm))
  · intro atom heq
    have hport : f atom = 0 ∨ f atom = 1 := by simpa [heq] using hports1
    rcases (hcovered atom).mp hport with h | h
    · exact False.elim (hsep (by simpa [h] using heq))
    · exact h

theorem newly_registered_singletons (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (a : Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) (hbefore : s.origin = none)
    (hafter : (step {0, 1} s a).origin.isSome = true) :
    SeparateSingletons f := by
  cases a with
  | p => simp [step, hbefore] at hafter
  | d =>
      cases h0 : s.placed 0 with
      | none => simp [step, stepDefect, h0, hbefore] at hafter
      | some u =>
          cases h1 : s.placed 1 with
          | none => simp [step, stepDefect, h0, h1, hbefore] at hafter
          | some v =>
              by_cases hu : u ∪ v = ({0, 1} : Finset (ZMod n))
              · have huf := (placementOfMap_some_iff f 0 u).mp (hplaced ▸ h0)
                have hvf := (placementOfMap_some_iff f 1 v).mp (hplaced ▸ h1)
                exact pair_fusion_singletons f hn
                  (huf.1.symm ▸ huf.2) (hvf.1.symm ▸ hvf.2)
                  (by rw [huf.1, hvf.1]; exact hu)
              · simp [step, stepDefect, h0, h1, hbefore, hu] at hafter

/-- Future creation of the pair forces singleton source fibers already now. -/
theorem future_registration_singletons (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) (hbefore : s.origin = none)
    (hafter : (run {0, 1} s word).origin.isSome = true) :
    SeparateSingletons f := by
  induction word generalizing s f with
  | nil => simp [run, hbefore] at hafter
  | cons a rest ih =>
      by_cases hnew : (step {0, 1} s a).origin.isSome = true
      · exact newly_registered_singletons s f a hn hplaced hbefore hnew
      · have hnone : (step {0, 1} s a).origin = none := by
          cases h : (step {0, 1} s a).origin <;> simp_all
        have hnext := ih (step {0, 1} s a) (forwardMapStep f a)
          (step_placementOfMap {0, 1} s f a hn hplaced) hnone hafter
        constructor
        · intro atom heq
          apply hnext.1 atom
          cases a <;> simp [forwardMapStep, heq]
        · intro atom heq
          apply hnext.2 atom
          cases a <;> simp [forwardMapStep, heq]

theorem pairGenerated_sourceOrdered (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (h : PairGenerated s) : SourceOrdered s.placed := by
  obtain ⟨history, rfl⟩ := h
  exact run_ordered {0, 1} (singletonExecution n) history hn singletonExecution_ordered

end FutureEvent
