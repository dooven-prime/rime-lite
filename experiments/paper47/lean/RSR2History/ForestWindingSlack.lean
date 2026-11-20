import RSR2History.ForestStructuralReplay
import RSR2History.ForestWindingBudget
import RSR2History.FusionSourceRefill

/-! Compare the shared winding charge with the partition-relative budget. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

private theorem twice_choose_two (a : Nat) : 2*a.choose 2 = a*(a-1) := by
  obtain ⟨q,hq⟩ := Nat.even_mul_pred_self a
  rw [Nat.choose_two_right]
  omega

/-- Express the scalar budget in terms of fusion count and surviving rank. -/
private theorem relative_budget_rank_identity (n rank : Nat)
    (hr : 2 ≤ rank) (hrn : rank ≤ n) :
    (packedUpperBudget n n : Int) - 3*(n : Int) + rank + 2 -
      ((n-rank).choose 2 : Int) - ((n*(n-1)-(n-rank)^2 : Nat) : Int) =
      (n : Int) * (2*(n : Int) - rank - 2) +
        ((rank-1).choose 2 : Int) - (2*((n : Int)-rank)-1) := by
  have hn : 2 ≤ n := hr.trans hrn
  have hsq : (n-rank)^2 ≤ n*(n-1) := by
    simpa only [pow_two] using
      Nat.mul_le_mul (show n-rank ≤ n by omega) (show n-rank ≤ n-1 by omega)
  have hnChoose := twice_choose_two n
  have hrChoose := twice_choose_two (rank-1)
  have hsChoose := twice_choose_two (n-rank)
  have hsqZ : ((n*(n-1)-(n-rank)^2 : Nat) : Int) =
      (n : Int)*((n : Int)-1)-((n : Int)-rank)^2 := by
    rw [Int.ofNat_sub hsq]
    push_cast [Nat.cast_sub (show 1 ≤ n by omega), Nat.cast_sub hrn]
    rfl
  have hnChooseZ : (2 : Int)*(n.choose 2 : Int) = (n : Int)*((n : Int)-1) := by
    have h := congrArg (fun a : Nat => (a : Int)) hnChoose
    push_cast [Nat.cast_sub (show 1 ≤ n by omega)] at h
    exact h
  have hrChooseZ : (2 : Int)*((rank-1).choose 2 : Int) =
      ((rank : Int)-1)*((rank : Int)-2) := by
    have h := congrArg (fun a : Nat => (a : Int)) hrChoose
    push_cast [Nat.cast_sub (show 1 ≤ rank by omega),
      Nat.cast_sub (show 1 ≤ rank-1 by omega)] at h
    linarith
  have hsChooseZ : (2 : Int)*((n-rank).choose 2 : Int) =
      ((n : Int)-rank)*((n : Int)-rank-1) := by
    by_cases he : n = rank
    · subst rank
      simp
    · have h := congrArg (fun a : Nat => (a : Int)) hsChoose
      push_cast [Nat.cast_sub hrn, Nat.cast_sub (show 1 ≤ n-rank by omega)] at h
      exact h
  rw [hsqZ, packedUpperBudget_self hn]
  push_cast
  nlinarith only [hnChooseZ, hrChooseZ, hsChooseZ]

namespace ForestReplayAccount

variable {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}

theorem partition_block_count (r : ForestReplayAccount n hn Q H) :
    (unorderedPacketBlocks n Q).card = r.terminal.length := by
  have ht : logTransferCount H = n := r.grammar.transfer_count.symm.trans r.full_order
  have he := log_event_count_split H
  have hf := (runLogged_resource_balance n hn r.word r.actual_run).1
  rw [seed_totalPacketCount] at hf
  rw [unorderedPacketBlocks_card_eq_totalPacketCount]
  have hl := r.schedule.forest_event_count
  omega

theorem partition_cost_rank_bound (r : ForestReplayAccount n hn Q H)
    (hr : 0 < r.terminal.length) :
    2*(n-r.terminal.length)-1 ≤ r.partitionCost := by
  have hrn : r.terminal.length ≤ n := by
    have h := forestMergeMass_balance r.terminal
    rw [r.leaf_count] at h
    omega
  have h := partitionDistance_lower_bound_of_rank_drop n hn (unorderedPacketBlocks n Q)
    (partition_attainable_of_endpoint n hn Q
      (endpoint_attainable_of_logged hn r.observation.property))
    (n-r.terminal.length+1) (by omega) (by rw [r.partition_block_count]; omega)
  change 2*(n-r.terminal.length+1)-3 ≤ r.partitionCost at h
  omega

/-- The rank margin, the structural defect and the winding margin all enter
the same signed lower bound on the partition-relative slack. -/
theorem relative_slack_with_winding_margin (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length] (hn3 : 3 ≤ n) (hr : 2 ≤ r.terminal.length)
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2) :
    ((maxLowerExtractionCost n hn-r.extractionCost : Nat) : Int) +
      ((r.terminal.length-1).choose 2 : Int) + (forestStructuralDefect r.terminal : Int) +
      ((n : Int)*((H.length : Int)-2)-r.windingCharge) +
      ((r.partitionCost : Int) - (2*((n : Int)-r.terminal.length)-1)) +
      r.replayExcess ≤ (delayedChainTotalPremiumMaximum n hn3 : Int) - r.premium := by
  have hrn : r.terminal.length ≤ n := by
    have h := forestMergeMass_balance r.terminal
    rw [r.leaf_count] at h
    omega
  have hf : (r.finish.length : Int) + (forestGapMoment (forestRootGapProfile r.terminal) : Int) ≤
      ((n*(n-1)-(n-r.terminal.length)^2 : Nat) : Int) := by exact_mod_cast hfinish
  have hp := r.schedule.forest_event_count
  have hpZ := congrArg (fun a : Nat => (a : Int)) hp
  push_cast at hpZ
  have hs := r.relative_slack_with_cross_defect hn3
  have hscalar := relative_budget_rank_identity n r.terminal.length hr hrn
  have hw : (n : Int) * (2*(n : Int) - (r.terminal.length : Int) - 2) =
      (n : Int) * ((H.length : Int)-2) := by
    congr 1
    omega
  rw [hw] at hscalar
  unfold relativeBase defectJointCharge at hs
  unfold windingCharge forestStructuralDefect
  simp only [Nat.cast_add]
  omega

/-- Excess phase charge can be covered by the structural and rank margins.
In particular this applies whenever the final cursor lies at or above the
initial cursor and the schedule contains a fusion. -/
theorem premium_le_delayed_of_winding_phase (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length] (hn3 : 3 ≤ n) (hr : 2 ≤ r.terminal.length)
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2)
    (hfusion : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H)
    (hphase : (r.site 0).val ≤ r.finalCursor.val +
      (r.terminal.length-1).choose 2 + forestStructuralDefect r.terminal) :
    r.premium + (maxLowerExtractionCost n hn-r.extractionCost) ≤
      delayedChainTotalPremiumMaximum n hn3 := by
  have ht : logTransferCount H = n := r.grammar.transfer_count.symm.trans r.full_order
  have he := log_event_count_split H
  have hfpos : 0 < logFusionCount H := by
    obtain ⟨A,B,C,hm⟩ := hfusion
    unfold logFusionCount
    have hmem : 1 ∈ H.map (fun | .fusion _ _ _ _ => 1 | .transfer _ => 0) :=
      List.mem_map.mpr ⟨_, hm, rfl⟩
    exact List.le_sum_of_mem hmem
  have hcard := r.schedule.forest_event_count
  have hgap : 0 < n-r.terminal.length := by omega
  have hrk := r.partition_cost_rank_bound (by omega)
  have hrkZ : (2*((n : Int)-r.terminal.length)-1) ≤ r.partitionCost := by
    have h := congrArg (fun a : Nat => (a : Int)) (Nat.sub_add_cancel
      (show 1 ≤ 2*(n-r.terminal.length) by omega))
    push_cast [Nat.cast_sub (show r.terminal.length ≤ n by omega)] at h
    have hrk' := Int.ofNat_le.mpr hrk
    omega
  have hw := r.schedule.forest_windings_add_two_le_events hfusion
  have hwZ : (n : Int) * r.schedule.windings ≤ (n : Int) * ((H.length : Int)-2) := by
    apply mul_le_mul_of_nonneg_left _ (Int.natCast_nonneg _)
    omega
  have hs := r.relative_slack_with_winding_margin hn3 hr hfinish
  have hexcess : (0 : Int) ≤ (r.replayExcess : Int) := Int.natCast_nonneg _
  unfold windingCharge at hs
  omega

/-- With the phase included in the winding bound, the actual replay pays
the entire partition-relative budget, retaining all three savings. -/
theorem replay_budget_of_winding_charge (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length] (hn3 : 3 ≤ n)
    (hr : 2 ≤ r.terminal.length) (hfused : r.terminal.length < n)
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2)
    (hw : r.windingCharge ≤ (n : Int)*((H.length : Int)-2)) :
    r.premium + (maxLowerExtractionCost n hn-r.extractionCost) +
      (r.terminal.length-1).choose 2 + forestStructuralDefect r.terminal +
      r.replayExcess ≤ delayedChainTotalPremiumMaximum n hn3 := by
  have hrk := r.partition_cost_rank_bound (by omega)
  have hrkZ : (2*((n : Int)-r.terminal.length)-1) ≤ r.partitionCost := by
    have h := congrArg (fun a : Nat => (a : Int)) (Nat.sub_add_cancel
      (show 1 ≤ 2*(n-r.terminal.length) by omega))
    push_cast [Nat.cast_sub (show r.terminal.length ≤ n by omega)] at h
    have hrk' := Int.ofNat_le.mpr hrk
    omega
  have hs := r.relative_slack_with_winding_margin hn3 hr hfinish
  omega

/-- The selected word itself satisfies the bound after adding back the
minimum cost of its unordered terminal partition. -/
theorem word_budget_of_winding_charge (r : ForestReplayAccount n hn Q H)
    [NeZero r.terminal.length] (hn3 : 3 ≤ n)
    (hr : 2 ≤ r.terminal.length) (hfused : r.terminal.length < n)
    (hfinish : r.finish.length + forestGapMoment (forestRootGapProfile r.terminal) ≤
      n*(n-1)-(n-r.terminal.length)^2)
    (hw : r.windingCharge ≤ (n : Int)*((H.length : Int)-2)) :
    r.word.length + (maxLowerExtractionCost n hn-r.extractionCost) +
      (r.terminal.length-1).choose 2 + forestStructuralDefect r.terminal ≤
      r.partitionCost + delayedChainTotalPremiumMaximum n hn3 := by
  have hb := r.replay_budget_of_winding_charge hn3 hr hfused hfinish hw
  have hp := r.premium_balance
  have he := r.replayExcess_balance
  omega

end ForestReplayAccount

/-- The all-upper singleton grammar locates a genuine upper fusion as soon
as there are more events than transfers. -/
theorem SingletonUpperLog.fusion_mem_of_transfer_lt_length
    {n : Nat} {H : List (EffectiveEvent n)} {z : List (Fin n)}
    (grammar : SingletonUpperLog H z) (hcount : z.length < H.length) :
    ∃ A B, EffectiveEvent.fusion true A B (A ∪ B) ∈ H := by
  induction grammar with
  | nil => simp at hcount
  | transfer a tail ih =>
      obtain ⟨A,B,hm⟩ := ih (by simpa using hcount)
      exact ⟨A,B,List.mem_cons_of_mem _ hm⟩
  | fusion A B tail ih =>
      exact ⟨A,B,by simp⟩

end RSR2History
