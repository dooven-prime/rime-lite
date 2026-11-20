import FusionLogCompression.M3GapFlow
import FusionLogCompression.M3GapBatch
import FusionLogCompression.M3LinearSchedule

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n r : ℕ} [NeZero n] [NeZero r]
variable {α : Type*} [DecidableEq α]

namespace BatchPlacementPlan

def append {F : Finset α} {s : Execution n α}
    {middle target : Placement n (Finset α)}
    (first : BatchPlacementPlan F s middle)
    (second : BatchPlacementPlan F (withPlaced s middle) target) :
    BatchPlacementPlan F s target :=
  match first with
  | .done _ => second
  | .step s move tail => .step s move (append tail second)

theorem append_batches {F : Finset α} {s : Execution n α}
    {middle target : Placement n (Finset α)}
    (first : BatchPlacementPlan F s middle)
    (second : BatchPlacementPlan F (withPlaced s middle) target) :
    (first.append second).batches = first.batches + second.batches := by
  cases first with
  | done s => exact (Nat.zero_add _).symm
  | step s move tail =>
      change (tail.append second).batches + 1 = (tail.batches + 1) + second.batches
      rw [append_batches tail second]
      exact Nat.add_right_comm _ _ _

theorem append_transfers {F : Finset α} {s : Execution n α}
    {middle target : Placement n (Finset α)}
    (first : BatchPlacementPlan F s middle)
    (second : BatchPlacementPlan F (withPlaced s middle) target) :
    (first.append second).transfers = first.transfers + second.transfers := by
  cases first with
  | done s => exact (Nat.zero_add _).symm
  | step s move tail =>
      change (tail.append second).transfers + move.f =
        (tail.transfers + move.f) + second.transfers
      rw [append_transfers tail second]
      exact Nat.add_right_comm _ _ _

theorem done_at (F : Finset α) (s : Execution n α)
    (target : Placement n (Finset α)) (source : s.placed = target) :
    ∃ plan : BatchPlacementPlan F s target,
      plan.batches = 0 ∧ plan.transfers = 0 := by
  subst target
  exact ⟨.done s, rfl, rfl⟩

end BatchPlacementPlan

/-- Execute all edges after `cut`, leaving that zero-flow edge until last. -/
def cutIndex (cut : ZMod r) (k : ℕ) : ZMod r := cut + 1 + k

theorem cutIndex_next (cut : ZMod r) (k : ℕ) :
    cutIndex cut (k + 1) = cutIndex cut k + 1 := by
  simp [cutIndex, Nat.cast_add, add_assoc]

theorem cutIndex_injective_below (cut : ZMod r) {i j : ℕ}
    (hi : i < r) (hj : j < r)
    (eq : cutIndex cut i = cutIndex cut j) : i = j := by
  have hcast : (i : ZMod r) = (j : ZMod r) := add_left_cancel eq
  have hval := congrArg ZMod.val hcast
  simpa [ZMod.val_natCast, Nat.mod_eq_of_lt hi, Nat.mod_eq_of_lt hj] using hval

theorem cutIndex_surjective_below (cut q : ZMod r) :
    ∃ k : ℕ, k < r ∧ cutIndex cut k = q := by
  refine ⟨(q - (cut + 1)).val, ZMod.val_lt _, ?_⟩
  simp [cutIndex, ZMod.natCast_zmod_val]

theorem cutIndex_last (cut : ZMod r) : cutIndex cut (r - 1) = cut := by
  have hsum : (r - 1 : ℕ) + 1 = r := by have := NeZero.pos r; omega
  have hcast : ((r - 1 : ℕ) : ZMod r) + 1 = 0 := by
    have h := congrArg (fun k : ℕ => (k : ZMod r)) hsum
    simpa using h
  unfold cutIndex
  calc
    cut + 1 + ((r - 1 : ℕ) : ZMod r) =
        cut + (((r - 1 : ℕ) : ZMod r) + 1) := by abel
    _ = cut := by rw [hcast]; simp

def cutVector (cut : ZMod r) (v : ZMod r → ℕ) (k : ℕ) : ℕ :=
  if k < r then v (cutIndex cut k) else 0

theorem cutVector_balance (cut : ZMod r) (g target flow : ZMod r → ℕ)
    (zero : flow cut = 0)
    (balance : ∀ i, flow i + target i = g i + flow (i - 1)) :
    ∀ k, cutVector cut flow k + cutVector cut target k =
      cutVector cut g k + if k = 0 then 0 else cutVector cut flow (k - 1) := by
  intro k
  by_cases hk : k < r
  · by_cases hzero : k = 0
    · subst k
      simpa [cutVector, cutIndex, NeZero.pos r, zero] using balance (cutIndex cut 0)
    · have hprev : k - 1 < r := by omega
      have hidx : cutIndex cut k - 1 = cutIndex cut (k - 1) := by
        unfold cutIndex
        rw [Nat.cast_sub (by omega : 1 ≤ k)]
        simp only [Nat.cast_one]
        abel
      simpa [cutVector, hk, hzero, hprev, hidx] using balance (cutIndex cut k)
  · have hzero : k ≠ 0 := by have := NeZero.pos r; omega
    by_cases hprev : k - 1 < r
    · have hlast : k - 1 = r - 1 := by omega
      simp [cutVector, hk, hzero, hprev, hlast, cutIndex_last, zero]
    · simp [cutVector, hk, hzero, hprev]

theorem cutVector_last_zero (cut : ZMod r) (flow : ZMod r → ℕ)
    (zero : flow cut = 0) : cutVector cut flow (r - 1) = 0 := by
  have hlast : r - 1 < r := by have := NeZero.pos r; omega
  simp [cutVector, hlast, cutIndex_last, zero]

theorem cut_transfer (cut : ZMod r) (g : ZMod r → ℕ)
    (i amount k : ℕ) (hi : i + 1 < r) (hk : k < r) :
    cyclicGapTransfer g (cutIndex cut i) amount (cutIndex cut k) =
      transferGap (fun j => g (cutIndex cut j)) i amount k := by
  classical
  have hi0 : i < r := by omega
  have hsucc := cutIndex_next cut i
  by_cases hki : k = i
  · subst k
    have hne : cutIndex cut i ≠ cutIndex cut (i + 1) := by
      intro heq
      have := cutIndex_injective_below cut hi0 hi heq
      omega
    simp [cyclicGapTransfer, transferGap, ← hsucc, hne]
  · by_cases hnext : k = i + 1
    · subst k
      simp [cyclicGapTransfer, transferGap, ← hsucc]
    · have hne : cutIndex cut k ≠ cutIndex cut i := by
        intro heq
        exact hki (cutIndex_injective_below cut hk hi0 heq)
      have hnnext : cutIndex cut k ≠ cutIndex cut (i + 1) := by
        intro heq
        exact hnext (cutIndex_injective_below cut hk hi heq)
      simp [cyclicGapTransfer, transferGap, ← hsucc, hki, hnext, hne, hnnext]

theorem transferGap_zero (g : ℕ → ℕ) (i : ℕ) : transferGap g i 0 = g := by
  classical
  funext k
  by_cases hki : k = i
  · subst k
    simp [transferGap]
  · by_cases hnext : k = i + 1
    · subst k
      simp [transferGap]
    · simp [transferGap, hki, hnext]

theorem gapMass_eq_sum (g : Gaps r) : gapMass g = ∑ i : Fin r, g i := by
  unfold gapMass
  rw [← Fin.sum_univ_eq_sum_range]
  apply Finset.sum_congr rfl
  intro i _
  congr 1
  exact Fin.ext (Nat.mod_eq_of_lt i.isLt)

theorem finEquiv_val (i : Fin r) : (ZMod.finEquiv r i).val = i.val := by
  cases r with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ r => rfl

theorem finEquiv_cast (i : Fin r) : ZMod.finEquiv r i = (i.val : ZMod r) := by
  have h := ZMod.natCast_zmod_val (ZMod.finEquiv r i)
  rw [finEquiv_val] at h
  exact h.symm

theorem finEquiv_previous (i : Fin r) :
    ZMod.finEquiv r (previousGap i) = ZMod.finEquiv r i - 1 := by
  rw [finEquiv_cast, finEquiv_cast]
  by_cases hi : i.val = 0
  · simp only [previousGap, hi, ↓reduceDIte, ↓reduceIte]
    rw [Nat.cast_sub (by have := NeZero.pos r; omega : 1 ≤ r)]
    simp
  · simp only [previousGap, hi, ↓reduceDIte, ↓reduceIte]
    rw [Nat.cast_sub (by omega : 1 ≤ i.val)]
    simp

/-- The normalized finite flow, transported to the frame's cyclic indices. -/
theorem frameGapFlow_exists (start target : GapFrame n r α) :
    ∃ flow : ZMod r → ℕ,
      (∀ i, flow i ≤ n - r) ∧
      (∃ cut, flow cut = 0) ∧
      (∀ i, flow i + target.gap i = start.gap i + flow (i - 1)) := by
  have hm (frame : GapFrame n r α) : gapMass (finGaps frame.gap) = n - r := by
    rw [gapMass_eq_sum, finGaps_sum, frame.gap_total]
  obtain ⟨flow, bound, ⟨cut, zero⟩, balance⟩ :=
    gapFlow_exists_normalized (finGaps start.gap) (finGaps target.gap)
      ((hm start).trans (hm target).symm)
  let flowZ : ZMod r → ℕ := fun i => flow ((ZMod.finEquiv r).symm i)
  refine ⟨flowZ, ?_, ⟨ZMod.finEquiv r cut, ?_⟩, ?_⟩
  · intro i
    simpa [hm start] using bound ((ZMod.finEquiv r).symm i)
  · simpa [flowZ] using zero
  · intro i
    have h := balance ((ZMod.finEquiv r).symm i)
    have hp : previousGap ((ZMod.finEquiv r).symm i) =
        (ZMod.finEquiv r).symm (i - 1) := by
      apply (ZMod.finEquiv r).injective
      rw [finEquiv_previous]
      simp
    simpa [finGaps, flowZ, hp] using h

/-- Every arithmetic prefix is compiled into a plan on its actual successor. -/
theorem cutSchedule_prefix (F : Finset α) (s : Execution n α)
    (start : GapFrame n r α) (cut : ZMod r)
    (g target flow : ℕ → ℕ) (hn : 3 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = start.decode)
    (initial : ∀ k < r, start.gap (cutIndex cut k) = g k)
    (balance : ∀ k, flow k + target k =
      g k + if k = 0 then 0 else flow (k - 1)) :
    ∀ stage, stage ≤ r - 1 →
      ∃ mid : GapFrame n r α, ∃ plan : BatchPlacementPlan F s mid.decode,
        mid.block = start.block ∧
        (∀ k < r, mid.gap (cutIndex cut k) = scheduledGap g target flow stage k) ∧
        plan.batches ≤ stage ∧
        plan.transfers = ∑ k ∈ Finset.range stage, flow k := by
  classical
  intro stage
  induction stage with
  | zero =>
      intro _
      obtain ⟨base, hbaseK, hbaseM⟩ := BatchPlacementPlan.done_at F s start.decode source
      refine ⟨start, base, rfl, ?_, hbaseK.le, ?_⟩
      · intro k hk
        rw [scheduledGap_initial]
        exact initial k hk
      · simpa using hbaseM
  | succ stage ih =>
      intro hstage
      have hprev : stage ≤ r - 1 := by omega
      have hnext : stage + 1 < r := by omega
      obtain ⟨mid, plan, blocks, invariant, hK, hM⟩ := ih hprev
      have hstep := scheduledGap_transfer g target flow stage (balance stage)
      by_cases hzero : flow stage = 0
      · have hsame : scheduledGap g target flow (stage + 1) =
            scheduledGap g target flow stage := by
          rw [← hstep, hzero, transferGap_zero]
        refine ⟨mid, plan, blocks, ?_, by omega, ?_⟩
        · intro k hk
          rw [hsame]
          exact invariant k hk
        · simpa [Finset.sum_range_succ, hzero] using hM
      · have positive : 0 < flow stage := Nat.pos_of_ne_zero hzero
        have fits : flow stage ≤ mid.gap (cutIndex cut stage) := by
          rw [invariant stage (by omega)]
          exact scheduledGap_capacity g target flow stage (balance stage)
        have hgap : mid.gap (cutIndex cut stage) ≤ n - r := by
          have h := Finset.single_le_sum (fun j _ => Nat.zero_le (mid.gap j))
            (Finset.mem_univ (cutIndex cut stage))
          rwa [mid.gap_total] at h
        have short : flow stage < n := by omega
        let next := gapBatchFrame mid (cutIndex cut stage) (flow stage)
          hr positive fits short
        have hinv : ∀ k < r,
            next.gap (cutIndex cut k) = scheduledGap g target flow (stage + 1) k := by
          intro k hk
          change cyclicGapTransfer mid.gap (cutIndex cut stage) (flow stage)
            (cutIndex cut k) = _
          rw [cut_transfer cut mid.gap stage (flow stage) k hnext hk]
          rw [← hstep]
          simp only [transferGap, Function.update_apply]
          rw [invariant stage (by omega), invariant (stage + 1) hnext, invariant k hk]
        let move := gapFrameLegalPlacementBatch F (withPlaced s mid.decode)
          mid (cutIndex cut stage) (flow stage) hn hr positive fits rfl
        have htarget : move.target = next.decode := by
          exact gapFrameLegalPlacementBatch_target F (withPlaced s mid.decode)
            mid (cutIndex cut stage) (flow stage) hn hr positive fits rfl
        obtain ⟨one, hOneK, hOneM⟩ :
            ∃ one : BatchPlacementPlan F (withPlaced s mid.decode) next.decode,
              one.batches = 1 ∧ one.transfers = flow stage := by
          rw [← htarget]
          refine ⟨.step _ move (.done _), rfl, ?_⟩
          change 0 + flow stage = flow stage
          omega
        let joined := plan.append one
        refine ⟨next, joined, blocks, hinv, ?_, ?_⟩
        · change (plan.append one).batches ≤ stage + 1
          rw [BatchPlacementPlan.append_batches, hOneK]
          omega
        · change (plan.append one).transfers = _
          rw [BatchPlacementPlan.append_transfers, hOneM, hM, Finset.sum_range_succ]

/-- A normalized cyclic flow yields a bounded plan of actual compressed batches. -/
theorem gapFramePlacement_plan (F : Finset α) (s : Execution n α)
    (start target : GapFrame n r α) (hn : 3 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = start.decode) :
    ∃ mid : GapFrame n r α, ∃ plan : BatchPlacementPlan F s mid.decode,
      mid.gap = target.gap ∧ mid.block = start.block ∧
      plan.batches ≤ r - 1 ∧ plan.transfers ≤ (n - r) * (r - 1) := by
  obtain ⟨flow, bounded, ⟨cut, zero⟩, balance⟩ := frameGapFlow_exists start target
  let g := cutVector cut start.gap
  let goal := cutVector cut target.gap
  let linear := cutVector cut flow
  have hbalance : ∀ k, linear k + goal k =
      g k + if k = 0 then 0 else linear (k - 1) :=
    cutVector_balance cut start.gap target.gap flow zero balance
  have hinitial : ∀ k < r, start.gap (cutIndex cut k) = g k := by
    intro k hk
    simp [g, cutVector, hk]
  obtain ⟨mid, plan, blocks, invariant, hK, hM⟩ :=
    cutSchedule_prefix F s start cut g goal linear hn hr source hinitial hbalance
      (r - 1) (by omega)
  have hzero : linear (r - 1) = 0 := cutVector_last_zero cut flow zero
  have hfinal := scheduledGap_final g goal linear r (by omega) hzero (hbalance (r - 1))
  have gaps : mid.gap = target.gap := by
    funext q
    obtain ⟨k, hk, hq⟩ := cutIndex_surjective_below cut q
    rw [← hq, invariant k hk, hfinal k hk]
    simp [goal, cutVector, hk]
  refine ⟨mid, plan, gaps, blocks, hK, ?_⟩
  rw [hM]
  apply scheduledGap_transfer_budget linear r (n - r)
  intro k hk
  have hkr : k < r := by omega
  simpa [linear, cutVector, hkr] using bounded (cutIndex cut k)

end FusionLogCompression
