import FutureEvent.ProbeCoalescence

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def pdWord : ℕ → List Letter
  | 0 => []
  | k + 1 => [.p, .d] ++ pdWord k

def sweepCore (k : ℕ) : List Letter := [.d] ++ pdWord k

def registeredSweep (q : ZMod n) : List Letter :=
  pWord (-q).val ++ sweepCore (n - 2)

omit [NeZero n] in
theorem pdWord_length (k : ℕ) : (pdWord k).length = 2 * k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pdWord, ih]; omega

omit [NeZero n] in
theorem pdWord_snoc (k : ℕ) : pdWord (k + 1) = pdWord k ++ [.p, .d] := by
  induction k with
  | zero => rfl
  | succ k ih =>
      change [.p, .d] ++ pdWord (k + 1) =
        ([.p, .d] ++ pdWord k) ++ [.p, .d]
      rw [ih, List.append_assoc]

omit [NeZero n] in
theorem pdWord_add (k l : ℕ) : pdWord (k + l) = pdWord k ++ pdWord l := by
  induction k with
  | zero => simp [pdWord]
  | succ k ih =>
      rw [Nat.succ_add, pdWord, ih, pdWord, List.append_assoc]

omit [NeZero n] in
theorem pdWord_dpWord (k : ℕ) (q : ZMod n) :
    siteWord (pdWord k) q = siteWord (dpWord k) (q + 1) - 1 := by
  induction k generalizing q with
  | zero => simp [pdWord, dpWord]
  | succ k ih =>
      rw [pdWord, siteWord_append, ih, dpWord, siteWord_append]
      congr 2

theorem pdWord_site (k : ℕ) (q : ZMod n) :
    siteWord (pdWord k) q = -(((-q).val - k : ℕ) : ZMod n) := by
  rw [pdWord_dpWord, dpWord_site]
  have h : 1 - (q + 1) = -q := by ring
  rw [h]
  ring

theorem sweepCore_site (k : ℕ) (q : ZMod n) :
    siteWord (sweepCore k) q =
      -(((-collapsePosition q).val - k : ℕ) : ZMod n) := by
  simp only [sweepCore, siteWord_append, siteWord, siteLetter]
  exact pdWord_site k (collapsePosition q)

theorem neg_collapse_val_le (q : ZMod n) (hn : 2 ≤ n) :
    (-collapsePosition q).val ≤ n - 2 := by
  by_cases hq : q = 1
  · simp [collapsePosition, hq]
  · have hv := ZMod.val_lt (-q)
    have hnot : (-q).val ≠ n - 1 := by
      intro he
      have hc := congrArg (fun k : ℕ => (k : ZMod n)) he
      rw [ZMod.natCast_zmod_val, Nat.cast_sub (by omega : 1 ≤ n)] at hc
      simp only [ZMod.natCast_self, Nat.cast_one, zero_sub] at hc
      apply hq
      exact neg_injective hc
    simpa [collapsePosition, hq] using (show (-q).val ≤ n - 2 by omega)

/-- Every initial site reaches zero after the complete aligned sweep. -/
theorem sweepCore_final_site (q : ZMod n) (hn : 2 ≤ n) :
    siteWord (sweepCore (n - 2)) q = 0 := by
  rw [sweepCore_site, Nat.sub_eq_zero_of_le (neg_collapse_val_le q hn)]
  simp

theorem registeredSweep_length_le (q : ZMod n) (hn : 2 ≤ n) :
    (registeredSweep q).length ≤ 3 * n - 4 := by
  have hq := ZMod.val_lt (-q)
  simp only [registeredSweep, List.length_append, pWord_length, sweepCore,
    List.length_cons, List.length_nil, pdWord_length]
  omega

/-- The position just before the defect in pair `k+1`, counted from one. -/
def sweepBeforeDefect (k : ℕ) : List Letter := sweepCore k ++ [.p]

/-- Port zero at a later defect has a singleton original-site fiber. This
does not assume that earlier defects were event-free. -/
theorem sweepBeforeDefect_zero_iff (k : ℕ) (q : ZMod n)
    (hk : k + 2 < n) :
    siteWord (sweepBeforeDefect k) q = 0 ↔ q = -((k + 1 : ℕ) : ZMod n) := by
  rw [sweepBeforeDefect, siteWord_append, sweepCore_site]
  simp only [siteWord, siteLetter]
  have hd : (-collapsePosition q).val - k < n :=
    lt_of_le_of_lt (Nat.sub_le _ _) (ZMod.val_lt _)
  have hiff : -((((-collapsePosition q).val - k : ℕ) : ZMod n)) + 1 = 0 ↔
      (-collapsePosition q).val = k + 1 := by
    constructor
    · intro h
      have hc : (((-collapsePosition q).val - k : ℕ) : ZMod n) = 1 := by
        linear_combination -h
      have he := natCast_injective_below_modulus hd (by omega : 1 < n)
        (show (((-collapsePosition q).val - k : ℕ) : ZMod n) = ((1 : ℕ) : ZMod n)
          from by simpa using hc)
      omega
    · intro h
      rw [h, show k + 1 - k = 1 by omega]
      simp
  rw [hiff]
  constructor
  · intro h
    have hq : q ≠ 1 := by intro he; simp [he, collapsePosition] at h
    have hc := congrArg (fun t : ℕ => (t : ZMod n)) h
    rw [ZMod.natCast_zmod_val] at hc
    simpa [collapsePosition, hq] using congrArg Neg.neg hc
  · intro h
    subst q
    have hq : (-((k + 1 : ℕ) : ZMod n)) ≠ 1 := by
      intro he
      have hc : ((k + 1 : ℕ) : ZMod n) = ((n - 1 : ℕ) : ZMod n) := by
        rw [Nat.cast_sub (by omega : 1 ≤ n)]
        simpa using congrArg Neg.neg he
      have := natCast_injective_below_modulus (by omega : k + 1 < n)
        (by omega : n - 1 < n) hc
      omega
    rw [collapsePosition, if_neg hq, neg_neg,
      ZMod.val_natCast_of_lt (by omega : k + 1 < n)]

theorem sweepCore_zero (k : ℕ) (hn : 2 ≤ n) :
    siteWord (sweepCore k) (0 : ZMod n) = 0 := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h.symm
    omega
  simp [sweepCore_site, collapsePosition, h01]

theorem sweepBeforeDefect_anchor (k : ℕ) (hn : 2 ≤ n) :
    siteWord (sweepBeforeDefect k) (0 : ZMod n) = 1 := by
  rw [sweepBeforeDefect, siteWord_append, sweepCore_zero k hn]
  simp [siteWord, siteLetter]

omit [NeZero n] in
theorem sweepCore_split (k : ℕ) (hk : k + 2 < n) :
    sweepCore (n - 2) = sweepBeforeDefect k ++ .d :: pdWord (n - 3 - k) := by
  have hlen : n - 2 = k + 1 + (n - 3 - k) := by omega
  rw [sweepCore, hlen, pdWord_add, pdWord_snoc]
  simp [sweepBeforeDefect, sweepCore, List.append_assoc]

end FutureEvent
