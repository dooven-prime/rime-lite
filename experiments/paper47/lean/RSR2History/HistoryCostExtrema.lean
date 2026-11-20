import RSR2History.QuadraticHistoryCompression
import RSR2.SingleVacancyOptimality

/-!
Budget extrema and actual hard history fibers are different notions. The
former are arithmetic; the latter follow by projecting to the already
proved single-vacancy literal endpoint. No new geometry is assumed here.
-/
namespace RSR2History
open RSR2.Parametric

/-- The current event/rank budget attains its uniform polynomial at these
counts. This statement does not assert a lower bound on witness lengths. -/
theorem reservation_budget_maximal_event_counts (n : Nat) (hn : 0 < n) :
    4*n*(n-1)+(2*n+1)*n+layerBudget n 0+layerBudget n 1 = quadraticHistoryBudget n := by
  simp [layerBudget, quadraticHistoryBudget]
  have he : n-1+1 = n := by omega
  have hm := congrArg (fun k => 4*n*k) he
  simp only [Nat.mul_add, Nat.mul_one] at hm
  have hc : 4*n*(n-1)+(2*n+1)*n+(n-1)+2*n+1 = 6*n*n := by nlinarith
  omega

/-- Fixing a complete event log cannot weaken a literal-endpoint lower
bound. This holds for every log compatible with the single-vacancy target. -/
theorem singleVacancy_history_length_lower_bound (n : Nat) (hn : 3 ≤ n)
    {word : List Letter} {events : List (EffectiveEvent n)}
    (hexec : runLogged n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega), events)) :
    n*(n-1) ≤ word.length := by
  apply singleVacancyEndpoint_length_lower_bound n hn word
  simpa [hexec] using (runLogged_project n (by omega) (seed n) word).symm

theorem singleVacancy_history_minimal_word_unique (n : Nat) (hn : 3 ≤ n)
    {word : List Letter} {events : List (EffectiveEvent n)}
    (hexec : runLogged n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega), events))
    (hlen : word.length = n*(n-1)) : word = singleVacancyWord n := by
  apply singleVacancyEndpoint_minimal_word_unique n hn word _ hlen
  simpa [hexec] using (runLogged_project n (by omega) (seed n) word).symm

/-- An actually attained full-history fiber has exact minimum n(n-1) and
a unique shortest raw word. The log is that of the explicit vacancy word. -/
theorem singleVacancy_history_exact_minimum (n : Nat) (hn : 3 ≤ n) :
    ∃ events : List (EffectiveEvent n),
      runLogged n (by omega) (seed n) (singleVacancyWord n) =
        some (singleVacancyEndpoint n (by omega), events) ∧
      (singleVacancyWord n).length = n*(n-1) ∧
      ∀ word, runLogged n (by omega) (seed n) word =
          some (singleVacancyEndpoint n (by omega), events) →
        n*(n-1) ≤ word.length ∧ (word.length = n*(n-1) ↔ word = singleVacancyWord n) := by
  obtain ⟨events, hw⟩ := runLogged_exists_of_run n (by omega) (singleVacancyWord_run n hn)
  refine ⟨events, hw, singleVacancyWord_length n hn, ?_⟩
  intro word he
  refine ⟨singleVacancy_history_length_lower_bound n hn he, ?_⟩
  constructor
  · exact singleVacancy_history_minimal_word_unique n hn he
  · rintro rfl
    exact singleVacancyWord_length n hn

/-- Any uniform full-observation witness bound must be at least n(n-1).
The quantified formulation avoids introducing a maximum over raw words. -/
theorem uniform_history_bound_ge_quadratic (n : Nat) (hn : 3 ≤ n) (bound : Nat)
    (cover : ∀ (Q : Placement n) (events : List (EffectiveEvent n)),
      (∃ word, runLogged n (by omega) (seed n) word = some (Q, events)) →
        ∃ short, runLogged n (by omega) (seed n) short = some (Q, events) ∧
          short.length ≤ bound) : n*(n-1) ≤ bound := by
  obtain ⟨events, hw, _, _⟩ := singleVacancy_history_exact_minimum n hn
  obtain ⟨short, hs, hl⟩ := cover _ events ⟨singleVacancyWord n, hw⟩
  exact (singleVacancy_history_length_lower_bound n hn hs).trans hl

end RSR2History
