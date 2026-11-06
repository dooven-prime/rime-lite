import RegisteredAbsorptionChains.SourceOrderInvariant
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem SourceOrderLift.window_bounds (lift : SourceOrderLift n)
    {x : ℤ} (hx0 : 0 ≤ x) (hxn : x ≤ n) :
    lift.map 0 ≤ lift.map x ∧ lift.map x ≤ lift.map 0 + n := by
  have hleft := lift.monotone hx0
  have hright := lift.monotone hxn
  have hend : lift.map (n : ℤ) = lift.map 0 + n := by
    simpa using lift.periodic 0 1
  omega

/-- A modular fiber can wrap only across the source-window seam. -/
theorem SourceOrderLift.same_residue_in_window (lift : SourceOrderLift n)
    {x z : ℤ} (hx0 : 0 ≤ x) (hxz : x ≤ z) (hzn : z ≤ n)
    (hmod : (lift.map x : ZMod n) = (lift.map z : ZMod n)) :
    lift.map x = lift.map z ∨
      (lift.map x = lift.map 0 ∧ lift.map z = lift.map 0 + n) := by
  have hdiff : ((lift.map z - lift.map x : ℤ) : ZMod n) = 0 := by
    push_cast
    rw [hmod]
    simp
  obtain ⟨k, hk⟩ := (ZMod.intCast_zmod_eq_zero_iff_dvd _ n).mp hdiff
  have hboundsx := lift.window_bounds hx0 (le_trans hxz hzn)
  have hboundsz := lift.window_bounds (le_trans hx0 hxz) hzn
  have hmon := lift.monotone hxz
  have hn : (0 : ℤ) < n := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne n)
  have hdiff_bound : 0 ≤ lift.map z - lift.map x ∧
      lift.map z - lift.map x ≤ (n : ℤ) := by omega
  have hk01 : k = 0 ∨ k = 1 := by
    rcases lt_trichotomy k 0 with hkneg | hzero | hkpos
    · have hkn : k ≤ -1 := by omega
      have : k * (n : ℤ) ≤ -n := by nlinarith
      nlinarith [hk]
    · exact Or.inl hzero
    · by_cases hkone : k = 1
      · exact Or.inr hkone
      · have hktwo : 2 ≤ k := by omega
        have : 2 * (n : ℤ) ≤ k * n := by nlinarith
        nlinarith [hk]
  rcases hk01 with rfl | rfl
  · left
    omega
  · right
    constructor <;> omega

omit [NeZero n] in
theorem SourceOrderLift.position_nat (lift : SourceOrderLift n)
    {x : ℕ} (hx : x < n) :
    lift.position (x : ZMod n) = (lift.map x : ZMod n) := by
  simp [SourceOrderLift.position, ZMod.val_natCast, Nat.mod_eq_of_lt hx]

/-- Linear convexity in the source window `0,...,n-1`. -/
def LinearSourceConvex (B : Finset (ZMod n)) : Prop :=
  ∀ x y z : ℕ, x ≤ y → y ≤ z → z < n →
    (x : ZMod n) ∈ B → (z : ZMod n) ∈ B → (y : ZMod n) ∈ B

/-- A cyclic source arc is an interval, possibly wrapping across atom zero. -/
def CyclicSourceArc (B : Finset (ZMod n)) : Prop :=
  LinearSourceConvex B ∨
    ((0 : ZMod n) ∈ B ∧ LinearSourceConvex (Finset.univ \ B))

theorem SourceOrderLift.source_fiber_cyclic_arc (lift : SourceOrderLift n)
    (q : ZMod n) : CyclicSourceArc (sourceFiber lift.position q) := by
  by_cases hq : q = (lift.map 0 : ZMod n)
  · right
    subst q
    constructor
    · simp [sourceFiber, SourceOrderLift.position]
    · intro x y z hxy hyz hzn hx hz
      have hylt : y < n := by omega
      have hxlt : x < n := by omega
      have hxnot : (lift.map x : ZMod n) ≠ (lift.map 0 : ZMod n) := by
        simpa [sourceFiber, lift.position_nat hxlt] using hx
      have hznot : (lift.map z : ZMod n) ≠ (lift.map 0 : ZMod n) := by
        simpa [sourceFiber, lift.position_nat hzn] using hz
      by_contra hymem
      have hymod : (lift.map y : ZMod n) = (lift.map 0 : ZMod n) := by
        simpa [sourceFiber, lift.position_nat hylt] using hymem
      have hcases := lift.same_residue_in_window
        (x := 0) (z := y) (by omega) (by omega) (by omega) hymod.symm
      have hyvalue : lift.map y = lift.map 0 ∨
          lift.map y = lift.map 0 + n := by
        rcases hcases with heq | ⟨_, heq⟩
        · exact Or.inl heq.symm
        · exact Or.inr heq
      rcases hyvalue with hlow | hhigh
      · have hmx := lift.monotone (show (x : ℤ) ≤ y by exact_mod_cast hxy)
        have hlo := lift.window_bounds (x := x) (by omega) (by omega)
        have hxeq : lift.map x = lift.map 0 := by omega
        exact hxnot (by rw [hxeq])
      · have hmz := lift.monotone (show (y : ℤ) ≤ z by exact_mod_cast hyz)
        have hhi := lift.window_bounds (x := z) (by omega) (by omega)
        have hzeq : lift.map z = lift.map 0 + n := by omega
        exact hznot (by rw [hzeq]; simp)
  · left
    intro x y z hxy hyz hzn hx hz
    have hxlt : x < n := by omega
    have hylt : y < n := by omega
    have hxmod : (lift.map x : ZMod n) = q := by
      simpa [sourceFiber, lift.position_nat hxlt] using hx
    have hzmod : (lift.map z : ZMod n) = q := by
      simpa [sourceFiber, lift.position_nat hzn] using hz
    have hcases := lift.same_residue_in_window
      (x := x) (z := z) (by omega)
      (by exact_mod_cast hxy.trans hyz) (by omega) (hxmod.trans hzmod.symm)
    have heq : lift.map x = lift.map z := by
      rcases hcases with heq | ⟨hseam, _⟩
      · exact heq
      · exact False.elim (hq (by rw [← hxmod, hseam]))
    have hmid := lift.fiber_convex
      (show (x : ℤ) ≤ y by exact_mod_cast hxy)
      (show (y : ℤ) ≤ z by exact_mod_cast hyz) heq
    apply (mem_sourceFiber lift.position (y : ZMod n) q).mpr
    rw [lift.position_nat hylt, hmid]
    exact hxmod

theorem sourceOrdered_blocks_are_cyclic_arcs
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) (q : ZMod n) (B : Finset (ZMod n))
    (hplaced : placed q = some B) :
    B.Nonempty ∧ CyclicSourceArc B := by
  obtain ⟨lift, hsource⟩ := ordered
  obtain ⟨hB, hnonempty⟩ :=
    (placementOfMap_some_iff lift.position q B).mp (hsource ▸ hplaced)
  exact ⟨hnonempty, hB ▸ lift.source_fiber_cyclic_arc q⟩

/-- Every nonzero source block lies strictly inside the positive one-turn
window measured from the block containing source atom zero. -/
theorem SourceOrderLift.positive_offset_of_other_block
    (lift : SourceOrderLift n) (a : ZMod n)
    (ha : lift.position a ≠ lift.position 0) :
    lift.map 0 < lift.map a.val ∧ lift.map a.val < lift.map 0 + n := by
  have hbounds := lift.window_bounds (x := (a.val : ℤ))
    (by omega) (by exact_mod_cast a.val_lt.le)
  have hbottom : lift.map a.val ≠ lift.map 0 := by
    intro heq
    apply ha
    simpa only [SourceOrderLift.position, ZMod.val_zero, Nat.cast_zero] using
      congrArg (fun t : ℤ => (t : ZMod n)) heq
  have htop : lift.map a.val ≠ lift.map 0 + n := by
    intro heq
    apply ha
    simpa only [SourceOrderLift.position, ZMod.val_zero,
      Nat.cast_zero, Int.cast_add, Int.cast_natCast, ZMod.natCast_self, add_zero] using
      congrArg (fun t : ℤ => (t : ZMod n)) heq
  omega

/-- The physical positive offset is the exact integer-lift increment. -/
theorem SourceOrderLift.position_offset_of_other_block
    (lift : SourceOrderLift n) (a : ZMod n)
    (ha : lift.position a ≠ lift.position 0) :
    ((lift.position a - lift.position 0).val : ℤ) =
      lift.map a.val - lift.map 0 := by
  have hbounds := lift.positive_offset_of_other_block a ha
  have hcast : lift.position a - lift.position 0 =
      ((lift.map a.val - lift.map 0 : ℤ) : ZMod n) := by
    simp [SourceOrderLift.position]
  rw [hcast, ZMod.val_intCast]
  exact Int.emod_eq_of_lt (by omega) (by omega)

/-- Source order of distinct blocks agrees with positive physical order.
This comparison is independent of the chosen lift certificate. -/
theorem SourceOrderLift.distinct_blocks_preserve_order
    (lift : SourceOrderLift n) (a b : ZMod n)
    (hab : a.val < b.val)
    (hdistinct : lift.position a ≠ lift.position b)
    (hb0 : lift.position b ≠ lift.position 0) :
    lift.map a.val < lift.map b.val ∧
      ((lift.position a - lift.position 0).val : ℤ) <
        ((lift.position b - lift.position 0).val : ℤ) := by
  have hle := lift.monotone (show (a.val : ℤ) ≤ b.val by omega)
  have hne : lift.map a.val ≠ lift.map b.val := by
    intro heq
    apply hdistinct
    change (lift.map a.val : ZMod n) = (lift.map b.val : ZMod n)
    rw [heq]
  have hstrict : lift.map a.val < lift.map b.val := by omega
  refine ⟨hstrict, ?_⟩
  rw [lift.position_offset_of_other_block b hb0]
  by_cases ha0 : lift.position a = lift.position 0
  · rw [ha0, sub_self]
    simp only [ZMod.val_zero, Int.ofNat_zero]
    have := (lift.positive_offset_of_other_block b hb0).1
    omega
  · rw [lift.position_offset_of_other_block a ha0]
    omega

/-- The key of a nonempty source packet is its first atom after source zero.
It is a property of the atom set, not of a lift or a physical coordinate. -/
noncomputable def sourceBlockKey (B : Finset (ZMod n)) (hB : B.Nonempty) : ℕ :=
  (B.image ZMod.val).min' (hB.image ZMod.val)

theorem sourceBlockKey_mem (B : Finset (ZMod n)) (hB : B.Nonempty) :
    (sourceBlockKey B hB : ZMod n) ∈ B := by
  have hmem := Finset.min'_mem (B.image ZMod.val) (hB.image ZMod.val)
  obtain ⟨a, ha, hval⟩ := Finset.mem_image.mp hmem
  simpa [sourceBlockKey, ← hval, ZMod.natCast_zmod_val] using ha

theorem sourceBlockKey_lt (B : Finset (ZMod n)) (hB : B.Nonempty) :
    sourceBlockKey B hB < n := by
  have hmem := Finset.min'_mem (B.image ZMod.val) (hB.image ZMod.val)
  obtain ⟨a, _, hval⟩ := Finset.mem_image.mp hmem
  simpa [sourceBlockKey, ← hval] using a.val_lt

omit [NeZero n] in
theorem sourceBlockKey_le (B : Finset (ZMod n)) (hB : B.Nonempty)
    (a : ZMod n) (ha : a ∈ B) :
    sourceBlockKey B hB ≤ a.val := by
  exact Finset.min'_le (B.image ZMod.val) a.val
    (Finset.mem_image.mpr ⟨a, ha, rfl⟩)

theorem sourceBlockKey_injective_of_disjoint
    (B C : Finset (ZMod n)) (hB : B.Nonempty) (hC : C.Nonempty)
    (hdisjoint : Disjoint B C)
    (hkey : sourceBlockKey B hB = sourceBlockKey C hC) : False := by
  have hb := sourceBlockKey_mem B hB
  have hc := sourceBlockKey_mem C hC
  rw [hkey] at hb
  exact Finset.disjoint_left.mp hdisjoint hb hc

/-- The canonical source-block keys impose the same positive physical order
on every source-ordered placement. The key uses only the atom block. -/
theorem sourceOrdered_block_key_offsets
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (q₀ qB qC : ZMod n)
    (B₀ B C : Finset (ZMod n))
    (hzero : placed q₀ = some B₀) (zero_mem : (0 : ZMod n) ∈ B₀)
    (hB : placed qB = some B) (hC : placed qC = some C)
    (hBne : B.Nonempty) (hCne : C.Nonempty)
    (hkey : sourceBlockKey B hBne < sourceBlockKey C hCne) :
    (qB - q₀).val < (qC - q₀).val := by
  obtain ⟨lift, hplaced⟩ := ordered
  have hfiber₀ := (placementOfMap_some_iff lift.position q₀ B₀).mp
    (hplaced ▸ hzero)
  have hfiberB := (placementOfMap_some_iff lift.position qB B).mp
    (hplaced ▸ hB)
  have hfiberC := (placementOfMap_some_iff lift.position qC C).mp
    (hplaced ▸ hC)
  have hq₀ : lift.position 0 = q₀ := by
    apply (mem_sourceFiber lift.position 0 q₀).mp
    rw [hfiber₀.1]
    exact zero_mem
  have hqB : lift.position (sourceBlockKey B hBne : ZMod n) = qB := by
    apply (mem_sourceFiber lift.position _ qB).mp
    rw [hfiberB.1]
    exact sourceBlockKey_mem B hBne
  have hqC : lift.position (sourceBlockKey C hCne : ZMod n) = qC := by
    apply (mem_sourceFiber lift.position _ qC).mp
    rw [hfiberC.1]
    exact sourceBlockKey_mem C hCne
  have hqBC : qB ≠ qC := by
    intro heq
    have hsame : B = C := by
      have h := hB.symm.trans (heq ▸ hC)
      exact Option.some.inj h
    subst C
    have hkeys : sourceBlockKey B hBne = sourceBlockKey B hCne := rfl
    omega
  have hqC₀ : qC ≠ q₀ := by
    intro heq
    have hcmem : (0 : ZMod n) ∈ C := by
      rw [← hfiberC.1]
      apply (mem_sourceFiber lift.position 0 qC).mpr
      rw [hq₀, ← heq]
    have hsmall := sourceBlockKey_le C hCne 0 hcmem
    simp only [ZMod.val_zero] at hsmall
    omega
  have hkeys_nat := lift.distinct_blocks_preserve_order
    (sourceBlockKey B hBne : ZMod n)
    (sourceBlockKey C hCne : ZMod n)
    (by rw [ZMod.val_natCast, ZMod.val_natCast]
        simp [Nat.mod_eq_of_lt (sourceBlockKey_lt B hBne),
          Nat.mod_eq_of_lt (sourceBlockKey_lt C hCne)]
        exact hkey)
    (by rw [hqB, hqC]; exact hqBC)
    (by rw [hqC, hq₀]; exact hqC₀)
  have hpos : ((qB - q₀).val : ℤ) < ((qC - q₀).val : ℤ) := by
    simpa only [hqB, hqC, hq₀] using hkeys_nat.2
  exact_mod_cast hpos

/-- The finite set of actually occupied nonempty atom blocks. -/
noncomputable def placedBlocks
    (placed : Placement n (Finset (ZMod n))) :
    Finset (Finset (ZMod n)) :=
  Finset.univ.filter (fun B => B.Nonempty ∧ ∃ q, placed q = some B)

theorem mem_placedBlocks
    (placed : Placement n (Finset (ZMod n)))
    (B : Finset (ZMod n)) :
    B ∈ placedBlocks placed ↔ B.Nonempty ∧ ∃ q, placed q = some B := by
  simp [placedBlocks]

/-- A common block set gives two physical orders induced by the same
source-only keys. This is the order content needed by named admission. -/
theorem sourceOrdered_same_blocks_key_order
    (first second : Placement n (Finset (ZMod n)))
    (ordered₁ : SourceOrdered first) (ordered₂ : SourceOrdered second)
    (same : placedBlocks first = placedBlocks second)
    (B₀ B C : Finset (ZMod n))
    (hB₀ : B₀ ∈ placedBlocks first) (zero_mem : (0 : ZMod n) ∈ B₀)
    (hB : B ∈ placedBlocks first) (hC : C ∈ placedBlocks first)
    (hkey : sourceBlockKey B ((mem_placedBlocks first B).mp hB).1 <
      sourceBlockKey C ((mem_placedBlocks first C).mp hC).1) :
    ∃ q₀ qB qC q₀' qB' qC' : ZMod n,
      first q₀ = some B₀ ∧ first qB = some B ∧ first qC = some C ∧
      second q₀' = some B₀ ∧ second qB' = some B ∧ second qC' = some C ∧
      (qB - q₀).val < (qC - q₀).val ∧
      (qB' - q₀').val < (qC' - q₀').val := by
  obtain ⟨hB₀ne, q₀, hq₀⟩ := (mem_placedBlocks first B₀).mp hB₀
  obtain ⟨hBne, qB, hqB⟩ := (mem_placedBlocks first B).mp hB
  obtain ⟨hCne, qC, hqC⟩ := (mem_placedBlocks first C).mp hC
  have hB₀' : B₀ ∈ placedBlocks second := same ▸ hB₀
  have hB' : B ∈ placedBlocks second := same ▸ hB
  have hC' : C ∈ placedBlocks second := same ▸ hC
  obtain ⟨_, q₀', hq₀'⟩ := (mem_placedBlocks second B₀).mp hB₀'
  obtain ⟨_, qB', hqB'⟩ := (mem_placedBlocks second B).mp hB'
  obtain ⟨_, qC', hqC'⟩ := (mem_placedBlocks second C).mp hC'
  refine ⟨q₀, qB, qC, q₀', qB', qC', hq₀, hqB, hqC,
    hq₀', hqB', hqC', ?_, ?_⟩
  · exact sourceOrdered_block_key_offsets first ordered₁
      q₀ qB qC B₀ B C hq₀ zero_mem hqB hqC hBne hCne hkey
  · exact sourceOrdered_block_key_offsets second ordered₂
      q₀' qB' qC' B₀ B C hq₀' zero_mem hqB' hqC' hBne hCne hkey

end RegisteredAbsorptionChains
