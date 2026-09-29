/-!
# Exact relation-valued orbit reduction

The quotient edge is existential. Exact path lifting is recovered from one
additional hypothesis: every two representatives of one fiber can be joined
inside the original relation. This is the data-independent spine of Theorem
4.1 in Paper XXX.
-/

namespace Rime.Paper30

universe u v

/-- Reflexive-transitive paths, with the concrete intermediate witnesses kept. -/
inductive Reach {α : Type u} (step : α → α → Prop) : α → α → Prop
  | refl (x : α) : Reach step x x
  | head {x y z : α} : step x y → Reach step y z → Reach step x z

namespace Reach

variable {α : Type u} {β : Type v}
variable {step : α → α → Prop} {next : β → β → Prop}

theorem single {x y : α} (h : step x y) : Reach step x y :=
  .head h (.refl y)

theorem trans {x y z : α} (hxy : Reach step x y) (hyz : Reach step y z) :
    Reach step x z := by
  induction hxy with
  | refl => exact hyz
  | head hstep htail ih => exact .head hstep (ih hyz)

theorem map (f : α → β)
    (preserves : ∀ {x y}, step x y → next (f x) (f y))
    {x y : α} (h : Reach step x y) : Reach next (f x) (f y) := by
  induction h with
  | refl => exact .refl _
  | head hstep _ ih => exact .head (preserves hstep) ih

end Reach

/-- Existential edge relation induced on an arbitrary projection. -/
def QuotStep {α : Type u} {β : Type v}
    (q : α → β) (step : α → α → Prop) (left right : β) : Prop :=
  ∃ x y, q x = left ∧ q y = right ∧ step x y

theorem reach_projects {α : Type u} {β : Type v}
    (q : α → β) (step : α → α → Prop)
    {x y : α} (h : Reach step x y) :
    Reach (QuotStep q step) (q x) (q y) := by
  exact Reach.map q (fun hxy => ⟨_, _, rfl, rfl, hxy⟩) h

/-- A quotient path lifts once every fiber is internally directed-connected. -/
theorem quotient_path_lifts {α : Type u} {β : Type v}
    (q : α → β) (step : α → α → Prop)
    (internal : ∀ {x y}, q x = q y → Reach step x y)
    {left right : β} (path : Reach (QuotStep q step) left right)
    {x : α} (hx : q x = left) :
    ∃ y, q y = right ∧ Reach step x y := by
  induction path generalizing x with
  | refl => exact ⟨x, hx, .refl x⟩
  | @head left middle right hedge htail ih =>
      rcases hedge with ⟨u, v, hu, hv, huv⟩
      have hxu : Reach step x u := internal (hx.trans hu.symm)
      have hxv : Reach step x v := hxu.trans (Reach.single huv)
      rcases ih hv with ⟨y, hy, hvy⟩
      exact ⟨y, hy, hxv.trans hvy⟩

/-- Exact reachability reflection for a relation-valued quotient. -/
theorem exact_quotient_reachability {α : Type u} {β : Type v}
    (q : α → β) (step : α → α → Prop)
    (internal : ∀ {x y}, q x = q y → Reach step x y)
    (x y : α) :
    Reach (QuotStep q step) (q x) (q y) ↔ Reach step x y := by
  constructor
  · intro quotientPath
    rcases quotient_path_lifts q step internal quotientPath rfl with
      ⟨z, hz, hxz⟩
    exact hxz.trans (internal hz)
  · exact reach_projects q step

end Rime.Paper30
