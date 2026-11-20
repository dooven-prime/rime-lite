import RSR2History.ReservedHistoryReplay
import RSR2History.ReservationBudget

/-! Unconditional quadratic representatives of the complete effective-event
log and literal endpoint, on the original five-letter guarded machine. -/
namespace RSR2History
open RSR2.Parametric

def quadraticHistoryBudget (n : Nat) : Nat := 6*n*n-2*n-1

theorem SameCyclicSignatures.silentBudget_eq {P Q : Placement n}
    (same : SameCyclicSignatures P Q) : silentBudget n P = silentBudget n Q := by
  change rankBudget n (layerRanks P) = rankBudget n (layerRanks Q)
  rw [same.ranks_eq]

/-- Replay pays a linear cost per effective event, then one final
rank-sensitive silent route restores the entire literal endpoint. -/
theorem history_fiber_reservation_bound (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ 4*n*logFusionCount events +
        (2*n+1)*logTransferCount events + silentBudget n Q := by
  obtain ⟨word, hw⟩ := hexec
  obtain ⟨R, replay, hr, hs, hl⟩ := history_event_replay_bound n hn hw
  obtain ⟨finish, hf, hfl⟩ := silent_preparation_short n hn R Q hs
  rw [hs.silentBudget_eq] at hfl
  refine ⟨replay ++ finish, ?_, ?_⟩
  · simp [runLogged_append, hr, hf]
  · simp only [List.length_append]
    exact Nat.add_le_add hl hfl

/-- Every actually attained full observation has a uniformly quadratic
raw-word witness. No forest, direction or reservation hypothesis remains. -/
theorem history_fiber_quadratic_bound (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ quadraticHistoryBudget n := by
  obtain ⟨word, hw⟩ := hexec
  obtain ⟨short, hs, hl⟩ := history_fiber_reservation_bound n hn ⟨word, hw⟩
  exact ⟨short, hs, reservation_replay_length_le_uniform n hn hw hl⟩

/-- Choosing the input when shorter proves non-increase, while retaining
every ordered effective event and every final physical atom coordinate. -/
theorem history_compression_quadratic_length_le_min (n : Nat) (hn : 1 < n)
    (word : List Letter) {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ min word.length (quadraticHistoryBudget n) := by
  by_cases hsmall : word.length ≤ quadraticHistoryBudget n
  · exact ⟨word, hexec, by simp [hsmall]⟩
  · obtain ⟨short, hw, hl⟩ := history_fiber_quadratic_bound n hn ⟨word, hexec⟩
    exact ⟨short, hw, by simpa [min_eq_right (Nat.le_of_lt (Nat.lt_of_not_ge hsmall))] using hl⟩

/-- Paper-facing guarded statement, with the explicit polynomial bound. -/
theorem history_fiber_guarded_quadratic_bound (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, run n hn (seed n) short = some Q ∧
      runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ 6*n*n-2*n-1 := by
  obtain ⟨short, hw, hl⟩ := history_fiber_quadratic_bound n hn hexec
  exact ⟨short, by simpa [hw] using (runLogged_project n hn (seed n) short).symm, hw, hl⟩

end RSR2History
