import PaperXL.CircularModel
import RGTBoundedHistory.LogEncoding

namespace PaperXL

open RGTBoundedHistory

namespace CircularLogState

variable {n m : Nat} (E : CircularEnvironment n m)

def encodeEvent (e : EventCode m) : List (Fin 3) := List.ofFn e

def decodeEvent (e : List (Fin 3)) : EventCode m :=
  fun i => e.getD i.val 2

def encodeComplete (s : CircularLogState n m) : LogCode n :=
  (List.ofFn s.site, s.events.map encodeEvent)

def decodeComplete (E : CircularEnvironment n m) (c : LogCode n) :
    CircularLogState n m :=
  ⟨(fun i => c.1.getD i.val ⟨0, E.hn⟩), c.2.map decodeEvent⟩

theorem getD_ofFn (f : Fin m → α) (i : Fin m) (fallback : α) :
    (List.ofFn f).getD i.val fallback = f i := by
  rw [List.getD_eq_getElem?_getD]
  simp [i.isLt]

theorem decodeEvent_encodeEvent (e : EventCode m) :
    decodeEvent (encodeEvent e) = e := by
  funext i
  exact getD_ofFn e i 2

theorem decodeComplete_encodeComplete (s : CircularLogState n m) :
    decodeComplete E (encodeComplete s) = s := by
  cases s with
  | mk site events =>
      have hsite :
          (decodeComplete E (encodeComplete { site := site, events := events })).site
            = site := by
        funext i
        exact getD_ofFn site i ⟨0, E.hn⟩
      have hevents :
          (decodeComplete E (encodeComplete { site := site, events := events })).events
            = events := by
        dsimp [decodeComplete, encodeComplete]
        simp only [List.map_map, Function.comp_def]
        simp [decodeEvent_encodeEvent]
      exact CircularLogState.ext hsite hevents

theorem placement_length (s : CircularLogState n m) :
    (encodeComplete s).1.length = m := by
  simp [encodeComplete]

theorem event_length (s : CircularLogState n m) (e : List (Fin 3))
    (he : e ∈ (encodeComplete s).2) : e.length = m := by
  simp only [encodeComplete, List.mem_map] at he
  rcases he with ⟨event, _, rfl⟩
  simp [encodeEvent]

end CircularLogState

theorem recursiveRun_eq_rawRun (E : CircularEnvironment n m)
    (w : List RawLetter) :
    RGTBoundedHistory.run (CircularLogState.step E)
      (CircularLogState.seedState E) w =
      RawSystem.run (CircularLogState.rawSystem E) w := by
  have hrec : ∀ (s : CircularLogState n m) (w : List RawLetter),
      RGTBoundedHistory.run (CircularLogState.step E) s w =
        w.foldl (CircularLogState.step E) s := by
    intro s w
    induction w generalizing s with
    | nil => rfl
    | cons a w ih =>
        simp only [RGTBoundedHistory.run, List.foldl_cons]
        exact ih _
  simpa [RawSystem.run, CircularLogState.rawSystem] using
    hrec (CircularLogState.seedState E) w

theorem event_count_lt_atoms_recursive (E : CircularEnvironment n m)
    (w : List RawLetter) :
    (RGTBoundedHistory.run (CircularLogState.step E)
      (CircularLogState.seedState E) w).events.length < m := by
  rw [recursiveRun_eq_rawRun]
  exact CircularLogState.event_count_lt_atoms E w

def completeLogEncoding (E : CircularEnvironment n m) :
    RGTBoundedHistory.CompleteLogEncoding (CircularLogState.step E)
      (CircularLogState.seedState E) n m where
  encode := CircularLogState.encodeComplete
  decode := CircularLogState.decodeComplete E
  placement_length := by
    intro w
    exact CircularLogState.placement_length _
  log_length := by
    intro w
    simpa [CircularLogState.encodeComplete] using
      event_count_lt_atoms_recursive E w
  event_length := by
    intro w e he
    exact CircularLogState.event_length _ e he
  recover := by
    intro w
    exact CircularLogState.decodeComplete_encodeComplete E _

theorem circular_history_replacement (E : CircularEnvironment n m)
    (w : List RawLetter) :
    ∃ v : List RawLetter,
      RGTBoundedHistory.run (CircularLogState.step E)
        (CircularLogState.seedState E) v =
        RGTBoundedHistory.run (CircularLogState.step E)
          (CircularLogState.seedState E) w ∧
      v.length ≤ RGTBoundedHistory.logBound n m - 1 :=
  (completeLogEncoding E).bounded_replacement w

variable {Cmd : Type u} {V : Type v} {O : Type w}

theorem circular_read_failure_bound
    (E : CircularEnvironment n m)
    (C : RGTBoundedHistory.CheckSpec
      (CircularLogState n m) RawLetter Cmd V O) :
    ¬ C.readCondition (completeLogEncoding E).system ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.readCollision
          ((completeLogEncoding E).system.eval h)
          ((completeLogEncoding E).system.eval k) :=
  (completeLogEncoding E).bounded_read_failure_iff C

theorem circular_guard_failure_bound
    (E : CircularEnvironment n m)
    (C : RGTBoundedHistory.CheckSpec
      (CircularLogState n m) RawLetter Cmd V O) :
    ¬ C.guardCondition (completeLogEncoding E).system ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.guardCollision
          ((completeLogEncoding E).system.eval h)
          ((completeLogEncoding E).system.eval k) :=
  (completeLogEncoding E).bounded_guard_failure_iff C

theorem circular_successor_failure_bound
    (E : CircularEnvironment n m)
    (C : RGTBoundedHistory.CheckSpec
      (CircularLogState n m) RawLetter Cmd V O) :
    ¬ C.successorCondition (completeLogEncoding E).system ↔
      ∃ h k,
        h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
        C.successorCollision (completeLogEncoding E).system
          ((completeLogEncoding E).system.eval h)
          ((completeLogEncoding E).system.eval k) :=
  (completeLogEncoding E).bounded_successor_failure_iff C

theorem circular_successor_failure_certificate
    (E : CircularEnvironment n m)
    (C : RGTBoundedHistory.CheckSpec
      (CircularLogState n m) RawLetter Cmd V O)
    (hfail : ¬ C.successorCondition (completeLogEncoding E).system) :
    ∃ h k a,
      h.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
      k.length ≤ RGTBoundedHistory.logBound n m - 1 ∧
      C.sameFiber
        ((completeLogEncoding E).system.eval h)
        ((completeLogEncoding E).system.eval k) ∧
      C.enabled ((completeLogEncoding E).system.eval h) a = true ∧
      C.enabled ((completeLogEncoding E).system.eval k) a = true ∧
      (h ++ [C.letter a]).length ≤ RGTBoundedHistory.logBound n m ∧
      (k ++ [C.letter a]).length ≤ RGTBoundedHistory.logBound n m ∧
      C.candidate
        ((completeLogEncoding E).system.eval (h ++ [C.letter a])) ≠
      C.candidate
        ((completeLogEncoding E).system.eval (k ++ [C.letter a])) :=
  (completeLogEncoding E).bounded_successor_certificate C hfail

end PaperXL
