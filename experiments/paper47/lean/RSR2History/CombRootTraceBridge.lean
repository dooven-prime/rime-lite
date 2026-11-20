import RSR2History.CombRootRelativeBudget

/-!
Replay a supplied actual forest annotation, retaining its terminal forest
literally.  The comb shape and transfer-first hypothesis are structural
assumptions about that annotation and the original event log.  No terminal
routing budget or nonnegative-slack premise is introduced here.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- The endpoint replay theorem accepts the original annotation directly.
In particular, this construction does not first choose a possibly different
existential forest and then assume that its roots have the desired shape. -/
theorem allUpper_singleton_forest_account_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal) :
    ∃ account : ForestReplayAccount n hn Q H,
      account.terminal = terminal := by
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
  obtain ⟨R, cf, replay, finish, schedule, prefixRun, _, _, finishRun, _,
      _, lengthEq, terminalBound⟩ :=
    trace.toPath.singleton_forest_endpoint_replay grammar state
      (lowerConfiguration_seed n) extraction emptyQ trace.target_cycle
  exact ⟨⟨z, terminal, site, cf, R, replay, finish, schedule,
    grammar, hlen, hnd, trace, prefixRun, finishRun, lengthEq, terminalBound⟩, rfl⟩

/-- A physical annotation whose ordered terminal forest has the declared
comb shape gives an account with that same ordered terminal forest. -/
theorem combJointTerminalAccount_of_trace_preserving_terminal
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {k : Nat}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (shape : CombRootForestNormalForm terminal k)
    (transfersFirst : SingletonTransfersFirst H) :
    ∃ account : CombJointTerminalAccount n hn Q H k,
      account.forestAccount.terminal = terminal := by
  obtain ⟨account, hterminal⟩ :=
    allUpper_singleton_forest_account_of_trace hn word run upper singletons trace
  have accountShape : CombRootForestNormalForm account.terminal k := by
    rw [hterminal]
    exact shape
  exact ⟨⟨account, accountShape, transfersFirst⟩, hterminal⟩

/-- Existence only: this theorem supplies an actual same-observation replay
account, leaving the joint geometric budget as a separate question. -/
theorem combJointTerminalAccount_of_trace
    {n : Nat} [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    {terminal : List (UpperFusionTree n)} {k : Nat}
    (word : List Letter)
    (run : runLogged n hn (seed n) word = some (Q, H))
    (upper : ∀ a, (Q a).1 = true)
    (singletons : ∀ B, .transfer B ∈ H → B.card = 1)
    (trace : UpperForestTrace (seed n) 0 [] H Q n terminal)
    (shape : CombRootForestNormalForm terminal k)
    (transfersFirst : SingletonTransfersFirst H) :
    Nonempty (CombJointTerminalAccount n hn Q H k) := by
  obtain ⟨account, _⟩ := combJointTerminalAccount_of_trace_preserving_terminal
    hn word run upper singletons trace shape transfersFirst
  exact ⟨account⟩

end RSR2History
