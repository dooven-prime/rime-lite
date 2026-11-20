import RSR2History.PackedForestReplay
import RSR2History.PackedForestWinding
import RSR2History.PackedForestBudget
import RSR2History.AllUpperSingletonExtrema

/-! Partition-relative domination for all-upper histories. Lower prefusions
are charged by fusion elimination; the upper winding charge and final route
come from one actual packed forest replay. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

private theorem cursor_event_count (H : List (EffectiveEvent n)) :
    upperCursorEventCount H = logTransferCount H + logLayerFusionCount true H := by
  induction H with
  | nil => rfl
  | cons e H ih =>
      cases e with
      | transfer B => (simp [upperCursorEventCount, logTransferCount, logLayerFusionCount, ih]; omega)
      | fusion layer A B C =>
          cases layer
          · simp [upperCursorEventCount, logTransferCount, logLayerFusionCount, ih]
          · simp [upperCursorEventCount, logTransferCount, logLayerFusionCount, ih]
            omega

private theorem upper_fusion_exists (H : List (EffectiveEvent n))
    (h : 0 < logLayerFusionCount true H) :
    ∃ A B C, EffectiveEvent.fusion true A B C ∈ H := by
  induction H with
  | nil => simp [logLayerFusionCount] at h
  | cons e H ih =>
      cases e with
      | transfer B =>
          obtain ⟨A,B,C,hm⟩ := ih (by simpa [logLayerFusionCount] using h)
          exact ⟨A,B,C,List.mem_cons_of_mem _ hm⟩
      | fusion layer A B C =>
          cases layer
          · obtain ⟨X,Y,Z,hm⟩ := ih (by simpa [logLayerFusionCount] using h)
            exact ⟨X,Y,Z,List.mem_cons_of_mem _ hm⟩
          · exact ⟨A,B,C,List.mem_cons_self⟩

namespace PackedForestReplayAccount
variable {n : Nat} {hn : 1 < n} {Q : Placement n}
  {H : List (EffectiveEvent n)} {terminal : List (UpperFusionTree n)}

theorem debt_bound (a : PackedForestReplayAccount n hn Q H terminal) :
    a.schedule.debt ≤ (logTransferCount H-terminal.length).choose 2 := by
  have hb := forest_crossDefect_identity terminal
  have hm := forestMergeMass_balance terminal
  rw [a.leaf_count] at hm
  have he := a.schedule.debt_balance
  change forestGapDebt terminal = forestGapDebt [] + a.schedule.debt at he
  have hemp : forestGapDebt ([] : List (UpperFusionTree n)) = 0 := rfl
  rw [hemp, zero_add] at he
  rw [he] at hb
  have hc : forestMergeMass terminal = logTransferCount H-terminal.length := by omega
  rw [hc] at hb
  omega

theorem canonical_zero_site (a : PackedForestReplayAccount n hn Q H terminal)
    (ht : 0 < logTransferCount H) :
    ∃ i, i < logTransferCount H ∧ (a.site i).val = 0 := by
  have hlen := a.leaf_count
  have hne : forestLeaves terminal ≠ [] := by intro h; simp [h] at hlen; omega
  obtain ⟨i,is,hi⟩ := List.exists_cons_of_ne_nil hne
  have hm : i ∈ forestLeaves terminal := by simp [hi]
  exact ⟨i,List.mem_range.mp (a.complete.mem_iff.mp hm),
    by rw [a.site_index i hm,hi]; simp⟩

theorem fused_cursor_cost_bound (a : PackedForestReplayAccount n hn Q H terminal)
    (hrt : terminal.length < logTransferCount H) :
    a.schedule.cost ≤ (2*logTransferCount H-terminal.length) +
      (logTransferCount H-terminal.length).choose 2 +
      n*(2*logTransferCount H-terminal.length-2) := by
  have he := a.schedule.event_length_balance
  simp only [List.length_nil, zero_add] at he
  have hc : upperCursorEventCount H = 2*logTransferCount H-terminal.length := by omega
  have hf := cursor_event_count H
  have fused := upper_fusion_exists H (by omega)
  have phase := a.schedule.forest_winding_phase_payment
    (a.canonical_zero_site (by omega)) fused
  have pay := a.schedule.payment
  have debt := a.debt_bound
  rw [hc] at phase pay
  omega

theorem unfused_cursor_cost_bound (a : PackedForestReplayAccount n hn Q H terminal)
    (hrt : terminal.length = logTransferCount H) (ht : 0 < logTransferCount H) :
    a.schedule.cost ≤ logTransferCount H+n*(logTransferCount H-1) := by
  have he := a.schedule.event_length_balance
  simp only [List.length_nil, zero_add] at he
  have hc : upperCursorEventCount H = logTransferCount H := by omega
  have phase := a.schedule.forest_initial_winding_phase_payment ht
  have pay := a.schedule.payment
  have debt := a.debt_bound
  rw [hrt,Nat.sub_self] at debt
  simp only [Nat.choose_zero_succ] at debt
  rw [hc] at phase pay
  omega

end PackedForestReplayAccount

/-- The very same packed replay accounts for both the upper cursor and the
final silent route. Its length is bounded relative to the endpoint partition. -/
theorem PackedForestReplayAccount.length_le_partition_add_delayed
    {n : Nat} (hn : 3 ≤ n) {Q : Placement n}
    {H : List (EffectiveEvent n)} {terminal : List (UpperFusionTree n)}
    (a : PackedForestReplayAccount n (by omega) Q H terminal)
    (upper : ∀ x, (Q x).1 = true) (hr : 2 ≤ terminal.length)
    (ht : logTransferCount H < n) :
    a.word.length ≤ a.partitionCost + delayedChainTotalPremiumMaximum n hn := by
  have hrt := (a.rank_pos_le_transfers upper).2
  have hlower := a.lowerCost_fusion_bound upper
  have hpartition := a.partition_cost_rank_bound upper
  have hnrm := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn
  rw [a.length_eq]
  by_cases hf : terminal.length < logTransferCount H
  · have bound := packedForest_fused_budget hr hf ht.le hlower
      (fusionSaving := 0) (terminalSaving := 0)
      (by simpa using a.fused_cursor_cost_bound hf)
      (by simpa using a.terminal_bound) hpartition
    omega
  · have he : terminal.length = logTransferCount H := by omega
    have bound := packedForest_unfused_budget (by omega) ht hlower
      (phaseSaving := 0) (by simpa using a.unfused_cursor_cost_bound he (by omega))
      (by simpa only [he] using a.terminal_bound)
      (by simpa only [he] using hpartition)
    omega

/-- All actual observations ending with every atom upstairs are dominated by
the delayed family, allowing arbitrary lower prefusion and packet transfers. -/
theorem allUpper_totalPremium_le_delayed {n : Nat} [NeZero n]
    (hn : 3 ≤ n) (o : AttainableObservation n (by omega))
    (upper : ∀ x, (o.val.1 x).1 = true) :
    totalObservationPremium n (by omega) o ≤ delayedChainTotalPremiumMaximum n hn := by
  by_contra! hbad
  obtain ⟨word, hw⟩ := o.property
  have ht : logTransferCount o.val.2 ≤ n := singleton_transfer_count_le n (by omega) hw
  by_cases hfull : logTransferCount o.val.2 = n
  · exact (not_lt_of_ge (allUpperSingleton_totalPremium_le_delayed hn o
      ⟨upper, allUpper_fullTransfer_singletons (by omega) word hw upper hfull⟩)) hbad
  obtain ⟨terminal, ⟨a⟩⟩ := allUpper_packed_forest_replay_account (by omega) word hw upper
  have hr := delayed_counterexample_has_multiblock_endpoint hn o hbad
  rw [a.partition_block_count upper] at hr
  have hlen := a.length_le_partition_add_delayed hn upper hr (lt_of_le_of_ne ht hfull)
  have hd := minimumWordLength_le
    (fun w => runLogged n (by omega) (seed n) w = some o.val) o.property a.actual_run
  change historyDistance n (by omega) o.val.1 o.val.2 o.property ≤ a.word.length at hd
  change delayedChainTotalPremiumMaximum n hn <
    historyDistance n (by omega) o.val.1 o.val.2 o.property - a.partitionCost at hbad
  omega

noncomputable def allUpperObservations (n : Nat) (hn : 1 < n) :
    Finset (AttainableObservation n hn) := by
  classical
  exact Finset.univ.filter (fun o => ∀ x, (o.val.1 x).1 = true)

@[simp] theorem mem_allUpperObservations (o : AttainableObservation n hn) :
    o ∈ allUpperObservations n hn ↔ ∀ x, (o.val.1 x).1 = true := by
  classical
  simp [allUpperObservations]

noncomputable def allUpperTotalPremiumMaximum (n : Nat) (hn : 1 < n) : Nat :=
  (allUpperObservations n hn).sup (totalObservationPremium n hn)

/-- A delayed chain attains the maximum even in the larger class allowing
arbitrary whole-packet transfers. -/
theorem allUpperTotalPremiumMaximum_eq_delayed {n : Nat} [NeZero n]
    (hn : 3 ≤ n) :
    allUpperTotalPremiumMaximum n (by omega) = delayedChainTotalPremiumMaximum n hn := by
  apply le_antisymm
  · exact Finset.sup_le fun o ho =>
      allUpper_totalPremium_le_delayed hn o ((mem_allUpperObservations o).mp ho)
  · obtain ⟨o, ho, hmax⟩ := allUpperSingleton_delayed_maximum_attained hn
    rw [← hmax]
    exact Finset.le_sup ((mem_allUpperObservations o).mpr ho.1)

theorem allUpperTotalPremiumMaximum_eq {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    allUpperTotalPremiumMaximum n (by omega) =
      (5*n*(n-1))/2 + maxLowerExtractionCost n (by omega) - n + 2 := by
  rw [allUpperTotalPremiumMaximum_eq_delayed hn, delayedChainTotalPremiumMaximum_eq n hn]

theorem delayed_counterexample_has_lower_survivor {n : Nat} [NeZero n]
    (hn : 3 ≤ n) (o : AttainableObservation n (by omega))
    (hbad : delayedChainTotalPremiumMaximum n hn < totalObservationPremium n (by omega) o) :
    2 ≤ (unorderedPacketBlocks n o.val.1).card ∧ ∃ x, (o.val.1 x).1 = false := by
  refine ⟨delayed_counterexample_has_multiblock_endpoint hn o hbad, ?_⟩
  by_contra h
  have upper : ∀ x, (o.val.1 x).1 = true := by
    intro x
    cases hx : (o.val.1 x).1
    · exact (h ⟨x, hx⟩).elim
    · rfl
  exact (not_lt_of_ge (allUpper_totalPremium_le_delayed hn o upper)) hbad

end RSR2History
