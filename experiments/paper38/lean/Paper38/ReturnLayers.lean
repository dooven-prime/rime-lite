import Mathlib.Algebra.Group.Pointwise.Finset.Basic
import Mathlib.Algebra.Group.Subgroup.Lattice

/-!
# Positive layers with a retained initial factor

The index n counts additional factors after the first, so it represents
n + 1 charged returns. These definitions describe algebraic layers only;
concrete guarded-path soundness and realization are not asserted here.
-/

namespace Rime.Paper38

open scoped Pointwise

variable {G : Type*} [Group G] [DecidableEq G]

def exactLayer (A B : Finset G) : Nat → Finset G
  | 0 => B
  | n + 1 => A * exactLayer A B n

def cumulativeLayer (A B : Finset G) : Nat → Finset G
  | 0 => B
  | n + 1 => cumulativeLayer A B n ∪ A * cumulativeLayer A B n

theorem exactLayer_eq_power (A B : Finset G) (n : Nat) :
    exactLayer A B n = A ^ n * B := by
  induction n with
  | zero => simp [exactLayer]
  | succ n ih => rw [exactLayer, ih, pow_succ', mul_assoc]

theorem mem_exactLayer_iff_product_word (A B : Finset G) (n : Nat) (x : G) :
    x ∈ exactLayer A B n ↔
      ∃ word : List G, word.length = n ∧
        (∀ a ∈ word, a ∈ A) ∧ ∃ b ∈ B, x = word.prod * b := by
  induction n generalizing x with
  | zero =>
      constructor
      · intro hx
        exact ⟨[], rfl, by simp, x, hx, by simp⟩
      · rintro ⟨word, hlen, _, b, hb, hprod⟩
        have hnil : word = [] := by simpa using hlen
        subst word
        simpa [exactLayer, hprod] using hb
  | succ n ih =>
      constructor
      · intro hx
        obtain ⟨a, ha, y, hy, rfl⟩ := Finset.mem_mul.mp hx
        obtain ⟨word, hlen, hword, b, hb, hprod⟩ := (ih y).mp hy
        refine ⟨a :: word, by simp [hlen], ?_, b, hb, ?_⟩
        · intro z hz
          rcases List.mem_cons.mp hz with rfl | hz
          · exact ha
          · exact hword z hz
        · simp [hprod, mul_assoc]
      · rintro ⟨word, hlen, hword, b, hb, hprod⟩
        cases word with
        | nil => simp at hlen
        | cons a rest =>
            have hrest : rest.length = n := by simpa using hlen
            have hmem : rest.prod * b ∈ exactLayer A B n :=
              (ih _).mpr ⟨rest, hrest, fun z hz => hword z (List.mem_cons_of_mem a hz),
                b, hb, rfl⟩
            rw [exactLayer]
            apply Finset.mem_mul.mpr
            refine ⟨a, hword a (by simp), rest.prod * b, hmem, ?_⟩
            simpa [List.prod_cons, mul_assoc] using hprod.symm

theorem mem_cumulativeLayer_iff (A B : Finset G) (n : Nat) (x : G) :
    x ∈ cumulativeLayer A B n ↔ ∃ k ≤ n, x ∈ exactLayer A B k := by
  induction n generalizing x with
  | zero => simp [cumulativeLayer, exactLayer]
  | succ n ih =>
      constructor
      · intro hx
        rcases Finset.mem_union.mp hx with hx | hx
        · obtain ⟨k, hk, hx⟩ := (ih x).mp hx
          exact ⟨k, Nat.le.step hk, hx⟩
        · obtain ⟨a, ha, y, hy, rfl⟩ := Finset.mem_mul.mp hx
          obtain ⟨k, hk, hy⟩ := (ih y).mp hy
          exact ⟨k + 1, Nat.succ_le_succ hk, Finset.mem_mul.mpr ⟨a, ha, y, hy, rfl⟩⟩
      · rintro ⟨k, hk, hx⟩
        by_cases hkn : k ≤ n
        · exact Finset.mem_union_left _ ((ih x).mpr ⟨k, hkn, hx⟩)
        · have hkeq : k = n + 1 := by omega
          rw [hkeq, exactLayer] at hx
          obtain ⟨a, ha, y, hy, rfl⟩ := Finset.mem_mul.mp hx
          exact Finset.mem_union_right _
            (Finset.mem_mul.mpr ⟨a, ha, y, (ih y).mpr ⟨n, le_rfl, hy⟩, rfl⟩)

theorem cumulativeLayer_eq_union (A B : Finset G) (n : Nat) :
    cumulativeLayer A B n = (Finset.range (n + 1)).biUnion (fun k => A ^ k * B) := by
  ext x
  simp [mem_cumulativeLayer_iff, exactLayer_eq_power, Nat.lt_succ_iff]

theorem cumulativeLayer_mono (A B : Finset G) : Monotone (cumulativeLayer A B) := by
  intro n m hnm x hx
  obtain ⟨k, hk, hx⟩ := (mem_cumulativeLayer_iff A B n x).mp hx
  exact (mem_cumulativeLayer_iff A B m x).mpr ⟨k, hk.trans hnm, hx⟩

theorem cumulativeLayer_nonempty (A B : Finset G) (hB : B.Nonempty) (n : Nat) :
    (cumulativeLayer A B n).Nonempty :=
  hB.mono (cumulativeLayer_mono A B (Nat.zero_le n))

def LeftStable (H : Subgroup G) (S : Finset G) : Prop :=
  ∀ h ∈ H, ∀ x ∈ S, h * x ∈ S

theorem cumulativeLayer_leftStable (H : Subgroup G) (A B : Finset G)
    (hA : LeftStable H A) (hB : LeftStable H B) (n : Nat) :
    LeftStable H (cumulativeLayer A B n) := by
  induction n with
  | zero => exact hB
  | succ n ih =>
      intro h hh x hx
      rcases Finset.mem_union.mp hx with hx | hx
      · exact Finset.mem_union_left _ (ih h hh x hx)
      · obtain ⟨a, ha, y, hy, rfl⟩ := Finset.mem_mul.mp hx
        apply Finset.mem_union_right
        exact Finset.mem_mul.mpr ⟨h * a, hA h hh a ha, y, hy, mul_assoc _ _ _⟩

end Rime.Paper38
