import Paper38.ReturnLayers
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.GroupTheory.Index
import Mathlib.Data.Fintype.Perm

/-!
# Cumulative saturation without a deterministic coset update

G is the generated group, not a larger ambient carrier. The hypotheses
say A generates G and A,B are invariant under left phase multiplication.
The proof counts entire phase blocks and does not require normality.
-/

namespace Rime.Paper38

open scoped Pointwise

variable {G : Type*} [Group G] [Fintype G] [DecidableEq G]

def preservingMonoid (S : Finset G) : Submonoid G where
  carrier := {g | ∀ x ∈ S, g * x ∈ S}
  one_mem' := by intro x hx; simpa using hx
  mul_mem' := by
    intro a b ha hb x hx
    simpa [mul_assoc] using ha (b * x) (hb x hx)

omit [DecidableEq G] in
theorem positiveClosure_eq_subgroup (A : Finset G) :
    Submonoid.closure (A : Set G) = (Subgroup.closure (A : Set G)).toSubmonoid :=
  Subgroup.closure_toSubmonoid_of_finite.symm

theorem no_premature_stall (A S : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hS : S.Nonempty)
    (hstall : S ∪ A * S = S) : S = Finset.univ := by
  have hle : Submonoid.closure (A : Set G) ≤ preservingMonoid S := by
    apply Submonoid.closure_le.mpr
    intro a ha x hx
    rw [← hstall]
    exact Finset.mem_union_right _ (Finset.mem_mul.mpr ⟨a, ha, x, hx, rfl⟩)
  rw [positiveClosure_eq_subgroup, hgen] at hle
  obtain ⟨y, hy⟩ := hS
  apply Finset.eq_univ_iff_forall.mpr
  intro z
  have hp : z * y⁻¹ ∈ preservingMonoid S := hle (by trivial)
  simpa using hp y hy

theorem cumulative_stall_iff_full (A B : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hB : B.Nonempty) (n : Nat) :
    cumulativeLayer A B (n + 1) = cumulativeLayer A B n ↔
      cumulativeLayer A B n = Finset.univ := by
  constructor
  · exact no_premature_stall A _ hgen (cumulativeLayer_nonempty A B hB n)
  · intro hfull
    simp [cumulativeLayer, hfull]

noncomputable def phaseCoset (H : Subgroup G) [Fintype H] (x : G) : Finset G :=
  Finset.univ.image (fun h : H => (h : G) * x)

omit [Fintype G] in
theorem phaseCoset_card (H : Subgroup G) [Fintype H] (x : G) :
    (phaseCoset H x).card = Fintype.card H := by
  rw [phaseCoset, Finset.card_image_of_injective]
  · exact Finset.card_univ
  · intro h k heq
    exact Subtype.ext (mul_right_cancel heq)

omit [Fintype G] in
theorem phaseCoset_subset (H : Subgroup G) [Fintype H] (S : Finset G)
    (hS : LeftStable H S) {x : G} (hx : x ∈ S) : phaseCoset H x ⊆ S := by
  intro y hy
  obtain ⟨h, _, rfl⟩ := Finset.mem_image.mp hy
  exact hS h h.property x hx

omit [Fintype G] in
theorem phaseCoset_leftStable (H : Subgroup G) [Fintype H] (x : G) :
    LeftStable H (phaseCoset H x) := by
  intro h hh y hy
  obtain ⟨k, _, rfl⟩ := Finset.mem_image.mp hy
  apply Finset.mem_image.mpr
  exact ⟨⟨h * k, H.mul_mem hh k.property⟩, Finset.mem_univ _, mul_assoc _ _ _⟩

noncomputable def phaseAggregate (H : Subgroup G) [Fintype H] (S : Finset G) : Finset G :=
  S.biUnion (phaseCoset H)

omit [Fintype G] in
theorem phaseAggregate_leftStable (H : Subgroup G) [Fintype H] (S : Finset G) :
    LeftStable H (phaseAggregate H S) := by
  intro h hh x hx
  obtain ⟨s, hs, hx⟩ := Finset.mem_biUnion.mp hx
  exact Finset.mem_biUnion.mpr ⟨s, hs, phaseCoset_leftStable H s h hh x hx⟩

omit [Fintype G] in
theorem local_mem_phaseAggregate (H : Subgroup G) [Fintype H] (S : Finset G)
    {s : G} (hs : s ∈ S) : s ∈ phaseAggregate H S := by
  apply Finset.mem_biUnion.mpr
  refine ⟨s, hs, Finset.mem_image.mpr ?_⟩
  exact ⟨1, Finset.mem_univ _, by simp⟩

omit [Fintype G] in
theorem phaseAggregate_closure (H : Subgroup G) [Fintype H] (S : Finset G)
    (hS : S.Nonempty) :
    Subgroup.closure (phaseAggregate H S : Set G) =
      Subgroup.closure ((H : Set G) ∪ (S : Set G)) := by
  apply le_antisymm
  · apply (Subgroup.closure_le _).mpr
    intro x hx
    obtain ⟨s, hs, hx⟩ := Finset.mem_biUnion.mp hx
    obtain ⟨h, _, rfl⟩ := Finset.mem_image.mp hx
    exact Subgroup.mul_mem _ (Subgroup.subset_closure (Or.inl h.property))
      (Subgroup.subset_closure (Or.inr hs))
  · apply (Subgroup.closure_le _).mpr
    intro x hx
    rcases hx with hx | hx
    · obtain ⟨s, hs⟩ := hS
      have hsC := Subgroup.subset_closure (local_mem_phaseAggregate H S hs)
      have hxs : x * s ∈ phaseAggregate H S :=
        Finset.mem_biUnion.mpr ⟨s, hs,
          Finset.mem_image.mpr ⟨⟨x, hx⟩, Finset.mem_univ _, rfl⟩⟩
      have hmul := Subgroup.mul_mem (Subgroup.closure (phaseAggregate H S : Set G))
        (Subgroup.subset_closure hxs) (Subgroup.inv_mem _ hsC)
      simpa using hmul
    · exact Subgroup.subset_closure (local_mem_phaseAggregate H S hx)

omit [Fintype G] in
theorem phaseCoset_disjoint (H : Subgroup G) [Fintype H] (S : Finset G)
    (hS : LeftStable H S) {x : G} (hx : x ∉ S) : Disjoint S (phaseCoset H x) := by
  apply Finset.disjoint_left.mpr
  intro y hy hcoset
  obtain ⟨h, _, rfl⟩ := Finset.mem_image.mp hcoset
  have hxS := hS (h : G)⁻¹ (H.inv_mem h.property) ((h : G) * x) hy
  exact hx (by simpa using hxS)

omit [Fintype G] in
theorem stable_strict_growth (H : Subgroup G) [Fintype H] (S T : Finset G)
    (hS : LeftStable H S) (hT : LeftStable H T)
    (hST : S ⊆ T) (hne : T ≠ S) : S.card + Fintype.card H ≤ T.card := by
  have hnot : ¬ T ⊆ S := fun h => hne (Finset.Subset.antisymm h hST)
  obtain ⟨x, hxT, hxS⟩ := Finset.not_subset.mp hnot
  have hle : S ∪ phaseCoset H x ⊆ T :=
    Finset.union_subset hST (phaseCoset_subset H T hT hxT)
  have hcard := Finset.card_le_card hle
  rwa [Finset.card_union_of_disjoint (phaseCoset_disjoint H S hS hxS), phaseCoset_card] at hcard

theorem cumulative_card_growth (H : Subgroup G) [Fintype H] (A B : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hBne : B.Nonempty)
    (hA : LeftStable H A) (hB : LeftStable H B) (n : Nat)
    (hproper : cumulativeLayer A B n ≠ Finset.univ) :
    (cumulativeLayer A B n).card + Fintype.card H ≤ (cumulativeLayer A B (n + 1)).card := by
  apply stable_strict_growth H _ _
    (cumulativeLayer_leftStable H A B hA hB n)
    (cumulativeLayer_leftStable H A B hA hB (n + 1))
    (cumulativeLayer_mono A B (Nat.le_succ n))
  intro hstall
  exact hproper ((cumulative_stall_iff_full A B hgen hBne n).mp hstall)

theorem cumulative_card_lower_bound (H : Subgroup G) [Fintype H] (A B : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hBne : B.Nonempty)
    (hA : LeftStable H A) (hB : LeftStable H B) (n : Nat)
    (hproper : cumulativeLayer A B n ≠ Finset.univ) :
    (n + 1) * Fintype.card H ≤ (cumulativeLayer A B n).card := by
  induction n with
  | zero =>
      obtain ⟨x, hx⟩ := hBne
      have hle := Finset.card_le_card (phaseCoset_subset H B hB hx)
      simpa [cumulativeLayer, phaseCoset_card] using hle
  | succ n ih =>
      have hprev : cumulativeLayer A B n ≠ Finset.univ := by
        intro hfull
        apply hproper
        apply Finset.Subset.antisymm (Finset.subset_univ _)
        rw [← hfull]
        exact cumulativeLayer_mono A B (Nat.le_succ n)
      have lower := ih hprev
      have growth := cumulative_card_growth H A B hgen hBne hA hB n hprev
      calc
        (n + 1 + 1) * Fintype.card H = (n + 1) * Fintype.card H + Fintype.card H := by
          rw [Nat.add_mul, Nat.one_mul]
        _ ≤ (cumulativeLayer A B n).card + Fintype.card H := Nat.add_le_add_right lower _
        _ ≤ (cumulativeLayer A B (n + 1)).card := growth

theorem cumulative_full_at_index (H : Subgroup G) [Fintype H] (A B : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hBne : B.Nonempty)
    (hA : LeftStable H A) (hB : LeftStable H B) :
    cumulativeLayer A B (H.index - 1) = Finset.univ := by
  have hi : 0 < H.index := Nat.pos_of_ne_zero H.index_ne_zero_of_finite
  have hcard : H.index * Fintype.card H = Fintype.card G := by
    simpa only [Nat.card_eq_fintype_card] using H.index_mul_card
  by_contra hproper
  have lower := cumulative_card_lower_bound H A B hgen hBne hA hB _ hproper
  rw [Nat.sub_add_cancel hi] at lower
  have hfull : cumulativeLayer A B (H.index - 1) = Finset.univ := by
    apply Finset.eq_of_subset_of_card_le (Finset.subset_univ _)
    simpa [Finset.card_univ, hcard] using lower
  exact hproper hfull

theorem at_most_index_product_word (H : Subgroup G) [Fintype H] (A B : Finset G)
    (hgen : Subgroup.closure (A : Set G) = ⊤) (hBne : B.Nonempty)
    (hA : LeftStable H A) (hB : LeftStable H B) (x : G) :
    ∃ n < H.index, ∃ word : List G, word.length = n ∧
      (∀ a ∈ word, a ∈ A) ∧ ∃ b ∈ B, x = word.prod * b := by
  have hx : x ∈ cumulativeLayer A B (H.index - 1) := by
    rw [cumulative_full_at_index H A B hgen hBne hA hB]
    exact Finset.mem_univ _
  obtain ⟨n, hn, hx⟩ := (mem_cumulativeLayer_iff A B _ x).mp hx
  have hi : 0 < H.index := Nat.pos_of_ne_zero H.index_ne_zero_of_finite
  refine ⟨n, by omega, ?_⟩
  exact (mem_exactLayer_iff_product_word A B n x).mp hx

theorem five_phase_index_le_twentyFour (K : Subgroup (Equiv.Perm (Fin 5)))
    (H : Subgroup K) (hH : Nat.card H = 5) : H.index ≤ 24 := by
  have hk : Nat.card K ≤ 120 := by
    have hle := Nat.card_le_card_of_injective (f := fun x : K => (x : Equiv.Perm (Fin 5)))
      Subtype.val_injective
    have hperm : Nat.card (Equiv.Perm (Fin 5)) = 120 := by
      rw [Nat.card_eq_fintype_card, Fintype.card_perm]
      simp only [Fintype.card_fin]
      decide
    rw [hperm] at hle
    exact hle
  have hm := H.index_mul_card
  rw [hH] at hm
  omega

theorem uniform_twentyFour_product_word (K : Subgroup (Equiv.Perm (Fin 5)))
    [Fintype K] [DecidableEq K] (H : Subgroup K) [Fintype H]
    (hH : Nat.card H = 5) (A B : Finset K)
    (hgen : Subgroup.closure (A : Set K) = ⊤) (hBne : B.Nonempty)
    (hA : LeftStable H A) (hB : LeftStable H B) (x : K) :
    ∃ n, n + 1 ≤ 24 ∧ ∃ word : List K, word.length = n ∧
      (∀ a ∈ word, a ∈ A) ∧ ∃ b ∈ B, x = word.prod * b := by
  obtain ⟨n, hn, hword⟩ := at_most_index_product_word H A B hgen hBne hA hB x
  exact ⟨n, (Nat.succ_le_of_lt hn).trans (five_phase_index_le_twentyFour K H hH), hword⟩

end Rime.Paper38
