import RSR2History.PhaseFreeFusion

/-! Expose the port occupied by the last phase-free fusion. -/

namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

theorem packetAt_mem_cyclicSignature (P : Placement n) (layer : Layer) (q : Fin n)
    (hne : (packetAt P layer q).Nonempty) :
    packetAt P layer q ∈ cyclicSignature P layer := by
  apply List.mem_filter.mpr
  exact ⟨List.mem_ofFn.mpr ⟨q, rfl⟩, by simpa using hne.ne_empty⟩

theorem CyclicEventEdge.phaseFree_fusion_word_at_port (hn : 1 < n)
    {P Q : Placement n} {layer : Layer} {A B C : Finset (Fin n)}
    (edge : CyclicEventEdge P (.fusion layer A B C) Q) :
    ∃ R word, runLogged n hn P word = some (R, [.fusion layer A B C]) ∧
      SameCyclicSignatures R Q ∧ word.length ≤ 3*n-4 ∧
      packetAt R layer (site0 n (by omega)) = C ∧ C.Nonempty := by
  obtain ⟨ha, hb, tail, hs⟩ := edge.fusion_source
  obtain ⟨left, hl⟩ := packet_site_of_mem_signature P layer
    (hs.perm.mem_iff.mpr (by simp : A ∈ A :: B :: tail))
  obtain ⟨right, hr⟩ := packet_site_of_mem_signature P layer
    (hs.perm.mem_iff.mpr (by simp : B ∈ A :: B :: tail))
  obtain ⟨f, hfn, hgap, hholes⟩ :=
    cyclic_parents_gap hn P layer left right A B tail hl hr ha hb hs
  have hw := phaseFreeFusionWord_spec hn P layer left right f hfn hgap
    (hl.symm ▸ ha) (hr.symm ▸ hb) hholes
  have hC : C = A ∪ B := by cases edge; rfl
  subst C
  rw [hl, hr] at hw
  let R := phaseShift (relocateAt P layer right left) layer (-left)
  have hedge := (cyclicEventEdge_iff_one_event_word n hn P R
    (.fusion layer A B (A ∪ B))).mpr ⟨_, hw⟩
  have hsame : SameCyclicSignatures R Q := by
    intro other
    by_cases ho : other = layer
    · subst other
      exact hedge.fusion_target_unique edge (.refl _)
    · cases hedge with
      | fusion _ _ _ _ _ _ _ _ _ _ hu =>
        cases edge with
        | fusion _ _ _ _ _ _ _ _ _ _ hv =>
          exact (hu other ho).symm.trans (hv other ho)
  have hport : packetAt R layer (site0 n (by omega)) = A ∪ B := by
    dsimp only [R]
    rw [← zsite_zero, packetAt_phaseShift]
    simp only [zero_sub, neg_neg]
    rw [packetAt_relocateAt]
    simp [hl, hr, Finset.union_comm]
  refine ⟨R, phaseFreeFusionWord layer left right f, hw, hsame, ?_, hport, ?_⟩
  · have hlen := phaseFreeFusionWord_length_le layer left right f
    omega
  · exact ha.mono Finset.subset_union_left

/-- A nonempty all-lower fusion log can be replayed with its final packet
at lower port zero, without an extra phase-restoration word. -/
theorem CyclicEventPath.phaseFree_lower_fusion_replay_port (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (path : CyclicEventPath P events Q)
    (hfusion : ∀ e ∈ events, ∃ A B C, e = .fusion false A B C)
    (hne : events ≠ []) :
    ∀ P', SameCyclicSignatures P' P →
      ∃ R word, runLogged n hn P' word = some (R, events) ∧
        SameCyclicSignatures R Q ∧ word.length ≤ (3*n-4)*events.length ∧
        (packetAt R false (site0 n (by omega))).Nonempty := by
  induction path with
  | nil same => exact (hne rfl).elim
  | @cons P S Q event events edge tail ih =>
      intro P' hP
      obtain ⟨A, B, C, hevent⟩ := hfusion event (by simp)
      subst event
      obtain ⟨R, first, hfirst, hsame, hlen, hport, hC⟩ :=
        (edge.congr hP (.refl _)).phaseFree_fusion_word_at_port hn
      by_cases he : events = []
      · subst events
        cases tail with
        | nil same =>
            refine ⟨R, first, hfirst, hsame.trans same, ?_, ?_⟩
            · simpa using hlen
            · rwa [hport]
      · have hrest : ∀ e ∈ events, ∃ A B C, e = .fusion false A B C := by
          intro e he
          exact hfusion e (by simp [he])
        obtain ⟨T, rest, hrun, hfinal, hrestLen, hbusy⟩ := ih hrest he R hsame
        refine ⟨T, first ++ rest, ?_, hfinal, ?_, hbusy⟩
        · simp [runLogged_append, hfirst, hrun]
        · rw [List.length_append, List.length_cons]
          nlinarith

end RSR2History
