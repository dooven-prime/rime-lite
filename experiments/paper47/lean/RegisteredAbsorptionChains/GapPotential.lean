import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- Gaps following each block in a fixed oriented cyclic block order. -/
abbrev Gaps (r : ℕ) := Fin r → ℕ

/-- The paper's excess-hole measure relative to the target gaps. -/
def gapPotential {r : ℕ} (h g : Gaps r) : ℕ :=
  ∑ i : Fin r, (h i - g i)

/-- The net gap update of a complete route from `e` to `f`. -/
def transferHole {r : ℕ} (h : Gaps r) (e f : Fin r) : Gaps r :=
  Function.update (Function.update h e (h e - 1)) f (h f + 1)

theorem transferHole_preserves_total {r : ℕ} (h : Gaps r) (e f : Fin r)
    (hef : e ≠ f) (positive : 0 < h e) :
    (∑ i : Fin r, transferHole h e f i) = ∑ i : Fin r, h i := by
  classical
  unfold transferHole
  rw [Finset.sum_update_of_mem (Finset.mem_univ f)]
  rw [Finset.sdiff_singleton_eq_erase]
  have heMem : e ∈ Finset.univ.erase f := by simpa using hef
  rw [Finset.sum_update_of_mem heMem]
  rw [Finset.sdiff_singleton_eq_erase]
  have heSum := Finset.sum_erase_add (Finset.univ.erase f) h heMem
  have hfSum := Finset.sum_erase_add Finset.univ h (Finset.mem_univ f)
  omega

theorem transferHole_potential_drop {r : ℕ} (h g : Gaps r) (e f : Fin r)
    (hef : e ≠ f) (he : g e < h e) (hf : h f < g f) :
    gapPotential (transferHole h e f) g + 1 = gapPotential h g := by
  classical
  let base : Fin r → ℕ := fun i => h i - g i
  have hpoint : (fun i => transferHole h e f i - g i) =
      Function.update base e (base e - 1) := by
    funext i
    by_cases hie : i = e
    · subst i
      simp [transferHole, base, Function.update_self,
        Function.update_of_ne, hef]
      omega
    by_cases hif : i = f
    · subst i
      simp [transferHole, base, Function.update_self,
        Function.update_of_ne, hie]
      omega
    · simp [transferHole, base, Function.update_of_ne, hie, hif]
  change (∑ i : Fin r, (transferHole h e f i - g i)) + 1 =
    ∑ i : Fin r, (h i - g i)
  rw [hpoint, Finset.sum_update_of_mem (Finset.mem_univ e)]
  have hsum := Finset.sum_erase_add Finset.univ base (Finset.mem_univ e)
  change (∑ i ∈ Finset.univ.erase e, base i) + base e =
    ∑ i : Fin r, (h i - g i) at hsum
  dsimp [base] at *
  rw [Finset.sdiff_singleton_eq_erase]
  omega

theorem exists_gap_deficit {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) : ∃ i : Fin r, h i < g i := by
  by_contra absent
  push Not at absent
  have strict : ∃ i : Fin r, g i < h i := by
    by_contra noStrict
    push Not at noStrict
    apply different
    funext i
    exact Nat.le_antisymm (noStrict i) (absent i)
  obtain ⟨i, hi⟩ := strict
  have hlt : (∑ j : Fin r, g j) < ∑ j : Fin r, h j :=
    Finset.sum_lt_sum (fun j _ => absent j) ⟨i, Finset.mem_univ i, hi⟩
  omega

theorem exists_gap_excess {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) : ∃ i : Fin r, g i < h i := by
  have reverse : g ≠ h := Ne.symm different
  exact exists_gap_deficit g h total.symm reverse

theorem transferHole_potential_lt {r : ℕ} (h g : Gaps r) (e f : Fin r)
    (hef : e ≠ f) (he : g e < h e) (hf : h f < g f) :
    gapPotential (transferHole h e f) g < gapPotential h g := by
  have drop := transferHole_potential_drop h g e f hef he hf
  omega

def firstExcess {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) : Fin r :=
  (Finset.univ.filter (fun i => g i < h i)).min' (by
    obtain ⟨i, hi⟩ := exists_gap_excess h g total different
    exact ⟨i, by simp [hi]⟩)

theorem firstExcess_spec {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) :
    g (firstExcess h g total different) < h (firstExcess h g total different) := by
  have hm := Finset.min'_mem (Finset.univ.filter (fun i => g i < h i))
    (by obtain ⟨i, hi⟩ := exists_gap_excess h g total different
        exact ⟨i, by simp [hi]⟩)
  simpa [firstExcess] using hm

def firstDeficit {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) : Fin r :=
  (Finset.univ.filter (fun i => h i < g i)).min' (by
    obtain ⟨i, hi⟩ := exists_gap_deficit h g total different
    exact ⟨i, by simp [hi]⟩)

theorem firstDeficit_spec {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i)
    (different : h ≠ g) :
    h (firstDeficit h g total different) < g (firstDeficit h g total different) := by
  have hm := Finset.min'_mem (Finset.univ.filter (fun i => h i < g i))
    (by obtain ⟨i, hi⟩ := exists_gap_deficit h g total different
        exact ⟨i, by simp [hi]⟩)
  simpa [firstDeficit] using hm

/-- Repeated net transfers terminate; cyclic local-word realization is separate. -/
def balanceTransfers {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i) :
    List (Fin r × Fin r) := by
  by_cases hd : h = g
  · exact []
  · let e := firstExcess h g total hd
    let f := firstDeficit h g total hd
    have he : g e < h e := firstExcess_spec h g total hd
    have hf : h f < g f := firstDeficit_spec h g total hd
    have hef : e ≠ f := by
      intro eq
      have he' : g f < h f := by simpa [eq] using he
      omega
    have positive : 0 < h e := by omega
    have nextTotal :
        (∑ i : Fin r, transferHole h e f i) = ∑ i : Fin r, g i := by
      rw [transferHole_preserves_total h e f hef positive]
      exact total
    exact (e, f) :: balanceTransfers (transferHole h e f) g nextTotal
termination_by gapPotential h g
decreasing_by
  exact transferHole_potential_lt h g e f hef he hf

def applyTransfers {r : ℕ} (h : Gaps r) :
    List (Fin r × Fin r) → Gaps r
  | [] => h
  | (e, f) :: rest => applyTransfers (transferHole h e f) rest

theorem balanceTransfers_correct {r : ℕ} (h g : Gaps r)
    (total : (∑ i : Fin r, h i) = ∑ i : Fin r, g i) :
    applyTransfers h (balanceTransfers h g total) = g := by
  by_cases hd : h = g
  · subst g
    simp [balanceTransfers, applyTransfers]
  · let e := firstExcess h g total hd
    let f := firstDeficit h g total hd
    have he : g e < h e := firstExcess_spec h g total hd
    have hf : h f < g f := firstDeficit_spec h g total hd
    have hef : e ≠ f := by
      intro eq
      have he' : g f < h f := by simpa [eq] using he
      omega
    have positive : 0 < h e := by omega
    have nextTotal :
        (∑ i : Fin r, transferHole h e f i) = ∑ i : Fin r, g i := by
      rw [transferHole_preserves_total h e f hef positive]
      exact total
    rw [balanceTransfers]
    simp only [dif_neg hd]
    change applyTransfers (transferHole h e f)
      (balanceTransfers (transferHole h e f) g nextTotal) = g
    exact balanceTransfers_correct (transferHole h e f) g nextTotal
termination_by gapPotential h g
decreasing_by
  exact transferHole_potential_lt h g e f hef he hf

end RegisteredAbsorptionChains
