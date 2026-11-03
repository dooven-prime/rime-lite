import FutureEvent.RegisteredDomain

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem eventTrace_next_output (x y : Execution n (ZMod n))
    (lead rest : List Letter) (a : Letter)
    (h : eventTrace {0, 1} x (lead ++ a :: rest) =
      eventTrace {0, 1} y (lead ++ a :: rest)) :
    selectedOutput {0, 1} (run {0, 1} x lead) a =
      selectedOutput {0, 1} (run {0, 1} y lead) a := by
  rw [eventTrace_append, eventTrace_append] at h
  have hd := congrArg (List.drop lead.length) h
  have hx := eventTrace_length {0, 1} x lead
  have hy := eventTrace_length {0, 1} y lead
  rw [← hx, List.drop_append_length] at hd
  rw [hx, ← hy, List.drop_append_length] at hd
  exact (List.cons.inj hd).1

omit [NeZero n] in
theorem registeredSweep_tail_trace (x y : Execution n (ZMod n)) (q : ZMod n)
    (h : eventTrace {0, 1} x (registeredSweep q) =
      eventTrace {0, 1} y (registeredSweep q)) :
    eventTrace {0, 1} (run {0, 1} x (pWord (-q).val)) (sweepCore (n - 2)) =
      eventTrace {0, 1} (run {0, 1} y (pWord (-q).val)) (sweepCore (n - 2)) := by
  rw [registeredSweep, eventTrace_append, eventTrace_append] at h
  have hx := (fusionFree_records_and_trace {0, 1} x (pWord (-q).val)
    (fusionFree_pWord {0, 1} x _)).2.2
  have hy := (fusionFree_records_and_trace {0, 1} y (pWord (-q).val)
    (fusionFree_pWord {0, 1} y _)).2.2
  rw [hx, hy] at h
  exact List.append_cancel_left h

/-- The left-parent direction decodes its initial site from this output
alone, a stronger statement than requiring it to be the first event. -/
theorem sweep_left_parent_phase_decoder (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (record : FusionRecord (ZMod n))
    (k : ℕ) (hn : 2 ≤ n) (hk : k + 2 < n)
    (hp : s.placed = placementOfMap f)
    (he : selectedOutput {0, 1} (run {0, 1} s (sweepBeforeDefect k)) .d =
      some (.absorption record)) (ha : (0 : ZMod n) ∈ record.left) :
    f 0 = -((k + 1 : ℕ) : ZMod n) := by
  have hsite := selected_absorption_left_site _
    (siteWord (sweepBeforeDefect k) ∘ f) record 0
    (atomSite_run {0, 1} s f _ hn hp) he ha
  exact (sweepBeforeDefect_zero_iff k (f 0) hk).mp hsite

theorem sweep_initial_right_phase_decoder (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (record : FusionRecord (ZMod n))
    (hp : s.placed = placementOfMap f)
    (he : selectedOutput {0, 1} s .d = some (.absorption record))
    (ha : (0 : ZMod n) ∈ record.right) : f 0 = 1 :=
  selected_absorption_right_site s f record 0 hp he ha

theorem sweep_initial_left_phase_decoder (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (record : FusionRecord (ZMod n))
    (hp : s.placed = placementOfMap f)
    (he : selectedOutput {0, 1} s .d = some (.absorption record))
    (ha : (0 : ZMod n) ∈ record.left) : f 0 = 0 :=
  selected_absorption_left_site s f record 0 hp he ha

/-- An outside anchor belongs only to the first state. No packet or site
assumption is imposed on the comparison state at the anchor coordinate. -/
theorem sweepCore_outside_anchor_phase (x y : Execution n (ZMod n))
    (f g : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxreg : x.origin.isSome = true) (hpair : f 0 = f 1)
    (hnot : f 0 ≠ 0) (hanchor : ∃ atom, f atom = 0)
    (ht : eventTrace {0, 1} x (sweepCore (n - 2)) =
      eventTrace {0, 1} y (sweepCore (n - 2))) : g 0 = f 0 := by
  obtain ⟨anchor, ha⟩ := hanchor
  by_cases hright : f 0 = 1
  · let record : FusionRecord (ZMod n) :=
      ⟨sourceFiber f 0, sourceFiber f 1, sourceFiber f 0 ∪ sourceFiber f 1⟩
    have hleftport : x.placed 0 = some (sourceFiber f 0) := by
      rw [hx]
      exact (placementOfMap_some_iff f 0 _).mpr ⟨rfl, ⟨anchor, by simp [ha]⟩⟩
    have hrightport : x.placed 1 = some (sourceFiber f 1) := by
      rw [hx]
      exact (placementOfMap_some_iff f 1 _).mpr ⟨rfl, ⟨0, by simp [hright]⟩⟩
    have hsubset : ({0, 1} : Finset (ZMod n)) ⊆ sourceFiber f 1 := by
      intro atom hm
      simp only [Finset.mem_insert, Finset.mem_singleton] at hm
      rcases hm with rfl | rfl <;> simp [hright, ← hpair]
    have he : selectedOutput {0, 1} x .d = some (.absorption record) := by
      simp [selectedOutput, hxreg, hleftport, hrightport, hsubset, record]
    have heq := (List.cons.inj ht).1
    have hyout : selectedOutput {0, 1} y .d = some (.absorption record) := heq.symm.trans he
    exact (sweep_initial_right_phase_decoder y g record hy hyout
      (by simpa [record] using (show 0 ∈ sourceFiber f 1 by simp [hright]))).trans hright.symm
  · let d := (-f 0).val
    have hdpos : 1 ≤ d := by
      by_contra h
      have hz : d = 0 := by omega
      have hc := congrArg (fun t : ℕ => (t : ZMod n)) hz
      have hf0 : f 0 = 0 := by simpa [d] using congrArg Neg.neg hc
      exact hnot hf0
    have hdmax : d ≤ n - 2 := by
      simpa [d, collapsePosition, hright] using neg_collapse_val_le (f 0) (by omega : 2 ≤ n)
    let k := d - 1
    have hk : k + 2 < n := by dsimp [k]; omega
    have hf0 : f 0 = -((k + 1 : ℕ) : ZMod n) := by
      have hkcast : k + 1 = d := by dsimp [k]; omega
      rw [hkcast]
      simp [d]
    let word := sweepBeforeDefect k
    let xp := run {0, 1} x word
    let fp := siteWord word ∘ f
    have hxp : xp.placed = placementOfMap fp := atomSite_run {0, 1} x f word (by omega) hx
    have hzero : fp 0 = 0 := (sweepBeforeDefect_zero_iff k (f 0) hk).mpr hf0
    have hone : fp anchor = 1 := by
      change siteWord (sweepBeforeDefect k) (f anchor) = 1
      rw [ha]
      exact sweepBeforeDefect_anchor k (by omega)
    let record : FusionRecord (ZMod n) :=
      ⟨sourceFiber fp 0, sourceFiber fp 1, sourceFiber fp 0 ∪ sourceFiber fp 1⟩
    have hleftport : xp.placed 0 = some (sourceFiber fp 0) := by
      rw [hxp]
      exact (placementOfMap_some_iff fp 0 _).mpr ⟨rfl, ⟨0, by simp [hzero]⟩⟩
    have hrightport : xp.placed 1 = some (sourceFiber fp 1) := by
      rw [hxp]
      exact (placementOfMap_some_iff fp 1 _).mpr ⟨rfl, ⟨anchor, by simp [hone]⟩⟩
    have hsubset : ({0, 1} : Finset (ZMod n)) ⊆ sourceFiber fp 0 := by
      intro atom hm
      simp only [Finset.mem_insert, Finset.mem_singleton] at hm
      rcases hm with rfl | rfl
      · simp [hzero]
      · have heq : fp 1 = fp 0 := congrArg (siteWord word) hpair.symm
        simp [heq, hzero]
    have he : selectedOutput {0, 1} xp .d = some (.absorption record) := by
      simp [selectedOutput, run_registered x word hxreg, xp, hleftport, hrightport,
        hsubset, record]
    have hsplit := sweepCore_split (n := n) k hk
    rw [hsplit] at ht
    have heq := eventTrace_next_output x y word (pdWord (n - 3 - k)) .d ht
    have hyout : selectedOutput {0, 1} (run {0, 1} y word) .d = some (.absorption record) :=
      heq.symm.trans he
    exact (sweep_left_parent_phase_decoder y g record k (by omega) hk hy hyout
      (by simpa [record] using (show 0 ∈ sourceFiber fp 0 by simp [hzero]))).trans hf0.symm

/-- Lemma 4.3 in physical coordinates, without any anchor premise on y. -/
theorem registeredSweep_outside_anchor_phase (x y : Execution n (ZMod n))
    (f g : ZMod n → ZMod n) (q : ZMod n) (hn : 3 ≤ n)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxreg : x.origin.isSome = true) (hpair : f 0 = f 1)
    (hnot : f 0 ≠ q) (hanchor : ∃ atom, f atom = q)
    (ht : eventTrace {0, 1} x (registeredSweep q) =
      eventTrace {0, 1} y (registeredSweep q)) : g 0 = f 0 := by
  let xr := run {0, 1} x (pWord (-q).val)
  let yr := run {0, 1} y (pWord (-q).val)
  let fr := fun atom => f atom - q
  let gr := fun atom => g atom - q
  have hxr : xr.placed = placementOfMap fr := by
    simpa [xr, fr, siteWord_pWord, Function.comp_def, sub_eq_add_neg] using
      atomSite_run {0, 1} x f (pWord (-q).val) (by omega) hx
  have hyr : yr.placed = placementOfMap gr := by
    simpa [yr, gr, siteWord_pWord, Function.comp_def, sub_eq_add_neg] using
      atomSite_run {0, 1} y g (pWord (-q).val) (by omega) hy
  have heq := sweepCore_outside_anchor_phase xr yr fr gr hn hxr hyr
    (run_registered x _ hxreg) (by simp [fr, hpair])
    (by simpa [fr] using sub_ne_zero.mpr hnot)
    (by obtain ⟨atom, ha⟩ := hanchor; exact ⟨atom, by simp [fr, ha]⟩)
    (registeredSweep_tail_trace x y q ht)
  exact add_right_cancel (show g 0 + -q = f 0 + -q by
    simpa only [gr, fr, sub_eq_add_neg] using heq)

/-- Registered placement separation, with one common actual sweep word and
the stated linear raw-letter bound. -/
theorem registered_sweep_separation (x y : Execution n (ZMod n))
    (f g : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (houtside : ∃ atom, f atom ≠ f 0) (hne : x.placed ≠ y.placed) :
    ∃ q : ZMod n,
      eventTrace {0, 1} x (registeredSweep q) ≠ eventTrace {0, 1} y (registeredSweep q) ∧
      (registeredSweep q).length ≤ 3 * n - 4 := by
  have hxc := generated_registered_carrier x f (by omega) hxgen hx hxreg
  have hyc := generated_registered_carrier y g (by omega) hygen hy hyreg
  by_cases hphase : f 0 = g 0
  · refine ⟨f 0, ?_, registeredSweep_length_le _ (by omega)⟩
    intro ht
    apply hne
    exact registeredSweep_aligned_injective {0, 1} x y f g (f 0) (by omega)
      hx hy hxc (by simpa [hphase] using hyc) hxreg hyreg ht
  · obtain ⟨atom, ha⟩ := houtside
    refine ⟨f atom, ?_, registeredSweep_length_le _ (by omega)⟩
    intro ht
    apply hphase
    exact (registeredSweep_outside_anchor_phase x y f g (f atom) hn hx hy hxreg
      (generated_registered_colocated x f (by omega) hxgen hx hxreg)
      ha.symm ⟨atom, rfl⟩ ht).symm

end FutureEvent
