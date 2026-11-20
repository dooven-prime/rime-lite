import FusionLogCompression.M1Batch
import RegisteredAbsorptionChains.CyclicOrderAdmission
import RegisteredAbsorptionChains.PhaseAlignment

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- A placement-only batch step: the named packet at `q` crosses a positive
run of holes immediately before it. -/
structure LegalPlacementBatch (F : Finset α) (s : Execution n α) where
  q : ZMod n
  f : ℕ
  block : Finset α
  positive : 1 ≤ f
  short : f ≤ n - 2
  occupied : s.placed q = some block
  holes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
    s.placed (q - (i : ZMod n)) = none

namespace LegalPlacementBatch

variable {F : Finset α} {s : Execution n α}

def target (move : LegalPlacementBatch F s) : Placement n (Finset α) :=
  batchTarget s.placed move.q move.f

def word (move : LegalPlacementBatch F s) : List Letter :=
  batchWord move.q move.f

theorem execute (move : LegalPlacementBatch F s) :
    FusionFree F s move.word ∧
      run F s move.word = withPlaced s move.target ∧
      move.word.length ≤ 2 * n + move.f := by
  exact batchWord_spec F s move.q move.block move.f
    (by have := move.positive; have := move.short; omega)
    move.positive move.short move.occupied move.holes

end LegalPlacementBatch

/-- A finite placement plan stores each actual M1 batch together with the
execution reached by that literal word. No placement change is free. -/
inductive BatchPlacementPlan (F : Finset α) :
    Execution n α → Placement n (Finset α) → Type _
  | done (s : Execution n α) : BatchPlacementPlan F s s.placed
  | step (s : Execution n α) (move : LegalPlacementBatch F s)
      {target : Placement n (Finset α)}
      (tail : BatchPlacementPlan F (withPlaced s move.target) target) :
      BatchPlacementPlan F s target

namespace BatchPlacementPlan

def batches {F : Finset α} {s : Execution n α} {target : Placement n (Finset α)} :
    BatchPlacementPlan F s target → ℕ
  | .done _ => 0
  | .step _ _ tail => batches tail + 1

def transfers {F : Finset α} {s : Execution n α} {target : Placement n (Finset α)} :
    BatchPlacementPlan F s target → ℕ
  | .done _ => 0
  | .step _ move tail => transfers tail + move.f

def word {F : Finset α} {s : Execution n α} {target : Placement n (Finset α)} :
    BatchPlacementPlan F s target → List Letter
  | .done _ => []
  | .step _ move tail => move.word ++ word tail

theorem word_length_le {F : Finset α} {s : Execution n α}
    {target : Placement n (Finset α)} (plan : BatchPlacementPlan F s target) :
    plan.word.length ≤ 2 * n * plan.batches + plan.transfers := by
  induction plan with
  | done _ => simp [word, batches, transfers]
  | @step s move target tail ih =>
      obtain ⟨hfree, hrun, hlen⟩ := move.execute
      simp only [word, batches, transfers, List.length_append]
      rw [Nat.mul_add, Nat.mul_one]
      omega

theorem fusionFree {F : Finset α} {s : Execution n α}
    {target : Placement n (Finset α)} (plan : BatchPlacementPlan F s target) :
    FusionFree F s plan.word := by
  induction plan with
  | done s => simp [word, FusionFree]
  | @step s move target tail ih =>
      obtain ⟨hfree, hrun, hlen⟩ := move.execute
      change FusionFree F s (move.word ++ tail.word)
      rw [fusionFree_append]
      rw [hrun]
      exact ⟨hfree, ih⟩

theorem run_eq_target {F : Finset α} {s : Execution n α}
    {target : Placement n (Finset α)} (plan : BatchPlacementPlan F s target) :
    run F s plan.word = { s with placed := target } := by
  induction plan with
  | done s => simp [word, run]
  | @step s move target tail ih =>
      obtain ⟨hfree, hrun, hlen⟩ := move.execute
      change run F s (move.word ++ tail.word) = { s with placed := target }
      rw [run_append, hrun, ih]
      rfl

end BatchPlacementPlan

/-- Cost interface for a concrete gap-flow schedule. Once a schedule has
`K` nonempty batches and total flow `M`, its raw routing word costs at most
`2*n*K + M`; the schedule itself is responsible for exact placement. -/
theorem batchPlan_budget (F : Finset α) (s : Execution n α)
    (target : Placement n (Finset α))
    (plan : BatchPlacementPlan F s target) :
    FusionFree F s plan.word ∧
      run F s plan.word = { s with placed := target } ∧
      plan.word.length ≤ 2 * n * plan.batches + plan.transfers := by
  exact ⟨plan.fusionFree, plan.run_eq_target, plan.word_length_le⟩

/-- If a schedule uses at most `r - 1` batches and at most
`(n-r)(r-1)` hole transfers, its routing part meets the M3 raw-letter budget. -/
theorem batchPlan_gap_budget (F : Finset α) (s : Execution n α)
    (target : Placement n (Finset α)) (r : ℕ) (plan : BatchPlacementPlan F s target)
    (hr : r ≤ n) (hK : plan.batches ≤ r - 1)
    (hM : plan.transfers ≤ (n - r) * (r - 1)) :
    plan.word.length ≤ (3 * n - r) * (r - 1) := by
  have hK' := Nat.mul_le_mul_left (2 * n) hK
  calc
    plan.word.length ≤ 2 * n * plan.batches + plan.transfers := plan.word_length_le
    _ ≤ 2 * n * (r - 1) + (n - r) * (r - 1) := Nat.add_le_add hK' hM
    _ = (3 * n - r) * (r - 1) := by
      have hdecomp : 3 * n - r = 2 * n + (n - r) := by omega
      rw [hdecomp]
      ring

/-- Append the final phase rotation. This is the exact M3 placement budget
once the gap-flow schedule has supplied its batch and transfer bounds. -/
theorem batchPlan_gap_budget_with_phase (F : Finset α) (s : Execution n α)
    (target : Placement n (Finset α)) (r : ℕ) (plan : BatchPlacementPlan F s target)
    (phase : ZMod n) (hr : r ≤ n) (hK : plan.batches ≤ r - 1)
    (hM : plan.transfers ≤ (n - r) * (r - 1)) :
    FusionFree F s (plan.word ++ pWord phase.val) ∧
      run F s (plan.word ++ pWord phase.val) =
        { s with placed := rotate phase target } ∧
      (plan.word ++ pWord phase.val).length ≤
        (3 * n - r) * (r - 1) + (n - 1) := by
  have hbudget := batchPlan_gap_budget F s target r plan hr hK hM
  have hphase : phase.val ≤ n - 1 := by
    have := ZMod.val_lt phase
    omega
  refine ⟨?_, ?_, ?_⟩
  · rw [fusionFree_append]
    exact ⟨plan.fusionFree, fusionFree_pWord F (run F s plan.word) phase.val⟩
  · rw [run_append, plan.run_eq_target, run_rotation]
  · simp only [List.length_append, pWord_length]
    exact Nat.add_le_add hbudget hphase

/-- Rank one has no gap-flow: two placements of the same single named block
differ only by phase, so at most `n-1` raw rotations suffice. -/
theorem oneBlock_phase_only (F : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n 1 α)
    (source : s.placed = first.placed) (blocks : first.block = second.block) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = { s with placed := second.placed } ∧
      word.length ≤ n - 1 := by
  let phase := second.position 0 - first.position 0
  refine ⟨pWord phase.val, fusionFree_pWord F s _, ?_, ?_⟩
  · rw [run_rotation, source]
    rw [single_block_rotate first second blocks]
  · rw [pWord_length]
    have hphase := ZMod.val_lt phase
    omega

/-- A full-rank same-order placement has no holes to route: every gap is
zero, and only the common physical phase can differ. -/
theorem fullRank_phase_only (F : Finset α) (s : Execution n α)
    (first second : NamedCyclicPlacement n n α)
    (source : s.placed = first.placed) (blocks : first.block = second.block) :
    ∃ word : List Letter,
      FusionFree F s word ∧
      run F s word = { s with placed := second.placed } ∧
      word.length ≤ n - 1 := by
  let start := first.toGapFrame
  let finish := second.toGapFrame
  have startGap (i : ZMod n) : start.gap i = 0 := by
    have hsum : (∑ j : ZMod n, start.gap j) = 0 := by
      rw [start.gap_total]
      omega
    have hle := Finset.single_le_sum (fun j _ => Nat.zero_le (start.gap j))
      (Finset.mem_univ i)
    omega
  have finishGap (i : ZMod n) : finish.gap i = 0 := by
    have hsum : (∑ j : ZMod n, finish.gap j) = 0 := by
      rw [finish.gap_total]
      omega
    have hle := Finset.single_le_sum (fun j _ => Nat.zero_le (finish.gap j))
      (Finset.mem_univ i)
    omega
  have hgap : start.gap = finish.gap := by
    funext i
    rw [startGap, finishGap]
  have hblock : start.block = finish.block := blocks
  have hphase := start.decode_phase finish hgap hblock
  have htarget :
      rotate (finish.anchor - start.anchor) first.placed = second.placed := by
    rw [← first.toGapFrame_decode, ← second.toGapFrame_decode]
    exact hphase
  let phase := finish.anchor - start.anchor
  refine ⟨pWord phase.val, fusionFree_pWord F s _, ?_, ?_⟩
  · rw [run_rotation, source, htarget]
  · rw [pWord_length]
    have hphase' := ZMod.val_lt phase
    omega

end FusionLogCompression
