import Paper44.ProperCarrierLabels
import RegisteredAbsorptionChains.FinitePositiveFiber

/-! # The actual placement fibre for a fixed proper carrier and label

Complete histories are used only as witnesses. The elements counted are
literal placements, each counted once. The full chain may vary within a
retained-label class; its carrier and retained ordered records do not vary.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

def ActualProperPlacements (j : ℕ) (f : ProperCarrier n)
    (label : ActualProperPrefixLabel j f) :=
  {P : Placement n (Finset (ZMod n)) //
    ∃ s : CircularState n, s.val.origin.isSome = true ∧
      (∃ q, s.val.placed q = some f.val.carrier) ∧
      circularLabel j s.val = label.val ∧ s.val.placed = P}

/-- Changing the complete chain while keeping its exact proper frontier does
not change which literal placements its actual execution fibre contains. -/
theorem fixedChain_placement_transfer (hn : 3 ≤ n)
    (c d : Code (n - 2))
    (hf : (decodeCode c (by omega)).frontier = (decodeCode d (by omega)).frontier)
    (hp : (decodeCode c (by omega)).frontier.lo < (decodeCode c (by omega)).frontier.hi)
    (P : ActualFixedChainPlacements d (by omega)) :
    ∃ w : List Letter,
      let s := run (selectedPair n) (singletonExecution n) w
      s.origin = some (canonicalOrigin n) ∧ s.chain = decodeChain c (by omega) ∧ s.placed = P.val := by
  obtain ⟨w, hr, hc, hP⟩ := P.property
  have hp' : (decodeCode d (by omega)).frontier.lo < (decodeCode d (by omega)).frontier.hi := by
    rw [← hf]; exact hp
  obtain ⟨t, data, hu, hv, hplace⟩ := actual_fiber_normal_form w (by omega) d hr hc hp'
  obtain ⟨v, ho, hchain, hvplace⟩ := code_fiber_target_reachable c (by omega) data
    (by rw [hf]; exact hu) (by rw [hf]; exact hv)
  rw [registration_origin (by omega)] at ho
  exact ⟨v, ho, hchain, hvplace.trans (hplace.symm.trans hP)⟩

/-- The forward map is literally the placement identity. In particular no
choice of realizing history is counted as another placement. -/
noncomputable def properPrefixPlacementEquiv (hn : 3 ≤ n) (j : ℕ)
    (f : ProperCarrier n) (label : ActualProperPrefixLabel j f)
    (c : Code (n - 2)) (hc : (decodeCode c (by omega)).frontier = f.val)
    (hl : codePrefixLabel hn j c = label.val) :
    ActualFixedChainPlacements c (by omega) ≃ ActualProperPlacements j f label := by
  have hp : (decodeCode c (by omega)).frontier.lo < (decodeCode c (by omega)).frontier.hi := by
    rw [hc]; exact f.property
  let lift : ActualFixedChainPlacements c (by omega) → ActualProperPlacements j f label := fun P =>
    ⟨P.val, by
      obtain ⟨w, hr, hchain, hP⟩ := P.property
      have ho := actual_registered_origin_unique w hn hr
      rw [registration_origin (by omega)] at ho
      obtain ⟨q, hq⟩ := actual_code_carrier_at_site w (by omega) c hr hchain
      exact ⟨⟨run {0, 1} (singletonExecution n) w, w, rfl⟩, hr,
        ⟨q, by
          change (run (selectedPair n) (singletonExecution n) w).placed q = _
          simpa only [decodedCarrier, hc] using hq⟩,
        by
          change circularLabel j (run (selectedPair n) (singletonExecution n) w) = _
          rw [circularLabel, ho, hchain]
          exact hl,
        hP⟩⟩
  refine Equiv.ofBijective lift ⟨?_, ?_⟩
  · intro a b h
    apply Subtype.ext
    exact congrArg (fun P : ActualProperPlacements j f label => P.val) h
  ·
    intro P
    obtain ⟨s, hr, hq, hlabel, hP⟩ := P.property
    obtain ⟨w, hw⟩ := s.property
    have hr' : (run (selectedPair n) (singletonExecution n) w).origin.isSome = true := by
      simpa only [selectedPair, hw] using hr
    obtain ⟨e, he⟩ := actual_chain_in_decode_range w (by omega) hr'
    have hefront : (decodeCode e (by omega)).frontier = f.val := by
      obtain ⟨q', hq'⟩ := actual_code_carrier_at_site w (by omega) e hr' he
      obtain ⟨q, hq⟩ := hq
      have hin (g : CheckpointSourceFrontier n) : selectedPair n ⊆ g.carrier := by
        intro a ha; exact Finset.mem_union_left _ (Finset.mem_union_left _ ha)
      have hplaced : (run (selectedPair n) (singletonExecution n) w).placed q = some f.val.carrier := by
        simpa only [selectedPair, hw] using hq
      have hC := (sourceOrdered_selected_packet_unique _ (selectedPair n) _ _ q q'
        (run_ordered _ _ w (by omega) singletonExecution_ordered)
        ⟨0, by simp [selectedPair]⟩ hplaced (hin _) hq' (hin _)).2
      exact (frontier_eq_of_carrier_eq_of_remaining f.val _ hC f.property).symm
    let Pe : ActualFixedChainPlacements e (by omega) :=
      ⟨P.val, w, hr', he, by simpa only [selectedPair, hw] using hP⟩
    obtain ⟨v, ho, hchain, hv⟩ := fixedChain_placement_transfer hn c e (hc.trans hefront.symm) hp Pe
    exact ⟨⟨P.val, v, by simp [ho], hchain, hv⟩, Subtype.ext rfl⟩

@[simp] theorem properPrefixPlacementEquiv_value (hn : 3 ≤ n) (j : ℕ)
    (f : ProperCarrier n) (label : ActualProperPrefixLabel j f)
    (c : Code (n - 2)) (hc : (decodeCode c (by omega)).frontier = f.val)
    (hl : codePrefixLabel hn j c = label.val) (P : ActualFixedChainPlacements c (by omega)) :
    (properPrefixPlacementEquiv hn j f label c hc hl P).val = P.val := rfl

theorem card_actualProperPlacements (hn : 3 ≤ n) (j : ℕ)
    (f : ProperCarrier n) (label : ActualProperPrefixLabel j f) :
    Nat.card (ActualProperPlacements j f label) =
      n * (n + (f.val.hi - f.val.lo) - 2).choose (f.val.hi - f.val.lo) := by
  obtain ⟨c, hc, hl⟩ := actual_proper_code hn j f label
  have hp : (decodeCode c (by omega)).frontier.lo < (decodeCode c (by omega)).frontier.hi := by
    rw [hc]; exact f.property
  rw [← Nat.card_congr (properPrefixPlacementEquiv hn j f label c hc hl), Nat.card_eq_fintype_card]
  simpa only [hc] using card_actualFixedChainPlacements_positive c (by omega) hp

/-- Manuscript weight, with `r` the number of absorbed outside atoms. -/
theorem card_actualProperPlacements_paper (hn : 3 ≤ n) (j : ℕ)
    (f : ProperCarrier n) (label : ActualProperPrefixLabel j f) (r : ℕ)
    (hr : f.val.absorbed = r) :
    Nat.card (ActualProperPlacements j f label) =
      n * (2 * (n - 2) - r).choose (n - 2 - r) := by
  have htotal := f.val.remaining_plus_absorbed
  rw [f.val.remaining_card, hr] at htotal
  have hk : f.val.hi - f.val.lo = n - 2 - r := by omega
  have ht : n + (f.val.hi - f.val.lo) - 2 = 2 * (n - 2) - r := by omega
  rw [card_actualProperPlacements hn j f label, hk, ← hk, ht, hk]

end Paper44
