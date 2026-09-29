import Mathlib.Logic.Equiv.Defs
import Paper30.CycleGluing

/-!
# Branch fibers and fixed-arrow constraints

The broad branch-completion theorem is a manuscript construction. This file
freezes its data-independent consequences: an equivalence restricts exactly
to a prescribed fiber, the fixed arrow forces one cycle join, and a fixed
singleton cycle is isolated.
-/

namespace Rime.Paper30

universe u v w

/-- Any equivalence restricts to an equivalence of corresponding fibers. -/
def restrictEquivToFiber {Source : Type u} {Parameter : Type v} {Value : Type w}
    (equiv : Source ≃ Parameter) (read : Parameter → Value) (value : Value) :
    {source : Source // read (equiv source) = value} ≃
      {parameter : Parameter // read parameter = value} where
  toFun source := ⟨equiv source, source.property⟩
  invFun parameter := ⟨equiv.symm parameter, by simpa using parameter.property⟩
  left_inv source := by ext; simp
  right_inv parameter := by ext; simp

theorem fixed_arrow_forces_gluing
    {Point : Type u} {Cycle : Type v}
    (cycleOf : Point → Cycle) (a : Equiv.Perm Point)
    {source target : Point} (fixed : a source = target) :
    GluingEdge cycleOf a (cycleOf source) (cycleOf target) :=
  ⟨source, target, rfl, rfl, Or.inl fixed⟩

/-- If a fixed point is the sole point of its cycle, that cycle cannot glue. -/
theorem fixed_singleton_cycle_isolated
    {Point : Type u} {Cycle : Type v}
    (cycleOf : Point → Cycle) (a : Equiv.Perm Point) (source : Point)
    (fixed : a source = source)
    (singleton : ∀ point, cycleOf point = cycleOf source → point = source)
    {other : Cycle} (different : other ≠ cycleOf source) :
    ¬ GluingEdge cycleOf a (cycleOf source) other := by
  rintro ⟨x, y, hx, hy, hedge⟩
  have hxs : x = source := singleton x hx
  rcases hedge with hforward | hreverse
  · have hys : y = source := by
      calc
        y = a x := hforward.symm
        _ = a source := congrArg a hxs
        _ = source := fixed
    exact different (hy.symm.trans (congrArg cycleOf hys))
  · have hys : y = source := by
      apply a.injective
      calc
        a y = x := hreverse
        _ = source := hxs
        _ = a source := fixed.symm
    exact different (hy.symm.trans (congrArg cycleOf hys))

/-- Point-orbit data alone cannot supply arbitrary coloring-orbit data. -/
theorem no_unconditional_point_to_coloring_promotion :
    ¬ (∀ (PointOrbit ColoringOrbit : Type),
      Nonempty PointOrbit → Nonempty ColoringOrbit) := by
  intro promote
  obtain ⟨coloring⟩ := promote Unit Empty ⟨()⟩
  exact nomatch coloring

end Rime.Paper30
