import RSR2History.LoggedExecution
import Mathlib.Order.Lattice.Nat

/-!
The auxiliary lower-ring extraction problem. A configuration records the
site of each remaining singleton, or `none` after deletion. Rotations and
non-idle slides cost one; a prescribed singleton deletion costs zero.
Neither upper-layer operations nor fusion edges occur in this model.
-/

namespace RSR2History
open RSR2.Parametric

abbrev LowerConfiguration (n : Nat) := Fin n → Option (Fin n)

def lowerConfiguration (P : Placement n) : LowerConfiguration n :=
  fun a => if (P a).1 = false then some (P a).2 else none

def lowerExtractionSeed (n : Nat) : LowerConfiguration n := fun a => some a
def lowerExtractionEmpty (n : Nat) : LowerConfiguration n := fun _ => none

def LowerConfiguration.Valid (c : LowerConfiguration n) : Prop :=
  ∀ a b q, c a = some q → c b = some q → a = b

def lowerRotate (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) :
    LowerConfiguration n := fun a => (c a).map (next n (by omega))

def lowerSlide (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) :
    LowerConfiguration n := fun a =>
  if c a = some (site1 n hn) then some (site0 n (by omega)) else c a

def lowerDelete (c : LowerConfiguration n) (a : Fin n) : LowerConfiguration n :=
  fun b => if b = a then none else c b

/-- The indices retain the actual deletion order and exact preparation cost.
The slide guard excludes both fusion and idle defects. -/
inductive LowerExtractionPath (n : Nat) (hn : 1 < n) :
    LowerConfiguration n → List (Fin n) → LowerConfiguration n → Nat → Prop where
  | refl (c) : LowerExtractionPath n hn c [] c 0
  | rotate (c) : LowerExtractionPath n hn c [] (lowerRotate n hn c) 1
  | slide (c)
      (empty : ∀ a, c a ≠ some (site0 n (by omega)))
      (occupied : ∃ a, c a = some (site1 n hn)) :
      LowerExtractionPath n hn c [] (lowerSlide n hn c) 1
  | delete (c) (a)
      (atPort : c a = some (site0 n (by omega)))
      (singleton : ∀ b, c b = some (site0 n (by omega)) → b = a) :
      LowerExtractionPath n hn c [a] (lowerDelete c a) 0
  | trans {c d e} {u v} {k l}
      (first : LowerExtractionPath n hn c u d k)
      (second : LowerExtractionPath n hn d v e l) :
      LowerExtractionPath n hn c (u ++ v) e (k + l)

def lowerRotateMany (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) : Nat →
    LowerConfiguration n
  | 0 => c
  | k + 1 => lowerRotateMany n hn (lowerRotate n hn c) k

theorem lowerRotateMany_path {n : Nat} {hn : 1 < n}
    (c : LowerConfiguration n) (k : Nat) :
    LowerExtractionPath n hn c [] (lowerRotateMany n hn c k) k := by
  induction k generalizing c with
  | zero => exact .refl c
  | succ k ih =>
      rw [show k + 1 = Nat.succ k by omega, lowerRotateMany]
      simpa only [List.nil_append, Nat.one_add] using
        (LowerExtractionPath.trans (LowerExtractionPath.rotate c)
          (ih (lowerRotate n hn c)))

theorem lowerRotateMany_apply {n : Nat} {hn : 1 < n}
    (c : LowerConfiguration n) (k : Nat) (a q : Fin n)
    (hc : c a = some q) :
    lowerRotateMany n hn c k a = some (nextMany n (by omega) q k) := by
  induction k generalizing c q with
  | zero => simpa [lowerRotateMany, nextMany] using hc
  | succ k ih =>
      apply ih (lowerRotate n hn c) (next n (by omega) q)
      simp [lowerRotate, hc]

theorem lowerRotateMany_none {n : Nat} {hn : 1 < n}
    (c : LowerConfiguration n) (k : Nat) (a : Fin n)
    (hc : c a = none) : lowerRotateMany n hn c k a = none := by
  induction k generalizing c with
  | zero => simpa [lowerRotateMany] using hc
  | succ k ih =>
      apply ih (lowerRotate n hn c)
      simp [lowerRotate, hc]

@[simp] theorem lowerConfiguration_seed (n : Nat) :
    lowerConfiguration (seed n) = lowerExtractionSeed n := by
  funext a
  simp [lowerConfiguration, seed, lowerExtractionSeed]

theorem lowerExtractionSeed_valid (n : Nat) : (lowerExtractionSeed n).Valid := by
  intro a b q ha hb
  simp only [lowerExtractionSeed, Option.some.injEq] at ha hb
  exact ha.trans hb.symm

theorem LowerExtractionPath.valid {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k) (hvalid : c.Valid) : d.Valid := by
  induction path with
  | refl => exact hvalid
  | rotate c =>
      intro a b q ha hb
      cases hca : c a with
      | none => simp [lowerRotate, hca] at ha
      | some qa =>
          cases hcb : c b with
          | none => simp [lowerRotate, hcb] at hb
          | some qb =>
              have hab : next n (by omega) qa = next n (by omega) qb := by
                simpa [lowerRotate, hca, hcb] using ha.trans hb.symm
              have hq := next_injective n (by omega) hab
              exact hvalid a b qa hca (by simpa [hq] using hcb)
  | slide c empty occupied =>
      intro a b q ha hb
      by_cases hca : c a = some (site1 n hn)
      · have hq : site0 n (by omega) = q := by simpa [lowerSlide, hca] using ha
        have hcb : c b = some (site1 n hn) := by
          by_contra h
          have hb0 : c b = some (site0 n (by omega)) := by
            simpa [lowerSlide, h, ← hq] using hb
          exact empty b hb0
        exact hvalid a b _ hca hcb
      · by_cases hcb : c b = some (site1 n hn)
        · have hq : site0 n (by omega) = q := by simpa [lowerSlide, hcb] using hb
          exact False.elim (empty a (by simpa [lowerSlide, hca, ← hq] using ha))
        · exact hvalid a b q (by simpa [lowerSlide, hca] using ha)
            (by simpa [lowerSlide, hcb] using hb)
  | delete c a atPort singleton =>
      intro b e q hb he
      by_cases hba : b = a
      · simp [lowerDelete, hba] at hb
      · by_cases hea : e = a
        · simp [lowerDelete, hea] at he
        · exact hvalid b e q (by simpa [lowerDelete, hba] using hb)
            (by simpa [lowerDelete, hea] using he)
  | trans first second ih₁ ih₂ => exact ih₂ (ih₁ hvalid)

/-- No auxiliary operation recreates an atom; precisely the listed deletions
remove atoms. This also certifies that a full permutation ends empty. -/
theorem LowerExtractionPath.support {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k) (a : Fin n) :
    d a ≠ none ↔ c a ≠ none ∧ a ∉ z := by
  induction path with
  | refl => simp
  | rotate c => cases h : c a <;> simp [lowerRotate, h]
  | slide c empty occupied =>
      by_cases h : c a = some (site1 n hn)
      · simp [lowerSlide, h]
      · simp [lowerSlide, h]
  | delete c b atPort singleton =>
      by_cases h : a = b <;> simp [lowerDelete, h]
  | trans first second ih₁ ih₂ => simp [ih₂, ih₁, and_assoc]

theorem LowerExtractionPath.terminal_empty {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k) (hcover : ∀ a, a ∈ z) :
    d = lowerExtractionEmpty n := by
  funext a
  have h := path.support a
  simpa [lowerExtractionEmpty, hcover a] using not_ne_iff.mp (by tauto : ¬ d a ≠ none)

theorem lowerExtractionPath_exists_of_order
    {n : Nat} {hn : 1 < n} {c : LowerConfiguration n}
    {z : List (Fin n)}
    (hvalid : c.Valid) (hnodup : z.Nodup)
    (hcover : ∀ a ∈ z, c a ≠ none) :
    ∃ d k, LowerExtractionPath n hn c z d k := by
  induction z generalizing c with
  | nil => exact ⟨c, 0, .refl c⟩
  | cons a rest ih =>
      have ha : c a ≠ none := hcover a (by simp)
      cases hq : c a with
      | none => exact (ha hq).elim
      | some q =>
          let turns : Nat := if q.val = 0 then 0 else n - q.val
          have hturns :
              (nextMany n (by omega) q turns) = site0 n (by omega) := by
            apply Fin.ext
            simp only [nextMany_val]
            by_cases hzero : q.val = 0
            · simp [turns, hzero, site0]
            · have hqpos : 0 < q.val := by omega
              have hlt : q.val < n := q.isLt
              have hsum : q.val + (n - q.val) = n := by omega
              simp [turns, hzero, hsum, site0]
          let route := lowerRotateMany n hn c turns
          have hroute : route a = some (site0 n (by omega)) := by
            simp [route, lowerRotateMany_apply c turns a q hq, hturns]
          have hroutePath : LowerExtractionPath n hn c [] route turns := by
            exact lowerRotateMany_path c turns
          have hrouteValid : route.Valid := LowerExtractionPath.valid hroutePath hvalid
          have hsingleton : ∀ b, route b = some (site0 n (by omega)) → b = a := by
            intro b hb
            have hab := hrouteValid b a _ hb hroute
            exact hab
          let deleted := lowerDelete route a
          have hdelete : LowerExtractionPath n hn route [a] deleted 0 :=
            .delete route a hroute hsingleton
          have hdeletedValid : deleted.Valid := LowerExtractionPath.valid hdelete hrouteValid
          have hrestCover : ∀ b ∈ rest, deleted b ≠ none := by
            intro b hb
            have hba : b ≠ a := by
              intro hba
              subst b
              exact (List.nodup_cons.mp hnodup).1 hb
            have hcb : c b ≠ none := hcover b (by simp [hb])
            cases hqb : c b with
            | none => exact (hcb hqb).elim
            | some qb =>
                have hrb : route b = some (nextMany n (by omega) qb turns) :=
                  lowerRotateMany_apply c turns b qb hqb
                simp [deleted, lowerDelete, hba, hrb]
          obtain ⟨e, k, htail⟩ := ih hdeletedValid
            (List.nodup_cons.mp hnodup).2 hrestCover
          refine ⟨e, turns + k, ?_⟩
          have hfirst := hroutePath.trans hdelete
          simpa [hfirst, Nat.add_assoc] using hfirst.trans htail

theorem lowerExtractionPath_exists_of_permutation
    {n : Nat} {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup) :
    ∃ k, LowerExtractionPath n hn (lowerExtractionSeed n) z
      (lowerExtractionEmpty n) k := by
  obtain ⟨d, k, path⟩ := @lowerExtractionPath_exists_of_order n hn
    (lowerExtractionSeed n) z (lowerExtractionSeed_valid n) hnodup (by
      intro a ha
      simp [lowerExtractionSeed])
  have hcover : ∀ a, a ∈ z := by
    intro a
    have hset : z.toFinset = Finset.univ := by
      apply (Finset.card_eq_iff_eq_univ _).mp
      rw [List.toFinset_card_of_nodup hnodup, hlen]
      simp
    have : a ∈ z.toFinset := by simp [hset]
    simpa using this
  have hempty := @LowerExtractionPath.terminal_empty n hn
    (lowerExtractionSeed n) d z k path hcover
  exact ⟨k, by simpa [hempty] using path⟩

/-- The independent auxiliary optimum. Attainment is asserted only with a
nonempty feasible-cost set; actual delayed-chain projection supplies one. -/
noncomputable def lowerExtractionCost (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) : Nat :=
  sInf {k | LowerExtractionPath n hn (lowerExtractionSeed n) z
    (lowerExtractionEmpty n) k}

theorem lowerExtractionCost_le {n : Nat} {hn : 1 < n}
    {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn (lowerExtractionSeed n) z
      (lowerExtractionEmpty n) k) : lowerExtractionCost n hn z ≤ k :=
  Nat.sInf_le path

theorem lowerExtractionCost_attained {n : Nat} {hn : 1 < n}
    {z : List (Fin n)}
    (h : ∃ k, LowerExtractionPath n hn (lowerExtractionSeed n) z
      (lowerExtractionEmpty n) k) :
    LowerExtractionPath n hn (lowerExtractionSeed n) z (lowerExtractionEmpty n)
      (lowerExtractionCost n hn z) := Nat.sInf_mem h

/-- A full duplicate-free order has an optimal auxiliary path independently
of whether a physical delayed-chain realization has already been supplied. -/
theorem lowerExtractionCost_attained_of_permutation
    {n : Nat} {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup) :
    LowerExtractionPath n hn (lowerExtractionSeed n) z (lowerExtractionEmpty n)
      (lowerExtractionCost n hn z) :=
  lowerExtractionCost_attained (lowerExtractionPath_exists_of_permutation hlen hnodup)

end RSR2History
