import PaperXL

/-!
# Prefix-observer controls

These finite examples exercise the generic prefix-label transition. They are
kernel-checked controls, not an instantiation of the manuscript's circular
registered-summary model.
-/

namespace PaperXL.PrefixObserverChecks

abbrev Event := PaperXL.PrefixEvent Nat Nat
abbrev Label := PaperXL.PrefixLabel Nat Nat

def registration : Event := PaperXL.PrefixEvent.registration 7
def firstAbsorption : Event := PaperXL.PrefixEvent.absorption 11
def secondAbsorption : Event := PaperXL.PrefixEvent.absorption 13

example :
    PaperXL.PrefixLabel.scan 2 [registration, firstAbsorption] =
      PaperXL.PrefixLabel.registered 7 [11] .short := by
  decide

example :
    PaperXL.PrefixLabel.scan 2 [registration, firstAbsorption, secondAbsorption] =
      PaperXL.PrefixLabel.registered 7 [11, 13] .saturated := by
  decide

example :
    PaperXL.PrefixLabel.scan 2 [registration, firstAbsorption, secondAbsorption,
      PaperXL.PrefixEvent.absorption 17] =
      PaperXL.PrefixLabel.registered 7 [11, 13] .saturated := by
  decide

example :
    PaperXL.PrefixLabel.scan 2 [PaperXL.PrefixEvent.absorption 5, registration,
      firstAbsorption] =
      PaperXL.PrefixLabel.registered 7 [11] .short := by
  decide

example :
    PaperXL.PrefixLabel.scan 2 [registration, PaperXL.PrefixEvent.registration 19,
      firstAbsorption] =
      PaperXL.PrefixLabel.registered 7 [11] .short := by
  decide

example (events : List Event) :
    PaperXL.PrefixLabel.WellFormed 2 (PaperXL.PrefixLabel.scan 2 events) :=
  PaperXL.PrefixLabel.scan_wellFormed 2 events

def eventMachine (depth : Nat) :
    PaperXL.PrefixObserver Label Event Nat Nat := {
  step := fun label event => PaperXL.PrefixLabel.update depth label event
  emit := fun _ event => event
  label := id
  update := PaperXL.PrefixLabel.update depth
  label_step := by
    intro label event
    rfl
}

example :
    PaperXL.LabelledMachine.run (eventMachine 2) PaperXL.PrefixLabel.unregistered
      [registration, firstAbsorption, secondAbsorption] =
      PaperXL.PrefixLabel.registered 7 [11, 13] .saturated := by
  decide

example (label : Label) (events : List Event) :
    PaperXL.LabelledMachine.label (eventMachine 2)
        (PaperXL.LabelledMachine.run (eventMachine 2) label events) =
      List.foldl (PaperXL.PrefixLabel.update 2) label
        (PaperXL.LabelledMachine.trace (eventMachine 2) label events) :=
  PaperXL.LabelledMachine.label_run (eventMachine 2) label events

end PaperXL.PrefixObserverChecks
