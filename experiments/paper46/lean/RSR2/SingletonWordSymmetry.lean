import RSR2.PortCostSharpness

/-!
# Symmetry of shortest singleton witnesses

The lower and upper rotations act on disjoint layers, so their physical
actions commute. This gives a family of distinct raw words with the same
singleton endpoint; it does not assert that these are all optimal words.
-/

namespace RSR2.Parametric

theorem rotate_lower_upper_commute (n : Nat) (hn : 0 < n) (P : Placement n) :
    rotate n hn (rotate n hn P false) true =
      rotate n hn (rotate n hn P true) false := by
  funext a
  rcases h : P a with ⟨layer, q⟩
  cases layer <;> simp [rotate, h]

def singletonRound (swap : Bool) : List Letter :=
  if swap then [.p true, .p false, .v] else [.p false, .p true, .v]

def singletonVariantWord : List Bool → List Letter
  | [] => [.v]
  | b :: bs => singletonVariantWord bs ++ singletonRound b

theorem singletonRound_run_eq (n : Nat) (hn : 1 < n)
    (P : Placement n) (swap : Bool) :
    run n hn P (singletonRound swap) =
      run n hn P [.p false, .p true, .v] := by
  cases swap with
  | false => rfl
  | true =>
      simp only [singletonRound, ite_true, run, step_p, Option.bind_some]
      rw [rotate_lower_upper_commute]

theorem singletonVariantWord_run_eq_prefix (n : Nat) (hn : 1 < n)
    (P : Placement n) (bits : List Bool) :
    run n hn P (singletonVariantWord bits) =
      run n hn P (singletonTransferPrefix bits.length) := by
  induction bits generalizing P with
  | nil => rfl
  | cons b bs ih =>
      simp only [singletonVariantWord, singletonTransferPrefix, List.length_cons,
        run_append]
      rw [ih]
      cases hrun : run n hn P (singletonTransferPrefix bs.length) with
      | none => simp
      | some P' => simp [singletonRound_run_eq]

theorem singletonRound_length (swap : Bool) :
    (singletonRound swap).length = 3 := by
  cases swap <;> simp [singletonRound]

theorem singletonVariantWord_length (bits : List Bool) :
    (singletonVariantWord bits).length = 3 * bits.length + 1 := by
  induction bits with
  | nil => simp [singletonVariantWord]
  | cons b bs ih =>
      simp only [singletonVariantWord, List.length_append, singletonRound_length,
        List.length_cons, ih]
      omega

theorem singletonVariantWord_head_swap_ne (tail : List Bool) :
    singletonVariantWord (true :: tail) ≠ singletonVariantWord (false :: tail) := by
  intro h
  have hd := congrArg (List.drop (singletonVariantWord tail).length) h
  have hr : singletonRound true = singletonRound false := by
    simpa [singletonVariantWord, List.drop_append] using hd
  simp [singletonRound] at hr

theorem singletonVariantWord_injective_of_length :
    ∀ {xs ys : List Bool}, xs.length = ys.length →
      singletonVariantWord xs = singletonVariantWord ys → xs = ys
  | [], [], _, _ => rfl
  | [], _ :: _, hlen, _ => by simp at hlen
  | _ :: _, [], hlen, _ => by simp at hlen
  | b :: bs, c :: cs, hlen, heq => by
      have hbslen0 : bs.length = cs.length := by
        simp only [List.length_cons] at hlen
        omega
      have hbslen : (singletonVariantWord bs).length =
          (singletonVariantWord cs).length := by
        simp [singletonVariantWord_length, hbslen0]
      have hprefix := congrArg (List.take (singletonVariantWord bs).length) heq
      have hbs : singletonVariantWord bs = singletonVariantWord cs := by
        simpa [singletonVariantWord, List.take_append, hbslen] using hprefix
      have hdrop := congrArg (List.drop (singletonVariantWord bs).length) heq
      have hround : singletonRound b = singletonRound c := by
        simpa [singletonVariantWord, List.drop_append, hbs, hbslen] using hdrop
      have hbc : b = c := by
        cases b <;> cases c <;> simp [singletonRound] at hround ⊢
      have htail : bs = cs := singletonVariantWord_injective_of_length hbslen0 hbs
      simp [hbc, htail]

theorem singletonVariantWord_run (n : Nat) (hn : 1 < n)
    (bits : List Bool) (hbits : bits.length = n - 1) :
    run n hn (seed n) (singletonVariantWord bits) =
      some (upperSingletonEndpoint n (by omega)) := by
  rw [singletonVariantWord_run_eq_prefix]
  have hlen : bits.length < n := by omega
  rw [singletonTransferPrefix_run n hn bits.length hlen]
  simp only [Option.some.injEq]
  funext a
  by_cases hz : a.val = 0
  · simp [singletonTransferStage, upperSingletonEndpoint, hz, hbits]
  · have hw : n ≤ a.val + bits.length := by omega
    simp [singletonTransferStage, upperSingletonEndpoint, hz, hw]
    omega

def singletonCanonicalBits (n : Nat) : List Bool := List.replicate (n - 1) false

def singletonOneSwapBits (n : Nat) : List Bool :=
  true :: List.replicate (n - 2) false

theorem singleton_two_distinct_optimal_witnesses (n : Nat) (hn : 1 < n) :
    run n hn (seed n) (singletonVariantWord (singletonCanonicalBits n)) =
        some (upperSingletonEndpoint n (by omega)) ∧
      run n hn (seed n) (singletonVariantWord (singletonOneSwapBits n)) =
        some (upperSingletonEndpoint n (by omega)) ∧
      (singletonVariantWord (singletonCanonicalBits n)).length = 3 * n - 2 ∧
      (singletonVariantWord (singletonOneSwapBits n)).length = 3 * n - 2 ∧
      singletonVariantWord (singletonCanonicalBits n) ≠
        singletonVariantWord (singletonOneSwapBits n) := by
  have hcanon : (singletonCanonicalBits n).length = n - 1 := by
    simp [singletonCanonicalBits]
  have hswap : (singletonOneSwapBits n).length = n - 1 := by
    simp [singletonOneSwapBits]
    omega
  have hrunCanon := singletonVariantWord_run n hn _ hcanon
  have hrunSwap := singletonVariantWord_run n hn _ hswap
  have hlenCanon := singletonVariantWord_length (singletonCanonicalBits n)
  have hlenSwap := singletonVariantWord_length (singletonOneSwapBits n)
  have hne : singletonVariantWord (singletonOneSwapBits n) ≠
      singletonVariantWord (singletonCanonicalBits n) := by
    have hrep : List.replicate (n - 1) false =
        false :: List.replicate (n - 2) false := by
      rw [show n - 1 = (n - 2) + 1 by omega]
      simp [List.replicate_succ]
    rw [singletonOneSwapBits, singletonCanonicalBits, hrep]
    exact singletonVariantWord_head_swap_ne (List.replicate (n - 2) false)
  refine ⟨hrunCanon, hrunSwap, ?_, ?_, ?_⟩
  · omega
  · omega
  · intro heq
    exact hne heq.symm

end RSR2.Parametric
