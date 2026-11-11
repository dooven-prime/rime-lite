import RGTBoundedHistory

/-! Kernel-checked interface examples, not an independent raw-runtime replay. -/

namespace RGTBoundedHistory.Checks

def emptyAlphabetSystem : FiniteSystem Unit Empty where
  step x a := nomatch a
  seed := ()
  cover := [(), ()]
  complete h := by
    cases h with
    | nil => decide
    | cons a _ => exact nomatch a

/-- An empty alphabet and a duplicate cover are both admitted. -/
example (w : List Empty) :
    ∃ v, emptyAlphabetSystem.eval v = emptyAlphabetSystem.eval w ∧ v.length ≤ 1 :=
  emptyAlphabetSystem.bounded_replacement_le w

inductive ChainState where
  | zero | one | two | three
  deriving DecidableEq

open ChainState

def chainStep : ChainState → Unit → ChainState
  | zero, _ => one
  | one, _ => two
  | two, _ => three
  | three, _ => three

def chainSystem : FiniteSystem ChainState Unit where
  step := chainStep
  seed := zero
  cover := [zero, one, two, three]
  complete h := by
    cases run chainStep zero h <;> decide

example : chainSystem.eval [(), (), ()] = three := rfl

/-- N-1 cannot in general be replaced by N-2, even for a four-state chain. -/
theorem chain_bound_sharp (w : List Unit) (hend : chainSystem.eval w = three) :
    3 ≤ w.length := by
  cases w with
  | nil => contradiction
  | cons a w =>
      cases w with
      | nil => contradiction
      | cons b w =>
          cases w with
          | nil => contradiction
          | cons c w => simp

example : ∃ v, chainSystem.eval v = chainSystem.eval (List.replicate 20 ()) ∧
    v.length ≤ 3 := chainSystem.bounded_replacement_le _

def readSpec : CheckSpec ChainState Unit Unit Unit ChainState where
  domain _ := True
  candidate _ := ()
  report x := x
  enabled _ _ := true
  letter _ := ()

theorem read_rejected : ¬ readSpec.readCondition chainSystem := by
  intro h
  have heq := h [] [()] ⟨True.intro, True.intro, rfl⟩
  exact (by decide : readSpec.report (chainSystem.eval []) ≠
    readSpec.report (chainSystem.eval [()])) heq

example : ∃ h k, h.length ≤ 3 ∧ k.length ≤ 3 ∧
    readSpec.readCollision (chainSystem.eval h) (chainSystem.eval k) :=
  (readSpec.bounded_read_failure_iff chainSystem).mp read_rejected

example : ∃ h k, h.length ≤ chainSystem.cover.length - 1 ∧
    k.length ≤ chainSystem.cover.length - 1 ∧
    readSpec.readCollision (chainSystem.eval h) (chainSystem.eval k) :=
  (readSpec.compressed_read_failure_iff chainSystem id
    (chainSystem.cover.length - 1)
    (FiniteSystem.identityBoundedObservationReplacement chainSystem)
    (CheckSpecObservationFactorization.identity readSpec chainSystem)).mp read_rejected

def guardSpec : CheckSpec ChainState Unit Unit Unit Unit where
  domain _ := True
  candidate _ := ()
  report _ := ()
  enabled x _ := x == zero
  letter _ := ()

theorem guard_rejected : ¬ guardSpec.guardCondition chainSystem := by
  intro h
  have heq := h [] [()] ⟨True.intro, True.intro, rfl⟩ ()
  exact (by decide : guardSpec.enabled (chainSystem.eval []) () ≠
    guardSpec.enabled (chainSystem.eval [()]) ()) heq

example : ∃ h k, h.length ≤ 3 ∧ k.length ≤ 3 ∧
    guardSpec.guardCollision (chainSystem.eval h) (chainSystem.eval k) :=
  (guardSpec.bounded_guard_failure_iff chainSystem).mp guard_rejected

def successorSpec : CheckSpec ChainState Unit Unit Nat Unit where
  domain _ := True
  candidate x := match x with
    | zero | one => 0
    | two => 1
    | three => 2
  report _ := ()
  enabled _ _ := true
  letter _ := ()

theorem successor_rejected : ¬ successorSpec.successorCondition chainSystem := by
  intro h
  have heq := h [] [()] ⟨True.intro, True.intro, rfl⟩ () rfl rfl
  exact (by decide :
    successorSpec.candidate (chainSystem.step (chainSystem.eval []) ()) ≠
    successorSpec.candidate (chainSystem.step (chainSystem.eval [()]) ())) heq

/-- R and G can hold even when the proposed candidate fails T. -/
example : successorSpec.readCondition chainSystem ∧
    successorSpec.guardCondition chainSystem := by
  constructor
  · intro h k _
    rfl
  · intro h k _ a
    rfl

/-- The reports and guards remain identical under every suffix despite T failure. -/
example (h k w : List Unit) :
    successorSpec.report (chainSystem.eval (h ++ w)) =
      successorSpec.report (chainSystem.eval (k ++ w)) ∧
    successorSpec.enabled (chainSystem.eval (h ++ w)) () =
      successorSpec.enabled (chainSystem.eval (k ++ w)) () := ⟨rfl, rfl⟩

example : ∃ h k a,
    h.length ≤ 3 ∧ k.length ≤ 3 ∧
    successorSpec.sameFiber (chainSystem.eval h) (chainSystem.eval k) ∧
    successorSpec.enabled (chainSystem.eval h) a = true ∧
    successorSpec.enabled (chainSystem.eval k) a = true ∧
    (h ++ [successorSpec.letter a]).length ≤ 4 ∧
    (k ++ [successorSpec.letter a]).length ≤ 4 ∧
    successorSpec.candidate (chainSystem.eval (h ++ [successorSpec.letter a])) ≠
      successorSpec.candidate (chainSystem.eval (k ++ [successorSpec.letter a])) :=
  successorSpec.bounded_successor_certificate chainSystem successor_rejected

def noDomainSpec : CheckSpec ChainState Unit Unit Nat Unit :=
  { successorSpec with domain := fun _ => False }

example : noDomainSpec.readCondition chainSystem ∧
    noDomainSpec.guardCondition chainSystem ∧
    noDomainSpec.successorCondition chainSystem :=
  noDomainSpec.empty_domain chainSystem (by intro h; exact id)

example : logBound 1 1 = 1 := by decide
example : logBound 3 2 = 90 := by decide
example : logBound 4 3 = 48448 := by decide
example : (logCodes 2 2).length = 40 := by decide

/-- A concrete recoverable codec; no Paper XL implementation is assumed here. -/
def singletonCodec : CompleteLogEncoding
    (fun (_ : Unit) (_ : Empty) => ()) () 1 1 where
  encode _ := ([0], [])
  decode _ := ()
  placement_length _ := rfl
  log_length _ := by decide
  event_length _ e he := by cases he
  recover _ := rfl

example (h : List Empty) : ∃ k,
    run (fun (_ : Unit) (_ : Empty) => ()) () k =
      run (fun (_ : Unit) (_ : Empty) => ()) () h ∧ k.length ≤ 0 :=
  singletonCodec.bounded_replacement h

end RGTBoundedHistory.Checks
