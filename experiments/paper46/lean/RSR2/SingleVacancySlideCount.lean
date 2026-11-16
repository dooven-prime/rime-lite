import RSR2.SingleVacancyOptimality

/-!
# Productive vacancy resets in the same actual execution

This observer charges a lower defect only when port 0 is empty and port 1
is occupied before the step. Failed elevators still fail. Its endpoint
projection is exactly `run`, not a separate vacancy rewrite system.
-/

namespace RSR2.Parametric

noncomputable def vacancySlideCharge (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) : Nat := by
  classical
  exact if letter = .d false ∧ ¬ occupiedAt P false (site0 n (by omega)) ∧
      occupiedAt P false (site1 n hn) then 1 else 0

noncomputable def runWithVacancySlides (n : Nat) (hn : 1 < n) :
    Placement n → List Letter → Option (Placement n × Nat)
  | P, [] => some (P, 0)
  | P, letter :: rest => (step n hn P letter).bind (fun R =>
      (runWithVacancySlides n hn R rest).map (fun result =>
        (result.1, vacancySlideCharge n hn P letter + result.2)))

theorem vacancySlideCharge_eq_payment (n : Nat) (hn : 1 < n)
    (P : Placement n) (rep : SingleVacancyRep n hn P) (letter : Letter) :
    vacancySlideCharge n hn P letter = rep.slidePayment letter := by
  classical
  cases rep with
  | full lower occupied adjacent =>
      simp [vacancySlideCharge, occupied, SingleVacancyRep.slidePayment]
  | deleted hole missing upper lower =>
      by_cases hz : hole.val = 0
      · have hh : hole = site0 n (by omega) := Fin.ext hz
        have h10 : site1 n hn ≠ site0 n (by omega) := by
          simp [site0, site1, Fin.mk.injEq]
        have hempty : ¬ occupiedAt P false (site0 n (by omega)) := by
          rw [missing]
          simp [hh]
        have hocc : occupiedAt P false (site1 n hn) :=
          (missing _).mpr (fun he => h10 (he.trans hh))
        simp [vacancySlideCharge, SingleVacancyRep.slidePayment, hempty, hocc, hz]
      · have h0 : site0 n (by omega) ≠ hole := by
          intro he; exact hz (congrArg Fin.val he.symm)
        simp [vacancySlideCharge, SingleVacancyRep.slidePayment, missing, h0, hz]

theorem runWithVacancySlides_project (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runWithVacancySlides n hn P word).map Prod.fst = run n hn P word := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithVacancySlides, run, hs]
      | some R =>
          simp only [runWithVacancySlides, hs, Option.bind_some, Option.map_map,
            Function.comp_def, run]
          exact ih R

theorem run_exists_vacancySlides (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (hrun : run n hn P word = some Q) :
    ∃ D, runWithVacancySlides n hn P word = some (Q, D) := by
  have hp := runWithVacancySlides_project n hn P word
  rw [hrun] at hp
  cases he : runWithVacancySlides n hn P word with
  | none => simp [he] at hp
  | some result =>
      have hq : result.1 = Q := by simpa [he] using hp
      exact ⟨result.2, congrArg some (Prod.ext hq rfl)⟩

theorem runWithVacancySlides_le_defects (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (D : Nat)
    (hrun : runWithVacancySlides n hn P word = some (Q, D)) :
    D ≤ lowerDefectCount word := by
  classical
  induction word generalizing P D with
  | nil => simp [runWithVacancySlides] at hrun; simp [← hrun.2, lowerDefectCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithVacancySlides, hs] at hrun
      | some R =>
          cases ht : runWithVacancySlides n hn R rest with
          | none => simp [runWithVacancySlides, hs, ht] at hrun
          | some result =>
              have he : result.1 = Q ∧ vacancySlideCharge n hn P letter + result.2 = D := by
                simpa [runWithVacancySlides, hs, ht] using hrun
              have htail : runWithVacancySlides n hn R rest = some (Q, result.2) := by
                rw [ht]
                exact congrArg some (Prod.ext he.1 rfl)
              have hb := ih R result.2 htail
              have hc : vacancySlideCharge n hn P letter ≤
                  (if letter = .d false then 1 else 0) := by
                unfold vacancySlideCharge
                split <;> split <;> simp_all
              have hcount : lowerDefectCount (letter :: rest) =
                  lowerDefectCount rest + (if letter = .d false then 1 else 0) := by
                simp [lowerDefectCount, List.count_cons]
              rw [hcount]
              omega

/-- Slide debt and transfer balance are obtained along the original steps.
There is no prior choice of event times or a canonical intermediate layout. -/
theorem singleVacancyRep_run_counters (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (D : Nat)
    (rep : SingleVacancyRep n hn P)
    (hrun : runWithVacancySlides n hn P word = some (Q, D))
    (hi : Function.Injective Q)
    (hk : ∀ a, a ≠ site1 n hn → (Q a).1 = false) :
    ∃ finalRep : SingleVacancyRep n hn Q,
      rep.slidesRemaining ≤ D + finalRep.slidesRemaining ∧
      rep.transferRemaining = verticalCount word + finalRep.transferRemaining := by
  induction word generalizing P D with
  | nil =>
      have he : P = Q ∧ 0 = D := by simpa [runWithVacancySlides] using hrun
      obtain ⟨rfl, rfl⟩ := he
      exact ⟨rep, by simp [verticalCount]⟩
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithVacancySlides, hs] at hrun
      | some R =>
          cases ht : runWithVacancySlides n hn R rest with
          | none => simp [runWithVacancySlides, hs, ht] at hrun
          | some result =>
              have he : result.1 = Q ∧ vacancySlideCharge n hn P letter + result.2 = D := by
                simpa [runWithVacancySlides, hs, ht] using hrun
              have htail : runWithVacancySlides n hn R rest = some (Q, result.2) := by
                rw [ht]
                exact congrArg some (Prod.ext he.1 rfl)
              have htRun : run n hn R rest = some Q := by
                rw [← runWithVacancySlides_project, htail]
                rfl
              have hiR := run_injective_of_terminal n hn R Q rest htRun hi
              have hkR : ∀ a, a ≠ site1 n hn → (R a).1 = false := by
                intro a ha
                exact run_lower_of_terminal_lower n hn R Q rest a htRun (hk a ha)
              obtain ⟨nextRep, _, hd, hv⟩ :=
                singleVacancyRep_step_payments n hn P R letter rep hs hiR hkR
              obtain ⟨finalRep, hdt, hvt⟩ := ih R result.2 nextRep htail
              have hc := vacancySlideCharge_eq_payment n hn P rep letter
              have hcount : verticalCount (letter :: rest) =
                  verticalCount rest + (if letter = .v then 1 else 0) := by
                simp [verticalCount, List.count_cons]
              refine ⟨finalRep, ?_, ?_⟩
              · omega
              · rw [hcount]; omega

theorem singleVacancyTerminal_slide_and_transfer_counts (n : Nat) (hn : 3 ≤ n)
    (Q : Placement n) (word : List Letter) (D : Nat)
    (hrun : runWithVacancySlides n (by omega) (seed n) word = some (Q, D))
    (terminal : SingleVacancyTerminal n (by omega) Q) :
    n - 2 ≤ D ∧ D ≤ lowerDefectCount word ∧ verticalCount word = 1 := by
  obtain ⟨finalRep, hd, hv⟩ := singleVacancyRep_run_counters n (by omega) (seed n)
    Q word D (singleton_singleVacancyRep n (by omega)) hrun terminal.injective terminal.lower
  obtain ⟨hds, hvs⟩ := singleVacancyTerminal_remaining_zero n (by omega) Q terminal finalRep
  have hs0 : (singleton_singleVacancyRep n (by omega)).slidesRemaining = n - 2 := rfl
  have hv0 : (singleton_singleVacancyRep n (by omega)).transferRemaining = 1 := rfl
  rw [hds, Nat.add_zero, hs0] at hd
  rw [hvs, Nat.add_zero, hv0] at hv
  exact ⟨hd, runWithVacancySlides_le_defects n (by omega) (seed n) Q word D hrun, hv.symm⟩

theorem singleVacancyEndpoint_defect_and_vertical_bounds (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega))) :
    n - 2 ≤ lowerDefectCount word ∧ verticalCount word = 1 := by
  obtain ⟨D, hD⟩ := run_exists_vacancySlides n (by omega) _ _ word hrun
  obtain ⟨hd, hle, hv⟩ := singleVacancyTerminal_slide_and_transfer_counts n hn
    _ word D hD (singleVacancyEndpoint_terminal n (by omega))
  exact ⟨Nat.le_trans hd hle, hv⟩

theorem singleVacancyWord_defect_and_vertical_counts (n : Nat) :
    lowerDefectCount (singleVacancyWord n) = n - 2 ∧
      verticalCount (singleVacancyWord n) = 1 := by
  have hc : ∀ k, lowerDefectCount
      (List.replicate k (singleVacancyCycleWord n)).flatten = k ∧
      verticalCount (List.replicate k (singleVacancyCycleWord n)).flatten = 0 := by
    intro k
    induction k with
    | zero => simp [lowerDefectCount, verticalCount]
    | succ k ih =>
        rw [List.replicate_succ, List.flatten_cons]
        simp only [lowerDefectCount, verticalCount, List.count_append] at ih ⊢
        rw [ih.1, ih.2]
        simp [singleVacancyCycleWord, List.count_replicate, Nat.add_comm]
  have he := hc (n - 2)
  simp only [lowerDefectCount, verticalCount] at he
  simp [singleVacancyWord, lowerDefectCount, verticalCount, he, List.count_replicate]

theorem singleVacancyEndpoint_minimal_letter_counts (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega))) (hlen : word.length = n * (n - 1)) :
    lowerRotationCount word = (n - 1) * (n - 1) ∧
    lowerDefectCount word = n - 2 ∧ verticalCount word = 1 ∧
    rawUpperRotationCount word = 0 ∧ rawUpperDefectCount word = 0 := by
  rw [singleVacancyEndpoint_minimal_word_unique n hn word hrun hlen]
  obtain ⟨hd, hv⟩ := singleVacancyWord_defect_and_vertical_counts n
  obtain ⟨hp1, hd1⟩ := singleVacancyWord_upper_counts n
  exact ⟨singleVacancyWord_rotationCount n, hd, hv, hp1, hd1⟩

theorem singleVacancyEndpoint_minimal_productive_slides (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (D : Nat)
    (hrun : runWithVacancySlides n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega), D))
    (hlen : word.length = n * (n - 1)) : D = n - 2 := by
  have hr : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega)) := by
    rw [← runWithVacancySlides_project, hrun]
    rfl
  obtain ⟨_, hd, _, _, _⟩ := singleVacancyEndpoint_minimal_letter_counts n hn word hr hlen
  obtain ⟨hlo, hhi, _⟩ := singleVacancyTerminal_slide_and_transfer_counts n hn _ word D
    hrun (singleVacancyEndpoint_terminal n (by omega))
  omega

end RSR2.Parametric
