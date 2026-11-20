/-!
# RSR-2-B: all-parameter partition presentations and cost ledger

An `OrderedPartition n` is a finite set partition with an order chosen for
the blocks and for the atoms inside each block. Its flattening is therefore
a permutation of `List.finRange n`. This makes the combinatorial Bell target
explicit and provides the input to the permutation-loading construction.

The proofs below certify the all-parameter ordering facts and the raw-letter
budget arithmetic. The arbitrary-`n` guarded execution and exact canonical
endpoint are proved downstream in `RSR2.Executable` and
`RSR2.CanonicalEndpoint`; this module supplies their ordered-partition input
and cost ledger.
-/

namespace RSR2

structure OrderedPartition (n : Nat) where
  blocks : List (List (Fin n))
  nonempty : ∀ b, b ∈ blocks → b ≠ []
  flatten_perm : List.Perm blocks.flatten (List.finRange n)

def OrderedPartition.blockCount (p : OrderedPartition n) : Nat := p.blocks.length

def OrderedPartition.atomOrder (p : OrderedPartition n) : List (Fin n) := p.blocks.flatten

def sourceLoadingLetters (n : Nat) : Nat := n - 1 + 1

def permutationLoadingLetters (n : Nat) : Nat :=
  n * sourceLoadingLetters n + (n - 1)

def fusionCount (p : OrderedPartition n) : Nat := n - p.blockCount

def interleavedBellBudget (n b : Nat) : Nat :=
  permutationLoadingLetters n + (n - b)

theorem atomOrder_length (p : OrderedPartition n) :
    p.atomOrder.length = n := by
  simpa [OrderedPartition.atomOrder] using p.flatten_perm.length_eq

theorem blockCount_le_atomCount :
    ∀ (xs : List (List (Fin n))),
      (∀ b, b ∈ xs → b ≠ []) → xs.length ≤ xs.flatten.length
  | [], _ => by simp
  | b :: xs, h => by
      have hb : b ≠ [] := h b (by simp)
      have hxs : ∀ c, c ∈ xs → c ≠ [] := by
        intro c hc
        exact h c (by simp [hc])
      cases b with
      | nil => contradiction
      | cons x tail =>
          simp only [List.length_cons, List.flatten_cons, List.length_append]
          have ih := blockCount_le_atomCount xs hxs
          omega

theorem blockCount_le_n (p : OrderedPartition n) : p.blockCount ≤ n := by
  have hle := blockCount_le_atomCount p.blocks p.nonempty
  calc
    p.blockCount ≤ p.atomOrder.length := hle
    _ = n := atomOrder_length p

theorem fusionCount_eq (p : OrderedPartition n) :
    fusionCount p + p.blockCount = n := by
  have hb := blockCount_le_n p
  unfold fusionCount
  omega

theorem sourceLoadingLetters_eq (n : Nat) (hn : 0 < n) :
    sourceLoadingLetters n = n := by
  unfold sourceLoadingLetters
  omega

theorem permutationLoadingLetters_eq (n : Nat) (hn : 0 < n) :
    permutationLoadingLetters n = n * (n - 1) + n + (n - 1) := by
  unfold permutationLoadingLetters
  rw [sourceLoadingLetters_eq n hn]
  have hmul : n * (n - 1) + n = n * n := by
    calc
      n * (n - 1) + n = n * (n - 1) + n * 1 := by simp
      _ = n * ((n - 1) + 1) := by rw [Nat.mul_add]
      _ = n * n := by congr 1 <;> omega
  rw [← hmul]

theorem bell_budget_eq (p : OrderedPartition n) :
    interleavedBellBudget n p.blockCount =
      permutationLoadingLetters n + fusionCount p := by
  rfl

theorem bell_uniform_budget (n b : Nat) (hb : 1 ≤ b) :
    interleavedBellBudget n b ≤ permutationLoadingLetters n + (n - 1) := by
  unfold interleavedBellBudget
  apply Nat.add_le_add_left
  exact Nat.sub_le_sub_left hb n

theorem blockCount_positive (p : OrderedPartition n) (hn : 0 < n) :
    1 ≤ p.blockCount := by
  cases hblocks : p.blocks with
  | nil =>
      have hlen := atomOrder_length p
      simp [OrderedPartition.atomOrder, hblocks] at hlen
      omega
  | cons b rest => simp [OrderedPartition.blockCount, hblocks]

theorem bell_plan_uniform_budget (p : OrderedPartition n) (hn : 0 < n) :
    interleavedBellBudget n p.blockCount ≤ permutationLoadingLetters n + (n - 1) := by
  exact bell_uniform_budget n p.blockCount (blockCount_positive p hn)

theorem orderedPresentation (n : Nat) (blocks : List (List (Fin n)))
    (hperm : List.Perm blocks.flatten (List.finRange n))
    (hnonempty : ∀ b, b ∈ blocks → b ≠ []) :
    Nonempty (OrderedPartition n) :=
  ⟨⟨blocks, hnonempty, hperm⟩⟩

end RSR2
