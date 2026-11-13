import Mathlib

/-!
# Continuants and Fibonacci envelopes

The geometric interpretation of a run list as a reduced Farey flag path is
outside this module. Once that interpretation is supplied, this module proves
the all-parameter arithmetic envelope used by Paper XXII, Lemma 5.1.
-/

namespace Rime.Paper22

/-- Continuant with the convention `K([])=1`, `K([q])=q`. -/
def continuant : List Nat → Nat
  | [] => 1
  | [q] => q
  | q :: r :: tail => q * continuant (r :: tail) + continuant tail

private theorem fib_run_bound (m q : Nat) :
    q * Nat.fib (m + 1) + Nat.fib m ≤ Nat.fib (m + q + 1) := by
  induction q with
  | zero =>
      simpa [Nat.add_comm] using (Nat.fib_le_fib_succ (n := m))
  | succ q ih =>
      cases q with
      | zero =>
          simp [Nat.fib_add_two, Nat.add_comm, Nat.add_left_comm]
      | succ q =>
          have hmono' : Nat.fib (m + 1) ≤ Nat.fib (m + q + 1) := by
            exact Nat.fib_mono (by omega)
          have hrec : Nat.fib (m + q + 3) =
              Nat.fib (m + q + 2) + Nat.fib (m + q + 1) := by
            calc
              Nat.fib (m + q + 3) =
                  Nat.fib ((m + q + 1) + 2) := by congr 1
              _ = Nat.fib (m + q + 1) +
                  Nat.fib ((m + q + 1) + 1) := Nat.fib_add_two
              _ = Nat.fib (m + q + 2) + Nat.fib (m + q + 1) := by
                rw [show (m + q + 1) + 1 = m + q + 2 by omega,
                  Nat.add_comm]
          calc
            (q + 2) * Nat.fib (m + 1) + Nat.fib m
                = ((q + 1) * Nat.fib (m + 1) + Nat.fib m) +
                    Nat.fib (m + 1) := by ring
            _ ≤ Nat.fib (m + q + 2) + Nat.fib (m + q + 1) :=
              Nat.add_le_add ih hmono'
            _ = Nat.fib (m + q + 3) := hrec.symm

private theorem fib_mono_nat : Monotone Nat.fib := by
  intro a b hab
  exact Nat.fib_mono hab

/-- The all-parameter arithmetic estimate for the continuant recurrence. -/
theorem continuant_le_fib (runs : List Nat)
    (hpos : ∀ q ∈ runs, 0 < q) :
    continuant runs ≤ Nat.fib (runs.sum + 1) := by
  have aux : ∀ n (xs : List Nat), xs.length = n →
      (∀ q ∈ xs, 0 < q) → continuant xs ≤ Nat.fib (xs.sum + 1) := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n ih =>
        intro xs hlen hpos
        cases xs with
        | nil => simp [continuant]
        | cons q rest =>
            cases rest with
            | nil =>
                simpa [continuant, List.sum] using fib_run_bound 0 q
            | cons r tail =>
                have hqr : 0 < q := hpos q (by simp)
                have hrr : 0 < r := hpos r (by simp)
                have hrest : ∀ z ∈ r :: tail, 0 < z := by
                  intro z hz
                  exact hpos z (List.mem_cons_of_mem q hz)
                have htail : ∀ z ∈ tail, 0 < z := by
                  intro z hz
                  exact hpos z (List.mem_cons_of_mem q (List.mem_cons_of_mem r hz))
                have hlen' : tail.length + 2 = n := by
                  simpa [List.length_cons, Nat.add_assoc] using hlen
                have hn₁ : (r :: tail).length < n := by
                  rw [List.length_cons]
                  omega
                have hn₂ : tail.length < n := by omega
                have h₁ := ih (r :: tail).length hn₁ (r :: tail) rfl hrest
                have h₂ := ih tail.length hn₂ tail rfl htail
                have hindex : tail.sum + 1 ≤ (r :: tail).sum := by
                  simp [List.sum_cons]
                  omega
                have hsmall : Nat.fib (tail.sum + 1) ≤ Nat.fib ((r :: tail).sum) :=
                  fib_mono_nat hindex
                have hmain := fib_run_bound (r :: tail).sum q
                calc
                  continuant (q :: r :: tail)
                      = q * continuant (r :: tail) + continuant tail := rfl
                  _ ≤ q * Nat.fib ((r :: tail).sum + 1) +
                      Nat.fib ((r :: tail).sum) := by
                        exact Nat.add_le_add
                          (Nat.mul_le_mul_left q h₁)
                          (h₂.trans hsmall)
                  _ ≤ Nat.fib ((r :: tail).sum + q + 1) := by
                        simpa [Nat.add_assoc, Nat.add_left_comm,
                          Nat.add_comm] using hmain
                  _ = Nat.fib ((q :: r :: tail).sum + 1) := by
                        simp [List.sum_cons, Nat.add_assoc, Nat.add_comm]
  exact aux runs.length runs rfl hpos

end Rime.Paper22
