import RSR2History.SingletonStratumExtrema

/-!
The extraction order is read from the same original effective log. On the
actual n-transfer one-block stratum, every transfer is a singleton; the
`SingletonUpperLog` proof identifies this observer with that exact order.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer
variable {n : Nat}

noncomputable def singletonTransferOrder (H : List (EffectiveEvent n)) : List (Fin n) :=
  H.filterMap (fun | .fusion _ _ _ _ => none | .transfer B => B.toList.head?)

theorem SingletonUpperLog.order_eq {H : List (EffectiveEvent n)} {z : List (Fin n)}
    (grammar : SingletonUpperLog H z) : singletonTransferOrder H = z := by
  induction grammar with
  | nil => rfl
  | transfer a tail ih => simpa [singletonTransferOrder] using congrArg (List.cons a) ih
  | fusion A B tail ih => simpa [singletonTransferOrder] using ih

section ActualOrder
variable [NeZero n]

omit [NeZero n] in
theorem singleBlock_nTransfer_actual_order
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) (ht : logTransferCount H = n) :
    SingletonUpperLog H (singletonTransferOrder H) ∧ (singletonTransferOrder H).length = n ∧
      (singletonTransferOrder H).Nodup := by
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
  have hz : z = singletonTransferOrder H := grammar.order_eq.symm
  subst z
  refine ⟨grammar, grammar.transfer_count.trans ht, ?_⟩
  apply List.nodup_iff_count_le_one.mpr
  intro a
  rw [← grammar.atom_count a]
  exact le_of_eq (singleton_fullUpper_atomTransferCount (by omega) word hexec
    (by intro a; simp [hQ]) a)

theorem singleBlock_nTransfer_order_defect_word
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) (ht : logTransferCount H = n) :
    ∃ T : UpperFusionTree n, ∃ replay,
      UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      runLogged n (by omega) (seed n) replay = some (Q, H) ∧
      replay.length + T.leftBranchDefect + T.initialCursorSlack ≤
        lowerExtractionCost n (by omega) (singletonTransferOrder H) + 5*n.choose 2 + (n-1) := by
  obtain ⟨grammar, hzlen, hnodup⟩ := singleBlock_nTransfer_actual_order hn word hexec hblocks ht
  obtain ⟨_, ⟨q, hQ⟩, _, _⟩ := singleBlock_positiveTransfer_shape n (by omega) word hexec hblocks
    (by omega : 0 < logTransferCount H)
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
  exact ⟨T, replay, trace, by simpa only [← hQ] using hr, hc⟩

private theorem five_choose_two (n : Nat) : 5*n.choose 2 = (5*n*(n-1))/2 := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self n
  rw [Nat.mul_assoc, hq, Nat.choose_two_right, hq]
  omega

theorem singleBlock_nTransfer_extraction_slack
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q, H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) (ht : logTransferCount H = n) :
    ∃ T : UpperFusionTree n, UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      totalObservationPremium n (by omega) ⟨(Q,H), ⟨word,hexec⟩⟩ + T.leftBranchDefect +
        T.initialCursorSlack + (maxLowerExtractionCost n (by omega) -
          lowerExtractionCost n (by omega) (singletonTransferOrder H)) ≤
        delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, replay, trace, hr, hc⟩ := singleBlock_nTransfer_order_defect_word hn word hexec hblocks ht
  obtain ⟨_, hlen, hnodup⟩ := singleBlock_nTransfer_actual_order hn word hexec hblocks ht
  have hk := lowerExtractionCost_le_max (hn := by omega) hlen hnodup
  have hd : historyDistance n (by omega) Q H ⟨word,hexec⟩ ≤ replay.length :=
    minimumWordLength_le _ ⟨word,hexec⟩ hr
  have hp := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  rw [five_choose_two] at hc
  refine ⟨T, trace, ?_⟩
  rw [delayedChainTotalPremiumMaximum_eq n hn]
  omega

theorem singleBlock_nTransfer_extremal_extraction
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)} (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ}) (ht : logTransferCount H = n)
    (hmax : totalObservationPremium n (by omega) ⟨(Q,H), ⟨word,hexec⟩⟩ =
      delayedChainTotalPremiumMaximum n hn) :
    (∃ T : UpperFusionTree n, UpperForestTrace (seed n) 0 [] H Q n [T] ∧
      T.IsLeftComb ∧ T.leaves.idxOf 0 = 0) ∧
    lowerExtractionCost n (by omega) (singletonTransferOrder H) = maxLowerExtractionCost n (by omega) := by
  obtain ⟨T, _, hs⟩ := singleBlock_nTransfer_extraction_slack hn word hexec hblocks ht
  obtain ⟨_, hlen, hnodup⟩ := singleBlock_nTransfer_actual_order hn word hexec hblocks ht
  have hk := lowerExtractionCost_le_max (hn := by omega) hlen hnodup
  exact ⟨singleBlock_nTransfer_extremal_shape hn word hexec hblocks ht hmax, by omega⟩

end ActualOrder
end RSR2History
