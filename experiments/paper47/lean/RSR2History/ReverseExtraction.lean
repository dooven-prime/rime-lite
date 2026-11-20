import RSR2History.LowerExtractionModel
import Mathlib.Data.List.OfFn
import Mathlib.Data.List.Nodup

/-!
An exact auxiliary optimum proved without a finite optimizer.  A full layer
must rotate n-1 times before deleting atom 1; each subsequent deletion needs
a new positive-cost preparation.  A reverse sweep attains their sum.
-/

namespace RSR2History
open RSR2.Parametric

private noncomputable def extractionPortOccupied (n : Nat) (hn : 1 < n)
    (c : LowerConfiguration n) : Nat := by
  classical
  exact if ∃ a, c a = some (site0 n (by omega)) then 1 else 0

private theorem extractionPortOccupied_le_one (n : Nat) (hn : 1 < n)
    (c : LowerConfiguration n) : extractionPortOccupied n hn c ≤ 1 := by
  classical
  unfold extractionPortOccupied
  split <;> omega

/-- Each deletion consumes an occupied lower port; only a positive-cost
preparation can replenish it.  This holds for every auxiliary path. -/
theorem LowerExtractionPath.port_budget {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k) :
    z.length + extractionPortOccupied n hn d ≤
      k + extractionPortOccupied n hn c := by
  classical
  induction path with
  | refl => simp
  | rotate c =>
      have := extractionPortOccupied_le_one n hn (lowerRotate n hn c)
      simp only [List.length_nil]
      omega
  | slide c empty occupied =>
      have := extractionPortOccupied_le_one n hn (lowerSlide n hn c)
      simp only [List.length_nil]
      omega
  | delete c a atPort singleton =>
      have hbefore : extractionPortOccupied n hn c = 1 := by
        simp only [extractionPortOccupied, if_pos (show ∃ b, c b = some _ from ⟨a, atPort⟩)]
      have hafter : extractionPortOccupied n hn (lowerDelete c a) = 0 := by
        have hnot : ¬ ∃ b, lowerDelete c a b = some (site0 n (by omega)) := by
          rintro ⟨b, hb⟩
          by_cases hba : b = a
          · simp [lowerDelete, hba] at hb
          · have hcb : c b = some (site0 n (by omega)) := by
              simpa [lowerDelete, hba] using hb
            exact hba (singleton b hcb)
        simp [extractionPortOccupied, hnot]
      simp [hbefore, hafter]
  | trans first second ih₁ ih₂ =>
      simp only [List.length_append]
      omega

/-- Split at the actual first zero-cost deletion, retaining its real
configuration, singleton guard and the exact additive preparation cost. -/
theorem LowerExtractionPath.first_delete {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k)
    {a : Fin n} {rest : List (Fin n)} (order : z = a :: rest) :
    ∃ before p q,
      LowerExtractionPath n hn c [] before p ∧
      before a = some (site0 n (by omega)) ∧
      (∀ b, before b = some (site0 n (by omega)) → b = a) ∧
      LowerExtractionPath n hn (lowerDelete before a) rest d q ∧ k = p + q := by
  induction path generalizing a rest with
  | refl => simp at order
  | rotate => simp at order
  | slide => simp at order
  | delete c b atPort singleton =>
      have he : b = a ∧ rest = [] := by simpa using order
      obtain ⟨rfl, rfl⟩ := he
      exact ⟨c, 0, 0, .refl c, atPort, singleton, .refl _, rfl⟩
  | @trans c d e u v k l first second ih₁ ih₂ =>
      cases u with
      | nil =>
          obtain ⟨before, p, q, hpre, hat, hsingle, htail, hcost⟩ := ih₂ order
          exact ⟨before, k + p, q, by simpa using first.trans hpre,
            hat, hsingle, htail, by omega⟩
      | cons b tail =>
          have he : b = a ∧ tail ++ v = rest := by simpa using order
          obtain ⟨rfl, rfl⟩ := he
          obtain ⟨before, p, q, hpre, hat, hsingle, htail, hcost⟩ := ih₁ rfl
          exact ⟨before, p, q + l, hpre, hat, hsingle,
            htail.trans second, by omega⟩

private def extractionFull (c : LowerConfiguration n) : Prop :=
  ∀ q, ∃ a, c a = some q

private theorem extractionFull_rotate {n : Nat} {hn : 1 < n}
    {c : LowerConfiguration n} (full : extractionFull c) :
    extractionFull (lowerRotate n hn c) := by
  intro q
  obtain ⟨r, hr⟩ := (Finite.surjective_of_injective (next_injective n (by omega))) q
  obtain ⟨a, ha⟩ := full r
  exact ⟨a, by simp [lowerRotate, ha, hr]⟩

/-- With no deletion and no hole, slides cannot occur. The endpoint is
exactly the initial configuration rotated by the entire preparation cost. -/
private theorem noDeletion_full {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k)
    (order : z = []) (full : extractionFull c) :
    extractionFull d ∧
      ∀ a q, c a = some q → d a = some (nextMany n (by omega) q k) := by
  induction path with
  | refl => exact ⟨full, by intro a q ha; simpa [nextMany] using ha⟩
  | rotate c =>
      refine ⟨extractionFull_rotate full, ?_⟩
      intro a q ha
      simp [lowerRotate, ha, nextMany]
  | slide c empty occupied =>
      obtain ⟨a, ha⟩ := full (site0 n (by omega))
      exact (empty a ha).elim
  | delete => simp at order
  | @trans c d e u v k l first second ih₁ ih₂ =>
      obtain ⟨hu, hv⟩ := List.append_eq_nil_iff.mp order
      obtain ⟨hdfull, hd⟩ := ih₁ hu full
      obtain ⟨hefull, he⟩ := ih₂ hv hdfull
      refine ⟨hefull, ?_⟩
      intro a q ha
      rw [he _ _ (hd _ _ ha)]
      congr 1
      apply Fin.ext
      simp [nextMany_val, Nat.mod_add_mod, Nat.add_assoc]

/-- Any deletion order first pays the directed rotation distance from its
first atom to the lower port, then at least one unit before every further
deletion. -/
theorem LowerExtractionPath.first_atom_cost_lower_bound
    {n : Nat} {hn : 1 < n} {rest : List (Fin n)}
    {a : Fin n}
    {d : LowerConfiguration n} {k : Nat}
    (path : LowerExtractionPath n hn (lowerExtractionSeed n)
      (a :: rest) d k) :
    (n - a.val) % n + rest.length ≤ k := by
  classical
  obtain ⟨before, p, q, hpre, hat, hsingle, htail, hcost⟩ := path.first_delete rfl
  have hfull : extractionFull (lowerExtractionSeed n) := by
    intro r
    exact ⟨r, rfl⟩
  have hport := (noDeletion_full hpre rfl hfull).2 a a rfl
  have he : (a.val + p) % n = 0 := by
    have h := congrArg (fun opt => opt.map Fin.val) (hport.symm.trans hat)
    simpa [nextMany_val, site0] using h
  have hp : (n - a.val) % n ≤ p := by
    by_cases ha0 : a.val = 0
    · simp [ha0]
    · have ha : 0 < a.val := by omega
      have hna : n - a.val < n := by omega
      rw [Nat.mod_eq_of_lt hna]
      by_contra hlt
      have hp' : p < n - a.val := by omega
      have hsum : a.val + p < n := by omega
      rw [Nat.mod_eq_of_lt hsum] at he
      omega
  have hempty : extractionPortOccupied n hn (lowerDelete before a) = 0 := by
    have hnot : ¬ ∃ b, lowerDelete before a b =
        some (site0 n (by omega)) := by
      rintro ⟨b, hb⟩
      by_cases hba : b = a
      · simp [lowerDelete, hba] at hb
      · exact hba (hsingle b (by simpa [lowerDelete, hba] using hb))
    simp [extractionPortOccupied, hnot]
  have htailCost := htail.port_budget
  rw [hempty] at htailCost
  omega

/-- Preserve the original first-one path interface as a specialization. -/
theorem LowerExtractionPath.first_one_cost_lower_bound
    {n : Nat} {hn : 1 < n} {rest : List (Fin n)}
    {d : LowerConfiguration n} {k : Nat}
    (path : LowerExtractionPath n hn (lowerExtractionSeed n)
      (site1 n hn :: rest) d k) :
    (n - 1) + rest.length ≤ k := by
  have h := path.first_atom_cost_lower_bound
  simpa [site1] using h

/-- A full duplicate-free order pays its first atom's directed distance to
the port, plus one new preparation for every later deletion. -/
theorem lowerExtractionCost_first_atom_lower_bound
    {n : Nat} {hn : 1 < n} {a : Fin n} {rest : List (Fin n)}
    (hlen : (a :: rest).length = n)
    (hnodup : (a :: rest).Nodup) :
    (n - a.val) % n + (n - 1) ≤ lowerExtractionCost n hn (a :: rest) := by
  have path := lowerExtractionCost_attained_of_permutation
    (hn := hn) hlen hnodup
  have h := path.first_atom_cost_lower_bound
  simp only [List.length_cons] at hlen
  omega

/-- The first-atom-one estimate is the special case of the uniform bound. -/
theorem lowerExtractionCost_first_one_lower_bound
    {n : Nat} {hn : 1 < n} {rest : List (Fin n)}
    (hlen : (site1 n hn :: rest).length = n)
    (hnodup : (site1 n hn :: rest).Nodup) :
    2 * n - 2 ≤ lowerExtractionCost n hn (site1 n hn :: rest) := by
  have h := lowerExtractionCost_first_atom_lower_bound (hn := hn)
    (a := site1 n hn) hlen hnodup
  have hrho : (n - (site1 n hn).val) % n = n - 1 := by
    simp [site1]
  rw [hrho] at h
  omega

/-- The atom at extraction index i in (1,0,n-1,...,2). -/
def reverseExtractionAtom (n : Nat) (hn : 1 < n) (i : Fin n) : Fin n :=
  ⟨if i.val = 0 then 1 else if i.val = 1 then 0 else n + 1 - i.val,
    by split_ifs <;> omega⟩

def reverseExtractionOrder (n : Nat) (hn : 1 < n) : List (Fin n) :=
  List.ofFn (reverseExtractionAtom n hn)

@[simp] theorem reverseExtractionOrder_length (n : Nat) (hn : 1 < n) :
    (reverseExtractionOrder n hn).length = n := by simp [reverseExtractionOrder]

theorem reverseExtractionOrder_nodup (n : Nat) (hn : 1 < n) :
    (reverseExtractionOrder n hn).Nodup := by
  have hinj : Function.Injective (reverseExtractionAtom n hn) := by
    intro i j he
    apply Fin.ext
    have hv := congrArg Fin.val he
    simp only [reverseExtractionAtom] at hv
    split_ifs at hv <;> omega
  rw [reverseExtractionOrder, List.ofFn_eq_map]
  exact (List.nodup_finRange n).map hinj

private def sweepSite (n : Nat) (hn : 1 < n) (i : Fin n) : Fin n :=
  ⟨if i.val = 0 then 0 else n - i.val, by split_ifs <;> omega⟩

/-- Once the next named singleton is at zero and the remaining names
occupy successive predecessor sites, one rotation prepares each deletion. -/
private theorem sweep_path {n : Nat} {hn : 1 < n}
    {z : List (Fin n)} {c : LowerConfiguration n}
    (hvalid : c.Valid) (hnodup : z.Nodup) (hlen : z.length ≤ n)
    (packed : ∀ i (hi : i < z.length),
      c z[i] = some (sweepSite n hn ⟨i, by omega⟩)) :
    ∃ d, LowerExtractionPath n hn c z d (z.length - 1) := by
  induction z generalizing c with
  | nil => exact ⟨c, .refl c⟩
  | cons a rest ih =>
      have hat : c a = some (site0 n (by omega)) := by
        exact packed 0 (by simp)
      have hsingle : ∀ b, c b = some (site0 n (by omega)) → b = a := by
        intro b hb
        exact hvalid b a _ hb hat
      have hdelete : LowerExtractionPath n hn c [a] (lowerDelete c a) 0 :=
        .delete c a hat hsingle
      cases rest with
      | nil => exact ⟨_, by simpa using hdelete⟩
      | cons b tail =>
          let d := lowerRotate n hn (lowerDelete c a)
          have hrestLen : (b :: tail).length + 1 ≤ n := hlen
          have hrotate : LowerExtractionPath n hn (lowerDelete c a) [] d 1 := .rotate _
          have hrestValid := (hdelete.trans hrotate).valid hvalid
          have hrestPacked : ∀ i (hi : i < (b :: tail).length),
              d (b :: tail)[i] = some (sweepSite n hn ⟨i, by omega⟩) := by
            intro i hi
            have hnot : (b :: tail)[i] ≠ a := by
              intro he
              exact (List.nodup_cons.mp hnodup).1
                (he ▸ List.getElem_mem hi)
            have hp := packed (i + 1) (Nat.succ_lt_succ hi)
            simp only [List.getElem_cons_succ] at hp
            simp only [d, lowerRotate, lowerDelete, if_neg hnot, hp, Option.map_some]
            congr 1
            apply Fin.ext
            rw [next_val]
            simp only [sweepSite, Nat.add_eq_zero_iff, Nat.one_ne_zero,
              and_false, if_false]
            by_cases hi0 : i = 0
            · subst i
              simp [show n - 1 + 1 = n by omega]
            · have hs : n - (i + 1) + 1 = n - i := by omega
              have hlt : n - i < n := by omega
              simp [hi0, hs, Nat.mod_eq_of_lt hlt]
          obtain ⟨e, htail⟩ := ih hrestValid (List.nodup_cons.mp hnodup).2
            (by simp at hlen ⊢; omega) hrestPacked
          refine ⟨e, ?_⟩
          have hcost : 0 + 1 + ((b :: tail).length - 1) = (a :: b :: tail).length - 1 := by
            simp
            omega
          simpa only [List.append_nil, List.singleton_append, hcost] using
            (hdelete.trans hrotate).trans htail

/-- The atom at extraction index `i` in the cyclic descending order
`a, a-1, ..., 0, n-1, ..., a+1`. -/
def firstAtomDescending (n : Nat) (hn : 1 < n) (a i : Fin n) : Fin n :=
  ⟨if i.val ≤ a.val then a.val - i.val else a.val + n - i.val, by
    by_cases h : i.val ≤ a.val
    · simp [h]
      exact Nat.lt_of_le_of_lt (Nat.sub_le _ _) a.isLt
    · simp [h]
      omega⟩

def firstAtomDescendingOrder (n : Nat) (hn : 1 < n) (a : Fin n) : List (Fin n) :=
  List.ofFn (firstAtomDescending n hn a)

@[simp] theorem firstAtomDescendingOrder_length (n : Nat) (hn : 1 < n)
    (a : Fin n) : (firstAtomDescendingOrder n hn a).length = n := by
  simp [firstAtomDescendingOrder]

theorem firstAtomDescendingOrder_nodup (n : Nat) (hn : 1 < n) (a : Fin n) :
    (firstAtomDescendingOrder n hn a).Nodup := by
  have hinj : Function.Injective (firstAtomDescending n hn a) := by
    intro i j he
    apply Fin.ext
    have hv := congrArg Fin.val he
    dsimp [firstAtomDescending] at hv
    by_cases hi : i.val ≤ a.val <;> by_cases hj : j.val ≤ a.val
    · simp [hi, hj] at hv
      omega
    · simp [hi, hj] at hv
      omega
    · simp [hi, hj] at hv
      omega
    · simp [hi, hj] at hv
      omega
  rw [firstAtomDescendingOrder, List.ofFn_eq_map]
  exact (List.nodup_finRange n).map hinj

private theorem firstAtomDescending_rotated_to_sweep
    {n : Nat} {hn : 1 < n} (a : Fin n) (i : Fin n) :
    nextMany n (by omega) (firstAtomDescending n hn a i)
      ((n - a.val) % n) = sweepSite n hn i := by
  apply Fin.ext
  rw [nextMany_val]
  by_cases ha0 : a.val = 0
  · by_cases hi0 : i.val = 0
    · simp [firstAtomDescending, ha0, hi0, sweepSite]
    · have hi : 0 < i.val := by omega
      have hlt : n - i.val < n := by omega
      simp [firstAtomDescending, ha0, hi0, sweepSite,
        Nat.mod_eq_of_lt hlt]
  · have ha : 0 < a.val := by omega
    have hrho : (n - a.val) % n = n - a.val :=
      Nat.mod_eq_of_lt (by omega)
    rw [hrho]
    by_cases hi0 : i.val = 0
    · simp [firstAtomDescending, hi0, sweepSite, Nat.mod_eq_of_lt (by omega)]
    · have hi : 0 < i.val := by omega
      by_cases hia : i.val ≤ a.val
      · have hsum : (a.val - i.val) + (n - a.val) = n - i.val := by omega
        have hlt : n - i.val < n := by omega
        simp [firstAtomDescending, hi0, hia, hsum, sweepSite,
          Nat.mod_eq_of_lt hlt]
      · have hsum : (a.val + n - i.val) + (n - a.val) = n + (n - i.val) := by
          omega
        have hlt : n - i.val < n := by omega
        simp [firstAtomDescending, hi0, hia, hsum, sweepSite,
          Nat.add_mod, Nat.mod_eq_of_lt hlt]

/-- A descending sweep after the least number of rotations to bring its
first requested atom to the port attains the first-element lower bound. -/
theorem firstAtomDescendingPath (n : Nat) (hn : 1 < n) (a : Fin n) :
    LowerExtractionPath n hn (lowerExtractionSeed n)
      (firstAtomDescendingOrder n hn a) (lowerExtractionEmpty n)
      ((n - a.val) % n + (n - 1)) := by
  let z := firstAtomDescendingOrder n hn a
  let rho := (n - a.val) % n
  let c := lowerRotateMany n hn (lowerExtractionSeed n) rho
  have hzlen : z.length = n := by
    dsimp [z]
    exact firstAtomDescendingOrder_length n hn a
  have znodup : z.Nodup := by
    dsimp [z]
    exact firstAtomDescendingOrder_nodup n hn a
  have hpre : LowerExtractionPath n hn (lowerExtractionSeed n) [] c rho :=
    lowerRotateMany_path _ _
  have hpacked : ∀ i (hi : i < z.length),
      c z[i] = some (sweepSite n hn ⟨i, by omega⟩) := by
    intro i hi
    have hin : i < n := by omega
    have hc : c z[i] = some (nextMany n (by omega) (z[i]) rho) := by
      exact lowerRotateMany_apply (lowerExtractionSeed n) rho (z[i]) (z[i]) rfl
    have hzi : z[i] = firstAtomDescending n hn a ⟨i, hin⟩ := by
      dsimp [z, firstAtomDescendingOrder]
      have hidx : i < (List.ofFn (firstAtomDescending n hn a)).length := by
        simpa using hin
      exact List.getElem_ofFn hidx
    have hsweep := firstAtomDescending_rotated_to_sweep (hn := hn) a ⟨i, hin⟩
    rw [hzi] at hc
    rw [hzi]
    exact hc.trans (congrArg some hsweep)
  obtain ⟨d, hrest⟩ := sweep_path
    (hpre.valid (lowerExtractionSeed_valid n))
    znodup
    (by omega) hpacked
  have hcover : ∀ b, b ∈ z := by
    intro b
    have hset : z.toFinset = Finset.univ := by
      apply (Finset.card_eq_iff_eq_univ _).mp
      rw [List.toFinset_card_of_nodup znodup, hzlen]
      simp
    have hb : b ∈ z.toFinset := by simp [hset]
    simpa using hb
  have hempty := hrest.terminal_empty hcover
  have hcost : rho + (z.length - 1) = rho + (n - 1) := by simp [z]
  have hwhole := hpre.trans hrest
  rw [hempty] at hwhole
  simpa [z, hcost] using hwhole

/-- Every first-element bound is attained by the cyclic descending order. -/
theorem firstAtomDescendingCost_exact (n : Nat) (hn : 1 < n) (a : Fin n) :
    lowerExtractionCost n hn (firstAtomDescendingOrder n hn a) =
      (n - a.val) % n + (n - 1) := by
  apply Nat.le_antisymm
  · exact lowerExtractionCost_le (firstAtomDescendingPath n hn a)
  · have hsize : n - 1 + 1 = n := by omega
    let rest : List (Fin n) := List.ofFn (fun i : Fin (n - 1) =>
      firstAtomDescending n hn a (Fin.cast hsize i.succ))
    have hdecomp : firstAtomDescendingOrder n hn a = a :: rest := by
      dsimp [firstAtomDescendingOrder]
      rw [List.ofFn_congr (h := hsize.symm) (f := firstAtomDescending n hn a)]
      rw [List.ofFn_succ]
      simp [rest, firstAtomDescending, Fin.cast_mk]
    have hlen : (a :: rest).length = n := by
      rw [← hdecomp]
      exact firstAtomDescendingOrder_length n hn a
    have hnodup : (a :: rest).Nodup := by
      rw [← hdecomp]
      exact firstAtomDescendingOrder_nodup n hn a
    rw [hdecomp]
    exact lowerExtractionCost_first_atom_lower_bound
      (hn := hn) (a := a) hlen hnodup

/-- An actual legal auxiliary path of cost 2n-2 for the reverse order. -/
theorem reverseExtractionPath (n : Nat) (hn : 1 < n) :
    LowerExtractionPath n hn (lowerExtractionSeed n) (reverseExtractionOrder n hn)
      (lowerExtractionEmpty n) (2 * n - 2) := by
  let c := lowerRotateMany n hn (lowerExtractionSeed n) (n - 1)
  have hpre : LowerExtractionPath n hn (lowerExtractionSeed n) [] c (n - 1) :=
    lowerRotateMany_path _ _
  have hpacked : ∀ i (hi : i < (reverseExtractionOrder n hn).length),
      c (reverseExtractionOrder n hn)[i] = some (sweepSite n hn ⟨i, by simpa using hi⟩) := by
    intro i hi
    have hin : i < n := by simpa using hi
    simp only [reverseExtractionOrder, List.getElem_ofFn]
    rw [show c (reverseExtractionAtom n hn ⟨i, hin⟩) =
      some (nextMany n (by omega) (reverseExtractionAtom n hn ⟨i, hin⟩) (n - 1)) from
        lowerRotateMany_apply _ _ _ _ rfl]
    congr 1
    apply Fin.ext
    rw [nextMany_val]
    simp only [reverseExtractionAtom, sweepSite]
    by_cases hi0 : i = 0
    · subst i
      simp [show 1 + (n - 1) = n by omega]
    · by_cases hi1 : i = 1
      · subst i
        simp [Nat.mod_eq_of_lt (show n - 1 < n by omega)]
      · have hs : n + 1 - i + (n - 1) = n + (n - i) := by omega
        have hlt : n - i < n := by omega
        simp [hi0, hi1, hs, Nat.mod_eq_of_lt hlt]
  obtain ⟨d, hrest⟩ := sweep_path (hpre.valid (lowerExtractionSeed_valid n))
    (reverseExtractionOrder_nodup n hn) (by simp) hpacked
  have hcover : ∀ a, a ∈ reverseExtractionOrder n hn := by
    have hset : (reverseExtractionOrder n hn).toFinset = Finset.univ := by
      apply (Finset.card_eq_iff_eq_univ _).mp
      rw [List.toFinset_card_of_nodup (reverseExtractionOrder_nodup n hn)]
      simp
    intro a
    have hm : a ∈ (reverseExtractionOrder n hn).toFinset := by simp [hset]
    simpa using hm
  have hempty := hrest.terminal_empty hcover
  have hcost : n - 1 + ((reverseExtractionOrder n hn).length - 1) = 2 * n - 2 := by
    simp
    omega
  simpa only [List.nil_append, hempty, hcost] using hpre.trans hrest

/-- The reverse-order value is proved inside the auxiliary model, with no
Python optimizer or physical delayed-chain existence premise. -/
theorem reverseExtractionCost_exact (n : Nat) (hn : 1 < n) :
    lowerExtractionCost n hn (reverseExtractionOrder n hn) = 2 * n - 2 := by
  apply Nat.le_antisymm (lowerExtractionCost_le (reverseExtractionPath n hn))
  have path := lowerExtractionCost_attained_of_permutation (hn := hn)
    (reverseExtractionOrder_length n hn) (reverseExtractionOrder_nodup n hn)
  have hfirst : (reverseExtractionOrder n hn)[0]'(by simp; omega) = site1 n hn := by
    apply Fin.ext
    simp [reverseExtractionOrder, reverseExtractionAtom, site1]
  cases hz : reverseExtractionOrder n hn with
  | nil => have := reverseExtractionOrder_length n hn; rw [hz] at this; simp at this; omega
  | cons a rest =>
      have ha : a = site1 n hn := by simpa [hz] using hfirst
      subst a
      have hpath : LowerExtractionPath n hn (lowerExtractionSeed n)
          (site1 n hn :: rest) (lowerExtractionEmpty n) (lowerExtractionCost n hn (site1 n hn :: rest)) := by
        simpa [hz] using path
      have hbound := hpath.first_atom_cost_lower_bound
      have hrho : (n - (site1 n hn).val) % n = n - 1 := by
        simp [site1]
      rw [hrho] at hbound
      have hlen := reverseExtractionOrder_length n hn
      rw [hz] at hlen
      simp only [List.length_cons] at hlen
      omega

end RSR2History
