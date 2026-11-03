import FutureEvent.CrossRegionSeparation

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The three structural alternatives in equation (6.1). This definition
contains no universal trace comparison. -/
def FutureNormalFormEq (x y : Execution n (ZMod n)) : Prop :=
  (SilentRegion x ∧ SilentRegion y) ∨
    (PairRegisterable x ∧ PairRegisterable y ∧ x.placed = y.placed) ∨
    (RegisteredNonterminal x ∧ RegisteredNonterminal y ∧ x.placed = y.placed)

theorem futureNormalForm_sound (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (h : FutureNormalFormEq x y) : FutureEquivalent {0, 1} x y := by
  rcases h with ⟨hx, hy⟩ | ⟨hx, hy, hp⟩ | ⟨hx, hy, hp⟩
  · exact silentRegion_futureEquivalent x y (by omega) hx hy
  · have heq := generated_unregistered_same_placement_eq x y hxgen hygen hx.1 hy.1 hp
    subst y
    exact futureEquivalent_refl {0, 1} x
  · exact registered_same_placement_futureEquivalent {0, 1} x y hx.1 hy.1 hp

/-- Every pair outside the declared structural classes has a common actual
distinguishing suffix. Counting the classes is a separate theorem surface. -/
theorem normalForm_inequality_uniform_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hne : ¬ FutureNormalFormEq x y) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 6 * n - 10 := by
  rcases region_trichotomy x with hx | hx | hx
  · rcases region_trichotomy y with hy | hy | hy
    · exact False.elim (hne (Or.inl ⟨hx, hy⟩))
    · obtain ⟨word, hsep, hlength⟩ := registerable_silent_separation y x hn hygen hy hx
      exact ⟨word, hsep.symm, by omega⟩
    · obtain ⟨word, hsep, hlength⟩ := registered_silent_separation y x hn hygen hy hx
      exact ⟨word, hsep.symm, by omega⟩
  · rcases region_trichotomy y with hy | hy | hy
    · obtain ⟨word, hsep, hlength⟩ := registerable_silent_separation x y hn hxgen hx hy
      exact ⟨word, hsep, by omega⟩
    · have hxy : x ≠ y := by
        intro heq
        exact hne (Or.inr (Or.inl ⟨hx, hy, congrArg Execution.placed heq⟩))
      exact registerable_pair_separation x y hn hxgen hygen hx hy hxy
    · obtain ⟨word, hsep, hlength⟩ := registerable_registered_separation x y hn hxgen hx hy.1
      exact ⟨word, hsep, by omega⟩
  · rcases region_trichotomy y with hy | hy | hy
    · obtain ⟨word, hsep, hlength⟩ := registered_silent_separation x y hn hxgen hx hy
      exact ⟨word, hsep, by omega⟩
    · obtain ⟨word, hsep, hlength⟩ := registerable_registered_separation y x hn hygen hy hx.1
      exact ⟨word, hsep.symm, by omega⟩
    · have hp : x.placed ≠ y.placed := by
        intro heq
        exact hne (Or.inr (Or.inr ⟨hx, hy, heq⟩))
      obtain ⟨word, hsep, hlength⟩ := registered_nonterminal_separation x y hn hxgen hygen hx hy.1 hp
      exact ⟨word, hsep, by omega⟩

/-- The behavioral classification of Theorem 1, on actual singleton-seed
generated states, without the subsequent cardinality formula. -/
theorem futureEquivalent_iff_normalForm (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y) :
    FutureEquivalent {0, 1} x y ↔ FutureNormalFormEq x y := by
  constructor
  · intro h
    by_contra hne
    obtain ⟨word, hsep, _⟩ := normalForm_inequality_uniform_separation x y hn hxgen hygen hne
    exact hsep (h word)
  · exact futureNormalForm_sound x y hn hxgen hygen

/-- The uniform distinguishing-length statement for all three regions. -/
theorem future_inequivalence_uniform_separation (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (hne : ¬ FutureEquivalent {0, 1} x y) :
    ∃ word : List Letter, eventTrace {0, 1} x word ≠ eventTrace {0, 1} y word ∧
      word.length ≤ 6 * n - 10 := by
  apply normalForm_inequality_uniform_separation x y hn hxgen hygen
  intro hkey
  exact hne ((futureEquivalent_iff_normalForm x y hn hxgen hygen).mpr hkey)

theorem bounded_traces_iff_futureEquivalent (x y : Execution n (ZMod n))
    (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y) :
    (∀ word : List Letter, word.length ≤ 6 * n - 10 →
      eventTrace {0, 1} x word = eventTrace {0, 1} y word) ↔
      FutureEquivalent {0, 1} x y := by
  constructor
  · intro h
    by_contra hne
    obtain ⟨word, hsep, hlength⟩ := future_inequivalence_uniform_separation x y hn hxgen hygen hne
    exact hsep (h word hlength)
  · intro h word _
    exact h word

theorem futureNormalForm_right_congruent (x y : Execution n (ZMod n))
    (word : List Letter) (hn : 3 ≤ n) (hxgen : PairGenerated x) (hygen : PairGenerated y)
    (h : FutureNormalFormEq x y) :
    FutureNormalFormEq (run {0, 1} x word) (run {0, 1} y word) := by
  apply (futureEquivalent_iff_normalForm _ _ hn
    (pairGenerated_run x word hxgen) (pairGenerated_run y word hygen)).mp
  exact futureEquivalent_right_congruent {0, 1} x y
    (futureNormalForm_sound x y hn hxgen hygen h) word

end FutureEvent
