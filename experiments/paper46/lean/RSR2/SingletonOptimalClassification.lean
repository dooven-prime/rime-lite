import RSR2.SingletonElevatorSkeleton

/-!
# All shortest singleton words, from actual guarded runs

The tight-budget skeleton still admits lower defects. The literal target
excludes a first defect for `n >= 3`; the holes at lower sites 0 and 1 then
exclude all subsequent defects. Only independent rotation swaps remain.
-/

namespace RSR2.Parametric

theorem collapse_lower_rotate_upper_commute (n : Nat) (hn : 1 < n)
    (P : Placement n) :
    rotate n (by omega) (collapse n hn P false) true =
      collapse n hn (rotate n (by omega) P true) false := by
  funext a
  rcases h : P a with ⟨layer, q⟩
  cases layer <;> simp [rotate, collapse, h]
  split <;> simp_all

theorem singletonControlRound_run_eq (n : Nat) (hn : 1 < n)
    (P : Placement n) (defect swap : Bool) :
    run n hn P (singletonControlRound (defect, swap)) =
      run n hn P (singletonControlRound (defect, false)) := by
  cases swap with
  | false => rfl
  | true =>
      cases defect with
      | false =>
          simp [singletonControlRound, singletonLowerChoice, run, step_p]
          rw [rotate_lower_upper_commute]
      | true =>
          simp [singletonControlRound, singletonLowerChoice, run, step_p, step_d]
          rw [collapse_lower_rotate_upper_commute]

private def controlRoundPre (n : Nat) (hn : 1 < n) (P : Placement n)
    (defect : Bool) : Placement n :=
  rotate n (by omega)
    (if defect then collapse n hn P false else rotate n (by omega) P false) true

private theorem controlRound_result (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (defect swap : Bool)
    (hrun : run n hn P (singletonControlRound (defect, swap)) = some Q) :
    liftGuard n (by omega) (controlRoundPre n hn P defect) ∧
      Q = liftPacket n (by omega) (controlRoundPre n hn P defect) := by
  rw [singletonControlRound_run_eq] at hrun
  have hs : step n hn (controlRoundPre n hn P defect) .v = some Q := by
    cases defect <;>
      simpa [singletonControlRound, singletonLowerChoice, controlRoundPre,
        run, step_p, step_d] using hrun
  exact (step_v_eq_some_iff n hn _ _).mp hs

theorem singletonControlRound_upper_atom (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (choice : Bool × Bool) (a : Fin n) (q : Site n)
    (ha : P a = (true, q))
    (hrun : run n hn P (singletonControlRound choice) = some Q) :
    Q a = (true, next n (by omega) q) := by
  obtain ⟨_, he⟩ := controlRound_result n hn P Q choice.1 choice.2 hrun
  rw [he]
  cases choice.1 <;> simp [controlRoundPre, rotate, collapse, liftPacket, ha]

theorem singletonControlTail_upper_atom (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (choices : List (Bool × Bool)) (a : Fin n) (q : Site n)
    (ha : P a = (true, q))
    (hrun : run n hn P (singletonControlTail choices) = some Q) :
    Q a = (true, nextMany n (by omega) q choices.length) := by
  induction choices generalizing P q with
  | nil =>
      have he : P = Q := by simpa [singletonControlTail, run] using hrun
      simpa [he, nextMany] using ha
  | cons c cs ih =>
      change run n hn P (singletonControlRound c ++ singletonControlTail cs) = some Q at hrun
      rw [run_append] at hrun
      cases hs : run n hn P (singletonControlRound c) with
      | none => simp [hs] at hrun
      | some R =>
          have ht : run n hn R (singletonControlTail cs) = some Q := by simpa [hs] using hrun
          have har := singletonControlRound_upper_atom n hn P R c a q ha hs
          simpa [nextMany] using ih R (next n (by omega) q) har ht

private theorem first_defect_transfers_atom_one (n : Nat) (hn : 1 < n)
    (Q : Placement n) (swap : Bool)
    (hrun : run n hn (singletonTransferStage n (by omega) 0 (by omega))
      (singletonControlRound (true, swap)) = some Q) :
    Q (site1 n hn) = (true, site0 n (by omega)) := by
  obtain ⟨_, he⟩ := controlRound_result n hn _ Q true swap hrun
  rw [he]
  simp [controlRoundPre, singletonTransferStage, site1, site0, rotate, collapse,
    liftPacket, show ¬ n ≤ 1 by omega]

/-- At a canonical stage `k`, every remaining lower atom is strictly beyond
site `k`. In particular sites 0 and, after the first round, 1 are holes. -/
theorem singletonTransferStage_lower_site (n : Nat) (hn : 0 < n)
    (k : Nat) (hk : k < n) (a : Fin n) (q : Site n)
    (ha : singletonTransferStage n hn k hk a = (false, q)) : k < q.val := by
  by_cases hz : a.val = 0
  · simp [singletonTransferStage, hz] at ha
  · by_cases hw : n ≤ a.val + k
    · simp [singletonTransferStage, hz, hw] at ha
    · have hq := congrArg (fun l : Location n => l.2.val) ha
      simp [singletonTransferStage, hz, hw] at hq
      omega

private theorem stage_defect_round_impossible (n : Nat) (hn : 1 < n)
    (k : Nat) (hk : k < n) (hpos : 1 ≤ k) (Q : Placement n) (swap : Bool) :
    run n hn (singletonTransferStage n (by omega) k hk)
      (singletonControlRound (true, swap)) ≠ some Q := by
  intro hrun
  obtain ⟨hg, _⟩ := controlRound_result n hn _ Q true swap hrun
  obtain ⟨a, ha⟩ := hg.1
  change controlRoundPre n hn (singletonTransferStage n (by omega) k hk) true a =
    (false, site0 n (by omega)) at ha
  simp only [controlRoundPre, ite_true] at ha
  unfold rotate at ha
  split at ha
  · exact Bool.noConfusion (congrArg Prod.fst ha)
  · unfold collapse at ha
    split at ha
    · rename_i he
      have hb := singletonTransferStage_lower_site n (by omega) k hk a (site1 n hn) he
      simp [site1] at hb
      omega
    · have hb := singletonTransferStage_lower_site n (by omega) k hk a
        (site0 n (by omega)) ha
      simp [site0] at hb

theorem singletonControlRound_stage_run (n : Nat) (hn : 1 < n)
    (k : Nat) (hk : k + 1 < n) (swap : Bool) :
    run n hn (singletonTransferStage n (by omega) k (by omega))
      (singletonControlRound (false, swap)) =
        some (singletonTransferStage n (by omega) (k + 1) hk) := by
  rw [singletonControlRound_run_eq]
  have hg := singletonTransferStage_guard n hn k hk
  have he := singletonTransferStage_step n hn k hk
  simp [singletonControlRound, singletonLowerChoice, run, step, hg, he]

theorem singletonControlTail_no_defects_after_first_rotation (n : Nat) (hn : 1 < n)
    (k : Nat) (hk : k < n) (hpos : 1 ≤ k) (choices : List (Bool × Bool))
    (hlen : k + choices.length = n - 1)
    (hrun : run n hn (singletonTransferStage n (by omega) k hk)
      (singletonControlTail choices) = some (upperSingletonEndpoint n (by omega))) :
    ∀ c ∈ choices, c.1 = false := by
  induction choices generalizing k with
  | nil => simp
  | cons c cs ih =>
      rcases c with ⟨defect, swap⟩
      change run n hn _ (singletonControlRound (defect, swap) ++ singletonControlTail cs) =
        some _ at hrun
      rw [run_append] at hrun
      have hk' : k + 1 < n := by simp at hlen; omega
      cases defect with
      | true =>
          cases hs : run n hn (singletonTransferStage n (by omega) k hk)
              (singletonControlRound (true, swap)) with
          | none => simp [hs] at hrun
          | some R => exact False.elim ((stage_defect_round_impossible n hn k hk hpos R swap) hs)
      | false =>
          rw [singletonControlRound_stage_run n hn k hk' swap] at hrun
          have ht : run n hn (singletonTransferStage n (by omega) (k + 1) hk')
              (singletonControlTail cs) = some (upperSingletonEndpoint n (by omega)) := by
            simpa using hrun
          have hi := ih (k + 1) hk' (by omega) (by simp at hlen; omega) ht
          simp only [List.mem_cons] at *
          intro c hc
          rcases hc with rfl | hc
          · rfl
          · exact hi c hc

/-- The only use of the literal endpoint in excluding the first lower
defect: its second transfer would place atom 1 at upper `n-2`, not site 0. -/
theorem singletonControlTail_no_defects (n : Nat) (hn : 3 ≤ n)
    (choices : List (Bool × Bool)) (hlen : choices.length = n - 1)
    (hrun : run n (by omega) (singletonTransferStage n (by omega) 0 (by omega))
      (singletonControlTail choices) = some (upperSingletonEndpoint n (by omega))) :
    ∀ c ∈ choices, c.1 = false := by
  cases choices with
  | nil => simp at hlen; omega
  | cons c cs =>
      rcases c with ⟨defect, swap⟩
      have hcs : cs.length = n - 2 := by simp at hlen; omega
      change run n (by omega) _ (singletonControlRound (defect, swap) ++
        singletonControlTail cs) = some _ at hrun
      rw [run_append] at hrun
      cases defect with
      | true =>
          cases hs : run n (by omega) (singletonTransferStage n (by omega) 0 (by omega))
              (singletonControlRound (true, swap)) with
          | none => simp [hs] at hrun
          | some R =>
              have ht : run n (by omega) R (singletonControlTail cs) =
                  some (upperSingletonEndpoint n (by omega)) := by simpa [hs] using hrun
              have ha := first_defect_transfers_atom_one n (by omega) R swap hs
              have hend := singletonControlTail_upper_atom n (by omega) R _ cs
                (site1 n (by omega)) (site0 n (by omega)) ha ht
              have hv := congrArg (fun l : Location n => l.2.val) hend
              have hsmall : cs.length < n := by omega
              simp [upperSingletonEndpoint, site1, site0, nextMany_val, hcs,
                Nat.mod_eq_of_lt (show n - 2 < n by omega)] at hv
              omega
      | false =>
          rw [singletonControlRound_stage_run n (by omega) 0 (by omega) swap] at hrun
          have ht : run n (by omega) (singletonTransferStage n (by omega) 1 (by omega))
              (singletonControlTail cs) = some (upperSingletonEndpoint n (by omega)) := by
            simpa using hrun
          have hi := singletonControlTail_no_defects_after_first_rotation n (by omega)
            1 (by omega) (by omega) cs (by omega) ht
          intro c hc
          rcases List.mem_cons.mp hc with rfl | hc
          · rfl
          · exact hi c hc

theorem singletonVariantWord_controlTail (bits : List Bool) :
    singletonVariantWord bits = .v ::
      singletonControlTail (bits.reverse.map (fun b => (false, b))) := by
  induction bits with
  | nil => rfl
  | cons b bs ih =>
      simp only [singletonVariantWord, ih, List.reverse_cons, List.map_append,
        List.map_cons, List.map_nil, singletonControlTail, List.flatMap_append,
        List.flatMap_cons, List.flatMap_nil, List.append_nil, List.cons_append]
      rfl

theorem singletonControlTail_rotations_word (choices : List (Bool × Bool))
    (h : ∀ c ∈ choices, c.1 = false) :
    .v :: singletonControlTail choices =
      singletonVariantWord (choices.map Prod.snd).reverse := by
  have hm : choices.map (fun c => (false, c.2)) = choices := by
    induction choices with
    | nil => rfl
    | cons c cs ih =>
        have hc := h c (by simp)
        have ht : ∀ a ∈ cs, a.1 = false := by intro a ha; exact h a (by simp [ha])
        simp only [List.map_cons, ih ht]
        rcases c with ⟨defect, swap⟩
        change defect = false at hc
        subst defect
        rfl
  rw [singletonVariantWord_controlTail]
  simp [List.map_map, Function.comp_def, hm]

/-- Complete classification at the fixed literal singleton endpoint. -/
theorem singleton_optimal_iff_variant (n : Nat) (hn : 3 ≤ n)
    (word : List Letter) :
    (run n (by omega) (seed n) word =
        some (upperSingletonEndpoint n (by omega)) ∧ word.length = 3 * n - 2) ↔
      ∃ bits : List Bool, bits.length = n - 1 ∧ word = singletonVariantWord bits := by
  constructor
  · rintro ⟨hrun, hlen⟩
    obtain ⟨choices, hc, rfl⟩ := singleton_optimal_elevator_skeleton n (by omega) word hrun hlen
    have hprefix := singletonTransferPrefix_run n (by omega) 0 (by omega)
    change run n (by omega) (seed n) [.v] = some _ at hprefix
    change run n (by omega) (seed n) ([.v] ++ singletonControlTail choices) = some _ at hrun
    rw [run_append, hprefix] at hrun
    have ht : run n (by omega) (singletonTransferStage n (by omega) 0 (by omega))
        (singletonControlTail choices) = some (upperSingletonEndpoint n (by omega)) := by
      simpa using hrun
    have hd := singletonControlTail_no_defects n hn choices hc ht
    exact ⟨(choices.map Prod.snd).reverse, by simp [hc],
      singletonControlTail_rotations_word choices hd⟩
  · rintro ⟨bits, hbits, rfl⟩
    refine ⟨singletonVariantWord_run n (by omega) bits hbits, ?_⟩
    have hl := singletonVariantWord_length bits
    omega

end RSR2.Parametric
