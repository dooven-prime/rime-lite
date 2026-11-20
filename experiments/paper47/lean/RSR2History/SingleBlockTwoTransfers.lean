import RSR2History.TwoPacketLoading

/-! Same-complete-log, same-literal-endpoint replay for two transfers. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer
variable {n : Nat} [NeZero n]

theorem singleBlock_twoTransfer_short_word (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n hn (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) :
    ∃ replay, runLogged n hn (seed n) replay = some (Q, H) ∧
      replay.length ≤ (3*n-4)*(n-2)+4*n := by
  obtain ⟨form⟩ := singleBlock_twoTransfer_normalForm hn word hr hblocks ht
  have hf0 : ∀ e ∈ form.L0, ∃ layer A B C, e = .fusion layer A B C := by
    intro e he
    obtain ⟨A, B, C, h⟩ := form.lower0 e he
    exact ⟨false, A, B, C, h⟩
  have hf1 : ∀ e ∈ form.L1, ∃ layer A B C, e = .fusion layer A B C := by
    intro e he
    obtain ⟨A, B, C, h⟩ := form.lower1 e he
    exact ⟨false, A, B, C, h⟩
  obtain ⟨R0, w0, h0, hs0, hc0⟩ := form.initial_path.phaseFree_fusion_replay hn hf0
  have hu0 : cyclicSignature R0 true = [] :=
    List.isRotated_nil_iff.mp ((hs0 true).trans (form.first_receiver_empty ▸ .refl _))
  obtain ⟨R1, w1, h1, hs1, hc1⟩ :=
    (form.first_transfer.congr hs0 (.refl _)).transfer_to_empty_short hn hu0
  obtain ⟨R2, w2, h2, hs2, hc2⟩ :=
    form.middle_path.phaseFree_fusion_replay_from hn hf1 R1 hs1
  have hu2 : cyclicSignature R2 true = [form.B1] :=
    List.isRotated_singleton_iff.mp ((hs2 true).trans (form.second_upper ▸ .refl _))
  have hl2 : cyclicSignature R2 false = [form.B2] :=
    List.isRotated_singleton_iff.mp ((hs2 false).trans (form.second_lower ▸ .refl _))
  obtain ⟨_, ⟨q, hQ⟩, _, _⟩ := singleBlock_positiveTransfer_shape n hn word hr hblocks (by omega)
  obtain ⟨side, hside⟩ : ∃ side, pairFinalEvent side form.B1 form.B2 =
      .fusion true form.left form.right Finset.univ := by
    rcases form.ordered with h | h
    · exact ⟨true, by simp [pairFinalEvent, h.1, h.2]⟩
    · exact ⟨false, by simp [pairFinalEvent, h.1, h.2]⟩
  obtain ⟨finish, hf, hcf⟩ := twoPacket_guarded_finish hn form.B1 form.B2
    form.first_nonempty form.second_nonempty form.disjoint form.covers hu2 hl2 side q
  have h01 : runLogged n hn (seed n) (w0 ++ w1) =
      some (R1, form.L0 ++ [.transfer form.B1]) := by
    rw [runLogged_append, h0]
    simp only [Option.bind_some, h1, Option.map_some]
  have h012 : runLogged n hn (seed n) ((w0 ++ w1) ++ w2) =
      some (R2, (form.L0 ++ [.transfer form.B1]) ++ form.L1) := by
    rw [runLogged_append, h01]
    simp only [Option.bind_some, h2, Option.map_some]
  refine ⟨((w0 ++ w1) ++ w2) ++ finish, ?_, ?_⟩
  · rw [runLogged_append, h012]
    simp only [Option.bind_some, hf, Option.map_some]
    rw [← hQ, hside]
    simpa only [List.append_assoc, List.singleton_append, List.cons_append, List.nil_append] using
      congrArg (fun events => some (Q, events)) form.log_eq.symm
  · simp only [List.length_append]
    calc
      w0.length + w1.length + w2.length + finish.length ≤
          (3*n-4)*form.L0.length + n + (3*n-4)*form.L1.length + 3*n := by omega
      _ = (3*n-4)*(n-2)+4*n := by rw [← form.fusion_count]; ring

theorem singleBlock_twoTransfer_historyDistance_le (hn : 1 < n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n hn (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) :
    historyDistance n hn Q H ⟨word, hr⟩ ≤ (3*n-4)*(n-2)+4*n := by
  obtain ⟨replay, hw, hc⟩ := singleBlock_twoTransfer_short_word hn word hr hblocks ht
  exact (minimumWordLength_le _ ⟨word, hr⟩ hw).trans hc

theorem singleBlock_twoTransfer_replay_budget (n : Nat) (hn : 3 ≤ n) :
    (3*n-4)*(n-2)+4*n = 3*(n-1)^2+5 := by
  have hfour := Nat.sub_add_cancel (show 4 ≤ 3*n by omega)
  have htwo := Nat.sub_add_cancel (show 2 ≤ n by omega)
  have hone := Nat.sub_add_cancel (show 1 ≤ n by omega)
  nlinarith

theorem singleBlock_twoTransfer_totalPremium_bound (hn : 3 ≤ n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) :
    totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hr⟩⟩ ≤ 3*n^2-8*n+11 := by
  have hd := singleBlock_twoTransfer_historyDistance_le (by omega) word hr hblocks ht
  rw [singleBlock_twoTransfer_replay_budget n hn] at hd
  have he := singleBlock_totalPremium_add_partitionCost n (by omega) word hr hblocks
  have hb := singleBlock_closed_premium_budget n hn 5
  omega

theorem singleBlock_twoTransfer_delayed_gap (hn : 3 ≤ n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) :
    4*n-9 + extractionExcess n (by omega) ≤ delayedChainTotalPremiumMaximum n hn -
      totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hr⟩⟩ := by
  have hb := singleBlock_twoTransfer_totalPremium_bound hn word hr hblocks ht
  have he := delayedMaximum_extractionExcess_balance n hn
  have hbig : 8*n ≤ 3*n^2 := by nlinarith
  have hs := Nat.sub_add_cancel hbig
  omega

theorem singleBlock_twoTransfer_not_global_maximizer (hn : 3 ≤ n)
    {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hr : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = 2) :
    totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hr⟩⟩ <
      globalTotalObservationPremium n (by omega) := by
  have hgap := singleBlock_twoTransfer_delayed_gap hn word hr hblocks ht
  have hle := delayedChainTotalPremiumMaximum_le_global hn
  omega

end RSR2History
