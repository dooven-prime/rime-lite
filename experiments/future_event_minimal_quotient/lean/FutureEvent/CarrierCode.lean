import RegisteredAbsorptionChains.ActualChainRange

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem decode_frontier_congr (c : Code (n - 2)) (hn : 2 ≤ n)
    {i j : ℕ} (hi : i ≤ n - 2) (hj : j ≤ n - 2) (h : i = j) :
    (decodeCodePrefix c hn i hi).frontier = (decodeCodePrefix c hn j hj).frontier := by
  subst j
  rfl

/-- Dense singleton checkpoints first extend the carrier right, then left.
The code is independent of all physical placement and outside-cut choices. -/
def carrierCode (a b : ℕ) : Code (n - 2) := fun i =>
  if i.val < a then some true else if i.val < a + b then some false else none

theorem carrierCode_right_prefix (a b : ℕ) (hn : 2 ≤ n) (hab : a + b ≤ n - 2) :
    ∀ (j : ℕ) (hj : j ≤ a),
      (decodeCodePrefix (carrierCode (n := n) a b) hn j (by omega)).frontier.lo = 2 + j ∧
      (decodeCodePrefix (carrierCode (n := n) a b) hn j (by omega)).frontier.hi = n := by
  intro j
  induction j with
  | zero => intro hj; simp [decodeCodePrefix, DecodedCodePrefix.initial]
  | succ j ih =>
      intro hj
      obtain ⟨hlo, hhi⟩ := ih (by omega)
      let f := (decodeCodePrefix (carrierCode (n := n) a b) hn j (by omega)).frontier
      have hsym : carrierCode (n := n) a b ⟨j, by omega⟩ = some true := by
        simp [carrierCode, show j < a by omega]
      have he : j + 1 - f.absorbed = 1 := by
        have hfl : f.lo = 2 + j := hlo
        have hfh : f.hi = n := hhi
        simp [CheckpointSourceFrontier.absorbed, hfl, hfh]
      have hstep : (decodeCodePrefix (carrierCode (n := n) a b) hn (j + 1)
          (by omega)).frontier.lo = f.lo + 1 ∧
          (decodeCodePrefix (carrierCode (n := n) a b) hn (j + 1)
          (by omega)).frontier.hi = f.hi := by
        simp only [decodeCodePrefix, DecodedCodePrefix.advance, hsym]
        change f.lo + (j + 1 - f.absorbed) = f.lo + 1 ∧ f.hi = f.hi
        rw [he]
        exact ⟨rfl, rfl⟩
      constructor
      · have hfl : f.lo = 2 + j := hlo
        omega
      · exact hstep.2.trans hhi

theorem carrierCode_left_prefix (a b : ℕ) (hn : 2 ≤ n) (hab : a + b ≤ n - 2) :
    ∀ (j : ℕ) (hj : j ≤ b),
      (decodeCodePrefix (carrierCode (n := n) a b) hn (a + j) (by omega)).frontier.lo = 2 + a ∧
      (decodeCodePrefix (carrierCode (n := n) a b) hn (a + j) (by omega)).frontier.hi = n - j := by
  intro j
  induction j with
  | zero => intro hj; simpa using carrierCode_right_prefix a b hn hab a (le_refl _)
  | succ j ih =>
      intro hj
      obtain ⟨hlo, hhi⟩ := ih (by omega)
      let f := (decodeCodePrefix (carrierCode (n := n) a b) hn (a + j) (by omega)).frontier
      have hsym : carrierCode (n := n) a b ⟨a + j, by omega⟩ = some false := by
        simp [carrierCode, show ¬ a + j < a by omega, show a + j < a + b by omega]
      have he : a + j + 1 - f.absorbed = 1 := by
        have hfl : f.lo = 2 + a := hlo
        have hfh : f.hi = n - j := hhi
        simp only [CheckpointSourceFrontier.absorbed, hfl, hfh]
        omega
      have hstep : (decodeCodePrefix (carrierCode (n := n) a b) hn (a + (j + 1))
          (by omega)).frontier.lo = f.lo ∧
          (decodeCodePrefix (carrierCode (n := n) a b) hn (a + (j + 1))
          (by omega)).frontier.hi = f.hi - 1 := by
        suffices hh : (decodeCodePrefix (carrierCode (n := n) a b) hn ((a + j) + 1)
            (by omega)).frontier.lo = f.lo ∧
            (decodeCodePrefix (carrierCode (n := n) a b) hn ((a + j) + 1)
            (by omega)).frontier.hi = f.hi - 1 by
          have hf := decode_frontier_congr (carrierCode (n := n) a b) hn
            (show a + (j + 1) ≤ n - 2 by omega) (show (a + j) + 1 ≤ n - 2 by omega)
            (by omega)
          exact ⟨(congrArg CheckpointSourceFrontier.lo hf).trans hh.1,
            (congrArg CheckpointSourceFrontier.hi hf).trans hh.2⟩
        simp only [decodeCodePrefix, DecodedCodePrefix.advance, hsym]
        change f.lo = f.lo ∧ f.hi - (a + j + 1 - f.absorbed) = f.hi - 1
        rw [he]
        exact ⟨rfl, rfl⟩
      constructor
      · exact hstep.1.trans hlo
      · have hfh : f.hi = n - j := hhi
        omega

theorem carrierCode_frontier (a b : ℕ) (hn : 2 ≤ n) (hab : a + b ≤ n - 2) :
    (decodeCode (carrierCode (n := n) a b) hn).frontier.lo = 2 + a ∧
      (decodeCode (carrierCode (n := n) a b) hn).frontier.hi = n - b := by
  have hskip := decodeCodePrefix_skip (carrierCode (n := n) a b) hn
    (a + b) hab (n - 2) (le_refl _) hab (by
      intro i hi _
      simp [carrierCode, show ¬ i.val < a by omega, show ¬ i.val < a + b by omega])
  obtain ⟨hlo, hhi⟩ := carrierCode_left_prefix a b hn hab b (le_refl _)
  exact ⟨(congrArg CheckpointSourceFrontier.lo hskip.1).trans hlo,
    (congrArg CheckpointSourceFrontier.hi hskip.1).trans hhi⟩

def canonicalCarrierCode (u k : ℕ) : Code (n - 2) :=
  carrierCode (u - 2) (n - (u + k))

theorem canonicalCarrierCode_frontier (u k : ℕ)
    (hu : 2 ≤ u) (huk : u + k ≤ n) :
    (decodeCode (canonicalCarrierCode (n := n) u k) (by omega)).frontier.lo = u ∧
      (decodeCode (canonicalCarrierCode (n := n) u k) (by omega)).frontier.hi = u + k := by
  have h := carrierCode_frontier (u - 2) (n - (u + k)) (by omega : 2 ≤ n) (by omega)
  dsimp [canonicalCarrierCode]
  constructor <;> omega

end FutureEvent
