import RegisteredAbsorptionChains.CombinatorialCore
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Nat.Choose.Vandermonde

namespace RegisteredAbsorptionChains

/-- An `r`-element subset of a finite linear carrier. -/
abbrev Select (N r : ℕ) := {s : Finset (Fin N) // s.card = r}

theorem card_select (N r : ℕ) : Fintype.card (Select N r) = N.choose r := by
  classical
  rw [Fintype.card_subtype]
  change (Finset.univ.filter (fun s : Finset (Fin N) => s.card = r)).card = N.choose r
  have h : Finset.univ.filter (fun s : Finset (Fin N) => s.card = r) =
      (Finset.univ : Finset (Fin N)).powersetCard r := by
    ext s
    simp [Finset.mem_powersetCard]
  rw [h, Finset.card_powersetCard]
  simp

/-- Cuts, carrier phase, and occupied offsets for a fixed-rank fiber. -/
abbrev RankFiberParams (n k t : ℕ) :=
  Fin n × Select (k - 1) (t - 1) × Select (n - 1) t

theorem card_rankFiberParams (n k t : ℕ) :
    Fintype.card (RankFiberParams n k t) =
      n * (k - 1).choose (t - 1) * (n - 1).choose t := by
  simp [RankFiberParams, Fintype.card_prod, mul_assoc]

/-- Equation (4.4) with `t = r - 1`, for the finite parameter type. -/
theorem card_rankFiberParams_paper (n k t : ℕ) (hn : 1 ≤ n) :
    Fintype.card (RankFiberParams n k t) =
      (t + 1) * (k - 1).choose (t - 1) * n.choose (t + 1) := by
  rw [card_rankFiberParams]
  have h := Nat.add_one_mul_choose_eq (n - 1) t
  rw [Nat.sub_add_cancel hn] at h
  calc
    n * (k - 1).choose (t - 1) * (n - 1).choose t =
        (k - 1).choose (t - 1) * (n * (n - 1).choose t) := by ac_rfl
    _ = (k - 1).choose (t - 1) * (n.choose (t + 1) * (t + 1)) := by rw [h]
    _ = (t + 1) * (k - 1).choose (t - 1) * n.choose (t + 1) := by ac_rfl

/-- The Vandermonde reduction of the fixed-fiber rank sum, indexed by `i = t - 1`. -/
theorem vandermonde_rank_sum (n k : ℕ) (hn : 1 ≤ n) (hk : 1 ≤ k) :
    ∑ i ∈ Finset.range k, (k - 1).choose i * (n - 1).choose (i + 1) =
      (n + k - 2).choose k := by
  have hsum := Nat.add_choose_eq (n - 1) (k - 1) k
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hsum
  rw [Finset.sum_range_succ'] at hsum
  have hzero : (k - 1).choose k = 0 :=
    Nat.choose_eq_zero_of_lt (by omega)
  simp [hzero] at hsum
  have hsum' : ∑ i ∈ Finset.range k,
      (n - 1).choose (i + 1) * (k - 1).choose (k - (i + 1)) =
      ((n - 1) + (k - 1)).choose k := hsum.symm
  calc
    ∑ i ∈ Finset.range k, (k - 1).choose i * (n - 1).choose (i + 1) =
      ∑ i ∈ Finset.range k,
        (n - 1).choose (i + 1) * (k - 1).choose (k - (i + 1)) := by
          apply Finset.sum_congr rfl
          intro i hi
          have hik : i < k := Finset.mem_range.mp hi
          have hsym : (k - 1).choose (k - (i + 1)) = (k - 1).choose i := by
            apply Nat.choose_symm_of_eq_add
            omega
          rw [hsym]
          ac_rfl
    _ = ((n - 1) + (k - 1)).choose k := hsum'
    _ = (n + k - 2).choose k := by congr 1; omega

/-- Formal fixed-chain placements, stratified by the positive number of outside blocks. -/
abbrev FiberParams (n k : ℕ) :=
  (i : Fin k) × RankFiberParams n k (i.1 + 1)

/-- Equation (4.3) for the complete cut/phase/offset parameter type. -/
theorem card_fiberParams (n k : ℕ) (hn : 1 ≤ n) (hk : 1 ≤ k) :
    Fintype.card (FiberParams n k) = n * (n + k - 2).choose k := by
  classical
  rw [Fintype.card_sigma]
  simp_rw [card_rankFiberParams]
  simp only [Nat.add_sub_cancel_right]
  calc
    ∑ i : Fin k, n * (k - 1).choose i.1 * (n - 1).choose (i.1 + 1) =
      n * ∑ i : Fin k,
        (k - 1).choose i.1 * (n - 1).choose (i.1 + 1) := by
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro i _
          ac_rfl
    _ = n * ∑ i ∈ Finset.range k,
        (k - 1).choose i * (n - 1).choose (i + 1) := by
          rw [← Fin.sum_univ_eq_sum_range]
    _ = n * (n + k - 2).choose k := by rw [vandermonde_rank_sum n k hn hk]

end RegisteredAbsorptionChains
