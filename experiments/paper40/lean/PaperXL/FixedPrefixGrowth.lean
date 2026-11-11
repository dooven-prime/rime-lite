import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.Prod

open Filter

namespace PaperXL

universe u v w

/-!
# Fixed-prefix cardinality interface

This file deliberately works one level below a concrete quotient
construction.  `Future` represents the classes retained by the future-event
observer, `Observer` represents the classes of an observer which also keeps a
finite prefix label, and `Tag` is the finite label alphabet.  The two maps in
`FixedPrefixExtension` are the only data needed for the counting argument:
the future projection is onto, while the pair (future class, prefix tag)
identifies an extended class.

Consequently this module proves a finite cardinality envelope, not a concrete
formula for the circular model.  A model-specific quotient theorem can use
these lemmas after supplying its own quotient representatives and a bound on
the number of prefix tags.
-/

structure FixedPrefixExtension
    (Future : Type u) (Observer : Type v) (Tag : Type w)
    [Fintype Future] [Fintype Observer] [Fintype Tag] where
  /-- Forget the retained prefix and project to the future-observer class. -/
  futureCode : Observer → Future
  /-- The finite information retained in addition to the future class. -/
  prefixTag : Observer → Tag
  /-- Every future class has at least one extended observer class. -/
  future_surjective : Function.Surjective futureCode
  /-- The future class together with the retained tag identifies the class. -/
  pair_injective :
    Function.Injective (fun x => (futureCode x, prefixTag x))

namespace FixedPrefixExtension

variable {Future : Type u} {Observer : Type v} {Tag : Type w}
variable [Fintype Future] [Fintype Observer] [Fintype Tag]

theorem future_card_le_observer_card (E : FixedPrefixExtension Future Observer Tag) :
    Fintype.card Future ≤ Fintype.card Observer := by
  exact Fintype.card_le_of_surjective E.futureCode E.future_surjective

theorem observer_card_le_future_mul_tag (E : FixedPrefixExtension Future Observer Tag) :
    Fintype.card Observer ≤ Fintype.card Future * Fintype.card Tag := by
  have h := Fintype.card_le_of_injective
    (fun x => (E.futureCode x, E.prefixTag x)) E.pair_injective
  simpa [Fintype.card_prod] using h

theorem card_bounds (E : FixedPrefixExtension Future Observer Tag) :
    Fintype.card Future ≤ Fintype.card Observer ∧
      Fintype.card Observer ≤ Fintype.card Future * Fintype.card Tag :=
  ⟨E.future_card_le_observer_card, E.observer_card_le_future_mul_tag⟩

/-- A fixed finite-prefix tag family contributes at most a polynomial factor.

The parameter `k` is intentionally an external bound: the model-specific
part of a Paper XL observer must prove `card Tag ≤ (n + 1)^k`.  This theorem
then turns that proof into the corresponding cardinality bound without making
any asymptotic or circular-model assumptions.
-/
theorem observer_card_le_future_mul_pow
    (E : FixedPrefixExtension Future Observer Tag)
    (n k : ℕ)
    (hTag : Fintype.card Tag ≤ (n + 1) ^ k) :
    Fintype.card Observer ≤ Fintype.card Future * (n + 1) ^ k := by
  exact le_trans E.observer_card_le_future_mul_tag
    (Nat.mul_le_mul_left _ hTag)

end FixedPrefixExtension

/-! ## Exponential growth under subexponential labels

The next results isolate the asymptotic step used for fixed-depth prefix
observers.  They are stated for cardinality sequences, so a concrete model
only needs to prove the two pointwise counting bounds and the growth limit of
its future quotient.  In particular, the results do not assert a specific
limit for the circular model.
-/

/-- The `(n+1)`-st-root growth profile of a natural-number sequence. -/
noncomputable def cardRoot (f : ℕ → ℕ) (n : ℕ) : ℝ :=
  (f n : ℝ) ^ ((n + 1 : ℕ) : ℝ)⁻¹

theorem cardRoot_mono {f g : ℕ → ℕ} (hfg : ∀ n, f n ≤ g n) :
    ∀ n, cardRoot f n ≤ cardRoot g n := by
  intro n
  unfold cardRoot
  apply Real.rpow_le_rpow (Nat.cast_nonneg _) (by exact_mod_cast hfg n)
  positivity

theorem cardRoot_mul (f g : ℕ → ℕ) (n : ℕ) :
    cardRoot (fun i => f i * g i) n = cardRoot f n * cardRoot g n := by
  unfold cardRoot
  rw [Nat.cast_mul, Real.mul_rpow (Nat.cast_nonneg _) (Nat.cast_nonneg _)]

theorem cardRoot_pow_add_one_tendsto (k : ℕ) :
    Tendsto (cardRoot (fun n => (n + 1) ^ k)) atTop (nhds 1) := by
  have hbase : Tendsto (fun n : ℕ =>
      ((n + 1 : ℕ) : ℝ) ^ ((n + 1 : ℕ) : ℝ)⁻¹) atTop (nhds 1) := by
    convert tendsto_rpow_div.comp
      (tendsto_natCast_atTop_atTop.comp (tendsto_add_atTop_nat 1)) using 1
    funext n
    simp [one_div]
  have hEq : (fun n : ℕ => cardRoot (fun i => (i + 1) ^ k) n) =
      (fun n => (((n + 1 : ℕ) : ℝ) ^ ((n + 1 : ℕ) : ℝ)⁻¹) ^ k) := by
    funext n
    simp only [cardRoot, Nat.cast_pow]
    rw [← Real.rpow_natCast_mul (by positivity : 0 ≤ ((n + 1 : ℕ) : ℝ)) k
      (((n + 1 : ℕ) : ℝ)⁻¹)]
    rw [mul_comm]
    rw [Real.rpow_mul (by positivity : 0 ≤ ((n + 1 : ℕ) : ℝ))]
    rw [Real.rpow_natCast]
  simpa [hEq] using hbase.pow k

theorem cardRoot_tendsto_one_of_polynomial_bounds
    (tag : ℕ → ℕ) (k : ℕ)
    (hTagLower : ∀ n, 1 ≤ tag n)
    (hTagUpper : ∀ n, tag n ≤ (n + 1) ^ k) :
    Tendsto (cardRoot tag) atTop (nhds 1) := by
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le
    (f := cardRoot tag)
    (g := fun _ : ℕ => (1 : ℝ))
    (h := cardRoot (fun n => (n + 1) ^ k))
    (a := (1 : ℝ))
  · exact tendsto_const_nhds
  · exact cardRoot_pow_add_one_tendsto k
  · intro n
    have hroot := cardRoot_mono hTagLower n
    simpa [cardRoot] using hroot
  · exact cardRoot_mono hTagUpper

/-- A polynomially bounded, nonempty tag family does not change an existing
exponential growth base when appended to every future class. -/
theorem observer_growth_eq_future_growth_of_polynomial_tags
    (future observer tag : ℕ → ℕ) (k : ℕ) (lim : ℝ)
    (hLower : ∀ n, future n ≤ observer n)
    (hUpper : ∀ n, observer n ≤ future n * tag n)
    (hTagLower : ∀ n, 1 ≤ tag n)
    (hTagUpper : ∀ n, tag n ≤ (n + 1) ^ k)
    (hFuture : Tendsto (cardRoot future) atTop (nhds lim)) :
    Tendsto (cardRoot observer) atTop (nhds lim) := by
  have hTag := cardRoot_tendsto_one_of_polynomial_bounds tag k hTagLower hTagUpper
  have hProduct : Tendsto (fun n => cardRoot future n * cardRoot tag n)
      atTop (nhds lim) := by
    simpa using hFuture.mul hTag
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le hFuture hProduct ?_ ?_
  · exact cardRoot_mono hLower
  · intro n
    have hroot := cardRoot_mono hUpper n
    rw [cardRoot_mul] at hroot
    exact hroot

end PaperXL
