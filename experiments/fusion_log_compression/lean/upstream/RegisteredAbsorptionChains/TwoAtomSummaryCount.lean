import RegisteredAbsorptionChains.TotalCountFormula
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

private instance : DecidableEq (FusionRecord (ZMod 2)) := by
  intro a b
  exact decidable_of_iff
    (a.left = b.left ∧ a.right = b.right ∧ a.result = b.result)
    (by cases a; cases b; simp [FusionRecord.mk.injEq])

private instance : DecidableEq (Execution 2 (ZMod 2)) := by
  intro a b
  exact decidable_of_iff
    (a.placed = b.placed ∧ a.origin = b.origin ∧ a.chain = b.chain)
    (by cases a; cases b; simp [Execution.mk.injEq])

private abbrev F₂ : Finset (ZMod 2) := selectedPair 2
private abbrev Seed₂ : Execution 2 (ZMod 2) := singletonExecution 2
private abbrev Pre₁ : Execution 2 (ZMod 2) := step F₂ Seed₂ .p
private abbrev Reg₀ : Execution 2 (ZMod 2) := step F₂ Seed₂ .d
private abbrev Reg₁ : Execution 2 (ZMod 2) := step F₂ Pre₁ .d
private abbrev Reg₀p : Execution 2 (ZMod 2) := step F₂ Reg₀ .p
private abbrev Reg₁p : Execution 2 (ZMod 2) := step F₂ Reg₁ .p

private theorem two_pre_rotates : step F₂ Pre₁ .p = Seed₂ := by
  decide

/-- Two pre-registration phases, then two origins at two physical phases. -/
private def twoState : Fin 6 → Execution 2 (ZMod 2) :=
  ![Seed₂, Pre₁, Reg₀, Reg₀p, Reg₁, Reg₁p]

private def twoNextP : Fin 6 → Fin 6 := ![1, 0, 3, 2, 5, 4]
private def twoNextD : Fin 6 → Fin 6 := ![2, 4, 2, 2, 4, 4]

private theorem twoState_step (i : Fin 6) (a : Letter) :
    step F₂ (twoState i) a =
      twoState (if a = .p then twoNextP i else twoNextD i) := by
  fin_cases i <;> cases a <;> decide

private theorem twoState_injective : Function.Injective twoState := by
  decide

private theorem twoState_registered (i : Fin 6) :
    (twoState i).origin.isSome = true ↔ 2 ≤ i.val := by
  fin_cases i <;> decide

private def twoWord : Fin 6 → List Letter :=
  ![[], [.p], [.d], [.d, .p], [.p, .d], [.p, .d, .p]]

private theorem twoState_word (i : Fin 6) :
    run F₂ Seed₂ (twoWord i) = twoState i := by
  fin_cases i <;> decide

/-- The two registration words differ in their ordered parent-to-port origin. -/
theorem two_registration_origins_distinct :
    (run F₂ Seed₂ [.d]).origin ≠
      (run F₂ Seed₂ [.p, .d]).origin := by
  decide

/-- This is an actual-word closure argument, not a count of ambient records. -/
private theorem twoState_run (i : Fin 6) :
    ∀ w : List Letter, ∃ j : Fin 6,
      run F₂ (twoState i) w = twoState j := by
  intro w
  induction w generalizing i with
  | nil => exact ⟨i, rfl⟩
  | cons a w ih =>
      simpa [run, twoState_step] using
        ih (if a = .p then twoNextP i else twoNextD i)

private theorem twoState_from_seed (w : List Letter) :
    ∃ i : Fin 6, run F₂ Seed₂ w = twoState i := by
  simpa [twoState] using twoState_run 0 w

/-- Every registered generated summary in the two-atom environment is one
of the four origin/phase states. -/
theorem actualRegisteredSummaries_two_complete
    (s : ActualRegisteredSummaries 2) :
    ∃ i : Fin 6, 2 ≤ i.val ∧ s.1 = twoState i := by
  obtain ⟨w, hw⟩ := s.2.1
  obtain ⟨i, hi⟩ := twoState_from_seed w
  refine ⟨i, ?_, ?_⟩
  · apply (twoState_registered i).mp
    rw [← hi, hw]
    exact s.2.2
  · exact hw.symm.trans hi

/-- Four actual histories, with no identification of opposite origins. -/
noncomputable def actualRegisteredSummariesTwoEquiv :
    Fin 4 ≃ ActualRegisteredSummaries 2 := by
  let encode (j : Fin 4) : ActualRegisteredSummaries 2 :=
    ⟨twoState ⟨j.val + 2, by omega⟩, by
      constructor
      · exact ⟨twoWord ⟨j.val + 2, by omega⟩,
          twoState_word ⟨j.val + 2, by omega⟩⟩
      · exact (twoState_registered ⟨j.val + 2, by omega⟩).2 (by simp)⟩
  apply Equiv.ofBijective encode
  constructor
  · intro i j hij
    have hstates :
        twoState ⟨i.val + 2, by omega⟩ =
          twoState ⟨j.val + 2, by omega⟩ := congrArg Subtype.val hij
    have hindices := twoState_injective hstates
    apply Fin.ext
    have hvals := congrArg Fin.val hindices
    dsimp at hvals
    omega
  · intro s
    obtain ⟨i, hi, his⟩ := actualRegisteredSummaries_two_complete s
    let j : Fin 4 := ⟨i.val - 2, by omega⟩
    refine ⟨j, Subtype.ext ?_⟩
    change twoState ⟨j.val + 2, by omega⟩ = s.1
    have hindex : (⟨j.val + 2, by omega⟩ : Fin 6) = i := by
      apply Fin.ext
      dsimp [j]
      omega
    rw [hindex]
    exact his.symm

private def twoOriginPhaseIndex (orientation : Bool) (phase : ZMod 2) : Fin 4 :=
  ⟨(if orientation then 2 else 0) + phase.val, by
    have hphase := phase.val_lt
    split_ifs <;> omega⟩

/-- `false` selects the `d` registration, `true` the `pd` registration;
the second coordinate selects the physical phase after registration. -/
noncomputable def actualRegisteredSummariesTwoProductEquiv :
    Bool × ZMod 2 ≃ ActualRegisteredSummaries 2 :=
  (Equiv.ofBijective (fun pair : Bool × ZMod 2 =>
    twoOriginPhaseIndex pair.1 pair.2) (by decide)).trans
      actualRegisteredSummariesTwoEquiv

/-- The Boolean coordinate reads the ordered registration origin, not just
an arbitrary enumeration of the four states. -/
theorem actualRegisteredSummariesTwoProduct_origin
    (orientation : Bool) (phase : ZMod 2) :
    (actualRegisteredSummariesTwoProductEquiv (orientation, phase)).1.origin =
      if orientation then (run F₂ Seed₂ [.p, .d]).origin
      else (run F₂ Seed₂ [.d]).origin := by
  cases orientation <;> fin_cases phase <;> decide

private theorem actualRegisteredSummariesTwoProduct_phase_at
    (orientation : Bool) (phase : ZMod 2) :
    (actualRegisteredSummariesTwoProductEquiv (orientation, phase)).1.placed phase =
      some F₂ := by
  cases orientation <;> fin_cases phase <;> decide

private theorem actualRegisteredSummariesTwoProduct_other_empty
    (orientation : Bool) (phase q : ZMod 2) (hne : q ≠ phase) :
    (actualRegisteredSummariesTwoProductEquiv (orientation, phase)).1.placed q =
      none := by
  exact (by decide : ∀ orientation : Bool, ∀ phase q : ZMod 2,
    q ≠ phase →
      (actualRegisteredSummariesTwoProductEquiv (orientation, phase)).1.placed q =
        none) orientation phase q hne

/-- The phase coordinate is exactly the unique physical carrier site. -/
theorem actualRegisteredSummariesTwoProduct_phase
    (orientation : Bool) (phase q : ZMod 2) :
    (actualRegisteredSummariesTwoProductEquiv (orientation, phase)).1.placed q =
      some F₂ ↔ q = phase := by
  constructor
  · intro h
    by_contra hne
    rw [actualRegisteredSummariesTwoProduct_other_empty orientation phase q hne] at h
    contradiction
  · intro h
    subst q
    exact actualRegisteredSummariesTwoProduct_phase_at orientation phase

noncomputable instance actualRegisteredSummariesTwoFintype :
    Fintype (ActualRegisteredSummaries 2) :=
  Fintype.ofEquiv (Fin 4) actualRegisteredSummariesTwoEquiv

theorem card_actualRegisteredSummaries_two :
    Fintype.card (ActualRegisteredSummaries 2) = 4 := by
  calc
    Fintype.card (ActualRegisteredSummaries 2) =
        Fintype.card (Bool × ZMod 2) :=
      (Fintype.card_congr actualRegisteredSummariesTwoProductEquiv).symm
    _ = 4 := by simp

/-- The actual-summary count for every environment in the manuscript's
domain. The `n ≥ 3` branch uses the origin-classified code-fiber assembly;
the `n = 2` branch uses the independent four-state execution table above. -/
theorem card_actualRegisteredSummaries_piecewise
    {n : ℕ} [NeZero n] (hn : 2 ≤ n) :
    Nat.card (ActualRegisteredSummaries n) =
      if n = 2 then 4 else
        n * ((2 * (n - 2)).choose (n - 2) +
          2 * ∑ b : Fin (n - 2),
            3 ^ b.1 * (2 * (n - 2) - (b.1 + 1)).choose
              ((n - 2) - (b.1 + 1))) := by
  by_cases htwo : n = 2
  · subst n
    simp only [Nat.card_eq_fintype_card]
    exact card_actualRegisteredSummaries_two
  · haveI : Fact (3 ≤ n) := ⟨by omega⟩
    rw [if_neg htwo, Nat.card_eq_fintype_card]
    exact card_actualRegisteredSummaries_closed

end RegisteredAbsorptionChains
