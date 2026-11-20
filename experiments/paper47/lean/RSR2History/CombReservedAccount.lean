import RSR2History.CombRootTraceBridge

/-!
Retain the physical reservation invariant of the actual forest replay and
allow its final silent route to be replaced by a shorter route.  Neither
operation changes the terminal forest, reservation frame, or effective log.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

theorem allUpper_singleton_reserved_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal ∧
      UpperReservedReplay account.intermediate account.finalCursor n
        account.terminal account.terminal (forestLeaves account.terminal)
        account.site ∧
      lowerConfiguration account.intermediate = lowerExtractionEmpty n := by
  obtain ⟨z, grammar, hlen, hnd⟩ :=
    allUpper_singleton_log_order hn word run upper singletons
  have complete := trace.toPath.complete_leaves (by simp [forestLeaves])
  have hbound : (forestLeaves terminal).length ≤ n := by
    simpa using complete.length_eq.le
  let site := reservationSite (show 0 < n by omega) (forestLeaves terminal) hbound
  have state := upperReserved_seed_of_forestPath (show 0 < n by omega)
    (site 0) trace.toPath hbound
  have extraction := lowerExtractionCost_attained_of_permutation (hn := hn) hlen hnd
  have emptyQ : lowerConfiguration Q = lowerExtractionEmpty n := by
    funext a
    simp [lowerConfiguration, lowerExtractionEmpty, upper a]
  obtain ⟨R, cf, replay, finish, schedule, prefixRun, stateR, emptyR,
      finishRun, _, _, lengthEq, terminalBound⟩ :=
    trace.toPath.singleton_forest_endpoint_replay grammar state
      (lowerConfiguration_seed n) extraction emptyQ trace.target_cycle
  exact ⟨⟨z, terminal, site, cf, R, replay, finish, schedule,
    grammar, hlen, hnd, trace, prefixRun, finishRun, lengthEq, terminalBound⟩,
    rfl, stateR, emptyR⟩

namespace ForestReplayAccount

/-- Replace only the last physical silent route.  Choosing the shorter of
the old and new routes retains both its old layer budget and any proved
budget for the new route. -/
theorem choose_finish {n : Nat} {hn : 1 < n}
    {Q : Placement n} {H : List (EffectiveEvent n)}
    (r : ForestReplayAccount n hn Q H)
    (finish : List Letter)
    (run : runLogged n hn r.intermediate finish = some (Q, [])) :
    ∃ s : ForestReplayAccount n hn Q H,
      s.order = r.order ∧ s.terminal = r.terminal ∧ s.site = r.site ∧
      s.finalCursor = r.finalCursor ∧ s.intermediate = r.intermediate ∧
      s.replayWord = r.replayWord ∧
      s.finish.length ≤ finish.length ∧
      s.finish.length ≤ r.finish.length := by
  by_cases h : r.finish.length ≤ finish.length
  · exact ⟨r, rfl, rfl, rfl, rfl, rfl, rfl, h, le_rfl⟩
  · have hle : finish.length ≤ r.finish.length := by omega
    have hlen : (r.replayWord ++ finish).length =
        lowerExtractionCost n hn r.order + r.schedule.cost + finish.length := by
      have he := r.length_eq
      simp only [List.length_append] at he ⊢
      omega
    let s : ForestReplayAccount n hn Q H :=
      ⟨r.order, r.terminal, r.site, r.finalCursor, r.intermediate,
        r.replayWord, finish, r.schedule, r.grammar, r.full_order,
        r.nodup, r.trace, r.prefix_run, run, hlen,
        hle.trans r.terminal_bound⟩
    exact ⟨s, rfl, rfl, rfl, rfl, rfl, rfl, le_rfl, hle⟩

end ForestReplayAccount
end RSR2History
