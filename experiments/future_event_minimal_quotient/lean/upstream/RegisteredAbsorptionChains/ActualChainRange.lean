import RegisteredAbsorptionChains.ActualSelectedFrontier
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem decoded_advance_congr (c d : Code (n - 2))
    (i : Fin (n - 2)) (x : DecodedCodePrefix n i.val)
    (h : c i = d i) : x.advance c i = x.advance d i := by
  unfold DecodedCodePrefix.advance
  rw [h]

theorem decoded_advance_none (c : Code (n - 2))
    (i : Fin (n - 2)) (x : DecodedCodePrefix n i.val)
    (h : c i = none) :
    (x.advance c i).frontier = x.frontier ∧
      (x.advance c i).chain = x.chain := by
  unfold DecodedCodePrefix.advance
  rw [h]
  exact ⟨rfl, rfl⟩

/-- A carrier with an unabsorbed source address determines both endpoints
of its source frontier. The full-carrier case is intentionally excluded. -/
theorem frontier_eq_of_carrier_eq_of_remaining
    (f g : CheckpointSourceFrontier n)
    (hcarrier : f.carrier = g.carrier)
    (hremaining : f.lo < f.hi) : f = g := by
  have hfg : ∀ a : ZMod n, a ∈ f.remaining ↔ a ∈ g.remaining := by
    intro a
    rw [← f.not_mem_carrier_iff_remaining,
      ← g.not_mem_carrier_iff_remaining, hcarrier]
  have hflo_n : f.lo < n := by have := f.hi_valid; omega
  have hflo : (f.lo : ZMod n) ∈ f.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simp [ZMod.val_natCast_of_lt hflo_n, hremaining]
  have hglo_lt : g.lo < g.hi := by
    have hmem := (mem_sourceInterval_iff g.lo g.hi g.hi_valid _).mp
      (hfg _ |>.mp hflo)
    omega
  have hglo_n : g.lo < n := by have := g.hi_valid; omega
  have hglo : (g.lo : ZMod n) ∈ g.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff g.lo g.hi g.hi_valid]
    simp [ZMod.val_natCast_of_lt hglo_n, hglo_lt]
  have hlo_le : g.lo ≤ f.lo := by
    have hmem := (mem_sourceInterval_iff g.lo g.hi g.hi_valid _).mp
      (hfg _ |>.mp hflo)
    simpa [ZMod.val_natCast_of_lt hflo_n] using hmem.1
  have hle_lo : f.lo ≤ g.lo := by
    have hmem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
      (hfg _ |>.mpr hglo)
    simpa [ZMod.val_natCast_of_lt hglo_n] using hmem.1
  have hlo : f.lo = g.lo := by omega
  have hfhi_n : f.hi - 1 < n := by
    have := f.lo_valid
    have := f.noncrossing
    have := f.hi_valid
    omega
  have hfhi : ((f.hi - 1 : ℕ) : ZMod n) ∈ f.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simp [ZMod.val_natCast_of_lt hfhi_n]
    omega
  have hghi_n : g.hi - 1 < n := by
    have := g.lo_valid
    have := g.noncrossing
    have := g.hi_valid
    omega
  have hghi : ((g.hi - 1 : ℕ) : ZMod n) ∈ g.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff g.lo g.hi g.hi_valid]
    simp [ZMod.val_natCast_of_lt hghi_n]
    omega
  have hhi_le : f.hi ≤ g.hi := by
    have hmem := (mem_sourceInterval_iff g.lo g.hi g.hi_valid _).mp
      (hfg _ |>.mp hfhi)
    have hv : f.hi - 1 < g.hi := by
      simpa [ZMod.val_natCast_of_lt hfhi_n] using hmem.2
    omega
  have hle_hi : g.hi ≤ f.hi := by
    have hmem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
      (hfg _ |>.mpr hghi)
    have hv : g.hi - 1 < f.hi := by
      simpa [ZMod.val_natCast_of_lt hghi_n] using hmem.2
    omega
  have hhi : f.hi = g.hi := by omega
  cases f with
  | mk flo fhi hfl hfn hfh =>
      cases g with
      | mk glo ghi hgl hgn hgh =>
          simp only at hlo hhi
          subst glo
          subst ghi
          rfl

/-- A decoder prefix reads only symbols strictly before its endpoint. -/
theorem decodeCodePrefix_congr (c d : Code (n - 2)) (hn : 2 ≤ n) :
    ∀ (j : ℕ) (hj : j ≤ n - 2),
      (∀ i : Fin (n - 2), i.val < j → c i = d i) →
      decodeCodePrefix c hn j hj = decodeCodePrefix d hn j hj := by
  intro j
  induction j with
  | zero =>
      intro hj _
      rfl
  | succ j ih =>
      intro hj hagree
      have hj' : j ≤ n - 2 := by omega
      have hprior := ih hj' (by
        intro i hi
        exact hagree i (by omega))
      let i : Fin (n - 2) := ⟨j, by omega⟩
      have hsymbol : c i = d i := hagree i (by simp [i])
      change (decodeCodePrefix c hn j hj').advance c i =
        (decodeCodePrefix d hn j hj').advance d i
      rw [hprior]
      exact decoded_advance_congr c d i _ hsymbol

/-- If a code has no symbols between two checkpoints, only the decoder's
proof-index changes; its source frontier and ordered chain do not. -/
theorem decodeCodePrefix_skip (c : Code (n - 2)) (hn : 2 ≤ n)
    (j : ℕ) (hj : j ≤ n - 2) :
    ∀ (k : ℕ) (hk : k ≤ n - 2), j ≤ k →
      (∀ i : Fin (n - 2), j ≤ i.val → i.val < k → c i = none) →
      (decodeCodePrefix c hn k hk).frontier =
          (decodeCodePrefix c hn j hj).frontier ∧
        (decodeCodePrefix c hn k hk).chain =
          (decodeCodePrefix c hn j hj).chain := by
  intro k
  induction k with
  | zero =>
      intro hk hjk _
      have hzero : j = 0 := by omega
      subst j
      exact ⟨rfl, rfl⟩
  | succ k ih =>
      intro hk hjk hnone
      by_cases hbelow : j ≤ k
      · have hk' : k ≤ n - 2 := by omega
        obtain ⟨hf, hc⟩ := ih hk' hbelow (by
          intro i hji hik
          exact hnone i hji (by omega))
        let i : Fin (n - 2) := ⟨k, by omega⟩
        have hci : c i = none := hnone i hbelow (by simp [i])
        change ( (decodeCodePrefix c hn k hk').advance c i).frontier =
            (decodeCodePrefix c hn j hj).frontier ∧
          ((decodeCodePrefix c hn k hk').advance c i).chain =
            (decodeCodePrefix c hn j hj).chain
        obtain ⟨hstepf, hstepc⟩ := decoded_advance_none c i _ hci
        exact ⟨hstepf.trans hf, hstepc.trans hc⟩
      · have heq : j = k + 1 := by omega
        subst j
        exact ⟨rfl, rfl⟩

/-- Insert one later checkpoint while retaining every earlier code symbol. -/
def insertCheckpoint (c : Code (n - 2)) (b : ℕ) (side : Side) :
    Code (n - 2) :=
  fun i => if i.val + 1 = b then some side else c i

omit [NeZero n] in
theorem insertCheckpoint_before (c : Code (n - 2)) (b : ℕ)
    (side : Side) (i : Fin (n - 2)) (hi : i.val + 1 < b) :
    insertCheckpoint c b side i = c i := by
  simp [insertCheckpoint, ne_of_lt hi]

omit [NeZero n] in
theorem insertCheckpoint_at (c : Code (n - 2)) (b : ℕ)
    (side : Side) (hb : 1 ≤ b) (hmax : b ≤ n - 2) :
    insertCheckpoint c b side ⟨b - 1, by omega⟩ = some side := by
  simp [insertCheckpoint, Nat.sub_add_cancel hb]

omit [NeZero n] in
theorem insertCheckpoint_after (c : Code (n - 2)) (b : ℕ)
    (side : Side) (i : Fin (n - 2)) (hi : b ≤ i.val) :
    insertCheckpoint c b side i = c i := by
  simp [insertCheckpoint, show i.val + 1 ≠ b by omega]

/-- Sparse insertion acts on the decoder by one exact L/R checkpoint step.
The intervening zero positions have no effect on the carrier or records. -/
theorem decodeCodePrefix_insertCheckpoint
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (j b : ℕ) (hj : j ≤ n - 2) (hb : b ≤ n - 2)
    (hjb : j < b) (side : Side)
    (hsuffix : ∀ i : Fin (n - 2), j ≤ i.val → c i = none)
    (habs : (decodeCodePrefix c hn j hj).frontier.absorbed = j) :
    let c' := insertCheckpoint c b side
    let old := decodeCodePrefix c hn j hj
    let fresh := decodeCodePrefix c' hn b hb
    (∀ i : Fin (n - 2), b ≤ i.val → c' i = none) ∧
      fresh.chain = old.chain ++
        [checkpointRecord side old.frontier.carrier
          (if side then old.frontier.partnerR (b - j)
            else old.frontier.partnerL (b - j))] ∧
      fresh.frontier.carrier = old.frontier.carrier ∪
        (if side then old.frontier.partnerR (b - j)
          else old.frontier.partnerL (b - j)) ∧
      fresh.frontier.absorbed = b := by
  let c' := insertCheckpoint c b side
  let old := decodeCodePrefix c hn j hj
  let fresh := decodeCodePrefix c' hn b hb
  have hbpos : 1 ≤ b := by omega
  have hbefore : ∀ i : Fin (n - 2), i.val < b - 1 → c' i = c i := by
    intro i hi
    exact insertCheckpoint_before c b side i (by omega)
  have hcongr : decodeCodePrefix c' hn (b - 1) (by omega) =
      decodeCodePrefix c hn (b - 1) (by omega) :=
    decodeCodePrefix_congr c' c hn (b - 1) (by omega) hbefore
  have hgap : j ≤ b - 1 := by omega
  have hskip := decodeCodePrefix_skip c hn j hj (b - 1) (by omega)
    hgap (by
      intro i hji hib
      exact hsuffix i hji)
  have hat : c' ⟨b - 1, by omega⟩ = some side :=
    insertCheckpoint_at c b side hbpos hb
  have hafter : ∀ i : Fin (n - 2), b ≤ i.val → c' i = none := by
    intro i hbi
    change insertCheckpoint c b side i = none
    rw [insertCheckpoint_after c b side i hbi]
    exact hsuffix i (by omega)
  have hfresh_chain : fresh.chain =
      ((decodeCodePrefix c' hn (b - 1) (by omega)).advance c'
        ⟨b - 1, by omega⟩).chain := by
    cases b with
    | zero => omega
    | succ k => rfl
  have hfresh_frontier : fresh.frontier =
      ((decodeCodePrefix c' hn (b - 1) (by omega)).advance c'
        ⟨b - 1, by omega⟩).frontier := by
    cases b with
    | zero => omega
    | succ k => rfl
  have hbound : b - j ≤ old.frontier.hi - old.frontier.lo := by
    have htotal := old.frontier.remaining_plus_absorbed
    rw [old.frontier.remaining_card, habs] at htotal
    omega
  have hbefore_absorbed :
      (decodeCodePrefix c hn (b - 1) (by omega)).frontier.absorbed = j := by
    calc
      _ = old.frontier.absorbed := congrArg CheckpointSourceFrontier.absorbed hskip.1
      _ = j := habs
  have hlen : b - 1 + 1 - j = b - j := by omega
  have hlen_frontier :
      b - 1 + 1 - (decodeCodePrefix c hn j hj).frontier.absorbed = b - j := by
    rw [habs]
    exact hlen
  have hstep_chain : fresh.chain = old.chain ++
      [checkpointRecord side old.frontier.carrier
        (if side then old.frontier.partnerR (b - j)
          else old.frontier.partnerL (b - j))] := by
    rw [hfresh_chain, hcongr]
    cases side with
    | false =>
        simp [DecodedCodePrefix.advance, hat, hskip.1, hskip.2,
          hlen_frontier, old]
    | true =>
        simp [DecodedCodePrefix.advance, hat, hskip.1, hskip.2,
          hlen_frontier, old]
  have hstep_frontier : fresh.frontier.carrier = old.frontier.carrier ∪
      (if side then old.frontier.partnerR (b - j)
        else old.frontier.partnerL (b - j)) := by
    rw [hfresh_frontier, hcongr]
    cases side with
    | false =>
        simp only [DecodedCodePrefix.advance, hat, hskip.1,
          hlen_frontier]
        exact old.frontier.carrier_nextL (b - j) hbound
    | true =>
        simp only [DecodedCodePrefix.advance, hat, hskip.1,
          hlen_frontier]
        exact old.frontier.carrier_nextR (b - j) hbound
  have hstep_absorbed : fresh.frontier.absorbed = b := by
    rw [hfresh_frontier, hcongr]
    cases side with
    | false =>
        simp only [DecodedCodePrefix.advance, hat, hskip.1,
          hlen_frontier]
        rw [old.frontier.absorbed_nextL, habs]
        omega
    | true =>
        simp only [DecodedCodePrefix.advance, hat, hskip.1,
          hlen_frontier]
        rw [old.frontier.absorbed_nextR, habs]
        omega
  exact ⟨hafter, hstep_chain, hstep_frontier, hstep_absorbed⟩

/-- One actual selected merger extends a sparse decoder prefix by exactly
one checkpoint, with its source address and port orientation unchanged. -/
theorem actual_selected_step_extends_code
    (s : Execution n (ZMod n)) (c : Code (n - 2))
    (j : ℕ) (hn : 2 ≤ n) (hj : j ≤ n - 2)
    (hordered : SourceOrdered s.placed)
    (hregistered : s.origin.isSome = true)
    (hcarrier : RecordedCarrier (selectedPair n) s)
    (hsuffix : ∀ i : Fin (n - 2), j ≤ i.val → c i = none)
    (hchain : s.chain = (decodeCodePrefix c hn j hj).chain)
    (hread : recordedCarrierResult s =
      some (decodeCodePrefix c hn j hj).frontier.carrier)
    (habsorbed : (decodeCodePrefix c hn j hj).frontier.absorbed = j)
    (u v : Finset (ZMod n))
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hselected : selectedPair n ⊆ u ∨ selectedPair n ⊆ v) :
    ∃ (c' : Code (n - 2)) (b : ℕ) (hb : b ≤ n - 2),
      j < b ∧
      (∀ i : Fin (n - 2), b ≤ i.val → c' i = none) ∧
      (stepDefect (selectedPair n) s).origin.isSome = true ∧
      (stepDefect (selectedPair n) s).chain =
        (decodeCodePrefix c' hn b hb).chain ∧
      recordedCarrierResult (stepDefect (selectedPair n) s) =
        some (decodeCodePrefix c' hn b hb).frontier.carrier ∧
      (decodeCodePrefix c' hn b hb).frontier.absorbed = b ∧
      RecordedCarrier (selectedPair n) (stepDefect (selectedPair n) s) := by
  obtain ⟨q, C, hC, hinside, hCread⟩ := hcarrier
  have hCeq : C = (decodeCodePrefix c hn j hj).frontier.carrier := by
    have heq := hCread.symm.trans hread
    exact Option.some.inj heq
  obtain ⟨f, side, B, ell, hfC, hellpos, hellbound,
      _hports, hB, horigin, hchain_step, hplaced, hsize, _⟩ :=
    actual_selected_fusion_frontier s C u v q hn hordered
      hC hinside hregistered h0 h1 hselected
  have hfremaining : f.lo < f.hi := by omega
  have hfeq : f = (decodeCodePrefix c hn j hj).frontier :=
    frontier_eq_of_carrier_eq_of_remaining f _
      (hfC.trans hCeq) hfremaining
  have hell : ell ≤ (decodeCodePrefix c hn j hj).frontier.hi -
      (decodeCodePrefix c hn j hj).frontier.lo := by
    simpa [hfeq] using hellbound
  let b := (C ∪ B).card - 2
  have hbval : b = j + ell := by
    dsimp [b]
    rw [hsize, hfeq, habsorbed]
  have hjb : j < b := by omega
  have hb : b ≤ n - 2 := by
    have htotal := (decodeCodePrefix c hn j hj).frontier.remaining_plus_absorbed
    rw [(decodeCodePrefix c hn j hj).frontier.remaining_card,
      habsorbed] at htotal
    omega
  let c' := insertCheckpoint c b side
  obtain ⟨hafter, hdecode_chain, hdecode_carrier, hdecode_absorbed⟩ :=
    decodeCodePrefix_insertCheckpoint c hn j b hj hb hjb side hsuffix habsorbed
  have hB' : B = if side then
      (decodeCodePrefix c hn j hj).frontier.partnerR (b - j) else
      (decodeCodePrefix c hn j hj).frontier.partnerL (b - j) := by
    rw [hB, hfeq]
    simp only [show b - j = ell by omega]
  have hnextchain : (stepDefect (selectedPair n) s).chain =
      (decodeCodePrefix c' hn b hb).chain := by
    rw [hchain_step, hchain, hdecode_chain]
    rw [← hCeq, ← hB']
  have hnextread : recordedCarrierResult (stepDefect (selectedPair n) s) =
      some (decodeCodePrefix c' hn b hb).frontier.carrier := by
    have hrec : recordedCarrierResult (stepDefect (selectedPair n) s) =
        some (C ∪ B) := by
      unfold recordedCarrierResult
      rw [hchain_step]
      cases side <;> simp [checkpointRecord, Finset.union_comm]
    rw [hrec, hdecode_carrier, ← hCeq, ← hB']
  have hnextregistered : (stepDefect (selectedPair n) s).origin.isSome = true := by
    rw [horigin]
    exact hregistered
  have hnextcarrier : RecordedCarrier (selectedPair n)
      (stepDefect (selectedPair n) s) := by
    exact ⟨0, C ∪ B, hplaced, hinside.trans Finset.subset_union_left,
      by rw [hnextread, hdecode_carrier, ← hCeq, ← hB']⟩
  exact ⟨c', b, hb, hjb, hafter, hnextregistered,
    hnextchain, hnextread, hdecode_absorbed, hnextcarrier⟩

/-- The reverse induction retains a sparse code only after registration.
Before registration there is no selected chain to decode. -/
def ActualDecodedTrace (hn : 2 ≤ n) (s : Execution n (ZMod n)) : Prop :=
  (s.origin = none ∧ s.chain = []) ∨
    ∃ (c : Code (n - 2)) (j : ℕ) (hj : j ≤ n - 2),
      (∀ i : Fin (n - 2), j ≤ i.val → c i = none) ∧
      s.origin.isSome = true ∧
      s.chain = (decodeCodePrefix c hn j hj).chain ∧
      recordedCarrierResult s =
        some (decodeCodePrefix c hn j hj).frontier.carrier ∧
      (decodeCodePrefix c hn j hj).frontier.absorbed = j ∧
      RecordedCarrier (selectedPair n) s

theorem actual_decoded_trace_preserved
    (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (a : Letter) (hordered : SourceOrdered s.placed)
    (htrace : ActualDecodedTrace hn s) :
    ActualDecodedTrace hn (step (selectedPair n) s a) := by
  rcases htrace with ⟨horigin, hchain⟩ |
    ⟨c, j, hj, hsuffix, hregistered, hchain,
      hread, habsorbed, hcarrier⟩
  · cases a with
    | p =>
        left
        simpa [step, horigin, hchain]
    | d =>
        cases h0 : s.placed 0 with
        | none =>
            left
            simp [step, stepDefect, h0, horigin, hchain]
        | some u =>
            cases h1 : s.placed 1 with
            | none =>
                left
                simp [step, stepDefect, h0, h1, horigin, hchain]
            | some v =>
                by_cases hreg : u ∪ v = selectedPair n
                · right
                  let c : Code (n - 2) := fun _ => none
                  have hnew_origin : (stepDefect (selectedPair n) s).origin =
                      some ⟨u, v, u ∪ v⟩ := by
                    simp [stepDefect, h0, h1, horigin, hreg]
                  have hnew_chain : (stepDefect (selectedPair n) s).chain = [] := by
                    simp [stepDefect, h0, h1, horigin, hchain]
                  have hbase : (decodeCodePrefix c hn 0 (by omega)).frontier.carrier =
                      selectedPair n := by
                    simp [decodeCodePrefix, DecodedCodePrefix.initial,
                      CheckpointSourceFrontier.carrier, sourceInterval]
                  have hread : recordedCarrierResult
                      (stepDefect (selectedPair n) s) = some (selectedPair n) := by
                    simp [recordedCarrierResult, hnew_origin, hnew_chain, hreg]
                  have hplaced : (stepDefect (selectedPair n) s).placed 0 =
                      some (selectedPair n) := by
                    simpa [stepDefect_placed, fusionPlacement, h0, h1, hreg]
                  refine ⟨c, 0, by omega, ?_, ?_, ?_, ?_, ?_, ?_⟩
                  · intro i _
                    rfl
                  · simpa [step, hnew_origin]
                  · simpa [step, decodeCodePrefix, DecodedCodePrefix.initial,
                      hnew_chain]
                  · simpa [step, hbase] using hread
                  · simp [decodeCodePrefix, DecodedCodePrefix.initial,
                      CheckpointSourceFrontier.absorbed]
                  · exact ⟨0, selectedPair n, by simpa [step] using hplaced,
                      Finset.Subset.rfl, by simpa [step] using hread⟩
                · left
                  simp [step, stepDefect, h0, h1, horigin, hchain, hreg]
  · have hselected_ne : (selectedPair n).Nonempty :=
      ⟨0, by simp [selectedPair]⟩
    have hnext := actual_registered_carrier_step s (selectedPair n) a hn
      hordered hselected_ne hregistered hcarrier
    cases a with
    | p =>
        right
        refine ⟨c, j, hj, hsuffix, hnext.1, ?_, ?_, habsorbed, hnext.2⟩
        · simpa [step] using hchain
        · simpa [step, recordedCarrierResult] using hread
    | d =>
        cases h0 : s.placed 0 with
        | none =>
            right
            refine ⟨c, j, hj, hsuffix, hnext.1, ?_, ?_, habsorbed,
              hnext.2⟩
            · simpa [step, stepDefect, h0] using hchain
            · simpa [step, stepDefect, h0, recordedCarrierResult] using hread
        | some u =>
            cases h1 : s.placed 1 with
            | none =>
                right
                refine ⟨c, j, hj, hsuffix, hnext.1, ?_, ?_, habsorbed,
                  hnext.2⟩
                · simpa [step, stepDefect, h0, h1] using hchain
                · simpa [step, stepDefect, h0, h1, recordedCarrierResult]
                    using hread
            | some v =>
                by_cases hsel : selectedPair n ⊆ u ∨ selectedPair n ⊆ v
                · obtain ⟨c', b, hb, _, hafter, hreg', hchain',
                    hread', habs', hcarrier'⟩ :=
                    actual_selected_step_extends_code s c j hn hj hordered
                      hregistered hcarrier hsuffix hchain hread habsorbed
                      u v h0 h1 hsel
                  exact Or.inr ⟨c', b, hb, hafter, by simpa [step] using hreg',
                    by simpa [step] using hchain',
                    by simpa [step] using hread', habs',
                    by simpa [step] using hcarrier'⟩
                · right
                  have hsame_origin :
                      (stepDefect (selectedPair n) s).origin = s.origin := by
                    cases ho : s.origin with
                    | none => simp [ho] at hregistered
                    | some rho => simp [stepDefect, h0, h1, ho]
                  have hsame_chain :
                      (stepDefect (selectedPair n) s).chain = s.chain := by
                    simp [stepDefect, h0, h1, hregistered, hsel]
                  refine ⟨c, j, hj, hsuffix, hnext.1, ?_, ?_, habsorbed,
                    hnext.2⟩
                  · simpa [step, hsame_chain] using hchain
                  · change recordedCarrierResult (stepDefect (selectedPair n) s) =
                      some (decodeCodePrefix c hn j hj).frontier.carrier
                    unfold recordedCarrierResult at hread ⊢
                    rw [hsame_origin, hsame_chain]
                    exact hread

/-- The reverse decoder invariant holds along one uninterrupted actual word. -/
theorem actual_decoded_trace_run_from
    (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (word : List Letter) (hordered : SourceOrdered s.placed)
    (htrace : ActualDecodedTrace hn s) :
    ActualDecodedTrace hn (run (selectedPair n) s word) := by
  induction word generalizing s with
  | nil => simpa [run] using htrace
  | cons a rest ih =>
      change ActualDecodedTrace hn
        (run (selectedPair n) (step (selectedPair n) s a) rest)
      exact ih (step (selectedPair n) s a)
        (step_ordered (selectedPair n) s a hn hordered)
        (actual_decoded_trace_preserved s hn a hordered htrace)

theorem actual_decoded_trace_run (word : List Letter) (hn : 2 ≤ n) :
    ActualDecodedTrace hn
      (run (selectedPair n) (singletonExecution n) word) := by
  exact actual_decoded_trace_run_from (singletonExecution n) hn word
    singletonExecution_ordered (Or.inl ⟨rfl, rfl⟩)

/-- Every actual registered selected chain belongs to the image of the
symbolic ternary-code decoder. This is the reverse direction of the chain
classification; no cleanliness is assumed of the actual history. -/
theorem actual_chain_in_decode_range (word : List Letter) (hn : 2 ≤ n)
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true) :
    ∃ c : Code (n - 2),
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn := by
  rcases actual_decoded_trace_run word hn with hpre |
    ⟨c, j, hj, hsuffix, _, hchain, _, _, _⟩
  · simp [hpre.1] at hregistered
  · have hskip := decodeCodePrefix_skip c hn j hj (n - 2) (le_refl _)
      (by omega) (by
        intro i hji _
        exact hsuffix i hji)
    exact ⟨c, hchain.trans hskip.2.symm⟩

/-- A registered actual chain has one and only one ternary code. The
registration origin is deliberately not included in this uniqueness claim. -/
theorem actual_chain_unique_code (word : List Letter) (hn : 2 ≤ n)
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true) :
    ∃! c : Code (n - 2),
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn := by
  obtain ⟨c, hc⟩ := actual_chain_in_decode_range word hn hregistered
  refine ⟨c, hc, ?_⟩
  intro d hd
  exact (decodeChain_injective hn (hc.symm.trans hd)).symm

/-- The codomain is the genuinely reachable chain set, not all syntactic
lists of fusion records. -/
def ReachableSelectedChain (n : ℕ) [NeZero n] :=
  { A : List (FusionRecord (ZMod n)) //
    ∃ word : List Letter,
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true ∧
      (run (selectedPair n) (singletonExecution n) word).chain = A }

noncomputable def codeEquivReachableSelectedChain (hn : 2 ≤ n) :
    Code (n - 2) ≃ ReachableSelectedChain n := by
  let f : Code (n - 2) → ReachableSelectedChain n := fun c =>
    ⟨decodeChain c hn, by
      obtain ⟨word, horigin, hchain, _, _⟩ := realize_clean_code c hn
      refine ⟨word, ?_, hchain⟩
      rw [horigin, registration_origin hn]
      rfl⟩
  apply Equiv.ofBijective f
  constructor
  · intro c d hcd
    exact decodeChain_injective hn (congrArg Subtype.val hcd)
  · intro A
    obtain ⟨word, hregistered, hchain⟩ := A.property
    obtain ⟨c, hc⟩ := actual_chain_in_decode_range word hn hregistered
    refine ⟨c, Subtype.ext ?_⟩
    exact hc.symm.trans hchain

end RegisteredAbsorptionChains
