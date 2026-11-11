import PaperXL.ConsumerBridge

/-! Kernel-checked control for the consumer-to-CheckSpec adapter. -/

namespace PaperXL.ConsumerBridgeChecks

inductive Command
  | tick
deriving DecidableEq

def flipStep (s : Bool) (_ : Unit) : Bool := !s

def system : RGTBoundedHistory.FiniteSystem Bool Unit where
  step := flipStep
  seed := false
  cover := [false, true]
  complete w := by
    cases RGTBoundedHistory.run flipStep false w <;> simp

def consumer : Consumer Bool Unit Command Bool Bool where
  domain := fun _ => True
  candidate := id
  report := id
  enabled := fun _ _ => true
  letter := fun _ => ()

theorem registeredDomain_reachable : consumer.DomainReachable system := by
  intro s _
  cases s with
  | false => exact ⟨[], rfl⟩
  | true => exact ⟨[()], rfl⟩

example : consumer.R ∧ consumer.G ∧
    consumer.T ⟨system.step, system.seed⟩ ↔
      consumer.toCheckSpec.readCondition system ∧
        consumer.toCheckSpec.guardCondition system ∧
        consumer.toCheckSpec.successorCondition system :=
  consumer.RGT_toCheckSpec_iff system registeredDomain_reachable

example (s t : Bool) :
    consumer.toCheckSpec.sameFiber s t = consumer.sameFiber s t := rfl

def causalSystem : RawSystem Bool Unit where
  step := flipStep
  seed := false

def fullLogSystem : RGTBoundedHistory.FiniteSystem (Bool × Unit) Unit where
  step := fun s _ => (!s.1, ())
  seed := (false, ())
  cover := [(false, ()), (true, ())]
  complete w := by
    cases RGTBoundedHistory.run (fun s _ => (!s.1, ())) (false, ()) w with
    | mk b u => cases b <;> cases u <;> simp

def projectedBridge : ConsumerLogBridge fullLogSystem causalSystem consumer where
  project := Prod.fst
  registered _ := True
  registered_iff_domain _ := Iff.rfl
  step_commutes _ _ := rfl
  realizes_domain t _ := by
    cases t with
    | false => exact ⟨[], trivial, rfl⟩
    | true => exact ⟨[()], trivial, rfl⟩

example : consumer.R ∧ consumer.G ∧ consumer.T causalSystem ↔
    projectedBridge.toCheckSpec.readCondition fullLogSystem ∧
      projectedBridge.toCheckSpec.guardCondition fullLogSystem ∧
      projectedBridge.toCheckSpec.successorCondition fullLogSystem :=
  projectedBridge.RGT_iff

end PaperXL.ConsumerBridgeChecks
