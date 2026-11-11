import PaperXL.Consumer
import PaperXL.BoundedHistory

/-!
# Consumer bridge to complete-log checking

This module converts a Paper XL consumer on complete states into the reusable
history-quantified `CheckSpec`.  The reverse implication uses an explicit
reachability premise for every state in the consumer's registered domain.
Completeness of a finite cover alone does not establish that premise.
-/

namespace PaperXL

open RGTBoundedHistory

universe u v w x y z

variable {S : Type u} {A : Type v} {Cmd : Type w} {V : Type x} {O : Type y}

namespace Consumer

/-- View the single report value as the consumer's tuple of declared reports. -/
def toCheckSpec (C : Consumer S A Cmd V O) : CheckSpec S A Cmd V O :=
  { domain := C.domain
    candidate := C.candidate
    report := C.report
    enabled := C.enabled
    letter := C.letter }

@[simp] theorem sameFiber_toCheckSpec (C : Consumer S A Cmd V O) (s t : S) :
    (C.toCheckSpec).sameFiber s t = C.sameFiber s t := rfl

/-- Every consumer-domain complete state is represented by a generated history. -/
def DomainReachable (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) : Prop :=
  ∀ s, C.domain s → ∃ h : List A, G.eval h = s

theorem readCondition_toCheckSpec_of_R (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hR : C.R) :
    (C.toCheckSpec).readCondition G := by
  intro h k hf
  exact hR (G.eval h) (G.eval k) hf

theorem guardCondition_toCheckSpec_of_G (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hG : C.G) :
    (C.toCheckSpec).guardCondition G := by
  intro h k hf c
  exact hG (G.eval h) (G.eval k) hf c

theorem successorCondition_toCheckSpec_of_T (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hT : C.T ⟨G.step, G.seed⟩) :
    (C.toCheckSpec).successorCondition G := by
  intro h k hf c hc hc'
  exact hT (G.eval h) (G.eval k) hf c hc hc'

theorem readCondition_toCheckSpec_iff (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hreach : C.DomainReachable G) :
    C.R ↔ (C.toCheckSpec).readCondition G := by
  constructor
  · exact readCondition_toCheckSpec_of_R C G
  · intro hcheck s t hst
    obtain ⟨hs, hse⟩ := hreach s hst.1
    obtain ⟨ht, hte⟩ := hreach t hst.2.1
    have hf : (C.toCheckSpec).sameFiber (G.eval hs) (G.eval ht) := by
      simpa [hse, hte] using hst
    have hr := hcheck hs ht hf
    simpa [toCheckSpec, hse, hte] using hr

theorem guardCondition_toCheckSpec_iff (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hreach : C.DomainReachable G) :
    C.G ↔ (C.toCheckSpec).guardCondition G := by
  constructor
  · exact guardCondition_toCheckSpec_of_G C G
  · intro hcheck s t hst c
    obtain ⟨hs, hse⟩ := hreach s hst.1
    obtain ⟨ht, hte⟩ := hreach t hst.2.1
    have hf : (C.toCheckSpec).sameFiber (G.eval hs) (G.eval ht) := by
      simpa [hse, hte] using hst
    have hg := hcheck hs ht hf c
    simpa [toCheckSpec, hse, hte] using hg

theorem successorCondition_toCheckSpec_iff (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hreach : C.DomainReachable G) :
    C.T ⟨G.step, G.seed⟩ ↔ (C.toCheckSpec).successorCondition G := by
  constructor
  · exact successorCondition_toCheckSpec_of_T C G
  · intro hcheck s t hst c hc hc'
    obtain ⟨hs, hse⟩ := hreach s hst.1
    obtain ⟨ht, hte⟩ := hreach t hst.2.1
    have hf : (C.toCheckSpec).sameFiber (G.eval hs) (G.eval ht) := by
      simpa [hse, hte] using hst
    have hc₁ : (C.toCheckSpec).enabled (G.eval hs) c = true := by
      simpa [toCheckSpec, hse] using hc
    have hc₂ : (C.toCheckSpec).enabled (G.eval ht) c = true := by
      simpa [toCheckSpec, hte] using hc'
    have hsuc := hcheck hs ht hf c hc₁ hc₂
    simpa [toCheckSpec, hse, hte] using hsuc

theorem RGT_toCheckSpec_iff (C : Consumer S A Cmd V O)
    (G : FiniteSystem S A) (hreach : C.DomainReachable G) :
    C.R ∧ C.G ∧ C.T ⟨G.step, G.seed⟩ ↔
      (C.toCheckSpec).readCondition G ∧
        (C.toCheckSpec).guardCondition G ∧
        (C.toCheckSpec).successorCondition G := by
  rw [readCondition_toCheckSpec_iff C G hreach,
    guardCondition_toCheckSpec_iff C G hreach,
    successorCondition_toCheckSpec_iff C G hreach]

end Consumer

/-! A consumer can live on a causal/registered state type distinct from the
complete log state.  The following structure records exactly the bridge data
needed to pull that consumer back to complete logs. -/

structure ConsumerLogBridge {S : Type u} {T : Type x} {A : Type v}
    {Cmd : Type w} {V : Type y} {O : Type z}
    (G : FiniteSystem S A) (M : RawSystem T A)
    (C : Consumer T A Cmd V O) where
  project : S → T
  registered : S → Prop
  registered_iff_domain : ∀ s, registered s ↔ C.domain (project s)
  step_commutes : ∀ s a, project (G.step s a) = M.step (project s) a
  realizes_domain : ∀ t, C.domain t →
    ∃ h : List A, registered (G.eval h) ∧ project (G.eval h) = t

namespace ConsumerLogBridge

variable {S : Type u} {T : Type x} {A : Type v} {Cmd : Type w}
  {V : Type y} {O : Type z}
variable {G : FiniteSystem S A} {M : RawSystem T A}
variable {C : Consumer T A Cmd V O}
variable (B : ConsumerLogBridge G M C)

/-- Pull the registered consumer's outputs and candidate back to complete logs. -/
def toCheckSpec : CheckSpec S A Cmd V O :=
  { domain := B.registered
    candidate := fun s => C.candidate (B.project s)
    report := fun s => C.report (B.project s)
    enabled := fun s c => C.enabled (B.project s) c
    letter := C.letter }

@[simp] theorem sameFiber_iff (s t : S) :
    (B.toCheckSpec).sameFiber s t ↔
      C.sameFiber (B.project s) (B.project t) := by
  simp [toCheckSpec, Consumer.sameFiber, CheckSpec.sameFiber,
    B.registered_iff_domain]

theorem readCondition_iff :
    C.R ↔ (B.toCheckSpec).readCondition G := by
  constructor
  · intro hR h k hf
    exact hR _ _ ((B.sameFiber_iff _ _).mp hf)
  · intro hcheck x y hxy
    obtain ⟨hx, hxr, hxp⟩ := B.realizes_domain x hxy.1
    obtain ⟨hy, hyr, hyp⟩ := B.realizes_domain y hxy.2.1
    have hf : (B.toCheckSpec).sameFiber (G.eval hx) (G.eval hy) := by
      apply (B.sameFiber_iff _ _).2
      simpa [hxp, hyp] using hxy
    have hr := hcheck hx hy hf
    simpa [toCheckSpec, hxp, hyp] using hr

theorem guardCondition_iff :
    C.G ↔ (B.toCheckSpec).guardCondition G := by
  constructor
  · intro hG h k hf c
    exact hG _ _ ((B.sameFiber_iff _ _).mp hf) c
  · intro hcheck x y hxy c
    obtain ⟨hx, hxr, hxp⟩ := B.realizes_domain x hxy.1
    obtain ⟨hy, hyr, hyp⟩ := B.realizes_domain y hxy.2.1
    have hf : (B.toCheckSpec).sameFiber (G.eval hx) (G.eval hy) := by
      apply (B.sameFiber_iff _ _).2
      simpa [hxp, hyp] using hxy
    have hg := hcheck hx hy hf c
    simpa [toCheckSpec, hxp, hyp] using hg

theorem successorCondition_iff :
    C.T M ↔ (B.toCheckSpec).successorCondition G := by
  constructor
  · intro hT h k hf c hc hc'
    have hf' := (B.sameFiber_iff _ _).mp hf
    have ht := hT _ _ hf' c hc hc'
    simpa [toCheckSpec, B.step_commutes] using ht
  · intro hcheck x y hxy c hc hc'
    obtain ⟨hx, hxr, hxp⟩ := B.realizes_domain x hxy.1
    obtain ⟨hy, hyr, hyp⟩ := B.realizes_domain y hxy.2.1
    have hf : (B.toCheckSpec).sameFiber (G.eval hx) (G.eval hy) := by
      apply (B.sameFiber_iff _ _).2
      simpa [hxp, hyp] using hxy
    have hc₁ : (B.toCheckSpec).enabled (G.eval hx) c = true := by
      simpa [toCheckSpec, hxp] using hc
    have hc₂ : (B.toCheckSpec).enabled (G.eval hy) c = true := by
      simpa [toCheckSpec, hyp] using hc'
    have ht := hcheck hx hy hf c hc₁ hc₂
    simpa [toCheckSpec, hxp, hyp, B.step_commutes] using ht

theorem RGT_iff :
    C.R ∧ C.G ∧ C.T M ↔
      (B.toCheckSpec).readCondition G ∧
        (B.toCheckSpec).guardCondition G ∧
        (B.toCheckSpec).successorCondition G := by
  rw [readCondition_iff B, guardCondition_iff B, successorCondition_iff B]

end ConsumerLogBridge

namespace CircularConsumerBridge

variable {n m : Nat} {Cmd : Type u} {V : Type v} {O : Type w}

abbrev CompleteState := CircularLogState n m

/-- A consumer whose domain predicate identifies its registered complete states. -/
abbrev RegisteredConsumer (Cmd : Type u) (V : Type v) (O : Type w) :=
  PaperXL.Consumer (CompleteState (n := n) (m := m)) RawLetter Cmd V O

def completeSystem (E : CircularEnvironment n m) :
    FiniteSystem (CompleteState (n := n) (m := m)) RawLetter :=
  (completeLogEncoding E).system

theorem completeSystem_step (E : CircularEnvironment n m) :
    (completeSystem E).step = (CircularLogState.rawSystem E).step := rfl

theorem eval_append_letter (E : CircularEnvironment n m)
    (h : List RawLetter) (a : RawLetter) :
    (completeSystem E).eval (h ++ [a]) =
      (completeSystem E).step ((completeSystem E).eval h) a := by
  simp [completeSystem, FiniteSystem.eval, run_append, run]

theorem registered_RGT_iff_checkSpec
    (E : CircularEnvironment n m)
    (C : RegisteredConsumer Cmd V O (n := n) (m := m))
    (hregistered : C.DomainReachable (completeSystem E)) :
    C.R ∧ C.G ∧
        C.T (CircularLogState.rawSystem E) ↔
      (C.toCheckSpec).readCondition (completeSystem E) ∧
        (C.toCheckSpec).guardCondition (completeSystem E) ∧
        (C.toCheckSpec).successorCondition (completeSystem E) := by
  have hstep : (completeSystem E).step = (CircularLogState.rawSystem E).step := rfl
  have hseed : (completeSystem E).seed = (CircularLogState.rawSystem E).seed := rfl
  cases hstep
  cases hseed
  exact Consumer.RGT_toCheckSpec_iff C (completeSystem E) hregistered

theorem registered_read_failure_bounded
    (E : CircularEnvironment n m)
    (C : RegisteredConsumer Cmd V O (n := n) (m := m))
    (hregistered : C.DomainReachable (completeSystem E)) :
    ¬ C.R ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.sameFiber ((completeSystem E).eval h) ((completeSystem E).eval k) ∧
        C.report ((completeSystem E).eval h) ≠ C.report ((completeSystem E).eval k) := by
  rw [Consumer.readCondition_toCheckSpec_iff C (completeSystem E) hregistered]
  exact (completeLogEncoding E).bounded_read_failure_iff C.toCheckSpec

theorem registered_guard_failure_bounded
    (E : CircularEnvironment n m)
    (C : RegisteredConsumer Cmd V O (n := n) (m := m))
    (hregistered : C.DomainReachable (completeSystem E)) :
    ¬ C.G ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.sameFiber ((completeSystem E).eval h) ((completeSystem E).eval k) ∧
        ∃ c, C.enabled ((completeSystem E).eval h) c ≠
          C.enabled ((completeSystem E).eval k) c := by
  rw [Consumer.guardCondition_toCheckSpec_iff C (completeSystem E) hregistered]
  exact (completeLogEncoding E).bounded_guard_failure_iff C.toCheckSpec

theorem registered_successor_failure_bounded
    (E : CircularEnvironment n m)
    (C : RegisteredConsumer Cmd V O (n := n) (m := m))
    (hregistered : C.DomainReachable (completeSystem E)) :
    ¬ C.T (CircularLogState.rawSystem E) ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.sameFiber ((completeSystem E).eval h) ((completeSystem E).eval k) ∧
        ∃ c,
          C.enabled ((completeSystem E).eval h) c = true ∧
          C.enabled ((completeSystem E).eval k) c = true ∧
          C.candidate ((completeSystem E).eval (h ++ [C.letter c])) ≠
            C.candidate ((completeSystem E).eval (k ++ [C.letter c])) := by
  have hstep := completeSystem_step E
  have hspec := Consumer.successorCondition_toCheckSpec_iff C
    (completeSystem E) hregistered
  rw [hstep] at hspec
  constructor
  · intro hfail
    have hcheck : ¬ (C.toCheckSpec).successorCondition (completeSystem E) :=
      fun hgood => hfail (hspec.mpr hgood)
    obtain ⟨h, k, hh, hk, hcollision⟩ :=
      ((completeLogEncoding E).bounded_successor_failure_iff C.toCheckSpec).mp hcheck
    rcases hcollision with ⟨hf, c, hc, hc', hneq⟩
    have hneq' :
        C.candidate ((completeSystem E).step ((completeSystem E).eval h) (C.letter c)) ≠
          C.candidate ((completeSystem E).step ((completeSystem E).eval k) (C.letter c)) := by
      simpa [completeSystem, Consumer.toCheckSpec] using hneq
    refine ⟨h, k, hh, hk, hf, c, hc, hc', ?_⟩
    rw [eval_append_letter E h (C.letter c), eval_append_letter E k (C.letter c)]
    exact hneq'
  · rintro ⟨h, k, hh, hk, hf, c, hc, hc', hneq⟩ hgood
    have hcheck := hspec.mp hgood
    have hsucc := hcheck h k hf c hc hc'
    have hsucc' :
        C.candidate ((completeSystem E).step ((completeSystem E).eval h) (C.letter c)) =
          C.candidate ((completeSystem E).step ((completeSystem E).eval k) (C.letter c)) := by
      simpa [completeSystem, Consumer.toCheckSpec] using hsucc
    rw [eval_append_letter E h (C.letter c), eval_append_letter E k (C.letter c)] at hneq
    exact hneq hsucc'

end CircularConsumerBridge

end PaperXL
