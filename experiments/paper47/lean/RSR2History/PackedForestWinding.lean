import RSR2History.PackedCursorSchedule
import RSR2History.ForestWindingReplay

/-! The winding charge of a packed cursor schedule depends on transfer
occurrences and ordered tree shapes. Erasing lower events and forgetting
packet labels preserves this charge, so the geometric phase bounds for a
singleton cursor schedule apply to the packed schedule as well. -/

namespace RSR2History

open RSR2.Parametric

namespace PackedCursorSchedule

private def shape (a : Fin n) : UpperFusionTree n → UpperFusionTree n
  | .leaf i _ => .leaf i {a}
  | .merge A B => .merge (shape a A) (shape a B)

@[simp] private theorem shape_leaves (a : Fin n) (T : UpperFusionTree n) :
    (shape a T).leaves = T.leaves := by
  induction T <;> simp_all [shape, UpperFusionTree.leaves]

@[simp] private theorem shape_firstLeaf (a : Fin n) (T : UpperFusionTree n) :
    (shape a T).firstLeaf = T.firstLeaf := by
  induction T <;> simp_all [shape, UpperFusionTree.firstLeaf]

@[simp] private theorem shape_packet (a : Fin n) (T : UpperFusionTree n) :
    (shape a T).packet = {a} := by
  induction T <;> simp_all [shape, UpperFusionTree.packet]

private def shapeLog (a : Fin n) : List (EffectiveEvent n) → List (EffectiveEvent n)
  | [] => []
  | .transfer _ :: H => .transfer {a} :: shapeLog a H
  | .fusion false _ _ _ :: H => shapeLog a H
  | .fusion true _ _ _ :: H => .fusion true {a} {a} ({a} ∪ {a}) :: shapeLog a H

private theorem shapeLog_length (a : Fin n) (H : List (EffectiveEvent n)) :
    (shapeLog a H).length = upperCursorEventCount H := by
  induction H with
  | nil => rfl
  | cons e H ih =>
      cases e with
      | transfer B => simp [shapeLog, upperCursorEventCount, ih, Nat.add_comm]
      | fusion layer A B C =>
          cases layer <;> simp [shapeLog, upperCursorEventCount, ih, Nat.add_comm]

private theorem shapeLog_has_fusion (a : Fin n) {H : List (EffectiveEvent n)}
    (fused : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H) :
    EffectiveEvent.fusion true {a} {a} ({a} ∪ {a}) ∈ shapeLog a H := by
  induction H with
  | nil => simp at fused
  | cons e H ih =>
      obtain ⟨A, B, C, he⟩ := fused
      cases e with
      | transfer packet =>
          exact List.mem_cons_of_mem _ (ih ⟨A, B, C, by simpa using he⟩)
      | fusion layer X Y Z =>
          cases layer with
          | false => exact ih ⟨A, B, C, by simpa using he⟩
          | true => exact List.mem_cons_self

private theorem reframe_shape_schedule
    {n k kfinal : Nat} {site : Nat → Fin n}
    {xs ys terminal : List (UpperFusionTree n)} {cursor cf : Fin n}
    {H : List (EffectiveEvent n)}
    (u : UpperCursorSchedule site k ys cursor H kfinal terminal cf)
    (same : xs.IsRotated ys) :
    ∃ u' : UpperCursorSchedule site k xs cursor H kfinal terminal cf,
      u'.windings = u.windings := by
  cases u with
  | nil h => exact ⟨.nil (same.trans h), rfl⟩
  | birth b roots before after rest =>
      exact ⟨.birth b roots (same.trans before) after rest, rfl⟩
  | fusion A B roots before after gap rest =>
      exact ⟨.fusion A B roots (same.trans before) after gap rest, rfl⟩

private theorem change_shape_cursor
    {n k kfinal : Nat} {site : Nat → Fin n}
    {xs terminal : List (UpperFusionTree n)} {cursor cursor' cf : Fin n}
    {H : List (EffectiveEvent n)}
    (u : UpperCursorSchedule site k xs cursor H kfinal terminal cf)
    (same : cursor = cursor') :
    ∃ u' : UpperCursorSchedule site k xs cursor' H kfinal terminal cf,
      u'.windings = u.windings := by
  cases same
  exact ⟨u, rfl⟩

private theorem change_shape_log
    {n k kfinal : Nat} {site : Nat → Fin n}
    {xs terminal : List (UpperFusionTree n)} {cursor cf : Fin n}
    {H H' : List (EffectiveEvent n)}
    (u : UpperCursorSchedule site k xs cursor H kfinal terminal cf)
    (same : H = H') :
    ∃ u' : UpperCursorSchedule site k xs cursor H' kfinal terminal cf,
      u'.windings = u.windings := by
  cases same
  exact ⟨u, rfl⟩

private theorem exists_shape_schedule
    {n k kfinal : Nat} {site : Nat → Fin n}
    {xs terminal : List (UpperFusionTree n)} {cursor cf : Fin n}
    {H : List (EffectiveEvent n)} (a : Fin n)
    (s : PackedCursorSchedule site k xs cursor H kfinal terminal cf) :
    ∃ u : UpperCursorSchedule site k (xs.map (shape a)) cursor (shapeLog a H)
        kfinal (terminal.map (shape a)) cf,
      u.windings = s.windings := by
  induction s with
  | nil same =>
      exact ⟨.nil (same.map _), rfl⟩
  | lower A B same rest ih =>
      obtain ⟨u, hu⟩ := ih
      obtain ⟨u', hu'⟩ := reframe_shape_schedule u (same.map (shape a))
      exact ⟨u', hu'.trans hu⟩
  | birth packet roots before after rest ih =>
      obtain ⟨u, hu⟩ := ih
      refine ⟨.birth a (roots.map (shape a)) (before.map _) ?_ u, ?_⟩
      · simpa only [List.map_cons, shape] using after.map (shape a)
      · simp [UpperCursorSchedule.windings, windings, hu]
  | @fusion i xs ys cur H kf terminal cf A B roots before after gap rest ih =>
      obtain ⟨u, hu⟩ := ih
      obtain ⟨u', hu'⟩ := change_shape_cursor u
        (congrArg site (shape_firstLeaf a A).symm)
      have hbefore := before.map (shape a)
      have hafter := after.map (shape a)
      let v := UpperCursorSchedule.fusion (cursor := cur)
        (shape a A) (shape a B) (roots.map (shape a))
        hbefore hafter (by simpa only [shape_firstLeaf, shape_leaves] using gap) u'
      obtain ⟨v', hv'⟩ := change_shape_log v
        (show _ = shapeLog a (.fusion true A.packet B.packet (A.packet ∪ B.packet) :: H) by
          simp only [shapeLog, shape_packet])
      refine ⟨v', hv'.trans ?_⟩
      simp only [v, UpperCursorSchedule.windings, windings, shape_leaves, shape_firstLeaf,
        hu', hu]

/-- At least two upper events fail to wind if the schedule contains an upper
fusion. At equality the final phase covers the initial phase. -/
theorem forest_winding_phase_payment
    {n kfinal : Nat} {site : Nat → Fin n} {terminal : List (UpperFusionTree n)}
    {H : List (EffectiveEvent n)} {cf : Fin n}
    (s : PackedCursorSchedule site 0 [] (site 0) H kfinal terminal cf)
    (hzero : ∃ i, i < kfinal ∧ (site i).val = 0)
    (hfusion : ∃ A B C, EffectiveEvent.fusion true A B C ∈ H) :
    n*s.windings + (site 0).val ≤ n*(upperCursorEventCount H-2) + cf.val := by
  obtain ⟨u, hu⟩ := s.exists_shape_schedule (site 0)
  have hfu := shapeLog_has_fusion (site 0) hfusion
  have hb := u.forest_winding_phase_payment hzero ⟨_, _, hfu⟩
  rwa [hu, shapeLog_length] at hb

private theorem upper_initial_phase_payment
    {n kfinal : Nat} {site : Nat → Fin n} {terminal : List (UpperFusionTree n)}
    {H : List (EffectiveEvent n)} {cf : Fin n}
    (u : UpperCursorSchedule site 0 [] (site 0) H kfinal terminal cf)
    (hpos : 0 < kfinal) :
    n*u.windings + (site 0).val ≤ n*(H.length-1) + cf.val := by
  cases u with
  | nil same => omega
  | fusion A B roots before after gap rest =>
      have he := before.perm.length_eq
      simp at he
  | @birth i xs ys cur tailEvents kf terminal cf a roots before after rest =>
      have hpart := rest.winding_partition
      simp only [UpperCursorSchedule.windings, cursorWinding, lt_self_iff_false,
        if_false, Nat.zero_add, List.length_cons, Nat.add_sub_cancel]
      by_cases hmax : rest.windings = tailEvents.length
      · have hphase := rest.final_phase_ge_of_all_winding (c := (site 0).val) hmax
          (fun T hT hsmall => by
            rcases List.mem_cons.mp (after.perm.mem_iff.mp hT) with rfl | hT'
            · simp [UpperFusionTree.firstLeaf] at hsmall
            · have hz : roots = [] := by
                have hl := before.perm.length_eq
                simpa using hl.symm
              simp [hz] at hT') (Or.inl le_rfl)
        rw [hmax]
        omega
      · have hmul := Nat.mul_le_mul_left n (show rest.windings+1 ≤ tailEvents.length by omega)
        rw [Nat.mul_add, Nat.mul_one] at hmul
        exact by have hi := (site 0).isLt; omega

/-- Every nonempty empty-start schedule has a phase-adjusted saving of at
least one upper event. In the absence of upper fusions the event count is
exactly the number of transfers. -/
theorem forest_initial_winding_phase_payment
    {n kfinal : Nat} {site : Nat → Fin n} {terminal : List (UpperFusionTree n)}
    {H : List (EffectiveEvent n)} {cf : Fin n}
    (s : PackedCursorSchedule site 0 [] (site 0) H kfinal terminal cf)
    (hpos : 0 < kfinal) :
    n*s.windings + (site 0).val ≤ n*(upperCursorEventCount H-1) + cf.val := by
  obtain ⟨u, hu⟩ := s.exists_shape_schedule (site 0)
  have hb := upper_initial_phase_payment u hpos
  rwa [hu, shapeLog_length] at hb

/-- If no upper root is merged, the phase-adjusted winding charge is at
most one complete turn for each transfer after the first. -/
theorem forest_transfer_only_winding_phase_payment
    {n kfinal : Nat} {site : Nat → Fin n} {terminal : List (UpperFusionTree n)}
    {H : List (EffectiveEvent n)} {cf : Fin n}
    (s : PackedCursorSchedule site 0 [] (site 0) H kfinal terminal cf)
    (hpos : 0 < kfinal) (hroots : terminal.length = kfinal) :
    n*s.windings + (site 0).val ≤ n*(kfinal-1) + cf.val := by
  have he := s.event_length_balance
  simp only [List.length_nil, Nat.mul_zero, Nat.add_zero, Nat.zero_add] at he
  have hc : upperCursorEventCount H = kfinal := by omega
  simpa only [hc] using s.forest_initial_winding_phase_payment hpos

end PackedCursorSchedule

end RSR2History
