import RSR2History.UpperCursorSchedule

/-! Phase constraints in event segments with maximal winding count. -/
namespace RSR2History
namespace UpperCursorSchedule

/-- In a segment where every event winds, a root anchored below the threshold
stays a leaf if it starts as a leaf behind the cursor. A fusion in such a
segment sets the cursor at or above the threshold, where it then stays. -/
theorem final_phase_ge_of_all_winding
    {n : Nat} {site : Nat → Fin n} {k kfinal c : Nat} {cursor finalCursor : Fin n}
    {xs terminal : List (UpperFusionTree n)} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (hwind : s.windings = H.length)
    (hlow : ∀ T ∈ xs, (site T.firstLeaf).val < c →
      T.leaves.length = 1 ∧ (site T.firstLeaf).val ≤ cursor.val)
    (hphase : c ≤ cursor.val ∨ ∃ A B, .fusion true A B (A ∪ B) ∈ H) :
    c ≤ finalCursor.val := by
  induction s with
  | nil same =>
      simpa using hphase
  | @birth i xs ys cur H kf terminal cf a roots before after rest ih =>
      have hbound := rest.winding_partition
      have htarget : cur.val < (site i).val := by
        by_contra h
        simp only [windings, cursorWinding, if_neg h, Nat.zero_add, List.length_cons] at hwind
        omega
      have hrest : rest.windings = H.length := by
        simp only [windings, cursorWinding, if_pos htarget, List.length_cons] at hwind
        omega
      apply ih hrest
      · intro T hT hsmall
        rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
        · simp [UpperFusionTree.leaves, UpperFusionTree.firstLeaf]
        · obtain ⟨hone, hle⟩ := hlow T (before.perm.mem_iff.mpr hT') hsmall
          exact ⟨hone, by omega⟩
      · rcases hphase with hcur | ⟨A, B, hmem⟩
        · exact Or.inl (by omega)
        · exact Or.inr ⟨A, B, by simpa using hmem⟩
  | @fusion i xs ys cur H kf terminal cf A B roots before after gap rest ih =>
      have hbound := rest.winding_partition
      have htarget : cur.val < (site A.firstLeaf).val + (A.leaves.length - 1) := by
        by_contra h
        simp only [windings, cursorWinding, if_neg h, Nat.zero_add, List.length_cons] at hwind
        omega
      have hrest : rest.windings = H.length := by
        simp only [windings, cursorWinding, if_pos htarget, List.length_cons] at hwind
        omega
      have hleft : c ≤ (site A.firstLeaf).val := by
        by_contra h
        obtain ⟨hone, hle⟩ := hlow A (before.perm.mem_iff.mpr (by simp)) (by omega)
        omega
      apply ih hrest _ (Or.inl hleft)
      intro T hT hsmall
      rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
      · simp only [UpperFusionTree.firstLeaf] at hsmall
        omega
      · obtain ⟨hone, _⟩ := hlow T (before.perm.mem_iff.mpr (by simp [hT'])) hsmall
        exact ⟨hone, by omega⟩

end UpperCursorSchedule
end RSR2History
