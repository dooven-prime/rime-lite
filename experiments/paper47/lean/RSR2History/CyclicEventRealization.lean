import RSR2History.CyclicEventRelation

namespace RSR2History

open RSR2.Parametric

/-- H2-A: each combinatorial event edge has physical representatives joined
by one actual event letter. Silent preparation supplies those representatives. -/
theorem CyclicEventEdge.port_realization {n : Nat} (hn : 1 < n)
    {P Q : Placement n} {event : EffectiveEvent n} (h : CyclicEventEdge P event Q) :
    ∃ S T letter, EventStep n hn S T letter event ∧
      SameCyclicSignatures P S ∧ SameCyclicSignatures Q T := by
  cases h with
  | fusion layer left right tail Q hL hR hd hs ht ho =>
      obtain ⟨S, hPS, hslots, hother⟩ :=
        prepare_packed_layer hn P layer (left :: right :: tail) hs
      have hslots' : layerSlots S layer = left :: right ::
          (tail ++ List.replicate (n-(left :: right :: tail).length) ∅) := by
        simpa using hslots
      have hleft := layerSlots_head n (by omega) S layer left _ hslots'
      have hright := layerSlots_second n hn S layer left right _ hslots'
      have hbusy : occupiedAt S layer (site0 n (by omega)) ∧
          occupiedAt S layer (site1 n hn) := by
        rw [← packetAt_nonempty, ← packetAt_nonempty, hleft, hright]
        exact ⟨hL, hR⟩
      have hstep : EventStep n hn S (collapse n hn S layer) (.d layer)
          (.fusion layer left right (left ∪ right)) :=
        ⟨step_d n hn S layer, by simp [emittedEvents, hbusy, hleft, hright]⟩
      have htail : stripEmpty (∅ : Finset (Fin n)) tail = tail := by
        apply stripEmpty_of_nonempty
        intro block hb
        exact rotated_signature_nonempty hs block (by simp [hb])
      have hsig : cyclicSignature (collapse n hn S layer) layer = (left ∪ right) :: tail := by
        have hU : (left ∪ right).Nonempty := hL.mono Finset.subset_union_left
        rw [signature_of_head _ layer (layerSlots_collapse_head n hn S layer _ _ _ hslots') hU]
        congr 1
        simpa [stripEmpty] using
          (stripEmpty_append_empty tail (n-(left :: right :: tail).length)).trans htail
      refine ⟨S, collapse n hn S layer, .d layer, hstep,
        (silent_reachable_iff_cyclic_signatures n hn P S).mp hPS, ?_⟩
      intro other
      by_cases he : other = layer
      · subst other
        simpa [hsig] using ht
      · have heq := (layerSlots_collapse_other n hn S layer other he).trans (hother other he)
        have hsigOther : cyclicSignature (collapse n hn S layer) other = cyclicSignature P other :=
          congrArg (stripEmpty ∅) heq
        rw [hsigOther]
        exact (ho other he).symm
  | transfer packet lower upper Q hp hls hlt hus hut hc =>
      obtain ⟨R, hPR, hlo, hRother⟩ := prepare_packed_layer hn P false (packet :: lower) hls
      have hupper : (cyclicSignature R true).IsRotated upper := by
        change (stripEmpty ∅ (layerSlots R true)).IsRotated upper
        rw [hRother true (by decide)]
        exact hus
      have hupfilter : stripEmpty (∅ : Finset (Fin n)) upper = upper :=
        stripEmpty_of_nonempty (rotated_signature_nonempty hus)
      let uslots : List (Finset (Fin n)) := ∅ :: (upper ++ List.replicate (n-upper.length-1) ∅)
      have huslots : uslots.length = n := by simp [uslots]; omega
      have husig : stripEmpty ∅ uslots = upper := by
        simpa [uslots, stripEmpty] using
          (stripEmpty_append_empty upper (n-upper.length-1)).trans hupfilter
      obtain ⟨S, hRS, hup, hSother⟩ := prepare_layer_slots hn R true uslots huslots
        (by rw [husig]; exact hupper)
      have hlo' : layerSlots S false = packet ::
          (lower ++ List.replicate (n-(packet :: lower).length) ∅) := by
        simpa using (hSother false (by decide)).trans hlo
      have hup' : layerSlots S true = ∅ ::
          (upper ++ List.replicate (n-upper.length-1) ∅) := hup
      have hsource := layerSlots_head n (by omega) S false packet _ hlo'
      have hempty := layerSlots_head n (by omega) S true ∅ _ hup'
      have hguard : liftGuard n (by omega) S := by
        constructor
        · rw [← packetAt_nonempty, hsource]; exact hp
        · rw [← packetAt_nonempty, hempty]; simp
      have hstep : EventStep n hn S (liftPacket n (by omega) S) .v (.transfer packet) := by
        exact ⟨(step_v_eq_some_iff n hn S _).mpr ⟨hguard, rfl⟩,
          by simp [emittedEvents, hsource]⟩
      have hlofilter : stripEmpty (∅ : Finset (Fin n)) lower = lower := by
        apply stripEmpty_of_nonempty
        intro block hb
        exact rotated_signature_nonempty hls block (by simp [hb])
      have hsigLo : cyclicSignature (liftPacket n (by omega) S) false = lower := by
        have hl := layerSlots_lift_lower n (by omega) S packet _ hlo'
        simpa [cyclicSignature, stripEmpty, hl] using
          (stripEmpty_append_empty lower (n-(packet :: lower).length)).trans hlofilter
      have hsigUp : cyclicSignature (liftPacket n (by omega) S) true = packet :: upper := by
        have hu := layerSlots_lift_upper n (by omega) S packet _ hsource hup'
        rw [signature_of_head _ true hu hp, stripEmpty_append_empty, hupfilter]
      refine ⟨S, liftPacket n (by omega) S, .v, hstep,
        (silent_reachable_iff_cyclic_signatures n hn P S).mp (hPR.trans hRS), ?_⟩
      intro layer
      cases layer with
      | false => simpa [hsigLo] using hlt
      | true => simpa [hsigUp] using hut

/-- Lift one abstract event to one guarded word with exactly its singleton log. -/
theorem CyclicEventEdge.realize {n : Nat} (hn : 1 < n)
    {P Q : Placement n} {event : EffectiveEvent n} (h : CyclicEventEdge P event Q) :
    ∃ word, runLogged n hn P word = some (Q, [event]) := by
  obtain ⟨S, T, letter, hstep, hpre, hpost⟩ := h.port_realization hn
  exact event_transport hn hstep hpre hpost

/-- The abstract rule is exactly the image of a physical event edge under
cyclic equivalence, not an assumed admissibility certificate. -/
theorem cyclicEventEdge_iff_port_representatives (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (event : EffectiveEvent n) :
    CyclicEventEdge P event Q ↔
      ∃ S T letter, EventStep n hn S T letter event ∧
        SameCyclicSignatures P S ∧ SameCyclicSignatures Q T := by
  refine ⟨fun h => h.port_realization hn, ?_⟩
  rintro ⟨S, T, letter, he, hP, hQ⟩
  exact he.cyclicEventEdge.congr hP hQ

end RSR2History
