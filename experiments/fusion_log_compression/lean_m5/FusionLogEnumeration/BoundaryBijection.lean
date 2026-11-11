import FusionLogEnumeration.Schedules

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

/-- Ordered distinct original boundaries, restricted to the current circle. -/
abbrev BoundaryDeletions (C : MarkedCircle α) (d : ℕ) :=
  {xs : List α // xs.Nodup ∧ xs.length = d ∧ ∀ a ∈ xs, a ∈ C.boundaries}

theorem exists_schedule_of_deletions (C : MarkedCircle α) (xs : List α)
    (nodup : xs.Nodup) (inside : ∀ a ∈ xs, a ∈ C.boundaries)
    (short : xs.length < C.rank) :
    ∃ path : Schedule C xs.length, path.deletions = xs := by
  induction xs generalizing C with
  | nil => exact ⟨.stop C, rfl⟩
  | cons a xs ih =>
      have hr : 2 ≤ C.rank := by simp only [List.length_cons] at short; omega
      let i := C.boundaryEquiv.symm ⟨a, inside a (by simp)⟩
      have chosen : C.deleted i hr = a := by
        have eq := congrArg Subtype.val (C.boundaryEquiv.apply_symm_apply
          ⟨a, inside a (by simp)⟩)
        change C.packets[i].boundary = a at eq
        simpa [MarkedCircle.deleted_eq_get, i] using eq
      have small : xs.length < (C.contract i hr).rank := by
        have := C.rank_contract i hr
        simp only [List.length_cons] at short
        omega
      have nextInside : ∀ b ∈ xs, b ∈ (C.contract i hr).boundaries := by
        intro b member
        rw [C.boundaries_contract i hr, chosen]
        exact Finset.mem_erase.mpr ⟨by
          intro eq
          subst b
          exact (List.nodup_cons.mp nodup).1 member,
          inside b (by simp [member])⟩
      obtain ⟨tail, tailEq⟩ := ih (C.contract i hr) (List.nodup_cons.mp nodup).2 nextInside small
      exact ⟨.step hr i tail, by simp only [Schedule.deletions, chosen, tailEq]⟩

noncomputable def scheduleEquivBoundaryDeletions (C : MarkedCircle α) (d : ℕ)
    (short : d < C.rank) : Schedule C d ≃ BoundaryDeletions C d := by
  apply Equiv.ofBijective (fun path =>
    ⟨path.deletions, path.deletions_nodup, path.deletions_length, path.deletions_mem⟩)
  constructor
  · intro first second eq
    exact Schedule.deletions_injective (congrArg Subtype.val eq)
  · rintro ⟨xs, nodup, length, inside⟩
    subst d
    obtain ⟨path, eq⟩ := exists_schedule_of_deletions C xs nodup inside short
    exact ⟨path, Subtype.ext eq⟩

/-- Lemma 5.1 for the concrete record-only cyclic contraction system.
The last rank-two contraction retains its ordered parents. -/
noncomputable def admissibleLogsEquivBoundaryDeletions (C : MarkedCircle α) (d : ℕ)
    (short : d < C.rank) : AdmissibleLogs C d ≃ BoundaryDeletions C d :=
  (admissibleLogsEquivSchedule C d).trans (scheduleEquivBoundaryDeletions C d short)

noncomputable def boundaryDeletionsEquivEmbedding (C : MarkedCircle α) (d : ℕ) :
    BoundaryDeletions C d ≃ (Fin d ↪ C.boundaries) := by
  let encode : BoundaryDeletions C d → (Fin d ↪ C.boundaries) := fun xs =>
    { toFun := fun i => ⟨xs.val.get (Fin.cast xs.property.2.1.symm i),
        xs.property.2.2 _ (List.get_mem _ _)⟩
      inj' := by
        intro i j same
        have eq := (List.nodup_iff_injective_get.mp xs.property.1) (congrArg Subtype.val same)
        exact Fin.ext (congrArg (fun k : Fin xs.val.length => k.val) eq) }
  apply Equiv.ofBijective encode
  constructor
  · intro xs ys same
    apply Subtype.ext
    apply List.ext_get
    · exact xs.property.2.1.trans ys.property.2.1.symm
    · intro i hi hj
      have eq := congrArg (fun e : Fin d ↪ C.boundaries => (e ⟨i, by omega⟩).val) same
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
    have inside : ∀ a ∈ xs, a ∈ C.boundaries := by
      intro a member
      obtain ⟨i, rfl⟩ := List.mem_ofFn.mp member
      exact (f i).property
    refine ⟨⟨xs, nodup, by simp [xs], inside⟩, ?_⟩
    apply Function.Embedding.ext
    intro i
    apply Subtype.ext
    simp [encode, xs]

noncomputable def admissibleLogsEquivEmbedding (C : MarkedCircle α) (d : ℕ)
    (short : d < C.rank) : AdmissibleLogs C d ≃ (Fin d ↪ C.boundaries) :=
  (admissibleLogsEquivBoundaryDeletions C d short).trans (boundaryDeletionsEquivEmbedding C d)

noncomputable instance admissibleLogsFintype (C : MarkedCircle α) (d : ℕ) :
    Fintype (AdmissibleLogs C d) := by
  classical
  by_cases short : d < C.rank
  · exact Fintype.ofEquiv (Fin d ↪ C.boundaries) (admissibleLogsEquivEmbedding C d short).symm
  · have empty : IsEmpty (AdmissibleLogs C d) := ⟨by
      rintro ⟨events, run, length⟩
      obtain ⟨path, eq⟩ := run.exists_schedule
      have nodup := path.deletions_nodup
      have bound := (Finset.card_le_card (show path.deletions.toFinset ⊆ C.boundaries from
        fun a member => path.deletions_mem a (List.mem_toFinset.mp member)))
      rw [List.toFinset_card_of_nodup nodup, path.deletions_length, length,
        C.card_boundaries] at bound
      have positive : d < C.rank := by
        have terminal : ∀ {E : MarkedCircle α} {k : ℕ}, Schedule E k → k < E.rank := by
          intro E k p
          induction p with
          | stop E => exact E.rank_pos
          | @step E k hr i tail ih =>
              have := E.rank_contract i hr
              omega
        simpa [length] using terminal path
      exact short positive⟩
    exact Fintype.ofIsEmpty

theorem card_admissibleLogs (C : MarkedCircle α) (d : ℕ) (short : d < C.rank) :
    Fintype.card (AdmissibleLogs C d) = C.rank.descFactorial d := by
  rw [Fintype.card_congr (admissibleLogsEquivEmbedding C d short),
    Fintype.card_embedding_eq]
  simp [C.card_boundaries]

theorem card_admissibleLogs_rank (C : MarkedCircle α) (s : ℕ)
    (positive : 1 ≤ s) (le : s ≤ C.rank) :
    Fintype.card (AdmissibleLogs C (C.rank - s)) = C.rank.factorial / s.factorial := by
  rw [card_admissibleLogs C _ (by omega), Nat.descFactorial_eq_div (by omega)]
  congr 2
  omega

end FusionLogEnumeration
