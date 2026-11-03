import FutureEvent.SweepSeparation

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem gapProbe_trace_registration_origin (s : Execution n (ZMod n))
    (b : ZMod n) (g : ℕ)
    (h : eventTrace {0, 1} s (gapProbe b g) =
      List.replicate (gapPreFinal b g).length none ++
        [some (.registration (pairRegistration n))]) :
    (run {0, 1} s (gapProbe b g)).origin = some (pairRegistration n) := by
  rw [gapProbe, eventTrace_append] at h
  have hd := congrArg (List.drop (gapPreFinal b g).length) h
  have hlen := eventTrace_length {0, 1} s (gapPreFinal b g)
  rw [← hlen, List.drop_append_length] at hd
  rw [hlen] at hd
  have hdrop : List.drop (gapPreFinal b g).length
      (List.replicate (gapPreFinal b g).length (none : Option (SelectedEvent (ZMod n))) ++
        [some (.registration (pairRegistration n))]) =
      [some (.registration (pairRegistration n))] := by
    simpa only [List.length_replicate] using
      (List.drop_append_length (l₁ := List.replicate (gapPreFinal b g).length
        (none : Option (SelectedEvent (ZMod n))))
        (l₂ := [some (.registration (pairRegistration n))]))
  rw [hdrop] at hd
  have hout : selectedOutput {0, 1} (run {0, 1} s (gapPreFinal b g)) .d =
      some (.registration (pairRegistration n)) := (List.cons.inj hd).1
  obtain ⟨ho, h0, h1⟩ := selected_registration_ports _ hout
  rw [gapProbe, run_append]
  change (stepDefect {0, 1} (run {0, 1} s (gapPreFinal b g))).origin = _
  simp [stepDefect, ho, h0, h1, pairRegistration]

theorem registerable_probe_terminal_outside (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hg : PairGenerated s)
    (hp : s.placed = placementOfMap f) (hr : PairRegisterable s) :
    ∃ atom, siteWord (gapProbe (f 1) (f 1 - f 0).val) (f atom) ≠
      siteWord (gapProbe (f 1) (f 1 - f 0).val) (f 0) := by
  obtain ⟨_, hgpos, hgmax, _, _, _⟩ := registerable_gap_admission s f hn hg hp hr
  have h0 : siteWord (gapProbe (f 1) (f 1 - f 0).val) (f 0) = 0 := by
    rw [gapProbe_site]
    have hpre : siteWord (gapPreFinal (f 1) (f 1 - f 0).val) (f 0) = 0 := by
      apply (gapPreFinal_zero_iff _ _ _ hgpos (by omega)).mpr
      rw [ZMod.natCast_zmod_val]
      ring
    rw [hpre]
    simp [collapsePosition]
  have h20 : (2 : ZMod n) ≠ 0 := by
    intro he
    have hv := congrArg ZMod.val he
    have hv2 : (2 : ZMod n).val = 2 := by
      simpa using ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega : 2 < n)
    rw [hv2, ZMod.val_zero] at hv
    omega
  have h21 : (2 : ZMod n) ≠ 1 := by
    intro he
    have hv := congrArg ZMod.val he
    have h2 := ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega : 2 < n)
    have h1 := ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega : 1 < n)
    norm_num at h2 h1
    omega
  refine ⟨2, ?_⟩
  rw [h0]
  exact gapProbe_outside_nonzero s f hn hg hp hr 2 h20 h21

/-- Choose the smaller-gap source's probe. Equal traces then force different
registered nonterminal endpoints, where one common sweep completes separation. -/
theorem smaller_gap_two_probe_separation (x y : Execution n (ZMod n))
    (f g : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxreg : PairRegisterable x) (hyreg : PairRegisterable y) (hne : x ≠ y)
    (hle : (f 1 - f 0).val ≤ (g 1 - g 0).val) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 6 * n - 10 := by
  obtain ⟨hs, _, _, _, _, _⟩ := registerable_gap_admission x f hn hxgen hx hxreg
  obtain ⟨htrace, horigin, _, hlength⟩ :=
    generated_singletons_probe x f hn hxgen hx hxreg.1 hs
  let v := gapProbe (f 1) (f 1 - f 0).val
  by_cases ht : eventTrace {0, 1} x v = eventTrace {0, 1} y v
  · let xv := run {0, 1} x v
    let yv := run {0, 1} y v
    let fv := siteWord v ∘ f
    let gv := siteWord v ∘ g
    have hxv : xv.placed = placementOfMap fv := atomSite_run {0, 1} x f v (by omega) hx
    have hyv : yv.placed = placementOfMap gv := atomSite_run {0, 1} y g v (by omega) hy
    have hxvr : xv.origin.isSome = true := by simp [xv, v, horigin]
    have hyvo := gapProbe_trace_registration_origin y (f 1) (f 1 - f 0).val
      (ht.symm.trans htrace)
    have hyvr : yv.origin.isSome = true := by simp [yv, v, hyvo]
    have hneq : xv.placed ≠ yv.placed := by
      intro heq
      have hdrop := probe_coalescence_strict_gap x y f g hn hxgen hygen hx hy hxreg hyreg
        hne ⟨ht, heq⟩
      omega
    obtain ⟨q, hsep, hbound⟩ := registered_sweep_separation xv yv fv gv hn
      (pairGenerated_run x v hxgen) (pairGenerated_run y v hygen) hxv hyv hxvr hyvr
      (registerable_probe_terminal_outside x f hn hxgen hx hxreg) hneq
    refine ⟨v ++ registeredSweep q, ?_, ?_⟩
    · intro heq
      rw [eventTrace_append, eventTrace_append, ht] at heq
      exact hsep (List.append_cancel_left heq)
    · rw [List.length_append]
      change v.length ≤ 3 * n - 6 at hlength
      omega
  · exact ⟨v, ht, by change v.length ≤ 3 * n - 6 at hlength; omega⟩

/-- The linear distinguishing bound for two distinct actual registerable
states. Other observation classes are not part of this theorem. -/
theorem registerable_pair_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hxreg : PairRegisterable x) (hyreg : PairRegisterable y) (hne : x ≠ y) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 6 * n - 10 := by
  obtain ⟨xLift, hx⟩ := pairGenerated_sourceOrdered x (by omega) hxgen
  obtain ⟨yLift, hy⟩ := pairGenerated_sourceOrdered y (by omega) hygen
  by_cases hle : (xLift.position 1 - xLift.position 0).val ≤
      (yLift.position 1 - yLift.position 0).val
  · exact smaller_gap_two_probe_separation x y xLift.position yLift.position hn
      hxgen hygen hx hy hxreg hyreg hne hle
  · obtain ⟨word, htrace, hlength⟩ := smaller_gap_two_probe_separation y x
      yLift.position xLift.position hn hygen hxgen hy hx hyreg hxreg hne.symm (by omega)
    exact ⟨word, htrace.symm, hlength⟩

end FutureEvent
