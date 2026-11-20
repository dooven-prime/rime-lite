import RSR2History.ForestGapTerminalReplay

/-! At full rank all named coordinates are forced relative to their cut,
so the terminal part of a forest replay costs a single rotation word. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- Relative coordinates agree at full rank. Only the literal phase of the
target has to be restored physically. -/
theorem ForestTerminalSource.full_rank_rotation
    {n : Nat} [NeZero n] (hn : 1 < n) {P Q : Placement n}
    (source : ForestTerminalSource n n P)
    (same : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ amount : ZMod n,
      runLogged n hn P (pWord true amount.val) = some (Q, []) ∧
      (pWord true amount.val).length ≤ n-1 := by
  obtain ⟨coords⟩ := source.target_coordinates same
  have hsite (j : Fin n) : (source.site j).val = j.val := by
    have hl := source.source_lower j
    have hu := source.source_upper j
    omega
  have htarget (j : Fin n) : (coords.target j).val = j.val := by
    have hl := coords.target_lower j
    have hu := coords.target_upper j
    omega
  have hend : phaseShift P true coords.phase = Q := by
    funext a
    rw [coords.finish a]
    simp [phaseShift, source.start a, hsite, htarget, add_comm]
  refine ⟨coords.phase, ?_, ?_⟩
  · rw [runLogged_phase, hend]
  · have hlt := ZMod.val_lt coords.phase
    simpa [pWord] using (show coords.phase.val ≤ n-1 by omega)

theorem forest_full_rank_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (rank : terminal.length = n) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal ∧
      (∀ a ∈ forestLeaves terminal,
        (account.site a).val = (forestLeaves terminal).idxOf a) ∧
      (∃ amount : ZMod n, account.finish = pWord true amount.val) ∧
      account.finish.length ≤ n-1 := by
  obtain ⟨base, hterminal, state, empty⟩ :=
    allUpper_singleton_reserved_account_of_trace hn word run upper singletons trace
  have upperBase : ∀ a, (base.intermediate a).1 = true := by
    intro a
    have he := congrFun empty a
    cases hh : (base.intermediate a).1
    · simp [lowerConfiguration, lowerExtractionEmpty, hh] at he
    · rfl
  have nonempty : H ≠ [] := by
    intro he
    have count : logTransferCount H = n :=
      base.grammar.transfer_count.symm.trans base.full_order
    simp [he, logTransferCount] at count
    omega
  obtain ⟨T, ht, anchor⟩ := base.schedule.final_cursor_anchor nonempty
  have hrank : base.terminal.length = n := by simpa only [hterminal] using rank
  obtain ⟨source⟩ := state.forest_terminal_source_of_anchor hn upperBase hrank ht anchor
  obtain ⟨amount, hrun, hlen⟩ := source.full_rank_rotation hn
    ((state.forest_packet_cycle hn).symm.trans base.trace.target_cycle)
  let finish := pWord true amount.val
  have hl : (base.replayWord ++ finish).length =
      lowerExtractionCost n hn base.order + base.schedule.cost + finish.length := by
    have he := base.length_eq
    simp only [List.length_append] at he ⊢
    omega
  have hb : finish.length ≤ layerBudget n base.terminal.length := by
    rw [hrank]
    have hp : n ≠ 0 := by omega
    unfold layerBudget
    simp only [hp, if_false]
    have hf : finish.length ≤ n-1 := hlen
    omega
  let selected : ForestReplayAccount n hn Q H :=
    { base with finish := finish, finish_run := hrun, length_eq := hl, terminal_bound := hb }
  refine ⟨selected, hterminal, ?_, ⟨amount, rfl⟩, hlen⟩
  intro a ha
  have hi := state.frame.site_index a (by simpa only [hterminal] using ha)
  simpa only [selected, hterminal] using hi

private theorem full_rank_scalar_budget (n : Nat) (hn : 3 ≤ n) :
    n + n*(n-1) + 2*(n-1) + n < packedUpperBudget n n + 2 := by
  rw [packedUpperBudget_self (by omega)]
  have hchoose : 2 * n.choose 2 = n * (n-1) := by
    obtain ⟨q,hq⟩ := Nat.even_mul_pred_self n
    rw [Nat.choose_two_right, hq]
    omega
  have hd : n-1+1=n := by omega
  have hprod : 6*(n-1) ≤ 3*(n-1)*(n-1) := by
    have hmul := Nat.mul_le_mul_left (n-1) (show 6 ≤ 3*(n-1) by omega)
    nlinarith
  nlinarith

/-- The full rank case retains the original extraction deficit and pays
the final literal rotation within the delayed family budget. -/
theorem ForestReplayAccount.replay_length_lt_delayed_of_full_rank
    {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (rank : r.terminal.length = n) (hfinish : r.finish.length ≤ n-1) :
    r.word.length + (maxLowerExtractionCost n hn-r.extractionCost) <
      delayedChainTotalPremiumMaximum n hn3 := by
  have he := r.schedule.forest_event_count
  rw [rank] at he
  have hd := r.cross_defect_account
  rw [rank, Nat.sub_self] at hd
  norm_num at hd
  have hw := r.schedule.forest_windings_lt_events (by omega)
  have hw' := Nat.mul_le_mul_left n (show r.schedule.windings ≤ n-1 by omega)
  have hc := r.schedule.forest_payment
  have hs := (r.site 0).isLt
  have hbound : r.schedule.cost+r.finish.length+n < packedUpperBudget n n+2 := by
    have hscalar := full_rank_scalar_budget n hn3
    omega
  have hj := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn3
  have hk := r.extractionCost_le_max
  have hlen := r.length_eq
  change r.word.length = r.extractionCost + r.schedule.cost + r.finish.length at hlen
  omega

theorem ForestReplayAccount.premium_le_delayed_of_full_rank
    {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}
    (r : ForestReplayAccount n hn Q H) (hn3 : 3 ≤ n)
    (rank : r.terminal.length = n) (hfinish : r.finish.length ≤ n-1) :
    r.premium + (maxLowerExtractionCost n hn-r.extractionCost) ≤
      delayedChainTotalPremiumMaximum n hn3 := by
  have hl := r.replay_length_lt_delayed_of_full_rank hn3 rank hfinish
  have hp := r.premium_balance
  have hmin := r.historyCost_le_word
  omega

end RSR2History
