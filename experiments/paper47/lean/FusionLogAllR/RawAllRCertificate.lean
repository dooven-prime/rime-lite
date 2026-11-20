import FusionLogAllR.RawAllRSegmentation

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

private def registeredSite (i : ℕ) : ℤ := (i : ℤ) + 2

private def registeredRing (n : ℕ) : PhysicalPacketRing n where
  head := 0
  tail := (List.range (n - 2)).map registeredSite
  increasing := by
    apply List.pairwise_cons.mpr
    constructor
    · intro x hx
      rcases List.mem_map.mp hx with ⟨i, hi, rfl⟩
      have hi' : i < n - 2 := List.mem_range.mp hi
      norm_num [registeredSite]
      omega
    · rw [List.pairwise_map]
      apply List.Pairwise.imp
      · intro a b hab
        change (a : ℤ) + 2 < (b : ℤ) + 2
        exact_mod_cast hab
      · apply List.pairwise_iff_getElem.mpr
        intro i j hi hj hij
        simp only [List.getElem_range] at hi hj ⊢
        omega
  below_end := by
    intro x hx
    rcases List.mem_map.mp hx with ⟨i, hi, rfl⟩
    have hi' : i < n - 2 := List.mem_range.mp hi
    change (i : ℤ) + 2 < 0 + n
    omega

private theorem registeredSite_cast {n : ℕ} [NeZero n]
    (i : ℕ) : (registeredSite i : ZMod n) = ((i + 2 : ℕ) : ZMod n) := by
  norm_num [registeredSite]

private theorem registeredSite_val {n : ℕ} [NeZero n]
    (i : ℕ) (hi : i + 2 < n) : (registeredSite i : ZMod n).val = i + 2 := by
  rw [registeredSite_cast, ZMod.val_natCast, Nat.mod_eq_of_lt hi]

private theorem registeredSite_ne_zero {n : ℕ} [NeZero n]
    (i : ℕ) (hi : i + 2 < n) : (registeredSite i : ZMod n) ≠ 0 := by
  intro h
  have hv := congrArg ZMod.val h
  rw [registeredSite_val i hi, ZMod.val_zero] at hv
  omega

private theorem registeredSite_ne_one {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (i : ℕ) (hi : i + 2 < n) :
    (registeredSite i : ZMod n) ≠ 1 := by
  intro h
  letI : Fact (1 < n) := ⟨by omega⟩
  have hv := congrArg ZMod.val h
  rw [registeredSite_val i hi, ZMod.val_one] at hv
  omega

private theorem registeredRing_support {n : ℕ} [NeZero n]
    (hn : 3 ≤ n) (q : ZMod n) :
    (allRRegistered (n := n)).placed q ≠ none ↔
      ∃ x ∈ (registeredRing n).sites, (x : ZMod n) = q := by
  by_cases hq0 : q = 0
  · subst q
    constructor
    · intro _
      exact ⟨0, by simp [registeredRing, PhysicalPacketRing.sites], by simp⟩
    · intro _
      rw [allRRegistered_zero]
      simp
  by_cases hq1 : q = 1
  · subst q
    constructor
    · intro h
      have hnone : (allRRegistered (n := n)).placed 1 = none := by
        change (step (allRSelectedPair n) (singletonExecution n) .d).placed 1 = none
        exact defect_port_one_empty _ _ (by omega)
      exact False.elim (h hnone)
    · rintro ⟨x, hx, hx1⟩
      change x ∈ 0 :: (List.range (n - 2)).map registeredSite at hx
      rcases List.mem_cons.mp hx with hx | hx
      · subst x
        have h01 : (0 : ZMod n) ≠ 1 := by
          intro h
          have := ZMod.one_eq_zero_iff.mp h.symm
          omega
        exfalso
        exact h01 (by simpa using hx1)
      · rcases List.mem_map.mp hx with ⟨i, hi, rfl⟩
        have hi' : i < n - 2 := List.mem_range.mp hi
        have hlt : i + 2 < n := by omega
        exfalso
        exact (registeredSite_ne_one hn i hlt) hx1
  · constructor
    · intro _
      have hqcast : ((q.val : ℕ) : ZMod n) = q := ZMod.natCast_zmod_val q
      have hlow : 2 ≤ q.val := by
        by_contra hlow
        have hc : q.val = 0 ∨ q.val = 1 := by omega
        rcases hc with h | h
        · apply hq0
          calc
            q = (q.val : ZMod n) := (ZMod.natCast_zmod_val q).symm
            _ = 0 := by simp [h]
        · apply hq1
          calc
            q = (q.val : ZMod n) := (ZMod.natCast_zmod_val q).symm
            _ = 1 := by simp [h]
      let i : ℕ := q.val - 2
      have hlow' : 2 ≤ q.val := hlow
      have hsubq : q.val - 2 + 2 = q.val := Nat.sub_add_cancel hlow'
      have hsubn : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
      have hi : i < n - 2 := by
        apply (Nat.sub_lt_sub_iff_right (by omega : 2 ≤ q.val)).2
        exact Nat.lt_of_lt_of_le (ZMod.val_lt q) (Nat.le_refl n)
      have hcoord : i + 2 = q.val := by dsimp [i]; omega
      have hsite : (registeredSite i : ZMod n) = q := by
        rw [registeredSite_cast, hcoord]
        exact hqcast
      refine ⟨registeredSite i, ?_, hsite⟩
      exact List.mem_cons.mpr (Or.inr (List.mem_map.mpr
        ⟨i, List.mem_range.mpr hi, rfl⟩))
    · rintro ⟨x, hx, hcast⟩
      change x ∈ 0 :: (List.range (n - 2)).map registeredSite at hx
      rcases List.mem_cons.mp hx with hx | hx
      · subst x
        simp at hcast
        exact False.elim (hq0 hcast.symm)
      · rcases List.mem_map.mp hx with ⟨i, hi, rfl⟩
        have hi' : i < n - 2 := List.mem_range.mp hi
        have hlt : i + 2 < n := by omega
        have hzero := registeredSite_ne_zero (n := n) i hlt
        have hone := registeredSite_ne_one hn i hlt
        rw [← hcast, allRRegistered_other _ hzero hone]
        simp

private theorem consecutiveGaps_append_one (xs : List ℤ) (hxs : xs ≠ [])
    (z : ℤ) :
    consecutiveGaps (xs ++ [z]) =
      consecutiveGaps xs ++ [z - xs.getLast hxs - 1] := by
  induction xs using List.twoStepInduction generalizing z with
  | nil => contradiction
  | singleton x => simp [consecutiveGaps]
  | cons_cons x y rest _ ih =>
      have hrest : y :: rest ≠ [] := by simp
      have h := ih y hrest z
      have hlast : (x :: y :: rest).getLast (by simp) =
          (y :: rest).getLast hrest := by rfl
      change (y - x - 1) :: consecutiveGaps ((y :: rest) ++ [z]) =
        (y - x - 1) :: (consecutiveGaps (y :: rest) ++
          [z - (x :: y :: rest).getLast hxs - 1])
      rw [h, hlast]

private theorem replicate_zero_append (m : ℕ) :
    List.replicate m (0 : ℤ) ++ [0] = 0 :: List.replicate m 0 := by
  induction m with
  | zero => rfl
  | succ m ih =>
      simp only [List.replicate_succ]
      exact congrArg (fun xs : List ℤ => (0 : ℤ) :: xs) ih

private theorem consecutiveGaps_registered (m : ℕ) :
    consecutiveGaps
        (0 :: ((List.range m).map registeredSite ++ [((m + 2 : ℕ) : ℤ)])) =
      1 :: List.replicate m 0 := by
  induction m with
  | zero => simp [consecutiveGaps, registeredSite]
  | succ m ih =>
      rw [List.range_succ, List.map_append, List.map_singleton]
      change consecutiveGaps
          ((0 :: (List.map registeredSite (List.range m) ++ [registeredSite m])) ++
            [((m + 3 : ℕ) : ℤ)]) = _
      rw [show 0 :: (List.map registeredSite (List.range m) ++ [registeredSite m]) =
          0 :: (List.map registeredSite (List.range m) ++ [((m + 2 : ℕ) : ℤ)]) by
            simp [registeredSite]]
      rw [consecutiveGaps_append_one _ (by simp) ((m + 3 : ℕ) : ℤ)]
      rw [ih]
      have hbase :
          (0 :: (List.map registeredSite (List.range m) ++
            [((m + 2 : ℕ) : ℤ)])) =
            (0 :: List.map registeredSite (List.range m)) ++
              [((m + 2 : ℕ) : ℤ)] := by simp
      have hlast :
          ((m + 3 : ℕ) : ℤ) -
            (0 :: (List.map registeredSite (List.range m) ++
              [((m + 2 : ℕ) : ℤ)])).getLast (by simp) - 1 = 0 := by
        have hlast' :
            (0 :: (List.map registeredSite (List.range m) ++
              [((m + 2 : ℕ) : ℤ)])).getLast (by simp) =
                ((m + 2 : ℕ) : ℤ) := by
          simpa using List.getLast_append_singleton
            (0 :: List.map registeredSite (List.range m))
        rw [hlast']
        norm_num
      rw [hlast]
      simpa [List.replicate_succ] using
        congrArg (List.cons (1 : ℤ)) (replicate_zero_append m)

theorem allRRegistered_gapRep {n : ℕ} [NeZero n] (hn : 3 ≤ n) :
    GapRep (allRRegistered (n := n)) 0 (initialGaps n) := by
  refine ⟨step_ordered (allRSelectedPair n) (singletonExecution n) .d
    (by omega) singletonExecution_ordered, registeredRing n, ?_, ?_, ?_⟩
  · exact registeredRing_support hn
  · simpa [registeredRing] using
      (show (0 : ZMod n) ∈
        ((allRRegistered (n := n)).placed (0 : ZMod n)).getD ∅ by
          simp [allRRegistered_zero, allRSelectedPair])
  · have hnsub : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
    simpa [registeredRing, PhysicalPacketRing.gaps, PhysicalPacketRing.sites,
      initialGaps, hnsub] using (consecutiveGaps_registered (n - 2)).symm

private def terminalRing (n : ℕ) : PhysicalPacketRing n where
  head := (n - 1 : ℕ)
  tail := []
  increasing := by simp
  below_end := by simp

theorem allREndpoint_gapRep {n : ℕ} [NeZero n]
    (s : Execution n (ZMod n))
    (horder : SourceOrdered s.placed)
    (hend : s.placed = allREndpoint (n := n)) :
    GapRep s 0 [((n - 1 : ℕ) : ℤ)] := by
  refine ⟨horder, terminalRing n, ?_, ?_, ?_⟩
  · intro q
    rw [hend]
    constructor
    · intro h
      by_cases hq : q = ((n - 1 : ℕ) : ZMod n)
      · refine ⟨(n - 1 : ℕ), by simp [terminalRing, PhysicalPacketRing.sites], ?_⟩
        simpa [hq]
      · simp [allREndpoint, hq] at h
    · rintro ⟨x, hx, hq⟩
      have hx' : x = ((n - 1 : ℕ) : ℤ) := by
        simpa [terminalRing, PhysicalPacketRing.sites] using hx
      subst x
      simpa [allREndpoint] using hq.symm
  · simp [hend, allREndpoint, terminalRing]
  · have hnpos : 0 < n := NeZero.pos n
    have hsub : (n - 1 : ℕ) + 1 = n := Nat.sub_add_cancel (by omega)
    have hsubZ : ((n - 1 : ℕ) : ℤ) = (n : ℤ) - 1 := by
      simpa using (Int.ofNat_sub (m := 1) (n := n) (by omega))
    simp [terminalRing, PhysicalPacketRing.gaps, consecutiveGaps, hsubZ]

theorem PhysicalTrace.fusionSteps_eq_completeFusionLog_length
    {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ}
    (trace : PhysicalTrace F a s word t g h) :
    trace.toExecutionTrace.fusionSteps =
      (completeFusionLog F s word).length := by
  induction trace with
  | nil hrep => rfl
  | @p s0 word0 t0 g0 h0 hrep rest ih =>
      simpa [PhysicalTrace.toExecutionTrace, ExecutionTrace.fusionSteps,
        completeFusionLog] using ih
  | @d s0 word0 t0 g0 h0 k0 hrep transition hnext hmatch rest ih =>
      simp only [PhysicalTrace.toExecutionTrace, ExecutionTrace.fusionSteps,
        completeFusionLog]
      rw [ih, hmatch.fusion]
      cases h0' : s0.placed 0 <;> cases h1' : s0.placed 1 <;>
        simp [h0', h1'] <;> omega

theorem allRTraceExtraction_of_realizes
    {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    ∃ cert : AllRTraceExtraction n, cert.word = word := by
  obtain ⟨reg, inter, tail, afterInter, hword, hprefix, hstart,
    hintervals, hpostlog, hmarked, hfree, hright⟩ := h.fusion_intervals hn
  have hrun : run (allRSelectedPair n) allRRegistered (inter ++ tail) =
      run (allRSelectedPair n) (singletonExecution n) word := by
    rw [← hstart, ← run_append, hword]
  have hend : (run (allRSelectedPair n) allRRegistered (inter ++ tail)).placed =
      allREndpoint (n := n) := by
    rw [hrun, h.endpoint_eq]
  have hstartRep : GapRep (allRRegistered (n := n)) 0 (initialGaps n) :=
    allRRegistered_gapRep hn
  obtain ⟨gap, ⟨physical⟩⟩ := physicalTrace_exists
    (allRSelectedPair n) (a := (0 : ZMod n))
      (s := allRRegistered (n := n)) (g := initialGaps n)
      (by omega) hstartRep (inter ++ tail) hright
  have horder : SourceOrdered (allRRegistered (n := n)).placed :=
    step_ordered (allRSelectedPair n) (singletonExecution n) .d
      (by omega) singletonExecution_ordered
  have hterminalRep :
      GapRep (run (allRSelectedPair n) allRRegistered (inter ++ tail))
        0 [((n - 1 : ℕ) : ℤ)] :=
    allREndpoint_gapRep _ (run_ordered _ _ _ (by omega) horder) hend
  have hgap : gap = [((n - 1 : ℕ) : ℤ)] :=
    gapRep_unique physical.end_rep hterminalRep
  rw [hgap] at physical
  have htraceFusion : physical.toExecutionTrace.fusionSteps = n - 2 := by
    rw [physical.fusionSteps_eq_completeFusionLog_length, hpostlog,
      allRPostLog_length]
  have htailRun : run (allRSelectedPair n) afterInter tail =
      run (allRSelectedPair n) allRRegistered (inter ++ tail) := by
    rw [← hintervals.run_eq]
    simp [run_append]
  have htailEnd :
      ∃ D, (run (allRSelectedPair n) afterInter tail).placed
          (n - 1 : ℕ) = some D ∧ (0 : ZMod n) ∈ D := by
    refine ⟨Finset.univ, ?_, ?_⟩
    · rw [htailRun, hend]
      simp [allREndpoint]
    · simp
  have hstartPacket :
      ∃ C, (allRRegistered (n := n)).placed 0 = some C ∧ (0 : ZMod n) ∈ C := by
    exact ⟨allRSelectedPair n, allRRegistered_zero, by simp [allRSelectedPair]⟩
  have hafterPacket :
      ∃ C, afterInter.placed 0 = some C ∧ (0 : ZMod n) ∈ C := by
    cases h0 : afterInter.placed 0 with
    | none => simp [h0] at hmarked
    | some C => exact ⟨C, rfl, by simpa [h0] using hmarked⟩
  refine ⟨
    { F := allRSelectedPair n
      carrier := 0
      registrationPrefix := reg
      registrationRun := hstart
      interWord := inter
      tail := tail
      start := allRRegistered
      afterInter := afterInter
      intervals := hintervals
      ordered := horder
      startPacket := hstartPacket
      afterPacket := hafterPacket
      tailEnd := htailEnd
      trace := physical.toExecutionTrace
      traceFusionSteps := htraceFusion
      prefixD := hprefix
      word := word
      word_eq := by simpa [List.append_assoc] using hword
      return_dominates := by
        exact le_of_eq (PhysicalTrace.backslides_eq_returns physical) }, ?_⟩
  rfl

end FusionLogAllR
