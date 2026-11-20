import FusionLogAllR.RawAllRLowerBound

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # The explicit all-right candidate word

This file formalizes the raw word displayed in the manuscript and its exact
letter count.  The execution theorem `RealizesAllR (allRCanonicalWord n)` is
intentionally kept separate: defining and counting the candidate is not a
proof that its actual execution realizes the target.
-/

def allRStage (n j : ℕ) : List Letter :=
  pWord (n - j) ++ [.d] ++ pdWord j

def allRCanonicalWord (n : ℕ) : List Letter :=
  [.d] ++ (List.range (n - 2)).flatMap (fun i => allRStage n (i + 1)) ++
    pWord (n - 1)

theorem allRStage_length {n j : ℕ} (hjn : j ≤ n) :
    (allRStage n j).length = n + j + 1 := by
  simp [allRStage, pWord_length, pdWord_length]
  omega

private theorem range_stage_length_double (n m : ℕ) (hm : m ≤ n) :
    2 * ((List.range m).flatMap (fun i => allRStage n (i + 1))).length =
      m * (2 * n + m + 3) := by
  induction m with
  | zero => simp
  | succ m ih =>
      have hm' : m ≤ n := by omega
      rw [List.range_succ, List.flatMap_append]
      simp only [List.flatMap_singleton, List.length_append]
      have hi := ih hm'
      rw [allRStage_length (by omega : m + 1 ≤ n)]
      nlinarith

theorem allRCanonicalWord_length {n : ℕ} (hn : 3 ≤ n) :
    (allRCanonicalWord n).length = (3 * n * (n - 1)) / 2 - 1 := by
  have hstages := range_stage_length_double n (n - 2) (by omega)
  simp only [allRCanonicalWord, List.length_append,
    List.length_singleton, pWord_length]
  have hprod : 2 ∣ 3 * n * (n - 1) := by
    simpa [Nat.mul_assoc] using
      (dvd_mul_of_dvd_right (Nat.even_mul_pred_self n).two_dvd 3)
  have hq : 2 * ((3 * n * (n - 1)) / 2) = 3 * n * (n - 1) :=
    Nat.mul_div_cancel' hprod
  have hsub₂ : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
  have hsub₁ : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
  apply Nat.eq_sub_of_add_eq
  nlinarith

end FusionLogAllR
