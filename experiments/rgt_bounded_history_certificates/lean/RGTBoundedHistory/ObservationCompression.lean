import RGTBoundedHistory.Certificates

/-!
# R/G/T certificates under observation-preserving history compression

The compressor may preserve a semantic observation rather than the consumer's
entire implementation state. The factorization structure states exactly what
must pass through that observation, including closure under a common raw step.
-/

namespace RGTBoundedHistory

universe u v w z t x

variable {S : Type u} {A : Type v} {Cmd : Type w}
  {V : Type z} {O : Type t} {X : Type x}

structure BoundedObservationReplacement
    (M : FiniteSystem S A) (observe : S → X) (B : Nat) where
  replace : ∀ h : List A, ∃ k : List A,
    k.length ≤ B ∧ observe (M.eval k) = observe (M.eval h)

/-- A compression theorem preserving the complete event log and literal
terminal endpoint. The observation is their ordered pair. -/
structure CompleteLogEndpointCompression
    (M : FiniteSystem S A) (Log Endpoint : Type x) (B : Nat) where
  completeLog : S → Log
  endpoint : S → Endpoint
  replace : ∀ h : List A, ∃ k : List A,
    k.length ≤ B ∧
      completeLog (M.eval k) = completeLog (M.eval h) ∧
      endpoint (M.eval k) = endpoint (M.eval h)

namespace CompleteLogEndpointCompression

variable {M : FiniteSystem S A} {Log Endpoint : Type x} {B : Nat}
variable (K : CompleteLogEndpointCompression M Log Endpoint B)

def observation (s : S) : Log × Endpoint := (K.completeLog s, K.endpoint s)

theorem toBoundedObservationReplacement :
    BoundedObservationReplacement M K.observation B where
  replace h := by
    obtain ⟨k, hk, hlog, hend⟩ := K.replace h
    exact ⟨k, hk, Prod.ext hlog hend⟩

end CompleteLogEndpointCompression

structure CheckSpecObservationFactorization
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (observe : S → X) where
  domain : ∀ s t, observe s = observe t → (C.domain s ↔ C.domain t)
  candidate : ∀ s t, observe s = observe t → C.candidate s = C.candidate t
  report : ∀ s t, observe s = observe t → C.report s = C.report t
  enabled : ∀ s t (_h : observe s = observe t) (c : Cmd),
    C.enabled s c = C.enabled t c
  step : ∀ s t (_h : observe s = observe t) (a : A),
    observe (M.step s a) = observe (M.step t a)

namespace CheckSpecObservationFactorization

theorem identity (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A) :
    CheckSpecObservationFactorization C M id where
  domain s t h := by cases h; exact Iff.rfl
  candidate s t h := by cases h; rfl
  report s t h := by cases h; rfl
  enabled s t h _ := by cases h; rfl
  step s t h a := by cases h; rfl

end CheckSpecObservationFactorization

namespace FiniteSystem

theorem identityBoundedObservationReplacement (M : FiniteSystem S A) :
    BoundedObservationReplacement M id (M.cover.length - 1) where
  replace h := by
    obtain ⟨k, hk, hlen⟩ := M.bounded_replacement_le h
    exact ⟨k, hlen, hk⟩

end FiniteSystem

namespace CheckSpecObservationFactorization

variable {C : CheckSpec S A Cmd V O} {M : FiniteSystem S A}
  {observe : S → X}
variable (F : CheckSpecObservationFactorization C M observe)

theorem readCollision_transfer (F : CheckSpecObservationFactorization C M observe)
    {s t s' t' : S}
    (hs : observe s = observe s') (ht : observe t = observe t')
    (hcol : C.readCollision s t) : C.readCollision s' t' := by
  rcases hcol with ⟨⟨hds, hdt, hcan⟩, hrep⟩
  refine ⟨?_, ?_⟩
  · refine ⟨(F.domain s s' hs).mp hds, (F.domain t t' ht).mp hdt, ?_⟩
    calc
      C.candidate s' = C.candidate s :=
        (F.candidate s s' hs).symm
      _ = C.candidate t := hcan
      _ = C.candidate t' := F.candidate t t' ht
  · intro heq
    apply hrep
    calc
      C.report s = C.report s' := F.report s s' hs
      _ = C.report t' := heq
      _ = C.report t := (F.report t t' ht).symm

theorem guardCollision_transfer (F : CheckSpecObservationFactorization C M observe)
    {s t s' t' : S}
    (hs : observe s = observe s') (ht : observe t = observe t')
    (hcol : C.guardCollision s t) : C.guardCollision s' t' := by
  rcases hcol with ⟨⟨hds, hdt, hcan⟩, c, hguard⟩
  refine ⟨?_, c, ?_⟩
  · refine ⟨(F.domain s s' hs).mp hds, (F.domain t t' ht).mp hdt, ?_⟩
    calc
      C.candidate s' = C.candidate s :=
        (F.candidate s s' hs).symm
      _ = C.candidate t := hcan
      _ = C.candidate t' := F.candidate t t' ht
  · intro heq
    apply hguard
    calc
      C.enabled s c = C.enabled s' c := F.enabled s s' hs c
      _ = C.enabled t' c := heq
      _ = C.enabled t c := (F.enabled t t' ht c).symm

theorem successorCollision_transfer (F : CheckSpecObservationFactorization C M observe)
    {s t s' t' : S}
    (hs : observe s = observe s') (ht : observe t = observe t')
    (hcol : C.successorCollision M s t) : C.successorCollision M s' t' := by
  rcases hcol with ⟨⟨hds, hdt, hcan⟩, c, hcs, hct, hnext⟩
  refine ⟨?_, c, ?_, ?_, ?_⟩
  · refine ⟨(F.domain s s' hs).mp hds, (F.domain t t' ht).mp hdt, ?_⟩
    calc
      C.candidate s' = C.candidate s :=
        (F.candidate s s' hs).symm
      _ = C.candidate t := hcan
      _ = C.candidate t' := F.candidate t t' ht
  · rw [(F.enabled s s' hs c).symm]
    exact hcs
  · rw [(F.enabled t t' ht c).symm]
    exact hct
  · intro heq
    apply hnext
    calc
      C.candidate (M.step s (C.letter c)) =
          C.candidate (M.step s' (C.letter c)) := by
        apply F.candidate _ _ (F.step s s' hs (C.letter c))
      _ = C.candidate (M.step t' (C.letter c)) := heq
      _ = C.candidate (M.step t (C.letter c)) := by
        apply (F.candidate _ _ (F.step t t' ht (C.letter c))).symm

end CheckSpecObservationFactorization

namespace CheckSpec

/-- A failed read clause has two observation-equivalent replacements of length
at most `B`, still witnessing the report mismatch. -/
theorem compressed_read_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (observe : S → X) (B : Nat)
    (R : BoundedObservationReplacement M observe B)
    (F : CheckSpecObservationFactorization C M observe) :
    ¬ C.readCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.readCollision (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hcol⟩ := (C.read_failure_iff M).mp hfail
    obtain ⟨h', hh', hs⟩ := BoundedObservationReplacement.replace R h
    obtain ⟨k', hk', ht⟩ := BoundedObservationReplacement.replace R k
    exact ⟨h', k', hh', hk',
      F.readCollision_transfer hs.symm ht.symm hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.read_failure_iff M).mpr ⟨h, k, hcol⟩

/-- A failed guard clause has two observation-equivalent replacements of
length at most `B`, still witnessing the enabledness mismatch. -/
theorem compressed_guard_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (observe : S → X) (B : Nat)
    (R : BoundedObservationReplacement M observe B)
    (F : CheckSpecObservationFactorization C M observe) :
    ¬ C.guardCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.guardCollision (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hcol⟩ := (C.guard_failure_iff M).mp hfail
    obtain ⟨h', hh', hs⟩ := BoundedObservationReplacement.replace R h
    obtain ⟨k', hk', ht⟩ := BoundedObservationReplacement.replace R k
    exact ⟨h', k', hh', hk',
    F.guardCollision_transfer hs.symm ht.symm hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.guard_failure_iff M).mpr ⟨h, k, hcol⟩

/-- A failed successor clause has bounded prehistories; the common command is
still enabled and separates the candidates after one common raw letter. -/
theorem compressed_successor_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (observe : S → X) (B : Nat)
    (R : BoundedObservationReplacement M observe B)
    (F : CheckSpecObservationFactorization C M observe) :
    ¬ C.successorCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.successorCollision M (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hcol⟩ := (C.successor_failure_iff M).mp hfail
    obtain ⟨h', hh', hs⟩ := BoundedObservationReplacement.replace R h
    obtain ⟨k', hk', ht⟩ := BoundedObservationReplacement.replace R k
    exact ⟨h', k', hh', hk',
    F.successorCollision_transfer hs.symm ht.symm hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.successor_failure_iff M).mpr ⟨h, k, hcol⟩

theorem compressed_successor_certificate
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (observe : S → X) (B : Nat)
    (R : BoundedObservationReplacement M observe B)
    (F : CheckSpecObservationFactorization C M observe)
    (hfail : ¬ C.successorCondition M) :
    ∃ h k c,
      h.length ≤ B ∧ k.length ≤ B ∧
      C.sameFiber (M.eval h) (M.eval k) ∧
      C.enabled (M.eval h) c = true ∧ C.enabled (M.eval k) c = true ∧
      (h ++ [C.letter c]).length ≤ B + 1 ∧
      (k ++ [C.letter c]).length ≤ B + 1 ∧
      C.candidate (M.eval (h ++ [C.letter c])) ≠
        C.candidate (M.eval (k ++ [C.letter c])) := by
  obtain ⟨h, k, hh, hk, hcol⟩ :=
    (compressed_successor_failure_iff C M observe B R F).mp hfail
  rcases hcol with ⟨hf, c, hc, hc', hnext⟩
  have hlen : (h ++ [C.letter c]).length ≤ B + 1 := by
    simp only [List.length_append, List.length_singleton]
    omega
  have klen : (k ++ [C.letter c]).length ≤ B + 1 := by
    simp only [List.length_append, List.length_singleton]
    omega
  refine ⟨h, k, c, hh, hk, hf, hc, hc', hlen, klen, ?_⟩
  simpa only [FiniteSystem.eval, run_append, run] using hnext

/-- Direct C1-to-R/G/T interface: once the consumer factors through the
complete-log/literal-endpoint pair, the compression theorem supplies the
bounded R/G/T witnesses. -/
theorem completeLogEndpoint_compressed_read_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (Log Endpoint : Type x) (B : Nat)
    (K : CompleteLogEndpointCompression M Log Endpoint B)
    (F : CheckSpecObservationFactorization C M K.observation) :
    ¬ C.readCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.readCollision (M.eval h) (M.eval k) :=
  compressed_read_failure_iff C M K.observation B
    K.toBoundedObservationReplacement F

theorem completeLogEndpoint_compressed_guard_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (Log Endpoint : Type x) (B : Nat)
    (K : CompleteLogEndpointCompression M Log Endpoint B)
    (F : CheckSpecObservationFactorization C M K.observation) :
    ¬ C.guardCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.guardCollision (M.eval h) (M.eval k) :=
  compressed_guard_failure_iff C M K.observation B
    K.toBoundedObservationReplacement F

theorem completeLogEndpoint_compressed_successor_failure_iff
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (Log Endpoint : Type x) (B : Nat)
    (K : CompleteLogEndpointCompression M Log Endpoint B)
    (F : CheckSpecObservationFactorization C M K.observation) :
    ¬ C.successorCondition M ↔
      ∃ h k, h.length ≤ B ∧ k.length ≤ B ∧
        C.successorCollision M (M.eval h) (M.eval k) :=
  compressed_successor_failure_iff C M K.observation B
    K.toBoundedObservationReplacement F

theorem completeLogEndpoint_compressed_successor_certificate
    (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)
    (Log Endpoint : Type x) (B : Nat)
    (K : CompleteLogEndpointCompression M Log Endpoint B)
    (F : CheckSpecObservationFactorization C M K.observation)
    (hfail : ¬ C.successorCondition M) :
    ∃ h k c,
      h.length ≤ B ∧ k.length ≤ B ∧
      C.sameFiber (M.eval h) (M.eval k) ∧
      C.enabled (M.eval h) c = true ∧ C.enabled (M.eval k) c = true ∧
      (h ++ [C.letter c]).length ≤ B + 1 ∧
      (k ++ [C.letter c]).length ≤ B + 1 ∧
      C.candidate (M.eval (h ++ [C.letter c])) ≠
        C.candidate (M.eval (k ++ [C.letter c])) :=
  compressed_successor_certificate C M K.observation B
    K.toBoundedObservationReplacement F hfail

end CheckSpec
end RGTBoundedHistory
