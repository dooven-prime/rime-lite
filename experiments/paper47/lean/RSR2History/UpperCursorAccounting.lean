import RSR2History.ReservedInvariant

/-!
Tree-shape-independent gap debt and scalar cursor payments. This module
does not assert the full guarded replay or its lower-extraction coupling.
-/
namespace RSR2History

def UpperFusionTree.leftGapDebt : UpperFusionTree n → Nat
  | .leaf _ _ => 0
  | .merge A B => A.leftGapDebt + B.leftGapDebt + (A.leaves.length - 1)

def UpperFusionTree.leftBranchDefect : UpperFusionTree n → Nat
  | .leaf _ _ => 0
  | .merge A B => A.leftBranchDefect + B.leftBranchDefect +
      A.leaves.length * (B.leaves.length - 1)

theorem UpperFusionTree.leaves_length_pos (T : UpperFusionTree n) :
    1 ≤ T.leaves.length := by
  induction T with
  | leaf => simp [leaves]
  | merge A B ihA ihB => simp only [leaves, List.length_append]; omega

private theorem twice_choose_two (k : Nat) :
    2 * k.choose 2 = k * (k - 1) := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self k
  rw [Nat.choose_two_right]
  omega

private theorem add_choose_two (a b : Nat) (ha : 1 ≤ a) (hb : 1 ≤ b) :
    (a + b).choose 2 = a.choose 2 + b.choose 2 + a * b := by
  have h1 := twice_choose_two a
  have h2 := twice_choose_two b
  have h3 := twice_choose_two (a + b)
  have h4 := Nat.sub_add_cancel ha
  have h5 := Nat.sub_add_cancel hb
  have h6 := Nat.sub_add_cancel (show 1 ≤ a + b by omega)
  nlinarith

theorem UpperFusionTree.gapDebt_add_defect (T : UpperFusionTree n) :
    T.leftGapDebt + T.leftBranchDefect = (T.leaves.length - 1).choose 2 := by
  have aux : ∀ T : UpperFusionTree n,
      T.leftGapDebt + T.leftBranchDefect + (T.leaves.length - 1) =
        T.leaves.length.choose 2 := by
    intro T
    induction T with
    | leaf => simp [leftGapDebt, leftBranchDefect, leaves]
    | merge A B ihA ihB =>
        have ha := A.leaves_length_pos
        have hb := B.leaves_length_pos
        have hc := add_choose_two A.leaves.length B.leaves.length ha hb
        have hpa := Nat.sub_add_cancel ha
        have hpb := Nat.sub_add_cancel hb
        have hpab := Nat.sub_add_cancel (show 1 ≤ A.leaves.length + B.leaves.length by omega)
        simp only [leftGapDebt, leftBranchDefect, leaves, List.length_append]
        nlinarith
  have hp := T.leaves_length_pos
  have h := Nat.choose_succ_succ (T.leaves.length - 1) 1
  simp only [Nat.succ_eq_add_one, Nat.sub_add_cancel hp, Nat.choose_one_right] at h
  change T.leaves.length.choose 2 =
    (T.leaves.length - 1) + (T.leaves.length - 1).choose 2 at h
  have he := aux T
  omega

theorem UpperFusionTree.gapDebt_le (T : UpperFusionTree n) :
    T.leftGapDebt ≤ (T.leaves.length - 1).choose 2 := by
  have h := T.gapDebt_add_defect
  omega

theorem UpperFusionTree.leaves_eq_first_cons (T : UpperFusionTree n) :
    ∃ tail, T.leaves = T.firstLeaf :: tail := by
  induction T with
  | leaf => exact ⟨[], rfl⟩
  | merge A B ihA _ =>
      obtain ⟨tail, he⟩ := ihA
      exact ⟨tail ++ B.leaves, by simp [leaves, firstLeaf, he]⟩

private theorem idxOf_middle (pre tail : List Nat) (x : Nat)
    (h : (pre ++ x :: tail).Nodup) :
    (pre ++ x :: tail).idxOf x = pre.length := by
  have hx : x ∉ pre := by
    intro hx
    exact (List.nodup_append.mp h).2.2 x hx x (by simp) rfl
  simp [List.idxOf_append, hx]

/-- An ordered merge's anchor gap is the full left-subtree leaf count. -/
theorem UpperFusionTree.Subtree.anchor_gap {A B T : UpperFusionTree n}
    (h : (UpperFusionTree.merge A B).Subtree T) (hnd : T.leaves.Nodup) :
    T.leaves.idxOf B.firstLeaf = T.leaves.idxOf A.firstLeaf + A.leaves.length := by
  obtain ⟨pre, post, he⟩ := h.leaf_interval
  obtain ⟨as, ha⟩ := A.leaves_eq_first_cons
  obtain ⟨bs, hb⟩ := B.leaves_eq_first_cons
  have hA : T.leaves = pre ++ A.firstLeaf :: (as ++ B.leaves ++ post) := by
    simpa [leaves, ha, List.append_assoc] using he
  have hB : T.leaves = (pre ++ A.leaves) ++ B.firstLeaf :: (bs ++ post) := by
    simpa [leaves, hb, List.append_assoc] using he
  have hiA : T.leaves.idxOf A.firstLeaf = pre.length := by
    rw [hA] at hnd ⊢
    exact idxOf_middle _ _ _ hnd
  have hiB : T.leaves.idxOf B.firstLeaf = (pre ++ A.leaves).length := by
    rw [hB] at hnd ⊢
    exact idxOf_middle _ _ _ hnd
  simpa [hiA, List.length_append] using hiB

/-- The first merge on the leftmost leaf's ancestry has a singleton left child. -/
theorem UpperFusionTree.leftmost_singleton_merge (T : UpperFusionTree n)
    (h : 2 ≤ T.leaves.length) :
    ∃ packet R, (UpperFusionTree.merge (.leaf T.firstLeaf packet) R).Subtree T := by
  induction T with
  | leaf => simp [leaves] at h
  | merge A B ihA _ =>
      cases A with
      | leaf i packet => exact ⟨packet, B, .refl _⟩
      | merge L R =>
          have hL := L.leaves_length_pos
          have hR := R.leaves_length_pos
          obtain ⟨packet, tree, ht⟩ := ihA (by simp only [leaves, List.length_append]; omega)
          exact ⟨packet, tree, .left ht⟩

def cursorTurn (n c target : Nat) : Nat :=
  if target ≤ c then c - target else c + n - target

def cursorWinding (c target : Nat) : Nat := if c < target then 1 else 0

theorem cursorTurn_payment (_hc : c < n) (ht : target < n) :
    cursorTurn n c target + target = c + n * cursorWinding c target := by
  unfold cursorTurn cursorWinding
  split_ifs <;> omega

theorem cursorTurn_eq_zmod_val [NeZero n] (hc : c < n) (ht : target < n) :
    cursorTurn n c target = ((c : ZMod n) - (target : ZMod n)).val := by
  by_cases htc : target ≤ c
  · simp only [cursorTurn, if_pos htc]
    symm
    have hv : (target : ZMod n).val ≤ (c : ZMod n).val := by
      simpa [ZMod.val_natCast_of_lt hc, ZMod.val_natCast_of_lt ht] using htc
    simpa [ZMod.val_natCast_of_lt hc, ZMod.val_natCast_of_lt ht] using ZMod.val_sub hv
  · have hsmall : c + n - target < n := by omega
    have hle : target ≤ c + n := by omega
    have hcast : ((c + n - target : Nat) : ZMod n) =
        (c : ZMod n) - (target : ZMod n) := by
      rw [Nat.cast_sub hle]
      simp
    rw [cursorTurn, if_neg htc, ← hcast, ZMod.val_natCast_of_lt hsmall]

theorem transfer_cursor_payment (hc : c < n) (hj : j < n) :
    (cursorTurn n c j + 1) + j = c + 1 + n * cursorWinding c j := by
  have h := cursorTurn_payment hc hj
  omega

theorem fusion_cursor_payment (hc : c < n) (haf : a + f < n) :
    (cursorTurn n c (a + f) + 2 * f + 1) + a =
      c + (f + 1) + n * cursorWinding c (a + f) := by
  have h := cursorTurn_payment hc haf
  omega

theorem cursorWinding_zero_target (c : Nat) : cursorWinding c 0 = 0 := by
  simp [cursorWinding]

theorem singleton_upper_budget_identity (hn : 2 ≤ n) :
    2 * n - 1 + (n - 1).choose 2 + n * (2 * n - 3) = 5 * n.choose 2 := by
  have h1 := twice_choose_two n
  have h2 := twice_choose_two (n - 1)
  have hp := Nat.sub_add_cancel (show 1 ≤ n by omega)
  have hpp := Nat.sub_add_cancel (show 1 ≤ n - 1 by omega)
  have h3 := Nat.sub_add_cancel (show 3 ≤ 2 * n by omega)
  have h4 := Nat.sub_add_cancel (show 1 ≤ 2 * n by omega)
  nlinarith

/-- The dynamic winding-count premises are explicit; no replay is hidden here. -/
theorem singleton_cursor_budget (hn : 2 ≤ n) (hj : j < n)
    (hD : D ≤ (n - 1).choose 2)
    (hW0 : j = 0 → W ≤ 2 * n - 3)
    (hWpos : 0 < j → W ≤ 2 * n - 4) :
    2 * n - 1 + D + n * W + j ≤ 5 * n.choose 2 := by
  rw [← singleton_upper_budget_identity hn]
  by_cases hj0 : j = 0
  · have hmul := Nat.mul_le_mul_left n (hW0 hj0)
    omega
  · have hmul := Nat.mul_le_mul_left n (hWpos (by omega))
    have h4 := Nat.sub_add_cancel (show 4 ≤ 2 * n by omega)
    have h3 := Nat.sub_add_cancel (show 3 ≤ 2 * n by omega)
    nlinarith

end RSR2History
