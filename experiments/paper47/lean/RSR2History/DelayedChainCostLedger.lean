import RSR2History.LowerExtractionProjection
import RSR2History.UpperLoadingWindow
import RSR2History.EventResourceLedger
import RSR2History.AllRTransferBridge

/-!
Non-overlapping cost accounting for the delayed upper-chain contract. This
module stops before the all-R suffix bridge: it combines the actual lower
extraction projection, the loading-window upper-rotation barrier, and the
event-letter counts into a first unconditional raw-word lower bound.
-/

namespace RSR2History
open RSR2.Parametric

@[simp] theorem singletonTransferLog_transfer_count
    (z : List (Fin n)) :
    logTransferCount (singletonTransferLog z) = z.length := by
  induction z with
  | nil => simp [singletonTransferLog, logTransferCount]
  | cons a rest ih =>
      simp only [singletonTransferLog, logTransferCount, List.map_cons,
        List.sum_cons]
      change 1 + logTransferCount (singletonTransferLog rest) = rest.length + 1
      rw [ih]
      omega

@[simp] theorem singletonTransferLog_upper_fusion_count
    (z : List (Fin n)) :
    logLayerFusionCount true (singletonTransferLog z) = 0 := by
  induction z with
  | nil => simp [singletonTransferLog, logLayerFusionCount]
  | cons a rest ih =>
      simp only [singletonTransferLog, logLayerFusionCount, List.map_cons,
        List.sum_cons]
      change 0 + logLayerFusionCount true (singletonTransferLog rest) = 0
      simpa only [Nat.zero_add] using ih

@[simp] theorem orderedUpperFusionLog_transfer_count
    (carrier : Finset (Fin n)) (z : List (Fin n)) :
    logTransferCount (orderedUpperFusionLog carrier z) = 0 := by
  induction z generalizing carrier with
  | nil => rfl
  | cons a rest ih =>
      simpa only [orderedUpperFusionLog, logTransferCount, List.map_cons,
        List.sum_cons, Nat.zero_add] using ih (carrier ∪ {a})

@[simp] theorem orderedUpperFusionLog_upper_fusion_count
    (carrier : Finset (Fin n)) (z : List (Fin n)) :
    logLayerFusionCount true (orderedUpperFusionLog carrier z) = z.length := by
  induction z generalizing carrier with
  | nil => simp [orderedUpperFusionLog, logLayerFusionCount]
  | cons a rest ih =>
      simp only [orderedUpperFusionLog, logLayerFusionCount, List.map_cons,
        List.sum_cons]
      change 1 + logLayerFusionCount true
        (orderedUpperFusionLog (carrier ∪ {a}) rest) = rest.length + 1
      rw [ih]
      omega

theorem delayedUpperFusionLog_upper_fusion_count
    (z : List (Fin n)) :
    logLayerFusionCount true (delayedUpperFusionLog z) = z.length - 1 := by
  cases z with
  | nil => rfl
  | cons a rest =>
      simp [delayedUpperFusionLog]

@[simp] theorem delayedUpperChainLog_transfer_count
    (z : List (Fin n)) :
    logTransferCount (delayedUpperChainLog z) = z.length := by
  rw [delayedUpperChainLog, logTransferCount_append,
    singletonTransferLog_transfer_count]
  cases z with
  | nil => simp [delayedUpperFusionLog, logTransferCount]
  | cons a rest => simp [delayedUpperFusionLog]

@[simp] theorem delayedUpperChainLog_upper_fusion_count
    (z : List (Fin n)) :
    logLayerFusionCount true (delayedUpperChainLog z) = z.length - 1 := by
  rw [delayedUpperChainLog, logLayerFusionCount_append,
    singletonTransferLog_upper_fusion_count, delayedUpperFusionLog_upper_fusion_count]
  omega

private theorem emitted_upper_fusion_count_le (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logLayerFusionCount true (emittedEvents n hn P letter) ≤
      if letter = .d true then 1 else 0 := by
  cases letter with
  | p layer => simp [emittedEvents, logLayerFusionCount]
  | d layer =>
      cases layer with
      | false =>
          simp only [emittedEvents]
          split <;> simp [logLayerFusionCount]
      | true =>
          simp only [emittedEvents]
          split <;> simp [logLayerFusionCount]
  | v => simp [emittedEvents, logLayerFusionCount]

theorem runLogged_upper_fusion_count_le_d (n : Nat) (hn : 1 < n)
    (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    logLayerFusionCount true events ≤ word.count (.d true) := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.2, logLayerFusionCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              have hi := ih (by simpa [he.1] using hr)
              have hemit := emitted_upper_fusion_count_le n hn P letter
              rw [← he.2, logLayerFusionCount_append]
              have hc : (letter :: rest).count (.d true) =
                  (if letter = .d true then 1 else 0) + rest.count (.d true) := by
                cases letter with
                | p layer => cases layer <;> simp
                | d layer => cases layer <;> simp [Nat.add_comm]
                | v => simp
              rw [hc]
              omega

theorem raw_letter_count_partition (word : List Letter) :
    word.length = word.count (.p false) + word.count (.p true) +
      word.count (.d false) + word.count (.d true) + word.count .v := by
  induction word with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p layer => cases layer <;> simp [List.length_cons, ih] <;> omega
      | d layer => cases layer <;> simp [List.length_cons, ih] <;> omega
      | v => simp [List.length_cons, ih]; omega

theorem delayedChain_raw_length_lower_bound
    {n : Nat} {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup)
    {word : List Letter} {Q : Placement n}
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hexec : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog z)) :
    lowerExtractionCost n hn z + n * n + n - 1 ≤ word.length := by
  cases z with
  | nil =>
      have hn0 : n = 0 := by simpa using hlen.symm
      omega
  | cons a rest =>
      cases rest with
      | nil =>
          have hn1 : n = 1 := by simpa using hlen.symm
          omega
      | cons b tail =>
          have hk := delayedChain_lowerExtractionCost_lower_bound n hn
            (a :: b :: tail) hlen hnodup hexec
          have hp := delayedChain_raw_rotations_lower_bound hlen hnodup terminal hexec
          have hv := AllRTransfer.runLogged_transfer_count n hn hexec
          rw [delayedUpperChainLog_transfer_count, hlen] at hv
          have hd := runLogged_upper_fusion_count_le_d n hn word hexec
          rw [delayedUpperChainLog_upper_fusion_count, hlen] at hd
          have hc : word.count (.p false) + word.count (.d false) +
              word.count (.p true) + word.count (.d true) + word.count .v = word.length := by
            rw [raw_letter_count_partition]
            omega
          have hprod : n * (n - 1) + n = n * n := by
            have he := congrArg (n * ·) (show n - 1 + 1 = n by omega)
            simpa only [Nat.mul_add, Nat.mul_one] using he
          omega

/-- The disjoint-count checkpoint used before the all-R suffix bridge. -/
theorem delayedChain_combined_cost_lower_bound
    {n : Nat} {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup)
    {word : List Letter} {Q : Placement n}
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hexec : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog z)) :
    lowerExtractionCost n hn z + n * (n - 1) + (n - 1) + n ≤ word.length := by
  have h := delayedChain_raw_length_lower_bound hlen hnodup terminal hexec
  have hprod : n * (n - 1) + n = n * n := by
    have he := congrArg (n * ·) (show n - 1 + 1 = n by omega)
    simpa only [Nat.mul_add, Nat.mul_one] using he
  omega

end RSR2History
