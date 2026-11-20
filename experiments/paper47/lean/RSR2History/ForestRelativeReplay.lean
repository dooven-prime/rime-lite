import RSR2History.ForestWindingReplay
import RSR2History.ForestFullRankReplay
import RSR2History.SingletonExtractionDefect

/-! Partition-relative domination for the all-upper singleton-transfer class. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- Every actual multi-root observation in the all-upper singleton class
admits a replay that retains the extraction deficit in its length budget. -/
theorem allUpper_singleton_multiRoot_delayed_replay
    {n : Nat} [NeZero n] (hn3 : 3 ≤ n) (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (hr : 2 ≤ (unorderedPacketBlocks n Q).card) :
    ∃ replay, runLogged n hn (seed n) replay = some (Q,H) ∧
      replay.length + (maxLowerExtractionCost n hn -
        lowerExtractionCost n hn (singletonTransferOrder H)) ≤
        partitionDistance n hn (unorderedPacketBlocks n Q)
          (partition_attainable_of_endpoint n hn Q (endpoint_attainable_of_logged hn ⟨word,run⟩)) +
          delayedChainTotalPremiumMaximum n hn3 := by
  obtain ⟨base⟩ := allUpper_singleton_forest_account hn word run upper singletons
  by_cases hfull : base.terminal.length = n
  · obtain ⟨account, hterm, _, _, hfinish⟩ :=
      forest_full_rank_account_of_trace hn word run upper singletons base.trace hfull
    have hlen := account.replay_length_lt_delayed_of_full_rank hn3 (by rwa [hterm]) hfinish
    rw [account.grammar.order_eq]
    change ∃ replay, runLogged n hn (seed n) replay = some (Q,H) ∧
      replay.length + (maxLowerExtractionCost n hn - account.extractionCost) ≤
        account.partitionCost + delayedChainTotalPremiumMaximum n hn3
    exact ⟨account.word,account.actual_run,by omega⟩
  · have hfuse : (unorderedPacketBlocks n Q).card < n := by
      rw [base.partition_block_count]
      have hb := base.rank_le
      omega
    obtain ⟨account, _, hlen⟩ :=
      allUpper_singleton_fused_forest_delayed_replay hn3 hn word run upper singletons hr hfuse
    rw [account.grammar.order_eq]
    change ∃ replay, runLogged n hn (seed n) replay = some (Q,H) ∧
      replay.length + (maxLowerExtractionCost n hn - account.extractionCost) ≤
        account.partitionCost + delayedChainTotalPremiumMaximum n hn3
    exact ⟨account.word,account.actual_run,by omega⟩

/-- The strategy-independent slack is nonnegative for every realizable
all-upper singleton-transfer observation, across all terminal ranks. -/
theorem allUpper_singleton_extraction_slack
    {n : Nat} [NeZero n] (hn3 : 3 ≤ n) (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1) :
    totalObservationPremium n hn ⟨(Q,H),⟨word,run⟩⟩ +
      (maxLowerExtractionCost n hn - lowerExtractionCost n hn (singletonTransferOrder H)) ≤
        delayedChainTotalPremiumMaximum n hn3 := by
  by_cases hr : 2 ≤ (unorderedPacketBlocks n Q).card
  · obtain ⟨replay, hr, hlen⟩ :=
      allUpper_singleton_multiRoot_delayed_replay hn3 hn word run upper singletons hr
    have he : ∃ w, runLogged n hn (seed n) w = some (Q,H) := ⟨word,run⟩
    have hmin := minimumWordLength_le _ he hr
    change historyDistance n hn Q H he ≤ replay.length at hmin
    have hdist := observationDistance_chain n hn Q H he
    change historyDistance n hn Q H he -
      partitionDistance n hn (unorderedPacketBlocks n Q)
        (partition_attainable_of_endpoint n hn Q (endpoint_attainable_of_logged hn he)) +
      (maxLowerExtractionCost n hn - lowerExtractionCost n hn (singletonTransferOrder H)) ≤
        delayedChainTotalPremiumMaximum n hn3
    omega
  · have hm (a : Fin n) :
        Finset.univ.filter (fun b => Q b = Q a) ∈ unorderedPacketBlocks n Q :=
      Finset.mem_image.mpr ⟨a,Finset.mem_univ _,rfl⟩
    have hp : 0 < (unorderedPacketBlocks n Q).card :=
      Finset.card_pos.mpr ⟨_,hm ⟨0,by omega⟩⟩
    obtain ⟨B,hB⟩ := Finset.card_eq_one.mp (show (unorderedPacketBlocks n Q).card = 1 by omega)
    have huniv : B = Finset.univ := by
      apply Finset.eq_univ_of_forall
      intro a
      have ha := hm a
      rw [hB, Finset.mem_singleton] at ha
      rw [← ha]
      simp
    have hsingle : unorderedPacketBlocks n Q = {Finset.univ} := by simpa [huniv] using hB
    obtain ⟨base⟩ := allUpper_singleton_forest_account hn word run upper singletons
    have ht : logTransferCount H = n := base.grammar.transfer_count.symm.trans base.full_order
    obtain ⟨T, trace, hs⟩ := singleBlock_nTransfer_extraction_slack hn3 word run hsingle ht
    omega

end RSR2History
