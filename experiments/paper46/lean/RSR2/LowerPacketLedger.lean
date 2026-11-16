import RSR2.Parameterized

/-!
# Lower packet reduction and lower control-letter accounting

Packets are counted by occupied physical sites, not by atom mass. The history
observer replays the original guarded `step` and charges a lower fusion only
when both lower defect ports are occupied immediately before a `d false`.
Nonfusing lower defects, including ineffective ones, are counted separately.
No source-order or prescribed loading strategy is assumed.
The legacy name `lowerPortCost` denotes the number of lower control letters
`p false`, `d false`, and `v`, not the number of physical sync-port visits.
-/

namespace RSR2.Parametric

/-- Number of actual nonempty lower packets. -/
noncomputable def lowerPacketCount (P : Placement n) : Nat := by
  classical
  exact (List.finRange n).countP (fun q => decide (occupiedAt P false q))

/-- Pre-step effective lower fusion indicator. -/
noncomputable def lowerFusionCharge (n : Nat) (hn : 1 < n)
    (P : Placement n) : Letter → Nat := by
  classical
  intro letter
  exact match letter with
  | .d false => if occupiedAt P false (site0 n (by omega)) ∧
      occupiedAt P false (site1 n hn) then 1 else 0
  | _ => 0

/-- Every other lower defect, whether a slide or an ineffective action. -/
noncomputable def lowerNonfusionCharge (n : Nat) (hn : 1 < n)
    (P : Placement n) : Letter → Nat
  | .d false => 1 - lowerFusionCharge n hn P (.d false)
  | _ => 0

def lowerRotationCount (word : List Letter) : Nat := word.count (.p false)
def lowerDefectCount (word : List Letter) : Nat := word.count (.d false)
def verticalCount (word : List Letter) : Nat := word.count .v
def rawUpperRotationCount (word : List Letter) : Nat := word.count (.p true)
def rawUpperDefectCount (word : List Letter) : Nat := word.count (.d true)

/-- Lower control-letter cost (port-facing cost), charging all lower defects.
This is not a count of physical visits to the synchronization port. -/
def lowerPortCost (word : List Letter) : Nat :=
  lowerRotationCount word + lowerDefectCount word + verticalCount word

/-- Actual replay with effective and nonfusing lower defect counts. Guard
failure is unchanged and returns `none`. -/
noncomputable def runWithLowerPacketLedger (n : Nat) (hn : 1 < n) :
    Placement n → List Letter → Option (Placement n × Nat × Nat)
  | P, [] => some (P, 0, 0)
  | P, letter :: rest =>
      (step n hn P letter).bind (fun P' =>
        (runWithLowerPacketLedger n hn P' rest).map (fun result =>
          (result.1, lowerFusionCharge n hn P letter + result.2.1,
            lowerNonfusionCharge n hn P letter + result.2.2)))

private theorem next_surjective (n : Nat) (hn : 0 < n) (q : Site n) :
    ∃ r, next n hn r = q := by
  by_cases hq : q.val = 0
  · refine ⟨⟨n - 1, by omega⟩, ?_⟩
    apply Fin.ext
    have hlast : ¬ (n - 1 + 1 < n) := by omega
    simp [next, hlast, hq]
  · refine ⟨⟨q.val - 1, by omega⟩, ?_⟩
    apply Fin.ext
    have hlt : q.val - 1 + 1 < n := by omega
    simp [next, hlt]
    omega

private theorem next_finRange_perm (n : Nat) (hn : 0 < n) :
    ((List.finRange n).map (next n hn)).Perm (List.finRange n) := by
  have hnd : ((List.finRange n).map (next n hn)).Nodup := by
    apply (List.nodup_finRange n).map (next n hn)
    intro a b hab heq
    exact hab (next_injective n hn heq)
  apply (List.perm_ext_iff_of_nodup hnd (List.nodup_finRange n)).mpr
  intro q
  simp only [List.mem_finRange, iff_true]
  obtain ⟨r, hr⟩ := next_surjective n hn q
  exact List.mem_map.mpr ⟨r, List.mem_finRange r, hr⟩

private theorem occupied_rotate_next (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Site n) :
    occupiedAt (rotate n hn P false) false (next n hn q) ↔
      occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    by_cases hl : (P a).1 = false
    · simp only [hl, if_true, Prod.mk.injEq, true_and] at ha
      exact ⟨a, Prod.ext hl (next_injective n hn ha)⟩
    · simp only [hl] at ha
      exact False.elim (hl (congrArg Prod.fst ha))
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, rotate, ha]⟩

theorem rotate_lowerPacketCount (n : Nat) (hn : 0 < n)
    (P : Placement n) (layer : Layer) :
    lowerPacketCount (rotate n hn P layer) = lowerPacketCount P := by
  classical
  cases layer with
  | false =>
      have hperm := next_finRange_perm n hn
      have hcount := hperm.countP_eq
        (fun q => decide (occupiedAt (rotate n hn P false) false q))
      rw [List.countP_map] at hcount
      unfold lowerPacketCount
      rw [← hcount]
      apply List.countP_congr
      intro q _
      simp only [Function.comp_apply, decide_eq_true_eq]
      exact occupied_rotate_next n hn P q
  | true =>
      unfold lowerPacketCount
      apply List.countP_congr
      intro q _
      simp only [decide_eq_true_eq]
      constructor
      · rintro ⟨a, ha⟩
        unfold packet rotate at ha
        split at ha
        · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
        · exact ⟨a, ha⟩
      · rintro ⟨a, ha⟩
        change P a = (false, q) at ha
        exact ⟨a, by simp [packet, rotate, ha]⟩

private theorem zero_ne_one (n : Nat) (hn : 1 < n) :
    site0 n (by omega) ≠ site1 n hn := by
  simp [site0, site1, Fin.mk.injEq]

private theorem countP_split_ports (n : Nat) (hn : 1 < n)
    (p : Site n → Bool) :
    (List.finRange n).countP p =
      (((List.finRange n).erase (site0 n (by omega))).erase (site1 n hn)).countP p +
        (if p (site0 n (by omega)) then 1 else 0) +
        (if p (site1 n hn) then 1 else 0) := by
  have hzero := List.perm_cons_erase (List.mem_finRange (site0 n (by omega)))
  have hmem : site1 n hn ∈ (List.finRange n).erase (site0 n (by omega)) := by
    rw [List.mem_erase_of_ne (Ne.symm (zero_ne_one n hn))]
    exact List.mem_finRange _
  have hperm := hzero.trans (List.Perm.cons _ (List.perm_cons_erase hmem))
  have hcount := hperm.countP_eq p
  simp only [List.countP_cons] at hcount
  omega

private theorem occupied_collapse_zero (n : Nat) (hn : 1 < n)
    (P : Placement n) :
    occupiedAt (collapse n hn P false) false (site0 n (by omega)) ↔
      occupiedAt P false (site0 n (by omega)) ∨
        occupiedAt P false (site1 n hn) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · rename_i h
      exact Or.inr ⟨a, h⟩
    · exact Or.inl ⟨a, ha⟩
  · rintro (⟨a, ha⟩ | ⟨a, ha⟩)
    · change P a = (false, site0 n (by omega)) at ha
      exact ⟨a, by simp [packet, collapse, ha, zero_ne_one n hn]⟩
    · change P a = (false, site1 n hn) at ha
      exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem not_occupied_collapse_one (n : Nat) (hn : 1 < n)
    (P : Placement n) :
    ¬ occupiedAt (collapse n hn P false) false (site1 n hn) := by
  rintro ⟨a, ha⟩
  unfold packet collapse at ha
  split at ha
  · exact zero_ne_one n hn (congrArg Prod.snd ha)
  · rename_i h
    exact h ha

private theorem occupied_collapse_other (n : Nat) (hn : 1 < n)
    (P : Placement n) (q : Site n)
    (hzero : q ≠ site0 n (by omega)) (hone : q ≠ site1 n hn) :
    occupiedAt (collapse n hn P false) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · exact False.elim (hzero (congrArg Prod.snd ha).symm)
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, collapse, ha, hone]⟩

/-- Only an effective lower fusion decreases the lower packet count. A
nonfusing slide and an ineffective defect both preserve it. -/
theorem collapse_lowerPacketCount (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) :
    lowerPacketCount (collapse n hn P layer) +
      lowerFusionCharge n hn P (.d layer) = lowerPacketCount P := by
  classical
  cases layer with
  | false =>
      have hrest :
          (((List.finRange n).erase (site0 n (by omega))).erase (site1 n hn)).countP
            (fun q => decide (occupiedAt (collapse n hn P false) false q)) =
          (((List.finRange n).erase (site0 n (by omega))).erase (site1 n hn)).countP
            (fun q => decide (occupiedAt P false q)) := by
        apply List.countP_congr
        intro q hq
        have hzero : q ≠ site0 n (by omega) := by
          intro h
          subst q
          exact (List.nodup_finRange n).not_mem_erase (List.mem_of_mem_erase hq)
        have hone : q ≠ site1 n hn := by
          intro h
          subst q
          exact ((List.nodup_finRange n).erase _).not_mem_erase hq
        simp only [decide_eq_true_eq]
        exact occupied_collapse_other n hn P q hzero hone
      unfold lowerPacketCount
      rw [countP_split_ports n hn, countP_split_ports n hn, hrest]
      have hz := occupied_collapse_zero n hn P
      have ho := not_occupied_collapse_one n hn P
      by_cases hzero : occupiedAt P false (site0 n (by omega)) <;>
        by_cases hone : occupiedAt P false (site1 n hn)
      all_goals simp [lowerFusionCharge, hz, ho, hzero, hone, Nat.add_assoc]
  | true =>
      simp only [lowerFusionCharge, Nat.add_zero]
      unfold lowerPacketCount
      apply List.countP_congr
      intro q _
      simp only [decide_eq_true_eq]
      constructor
      · rintro ⟨a, ha⟩
        unfold packet collapse at ha
        split at ha
        · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
        · exact ⟨a, ha⟩
      · rintro ⟨a, ha⟩
        change P a = (false, q) at ha
        exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem occupied_lift_lower_other (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Site n) (hq : q ≠ site0 n hn) :
    occupiedAt (liftPacket n hn P) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet liftPacket at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, liftPacket, ha, hq]⟩

private theorem not_occupied_lift_lower_zero (n : Nat) (hn : 0 < n)
    (P : Placement n) :
    ¬ occupiedAt (liftPacket n hn P) false (site0 n hn) := by
  rintro ⟨a, ha⟩
  unfold packet liftPacket at ha
  split at ha
  · exact Bool.noConfusion (congrArg Prod.fst ha)
  · rename_i h
    exact h ha

/-- Transferring a whole, possibly prefused packet removes exactly one lower
packet. The source occupancy is supplied by every successful elevator step. -/
theorem liftPacket_lowerPacketCount (n : Nat) (hn : 0 < n)
    (P : Placement n) (hsource : occupiedAt P false (site0 n hn)) :
    lowerPacketCount (liftPacket n hn P) + 1 = lowerPacketCount P := by
  classical
  have hperm := List.perm_cons_erase (List.mem_finRange (site0 n hn))
  have hbefore := hperm.countP_eq (fun q => decide (occupiedAt P false q))
  have hafter := hperm.countP_eq
    (fun q => decide (occupiedAt (liftPacket n hn P) false q))
  have hrest :
      ((List.finRange n).erase (site0 n hn)).countP
        (fun q => decide (occupiedAt (liftPacket n hn P) false q)) =
      ((List.finRange n).erase (site0 n hn)).countP
        (fun q => decide (occupiedAt P false q)) := by
    apply List.countP_congr
    intro q hq
    have hne : q ≠ site0 n hn := by
      intro h
      subst q
      exact (List.nodup_finRange n).not_mem_erase hq
    simp only [decide_eq_true_eq]
    exact occupied_lift_lower_other n hn P q hne
  simp only [List.countP_cons, not_occupied_lift_lower_zero, decide_false,
    Bool.false_eq_true, ↓reduceIte, Nat.add_zero, hsource, decide_true,
    hrest] at hbefore hafter
  unfold lowerPacketCount
  omega

theorem lowerFusionCharge_le_one (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    lowerFusionCharge n hn P letter ≤ 1 := by
  classical
  cases letter with
  | p _ => simp [lowerFusionCharge]
  | v => simp [lowerFusionCharge]
  | d layer => cases layer <;> simp [lowerFusionCharge] <;> split <;> omega

/-- Each lower defect pays exactly once, as either an effective fusion or a
nonfusion. No ineffective `d false` is discarded by the ledger. -/
theorem lowerDefectCharge_partition (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    lowerFusionCharge n hn P letter + lowerNonfusionCharge n hn P letter =
      if letter = .d false then 1 else 0 := by
  cases letter with
  | p _ => simp [lowerFusionCharge, lowerNonfusionCharge]
  | v => simp [lowerFusionCharge, lowerNonfusionCharge]
  | d layer =>
      cases layer with
      | false =>
          have h := lowerFusionCharge_le_one n hn P (.d false)
          simp only [lowerNonfusionCharge, ↓reduceIte]
          omega
      | true => simp [lowerFusionCharge, lowerNonfusionCharge]

/-- Packet balance for one successful raw letter, using its actual pre-step
ports. Upper actions and rotations do not reduce the lower packet count. -/
theorem step_lowerPacketCount_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (hstep : step n hn P letter = some Q) :
    lowerPacketCount Q + (if letter = .v then 1 else 0) +
      lowerFusionCharge n hn P letter = lowerPacketCount P := by
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      simp [lowerFusionCharge, rotate_lowerPacketCount]
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      simpa using collapse_lowerPacketCount n hn P layer
  | v =>
      obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      simpa [lowerFusionCharge] using liftPacket_lowerPacketCount n (by omega) P hg.1

theorem seed_lowerPacketCount (n : Nat) : lowerPacketCount (seed n) = n := by
  classical
  have hocc : ∀ q : Site n, occupiedAt (seed n) false q := fun q => ⟨q, rfl⟩
  simp [lowerPacketCount, hocc]

/-- Forgetting the two counters gives precisely the original guarded run,
including failure. -/
theorem runWithLowerPacketLedger_project (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runWithLowerPacketLedger n hn P word).map Prod.fst = run n hn P word := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithLowerPacketLedger, run, hs]
      | some P' =>
          simpa [runWithLowerPacketLedger, run, hs, Option.map_map,
            Function.comp_def] using ih P'

/-- Two exact all-history ledgers from any initial placement: lower packet
reduction, and the partition of all lower defect letters into the two charges. -/
theorem runWithLowerPacketLedger_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn P word = some (Q, fusions, nonfusions)) :
    lowerPacketCount Q + verticalCount word + fusions = lowerPacketCount P ∧
      fusions + nonfusions = lowerDefectCount word := by
  induction word generalizing P fusions nonfusions with
  | nil =>
      have h : P = Q ∧ 0 = fusions ∧ 0 = nonfusions := by
        simpa only [runWithLowerPacketLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      simp [h.1, ← h.2.1, ← h.2.2, verticalCount, lowerDefectCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithLowerPacketLedger, hs] at hrun
      | some P' =>
          cases ht : runWithLowerPacketLedger n hn P' rest with
          | none => simp [runWithLowerPacketLedger, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, f, z⟩
              have h : R = Q ∧ lowerFusionCharge n hn P letter + f = fusions ∧
                  lowerNonfusionCharge n hn P letter + z = nonfusions := by
                simpa only [runWithLowerPacketLedger, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have htail := ih P' f z (by simpa [h.1] using ht)
              have hletter := step_lowerPacketCount_balance n hn P P' letter hs
              have hcharges := lowerDefectCharge_partition n hn P letter
              have hv : verticalCount (letter :: rest) = verticalCount rest +
                  (if letter = .v then 1 else 0) := by
                simp only [verticalCount, List.count_cons, beq_iff_eq]
              have hd : lowerDefectCount (letter :: rest) = lowerDefectCount rest +
                  (if letter = .d false then 1 else 0) := by
                simp only [lowerDefectCount, List.count_cons, beq_iff_eq]
              constructor <;> omega

/-- Every successful original run has a ledger on exactly the same history;
no additional guards or execution hypotheses are imposed. -/
theorem run_exists_lowerPacketLedger (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) :
    ∃ fusions nonfusions,
      runWithLowerPacketLedger n hn P word = some (Q, fusions, nonfusions) ∧
      lowerPacketCount Q + verticalCount word + fusions = lowerPacketCount P ∧
      fusions + nonfusions = lowerDefectCount word := by
  have hproj := runWithLowerPacketLedger_project n hn P word
  cases ht : runWithLowerPacketLedger n hn P word with
  | none => simp [ht, hrun] at hproj
  | some result =>
      rcases result with ⟨R, f, z⟩
      have hR : R = Q := by simpa [ht, hrun] using hproj
      subst R
      exact ⟨f, z, rfl, runWithLowerPacketLedger_balance n hn P Q word f z ht⟩

/-- The exact lower port-cost balance separates productive packet reduction
from rotations and all nonfusing lower defects. -/
theorem runWithLowerPacketLedger_port_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn P word = some (Q, fusions, nonfusions)) :
    lowerPortCost word + lowerPacketCount Q =
      lowerPacketCount P + lowerRotationCount word + nonfusions := by
  obtain ⟨hpackets, hdefects⟩ :=
    runWithLowerPacketLedger_balance n hn P Q word fusions nonfusions hrun
  unfold lowerPortCost
  omega

/-- All five raw letters are charged once; the lower port cost is a sub-cost
of raw length, independent of whether the word is executable. -/
theorem word_length_eq_lowerPortCost_add_upper (word : List Letter) :
    word.length = lowerPortCost word + rawUpperRotationCount word + rawUpperDefectCount word := by
  induction word with
  | nil => simp [lowerPortCost, lowerRotationCount, lowerDefectCount, verticalCount,
      rawUpperRotationCount, rawUpperDefectCount]
  | cons letter rest ih =>
      cases letter with
      | p layer => cases layer <;>
          simp_all [lowerPortCost, lowerRotationCount, lowerDefectCount, verticalCount,
            rawUpperRotationCount, rawUpperDefectCount] <;> omega
      | d layer => cases layer <;>
          simp_all [lowerPortCost, lowerRotationCount, lowerDefectCount, verticalCount,
            rawUpperRotationCount, rawUpperDefectCount] <;> omega
      | v =>
          simp_all [lowerPortCost, lowerRotationCount, lowerDefectCount, verticalCount,
            rawUpperRotationCount, rawUpperDefectCount] <;> omega

theorem lowerPortCost_le_length (word : List Letter) : lowerPortCost word ≤ word.length := by
  have h := word_length_eq_lowerPortCost_add_upper word
  omega

/-- Singleton-seed specialization of both packet and port ledgers. -/
theorem singleton_run_lowerPacketLedger (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn (seed n) word = some (Q, fusions, nonfusions)) :
    lowerPacketCount Q + verticalCount word + fusions = n ∧
      fusions + nonfusions = lowerDefectCount word ∧
      lowerPortCost word + lowerPacketCount Q =
        n + lowerRotationCount word + nonfusions := by
  obtain ⟨hpackets, hdefects⟩ :=
    runWithLowerPacketLedger_balance n hn (seed n) Q word fusions nonfusions hrun
  have hport := runWithLowerPacketLedger_port_balance n hn (seed n) Q word
    fusions nonfusions hrun
  rw [seed_lowerPacketCount] at hpackets hport
  exact ⟨hpackets, hdefects, hport⟩

theorem singleton_run_exists_lowerPacketLedger (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (hrun : run n hn (seed n) word = some Q) :
    ∃ fusions nonfusions,
      runWithLowerPacketLedger n hn (seed n) word = some (Q, fusions, nonfusions) ∧
      lowerPacketCount Q + verticalCount word + fusions = n ∧
      fusions + nonfusions = lowerDefectCount word ∧
      lowerPortCost word + lowerPacketCount Q =
        n + lowerRotationCount word + nonfusions := by
  obtain ⟨f, z, hledger, _⟩ := run_exists_lowerPacketLedger n hn (seed n) Q word hrun
  exact ⟨f, z, hledger, singleton_run_lowerPacketLedger n hn Q word f z hledger⟩

/-- Unconditional lower control-letter bound for every legal singleton-seed word.
It does not assert a superlinear bound or optimize sync-port access. -/
theorem singleton_run_lowerPortCost_bounds (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (hrun : run n hn (seed n) word = some Q) :
    n - lowerPacketCount Q ≤ lowerPortCost word ∧ lowerPortCost word ≤ word.length := by
  obtain ⟨f, z, _, _, _, hport⟩ := singleton_run_exists_lowerPacketLedger n hn Q word hrun
  exact ⟨by omega, lowerPortCost_le_length word⟩

end RSR2.Parametric
