import FusionLogInterpretation.InitialEncoding
import FusionLogInterpretation.PhysicalRoutes

namespace FusionLogInterpretation

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- Transport the frozen bound without changing its word, gaps or costs.
An existing actual log prefix is retained literally, not decoded backwards
as a union of the new initial packet labels. -/
theorem interpreted_sourceOrdered_budget (labels : ZMod n → Finset α)
    (G : Finset (ZMod n)) (F : Finset α)
    (source : Execution n (ZMod n)) (actual : LoggedExecution n α)
    (word : List Letter) (hn : 3 ≤ n) (ordered : SourceOrdered source.placed)
    (same : actual.state.placed = expandPlacement labels source.placed) :
    ∃ plan : InterpretedJointPlan labels G F source actual.state (run G source word).placed,
      (runLogged F actual plan.word).fullLog = (runLogged F actual word).fullLog ∧
      (runLogged F actual plan.word).state.placed = (runLogged F actual word).state.placed ∧
      plan.word.length ≤ normalFormBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card ∧
      plan.batches ≤ (occupiedSites actual.state.placed).card - 1 ∧
      plan.transfers ≤ normalFormTransferBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card := by
  obtain ⟨encoded, logs, endpoint, cost, batches, transfers⟩ :=
    sourceOrdered_log_endpoint_budget G ⟨source, []⟩ word hn ordered
  have sourceTrace : eventTrace G source encoded.word = eventTrace G source word := by
    simpa only [runLogged_fullLog, List.nil_append] using logs
  have sourceEndpoint : (run G source encoded.word).placed = (run G source word).placed := by
    simpa only [runLogged_state] using endpoint
  obtain ⟨plan, encoding⟩ := jointPlan_interprets labels G F source actual.state
    (run G source word).placed encoded same
  have wordEq : plan.word = encoded.word :=
    plan.word_eq.trans (congrArg JointReplayPlan.word encoding)
  have batchesEq : plan.batches = encoded.batches :=
    plan.batches_eq.trans (congrArg JointReplayPlan.batches encoding)
  have transfersEq : plan.transfers = encoded.transfers :=
    plan.transfers_eq.trans (congrArg JointReplayPlan.transfers encoding)
  have rankStart : packetRank source.placed = (occupiedSites actual.state.placed).card := by
    rw [same, occupiedSites_expand]
    exact packetRank_eq_occupied _ (sourceOrdered_uniquePackets _ ordered)
  have finalOrdered := run_ordered G source word (by omega) ordered
  have rankEnd : packetRank (run G source word).placed =
      (occupiedSites (run F actual.state word).placed).card := by
    rw [run_support_interprets labels G F source actual.state same word]
    exact packetRank_eq_occupied _ (sourceOrdered_uniquePackets _ finalOrdered)
  refine ⟨plan, ?_, ?_, ?_, ?_, ?_⟩
  · rw [runLogged_fullLog, runLogged_fullLog, wordEq,
      eventTrace_interprets labels G F source actual.state same encoded.word,
      eventTrace_interprets labels G F source actual.state same word, sourceTrace]
  · rw [runLogged_state, runLogged_state, wordEq,
      run_placement_interprets labels G F source actual.state same encoded.word,
      run_placement_interprets labels G F source actual.state same word, sourceEndpoint]
  · rw [wordEq]
    simpa only [rankStart, rankEnd] using cost
  · rw [batchesEq]
    simpa only [rankStart] using batches
  · rw [transfersEq]
    simpa only [rankStart, rankEnd] using transfers

def initialIndexExecution (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) : Execution n (ZMod n) :=
  ⟨canonicalPlacement P nonempty, none, []⟩

/-- Actual-word compression for arbitrary initial packet labels and sites.
No singleton-seed provenance, clean condition, or input order lift is assumed. -/
theorem arbitrary_initial_log_endpoint_budget
    (F : Finset α) (actual : LoggedExecution n α) (word : List Letter) (hn : 3 ≤ n)
    (nonempty : (occupiedSites actual.state.placed).Nonempty) :
    ∃ plan : InterpretedJointPlan (siteLabels actual.state.placed) ∅ F
        (initialIndexExecution actual.state.placed nonempty) actual.state
        (run ∅ (initialIndexExecution actual.state.placed nonempty) word).placed,
      (runLogged F actual plan.word).fullLog = (runLogged F actual word).fullLog ∧
      (runLogged F actual plan.word).state.placed = (runLogged F actual word).state.placed ∧
      plan.word.length ≤ normalFormBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card ∧
      plan.batches ≤ (occupiedSites actual.state.placed).card - 1 ∧
      plan.transfers ≤ normalFormTransferBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card :=
  interpreted_sourceOrdered_budget (siteLabels actual.state.placed) ∅ F
    (initialIndexExecution actual.state.placed nonempty) actual word hn
    (canonicalPlacement_ordered actual.state.placed nonempty)
    (initial_placement_interprets actual.state.placed nonempty)

theorem named_occupied_rank {r : ℕ} [NeZero r]
    (named : LegalNamedPlacement n r α) : (occupiedSites named.placed).card = r := by
  have sites : occupiedSites named.placed = Finset.univ.image named.position := by
    ext q
    simp only [occupiedSites, Finset.mem_filter, Finset.mem_univ, true_and,
      Finset.mem_image]
    constructor
    · intro occupied
      obtain ⟨i, hi⟩ := named.only_named q occupied
      exact ⟨i, hi⟩
    · rintro ⟨i, rfl⟩
      rw [named.placed_at]
      simp
  rw [sites, Finset.card_image_of_injective _ named.position_injective]
  simp

theorem arbitrary_initial_log_endpoint_representative
    (F : Finset α) (actual : LoggedExecution n α) (word : List Letter) (hn : 3 ≤ n)
    (nonempty : (occupiedSites actual.state.placed).Nonempty) :
    ∃ representative : List Letter,
      (runLogged F actual representative).fullLog = (runLogged F actual word).fullLog ∧
      (runLogged F actual representative).state.placed = (runLogged F actual word).state.placed ∧
      representative.length ≤ normalFormBudget n (occupiedSites actual.state.placed).card
        (occupiedSites (run F actual.state word).placed).card := by
  obtain ⟨plan, logs, endpoint, cost, _, _⟩ :=
    arbitrary_initial_log_endpoint_budget F actual word hn nonempty
  exact ⟨plan.word, logs, endpoint, cost⟩

theorem named_initial_log_endpoint_representative {r : ℕ} [NeZero r]
    (F : Finset α) (actual : LoggedExecution n α) (word : List Letter) (hn : 3 ≤ n)
    (named : LegalNamedPlacement n r α) (source : actual.state.placed = named.placed) :
    ∃ representative : List Letter,
      (runLogged F actual representative).fullLog = (runLogged F actual word).fullLog ∧
      (runLogged F actual representative).state.placed = (runLogged F actual word).state.placed ∧
      representative.length ≤ normalFormBudget n r
        (occupiedSites (run F actual.state word).placed).card := by
  have rank : (occupiedSites actual.state.placed).card = r := by
    rw [source, named_occupied_rank]
  have nonempty : (occupiedSites actual.state.placed).Nonempty := by
    apply Finset.card_pos.mp
    rw [rank]
    exact NeZero.pos r
  have result := arbitrary_initial_log_endpoint_representative F actual word hn nonempty
  simpa only [rank] using result

end FusionLogInterpretation
