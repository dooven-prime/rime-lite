import FutureEvent.TwoProbeSeparation

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Literal one-packet placement: every source atom is at the same site. -/
def RankOnePlacement (s : Execution n (ZMod n)) : Prop :=
  ∃ q : ZMod n, s.placed = placementOfMap (fun _ : ZMod n => q)

def RegisteredNonterminal (s : Execution n (ZMod n)) : Prop :=
  s.origin.isSome = true ∧ ¬ RankOnePlacement s

/-- The structural silent region of the fixed manuscript, not a trace-based
definition that assumes the desired behavioral conclusion. -/
def SilentRegion (s : Execution n (ZMod n)) : Prop :=
  (s.origin = none ∧ ¬ PairRegisterable s) ∨
    (s.origin.isSome = true ∧ RankOnePlacement s)

def AlwaysSilent (s : Execution n (ZMod n)) : Prop :=
  ∀ word, eventTrace {0, 1} s word = List.replicate word.length none

omit [NeZero n] in
theorem unregistered_step_output_null (s : Execution n (ZMod n)) (a : Letter)
    (hs : s.origin = none) (ht : (step {0, 1} s a).origin = none) :
    selectedOutput {0, 1} s a = none := by
  cases a with
  | p => rfl
  | d =>
      cases h0 : s.placed 0 with
      | none => simp [selectedOutput, h0]
      | some U =>
          cases h1 : s.placed 1 with
          | none => simp [selectedOutput, h0, h1]
          | some V =>
              by_cases hu : U ∪ V = ({0, 1} : Finset (ZMod n))
              · simp [step, stepDefect, h0, h1, hs, hu] at ht
              · simp [selectedOutput, h0, h1, hs, hu]

omit [NeZero n] in
theorem unregistered_endpoint_trace_null (s : Execution n (ZMod n))
    (word : List Letter) (ht : (run {0, 1} s word).origin = none) :
    eventTrace {0, 1} s word = List.replicate word.length none := by
  induction word generalizing s with
  | nil => rfl
  | cons a rest ih =>
      have hnext : (step {0, 1} s a).origin = none :=
        (run_unregistered_records {0, 1} (step {0, 1} s a) rest ht).1
      have hs := (step_unregistered_records {0, 1} s a hnext).1
      simp [eventTrace, unregistered_step_output_null s a hs hnext,
        ih (step {0, 1} s a) ht, List.replicate_succ]

omit [NeZero n] in
theorem unregisterable_trace_null (s : Execution n (ZMod n))
    (hs : s.origin = none) (hr : ¬ PairRegisterable s) : AlwaysSilent s := by
  intro word
  apply unregistered_endpoint_trace_null s word
  cases h : (run {0, 1} s word).origin with
  | none => rfl
  | some record => exact False.elim (hr ⟨hs, word, by simp [h]⟩)

theorem rankOne_fusionFree (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (h : RankOnePlacement s) (word : List Letter) : FusionFree {0, 1} s word := by
  obtain ⟨q, hq⟩ := h
  exact fusionFree_of_final_site_injective {0, 1} s (fun _ => q) word hn hq
    (fun _ _ _ => rfl)

theorem rankOne_trace_null (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (h : RankOnePlacement s) : AlwaysSilent s := by
  intro word
  exact (fusionFree_records_and_trace {0, 1} s word (rankOne_fusionFree s hn h word)).2.2

theorem rankOne_run (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (h : RankOnePlacement s) (word : List Letter) :
    RankOnePlacement (run {0, 1} s word) := by
  obtain ⟨q, hq⟩ := h
  exact ⟨siteWord word q, atomSite_run {0, 1} s (fun _ => q) word hn hq⟩

theorem silentRegion_trace_null (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (h : SilentRegion s) : AlwaysSilent s := by
  rcases h with ⟨hs, hr⟩ | ⟨_, hterminal⟩
  · exact unregisterable_trace_null s hs hr
  · exact rankOne_trace_null s hn hterminal

theorem silentRegion_futureEquivalent (x y : Execution n (ZMod n)) (hn : 2 ≤ n)
    (hx : SilentRegion x) (hy : SilentRegion y) : FutureEquivalent {0, 1} x y := by
  intro word
  exact (silentRegion_trace_null x hn hx word).trans (silentRegion_trace_null y hn hy word).symm

theorem rankOne_iff_map_constant (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hp : s.placed = placementOfMap f) :
    RankOnePlacement s ↔ ∀ atom, f atom = f 0 := by
  constructor
  · rintro ⟨q, hq⟩ atom
    have hf : f = (fun _ => q) := placementOfMap_injective (hp.symm.trans hq)
    simp [hf]
  · intro h
    exact ⟨f 0, hp.trans (congrArg placementOfMap (funext h))⟩

theorem nonterminal_has_outside (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hp : s.placed = placementOfMap f)
    (h : ¬ RankOnePlacement s) : ∃ atom, f atom ≠ f 0 := by
  by_contra hn
  apply h
  apply (rankOne_iff_map_constant s f hp).mpr
  intro atom
  by_contra ha
  exact hn ⟨atom, ha⟩

theorem region_trichotomy (s : Execution n (ZMod n)) :
    SilentRegion s ∨ PairRegisterable s ∨ RegisteredNonterminal s := by
  by_cases hr : PairRegisterable s
  · exact Or.inr (Or.inl hr)
  · cases ho : s.origin with
    | none => exact Or.inl (Or.inl ⟨ho, hr⟩)
    | some record =>
        by_cases ht : RankOnePlacement s
        · exact Or.inl (Or.inr ⟨by simp [ho], ht⟩)
        · exact Or.inr (Or.inr ⟨by simp [ho], ht⟩)

omit [NeZero n] in
theorem registerable_not_registered (s : Execution n (ZMod n))
    (h : PairRegisterable s) : s.origin.isSome ≠ true := by simp [h.1]

theorem silentRegion_not_registerable (s : Execution n (ZMod n))
    (h : SilentRegion s) : ¬ PairRegisterable s := by
  rcases h with ⟨_, hr⟩ | ⟨hs, _⟩
  · exact hr
  · intro hr
    exact registerable_not_registered s hr hs

theorem silentRegion_not_registeredNonterminal (s : Execution n (ZMod n))
    (h : SilentRegion s) : ¬ RegisteredNonterminal s := by
  rcases h with ⟨hs, _⟩ | ⟨_, ht⟩
  · intro hr
    simpa [hs] using hr.1
  · intro hr
    exact hr.2 ht

omit [NeZero n] in
theorem registered_no_registration_output (s : Execution n (ZMod n))
    (a : Letter) (record : FusionRecord (ZMod n)) (hs : s.origin.isSome = true) :
    selectedOutput {0, 1} s a ≠ some (.registration record) := by
  cases a with
  | p => simp [selectedOutput]
  | d =>
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1
      all_goals simp [selectedOutput, h0, h1, hs]

omit [NeZero n] in
theorem registered_trace_no_registration (s : Execution n (ZMod n))
    (word : List Letter) (record : FusionRecord (ZMod n)) (hs : s.origin.isSome = true) :
    some (.registration record) ∉ eventTrace {0, 1} s word := by
  induction word generalizing s with
  | nil => simp [eventTrace]
  | cons a rest ih =>
      intro hm
      rcases List.mem_cons.mp hm with he | htail
      · exact registered_no_registration_output s a record hs he.symm
      · exact ih (step {0, 1} s a) (step_registered {0, 1} s a hs) htail

end FutureEvent
