import FutureEvent.SweepSites

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} {α : Type*} [DecidableEq α]

def CarrierAt (F : Finset α) (s : Execution n α) (q : ZMod n) : Prop :=
  ∃ B, s.placed q = some B ∧ F ⊆ B

theorem carrierAt_rotation (F : Finset α) (s : Execution n α)
    (q : ZMod n) (h : CarrierAt F s q) : CarrierAt F (step F s .p) (q + 1) := by
  obtain ⟨B, hB, hF⟩ := h
  refine ⟨B, ?_, hF⟩
  change s.placed (q + 1 - 1) = some B
  simpa using hB

theorem carrierAt_defect_zero (F : Finset α) (s : Execution n α)
    (h : CarrierAt F s 0) : CarrierAt F (step F s .d) 0 := by
  obtain ⟨B, hB, hF⟩ := h
  cases h1 : s.placed 1 with
  | none => exact ⟨B, by simp [step, stepDefect, hB, h1, fusionPlacement], hF⟩
  | some V =>
      exact ⟨B ∪ V, by simp [step, stepDefect, hB, h1, fusionPlacement],
        hF.trans Finset.subset_union_left⟩

theorem carrierAt_defect_one (F : Finset α) (s : Execution n α)
    (h : CarrierAt F s 1) : CarrierAt F (step F s .d) 0 := by
  obtain ⟨B, hB, hF⟩ := h
  cases h0 : s.placed 0 with
  | none => exact ⟨B, by simp [step, stepDefect, h0, hB, fusionPlacement], hF⟩
  | some U =>
      exact ⟨U ∪ B, by simp [step, stepDefect, h0, hB, fusionPlacement],
        hF.trans Finset.subset_union_right⟩

theorem fusionPlacement_recover (x y : Placement n (Finset α))
    (h0 : x 0 = y 0) (h1 : x 1 = y 1)
    (h : fusionPlacement x = fusionPlacement y) : x = y := by
  funext q
  by_cases hq0 : q = 0
  · simpa [hq0] using h0
  · by_cases hq1 : q = 1
    · simpa [hq1] using h1
    · simpa [fusionPlacement, hq0, hq1] using congrFun h q

/-- At a known left carrier, the event and actual successor recover both
kernel parents, including the empty-right-port case. -/
theorem selectedDefect_reverse_left (F : Finset α) (x y : Execution n α)
    (hx : CarrierAt F x 0) (hy : CarrierAt F y 0)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : selectedOutput F x .d = selectedOutput F y .d)
    (hp : (step F x .d).placed = (step F y .d).placed) : x.placed = y.placed := by
  obtain ⟨U, hx0, hFU⟩ := hx
  obtain ⟨V, hy0, hFV⟩ := hy
  have hplaced : fusionPlacement x.placed = fusionPlacement y.placed := by
    change (stepDefect F x).placed = (stepDefect F y).placed at hp
    cases h0 : x.placed 0 <;> cases h1 : x.placed 1 <;>
      cases h2 : y.placed 0 <;> cases h3 : y.placed 1 <;>
        simpa only [stepDefect, h0, h1, h2, h3] using hp
  cases hx1 : x.placed 1 with
  | none =>
      cases hy1 : y.placed 1 with
      | none =>
          apply fusionPlacement_recover _ _ _ (hx1.trans hy1.symm) hplaced
          have h := congrFun hplaced 0
          simpa [fusionPlacement, hx0, hx1, hy0, hy1] using h
      | some B => simp [selectedOutput, hx0, hx1, hy0, hy1, hyreg, hFV] at ht
  | some A =>
      cases hy1 : y.placed 1 with
      | none => simp [selectedOutput, hx0, hx1, hy0, hy1, hxreg, hFU] at ht
      | some B =>
          have hr : (⟨U, A, U ∪ A⟩ : FusionRecord α) = ⟨V, B, V ∪ B⟩ := by
            simpa [selectedOutput, hx0, hx1, hy0, hy1, hxreg, hyreg, hFU, hFV] using ht
          apply fusionPlacement_recover _ _ _ _ hplaced
          · simpa [hx0, hy0] using congrArg (fun r : FusionRecord α => some r.left) hr
          · simpa [hx1, hy1] using congrArg (fun r : FusionRecord α => some r.right) hr

/-- The symmetric inverse also covers a carrier moving from port one into
an empty port zero: a null output is not silently treated as no movement. -/
theorem selectedDefect_reverse_right (F : Finset α) (x y : Execution n α)
    (hx : CarrierAt F x 1) (hy : CarrierAt F y 1)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : selectedOutput F x .d = selectedOutput F y .d)
    (hp : (step F x .d).placed = (step F y .d).placed) : x.placed = y.placed := by
  obtain ⟨U, hx1, hFU⟩ := hx
  obtain ⟨V, hy1, hFV⟩ := hy
  have hplaced : fusionPlacement x.placed = fusionPlacement y.placed := by
    change (stepDefect F x).placed = (stepDefect F y).placed at hp
    cases h0 : x.placed 0 <;> cases h1 : x.placed 1 <;>
      cases h2 : y.placed 0 <;> cases h3 : y.placed 1 <;>
        simpa only [stepDefect, h0, h1, h2, h3] using hp
  cases hx0 : x.placed 0 with
  | none =>
      cases hy0 : y.placed 0 with
      | none =>
          apply fusionPlacement_recover _ _ (hx0.trans hy0.symm) _ hplaced
          have h := congrFun hplaced 0
          simpa [fusionPlacement, hx0, hx1, hy0, hy1] using h
      | some B => simp [selectedOutput, hx0, hx1, hy0, hy1, hyreg, hFV] at ht
  | some A =>
      cases hy0 : y.placed 0 with
      | none => simp [selectedOutput, hx0, hx1, hy0, hy1, hxreg, hFU] at ht
      | some B =>
          have hr : (⟨A, U, A ∪ U⟩ : FusionRecord α) = ⟨B, V, B ∪ V⟩ := by
            simpa [selectedOutput, hx0, hx1, hy0, hy1, hxreg, hyreg, hFU, hFV] using ht
          apply fusionPlacement_recover _ _ _ _ hplaced
          · simpa [hx0, hy0] using congrArg (fun r : FusionRecord α => some r.left) hr
          · simpa [hx1, hy1] using congrArg (fun r : FusionRecord α => some r.right) hr

theorem rotation_placed_injective (F : Finset α) (x y : Execution n α)
    (h : (step F x .p).placed = (step F y .p).placed) : x.placed = y.placed := by
  funext q
  have he := congrFun h (q + 1)
  simpa [step, rotate] using he

/-- Reverse an actual aligned sequence from its outputs and its endpoint.
Every recursive call uses the actual successor, never a new representative. -/
theorem pdWord_trace_endpoint_injective (F : Finset α) (k : ℕ)
    (x y : Execution n α) (hx : CarrierAt F x 0) (hy : CarrierAt F y 0)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : eventTrace F x (pdWord k) = eventTrace F y (pdWord k))
    (hp : (run F x (pdWord k)).placed = (run F y (pdWord k)).placed) :
    x.placed = y.placed := by
  induction k generalizing x y with
  | zero => exact hp
  | succ k ih =>
      let xp := step F x .p
      let yp := step F y .p
      let xd := step F xp .d
      let yd := step F yp .d
      have hxp : CarrierAt F xp 1 := by simpa [xp] using carrierAt_rotation F x 0 hx
      have hyp : CarrierAt F yp 1 := by simpa [yp] using carrierAt_rotation F y 0 hy
      have hxpreg := step_registered F x .p hxreg
      have hypreg := step_registered F y .p hyreg
      change none :: selectedOutput F xp .d :: eventTrace F xd (pdWord k) =
        none :: selectedOutput F yp .d :: eventTrace F yd (pdWord k) at ht
      have hs := (List.cons.inj ht).2
      have hlast : xd.placed = yd.placed := ih xd yd
        (carrierAt_defect_one F xp hxp) (carrierAt_defect_one F yp hyp)
        (step_registered F xp .d hxpreg) (step_registered F yp .d hypreg)
        (List.cons.inj hs).2 hp
      exact rotation_placed_injective F x y
        (selectedDefect_reverse_right F xp yp hxp hyp hxpreg hypreg
          (List.cons.inj hs).1 hlast)

theorem sweepCore_trace_endpoint_injective (F : Finset α) (k : ℕ)
    (x y : Execution n α) (hx : CarrierAt F x 0) (hy : CarrierAt F y 0)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : eventTrace F x (sweepCore k) = eventTrace F y (sweepCore k))
    (hp : (run F x (sweepCore k)).placed = (run F y (sweepCore k)).placed) :
    x.placed = y.placed := by
  change selectedOutput F x .d :: eventTrace F (step F x .d) (pdWord k) =
    selectedOutput F y .d :: eventTrace F (step F y .d) (pdWord k) at ht
  apply selectedDefect_reverse_left F x y hx hy hxreg hyreg (List.cons.inj ht).1
  exact pdWord_trace_endpoint_injective F k (step F x .d) (step F y .d)
    (carrierAt_defect_zero F x hx) (carrierAt_defect_zero F y hy)
    (step_registered F x .d hxreg) (step_registered F y .d hyreg)
    (List.cons.inj ht).2 hp

variable [NeZero n]

/-- Full scanning ends at the same literal one-packet placement for every
atom map, so the reverse theorem needs no additional endpoint assumption. -/
theorem sweepCore_aligned_injective (F : Finset (ZMod n))
    (x y : Execution n (ZMod n)) (f g : ZMod n → ZMod n) (hn : 2 ≤ n)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxc : CarrierAt F x 0) (hyc : CarrierAt F y 0)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : eventTrace F x (sweepCore (n - 2)) =
      eventTrace F y (sweepCore (n - 2))) : x.placed = y.placed := by
  apply sweepCore_trace_endpoint_injective F (n - 2) x y hxc hyc hxreg hyreg ht
  rw [atomSite_run F x f _ hn hx, atomSite_run F y g _ hn hy]
  congr 1
  funext atom
  exact (sweepCore_final_site (f atom) hn).trans (sweepCore_final_site (g atom) hn).symm

/-- Lemma 4.1, with an arbitrary common physical carrier site. -/
theorem registeredSweep_aligned_injective (F : Finset (ZMod n))
    (x y : Execution n (ZMod n)) (f g : ZMod n → ZMod n)
    (q : ZMod n) (hn : 2 ≤ n)
    (hx : x.placed = placementOfMap f) (hy : y.placed = placementOfMap g)
    (hxc : CarrierAt F x q) (hyc : CarrierAt F y q)
    (hxreg : x.origin.isSome = true) (hyreg : y.origin.isSome = true)
    (ht : eventTrace F x (registeredSweep q) = eventTrace F y (registeredSweep q)) :
    x.placed = y.placed := by
  let xr := run F x (pWord (-q).val)
  let yr := run F y (pWord (-q).val)
  have hxrc : CarrierAt F xr 0 := by
    obtain ⟨B, hB, hFB⟩ := hxc
    exact ⟨B, by simpa [xr, run_rotation, rotate] using hB, hFB⟩
  have hyrc : CarrierAt F yr 0 := by
    obtain ⟨B, hB, hFB⟩ := hyc
    exact ⟨B, by simpa [yr, run_rotation, rotate] using hB, hFB⟩
  have hxrreg : xr.origin.isSome = true := by simpa [xr, run_rotation] using hxreg
  have hyrreg : yr.origin.isSome = true := by simpa [yr, run_rotation] using hyreg
  have htail : eventTrace F xr (sweepCore (n - 2)) =
      eventTrace F yr (sweepCore (n - 2)) := by
    rw [registeredSweep, eventTrace_append, eventTrace_append] at ht
    have hxnull := (fusionFree_records_and_trace F x (pWord (-q).val)
      (fusionFree_pWord F x _)).2.2
    have hynull := (fusionFree_records_and_trace F y (pWord (-q).val)
      (fusionFree_pWord F y _)).2.2
    rw [hxnull, hynull] at ht
    exact List.append_cancel_left ht
  have hplaced := sweepCore_aligned_injective F xr yr
    (siteWord (pWord (-q).val) ∘ f) (siteWord (pWord (-q).val) ∘ g) hn
    (atomSite_run F x f _ hn hx) (atomSite_run F y g _ hn hy)
    hxrc hyrc hxrreg hyrreg htail
  funext site
  have hsite := congrFun hplaced (site - q)
  simpa [xr, yr, run_rotation, rotate] using hsite

end FutureEvent
