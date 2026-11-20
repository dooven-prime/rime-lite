import RSR2History.ForestGapMomentGeometry
import RSR2History.ForestGapTerminalReplay
import RSR2History.ForestRootGapBridge

/-! Actual silent terminal routing with the source's cyclic hole moment.
The coordinate cut, slides and final physical phase belong to one guarded
execution; the moment is a saving in that same word's length certificate. -/
namespace RSR2History
open RSR2.Parametric

private theorem moment_route_cap_identity (n r : Nat) (hr : 2 ≤ r) (hrn : r ≤ n) :
    r*(n-1)+(r-1)*(n-r) = n*(n-1)-(n-r)^2 := by
  have hn : 1 ≤ n := by omega
  have he : r*(n-1)+(r-1)*(n-r)+(n-r)^2 = n*(n-1) := by
    have hn0 : n=(n-r)+r := by omega
    have hr0 : r=(r-1)+1 := by omega
    have hn1 : n-1=(n-r)+(r-1) := by omega
    rw [hn1]
    nlinarith
  omega

/-- Retain the minimum cyclic source moment in the actual silent route.
The additive form also certifies that the subtracted allowance is valid. -/
theorem ForestTerminalSource.terminal_route_moment
    {n r : Nat} [NeZero n] [NeZero r] (hn : 1 < n)
    {P Q : Placement n} (source : ForestTerminalSource n r P) (hr : 2 ≤ r)
    (same : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length + forestGapMoment source.gapProfile ≤ n*(n-1)-(n-r)^2 := by
  obtain ⟨coordinates⟩ := source.target_coordinates same
  obtain ⟨cert, hmoment⟩ := source.dominating_coordinates_moment hr coordinates
  obtain ⟨finish, hrun, hlen⟩ := cert.terminal_route_displacement hn
  have hr1 : r-1+1=r := by omega
  rw [hr1] at hlen
  refine ⟨finish,hrun,?_⟩
  have hcap := moment_route_cap_identity n r hr source.rank_le
  omega

/-- The same improvement displayed as an explicit subtraction from the
previous rank-sensitive terminal cap. -/
theorem ForestTerminalSource.terminal_route_sub_moment
    {n r : Nat} [NeZero n] [NeZero r] (hn : 1 < n)
    {P Q : Placement n} (source : ForestTerminalSource n r P) (hr : 2 ≤ r)
    (same : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length ≤ n*(n-1)-(n-r)^2-forestGapMoment source.gapProfile := by
  obtain ⟨finish,hrun,hlen⟩ := source.terminal_route_moment hn hr same
  exact ⟨finish,hrun,by omega⟩

/-- The actual reservation source has the moment of the original forest's
root leaf counts. No arbitrary root permutation enters the route. -/
theorem UpperReservedReplay.forest_terminal_route_moment
    {n : Nat} [NeZero n] (hn : 1 < n)
    {P Q : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal (forestLeaves terminal) site)
    (upper : ∀ a, (P a).1 = true) (rank : 2 ≤ terminal.length)
    {T : UpperFusionTree n} (ht : T ∈ terminal)
    (anchor : cursor = site T.firstLeaf)
    (target : (forestPackets terminal).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length + forestGapMoment (forestRootGapProfile terminal) ≤
        n*(n-1)-(n-terminal.length)^2 := by
  obtain ⟨source⟩ := state.forest_terminal_source_of_anchor hn upper rfl ht anchor
  obtain ⟨finish,hrun,hlen⟩ := source.terminal_route_moment hn rank
    ((state.forest_packet_cycle hn).symm.trans target)
  rw [state.gapMoment_eq_root hn source] at hlen
  exact ⟨finish,hrun,hlen⟩

/-- Two actual nontrivial roots force a strict saving over the rank-only
terminal allowance. -/
theorem UpperReservedReplay.forest_terminal_route_strict_of_two_roots
    {n : Nat} [NeZero n] (hn : 1 < n)
    {P Q : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal (forestLeaves terminal) site)
    (upper : ∀ a, (P a).1 = true) (rank : 2 ≤ terminal.length)
    {T : UpperFusionTree n} (ht : T ∈ terminal)
    (anchor : cursor = site T.firstLeaf)
    (target : (forestPackets terminal).IsRotated (cyclicSignature Q true))
    (i j : Fin terminal.length) (hne : i ≠ j)
    (hi : 2 ≤ terminal[i].leaves.length) (hj : 2 ≤ terminal[j].leaves.length) :
    ∃ finish, runLogged n hn P finish = some (Q, []) ∧
      finish.length < n*(n-1)-(n-terminal.length)^2 := by
  obtain ⟨finish,hrun,hlen⟩ := state.forest_terminal_route_moment hn upper rank ht anchor target
  have hm := forestRootGapMoment_pos_of_two_roots terminal i j hne hi hj
  exact ⟨finish,hrun,by omega⟩

/-- The two binary-root example gives a guarded terminal allowance of seven
in the four-site system, with the same named target and paid final phase. -/
theorem UpperReservedReplay.forest_terminal_route_two_binary_roots
    {P Q : Placement 4} {cursor : Fin 4}
    {A B : UpperFusionTree 4} {site : Nat → Fin 4}
    (state : UpperReservedReplay P cursor 4 [A,B] [A,B] (forestLeaves [A,B]) site)
    (upper : ∀ a, (P a).1 = true)
    (ha : A.leaves.length = 2) (hb : B.leaves.length = 2)
    {T : UpperFusionTree 4} (ht : T ∈ [A,B])
    (anchor : cursor = site T.firstLeaf)
    (target : (forestPackets [A,B]).IsRotated (cyclicSignature Q true)) :
    ∃ finish, runLogged 4 (by decide) P finish = some (Q, []) ∧ finish.length ≤ 7 := by
  obtain ⟨finish,hrun,hlen⟩ := state.forest_terminal_route_moment
    (by decide) upper (by simp) ht anchor target
  rw [forestRootGapMoment_two_binary_roots A B ha hb] at hlen
  norm_num at hlen
  exact ⟨finish,hrun,by omega⟩

/-- Select a real final silent route retaining the full original-root
moment. The event prefix, named target and reservation embedding are kept. -/
theorem forest_terminal_moment_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
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
      account.finish.length + forestGapMoment (forestRootGapProfile terminal) ≤
        n*(n-1)-(n-terminal.length)^2 := by
  obtain ⟨base,hterminal,state,empty⟩ :=
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
  obtain ⟨T,ht,anchor⟩ := base.schedule.final_cursor_anchor nonempty
  have hr : 2 ≤ base.terminal.length := by simpa only [hterminal] using rank
  let : NeZero base.terminal.length := ⟨by omega⟩
  obtain ⟨finish,hrun,hlen⟩ := state.forest_terminal_route_moment hn upperBase hr
    ht anchor base.trace.target_cycle
  obtain ⟨selected,_,hterm,hsite,_,_,_,hshort,_⟩ := base.choose_finish finish hrun
  refine ⟨selected,hterm.trans hterminal,?_,?_⟩
  · intro a ha
    rw [hsite]
    have hi := state.frame.site_index a (by simpa only [hterminal] using ha)
    simpa only [hterminal] using hi
  · have hs : selected.finish.length + forestGapMoment (forestRootGapProfile base.terminal) ≤
        n*(n-1)-(n-base.terminal.length)^2 := by omega
    have hm : forestGapMoment (forestRootGapProfile base.terminal) =
        forestGapMoment (forestRootGapProfile terminal) := by
      cases hterminal
      rfl
    rw [hm] at hs
    simpa only [hterminal] using hs

end RSR2History
