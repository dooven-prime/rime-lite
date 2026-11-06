import RegisteredAbsorptionChains.FullCarrierPlacementEquiv
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Complete registered execution records attained from the singleton seed. -/
abbrev ActualRegisteredSummaries (n : ℕ) [NeZero n] :=
  {s : Execution n (ZMod n) //
    ReachableExecution (selectedPair n) s ∧ s.origin.isSome = true}

/-- One fiber type for each ternary code. The positive-complement branch
uses rank parameters; the full-carrier branch uses a physical site. -/
noncomputable abbrev CodeFiberParams (c : Code (n - 2)) (hn : 2 ≤ n) :=
  if (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi then
    PositiveRankFiberParams n
      ((decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo)
  else ZMod n

noncomputable def codeFiberPlacementEquiv
    (c : Code (n - 2)) (hn : 2 ≤ n) :
    CodeFiberParams c hn ≃ ActualFixedChainPlacements c hn := by
  classical
  by_cases hpositive :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi
  · simpa [CodeFiberParams, hpositive] using
      actualFixedChainPlacementEquiv c hn hpositive
  · have hempty :
        (decodeCode c hn).frontier.lo = (decodeCode c hn).frontier.hi := by
      have := (decodeCode c hn).frontier.noncrossing
      omega
    simpa [CodeFiberParams, hpositive] using
      fullCarrierFixedChainPlacementEquiv c hn hempty

/-- For `n >= 3`, origin classification upgrades the code/placement pair
to a complete generated execution record. This is not merely an equivalence
between formal targets and codes. -/
noncomputable def codePlacementEquivActualSummaries
    (hn : 3 ≤ n) :
    (Σ c : Code (n - 2), ActualFixedChainPlacements c (by omega)) ≃
      ActualRegisteredSummaries n := by
  let assemble :
      (Σ c : Code (n - 2), ActualFixedChainPlacements c (by omega)) →
        ActualRegisteredSummaries n := fun ⟨c, P⟩ =>
    ⟨⟨P.1, (registrationExecution n).origin, decodeChain c (by omega)⟩, by
      obtain ⟨word, hregistered, hchain, hplaced⟩ := P.2
      have horigin := actual_registered_origin_unique word hn hregistered
      have hstate :
          run (selectedPair n) (singletonExecution n) word =
            ⟨P.1, (registrationExecution n).origin, decodeChain c (by omega)⟩ := by
        cases hrun : run (selectedPair n) (singletonExecution n) word with
        | mk placed origin chain =>
            simp only [hrun] at hplaced horigin hchain ⊢
            simp only [Execution.mk.injEq]
            exact ⟨hplaced, horigin, hchain⟩
      exact ⟨⟨word, hstate⟩, by
        rw [registration_origin (show 2 ≤ n by omega)]
        rfl⟩⟩
  apply Equiv.ofBijective assemble
  constructor
  · intro ⟨c, P⟩ ⟨d, Q⟩ heq
    have hchain : decodeChain c (by omega : 2 ≤ n) =
        decodeChain d (by omega : 2 ≤ n) :=
      congrArg (fun s : ActualRegisteredSummaries n => s.1.chain) heq
    have hcode := decodeChain_injective (by omega : 2 ≤ n) hchain
    cases hcode
    have hplace : P.1 = Q.1 :=
      congrArg (fun s : ActualRegisteredSummaries n => s.1.placed) heq
    have hP : P = Q := Subtype.ext hplace
    cases hP
    rfl
  · intro s
    obtain ⟨word, hword⟩ := s.2.1
    have hregistered :
        (run (selectedPair n) (singletonExecution n) word).origin.isSome = true := by
      rw [hword]
      exact s.2.2
    obtain ⟨c, hchain⟩ :=
      actual_chain_in_decode_range word (by omega : 2 ≤ n) hregistered
    let P : ActualFixedChainPlacements c (by omega : 2 ≤ n) :=
      ⟨s.1.placed, ⟨word, hregistered, hchain, congrArg Execution.placed hword⟩⟩
    refine ⟨⟨c, P⟩, ?_⟩
    apply Subtype.ext
    have horigin := actual_registered_origin_unique word hn hregistered
    rw [hword] at horigin hchain
    change (⟨s.1.placed, (registrationExecution n).origin,
      decodeChain c (by omega)⟩ : Execution n (ZMod n)) = s.1
    cases hs : s.1 with
    | mk placed origin chain =>
        simp only [hs] at horigin hchain ⊢
        simp only [Execution.mk.injEq]
        exact ⟨trivial, horigin.symm, hchain.symm⟩

/-- The global, actual-summary version of the dependent fiber
classification. The older checkpoint-stratified `TotalParams` is a separate
finite counting presentation, not silently identified with this sigma type. -/
noncomputable def actualSummaryCodeFiberEquiv
    (hn : 3 ≤ n) :
    (Σ c : Code (n - 2), CodeFiberParams c (by omega)) ≃
      ActualRegisteredSummaries n :=
  (Equiv.sigmaCongrRight fun c =>
    codeFiberPlacementEquiv c (by omega)).trans
      (codePlacementEquivActualSummaries hn)

end RegisteredAbsorptionChains
