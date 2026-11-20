import RSR2History.EventRankBudget

namespace RSR2History
open RSR2.Parametric

/-- A uniform two-layer silent budget, before substituting the event count. -/
def twoLayerBudget (n : Nat) : Nat := 2*(2*n+1)*(n-1)

def eventCountBudget (n count : Nat) : Nat := (count+1)*twoLayerBudget n + count

/-- The uniform cubic budget, with its event-count term written as `2n-1`. -/
def cubicHistoryBudget (n : Nat) : Nat := 4*n*(2*n+1)*(n-1)+(2*n-1)

theorem historyBudget_le_eventCountBudget (n : Nat) (hn : 1 < n)
    (word : List Letter) {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    historyBudget n (layerRanks P) events ≤ eventCountBudget n events.length := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      rw [he.2]
      simpa [historyBudget, eventCountBudget, twoLayerBudget] using silentBudget_le n (by omega) P
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              have htail := ih (by simpa [he.1] using hr)
              rcases emittedEvents_nil_or_singleton n hn P letter with hempty | ⟨event, hevent⟩
              · have hPR := (show SilentStep n hn P R letter from ⟨hs, hempty⟩).sameCyclicSignatures
                have hlog : events = later := by simpa [hempty] using he.2.symm
                subst events
                simpa [hPR.ranks_eq] using htail
              · have hstep : EventStep n hn P R letter event := ⟨hs, hevent⟩
                have hlog : events = event :: later := by simpa [hevent] using he.2.symm
                subst events
                have hpre := silentBudget_le n (by omega) P
                rw [← rankBudget_layerRanks] at hpre
                rw [hstep.ranks_update] at htail
                simp only [historyBudget, List.length_cons, eventCountBudget] at *
                change rankBudget n (layerRanks P) ≤ twoLayerBudget n at hpre
                nlinarith

/-- Each fusion consumes a packet and each transfer consumes at least one
remaining lower atom. This potential counts neither coordinates nor letters. -/
noncomputable def eventPotential (P : Placement n) : Nat :=
  lowerAtomMass P + totalPacketCount P

theorem successful_step_event_potential (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hs : step n hn P letter = some Q) :
    eventPotential Q + (emittedEvents n hn P letter).length ≤ eventPotential P := by
  classical
  have ht := step_totalPacketCount_balance n hn P Q letter hs
  have hm := step_transferMass_balance n hn P Q letter hs
  have hP := upperAtomMass_add_lowerAtomMass P
  have hQ := upperAtomMass_add_lowerAtomMass Q
  have hcharge : (emittedEvents n hn P letter).length ≤
      lowerFusionCharge n hn P letter + upperFusionCharge n hn P letter +
        transferLetterMass n hn P letter := by
    cases letter with
    | p layer => simp [emittedEvents, lowerFusionCharge, upperFusionCharge, transferLetterMass]
    | d layer =>
        cases layer with
        | false =>
            by_cases hb : occupiedAt P false (site0 n (by omega)) ∧ occupiedAt P false (site1 n hn) <;>
              simp [emittedEvents, lowerFusionCharge, upperFusionCharge, transferLetterMass, hb]
        | true =>
            by_cases hb : occupiedAt P true (site0 n (by omega)) ∧ occupiedAt P true (site1 n hn) <;>
              simp [emittedEvents, lowerFusionCharge, upperFusionCharge, transferLetterMass, hb]
    | v =>
        obtain ⟨hg, _⟩ := (step_v_eq_some_iff n hn P Q).mp hs
        obtain ⟨a, ha⟩ := hg.1
        have hone : 1 ≤ packetAtomMass P false (site0 n (by omega)) := by
          apply List.one_le_countP_iff.mpr
          exact ⟨a, List.mem_finRange a, by simpa [packet] using ha⟩
        simpa [emittedEvents, lowerFusionCharge, upperFusionCharge, transferLetterMass] using hone
  unfold eventPotential
  omega

theorem runLogged_event_potential (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    eventPotential Q + events.length ≤ eventPotential P := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.1, he.2]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              have htail := ih (by simpa [he.1] using hr)
              have hstep := successful_step_event_potential n hn P R letter hs
              have hlen := congrArg List.length he.2
              simp only [List.length_append] at hlen
              omega

theorem eventPotential_pos (n : Nat) (hn : 0 < n) (P : Placement n) : 1 ≤ eventPotential P := by
  classical
  let a : Fin n := ⟨0, hn⟩
  have hoc : occupiedAt P (P a).1 (P a).2 := ⟨a, rfl⟩
  have hrank : 1 ≤ layerRank P (P a).1 := by
    rw [rank_countP]
    exact List.one_le_countP_iff.mpr ⟨(P a).2, List.mem_finRange _, by simp [hoc]⟩
  cases hl : (P a).1 with
  | false => simp only [hl, layerRank_lower] at hrank; unfold eventPotential totalPacketCount; omega
  | true => simp only [hl, layerRank_upper] at hrank; unfold eventPotential totalPacketCount; omega

theorem singleton_event_count_le (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) : events.length ≤ 2*n-1 := by
  obtain ⟨word, hw⟩ := hexec
  have h := runLogged_event_potential n hn word hw
  have hp := eventPotential_pos n (by omega) Q
  have hs : eventPotential (seed n) = 2*n := by
    have hmass := upperAtomMass_add_lowerAtomMass (seed n)
    rw [seed_upperAtomMass] at hmass
    simp only [eventPotential, seed_totalPacketCount]
    omega
  rw [hs] at h
  omega

theorem eventCountBudget_le_cubic (n count : Nat) (hn : 0 < n) (hk : count ≤ 2*n-1) :
    eventCountBudget n count ≤ cubicHistoryBudget n := by
  have hcount : count+1 ≤ 2*n := by omega
  have hm := Nat.mul_le_mul_right (twoLayerBudget n) hcount
  unfold eventCountBudget cubicHistoryBudget
  unfold twoLayerBudget at hm ⊢
  nlinarith

/-- H3: every actual singleton-seed complete event-log/literal-endpoint fiber
has a representative within the uniform cubic raw-letter budget. -/
theorem history_fiber_cubic_bound (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ cubicHistoryBudget n := by
  obtain ⟨short, hw, hlen⟩ := history_fiber_rank_bound n hn hexec
  have hrank := historyBudget_le_eventCountBudget n hn short hw
  have hevents := singleton_event_count_le n hn hexec
  have hbound := eventCountBudget_le_cubic n events.length (by omega) hevents
  exact ⟨short, hw, hlen.trans (hrank.trans hbound)⟩

/-- The same non-increase conclusion with the stronger log-dependent budget. -/
theorem history_compression_rank_length_le_min (n : Nat) (hn : 1 < n)
    (word : List Letter) {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ min word.length (historyBudget n (layerRanks (seed n)) events) := by
  by_cases hsmall : word.length ≤ historyBudget n (layerRanks (seed n)) events
  · exact ⟨word, hexec, by simp [hsmall]⟩
  · obtain ⟨short, hw, hlen⟩ := history_fiber_rank_bound n hn ⟨word, hexec⟩
    exact ⟨short, hw, by simpa [min_eq_right (Nat.le_of_lt (Nat.lt_of_not_ge hsmall))] using hlen⟩

/-- Choosing the original input when it is shorter makes compression
non-increasing, without claiming a shortest-word algorithm. -/
theorem history_compression_length_le_min (n : Nat) (hn : 1 < n)
    (word : List Letter) {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ min word.length (cubicHistoryBudget n) := by
  by_cases hsmall : word.length ≤ cubicHistoryBudget n
  · exact ⟨word, hexec, by simp [hsmall]⟩
  · obtain ⟨short, hw, hlen⟩ := history_fiber_cubic_bound n hn ⟨word, hexec⟩
    exact ⟨short, hw, by simpa [min_eq_right (Nat.le_of_lt (Nat.lt_of_not_ge hsmall))] using hlen⟩

/-- Paper-facing H3 statement: the same original guarded executor, exact
complete effective-event tuples, literal endpoint, and expanded cubic budget. -/
theorem history_fiber_guarded_cubic_bound (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ short, run n hn (seed n) short = some Q ∧
      runLogged n hn (seed n) short = some (Q, events) ∧
      short.length ≤ 4*n*(2*n+1)*(n-1)+(2*n-1) := by
  obtain ⟨short, hw, hlen⟩ := history_fiber_cubic_bound n hn hexec
  refine ⟨short, ?_, hw, hlen⟩
  simpa [hw] using (runLogged_project n hn (seed n) short).symm

end RSR2History
