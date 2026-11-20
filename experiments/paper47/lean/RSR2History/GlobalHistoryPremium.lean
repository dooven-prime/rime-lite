import RSR2History.AllRHistoryPremiumExact
import RSR2History.QuadraticHistoryCompression
import Mathlib.Data.Set.Finite.List
import Mathlib.Data.Finset.Lattice.Fold

/-!
The global history-preservation premium is a genuine attained maximum over
finite actual observations. An observation contains only a literal placement
and its complete effective-event log; raw words are reachability witnesses.
The exact all-R family and the uniform compression theorem supply its bounds.
-/

namespace RSR2History

open RSR2.Parametric AllRTransfer

private def effectiveEventCode (n : Nat) : EffectiveEvent n →
    (Bool × Finset (Fin n) × Finset (Fin n) × Finset (Fin n)) ⊕ Finset (Fin n)
  | .fusion layer left right result => .inl (layer, left, right, result)
  | .transfer packet => .inr packet

private theorem effectiveEventCode_injective (n : Nat) :
    Function.Injective (effectiveEventCode n) := by
  intro x y h
  cases x <;> cases y <;> simp_all [effectiveEventCode]

instance effectiveEventFinite (n : Nat) : Finite (EffectiveEvent n) :=
  Finite.of_injective (effectiveEventCode n) (effectiveEventCode_injective n)

/-- The full observation contract, before imposing actual attainability. -/
abbrev CompleteObservation (n : Nat) := Placement n × List (EffectiveEvent n)

def attainableObservations (n : Nat) (hn : 1 < n) : Set (CompleteObservation n) :=
  { observation | ∃ word,
    runLogged n hn (seed n) word = some observation }

/-- Finiteness uses the actual seed event cap, not a bound on raw histories.
The ambient event encoding permits all tuples, so this is only an enclosing
finite set, not a proposed enumeration of attainable logs. -/
theorem attainableObservations_finite (n : Nat) (hn : 1 < n) :
    (attainableObservations n hn).Finite := by
  apply ((Set.toFinite (Set.univ : Set (Placement n))).prod
    (List.finite_length_le (EffectiveEvent n) (2 * n - 1))).subset
  intro observation h
  exact ⟨Set.mem_univ _, singleton_event_count_le n hn h⟩

/-- The execution witness is propositional and is not part of the data
being maximized over. Different words with the same pair give one element. -/
abbrev AttainableObservation (n : Nat) (hn : 1 < n) :=
  { observation : CompleteObservation n // observation ∈ attainableObservations n hn }

noncomputable instance attainableObservationFintype (n : Nat) (hn : 1 < n) :
    Fintype (AttainableObservation n hn) :=
  (attainableObservations_finite n hn).fintype

theorem attainableObservation_nonempty (n : Nat) (hn : 1 < n) :
    Nonempty (AttainableObservation n hn) :=
  ⟨⟨(seed n, []), ⟨[], rfl⟩⟩⟩

noncomputable def observationPremium (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) : Nat :=
  historyPremium n hn observation.val.1 observation.val.2 observation.property

/-- `G_n`: the maximum extra minimum length caused by preserving a complete
effective log at the very same literal endpoint. -/
noncomputable def globalHistoryPremium (n : Nat) (hn : 1 < n) : Nat :=
  Finset.univ.sup (observationPremium n hn)

theorem observationPremium_le_global (n : Nat) (hn : 1 < n)
    (observation : AttainableObservation n hn) :
    observationPremium n hn observation ≤ globalHistoryPremium n hn := by
  exact Finset.le_sup (Finset.mem_univ observation)

theorem historyPremium_le_global (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    historyPremium n hn Q events attain ≤ globalHistoryPremium n hn :=
  observationPremium_le_global n hn ⟨(Q, events), attain⟩

theorem globalHistoryPremium_attained (n : Nat) (hn : 1 < n) :
    ∃ observation : AttainableObservation n hn,
      observationPremium n hn observation = globalHistoryPremium n hn := by
  have := attainableObservation_nonempty n hn
  obtain ⟨observation, _, h⟩ := Finset.exists_mem_eq_sup
    Finset.univ Finset.univ_nonempty (observationPremium n hn)
  exact ⟨observation, h.symm⟩

theorem globalHistoryPremium_realized (n : Nat) (hn : 1 < n) :
    ∃ (Q : Placement n) (events : List (EffectiveEvent n))
      (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)),
      historyPremium n hn Q events attain = globalHistoryPremium n hn := by
  obtain ⟨observation, h⟩ := globalHistoryPremium_attained n hn
  exact ⟨observation.val.1, observation.val.2, observation.property, h⟩

/-- An upper-bound interface over actual pairs, without mentioning the
chosen finite enumeration of observations. -/
theorem globalHistoryPremium_le_iff (n : Nat) (hn : 1 < n) (bound : Nat) :
    globalHistoryPremium n hn ≤ bound ↔
      ∀ (Q : Placement n) (events : List (EffectiveEvent n))
        (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)),
        historyPremium n hn Q events attain ≤ bound := by
  constructor
  · intro h Q events attain
    exact (historyPremium_le_global n hn Q events attain).trans h
  · intro h
    apply Finset.sup_le
    intro observation _
    exact h observation.val.1 observation.val.2 observation.property

theorem historyDistance_le_quadratic (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    historyDistance n hn Q events attain ≤ quadraticHistoryBudget n := by
  obtain ⟨short, hw, hl⟩ := history_fiber_quadratic_bound n hn attain
  exact (minimumWordLength_le _ attain hw).trans hl

theorem historyPremium_le_quadratic (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    historyPremium n hn Q events attain ≤ quadraticHistoryBudget n := by
  exact (Nat.sub_le _ _).trans (historyDistance_le_quadratic n hn Q events attain)

theorem globalHistoryPremium_le_quadratic (n : Nat) (hn : 1 < n) :
    globalHistoryPremium n hn ≤ 6 * n * n - 2 * n - 1 := by
  apply (globalHistoryPremium_le_iff n hn _).2
  exact historyPremium_le_quadratic n hn

/-- The all-R family is an attained lower-bound witness, not an assertion
that it maximizes the premium at any fixed size. -/
theorem allR_premium_le_global (n : Nat) (hn : 3 ≤ n) :
    (3 * (n - 1) * (n - 2)) / 2 ≤ globalHistoryPremium n (by omega) := by
  let : NeZero n := ⟨by omega⟩
  have h := historyPremium_le_global n (by omega)
    (upperFullPacket n (by omega)) (allRHistory n) (allRHistory_attainable hn)
  simpa only [allR_history_premium_exact hn] using h

/-- All-parameter bounds for the finite attained global premium `G_n`.
Their quadratic asymptotic order follows mathematically; no exact global
maximum value, leading constant, or maximizer classification is asserted. -/
theorem global_history_premium_bounds (n : Nat) (hn : 3 ≤ n) :
    (3 * (n - 1) * (n - 2)) / 2 ≤ globalHistoryPremium n (by omega) ∧
      globalHistoryPremium n (by omega) ≤ 6 * n * n - 2 * n - 1 :=
  ⟨allR_premium_le_global n hn, globalHistoryPremium_le_quadratic n (by omega)⟩

end RSR2History
