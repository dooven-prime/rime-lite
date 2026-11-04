import ProperArc.OriginAssembly

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def alignedExecution (c : ZMod n) : Execution n (ZMod n) :=
  ⟨fun q => some {c + q}, none, []⟩

theorem run_alignment (F : Finset (ZMod n)) (c : ZMod n) :
    run F (singletonExecution n) (pWord (-c).val) = alignedExecution c := by
  rw [run_rotation]
  unfold singletonExecution alignedExecution
  congr 1
  funext q
  simp [rotate, add_comm]

def parentsPlacement (c : ZMod n) (r t k : ℕ) : Placement n (Finset (ZMod n)) :=
  fun q => if q = 0 then some (interval c 0 t)
    else if q = (k : ZMod n) then some (interval c t r)
    else if q.val < r then none else some {c + q}

theorem assembled_parents_placement (c : ZMod n) (r t : ℕ)
    (hr : r ≤ n) (ht : 1 ≤ t) (htr : t < r) :
    segmentPlacement c t (r - t)
      (segmentPlacement c 0 t (alignedExecution c).placed) = parentsPlacement c r t t := by
  have hval : (t : ZMod n).val = t := ZMod.val_natCast_of_lt (by omega)
  have htne : (t : ZMod n) ≠ 0 := by
    intro h
    have := congrArg ZMod.val h
    simp only [hval, ZMod.val_zero] at this
    omega
  funext q
  by_cases hq0 : q = 0
  · subst q
    simp [segmentPlacement, parentsPlacement, htne.symm]
  by_cases hqt : q = (t : ZMod n)
  · subst q
    simp [segmentPlacement, parentsPlacement, htne, Nat.add_sub_of_le (by omega : t ≤ r)]
  · have hqv : 0 < q.val := by
      have hne : q.val ≠ 0 := by
        intro h
        apply hq0
        rw [← ZMod.natCast_zmod_val q, h]
        simp
      omega
    have hqvt : q.val ≠ t := by
      intro h
      apply hqt
      rw [← ZMod.natCast_zmod_val q, h]
    simp only [segmentPlacement, hqt, hq0, Nat.cast_zero, zero_add,
      show t + (r - t) = r by omega, parentsPlacement, ite_false, alignedExecution]
    split_ifs <;> simp_all <;> omega

def parentAssemblyWord (r t : ℕ) : List Letter :=
  assembleWord (n := n) 0 t ++ assembleWord (n := n) t (r - t)

theorem run_parentAssembly (c : ZMod n) (r t : ℕ)
    (hr : r ≤ n) (ht : 1 ≤ t) (htr : t < r) :
    run (arc c r) (alignedExecution c) (parentAssemblyWord (n := n) r t) =
      ⟨parentsPlacement c r t t, none, []⟩ := by
  have hleft := assemble_strict_parent c r t 0 (arc c r) (alignedExecution c)
    hr rfl ht htr (by omega) rfl (fun i _ _ => rfl)
  let s : Execution n (ZMod n) :=
    { alignedExecution c with placed := segmentPlacement c 0 t (alignedExecution c).placed }
  have hright : ∀ i, t ≤ i → i < t + (r - t) →
      s.placed (i : ZMod n) = some {c + (i : ZMod n)} := by
    intro i hi hj
    have hval : (i : ZMod n).val = i := ZMod.val_natCast_of_lt (by omega)
    have hne : (i : ZMod n) ≠ 0 := by
      intro h
      have := congrArg ZMod.val h
      rw [hval, ZMod.val_zero] at this
      omega
    simp [s, segmentPlacement, hne, hval, show ¬(0 < i ∧ i < t) by omega, alignedExecution]
  have hrightRun := assemble_strict_parent c r (r - t) t (arc c r) s
    hr rfl (by omega) (by omega) (by omega) rfl hright
  rw [parentAssemblyWord, run_append, hleft]
  rw [hrightRun]
  change (⟨segmentPlacement c t (r - t) (segmentPlacement c 0 t (alignedExecution c).placed),
    none, []⟩ : Execution n (ZMod n)) = _
  rw [assembled_parents_placement c r t hr ht htr]

def slideParentWord : ℕ → List Letter
  | 0 => []
  | k + 1 => localLetters ((k + 1 : ℕ) : ZMod n) ++ slideParentWord k

omit [NeZero n] in
theorem moveBack_parents (c : ZMod n) (r t k : ℕ)
    (hr : r ≤ n) (hk : 1 ≤ k) (hkr : k + 1 < r) :
    moveBack (k : ZMod n) (parentsPlacement c r t (k + 1)) =
      parentsPlacement c r t k := by
  have hvk : (k : ZMod n).val = k := ZMod.val_natCast_of_lt (by omega)
  have hvk1 : ((k + 1 : ℕ) : ZMod n).val = k + 1 := ZMod.val_natCast_of_lt (by omega)
  have hk0 : (k : ZMod n) ≠ 0 := by
    intro h
    have := congrArg ZMod.val h
    rw [hvk, ZMod.val_zero] at this
    omega
  have hk10 : ((k + 1 : ℕ) : ZMod n) ≠ 0 := by
    intro h
    have := congrArg ZMod.val h
    rw [hvk1, ZMod.val_zero] at this
    omega
  have hne : (k : ZMod n) ≠ ((k + 1 : ℕ) : ZMod n) := by
    intro h
    have := congrArg ZMod.val h
    rw [hvk, hvk1] at this
    omega
  have hcast : ((k + 1 : ℕ) : ZMod n) = (k : ZMod n) + 1 := by simp
  funext q
  by_cases hq : q = (k : ZMod n)
  · subst q
    simp only [moveBack, ite_true]
    rw [← hcast]
    simp only [parentsPlacement, hk0, hk10, ite_false, ite_true]
  by_cases hq1 : q = ((k + 1 : ℕ) : ZMod n)
  · subst q
    simp only [moveBack, hne.symm, ite_false, ← hcast, ite_true]
    simp only [parentsPlacement, hk10, hne.symm, ite_false, hvk1]
    rw [if_pos hkr]
  · simp only [moveBack, hq, ite_false, ← hcast, hq1, parentsPlacement]

theorem run_slideParents (c : ZMod n) (r t k : ℕ)
    (hr : r ≤ n) (hk : k + 1 < r) :
    run (arc c r) ⟨parentsPlacement c r t (k + 1), none, []⟩ (slideParentWord (n := n) k) =
      ⟨parentsPlacement c r t 1, none, []⟩ := by
  induction k with
  | zero => rfl
  | succ k ih =>
    have hv : ((k + 1 : ℕ) : ZMod n).val = k + 1 := ZMod.val_natCast_of_lt (by omega)
    have hv2 : ((k + 2 : ℕ) : ZMod n).val = k + 2 := ZMod.val_natCast_of_lt (by omega)
    have h0 : ((k + 1 : ℕ) : ZMod n) ≠ 0 := by
      intro h
      have := congrArg ZMod.val h
      rw [hv, ZMod.val_zero] at this
      omega
    have hne : ((k + 1 : ℕ) : ZMod n) ≠ ((k + 2 : ℕ) : ZMod n) := by
      intro h
      have := congrArg ZMod.val h
      rw [hv, hv2] at this
      omega
    have hole : parentsPlacement c r t (k + 1 + 1) ((k + 1 : ℕ) : ZMod n) = none := by
      simp only [show k + 1 + 1 = k + 2 by omega, parentsPlacement, h0, hne,
        ite_false, hv, show k + 1 < r by omega, ite_true]
    rw [slideParentWord, run_append, run_localLetters_safe (arc c r) _ _ (by omega) hole]
    rw [moveBack_parents c r t (k + 1) hr (by omega) (by omega)]
    exact ih (by omega)

def originPrefix (c : ZMod n) (r t : ℕ) : List Letter :=
  pWord (-c).val ++ parentAssemblyWord (n := n) r t ++ slideParentWord (n := n) (t - 1)

def originWord (c : ZMod n) (r t : ℕ) : List Letter := originPrefix c r t ++ [.d]

theorem run_originPrefix (c : ZMod n) (r t : ℕ)
    (hr : r < n) (ht : 1 ≤ t) (htr : t < r) :
    run (arc c r) (singletonExecution n) (originPrefix c r t) =
      ⟨parentsPlacement c r t 1, none, []⟩ := by
  have hs := run_slideParents c r t (t - 1) (by omega) (by omega)
  rw [show t - 1 + 1 = t by omega] at hs
  rw [originPrefix, run_append, run_append, run_alignment,
    run_parentAssembly c r t (by omega) ht htr, hs]

def boundaryPlacement (c : ZMod n) (r : ℕ) : Placement n (Finset (ZMod n)) :=
  fun q => if q = 0 then some (arc c r)
    else if q.val < r then none else some {c + q}

theorem fusionParents_boundary (c : ZMod n) (r t : ℕ)
    (hr : r ≤ n) (ht : 1 ≤ t) (htr : t < r) :
    fusionPlacement (parentsPlacement c r t 1) = boundaryPlacement c r := by
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  have hval1 : (1 : ZMod n).val = 1 := by
    simpa only [Nat.cast_one] using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
  have hunion : interval c 0 t ∪ interval c t r = arc c r :=
    originRecord_union c r t (by omega) hr
  funext q
  by_cases hq0 : q = 0
  · subst q
    simp [fusionPlacement, parentsPlacement, boundaryPlacement, h10, hunion]
  by_cases hq1 : q = 1
  · subst q
    simp [fusionPlacement, boundaryPlacement, h10, hval1, show 1 < r by omega]
  · simp [fusionPlacement, parentsPlacement, boundaryPlacement, hq0, hq1]

/-- Every legal internal cut is realized by the same explicit chronological
word scheme, with literal common boundary placement and no selected absorption. -/
theorem run_originWord (c : ZMod n) (r t : ℕ)
    (hr : r < n) (ht : 1 ≤ t) (htr : t < r) :
    run (arc c r) (singletonExecution n) (originWord c r t) =
      ⟨boundaryPlacement c r, some (originRecord c r t), []⟩ := by
  rw [originWord, run_append, run_originPrefix c r t hr ht htr]
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  have h0 : parentsPlacement c r t 1 0 = some (interval c 0 t) := by
    simp [parentsPlacement]
  have h1 : parentsPlacement c r t 1 1 = some (interval c t r) := by
    simp [parentsPlacement, h10]
  have hunion : interval c 0 t ∪ interval c t r = arc c r :=
    originRecord_union c r t (by omega) (by omega)
  change stepDefect (arc c r) ⟨parentsPlacement c r t 1, none, []⟩ = _
  unfold stepDefect
  dsimp only
  rw [h0, h1]
  simp only [hunion, Option.isNone_none, Bool.true_and, decide_true,
    ite_true, Option.isSome_none, Bool.false_and]
  rw [fusionParents_boundary c r t (by omega) ht htr]
  rfl

theorem distinct_cut_origins (c : ZMod n) (r : ℕ) (hr : r < n)
    (i j : Fin (r - 1)) (hne : i ≠ j) :
    (run (arc c r) (singletonExecution n) (originWord c r (i.val + 1))).origin ≠
      (run (arc c r) (singletonExecution n) (originWord c r (j.val + 1))).origin := by
  rw [run_originWord c r _ hr (by omega) (by omega),
    run_originWord c r _ hr (by omega) (by omega)]
  intro heq
  apply hne
  apply originRecord_injective c r (by omega)
  exact Option.some.inj heq

omit [NeZero n] in
theorem run_origin_of_some (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (record : FusionRecord (ZMod n)) (h : s.origin = some record) (word : List Letter) :
    (run F s word).origin = some record := by
  induction word generalizing s with
  | nil => exact h
  | cons letter rest ih =>
    apply ih (step F s letter)
    cases letter with
    | p => exact h
    | d =>
      unfold step stepDefect
      cases hp0 : s.placed 0 <;> cases hp1 : s.placed 1 <;> simp [h]

/-- No earlier prefix of the explicit pre-terminal word can already have
registered F: the real interpreter never erases an origin. -/
theorem originPrefix_no_early_registration (c : ZMod n) (r t : ℕ)
    (hr : r < n) (ht : 1 ≤ t) (htr : t < r)
    (u v : List Letter) (hword : u ++ v = originPrefix c r t) :
    (run (arc c r) (singletonExecution n) u).origin = none := by
  have hfinal : (run (arc c r) (singletonExecution n) (u ++ v)).origin = none := by
    rw [hword, run_originPrefix c r t hr ht htr]
  rw [run_append] at hfinal
  cases hearly : (run (arc c r) (singletonExecution n) u).origin with
  | none => rfl
  | some record =>
    have hp := run_origin_of_some (arc c r) _ record hearly v
    rw [hfinal] at hp
    contradiction

omit [NeZero n] in
theorem boundary_clean (c : ZMod n) (r : ℕ) :
    (∃ q, boundaryPlacement c r q = some (arc c r)) ∧
      ∀ q B, boundaryPlacement c r q = some B →
        B = arc c r ∨ ∃ a, B = {a} := by
  refine ⟨⟨0, by simp [boundaryPlacement]⟩, ?_⟩
  intro q B hB
  by_cases hq : q = 0
  · subst q
    simp only [boundaryPlacement, ite_true, Option.some.injEq] at hB
    exact Or.inl hB.symm
  by_cases hqr : q.val < r
  · simp [boundaryPlacement, hq, hqr] at hB
  · simp only [boundaryPlacement, hq, hqr, ite_false, Option.some.injEq] at hB
    exact Or.inr ⟨c + q, hB.symm⟩

end ProperArc
