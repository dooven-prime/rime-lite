import RegisteredAbsorptionChains.NamedOutsideMerge
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]

/-- The first `ell` outside named blocks are precisely the source-addressed
pieces of the desired R partner. -/
def RPartnerPrefix (first : LegalNamedPlacement n r (ZMod n))
    (B : Finset (ZMod n)) (ell : ℕ) : Prop :=
  0 < ell ∧ ell < r ∧
  (∀ i : ℕ, 1 ≤ i → i ≤ ell → first.block (i : ZMod r) ⊆ B) ∧
  (∀ a ∈ B, ∃ i : ℕ, 1 ≤ i ∧ i ≤ ell ∧
    a ∈ first.block (i : ZMod r))

theorem RPartnerPrefix.one_eq
    (first : LegalNamedPlacement n r (ZMod n))
    (B : Finset (ZMod n))
    (h : RPartnerPrefix first B 1) :
    first.block ((1 : ℕ) : ZMod r) = B := by
  apply Finset.Subset.antisymm (h.2.2.1 1 (by omega) (by omega))
  intro a ha
  obtain ⟨i, hi1, hi2, hmem⟩ := h.2.2.2 a ha
  have : i = 1 := by omega
  simpa [this] using hmem

theorem RPartnerPrefix.step
    [NeZero (r - 1)]
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (B : Finset (ZMod n))
    (ell : ℕ) (hr : 3 ≤ r) (hmore : 1 < ell)
    (h : RPartnerPrefix first B ell) :
    RPartnerPrefix
      (merge_named_outside first hrn 1 (by omega)) B (ell - 1) := by
  obtain ⟨hpos, hlt, hsubset, hcover⟩ := h
  obtain ⟨_, hmerge, htail⟩ := merge_named_R_blocks first hrn hr
  refine ⟨by omega, by omega, ?_, ?_⟩
  · intro i hi1 hile
    by_cases hi : i = 1
    · subst i
      rw [hmerge]
      exact Finset.union_subset
        (hsubset 1 (by omega) (by omega))
        (hsubset 2 (by omega) (by omega))
    · have hi2 : 2 ≤ i := by omega
      rw [htail i hi2 (by omega)]
      exact hsubset (i + 1) (by omega) (by omega)
  · intro a ha
    obtain ⟨i, hi1, hile, hmem⟩ := hcover a ha
    by_cases hi2 : i ≤ 2
    · refine ⟨1, by omega, by omega, ?_⟩
      rw [hmerge]
      interval_cases i <;> simp_all
    · refine ⟨i - 1, by omega, by omega, ?_⟩
      rw [htail (i - 1) (by omega) (by omega)]
      simpa [show i - 1 + 1 = i by omega] using hmem

/-- Concatenation keeps the concrete midpoint of two assembly schedules. -/
theorem OutsideAssemblySchedule.trans
    {F C : Finset (ZMod n)} {s mid : Execution n (ZMod n)}
    (head : OutsideAssemblySchedule F C s mid) :
    ∀ {final : Execution n (ZMod n)},
      OutsideAssemblySchedule F C mid final →
        OutsideAssemblySchedule F C s final := by
  induction head with
  | empty _ =>
      intro final tail
      exact tail
  | @merge s mid r _ first second hn hr source same u v h0 h1
      registered selected inside leftOutside rightOutside carrier tail ih =>
      intro final rest
      exact .merge first second hn hr source same u v h0 h1
        registered selected inside leftOutside rightOutside carrier (ih rest)

/-- The index counts genuine outside-merge stages, not occurrences of the
letter `d` inside the fusion-free placement routes. -/
inductive CountedOutsideSchedule (F C : Finset (ZMod n)) :
    ℕ → Execution n (ZMod n) → Execution n (ZMod n) → Prop where
  | empty (s : Execution n (ZMod n)) : CountedOutsideSchedule F C 0 s s
  | merge {s final : Execution n (ZMod n)} {r k : ℕ} [NeZero r]
      (first second : LegalNamedPlacement n r (ZMod n))
      (hn : 2 ≤ n) (hr : 2 ≤ r)
      (source : s.placed = first.placed)
      (same : SameOrientedCyclicOrder first second)
      (u v : Finset (ZMod n))
      (h0 : second.placed 0 = some u)
      (h1 : second.placed 1 = some v)
      (registered : s.origin.isSome = true)
      (selected : F.Nonempty) (inside : F ⊆ C)
      (leftOutside : Disjoint C u) (rightOutside : Disjoint C v)
      (carrier : ∃ q, second.placed q = some C ∧ q ≠ 0 ∧ q ≠ 1)
      (tail : CountedOutsideSchedule F C k
        { s with placed := fusionPlacement second.placed } final) :
      CountedOutsideSchedule F C (k + 1) s final

theorem CountedOutsideSchedule.toSchedule
    {F C : Finset (ZMod n)} {k : ℕ}
    {s final : Execution n (ZMod n)}
    (h : CountedOutsideSchedule F C k s final) :
    OutsideAssemblySchedule F C s final := by
  induction h with
  | empty s => exact .empty s
  | @merge s final r k _ first second hn hr source same u v h0 h1
      registered selected inside leftOutside rightOutside carrier tail ih =>
      exact .merge first second hn hr source same u v h0 h1
        registered selected inside leftOutside rightOutside carrier ih

theorem CountedOutsideSchedule.realize
    {F C : Finset (ZMod n)} {k : ℕ}
    {s final : Execution n (ZMod n)}
    (h : CountedOutsideSchedule F C k s final) :
    ∃ word : List Letter,
      run F s word = final ∧
      final.origin = s.origin ∧ final.chain = s.chain :=
  h.toSchedule.realize

theorem CountedOutsideSchedule.trans
    {F C : Finset (ZMod n)} {p : ℕ}
    {s mid : Execution n (ZMod n)}
    (head : CountedOutsideSchedule F C p s mid) :
    ∀ {q : ℕ} {final : Execution n (ZMod n)},
      CountedOutsideSchedule F C q mid final →
        CountedOutsideSchedule F C (p + q) s final := by
  induction head with
  | empty _ =>
      intro q final tail
      simpa using tail
  | @merge s mid r k _ first second hn hr source same u v h0 h1
      registered selected inside leftOutside rightOutside carrier tail ih =>
      intro q final rest
      simpa [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc] using
        (CountedOutsideSchedule.merge first second hn hr source same u v h0 h1
          registered selected inside leftOutside rightOutside carrier (ih rest))

/-- One adjacent packed merger contributes exactly one counted stage. -/
theorem packed_adjacent_partner_schedule_count
    (F C : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (source : s.placed = first.placed)
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftOutside : Disjoint C (first.block (j : ZMod r)))
    (rightOutside : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r))) :
    CountedOutsideSchedule F C 1 s
      ({ s with placed :=
        fusionPlacement ((packedLegalNamed first hrn (-(j : ZMod n))).placed) } :
        Execution n (ZMod n)) := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  obtain ⟨h0, h1, qC, hC, hq0, hq1⟩ :=
    packed_outside_ports_with_carrier first hrn j hjpos hj
  have hr : 2 ≤ r := by omega
  have hn : 2 ≤ n := by omega
  exact CountedOutsideSchedule.merge first target hn hr source
    (packedLegalNamed_same_order first ordered hrn (-(j : ZMod n)))
    (first.block (j : ZMod r))
    (first.block ((j + 1 : ℕ) : ZMod r))
    h0 h1 registered selected inside leftOutside rightOutside
    ⟨qC, by simpa [hcarrier] using hC, hq0, hq1⟩
    (CountedOutsideSchedule.empty _)

/-- Repeatedly fuse the first two outside blocks and retain the exact final
named placement, with the prescribed partner still at index one. -/
theorem RPartnerPrefix.assemble_named (ell : ℕ) :
    ∀ {r : ℕ} [NeZero r]
      (F C B : Finset (ZMod n))
      (s : Execution n (ZMod n))
      (first : LegalNamedPlacement n r (ZMod n)),
      first.PositivelyOrdered → r ≤ n → s.placed = first.placed →
      first.block 0 = C → s.origin.isSome = true →
      F.Nonempty → F ⊆ C → PartnerAssemblyInvariant C B s →
      RPartnerPrefix first B ell →
      ∃ (m : ℕ) (hm : NeZero m),
        letI : NeZero m := hm
        ∃ (final : Execution n (ZMod n))
          (lastNamed : LegalNamedPlacement n m (ZMod n)),
          m = r - ell + 1 ∧
          final.placed = lastNamed.placed ∧
          lastNamed.PositivelyOrdered ∧
          lastNamed.block 0 = C ∧
          lastNamed.block 1 = B ∧
          CountedOutsideSchedule F C (ell - 1) s final ∧
          PartnerAssemblyInvariant C B final := by
  induction ell with
  | zero =>
      intro r _ F C B s first ordered hrn source hcarrier registered
        selected inside hinvariant hprefix
      exact False.elim (Nat.not_succ_le_zero 0 hprefix.1)
  | succ k ih =>
      intro r _ F C B s first ordered hrn source hcarrier registered
        selected inside hinvariant hprefix
      by_cases hk : k = 0
      · subst k
        have hB := RPartnerPrefix.one_eq first B hprefix
        refine ⟨r, inferInstance, s, first, ?_, source, ordered, hcarrier,
          ?_, .empty s, hinvariant⟩
        · have := hprefix.2.1
          omega
        · simpa only [Nat.cast_one] using hB
      · have hmore : 1 < k + 1 := by omega
        have hr : 3 ≤ r := by have := hprefix.2.1; omega
        letI : NeZero (r - 1) := ⟨by omega⟩
        let next := merge_named_outside first hrn 1 (by omega)
        let s1 : Execution n (ZMod n) := { s with placed := next.placed }
        have hprefix1 : RPartnerPrefix next B k := by
          simpa only [Nat.add_sub_cancel_right] using
            RPartnerPrefix.step first hrn B (k + 1) hr hmore hprefix
        have hnextordered : next.PositivelyOrdered :=
          merge_named_outside_positive first hrn 1 (by omega) (by omega)
        have hnextcarrier : next.block 0 = C := by
          rw [merge_named_outside_zero first hrn 1 (by omega) (by omega)]
          exact hcarrier
        have hfirst : CountedOutsideSchedule F C 1 s s1 := by
          simpa only [s1, next, merge_named_outside] using
            packed_adjacent_partner_schedule_count F C s first ordered hrn source
              1 (by omega) (by omega) hcarrier registered selected inside
              (by
                rw [← hcarrier]
                exact first.block_disjoint _ _ (by
                  intro h
                  have hv := congrArg ZMod.val h
                  rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by omega)] at hv
                  omega))
              (by
                rw [← hcarrier]
                exact first.block_disjoint _ _ (by
                  intro h
                  have hv := congrArg ZMod.val h
                  rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by omega)] at hv
                  omega))
        have hinvariant1 : PartnerAssemblyInvariant C B s1 := by
          obtain ⟨word, hrun, hInv, _, _, _⟩ :=
            merge_named_outside_actual F C B s first ordered hrn 1
              (by omega) (by omega) source hcarrier registered selected inside
              (hprefix.2.2.1 1 (by omega) (by omega))
              (hprefix.2.2.1 2 (by omega) (by omega)) hinvariant
          simpa only [hrun] using hInv
        obtain ⟨m, hm, final, lastNamed, hmEq, hplacedFinal, horderedFinal,
          hcarrierFinal, hB, htail, hInvFinal⟩ :=
          ih F C B s1 next hnextordered (by omega) rfl hnextcarrier
            (by simpa [s1] using registered) selected inside hinvariant1 hprefix1
        have hcount := hfirst.trans htail
        refine ⟨m, hm, final, lastNamed, ?_, hplacedFinal, horderedFinal,
          hcarrierFinal, hB, ?_, hInvFinal⟩
        · omega
        · simpa [show 1 + (k - 1) = k by omega] using hcount

theorem RPartnerPrefix.assemble (ell : ℕ)
    {r : ℕ} [NeZero r]
    (F C B : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered) (hrn : r ≤ n)
    (source : s.placed = first.placed) (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (hinvariant : PartnerAssemblyInvariant C B s)
    (hprefix : RPartnerPrefix first B ell) :
    ∃ final : Execution n (ZMod n),
      CountedOutsideSchedule F C (ell - 1) s final ∧
      PartnerAssemblyInvariant C B final ∧
      ∃ q, final.placed q = some B := by
  obtain ⟨m, hm, final, lastNamed, _, hplaced, _, _, hB, hcount, hInv⟩ :=
    RPartnerPrefix.assemble_named ell F C B s first ordered hrn source hcarrier
      registered selected inside hinvariant hprefix
  letI : NeZero m := hm
  refine ⟨final, hcount, hInv, lastNamed.position 1, ?_⟩
  rw [hplaced, lastNamed.placed_at, hB]

/-- The final `ell` outside named blocks are precisely the source-addressed
pieces of the desired L partner. -/
def LPartnerSuffix (first : LegalNamedPlacement n r (ZMod n))
    (B : Finset (ZMod n)) (ell : ℕ) : Prop :=
  0 < ell ∧ ell < r ∧
  (∀ i : ℕ, r - ell ≤ i → i < r → first.block (i : ZMod r) ⊆ B) ∧
  (∀ a ∈ B, ∃ i : ℕ, r - ell ≤ i ∧ i < r ∧
    a ∈ first.block (i : ZMod r))

theorem LPartnerSuffix.one_eq
    (first : LegalNamedPlacement n r (ZMod n))
    (B : Finset (ZMod n))
    (h : LPartnerSuffix first B 1) :
    first.block ((r - 1 : ℕ) : ZMod r) = B := by
  have hr : 1 < r := h.2.1
  apply Finset.Subset.antisymm (h.2.2.1 (r - 1) (by omega) (by omega))
  intro a ha
  obtain ⟨i, hi1, hi2, hmem⟩ := h.2.2.2 a ha
  have : i = r - 1 := by omega
  simpa [this] using hmem

theorem LPartnerSuffix.step
    [NeZero (r - 1)]
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (B : Finset (ZMod n))
    (ell : ℕ) (hr : 3 ≤ r) (hmore : 1 < ell)
    (h : LPartnerSuffix first B ell) :
    LPartnerSuffix
      (merge_named_outside first hrn (r - 2) (by omega)) B (ell - 1) := by
  obtain ⟨hpos, hlt, hsubset, hcover⟩ := h
  obtain ⟨_, hmerge, hhead⟩ := merge_named_L_blocks first hrn hr
  refine ⟨by omega, by omega, ?_, ?_⟩
  · intro i hil hir
    by_cases hi : i = r - 2
    · subst i
      rw [hmerge]
      exact Finset.union_subset
        (hsubset (r - 2) (by omega) (by omega))
        (hsubset (r - 1) (by omega) (by omega))
    · have hii : i < r - 2 := by omega
      rw [hhead i hii]
      exact hsubset i (by omega) (by omega)
  · intro a ha
    obtain ⟨i, hil, hir, hmem⟩ := hcover a ha
    by_cases hi : i < r - 2
    · refine ⟨i, by omega, by omega, ?_⟩
      rw [hhead i hi]
      exact hmem
    · refine ⟨r - 2, by omega, by omega, ?_⟩
      rw [hmerge]
      by_cases hii : i = r - 2
      · exact Finset.mem_union_left _ (by simpa only [hii] using hmem)
      · have heq : i = r - 1 := by omega
        exact Finset.mem_union_right _ (by simpa only [heq] using hmem)

/-- Repeatedly fuse the final two outside blocks and retain the exact final
named placement, with the prescribed partner at its last outside index. -/
theorem LPartnerSuffix.assemble_named (ell : ℕ) :
    ∀ {r : ℕ} [NeZero r]
      (F C B : Finset (ZMod n))
      (s : Execution n (ZMod n))
      (first : LegalNamedPlacement n r (ZMod n)),
      first.PositivelyOrdered → r ≤ n → s.placed = first.placed →
      first.block 0 = C → s.origin.isSome = true →
      F.Nonempty → F ⊆ C → PartnerAssemblyInvariant C B s →
      LPartnerSuffix first B ell →
      ∃ (m : ℕ) (hm : NeZero m),
        letI : NeZero m := hm
        ∃ (final : Execution n (ZMod n))
          (lastNamed : LegalNamedPlacement n m (ZMod n)),
          m = r - ell + 1 ∧
          final.placed = lastNamed.placed ∧
          lastNamed.PositivelyOrdered ∧
          lastNamed.block 0 = C ∧
          lastNamed.block ((m - 1 : ℕ) : ZMod m) = B ∧
          CountedOutsideSchedule F C (ell - 1) s final ∧
          PartnerAssemblyInvariant C B final := by
  induction ell with
  | zero =>
      intro r _ F C B s first ordered hrn source hcarrier registered
        selected inside hinvariant hsuffix
      exact False.elim (Nat.not_succ_le_zero 0 hsuffix.1)
  | succ k ih =>
      intro r _ F C B s first ordered hrn source hcarrier registered
        selected inside hinvariant hsuffix
      by_cases hk : k = 0
      · subst k
        have hB := LPartnerSuffix.one_eq first B hsuffix
        refine ⟨r, inferInstance, s, first, ?_, source, ordered, hcarrier,
          hB, .empty s, hinvariant⟩
        have := hsuffix.2.1
        omega
      · have hmore : 1 < k + 1 := by omega
        have hr : 3 ≤ r := by have := hsuffix.2.1; omega
        letI : NeZero (r - 1) := ⟨by omega⟩
        let j := r - 2
        let next := merge_named_outside first hrn j (by dsimp [j]; omega)
        let s1 : Execution n (ZMod n) := { s with placed := next.placed }
        have hsuffix1 : LPartnerSuffix next B k := by
          simpa only [Nat.add_sub_cancel_right, j] using
            LPartnerSuffix.step first hrn B (k + 1) hr hmore hsuffix
        have hnextordered : next.PositivelyOrdered :=
          merge_named_outside_positive first hrn j (by dsimp [j]; omega)
            (by dsimp [j]; omega)
        have hnextcarrier : next.block 0 = C := by
          rw [merge_named_outside_zero first hrn j
            (by dsimp [j]; omega) (by dsimp [j]; omega)]
          exact hcarrier
        have hleft : Disjoint C (first.block (j : ZMod r)) := by
          rw [← hcarrier]
          exact first.block_disjoint _ _ (by
            intro h
            have hv := congrArg ZMod.val h
            rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by dsimp [j]; omega)] at hv
            dsimp [j] at hv
            omega)
        have hright : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r)) := by
          rw [← hcarrier]
          exact first.block_disjoint _ _ (by
            intro h
            have hv := congrArg ZMod.val h
            rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by dsimp [j]; omega)] at hv
            dsimp [j] at hv
            omega)
        have hfirst : CountedOutsideSchedule F C 1 s s1 := by
          simpa only [s1, next, merge_named_outside] using
            packed_adjacent_partner_schedule_count F C s first ordered hrn source
              j (by dsimp [j]; omega) (by dsimp [j]; omega)
              hcarrier registered selected inside hleft hright
        have hinvariant1 : PartnerAssemblyInvariant C B s1 := by
          obtain ⟨word, hrun, hInv, _, _, _⟩ :=
            merge_named_outside_actual F C B s first ordered hrn j
              (by dsimp [j]; omega) (by dsimp [j]; omega)
              source hcarrier registered selected inside
              (hsuffix.2.2.1 j (by dsimp [j]; omega)
                (by dsimp [j]; omega))
              (hsuffix.2.2.1 (j + 1) (by dsimp [j]; omega)
                (by dsimp [j]; omega)) hinvariant
          simpa only [hrun] using hInv
        obtain ⟨m, hm, final, lastNamed, hmEq, hplacedFinal, horderedFinal,
          hcarrierFinal, hB, htail, hInvFinal⟩ :=
          ih F C B s1 next hnextordered (by omega) rfl hnextcarrier
            (by simpa [s1] using registered) selected inside hinvariant1 hsuffix1
        have hcount := hfirst.trans htail
        refine ⟨m, hm, final, lastNamed, ?_, hplacedFinal, horderedFinal,
          hcarrierFinal, hB, ?_, hInvFinal⟩
        · omega
        · simpa [show 1 + (k - 1) = k by omega] using hcount

theorem LPartnerSuffix.assemble (ell : ℕ)
    {r : ℕ} [NeZero r]
    (F C B : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered) (hrn : r ≤ n)
    (source : s.placed = first.placed) (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (hinvariant : PartnerAssemblyInvariant C B s)
    (hsuffix : LPartnerSuffix first B ell) :
    ∃ final : Execution n (ZMod n),
      CountedOutsideSchedule F C (ell - 1) s final ∧
      PartnerAssemblyInvariant C B final ∧
      ∃ q, final.placed q = some B := by
  obtain ⟨m, hm, final, lastNamed, _, hplaced, _, _, hB, hcount, hInv⟩ :=
    LPartnerSuffix.assemble_named ell F C B s first ordered hrn source hcarrier
      registered selected inside hinvariant hsuffix
  letI : NeZero m := hm
  refine ⟨final, hcount, hInv,
    lastNamed.position ((m - 1 : ℕ) : ZMod m), ?_⟩
  rw [hplaced, lastNamed.placed_at, hB]

end RegisteredAbsorptionChains
