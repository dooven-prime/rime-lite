import FusionLogAllR.CarrierRotation
import FusionLogAllR.HoleTrace

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # Executions annotated by a gap trace

`HoleTrace` is deliberately a word-free rewrite certificate.  The inductive
relation below is the missing bookkeeping layer: every literal `p` is a
stationary gap step, while every literal `d` carries the rewrite it performs.
The physical extraction of such an annotation from a raw all-R execution is a
separate theorem; once supplied, the cost consequences are unconditional.
-/

def HoleTransition.fusionStep {g h : List ℤ} : HoleTransition g h → ℕ
  | .fusion _ _ => 1
  | _ => 0

inductive ExecutionTrace : List Letter → List ℤ → List ℤ → Type
  | nil (g : List ℤ) : ExecutionTrace [] g g
  | p {word : List Letter} {g h : List ℤ}
      (rest : ExecutionTrace word g h) :
      ExecutionTrace (.p :: word) g h
  | d {word : List Letter} {g h k : List ℤ}
      (transition : HoleTransition g h)
      (rest : ExecutionTrace word h k) :
      ExecutionTrace (.d :: word) g k

def ExecutionTrace.holeTrace {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → HoleTrace g h
  | .nil g => .nil g
  | .p rest => rest.holeTrace
  | .d transition rest => .cons transition rest.holeTrace

def ExecutionTrace.fusionSteps {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → ℕ
  | .nil _ => 0
  | .p rest => rest.fusionSteps
  | .d transition rest => transition.fusionStep + rest.fusionSteps

def ExecutionTrace.dLetters {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → ℕ
  | .nil _ => 0
  | .p rest => rest.dLetters
  | .d _ rest => rest.dLetters + 1

/-- A stationary rewrite consumes a real `d`, even though its potential
change and all four entries of `HoleLedger` are zero. -/
def HoleTransition.idleStep {g h : List ℤ} : HoleTransition g h → ℕ
  | .stationary _ => 1
  | _ => 0

def ExecutionTrace.idleSteps {word : List Letter} {g h : List ℤ} :
    ExecutionTrace word g h → ℕ
  | .nil _ => 0
  | .p rest => rest.idleSteps
  | .d transition rest => transition.idleStep + rest.idleSteps

/-- Every defect letter pays exactly one of four disjoint charges. Both
ordinary and rank-one backslides are included in the unweighted charge. -/
theorem ExecutionTrace.defect_accounting {word : List Letter} {g h : List ℤ}
    (trace : ExecutionTrace word g h) :
    trace.dLetters = trace.holeTrace.ledger.slides + trace.fusionSteps +
      trace.holeTrace.ledger.backslides + trace.idleSteps := by
  induction trace with
  | nil g => rfl
  | p rest ih => exact ih
  | d transition rest ih =>
      cases transition <;>
        simp_all [ExecutionTrace.dLetters, ExecutionTrace.holeTrace,
          ExecutionTrace.fusionSteps, ExecutionTrace.idleSteps,
          HoleTransition.idleStep, HoleTransition.fusionStep,
          HoleTransition.ledger, HoleTrace.ledger, HoleLedger.add] <;> omega

theorem HoleTransition.fusionStep_le_one {g h : List ℤ}
    (transition : HoleTransition g h) : transition.fusionStep ≤ 1 := by
  cases transition <;> simp [HoleTransition.fusionStep]

theorem ExecutionTrace.dLetters_eq_count {word : List Letter}
    {g h : List ℤ} (trace : ExecutionTrace word g h) :
    trace.dLetters = word.count .d := by
  induction trace with
  | nil g => simp [ExecutionTrace.dLetters]
  | p rest ih => simpa [ExecutionTrace.dLetters] using ih
  | d transition rest ih =>
      simp [ExecutionTrace.dLetters]
      omega

theorem ExecutionTrace.slides_add_fusions_le_dLetters
    {word : List Letter} {g h : List ℤ}
    (trace : ExecutionTrace word g h) :
    trace.holeTrace.ledger.slides + trace.fusionSteps ≤ trace.dLetters := by
  induction trace with
  | nil g => simp [ExecutionTrace.holeTrace, ExecutionTrace.fusionSteps,
      ExecutionTrace.dLetters, HoleTrace.ledger]
  | p rest ih =>
      simpa [ExecutionTrace.holeTrace, ExecutionTrace.fusionSteps,
        ExecutionTrace.dLetters, HoleTrace.ledger] using ih
  | d transition rest ih =>
      have hstep : transition.ledger.slides + transition.fusionStep ≤ 1 := by
        cases transition <;>
          simp [HoleTransition.ledger, HoleTransition.fusionStep]
      have hrest := ih
      simp only [ExecutionTrace.holeTrace, ExecutionTrace.fusionSteps,
        ExecutionTrace.dLetters, HoleTrace.ledger, HoleLedger.add]
      omega

theorem count_p_add_count_d (word : List Letter) :
    word.count .p + word.count .d = word.length := by
  induction word with
  | nil => simp
  | cons letter rest ih =>
      cases letter <;> simp <;> omega

/-! A certificate contains the concrete interval decomposition already used by
the rotation theorem, together with the literal-to-trace simulation.  The
fields are intentionally explicit: `RawAllRCertificate` can populate the
same structure directly from a full event-log target without changing the
arithmetic theorems below.
-/
structure AllRTraceExtraction (n : ℕ) [NeZero n] where
  F : Finset (ZMod n)
  carrier : ZMod n
  registrationPrefix : List Letter
  interWord : List Letter
  tail : List Letter
  start : Execution n (ZMod n)
  registrationRun :
    run F (singletonExecution n) registrationPrefix = start
  afterInter : Execution n (ZMod n)
  intervals : RightFusionIntervals F carrier (n - 2) start afterInter interWord
  ordered : SourceOrdered start.placed
  startPacket : ∃ C, start.placed 0 = some C ∧ carrier ∈ C
  afterPacket : ∃ C, afterInter.placed 0 = some C ∧ carrier ∈ C
  tailEnd : ∃ D, (run F afterInter tail).placed (n - 1 : ℕ) = some D ∧ carrier ∈ D
  trace : ExecutionTrace (interWord ++ tail) (initialGaps n) [((n - 1 : ℕ) : ℤ)]
  traceFusionSteps : trace.fusionSteps = n - 2
  prefixD : registrationPrefix.count .d = 1
  word : List Letter
  word_eq : word = registrationPrefix ++ interWord ++ tail
  return_dominates :
    trace.holeTrace.ledger.backslides ≤
      executionCarrierReturns F start carrier (interWord ++ tail)

theorem AllRTraceExtraction.post_rotation_lower_bound
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    pMin n ≤ (cert.interWord ++ cert.tail).count .p := by
  obtain ⟨C, hC, hcarrierC⟩ := cert.afterPacket
  obtain ⟨D, hD, hcarrierD⟩ := cert.tailEnd
  have hrot := actual_allR_rotation_lower_bound cert.intervals hn cert.ordered
    cert.tail C D hC hcarrierC hD hcarrierD
  omega

theorem AllRTraceExtraction.post_rotation_lower_bound_with_trace
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    pMin n + cert.trace.holeTrace.ledger.backslides ≤
      (cert.interWord ++ cert.tail).count .p := by
  obtain ⟨C, hC, hcarrierC⟩ := cert.afterPacket
  obtain ⟨D, hD, hcarrierD⟩ := cert.tailEnd
  have hrot := actual_allR_rotation_lower_bound cert.intervals hn cert.ordered
    cert.tail C D hC hcarrierC hD hcarrierD
  have hdom := cert.return_dominates
  omega

theorem AllRTraceExtraction.post_d_lower_bound
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    (n - 2) + allRSlides n ≤ (cert.interWord ++ cert.tail).count .d := by
  have hledger := ExecutionTrace.slides_add_fusions_le_dLetters cert.trace
  have hslides := HoleTrace.allR_slide_identity hn (n - 1 : ℕ) cert.trace.holeTrace
  have hfusions := cert.traceFusionSteps
  have hcount := cert.trace.dLetters_eq_count
  rw [hfusions, hslides, hcount] at hledger
  omega

theorem AllRTraceExtraction.post_d_lower_bound_with_trace
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    (n - 2) + allRSlides n + cert.trace.holeTrace.ledger.weightedBack +
        cert.trace.holeTrace.ledger.backslides ≤
      (cert.interWord ++ cert.tail).count .d := by
  have hledger := ExecutionTrace.defect_accounting cert.trace
  have hslides := HoleTrace.allR_slide_identity hn (n - 1 : ℕ) cert.trace.holeTrace
  have hfusions := cert.traceFusionSteps
  have hcount := cert.trace.dLetters_eq_count
  rw [hfusions, hslides, hcount] at hledger
  omega

theorem AllRTraceExtraction.word_length_lower_bound
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    pMin n + (n - 1) + allRSlides n ≤ cert.word.length := by
  have hp := cert.post_rotation_lower_bound hn
  have hd := cert.post_d_lower_bound hn
  have hprefix : cert.registrationPrefix.count .d = 1 := cert.prefixD
  simp [List.count_append] at hp hd
  have hcounts := count_p_add_count_d (cert.registrationPrefix ++ cert.interWord ++ cert.tail)
  have hsum :
      pMin n + (n - 1) + allRSlides n ≤
        (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .p +
          (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .d := by
    simp [List.count_append, hprefix]
    omega
  calc
    pMin n + (n - 1) + allRSlides n ≤
        (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .p +
          (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .d := hsum
    _ = (cert.registrationPrefix ++ cert.interWord ++ cert.tail).length := hcounts
    _ = cert.word.length := by rw [cert.word_eq]

theorem allRMinimumLength_eq (n : ℕ) (hn : 3 ≤ n) :
    pMin n + (n - 1) + allRSlides n =
      (3 * n * (n - 1)) / 2 - 1 := by
  have hAdiv : 2 ∣ (n - 1) * (n - 2) := by
    have h := (Nat.even_mul_pred_self (n - 1)).two_dvd
    simpa [show n - 1 - 1 = n - 2 by omega] using h
  have hBdiv : 2 ∣ n * (n - 1) := (Nat.even_mul_pred_self n).two_dvd
  have hCdiv : 2 ∣ 3 * n * (n - 1) := by
    simpa [Nat.mul_assoc] using (dvd_mul_of_dvd_right hBdiv 3)
  have hA : 2 * allRSlides n = (n - 1) * (n - 2) := by
    unfold allRSlides
    exact Nat.mul_div_cancel' hAdiv
  have hC : 2 * ((3 * n * (n - 1)) / 2) = 3 * n * (n - 1) :=
    Nat.mul_div_cancel' hCdiv
  have hprod : 1 ≤ n * (n - 1) := by
    have hnpos : 0 < n := by omega
    have hpredpos : 0 < n - 1 := by omega
    exact Nat.succ_le_of_lt (Nat.mul_pos hnpos hpredpos)
  have hcancel : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
  have hgap : 2 * (n - 1) + (n - 1) * (n - 2) = n * (n - 1) := by
    calc
      2 * (n - 1) + (n - 1) * (n - 2) =
          (n - 1) * (2 + (n - 2)) := by ring
      _ = (n - 1) * n := by congr 1; omega
      _ = n * (n - 1) := by ring
  have hleft :
      pMin n + (n - 1) + allRSlides n + 1 =
        3 * (n * (n - 1)) / 2 := by
    apply Nat.mul_left_cancel (by omega : 0 < 2)
    simp only [Nat.mul_add]
    have hp := Nat.sub_add_cancel hprod
    have hC' : 2 * (3 * (n * (n - 1)) / 2) =
        3 * (n * (n - 1)) := by
      simpa [Nat.mul_assoc] using hC
    unfold pMin
    rw [hA, hC']
    omega
  have hright :
      (3 * n * (n - 1)) / 2 - 1 + 1 =
        3 * (n * (n - 1)) / 2 := by
    have hQpos : 1 ≤ (3 * n * (n - 1)) / 2 := by
      have hnum : 2 ≤ 3 * n * (n - 1) := by nlinarith [hn]
      exact Nat.succ_le_of_lt (Nat.div_pos hnum (by omega))
    have hQ := Nat.sub_add_cancel hQpos
    rw [show 3 * n * (n - 1) = 3 * (n * (n - 1)) by ring]
    simpa [show 3 * n * (n - 1) = 3 * (n * (n - 1)) by ring] using hQ
  have hsum := hleft.trans hright.symm
  exact Nat.add_right_cancel hsum

theorem AllRTraceExtraction.word_length_lower_bound_closed
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    (3 * n * (n - 1)) / 2 - 1 ≤ cert.word.length := by
  rw [← allRMinimumLength_eq n hn]
  exact cert.word_length_lower_bound hn

theorem AllRTraceExtraction.word_length_surplus_bound
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n) :
    (3 * n * (n - 1)) / 2 - 1 +
        2 * cert.trace.holeTrace.ledger.backslides +
        cert.trace.holeTrace.ledger.weightedBack ≤ cert.word.length := by
  have hp := cert.post_rotation_lower_bound_with_trace hn
  have hd := cert.post_d_lower_bound_with_trace hn
  have hprefix : cert.registrationPrefix.count .d = 1 := cert.prefixD
  simp [List.count_append] at hp hd
  have hcounts := count_p_add_count_d
    (cert.registrationPrefix ++ cert.interWord ++ cert.tail)
  have hbase := allRMinimumLength_eq n hn
  have hsum :
      pMin n + (n - 1) + allRSlides n +
          2 * cert.trace.holeTrace.ledger.backslides +
          cert.trace.holeTrace.ledger.weightedBack ≤
        (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .p +
          (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .d := by
    simp [List.count_append, hprefix]
    omega
  calc
    (3 * n * (n - 1)) / 2 - 1 +
          2 * cert.trace.holeTrace.ledger.backslides +
          cert.trace.holeTrace.ledger.weightedBack =
        pMin n + (n - 1) + allRSlides n +
          2 * cert.trace.holeTrace.ledger.backslides +
          cert.trace.holeTrace.ledger.weightedBack := by omega
    _ ≤ (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .p +
          (cert.registrationPrefix ++ cert.interWord ++ cert.tail).count .d := hsum
    _ = (cert.registrationPrefix ++ cert.interWord ++ cert.tail).length := hcounts
    _ = cert.word.length := by rw [cert.word_eq]

/-! Equality at the lower bound only removes the numerical slack.  The
semantic ordering of zero-slack steps is intentionally left for the later
rigidity/uniqueness module.
-/
theorem AllRTraceExtraction.minimal_length_budget
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n)
    (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.trace.holeTrace.ledger.weightedBack = 0 ∧
      cert.registrationPrefix.count .p = 0 ∧
      (cert.interWord ++ cert.tail).count .p = pMin n ∧
      (cert.interWord ++ cert.tail).count .d = (n - 2) + allRSlides n := by
  have hp := cert.post_rotation_lower_bound_with_trace hn
  have hd := cert.post_d_lower_bound_with_trace hn
  have hprefixD : cert.registrationPrefix.count .d = 1 := cert.prefixD
  let post := cert.interWord ++ cert.tail
  have hprefixCounts := count_p_add_count_d cert.registrationPrefix
  have hpostCounts := count_p_add_count_d post
  have hbase := allRMinimumLength_eq n hn
  have hsurplus := cert.word_length_surplus_bound hn
  have hwb : cert.trace.holeTrace.ledger.weightedBack = 0 := by
    omega
  have hprefixLength :
      cert.registrationPrefix.length = cert.registrationPrefix.count .p + 1 := by
    simp [hprefixD] at hprefixCounts
    omega
  have hpostLength :
      post.length = post.count .p + post.count .d := by
    simpa using hpostCounts.symm
  have hwordCounts :
      cert.word.length = cert.registrationPrefix.count .p + 1 +
        post.count .p + post.count .d := by
    calc
      cert.word.length =
          (cert.registrationPrefix ++ cert.interWord ++ cert.tail).length := by
        rw [cert.word_eq]
      _ = cert.registrationPrefix.length + (cert.interWord ++ cert.tail).length := by
        simp [List.length_append]
      _ = cert.registrationPrefix.count .p + 1 +
          post.count .p + post.count .d := by
        rw [hprefixLength, hpostLength]
        omega
  have hp' : pMin n + cert.trace.holeTrace.ledger.backslides ≤ post.count .p := by
    simpa [post] using hp
  have hd' : n - 2 + allRSlides n + cert.trace.holeTrace.ledger.weightedBack +
        cert.trace.holeTrace.ledger.backslides ≤
      post.count .d := by
    simpa [post] using hd
  constructor
  · exact hwb
  constructor
  · omega
  constructor
  · change post.count .p = pMin n
    omega
  · change post.count .d = (n - 2) + allRSlides n
    omega

end FusionLogAllR
