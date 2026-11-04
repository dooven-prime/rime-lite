import converse.DecoderInsertion

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem canonical_pair_inside (r : ℕ) (hr : 2 ≤ r ∧ r ≤ n) :
    selectedPair n ⊆ arc (0 : ZMod n) r := by
  intro a ha
  have ha01 : a=0 ∨ a=1 := by simpa [selectedPair] using ha
  have hone : (1 : ZMod n).val=1 := ZMod.val_one'' (by omega)
  rw [arc, mem_interval_iff 0 a 0 r hr.2]
  rcases ha01 with rfl | rfl <;> simp [hone] <;> omega

theorem canonical_arc_nonempty (r : ℕ) (hr : 2 ≤ r ∧ r ≤ n) :
    (arc (0 : ZMod n) r).Nonempty := by
  refine ⟨0, ?_⟩
  exact canonical_pair_inside r hr (by simp [selectedPair])

/-- Even when the entire remaining complement is the partner, the two port
bindings are different full records. The side is not inferred from that set. -/
theorem checkpoint_port_bindings_distinct (C B : Finset (ZMod n))
    (carrier : C.Nonempty) (disjoint : Disjoint C B) :
    checkpointRecord true C B ≠ checkpointRecord false C B := by
  intro h
  have hparents : C=B := congrArg FusionRecord.left h
  obtain ⟨a, ha⟩ := carrier
  exact Finset.disjoint_left.mp disjoint ha (hparents ▸ ha)

/-- This is a statement about the current actual ports, not a clean witness.
The full-arc final merger still records which parent occupied each port. -/
theorem actual_checkpoint_increases {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (s : Execution n (ZMod n)) (C B : Finset (ZMod n)) (side : Bool)
    (ordered : SourceOrdered s.placed) (inside : arc 0 r ⊆ C)
    (ports : CheckpointPorts side s.placed C B) :
    B.Nonempty ∧ C.card-r < (C∪B).card-r ∧ (C∪B).card-r ≤ n-r := by
  have hn : 2 ≤ n := by omega
  have hstrict := actual_selected_partner_strict s C B side hn ordered ports
  have hbase : r ≤ C.card := by
    have hcard := Finset.card_le_card inside
    rw [card_arc 0 r hr.2] at hcard
    exact hcard
  have htotal : (C∪B).card ≤ n := by
    simpa only [ZMod.card] using Finset.card_le_univ (s := C∪B)
  exact ⟨hstrict.1, by omega, by omega⟩

/-- In the aligned source frame, every actual selected partner is a nonempty
end interval. Only the inherited interval geometry is reused: the origin,
record append and successor below are proved for this proper arc's own F. -/
theorem actual_partner_is_end_interval {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (s : Execution n (ZMod n)) (C u v : Finset (ZMod n)) (q : ZMod n)
    (ordered : SourceOrdered s.placed) (hC : s.placed q = some C)
    (inside : arc 0 r ⊆ C) (registered : s.origin.isSome = true)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (selected : arc 0 r ⊆ u ∨ arc 0 r ⊆ v) :
    ∃ (f : CheckpointSourceFrontier n) (side : Bool) (B : Finset (ZMod n)) (ell : ℕ),
      f.carrier=C ∧ 0<ell ∧ ell ≤ f.hi-f.lo ∧
      CheckpointPorts side s.placed C B ∧
      B = (if side then f.partnerR ell else f.partnerL ell) ∧
      (stepDefect (arc 0 r) s).origin=s.origin ∧
      (stepDefect (arc 0 r) s).chain=s.chain++[checkpointRecord side C B] ∧
      (stepDefect (arc 0 r) s).placed 0=some (C∪B) ∧
      (C∪B).card-r = (C.card-r)+ell ∧
      C.card-r < (C∪B).card-r ∧ (C∪B).card-r ≤ n-r := by
  have hn : 2 ≤ n := by omega
  have hp := canonical_pair_inside r hr
  have hselected : selectedPair n ⊆ u ∨ selectedPair n ⊆ v :=
    selected.imp (hp.trans ·) (hp.trans ·)
  obtain ⟨f, side, B, ell, hfC, hell, hbound, ports, hB,
      _oldOrigin, _oldChain, _oldPlacement, hsize, _oldStrict⟩ :=
    actual_selected_fusion_frontier s C u v q hn ordered hC
      (hp.trans inside) registered h0 h1 hselected
  obtain ⟨ho, hc, hplaced, _⟩ :=
    checkpoint_step_records (arc 0 r) C B side s hn registered inside ports
  have hcardC := f.carrier_card
  rw [hfC] at hcardC
  have hbase : r ≤ C.card := by
    have h := Finset.card_le_card inside
    simpa only [card_arc 0 r hr.2] using h
  have hproper := actual_checkpoint_increases hr s C B side ordered inside ports
  refine ⟨f, side, B, ell, hfC, hell, hbound, ports, hB, ho, hc, hplaced, ?_,
    hproper.2.1, hproper.2.2⟩
  omega

/-- A selected merger inserts exactly one new checkpoint. All three record
fields are transported from the actual step, rather than reconstructed from
the numeric key alone. -/
theorem actual_step_extends_code {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (s : Execution n (ZMod n)) (v : Code (n-r)) (j : ℕ) (hj : j ≤ n-r)
    (ordered : SourceOrdered s.placed) (registered : s.origin.isSome = true)
    (carrier : RecordedCarrier (arc 0 r) s)
    (suffix : ∀ i : Fin (n-r), j ≤ i.val → v i = none)
    (chain : s.chain=(decodePrefix hr v j hj).chain)
    (read : recordedCarrierResult s=some (decodePrefix hr v j hj).frontier.carrier)
    (absorbed : (decodePrefix hr v j hj).frontier.absorbed=r-2+j)
    (u w : Finset (ZMod n)) (h0 : s.placed 0=some u) (h1 : s.placed 1=some w)
    (selected : arc 0 r ⊆ u ∨ arc 0 r ⊆ w) :
    ∃ (v' : Code (n-r)) (b : ℕ) (hb : b ≤ n-r), j<b ∧
      (∀ i : Fin (n-r), b ≤ i.val → v' i=none) ∧
      (stepDefect (arc 0 r) s).origin.isSome=true ∧
      (stepDefect (arc 0 r) s).chain=(decodePrefix hr v' b hb).chain ∧
      recordedCarrierResult (stepDefect (arc 0 r) s)=some (decodePrefix hr v' b hb).frontier.carrier ∧
      (decodePrefix hr v' b hb).frontier.absorbed=r-2+b ∧
      RecordedCarrier (arc 0 r) (stepDefect (arc 0 r) s) := by
  obtain ⟨q, C, hC, inside, hread⟩ := carrier
  have hCeq : C=(decodePrefix hr v j hj).frontier.carrier :=
    Option.some.inj (hread.symm.trans read)
  obtain ⟨f, side, B, ell, hfC, hell, hbound, _ports, hB, ho, hc, hp, hsize, _, hmax⟩ :=
    actual_partner_is_end_interval hr s C u w q ordered hC inside registered h0 h1 selected
  have hfeq : f=(decodePrefix hr v j hj).frontier :=
    frontier_eq_of_carrier_eq_of_remaining f _ (hfC.trans hCeq) (by omega)
  let b := (C∪B).card-r
  have hcsize : C.card = r+j := by
    have h := (decodePrefix hr v j hj).frontier.carrier_card
    rw [← hCeq, absorbed] at h
    omega
  have hbval : b=j+ell := by dsimp [b]; omega
  have hjb : j<b := by omega
  obtain ⟨hafter, hdecode, hcarrier, habs⟩ :=
    decodePrefix_insert hr v j b hj hmax hjb side suffix absorbed
  have hB' : B = if side then (decodePrefix hr v j hj).frontier.partnerR (b-j)
      else (decodePrefix hr v j hj).frontier.partnerL (b-j) := by
    rw [hB, hfeq]
    simp only [show b-j=ell by omega]
  have hchain' : (stepDefect (arc 0 r) s).chain =
      (decodePrefix hr (insertCheckpoint v b side) b hmax).chain := by
    rw [hc, chain, hdecode, ← hCeq, ← hB']
  have hrec : recordedCarrierResult (stepDefect (arc 0 r) s)=some (C∪B) := by
    unfold recordedCarrierResult
    rw [hc]
    cases side <;> simp [checkpointRecord, Finset.union_comm]
  have hread' : recordedCarrierResult (stepDefect (arc 0 r) s)=
      some (decodePrefix hr (insertCheckpoint v b side) b hmax).frontier.carrier := by
    rw [hrec, hcarrier, ← hCeq, ← hB']
  refine ⟨insertCheckpoint v b side, b, hmax, hjb, hafter, ?_, hchain', hread', habs, ?_⟩
  · rw [ho]; exact registered
  · exact ⟨0, C∪B, hp, inside.trans Finset.subset_union_left, hrec⟩

end ProperArc.Chains
