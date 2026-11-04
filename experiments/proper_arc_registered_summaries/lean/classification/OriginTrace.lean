import ProperArc

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
/-- A previously absent origin is created only by the actual d collision,
with the ordered parents read from that very predecessor. -/
theorem new_origin_step (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (letter : Letter) (record : FusionRecord (ZMod n)) (hnone : s.origin = none)
    (hnew : (step F s letter).origin = some record) :
    letter = .d ∧ ∃ U V, s.placed 0 = some U ∧ s.placed 1 = some V ∧
      U ∪ V = F ∧ record = ⟨U, V, F⟩ := by
  cases letter with
  | p => simp [step, hnone] at hnew
  | d =>
    refine ⟨rfl, ?_⟩
    cases h0 : s.placed 0 with
    | none => simp [step, stepDefect, h0, hnone] at hnew
    | some U =>
      cases h1 : s.placed 1 with
      | none => simp [step, stepDefect, h0, h1, hnone] at hnew
      | some V =>
        by_cases hjoin : U ∪ V = F
        · refine ⟨U, V, rfl, rfl, hjoin, ?_⟩
          simpa [step, stepDefect, h0, h1, hnone, hjoin] using hnew.symm
        · simp [step, stepDefect, h0, h1, hnone, hjoin] at hnew

omit [NeZero n] in
/-- Recover one first-registration occurrence from the original word.
The source, ports, event and suffix all belong to that same invocation. -/
theorem extract_first_registration (F : Finset (ZMod n))
    (start : Execution n (ZMod n)) (word : List Letter)
    (record : FusionRecord (ZMod n)) (hstart : start.origin = none)
    (hfinal : (run F start word).origin = some record) :
    ∃ pre post U V,
      word = pre ++ .d :: post ∧
      (run F start pre).origin = none ∧
      (run F start pre).placed 0 = some U ∧
      (run F start pre).placed 1 = some V ∧
      U ∪ V = F ∧ record = ⟨U, V, F⟩ := by
  induction word generalizing start with
  | nil => simp [run, hstart] at hfinal
  | cons letter rest ih =>
    let next := step F start letter
    cases hnext : next.origin with
    | none =>
      have htail : (run F next rest).origin = some record := hfinal
      obtain ⟨pre, post, U, V, hword, horigin, h0, h1, hjoin, hrecord⟩ :=
        ih next hnext htail
      refine ⟨letter :: pre, post, U, V, ?_, ?_, ?_, ?_, hjoin, hrecord⟩
      · simp [hword]
      · exact horigin
      · exact h0
      · exact h1
    | some first =>
      have hpersist := run_origin_of_some F next first hnext rest
      have hrecord : first = record := Option.some.inj (hpersist.symm.trans hfinal)
      have hstep : (step F start letter).origin = some record := by
        simpa only [next, hrecord] using hnext
      obtain ⟨hletter, U, V, h0, h1, hjoin, hevent⟩ := new_origin_step F start letter record hstart hstep
      refine ⟨[], rest, U, V, ?_, hstart, h0, h1, hjoin, hevent⟩
      simp [hletter]

end ProperArc
