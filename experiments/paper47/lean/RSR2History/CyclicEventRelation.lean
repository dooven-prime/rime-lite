import RSR2History.SignatureFrames

/-!
H2-A's cyclic event relation is defined by literal packet-list rewrites,
independently of physical reachability. Placements serve only as well-typed
representatives: their atom assignment enforces disjointness and coverage.
The relation forgets all sites and is invariant under SameCyclicSignatures.
-/

namespace RSR2History

open RSR2.Parametric

inductive CyclicEventEdge (P : Placement n) : EffectiveEvent n → Placement n → Prop
  | fusion (layer : Layer) (left right : Finset (Fin n))
      (tail : List (Finset (Fin n))) (Q : Placement n)
      (left_nonempty : left.Nonempty) (right_nonempty : right.Nonempty)
      (parents_disjoint : Disjoint left right)
      (source : (cyclicSignature P layer).IsRotated (left :: right :: tail))
      (target : (cyclicSignature Q layer).IsRotated ((left ∪ right) :: tail))
      (other : ∀ l, l ≠ layer →
        (cyclicSignature P l).IsRotated (cyclicSignature Q l)) :
      CyclicEventEdge P (.fusion layer left right (left ∪ right)) Q
  | transfer (packet : Finset (Fin n)) (lower upper : List (Finset (Fin n)))
      (Q : Placement n) (packet_nonempty : packet.Nonempty)
      (lower_source : (cyclicSignature P false).IsRotated (packet :: lower))
      (lower_target : (cyclicSignature Q false).IsRotated lower)
      (upper_source : (cyclicSignature P true).IsRotated upper)
      (upper_target : (cyclicSignature Q true).IsRotated (packet :: upper))
      (upper_capacity : upper.length < n) :
      CyclicEventEdge P (.transfer packet) Q

theorem CyclicEventEdge.congr {P Q P' Q' : Placement n} {event : EffectiveEvent n}
    (h : CyclicEventEdge P event Q)
    (hP : SameCyclicSignatures P' P) (hQ : SameCyclicSignatures Q' Q) :
    CyclicEventEdge P' event Q' := by
  cases h with
  | fusion layer left right tail Q hL hR hd hs ht ho =>
      exact .fusion layer left right tail Q' hL hR hd ((hP layer).trans hs)
        ((hQ layer).trans ht) (fun l hne => ((hP l).trans (ho l hne)).trans (hQ l).symm)
  | transfer packet lower upper Q hp hls hlt hus hut hc =>
      exact .transfer packet lower upper Q' hp ((hP false).trans hls)
        ((hQ false).trans hlt) ((hP true).trans hus) ((hQ true).trans hut) hc

/-- Fusion cannot be admitted in an empty or singleton cyclic layer. -/
theorem CyclicEventEdge.fusion_rank_ge_two {P Q : Placement n} {layer : Layer}
    {left right result : Finset (Fin n)}
    (h : CyclicEventEdge P (.fusion layer left right result) Q) :
    2 ≤ (cyclicSignature P layer).length := by
  cases h with
  | fusion layer left right tail Q hL hR hd hs ht ho =>
      have hlen := hs.perm.length_eq
      simp only [List.length_cons] at hlen
      omega

/-- A full receiver cycle admits no transfer. -/
theorem CyclicEventEdge.transfer_receiver_not_full {P Q : Placement n}
    {packet : Finset (Fin n)} (h : CyclicEventEdge P (.transfer packet) Q) :
    (cyclicSignature P true).length < n := by
  cases h with
  | transfer packet lower upper Q hp hls hlt hus hut hc =>
      rw [hus.perm.length_eq]
      exact hc

/-- Distinct nonempty parents are required, including in a two-packet cycle. -/
theorem CyclicEventEdge.fusion_parents_ne {P Q : Placement n} {layer : Layer}
    {left right result : Finset (Fin n)}
    (h : CyclicEventEdge P (.fusion layer left right result) Q) : left ≠ right := by
  cases h with
  | fusion layer left right tail Q hL hR hd hs ht ho =>
      intro he
      obtain ⟨a, ha⟩ := hL
      exact Finset.disjoint_left.mp hd ha (he ▸ ha)

/-- Distinct physical slots cannot share an atom. -/
theorem packetAt_disjoint (P : Placement n) (layer : Layer) (q r : Fin n)
    (hqr : q ≠ r) : Disjoint (packetAt P layer q) (packetAt P layer r) := by
  apply Finset.disjoint_left.mpr
  intro a ha hb
  exact hqr (congrArg Prod.snd ((mem_packetAt _ _ _ _).mp ha |>.symm.trans
    ((mem_packetAt _ _ _ _).mp hb)))

/-- Nonempty head packets survive empty-slot filtering literally. -/
theorem signature_of_head (P : Placement n) (layer : Layer)
    {a : Finset (Fin n)} {post : List (Finset (Fin n))}
    (hslots : layerSlots P layer = a :: post) (ha : a.Nonempty) :
    cyclicSignature P layer = a :: stripEmpty ∅ post := by
  simp [cyclicSignature, stripEmpty, hslots, ha.ne_empty]

theorem signature_of_two (P : Placement n) (layer : Layer)
    {a b : Finset (Fin n)} {post : List (Finset (Fin n))}
    (hslots : layerSlots P layer = a :: b :: post) (ha : a.Nonempty) (hb : b.Nonempty) :
    cyclicSignature P layer = a :: b :: stripEmpty ∅ post := by
  simp [cyclicSignature, stripEmpty, hslots, ha.ne_empty, hb.ne_empty]

/-- One real observable letter has exactly the declared cyclic rewrite. -/
theorem EventStep.cyclicEventEdge {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {letter : Letter} {event : EffectiveEvent n}
    (h : EventStep n hn P Q letter event) : CyclicEventEdge P event Q := by
  classical
  cases letter with
  | p layer =>
      have he := h.2
      simp [emittedEvents] at he
  | d layer =>
      have hbusy : occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn) := by
        by_contra hb
        have := h.2
        simp [emittedEvents, hb] at this
      have he : event = .fusion layer (packetAt P layer (site0 n (by omega)))
          (packetAt P layer (site1 n hn))
          (packetAt P layer (site0 n (by omega)) ∪ packetAt P layer (site1 n hn)) := by
        simpa [emittedEvents, hbusy] using h.2.symm
      subst event
      have hQ : Q = collapse n hn P layer := by simpa [step_d] using h.1.symm
      subst Q
      have hL := (packetAt_nonempty P layer (site0 n (by omega))).mpr hbusy.1
      have hR := (packetAt_nonempty P layer (site1 n hn)).mpr hbusy.2
      obtain ⟨post, hslots⟩ := layerSlots_cons_two n hn P layer
      have hsig := signature_of_two P layer hslots hL hR
      have hafter := layerSlots_collapse_head n hn P layer _ _ post hslots
      refine .fusion layer _ _ (stripEmpty ∅ post) _ hL hR
        (packetAt_disjoint P layer _ _ (by intro he; have := congrArg Fin.val he; simp [site0, site1] at this))
        (hsig ▸ .refl _) ?_ ?_
      · have hU : (packetAt P layer (site0 n (by omega)) ∪
            packetAt P layer (site1 n hn)).Nonempty := hL.mono Finset.subset_union_left
        have hs := signature_of_head (collapse n hn P layer) layer hafter hU
        simpa [stripEmpty] using (hs ▸ List.IsRotated.refl
          (cyclicSignature (collapse n hn P layer) layer))
      · intro other hne
        have ho := layerSlots_collapse_other n hn P layer other hne
        change (stripEmpty ∅ (layerSlots P other)).IsRotated
          (stripEmpty ∅ (layerSlots (collapse n hn P layer) other))
        rw [ho]
  | v =>
      obtain ⟨hguard, hQ⟩ := (step_v_eq_some_iff n hn P Q).mp h.1
      have he : event = .transfer (packetAt P false (site0 n (by omega))) := by
        simpa [emittedEvents] using h.2.symm
      subst event
      subst Q
      obtain ⟨lo, hlo⟩ := layerSlots_cons n (by omega) P false
      obtain ⟨up, hup⟩ := layerSlots_cons n (by omega) P true
      have hL := (packetAt_nonempty P false (site0 n (by omega))).mpr hguard.1
      have hU : packetAt P true (site0 n (by omega)) = ∅ := by
        exact Finset.not_nonempty_iff_eq_empty.mp
          (fun hh => hguard.2 ((packetAt_nonempty _ _ _).mp hh))
      rw [hU] at hup
      refine .transfer _ (stripEmpty ∅ lo) (stripEmpty ∅ up) _ hL ?_ ?_ ?_ ?_ ?_
      · rw [signature_of_head P false hlo hL]
      · have hs := layerSlots_lift_lower n (by omega) P _ lo hlo
        simpa [cyclicSignature, stripEmpty, hs] using
          List.IsRotated.refl (stripEmpty (∅ : Finset (Fin n)) lo)
      · simpa [cyclicSignature, stripEmpty, hup] using
          List.IsRotated.refl (stripEmpty (∅ : Finset (Fin n)) up)
      · have hs := layerSlots_lift_upper n (by omega) P _ up rfl hup
        rw [signature_of_head _ true hs hL]
      · have hlen := congrArg List.length hup
        simp only [layerSlots_length, List.length_cons] at hlen
        have hh := List.length_filter_le (fun a : Finset (Fin n) => a != ∅) up
        change (up.filter _).length < n
        omega

end RSR2History
