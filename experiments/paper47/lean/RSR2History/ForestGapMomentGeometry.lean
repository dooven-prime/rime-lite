import RSR2History.ForestDominatingCoordinates
import RSR2History.ForestGapMoment

/-! Source gap moments and the displacement budget at one common cyclic cut. -/
namespace RSR2History
open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)

variable {n r : Nat} [NeZero n] [NeZero r]

/-- The actual gap following each named frame packet. -/
def forestFrameGapProfile (frame : GapFrame n r (Fin n)) (i : Fin r) : Nat :=
  frame.gap (i.val : ZMod r)

noncomputable def ForestTerminalSource.gapProfile {P : Placement n}
    (source : ForestTerminalSource n r P) : Fin r → Nat :=
  forestFrameGapProfile source.sourceFrame

private theorem prefix_weight_identity (f : Nat → Nat) (r : Nat) :
    (∑ j ∈ Finset.range r, ∑ i ∈ Finset.range j, f i) +
      (∑ i ∈ Finset.range r, i * f i) =
        (r-1) * ∑ i ∈ Finset.range r, f i := by
  induction r with
  | zero => simp
  | succ r ih =>
      rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_succ]
      by_cases hz : r = 0
      · subst r; simp
      · have hsplit : r = (r-1)+1 := by omega
        simp only [Nat.add_sub_cancel]
        calc
          _ = ((∑ j ∈ Finset.range r, ∑ i ∈ Finset.range j, f i) +
              ∑ i ∈ Finset.range r, i*f i) +
              (∑ i ∈ Finset.range r, f i) + r*f r := by omega
          _ = (r-1)*(∑ i ∈ Finset.range r, f i) +
              (∑ i ∈ Finset.range r, f i) + r*f r := by rw [ih]
          _ = r*((∑ i ∈ Finset.range r, f i)+f r) := by
            calc
              _ = ((r-1)+1)*(∑ i ∈ Finset.range r, f i)+r*f r := by ring
              _ = _ := by rw [←hsplit, Nat.mul_add]

theorem forestFrameGapProfile_sum (frame : GapFrame n r (Fin n)) :
    (∑ i, forestFrameGapProfile frame i) = n-r := by
  unfold forestFrameGapProfile
  exact (Fin.sum_univ_eq_sum_range (fun i => frame.gap (i : ZMod r)) r).trans
    (ForestGapOffsets.sum_total frame)

theorem forestGapWeight_frame_reindex (frame : GapFrame n r (Fin n)) (q : Fin r) :
    forestGapWeight (forestFrameGapProfile frame) q =
      ∑ i ∈ Finset.range r, i * (reindexGapFrame frame (q.val : ZMod r)).gap (i : ZMod r) := by
  unfold forestGapWeight forestFrameGapProfile
  have he (j : Fin r) : ((q+j).val : ZMod r) =
      (j.val : ZMod r)+(q.val : ZMod r) := by
    simp [Fin.val_add, Nat.cast_add, add_comm]
  simp only [he, reindexGapFrame]
  exact Fin.sum_univ_eq_sum_range (fun i => i * frame.gap ((i : ZMod r)+(q.val : ZMod r))) r

theorem forestGapOffset_weight_identity (frame : GapFrame n r (Fin n)) (q : Fin r) :
    (∑ j : Fin r, ForestGapOffsets.offset
      (reindexGapFrame frame (q.val : ZMod r)) j.val) +
      forestGapWeight (forestFrameGapProfile frame) q =
        (r-1)*(n-r) + ∑ j : Fin r, j.val := by
  rw [forestGapWeight_frame_reindex]
  simp only [ForestGapOffsets.offset, Finset.sum_add_distrib]
  rw [Fin.sum_univ_eq_sum_range (fun j => j) r,
    Fin.sum_univ_eq_sum_range (fun j => ∑ i ∈ Finset.range j,
      (reindexGapFrame frame (q.val : ZMod r)).gap (i : ZMod r)) r]
  have hi := prefix_weight_identity
    (fun i => (reindexGapFrame frame (q.val : ZMod r)).gap (i : ZMod r)) r
  rw [ForestGapOffsets.sum_total] at hi
  omega

theorem forestCutOffset_frame_eq
    (p : Fin r → Fin n) (hp : StrictMono p) (blocks : Fin r → Finset (Fin n))
    (q j : Fin r) :
    forestCutOffset p q j = ForestGapOffsets.offset
      (reindexGapFrame (increasingGapFrame p hp blocks) (q.val : ZMod r)) j.val := by
  let frame := reindexGapFrame (increasingGapFrame p hp blocks) (q.val : ZMod r)
  have he := ForestGapOffsets.position_eq frame j.val
  have hpos : frame.position (j.val : ZMod r) = ((p (q+j)).val : ZMod n) := by
    simp only [frame, reindexGapFrame, increasingGapFrame]
    congr 3
    apply Fin.ext
    simp [Fin.val_add, ZMod.val_add, add_comm]
  have hanchor : frame.anchor = ((p q).val : ZMod n) := by
    simp [frame, reindexGapFrame, increasingGapFrame, Nat.mod_eq_of_lt q.isLt]
  rw [hpos, hanchor] at he
  have hcast : (forestCutOffset p q j : ZMod n) =
      (ForestGapOffsets.offset frame j.val : ZMod n) := by
    rw [forestCutOffset_cast p hp q j]
    linear_combination he
  have hsmall : ForestGapOffsets.offset frame j.val < n := by
    have hrn : r ≤ n := by simpa using Fintype.card_le_of_injective p hp.injective
    have := ForestGapOffsets.upper frame j.isLt.le
    have := j.isLt
    omega
  have hval := congrArg ZMod.val hcast
  simpa only [ZMod.val_natCast, Nat.mod_eq_of_lt (forestCutOffset_lt p hp q j),
    Nat.mod_eq_of_lt hsmall] using hval

namespace ForestTerminalSource
variable {P Q : Placement n}

theorem gapProfile_sum (source : ForestTerminalSource n r P) :
    (∑ i, source.gapProfile i) = n-r :=
  forestFrameGapProfile_sum source.sourceFrame

/-- Named frame blocks are read at their actual physical positions. -/
theorem frame_packetAt (source : ForestTerminalSource n r P) (j : ZMod r) :
    packetAt P true (zsite (source.sourceFrame.position j)) = source.sourceFrame.block j := by
  simp [sourceFrame, increasingGapFrame, zsite_cast]

/-- The source frame displays exactly the actual positive named packet cycle. -/
theorem frame_blocks (source : ForestTerminalSource n r P) :
    frameBlocks source.sourceFrame = cyclicSignature P true := by
  rw [signature_eq_occupied_map, source.occupied_source, List.map_ofFn]
  apply congrArg List.ofFn
  funext j
  simp [sourceFrame, frameBlocks, increasingGapFrame, Nat.mod_eq_of_lt j.isLt]

/-- Gaps after the same named target roots, independently of their physical phase. -/
noncomputable def targetGapProfile {source : ForestTerminalSource n r P}
    (coordinates : ForestTerminalCoordinates source Q) : Fin r → Nat :=
  forestFrameGapProfile
    (increasingGapFrame coordinates.target coordinates.target_strict (fun _ => ∅))

/-- The full weighted source displacement account at any common named cut. -/
theorem cut_gap_weight_identity (source : ForestTerminalSource n r P) (q : Fin r) :
    (∑ j : Fin r, forestCutOffset source.site q j) +
      forestGapWeight source.gapProfile q =
        (r-1)*(n-r) + ∑ j : Fin r, j.val := by
  have he := forestGapOffset_weight_identity source.sourceFrame q
  have hh (j : Fin r) : forestCutOffset source.site q j =
      ForestGapOffsets.offset (reindexGapFrame source.sourceFrame (q.val : ZMod r)) j.val :=
    forestCutOffset_frame_eq source.site source.site_strict
      (fun j => packetAt P true (source.site j)) q j
  simpa only [←hh, gapProfile] using he

/-- Exact conservation of the weighted source and target gap differences.
The dominance hypothesis makes every displacement an ordinary natural debt. -/
theorem cut_displacement_gap_balance (source : ForestTerminalSource n r P)
    (coordinates : ForestTerminalCoordinates source Q) (q : Fin r)
    (dom : ∀ j, forestCutOffset coordinates.target q j ≤ forestCutOffset source.site q j) :
    (∑ j : Fin r, (forestCutOffset source.site q j -
      forestCutOffset coordinates.target q j)) + forestGapWeight source.gapProfile q =
        forestGapWeight (targetGapProfile coordinates) q := by
  have hs := source.cut_gap_weight_identity q
  let targetFrame := increasingGapFrame coordinates.target coordinates.target_strict
    (fun _ => (∅ : Finset (Fin n)))
  have ht := forestGapOffset_weight_identity targetFrame q
  have hh (j : Fin r) : forestCutOffset coordinates.target q j =
      ForestGapOffsets.offset (reindexGapFrame targetFrame (q.val : ZMod r)) j.val :=
    forestCutOffset_frame_eq coordinates.target coordinates.target_strict
      (fun _ => ∅) q j
  have ht' : (∑ j : Fin r, forestCutOffset coordinates.target q j) +
      forestGapWeight (targetGapProfile coordinates) q =
        (r-1)*(n-r) + ∑ j : Fin r, j.val := by
    simpa only [←hh, targetGapProfile, targetFrame] using ht
  have hd : (∑ j : Fin r, (forestCutOffset source.site q j -
      forestCutOffset coordinates.target q j)) +
        (∑ j : Fin r, forestCutOffset coordinates.target q j) =
          ∑ j : Fin r, forestCutOffset source.site q j := by
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro j _
    exact Nat.sub_add_cancel (dom j)
  omega

/-- Target gap mass can only reduce the source displacement debt. Its
minimum source moment is retained, rather than dropping every gap position. -/
theorem cut_displacement_moment_bound (source : ForestTerminalSource n r P)
    (coordinates : ForestTerminalCoordinates source Q) (q : Fin r)
    (dom : ∀ j, forestCutOffset coordinates.target q j ≤ forestCutOffset source.site q j) :
    (∑ j : Fin r, (forestCutOffset source.site q j -
      forestCutOffset coordinates.target q j)) + forestGapMoment source.gapProfile ≤
        (r-1)*(n-r) := by
  have he := source.cut_gap_weight_identity q
  have hm := forestGapMoment_le_weight source.gapProfile q
  have ht : (∑ j : Fin r, j.val) ≤
      ∑ j : Fin r, forestCutOffset coordinates.target q j := by
    apply Finset.sum_le_sum
    intro j _
    exact forestCutOffset_lower coordinates.target coordinates.target_strict q j
  have hd : (∑ j : Fin r, (forestCutOffset source.site q j -
      forestCutOffset coordinates.target q j)) +
        (∑ j : Fin r, forestCutOffset coordinates.target q j) =
          ∑ j : Fin r, forestCutOffset source.site q j := by
    rw [←Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro j _
    exact Nat.sub_add_cancel (dom j)
  omega

/-- The original physical common-cut certificate carries its moment budget.
No new routing or free phase change is introduced. -/
theorem dominating_coordinates_moment (source : ForestTerminalSource n r P)
    (hr : 2 ≤ r) (coordinates : ForestTerminalCoordinates source Q) :
    ∃ cert : GapTerminalCoordinates n (n-r) (r-1) P Q,
      cert.displacement + forestGapMoment source.gapProfile ≤ (r-1)*(n-r) := by
  classical
  obtain ⟨q, cert, hs, ht⟩ := source.dominating_coordinates_with_cut hr coordinates
  have hfin (j : Fin r) : Fin.ofNat r j.val = j := by
    apply Fin.ext
    simp [Fin.ofNat_eq_cast, Nat.mod_eq_of_lt j.isLt]
  have dom (j : Fin r) : forestCutOffset coordinates.target q j ≤
      forestCutOffset source.site q j := by
    have hfit := cert.target_fits j.val (by have := j.isLt; omega)
    simpa only [hs, ht, hfin] using hfit
  have hbound := source.cut_displacement_moment_bound coordinates q dom
  have hd : cert.displacement = ∑ j : Fin r,
      (forestCutOffset source.site q j - forestCutOffset coordinates.target q j) := by
    unfold GapTerminalCoordinates.displacement
    have hr1 : r-1+1=r := by omega
    rw [hr1, ←Fin.sum_univ_eq_sum_range]
    apply Finset.sum_congr rfl
    intro j _
    simp only [hs, ht, hfin]
  exact ⟨cert, by simpa only [hd] using hbound⟩

end ForestTerminalSource
end RSR2History
