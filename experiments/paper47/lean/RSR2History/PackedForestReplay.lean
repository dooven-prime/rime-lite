import RSR2History.PackedLowerMinimum
import RSR2History.ForestGapTerminalReplay
import RSR2History.SingleBlockFusionElimination
import RSR2History.FusionSourceRefill

/-! Guarded replay of packed transfers and both layers' fusions into an
arbitrary terminal upper forest. The final named layout is restored by the
same single terminal route used for the singleton forest branch. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

section Replay
variable {n : Nat} [NeZero n]

private theorem no_v_lower {word : List Letter}
    (letters : ∀ letter ∈ word, letter = .p false ∨ letter = .d false) :
    word.count .v = 0 := by
  apply List.count_eq_zero.mpr
  intro hv
  rcases letters .v hv with he | he <;> cases he

theorem UpperForestPath.packed_forest_cursor_replay
    {hn : 1 < n} {events : List (EffectiveEvent n)} {terminal : List (UpperFusionTree n)}
    {site : Nat → Fin n} {kfinal : Nat}
    {P : Placement n} {cursor : Fin n} {k : Nat} {forest : List (UpperFusionTree n)}
    {c d : LowerConfiguration n} {cost : Nat}
    (path : UpperForestPath k forest events kfinal terminal)
    (state : UpperReservedReplay P cursor k forest terminal (forestLeaves terminal) site)
    (lower : lowerConfiguration P = c)
    (extraction : PackedLowerPath n hn c (packedLowerLog events) d cost) :
    ∃ Q finalCursor word,
      ∃ s : PackedCursorSchedule site k forest cursor events kfinal terminal finalCursor,
        runLogged n hn P word = some (Q, events) ∧
        UpperReservedReplay Q finalCursor kfinal terminal terminal (forestLeaves terminal) site ∧
        lowerConfiguration Q = d ∧ word.length = cost + s.cost ∧
        word.count .v = logTransferCount events := by
  induction events generalizing k forest P cursor c cost with
  | nil =>
      cases path with
      | nil same =>
          obtain ⟨Q, word, hw, hQ, hs, hl, letters⟩ :=
            (extraction.empty_preparation rfl).silent_lower_word rfl P lower
          have final := (state.congr_upper hs).reframe same.perm (state.frame.rotate same)
          refine ⟨Q, cursor, word, .nil same, hw, final, hQ, ?_, ?_⟩
          · simpa [PackedCursorSchedule.cost] using hl
          · simpa [logTransferCount] using no_v_lower letters
  | cons event events ih =>
      cases path with
      | cons step tail =>
          have nextFrame := ReservationFrame.of_path tail (step.complete_leaves state.frame.complete)
            state.frame.terminal_order state.frame.site_injective state.frame.site_index
          cases step with
          | lower A B same =>
              obtain ⟨mid, next, prep, charge, rest, before, fusion, remaining, hcost⟩ :=
                extraction.split_first_event (.fusion false A B (A ∪ B)) (packedLowerLog events) rfl
              obtain ⟨R, u, hu, hR, hsUpper, hlenU, letters⟩ := before.silent_lower_word rfl P lower
              obtain ⟨hd, hLower, hcharge, hUpper⟩ := fusion.fusion_word R hR
              have first := ((state.congr_upper hsUpper).congr_upper hUpper).reframe same.perm nextFrame
              obtain ⟨Q, cf, word, s, hv, stateQ, hQ, hlenV, hcount⟩ :=
                ih tail first hLower remaining
              refine ⟨Q, cf, u ++ [.d false] ++ word, .lower A B same s, ?_, stateQ, hQ, ?_, ?_⟩
              · rw [runLogged_append, runLogged_append, hu]
                simp [hd, hv]
              · simp only [List.length_append, List.length_singleton, PackedCursorSchedule.cost]
                omega
              · simp [List.count_append, no_v_lower letters, hcount, logTransferCount]
          | fusion A B roots before after =>
              have first := state.reframe before.perm (state.frame.rotate before)
              have frame := nextFrame.rotate after
              have gap := first.frame.forest_ordered_merge_anchor_gap frame
              obtain ⟨R, hu, stateR, hlenU⟩ := first.forest_fusion_word hn frame
              have ready := stateR.reframe after.perm.symm nextFrame
              have hLower := (cursorFusion_preserves_lower hu).trans lower
              obtain ⟨Q, cf, word, s, hv, stateQ, hQ, hlenV, hcount⟩ :=
                ih tail ready hLower (by simpa using extraction)
              let u := phaseFreeFusionWord true
                (((site A.firstLeaf).val : ZMod n) - (cursor.val : ZMod n))
                (((site B.firstLeaf).val : ZMod n) - (cursor.val : ZMod n)) (A.leaves.length-1)
              have hcountU : u.count .v = 0 := by
                apply List.count_eq_zero.mpr
                intro hm
                rcases phaseFreeFusionWord_upper_letters _ _ _ .v hm with he | he <;> cases he
              refine ⟨Q, cf, u ++ word, .fusion A B roots before after gap s, ?_, stateQ, hQ, ?_, ?_⟩
              · simp [runLogged_append, u, hu, hv]
              · change u.length = _ at hlenU
                simp only [List.length_append, PackedCursorSchedule.cost]
                omega
              · simp [List.count_append, hcountU, hcount, logTransferCount]
          | transfer packet roots before after =>
              have first := state.reframe before.perm (state.frame.rotate before)
              have frame := nextFrame.rotate after
              obtain ⟨mid, prep, rest, R, u, _, remaining, hcost, hu, stateR, hR, hlenU, hcountU⟩ :=
                packed_cursor_extract_checkpoint first lower (by simpa using extraction) frame
              have ready := stateR.reframe after.perm.symm nextFrame
              obtain ⟨Q, cf, word, s, hv, stateQ, hQ, hlenV, hcount⟩ :=
                ih tail ready hR remaining
              refine ⟨Q, cf, u ++ word, .birth packet roots before after s, ?_, stateQ, hQ, ?_, ?_⟩
              · simp [runLogged_append, hu, hv]
              · simp only [List.length_append, PackedCursorSchedule.cost]
                omega
              · simp [List.count_append, hcountU, hcount, logTransferCount]

omit [NeZero n] in
private theorem PackedCursorSchedule.preserves_cursor_anchor
    {site : Nat → Fin n} {k t : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor cf : Fin n} {H : List (EffectiveEvent n)}
    (schedule : PackedCursorSchedule site k xs cursor H t terminal cf)
    (anchor : ∃ T ∈ xs, cursor = site T.firstLeaf) :
    ∃ T ∈ terminal, cf = site T.firstLeaf := by
  induction schedule with
  | nil same =>
      obtain ⟨T, ht, hc⟩ := anchor
      exact ⟨T, same.perm.mem_iff.mp ht, hc⟩
  | lower A B same rest ih =>
      obtain ⟨T, ht, hc⟩ := anchor
      exact ih ⟨T, same.perm.mem_iff.mp ht, hc⟩
  | @birth k xs ys cursor H t terminal cf packet roots before after rest ih =>
      exact ih ⟨.leaf k packet, after.perm.mem_iff.mpr (by simp), rfl⟩
  | fusion A B roots before after gap rest ih =>
      exact ih ⟨.merge A B, after.perm.mem_iff.mpr (by simp), rfl⟩

/-- At least one upper event leaves the final cursor at a live anchor,
even with subsequent effective lower fusions. -/
theorem PackedCursorSchedule.final_cursor_anchor
    {site : Nat → Fin n} {k t : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor cf : Fin n} {H : List (EffectiveEvent n)}
    (schedule : PackedCursorSchedule site k xs cursor H t terminal cf)
    (positive : 0 < upperCursorEventCount H) :
    ∃ T ∈ terminal, cf = site T.firstLeaf := by
  induction schedule with
  | nil same => simp [upperCursorEventCount] at positive
  | lower A B same rest ih => exact ih positive
  | @birth k xs ys cursor H t terminal cf packet roots before after rest ih =>
      exact rest.preserves_cursor_anchor
        ⟨.leaf k packet, after.perm.mem_iff.mpr (by simp), rfl⟩
  | fusion A B roots before after gap rest ih =>
      exact rest.preserves_cursor_anchor
        ⟨.merge A B, after.perm.mem_iff.mpr (by simp), rfl⟩

/-- One silent route for an all-upper source with an occupied port zero.
The transfer leaf count remains independent of the physical ring size. -/
theorem UpperReservedReplay.packed_forest_terminal_route
    (hn : 1 < n) {P Q : Placement n} {cursor : Fin n} {t : Nat}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor t terminal terminal (forestLeaves terminal) site)
    (lowerP : lowerConfiguration P = lowerExtractionEmpty n)
    (lowerQ : lowerConfiguration Q = lowerExtractionEmpty n)
    {T : UpperFusionTree n} (ht : T ∈ terminal)
    (anchor : cursor = site T.firstLeaf)
    (target : (forestPackets terminal).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length ≤ n*(n-1)-(n-terminal.length)^2 := by
  have hpos : 0 < terminal.length := List.length_pos_of_mem ht
  by_cases hr : 2 ≤ terminal.length
  · have upper : ∀ a, (P a).1 = true := by
      intro a
      have he := congrFun lowerP a
      cases h : (P a).1
      · simp [lowerConfiguration, lowerExtractionEmpty, h] at he
      · rfl
    have hp := state.packet_at_anchor ht
    rw [← anchor] at hp
    simp only [sub_self, zsite_zero] at hp
    have hport : (packetAt P true 0).Nonempty := hp.symm ▸ state.packet_nonempty T ht
    have hcycle := state.forest_packet_cycle hn
    have hrank : (occupiedSites P true).length = terminal.length := by
      simpa only [forestPackets, List.length_map, signature_eq_occupied_map] using
        hcycle.perm.length_eq.symm
    let : NeZero terminal.length := ⟨by omega⟩
    obtain ⟨source⟩ := forestTerminalSource_of_occupied P upper hport hrank
    exact source.terminal_route hn hr (hcycle.symm.trans target)
  · have hone : terminal.length = 1 := by omega
    obtain ⟨finish, _, hrun, hlen⟩ := state.joint_terminal_route hn lowerP lowerQ target
    rw [hone] at hlen ⊢
    have hcomp : n*(n-1) = (n-1)^2+(n-1) := by
      have hn' : n-1+1=n := by omega
      nlinarith
    have hbudget : layerBudget n 1 = n-1 := by simp [layerBudget]
    rw [hbudget] at hlen
    exact ⟨finish, hrun, by omega⟩

end Replay

/-- A realized packed replay with an independently minimized lower path,
the actual ordered terminal forest, and one final physical placement route. -/
structure PackedForestReplayAccount (n : Nat) (hn : 1 < n) (Q : Placement n)
    (H : List (EffectiveEvent n)) (terminal : List (UpperFusionTree n)) where
  trace : UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) terminal
  site : Nat → Fin n
  site_index : ∀ i ∈ forestLeaves terminal, (site i).val = (forestLeaves terminal).idxOf i
  finalCursor : Fin n
  schedule : PackedCursorSchedule site 0 [] (site 0) H (logTransferCount H) terminal finalCursor
  intermediate : Placement n
  replayWord : List Letter
  finish : List Letter
  prefix_run : runLogged n hn (seed n) replayWord = some (intermediate, H)
  finish_run : runLogged n hn intermediate finish = some (Q, [])
  prefix_length : replayWord.length = packedLowerCost n hn (packedLowerLog H) + schedule.cost
  terminal_bound : finish.length ≤ n*(n-1)-(n-terminal.length)^2

namespace PackedForestReplayAccount
variable {n : Nat} {hn : 1 < n} {Q : Placement n}
  {H : List (EffectiveEvent n)} {terminal : List (UpperFusionTree n)}

def word (a : PackedForestReplayAccount n hn Q H terminal) : List Letter :=
  a.replayWord ++ a.finish

theorem actual_run (a : PackedForestReplayAccount n hn Q H terminal) :
    runLogged n hn (seed n) a.word = some (Q, H) := by
  simp [word, runLogged_append, a.prefix_run, a.finish_run]

def observation (a : PackedForestReplayAccount n hn Q H terminal) :
    AttainableObservation n hn := ⟨(Q,H), ⟨a.word,a.actual_run⟩⟩

noncomputable def partitionCost (a : PackedForestReplayAccount n hn Q H terminal) : Nat :=
  partitionDistance n hn (unorderedPacketBlocks n Q)
    (partition_attainable_of_endpoint n hn Q
      (endpoint_attainable_of_logged hn a.observation.property))

theorem length_eq (a : PackedForestReplayAccount n hn Q H terminal) :
    a.word.length = packedLowerCost n hn (packedLowerLog H) + a.schedule.cost + a.finish.length :=
  by simp [word, a.prefix_length]

theorem complete (a : PackedForestReplayAccount n hn Q H terminal) :
    (forestLeaves terminal).Perm (List.range (logTransferCount H)) :=
  a.trace.toPath.complete_leaves (by simp [forestLeaves])

theorem leaf_count (a : PackedForestReplayAccount n hn Q H terminal) :
    (forestLeaves terminal).length = logTransferCount H :=
  a.complete.length_eq.trans List.length_range

theorem terminal_rank (a : PackedForestReplayAccount n hn Q H terminal) :
    terminal.length = (cyclicSignature Q true).length :=
  by simpa only [forestPackets, List.length_map] using a.trace.target_cycle.perm.length_eq

theorem partition_block_count (a : PackedForestReplayAccount n hn Q H terminal)
    (upper : ∀ x, (Q x).1 = true) :
    (unorderedPacketBlocks n Q).card = terminal.length := by
  have hmass : lowerAtomMass Q = 0 := by simp [lowerAtomMass, upper]
  have hzero := lower_count_zero_of_mass_zero Q hmass
  rw [unorderedPacketBlocks_card_eq_totalPacketCount, totalPacketCount, hzero,
    Nat.zero_add, ← layerRank_upper]
  exact a.terminal_rank.symm

theorem rank_pos_le_transfers (a : PackedForestReplayAccount n hn Q H terminal)
    (upper : ∀ x, (Q x).1 = true) :
    0 < terminal.length ∧ terminal.length ≤ logTransferCount H := by
  letI : NeZero n := ⟨by omega⟩
  let x : Fin n := ⟨0, by omega⟩
  have hx : x ∈ packetAt Q true (Q x).2 := by
    rw [mem_packetAt]
    exact Prod.ext (upper x) rfl
  have hmem := packetAt_mem_cyclicSignature Q true (Q x).2 ⟨x,hx⟩
  have hpos := List.length_pos_of_mem hmem
  have hbalance := forestMergeMass_balance terminal
  rw [a.leaf_count] at hbalance
  rw [← a.terminal_rank] at hpos
  exact ⟨hpos, by omega⟩

theorem partition_cost_rank_bound (a : PackedForestReplayAccount n hn Q H terminal)
    (upper : ∀ x, (Q x).1 = true) :
    2*(n-terminal.length)-1 ≤ a.partitionCost := by
  have bound := partitionDistance_lower_bound_of_card n hn (unorderedPacketBlocks n Q)
    (partition_attainable_of_endpoint n hn Q
      (endpoint_attainable_of_logged hn a.observation.property))
  simpa only [partitionCost, a.partition_block_count upper] using bound

theorem lower_fusion_count (a : PackedForestReplayAccount n hn Q H terminal)
    (upper : ∀ x, (Q x).1 = true) :
    logLayerFusionCount false H = n-logTransferCount H := by
  have hzero := lower_count_zero_of_mass_zero Q (by simp [lowerAtomMass, upper])
  have balance := runLogged_lower_packet_balance n hn a.word a.actual_run
  rw [hzero, seed_lowerPacketCount] at balance
  omega

end PackedForestReplayAccount

private theorem lowerConfiguration_eq_empty_of_upper {Q : Placement n}
    (upper : ∀ a, (Q a).1 = true) : lowerConfiguration Q = lowerExtractionEmpty n := by
  funext a
  simp [lowerConfiguration, lowerExtractionEmpty, upper a]

/-- The lower projection of any actual history ending all upstairs supplies
a feasible packed lower problem. -/
theorem allUpper_packedLowerCost_attained
    {n : Nat} (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter) (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true) :
    PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) (packedLowerCost n hn (packedLowerLog H)) := by
  obtain ⟨cost, path, _⟩ := runLogged_packedLower_projection word run
  exact packedLowerCost_attained ⟨cost, by simpa only
    [lowerConfiguration_seed, lowerConfiguration_eq_empty_of_upper upper] using path⟩

theorem PackedForestReplayAccount.lowerCost_fusion_bound
    {n : Nat} {hn : 1 < n} {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)}
    (a : PackedForestReplayAccount n hn Q H terminal)
    (upper : ∀ x, (Q x).1 = true) :
    packedLowerCost n hn (packedLowerLog H) ≤
      maxLowerExtractionCost n hn+(2*n-1)*(n-logTransferCount H) := by
  have bound := packedLowerCost_le_max_add_fusions
    (allUpper_packedLowerCost_attained hn a.word a.actual_run upper)
  simpa only [logFusionCount_packedLowerLog, a.lower_fusion_count upper] using bound

/-- Full transfer capacity forces each recorded transferred packet to contain
one atom, independently of the upper fusion order. -/
theorem allUpper_fullTransfer_singletons
    {n : Nat} (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter) (run : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ x, (Q x).1 = true) (full : logTransferCount H = n) :
    ∀ packet, .transfer packet ∈ H → packet.card = 1 := by
  have hmass : lowerAtomMass Q = 0 := by simp [lowerAtomMass, upper]
  have balance := singleton_log_resource_balance n hn word run
  have hseed := (runLogged_resource_balance n hn word run).2.1
  have hmassSeed : lowerAtomMass (seed n) = n := by simp [lowerAtomMass, seed]
  rw [hmass, hmassSeed] at hseed
  have hexcess : logTransferExcess H = 0 := by omega
  exact (logTransferExcess_eq_zero_iff_singleton_transfers H
    (runLogged_transfer_nonempty n hn word run)).mp hexcess

/-- Build an account against the original trace's named terminal forest. -/
theorem allUpper_packed_forest_replay_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} {terminal : List (UpperFusionTree n)}
    (word : List Letter) (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (trace : UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) terminal) :
    Nonempty (PackedForestReplayAccount n hn Q H terminal) := by
  have ht := singleton_transfer_count_le n hn run
  have complete := trace.toPath.complete_leaves (by simp [forestLeaves])
  have hbound : (forestLeaves terminal).length ≤ n := by simpa only [complete.length_eq, List.length_range] using ht
  let site := reservationSite (show 0 < n by omega) (forestLeaves terminal) hbound
  have state := upperReserved_seed_of_forestPath (show 0 < n by omega) (site 0) trace.toPath hbound
  have extraction := allUpper_packedLowerCost_attained hn word run upper
  obtain ⟨R, cf, replay, schedule, hp, stateR, lowerR, hl, _⟩ :=
    trace.toPath.packed_forest_cursor_replay state (lowerConfiguration_seed n) extraction
  have hmass := (runLogged_resource_balance n hn word run).2.1
  have hempty := lowerConfiguration_eq_empty_of_upper upper
  have hM : 0 < logTransferMass H := by
    have hLower : lowerAtomMass Q = 0 := by simp [lowerAtomMass, upper]
    have hseed : lowerAtomMass (seed n) = n := by simp [lowerAtomMass, seed]
    rw [hLower, hseed] at hmass
    omega
  have hV : 0 < logTransferCount H := by
    by_contra h
    have hh := logTransferMass_eq_zero_of_count_zero H (by omega)
    omega
  have he := schedule.event_length_balance
  have hleaf := forestMergeMass_balance terminal
  rw [complete.length_eq, List.length_range] at hleaf
  obtain ⟨T, hT, anchor⟩ := schedule.final_cursor_anchor (by simp at he; omega)
  obtain ⟨finish, hf, hbound⟩ :=
    stateR.packed_forest_terminal_route hn lowerR hempty hT anchor trace.target_cycle
  exact ⟨⟨trace, site, state.frame.site_index, cf, schedule, R, replay, finish, hp, hf, hl, hbound⟩⟩

/-- Extract the actual upper forest and use its same observation replay with
an optimal independent lower path. -/
theorem allUpper_packed_forest_replay_account
    {n : Nat} [NeZero n] (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter) (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true) :
    ∃ terminal, Nonempty (PackedForestReplayAccount n hn Q H terminal) := by
  obtain ⟨t, terminal, trace, _, _⟩ := singleton_run_ordered_forest hn run
  have ht : t = logTransferCount H := by simpa using trace.toPath.transfer_count
  subst t
  exact ⟨terminal, allUpper_packed_forest_replay_account_of_trace hn word run upper trace⟩

end RSR2History
