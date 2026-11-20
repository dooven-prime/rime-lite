import RSR2History.MultiRootRelativeSlack
import RSR2History.SingletonExtractionDefect

/-!
Strategy-independent signed slack for the original effective observation.
The identities below do not assert geometric nonnegativity for arbitrary
multi-root observations. The final theorem isolates the existing one-block
case, where nonnegativity already follows from singleton extraction slack.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- A signed quantity on actual observations. Its interpretation as an
extraction deficit requires the original log's full singleton order. -/
noncomputable def strategyIndependentSlack (n : Nat) (hn3 : 3 ≤ n)
    (o : AttainableObservation n (by omega)) : Int :=
  (delayedChainTotalPremiumMaximum n hn3 : Int) -
    (totalObservationPremium n (by omega) o : Int) -
    ((maxLowerExtractionCost n (by omega) : Int) -
      (lowerExtractionCost n (by omega) (singletonTransferOrder o.val.2) : Int))

namespace ForestReplayAccount
variable {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}

/-- The account's order is read from the same original log, independently
of its reservation frame, cursor schedule or terminal route. -/
theorem order_eq_original (r : ForestReplayAccount n hn Q H) :
    r.order = singletonTransferOrder H := r.grammar.order_eq.symm

theorem extractionCost_eq_original (r : ForestReplayAccount n hn Q H) :
    r.extractionCost = lowerExtractionCost n hn (singletonTransferOrder H) := by
  simp only [extractionCost, r.order_eq_original]

theorem extractionCost_eq (r s : ForestReplayAccount n hn Q H) :
    r.extractionCost = s.extractionCost := by
  rw [r.extractionCost_eq_original, s.extractionCost_eq_original]

/-- Signed geometric slack of this particular actual replay. -/
noncomputable def geometricSlack (r : ForestReplayAccount n hn Q H) : Int :=
  (r.partitionCost : Int) + packedUpperBudget n n - 3*(n : Int) +
    r.terminal.length + 2 - r.jointCharge

theorem strategyIndependentSlack_balance (r : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) :
    strategyIndependentSlack n hn3 r.observation =
      r.geometricSlack + (r.replayExcess : Int) := by
  have hs := r.relative_slack hn3
  have hk := Int.ofNat_sub r.extractionCost_le_max
  have he := r.extractionCost_eq_original
  unfold relativeBase at hs
  rw [hk] at hs
  unfold strategyIndependentSlack geometricSlack
  change (delayedChainTotalPremiumMaximum n hn3 : Int) - (r.premium : Int) -
    ((maxLowerExtractionCost n hn : Int) -
      (lowerExtractionCost n hn (singletonTransferOrder H) : Int)) = _
  rw [← he]
  omega

/-- The extraction maximum cancels. This is the signed screen computed
from the observation's exact costs, independently of any replay policy. -/
theorem strategyIndependentSlack_eq_canceled (r : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) :
    strategyIndependentSlack n hn3 r.observation =
      (5*n.choose 2 : Nat) - (n : Int) + 2 - (r.historyCost : Int) +
        (r.partitionCost : Int) + (r.extractionCost : Int) := by
  have hj := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn3
  have hj' : delayedChainTotalPremiumMaximum n hn3+n =
      maxLowerExtractionCost n hn+packedUpperBudget n n+2 := by omega
  rw [packedUpperBudget_self (by omega)] at hj'
  have hjZ := congrArg (fun x : Nat => (x : Int)) hj'
  have hpZ := congrArg (fun x : Nat => (x : Int)) r.premium_balance
  push_cast at hjZ hpZ
  change (delayedChainTotalPremiumMaximum n hn3 : Int) - (r.premium : Int) -
    ((maxLowerExtractionCost n hn : Int) -
      (lowerExtractionCost n hn (singletonTransferOrder H) : Int)) = _
  rw [← r.extractionCost_eq_original]
  omega

theorem geometricSlack_eq_strategyIndependentSlack_sub_excess
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n) :
    r.geometricSlack =
      strategyIndependentSlack n hn3 r.observation - (r.replayExcess : Int) := by
  have := r.strategyIndependentSlack_balance hn3
  omega

/-- Two actual accounts of the same observation need no additional
same-extraction-cost premise. Their grammars already force that equality. -/
theorem geometricSlack_compensation (r s : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) :
    r.geometricSlack - s.geometricSlack =
      (s.replayExcess : Int) - (r.replayExcess : Int) := by
  have hr := r.strategyIndependentSlack_balance hn3
  have hs := s.strategyIndependentSlack_balance hn3
  have ho : strategyIndependentSlack n hn3 r.observation =
      strategyIndependentSlack n hn3 s.observation := rfl
  omega

theorem geometricSlack_le_strategyIndependentSlack
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n) :
    r.geometricSlack ≤ strategyIndependentSlack n hn3 r.observation := by
  have := r.strategyIndependentSlack_balance hn3
  omega

theorem geometricSlack_nonneg_iff (r : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) :
    0 ≤ r.geometricSlack ↔
      (r.replayExcess : Int) ≤ strategyIndependentSlack n hn3 r.observation := by
  rw [r.geometricSlack_eq_strategyIndependentSlack_sub_excess hn3]
  omega

theorem geometricSlack_negative_of_strategyIndependentSlack_negative
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (hneg : strategyIndependentSlack n hn3 r.observation < 0) :
    r.geometricSlack < 0 := by
  have := r.geometricSlack_le_strategyIndependentSlack hn3
  omega

theorem replayExcess_eq_zero_iff (r : ForestReplayAccount n hn Q H) :
    r.replayExcess = 0 ↔ r.word.length = r.historyCost := by
  have := r.replayExcess_balance
  omega

theorem geometricSlack_eq_strategyIndependentSlack_iff
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n) :
    r.geometricSlack = strategyIndependentSlack n hn3 r.observation ↔
      r.word.length = r.historyCost := by
  have hs := r.strategyIndependentSlack_balance hn3
  rw [← r.replayExcess_eq_zero_iff]
  omega

/-- An optimal replay maximizes geometry among all accounts for the same
observation. This does not claim that every observation has an optimal
account in this particular family. -/
theorem geometricSlack_maximal_of_optimal (r s : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) (hopt : r.word.length = r.historyCost) :
    s.geometricSlack ≤ r.geometricSlack := by
  have hr := (r.geometricSlack_eq_strategyIndependentSlack_iff hn3).mpr hopt
  have hs := s.geometricSlack_le_strategyIndependentSlack hn3
  have ho : strategyIndependentSlack n hn3 r.observation =
      strategyIndependentSlack n hn3 s.observation := rfl
  omega

/-- On one-block observations the original tree and cursor defects already
supply an all-parameter lower bound for the strategy-independent slack. -/
theorem singleBlock_strategyIndependentSlack_defects
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    ∃ T : UpperFusionTree n, UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      (T.leftBranchDefect : Int) + (T.initialCursorSlack : Int) ≤
        strategyIndependentSlack n hn3 r.observation := by
  have : NeZero n := ⟨by omega⟩
  have ht : logTransferCount H = n :=
    r.grammar.transfer_count.symm.trans r.full_order
  obtain ⟨T, trace, hs⟩ := singleBlock_nTransfer_extraction_slack
    hn3 r.word r.actual_run hblocks ht
  have hk := r.extractionCost_le_max
  rw [r.extractionCost_eq_original] at hk
  have hdef := Int.ofNat_sub hk
  refine ⟨T, trace, ?_⟩
  have hnat : r.premium + T.leftBranchDefect + T.initialCursorSlack +
      (maxLowerExtractionCost n hn - lowerExtractionCost n hn (singletonTransferOrder H)) ≤
        delayedChainTotalPremiumMaximum n hn3 := hs
  have hz : (r.premium : Int) + T.leftBranchDefect + T.initialCursorSlack +
      ((maxLowerExtractionCost n hn - lowerExtractionCost n hn (singletonTransferOrder H) : Nat) : Int) ≤
        (delayedChainTotalPremiumMaximum n hn3 : Int) := by exact_mod_cast hnat
  change (T.leftBranchDefect : Int) + (T.initialCursorSlack : Int) ≤
    (delayedChainTotalPremiumMaximum n hn3 : Int) - (r.premium : Int) -
      ((maxLowerExtractionCost n hn : Int) -
        (lowerExtractionCost n hn (singletonTransferOrder H) : Int))
  omega

/-- The one-root part of the all-observation screen is already controlled
for every n. The remaining nonnegativity question is multi-root. -/
theorem singleBlock_strategyIndependentSlack_nonneg
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    0 ≤ strategyIndependentSlack n hn3 r.observation := by
  obtain ⟨T, _, hs⟩ := r.singleBlock_strategyIndependentSlack_defects hn3 hblocks
  omega

end ForestReplayAccount

/-- Raw successful histories in the one-root part of the census inherit
the sign result without supplying a replay account as an extra premise. -/
theorem allUpper_singleton_singleBlock_strategyIndependentSlack_nonneg
    {n : Nat} [NeZero n] (hn3 : 3 ≤ n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (run : runLogged n (by omega) (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    0 ≤ strategyIndependentSlack n hn3 ⟨(Q,H),⟨word,run⟩⟩ := by
  obtain ⟨r⟩ := allUpper_singleton_forest_account (by omega) word run upper singletons
  exact r.singleBlock_strategyIndependentSlack_nonneg hn3 hblocks

end RSR2History
