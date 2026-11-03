import FutureEvent.SilentRegion

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- A registered nonterminal state must emit an event in its aligned sweep.
The comparison one-packet state is used only in the reconstruction theorem;
it is not substituted for any actual intermediate execution. -/
theorem registered_nonterminal_active_probe (s : Execution n (ZMod n))
    (hn : 3 ≤ n) (hg : PairGenerated s) (hr : RegisteredNonterminal s) :
    ∃ q : ZMod n,
      eventTrace {0, 1} s (registeredSweep q) ≠
        List.replicate (registeredSweep q).length none ∧
      (registeredSweep q).length ≤ 3 * n - 4 := by
  obtain ⟨lift, hp⟩ := pairGenerated_sourceOrdered s (by omega) hg
  let f := lift.position
  let t : Execution n (ZMod n) := { s with placed := placementOfMap (fun _ => f 0) }
  have ht : RankOnePlacement t := ⟨f 0, rfl⟩
  have htc : CarrierAt {0, 1} t (f 0) :=
    carrierAt_pair_of_map t (fun _ => f 0) (f 0) rfl rfl rfl
  refine ⟨f 0, ?_, registeredSweep_length_le _ (by omega)⟩
  intro hnull
  have htrace : eventTrace {0, 1} s (registeredSweep (f 0)) =
      eventTrace {0, 1} t (registeredSweep (f 0)) :=
    hnull.trans (rankOne_trace_null t (by omega) ht _).symm
  have heq := registeredSweep_aligned_injective {0, 1} s t f (fun _ => f 0) (f 0)
    (by omega) hp rfl (generated_registered_carrier s f (by omega) hg hp hr.1)
    htc hr.1 hr.1 htrace
  exact hr.2 ⟨f 0, heq⟩

theorem registerable_active_probe (s : Execution n (ZMod n))
    (hn : 3 ≤ n) (hg : PairGenerated s) (hr : PairRegisterable s) :
    ∃ (b : ZMod n) (g : ℕ),
      eventTrace {0, 1} s (gapProbe b g) ≠ List.replicate (gapProbe b g).length none ∧
      (gapProbe b g).length ≤ 3 * n - 6 := by
  obtain ⟨b, g, _, _, htrace, _, hbound⟩ := generated_registerable_probe s hn hg hr
  refine ⟨b, g, ?_, hbound⟩
  intro hnull
  have hm : some (.registration (pairRegistration n)) ∈ eventTrace {0, 1} s (gapProbe b g) := by
    rw [htrace]
    simp
  rw [hnull] at hm
  simp at hm

theorem registerable_silent_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x)
    (hx : PairRegisterable x) (hy : SilentRegion y) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 3 * n - 6 := by
  obtain ⟨b, g, hactive, hbound⟩ := registerable_active_probe x hn hxgen hx
  refine ⟨gapProbe b g, ?_, hbound⟩
  intro heq
  exact hactive (heq.trans (silentRegion_trace_null y (by omega) hy _))

theorem registered_silent_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x)
    (hx : RegisteredNonterminal x) (hy : SilentRegion y) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 3 * n - 4 := by
  obtain ⟨q, hactive, hbound⟩ := registered_nonterminal_active_probe x hn hxgen hx
  refine ⟨registeredSweep q, ?_, hbound⟩
  intro heq
  exact hactive (heq.trans (silentRegion_trace_null y (by omega) hy _))

/-- Registration and absorption remain different output tags even if an old
origin happens to equal the prospective registration record. -/
theorem registerable_registered_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x)
    (hx : PairRegisterable x) (hy : y.origin.isSome = true) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 3 * n - 6 := by
  obtain ⟨b, g, _, _, htrace, _, hbound⟩ := generated_registerable_probe x hn hxgen hx
  refine ⟨gapProbe b g, ?_, hbound⟩
  intro heq
  have hm : some (.registration (pairRegistration n)) ∈ eventTrace {0, 1} x (gapProbe b g) := by
    rw [htrace]
    simp
  rw [heq] at hm
  exact registered_trace_no_registration y (gapProbe b g) (pairRegistration n) hy hm

theorem registered_nonterminal_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hx : RegisteredNonterminal x) (hy : y.origin.isSome = true)
    (hne : x.placed ≠ y.placed) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 3 * n - 4 := by
  obtain ⟨xLift, hxp⟩ := pairGenerated_sourceOrdered x (by omega) hxgen
  obtain ⟨yLift, hyp⟩ := pairGenerated_sourceOrdered y (by omega) hygen
  obtain ⟨q, htrace, hbound⟩ := registered_sweep_separation x y xLift.position yLift.position hn
    hxgen hygen hxp hyp hx.1 hy (nonterminal_has_outside x xLift.position hxp hx.2) hne
  exact ⟨registeredSweep q, htrace, hbound⟩

theorem generated_alwaysSilent_iff (s : Execution n (ZMod n))
    (hn : 3 ≤ n) (hg : PairGenerated s) : AlwaysSilent s ↔ SilentRegion s := by
  constructor
  · intro hs
    rcases region_trichotomy s with hz | hr | ha
    · exact hz
    · obtain ⟨b, g, hactive, _⟩ := registerable_active_probe s hn hg hr
      exact False.elim (hactive (hs _))
    · obtain ⟨q, hactive, _⟩ := registered_nonterminal_active_probe s hn hg ha
      exact False.elim (hactive (hs _))
  · exact silentRegion_trace_null s (by omega)

/-- On the generated domain the silent-region test uses only the current
origin status and source fibers, not a search over future words. -/
theorem silentRegion_iff_currentShape (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hg : PairGenerated s)
    (hp : s.placed = placementOfMap f) :
    SilentRegion s ↔
      (s.origin = none ∧ ¬ SeparateSingletons f) ∨
        (s.origin.isSome = true ∧ ∀ atom, f atom = f 0) := by
  constructor
  · rintro (⟨ho, hr⟩ | ⟨ho, ht⟩)
    · refine Or.inl ⟨ho, ?_⟩
      intro hs
      exact hr ((generated_registerable_iff_singletons s f hn hg hp ho).mpr hs)
    · exact Or.inr ⟨ho, (rankOne_iff_map_constant s f hp).mp ht⟩
  · rintro (⟨ho, hs⟩ | ⟨ho, ht⟩)
    · refine Or.inl ⟨ho, ?_⟩
      intro hr
      exact hs ((generated_registerable_iff_singletons s f hn hg hp ho).mp hr)
    · exact Or.inr ⟨ho, (rankOne_iff_map_constant s f hp).mpr ht⟩

theorem generated_unregistered_same_placement_eq (x y : Execution n (ZMod n))
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hx : x.origin = none) (hy : y.origin = none) (hp : x.placed = y.placed) : x = y := by
  exact execution_ext x y hp (hx.trans hy.symm)
    ((generated_unregistered_chain_empty x hxgen hx).trans
      (generated_unregistered_chain_empty y hygen hy).symm)

end FutureEvent
