import RSR2.SequentialPreparationDebts
import RSR2.PortCostSharpness
import RSR2.Construction

/-!
# An endpoint forcing two successive positive preparation debts

Suppose atom 0 is finally below and atom 1 is finally above.  Before the
first lower rotation, a lower defect would fuse these atoms irreversibly,
and an elevator would send atom 0 up permanently.  Thus only upper actions,
which fix the seed, may precede that first rotation.  It pays the last
atom's one-unit approach debt and places atom 1 at lower site 2.  Transferring
atom 1 then pays a fresh `n-2` approach debt on the disjoint suffix.

The cuts are extracted from every successful raw word, rather than supplied
by a chosen construction.  This is a linear two-interval obstruction, not a
superlinear partition-diameter bound.
-/

namespace RSR2.Parametric

private theorem step_upper_atom_persists (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (a : Fin n)
    (hstep : step n hn P letter = some Q) (ha : (P a).1 = true) :
    (Q a).1 = true := by
  cases letter with
  | p layer =>
      have hQ : Q = rotate n (by omega) P layer := by
        simpa only [step_p, Option.some.injEq] using hstep.symm
      rw [hQ]
      cases layer <;> simp [rotate, ha]
  | d layer =>
      have hQ : Q = collapse n hn P layer := by
        simpa only [step_d, Option.some.injEq] using hstep.symm
      rw [hQ]
      unfold collapse
      split
      · rename_i hloc
        have hl := congrArg Prod.fst hloc
        simp only at hl
        simp [← hl, ha]
      · exact ha
  | v =>
      have hQ := ((step_v_eq_some_iff n hn P Q).mp hstep).2
      rw [hQ]
      have hne : P a ≠ (false, site0 n (by omega)) := by
        intro hloc
        have hl := congrArg Prod.fst hloc
        simp [ha] at hl
      simp [liftPacket, hne, ha]

private theorem run_upper_atom_persists (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (a : Fin n)
    (hrun : run n hn P word = some Q) (ha : (P a).1 = true) :
    (Q a).1 = true := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      exact he ▸ ha
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          exact ih R ht (step_upper_atom_persists n hn P R letter a hs ha)

theorem splitEndpoint_first_lower_rotation
    (n : Nat) (hn : 1 < n) (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q)
    (hzero : (Q (site0 n (by omega))).1 = false)
    (hone : (Q (site1 n hn)).1 = true) :
    ∃ before after,
      word = before ++ (.p false :: after) ∧
      lowerRotationCount before = 0 ∧
      run n hn (seed n) before = some (seed n) ∧
      run n hn (rotate n (by omega) (seed n) false) after = some Q := by
  induction word with
  | nil =>
      have he : seed n = Q := by simpa only [run, Option.some.injEq] using hrun
      simp [← he, seed] at hone
  | cons letter rest ih =>
      cases letter with
      | p layer =>
          cases layer with
          | false =>
              refine ⟨[], rest, rfl, rfl, rfl, ?_⟩
              simpa [run, step_p] using hrun
          | true =>
              have hseed : rotate n (by omega) (seed n) true = seed n := by
                funext a
                simp [rotate, seed]
              have ht : run n hn (seed n) rest = some Q := by
                simpa [run, step_p, hseed] using hrun
              obtain ⟨before, after, hword, hcount, hbefore, hafter⟩ := ih ht
              refine ⟨.p true :: before, after, ?_, ?_, ?_, hafter⟩
              · simp [hword]
              · simpa [lowerRotationCount] using hcount
              · simpa [run, step_p, hseed] using hbefore
      | d layer =>
          cases layer with
          | false =>
              have ht : run n hn (collapse n hn (seed n) false) rest = some Q := by
                simpa [run, step_d] using hrun
              have hparents : samePacket (collapse n hn (seed n) false)
                  (site0 n (by omega)) (site1 n hn) := by
                simp [samePacket, collapse, seed, site0, site1, Fin.mk.injEq]
              have he := run_samePacket_mono n hn _ Q rest ht _ _ hparents
              have hl := congrArg Prod.fst he
              simp [hzero, hone] at hl
          | true =>
              have hseed : collapse n hn (seed n) true = seed n := by
                funext a
                simp [collapse, seed]
              have ht : run n hn (seed n) rest = some Q := by
                simpa [run, step_d, hseed] using hrun
              obtain ⟨before, after, hword, hcount, hbefore, hafter⟩ := ih ht
              refine ⟨.d true :: before, after, ?_, ?_, ?_, hafter⟩
              · simp [hword]
              · simpa [lowerRotationCount] using hcount
              · simpa [run, step_d, hseed] using hbefore
      | v =>
          cases hs : step n hn (seed n) .v with
          | none => simp [run, hs] at hrun
          | some R =>
              have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
              have hR := ((step_v_eq_some_iff n hn (seed n) R).mp hs).2
              have hupper : (R (site0 n (by omega))).1 = true := by
                simp [hR, liftPacket, seed]
              have hfinal := run_upper_atom_persists n hn R Q rest _ ht hupper
              simp [hzero] at hfinal

theorem splitEndpoint_two_preparation_debts
    (n : Nat) (hn : 3 ≤ n) (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hzero : (Q (site0 n (by omega))).1 = false)
    (hone : (Q (site1 n (by omega))).1 = true) :
    ∃ schedule : DebtSchedule n (by omega),
      schedule.initial = seed n ∧ schedule.final = Q ∧
      schedule.word = word ∧
      schedule.intervals.map DebtInterval.debt = [1, n - 2] := by
  obtain ⟨before, after, hword, _, hbefore, hafter⟩ :=
    splitEndpoint_first_lower_rotation n (by omega) Q word hrun hzero hone
  let rotated := rotate n (by omega) (seed n) false
  let first : DebtInterval n (by omega) := {
    start := seed n
    finish := rotated
    word := before ++ [.p false]
    potential := .approach ⟨n - 1, by omega⟩
    run_ok := by simp [run_append, hbefore, run, step_p, rotated]
  }
  let second : DebtInterval n (by omega) := {
    start := rotated
    finish := Q
    word := after
    potential := .approach (site1 n (by omega))
    run_ok := hafter
  }
  have hfirst : first.debt = 1 := by
    have hlast : ¬ (n - 1 + 1 < n) := by omega
    have hlarge : 1 < n - 1 := by omega
    have harith : n - (n - 1) = 1 := by omega
    simp [first, DebtInterval.debt, debtPotentialValue,
      lowerPortApproachDistance, rotated, rotate, seed, next,
      hlast, hlarge, harith]
  have hsecond : second.debt = n - 2 := by
    dsimp [second, DebtInterval.debt, debtPotentialValue]
    have hrot : lowerPortApproachDistance n rotated (site1 n (by omega)) = n - 2 := by
      simp [lowerPortApproachDistance, rotated, rotate, seed, site1, next,
        show 1 + 1 < n by omega]
    have hupper : lowerPortApproachDistance n Q (site1 n (by omega)) = 0 := by
      simp [lowerPortApproachDistance, hone]
    rw [hrot, hupper, Nat.sub_zero]
  refine ⟨{
    initial := seed n
    final := Q
    word := word
    intervals := [first, second]
    chain := by simp [IntervalChain, first, second]
    word_split := by simpa [first, second, List.append_assoc] using hword
  }, rfl, rfl, rfl, ?_⟩
  simp [hfirst, hsecond]

theorem splitEndpoint_rotation_lower_bound
    (n : Nat) (hn : 3 ≤ n) (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hzero : (Q (site0 n (by omega))).1 = false)
    (hone : (Q (site1 n (by omega))).1 = true) :
    n - 1 ≤ lowerRotationCount word := by
  obtain ⟨schedule, _, _, hword, hdebts⟩ :=
    splitEndpoint_two_preparation_debts n hn Q word hrun hzero hone
  have hbound := debtSchedule_totalDebt_le_rotations schedule
  simp only [DebtSchedule.totalDebt, hdebts, List.sum_cons, List.sum_nil,
    Nat.add_zero, DebtSchedule.totalRotations, hword] at hbound
  omega

/-- One actual endpoint in the family; all but atom 1 remain below. -/
def splitEndpointWitness (n : Nat) (hn : 1 < n) : Placement n :=
  liftPacket n (by omega)
    (rotateMany n (by omega) (seed n) false (n - 1))

def splitEndpointWitnessWord (n : Nat) : List Letter :=
  List.replicate (n - 1) (.p false) ++ [.v]

theorem splitEndpointWitness_attains
    (n : Nat) (hn : 3 ≤ n) :
    run n (by omega) (seed n) (splitEndpointWitnessWord n) =
        some (splitEndpointWitness n (by omega)) ∧
      (splitEndpointWitness n (by omega) (site0 n (by omega))).1 = false ∧
      (splitEndpointWitness n (by omega) (site1 n (by omega))).1 = true ∧
      lowerRotationCount (splitEndpointWitnessWord n) = n - 1 := by
  let P := rotateMany n (by omega) (seed n) false (n - 1)
  have hlower : ∀ a, (P a).1 = false := by
    intro a
    simp [P, rotateMany_apply, seed]
  have hzeroSite : (P (site0 n (by omega))).2.val = n - 1 := by
    simp [P, rotateMany_apply, seed, nextMany_val, site0,
      Nat.mod_eq_of_lt (show n - 1 < n by omega)]
  have honeLoc : P (site1 n (by omega)) = (false, site0 n (by omega)) := by
    apply Prod.ext
    · exact hlower _
    · apply Fin.ext
      simp [P, rotateMany_apply, seed, nextMany_val, site0, site1,
        show 1 + (n - 1) = n by omega]
  have hg : liftGuard n (by omega) P := by
    constructor
    · exact ⟨site1 n (by omega), honeLoc⟩
    · rintro ⟨a, ha⟩
      have hbad := congrArg Prod.fst ha
      simp [hlower] at hbad
  have hzeroNe : P (site0 n (by omega)) ≠ (false, site0 n (by omega)) := by
    intro he
    have hv : (P (site0 n (by omega))).2.val = 0 :=
      congrArg (fun loc => loc.2.val) he
    rw [hzeroSite] at hv
    omega
  have hg' : liftGuard n (by omega)
      (rotateMany n (by omega) (seed n) false (n - 1)) := hg
  refine ⟨?_, ?_, ?_, ?_⟩
  · simp [splitEndpointWitnessWord, run_append, run_powers,
      run, step, hg', splitEndpointWitness]
  · change (liftPacket n (by omega) P (site0 n (by omega))).1 = false
    simp [liftPacket, hzeroNe, hlower]
  · change (liftPacket n (by omega) P (site1 n (by omega))).1 = true
    simp [liftPacket, honeLoc]
  · simp [splitEndpointWitnessWord, lowerRotationCount]

end RSR2.Parametric

