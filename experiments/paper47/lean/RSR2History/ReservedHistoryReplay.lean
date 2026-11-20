import RSR2History.ReservedEventReplay
import RSR2History.EventResourceLedger

/-! Replay one complete original event path on a continuous physical state
chain. Only the final silent preparation is postponed. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

def eventReplayBudget (n : Nat) (events : List (EffectiveEvent n)) : Nat :=
  4*n*logFusionCount events + (2*n+1)*logTransferCount events

@[simp] theorem eventReplayBudget_nil (n : Nat) : eventReplayBudget n [] = 0 := by
  simp [eventReplayBudget, logFusionCount, logTransferCount]

theorem eventReplayBudget_cons (n : Nat) (event : EffectiveEvent n)
    (events : List (EffectiveEvent n)) :
    eventReplayBudget n (event :: events) = eventReplayCost n event + eventReplayBudget n events := by
  cases event <;> simp [eventReplayBudget, eventReplayCost, logFusionCount,
    logTransferCount, Nat.mul_add] <;> omega

/-- Transfer occurrence numbers are determined by the same exact event log. -/
theorem UpperForestPath.transfer_count
    {k kfinal : Nat} {forest terminal : List (UpperFusionTree n)}
    {events : List (EffectiveEvent n)}
    (path : UpperForestPath k forest events kfinal terminal) :
    kfinal = k + logTransferCount events := by
  induction path with
  | nil => simp [logTransferCount]
  | cons head _ ih =>
      cases head <;> simp only [logTransferCount, List.map_cons, List.sum_cons] at * <;> omega

/-- All three event kinds use the same induction. At every boundary the
reserved upper forest and the original lower cyclic packet order agree.
No intermediate literal coordinate equality is required. -/
theorem UpperForestTrace.reserved_replay [NeZero n]
    (hn : 1 < n) {reference Q : Placement n} {k kfinal : Nat}
    {forest terminal : List (UpperFusionTree n)} {events : List (EffectiveEvent n)}
    (trace : UpperForestTrace reference k forest events Q kfinal terminal)
    {P : Placement n} {omega : List Nat} {site : Nat → Fin n}
    (h : ReplayCompatible P reference k forest terminal omega site) :
    ∃ R word, runLogged n hn P word = some (R, events) ∧
      SameCyclicSignatures R Q ∧ ReservedState R kfinal terminal terminal omega site ∧
      word.length ≤ eventReplayBudget n events := by
  induction trace generalizing P with
  | nil hmatch same =>
      exact ⟨P, [], rfl, (h.same_signatures hmatch).trans same, h.reserved, by simp⟩
  | cons hmatch edge update tail ih =>
      obtain ⟨mid, first, hf, hm, hfl⟩ := h.advance hn edge update tail.toPath
      obtain ⟨R, last, hl, hsame, hr, hll⟩ := ih hm
      refine ⟨R, first ++ last, ?_, hsame, hr, ?_⟩
      · simp [runLogged_append, hf, hl]
      · rw [List.length_append, eventReplayBudget_cons]
        exact Nat.add_le_add hfl hll

/-- The transfer leaves fit in `n` sites, by one-way atom mass conservation. -/
theorem singleton_transfer_count_le (n : Nat) (hn : 1 < n)
    {word : List Letter} {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    logTransferCount events ≤ n := by
  obtain ⟨_, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  have hs := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hs
  omega

/-- Every successful singleton-seed history has an exact-log event replay.
The terminal literal placement is deferred, but both named layer cycles
already match the requested endpoint. There is no reservation premise. -/
theorem history_event_replay_bound (n : Nat) (hn : 1 < n)
    {word : List Letter} {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    ∃ R replay, runLogged n hn (seed n) replay = some (R, events) ∧
      SameCyclicSignatures R Q ∧
      replay.length ≤ 4*n*logFusionCount events + (2*n+1)*logTransferCount events := by
  let : NeZero n := ⟨by omega⟩
  obtain ⟨k, terminal, trace, complete, _⟩ := singleton_run_ordered_forest hn hexec
  have hk : k = logTransferCount events := by simpa using trace.toPath.transfer_count
  have hlen : (forestLeaves terminal).length ≤ n := by
    rw [complete.length_eq, List.length_range, hk]
    exact singleton_transfer_count_le n hn hexec
  have hr := reserved_seed_of_forestPath (by omega : 0 < n) trace.toPath hlen
  obtain ⟨R, replay, hw, hs, _, hl⟩ := trace.reserved_replay hn ⟨hr, .refl _⟩
  exact ⟨R, replay, hw, hs, hl⟩

end RSR2History
