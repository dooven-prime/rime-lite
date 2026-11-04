import ProperArc.LocalMerge

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def segmentPlacement (c : ZMod n) (lo ell : ℕ)
    (P : Placement n (Finset (ZMod n))) : Placement n (Finset (ZMod n)) :=
  fun q => if q = (lo : ZMod n) then some (interval c lo (lo + ell))
    else if lo < q.val ∧ q.val < lo + ell then none else P q

def assembleWord (lo : ℕ) : ℕ → List Letter
  | 0 => []
  | 1 => []
  | ell + 2 => assembleWord (lo + 1) (ell + 1) ++ localLetters (lo : ZMod n)

omit [NeZero n] in
theorem segmentPlacement_at (c : ZMod n) (lo ell : ℕ) (P : Placement n (Finset (ZMod n))) :
    segmentPlacement c lo ell P (lo : ZMod n) = some (interval c lo (lo + ell)) := by
  simp [segmentPlacement]

omit [NeZero n] in
theorem interval_singleton (c : ZMod n) (lo : ℕ) :
    interval c lo (lo + 1) = {c + (lo : ZMod n)} := by
  simp [interval]

omit [NeZero n] in
theorem segmentPlacement_one (c : ZMod n) (lo : ℕ)
    (P : Placement n (Finset (ZMod n))) (_hlo : lo < n)
    (hp : P (lo : ZMod n) = some {c + (lo : ZMod n)}) :
    segmentPlacement c lo 1 P = P := by
  funext q
  by_cases hq : q = (lo : ZMod n)
  · subst q
    simp [segmentPlacement, interval_singleton, hp]
  · simp [segmentPlacement, hq]

theorem segmentPlacement_step (c : ZMod n) (lo ell : ℕ)
    (P : Placement n (Finset (ZMod n))) (hb : lo + ell + 2 ≤ n)
    (hp : P (lo : ZMod n) = some {c + (lo : ZMod n)}) :
    localFusion (lo : ZMod n) (segmentPlacement c (lo + 1) (ell + 1) P) =
      segmentPlacement c lo (ell + 2) P := by
  have hcast : ((lo + 1 : ℕ) : ZMod n) = (lo : ZMod n) + 1 := by push_cast; rfl
  have hlo : ((lo : ZMod n)).val = lo := ZMod.val_natCast_of_lt (by omega)
  have hnext : (((lo + 1 : ℕ) : ZMod n)).val = lo + 1 := ZMod.val_natCast_of_lt (by omega)
  have hne : (lo : ZMod n) ≠ ((lo + 1 : ℕ) : ZMod n) := by
    intro h
    have := congrArg ZMod.val h
    rw [hlo, hnext] at this
    omega
  have hp0 : segmentPlacement c (lo + 1) (ell + 1) P (lo : ZMod n) =
      some {c + (lo : ZMod n)} := by
    simp only [segmentPlacement, hne, ite_false, hlo, hp]
    rw [if_neg (by omega)]
  have hp1 : segmentPlacement c (lo + 1) (ell + 1) P ((lo : ZMod n) + 1) =
      some (interval c (lo + 1) (lo + (ell + 2))) := by
    rw [← hcast, segmentPlacement_at]
    congr 2
    omega
  have hunion : {c + (lo : ZMod n)} ∪ interval c (lo + 1) (lo + (ell + 2)) =
      interval c lo (lo + (ell + 2)) := by
    rw [← interval_singleton]
    exact interval_union c lo (lo + 1) _ (by omega) (by omega) (by omega)
  funext q
  by_cases hq : q = (lo : ZMod n)
  · subst q
    simp only [localFusion, ite_true, hp0, hp1, segmentPlacement_at, hunion]
  by_cases hq1 : q = ((lo + 1 : ℕ) : ZMod n)
  · subst q
    have hqne : ((lo + 1 : ℕ) : ZMod n) ≠ (lo : ZMod n) := hne.symm
    simp only [localFusion, hqne, ite_false, ← hcast, ite_true]
    simp only [segmentPlacement, hqne, ite_false, hnext]
    rw [if_pos (by omega)]
  · have hval : q.val ≠ lo + 1 := by
      intro h
      apply hq1
      rw [← ZMod.natCast_zmod_val q, h]
    have heq : (lo + 1 < q.val ∧ q.val < lo + 1 + (ell + 1)) ↔
        (lo < q.val ∧ q.val < lo + (ell + 2)) := by omega
    simp only [localFusion, hq, ite_false, ← hcast, hq1, segmentPlacement, heq]

/-- A strict parent interval is assembled by real local fusion macros.
The selected origin and chain remain unchanged throughout the construction. -/
theorem assemble_strict_parent (c : ZMod n) (r ell lo : ℕ)
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (hr : r ≤ n) (hF : F = arc c r) (hell : 1 ≤ ell) (hstrict : ell < r)
    (hbound : lo + ell ≤ r) (hreg : s.origin = none)
    (hsingle : ∀ i, lo ≤ i → i < lo + ell →
      s.placed (i : ZMod n) = some {c + (i : ZMod n)}) :
    run F s (assembleWord (n := n) lo ell) =
      { s with placed := segmentPlacement c lo ell s.placed } := by
  induction ell using Nat.twoStepInduction generalizing lo s with
  | zero => omega
  | one =>
      simp only [assembleWord, run, List.foldl_nil]
      rw [segmentPlacement_one c lo s.placed (by omega) (hsingle lo (by omega) (by omega))]
  | more ell _ ih =>
      have htail := ih (lo + 1) s (by omega) (by omega) (by omega) hreg
        (fun i hi hj => hsingle i (by omega) (by omega))
      let t : Execution n (ZMod n) :=
        { s with placed := segmentPlacement c (lo + 1) (ell + 1) s.placed }
      have hval : ((lo : ZMod n)).val = lo := ZMod.val_natCast_of_lt (by omega)
      have hval1 : (((lo + 1 : ℕ) : ZMod n)).val = lo + 1 := ZMod.val_natCast_of_lt (by omega)
      have hne : (lo : ZMod n) ≠ ((lo + 1 : ℕ) : ZMod n) := by
        intro h
        have := congrArg ZMod.val h
        rw [hval, hval1] at this
        omega
      have h0 : t.placed (lo : ZMod n) = some {c + (lo : ZMod n)} := by
        change segmentPlacement c (lo + 1) (ell + 1) s.placed (lo : ZMod n) = _
        simp only [segmentPlacement, hne, ite_false, hval]
        rw [if_neg (by omega)]
        exact hsingle lo (by omega) (by omega)
      have h1 : t.placed ((lo : ZMod n) + 1) =
          some (interval c (lo + 1) (lo + (ell + 2))) := by
        rw [← show ((lo + 1 : ℕ) : ZMod n) = (lo : ZMod n) + 1 by simp]
        change segmentPlacement c (lo + 1) (ell + 1) s.placed _ = _
        rw [segmentPlacement_at]
        congr 2
        omega
      have hU : {c + (lo : ZMod n)} ∪ interval c (lo + 1) (lo + (ell + 2)) =
          interval c lo (lo + (ell + 2)) := by
        rw [← interval_singleton]
        exact interval_union c lo (lo + 1) _ (by omega) (by omega) (by omega)
      have hnot : {c + (lo : ZMod n)} ∪ interval c (lo + 1) (lo + (ell + 2)) ≠ F := by
        intro heq
        have hc := congrArg Finset.card heq
        rw [hU, card_interval c lo _ (by omega), hF, card_arc c r hr] at hc
        omega
      rw [assembleWord, run_append, htail]
      rw [run_local_unregistered F t (lo : ZMod n) _ _ h0 h1 hreg hnot]
      change { s with placed := localFusion _ (segmentPlacement _ _ _ _) } = _
      rw [segmentPlacement_step c lo ell s.placed (by omega)
        (hsingle lo (by omega) (by omega))]

end ProperArc
