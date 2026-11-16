import RSR2.Model

namespace RSR2

def crossingWord : List Action :=
  [.v, .p1, .d0, .p0, .d0, .p0, .v, .d1]

def crossingFinal : RawState :=
  { l0 := ⟨0, 10, 0, 0⟩
    l1 := ⟨5, 0, 0, 0⟩
    events :=
      [ .vertical 1
      , .fusion false 8 2 10
      , .vertical 4
      , .fusion true 4 1 5 ] }

theorem crossing_word_executes :
    replayRaw seedRaw crossingWord = some crossingFinal := by
  decide

theorem crossing_word_checked_value :
    (replay seed crossingWord).map Subtype.val = some crossingFinal := by
  decide

theorem crossing_word_is_valid : validRaw crossingFinal := by
  decide

theorem crossing_word_has_crossing_blocks :
    crossingFinal.l0.s0 = 0 ∧
    crossingFinal.l0.s1 = 10 ∧
    crossingFinal.l1.s0 = 5 := by
  decide

theorem crossing_word_length : crossingWord.length = 8 := by rfl

end RSR2
