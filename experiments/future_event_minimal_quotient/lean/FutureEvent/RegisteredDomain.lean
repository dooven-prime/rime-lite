import FutureEvent.SweepReconstruction

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem run_registered (s : Execution n (ZMod n)) (word : List Letter)
    (h : s.origin.isSome = true) : (run {0, 1} s word).origin.isSome = true := by
  induction word generalizing s with
  | nil => exact h
  | cons a rest ih => exact ih (step {0, 1} s a) (step_registered {0, 1} s a h)

theorem new_registration_colocated (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (a : Letter)
    (hp : s.placed = placementOfMap f) (ho : s.origin = none)
    (hnew : (step {0, 1} s a).origin.isSome = true) :
    forwardMapStep f a 0 = forwardMapStep f a 1 := by
  cases a with
  | p => simp [step, ho] at hnew
  | d =>
      cases h0 : s.placed 0 with
      | none => simp [step, stepDefect, h0, ho] at hnew
      | some U =>
          cases h1 : s.placed 1 with
          | none => simp [step, stepDefect, h0, h1, ho] at hnew
          | some V =>
              by_cases he : U ∪ V = ({0, 1} : Finset (ZMod n))
              · have hU := (placementOfMap_some_iff f 0 U).mp (hp ▸ h0)
                have hV := (placementOfMap_some_iff f 1 V).mp (hp ▸ h1)
                have hports (atom : ZMod n) (ha : atom ∈ ({0, 1} : Finset (ZMod n))) :
                    f atom = 0 ∨ f atom = 1 := by
                  rw [← he, Finset.mem_union] at ha
                  rcases ha with h | h
                  · exact Or.inl ((mem_sourceFiber f atom 0).mp (hU.1.symm ▸ h))
                  · exact Or.inr ((mem_sourceFiber f atom 1).mp (hV.1.symm ▸ h))
                have hc (atom : ZMod n) (ha : atom ∈ ({0, 1} : Finset (ZMod n))) :
                    collapsePosition (f atom) = 0 := by
                  rcases hports atom ha with h | h <;> simp [h, collapsePosition]
                exact (hc 0 (by simp)).trans (hc 1 (by simp)).symm
              · simp [step, stepDefect, h0, h1, ho, he] at hnew

theorem run_registered_colocated (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (word : List Letter) (hn : 2 ≤ n)
    (hp : s.placed = placementOfMap f)
    (hbefore : s.origin.isSome = true → f 0 = f 1)
    (hafter : (run {0, 1} s word).origin.isSome = true) :
    forwardMapRun f word 0 = forwardMapRun f word 1 := by
  induction word generalizing s f with
  | nil => exact hbefore hafter
  | cons a rest ih =>
      apply ih (step {0, 1} s a) (forwardMapStep f a)
        (step_placementOfMap {0, 1} s f a hn hp) _ hafter
      intro hstep
      cases ho : s.origin with
      | none => exact new_registration_colocated s f a hp ho hstep
      | some record =>
          have hpair := hbefore (by simp [ho])
          cases a <;> simp [forwardMapStep, hpair]

/-- Registration and no-splitting bind both selected source atoms to the
same actual current packet, independently of the stored old chain. -/
theorem generated_registered_colocated (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 2 ≤ n) (hg : PairGenerated s)
    (hp : s.placed = placementOfMap f) (hr : s.origin.isSome = true) : f 0 = f 1 := by
  obtain ⟨word, rfl⟩ := hg
  obtain ⟨lift, hseed⟩ := (singletonExecution_ordered (n := n))
  have hactual := run_placementOfMap {0, 1} (singletonExecution n) lift.position word hn hseed
  have heq : forwardMapRun lift.position word = f := placementOfMap_injective (hactual.symm.trans hp)
  rw [← heq]
  exact run_registered_colocated (singletonExecution n) lift.position word hn hseed
    (by simp [singletonExecution]) hr

theorem carrierAt_pair_of_map (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (q : ZMod n)
    (hp : s.placed = placementOfMap f) (h0 : f 0 = q) (h1 : f 1 = q) :
    CarrierAt {0, 1} s q := by
  refine ⟨sourceFiber f q, ?_, ?_⟩
  · rw [hp]
    exact (placementOfMap_some_iff f q _).mpr ⟨rfl, ⟨0, by simp [h0]⟩⟩
  · intro atom ha
    simp only [Finset.mem_insert, Finset.mem_singleton] at ha
    rcases ha with rfl | rfl <;> simp [h0, h1]

theorem generated_registered_carrier (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 2 ≤ n) (hg : PairGenerated s)
    (hp : s.placed = placementOfMap f) (hr : s.origin.isSome = true) :
    CarrierAt {0, 1} s (f 0) :=
  carrierAt_pair_of_map s f (f 0) hp rfl
    (generated_registered_colocated s f hn hg hp hr).symm

omit [NeZero n] in
theorem selected_absorption_parents (s : Execution n (ZMod n))
    (record : FusionRecord (ZMod n))
    (h : selectedOutput {0, 1} s .d = some (.absorption record)) :
    s.placed 0 = some record.left ∧ s.placed 1 = some record.right := by
  cases h0 : s.placed 0 with
  | none => simp [selectedOutput, h0] at h
  | some U =>
      cases h1 : s.placed 1 with
      | none => simp [selectedOutput, h0, h1] at h
      | some V =>
          cases ho : s.origin with
          | none =>
              by_cases he : U ∪ V = ({0, 1} : Finset (ZMod n)) <;>
                simp [selectedOutput, h0, h1, ho, he] at h
          | some old =>
              by_cases hU : ({0, 1} : Finset (ZMod n)) ⊆ U <;>
                by_cases hV : ({0, 1} : Finset (ZMod n)) ⊆ V
              all_goals try simp [selectedOutput, h0, h1, ho, hU, hV] at h
              all_goals
                have he : (⟨U, V, U ∪ V⟩ : FusionRecord (ZMod n)) = record := by
                  simpa [selectedOutput, h0, h1, ho, hU, hV] using h
                exact ⟨congrArg (fun r => some r.left) he,
                  congrArg (fun r => some r.right) he⟩

theorem selected_absorption_left_site (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (record : FusionRecord (ZMod n)) (atom : ZMod n)
    (hp : s.placed = placementOfMap f)
    (h : selectedOutput {0, 1} s .d = some (.absorption record))
    (ha : atom ∈ record.left) : f atom = 0 := by
  have hleft := (selected_absorption_parents s record h).1
  have hf := (placementOfMap_some_iff f 0 _).mp (hp ▸ hleft)
  exact (mem_sourceFiber f atom 0).mp (hf.1.symm ▸ ha)

theorem selected_absorption_right_site (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (record : FusionRecord (ZMod n)) (atom : ZMod n)
    (hp : s.placed = placementOfMap f)
    (h : selectedOutput {0, 1} s .d = some (.absorption record))
    (ha : atom ∈ record.right) : f atom = 1 := by
  have hright := (selected_absorption_parents s record h).2
  have hf := (placementOfMap_some_iff f 1 _).mp (hp ▸ hright)
  exact (mem_sourceFiber f atom 1).mp (hf.1.symm ▸ ha)

end FutureEvent
