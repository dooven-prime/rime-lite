import ProperArc
import RegisteredAbsorptionChains.CleanChainWitness

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Both kernel sites are occupied: this is a real fusion, not an invocation
of the empty-port routing lemma. The union must still be a strict parent of F. -/
theorem localLetters_fuse_adjacent (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (j : ZMod n) (U V : Finset (ZMod n)) (hn : 2 ≤ n)
    (h0 : s.placed j = some U) (h1 : s.placed (j + 1) = some V)
    (horigin : s.origin = none) (hnot : U ∪ V ≠ F) :
    let z := run F s (localLetters j)
    z.placed j = some (U ∪ V) ∧ z.placed (j + 1) = none ∧
      (∀ q, q ≠ j → q ≠ j + 1 → z.placed q = s.placed q) ∧
      z.origin = none ∧ z.chain = s.chain := by
  rw [run_local_unregistered F s j U V h0 h1 horigin hnot]
  have hne : j + 1 ≠ j := by
    intro h
    have h10 : (1 : ZMod n) = 0 := add_left_cancel (show j + 1 = j + 0 by simpa using h)
    have := ZMod.one_eq_zero_iff.mp h10
    omega
  refine ⟨?_, ?_, ?_, horigin, rfl⟩
  · simp only [localFusion, ite_true, h0, h1]
  · simp only [localFusion, hne, ite_false, ite_true]
  · intro q hq hq1
    simp only [localFusion, hq, hq1, ite_false]

/-- The existential API retains the explicit, computable word as its witness. -/
theorem originCut_reaches_common_boundary (c : ZMod n) (r t : ℕ)
    (_hn : 3 ≤ n) (hr : 2 ≤ r ∧ r < n) (ht : 1 ≤ t ∧ t < r) :
    ∃ w : List Letter,
      let s := run (arc c r) (singletonExecution n) w
      s.origin = some (originRecord c r t) ∧ s.chain = [] ∧
        s.placed = boundaryPlacement c r := by
  refine ⟨originWord c r t, ?_⟩
  rw [run_originWord c r t hr.2 ht.1 ht.2]
  exact ⟨rfl, rfl, rfl⟩

theorem originWords_same_boundary (c : ZMod n) (r t u : ℕ)
    (hr : r < n) (ht : 1 ≤ t ∧ t < r) (hu : 1 ≤ u ∧ u < r) :
    (run (arc c r) (singletonExecution n) (originWord c r t)).placed =
      (run (arc c r) (singletonExecution n) (originWord c r u)).placed ∧
    (run (arc c r) (singletonExecution n) (originWord c r t)).placed =
      boundaryPlacement c r := by
  rw [run_originWord c r t hr ht.1 ht.2, run_originWord c r u hr hu.1 hu.2]
  exact ⟨rfl, rfl⟩

theorem originWord_clean (c : ZMod n) (r t : ℕ)
    (hr : r < n) (ht : 1 ≤ t ∧ t < r) :
    CleanOutside (arc c r) (run (arc c r) (singletonExecution n) (originWord c r t)) := by
  rw [run_originWord c r t hr ht.1 ht.2]
  exact boundary_clean c r

theorem originWord_reachable (c : ZMod n) (r t : ℕ) :
    ReachableExecution (arc c r) (run (arc c r) (singletonExecution n) (originWord c r t)) :=
  ⟨originWord c r t, rfl⟩

end ProperArc
