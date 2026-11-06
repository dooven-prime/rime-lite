import FusionLogReplay.BudgetedReplay
import FusionLogReplay.EndpointPlan

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

def normalFormBudget (n t s : ℕ) : ℕ :=
  3 * n * (t - s) + (n - t) * (t - s) + Nat.choose (t - s) 2 +
    (3 * n - s) * (s - 1) + (n - 1)

def normalFormTransferBudget (n t s : ℕ) : ℕ :=
  (n - t) * (t - s) + Nat.choose (t - s) 2 + (n - s) * (s - 1)

/-- A joint certificate for the real fusion replay and the real M3 alignment.
Its counters count the constituent nonempty M1 batches and hole transfers. -/
structure JointReplayPlan (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n))) where
  last : Execution n (ZMod n)
  fusion : FusionReplayPlan F s last
  alignment : EndpointPlan F last target (packetRank target)
  rank_match : packetRank last.placed = packetRank target

namespace JointReplayPlan

variable {F : Finset (ZMod n)} {s : Execution n (ZMod n)}
variable {target : Placement n (Finset (ZMod n))}

def word (plan : JointReplayPlan F s target) : List Letter :=
  plan.fusion.word ++ plan.alignment.word

def batches (plan : JointReplayPlan F s target) : ℕ :=
  plan.fusion.batches + plan.alignment.flow.batches

def transfers (plan : JointReplayPlan F s target) : ℕ :=
  plan.fusion.transfers + plan.alignment.flow.transfers

theorem event_count (plan : JointReplayPlan F s target) :
    plan.fusion.events.length = packetRank s.placed - packetRank target := by
  have ledger := plan.fusion.rank_ledger
  rw [plan.rank_match] at ledger
  omega

theorem execute (plan : JointReplayPlan F s target) (rank_le : packetRank target ≤ n) :
    eventTrace F s plan.word = plan.fusion.events ∧
      (run F s plan.word).placed = target := by
  obtain ⟨free, executed, _⟩ := plan.alignment.execute rank_le
  constructor
  · rw [word, eventTrace_append, plan.fusion.run_eq,
      (eventTrace_eq_nil_iff F plan.last _).mpr free,
      List.append_nil, plan.fusion.trace_eq]
  · rw [word, run_append, plan.fusion.run_eq, executed]

theorem length_bound (plan : JointReplayPlan F s target) (rank_le : packetRank target ≤ n) :
    plan.word.length ≤ normalFormBudget n (packetRank s.placed) (packetRank target) := by
  have fusionCost := plan.fusion.sharp_length_bound
  rw [plan.event_count] at fusionCost
  have alignmentCost := (plan.alignment.execute rank_le).2.2
  simp only [word, List.length_append, normalFormBudget]
  omega

theorem batch_bound (plan : JointReplayPlan F s target) (rank_pos : 1 ≤ packetRank target) :
    plan.batches ≤ packetRank s.placed - 1 := by
  have fusionCost := plan.fusion.batch_bound
  have alignmentCost := plan.alignment.batch_bound
  have rank := plan.fusion.rank_ledger
  rw [plan.rank_match] at rank
  dsimp [batches]
  omega

theorem transfer_bound (plan : JointReplayPlan F s target) :
    plan.transfers ≤
      normalFormTransferBudget n (packetRank s.placed) (packetRank target) := by
  have fusionCost := plan.fusion.transfer_bound
  rw [plan.event_count] at fusionCost
  have alignmentCost := plan.alignment.transfer_bound
  dsimp [transfers, normalFormTransferBudget]
  omega

end JointReplayPlan

/-- The manuscript's B(n,t,s) and K/M upper bounds on the SourceOrdered domain.
The same certificate supplies the complete log, literal endpoint, and costs. -/
theorem sourceOrdered_log_endpoint_budget
    (F : Finset (ZMod n)) (s : LoggedExecution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n) (ordered : SourceOrdered s.state.placed) :
    ∃ plan : JointReplayPlan F s.state (run F s.state word).placed,
      (runLogged F s plan.word).fullLog = (runLogged F s word).fullLog ∧
      (runLogged F s plan.word).state.placed = (runLogged F s word).state.placed ∧
      plan.word.length ≤ normalFormBudget n (packetRank s.state.placed)
        (packetRank (run F s.state word).placed) ∧
      plan.batches ≤ packetRank s.state.placed - 1 ∧
      plan.transfers ≤ normalFormTransferBudget n (packetRank s.state.placed)
        (packetRank (run F s.state word).placed) := by
  obtain ⟨last, fusion, trace, lastOrdered, same⟩ :=
    replay_complete_events_plan F s.state s.state word hn ordered ordered rfl
  have targetOrdered := run_ordered F s.state word (by omega) ordered
  obtain ⟨alignment⟩ := align_sourceOrdered_endpoint_plan F last
    (run F s.state word).placed hn lastOrdered targetOrdered same
  let plan : JointReplayPlan F s.state (run F s.state word).placed :=
    ⟨last, fusion, alignment, congrArg Finset.card same⟩
  have rank_le := packetRank_le_sites _ (sourceOrdered_uniquePackets _ targetOrdered)
  have rank_pos : 1 ≤ packetRank (run F s.state word).placed := by
    have pos := sourceOrdered_blocks_card_pos _ targetOrdered
    rw [← packetSet_eq_placedBlocks _ targetOrdered] at pos
    exact pos
  have executed := plan.execute rank_le
  refine ⟨plan, ?_, ?_, plan.length_bound rank_le, plan.batch_bound rank_pos,
    plan.transfer_bound⟩
  · rw [runLogged_fullLog, runLogged_fullLog, executed.1]
    exact congrArg (List.append s.fullLog) trace
  · rw [runLogged_state, runLogged_state, executed.2]

end FusionLogReplay
