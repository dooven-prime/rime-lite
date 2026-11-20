import RSR2History.PortFacingExtraction

/-!
An explicit quadratic extraction family, without a finite optimizer.
Delete the second live atom and continue from its successor.  The physical
port-list projection forces fresh preparation debts r-1 at remaining
sizes r = n, n-1, ..., 2. Legal nonfusion slides are fully allowed.
-/

namespace RSR2History
open RSR2.Parametric

/-- Step-two Josephus deletion order, based at the current port-facing
linear list. This is a computable permutation of the input list. -/
def secondLiveOrder {α : Type*} : List α → List α
  | [] => []
  | [a] => [a]
  | a :: b :: tail => b :: secondLiveOrder (tail ++ [a])
termination_by xs => xs.length
decreasing_by simp

theorem secondLiveOrder_perm {α : Type*} (xs : List α) :
    (secondLiveOrder xs).Perm xs := by
  fun_induction secondLiveOrder xs with
  | case1 => exact .refl _
  | case2 a => exact .refl _
  | case3 a b tail ih =>
      exact (List.Perm.cons b ih).trans
        (List.isRotated_concat a (b :: tail)).perm

@[simp] theorem secondLiveOrder_length {α : Type*} (xs : List α) :
    (secondLiveOrder xs).length = xs.length := (secondLiveOrder_perm xs).length_eq

theorem secondLiveOrder_nodup {α : Type*} {xs : List α} (h : xs.Nodup) :
    (secondLiveOrder xs).Nodup := (secondLiveOrder_perm xs).nodup_iff.mpr h

/-- All real extraction paths for the Josephus order pay a triangular
preparation cost. The statement is doubled to avoid parity premises. -/
theorem LowerExtractionPath.secondLive_cost_lower_bound
    {n : Nat} {hn : 1 < n} {xs : List (Fin n)}
    {c d : LowerConfiguration n} {k : Nat}
    (path : LowerExtractionPath n hn c (secondLiveOrder xs) d k)
    (horder : portFacingPackets c = xs.map (fun a => ({a} : Finset (Fin n))))
    (hnd : xs.Nodup) : xs.length * (xs.length - 1) ≤ 2 * k := by
  induction hlen : xs.length using Nat.strong_induction_on generalizing xs c d k with
  | h r ih =>
      cases xs with
      | nil =>
          have hr : r = 0 := by simpa using hlen.symm
          simp [hr]
      | cons x rest =>
        cases rest with
        | nil => simp_all
        | cons y tail =>
          obtain ⟨before, p, q, hpre, hat, hsingle, htail, hcost⟩ :=
            path.first_delete (by rw [secondLiveOrder])
          obtain ⟨hp, hnext⟩ := hpre.second_live_deletion horder hnd hat hsingle
          have hndnext : (tail ++ [x]).Nodup := by
            have hrot := (List.isRotated_concat x (y :: tail)).symm
            have h := hrot.nodup_iff.mp hnd
            exact (List.nodup_cons.mp h).2
          have hsub : (tail ++ [x]).length < r := by simp_all; omega
          have hi' := ih (tail ++ [x]).length hsub htail hnext hndnext rfl
          have hi : (tail.length + 1) * tail.length ≤ 2 * q := by simpa using hi'
          have hr : r = tail.length + 2 := by simpa using hlen.symm
          rw [hr]
          have ht' : tail.length + 2 - 1 = tail.length + 1 := by omega
          rw [ht']
          nlinarith

def josephusExtractionOrder (n : Nat) : List (Fin n) :=
  secondLiveOrder (List.finRange n)

@[simp] theorem josephusExtractionOrder_length (n : Nat) :
    (josephusExtractionOrder n).length = n := by simp [josephusExtractionOrder]

theorem josephusExtractionOrder_nodup (n : Nat) :
    (josephusExtractionOrder n).Nodup :=
  secondLiveOrder_nodup (List.nodup_finRange n)

/-- A uniform quadratic lower bound for an explicit full permutation.
This is not an assertion that this family maximizes extraction cost. -/
theorem josephusExtractionCost_lower_bound (n : Nat) (hn : 1 < n) :
    n * (n - 1) ≤ 2 * lowerExtractionCost n hn (josephusExtractionOrder n) := by
  have path := lowerExtractionCost_attained_of_permutation
    (hn := hn) (josephusExtractionOrder_length n) (josephusExtractionOrder_nodup n)
  have h := path.secondLive_cost_lower_bound (portFacingPackets_seed n)
    (List.nodup_finRange n)
  simpa using h

end RSR2History
