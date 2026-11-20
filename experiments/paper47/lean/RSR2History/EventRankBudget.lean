import RSR2History.BudgetedSilentPreparation
import RSR2History.CyclicEventPath
import RSR2.PacketRankLedger
import RSR2.TransferMass

namespace RSR2History
open RSR2.Parametric

/-- The rank pair is read from the actual placement, not from a chosen route. -/
def layerRanks (P : Placement n) : Nat × Nat := (layerRank P false, layerRank P true)

/-- Ranks after an effective event. These are determined by the event kind/layer. -/
def eventRanks (ranks : Nat × Nat) : EffectiveEvent n → Nat × Nat
  | .fusion false _ _ _ => (ranks.1-1, ranks.2)
  | .fusion true _ _ _ => (ranks.1, ranks.2-1)
  | .transfer _ => (ranks.1-1, ranks.2+1)

def rankBudget (n : Nat) (ranks : Nat × Nat) : Nat :=
  layerBudget n ranks.1 + layerBudget n ranks.2

/-- The initial silent interval and one new interval after every observed event. -/
def historyBudget (n : Nat) (ranks : Nat × Nat) : List (EffectiveEvent n) → Nat
  | [] => rankBudget n ranks
  | event :: events => rankBudget n ranks + 1 + historyBudget n (eventRanks ranks event) events

@[simp] theorem rankBudget_layerRanks (P : Placement n) :
    rankBudget n (layerRanks P) = silentBudget n P := rfl

theorem SameCyclicSignatures.ranks_eq {P Q : Placement n} (h : SameCyclicSignatures P Q) :
    layerRanks P = layerRanks Q := by
  apply Prod.ext
  · simpa only [layerRanks, layerRank, List.length_rotate] using congrArg List.length (h false).choose_spec
  · simpa only [layerRanks, layerRank, List.length_rotate] using congrArg List.length (h true).choose_spec

theorem rank_countP (P : Placement n) (layer : Layer) :
    layerRank P layer = (by classical
      exact (List.finRange n).countP (fun q => decide (occupiedAt P layer q))) := by
  classical
  rw [layerRank_eq_occupied_length]
  unfold occupiedSites
  rw [← List.countP_eq_length_filter]
  apply List.countP_congr
  intro q _
  simp only [bne_iff_ne, decide_eq_true_eq]
  exact Finset.nonempty_iff_ne_empty.symm.trans (packetAt_nonempty P layer q)

@[simp] theorem layerRank_lower (P : Placement n) :
    layerRank P false = lowerPacketCount P := rank_countP P false

@[simp] theorem layerRank_upper (P : Placement n) :
    layerRank P true = upperPacketCount P := by
  rw [upperPacketCount_eq_countP]
  exact rank_countP P true

theorem EventStep.ranks_update {n : Nat} {hn : 1 < n} {P Q : Placement n}
    {letter : Letter} {event : EffectiveEvent n} (h : EventStep n hn P Q letter event) :
    layerRanks Q = eventRanks (layerRanks P) event := by
  classical
  have hl := step_lowerPacketCount_balance n hn P Q letter h.1
  have ht := step_totalPacketCount_balance n hn P Q letter h.1
  cases letter with
  | p layer => have he := h.2; simp [emittedEvents] at he
  | d layer =>
      have hb : occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn) := by
        by_contra hb
        have he := h.2
        simp [emittedEvents, hb] at he
      have he := h.2
      simp only [emittedEvents, if_pos hb, List.singleton_inj] at he
      subst event
      cases layer <;> apply Prod.ext <;>
        simp only [layerRanks, eventRanks, layerRank_lower, layerRank_upper]
      all_goals simp [lowerFusionCharge, upperFusionCharge, hb, totalPacketCount] at hl ht
      all_goals omega
  | v =>
      have he : event = .transfer (packetAt P false (site0 n (by omega))) := by
        simpa [emittedEvents] using h.2.symm
      subst event
      apply Prod.ext <;>
        simp only [layerRanks, eventRanks, layerRank_lower, layerRank_upper]
      all_goals simp [lowerFusionCharge, upperFusionCharge, totalPacketCount] at hl ht
      all_goals omega

/-- Replace each maximal silent stretch by one bounded route. The induction
allows a cyclic-equivalent representative as its current physical start. -/
theorem history_short_from (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events))
    (P' : Placement n) (hsig : SameCyclicSignatures P' P) :
    ∃ short, runLogged n hn P' short = some (Q, events) ∧
      short.length ≤ historyBudget n (layerRanks P) events := by
  induction word generalizing P P' events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      obtain ⟨rfl, rfl⟩ := he
      obtain ⟨short, hrun, hlen⟩ := silent_preparation_short n hn P' P hsig
      refine ⟨short, hrun, ?_⟩
      change short.length ≤ rankBudget n (layerRanks P)
      rw [← hsig.ranks_eq, rankBudget_layerRanks]
      exact hlen
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
              have hrQ : runLogged n hn R rest = some (Q, later) := by simpa [he.1] using hr
              rcases emittedEvents_nil_or_singleton n hn P letter with hempty | ⟨event, hevent⟩
              · have hPR := (show SilentStep n hn P R letter from ⟨hs, hempty⟩).sameCyclicSignatures
                have hlog : events = later := by simpa [hempty] using he.2.symm
                subst events
                obtain ⟨short, hw, hlen⟩ := ih hrQ P' (hsig.trans hPR)
                exact ⟨short, hw, by simpa [hPR.ranks_eq] using hlen⟩
              · have hstep : EventStep n hn P R letter event := ⟨hs, hevent⟩
                have hlog : events = event :: later := by simpa [hevent] using he.2.symm
                subst events
                obtain ⟨pre, hp, hpre⟩ := silent_preparation_short n hn P' P hsig
                obtain ⟨tail, htail, hlen⟩ := ih hrQ R (.refl R)
                refine ⟨pre ++ [letter] ++ tail, ?_, ?_⟩
                · simp [runLogged_append, hp, runLogged, hs, hevent, htail]
                · rw [← rankBudget_layerRanks, hsig.ranks_eq] at hpre
                  rw [hstep.ranks_update] at hlen
                  simp only [List.length_append, List.length_singleton, historyBudget]
                  omega

/-- H3's event-log-dependent budget preserves exact event tuples and the
literal endpoint in one guarded raw execution. -/
theorem history_fiber_rank_bound (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (h : ∃ word, runLogged n hn P word = some (Q, events)) :
    ∃ short, runLogged n hn P short = some (Q, events) ∧
      short.length ≤ historyBudget n (layerRanks P) events := by
  obtain ⟨word, hw⟩ := h
  exact history_short_from n hn word hw P (.refl P)

/-- Rank trajectory (including the initial pair) depends only on the event log. -/
def eventRankTrace (ranks : Nat × Nat) : List (EffectiveEvent n) → List (Nat × Nat)
  | [] => [ranks]
  | event :: events => ranks :: eventRankTrace (eventRanks ranks event) events

/-- The recursive budget is exactly the advertised sum over event intervals. -/
theorem historyBudget_eq_rank_sum (n : Nat) (ranks : Nat × Nat)
    (events : List (EffectiveEvent n)) :
    historyBudget n ranks events = events.length +
      ((eventRankTrace ranks events).map (rankBudget n)).sum := by
  induction events generalizing ranks with
  | nil => simp [historyBudget, eventRankTrace]
  | cons event events ih => simp [historyBudget, eventRankTrace, ih]; omega

end RSR2History
