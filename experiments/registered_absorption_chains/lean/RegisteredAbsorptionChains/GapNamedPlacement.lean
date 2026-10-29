import RegisteredAbsorptionChains.PackedNamedPlacement
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]
variable {α : Type*}

noncomputable def namedPlacementAt
    (first : LegalNamedPlacement n r α)
    (position : ZMod r → ZMod n) : Placement n (Finset α) := by
  classical
  exact fun q =>
    if h : ∃ i : ZMod r, position i = q then
      some (first.block (Classical.choose h))
    else none

theorem namedPlacementAt_at
    (first : LegalNamedPlacement n r α)
    (position : ZMod r → ZMod n) (hinj : Function.Injective position)
    (i : ZMod r) :
    namedPlacementAt first position (position i) = some (first.block i) := by
  classical
  let h : ∃ j : ZMod r, position j = position i := ⟨i, rfl⟩
  have hchoose : Classical.choose h = i := hinj (Classical.choose_spec h)
  simp [namedPlacementAt, h, hchoose]

theorem namedPlacementAt_only_named
    (first : LegalNamedPlacement n r α)
    (position : ZMod r → ZMod n) (q : ZMod n)
    (hq : namedPlacementAt first position q ≠ none) :
    ∃ i, position i = q := by
  classical
  by_contra h
  simp [namedPlacementAt, h] at hq

noncomputable def legalNamedAt
    (first : LegalNamedPlacement n r α)
    (position : ZMod r → ZMod n) (hinj : Function.Injective position) :
    LegalNamedPlacement n r α where
  placed := namedPlacementAt first position
  position := position
  block := first.block
  position_injective := hinj
  placed_at := namedPlacementAt_at first position hinj
  only_named := namedPlacementAt_only_named first position
  block_nonempty := first.block_nonempty
  block_disjoint := first.block_disjoint
  atom_covered := first.atom_covered

/-- Block zero occupies port one; the last named block occupies port zero.
The unused sites are left after block zero in positive cyclic order. -/
def gapOffset (_hrn : r ≤ n) (i : ZMod r) : ℕ :=
  if i.val = 0 then 0 else n - r + i.val

def gapPosition (hrn : r ≤ n) (i : ZMod r) : ZMod n :=
  1 + (gapOffset hrn i : ZMod n)

theorem gapOffset_lt (hrn : r ≤ n) (i : ZMod r) :
    gapOffset hrn i < n := by
  have hi := ZMod.val_lt i
  by_cases h : i.val = 0
  · simp [gapOffset, h]; exact Nat.pos_of_ne_zero (NeZero.ne n)
  · simp only [gapOffset, if_neg h]
    omega

omit [NeZero n] in
theorem gapOffset_injective (hrn : r ≤ n) :
    Function.Injective (gapOffset hrn) := by
  intro i j hij
  have hi := ZMod.val_lt i
  have hj := ZMod.val_lt j
  have hval : i.val = j.val := by
    by_cases hi0 : i.val = 0
    · by_cases hj0 : j.val = 0
      · omega
      · simp [gapOffset, hi0, hj0] at hij
        omega
    · by_cases hj0 : j.val = 0
      · simp [gapOffset, hi0, hj0] at hij
      · simp [gapOffset, hi0, hj0] at hij
        omega
  exact ZMod.val_injective r hval

theorem gapPosition_injective (hrn : r ≤ n) :
    Function.Injective (gapPosition hrn) := by
  intro i j hij
  have hcast : (gapOffset hrn i : ZMod n) =
      (gapOffset hrn j : ZMod n) := by
    exact add_left_cancel hij
  have hval := congrArg ZMod.val hcast
  rw [ZMod.val_natCast_of_lt (gapOffset_lt hrn i),
    ZMod.val_natCast_of_lt (gapOffset_lt hrn j)] at hval
  exact gapOffset_injective hrn hval

noncomputable def gapLegalNamed
    (first : LegalNamedPlacement n r α) (hrn : r ≤ n) :
    LegalNamedPlacement n r α :=
  legalNamedAt first (gapPosition hrn) (gapPosition_injective hrn)

theorem gapLegalNamed_positive
    (first : LegalNamedPlacement n r α)
    (hrn : r ≤ n) (hr : 2 ≤ r) :
    (gapLegalNamed first hrn).PositivelyOrdered := by
  let target := gapLegalNamed first hrn
  have hoffset (k : ℕ) (hk : k < r) :
      target.offset k = if k = 0 then 0 else n - r + k := by
    have hkval : (k : ZMod r).val = k := ZMod.val_natCast_of_lt hk
    have hkn : gapOffset hrn (k : ZMod r) < n := gapOffset_lt hrn _
    simp [LegalNamedPlacement.offset, hk, target, gapLegalNamed,
      legalNamedAt, gapPosition, gapOffset, hkval,
      add_sub_cancel_left]
    split_ifs with h
    · simp
    · rw [← Nat.cast_add]
      exact ZMod.val_natCast_of_lt (by omega)
  intro k hk
  by_cases hnext : k + 1 < r
  · rw [hoffset k hk, hoffset (k + 1) hnext]
    by_cases hk0 : k = 0
    · subst k
      simp
    · simp [hk0]
  · have hend : k + 1 = r := by omega
    rw [hoffset k hk, hend, target.offset_end]
    split_ifs <;> omega

theorem gapLegalNamed_same_order
    (first : LegalNamedPlacement n r α)
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (hr : 2 ≤ r) :
    SameOrientedCyclicOrder first (gapLegalNamed first hrn) :=
  ⟨rfl, ordered, gapLegalNamed_positive first hrn hr⟩

theorem gap_ports
    (first : LegalNamedPlacement n r α)
    (hrn : r ≤ n) (hr : 2 ≤ r) :
    let target := gapLegalNamed first hrn
    target.placed 0 = some (first.block ((r - 1 : ℕ) : ZMod r)) ∧
    target.placed 1 = some (first.block 0) := by
  let target := gapLegalNamed first hrn
  have hlast : ((r - 1 : ℕ) : ZMod r).val = r - 1 :=
    ZMod.val_natCast_of_lt (by omega)
  have hposlast : gapPosition hrn ((r - 1 : ℕ) : ZMod r) = 0 := by
    have hoff : gapOffset hrn ((r - 1 : ℕ) : ZMod r) = n - 1 := by
      have hrm : r - 1 ≠ 0 := by omega
      simp only [gapOffset, hlast, if_neg hrm]
      omega
    simp only [gapPosition, hoff]
    have hsum : 1 + (n - 1) = n := by omega
    calc
      (1 : ZMod n) + ((n - 1 : ℕ) : ZMod n) =
          ((1 + (n - 1) : ℕ) : ZMod n) := by push_cast; rfl
      _ = (n : ZMod n) := congrArg (fun t : ℕ => (t : ZMod n)) hsum
      _ = 0 := ZMod.natCast_self n
  have hposzero : gapPosition hrn (0 : ZMod r) = 1 := by
    simp [gapPosition, gapOffset]
  constructor
  · rw [← hposlast]
    exact target.placed_at ((r - 1 : ℕ) : ZMod r)
  · rw [← hposzero]
    exact target.placed_at 0

end RegisteredAbsorptionChains
