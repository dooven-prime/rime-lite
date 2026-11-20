import RSR2History.CombRootForestNormalForm
import RSR2History.StrategyIndependentSlack

/-!
Joint cursor and terminal-routing costs for the transfer-first, single-comb
subclass. The joint budget is an explicit geometric hypothesis.
-/
namespace RSR2History
open RSR2.Parametric AllRTransfer

/-- All singleton transfers occur in one prefix, followed by upper fusions. -/
def SingletonTransfersFirst (H : List (EffectiveEvent n)) : Prop :=
  ∃ (z : List (Fin n)) (tail : List (EffectiveEvent n)),
    H = z.map (fun a : Fin n => EffectiveEvent.transfer {a}) ++ tail ∧
    ∀ e ∈ tail, ∃ A B : Finset (Fin n),
      e = EffectiveEvent.fusion true A B (A ∪ B)

/-- A replay of the original log to the literal target, with a single comb
and singleton roots elsewhere. The schedule and the final silent word are
data of the same account. -/
structure CombJointTerminalAccount (n : Nat) (hn : 1 < n)
    (Q : Placement n) (H : List (EffectiveEvent n)) (k : Nat) where
  forestAccount : ForestReplayAccount n hn Q H
  forestShape : CombRootForestNormalForm forestAccount.terminal k
  transfers_first : SingletonTransfersFirst H

/-- The right side of the joint budget, with the minimum for the same
unordered partition supplied as `partitionCost`. -/
def combJointTerminalCap (n k partitionCost : Nat) : Int :=
  (partitionCost : Int) + (5 * n.choose 2 : Nat) -
    2 * (n : Int) - k + 3 - ((k - 1).choose 2 : Nat)

namespace CombJointTerminalAccount
variable {n : Nat} {hn : 1 < n} {Q : Placement n}
  {H : List (EffectiveEvent n)} {k : Nat}

/-- The joint charge uses the final cursor of the replay and the silent route
from the intermediate placement that the replay actually reaches. -/
def jointTerminalCost (r : CombJointTerminalAccount n hn Q H k) : Int :=
  (n : Int) * r.forestAccount.schedule.windings +
    r.forestAccount.finish.length - r.forestAccount.finalCursor.val +
    (r.forestAccount.site 0).val

noncomputable def cap (r : CombJointTerminalAccount n hn Q H k) : Int :=
  combJointTerminalCap n k r.forestAccount.partitionCost

theorem terminal_root_count (r : CombJointTerminalAccount n hn Q H k) :
    r.forestAccount.terminal.length = n - k + 1 :=
  r.forestShape.length_eq r.forestAccount.leaf_count

theorem event_count (r : CombJointTerminalAccount n hn Q H k) :
    H.length = n + k - 1 := by
  have he := r.forestAccount.schedule.forest_event_count
  rw [r.terminal_root_count] at he
  have hk := r.forestShape.two_le
  have hkn := r.forestShape.lt_sites
  omega

/-- Exact cursor payment, with the final cursor transferred to the left
side so the identity can be stated over naturals. -/
theorem cursor_payment (r : CombJointTerminalAccount n hn Q H k) :
    r.forestAccount.schedule.cost + r.forestAccount.finalCursor.val =
      n + k - 1 + (k - 1).choose 2 +
        n * r.forestAccount.schedule.windings +
        (r.forestAccount.site 0).val := by
  rw [r.forestAccount.schedule.forest_payment,
    r.event_count, r.forestShape.gapDebt_eq]

/-- The lower extraction, cursor replay and final route belong to one word;
the joint charge does not charge any of its letters a second time. -/
theorem word_payment (r : CombJointTerminalAccount n hn Q H k) :
    (r.forestAccount.word.length : Int) =
      r.forestAccount.extractionCost + (n : Int) + k - 1 +
        ((k - 1).choose 2 : Nat) + r.jointTerminalCost := by
  have hl := r.forestAccount.length_eq
  change r.forestAccount.word.length =
    r.forestAccount.extractionCost + r.forestAccount.schedule.cost +
      r.forestAccount.finish.length at hl
  have hp := r.cursor_payment
  have lZ := congrArg (fun x : Nat => (x : Int)) hl
  have pZ := congrArg (fun x : Nat => (x : Int)) hp
  push_cast at lZ pZ
  unfold jointTerminalCost
  omega

theorem geometricSlack_eq_cap_sub_jointTerminalCost
    (r : CombJointTerminalAccount n hn Q H k) :
    r.forestAccount.geometricSlack = r.cap - r.jointTerminalCost := by
  have hroots : (r.forestAccount.terminal.length : Int) = (n : Int) - k + 1 := by
    rw [r.terminal_root_count, Nat.cast_add, Int.ofNat_sub r.forestShape.lt_sites.le]
    rfl
  unfold ForestReplayAccount.geometricSlack ForestReplayAccount.jointCharge
  rw [packedUpperBudget_self (by omega), hroots, r.forestShape.gapDebt_eq]
  unfold cap combJointTerminalCap jointTerminalCost
  ring

/-- The joint budget is exactly nonnegative geometric slack for this replay. -/
theorem joint_budget_iff_geometricSlack_nonneg
    (r : CombJointTerminalAccount n hn Q H k) :
    r.jointTerminalCost ≤ r.cap ↔ 0 ≤ r.forestAccount.geometricSlack := by
  rw [r.geometricSlack_eq_cap_sub_jointTerminalCost]
  omega

/-- The joint budget bounds the length of the replay itself, while retaining
the extraction deficit of the original transfer order. -/
theorem replay_length_of_joint_budget
    (r : CombJointTerminalAccount n hn Q H k) (hn3 : 3 ≤ n)
    (hbudget : r.jointTerminalCost ≤ r.cap) :
    r.forestAccount.word.length +
        (maxLowerExtractionCost n hn - r.forestAccount.extractionCost) ≤
      r.forestAccount.partitionCost + delayedChainTotalPremiumMaximum n hn3 := by
  have hgeo : 0 ≤ r.forestAccount.geometricSlack :=
    r.joint_budget_iff_geometricSlack_nonneg.mp hbudget
  have hs := r.forestAccount.relative_slack hn3
  unfold ForestReplayAccount.relativeBase at hs
  unfold ForestReplayAccount.geometricSlack at hgeo
  have hp := r.forestAccount.premium_balance
  have hl := r.forestAccount.replayExcess_balance
  omega

theorem delayed_dominance_of_joint_budget
    (r : CombJointTerminalAccount n hn Q H k) (hn3 : 3 ≤ n)
    (hbudget : r.jointTerminalCost ≤ r.cap) :
    r.forestAccount.premium +
        (maxLowerExtractionCost n hn - r.forestAccount.extractionCost) ≤
      delayedChainTotalPremiumMaximum n hn3 := by
  have hw := r.replay_length_of_joint_budget hn3 hbudget
  have hp := r.forestAccount.premium_balance
  have hm := r.forestAccount.historyCost_le_word
  omega

/-- Choosing the shorter of the supplied history and the certified replay
gives a non-increasing compression within the same actual observation. -/
theorem same_observation_compression_of_joint_budget
    (r : CombJointTerminalAccount n hn Q H k) (hn3 : 3 ≤ n)
    (hbudget : r.jointTerminalCost ≤ r.cap)
    (word : List Letter)
    (hrun : runLogged n hn (seed n) word = some (Q,H)) :
    ∃ word' : List Letter,
      runLogged n hn (seed n) word' = some (Q,H) ∧
      word'.length ≤ word.length ∧
      word'.length +
          (maxLowerExtractionCost n hn - r.forestAccount.extractionCost) ≤
        r.forestAccount.partitionCost + delayedChainTotalPremiumMaximum n hn3 := by
  have hb := r.replay_length_of_joint_budget hn3 hbudget
  by_cases hshort : word.length ≤ r.forestAccount.word.length
  · exact ⟨word, hrun, le_rfl, by omega⟩
  · exact ⟨r.forestAccount.word, r.forestAccount.actual_run, by omega, hb⟩

end CombJointTerminalAccount

/-- Arithmetic check for the recorded four-site account. -/
theorem comb_four_point_boundary_check :
    combJointTerminalCap 4 3 3 = (4 : Int) * 4 + 8 - 0 + 0 ∧
      combJointTerminalCap 4 3 2 + 1 = combJointTerminalCap 4 3 3 := by
  norm_num [combJointTerminalCap, Nat.choose]

end RSR2History
