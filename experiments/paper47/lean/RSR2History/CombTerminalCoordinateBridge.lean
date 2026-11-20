import RSR2History.CombTerminalRouting
import RSR2History.CyclicGapFrames
import RSR2History.ReservedGeometry

/-! Recover named terminal coordinates from a literal packed source and a
cyclically compatible target.  All changes of frame below are coordinate
identities; the route itself is the guarded word in `terminal_route`. -/
namespace RSR2History
open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)
variable {n : Nat} [NeZero n]

/-- The literal source after the comb has released its consecutive holes.
The root numbering starts at the comb and follows the retained physical
cycle.  This contains no word, distance, or budget premise. -/
structure CombTerminalSource (n g l : Nat) [NeZero n] (P : Placement n) where
  size : n = g+l+1
  gap_positive : 1 ≤ g
  roots_positive : 1 ≤ l
  root : Fin n → Nat
  root_bound : ∀ a, root a ≤ l
  root_nonempty : ∀ j, j ≤ l → ∃ a, root a = j
  start : P = combCoordinatePlacement root (fun j => if j = 0 then 0 else g+j)

namespace CombTerminalSource
variable {g l : Nat} {P Q : Placement n}

private def sourceSite (h : CombTerminalSource n g l P) (j : Fin (l+1)) : Fin n :=
  ⟨if j.val = 0 then 0 else g+j.val, by have := h.size; split <;> omega⟩

private theorem sourceSite_strict (h : CombTerminalSource n g l P) :
    StrictMono h.sourceSite := by
  intro i j hij
  change (if i.val = 0 then 0 else g+i.val) <
    (if j.val = 0 then 0 else g+j.val)
  split <;> split <;> have := h.gap_positive <;> omega

private theorem occupied_source (h : CombTerminalSource n g l P) :
    occupiedSites P true = List.ofFn h.sourceSite := by
  classical
  have hs : (occupiedSites P true).Pairwise (· < ·) := by
    rw [List.pairwise_iff_getElem]
    intro i j hi hj hij
    exact occupiedSites_strict P true (show (⟨i, hi⟩ : Fin _) < ⟨j, hj⟩ from hij)
  have ht : (List.ofFn h.sourceSite).Pairwise (· < ·) :=
    List.pairwise_ofFn.mpr h.sourceSite_strict
  apply hs.eq_of_mem_iff ht
  intro q
  simp only [occupiedSites, List.mem_filter, List.mem_finRange, true_and,
    bne_iff_ne, List.mem_ofFn]
  constructor
  · intro hne
    obtain ⟨a, ha⟩ := Finset.nonempty_iff_ne_empty.mpr hne
    have hp := (mem_packetAt _ _ _ _).mp ha
    refine ⟨⟨h.root a, by have := h.root_bound a; omega⟩, ?_⟩
    have he := congrArg Prod.snd hp
    rw [h.start] at he
    change zsite ((if h.root a = 0 then 0 else g+h.root a : Nat) : ZMod n) = q at he
    have hn : (if h.root a = 0 then 0 else g+h.root a) < n := by
      have := h.root_bound a; have := h.size; split <;> omega
    apply Fin.ext
    simpa only [sourceSite, zsite, ZMod.val_natCast, Nat.mod_eq_of_lt hn] using
      congrArg Fin.val he
  · rintro ⟨j, rfl⟩
    obtain ⟨a, ha⟩ := h.root_nonempty j.val (by omega)
    apply Finset.nonempty_iff_ne_empty.mp
    refine ⟨a, (mem_packetAt _ _ _ _).mpr ?_⟩
    rw (occs := .pos [1]) [h.start]
    simp only [combCoordinatePlacement, ha]
    congr 1
    change zsite ((h.sourceSite j).val : ZMod n) = h.sourceSite j
    exact zsite_cast _

private theorem sum_gap_range {r : Nat} [NeZero r]
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

private def gapOffset {r : Nat} [NeZero r]
    (frame : GapFrame n r (Fin n)) (j : Nat) : Nat :=
  j + ∑ i ∈ Finset.range j, frame.gap (i : ZMod r)

private theorem gapOffset_le {r : Nat} [NeZero r]
    (frame : GapFrame n r (Fin n)) {j : Nat} (hj : j ≤ r) :
    gapOffset frame j ≤ j+(n-r) := by
  unfold gapOffset
  have hle := Finset.sum_le_sum_of_subset
    (f := fun i : Nat => frame.gap (i : ZMod r)) (Finset.range_mono hj)
  rw [sum_gap_range] at hle
  omega

private theorem gapOffset_strict {r : Nat} [NeZero r]
    (frame : GapFrame n r (Fin n)) : StrictMono (gapOffset frame) := by
  intro i j hij
  have hle := Finset.sum_le_sum_of_subset
    (f := fun a : Nat => frame.gap (a : ZMod r)) (Finset.range_mono (by omega : i ≤ j))
  unfold gapOffset
  omega

private theorem gapOffset_position {r : Nat} [NeZero r]
    (frame : GapFrame n r (Fin n)) (j : Nat) :
    frame.position (j : ZMod r) = frame.anchor + (gapOffset frame j : ZMod n) := by
  induction j with
  | zero => simp [gapOffset, frame.anchor_eq]
  | succ j ih =>
      have hstep := frame.next_eq (j : ZMod r)
      rw [Nat.cast_add, Nat.cast_one, hstep, ih]
      simp only [gapOffset, Finset.sum_range_succ, Nat.cast_add, Nat.cast_one] at *
      abel

/-- A same-cycle target supplies all target coordinates, including its
physical phase.  Positivity and the terminal gap bound come from the real
gap frame, rather than an assumed routing allowance. -/
theorem coordinates_named (h : CombTerminalSource n g l P)
    (hsig : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ coordinates : CombTerminalCoordinates n g l P Q, coordinates.root = h.root := by
  classical
  let r := l+1
  let : NeZero r := ⟨by dsimp [r]; omega⟩
  have hplen : (occupiedSites P true).length = r := by
    rw [h.occupied_source, List.length_ofFn]
  have hqlen : (occupiedSites Q true).length = r := by
    have he := hsig.perm.length_eq
    simpa only [signature_eq_occupied_map, List.length_map, hplen] using he.symm
  obtain ⟨cut, hcut⟩ := hsig.symm
  let frame := reindexGapFrame (layerGapFrameOfRank Q true hqlen) (cut : ZMod r)
  have hdecode : frame.decode = layerView Q true := by simp [frame]
  have hblocks : frameBlocks frame =
      List.ofFn (fun j : Fin r => packetAt P true (h.sourceSite j)) := by
    rw [show frameBlocks frame = (cyclicSignature Q true).rotate cut by
      simp [frame, frameBlocks_reindex]]
    rw [hcut, signature_eq_occupied_map, h.occupied_source, List.map_ofFn]
    rfl
  have hblock (j : Fin r) :
      frame.block (j.val : ZMod r) = packetAt P true (h.sourceSite j) := by
    have he := congrArg (fun xs : List (Finset (Fin n)) => xs[j.val]?) hblocks
    simpa only [frameBlocks, List.getElem?_ofFn, dif_pos j.isLt, Option.some.injEq] using he
  have hpos (a : Fin n) : Q a = (true, zsite (frame.position (h.root a : ZMod r))) := by
    let j : Fin r := ⟨h.root a, by have := h.root_bound a; dsimp [r]; omega⟩
    have ham : a ∈ packetAt P true (h.sourceSite j) := by
      apply (mem_packetAt _ _ _ _).mpr
      rw (occs := .pos [1]) [h.start]
      change (true, zsite ((h.sourceSite j).val : ZMod n)) = (true, h.sourceSite j)
      rw [zsite_cast]
    have he := frame.decode_at (j.val : ZMod r)
    rw [hdecode, hblock j] at he
    have hp := layerView_some_packet Q true _ _ he
    exact (mem_packetAt _ _ _ _).mp (hp.symm ▸ ham)
  refine ⟨{
    size := h.size
    gap_positive := h.gap_positive
    roots_positive := h.roots_positive
    root := h.root
    root_bound := h.root_bound
    root_nonempty := h.root_nonempty
    target := gapOffset frame
    target_zero := by simp [gapOffset]
    target_strict := fun i j hij _ => gapOffset_strict frame hij
    target_lt := ?_
    target_fits := ?_
    phase := frame.anchor
    start := h.start
    finish := ?_ }, rfl⟩
  · intro j hj
    have hb := gapOffset_le frame (by dsimp [r]; omega : j ≤ r)
    have hs := h.size
    dsimp [r] at hb
    omega
  · intro j hj
    have hb := gapOffset_le frame (by dsimp [r]; omega : j ≤ r)
    have hs := h.size
    dsimp [r] at hb
    omega
  · funext a
    rw [hpos a, gapOffset_position]
    simp only [phaseShift, combCoordinatePlacement, zsite_val_cast]
    congr 2
    abel

theorem coordinates (h : CombTerminalSource n g l P)
    (hsig : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    Nonempty (CombTerminalCoordinates n g l P Q) := by
  obtain ⟨coordinates, _⟩ := h.coordinates_named hsig
  exact ⟨coordinates⟩

/-- The coordinate extraction and terminal router compose without an
additional endpoint or cost assumption. -/
theorem terminal_route (h : CombTerminalSource n g l P) (hn : 1 < n)
    (hsig : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ word, runLogged n hn P word = some (Q, []) ∧
      word.length ≤ l*(n+g-1)+(n-1) := by
  obtain ⟨coordinates⟩ := h.coordinates hsig
  exact coordinates.terminal_route hn

end CombTerminalSource
end RSR2History
