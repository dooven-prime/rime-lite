import FusionLogInterpretation

namespace FusionLogSchedule

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation

variable {n : ℕ} [NeZero n]

abbrev IndexPackets (n : ℕ) := Finset (Finset (ZMod n))

def mergePackets (C : IndexPackets n) (A B : Finset (ZMod n)) : IndexPackets n :=
  insert (A ∪ B) ((C.erase A).erase B)

/-- A word-free contraction trace. The source boundary predicate encodes
positive ordered cyclic neighbours; it retains both directions at rank two. -/
inductive AbstractTrace : IndexPackets n → List (FusionRecord (ZMod n)) → IndexPackets n → Prop
  | nil (C) : AbstractTrace C [] C
  | cons {C last} {A B : Finset (ZMod n)} {rest}
      (left : A ∈ C) (right : B ∈ C) (distinct : A ≠ B)
      (boundary : SourceAtomAdjacent A B)
      (tail : AbstractTrace (mergePackets C A B) rest last) :
      AbstractTrace C (⟨A, B, A ∪ B⟩ :: rest) last

def advance (C : IndexPackets n) (event : FusionRecord (ZMod n)) : IndexPackets n :=
  mergePackets C event.left event.right

theorem AbstractTrace.last_eq_fold {C last : IndexPackets n}
    {events : List (FusionRecord (ZMod n))} (trace : AbstractTrace C events last) :
    last = events.foldl advance C := by
  induction trace with
  | nil C => rfl
  | cons _ _ _ _ _ ih => exact ih

theorem AbstractTrace.last_unique {C last other : IndexPackets n}
    {events : List (FusionRecord (ZMod n))}
    (first : AbstractTrace C events last) (second : AbstractTrace C events other) :
    last = other := first.last_eq_fold.trans second.last_eq_fold.symm

/-- This is a static oriented placement certificate, not an execution path. -/
def IndexCompatible (last : IndexPackets n) (target : Placement n (Finset (ZMod n))) : Prop :=
  SourceOrdered target ∧ packetSet target = last

end FusionLogSchedule
