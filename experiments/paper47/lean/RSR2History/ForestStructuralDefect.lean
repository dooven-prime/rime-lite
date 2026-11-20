import RSR2History.ForestRootGapMoment
import RSR2History.UpperCursorSlack

/-! The three savings come from within-root fusion, between-root fusion,
and the placement of released holes in the cyclic terminal source. -/
namespace RSR2History

noncomputable def forestStructuralDefect (terminal : List (UpperFusionTree n))
    [NeZero terminal.length] : Nat :=
  (terminal.map UpperFusionTree.leftBranchDefect).sum + forestCrossDefect terminal +
    forestGapMoment (forestRootGapProfile terminal)

theorem forestStructuralDefect_congr
    {A B : List (UpperFusionTree n)} [NeZero A.length] [NeZero B.length]
    (h : A = B) : forestStructuralDefect A = forestStructuralDefect B := by
  cases h
  rfl

private theorem forestMergeMass_cons (T : UpperFusionTree n)
    (rest : List (UpperFusionTree n)) :
    forestMergeMass (T :: rest) = T.leaves.length - 1 + forestMergeMass rest := rfl

private theorem forestMergeMass_eq_zero_of_leaf_roots (terminal : List (UpperFusionTree n))
    (h : ∀ T ∈ terminal, T.leaves.length = 1) : forestMergeMass terminal = 0 := by
  unfold forestMergeMass
  apply List.sum_eq_zero_iff.mpr
  intro mass hmass
  obtain ⟨T, hT, rfl⟩ := List.mem_map.mp hmass
  simp [h T hT]

private theorem forestMergeMass_ge_root (terminal : List (UpperFusionTree n))
    (A : UpperFusionTree n) (hA : A ∈ terminal) :
    A.leaves.length - 1 ≤ forestMergeMass terminal := by
  induction terminal with
  | nil => simp at hA
  | cons T rest ih =>
      rw [forestMergeMass_cons]
      rcases List.mem_cons.mp hA with rfl | hrest
      · omega
      · have := ih hrest
        omega

private theorem forestCrossDefect_mass_le_add_root (terminal : List (UpperFusionTree n))
    (A : UpperFusionTree n) (hA : A ∈ terminal) (hpos : 0 < A.leaves.length - 1) :
    forestMergeMass terminal ≤ forestCrossDefect terminal + (A.leaves.length - 1) := by
  induction terminal with
  | nil => simp at hA
  | cons T rest ih =>
      rw [forestMergeMass_cons, forestCrossDefect]
      rcases List.mem_cons.mp hA with rfl | hrest
      · have hm := Nat.mul_le_mul_right (forestMergeMass rest) (show 1 ≤ A.leaves.length - 1 by omega)
        rw [Nat.one_mul] at hm
        omega
      · have hp := forestMergeMass_ge_root rest A hrest
        have hm := Nat.mul_le_mul_left (T.leaves.length - 1) (show 1 ≤ forestMergeMass rest by omega)
        rw [Nat.mul_one] at hm
        have htail := ih hrest
        omega

private theorem forestCrossDefect_eq_zero_of_mass_eq_zero (terminal : List (UpperFusionTree n))
    (h : forestMergeMass terminal = 0) : forestCrossDefect terminal = 0 := by
  induction terminal with
  | nil => rfl
  | cons T rest ih =>
      rw [forestMergeMass_cons] at h
      simp [forestCrossDefect, ih (by omega), show forestMergeMass rest = 0 by omega]

private theorem forestCrossDefect_eq_zero_of_mass_le_root (terminal : List (UpperFusionTree n))
    (A : UpperFusionTree n) (hA : A ∈ terminal)
    (h : forestMergeMass terminal ≤ A.leaves.length - 1) : forestCrossDefect terminal = 0 := by
  induction terminal with
  | nil => simp at hA
  | cons T rest ih =>
      rw [forestMergeMass_cons] at h
      rcases List.mem_cons.mp hA with rfl | hrest
      · have hm : forestMergeMass rest = 0 := by omega
        simp [forestCrossDefect, hm, forestCrossDefect_eq_zero_of_mass_eq_zero rest hm]
      · have hm := forestMergeMass_ge_root rest A hrest
        have hz : T.leaves.length - 1 = 0 := by omega
        simp [forestCrossDefect, hz, ih hrest (by omega)]

/-- The cross-root defect pays all released holes except possibly the largest
root's own hole interval. Any positive root can be used in place of the largest. -/
theorem forestCrossDefect_lower_bound (terminal : List (UpperFusionTree n)) :
    forestMergeMass terminal - Finset.univ.sup (forestRootGapProfile terminal) ≤
      forestCrossDefect terminal := by
  by_cases hpos : ∃ A ∈ terminal, 0 < A.leaves.length - 1
  · obtain ⟨A, hA, hpos⟩ := hpos
    obtain ⟨i, hi, he⟩ := List.mem_iff_getElem.mp hA
    have hs : A.leaves.length - 1 ≤ Finset.univ.sup (forestRootGapProfile terminal) := by
      rw [← he]
      exact Finset.le_sup (f := forestRootGapProfile terminal)
        (Finset.mem_univ (⟨i, hi⟩ : Fin terminal.length))
    have hc := forestCrossDefect_mass_le_add_root terminal A hA hpos
    omega
  · have hm := forestMergeMass_eq_zero_of_leaf_roots terminal (by
      intro T hT
      have hp := T.leaves_length_pos
      have hzero : ¬ 0 < T.leaves.length - 1 := fun h => hpos ⟨T, hT, h⟩
      omega)
    simp [hm]

/-- Zero structural defect means all roots but possibly one are leaves,
and the exceptional root is an ordered left comb. -/
theorem forestStructuralDefect_eq_zero_iff (terminal : List (UpperFusionTree n))
    [NeZero terminal.length] :
    forestStructuralDefect terminal = 0 ↔
      ∃ q : Fin terminal.length, terminal[q].IsLeftComb ∧
        ∀ i, i ≠ q → terminal[i].leaves.length = 1 := by
  classical
  constructor
  · intro h
    have hsum : (terminal.map UpperFusionTree.leftBranchDefect).sum = 0 := by
      unfold forestStructuralDefect at h
      omega
    have hm : forestGapMoment (forestRootGapProfile terminal) = 0 := by
      unfold forestStructuralDefect at h
      omega
    obtain ⟨q, hq⟩ := (forestRootGapMoment_eq_zero_iff terminal).mp hm
    refine ⟨q, terminal[q].defect_zero_iff_leftComb.mp ?_, hq⟩
    exact List.sum_eq_zero_iff.mp hsum _ (List.mem_map.mpr
      ⟨_, List.getElem_mem q.isLt, rfl⟩)
  · rintro ⟨q, hq, hleaf⟩
    have hm := (forestRootGapMoment_eq_zero_iff terminal).mpr ⟨q, hleaf⟩
    have hgap (i : Fin terminal.length) (hi : i ≠ q) : forestRootGapProfile terminal i = 0 :=
      (forestRootGapProfile_eq_zero_iff _ _).mpr (hleaf i hi)
    have hmass : forestMergeMass terminal = terminal[q].leaves.length - 1 := by
      rw [← forestRootGapProfile_sum, Finset.sum_eq_single q]
      · rfl
      · exact fun i _ hi => hgap i hi
      · simp
    have hc := forestCrossDefect_eq_zero_of_mass_le_root terminal terminal[q]
      (List.getElem_mem q.isLt) hmass.le
    have hd : (terminal.map UpperFusionTree.leftBranchDefect).sum = 0 := by
      apply List.sum_eq_zero_iff.mpr
      intro d hd
      obtain ⟨T, hT, rfl⟩ := List.mem_map.mp hd
      obtain ⟨i, hi, he⟩ := List.mem_iff_getElem.mp hT
      have hcomb : terminal[(⟨i, hi⟩ : Fin terminal.length)].IsLeftComb := by
        by_cases heq : (⟨i, hi⟩ : Fin terminal.length) = q
        · exact (congrArg (fun j : Fin terminal.length => terminal[j].IsLeftComb) heq).mpr hq
        · obtain ⟨j, packet, ht⟩ := (UpperFusionTree.leaves_length_eq_one_iff _).mp
            (hleaf _ heq)
          rw [ht]
          exact .leaf j packet
      exact T.defect_zero_iff_leftComb.mpr (he ▸ hcomb)
    simp [forestStructuralDefect, hd, hc, hm]

/-- The cross-root defect and the cyclic moment each pay the released hole
mass outside the largest root. -/
theorem forestStructuralDefect_lower_bound (terminal : List (UpperFusionTree n))
    [NeZero terminal.length] :
    2 * (forestMergeMass terminal - Finset.univ.sup (forestRootGapProfile terminal)) ≤
      forestStructuralDefect terminal := by
  have hc := forestCrossDefect_lower_bound terminal
  have hm := forestGapMoment_lower_bound (forestRootGapProfile terminal)
  rw [forestRootGapProfile_sum] at hm
  unfold forestStructuralDefect
  omega

theorem ReservationFrame.structural_defect_lower_bound
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    2 * (n - terminal.length - Finset.univ.sup (forestRootGapProfile terminal)) ≤
      forestStructuralDefect terminal := by
  rw [← frame.root_gap_total, forestRootGapProfile_sum]
  exact forestStructuralDefect_lower_bound terminal

theorem forestStructuralDefect_ge_two_of_two_roots
    (terminal : List (UpperFusionTree n)) [NeZero terminal.length]
    (i j : Fin terminal.length) (hne : i ≠ j)
    (hi : 2 ≤ terminal[i].leaves.length) (hj : 2 ≤ terminal[j].leaves.length) :
    2 ≤ forestStructuralDefect terminal := by
  obtain ⟨q, _, hq⟩ := Finset.univ.exists_mem_eq_sup ⟨i,Finset.mem_univ _⟩
    (forestRootGapProfile terminal)
  have hother : ∃ a : Fin terminal.length, a ≠ q ∧ 0 < forestRootGapProfile terminal a := by
    by_cases h : i = q
    · exact ⟨j, by simpa only [← h] using hne.symm, by
        simpa only [forestRootGapProfile] using (show 0 < terminal[j].leaves.length-1 by omega)⟩
    · exact ⟨i, h, by
        simpa only [forestRootGapProfile] using (show 0 < terminal[i].leaves.length-1 by omega)⟩
  obtain ⟨a, hne', hpos⟩ := hother
  have hmass : forestRootGapProfile terminal q + forestRootGapProfile terminal a ≤
      forestMergeMass terminal := by
    rw [← forestRootGapProfile_sum]
    have hsum := Finset.sum_le_sum_of_subset
      (show ({q,a} : Finset (Fin terminal.length)) ⊆ Finset.univ by simp)
      (f := forestRootGapProfile terminal)
    simpa [Finset.sum_insert, hne'.symm] using hsum
  have hdef := forestStructuralDefect_lower_bound terminal
  rw [hq] at hdef
  omega

private theorem UpperFusionTree.leftBranchDefect_eq_zero_of_two_leaves (T : UpperFusionTree n)
    (h : T.leaves.length = 2) : T.leftBranchDefect = 0 := by
  cases T with
  | leaf i packet => rfl
  | merge A B =>
      have ha := A.leaves_length_pos
      have hb := B.leaves_length_pos
      simp only [UpperFusionTree.leaves, List.length_append] at h
      obtain ⟨i, packetA, rfl⟩ := A.leaves_length_eq_one_iff.mp (by omega)
      obtain ⟨j, packetB, rfl⟩ := B.leaves_length_eq_one_iff.mp (by omega)
      rfl

/-- Two binary roots incur no within-root defect and contribute one unit
each from cross-root fusion and from the cyclic moment. -/
theorem forestStructuralDefect_two_binary_roots (A B : UpperFusionTree n)
    (ha : A.leaves.length = 2) (hb : B.leaves.length = 2) :
    forestStructuralDefect [A, B] = 2 := by
  simp [forestStructuralDefect, forestCrossDefect, forestMergeMass, ha, hb,
    A.leftBranchDefect_eq_zero_of_two_leaves ha, B.leftBranchDefect_eq_zero_of_two_leaves hb,
    forestRootGapMoment_two_binary_roots A B ha hb]

end RSR2History
