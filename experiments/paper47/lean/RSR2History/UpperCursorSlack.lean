import RSR2History.UpperCursorAccounting

namespace RSR2History

inductive UpperFusionTree.IsLeftComb : UpperFusionTree n → Prop
  | leaf (i packet) : IsLeftComb (.leaf i packet)
  | snoc {A} (h : IsLeftComb A) (i packet) : IsLeftComb (.merge A (.leaf i packet))

theorem UpperFusionTree.leaves_length_eq_one_iff (T : UpperFusionTree n) :
    T.leaves.length = 1 ↔ ∃ i packet, T = .leaf i packet := by
  cases T with
  | leaf i packet => simp [leaves]
  | merge A B =>
      have ha := A.leaves_length_pos
      have hb := B.leaves_length_pos
      simp only [leaves, List.length_append]
      constructor
      · omega
      · rintro ⟨_, _, h⟩; cases h

theorem UpperFusionTree.defect_zero_iff_leftComb (T : UpperFusionTree n) :
    T.leftBranchDefect = 0 ↔ T.IsLeftComb := by
  induction T with
  | leaf i packet => exact ⟨fun _ => .leaf i packet, fun _ => rfl⟩
  | merge A B ihA _ =>
      constructor
      · intro h
        have ha := A.leaves_length_pos
        have hmul : A.leaves.length * (B.leaves.length - 1) = 0 := by
          simp only [leftBranchDefect] at h
          omega
        have hb : B.leaves.length = 1 := by
          have hp := B.leaves_length_pos
          rcases Nat.mul_eq_zero.mp hmul with hz | hz <;> omega
        obtain ⟨i, packet, rfl⟩ := B.leaves_length_eq_one_iff.mp hb
        exact .snoc (ihA.mp (by simpa [leftBranchDefect, leaves] using h)) i packet
      · intro h
        cases h with
        | snoc hA i packet => simp [leftBranchDefect, leaves, ihA.mpr hA]

/-- Additive form avoids truncated subtraction in the cost-slack statement. -/
theorem cursor_budget_with_defect (ht : 2 ≤ t) (hj : j < n)
    (hDE : D + E = (t - 1).choose 2)
    (hW0 : j = 0 → W ≤ 2 * t - 3)
    (hWpos : 0 < j → W ≤ 2 * t - 4) :
    (2 * t - 1 + D + n * W + j) + E + (if j = 0 then 0 else n - j) ≤
      2 * t - 1 + (t - 1).choose 2 + n * (2 * t - 3) := by
  by_cases hj0 : j = 0
  · have hm := Nat.mul_le_mul_left n (hW0 hj0)
    simp only [hj0, if_pos, add_zero]
    omega
  · have hm := Nat.mul_le_mul_left n (hWpos (by omega))
    have h3 := Nat.sub_add_cancel (show 3 ≤ 2 * t by omega)
    have h4 := Nat.sub_add_cancel (show 4 ≤ 2 * t by omega)
    have hjn := Nat.sub_add_cancel (Nat.le_of_lt hj)
    simp only [if_neg hj0]
    nlinarith

theorem singleton_cursor_budget_with_defect (hn : 2 ≤ n) (hj : j < n)
    (hDE : D + E = (n - 1).choose 2)
    (hW0 : j = 0 → W ≤ 2 * n - 3)
    (hWpos : 0 < j → W ≤ 2 * n - 4) :
    (2 * n - 1 + D + n * W + j) + E + (if j = 0 then 0 else n - j) ≤
      5 * n.choose 2 := by
  rw [← singleton_upper_budget_identity hn]
  exact cursor_budget_with_defect hn hj hDE hW0 hWpos

end RSR2History
