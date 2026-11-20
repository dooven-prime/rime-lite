import RSR2History.ReservedGeometry

/-! Named lower cycles are updated deterministically by the exact event.
Only transfers' upper insertion gap is intentionally nondeterministic. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

theorem cyclicSignature_nodup (P : Placement n) (layer : Layer) :
    (cyclicSignature P layer).Nodup := by
  rw [signature_eq_occupied_map]
  apply List.Nodup.map_on
  · intro q hq r _ he
    have hne : (packetAt P layer q).Nonempty := by
      apply Finset.nonempty_iff_ne_empty.mpr
      simpa [occupiedSites] using hq
    obtain ⟨a, ha⟩ := hne
    have hq' := (mem_packetAt _ _ _ _).mp ha
    have hr' := (mem_packetAt _ _ _ _).mp (he ▸ ha)
    exact congrArg Prod.snd (hq'.symm.trans hr')
  · exact (List.nodup_finRange n).filter _

private theorem fusion_rewrite (A B : Finset (Fin n)) (tail : List (Finset (Fin n)))
    (hnd : (A :: B :: tail).Nodup) :
    ((A :: B :: tail).filter (fun X => X ≠ B)).map
        (fun X => if X = A then A ∪ B else X) = (A ∪ B) :: tail := by
  have hA := (List.nodup_cons.mp hnd).1
  have hB := (List.nodup_cons.mp (List.nodup_cons.mp hnd).2).1
  have hAB : A ≠ B := by simpa using (fun he => hA (by simp [he]))
  have hf : tail.filter (fun X => X ≠ B) = tail := by
    apply List.filter_eq_self.mpr
    intro X hX
    simp only [decide_eq_true_eq]
    exact fun he => hB (he ▸ hX)
  have hm : tail.map (fun X => if X = A then A ∪ B else X) = tail := by
    calc
      _ = tail.map id := by
        apply List.map_congr_left
        intro X hX
        exact if_neg (fun he => hA (by simp [← he, hX]))
      _ = tail := List.map_id' tail
  have hfilter : (A :: B :: tail).filter (fun X => X ≠ B) = A :: tail := by
    simpa only [List.filter_cons, decide_eq_true hAB,
      show decide (B ≠ B) = false from by simp,
      Bool.false_eq_true, if_false, if_true] using congrArg (List.cons A) hf
  rw [hfilter, List.map_cons, if_pos rfl, hm]

theorem CyclicEventEdge.fusion_target_unique
    {P P' Q Q' : Placement n} {layer : Layer} {A B C : Finset (Fin n)}
    (first : CyclicEventEdge P (.fusion layer A B C) Q)
    (second : CyclicEventEdge P' (.fusion layer A B C) Q')
    (same : (cyclicSignature P layer).IsRotated (cyclicSignature P' layer)) :
    (cyclicSignature Q layer).IsRotated (cyclicSignature Q' layer) := by
  cases first with
  | fusion _ A B tail Q hA hB hd hs ht ho =>
    cases second with
    | fusion _ _ _ rest Q' hA' hB' hd' hs' ht' ho' =>
      have hc := hs.symm.trans (same.trans hs')
      have hf := (cyclic_filter hc (fun X => X ≠ B)).map
        (fun X => if X = A then A ∪ B else X)
      rw [fusion_rewrite A B tail (hs.nodup_iff.mp (cyclicSignature_nodup P layer)),
        fusion_rewrite A B rest (hs'.nodup_iff.mp (cyclicSignature_nodup P' layer))] at hf
      exact ht.trans (hf.trans ht'.symm)

private theorem transfer_rewrite (packet : Finset (Fin n)) (tail : List (Finset (Fin n)))
    (hnd : (packet :: tail).Nodup) :
    (packet :: tail).filter (fun X => X ≠ packet) = tail := by
  have hn := (List.nodup_cons.mp hnd).1
  have hf : tail.filter (fun X => X ≠ packet) = tail := by
    apply List.filter_eq_self.mpr
    intro X hX
    simp only [decide_eq_true_eq]
    exact fun he => hn (he ▸ hX)
  simpa only [List.filter_cons, show decide (packet ≠ packet) = false from by simp,
    Bool.false_eq_true, if_false] using hf

theorem CyclicEventEdge.transfer_lower_target_unique
    {P P' Q Q' : Placement n} {packet : Finset (Fin n)}
    (first : CyclicEventEdge P (.transfer packet) Q)
    (second : CyclicEventEdge P' (.transfer packet) Q')
    (same : (cyclicSignature P false).IsRotated (cyclicSignature P' false)) :
    (cyclicSignature Q false).IsRotated (cyclicSignature Q' false) := by
  cases first with
  | transfer packet lower upper Q hp hs ht hu hv cap =>
    cases second with
    | transfer _ lower' upper' Q' hp' hs' ht' hu' hv' cap' =>
      have hf := cyclic_filter (hs.symm.trans (same.trans hs')) (fun X => X ≠ packet)
      rw [transfer_rewrite packet lower (hs.nodup_iff.mp (cyclicSignature_nodup P false)),
        transfer_rewrite packet lower' (hs'.nodup_iff.mp (cyclicSignature_nodup P' false))] at hf
      exact ht.trans (hf.trans ht'.symm)

/-- Upper insertion need not be deterministic, but the lower cycle is
determined by the exact event in all three cases. -/
theorem CyclicEventEdge.lower_target_compatible
    {P P' Q Q' : Placement n} {event : EffectiveEvent n}
    (first : CyclicEventEdge P event Q) (second : CyclicEventEdge P' event Q')
    (same : (cyclicSignature P false).IsRotated (cyclicSignature P' false)) :
    (cyclicSignature Q false).IsRotated (cyclicSignature Q' false) := by
  cases event with
  | fusion layer A B C =>
    cases layer with
    | false => exact first.fusion_target_unique second same
    | true =>
      cases first with
      | fusion _ _ _ _ _ _ _ _ _ _ other =>
        cases second with
        | fusion _ _ _ _ _ _ _ _ _ _ other' =>
          exact (other false (by decide)).symm.trans
            (same.trans (other' false (by decide)))
  | transfer packet => exact first.transfer_lower_target_unique second same

theorem CyclicEventEdge.fusion_source
    {P Q : Placement n} {layer : Layer} {A B C : Finset (Fin n)}
    (edge : CyclicEventEdge P (.fusion layer A B C) Q) :
    A.Nonempty ∧ B.Nonempty ∧
      ∃ tail, (cyclicSignature P layer).IsRotated (A :: B :: tail) := by
  cases edge with
  | fusion _ _ _ tail _ ha hb _ hs _ _ => exact ⟨ha, hb, tail, hs⟩

theorem CyclicEventEdge.transfer_packet_mem
    {P Q : Placement n} {packet : Finset (Fin n)}
    (edge : CyclicEventEdge P (.transfer packet) Q) :
    packet.Nonempty ∧ packet ∈ cyclicSignature P false := by
  cases edge with
  | transfer _ _ _ _ hp hs _ _ _ _ => exact ⟨hp, hs.perm.mem_iff.mpr (by simp)⟩

theorem packet_site_of_mem_signature [NeZero n] (P : Placement n) (layer : Layer)
    {packet : Finset (Fin n)} (hm : packet ∈ cyclicSignature P layer) :
    ∃ q : ZMod n, packetAt P layer (zsite q) = packet := by
  rw [signature_eq_occupied_map] at hm
  obtain ⟨q, _, he⟩ := List.mem_map.mp hm
  exact ⟨(q.val : ZMod n), by simpa using he⟩

end RSR2History
