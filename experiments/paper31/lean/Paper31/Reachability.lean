/-!
# Reachability through an existential quotient

This file keeps concrete path witnesses while proving exact Safe-Hit
reduction under one explicit hypothesis: every quotient fiber is internally
directed-connected by the original step relation.
-/

namespace Rime.Paper31

universe u v

/-- Reflexive-transitive reachability with concrete intermediate witnesses. -/
inductive Reach {State : Type u} (step : State → State → Prop) : State → State → Prop
  | refl (x : State) : Reach step x x
  | head {x y z : State} : step x y → Reach step y z → Reach step x z

namespace Reach

variable {State : Type u} {Other : Type v}
variable {step next : State → State → Prop}

theorem single {x y : State} (h : step x y) : Reach step x y :=
  .head h (.refl y)

theorem trans {x y z : State} (hxy : Reach step x y) (hyz : Reach step y z) :
    Reach step x z := by
  induction hxy with
  | refl => exact hyz
  | head hstep _ ih => exact .head hstep (ih hyz)

theorem map (f : State → Other) {otherStep : Other → Other → Prop}
    (preserves : ∀ {x y}, step x y → otherStep (f x) (f y))
    {x y : State} (path : Reach step x y) : Reach otherStep (f x) (f y) := by
  induction path with
  | refl => exact .refl _
  | head hstep _ ih => exact .head (preserves hstep) ih

theorem congr (edge : ∀ x y, step x y ↔ next x y) {x y : State} :
    Reach step x y ↔ Reach next x y := by
  constructor
  · intro path
    exact path.map id (fun h => (edge _ _).mp h)
  · intro path
    exact path.map id (fun h => (edge _ _).mpr h)

end Reach

/-- A target can be reached by one concrete path. -/
def SafeHit {State : Type u} (step : State → State → Prop)
    (target : State → Prop) (start : State) : Prop :=
  ∃ finish, Reach step start finish ∧ target finish

/-- Existential edge relation induced by an arbitrary projection. -/
def QuotStep {State : Type u} {Bucket : Type v}
    (project : State → Bucket) (step : State → State → Prop)
    (left right : Bucket) : Prop :=
  ∃ x y, project x = left ∧ project y = right ∧ step x y

/-- Existential target predicate induced by a projection. -/
def QuotTarget {State : Type u} {Bucket : Type v}
    (project : State → Bucket) (target : State → Prop) (bucket : Bucket) : Prop :=
  ∃ x, project x = bucket ∧ target x

theorem reach_projects {State : Type u} {Bucket : Type v}
    (project : State → Bucket) (step : State → State → Prop)
    {x y : State} (path : Reach step x y) :
    Reach (QuotStep project step) (project x) (project y) := by
  exact path.map project (fun h => ⟨_, _, rfl, rfl, h⟩)

theorem quotient_path_lifts {State : Type u} {Bucket : Type v}
    (project : State → Bucket) (step : State → State → Prop)
    (internal : ∀ {x y}, project x = project y → Reach step x y)
    {left right : Bucket}
    (path : Reach (QuotStep project step) left right)
    {x : State} (hx : project x = left) :
    ∃ y, project y = right ∧ Reach step x y := by
  induction path generalizing x with
  | refl => exact ⟨x, hx, .refl x⟩
  | @head left middle right hedge htail ih =>
      rcases hedge with ⟨u, v, hu, hv, huv⟩
      have hxu : Reach step x u := internal (hx.trans hu.symm)
      have hxv : Reach step x v := hxu.trans (Reach.single huv)
      rcases ih hv with ⟨y, hy, hvy⟩
      exact ⟨y, hy, hxv.trans hvy⟩

/-- Exact Safe-Hit reduction through an internally controllable quotient. -/
theorem safeHit_iff_quotient {State : Type u} {Bucket : Type v}
    (project : State → Bucket) (step : State → State → Prop)
    (target : State → Prop)
    (internal : ∀ {x y}, project x = project y → Reach step x y)
    (start : State) :
    SafeHit step target start ↔
      SafeHit (QuotStep project step) (QuotTarget project target) (project start) := by
  constructor
  · rintro ⟨finish, path, htarget⟩
    exact ⟨project finish, reach_projects project step path, finish, rfl, htarget⟩
  · rintro ⟨bucket, quotientPath, finish, hfinish, htarget⟩
    rcases quotient_path_lifts project step internal quotientPath rfl with
      ⟨lifted, hlifted, path⟩
    have tail : Reach step lifted finish := internal (hlifted.trans hfinish.symm)
    exact ⟨finish, path.trans tail, htarget⟩

theorem safeHit_congr {State : Type u}
    {step next : State → State → Prop} {target nextTarget : State → Prop}
    (edge : ∀ x y, step x y ↔ next x y)
    (targetEq : ∀ x, target x ↔ nextTarget x)
    (start : State) :
    SafeHit step target start ↔ SafeHit next nextTarget start := by
  constructor
  · rintro ⟨finish, path, htarget⟩
    exact ⟨finish, (Reach.congr edge).mp path, (targetEq finish).mp htarget⟩
  · rintro ⟨finish, path, htarget⟩
    exact ⟨finish, (Reach.congr edge).mpr path, (targetEq finish).mpr htarget⟩

/-- Two concrete systems have the same Safe-Hit truth once their exact
quotient edge and target relations agree. -/
theorem safeHit_of_same_exact_quotient {State : Type u} {Bucket : Type v}
    (project : State → Bucket)
    (step₁ step₂ : State → State → Prop)
    (target₁ target₂ : State → Prop)
    (internal₁ : ∀ {x y}, project x = project y → Reach step₁ x y)
    (internal₂ : ∀ {x y}, project x = project y → Reach step₂ x y)
    (edgeEq : ∀ left right,
      QuotStep project step₁ left right ↔ QuotStep project step₂ left right)
    (targetEq : ∀ bucket,
      QuotTarget project target₁ bucket ↔ QuotTarget project target₂ bucket)
    (start : State) :
    SafeHit step₁ target₁ start ↔ SafeHit step₂ target₂ start := by
  calc
    SafeHit step₁ target₁ start ↔
        SafeHit (QuotStep project step₁) (QuotTarget project target₁)
          (project start) := safeHit_iff_quotient project step₁ target₁ internal₁ start
    _ ↔ SafeHit (QuotStep project step₂) (QuotTarget project target₂)
          (project start) := safeHit_congr edgeEq targetEq (project start)
    _ ↔ SafeHit step₂ target₂ start :=
      (safeHit_iff_quotient project step₂ target₂ internal₂ start).symm

end Rime.Paper31
