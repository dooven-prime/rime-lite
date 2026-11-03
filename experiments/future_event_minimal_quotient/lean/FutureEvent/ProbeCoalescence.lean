import FutureEvent.HoleMove

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def ProbeCoalesce (x y : Execution n (ZMod n)) (word : List Letter) : Prop :=
  eventTrace {0, 1} x word = eventTrace {0, 1} y word ∧
    (run {0, 1} x word).placed = (run {0, 1} y word).placed

omit [NeZero n] in
theorem eventTrace_length (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (word : List Letter) : (eventTrace F s word).length = word.length := by
  induction word generalizing s with
  | nil => rfl
  | cons a rest ih => simpa [eventTrace] using congrArg Nat.succ (ih (step F s a))

omit [NeZero n] in
theorem eventTrace_last_output (F : Finset (ZMod n)) (x y : Execution n (ZMod n))
    (lead : List Letter) (a : Letter)
    (h : eventTrace F x (lead ++ [a]) = eventTrace F y (lead ++ [a])) :
    selectedOutput F (run F x lead) a = selectedOutput F (run F y lead) a := by
  rw [eventTrace_append, eventTrace_append] at h
  have hd := congrArg (List.drop lead.length) h
  have hx := eventTrace_length F x lead
  have hy := eventTrace_length F y lead
  rw [← hx, List.drop_append_length] at hd
  rw [hx, ← hy, List.drop_append_length] at hd
  simpa only [eventTrace, List.cons.injEq, and_true] using hd

omit [NeZero n] in
theorem selected_registration_ports (s : Execution n (ZMod n))
    (h : selectedOutput {0, 1} s .d = some (.registration (pairRegistration n))) :
    s.origin = none ∧ s.placed 0 = some {0} ∧ s.placed 1 = some {1} := by
  cases h0 : s.placed 0 with
  | none => simp [selectedOutput, h0] at h
  | some u =>
      cases h1 : s.placed 1 with
      | none => simp [selectedOutput, h0, h1] at h
      | some v =>
          cases ho : s.origin with
          | none =>
              by_cases hu : u ∪ v = ({0, 1} : Finset (ZMod n))
              · have heq : (⟨u, v, u ∪ v⟩ : FusionRecord (ZMod n)) = pairRegistration n := by
                  simpa [selectedOutput, h0, h1, ho, hu] using h
                have hleft := congrArg FusionRecord.left heq
                have hright := congrArg FusionRecord.right heq
                exact ⟨rfl, by simpa [pairRegistration] using hleft,
                  by simpa [pairRegistration] using hright⟩
              · simp [selectedOutput, h0, h1, ho, hu] at h
          | some record =>
              by_cases hu : ({0, 1} : Finset (ZMod n)) ⊆ u <;>
                by_cases hv : ({0, 1} : Finset (ZMod n)) ⊆ v <;>
                  simp [selectedOutput, h0, h1, ho, hu, hv] at h

omit [NeZero n] in
theorem step_unregistered_records (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (a : Letter) (h : (step F s a).origin = none) :
    s.origin = none ∧ (step F s a).chain = s.chain := by
  have ho : s.origin = none := by
    cases hs : s.origin with
    | none => rfl
    | some record =>
        have hr := step_registered F s a (by simp [hs])
        rw [h] at hr
        simp at hr
  refine ⟨ho, ?_⟩
  cases a with
  | p => rfl
  | d =>
      unfold step stepDefect
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;> simp [ho]

omit [NeZero n] in
theorem run_unregistered_records (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (word : List Letter) (h : (run F s word).origin = none) :
    s.origin = none ∧ (run F s word).chain = s.chain := by
  induction word generalizing s with
  | nil => exact ⟨h, rfl⟩
  | cons a rest ih =>
      obtain ⟨ho, hc⟩ := ih (step F s a) h
      obtain ⟨hbefore, hchain⟩ := step_unregistered_records F s a ho
      exact ⟨hbefore, hc.trans hchain⟩

theorem generated_unregistered_chain_empty (s : Execution n (ZMod n))
    (hgen : PairGenerated s) (ho : s.origin = none) : s.chain = [] := by
  obtain ⟨history, rfl⟩ := hgen
  exact (run_unregistered_records {0, 1} (singletonExecution n) history ho).2

omit [NeZero n] in
theorem gapProbe_site (b q : ZMod n) (g : ℕ) :
    siteWord (gapProbe b g) q = collapsePosition (siteWord (gapPreFinal b g) q) := by
  simp [gapProbe, siteWord_append, siteWord, siteLetter]

omit [NeZero n] in
theorem collapse_injective_off_zero (q q' : ZMod n)
    (heq : collapsePosition q = collapsePosition q')
    (hne : collapsePosition q ≠ 0) : q = q' ∧ q ≠ 1 := by
  have hq : q ≠ 1 := by intro h; simp [collapsePosition, h] at hne
  have hq' : q' ≠ 1 := by
    intro h
    apply hne
    rw [heq, h]
    simp [collapsePosition]
  exact ⟨by simpa [collapsePosition, hq, hq'] using heq, hq⟩

theorem gapProbe_injective_off_zero (b q q' : ZMod n) (g : ℕ)
    (heq : siteWord (gapProbe b g) q = siteWord (gapProbe b g) q')
    (hne : siteWord (gapProbe b g) q ≠ 0) : q = q' := by
  rw [gapProbe_site, gapProbe_site] at heq
  rw [gapProbe_site] at hne
  obtain ⟨hpre, hnotone⟩ := collapse_injective_off_zero _ _ heq hne
  exact gapPreFinal_injective_off_one b q q' g hpre hnotone

theorem gapProbe_outside_nonzero (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated x)
    (hplaced : x.placed = placementOfMap f) (hreg : PairRegisterable x)
    (atom : ZMod n) (hz : atom ≠ 0) (ho : atom ≠ 1) :
    siteWord (gapProbe (f 1) (f 1 - f 0).val) (f atom) ≠ 0 := by
  obtain ⟨hs, hgpos, hgmax, _, _, hsupport⟩ :=
    registerable_gap_admission x f hn hgen hplaced hreg
  intro hfinal
  rw [gapProbe_site] at hfinal
  by_cases hpre : siteWord (gapPreFinal (f 1) (f 1 - f 0).val) (f atom) = 1
  · have hatom := hs.2 atom (hsupport atom ((gapPreFinal_one_iff _ _ _ hgpos).mp hpre))
    exact ho hatom
  · have hzero : siteWord (gapPreFinal (f 1) (f 1 - f 0).val) (f atom) = 0 := by
      simpa [collapsePosition, hpre] using hfinal
    have hsite := (gapPreFinal_zero_iff _ _ _ hgpos (by omega)).mp hzero
    have hleft : f 1 - ((f 1 - f 0).val : ZMod n) = f 0 := by
      rw [ZMod.natCast_zmod_val]
      ring
    exact hz (hs.1 atom (hsite.trans hleft))

omit [NeZero n] in
theorem holeMove_equal_initial_sites (f : ZMod n → ZMod n) (h : ℕ)
    (hone : SingletonSource f 1) (a b : ZMod n) (heq : f a = f b) :
    holeMoveSites f h a = holeMoveSites f h b := by
  by_cases ha : a = 1
  · subst a
    have hb : b = 1 := hone b heq.symm
    simp [hb]
  · by_cases hb : b = 1
    · subst b
      exact False.elim (ha (hone a heq))
    · simp [holeMoveSites, ha, hb, heq]

theorem holeMove_prefix_map (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated x)
    (hplaced : x.placed = placementOfMap f) (hreg : PairRegisterable x)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    siteWord (gapPreFinal (f 1) (f 1 - f 0).val) ∘ holeMoveSites f h =
      siteWord (gapPreFinal (f 1) (f 1 - f 0).val) ∘ f := by
  obtain ⟨_, hgpos, hgmax, _, _, _⟩ := registerable_gap_admission x f hn hgen hplaced hreg
  funext atom
  by_cases ha : atom = 1
  · subst atom
    simp only [Function.comp_apply, holeMoveSites, ite_true]
    have hd : (f 1 - (f 0 + (h : ZMod n))).val = (f 1 - f 0).val - h := by
      have hc : f 1 - (f 0 + (h : ZMod n)) =
          (((f 1 - f 0).val - h : ℕ) : ZMod n) := by
        rw [Nat.cast_sub hle, ZMod.natCast_zmod_val]
        ring
      rw [hc, ZMod.val_natCast_of_lt (by omega)]
    have hmoved := (gapPreFinal_one_iff (f 1) (f 0 + (h : ZMod n)) (f 1 - f 0).val hgpos).mpr
      (by rw [hd]; omega)
    have horiginal := (gapPreFinal_one_iff (f 1) (f 1) (f 1 - f 0).val hgpos).mpr
      (by simp only [sub_self, ZMod.val_zero]; omega)
    exact hmoved.trans horiginal.symm
  · simp [Function.comp_apply, holeMoveSites, ha]

/-- Moving source one inside the gap gives the same literal pre-final state,
and hence the same actual terminal execution, not just equal counts. -/
theorem holeMove_probe_same_run (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated x)
    (hplaced : x.placed = placementOfMap f) (hreg : PairRegisterable x)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    let word := gapProbe (f 1) (f 1 - f 0).val
    eventTrace {0, 1} x word = eventTrace {0, 1} (holeMoveExecution x f h) word ∧
      run {0, 1} x word = run {0, 1} (holeMoveExecution x f h) word := by
  let lead := gapPreFinal (f 1) (f 1 - f 0).val
  let y := holeMoveExecution x f h
  have hmap := holeMove_prefix_map x f hn hgen hplaced hreg h hpos hle
  obtain ⟨hs, hgpos, _, _, _, hsupport⟩ := registerable_gap_admission x f hn hgen hplaced hreg
  have hxFree := registerable_gap_prefix_fusionFree x f hn hgen hplaced hreg
  have hyFree : FusionFree {0, 1} y lead := by
    apply fusionFree_of_final_site_injective {0, 1} y (holeMoveSites f h) lead (by omega) rfl
    intro a b heq
    have ha := congrFun hmap a
    have hb := congrFun hmap b
    change siteWord lead (holeMoveSites f h a) = siteWord lead (f a) at ha
    change siteWord lead (holeMoveSites f h b) = siteWord lead (f b) at hb
    have hf : siteWord lead (f a) = siteWord lead (f b) := ha.symm.trans (heq.trans hb)
    have hinitial := gapPreFinal_injective_on_initial_sites (f 1) _ hgpos f hsupport a b hf
    exact holeMove_equal_initial_sites f h hs.2 a b hinitial
  have hp : (run {0, 1} x lead).placed = (run {0, 1} y lead).placed := by
    rw [atomSite_run {0, 1} x f lead (by omega) hplaced,
      atomSite_run {0, 1} y (holeMoveSites f h) lead (by omega) rfl, hmap]
  obtain ⟨hxo, hxc, hxt⟩ := fusionFree_records_and_trace {0, 1} x lead hxFree
  obtain ⟨hyo, hyc, hyt⟩ := fusionFree_records_and_trace {0, 1} y lead hyFree
  have hstates : run {0, 1} x lead = run {0, 1} y lead :=
    execution_ext _ _ hp (hxo.trans hyo.symm) (hxc.trans hyc.symm)
  constructor
  · change eventTrace {0, 1} x (lead ++ [.d]) = eventTrace {0, 1} y (lead ++ [.d])
    rw [eventTrace_append, eventTrace_append, hxt, hyt, hstates]
  · change run {0, 1} x (lead ++ [.d]) = run {0, 1} y (lead ++ [.d])
    rw [run_append, run_append, hstates]

theorem holeMove_probe_coalesces (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated x)
    (hplaced : x.placed = placementOfMap f) (hreg : PairRegisterable x)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    ProbeCoalesce x (holeMoveExecution x f h) (gapProbe (f 1) (f 1 - f 0).val) := by
  obtain ⟨ht, hr⟩ := holeMove_probe_same_run x f hn hgen hplaced hreg h hpos hle
  exact ⟨ht, congrArg Execution.placed hr⟩

theorem holeMove_registerable (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated x)
    (hplaced : x.placed = placementOfMap f) (hreg : PairRegisterable x)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    PairRegisterable (holeMoveExecution x f h) := by
  obtain ⟨hs, _⟩ := registerable_gap_admission x f hn hgen hplaced hreg
  have hx := (generated_singletons_probe x f hn hgen hplaced hreg.1 hs).2.1
  have hr := (holeMove_probe_same_run x f hn hgen hplaced hreg h hpos hle).2
  refine ⟨hreg.1, gapProbe (f 1) (f 1 - f 0).val, ?_⟩
  rw [← hr, hx]
  rfl

theorem holeMove_parameter_injective (x : Execution n (ZMod n))
    (f : ZMod n → ZMod n) {h h' : ℕ} (hh : h < n) (hh' : h' < n)
    (heq : holeMoveExecution x f h = holeMoveExecution x f h') : h = h' := by
  have hp := congrArg Execution.placed heq
  have hf := congrFun (placementOfMap_injective hp) 1
  have hc : (h : ZMod n) = (h' : ZMod n) := by
    simpa [holeMoveSites] using congrArg (fun q : ZMod n => q - f 0) hf
  exact natCast_injective_below_modulus hh hh' hc

/-- Equal complete traces fix both ordered terminal parents. Equal literal
endpoints then recover every outside atom at its unique nonzero site fiber. -/
theorem probe_coalescence_recovers_holeMove (x y : Execution n (ZMod n))
    (f fy : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hxplaced : x.placed = placementOfMap f) (hyplaced : y.placed = placementOfMap fy)
    (hxreg : PairRegisterable x) (hyreg : PairRegisterable y)
    (hco : ProbeCoalesce x y (gapProbe (f 1) (f 1 - f 0).val)) :
    ∃ h, 1 ≤ h ∧ h ≤ (f 1 - f 0).val ∧ y = holeMoveExecution x f h := by
  let b := f 1
  let g := (f 1 - f 0).val
  let lead := gapPreFinal b g
  obtain ⟨_, hgpos, hgmax, hz, ho, hsupport⟩ :=
    registerable_gap_admission x f hn hxgen hxplaced hxreg
  obtain ⟨hxp0, hxp1⟩ := gapPreFinal_ports {0, 1} x f b g (by omega)
    hgpos (by omega) hxplaced hz ho hsupport
  change (run {0, 1} x lead).placed 0 = some {0} at hxp0
  change (run {0, 1} x lead).placed 1 = some {1} at hxp1
  have hxo : (run {0, 1} x lead).origin = none :=
    (fusionFree_records_and_trace {0, 1} x lead
      (registerable_gap_prefix_fusionFree x f hn hxgen hxplaced hxreg)).1.trans hxreg.1
  have hxout : selectedOutput {0, 1} (run {0, 1} x lead) .d =
      some (.registration (pairRegistration n)) := by
    simp [selectedOutput, hxp0, hxp1, hxo, pairRegistration]
  have hyout := (eventTrace_last_output {0, 1} x y lead .d hco.1).symm.trans hxout
  obtain ⟨_, hyp0, hyp1⟩ := selected_registration_ports (run {0, 1} y lead) hyout
  have hypmap := atomSite_run {0, 1} y fy lead (by omega) hyplaced
  have hyfiber0 := (placementOfMap_some_iff (siteWord lead ∘ fy) 0 {0}).mp (hypmap ▸ hyp0)
  have hyfiber1 := (placementOfMap_some_iff (siteWord lead ∘ fy) 1 {1}).mp (hypmap ▸ hyp1)
  have hy0 : siteWord lead (fy 0) = 0 := by
    apply (mem_sourceFiber (siteWord lead ∘ fy) 0 0).mp
    rw [hyfiber0.1]
    simp
  have hy1 : siteWord lead (fy 1) = 1 := by
    apply (mem_sourceFiber (siteWord lead ∘ fy) 1 1).mp
    rw [hyfiber1.1]
    simp
  have hleft : b - (g : ZMod n) = f 0 := by
    dsimp [b, g]
    rw [ZMod.natCast_zmod_val]
    ring
  have hyzero : fy 0 = f 0 :=
    ((gapPreFinal_zero_iff b (fy 0) g hgpos (by dsimp [g]; omega)).mp hy0).trans hleft
  have hdist : (b - fy 1).val < g := (gapPreFinal_one_iff b (fy 1) g hgpos).mp hy1
  let h := g - (b - fy 1).val
  have hpos : 1 ≤ h := by dsimp [h]; omega
  have hle : h ≤ g := Nat.sub_le _ _
  have hyone : fy 1 = f 0 + (h : ZMod n) := by
    change fy 1 = f 0 + (((f 1 - f 0).val - (f 1 - fy 1).val : ℕ) : ZMod n)
    rw [Nat.cast_sub (by exact Nat.le_of_lt hdist),
      ZMod.natCast_zmod_val, ZMod.natCast_zmod_val]
    ring
  have hsites := (run_placed_eq_iff_atomSites {0, 1} x y f fy
    (gapProbe b g) (by omega) hxplaced hyplaced).mp hco.2
  have houtside (atom : ZMod n) (hzero : atom ≠ 0) (hone : atom ≠ 1) :
      fy atom = f atom := by
    exact (gapProbe_injective_off_zero b (f atom) (fy atom) g (hsites atom)
      (gapProbe_outside_nonzero x f hn hxgen hxplaced hxreg atom hzero hone)).symm
  have hmap : fy = holeMoveSites f h := by
    funext atom
    by_cases hone : atom = 1
    · subst atom
      simpa [holeMoveSites] using hyone
    · by_cases hzero : atom = 0
      · subst atom
        simpa [holeMoveSites, hone] using hyzero
      · simpa [holeMoveSites, hone] using houtside atom hzero hone
  refine ⟨h, hpos, hle, execution_ext y (holeMoveExecution x f h) ?_ ?_ ?_⟩
  · exact hyplaced.trans (congrArg placementOfMap hmap)
  · simp only [holeMoveExecution, hyreg.1, hxreg.1]
  · simp only [holeMoveExecution,
      generated_unregistered_chain_empty y hygen hyreg.1,
      generated_unregistered_chain_empty x hxgen hxreg.1]

/-- Lemma 5.3 on the actual generated registerable domain; the comparison
parameter is unique and the case h=g is retained. -/
theorem gapProbe_coalesces_iff_holeMove (x y : Execution n (ZMod n))
    (f fy : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hxplaced : x.placed = placementOfMap f) (hyplaced : y.placed = placementOfMap fy)
    (hxreg : PairRegisterable x) (hyreg : PairRegisterable y) :
    ProbeCoalesce x y (gapProbe (f 1) (f 1 - f 0).val) ↔
      ∃! h, 1 ≤ h ∧ h ≤ (f 1 - f 0).val ∧ y = holeMoveExecution x f h := by
  constructor
  · intro hco
    obtain ⟨h, hpos, hle, hy⟩ := probe_coalescence_recovers_holeMove
      x y f fy hn hxgen hygen hxplaced hyplaced hxreg hyreg hco
    refine ⟨h, ⟨hpos, hle, hy⟩, ?_⟩
    rintro h' ⟨_, hle', hy'⟩
    exact holeMove_parameter_injective x f
      (lt_of_le_of_lt hle' (ZMod.val_lt _)) (lt_of_le_of_lt hle (ZMod.val_lt _))
      (hy'.symm.trans hy)
  · rintro ⟨h, ⟨hpos, hle, rfl⟩, _⟩
    exact holeMove_probe_coalesces x f hn hxgen hxplaced hxreg h hpos hle

theorem holeMove_identity (x : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (hplaced : x.placed = placementOfMap f) :
    holeMoveExecution x f (f 1 - f 0).val = x := by
  have hmap : holeMoveSites f (f 1 - f 0).val = f := by
    funext atom
    by_cases ha : atom = 1
    · simp only [holeMoveSites, ha, ite_true]
      rw [ZMod.natCast_zmod_val]
      ring
    · simp [holeMoveSites, ha]
  exact execution_ext _ _ ((congrArg placementOfMap hmap).trans hplaced.symm) rfl rfl

omit [NeZero n] in
theorem holeMove_gap (f : ZMod n → ZMod n) (h : ℕ) (hn : 2 ≤ n) (hh : h < n) :
    (holeMoveSites f h 1 - holeMoveSites f h 0).val = h := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro heq
    have := ZMod.one_eq_zero_iff.mp heq.symm
    omega
  simp [holeMoveSites, h01, ZMod.val_natCast_of_lt hh]

theorem holeMove_eq_source_iff (x : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (hplaced : x.placed = placementOfMap f) (h : ℕ) (hh : h < n) :
    holeMoveExecution x f h = x ↔ h = (f 1 - f 0).val := by
  constructor
  · intro heq
    exact holeMove_parameter_injective x f hh (ZMod.val_lt _)
      (heq.trans (holeMove_identity x f hplaced).symm)
  · intro heq
    rw [heq, holeMove_identity x f hplaced]

/-- Only nonidentity coalescing comparisons give a strict directed gap drop. -/
theorem probe_coalescence_strict_gap (x y : Execution n (ZMod n))
    (f fy : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hxplaced : x.placed = placementOfMap f) (hyplaced : y.placed = placementOfMap fy)
    (hxreg : PairRegisterable x) (hyreg : PairRegisterable y) (hxy : x ≠ y)
    (hco : ProbeCoalesce x y (gapProbe (f 1) (f 1 - f 0).val)) :
    (fy 1 - fy 0).val < (f 1 - f 0).val := by
  obtain ⟨h, _, hle, hyeq⟩ := probe_coalescence_recovers_holeMove
    x y f fy hn hxgen hygen hxplaced hyplaced hxreg hyreg hco
  have hh : h < n := lt_of_le_of_lt hle (ZMod.val_lt _)
  have hp := hyplaced.symm.trans (congrArg Execution.placed hyeq)
  have hf : fy = holeMoveSites f h := placementOfMap_injective hp
  have hgap : (fy 1 - fy 0).val = h := by
    rw [hf]
    exact holeMove_gap f h (by omega) hh
  have hneq : h ≠ (f 1 - f 0).val := by
    intro heq
    rw [heq, holeMove_identity x f hxplaced] at hyeq
    exact hxy hyeq.symm
  omega

end FutureEvent
