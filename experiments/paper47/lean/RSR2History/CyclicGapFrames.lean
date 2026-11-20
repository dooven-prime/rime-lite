import FusionLogCompression.M3Placement
import RSR2History.SignatureFrames
import Mathlib.Data.Finset.Sort

/-! Geometric frames for a partially occupied layer.  Unlike the stronger
`NamedCyclicPlacement`, `GapFrame` imposes no atom-coverage hypothesis. -/
namespace RSR2History

open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)

private def liftedSite {n r : Nat} (hr : 0 < r) (p : Fin r → Fin n) (k : Nat) : Nat :=
  if h : k < r then (p ⟨k, h⟩).val else (p ⟨0, hr⟩).val + n

private theorem liftedSite_mono {n r : Nat} (hr : 0 < r) (p : Fin r → Fin n)
    (hp : StrictMono p) : Monotone (liftedSite hr p) := by
  intro a b hab
  unfold liftedSite
  split <;> split
  · exact Fin.le_iff_val_le_val.mp (hp.monotone (by exact hab))
  · have := (p ⟨a, by assumption⟩).isLt
    omega
  · omega
  · exact le_rfl

private theorem liftedSite_step_pos {n r : Nat} (hr : 0 < r) (p : Fin r → Fin n)
    (hp : StrictMono p) (k : Nat) (hk : k < r) :
    0 < liftedSite hr p (k+1) - liftedSite hr p k := by
  unfold liftedSite
  rw [dif_pos hk]
  split
  · have := hp (show (⟨k, hk⟩ : Fin r) < ⟨k+1, by assumption⟩ from by simp)
    change (p ⟨k, hk⟩).val < (p ⟨k+1, by assumption⟩).val at this
    omega
  · have := (p ⟨k, hk⟩).isLt
    omega

private theorem sum_zmod_val {r : Nat} [NeZero r] (f : Nat → Nat) :
    (∑ j : ZMod r, f j.val) = ∑ j ∈ Finset.range r, f j := by
  rw [← Fin.sum_univ_eq_sum_range]
  symm
  apply Fintype.sum_equiv (ZMod.finEquiv r).toEquiv
  intro j
  have hj : ((ZMod.finEquiv r) j).val = j.val := by
    cases r with
    | zero => exact (NeZero.ne 0 rfl).elim
    | succ r => rfl
  exact congrArg f hj.symm

/-- A strictly increasing physical enumeration determines positive cyclic gaps. -/
noncomputable def increasingGapFrame {n r : Nat} [NeZero n] [NeZero r]
    (p : Fin r → Fin n) (hp : StrictMono p) (blocks : Fin r → Finset (Fin n)) :
    GapFrame n r (Fin n) := by
  let hr : 0 < r := Nat.pos_of_ne_zero (NeZero.ne r)
  let pos : ZMod r → ZMod n := fun j => ((p ⟨j.val, ZMod.val_lt j⟩).val : ZMod n)
  let delta : Nat → Nat := fun k => liftedSite hr p (k+1) - liftedSite hr p k
  have hpos (j : ZMod r) : 0 < delta j.val :=
    liftedSite_step_pos hr p hp j.val (ZMod.val_lt j)
  have hsum : (∑ j : ZMod r, delta j.val) = n := by
    rw [sum_zmod_val]
    rw [Finset.sum_range_tsub (liftedSite_mono hr p hp)]
    simp [liftedSite, hr]
  have hinj : Function.Injective pos := by
    intro i j hij
    have hval := congrArg ZMod.val hij
    simp only [pos, ZMod.val_natCast, Nat.mod_eq_of_lt (p _).isLt] at hval
    have hfin := hp.injective (Fin.ext hval)
    exact (ZMod.val_injective r) (congrArg Fin.val hfin)
  have hrn : r ≤ n := by
    have h := Fintype.card_le_of_injective p hp.injective
    simpa using h
  refine {
    position := pos
    block := fun j => blocks ⟨j.val, ZMod.val_lt j⟩
    gap := fun j => delta j.val - 1
    anchor := pos 0
    anchor_eq := rfl
    position_injective := hinj
    next_eq := ?_
    gap_total := ?_ }
  · intro j
    have hk := ZMod.val_lt j
    have hdel : 1 + (delta j.val - 1) = delta j.val := by have := hpos j; omega
    have hc : (1 : ZMod n) + ((delta j.val - 1 : Nat) : ZMod n) =
        (delta j.val : ZMod n) := by
      simpa using congrArg (fun x : Nat => (x : ZMod n)) hdel
    rw [add_assoc, hc]
    change pos (j+1) = pos j + (delta j.val : ZMod n)
    have hnext : ((j+1).val : Nat) = (j.val+1) % r := by
      have hcast : j+1 = ((j.val+1 : Nat) : ZMod r) := by simp
      rw [hcast, ZMod.val_natCast]
    by_cases hlt : j.val+1 < r
    · have hv : (j+1).val = j.val+1 := by rw [hnext, Nat.mod_eq_of_lt hlt]
      dsimp [pos, delta]
      simp only [liftedSite, dif_pos hk, dif_pos hlt, hv]
      have hle : (p ⟨j.val, hk⟩).val ≤ (p ⟨j.val+1, hlt⟩).val :=
        hp.monotone (by simp)
      rw [Nat.cast_sub hle]
      abel
    · have he : j.val+1 = r := by omega
      have hv : (j+1).val = 0 := by rw [hnext, he, Nat.mod_self]
      dsimp [pos, delta]
      simp only [liftedSite, dif_pos hk, dif_neg hlt, hv]
      have hle : (p ⟨j.val, hk⟩).val ≤ (p ⟨0, hr⟩).val+n := by
        have := (p ⟨j.val, hk⟩).isLt; omega
      rw [Nat.cast_sub hle, Nat.cast_add, ZMod.natCast_self]
      abel
  · have htotal : (∑ j : ZMod r, (delta j.val - 1)) + r = n := by
      calc
        _ = ∑ j : ZMod r, ((delta j.val - 1)+1) := by simp [Finset.sum_add_distrib]
        _ = ∑ j : ZMod r, delta j.val := by
          apply Finset.sum_congr rfl
          intro j _
          have := hpos j
          omega
        _ = n := hsum
    omega

/-- Reindex names and gaps cyclically while preserving the decoded literal placement. -/
noncomputable def reindexGapFrame {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (cut : ZMod r) : GapFrame n r (Fin n) where
  position j := frame.position (j+cut)
  block j := frame.block (j+cut)
  gap j := frame.gap (j+cut)
  anchor := frame.position cut
  anchor_eq := by simp
  next_eq j := by simpa [add_assoc, add_comm, add_left_comm] using frame.next_eq (j+cut)
  position_injective := frame.position_injective.comp (add_left_injective cut)
  gap_total := by
    have h := Fintype.sum_equiv (Equiv.addRight cut)
      (fun j => frame.gap (j+cut)) frame.gap (fun _ => rfl)
    exact h.trans frame.gap_total

@[simp] theorem reindexGapFrame_decode {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (cut : ZMod r) :
    (reindexGapFrame frame cut).decode = frame.decode := by
  funext q
  by_cases h : ∃ j, frame.position j = q
  · obtain ⟨j, rfl⟩ := h
    have hpos : (reindexGapFrame frame cut).position (j-cut) = frame.position j := by
      simp [reindexGapFrame]
    rw [← hpos, GapFrame.decode_at]
    simp only [reindexGapFrame, sub_add_cancel]
    exact (frame.decode_at j).symm
  · rw [frame.decode_empty q (by simpa using h)]
    apply GapFrame.decode_empty
    intro j hj
    exact h ⟨j+cut, hj⟩

/-- Occupied sites, in increasing physical order. -/
def occupiedSites (P : Placement n) (layer : Layer) : List (Fin n) :=
  (List.finRange n).filter (fun q => packetAt P layer q != ∅)

@[simp] theorem signature_eq_occupied_map (P : Placement n) (layer : Layer) :
    cyclicSignature P layer = (occupiedSites P layer).map (packetAt P layer) := by
  simp [cyclicSignature, layerSlots, stripEmpty, List.ofFn_eq_map, List.filter_map,
    occupiedSites, Function.comp_def]

theorem occupiedSites_strict (P : Placement n) (layer : Layer) :
    StrictMono (occupiedSites P layer).get := by
  have h : (List.finRange n).Pairwise (· < ·) := by
    rw [List.pairwise_iff_getElem]
    intro i j hi hj hij
    simpa using hij
  have hf := h.filter (fun q => packetAt P layer q != ∅)
  intro i j hij
  exact (List.pairwise_iff_getElem.mp hf) i.val j.val i.isLt j.isLt hij

noncomputable def layerGapFrame {n : Nat} [NeZero n]
    (P : Placement n) (layer : Layer) [NeZero (occupiedSites P layer).length] :
    GapFrame n (occupiedSites P layer).length (Fin n) :=
  increasingGapFrame (occupiedSites P layer).get (occupiedSites_strict P layer)
    (fun j => packetAt P layer ((occupiedSites P layer).get j))

/-- Packet observation in the single-ring executor's site/option convention. -/
def layerView {n : Nat} [NeZero n] (P : Placement n) (layer : Layer) :
    RegisteredAbsorptionChains.Placement n (Finset (Fin n)) := fun q =>
  let b := packetAt P layer ⟨q.val, ZMod.val_lt q⟩
  if b = ∅ then none else some b

theorem layerGapFrame_decode {n : Nat} [NeZero n]
    (P : Placement n) (layer : Layer) [NeZero (occupiedSites P layer).length] :
    (layerGapFrame P layer).decode = layerView P layer := by
  classical
  funext q
  let site : Fin n := ⟨q.val, ZMod.val_lt q⟩
  by_cases hb : packetAt P layer site = ∅
  · rw [show layerView P layer q = none by simp [layerView, site, hb]]
    apply GapFrame.decode_empty
    intro j hj
    have hv := congrArg ZMod.val hj
    dsimp [layerGapFrame, increasingGapFrame] at hv
    change (((occupiedSites P layer).get ⟨j.val, ZMod.val_lt j⟩).val : ZMod n).val = q.val at hv
    rw [ZMod.val_natCast] at hv
    rw [Nat.mod_eq_of_lt ((occupiedSites P layer).get ⟨j.val, ZMod.val_lt j⟩).isLt] at hv
    have he : (occupiedSites P layer).get ⟨j.val, ZMod.val_lt j⟩ = site := Fin.ext hv
    have hm := List.get_mem (occupiedSites P layer) ⟨j.val, ZMod.val_lt j⟩
    rw [he] at hm
    have := (List.mem_filter.mp hm).2
    simp [hb] at this
  · have hm : site ∈ occupiedSites P layer := by simp [occupiedSites, hb]
    obtain ⟨j, hj⟩ := List.mem_iff_get.mp hm
    let k : ZMod (occupiedSites P layer).length := (j.val : Nat)
    have hk : k.val = j.val := by simp [k, Nat.mod_eq_of_lt j.isLt]
    have hpos : (layerGapFrame P layer).position k = q := by
      apply (ZMod.val_injective n)
      change (((occupiedSites P layer).get ⟨k.val, ZMod.val_lt k⟩).val : ZMod n).val = q.val
      rw [ZMod.val_natCast]
      simp only [hk]
      rw [Nat.mod_eq_of_lt ((occupiedSites P layer).get j).isLt]
      exact congrArg Fin.val hj
    rw [← hpos, GapFrame.decode_at]
    rw [hpos]
    change some (packetAt P layer ((occupiedSites P layer).get ⟨k.val, ZMod.val_lt k⟩)) = _
    have he : (occupiedSites P layer).get ⟨k.val, ZMod.val_lt k⟩ = site := by simpa [hk] using hj
    rw [he]
    simp [layerView, site, hb]

/-- The linear list of names in a gap frame, with its selected anchor. -/
def frameBlocks {n r : Nat} [NeZero n] [NeZero r] (frame : GapFrame n r (Fin n)) :=
  List.ofFn (fun j : Fin r => frame.block (j.val : ZMod r))

@[simp] theorem layerGapFrame_blocks {n : Nat} [NeZero n]
    (P : Placement n) (layer : Layer) [NeZero (occupiedSites P layer).length] :
    frameBlocks (layerGapFrame P layer) = cyclicSignature P layer := by
  rw [signature_eq_occupied_map]
  have he : frameBlocks (layerGapFrame P layer) =
      List.ofFn (fun j => packetAt P layer ((occupiedSites P layer).get j)) := by
    apply congrArg List.ofFn
    funext j
    simp [layerGapFrame, increasingGapFrame, Nat.mod_eq_of_lt j.isLt]
  rw [he]
  change List.ofFn (packetAt P layer ∘ (occupiedSites P layer).get) = _
  rw [← List.map_ofFn, List.ofFn_get]

theorem frameBlocks_reindex {n r : Nat} [NeZero n] [NeZero r]
    (frame : GapFrame n r (Fin n)) (cut : Nat) :
    frameBlocks (reindexGapFrame frame (cut : ZMod r)) = (frameBlocks frame).rotate cut := by
  apply List.ext_getElem
  · simp [frameBlocks]
  · intro j hj hj'
    simp only [frameBlocks, List.getElem_ofFn, List.getElem_rotate, List.length_ofFn,
      reindexGapFrame]
    congr 1
    simp [Nat.cast_add, ZMod.natCast_mod]

theorem frameBlocks_eq_iff {n r : Nat} [NeZero n] [NeZero r]
    (first second : GapFrame n r (Fin n)) :
    frameBlocks first = frameBlocks second ↔ first.block = second.block := by
  constructor
  · intro h
    funext j
    have he := congrArg (fun xs : List (Finset (Fin n)) => xs[j.val]?) h
    simpa [frameBlocks, List.getElem?_eq_getElem, ZMod.val_lt j,
      ZMod.natCast_zmod_val] using he
  · intro h
    simp [frameBlocks, h]

noncomputable def layerGapFrameOfRank {n r : Nat} [NeZero n] [NeZero r]
    (P : Placement n) (layer : Layer) (hr : (occupiedSites P layer).length = r) :
    GapFrame n r (Fin n) := by
  subst r
  exact layerGapFrame P layer

@[simp] theorem layerGapFrameOfRank_decode {n r : Nat} [NeZero n] [NeZero r]
    (P : Placement n) (layer : Layer) (hr : (occupiedSites P layer).length = r) :
    (layerGapFrameOfRank P layer hr).decode = layerView P layer := by
  subst r
  exact layerGapFrame_decode P layer

@[simp] theorem layerGapFrameOfRank_blocks {n r : Nat} [NeZero n] [NeZero r]
    (P : Placement n) (layer : Layer) (hr : (occupiedSites P layer).length = r) :
    frameBlocks (layerGapFrameOfRank P layer hr) = cyclicSignature P layer := by
  subst r
  exact layerGapFrame_blocks P layer

/-- Matching cyclic signatures provide frames with exactly the same indexed names. -/
theorem common_layer_frames {n r : Nat} [NeZero n] [NeZero r]
    (P Q : Placement n) (layer : Layer)
    (hp : (occupiedSites P layer).length = r)
    (hsig : (cyclicSignature P layer).IsRotated (cyclicSignature Q layer)) :
    ∃ first second : GapFrame n r (Fin n),
      first.decode = layerView P layer ∧ second.decode = layerView Q layer ∧
      first.block = second.block := by
  have hq : (occupiedSites Q layer).length = r := by
    have h := congrArg List.length hsig.choose_spec
    simpa only [List.length_rotate, signature_eq_occupied_map, List.length_map, hp] using h.symm
  obtain ⟨cut, hcut⟩ := hsig.symm
  let first := layerGapFrameOfRank P layer hp
  let target := layerGapFrameOfRank Q layer hq
  refine ⟨first, reindexGapFrame target (cut : ZMod r),
    layerGapFrameOfRank_decode _ _ _, ?_, ?_⟩
  · simp [target]
  · apply (frameBlocks_eq_iff _ _).mp
    rw [frameBlocks_reindex]
    simpa [first, target] using hcut.symm

end RSR2History
