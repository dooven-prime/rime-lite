import RSR2History.CyclicEventDeterminism

/-! Exact ordered fusion at linear cost when the ending phase is free. -/

namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

private theorem map_singleRing_pWord (layer : Layer) (k : Nat) :
    (RegisteredAbsorptionChains.pWord k).map (layerLetter layer) = pWord layer k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    simp only [RegisteredAbsorptionChains.pWord,
      List.map_append, List.map_cons, List.map_nil, layerLetter]
    rw [ih]
    simpa [pWord] using (List.replicate_succ' (n := k) (a := Letter.p layer)).symm

private theorem runLogged_unphase_suffix (hn : 1 < n) (P Q : Placement n)
    (word : List Letter) (layer : Layer) (amount : ZMod n)
    (H : List (EffectiveEvent n))
    (hrun : runLogged n hn P (word ++ pWord layer amount.val) = some (Q, H)) :
    runLogged n hn P word = some (phaseShift Q layer (-amount), H) := by
  rw [runLogged_append] at hrun
  cases hw : runLogged n hn P word with
  | none => simp [hw] at hrun
  | some result =>
    obtain ⟨R, events⟩ := result
    simp only [hw, Option.bind_some, runLogged_phase, Option.map_some,
      List.append_nil, Option.some.injEq, Prod.mk.injEq] at hrun
    rcases hrun with ⟨hQ, hH⟩
    have hR : phaseShift Q layer (-amount) = R := by
      rw [← hQ, phaseShift_add]
      have he : amount + -amount = 0 := by ring
      rw [he, phaseShift_zero]
    rw [← hR, ← hH]

def phaseFreeFusionWord (layer : Layer) (left right : ZMod n) (f : Nat) : List Letter :=
  if f = 0 then pWord layer (-left).val ++ [.d layer]
  else pWord layer (1-right).val ++ [.d layer] ++
    (FusionLogCompression.pdWord (f-1)).map (layerLetter layer) ++ [.p layer, .d layer]

theorem phaseFreeFusionWord_length_le (layer : Layer)
    (left right : ZMod n) (f : Nat) :
    (phaseFreeFusionWord layer left right f).length ≤ n + 2*f := by
  have hleft := ZMod.val_lt (-left)
  have hright := ZMod.val_lt (1-right)
  by_cases hf : f = 0
  · simp [phaseFreeFusionWord, hf, pWord]
    omega
  · simp only [phaseFreeFusionWord, if_neg hf, List.length_append,
      pWord, List.length_replicate, List.length_map, FusionLogCompression.pdWord_length,
      List.length_cons, List.length_nil]
    omega

/-- Exact event replay without restoring the input phase. The residual phase
is explicit and can be reused as the next event's starting geometry. -/
theorem phaseFreeFusionWord_spec (hn : 1 < n) (P : Placement n) (layer : Layer)
    (left right : ZMod n) (f : Nat) (hfn : f ≤ n-2)
    (hgap : right = left+1+(f : ZMod n))
    (hleft : (packetAt P layer (zsite left)).Nonempty)
    (hright : (packetAt P layer (zsite right)).Nonempty)
    (hholes : ∀ j : Nat, 1 ≤ j → j ≤ f →
      packetAt P layer (zsite (right-j)) = ∅) :
    runLogged n hn P (phaseFreeFusionWord layer left right f) =
      some (phaseShift (relocateAt P layer right left) layer (-left),
        [.fusion layer (packetAt P layer (zsite left)) (packetAt P layer (zsite right))
          (packetAt P layer (zsite left) ∪ packetAt P layer (zsite right))]) := by
  by_cases hf : f = 0
  · subst f
    have hright' : right = left+1 := by simpa using hgap
    obtain ⟨hw, _⟩ := phaseFusionWord_spec hn P layer left hleft
      (by simpa [hright'] using hright)
    have hw' : runLogged n hn P
        ((pWord layer (-left).val ++ [.d layer]) ++ pWord layer left.val) =
        some (relocateAt P layer right left,
          [.fusion layer (packetAt P layer (zsite left)) (packetAt P layer (zsite right))
            (packetAt P layer (zsite left) ∪ packetAt P layer (zsite right))]) := by
      simpa [phaseFusionWord, hright', List.append_assoc] using hw
    exact runLogged_unphase_suffix hn P _ (pWord layer (-left).val ++ [.d layer])
      layer left _ hw'
  · have hn3 : 3 ≤ n := by omega
    have hvia : right-(f : ZMod n) = left+1 := by rw [hgap]; ring
    have hval : (right-(f : ZMod n)).val = (left+1).val :=
      congrArg ZMod.val hvia
    let core := pWord layer (1-right).val ++ [.d layer] ++
      (FusionLogCompression.pdWord (f-1)).map (layerLetter layer)
    have hsplit :
        (FusionLogCompression.batchWord right f).map (layerLetter layer) =
          core ++ pWord layer (left+1).val := by
      simp [FusionLogCompression.batchWord, core, List.map_append,
        map_singleRing_pWord, hval, layerLetter]
    obtain ⟨hbatch, _⟩ := reservedBatchWord_spec hn3 P layer right f (by omega)
      hfn hright hholes
    rw [hsplit] at hbatch
    rw [hvia] at hbatch
    have hprefix : runLogged n hn P core =
        some (phaseShift (relocateAt P layer right (left+1)) layer (-(left+1)), []) :=
      runLogged_unphase_suffix hn P _ core layer (left+1) [] hbatch
    let R := relocateAt P layer right (left+1)
    let T := phaseShift R layer (-left)
    have hrot : rotate n (by omega)
        (phaseShift R layer (-(left+1))) layer = T := by
      have hp : rotate n (by omega) (phaseShift R layer (-(left+1))) layer =
          phaseShift (phaseShift R layer (-(left+1))) layer 1 := by
        simpa [rotateMany] using rotateMany_eq_phaseShift (by omega)
          (phaseShift R layer (-(left+1))) layer 1
      rw [hp, phaseShift_add]
      congr 1
      ring
    have hempty : packetAt P layer (zsite (left+1)) = ∅ := by
      rw [← hvia]
      exact hholes f (by omega) (by omega)
    have hd := gap_sites_distinct hn left f hfn
    have h0 : packetAt T layer (site0 n (by omega)) = packetAt P layer (zsite left) := by
      rw [← zsite_zero, packetAt_phaseShift]
      simp only [zero_sub, neg_neg]
      rw [packetAt_relocateAt, if_neg hd.2, if_neg (hgap ▸ hd.1)]
    have h1 : packetAt T layer (site1 n hn) = packetAt P layer (zsite right) := by
      rw [← zsite_one hn, packetAt_phaseShift]
      have he : (1 : ZMod n) - -left = left+1 := by ring
      rw [he, packetAt_relocateAt]
      simp [hempty]
    have hbusy : occupiedAt T layer (site0 n (by omega)) ∧
        occupiedAt T layer (site1 n hn) :=
      ⟨(packetAt_nonempty _ _ _).mp (h0.symm ▸ hleft),
        (packetAt_nonempty _ _ _).mp (h1.symm ▸ hright)⟩
    have hcollapse : collapse n hn T layer =
        phaseShift (relocateAt P layer right left) layer (-left) := by
      have hc := collapse_phase_restored hn R layer left
      have hc' := congrArg (fun Q => phaseShift Q layer (-left)) hc
      rw [phaseShift_add] at hc'
      simp only [add_neg_cancel, phaseShift_zero] at hc'
      rw [relocateAt_compose_empty P layer right (left+1) left hempty] at hc'
      exact hc'
    have hword : phaseFreeFusionWord layer left right f =
        core ++ [.p layer, .d layer] := by simp [phaseFreeFusionWord, hf, core]
    rw [hword, runLogged_append, hprefix]
    simp only [Option.bind_some, runLogged, step_p, Option.bind_some]
    rw [hrot]
    simp [step_d, hbusy, h0, h1, hcollapse, emittedEvents]

/-- A cyclic event edge has a linear raw-word realization when the ending
phase is free. This is the event-level primitive for replay without restoring
each intermediate literal placement. -/
theorem CyclicEventEdge.phaseFree_fusion_word_preserves (hn : 1 < n)
    {P Q : Placement n} {layer : Layer} {A B C : Finset (Fin n)}
    (edge : CyclicEventEdge P (.fusion layer A B C) Q) :
    ∃ R word, runLogged n hn P word = some (R, [.fusion layer A B C]) ∧
      SameCyclicSignatures R Q ∧ word.length ≤ 3*n-4 ∧
      (∀ other, other ≠ layer → ∀ q, packetAt R other q = packetAt P other q) := by
  obtain ⟨ha, hb, tail, hs⟩ := edge.fusion_source
  have hAmem : A ∈ cyclicSignature P layer :=
    hs.perm.mem_iff.mpr (by simp)
  have hBmem : B ∈ cyclicSignature P layer :=
    hs.perm.mem_iff.mpr (by simp)
  obtain ⟨left, hl⟩ := packet_site_of_mem_signature P layer hAmem
  obtain ⟨right, hr⟩ := packet_site_of_mem_signature P layer hBmem
  obtain ⟨f, hfn, hgap, hholes⟩ :=
    cyclic_parents_gap hn P layer left right A B tail hl hr ha hb hs
  have hw := phaseFreeFusionWord_spec hn P layer left right f hfn hgap
    (hl.symm ▸ ha) (hr.symm ▸ hb) hholes
  have hC : C = A ∪ B := by cases edge; rfl
  subst C
  rw [hl, hr] at hw
  let R := phaseShift (relocateAt P layer right left) layer (-left)
  have hedge := (cyclicEventEdge_iff_one_event_word n hn P R
    (.fusion layer A B (A ∪ B))).mpr
      ⟨phaseFreeFusionWord layer left right f, hw⟩
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
  refine ⟨R, phaseFreeFusionWord layer left right f, hw, hsame, ?_, ?_⟩
  · have hlen := phaseFreeFusionWord_length_le layer left right f
    omega
  · intro other ho q
    dsimp only [R]
    rw [packetAt_phaseShift_other _ _ _ ho, packetAt_relocateAt_other _ _ _ ho]

theorem CyclicEventEdge.phaseFree_fusion_word (hn : 1 < n)
    {P Q : Placement n} {layer : Layer} {A B C : Finset (Fin n)}
    (edge : CyclicEventEdge P (.fusion layer A B C) Q) :
    ∃ R word, runLogged n hn P word = some (R, [.fusion layer A B C]) ∧
      SameCyclicSignatures R Q ∧ word.length ≤ 3*n-4 := by
  obtain ⟨R, word, hw, hs, hc, _⟩ := edge.phaseFree_fusion_word_preserves hn
  exact ⟨R, word, hw, hs, hc⟩

/-- Lower-only replay carries the upper physical layout literally through
every event, rather than merely preserving its cyclic signature. -/
theorem CyclicEventPath.phaseFree_lower_replay_preserves (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (path : CyclicEventPath P events Q)
    (hlower : ∀ e ∈ events, ∃ A B C, e = .fusion false A B C) :
    ∀ P', SameCyclicSignatures P' P →
      ∃ R word, runLogged n hn P' word = some (R, events) ∧
        SameCyclicSignatures R Q ∧ word.length ≤ (3*n-4)*events.length ∧
        (∀ q, packetAt R true q = packetAt P' true q) := by
  induction path with
  | nil same =>
      intro P' hP
      exact ⟨P', [], rfl, hP.trans same, by simp, fun _ => rfl⟩
  | @cons P S Q event events edge tail ih =>
      intro P' hP
      obtain ⟨A, B, C, he⟩ := hlower event (by simp)
      subst event
      obtain ⟨R, first, hf, hs, hc, hp⟩ :=
        (edge.congr hP (.refl _)).phaseFree_fusion_word_preserves hn
      have ht : ∀ e ∈ events, ∃ A B C, e = .fusion false A B C := by
        intro e he
        exact hlower e (by simp [he])
      obtain ⟨T, rest, hr, hts, htc, htp⟩ := ih ht R hs
      refine ⟨T, first ++ rest, ?_, hts, ?_, ?_⟩
      · simp [runLogged_append, hf, hr]
      · simp only [List.length_append, List.length_cons]
        calc
          first.length + rest.length ≤ (3*n-4)+(3*n-4)*events.length := by omega
          _ = (3*n-4)*(events.length+1) := by ring
      · intro q
        exact (htp q).trans (hp true (by decide) q)

/-- A path consisting only of lower-layer fusions can be replayed while
carrying the phase chosen by the previous event. Each event costs at most
3*n-4; the original intermediate literal placements are not restored. -/
theorem CyclicEventPath.phaseFree_fusion_replay_from (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (path : CyclicEventPath P events Q)
    (hfusion : ∀ e ∈ events, ∃ layer A B C, e = .fusion layer A B C) :
    ∀ P', SameCyclicSignatures P' P →
      ∃ R word, runLogged n hn P' word = some (R, events) ∧
        SameCyclicSignatures R Q ∧ word.length ≤ (3*n-4)*events.length := by
  induction path with
  | nil same =>
      intro P' hP
      exact ⟨P', [], rfl, hP.trans same, by simp⟩
  | @cons P S Q event events edge tail ih =>
      intro P' hP
      obtain ⟨layer, A, B, C, hevent⟩ := hfusion event (by simp)
      subst event
      have edge' := edge.congr hP (.refl _)
      obtain ⟨R, first, hfirst, hfirstSame, hfirstLen⟩ :=
        edge'.phaseFree_fusion_word hn
      have hrest : ∀ e ∈ events, ∃ layer A B C, e = .fusion layer A B C := by
        intro e he
        exact hfusion e (by simp [he])
      obtain ⟨T, rest, hrestRun, hrestSame, hrestLen⟩ :=
        ih hrest R hfirstSame
      refine ⟨T, first ++ rest, ?_, hrestSame, ?_⟩
      · simp [runLogged_append, hfirst, hrestRun]
      · calc
          (first ++ rest).length = first.length + rest.length := List.length_append
          _ ≤ (3*n-4) + (3*n-4)*events.length :=
            Nat.add_le_add hfirstLen hrestLen
          _ = (3*n-4)*(EffectiveEvent.fusion layer A B C :: events).length := by
            simp
            ring

theorem CyclicEventPath.phaseFree_fusion_replay (hn : 1 < n)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (path : CyclicEventPath P events Q)
    (hfusion : ∀ e ∈ events, ∃ layer A B C, e = .fusion layer A B C) :
    ∃ R word, runLogged n hn P word = some (R, events) ∧
      SameCyclicSignatures R Q ∧ word.length ≤ (3*n-4)*events.length :=
  path.phaseFree_fusion_replay_from hn hfusion P (.refl _)

end RSR2History
