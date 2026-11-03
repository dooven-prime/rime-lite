import Mathlib.Data.ZMod.Basic

namespace RegisteredAbsorptionChains

variable {n : ℕ} {α : Type*} [NeZero n] [DecidableEq α]

/-- A finite circular placement, with `none` denoting a hole. -/
abbrev Placement (n : ℕ) (α : Type*) := ZMod n → Option α

/-- The chronological action of `p^j` shifts packet positions by `j`. -/
def rotate (j : ZMod n) (s : Placement n α) : Placement n α :=
  fun q => s (q - j)

/-- The nonfusion branch of `d`; a collision is deliberately undefined. -/
def defect (s : Placement n α) : Option (Placement n α) :=
  if s 0 ≠ none ∧ s 1 ≠ none then none else
    some (fun q => if q = 0 then (s 0).orElse fun _ => s 1
      else if q = 1 then none else s q)

/-- Execute the chronological word `p^(-j) d p^j`. -/
def localWord (j : ZMod n) (s : Placement n α) : Option (Placement n α) :=
  (defect (rotate (-j) s)).map (rotate j)

/-- The expected hole transfer from `j+1` to `j`. -/
def moveBack (j : ZMod n) (s : Placement n α) : Placement n α :=
  fun q => if q = j then s (j + 1) else if q = j + 1 then none else s q

omit [NeZero n] [DecidableEq α] in
theorem rotate_to_zero (j : ZMod n) (s : Placement n α) :
    rotate (-j) s 0 = s j := by
  simp [rotate]

omit [NeZero n] [DecidableEq α] in
theorem rotate_to_one (j : ZMod n) (s : Placement n α) :
    rotate (-j) s 1 = s (j + 1) := by
  simp [rotate, add_comm]

omit [NeZero n] [DecidableEq α] in
theorem localWord_moves_into_hole (j : ZMod n) (s : Placement n α)
    (hn : 2 ≤ n) (hj : s j = none) :
    localWord j s = some (moveBack j s) := by
  have hone : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  have h0 : rotate (-j) s 0 = none := by simpa [rotate_to_zero] using hj
  unfold localWord defect
  simp only [h0, ne_eq, not_true_eq_false, false_and, ite_false, Option.map_some]
  congr 1
  funext q
  by_cases hq0 : q = j
  · subst q
    simp [rotate, moveBack, add_comm]
  by_cases hq1 : q = j + 1
  · subst q
    simp [rotate, moveBack, hq0, hone]
  · have hsub0 : q - j ≠ 0 := by
      intro h
      exact hq0 (sub_eq_zero.mp h)
    have hsub1 : q - j ≠ 1 := by
      intro h
      apply hq1
      have hh := congrArg (fun x : ZMod n => x + j) h
      simpa [sub_add_cancel, add_comm] using hh
    simp [rotate, moveBack, hq0, hq1, hsub0, hsub1]

end RegisteredAbsorptionChains
