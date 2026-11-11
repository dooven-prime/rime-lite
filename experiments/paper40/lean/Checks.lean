import PaperXL

namespace PaperXL

inductive Letter | stay | flip
deriving DecidableEq

inductive Command | observe
deriving DecidableEq

abbrev State := Bool × Bool

def step (s : State) : Letter → State
  | .stay => s
  | .flip => (s.2, s.1)

def M : RawSystem State Letter := { step := step, seed := (false, false) }

def readConsumer : Consumer State Letter Command Bool Bool := {
  domain := fun _ => True
  candidate := Prod.fst
  report := Prod.fst
  enabled := fun _ _ => true
  letter := fun _ => .flip
}

def guardConsumer : Consumer State Letter Command Bool Bool := {
  domain := fun _ => True
  candidate := Prod.fst
  report := fun _ => true
  enabled := fun s _ => s.2
  letter := fun _ => .flip
}

def successorConsumer : Consumer State Letter Command Bool Bool := {
  domain := fun _ => True
  candidate := Prod.fst
  report := fun _ => true
  enabled := fun _ _ => true
  letter := fun _ => .flip
}

example : RawSystem.run M [.flip] = (false, false) := by decide

example : Consumer.R readConsumer := by
  intro x y hxy
  exact hxy.2.2

example : ¬ Consumer.G guardConsumer := by
  intro h
  have hg := h (false, false) (false, true)
    ⟨trivial, trivial, rfl⟩ Command.observe
  change false = true at hg
  contradiction

example : ¬ Consumer.T M successorConsumer := by
  intro h
  have hf : Consumer.sameFiber successorConsumer (false, false) (false, true) :=
    ⟨trivial, trivial, rfl⟩
  have ht := h (false, false) (false, true) hf Command.observe (by decide) (by decide)
  change false = true at ht
  contradiction

def Cover : GeneratedCover State Letter := {
  toRawSystem := M
  cover := [(false, false), (false, true), (true, false), (true, true)]
  complete := by
    intro h
    cases RawSystem.run M h with
    | mk a b => cases a <;> cases b <;> simp
}

example (h : List Letter) : GeneratedCover.contains Cover (Cover.run h) :=
  GeneratedCover.endpoint_mem Cover h

end PaperXL
