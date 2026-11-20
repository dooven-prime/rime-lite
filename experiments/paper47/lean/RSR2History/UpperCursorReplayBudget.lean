import RSR2History.SingletonCursorReplay

/-! Forced nonwinding events on the very schedule returned by actual replay. -/
namespace RSR2History

theorem UpperFusionTree.Subtree.merge_cases {S A B : UpperFusionTree n}
    (h : S.Subtree (.merge A B)) : S = .merge A B ∨ S.Subtree A ∨ S.Subtree B := by
  cases h with
  | refl => exact Or.inl rfl
  | left h => exact Or.inr (Or.inl h)
  | right h => exact Or.inr (Or.inr h)

theorem UpperFusionTree.not_merge_subtree_leaf {A B : UpperFusionTree n} {i packet} :
    ¬ (UpperFusionTree.merge A B).Subtree (.leaf i packet) := by
  intro h
  cases h

def forestGapDebt (forest : List (UpperFusionTree n)) : Nat :=
  (forest.map UpperFusionTree.leftGapDebt).sum

namespace UpperCursorSchedule
variable {n : Nat} {site : Nat → Fin n}
  {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
  {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}

theorem event_length_balance (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    H.length + terminal.length + 2*k = xs.length + 2*kfinal := by
  induction s with
  | nil same => have he := same.perm.length_eq; simp; omega
  | birth a roots before after rest ih =>
      have hb := before.perm.length_eq
      have ha := after.perm.length_eq
      simp only [List.length_cons] at ha ⊢
      omega
  | fusion A B roots before after gap rest ih =>
      have hb := before.perm.length_eq
      have ha := after.perm.length_eq
      simp only [List.length_cons] at hb ha ⊢
      omega

theorem debt_balance (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    forestGapDebt terminal = forestGapDebt xs + s.debt := by
  induction s with
  | nil same =>
      simpa [forestGapDebt, debt] using (same.perm.map UpperFusionTree.leftGapDebt).sum_eq.symm
  | birth a roots before after rest ih =>
      have hb := (before.perm.map UpperFusionTree.leftGapDebt).sum_eq
      have ha := (after.perm.map UpperFusionTree.leftGapDebt).sum_eq
      simp only [List.map_cons, List.sum_cons, UpperFusionTree.leftGapDebt, zero_add] at ha
      simp only [forestGapDebt, debt] at ih ⊢
      omega
  | fusion A B roots before after gap rest ih =>
      have hb := (before.perm.map UpperFusionTree.leftGapDebt).sum_eq
      have ha := (after.perm.map UpperFusionTree.leftGapDebt).sum_eq
      simp only [List.map_cons, List.sum_cons, UpperFusionTree.leftGapDebt] at hb ha
      simp only [forestGapDebt, debt] at ih ⊢
      omega

theorem zero_birth_occurs
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) (i : Nat) :
    k ≤ i → i < kfinal → (site i).val = 0 → 1 ≤ s.birthZeros := by
  induction s with
  | nil same => intro hk hi hz; omega
  | @birth j xs ys c H kf terminal cf a roots before after rest ih =>
      intro hk hi hz
      by_cases he : i = j
      · subst i
        simp [birthZeros, hz, cursorWinding]
      · have hh := ih (by omega) hi hz
        simp only [birthZeros]
        omega
  | fusion A B roots before after gap rest ih =>
      exact ih

/-- A zero-threshold merge must actually be created on this event path. -/
theorem zero_merge_occurs
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (i : Nat) (packet : Finset (Fin n)) (R : UpperFusionTree n) (hz : (site i).val = 0) :
    (∀ tree ∈ xs, ¬ (UpperFusionTree.merge (.leaf i packet) R).Subtree tree) →
    (∃ tree ∈ terminal, (UpperFusionTree.merge (.leaf i packet) R).Subtree tree) →
    1 ≤ s.fusionZeros := by
  induction s with
  | nil same =>
      intro absent present
      obtain ⟨tree, ht, hs⟩ := present
      exact False.elim (absent tree (same.perm.mem_iff.mpr ht) hs)
  | @birth j xs ys c H kf terminal cf a roots before after rest ih =>
      intro absent present
      have ha : ∀ tree ∈ ys, ¬ (UpperFusionTree.merge (.leaf i packet) R).Subtree tree := by
        intro tree ht hs
        have hm := after.perm.mem_iff.mp ht
        rcases List.mem_cons.mp hm with rfl | hm
        · exact UpperFusionTree.not_merge_subtree_leaf hs
        · exact absent tree (before.perm.mem_iff.mpr hm) hs
      exact ih ha present
  | @fusion j xs ys c H kf terminal cf A B roots before after gap rest ih =>
      intro absent present
      by_cases he : UpperFusionTree.merge (.leaf i packet) R = .merge A B
      · obtain ⟨hA, hB⟩ := UpperFusionTree.merge.inj he
        subst A
        subst B
        simp [fusionZeros, UpperFusionTree.firstLeaf, UpperFusionTree.leaves, hz, cursorWinding]
      · have ha : ∀ tree ∈ ys, ¬ (UpperFusionTree.merge (.leaf i packet) R).Subtree tree := by
          intro tree ht hs
          have hm := after.perm.mem_iff.mp ht
          rcases List.mem_cons.mp hm with rfl | hm
          · rcases hs.merge_cases with h | h | h
            · exact he h
            · exact absent A (before.perm.mem_iff.mpr (by simp)) h
            · exact absent B (before.perm.mem_iff.mpr (by simp)) h
          · exact absent tree (before.perm.mem_iff.mpr (by simp [hm])) hs
        have hh := ih ha present
        simp only [fusionZeros]
        omega

theorem initial_birth_zeros {T : UpperFusionTree n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal [T] finalCursor)
    (i : Nat) (hi : i < kfinal) (hz : (site i).val = 0) :
    1 ≤ s.birthZeros ∧ (0 < (site 0).val → 2 ≤ s.birthZeros) := by
  cases s with
  | nil same => have he := same.perm.length_eq; simp at he
  | birth a roots before after rest =>
      have hw : cursorWinding (site 0).val (site 0).val = 0 := by simp [cursorWinding]
      simp only [birthZeros, hw, ite_true]
      constructor
      · omega
      · intro hp
        have hpos : 1 ≤ i := by
          by_contra hh
          have he : i = 0 := by omega
          subst i
          omega
        have he := rest.zero_birth_occurs i hpos hi hz
        omega
  | fusion A B roots before after gap rest =>
      have he := before.perm.length_eq
      simp at he

end UpperCursorSchedule

theorem ReservationFrame.root_first_site_zero
    {k : Nat} {forest : List (UpperFusionTree n)} {T : UpperFusionTree n} {site : Nat → Fin n}
    (frame : ReservationFrame k forest [T] T.leaves site) : (site T.firstLeaf).val = 0 := by
  rw [frame.site_index T.firstLeaf T.firstLeaf_mem]
  obtain ⟨tail, he⟩ := T.leaves_eq_first_cons
  simp [he]

theorem UpperCursorSchedule.initial_winding_bounds
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {T : UpperFusionTree n} {kfinal : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal [T] finalCursor)
    (frame : ReservationFrame 0 [] [T] T.leaves site)
    (hsize : 2 ≤ T.leaves.length) :
    ((site 0).val = 0 → s.windings ≤ 2*kfinal-3) ∧
      (0 < (site 0).val → s.windings ≤ 2*kfinal-4) := by
  have complete : T.leaves.Perm (List.range kfinal) := by
    simpa [forestLeaves] using s.toPath.complete_leaves (by simp [forestLeaves])
  have hi : T.firstLeaf < kfinal := List.mem_range.mp (complete.mem_iff.mp T.firstLeaf_mem)
  have hz := frame.root_first_site_zero
  have hb := s.initial_birth_zeros T.firstLeaf hi hz
  obtain ⟨packet, R, hs⟩ := T.leftmost_singleton_merge hsize
  have hm := s.zero_merge_occurs T.firstLeaf packet R hz (by simp) ⟨T, by simp, hs⟩
  have hp := s.winding_partition
  have hl := s.event_length_balance
  simp only [List.length_cons, List.length_nil] at hl
  constructor
  · intro _
    omega
  · intro hj
    have hb2 := hb.2 hj
    omega

/-- No winding-count premise: the bound is discharged on this schedule. -/
theorem UpperCursorSchedule.cost_le_with_defect
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {T : UpperFusionTree n} {t : Nat} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H t [T] finalCursor)
    (frame : ReservationFrame 0 [] [T] T.leaves site)
    (ht : 2 ≤ t) :
    s.cost + T.leftBranchDefect + (if (site 0).val = 0 then 0 else n-(site 0).val) ≤
      2*t-1+(t-1).choose 2+n*(2*t-3) := by
  have complete : T.leaves.Perm (List.range t) := by
    simpa [forestLeaves] using s.toPath.complete_leaves (by simp [forestLeaves])
  have hlen : T.leaves.length = t := by simpa using complete.length_eq
  have hw := s.initial_winding_bounds frame (by omega)
  have hd : T.leftGapDebt = s.debt := by
    simpa [forestGapDebt] using s.debt_balance
  have hDE : s.debt+T.leftBranchDefect = (t-1).choose 2 := by
    rw [← hd, ← hlen]
    exact T.gapDebt_add_defect
  have hc := cursor_budget_with_defect ht (site 0).isLt hDE hw.1 hw.2
  have hp := s.payment
  have he := s.event_length_balance
  simp only [List.length_cons, List.length_nil] at he
  have hH : H.length = 2*t-1 := by omega
  rw [hH] at hp
  omega

theorem UpperCursorSchedule.singleton_cost_le_with_defect
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {T : UpperFusionTree n} {finalCursor : Fin n}
    (s : UpperCursorSchedule site 0 [] (site 0) H n [T] finalCursor)
    (frame : ReservationFrame 0 [] [T] T.leaves site)
    (hn : 2 ≤ n) :
    s.cost + T.leftBranchDefect + (if (site 0).val = 0 then 0 else n-(site 0).val) ≤
      5*n.choose 2 := by
  simpa only [singleton_upper_budget_identity hn] using s.cost_le_with_defect frame hn

end RSR2History
