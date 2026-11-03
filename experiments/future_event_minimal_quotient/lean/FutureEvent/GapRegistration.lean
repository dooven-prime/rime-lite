import FutureEvent.GapProbe
import FutureEvent.Events

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The literal ports before the final defect, under the initial singleton
and empty-open-gap premises. No clean-chain premise is used. -/
theorem gapPreFinal_ports (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (b : ZMod n) (g : ℕ) (hn : 2 ≤ n) (hg : 1 ≤ g) (hgn : g < n)
    (hplaced : s.placed = placementOfMap f)
    (hzero : sourceFiber f (b - (g : ZMod n)) = {0})
    (hone : sourceFiber f b = {1})
    (hsupport : ∀ atom, (b - f atom).val < g → f atom = b) :
    (run F s (gapPreFinal b g)).placed 0 = some {0} ∧
      (run F s (gapPreFinal b g)).placed 1 = some {1} := by
  have hz : sourceFiber (siteWord (gapPreFinal b g) ∘ f) 0 = {0} := by
    rw [← hzero]
    ext atom
    simp only [mem_sourceFiber, Function.comp_apply]
    exact gapPreFinal_zero_iff b (f atom) g hg hgn
  have ho : sourceFiber (siteWord (gapPreFinal b g) ∘ f) 1 = {1} := by
    rw [← hone]
    ext atom
    simp only [mem_sourceFiber, Function.comp_apply]
    rw [gapPreFinal_one_iff b (f atom) g hg]
    constructor
    · exact hsupport atom
    · intro h
      simpa [h] using (show 0 < g from hg)
  rw [atomSite_run F s f _ hn hplaced]
  constructor
  · exact (placementOfMap_some_iff _ 0 _).mpr ⟨hz, Finset.singleton_nonempty _⟩
  · exact (placementOfMap_some_iff _ 1 _).mpr ⟨ho, Finset.singleton_nonempty _⟩

def pairRegistration (n : ℕ) : FusionRecord (ZMod n) :=
  ⟨{0}, {1}, {0, 1}⟩

/-- The gap-admitted actual probe emits nothing before its last letter,
then registers exactly the ordered singleton pair. -/
theorem gapProbe_first_registration
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (b : ZMod n) (g : ℕ) (hn : 2 ≤ n) (hg : 1 ≤ g) (hgn : g < n)
    (hplaced : s.placed = placementOfMap f) (hunregistered : s.origin = none)
    (hzero : sourceFiber f (b - (g : ZMod n)) = {0})
    (hone : sourceFiber f b = {1})
    (hsupport : ∀ atom, (b - f atom).val < g → f atom = b) :
    eventTrace {0, 1} s (gapProbe b g) =
        List.replicate (gapPreFinal b g).length none ++
          [some (.registration (pairRegistration n))] ∧
      (run {0, 1} s (gapProbe b g)).origin = some (pairRegistration n) ∧
      (run {0, 1} s (gapProbe b g)).chain = s.chain := by
  have hfree := gapPreFinal_fusionFree {0, 1} s f b g hn hg hplaced hsupport
  obtain ⟨ho, hc, ht⟩ := fusionFree_records_and_trace {0, 1} s _ hfree
  have horigin : (run {0, 1} s (gapPreFinal b g)).origin = none :=
    ho.trans hunregistered
  obtain ⟨hport0, hport1⟩ :=
    gapPreFinal_ports {0, 1} s f b g hn hg hgn hplaced hzero hone hsupport
  constructor
  · rw [gapProbe, eventTrace_append, ht]
    simp [eventTrace, selectedOutput, hport0, hport1, horigin, pairRegistration]
  · rw [gapProbe, run_append]
    change (stepDefect {0, 1} (run {0, 1} s (gapPreFinal b g))).origin =
        some (pairRegistration n) ∧
      (stepDefect {0, 1} (run {0, 1} s (gapPreFinal b g))).chain = s.chain
    simp [stepDefect, hport0, hport1, horigin, pairRegistration, hc]

@[simp] theorem pWord_length (k : ℕ) : (pWord k).length = k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pWord, ih]

omit [NeZero n] in
theorem gapProbe_length (b : ZMod n) (g : ℕ) :
    (gapProbe b g).length = (1 - b).val + 2 * (g - 1) + 1 := by
  simp [gapProbe, gapPreFinal, add_assoc]

theorem gapProbe_length_le (b : ZMod n) (g : ℕ)
    (hn : 3 ≤ n) (hg : 1 ≤ g) (hgn : g ≤ n - 2) :
    (gapProbe b g).length ≤ 3 * n - 6 := by
  rw [gapProbe_length]
  have := ZMod.val_lt (1 - b)
  omega

end FutureEvent
