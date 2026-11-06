import RegisteredAbsorptionChains.BalanceExecution
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r]

/-- Equal named gaps determine every block coordinate up to the anchor phase. -/
theorem GapFrame.position_phase (start target : GapFrame n r α)
    (gaps : start.gap = target.gap) (i : ZMod r) :
    target.position i = start.position i + (target.anchor - start.anchor) := by
  have hnat (k : ℕ) (hk : k ≤ r) :
      target.position (k : ZMod r) =
        start.position (k : ZMod r) + (target.anchor - start.anchor) := by
    induction k with
    | zero =>
        simp only [Nat.cast_zero, start.anchor_eq, target.anchor_eq]
        abel
    | succ k ih =>
        have hkle : k ≤ r := by omega
        have hnext₁ := start.next_eq (k : ZMod r)
        have hnext₂ := target.next_eq (k : ZMod r)
        have hgap : start.gap (k : ZMod r) = target.gap (k : ZMod r) :=
          congrFun gaps _
        push_cast
        rw [hnext₁, hnext₂, ← hgap, ih hkle]
        abel
  have h := hnat i.val (by have := ZMod.val_lt i; omega)
  simpa only [ZMod.natCast_zmod_val] using h

/-- Matching gaps and names make the decoded placements rotations of one another. -/
theorem GapFrame.decode_phase (start target : GapFrame n r α)
    (gaps : start.gap = target.gap) (blocks : start.block = target.block) :
    rotate (target.anchor - start.anchor) start.decode = target.decode := by
  classical
  let phase := target.anchor - start.anchor
  have hpos (i : ZMod r) : target.position i = start.position i + phase :=
    start.position_phase target gaps i
  funext q
  by_cases hnamed : ∃ i, target.position i = q
  · obtain ⟨i, hi⟩ := hnamed
    subst q
    have hback : target.position i - phase = start.position i := by
      rw [hpos]
      abel
    rw [show rotate phase start.decode (target.position i) =
        start.decode (target.position i - phase) from rfl,
      hback, start.decode_at i, target.decode_at i]
    rw [congrFun blocks i]
  · have htarget : target.decode q = none := by
      apply target.decode_empty
      intro i hi
      exact hnamed ⟨i, hi⟩
    have hsource : start.decode (q - phase) = none := by
      apply start.decode_empty
      intro i hi
      apply hnamed
      refine ⟨i, ?_⟩
      rw [hpos]
      have h := congrArg (fun x : ZMod n => x + phase) hi
      simpa [sub_add_cancel] using h
    change start.decode (q - phase) = target.decode q
    rw [hsource, htarget]

theorem finGaps_sum (h : ZMod r → ℕ) :
    (∑ i : Fin r, finGaps h i) = ∑ i : ZMod r, h i := by
  exact Equiv.sum_comp (ZMod.finEquiv r).toEquiv h

theorem finGaps_injective {h g : ZMod r → ℕ}
    (eq : finGaps h = finGaps g) : h = g := by
  funext i
  obtain ⟨j, hj⟩ := (ZMod.finEquiv r).surjective i
  have hpoint := congrFun eq j
  simpa [finGaps, hj] using hpoint

/-- From one phase-aware frame to another with the same named blocks, an
actual word balances all gaps and then rotates to the target phase. -/
theorem realizeFrameTarget [DecidableEq α] (F : Finset α) (s : Execution n α)
    (start target : GapFrame n r α) (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = start.decode) (blocks : start.block = target.block) :
    ∃ word : List Letter,
      run F s word = { s with placed := target.decode } ∧
      FusionFree F s word := by
  have total : (∑ i : Fin r, finGaps start.gap i) =
      ∑ i : Fin r, finGaps target.gap i := by
    rw [finGaps_sum, finGaps_sum, start.gap_total, target.gap_total]
  obtain ⟨mid, route, hrun, hgap, hblock, hfree⟩ :=
    realizeBalancedGaps F s start (finGaps target.gap) hn hr total source
  have hgapZ : mid.gap = target.gap := finGaps_injective hgap
  have hblockZ : mid.block = target.block := hblock.trans blocks
  let phase := target.anchor - mid.anchor
  refine ⟨route ++ pWord phase.val, ?_, ?_⟩
  · rw [run_append, hrun, run_rotation]
    have hrotate := mid.decode_phase target hgapZ hblockZ
    change { s with placed := rotate phase mid.decode } =
      { s with placed := target.decode }
    rw [hrotate]
  · exact (fusionFree_append F s route _).mpr
      ⟨hfree, fusionFree_pWord F (run F s route) _⟩

/-- Conditional placement-to-placement reachability for a fixed named cyclic
block order; admission of that order from arbitrary histories is separate. -/
theorem realizeNamedPlacementTarget [DecidableEq α] (F : Finset α)
    (s : Execution n α) (first second : NamedCyclicPlacement n r α)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed) (blocks : first.block = second.block) :
    ∃ word : List Letter,
      run F s word = { s with placed := second.placed } ∧
      FusionFree F s word := by
  have hsource : s.placed = first.toGapFrame.decode := by
    rw [first.toGapFrame_decode]
    exact source
  have hblocks : first.toGapFrame.block = second.toGapFrame.block := by
    simpa using blocks
  obtain ⟨word, hrun, hfree⟩ :=
    realizeFrameTarget F s first.toGapFrame second.toGapFrame hn hr hsource hblocks
  refine ⟨word, ?_, hfree⟩
  rwa [second.toGapFrame_decode] at hrun

end RegisteredAbsorptionChains
