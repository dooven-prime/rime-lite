import PaperXL

namespace PaperXL.FixedPrefixGrowthChecks

private def demo : FixedPrefixExtension (Fin 2) (Fin 2 × Fin 2) (Fin 2) where
  futureCode := Prod.fst
  prefixTag := Prod.snd
  future_surjective := by
    intro x
    exact ⟨(x, 0), rfl⟩
  pair_injective := by
    intro x y h
    exact Prod.ext (congrArg Prod.fst h) (congrArg Prod.snd h)

example : Fintype.card (Fin 2) ≤ Fintype.card (Fin 2 × Fin 2) := by
  simpa using demo.future_card_le_observer_card

example : Fintype.card (Fin 2 × Fin 2) ≤
    Fintype.card (Fin 2) * Fintype.card (Fin 2) := by
  simpa using demo.observer_card_le_future_mul_tag

example : Fintype.card (Fin 2 × Fin 2) ≤
    Fintype.card (Fin 2) * (2 + 1) ^ 1 := by
  apply demo.observer_card_le_future_mul_pow 2 1
  decide

example (tag : ℕ → ℕ) (k : ℕ)
    (hLower : ∀ n, 1 ≤ tag n)
    (hUpper : ∀ n, tag n ≤ (n + 1) ^ k) :
    Filter.Tendsto (cardRoot tag) Filter.atTop (nhds 1) := by
  exact cardRoot_tendsto_one_of_polynomial_bounds tag k hLower hUpper

example (future observer tag : ℕ → ℕ) (k : ℕ) (lim : ℝ)
    (hLower : ∀ n, future n ≤ observer n)
    (hUpper : ∀ n, observer n ≤ future n * tag n)
    (hTagLower : ∀ n, 1 ≤ tag n)
    (hTagUpper : ∀ n, tag n ≤ (n + 1) ^ k)
    (hFuture : Filter.Tendsto (cardRoot future) Filter.atTop (nhds lim)) :
    Filter.Tendsto (cardRoot observer) Filter.atTop (nhds lim) := by
  exact observer_growth_eq_future_growth_of_polynomial_tags future observer tag k lim
    hLower hUpper hTagLower hTagUpper hFuture

end PaperXL.FixedPrefixGrowthChecks
