import PaperXL.CircularObservation

/-! Kernel-checked generic instantiation of the circular consumer bridge. -/

namespace PaperXL.CircularObservationChecks

open RGTBoundedHistory

variable {n m : Nat} {Cmd : Type} {V : Type} {O : Type}
variable (E : CircularEnvironment n m)
variable (C : Consumer (CircularLogState n m) RawLetter Cmd V O)

example : CheckSpecObservationFactorization C.toCheckSpec
    (CircularConsumerBridge.completeSystem E)
    (CircularLogEndpoint.observe (n := n) (m := m)) :=
  circularConsumer_factors_through_log_endpoint E C

example (B : Nat)
    (K : RGTBoundedHistory.CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site) :
    CheckSpecObservationFactorization C.toCheckSpec
      (CircularConsumerBridge.completeSystem E) K.observation := by
  apply circularConsumer_factors_of_exact_components E C B K
  · exact hlog
  · exact hend

example (B : Nat)
    (K : RGTBoundedHistory.CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site) :
    ¬ C.toCheckSpec.readCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.toCheckSpec.readCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) :=
  circular_consumer_compressed_read_failure_iff E C B K hlog hend

example : ∀ s : CircularLogState n m,
    (circularFiniteLogEndpointCompression E).completeLog s = s.events ∧
      (circularFiniteLogEndpointCompression E).endpoint s = s.site := by
  intro s
  exact ⟨rfl, rfl⟩

example :
    ¬ C.toCheckSpec.readCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.toCheckSpec.readCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) :=
  circular_consumer_finite_read_failure_iff E C

end PaperXL.CircularObservationChecks
