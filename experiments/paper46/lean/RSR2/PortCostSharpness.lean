import RSR2.LowerPortGeometry
import RSR2.UpperPortVacancy

/-!
# Sharp raw lengths and lower-control costs for two literal upper endpoints

Both witnesses are raw five-letter words executed by the existing guarded
`run`. No macro is assigned unit cost. The all-upper full packet has exact
minimum raw length and lower-control cost `2*n-2` for `n >= 3`. The all-upper
singleton endpoint has exact minimum lower-control cost `2*n-1` and exact
minimum raw length `3*n-2` for `n > 1`. Its additional upper rotations are
forced by the independent receiver-vacancy budget.
-/

namespace RSR2.Parametric

/-- Initial lower fusion followed by `k` raw lower rotation/defect pairs. -/
def lowerCoalescencePrefix : Nat → List Letter
  | 0 => [.d false]
  | k + 1 => lowerCoalescencePrefix k ++ [.p false, .d false]

/-- The literal word `d0 (p0 d0)^(n-2) v`. -/
def fullPacketTransferWord (n : Nat) : List Letter :=
  lowerCoalescencePrefix (n - 2) ++ [.v]

/-- One full packet at the upper synchronization site. -/
def upperFullPacket (n : Nat) (hn : 0 < n) : Placement n :=
  fun _ => (true, site0 n hn)

/-- After `k` rotation/defect pairs the accumulated packet is at lower 0;
the not-yet-absorbed atoms retain their exact shifted physical coordinates. -/
def lowerCoalescenceStage (n : Nat) (hn : 0 < n) (k : Nat) : Placement n :=
  fun a => if h : a.val ≤ 1 ∨ n ≤ a.val + k then (false, site0 n hn)
    else (false, ⟨a.val + k, by omega⟩)

theorem lowerCoalescenceStage_initial (n : Nat) (hn : 1 < n) :
    collapse n hn (seed n) false = lowerCoalescenceStage n (by omega) 0 := by
  funext a
  by_cases hzero : a.val = 0
  · have ha : a = site0 n (by omega) := Fin.ext hzero
    simp [collapse, seed, lowerCoalescenceStage, ha, site0, site1, Fin.mk.injEq]
  · by_cases hone : a.val = 1
    · have ha : a = site1 n hn := Fin.ext hone
      simp [collapse, seed, lowerCoalescenceStage, ha, site0, site1]
    · have hle : ¬ a.val ≤ 1 := by omega
      have hlt := a.isLt
      have hne : a ≠ site1 n hn := by
        intro h
        exact hone (congrArg Fin.val h)
      simp [collapse, seed, lowerCoalescenceStage, hle, hne, Nat.not_le.mpr hlt]

theorem lowerCoalescenceStage_step (n : Nat) (hn : 1 < n) (k : Nat) :
    collapse n hn (rotate n (by omega) (lowerCoalescenceStage n (by omega) k) false)
      false = lowerCoalescenceStage n (by omega) (k + 1) := by
  funext a
  by_cases h : a.val ≤ 1 ∨ n ≤ a.val + k
  · have h' : a.val ≤ 1 ∨ n ≤ a.val + (k + 1) := by omega
    simp [lowerCoalescenceStage, h, h', rotate, collapse, next, site0, site1, hn]
  · have ha : 1 < a.val := by omega
    have hk : a.val + k < n := by omega
    by_cases hnext : a.val + k + 1 < n
    · have h' : ¬ (a.val ≤ 1 ∨ n ≤ a.val + (k + 1)) := by omega
      have hnext' : a.val + (k + 1) < n := by omega
      have hneq' : a.val + (k + 1) ≠ 1 := by omega
      simp [lowerCoalescenceStage, h, h', rotate, next, collapse,
        site1, Fin.mk.injEq, Nat.add_assoc, hnext', hneq']
    · have h' : a.val ≤ 1 ∨ n ≤ a.val + (k + 1) := by omega
      simp [lowerCoalescenceStage, h, h', rotate, next, hnext, collapse,
        site0, site1, Fin.mk.injEq]

theorem lowerCoalescencePrefix_run (n : Nat) (hn : 1 < n) (k : Nat) :
    run n hn (seed n) (lowerCoalescencePrefix k) =
      some (lowerCoalescenceStage n (by omega) k) := by
  induction k with
  | zero => simp [lowerCoalescencePrefix, run, step_d, lowerCoalescenceStage_initial]
  | succ k ih =>
      simp [lowerCoalescencePrefix, run_append, ih, run, step_p, step_d,
        lowerCoalescenceStage_step]

theorem lowerCoalescenceStage_terminal (n : Nat) (hn : 1 < n) :
    lowerCoalescenceStage n (by omega) (n - 2) =
      fun _ => (false, site0 n (by omega)) := by
  funext a
  have h : a.val ≤ 1 ∨ n ≤ a.val + (n - 2) := by omega
  simp [lowerCoalescenceStage, h]

theorem fullPacketTransferWord_run (n : Nat) (hn : 1 < n) :
    run n hn (seed n) (fullPacketTransferWord n) = some (upperFullPacket n (by omega)) := by
  have hguard : liftGuard n (by omega) (lowerCoalescenceStage n (by omega) (n - 2)) := by
    rw [lowerCoalescenceStage_terminal n hn]
    constructor
    · exact ⟨site0 n (by omega), rfl⟩
    · rintro ⟨a, ha⟩
      exact Bool.noConfusion (congrArg Prod.fst ha)
  have hstep := (step_v_eq_some_iff n hn _ _).mpr ⟨hguard, rfl⟩
  have hend : liftPacket n (by omega) (lowerCoalescenceStage n (by omega) (n - 2)) =
      upperFullPacket n (by omega) := by
    rw [lowerCoalescenceStage_terminal n hn]
    funext a
    simp [liftPacket, upperFullPacket]
  simp [fullPacketTransferWord, run_append, lowerCoalescencePrefix_run, run,
    hstep, hend]

theorem lowerCoalescencePrefix_counts (k : Nat) :
    lowerRotationCount (lowerCoalescencePrefix k) = k ∧
      lowerDefectCount (lowerCoalescencePrefix k) = k + 1 ∧
      verticalCount (lowerCoalescencePrefix k) = 0 ∧
      (lowerCoalescencePrefix k).length = 2 * k + 1 := by
  induction k with
  | zero => simp [lowerCoalescencePrefix, lowerRotationCount, lowerDefectCount, verticalCount]
  | succ k ih =>
      simp only [lowerCoalescencePrefix, lowerRotationCount, lowerDefectCount, verticalCount,
        List.count_append, List.length_append] at *
      simp only [List.count_cons, List.count_nil, List.length_cons, List.length_nil,
        beq_self_eq_true, ↓reduceIte, Nat.zero_add] at *
      simp at *
      omega

theorem fullPacketTransferWord_cost (n : Nat) (hn : 1 < n) :
    lowerRotationCount (fullPacketTransferWord n) = n - 2 ∧
      lowerDefectCount (fullPacketTransferWord n) = n - 1 ∧
      verticalCount (fullPacketTransferWord n) = 1 ∧
      lowerPortCost (fullPacketTransferWord n) = 2 * n - 2 ∧
      (fullPacketTransferWord n).length = 2 * n - 2 := by
  have hc := lowerCoalescencePrefix_counts (n - 2)
  simp only [fullPacketTransferWord, lowerPortCost, lowerRotationCount, lowerDefectCount,
    verticalCount, List.count_append, List.length_append] at *
  simp at *
  omega

theorem fullPacketTransferWord_ledger (n : Nat) (hn : 1 < n) :
    runWithLowerPacketLedger n hn (seed n) (fullPacketTransferWord n) =
      some (upperFullPacket n (by omega), n - 1, 0) := by
  obtain ⟨f, z, hl, hp, hd, _⟩ := singleton_run_exists_lowerPacketLedger n hn _
    (fullPacketTransferWord n) (fullPacketTransferWord_run n hn)
  have hk := lowerPacketCount_eq_zero_of_allUpper (upperFullPacket n (by omega))
    (by intro a; rfl)
  have hc := fullPacketTransferWord_cost n hn
  have hf : f = n - 1 := by omega
  have hz : z = 0 := by omega
  simpa [hf, hz] using hl

theorem upperFullPacket_optimal (n : Nat) (hn : 2 < n) :
    run n (by omega) (seed n) (fullPacketTransferWord n) =
        some (upperFullPacket n (by omega)) ∧
      (fullPacketTransferWord n).length = 2 * n - 2 ∧
      lowerPortCost (fullPacketTransferWord n) = 2 * n - 2 ∧
      ∀ word : List Letter,
        run n (by omega) (seed n) word = some (upperFullPacket n (by omega)) →
          2 * n - 2 ≤ word.length ∧ 2 * n - 2 ≤ lowerPortCost word := by
  have hc := fullPacketTransferWord_cost n (by omega)
  refine ⟨fullPacketTransferWord_run n (by omega), hc.2.2.2.2, hc.2.2.2.1, ?_⟩
  intro word hrun
  have hb := singleton_run_allUpper_control_lower_bound n hn _ word hrun (by intro a; rfl)
  exact ⟨hb.2.2, hb.2.1⟩

/-- The literal word `v (p0 p1 v)^k`, with no defect letters. -/
def singletonTransferPrefix : Nat → List Letter
  | 0 => [.v]
  | k + 1 => singletonTransferPrefix k ++ [.p false, .p true, .v]

def singletonTransferWord (n : Nat) : List Letter := singletonTransferPrefix (n - 1)

/-- After the initial elevator and `k` paired rotations/transfers, all
transferred atoms are upstairs at sites `0,...,k`; the rest are downstairs. -/
def singletonTransferStage (n : Nat) (_hn : 0 < n) (k : Nat) (hk : k < n) : Placement n :=
  fun a => if a.val = 0 then (true, ⟨k, hk⟩)
    else if h : n ≤ a.val + k then (true, ⟨a.val + k - n, by have := a.isLt; omega⟩)
    else (false, ⟨a.val + k, by omega⟩)

/-- The literal singleton endpoint: atom 0 at upper `n-1` and every other
atom `a` at upper `a-1`. The target fixes labels and physical coordinates. -/
def upperSingletonEndpoint (n : Nat) (hn : 0 < n) : Placement n :=
  fun a => (true, if a.val = 0 then ⟨n - 1, by omega⟩
    else ⟨a.val - 1, by have := a.isLt; omega⟩)

private theorem pairedRotations_apply (n : Nat) (hn : 0 < n)
    (P : Placement n) (a : Fin n) :
    rotate n hn (rotate n hn P false) true a = ((P a).1, next n hn (P a).2) := by
  rcases ha : P a with ⟨layer, q⟩
  cases layer <;> simp [rotate, ha]

theorem singletonTransferStage_guard (n : Nat) (hn : 1 < n) (k : Nat)
    (hk : k + 1 < n) :
    liftGuard n (by omega)
      (rotate n (by omega) (rotate n (by omega)
        (singletonTransferStage n (by omega) k (by omega)) false) true) := by
  constructor
  · let a : Fin n := ⟨n - (k + 1), by omega⟩
    refine ⟨a, ?_⟩
    have hzero : ¬ a.val = 0 := by dsimp [a]; omega
    have hsum : a.val + k = n - 1 := by dsimp [a]; omega
    have hpred : ¬ n ≤ n - 1 := by omega
    have hnext : ¬ (n - 1 + 1 < n) := by omega
    simp [packet, pairedRotations_apply, singletonTransferStage, hzero,
      next, hsum, site0, hpred, hnext]
  · rintro ⟨a, ha⟩
    change rotate n (by omega) (rotate n (by omega)
      (singletonTransferStage n (by omega) k (by omega)) false) true a =
        (true, site0 n (by omega)) at ha
    rw [pairedRotations_apply] at ha
    by_cases hzero : a.val = 0
    · have hv := congrArg (fun loc => loc.2.val) ha
      simp [singletonTransferStage, hzero, next, hk, site0] at hv
    · by_cases hwrap : n ≤ a.val + k
      · have hnext : a.val + k - n + 1 < n := by have := a.isLt; omega
        have hv := congrArg (fun loc => loc.2.val) ha
        simp [singletonTransferStage, hzero, hwrap, next, hnext, site0] at hv
      · have hl := congrArg Prod.fst ha
        simp [singletonTransferStage, hzero, hwrap] at hl

theorem singletonTransferStage_step (n : Nat) (hn : 1 < n) (k : Nat)
    (hk : k + 1 < n) :
    liftPacket n (by omega) (rotate n (by omega) (rotate n (by omega)
      (singletonTransferStage n (by omega) k (by omega)) false) true) =
        singletonTransferStage n (by omega) (k + 1) hk := by
  funext a
  unfold liftPacket
  rw [pairedRotations_apply]
  by_cases hzero : a.val = 0
  · simp [singletonTransferStage, hzero, next, hk]
  · by_cases hwrap : n ≤ a.val + k
    · have hwrap' : n ≤ a.val + (k + 1) := by omega
      have hnext : a.val + k - n + 1 < n := by have := a.isLt; omega
      simp [singletonTransferStage, hzero, hwrap, hwrap', next, hnext]
      omega
    · by_cases hwrap' : n ≤ a.val + (k + 1)
      · have hlast : a.val + k + 1 = n := by omega
        have hnext : ¬ a.val + k + 1 < n := by omega
        have hsite : a.val + (k + 1) - n = 0 := by omega
        simp [singletonTransferStage, hzero, hwrap, hwrap', next, hnext, hsite, site0]
      · have hnext : a.val + k + 1 < n := by omega
        have hnext' : a.val + (k + 1) < n := by omega
        simp [singletonTransferStage, hzero, hwrap, hwrap', next,
          site0, Fin.mk.injEq, Nat.add_assoc, hnext']

theorem singletonTransferPrefix_run (n : Nat) (hn : 1 < n) (k : Nat) (hk : k < n) :
    run n hn (seed n) (singletonTransferPrefix k) =
      some (singletonTransferStage n (by omega) k hk) := by
  induction k with
  | zero =>
      have hg : liftGuard n (by omega) (seed n) := by
        constructor
        · exact ⟨site0 n (by omega), rfl⟩
        · rintro ⟨a, ha⟩
          exact Bool.noConfusion (congrArg Prod.fst ha)
      have heq : liftPacket n (by omega) (seed n) =
          singletonTransferStage n (by omega) 0 hk := by
        funext a
        have hlt := a.isLt
        by_cases hz : a.val = 0
        · have ha : a = site0 n (by omega) := Fin.ext hz
          simp [liftPacket, seed, singletonTransferStage, ha, site0]
        · have ha : a ≠ site0 n (by omega) := by intro he; exact hz (congrArg Fin.val he)
          simp [liftPacket, seed, singletonTransferStage, ha, hz, Nat.not_le.mpr hlt]
      simp [singletonTransferPrefix, run, step, hg, heq]
  | succ k ih =>
      have hs := singletonTransferStage_guard n hn k hk
      have he := singletonTransferStage_step n hn k hk
      simp [singletonTransferPrefix, run_append, ih (by omega), run,
        step, hs, he]

theorem singletonTransferStage_terminal (n : Nat) (hn : 1 < n) :
    singletonTransferStage n (by omega) (n - 1) (by omega) =
      upperSingletonEndpoint n (by omega) := by
  funext a
  by_cases hz : a.val = 0
  · simp [singletonTransferStage, upperSingletonEndpoint, hz]
  · have hw : n ≤ a.val + (n - 1) := by omega
    simp [singletonTransferStage, upperSingletonEndpoint, hz, hw]
    omega

theorem singletonTransferWord_run (n : Nat) (hn : 1 < n) :
    run n hn (seed n) (singletonTransferWord n) =
      some (upperSingletonEndpoint n (by omega)) := by
  simp [singletonTransferWord, singletonTransferPrefix_run n hn (n - 1) (by omega),
    singletonTransferStage_terminal n hn]

theorem upperSingletonEndpoint_injective (n : Nat) (hn : 0 < n) :
    Function.Injective (upperSingletonEndpoint n hn) := by
  intro a b hab
  have hv := congrArg (fun loc => loc.2.val) hab
  by_cases ha : a.val = 0 <;> by_cases hb : b.val = 0
  all_goals simp [upperSingletonEndpoint, ha, hb] at hv
  all_goals apply Fin.ext; have := a.isLt; have := b.isLt; omega

theorem singletonTransferPrefix_counts (k : Nat) :
    lowerRotationCount (singletonTransferPrefix k) = k ∧
      lowerDefectCount (singletonTransferPrefix k) = 0 ∧
      verticalCount (singletonTransferPrefix k) = k + 1 ∧
      rawUpperRotationCount (singletonTransferPrefix k) = k ∧
      rawUpperDefectCount (singletonTransferPrefix k) = 0 ∧
      (singletonTransferPrefix k).length = 3 * k + 1 := by
  induction k with
  | zero => simp [singletonTransferPrefix, lowerRotationCount, lowerDefectCount, verticalCount,
      rawUpperRotationCount, rawUpperDefectCount]
  | succ k ih =>
      simp only [singletonTransferPrefix, lowerRotationCount, lowerDefectCount, verticalCount,
        rawUpperRotationCount, rawUpperDefectCount, List.count_append, List.length_append] at *
      simp at *
      omega

theorem singletonTransferWord_cost (n : Nat) (hn : 0 < n) :
    lowerPortCost (singletonTransferWord n) = 2 * n - 1 ∧
      (singletonTransferWord n).length = 3 * n - 2 ∧
      verticalCount (singletonTransferWord n) = n := by
  have hc := singletonTransferPrefix_counts (n - 1)
  simp only [singletonTransferWord, lowerPortCost] at *
  omega

theorem singletonTransferWord_ledger (n : Nat) (hn : 1 < n) :
    runWithLowerPacketLedger n hn (seed n) (singletonTransferWord n) =
      some (upperSingletonEndpoint n (by omega), 0, 0) := by
  obtain ⟨f, z, hl, _, hd, _⟩ := singleton_run_exists_lowerPacketLedger n hn _
    (singletonTransferWord n) (singletonTransferWord_run n hn)
  have hc : lowerDefectCount (singletonTransferWord n) = 0 :=
    (singletonTransferPrefix_counts (n - 1)).2.1
  have hf : f = 0 := by omega
  have hz : z = 0 := by omega
  simpa [hf, hz] using hl

/-- Packet equality is irreversible along any successful guarded history. -/
theorem run_samePacket_mono (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) (a b : Fin n)
    (hab : samePacket P a b) : samePacket Q a b := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      simpa [he] using hab
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some P' =>
          have ht : run n hn P' rest = some Q := by simpa [run, hs] using hrun
          apply ih P' ht
          cases letter with
          | p layer =>
              have he : rotate n (by omega) P layer = P' := by
                simpa only [step_p, Option.some.injEq] using hs
              exact he ▸ (rotate_samePacket_iff n hn P layer a b).mpr hab
          | d layer =>
              have he : collapse n hn P layer = P' := by
                simpa only [step_d, Option.some.injEq] using hs
              exact he ▸ collapse_preserves_existing_packet_eq n hn P layer a b hab
          | v => exact (successful_lift_preserves_partition n hn P P' hs a b).mpr hab

theorem run_injective_of_terminal (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) (hinj : Function.Injective Q) :
    Function.Injective P := by
  intro a b hab
  exact hinj (run_samePacket_mono n hn P Q word hrun a b hab)

private theorem fusionCharge_zero_of_injective_step (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hs : step n hn P letter = some Q)
    (hinj : Function.Injective Q) : lowerFusionCharge n hn P letter = 0 := by
  classical
  cases letter with
  | p _ => simp [lowerFusionCharge]
  | v => simp [lowerFusionCharge]
  | d layer =>
      cases layer with
      | true => simp [lowerFusionCharge]
      | false =>
          have he : collapse n hn P false = Q := by
            simpa only [step_d, Option.some.injEq] using hs
          by_cases hc : occupiedAt P false (site0 n (by omega)) ∧
              occupiedAt P false (site1 n hn)
          · obtain ⟨⟨a, ha⟩, ⟨b, hb⟩⟩ := hc
            have hsame : samePacket Q a b := by
              rw [← he]
              exact (collapse_samePacket_iff n hn P false a b).mpr (Or.inr (Or.inl ⟨ha, hb⟩))
            have hab := hinj hsame
            subst b
            have hports : (false, site0 n (by omega)) = (false, site1 n hn) := ha.symm.trans hb
            have hv := congrArg (fun loc => loc.2.val) hports
            simp [site0, site1] at hv
          · simp [lowerFusionCharge, hc]

/-- A singleton endpoint rules out every effective lower fusion, including
ones before arbitrary upper operations and whole-packet transfers. -/
theorem runWithLowerPacketLedger_fusions_zero_of_injective (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn P word = some (Q, fusions, nonfusions))
    (hinj : Function.Injective Q) : fusions = 0 := by
  induction word generalizing P fusions nonfusions with
  | nil =>
      have h : P = Q ∧ 0 = fusions ∧ 0 = nonfusions := by
        simpa only [runWithLowerPacketLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      omega
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
              have ht' : runWithLowerPacketLedger n hn P' rest = some (Q, f, z) := by
                simpa [h.1] using ht
              have hf := ih P' f z ht'
              have hplain : run n hn P' rest = some Q := by
                have hp := runWithLowerPacketLedger_project n hn P' rest
                rw [ht'] at hp
                exact hp.symm
              have hp := run_injective_of_terminal n hn P' Q rest hplain hinj
              have hone := fusionCharge_zero_of_injective_step n hn P P' letter hs hp
              omega

theorem singleton_run_allUpper_singletons_cost_lower_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q)
    (hupper : ∀ a, (Q a).1 = true) (hinj : Function.Injective Q) :
    verticalCount word = n ∧ 2 * n - 1 ≤ lowerPortCost word := by
  obtain ⟨f, z, hl, hpackets, _, hport⟩ := singleton_run_exists_lowerPacketLedger n hn Q word hrun
  have hf := runWithLowerPacketLedger_fusions_zero_of_injective n hn (seed n) Q word f z hl hinj
  have hz := lowerPacketCount_eq_zero_of_allUpper Q hupper
  have hrefill := singleton_ledger_refill_bound n hn Q word f z hl
  constructor <;> omega

/-- Every all-upper singleton endpoint requires at least `n-1` upper
rotations to replenish the vacancies consumed by its `n` elevators. -/
theorem singleton_run_allUpper_singletons_rotation_lower_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q)
    (hupper : ∀ a, (Q a).1 = true) (hinj : Function.Injective Q) :
    n - 1 ≤ rawUpperRotationCount word := by
  have hv := (singleton_run_allUpper_singletons_cost_lower_bound n hn Q word hrun hupper hinj).1
  have hbudget := singleton_run_upperPortVacancy_bound n hn Q word hrun
  omega

/-- The lower control cost and the upper receiver replenishment cost pay
for disjoint raw letters, giving a bound for every all-upper singleton target. -/
theorem singleton_run_allUpper_singletons_length_lower_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q)
    (hupper : ∀ a, (Q a).1 = true) (hinj : Function.Injective Q) :
    3 * n - 2 ≤ word.length := by
  have hcost := (singleton_run_allUpper_singletons_cost_lower_bound n hn Q word hrun hupper hinj).2
  have hrot := singleton_run_allUpper_singletons_rotation_lower_bound n hn Q word hrun hupper hinj
  have hsplit := word_length_eq_lowerPortCost_add_upper word
  omega

/-- Exact lower control-letter cost for the specified literal endpoint.
`upperSingletonEndpoint_optimal` also records exact raw-length optimality. -/
theorem upperSingletonEndpoint_port_optimal (n : Nat) (hn : 1 < n) :
    run n hn (seed n) (singletonTransferWord n) =
        some (upperSingletonEndpoint n (by omega)) ∧
      lowerPortCost (singletonTransferWord n) = 2 * n - 1 ∧
      (singletonTransferWord n).length = 3 * n - 2 ∧
      ∀ word : List Letter,
        run n hn (seed n) word = some (upperSingletonEndpoint n (by omega)) →
          2 * n - 1 ≤ lowerPortCost word := by
  have hc := singletonTransferWord_cost n (by omega)
  refine ⟨singletonTransferWord_run n hn, hc.1, hc.2.1, ?_⟩
  intro word hrun
  exact (singleton_run_allUpper_singletons_cost_lower_bound n hn _ word hrun
    (by intro a; rfl) (upperSingletonEndpoint_injective n (by omega))).2

/-- The same guarded witness attains both exact minima at the specified
literal singleton endpoint. The bounds quantify over every successful raw
realization; irreversibility rules out effective prefusions within the proof. -/
theorem upperSingletonEndpoint_optimal (n : Nat) (hn : 1 < n) :
    run n hn (seed n) (singletonTransferWord n) =
        some (upperSingletonEndpoint n (by omega)) ∧
      (singletonTransferWord n).length = 3 * n - 2 ∧
      lowerPortCost (singletonTransferWord n) = 2 * n - 1 ∧
      ∀ word : List Letter,
        run n hn (seed n) word = some (upperSingletonEndpoint n (by omega)) →
          3 * n - 2 ≤ word.length ∧ 2 * n - 1 ≤ lowerPortCost word := by
  have hc := singletonTransferWord_cost n (by omega)
  refine ⟨singletonTransferWord_run n hn, hc.2.1, hc.1, ?_⟩
  intro word hrun
  have hupper : ∀ a, (upperSingletonEndpoint n (by omega) a).1 = true := by intro a; rfl
  have hinj := upperSingletonEndpoint_injective n (by omega)
  exact ⟨singleton_run_allUpper_singletons_length_lower_bound n hn _ word hrun hupper hinj,
    (singleton_run_allUpper_singletons_cost_lower_bound n hn _ word hrun hupper hinj).2⟩

end RSR2.Parametric
