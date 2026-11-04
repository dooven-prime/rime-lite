import RegisteredAbsorptionChains.FiberReachability
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def selectedPair (n : ℕ) : Finset (ZMod n) := {0, 1}

/-- The first defect letter is the actual registration event. -/
def registrationExecution (n : ℕ) [NeZero n] : Execution n (ZMod n) :=
  run (selectedPair n) (singletonExecution n) [.d]

theorem registration_placed_zero (_hn : 2 ≤ n) :
    (registrationExecution n).placed 0 = some (selectedPair n) := by
  simp [registrationExecution, run, step, stepDefect, singletonExecution,
    fusionPlacement, selectedPair]

theorem registration_placed_one (hn : 2 ≤ n) :
    (registrationExecution n).placed 1 = none := by
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  simp [registrationExecution, run, step, stepDefect, singletonExecution,
    fusionPlacement, selectedPair, h10]

theorem registration_placed_other (_hn : 2 ≤ n) (q : ZMod n)
    (hq0 : q ≠ 0) (hq1 : q ≠ 1) :
    (registrationExecution n).placed q = some {q} := by
  simp [registrationExecution, run, step, stepDefect, singletonExecution,
    fusionPlacement, hq0, hq1, selectedPair]

theorem registration_origin (_hn : 2 ≤ n) :
    (registrationExecution n).origin =
      some ⟨({0} : Finset (ZMod n)), {1}, selectedPair n⟩ := by
  simp [registrationExecution, run, step, stepDefect, singletonExecution,
    selectedPair]

theorem registration_chain (_hn : 2 ≤ n) :
    (registrationExecution n).chain = [] := by
  simp [registrationExecution, run, step, stepDefect, singletonExecution,
    selectedPair]

/-- A selected carrier is present, and every other occupied packet is an
unmerged atom. This says nothing about the carrier's physical phase. -/
def CleanOutside (C : Finset (ZMod n)) (s : Execution n (ZMod n)) : Prop :=
  (∃ q, s.placed q = some C) ∧
    ∀ q B, s.placed q = some B → B = C ∨ ∃ x, B = {x}

/-- In a genuinely reachable clean state, no outside atom can be absent:
each one occupies its own singleton packet. -/
theorem clean_reachable_outside_singletons
    (F C : Finset (ZMod n)) (s : Execution n (ZMod n))
    (hn : 2 ≤ n) (reachable : ReachableExecution F s)
    (hclean : CleanOutside C s)
    (y : ZMod n) (hy : y ∉ C) :
    ∃ q, s.placed q = some {y} := by
  obtain ⟨word, hword⟩ := reachable
  have hfrom : ReachableFromSingleton F s.placed :=
    ⟨word, congrArg Execution.placed hword⟩
  have hordered : SourceOrdered s.placed :=
    reachable_source_ordered F s.placed hn hfrom
  obtain ⟨B, hB, hyB⟩ := sourceOrdered_blocks_cover s.placed hordered y
  obtain ⟨_, q, hq⟩ := (mem_placedBlocks s.placed B).mp hB
  rcases hclean.2 q B hq with hcarrier | ⟨x, hsingle⟩
  · exact False.elim (hy (hcarrier ▸ hyB))
  · have hyx : y = x := by simpa [hsingle] using hyB
    refine ⟨q, ?_⟩
    simpa [hsingle, hyx] using hq

/-- The literal one-letter registration supplies the clean base case. -/
theorem registration_clean (hn : 2 ≤ n) :
    ReachableExecution (selectedPair n) (registrationExecution n) ∧
      (registrationExecution n).origin =
        some ⟨({0} : Finset (ZMod n)), {1}, selectedPair n⟩ ∧
      (registrationExecution n).chain = [] ∧
      CleanOutside (selectedPair n) (registrationExecution n) := by
  refine ⟨⟨[.d], rfl⟩, registration_origin hn, registration_chain hn, ?_⟩
  constructor
  · exact ⟨0, registration_placed_zero hn⟩
  · intro q B hB
    by_cases hq0 : q = 0
    · subst q
      left
      exact Option.some.inj ((registration_placed_zero hn).symm.trans hB) |>.symm
    by_cases hq1 : q = 1
    · subst q
      simp [registration_placed_one hn] at hB
    · right
      exact ⟨q, (Option.some.inj
        ((registration_placed_other hn q hq0 hq1).symm.trans hB)).symm⟩

/-- A fusion-free placement change with the same named packets carries the
clean-outside invariant to its target placement. -/
theorem clean_same_named_blocks
    {r : ℕ} [NeZero r]
    (C : Finset (ZMod n)) (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (source : s.placed = first.placed)
    (sameBlocks : first.block = second.block)
    (hclean : CleanOutside C s) :
    CleanOutside C { s with placed := second.placed } := by
  obtain ⟨qC, hC⟩ := hclean.1
  have hfirstC : first.placed qC = some C := source ▸ hC
  obtain ⟨iC, hiC⟩ := first.only_named qC (by simp [hfirstC])
  have hblockC : first.block iC = C := by
    exact Option.some.inj ((first.placed_at iC).symm.trans (hiC ▸ hfirstC))
  constructor
  · refine ⟨second.position iC, ?_⟩
    change second.placed (second.position iC) = some C
    rw [second.placed_at, ← sameBlocks, hblockC]
  · intro q B hB
    change second.placed q = some B at hB
    obtain ⟨i, hi⟩ := second.only_named q (by simp [hB])
    have hblock : second.block i = B := by
      exact Option.some.inj ((second.placed_at i).symm.trans (hi ▸ hB))
    have hsourceBlock : s.placed (first.position i) = some B := by
      rw [source, first.placed_at, sameBlocks, hblock]
    exact hclean.2 (first.position i) B hsourceBlock

/-- Distinct physical sites of a legal named placement cannot carry the
same nonempty packet. -/
theorem unique_named_block_site
    {r : ℕ} [NeZero r]
    (named : LegalNamedPlacement n r (ZMod n))
    (B : Finset (ZMod n)) (q q' : ZMod n)
    (hq : named.placed q = some B)
    (hq' : named.placed q' = some B) : q = q' := by
  obtain ⟨i, hi⟩ := named.only_named q (by simp [hq])
  obtain ⟨j, hj⟩ := named.only_named q' (by simp [hq'])
  have hbi : named.block i = B :=
    Option.some.inj ((named.placed_at i).symm.trans (hi ▸ hq))
  have hbj : named.block j = B :=
    Option.some.inj ((named.placed_at j).symm.trans (hj ▸ hq'))
  by_cases hij : i = j
  · exact hi.symm.trans (hij ▸ hj)
  · have hdisj := named.block_disjoint i j hij
    obtain ⟨x, hx⟩ := named.block_nonempty i
    have hxi : x ∈ named.block i := hx
    have hxj : x ∈ named.block j := by
      rw [hbj, ← hbi]
      exact hx
    exact False.elim ((Finset.disjoint_left.mp hdisj) hxi hxj)

/-- A supplied legal placement of the carrier and one fresh singleton at
the kernel ports yields one literal selected absorption. The preparatory
word is fusion-free; the final defect letter is a genuine fusion. -/
theorem realize_prepared_clean_absorption
    {r : ℕ} [NeZero r]
    (F C : Finset (ZMod n)) (x : ZMod n)
    (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (h0 : second.placed 0 = some C)
    (h1 : second.placed 1 = some {x})
    (hregistered : s.origin.isSome = true)
    (hFC : F ⊆ C) :
    ∃ prep : List Letter,
      FusionFree F s prep ∧
      run F s prep = { s with placed := second.placed } ∧
      (run F s (prep ++ [.d])).placed = fusionPlacement second.placed ∧
      (run F s (prep ++ [.d])).origin = s.origin ∧
      (run F s (prep ++ [.d])).chain =
        s.chain ++ [⟨C, {x}, C ∪ {x}⟩] := by
  obtain ⟨prep, hprep, hfree⟩ :=
    realize_same_oriented_placements F s first second hn hr source same
  have hstep : stepDefect F (run F s prep) =
      { placed := fusionPlacement second.placed,
        origin := s.origin,
        chain := s.chain ++ [⟨C, {x}, C ∪ {x}⟩] } := by
    have hsome : s.origin ≠ none := by
      cases h : s.origin <;> simp_all
    rw [hprep]
    simp [stepDefect, h0, h1, hsome, hregistered, hFC]
  refine ⟨prep, hfree, hprep, ?_, ?_, ?_⟩
  · rw [run_append]
    change (stepDefect F (run F s prep)).placed = _
    rw [hstep]
  · rw [run_append]
    change (stepDefect F (run F s prep)).origin = _
    rw [hstep]
  · rw [run_append]
    change (stepDefect F (run F s prep)).chain = _
    rw [hstep]

omit [NeZero n] in
/-- At a prepared kernel configuration, merging the carrier with one
singleton preserves the clean-outside property. Uniqueness of the carrier
site is supplied explicitly; it holds for a legal actual partition. -/
theorem clean_after_prepared_absorption
    (F C : Finset (ZMod n)) (x : ZMod n)
    (s : Execution n (ZMod n))
    (hn : 2 ≤ n)
    (h0 : s.placed 0 = some C) (h1 : s.placed 1 = some {x})
    (hclean : CleanOutside C s)
    (hunique : ∀ q, s.placed q = some C → q = 0) :
    CleanOutside (C ∪ {x}) (stepDefect F s) := by
  have hplaced : (stepDefect F s).placed = fusionPlacement s.placed :=
    stepDefect_placed F s
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  constructor
  · refine ⟨0, ?_⟩
    rw [hplaced]
    simp [fusionPlacement, h0, h1]
  · intro q B hB
    rw [hplaced] at hB
    by_cases hq0 : q = 0
    · subst q
      left
      have hzero : fusionPlacement s.placed 0 = some (C ∪ {x}) := by
        simp [fusionPlacement, h0, h1]
      exact (Option.some.inj (hzero.symm.trans hB)).symm
    by_cases hq1 : q = 1
    · subst q
      simp [fusionPlacement, h10] at hB
    · have hold : s.placed q = some B := by
        simpa [fusionPlacement, hq0, hq1] using hB
      rcases hclean.2 q B hold with hcarrier | hsingle
      · exact False.elim (hq0 (hunique q (hcarrier ▸ hold)))
      · exact Or.inr hsingle

/-- One clean, actually reachable chain witness extends by a prescribed
adjacent singleton once the corresponding same-order legal placement is
supplied. The new witness is still clean and retains the old origin. -/
theorem realize_clean_absorption_step
    {r : ℕ} [NeZero r]
    (F C : Finset (ZMod n)) (x : ZMod n)
    (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F s)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (h0 : second.placed 0 = some C)
    (h1 : second.placed 1 = some {x})
    (hregistered : s.origin.isSome = true)
    (hFC : F ⊆ C)
    (hclean : CleanOutside C s) :
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [⟨C, {x}, C ∪ {x}⟩] ∧
      CleanOutside (C ∪ {x}) (run F s word) := by
  obtain ⟨prep, hfree, hprep, _, horigin, hchain⟩ :=
    realize_prepared_clean_absorption F C x s first second hn hr source
      same h0 h1 hregistered hFC
  let word := prep ++ [.d]
  have hpreclean : CleanOutside C (run F s prep) := by
    rw [hprep]
    exact clean_same_named_blocks C s first second source same.1 hclean
  have hp0 : (run F s prep).placed 0 = some C := by
    simpa [hprep] using h0
  have hp1 : (run F s prep).placed 1 = some {x} := by
    simpa [hprep] using h1
  have hunique : ∀ q, (run F s prep).placed q = some C → q = 0 := by
    intro q hq
    have hq' : second.placed q = some C := by simpa [hprep] using hq
    exact unique_named_block_site second C q 0 hq' h0
  have hpostclean : CleanOutside (C ∪ {x}) (run F s word) := by
    dsimp [word]
    rw [run_append]
    change CleanOutside (C ∪ {x}) (stepDefect F (run F s prep))
    exact clean_after_prepared_absorption F C x (run F s prep) hn
      hp0 hp1 hpreclean hunique
  obtain ⟨initialWord, hinitial⟩ := reachable
  refine ⟨word, ⟨initialWord ++ word, ?_⟩, horigin, hchain, hpostclean⟩
  rw [run_append, hinitial]

end RegisteredAbsorptionChains
