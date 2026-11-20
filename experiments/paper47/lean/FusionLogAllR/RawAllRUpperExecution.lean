import FusionLogAllR.RawAllRUpperWitness

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # Execution of the explicit all-right word

The stage boundary fixes the entire literal placement. The existing M1
batch realizes the stage's fusion-free prefix; its last defect appends
exactly the required ordered record.
-/

def allRCarrier (n : ℕ) [NeZero n] (j : ℕ) : Finset (ZMod n) :=
  Finset.univ.filter (fun a => a.val ≤ j)

def allRBoundaryPlaced {n : ℕ} [NeZero n] (j : ℕ) :
    Placement n (Finset (ZMod n)) :=
  fun q => if q = 0 then some (allRCarrier n j)
    else if q.val ≤ j then none else some {q}

private theorem carrier_succ {n : ℕ} [NeZero n] {j : ℕ}
    (hj : j + 1 < n) :
    allRCarrier n j ∪ {((j + 1 : ℕ) : ZMod n)} = allRCarrier n (j + 1) := by
  ext a
  have hv : (((j + 1 : ℕ) : ZMod n)).val = j + 1 :=
    ZMod.val_natCast_of_lt hj
  have heq : a = ((j + 1 : ℕ) : ZMod n) ↔ a.val = j + 1 := by
    constructor
    · intro h; rw [h]; exact hv
    · intro h
      apply ZMod.val_injective
      rw [hv]
      exact h
  simp only [allRCarrier, Finset.mem_union, Finset.mem_filter,
    Finset.mem_univ, true_and, Finset.mem_singleton, heq]
  omega

private theorem carrier_one {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    allRCarrier n 1 = allRSelectedPair n := by
  have : Fact (1 < n) := ⟨by omega⟩
  ext a
  simp only [allRCarrier, Finset.mem_filter, Finset.mem_univ, true_and,
    allRSelectedPair, Finset.mem_insert, Finset.mem_singleton]
  constructor
  · intro h
    have hc : a.val = 0 ∨ a.val = 1 := by omega
    rcases hc with hc | hc
    · left; apply ZMod.val_injective; rw [ZMod.val_zero]; exact hc
    · right; apply ZMod.val_injective; rw [ZMod.val_one]; exact hc
  · rintro (rfl | rfl)
    · rw [ZMod.val_zero]; omega
    · rw [ZMod.val_one]

private theorem registered_boundary {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    (allRRegistered (n := n)).placed = allRBoundaryPlaced 1 := by
  have : Fact (1 < n) := ⟨by omega⟩
  funext q
  by_cases h0 : q = 0
  · subst q
    simp [allRBoundaryPlaced, carrier_one hn, allRRegistered_zero]
  by_cases h1 : q = 1
  · subst q
    have hp := defect_port_one_empty (allRSelectedPair n)
      (singletonExecution n) (by omega : 2 ≤ n)
    simpa [allRRegistered, allRBoundaryPlaced, h0, ZMod.val_one] using hp
  · have hv : ¬q.val ≤ 1 := by
      intro hv
      have hq : q.val = 0 ∨ q.val = 1 := by omega
      rcases hq with hq | hq
      · apply h0; apply ZMod.val_injective; rw [ZMod.val_zero]; exact hq
      · apply h1; apply ZMod.val_injective; rw [ZMod.val_one]; exact hq
    simp [allRBoundaryPlaced, h0, hv, allRRegistered_other q h0 h1]

/-- Public normalization interfaces for the independent equality-case
induction.  These expose the already proved boundary identities without
changing the attaining construction. -/
theorem allRCarrier_one {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    allRCarrier n 1 = allRSelectedPair n := carrier_one hn

theorem allRCarrier_succ {n : ℕ} [NeZero n] {j : ℕ} (hj : j + 1 < n) :
    allRCarrier n j ∪ {((j + 1 : ℕ) : ZMod n)} = allRCarrier n (j + 1) :=
  carrier_succ hj

theorem allRRegistered_boundary {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    (allRRegistered (n := n)).placed = allRBoundaryPlaced 1 := registered_boundary hn

private theorem stage_eq_batch {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {j : ℕ} (hj : 1 ≤ j) (hjn : j ≤ n - 2) :
    allRStage n j = batchWord ((j + 1 : ℕ) : ZMod n) j ++ [.d] := by
  have : Fact (1 < n) := ⟨by omega⟩
  have hsum : n - j + j = n := Nat.sub_add_cancel (by omega)
  have hcast : ((n - j : ℕ) : ZMod n) = 1 - ((j + 1 : ℕ) : ZMod n) := by
    have hc := congrArg (fun k : ℕ => (k : ZMod n)) hsum
    push_cast at hc ⊢
    rw [ZMod.natCast_self] at hc
    linear_combination hc
  have hval : (1 - ((j + 1 : ℕ) : ZMod n)).val = n - j := by
    rw [← hcast]
    exact ZMod.val_natCast_of_lt (by omega)
  have hphase : (((j + 1 : ℕ) : ZMod n) - (j : ZMod n)).val = 1 := by
    rw [show ((j + 1 : ℕ) : ZMod n) - (j : ZMod n) = 1 by push_cast; ring]
    exact ZMod.val_one n
  have hpd : pdWord j = pdWord (j - 1) ++ [.p, .d] := by
    conv_lhs => rw [← Nat.sub_add_cancel hj]
    rfl
  unfold allRStage batchWord
  rw [hval, hphase, hpd]
  simp only [pWord, List.nil_append, List.append_assoc, List.cons_append]

theorem allRStage_execution {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {j : ℕ} (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (hplaced : s.placed = allRBoundaryPlaced j) :
    (run F s (allRStage n j)).placed = allRBoundaryPlaced (j + 1) ∧
      completeFusionLog F s (allRStage n j) =
        [⟨allRCarrier n j, {((j + 1 : ℕ) : ZMod n)}, allRCarrier n (j + 1)⟩] := by
  have : Fact (1 < n) := ⟨by omega⟩
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have hv := congrArg ZMod.val h
    rw [ZMod.val_one, ZMod.val_zero] at hv
    omega
  let q : ZMod n := (j + 1 : ℕ)
  have hqv : q.val = j + 1 := ZMod.val_natCast_of_lt (by omega)
  have hq0 : q ≠ 0 := by
    intro h
    have hc := congrArg ZMod.val h
    rw [hqv, ZMod.val_zero] at hc
    omega
  have hq1 : q ≠ 1 := by
    intro h
    have hc := congrArg ZMod.val h
    rw [hqv, ZMod.val_one] at hc
    omega
  have hq : s.placed q = some {q} := by
    rw [hplaced]
    simp [allRBoundaryPlaced, hq0, hqv]
  have hholes : ∀ i : ℕ, 1 ≤ i → i ≤ j → s.placed (q - (i : ZMod n)) = none := by
    intro i hi hij
    have harg : q - (i : ZMod n) = ((j + 1 - i : ℕ) : ZMod n) := by
      dsimp [q]
      rw [Nat.cast_sub (by omega : i ≤ j + 1)]
    have hv : (q - (i : ZMod n)).val = j + 1 - i := by
      rw [harg]
      exact ZMod.val_natCast_of_lt (by omega)
    have hne : q - (i : ZMod n) ≠ 0 := by
      intro h
      have hc := congrArg ZMod.val h
      rw [hv, ZMod.val_zero] at hc
      omega
    rw [hplaced]
    simp [allRBoundaryPlaced, hne, hv, show j + 1 - i ≤ j by omega]
  have hbatch := batchWord_spec F s q {q} j hn hj hjn hq hholes
  have hphase : q - (j : ZMod n) = 1 := by dsimp [q]; push_cast; ring
  let mid := withPlaced s (batchTarget s.placed q j)
  have hm0 : mid.placed 0 = some (allRCarrier n j) := by
    simp [mid, withPlaced, batchTarget, hphase, h10.symm,
      hq0.symm, hplaced, allRBoundaryPlaced]
  have hm1 : mid.placed 1 = some {q} := by
    simp [mid, withPlaced, batchTarget, hphase, hq]
  have hr : run F s (allRStage n j) = step F mid .d := by
    rw [stage_eq_batch hn hj hjn, run_append, hbatch.2.1]
    rfl
  have hlog : completeFusionLog F s (allRStage n j) =
      [⟨allRCarrier n j, {q}, allRCarrier n (j + 1)⟩] := by
    rw [stage_eq_batch hn hj hjn, completeFusionLog_append]
    rw [(completeFusionLog_eq_nil_iff_fusionFree F s _).mpr hbatch.1, hbatch.2.1]
    change completeFusionLog F mid [.d] = _
    simp only [completeFusionLog, hm0, hm1]
    rw [carrier_succ (by omega : j + 1 < n)]
  refine ⟨?_, hlog⟩
  rw [hr]
  change (stepDefect F mid).placed = _
  rw [stepDefect_placed]
  funext z
  by_cases hz0 : z = 0
  · subst z
    simpa [q, fusionPlacement, hm0, hm1, allRBoundaryPlaced] using
      congrArg some (carrier_succ (n := n) (by omega : j + 1 < n))
  by_cases hz1 : z = 1
  · subst z
    simp [fusionPlacement, h10, allRBoundaryPlaced, ZMod.val_one]
  by_cases hzq : z = q
  · subst z
    simp [fusionPlacement, hz0, hz1, mid, withPlaced, batchTarget, hphase,
      allRBoundaryPlaced, hqv]
  · have hvq : z.val ≠ j + 1 := by
      intro h
      apply hzq
      apply ZMod.val_injective
      rw [hqv]
      exact h
    have hv : (z.val ≤ j + 1) ↔ (z.val ≤ j) := by omega
    simp [fusionPlacement, hz0, hz1, mid, withPlaced, batchTarget, hphase,
      hzq, hplaced, allRBoundaryPlaced, hv]

def allRStages (n k : ℕ) : List Letter :=
  (List.range k).flatMap (fun i => allRStage n (i + 1))

private def allRPartnersPrefix (n k : ℕ) : List (ZMod n) :=
  (List.range k).map (fun i => ((i + 2 : ℕ) : ZMod n))

private theorem allRStages_succ (n k : ℕ) :
    allRStages n (k + 1) = allRStages n k ++ allRStage n (k + 1) := by
  simp [allRStages, List.range_succ, List.flatMap_append]

private theorem allRPartnersPrefix_succ (n k : ℕ) :
    allRPartnersPrefix n (k + 1) =
      allRPartnersPrefix n k ++ [((k + 2 : ℕ) : ZMod n)] := by
  simp [allRPartnersPrefix, List.range_succ]

theorem allRStages_placed {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {k : ℕ} (hk : k ≤ n - 2) (F : Finset (ZMod n)) :
    (run F (allRRegistered (n := n)) (allRStages n k)).placed =
      allRBoundaryPlaced (k + 1) := by
  induction k with
  | zero =>
      change (allRRegistered (n := n)).placed = allRBoundaryPlaced 1
      exact registered_boundary hn
  | succ k ih =>
      have hk' : k ≤ n - 2 := by omega
      have hprev := ih hk'
      rw [allRStages_succ, run_append]
      exact (allRStage_execution hn (by omega) (by omega) F
        (run F (allRRegistered (n := n)) (allRStages n k)) hprev).1

private def allRStageRecord (n : ℕ) [NeZero n] (j : ℕ) : FusionRecord (ZMod n) :=
  ⟨allRCarrier n j, {((j + 1 : ℕ) : ZMod n)}, allRCarrier n (j + 1)⟩

private def allRPrefixLog (n : ℕ) [NeZero n] (k : ℕ) : List (FusionRecord (ZMod n)) :=
  (List.range k).map (fun i => allRStageRecord n (i + 1))

private theorem allRPrefixLog_succ {n : ℕ} [NeZero n] (k : ℕ) :
    allRPrefixLog n (k + 1) = allRPrefixLog n k ++ [allRStageRecord n (k + 1)] := by
  simp [allRPrefixLog, allRStageRecord, List.range_succ]

private theorem rightFusionLog_append {n : ℕ} (C : Finset (ZMod n))
    (xs ys : List (ZMod n)) :
    rightFusionLog C (xs ++ ys) =
      rightFusionLog C xs ++
        rightFusionLog (xs.foldl (fun D a => D ∪ {a}) C) ys := by
  induction xs generalizing C with
  | nil => simp [rightFusionLog]
  | cons a xs ih =>
      simp only [List.cons_append, rightFusionLog]
      rw [ih]
      simp [List.foldl_cons]

private theorem allRPartnersPrefix_fold {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (k : ℕ) (hk : k ≤ n - 2) :
    (allRPartnersPrefix n k).foldl (fun C a => C ∪ {a})
      (allRSelectedPair n) = allRCarrier n (k + 1) := by
  have hpair : allRCarrier n 1 = allRSelectedPair n := carrier_one hn
  induction k with
  | zero => simpa [allRPartnersPrefix] using hpair.symm
  | succ k ih =>
      have hk' : k ≤ n - 2 := by omega
      rw [allRPartnersPrefix_succ, List.foldl_append]
      rw [List.foldl_cons, List.foldl_nil]
      change ((allRPartnersPrefix n k).foldl
        (fun C a => C ∪ {a}) (allRSelectedPair n)) ∪
        {((k + 2 : ℕ) : ZMod n)} = allRCarrier n (k + 2)
      rw [ih hk']
      exact carrier_succ (j := k + 1) (by omega)

theorem allRStages_log {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {k : ℕ} (hk : k ≤ n - 2) (F : Finset (ZMod n)) :
    completeFusionLog F (allRRegistered (n := n)) (allRStages n k) =
      allRPrefixLog n k := by
  induction k with
  | zero => rfl
  | succ k ih =>
      have hk' : k ≤ n - 2 := by omega
      have hprev := ih hk'
      rw [allRStages_succ, completeFusionLog_append, hprev]
      have hplaced := allRStages_placed hn hk' F
      have hstage := allRStage_execution hn (by omega) (by omega) F
        (run F (allRRegistered (n := n)) (allRStages n k)) hplaced
      rw [hstage.2, allRPrefixLog_succ]
      rfl

private theorem allRPrefixLog_eq_postLog {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    allRPrefixLog n (n - 2) = allRPostLog n := by
  have hrec : ∀ k ≤ n - 2,
      rightFusionLog (allRSelectedPair n) (allRPartnersPrefix n k) =
        allRPrefixLog n k := by
    intro k hk
    induction k with
    | zero => simp [allRPartnersPrefix, allRPrefixLog, rightFusionLog]
    | succ k ih =>
        have hk' : k ≤ n - 2 := by omega
        rw [allRPartnersPrefix_succ, rightFusionLog_append, ih hk']
        rw [allRPartnersPrefix_fold hn k hk']
        rw [allRPrefixLog_succ]
        simp only [rightFusionLog, allRStageRecord]
        apply congrArg (fun r => allRPrefixLog n k ++ [r])
        rw [FusionRecord.mk.injEq]
        constructor
        · rfl
        constructor
        · rfl
        · simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using
            (carrier_succ (n := n) (j := k + 1) (by omega))
  rw [← hrec (n - 2) (by omega)]
  simp [allRPartnersPrefix, allRPartners, allRPostLog]

theorem allRCanonicalWord_realizes {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    RealizesAllR (n := n) (allRCanonicalWord n) := by
  have hplaced := allRStages_placed hn (by omega : n - 2 ≤ n - 2)
    (allRSelectedPair n)
  have hlog := allRStages_log hn (by omega : n - 2 ≤ n - 2)
    (allRSelectedPair n)
  have hpost := allRPrefixLog_eq_postLog hn
  have hstage : allRCanonicalWord n =
      [.d] ++ allRStages n (n - 2) ++ pWord (n - 1) := by
    rfl
  have hrunReg : run (allRSelectedPair n) (singletonExecution n) [.d] =
      allRRegistered (n := n) := by rfl
  have hprefix : run (allRSelectedPair n) (singletonExecution n)
      ([.d] ++ allRStages n (n - 2)) =
      run (allRSelectedPair n) (allRRegistered (n := n))
        (allRStages n (n - 2)) := by
    rw [run_append, hrunReg]
  refine ⟨?_, ?_⟩
  · rw [hstage, completeFusionLog_append, completeFusionLog_append]
    have hregLog : completeFusionLog (allRSelectedPair n)
        (singletonExecution n) [.d] = [allRRegistration n] := by rfl
    rw [hregLog, hrunReg, hlog, hpost]
    have htail : completeFusionLog (allRSelectedPair n)
        (run (allRSelectedPair n) allRRegistered (allRStages n (n - 2)))
        (pWord (n - 1)) = [] :=
      (completeFusionLog_eq_nil_iff_fusionFree _ _ _).2
        (fusionFree_pWord _ _ _)
    have htail' : completeFusionLog (allRSelectedPair n)
        (run (allRSelectedPair n) (singletonExecution n)
          ([.d] ++ allRStages n (n - 2))) (pWord (n - 1)) = [] := by
      rw [hprefix]
      exact htail
    rw [htail']
    simp [allRLog, allRPostLog]
  · rw [hstage, run_append, hprefix, run_pWord]
    have hfinalRank : n - 2 + 1 = n - 1 := by omega
    rw [hfinalRank] at hplaced
    have hfull : allRCarrier n (n - 1) = Finset.univ := by
      ext a
      simp only [allRCarrier, Finset.mem_filter, Finset.mem_univ, true_and]
      constructor
      · intro _
        trivial
      · intro _
        exact Nat.le_pred_of_lt (ZMod.val_lt a)
    funext q
    by_cases hq : q = ((n - 1 : ℕ) : ZMod n)
    · subst q
      simp [rotate, hplaced, allRBoundaryPlaced, allREndpoint, hfull]
    · have hsource : q - ((n - 1 : ℕ) : ZMod n) ≠ 0 := by
        intro hz
        apply hq
        exact sub_eq_zero.mp hz
      have hsourceVal : (q - ((n - 1 : ℕ) : ZMod n)).val ≤ n - 1 := by
        exact Nat.le_pred_of_lt (ZMod.val_lt _)
      simp [rotate, hplaced, allRBoundaryPlaced, allREndpoint,
        hq, hsource, hsourceVal]

theorem allRCanonicalWord_is_shortest {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    RealizesAllR (n := n) (allRCanonicalWord n) ∧
      ∀ word, RealizesAllR (n := n) word →
        (allRCanonicalWord n).length ≤ word.length := by
  refine ⟨allRCanonicalWord_realizes hn, ?_⟩
  intro word hword
  rw [allRCanonicalWord_length hn]
  exact hword.word_length_lower_bound hn

end FusionLogAllR
