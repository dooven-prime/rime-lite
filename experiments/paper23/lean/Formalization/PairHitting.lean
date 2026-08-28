import Mathlib.Data.Finset.Card
import Mathlib.Order.Lattice.Nat

/-!
# Pair-hitting identity for finite deterministic automata

This file formalizes Theorem 2.1 of the synchronizing-automata manuscript.
Words act from left to right via `List.foldl`.  A word drops the cardinality of
a finite subset exactly when it merges two distinct states in that subset.
The equality of the two extended distances then follows from equality of their
sets of attainable word lengths.
-/

namespace Rime.SynchronizingAutomata

section PairHitting

variable {Q A : Type*} [DecidableEq Q]

/-- Left-to-right action of a word on one state. -/
def wordAction (δ : Q → A → Q) (q : Q) (w : List A) : Q :=
  w.foldl δ q

/-- Image of a finite state subset under a word. -/
def subsetImage (δ : Q → A → Q) (T : Finset Q) (w : List A) : Finset Q :=
  T.image fun q => wordAction δ q w

/-- A word strictly drops the cardinality of `T`. -/
def DropsSubset (δ : Q → A → Q) (T : Finset Q) (w : List A) : Prop :=
  (subsetImage δ T w).card < T.card

/-- A word merges the two declared states. -/
def MergesPair (δ : Q → A → Q) (x y : Q) (w : List A) : Prop :=
  wordAction δ x w = wordAction δ y w

/-- Attainable lengths of strict rank-drop words on `T`. -/
def escapeLengths (δ : Q → A → Q) (T : Finset Q) : Set (WithTop Nat) :=
  {d | ∃ w : List A, DropsSubset δ T w ∧ d = w.length}

/-- Attainable lengths of words merging `x` and `y`. -/
def pairMergeLengths (δ : Q → A → Q) (x y : Q) : Set (WithTop Nat) :=
  {d | ∃ w : List A, MergesPair δ x y w ∧ d = w.length}

/-- Extended rank-escape distance; `sInf ∅ = ⊤` in `WithTop Nat`. -/
noncomputable def escapeDistance (δ : Q → A → Q) (T : Finset Q) :
    WithTop Nat :=
  sInf (escapeLengths δ T)

/-- Extended pair-hitting distance. -/
noncomputable def pairDistance (δ : Q → A → Q) (x y : Q) :
    WithTop Nat :=
  sInf (pairMergeLengths δ x y)

theorem dropsSubset_iff_exists_merged_pair
    (δ : Q → A → Q) (T : Finset Q) (w : List A) :
    DropsSubset δ T w ↔
      ∃ x ∈ T, ∃ y ∈ T, x ≠ y ∧ MergesPair δ x y w := by
  constructor
  · intro hdrop
    simpa only [DropsSubset, subsetImage, MergesPair] using
      (Finset.exists_ne_map_eq_of_card_image_lt hdrop)
  · rintro ⟨x, hx, y, hy, hxy, hmerge⟩
    unfold DropsSubset subsetImage
    apply lt_of_le_of_ne Finset.card_image_le
    intro heq
    have hinj : Set.InjOn (fun q => wordAction δ q w) (T : Set Q) :=
      Finset.card_image_iff.mp heq
    exact hxy (hinj hx hy hmerge)

theorem escapeLengths_eq_iUnion_pairMergeLengths
    (δ : Q → A → Q) (T : Finset Q) :
    escapeLengths δ T =
      ⋃ x ∈ (T : Set Q), ⋃ y ∈ (T : Set Q),
        ⋃ (_hxy : x ≠ y), pairMergeLengths δ x y := by
  ext d
  constructor
  · rintro ⟨w, hdrop, hd⟩
    obtain ⟨x, hx, y, hy, hxy, hmerge⟩ :=
      (dropsSubset_iff_exists_merged_pair δ T w).mp hdrop
    refine Set.mem_iUnion.2 ⟨x, Set.mem_iUnion.2 ⟨hx, ?_⟩⟩
    refine Set.mem_iUnion.2 ⟨y, Set.mem_iUnion.2 ⟨hy, ?_⟩⟩
    refine Set.mem_iUnion.2 ⟨hxy, ?_⟩
    exact ⟨w, hmerge, hd⟩
  · intro hd
    obtain ⟨x, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hx, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨y, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hy, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hxy, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨w, hmerge, hd⟩ := hd
    exact ⟨w, (dropsSubset_iff_exists_merged_pair δ T w).2
      ⟨x, hx, y, hy, hxy, hmerge⟩, hd⟩

/-- The attainable-length formulation underlying Theorem 2.1. -/
theorem escapeDistance_eq_sInf_pairMergeLengths
    (δ : Q → A → Q) (T : Finset Q) :
    escapeDistance δ T =
      sInf (⋃ x ∈ (T : Set Q), ⋃ y ∈ (T : Set Q),
        ⋃ (_hxy : x ≠ y), pairMergeLengths δ x y) := by
  unfold escapeDistance
  rw [escapeLengths_eq_iUnion_pairMergeLengths]

/-- Theorem 2.1: rank-escape distance is the minimum pair-hitting distance
inside `T`.  The indexed infimum is a finite minimum when `T.card ≥ 2`; the
same statement also gives `⊤` for the empty and singleton cases. -/
theorem pair_hitting_identity
    (δ : Q → A → Q) (T : Finset Q) :
    escapeDistance δ T =
      ⨅ x ∈ (T : Set Q), ⨅ y ∈ (T : Set Q),
        ⨅ (_hxy : x ≠ y), pairDistance δ x y := by
  rw [escapeDistance_eq_sInf_pairMergeLengths]
  apply le_antisymm
  · refine le_iInf fun x => le_iInf fun hx => le_iInf fun y =>
      le_iInf fun hy => le_iInf fun hxy => ?_
    refine le_sInf ?_
    intro d hd
    apply sInf_le
    refine Set.mem_iUnion.2 ⟨x, Set.mem_iUnion.2 ⟨hx, ?_⟩⟩
    refine Set.mem_iUnion.2 ⟨y, Set.mem_iUnion.2 ⟨hy, ?_⟩⟩
    exact Set.mem_iUnion.2 ⟨hxy, hd⟩
  · refine le_sInf ?_
    intro d hd
    obtain ⟨x, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hx, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨y, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hy, hd⟩ := Set.mem_iUnion.1 hd
    obtain ⟨hxy, hd⟩ := Set.mem_iUnion.1 hd
    exact iInf_le_of_le x (iInf_le_of_le hx (iInf_le_of_le y
      (iInf_le_of_le hy (iInf_le_of_le hxy (sInf_le hd)))))

end PairHitting

end Rime.SynchronizingAutomata
