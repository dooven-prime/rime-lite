import FusionLogEnumeration.DeletionFiber
import FusionLogEnumeration.SurvivorRecovery

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

/-- Complete event lists whose associated schedule has the specified visible
survivors. The elements are logs, not execution words or schedule witnesses. -/
abbrev LogsWithSurvivors (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :=
  {log : AdmissibleLogs C (C.rank - s) //
    C.boundaries \ ((admissibleLogsEquivSchedule C _ log).deletions.toFinset) =
      survivors.1.image Subtype.val}

theorem survivor_image_card (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :
    (survivors.1.image Subtype.val).card = s := by
  rw [Finset.card_image_of_injective _ Subtype.val_injective, survivors.property]

theorem survivor_image_subset (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :
    survivors.1.image Subtype.val ⊆ C.boundaries := by
  rintro a ha
  obtain ⟨a, _, rfl⟩ := Finset.mem_image.mp ha
  exact a.property

/-- A literal boundary label outside the survivors is the same object as an
initial boundary subtype outside the typed survivor set. -/
def remainingBoundaryEquiv (C : MarkedCircle α) (s : ℕ)
    (survivors : SurvivingBoundaryChoices C s) :
    {a // a ∈ C.boundaries \ survivors.1.image Subtype.val} ≃
      {a : C.boundaries // a ∈ Finset.univ \ survivors.1} where
  toFun a := ⟨⟨a.1, (Finset.mem_sdiff.mp a.2).1⟩, by
    simp only [Finset.mem_sdiff, Finset.mem_univ, true_and]
    intro h
    exact (Finset.mem_sdiff.mp a.2).2 (Finset.mem_image.mpr ⟨_, h, rfl⟩)⟩
  invFun a := ⟨a.1.1, Finset.mem_sdiff.mpr ⟨a.1.2, by
    intro h
    obtain ⟨b, hb, same⟩ := Finset.mem_image.mp h
    have eq : b = a.1 := Subtype.ext same
    exact (Finset.mem_sdiff.mp a.2).2 (eq ▸ hb)⟩⟩
  left_inv _ := Subtype.ext rfl
  right_inv _ := Subtype.ext (Subtype.ext rfl)

/-- Restrict the boundary-deletion bijection to one survivor set. The inverse
uses every missing boundary exactly once, rather than counting schedules with
possibly redundant representations. -/
noncomputable def logsWithSurvivorsEquivOrderedDeletions
    (C : MarkedCircle α) (s : ℕ) (positive : 1 ≤ s) (bounded : s ≤ C.rank)
    (survivors : SurvivingBoundaryChoices C s) :
    LogsWithSurvivors C s survivors ≃
      OrderedDeletions (C.boundaries \ survivors.1.image Subtype.val) (C.rank - s) := by
  let e := admissibleLogsEquivBoundaryDeletions C (C.rank - s) (by omega)
  have boundaryCard : (C.boundaries \ survivors.1.image Subtype.val).card = C.rank - s := by
    rw [Finset.card_sdiff_of_subset (survivor_image_subset C s survivors),
      C.card_boundaries, survivor_image_card C s survivors]
  let encode : LogsWithSurvivors C s survivors →
      OrderedDeletions (C.boundaries \ survivors.1.image Subtype.val) (C.rank - s) := fun log =>
    ⟨(e log.1).1, (e log.1).2.1, (e log.1).2.2.1, by
      intro a ha
      have member := (e log.1).2.2.2 a ha
      have same := log.2
      change C.boundaries \ (e log.1).1.toFinset = survivors.1.image Subtype.val at same
      refine Finset.mem_sdiff.mpr ⟨member, ?_⟩
      rw [← same]
      exact fun h => (Finset.mem_sdiff.mp h).2 (List.mem_toFinset.mpr ha)⟩
  apply Equiv.ofBijective encode
  constructor
  · intro first second same
    apply Subtype.ext
    apply e.injective
    apply Subtype.ext
    exact congrArg (fun z : OrderedDeletions
      (C.boundaries \ survivors.1.image Subtype.val) (C.rank - s) => z.1) same
  · intro xs
    have inside : ∀ a ∈ xs.1, a ∈ C.boundaries :=
      fun a ha => (Finset.mem_sdiff.mp (xs.2.2.2 a ha)).1
    let raw : BoundaryDeletions C (C.rank - s) := ⟨xs.1, xs.2.1, xs.2.2.1, inside⟩
    have cover : xs.1.toFinset = C.boundaries \ survivors.1.image Subtype.val := by
      apply Finset.eq_of_subset_of_card_le
      · intro a ha
        exact xs.2.2.2 a (List.mem_toFinset.mp ha)
      · rw [List.toFinset_card_of_nodup xs.2.1, xs.2.2.1, boundaryCard]
    have same : C.boundaries \ xs.1.toFinset = survivors.1.image Subtype.val := by
      rw [cover]
      ext a
      have inside := survivor_image_subset C s survivors
      simp only [Finset.mem_sdiff]
      constructor
      · tauto
      · intro ha
        exact ⟨inside ha, by tauto⟩
    refine ⟨⟨e.symm raw, ?_⟩, ?_⟩
    · change C.boundaries \ (e (e.symm raw)).1.toFinset = _
      simpa only [e.apply_symm_apply] using same
    · apply Subtype.ext
      change (e (e.symm raw)).1 = xs.1
      rw [e.apply_symm_apply]

/-- The typed complement formulation used by the Section 5 counting layer. -/
noncomputable def logsWithSurvivorsEquivFixedSurvivorDeletionOrders
    (C : MarkedCircle α) (s : ℕ) (positive : 1 ≤ s) (bounded : s ≤ C.rank)
    (survivors : SurvivingBoundaryChoices C s) :
    LogsWithSurvivors C s survivors ≃ FixedSurvivorDeletionOrders C s survivors :=
  (logsWithSurvivorsEquivOrderedDeletions C s positive bounded survivors).trans
    ((orderedDeletionsEquivEmbedding _ _).trans
      ((Equiv.embeddingCongr (Equiv.refl _) (remainingBoundaryEquiv C s survivors)).trans
        (orderedDeletionsEquivEmbedding _ _).symm))

end FusionLogEnumeration
