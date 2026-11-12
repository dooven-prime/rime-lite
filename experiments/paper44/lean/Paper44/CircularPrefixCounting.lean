import Paper44.CircularPrefixClassification
import RegisteredAbsorptionChains.FiberParameters

/-!
# Terminal prefix-code cardinality

This file formalizes the finite combinatorial code underlying the terminal
prefix count. Its cardinality proof is separate from `TerminalLabelEquiv`,
which identifies these codes with actual generated full-carrier labels.
-/

namespace Paper44

open RegisteredAbsorptionChains

/-- A saturated terminal label: `j` checkpoints and one L/R binding each. -/
abbrev TerminalSaturated (N j : ℕ) :=
  Select N j × (Fin j → Bool)

/-- A short terminal label: its complete chain ends at checkpoint `N`. -/
abbrev TerminalShort (N j : ℕ) :=
  (ell : Fin (j - 1)) × Select (N - 1) ell.val ×
    (Fin (ell.val + 1) → Bool)

/-- The phase tag makes saturated and short retained labels disjoint. -/
abbrev TerminalPrefixCode (N j : ℕ) :=
  Sum (TerminalSaturated N j) (TerminalShort N j)

theorem card_terminalSaturated (N j : ℕ) :
    Fintype.card (TerminalSaturated N j) = 2 ^ j * N.choose j := by
  simp [TerminalSaturated, Fintype.card_prod, mul_comm]

theorem card_terminalShort (N j : ℕ) :
    Fintype.card (TerminalShort N j) =
      ∑ ell ∈ Finset.range (j - 1),
        2 ^ (ell + 1) * (N - 1).choose ell := by
  classical
  rw [Fintype.card_sigma]
  calc
    (∑ ell : Fin (j - 1),
        Fintype.card (Select (N - 1) ell.val × (Fin (ell.val + 1) → Bool))) =
      ∑ ell : Fin (j - 1),
        2 ^ (ell.val + 1) * (N - 1).choose ell.val := by
          apply Finset.sum_congr rfl
          intro ell _
          simp [Fintype.card_prod, mul_comm]
    _ = ∑ ell ∈ Finset.range (j - 1),
        2 ^ (ell + 1) * (N - 1).choose ell := by
          rw [← Fin.sum_univ_eq_sum_range]

def terminalPrefixCount (N j : ℕ) : ℕ :=
  2 ^ j * N.choose j +
    ∑ ell ∈ Finset.range (j - 1),
      2 ^ (ell + 1) * (N - 1).choose ell

theorem card_terminalPrefixCode (N j : ℕ) :
    Fintype.card (TerminalPrefixCode N j) = terminalPrefixCount N j := by
  change Fintype.card (TerminalSaturated N j ⊕ TerminalShort N j) = _
  rw [Fintype.card_sum, card_terminalSaturated, card_terminalShort]
  unfold terminalPrefixCount
  ac_rfl

/-- Reindexed form of the manuscript's terminal-prefix formula. -/
theorem terminalPrefixCount_eq_paper (N j : ℕ) :
    terminalPrefixCount N j =
      2 ^ j * N.choose j +
        ∑ ell ∈ Finset.Icc 1 (j - 1),
          2 ^ ell * (N - 1).choose (ell - 1) := by
  classical
  rw [show Finset.Icc 1 (j - 1) =
      (Finset.range (j - 1)).image Nat.succ by
        ext ell
        simp only [Finset.mem_Icc, Finset.mem_image, Finset.mem_range]
        constructor
        · rintro ⟨hlo, hhi⟩
          refine ⟨ell - 1, ?_, ?_⟩
          · omega
          · simp [Nat.sub_add_cancel (by omega : 1 ≤ ell)]
        · rintro ⟨k, hk, rfl⟩
          exact ⟨by omega, by omega⟩]
  rw [Finset.sum_image]
  · simp [terminalPrefixCount]
  · intro a ha b hb hab
    omega

/-- Exact count of the finite terminal-prefix code type, in paper notation.
`TerminalLabelEquiv.card_actualTerminalLabel_paper` transfers it to actual labels. -/
theorem card_terminalPrefixCode_paper (N j : ℕ) :
    Fintype.card (TerminalPrefixCode N j) =
      2 ^ j * N.choose j +
        ∑ ell ∈ Finset.Icc 1 (j - 1),
          2 ^ ell * (N - 1).choose (ell - 1) := by
  rw [card_terminalPrefixCode, terminalPrefixCount_eq_paper]

end Paper44
