import FusionLogCompression.M1Batch
import RegisteredAbsorptionChains.SourceOrderInvariant

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n : ℕ} {α : Type*} [NeZero n] [DecidableEq α]

/-- Use no batch when the ordered parents already occupy consecutive sites. -/
def adjacentBatchWord (q : ZMod n) (f : ℕ) : List Letter :=
  if f = 0 then [] else batchWord q f

/-- The fusion-free prefix that places the ordered parents at ports `0,1`. -/
def adjacentRoutePrefix (qLeft qRight : ZMod n) (f : ℕ) : List Letter :=
  adjacentBatchWord qRight f ++ pWord (-qLeft).val

/-- Append exactly one actual fusion after the fusion-free routing prefix. -/
def adjacentFusionWord (qLeft qRight : ZMod n) (f : ℕ) : List Letter :=
  adjacentRoutePrefix qLeft qRight f ++ [.d]

/-- Frozen source-order interface for a fusion already occupying ports `0,1`.
The ordered parent fibers have no third source fiber in the positive interval. -/
theorem sourceOrderParentInterval (s : Execution n (ZMod n))
    (A B : Finset (ZMod n))
    (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some A) (h1 : s.placed 1 = some B) :
    ∃ (lift : SourceOrderLift n) (a b : ZMod n) (k : ℤ),
      s.placed = placementOfMap lift.position ∧
      a ∈ A ∧ b ∈ B ∧
      (a.val : ℤ) < (b.val : ℤ) + k * n ∧
      lift.map ((b.val : ℤ) + k * n) = lift.map (a.val : ℤ) + 1 ∧
      ∀ x : ℤ, (a.val : ℤ) ≤ x → x ≤ (b.val : ℤ) + k * n →
        lift.map x = lift.map (a.val : ℤ) ∨
          lift.map x = lift.map (a.val : ℤ) + 1 := by
  exact fusion_ports_source_adjacent s A B ordered h0 h1

private theorem natCast_ne_zero_of_pos_lt (k : ℕ) (hk₀ : 0 < k) (hkn : k < n) :
    (k : ZMod n) ≠ 0 := by
  intro h
  have hv := congrArg ZMod.val h
  rw [ZMod.val_natCast_of_lt hkn, ZMod.val_zero] at hv
  omega

private theorem one_ne_zero_of_three_le (hn : 3 ≤ n) :
    (1 : ZMod n) ≠ 0 := by
  intro hzero
  have hn1 : n = 1 := ZMod.one_eq_zero_iff.mp hzero
  omega

private theorem adjacent_sites_distinct (qLeft qRight : ZMod n) (f : ℕ)
    (hn : 3 ≤ n) (hf₁ : 1 ≤ f) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n)) :
    qLeft ≠ qRight ∧ qLeft + 1 ≠ qRight := by
  have hfbound : f + 2 ≤ n :=
    (Nat.le_sub_iff_add_le (by omega : 2 ≤ n)).mp hfn
  have hflt : f < n := by omega
  have hf : f + 1 < n := by omega
  have hsum : ((f + 1 : ℕ) : ZMod n) ≠ 0 :=
    natCast_ne_zero_of_pos_lt (f + 1) (by omega) hf
  have hfone : (f : ZMod n) ≠ 0 := by
    intro h
    have hv := congrArg ZMod.val h
    rw [ZMod.val_natCast_of_lt hflt, ZMod.val_zero] at hv
    omega
  constructor
  · intro h
    have hh : (0 : ZMod n) = ((f + 1 : ℕ) : ZMod n) := by
      calc
        0 = qLeft - qLeft := by ring
        _ = qRight - qLeft := congrArg (fun z : ZMod n => z - qLeft) h
        _ = (qLeft + 1 + (f : ZMod n)) - qLeft := by rw [hgap]
        _ = ((f + 1 : ℕ) : ZMod n) := by push_cast; ring
    exact hsum hh.symm
  · intro h
    have hh : (0 : ZMod n) = (f : ZMod n) := by
      calc
        0 = (qLeft + 1) - (qLeft + 1) := by ring
        _ = qRight - (qLeft + 1) := congrArg (fun z : ZMod n => z - (qLeft + 1)) h
        _ = (qLeft + 1 + (f : ZMod n)) - (qLeft + 1) := by rw [hgap]
        _ = (f : ZMod n) := by ring
    exact hfone hh.symm

private def adjacentBatchWordTarget (s : Placement n (Finset α))
    (q : ZMod n) (f : ℕ) : Placement n (Finset α) :=
  if f = 0 then s else batchTarget s q f

private theorem adjacentBatch_spec (F : Finset α) (s : Execution n α)
    (q : ZMod n) (B : Finset α) (f : ℕ) (hn : 3 ≤ n)
    (hfn : f ≤ n - 2) (hB : s.placed q = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    FusionFree F s (adjacentBatchWord q f) ∧
      run F s (adjacentBatchWord q f) =
        withPlaced s (adjacentBatchWordTarget s.placed q f) ∧
      (adjacentBatchWord q f).length ≤ 2 * n + f := by
  by_cases hf : f = 0
  · subst f
    constructor
    · change True
      trivial
    constructor
    · cases s <;> rfl
    · simp [adjacentBatchWord]
  · have hf₁ : 1 ≤ f := by omega
    have hspec := batchWord_spec F s q B f hn hf₁ hfn hB hholes
    simpa [adjacentBatchWord, adjacentBatchWordTarget, hf] using hspec

private theorem adjacentBatchTarget_left (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (_hB : s.placed qRight = some B) :
    adjacentBatchWordTarget s.placed qRight f qLeft = some A := by
  by_cases hf : f = 0
  · subst f
    simpa [adjacentBatchWordTarget] using hA
  · have hdist := adjacent_sites_distinct qLeft qRight f hn (by omega) hfn hgap
    have hdest : qRight - (f : ZMod n) = qLeft + 1 := by
      rw [hgap]
      ring
    have hleftdest : qLeft ≠ qRight - (f : ZMod n) := by
      rw [hdest]
      intro heq
      have hh := congrArg (fun z : ZMod n => z - qLeft) heq
      have hone : (1 : ZMod n) ≠ 0 := one_ne_zero_of_three_le hn
      have hbad : (1 : ZMod n) = 0 := by simpa using hh.symm
      exact hone hbad
    simp [adjacentBatchWordTarget, hf, batchTarget, hleftdest, hdist.1, hA]

private theorem adjacentBatchTarget_right (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (_hA : s.placed qLeft = some A) (hB : s.placed qRight = some B) :
    adjacentBatchWordTarget s.placed qRight f (qLeft + 1) = some B := by
  by_cases hf : f = 0
  · subst f
    have hsite : qRight = qLeft + 1 := by simpa using hgap
    simpa [adjacentBatchWordTarget, hsite] using hB
  · have hdist := adjacent_sites_distinct qLeft qRight f hn (by omega) hfn hgap
    have hdest : qRight - (f : ZMod n) = qLeft + 1 := by
      rw [hgap]
      ring
    simp only [adjacentBatchWordTarget, if_neg hf, batchTarget]
    rw [if_pos hdest.symm]
    exact hB

/-- Route an ordered cyclically adjacent parent pair to ports `0,1`.

The certificate says that the right parent is `f` holes after the left
parent in positive cyclic order. The right parent is moved backward through
those holes in one M1 batch, then a common rotation aligns the pair. -/
theorem adjacentRoutePrefix_spec (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    FusionFree F s (adjacentRoutePrefix qLeft qRight f) ∧
      (run F s (adjacentRoutePrefix qLeft qRight f)).placed 0 = some A ∧
      (run F s (adjacentRoutePrefix qLeft qRight f)).placed 1 = some B ∧
      (adjacentRoutePrefix qLeft qRight f).length + 1 ≤ 3 * n + f := by
  let target := adjacentBatchWordTarget s.placed qRight f
  have hbatch := adjacentBatch_spec F s qRight B f hn hfn hB hholes
  have hleft : target qLeft = some A :=
    adjacentBatchTarget_left s qLeft qRight A B f hn hfn hgap hA hB
  have hright : target (qLeft + 1) = some B :=
    adjacentBatchTarget_right s qLeft qRight A B f hn hfn hgap hA hB
  have hrun : run F s (adjacentRoutePrefix qLeft qRight f) =
      withPlaced s (rotate (-qLeft) target) := by
    rw [adjacentRoutePrefix, run_append, hbatch.2.1]
    have hrot := run_rotation F (withPlaced s target) (-qLeft)
    simpa [withPlaced, target] using hrot
  have hfree : FusionFree F s (adjacentRoutePrefix qLeft qRight f) := by
    rw [adjacentRoutePrefix, fusionFree_append]
    exact ⟨hbatch.1, fusionFree_pWord F
      (run F s (adjacentBatchWord qRight f)) (-qLeft).val⟩
  have hport0 : (withPlaced s (rotate (-qLeft) target)).placed 0 = some A := by
    change rotate (-qLeft) target 0 = some A
    change target (0 - (-qLeft)) = some A
    rw [show (0 : ZMod n) - (-qLeft) = qLeft by ring]
    exact hleft
  have hport1 : (withPlaced s (rotate (-qLeft) target)).placed 1 = some B := by
    change rotate (-qLeft) target 1 = some B
    change target (1 - (-qLeft)) = some B
    rw [show (1 : ZMod n) - (-qLeft) = qLeft + 1 by ring]
    exact hright
  have hlen' : (adjacentRoutePrefix qLeft qRight f).length + 1 ≤ 3 * n + f := by
    by_cases hf : f = 0
    · subst f
      simp [adjacentRoutePrefix, adjacentBatchWord, pWord_length]
      have hval : (-qLeft).val < n := ZMod.val_lt _
      omega
    · have hbatchLen : (adjacentBatchWord qRight f).length ≤ 2 * n + f :=
        hbatch.2.2
      have hrotLen : (pWord (-qLeft).val).length + 1 ≤ n := by
        rw [pWord_length]
        have hval : (-qLeft).val < n := ZMod.val_lt _
        omega
      have hrouteLen : (adjacentRoutePrefix qLeft qRight f).length =
          (adjacentBatchWord qRight f).length + (pWord (-qLeft).val).length := by
        simp [adjacentRoutePrefix, List.length_append]
      rw [hrouteLen]
      calc
        (adjacentBatchWord qRight f).length + (pWord (-qLeft).val).length + 1 ≤
            (2 * n + f) + n := by omega
        _ = 3 * n + f := by omega
  rw [hrun]
  exact ⟨hfree, hport0, hport1, hlen'⟩

/-- Exact cost interface for the adjacent fusion word. The final `d` is
already paid for by the rotation slack when `f = 0`, and by the M1 batch
bound when `f > 0`; no extra unit is needed in the fusion-stage budget. -/
theorem adjacentFusionWord_length_le (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f := by
  rcases adjacentRoutePrefix_spec F s qLeft qRight A B f
      hn hfn hgap hA hB hholes with ⟨_, _, _, hlen⟩
  simpa [adjacentFusionWord, List.length_append, List.length_singleton] using hlen

/-- The final letter is the only potentially fusing operation in this route.
Its ordered event is exactly `(A,B,A ∪ B)`, with the base execution's
registration and selected-chain policy applied by `stepDefect`. -/
theorem adjacentFusionWord_spec (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    let route := adjacentRoutePrefix qLeft qRight f
    let mid := run F s route
    FusionFree F s route ∧
      mid.placed 0 = some A ∧
      mid.placed 1 = some B ∧
      run F s (adjacentFusionWord qLeft qRight f) = stepDefect F mid ∧
      (stepDefect F mid).placed 0 = some (A ∪ B) ∧
      (stepDefect F mid).placed 1 = none ∧
      (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f := by
  let route := adjacentRoutePrefix qLeft qRight f
  let mid := run F s route
  rcases adjacentRoutePrefix_spec F s qLeft qRight A B f
      hn hfn hgap hA hB hholes with ⟨hfree, hleft, hright, hrouteLen⟩
  have hstep : (stepDefect F mid).placed = fusionPlacement mid.placed := by
    cases mid with
    | mk placed origin chain =>
        unfold stepDefect
        cases h0 : placed 0 <;> cases h1 : placed 1 <;>
          simp [fusionPlacement, h0, h1]
  have hleft' : mid.placed 0 = some A := by simpa [mid, route] using hleft
  have hright' : mid.placed 1 = some B := by simpa [mid, route] using hright
  have h10 : (1 : ZMod n) ≠ 0 := one_ne_zero_of_three_le hn
  have hzero : (stepDefect F mid).placed 0 = some (A ∪ B) := by
    rw [hstep]
    simp [fusionPlacement, hleft', hright']
  have hone : (stepDefect F mid).placed 1 = none := by
    rw [hstep]
    simp [fusionPlacement, h10, hleft', hright']
  have hrun : run F s (adjacentFusionWord qLeft qRight f) =
      stepDefect F mid := by
    change run F s (route ++ [.d]) = stepDefect F mid
    rw [run_append]
    rfl
  have hlen : (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f :=
    adjacentFusionWord_length_le F s qLeft qRight A B f hn hfn hgap hA hB hholes
  dsimp [route, mid]
  exact ⟨hfree, hleft', hright', hrun, hzero, hone, hlen⟩

/-- The ordered fusion is exposed as the exact structured event tuple. -/
theorem adjacentFusionWord_event_update (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    let mid := run F s (adjacentRoutePrefix qLeft qRight f)
    let event : FusionRecord α := ⟨A, B, A ∪ B⟩
    ((run F s (adjacentFusionWord qLeft qRight f)).origin =
        (if mid.origin.isNone && A ∪ B = F then some event else mid.origin)) ∧
      ((run F s (adjacentFusionWord qLeft qRight f)).chain =
        (if mid.origin.isSome && (F ⊆ A || F ⊆ B) then
          mid.chain ++ [event] else mid.chain)) := by
  let route := adjacentRoutePrefix qLeft qRight f
  let mid := run F s route
  rcases adjacentFusionWord_spec F s qLeft qRight A B f
      hn hfn hgap hA hB hholes with
    ⟨_, hleft, hright, hrun, _, _, _⟩
  have hleft' : mid.placed 0 = some A := by simpa [mid, route] using hleft
  have hright' : mid.placed 1 = some B := by simpa [mid, route] using hright
  have hrun' : run F s (adjacentFusionWord qLeft qRight f) = stepDefect F mid := by
    simpa [mid, route] using hrun
  rw [hrun']
  dsimp [mid, route]
  simp [stepDefect, hleft, hright]

/-- Segment budget for the complete adjacent-parent route and its one fusion. -/
def adjacentFusionBudget (qLeft qRight : ZMod n) (f : ℕ) : RouteBudget :=
  ⟨if f = 0 then 0 else 1, f, (adjacentFusionWord qLeft qRight f).length⟩

theorem adjacentFusionWord_budget (F : Finset α) (s : Execution n α)
    (qLeft qRight : ZMod n) (A B : Finset α) (f : ℕ)
    (hn : 3 ≤ n) (hfn : f ≤ n - 2)
    (hgap : qRight = qLeft + 1 + (f : ZMod n))
    (hA : s.placed qLeft = some A) (hB : s.placed qRight = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (qRight - (i : ZMod n)) = none) :
    (adjacentFusionBudget qLeft qRight f).batches ≤ 1 ∧
      (adjacentFusionBudget qLeft qRight f).holeTransfers = f ∧
      (adjacentFusionBudget qLeft qRight f).rawLetters ≤ 3 * n + f := by
  rcases adjacentFusionWord_spec F s qLeft qRight A B f
      hn hfn hgap hA hB hholes with ⟨_, _, _, _, _, _, hlen⟩
  change (if f = 0 then 0 else 1) ≤ 1 ∧ f = f ∧
    (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f
  refine ⟨?_, rfl, hlen⟩
  split <;> omega

end FusionLogCompression
