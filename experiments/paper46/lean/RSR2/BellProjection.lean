import RSR2.CanonicalEndpoint

/-!
# Unordered Bell endpoint projection

An unordered partition is an equivalence relation on the finite atom type;
it comes with no choice of block order or atom order. Every such relation has
an ordered presentation. The existing guarded canonical-endpoint theorem then
realizes exactly that relation as `samePacket`, with its existing word bound.
No change to the executor, loading algorithm, or cost ledger is made here.
-/

namespace RSR2

/-- Unordered set partitions, specified by their same-block equivalence relation. -/
abbrev UnorderedPartition (n : Nat) := Setoid (Fin n)

/-- Forget both orders in an ordered presentation. -/
def OrderedPartition.Represents (p : OrderedPartition n)
    (π : UnorderedPartition n) : Prop :=
  ∀ a b, (∃ B ∈ p.blocks, a ∈ B ∧ b ∈ B) ↔ π.r a b

/-- Group a finite list into equivalence classes. This is a presentation
lemma only: the input need not already provide ordered blocks. -/
private theorem equivalence_list_presentation (r : Setoid α) (xs : List α) :
    ∃ blocks : List (List α),
      (∀ B ∈ blocks, B ≠ []) ∧ blocks.flatten.Perm xs ∧
      ∀ a b, (∃ B ∈ blocks, a ∈ B ∧ b ∈ B) ↔
        a ∈ xs ∧ b ∈ xs ∧ r.r a b := by
  classical
  cases xs with
  | nil => exact ⟨[], by simp, .refl _, by simp⟩
  | cons x tail =>
      let same := tail.filter (fun a => decide (r.r x a))
      let rest := tail.filter (fun a => !decide (r.r x a))
      obtain ⟨blocks, hne, hperm, hrel⟩ := equivalence_list_presentation r rest
      have hsame (a : α) : a ∈ x :: same ↔ a ∈ x :: tail ∧ r.r x a := by
        simp only [List.mem_cons, same, List.mem_filter, decide_eq_true_eq]
        constructor
        · rintro (rfl | ⟨ha, hr⟩)
          · exact ⟨by simp, r.iseqv.refl _⟩
          · exact ⟨by simp [ha], hr⟩
        · rintro ⟨ha, hr⟩
          rcases ha with rfl | ha
          · exact Or.inl rfl
          · exact Or.inr ⟨ha, hr⟩
      have hrest (a : α) : a ∈ rest ↔ a ∈ tail ∧ ¬r.r x a := by
        simp [rest]
      refine ⟨(x :: same) :: blocks, ?_, ?_, ?_⟩
      · intro B hB
        rcases List.mem_cons.mp hB with rfl | hB
        · simp
        · exact hne B hB
      · simp only [List.flatten_cons]
        apply (List.Perm.append_left (x :: same) hperm).trans
        simpa only [List.cons_append] using
          (List.filter_append_perm (fun a => decide (r.r x a)) tail).cons x
      · intro a b
        constructor
        · rintro ⟨B, hB, ha, hb⟩
          rcases List.mem_cons.mp hB with rfl | hB
          · obtain ⟨ha, hxa⟩ := (hsame a).mp ha
            obtain ⟨hb, hxb⟩ := (hsame b).mp hb
            exact ⟨ha, hb, r.iseqv.trans (r.iseqv.symm hxa) hxb⟩
          · obtain ⟨ha, hb, hab⟩ := (hrel a b).mp ⟨B, hB, ha, hb⟩
            exact ⟨by simp [(hrest a).mp ha], by simp [(hrest b).mp hb], hab⟩
        · rintro ⟨ha, hb, hab⟩
          by_cases hxa : r.r x a
          · exact ⟨x :: same, by simp, (hsame a).mpr ⟨ha, hxa⟩,
              (hsame b).mpr ⟨hb, r.iseqv.trans hxa hab⟩⟩
          · have hxb : ¬r.r x b := fun h => hxa
              (r.iseqv.trans h (r.iseqv.symm hab))
            have hat : a ∈ tail := by
              rcases List.mem_cons.mp ha with rfl | h
              · exact False.elim (hxa (r.iseqv.refl _))
              · exact h
            have hbt : b ∈ tail := by
              rcases List.mem_cons.mp hb with rfl | h
              · exact False.elim (hxb (r.iseqv.refl _))
              · exact h
            obtain ⟨B, hB, haB, hbB⟩ := (hrel a b).mpr
              ⟨(hrest a).mpr ⟨hat, hxa⟩, (hrest b).mpr ⟨hbt, hxb⟩, hab⟩
            exact ⟨B, by simp [hB], haB, hbB⟩
termination_by xs.length
decreasing_by
  classical
  have h := List.length_filter_le (fun a => !decide (r.r x a)) tail
  simp only [List.length_cons]
  exact Nat.lt_succ_of_le h

/-- Every unordered finite partition has an ordered presentation, rather
than requiring a block ordering as an additional input hypothesis. -/
theorem unorderedPartition_has_orderedPresentation (π : UnorderedPartition n) :
    ∃ p : OrderedPartition n, p.Represents π := by
  obtain ⟨blocks, hne, hperm, hrel⟩ :=
    equivalence_list_presentation π (List.finRange n)
  exact ⟨⟨blocks, hne, hperm⟩, by
    intro a b
    simpa [List.mem_finRange] using hrel a b⟩

end RSR2

namespace RSR2.Parametric

/-- The canonical endpoint has exactly the unordered same-block relation
of its ordered input, independently of the chosen orders. -/
theorem canonicalPlacement_samePacket_iff (p : RSR2.OrderedPartition n)
    (a b : Fin n) :
    samePacket (canonicalPlacement p) a b ↔
      ∃ B ∈ p.blocks, a ∈ B ∧ b ∈ B := by
  constructor
  · intro hab
    have ha : a ∈ p.blocks.flatten :=
      p.flatten_perm.mem_iff.mpr (List.mem_finRange a)
    obtain ⟨B, hB, haB⟩ := List.mem_flatten.mp ha
    obtain ⟨pre, post, hblocks⟩ := List.mem_iff_append.mp hB
    have haq := (canonicalPlacement_packet_iff p pre B post hblocks a).mpr haB
    have hbq : (canonicalPlacement p b).2.val = blockAtomCount pre := by
      rw [← haq]
      exact congrArg (fun loc => loc.2.val) hab.symm
    exact ⟨B, hB, haB,
      (canonicalPlacement_packet_iff p pre B post hblocks b).mp hbq⟩
  · rintro ⟨B, hB, ha, hb⟩
    obtain ⟨pre, post, hblocks⟩ := List.mem_iff_append.mp hB
    have haq := (canonicalPlacement_packet_iff p pre B post hblocks a).mpr ha
    have hbq := (canonicalPlacement_packet_iff p pre B post hblocks b).mpr hb
    apply Prod.ext
    · rfl
    · exact Fin.ext (haq.trans hbq.symm)

/-- Bell endpoint universality for genuinely unordered partitions. The
successful guarded run and bound are reused from the ordered construction. -/
theorem unorderedPartition_bell_realization (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) :
    ∃ W P, run n hn (seed n) W = some P ∧
      (∀ a b, samePacket P a b ↔ π.r a b) ∧
      W.length ≤ n * n + 2 * n - 2 := by
  obtain ⟨p, hp⟩ := RSR2.unorderedPartition_has_orderedPresentation π
  obtain ⟨W, hrun, hlen⟩ := orderedPartition_bell_realization_uniform n hn p
  refine ⟨W, canonicalPlacement p, hrun, ?_, hlen⟩
  intro a b
  exact (canonicalPlacement_samePacket_iff p a b).trans (hp a b)

end RSR2.Parametric
