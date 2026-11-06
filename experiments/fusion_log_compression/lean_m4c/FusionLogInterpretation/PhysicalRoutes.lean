import FusionLogInterpretation.PacketInterpretation

namespace FusionLogInterpretation

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay

variable {n : ℕ} [NeZero n]
variable {ι α : Type*} [DecidableEq ι] [DecidableEq α]

/-- The interpreted M3 plan has the same literal word and the same real
batch/transfer counts, but is typed at the actual execution states. -/
theorem batchPlan_interprets (labels : ι → Finset α)
    (G : Finset ι) (F : Finset α)
    (source : Execution n ι) (target : Placement n (Finset ι))
    (plan : BatchPlacementPlan G source target) (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) :
    ∃ actualPlan : BatchPlacementPlan F actual (expandPlacement labels target),
      actualPlan.word = plan.word ∧ actualPlan.batches = plan.batches ∧
      actualPlan.transfers = plan.transfers := by
  induction plan generalizing actual with
  | done source =>
      rw [← same]
      exact ⟨.done actual, rfl, rfl, rfl⟩
  | @step source move target tail ih =>
      let actualMove : LegalPlacementBatch F actual :=
        { q := move.q
          f := move.f
          block := expandBlock labels move.block
          positive := move.positive
          short := move.short
          occupied := by
            rw [same]
            change (source.placed move.q).map (expandBlock labels) = _
            rw [move.occupied]
            rfl
          holes := by
            intro i lo hi
            rw [same]
            change (source.placed _).map (expandBlock labels) = none
            rw [move.holes i lo hi]
            rfl }
      have targetSame : actualMove.target = expandPlacement labels move.target := by
        funext q
        change batchTarget actual.placed move.q move.f q =
          (batchTarget source.placed move.q move.f q).map (expandBlock labels)
        rw [same]
        simp only [batchTarget, expandPlacement]
        split_ifs <;> rfl
      obtain ⟨actualTail, wordEq, batchesEq, transfersEq⟩ :=
        ih (withPlaced actual actualMove.target) targetSame
      refine ⟨.step actual actualMove actualTail, ?_, ?_, ?_⟩
      · simp only [BatchPlacementPlan.word, wordEq]
        rfl
      · simp only [BatchPlacementPlan.batches, batchesEq]
      · simp only [BatchPlacementPlan.transfers, transfersEq]
        rfl

/-- Every canonical M2 stage is enabled at the actual predecessor reached
by its own preceding literal words. No existential representative switch. -/
def FusionAdmission (labels : ZMod n → Finset α) (F : Finset α)
    {G : Finset (ZMod n)} {source last : Execution n (ZMod n)} :
    FusionReplayPlan G source last → Execution n α → Prop
  | .done _, _ => True
  | .step stage tail, actual =>
      actual.placed stage.qLeft = some (expandBlock labels stage.left) ∧
      actual.placed stage.qRight = some (expandBlock labels stage.right) ∧
      (∀ i : ℕ, 1 ≤ i → i ≤ stage.gap →
        actual.placed (stage.qRight - (i : ZMod n)) = none) ∧
      FusionAdmission labels F tail (run F actual stage.word)

theorem admitted_fusion_stage (labels : ZMod n → Finset α) (F : Finset α)
    {G : Finset (ZMod n)} {source : Execution n (ZMod n)}
    (stage : FusionStage G source) (actual : Execution n α)
    (left : actual.placed stage.qLeft = some (expandBlock labels stage.left))
    (right : actual.placed stage.qRight = some (expandBlock labels stage.right))
    (holes : ∀ i : ℕ, 1 ≤ i → i ≤ stage.gap →
      actual.placed (stage.qRight - (i : ZMod n)) = none) :
    eventTrace F actual stage.word = [expandRecord labels stage.event] ∧
      stage.budget.batches ≤ 1 ∧ stage.budget.holeTransfers = stage.gap ∧
      stage.word.length ≤ 3 * n + stage.gap := by
  have event := eventTrace_adjacentFusionWord F actual stage.qLeft stage.qRight
    (expandBlock labels stage.left) (expandBlock labels stage.right) stage.gap
    stage.three_le stage.gap_small stage.sites left right holes
  have budget := adjacentFusionWord_budget F actual stage.qLeft stage.qRight
    (expandBlock labels stage.left) (expandBlock labels stage.right) stage.gap
    stage.three_le stage.gap_small stage.sites left right holes
  refine ⟨?_, budget⟩
  simpa only [FusionStage.word, FusionStage.event, expandRecord, expandBlock_union] using event

theorem fusionPlan_interprets (labels : ZMod n → Finset α)
    (G : Finset (ZMod n)) (F : Finset α)
    (source last : Execution n (ZMod n)) (plan : FusionReplayPlan G source last)
    (actual : Execution n α)
    (same : actual.placed = expandPlacement labels source.placed) :
    FusionAdmission labels F plan actual := by
  induction plan generalizing actual with
  | done source => trivial
  | @step source last stage tail ih =>
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [same]
        change (source.placed stage.qLeft).map (expandBlock labels) = _
        rw [stage.at_left]
        rfl
      · rw [same]
        change (source.placed stage.qRight).map (expandBlock labels) = _
        rw [stage.at_right]
        rfl
      · intro i lo hi
        rw [same]
        change (source.placed _).map (expandBlock labels) = none
        rw [stage.holes i lo hi]
        rfl
      · exact ih (run F actual stage.word)
          (run_placement_interprets labels G F source actual same stage.word)

structure InterpretedJointPlan (labels : ZMod n → Finset α)
    (G : Finset (ZMod n)) (F : Finset α)
    (source : Execution n (ZMod n)) (actual : Execution n α)
    (target : Placement n (Finset (ZMod n))) where
  encoded : JointReplayPlan G source target
  fusion_admission : FusionAdmission labels F encoded.fusion actual
  alignment : BatchPlacementPlan F (run F actual encoded.fusion.word)
    (expandPlacement labels encoded.alignment.mid)
  alignment_word : alignment.word = encoded.alignment.flow.word
  alignment_batches : alignment.batches = encoded.alignment.flow.batches
  alignment_transfers : alignment.transfers = encoded.alignment.flow.transfers

namespace InterpretedJointPlan

variable {labels : ZMod n → Finset α} {G : Finset (ZMod n)} {F : Finset α}
variable {source : Execution n (ZMod n)} {actual : Execution n α}
variable {target : Placement n (Finset (ZMod n))}

def word (plan : InterpretedJointPlan labels G F source actual target) : List Letter :=
  plan.encoded.fusion.word ++ (plan.alignment.word ++ pWord plan.encoded.alignment.phase.val)

def batches (plan : InterpretedJointPlan labels G F source actual target) : ℕ :=
  plan.encoded.fusion.batches + plan.alignment.batches

def transfers (plan : InterpretedJointPlan labels G F source actual target) : ℕ :=
  plan.encoded.fusion.transfers + plan.alignment.transfers

theorem word_eq (plan : InterpretedJointPlan labels G F source actual target) :
    plan.word = plan.encoded.word := by
  rw [word, plan.alignment_word]
  rfl

theorem batches_eq (plan : InterpretedJointPlan labels G F source actual target) :
    plan.batches = plan.encoded.batches := by
  change _ + plan.alignment.batches = _ + plan.encoded.alignment.flow.batches
  rw [plan.alignment_batches]

theorem transfers_eq (plan : InterpretedJointPlan labels G F source actual target) :
    plan.transfers = plan.encoded.transfers := by
  change _ + plan.alignment.transfers = _ + plan.encoded.alignment.flow.transfers
  rw [plan.alignment_transfers]

end InterpretedJointPlan

theorem jointPlan_interprets (labels : ZMod n → Finset α)
    (G : Finset (ZMod n)) (F : Finset α)
    (source : Execution n (ZMod n)) (actual : Execution n α)
    (target : Placement n (Finset (ZMod n))) (plan : JointReplayPlan G source target)
    (same : actual.placed = expandPlacement labels source.placed) :
    ∃ interpreted : InterpretedJointPlan labels G F source actual target,
      interpreted.encoded = plan := by
  have after := run_placement_interprets labels G F source actual same plan.fusion.word
  rw [plan.fusion.run_eq] at after
  obtain ⟨alignment, words, batches, transfers⟩ := batchPlan_interprets labels G F
    plan.last plan.alignment.mid plan.alignment.flow (run F actual plan.fusion.word) after
  exact ⟨⟨plan, fusionPlan_interprets labels G F source plan.last plan.fusion actual same,
    alignment, words, batches, transfers⟩, rfl⟩

end FusionLogInterpretation
