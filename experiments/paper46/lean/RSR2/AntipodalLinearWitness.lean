import RSR2.AntipodalFusionGate

/-!
# Two-pass antipodal loading with spaced upper storage

The coordinate invariants below describe the actual five-letter guarded run.
All rotations and defects in the witness are primitive letters.
-/

namespace RSR2.Parametric

/-- Position in the extraction order `0, 2*m-1, ..., 1`. -/
def antipodalExtractionIndex (m : Nat) (a : Fin (2 * m)) : Nat :=
  if a.val = 0 then 0 else 2 * m - a.val

theorem antipodalExtractionIndex_lt (m : Nat) (hm : 0 < m) (a : Fin (2 * m)) :
    antipodalExtractionIndex m a < 2 * m := by
  unfold antipodalExtractionIndex
  split <;> omega

theorem antipodalExtractionIndex_zero_iff (m : Nat) (a : Fin (2 * m)) :
    antipodalExtractionIndex m a = 0 ↔ a.val = 0 := by
  unfold antipodalExtractionIndex
  split <;> have := a.isLt <;> omega

def antipodalFirstStage (m : Nat) (hm : 0 < m) (k : Nat)
    (hk : 1 ≤ k) (hkm : k ≤ m) : Placement (2 * m) := fun a =>
  let j := antipodalExtractionIndex m a
  if h : j < k then (true, ⟨2 * (k - 1 - j), by omega⟩)
  else (false, ⟨2 * m + k - 1 - j, by
    have := antipodalExtractionIndex_lt m hm a
    omega⟩)

def antipodalSecondStage (m : Nat) (hm : 0 < m) (k : Nat)
    (hk : 1 ≤ k) (hkm : k ≤ m) : Placement (2 * m) := fun a =>
  let j := antipodalExtractionIndex m a
  if hj : j < m then
    if h : j < k then (true, ⟨2 * (k - 1 - j), by omega⟩)
    else (true, ⟨2 * m + 2 * k - 1 - 2 * j, by omega⟩)
  else if h : j - m < k then (true, ⟨2 * (k - 1 - (j - m)), by omega⟩)
  else (false, ⟨2 * m + m + k - 1 - j, by
    have := antipodalExtractionIndex_lt m hm a
    omega⟩)

def antipodalFirstPrefix : Nat → List Letter
  | 0 => [.v]
  | k + 1 => antipodalFirstPrefix k ++ [.p false, .p true, .p true, .v]

def antipodalSecondSuffix : Nat → List Letter
  | 0 => []
  | k + 1 => antipodalSecondSuffix k ++ [.p false, .p true, .p true, .v, .d true]

def antipodalLinearWord (m : Nat) : List Letter :=
  antipodalFirstPrefix (m - 1) ++
    [.p false, .p true, .p true, .p true, .v, .d true] ++
    antipodalSecondSuffix (m - 1)

theorem antipodalFirstStage_initial (m : Nat) (hm : 0 < m) :
    run (2 * m) (by omega) (seed (2 * m)) [.v] =
      some (antipodalFirstStage m hm 1 (by omega) (by omega)) := by
  have hg : liftGuard (2 * m) (by omega) (seed (2 * m)) := by
    constructor
    · exact ⟨site0 _ (by omega), rfl⟩
    · rintro ⟨a, ha⟩
      exact Bool.noConfusion (congrArg Prod.fst ha)
  have he : liftPacket (2 * m) (by omega) (seed (2 * m)) =
      antipodalFirstStage m hm 1 (by omega) (by omega) := by
    funext a
    have hlt := a.isLt
    by_cases hzero : a.val = 0
    · simp [liftPacket, seed, antipodalFirstStage, antipodalExtractionIndex,
        hzero, site0, Fin.ext_iff]
    · have hj : ¬ antipodalExtractionIndex m a < 1 := by
        simp only [antipodalExtractionIndex, if_neg hzero]
        omega
      have hne : a ≠ site0 (2 * m) (by omega) := by
        intro he
        exact hzero (congrArg Fin.val he)
      simp only [liftPacket, seed, Prod.mk.injEq, true_and, hne, if_false,
        antipodalFirstStage, hj, ↓reduceDIte]
      apply Fin.ext
      simp only [antipodalExtractionIndex, hzero, if_false]
      omega
  have hs := (step_v_eq_some_iff (2 * m) (by omega) _ _).mpr ⟨hg, rfl⟩
  simp only [run, hs, Option.bind_some]
  exact congrArg some he

private theorem rotated_location (n : Nat) (hn : 0 < n) (P : Placement n)
    (a : Fin n) (upperTurns : Nat) :
    rotateMany n hn (rotate n hn P false) true upperTurns a =
      if (P a).1 then (true, nextMany n hn (P a).2 upperTurns)
      else (false, next n hn (P a).2) := by
  cases hPa : P a with
  | mk layer q => cases layer <;> simp [rotateMany_apply, rotate, hPa]

theorem antipodalFirstStage_step (m : Nat) (hm : 0 < m) (k : Nat)
    (hk : 1 ≤ k) (hkm : k < m) :
    run (2 * m) (by omega) (antipodalFirstStage m hm k hk (by omega))
      [.p false, .p true, .p true, .v] =
      some (antipodalFirstStage m hm (k + 1) (by omega) (by omega)) := by
  let P := antipodalFirstStage m hm k hk (by omega)
  let R := rotateMany (2 * m) (by omega) (rotate (2 * m) (by omega) P false) true 2
  have hjlt (a : Fin (2 * m)) := antipodalExtractionIndex_lt m hm a
  have hsource : occupiedAt R false (site0 (2 * m) (by omega)) := by
    let a : Fin (2 * m) := ⟨2 * m - k, by omega⟩
    have hindex : antipodalExtractionIndex m a = k := by
      have ha : a.val ≠ 0 := by dsimp [a]; omega
      simp only [antipodalExtractionIndex, if_neg ha]
      dsimp [a]
      omega
    refine ⟨a, ?_⟩
    simp [packet, R, rotated_location, P, antipodalFirstStage, hindex,
      next, site0, Fin.ext_iff]
    omega
  have hreceiver : ¬ occupiedAt R true (site0 (2 * m) (by omega)) := by
    rintro ⟨a, ha⟩
    change R a = (true, site0 _ _) at ha
    dsimp [R] at ha
    rw [rotated_location] at ha
    by_cases hj : antipodalExtractionIndex m a < k
    · have hv := congrArg (fun loc => loc.2.val) ha
      have hsum : 2 * (k - 1 - antipodalExtractionIndex m a) + 2 < 2 * m := by omega
      simp [P, antipodalFirstStage, hj, nextMany_val, site0,
        Nat.mod_eq_of_lt hsum] at hv
    · have hl := congrArg Prod.fst ha
      simp [P, antipodalFirstStage, hj] at hl
  have he : liftPacket (2 * m) (by omega) R =
      antipodalFirstStage m hm (k + 1) (by omega) (by omega) := by
    funext a
    have hj := hjlt a
    by_cases hbefore : antipodalExtractionIndex m a < k
    · have hafter : antipodalExtractionIndex m a < k + 1 := by omega
      have hsum : 2 * (k - 1 - antipodalExtractionIndex m a) + 2 < 2 * m := by omega
      simp [liftPacket, R, rotated_location, P, antipodalFirstStage, hbefore,
        hafter, nextMany_val, Nat.mod_eq_of_lt hsum, Fin.ext_iff]
      omega
    · by_cases heq : antipodalExtractionIndex m a = k
      · have hnext : ¬ 2 * m + k - 1 - antipodalExtractionIndex m a + 1 < 2 * m := by omega
        simp [liftPacket, R, rotated_location, P, antipodalFirstStage, heq,
          next, site0, Fin.ext_iff]
        omega
      · have hafter : ¬ antipodalExtractionIndex m a < k + 1 := by omega
        have hnext : 2 * m + k - 1 - antipodalExtractionIndex m a + 1 < 2 * m := by omega
        have hnonzero : 2 * m + k - 1 - antipodalExtractionIndex m a + 1 ≠ 0 := by omega
        simp only [liftPacket, R, rotated_location, P, antipodalFirstStage, hbefore,
          hafter, ↓reduceDIte, Bool.false_eq_true, if_false, next, hnext,
          Prod.mk.injEq, true_and, Fin.mk.injEq, site0, hnonzero]
        omega
  have hs := (step_v_eq_some_iff (2 * m) (by omega) R _).mpr ⟨⟨hsource, hreceiver⟩, rfl⟩
  change (step (2 * m) (by omega) R .v).bind (fun P' => some P') = _
  rw [hs]
  exact congrArg some he

theorem antipodalFirstPrefix_run (m : Nat) (hm : 0 < m) (k : Nat)
    (hkm : k + 1 ≤ m) :
    run (2 * m) (by omega) (seed (2 * m)) (antipodalFirstPrefix k) =
      some (antipodalFirstStage m hm (k + 1) (by omega) hkm) := by
  induction k with
  | zero => exact antipodalFirstStage_initial m hm
  | succ k ih =>
      rw [antipodalFirstPrefix, run_append, ih (by omega), Option.bind_some]
      exact antipodalFirstStage_step m hm (k + 1) (by omega) (by omega)

private theorem rotated_upper_at (n : Nat) (hn : 0 < n) (P : Placement n)
    (a : Fin n) (turns : Nat) (q r : Fin n) (hPa : P a = (true, q))
    (hr : (q.val + turns) % n = r.val) :
    rotateMany n hn (rotate n hn P false) true turns a = (true, r) := by
  rw [rotated_location, hPa]
  simp only [↓reduceIte]
  congr 1
  exact Fin.ext (by simpa only [nextMany_val] using hr)

private theorem rotated_lower_at (n : Nat) (hn : 0 < n) (P : Placement n)
    (a : Fin n) (turns : Nat) (q r : Fin n) (hPa : P a = (false, q))
    (hr : (q.val + 1) % n = r.val) :
    rotateMany n hn (rotate n hn P false) true turns a = (false, r) := by
  rw [rotated_location, hPa]
  simp only [Bool.false_eq_true, ↓reduceIte]
  congr 1
  exact Fin.ext (by simpa only [next_val] using hr)

/-- The extra upper rotation exposes the first stored partner at port 1. -/
theorem antipodalSecondStage_initial (m : Nat) (hm : 0 < m) :
    run (2 * m) (by omega) (antipodalFirstStage m hm m hm (by omega))
      [.p false, .p true, .p true, .p true, .v, .d true] =
      some (antipodalSecondStage m hm 1 (by omega) (by omega)) := by
  let P := antipodalFirstStage m hm m hm (by omega)
  let R := rotateMany (2 * m) (by omega) (rotate (2 * m) (by omega) P false) true 3
  have hjlt (a : Fin (2 * m)) := antipodalExtractionIndex_lt m hm a
  have hR (a : Fin (2 * m)) :
      R a = if hj : antipodalExtractionIndex m a < m then
        if hz : antipodalExtractionIndex m a = 0 then (true, site1 (2 * m) (by omega))
        else (true, ⟨2 * m + 1 - 2 * antipodalExtractionIndex m a, by
          have := hjlt a
          omega⟩)
      else if heq : antipodalExtractionIndex m a = m then (false, site0 (2 * m) (by omega))
      else (false, ⟨2 * m + m - antipodalExtractionIndex m a, by
        have := hjlt a
        omega⟩) := by
    have hj := hjlt a
    by_cases hfirst : antipodalExtractionIndex m a < m
    · rw [dif_pos hfirst]
      by_cases hzero : antipodalExtractionIndex m a = 0
      · let q : Fin (2 * m) := ⟨2 * (m - 1 - antipodalExtractionIndex m a), by omega⟩
        rw [dif_pos hzero]
        apply rotated_upper_at (2 * m) (by omega) P a 3 q
          (site1 (2 * m) (by omega))
        · simp only [P, antipodalFirstStage, dif_pos hfirst]
          rfl
        · dsimp only [q, site1]
          have he : 2 * (m - 1 - antipodalExtractionIndex m a) + 3 = 2 * m + 1 := by omega
          rw [he, Nat.add_mod, Nat.mod_self, Nat.zero_add]
          simp only [Nat.mod_eq_of_lt (show 1 < 2 * m by omega)]
      · let q : Fin (2 * m) := ⟨2 * (m - 1 - antipodalExtractionIndex m a), by omega⟩
        let r : Fin (2 * m) := ⟨2 * m + 1 - 2 * antipodalExtractionIndex m a, by
          have := hjlt a
          omega⟩
        rw [dif_neg hzero]
        apply rotated_upper_at (2 * m) (by omega) P a 3 q r
        · simp only [P, antipodalFirstStage, dif_pos hfirst]
          rfl
        ·
          dsimp [q, r]
          rw [show 2 * (m - 1 - antipodalExtractionIndex m a) + 3 =
            2 * m + 1 - 2 * antipodalExtractionIndex m a by omega]
          rw [Nat.mod_eq_of_lt (by have := hjlt a; omega)]
    · rw [dif_neg hfirst]
      by_cases heq : antipodalExtractionIndex m a = m
      · let q : Fin (2 * m) := ⟨2 * m + m - 1 - antipodalExtractionIndex m a, by omega⟩
        rw [dif_pos heq]
        apply rotated_lower_at (2 * m) (by omega) P a 3 q
          (site0 (2 * m) (by omega))
        · simp only [P, antipodalFirstStage, dif_neg hfirst]
          rfl
        · dsimp only [q, site0]
          rw [show 2 * m + m - 1 - antipodalExtractionIndex m a + 1 = 2 * m by omega]
          simp only [Nat.mod_self]
      · let q : Fin (2 * m) := ⟨2 * m + m - 1 - antipodalExtractionIndex m a, by omega⟩
        let r : Fin (2 * m) := ⟨2 * m + m - antipodalExtractionIndex m a, by
          have := hjlt a
          omega⟩
        rw [dif_neg heq]
        apply rotated_lower_at (2 * m) (by omega) P a 3 q r
        · simp only [P, antipodalFirstStage, dif_neg hfirst]
          rfl
        · dsimp [q, r]
          rw [show 2 * m + m - 1 - antipodalExtractionIndex m a + 1 =
            2 * m + m - antipodalExtractionIndex m a by omega]
          rw [Nat.mod_eq_of_lt (by have := hjlt a; omega)]
  have hsource : occupiedAt R false (site0 (2 * m) (by omega)) := by
    let a : Fin (2 * m) := ⟨m, by omega⟩
    have hi : antipodalExtractionIndex m a = m := by
      simp only [antipodalExtractionIndex, a]
      split <;> omega
    exact ⟨a, by simp [packet, hR, hi]⟩
  have hreceiver : ¬ occupiedAt R true (site0 (2 * m) (by omega)) := by
    rintro ⟨a, ha⟩
    change R a = (true, site0 _ _) at ha
    rw [hR] at ha
    split at ha
    · split at ha
      · have hv := congrArg (fun loc => loc.2.val) ha
        simp [site0, site1] at hv
      · have hv := congrArg (fun loc => loc.2.val) ha
        simp only [site0] at hv
        omega
    · split at ha <;> exact Bool.noConfusion (congrArg Prod.fst ha)
  have he : collapse (2 * m) (by omega) (liftPacket (2 * m) (by omega) R) true =
      antipodalSecondStage m hm 1 (by omega) (by omega) := by
    funext a
    have hj := hjlt a
    by_cases hfirst : antipodalExtractionIndex m a < m
    · by_cases hzero : antipodalExtractionIndex m a = 0
      · simp [collapse, liftPacket, hR, antipodalSecondStage, hzero, hm,
          site0, site1, Fin.ext_iff]
      · have hpos : 1 ≤ antipodalExtractionIndex m a := by omega
        have hport : 2 * m + 1 - 2 * antipodalExtractionIndex m a ≠ 1 := by omega
        simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, hzero,
          site0, site1, Fin.ext_iff, hport]
    · by_cases heq : antipodalExtractionIndex m a = m
      · simp [collapse, liftPacket, hR, antipodalSecondStage, heq,
          site0, site1, Fin.ext_iff]
      · have hafter : ¬ antipodalExtractionIndex m a - m < 1 := by omega
        have hnonzero : 2 * m + m - antipodalExtractionIndex m a ≠ 0 := by omega
        simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, heq, hafter,
          site0, site1, Fin.ext_iff, hnonzero]
  have hs := (step_v_eq_some_iff (2 * m) (by omega) R _).mpr ⟨⟨hsource, hreceiver⟩, rfl⟩
  change (step (2 * m) (by omega) R .v).bind
    (fun P' => some (collapse (2 * m) (by omega) P' true)) = _
  rw [hs]
  exact congrArg some he

/-- Each later pass exposes one pending partner, transfers its mate, and
fuses exactly those atoms at the upper ordered ports. -/
theorem antipodalSecondStage_step (m : Nat) (hm : 0 < m) (k : Nat)
    (hk : 1 ≤ k) (hkm : k < m) :
    run (2 * m) (by omega) (antipodalSecondStage m hm k hk (by omega))
      [.p false, .p true, .p true, .v, .d true] =
      some (antipodalSecondStage m hm (k + 1) (by omega) (by omega)) := by
  let P := antipodalSecondStage m hm k hk (by omega)
  let R := rotateMany (2 * m) (by omega) (rotate (2 * m) (by omega) P false) true 2
  have hjlt (a : Fin (2 * m)) := antipodalExtractionIndex_lt m hm a
  have hR (a : Fin (2 * m)) :
      R a = if hj : antipodalExtractionIndex m a < m then
        if h : antipodalExtractionIndex m a < k then
          (true, ⟨2 * (k - antipodalExtractionIndex m a), by omega⟩)
        else if heq : antipodalExtractionIndex m a = k then
          (true, site1 (2 * m) (by omega))
        else (true, ⟨2 * m + 2 * k + 1 - 2 * antipodalExtractionIndex m a, by omega⟩)
      else if h : antipodalExtractionIndex m a - m < k then
        (true, ⟨2 * (k - (antipodalExtractionIndex m a - m)), by omega⟩)
      else if heq : antipodalExtractionIndex m a - m = k then
        (false, site0 (2 * m) (by omega))
      else (false, ⟨2 * m + m + k - antipodalExtractionIndex m a, by
        have := hjlt a
        omega⟩) := by
    have hj := hjlt a
    by_cases hfirst : antipodalExtractionIndex m a < m
    · rw [dif_pos hfirst]
      by_cases hbefore : antipodalExtractionIndex m a < k
      · rw [dif_pos hbefore]
        let q : Fin (2 * m) := ⟨2 * (k - 1 - antipodalExtractionIndex m a), by omega⟩
        let r : Fin (2 * m) := ⟨2 * (k - antipodalExtractionIndex m a), by omega⟩
        apply rotated_upper_at (2 * m) (by omega) P a 2 q r
        · simp only [P, antipodalSecondStage, dif_pos hfirst, dif_pos hbefore]
          rfl
        · dsimp [q, r]
          rw [Nat.mod_eq_of_lt (show 2 * (k - 1 - antipodalExtractionIndex m a) + 2 < 2 * m by omega)]
          omega
      · rw [dif_neg hbefore]
        by_cases heq : antipodalExtractionIndex m a = k
        · rw [dif_pos heq]
          let q : Fin (2 * m) := ⟨2 * m + 2 * k - 1 - 2 * antipodalExtractionIndex m a, by omega⟩
          apply rotated_upper_at (2 * m) (by omega) P a 2 q (site1 (2 * m) (by omega))
          · simp only [P, antipodalSecondStage, dif_pos hfirst, dif_neg hbefore]
            rfl
          · dsimp only [q, site1]
            rw [show 2 * m + 2 * k - 1 - 2 * antipodalExtractionIndex m a + 2 =
              2 * m + 1 by omega]
            simp [Nat.mod_eq_of_lt (show 1 < 2 * m by omega)]
        · rw [dif_neg heq]
          let q : Fin (2 * m) := ⟨2 * m + 2 * k - 1 - 2 * antipodalExtractionIndex m a, by omega⟩
          let r : Fin (2 * m) := ⟨2 * m + 2 * k + 1 - 2 * antipodalExtractionIndex m a, by omega⟩
          apply rotated_upper_at (2 * m) (by omega) P a 2 q r
          · simp only [P, antipodalSecondStage, dif_pos hfirst, dif_neg hbefore]
            rfl
          · dsimp [q, r]
            rw [Nat.mod_eq_of_lt (show
              2 * m + 2 * k - 1 - 2 * antipodalExtractionIndex m a + 2 < 2 * m by omega)]
            omega
    · rw [dif_neg hfirst]
      by_cases hbefore : antipodalExtractionIndex m a - m < k
      · rw [dif_pos hbefore]
        let q : Fin (2 * m) := ⟨2 * (k - 1 - (antipodalExtractionIndex m a - m)), by omega⟩
        let r : Fin (2 * m) := ⟨2 * (k - (antipodalExtractionIndex m a - m)), by omega⟩
        apply rotated_upper_at (2 * m) (by omega) P a 2 q r
        · simp only [P, antipodalSecondStage, dif_neg hfirst, dif_pos hbefore]
          rfl
        · dsimp [q, r]
          rw [Nat.mod_eq_of_lt (show 2 * (k - 1 - (antipodalExtractionIndex m a - m)) + 2 < 2 * m by omega)]
          omega
      · rw [dif_neg hbefore]
        by_cases heq : antipodalExtractionIndex m a - m = k
        · rw [dif_pos heq]
          let q : Fin (2 * m) := ⟨2 * m + m + k - 1 - antipodalExtractionIndex m a, by omega⟩
          apply rotated_lower_at (2 * m) (by omega) P a 2 q (site0 (2 * m) (by omega))
          · simp only [P, antipodalSecondStage, dif_neg hfirst, dif_neg hbefore]
            rfl
          · dsimp only [q, site0]
            rw [show 2 * m + m + k - 1 - antipodalExtractionIndex m a + 1 =
              2 * m by omega]
            exact Nat.mod_self _
        · rw [dif_neg heq]
          let q : Fin (2 * m) := ⟨2 * m + m + k - 1 - antipodalExtractionIndex m a, by omega⟩
          let r : Fin (2 * m) := ⟨2 * m + m + k - antipodalExtractionIndex m a, by omega⟩
          apply rotated_lower_at (2 * m) (by omega) P a 2 q r
          · simp only [P, antipodalSecondStage, dif_neg hfirst, dif_neg hbefore]
            rfl
          · dsimp [q, r]
            rw [Nat.mod_eq_of_lt (show
              2 * m + m + k - 1 - antipodalExtractionIndex m a + 1 < 2 * m by omega)]
            omega
  have hsource : occupiedAt R false (site0 (2 * m) (by omega)) := by
    let a : Fin (2 * m) := ⟨m - k, by omega⟩
    have hi : antipodalExtractionIndex m a = m + k := by
      have ha : a.val ≠ 0 := by dsimp [a]; omega
      simp only [antipodalExtractionIndex, if_neg ha, a]
      omega
    refine ⟨a, ?_⟩
    simp [packet, hR, hi, Nat.add_sub_cancel_left, show ¬ m + k < m by omega]
  have hreceiver : ¬ occupiedAt R true (site0 (2 * m) (by omega)) := by
    rintro ⟨a, ha⟩
    change R a = (true, site0 _ _) at ha
    rw [hR] at ha
    split at ha
    · split at ha
      · have hv := congrArg (fun loc => loc.2.val) ha
        simp only [site0] at hv
        omega
      · split at ha
        · have hv := congrArg (fun loc => loc.2.val) ha
          simp [site0, site1] at hv
        · have hv := congrArg (fun loc => loc.2.val) ha
          simp only [site0] at hv
          omega
    · split at ha
      · have hv := congrArg (fun loc => loc.2.val) ha
        simp only [site0] at hv
        omega
      · split at ha <;> exact Bool.noConfusion (congrArg Prod.fst ha)
  have he : collapse (2 * m) (by omega) (liftPacket (2 * m) (by omega) R) true =
      antipodalSecondStage m hm (k + 1) (by omega) (by omega) := by
    funext a
    have hj := hjlt a
    by_cases hfirst : antipodalExtractionIndex m a < m
    · by_cases hbefore : antipodalExtractionIndex m a < k
      · have hafter : antipodalExtractionIndex m a < k + 1 := by omega
        have hport : 2 * (k - antipodalExtractionIndex m a) ≠ 1 := by omega
        simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, hbefore,
          hafter, site0, site1, Fin.ext_iff, hport]
      · by_cases heq : antipodalExtractionIndex m a = k
        · simp [collapse, liftPacket, hR, antipodalSecondStage, heq, hkm,
            site0, site1, Fin.ext_iff]
        · have hafter : ¬ antipodalExtractionIndex m a < k + 1 := by omega
          have hport : 2 * m + 2 * k + 1 - 2 * antipodalExtractionIndex m a ≠ 1 := by omega
          simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, hbefore,
            heq, hafter, site0, site1, Fin.ext_iff, hport]
          omega
    · by_cases hbefore : antipodalExtractionIndex m a - m < k
      · have hafter : antipodalExtractionIndex m a - m < k + 1 := by omega
        have hport : 2 * (k - (antipodalExtractionIndex m a - m)) ≠ 1 := by omega
        simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, hbefore,
          hafter, site0, site1, Fin.ext_iff, hport]
      · by_cases heq : antipodalExtractionIndex m a - m = k
        · have hafter : antipodalExtractionIndex m a - m < k + 1 := by omega
          simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst,
            heq, site0, site1, Fin.ext_iff]
        · have hafter : ¬ antipodalExtractionIndex m a - m < k + 1 := by omega
          have hnonzero : 2 * m + m + k - antipodalExtractionIndex m a ≠ 0 := by omega
          simp [collapse, liftPacket, hR, antipodalSecondStage, hfirst, hbefore,
            heq, hafter, site0, site1, Fin.ext_iff, hnonzero]
  have hs := (step_v_eq_some_iff (2 * m) (by omega) R _).mpr ⟨⟨hsource, hreceiver⟩, rfl⟩
  change (step (2 * m) (by omega) R .v).bind
    (fun P' => some (collapse (2 * m) (by omega) P' true)) = _
  rw [hs]
  exact congrArg some he

theorem antipodalSecondSuffix_run (m : Nat) (hm : 0 < m) (k : Nat)
    (hkm : k + 1 ≤ m) :
    run (2 * m) (by omega) (antipodalSecondStage m hm 1 (by omega) (by omega))
      (antipodalSecondSuffix k) =
      some (antipodalSecondStage m hm (k + 1) (by omega) hkm) := by
  induction k with
  | zero => rfl
  | succ k ih =>
      rw [antipodalSecondSuffix, run_append, ih (by omega), Option.bind_some]
      exact antipodalSecondStage_step m hm (k + 1) (by omega) (by omega)

/-- Pair `i` occupies the even site `2*((i-1) mod m)`. -/
def antipodalSpacedSite (m : Nat) (hm : 0 < m) (i : Fin m) : Fin (2 * m) :=
  if i.val = 0 then ⟨2 * (m - 1), by omega⟩ else ⟨2 * (i.val - 1), by omega⟩

def antipodalSpacedEndpoint (m : Nat) (hm : 0 < m) : Placement (2 * m) := fun a =>
  (true, antipodalSpacedSite m hm ⟨antipodalLabel m a, Nat.mod_lt _ hm⟩)

theorem antipodalSpacedSite_injective (m : Nat) (hm : 0 < m) :
    Function.Injective (antipodalSpacedSite m hm) := by
  intro i j h
  have hi := i.isLt
  have hj := j.isLt
  apply Fin.ext
  have hv := congrArg Fin.val h
  unfold antipodalSpacedSite at hv
  split at hv <;> split at hv <;> simp only at hv <;> omega

theorem antipodalSpacedEndpoint_partition (m : Nat) (hm : 0 < m) :
    AntipodalEndpoint m (antipodalSpacedEndpoint m hm) := by
  intro a b
  constructor
  · intro h
    have hs := congrArg Prod.snd h
    have hi := antipodalSpacedSite_injective m hm hs
    exact congrArg Fin.val hi
  · intro h
    unfold samePacket antipodalSpacedEndpoint
    congr 2
    exact Fin.ext h

theorem antipodalSecondStage_terminal (m : Nat) (hm : 0 < m) :
    antipodalSecondStage m hm m hm (by omega) = antipodalSpacedEndpoint m hm := by
  funext a
  obtain ⟨i, ha⟩ := antipodal_atom_cases m a
  have hi := i.isLt
  rcases ha with rfl | rfl
  · by_cases hzero : i.val = 0
    · simp [antipodalSecondStage, antipodalExtractionIndex, antipodalLeft,
        antipodalSpacedEndpoint, antipodalLabel, antipodalSpacedSite, hzero, hm]
    · have hindex : antipodalExtractionIndex m (antipodalLeft m i) = 2 * m - i.val := by
        simp [antipodalExtractionIndex, antipodalLeft, hzero]
      have hfirst : ¬ 2 * m - i.val < m := by omega
      have hbefore : 2 * m - i.val - m < m := by omega
      simp [antipodalSecondStage, hindex, hfirst, hbefore, antipodalSpacedEndpoint,
        antipodalLabel_left, antipodalSpacedSite, hzero, Fin.ext_iff]
      omega
  · have hindex : antipodalExtractionIndex m (antipodalRight m i) = m - i.val := by
      change (if i.val + m = 0 then 0 else 2 * m - (i.val + m)) = m - i.val
      rw [if_neg (show i.val + m ≠ 0 by omega)]
      omega
    by_cases hzero : i.val = 0
    · simp [antipodalSecondStage, hindex, antipodalSpacedEndpoint,
        antipodalLabel_right, antipodalSpacedSite, hzero, hm]
    · have hfirst : m - i.val < m := by omega
      simp [antipodalSecondStage, hindex, hfirst, antipodalSpacedEndpoint,
        antipodalLabel_right, antipodalSpacedSite, hzero, Fin.ext_iff]
      omega

/-- A single actual guarded history realizes the complete spaced endpoint. -/
theorem antipodal_linear_word_realizes (m : Nat) (hm : 0 < m) :
    run (2 * m) (by omega) (seed (2 * m)) (antipodalLinearWord m) =
      some (antipodalSpacedEndpoint m hm) := by
  cases m with
  | zero => omega
  | succ k =>
      unfold antipodalLinearWord
      simp only [Nat.add_sub_cancel]
      rw [run_append, run_append,
        antipodalFirstPrefix_run (k + 1) hm k (by omega), Option.bind_some,
        antipodalSecondStage_initial, Option.bind_some,
        antipodalSecondSuffix_run (k + 1) hm k (by omega),
        antipodalSecondStage_terminal]

theorem antipodalFirstPrefix_length (k : Nat) :
    (antipodalFirstPrefix k).length = 4 * k + 1 := by
  induction k with
  | zero => rfl
  | succ k ih => simp only [antipodalFirstPrefix, List.length_append, List.length_cons,
      List.length_nil, ih]; omega

theorem antipodalSecondSuffix_length (k : Nat) :
    (antipodalSecondSuffix k).length = 5 * k := by
  induction k with
  | zero => rfl
  | succ k ih => simp only [antipodalSecondSuffix, List.length_append, List.length_cons,
      List.length_nil, ih]; omega

theorem antipodal_linear_word_length (m : Nat) (hm : 0 < m) :
    (antipodalLinearWord m).length = 9 * m - 2 := by
  simp only [antipodalLinearWord, List.length_append, antipodalFirstPrefix_length,
    antipodalSecondSuffix_length, List.length_cons, List.length_nil]
  omega

theorem antipodalFirstPrefix_counts (k : Nat) :
    lowerRotationCount (antipodalFirstPrefix k) = k ∧
      lowerDefectCount (antipodalFirstPrefix k) = 0 ∧
      verticalCount (antipodalFirstPrefix k) = k + 1 ∧
      rawUpperRotationCount (antipodalFirstPrefix k) = 2 * k ∧
      rawUpperDefectCount (antipodalFirstPrefix k) = 0 := by
  induction k with
  | zero => simp [antipodalFirstPrefix, lowerRotationCount, lowerDefectCount,
      verticalCount, rawUpperRotationCount, rawUpperDefectCount]
  | succ k ih =>
      simp only [antipodalFirstPrefix, lowerRotationCount, lowerDefectCount,
        verticalCount, rawUpperRotationCount, rawUpperDefectCount, List.count_append] at *
      simp at *
      omega

theorem antipodalSecondSuffix_counts (k : Nat) :
    lowerRotationCount (antipodalSecondSuffix k) = k ∧
      lowerDefectCount (antipodalSecondSuffix k) = 0 ∧
      verticalCount (antipodalSecondSuffix k) = k ∧
      rawUpperRotationCount (antipodalSecondSuffix k) = 2 * k ∧
      rawUpperDefectCount (antipodalSecondSuffix k) = k := by
  induction k with
  | zero => simp [antipodalSecondSuffix, lowerRotationCount, lowerDefectCount,
      verticalCount, rawUpperRotationCount, rawUpperDefectCount]
  | succ k ih =>
      simp only [antipodalSecondSuffix, lowerRotationCount, lowerDefectCount,
        verticalCount, rawUpperRotationCount, rawUpperDefectCount, List.count_append] at *
      simp at *
      omega

theorem antipodal_linear_word_counts (m : Nat) (hm : 0 < m) :
    lowerRotationCount (antipodalLinearWord m) = 2 * m - 1 ∧
      lowerDefectCount (antipodalLinearWord m) = 0 ∧
      verticalCount (antipodalLinearWord m) = 2 * m ∧
      rawUpperRotationCount (antipodalLinearWord m) = 4 * m - 1 ∧
      rawUpperDefectCount (antipodalLinearWord m) = m ∧
      lowerPortCost (antipodalLinearWord m) = 4 * m - 1 := by
  have hfirst := antipodalFirstPrefix_counts (m - 1)
  have hsecond := antipodalSecondSuffix_counts (m - 1)
  simp only [antipodalLinearWord, lowerRotationCount, lowerDefectCount, verticalCount,
    rawUpperRotationCount, rawUpperDefectCount, lowerPortCost, List.count_append] at *
  simp at *
  omega

end RSR2.Parametric
