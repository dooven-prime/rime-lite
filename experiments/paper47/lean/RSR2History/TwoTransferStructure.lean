import RSR2History.SingleBlockStrictGaps

/-! The two-transfer split is extracted from one actual event trace. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer
variable {n : Nat}

theorem runLogged_upper_packet_balance (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {H : List (EffectiveEvent n)}
    (hr : runLogged n hn P word = some (Q, H)) :
    upperPacketCount Q + logLayerFusionCount true H =
      upperPacketCount P + logTransferCount H := by
  have hl := runLogged_lower_packet_balance n hn word hr
  have ht := (runLogged_resource_balance n hn word hr).1
  have hs := logFusionCount_layer_split H
  unfold totalPacketCount at ht
  omega

theorem CyclicEventEdge.upper_nonempty {P Q : Placement n} {event : EffectiveEvent n}
    (edge : CyclicEventEdge P event Q)
    (hp : 0 < (cyclicSignature P true).length) :
    0 < (cyclicSignature Q true).length := by
  cases edge with
  | fusion layer A B tail Q ha hb hd hs ht ho =>
      cases layer with
      | false => exact (ho true (by decide)).perm.length_eq ▸ hp
      | true => have hl := ht.perm.length_eq; simp only [List.length_cons] at hl; omega
  | transfer B lower upper Q hb hls hlt hus hut hc =>
      have hl := hut.perm.length_eq
      simp only [List.length_cons] at hl
      omega

theorem CyclicEventPath.upper_nonempty {P Q : Placement n} {H : List (EffectiveEvent n)}
    (path : CyclicEventPath P H Q) (hp : 0 < (cyclicSignature P true).length) :
    0 < (cyclicSignature Q true).length := by
  induction path with
  | nil same => exact (same true).perm.length_eq ▸ hp
  | cons edge tail ih => exact ih (edge.upper_nonempty hp)

theorem lower_count_zero_of_mass_zero (P : Placement n) (hm : lowerAtomMass P = 0) :
    lowerPacketCount P = 0 := by
  classical
  have hsum : ∑ q : Fin n, (packetAt P false q).card = 0 := by
    rwa [← lowerAtomMass_eq_sum_packet_card]
  have hempty (q : Fin n) : packetAt P false q = ∅ :=
    Finset.card_eq_zero.mp ((Finset.sum_eq_zero_iff.mp hsum) q (by simp))
  have hnot (q : Fin n) : ¬ occupiedAt P false q := by
    rw [← packetAt_nonempty, hempty]
    simp
  simp [lowerPacketCount, hnot]

/-- No-transfer suffixes cannot conceal lower fusions if the final lower
layer is empty: lower atom mass cannot disappear by a fusion. -/
theorem runLogged_noTransfer_to_allUpper (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {H : List (EffectiveEvent n)}
    (hr : runLogged n hn P word = some (Q, H))
    (ht : logTransferCount H = 0) (hq : lowerAtomMass Q = 0) :
    lowerPacketCount P = 0 ∧ logLayerFusionCount false H = 0 := by
  have hm := (runLogged_resource_balance n hn word hr).2.1
  have hz := logTransferMass_eq_zero_of_count_zero H ht
  have hp : lowerAtomMass P = 0 := by omega
  have hl := runLogged_lower_packet_balance n hn word hr
  have hp0 := lower_count_zero_of_mass_zero P hp
  have hq0 := lower_count_zero_of_mass_zero Q hq
  exact ⟨hp0, by omega⟩

private theorem first_log_transfer (H : List (EffectiveEvent n))
    (ht : 0 < logTransferCount H) :
    ∃ before B after, H = before ++ .transfer B :: after ∧ logTransferCount before = 0 := by
  induction H with
  | nil => simp [logTransferCount] at ht
  | cons event rest ih =>
      cases event with
      | transfer B => exact ⟨[], B, rest, rfl, rfl⟩
      | fusion layer A B C =>
          obtain ⟨before, packet, after, he, hz⟩ := ih (by simpa [logTransferCount] using ht)
          exact ⟨.fusion layer A B C :: before, packet, after,
            by simp [he], by simpa [logTransferCount] using hz⟩

theorem log_two_transfers_split (H : List (EffectiveEvent n)) (ht : logTransferCount H = 2) :
    ∃ L0 B1 L1 B2 L2,
      H = L0 ++ .transfer B1 :: (L1 ++ .transfer B2 :: L2) ∧
      logTransferCount L0 = 0 ∧ logTransferCount L1 = 0 ∧ logTransferCount L2 = 0 := by
  obtain ⟨L0, B1, rest, he, hz⟩ := first_log_transfer H (by omega)
  have hr : logTransferCount rest = 1 := by
    rw [he, logTransferCount_append] at ht
    change logTransferCount L0 + (1 + logTransferCount rest) = 2 at ht
    omega
  obtain ⟨L1, B2, L2, he', hz'⟩ := first_log_transfer rest (by omega)
  have hz2 : logTransferCount L2 = 0 := by
    rw [he', logTransferCount_append] at hr
    change logTransferCount L1 + (1 + logTransferCount L2) = 1 at hr
    omega
  exact ⟨L0, B1, L1, B2, L2, by simp [he, he'], hz, hz', hz2⟩

theorem CyclicEventPath.lower_fusions_upper_same
    {P Q : Placement n} {H : List (EffectiveEvent n)}
    (path : CyclicEventPath P H Q)
    (hlow : ∀ e ∈ H, ∃ A B C, e = .fusion false A B C) :
    (cyclicSignature P true).IsRotated (cyclicSignature Q true) := by
  induction path with
  | nil same => exact same true
  | @cons P S Q event events edge tail ih =>
      obtain ⟨A, B, C, he⟩ := hlow event (by simp)
      subst event
      cases edge with
      | fusion _ _ _ _ _ _ _ _ _ _ other =>
          exact (other true (by decide)).trans (ih (by
            intro e he
            exact hlow e (by simp [he])))

theorem CyclicEventEdge.transfer_upper_from_empty
    {P Q : Placement n} {B : Finset (Fin n)} (edge : CyclicEventEdge P (.transfer B) Q)
    (hu : cyclicSignature P true = []) : cyclicSignature Q true = [B] := by
  cases edge with
  | transfer B lower upper Q hb hls hlt hus hut hc =>
      rw [hu] at hus
      have hz : upper = [] := List.isRotated_nil_iff.mp hus.symm
      exact List.isRotated_singleton_iff.mp (by simpa [hz] using hut)

theorem CyclicEventEdge.transfer_upper_from_singleton
    {P Q : Placement n} {B1 B2 : Finset (Fin n)}
    (edge : CyclicEventEdge P (.transfer B2) Q)
    (hu : cyclicSignature P true = [B1]) :
    (cyclicSignature Q true).IsRotated [B2, B1] := by
  cases edge with
  | transfer B lower upper Q hb hls hlt hus hut hc =>
      have hz : upper = [B1] := List.isRotated_singleton_iff.mp (hus.symm.trans (hu ▸ .refl _))
      simpa [hz] using hut

private theorem upper_singleton_log (H : List (EffectiveEvent n))
    (ht : logTransferCount H = 0) (hl : logLayerFusionCount false H = 0)
    (hu : logLayerFusionCount true H = 1) :
    ∃ A B C, H = [.fusion true A B C] := by
  have hs := logFusionCount_layer_split H
  have hc := log_event_count_split H
  have hlen : H.length = 1 := by omega
  obtain ⟨event, rfl⟩ := List.length_eq_one_iff.mp hlen
  cases event with
  | transfer B => simp [logTransferCount] at ht
  | fusion layer A B C =>
      cases layer with
      | false => simp [logLayerFusionCount] at hl
      | true => exact ⟨A, B, C, rfl⟩

private theorem constant_upper_signature_member [NeZero n] (q : Fin n)
    {B : Finset (Fin n)} (hm : B ∈ cyclicSignature (fun _ => (true, q)) true) :
    B = Finset.univ := by
  obtain ⟨r, hr⟩ := packet_site_of_mem_signature (fun _ => (true, q)) true hm
  obtain ⟨a, ha⟩ := cyclicSignature_packet_nonempty _ _ hm
  have hq : q = zsite r := congrArg Prod.snd
    ((mem_packetAt (fun _ => (true, q)) true (zsite r) a).mp (by rwa [hr]))
  rw [← hr]
  ext a
  simp [packetAt, hq]

/-- A classified log with its event-path witnesses inherited from the same
actual trace. The final ordered parents are not determined by arrival order. -/
structure TwoTransferNormalForm (n : Nat) (Q : Placement n) (H : List (EffectiveEvent n)) where
  L0 : List (EffectiveEvent n)
  L1 : List (EffectiveEvent n)
  B1 : Finset (Fin n)
  B2 : Finset (Fin n)
  left : Finset (Fin n)
  right : Finset (Fin n)
  P0 : Placement n
  P1 : Placement n
  P2 : Placement n
  P3 : Placement n
  log_eq : H = L0 ++ .transfer B1 :: (L1 ++ [.transfer B2, .fusion true left right Finset.univ])
  lower0 : ∀ e ∈ L0, ∃ A B C, e = .fusion false A B C
  lower1 : ∀ e ∈ L1, ∃ A B C, e = .fusion false A B C
  fusion_count : L0.length + L1.length = n-2
  first_nonempty : B1.Nonempty
  second_nonempty : B2.Nonempty
  disjoint : Disjoint B1 B2
  covers : B1 ∪ B2 = Finset.univ
  ordered : (left = B1 ∧ right = B2) ∨ (left = B2 ∧ right = B1)
  initial_path : CyclicEventPath (seed n) L0 P0
  first_transfer : CyclicEventEdge P0 (.transfer B1) P1
  middle_path : CyclicEventPath P1 L1 P2
  second_transfer : CyclicEventEdge P2 (.transfer B2) P3
  final_path : CyclicEventPath P3 [.fusion true left right Finset.univ] Q
  first_receiver_empty : cyclicSignature P0 true = []
  first_upper : cyclicSignature P1 true = [B1]
  second_upper : cyclicSignature P2 true = [B1]
  second_lower : cyclicSignature P2 false = [B2]

/-- Every actual two-transfer full-packet history has this exact form.
No clean-prefix or transfer-first premise is imposed. -/
theorem singleBlock_twoTransfer_normalForm [NeZero n] (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n hn (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) : Nonempty (TwoTransferNormalForm n Q H) := by
  classical
  obtain ⟨_, ⟨q, hQ⟩, hF0, hF1⟩ :=
    singleBlock_positiveTransfer_shape n hn word hr hblocks (by omega)
  have hQmass : lowerAtomMass Q = 0 := by rw [hQ, constant_lowerAtomMass]; rfl
  obtain ⟨L0, B1, L1, B2, L2, hlog, h0, h1, h2⟩ := log_two_transfers_split H ht
  obtain ⟨trace, _⟩ := actualEventTrace_of_runLogged n hn word hr
  rw [hlog] at trace
  obtain ⟨S0, early, after0⟩ := trace.split (early := L0)
  let v1 := after0.first
  obtain ⟨S1, middle, after1⟩ := v1.rest.split (early := L1)
  let v2 := after1.first
  have hp : runLogged n hn (seed n) (early.word ++ v1.before) =
      some (v1.beforeState, L0) := by
    simp [runLogged_append, early.runLogged, v1.silent]
  have hm : runLogged n hn v1.afterState (middle.word ++ v2.before) =
      some (v2.beforeState, L1) := by
    simp [runLogged_append, middle.runLogged, v2.silent]
  have he1 := v1.eventStep.cyclicEventEdge
  have he2 := v2.eventStep.cyclicEventEdge
  have hub0 := runLogged_upper_packet_balance hn _ hp
  have hseed : upperPacketCount (seed n) = 0 := by
    rw [← layerRank_upper]
    change (cyclicSignature (seed n) true).length = 0
    rw [cyclicSignature_seed_upper]
    rfl
  have hupper0 : logLayerFusionCount true L0 = 0 := by omega
  have hs0 : cyclicSignature v1.beforeState true = [] := by
    apply List.length_eq_zero_iff.mp
    change layerRank v1.beforeState true = 0
    rw [layerRank_upper]
    omega
  have hs1 := he1.transfer_upper_from_empty hs0
  have hcount1 : upperPacketCount v1.afterState = 1 := by
    rw [← layerRank_upper]
    simp only [layerRank, hs1, List.length_singleton]
  have hmpath := runLogged_cyclicEventPath n hn _ hm
  have hmpos : 0 < upperPacketCount v2.beforeState := by
    rw [← layerRank_upper]
    exact hmpath.upper_nonempty (by simp only [hs1, List.length_singleton]; omega)
  have hub1 := runLogged_upper_packet_balance hn _ hm
  have hupper1 : logLayerFusionCount true L1 = 0 := by omega
  have hlo0 := lowerFusionOnly_of_counts L0 h0 hupper0
  have hlo1 := lowerFusionOnly_of_counts L1 h1 hupper1
  have hs2 : cyclicSignature v2.beforeState true = [B1] :=
    List.isRotated_singleton_iff.mp
      (hmpath.lower_fusions_upper_same hlo1 |>.symm.trans (hs1 ▸ .refl _))
  have hfinal := v2.rest.runLogged
  have hlowtail := runLogged_noTransfer_to_allUpper hn _ hfinal h2 hQmass
  have hupper2 : logLayerFusionCount true L2 = 1 := by
    have hh : logLayerFusionCount true H = logLayerFusionCount true L0 +
        logLayerFusionCount true L1 + logLayerFusionCount true L2 := by
      simp [hlog, logLayerFusionCount, Nat.add_assoc]
    rw [hh] at hF1
    omega
  obtain ⟨A, B, C, hL2⟩ := upper_singleton_log L2 h2 hlowtail.2 hupper2
  have hlower2 : cyclicSignature v2.beforeState false = [B2] := by
    have hafter : cyclicSignature v2.afterState false = [] := by
      apply List.length_eq_zero_iff.mp
      change layerRank v2.afterState false = 0
      rw [layerRank_lower]
      exact hlowtail.1
    cases he2 with
    | transfer _ lower upper _ hb hls hlt hus hut hc =>
        have hz : lower = [] := List.isRotated_nil_iff.mp (hlt.symm.trans (hafter ▸ .refl _))
        exact List.isRotated_singleton_iff.mp (by simpa [hz] using hls)
  have huAfter2 := he2.transfer_upper_from_singleton hs2
  have finalTrace : ActualEventTrace n hn v2.afterState [.fusion true A B C] Q :=
    hL2 ▸ v2.rest
  let final := finalTrace.first
  have hfedge := final.eventStep.cyclicEventEdge
  have hsfinal : (cyclicSignature final.beforeState true).IsRotated [B2, B1] :=
    ((runLogged_empty_signatures n hn _ final.silent) true).symm.trans huAfter2
  have hparents : (A = B1 ∧ B = B2) ∨ (A = B2 ∧ B = B1) := by
    obtain ⟨_, _, tail, hs⟩ := hfedge.fusion_source
    have htlen := hs.perm.length_eq
    have hflen := hsfinal.perm.length_eq
    have hz : tail = [] := by
      apply List.length_eq_zero_iff.mp
      simp only [List.length_cons, List.length_nil] at htlen hflen
      omega
    rw [hz] at hs
    have hp : [A, B].Perm [B2, B1] := hs.perm.symm.trans hsfinal.perm
    rcases List.perm_pair.mp hp with he | he
    · right
      exact ⟨(List.cons.inj he).1, (List.cons.inj (List.cons.inj he).2).1⟩
    · left
      exact ⟨(List.cons.inj he).1, (List.cons.inj (List.cons.inj he).2).1⟩
  have hC : C = Finset.univ := by
    have hmem : C ∈ cyclicSignature final.afterState true := by
      cases hfedge with
      | fusion _ _ _ tail _ ha hb hd hs ht ho =>
          exact ht.perm.mem_iff.mpr (by simp)
    have hsame := runLogged_empty_signatures n hn _ final.rest.runLogged
    have hmQ := (hsame true).mem_iff.mp hmem
    rw [hQ] at hmQ
    exact constant_upper_signature_member q hmQ
  have hdis : Disjoint A B := by cases hfedge; assumption
  have hres : A ∪ B = Finset.univ := by
    have hc : C = A ∪ B := by cases hfedge; rfl
    exact hc.symm.trans hC
  have hdis12 : Disjoint B1 B2 := by
    rcases hparents with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · exact hdis
    · exact hdis.symm
  have hcover : B1 ∪ B2 = Finset.univ := by
    rcases hparents with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · exact hres
    · simpa [Finset.union_comm] using hres
  have hlen : L0.length + L1.length = n-2 := by
    have hc := log_event_count_split H
    have hf := logFusionCount_layer_split H
    have hlenH : H.length = n+1 := by omega
    have hlenEq := congrArg List.length hlog
    rw [hL2] at hlenEq
    simp only [List.length_append, List.length_cons, List.length_nil] at hlenEq
    omega
  exact ⟨{
    L0 := L0, L1 := L1, B1 := B1, B2 := B2, left := A, right := B,
    P0 := v1.beforeState, P1 := v1.afterState, P2 := v2.beforeState, P3 := v2.afterState,
    log_eq := by simpa [hL2, hC] using hlog,
    lower0 := hlo0, lower1 := hlo1, fusion_count := hlen,
    first_nonempty := he1.transfer_packet_mem.1,
    second_nonempty := he2.transfer_packet_mem.1,
    disjoint := hdis12, covers := hcover, ordered := hparents,
    initial_path := runLogged_cyclicEventPath n hn _ hp,
    first_transfer := he1, middle_path := hmpath, second_transfer := he2,
    final_path := runLogged_cyclicEventPath n hn _ (by simpa [hL2, hC] using hfinal),
    first_receiver_empty := hs0, first_upper := hs1, second_upper := hs2,
    second_lower := hlower2 }⟩

end RSR2History
