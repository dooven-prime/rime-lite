import RSR2.LowerPacketLedger

/-!
# Total packet rank along the original guarded execution

The independent observer records effective fusions on both layers. An elevator
deletes one lower packet and creates one upper packet, without changing total
rank. Its guard and its whole-packet semantics are unchanged.
-/

namespace RSR2.Parametric

def swapLayers (P : Placement n) : Placement n := fun a => (!(P a).1, (P a).2)

noncomputable def upperPacketCount (P : Placement n) : Nat := lowerPacketCount (swapLayers P)

noncomputable def totalPacketCount (P : Placement n) : Nat :=
  lowerPacketCount P + upperPacketCount P

noncomputable def upperFusionCharge (n : Nat) (hn : 1 < n)
    (P : Placement n) : Letter → Nat := by
  classical
  intro letter
  exact match letter with
  | .d true => if occupiedAt P true (site0 n (by omega)) ∧
      occupiedAt P true (site1 n hn) then 1 else 0
  | _ => 0

theorem occupiedAt_swapLayers (P : Placement n) (layer : Bool) (q : Site n) :
    occupiedAt (swapLayers P) layer q ↔ occupiedAt P (!layer) q := by
  unfold occupiedAt packet swapLayers
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨a, ?_⟩
    cases hPa : P a with
    | mk l r => cases l <;> cases layer <;> simp_all
  · rintro ⟨a, ha⟩
    refine ⟨a, ?_⟩
    cases hPa : P a with
    | mk l r => cases l <;> cases layer <;> simp_all

theorem upperPacketCount_eq_countP (P : Placement n) :
    upperPacketCount P = (by
      classical
      exact (List.finRange n).countP (fun q => decide (occupiedAt P true q))) := by
  classical
  unfold upperPacketCount lowerPacketCount
  apply List.countP_congr
  intro q _
  simp only [decide_eq_true_eq]
  exact occupiedAt_swapLayers P false q

private theorem swapLayers_rotate (n : Nat) (hn : 0 < n)
    (P : Placement n) (layer : Bool) :
    swapLayers (rotate n hn P layer) = rotate n hn (swapLayers P) (!layer) := by
  funext a
  cases hPa : P a with
  | mk l q => cases l <;> cases layer <;> simp [swapLayers, rotate, hPa]

private theorem swapLayers_collapse (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Bool) :
    swapLayers (collapse n hn P layer) = collapse n hn (swapLayers P) (!layer) := by
  funext a
  cases hPa : P a with
  | mk l q =>
      cases l <;> cases layer <;>
        by_cases hq : q = site1 n hn <;> simp [swapLayers, collapse, hPa, hq]

theorem rotate_upperPacketCount (n : Nat) (hn : 0 < n)
    (P : Placement n) (layer : Bool) :
    upperPacketCount (rotate n hn P layer) = upperPacketCount P := by
  unfold upperPacketCount
  rw [swapLayers_rotate]
  exact rotate_lowerPacketCount n hn (swapLayers P) (!layer)

theorem collapse_upperPacketCount (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Bool) :
    upperPacketCount (collapse n hn P layer) + upperFusionCharge n hn P (.d layer) =
      upperPacketCount P := by
  classical
  have hcharge : upperFusionCharge n hn P (.d layer) =
      lowerFusionCharge n hn (swapLayers P) (.d (!layer)) := by
    cases layer <;> simp [upperFusionCharge, lowerFusionCharge, occupiedAt_swapLayers]
  unfold upperPacketCount
  rw [swapLayers_collapse, hcharge]
  exact collapse_lowerPacketCount n hn (swapLayers P) (!layer)

private theorem occupied_lift_upper_other (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Site n) (hq : q ≠ site0 n hn) :
    occupiedAt (liftPacket n hn P) true q ↔ occupiedAt P true q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet liftPacket at ha
    split at ha
    · exact False.elim (hq (congrArg Prod.snd ha).symm)
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (true, q) at ha
    exact ⟨a, by simp [packet, liftPacket, ha]⟩

theorem liftPacket_upperPacketCount (n : Nat) (hn : 0 < n)
    (P : Placement n) (hg : liftGuard n hn P) :
    upperPacketCount (liftPacket n hn P) = upperPacketCount P + 1 := by
  classical
  obtain ⟨a, ha⟩ := hg.1
  change P a = (false, site0 n hn) at ha
  have hafter : occupiedAt (liftPacket n hn P) true (site0 n hn) :=
    ⟨a, by simp [packet, liftPacket, ha]⟩
  have hperm := List.perm_cons_erase (List.mem_finRange (site0 n hn))
  have hbefore := hperm.countP_eq (fun q => decide (occupiedAt P true q))
  have hnext := hperm.countP_eq
    (fun q => decide (occupiedAt (liftPacket n hn P) true q))
  have hrest : ((List.finRange n).erase (site0 n hn)).countP
      (fun q => decide (occupiedAt (liftPacket n hn P) true q)) =
      ((List.finRange n).erase (site0 n hn)).countP
        (fun q => decide (occupiedAt P true q)) := by
    apply List.countP_congr
    intro q hq
    have hne : q ≠ site0 n hn := by
      intro h
      subst q
      exact (List.nodup_finRange n).not_mem_erase hq
    simp only [decide_eq_true_eq]
    exact occupied_lift_upper_other n hn P q hne
  simp only [List.countP_cons, hg.2, decide_false, Bool.false_eq_true,
    ↓reduceIte, Nat.add_zero, hafter, decide_true, hrest] at hbefore hnext
  rw [upperPacketCount_eq_countP, upperPacketCount_eq_countP]
  omega

theorem step_totalPacketCount_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hs : step n hn P letter = some Q) :
    totalPacketCount Q + lowerFusionCharge n hn P letter +
      upperFusionCharge n hn P letter = totalPacketCount P := by
  have hl := step_lowerPacketCount_balance n hn P Q letter hs
  have hu : upperPacketCount Q + upperFusionCharge n hn P letter =
      upperPacketCount P + (if letter = .v then 1 else 0) := by
    cases letter with
    | p layer =>
        have he : rotate n (by omega) P layer = Q := by
          simpa only [step_p, Option.some.injEq] using hs
        rw [← he]
        simp [upperFusionCharge, rotate_upperPacketCount]
    | d layer =>
        have he : collapse n hn P layer = Q := by
          simpa only [step_d, Option.some.injEq] using hs
        rw [← he]
        simpa using collapse_upperPacketCount n hn P layer
    | v =>
        obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
        simpa [upperFusionCharge] using liftPacket_upperPacketCount n (by omega) P hg
  unfold totalPacketCount
  omega

/-- Same raw history, with the two actual effective-fusion counters. -/
noncomputable def runWithPacketRankLedger (n : Nat) (hn : 1 < n) :
    Placement n → List Letter → Option (Placement n × Nat × Nat)
  | P, [] => some (P, 0, 0)
  | P, letter :: rest => (step n hn P letter).bind (fun P' =>
      (runWithPacketRankLedger n hn P' rest).map (fun result =>
        (result.1, lowerFusionCharge n hn P letter + result.2.1,
          upperFusionCharge n hn P letter + result.2.2)))

theorem runWithPacketRankLedger_project (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runWithPacketRankLedger n hn P word).map Prod.fst = run n hn P word := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithPacketRankLedger, run, hs]
      | some P' =>
          simpa [runWithPacketRankLedger, run, hs, Option.map_map,
            Function.comp_def] using ih P'

/-- The lower effective-fusion counter is exactly the one already used by
the lower packet ledger and the antipodal fusion gate. -/
theorem runWithPacketRankLedger_lower_agreement (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runWithPacketRankLedger n hn P word).map (fun r => (r.1, r.2.1)) =
      (runWithLowerPacketLedger n hn P word).map (fun r => (r.1, r.2.1)) := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithPacketRankLedger, runWithLowerPacketLedger, hs]
      | some P' =>
          have h := congrArg (Option.map (fun r =>
            (r.1, lowerFusionCharge n hn P letter + r.2))) (ih P')
          simpa [runWithPacketRankLedger, runWithLowerPacketLedger, hs,
            Option.map_map, Function.comp_def] using h

theorem upperFusionCharge_le_defect (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    upperFusionCharge n hn P letter ≤ if letter = .d true then 1 else 0 := by
  classical
  cases letter with
  | p _ => simp [upperFusionCharge]
  | v => simp [upperFusionCharge]
  | d layer => cases layer <;> simp [upperFusionCharge] <;> split <;> omega

/-- Total packet rank and the upper raw-defect budget on the same execution. -/
theorem runWithPacketRankLedger_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (f0 f1 : Nat)
    (hrun : runWithPacketRankLedger n hn P word = some (Q, f0, f1)) :
    totalPacketCount Q + f0 + f1 = totalPacketCount P ∧
      f1 ≤ rawUpperDefectCount word := by
  induction word generalizing P f0 f1 with
  | nil =>
      have h : P = Q ∧ 0 = f0 ∧ 0 = f1 := by
        simpa only [runWithPacketRankLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      simp [← h.1, ← h.2.1, ← h.2.2, rawUpperDefectCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithPacketRankLedger, hs] at hrun
      | some P' =>
          cases ht : runWithPacketRankLedger n hn P' rest with
          | none => simp [runWithPacketRankLedger, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, f, g⟩
              have h : R = Q ∧ lowerFusionCharge n hn P letter + f = f0 ∧
                  upperFusionCharge n hn P letter + g = f1 := by
                simpa only [runWithPacketRankLedger, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have hf := ih P' f g (by simpa [h.1] using ht)
              have hb := step_totalPacketCount_balance n hn P P' letter hs
              have hc := upperFusionCharge_le_defect n hn P letter
              have hd : rawUpperDefectCount (letter :: rest) = rawUpperDefectCount rest +
                  (if letter = .d true then 1 else 0) := by
                simp only [rawUpperDefectCount, List.count_cons, beq_iff_eq]
              constructor <;> omega

theorem run_exists_packetRankLedger (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (hrun : run n hn P word = some Q) :
    ∃ f0 f1, runWithPacketRankLedger n hn P word = some (Q, f0, f1) := by
  have hp := runWithPacketRankLedger_project n hn P word
  cases ht : runWithPacketRankLedger n hn P word with
  | none => simp [ht, hrun] at hp
  | some result =>
      rcases result with ⟨R, f0, f1⟩
      have hR : R = Q := by simpa [ht, hrun] using hp
      subst R
      exact ⟨f0, f1, rfl⟩

theorem seed_totalPacketCount (n : Nat) : totalPacketCount (seed n) = n := by
  classical
  have hu : upperPacketCount (seed n) = 0 := by
    rw [upperPacketCount_eq_countP]
    apply List.countP_eq_zero.mpr
    intro q _
    have hnot : ¬ occupiedAt (seed n) true q := by
      rintro ⟨a, ha⟩
      exact Bool.noConfusion (congrArg Prod.fst ha)
    simp [hnot]
  simp [totalPacketCount, seed_lowerPacketCount, hu]

/-- Exact two-layer fusion accounting for every successful seed history. -/
theorem singleton_run_packetRankLedger_balance (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q) :
    ∃ f0 f1, runWithPacketRankLedger n hn (seed n) word = some (Q, f0, f1) ∧
      lowerPacketCount Q + upperPacketCount Q + f0 + f1 = n ∧
      f1 ≤ rawUpperDefectCount word := by
  obtain ⟨f0, f1, hl⟩ := run_exists_packetRankLedger n hn (seed n) Q word hrun
  have hb := runWithPacketRankLedger_balance n hn (seed n) Q word f0 f1 hl
  rw [seed_totalPacketCount] at hb
  exact ⟨f0, f1, hl, hb⟩

/-- A duplicate-free list of all actual packet locations counts total rank.
The list contains packet identities through their locations, not just sites. -/
theorem totalPacketCount_eq_representatives_length (P : Placement n)
    (reps : List (Location n)) (hnd : reps.Nodup)
    (hmem : ∀ loc, loc ∈ reps ↔ ∃ a, P a = loc) :
    totalPacketCount P = reps.length := by
  classical
  let sites : List (Location n) :=
    (List.finRange n).map (fun q => (false, q)) ++
      (List.finRange n).map (fun q => (true, q))
  let live := sites.filter (fun loc => occupiedAt P loc.1 loc.2)
  have hsites : sites.Nodup := by
    apply List.nodup_append.mpr
    refine ⟨?_, ?_, ?_⟩
    · apply (List.nodup_finRange n).map
      intro a b hne h
      exact hne (congrArg Prod.snd h)
    · apply (List.nodup_finRange n).map
      intro a b hne h
      exact hne (congrArg Prod.snd h)
    · intro loc hl loc' hr he
      obtain ⟨a, _, ha⟩ := List.mem_map.mp hl
      obtain ⟨b, _, hb⟩ := List.mem_map.mp hr
      exact Bool.noConfusion (congrArg Prod.fst (ha.trans (he.trans hb.symm)))
  have hperm : live.Perm reps := by
    apply (List.perm_ext_iff_of_nodup (hsites.filter _) hnd).mpr
    intro loc
    have hall : loc ∈ sites := by
      cases loc with
      | mk layer q => cases layer <;> simp [sites]
    simp only [List.mem_filter, hall, true_and, decide_eq_true_eq]
    exact (hmem loc).symm
  have hcount : live.length = totalPacketCount P := by
    rw [totalPacketCount, upperPacketCount_eq_countP]
    unfold lowerPacketCount
    dsimp [live, sites]
    rw [List.filter_append, List.length_append]
    congr 1 <;> rw [List.filter_map, List.length_map, ← List.countP_eq_length_filter]
    all_goals
      apply List.countP_congr
      intro q _
      simp only [Function.comp_apply, occupiedAt, packet]
  exact hcount.symm.trans hperm.length_eq

end RSR2.Parametric
