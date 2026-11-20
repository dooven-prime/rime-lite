import RegisteredAbsorptionChains.CrossNextBlock
import RegisteredAbsorptionChains.GapPotential
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r]

/-- Net transfer in the cyclic block indexing used by physical frames. -/
def transferHoleZ (h : ZMod r → ℕ) (e f : ZMod r) : ZMod r → ℕ :=
  Function.update (Function.update h e (h e - 1)) f (h f + 1)

private theorem crossGap_eq_transfer (frame : GapFrame n r α) (i : ZMod r) :
    crossGap frame i = transferHoleZ frame.gap i (i + 1) := rfl

private theorem transfer_after_cross (frame : GapFrame n r α) (i f : ZMod r)
    (hr : 2 ≤ r) (hif : i ≠ f) (hnf : i + 1 ≠ f) :
    transferHoleZ (crossGap frame i) (i + 1) f =
      transferHoleZ frame.gap i f := by
  classical
  have hni : i + 1 ≠ i := by
    intro h
    have hz : (1 : ZMod r) = 0 := by
      have := congrArg (fun x : ZMod r => x - i) h
      simpa [add_sub_cancel_left] using this
    have := ZMod.one_eq_zero_iff.mp hz
    omega
  funext j
  by_cases hji : j = i
  · subst j
    simp [transferHoleZ, hif, hni.symm,
      crossGap_donor frame i hr]
  by_cases hjn : j = i + 1
  · subst j
    simp [transferHoleZ, hni, hnf,
      crossGap_receiver frame i]
  by_cases hjf : j = f
  · subst j
    simp [transferHoleZ,
      crossGap_other frame i f hif.symm hnf.symm]
  · simp [transferHoleZ, hji, hjn, hjf,
      crossGap_other frame i j hji hjn]

omit [NeZero r] in
private theorem cyclic_shift_ne_self (e : ZMod r) {k : ℕ}
    (hk0 : 0 < k) (hk : k < r) : e + (k : ZMod r) ≠ e := by
  intro heq
  have hzero : (k : ZMod r) = 0 := by simpa using heq
  have hdiv : r ∣ k := (ZMod.natCast_eq_zero_iff k r).mp hzero
  have hle := Nat.le_of_dvd hk0 hdiv
  omega

/-- Route one hole across successive named blocks with actual `p,d` letters. -/
theorem realizeNetTransferZ [DecidableEq α] (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (e : ZMod r) (k : ℕ)
    (hn : 2 ≤ n) (hr : 2 ≤ r) (hk0 : 0 < k) (hk : k < r)
    (source : s.placed = frame.decode) (positive : 0 < frame.gap e) :
    ∃ (next : GapFrame n r α) (word : List Letter),
      run F s word = { s with placed := next.decode } ∧
      next.gap = transferHoleZ frame.gap e (e + (k : ZMod r)) ∧
      next.block = frame.block ∧ FusionFree F s word := by
  induction k generalizing s frame e with
  | zero => omega
  | succ k ih =>
      let can := frame.canCross_of_positive e positive
      let first := localLetters (frame.position (e + 1) - 1)
      let mid := frame.cross e hr can
      have hstep : run F s first = { s with placed := mid.decode } :=
        crossNextBlock_from_gap F s frame e hn hr source positive
      have hfree : FusionFree F s first :=
        crossNextBlock_fusionFree F s frame e source positive
      by_cases hzero : k = 0
      · subst k
        refine ⟨mid, first, hstep, ?_, rfl, hfree⟩
        change crossGap frame e = transferHoleZ frame.gap e
          (e + ((0 + 1 : ℕ) : ZMod r))
        simpa using crossGap_eq_transfer frame e
      · have hkpos : 0 < k := by omega
        have hmidpos : 0 < mid.gap (e + 1) := by
          change 0 < crossGap frame e (e + 1)
          rw [crossGap_receiver]
          omega
        let s₁ := run F s first
        have hsource₁ : s₁.placed = mid.decode := by
          change (run F s first).placed = mid.decode
          rw [hstep]
        obtain ⟨last, rest, hrest⟩ :=
          ih s₁ mid (e + 1) hkpos (by omega) hsource₁ hmidpos
        have hrun := hrest.1
        have hgap := hrest.2.1
        have hblock := hrest.2.2.1
        have hfreeRest := hrest.2.2.2
        refine ⟨last, first ++ rest, ?_, ?_, ?_, ?_⟩
        · rw [run_append, ← show s₁ = run F s first from rfl, hrun]
          simp only [s₁, hstep]
        · have hif : e ≠ e + ((k + 1 : ℕ) : ZMod r) :=
            (cyclic_shift_ne_self e (by omega) hk).symm
          have hnf : e + 1 ≠ e + ((k + 1 : ℕ) : ZMod r) := by
            have hne := cyclic_shift_ne_self (e + 1) hkpos (by omega : k < r)
            convert hne.symm using 1
            push_cast
            abel
          rw [hgap]
          change transferHoleZ (crossGap frame e) (e + 1)
            ((e + 1) + (k : ZMod r)) =
              transferHoleZ frame.gap e (e + ((k + 1 : ℕ) : ZMod r))
          rw [show (e + 1) + (k : ZMod r) = e + ((k + 1 : ℕ) : ZMod r) by
            push_cast; abel]
          exact transfer_after_cross frame e _ hr hif hnf
        · exact hblock.trans rfl
        · exact (fusionFree_append F s first rest).mpr ⟨hfree, hfreeRest⟩

/-- Explicitly transport a cyclic frame's gaps to the `Fin` indexing of the balancer. -/
def finGaps (h : ZMod r → ℕ) : Gaps r :=
  fun i => h (ZMod.finEquiv r i)

theorem finGaps_transfer (h : ZMod r → ℕ) (e f : Fin r) (hef : e ≠ f) :
    finGaps (transferHoleZ h (ZMod.finEquiv r e) (ZMod.finEquiv r f)) =
      transferHole (finGaps h) e f := by
  classical
  funext j
  have hinj := (ZMod.finEquiv r).injective
  by_cases hje : j = e
  · subst j
    simp [finGaps, transferHoleZ, transferHole, hef, hinj.ne_iff.mpr hef]
  by_cases hjf : j = f
  · subst j
    simp [finGaps, transferHoleZ, transferHole]
  · simp [finGaps, transferHoleZ, transferHole, hje, hjf,
      hinj.ne_iff.mpr hje, hinj.ne_iff.mpr hjf]

theorem exists_forward_distance (e f : Fin r) (hef : e ≠ f) :
    ∃ k : ℕ, 0 < k ∧ k < r ∧
      ZMod.finEquiv r e + (k : ZMod r) = ZMod.finEquiv r f := by
  let diff : ZMod r := ZMod.finEquiv r f - ZMod.finEquiv r e
  refine ⟨diff.val, ?_, ZMod.val_lt diff, ?_⟩
  · by_contra h
    have hz : diff.val = 0 := by omega
    have heq : ZMod.finEquiv r f = ZMod.finEquiv r e := by
      have hdiff : diff = 0 := by
        rw [← ZMod.natCast_zmod_val diff, hz]
        simp
      exact sub_eq_zero.mp hdiff
    exact hef ((ZMod.finEquiv r).injective heq.symm)
  · rw [ZMod.natCast_zmod_val]
    dsimp [diff]
    abel

/-- Every distinct ordered pair of gaps has a real-word net transfer. -/
theorem realizeNetTransfer [DecidableEq α] (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (e f : Fin r)
    (hn : 2 ≤ n) (hr : 2 ≤ r) (hef : e ≠ f)
    (source : s.placed = frame.decode)
    (positive : 0 < finGaps frame.gap e) :
    ∃ (next : GapFrame n r α) (word : List Letter),
      run F s word = { s with placed := next.decode } ∧
      finGaps next.gap = transferHole (finGaps frame.gap) e f ∧
      next.block = frame.block ∧ FusionFree F s word := by
  obtain ⟨k, hk0, hk, htarget⟩ := exists_forward_distance e f hef
  obtain ⟨next, word, hrest⟩ :=
    realizeNetTransferZ F s frame (ZMod.finEquiv r e) k hn hr hk0 hk
      source positive
  have hrun := hrest.1
  have hgap := hrest.2.1
  have hblock := hrest.2.2.1
  have hfree := hrest.2.2.2
  refine ⟨next, word, hrun, ?_, hblock, hfree⟩
  rw [hgap, htarget]
  exact finGaps_transfer frame.gap e f hef

end RegisteredAbsorptionChains
