import RSR2History.ForestDominatingCoordinates
import RSR2History.ForestPhysicalSource
import RSR2History.ForestCursorAnchor
import RSR2History.CombReservedAccount

/-! Rank-sensitive actual silent routing from distributed terminal gaps.
The source may have any number of nontrivial roots and arbitrary tree
shapes. This bounds the terminal route only, not the full history budget. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer

private theorem forest_route_cap_identity (n r : Nat) (hr : 2 ≤ r) (hrn : r ≤ n) :
    (r-1)*(n+(n-r)-1)+(n-1) = n*(n-1)-(n-r)^2 := by
  have hn : 1 ≤ n := by omega
  have he : (r-1)*(n+(n-r)-1)+(n-1)+(n-r)^2 = n*(n-1) := by
    have hn0 : n = (n-r)+r := by omega
    have hr0 : r = (r-1)+1 := by omega
    have hn1 : n-1 = (n-r)+(r-1) := by omega
    have hunit : n+(n-r)-1 = 2*(n-r)+(r-1) := by omega
    rw [hn1, hunit]
    nlinarith
  omega

/-- Every named, cyclically compatible target has an actual silent route
from a source with an occupied port-zero cut. The common cut, all slides,
and the final physical phase are included in one shared-cursor account. -/
theorem ForestTerminalSource.terminal_route
    {n r : Nat} [NeZero n] [NeZero r] (hn : 1 < n)
    {P Q : Placement n} (source : ForestTerminalSource n r P) (hr : 2 ≤ r)
    (same : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length ≤ n*(n-1)-(n-r)^2 := by
  obtain ⟨coordinates⟩ := source.dominating_coordinates_of_same_cycle hr same
  obtain ⟨finish, hrun, hlen⟩ := coordinates.terminal_route hn
  rw [forest_route_cap_identity n r hr source.rank_le] at hlen
  exact ⟨finish, hrun, hlen⟩

/-- The needed source certificate comes from the same actual reserved
layout, and its occupied cut is the surviving final cursor anchor. -/
theorem UpperReservedReplay.forest_terminal_route
    {n r : Nat} [NeZero n] [NeZero r] (hn : 1 < n)
    {P Q : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal (forestLeaves terminal) site)
    (upper : ∀ a, (P a).1 = true)
    (rank : terminal.length = r) (hr : 2 ≤ r)
    {T : UpperFusionTree n} (ht : T ∈ terminal)
    (anchor : cursor = site T.firstLeaf)
    (target : (forestPackets terminal).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length ≤ n*(n-1)-(n-r)^2 := by
  obtain ⟨source⟩ := state.forest_terminal_source_of_anchor hn upper rank ht anchor
  exact source.terminal_route hn hr ((state.forest_packet_cycle hn).symm.trans target)

/-- Replace the final route of an actual arbitrary-shape annotated forest
replay. No transfer-first condition or comb-shape certificate is needed.
The event schedule budget is deliberately left unchanged. -/
theorem forest_terminal_budgeted_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (rank : 2 ≤ terminal.length) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal ∧
      (∀ a ∈ forestLeaves terminal,
        (account.site a).val = (forestLeaves terminal).idxOf a) ∧
      account.finish.length ≤ n*(n-1)-(n-terminal.length)^2 := by
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
  let r := base.terminal.length
  have hr : 2 ≤ r := by simpa only [r, hterminal] using rank
  let : NeZero r := ⟨by omega⟩
  obtain ⟨finish, hrun, hlen⟩ := state.forest_terminal_route hn upperBase
    (rfl : base.terminal.length = r) hr ht anchor base.trace.target_cycle
  obtain ⟨selected, _, hterm, hsite, _, _, _, hshort, _⟩ :=
    base.choose_finish finish hrun
  refine ⟨selected, hterm.trans hterminal, ?_, ?_⟩
  · intro a ha
    rw [hsite]
    have hi := state.frame.site_index a (by simpa only [hterminal] using ha)
    simpa only [hterminal] using hi
  · have hlen' := hshort.trans hlen
    simpa only [r, hterminal] using hlen'

end RSR2History
