import RGTBoundedHistory

/-! A concrete one-state-space check of the observation transport interface. -/

namespace RGTBoundedHistory.ObservationCompressionChecks

inductive Command
  | tick
deriving DecidableEq

def toggle : Bool → Unit → Bool := fun b _ => !b

def system : FiniteSystem Bool Unit where
  step := toggle
  seed := false
  cover := [false, true]
  complete w := by
    cases run toggle false w <;> simp

def consumer : CheckSpec Bool Unit Command Unit Bool where
  domain := fun _ => True
  candidate := fun _ => ()
  report := id
  enabled := fun _ _ => true
  letter := fun _ => ()

theorem boundedReplacement : BoundedObservationReplacement system id 1 where
  replace h := by
    cases hend : system.eval h with
    | false =>
        refine ⟨[], by decide, ?_⟩
        simp [FiniteSystem.eval, run, system]
    | true =>
        refine ⟨[()], by decide, ?_⟩
        simp [FiniteSystem.eval, run, system, toggle]

theorem factorization : CheckSpecObservationFactorization consumer system id where
  domain _ _ _ := Iff.rfl
  candidate _ _ _ := rfl
  report _ _ h := h
  enabled _ _ _ _ := rfl
  step s t h a := by
    simpa using congrArg (fun x => system.step x a) h

theorem read_fails : ¬ consumer.readCondition system := by
  intro h
  have hf : consumer.sameFiber (system.eval []) (system.eval [()]) := by
    simp [CheckSpec.sameFiber, system, consumer, toggle, FiniteSystem.eval,
      run, CheckSpec.sameFiber]
  have reports := h [] [()] hf
  change false = true at reports
  cases reports

example :
    ∃ h k, h.length ≤ 1 ∧ k.length ≤ 1 ∧
      consumer.readCollision (system.eval h) (system.eval k) :=
  (CheckSpec.compressed_read_failure_iff consumer system id 1
    boundedReplacement factorization).mp read_fails

end RGTBoundedHistory.ObservationCompressionChecks
