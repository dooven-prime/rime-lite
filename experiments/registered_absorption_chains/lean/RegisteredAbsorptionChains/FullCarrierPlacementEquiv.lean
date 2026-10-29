import RegisteredAbsorptionChains.OriginClassification
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

private theorem decodedCarrier_eq_univ_of_empty
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (hempty :
      (decodeCode c hn).frontier.lo = (decodeCode c hn).frontier.hi) :
    decodedCarrier c hn = (Finset.univ : Finset (ZMod n)) := by
  let f := (decodeCode c hn).frontier
  change f.carrier = Finset.univ
  ext a
  rw [f.mem_carrier_iff]
  simp only [Finset.mem_univ, iff_true]
  have := f.noncrossing
  change f.lo = f.hi at hempty
  omega

/-- The empty-complement fiber of a reachable code consists of exactly the
physical phases of its complete carrier. The codomain records literal
placements attained by actual histories, not formal phase targets. -/
noncomputable def fullCarrierFixedChainPlacementEquiv
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (hempty :
      (decodeCode c hn).frontier.lo = (decodeCode c hn).frontier.hi) :
    ZMod n ≃ ActualFixedChainPlacements c hn := by
  classical
  let phases : ZMod n → ActualFixedChainPlacements c hn := fun q =>
    ⟨fullCarrierPlacement Finset.univ q, by
      obtain ⟨base, horigin, hchain, hrange, _⟩ :=
        full_carrier_code_fiber_phases c hn hempty
      have hmember :
          { base with placed := fullCarrierPlacement Finset.univ q } ∈
            FullCarrierFixedRecords (selectedPair n) base.origin base.chain := by
        rw [hrange]
        exact Set.mem_range_self q
      obtain ⟨⟨word, hword⟩, _, _, _⟩ := hmember
      refine ⟨word, ?_, ?_, ?_⟩
      · rw [hword, horigin, registration_origin hn]
        rfl
      · rw [hword, hchain]
      · exact congrArg Execution.placed hword⟩
  apply Equiv.ofBijective phases
  constructor
  · intro q q' heq
    apply fullCarrierPlacement_injective (Finset.univ : Finset (ZMod n))
    exact congrArg Subtype.val heq
  · intro P
    obtain ⟨word, hregistered, hchainP, hplaced⟩ := P.2
    obtain ⟨q, hq⟩ :=
      actual_code_carrier_at_site word hn c hregistered hchainP
    have hfull :
        (run (selectedPair n) (singletonExecution n) word).placed q =
          some (Finset.univ : Finset (ZMod n)) := by
      simpa [decodedCarrier_eq_univ_of_empty c hn hempty] using hq
    have hsource :
        SourceOrdered
          (run (selectedPair n) (singletonExecution n) word).placed :=
      reachable_source_ordered (selectedPair n) _ hn ⟨word, rfl⟩
    have hphase := sourceOrdered_fullCarrier _ hsource q hfull
    refine ⟨q, ?_⟩
    apply Subtype.ext
    exact hphase.symm.trans hplaced

end RegisteredAbsorptionChains
