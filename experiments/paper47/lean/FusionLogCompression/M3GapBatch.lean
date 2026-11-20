import FusionLogCompression.M3BatchPlacement
import RegisteredAbsorptionChains.CrossNextBlock

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]
variable {α : Type*} [DecidableEq α]

private theorem next_index_ne (i : ZMod r) (hr : 2 ≤ r) : i + 1 ≠ i := by
  intro h
  have hz : (1 : ZMod r) = 0 := by
    have := congrArg (fun x : ZMod r => x - i) h
    simpa [add_sub_cancel_left] using this
  have := ZMod.one_eq_zero_iff.mp hz
  omega

def gapBatchPosition (frame : GapFrame n r α) (i : ZMod r) (f : ℕ) :
    ZMod r → ZMod n :=
  Function.update frame.position (i + 1) (frame.position (i + 1) - f)

def gapBatchGaps (frame : GapFrame n r α) (i : ZMod r) (f : ℕ) :
    ZMod r → ℕ :=
  Function.update
    (Function.update frame.gap i (frame.gap i - f))
    (i + 1) (frame.gap (i + 1) + f)

/-- The abstract cyclic gap transfer used by the linear scheduler. -/
def cyclicGapTransfer (gap : ZMod r → ℕ) (i : ZMod r) (f : ℕ) :
    ZMod r → ℕ :=
  Function.update
    (Function.update gap i (gap i - f))
    (i + 1) (gap (i + 1) + f)

noncomputable def gapBatchFrame (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) : GapFrame n r α := by
  let k := i + 1
  let t := frame.gap i + 1 - f
  have hki : k ≠ i := next_index_ne i hr
  have htpos : 0 < t := by dsimp [t]; omega
  have htle : t ≤ frame.gap i := by dsimp [t]; omega
  have hsite : frame.position k - (f : ZMod n) =
      frame.position i + (t : ZMod n) := by
    dsimp [t]
    rw [frame.next_eq i]
    have hnat : frame.gap i + 1 - f + f = frame.gap i + 1 := by omega
    have hcast :
        ((frame.gap i + 1 - f : ℕ) : ZMod n) + (f : ZMod n) =
          (frame.gap i + 1 : ZMod n) := by
      simpa only [Nat.cast_add, Nat.cast_one] using
        congrArg (fun x : ℕ => (x : ZMod n)) hnat
    have hcast' : ((frame.gap i + 1 - f : ℕ) : ZMod n) =
        (frame.gap i + 1 : ZMod n) - (f : ZMod n) := by
      exact eq_sub_iff_add_eq.mpr hcast
    rw [hcast']
    abel
  have hnewhole : frame.decode (frame.position k - (f : ZMod n)) = none := by
    rw [hsite]
    exact frame.faithful i t htpos htle
  have hnewne : frame.position k - (f : ZMod n) ≠ frame.position k := by
    intro h
    have hz : (f : ZMod n) = 0 := by
      have := congrArg (fun x : ZMod n => frame.position k - x) h
      simpa using this
    have hdiv : n ∣ f := (ZMod.natCast_eq_zero_iff f n).mp hz
    have hdn := Nat.le_of_dvd (by omega : 0 < f) hdiv
    omega
  have hinj : Function.Injective (gapBatchPosition frame i f) := by
    intro a b hab
    by_cases ha : a = k
    · subst a
      by_cases hb : b = k
      · exact hb.symm
      · have hpos : gapBatchPosition frame i f k =
          frame.position k - (f : ZMod n) := by simp [gapBatchPosition, k]
        have hold : gapBatchPosition frame i f b = frame.position b := by
          simp [gapBatchPosition, k, hb]
        rw [hpos, hold] at hab
        have hposEq : frame.position k - (f : ZMod n) = frame.position b := hab
        have hnone : frame.decode (frame.position b) = none := by
          rw [← hposEq]
          exact hnewhole
        rw [frame.decode_at b] at hnone
        cases hnone
    · by_cases hb : b = k
      · subst b
        have hpos : gapBatchPosition frame i f k =
          frame.position k - (f : ZMod n) := by simp [gapBatchPosition, k]
        have hold : gapBatchPosition frame i f a = frame.position a := by
          simp [gapBatchPosition, k, ha]
        rw [hpos, hold] at hab
        have hposEq : frame.position k - (f : ZMod n) = frame.position a :=
          hab.symm
        have hnone : frame.decode (frame.position a) = none := by
          rw [← hposEq]
          exact hnewhole
        rw [frame.decode_at a] at hnone
        cases hnone
      · apply frame.position_injective
        simpa [gapBatchPosition, k, ha, hb] using hab
  refine
    { position := gapBatchPosition frame i f
      block := frame.block
      gap := gapBatchGaps frame i f
      anchor := gapBatchPosition frame i f 0
      anchor_eq := rfl
      next_eq := ?_
      position_injective := hinj
      gap_total := ?_ }
  · intro j
    by_cases hji : j = i
    · subst j
      have hne : i + 1 ≠ i := next_index_ne i hr
      have hnext : gapBatchPosition frame i f (i + 1) =
          frame.position (i + 1) - (f : ZMod n) := by
        simp [gapBatchPosition]
      have hine : i ≠ i + 1 := by
        simpa [k] using hki.symm
      have hcurr : gapBatchPosition frame i f i = frame.position i := by
        simp [gapBatchPosition, hine]
      have hgap : gapBatchGaps frame i f i = frame.gap i - f := by
        simp [gapBatchGaps, hine]
      rw [hnext, hcurr, hgap, frame.next_eq i]
      have hnat : frame.gap i - f + f = frame.gap i := Nat.sub_add_cancel fits
      have hcast :
          ((frame.gap i - f : ℕ) : ZMod n) + (f : ZMod n) =
            (frame.gap i : ZMod n) := by
        simpa only [Nat.cast_add] using
          congrArg (fun x : ℕ => (x : ZMod n)) hnat
      have hcast' : ((frame.gap i - f : ℕ) : ZMod n) =
          (frame.gap i : ZMod n) - (f : ZMod n) := by
        exact eq_sub_iff_add_eq.mpr hcast
      rw [hcast']
      abel
    by_cases hjk : j = k
    · subst j
      have hnextne : k + 1 ≠ k := next_index_ne k hr
      have hcurr : gapBatchPosition frame i f k =
          frame.position k - (f : ZMod n) := by
        simp [gapBatchPosition, k]
      have hnext : gapBatchPosition frame i f (k + 1) =
          frame.position (k + 1) := by
        simp [gapBatchPosition, k, hnextne]
      have hgap : gapBatchGaps frame i f k = frame.gap k + f := by
        simp [gapBatchGaps, k, next_index_ne i hr]
      rw [hnext, hcurr, hgap, frame.next_eq k]
      push_cast
      abel
    · have hjnext : j + 1 ≠ k := by
        intro h
        exact hji (add_right_cancel h)
      simp [gapBatchPosition, gapBatchGaps, k, hji, hjk, hjnext,
        frame.next_eq j]
  · classical
    have hki : i ≠ i + 1 := Ne.symm (next_index_ne i hr)
    unfold gapBatchGaps
    rw [Finset.sum_update_of_mem (Finset.mem_univ (i + 1))]
    rw [Finset.sdiff_singleton_eq_erase]
    have hiMem : i ∈ Finset.univ.erase (i + 1) := by
      simpa using hki
    rw [Finset.sum_update_of_mem hiMem]
    rw [Finset.sdiff_singleton_eq_erase]
    have hiSum := Finset.sum_erase_add (Finset.univ.erase (i + 1))
      frame.gap hiMem
    have hkSum := Finset.sum_erase_add Finset.univ frame.gap
      (Finset.mem_univ (i + 1))
    rw [← frame.gap_total]
    rw [← hkSum]
    rw [← hiSum]
    omega

theorem gapBatchFrame_gap_donor (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) :
    (gapBatchFrame frame i f hr positive fits f_lt).gap i = frame.gap i - f := by
  simp [gapBatchFrame, gapBatchGaps, Function.update_of_ne,
    (next_index_ne i hr).symm]

theorem gapBatchFrame_gap_receiver (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) :
    (gapBatchFrame frame i f hr positive fits f_lt).gap (i + 1) =
      frame.gap (i + 1) + f := by
  simp [gapBatchFrame, gapBatchGaps, Function.update_of_ne,
    (next_index_ne i hr).symm]

/-- A physical frame batch changes its gap vector by exactly the abstract
donor/receiver transfer; this is the interface used to compose scheduled
flow edges. -/
theorem gapBatchFrame_gap_transfer (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) :
    (gapBatchFrame frame i f hr positive fits f_lt).gap =
      cyclicGapTransfer frame.gap i f := by
  rfl

theorem gapBatchFrame_position_moved (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) :
    (gapBatchFrame frame i f hr positive fits f_lt).position (i + 1) =
      frame.position (i + 1) - (f : ZMod n) := by
  simp [gapBatchFrame, gapBatchPosition]

theorem gapBatchFrame_position_other (frame : GapFrame n r α) (i j : ZMod r)
    (f : ℕ) (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) (hji : j ≠ i + 1) :
    (gapBatchFrame frame i f hr positive fits f_lt).position j =
      frame.position j := by
  simp [gapBatchFrame, gapBatchPosition, hji]

private theorem gapBatch_site_ne (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (positive : 0 < f) (f_lt : f < n) :
    frame.position (i + 1) - (f : ZMod n) ≠ frame.position (i + 1) := by
  intro h
  have hz : (f : ZMod n) = 0 := by
    have := congrArg (fun x : ZMod n => frame.position (i + 1) - x) h
    simpa using this
  have hdiv : n ∣ f := (ZMod.natCast_eq_zero_iff f n).mp hz
  have hle := Nat.le_of_dvd (by omega : 0 < f) hdiv
  omega

private theorem gapBatch_site_is_hole (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (positive : 0 < f) (fits : f ≤ frame.gap i) :
    frame.decode (frame.position (i + 1) - (f : ZMod n)) = none := by
  let t := frame.gap i + 1 - f
  have htpos : 0 < t := by dsimp [t]; omega
  have htle : t ≤ frame.gap i := by dsimp [t]; omega
  have hcoord : frame.position (i + 1) - (f : ZMod n) =
      frame.position i + (t : ZMod n) := by
    dsimp [t]
    rw [frame.next_eq i]
    have hnat : frame.gap i + 1 - f + f = frame.gap i + 1 := by omega
    have hcast :
        ((frame.gap i + 1 - f : ℕ) : ZMod n) + (f : ZMod n) =
          (frame.gap i + 1 : ZMod n) := by
      convert congrArg (fun x : ℕ => (x : ZMod n)) hnat using 1 <;>
        simp [Nat.cast_add, Nat.cast_one]
    have hcast' : ((frame.gap i + 1 - f : ℕ) : ZMod n) =
        (frame.gap i + 1 : ZMod n) - (f : ZMod n) := by
      exact eq_sub_iff_add_eq.mpr hcast
    rw [hcast']
    abel
  rw [hcoord]
  exact frame.faithful i t htpos htle

theorem gapBatchFrame_decode (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hr : 2 ≤ r) (positive : 0 < f) (fits : f ≤ frame.gap i)
    (f_lt : f < n) :
    (gapBatchFrame frame i f hr positive fits f_lt).decode =
      batchTarget frame.decode (frame.position (i + 1)) f := by
  classical
  let next := gapBatchFrame frame i f hr positive fits f_lt
  let oldSite := frame.position (i + 1)
  let newSite := oldSite - (f : ZMod n)
  have hmoved : next.position (i + 1) = newSite :=
    gapBatchFrame_position_moved frame i f hr positive fits f_lt
  have holdne : newSite ≠ oldSite :=
    gapBatch_site_ne frame i f positive f_lt
  funext z
  by_cases hznew : z = newSite
  · subst z
    rw [← hmoved, next.decode_at]
    simp [next, gapBatchFrame, gapBatchPosition, batchTarget, newSite, oldSite,
      frame.decode_at, (Ne.symm holdne)]
  by_cases hzold : z = oldSite
  · subst z
    have hnone : next.decode oldSite = none := by
      apply next.decode_empty
      intro j
      by_cases hj : j = i + 1
      · subst j
        rw [hmoved]
        exact holdne
      · rw [gapBatchFrame_position_other frame i j f hr positive fits f_lt hj]
        intro heq
        exact hj (frame.position_injective heq)
    rw [hnone]
    have holdne' : oldSite ≠ newSite := Ne.symm holdne
    simp [batchTarget, oldSite, newSite, holdne', frame.decode_at]
  · have hsites :
        (∃ j, next.position j = z) ↔ ∃ j, frame.position j = z := by
      constructor
      · rintro ⟨j, hj⟩
        by_cases hjm : j = i + 1
        · subst j
          rw [hmoved] at hj
          exact False.elim (hznew hj.symm)
        · refine ⟨j, ?_⟩
          rw [gapBatchFrame_position_other frame i j f hr positive fits f_lt hjm] at hj
          exact hj
      · rintro ⟨j, hj⟩
        by_cases hjm : j = i + 1
        · subst j
          have : z = oldSite := by simpa [oldSite] using hj.symm
          exact False.elim (hzold this)
        · refine ⟨j, ?_⟩
          rw [gapBatchFrame_position_other frame i j f hr positive fits f_lt hjm]
          exact hj
    by_cases hocc : ∃ j, next.position j = z
    · obtain ⟨j, hj⟩ := hocc
      have hjm : j ≠ i + 1 := by
        intro heq
        subst j
        rw [hmoved] at hj
        exact hznew hj.symm
      have hsource : frame.position j = z := by
        rw [← gapBatchFrame_position_other frame i j f hr positive fits f_lt hjm]
        exact hj
      calc
        next.decode z = next.decode (next.position j) := by rw [hj]
        _ = some (next.block j) := next.decode_at j
        _ = some (frame.block j) := rfl
        _ = frame.decode (frame.position j) := (frame.decode_at j).symm
        _ = frame.decode z := by rw [hsource]
        _ = batchTarget frame.decode oldSite f z := by
          simp [batchTarget, oldSite, newSite, hznew, hzold]
    · have hsourceNone : frame.decode z = none := by
        apply frame.decode_empty
        intro j hj
        have hjm : j ≠ i + 1 := by
          intro heq
          subst j
          have : z = oldSite := by simpa [oldSite] using hj.symm
          exact hzold this
        have hnext : next.position j = frame.position j :=
          gapBatchFrame_position_other frame i j f hr positive fits f_lt hjm
        exact hocc ⟨j, by rw [hnext]; exact hj⟩
      have hnextNone : next.decode z = none := by
        apply next.decode_empty
        intro j hj
        exact hocc ⟨j, hj⟩
      rw [hnextNone]
      simp [batchTarget, oldSite, newSite, hznew, hzold, hsourceNone]

/-- The compressed M1 word realizes the corresponding named-frame update. -/
theorem realizeGapBatch (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hn : 3 ≤ n) (hr : 2 ≤ r) (positive : 0 < f)
    (fits : f ≤ frame.gap i) (source : s.placed = frame.decode) :
    FusionFree F s (batchWord (frame.position (i + 1)) f) ∧
      run F s (batchWord (frame.position (i + 1)) f) =
        { s with placed := (gapBatchFrame frame i f hr positive fits
          (by
            have hle : frame.gap i ≤ n - r := by
              have hsum := Finset.single_le_sum
                (fun j _ => Nat.zero_le (frame.gap j))
                (Finset.mem_univ i)
              rw [frame.gap_total] at hsum
              exact hsum
            omega)).decode } ∧
      (batchWord (frame.position (i + 1)) f).length ≤ 2 * n + f := by
  have hgap : frame.gap i ≤ n - r := by
    have hsum := Finset.single_le_sum
      (fun j _ => Nat.zero_le (frame.gap j)) (Finset.mem_univ i)
    rw [frame.gap_total] at hsum
    exact hsum
  have hbound : f ≤ n - 2 := by omega
  have hf_lt : f < n := by omega
  have hpacket : s.placed (frame.position (i + 1)) =
      some (frame.block (i + 1)) := by
    rw [source]
    exact frame.decode_at (i + 1)
  have hholes : ∀ k : ℕ, 1 ≤ k → k ≤ f →
      s.placed (frame.position (i + 1) - (k : ZMod n)) = none := by
    intro k hk hkf
    have hkfit : k ≤ frame.gap i := by omega
    rw [source]
    exact gapBatch_site_is_hole frame i k (by omega) hkfit
  obtain ⟨hfree, hrun, hlen⟩ :=
    batchWord_spec F s (frame.position (i + 1)) (frame.block (i + 1))
      f hn positive hbound hpacket hholes
  refine ⟨hfree, ?_, hlen⟩
  rw [hrun]
  simp only [withPlaced]
  rw [source, gapBatchFrame_decode frame i f hr positive fits hf_lt]

private theorem gapFrame_gap_le_n_sub_rank (frame : GapFrame n r α) (i : ZMod r) :
    frame.gap i ≤ n - r := by
  have hsum := Finset.single_le_sum
    (fun j _ => Nat.zero_le (frame.gap j)) (Finset.mem_univ i)
  rw [frame.gap_total] at hsum
  exact hsum

/-- Package one positive frame-flow edge as the legal M1 placement move
consumed by `BatchPlacementPlan`. -/
noncomputable def gapFrameLegalPlacementBatch (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hn : 3 ≤ n) (hr : 2 ≤ r) (positive : 0 < f)
    (fits : f ≤ frame.gap i) (source : s.placed = frame.decode) :
    LegalPlacementBatch F s := by
  have hgap := gapFrame_gap_le_n_sub_rank frame i
  have hshort : f ≤ n - 2 := by omega
  refine ⟨frame.position (i + 1), f, frame.block (i + 1),
    by omega, hshort, ?_, ?_⟩
  · rw [source]
    exact frame.decode_at (i + 1)
  · intro k hk₁ hkf
    rw [source]
    exact gapBatch_site_is_hole frame i k (by omega) (by omega)

/-- The target selected by the generic placement-plan interface is the
decoded frame produced by the corresponding gap-flow edge. -/
theorem gapFrameLegalPlacementBatch_target (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hn : 3 ≤ n) (hr : 2 ≤ r) (positive : 0 < f)
    (fits : f ≤ frame.gap i) (source : s.placed = frame.decode) :
    (gapFrameLegalPlacementBatch F s frame i f hn hr positive fits source).target =
      (gapBatchFrame frame i f hr positive fits
        (by have hgap := gapFrame_gap_le_n_sub_rank frame i; omega)).decode := by
  rw [LegalPlacementBatch.target]
  change batchTarget s.placed (frame.position (i + 1)) f = _
  rw [source]
  have hgap := gapFrame_gap_le_n_sub_rank frame i
  exact (gapBatchFrame_decode frame i f hr positive fits (by omega)).symm

/-- Compose a real gap-frame batch with any plan for the resulting frame.
This bridges the scheduled gap invariant to the inductive plan. -/
noncomputable def gapFrameBatch_plan_step (F : Finset α) (s : Execution n α)
    (frame : GapFrame n r α) (i : ZMod r) (f : ℕ)
    (hn : 3 ≤ n) (hr : 2 ≤ r) (positive : 0 < f)
    (fits : f ≤ frame.gap i) (source : s.placed = frame.decode)
    {target : Placement n (Finset α)}
    (tail : BatchPlacementPlan F
      {s with placed := (gapBatchFrame frame i f hr positive fits (by
        have hgap := gapFrame_gap_le_n_sub_rank frame i
        omega)).decode} target) :
    BatchPlacementPlan F s target := by
  let move := gapFrameLegalPlacementBatch F s frame i f hn hr positive fits source
  have htarget := gapFrameLegalPlacementBatch_target F s frame i f
    hn hr positive fits source
  refine BatchPlacementPlan.step s move ?_
  rw [show move.target =
    (gapBatchFrame frame i f hr positive fits (by
      have hgap := gapFrame_gap_le_n_sub_rank frame i
      omega)).decode from htarget]
  exact tail

end FusionLogCompression
