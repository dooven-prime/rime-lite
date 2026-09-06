import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith

/-!
# Paper XXV: scalar-margin consequences

This file formalizes the exact order-theoretic part of the margin policy. Its
input is the certified scalar error statement `|n' - n| <= b`; no numerical
approximation or zero substitution is used.
-/

namespace Rime.Paper25

def StableActive (n b threshold : ℝ) : Prop := n - b > threshold

def StableInactive (n b threshold : ℝ) : Prop := n + b ≤ threshold

def Unresolved (n b threshold : ℝ) : Prop :=
  ¬ StableActive n b threshold ∧ ¬ StableInactive n b threshold

theorem stable_active_of_error
    {n n' b threshold : ℝ}
    (herror : |n' - n| ≤ b)
    (hactive : StableActive n b threshold) :
    n' > threshold := by
  have hlow : -b ≤ n' - n := (abs_le.mp herror).1
  dsimp [StableActive] at hactive
  linarith

theorem stable_inactive_of_error
    {n n' b threshold : ℝ}
    (herror : |n' - n| ≤ b)
    (hinactive : StableInactive n b threshold) :
    n' ≤ threshold := by
  have hupp : n' - n ≤ b := (abs_le.mp herror).2
  dsimp [StableInactive] at hinactive
  linarith

theorem margin_trichotomy (n b threshold : ℝ) :
    StableActive n b threshold ∨
      StableInactive n b threshold ∨ Unresolved n b threshold := by
  by_cases hactive : StableActive n b threshold
  · exact Or.inl hactive
  · by_cases hinactive : StableInactive n b threshold
    · exact Or.inr (Or.inl hinactive)
    · exact Or.inr (Or.inr ⟨hactive, hinactive⟩)

theorem unresolved_iff_interval
    (n b threshold : ℝ) :
    Unresolved n b threshold ↔ n - b ≤ threshold ∧ threshold < n + b := by
  constructor
  · intro h
    exact ⟨le_of_not_gt h.1, lt_of_not_ge h.2⟩
  · rintro ⟨hlow, hupp⟩
    exact ⟨not_lt_of_ge hlow, not_le_of_gt hupp⟩

/-- Completeness witnesses for the unresolved scalar interval. -/
theorem unresolved_has_inactive_and_active
    {n b threshold : ℝ}
    (hn : 0 ≤ n) (_hb : 0 ≤ b) (ht : 0 ≤ threshold)
    (hunresolved : Unresolved n b threshold) :
    (∃ xminus : ℝ, 0 ≤ xminus ∧ |xminus - n| ≤ b ∧ xminus ≤ threshold) ∧
      (∃ xplus : ℝ, 0 ≤ xplus ∧ |xplus - n| ≤ b ∧ threshold < xplus) := by
  have hinterval := (unresolved_iff_interval n b threshold).mp hunresolved
  let xminus : ℝ := max 0 (n - b)
  have hxminus_nonneg : 0 ≤ xminus := by
    dsimp [xminus]
    exact le_max_left _ _
  have hxminus_lower : n - b ≤ xminus := by
    dsimp [xminus]
    exact le_max_right _ _
  have hxminus_upper : xminus ≤ n := by
    dsimp [xminus]
    exact max_le hn (by linarith)
  have hxminus_threshold : xminus ≤ threshold := by
    dsimp [xminus]
    exact max_le ht hinterval.1
  have hxminus_error : |xminus - n| ≤ b := by
    apply abs_le.mpr
    constructor <;> linarith
  have hplus_upper : threshold < n + b := hinterval.2
  let xplus : ℝ := (threshold + (n + b)) / 2
  have hxplus_nonneg : 0 ≤ xplus := by
    dsimp [xplus]
    linarith
  have hxplus_threshold : threshold < xplus := by
    dsimp [xplus]
    linarith
  have hxplus_lower : n - b ≤ xplus := by
    dsimp [xplus]
    linarith
  have hxplus_upper : xplus ≤ n + b := by
    dsimp [xplus]
    linarith
  have hxplus_error : |xplus - n| ≤ b := by
    apply abs_le.mpr
    constructor <;> linarith
  exact
    ⟨⟨xminus, hxminus_nonneg, hxminus_error, hxminus_threshold⟩,
      ⟨xplus, hxplus_nonneg, hxplus_error, hxplus_threshold⟩⟩

end Rime.Paper25
