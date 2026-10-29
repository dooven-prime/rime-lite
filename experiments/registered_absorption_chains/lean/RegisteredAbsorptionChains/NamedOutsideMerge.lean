import RegisteredAbsorptionChains.PartnerScheduleGeometry
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r] [NeZero (r - 1)]

/-- Remove the old index `j+1`, leaving `j` to name the fused block. -/
def mergeSkip (j : ℕ) (i : ZMod (r - 1)) : ℕ :=
  if i.val ≤ j then i.val else i.val + 1

theorem mergeSkip_lt (j : ℕ) (i : ZMod (r - 1)) :
    mergeSkip (r := r) j i < r := by
  have hi := ZMod.val_lt i
  unfold mergeSkip
  split_ifs <;> omega

theorem mergeSkip_injective (j : ℕ) :
    Function.Injective (mergeSkip (r := r) j) := by
  intro i k h
  have hi := ZMod.val_lt i
  have hk := ZMod.val_lt k
  have hval : i.val = k.val := by
    unfold mergeSkip at h
    split_ifs at h <;> omega
  exact ZMod.val_injective (r - 1) hval

theorem mergeSkip_ne_removed (j : ℕ) (i : ZMod (r - 1)) :
    mergeSkip (r := r) j i ≠ j + 1 := by
  unfold mergeSkip
  split_ifs <;> omega

theorem mergeSkip_surj_except
    (j : ℕ) (hj : j + 1 < r)
    (k : ℕ) (hk : k < r) (hremoved : k ≠ j + 1) :
    ∃ i : ZMod (r - 1), mergeSkip j i = k := by
  by_cases hkj : k ≤ j
  · have hki : k < r - 1 := by omega
    refine ⟨(k : ZMod (r - 1)), ?_⟩
    simp [mergeSkip, ZMod.val_natCast_of_lt hki, hkj]
  · have hki : k - 1 < r - 1 := by omega
    have hnot : ¬ k - 1 ≤ j := by omega
    refine ⟨((k - 1 : ℕ) : ZMod (r - 1)), ?_⟩
    simp [mergeSkip, ZMod.val_natCast_of_lt hki, hnot]
    omega

def mergeOldIndex (j : ℕ) (i : ZMod (r - 1)) : ZMod r :=
  (mergeSkip j i : ZMod r)

theorem mergeOldIndex_injective (j : ℕ) :
    Function.Injective (mergeOldIndex (r := r) j) := by
  intro i k h
  have hval := congrArg ZMod.val h
  dsimp [mergeOldIndex] at hval
  rw [ZMod.val_natCast_of_lt (mergeSkip_lt j i),
    ZMod.val_natCast_of_lt (mergeSkip_lt j k)] at hval
  exact mergeSkip_injective j hval

theorem mergeOldIndex_val (j : ℕ) (i : ZMod (r - 1)) :
    (mergeOldIndex j i).val = mergeSkip j i :=
  ZMod.val_natCast_of_lt (mergeSkip_lt j i)

theorem mergeOldIndex_at_j (j : ℕ) (hj : j + 1 < r) :
    mergeOldIndex (r := r) j (j : ZMod (r - 1)) = (j : ZMod r) := by
  have hjnew : j < r - 1 := by omega
  simp [mergeOldIndex, mergeSkip, ZMod.val_natCast_of_lt hjnew]

theorem mergeOldIndex_zero (j : ℕ) :
    mergeOldIndex (r := r) j 0 = 0 := by
  simp [mergeOldIndex, mergeSkip]

theorem mergeOldIndex_ne_pair (j : ℕ) (hj : j + 1 < r)
    (i : ZMod (r - 1)) (hi : i ≠ (j : ZMod (r - 1))) :
    mergeOldIndex j i ≠ (j : ZMod r) ∧
    mergeOldIndex j i ≠ ((j + 1 : ℕ) : ZMod r) := by
  have hjnew : j < r - 1 := by omega
  have hival : i.val ≠ j := by
    intro heq
    apply hi
    exact ZMod.val_injective (r - 1)
      (heq.trans (ZMod.val_natCast_of_lt hjnew).symm)
  have hskip : mergeSkip j i ≠ j := by
    dsimp [mergeSkip]
    split_ifs <;> omega
  have hskipnext := mergeSkip_ne_removed (r := r) j i
  constructor
  · intro h
    have hv := congrArg ZMod.val h
    rw [mergeOldIndex_val, ZMod.val_natCast_of_lt (by omega)] at hv
    exact hskip hv
  · intro h
    have hv := congrArg ZMod.val h
    rw [mergeOldIndex_val, ZMod.val_natCast_of_lt hj] at hv
    exact hskipnext hv

def mergedNamedBlock (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (i : ZMod (r - 1)) : Finset (ZMod n) :=
  if i = (j : ZMod (r - 1)) then
    first.block (j : ZMod r) ∪ first.block ((j + 1 : ℕ) : ZMod r)
  else first.block (mergeOldIndex j i)

def mergedNamedPosition (hrn : r ≤ n) (j : ℕ)
    (i : ZMod (r - 1)) : ZMod n :=
  packedPosition (-(j : ZMod n)) (mergeOldIndex j i)

theorem mergedNamedPosition_injective (hrn : r ≤ n) (j : ℕ) :
    Function.Injective (mergedNamedPosition (r := r) hrn j) :=
  (packedPosition_injective (-(j : ZMod n)) hrn).comp
    (mergeOldIndex_injective j)

theorem packed_merge_port_positions (hrn : r ≤ n)
    (j : ℕ) (hj : j + 1 < r) :
    packedPosition (-(j : ZMod n)) (j : ZMod r) = 0 ∧
    packedPosition (-(j : ZMod n)) ((j + 1 : ℕ) : ZMod r) = 1 := by
  have hjval : ((j : ℕ) : ZMod r).val = j :=
    ZMod.val_natCast_of_lt (by omega)
  have hnextval : (((j + 1 : ℕ) : ZMod r)).val = j + 1 :=
    ZMod.val_natCast_of_lt hj
  constructor
  · simp [packedPosition, hjval]
  · simp only [packedPosition, hnextval]
    push_cast
    abel

theorem mergedNamedBlock_zero
    (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r) :
    mergedNamedBlock first j 0 = first.block 0 := by
  have hj0 : (0 : ZMod (r - 1)) ≠ (j : ZMod (r - 1)) := by
    intro h
    have hv := congrArg ZMod.val h
    rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by omega)] at hv
    omega
  simp [mergedNamedBlock, hj0, mergeOldIndex_zero]

theorem mergedNamedBlock_at_j
    (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (hj : j + 1 < r) :
    mergedNamedBlock first j (j : ZMod (r - 1)) =
      first.block (j : ZMod r) ∪
        first.block ((j + 1 : ℕ) : ZMod r) := by
  simp [mergedNamedBlock]

theorem mergedNamedBlock_nonempty
    (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (i : ZMod (r - 1)) :
    (mergedNamedBlock first j i).Nonempty := by
  by_cases hi : i = (j : ZMod (r - 1))
  · simp only [mergedNamedBlock, if_pos hi]
    exact (first.block_nonempty (j : ZMod r)).mono Finset.subset_union_left
  · simpa [mergedNamedBlock, hi] using first.block_nonempty (mergeOldIndex j i)

theorem mergedNamedBlock_disjoint
    (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (hj : j + 1 < r)
    (i k : ZMod (r - 1)) (hik : i ≠ k) :
    Disjoint (mergedNamedBlock first j i) (mergedNamedBlock first j k) := by
  by_cases hi : i = (j : ZMod (r - 1))
  · have hk : k ≠ (j : ZMod (r - 1)) := by intro h; exact hik (hi.trans h.symm)
    rw [hi]
    simp only [mergedNamedBlock, if_pos rfl, if_neg hk]
    have hpair := mergeOldIndex_ne_pair j hj k hk
    exact Finset.disjoint_union_left.mpr
      ⟨first.block_disjoint _ _ hpair.1.symm,
       first.block_disjoint _ _ hpair.2.symm⟩
  · by_cases hk : k = (j : ZMod (r - 1))
    · have hpair := mergeOldIndex_ne_pair j hj i hi
      rw [hk]
      simp only [mergedNamedBlock, if_neg hi, if_pos rfl]
      exact Finset.disjoint_union_right.mpr
        ⟨first.block_disjoint _ _ hpair.1,
         first.block_disjoint _ _ hpair.2⟩
    · simp only [mergedNamedBlock, if_neg hi, if_neg hk]
      exact first.block_disjoint _ _ (by
        intro h
        exact hik (mergeOldIndex_injective j h))

theorem mergedNamedBlock_cover
    (first : LegalNamedPlacement n r (ZMod n))
    (j : ℕ) (hj : j + 1 < r)
    (a : ZMod n) :
    ∃ i : ZMod (r - 1), a ∈ mergedNamedBlock first j i := by
  obtain ⟨k, ha⟩ := first.atom_covered a
  by_cases hkj : k.val = j
  · refine ⟨(j : ZMod (r - 1)), ?_⟩
    rw [mergedNamedBlock_at_j first j hj]
    have hidx : k = (j : ZMod r) :=
      ZMod.val_injective r (hkj.trans (ZMod.val_natCast_of_lt (by omega)).symm)
    exact Finset.mem_union_left _ (hidx ▸ ha)
  · by_cases hknext : k.val = j + 1
    · refine ⟨(j : ZMod (r - 1)), ?_⟩
      rw [mergedNamedBlock_at_j first j hj]
      have hidx : k = ((j + 1 : ℕ) : ZMod r) :=
        ZMod.val_injective r
          (hknext.trans (ZMod.val_natCast_of_lt hj).symm)
      exact Finset.mem_union_right _ (hidx ▸ ha)
    · obtain ⟨i, hskip⟩ := mergeSkip_surj_except j hj k.val (ZMod.val_lt k) hknext
      have hidx : mergeOldIndex j i = k := by
        apply ZMod.val_injective r
        rw [mergeOldIndex_val, hskip]
      have hi : i ≠ (j : ZMod (r - 1)) := by
        intro heq
        have hv : k.val = j := by
          rw [← hidx, heq, mergeOldIndex_at_j j hj]
          exact ZMod.val_natCast_of_lt (by omega)
        exact hkj hv
      refine ⟨i, ?_⟩
      simpa [mergedNamedBlock, hi, hidx] using ha

theorem mergedNamedPosition_at_j (hrn : r ≤ n)
    (j : ℕ) (hj : j + 1 < r) :
    mergedNamedPosition (r := r) hrn j (j : ZMod (r - 1)) = 0 := by
  simp only [mergedNamedPosition, mergeOldIndex_at_j j hj]
  exact (packed_merge_port_positions hrn j hj).1

theorem mergedNamedPosition_zero (hrn : r ≤ n) (j : ℕ) :
    mergedNamedPosition (r := r) hrn j 0 = -(j : ZMod n) := by
  simp [mergedNamedPosition, mergeOldIndex_zero, packedPosition]

theorem mergedNamedPosition_ne_ports (hrn : r ≤ n)
    (j : ℕ) (hj : j + 1 < r)
    (i : ZMod (r - 1)) (hi : i ≠ (j : ZMod (r - 1))) :
    mergedNamedPosition hrn j i ≠ 0 ∧
    mergedNamedPosition hrn j i ≠ 1 := by
  have hpair := mergeOldIndex_ne_pair j hj i hi
  have hpos := packed_merge_port_positions hrn j hj
  constructor
  · intro h
    apply hpair.1
    exact packedPosition_injective (-(j : ZMod n)) hrn (h.trans hpos.1.symm)
  · intro h
    apply hpair.2
    exact packedPosition_injective (-(j : ZMod n)) hrn (h.trans hpos.2.symm)

theorem merged_named_placed_at
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hj : j + 1 < r)
    (i : ZMod (r - 1)) :
    fusionPlacement (packedLegalNamed first hrn (-(j : ZMod n))).placed
      (mergedNamedPosition hrn j i) =
        some (mergedNamedBlock first j i) := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  by_cases hi : i = (j : ZMod (r - 1))
  · subst i
    have hports := packed_adjacent_ports first hrn j hj
    rw [mergedNamedPosition_at_j hrn j hj]
    simp [fusionPlacement, hports.1, hports.2,
      mergedNamedBlock_at_j first j hj]
  · have hq := mergedNamedPosition_ne_ports hrn j hj i hi
    rw [fusionPlacement_other_site target.placed _ hq.1 hq.2]
    change target.placed (target.position (mergeOldIndex j i)) =
      some (mergedNamedBlock first j i)
    rw [target.placed_at]
    simp [target, packedLegalNamed, mergedNamedBlock, hi]

theorem merged_named_only_sites
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hj : j + 1 < r)
    (q : ZMod n)
    (hq : fusionPlacement (packedLegalNamed first hrn (-(j : ZMod n))).placed q ≠ none) :
    ∃ i : ZMod (r - 1), mergedNamedPosition hrn j i = q := by
  let target := packedLegalNamed first hrn (-(j : ZMod n))
  by_cases hzero : q = 0
  · refine ⟨(j : ZMod (r - 1)), ?_⟩
    simpa [hzero] using mergedNamedPosition_at_j hrn j hj
  have hone : q ≠ 1 := by
    intro heq
    apply hq
    have h10 : (1 : ZMod n) ≠ 0 := by
      intro h
      have hzero := ZMod.one_eq_zero_iff.mp h
      omega
    simp [fusionPlacement, heq, h10]
  have htarget : target.placed q ≠ none := by
    change fusionPlacement target.placed q ≠ none at hq
    rw [fusionPlacement_other_site target.placed q hzero hone] at hq
    exact hq
  obtain ⟨k, hposk⟩ := target.only_named q htarget
  have hremoved : k.val ≠ j + 1 := by
    intro heq
    have hk : k = ((j + 1 : ℕ) : ZMod r) :=
      ZMod.val_injective r (heq.trans (ZMod.val_natCast_of_lt hj).symm)
    have hpos := (packed_merge_port_positions hrn j hj).2
    have hposk' : target.position ((j + 1 : ℕ) : ZMod r) = q := hk ▸ hposk
    exact hone (hposk'.symm.trans hpos)
  obtain ⟨i, hskip⟩ := mergeSkip_surj_except j hj k.val (ZMod.val_lt k) hremoved
  refine ⟨i, ?_⟩
  have hidx : mergeOldIndex j i = k := by
    apply ZMod.val_injective r
    rw [mergeOldIndex_val, hskip]
  change packedPosition (-(j : ZMod n)) k = q at hposk
  simpa [mergedNamedPosition, hidx] using hposk

/-- Re-name the actual state immediately after merging two adjacent named
outside packets. In particular the new `placed` field is the literal
`fusionPlacement` of the packed predecessor, not merely an equal partition. -/
noncomputable def merge_named_outside
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hj : j + 1 < r) :
    LegalNamedPlacement n (r - 1) (ZMod n) where
  placed := fusionPlacement (packedLegalNamed first hrn (-(j : ZMod n))).placed
  position := mergedNamedPosition hrn j
  block := mergedNamedBlock first j
  position_injective := mergedNamedPosition_injective hrn j
  placed_at := merged_named_placed_at first hrn j hj
  only_named := merged_named_only_sites first hrn j hj
  block_nonempty := mergedNamedBlock_nonempty first j
  block_disjoint := mergedNamedBlock_disjoint first j hj
  atom_covered := mergedNamedBlock_cover first j hj

theorem merge_named_outside_positive
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r) :
    (merge_named_outside first hrn j hj).PositivelyOrdered := by
  let next := merge_named_outside first hrn j hj
  have hoffset (k : ℕ) (hk : k < r - 1) :
      next.offset k = if k ≤ j then k else k + 1 := by
    have hval : ((k : ℕ) : ZMod (r - 1)).val = k :=
      ZMod.val_natCast_of_lt hk
    have hskip : mergeSkip j (k : ZMod (r - 1)) =
        if k ≤ j then k else k + 1 := by
      simp [mergeSkip, hval]
    have hbound : mergeSkip j (k : ZMod (r - 1)) < n :=
      (mergeSkip_lt j _).trans_le hrn
    simp [LegalNamedPlacement.offset, hk, next, merge_named_outside,
      mergedNamedPosition, packedPosition, mergeOldIndex_val,
      mergeOldIndex_zero, hskip]
    split_ifs with h
    · exact ZMod.val_natCast_of_lt (by omega)
    · simpa only [Nat.cast_add, Nat.cast_one] using
        (ZMod.val_natCast_of_lt (show k + 1 < n by omega))
  intro k hk
  by_cases hnext : k + 1 < r - 1
  · rw [hoffset k hk, hoffset (k + 1) hnext]
    split_ifs <;> omega
  · have hend : k + 1 = r - 1 := by omega
    rw [hoffset k hk, hend, next.offset_end]
    split_ifs <;> omega

theorem merge_named_outside_zero
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r) :
    (merge_named_outside first hrn j hj).block 0 = first.block 0 :=
  mergedNamedBlock_zero first j hjpos hj

theorem merge_named_outside_at_j
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hj : j + 1 < r) :
    (merge_named_outside first hrn j hj).block (j : ZMod (r - 1)) =
      first.block (j : ZMod r) ∪ first.block ((j + 1 : ℕ) : ZMod r) :=
  mergedNamedBlock_at_j first j hj

theorem merge_named_outside_other
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (j : ℕ) (hj : j + 1 < r)
    (i : ZMod (r - 1)) (hi : i ≠ (j : ZMod (r - 1))) :
    (merge_named_outside first hrn j hj).block i =
      first.block (mergeOldIndex j i) := by
  simp [merge_named_outside, mergedNamedBlock, hi]

/-- One actual outside merge produces the explicitly re-named state. The
next proof stage may use `next` itself, including its exact placement. -/
theorem merge_named_outside_actual
    (F C B : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (ordered : first.PositivelyOrdered)
    (hrn : r ≤ n) (j : ℕ) (hjpos : 0 < j) (hj : j + 1 < r)
    (source : s.placed = first.placed)
    (hcarrier : first.block 0 = C)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftPartner : first.block (j : ZMod r) ⊆ B)
    (rightPartner : first.block ((j + 1 : ℕ) : ZMod r) ⊆ B)
    (hinvariant : PartnerAssemblyInvariant C B s) :
    let next := merge_named_outside first hrn j hj
    ∃ word : List Letter,
      run F s word = { s with placed := next.placed } ∧
      PartnerAssemblyInvariant C B (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain ∧
      next.PositivelyOrdered := by
  let next := merge_named_outside first hrn j hj
  have hleft : Disjoint C (first.block (j : ZMod r)) := by
    rw [← hcarrier]
    exact first.block_disjoint _ _ (by
      intro h
      have hv := congrArg ZMod.val h
      rw [ZMod.val_zero, ZMod.val_natCast_of_lt (by omega)] at hv
      omega)
  have hright : Disjoint C (first.block ((j + 1 : ℕ) : ZMod r)) := by
    rw [← hcarrier]
    exact first.block_disjoint _ _ (by
      intro h
      have hv := congrArg ZMod.val h
      rw [ZMod.val_zero, ZMod.val_natCast_of_lt hj] at hv
      omega)
  obtain ⟨word, hrun, horigin, hchain, hInv⟩ :=
    packed_adjacent_partner_stage_exact F C B s first ordered hrn source
      j hjpos hj hcarrier registered selected inside hleft hright
      leftPartner rightPartner hinvariant
  refine ⟨word, ?_, ?_, ?_, ?_, merge_named_outside_positive first hrn j hjpos hj⟩
  · exact hrun
  · exact hrun ▸ hInv
  · simpa [hrun] using horigin
  · simpa [hrun] using hchain

/-- Repeating index one grows the first outside packet and shifts every
remaining outside packet one place toward the carrier. -/
theorem merge_named_R_blocks
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (hr : 3 ≤ r) :
    let next := merge_named_outside first hrn 1 (by omega)
    next.block 0 = first.block 0 ∧
    next.block ((1 : ℕ) : ZMod (r - 1)) =
      first.block ((1 : ℕ) : ZMod r) ∪ first.block ((2 : ℕ) : ZMod r) ∧
    ∀ k : ℕ, 2 ≤ k → k < r - 1 →
      next.block (k : ZMod (r - 1)) = first.block ((k + 1 : ℕ) : ZMod r) := by
  let next := merge_named_outside first hrn 1 (by omega)
  refine ⟨merge_named_outside_zero first hrn 1 (by omega) (by omega),
    ?_, ?_⟩
  · simpa using merge_named_outside_at_j first hrn 1 (by omega)
  intro k hk2 hkr
  have hkval : ((k : ℕ) : ZMod (r - 1)).val = k :=
    ZMod.val_natCast_of_lt hkr
  have hk1 : (k : ZMod (r - 1)) ≠ ((1 : ℕ) : ZMod (r - 1)) := by
    intro h
    have hv := congrArg ZMod.val h
    rw [hkval, ZMod.val_natCast_of_lt (by omega)] at hv
    omega
  rw [merge_named_outside_other first hrn 1 (by omega) _ hk1]
  simp [mergeOldIndex, mergeSkip, hkval, show ¬ k ≤ 1 by omega]

/-- Repeating index `r-2` grows the final outside packet; all earlier
named blocks retain their indices. -/
theorem merge_named_L_blocks
    (first : LegalNamedPlacement n r (ZMod n))
    (hrn : r ≤ n) (hr : 3 ≤ r) :
    let next := merge_named_outside first hrn (r - 2) (by omega)
    next.block 0 = first.block 0 ∧
    next.block ((r - 2 : ℕ) : ZMod (r - 1)) =
      first.block ((r - 2 : ℕ) : ZMod r) ∪ first.block ((r - 1 : ℕ) : ZMod r) ∧
    ∀ k : ℕ, k < r - 2 →
      next.block (k : ZMod (r - 1)) = first.block (k : ZMod r) := by
  let next := merge_named_outside first hrn (r - 2) (by omega)
  refine ⟨merge_named_outside_zero first hrn (r - 2) (by omega) (by omega),
    ?_, ?_⟩
  · have hlast : r - 2 + 1 = r - 1 := by omega
    simpa only [hlast] using
      (merge_named_outside_at_j first hrn (r - 2) (by omega))
  intro k hk
  have hkval : ((k : ℕ) : ZMod (r - 1)).val = k :=
    ZMod.val_natCast_of_lt (by omega)
  have hjval : (((r - 2 : ℕ) : ZMod (r - 1))).val = r - 2 :=
    ZMod.val_natCast_of_lt (by omega)
  have hkj : (k : ZMod (r - 1)) ≠ ((r - 2 : ℕ) : ZMod (r - 1)) := by
    intro h
    have hv := congrArg ZMod.val h
    rw [hkval, hjval] at hv
    omega
  rw [merge_named_outside_other first hrn (r - 2) (by omega) _ hkj]
  simp [mergeOldIndex, mergeSkip, hkval, show k ≤ r - 2 by omega]

end RegisteredAbsorptionChains
