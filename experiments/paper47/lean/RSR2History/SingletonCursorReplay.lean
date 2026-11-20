import RSR2History.UpperCursorSchedule

/-! Complete interleaving of one auxiliary extraction path with the same upper log. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

omit [NeZero n] in
theorem ReservationFrame.ordered_merge_anchor_gap
    {k : Nat} {A B T : UpperFusionTree n} {roots : List (UpperFusionTree n)}
    {site : Nat → Fin n}
    (before : ReservationFrame k (A :: B :: roots) [T] T.leaves site)
    (after : ReservationFrame k (.merge A B :: roots) [T] T.leaves site) :
    (site B.firstLeaf).val = (site A.firstLeaf).val + A.leaves.length := by
  obtain ⟨root, hr, hs⟩ := after.subtrees (.merge A B) (by simp)
  have he : root = T := by simpa using hr
  subst root
  have hg := hs.anchor_gap before.omega_nodup
  simpa only [before.site_index A.firstLeaf (before.firstLeaf_in_omega (by simp)),
    before.site_index B.firstLeaf (before.firstLeaf_in_omega (by simp))] using hg

private theorem no_v_of_lower_letters {word : List Letter}
    (letters : ∀ letter ∈ word, letter = .p false ∨ letter = .d false) : word.count .v = 0 := by
  apply List.count_eq_zero.mpr
  intro hv
  rcases letters .v hv with he | he <;> cases he

theorem UpperForestPath.singleton_cursor_replay
    {hn : 1 < n} {events : List (EffectiveEvent n)} {T : UpperFusionTree n}
    {site : Nat → Fin n} {kfinal : Nat}
    {P : Placement n} {cursor : Fin n} {k : Nat} {forest : List (UpperFusionTree n)}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : UpperForestPath k forest events kfinal [T])
    (grammar : SingletonUpperLog events z)
    (state : UpperReservedReplay P cursor k forest [T] T.leaves site)
    (lower : lowerConfiguration P = c)
    (extraction : LowerExtractionPath n hn c z d cost) :
    ∃ Q finalCursor word,
      ∃ s : UpperCursorSchedule site k forest cursor events kfinal [T] finalCursor,
        runLogged n hn P word = some (Q, events) ∧
        UpperReservedReplay Q finalCursor kfinal [T] [T] T.leaves site ∧
        lowerConfiguration Q = d ∧ word.length = cost + s.cost ∧ word.count .v = z.length := by
  induction events generalizing k forest P cursor c z cost with
  | nil =>
      cases grammar
      cases path with
      | nil same =>
          obtain ⟨Q, word, hw, hQ, hs, hl, letters⟩ := extraction.silent_lower_word rfl P lower
          have hstate := state.congr_upper hs
          have final := hstate.reframe same.perm (state.frame.rotate same)
          refine ⟨Q, cursor, word, .nil same, hw, final, hQ, ?_, ?_⟩
          · simpa [UpperCursorSchedule.cost] using hl
          · exact no_v_of_lower_letters letters
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
                  have gap := first.frame.ordered_merge_anchor_gap frame
                  obtain ⟨R, hu, stateR, hlenU⟩ := first.fusion_word hn frame
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

end RSR2History
