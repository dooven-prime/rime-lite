import FusionLogAllR.AllRTraceExtraction

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! # Equality forces every defect to pay for a slide or a fusion

These statements concern every step of the supplied execution annotation,
including a rank-one tail. They do not assert uniqueness of the raw word,
or assume that an annotation has already been extracted from every all-R
realization.
-/

def HoleTransition.Paid {g h : List ℤ} : HoleTransition g h → Prop
  | .slide _ _ _ _ => True
  | .fusion _ _ => True
  | _ => False

def ExecutionTrace.AllDefectsPaid {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → Prop
  | .nil _ => True
  | .p rest => rest.AllDefectsPaid
  | .d transition rest => transition.Paid ∧ rest.AllDefectsPaid

theorem ExecutionTrace.allDefectsPaid_of_zero_unpaid
    {word : List Letter} {g h : List ℤ} (trace : ExecutionTrace word g h)
    (hback : trace.holeTrace.ledger.backslides = 0)
    (hidle : trace.idleSteps = 0) : trace.AllDefectsPaid := by
  induction trace with
  | nil g => trivial
  | p rest ih => exact ih hback hidle
  | d transition rest ih =>
      simp only [ExecutionTrace.holeTrace, HoleTrace.ledger, HoleLedger.add,
        ExecutionTrace.idleSteps] at hback hidle
      have hrestBack : rest.holeTrace.ledger.backslides = 0 := by omega
      have hrestIdle : rest.idleSteps = 0 := by omega
      have hpaid : transition.Paid := by
        cases transition <;>
          simp_all [HoleTransition.Paid, HoleTransition.ledger, HoleTransition.idleStep]
      exact ⟨hpaid, ih hrestBack hrestIdle⟩

theorem ExecutionTrace.allDefectsPaid_of_exact_payment
    {word : List Letter} {g h : List ℤ} (trace : ExecutionTrace word g h)
    (hpaid : trace.holeTrace.ledger.slides + trace.fusionSteps = trace.dLetters) :
    trace.AllDefectsPaid := by
  have h := trace.defect_accounting
  apply trace.allDefectsPaid_of_zero_unpaid <;> omega

theorem AllRTraceExtraction.minimal_exact_defect_payment
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.trace.holeTrace.ledger.slides + cert.trace.fusionSteps =
      cert.trace.dLetters := by
  obtain ⟨hback, _, _, hd⟩ := cert.minimal_length_budget hn hmin
  have hslides := HoleTrace.allR_slide_identity hn (n - 1 : ℕ) cert.trace.holeTrace
  have hfusion := cert.traceFusionSteps
  have hcount := cert.trace.dLetters_eq_count
  omega

/-- A minimum-length certificate contains no idle defect, no ordinary
carrier backslide, and no rank-one backslide. -/
theorem AllRTraceExtraction.minimal_allDefectsPaid
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.trace.AllDefectsPaid :=
  cert.trace.allDefectsPaid_of_exact_payment
    (cert.minimal_exact_defect_payment hn hmin)

theorem AllRTraceExtraction.minimal_unpaid_counts_zero
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.trace.holeTrace.ledger.backslides = 0 ∧ cert.trace.idleSteps = 0 := by
  have h := cert.trace.defect_accounting
  have heq := cert.minimal_exact_defect_payment hn hmin
  constructor <;> omega

/-- This vanishing statement uses the actual port-membership return
counter, not the weighted potential correction. -/
theorem AllRTraceExtraction.minimal_executionCarrierReturns_zero
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    executionCarrierReturns cert.F cert.start cert.carrier
      (cert.interWord ++ cert.tail) = 0 := by
  obtain ⟨_, _, hp, _⟩ := cert.minimal_length_budget hn hmin
  obtain ⟨C, hC, hcarrierC⟩ := cert.afterPacket
  obtain ⟨D, hD, hcarrierD⟩ := cert.tailEnd
  have hrot := actual_allR_rotation_lower_bound cert.intervals hn cert.ordered
    cert.tail C D hC hcarrierC hD hcarrierD
  omega

end FusionLogAllR
