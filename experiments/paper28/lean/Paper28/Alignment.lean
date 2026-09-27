import Std

/-!
# Paper XXVIII: alignment transport spine

The finite existence of canonical images is certificate-owned. An observable
bundle can include typed boundary, ancestry, normalization, and provenance;
this module assumes their preservation and proves only return transport.
-/

namespace Rime.Paper28

structure Alignment (Adapter : Type u) (Canonical : Type v)
    (Observable : Type w) where
  adapterPath : Adapter → Prop
  canonicalPath : Canonical → Prop
  image : Adapter → Canonical
  image_mem : ∀ {path}, adapterPath path → canonicalPath (image path)
  readAdapter : Adapter → Observable
  readCanonical : Canonical → Observable
  preserves : ∀ {path}, adapterPath path →
    readCanonical (image path) = readAdapter path

def AdapterReturn (alignment : Alignment Adapter Canonical Observable)
    (criterion : Observable → Target → Prop) (path : Adapter)
    (target : Target) : Prop :=
  alignment.adapterPath path ∧ criterion (alignment.readAdapter path) target

def CanonicalReturn (alignment : Alignment Adapter Canonical Observable)
    (criterion : Observable → Target → Prop) (path : Canonical)
    (target : Target) : Prop :=
  alignment.canonicalPath path ∧ criterion (alignment.readCanonical path) target

/-- One adapter return remains a return along its certified path image. -/
theorem alignment_return_transport
    (alignment : Alignment Adapter Canonical Observable)
    (criterion : Observable → Target → Prop)
    (path : Adapter) (target : Target)
    (hreturn : AdapterReturn alignment criterion path target) :
    CanonicalReturn alignment criterion (alignment.image path) target := by
  obtain ⟨hpath, hcriterion⟩ := hreturn
  refine ⟨alignment.image_mem hpath, ?_⟩
  rw [alignment.preserves hpath]
  exact hcriterion

theorem existential_alignment_return_transport
    (alignment : Alignment Adapter Canonical Observable)
    (criterion : Observable → Target → Prop) (target : Target)
    (hreturn : ∃ path, AdapterReturn alignment criterion path target) :
    ∃ path, CanonicalReturn alignment criterion path target := by
  obtain ⟨path, hpath⟩ := hreturn
  exact ⟨alignment.image path,
    alignment_return_transport alignment criterion path target hpath⟩

/-- An injective path image may still miss canonical paths. -/
theorem alignment_not_relation_equality_control :
    Function.Injective (fun _ : Unit => false) ∧
      ¬ Function.Surjective (fun _ : Unit => false) := by
  constructor
  · intro a b _
    cases a
    cases b
    rfl
  · intro hsurj
    obtain ⟨_, heq⟩ := hsurj true
    cases heq

end Rime.Paper28
