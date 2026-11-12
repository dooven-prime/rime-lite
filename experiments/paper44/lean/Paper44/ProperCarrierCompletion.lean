import Paper44.TerminalLabelEquiv

/-! # Completing a prefix to a fixed proper carrier

The completion preserves literal ordered records, not just checkpoint counts.
It supplies the actual-chain representative used by both the label range
equivalence and the placement fibre theorem.
-/

namespace Paper44

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem sourceFrontier_ext {f g : CheckpointSourceFrontier n}
    (hlo : f.lo = g.lo) (hhi : f.hi = g.hi) : f = g := by
  cases f
  cases g
  simp_all

omit [NeZero n] in
/-- Every nonzero processed symbol lies at or before the last checkpoint. -/
theorem nonzero_le_lastCheckpoint (c : Code (n - 2)) :
    ∀ k (hk : k ≤ n - 2) (i : Fin (n - 2)), i.val < k → c i ≠ none →
      i.val + 1 ≤ lastCodeCheckpoint c k hk := by
  intro k
  induction k with
  | zero => intro hk i hi; omega
  | succ k ih =>
      intro hk i hi hc
      by_cases hik : i.val = k
      · have he : i = ⟨k, by omega⟩ := Fin.ext hik
        rw [he] at hc ⊢
        simp only [lastCodeCheckpoint]
        split
        · contradiction
        · omega
      · have hip : i.val < k := by omega
        have hprev := ih (by omega) i hip hc
        cases hs : c ⟨k, by omega⟩ <;> simp only [lastCodeCheckpoint, hs]
        · exact hprev
        · omega

theorem code_zero_after_absorbed (c : Code (n - 2)) (hn : 2 ≤ n)
    (i : Fin (n - 2)) (hi : (decodeCode c hn).frontier.absorbed ≤ i.val) :
    c i = none := by
  by_contra hc
  have h := nonzero_le_lastCheckpoint c (n - 2) (le_refl _) i i.isLt hc
  rw [← decodeCodePrefix_absorbed c hn] at h
  change i.val + 1 ≤ (decodeCode c hn).frontier.absorbed at h
  omega

/-- One new checkpoint extends an existing proper frontier, retaining all
earlier complete records. The destination remains proper. -/
theorem extend_proper_code_step (hn : 3 ≤ n) (c : Code (n - 2))
    (f : CheckpointSourceFrontier n) (hf : f.lo < f.hi)
    (side : Bool) (ell : ℕ) (hell : 0 < ell)
    (hnext : if side then
      f.lo = (decodeCode c (by omega)).frontier.lo + ell ∧
        f.hi = (decodeCode c (by omega)).frontier.hi
      else f.lo = (decodeCode c (by omega)).frontier.lo ∧
        f.hi + ell = (decodeCode c (by omega)).frontier.hi) :
    ∃ (d : Code (n - 2)) (rho : FusionRecord (ZMod n)),
      (decodeCode d (by omega)).frontier = f ∧
        decodeChain d (by omega) = decodeChain c (by omega) ++ [rho] := by
  let hn2 : 2 ≤ n := by omega
  let old := (decodeCode c hn2).frontier
  change (if side then f.lo = old.lo + ell ∧ f.hi = old.hi
    else f.lo = old.lo ∧ f.hi + ell = old.hi) at hnext
  let b := old.absorbed + ell
  have ho := old.lo_valid
  have hon := old.noncrossing
  have hoi := old.hi_valid
  have hfl := f.lo_valid
  have hfh := f.hi_valid
  have hgap : ell ≤ old.hi - old.lo := by
    cases side <;> simp only [Bool.false_eq_true, ↓reduceIte] at hnext
    all_goals omega
  have hb : b ≤ n - 2 := by
    have htotal := old.remaining_plus_absorbed
    rw [old.remaining_card] at htotal
    dsimp [b]; omega
  have hj : old.absorbed ≤ n - 2 := by
    have htotal := old.remaining_plus_absorbed
    omega
  have hz := fun i hi => code_zero_after_absorbed c hn2 i hi
  have hskip := decodeCodePrefix_skip c hn2 old.absorbed hj (n - 2) (le_refl _) hj
    (by intro i hi _; exact hz i hi)
  have hab : (decodeCodePrefix c hn2 old.absorbed hj).frontier.absorbed = old.absorbed :=
    congrArg CheckpointSourceFrontier.absorbed hskip.1.symm
  obtain ⟨hz', hchain, hcarrier, _⟩ := decodeCodePrefix_insertCheckpoint c hn2
    old.absorbed b hj hb (by dsimp [b]; omega) side hz hab
  let d := insertCheckpoint c b side
  have hskip' := decodeCodePrefix_skip d hn2 b hb (n - 2) (le_refl _) hb
    (by intro i hi _; exact hz' i hi)
  have hcarrier' : (decodeCode d hn2).frontier.carrier = f.carrier := by
    change (decodeCodePrefix d hn2 (n - 2) _).frontier.carrier = _
    rw [hskip'.1, hcarrier, ← hskip.1]
    have hbell : b - old.absorbed = ell := by dsimp [b]; omega
    rw [hbell]
    cases side
    · simp only [Bool.false_eq_true, ↓reduceIte] at hnext
      change old.carrier ∪ old.partnerL ell = f.carrier
      rw [← old.carrier_nextL ell hgap]
      apply congrArg CheckpointSourceFrontier.carrier
      apply sourceFrontier_ext
      · exact hnext.1.symm
      · change old.hi - ell = f.hi
        omega
    · simp only [↓reduceIte] at hnext
      change old.carrier ∪ old.partnerR ell = f.carrier
      rw [← old.carrier_nextR ell hgap]
      apply congrArg CheckpointSourceFrontier.carrier
      exact sourceFrontier_ext hnext.1.symm hnext.2.symm
  let rho := checkpointRecord side old.carrier
    (if side then old.partnerR ell else old.partnerL ell)
  refine ⟨d, rho, (frontier_eq_of_carrier_eq_of_remaining f _ hcarrier'.symm hf).symm, ?_⟩
  have hbell : b - old.absorbed = ell := by dsimp [b]; omega
  rw [← hskip.1, ← hskip.2, hbell] at hchain
  exact hskip'.2.trans hchain

/-- Coordinate containment is sufficient for completion to the exact carrier.
The appended records are outside the already retained saturated prefix. -/
theorem complete_code_to_proper_frontier (hn : 3 ≤ n) (c : Code (n - 2))
    (f : CheckpointSourceFrontier n) (hf : f.lo < f.hi)
    (hlo : (decodeCode c (by omega)).frontier.lo ≤ f.lo)
    (hhi : f.hi ≤ (decodeCode c (by omega)).frontier.hi) :
    ∃ (d : Code (n - 2)) (tail : List (FusionRecord (ZMod n))),
      (decodeCode d (by omega)).frontier = f ∧
        decodeChain d (by omega) = decodeChain c (by omega) ++ tail := by
  let old := (decodeCode c (by omega)).frontier
  change old.lo ≤ f.lo at hlo
  change f.hi ≤ old.hi at hhi
  let mid : CheckpointSourceFrontier n :=
    ⟨f.lo, old.hi, f.lo_valid, by omega, old.hi_valid⟩
  have hm : mid.lo < mid.hi := by dsimp [mid]; omega
  have hfirst : ∃ (d : Code (n - 2)) (tail : List (FusionRecord (ZMod n))),
      (decodeCode d (by omega)).frontier = mid ∧
        decodeChain d (by omega) = decodeChain c (by omega) ++ tail := by
    by_cases he : old.lo = f.lo
    · refine ⟨c, [], ?_, by simp⟩
      exact sourceFrontier_ext he rfl
    · obtain ⟨d, rho, hd, hc⟩ := extend_proper_code_step hn c mid hm true
        (f.lo - old.lo) (by omega) (by
          change f.lo = old.lo + (f.lo - old.lo) ∧ old.hi = old.hi
          omega)
      exact ⟨d, [rho], hd, hc⟩
  obtain ⟨d, tail, hd, hc⟩ := hfirst
  by_cases he : old.hi = f.hi
  · refine ⟨d, tail, hd.trans ?_, hc⟩
    exact sourceFrontier_ext rfl he
  · obtain ⟨e, rho, heq, hec⟩ := extend_proper_code_step hn d f hf false
      (old.hi - f.hi) (by omega) (by
        simp only [Bool.false_eq_true, ↓reduceIte, hd]
        change f.lo = f.lo ∧ f.hi + (old.hi - f.hi) = old.hi
        omega)
    exact ⟨e, tail ++ [rho], heq, by rw [hec, hc, List.append_assoc]⟩

end Paper44
