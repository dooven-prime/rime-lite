import RSR2History.PackedLowerExtraction

/-!
Projection of a real effective-event trace to its independent lower
fusion/extraction path. Upper fusions disappear; lower ordered fusions and
whole-packet transfers retain their exact event fields and order. Idle lower
defects may be erased. No comparison with the singleton extraction maximum
is used.
-/
namespace RSR2History
open RSR2.Parametric

/-- Preserve lower fusions and complete transfer records, omitting only
upper fusion events. -/
def packedLowerLog (H : List (EffectiveEvent n)) : List (EffectiveEvent n) :=
  H.filterMap (fun
    | .fusion true _ _ _ => none
    | e => some e)

@[simp] theorem packedLowerLog_nil : packedLowerLog ([] : List (EffectiveEvent n)) = [] := rfl

@[simp] theorem packedLowerLog_lowerFusion (A B C : Finset (Fin n)) (H : List (EffectiveEvent n)) :
    packedLowerLog (.fusion false A B C :: H) = .fusion false A B C :: packedLowerLog H := rfl

@[simp] theorem packedLowerLog_upperFusion (A B C : Finset (Fin n)) (H : List (EffectiveEvent n)) :
    packedLowerLog (.fusion true A B C :: H) = packedLowerLog H := rfl

@[simp] theorem packedLowerLog_transfer (B : Finset (Fin n)) (H : List (EffectiveEvent n)) :
    packedLowerLog (.transfer B :: H) = .transfer B :: packedLowerLog H := rfl

@[simp] theorem packedLowerLog_append (H K : List (EffectiveEvent n)) :
    packedLowerLog (H ++ K) = packedLowerLog H ++ packedLowerLog K := by
  simp [packedLowerLog, List.filterMap_append]

/-- A specified prepared lower fusion is a real one-letter step, preserving
all upper coordinates and the independent lower successor. -/
theorem PackedLowerEvent.fusion_word {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {A B C : Finset (Fin n)} {cost : Nat}
    (event : PackedLowerEvent n hn c (.fusion false A B C) d cost)
    (P : Placement n) (lower : lowerConfiguration P = c) :
    runLogged n hn P [.d false] = some (collapse n hn P false, [.fusion false A B C]) ∧
      lowerConfiguration (collapse n hn P false) = d ∧ cost = 1 ∧
      (∀ a q, collapse n hn P false a = (true,q) ↔ P a = (true,q)) := by
  cases event with
  | fusion left right =>
      have hp0 : packetAt P false (site0 n (by omega)) = lowerPacket c (site0 n (by omega)) := by
        rw [← lowerPacket_configuration, lower]
      have hp1 : packetAt P false (site1 n hn) = lowerPacket c (site1 n hn) := by
        rw [← lowerPacket_configuration, lower]
      have hb : occupiedAt P false (site0 n (by omega)) ∧ occupiedAt P false (site1 n hn) := by
        exact ⟨(packetAt_nonempty _ _ _).mp (hp0.symm ▸ left),
          (packetAt_nonempty _ _ _).mp (hp1.symm ▸ right)⟩
      refine ⟨by simp [runLogged, step_d, emittedEvents, hb, hp0, hp1], ?_, rfl, ?_⟩
      · rw [lowerConfiguration_collapse_lower n hn, lower]
      · intro a q
        by_cases ha : P a = (false, site1 n hn)
        · simp [collapse, ha]
        · simp [collapse, ha]

/-- A real event supplies the corresponding lower event or an empty lower
path when it is an upper fusion. -/
theorem EventStep.packedLower {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {letter : Letter} {event : EffectiveEvent n}
    (h : EventStep n hn P Q letter event) :
    ∃ cost, PackedLowerPath n hn (lowerConfiguration P) (packedLowerLog [event])
      (lowerConfiguration Q) cost ∧ cost ≤ lowerPreparationCount [letter] := by
  classical
  cases letter with
  | p layer => have he := h.2; simp [emittedEvents] at he
  | d layer =>
      have hb : occupiedAt P layer (site0 n (by omega)) ∧ occupiedAt P layer (site1 n hn) := by
        by_contra hb
        have he := h.2
        simp [emittedEvents, hb] at he
      have he := h.2
      simp only [emittedEvents, if_pos hb, List.singleton_inj] at he
      subst event
      have hQ : Q = collapse n hn P layer := by simpa [step_d] using h.1.symm
      subst Q
      cases layer with
      | false =>
          refine ⟨1, ?_, by simp [lowerPreparationCount]⟩
          rw [lowerConfiguration_collapse_lower n hn]
          simp only [packedLowerLog_lowerFusion, packedLowerLog_nil]
          have hleft : (lowerPacket (lowerConfiguration P) (site0 n (by omega))).Nonempty := by
            rw [lowerPacket_configuration]
            exact (packetAt_nonempty _ _ _).mpr hb.1
          have hright : (lowerPacket (lowerConfiguration P) (site1 n hn)).Nonempty := by
            rw [lowerPacket_configuration]
            exact (packetAt_nonempty _ _ _).mpr hb.2
          simpa only [lowerPacket_configuration] using
            (PackedLowerPath.event (PackedLowerEvent.fusion (lowerConfiguration P) hleft hright))
      | true =>
          rw [lowerConfiguration_collapse_upper n hn]
          exact ⟨0, by simpa using (PackedLowerPath.prepare (LowerExtractionPath.refl (lowerConfiguration P))), by simp [lowerPreparationCount]⟩
  | v =>
      have he : event = .transfer (packetAt P false (site0 n (by omega))) := by
        simpa [emittedEvents] using h.2.symm
      subst event
      obtain ⟨guard, hQ⟩ := (step_v_eq_some_iff n hn P Q).mp h.1
      rw [hQ, lowerConfiguration_liftPacket P hn]
      refine ⟨0, ?_, by simp [lowerPreparationCount]⟩
      have hnon : (lowerPacket (lowerConfiguration P) (site0 n (by omega))).Nonempty := by
        rw [lowerPacket_configuration]
        exact (packetAt_nonempty _ _ _).mpr guard.1
      simpa only [packedLowerLog_transfer, packedLowerLog_nil, lowerPacket_configuration] using
        (PackedLowerPath.event (PackedLowerEvent.extract (lowerConfiguration P) hnon))

/-- All path events and all charged preparation come from the same real
trace. Its arbitrary upper interleavings require no lower path edges. -/
theorem ActualEventTrace.packedLower {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {H : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P H Q) :
    ∃ cost, PackedLowerPath n hn (lowerConfiguration P) (packedLowerLog H)
      (lowerConfiguration Q) cost ∧ cost ≤ lowerPreparationCount trace.word := by
  induction trace with
  | done tail htail =>
      obtain ⟨cost, path, bound⟩ := runLogged_empty_lowerExtraction n hn tail htail
      exact ⟨cost, .prepare path, bound⟩
  | cons before silent letter event tail ih =>
      obtain ⟨prep, hp, bp⟩ := runLogged_empty_lowerExtraction n hn before silent
      obtain ⟨paid, he, be⟩ := event.packedLower
      obtain ⟨rest, hr, br⟩ := ih
      refine ⟨prep+paid+rest, ?_, ?_⟩
      · have joined := ((PackedLowerPath.prepare hp).trans he).trans hr
        simpa [← packedLowerLog_append] using joined
      · have hcount := lowerPreparationCount_append [letter] tail.word
        simp only [List.singleton_append] at hcount
        simp only [ActualEventTrace.word, lowerPreparationCount_append]
        omega

/-- Every successful arbitrary real word has an independent packed lower
projection. The bound is on its own lower letters, allowing erased idle d0. -/
theorem runLogged_packedLower_projection {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (run : runLogged n hn P word = some (Q,H)) :
    ∃ cost, PackedLowerPath n hn (lowerConfiguration P) (packedLowerLog H)
      (lowerConfiguration Q) cost ∧ cost ≤ word.count (.p false) + word.count (.d false) := by
  obtain ⟨trace, hword⟩ := actualEventTrace_of_runLogged n hn word run
  obtain ⟨cost, path, bound⟩ := trace.packedLower
  exact ⟨cost, path, by simpa [hword, lowerPreparationCount] using bound⟩

end RSR2History
