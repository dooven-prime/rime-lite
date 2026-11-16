import RSR2.SingleVacancyWitness

/-!
# Exact cost and rigidity of the one-vacancy endpoint

The three payments are lower rotations, productive vacancy slides, and the
sole elevator.  A tight execution must pay at every letter.  Its next letter
is then forced by the actual vacancy (or the still-untransferred atom 1).
All bounds quantify over the original guarded executor.
-/

namespace RSR2.Parametric

def SingleVacancyRep.work {n : Nat} {hn : 1 < n} {P : Placement n}
    (rep : SingleVacancyRep n hn P) : Nat :=
  rep.debt + rep.slidesRemaining + rep.transferRemaining

def SingleVacancyRep.payment {n : Nat} {hn : 1 < n} {P : Placement n}
    (rep : SingleVacancyRep n hn P) (letter : Letter) : Nat :=
  rep.rotationPayment letter + rep.slidePayment letter +
    (if letter = .v then 1 else 0)

def SingleVacancyRep.nextLetter {n : Nat} {hn : 1 < n} {P : Placement n} :
    SingleVacancyRep n hn P → Letter
  | .full _ _ _ => if (P (site1 n hn)).2.val = 0 then .v else .p false
  | .deleted h _ _ _ => if h.val = 0 then .d false else .p false

theorem SingleVacancyRep.payment_le_one {n : Nat} {hn : 1 < n}
    {P : Placement n} (rep : SingleVacancyRep n hn P) (letter : Letter) :
    rep.payment letter ≤ 1 := by
  cases rep <;> cases letter with
  | p layer => cases layer <;> simp [payment, rotationPayment, slidePayment] <;>
      split <;> omega
  | d layer => cases layer <;> simp [payment, rotationPayment, slidePayment] <;>
      split <;> omega
  | v => simp [payment, rotationPayment, slidePayment]

theorem singleVacancyRep_payment_forces_letter (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (rep : SingleVacancyRep n hn P)
    (hs : step n hn P letter = some Q)
    (hkeep : ∀ a, a ≠ site1 n hn → (Q a).1 = false)
    (hpaid : rep.payment letter = 1) : letter = rep.nextLetter := by
  cases rep with
  | full lower occupied adjacent =>
      cases letter with
      | p layer =>
          cases layer <;>
            simp_all [SingleVacancyRep.payment, SingleVacancyRep.rotationPayment,
              SingleVacancyRep.slidePayment, SingleVacancyRep.nextLetter]
      | d layer =>
          cases layer <;>
            simp_all [SingleVacancyRep.payment, SingleVacancyRep.rotationPayment,
              SingleVacancyRep.slidePayment]
      | v =>
          obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
          obtain ⟨a, ha⟩ := hg.1
          change P a = (false, site0 n (by omega)) at ha
          have ha1 : a = site1 n hn := by
            by_cases he : a = site1 n hn
            · exact he
            · have hk := hkeep a he
              simp [liftPacket, ha] at hk
          subst a
          simp [SingleVacancyRep.nextLetter, ha, site0]
  | deleted hole missing upper lower =>
      cases letter with
      | p layer =>
          cases layer <;>
            simp_all [SingleVacancyRep.payment, SingleVacancyRep.rotationPayment,
              SingleVacancyRep.slidePayment, SingleVacancyRep.nextLetter]
      | d layer =>
          cases layer <;>
            simp_all [SingleVacancyRep.payment, SingleVacancyRep.rotationPayment,
              SingleVacancyRep.slidePayment, SingleVacancyRep.nextLetter]
      | v =>
          obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
          obtain ⟨a, ha⟩ := hg.1
          change P a = (false, site0 n (by omega)) at ha
          have hne : a ≠ site1 n hn := by
            intro he; subst a
            have hl := congrArg Prod.fst ha
            simp [upper] at hl
          have hk := hkeep a hne
          simp [liftPacket, ha] at hk

theorem singleVacancyTerminal_remaining_zero (n : Nat) (hn : 1 < n)
    (Q : Placement n) (terminal : SingleVacancyTerminal n hn Q)
    (rep : SingleVacancyRep n hn Q) :
    rep.slidesRemaining = 0 ∧ rep.transferRemaining = 0 := by
  cases rep with
  | full lower _ _ =>
      have hl := lower (site1 n hn)
      simp [terminal.upper] at hl
  | deleted hole missing _ _ =>
      have hh : hole = site0 n (by omega) := by
        by_cases he : hole = site0 n (by omega)
        · exact he
        · exact False.elim (terminal.empty ((missing _).mpr (Ne.symm he)))
      subst hole
      simp only [SingleVacancyRep.slidesRemaining, SingleVacancyRep.transferRemaining]
      rw [terminal.anchor]
      simp [vacancyAnchorGap, site0, site1]

theorem singleVacancyTerminal_work_zero (n : Nat) (hn : 1 < n)
    (Q : Placement n) (terminal : SingleVacancyTerminal n hn Q)
    (rep : SingleVacancyRep n hn Q) : rep.work = 0 := by
  obtain ⟨hs, hv⟩ := singleVacancyTerminal_remaining_zero n hn Q terminal rep
  simp [SingleVacancyRep.work, hs, hv,
    singleVacancyTerminal_debt_zero n hn Q terminal rep]

theorem singleVacancyRep_work_step (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (rep : SingleVacancyRep n hn P)
    (hs : step n hn P letter = some Q) (hi : Function.Injective Q)
    (hk : ∀ a, a ≠ site1 n hn → (Q a).1 = false) :
    ∃ nextRep : SingleVacancyRep n hn Q,
      rep.work ≤ rep.payment letter + nextRep.work := by
  obtain ⟨nextRep, hr, hd, hv⟩ :=
    singleVacancyRep_step_payments n hn P Q letter rep hs hi hk
  refine ⟨nextRep, ?_⟩
  dsimp [SingleVacancyRep.work, SingleVacancyRep.payment]
  omega

/-- Arbitrary suffix bound from its actual current placement, not a canonical
intermediate state. -/
theorem singleVacancyRep_work_run (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (rep : SingleVacancyRep n hn P)
    (hrun : run n hn P word = some Q) (terminal : SingleVacancyTerminal n hn Q) :
    rep.work ≤ word.length := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      subst Q
      simp [singleVacancyTerminal_work_zero n hn P terminal rep]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          have hi := run_injective_of_terminal n hn R Q rest ht terminal.injective
          have hk : ∀ a, a ≠ site1 n hn → (R a).1 = false := by
            intro a ha
            exact run_lower_of_terminal_lower n hn R Q rest a ht (terminal.lower a ha)
          obtain ⟨nextRep, hb⟩ := singleVacancyRep_work_step n hn P R letter rep hs hi hk
          have hh := ih R nextRep ht
          have hc := rep.payment_le_one letter
          simp only [List.length_cons]
          omega

theorem singleVacancyRep_work_port_run (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (rep : SingleVacancyRep n hn P)
    (hrun : run n hn P word = some Q) (terminal : SingleVacancyTerminal n hn Q) :
    rep.work ≤ lowerPortCost word := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      subst Q
      simp [singleVacancyTerminal_work_zero n hn P terminal rep, lowerPortCost,
        lowerRotationCount, lowerDefectCount, verticalCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          have hi := run_injective_of_terminal n hn R Q rest ht terminal.injective
          have hk : ∀ a, a ≠ site1 n hn → (R a).1 = false := by
            intro a ha
            exact run_lower_of_terminal_lower n hn R Q rest a ht (terminal.lower a ha)
          obtain ⟨nextRep, hb⟩ := singleVacancyRep_work_step n hn P R letter rep hs hi hk
          have hh := ih R nextRep ht
          have hc := rep.payment_le_one letter
          cases letter with
          | p layer =>
              cases layer
              all_goals simp [lowerPortCost, lowerRotationCount, lowerDefectCount,
                verticalCount] at hh ⊢
              · omega
              · have he : rep.payment (.p true) = 0 := by
                  cases rep <;> simp [SingleVacancyRep.payment,
                    SingleVacancyRep.rotationPayment, SingleVacancyRep.slidePayment]
                omega
          | d layer =>
              cases layer
              all_goals simp [lowerPortCost, lowerRotationCount, lowerDefectCount,
                verticalCount] at hh ⊢
              · omega
              · have he : rep.payment (.d true) = 0 := by
                  cases rep <;> simp [SingleVacancyRep.payment,
                    SingleVacancyRep.rotationPayment, SingleVacancyRep.slidePayment]
                omega
          | v =>
              simp [lowerPortCost, lowerRotationCount, lowerDefectCount,
                verticalCount] at hh ⊢
              omega

theorem singleton_singleVacancyRep_work (n : Nat) (hn : 3 ≤ n) :
    (singleton_singleVacancyRep n (by omega)).work = n * (n - 1) := by
  change (n - 2) * (n - 1) + (n - 1) + (n - 2) + 1 = _
  have he : n - 2 + 1 = n - 1 := by omega
  calc
    _ = ((n - 2) + 1) * (n - 1) + (n - 1) := by
      rw [Nat.add_mul, Nat.one_mul]
      omega
    _ = n * (n - 1) := by
      rw [he]
      calc
        _ = (n - 1 + 1) * (n - 1) := by rw [Nat.add_mul, Nat.one_mul]
        _ = _ := by congr 1; omega

theorem singleVacancyEndpoint_length_lower_bound (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega))) : n * (n - 1) ≤ word.length := by
  have hb := singleVacancyRep_work_run n (by omega) (seed n) _ word
    (singleton_singleVacancyRep n (by omega)) hrun
    (singleVacancyEndpoint_terminal n (by omega))
  rwa [singleton_singleVacancyRep_work n hn] at hb

theorem singleVacancyEndpoint_port_lower_bound (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega))) :
    n * (n - 1) ≤ lowerPortCost word := by
  have hb := singleVacancyRep_work_port_run n (by omega) (seed n) _ word
    (singleton_singleVacancyRep n (by omega)) hrun
    (singleVacancyEndpoint_terminal n (by omega))
  rwa [singleton_singleVacancyRep_work n hn] at hb

/-- Equality forces payment at the head and leaves a tight actual suffix. -/
theorem singleVacancyRep_tight_head (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (rest : List Letter)
    (rep : SingleVacancyRep n hn P)
    (hrun : run n hn P (letter :: rest) = some Q)
    (terminal : SingleVacancyTerminal n hn Q)
    (hlen : (letter :: rest).length = rep.work) :
    ∃ R, ∃ nextRep : SingleVacancyRep n hn R,
      step n hn P letter = some R ∧ run n hn R rest = some Q ∧
      letter = rep.nextLetter ∧ rest.length = nextRep.work := by
  cases hs : step n hn P letter with
  | none => simp [run, hs] at hrun
  | some R =>
      have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
      have hi := run_injective_of_terminal n hn R Q rest ht terminal.injective
      have hk : ∀ a, a ≠ site1 n hn → (R a).1 = false := by
        intro a ha
        exact run_lower_of_terminal_lower n hn R Q rest a ht (terminal.lower a ha)
      obtain ⟨nextRep, hb⟩ := singleVacancyRep_work_step n hn P R letter rep hs hi hk
      have htbound := singleVacancyRep_work_run n hn R Q rest nextRep ht terminal
      have hc := rep.payment_le_one letter
      have hpaid : rep.payment letter = 1 := by simp only [List.length_cons] at hlen; omega
      have heq := singleVacancyRep_payment_forces_letter n hn P R letter rep hs hk hpaid
      refine ⟨R, nextRep, rfl, ht, heq, ?_⟩
      simp only [List.length_cons] at hlen
      omega

/-- Determinism of paid letters gives literal list equality, not equality
modulo commutation, phase, or a normalized trace. -/
theorem singleVacancyRep_tight_run_unique (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word other : List Letter) (rep : SingleVacancyRep n hn P)
    (hrun : run n hn P word = some Q) (hother : run n hn P other = some Q)
    (terminal : SingleVacancyTerminal n hn Q)
    (hlen : word.length = rep.work) (holength : other.length = rep.work) :
    word = other := by
  induction word generalizing P other with
  | nil =>
      have hz : other.length = 0 := by simp only [List.length_nil] at hlen; omega
      exact (List.length_eq_zero_iff.mp hz).symm
  | cons letter rest ih =>
      cases other with
      | nil => simp only [List.length_cons, List.length_nil] at hlen holength; omega
      | cons next tail =>
          obtain ⟨R, nextRep, hs, ht, hhead, htail⟩ :=
            singleVacancyRep_tight_head n hn P Q letter rest rep hrun terminal hlen
          obtain ⟨_, _, _, _, hnext, _⟩ :=
            singleVacancyRep_tight_head n hn P Q next tail rep hother terminal holength
          have he : next = letter := hnext.trans hhead.symm
          rw [he] at hother holength ⊢
          have hot : run n hn R tail = some Q := by simpa [run, hs] using hother
          have hol : tail.length = nextRep.work := by
            simp only [List.length_cons] at hlen holength
            omega
          exact congrArg (List.cons letter) (ih R tail nextRep ht hot htail hol)

theorem singleVacancyWord_length (n : Nat) (hn : 3 ≤ n) :
    (singleVacancyWord n).length = n * (n - 1) := by
  have hc : ∀ k, (List.replicate k (singleVacancyCycleWord n)).flatten.length = k * n := by
    intro k
    induction k with
    | zero => simp
    | succ k ih =>
        rw [List.replicate_succ, List.flatten_cons, List.length_append, ih]
        simp only [singleVacancyCycleWord, List.length_cons, List.length_replicate]
        rw [Nat.add_mul, Nat.one_mul]
        omega
  simp only [singleVacancyWord, List.length_append, List.length_replicate,
    List.length_singleton, hc]
  calc
    _ = (n - 2) * n + n := by omega
    _ = (n - 2 + 1) * n := by rw [Nat.add_mul, Nat.one_mul]
    _ = n * (n - 1) := by rw [show n - 2 + 1 = n - 1 by omega, Nat.mul_comm]

theorem singleVacancyWord_upper_counts (n : Nat) :
    rawUpperRotationCount (singleVacancyWord n) = 0 ∧
      rawUpperDefectCount (singleVacancyWord n) = 0 := by
  have hc : ∀ k, rawUpperRotationCount
      (List.replicate k (singleVacancyCycleWord n)).flatten = 0 ∧
      rawUpperDefectCount (List.replicate k (singleVacancyCycleWord n)).flatten = 0 := by
    intro k
    induction k with
    | zero => simp [rawUpperRotationCount, rawUpperDefectCount]
    | succ k ih =>
        rw [List.replicate_succ, List.flatten_cons]
        simp only [rawUpperRotationCount, rawUpperDefectCount, List.count_append] at ih ⊢
        rw [ih.1, ih.2]
        simp [singleVacancyCycleWord, List.count_replicate]
  have he := hc (n - 2)
  simp only [rawUpperRotationCount, rawUpperDefectCount] at he
  simp [singleVacancyWord, rawUpperRotationCount, rawUpperDefectCount, he,
    List.count_replicate]

theorem singleVacancyWord_portCost (n : Nat) (hn : 3 ≤ n) :
    lowerPortCost (singleVacancyWord n) = n * (n - 1) := by
  have he := word_length_eq_lowerPortCost_add_upper (singleVacancyWord n)
  obtain ⟨hp, hd⟩ := singleVacancyWord_upper_counts n
  rw [singleVacancyWord_length n hn, hp, hd] at he
  omega

theorem singleVacancyEndpoint_optimal (n : Nat) (hn : 3 ≤ n) :
    (∀ word, run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega)) →
        n * (n - 1) ≤ lowerPortCost word ∧ n * (n - 1) ≤ word.length) ∧
    run n (by omega) (seed n) (singleVacancyWord n) =
      some (singleVacancyEndpoint n (by omega)) ∧
    lowerPortCost (singleVacancyWord n) = n * (n - 1) ∧
      (singleVacancyWord n).length = n * (n - 1) :=
  ⟨fun word h => ⟨singleVacancyEndpoint_port_lower_bound n hn word h,
      singleVacancyEndpoint_length_lower_bound n hn word h⟩,
    singleVacancyWord_run n hn, singleVacancyWord_portCost n hn,
    singleVacancyWord_length n hn⟩

theorem singleVacancyEndpoint_minimal_word_unique (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega)))
    (hlen : word.length = n * (n - 1)) : word = singleVacancyWord n := by
  apply singleVacancyRep_tight_run_unique n (by omega) (seed n)
    (singleVacancyEndpoint n (by omega)) word (singleVacancyWord n)
    (singleton_singleVacancyRep n (by omega)) hrun (singleVacancyWord_run n hn)
    (singleVacancyEndpoint_terminal n (by omega))
  · rwa [singleton_singleVacancyRep_work n hn]
  · rw [singleVacancyWord_length n hn, singleton_singleVacancyRep_work n hn]

/-- Exact minimum and uniqueness for the specified literal endpoint. -/
theorem singleVacancyEndpoint_exists_unique_shortest (n : Nat) (hn : 3 ≤ n) :
    ∃ word : List Letter,
      (run n (by omega) (seed n) word = some (singleVacancyEndpoint n (by omega)) ∧
        word.length = n * (n - 1)) ∧
      ∀ other, (run n (by omega) (seed n) other =
        some (singleVacancyEndpoint n (by omega)) ∧ other.length = n * (n - 1)) →
        other = word := by
  refine ⟨singleVacancyWord n, ⟨singleVacancyWord_run n hn,
    singleVacancyWord_length n hn⟩, ?_⟩
  intro word hw
  exact singleVacancyEndpoint_minimal_word_unique n hn word hw.1 hw.2

end RSR2.Parametric
