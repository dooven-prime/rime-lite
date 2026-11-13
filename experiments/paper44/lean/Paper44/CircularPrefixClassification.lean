import Paper44.CircularPrefixInstance
import FutureEvent.FutureClassification

/-!
# Structural classification on actual circular states

The future-event classification is reused, not reproved. Retaining a prefix
refines each future-equivalence class exactly by equality of its current
label. In particular all literal terminal phases have identical futures;
terminal prefix equivalence is precisely retained-label equality.

The terminal-label range equivalence and count are proved separately in
`TerminalLabelEquiv`; this module establishes only the semantic criterion.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

/-- Both companions define generated states by the same actual raw run. -/
theorem circularGenerated_iff_pairGenerated (s : Execution n (ZMod n)) :
    CircularGenerated s ↔ PairGenerated s := Iff.rfl

/-- All-region classification with the explicit retained-label refinement. -/
theorem circular_prefix_classification (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x y : CircularState n) :
    (circularPrefixMachine hn j hj).ObserverEq x y ↔
      FutureNormalFormEq x.val y.val ∧
        circularLabel j x.val = circularLabel j y.val := by
  rw [circular_observerEq_iff,
    futureEquivalent_iff_normalForm x.val y.val hn x.property y.property]

/-- A still-registerable pre-registration state retains its literal placement. -/
theorem circular_preregistration_observerEq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x y : CircularState n)
    (hx : PairRegisterable x.val) (hy : PairRegisterable y.val) :
    (circularPrefixMachine hn j hj).ObserverEq x y ↔ x.val.placed = y.val.placed := by
  rw [circular_prefix_classification]
  constructor
  · rintro ⟨hfuture, _⟩
    rcases hfuture with ⟨hsilent, _⟩ | ⟨_, _, hp⟩ | ⟨hr, _, _⟩
    · exact False.elim (silentRegion_not_registerable _ hsilent hx)
    · exact hp
    · exact False.elim (registerable_not_registered _ hx hr.1)
  · intro hp
    exact ⟨Or.inr (Or.inl ⟨hx, hy, hp⟩), by simp [circularLabel, hx.1, hy.1]⟩

/-- On the registered nonterminal region, keep placement and prefix label. -/
theorem circular_nonterminal_observerEq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x y : CircularState n)
    (hx : RegisteredNonterminal x.val) (hy : RegisteredNonterminal y.val) :
    (circularPrefixMachine hn j hj).ObserverEq x y ↔
      x.val.placed = y.val.placed ∧ circularLabel j x.val = circularLabel j y.val := by
  rw [circular_prefix_classification]
  constructor
  · rintro ⟨hfuture, hlabel⟩
    rcases hfuture with ⟨hsilent, _⟩ | ⟨hr, _, _⟩ | ⟨_, _, hp⟩
    · exact False.elim (silentRegion_not_registeredNonterminal _ hsilent hx)
    · exact False.elim (registerable_not_registered _ hr hx.1)
    · exact ⟨hp, hlabel⟩
  · rintro ⟨hp, hlabel⟩
    exact ⟨Or.inr (Or.inr ⟨hx, hy, hp⟩), hlabel⟩

/-- A terminal carrier's physical phase is absent from this observer. -/
theorem circular_terminal_observerEq_iff_label (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x y : CircularState n) (hx : RankOnePlacement x.val) (hy : RankOnePlacement y.val) :
    (circularPrefixMachine hn j hj).ObserverEq x y ↔
      circularLabel j x.val = circularLabel j y.val := by
  rw [circular_observerEq_iff]
  constructor
  · exact And.right
  · intro hlabel
    refine ⟨?_, hlabel⟩
    intro word
    exact (rankOne_trace_null x.val (by omega) hx word).trans
      (rankOne_trace_null y.val (by omega) hy word).symm

end Paper44
