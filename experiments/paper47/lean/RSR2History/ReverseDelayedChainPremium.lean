import RSR2History.ReverseExtraction
import RSR2History.DelayedChainExactCost
import RSR2History.GlobalHistoryPremium

/-!
The reverse-order delayed chain gives an exact premium 5n(n-1)/2 at the
same upper full-packet endpoint whose endpoint-only distance is 2n-2.
This upgrades the global lower bound, without a finite optimizer and
without asserting that the reverse order is a global maximizer.
-/

namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- Exact history distance at the cheap literal site-zero endpoint. -/
theorem reverseDelayedChain_history_distance_exact
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    (attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint (site0 n (by omega)),
        delayedUpperChainLog (reverseExtractionOrder n (by omega)))) :
    historyDistance n (by omega) (delayedChainEndpoint (site0 n (by omega)))
      (delayedUpperChainLog (reverseExtractionOrder n (by omega))) attain =
        (2 * n - 2) + (5 * n * (n - 1)) / 2 := by
  have h := delayedChain_history_distance_exact hn
    (reverseExtractionOrder_length n (by omega))
    (reverseExtractionOrder_nodup n (by omega)) (site0 n (by omega)) attain
  simpa only [reverseExtractionCost_exact, site0, Nat.add_zero] using h

/-- The stronger premium is an exact all-parameter value for this explicit
family; no extremality of its extraction order is a premise. -/
theorem reverseDelayedChain_history_premium_exact
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    historyPremium n (by omega) (delayedChainEndpoint (site0 n (by omega)))
      (delayedUpperChainLog (reverseExtractionOrder n (by omega)))
      (delayedChain_attainable hn (reverseExtractionOrder_length n (by omega))
        (reverseExtractionOrder_nodup n (by omega)) (site0 n (by omega))) =
      (5 * n * (n - 1)) / 2 := by
  have hendpoint' : endpointDistance n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (endpoint_attainable_of_logged (by omega)
        (delayedChain_attainable hn (reverseExtractionOrder_length n (by omega))
          (reverseExtractionOrder_nodup n (by omega)) (site0 n (by omega)))) = 2 * n - 2 := by
    exact allR_endpoint_distance_exact n hn _
  unfold historyPremium
  rw [reverseDelayedChain_history_distance_exact hn, hendpoint']
  omega

/-- For every full delayed-chain order beginning with atom 1, its premium
is the common quadratic loading premium plus its excess extraction cost. -/
theorem delayedChain_history_premium_eq_extraction_excess
    {n : Nat} [NeZero n] (hn : 3 ≤ n) {rest : List (Fin n)}
    (hlen : (site1 n (by omega) :: rest).length = n)
    (hnodup : (site1 n (by omega) :: rest).Nodup) :
    historyPremium n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (delayedUpperChainLog (site1 n (by omega) :: rest))
      (delayedChain_attainable hn hlen hnodup (site0 n (by omega))) =
      (5 * n * (n - 1)) / 2 +
        (lowerExtractionCost n (by omega) (site1 n (by omega) :: rest) -
          (2 * n - 2)) := by
  have hk := lowerExtractionCost_first_one_lower_bound hlen hnodup
  have hdist := delayedChain_history_distance_exact hn hlen hnodup
    (site0 n (by omega))
    (delayedChain_attainable hn hlen hnodup (site0 n (by omega)))
  have hendpoint : endpointDistance n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (endpoint_attainable_of_logged (by omega)
        (delayedChain_attainable hn hlen hnodup (site0 n (by omega)))) =
      2 * n - 2 := by
    exact allR_endpoint_distance_exact n hn _
  unfold historyPremium
  rw [hdist, hendpoint]
  simp only [site0, Fin.val_mk, Nat.add_zero]
  omega

/-- All delayed upper chains whose first transfer is atom 1 carry at least
the uniform quadratic history premium. -/
theorem delayedChain_history_premium_ge_of_first_one
    {n : Nat} [NeZero n] (hn : 3 ≤ n) {rest : List (Fin n)}
    (hlen : (site1 n (by omega) :: rest).length = n)
    (hnodup : (site1 n (by omega) :: rest).Nodup) :
    (5 * n * (n - 1)) / 2 ≤
      historyPremium n (by omega)
        (delayedChainEndpoint (site0 n (by omega)))
        (delayedUpperChainLog (site1 n (by omega) :: rest))
        (delayedChain_attainable hn hlen hnodup (site0 n (by omega))) := by
  rw [delayedChain_history_premium_eq_extraction_excess hn hlen hnodup]
  have hk := lowerExtractionCost_first_one_lower_bound hlen hnodup
  omega

/-- The first requested transfer gives a general directed-distance lower
bound for every full delayed-chain order, regardless of its remaining order. -/
theorem delayedChain_history_premium_ge_of_first_atom
    {n : Nat} [NeZero n] (hn : 3 ≤ n) {a : Fin n} {rest : List (Fin n)}
    (hlen : (a :: rest).length = n)
    (hnodup : (a :: rest).Nodup) :
    (5 * n * (n - 1)) / 2 + (n - a.val) % n - (n - 1) ≤
      historyPremium n (by omega)
        (delayedChainEndpoint (site0 n (by omega)))
        (delayedUpperChainLog (a :: rest))
        (delayedChain_attainable hn hlen hnodup (site0 n (by omega))) := by
  have hk := lowerExtractionCost_first_atom_lower_bound (hn := by omega) hlen hnodup
  have hdist := delayedChain_history_distance_exact hn hlen hnodup
    (site0 n (by omega))
    (delayedChain_attainable hn hlen hnodup (site0 n (by omega)))
  have hendpoint : endpointDistance n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (endpoint_attainable_of_logged (by omega)
        (delayedChain_attainable hn hlen hnodup (site0 n (by omega)))) =
      2 * n - 2 := by
    exact allR_endpoint_distance_exact n hn _
  unfold historyPremium
  rw [hdist, hendpoint]
  simp only [site0, Fin.val_mk, Nat.add_zero]
  omega

/-- The cyclic descending order beginning at any atom attains the directed
first-atom premium bound exactly. -/
theorem firstAtomDescending_delayedChain_premium_exact
    {n : Nat} [NeZero n] (hn : 3 ≤ n) (a : Fin n) :
    historyPremium n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (delayedUpperChainLog (firstAtomDescendingOrder n (by omega) a))
      (delayedChain_attainable hn
        (firstAtomDescendingOrder_length n (by omega) a)
        (firstAtomDescendingOrder_nodup n (by omega) a)
        (site0 n (by omega))) =
      (5 * n * (n - 1)) / 2 + (n - a.val) % n - (n - 1) := by
  have hdist := delayedChain_history_distance_exact hn
    (firstAtomDescendingOrder_length n (by omega) a)
    (firstAtomDescendingOrder_nodup n (by omega) a)
    (site0 n (by omega))
    (delayedChain_attainable hn
      (firstAtomDescendingOrder_length n (by omega) a)
      (firstAtomDescendingOrder_nodup n (by omega) a)
      (site0 n (by omega)))
  have hendpoint : endpointDistance n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (endpoint_attainable_of_logged (by omega)
        (delayedChain_attainable hn
          (firstAtomDescendingOrder_length n (by omega) a)
          (firstAtomDescendingOrder_nodup n (by omega) a)
          (site0 n (by omega)))) = 2 * n - 2 := by
    exact allR_endpoint_distance_exact n hn _
  have hk := firstAtomDescendingCost_exact n (by omega) a
  unfold historyPremium
  rw [hdist, hendpoint, hk]
  simp only [site0, Fin.val_mk, Nat.add_zero]
  omega

/-- A witnessed global lower bound, independent of any Python search. -/
theorem reverseDelayedChain_premium_le_global (n : Nat) (hn : 3 ≤ n) :
    (5 * n * (n - 1)) / 2 ≤ globalHistoryPremium n (by omega) := by
  let : NeZero n := ⟨by omega⟩
  have h := historyPremium_le_global n (by omega)
    (delayedChainEndpoint (site0 n (by omega)))
    (delayedUpperChainLog (reverseExtractionOrder n (by omega)))
    (delayedChain_attainable hn (reverseExtractionOrder_length n (by omega))
      (reverseExtractionOrder_nodup n (by omega)) (site0 n (by omega)))
  simpa only [reverseDelayedChain_history_premium_exact hn] using h

/-- The delayed chain strengthens the certified quadratic lower constant
from the original all-R witness; the existing uniform upper bound is reused. -/
theorem global_history_premium_bounds_delayed (n : Nat) (hn : 3 ≤ n) :
    (5 * n * (n - 1)) / 2 ≤ globalHistoryPremium n (by omega) ∧
      globalHistoryPremium n (by omega) ≤ 6 * n * n - 2 * n - 1 :=
  ⟨reverseDelayedChain_premium_le_global n hn,
    globalHistoryPremium_le_quadratic n (by omega)⟩

end RSR2History
