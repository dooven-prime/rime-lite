import RSR2History.PhaseFreeFusion
import RSR2History.KSensitivePremium
import RSR2History.SingleBlockTransferStructure
import RSR2History.DelayedFamilyPremium

/-! A first relative-cost bound for one-block histories with no transfers.
The phase-free fusion replay carries residual cyclic phase between events. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

private theorem fusionOnly_of_noTransfers (events : List (EffectiveEvent n))
    (hzero : logTransferCount events = 0) :
    (∀ e ∈ events, ∃ layer A B C, e = .fusion layer A B C) ∧
      logFusionCount events = events.length := by
  induction events with
  | nil => simp [logFusionCount]
  | cons event rest ih =>
      cases event with
      | fusion layer A B C =>
          have hz : logTransferCount rest = 0 := by
            simpa [logTransferCount] using hzero
          obtain ⟨hr, hcount⟩ := ih hz
          constructor
          · intro e he
            simp only [List.mem_cons] at he
            rcases he with rfl | he
            · exact ⟨layer, A, B, C, rfl⟩
            · exact hr e he
          · change 1 + logFusionCount rest = (EffectiveEvent.fusion layer A B C :: rest).length
            rw [hcount]
            rw [List.length_cons]
            omega
      | transfer packet =>
          simp [logTransferCount] at hzero

private theorem oneBlock_totalPacketCount
    (n : Nat) (hn : 0 < n) (Q : Placement n)
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    totalPacketCount Q = 1 := by
  obtain ⟨coord, hQ⟩ := (unorderedPacketBlocks_eq_singleBlock_iff n hn Q).mp hblocks
  have hcount : totalPacketCount (fun _ : Fin n => coord) = 1 := by
    apply totalPacketCount_eq_representatives_length _ [coord] (by simp)
    intro loc
    simp only [List.mem_singleton]
    constructor
    · intro h
      exact ⟨site0 n hn, h.symm⟩
    · rintro ⟨_, h⟩
      exact h.symm
  rw [hQ]
  exact hcount

private theorem rank_one_silentBudget
    (n : Nat) (_hn : 1 < n) (Q : Placement n)
    (hcount : totalPacketCount Q = 1) :
    silentBudget n Q = n-1 := by
  have hrank : layerRank Q false + layerRank Q true = 1 := by
    rw [layerRank_lower, layerRank_upper]
    exact hcount
  have h0 : layerRank Q false = 0 ∨ layerRank Q false = 1 := by omega
  rcases h0 with h0 | h0
  · have h1 : layerRank Q true = 1 := by omega
    rw [← rankBudget_layerRanks]
    change layerBudget n (layerRank Q false) + layerBudget n (layerRank Q true) = n-1
    rw [h0, h1]
    simp [layerBudget]
  · have h1 : layerRank Q true = 0 := by omega
    rw [← rankBudget_layerRanks]
    change layerBudget n (layerRank Q false) + layerBudget n (layerRank Q true) = n-1
    rw [h0, h1]
    simp [layerBudget]

private theorem extraction_max_lower (n : Nat) (hn : 1 < n) :
    n*(n-1) ≤ 2*maxLowerExtractionCost n hn := by
  have hj := josephusExtractionCost_lower_bound n hn
  have hk := lowerExtractionCost_le_max (hn := hn)
    (josephusExtractionOrder_length n) (josephusExtractionOrder_nodup n)
  omega

theorem delayedChainTotalPremiumMaximum_lower_bound
    (n : Nat) (hn : 3 ≤ n) :
    3*(n-1)^2 ≤ delayedChainTotalPremiumMaximum n hn := by
  rw [delayedChainTotalPremiumMaximum_eq n hn]
  let x := n*(n-1)
  have hx : x ≤ 2*maxLowerExtractionCost n (by omega) :=
    extraction_max_lower n (by omega)
  have hdiv : 5*n*(n-1) ≤ 2*((5*n*(n-1))/2)+1 := by omega
  have hx' : n*(n-1) ≤ 2*maxLowerExtractionCost n (by omega) := by
    simpa [x] using hx
  have htwice :
      2*(3*(n-1)^2+n) ≤
        2*((5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) + 2) := by
    have hsub : n-1+1=n := Nat.sub_add_cancel (by omega)
    nlinarith [hdiv, hx', hsub]
  have hsum : 3*(n-1)^2+n ≤
      (5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) + 2 := by
    omega
  omega

/-- A transfer-free one-block log has a short same-log, literal-endpoint
replay. From the singleton seed the upper layer stays empty. -/
theorem singleBlock_noTransfer_historyDistance_le
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (htransfers : logTransferCount events = 0) :
    historyDistance n (by omega) Q events ⟨word, hexec⟩ ≤ 3*(n-1)^2 := by
  have hcount := oneBlock_totalPacketCount n (by omega) Q hblocks
  obtain ⟨hfusion, hfusionCount⟩ := fusionOnly_of_noTransfers events htransfers
  have hbalance := (runLogged_resource_balance n (by omega) word hexec).1
  rw [hcount, seed_totalPacketCount] at hbalance
  have hlenEvents : events.length = n-1 := by omega
  let path := runLogged_cyclicEventPath n (by omega) word hexec
  obtain ⟨R, replay, hreplay, hsame, hreplayLen⟩ :=
    CyclicEventPath.phaseFree_fusion_replay (n := n) (hn := by omega)
      path (by
        intro e he
        exact hfusion e he)
  obtain ⟨align, halign, halignLen⟩ :=
    silent_preparation_short n (by omega) R Q hsame
  have hroute : runLogged n (by omega) (seed n) (replay ++ align) =
      some (Q, events) := by
    simp [runLogged_append, hreplay, halign]
  have hQcount := hcount
  have hRcount : totalPacketCount R = 1 := by
    have hranks := hsame.ranks_eq
    have hsum : layerRank R false + layerRank R true =
        layerRank Q false + layerRank Q true := by
      have h := congrArg (fun ranks : Nat × Nat => ranks.1 + ranks.2) hranks
      simpa [layerRanks] using h
    have hsumQ : layerRank Q false + layerRank Q true = 1 := by
      rw [layerRank_lower, layerRank_upper]
      exact hQcount
    have hsumR : layerRank R false + layerRank R true = 1 := hsum.trans hsumQ
    unfold totalPacketCount
    rw [← layerRank_lower, ← layerRank_upper]
    exact hsumR
  have hbudget := rank_one_silentBudget n (by omega) R hRcount
  have hdist : historyDistance n (by omega) Q events ⟨word, hexec⟩ ≤
      (replay ++ align).length :=
    minimumWordLength_le _ ⟨word, hexec⟩ hroute
  rw [hlenEvents] at hreplayLen
  have hrouteLen' : (replay ++ align).length ≤ 3*(n-1)^2 := by
    rw [List.length_append]
    calc
      replay.length + align.length ≤ (3*n-4)*(n-1)+(n-1) :=
        Nat.add_le_add hreplayLen (by rw [hbudget] at halignLen; exact halignLen)
      _ = 3*(n-1)^2 := by
        have hn4 : 4 ≤ 3*n := by omega
        have hsub4 : 3*n-4+4=3*n := Nat.sub_add_cancel hn4
        have hsub1 : n-1+1=n := Nat.sub_add_cancel (by omega)
        nlinarith [hsub4, hsub1]
  exact hdist.trans hrouteLen'

/-- Preserve the earlier non-strict interface as a consequence. -/
theorem singleBlock_noTransfer_totalPremium_le_delayed
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (htransfers : logTransferCount events = 0) :
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ ≤
      delayedChainTotalPremiumMaximum n hn := by
  have hcost := (singleBlock_noTransfer_historyDistance_le hn word hexec hblocks htransfers).trans
    (delayedChainTotalPremiumMaximum_lower_bound n hn)
  unfold totalObservationPremium
  exact (Nat.sub_le _ _).trans hcost

theorem singleBlock_closed_premium_budget (n : Nat) (hn : 3 ≤ n) (extra : Nat) :
    (3*n^2-8*n+6+extra)+(2*n-3) = 3*(n-1)^2+extra := by
  have hbig : 8*n ≤ 3*n^2 := by
    have hm := Nat.mul_le_mul_left n hn
    nlinarith
  have hp := Nat.sub_add_cancel hbig
  have hb := Nat.sub_add_cancel (show 3 ≤ 2*n by omega)
  have hn1 := Nat.sub_add_cancel (show 1 ≤ n by omega)
  nlinarith

/-- Subtract the exact partition baseline, rather than dropping it. -/
theorem singleBlock_noTransfer_totalPremium_bound
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 0) :
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ ≤
      3*n^2-8*n+6 := by
  have hd := singleBlock_noTransfer_historyDistance_le hn word hexec hblocks ht
  have he := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hb := singleBlock_closed_premium_budget n hn 0
  omega

/-- Quantitative strict exclusion from the attained delayed-family maximum. -/
theorem singleBlock_noTransfer_delayed_gap
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 0) :
    2*n-3 ≤ delayedChainTotalPremiumMaximum n hn -
      totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ ∧
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ <
      delayedChainTotalPremiumMaximum n hn := by
  have hd := singleBlock_noTransfer_historyDistance_le hn word hexec hblocks ht
  have he := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hb := delayedChainTotalPremiumMaximum_lower_bound n hn
  constructor <;> omega

theorem singleBlock_noTransfer_not_global_maximizer
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 0) :
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ <
      globalTotalObservationPremium n (by omega) :=
  (singleBlock_noTransfer_delayed_gap hn word hexec hblocks ht).2.trans_le
    (delayedChainTotalPremiumMaximum_le_global hn)

end RSR2History
