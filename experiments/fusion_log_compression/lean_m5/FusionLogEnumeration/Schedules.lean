import FusionLogEnumeration.Contraction

namespace FusionLogEnumeration

open RegisteredAbsorptionChains

variable {α : Type*} [DecidableEq α]

/-- A path of genuine cyclic-neighbour contractions. Its literal complete
records are read separately below; boundary labels are not part of a record. -/
inductive Schedule : MarkedCircle α → ℕ → Type _
  | stop (C) : Schedule C 0
  | step {C d} (hr : 2 ≤ C.rank) (i : Fin C.rank)
      (tail : Schedule (C.contract i hr) d) : Schedule C (d + 1)

namespace Schedule

def records {C : MarkedCircle α} {d : ℕ} : Schedule C d → List (FusionRecord α)
  | .stop _ => []
  | .step hr i tail => C.event i hr :: tail.records

def deletions {C : MarkedCircle α} {d : ℕ} : Schedule C d → List α
  | .stop _ => []
  | .step hr i tail => C.deleted i hr :: tail.deletions

@[simp] theorem records_length {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    path.records.length = d := by induction path <;> simp_all [records]

@[simp] theorem deletions_length {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    path.deletions.length = d := by induction path <;> simp_all [deletions]

theorem deletions_mem {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    ∀ a ∈ path.deletions, a ∈ C.boundaries := by
  induction path with
  | stop C => simp [deletions]
  | @step C d hr i tail ih =>
      intro a member
      simp only [deletions, List.mem_cons] at member
      rcases member with rfl | member
      · exact C.deleted_mem i hr
      · have hm := ih a member
        rw [C.boundaries_contract i hr] at hm
        exact Finset.mem_of_mem_erase hm

theorem deletions_nodup {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    path.deletions.Nodup := by
  induction path with
  | stop C => simp [deletions]
  | @step C d hr i tail ih =>
      rw [deletions, List.nodup_cons]
      refine ⟨?_, ih⟩
      intro member
      have hm := tail.deletions_mem _ member
      rw [C.boundaries_contract i hr] at hm
      exact (Finset.mem_erase.mp hm).1 rfl

theorem deletions_injective {C : MarkedCircle α} {d : ℕ} :
    Function.Injective (fun path : Schedule C d => path.deletions) := by
  intro first
  induction first with
  | stop C => intro second same; cases second; rfl
  | @step C d hr i tail ih =>
      intro second same
      cases second with
      | step hs j other =>
          have eqs := List.cons.inj same
          have ij := C.deleted_injective hr eqs.1
          subst j
          have hrs : hr = hs := Subsingleton.elim _ _
          subst hs
          have tails := ih eqs.2
          subst other
          rfl

theorem records_injective {C : MarkedCircle α} {d : ℕ} :
    Function.Injective (fun path : Schedule C d => path.records) := by
  intro first
  induction first with
  | stop C => intro second same; cases second; rfl
  | @step C d hr i tail ih =>
      intro second same
      cases second with
      | step hs j other =>
          have eqs := List.cons.inj same
          have ij := C.event_injective hr eqs.1
          subst j
          have hrs : hr = hs := Subsingleton.elim _ _
          subst hs
          have tails := ih eqs.2
          subst other
          rfl

end Schedule

/-- Record-only local admissibility, independent of any chosen deletion list
or actual execution word. The constructor contracts neighbouring packets. -/
inductive LogRun : MarkedCircle α → List (FusionRecord α) → Prop
  | nil (C) : LogRun C []
  | cons {C rest} (hr : 2 ≤ C.rank) (i : Fin C.rank)
      (tail : LogRun (C.contract i hr) rest) : LogRun C (C.event i hr :: rest)

theorem Schedule.logRun {C : MarkedCircle α} {d : ℕ} (path : Schedule C d) :
    LogRun C path.records := by
  induction path with
  | stop C => exact .nil C
  | step hr i _ ih => exact .cons hr i ih

theorem LogRun.exists_schedule {C : MarkedCircle α} {events : List (FusionRecord α)}
    (run : LogRun C events) : ∃ path : Schedule C events.length, path.records = events := by
  induction run with
  | nil C => exact ⟨.stop C, rfl⟩
  | cons hr i tail ih =>
      obtain ⟨path, eq⟩ := ih
      exact ⟨.step hr i path, by simp [Schedule.records, eq]⟩

abbrev AdmissibleLogs (C : MarkedCircle α) (d : ℕ) :=
  {events : List (FusionRecord α) // LogRun C events ∧ events.length = d}

noncomputable def admissibleLogsEquivSchedule (C : MarkedCircle α) (d : ℕ) :
    AdmissibleLogs C d ≃ Schedule C d := by
  refine (Equiv.ofBijective
    (fun path : Schedule C d => (⟨path.records, path.logRun, path.records_length⟩ : AdmissibleLogs C d))
    ⟨?_, ?_⟩).symm
  · intro first second eq
    exact Schedule.records_injective (congrArg Subtype.val eq)
  · rintro ⟨events, valid, length⟩
    subst d
    obtain ⟨path, eq⟩ := valid.exists_schedule
    exact ⟨path, Subtype.ext eq⟩

end FusionLogEnumeration
