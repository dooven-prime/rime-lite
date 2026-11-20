import RSR2History.GlobalHistoryPremium
import Mathlib.Data.Finset.Max

/-! Exact finite raw-word search cutoffs. The alphabet and bounded word
enumeration are executable; acceptance uses the original classical guarded
semantics. These theorems do not certify a BFS implementation. -/

namespace RSR2History

open RSR2.Parametric AllRTransfer

def primitiveLetters : Finset Letter :=
  {.p false, .p true, .d false, .d true, .v}

@[simp] theorem mem_primitiveLetters (letter : Letter) : letter ∈ primitiveLetters := by
  cases letter with
  | p layer => cases layer <;> simp [primitiveLetters]
  | d layer => cases layer <;> simp [primitiveLetters]
  | v => simp [primitiveLetters]

/-- All raw words up to the cutoff. Guard failures are rejected separately. -/
def rawWordsUpTo : Nat → Finset (List Letter)
  | 0 => {[]}
  | bound + 1 => insert []
      ((primitiveLetters ×ˢ rawWordsUpTo bound).image (fun pair => pair.1 :: pair.2))

@[simp] theorem mem_rawWordsUpTo (word : List Letter) (bound : Nat) :
    word ∈ rawWordsUpTo bound ↔ word.length ≤ bound := by
  induction bound generalizing word with
  | zero => cases word <;> simp [rawWordsUpTo]
  | succ bound ih =>
      cases word with
      | nil => simp [rawWordsUpTo]
      | cons letter rest => simp [rawWordsUpTo, Finset.mem_product, ih]

noncomputable def boundedAcceptedWords (accepts : List Letter → Prop)
    (bound : Nat) : Finset (List Letter) := by
  classical
  exact (rawWordsUpTo bound).filter accepts

@[simp] theorem mem_boundedAcceptedWords (accepts : List Letter → Prop)
    (bound : Nat) (word : List Letter) :
    word ∈ boundedAcceptedWords accepts bound ↔ accepts word ∧ word.length ≤ bound := by
  classical
  simp [boundedAcceptedWords, and_comm]

theorem boundedAcceptedWords_nonempty (accepts : List Letter → Prop) (bound : Nat)
    (attain : ∃ word, accepts word ∧ word.length ≤ bound) :
    (boundedAcceptedWords accepts bound).Nonempty := by
  obtain ⟨word, hword⟩ := attain
  exact ⟨word, (mem_boundedAcceptedWords accepts bound word).2 hword⟩

/-- An actual minimum over the finite accepted-word search set. -/
noncomputable def boundedMinimumWordLength (accepts : List Letter → Prop)
    (bound : Nat) (attain : ∃ word, accepts word ∧ word.length ≤ bound) : Nat :=
  ((boundedAcceptedWords accepts bound).image List.length).min'
    ((boundedAcceptedWords_nonempty accepts bound attain).image List.length)

theorem boundedMinimumWordLength_spec (accepts : List Letter → Prop) (bound : Nat)
    (attain : ∃ word, accepts word ∧ word.length ≤ bound) :
    ∃ word, (accepts word ∧ word.length ≤ bound) ∧
      word.length = boundedMinimumWordLength accepts bound attain := by
  obtain ⟨word, hw, hlen⟩ := Finset.mem_image.mp
    (Finset.min'_mem ((boundedAcceptedWords accepts bound).image List.length)
      ((boundedAcceptedWords_nonempty accepts bound attain).image List.length))
  exact ⟨word, (mem_boundedAcceptedWords accepts bound word).1 hw, hlen⟩

theorem minimumWordLength_eq_bounded_minimum (accepts : List Letter → Prop)
    (attain : ∃ word, accepts word) (bound : Nat)
    (short : ∃ word, accepts word ∧ word.length ≤ bound) :
    minimumWordLength accepts attain = boundedMinimumWordLength accepts bound short := by
  obtain ⟨best, hbest, hbest_len⟩ := minimumWordLength_spec accepts attain
  have hbest_bound : best.length ≤ bound := by
    obtain ⟨word, hword, hlen⟩ := short
    have hmin := minimumWordLength_le accepts attain hword
    omega
  obtain ⟨boundedBest, hboundedBest, hboundedBest_len⟩ :=
    boundedMinimumWordLength_spec accepts bound short
  have hle := minimumWordLength_le accepts attain hboundedBest.1
  have hge := Finset.min'_le ((boundedAcceptedWords accepts bound).image List.length)
    best.length (Finset.mem_image_of_mem List.length
      ((mem_boundedAcceptedWords accepts bound best).2 ⟨hbest, hbest_bound⟩))
  change boundedMinimumWordLength accepts bound short ≤ best.length at hge
  omega

theorem history_bounded_attainable (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ word, runLogged n hn (seed n) word = some (Q, events) ∧
      word.length ≤ quadraticHistoryBudget n :=
  history_fiber_quadratic_bound n hn attain

theorem historyDistance_eq_bounded_minimum (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    historyDistance n hn Q events attain =
      boundedMinimumWordLength
        (fun word => runLogged n hn (seed n) word = some (Q, events))
        (quadraticHistoryBudget n) (history_bounded_attainable n hn attain) :=
  minimumWordLength_eq_bounded_minimum _ attain _ (history_bounded_attainable n hn attain)

theorem endpoint_log_attainable (n : Nat) (hn : 1 < n)
    {Q : Placement n} (attain : ∃ word, run n hn (seed n) word = some Q) :
    ∃ events, ∃ word, runLogged n hn (seed n) word = some (Q, events) := by
  obtain ⟨word, hword⟩ := attain
  obtain ⟨events, hevents⟩ := runLogged_exists_of_run n hn hword
  exact ⟨events, word, hevents⟩

theorem endpoint_bounded_attainable (n : Nat) (hn : 1 < n)
    {Q : Placement n} (attain : ∃ word, run n hn (seed n) word = some Q) :
    ∃ word, run n hn (seed n) word = some Q ∧
      word.length ≤ quadraticHistoryBudget n := by
  obtain ⟨events, loggedWord, hlogged⟩ := endpoint_log_attainable n hn attain
  obtain ⟨short, hshort, hlen⟩ := history_bounded_attainable n hn ⟨loggedWord, hlogged⟩
  exact ⟨short, by simpa [hshort] using (runLogged_project n hn (seed n) short).symm, hlen⟩

theorem endpointDistance_eq_bounded_minimum (n : Nat) (hn : 1 < n)
    (Q : Placement n) (attain : ∃ word, run n hn (seed n) word = some Q) :
    endpointDistance n hn Q attain =
      boundedMinimumWordLength (fun word => run n hn (seed n) word = some Q)
        (quadraticHistoryBudget n) (endpoint_bounded_attainable n hn attain) :=
  minimumWordLength_eq_bounded_minimum _ attain _ (endpoint_bounded_attainable n hn attain)

theorem historyPremium_eq_bounded_minima (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    historyPremium n hn Q events attain =
      boundedMinimumWordLength
        (fun word => runLogged n hn (seed n) word = some (Q, events))
        (quadraticHistoryBudget n) (history_bounded_attainable n hn attain) -
      boundedMinimumWordLength (fun word => run n hn (seed n) word = some Q)
        (quadraticHistoryBudget n)
        (endpoint_bounded_attainable n hn (endpoint_attainable_of_logged hn attain)) := by
  unfold historyPremium
  rw [historyDistance_eq_bounded_minimum, endpointDistance_eq_bounded_minimum]

/-- Both minimizations in the finite global maximum can be performed inside
the same proved raw-word cutoff. This is a completeness specification for
a search, not a correctness theorem for any external search implementation. -/
theorem globalHistoryPremium_eq_bounded_search (n : Nat) (hn : 1 < n) :
    globalHistoryPremium n hn = Finset.univ.sup
      (fun observation : AttainableObservation n hn =>
        boundedMinimumWordLength
          (fun word => runLogged n hn (seed n) word = some observation.val)
          (quadraticHistoryBudget n) (history_bounded_attainable n hn observation.2) -
        boundedMinimumWordLength
          (fun word => run n hn (seed n) word = some observation.val.1)
          (quadraticHistoryBudget n) (endpoint_bounded_attainable n hn
            (endpoint_attainable_of_logged hn observation.2))) := by
  unfold globalHistoryPremium
  apply Finset.sup_congr rfl
  intro observation _
  exact historyPremium_eq_bounded_minima n hn observation.val.1 observation.val.2 observation.2

/-- The cutoff covers exactly the attainable full observations. -/
theorem history_realizable_iff_bounded_search (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n)) :
    (∃ word, runLogged n hn (seed n) word = some (Q, events)) ↔
      ∃ word ∈ rawWordsUpTo (quadraticHistoryBudget n),
        runLogged n hn (seed n) word = some (Q, events) := by
  constructor
  · intro attain
    obtain ⟨word, hw, hlen⟩ := history_bounded_attainable n hn attain
    exact ⟨word, (mem_rawWordsUpTo word _).2 hlen, hw⟩
  · rintro ⟨word, _, hw⟩
    exact ⟨word, hw⟩

def boundedObservations (n : Nat) (hn : 1 < n) : Set (CompleteObservation n) :=
  { observation | ∃ word ∈ rawWordsUpTo (quadraticHistoryBudget n),
    runLogged n hn (seed n) word = some observation }

theorem boundedObservations_eq_attainable (n : Nat) (hn : 1 < n) :
    boundedObservations n hn = attainableObservations n hn := by
  ext observation
  exact (history_realizable_iff_bounded_search n hn observation.1 observation.2).symm

theorem boundedObservations_finite (n : Nat) (hn : 1 < n) :
    (boundedObservations n hn).Finite := by
  rw [boundedObservations_eq_attainable]
  exact attainableObservations_finite n hn

theorem endpoint_realizable_iff_bounded_search (n : Nat) (hn : 1 < n)
    (Q : Placement n) :
    (∃ word, run n hn (seed n) word = some Q) ↔
      ∃ word ∈ rawWordsUpTo (quadraticHistoryBudget n),
        run n hn (seed n) word = some Q := by
  constructor
  · intro attain
    obtain ⟨word, hw, hlen⟩ := endpoint_bounded_attainable n hn attain
    exact ⟨word, (mem_rawWordsUpTo word _).2 hlen, hw⟩
  · rintro ⟨word, _, hw⟩
    exact ⟨word, hw⟩

def boundedEndpoints (n : Nat) (hn : 1 < n) : Set (Placement n) :=
  { Q | ∃ word ∈ rawWordsUpTo (quadraticHistoryBudget n),
    run n hn (seed n) word = some Q }

theorem boundedEndpoints_eq_attainable (n : Nat) (hn : 1 < n) :
    boundedEndpoints n hn =
      { Q | ∃ word, run n hn (seed n) word = some Q } := by
  ext Q
  exact (endpoint_realizable_iff_bounded_search n hn Q).symm

theorem boundedEndpoints_finite (n : Nat) (hn : 1 < n) :
    (boundedEndpoints n hn).Finite := by
  exact Set.toFinite _

end RSR2History
