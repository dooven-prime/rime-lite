import RSR2.SingletonOptimalClassification

/-!
# Exact number of shortest singleton words

This core-only module certifies the cardinality by an exhaustive duplicate-free
list: membership is equivalent to actual realization at the optimal length.
No decidability assumption on the noncomputable executor is needed.
-/

namespace RSR2.Parametric

private theorem two_stage_defect_eq_rotation :
    collapse 2 (by decide) (singletonTransferStage 2 (by decide) 0 (by decide)) false =
      rotate 2 (by decide) (singletonTransferStage 2 (by decide) 0 (by decide)) false := by
  funext a
  have ha : a = (⟨0, by decide⟩ : Fin 2) ∨ a = (⟨1, by decide⟩ : Fin 2) := by
    by_cases hz : a.val = 0
    · exact Or.inl (Fin.ext hz)
    · apply Or.inr
      apply Fin.ext
      change a.val = 1
      have := a.isLt
      omega
  rcases ha with rfl | rfl <;> rfl

private theorem two_defect_round_run (swap : Bool) :
    run 2 (by decide) (singletonTransferStage 2 (by decide) 0 (by decide))
      (singletonControlRound (true, swap)) =
        some (upperSingletonEndpoint 2 (by decide)) := by
  rw [singletonControlRound_run_eq]
  have he : run 2 (by decide) (singletonTransferStage 2 (by decide) 0 (by decide))
        [.d false, .p true, .v] =
      run 2 (by decide) (singletonTransferStage 2 (by decide) 0 (by decide))
        [.p false, .p true, .v] := by
    simp only [run, step_p, step_d, Option.bind_some]
    rw [two_stage_defect_eq_rotation]
  change run 2 (by decide) _ [.d false, .p true, .v] = some _
  rw [he]
  have hs := singletonControlRound_stage_run 2 (by decide) 0 (by decide) false
  have hend := singletonTransferStage_terminal 2 (by decide)
  change singletonTransferStage 2 (by decide) 1 (by decide) = _ at hend
  rw [hend] at hs
  simpa [singletonControlRound, singletonLowerChoice] using hs

theorem singleton_two_control_round_run (defect swap : Bool) :
    run 2 (by decide) (seed 2) (.v :: singletonControlRound (defect, swap)) =
      some (upperSingletonEndpoint 2 (by decide)) := by
  have hp := singletonTransferPrefix_run 2 (by decide) 0 (by decide)
  change run 2 (by decide) (seed 2) [.v] = some _ at hp
  change run 2 (by decide) (seed 2) ([.v] ++ singletonControlRound (defect, swap)) = some _
  rw [run_append, hp]
  simp only [Option.bind_some]
  cases defect with
  | true => exact two_defect_round_run swap
  | false =>
      have hs := singletonControlRound_stage_run 2 (by decide) 0 (by decide) swap
      have hend := singletonTransferStage_terminal 2 (by decide)
      change singletonTransferStage 2 (by decide) 1 (by decide) = _ at hend
      rw [hend] at hs
      exact hs

def twoSingletonOptimalWords : List (List Letter) :=
  [[.v, .p false, .p true, .v], [.v, .p true, .p false, .v],
    [.v, .d false, .p true, .v], [.v, .p true, .d false, .v]]

/-- The exceptional two-site model has exactly these four actual optimal
words, including two genuine lower-defect schedules. -/
theorem singleton_two_optimal_iff (word : List Letter) :
    (run 2 (by decide) (seed 2) word = some (upperSingletonEndpoint 2 (by decide)) ∧
      word.length = 4) ↔ word ∈ twoSingletonOptimalWords := by
  constructor
  · rintro ⟨hrun, hlen⟩
    obtain ⟨choices, hc, rfl⟩ := singleton_optimal_elevator_skeleton 2 (by decide) word hrun hlen
    have hc' : choices.length = 1 := hc
    obtain ⟨c, rfl⟩ := List.length_eq_one_iff.mp hc'
    rcases c with ⟨defect, swap⟩
    cases defect <;> cases swap <;>
      simp [singletonControlTail, singletonControlRound, singletonLowerChoice,
        twoSingletonOptimalWords]
  · intro hw
    simp only [twoSingletonOptimalWords, List.mem_cons, List.not_mem_nil, or_false] at hw
    rcases hw with rfl | rfl | rfl | rfl
    · exact ⟨singleton_two_control_round_run false false, rfl⟩
    · exact ⟨singleton_two_control_round_run false true, rfl⟩
    · exact ⟨singleton_two_control_round_run true false, rfl⟩
    · exact ⟨singleton_two_control_round_run true true, rfl⟩

def booleanChoiceLists : Nat → List (List Bool)
  | 0 => [[]]
  | k + 1 => (booleanChoiceLists k).map (false :: ·) ++
      (booleanChoiceLists k).map (true :: ·)

theorem booleanChoiceLists_mem (k : Nat) (bits : List Bool) :
    bits ∈ booleanChoiceLists k ↔ bits.length = k := by
  induction k generalizing bits with
  | zero => simp [booleanChoiceLists, List.length_eq_zero_iff]
  | succ k ih =>
      cases bits with
      | nil => simp [booleanChoiceLists]
      | cons b bs =>
          cases b <;> simp [booleanChoiceLists, ih]

theorem booleanChoiceLists_nodup (k : Nat) : (booleanChoiceLists k).Nodup := by
  induction k with
  | zero => simp [booleanChoiceLists]
  | succ k ih =>
      apply List.nodup_append.mpr
      refine ⟨?_, ?_, ?_⟩
      · apply ih.map (false :: ·)
        intro a b hab he
        exact hab (List.cons.inj he).2
      · apply ih.map (true :: ·)
        intro a b hab he
        exact hab (List.cons.inj he).2
      · intro a ha b hb he
        obtain ⟨as, _, rfl⟩ := List.mem_map.mp ha
        obtain ⟨bs, _, rfl⟩ := List.mem_map.mp hb
        simp at he

theorem booleanChoiceLists_length (k : Nat) :
    (booleanChoiceLists k).length = 2 ^ k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [booleanChoiceLists, ih, Nat.pow_succ, Nat.mul_two]

theorem singletonVariantWord_injective : Function.Injective singletonVariantWord := by
  intro xs ys he
  have hl := congrArg List.length he
  rw [singletonVariantWord_length, singletonVariantWord_length] at hl
  exact singletonVariantWord_injective_of_length (by omega) he

/-- Explicit finite enumeration of all optimal words at the fixed endpoint.
Its specification and lack of duplicates, together with its length, give
the exact cardinality without importing a separate finite-set library. -/
def singletonOptimalWords (n : Nat) : List (List Letter) :=
  if n = 2 then twoSingletonOptimalWords
  else (booleanChoiceLists (n - 1)).map singletonVariantWord

theorem singletonOptimalWords_mem_iff (n : Nat) (hn : 1 < n) (word : List Letter) :
    word ∈ singletonOptimalWords n ↔
      run n hn (seed n) word = some (upperSingletonEndpoint n (by omega)) ∧
        word.length = 3 * n - 2 := by
  by_cases htwo : n = 2
  · subst n
    exact (singleton_two_optimal_iff word).symm
  · have hn3 : 3 ≤ n := by omega
    rw [singleton_optimal_iff_variant n hn3]
    simp only [singletonOptimalWords, htwo, ite_false, List.mem_map]
    constructor
    · rintro ⟨bits, hb, he⟩
      exact ⟨bits, (booleanChoiceLists_mem _ _).mp hb, he.symm⟩
    · rintro ⟨bits, hb, he⟩
      exact ⟨bits, (booleanChoiceLists_mem _ _).mpr hb, he.symm⟩

theorem singletonOptimalWords_nodup (n : Nat) : (singletonOptimalWords n).Nodup := by
  by_cases htwo : n = 2
  · simp only [singletonOptimalWords, htwo, ite_true]
    decide
  · simp only [singletonOptimalWords, htwo, ite_false]
    apply (booleanChoiceLists_nodup _).map singletonVariantWord
    intro a b hab he
    exact hab (singletonVariantWord_injective he)

theorem singletonOptimalWords_length (n : Nat) :
    (singletonOptimalWords n).length = if n = 2 then 4 else 2 ^ (n - 1) := by
  by_cases htwo : n = 2
  · simp [singletonOptimalWords, htwo, twoSingletonOptimalWords]
  · simp [singletonOptimalWords, htwo, booleanChoiceLists_length]

/-- Exact finite-cardinality certificate for every `n > 1`: the list contains
every and only optimal actual raw words, each once, and has the stated size. -/
theorem singleton_optimal_words_exact_count (n : Nat) (hn : 1 < n) :
    (singletonOptimalWords n).Nodup ∧
      (singletonOptimalWords n).length = (if n = 2 then 4 else 2 ^ (n - 1)) ∧
      ∀ word : List Letter, word ∈ singletonOptimalWords n ↔
        run n hn (seed n) word = some (upperSingletonEndpoint n (by omega)) ∧
          word.length = 3 * n - 2 := by
  exact ⟨singletonOptimalWords_nodup n, singletonOptimalWords_length n,
    singletonOptimalWords_mem_iff n hn⟩

end RSR2.Parametric
