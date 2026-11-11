import PaperXL.ConsumerBridge
import RGTBoundedHistory.ObservationCompression

/-!
# Consumer factorization through the declared circular log endpoint

The observation contains the complete ordered event-code list and every
atom's terminal site. Environment parameters and invocation data (such as a
fixed selected block) are parameters of the consumer built on this view.
-/

namespace PaperXL

open RGTBoundedHistory

universe u v w x y

variable {n m : Nat} {Cmd : Type u} {V : Type v} {O : Type w}

/-- The lossless complete-log/literal-endpoint view of a circular state. -/
structure CircularLogEndpoint where
  events : List (EventCode m)
  site : Fin m → Fin n

namespace CircularLogEndpoint

def observe (s : CircularLogState n m) : CircularLogEndpoint (n := n) (m := m) :=
  ⟨s.events, s.site⟩

def decode (o : CircularLogEndpoint (n := n) (m := m)) :
    CircularLogState n m :=
  ⟨o.site, o.events⟩

@[simp] theorem decode_observe (s : CircularLogState n m) :
    decode (observe s) = s := by
  cases s
  rfl

@[simp] theorem observe_decode (o : CircularLogEndpoint (n := n) (m := m)) :
    observe (decode o) = o := by
  cases o
  rfl

theorem observe_injective : Function.Injective (observe (n := n) (m := m)) := by
  intro s t h
  apply CircularLogState.ext
  · exact congrArg CircularLogEndpoint.site h
  · exact congrArg CircularLogEndpoint.events h

end CircularLogEndpoint

namespace CircularLogState

def observeConsumer (C : Consumer (CircularLogState n m) RawLetter Cmd V O) :
    Consumer (CircularLogEndpoint (n := n) (m := m)) RawLetter Cmd V O where
  domain o := C.domain (CircularLogEndpoint.decode o)
  candidate o := C.candidate (CircularLogEndpoint.decode o)
  report o := C.report (CircularLogEndpoint.decode o)
  enabled o c := C.enabled (CircularLogEndpoint.decode o) c
  letter := C.letter

theorem lift_observeConsumer (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (s : CircularLogState n m) :
    (observeConsumer C).domain (CircularLogEndpoint.observe s) = C.domain s := by
  simp [observeConsumer]

theorem candidate_observeConsumer
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (s : CircularLogState n m) :
    (observeConsumer C).candidate (CircularLogEndpoint.observe s) = C.candidate s := by
  simp [observeConsumer]

theorem report_observeConsumer
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (s : CircularLogState n m) :
    (observeConsumer C).report (CircularLogEndpoint.observe s) = C.report s := by
  simp [observeConsumer]

theorem enabled_observeConsumer
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (s : CircularLogState n m) (c : Cmd) :
    (observeConsumer C).enabled (CircularLogEndpoint.observe s) c = C.enabled s c := by
  simp [observeConsumer]

end CircularLogState

/-- Every Paper XL consumer on the declared circular complete state factors
through the complete event-log/literal-endpoint view. Fixed environment and
invocation values remain parameters of `C`; no lossy consumer quotient is
asserted here. -/
theorem circularConsumer_factors_through_log_endpoint
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O) :
    CheckSpecObservationFactorization C.toCheckSpec
      (CircularConsumerBridge.completeSystem E)
      (CircularLogEndpoint.observe (n := n) (m := m)) where
  domain s t h := by
    have heq : s = t := CircularLogEndpoint.observe_injective h
    rw [heq]
  candidate s t h := by
    have heq : s = t := CircularLogEndpoint.observe_injective h
    rw [heq]
  report s t h := by
    have heq : s = t := CircularLogEndpoint.observe_injective h
    rw [heq]
  enabled s t h c := by
    have heq : s = t := CircularLogEndpoint.observe_injective h
    rw [heq]
  step s t h a := by
    have heq : s = t := CircularLogEndpoint.observe_injective h
    rw [heq]

theorem circularConsumer_factors_of_exact_components
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (B : Nat) (K : CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site) :
    CheckSpecObservationFactorization C.toCheckSpec
      (CircularConsumerBridge.completeSystem E) K.observation := by
  have F := circularConsumer_factors_through_log_endpoint E C
  have observe_eq_of_components {s t : CircularLogState n m}
      (h : K.observation s = K.observation t) :
      CircularLogEndpoint.observe s = CircularLogEndpoint.observe t := by
    have hlogs : K.completeLog s = K.completeLog t := congrArg Prod.fst h
    have hsites : K.endpoint s = K.endpoint t := congrArg Prod.snd h
    rw [hlog s, hlog t] at hlogs
    rw [hend s, hend t] at hsites
    cases s with
    | mk ss se =>
      cases t with
      | mk ts te =>
        cases hlogs
        cases hsites
        rfl
  refine {
    domain := ?_
    candidate := ?_
    report := ?_
    enabled := ?_
    step := ?_
  }
  · intro s t h
    exact F.domain s t (observe_eq_of_components h)
  · intro s t h
    exact F.candidate s t (observe_eq_of_components h)
  · intro s t h
    exact F.report s t (observe_eq_of_components h)
  · intro s t h c
    exact F.enabled s t (observe_eq_of_components h) c
  · intro s t h a
    have heq : s = t := by
      apply CircularLogEndpoint.observe_injective
      exact observe_eq_of_components h
    subst t
    rfl

/-- The existing finite-code loop erasure, viewed as a compressor preserving
the exact complete event list and terminal site map. This supplies the
large finite bound for the concrete circular model, not the quadratic C1
bound. -/
def circularFiniteLogEndpointCompression (E : CircularEnvironment n m) :
    CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n)
      (logBound n m - 1) where
  completeLog s := s.events
  endpoint s := s.site
  replace h := by
    obtain ⟨k, heq, hk⟩ := (completeLogEncoding E).bounded_replacement h
    refine ⟨k, hk, ?_, ?_⟩
    · exact congrArg CircularLogState.events heq
    · exact congrArg CircularLogState.site heq

@[simp] theorem circularFiniteLogEndpointCompression_log (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    (circularFiniteLogEndpointCompression E).completeLog s = s.events := rfl

@[simp] theorem circularFiniteLogEndpointCompression_endpoint
    (E : CircularEnvironment n m) (s : CircularLogState n m) :
    (circularFiniteLogEndpointCompression E).endpoint s = s.site := rfl

/-- Conditional C1-style transport for any concrete consumer on the circular
complete state. Supplying `K` is the explicit remaining compressor/model
connection; the consumer-factorization premise is discharged above. -/
theorem circular_consumer_compressed_read_failure_iff
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (B : Nat)
    (K : CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site) :
    ¬ (C.toCheckSpec).readCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        (C.toCheckSpec).readCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) := by
  exact CheckSpec.completeLogEndpoint_compressed_read_failure_iff
    C.toCheckSpec (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B K
    (circularConsumer_factors_of_exact_components E C B K hlog hend)

theorem circular_consumer_compressed_guard_failure_iff
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (B : Nat)
    (K : CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site) :
    ¬ (C.toCheckSpec).guardCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        (C.toCheckSpec).guardCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) := by
  exact CheckSpec.completeLogEndpoint_compressed_guard_failure_iff
    C.toCheckSpec (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B K
    (circularConsumer_factors_of_exact_components E C B K hlog hend)

theorem circular_consumer_compressed_successor_failure_certificate
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (B : Nat)
    (K : CompleteLogEndpointCompression
      (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B)
    (hlog : ∀ s, K.completeLog s = s.events)
    (hend : ∀ s, K.endpoint s = s.site)
    (hfail : ¬ (C.toCheckSpec).successorCondition
      (CircularConsumerBridge.completeSystem E)) :
    ∃ h k c,
      h.length ≤ B ∧ k.length ≤ B ∧
      (C.toCheckSpec).sameFiber
        ((CircularConsumerBridge.completeSystem E).eval h)
        ((CircularConsumerBridge.completeSystem E).eval k) ∧
      (C.toCheckSpec).enabled
        ((CircularConsumerBridge.completeSystem E).eval h) c = true ∧
      (C.toCheckSpec).enabled
        ((CircularConsumerBridge.completeSystem E).eval k) c = true ∧
      (h ++ [(C.toCheckSpec).letter c]).length ≤ B + 1 ∧
      (k ++ [(C.toCheckSpec).letter c]).length ≤ B + 1 ∧
      (C.toCheckSpec).candidate
        ((CircularConsumerBridge.completeSystem E).eval
          (h ++ [(C.toCheckSpec).letter c])) ≠
      (C.toCheckSpec).candidate
        ((CircularConsumerBridge.completeSystem E).eval
          (k ++ [(C.toCheckSpec).letter c])) := by
  exact CheckSpec.completeLogEndpoint_compressed_successor_certificate
    C.toCheckSpec (CircularConsumerBridge.completeSystem E)
      (List (EventCode m)) (Fin m → Fin n) B K
    (circularConsumer_factors_of_exact_components E C B K hlog hend) hfail

/-- The model's already-proved finite-code compressor instantiated with the
exact event-list and endpoint-site components. -/
theorem circular_consumer_finite_read_failure_iff
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O) :
    ¬ (C.toCheckSpec).readCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k,
        h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        (C.toCheckSpec).readCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) := by
  exact circular_consumer_compressed_read_failure_iff E C
    (logBound n m - 1) (circularFiniteLogEndpointCompression E)
    (by intro s; rfl) (by intro s; rfl)

theorem circular_consumer_finite_guard_failure_iff
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O) :
    ¬ (C.toCheckSpec).guardCondition (CircularConsumerBridge.completeSystem E) ↔
      ∃ h k,
        h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        (C.toCheckSpec).guardCollision
          ((CircularConsumerBridge.completeSystem E).eval h)
          ((CircularConsumerBridge.completeSystem E).eval k) := by
  exact circular_consumer_compressed_guard_failure_iff E C
    (logBound n m - 1) (circularFiniteLogEndpointCompression E)
    (by intro s; rfl) (by intro s; rfl)

theorem circular_consumer_finite_successor_failure_certificate
    (E : CircularEnvironment n m)
    (C : Consumer (CircularLogState n m) RawLetter Cmd V O)
    (hfail : ¬ (C.toCheckSpec).successorCondition
      (CircularConsumerBridge.completeSystem E)) :
    ∃ h k c,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
      (C.toCheckSpec).sameFiber
        ((CircularConsumerBridge.completeSystem E).eval h)
        ((CircularConsumerBridge.completeSystem E).eval k) ∧
      (C.toCheckSpec).enabled
        ((CircularConsumerBridge.completeSystem E).eval h) c = true ∧
      (C.toCheckSpec).enabled
        ((CircularConsumerBridge.completeSystem E).eval k) c = true ∧
      (h ++ [(C.toCheckSpec).letter c]).length ≤ logBound n m ∧
      (k ++ [(C.toCheckSpec).letter c]).length ≤ logBound n m ∧
      (C.toCheckSpec).candidate
        ((CircularConsumerBridge.completeSystem E).eval
          (h ++ [(C.toCheckSpec).letter c])) ≠
      (C.toCheckSpec).candidate
        ((CircularConsumerBridge.completeSystem E).eval
          (k ++ [(C.toCheckSpec).letter c])) := by
  obtain ⟨h, k, c, hh, hk, hf, hc, hc', hlen, klen, hnext⟩ :=
    circular_consumer_compressed_successor_failure_certificate E C
      (logBound n m - 1) (circularFiniteLogEndpointCompression E)
      (by intro s; rfl) (by intro s; rfl) hfail
  have hpos := (completeLogEncoding E).system.cover_positive
  have hlenB : 0 < logBound n m := by
    rw [← (completeLogEncoding E).system_cover_length]
    exact hpos
  refine ⟨h, k, c, hh, hk, hf, hc, hc', ?_, ?_, hnext⟩
  · simp only [List.length_append, List.length_singleton] at hlen ⊢
    omega
  · simp only [List.length_append, List.length_singleton] at klen ⊢
    omega

end PaperXL
