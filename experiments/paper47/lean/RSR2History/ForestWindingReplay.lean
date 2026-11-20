import RSR2History.ForestWindingSlack

/-! Guarded partition-relative replay for all-upper singleton histories with
both a surviving forest and at least one effective fusion. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- The fully charged winding count includes the initial and final physical
cursor phases. If two nonwinding events are the only ones, the final phase
must cover any positive initial phase. -/
theorem UpperCursorSchedule.forest_winding_phase_payment
    {n kfinal : Nat} {site : Nat → Fin n} {terminal : List (UpperFusionTree n)}
    {H : List (EffectiveEvent n)} {cf : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal cf)
    (hzero : ∃ i, i < kfinal ∧ (site i).val = 0)
    (hfusion : ∃ A B, EffectiveEvent.fusion true A B (A ∪ B) ∈ H) :
    n*s.windings + (site 0).val ≤ n*(H.length-2) + cf.val := by
  obtain ⟨A,B,hm⟩ := hfusion
  have hw := s.forest_windings_add_two_le_events ⟨A,B,_,hm⟩
  by_cases hmax : s.windings+2 = H.length
  · have hphase : (site 0).val ≤ cf.val := by
      by_cases hp : 0 < (site 0).val
      · exact s.forest_final_phase_ge_of_max_windings hmax hp hzero ⟨A,B,hm⟩
      · omega
    have he : s.windings = H.length-2 := by omega
    rw [he]
    omega
  · have hp := Nat.mul_le_mul_left n (show s.windings+1 ≤ H.length-2 by omega)
    rw [Nat.mul_add, Nat.mul_one] at hp
    have hi := (site 0).isLt
    omega

namespace ForestReplayAccount

variable {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}

theorem rank_le (r : ForestReplayAccount n hn Q H) : r.terminal.length ≤ n := by
  have hm := forestMergeMass_balance r.terminal
  rw [r.leaf_count] at hm
  omega

theorem winding_charge_le_of_canonical_sites (r : ForestReplayAccount n hn Q H)
    (hindex : ∀ a ∈ forestLeaves r.terminal,
      (r.site a).val = (forestLeaves r.terminal).idxOf a)
    (hfused : r.terminal.length < n) :
    r.windingCharge ≤ (n : Int)*((H.length : Int)-2) := by
  have he := r.schedule.forest_event_count
  have hfusion := r.grammar.fusion_mem_of_transfer_lt_length (by rw [r.full_order]; omega)
  have hzero : ∃ a, a < n ∧ (r.site a).val = 0 := by
    have hpos : (forestLeaves r.terminal).length ≠ 0 := by rw [r.leaf_count]; omega
    have hnil : forestLeaves r.terminal ≠ [] := by
      intro h
      simp [h] at hpos
    obtain ⟨a,as,ha⟩ := List.exists_cons_of_ne_nil hnil
    have hm : a ∈ forestLeaves r.terminal := by simp [ha]
    have hc : (forestLeaves r.terminal).Perm (List.range n) :=
      r.trace.toPath.complete_leaves (by simp [forestLeaves])
    refine ⟨a,List.mem_range.mp (hc.mem_iff.mp hm),?_⟩
    rw [hindex a hm, ha]
    simp
  have hpay := r.schedule.forest_winding_phase_payment hzero hfusion
  have htwo : 2 ≤ H.length := by omega
  have hint := Int.ofNat_le.mpr hpay
  push_cast [Nat.cast_sub htwo] at hint
  unfold windingCharge
  omega

end ForestReplayAccount

/-- The original named forest, exact log and literal endpoint admit one
word paying the partition-relative budget with all the savings retained. -/
theorem allUpper_singleton_fused_forest_delayed_replay_of_trace
    {n : Nat} [NeZero n] (hn3 : 3 ≤ n) (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (hr : 2 ≤ terminal.length) (hfused : terminal.length < n) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal ∧
      (∀ a ∈ forestLeaves terminal,
        (account.site a).val = (forestLeaves terminal).idxOf a) ∧
      account.word.length + (maxLowerExtractionCost n hn-account.extractionCost) +
        (terminal.length-1).choose 2 + forestStructuralDefect terminal ≤
        account.partitionCost + delayedChainTotalPremiumMaximum n hn3 := by
  obtain ⟨account,hterminal,hindex,hfin⟩ :=
    forest_terminal_moment_account_of_trace hn word run upper singletons trace hr
  refine ⟨account,hterminal,hindex,?_⟩
  have hrank : 2 ≤ account.terminal.length := by rwa [hterminal]
  let : NeZero account.terminal.length := ⟨by omega⟩
  have hmoment : forestGapMoment (forestRootGapProfile account.terminal) =
      forestGapMoment (forestRootGapProfile terminal) := by
    cases hterminal
    rfl
  have hdefect : forestStructuralDefect account.terminal = forestStructuralDefect terminal := by
    cases hterminal
    rfl
  have hfinish : account.finish.length +
      forestGapMoment (forestRootGapProfile account.terminal) ≤
        n*(n-1)-(n-account.terminal.length)^2 := by
    rw [hmoment,hterminal]
    exact hfin
  have hdrop : account.terminal.length < n := by rwa [hterminal]
  have hcharge := account.winding_charge_le_of_canonical_sites
    (by simpa only [hterminal] using hindex) hdrop
  have hbound := account.word_budget_of_winding_charge hn3 hrank hdrop hfinish hcharge
  simpa only [hterminal,hdefect] using hbound

/-- The actual success run and its terminal partition rank suffice to
select the guarded replay. -/
theorem allUpper_singleton_fused_forest_delayed_replay
    {n : Nat} [NeZero n] (hn3 : 3 ≤ n) (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (hr : 2 ≤ (unorderedPacketBlocks n Q).card)
    (hfused : (unorderedPacketBlocks n Q).card < n) :
    ∃ account : ForestReplayAccount n hn Q H,
      ∃ _ : NeZero account.terminal.length,
      account.word.length + (maxLowerExtractionCost n hn-account.extractionCost) +
        (account.terminal.length-1).choose 2 + forestStructuralDefect account.terminal ≤
        account.partitionCost + delayedChainTotalPremiumMaximum n hn3 := by
  obtain ⟨base⟩ := allUpper_singleton_forest_account hn word run upper singletons
  have hrank : 2 ≤ base.terminal.length := by rwa [← base.partition_block_count]
  have hd : base.terminal.length < n := by rwa [← base.partition_block_count]
  let : NeZero base.terminal.length := ⟨by omega⟩
  obtain ⟨account,hterm,_,hb⟩ :=
    allUpper_singleton_fused_forest_delayed_replay_of_trace hn3 hn word run upper singletons
      base.trace hrank hd
  have hnzero : account.terminal.length ≠ 0 := by rw [hterm]; omega
  let : NeZero account.terminal.length := ⟨hnzero⟩
  have hdef := forestStructuralDefect_congr hterm
  exact ⟨account,inferInstance,by simpa only [hterm,hdef] using hb⟩

end RSR2History
