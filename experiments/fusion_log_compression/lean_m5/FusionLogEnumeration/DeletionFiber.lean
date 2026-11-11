import FusionLogEnumeration.EndpointCounting

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

/-- An ordered deletion history using every element of a fixed finite boundary
set exactly once. -/
abbrev OrderedDeletions (D : Finset α) (d : ℕ) :=
  {xs : List α // xs.Nodup ∧ xs.length = d ∧ ∀ a ∈ xs, a ∈ D}

noncomputable def orderedDeletionsEquivEmbedding (D : Finset α) (d : ℕ) :
    OrderedDeletions D d ≃ (Fin d ↪ D) := by
  let encode : OrderedDeletions D d → (Fin d ↪ D) := fun xs =>
    { toFun := fun i => ⟨xs.1.get (Fin.cast xs.2.2.1.symm i),
        xs.2.2.2 _ (List.get_mem _ _)⟩
      inj' := by
        intro i j same
        have eq := (List.nodup_iff_injective_get.mp xs.2.1)
          (congrArg Subtype.val same)
        exact Fin.ext (congrArg (fun k : Fin xs.1.length => k.val) eq) }
  apply Equiv.ofBijective encode
  constructor
  · intro xs ys same
    apply Subtype.ext
    apply List.ext_get
    · exact xs.2.2.1.trans ys.2.2.1.symm
    · intro i hi hj
      have eq := congrArg (fun e : Fin d ↪ D => (e ⟨i, by omega⟩).val) same
      exact eq
  · intro f
    let xs : List α := List.ofFn (fun i : Fin d => (f i).val)
    have nodup : xs.Nodup := by
      rw [List.nodup_iff_injective_get]
      intro i j eq
      have values : (f ⟨i.val, by simpa [xs] using i.isLt⟩).val =
          (f ⟨j.val, by simpa [xs] using j.isLt⟩).val := by simpa [xs] using eq
      have indices := f.injective (Subtype.ext values)
      exact Fin.ext (congrArg (fun k : Fin d => k.val) indices)
    have inside : ∀ a ∈ xs, a ∈ D := by
      intro a member
      obtain ⟨i, rfl⟩ := List.mem_ofFn.mp member
      exact (f i).property
    refine ⟨⟨xs, nodup, by simp [xs], inside⟩, ?_⟩
    apply Function.Embedding.ext
    intro i
    apply Subtype.ext
    simp [encode, xs]

noncomputable instance orderedDeletionsFintype (D : Finset α) (d : ℕ) :
    Fintype (OrderedDeletions D d) :=
  Fintype.ofEquiv (Fin d ↪ D) (orderedDeletionsEquivEmbedding D d).symm

omit [DecidableEq α] in
theorem card_orderedDeletions (D : Finset α) (d : ℕ)
    (card_eq : D.card = d) :
    Fintype.card (OrderedDeletions D d) = d.factorial := by
  rw [Fintype.card_congr (orderedDeletionsEquivEmbedding D d),
    Fintype.card_embedding_eq]
  rw [Fintype.card_fin, Fintype.card_coe D, card_eq]
  exact Nat.descFactorial_self d

/-- Deletion orders for the complement of a specified survivor set. This is a
combinatorial fibre; it is an actual literal-endpoint log fibre only when the
endpoint semantics makes the survivor set visible (in particular, rank ≥ 2). -/
abbrev FixedSurvivorDeletionOrders (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :=
  OrderedDeletions (Finset.univ \ survivors.1) (C.rank - s)

theorem remainingBoundary_card (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :
    (Finset.univ \ survivors.1).card = C.rank - s := by
  have hcard : Fintype.card C.boundaries = C.rank := by
    rw [Fintype.card_coe, C.card_boundaries]
  rw [Finset.card_sdiff_of_subset (Finset.subset_univ _), Finset.card_univ,
    hcard, survivors.property]

theorem card_fixedSurvivorDeletionOrders (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :
    Fintype.card (FixedSurvivorDeletionOrders C s survivors) =
      (C.rank - s).factorial := by
  exact card_orderedDeletions _ _ (remainingBoundary_card C s survivors)

end FusionLogEnumeration
