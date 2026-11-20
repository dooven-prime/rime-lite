import RSR2History.CombTerminalCoordinateBridge

/-!
Named coordinates for a general all-upper terminal source. Source and target
hole prefixes are recorded separately: no dominance between them, and no
routing cost bound, is assumed in this certificate.
-/
namespace RSR2History
open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)

namespace ForestGapOffsets

def offset {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (j : Nat) : Nat :=
  j + ∑ i ∈ Finset.range j, frame.gap (i : ZMod r)

theorem sum_total {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) :
    (∑ i ∈ Finset.range r, frame.gap (i : ZMod r)) = n-r := by
  rw [← Fin.sum_univ_eq_sum_range]
  calc
    _ = ∑ j : ZMod r, frame.gap j := by
      apply Fintype.sum_equiv (ZMod.finEquiv r).toEquiv
      intro j
      have hj : ((ZMod.finEquiv r) j).val = j.val := by
        cases r with
        | zero => exact (NeZero.ne 0 rfl).elim
        | succ r => rfl
      apply congrArg frame.gap
      apply ZMod.val_injective
      simp [hj, Nat.mod_eq_of_lt j.isLt]
    _ = n-r := frame.gap_total

theorem lower {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (j : Nat) : j ≤ offset frame j := by
  simp only [offset]
  omega

theorem upper {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) {j : Nat} (hj : j ≤ r) :
    offset frame j ≤ j+(n-r) := by
  unfold offset
  have hle := Finset.sum_le_sum_of_subset
    (f := fun i : Nat => frame.gap (i : ZMod r)) (Finset.range_mono hj)
  rw [sum_total] at hle
  omega

theorem strict {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) : StrictMono (offset frame) := by
  intro i j hij
  have hle := Finset.sum_le_sum_of_subset
    (f := fun a : Nat => frame.gap (a : ZMod r)) (Finset.range_mono (by omega : i ≤ j))
  unfold offset
  omega

theorem position_eq {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (j : Nat) :
    frame.position (j : ZMod r) = frame.anchor + (offset frame j : ZMod n) := by
  induction j with
  | zero => simp [offset, frame.anchor_eq]
  | succ j ih =>
      have hstep := frame.next_eq (j : ZMod r)
      rw [Nat.cast_add, Nat.cast_one, hstep, ih]
      simp only [offset, Finset.sum_range_succ, Nat.cast_add, Nat.cast_one] at *
      abel

end ForestGapOffsets

/-- Names are read from the actual placement. The source cut is at its
occupied physical site zero; each source root is nonempty. -/
structure ForestTerminalSource (n r : Nat) [NeZero n] [NeZero r]
    (P : Placement n) where
  root : Fin n → Fin r
  site : Fin r → Fin n
  site_strict : StrictMono site
  site_zero : site 0 = 0
  root_nonempty : ∀ j, ∃ a, root a = j
  start : ∀ a, P a = (true, site (root a))

/-- Target coordinates have exactly the same indexed named roots. The phase
is a datum of the literal target, not a free physical rotation. -/
structure ForestTerminalCoordinates {n r : Nat} [NeZero n] [NeZero r]
    {P : Placement n} (source : ForestTerminalSource n r P) (Q : Placement n) where
  target : Fin r → Fin n
  target_strict : StrictMono target
  target_zero : target 0 = 0
  target_lower : ∀ j, j.val ≤ (target j).val
  target_upper : ∀ j, (target j).val ≤ j.val+(n-r)
  phase : ZMod n
  finish : ∀ a, Q a = (true, zsite (phase+((target (source.root a)).val : ZMod n)))

namespace ForestTerminalSource
variable {n r : Nat} [NeZero n] [NeZero r] {P Q : Placement n}

theorem rank_le (h : ForestTerminalSource n r P) : r ≤ n := by
  simpa using Fintype.card_le_of_injective h.site h.site_strict.injective

theorem occupied_source (h : ForestTerminalSource n r P) :
    occupiedSites P true = List.ofFn h.site := by
  classical
  have hs : (occupiedSites P true).Pairwise (· < ·) := by
    rw [List.pairwise_iff_getElem]
    intro i j hi hj hij
    exact occupiedSites_strict P true (show (⟨i, hi⟩ : Fin _) < ⟨j, hj⟩ from hij)
  have ht : (List.ofFn h.site).Pairwise (· < ·) :=
    List.pairwise_ofFn.mpr h.site_strict
  apply hs.eq_of_mem_iff ht
  intro q
  simp only [occupiedSites, List.mem_filter, List.mem_finRange, true_and,
    bne_iff_ne, List.mem_ofFn]
  constructor
  · intro hne
    obtain ⟨a, ha⟩ := Finset.nonempty_iff_ne_empty.mpr hne
    have hp := (mem_packetAt _ _ _ _).mp ha
    refine ⟨h.root a, ?_⟩
    exact (congrArg Prod.snd (h.start a)).symm.trans (congrArg Prod.snd hp)
  · rintro ⟨j, rfl⟩
    obtain ⟨a, ha⟩ := h.root_nonempty j
    exact Finset.nonempty_iff_ne_empty.mp
      ⟨a, (mem_packetAt _ _ _ _).mpr (by simpa only [ha] using h.start a)⟩

noncomputable def sourceFrame (h : ForestTerminalSource n r P) : GapFrame n r (Fin n) :=
  increasingGapFrame h.site h.site_strict (fun j => packetAt P true (h.site j))

/-- Source offsets are cumulative *actual* gaps. These need not dominate the
target's gap prefixes in the same displayed cut. -/
theorem source_gap_prefix (h : ForestTerminalSource n r P) (j : Fin r) :
    (h.site j).val = ForestGapOffsets.offset h.sourceFrame j.val := by
  have he := ForestGapOffsets.position_eq h.sourceFrame j.val
  have hp : h.sourceFrame.position (j.val : ZMod r) = ((h.site j).val : ZMod n) := by
    simp [sourceFrame, increasingGapFrame, Nat.mod_eq_of_lt j.isLt]
  have ha : h.sourceFrame.anchor = 0 := by
    simp [sourceFrame, increasingGapFrame, h.site_zero]
  rw [hp, ha, zero_add] at he
  have hb := ForestGapOffsets.upper h.sourceFrame j.isLt.le
  have hrn := h.rank_le
  have ht : ForestGapOffsets.offset h.sourceFrame j.val < n := by omega
  have hv := congrArg ZMod.val he
  simpa only [ZMod.val_natCast, Nat.mod_eq_of_lt (h.site j).isLt,
    Nat.mod_eq_of_lt ht] using hv

theorem source_lower (h : ForestTerminalSource n r P) (j : Fin r) :
    j.val ≤ (h.site j).val := by
  rw [h.source_gap_prefix]
  exact ForestGapOffsets.lower _ _

theorem source_upper (h : ForestTerminalSource n r P) (j : Fin r) :
    (h.site j).val ≤ j.val+(n-r) := by
  rw [h.source_gap_prefix]
  exact ForestGapOffsets.upper _ j.isLt.le

/-- Every cyclically compatible named literal target has target coordinates.
The source root labels and their positive order remain unchanged. -/
theorem target_coordinates (h : ForestTerminalSource n r P)
    (hsig : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    Nonempty (ForestTerminalCoordinates h Q) := by
  classical
  have hplen : (occupiedSites P true).length = r := by
    rw [h.occupied_source, List.length_ofFn]
  have hqlen : (occupiedSites Q true).length = r := by
    have he := hsig.perm.length_eq
    simpa only [signature_eq_occupied_map, List.length_map, hplen] using he.symm
  obtain ⟨cut, hcut⟩ := hsig.symm
  let frame := reindexGapFrame (layerGapFrameOfRank Q true hqlen) (cut : ZMod r)
  have hdecode : frame.decode = layerView Q true := by simp [frame]
  have hblocks : frameBlocks frame =
      List.ofFn (fun j : Fin r => packetAt P true (h.site j)) := by
    rw [show frameBlocks frame = (cyclicSignature Q true).rotate cut by
      simp [frame, frameBlocks_reindex]]
    rw [hcut, signature_eq_occupied_map, h.occupied_source, List.map_ofFn]
    rfl
  have hblock (j : Fin r) :
      frame.block (j.val : ZMod r) = packetAt P true (h.site j) := by
    have he := congrArg (fun xs : List (Finset (Fin n)) => xs[j.val]?) hblocks
    simpa only [frameBlocks, List.getElem?_ofFn, dif_pos j.isLt, Option.some.injEq] using he
  have hpos (a : Fin n) : Q a = (true, zsite (frame.position ((h.root a).val : ZMod r))) := by
    have ham : a ∈ packetAt P true (h.site (h.root a)) :=
      (mem_packetAt _ _ _ _).mpr (h.start a)
    have he := frame.decode_at ((h.root a).val : ZMod r)
    rw [hdecode, hblock (h.root a)] at he
    have hp := layerView_some_packet Q true _ _ he
    exact (mem_packetAt _ _ _ _).mp (hp.symm ▸ ham)
  let target : Fin r → Fin n := fun j =>
    ⟨ForestGapOffsets.offset frame j.val, by
      have hb := ForestGapOffsets.upper frame j.isLt.le
      have hrn := h.rank_le
      omega⟩
  refine ⟨⟨target, ?_, ?_, ?_, ?_, frame.anchor, ?_⟩⟩
  · intro i j hij
    exact ForestGapOffsets.strict frame hij
  · apply Fin.ext
    simp [target, ForestGapOffsets.offset]
  · intro j
    exact ForestGapOffsets.lower frame j.val
  · intro j
    exact ForestGapOffsets.upper frame j.isLt.le
  · intro a
    rw [hpos a, ForestGapOffsets.position_eq]

end ForestTerminalSource
end RSR2History
