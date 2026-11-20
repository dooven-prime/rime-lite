import RSR2History.SingleBlockPartitionCost

/-! Transfer count is a structural parameter of actual one-block histories. -/

namespace RSR2History
open RSR2.Parametric AllRTransfer

theorem logTransferMass_eq_zero_of_count_zero (events : List (EffectiveEvent n))
    (hzero : logTransferCount events = 0) : logTransferMass events = 0 := by
  induction events with
  | nil => rfl
  | cons event rest ih =>
      cases event with
      | fusion layer A B C =>
          simpa [logTransferMass] using ih (by simpa [logTransferCount] using hzero)
      | transfer packet => simp [logTransferCount] at hzero

theorem constant_totalPacketCount (n : Nat) (hn : 0 < n) (coord : Bool × Fin n) :
    totalPacketCount (fun _ : Fin n => coord) = 1 := by
  apply totalPacketCount_eq_representatives_length _ [coord] (by simp)
  intro loc
  simp only [List.mem_singleton]
  constructor
  · intro h
    exact ⟨site0 n hn, h.symm⟩
  · rintro ⟨_, h⟩
    exact h.symm

theorem constant_lowerPacketCount (n : Nat) (hn : 0 < n) (layer : Bool) (q : Fin n) :
    lowerPacketCount (fun _ : Fin n => (layer, q)) = if layer then 0 else 1 := by
  classical
  have hc := constant_totalPacketCount n hn (layer, q)
  cases layer with
  | false =>
      have hu : upperPacketCount (fun _ : Fin n => (false, q)) = 0 := by
        simp [upperPacketCount_eq_countP, occupiedAt, packet]
      simpa [totalPacketCount, hu] using hc
  | true => simp [lowerPacketCount, occupiedAt, packet]

theorem constant_lowerAtomMass (n : Nat) (layer : Bool) (q : Fin n) :
    lowerAtomMass (fun _ : Fin n => (layer, q)) = if layer then 0 else n := by
  cases layer <;> simp [lowerAtomMass]

/-- A positive transfer count forces the terminal full packet upstairs.
The two cases give exact layer fusion counts on the same effective log. -/
theorem singleBlock_transfer_strata (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    (logTransferCount events = 0 ∧
      (∃ q, Q = fun _ => (false, q)) ∧
      logLayerFusionCount false events = n-1 ∧ logLayerFusionCount true events = 0) ∨
    (1 ≤ logTransferCount events ∧ logTransferCount events ≤ n ∧
      (∃ q, Q = fun _ => (true, q)) ∧
      logLayerFusionCount false events = n-logTransferCount events ∧
      logLayerFusionCount true events = logTransferCount events-1) := by
  obtain ⟨⟨layer, q⟩, hQ⟩ :=
    (unorderedPacketBlocks_eq_singleBlock_iff n (by omega) Q).mp hblocks
  have hr := (runLogged_resource_balance n hn word hexec).1
  have hm := (runLogged_resource_balance n hn word hexec).2
  have hl := runLogged_lower_packet_balance n hn word hexec
  have hseed : lowerAtomMass (seed n) = n := by simp [lowerAtomMass, seed]
  rw [seed_totalPacketCount, hQ, constant_totalPacketCount n (by omega)] at hr
  rw [seed_lowerPacketCount, hQ, constant_lowerPacketCount n (by omega)] at hl
  rw [hseed, hQ, constant_lowerAtomMass] at hm
  have hsplit := logFusionCount_layer_split events
  cases layer with
  | false =>
      simp only [Bool.false_eq_true, if_false] at hl hm
      left
      refine ⟨by omega, ⟨q, hQ⟩, by omega, by omega⟩
  | true =>
      simp only [if_true, Nat.zero_add] at hl hm
      have hpos : 1 ≤ logTransferCount events := by
        by_contra h
        have hz : logTransferCount events = 0 := by omega
        have hmass := logTransferMass_eq_zero_of_count_zero events hz
        omega
      exact Or.inr ⟨hpos, by omega, ⟨q, hQ⟩, by omega, by omega⟩

theorem singleBlock_noTransfer_shape (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hzero : logTransferCount events = 0) :
    (∃ q, Q = fun _ => (false, q)) ∧
      logLayerFusionCount false events = n-1 ∧ logLayerFusionCount true events = 0 := by
  rcases singleBlock_transfer_strata n hn word hexec hblocks with h | h
  · exact h.2
  · omega

theorem singleBlock_positiveTransfer_shape (n : Nat) (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (hpos : 0 < logTransferCount events) :
    logTransferCount events ≤ n ∧ (∃ q, Q = fun _ => (true, q)) ∧
      logLayerFusionCount false events = n-logTransferCount events ∧
      logLayerFusionCount true events = logTransferCount events-1 := by
  rcases singleBlock_transfer_strata n hn word hexec hblocks with h | h
  · omega
  · exact h.2

/-- No upper event can be hidden inside a zero-transfer lower-fusion prefix. -/
theorem lowerFusionOnly_of_counts (events : List (EffectiveEvent n))
    (ht : logTransferCount events = 0) (hu : logLayerFusionCount true events = 0) :
    ∀ e ∈ events, ∃ A B C, e = .fusion false A B C := by
  induction events with
  | nil => simp
  | cons event rest ih =>
      cases event with
      | transfer packet => simp [logTransferCount] at ht
      | fusion layer A B C =>
          cases layer with
          | true => simp [logLayerFusionCount] at hu
          | false =>
              have hr := ih (by simpa [logTransferCount] using ht)
                (by simpa [logLayerFusionCount] using hu)
              intro e he
              rcases List.mem_cons.mp he with rfl | he
              · exact ⟨A, B, C, rfl⟩
              · exact hr e he

theorem singleBlock_totalPremium_add_partitionCost
    (n : Nat) (hn : 1 < n) {Q : Placement n} {events : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) :
    totalObservationPremium n hn ⟨(Q, events), ⟨word, hexec⟩⟩ + (2*n-3) =
      historyDistance n hn Q events ⟨word, hexec⟩ := by
  obtain ⟨coord, hQ⟩ :=
    (unorderedPacketBlocks_eq_singleBlock_iff n (by omega) Q).mp hblocks
  subst Q
  have hchain := observationDistance_chain n hn (fun _ => coord) events ⟨word, hexec⟩
  have hbase := fullPacket_partitionDistance_eq_singleBlock n hn coord
    (partition_attainable_of_endpoint n hn (fun _ => coord)
      (endpoint_attainable_of_logged hn ⟨word, hexec⟩))
  rw [singleBlockPartitionDistance_exact n hn] at hbase
  rw [hbase] at hchain
  unfold totalObservationPremium
  dsimp only
  rw [hbase]
  exact Nat.sub_add_cancel (hchain.1.trans hchain.2)

end RSR2History
