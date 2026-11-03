import RegisteredAbsorptionChains.CombinatorialCore
import Mathlib.Data.Fin.Tuple.Basic

namespace RegisteredAbsorptionChains

/-- A code whose final checkpoint is selected. -/
abbrev EndNonzero (b : ℕ) :=
  {c : Code (b + 1) // c (Fin.last b) ≠ none}

def endEquiv (b : ℕ) : (Code b × Side) ≃ EndNonzero b where
  toFun ps := ⟨Fin.snoc ps.1 (some ps.2), by simp [Fin.snoc_last]⟩
  invFun c := (Fin.init c.1, (c.1 (Fin.last b)).getD false)
  left_inv := by
    intro ⟨pre, side⟩
    simp [Fin.init_snoc, Fin.snoc_last]
  right_inv := by
    intro ⟨c, hc⟩
    apply Subtype.ext
    change Fin.snoc (Fin.init c) (some ((c (Fin.last b)).getD false)) = c
    have hlast : some ((c (Fin.last b)).getD false) = c (Fin.last b) := by
      cases h : c (Fin.last b) with
      | none => exact False.elim (hc h)
      | some side => simp
    rw [hlast, Fin.snoc_init_self]

noncomputable instance (b : ℕ) : Fintype (EndNonzero b) :=
  Fintype.ofEquiv (Code b × Side) (endEquiv b)

theorem card_endNonzero (b : ℕ) :
    Fintype.card (EndNonzero b) = 2 * 3 ^ b := by
  rw [← Fintype.card_congr (endEquiv b)]
  simp [Side, Nat.mul_comm]

/-- A length-`b+1+d` code whose last checkpoint is at index `b`. -/
abbrev LastAt (b d : ℕ) :=
  {c : Code (b + 1 + d) //
    c (Fin.castAdd d (Fin.last b)) ≠ none ∧
    ∀ i : Fin d, c (Fin.natAdd (b + 1) i) = none}

def lastAtEquiv (b d : ℕ) : EndNonzero b ≃ LastAt b d where
  toFun c := ⟨Fin.append c.1 (fun _ => none), by
    constructor
    · simpa using c.2
    · intro i
      simp⟩
  invFun c := ⟨fun i => c.1 (Fin.castAdd d i), c.2.1⟩
  left_inv := by
    intro c
    apply Subtype.ext
    funext i
    simp
  right_inv := by
    intro c
    apply Subtype.ext
    funext i
    refine Fin.addCases (fun j => ?_) (fun j => ?_) i
    · simp
    · simpa using (c.2.2 j).symm

noncomputable instance (b d : ℕ) : Fintype (LastAt b d) :=
  Fintype.ofEquiv (EndNonzero b) (lastAtEquiv b d)

theorem card_lastAt (b d : ℕ) :
    Fintype.card (LastAt b d) = 2 * 3 ^ b := by
  rw [← Fintype.card_congr (lastAtEquiv b d)]
  exact card_endNonzero b

end RegisteredAbsorptionChains
