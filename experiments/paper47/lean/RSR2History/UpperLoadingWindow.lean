import RSR2History.UpperLoadingExtraction

/-!
The common integer-lift window is extracted from actual silent steps and
the cyclic order forced by the delayed fusion suffix. Birth representatives
are never identified from their residues alone.
-/
namespace RSR2History
open RSR2.Parametric

private theorem rotated_head_tail {α : Type*} {a : α} {xs ys : List α}
    (hnd : (a :: xs).Nodup) (hrot : (a :: xs).IsRotated (a :: ys)) : xs = ys := by
  obtain ⟨k, hk, he⟩ := List.isRotated_iff_mod.mp hrot
  by_cases hzero : k = 0
  · subst k
    simpa using he
  · by_cases hend : k = xs.length + 1
    · subst k
      simpa using he
    · obtain ⟨j, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hzero
      have hj : j < xs.length := by simp at hk; omega
      have he' : (xs ++ [a]).rotate j = a :: ys := by
        simpa only [List.rotate_cons_succ] using he
      have hh := congrArg List.head? he'
      rw [List.head?_rotate (by simp; omega)] at hh
      have hget : xs[j]? = some a := by
        simpa [List.getElem?_append_left hj] using hh
      exact False.elim ((List.nodup_cons.mp hnd).1
        (List.mem_iff_getElem?.mpr ⟨j, hget⟩))

/-- Before singleton insertions, recover the old cycle by deleting those
same arrivals from the prescribed terminal cycle. -/
theorem singletonTransferPath_source_cycle {n : Nat}
    {P Q : Placement n} {arrived pending : List (Fin n)}
    (path : CyclicEventPath P (singletonTransferLog pending) Q)
    (distinct : (arrived ++ pending).Nodup)
    (terminal : (cyclicSignature Q true).IsRotated
      ((arrived ++ pending).map fun a => ({a} : Finset (Fin n)))) :
    (cyclicSignature P true).IsRotated
      (arrived.map fun a => ({a} : Finset (Fin n))) := by
  induction pending generalizing P arrived with
  | nil =>
      cases path with
      | nil same => simpa using (same true).trans terminal
  | cons a rest ih =>
      cases path with
      | cons edge tail =>
          have hdistinct : ((arrived ++ [a]) ++ rest).Nodup := by
            simpa [List.append_assoc] using distinct
          have hterminal : (cyclicSignature Q true).IsRotated
              (((arrived ++ [a]) ++ rest).map fun x => ({x} : Finset (Fin n))) := by
            simpa [List.append_assoc] using terminal
          have hmid := ih tail hdistinct hterminal
          cases edge with
          | transfer packet lower upper target hp hs ht hu hv cap =>
              have hcycle : (({a} : Finset (Fin n)) :: upper).IsRotated
                  (({a} : Finset (Fin n)) ::
                    arrived.map fun x => ({x} : Finset (Fin n))) := by
                exact (hv.symm.trans hmid).trans
                  (by simpa using (List.isRotated_append
                    (l := arrived.map fun x => ({x} : Finset (Fin n)))
                    (l' := [({a} : Finset (Fin n))])))
              have hnd : (({a} : Finset (Fin n)) :: upper).Nodup :=
                hv.nodup_iff.mp (cyclicSignature_nodup _ true)
              have htail := rotated_head_tail hnd hcycle
              simpa [htail] using hu

/-- Physical sites increase in the literal (unrotated) packet signature. -/
theorem cyclicSignature_sites_strict {n : Nat} (P : Placement n) (layer : Layer) :
    (cyclicSignature P layer).Pairwise
      (fun A B => ∀ a ∈ A, ∀ b ∈ B, (P a).2 < (P b).2) := by
  rw [signature_eq_occupied_map, List.pairwise_map]
  apply List.pairwise_iff_getElem.mpr
  intro i j hi hj hij a ha b hb
  have hsite := occupiedSites_strict P layer
    (show (⟨i, hi⟩ : Fin (occupiedSites P layer).length) < ⟨j, hj⟩ from hij)
  have hpa : P a = (layer, (occupiedSites P layer)[i]) :=
    (mem_packetAt _ _ _ _).mp ha
  have hpb : P b = (layer, (occupiedSites P layer)[j]) :=
    (mem_packetAt _ _ _ _).mp hb
  rw [hpa, hpb]
  exact hsite

theorem upperLiftProjection_append (u v : List Letter) :
    upperLiftProjection (u ++ v) = upperLiftProjection u ++ upperLiftProjection v := by
  induction u with
  | nil => rfl
  | cons a u ih =>
      cases a with
      | p layer => cases layer <;> simp [upperLiftProjection, ih]
      | d layer => cases layer <;> simp [upperLiftProjection, ih]
      | v => simp [upperLiftProjection, ih]

/-- Both anchors refer to packets in the same physical silent step. The
excluded boundary collision would otherwise be an effective upper fusion. -/
theorem SilentStep.upperAnchorWindow {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {letter : Letter} {root last : UpperAnchorState n}
    (step : SilentStep n hn P Q letter)
    (rootNonempty : root.packet.Nonempty) (lastNonempty : last.packet.Nonempty)
    (rootMatches : UpperAnchorMatches n P root)
    (lastMatches : UpperAnchorMatches n P last)
    (window : root.coord ≤ last.coord ∧ last.coord < root.coord + n) :
    (upperAnchorUpdate n root letter).coord ≤ (upperAnchorUpdate n last letter).coord ∧
      (upperAnchorUpdate n last letter).coord < (upperAnchorUpdate n root letter).coord + n := by
  cases letter with
  | p layer => cases layer <;> simp only [upperAnchorUpdate] <;> omega
  | v => exact False.elim (not_silentStep_v n hn P Q step)
  | d layer =>
      cases layer with
      | false => exact window
      | true =>
          have nofusion : ¬ (occupiedAt P true (site0 n (by omega)) ∧
              occupiedAt P true (site1 n hn)) := by
            by_contra h
            have he := step.2
            simp [emittedEvents, h] at he
          have noboundary : ¬ (root.coord % (n : Int) = 1 ∧
              last.coord % (n : Int) = 0) := by
            rintro ⟨hroot, hlast⟩
            obtain ⟨a, ha⟩ := rootNonempty
            obtain ⟨b, hb⟩ := lastNonempty
            obtain ⟨hla, hxa⟩ := rootMatches a ha
            obtain ⟨hlb, hxb⟩ := lastMatches b hb
            apply nofusion
            constructor
            · refine ⟨b, Prod.ext hlb (Fin.ext ?_)⟩
              simp only [site0]
              omega
            · refine ⟨a, Prod.ext hla (Fin.ext ?_)⟩
              simp only [site1]
              omega
          refine ⟨upperDefectLift_mono n window.1, ?_⟩
          change upperDefectLift n last.coord < upperDefectLift n root.coord + n
          by_cases hr : root.coord % (n : Int) = 1
          · have hgap : last.coord < root.coord + n - 1 := by
              by_contra h
              have heq : last.coord = root.coord + n - 1 := by omega
              have hm : last.coord % (n : Int) = 0 := by
                rw [heq]
                simp [Int.sub_emod, hr]
              exact noboundary ⟨hr, hm⟩
            by_cases hl : last.coord % (n : Int) = 1
            · simpa [upperDefectLift, hr, hl] using (show last.coord - 1 < root.coord - 1 + n by omega)
            · simpa [upperDefectLift, hr, hl] using (show last.coord < root.coord - 1 + n by omega)
          · have hlast : upperDefectLift n last.coord ≤ last.coord := by
              unfold upperDefectLift
              split <;> omega
            simpa only [upperDefectLift, if_neg hr] using lt_of_le_of_lt hlast window.2

/-- The common one-period window is preserved by the actual event-free
executor, not by an arbitrary abstract rewrite path. -/
theorem runLogged_empty_upperAnchorWindow {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {word : List Letter} {root last : UpperAnchorState n}
    (run : runLogged n hn P word = some (Q, []))
    (rootNonempty : root.packet.Nonempty) (lastNonempty : last.packet.Nonempty)
    (rootMatches : UpperAnchorMatches n P root)
    (lastMatches : UpperAnchorMatches n P last)
    (window : root.coord ≤ last.coord ∧ last.coord < root.coord + n) :
    (upperAnchorAdvance n (upperLiftProjection word) root).coord ≤
        (upperAnchorAdvance n (upperLiftProjection word) last).coord ∧
      (upperAnchorAdvance n (upperLiftProjection word) last).coord <
        (upperAnchorAdvance n (upperLiftProjection word) root).coord + n := by
  induction word generalizing P root last with
  | nil => simpa [upperAnchorAdvance, upperLiftProjection, upperLiftRun] using window
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at run
      | some R =>
          cases ht : runLogged n hn R rest with
          | none => simp [runLogged, hs, ht] at run
          | some result =>
              obtain ⟨S, events⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ events = [] := by
                simpa [runLogged, hs, ht] using run
              obtain ⟨hfirst, hrest⟩ := List.append_eq_nil_iff.mp he.2
              have silent : SilentStep n hn P R letter := ⟨hs, hfirst⟩
              have hr : runLogged n hn R rest = some (Q, []) := by
                simpa [he.1, hrest] using ht
              have hw := silent.upperAnchorWindow rootNonempty lastNonempty
                rootMatches lastMatches window
              have hroot := upperAnchorUpdate_matches n hn hs rootMatches
              have hlast := upperAnchorUpdate_matches n hn hs lastMatches
              have hne (anchor : UpperAnchorState n) (h : anchor.packet.Nonempty) :
                  (upperAnchorUpdate n anchor letter).packet.Nonempty := by
                cases letter with
                | p layer => cases layer <;> exact h
                | d layer => cases layer <;> exact h
                | v => exact h
              have htail := ih hr (hne root rootNonempty) (hne last lastNonempty)
                hroot hlast hw
              rw [upperLiftProjection_cons letter rest, upperAnchorAdvance_append,
                upperAnchorAdvance_append,
                ← upperAnchorUpdate_eq_advance n root letter,
                ← upperAnchorUpdate_eq_advance n last letter]
              exact htail

/-- Every transfer prepends its true packet to the literal upper signature:
the successful guard gives the empty site-0 head before insertion. -/
theorem EventStep.transfer_upper_signature {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {packet : Finset (Fin n)}
    (event : EventStep n hn P Q .v (.transfer packet)) :
    cyclicSignature Q true = packet :: cyclicSignature P true := by
  obtain ⟨guard, hQ⟩ := (step_v_eq_some_iff n hn P Q).mp event.1
  obtain ⟨post, hslots⟩ := layerSlots_cons n (by omega) P true
  have hempty : packetAt P true (site0 n (by omega)) = ∅ := by
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro a ha
    exact guard.2 ⟨a, (mem_packetAt _ _ _ _).mp ha⟩
  rw [hempty] at hslots
  have hnempty : packet.Nonempty := by
    rw [← event.transfer_source]
    exact (packetAt_nonempty _ _ _).mpr guard.1
  subst Q
  have hlift := layerSlots_lift_upper n (by omega) P packet post
    event.transfer_source hslots
  rw [signature_of_head _ true hlift hnempty]
  simp [cyclicSignature, stripEmpty, hslots]

/-- The arrival lift selected after a vacant receiver is in the root's
current period whenever the literal source order puts the root first. -/
private theorem receiverBirth_in_window {n : Nat} (hn : 1 < n)
    {root last : Int}
    (window : root ≤ last ∧ last < root + n)
    (siteOrder : root % (n : Int) ≤ last % (n : Int))
    (rootAway : root % (n : Int) ≠ 0) :
    root ≤ upperReceiverBirth n last ∧ upperReceiverBirth n last < root + n := by
  have hnpos : 0 < (n : Int) := by omega
  have hr0 := Int.emod_nonneg root (ne_of_gt hnpos)
  have hrn := Int.emod_lt_of_pos root hnpos
  have hs0 := Int.emod_nonneg last (ne_of_gt hnpos)
  have hsn := Int.emod_lt_of_pos last hnpos
  have hd0 : 0 ≤ last - root := by omega
  have hdn : last - root < (n : Int) := by omega
  have hmod : last % (n : Int) =
      (root % (n : Int) + (last - root)) % (n : Int) := by
    conv_lhs => rw [show last = root + (last-root) by omega]
    rw [Int.add_emod, Int.emod_eq_of_lt hd0 hdn]
  have hnowrap : root % (n : Int) + (last - root) < (n : Int) := by
    by_contra h
    have hsum : root % (n : Int) + (last - root) =
        n + (root % (n : Int) + (last - root) - n) := by omega
    rw [hsum] at hmod
    have hdelta0 : 0 ≤ root % (n : Int) + (last - root) - n := by omega
    have hdeltan : root % (n : Int) + (last - root) - n < (n : Int) := by omega
    simp only [Int.add_emod_left, Int.emod_eq_of_lt hdelta0 hdeltan] at hmod
    omega
  rw [Int.emod_eq_of_lt (by omega) hnowrap] at hmod
  unfold upperReceiverBirth
  omega

private theorem finRange_getLast? (n : Nat) (hn : 0 < n) :
    (List.finRange n).getLast? = some ⟨n-1, by omega⟩ := by
  cases n with
  | zero => omega
  | succ n =>
      cases n with
      | zero => simp [List.finRange]
      | succ n =>
          rw [List.finRange_succ, List.getLast?_cons, List.getLast?_map]
          rw [finRange_getLast? (n+1) (by omega)]
          simp

private theorem occupiedSites_eq_finRange_of_length {n : Nat}
    (P : Placement n) (layer : Layer)
    (hlen : (occupiedSites P layer).length = n) :
    occupiedSites P layer = List.finRange n := by
  have hfilter : ((List.finRange n).filter
      (fun q => packetAt P layer q != ∅)).length = (List.finRange n).length := by
    simpa [occupiedSites] using hlen
  unfold occupiedSites
  apply List.filter_eq_self.mpr
  intro q hq
  exact (List.length_filter_eq_length_iff.mp hfilter) q hq

/-- The first ordered fusion fixes the cyclic origin at the first arrival. -/
theorem DelayedUpperLoadingPrefix.stop_packed_signature
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    cyclicSignature cut.stop true =
      (a :: b :: rest).map (fun x => ({x} : Finset (Fin n))) := by
  have hset : (a :: b :: rest).toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  have hcover : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
      Finset.univ := by
    have he : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
        (a :: b :: rest).toFinset := by simp
    exact he.trans hset
  have hterminal : cyclicSignature Q true =
      [({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset] := by
    rw [hcover]
    exact terminal
  have hcycle := cut.stop_cycle hterminal
  have hhead : ∃ tail, cyclicSignature cut.stop true = {a} :: tail := by
    obtain ⟨post, hslots⟩ := layerSlots_cons n (by omega) cut.stop true
    rw [cut.fusion.upperFusion_ports.1] at hslots
    exact ⟨stripEmpty ∅ post,
      signature_of_head cut.stop true hslots (by simp)⟩
  obtain ⟨signatureTail, hsignatureHead⟩ := hhead
  change cyclicSignature cut.stop true =
      ({a} : Finset (Fin n)) :: {b} ::
        rest.map fun x => ({x} : Finset (Fin n))
  have hnd : (({a} : Finset (Fin n)) :: signatureTail).Nodup := by
    rw [← hsignatureHead]
    exact cyclicSignature_nodup cut.stop true
  rw [hsignatureHead] at hcycle
  have htail := rotated_head_tail hnd hcycle
  rw [hsignatureHead]
  exact congrArg (List.cons ({a} : Finset (Fin n))) htail

/-- Every physical upper site, including its singleton identity, is forced
at the actual first-fusion boundary. -/
theorem DelayedUpperLoadingPrefix.stop_packed_sites
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) (q : Fin n) :
    packetAt cut.stop true q = {(a :: b :: rest)[q.val]'(by omega)} := by
  have hsignature := cut.stop_packed_signature hlen hnodup terminal
  have hoccupiedLen : (occupiedSites cut.stop true).length = n := by
    have he := congrArg List.length hsignature
    simpa only [signature_eq_occupied_map, List.length_map, hlen] using he
  rw [signature_eq_occupied_map,
    occupiedSites_eq_finRange_of_length cut.stop true hoccupiedLen] at hsignature
  have he := congrArg (fun xs : List (Finset (Fin n)) => xs[q.val]?) hsignature
  have hq : q.val < (a :: b :: rest).length := by omega
  rw [List.getElem?_map, List.getElem?_map,
    List.getElem?_eq_getElem hq] at he
  simpa using he

/-- The full upper cycle forced by the delayed suffix fills every site; its
last prescribed singleton is therefore literally at site `n-1`. -/
theorem DelayedUpperLoadingPrefix.lastPacket_at_final_site
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    ∃ y, (b :: rest).getLast? = some y ∧
      ∀ x ∈ ({y} : Finset (Fin n)),
        cut.stop x = (true, ⟨n-1, by omega⟩) := by
  have hsignature : cyclicSignature cut.stop true =
      ({a} : Finset (Fin n)) :: {b} ::
        rest.map fun x => ({x} : Finset (Fin n)) :=
    cut.stop_packed_signature hlen hnodup terminal
  have hsignatureLen : (cyclicSignature cut.stop true).length = n := by
    rw [hsignature]
    simpa only [List.length_cons, List.length_map] using hlen
  have hoccupiedLen : (occupiedSites cut.stop true).length = n := by
    simpa only [signature_eq_occupied_map, List.length_map] using hsignatureLen
  have hoccupied := occupiedSites_eq_finRange_of_length cut.stop true hoccupiedLen
  obtain ⟨y, hylog, hyPacket⟩ := cut.births.last_packet (by simp)
  have hlastAtom : rest.getLast?.getD b = y := by
    have h := hylog
    simp only [List.getLast?_cons] at h
    exact Option.some.inj h
  have hmapLast : ((b :: rest).map fun x => ({x} : Finset (Fin n))).getLast? =
      some ({y} : Finset (Fin n)) := by
    rw [List.getLast?_map, hylog]
    rfl
  have htargetLast :
      (({a} : Finset (Fin n)) :: ({b} : Finset (Fin n)) ::
        rest.map fun x => ({x} : Finset (Fin n))).getLast? = some {y} := by
    change (({a} : Finset (Fin n)) ::
      ((b :: rest).map fun x => ({x} : Finset (Fin n)))).getLast? = some {y}
    rw [List.getLast?_cons, hmapLast]
    rfl
  have hsigLast : (cyclicSignature cut.stop true).getLast? = some {y} := by
    rw [hsignature]
    exact htargetLast
  have hsiteLast : packetAt cut.stop true ⟨n-1, by omega⟩ = {y} := by
    rw [signature_eq_occupied_map, hoccupied, List.getLast?_map,
      finRange_getLast? n (by omega)] at hsigLast
    exact Option.some.inj hsigLast
  refine ⟨y, hylog, ?_⟩
  intro x hx
  have hx' : x ∈ packetAt cut.stop true ⟨n-1, by omega⟩ := by
    rw [hsiteLast]
    exact hx
  exact (mem_packetAt _ _ _ _).mp hx'

theorem ActualUpperBirthTrace.runLogged {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last) :
    runLogged n hn P trace.word = some (Q, singletonTransferLog z) := by
  induction trace with
  | done word silent tracked => exact silent
  | cons before silent tracked event nonempty hmatch tail ih =>
      rw [ActualUpperBirthTrace.word, runLogged_append, silent]
      simp only [Option.bind_some]
      rw [show Letter.v :: tail.word = [Letter.v] ++ tail.word from rfl,
        runLogged_append, event.runLogged]
      simpa [singletonTransferLog] using ih

private theorem anchor_residue_min_of_signature_head {n : Nat}
    {P : Placement n} {root last : UpperAnchorState n}
    {tail : List (Finset (Fin n))}
    (head : cyclicSignature P true = root.packet :: tail)
    (rootNonempty : root.packet.Nonempty) (lastNonempty : last.packet.Nonempty)
    (rootMatches : UpperAnchorMatches n P root)
    (lastMatches : UpperAnchorMatches n P last) :
    root.coord % (n : Int) ≤ last.coord % (n : Int) := by
  obtain ⟨a, ha⟩ := rootNonempty
  obtain ⟨b, hb⟩ := lastNonempty
  obtain ⟨hlb, hxb⟩ := lastMatches b hb
  let B := packetAt P true (P b).2
  have hbB : b ∈ B := (mem_packetAt _ _ _ _).mpr (Prod.ext hlb rfl)
  have hmem : B ∈ cyclicSignature P true := by
    rw [signature_eq_occupied_map]
    apply List.mem_map.mpr
    refine ⟨(P b).2, ?_, rfl⟩
    simp only [occupiedSites, List.mem_filter, List.mem_finRange, true_and]
    simpa only [bne_iff_ne] using (Finset.nonempty_iff_ne_empty.mp ⟨b, hbB⟩)
  rw [head] at hmem
  rcases List.mem_cons.mp hmem with heq | htail
  · have hrootb := (rootMatches b (heq ▸ hbB)).2
    omega
  · have hp := cyclicSignature_sites_strict P true
    rw [head] at hp
    have hsites := List.rel_of_pairwise_cons hp htail a ha b hbB
    have hxa := (rootMatches a ha).2
    have hval : ((P a).2.val : Int) < ((P b).2.val : Int) := by exact_mod_cast hsites
    omega

/-- The target cyclic order fixes the actual insertion gap. In particular
the first-arrival packet is the first occupied source site before this `v`. -/
private theorem transfer_source_aligned {n : Nat} {hn : 1 < n}
    {P R Q : Placement n} {a : Fin n} {arrived pending : List (Fin n)}
    (event : EventStep n hn P R .v (.transfer {a}))
    (tail : CyclicEventPath R (singletonTransferLog pending) Q)
    (distinct : ((arrived ++ [a]) ++ pending).Nodup)
    (terminal : (cyclicSignature Q true).IsRotated
      (((arrived ++ [a]) ++ pending).map fun x => ({x} : Finset (Fin n)))) :
    cyclicSignature P true = arrived.map fun x => ({x} : Finset (Fin n)) := by
  have htarget := singletonTransferPath_source_cycle tail distinct terminal
  rw [event.transfer_upper_signature] at htarget
  have haligned : (({a} : Finset (Fin n)) :: cyclicSignature P true).IsRotated
      (({a} : Finset (Fin n)) :: arrived.map fun x => ({x} : Finset (Fin n))) :=
    htarget.trans (by simpa using (List.isRotated_append
      (l := arrived.map fun x => ({x} : Finset (Fin n)))
      (l' := [({a} : Finset (Fin n))])))
  have hnd : (({a} : Finset (Fin n)) :: cyclicSignature P true).Nodup := by
    rw [← event.transfer_upper_signature]
    exact cyclicSignature_nodup R true
  exact rotated_head_tail hnd haligned

/-- The first and latest arrival have lifts in the same one-period window.
The cycle at the end is supplied by the prescribed fusion suffix; at each
earlier birth its restriction determines the actual vacant insertion gap. -/
theorem ActualUpperBirthTrace.common_window {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {pending : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor pending Q birth last)
    (root : UpperAnchorState n) (a : Fin n) (arrived : List (Fin n))
    (rootPacket : root.packet = {a})
    (rootMatches : UpperAnchorMatches n P root)
    (anchorNonempty : anchor.packet.Nonempty)
    (anchorMatches : UpperAnchorMatches n P anchor)
    (window : root.coord ≤ anchor.coord ∧ anchor.coord < root.coord + n)
    (distinct : ((a :: arrived) ++ pending).Nodup)
    (terminal : (cyclicSignature Q true).IsRotated
      (((a :: arrived) ++ pending).map fun x => ({x} : Finset (Fin n)))) :
    (upperAnchorAdvance n (upperLiftProjection trace.word) root).coord ≤ last.coord ∧
      last.coord < (upperAnchorAdvance n (upperLiftProjection trace.word) root).coord + n := by
  have rootNonempty : root.packet.Nonempty := by simp [rootPacket]
  induction trace generalizing root arrived with
  | done word silent tracked =>
      have hlast := runWithUpperAnchor_lift n hn _ _ _ _ _ tracked
      simp only [ActualUpperBirthTrace.word]
      rw [hlast]
      exact runLogged_empty_upperAnchorWindow silent rootNonempty anchorNonempty
        rootMatches anchorMatches window
  | @cons P R S Q anchor atPort last c rest lastBirth before silent tracked
      event nonempty hmatch tail ih =>
      let rootPort := upperAnchorAdvance n (upperLiftProjection before) root
      obtain ⟨physicalRoot, rootRun⟩ := runWithUpperAnchor_of_runLogged n hn silent root
      have hrootPort : physicalRoot = rootPort :=
        runWithUpperAnchor_lift n hn _ _ _ _ _ rootRun
      subst physicalRoot
      have rootMatchesPort := runWithUpperAnchor_matches n hn _ _ _ _ _ rootMatches rootRun
      have anchorMatchesPort := runWithUpperAnchor_matches n hn _ _ _ _ _ hmatch tracked
      have hanchorPort := runWithUpperAnchor_lift n hn _ _ _ _ _ tracked
      have anchorPortNonempty : atPort.packet.Nonempty := by
        rw [hanchorPort]
        simpa [upperAnchorAdvance] using anchorNonempty
      have rootPortNonempty : rootPort.packet.Nonempty := by
        simpa [rootPort, upperAnchorAdvance] using rootNonempty
      have portWindow : rootPort.coord ≤ atPort.coord ∧ atPort.coord < rootPort.coord + n := by
        rw [hanchorPort]
        exact runLogged_empty_upperAnchorWindow silent rootNonempty anchorNonempty
          rootMatches hmatch window
      have path := runLogged_cyclicEventPath n hn tail.word tail.runLogged
      have hdistinct : (((a :: arrived) ++ [c]) ++ rest).Nodup := by
        simpa [List.append_assoc] using distinct
      have hterminal : (cyclicSignature Q true).IsRotated
          ((((a :: arrived) ++ [c]) ++ rest).map fun x => ({x} : Finset (Fin n))) := by
        simpa [List.append_assoc] using terminal
      have haligned := transfer_source_aligned event path hdistinct hterminal
      have hhead : cyclicSignature R true = rootPort.packet ::
          (arrived.map fun x => ({x} : Finset (Fin n))) := by
        simpa [rootPort, upperAnchorAdvance, rootPacket] using haligned
      have siteOrder := anchor_residue_min_of_signature_head hhead rootPortNonempty
        anchorPortNonempty rootMatchesPort anchorMatchesPort
      have rootAway : rootPort.coord % (n : Int) ≠ 0 := by
        have h := (event.upperReceiverBirth_spec rootPortNonempty rootMatchesPort).2.2
        intro hzero
        dsimp [upperReceiverBirth] at h
        omega
      have birthWindow := receiverBirth_in_window hn portWindow siteOrder rootAway
      have rootMatchesAfter : UpperAnchorMatches n S rootPort := by
        exact upperAnchorUpdate_matches n hn event.1 rootMatchesPort
      have bornMatches := event.transfer_target
        (event.upperReceiverBirth_spec anchorPortNonempty anchorMatchesPort).1
      have hrest := ih rootPort (arrived ++ [c])
        (by simpa [rootPort, upperAnchorAdvance] using rootPacket)
        rootMatchesAfter (by simp) bornMatches birthWindow
        (by simpa [List.append_assoc] using hdistinct)
        (by simpa [List.append_assoc] using hterminal)
        rootPortNonempty
      simpa only [ActualUpperBirthTrace.word, upperLiftProjection_append,
        upperAnchorAdvance_append, upperLiftProjection, rootPort] using hrest

private theorem residue_window_unique {n : Nat} (hn : 1 < n)
    {root last : Int}
    (root_periodic : root % (n : Int) = 0)
    (last_residue : last % (n : Int) = (n : Int) - 1)
    (window : root ≤ last ∧ last < root + n) :
    last = root + (n : Int) - 1 := by
  have hnpos : 0 < (n : Int) := by omega
  have hdelta0 : 0 ≤ last - root := by omega
  have hdeltan : last - root < (n : Int) := by omega
  have hmod : last % (n : Int) = (last - root) % (n : Int) := by
    calc
      last % (n : Int) = (root + (last - root)) % (n : Int) := by
        congr 1
        omega
      _ = (root % (n : Int) + (last - root) % (n : Int)) % (n : Int) :=
        Int.add_emod _ _ _
      _ = (last - root) % (n : Int) := by simp [root_periodic]
  rw [Int.emod_eq_of_lt hdelta0 hdeltan] at hmod
  omega

/-- The prescribed delayed-chain history forces the last arriving singleton
to be exactly one period minus one site ahead of the first anchor. This is
derived from its real pre-fusion placement, not supplied as barrier data. -/
theorem DelayedUpperLoadingPrefix.packedCycle_of_full_terminal
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    cut.lastAnchor.coord = cut.anchorStop.coord + (n : Int) - 1 := by
  have hset : (a :: b :: rest).toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  have hcover : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
      Finset.univ := by
    have heq : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
        (a :: b :: rest).toFinset := by simp
    exact heq.trans hset
  have hterminal : cyclicSignature Q true =
      [({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset] := by
    rw [hcover]
    exact terminal
  have hcycle := cut.stop_cycle hterminal
  have hcycle' : (cyclicSignature cut.stop true).IsRotated
      (((a :: []) ++ (b :: rest)).map fun x => ({x} : Finset (Fin n))) := by
    simpa using hcycle
  have hstart : UpperAnchorMatches n cut.start ⟨{a}, 0, 0⟩ :=
    cut.transfer.transfer_target (by simp)
  have hwindow := cut.births.common_window
      (⟨{a}, 0, 0⟩ : UpperAnchorState n) a [] rfl hstart
      (by simp) hstart ⟨by omega, by simp; omega⟩
      (by simpa using hnodup) hcycle'
  rw [cut.births_word] at hwindow
  have hanchorRun := runWithUpperAnchor_lift n hn _ _ _ _ _ cut.anchorRun
  rw [← hanchorRun] at hwindow
  obtain ⟨y, hylog, hsite⟩ := cut.lastPacket_at_final_site hlen hnodup terminal
  obtain ⟨y', hylog', hpacket⟩ := cut.births.last_packet (by simp)
  have hyy : y = y' := Option.some.inj (hylog.symm.trans hylog')
  rw [← hyy] at hpacket
  have hmatch := cut.births.final_matches hstart
  have hposition := hsite y (by simp)
  have hresidue : cut.lastAnchor.coord % (n : Int) = (n : Int) - 1 := by
    have hm := (hmatch y (by rw [hpacket]; simp)).2
    rw [hposition] at hm
    have hresNat : cut.lastAnchor.coord % (n : Int) = ((n - 1 : Nat) : Int) := by
      simpa [hposition] using hm
    have hn1 : 1 ≤ n := by omega
    simpa [Nat.cast_sub hn1] using hresNat
  obtain ⟨q, hq⟩ := cut.anchor_periodic
  have hrootResidue : cut.anchorStop.coord % (n : Int) = 0 := by
    rw [hq]
    simp
  exact residue_window_unique hn hrootResidue hresidue hwindow

/-- Package the birth chain and the packed-cycle equation into the physical
barrier interface, with every field obtained from the actual loading cut. -/
theorem DelayedUpperLoadingPrefix.barrierCertificate_exists
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    ∃ cert : UpperLoadingBarrierCertificate n hn,
      cert.word = cut.word ∧ cert.start = cut.start ∧ cert.stop = cut.stop ∧
        cert.anchorStop = cut.anchorStop := by
  have hstart : UpperAnchorMatches n cut.start ⟨{a}, 0, 0⟩ :=
    cut.transfer.transfer_target (by simp)
  have hlastMatches := cut.births.final_matches hstart
  have hstopMatches := runWithUpperAnchor_matches n hn _ _ _ _ _ hstart cut.anchorRun
  have hlastBirth := cut.births.birth_le_final (by simp)
  have hpacked := cut.packedCycle_of_full_terminal hlen hnodup terminal
  obtain ⟨arrivals⟩ := cut.arrivals hlen
  refine ⟨{
    word := cut.word
    start := cut.start
    stop := cut.stop
    anchorPacket := {a}
    lastPacket := cut.lastAnchor.packet
    lastBirth := cut.lastBirth
    lastLift := cut.lastAnchor.coord
    anchorStart := ⟨{a}, 0, 0⟩
    anchorStop := cut.anchorStop
    anchorStartsAtZero := rfl
    anchorStartsWithoutSlides := rfl
    anchorNonempty := by simp
    lastPacketNonempty := cut.births.final_packet_nonempty (by simp)
    anchorStartMatches := hstart
    anchorExecution := cut.anchorRun
    anchorStopMatches := hstopMatches
    lastPacketAtLift := hlastMatches
    arrivals := arrivals
    lastBirth_le_lastLift := hlastBirth
    anchorStopPeriodic := cut.anchor_periodic
    packedCycle := by omega
  }, rfl, rfl, rfl, rfl⟩

/-- Extract the upper loading barrier from the *specified actual event log*.
The returned word is the original interval between the first singleton
transfer and the first upper fusion. -/
theorem upperLoadingBarrierCertificate_of_delayedChain_run
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hrun : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    ∃ cut : DelayedUpperLoadingPrefix n hn a b rest word Q,
      ∃ cert : UpperLoadingBarrierCertificate n hn,
        cert.word = cut.word ∧
        cert.start = cut.start ∧ cert.stop = cut.stop ∧
        cert.anchorStop = cut.anchorStop ∧
        n * (n - 1) + cert.anchorStop.slides ≤ cert.word.count (.p true) ∧
        word = cut.beforeWord ++ .v :: (cert.word ++ .d true :: cut.tail) := by
  obtain ⟨cut⟩ := delayedUpperLoadingPrefix_of_runLogged n hn a b rest hrun
  obtain ⟨cert, hword, hstart, hstop, hanchor⟩ :=
    cut.barrierCertificate_exists hlen hnodup terminal
  exact ⟨cut, cert, hword, hstart, hstop, hanchor,
    cert.rotations_lower_bound, by rw [hword]; exact cut.word_eq⟩

/-- Counts in the actual contiguous loading segment are bounded by counts
in the complete competing raw word. -/
theorem DelayedUpperLoadingPrefix.count_le_raw
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q) (letter : Letter) :
    cut.word.count letter ≤ word.count letter := by
  conv_rhs => rw [cut.word_eq]
  simp only [List.count_append, List.count_cons]
  omega

/-- The slide-sensitive bound on the actual loading interval itself. This
keeps its cost separate from the subsequent all-R fusion suffix. -/
theorem DelayedUpperLoadingPrefix.loading_rotations_lower_bound
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    n * (n - 1) + cut.anchorStop.slides ≤ cut.word.count (.p true) := by
  obtain ⟨cert, hword, _, _, hanchor⟩ :=
    cut.barrierCertificate_exists hlen hnodup terminal
  have hb := cert.rotations_lower_bound
  rw [hword, hanchor] at hb
  exact hb

/-- Slide-sensitive raw-word bound; `slides` counts hits on the first arrival
only during the actual loading interval specified by `cut`. -/
theorem DelayedUpperLoadingPrefix.raw_rotations_lower_bound
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    n * (n - 1) + cut.anchorStop.slides ≤ word.count (.p true) :=
  (cut.loading_rotations_lower_bound hlen hnodup terminal).trans (cut.count_le_raw _)

theorem delayedChain_raw_rotations_lower_bound_with_slides
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hrun : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    ∃ cut : DelayedUpperLoadingPrefix n hn a b rest word Q,
      n * (n - 1) + cut.anchorStop.slides ≤ word.count (.p true) := by
  obtain ⟨cut⟩ := delayedUpperLoadingPrefix_of_runLogged n hn a b rest hrun
  exact ⟨cut, cut.raw_rotations_lower_bound hlen hnodup terminal⟩

/-- No geometric certificate is a premise of this raw-execution bound. -/
theorem delayedChain_raw_rotations_lower_bound
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hrun : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    n * (n - 1) ≤ word.count (.p true) := by
  obtain ⟨cut, hbound⟩ :=
    delayedChain_raw_rotations_lower_bound_with_slides hlen hnodup terminal hrun
  omega

end RSR2History
