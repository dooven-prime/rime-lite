import RegisteredAbsorptionChains.FiberParamDecode
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

omit [NeZero n] in
/-- A defect step with an already registered origin and neither parent
containing the selected block cannot add a selected absorption. It may still
be a genuine fusion of two outside packets. -/
theorem stepDefect_outside_records
    (F : Finset α) (s : Execution n α)
    (u v : Finset α)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hregistered : s.origin.isSome = true)
    (hu : ¬ F ⊆ u) (hv : ¬ F ⊆ v) :
    (stepDefect F s).placed = fusionPlacement s.placed ∧
    (stepDefect F s).origin = s.origin ∧
    (stepDefect F s).chain = s.chain := by
  have hnone : s.origin.isNone = false := by
    cases h : s.origin <;> simp_all
  simp [stepDefect, h0, h1, hnone, hu, hv]

omit [NeZero n] in
/-- Fusion-free preparatory routing preserves both registered records. -/
theorem run_fusionFree_records
    (F : Finset α) (s : Execution n α) (word : List Letter)
    (free : FusionFree F s word) :
    (run F s word).origin = s.origin ∧
    (run F s word).chain = s.chain := by
  induction word generalizing s with
  | nil => simp [run]
  | cons letter rest ih =>
      cases letter with
      | p =>
          have htail : FusionFree F (step F s .p) rest := free
          have h := ih (step F s .p) htail
          simpa [run, step] using h
      | d =>
          obtain ⟨hole, tail⟩ := free
          have hstep : (step F s .d).origin = s.origin ∧
              (step F s .d).chain = s.chain := by
            rcases hole with hzero | hone
            · simpa [step] using stepDefect_no_origin_or_chain F s hzero
            · simp [step, stepDefect, hone]
          have h := ih (step F s .d) tail
          simpa [run, hstep.1, hstep.2] using h

omit [NeZero n] in
/-- A single outside merge may be preceded by a genuinely fusion-free
placement adjustment. The last `d` is *not* required to be fusion-free. -/
theorem run_prepared_outside_merge
    (F : Finset α) (s : Execution n α) (prep : List Letter)
    (free : FusionFree F s prep)
    (u v : Finset α)
    (h0 : (run F s prep).placed 0 = some u)
    (h1 : (run F s prep).placed 1 = some v)
    (hregistered : s.origin.isSome = true)
    (hu : ¬ F ⊆ u) (hv : ¬ F ⊆ v) :
    (run F s (prep ++ [.d])).placed =
      fusionPlacement (run F s prep).placed ∧
    (run F s (prep ++ [.d])).origin = s.origin ∧
    (run F s (prep ++ [.d])).chain = s.chain := by
  have hrecords := run_fusionFree_records F s prep free
  have hstep := stepDefect_outside_records F (run F s prep) u v h0 h1
    (by simpa [hrecords.1] using hregistered) hu hv
  rw [hrecords.1, hrecords.2] at hstep
  simpa [run_append, run, step, hrecords.1, hrecords.2] using hstep

omit [DecidableEq α] in
/-- If a nonempty selected block lies in a distinct carrier packet, neither
of two packets disjoint from that carrier can trigger its absorption. -/
theorem outside_parents_not_selected
    (F C u v : Finset α) (hF : F.Nonempty) (hFC : F ⊆ C)
    (hCu : Disjoint C u) (hCv : Disjoint C v) :
    ¬ F ⊆ u ∧ ¬ F ⊆ v := by
  obtain ⟨a, ha⟩ := hF
  have hCa : a ∈ C := hFC ha
  constructor
  · intro hFu
    exact (Finset.disjoint_left.mp hCu) hCa (hFu ha)
  · intro hFv
    exact (Finset.disjoint_left.mp hCv) hCa (hFv ha)

omit [NeZero n] in
/-- A defect fusion changes only the two kernel sites. In particular an
outside merger leaves a carrier at any other physical site untouched. -/
theorem fusionPlacement_other_site
    (placed : Placement n (Finset α)) (q : ZMod n)
    (hq0 : q ≠ 0) (hq1 : q ≠ 1) :
    fusionPlacement placed q = placed q := by
  simp [fusionPlacement, hq0, hq1]

/-- A genuine outside fusion can follow the actual fusion-free word from
Lemma 2.2. The final defect letter merges `u,v`; only that preparatory word
is required to be fusion-free. -/
theorem realize_one_outside_merge
    {r : ℕ} [NeZero r]
    (F : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n r α)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (u v : Finset α)
    (h0 : second.placed 0 = some u)
    (h1 : second.placed 1 = some v)
    (hregistered : s.origin.isSome = true)
    (hu : ¬ F ⊆ u) (hv : ¬ F ⊆ v) :
    ∃ word : List Letter,
      (run F s word).placed = fusionPlacement second.placed ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain ∧
      (run F s word).placed 0 = some (u ∪ v) ∧
      (run F s word).placed 1 = none := by
  obtain ⟨prep, hprep, hfree⟩ :=
    realize_same_oriented_placements F s first second hn hr source same
  let word := prep ++ [.d]
  have hmerge := run_prepared_outside_merge F s prep hfree u v
    (by simpa [hprep] using h0)
    (by simpa [hprep] using h1) hregistered hu hv
  refine ⟨word, ?_, hmerge.2.1, hmerge.2.2, ?_, ?_⟩
  · simpa only [word, hprep] using hmerge.1
  · rw [show (run F s word).placed = fusionPlacement second.placed by
      simpa only [word, hprep] using hmerge.1]
    simp [fusionPlacement, h0, h1]
  · rw [show (run F s word).placed = fusionPlacement second.placed by
      simpa only [word, hprep] using hmerge.1]
    have h10 : (1 : ZMod n) ≠ 0 := by
      intro h
      have := ZMod.one_eq_zero_iff.mp h
      omega
    simp [fusionPlacement, h10]

/-- The carrier-based interface for one actual outside merger. The carrier
contains the selected block, while both parents are disjoint from it. -/
theorem realize_one_carrier_safe_outside_merge
    {r : ℕ} [NeZero r]
    (F C : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n r α)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (u v : Finset α)
    (h0 : second.placed 0 = some u)
    (h1 : second.placed 1 = some v)
    (hregistered : s.origin.isSome = true)
    (hF : F.Nonempty) (hFC : F ⊆ C)
    (hCu : Disjoint C u) (hCv : Disjoint C v) :
    ∃ word : List Letter,
      (run F s word).placed = fusionPlacement second.placed ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain ∧
      (run F s word).placed 0 = some (u ∪ v) ∧
      (run F s word).placed 1 = none := by
  obtain ⟨hu, hv⟩ := outside_parents_not_selected F C u v hF hFC hCu hCv
  exact realize_one_outside_merge F s first second hn hr source same
    u v h0 h1 hregistered hu hv

/-- The same one-step construction explicitly retains the physical carrier
packet when its site is outside the two kernel ports. -/
theorem realize_one_outside_merge_retains_carrier
    {r : ℕ} [NeZero r]
    (F C : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n r α)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (u v : Finset α)
    (h0 : second.placed 0 = some u)
    (h1 : second.placed 1 = some v)
    (hregistered : s.origin.isSome = true)
    (hF : F.Nonempty) (hFC : F ⊆ C)
    (hCu : Disjoint C u) (hCv : Disjoint C v)
    (qC : ZMod n) (hC : second.placed qC = some C)
    (hq0 : qC ≠ 0) (hq1 : qC ≠ 1) :
    ∃ word : List Letter,
      (run F s word).placed 0 = some (u ∪ v) ∧
      (run F s word).placed 1 = none ∧
      (run F s word).placed qC = some C ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain := by
  obtain ⟨word, hplaced, horigin, hchain, hmerged, hhole⟩ :=
    realize_one_carrier_safe_outside_merge F C s first second hn hr source same
      u v h0 h1 hregistered hF hFC hCu hCv
  refine ⟨word, hmerged, hhole, ?_, horigin, hchain⟩
  rw [hplaced, fusionPlacement_other_site second.placed qC hq0 hq1]
  exact hC

/-- A finite plan of actual outside mergers. Each stage supplies a legal
placement target for Lemma 2.2 and an external pair at the kernel ports.
The existence of such a plan for every prescribed cut is a separate goal. -/
inductive OutsideAssemblySchedule (F C : Finset α) :
    Execution n α → Execution n α → Prop where
  | empty (s : Execution n α) : OutsideAssemblySchedule F C s s
  | merge {s final : Execution n α} {r : ℕ} [NeZero r]
      (first second : LegalNamedPlacement n r α)
      (hn : 2 ≤ n) (hr : 2 ≤ r)
      (source : s.placed = first.placed)
      (same : SameOrientedCyclicOrder first second)
      (u v : Finset α)
      (h0 : second.placed 0 = some u)
      (h1 : second.placed 1 = some v)
      (registered : s.origin.isSome = true)
      (selected : F.Nonempty) (inside : F ⊆ C)
      (leftOutside : Disjoint C u) (rightOutside : Disjoint C v)
      (carrier : ∃ q, second.placed q = some C ∧ q ≠ 0 ∧ q ≠ 1)
      (tail : OutsideAssemblySchedule F C
        { s with placed := fusionPlacement second.placed } final) :
      OutsideAssemblySchedule F C s final

/-- Any supplied finite plan expands to one literal chronological word.
Outside fusions are permitted; the selected chain is not extended. -/
theorem OutsideAssemblySchedule.realize
    {F C : Finset α} {s final : Execution n α}
    (schedule : OutsideAssemblySchedule F C s final) :
    ∃ word : List Letter,
      run F s word = final ∧
      final.origin = s.origin ∧ final.chain = s.chain := by
  induction schedule with
  | empty s =>
      exact ⟨[], by simp [run], rfl, rfl⟩
  | @merge s final r _ first second hn hr source same u v h0 h1
      registered selected inside leftOutside rightOutside carrier tail ih =>
      obtain ⟨word, hplaced, horigin, hchain, _, _⟩ :=
        realize_one_carrier_safe_outside_merge F C s first second hn hr
          source same u v h0 h1 registered selected inside
          leftOutside rightOutside
      have hfirst : run F s word =
          { s with placed := fusionPlacement second.placed } := by
        cases hrun : run F s word with
        | mk placed origin chain =>
          cases s with
          | mk placed0 origin0 chain0 =>
              simp_all
      obtain ⟨rest, hrest, hrestOrigin, hrestChain⟩ := ih
      refine ⟨word ++ rest, ?_, ?_, ?_⟩
      · rw [run_append, hfirst, hrest]
      · simpa using hrestOrigin
      · simpa using hrestChain

private def outsideControl : Execution 5 (ZMod 5) :=
  { placed := fun q =>
      if q = 0 then some {2} else
      if q = 1 then some {3} else
      if q = 3 then some {0, 1} else
      if q = 4 then some {4} else none
    origin := some ⟨{0}, {1}, {0, 1}⟩
    chain := [] }

private def outsideControlF : Finset (ZMod 5) := {0, 1}

private example :
    (step outsideControlF outsideControl .d).placed 0 = some ({2, 3} : Finset (ZMod 5)) ∧
    (step outsideControlF outsideControl .d).origin = outsideControl.origin ∧
    (step outsideControlF outsideControl .d).chain = outsideControl.chain := by
  have h := stepDefect_outside_records outsideControlF outsideControl
    ({2} : Finset (ZMod 5)) ({3} : Finset (ZMod 5))
    (by decide) (by decide) rfl (by decide) (by decide)
  refine ⟨?_, h.2.1, h.2.2⟩
  rw [show step outsideControlF outsideControl .d =
    stepDefect outsideControlF outsideControl from rfl, h.1]
  decide

private example : ¬ FusionFree outsideControlF outsideControl [.d] := by
  intro h
  have h0 : outsideControl.placed 0 ≠ none := by decide
  have h1 : outsideControl.placed 1 ≠ none := by decide
  rcases h.1 with h | h
  · exact h0 h
  · exact h1 h

end RegisteredAbsorptionChains
