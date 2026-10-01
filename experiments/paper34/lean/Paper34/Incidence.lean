import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Card

/-!
# Normalized terminal incidence

A terminal witness places two distinguished source lineages at the two points
of one marked collapse. This file checks the data-independent consequences:
the normalized incidence has exactly that double fiber, is injective on all
survivors, and avoids the collision root there. It also isolates the finite
cardinality argument that supplies a missing terminal coordinate.
-/

namespace Rime.Paper34

/-- The normalized marked collapse sends `zero` to `root` and fixes every
other coordinate. -/
def markedCollapse [DecidableEq Coord] (zero root : Coord) (q : Coord) : Coord :=
  if q = zero then root else q

theorem markedCollapse_eq_root_iff [DecidableEq Coord]
    (zero root q : Coord) :
    markedCollapse zero root q = root ↔ q = zero ∨ q = root := by
  by_cases hq : q = zero
  · subst q
    simp [markedCollapse]
  · simp [markedCollapse, hq]

/-- The abstract data read from one complete normalized terminal witness. -/
structure TerminalWitness (Lineage Coord : Type*) where
  pre : Lineage → Coord
  zero : Coord
  root : Coord
  first : Lineage
  second : Lineage

namespace TerminalWitness

variable {Lineage Coord : Type*} [DecidableEq Coord]

structure Valid (w : TerminalWitness Lineage Coord) : Prop where
  injective_pre : Function.Injective w.pre
  zero_ne_root : w.zero ≠ w.root
  pre_first : w.pre w.first = w.zero
  pre_second : w.pre w.second = w.root

def incidence (w : TerminalWitness Lineage Coord) : Lineage → Coord :=
  markedCollapse w.zero w.root ∘ w.pre

def IsSurvivor (w : TerminalWitness Lineage Coord) (q : Lineage) : Prop :=
  q ≠ w.first ∧ q ≠ w.second

omit [DecidableEq Coord] in
theorem first_ne_second (w : TerminalWitness Lineage Coord) (hw : w.Valid) :
    w.first ≠ w.second := by
  intro h
  apply hw.zero_ne_root
  calc
    w.zero = w.pre w.first := hw.pre_first.symm
    _ = w.pre w.second := by rw [h]
    _ = w.root := hw.pre_second

/-- The collision-root fiber is exactly the declared fused pair. -/
theorem incidence_eq_root_iff (w : TerminalWitness Lineage Coord) (hw : w.Valid)
    (q : Lineage) :
    w.incidence q = w.root ↔ q = w.first ∨ q = w.second := by
  rw [incidence, Function.comp_apply, markedCollapse_eq_root_iff]
  constructor
  · rintro (hq | hq)
    · exact Or.inl (hw.injective_pre (hq.trans hw.pre_first.symm))
    · exact Or.inr (hw.injective_pre (hq.trans hw.pre_second.symm))
  · rintro (rfl | rfl)
    · exact Or.inl hw.pre_first
    · exact Or.inr hw.pre_second

theorem root_fiber (w : TerminalWitness Lineage Coord) (hw : w.Valid) :
    {q | w.incidence q = w.root} = ({w.first, w.second} : Set Lineage) := by
  ext q
  simp [w.incidence_eq_root_iff hw q]

/-- Outside the fused pair, the strict-exit incidence remains injective. -/
theorem incidence_injOn_survivors (w : TerminalWitness Lineage Coord)
    (hw : w.Valid) :
    Set.InjOn w.incidence {q | w.IsSurvivor q} := by
  intro x hx y hy hxy
  change x ≠ w.first ∧ x ≠ w.second at hx
  change y ≠ w.first ∧ y ≠ w.second at hy
  have hx0 : w.pre x ≠ w.zero := by
    intro h
    exact hx.1 (hw.injective_pre (h.trans hw.pre_first.symm))
  have hy0 : w.pre y ≠ w.zero := by
    intro h
    exact hy.1 (hw.injective_pre (h.trans hw.pre_first.symm))
  apply hw.injective_pre
  simpa [incidence, markedCollapse, hx0, hy0] using hxy

theorem incidence_ne_root_of_survivor
    (w : TerminalWitness Lineage Coord) {q : Lineage}
    (hw : w.Valid)
    (hq : w.IsSurvivor q) :
    w.incidence q ≠ w.root := by
  intro hroot
  rcases (w.incidence_eq_root_iff hw q).mp hroot with hfirst | hsecond
  · exact hq.1 hfirst
  · exact hq.2 hsecond

/-- On a finite lineage type, the collision-root fiber has cardinality two. -/
theorem root_fiber_card [Fintype Lineage] [DecidableEq Lineage]
    (w : TerminalWitness Lineage Coord) (hw : w.Valid) :
    (Finset.univ.filter fun q => w.incidence q = w.root).card = 2 := by
  have hfiber :
      Finset.univ.filter (fun q => w.incidence q = w.root) =
        {w.first, w.second} := by
    ext q
    simp [w.incidence_eq_root_iff hw q]
  rw [hfiber]
  simp [w.first_ne_second hw]

end TerminalWitness

/-- A placement of fewer source lineages than carrier coordinates omits at
least one coordinate. This is the cardinality core of the manuscript's
missing-hole terminal realization. -/
theorem exists_missing_coordinate
    [Fintype Source] [Fintype Coord]
    (placement : Source → Coord)
    (hcard : Fintype.card Source < Fintype.card Coord) :
    ∃ q, q ∉ Set.range placement := by
  by_contra hmissing
  push Not at hmissing
  have hsurjective : Function.Surjective placement := by
    intro q
    exact hmissing q
  have hle : Fintype.card Coord ≤ Fintype.card Source :=
    Fintype.card_le_of_surjective placement hsurjective
  exact (Nat.not_lt_of_ge hle) hcard

end Rime.Paper34
