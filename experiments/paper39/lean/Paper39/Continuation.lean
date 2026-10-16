import Std

namespace Paper39

def execute (step : Label → X → Option X) : List Label → X → Option X
  | [], x => some x
  | label :: rest, x => (step label x).bind (execute step rest)

/-- The concrete adequacy proof must supply this hypothesis on its declared domain. -/
def StepCommutes (decode : X → Y) (implementation : Label → X → Option X)
    (consumer : Label → Y → Option Y) : Prop :=
  ∀ label x, (implementation label x).map decode = consumer label (decode x)

theorem step_domain_reflection (decode : X → Y) (implementation : Label → X → Option X)
    (consumer : Label → Y → Option Y) (adequate : StepCommutes decode implementation consumer)
    (label : Label) (x : X) :
    (implementation label x).isSome = (consumer label (decode x)).isSome := by
  rw [← adequate label x]
  simp

theorem execute_commutes (decode : X → Y) (implementation : Label → X → Option X)
    (consumer : Label → Y → Option Y) (adequate : StepCommutes decode implementation consumer)
    (word : List Label) (x : X) :
    (execute implementation word x).map decode = execute consumer word (decode x) := by
  induction word generalizing x with
  | nil => rfl
  | cons label rest ih =>
    have step := adequate label x
    cases hx : implementation label x with
    | none => simp [execute, hx, ← step]
    | some successor => simp [execute, hx, ← step, ih]

theorem execute_domain_reflection (decode : X → Y) (implementation : Label → X → Option X)
    (consumer : Label → Y → Option Y) (adequate : StepCommutes decode implementation consumer)
    (word : List Label) (x : X) :
    (execute implementation word x).isSome = (execute consumer word (decode x)).isSome := by
  rw [← execute_commutes decode implementation consumer adequate]
  simp

/-- The implementation path starts at this x; it cannot select a different decoder representative. -/
theorem same_representative_path_lift (decode : X → Y) (implementation : Label → X → Option X)
    (consumer : Label → Y → Option Y) (adequate : StepCommutes decode implementation consumer)
    (word : List Label) (x : X) (y : Y) :
    execute consumer word (decode x) = some y ↔
      ∃ successor, execute implementation word x = some successor ∧ decode successor = y := by
  have commutes := execute_commutes decode implementation consumer adequate word x
  cases hx : execute implementation word x with
  | none => simp [hx] at commutes; simp [← commutes]
  | some successor => simp [hx] at commutes; simp [← commutes]

end Paper39
