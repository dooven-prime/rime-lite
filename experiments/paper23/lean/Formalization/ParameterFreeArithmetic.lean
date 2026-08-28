import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Ring

/-!
# Arithmetic core of the parameter-free Cerny corollary

This file formalizes only the arithmetic implication used in Theorem 5.4.
The group-action theorem `s <= floor (n/2)` and the automata-theoretic reset
bound are explicit hypotheses here; they are separate formalization targets.
-/

namespace Rime.SynchronizingAutomata

theorem parameter_free_rank_substitution
    (n s : Nat) (hs : s ≤ n / 2) :
    1 + (n - 2) * (s + 1) ≤
      1 + (n - 2) * (n / 2 + 1) := by
  exact Nat.add_le_add_left (Nat.mul_le_mul_left (n - 2) (Nat.add_le_add_right hs 1)) 1

theorem parameter_free_quadratic_arithmetic
    (n : Nat) (hn : 2 ≤ n) :
    1 + (n - 2) * (n / 2 + 1) ≤ (n - 1) ^ 2 := by
  have hnpos : 0 < n := lt_of_lt_of_le (by decide) hn
  have hhalf : n / 2 + 1 ≤ n :=
    Nat.succ_le_iff.mpr (Nat.div_lt_self hnpos (by decide))
  calc
    1 + (n - 2) * (n / 2 + 1) ≤ 1 + (n - 2) * n :=
      Nat.add_le_add_left (Nat.mul_le_mul_left (n - 2) hhalf) 1
    _ = (n - 1) ^ 2 := by
      obtain ⟨k, rfl⟩ := Nat.exists_eq_add_of_le hn
      simp
      ring

/-- Arithmetic conclusion of Theorem 5.4, conditional on its group-rank and
reset-depth inputs. -/
theorem parameter_free_cerny_arithmetic
    (n s D : Nat)
    (hn : 2 ≤ n)
    (hs : s ≤ n / 2)
    (hD : D ≤ 1 + (n - 2) * (s + 1)) :
    D ≤ 1 + (n - 2) * (n / 2 + 1) ∧
      1 + (n - 2) * (n / 2 + 1) ≤ (n - 1) ^ 2 := by
  constructor
  · exact hD.trans (parameter_free_rank_substitution n s hs)
  · exact parameter_free_quadratic_arithmetic n hn

end Rime.SynchronizingAutomata
