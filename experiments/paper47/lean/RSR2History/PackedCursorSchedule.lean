import RSR2History.UpperCursorReplayBudget

/-! Whole-packet cursor schedules. Lower fusion events leave the upper
cursor and layout unchanged; only upper fusions and transfers are charged
by this schedule. The lower fusion/extraction ledger pays lower costs. -/
namespace RSR2History
open RSR2.Parametric

/-- The number of events charged to the upper cursor: transfers and upper
fusions. Effective lower fusion records remain present in the full log. -/
def upperCursorEventCount : List (EffectiveEvent n) → Nat
  | [] => 0
  | .fusion false _ _ _ :: H => upperCursorEventCount H
  | _ :: H => 1 + upperCursorEventCount H

inductive PackedCursorSchedule {n : Nat} (site : Nat → Fin n) :
    Nat → List (UpperFusionTree n) → Fin n → List (EffectiveEvent n) →
    Nat → List (UpperFusionTree n) → Fin n → Type where
  | nil {k xs ys cursor} (same : xs.IsRotated ys) :
      PackedCursorSchedule site k xs cursor [] k ys cursor
  | birth {k xs ys cursor H kfinal terminal finalCursor}
      (packet : Finset (Fin n)) (roots : List (UpperFusionTree n))
      (before : xs.IsRotated roots) (after : ys.IsRotated (.leaf k packet :: roots))
      (tail : PackedCursorSchedule site (k+1) ys (site k) H kfinal terminal finalCursor) :
      PackedCursorSchedule site k xs cursor (.transfer packet :: H) kfinal terminal finalCursor
  | lower {k xs ys cursor H kfinal terminal finalCursor}
      (A B : Finset (Fin n)) (same : xs.IsRotated ys)
      (tail : PackedCursorSchedule site k ys cursor H kfinal terminal finalCursor) :
      PackedCursorSchedule site k xs cursor
        (.fusion false A B (A ∪ B) :: H) kfinal terminal finalCursor
  | fusion {k xs ys cursor H kfinal terminal finalCursor}
      (A B : UpperFusionTree n) (roots : List (UpperFusionTree n))
      (before : xs.IsRotated (A :: B :: roots))
      (after : ys.IsRotated (.merge A B :: roots))
      (anchor_gap : (site B.firstLeaf).val = (site A.firstLeaf).val + A.leaves.length)
      (tail : PackedCursorSchedule site k ys (site A.firstLeaf) H kfinal terminal finalCursor) :
      PackedCursorSchedule site k xs cursor
        (.fusion true A.packet B.packet (A.packet ∪ B.packet) :: H) kfinal terminal finalCursor

namespace PackedCursorSchedule
variable {n : Nat} {site : Nat → Fin n}
  {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
  {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}

def cost {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .lower _ _ _ rest => rest.cost
  | .birth (k := i) _ _ _ _ rest => cursorTurn n cursor.val (site i).val + 1 + rest.cost
  | .fusion A _ _ _ _ _ rest =>
      let f := A.leaves.length - 1
      cursorTurn n cursor.val ((site A.firstLeaf).val+f) + 2*f+1 + rest.cost

def debt {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .lower _ _ _ rest => rest.debt
  | .birth _ _ _ _ rest => rest.debt
  | .fusion A _ _ _ _ _ rest => (A.leaves.length - 1) + rest.debt

def windings {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .lower _ _ _ rest => rest.windings
  | .birth (k := i) _ _ _ _ rest => cursorWinding cursor.val (site i).val + rest.windings
  | .fusion A _ _ _ _ _ rest =>
      cursorWinding cursor.val ((site A.firstLeaf).val+(A.leaves.length-1)) + rest.windings

def birthZeros {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .lower _ _ _ rest => rest.birthZeros
  | .birth (k := i) _ _ _ _ rest =>
      (if cursorWinding cursor.val (site i).val = 0 then 1 else 0) + rest.birthZeros
  | .fusion _ _ _ _ _ _ rest => rest.birthZeros

def fusionZeros {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .lower _ _ _ rest => rest.fusionZeros
  | .birth _ _ _ _ rest => rest.fusionZeros
  | .fusion A _ _ _ _ _ rest =>
      (if cursorWinding cursor.val ((site A.firstLeaf).val+(A.leaves.length-1)) = 0
        then 1 else 0) + rest.fusionZeros

theorem toPath (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    UpperForestPath k xs H kfinal terminal := by
  induction s with
  | nil same => exact .nil same
  | birth a roots before after rest ih => exact .cons (.transfer a roots before after) ih
  | lower A B same rest ih => exact .cons (.lower A B same) ih
  | fusion A B roots before after gap rest ih => exact .cons (.fusion A B roots before after) ih

theorem payment (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    s.cost + finalCursor.val = upperCursorEventCount H + s.debt + n*s.windings + cursor.val := by
  induction s with
  | nil same => simp [cost, debt, windings, upperCursorEventCount]
  | lower A B same rest ih => simpa [cost, debt, windings, upperCursorEventCount] using ih
  | @birth i xs ys c H kf terminal cf a roots before after rest ih =>
      have hp := transfer_cursor_payment c.isLt (site i).isLt
      simp only [cost, debt, windings, upperCursorEventCount, Nat.mul_add]
      omega
  | @fusion i xs ys c H kf terminal cf A B roots before after gap rest ih =>
      have hsize := A.leaves_length_pos
      have hbound : (site A.firstLeaf).val + (A.leaves.length-1) < n := by
        have hb := (site B.firstLeaf).isLt
        omega
      have hp := fusion_cursor_payment c.isLt hbound
      simp only [cost, debt, windings, upperCursorEventCount, Nat.mul_add]
      omega

theorem winding_partition (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    s.windings + s.birthZeros + s.fusionZeros = upperCursorEventCount H := by
  induction s with
  | nil same => simp [windings, birthZeros, fusionZeros, upperCursorEventCount]
  | lower A B same rest ih => simpa [windings, birthZeros, fusionZeros, upperCursorEventCount] using ih
  | @birth i xs ys c H kf terminal cf a roots before after rest ih =>
      by_cases he : c.val < (site i).val <;>
        simp [windings, birthZeros, fusionZeros, upperCursorEventCount, cursorWinding, he] <;> omega
  | @fusion i xs ys c H kf terminal cf A B roots before after gap rest ih =>
      by_cases he : c.val < (site A.firstLeaf).val+(A.leaves.length-1) <;>
        simp [windings, birthZeros, fusionZeros, upperCursorEventCount, cursorWinding, he] <;> omega

theorem event_length_balance (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    upperCursorEventCount H + terminal.length + 2*k = xs.length + 2*kfinal := by
  induction s with
  | nil same => have he := same.perm.length_eq; simp [upperCursorEventCount]; omega
  | lower A B same rest ih =>
      have he := same.perm.length_eq
      simp only [upperCursorEventCount]
      omega
  | birth a roots before after rest ih =>
      have hb := before.perm.length_eq
      have ha := after.perm.length_eq
      simp only [List.length_cons, upperCursorEventCount] at ha ⊢
      omega
  | fusion A B roots before after gap rest ih =>
      have hb := before.perm.length_eq
      have ha := after.perm.length_eq
      simp only [List.length_cons, upperCursorEventCount] at hb ha ⊢
      omega

theorem debt_balance (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    forestGapDebt terminal = forestGapDebt xs + s.debt := by
  induction s with
  | nil same =>
      simpa [forestGapDebt, debt] using (same.perm.map UpperFusionTree.leftGapDebt).sum_eq.symm
  | lower A B same rest ih =>
      have he := (same.perm.map UpperFusionTree.leftGapDebt).sum_eq
      simp only [forestGapDebt, debt] at ih ⊢
      omega
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
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor) (i : Nat) :
    k ≤ i → i < kfinal → (site i).val = 0 → 1 ≤ s.birthZeros := by
  induction s with
  | nil same => intro hk hi hz; omega
  | lower A B same rest ih => exact ih
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
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal finalCursor)
    (i : Nat) (packet : Finset (Fin n)) (R : UpperFusionTree n) (hz : (site i).val = 0) :
    (∀ tree ∈ xs, ¬ (UpperFusionTree.merge (.leaf i packet) R).Subtree tree) →
    (∃ tree ∈ terminal, (UpperFusionTree.merge (.leaf i packet) R).Subtree tree) →
    1 ≤ s.fusionZeros := by
  induction s with
  | nil same =>
      intro absent present
      obtain ⟨tree, ht, hs⟩ := present
      exact False.elim (absent tree (same.perm.mem_iff.mpr ht) hs)
  | lower A B same rest ih =>
      intro absent present
      exact ih (fun tree ht hs => absent tree (same.perm.mem_iff.mpr ht) hs) present
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
    (s : PackedCursorSchedule site 0 [] (site 0) H kfinal [T] finalCursor)
    (i : Nat) (hi : i < kfinal) (hz : (site i).val = 0) :
    1 ≤ s.birthZeros ∧ (0 < (site 0).val → 2 ≤ s.birthZeros) := by
  induction H with
  | nil =>
      cases s with
      | nil same => have he := same.perm.length_eq; simp at he
  | cons event H ih =>
      cases s with
      | @lower _ _ ys _ _ _ _ _ A B same rest =>
          have hempty : ys = ([] : List (UpperFusionTree n)) := by
            apply List.length_eq_zero_iff.mp
            simpa using same.perm.length_eq.symm
          subst hempty
          exact ih rest
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

end PackedCursorSchedule

theorem PackedCursorSchedule.initial_winding_bounds
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {T : UpperFusionTree n} {kfinal : Nat} {finalCursor : Fin n}
    (s : PackedCursorSchedule site 0 [] (site 0) H kfinal [T] finalCursor)
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
theorem PackedCursorSchedule.cost_le_with_defect
    {n : Nat} {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    {T : UpperFusionTree n} {t : Nat} {finalCursor : Fin n}
    (s : PackedCursorSchedule site 0 [] (site 0) H t [T] finalCursor)
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
  have hH : upperCursorEventCount H = 2*t-1 := by omega
  rw [hH] at hp
  omega

end RSR2History
