import RSR2History.ForestCrossDefect
import RSR2History.PackedLowerAmortization

namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- A proof record for the existing three-part actual replay; it adds no
state fields or operations to the physical executor. -/
structure ForestReplayAccount (n : Nat) (hn : 1 < n)
    (Q : Placement n) (H : List (EffectiveEvent n)) where
  order : List (Fin n)
  terminal : List (UpperFusionTree n)
  site : Nat → Fin n
  finalCursor : Fin n
  intermediate : Placement n
  replayWord : List Letter
  finish : List Letter
  schedule : UpperCursorSchedule site 0 [] (site 0) H n terminal finalCursor
  grammar : SingletonUpperLog H order
  full_order : order.length = n
  nodup : order.Nodup
  trace : UpperForestTrace (seed n) 0 [] H Q n terminal
  prefix_run : runLogged n hn (seed n) replayWord = some (intermediate,H)
  finish_run : runLogged n hn intermediate finish = some (Q,[])
  length_eq : (replayWord++finish).length = lowerExtractionCost n hn order +
    schedule.cost + finish.length
  terminal_bound : finish.length ≤ layerBudget n terminal.length

theorem allUpper_singleton_forest_account {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1) :
    Nonempty (ForestReplayAccount n hn Q H) := by
  obtain ⟨z,terminal,site,cf,R,u,v,s,grammar,hlen,hnd,trace,hu,hv,_,he,hb⟩ :=
    allUpper_singleton_forest_replay hn word run upper singletons
  exact ⟨⟨z,terminal,site,cf,R,u,v,s,grammar,hlen,hnd,trace,hu,hv,he,hb⟩⟩

namespace ForestReplayAccount
variable {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}

def word (r : ForestReplayAccount n hn Q H) := r.replayWord++r.finish

theorem actual_run (r : ForestReplayAccount n hn Q H) :
    runLogged n hn (seed n) r.word = some (Q,H) := by
  simp [word, runLogged_append, r.prefix_run, r.finish_run]

def observation (r : ForestReplayAccount n hn Q H) : AttainableObservation n hn :=
  ⟨(Q,H), ⟨r.word,r.actual_run⟩⟩

noncomputable def historyCost (r : ForestReplayAccount n hn Q H) : Nat :=
  historyDistance n hn Q H r.observation.property

noncomputable def partitionCost (r : ForestReplayAccount n hn Q H) : Nat :=
  partitionDistance n hn (unorderedPacketBlocks n Q)
    (partition_attainable_of_endpoint n hn Q
      (endpoint_attainable_of_logged hn r.observation.property))

noncomputable def premium (r : ForestReplayAccount n hn Q H) : Nat :=
  totalObservationPremium n hn r.observation

noncomputable def extractionCost (r : ForestReplayAccount n hn Q H) : Nat :=
  lowerExtractionCost n hn r.order

noncomputable def replayExcess (r : ForestReplayAccount n hn Q H) : Nat :=
  r.word.length-r.historyCost

def jointCharge (r : ForestReplayAccount n hn Q H) : Int :=
  (n : Int)*r.schedule.windings + r.finish.length - r.finalCursor.val +
    (r.site 0).val + forestGapDebt r.terminal

def defectJointCharge (r : ForestReplayAccount n hn Q H) : Int :=
  (n : Int)*r.schedule.windings + r.finish.length - r.finalCursor.val +
    (r.site 0).val + (n-r.terminal.length).choose 2

noncomputable def relativeBase (r : ForestReplayAccount n hn Q H) : Int :=
  ((maxLowerExtractionCost n hn-r.extractionCost : Nat) : Int) +
    r.partitionCost + packedUpperBudget n n - 3*(n : Int) + r.terminal.length + 2

theorem historyCost_le_word (r : ForestReplayAccount n hn Q H) :
    r.historyCost ≤ r.word.length :=
  minimumWordLength_le _ r.observation.property r.actual_run

theorem premium_balance (r : ForestReplayAccount n hn Q H) :
    r.premium+r.partitionCost = r.historyCost := by
  have h := observationDistance_chain n hn Q H r.observation.property
  exact Nat.sub_add_cancel (h.1.trans h.2)

theorem replayExcess_balance (r : ForestReplayAccount n hn Q H) :
    r.replayExcess+r.historyCost = r.word.length :=
  Nat.sub_add_cancel r.historyCost_le_word

theorem extractionCost_le_max (r : ForestReplayAccount n hn Q H) :
    r.extractionCost ≤ maxLowerExtractionCost n hn :=
  lowerExtractionCost_le_max r.full_order r.nodup

theorem leaf_count (r : ForestReplayAccount n hn Q H) :
    (forestLeaves r.terminal).length = n := by
  simpa using (r.trace.toPath.complete_leaves (by simp [forestLeaves])).length_eq

theorem cross_defect_account (r : ForestReplayAccount n hn Q H) :
    forestGapDebt r.terminal + (r.terminal.map UpperFusionTree.leftBranchDefect).sum +
      forestCrossDefect r.terminal = (n-r.terminal.length).choose 2 :=
  forest_crossDefect_identity_of_leaf_count r.terminal r.leaf_count

/-- Exact signed slack for this actual replay, retaining its excess over the
minimum for the same full observation. All subtractions displayed here are
integer subtractions; the two natural deficits are known nonnegative. -/
theorem relative_slack (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n) :
    (delayedChainTotalPremiumMaximum n hn3 : Int) - (r.premium : Int) =
      r.relativeBase-r.jointCharge+(r.replayExcess : Int) := by
  have hj := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn3
  have hj' : delayedChainTotalPremiumMaximum n hn3+n =
      maxLowerExtractionCost n hn+packedUpperBudget n n+2 := by omega
  have hp := r.schedule.forest_payment
  have he := r.schedule.forest_event_count
  have hl := r.length_eq
  change r.word.length = r.extractionCost+r.schedule.cost+r.finish.length at hl
  have hd := r.premium_balance
  have hr := r.replayExcess_balance
  have hk := r.extractionCost_le_max
  have hgap := Int.ofNat_sub hk
  have jZ := congrArg (fun x : Nat => (x : Int)) hj'
  have pZ := congrArg (fun x : Nat => (x : Int)) hp
  have eZ := congrArg (fun x : Nat => (x : Int)) he
  have lZ := congrArg (fun x : Nat => (x : Int)) hl
  have dZ := congrArg (fun x : Nat => (x : Int)) hd
  have rZ := congrArg (fun x : Nat => (x : Int)) hr
  push_cast at jZ pZ eZ lZ dZ rZ
  unfold relativeBase jointCharge
  rw [hgap]
  omega

/-- Both within-root and cross-root defects remain as explicit positive
terms in the same relative slack account. -/
theorem relative_slack_with_cross_defect (r : ForestReplayAccount n hn Q H)
    (hn3 : 3 ≤ n) :
    (delayedChainTotalPremiumMaximum n hn3 : Int) - (r.premium : Int) =
      r.relativeBase-r.defectJointCharge +
        ((r.terminal.map UpperFusionTree.leftBranchDefect).sum : Int) +
        (forestCrossDefect r.terminal : Int) + (r.replayExcess : Int) := by
  have hs := r.relative_slack hn3
  have htree : (forestGapDebt r.terminal : Int) +
      ((r.terminal.map UpperFusionTree.leftBranchDefect).sum : Int) +
      (forestCrossDefect r.terminal : Int) = ((n-r.terminal.length).choose 2 : Int) := by
    exact_mod_cast r.cross_defect_account
  unfold jointCharge at hs
  unfold defectJointCharge
  omega

theorem joint_charge_sufficient (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (hcharge : r.jointCharge ≤ r.relativeBase) :
    r.premium ≤ delayedChainTotalPremiumMaximum n hn3 := by
  have hs := r.relative_slack hn3
  have hr : (0 : Int) ≤ (r.replayExcess : Int) := Int.natCast_nonneg _
  omega

/-- Accounting is exact even if this particular replay is too expensive.
Only the simpler condition without replayExcess is a geometric sufficient bound. -/
theorem joint_charge_exact_criterion (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n) :
    r.premium ≤ delayedChainTotalPremiumMaximum n hn3 ↔
      r.jointCharge ≤ r.relativeBase+(r.replayExcess : Int) := by
  have hs := r.relative_slack hn3
  omega

end ForestReplayAccount
end RSR2History
