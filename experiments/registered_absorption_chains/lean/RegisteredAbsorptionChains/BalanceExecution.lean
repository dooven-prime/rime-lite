import RegisteredAbsorptionChains.NetTransfer
import RegisteredAbsorptionChains.PlacementFrame
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r] [DecidableEq α]

/-- Iterating the abstract balancing choices retains one concrete execution
and one phase-aware frame throughout. Final phase alignment is separate. -/
theorem realizeBalancedGaps (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (target : Gaps r)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (total : (∑ i : Fin r, finGaps frame.gap i) = ∑ i : Fin r, target i)
    (source : s.placed = frame.decode) :
    ∃ (next : GapFrame n r α) (word : List Letter),
      run F s word = { s with placed := next.decode } ∧
      finGaps next.gap = target ∧ next.block = frame.block ∧
      FusionFree F s word := by
  by_cases equal : finGaps frame.gap = target
  · refine ⟨frame, [], ?_, equal, rfl, trivial⟩
    simp only [run, List.foldl_nil]
    cases s
    simp_all
  · let h := finGaps frame.gap
    let e := firstExcess h target total equal
    let f := firstDeficit h target total equal
    have he : target e < h e := firstExcess_spec h target total equal
    have hf : h f < target f := firstDeficit_spec h target total equal
    have hef : e ≠ f := by
      intro eq
      have he' : target f < h f := by simpa [eq] using he
      omega
    have positive : 0 < finGaps frame.gap e := by
      change 0 < h e
      omega
    obtain ⟨mid, first, hrest⟩ :=
      realizeNetTransfer F s frame e f hn hr hef source positive
    have hrun := hrest.1
    have hgap := hrest.2.1
    have hblock := hrest.2.2.1
    have hfree₁ := hrest.2.2.2
    let s₁ := run F s first
    have hsource₁ : s₁.placed = mid.decode := by
      change (run F s first).placed = mid.decode
      rw [hrun]
    have total₁ : (∑ i : Fin r, finGaps mid.gap i) =
        ∑ i : Fin r, target i := by
      rw [hgap, transferHole_preserves_total h e f hef positive]
      exact total
    obtain ⟨last, rest, hrun₂, hfinal, hblock₂, hfree₂⟩ :=
      realizeBalancedGaps F s₁ mid target hn hr total₁ hsource₁
    refine ⟨last, first ++ rest, ?_, hfinal, ?_, ?_⟩
    · rw [run_append, ← show s₁ = run F s first from rfl, hrun₂]
      simp only [s₁, hrun]
    · exact hblock₂.trans hblock
    · exact (fusionFree_append F s first rest).mpr ⟨hfree₁, hfree₂⟩
termination_by gapPotential (finGaps frame.gap) target
decreasing_by
  rw [hgap]
  exact transferHole_potential_lt h target e f hef he hf

end RegisteredAbsorptionChains
