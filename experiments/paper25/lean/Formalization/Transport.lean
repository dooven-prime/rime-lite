import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Group.Basic
import Mathlib.Data.Real.Basic

/-!
# Paper XXV: typed transport core

The algebraic part is stated in a monoid so that the cancellation argument is
independent of a particular matrix implementation. The scalar diagnostic is
represented by an explicit conjugation-invariance hypothesis; this file does
not derive that hypothesis from a concrete unitary or norm implementation.
-/

namespace Rime.Paper25

section AlgebraicTransport

variable {R : Type*} [Monoid R]

/-- Conjugation by a chosen left/right pair. -/
def conjugate (u x uStar : R) : R := u * x * uStar

/-- A transported three-factor block. -/
def transportedBlock (u qi y qj uStar : R) : R :=
  conjugate u qi uStar * conjugate u y uStar * conjugate u qj uStar

theorem conjugate_mul
    (u x y uStar : R) (hcancel : uStar * u = 1) :
    conjugate u x uStar * conjugate u y uStar =
      conjugate u (x * y) uStar := by
  calc
    conjugate u x uStar * conjugate u y uStar =
        u * x * (uStar * u) * y * uStar := by
          simp [conjugate, mul_assoc]
    _ = conjugate u (x * y) uStar := by
          rw [hcancel]
          simp [conjugate, mul_assoc]

/-- Exact block covariance under the cancellation `uStar * u = 1`. -/
theorem transported_block_eq
    (u qi y qj uStar : R) (hcancel : uStar * u = 1) :
    transportedBlock u qi y qj uStar =
      conjugate u (qi * y * qj) uStar := by
  unfold transportedBlock
  rw [conjugate_mul u qi y uStar hcancel]
  exact conjugate_mul u (qi * y) qj uStar hcancel

end AlgebraicTransport

section FiniteAggregate

variable {R : Type*} [Semiring R]

/-! Finite aggregate covariance. -/
theorem finite_aggregate_conjugate
    {ι : Type*} [Fintype ι]
    (u uStar : R) (x : ι → R) :
    (∑ i, conjugate u (x i) uStar) =
      conjugate u (∑ i, x i) uStar := by
  simp only [conjugate]
  calc
    (∑ i, (u * x i) * uStar) =
        (∑ i, u * x i) * uStar := by
          exact (Finset.sum_mul Finset.univ (fun i => u * x i) uStar).symm
    _ = (u * ∑ i, x i) * uStar := by
          rw [Finset.mul_sum]

end FiniteAggregate

section MetricInterface

variable {R : Type*} [Monoid R]

/-- A scalar diagnostic that is invariant under the declared conjugation. -/
def ConjugationInvariant (u uStar : R) (m : R → ℝ) : Prop :=
  ∀ x, m (conjugate u x uStar) = m x

/-- The transported block has exactly the same declared metric diagnostic. -/
theorem transported_block_measure_eq
    (u qi y qj uStar : R) (hcancel : uStar * u = 1)
    (m : R → ℝ) (hm : ConjugationInvariant u uStar m) :
    m (transportedBlock u qi y qj uStar) = m (qi * y * qj) := by
  rw [transported_block_eq u qi y qj uStar hcancel]
  exact hm (qi * y * qj)

/-- Any threshold predicate built from an invariant scalar diagnostic is also
    preserved coordinatewise. -/
def Active (m : R → ℝ) (threshold : ℝ) (x : R) : Prop :=
  m x > threshold

theorem transported_block_active_iff
    (u qi y qj uStar : R) (hcancel : uStar * u = 1)
    (m : R → ℝ) (hm : ConjugationInvariant u uStar m)
    (threshold : ℝ) :
    Active m threshold (transportedBlock u qi y qj uStar) ↔
      Active m threshold (qi * y * qj) := by
  simp [Active, transported_block_measure_eq u qi y qj uStar hcancel m hm]

end MetricInterface

end Rime.Paper25
