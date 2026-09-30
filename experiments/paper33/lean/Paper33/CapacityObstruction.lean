import Mathlib.Data.Finset.Card

/-!
# Forward-invariant capacity obstruction

The punctured lane has capacity four while every enabled rank-five output has
support cardinality five. If an output is lane-shaped, it therefore lies on an
ordinary lane. Ordinary transport preserves marked nonedges, so the complete
ordinary-lane nonedge family is forward invariant and disjoint from the edge
target.
-/

namespace Rime.Paper33

universe u v w

/-- Reflexive-transitive reachability with all intermediate states retained. -/
inductive Reach {State : Type u} (step : State → State → Prop) :
    State → State → Prop
  | refl (x : State) : Reach step x x
  | head {x y z : State} : step x y → Reach step y z → Reach step x z

namespace Reach

variable {State : Type u} {step : State → State → Prop}

/-- A one-step forward invariant is preserved along every finite path. -/
theorem preserve {P : State → Prop}
    (closed : ∀ {x y}, P x → step x y → P y)
    {x y : State} (path : Reach step x y) (hx : P x) : P y := by
  induction path with
  | refl => exact hx
  | head hstep _ ih =>
      exact ih (closed hx hstep)

end Reach

/-- Abstract data used by the capacity part of Paper XXXIII, Theorem 5.1. -/
structure CapacitySystem
    (State : Type u) (Point : Type v) (Lane : Type w)
    [DecidableEq Point] where
  support : State → Finset Point
  punctured : Finset Point
  ordinary : Lane → Finset Point
  step : State → State → Prop
  edge : State → Prop
  target : State → Prop
  punctured_card : punctured.card = 4
  output_card : ∀ {x y}, step x y → (support y).card = 5
  output_lane :
    ∀ {x y i}, support x = ordinary i → step x y →
      support y = punctured ∨ ∃ j, support y = ordinary j
  ordinary_nonedge_preserved :
    ∀ {x y i j}, support x = ordinary i → support y = ordinary j →
      step x y → ¬ edge x → ¬ edge y
  target_edge : ∀ {x}, target x → edge x

namespace CapacitySystem

variable {State : Type u} {Point : Type v} {Lane : Type w}
variable [DecidableEq Point]

/-- The state is supported on one complete ordinary lane. -/
def SameLane (system : CapacitySystem State Point Lane) (x : State) : Prop :=
  ∃ i, system.support x = system.ordinary i

/-- The forward-invariant hostile family: ordinary support and a marked nonedge. -/
def OrdinaryNonedge
    (system : CapacitySystem State Point Lane) (x : State) : Prop :=
  system.SameLane x ∧ ¬ system.edge x

/-- Reachability of the declared edge target. -/
def SafeHit (system : CapacitySystem State Point Lane) (x : State) : Prop :=
  ∃ y, Reach system.step x y ∧ system.target y

/-- Capacity four excludes a rank-five output from the punctured lane. -/
theorem output_ne_punctured
    (system : CapacitySystem State Point Lane)
    {x y : State} (hstep : system.step x y) :
    system.support y ≠ system.punctured := by
  intro heq
  have hfive : (system.support y).card = 5 := system.output_card hstep
  have hfour : (system.support y).card = 4 := by
    rw [heq, system.punctured_card]
  have : (5 : Nat) = 4 := hfive.symm.trans hfour
  exact (by decide : (5 : Nat) ≠ 4) this

/-- One enabled return preserves the complete ordinary-lane nonedge family. -/
theorem ordinaryNonedge_step
    (system : CapacitySystem State Point Lane)
    {x y : State} (hx : system.OrdinaryNonedge x)
    (hstep : system.step x y) :
    system.OrdinaryNonedge y := by
  rcases hx with ⟨⟨i, hi⟩, hnonedge⟩
  rcases system.output_lane hi hstep with hpunctured | ⟨j, hj⟩
  · exact False.elim ((system.output_ne_punctured hstep) hpunctured)
  · exact ⟨⟨j, hj⟩,
      system.ordinary_nonedge_preserved hi hj hstep hnonedge⟩

/-- The hostile family is forward invariant along every finite return path. -/
theorem ordinaryNonedge_reach
    (system : CapacitySystem State Point Lane)
    {x y : State} (hx : system.OrdinaryNonedge x)
    (path : Reach system.step x y) :
    system.OrdinaryNonedge y := by
  exact Reach.preserve
    (step := system.step)
    (P := system.OrdinaryNonedge)
    (fun hstate hstep => system.ordinaryNonedge_step hstate hstep)
    path hx

/-- An ordinary-lane nonedge state is disjoint from the edge target. -/
theorem ordinaryNonedge_not_target
    (system : CapacitySystem State Point Lane)
    {x : State} (hx : system.OrdinaryNonedge x) :
    ¬ system.target x := by
  intro htarget
  exact hx.2 (system.target_edge htarget)

/-- No state in the forward-invariant hostile family can Safe-Hit. -/
theorem ordinaryNonedge_not_safeHit
    (system : CapacitySystem State Point Lane)
    {x : State} (hx : system.OrdinaryNonedge x) :
    ¬ system.SafeHit x := by
  rintro ⟨y, path, htarget⟩
  have hy : system.OrdinaryNonedge y :=
    system.ordinaryNonedge_reach hx path
  exact system.ordinaryNonedge_not_target hy htarget

/-- The capacity obstruction supplies a strict witness below the inherited
Safe-Hit-to-SameLane implication. -/
theorem strict_safeHit_gap
    (system : CapacitySystem State Point Lane)
    (safe_same : ∀ z, system.SafeHit z → system.SameLane z)
    {x : State} (hx : system.OrdinaryNonedge x) :
    (∀ z, system.SafeHit z → system.SameLane z) ∧
      ∃ z, system.SameLane z ∧ ¬ system.SafeHit z := by
  exact ⟨safe_same, ⟨x, hx.1, system.ordinaryNonedge_not_safeHit hx⟩⟩

end CapacitySystem

end Rime.Paper33
