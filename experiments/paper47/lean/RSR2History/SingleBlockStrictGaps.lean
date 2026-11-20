import RSR2History.SingleBlockOneTransfer

/-! Algebraic refinement of the delayed-family comparison; no new routing. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

theorem choose_two_le_maxLowerExtractionCost (n : Nat) (hn : 1 < n) :
    n.choose 2 ≤ maxLowerExtractionCost n hn := by
  have hj := josephusExtractionCost_lower_bound n hn
  have hk := lowerExtractionCost_le_max (hn := hn)
    (josephusExtractionOrder_length n) (josephusExtractionOrder_nodup n)
  rw [Nat.choose_two_right]
  omega

noncomputable def extractionExcess (n : Nat) (hn : 1 < n) : Nat :=
  maxLowerExtractionCost n hn - n.choose 2

theorem delayedMaximum_extractionExcess_balance (n : Nat) (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn + 4*n =
      3*n^2 + extractionExcess n (by omega) + 2 := by
  have hk := Nat.sub_add_cancel (choose_two_le_maxLowerExtractionCost n (by omega))
  change extractionExcess n (by omega) + n.choose 2 = _ at hk
  obtain ⟨k, heven⟩ := Nat.even_mul_pred_self n
  have htri : 2*(n.choose 2) = n*(n-1) := by
    rw [Nat.choose_two_right]
    omega
  have hfive : 5*n*(n-1) = 10*(n.choose 2) := by nlinarith
  have hdiv : (5*n*(n-1))/2 = 5*(n.choose 2) := by rw [hfive]; omega
  have hn1 := Nat.sub_add_cancel (show 1 ≤ n by omega)
  have hbase : n ≤ (5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) := by
    rw [hdiv]
    nlinarith
  have hsub := Nat.sub_add_cancel hbase
  rw [delayedChainTotalPremiumMaximum_eq, hdiv]
  rw [hdiv] at hsub
  nlinarith

theorem singleBlock_noTransfer_delayed_gap_sharp
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 0) :
    4*n-4 + extractionExcess n (by omega) ≤
      delayedChainTotalPremiumMaximum n hn -
        totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ := by
  have hb := singleBlock_noTransfer_totalPremium_bound hn word hexec hblocks ht
  have he := delayedMaximum_extractionExcess_balance n hn
  have hbig : 8*n ≤ 3*n^2 := by nlinarith
  have hs := Nat.sub_add_cancel hbig
  omega

theorem singleBlock_oneTransfer_delayed_gap_sharp
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 1) :
    4*n-5 + extractionExcess n (by omega) ≤
      delayedChainTotalPremiumMaximum n hn -
        totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ := by
  have hb := singleBlock_oneTransfer_totalPremium_bound hn word hexec hblocks ht
  have he := delayedMaximum_extractionExcess_balance n hn
  have hbig : 8*n ≤ 3*n^2 := by nlinarith
  have hs := Nat.sub_add_cancel hbig
  omega

end RSR2History
