import RegisteredAbsorptionChains.CutBoundaryLift
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n t : ℕ} [NeZero n]

/-- Every code's actual clean witness can be continued to any legal
fixed-chain outside cut and placement. The resulting origin and selected
chain are read from the same complete execution. -/
theorem code_fiber_target_reachable
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (data : ValidFiberPlacement n t)
    (hu : data.u = (decodeCode c hn).frontier.lo)
    (hv : data.v = (decodeCode c hn).frontier.hi) :
    ∃ word : List Letter,
      let s := run (selectedPair n) (singletonExecution n) word
      s.origin = (registrationExecution n).origin ∧
      s.chain = decodeChain c hn ∧
      s.placed = data.target := by
  obtain ⟨preword, horigin, hchain, hinside, hclean⟩ :=
    realize_clean_code c hn
  let F := selectedPair n
  let f := (decodeCode c hn).frontier
  let start := run F (singletonExecution n) preword
  have hreach : ReachableExecution F start := ⟨preword, rfl⟩
  have hreg : start.origin.isSome = true := by
    rw [horigin, registration_origin hn]
    rfl
  have hsel : F.Nonempty := ⟨0, by simp [F, selectedPair]⟩
  obtain ⟨suffix, hsuffix⟩ :=
    allCut_realize_target F data f hu hv start hreach hreg hsel hinside hclean
  refine ⟨preword ++ suffix, ?_⟩
  dsimp
  rw [run_append, hsuffix]
  exact ⟨horigin, hchain, rfl⟩

/-- The same result with native finite rank parameters. The cut, phase,
and occupied-site choices are all realized by one actual word. -/
theorem code_rank_params_reachable
    {k : ℕ} (c : Code (n - 2)) (hn : 2 ≤ n)
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t)
    (hlo : u = (decodeCode c hn).frontier.lo)
    (hhi : u + k = (decodeCode c hn).frontier.hi) :
    ∃ word : List Letter,
      let s := run (selectedPair n) (singletonExecution n) word
      s.origin = (registrationExecution n).origin ∧
      s.chain = decodeChain c hn ∧
      s.placed =
        (ValidFiberPlacement.ofRankParams u hu huk hk ht params).target := by
  exact code_fiber_target_reachable c hn
    (ValidFiberPlacement.ofRankParams u hu huk hk ht params) hlo hhi

end RegisteredAbsorptionChains
