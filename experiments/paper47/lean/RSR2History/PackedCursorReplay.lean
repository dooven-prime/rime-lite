import RSR2History.PackedCursorSchedule
import RSR2History.PackedLowerProjection
import RSR2History.SingleBlockSingletonCursor
import RSR2History.PackedCursorBudget

/-!
Continuous replay of all three event kinds, with an independent packed lower
path. Lower fusion/preparation is paid by that path; upper fusions and actual
transfer letters are paid by the cursor schedule. No bound by the singleton
extraction maximum is assumed for packed lower costs.
-/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

private theorem no_v_lower {word : List Letter}
    (letters : ∀ letter ∈ word, letter = .p false ∨ letter = .d false) :
    word.count .v = 0 := by
  apply List.count_eq_zero.mpr
  intro hv
  rcases letters .v hv with he | he <;> cases he

theorem UpperForestPath.packed_cursor_replay
    {hn : 1 < n} {events : List (EffectiveEvent n)} {T : UpperFusionTree n}
    {site : Nat → Fin n} {kfinal : Nat}
    {P : Placement n} {cursor : Fin n} {k : Nat} {forest : List (UpperFusionTree n)}
    {c d : LowerConfiguration n} {cost : Nat}
    (path : UpperForestPath k forest events kfinal [T])
    (state : UpperReservedReplay P cursor k forest [T] T.leaves site)
    (lower : lowerConfiguration P = c)
    (extraction : PackedLowerPath n hn c (packedLowerLog events) d cost) :
    ∃ Q finalCursor word,
      ∃ s : PackedCursorSchedule site k forest cursor events kfinal [T] finalCursor,
        runLogged n hn P word = some (Q, events) ∧
        UpperReservedReplay Q finalCursor kfinal [T] [T] T.leaves site ∧
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
              have gap := first.frame.ordered_merge_anchor_gap frame
              obtain ⟨R, hu, stateR, hlenU⟩ := first.fusion_word hn frame
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

/-- Exact three-part cost decomposition, including the final physical phase.
The same full effective log is retained through the final silent segment. -/
theorem UpperForestPath.packed_cursor_endpoint_replay
    {hn : 1 < n} {H : List (EffectiveEvent n)} {T : UpperFusionTree n}
    {site : Nat → Fin n} {k kfinal cost : Nat}
    {P : Placement n} {cursor : Fin n} {forest : List (UpperFusionTree n)}
    {c : LowerConfiguration n}
    (path : UpperForestPath k forest H kfinal [T])
    (state : UpperReservedReplay P cursor k forest [T] T.leaves site)
    (lower : lowerConfiguration P = c)
    (extraction : PackedLowerPath n hn c (packedLowerLog H) (lowerExtractionEmpty n) cost)
    (q : Fin n) :
    ∃ word finalCursor phase,
      ∃ s : PackedCursorSchedule site k forest cursor H kfinal [T] finalCursor,
        runLogged n hn P word = some ((fun _ => (true,q)), H) ∧
        word.length = cost + s.cost + phase ∧ phase ≤ n-1 := by
  obtain ⟨R, cf, u, s, hu, stateR, lowerR, hlenU, _⟩ :=
    path.packed_cursor_replay state lower extraction
  let loc : ZMod n := ((site T.firstLeaf).val : ZMod n) - (cf.val : ZMod n)
  have hR : R = fun _ => (true, zsite loc) := stateR.full_of_lower_empty lowerR
  let amount : ZMod n := (q.val : ZMod n) - loc
  let v := pWord true amount.val
  have hfinal : phaseShift R true amount = fun _ => (true,q) := by
    funext a
    rw [hR]
    simp only [phaseShift, ite_true, zsite_val_cast]
    have he : loc+amount = (q.val : ZMod n) := by dsimp [amount]; ring
    simp [he]
  have hv : runLogged n hn R v = some ((fun _ => (true,q)), []) := by
    simpa only [v, hfinal] using runLogged_phase hn R true amount
  refine ⟨u++v, cf, amount.val, s, ?_, ?_, ?_⟩
  · simp [runLogged_append, hu, hv]
  · simp [v, pWord, hlenU]
  · have he := ZMod.val_lt amount
    omega

/-- Finish one upper packet at the prescribed literal site. The lower path
is an independent input, with no comparison to the singleton maximum. -/
theorem packed_cursor_full_endpoint_word
    (hn : 1 < n) {H : List (EffectiveEvent n)} {T : UpperFusionTree n}
    {t cost : Nat} (ht : 2 ≤ t) (htn : t ≤ n)
    (path : UpperForestPath 0 [] H t [T])
    (extraction : PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) cost) (q : Fin n) :
    ∃ word, runLogged n hn (seed n) word = some ((fun _ => (true,q)), H) ∧
      word.length + T.leftBranchDefect + T.initialCursorSlack ≤
        cost + packedUpperBudget n t + (n-1) := by
  have complete : T.leaves.Perm (List.range t) := by
    simpa [forestLeaves] using path.complete_leaves (by simp [forestLeaves])
  have htree : T.leaves.length = t := by simpa using complete.length_eq
  have hbound : (forestLeaves [T]).length ≤ n := by simpa [forestLeaves, htree] using htn
  let site := reservationSite (show 0 < n by omega) (forestLeaves [T]) hbound
  have seedState : UpperReservedReplay (seed n) (site 0) 0 [] [T] T.leaves site := by
    simpa only [site, forestLeaves, List.flatMap_cons, List.flatMap_nil, List.append_nil] using
      upperReserved_seed_of_forestPath (show 0 < n by omega) (site 0) path hbound
  obtain ⟨word, cf, phase, s, hr, hlen, hphase⟩ :=
    path.packed_cursor_endpoint_replay seedState (lowerConfiguration_seed n) extraction q
  have hb := s.cost_le_with_defect seedState.frame ht
  have hzero : 0 ∈ T.leaves := complete.mem_iff.mpr (List.mem_range.mpr (by omega))
  have hindex : (site 0).val = T.leaves.idxOf 0 := by
    simpa [forestLeaves] using seedState.frame.site_index 0 (by simpa [forestLeaves] using hzero)
  rw [hindex] at hb
  refine ⟨word, hr, ?_⟩
  change s.cost + T.leftBranchDefect +
    (if T.leaves.idxOf 0 = 0 then 0 else n-T.leaves.idxOf 0) ≤ packedUpperBudget n t at hb
  unfold UpperFusionTree.initialCursorSlack
  omega

/-- Every actual one-block history with at least two transfers supplies both
the future forest and the independent packed lower path. Its lower cost is
bounded by the original lower letters, not by `K_n`. -/
theorem singleBlock_packed_cursor_replay
    (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ cost T replay,
      PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H) (lowerExtractionEmpty n) cost ∧
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      runLogged n hn (seed n) replay = some (Q,H) ∧
      replay.length + T.leftBranchDefect + T.initialCursorSlack ≤
        cost + packedUpperBudget n (logTransferCount H) + (n-1) ∧
      cost ≤ word.count (.p false) + word.count (.d false) := by
  obtain ⟨_, ⟨q, hQ⟩, _, _⟩ := singleBlock_positiveTransfer_shape n hn word hexec hblocks (by omega)
  obtain ⟨k, forest, trace, complete, cycle⟩ := singleton_run_ordered_forest hn hexec
  have hk : k = logTransferCount H := by simpa using trace.toPath.transfer_count
  subst k
  have hforestlen : forest.length = 1 := by
    have he := cycle.perm.length_eq
    rw [hQ, cyclicSignature_full_upper] at he
    simpa [forestPackets] using he
  obtain ⟨T, rfl⟩ := List.length_eq_one_iff.mp hforestlen
  obtain ⟨cost, extraction, hcost⟩ := runLogged_packedLower_projection word hexec
  have extraction' : PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) cost := by
    have hempty : lowerConfiguration Q = lowerExtractionEmpty n := by
      funext a
      simp [hQ, lowerConfiguration, lowerExtractionEmpty]
    simpa only [lowerConfiguration_seed, hempty] using extraction
  obtain ⟨replay, hr, hb⟩ := packed_cursor_full_endpoint_word hn ht
    (singleton_transfer_count_le n hn hexec) trace.toPath extraction' q
  exact ⟨cost, T, replay, extraction', trace, by simpa only [← hQ] using hr, hb, hcost⟩

end RSR2History
