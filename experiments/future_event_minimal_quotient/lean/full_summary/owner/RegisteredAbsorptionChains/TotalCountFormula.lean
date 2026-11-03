import RegisteredAbsorptionChains.FinitePositiveFiber
import RegisteredAbsorptionChains.CodeLastCheckpointCount
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

private theorem two_le_of_three {n : ℕ} [Fact (3 ≤ n)] : 2 ≤ n := by
  have hn : 3 ≤ n := Fact.out
  omega

/-- The actual decoded outside size is exactly the length left after the
last nonzero symbolic checkpoint. -/
theorem decodeCode_remaining_eq_lastCheckpoint
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n) :
    (decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo =
      (n - 2) - codeLastCheckpoint (n - 2) c := by
  have hbalance := (decodeCode c hn).frontier.remaining_plus_absorbed
  rw [(decodeCode c hn).frontier.remaining_card,
    decodeCode_absorbed_eq_codeLastCheckpoint] at hbalance
  omega

/-- All code-indexed actual placement fibers have a uniform expression in
the final checkpoint, including the full-carrier case. -/
theorem card_actualFixedChainPlacements_lastCheckpoint
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n) :
    Fintype.card (ActualFixedChainPlacements c hn) =
      n * (2 * (n - 2) - codeLastCheckpoint (n - 2) c).choose
        ((n - 2) - codeLastCheckpoint (n - 2) c) := by
  classical
  let k := (decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo
  let b := codeLastCheckpoint (n - 2) c
  have hk : k = (n - 2) - b :=
    decodeCode_remaining_eq_lastCheckpoint c hn
  have hb : b ≤ n - 2 := by
    have h := (decodeCode c hn).frontier.remaining_plus_absorbed
    rw [(decodeCode c hn).frontier.remaining_card,
      decodeCode_absorbed_eq_codeLastCheckpoint] at h
    dsimp [b]
    omega
  have htop : n + k - 2 = 2 * (n - 2) - b := by
    have hn3 : 2 ≤ n := hn
    omega
  by_cases hpositive : (decodeCode c hn).frontier.lo <
      (decodeCode c hn).frontier.hi
  · rw [card_actualFixedChainPlacements_positive c hn hpositive]
    change n * (n + k - 2).choose k = _
    rw [htop, hk]
  · have hempty : (decodeCode c hn).frontier.lo =
        (decodeCode c hn).frontier.hi := by
      have hle := (decodeCode c hn).frontier.noncrossing
      omega
    rw [card_actualFixedChainPlacements_full c hn hempty]
    have hkzero : (n - 2) - b = 0 := by
      have hk' : k = 0 := by simp [k, hempty]
      omega
    rw [hkzero]
    simp

/-- Closed count for generated complete summaries when `n ≥ 3`.
The code-sum premise uses `actualSummaryFiniteParamsEquiv`, whose assembly
depends on `actual_registered_origin_unique`; thus the passage from
placement fibers to complete records does not omit the origin read.
The two-origin `n=2` case is separate. -/
theorem card_actualRegisteredSummaries_closed
    {n : ℕ} [NeZero n] [Fact (3 ≤ n)] :
    Fintype.card (ActualRegisteredSummaries n) =
      n * ((2 * (n - 2)).choose (n - 2) +
        2 * ∑ b : Fin (n - 2),
          3 ^ b.1 * (2 * (n - 2) - (b.1 + 1)).choose
            ((n - 2) - (b.1 + 1))) := by
  classical
  have hsum :
      Fintype.card (ActualRegisteredSummaries n) =
        ∑ c : Code (n - 2),
          n * (2 * (n - 2) - codeLastCheckpoint (n - 2) c).choose
            ((n - 2) - codeLastCheckpoint (n - 2) c) := by
    rw [card_actualRegisteredSummaries_code_sum]
    apply Finset.sum_congr rfl
    intro c _
    by_cases hpositive :
        (decodeCode c two_le_of_three).frontier.lo <
          (decodeCode c two_le_of_three).frontier.hi
    · simp only [if_pos hpositive]
      rw [← card_actualFixedChainPlacements_positive c two_le_of_three hpositive]
      exact card_actualFixedChainPlacements_lastCheckpoint c two_le_of_three
    · simp only [if_neg hpositive]
      have hempty : (decodeCode c two_le_of_three).frontier.lo =
          (decodeCode c two_le_of_three).frontier.hi := by
        have hle := (decodeCode c two_le_of_three).frontier.noncrossing
        omega
      have hcard := card_actualFixedChainPlacements_lastCheckpoint c two_le_of_three
      rw [card_actualFixedChainPlacements_full c two_le_of_three hempty] at hcard
      exact hcard
  have hweighted := codeLastCheckpoint_weighted_sum (n - 2)
    (fun b => n * (2 * (n - 2) - b).choose ((n - 2) - b))
  rw [hsum, hweighted]
  simp only [Nat.sub_zero]
  rw [mul_add]
  congr 1
  simp only [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro b _
  ring

end RegisteredAbsorptionChains
