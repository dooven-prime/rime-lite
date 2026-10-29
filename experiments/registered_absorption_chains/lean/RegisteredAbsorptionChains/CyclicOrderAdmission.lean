import RegisteredAbsorptionChains.PhaseAlignment
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- The partition and its common block names are data; orientation is stated
separately, so position injectivity alone never supplies cyclic order. -/
structure LegalNamedPlacement (n r : ℕ) (α : Type*) [NeZero n] [NeZero r] where
  placed : Placement n (Finset α)
  position : ZMod r → ZMod n
  block : ZMod r → Finset α
  position_injective : Function.Injective position
  placed_at : ∀ i, placed (position i) = some (block i)
  only_named : ∀ q, placed q ≠ none → ∃ i, position i = q
  block_nonempty : ∀ i, (block i).Nonempty
  block_disjoint : ∀ i j, i ≠ j → Disjoint (block i) (block j)
  atom_covered : ∀ a : α, ∃ i, a ∈ block i

variable {n r : ℕ} {α : Type*} [NeZero n] [NeZero r]

/-- Canonical integer lift of a block coordinate relative to named block zero.
The endpoint at `r` is the completed turn, not another coordinate. -/
def LegalNamedPlacement.offset (named : LegalNamedPlacement n r α) (k : ℕ) : ℕ :=
  if k < r then (named.position (k : ZMod r) - named.position 0).val else n

/-- Exact positive orientation of the supplied naming around the circle. -/
def LegalNamedPlacement.PositivelyOrdered
    (named : LegalNamedPlacement n r α) : Prop :=
  ∀ k : ℕ, k < r → named.offset k < named.offset (k + 1)

theorem LegalNamedPlacement.offset_zero (named : LegalNamedPlacement n r α) :
    named.offset 0 = 0 := by
  have hr : 0 < r := Nat.pos_of_ne_zero (NeZero.ne r)
  simp [LegalNamedPlacement.offset, hr]

theorem LegalNamedPlacement.offset_end (named : LegalNamedPlacement n r α) :
    named.offset r = n := by
  simp [LegalNamedPlacement.offset]

theorem LegalNamedPlacement.position_offset (named : LegalNamedPlacement n r α)
    (k : ℕ) (hk : k < r) :
    named.position (k : ZMod r) =
      named.position 0 + (named.offset k : ZMod n) := by
  have hcast := ZMod.natCast_zmod_val
    (named.position (k : ZMod r) - named.position 0)
  simp only [LegalNamedPlacement.offset, if_pos hk]
  rw [hcast]
  abel

private theorem sum_step_differences (t : ℕ → ℕ) (m : ℕ)
    (mono : ∀ k < m, t k < t (k + 1)) :
    (∑ k ∈ Finset.range m, (t (k + 1) - t k)) + t 0 = t m := by
  induction m with
  | zero => simp
  | succ m ih =>
      have hprev : ∀ k < m, t k < t (k + 1) := by
        intro k hk
        exact mono k (by omega)
      have hstep := mono m (by omega)
      rw [Finset.sum_range_succ]
      have hsum := ih hprev
      omega

private theorem finEquiv_val (j : Fin r) :
    (ZMod.finEquiv r j).val = j.val := by
  cases r with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ m =>
      cases j
      rfl

/-- The canonical lift produces positive one-step distances summing to a
single turn, including the final edge across residue zero. -/
theorem LegalNamedPlacement.forward_distances
    (named : LegalNamedPlacement n r α) (order : named.PositivelyOrdered) :
    ∃ delta : ZMod r → ℕ,
      (∀ i, 0 < delta i) ∧
      (∑ i : ZMod r, delta i) = n ∧
      ∀ i, named.position (i + 1) =
        named.position i + (delta i : ZMod n) := by
  let delta : ZMod r → ℕ :=
    fun i => named.offset (i.val + 1) - named.offset i.val
  have hpositive (i : ZMod r) : 0 < delta i := by
    dsimp [delta]
    have hi := ZMod.val_lt i
    have hstrict := order i.val hi
    omega
  have hsum : (∑ i : ZMod r, delta i) = n := by
    have hfin : (∑ i : ZMod r, delta i) =
        ∑ j : Fin r, delta (ZMod.finEquiv r j) := by
      symm
      exact Equiv.sum_comp (ZMod.finEquiv r).toEquiv delta
    rw [hfin]
    have hterms : (∑ j : Fin r, delta (ZMod.finEquiv r j)) =
        ∑ j : Fin r, (named.offset (j.val + 1) - named.offset j.val) := by
      apply Finset.sum_congr rfl
      intro j _
      simp [delta, finEquiv_val]
    rw [hterms, Fin.sum_univ_eq_sum_range
      (fun k : ℕ => named.offset (k + 1) - named.offset k)]
    have hterm : (∑ k ∈ Finset.range r,
        (named.offset (k + 1) - named.offset k)) + named.offset 0 =
        named.offset r := sum_step_differences named.offset r order
    simp only [delta, finEquiv_val] at *
    rw [named.offset_zero, named.offset_end] at hterm
    omega
  refine ⟨delta, hpositive, hsum, ?_⟩
  intro i
  let k := i.val
  have hk : k < r := ZMod.val_lt i
  have hnext : k + 1 ≤ r := by omega
  have hcurrent := named.position_offset k hk
  have hnext_position : named.position ((k + 1 : ℕ) : ZMod r) =
      named.position 0 + (named.offset (k + 1) : ZMod n) := by
    by_cases hlt : k + 1 < r
    · exact named.position_offset (k + 1) hlt
    · have heq : k + 1 = r := by omega
      rw [heq, ZMod.natCast_self, named.offset_end]
      simp
  have hdelta : named.offset k + delta i = named.offset (k + 1) := by
    have hstrict := order i.val (ZMod.val_lt i)
    change named.offset i.val +
      (named.offset (i.val + 1) - named.offset i.val) =
        named.offset (i.val + 1)
    omega
  have hcast := congrArg (fun t : ℕ => (t : ZMod n)) hdelta
  rw [show ((k + 1 : ℕ) : ZMod r) = i + 1 by
    rw [← ZMod.natCast_zmod_val i]
    push_cast
    rfl] at hnext_position
  rw [show (k : ZMod r) = i from ZMod.natCast_zmod_val i] at hcurrent
  rw [hcurrent, hnext_position]
  simp only [Nat.cast_add] at hcast
  rw [← hcast]
  abel

/-- Admission preserves the original partition data and adds the derived
positive-distance certificate required by `GapFrame`. -/
noncomputable def LegalNamedPlacement.admit
    (named : LegalNamedPlacement n r α) (order : named.PositivelyOrdered) :
    NamedCyclicPlacement n r α :=
  { placed := named.placed
    position := named.position
    block := named.block
    position_injective := named.position_injective
    placed_at := named.placed_at
    only_named := named.only_named
    block_nonempty := named.block_nonempty
    block_disjoint := named.block_disjoint
    atom_covered := named.atom_covered
    forward_order := named.forward_distances order }

/-- The two placements share the same named blocks, each in positive order. -/
def SameOrientedCyclicOrder (first second : LegalNamedPlacement n r α) : Prop :=
  first.block = second.block ∧
    first.PositivelyOrdered ∧ second.PositivelyOrdered

theorem admit_same_oriented_pair
    (first second : LegalNamedPlacement n r α)
    (same : SameOrientedCyclicOrder first second) :
    ∃ (a b : NamedCyclicPlacement n r α),
      a.placed = first.placed ∧ b.placed = second.placed ∧
      a.block = b.block := by
  rcases same with ⟨blocks, order₁, order₂⟩
  exact ⟨first.admit order₁, second.admit order₂, rfl, rfl, blocks⟩

/-- Paper-level premise on two raw placements: a common enumeration of the
same distinct atom blocks follows the positive oriented cycle in each. -/
def SameOrientedBlockCycle
    (first second : Placement n (Finset α)) : Prop :=
  ∃ (a b : LegalNamedPlacement n r α),
    a.placed = first ∧ b.placed = second ∧
    SameOrientedCyclicOrder a b

theorem admit_same_oriented_block_cycle
    (first second : Placement n (Finset α))
    (same : SameOrientedBlockCycle (r := r) first second) :
    ∃ (a b : NamedCyclicPlacement n r α),
      a.placed = first ∧ b.placed = second ∧ a.block = b.block := by
  obtain ⟨a, b, ha, hb, hsame⟩ := same
  obtain ⟨a', b', hfirst, hsecond, hblocks⟩ :=
    admit_same_oriented_pair a b hsame
  exact ⟨a', b', hfirst.trans ha, hsecond.trans hb, hblocks⟩

/-- Lemma 2.2 on its stated two-placement domain, for at least two blocks. -/
theorem realize_same_oriented_placements [DecidableEq α]
    (F : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n r α)
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second) :
    ∃ word : List Letter,
      run F s word = { s with placed := second.placed } ∧
      FusionFree F s word := by
  rcases same with ⟨blocks, order₁, order₂⟩
  exact realizeNamedPlacementTarget F s (first.admit order₁)
    (second.admit order₂) hn hr source blocks

theorem realize_same_oriented_block_cycle [DecidableEq α]
    (F : Finset α) (s : Execution n α)
    (first second : Placement n (Finset α))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first)
    (same : SameOrientedBlockCycle (r := r) first second) :
    ∃ word : List Letter,
      run F s word = { s with placed := second } ∧
      FusionFree F s word := by
  obtain ⟨a, b, ha, hb, hsame⟩ := same
  have hsource : s.placed = a.placed := source.trans ha.symm
  obtain ⟨word, hrun, hfree⟩ :=
    realize_same_oriented_placements F s a b hn hr hsource hsame
  exact ⟨word, by simpa [hb] using hrun, hfree⟩

/-- One named block requires only a phase rotation, with no gap balancing. -/
theorem single_block_rotate
    (first second : LegalNamedPlacement n 1 α)
    (blocks : first.block = second.block) :
    rotate (second.position 0 - first.position 0) first.placed =
      second.placed := by
  let phase := second.position 0 - first.position 0
  funext q
  by_cases hq : q = second.position 0
  · subst q
    change first.placed (second.position 0 - phase) =
      second.placed (second.position 0)
    have hsite : second.position 0 - phase = first.position 0 := by
      dsimp [phase]
      abel
    rw [hsite, first.placed_at 0, second.placed_at 0, congrFun blocks 0]
  · have htarget : second.placed q = none := by
      by_contra hoccupied
      obtain ⟨i, hi⟩ := second.only_named q hoccupied
      have hi0 : i = 0 := Subsingleton.elim i 0
      exact hq (by simpa [hi0] using hi.symm)
    have hsource : first.placed (q - phase) = none := by
      by_contra hoccupied
      obtain ⟨i, hi⟩ := first.only_named (q - phase) hoccupied
      have hi0 : i = 0 := Subsingleton.elim i 0
      apply hq
      have h := congrArg (fun x : ZMod n => x + phase) hi
      simpa [hi0, phase, sub_add_cancel] using h.symm
    change first.placed (q - phase) = second.placed q
    rw [hsource, htarget]

theorem realize_same_single_block [DecidableEq α]
    (F : Finset α) (s : Execution n α)
    (first second : LegalNamedPlacement n 1 α)
    (source : s.placed = first.placed)
    (blocks : first.block = second.block) :
    ∃ word : List Letter,
      run F s word = { s with placed := second.placed } ∧
      FusionFree F s word := by
  let phase := second.position 0 - first.position 0
  refine ⟨pWord phase.val, ?_, fusionFree_pWord F s _⟩
  rw [run_rotation, source, single_block_rotate first second blocks]

/-- The one-block paper premise needs no cyclic-gap orientation. -/
def SameSingleBlock (first second : Placement n (Finset α)) : Prop :=
  ∃ (a b : LegalNamedPlacement n 1 α),
    a.placed = first ∧ b.placed = second ∧ a.block = b.block

theorem realize_same_single_block_cycle [DecidableEq α]
    (F : Finset α) (s : Execution n α)
    (first second : Placement n (Finset α))
    (source : s.placed = first) (same : SameSingleBlock first second) :
    ∃ word : List Letter,
      run F s word = { s with placed := second } ∧
      FusionFree F s word := by
  obtain ⟨a, b, ha, hb, hblocks⟩ := same
  obtain ⟨word, hrun, hfree⟩ :=
    realize_same_single_block F s a b (source.trans ha.symm) hblocks
  exact ⟨word, by simpa [hb] using hrun, hfree⟩

end RegisteredAbsorptionChains
