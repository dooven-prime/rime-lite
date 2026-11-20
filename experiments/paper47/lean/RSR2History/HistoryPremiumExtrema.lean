import RSR2History.FiniteHistorySearch

/-! Fixed-literal-endpoint maxima and the exact two-stage decomposition
of the global history-preservation premium. No particular history family
is assumed to be extremal. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

def attainableEndpoints (n : Nat) (hn : 1 < n) : Set (Placement n) :=
  { Q | ∃ word, run n hn (seed n) word = some Q }

abbrev AttainableEndpoint (n : Nat) (hn : 1 < n) :=
  { Q : Placement n // Q ∈ attainableEndpoints n hn }

theorem attainableEndpoints_finite (n : Nat) (hn : 1 < n) :
    (attainableEndpoints n hn).Finite := Set.toFinite _

noncomputable instance attainableEndpointFintype (n : Nat) (hn : 1 < n) :
    Fintype (AttainableEndpoint n hn) :=
  (attainableEndpoints_finite n hn).fintype

def attainableLogsAt (n : Nat) (hn : 1 < n) (Q : Placement n) :
    Set (List (EffectiveEvent n)) :=
  { events | ∃ word, runLogged n hn (seed n) word = some (Q, events) }

theorem attainableLogsAt_finite (n : Nat) (hn : 1 < n) (Q : Placement n) :
    (attainableLogsAt n hn Q).Finite := by
  apply (List.finite_length_le (EffectiveEvent n) (2 * n - 1)).subset
  intro events hevents
  exact singleton_event_count_le n hn hevents

abbrev AttainableLogAt (n : Nat) (hn : 1 < n) (Q : Placement n) :=
  { events : List (EffectiveEvent n) // events ∈ attainableLogsAt n hn Q }

noncomputable instance attainableLogAtFintype (n : Nat) (hn : 1 < n)
    (Q : Placement n) : Fintype (AttainableLogAt n hn Q) :=
  (attainableLogsAt_finite n hn Q).fintype

theorem attainableLogAt_nonempty (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) : Nonempty (AttainableLogAt n hn Q.1) := by
  obtain ⟨events, word, hword⟩ := endpoint_log_attainable n hn Q.2
  exact ⟨⟨events, word, hword⟩⟩

/-- `Lambda_n(Q)`: the hardest attainable complete effective log at this
reachable literal endpoint. The endpoint's physical coordinates are fixed. -/
noncomputable def endpointHistoryMaximum (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) : Nat :=
  Finset.univ.sup (fun events : AttainableLogAt n hn Q.1 =>
    historyDistance n hn Q.1 events.1 events.2)

theorem historyDistance_le_endpointHistoryMaximum (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) (events : AttainableLogAt n hn Q.1) :
    historyDistance n hn Q.1 events.1 events.2 ≤ endpointHistoryMaximum n hn Q := by
  unfold endpointHistoryMaximum
  exact Finset.le_sup (α := Nat)
    (f := fun events : AttainableLogAt n hn Q.1 =>
      historyDistance n hn Q.1 events.1 events.2)
    (Finset.mem_univ events)

theorem endpointHistoryMaximum_attained (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    ∃ events : AttainableLogAt n hn Q.1,
      historyDistance n hn Q.1 events.1 events.2 = endpointHistoryMaximum n hn Q := by
  have := attainableLogAt_nonempty n hn Q
  obtain ⟨events, _, h⟩ := Finset.exists_mem_eq_sup Finset.univ
    Finset.univ_nonempty
    (fun events : AttainableLogAt n hn Q.1 => historyDistance n hn Q.1 events.1 events.2)
  exact ⟨events, h.symm⟩

theorem endpointHistoryMaximum_le_iff (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) (bound : Nat) :
    endpointHistoryMaximum n hn Q ≤ bound ↔
      ∀ events : AttainableLogAt n hn Q.1,
        historyDistance n hn Q.1 events.1 events.2 ≤ bound := by
  constructor
  · intro h events
    exact (historyDistance_le_endpointHistoryMaximum n hn Q events).trans h
  · intro h
    exact Finset.sup_le (fun events _ => h events)

theorem endpointHistoryMaximum_le_quadratic (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointHistoryMaximum n hn Q ≤ quadraticHistoryBudget n := by
  apply (endpointHistoryMaximum_le_iff n hn Q _).2
  intro events
  exact historyDistance_le_quadratic n hn Q.1 events.1 events.2

theorem endpointDistance_le_endpointHistoryMaximum (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointDistance n hn Q.1 Q.2 ≤ endpointHistoryMaximum n hn Q := by
  obtain ⟨events, hevents⟩ := endpointHistoryMaximum_attained n hn Q
  have hle := endpointDistance_le_historyDistance n hn Q.1 events.1 events.2
  exact hle.trans_eq hevents

noncomputable def endpointPremiumMaximum (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) : Nat :=
  endpointHistoryMaximum n hn Q - endpointDistance n hn Q.1 Q.2

theorem endpointPremiumMaximum_balance (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointDistance n hn Q.1 Q.2 + endpointPremiumMaximum n hn Q =
      endpointHistoryMaximum n hn Q :=
  Nat.add_sub_cancel' (endpointDistance_le_endpointHistoryMaximum n hn Q)

theorem historyPremium_le_endpointPremiumMaximum (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) (events : AttainableLogAt n hn Q.1) :
    historyPremium n hn Q.1 events.1 events.2 ≤ endpointPremiumMaximum n hn Q :=
  Nat.sub_le_sub_right (historyDistance_le_endpointHistoryMaximum n hn Q events) _

/-- At a fixed endpoint, histories maximizing cost are exactly those
maximizing premium: the endpoint-only distance is the same subtracted term. -/
theorem historyPremium_eq_endpointMaximum_iff (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) (events : AttainableLogAt n hn Q.1) :
    historyPremium n hn Q.1 events.1 events.2 = endpointPremiumMaximum n hn Q ↔
      historyDistance n hn Q.1 events.1 events.2 = endpointHistoryMaximum n hn Q := by
  have hbalance := historyPremium_balance n hn Q.1 events.1 events.2
  have hmaximum := endpointPremiumMaximum_balance n hn Q
  constructor <;> intro h <;> omega

theorem endpointPremiumMaximum_attained (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    ∃ events : AttainableLogAt n hn Q.1,
      historyPremium n hn Q.1 events.1 events.2 = endpointPremiumMaximum n hn Q := by
  obtain ⟨events, hevents⟩ := endpointHistoryMaximum_attained n hn Q
  exact ⟨events, (historyPremium_eq_endpointMaximum_iff n hn Q events).2 hevents⟩

theorem endpointPremiumMaximum_le_global (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) :
    endpointPremiumMaximum n hn Q ≤ globalHistoryPremium n hn := by
  obtain ⟨events, hevents⟩ := endpointPremiumMaximum_attained n hn Q
  exact hevents ▸ historyPremium_le_global n hn Q.1 events.1 events.2

/-- A globally premium-maximizing observation consists exactly of a
premium-maximizing literal endpoint and a hardest log at that endpoint. -/
theorem historyPremium_eq_global_iff (n : Nat) (hn : 1 < n)
    (Q : AttainableEndpoint n hn) (events : AttainableLogAt n hn Q.1) :
    historyPremium n hn Q.1 events.1 events.2 = globalHistoryPremium n hn ↔
      historyDistance n hn Q.1 events.1 events.2 = endpointHistoryMaximum n hn Q ∧
        endpointPremiumMaximum n hn Q = globalHistoryPremium n hn := by
  have hlocal := historyPremium_le_endpointPremiumMaximum n hn Q events
  have hglobal := endpointPremiumMaximum_le_global n hn Q
  constructor
  · intro h
    have heq : historyPremium n hn Q.1 events.1 events.2 =
        endpointPremiumMaximum n hn Q := by omega
    exact ⟨(historyPremium_eq_endpointMaximum_iff n hn Q events).1 heq, by omega⟩
  · rintro ⟨hhardest, hendpoint⟩
    exact ((historyPremium_eq_endpointMaximum_iff n hn Q events).2 hhardest).trans
      hendpoint

/-- The same classification, with successful execution as the only
attainability premise and no choice of a finite enumeration. -/
theorem actual_historyPremium_eq_global_iff (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    let endpoint : AttainableEndpoint n hn := ⟨Q, endpoint_attainable_of_logged hn attain⟩
    historyPremium n hn Q events attain = globalHistoryPremium n hn ↔
      historyDistance n hn Q events attain = endpointHistoryMaximum n hn endpoint ∧
        endpointPremiumMaximum n hn endpoint = globalHistoryPremium n hn :=
  historyPremium_eq_global_iff n hn
    ⟨Q, endpoint_attainable_of_logged hn attain⟩ ⟨events, attain⟩

/-- First maximize history cost at a fixed literal endpoint, subtract its
endpoint distance, then take a finite maximum over reachable endpoints. -/
theorem globalHistoryPremium_eq_endpoint_sup (n : Nat) (hn : 1 < n) :
    globalHistoryPremium n hn =
      Finset.univ.sup (endpointPremiumMaximum n hn) := by
  apply Nat.le_antisymm
  · apply (globalHistoryPremium_le_iff n hn _).2
    intro Q events attain
    let endpoint : AttainableEndpoint n hn :=
      ⟨Q, endpoint_attainable_of_logged hn attain⟩
    exact (historyPremium_le_endpointPremiumMaximum n hn endpoint ⟨events, attain⟩).trans
      (Finset.le_sup (Finset.mem_univ endpoint))
  · exact Finset.sup_le (fun Q _ => endpointPremiumMaximum_le_global n hn Q)

theorem globalHistoryPremium_endpoint_attained (n : Nat) (hn : 1 < n) :
    ∃ Q : AttainableEndpoint n hn,
      endpointPremiumMaximum n hn Q = globalHistoryPremium n hn := by
  obtain ⟨Q, events, attain, hpremium⟩ := globalHistoryPremium_realized n hn
  let endpoint : AttainableEndpoint n hn := ⟨Q, endpoint_attainable_of_logged hn attain⟩
  have hle := historyPremium_le_endpointPremiumMaximum n hn endpoint ⟨events, attain⟩
  have hge := endpointPremiumMaximum_le_global n hn endpoint
  change historyPremium n hn Q events attain ≤ endpointPremiumMaximum n hn endpoint at hle
  rw [hpremium] at hle
  exact ⟨endpoint, Nat.le_antisymm hge hle⟩

end RSR2History
