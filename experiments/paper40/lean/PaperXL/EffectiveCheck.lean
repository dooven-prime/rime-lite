import PaperXL.BoundedHistory

/-!
# Effective finite R/G/T checking

This module turns the complete-log replacement bound into a finite, executable
search. The checker enumerates an explicitly supplied raw-letter alphabet and
command alphabet, and checks all words up to the proved complete-state bound.
It is a generic formal anchor for a fixed consumer specification; it does not
claim to reproduce Paper XL's Python saturation implementation.
-/

namespace PaperXL

open RGTBoundedHistory

universe u v w z t

variable {S : Type u} {A : Type v} {Cmd : Type w} {V : Type z} {O : Type t}

/-- All words over a finite listed alphabet with length at most `bound`. -/
def wordsUpTo (alphabet : List A) (bound : Nat) : List (List A) :=
  (List.range (bound + 1)).flatMap fun k => RGTBoundedHistory.words alphabet k

theorem letters_of_mem_words {alphabet : List A} {k : Nat} {w : List A}
    (hw : w ∈ RGTBoundedHistory.words alphabet k) :
    ∀ a ∈ w, a ∈ alphabet := by
  induction k generalizing w with
  | zero =>
      simp [RGTBoundedHistory.words] at hw
      subst w
      simp
  | succ k ih =>
      simp only [RGTBoundedHistory.words, List.mem_flatMap] at hw
      rcases hw with ⟨a, ha, htail⟩
      simp only [List.mem_map] at htail
      rcases htail with ⟨tail, htail, rfl⟩
      intro b hb
      simp only [List.mem_cons] at hb
      rcases hb with rfl | hb
      · exact ha
      · exact ih htail b hb

theorem length_of_mem_words {alphabet : List A} {k : Nat} {w : List A}
    (hw : w ∈ RGTBoundedHistory.words alphabet k) : w.length = k := by
  induction k generalizing w with
  | zero =>
      simp [RGTBoundedHistory.words] at hw
      subst w
      rfl
  | succ k ih =>
      simp only [RGTBoundedHistory.words, List.mem_flatMap] at hw
      rcases hw with ⟨a, ha, htail⟩
      simp only [List.mem_map] at htail
      rcases htail with ⟨tail, htail, rfl⟩
      simp [ih htail]

theorem mem_wordsUpTo_iff {alphabet : List A} {bound : Nat} {w : List A} :
    w ∈ wordsUpTo alphabet bound ↔
      w.length ≤ bound ∧ ∀ a ∈ w, a ∈ alphabet := by
  constructor
  · intro hw
    simp only [wordsUpTo, List.mem_flatMap] at hw
    rcases hw with ⟨k, hk, hw⟩
    have hwordlen := length_of_mem_words hw
    have hletters := letters_of_mem_words hw
    constructor
    · simp only [List.mem_range] at hk
      rw [hwordlen]
      omega
    · exact hletters
  · rintro ⟨hlen, hletters⟩
    simp only [wordsUpTo, List.mem_flatMap]
    refine ⟨w.length, ?_, ?_⟩
    · simp only [List.mem_range]
      omega
    · exact RGTBoundedHistory.mem_words alphabet w hletters

namespace EffectiveCheck

variable (M : FiniteSystem S A)
variable (C : CheckSpec S A Cmd V O)
variable (H : List (List A))

/-- R restricted to a finite complete list of representative histories. -/
def readConditionOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) : Prop :=
  ∀ h ∈ H, ∀ k ∈ H,
    C.sameFiber (M.eval h) (M.eval k) → C.report (M.eval h) = C.report (M.eval k)

/-- G restricted to representative histories and an explicit command list. -/
def guardConditionOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) (commands : List Cmd) : Prop :=
  ∀ h ∈ H, ∀ k ∈ H,
    C.sameFiber (M.eval h) (M.eval k) → ∀ a ∈ commands,
      C.enabled (M.eval h) a = C.enabled (M.eval k) a

/-- T restricted to representative histories and an explicit command list. -/
def successorConditionOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) (commands : List Cmd) : Prop :=
  ∀ h ∈ H, ∀ k ∈ H,
    C.sameFiber (M.eval h) (M.eval k) → ∀ a ∈ commands,
      C.enabled (M.eval h) a = true → C.enabled (M.eval k) a = true →
        C.candidate (M.step (M.eval h) (C.letter a)) =
          C.candidate (M.step (M.eval k) (C.letter a))

/-- Executable finite R check. -/
def sameFiberCheck (C : CheckSpec S A Cmd V O) (domainCheck : S → Bool)
    (x y : S) [DecidableEq V] : Bool :=
  domainCheck x && domainCheck y && decide (C.candidate x = C.candidate y)

theorem sameFiberCheck_correct (C : CheckSpec S A Cmd V O) (domainCheck : S → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s) (x y : S)
    [DecidableEq V] :
    sameFiberCheck C domainCheck x y = true ↔ C.sameFiber x y := by
  simp [sameFiberCheck, CheckSpec.sameFiber, Bool.and_eq_true, decide_eq_true_eq,
    hdomain, and_assoc]

theorem sameFiberCheck_false_iff (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s) (x y : S)
    [DecidableEq V] :
    sameFiberCheck C domainCheck x y = false ↔ ¬ C.sameFiber x y := by
  constructor
  · intro hfalse hfiber
    have htrue := (sameFiberCheck_correct C domainCheck hdomain x y).mpr hfiber
    rw [hfalse] at htrue
    contradiction
  · intro hnot
    cases hcheck : sameFiberCheck C domainCheck x y with
    | false => rfl
    | true =>
        exfalso
        exact hnot ((sameFiberCheck_correct C domainCheck hdomain x y).mp hcheck)

def readCheckOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) [DecidableEq V] [DecidableEq O] : Bool :=
  H.all fun h => H.all fun k =>
    decide (sameFiberCheck C domainCheck (M.eval h) (M.eval k) = true →
      C.report (M.eval h) = C.report (M.eval k))

/-- Executable finite G check. -/
def guardCheckOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    [DecidableEq V] : Bool :=
  H.all fun h => H.all fun k => commands.all fun a =>
    decide (sameFiberCheck C domainCheck (M.eval h) (M.eval k) = true →
      C.enabled (M.eval h) a = C.enabled (M.eval k) a)

/-- Executable finite T check. -/
def successorCheckOn (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    [DecidableEq V] : Bool :=
  H.all fun h => H.all fun k => commands.all fun a =>
    decide (sameFiberCheck C domainCheck (M.eval h) (M.eval k) = true →
        C.enabled (M.eval h) a = true → C.enabled (M.eval k) a = true →
        C.candidate (M.step (M.eval h) (C.letter a)) =
          C.candidate (M.step (M.eval k) (C.letter a)))

theorem readCheckOn_correct (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (hdomain : ∀ s,
      domainCheck s = true ↔ C.domain s) [DecidableEq V] [DecidableEq O] :
    readCheckOn M C domainCheck H = true ↔ readConditionOn M C H := by
  have hsf := sameFiberCheck_correct C domainCheck hdomain
  simp only [readCheckOn, readConditionOn, List.all_eq_true, decide_eq_true_eq,
    hsf]

theorem guardCheckOn_correct (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s) [DecidableEq V] :
    guardCheckOn M C domainCheck H commands = true ↔ guardConditionOn M C H commands := by
  have hsf := sameFiberCheck_correct C domainCheck hdomain
  simp only [guardCheckOn, guardConditionOn, List.all_eq_true, decide_eq_true_eq,
    hsf]
  constructor
  · intro hgood h hh k hk hf a ha
    exact hgood h hh k hk a ha hf
  · intro hgood h hh k hk a ha hf
    exact hgood h hh k hk hf a ha

theorem successorCheckOn_correct (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s) [DecidableEq V] :
    successorCheckOn M C domainCheck H commands = true ↔
      successorConditionOn M C H commands := by
  have hsf := sameFiberCheck_correct C domainCheck hdomain
  simp only [successorCheckOn, successorConditionOn, List.all_eq_true,
    decide_eq_true_eq, hsf]
  constructor
  · intro hgood h hh k hk hf a ha hx hy
    exact hgood h hh k hk a ha hf hx hy
  · intro hgood h hh k hk a ha hf hx hy
    exact hgood h hh k hk hf a ha hx hy

theorem readCondition_iff_on (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) (hcomplete : ∀ w, ∃ h ∈ H, M.eval h = M.eval w) :
    C.readCondition M ↔ readConditionOn M C H := by
  constructor
  · intro hgood h hh k hk hf
    exact hgood h k hf
  · intro hgood h k hf
    obtain ⟨h', h'h, heq⟩ := hcomplete h
    obtain ⟨k', k'h, keq⟩ := hcomplete k
    have hf' : C.sameFiber (M.eval h') (M.eval k') := by
      simpa [heq, keq] using hf
    have hout := hgood h' h'h k' k'h hf'
    simpa [heq, keq] using hout

theorem guardCondition_iff_on (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) (commands : List Cmd)
    (hcommands : ∀ a : Cmd, a ∈ commands)
    (hcomplete : ∀ w, ∃ h ∈ H, M.eval h = M.eval w) :
    C.guardCondition M ↔ guardConditionOn M C H commands := by
  constructor
  · intro hgood h hh k hk hf a ha
    exact hgood h k hf a
  · intro hgood h k hf a
    obtain ⟨h', h'h, heq⟩ := hcomplete h
    obtain ⟨k', k'h, keq⟩ := hcomplete k
    have hf' : C.sameFiber (M.eval h') (M.eval k') := by
      simpa [heq, keq] using hf
    have hout := hgood h' h'h k' k'h hf' a (hcommands a)
    simpa [heq, keq] using hout

theorem successorCondition_iff_on (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (H : List (List A)) (commands : List Cmd) (hcommands : ∀ a : Cmd, a ∈ commands)
    (hcomplete : ∀ w, ∃ h ∈ H, M.eval h = M.eval w) :
    C.successorCondition M ↔ successorConditionOn M C H commands := by
  constructor
  · intro hgood h hh k hk hf a ha hx hy
    exact hgood h k hf a hx hy
  · intro hgood h k hf a hx hy
    obtain ⟨h', h'h, heq⟩ := hcomplete h
    obtain ⟨k', k'h, keq⟩ := hcomplete k
    have hf' : C.sameFiber (M.eval h') (M.eval k') := by
      simpa [heq, keq] using hf
    have hx' : C.enabled (M.eval h') a = true := by simpa [heq] using hx
    have hy' : C.enabled (M.eval k') a = true := by simpa [keq] using hy
    have hout := hgood h' h'h k' k'h hf' a (hcommands a) hx' hy'
    simpa [heq, keq] using hout

/-- The returned Boolean is a direct recursive check of finite lists. -/
def decision (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    [DecidableEq V] [DecidableEq O] : Bool :=
  readCheckOn M C domainCheck H && guardCheckOn M C domainCheck H commands &&
    successorCheckOn M C domainCheck H commands

theorem decision_correct (M : FiniteSystem S A) (C : CheckSpec S A Cmd V O)
    (domainCheck : S → Bool) (H : List (List A)) (commands : List Cmd)
    (hcommands : ∀ a : Cmd, a ∈ commands)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s)
    (hcomplete : ∀ w, ∃ h ∈ H, M.eval h = M.eval w)
    [DecidableEq V] [DecidableEq O] :
    decision M C domainCheck H commands = true ↔
      C.readCondition M ∧ C.guardCondition M ∧ C.successorCondition M := by
  constructor
  · intro h
    have h' : (readCheckOn M C domainCheck H = true ∧
        guardCheckOn M C domainCheck H commands = true) ∧
        successorCheckOn M C domainCheck H commands = true := by
      simpa [decision, Bool.and_eq_true] using h
    exact ⟨(readCondition_iff_on M C H hcomplete).mpr
        ((readCheckOn_correct M C domainCheck H hdomain).mp h'.1.1),
      (guardCondition_iff_on M C H commands hcommands hcomplete).mpr
        ((guardCheckOn_correct M C domainCheck H commands hdomain).mp h'.1.2),
      (successorCondition_iff_on M C H commands hcommands hcomplete).mpr
        ((successorCheckOn_correct M C domainCheck H commands hdomain).mp h'.2)⟩
  · rintro ⟨hr, hg, ht⟩
    have hr' := (readCondition_iff_on M C H hcomplete).mp hr
    have hg' := (guardCondition_iff_on M C H commands hcommands hcomplete).mp hg
    have ht' := (successorCondition_iff_on M C H commands hcommands hcomplete).mp ht
    have hb : (readCheckOn M C domainCheck H = true ∧
        guardCheckOn M C domainCheck H commands = true) ∧
        successorCheckOn M C domainCheck H commands = true :=
      ⟨⟨(readCheckOn_correct M C domainCheck H hdomain).mpr hr',
        (guardCheckOn_correct M C domainCheck H commands hdomain).mpr hg'⟩,
        (successorCheckOn_correct M C domainCheck H commands hdomain).mpr ht'⟩
    simpa [decision, Bool.and_eq_true] using hb

end EffectiveCheck

namespace BoundedDecision

variable {step : S → A → S} {seed : S} {n m : Nat}

/-- The finite search universe over an explicitly supplied raw alphabet. -/
def histories (bound : Nat) (alphabet : List A) : List (List A) :=
  wordsUpTo alphabet bound

theorem histories_complete (E : CompleteLogEncoding step seed n m)
    (alphabet : List A) (halphabet : ∀ a : A, a ∈ alphabet)
    (w : List A) :
    ∃ h ∈ histories (logBound n m - 1) alphabet,
      E.system.eval h = E.system.eval w := by
  obtain ⟨h, heq, hlen⟩ := E.bounded_replacement w
  refine ⟨h, ?_, ?_⟩
  · apply mem_wordsUpTo_iff.mpr
    exact ⟨hlen, fun a ha => halphabet a⟩
  · simpa [FiniteSystem.eval, CompleteLogEncoding.system] using heq

theorem decision_correct (E : CompleteLogEncoding step seed n m)
    (alphabet : List A) (halphabet : ∀ a : A, a ∈ alphabet)
    (commands : List Cmd) (hcommands : ∀ c : Cmd, c ∈ commands)
    (C : CheckSpec S A Cmd V O) (domainCheck : S → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s)
    [DecidableEq V] [DecidableEq O] :
    EffectiveCheck.decision E.system C domainCheck
      (histories (logBound n m - 1) alphabet) commands = true ↔
      C.readCondition E.system ∧ C.guardCondition E.system ∧
        C.successorCondition E.system :=
  EffectiveCheck.decision_correct E.system C domainCheck
    (histories (logBound n m - 1) alphabet) commands hcommands hdomain
    (histories_complete E alphabet halphabet)

theorem rejected_with_bounded_witnesses (E : CompleteLogEncoding step seed n m)
    (alphabet : List A) (halphabet : ∀ a : A, a ∈ alphabet)
    (commands : List Cmd) (hcommands : ∀ c : Cmd, c ∈ commands)
    (C : CheckSpec S A Cmd V O) (domainCheck : S → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s)
    [DecidableEq V] [DecidableEq O]
    (hreject : EffectiveCheck.decision E.system C domainCheck
      (histories (logBound n m - 1) alphabet) commands = false) :
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.readCollision (E.system.eval h) (E.system.eval k)) ∨
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.guardCollision (E.system.eval h) (E.system.eval k)) ∨
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.successorCollision E.system (E.system.eval h) (E.system.eval k)) := by
  have hnot : ¬ (C.readCondition E.system ∧ C.guardCondition E.system ∧
      C.successorCondition E.system) := by
    intro hgood
    have htrue := (decision_correct E alphabet halphabet commands hcommands C
      domainCheck hdomain).2 hgood
    rw [hreject] at htrue
    contradiction
  by_cases hread : C.readCondition E.system
  · by_cases hguard : C.guardCondition E.system
    · have hsucc : ¬ C.successorCondition E.system := by
        intro hs
        exact hnot ⟨hread, hguard, hs⟩
      obtain ⟨h, k, hh, hk, hcollision⟩ :=
        (C.bounded_successor_failure_iff E.system).mp hsucc
      exact Or.inr (Or.inr ⟨h, k, by simpa [E.system_cover_length] using hh,
        by simpa [E.system_cover_length] using hk, hcollision⟩)
    · obtain ⟨h, k, hh, hk, hcollision⟩ :=
        (C.bounded_guard_failure_iff E.system).mp hguard
      exact Or.inr (Or.inl ⟨h, k, by simpa [E.system_cover_length] using hh,
        by simpa [E.system_cover_length] using hk, hcollision⟩)
  · obtain ⟨h, k, hh, hk, hcollision⟩ :=
      (C.bounded_read_failure_iff E.system).mp hread
    exact Or.inl ⟨h, k, by simpa [E.system_cover_length] using hh,
      by simpa [E.system_cover_length] using hk, hcollision⟩

/-- The effective checker specialized to the circular `p,d` source model. -/
theorem circular_decision_correct (env : CircularEnvironment n m)
    (commands : List Cmd) (hcommands : ∀ c : Cmd, c ∈ commands)
    (C : CheckSpec (CircularLogState n m) RawLetter Cmd V O)
    (domainCheck : CircularLogState n m → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s)
    [DecidableEq V] [DecidableEq O] :
    EffectiveCheck.decision (completeLogEncoding env).system C domainCheck
      (histories (logBound n m - 1) [.p, .d]) commands = true ↔
      C.readCondition (completeLogEncoding env).system ∧
        C.guardCondition (completeLogEncoding env).system ∧
        C.successorCondition (completeLogEncoding env).system := by
  have halphabet : ∀ a : RawLetter, a ∈ ([.p, .d] : List RawLetter) := by
    intro a
    cases a <;> simp
  exact decision_correct (completeLogEncoding env) [.p, .d] halphabet
    commands hcommands C domainCheck hdomain

/-- Any rejection of the circular-model decision has bounded actual histories. -/
theorem circular_rejected_with_bounded_witnesses
    (env : CircularEnvironment n m)
    (commands : List Cmd) (hcommands : ∀ c : Cmd, c ∈ commands)
    (C : CheckSpec (CircularLogState n m) RawLetter Cmd V O)
    (domainCheck : CircularLogState n m → Bool)
    (hdomain : ∀ s, domainCheck s = true ↔ C.domain s)
    [DecidableEq V] [DecidableEq O]
    (hreject : EffectiveCheck.decision (completeLogEncoding env).system C domainCheck
      (histories (logBound n m - 1) [.p, .d]) commands = false) :
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.readCollision
          ((completeLogEncoding env).system.eval h)
          ((completeLogEncoding env).system.eval k)) ∨
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.guardCollision
          ((completeLogEncoding env).system.eval h)
          ((completeLogEncoding env).system.eval k)) ∨
    (∃ h k,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.successorCollision (completeLogEncoding env).system
          ((completeLogEncoding env).system.eval h)
          ((completeLogEncoding env).system.eval k)) := by
  have halphabet : ∀ a : RawLetter, a ∈ ([.p, .d] : List RawLetter) := by
    intro a
    cases a <;> simp
  exact rejected_with_bounded_witnesses (completeLogEncoding env) [.p, .d]
    halphabet commands hcommands C domainCheck hdomain hreject

end BoundedDecision

end PaperXL
