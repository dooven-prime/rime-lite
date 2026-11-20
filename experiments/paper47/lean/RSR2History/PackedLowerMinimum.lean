import RSR2History.PackedCursorReplay

/-!
The independent minimum packed lower cost. Feasibility, attainment and
comparison use exactly the `PackedLowerPath` event contract, including ordered
lower fusions and zero-cost whole-packet extractions. The minimizing path can
replace the original lower projection without changing the original upper
forest trace or the complete effective log.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- The auxiliary lower optimum. No attainment assertion is made for an
infeasible event log; the actual-history theorem below supplies feasibility. -/
noncomputable def packedLowerCost (n : Nat) (hn : 1 < n)
    (h : List (EffectiveEvent n)) : Nat :=
  sInf {cost | PackedLowerPath n hn (lowerExtractionSeed n) h
    (lowerExtractionEmpty n) cost}

theorem packedLowerCost_le {n : Nat} {hn : 1 < n}
    {h : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn (lowerExtractionSeed n) h
      (lowerExtractionEmpty n) cost) : packedLowerCost n hn h ≤ cost :=
  Nat.sInf_le path

theorem packedLowerCost_attained {n : Nat} {hn : 1 < n}
    {h : List (EffectiveEvent n)}
    (feasible : ∃ cost, PackedLowerPath n hn (lowerExtractionSeed n) h
      (lowerExtractionEmpty n) cost) :
    PackedLowerPath n hn (lowerExtractionSeed n) h (lowerExtractionEmpty n)
      (packedLowerCost n hn h) := Nat.sInf_mem feasible

/-- Any actual positive-transfer one-block history supplies a feasible packed
lower problem. This does not require an upper tree or any budget hypothesis. -/
theorem singleBlock_packedLowerPath_exists
    (n : Nat) (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 0 < logTransferCount H) :
    ∃ cost, PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) cost := by
  obtain ⟨_, ⟨q, hQ⟩, _, _⟩ :=
    singleBlock_positiveTransfer_shape n hn word hexec hblocks ht
  obtain ⟨cost, path, _⟩ := runLogged_packedLower_projection word hexec
  have hempty : lowerConfiguration Q = lowerExtractionEmpty n := by
    funext a
    simp [hQ, lowerConfiguration, lowerExtractionEmpty]
  exact ⟨cost, by simpa only [lowerConfiguration_seed, hempty] using path⟩

theorem singleBlock_packedLowerCost_attained
    (n : Nat) (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 0 < logTransferCount H) :
    PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) (packedLowerCost n hn (packedLowerLog H)) :=
  packedLowerCost_attained
    (singleBlock_packedLowerPath_exists n hn word hexec hblocks ht)

/-- Minimizing removes the original realization's potentially redundant lower
preparations; its lower-letter count remains a valid comparison bound. -/
theorem singleBlock_packedLowerCost_le_lowerLetters
    (n : Nat) (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 0 < logTransferCount H) :
    packedLowerCost n hn (packedLowerLog H) ≤
      word.count (.p false) + word.count (.d false) := by
  obtain ⟨_, ⟨q, hQ⟩, _, _⟩ :=
    singleBlock_positiveTransfer_shape n hn word hexec hblocks ht
  obtain ⟨cost, path, hcost⟩ := runLogged_packedLower_projection word hexec
  have hempty : lowerConfiguration Q = lowerExtractionEmpty n := by
    funext a
    simp [hQ, lowerConfiguration, lowerExtractionEmpty]
  have path' : PackedLowerPath n hn (lowerExtractionSeed n) (packedLowerLog H)
      (lowerExtractionEmpty n) cost := by
    simpa only [lowerConfiguration_seed, hempty] using path
  exact (packedLowerCost_le path').trans hcost

section Replay
variable {n : Nat} [NeZero n]

/-- The minimum lower path is combined with the forest trace of the original
actual history. The exact cursor and final-phase costs are retained; neither
is replaced by its uniform budget in the length equality. -/
theorem singleBlock_packed_minimum_replay_exact
    (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ (T : UpperFusionTree n) (site : Nat → Fin n) (finalCursor : Fin n)
      (phase : Nat) (replay : List Letter),
      ∃ s : PackedCursorSchedule site 0 [] (site 0) H (logTransferCount H)
          [T] finalCursor,
        UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
        runLogged n hn (seed n) replay = some (Q,H) ∧
        replay.length = packedLowerCost n hn (packedLowerLog H) + s.cost + phase ∧
        phase ≤ n-1 ∧
        s.cost + T.leftBranchDefect + T.initialCursorSlack ≤
          packedUpperBudget n (logTransferCount H) := by
  obtain ⟨htn, ⟨q, hQ⟩, _, _⟩ :=
    singleBlock_positiveTransfer_shape n hn word hexec hblocks (by omega)
  obtain ⟨k, forest, trace, _, cycle⟩ := singleton_run_ordered_forest hn hexec
  have hk : k = logTransferCount H := by simpa using trace.toPath.transfer_count
  subst k
  have hforestlen : forest.length = 1 := by
    have he := cycle.perm.length_eq
    rw [hQ, cyclicSignature_full_upper] at he
    simpa [forestPackets] using he
  obtain ⟨T, rfl⟩ := List.length_eq_one_iff.mp hforestlen
  have extraction := singleBlock_packedLowerCost_attained n hn word hexec hblocks
    (by omega : 0 < logTransferCount H)
  have complete : T.leaves.Perm (List.range (logTransferCount H)) := by
    simpa [forestLeaves] using trace.toPath.complete_leaves (by simp [forestLeaves])
  have htree : T.leaves.length = logTransferCount H := by simpa using complete.length_eq
  have hbound : (forestLeaves [T]).length ≤ n := by
    simpa [forestLeaves, htree] using htn
  let site := reservationSite (show 0 < n by omega) (forestLeaves [T]) hbound
  have seedState : UpperReservedReplay (seed n) (site 0) 0 [] [T] T.leaves site := by
    simpa only [site, forestLeaves, List.flatMap_cons, List.flatMap_nil, List.append_nil] using
      upperReserved_seed_of_forestPath (show 0 < n by omega) (site 0) trace.toPath hbound
  obtain ⟨replay, cf, phase, s, hr, hlen, hphase⟩ :=
    trace.toPath.packed_cursor_endpoint_replay seedState (lowerConfiguration_seed n) extraction q
  have hb := s.cost_le_with_defect seedState.frame ht
  have hzero : 0 ∈ T.leaves := complete.mem_iff.mpr (List.mem_range.mpr (by omega))
  have hindex : (site 0).val = T.leaves.idxOf 0 := by
    simpa [forestLeaves] using seedState.frame.site_index 0
      (by simpa [forestLeaves] using hzero)
  rw [hindex] at hb
  refine ⟨T, site, cf, phase, replay, s, trace, ?_, hlen, hphase, ?_⟩
  · simpa only [← hQ] using hr
  · change s.cost + T.leftBranchDefect +
      (if T.leaves.idxOf 0 = 0 then 0 else n-T.leaves.idxOf 0) ≤
        packedUpperBudget n (logTransferCount H) at hb
    exact hb

/-- Bounded replay using the attained independent lower minimum. -/
theorem singleBlock_packed_minimum_replay
    (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ (T : UpperFusionTree n) (replay : List Letter),
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      runLogged n hn (seed n) replay = some (Q,H) ∧
      replay.length + T.leftBranchDefect + T.initialCursorSlack ≤
        packedLowerCost n hn (packedLowerLog H) +
          packedUpperBudget n (logTransferCount H) + (n-1) := by
  obtain ⟨T, site, cf, phase, replay, s, trace, hr, hlen, hphase, hb⟩ :=
    singleBlock_packed_minimum_replay_exact hn word hexec hblocks ht
  exact ⟨T, replay, trace, hr, by omega⟩

/-- The actual history distance, with the same trace's tree and initial
cursor defects, is bounded using the independently minimized lower problem. -/
theorem singleBlock_packed_minimum_historyDistance
    (hn : 1 < n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n hn (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ T : UpperFusionTree n,
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      historyDistance n hn Q H ⟨word,hexec⟩ +
        T.leftBranchDefect + T.initialCursorSlack ≤
          packedLowerCost n hn (packedLowerLog H) +
            packedUpperBudget n (logTransferCount H) + (n-1) := by
  obtain ⟨T, replay, trace, hr, hb⟩ :=
    singleBlock_packed_minimum_replay hn word hexec hblocks ht
  have hd : historyDistance n hn Q H ⟨word,hexec⟩ ≤ replay.length :=
    minimumWordLength_le _ ⟨word,hexec⟩ hr
  exact ⟨T, trace, by omega⟩

end Replay
end RSR2History
