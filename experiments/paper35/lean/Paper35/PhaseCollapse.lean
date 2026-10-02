import Mathlib.Data.Set.Card

/-!
# All-hole terminal-phase collapse

This file isolates the logical core of Paper XXXV's phase theorem. A supplied
order-fiber saturation law says that pullback reachability depends only on
cyclic order. Every well-typed terminal hole has the same pullback order, so
either all holes are phase witnesses or none are.
-/

namespace Rime.Paper35

universe u v w x

/-- Abstract data read by the all-hole phase-collapse argument. The concrete
manuscript instantiates `pullback terminal phase` by
`a⁻¹ p⁻ᵘ terminal`. -/
structure PhaseModel
    (Terminal : Type u) (Pullback : Type v) (Phase : Type w) (Order : Type x)
    where
  holes : Terminal → Set Phase
  pullback : Terminal → Phase → Pullback
  pullbackOrder : Pullback → Order
  terminalOrder : Terminal → Order
  reachable : Pullback → Prop
  reachableOrders : Set Order
  order_of_hole :
    ∀ terminal phase, phase ∈ holes terminal →
      pullbackOrder (pullback terminal phase) = terminalOrder terminal
  saturated : ∀ state, reachable state ↔ pullbackOrder state ∈ reachableOrders

namespace PhaseModel

variable {Terminal : Type u} {Pullback : Type v}
variable {Phase : Type w} {Order : Type x}

/-- The same-witness terminal phase fiber. Membership retains both the hole
condition and reachability of that hole's concrete pullback. -/
def phaseFiber
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal) :
    Set Phase :=
  {phase | phase ∈ model.holes terminal ∧
    model.reachable (model.pullback terminal phase)}

theorem mem_phaseFiber_iff
    (model : PhaseModel Terminal Pullback Phase Order)
    (terminal : Terminal) (phase : Phase) :
    phase ∈ model.phaseFiber terminal ↔
      phase ∈ model.holes terminal ∧
        model.terminalOrder terminal ∈ model.reachableOrders := by
  constructor
  · rintro ⟨hhole, hreachable⟩
    refine ⟨hhole, ?_⟩
    have horder :=
      (model.saturated (model.pullback terminal phase)).mp hreachable
    rwa [model.order_of_hole terminal phase hhole] at horder
  · rintro ⟨hhole, horder⟩
    refine ⟨hhole, (model.saturated (model.pullback terminal phase)).mpr ?_⟩
    rwa [model.order_of_hole terminal phase hhole]

/-- If the terminal cyclic order is reachable, every missing coordinate is a
phase witness. -/
theorem phaseFiber_eq_holes_of_reachableOrder
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal)
    (horder : model.terminalOrder terminal ∈ model.reachableOrders) :
    model.phaseFiber terminal = model.holes terminal := by
  ext phase
  rw [model.mem_phaseFiber_iff terminal phase]
  simp [horder]

/-- If the terminal cyclic order is unreachable, no missing coordinate is a
phase witness. -/
theorem phaseFiber_eq_empty_of_unreachableOrder
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal)
    (horder : model.terminalOrder terminal ∉ model.reachableOrders) :
    model.phaseFiber terminal = ∅ := by
  ext phase
  rw [model.mem_phaseFiber_iff terminal phase]
  simp [horder]

theorem phaseFiber_ncard_of_reachableOrder
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal)
    (horder : model.terminalOrder terminal ∈ model.reachableOrders) :
    (model.phaseFiber terminal).ncard = (model.holes terminal).ncard := by
  rw [model.phaseFiber_eq_holes_of_reachableOrder terminal horder]

/-- A terminal placement is attainable when one concrete phase witness
exists. -/
def Attainable
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal) :
    Prop :=
  (model.phaseFiber terminal).Nonempty

/-- Once the terminal placement has at least one hole, attainability is
equivalent to cyclic-order reachability. -/
theorem attainable_iff_of_holes_nonempty
    (model : PhaseModel Terminal Pullback Phase Order) (terminal : Terminal)
    (hholes : (model.holes terminal).Nonempty) :
    model.Attainable terminal ↔
      model.terminalOrder terminal ∈ model.reachableOrders := by
  constructor
  · rintro ⟨phase, hphase⟩
    exact (model.mem_phaseFiber_iff terminal phase).mp hphase |>.2
  · intro horder
    rcases hholes with ⟨phase, hphase⟩
    exact ⟨phase,
      (model.mem_phaseFiber_iff terminal phase).mpr ⟨hphase, horder⟩⟩

end PhaseModel

/-- A globally enabled branch equivalence transports reachability backward as
well as forward. This is the abstract finite-branch step used before the
phase-collapse argument. -/
theorem reachable_symm_iff
    {State : Type u} (reachable : State → Prop) (branch : State ≃ State)
    (invariant : ∀ state, reachable (branch state) ↔ reachable state)
    (state : State) :
    reachable (branch.symm state) ↔ reachable state := by
  simpa using (invariant (branch.symm state)).symm

end Rime.Paper35
