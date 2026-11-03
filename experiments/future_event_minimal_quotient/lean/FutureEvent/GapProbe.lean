import FutureEvent.Atomwise

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def dpWord : ℕ → List Letter
  | 0 => []
  | k + 1 => [.d, .p] ++ dpWord k

@[simp] theorem dpWord_length (k : ℕ) : (dpWord k).length = 2 * k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [dpWord, ih]; omega

omit [NeZero n] in
theorem siteWord_pWord (k : ℕ) (q : ZMod n) :
    siteWord (pWord k) q = q + k := by
  induction k with
  | zero => simp [pWord]
  | succ k ih =>
      rw [pWord, siteWord_append, ih]
      simp [siteWord, siteLetter, Nat.cast_succ, add_assoc]

omit [NeZero n] in
/-- Natural coordinates measured backwards from site one do not wrap. -/
theorem one_minus_natCast_injective {u v : ℕ} (hu : u < n) (hv : v < n)
    (h : (1 - (u : ZMod n)) = 1 - (v : ZMod n)) : u = v := by
  have hc : (u : ZMod n) = (v : ZMod n) := by
    calc
      (u : ZMod n) = 1 - (1 - u) := by ring
      _ = 1 - (1 - v) := congrArg (fun z : ZMod n => 1 - z) h
      _ = v := by ring
  have hval := congrArg ZMod.val hc
  simpa [ZMod.val_natCast_of_lt hu, ZMod.val_natCast_of_lt hv] using hval

omit [NeZero n] in
theorem dp_step_one_minus (d : ℕ) (hd : d < n) :
    siteWord [.d, .p] (1 - (d : ZMod n)) = 1 - ((d - 1 : ℕ) : ZMod n) := by
  by_cases hzero : d = 0
  · subst d
    simp [siteWord, siteLetter, collapsePosition]
  · have hne : (1 - (d : ZMod n)) ≠ 1 := by
      intro h
      have hcast : 1 - (d : ZMod n) = 1 - (0 : ℕ) := by simpa using h
      exact hzero (one_minus_natCast_injective hd (by omega) hcast)
    simp only [siteWord, siteLetter, collapsePosition, hne, ite_false]
    rw [Nat.cast_sub (by omega : 1 ≤ d), Nat.cast_one]
    ring

omit [NeZero n] in
/-- Exact site map of every number of chronological `dp` blocks. -/
theorem dpWord_one_minus (k d : ℕ) (hd : d < n) :
    siteWord (dpWord k) (1 - (d : ZMod n)) = 1 - ((d - k : ℕ) : ZMod n) := by
  induction k generalizing d with
  | zero => simp [dpWord]
  | succ k ih =>
      rw [dpWord, siteWord_append, dp_step_one_minus d hd, ih (d - 1) (by omega)]
      congr 2
      omega

theorem dpWord_site (k : ℕ) (q : ZMod n) :
    siteWord (dpWord k) q = 1 - (((1 - q).val - k : ℕ) : ZMod n) := by
  have hq : q = 1 - ((1 - q).val : ZMod n) := by
    rw [ZMod.natCast_zmod_val]
    ring
  conv_lhs => rw [hq]
  exact dpWord_one_minus k (1 - q).val (ZMod.val_lt (1 - q))

def gapPreFinal (b : ZMod n) (g : ℕ) : List Letter :=
  pWord (1 - b).val ++ dpWord (g - 1)

def gapProbe (b : ZMod n) (g : ℕ) : List Letter :=
  gapPreFinal b g ++ [.d]

/-- The prefix before the last defect, in the same raw alphabet as `run`. -/
theorem gapPreFinal_site (b q : ZMod n) (g : ℕ) :
    siteWord (gapPreFinal b g) q =
      1 - (((b - q).val - (g - 1) : ℕ) : ZMod n) := by
  rw [gapPreFinal, siteWord_append, siteWord_pWord, ZMod.natCast_zmod_val,
    dpWord_site]
  congr 3
  have h : 1 - (q + (1 - b)) = b - q := by ring
  rw [h]

/-- The port-one fiber is exactly the closed backwards interval of length `g`. -/
theorem gapPreFinal_one_iff (b q : ZMod n) (g : ℕ) (hg : 1 ≤ g) :
    siteWord (gapPreFinal b g) q = 1 ↔ (b - q).val < g := by
  rw [gapPreFinal_site]
  have hd : (b - q).val - (g - 1) < n :=
    lt_of_le_of_lt (Nat.sub_le _ _) (ZMod.val_lt _)
  constructor
  · intro h
    have he : 1 - (((b - q).val - (g - 1) : ℕ) : ZMod n) =
        1 - ((0 : ℕ) : ZMod n) := by simpa using h
    have := one_minus_natCast_injective hd (by omega) he
    omega
  · intro h
    have hz : (b - q).val - (g - 1) = 0 := by omega
    simp [hz]

/-- The port-zero fiber is a singleton, including seam-wrapping source gaps. -/
theorem gapPreFinal_zero_iff (b q : ZMod n) (g : ℕ)
    (hg : 1 ≤ g) (hgn : g < n) :
    siteWord (gapPreFinal b g) q = 0 ↔ q = b - (g : ZMod n) := by
  have hn : 1 < n := by omega
  rw [gapPreFinal_site]
  have hd : (b - q).val - (g - 1) < n :=
    lt_of_le_of_lt (Nat.sub_le _ _) (ZMod.val_lt _)
  constructor
  · intro h
    have he : 1 - (((b - q).val - (g - 1) : ℕ) : ZMod n) =
        1 - ((1 : ℕ) : ZMod n) := by simpa using h
    have hval := one_minus_natCast_injective hd hn he
    have hdist : (b - q).val = g := by omega
    have hcast := congrArg (fun k : ℕ => (k : ZMod n)) hdist
    rw [ZMod.natCast_zmod_val] at hcast
    calc
      q = b - (b - q) := by ring
      _ = b - (g : ZMod n) := congrArg (fun z : ZMod n => b - z) hcast
  · intro h
    subst q
    have hdist : (b - (b - (g : ZMod n))).val = g := by
      rw [sub_sub_cancel, ZMod.val_natCast_of_lt hgn]
    rw [hdist]
    have hsub : g - (g - 1) = 1 := by omega
    simp [hsub]

/-- All prefix fibers except port one's are singletons. -/
theorem gapPreFinal_injective_off_one (b q q' : ZMod n) (g : ℕ)
    (h : siteWord (gapPreFinal b g) q = siteWord (gapPreFinal b g) q')
    (hne : siteWord (gapPreFinal b g) q ≠ 1) : q = q' := by
  rw [gapPreFinal_site, gapPreFinal_site] at h
  have hdist := one_minus_natCast_injective
    (lt_of_le_of_lt (Nat.sub_le _ _) (ZMod.val_lt (b - q)))
    (lt_of_le_of_lt (Nat.sub_le _ _) (ZMod.val_lt (b - q'))) h
  have hpos : 0 < (b - q).val - (g - 1) := by
    by_contra hp
    have hz : (b - q).val - (g - 1) = 0 := by omega
    exact hne (by rw [gapPreFinal_site, hz]; simp)
  have heq : (b - q).val = (b - q').val := by omega
  have hcast := congrArg (fun k : ℕ => (k : ZMod n)) heq
  rw [ZMod.natCast_zmod_val, ZMod.natCast_zmod_val] at hcast
  calc
    q = b - (b - q) := by ring
    _ = b - (b - q') := congrArg (fun z : ZMod n => b - z) hcast
    _ = q' := by ring

/-- The port-one interval contains at most one initially occupied site. -/
theorem gapPreFinal_injective_on_initial_sites
    (b : ZMod n) (g : ℕ) (hg : 1 ≤ g) (f : ZMod n → ZMod n)
    (hsupport : ∀ atom, (b - f atom).val < g → f atom = b) :
    ∀ x y, siteWord (gapPreFinal b g) (f x) =
      siteWord (gapPreFinal b g) (f y) → f x = f y := by
  intro x y h
  by_cases hx : siteWord (gapPreFinal b g) (f x) = 1
  · have hy := h.symm.trans hx
    exact (hsupport x ((gapPreFinal_one_iff b (f x) g hg).mp hx)).trans
      (hsupport y ((gapPreFinal_one_iff b (f y) g hg).mp hy)).symm
  · exact gapPreFinal_injective_off_one b (f x) (f y) g h hx

theorem gapPreFinal_fusionFree (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (b : ZMod n) (g : ℕ) (hn : 2 ≤ n) (hg : 1 ≤ g)
    (hplaced : s.placed = placementOfMap f)
    (hsupport : ∀ atom, (b - f atom).val < g → f atom = b) :
    FusionFree F s (gapPreFinal b g) :=
  fusionFree_of_final_site_injective F s f _ hn hplaced
    (gapPreFinal_injective_on_initial_sites b g hg f hsupport)

end FutureEvent
