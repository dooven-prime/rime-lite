import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Paper XXVI: TA-III reset-word envelope

Lean uses zero-based indices for a border set: an index `j` represents the
one-based border length `j + 1`.  Thus the ambient set of possible lengths is
`Finset.range r`.  The exact pattern-waiting identity and the coupling from a
reset word to pair/global absorption are supplied by certificate fields.  The
envelope and its sharp finite-sum arithmetic are proved here without a
probability-measure formalization.
-/

namespace Rime.Paper26

open scoped BigOperators

/-! ### Border sums -/

/-- The border waiting sum for a zero-based border index set. -/
def borderSum (k : ℕ) (borders : Finset ℕ) : ℚ :=
  borders.sum (fun j => (k : ℚ) ^ (j + 1))

/-- The universal sum over all possible one-based border lengths `1, ..., r`. -/
def envelope (k r : ℕ) : ℚ :=
  (Finset.range r).sum (fun j => (k : ℚ) ^ (j + 1))

theorem border_sum_le_envelope
    {k r : ℕ} (_hk : 2 ≤ k) {borders : Finset ℕ}
    (hborders : borders ⊆ Finset.range r) :
    borderSum k borders ≤ envelope k r := by
  unfold borderSum envelope
  exact Finset.sum_le_sum_of_subset_of_nonneg hborders (by
    intro j hj hnot
    positivity)

/-! ### Closed form for the geometric envelope -/

theorem envelope_mul_sub (k r : ℕ) :
    envelope k r * ((k : ℚ) - 1) =
      (k : ℚ) ^ (r + 1) - (k : ℚ) := by
  induction r with
  | zero => simp [envelope]
  | succ r ih =>
      calc
        envelope k (r + 1) * ((k : ℚ) - 1) =
            (envelope k r + (k : ℚ) ^ (r + 1)) * ((k : ℚ) - 1) := by
              simp [envelope, Finset.sum_range_succ]
        _ = envelope k r * ((k : ℚ) - 1) +
              (k : ℚ) ^ (r + 1) * ((k : ℚ) - 1) := by
              ring
        _ = ((k : ℚ) ^ (r + 1) - (k : ℚ)) +
              (k : ℚ) ^ (r + 1) * ((k : ℚ) - 1) := by
              rw [ih]
        _ = (k : ℚ) ^ (r + 1 + 1) - (k : ℚ) := by
              rw [pow_succ]
              ring

theorem envelope_eq_closed
    {k r : ℕ} (hk : 1 < k) :
    envelope k r =
      ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  have hkq : (1 : ℚ) < (k : ℚ) := by
    exact_mod_cast hk
  have hden : (k : ℚ) - 1 ≠ 0 :=
    sub_ne_zero.mpr (ne_of_gt hkq)
  apply (eq_div_iff hden).2
  exact envelope_mul_sub k r

/-! ### The certificate interface for TA-III -/

/--
A border-waiting certificate packages the exact pattern formula.  The field
`mean_eq` is the only input from pattern waiting; the finite envelope is proved
from the border inclusion alone.
-/
structure BorderWaitingCertificate (k r : ℕ) where
  borders : Finset ℕ
  borders_subset : borders ⊆ Finset.range r
  expectedWait : ℚ
  mean_eq : expectedWait = borderSum k borders

theorem certificate_envelope
    {k r : ℕ} (hk : 2 ≤ k)
    (certificate : BorderWaitingCertificate k r) :
    certificate.expectedWait ≤ envelope k r := by
  rw [certificate.mean_eq]
  exact border_sum_le_envelope hk certificate.borders_subset

theorem certificate_closed_bound
    {k r : ℕ} (hk : 2 ≤ k)
    (certificate : BorderWaitingCertificate k r) :
    certificate.expectedWait ≤
      ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  calc
    certificate.expectedWait ≤ envelope k r := certificate_envelope hk certificate
    _ = ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) :=
      envelope_eq_closed (lt_of_lt_of_le (by decide) hk)

/-!
The probabilistic part of TA-III is represented by this small coupling
certificate.  `worstPairMean` is the maximum pairwise mean, while `globalMean`
is the mean of the synchronized process under one common random stream.
-/
structure TAIIIData (k r : ℕ) where
  worstPairMean : ℚ
  globalMean : ℚ
  pair_le_global : worstPairMean ≤ globalMean
  resetWord : BorderWaitingCertificate k r
  global_le_resetWord : globalMean ≤ resetWord.expectedWait

theorem taIII_global_bound
    {k r : ℕ} (hk : 2 ≤ k) (data : TAIIIData k r) :
    data.globalMean ≤
      ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  exact data.global_le_resetWord.trans (certificate_closed_bound hk data.resetWord)

theorem taIII_pair_bound
    {k r : ℕ} (hk : 2 ≤ k) (data : TAIIIData k r) :
    data.worstPairMean ≤
      ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  exact data.pair_le_global.trans (taIII_global_bound hk data)

theorem taIII_chain
    {k r : ℕ} (hk : 2 ≤ k) (data : TAIIIData k r) :
    data.worstPairMean ≤ data.globalMean ∧
      data.globalMean ≤
        ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  exact ⟨data.pair_le_global, taIII_global_bound hk data⟩

/-! ### Arithmetic sharpness -/

/-- The complete border set, which has every one-based border length. -/
def fullBorderCertificate (k r : ℕ) : BorderWaitingCertificate k r :=
  { borders := Finset.range r
    borders_subset := by exact Finset.Subset.rfl
    expectedWait := envelope k r
    mean_eq := by simp [envelope, borderSum] }

theorem full_border_attains_envelope (k r : ℕ) :
    (fullBorderCertificate k r).expectedWait = envelope k r := by
  simp [fullBorderCertificate]

theorem taIII_arithmetic_sharp (k r : ℕ) :
    ∃ certificate : BorderWaitingCertificate k r,
      certificate.expectedWait = envelope k r :=
  ⟨fullBorderCertificate k r, full_border_attains_envelope k r⟩

theorem taIII_arithmetic_sharp_closed
    {k r : ℕ} (hk : 2 ≤ k) :
    ∃ certificate : BorderWaitingCertificate k r,
      certificate.expectedWait =
        ((k : ℚ) ^ (r + 1) - (k : ℚ)) / ((k : ℚ) - 1) := by
  refine ⟨fullBorderCertificate k r, ?_⟩
  rw [full_border_attains_envelope]
  exact envelope_eq_closed (lt_of_lt_of_le (by decide) hk)

end Rime.Paper26
