import RGTBoundedHistory.FiniteHistory

/-!
# Bounded R/G/T counterexample histories

The registered domain, candidate, reports, and guards are functions of the
complete state. Reports can be a tuple of all declared report values. The raw
system is total; a consumer command is enabled only when its Boolean guard is
true. No closure or sufficiency assumption is used to extract a rejection.
-/

namespace RGTBoundedHistory

universe u v w z t

variable {S : Type u} {A : Type v} {Cmd : Type w} {V : Type z} {O : Type t}

structure CheckSpec (S : Type u) (A : Type v) (Cmd : Type w)
    (V : Type z) (O : Type t) where
  domain : S → Prop
  candidate : S → V
  report : S → O
  enabled : S → Cmd → Bool
  letter : Cmd → A

namespace CheckSpec

variable (C : CheckSpec S A Cmd V O) (M : FiniteSystem S A)

def sameFiber (x y : S) : Prop :=
  C.domain x ∧ C.domain y ∧ C.candidate x = C.candidate y

def readCollision (x y : S) : Prop :=
  C.sameFiber x y ∧ C.report x ≠ C.report y

def guardCollision (x y : S) : Prop :=
  C.sameFiber x y ∧ ∃ a, C.enabled x a ≠ C.enabled y a

def successorCollision (x y : S) : Prop :=
  C.sameFiber x y ∧ ∃ a, C.enabled x a = true ∧ C.enabled y a = true ∧
    C.candidate (M.step x (C.letter a)) ≠
      C.candidate (M.step y (C.letter a))

def readCondition : Prop :=
  ∀ h k : List A, C.sameFiber (M.eval h) (M.eval k) →
    C.report (M.eval h) = C.report (M.eval k)

def guardCondition : Prop :=
  ∀ h k : List A, C.sameFiber (M.eval h) (M.eval k) →
    ∀ a, C.enabled (M.eval h) a = C.enabled (M.eval k) a

def successorCondition : Prop :=
  ∀ h k : List A, C.sameFiber (M.eval h) (M.eval k) →
    ∀ a, C.enabled (M.eval h) a = true → C.enabled (M.eval k) a = true →
      C.candidate (M.step (M.eval h) (C.letter a)) =
        C.candidate (M.step (M.eval k) (C.letter a))

theorem read_failure_iff :
    ¬ C.readCondition M ↔ ∃ h k, C.readCollision (M.eval h) (M.eval k) := by
  classical
  constructor
  · intro hfail
    apply Classical.byContradiction
    intro hn
    apply hfail
    intro h k hf
    apply Classical.byContradiction
    intro hr
    exact hn ⟨h, k, hf, hr⟩
  · rintro ⟨h, k, hf, hr⟩ hgood
    exact hr (hgood h k hf)

theorem guard_failure_iff :
    ¬ C.guardCondition M ↔ ∃ h k, C.guardCollision (M.eval h) (M.eval k) := by
  classical
  constructor
  · intro hfail
    apply Classical.byContradiction
    intro hn
    apply hfail
    intro h k hf a
    apply Classical.byContradiction
    intro hg
    exact hn ⟨h, k, hf, a, hg⟩
  · rintro ⟨h, k, hf, a, hg⟩ hgood
    exact hg (hgood h k hf a)

theorem successor_failure_iff :
    ¬ C.successorCondition M ↔
      ∃ h k, C.successorCollision M (M.eval h) (M.eval k) := by
  classical
  constructor
  · intro hfail
    apply Classical.byContradiction
    intro hn
    apply hfail
    intro h k hf a hx hy
    apply Classical.byContradiction
    intro ht
    exact hn ⟨h, k, hf, a, hx, hy, ht⟩
  · rintro ⟨h, k, hf, a, hx, hy, ht⟩ hgood
    exact ht (hgood h k hf a hx hy)

/-- R fails iff it has two actual histories of length at most N-1. -/
theorem bounded_read_failure_iff :
    ¬ C.readCondition M ↔
      ∃ h k, h.length ≤ M.cover.length - 1 ∧ k.length ≤ M.cover.length - 1 ∧
        C.readCollision (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hh, hk, hcol⟩ :=
      M.bounded_pair C.readCollision ((C.read_failure_iff M).mp hfail)
    exact ⟨h, k, by omega, by omega, hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.read_failure_iff M).mpr ⟨h, k, hcol⟩

/-- G fails iff it has two actual histories of length at most N-1. -/
theorem bounded_guard_failure_iff :
    ¬ C.guardCondition M ↔
      ∃ h k, h.length ≤ M.cover.length - 1 ∧ k.length ≤ M.cover.length - 1 ∧
        C.guardCollision (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hh, hk, hcol⟩ :=
      M.bounded_pair C.guardCollision ((C.guard_failure_iff M).mp hfail)
    exact ⟨h, k, by omega, by omega, hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.guard_failure_iff M).mpr ⟨h, k, hcol⟩

/-- T fails iff it has bounded prehistories and one common enabled command. -/
theorem bounded_successor_failure_iff :
    ¬ C.successorCondition M ↔
      ∃ h k, h.length ≤ M.cover.length - 1 ∧ k.length ≤ M.cover.length - 1 ∧
        C.successorCollision M (M.eval h) (M.eval k) := by
  constructor
  · intro hfail
    obtain ⟨h, k, hh, hk, hcol⟩ :=
      M.bounded_pair (C.successorCollision M) ((C.successor_failure_iff M).mp hfail)
    exact ⟨h, k, by omega, by omega, hcol⟩
  · rintro ⟨h, k, _, _, hcol⟩
    exact (C.successor_failure_iff M).mpr ⟨h, k, hcol⟩

/-- The successor certificate appends the same raw letter to both histories. -/
theorem bounded_successor_certificate (hfail : ¬ C.successorCondition M) :
    ∃ h k a,
      h.length ≤ M.cover.length - 1 ∧ k.length ≤ M.cover.length - 1 ∧
      C.sameFiber (M.eval h) (M.eval k) ∧
      C.enabled (M.eval h) a = true ∧ C.enabled (M.eval k) a = true ∧
      (h ++ [C.letter a]).length ≤ M.cover.length ∧
      (k ++ [C.letter a]).length ≤ M.cover.length ∧
      C.candidate (M.eval (h ++ [C.letter a])) ≠
        C.candidate (M.eval (k ++ [C.letter a])) := by
  obtain ⟨h, k, hh, hk, hf, a, hx, hy, ht⟩ :=
    (C.bounded_successor_failure_iff M).mp hfail
  have hpos := M.cover_positive
  refine ⟨h, k, a, hh, hk, hf, hx, hy, ?_, ?_, ?_⟩
  · simp only [List.length_append, List.length_singleton]
    omega
  · simp only [List.length_append, List.length_singleton]
    omega
  · simpa only [FiniteSystem.eval, run_append, run] using ht

/-- An empty registered domain is vacuous; this theorem asserts no event supply. -/
theorem empty_domain (hempty : ∀ h, ¬ C.domain (M.eval h)) :
    C.readCondition M ∧ C.guardCondition M ∧ C.successorCondition M := by
  refine ⟨?_, ?_, ?_⟩
  all_goals
    intro h k hf
    exact (hempty h hf.1).elim

end CheckSpec
end RGTBoundedHistory
