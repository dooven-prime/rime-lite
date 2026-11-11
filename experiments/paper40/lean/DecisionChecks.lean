import PaperXL.EffectiveCheck

/-!
# Executable controls for the finite R/G/T checker

These tiny computations test the Boolean checker itself. They are not used as
premises in the complete-log theorems.
-/

namespace PaperXL.DecisionChecks

inductive Command
  | inspect
deriving DecidableEq

def flipStep (s : Bool) (_ : Bool) : Bool := !s

def system : RGTBoundedHistory.FiniteSystem Bool Bool where
  step := flipStep
  seed := false
  cover := [false, true]
  complete := by
    intro w
    cases RGTBoundedHistory.run flipStep false w <;> simp

def historyList : List (List Bool) := wordsUpTo [false, true] 1
def commandList : List Command := [.inspect]

def coherentConsumer : RGTBoundedHistory.CheckSpec Bool Bool Command Bool Bool := {
  domain := fun _ => True
  candidate := id
  report := id
  enabled := fun _ _ => true
  letter := fun _ => true
}

def readFailureConsumer : RGTBoundedHistory.CheckSpec Bool Bool Command Bool Bool := {
  domain := fun _ => True
  candidate := fun _ => false
  report := id
  enabled := fun _ _ => true
  letter := fun _ => true
}

def domainCheck (_ : Bool) : Bool := true

theorem domainCheck_correct (s : Bool) :
    domainCheck s = true ↔ coherentConsumer.domain s := by
  simp [domainCheck, coherentConsumer]

theorem coherentConsumer_accepted :
    EffectiveCheck.decision system coherentConsumer domainCheck historyList commandList = true := by
  decide

theorem readFailureConsumer_rejected :
    EffectiveCheck.decision system readFailureConsumer domainCheck historyList commandList = false := by
  decide

end PaperXL.DecisionChecks
