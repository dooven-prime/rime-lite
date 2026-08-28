import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic

/-!
# Finite Typed Context Descent

Lean core for the free finite-signature results. A signature is represented as
an `Option`-valued function so that definedness is part of local equality.
-/

namespace FiniteTypedContextDescent

variable {Atom Index Value : Type*} [DecidableEq Atom]

abbrev Signature (Atom Value : Type*) := Atom → Option Value

abbrev Cover (Index Atom : Type*) [DecidableEq Atom] := Index → Finset Atom

def Covers (U : Cover Index Atom) : Prop :=
  ∀ atom, ∃ index, atom ∈ U index

def LocallyEqual (U : Cover Index Atom)
    (left right : Signature Atom Value) : Prop :=
  ∀ index atom, atom ∈ U index → left atom = right atom

def JointlySeparating (U : Cover Index Atom) : Prop :=
  ∀ left right : Signature Atom Value,
    LocallyEqual U left right → left = right

theorem covers_implies_jointlySeparating
    {U : Cover Index Atom} (hcover : Covers U) :
    JointlySeparating (Value := Value) U := by
  intro left right hlocal
  funext atom
  obtain ⟨index, hmem⟩ := hcover atom
  exact hlocal index atom hmem

theorem jointlySeparating_implies_covers [Nonempty Value]
    {U : Cover Index Atom}
    (hseparating : JointlySeparating (Value := Value) U) :
    Covers U := by
  classical
  intro atom
  by_contra hmissing
  push Not at hmissing
  let value : Value := Classical.choice inferInstance
  let left : Signature Atom Value := fun _ => none
  let right : Signature Atom Value := fun candidate =>
    if candidate = atom then some value else none
  have hlocal : LocallyEqual U left right := by
    intro index candidate hmem
    have hne : candidate ≠ atom := by
      intro heq
      subst candidate
      exact hmissing index hmem
    simp [left, right, hne]
  have heq := hseparating left right hlocal
  have hatom := congrFun heq atom
  simp [left, right] at hatom

theorem jointlySeparating_iff_covers [Nonempty Value]
    {U : Cover Index Atom} :
    JointlySeparating (Value := Value) U ↔ Covers U := by
  constructor
  · exact jointlySeparating_implies_covers
  · exact covers_implies_jointlySeparating

abbrev LocalSection (U : Cover Index Atom) (index : Index) :=
  {atom : Atom // atom ∈ U index} → Option Value

def Compatible (U : Cover Index Atom)
    (sections : ∀ index, LocalSection (Value := Value) U index) : Prop :=
  ∀ i j atom (hi : atom ∈ U i) (hj : atom ∈ U j),
    sections i ⟨atom, hi⟩ = sections j ⟨atom, hj⟩

def RestrictsTo (U : Cover Index Atom)
    (global : Signature Atom Value)
    (sections : ∀ index, LocalSection (Value := Value) U index) : Prop :=
  ∀ index atom (hmem : atom ∈ U index),
    global atom = sections index ⟨atom, hmem⟩

noncomputable def glue {U : Cover Index Atom}
    (hcover : Covers U)
    (sections : ∀ index, LocalSection (Value := Value) U index) :
    Signature Atom Value :=
  fun atom =>
    sections (Classical.choose (hcover atom))
      ⟨atom, Classical.choose_spec (hcover atom)⟩

theorem glue_restricts {U : Cover Index Atom}
    (hcover : Covers U)
    (sections : ∀ index, LocalSection (Value := Value) U index)
    (hcompatible : Compatible U sections) :
    RestrictsTo U (glue hcover sections) sections := by
  intro index atom hmem
  exact hcompatible
    (Classical.choose (hcover atom)) index atom
    (Classical.choose_spec (hcover atom)) hmem

theorem finite_free_gluing {U : Cover Index Atom}
    (hcover : Covers U)
    (sections : ∀ index, LocalSection (Value := Value) U index)
    (hcompatible : Compatible U sections) :
    ∃! global : Signature Atom Value, RestrictsTo U global sections := by
  refine ⟨glue hcover sections, glue_restricts hcover sections hcompatible, ?_⟩
  intro candidate hcandidate
  funext atom
  obtain ⟨index, hmem⟩ := hcover atom
  exact (hcandidate index atom hmem).trans
    (glue_restricts hcover sections hcompatible index atom hmem).symm

inductive TriangleAtom where
  | ab
  | bc
  | ac
  deriving DecidableEq, Repr

def incompleteTriangleCover : Cover Bool TriangleAtom
  | false => {TriangleAtom.ab}
  | true => {TriangleAtom.bc}

def triangleLeft : Signature TriangleAtom Bool
  | .ab => some true
  | .bc => some true
  | .ac => some false

def triangleRight : Signature TriangleAtom Bool
  | .ab => some true
  | .bc => some true
  | .ac => some true

theorem triangle_label_cover_lookalike_is_not_separating :
    LocallyEqual incompleteTriangleCover triangleLeft triangleRight ∧
      triangleLeft ≠ triangleRight := by
  constructor
  · intro index atom hmem
    cases index <;> simp [incompleteTriangleCover] at hmem
    · subst atom
      rfl
    · subst atom
      rfl
  · intro heq
    have hac := congrFun heq TriangleAtom.ac
    simp [triangleLeft, triangleRight] at hac

inductive TrianglePatch where
  | ab
  | bc
  | ac
  deriving DecidableEq, Repr

def completeTriangleCover : Cover TrianglePatch TriangleAtom
  | .ab => {TriangleAtom.ab}
  | .bc => {TriangleAtom.bc}
  | .ac => {TriangleAtom.ac}

theorem completeTriangleCover_covers : Covers completeTriangleCover := by
  intro atom
  cases atom with
  | ab => exact ⟨TrianglePatch.ab, by simp [completeTriangleCover]⟩
  | bc => exact ⟨TrianglePatch.bc, by simp [completeTriangleCover]⟩
  | ac => exact ⟨TrianglePatch.ac, by simp [completeTriangleCover]⟩

theorem completeTriangleCover_is_separating :
    JointlySeparating (Value := Bool) completeTriangleCover :=
  covers_implies_jointlySeparating completeTriangleCover_covers

end FiniteTypedContextDescent
