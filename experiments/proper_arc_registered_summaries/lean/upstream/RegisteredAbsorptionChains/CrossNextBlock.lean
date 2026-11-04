import RegisteredAbsorptionChains.Execution
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- A cyclic gap description retaining the physical phase of block zero. -/
structure GapFrame (n r : ℕ) (α : Type*) [NeZero n] [NeZero r] where
  position : ZMod r → ZMod n
  block : ZMod r → Finset α
  gap : ZMod r → ℕ
  anchor : ZMod n
  anchor_eq : position 0 = anchor
  next_eq : ∀ i, position (i + 1) = position i + 1 + gap i
  position_injective : Function.Injective position
  gap_total : (∑ i : ZMod r, gap i) = n - r

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r]

/-- Interpret the named block positions as a physical placement. -/
noncomputable def GapFrame.decode (frame : GapFrame n r α) : Placement n (Finset α) :=
  fun q => if h : ∃ i, frame.position i = q then
    some (frame.block (Classical.choose h)) else none

theorem GapFrame.decode_at (frame : GapFrame n r α) (i : ZMod r) :
    frame.decode (frame.position i) = some (frame.block i) := by
  classical
  have h : ∃ j, frame.position j = frame.position i := ⟨i, rfl⟩
  simp only [GapFrame.decode, dif_pos h]
  congr 1
  exact congrArg frame.block (frame.position_injective (Classical.choose_spec h))

theorem GapFrame.decode_empty (frame : GapFrame n r α) (q : ZMod n)
    (h : ∀ i, frame.position i ≠ q) : frame.decode q = none := by
  classical
  simp [GapFrame.decode, not_exists.mpr h]

/-- The successor block is physically moved one site backward. -/
def crossPosition (frame : GapFrame n r α) (i : ZMod r) : ZMod r → ZMod n :=
  Function.update frame.position (i + 1) (frame.position (i + 1) - 1)

/-- One hole passes from the preceding gap to the following gap. -/
def crossGap (frame : GapFrame n r α) (i : ZMod r) : ZMod r → ℕ :=
  Function.update (Function.update frame.gap i (frame.gap i - 1))
    (i + 1) (frame.gap (i + 1) + 1)

/-- A one-step physical crossing, including the source-hole condition. -/
def CanCross (frame : GapFrame n r α) (i : ZMod r) : Prop :=
  0 < frame.gap i ∧ frame.decode (frame.position (i + 1) - 1) = none

/-- Every site counted by a gap is physically empty in the decoded placement. -/
def GapFrame.Faithful (frame : GapFrame n r α) : Prop :=
  ∀ i (t : ℕ), 0 < t → t ≤ frame.gap i →
    frame.decode (frame.position i + t) = none

private def GapFrame.stepSize (frame : GapFrame n r α) (j : ℕ) : ℕ :=
  1 + frame.gap (j : ZMod r)

private def GapFrame.offset (frame : GapFrame n r α) (k : ℕ) : ℕ :=
  ∑ j ∈ Finset.range k, frame.stepSize j

private theorem GapFrame.offset_succ (frame : GapFrame n r α) (k : ℕ) :
    frame.offset (k + 1) = frame.offset k + frame.stepSize k := by
  simp [GapFrame.offset, Finset.sum_range_succ]

private theorem GapFrame.offset_mono (frame : GapFrame n r α) {a b : ℕ}
    (hab : a ≤ b) : frame.offset a ≤ frame.offset b := by
  unfold GapFrame.offset
  exact Finset.sum_le_sum_of_subset (Finset.range_mono hab)

private theorem GapFrame.offset_strict (frame : GapFrame n r α) {a b : ℕ}
    (hab : a < b) : frame.offset a < frame.offset b := by
  have hs := frame.offset_succ a
  have hm := frame.offset_mono (show a + 1 ≤ b by omega)
  have hp : 0 < frame.stepSize a := by simp [GapFrame.stepSize]
  omega

private theorem GapFrame.offset_total (frame : GapFrame n r α) :
    frame.offset r = n := by
  have hrn : r ≤ n := by
    have h := Fintype.card_le_of_injective frame.position frame.position_injective
    simpa using h
  have hsum : (∑ j ∈ Finset.range r, frame.gap (j : ZMod r)) =
      ∑ j : ZMod r, frame.gap j := by
    rw [← Fin.sum_univ_eq_sum_range]
    have he (j : Fin r) : (ZMod.finEquiv r j : ZMod r) = (j.val : ZMod r) := by
      cases r with
      | zero => exact (NeZero.ne 0 rfl).elim
      | succ m =>
          apply ZMod.val_injective
          cases j with
          | mk value bound =>
              simp only [ZMod.finEquiv]
              exact (Nat.mod_eq_of_lt bound).symm
    calc
      (∑ j : Fin r, frame.gap (j.val : ZMod r)) =
          ∑ j : Fin r, frame.gap ((ZMod.finEquiv r).toEquiv j) := by
            apply Finset.sum_congr rfl
            intro j _
            change frame.gap (j.val : ZMod r) = frame.gap (ZMod.finEquiv r j)
            rw [he j]
      _ = ∑ j : ZMod r, frame.gap j :=
        Equiv.sum_comp (ZMod.finEquiv r).toEquiv frame.gap
  have hsteps : frame.offset r = r +
      ∑ j ∈ Finset.range r, frame.gap (j : ZMod r) := by
    unfold GapFrame.offset GapFrame.stepSize
    simp [Finset.sum_add_distrib]
  rw [hsteps, hsum, frame.gap_total]
  omega

private theorem GapFrame.position_offset (frame : GapFrame n r α) (k : ℕ)
    (hk : k ≤ r) :
    frame.position (k : ZMod r) = frame.anchor + (frame.offset k : ZMod n) := by
  induction k with
  | zero => simp [GapFrame.offset, frame.anchor_eq]
  | succ k ih =>
      have hkle : k ≤ r := by omega
      have hstep := frame.next_eq (k : ZMod r)
      have hcast : ((k + 1 : ℕ) : ZMod r) = (k : ZMod r) + 1 := by push_cast; rfl
      rw [hcast, hstep, ih hkle, frame.offset_succ]
      simp only [GapFrame.stepSize, Nat.cast_add, Nat.cast_one]
      abel

private theorem GapFrame.position_val_offset (frame : GapFrame n r α)
    (j : ZMod r) :
    frame.position j = frame.anchor + (frame.offset j.val : ZMod n) := by
  have hjlt : j.val < r := ZMod.val_lt j
  have h := frame.position_offset j.val (by omega)
  simpa only [ZMod.natCast_zmod_val] using h

/-- The positive cyclic steps and one-turn total leave no named block inside a gap. -/
theorem GapFrame.faithful (frame : GapFrame n r α) : frame.Faithful := by
  intro i t ht hle
  let k := i.val
  let x := frame.offset k + t
  have hk : k < r := ZMod.val_lt i
  have hlo : frame.offset k < x := by dsimp [x]; omega
  have hhi : x < frame.offset (k + 1) := by
    rw [frame.offset_succ]
    dsimp [x, GapFrame.stepSize]
    rw [show ((k : ℕ) : ZMod r) = i from ZMod.natCast_zmod_val i]
    omega
  have hxlt : x < n := by
    calc
      x < frame.offset (k + 1) := hhi
      _ ≤ frame.offset r := frame.offset_mono (by omega)
      _ = n := frame.offset_total
  apply frame.decode_empty
  intro j heq
  have hj : j.val < r := ZMod.val_lt j
  have hylt : frame.offset j.val < n := by
    calc
      frame.offset j.val < frame.offset r := frame.offset_strict hj
      _ = n := frame.offset_total
  have hcast : (frame.offset j.val : ZMod n) = (x : ZMod n) := by
    rw [frame.position_val_offset j, frame.position_val_offset i] at heq
    have heq' : frame.anchor + (frame.offset j.val : ZMod n) =
        frame.anchor + (x : ZMod n) := by
      simpa [x, k, Nat.cast_add, add_assoc] using heq
    exact add_left_cancel heq'
  have hnat : frame.offset j.val = x := by
    have hmod := (ZMod.natCast_eq_natCast_iff' (frame.offset j.val) x n).mp hcast
    rwa [Nat.mod_eq_of_lt hylt, Nat.mod_eq_of_lt hxlt] at hmod
  by_cases hleft : j.val ≤ k
  · have hle' := frame.offset_mono hleft
    omega
  · have hright : k + 1 ≤ j.val := by omega
    have hle' := frame.offset_mono hright
    omega

theorem GapFrame.canCross_of_faithful (frame : GapFrame n r α) (i : ZMod r)
    (faithful : frame.Faithful) (positive : 0 < frame.gap i) :
    CanCross frame i := by
  constructor
  · exact positive
  · have h := faithful i (frame.gap i) positive le_rfl
    have hsite : frame.position (i + 1) - 1 =
        frame.position i + (frame.gap i : ZMod n) := by
      rw [frame.next_eq i]
      abel
    rw [hsite]
    exact h

theorem GapFrame.canCross_of_positive (frame : GapFrame n r α) (i : ZMod r)
    (positive : 0 < frame.gap i) : CanCross frame i :=
  frame.canCross_of_faithful i frame.faithful positive

omit [NeZero r] in
private theorem next_ne_self (i : ZMod r) (hr : 2 ≤ r) : i + 1 ≠ i := by
  intro h
  have hz : (1 : ZMod r) = 0 := by
    have := congrArg (fun x : ZMod r => x - i) h
    simpa [add_sub_cancel_left] using this
  have := ZMod.one_eq_zero_iff.mp hz
  omega

theorem crossGap_donor (frame : GapFrame n r α) (i : ZMod r)
    (hr : 2 ≤ r) : crossGap frame i i = frame.gap i - 1 := by
  simp [crossGap, Function.update_of_ne, (next_ne_self i hr).symm]

theorem crossGap_receiver (frame : GapFrame n r α) (i : ZMod r) :
    crossGap frame i (i + 1) = frame.gap (i + 1) + 1 := by
  simp [crossGap]

theorem crossGap_other (frame : GapFrame n r α) (i j : ZMod r)
    (hji : j ≠ i) (hjk : j ≠ i + 1) : crossGap frame i j = frame.gap j := by
  simp [crossGap, Function.update_of_ne, hji, hjk]

theorem crossPosition_moved (frame : GapFrame n r α) (i : ZMod r) :
    crossPosition frame i (i + 1) = frame.position (i + 1) - 1 := by
  simp [crossPosition]

theorem crossPosition_other (frame : GapFrame n r α) (i j : ZMod r)
    (h : j ≠ i + 1) : crossPosition frame i j = frame.position j := by
  simp [crossPosition, Function.update_of_ne, h]

theorem crossPosition_next_eq (frame : GapFrame n r α) (i j : ZMod r)
    (hr : 2 ≤ r) (positive : 0 < frame.gap i) :
    crossPosition frame i (j + 1) =
      crossPosition frame i j + 1 + (crossGap frame i j : ZMod n) := by
  have hcast : ((frame.gap i - 1 : ℕ) : ZMod n) + 1 = frame.gap i := by
    have hs : frame.gap i - 1 + 1 = frame.gap i := by omega
    exact_mod_cast congrArg (fun x : ℕ => (x : ZMod n)) hs
  by_cases hji : j = i
  · subst j
    rw [crossPosition_moved, crossPosition_other _ _ _ (next_ne_self i hr).symm,
      crossGap_donor _ _ hr, frame.next_eq i]
    calc
      frame.position i + 1 + (frame.gap i : ZMod n) - 1 =
          frame.position i + 1 + ((frame.gap i - 1 : ℕ) : ZMod n) := by
            rw [← hcast]
            abel
      _ = _ := rfl
  by_cases hjk : j = i + 1
  · subst j
    have hnext : i + 1 + 1 ≠ i + 1 := next_ne_self (i + 1) hr
    rw [crossPosition_other _ _ _ hnext, crossPosition_moved,
      crossGap_receiver, frame.next_eq (i + 1)]
    push_cast
    abel
  · have hnext : j + 1 ≠ i + 1 := by
      intro h
      exact hji (add_right_cancel h)
    rw [crossPosition_other _ _ _ hnext, crossPosition_other _ _ _ hjk,
      crossGap_other _ _ _ hji hjk]
    exact frame.next_eq j

theorem crossGap_total (frame : GapFrame n r α) (i : ZMod r)
    (hr : 2 ≤ r) (positive : 0 < frame.gap i) :
    (∑ j : ZMod r, crossGap frame i j) = ∑ j : ZMod r, frame.gap j := by
  classical
  unfold crossGap
  rw [Finset.sum_update_of_mem (Finset.mem_univ (i + 1))]
  rw [Finset.sdiff_singleton_eq_erase]
  have hiMem : i ∈ Finset.univ.erase (i + 1) := by
    simpa using (next_ne_self i hr).symm
  rw [Finset.sum_update_of_mem hiMem]
  rw [Finset.sdiff_singleton_eq_erase]
  have hiSum := Finset.sum_erase_add (Finset.univ.erase (i + 1)) frame.gap hiMem
  have hkSum := Finset.sum_erase_add Finset.univ frame.gap (Finset.mem_univ (i + 1))
  omega

theorem GapFrame.hole_not_position (frame : GapFrame n r α) (q : ZMod n)
    (hole : frame.decode q = none) (j : ZMod r) : frame.position j ≠ q := by
  intro h
  have := frame.decode_at j
  rw [h, hole] at this
  cases this

theorem crossPosition_injective (frame : GapFrame n r α) (i : ZMod r)
    (hole : frame.decode (frame.position (i + 1) - 1) = none) :
    Function.Injective (crossPosition frame i) := by
  intro a b hab
  let k : ZMod r := i + 1
  by_cases ha : a = k
  · subst a
    by_cases hb : b = k
    · exact hb.symm
    · have hnew : crossPosition frame i k = frame.position k - 1 :=
        crossPosition_moved frame i
      have hold : crossPosition frame i b = frame.position b :=
        crossPosition_other frame i b hb
      rw [hnew, hold] at hab
      exact False.elim ((frame.hole_not_position _ hole b) hab.symm)
  · by_cases hb : b = k
    · subst b
      have hnew : crossPosition frame i k = frame.position k - 1 :=
        crossPosition_moved frame i
      have hold : crossPosition frame i a = frame.position a :=
        crossPosition_other frame i a ha
      rw [hnew, hold] at hab
      exact False.elim ((frame.hole_not_position _ hole a) hab)
    · rw [crossPosition_other frame i a ha,
        crossPosition_other frame i b hb] at hab
      exact frame.position_injective hab

/-- Update the physical phase, indexed positions, and two affected gaps together. -/
noncomputable def GapFrame.cross (frame : GapFrame n r α) (i : ZMod r)
    (hr : 2 ≤ r) (can : CanCross frame i) : GapFrame n r α :=
  { position := crossPosition frame i
    block := frame.block
    gap := crossGap frame i
    anchor := crossPosition frame i 0
    anchor_eq := rfl
    next_eq := fun j => crossPosition_next_eq frame i j hr can.1
    position_injective := crossPosition_injective frame i can.2
    gap_total := by rw [crossGap_total frame i hr can.1]; exact frame.gap_total }

theorem GapFrame.cross_faithful (frame : GapFrame n r α) (i : ZMod r)
    (_hn : 2 ≤ n) (hr : 2 ≤ r) (faithful : frame.Faithful)
    (positive : 0 < frame.gap i) :
    (frame.cross i hr (frame.canCross_of_faithful i faithful positive)).Faithful :=
  (frame.cross i hr (frame.canCross_of_faithful i faithful positive)).faithful

theorem GapFrame.cross_anchor_at_zero (frame : GapFrame n r α) (i : ZMod r)
    (hr : 2 ≤ r) (can : CanCross frame i) (h : i + 1 = 0) :
    (frame.cross i hr can).anchor = frame.anchor - 1 := by
  change crossPosition frame i 0 = frame.anchor - 1
  rw [← h, crossPosition_moved, h, frame.anchor_eq]

theorem GapFrame.cross_anchor_else (frame : GapFrame n r α) (i : ZMod r)
    (hr : 2 ≤ r) (can : CanCross frame i) (h : i + 1 ≠ 0) :
    (frame.cross i hr can).anchor = frame.anchor := by
  change crossPosition frame i 0 = frame.anchor
  rw [crossPosition_other frame i 0 (Ne.symm h), frame.anchor_eq]

theorem GapFrame.cross_decode (frame : GapFrame n r α) (i : ZMod r)
    (hn : 2 ≤ n) (hr : 2 ≤ r) (can : CanCross frame i) :
    (frame.cross i hr can).decode =
      moveBack (frame.position (i + 1) - 1) frame.decode := by
  classical
  let k : ZMod r := i + 1
  let old : ZMod n := frame.position k
  let new : ZMod n := old - 1
  let next := frame.cross i hr can
  have hnewold : new ≠ old := by
    intro h
    have hz : (1 : ZMod n) = 0 := by
      have := congrArg (fun x : ZMod n => old - x) h
      simpa [new] using this
    have := ZMod.one_eq_zero_iff.mp hz
    omega
  have hnext : new + 1 = old := by simp [new]
  have hposk : next.position k = new := by
    exact crossPosition_moved frame i
  have hposother (j : ZMod r) (hj : j ≠ k) :
      next.position j = frame.position j :=
    crossPosition_other frame i j hj
  have hblock (j : ZMod r) : next.block j = frame.block j := rfl
  funext q
  change next.decode q = moveBack new frame.decode q
  by_cases hqnew : q = new
  · subst q
    rw [← hposk, next.decode_at k, hblock]
    simp only [moveBack, ite_true]
    rw [hposk, hnext, frame.decode_at k]
  by_cases hqold : q = old
  · subst q
    have empty : next.decode old = none := by
      apply next.decode_empty
      intro j
      by_cases hj : j = k
      · subst j
        rw [hposk]
        exact hnewold
      · rw [hposother j hj]
        intro h
        exact hj (frame.position_injective h)
    rw [empty]
    simp [moveBack, hnewold.symm, hnext]
  have hmove : moveBack new frame.decode q = frame.decode q := by
    simp [moveBack, hqnew, hnext, hqold]
  rw [hmove]
  by_cases hocc : ∃ j, frame.position j = q
  · obtain ⟨j, hjq⟩ := hocc
    have hjk : j ≠ k := by
      intro h
      subst j
      exact hqold hjq.symm
    have hnextj : next.position j = q := by rw [hposother j hjk, hjq]
    calc
      next.decode q = some (next.block j) := by rw [← hnextj, next.decode_at]
      _ = some (frame.block j) := by rw [hblock]
      _ = frame.decode q := by rw [← hjq, frame.decode_at]
  · have hsource : frame.decode q = none := by
      apply frame.decode_empty
      simpa only [not_exists] using hocc
    have htarget : next.decode q = none := by
      apply next.decode_empty
      intro j
      by_cases hj : j = k
      · subst j
        rw [hposk]
        exact Ne.symm hqnew
      · rw [hposother j hj]
        exact (not_exists.mp hocc) j
    rw [hsource, htarget]

variable [DecidableEq α]

/-- A frame-indexed gap crossing is one actual nonfusion word. -/
theorem crossNextBlock_with_hole (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = frame.decode) (can : CanCross frame i) :
    run F s (localLetters (frame.position (i + 1) - 1)) =
      { s with placed := (frame.cross i hr can).decode } := by
  have hole : s.placed (frame.position (i + 1) - 1) = none := by
    rw [source]
    exact can.2
  rw [run_localLetters_safe F s _ hn hole]
  rw [source, frame.cross_decode i hn hr can]

theorem crossNextBlock_correct (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = frame.decode) (faithful : frame.Faithful)
    (positive : 0 < frame.gap i) :
    run F s (localLetters (frame.position (i + 1) - 1)) =
      { s with placed := (frame.cross i hr (frame.canCross_of_faithful i faithful positive)).decode } :=
  crossNextBlock_with_hole F s frame i hn hr source
    (frame.canCross_of_faithful i faithful positive)

theorem crossNextBlock_from_gap (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = frame.decode) (positive : 0 < frame.gap i) :
    run F s (localLetters (frame.position (i + 1) - 1)) =
      { s with placed := (frame.cross i hr (frame.canCross_of_positive i positive)).decode } :=
  crossNextBlock_correct F s frame i hn hr source frame.faithful positive

theorem crossNextBlock_fusionFree (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r)
    (source : s.placed = frame.decode) (positive : 0 < frame.gap i) :
    FusionFree F s (localLetters (frame.position (i + 1) - 1)) := by
  have can := frame.canCross_of_positive i positive
  have hole : s.placed (frame.position (i + 1) - 1) = none := by
    rw [source]
    exact can.2
  exact fusionFree_localLetters F s _ hole

theorem crossNextBlock_preserves_records (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = frame.decode) (faithful : frame.Faithful)
    (positive : 0 < frame.gap i) :
    (run F s (localLetters (frame.position (i + 1) - 1))).origin = s.origin ∧
      (run F s (localLetters (frame.position (i + 1) - 1))).chain = s.chain := by
  rw [crossNextBlock_correct F s frame i hn hr source faithful positive]
  exact ⟨rfl, rfl⟩

private def spacedBlocks6 : Execution 6 (Fin 3) :=
  { placed := fun q =>
      if q = 0 then some {0} else if q = 2 then some {1}
      else if q = 4 then some {2} else none
    origin := none
    chain := [] }

/-- Two physical hole steps do not cross two blocks in the spaced example. -/
private example :
    (run ∅ spacedBlocks6 (routeLetters (holeWalk (1 : ZMod 6) 2))).placed 4 = some {2} := by
  decide

private example :
    (run ∅ spacedBlocks6 (routeLetters (holeWalk (1 : ZMod 6) 2))).placed 3 = none := by
  decide

/-- Crossing the next actual block twice moves the third block to site three. -/
private example :
    (run ∅ spacedBlocks6 (routeLetters ([1, 3] : List (ZMod 6)))).placed 3 = some {2} := by
  decide

end RegisteredAbsorptionChains
