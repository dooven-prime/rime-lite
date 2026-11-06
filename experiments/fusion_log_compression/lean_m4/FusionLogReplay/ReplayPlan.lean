import FusionLogReplay.FusionStage

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]

/-- Each stage starts at the actual output of the preceding stage. -/
inductive FusionReplayPlan (F : Finset (ZMod n)) :
    Execution n (ZMod n) → Execution n (ZMod n) → Type where
  | done (s) : FusionReplayPlan F s s
  | step {s last} (stage : FusionStage F s)
      (tail : FusionReplayPlan F stage.next last) : FusionReplayPlan F s last

namespace FusionReplayPlan

variable {F : Finset (ZMod n)}

def word {s last : Execution n (ZMod n)} : FusionReplayPlan F s last → List Letter
  | .done _ => []
  | .step stage tail => stage.word ++ tail.word

def events {s last : Execution n (ZMod n)} :
    FusionReplayPlan F s last → List (FusionRecord (ZMod n))
  | .done _ => []
  | .step stage tail => stage.event :: tail.events

def batches {s last : Execution n (ZMod n)} : FusionReplayPlan F s last → ℕ
  | .done _ => 0
  | .step stage tail => stage.budget.batches + tail.batches

def transfers {s last : Execution n (ZMod n)} : FusionReplayPlan F s last → ℕ
  | .done _ => 0
  | .step stage tail => stage.gap + tail.transfers

variable {s last : Execution n (ZMod n)}

theorem run_eq (plan : FusionReplayPlan F s last) : run F s plan.word = last := by
  induction plan with
  | done s => rfl
  | step stage tail ih => simpa only [word, run_append, FusionStage.next] using ih

theorem trace_eq (plan : FusionReplayPlan F s last) :
    eventTrace F s plan.word = plan.events := by
  induction plan with
  | done s => rfl
  | step stage tail ih =>
      simp only [word, events, eventTrace_append, stage.trace, List.singleton_append]
      exact congrArg (List.cons stage.event) ih

theorem batch_bound (plan : FusionReplayPlan F s last) :
    plan.batches ≤ plan.events.length := by
  induction plan with
  | done s => simp [batches, events]
  | step stage tail ih =>
      have := stage.cost.1
      simp only [batches, events, List.length_cons]
      omega

theorem rank_ledger (plan : FusionReplayPlan F s last) :
    packetRank last.placed + plan.events.length = packetRank s.placed := by
  induction plan with
  | done s => simp [events]
  | step stage tail ih =>
      have := stage.rank_drop
      simp only [events, List.length_cons]
      omega

theorem length_bound (plan : FusionReplayPlan F s last) :
    plan.word.length ≤ 3 * n * plan.events.length + plan.transfers := by
  induction plan with
  | done s => simp [word, events, transfers]
  | step stage tail ih =>
      have cost := stage.cost.2.2
      simp only [word, events, transfers, List.length_append, List.length_cons]
      nlinarith

/-- Hole costs grow with the actual falling rank, not with a fresh worst case. -/
theorem transfer_bound (plan : FusionReplayPlan F s last) :
    plan.transfers ≤ (n - packetRank s.placed) * plan.events.length +
      Nat.choose plan.events.length 2 := by
  induction plan with
  | done s => simp [transfers, events]
  | @step s last stage tail ih =>
      have rank := stage.rank_drop
      have sites := packetRank_le_sites s.placed
        (sourceOrdered_uniquePackets _ stage.ordered)
      have holes : n - packetRank stage.next.placed = n - packetRank s.placed + 1 := by
        omega
      have gap := stage.gap_le_holes
      have choose : Nat.choose (tail.events.length + 1) 2 =
          Nat.choose tail.events.length 2 + tail.events.length := by
        simpa [Nat.add_comm] using Nat.choose_succ_succ tail.events.length 1
      simp only [transfers, events, List.length_cons]
      rw [holes] at ih
      rw [choose]
      nlinarith

theorem sharp_length_bound (plan : FusionReplayPlan F s last) :
    plan.word.length ≤ 3 * n * plan.events.length +
      (n - packetRank s.placed) * plan.events.length + Nat.choose plan.events.length 2 := by
  have := plan.length_bound
  have := plan.transfer_bound
  omega

end FusionReplayPlan
end FusionLogReplay
