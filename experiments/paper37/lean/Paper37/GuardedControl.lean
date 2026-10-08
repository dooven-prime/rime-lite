import Mathlib.GroupTheory.OrderOfElement

/-!
# Actual-word control and generated reachability

The concrete normalized guard and the geometric relocation/generator loops
are supplied by the manuscript. This module checks their logical use:
concatenated words run on the successor actually produced, finite-order
positive loops realize inverses, and supplied generator control realizes
the generated subgroup.
-/

namespace Rime.Paper37

universe u v w

def runWord {Label : Type u} {State : Type v}
    (step : Label → State → Option State) : List Label → State → Option State
  | [], state => some state
  | label :: rest, state => (step label state).bind (runWord step rest)

theorem runWord_append {Label : Type u} {State : Type v}
    (step : Label → State → Option State) (left right : List Label) (state : State) :
    runWord step (left ++ right) state =
      (runWord step left state).bind (runWord step right) := by
  induction left generalizing state with
  | nil => simp [runWord]
  | cons label rest ih =>
      cases hstep : step label state <;> simp [runWord, hstep, ih]

def GuardedReach {Label : Type u} {State : Type v}
    (step : Label → State → Option State) (start finish : State) : Prop :=
  ∃ word, runWord step word start = some finish

theorem guardedReach_refl {Label : Type u} {State : Type v}
    (step : Label → State → Option State) (state : State) :
    GuardedReach step state state :=
  ⟨[], rfl⟩

theorem guardedReach_trans {Label : Type u} {State : Type v}
    {step : Label → State → Option State} {x y z : State}
    (hxy : GuardedReach step x y) (hyz : GuardedReach step y z) :
    GuardedReach step x z := by
  rcases hxy with ⟨left, hleft⟩
  rcases hyz with ⟨right, hright⟩
  refine ⟨left ++ right, ?_⟩
  rw [runWord_append, hleft]
  simpa using hright

theorem runWord_preserves {Label : Type u} {State : Type v}
    (step : Label → State → Option State) (invariant : State → Prop)
    (hstep : ∀ label x y, invariant x → step label x = some y → invariant y)
    {word : List Label} {x y : State}
    (hx : invariant x) (hword : runWord step word x = some y) : invariant y := by
  induction word generalizing x with
  | nil =>
      have hxy : x = y := by simpa [runWord] using hword
      simpa [← hxy] using hx
  | cons label rest ih =>
      cases heq : step label x with
      | none => simp [runWord, heq] at hword
      | some successor =>
          apply ih (hstep label x successor hx heq)
          simpa [runWord, heq] using hword

section GroupControl

variable {Label : Type u} {Lane : Type v} {G : Type w} [Group G]

def LoopControl (step : Label → Lane × G → Option (Lane × G)) (g : G) : Prop :=
  ∀ lane current, GuardedReach step (lane, current) (lane, g * current)

theorem loopControl_one (step : Label → Lane × G → Option (Lane × G)) :
    LoopControl step 1 := by
  intro lane current
  simpa using guardedReach_refl step (lane, current)

theorem loopControl_mul {step : Label → Lane × G → Option (Lane × G)}
    {left right : G} (hl : LoopControl step left) (hr : LoopControl step right) :
    LoopControl step (left * right) := by
  intro lane current
  simpa [mul_assoc] using guardedReach_trans
    (hr lane current) (hl lane (right * current))

theorem loopControl_pow {step : Label → Lane × G → Option (Lane × G)}
    {g : G} (hg : LoopControl step g) (n : Nat) :
    LoopControl step (g ^ n) := by
  induction n with
  | zero => simpa using loopControl_one step
  | succ n ih => simpa [pow_succ] using loopControl_mul ih hg

theorem loopControl_inv [Finite G]
    {step : Label → Lane × G → Option (Lane × G)} {g : G}
    (hg : LoopControl step g) : LoopControl step g⁻¹ := by
  have hpower : g ^ (orderOf g - 1) = g⁻¹ := by
    apply mul_eq_one_iff_eq_inv.mp
    rw [← pow_succ, Nat.sub_add_cancel (Nat.succ_le_of_lt (orderOf_pos g)),
      pow_orderOf_eq_one]
  rw [← hpower]
  exact loopControl_pow hg _

def controlledSubgroup [Finite G]
    (step : Label → Lane × G → Option (Lane × G)) : Subgroup G where
  carrier := LoopControl step
  one_mem' := loopControl_one step
  mul_mem' := loopControl_mul
  inv_mem' := loopControl_inv

theorem generated_loop_control [Finite G]
    (step : Label → Lane × G → Option (Lane × G)) (generators : Set G)
    (hgenerators : ∀ g ∈ generators, LoopControl step g)
    {g : G} (hg : g ∈ Subgroup.closure generators) : LoopControl step g := by
  have hle : Subgroup.closure generators ≤ controlledSubgroup step :=
    (Subgroup.closure_le _).mpr hgenerators
  exact hle hg

/-- Conditional spine of Theorem 4.1: geometric edge soundness, actual
relocation, and uniform generator loops are explicit inputs. -/
theorem guardedReach_iff_mem_generated [Finite G]
    (step : Label → Lane × G → Option (Lane × G))
    (generators : Set G) (source lane : Lane) (g : G)
    (hsound : ∀ label (x y : Lane × G), x.2 ∈ Subgroup.closure generators →
      step label x = some y → y.2 ∈ Subgroup.closure generators)
    (hrelocate : ∀ left right current,
      GuardedReach step (left, current) (right, current))
    (hgenerators : ∀ generator ∈ generators, LoopControl step generator) :
    GuardedReach step (source, 1) (lane, g) ↔ g ∈ Subgroup.closure generators := by
  constructor
  · rintro ⟨word, hword⟩
    exact runWord_preserves step
      (fun state => state.2 ∈ Subgroup.closure generators) hsound
      (Subgroup.one_mem _) hword
  · intro hg
    have hloops := generated_loop_control step generators hgenerators hg
    simpa using guardedReach_trans (hrelocate source lane 1) (hloops lane 1)

end GroupControl

end Rime.Paper37
