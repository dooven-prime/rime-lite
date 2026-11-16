import RSR2.CanonicalEndpoint

/-!
Partial upper loading, with an explicit reserved lower singleton family.
The generated instructions and guarded semantics are unchanged.  Unlike the
full Bell loader, this interface does not require every atom to be loaded.
-/

namespace RSR2.Parametric

/-- The coordinate model remains exact when a disjoint tail of atoms is
reserved below.  The phase is existential because lower rotations are shared
by the whole lower layer. -/
theorem partialLoading_coordinates
    (n : Nat) (hn : 1 < n) (xs : List (Fin n × Bool))
    (reserved : List (Fin n)) (phase k : Nat) (first : Bool)
    (P : Placement n)
    (hupper : upperSupportBelow P k) (hk : k + xs.length ≤ n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (xs.map Prod.fst ++ reserved) phase)
    (hnodup : (xs.map Prod.fst ++ reserved).Nodup)
    (hsub : lowerSupportSubset P (xs.map Prod.fst ++ reserved)) :
    ∃ R finalPhase,
      GuardedPlan n hn first P (annotateMarked n phase xs) R ∧
      lowerFamily R reserved finalPhase ∧ lowerSupportSubset R reserved ∧
      (∀ a, upperCoordinate R a =
        packAtom first xs a (upperCoordinate P a)) := by
  induction xs generalizing phase k first P with
  | nil => exact ⟨P, phase, .nil first P, hfamily, hsub, fun _ => rfl⟩
  | cons x rest ih =>
      rcases x with ⟨a, continues⟩
      let q : Fin n := ⟨(a.val + phase) % n, Nat.mod_lt _ (by omega)⟩
      let i : LoadInstruction n := ⟨a, lowerBackCount n q, continues⟩
      have hk' : k < n := by simp only [List.length_cons] at hk; omega
      have hkrest : (k + 1) + rest.length ≤ n := by
        simp only [List.length_cons] at hk; omega
      have hf : lowerFamily P (i.atom :: (rest.map Prod.fst ++ reserved)) phase :=
        hfamily
      have hd : (i.atom :: (rest.map Prod.fst ++ reserved)).Nodup := hnodup
      have hs : lowerSupportSubset P (i.atom :: (rest.map Prod.fst ++ reserved)) :=
        hsub
      have halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0 := by
        simpa [i, q] using lowerBackCount_phaseSite_aligns n (by omega) a phase
      have hg := liftGuard_of_loadingInvariant n hn P
        (i.atom :: (rest.map Prod.fst ++ reserved)) phase k first i
        hupper hk' (by simp) hf halign hfirst
      have hi := loadingInvariant_after_instructionResult_cons n hn P
        (rest.map Prod.fst ++ reserved) phase k first i
        hupper hk' hfirst hf hd halign
      have hsnext := lowerSupportSubset_after_instructionResult_tail n hn P
        (rest.map Prod.fst ++ reserved) phase first i hs hf halign
      obtain ⟨R, finalPhase, hgr, hr, hsr, hc⟩ := ih
        (phase := phase + i.sourceTurns) (k := k + 1) (first := false)
        (P := instructionResult n hn first P i)
        hi.1 hkrest (by simp) hi.2.1 hi.2.2 hsnext
      refine ⟨R, finalPhase, ?_, hr, hsr, ?_⟩
      · change GuardedPlan n hn first P
          (i :: annotateMarked n (phase + i.sourceTurns) rest) R
        exact .cons hg hgr
      · intro b
        rw [hc b]
        have he := instructionResult_upperCoordinate n hn P
          (rest.map Prod.fst ++ reserved) phase k first i
          hupper hk' hfirst hf hd hs halign b
        simpa only [packAtom, i] using congrArg (packAtom false rest b) he

end RSR2.Parametric
