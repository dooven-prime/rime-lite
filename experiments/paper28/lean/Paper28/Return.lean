import Std

/-!
# Paper XXVIII: typed existential return spine

The menu and lift relations are source-addressed inputs. Their future-free
construction, exact replay, and finite coverage are not derived here.
The handoff relation is an explicit, same-word premise.
-/

namespace Rime.Paper28

structure TypedLifts (Source : Type u) (Target : Type v)
    (Menu : Type w) (Word : Type x) where
  offered : Source → Menu → Prop
  lift : Source → Menu → Word → Prop
  source : Word → Source
  handoff : Word → Target → Prop
  lift_offered : ∀ {s m word}, lift s m word → offered s m
  lift_source : ∀ {s m word}, lift s m word → source word = s

def Reaches (system : TypedLifts Source Target Menu Word)
    (source : Source) (target : Target) : Prop :=
  ∃ menu word, system.offered source menu ∧
    system.lift source menu word ∧ system.handoff word target

/-- All fields refer to the same upper word and its certified middle target. -/
structure ReturnChain
    (upper : TypedLifts C5 C4 M5 W5)
    (lower : TypedLifts C4 C3 M4 W4)
    (section4 : C4 → Prop) (base : C3 → Prop) (source5 : C5) where
  middle : C4
  upperMenu : M5
  upperWord : W5
  lowerMenu : M4
  lowerWord : W4
  terminal : C3
  middle_section : section4 middle
  upper_offered : upper.offered source5 upperMenu
  upper_lift : upper.lift source5 upperMenu upperWord
  upper_handoff : upper.handoff upperWord middle
  lower_offered : lower.offered middle lowerMenu
  lower_lift : lower.lift middle lowerMenu lowerWord
  lower_handoff : lower.handoff lowerWord terminal
  terminal_base : base terminal

/-- The abstract logical implication used after the two finite certificates. -/
theorem existential_return_compose
    (upper : TypedLifts C5 C4 M5 W5)
    (lower : TypedLifts C4 C3 M4 W4)
    (section5 : C5 → Prop) (section4 : C4 → Prop) (base : C3 → Prop)
    (hupper : ∀ source, section5 source →
      ∃ middle, section4 middle ∧ Reaches upper source middle)
    (hlower : ∀ middle, section4 middle →
      ∃ terminal, base terminal ∧ Reaches lower middle terminal)
    (source5 : C5) (hsource : section5 source5) :
    Nonempty (ReturnChain upper lower section4 base source5) := by
  obtain ⟨middle, hmiddle, m5, x, hm5, hx, hhx⟩ := hupper source5 hsource
  obtain ⟨terminal, hbase, m4, y, hm4, hy, hhy⟩ := hlower middle hmiddle
  exact ⟨{
    middle := middle
    upperMenu := m5
    upperWord := x
    lowerMenu := m4
    lowerWord := y
    terminal := terminal
    middle_section := hmiddle
    upper_offered := hm5
    upper_lift := hx
    upper_handoff := hhx
    lower_offered := hm4
    lower_lift := hy
    lower_handoff := hhy
    terminal_base := hbase
  }⟩

/-- Separate existential witnesses cannot be silently fused. -/
theorem separate_exists_not_same_witness :
    (∃ b : Bool, b = false) ∧ (∃ b : Bool, b = true) ∧
      ¬ (∃ b : Bool, b = false ∧ b = true) := by
  refine ⟨⟨false, rfl⟩, ⟨true, rfl⟩, ?_⟩
  intro h
  obtain ⟨b, hfalse, htrue⟩ := h
  cases hfalse
  cases htrue

end Rime.Paper28
