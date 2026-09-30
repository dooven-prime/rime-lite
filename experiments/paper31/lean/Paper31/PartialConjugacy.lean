import Mathlib.Logic.Equiv.Defs

/-!
# Labelled paths under a partial-system conjugacy

The concrete branch identity and guard calculation remain manuscript
mathematics. This file checks their data-independent consequence: an exact
one-edge equivalence transports and reflects a whole labelled path with one
common witness list.
-/

namespace Rime.Paper31

universe u v w x

/-- A path indexed by its exact list of labels. -/
inductive LabelledReach {Label : Type u} {State : Type v}
    (step : Label → State → State → Prop) : List Label → State → State → Prop
  | nil (state : State) : LabelledReach step [] state state
  | cons {label labels start middle finish} :
      step label start middle →
      LabelledReach step labels middle finish →
      LabelledReach step (label :: labels) start finish

namespace LabelledReach

variable {Label : Type u} {OtherLabel : Type v}
variable {State : Type w} {OtherState : Type x}
variable {step : Label → State → State → Prop}
variable {otherStep : OtherLabel → OtherState → OtherState → Prop}

theorem transport (stateMap : State → OtherState) (labelMap : Label → OtherLabel)
    (edge : ∀ label start finish,
      step label start finish →
        otherStep (labelMap label) (stateMap start) (stateMap finish))
    {labels : List Label} {start finish : State}
    (path : LabelledReach step labels start finish) :
    LabelledReach otherStep (labels.map labelMap) (stateMap start) (stateMap finish) := by
  induction path with
  | nil => exact .nil _
  | cons hstep _ ih => exact .cons (edge _ _ _ hstep) ih

theorem reflect (stateMap : State ≃ OtherState) (labelMap : Label ≃ OtherLabel)
    (edge : ∀ label start finish,
      step label start finish ↔
        otherStep (labelMap label) (stateMap start) (stateMap finish))
    {labels : List Label} {start finish : State}
    (path : LabelledReach otherStep (labels.map labelMap)
      (stateMap start) (stateMap finish)) :
    LabelledReach step labels start finish := by
  have back : LabelledReach step
      ((labels.map labelMap).map labelMap.symm)
      (stateMap.symm (stateMap start)) (stateMap.symm (stateMap finish)) :=
    transport (step := otherStep) (otherStep := step)
      stateMap.symm labelMap.symm
      (fun label x y h =>
        (edge (labelMap.symm label) (stateMap.symm x) (stateMap.symm y)).mpr
          (by simpa using h))
      path
  simpa using back

/-- Exact one-edge conjugacy gives exact transport of the same labelled path. -/
theorem exact_labelled_path_transport
    (stateMap : State ≃ OtherState) (labelMap : Label ≃ OtherLabel)
    (edge : ∀ label start finish,
      step label start finish ↔
        otherStep (labelMap label) (stateMap start) (stateMap finish))
    (labels : List Label) (start finish : State) :
    LabelledReach step labels start finish ↔
      LabelledReach otherStep (labels.map labelMap)
        (stateMap start) (stateMap finish) := by
  constructor
  · exact transport stateMap labelMap (fun l x y => (edge l x y).mp)
  · exact reflect stateMap labelMap edge

end LabelledReach

end Rime.Paper31
