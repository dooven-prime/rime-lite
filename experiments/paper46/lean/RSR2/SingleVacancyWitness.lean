import RSR2.SingleVacancyDebt

/-!
# An attaining execution for repeated vacancy debt

The word is `p0^(n-1) v (d0 p0^(n-1))^(n-2)`.  Every cycle after the
transfer starts and ends with the sole lower vacancy at 0.  It moves the
remaining named packets one step backwards around sites `1,...,n-1`.
-/

namespace RSR2.Parametric

private def vacancySlotIndex (n : Nat) (a : Fin n) : Nat :=
  if a.val = 0 then n - 2 else a.val - 2

private theorem vacancySlotIndex_lt (n : Nat) (hn : 3 ≤ n) (a : Fin n) :
    vacancySlotIndex n a < n - 1 := by
  unfold vacancySlotIndex
  split <;> omega

private def vacancyStageSite (n : Nat) (hn : 3 ≤ n) (k : Nat) (a : Fin n) : Fin n :=
  ⟨(vacancySlotIndex n a + (n - 1) - k) % (n - 1) + 1, by
    have hm := Nat.mod_lt (vacancySlotIndex n a + (n - 1) - k)
      (show 0 < n - 1 by omega)
    omega⟩

private def vacancyStage (n : Nat) (hn : 3 ≤ n) (k : Nat) : Placement n := fun a =>
  if a = site1 n (by omega) then (true, site0 n (by omega))
  else (false, vacancyStageSite n hn k a)

private theorem vacancyStageSite_succ (n : Nat) (hn : 3 ≤ n) (k : Nat)
    (hk : k < n - 2) (a : Fin n) :
    (vacancyStageSite n hn (k + 1) a).val =
      if (vacancyStageSite n hn k a).val = 1 then n - 1
      else (vacancyStageSite n hn k a).val - 1 := by
  let x := (vacancySlotIndex n a + (n - 1) - k) % (n - 1)
  let y := (vacancySlotIndex n a + (n - 1) - (k + 1)) % (n - 1)
  have hx : x < n - 1 := Nat.mod_lt _ (by omega)
  have hy : y < n - 1 := Nat.mod_lt _ (by omega)
  have hnum : vacancySlotIndex n a + (n - 1) - (k + 1) + 1 =
      vacancySlotIndex n a + (n - 1) - k := by omega
  have hrel : (y + 1) % (n - 1) = x := by
    dsimp [x, y]
    rw [Nat.mod_add_mod, hnum]
  change y + 1 = if x + 1 = 1 then n - 1 else x + 1 - 1
  by_cases hw : y + 1 < n - 1
  · rw [Nat.mod_eq_of_lt hw] at hrel
    rw [if_neg (by omega)]
    omega
  · have he : y + 1 = n - 1 := by omega
    rw [he, Nat.mod_self] at hrel
    rw [if_pos (by omega)]
    omega

def singleVacancyCycleWord (n : Nat) : List Letter :=
  .d false :: List.replicate (n - 1) (.p false)

def singleVacancyWord (n : Nat) : List Letter :=
  List.replicate (n - 1) (.p false) ++ [.v] ++
    (List.replicate (n - 2) (singleVacancyCycleWord n)).flatten

private theorem vacancyCycle_atom (n : Nat) (hn : 3 ≤ n)
    (P : Placement n) (a : Fin n) (q : Fin n)
    (hp : P a = (false, q)) (hq : 0 < q.val) :
    (rotateMany n (by omega) (collapse n (by omega) P false) false (n - 1) a).1 = false ∧
    (rotateMany n (by omega) (collapse n (by omega) P false) false (n - 1) a).2.val =
      if q.val = 1 then n - 1 else q.val - 1 := by
  by_cases hq1 : q.val = 1
  · have he : q = site1 n (by omega) := Fin.ext hq1
    simp [collapse, hp, he, rotateMany_apply, nextMany_val, site0,
      Nat.mod_eq_of_lt (show n - 1 < n by omega), site1]
  · have he : q ≠ site1 n (by omega) := fun h => hq1 (congrArg Fin.val h)
    have hsum : q.val + (n - 1) = n + (q.val - 1) := by omega
    simp [collapse, hp, he, rotateMany_apply, nextMany_val, hsum,
      Nat.add_mod_left, Nat.mod_eq_of_lt (show q.val - 1 < n by omega), hq1]

private theorem vacancyStage_cycle (n : Nat) (hn : 3 ≤ n) (k : Nat)
    (hk : k < n - 2) :
    run n (by omega) (vacancyStage n hn k) (singleVacancyCycleWord n) =
      some (vacancyStage n hn (k + 1)) := by
  have he : rotateMany n (by omega)
      (collapse n (by omega) (vacancyStage n hn k) false) false (n - 1) =
      vacancyStage n hn (k + 1) := by
    funext a
    by_cases ha : a = site1 n (by omega)
    · simp [vacancyStage, ha, collapse, rotateMany_apply]
    · have hp : vacancyStage n hn k a =
          (false, vacancyStageSite n hn k a) := by simp [vacancyStage, ha]
      have hpos : 0 < (vacancyStageSite n hn k a).val := by
        change 0 < (vacancySlotIndex n a + (n - 1) - k) % (n - 1) + 1
        exact Nat.zero_lt_succ _
      have hpoint := vacancyCycle_atom n hn (vacancyStage n hn k) a _ hp hpos
      apply Prod.ext
      · simpa [vacancyStage, ha] using hpoint.1
      · apply Fin.ext
        rw [show (vacancyStage n hn (k + 1) a).2 =
          vacancyStageSite n hn (k + 1) a by simp [vacancyStage, ha]]
        rw [hpoint.2, vacancyStageSite_succ n hn k hk a]
  simp only [singleVacancyCycleWord, run, step_d, Option.bind_some]
  rw [run_powers, he]

private theorem vacancyStage_prefix (n : Nat) (hn : 3 ≤ n) :
    run n (by omega) (seed n) (List.replicate (n - 1) (.p false) ++ [.v]) =
      some (vacancyStage n hn 0) := by
  let P := rotateMany n (by omega) (seed n) false (n - 1)
  have hp : ∀ a, (P a).1 = false := by intro a; simp [P, rotateMany_apply, seed]
  have ha1 : P (site1 n (by omega)) = (false, site0 n (by omega)) := by
    apply Prod.ext
    · exact hp _
    · apply Fin.ext
      simp [P, rotateMany_apply, seed, nextMany_val, site0, site1,
        show 1 + (n - 1) = n by omega]
  have hg : liftGuard n (by omega) P := by
    refine ⟨⟨site1 n (by omega), ha1⟩, ?_⟩
    rintro ⟨a, ha⟩
    have hl := congrArg Prod.fst ha
    simp [hp] at hl
  have he : liftPacket n (by omega) P = vacancyStage n hn 0 := by
    funext a
    by_cases ha : a = site1 n (by omega)
    · simp [ha, liftPacket, ha1, vacancyStage]
    · have hzero : a.val ≠ 1 := by intro hv; exact ha (Fin.ext hv)
      have hval : (P a).2.val = if a.val = 0 then n - 1 else a.val - 1 := by
        simp only [P, rotateMany_apply, seed, if_true, nextMany_val]
        by_cases hz : a.val = 0
        · simp [hz, Nat.mod_eq_of_lt (show n - 1 < n by omega)]
        · have hsum : a.val + (n - 1) = n + (a.val - 1) := by omega
          simp [hz, hsum, Nat.add_mod_left,
            Nat.mod_eq_of_lt (show a.val - 1 < n by omega)]
      have hne : P a ≠ (false, site0 n (by omega)) := by
        intro hh
        have hv := congrArg (fun l => l.2.val) hh
        change (P a).2.val = 0 at hv
        rw [hval] at hv
        split at hv <;> omega
      rw [show liftPacket n (by omega) P a = P a by simp [liftPacket, hne]]
      apply Prod.ext
      · simpa [vacancyStage, ha] using hp a
      · apply Fin.ext
        simp only [vacancyStage, if_neg ha, vacancyStageSite, Nat.sub_zero,
          Nat.add_mod_right, Nat.mod_eq_of_lt (vacancySlotIndex_lt n hn a)]
        rw [hval]
        unfold vacancySlotIndex
        split <;> omega
  rw [run_append, run_powers]
  change run n (by omega) P [.v] = _
  simp [run, step, hg, he]

private theorem vacancyStage_cycles (n : Nat) (hn : 3 ≤ n) :
    ∀ k, k ≤ n - 2 →
      run n (by omega) (vacancyStage n hn 0)
        (List.replicate k (singleVacancyCycleWord n)).flatten =
          some (vacancyStage n hn k)
  | 0, _ => rfl
  | k + 1, hk => by
      have hp := vacancyStage_cycles n hn k (by omega)
      rw [List.replicate_succ', List.flatten_append, List.flatten_cons,
        List.flatten_nil, List.append_nil, run_append, hp]
      exact vacancyStage_cycle n hn k (by omega)

private theorem vacancyStage_final (n : Nat) (hn : 3 ≤ n) :
    vacancyStage n hn (n - 2) = singleVacancyEndpoint n (by omega) := by
  funext a
  by_cases ha1 : a = site1 n (by omega)
  · simp [vacancyStage, singleVacancyEndpoint, ha1]
  · simp only [vacancyStage, singleVacancyEndpoint, if_neg ha1]
    by_cases ha0 : a = site0 n (by omega)
    · rw [if_pos ha0]
      congr 1
      apply Fin.ext
      have hz : a.val = 0 := congrArg Fin.val ha0
      have he : (n - 2) + (n - 1) - (n - 2) = n - 1 := by omega
      simp [vacancyStageSite, vacancySlotIndex, hz, he, site1]
    · rw [if_neg ha0]
      congr 1
      apply Fin.ext
      have hz : a.val ≠ 0 := fun h => ha0 (Fin.ext h)
      have ho : a.val ≠ 1 := fun h => ha1 (Fin.ext h)
      have he : a.val - 2 + (n - 1) - (n - 2) = a.val - 1 := by omega
      simp [vacancyStageSite, vacancySlotIndex, hz, he,
        Nat.mod_eq_of_lt (show a.val - 1 < n - 1 by omega)]
      omega

theorem singleVacancyWord_run (n : Nat) (hn : 3 ≤ n) :
    run n (by omega) (seed n) (singleVacancyWord n) =
      some (singleVacancyEndpoint n (by omega)) := by
  unfold singleVacancyWord
  rw [run_append, vacancyStage_prefix n hn]
  simpa [vacancyStage_final n hn] using vacancyStage_cycles n hn (n - 2) (by omega)

theorem singleVacancyWord_rotationCount (n : Nat) :
    lowerRotationCount (singleVacancyWord n) = (n - 1) * (n - 1) := by
  have hc : ∀ k, lowerRotationCount
      (List.replicate k (singleVacancyCycleWord n)).flatten = k * (n - 1) := by
    intro k
    induction k with
    | zero => simp [lowerRotationCount]
    | succ k ih =>
        rw [List.replicate_succ, List.flatten_cons]
        simp only [lowerRotationCount, List.count_append]
        rw [show (List.replicate k (singleVacancyCycleWord n)).flatten.count
          (.p false) = k * (n - 1) from ih]
        simp [singleVacancyCycleWord, Nat.add_mul, Nat.add_comm]
  simp only [singleVacancyWord, lowerRotationCount, List.count_append]
  have he := hc (n - 2)
  simp only [lowerRotationCount] at he
  rw [he]
  simp
  by_cases hn : 2 ≤ n
  · have hf : n - 2 + 1 = n - 1 := by omega
    calc
      _ = (n - 2 + 1) * (n - 1) := by rw [Nat.add_mul, Nat.one_mul, Nat.add_comm]
      _ = _ := by rw [hf]
  · have he : n - 1 = 0 := by omega
    simp [he]

/-- Universal lower bound and one actual attaining word, with no restriction
on the histories quantified in the lower-bound branch. -/
theorem singleVacancyEndpoint_rotation_optimal (n : Nat) (hn : 3 ≤ n) :
    (∀ word, run n (by omega) (seed n) word =
        some (singleVacancyEndpoint n (by omega)) →
          (n - 1) * (n - 1) ≤ lowerRotationCount word) ∧
    run n (by omega) (seed n) (singleVacancyWord n) =
      some (singleVacancyEndpoint n (by omega)) ∧
    lowerRotationCount (singleVacancyWord n) = (n - 1) * (n - 1) :=
  ⟨fun word h => singleVacancyEndpoint_rotation_lower_bound n hn word h,
    singleVacancyWord_run n hn, singleVacancyWord_rotationCount n⟩

end RSR2.Parametric
