import Mathlib.Logic.Equiv.Defs
import Paper31.Reachability

/-!
# Skew quotient transport and theorem firewalls

This file checks the abstract implication pattern beneath the normalizer
epilogue. It does not prove that a concrete branch normalizes the punctured
rotation or that a concrete multiplier preserves lane order.
-/

namespace Rime.Paper31

universe u v w

/-- Existential labelled edge on a projected state space. -/
def LabelledQuotStep {Label : Type u} {State : Type v} {Bucket : Type w}
    (project : State → Bucket) (step : Label → State → State → Prop)
    (label : Label) (left right : Bucket) : Prop :=
  ∃ x y, project x = left ∧ project y = right ∧ step label x y

/-- If a skew step is a base step after one equivariant deterministic twist,
its existential quotient edge is exactly the twisted base quotient edge. -/
theorem skew_quotient_edge
    {Label : Type u} {State : Type v} {Bucket : Type w}
    (project : State → Bucket)
    (twist : State ≃ State) (bucketTwist : Bucket ≃ Bucket)
    (baseStep skewStep : Label → State → State → Prop)
    (equivariant : ∀ x, project (twist x) = bucketTwist (project x))
    (factor : ∀ label x y, skewStep label x y ↔ baseStep label (twist x) y)
    (label : Label) (left right : Bucket) :
    LabelledQuotStep project skewStep label left right ↔
      LabelledQuotStep project baseStep label (bucketTwist left) right := by
  constructor
  · rintro ⟨x, y, hx, hy, hstep⟩
    refine ⟨twist x, y, ?_, hy, (factor label x y).mp hstep⟩
    exact (equivariant x).trans (congrArg bucketTwist hx)
  · rintro ⟨u, y, hu, hy, hstep⟩
    let x := twist.symm u
    have htwist : twist x = u := by simp [x]
    have hproject : project x = left := by
      apply bucketTwist.injective
      calc
        bucketTwist (project x) = project (twist x) := (equivariant x).symm
        _ = project u := congrArg project htwist
        _ = bucketTwist left := hu
    refine ⟨x, y, hproject, hy, (factor label x y).mpr ?_⟩
    simpa [htwist] using hstep

/-- The same deterministic twist transports existential target orbits. -/
theorem skew_quotient_target
    {State : Type v} {Bucket : Type w}
    (project : State → Bucket)
    (twist : State ≃ State) (bucketTwist : Bucket ≃ Bucket)
    (baseTarget skewTarget : State → Prop)
    (equivariant : ∀ x, project (twist x) = bucketTwist (project x))
    (factor : ∀ x, skewTarget x ↔ baseTarget (twist x))
    (bucket : Bucket) :
    QuotTarget project skewTarget bucket ↔
      QuotTarget project baseTarget (bucketTwist bucket) := by
  constructor
  · rintro ⟨x, hx, htarget⟩
    exact ⟨twist x, (equivariant x).trans (congrArg bucketTwist hx),
      (factor x).mp htarget⟩
  · rintro ⟨u, hu, htarget⟩
    let x := twist.symm u
    have htwist : twist x = u := by simp [x]
    have hproject : project x = bucket := by
      apply bucketTwist.injective
      calc
        bucketTwist (project x) = project (twist x) := (equivariant x).symm
        _ = project u := congrArg project htwist
        _ = bucketTwist bucket := hu
    exact ⟨x, hproject, (factor x).mpr (by simpa [htwist] using htarget)⟩

/-- The logical spine of the normalizer Safe-Hit sandwich. -/
theorem safeHit_sandwich {State : Type v}
    (laneAdjacent safeHit sameLane : State → Prop)
    (sufficient : ∀ x, laneAdjacent x → safeHit x)
    (necessary : ∀ x, safeHit x → sameLane x)
    (x : State) :
    laneAdjacent x → safeHit x ∧ sameLane x := by
  intro adjacent
  have hit := sufficient x adjacent
  exact ⟨hit, necessary x hit⟩

/-- Separate legal and target witnesses cannot be silently combined into one
same-witness path. -/
theorem separate_witnesses_do_not_combine :
    ¬ (∀ (Witness : Type), ∀ (legal target : Witness → Prop),
      (∃ witness, legal witness) →
      (∃ witness, target witness) →
      ∃ witness, legal witness ∧ target witness) := by
  intro combine
  rcases combine Bool (fun value => value = false) (fun value => value = true)
      ⟨false, rfl⟩ ⟨true, rfl⟩ with ⟨value, hfalse, htrue⟩
  have impossible : false = true := hfalse.symm.trans htrue
  exact Bool.noConfusion impossible

end Rime.Paper31
