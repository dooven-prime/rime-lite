import RSR2History.JosephusExtraction
import RSR2History.ReverseDelayedChainPremium

/-!
The explicit second-live extraction family raises the certified leading
lower coefficient of global history premium from 5/2 to 3. Its history
and endpoint use exactly the existing delayed-chain execution contract.
No global optimality of this family is asserted.
-/

namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- The same cheap upper full-packet endpoint now admits an explicit
history with premium at least `(n-1)*(3*n-2)`. -/
theorem josephusDelayedChain_premium_lower_bound
    {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    (n - 1) * (3 * n - 2) ≤
      historyPremium n (by omega)
        (delayedChainEndpoint (site0 n (by omega)))
        (delayedUpperChainLog (josephusExtractionOrder n))
        (delayedChain_attainable hn (josephusExtractionOrder_length n)
          (josephusExtractionOrder_nodup n) (site0 n (by omega))) := by
  have attain := delayedChain_attainable hn (josephusExtractionOrder_length n)
    (josephusExtractionOrder_nodup n) (site0 n (by omega))
  have hbalance := historyPremium_balance n (by omega)
    (delayedChainEndpoint (site0 n (by omega)))
    (delayedUpperChainLog (josephusExtractionOrder n)) attain
  have hdist := delayedChain_history_distance_exact hn
    (josephusExtractionOrder_length n) (josephusExtractionOrder_nodup n)
    (site0 n (by omega)) attain
  have hendpoint : endpointDistance n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (endpoint_attainable_of_logged (by omega) attain) = 2 * n - 2 :=
    allR_endpoint_distance_exact n hn _
  rw [hdist, hendpoint] at hbalance
  simp only [site0, Fin.val_mk, Nat.add_zero] at hbalance
  have hk := josephusExtractionCost_lower_bound n (by omega)
  have hprod : 2 ∣ 5 * n * (n - 1) := by
    rw [show 5 * n * (n - 1) = 5 * (n * (n - 1)) by ring]
    exact dvd_mul_of_dvd_right n.even_mul_pred_self.two_dvd 5
  have hhalf : 2 * (5 * n * (n - 1) / 2) = 5 * n * (n - 1) :=
    Nat.mul_div_cancel' hprod
  have htarget : (n - 1) * (3 * n - 2) + (2 * n - 2) = 3 * n * (n - 1) := by
    let r := n - 1
    have hn' : n = r + 1 := by dsimp [r]; omega
    change r * (3 * n - 2) + (2 * n - 2) = 3 * n * r
    rw [hn']
    rw [show 3 * (r + 1) - 2 = 3 * r + 1 by omega,
      show 2 * (r + 1) - 2 = 2 * r by omega]
    ring
  let premium := historyPremium n (by omega)
    (delayedChainEndpoint (site0 n (by omega)))
    (delayedUpperChainLog (josephusExtractionOrder n)) attain
  change (2 * n - 2) + premium =
    lowerExtractionCost n (by omega) (josephusExtractionOrder n) +
      (5 * n * (n - 1)) / 2 at hbalance
  change (n - 1) * (3 * n - 2) ≤ premium
  nlinarith only [hbalance, hk, hhalf, htarget]

theorem josephusDelayedChain_premium_le_global (n : Nat) (hn : 3 ≤ n) :
    (n - 1) * (3 * n - 2) ≤ globalHistoryPremium n (by omega) := by
  let : NeZero n := ⟨by omega⟩
  exact (josephusDelayedChain_premium_lower_bound hn).trans
    (historyPremium_le_global n (by omega)
      (delayedChainEndpoint (site0 n (by omega)))
      (delayedUpperChainLog (josephusExtractionOrder n))
      (delayedChain_attainable hn (josephusExtractionOrder_length n)
        (josephusExtractionOrder_nodup n) (site0 n (by omega))))

/-- Both independent lower witnesses are retained: the reverse sweep is
stronger at n=3, while the Josephus family improves the leading coefficient. -/
theorem global_history_premium_bounds_josephus (n : Nat) (hn : 3 ≤ n) :
    max ((5 * n * (n - 1)) / 2) ((n - 1) * (3 * n - 2)) ≤
        globalHistoryPremium n (by omega) ∧
      globalHistoryPremium n (by omega) ≤ 6 * n * n - 2 * n - 1 :=
  ⟨max_le (reverseDelayedChain_premium_le_global n hn)
      (josephusDelayedChain_premium_le_global n hn),
    globalHistoryPremium_le_quadratic n (by omega)⟩

end RSR2History
