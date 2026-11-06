import RegisteredAbsorptionChains.GapPotential
import Mathlib.Tactic

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {r : ℕ} [NeZero r]

/-- The mass of a cyclic gap vector, written using the standard `Finset.range`
enumeration of `Fin r`. -/
def gapMass (g : Gaps r) : ℕ :=
  ∑ j ∈ Finset.range r, g ⟨j % r, Nat.mod_lt _ (NeZero.pos r)⟩

/-- Prefix mass through the first `k` gaps. The modulo index makes the
definition total; all uses below have `k ≤ r`, so no wrap occurs. -/
def gapPrefix (g : Gaps r) (k : ℕ) : ℕ :=
  ∑ j ∈ Finset.range k, g ⟨j % r, Nat.mod_lt _ (NeZero.pos r)⟩

theorem gapPrefix_zero (g : Gaps r) : gapPrefix g 0 = 0 := by
  simp [gapPrefix]

theorem gapPrefix_succ (g : Gaps r) (k : ℕ) :
    gapPrefix g (k + 1) = gapPrefix g k +
      g ⟨k % r, Nat.mod_lt _ (NeZero.pos r)⟩ := by
  simp [gapPrefix, Finset.sum_range_succ]

theorem gapPrefix_le_mass (g : Gaps r) (k : ℕ) (hk : k ≤ r) :
    gapPrefix g k ≤ gapMass g := by
  unfold gapPrefix gapMass
  exact Finset.sum_le_sum_of_subset (Finset.range_mono hk)

theorem gapPrefix_mono (g : Gaps r) {k l : ℕ} (hkl : k ≤ l) :
    gapPrefix g k ≤ gapPrefix g l := by
  unfold gapPrefix
  apply Finset.sum_le_sum_of_subset
  exact Finset.range_mono hkl

/-- Prefix discrepancy between two gap vectors, measured in integers so
positive and negative imbalances are both retained. -/
def gapPrefixDiff (g target : Gaps r) (i : Fin r) : ℤ :=
  (gapPrefix g (i.val + 1) : ℤ) - gapPrefix target (i.val + 1)

def gapPrefixDiffSet (g target : Gaps r) : Finset ℤ :=
  Finset.univ.image (gapPrefixDiff g target)

noncomputable def gapPrefixDiffMin (g target : Gaps r) : ℤ :=
  (gapPrefixDiffSet g target).min' (by
    obtain ⟨i⟩ : Nonempty (Fin r) := Fin.pos_iff_nonempty.mp (NeZero.pos r)
    exact ⟨gapPrefixDiff g target i, Finset.mem_image.mpr ⟨i, Finset.mem_univ _, rfl⟩⟩)

/-- Normalized cyclic hole flow: subtract the least prefix discrepancy so all
edge flows are nonnegative and at least one edge has zero flow. -/
noncomputable def normalizedGapFlow (g target : Gaps r) : Gaps r :=
  fun i => Int.toNat (gapPrefixDiff g target i - gapPrefixDiffMin g target)

def previousGap (i : Fin r) : Fin r :=
  if i.val = 0 then ⟨r - 1, by have := NeZero.pos r; omega⟩
  else ⟨i.val - 1, by have := i.isLt; omega⟩

theorem gapPrefixDiffMin_le (g target : Gaps r) (i : Fin r) :
    gapPrefixDiffMin g target ≤ gapPrefixDiff g target i := by
  unfold gapPrefixDiffMin gapPrefixDiffSet
  apply Finset.min'_le
  exact Finset.mem_image.mpr ⟨i, Finset.mem_univ _, rfl⟩

theorem normalizedGapFlow_int (g target : Gaps r) (i : Fin r) :
    (normalizedGapFlow g target i : ℤ) =
      gapPrefixDiff g target i - gapPrefixDiffMin g target := by
  simp only [normalizedGapFlow]
  exact Int.toNat_of_nonneg (sub_nonneg.mpr (gapPrefixDiffMin_le g target i))

private theorem gapPrefixDiff_variation_le (g target : Gaps r)
    (total : gapMass g = gapMass target) (i j : Fin r) :
    gapPrefixDiff g target i - gapPrefixDiff g target j ≤ gapMass g := by
  unfold gapPrefixDiff
  by_cases hij : i.val ≤ j.val
  · have hg : gapPrefix g (i.val + 1) ≤ gapPrefix g (j.val + 1) :=
      gapPrefix_mono g (by omega)
    have ht : gapPrefix target (i.val + 1) ≤ gapPrefix target (j.val + 1) :=
      gapPrefix_mono target (by omega)
    have htBound : gapPrefix target (j.val + 1) ≤ gapMass target :=
      gapPrefix_le_mass target _ (by have := j.isLt; omega)
    rw [← total] at htBound
    have hgBound : gapPrefix g (i.val + 1) ≤ gapMass g :=
      gapPrefix_le_mass g _ (by have := i.isLt; omega)
    omega
  · have hji : j.val ≤ i.val := by omega
    have hg : gapPrefix g (j.val + 1) ≤ gapPrefix g (i.val + 1) :=
      gapPrefix_mono g (by omega)
    have ht : gapPrefix target (j.val + 1) ≤ gapPrefix target (i.val + 1) :=
      gapPrefix_mono target (by omega)
    have htBound : gapPrefix target (j.val + 1) ≤ gapMass target :=
      gapPrefix_le_mass target _ (by have := j.isLt; omega)
    rw [← total] at htBound
    have hgBound : gapPrefix g (i.val + 1) ≤ gapMass g :=
      gapPrefix_le_mass g _ (by have := i.isLt; omega)
    omega

theorem normalizedGapFlow_le_mass (g target : Gaps r)
    (total : gapMass g = gapMass target) (i : Fin r) :
    normalizedGapFlow g target i ≤ gapMass g := by
  have hmin := gapPrefixDiffMin_le g target i
  have hmin_exists : ∃ j : Fin r,
      gapPrefixDiff g target j = gapPrefixDiffMin g target := by
    have hm := Finset.min'_mem (gapPrefixDiffSet g target) (by
      obtain ⟨k⟩ : Nonempty (Fin r) := Fin.pos_iff_nonempty.mp (NeZero.pos r)
      exact ⟨gapPrefixDiff g target k,
        Finset.mem_image.mpr ⟨k, Finset.mem_univ _, rfl⟩⟩)
    rcases Finset.mem_image.mp hm with ⟨j, _, hj⟩
    exact ⟨j, by simpa [gapPrefixDiffMin] using hj⟩
  obtain ⟨j, hj⟩ := hmin_exists
  have hvariation := gapPrefixDiff_variation_le g target total i j
  rw [hj] at hvariation
  change Int.toNat
    (gapPrefixDiff g target i - gapPrefixDiffMin g target) ≤ gapMass g
  have hnonneg : 0 ≤ gapPrefixDiff g target i - gapPrefixDiffMin g target := by omega
  have hcast :
      ((Int.toNat (gapPrefixDiff g target i - gapPrefixDiffMin g target) : ℕ) : ℤ) =
        gapPrefixDiff g target i - gapPrefixDiffMin g target :=
    Int.toNat_of_nonneg hnonneg
  have hle :
      (Int.toNat (gapPrefixDiff g target i - gapPrefixDiffMin g target) : ℤ) ≤
        (gapMass g : ℤ) := by
    rw [hcast]
    exact hvariation
  exact_mod_cast hle

theorem normalizedGapFlow_has_zero (g target : Gaps r) :
    ∃ i, normalizedGapFlow g target i = 0 := by
  have hm := Finset.min'_mem (gapPrefixDiffSet g target) (by
    obtain ⟨k⟩ : Nonempty (Fin r) := Fin.pos_iff_nonempty.mp (NeZero.pos r)
    exact ⟨gapPrefixDiff g target k,
      Finset.mem_image.mpr ⟨k, Finset.mem_univ _, rfl⟩⟩)
  rcases Finset.mem_image.mp hm with ⟨i, _, hi⟩
  refine ⟨i, ?_⟩
  simp [normalizedGapFlow, gapPrefixDiffMin, hi]

private theorem gapPrefixDiff_step (g target : Gaps r)
    (total : gapMass g = gapMass target) (i : Fin r) :
    gapPrefixDiff g target i -
        gapPrefixDiff g target (previousGap i) =
      (g i : ℤ) - target i := by
  by_cases hi : i.val = 0
  · have hiEq : i = ⟨0, NeZero.pos r⟩ := Fin.ext hi
    subst i
    have hprev : (previousGap ⟨0, NeZero.pos r⟩).val + 1 = r := by
      simp [previousGap]
      have hr := NeZero.pos r
      omega
    have hfirstG : gapPrefix g 1 = g ⟨0, NeZero.pos r⟩ := by
      rw [gapPrefix_succ, gapPrefix_zero]
      have hidx : (⟨0 % r, Nat.mod_lt _ (NeZero.pos r)⟩ : Fin r) =
          ⟨0, NeZero.pos r⟩ := Fin.ext (by simp)
      rw [hidx]
      simp
    have hfirstT : gapPrefix target 1 = target ⟨0, NeZero.pos r⟩ := by
      rw [gapPrefix_succ, gapPrefix_zero]
      have hidx : (⟨0 % r, Nat.mod_lt _ (NeZero.pos r)⟩ : Fin r) =
          ⟨0, NeZero.pos r⟩ := Fin.ext (by simp)
      rw [hidx]
      simp
    have hlastG : gapPrefix g r = gapMass g := rfl
    have hlastT : gapPrefix target r = gapMass target := rfl
    have hprevDiff :
        gapPrefixDiff g target (previousGap ⟨0, NeZero.pos r⟩) = 0 := by
      unfold gapPrefixDiff
      rw [hprev, hlastG, hlastT, total]
      simp
    have hcurrent : gapPrefixDiff g target ⟨0, NeZero.pos r⟩ =
        (g ⟨0, NeZero.pos r⟩ : ℤ) - target ⟨0, NeZero.pos r⟩ := by
      unfold gapPrefixDiff
      rw [hfirstG, hfirstT]
    rw [hcurrent, hprevDiff]
    ring
  · have hpos : 0 < i.val := Nat.pos_of_ne_zero hi
    have hprev : (previousGap i).val + 1 = i.val := by
      simp [previousGap, hi]
      omega
    have hstepG : gapPrefix g (i.val + 1) = gapPrefix g i.val + g i := by
      rw [gapPrefix_succ]
      have hidx : (⟨i.val % r, Nat.mod_lt _ (NeZero.pos r)⟩ : Fin r) = i :=
        Fin.ext (Nat.mod_eq_of_lt i.isLt)
      rw [hidx]
    have hstepT : gapPrefix target (i.val + 1) =
        gapPrefix target i.val + target i := by
      rw [gapPrefix_succ]
      have hidx : (⟨i.val % r, Nat.mod_lt _ (NeZero.pos r)⟩ : Fin r) = i :=
        Fin.ext (Nat.mod_eq_of_lt i.isLt)
      rw [hidx]
    unfold gapPrefixDiff
    rw [hstepG, hstepT, hprev]
    push_cast
    ring

theorem normalizedGapFlow_balance_int (g target : Gaps r)
    (total : gapMass g = gapMass target) (i : Fin r) :
    (target i : ℤ) + normalizedGapFlow g target i =
      (g i : ℤ) + normalizedGapFlow g target (previousGap i) := by
  rw [normalizedGapFlow_int, normalizedGapFlow_int]
  have hstep := gapPrefixDiff_step g target total i
  linear_combination hstep

/-- The normalized prefix-difference flow has bounded nonnegative edge
weights, a zero edge, and exactly the conservation equation needed to move
the initial gap vector to the target gap vector. -/
theorem gapFlow_exists_normalized (g target : Gaps r)
    (total : gapMass g = gapMass target) :
    ∃ flow : Gaps r,
      (∀ i, flow i ≤ gapMass g) ∧
      (∃ i, flow i = 0) ∧
      (∀ i, flow i + target i = g i + flow (previousGap i)) := by
  refine ⟨normalizedGapFlow g target,
    ?_, normalizedGapFlow_has_zero g target, ?_⟩
  · intro i
    exact normalizedGapFlow_le_mass g target total i
  · intro i
    have h := normalizedGapFlow_balance_int g target total i
    have hnat : target i + normalizedGapFlow g target i =
        g i + normalizedGapFlow g target (previousGap i) := by
      exact_mod_cast h
    simpa [Nat.add_comm] using hnat

end FusionLogCompression
