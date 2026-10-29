import RegisteredAbsorptionChains.CrossNextBlock
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- An actual placed atom partition with named blocks in positive cyclic order.
The positive distances are order witnesses, not inferred from mere injectivity. -/
structure NamedCyclicPlacement (n r : ℕ) (α : Type*) [NeZero n] [NeZero r] where
  placed : Placement n (Finset α)
  position : ZMod r → ZMod n
  block : ZMod r → Finset α
  position_injective : Function.Injective position
  placed_at : ∀ i, placed (position i) = some (block i)
  only_named : ∀ q, placed q ≠ none → ∃ i, position i = q
  block_nonempty : ∀ i, (block i).Nonempty
  block_disjoint : ∀ i j, i ≠ j → Disjoint (block i) (block j)
  atom_covered : ∀ a : α, ∃ i, a ∈ block i
  forward_order : ∃ delta : ZMod r → ℕ,
    (∀ i, 0 < delta i) ∧
    (∑ i : ZMod r, delta i) = n ∧
    ∀ i, position (i + 1) = position i + (delta i : ZMod n)

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r]

/-- The forward distances yield holes between consecutive named blocks. -/
noncomputable def NamedCyclicPlacement.toGapFrame
    (named : NamedCyclicPlacement n r α) : GapFrame n r α := by
  classical
  let delta := Classical.choose named.forward_order
  let positive := (Classical.choose_spec named.forward_order).1
  let total := (Classical.choose_spec named.forward_order).2.1
  let next := (Classical.choose_spec named.forward_order).2.2
  have hrn : r ≤ n := by
    have h := Fintype.card_le_of_injective named.position named.position_injective
    simpa using h
  have hsum : (∑ i : ZMod r, (delta i - 1)) = n - r := by
    have heach (i : ZMod r) : delta i - 1 + 1 = delta i := by
      exact Nat.sub_add_cancel (Nat.succ_le_iff.mpr (positive i))
    have htotal : (∑ i : ZMod r, (delta i - 1)) + r = n := by
      calc
        (∑ i : ZMod r, (delta i - 1)) + r =
            ∑ i : ZMod r, ((delta i - 1) + 1) := by simp [Finset.sum_add_distrib]
        _ = ∑ i : ZMod r, delta i := by
          apply Finset.sum_congr rfl
          intro i _
          exact heach i
        _ = n := total
    omega
  refine
    { position := named.position
      block := named.block
      gap := fun i => delta i - 1
      anchor := named.position 0
      anchor_eq := rfl
      next_eq := ?_
      position_injective := named.position_injective
      gap_total := hsum }
  intro i
  have heach : delta i - 1 + 1 = delta i := by
    exact Nat.sub_add_cancel (Nat.succ_le_iff.mpr (positive i))
  have hcast : (delta i : ZMod n) = 1 + ((delta i - 1 : ℕ) : ZMod n) := by
    have h := congrArg (fun t : ℕ => (t : ZMod n)) heach
    simp only [Nat.cast_add, Nat.cast_one] at h
    rw [← h]
    abel
  rw [next i, hcast]
  abel

@[simp] theorem NamedCyclicPlacement.toGapFrame_position
    (named : NamedCyclicPlacement n r α) :
    named.toGapFrame.position = named.position := by
  unfold NamedCyclicPlacement.toGapFrame
  rfl

@[simp] theorem NamedCyclicPlacement.toGapFrame_block
    (named : NamedCyclicPlacement n r α) :
    named.toGapFrame.block = named.block := by
  unfold NamedCyclicPlacement.toGapFrame
  rfl

/-- Construction from an eligible named placement is an exact left inverse of decode. -/
theorem NamedCyclicPlacement.toGapFrame_decode
    (named : NamedCyclicPlacement n r α) :
    named.toGapFrame.decode = named.placed := by
  classical
  funext q
  by_cases h : ∃ i, named.position i = q
  · obtain ⟨i, hi⟩ := h
    subst q
    have hdecode : named.toGapFrame.decode (named.position i) =
        some (named.block i) := by
      simpa using named.toGapFrame.decode_at i
    exact hdecode.trans (named.placed_at i).symm
  · have hnone : named.placed q = none := by
      by_contra hc
      exact h (named.only_named q hc)
    have hdecode : named.toGapFrame.decode q = none := by
      apply named.toGapFrame.decode_empty
      intro i hi
      exact h ⟨i, by simpa using hi⟩
    rw [hdecode, hnone]

theorem exists_frame_of_named_cyclic_placement
    (named : NamedCyclicPlacement n r α) :
    ∃ frame : GapFrame n r α,
      frame.decode = named.placed ∧
      frame.position = named.position ∧ frame.block = named.block :=
  ⟨named.toGapFrame, named.toGapFrame_decode,
    named.toGapFrame_position, named.toGapFrame_block⟩

end RegisteredAbsorptionChains
