import RGTBoundedHistory.Certificates

/-!
# Counted complete-log encoding interface

One placement digit per atom has n choices; each ordered binary fusion is
encoded by m ternary digits (left parent / right parent / neither). There are
fewer than m events. The counted list intentionally includes invalid codes.
An application must prove recovery of its *complete* reachable state; a lossy
selected summary does not meet this interface merely by having such fields.
-/

namespace RGTBoundedHistory

universe u v w z t

private theorem length_flatMap_constant {X : Type u} {Y : Type v}
    (xs : List X) (f : X → List Y) (b : Nat)
    (h : ∀ x ∈ xs, (f x).length = b) :
    (xs.flatMap f).length = xs.length * b := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.flatMap_cons, List.length_append, List.length_cons]
      rw [h x (by simp), ih (fun y hy => h y (by simp [hy]))]
      simp [Nat.add_mul, Nat.add_comm]

def words {X : Type u} (alphabet : List X) : Nat → List (List X)
  | 0 => [[]]
  | k + 1 => alphabet.flatMap fun a => (words alphabet k).map (a :: ·)

theorem words_length {X : Type u} (alphabet : List X) (k : Nat) :
    (words alphabet k).length = alphabet.length ^ k := by
  induction k with
  | zero => simp [words]
  | succ k ih =>
      rw [words, length_flatMap_constant alphabet _ (alphabet.length ^ k)]
      · simp [Nat.pow_succ, Nat.mul_comm]
      · intro a _
        simp [ih]

theorem mem_words {X : Type u} (alphabet : List X) (xs : List X)
    (h : ∀ x ∈ xs, x ∈ alphabet) : xs ∈ words alphabet xs.length := by
  induction xs with
  | nil => simp [words]
  | cons a xs ih =>
      apply List.mem_flatMap.mpr
      refine ⟨a, h a (by simp), ?_⟩
      exact List.mem_map.mpr ⟨xs, ih (fun x hx => h x (by simp [hx])), rfl⟩

def eventAlphabet (m : Nat) : List (List (Fin 3)) := words (List.finRange 3) m

def logAlphabet (m : Nat) : List (List (List (Fin 3))) :=
  (List.range m).flatMap fun j => words (eventAlphabet m) j

abbrev LogCode (n : Nat) := List (Fin n) × List (List (Fin 3))

def logCodes (n m : Nat) : List (LogCode n) :=
  (words (List.finRange n) m).flatMap fun p => (logAlphabet m).map (p, ·)

/-- An overcount of complete placement-and-fusion-log states. -/
def logBound (n m : Nat) : Nat :=
  n ^ m * ((List.range m).map fun j => 3 ^ (m * j)).sum

theorem logAlphabet_length (m : Nat) :
    (logAlphabet m).length = ((List.range m).map fun j => 3 ^ (m * j)).sum := by
  simp [logAlphabet, List.length_flatMap, words_length,
    eventAlphabet, Nat.pow_mul]

theorem logCodes_length (n m : Nat) : (logCodes n m).length = logBound n m := by
  rw [logCodes, length_flatMap_constant _ _ (logAlphabet m).length]
  · simp [words_length, logAlphabet_length, logBound]
  · intro p _
    simp

theorem mem_logCodes {n m : Nat} (c : LogCode n)
    (hp : c.1.length = m) (hl : c.2.length < m)
    (he : ∀ e ∈ c.2, e.length = m) : c ∈ logCodes n m := by
  apply List.mem_flatMap.mpr
  have hpmem := mem_words (List.finRange n) c.1 (fun a _ => List.mem_finRange a)
  rw [hp] at hpmem
  refine ⟨c.1, hpmem, List.mem_map.mpr ⟨c.2, ?_, by simp⟩⟩
  apply List.mem_flatMap.mpr
  refine ⟨c.2.length, List.mem_range.mpr hl, ?_⟩
  apply mem_words
  intro e hemem
  have h := mem_words (List.finRange 3) e (fun a _ => List.mem_finRange a)
  simpa only [eventAlphabet, he e hemem] using h

/-- The semantic bridge is an explicit obligation, not supplied by counting. -/
structure CompleteLogEncoding {S : Type u} {A : Type v}
    (step : S → A → S) (seed : S) (n m : Nat) where
  encode : S → LogCode n
  decode : LogCode n → S
  placement_length : ∀ h, (encode (run step seed h)).1.length = m
  log_length : ∀ h, (encode (run step seed h)).2.length < m
  event_length : ∀ h e, e ∈ (encode (run step seed h)).2 → e.length = m
  recover : ∀ h, decode (encode (run step seed h)) = run step seed h

namespace CompleteLogEncoding

variable {S : Type u} {A : Type v} {step : S → A → S} {seed : S} {n m : Nat}
variable (E : CompleteLogEncoding step seed n m)

def system : FiniteSystem S A where
  step := step
  seed := seed
  cover := (logCodes n m).map E.decode
  complete h := List.mem_map.mpr ⟨E.encode (run step seed h),
    mem_logCodes _ (E.placement_length h) (E.log_length h) (E.event_length h),
    E.recover h⟩

theorem system_cover_length : E.system.cover.length = logBound n m := by
  simp [system, logCodes_length]

include E in
theorem bounded_replacement (h : List A) :
    ∃ k, run step seed k = run step seed h ∧ k.length ≤ logBound n m - 1 := by
  obtain ⟨k, hk, hlen⟩ := FiniteSystem.bounded_replacement_le E.system h
  exact ⟨k, hk, by simpa only [system_cover_length] using hlen⟩

variable {Cmd : Type w} {V : Type z} {O : Type t}

/-- The finite-state R certificate with the counted complete-log bound. -/
theorem bounded_read_failure_iff (C : CheckSpec S A Cmd V O) :
    ¬ C.readCondition E.system ↔
      ∃ h k, h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.readCollision (E.system.eval h) (E.system.eval k) := by
  simpa only [system_cover_length] using C.bounded_read_failure_iff E.system

/-- The finite-state G certificate with the counted complete-log bound. -/
theorem bounded_guard_failure_iff (C : CheckSpec S A Cmd V O) :
    ¬ C.guardCondition E.system ↔
      ∃ h k, h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.guardCollision (E.system.eval h) (E.system.eval k) := by
  simpa only [system_cover_length] using C.bounded_guard_failure_iff E.system

/-- T rejection needs bounded prehistories, not a future-language separator. -/
theorem bounded_successor_failure_iff (C : CheckSpec S A Cmd V O) :
    ¬ C.successorCondition E.system ↔
      ∃ h k, h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
        C.successorCollision E.system (E.system.eval h) (E.system.eval k) := by
  simpa only [system_cover_length] using C.bounded_successor_failure_iff E.system

theorem bounded_successor_certificate (C : CheckSpec S A Cmd V O)
    (hfail : ¬ C.successorCondition E.system) :
    ∃ h k a,
      h.length ≤ logBound n m - 1 ∧ k.length ≤ logBound n m - 1 ∧
      C.sameFiber (E.system.eval h) (E.system.eval k) ∧
      C.enabled (E.system.eval h) a = true ∧
      C.enabled (E.system.eval k) a = true ∧
      (h ++ [C.letter a]).length ≤ logBound n m ∧
      (k ++ [C.letter a]).length ≤ logBound n m ∧
      C.candidate (E.system.eval (h ++ [C.letter a])) ≠
        C.candidate (E.system.eval (k ++ [C.letter a])) := by
  simpa only [system_cover_length] using C.bounded_successor_certificate E.system hfail

end CompleteLogEncoding
end RGTBoundedHistory
