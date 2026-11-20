import RSR2History.MultiRootCursorGeometry

/-! The actual final cursor is anchored at one of the surviving named
roots. This fact is independent of the fusion-tree shape and event timing. -/
namespace RSR2History
open RSR2.Parametric

theorem UpperCursorSchedule.preserves_cursor_anchor
    {n : Nat} {site : Nat → Fin n}
    {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor cf : Fin n} {H : List (EffectiveEvent n)}
    (schedule : UpperCursorSchedule site k xs cursor H kfinal terminal cf)
    (anchor : ∃ T ∈ xs, cursor = site T.firstLeaf) :
    ∃ T ∈ terminal, cf = site T.firstLeaf := by
  induction schedule with
  | nil same =>
      obtain ⟨T, ht, hc⟩ := anchor
      exact ⟨T, same.perm.mem_iff.mp ht, hc⟩
  | @birth k xs ys cursor H kfinal terminal cf a roots before after rest ih =>
      exact ih ⟨.leaf k {a}, after.perm.mem_iff.mpr (by simp), rfl⟩
  | @fusion k xs ys cursor H kfinal terminal cf A B roots before after gap rest ih =>
      exact ih ⟨.merge A B, after.perm.mem_iff.mpr (by simp), rfl⟩

/-- A nonempty actual cursor schedule ends at a live packet anchor. -/
theorem UpperCursorSchedule.final_cursor_anchor
    {n : Nat} {site : Nat → Fin n}
    {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor cf : Fin n} {H : List (EffectiveEvent n)}
    (schedule : UpperCursorSchedule site k xs cursor H kfinal terminal cf)
    (nonempty : H ≠ []) :
    ∃ T ∈ terminal, cf = site T.firstLeaf := by
  cases schedule with
  | nil same => exact (nonempty rfl).elim
  | @birth k xs ys cursor H kfinal terminal cf a roots before after rest =>
      exact rest.preserves_cursor_anchor
        ⟨.leaf k {a}, after.perm.mem_iff.mpr (by simp), rfl⟩
  | fusion A B roots before after gap rest =>
      exact rest.preserves_cursor_anchor
        ⟨.merge A B, after.perm.mem_iff.mpr (by simp), rfl⟩

/-- An actual reserved replay with a nonempty schedule has an occupied
physical port zero. The coordinate equality is not a free rotation. -/
theorem UpperReservedReplay.port_zero_nonempty_of_schedule
    {n : Nat} [NeZero n] {P : Placement n} {cursor cf : Fin n}
    {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {site : Nat → Fin n} {H : List (EffectiveEvent n)}
    (state : UpperReservedReplay P cf kfinal terminal terminal (forestLeaves terminal) site)
    (schedule : UpperCursorSchedule site k xs cursor H kfinal terminal cf)
    (nonempty : H ≠ []) : (packetAt P true 0).Nonempty := by
  obtain ⟨T, ht, hc⟩ := schedule.final_cursor_anchor nonempty
  have he := state.packet_at_anchor ht
  rw [← hc] at he
  have hz : zsite ((cf.val : ZMod n)-(cf.val : ZMod n)) = (0 : Fin n) := by
    simp [zsite]
  rw [hz] at he
  rw [he]
  exact state.packet_nonempty T ht

end RSR2History
