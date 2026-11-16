import RSR2.SingletonWordSymmetry

/-!
# Tight port budgets force an elevator skeleton

The lower budget counts both rotations and defects. In particular this
module does not assume that an optimal word contains no lower defects.
The two physical port credits force exactly one lower control letter and
one upper rotation between successive elevators, with no prefix or tail.
-/

namespace RSR2.Parametric

def lowerControlCount (word : List Letter) : Nat :=
  lowerRotationCount word + lowerDefectCount word

private theorem vc_cons (a : Letter) (w : List Letter) :
    verticalCount (a :: w) = verticalCount w + (if a = .v then 1 else 0) := by
  simp [verticalCount, List.count_cons]

private theorem lc_cons (a : Letter) (w : List Letter) :
    lowerControlCount (a :: w) = lowerControlCount w +
      (if a = .p false ∨ a = .d false then 1 else 0) := by
  cases a with
  | p l => cases l <;> simp [lowerControlCount, lowerRotationCount, lowerDefectCount] <;> omega
  | d l => cases l <;> simp [lowerControlCount, lowerRotationCount, lowerDefectCount] <;> omega
  | v => simp [lowerControlCount, lowerRotationCount, lowerDefectCount]

private theorem uc_cons (a : Letter) (w : List Letter) :
    rawUpperRotationCount (a :: w) = rawUpperRotationCount w +
      (if a = .p true then 1 else 0) := by
  simp [rawUpperRotationCount, List.count_cons]

private theorem ud_cons (a : Letter) (w : List Letter) :
    rawUpperDefectCount (a :: w) = rawUpperDefectCount w +
      (if a = .d true then 1 else 0) := by
  simp [rawUpperDefectCount, List.count_cons]

theorem singleton_optimal_letter_counts (n : Nat) (hn : 1 < n)
    (word : List Letter)
    (hrun : run n hn (seed n) word =
      some (upperSingletonEndpoint n (by omega)))
    (hlen : word.length = 3 * n - 2) :
    verticalCount word = n ∧ rawUpperRotationCount word = n - 1 ∧
      rawUpperDefectCount word = 0 ∧ lowerControlCount word = n - 1 := by
  have hu : ∀ a, (upperSingletonEndpoint n (by omega) a).1 = true := by intro a; rfl
  have hi := upperSingletonEndpoint_injective n (by omega)
  have hc := singleton_run_allUpper_singletons_cost_lower_bound n hn _ word hrun hu hi
  have hr := singleton_run_allUpper_singletons_rotation_lower_bound n hn _ word hrun hu hi
  have hs := word_length_eq_lowerPortCost_add_upper word
  simp only [lowerPortCost, lowerControlCount] at *
  omega

theorem run_lowerControlCredit_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) :
    lowerSyncCredit n (by omega) Q + verticalCount word ≤
      lowerSyncCredit n (by omega) P + lowerControlCount word := by
  obtain ⟨f, z, hl, _, hd⟩ := run_exists_lowerPacketLedger n hn P Q word hrun
  have hb := runWithLowerPacketLedger_refill_bound n hn P Q word f z hl
  simp only [lowerControlCount]
  omega

private theorem lowerSyncCredit_le_one' (n : Nat) (hn : 0 < n) (P : Placement n) :
    lowerSyncCredit n hn P ≤ 1 := by
  classical
  unfold lowerSyncCredit
  split <;> omega

/-- A two-credit automaton derived from successful physical execution.
Both credits must be present to transfer; each other allowed letter
replenishes exactly its own previously absent credit. -/
inductive TightPortSchedule : Nat → Nat → List Letter → Prop
  | done : TightPortSchedule 0 0 []
  | elevator : TightPortSchedule 0 0 word → TightPortSchedule 1 1 (.v :: word)
  | lowerRotation : TightPortSchedule 1 u word →
      TightPortSchedule 0 u (.p false :: word)
  | lowerDefect : TightPortSchedule 1 u word →
      TightPortSchedule 0 u (.d false :: word)
  | upperRotation : TightPortSchedule l 1 word →
      TightPortSchedule l 0 (.p true :: word)

/-- Equality in the two whole-history budgets forces equality at every
physical step. This is not an assumption about a preselected loading plan. -/
theorem tightPortSchedule_of_run (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q)
    (hl : verticalCount word = lowerControlCount word + lowerSyncCredit n (by omega) P)
    (hu : verticalCount word = rawUpperRotationCount word + upperPortVacancy n (by omega) P)
    (hd : rawUpperDefectCount word = 0) :
    TightPortSchedule (lowerSyncCredit n (by omega) P)
      (upperPortVacancy n (by omega) P) word := by
  induction word generalizing P with
  | nil =>
      have hpl : lowerSyncCredit n (by omega) P = 0 := by
        simp [verticalCount, lowerControlCount, lowerRotationCount, lowerDefectCount] at hl
        exact hl.symm
      have hpu : upperPortVacancy n (by omega) P = 0 := by
        simpa [verticalCount, rawUpperRotationCount] using hu.symm
      rw [hpl, hpu]
      exact .done
  | cons a rest ih =>
      cases hs : step n hn P a with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          have hone : run n hn P [a] = some R := by simp [run, hs]
          have hsl0 := run_lowerControlCredit_bound n hn P R [a] hone
          have hsu0 := run_upperPortVacancy_bound n hn P R [a] hone
          have hsl : lowerSyncCredit n (by omega) R + (if a = .v then 1 else 0) ≤
              lowerSyncCredit n (by omega) P +
                (if a = .p false ∨ a = .d false then 1 else 0) := by
            cases a with
            | p l => cases l <;> simpa [lowerControlCount, lowerRotationCount,
                lowerDefectCount, verticalCount] using hsl0
            | d l => cases l <;> simpa [lowerControlCount, lowerRotationCount,
                lowerDefectCount, verticalCount] using hsl0
            | v => simpa [lowerControlCount, lowerRotationCount,
                lowerDefectCount, verticalCount] using hsl0
          have hsu : upperPortVacancy n (by omega) R + (if a = .v then 1 else 0) ≤
              upperPortVacancy n (by omega) P + (if a = .p true then 1 else 0) := by
            cases a with
            | p l => cases l <;> simpa [rawUpperRotationCount, verticalCount] using hsu0
            | d l => cases l <;> simpa [rawUpperRotationCount, verticalCount] using hsu0
            | v => simpa [rawUpperRotationCount, verticalCount] using hsu0
          have htl := run_lowerControlCredit_bound n hn R Q rest ht
          have htu := run_upperPortVacancy_bound n hn R Q rest ht
          have hpl := lowerSyncCredit_le_one' n (by omega) P
          have hrl := lowerSyncCredit_le_one' n (by omega) R
          have hpu := upperPortVacancy_le_one n (by omega) P
          have hru := upperPortVacancy_le_one n (by omega) R
          simp only [vc_cons, lc_cons, uc_cons, ud_cons] at hl hu hd
          have htail_l : verticalCount rest =
              lowerControlCount rest + lowerSyncCredit n (by omega) R := by
            omega
          have htail_u : verticalCount rest =
              rawUpperRotationCount rest + upperPortVacancy n (by omega) R := by
            omega
          have htail_d : rawUpperDefectCount rest = 0 := by
            omega
          have htail := ih R ht htail_l htail_u htail_d
          cases a with
          | p layer =>
              cases layer with
              | false =>
                  have hp : lowerSyncCredit n (by omega) P = 0 := by
                    simp at hl hsl
                    omega
                  have hr : lowerSyncCredit n (by omega) R = 1 := by
                    simp at hl hsl
                    omega
                  have he : upperPortVacancy n (by omega) P =
                      upperPortVacancy n (by omega) R := by
                    simp at hu
                    omega
                  rw [hp, he]
                  rw [hr] at htail
                  exact .lowerRotation htail
              | true =>
                  have hp : upperPortVacancy n (by omega) P = 0 := by
                    simp at hu hsu
                    omega
                  have hr : upperPortVacancy n (by omega) R = 1 := by
                    simp at hu hsu
                    omega
                  have he : lowerSyncCredit n (by omega) P =
                      lowerSyncCredit n (by omega) R := by
                    simp at hl
                    omega
                  rw [hp, he]
                  rw [hr] at htail
                  exact .upperRotation htail
          | d layer =>
              cases layer with
              | false =>
                  have hp : lowerSyncCredit n (by omega) P = 0 := by
                    simp at hl hsl
                    omega
                  have hr : lowerSyncCredit n (by omega) R = 1 := by
                    simp at hl hsl
                    omega
                  have he : upperPortVacancy n (by omega) P =
                      upperPortVacancy n (by omega) R := by
                    simp at hu
                    omega
                  rw [hp, he]
                  rw [hr] at htail
                  exact .lowerDefect htail
              | true => simp at hd
          | v =>
              have hcredits : lowerSyncCredit n (by omega) P = 1 ∧
                  upperPortVacancy n (by omega) P = 1 ∧
                  lowerSyncCredit n (by omega) R = 0 ∧
                  upperPortVacancy n (by omega) R = 0 := by
                simp at hl hsl hu hsu
                omega
              rw [hcredits.1, hcredits.2.1]
              rw [hcredits.2.2.1, hcredits.2.2.2] at htail
              exact .elevator htail

/-- The Boolean says whether the lower control is a defect, not a rotation. -/
def singletonLowerChoice (defect : Bool) : Letter := if defect then .d false else .p false

def singletonControlRound (choice : Bool × Bool) : List Letter :=
  if choice.2 then [.p true, singletonLowerChoice choice.1, .v]
  else [singletonLowerChoice choice.1, .p true, .v]

def singletonControlTail (choices : List (Bool × Bool)) : List Letter :=
  choices.flatMap singletonControlRound

theorem tightPortSchedule_tail_skeleton {word : List Letter}
    (h : TightPortSchedule 0 0 word) :
    ∃ choices, word = singletonControlTail choices := by
  suffices ∀ k (w : List Letter), w.length ≤ k → TightPortSchedule 0 0 w →
      ∃ choices, w = singletonControlTail choices from this word.length word (by omega) h
  intro k
  induction k with
  | zero =>
      intro w hw _
      have : w = [] := List.eq_nil_of_length_eq_zero (by omega)
      exact ⟨[], this⟩
  | succ k ih =>
      intro w hw h
      cases h with
      | done => exact ⟨[], rfl⟩
      | lowerRotation h =>
          cases h with
          | upperRotation h =>
              cases h with
              | elevator h =>
                  obtain ⟨choices, he⟩ := ih _ (by simp at hw; omega) h
                  exact ⟨(false, false) :: choices, by rw [he]; simp [singletonControlTail,
                    singletonControlRound, singletonLowerChoice]⟩
      | lowerDefect h =>
          cases h with
          | upperRotation h =>
              cases h with
              | elevator h =>
                  obtain ⟨choices, he⟩ := ih _ (by simp at hw; omega) h
                  exact ⟨(true, false) :: choices, by rw [he]; simp [singletonControlTail,
                    singletonControlRound, singletonLowerChoice]⟩
      | upperRotation h =>
          cases h with
          | lowerRotation h =>
              cases h with
              | elevator h =>
                  obtain ⟨choices, he⟩ := ih _ (by simp at hw; omega) h
                  exact ⟨(false, true) :: choices, by rw [he]; simp [singletonControlTail,
                    singletonControlRound, singletonLowerChoice]⟩
          | lowerDefect h =>
              cases h with
              | elevator h =>
                  obtain ⟨choices, he⟩ := ih _ (by simp at hw; omega) h
                  exact ⟨(true, true) :: choices, by rw [he]; simp [singletonControlTail,
                    singletonControlRound, singletonLowerChoice]⟩

theorem singletonControlTail_verticalCount (choices : List (Bool × Bool)) :
    verticalCount (singletonControlTail choices) = choices.length := by
  induction choices with
  | nil => rfl
  | cons c cs ih =>
      rcases c with ⟨defect, swap⟩
      cases defect <;> cases swap <;>
        simpa [singletonControlTail, singletonControlRound, singletonLowerChoice,
          verticalCount, List.count_append] using congrArg Nat.succ ih

/-- Every optimal singleton realization has exactly the proposed skeleton.
There is no extra prefix or suffix, and every inter-elevator interval has
exactly one lower control letter and one upper rotation. -/
theorem singleton_optimal_elevator_skeleton (n : Nat) (hn : 1 < n)
    (word : List Letter)
    (hrun : run n hn (seed n) word =
      some (upperSingletonEndpoint n (by omega)))
    (hlen : word.length = 3 * n - 2) :
    ∃ choices : List (Bool × Bool), choices.length = n - 1 ∧
      word = .v :: singletonControlTail choices := by
  have hc := singleton_optimal_letter_counts n hn word hrun hlen
  have hl : lowerSyncCredit n (by omega) (seed n) = 1 := by
    have ho : occupiedAt (seed n) false (site0 n (by omega)) := ⟨site0 n (by omega), rfl⟩
    simp [lowerSyncCredit, ho]
  have ht := tightPortSchedule_of_run n hn (seed n) _ word hrun
    (by rw [hc.1, hc.2.2.2, hl]; omega)
    (by rw [hc.1, hc.2.1, seed_upperPortVacancy]; omega) hc.2.2.1
  rw [hl, seed_upperPortVacancy] at ht
  cases ht with
  | elevator ht =>
      obtain ⟨choices, rfl⟩ := tightPortSchedule_tail_skeleton ht
      refine ⟨choices, ?_, rfl⟩
      have hv := singletonControlTail_verticalCount choices
      change List.count .v (singletonControlTail choices) = choices.length at hv
      simp [verticalCount] at hc
      omega

end RSR2.Parametric
