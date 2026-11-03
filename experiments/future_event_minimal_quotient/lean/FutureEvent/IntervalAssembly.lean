import FutureEvent.PlacementGeometry

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Descending adjacent collapses assemble a linear source block. The word
is an actual raw word; its defect letters are allowed to be genuine fusions. -/
def intervalWord (lo : ℕ) : ℕ → List Letter
  | 0 => []
  | k + 1 => intervalWord (lo + 1) k ++ localLetters (lo : ZMod n)

theorem intervalWord_site (lo k : ℕ) (hk : lo + k < n) (q : ZMod n) :
    siteWord (intervalWord (n := n) lo k) q =
      if lo ≤ q.val ∧ q.val ≤ lo + k then (lo : ZMod n) else q := by
  induction k generalizing lo with
  | zero =>
      change q = if lo ≤ q.val ∧ q.val ≤ lo then (lo : ZMod n) else q
      by_cases he : q.val = lo
      · have hq : q = (lo : ZMod n) := by rw [← ZMod.natCast_zmod_val q, he]
        simp [hq]
      · simp [show ¬ (lo ≤ q.val ∧ q.val ≤ lo) by omega]
  | succ k ih =>
      rw [intervalWord, siteWord_append, ih (lo + 1) (by omega), localLetters_site]
      by_cases hupper : lo + 1 ≤ q.val ∧ q.val ≤ lo + 1 + k
      · rw [if_pos hupper]
        have hcast : ((lo + 1 : ℕ) : ZMod n) = (lo : ZMod n) + 1 := by push_cast; rfl
        rw [if_pos hcast]
        rw [if_pos (show lo ≤ q.val ∧ q.val ≤ lo + (k + 1) by omega)]
      · rw [if_neg hupper]
        by_cases hsame : q.val = lo
        · have hq : q = (lo : ZMod n) := by rw [← ZMod.natCast_zmod_val q, hsame]
          have hne : q ≠ (lo : ZMod n) + 1 := by
            intro he
            have hv := congrArg ZMod.val he
            have hp : ((lo : ZMod n) + 1).val = lo + 1 := by
              simpa only [Nat.cast_add, Nat.cast_one] using
                ZMod.val_natCast_of_lt (n := n) (a := lo + 1) (by omega)
            rw [hsame, hp] at hv
            omega
          rw [if_neg hne, if_pos (show lo ≤ q.val ∧ q.val ≤ lo + (k + 1) by omega)]
          exact hq
        · have hne : q ≠ (lo : ZMod n) + 1 := by
            intro he
            have hv := congrArg ZMod.val he
            have hp : ((lo : ZMod n) + 1).val = lo + 1 := by
              simpa only [Nat.cast_add, Nat.cast_one] using
                ZMod.val_natCast_of_lt (n := n) (a := lo + 1) (by omega)
            rw [hp] at hv
            omega
          rw [if_neg hne, if_neg (show ¬ (lo ≤ q.val ∧ q.val ≤ lo + (k + 1)) by omega)]

def sourceBlockWord (lo hi : ℕ) : List Letter := intervalWord (n := n) lo (hi - lo - 1)

theorem sourceBlockWord_site (lo hi : ℕ) (hlt : lo < hi) (hhi : hi ≤ n) (q : ZMod n) :
    siteWord (sourceBlockWord (n := n) lo hi) q =
      if q ∈ sourceInterval lo hi then (lo : ZMod n) else q := by
  rw [sourceBlockWord, intervalWord_site lo (hi - lo - 1) (by omega)]
  simp only [mem_sourceInterval_iff lo hi hhi]
  have he : (lo ≤ q.val ∧ q.val ≤ lo + (hi - lo - 1)) ↔
      (lo ≤ q.val ∧ q.val < hi) := by omega
  simp only [he]

omit [NeZero n] in
theorem flatMap_site_fixed {ι : Type*} (macros : ι → List Letter)
    (indices : List ι) (q : ZMod n)
    (h : ∀ i ∈ indices, siteWord (macros i) q = q) :
    siteWord (indices.flatMap macros) q = q := by
  induction indices with
  | nil => rfl
  | cons i rest ih =>
      rw [List.flatMap_cons, siteWord_append, h i (by simp)]
      exact ih (by intro j hj; exact h j (by simp [hj]))

theorem map_matches_legal {r : ℕ} [NeZero r]
    (named : LegalNamedPlacement n r (ZMod n)) (f : ZMod n → ZMod n)
    (hmap : ∀ i atom, atom ∈ named.block i → f atom = named.position i) :
    placementOfMap f = named.placed := by
  have hf (i : ZMod r) : sourceFiber f (named.position i) = named.block i := by
    ext atom
    rw [mem_sourceFiber]
    constructor
    · intro ha
      obtain ⟨j, hj⟩ := named.atom_covered atom
      have he := named.position_injective ((hmap j atom hj).symm.trans ha)
      simpa [he] using hj
    · exact hmap i atom
  funext q
  cases hq : named.placed q with
  | none =>
      have hz : sourceFiber f q = ∅ := by
        ext atom
        simp only [mem_sourceFiber, Finset.notMem_empty, iff_false]
        intro he
        obtain ⟨i, hi⟩ := named.atom_covered atom
        have hp : named.position i = q := (hmap i atom hi).symm.trans he
        have hs := named.placed_at i
        rw [hp, hq] at hs
        simp at hs
      exact (placementOfMap_none_iff f q).mpr hz
  | some B =>
      obtain ⟨i, hi⟩ := named.only_named q (by rw [hq]; simp)
      have hB : B = named.block i := Option.some.inj (hq.symm.trans (hi ▸ named.placed_at i))
      apply (placementOfMap_some_iff f q B).mpr
      exact ⟨by rw [← hi, hf, hB], hB.symm ▸ named.block_nonempty i⟩

end FutureEvent
