import RegisteredAbsorptionChains.CyclicOrderAdmission
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]
variable {α : Type*}

/-- Pack the named blocks into consecutive physical sites, retaining their
positive cyclic order. The phase specifies the site of named block zero. -/
def packedPosition (phase : ZMod n) (i : ZMod r) : ZMod n :=
  phase + (i.val : ZMod n)

omit [NeZero n] in
theorem packedPosition_injective (phase : ZMod n) (hrn : r ≤ n) :
    Function.Injective (packedPosition (r := r) phase) := by
  intro i j hij
  have hcast : (i.val : ZMod n) = (j.val : ZMod n) := by
    exact add_left_cancel hij
  have hi : i.val < n := (ZMod.val_lt i).trans_le hrn
  have hj : j.val < n := (ZMod.val_lt j).trans_le hrn
  have hval := congrArg ZMod.val hcast
  rw [ZMod.val_natCast_of_lt hi, ZMod.val_natCast_of_lt hj] at hval
  exact ZMod.val_injective r hval

noncomputable def packedPlacement
    (first : LegalNamedPlacement n r α) (phase : ZMod n) :
    Placement n (Finset α) := by
  classical
  exact fun q =>
    if h : ∃ i : ZMod r, packedPosition phase i = q then
      some (first.block (Classical.choose h))
    else none

theorem packedPlacement_at
    (first : LegalNamedPlacement n r α) (phase : ZMod n)
    (hrn : r ≤ n) (i : ZMod r) :
    packedPlacement first phase (packedPosition phase i) = some (first.block i) := by
  classical
  let h : ∃ j : ZMod r, packedPosition phase j = packedPosition phase i :=
    ⟨i, rfl⟩
  have hchoose : Classical.choose h = i :=
    packedPosition_injective phase hrn (Classical.choose_spec h)
  simp [packedPlacement, h, hchoose]

theorem packedPlacement_only_named
    (first : LegalNamedPlacement n r α) (phase : ZMod n)
    (q : ZMod n) (hq : packedPlacement first phase q ≠ none) :
    ∃ i : ZMod r, packedPosition phase i = q := by
  classical
  by_contra h
  simp [packedPlacement, h] at hq

noncomputable def packedLegalNamed
    (first : LegalNamedPlacement n r α) (hrn : r ≤ n)
    (phase : ZMod n) : LegalNamedPlacement n r α where
  placed := packedPlacement first phase
  position := packedPosition phase
  block := first.block
  position_injective := packedPosition_injective phase hrn
  placed_at := packedPlacement_at first phase hrn
  only_named := packedPlacement_only_named first phase
  block_nonempty := first.block_nonempty
  block_disjoint := first.block_disjoint
  atom_covered := first.atom_covered

theorem packedLegalNamed_positive
    (first : LegalNamedPlacement n r α) (hrn : r ≤ n)
    (phase : ZMod n) :
    (packedLegalNamed first hrn phase).PositivelyOrdered := by
  let packed := packedLegalNamed first hrn phase
  have hoffset (k : ℕ) (hk : k < r) : packed.offset k = k := by
    have hkval : (k : ZMod r).val = k := ZMod.val_natCast_of_lt hk
    have hkn : k < n := hk.trans_le hrn
    simp [LegalNamedPlacement.offset, hk, packed,
      packedLegalNamed, packedPosition, hkval,
      ZMod.val_natCast_of_lt hkn, add_sub_cancel_left]
  intro k hk
  by_cases hnext : k + 1 < r
  · rw [hoffset k hk, hoffset (k + 1) hnext]
    omega
  · have hend : k + 1 = r := by omega
    rw [hoffset k hk, hend, packed.offset_end]
    omega

theorem packedLegalNamed_same_order
    (first : LegalNamedPlacement n r α)
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (phase : ZMod n) :
    SameOrientedCyclicOrder first (packedLegalNamed first hrn phase) := by
  exact ⟨rfl, ordered, packedLegalNamed_positive first hrn phase⟩

/-- Consecutive named blocks can be placed at the kernel ports by choosing
the packing phase. This does not swap their source-relative order. -/
theorem packed_adjacent_ports
    (first : LegalNamedPlacement n r α) (hrn : r ≤ n)
    (j : ℕ) (hj : j + 1 < r) :
    let target := packedLegalNamed first hrn (-(j : ZMod n))
    target.placed 0 = some (first.block (j : ZMod r)) ∧
    target.placed 1 = some (first.block ((j + 1 : ℕ) : ZMod r)) := by
  let phase : ZMod n := -(j : ZMod n)
  let target := packedLegalNamed first hrn phase
  have hjr : j < r := by omega
  have hjval : (j : ZMod r).val = j := ZMod.val_natCast_of_lt hjr
  have hnextval : ((j + 1 : ℕ) : ZMod r).val = j + 1 :=
    ZMod.val_natCast_of_lt hj
  have hzero : packedPosition phase (j : ZMod r) = 0 := by
    simp [packedPosition, phase, hjval]
  have hone : packedPosition phase ((j + 1 : ℕ) : ZMod r) = 1 := by
    dsimp only [packedPosition]
    rw [hnextval]
    dsimp only [phase]
    push_cast
    abel
  constructor
  · rw [← hzero]
    exact target.placed_at (j : ZMod r)
  · rw [← hone]
    exact target.placed_at ((j + 1 : ℕ) : ZMod r)

/-- If the adjacent pair is outside the carrier named at zero, the carrier
remains at a third physical site during the outside merger. -/
theorem packed_outside_ports_with_carrier
    (first : LegalNamedPlacement n r α) (hrn : r ≤ n)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r) :
    let target := packedLegalNamed first hrn (-(j : ZMod n))
    target.placed 0 = some (first.block (j : ZMod r)) ∧
    target.placed 1 = some (first.block ((j + 1 : ℕ) : ZMod r)) ∧
    ∃ qC, target.placed qC = some (first.block 0) ∧ qC ≠ 0 ∧ qC ≠ 1 := by
  let phase : ZMod n := -(j : ZMod n)
  let target := packedLegalNamed first hrn phase
  obtain ⟨h0, h1⟩ := packed_adjacent_ports first hrn j hj
  have hj0 : (0 : ZMod r) ≠ (j : ZMod r) := by
    intro h
    have hv := congrArg ZMod.val h
    rw [ZMod.val_natCast_of_lt (by omega : j < r)] at hv
    simp at hv
    omega
  have hj1 : (0 : ZMod r) ≠ ((j + 1 : ℕ) : ZMod r) := by
    intro h
    have hv := congrArg ZMod.val h
    rw [ZMod.val_natCast_of_lt hj] at hv
    simp at hv
  refine ⟨h0, h1, target.position 0, target.placed_at 0, ?_, ?_⟩
  · intro h
    have hposj : target.position (j : ZMod r) = 0 := by
      simpa [target, phase, packedLegalNamed] using
        (show packedPosition phase (j : ZMod r) = 0 by
          simp [packedPosition, phase, ZMod.val_natCast_of_lt (by omega : j < r)])
    exact hj0 (target.position_injective (h.trans hposj.symm))
  · intro h
    have hposj : target.position ((j + 1 : ℕ) : ZMod r) = 1 := by
      change packedPosition phase ((j + 1 : ℕ) : ZMod r) = 1
      dsimp only [packedPosition]
      rw [ZMod.val_natCast_of_lt hj]
      dsimp only [phase]
      push_cast
      abel
    exact hj1 (target.position_injective (h.trans hposj.symm))

end RegisteredAbsorptionChains
