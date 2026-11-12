import Paper44.CircularPrefixQuotient
import FutureEvent.ClosedQuotientCount

/-! # Theorem 3.3: exact actual prefix-observer quotient enumeration

The actual quotient equivalence supplies the four sectors. The finite
carrier/label/placement fibres are reindexed by absorbed size before summing.
No cardinality assumption is made about an unminimized history graph.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

theorem finite_actualProperFibreAt (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hj : 0 < j) :
    Finite (ActualProperFibreAt (n := n) r j) := by
  have : Finite (ActualProperLabelsAt (n := n) r j) := by
    by_cases hz : r = 0
    · subst r
      exact Nat.finite_of_card_ne_zero (by rw [card_actualProperLabelsAt_zero hn hj]; decide)
    · exact Finite.of_equiv _ (properCarrierCountEquiv hn hr (by omega) (j := j)).symm
  have : ∀ x : ActualProperLabelsAt (n := n) r j,
      Finite (ActualProperPlacements j x.1.val x.2) := by
    intro x
    unfold ActualProperPlacements
    infer_instance
  unfold ActualProperFibreAt
  infer_instance

theorem finite_actualProperObservation (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Finite (ActualProperObservation (n := n) j) := by
  have : ∀ r : Fin (n - 2), Finite (ActualProperFibreAt (n := n) r.val j) :=
    fun r => finite_actualProperFibreAt hn r.isLt hj
  exact Finite.of_equiv _ (properObservationSizeEquiv (n := n) j).symm

theorem card_actualProperObservation (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (ActualProperObservation (n := n) j) =
      n * ∑ r ∈ Finset.range (n - 2),
        properCarrierPrefixCount r j *
          (2 * (n - 2) - r).choose (n - 2 - r) := by
  classical
  have : ∀ r : Fin (n - 2), Finite (ActualProperFibreAt (n := n) r.val j) :=
    fun r => finite_actualProperFibreAt hn r.isLt hj
  rw [Nat.card_congr (properObservationSizeEquiv j), Nat.card_sigma]
  calc
    _ = ∑ r : Fin (n - 2), properCarrierPrefixCount r.val j *
        (n * (2 * (n - 2) - r.val).choose (n - 2 - r.val)) := by
      apply Finset.sum_congr rfl
      intro r _
      exact card_actualProperFibreAt_all hn r.isLt hj
    _ = n * ∑ r : Fin (n - 2), properCarrierPrefixCount r.val j *
        (2 * (n - 2) - r.val).choose (n - 2 - r.val) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro r _
      ac_rfl
    _ = _ := by rw [← Fin.sum_univ_eq_sum_range]

theorem finite_prefixNormalForms (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Finite (PrefixNormalForms n j) := by
  have : Finite (ActualTerminalLabel n j) :=
    Finite.of_equiv _ (terminalPrefixActualEquiv hn j hj)
  have := finite_actualProperObservation hn j hj
  unfold PrefixNormalForms
  infer_instance

theorem finite_prefixObserverQuotient (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Finite (PrefixObserverQuotient hn j hj) := by
  have := finite_prefixNormalForms hn j hj
  exact Finite.of_equiv _ (prefixObserverNormalEquiv hn j hj).symm

/-- Theorem 3.3's right-hand side, with `r=0` treated by `c(0,j)=1`. -/
def paperTheorem33Count (n j : ℕ) : ℕ :=
  1 + n * (2 * n - 4).choose (n - 3) +
    (2 ^ j * (n - 2).choose j +
      ∑ ell ∈ Finset.Icc 1 (j - 1),
        2 ^ ell * (n - 3).choose (ell - 1)) +
    n * ∑ r ∈ Finset.range (n - 2),
      properCarrierPrefixCount r j *
        (2 * (n - 2) - r).choose (n - 2 - r)

/-- Exact cardinality of the minimal all-word observer quotient on genuine
singleton-seed states. This is not merely the parameter-type count. -/
theorem card_prefixObserverQuotient_paper (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (PrefixObserverQuotient (n := n) hn j hj) =
      paperTheorem33Count n j := by
  have : Finite (ActualTerminalLabel n j) :=
    Finite.of_equiv _ (terminalPrefixActualEquiv hn j hj)
  have := finite_actualProperObservation hn j hj
  rw [Nat.card_congr (prefixObserverNormalEquiv hn j hj)]
  change Nat.card (Unit ⊕ (RegisterablePlacements n ⊕
    (ActualTerminalLabel n j ⊕ ActualProperObservation (n := n) j))) = _
  rw [Nat.card_sum, Nat.card_sum, Nat.card_sum,
    card_actual_registerable_placements hn,
    card_actualTerminalLabel_paper hn j hj,
    card_actualProperObservation hn j hj]
  simp only [Nat.card_unique]
  unfold paperTheorem33Count
  omega

/-- Expanded paper notation: `1 + R_n + T_(n-2,j) + A_n^[j]`. -/
theorem paperTheorem33_formula (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (PrefixObserverQuotient (n := n) hn j hj) =
      1 + n * (2 * n - 4).choose (n - 3) +
        (2 ^ j * (n - 2).choose j +
          ∑ ell ∈ Finset.Icc 1 (j - 1),
            2 ^ ell * (n - 3).choose (ell - 1)) +
        n * ∑ r ∈ Finset.range (n - 2),
          properCarrierPrefixCount r j *
            (2 * (n - 2) - r).choose (n - 2 - r) := by
  exact card_prefixObserverQuotient_paper hn j hj

def paperTheorem33RegisteredCount (n j : ℕ) : ℕ :=
  (2 ^ j * (n - 2).choose j +
    ∑ ell ∈ Finset.Icc 1 (j - 1), 2 ^ ell * (n - 3).choose (ell - 1)) +
  n * ∑ r ∈ Finset.range (n - 2),
    properCarrierPrefixCount r j *
      (2 * (n - 2) - r).choose (n - 2 - r)

/-- The second formula of Theorem 3.3, on the actual registered state domain
with the same per-letter observer and future equivalence. -/
theorem card_registeredPrefixObserverQuotient_paper (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (RegisteredPrefixObserverQuotient (n := n) hn j hj) =
      paperTheorem33RegisteredCount n j := by
  have : Finite (ActualTerminalLabel n j) :=
    Finite.of_equiv _ (terminalPrefixActualEquiv hn j hj)
  have := finite_actualProperObservation hn j hj
  rw [Nat.card_congr (registeredPrefixObserverNormalEquiv hn j hj)]
  change Nat.card (ActualTerminalLabel n j ⊕ ActualProperObservation (n := n) j) = _
  rw [Nat.card_sum, card_actualTerminalLabel_paper hn j hj,
    card_actualProperObservation hn j hj]
  rfl

/-- Both assertions of the manuscript's Theorem 3.3. -/
theorem paperTheorem33 (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (PrefixObserverQuotient (n := n) hn j hj) = paperTheorem33Count n j ∧
      Nat.card (RegisteredPrefixObserverQuotient (n := n) hn j hj) =
        paperTheorem33RegisteredCount n j :=
  ⟨card_prefixObserverQuotient_paper hn j hj,
    card_registeredPrefixObserverQuotient_paper hn j hj⟩

/-- The unregistered domain contributes exactly the sink and the inherited
registerable placements. This is a consequence of the two actual quotients. -/
theorem prefixQuotient_card_split (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Nat.card (PrefixObserverQuotient (n := n) hn j hj) =
      1 + n * (2 * n - 4).choose (n - 3) +
        Nat.card (RegisteredPrefixObserverQuotient (n := n) hn j hj) := by
  rw [card_prefixObserverQuotient_paper, card_registeredPrefixObserverQuotient_paper]
  unfold paperTheorem33Count paperTheorem33RegisteredCount
  omega

end Paper44
