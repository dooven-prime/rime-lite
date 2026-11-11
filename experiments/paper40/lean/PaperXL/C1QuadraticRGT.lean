import PaperXL.C1QuadraticCompression
import RGTBoundedHistory.ObservationCompression

/-!
# Conditional quadratic R/G/T certificates for C1 consumers

The C1 representative-word theorem preserves the complete `CircularLogState`.
This module supplies the remaining semantic adapter for consumers defined on
that state, including lossy candidate maps on the complete state. It does not
claim a transfer to an independently defined lossy runtime state or to the
archived Python consumer without an additional correspondence theorem.
-/

namespace PaperXL

open RGTBoundedHistory

universe u v w

variable {n m : Nat} {Cmd : Type u} {V : Type v} {O : Type w}

abbrev C1Consumer (n m : Nat) (Cmd : Type u) (V : Type v) (O : Type w) :=
  CircularConsumerBridge.RegisteredConsumer Cmd V O (n := n) (m := m)

theorem c1QuadraticReplacement [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E) (hn : 3 ≤ n) :
    BoundedObservationReplacement (CircularConsumerBridge.completeSystem E)
      id (c1QuadraticHistoryBudget n) where
  replace word := by
    obtain ⟨representative, hstate, hlength⟩ :=
      c1QuadraticCompression_budget E h hn word
    refine ⟨representative, hlength, ?_⟩
    change RGTBoundedHistory.run (CircularLogState.step E)
        (CircularLogState.seedState E) representative =
      RGTBoundedHistory.run (CircularLogState.step E)
        (CircularLogState.seedState E) word
    rw [recursiveRun_eq_rawRun E representative,
      recursiveRun_eq_rawRun E word]
    exact hstate

theorem c1CheckSpecFactorization [NeZero n]
    (E : CircularEnvironment n m) (C : C1Consumer n m Cmd V O) :
    CheckSpecObservationFactorization C.toCheckSpec
      (CircularConsumerBridge.completeSystem E) id :=
  CheckSpecObservationFactorization.identity C.toCheckSpec
    (CircularConsumerBridge.completeSystem E)

theorem c1_registered_read_failure_quadratic [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E) (hn : 3 ≤ n)
    (C : C1Consumer n m Cmd V O)
    (hregistered : C.DomainReachable
      (CircularConsumerBridge.completeSystem E)) :
    ¬ C.R ↔
      ∃ h₁ h₂,
        h₁.length ≤ c1QuadraticHistoryBudget n ∧
        h₂.length ≤ c1QuadraticHistoryBudget n ∧
        C.sameFiber
          ((CircularConsumerBridge.completeSystem E).eval h₁)
          ((CircularConsumerBridge.completeSystem E).eval h₂) ∧
        C.report ((CircularConsumerBridge.completeSystem E).eval h₁) ≠
          C.report ((CircularConsumerBridge.completeSystem E).eval h₂) := by
  rw [Consumer.readCondition_toCheckSpec_iff C
    (CircularConsumerBridge.completeSystem E) hregistered]
  have hcompressed := CheckSpec.compressed_read_failure_iff
    C.toCheckSpec (CircularConsumerBridge.completeSystem E) id
    (c1QuadraticHistoryBudget n)
    (c1QuadraticReplacement E h hn)
    (c1CheckSpecFactorization E C)
  simpa [Consumer.toCheckSpec, Consumer.sameFiber, CheckSpec.readCollision,
    CheckSpec.sameFiber] using hcompressed

theorem c1_registered_guard_failure_quadratic [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E) (hn : 3 ≤ n)
    (C : C1Consumer n m Cmd V O)
    (hregistered : C.DomainReachable
      (CircularConsumerBridge.completeSystem E)) :
    ¬ C.G ↔
      ∃ h₁ h₂,
        h₁.length ≤ c1QuadraticHistoryBudget n ∧
        h₂.length ≤ c1QuadraticHistoryBudget n ∧
        C.sameFiber
          ((CircularConsumerBridge.completeSystem E).eval h₁)
          ((CircularConsumerBridge.completeSystem E).eval h₂) ∧
        ∃ c, C.enabled ((CircularConsumerBridge.completeSystem E).eval h₁) c ≠
          C.enabled ((CircularConsumerBridge.completeSystem E).eval h₂) c := by
  rw [Consumer.guardCondition_toCheckSpec_iff C
    (CircularConsumerBridge.completeSystem E) hregistered]
  have hcompressed := CheckSpec.compressed_guard_failure_iff
    C.toCheckSpec (CircularConsumerBridge.completeSystem E) id
    (c1QuadraticHistoryBudget n)
    (c1QuadraticReplacement E h hn)
    (c1CheckSpecFactorization E C)
  simpa [Consumer.toCheckSpec, Consumer.sameFiber, CheckSpec.guardCollision,
    CheckSpec.sameFiber] using hcompressed

theorem c1_registered_successor_failure_quadratic
    [NeZero n] (E : CircularEnvironment n m) (h : C1Compatible E)
    (hn : 3 ≤ n) (C : C1Consumer n m Cmd V O)
    (hregistered : C.DomainReachable
      (CircularConsumerBridge.completeSystem E))
    (hfail : ¬ C.T (CircularLogState.rawSystem E)) :
    ∃ h₁ h₂ c,
      h₁.length ≤ c1QuadraticHistoryBudget n ∧
      h₂.length ≤ c1QuadraticHistoryBudget n ∧
      C.sameFiber
        ((CircularConsumerBridge.completeSystem E).eval h₁)
        ((CircularConsumerBridge.completeSystem E).eval h₂) ∧
      C.enabled ((CircularConsumerBridge.completeSystem E).eval h₁) c = true ∧
      C.enabled ((CircularConsumerBridge.completeSystem E).eval h₂) c = true ∧
      (h₁ ++ [C.letter c]).length ≤ c1QuadraticHistoryBudget n + 1 ∧
      (h₂ ++ [C.letter c]).length ≤ c1QuadraticHistoryBudget n + 1 ∧
      C.candidate ((CircularConsumerBridge.completeSystem E).eval
        (h₁ ++ [C.letter c])) ≠
        C.candidate ((CircularConsumerBridge.completeSystem E).eval
          (h₂ ++ [C.letter c])) := by
  have hspec := Consumer.successorCondition_toCheckSpec_iff C
    (CircularConsumerBridge.completeSystem E) hregistered
  rw [CircularConsumerBridge.completeSystem_step E] at hspec
  have hcheck : ¬ C.toCheckSpec.successorCondition
      (CircularConsumerBridge.completeSystem E) := by
    intro hgood
    apply hfail
    exact hspec.mpr hgood
  obtain ⟨h₁, h₂, c, hh₁, hh₂, hf, hc₁, hc₂, hlen₁, hlen₂, hnext⟩ :=
    CheckSpec.compressed_successor_certificate
      C.toCheckSpec (CircularConsumerBridge.completeSystem E) id
      (c1QuadraticHistoryBudget n)
      (c1QuadraticReplacement E h hn)
      (c1CheckSpecFactorization E C) hcheck
  refine ⟨h₁, h₂, c, hh₁, hh₂, ?_, hc₁, hc₂, hlen₁, hlen₂, ?_⟩
  · simpa [Consumer.toCheckSpec, Consumer.sameFiber, CheckSpec.sameFiber] using hf
  · simpa [Consumer.toCheckSpec, CircularConsumerBridge.completeSystem] using hnext

end PaperXL
