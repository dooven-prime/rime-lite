import RSR2History.MultiRootCursorGeometry
import RSR2History.SingletonExtractionDefect

/-! Singleton lower extraction interleaved with an arbitrary feasible upper
forest. All roots share one cursor and one final physical placement route. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer

section Replay
variable {n : Nat} [NeZero n]

private theorem lower_letters_no_v {word : List Letter}
    (letters : ∀ letter ∈ word, letter = .p false ∨ letter = .d false) : word.count .v = 0 := by
  apply List.count_eq_zero.mpr
  intro hv
  rcases letters .v hv with he | he <;> cases he

theorem UpperForestPath.singleton_forest_cursor_replay
    {hn : 1 < n} {events : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n} {kfinal : Nat}
    {P : Placement n} {cursor : Fin n} {k : Nat} {forest : List (UpperFusionTree n)}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : UpperForestPath k forest events kfinal terminal)
    (grammar : SingletonUpperLog events z)
    (state : UpperReservedReplay P cursor k forest terminal (forestLeaves terminal) site)
    (lower : lowerConfiguration P = c)
    (extraction : LowerExtractionPath n hn c z d cost) :
    ∃ Q finalCursor word,
      ∃ s : UpperCursorSchedule site k forest cursor events kfinal terminal finalCursor,
        runLogged n hn P word = some (Q, events) ∧
        UpperReservedReplay Q finalCursor kfinal terminal terminal (forestLeaves terminal) site ∧
        lowerConfiguration Q = d ∧ word.length = cost + s.cost ∧ word.count .v = z.length := by
  induction events generalizing k forest P cursor c z cost with
  | nil =>
      cases grammar
      cases path with
      | nil same =>
          obtain ⟨Q, word, hw, hQ, hs, hl, letters⟩ := extraction.silent_lower_word rfl P lower
          have final := (state.congr_upper hs).reframe same.perm (state.frame.rotate same)
          refine ⟨Q, cursor, word, .nil same, hw, final, hQ, ?_, ?_⟩
          · simpa [UpperCursorSchedule.cost] using hl
          · exact lower_letters_no_v letters
  | cons event events ih =>
      cases path with
      | cons step tail =>
          have nextFrame := ReservationFrame.of_path tail (step.complete_leaves state.frame.complete)
            state.frame.terminal_order state.frame.site_injective state.frame.site_index
          cases step with
          | lower A B same => cases grammar
          | fusion A B roots before after =>
              cases grammar with
              | fusion left right gramTail =>
                  have first := state.reframe before.perm (state.frame.rotate before)
                  have frame := nextFrame.rotate after
                  have gap := first.frame.forest_ordered_merge_anchor_gap frame
                  obtain ⟨R, hu, stateR, hlenU⟩ := first.forest_fusion_word hn frame
                  have ready := stateR.reframe after.perm.symm nextFrame
                  have hLower := (cursorFusion_preserves_lower hu).trans lower
                  obtain ⟨Q, cf, word, s, hv, stateQ, hQ, hlenV, hcount⟩ :=
                    ih tail gramTail ready hLower extraction
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
                    simp only [List.length_append, UpperCursorSchedule.cost]
                    omega
                  · simp only [List.count_append, hcountU, hcount]
                    omega
          | transfer packet roots before after =>
              cases grammar with
              | transfer a gramTail =>
                  have first := state.reframe before.perm (state.frame.rotate before)
                  have frame := nextFrame.rotate after
                  obtain ⟨mid, prep, rest, R, u, _, remaining, hcost, hu, stateR, hR, hlenU, hcountU⟩ :=
                    singleton_cursor_delete_checkpoint first lower extraction frame
                  have ready := stateR.reframe after.perm.symm nextFrame
                  obtain ⟨Q, cf, word, s, hv, stateQ, hQ, hlenV, hcount⟩ :=
                    ih tail gramTail ready hR remaining
                  refine ⟨Q, cf, u ++ word, .birth a roots before after s, ?_, stateQ, hQ, ?_, ?_⟩
                  · simp [runLogged_append, hu, hv]
                  · simp only [List.length_append, UpperCursorSchedule.cost]
                    omega
                  · simp only [List.count_append, hcountU, hcount, List.length_cons]
                    omega

/-- Finish the whole forest at one prescribed literal endpoint. Neither the
effective event order nor the lower extraction order is replaced. -/
theorem UpperForestPath.singleton_forest_endpoint_replay
    {hn : 1 < n} {H : List (EffectiveEvent n)} {z : List (Fin n)}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    {P Q : Placement n} {cursor : Fin n} {k kfinal cost : Nat}
    {forest : List (UpperFusionTree n)} {c : LowerConfiguration n}
    (path : UpperForestPath k forest H kfinal terminal)
    (grammar : SingletonUpperLog H z)
    (state : UpperReservedReplay P cursor k forest terminal (forestLeaves terminal) site)
    (lower : lowerConfiguration P = c)
    (extraction : LowerExtractionPath n hn c z (lowerExtractionEmpty n) cost)
    (lowerQ : lowerConfiguration Q = lowerExtractionEmpty n)
    (cycle : (forestPackets terminal).IsRotated (cyclicSignature Q true)) :
    ∃ R finalCursor replayWord finish,
      ∃ s : UpperCursorSchedule site k forest cursor H kfinal terminal finalCursor,
        runLogged n hn P replayWord = some (R,H) ∧
        UpperReservedReplay R finalCursor kfinal terminal terminal (forestLeaves terminal) site ∧
        lowerConfiguration R = lowerExtractionEmpty n ∧
        runLogged n hn R finish = some (Q,[]) ∧
        runLogged n hn P (replayWord++finish) = some (Q,H) ∧
        replayWord.length = cost+s.cost ∧
        (replayWord++finish).length = cost+s.cost+finish.length ∧
        finish.length ≤ layerBudget n terminal.length := by
  obtain ⟨R, cf, replayWord, s, hp, stateR, lowerR, hlen, _⟩ :=
    path.singleton_forest_cursor_replay grammar state lower extraction
  obtain ⟨finish, _, hf, hfl⟩ := stateR.joint_terminal_route hn lowerR lowerQ cycle
  refine ⟨R,cf,replayWord,finish,s,hp,stateR,lowerR,hf,?_,hlen,?_,hfl⟩
  · simp [runLogged_append, hp, hf]
  · simp [List.length_append, hlen]

end Replay

/-- The physically declared subclass supplies a full extraction permutation;
no single-block endpoint hypothesis is used. -/
theorem allUpper_singleton_log_order {n : Nat} (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1) :
    ∃ z, SingletonUpperLog H z ∧ z.length = n ∧ z.Nodup := by
  have hx := (logTransferExcess_eq_zero_iff_singleton_transfers H
    (runLogged_transfer_nonempty n hn word hexec)).mpr singletons
  have hempty : lowerAtomMass Q = 0 := by simp [lowerAtomMass, upper]
  have hl := singleton_lower_fusion_eq_excess_of_empty n hn word hexec hempty
  obtain ⟨z, grammar⟩ := (runLogged_cyclicEventPath n hn word hexec).singleton_upper_log_of_counts
    (by omega) hx
  have hb := runLogged_resource_balance n hn word hexec
  have hs := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hs
  have hlen : z.length = n := by
    have hc := grammar.transfer_count
    omega
  have hnd : z.Nodup := by
    apply List.nodup_iff_count_le_one.mpr
    intro a
    rw [← grammar.atom_count a]
    exact le_of_eq (singleton_fullUpper_atomTransferCount hn word hexec upper a)
  exact ⟨z,grammar,hlen,hnd⟩

/-- End-to-end actual-history interface with the three costs retained
separately. The lower cost is the optimum for this original transfer order. -/
theorem allUpper_singleton_forest_replay {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1) :
    ∃ z terminal site finalCursor R replayWord finish,
      ∃ s : UpperCursorSchedule site 0 [] (site 0) H n terminal finalCursor,
        SingletonUpperLog H z ∧ z.length = n ∧ z.Nodup ∧
        UpperForestTrace (seed n) 0 [] H Q n terminal ∧
        runLogged n hn (seed n) replayWord = some (R,H) ∧
        runLogged n hn R finish = some (Q,[]) ∧
        runLogged n hn (seed n) (replayWord++finish) = some (Q,H) ∧
        (replayWord++finish).length = lowerExtractionCost n hn z+s.cost+finish.length ∧
        finish.length ≤ layerBudget n terminal.length := by
  obtain ⟨z,grammar,hlen,hnd⟩ := allUpper_singleton_log_order hn word hexec upper singletons
  obtain ⟨k,terminal,trace,complete,cycle⟩ := singleton_run_ordered_forest hn hexec
  have hk : k = n := by
    have hc := trace.toPath.transfer_count
    have hg := grammar.transfer_count
    omega
  subst k
  have hbound : (forestLeaves terminal).length ≤ n := by simpa using complete.length_eq.le
  let site := reservationSite (show 0<n by omega) (forestLeaves terminal) hbound
  have state := upperReserved_seed_of_forestPath (show 0<n by omega) (site 0) trace.toPath hbound
  have extraction := lowerExtractionCost_attained_of_permutation (hn := hn) hlen hnd
  have emptyQ : lowerConfiguration Q = lowerExtractionEmpty n := by
    funext a
    simp [lowerConfiguration, lowerExtractionEmpty, upper a]
  obtain ⟨R,cf,replayWord,finish,s,hp,stateR,lowerR,hf,hr,hpl,hlen',hfl⟩ :=
    trace.toPath.singleton_forest_endpoint_replay grammar state (lowerConfiguration_seed n)
      extraction emptyQ cycle
  exact ⟨z,terminal,site,cf,R,replayWord,finish,s,grammar,hlen,hnd,trace,hp,hf,hr,hlen',hfl⟩

/-- One global cursor account for the entire forest. The final cursor is
charged once, not once per terminal root. -/
theorem UpperCursorSchedule.forest_payment
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor) :
    s.cost + finalCursor.val = H.length + forestGapDebt terminal +
      n*s.windings + (site 0).val := by
  have hd := s.debt_balance
  have he : s.debt = forestGapDebt terminal := by simpa [forestGapDebt] using hd.symm
  simpa only [he] using s.payment

theorem UpperCursorSchedule.forest_event_count
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor) :
    H.length + terminal.length = 2*kfinal := by
  simpa using s.event_length_balance

theorem forest_gapDebt_add_defect (terminal : List (UpperFusionTree n)) :
    forestGapDebt terminal + (terminal.map UpperFusionTree.leftBranchDefect).sum =
      (terminal.map (fun T => (T.leaves.length-1).choose 2)).sum := by
  induction terminal with
  | nil => rfl
  | cons T terminal ih =>
      have ht := T.gapDebt_add_defect
      simp only [forestGapDebt, List.map_cons, List.sum_cons] at ih ⊢
      omega

/-- Root-local defects telescope inside a single shared cursor ledger. -/
theorem UpperCursorSchedule.forest_defect_payment
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor) :
    s.cost + finalCursor.val + (terminal.map UpperFusionTree.leftBranchDefect).sum =
      H.length + (terminal.map (fun T => (T.leaves.length-1).choose 2)).sum +
        n*s.windings + (site 0).val := by
  have hp := s.forest_payment
  have hd := forest_gapDebt_add_defect terminal
  omega

/-- The first actual transfer starts at its own reserved cursor site and
therefore supplies a nonwinding event on every nonempty forest schedule. -/
theorem UpperCursorSchedule.forest_initial_birth_nonwinding
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor)
    (positive : 0 < kfinal) : 1 ≤ s.birthZeros := by
  cases s with
  | nil same => omega
  | birth a roots before after rest =>
      simp only [UpperCursorSchedule.birthZeros, cursorWinding, lt_self_iff_false,
        if_false, ite_true]
      omega
  | fusion A B roots before after gap rest =>
      have he := before.perm.length_eq
      simp at he

theorem UpperCursorSchedule.forest_windings_lt_events
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor)
    (positive : 0 < kfinal) : s.windings + 1 ≤ H.length := by
  have hzero := s.forest_initial_birth_nonwinding positive
  have hp := s.winding_partition
  omega

end RSR2History
