import RSR2History.MultiRootCursorReplay
import RSR2History.ForestWindingPhase

/-! The first fusion forces a second nonwinding event in a forest schedule. -/
namespace RSR2History
open RSR2.Parametric

namespace UpperCursorSchedule

variable {n : Nat} {site : Nat → Fin n}
  {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
  {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}

/-- Either a birth fails to wind before the first fusion, or successive
winding births preserve that the cursor is at least every live anchor.
In the latter case the first fusion fails to wind. -/
private theorem nonwinding_of_fusion_of_anchors_le
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (hanchors : ∀ T ∈ xs, (site T.firstLeaf).val ≤ cursor.val)
    (hfusion : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H) :
    1 ≤ s.birthZeros + s.fusionZeros := by
  induction s with
  | nil same =>
      simp at hfusion
  | @birth i xs ys c H kf terminal cf a roots before after rest ih =>
      obtain ⟨A, B, C, he⟩ := hfusion
      have htail : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H := by
        exact ⟨A, B, C, by simpa using he⟩
      by_cases hlt : c.val < (site i).val
      · have hnext : ∀ T ∈ ys, (site T.firstLeaf).val ≤ (site i).val := by
          intro T hT
          have hm := after.perm.mem_iff.mp hT
          rcases List.mem_cons.mp hm with rfl | hm
          · rfl
          · exact (hanchors T (before.perm.mem_iff.mpr hm)).trans (Nat.le_of_lt hlt)
        simpa [birthZeros, fusionZeros, cursorWinding, hlt] using ih hnext htail
      · simp [birthZeros, fusionZeros, cursorWinding, hlt]
        omega
  | @fusion i xs ys c H kf terminal cf A B roots before after gap rest ih =>
      have hB : B ∈ xs := before.perm.mem_iff.mpr (by simp)
      have hbound := hanchors B hB
      have hno : ¬ c.val < (site A.firstLeaf).val + (A.leaves.length - 1) := by
        omega
      simp [birthZeros, fusionZeros, cursorWinding, hno]
      omega

/-- With at least one fusion, the empty-start forest schedule has at least
two nonwinding events. The initial transfer is one of them. -/
theorem forest_windings_add_two_le_events
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor)
    (hfusion : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H) :
    s.windings + 2 ≤ H.length := by
  have hpayment := s.winding_partition
  cases s with
  | nil same => simp at hfusion
  | @birth i xs ys c H kf terminal cf a roots before after rest =>
      have hroots : roots = [] := by
        have he := before.perm.length_eq
        simpa using he.symm
      subst roots
      have hanchors : ∀ T ∈ ys, (site T.firstLeaf).val ≤ (site 0).val := by
        intro T hT
        have hm := after.perm.mem_iff.mp hT
        have he : T = .leaf 0 {a} := by simpa using hm
        subst T
        rfl
      obtain ⟨A, B, C, he⟩ := hfusion
      have htail : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H := by
        exact ⟨A, B, C, by simpa using he⟩
      have hnonwind := rest.nonwinding_of_fusion_of_anchors_le hanchors htail
      simp only [birthZeros, fusionZeros, windings, cursorWinding, lt_self_iff_false,
        if_false, ite_true, Nat.zero_add, List.length_cons] at hpayment ⊢
      omega
  | fusion A B roots before after gap rest =>
      have he := before.perm.length_eq
      simp at he

/-- Once all live anchors and the cursor are positive, a segment in which
every event winds cannot use reservation site zero for a birth. -/
private theorem birth_site_pos_of_all_winding
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (hwind : s.windings = H.length)
    (hcursor : 0 < cursor.val)
    (hanchors : ∀ T ∈ xs, 0 < (site T.firstLeaf).val) :
    ∀ i, k ≤ i → i < kfinal → 0 < (site i).val := by
  induction s with
  | nil same =>
      intro i hle hlt
      omega
  | @birth count xs ys cur H kf terminal cf a roots before after rest ih =>
      have hbound := rest.winding_partition
      have htarget : cur.val < (site count).val := by
        by_contra h
        simp only [windings, cursorWinding, if_neg h, Nat.zero_add,
          List.length_cons] at hwind
        omega
      have hrest : rest.windings = H.length := by
        simp only [windings, cursorWinding, if_pos htarget, List.length_cons] at hwind
        omega
      have hnew : 0 < (site count).val := by omega
      intro i hle hlt
      rcases Nat.eq_or_lt_of_le hle with rfl | hnext
      · exact hnew
      · apply ih hrest hnew _ i hnext hlt
        intro T hT
        rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
        · exact hnew
        · exact hanchors T (before.perm.mem_iff.mpr hT')
  | @fusion count xs ys cur H kf terminal cf A B roots before after gap rest ih =>
      have hbound := rest.winding_partition
      have htarget : cur.val < (site A.firstLeaf).val + (A.leaves.length - 1) := by
        by_contra h
        simp only [windings, cursorWinding, if_neg h, Nat.zero_add,
          List.length_cons] at hwind
        omega
      have hrest : rest.windings = H.length := by
        simp only [windings, cursorWinding, if_pos htarget, List.length_cons] at hwind
        omega
      have hnew := hanchors A (before.perm.mem_iff.mpr (by simp))
      apply ih hrest hnew
      intro T hT
      rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
      · exact hnew
      · exact hanchors T (before.perm.mem_iff.mpr (by simp [hT']))

/-- If only one nonwinding event remains and a site-zero birth is still
pending, that event is the site-zero birth. Before it, the cursor stays
above the threshold and only winding births occur. -/
private theorem final_phase_ge_of_pending_zero_birth {c : Nat}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (hwind : s.windings + 1 = H.length) (hpos : 0 < c) (hcur : c ≤ cursor.val)
    (hanchors : ∀ T ∈ xs, c ≤ (site T.firstLeaf).val ∧ (site T.firstLeaf).val ≤ cursor.val)
    (hzero : ∃ i, k ≤ i ∧ i < kfinal ∧ (site i).val = 0)
    (hfusion : ∃ A B, .fusion true A B (A ∪ B) ∈ H) :
    c ≤ finalCursor.val := by
  induction s with
  | nil same =>
      obtain ⟨i, hle, hlt, _⟩ := hzero
      omega
  | @birth count xs ys cur H kf terminal cf a roots before after rest ih =>
      obtain ⟨j, hjle, hjlt, hjzero⟩ := hzero
      obtain ⟨A, B, hf⟩ := hfusion
      have htailFusion : ∃ A B, .fusion true A B (A ∪ B) ∈ H := ⟨A, B, by simpa using hf⟩
      by_cases htarget : cur.val < (site count).val
      · have hrest : rest.windings + 1 = H.length := by
          simp only [windings, cursorWinding, if_pos htarget, List.length_cons] at hwind
          omega
        have hnext : c ≤ (site count).val := by omega
        apply ih hrest hnext _ _ htailFusion
        · intro T hT
          rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
          · exact ⟨hnext, le_rfl⟩
          · obtain ⟨hge, hle⟩ := hanchors T (before.perm.mem_iff.mpr hT')
            exact ⟨hge, by omega⟩
        · refine ⟨j, ?_, hjlt, hjzero⟩
          have hne : count ≠ j := by
            intro he
            subst j
            omega
          omega
      · have hrest : rest.windings = H.length := by
          simp only [windings, cursorWinding, if_neg htarget, Nat.zero_add,
            List.length_cons] at hwind
          omega
        by_cases hsite : (site count).val = 0
        · apply rest.final_phase_ge_of_all_winding hrest _ (Or.inr htailFusion)
          intro T hT hlow
          rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
          · simp [UpperFusionTree.leaves, UpperFusionTree.firstLeaf]
          · have hge := (hanchors T (before.perm.mem_iff.mpr hT')).1
            omega
        · have hnew : 0 < (site count).val := by omega
          have hall : ∀ T ∈ ys, 0 < (site T.firstLeaf).val := by
            intro T hT
            rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
            · exact hnew
            · exact hpos.trans_le (hanchors T (before.perm.mem_iff.mpr hT')).1
          have hne : count ≠ j := by
            intro he
            subst j
            exact hsite hjzero
          have hbad := rest.birth_site_pos_of_all_winding hrest hnew hall j (by omega) hjlt
          omega
  | @fusion count xs ys cur H kf terminal cf A B roots before after gap rest ih =>
      have hB := (hanchors B (before.perm.mem_iff.mpr (by simp))).2
      have hno : ¬ cur.val < (site A.firstLeaf).val + (A.leaves.length - 1) := by omega
      have hrest : rest.windings = H.length := by
        simp only [windings, cursorWinding, if_neg hno, Nat.zero_add,
          List.length_cons] at hwind
        omega
      have hnew := hpos.trans_le (hanchors A (before.perm.mem_iff.mpr (by simp))).1
      have hall : ∀ T ∈ ys, 0 < (site T.firstLeaf).val := by
        intro T hT
        rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
        · exact hnew
        · exact hpos.trans_le (hanchors T (before.perm.mem_iff.mpr (by simp [hT']))).1
      obtain ⟨j, hjle, hjlt, hjzero⟩ := hzero
      have hbad := rest.birth_site_pos_of_all_winding hrest hnew hall j hjle hjlt
      omega

/-- At maximal winding count the initial cursor does not exceed the final
cursor, as long as an actual birth uses reservation site zero. -/
theorem forest_final_phase_ge_of_max_windings
    (s : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal finalCursor)
    (hmax : s.windings + 2 = H.length) (hpos : 0 < (site 0).val)
    (hzero : ∃ i, i < kfinal ∧ (site i).val = 0)
    (hfusion : ∃ A B, .fusion true A B (A ∪ B) ∈ H) :
    (site 0).val ≤ finalCursor.val := by
  cases s with
  | nil same => simp at hfusion
  | @birth count xs ys cur H kf terminal cf a roots before after rest =>
      have hroots : roots = [] := by
        have he := before.perm.length_eq
        simpa using he.symm
      subst roots
      obtain ⟨i, hilt, hizero⟩ := hzero
      obtain ⟨A, B, hf⟩ := hfusion
      have hi : 1 ≤ i := by
        by_contra h
        have he : i = 0 := by omega
        subst i
        omega
      simp only [windings, cursorWinding, lt_self_iff_false, if_false, Nat.zero_add,
        List.length_cons] at hmax
      apply rest.final_phase_ge_of_pending_zero_birth (by omega) hpos le_rfl _
        ⟨i, hi, hilt, hizero⟩ ⟨A, B, by simpa using hf⟩
      intro T hT
      have hm := after.perm.mem_iff.mp hT
      have he : T = .leaf 0 {a} := by simpa using hm
      subst T
      exact ⟨le_rfl, le_rfl⟩
  | fusion A B roots before after gap rest =>
      have he := before.perm.length_eq
      simp at he

end UpperCursorSchedule
end RSR2History
