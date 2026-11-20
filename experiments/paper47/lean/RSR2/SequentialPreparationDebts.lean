import RSR2.LowerPortGeometry

/-!
# Interval preparation debts

This module packages the low-level part of the next geometric question.  An
interval is a contiguous piece of one actual successful execution, together
with either an approach or a separation potential.  The potential is allowed
to change from interval to interval, but every interval is charged against the
same raw lower-rotation counter.  No claim is made here that a target endpoint
forces many positive intervals; that is the separate geometric problem.
-/

namespace RSR2.Parametric

inductive DebtPotential (n : Nat) where
  | approach (a : Fin n)
  | separation (a b : Fin n)

def debtPotentialValue (n : Nat) (P : Placement n) :
    DebtPotential n → Nat
  | .approach a => lowerPortApproachDistance n P a
  | .separation a b => lowerSeparationDistance n P a b

structure DebtInterval (n : Nat) (hn : 1 < n) where
  start : Placement n
  finish : Placement n
  word : List Letter
  potential : DebtPotential n
  run_ok : run n hn start word = some finish

def DebtInterval.debt {n : Nat} {hn : 1 < n}
    (segment : DebtInterval n hn) : Nat :=
  debtPotentialValue n segment.start segment.potential -
    debtPotentialValue n segment.finish segment.potential

def DebtInterval.rotations {n : Nat} {hn : 1 < n}
    (segment : DebtInterval n hn) : Nat :=
  lowerRotationCount segment.word

theorem debtInterval_debt_le_rotations
    {n : Nat} {hn : 1 < n} (segment : DebtInterval n hn) :
    segment.debt ≤ segment.rotations := by
  cases segment with
  | mk start finish word potential run_ok =>
      cases potential with
      | approach a =>
          have h := run_lowerPortApproachDistance n hn start finish word a run_ok
          dsimp [DebtInterval.debt, DebtInterval.rotations,
            debtPotentialValue]
          omega
      | separation a b =>
          have h := run_lowerSeparationDistance n hn start finish word a b run_ok
          dsimp [DebtInterval.debt, DebtInterval.rotations,
            debtPotentialValue]
          omega

def IntervalChain {n : Nat} {hn : 1 < n} :
    Placement n → List (DebtInterval n hn) → Placement n → Prop
  | initial, [], final => initial = final
  | initial, segment :: rest, final =>
      initial = segment.start ∧
        IntervalChain segment.finish rest final

structure DebtSchedule (n : Nat) (hn : 1 < n) where
  initial : Placement n
  final : Placement n
  word : List Letter
  intervals : List (DebtInterval n hn)
  chain : IntervalChain initial intervals final
  word_split : word = (intervals.map (fun segment => segment.word)).flatten

def DebtSchedule.totalDebt {n : Nat} {hn : 1 < n}
    (schedule : DebtSchedule n hn) : Nat :=
  (schedule.intervals.map DebtInterval.debt).sum

def DebtSchedule.totalRotations {n : Nat} {hn : 1 < n}
    (schedule : DebtSchedule n hn) : Nat :=
  lowerRotationCount schedule.word

private theorem lowerRotationCount_flatten_map
    (segments : List (List Letter)) :
    lowerRotationCount segments.flatten =
      (segments.map lowerRotationCount).sum := by
  induction segments with
  | nil => simp [lowerRotationCount]
  | cons segment rest ih =>
      simp only [List.flatten_cons, List.map_cons, List.sum_cons]
      simp only [lowerRotationCount] at ih ⊢
      rw [List.count_append, ih]

theorem debtSchedule_totalDebt_le_rotations
    {n : Nat} {hn : 1 < n} (schedule : DebtSchedule n hn) :
    schedule.totalDebt ≤ schedule.totalRotations := by
  have hsum :
      (schedule.intervals.map DebtInterval.debt).sum ≤
        (schedule.intervals.map DebtInterval.rotations).sum := by
    induction schedule.intervals with
    | nil => exact Nat.le_refl 0
    | cons segment rest ih =>
        simp only [List.map_cons, List.sum_cons]
        exact Nat.add_le_add (debtInterval_debt_le_rotations segment) ih
  rw [DebtSchedule.totalDebt, DebtSchedule.totalRotations,
    schedule.word_split,
    lowerRotationCount_flatten_map]
  simp only [List.map_map, Function.comp_def]
  exact hsum

theorem intervalChain_run
    {n : Nat} {hn : 1 < n}
    (initial final : Placement n)
    (segments : List (DebtInterval n hn))
    (hchain : IntervalChain initial segments final) :
    run n hn initial
        (segments.map (fun segment => segment.word)).flatten = some final := by
  induction segments generalizing initial with
  | nil =>
      simp only [IntervalChain] at hchain
      simp only [hchain, List.map_nil, List.flatten_nil, run]
  | cons segment rest ih =>
      simp only [IntervalChain] at hchain
      obtain ⟨hstart, hrest⟩ := hchain
      rw [List.map_cons, List.flatten_cons, run_append]
      rw [hstart, segment.run_ok]
      simpa only [Option.bind_some] using ih segment.finish hrest

theorem DebtSchedule.whole_run
    {n : Nat} {hn : 1 < n} (schedule : DebtSchedule n hn) :
    run n hn schedule.initial schedule.word = some schedule.final := by
  rw [schedule.word_split]
  exact intervalChain_run schedule.initial schedule.final
    schedule.intervals schedule.chain

end RSR2.Parametric

