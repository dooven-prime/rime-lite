import RegisteredAbsorptionChains.CleanCodeInduction
import Mathlib.Data.Fin.Tuple.Basic
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- Zero for an all-zero code, otherwise the one-based location of its final
nonzero symbol. -/
def codeLastCheckpoint : (m : ℕ) → Code m → ℕ
  | 0, _ => 0
  | m + 1, c =>
      if c (Fin.last m) = none then codeLastCheckpoint m (Fin.init c)
      else m + 1

private def codeSnocEquiv (m : ℕ) : (Code m × Symbol) ≃ Code (m + 1) where
  toFun p := Fin.snoc p.1 p.2
  invFun c := (Fin.init c, c (Fin.last m))
  left_inv := by intro ⟨c, a⟩; simp [Fin.init_snoc, Fin.snoc_last]
  right_inv := by intro c; exact Fin.snoc_init_self c

theorem codeLastCheckpoint_snoc (m : ℕ) (c : Code m) (a : Symbol) :
    codeLastCheckpoint (m + 1) (Fin.snoc c a) =
      if a = none then codeLastCheckpoint m c else m + 1 := by
  simp [codeLastCheckpoint, Fin.snoc_last, Fin.init_snoc]

/-- The all-zero code contributes `weight 0`; the final checkpoint at
zero-based position `b` contributes `2 * 3^b` codes. -/
theorem codeLastCheckpoint_weighted_sum (m : ℕ) (weight : ℕ → ℕ) :
    ∑ c : Code m, weight (codeLastCheckpoint m c) =
      weight 0 + ∑ b : Fin m, 2 * 3 ^ b.1 * weight (b.1 + 1) := by
  induction m with
  | zero => simp [Code, codeLastCheckpoint]
  | succ m ih =>
      have hsymbol (c : Code m) :
          (∑ a : Symbol,
            weight (if a = none then codeLastCheckpoint m c else m + 1)) =
            weight (codeLastCheckpoint m c) + 2 * weight (m + 1) := by
        have huniv : (Finset.univ : Finset Symbol) =
            {none, some false, some true} := by
          ext a
          cases a with
          | none => simp
          | some side => cases side <;> simp
        rw [huniv]
        simp [Symbol, Side, two_mul]
      calc
        ∑ c : Code (m + 1), weight (codeLastCheckpoint (m + 1) c) =
            ∑ p : Code m × Symbol,
              weight (codeLastCheckpoint (m + 1) (Fin.snoc p.1 p.2)) := by
          exact (Fintype.sum_equiv (codeSnocEquiv m)
            (fun p : Code m × Symbol =>
              weight (codeLastCheckpoint (m + 1) (Fin.snoc p.1 p.2)))
            (fun c : Code (m + 1) =>
              weight (codeLastCheckpoint (m + 1) c))
            (by intro p; rfl)).symm
        _ = (∑ c : Code m, weight (codeLastCheckpoint m c)) +
            2 * 3 ^ m * weight (m + 1) := by
          simp only [Fintype.sum_prod_type, codeLastCheckpoint_snoc]
          simp_rw [hsymbol]
          rw [Finset.sum_add_distrib]
          simp [mul_assoc, mul_comm]
        _ = weight 0 + ∑ b : Fin (m + 1),
              2 * 3 ^ b.1 * weight (b.1 + 1) := by
          rw [ih, Fin.sum_univ_castSucc]
          simp [add_assoc]

/-- The independent last-checkpoint counter reads exactly the cumulative
checkpoint stored by the code decoder at every prefix. -/
theorem lastCodeCheckpoint_eq_codeLastCheckpoint
    {n : ℕ} [NeZero n] (c : Code (n - 2)) :
    ∀ (j : ℕ) (hj : j ≤ n - 2),
      lastCodeCheckpoint c j hj =
        codeLastCheckpoint j
          (fun i : Fin j => c ⟨i.1, by omega⟩) := by
  intro j
  induction j with
  | zero =>
      intro hj
      simp [lastCodeCheckpoint, codeLastCheckpoint]
  | succ j ih =>
      intro hj
      have hj' : j ≤ n - 2 := by omega
      have hinit :
          Fin.init (fun i : Fin (j + 1) => c ⟨i.1, by omega⟩) =
            (fun i : Fin j => c ⟨i.1, by omega⟩) := by
        funext i
        rfl
      by_cases hsymbol : c ⟨j, by omega⟩ = none
      · simp [lastCodeCheckpoint, codeLastCheckpoint, hsymbol,
          hinit, ih hj']
      · simp only [lastCodeCheckpoint, codeLastCheckpoint]
        split
        · contradiction
        · simp [hsymbol]

theorem decodeCode_absorbed_eq_codeLastCheckpoint
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n) :
    (decodeCode c hn).frontier.absorbed =
      codeLastCheckpoint (n - 2) c := by
  rw [decodeCode, decodeCodePrefix_absorbed,
    lastCodeCheckpoint_eq_codeLastCheckpoint]

end RegisteredAbsorptionChains
