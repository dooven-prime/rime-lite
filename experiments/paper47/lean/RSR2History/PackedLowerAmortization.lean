import RSR2History.PackedLowerMinimum

/-!
Budget accounting for packed lower extraction.

This module formalizes the exact budget released by lower prefusion and the
weaker compensated comparison sufficient for delayed-family domination. It
does not prove the geometric packed-lower amortization inequality.
-/

namespace RSR2History

private theorem twice_choose_two (k : Nat) : 2*k.choose 2 = k*(k-1) := by
  obtain ⟨q, hq⟩ := Nat.even_mul_pred_self k
  rw [Nat.choose_two_right]
  omega

/-- Eliminating one lower fusion increases the transfer count from `t` to
`t+1` and uses exactly this increment of upper-cursor budget. -/
theorem packedUpperBudget_successor
    {n t : Nat} (ht : 2 ≤ t) (_htn : t+1 ≤ n) :
    packedUpperBudget n (t+1) = packedUpperBudget n t + (2*n+t+1) := by
  have ht' : 2 ≤ t+1 := by omega
  have ha := packedUpperBudget_eq_choose (n := n) (t := t) ht
  have hb := packedUpperBudget_eq_choose (n := n) (t := t+1) ht'
  have h1 := twice_choose_two (t+1)
  have h2 := twice_choose_two (t+2)
  have hs1 := Nat.sub_add_cancel (show 3 ≤ 2*t by omega)
  have hs2 := Nat.sub_add_cancel (show 3 ≤ 2*(t+1) by omega)
  simp only [Nat.add_sub_cancel] at h1
  have hpred : t+2-1 = t+1 := by omega
  rw [hpred] at h2
  rw [ha, hb]
  nlinarith

/-- The released budget has the convenient quadratic form in the number of
lower prefusions `r=n-t`. -/
theorem packedUpperBudget_release_prefusions
    {n t : Nat} (ht : 2 ≤ t) (htn : t ≤ n) :
    (n-t)*(5*n+t+1)/2 = 3*n*(n-t) - (n-t).choose 2 := by
  have hc := twice_choose_two (n-t)
  have hnt := Nat.sub_add_cancel htn
  have hnonneg : (n-t).choose 2 ≤ 3*n*(n-t) := by
    have hmul : (n-t)*(n-t-1) ≤ 6*n*(n-t) := by
      have hr : n-t ≤ n := by omega
      have h2 : n-t-1 ≤ 2*n := by omega
      nlinarith
    nlinarith
  have he : (n-t)*(5*n+t+1) =
      2*(3*n*(n-t) - (n-t).choose 2) := by
    have hs := Nat.sub_add_cancel hnonneg
    by_cases hz : n-t = 0
    · simp [hz] at *
    · have hp := Nat.sub_add_cancel (show 1 ≤ n-t by omega)
      nlinarith
  omega

/-- Successive budget releases differ by `2*n+t+1`. This is the arithmetic
increment a fusion-elimination induction would need to pay. -/
theorem packedUpperBudget_release_succ
    {n t : Nat} (ht : 2 ≤ t) (htn : t+1 ≤ n) :
    (n-t)*(5*n+t+1)/2 =
      (n-(t+1))*(5*n+(t+1)+1)/2 + (2*n+t+1) := by
  have hleft := packedUpperBudget_release (n := n) (t := t) ht (by omega)
  have hright := packedUpperBudget_release (n := n) (t := t+1) (by omega) htn
  have hstep := packedUpperBudget_successor ht htn
  have hself : packedUpperBudget n n =
      packedUpperBudget n (t+1) +
        (n-(t+1))*(5*n+(t+1)+1)/2 := hright
  rw [hleft, hstep] at hself
  omega

/-- The original pure lower-cost comparison is sufficient for the one-block
delayed benchmark. The replay budget is kept as an explicit premise. -/
theorem packed_replay_delayed_bound_of_lower_comparison
    {n t length lower K : Nat} (ht : 2 ≤ t) (htn : t ≤ n)
    (hreplay : length ≤ lower + packedUpperBudget n t + (n-1))
    (hlower : lower ≤ K + (n-t)*(5*n+t+1)/2) :
    length ≤ K + packedUpperBudget n n + (n-1) := by
  have hrelease := packedUpperBudget_release ht htn
  omega

/-- Compensated lower slack is enough: tree defect and initial cursor slack
may pay for a packed lower path that exceeds the pure released budget. -/
theorem packed_replay_delayed_bound_of_compensated_comparison
    {n t length lower K defect cursorSlack : Nat}
    (ht : 2 ≤ t) (htn : t ≤ n)
    (hreplay : length + defect + cursorSlack ≤
      lower + packedUpperBudget n t + (n-1))
    (hlower : lower ≤ K + (n-t)*(5*n+t+1)/2 + defect + cursorSlack) :
    length ≤ K + packedUpperBudget n n + (n-1) := by
  have hrelease := packedUpperBudget_release ht htn
  have hself := packedUpperBudget_self (le_trans ht htn)
  omega

/-- In the one-prefusion stratum, the released upper budget is exactly `3*n`.
This is a sufficient conditional criterion, not a proved geometric bound on
`packedLowerCost`. -/
theorem packed_replay_one_prefusion_bound
    {n length lower K defect cursorSlack : Nat} (hn : 3 ≤ n)
    (hreplay : length + defect + cursorSlack ≤
      lower + packedUpperBudget n (n-1) + (n-1))
    (hlower : lower ≤ K + 3*n + defect + cursorSlack) :
    length ≤ K + packedUpperBudget n n + (n-1) := by
  have hrelease := packedUpperBudget_release_one hn
  omega

/-- Exact integer slack decomposition for a replay with lower cost `μ`,
cursor cost `C`, and final phase `p`. `e` is the one-block partition cost;
`D` is total observation premium and `λ` is the corresponding minimum
history distance. The theorem is accounting only: all four slacks are taken
from the supplied replay and minimum-distance facts. -/
theorem packed_replay_delayed_slack_identity
    {n t K μ C p e J D distance L : Nat}
    (hbudget : packedUpperBudget n n =
      packedUpperBudget n t + (n-t)*(5*n+t+1)/2)
    (hdelayed : J + e = K + packedUpperBudget n n + (n-1))
    (hpremium : D + e = distance)
    (hreplay : L = μ + C + p) :
    (J : Int) - (D : Int) =
      ((K + (n-t)*(5*n+t+1)/2 : Nat) : Int) - (μ : Int) +
      ((packedUpperBudget n t : Nat) : Int) - (C : Int) +
      ((n-1 : Nat) : Int) - (p : Int) +
      (L : Int) - (distance : Int) := by
  omega

/-- If the pure lower comparison holds, all four terms in the exact slack
identity are nonnegative provided the replay schedule and endpoint phase fit
their proved budgets. -/
theorem packed_replay_delayed_dominates_of_component_budgets
    {n t K μ C p e J D distance L : Nat}
    (hbudget : packedUpperBudget n n =
      packedUpperBudget n t + (n-t)*(5*n+t+1)/2)
    (hdelayed : J + e = K + packedUpperBudget n n + (n-1))
    (hpremium : D + e = distance)
    (hreplay : L = μ + C + p)
    (hlower : μ ≤ K + (n-t)*(5*n+t+1)/2)
    (hcursor : C ≤ packedUpperBudget n t)
    (hphase : p ≤ n-1)
    (hminimum : distance ≤ L) : D ≤ J := by
  have hidentity := packed_replay_delayed_slack_identity hbudget hdelayed hpremium hreplay
  omega

/-- The weaker compensated condition can be read directly as an upper-cursor
surplus requirement. This records the accounting available for later
fusion-elimination proofs. -/
theorem packed_cursor_surplus_covers_defects
    {n t C defect cursorSlack : Nat}
    (hcursor : C + defect + cursorSlack ≤ packedUpperBudget n t) :
    defect + cursorSlack ≤ packedUpperBudget n t - C := by
  omega


/-- Exact normalization of the delayed-family benchmark to the same upper
budget and the independently proved one-block partition minimum. -/
theorem delayedChainTotalPremiumMaximum_add_singleBlockCost
    (n : Nat) (hn : 3 ≤ n) :
    delayedChainTotalPremiumMaximum n hn + (2*n-3) =
      maxLowerExtractionCost n (by omega) + packedUpperBudget n n + (n-1) := by
  have hchoose : 5*n.choose 2 = (5*n*(n-1))/2 := by
    obtain ⟨q, hq⟩ := Nat.even_mul_pred_self n
    rw [Nat.mul_assoc, hq, Nat.choose_two_right, hq]
    omega
  rw [packedUpperBudget_self (by omega), hchoose,
    delayedChainTotalPremiumMaximum_eq n hn]
  have hbase : n ≤ (5*n*(n-1))/2 := by
    have hp : 2 ≤ n-1 := by omega
    have hm : 2*n ≤ 5*n*(n-1) := by nlinarith
    omega
  omega

section ActualReplay
open RSR2.Parametric AllRTransfer
variable {n : Nat} [NeZero n]

/-- The four signed slacks all come from the same optimal-lower replay of
this actual observation. Lower slack may be negative. The other three are
nonnegative; the upper one also dominates the original tree's defects. -/
theorem singleBlock_packed_minimum_slack_decomposition
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ (T : UpperFusionTree n) (C phase : Nat) (replay : List Letter),
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      runLogged n (by omega) (seed n) replay = some (Q,H) ∧
      replay.length = packedLowerCost n (by omega) (packedLowerLog H) + C + phase ∧
      C + T.leftBranchDefect + T.initialCursorSlack ≤
        packedUpperBudget n (logTransferCount H) ∧
      phase ≤ n-1 ∧
      historyDistance n (by omega) Q H ⟨word,hexec⟩ ≤ replay.length ∧
      (delayedChainTotalPremiumMaximum n hn : Int) -
        (totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ : Int) =
        ((maxLowerExtractionCost n (by omega) +
          (n-logTransferCount H)*(5*n+logTransferCount H+1)/2 : Nat) : Int) -
          (packedLowerCost n (by omega) (packedLowerLog H) : Int) +
        (packedUpperBudget n (logTransferCount H) : Int) - (C : Int) +
        ((n-1 : Nat) : Int) - (phase : Int) +
        (replay.length : Int) -
          (historyDistance n (by omega) Q H ⟨word,hexec⟩ : Int) := by
  obtain ⟨T, site, cf, phase, replay, schedule, trace, hr, hlen, hphase, hc⟩ :=
    singleBlock_packed_minimum_replay_exact (by omega) word hexec hblocks ht
  have hd : historyDistance n (by omega) Q H ⟨word,hexec⟩ ≤ replay.length :=
    minimumWordLength_le _ ⟨word,hexec⟩ hr
  refine ⟨T, schedule.cost, phase, replay, trace, hr, hlen, hc, hphase, hd, ?_⟩
  exact packed_replay_delayed_slack_identity
    (packedUpperBudget_release ht (singleton_transfer_count_le n (by omega) hexec))
    (delayedChainTotalPremiumMaximum_add_singleBlockCost n hn)
    (singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks)
    hlen

/-- A compensated lower comparison for the tree annotated by the same
actual observation is enough. This implication does not assert that the
comparison holds for every feasible packed log. -/
theorem singleBlock_packed_minimum_compensated_criterion
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H) :
    ∃ T : UpperFusionTree n,
      UpperForestTrace (seed n) 0 [] H Q (logTransferCount H) [T] ∧
      (packedLowerCost n (by omega) (packedLowerLog H) ≤
        maxLowerExtractionCost n (by omega) +
          (n-logTransferCount H)*(5*n+logTransferCount H+1)/2 +
            T.leftBranchDefect + T.initialCursorSlack →
        totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ ≤
          delayedChainTotalPremiumMaximum n hn) := by
  obtain ⟨T, trace, hd⟩ :=
    singleBlock_packed_minimum_historyDistance (by omega) word hexec hblocks ht
  refine ⟨T, trace, ?_⟩
  intro hlower
  have hc := packed_replay_delayed_bound_of_compensated_comparison ht
    (singleton_transfer_count_le n (by omega) hexec) hd hlower
  have hp := singleBlock_totalPremium_add_partitionCost n (by omega) word hexec hblocks
  have hj := delayedChainTotalPremiumMaximum_add_singleBlockCost n hn
  omega

/-- The stronger pure lower comparison yields a same-observation word and
then the actual delayed-family premium bound. It is stated only conditionally
on this still-independent geometric lower estimate. -/
theorem singleBlock_packed_minimum_delayed_of_lower_cost_comparison
    (hn : 3 ≤ n) {Q : Placement n} {H : List (EffectiveEvent n)}
    (word : List Letter)
    (hexec : runLogged n (by omega) (seed n) word = some (Q,H))
    (hblocks : unorderedPacketBlocks n Q = {Finset.univ})
    (ht : 2 ≤ logTransferCount H)
    (hlower : packedLowerCost n (by omega) (packedLowerLog H) ≤
      maxLowerExtractionCost n (by omega) +
        (n-logTransferCount H)*(5*n+logTransferCount H+1)/2) :
    totalObservationPremium n (by omega) ⟨(Q,H),⟨word,hexec⟩⟩ ≤
      delayedChainTotalPremiumMaximum n hn := by
  obtain ⟨T, _, criterion⟩ :=
    singleBlock_packed_minimum_compensated_criterion hn word hexec hblocks ht
  exact criterion (by omega)

end ActualReplay

end RSR2History
