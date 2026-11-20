import RSR2History.SingleBlockTransferStructure
import RSR2History.PhaseFreeFusionPort
import RSR2History.SingleBlockNoTransfer

/-! Exact event shape and short actual replay for one-transfer full packets. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer
variable {n : Nat} [NeZero n]

private theorem first_vertical (word : List Letter) (hv : .v ∈ word) :
    ∃ pre post, word = pre ++ .v :: post ∧ .v ∉ pre := by
  induction word with
  | nil => simp at hv
  | cons letter rest ih =>
      by_cases he : letter = .v
      · exact ⟨[], rest, by simp [he], by simp⟩
      · obtain ⟨pre, post, hw, hn⟩ := ih (by simpa [Ne.symm he] using hv)
        exact ⟨letter :: pre, post, by simp [hw], by simp [Ne.symm he, hn]⟩

/-- The split is extracted from the given actual word. The unique transfer
is of the whole atom set and is the last effective event; its raw tail is silent. -/
theorem singleBlock_oneTransfer_log_decomposition (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hone : logTransferCount events = 1) :
    ∃ pre post lowerEvents q,
      word = pre ++ .v :: post ∧
      events = lowerEvents ++ [.transfer Finset.univ] ∧
      (∀ e ∈ lowerEvents, ∃ A B C, e = .fusion false A B C) ∧
      lowerEvents.length = n-1 ∧
      runLogged n hn (seed n) pre =
        some ((fun _ => (false, site0 n (by omega))), lowerEvents) ∧
      runLogged n hn (fun _ => (true, site0 n (by omega))) post = some (Q, []) ∧
      Q = fun _ => (true, q) := by
  obtain ⟨_, ⟨q, hQ⟩, _, hupper⟩ := singleBlock_positiveTransfer_shape n hn word
    hexec hblocks (by omega)
  have hcount : word.count .v = 1 := (runLogged_transfer_count n hn hexec).symm.trans hone
  have hv : .v ∈ word := by
    by_contra h
    have := List.count_eq_zero.mpr h
    omega
  obtain ⟨pre, post, hw, hnpre⟩ := first_vertical word hv
  have hnpost : post.count .v = 0 := by
    have hz := List.count_eq_zero.mpr hnpre
    rw [hw, List.count_append] at hcount
    simp only [List.count_cons_self] at hcount
    omega
  cases hp : runLogged n hn (seed n) pre with
  | none => simp [hw, runLogged_append, hp] at hexec
  | some result =>
    obtain ⟨before, earlier⟩ := result
    cases hs : step n hn before .v with
    | none => simp [hw, runLogged_append, hp, runLogged, hs] at hexec
    | some after =>
      cases ht : runLogged n hn after post with
      | none => simp [hw, runLogged_append, hp, runLogged, hs, ht] at hexec
      | some result =>
        obtain ⟨last, later⟩ := result
        have he : last = Q ∧ earlier ++
            .transfer (packetAt before false (site0 n (by omega))) :: later = events := by
          simpa [hw, runLogged_append, hp, runLogged, hs, ht, emittedEvents] using hexec
        have hpzero : logTransferCount earlier = 0 := by
          rw [runLogged_transfer_count n hn hp, List.count_eq_zero.mpr hnpre]
        have htzero : logTransferCount later = 0 := by
          rw [runLogged_transfer_count n hn ht, hnpost]
        have hpm := logTransferMass_eq_zero_of_count_zero earlier hpzero
        have htm := logTransferMass_eq_zero_of_count_zero later htzero
        have hm := (runLogged_resource_balance n hn word hexec).2.1
        have hseed : lowerAtomMass (seed n) = n := by simp [lowerAtomMass, seed]
        rw [hQ, constant_lowerAtomMass, hseed] at hm
        have hevents : events = earlier ++ [.transfer (packetAt before false
            (site0 n (by omega)))] ++ later := by simpa using he.2.symm
        rw [hevents, logTransferMass_append, logTransferMass_append, hpm, htm] at hm
        have hcard : (packetAt before false (site0 n (by omega))).card = n := by
          simpa [logTransferMass] using hm
        have hfull : packetAt before false (site0 n (by omega)) = Finset.univ := by
          apply Finset.eq_of_subset_of_card_le (Finset.subset_univ _)
          simp [hcard]
        have hbefore : before = fun _ => (false, site0 n (by omega)) := by
          funext a
          exact (mem_packetAt _ _ _ _).mp (by rw [hfull]; simp)
        have hafter : after = fun _ => (true, site0 n (by omega)) := by
          have hlift : liftPacket n (by omega) before =
              fun _ => (true, site0 n (by omega)) := by
            funext a
            simp [liftPacket, hbefore]
          exact ((step_v_eq_some_iff n hn before after).mp hs).2.trans hlift
        have hrest := (runLogged_resource_balance n hn post ht).1
        rw [he.1, hQ, hafter, constant_totalPacketCount n (by omega),
          constant_totalPacketCount n (by omega)] at hrest
        have hsplit := log_event_count_split later
        have hlate : later = [] := by
          by_contra h
          have := List.length_pos_iff.mpr h
          omega
        have hevents' : events = earlier ++ [.transfer Finset.univ] := by
          simpa [hfull, hlate] using hevents
        have hearlyUpper : logLayerFusionCount true earlier = 0 := by
          have hz : logLayerFusionCount true events = 0 := by omega
          simpa [hevents', logLayerFusionCount] using hz
        have hpRank := (runLogged_resource_balance n hn pre hp).1
        rw [hbefore, constant_totalPacketCount n (by omega), seed_totalPacketCount] at hpRank
        have hlen : earlier.length = n-1 := by
          have := log_event_count_split earlier
          omega
        exact ⟨pre, post, earlier, q, hw, hevents',
          lowerFusionOnly_of_counts earlier hpzero hearlyUpper, hlen,
          by simpa [hbefore] using hp, by simpa [hafter, he.1, hlate] using ht, hQ⟩

private theorem full_packet_of_same_signature_at_port (hn : 1 < n)
    {P : Placement n} (layer : Layer) (q : Fin n)
    (hsame : SameCyclicSignatures P (fun _ => (layer, q)))
    (hbusy : (packetAt P layer (site0 n (by omega))).Nonempty) :
    P = fun _ => (layer, site0 n (by omega)) := by
  have hmem := packetAt_mem_cyclicSignature P layer (site0 n (by omega)) hbusy
  have hmemQ := (hsame layer).mem_iff.mp hmem
  obtain ⟨r, hr⟩ := packet_site_of_mem_signature (fun _ : Fin n => (layer, q)) layer hmemQ
  obtain ⟨a, ha⟩ := hbusy
  have haQ : (layer, q) = (layer, zsite r) :=
    (mem_packetAt _ _ _ a).mp (by rwa [hr])
  have hq : q = zsite r := congrArg Prod.snd haQ
  have hpkt : packetAt P layer (site0 n (by omega)) = Finset.univ := by
    rw [← hr]
    ext b
    simp [packetAt, hq]
  funext a
  exact (mem_packetAt _ _ _ a).mp (by rw [hpkt]; simp)

/-- Every actual one-transfer one-block observation has a single actual
short replay. The prefix does not pay a final lower phase-restoration cost. -/
theorem singleBlock_oneTransfer_short_word (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hone : logTransferCount events = 1) :
    ∃ replay, runLogged n hn (seed n) replay = some (Q, events) ∧
      replay.length ≤ (3*n-4)*(n-1)+n := by
  obtain ⟨pre, _, lowerEvents, q, _, hevents, hlow, hlen, hp, _, hQ⟩ :=
    singleBlock_oneTransfer_log_decomposition hn word hexec hblocks hone
  have path := runLogged_cyclicEventPath n hn pre hp
  obtain ⟨R, fusionWord, hprefix, hsame, hcost, hbusy⟩ :=
    path.phaseFree_lower_fusion_replay_port hn hlow (by intro h; simp [h] at hlen; omega)
      (seed n) (.refl _)
  have hR : R = fun _ => (false, site0 n (by omega)) :=
    full_packet_of_same_signature_at_port hn false (site0 n (by omega)) hsame hbusy
  have hguard : liftGuard n (by omega) R := by
    rw [hR]
    exact ⟨⟨site0 n (by omega), rfl⟩, by rintro ⟨a, ha⟩; cases ha⟩
  have hpacket : packetAt R false (site0 n (by omega)) = Finset.univ := by
    ext a
    simp [packetAt, hR]
  have hv : runLogged n hn R [.v] =
      some ((fun _ => (true, site0 n (by omega))), [.transfer Finset.univ]) := by
    have hs : step n hn R .v = some (fun _ => (true, site0 n (by omega))) := by
      apply (step_v_eq_some_iff n hn R _).mpr
      refine ⟨hguard, ?_⟩
      funext a
      simp [liftPacket, hR]
    simp [runLogged, hs, emittedEvents, hpacket]
  have ha := runLogged_phase hn (fun _ => (true, site0 n (by omega))) true (q.val : ZMod n)
  have hphase : phaseShift (fun _ : Fin n => (true, site0 n (by omega))) true
      (q.val : ZMod n) = Q := by
    rw [hQ]
    funext a
    simp [phaseShift, site0]
  rw [hphase] at ha
  let align := pWord true (q.val : ZMod n).val
  have halign : runLogged n hn (fun _ => (true, site0 n (by omega))) align =
      some (Q, []) := ha
  have hva : runLogged n hn R ([.v] ++ align) =
      some (Q, [.transfer Finset.univ]) := by
    simp only [runLogged_append, hv, Option.bind_some, halign, Option.map_some,
      List.append_nil]
  refine ⟨fusionWord ++ [.v] ++ align, ?_, ?_⟩
  · rw [List.append_assoc, runLogged_append, hprefix]
    simpa only [Option.bind_some, hva, Option.map_some] using
      congrArg (fun H => some (Q, H)) hevents.symm
  · have hqa : align.length ≤ n-1 := by
      simp only [align, pWord, List.length_replicate]
      have hlt := ZMod.val_lt (q.val : ZMod n)
      omega
    rw [hlen] at hcost
    simp only [List.length_append, List.length_singleton]
    omega

theorem singleBlock_oneTransfer_historyDistance_le (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hone : logTransferCount events = 1) :
    historyDistance n hn Q events ⟨word, hexec⟩ ≤ (3*n-4)*(n-1)+n := by
  obtain ⟨replay, hr, hc⟩ := singleBlock_oneTransfer_short_word hn word hexec hblocks hone
  exact (minimumWordLength_le _ ⟨word, hexec⟩ hr).trans hc

theorem singleBlock_oneTransfer_replay_budget (n : Nat) (hn : 3 ≤ n) :
    (3*n-4)*(n-1)+n = 3*(n-1)^2+1 := by
  have hfour := Nat.sub_add_cancel (show 4 ≤ 3*n by omega)
  have hone := Nat.sub_add_cancel (show 1 ≤ n by omega)
  nlinarith

theorem singleBlock_oneTransfer_totalPremium_bound (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 1) :
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ ≤
      3*n^2-8*n+7 := by
  have hd := singleBlock_oneTransfer_historyDistance_le (by omega) word hexec hblocks ht
  rw [singleBlock_oneTransfer_replay_budget n hn] at hd
  have he := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hb := singleBlock_closed_premium_budget n hn 1
  omega

theorem singleBlock_oneTransfer_delayed_gap (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 1) :
    2*n-4 ≤ delayedChainTotalPremiumMaximum n hn -
      totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ ∧
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ <
      delayedChainTotalPremiumMaximum n hn := by
  have hd := singleBlock_oneTransfer_historyDistance_le (by omega) word hexec hblocks ht
  rw [singleBlock_oneTransfer_replay_budget n hn] at hd
  have he := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hb := delayedChainTotalPremiumMaximum_lower_bound n hn
  constructor <;> omega

/-- Exclusion does not assume the open equality between global and delayed maxima. -/
theorem singleBlock_oneTransfer_not_global_maximizer (hn : 3 ≤ n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount events = 1) :
    totalObservationPremium n (by omega) ⟨(Q, events), ⟨word, hexec⟩⟩ <
      globalTotalObservationPremium n (by omega) :=
  (singleBlock_oneTransfer_delayed_gap hn word hexec hblocks ht).2.trans_le
    (delayedChainTotalPremiumMaximum_le_global hn)

end RSR2History
