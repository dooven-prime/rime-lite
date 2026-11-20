import RSR2History.UpperCursorReplayBudget
import RSR2History.AtomTransferLedger
import RSR2History.DelayedFamilyPremium

/-! Singleton-transfer replay with exact log and prescribed literal one-block endpoint. -/
namespace RSR2History
open RSR2.Parametric AllRTransfer
variable {n : Nat} [NeZero n]

def UpperFusionTree.initialCursorSlack (T : UpperFusionTree n) : Nat :=
  if T.leaves.idxOf 0 = 0 then 0 else n-T.leaves.idxOf 0

theorem UpperReservedReplay.full_of_lower_empty
    {P : Placement n} {cursor : Fin n} {k : Nat} {T : UpperFusionTree n}
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor k [T] [T] T.leaves site)
    (lower : lowerConfiguration P = lowerExtractionEmpty n) :
    P = fun _ => (true, zsite (((site T.firstLeaf).val : ZMod n) - (cursor.val : ZMod n))) := by
  funext a
  have hu : (P a).1 = true := by
    have he := congrFun lower a
    rcases hh : P a with ⟨layer, q⟩
    cases layer <;> simp [lowerConfiguration, lowerExtractionEmpty, hh] at *
  have hp : (phaseShift P true (cursor.val : ZMod n) a).1 = true := by simp [phaseShift, hu]
  have he : phaseShift P true (cursor.val : ZMod n) a =
      (true, (phaseShift P true (cursor.val : ZMod n) a).2) := Prod.ext hp rfl
  obtain ⟨tree, ht, ha, hq⟩ := (state.upper_position a _).mp he
  have htree : tree = T := by simpa using ht
  subst tree
  have hb : a ∈ packetAt (phaseShift P true (cursor.val : ZMod n)) true (site T.firstLeaf) := by
    apply (mem_packetAt _ _ _ _).mpr
    exact he.trans (congrArg (fun q => (true, q)) hq)
  rw [← zsite_cast (site T.firstLeaf), packetAt_phaseShift] at hb
  exact (mem_packetAt _ _ _ _).mp hb

theorem singleton_cursor_full_endpoint_word
    (hn : 2 ≤ n) {H : List (EffectiveEvent n)} {z : List (Fin n)} {T : UpperFusionTree n}
    (path : UpperForestPath 0 [] H n [T]) (grammar : SingletonUpperLog H z)
    (hlen : z.length = n) (hnodup : z.Nodup)
    (htree : T.leaves.length = n) (q : Fin n) :
    ∃ word, runLogged n (by omega) (seed n) word = some ((fun _ => (true, q)), H) ∧
      word.length + T.leftBranchDefect + T.initialCursorSlack ≤
        lowerExtractionCost n (by omega) z + 5*n.choose 2 + (n-1) := by
  have hbound : (forestLeaves [T]).length ≤ n := by simpa [forestLeaves] using htree.le
  let site := reservationSite (show 0 < n by omega) (forestLeaves [T]) hbound
  have seedState : UpperReservedReplay (seed n) (site 0) 0 [] [T] T.leaves site := by
    simpa only [site, forestLeaves, List.flatMap_cons, List.flatMap_nil, List.append_nil] using
      upperReserved_seed_of_forestPath (show 0 < n by omega) (site 0) path hbound
  have extraction := @lowerExtractionCost_attained_of_permutation n (by omega) z hlen hnodup
  obtain ⟨R, cf, u, s, hu, stateR, lowerR, hlenU, _⟩ :=
    path.singleton_cursor_replay grammar seedState (lowerConfiguration_seed n) extraction
  have hb := s.singleton_cost_le_with_defect seedState.frame hn
  have complete : T.leaves.Perm (List.range n) := by
    simpa [forestLeaves] using path.complete_leaves (by simp [forestLeaves])
  have hzero : 0 ∈ T.leaves := complete.mem_iff.mpr (List.mem_range.mpr (by omega))
  have hindex : (site 0).val = T.leaves.idxOf 0 := by
    simpa [forestLeaves] using seedState.frame.site_index 0 (by simpa [forestLeaves] using hzero)
  rw [hindex] at hb
  let loc : ZMod n := ((site T.firstLeaf).val : ZMod n) - (cf.val : ZMod n)
  have hR : R = fun _ => (true, zsite loc) := stateR.full_of_lower_empty lowerR
  let amount : ZMod n := (q.val : ZMod n) - loc
  let v := pWord true amount.val
  have hfinal : phaseShift R true amount = fun _ => (true, q) := by
    funext a
    rw [hR]
    simp only [phaseShift, ite_true, zsite_val_cast]
    have he : loc+amount = (q.val : ZMod n) := by dsimp [amount]; ring
    simp [he]
  have hv : runLogged n (by omega) R v = some ((fun _ => (true, q)), []) := by
    simpa only [v, hfinal] using runLogged_phase (show 1 < n by omega) R true amount
  have hvlen : v.length ≤ n-1 := by
    have he := ZMod.val_lt amount
    simpa only [v, pWord, List.length_replicate] using (show amount.val ≤ n-1 by omega)
  refine ⟨u++v, ?_, ?_⟩
  · simp [runLogged_append, hu, hv]
  · simp only [List.length_append]
    unfold UpperFusionTree.initialCursorSlack
    omega

omit [NeZero n] in
theorem SingletonUpperLog.transfer_count {H : List (EffectiveEvent n)} {z : List (Fin n)}
    (grammar : SingletonUpperLog H z) : z.length = logTransferCount H := by
  induction grammar with
  | nil => rfl
  | transfer a tail ih =>
      simp only [logTransferCount, List.map_cons, List.sum_cons, List.length_cons] at ih ⊢
      omega
  | fusion A B tail ih => simpa [logTransferCount] using ih

omit [NeZero n] in
theorem SingletonUpperLog.atom_count {H : List (EffectiveEvent n)} {z : List (Fin n)}
    (grammar : SingletonUpperLog H z) (a : Fin n) : atomTransferCount a H = z.count a := by
  induction grammar with
  | nil => rfl
  | transfer b tail ih =>
      rw [atomTransferCount_transfer_cons, ih]
      by_cases he : a = b <;> simp [he, eq_comm, Nat.add_comm]
  | fusion A B tail ih => simpa [atomTransferCount] using ih

omit [NeZero n] in
theorem CyclicEventPath.singleton_upper_log_of_counts {P Q : Placement n} {H : List (EffectiveEvent n)}
    (path : CyclicEventPath P H Q) :
    logLayerFusionCount false H = 0 → logTransferExcess H = 0 → ∃ z, SingletonUpperLog H z := by
  induction path with
  | nil same => exact fun _ _ => ⟨[], .nil⟩
  | cons edge tail ih =>
      intro hl hx
      cases edge with
      | fusion layer A B roots Q hA hB hd hs ht ho =>
          cases layer with
          | false => simp [logLayerFusionCount] at hl
          | true =>
              obtain ⟨z, hg⟩ := ih (by simpa [logLayerFusionCount] using hl)
                (by simpa [logTransferExcess] using hx)
              exact ⟨z, .fusion A B hg⟩
      | transfer packet lo up Q hp hls hlt hus hut hc =>
          have hcard : packet.card = 1 := by
            have hpos := Finset.card_pos.mpr hp
            simp only [logTransferExcess, List.map_cons, List.sum_cons] at hx
            omega
          obtain ⟨a, ha⟩ := Finset.card_eq_one.mp hcard
          subst packet
          obtain ⟨z, hg⟩ := ih (by simpa [logLayerFusionCount] using hl)
            (by simpa [logTransferExcess] using hx)
          exact ⟨a::z, .transfer a hg⟩

omit [NeZero n] in
theorem cyclicSignature_full_upper (q : Fin n) :
    cyclicSignature (fun _ : Fin n => (true, q)) true = [Finset.univ] := by
  have hp (r : Fin n) : packetAt (fun _ : Fin n => (true, q)) true r =
      if r = q then Finset.univ else ∅ := by
    ext a
    by_cases hr : r = q
    · subst r; simp [mem_packetAt]
    · simp [mem_packetAt, hr, Ne.symm hr]
  rw [signature_eq_occupied_map]
  have ho : occupiedSites (fun _ : Fin n => (true, q)) true = [q] := by
    have hU : (Finset.univ : Finset (Fin n)) ≠ ∅ := by
      intro he
      have hm := Finset.mem_univ q
      rw [he] at hm
      exact Finset.notMem_empty q hm
    have hb (r : Fin n) :
        ((if r = q then (Finset.univ : Finset (Fin n)) else ∅) != ∅) = decide (r = q) := by
      by_cases hr : r = q <;> simp [hr, hU]
    simp only [occupiedSites, hp, hb]
    rw [List.filter_eq]
    simp [List.Nodup.count (List.nodup_finRange n)]
  simp [ho, hp]

/-- The tree is an annotation of the original actual run, not a chosen replacement log. -/
theorem singleBlock_nTransfer_defect_word
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = n) :
    ∃ T : UpperFusionTree n, ∃ replay,
      UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      runLogged n (by omega) (seed n) replay = some (Q, H) ∧
      replay.length + T.leftBranchDefect + T.initialCursorSlack ≤
        maxLowerExtractionCost n (by omega) + 5*n.choose 2 + (n-1) := by
  obtain ⟨_, ⟨q, hQ⟩, hl, _⟩ := singleBlock_positiveTransfer_shape n (by omega) word hexec hblocks
    (by omega : 0 < logTransferCount H)
  have hlow : logLayerFusionCount false H = 0 := by omega
  have res := runLogged_resource_balance n (by omega) word hexec
  have hmass : logTransferMass H = n := by
    have he := res.2.1
    rw [hQ] at he
    simpa [lowerAtomMass, seed] using he
  have hx : logTransferExcess H = 0 := by omega
  obtain ⟨z, grammar⟩ := (runLogged_cyclicEventPath n (by omega) word hexec).singleton_upper_log_of_counts hlow hx
  have hzlen : z.length = n := grammar.transfer_count.trans ht
  have hupper : ∀ a, (Q a).1 = true := by intro a; simp [hQ]
  have hnodup : z.Nodup := by
    apply List.nodup_iff_count_le_one.mpr
    intro a
    rw [← grammar.atom_count a]
    exact le_of_eq (singleton_fullUpper_atomTransferCount (by omega) word hexec hupper a)
  obtain ⟨k, forest, trace, complete, cycle⟩ := singleton_run_ordered_forest (by omega) hexec
  have hk : k = n := by simpa [ht] using trace.toPath.transfer_count
  subst k
  have hforestlen : forest.length = 1 := by
    have he := cycle.perm.length_eq
    rw [hQ, cyclicSignature_full_upper] at he
    simpa [forestPackets] using he
  obtain ⟨T, rfl⟩ := List.length_eq_one_iff.mp hforestlen
  have htree : T.leaves.length = n := by simpa [forestLeaves] using complete.length_eq
  obtain ⟨replay, hr, hc⟩ := singleton_cursor_full_endpoint_word (by omega) trace.toPath
    grammar hzlen hnodup htree q
  have hk := lowerExtractionCost_le_max (hn := by omega) hzlen hnodup
  refine ⟨T, replay, trace, ?_, ?_⟩
  · simpa only [← hQ] using hr
  · omega

theorem singleBlock_nTransfer_short_word
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = n) :
    ∃ replay, runLogged n (by omega) (seed n) replay = some (Q, H) ∧
      replay.length ≤ maxLowerExtractionCost n (by omega) + 5*n.choose 2 + (n-1) := by
  obtain ⟨T, replay, _, hr, hc⟩ := singleBlock_nTransfer_defect_word hn word hexec hblocks ht
  exact ⟨replay, hr, by omega⟩

private theorem five_choose_two (n : Nat) : 5*n.choose 2 = (5*n*(n-1))/2 := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self n
  rw [Nat.mul_assoc, hq, Nat.choose_two_right, hq]
  omega

/-- The same actual tree witnesses both geometric slack terms. -/
theorem singleBlock_nTransfer_delayed_slack
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = n) :
    ∃ T : UpperFusionTree n,
      UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hexec⟩⟩ +
        T.leftBranchDefect + T.initialCursorSlack ≤ delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, replay, trace, hr, hc⟩ := singleBlock_nTransfer_defect_word hn word hexec hblocks ht
  have hd : historyDistance n (by omega) Q H ⟨word, hexec⟩ ≤ replay.length :=
    minimumWordLength_le _ ⟨word, hexec⟩ hr
  have hp := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  rw [five_choose_two] at hc
  refine ⟨T, trace, ?_⟩
  rw [delayedChainTotalPremiumMaximum_eq n hn]
  omega

/-- Unconditional within the actual n-transfer one-block stratum. -/
theorem singleBlock_nTransfer_delayed_domination
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = n) :
    totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hexec⟩⟩ ≤
      delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, _, h⟩ := singleBlock_nTransfer_delayed_slack hn word hexec hblocks ht
  omega

/-- Necessary geometric conditions only; no converse optimality assertion. -/
theorem singleBlock_nTransfer_extremal_shape
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : logTransferCount H = n)
    (hmax : totalObservationPremium n (by omega) ⟨(Q, H), ⟨word, hexec⟩⟩ =
      delayedChainTotalPremiumMaximum n hn) :
    ∃ T : UpperFusionTree n, UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      T.IsLeftComb ∧ T.leaves.idxOf 0 = 0 := by
  obtain ⟨T, trace, hs⟩ := singleBlock_nTransfer_delayed_slack hn word hexec hblocks ht
  have hE : T.leftBranchDefect = 0 := by omega
  have hphase : T.initialCursorSlack = 0 := by omega
  have complete : T.leaves.Perm (List.range n) := by
    simpa [forestLeaves] using trace.toPath.complete_leaves (by simp [forestLeaves])
  have hlen : T.leaves.length = n := by simpa using complete.length_eq
  have hzero : 0 ∈ T.leaves := complete.mem_iff.mpr (List.mem_range.mpr (by omega))
  have hindex : T.leaves.idxOf 0 < n := by
    simpa only [hlen] using List.idxOf_lt_length_iff.mpr hzero
  have hfirst : T.leaves.idxOf 0 = 0 := by
    by_contra he
    simp only [UpperFusionTree.initialCursorSlack, if_neg he] at hphase
    omega
  exact ⟨T, trace, T.defect_zero_iff_leftComb.mp hE, hfirst⟩

end RSR2History
