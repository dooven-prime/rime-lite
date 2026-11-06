import RegisteredAbsorptionChains.TotalSummaryAssembly
import RegisteredAbsorptionChains.TotalParameters
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- The positive rank in a realizable rank tuple never exceeds the number
of outside atoms: its cut set has `t-1` elements in a `k-1`-point carrier. -/
theorem positiveRankFiberParams_rank_le
    {n k : ℕ} (hk : 0 < k)
    (p : PositiveRankFiberParams n k) : p.1.1 ≤ k := by
  obtain ⟨⟨t, params⟩, ht⟩ := p
  have hcuts :
      params.2.1.1.card = t - 1 := params.2.1.2
  have hbound : params.2.1.1.card ≤ k - 1 := by
    calc
      params.2.1.1.card ≤ (Finset.univ : Finset (Fin (k - 1))).card :=
        Finset.card_le_card (Finset.subset_univ _)
      _ = k - 1 := by simp
  change t ≤ k
  change 0 < t at ht
  omega

/-- Replace the unbounded-looking positive sigma rank by `i=t-1 : Fin k`.
This is an equivalence of the actual parameter types, not only a card sum. -/
noncomputable def positiveRankFiberParamsEquiv
    (n k : ℕ) (hk : 0 < k) :
    PositiveRankFiberParams n k ≃ FiberParams n k := by
  let encode : PositiveRankFiberParams n k → FiberParams n k :=
    fun ⟨⟨t, params⟩, ht⟩ =>
    ⟨⟨t - 1, by
        have hle := positiveRankFiberParams_rank_le hk
          (⟨⟨t, params⟩, ht⟩ : PositiveRankFiberParams n k)
        change t ≤ k at hle
        change 0 < t at ht
        omega⟩,
      by
        change 0 < t at ht
        have heq : t - 1 + 1 = t := by omega
        simpa only [heq] using params⟩
  apply Equiv.ofBijective encode
  constructor
  · intro first second heq
    obtain ⟨⟨t, firstParams⟩, ht⟩ := first
    obtain ⟨⟨u, secondParams⟩, hu⟩ := second
    have hindex : t - 1 = u - 1 := by
      have h := congrArg (fun x : FiberParams n k => x.1.1) heq
      change t - 1 = u - 1 at h
      exact h
    change 0 < t at ht
    change 0 < u at hu
    have htu : t = u := by omega
    subst u
    have hparams : firstParams = secondParams := by
      simpa [encode, Sigma.mk.injEq] using heq
    cases hparams
    rfl
  · rintro ⟨i, params⟩
    refine ⟨⟨⟨i.1 + 1, params⟩, Nat.succ_pos _⟩, ?_⟩
    apply Sigma.ext
    · apply Fin.ext
      simp [encode]
    · simp [encode]

/-- The finite presentation of each code-indexed fiber. -/
noncomputable abbrev FiniteCodeFiberParams {n : ℕ} [NeZero n]
    (c : Code (n - 2)) (hn : 2 ≤ n) :=
  if (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi then
    FiberParams n
      ((decodeCode c hn).frontier.hi - (decodeCode c hn).frontier.lo)
  else ZMod n

noncomputable instance finiteCodeFiberFintype {n : ℕ} [NeZero n]
    (c : Code (n - 2)) (hn : 2 ≤ n) :
    Fintype (FiniteCodeFiberParams c hn) := by
  classical
  dsimp [FiniteCodeFiberParams]
  split <;> infer_instance

noncomputable def finiteCodeFiberEquiv {n : ℕ} [NeZero n]
    (c : Code (n - 2)) (hn : 2 ≤ n) :
    FiniteCodeFiberParams c hn ≃ CodeFiberParams c hn := by
  classical
  by_cases hpositive :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi
  · have hk : 0 < (decodeCode c hn).frontier.hi -
        (decodeCode c hn).frontier.lo := Nat.sub_pos_of_lt hpositive
    simpa [FiniteCodeFiberParams, CodeFiberParams, hpositive] using
      (positiveRankFiberParamsEquiv n _ hk).symm
  · simpa [FiniteCodeFiberParams, CodeFiberParams, hpositive] using
      (Equiv.refl (ZMod n))

noncomputable instance actualFixedChainPlacementsFintype
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n) :
    Fintype (ActualFixedChainPlacements c hn) :=
  Fintype.ofEquiv (FiniteCodeFiberParams c hn)
    ((finiteCodeFiberEquiv c hn).trans (codeFiberPlacementEquiv c hn))

/-- The fixed-chain positive-complement formula now counts literal
placements reached by generated histories. -/
theorem card_actualFixedChainPlacements_positive
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n)
    (hpositive :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    Fintype.card (ActualFixedChainPlacements c hn) =
      n * (n + ((decodeCode c hn).frontier.hi -
        (decodeCode c hn).frontier.lo) - 2).choose
          ((decodeCode c hn).frontier.hi -
            (decodeCode c hn).frontier.lo) := by
  classical
  have hk : 0 < (decodeCode c hn).frontier.hi -
      (decodeCode c hn).frontier.lo := Nat.sub_pos_of_lt hpositive
  calc
    Fintype.card (ActualFixedChainPlacements c hn) =
        Fintype.card (FiniteCodeFiberParams c hn) :=
      (Fintype.card_congr
        ((finiteCodeFiberEquiv c hn).trans
          (codeFiberPlacementEquiv c hn))).symm
    _ = _ := by
      simpa [FiniteCodeFiberParams, hpositive] using
        card_fiberParams n _ (by omega) hk

/-- When the decoded carrier is complete, only its `n` physical phases
remain in the actual fixed-chain placement fiber. -/
theorem card_actualFixedChainPlacements_full
    {n : ℕ} [NeZero n] (c : Code (n - 2)) (hn : 2 ≤ n)
    (hempty :
      (decodeCode c hn).frontier.lo = (decodeCode c hn).frontier.hi) :
    Fintype.card (ActualFixedChainPlacements c hn) = n := by
  classical
  have hpositive : ¬(decodeCode c hn).frontier.lo <
      (decodeCode c hn).frontier.hi := by omega
  calc
    Fintype.card (ActualFixedChainPlacements c hn) =
        Fintype.card (FiniteCodeFiberParams c hn) :=
      (Fintype.card_congr
        ((finiteCodeFiberEquiv c hn).trans
          (codeFiberPlacementEquiv c hn))).symm
    _ = n := by simp [FiniteCodeFiberParams, hpositive]

/-- Actual registered summaries, not just formal code targets, are in
bijection with a finite dependent family of code/placement parameters. -/
noncomputable def actualSummaryFiniteParamsEquiv {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) :
    (Σ c : Code (n - 2), FiniteCodeFiberParams c (by omega)) ≃
      ActualRegisteredSummaries n :=
  (Equiv.sigmaCongrRight fun c => finiteCodeFiberEquiv c (by omega)).trans
    (actualSummaryCodeFiberEquiv hn)

private theorem two_le_of_fact_three {n : ℕ} [Fact (3 ≤ n)] : 2 ≤ n := by
  have hn : 3 ≤ n := Fact.out
  omega

noncomputable instance actualRegisteredSummariesFintype
    {n : ℕ} [NeZero n] [Fact (3 ≤ n)] :
    Fintype (ActualRegisteredSummaries n) :=
  Fintype.ofEquiv
    (Σ c : Code (n - 2), FiniteCodeFiberParams c two_le_of_fact_three)
    (actualSummaryFiniteParamsEquiv Fact.out)

/-- The actual-summary count is the sum of the already proved finite fiber
counts. Regrouping this by the last checkpoint gives the closed expression. -/
theorem card_actualRegisteredSummaries_code_sum
    {n : ℕ} [NeZero n] [Fact (3 ≤ n)] :
    Fintype.card (ActualRegisteredSummaries n) =
      ∑ c : Code (n - 2),
        if (decodeCode c two_le_of_fact_three).frontier.lo <
            (decodeCode c two_le_of_fact_three).frontier.hi then
          n * (n + ((decodeCode c two_le_of_fact_three).frontier.hi -
            (decodeCode c two_le_of_fact_three).frontier.lo) - 2).choose
              ((decodeCode c two_le_of_fact_three).frontier.hi -
                (decodeCode c two_le_of_fact_three).frontier.lo)
        else n := by
  classical
  calc
    Fintype.card (ActualRegisteredSummaries n) =
        Fintype.card (Σ c : Code (n - 2),
          FiniteCodeFiberParams c two_le_of_fact_three) :=
      (Fintype.card_congr (actualSummaryFiniteParamsEquiv Fact.out)).symm
    _ = ∑ c : Code (n - 2),
          Fintype.card (FiniteCodeFiberParams c two_le_of_fact_three) :=
      Fintype.card_sigma
    _ = _ := by
      apply Finset.sum_congr rfl
      intro c _
      by_cases hpositive :
          (decodeCode c two_le_of_fact_three).frontier.lo <
            (decodeCode c two_le_of_fact_three).frontier.hi
      · have hk : 0 < (decodeCode c two_le_of_fact_three).frontier.hi -
            (decodeCode c two_le_of_fact_three).frontier.lo :=
          Nat.sub_pos_of_lt hpositive
        simpa [FiniteCodeFiberParams, hpositive] using
          card_fiberParams n _ (by
            have hn : 3 ≤ n := Fact.out
            omega) hk
      · simp [FiniteCodeFiberParams, hpositive]

end RegisteredAbsorptionChains
