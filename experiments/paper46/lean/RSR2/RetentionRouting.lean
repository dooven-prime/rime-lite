import RSR2.RetentionNecessity
import RSR2.Construction
import Init.Data.List.MinMax
import Init.Data.List.Nat.Pairwise

/-! Lower-only routing for retention sufficiency.  A safe source arc can be
collapsed to one of its own sites, fixing all retained sites outside it.
All routing words use the existing guarded five-letter semantics.
-/

namespace RSR2.Parametric

def lowerRemap (f : Fin n → Fin n) (P : Placement n) : Placement n :=
  fun a => if (P a).1 = false then (false, f (P a).2) else P a

def LowerRealizes (n : Nat) (hn : 1 < n) (w : List Letter)
    (f : Fin n → Fin n) : Prop :=
  ∀ P, run n hn P w = some (lowerRemap f P)

theorem lowerRemap_comp (f g : Fin n → Fin n) (P : Placement n) :
    lowerRemap g (lowerRemap f P) = lowerRemap (fun q => g (f q)) P := by
  funext a
  unfold lowerRemap
  by_cases h : (P a).1 = false <;> simp [h]

theorem LowerRealizes.append (h : LowerRealizes n hn w f)
    (h' : LowerRealizes n hn w' g) :
    LowerRealizes n hn (w ++ w') (fun q => g (f q)) := by
  intro P
  rw [run_append, h P]
  simpa only [Option.bind_some, lowerRemap_comp] using h' (lowerRemap f P)

theorem lower_rotation_realizes (n : Nat) (hn : 1 < n) (k : Nat) :
    LowerRealizes n hn (pWord false k) (fun q => nextMany n (by omega) q k) := by
  intro P
  rw [pWord, run_powers]
  congr 1
  funext a
  exact rotateMany_apply n (by omega) P false k a

/-- A local defect is expanded into actual rotations, one `d₀`, and rotations.
It changes just site `j+1` to site `j`; no elevator is used. -/
theorem lower_local_collapse_realizes (n : Nat) (hn : 1 < n)
    (j : Nat) (hj : j + 1 < n) :
    ∃ w, LowerRealizes n hn w
      (fun q => if q.val = j + 1 then ⟨j, by omega⟩ else q) := by
  refine ⟨pWord false (n - j) ++ [.d false] ++ pWord false j, ?_⟩
  intro P
  rw [run_append, run_append, show pWord false (n-j) =
    List.replicate (n-j) (.p false) from rfl, run_powers]
  simp only [Option.bind_some, run, step_d]
  rw [pWord, run_powers]
  congr 1
  funext a
  by_cases h : (P a).1 = false
  · have hq := (P a).2.isLt
    have hr := nextMany_val n (by omega) (P a).2 (n-j)
    have hport : nextMany n (by omega) (P a).2 (n-j) = site1 n hn ↔
        (P a).2.val = j+1 := by
      rw [Fin.ext_iff, nextMany_val]
      change ((P a).2.val + (n-j)) % n = 1 ↔ _
      by_cases hc : (P a).2.val < j
      · rw [Nat.mod_eq_of_lt (by omega)]
        omega
      · have heq : (P a).2.val + (n-j) = n + ((P a).2.val-j) := by omega
        have hs : (P a).2.val-j < n := by omega
        simp only [heq, Nat.add_mod, Nat.mod_self, Nat.zero_add,
          Nat.mod_eq_of_lt hs]
        omega
    simp only [rotateMany_apply, h, if_pos, collapse, Prod.mk.injEq,
      true_and, hport, lowerRemap]
    by_cases he : (P a).2.val = j+1
    · simp only [he, if_pos]
      congr 1
      apply Fin.ext
      rw [nextMany_val]
      simp only [site0]
      rw [Nat.zero_add, Nat.mod_eq_of_lt (by omega)]
    · simp only [he, if_false, if_true]
      congr 1
      apply Fin.ext
      rw [nextMany_val, nextMany_val, Nat.mod_add_mod]
      have hs : (P a).2.val + (n-j) + j = (P a).2.val + n := by omega
      rw [hs, Nat.add_mod, Nat.mod_self, Nat.add_zero,
        Nat.mod_eq_of_lt hq, Nat.mod_eq_of_lt hq]
  · have hu : (P a).1 = true := by cases h' : (P a).1 <;> simp_all
    have hnloc : P a ≠ (false, site1 n hn) := by
      intro he; have := congrArg Prod.fst he; simp_all
    simp [rotateMany_apply, hu, collapse, hnloc, lowerRemap]

/-- Descending local collapses gather the whole linear interval at its first
site.  This statement applies to arbitrary packets, not only singleton seeds. -/
theorem lower_interval_collapse_realizes (n : Nat) (hn : 1 < n)
    (lo len : Nat) (hhi : lo + len < n) :
    ∃ w, LowerRealizes n hn w
      (fun q => if lo ≤ q.val ∧ q.val ≤ lo+len then ⟨lo, by omega⟩ else q) := by
  induction len with
  | zero =>
      refine ⟨[], ?_⟩
      intro P
      change some P = some _
      congr 1
      funext a
      unfold lowerRemap
      by_cases h : (P a).1 = false
      · simp only [h, if_pos]
        by_cases he : (P a).2.val = lo
        · have hq : (P a).2 = (⟨lo, by omega⟩ : Fin n) := Fin.ext he
          simp only [hq, Fin.val_mk, Nat.add_zero, Nat.le_refl, and_self, if_true]
          exact Prod.ext h hq
        · have hh : ¬ (lo ≤ (P a).2.val ∧ (P a).2.val ≤ lo+0) := by omega
          simp only [if_neg hh]
          exact Prod.ext h rfl
      · simp [h]
  | succ len ih =>
      obtain ⟨w, hw⟩ := ih (by omega)
      obtain ⟨e, he⟩ := lower_local_collapse_realizes n hn (lo+len) (by omega)
      refine ⟨e++w, ?_⟩
      have hh := he.append hw
      have hf : (fun q : Fin n =>
          if lo ≤ (if q.val = lo+len+1 then (⟨lo+len, by omega⟩ : Fin n) else q).val ∧
            (if q.val = lo+len+1 then (⟨lo+len, by omega⟩ : Fin n) else q).val ≤ lo+len
          then (⟨lo, by omega⟩ : Fin n)
          else if q.val = lo+len+1 then ⟨lo+len, by omega⟩ else q) =
          (fun q : Fin n => if lo ≤ q.val ∧ q.val ≤ lo+(len+1)
            then ⟨lo, by omega⟩ else q) := by
        funext q
        by_cases hq : q.val = lo+len+1
        · simp only [if_pos hq]
          have ha : lo ≤ lo+len ∧ lo+len ≤ lo+len := by omega
          have hb : lo ≤ q.val ∧ q.val ≤ lo+(len+1) := by omega
          simp [ha, hb]
        · simp only [hq, if_neg]
          by_cases hb : lo ≤ q.val ∧ q.val ≤ lo+len
          · have hc : lo ≤ q.val ∧ q.val ≤ lo+(len+1) := by omega
            simp [hb, hc]
          · have hc : ¬(lo ≤ q.val ∧ q.val ≤ lo+(len+1)) := by omega
            simp [hb, hc]
      rw [hf] at hh
      exact hh

end RSR2.Parametric
