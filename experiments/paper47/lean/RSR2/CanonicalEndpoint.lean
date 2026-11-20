import RSR2.Executable

/-!
# Exact canonical endpoint of the guarded Bell construction

This module adds only the upper-coordinate invariant.  Guard legality, the
lower singleton family, and the raw-letter ledger are reused from the existing
executable construction.  Natural coordinates are justified by the existing
`upperSupportBelow` bound, so the argument never silently ignores wraparound.
-/

namespace RSR2.Parametric

/-- The upper coordinate, forgetting the site of an atom still downstairs. -/
def upperCoordinate (P : Placement n) (a : Fin n) : Option Nat :=
  if (P a).1 then some (P a).2.val else none

/-- Rotation, followed (only on continuation) by the upper defect. -/
def advanceUpper (first continues : Bool) (q : Nat) : Nat :=
  let r := q + bitCost (!first)
  if continues = true ∧ r = 1 then 0 else r

/-- Coordinate-only specification of the actual marked loading stream. -/
def packAtom (first : Bool) (xs : List (Fin n × Bool))
    (a : Fin n) (q : Option Nat) : Option Nat :=
  match xs with
  | [] => q
  | (b, continues) :: rest =>
      packAtom false rest a
        (if a = b then some 0 else q.map (advanceUpper first continues))

theorem packAtom_append (xs ys : List (Fin n × Bool))
    (a : Fin n) (q : Option Nat) :
    packAtom false (xs ++ ys) a q =
      packAtom false ys a (packAtom false xs a q) := by
  induction xs generalizing q with
  | nil => rfl
  | cons x xs ih => cases x; simp only [List.cons_append, packAtom]; exact ih _

theorem packAtom_first_empty (xs : List (Fin n × Bool)) (a : Fin n) :
    packAtom true xs a none = packAtom false xs a none := by
  cases xs with
  | nil => rfl
  | cons x xs => cases x; simp [packAtom]

theorem packAtom_continuations (xs : List (Fin n)) (a : Fin n)
    (q : Option Nat) :
    packAtom false (xs.map (fun b => (b, true))) a q =
      if a ∈ xs then some 0
      else q.map (fun r => if r = 0 then 0 else r + xs.length) := by
  induction xs generalizing q with
  | nil => cases q <;> simp [packAtom]
  | cons b xs ih =>
      simp only [List.map_cons, packAtom, ih, List.mem_cons, List.length_cons]
      by_cases hab : a = b
      · subst b; simp
      · by_cases hmem : a ∈ xs
        · simp [hab, hmem]
        · cases q with
          | none => simp [hab, hmem]
          | some r =>
              by_cases hr : r = 0
              · simp [hab, hmem, hr, advanceUpper, bitCost]
              · simp [hab, hmem, hr, advanceUpper, bitCost,
                  Nat.add_comm, Nat.add_left_comm]

/-- One block starts with a new singleton and keeps exactly that block at 0.
Every previously completed block advances by the full size of the new block. -/
theorem packAtom_markBlock (xs : List (Fin n)) (a : Fin n)
    (q : Option Nat) :
    packAtom false (markBlock xs) a q =
      if a ∈ xs then some 0 else q.map (fun r => r + xs.length) := by
  cases xs with
  | nil => cases q <;> simp [markBlock, packAtom]
  | cons b xs =>
      simp only [markBlock, packAtom, packAtom_continuations, List.mem_cons,
        List.length_cons]
      by_cases hab : a = b
      · subst b; simp
      · by_cases hmem : a ∈ xs
        · simp [hab, hmem]
        · cases q with
          | none => simp [hab, hmem]
          | some r =>
              simp [hab, hmem, advanceUpper, bitCost,
                Nat.add_comm, Nat.add_left_comm]

/-- A block's coordinate is the number of atoms in the preceding blocks. -/
def blockCoordinate (blocks : List (List (Fin n))) (a : Fin n) : Option Nat :=
  match blocks with
  | [] => none
  | b :: rest =>
      if a ∈ b then some 0 else (blockCoordinate rest a).map (b.length + ·)

theorem packAtom_markedReverseBlocks (blocks : List (List (Fin n)))
    (a : Fin n) :
    packAtom false (markedReverseBlocks blocks) a none =
      blockCoordinate blocks a := by
  induction blocks with
  | nil => rfl
  | cons b bs ih =>
      have heq : markedReverseBlocks (b :: bs) =
          markedReverseBlocks bs ++ markBlock b.reverse := by
        simp [markedReverseBlocks, List.reverse_cons, List.map_append]
      rw [heq, packAtom_append, ih, packAtom_markBlock]
      simp [blockCoordinate, Nat.add_comm]

theorem blockCoordinate_exists (blocks : List (List (Fin n))) (a : Fin n)
    (ha : a ∈ blocks.flatten) :
    ∃ q, blockCoordinate blocks a = some q ∧ q < blockAtomCount blocks := by
  induction blocks with
  | nil => simp at ha
  | cons b bs ih =>
      by_cases hab : a ∈ b
      · have hb : 0 < b.length := List.length_pos_of_mem hab
        exact ⟨0, by simp [blockCoordinate, hab], by
          simp only [blockAtomCount, List.map_cons, List.sum_cons]; omega⟩
      · have htail : a ∈ bs.flatten := by simpa [hab] using ha
        rcases ih htail with ⟨q, hq, hlt⟩
        refine ⟨b.length + q, by simp [blockCoordinate, hab, hq], ?_⟩
        simp only [blockAtomCount, List.map_cons, List.sum_cons]
        change q < (bs.map List.length).sum at hlt
        omega

theorem orderedPartition_blockCoordinate (p : RSR2.OrderedPartition n)
    (a : Fin n) :
    ∃ q, blockCoordinate p.blocks a = some q ∧ q < n := by
  have hmem : a ∈ p.blocks.flatten :=
    p.flatten_perm.mem_iff.mpr (List.mem_finRange a)
  simpa [orderedPartition_blockAtomCount p] using
    blockCoordinate_exists p.blocks a hmem

/-- The literal canonical representative: all atoms are upstairs and each
block is at the sum of the sizes of its predecessors. -/
def canonicalPlacement (p : RSR2.OrderedPartition n) : Placement n := fun a =>
  (true, ⟨(blockCoordinate p.blocks a).getD 0, by
    obtain ⟨q, hq, hlt⟩ := orderedPartition_blockCoordinate p a
    simpa [hq] using hlt⟩)

theorem canonicalPlacement_upperCoordinate (p : RSR2.OrderedPartition n)
    (a : Fin n) :
    upperCoordinate (canonicalPlacement p) a = blockCoordinate p.blocks a := by
  obtain ⟨q, hq, _⟩ := orderedPartition_blockCoordinate p a
  simp [canonicalPlacement, upperCoordinate, hq]

/-- The prefix-sum coordinate selects exactly the indicated block.  Nonempty
blocks separate consecutive coordinates; atom disjointness excludes a second
occurrence in an earlier block. -/
theorem blockCoordinate_eq_prefix_iff
    (pre : List (List (Fin n))) (b : List (Fin n))
    (post : List (List (Fin n)))
    (hnonempty : ∀ c ∈ pre ++ b :: post, c ≠ [])
    (hnodup : (pre ++ b :: post).flatten.Nodup) (a : Fin n) :
    blockCoordinate (pre ++ b :: post) a = some (blockAtomCount pre) ↔
      a ∈ b := by
  induction pre with
  | nil =>
      have hb : 0 < b.length := List.length_pos_iff.mpr (hnonempty b (by simp))
      by_cases hab : a ∈ b
      · simp [blockCoordinate, blockAtomCount, hab]
      · simp only [List.nil_append, blockCoordinate, hab, ↓reduceIte,
          blockAtomCount, List.map_nil, List.sum_nil]
        cases hq : blockCoordinate post a with
        | none => simp
        | some q =>
            simp only [Option.map_some, Option.some.injEq, iff_false]
            omega
  | cons c pre ih =>
      have hc : 0 < c.length := List.length_pos_iff.mpr (hnonempty c (by simp))
      have htail : ∀ d ∈ pre ++ b :: post, d ≠ [] := by
        intro d hd
        exact hnonempty d (by simp [hd])
      have hnd := List.nodup_append.mp (by
        simpa only [List.cons_append, List.flatten_cons] using hnodup)
      have hbt : b ⊆ (pre ++ b :: post).flatten := by
        intro x hx
        simp only [List.flatten_append, List.flatten_cons, List.mem_append]
        exact Or.inr (Or.inl hx)
      by_cases hac : a ∈ c
      · have hab : a ∉ b := by
          intro hab
          exact hnd.2.2 a hac a (hbt hab) rfl
        simp only [List.cons_append, blockCoordinate, hac, ↓reduceIte,
          blockAtomCount, List.map_cons, List.sum_cons]
        simp only [Option.some.injEq, hab, iff_false]
        omega
      · have hi := ih htail hnd.2.1
        simp only [List.cons_append, blockCoordinate, hac, ↓reduceIte,
          blockAtomCount, List.map_cons, List.sum_cons]
        change (blockCoordinate (pre ++ b :: post) a).map (c.length + ·) =
          some (c.length + blockAtomCount pre) ↔ a ∈ b
        cases hq : blockCoordinate (pre ++ b :: post) a <;>
          simpa [hq] using hi

/-- Literal packet characterization, not just an atom-count or all-upper
statement: block `b` is exactly the packet at its prefix-sum site. -/
theorem canonicalPlacement_packet_iff
    (p : RSR2.OrderedPartition n)
    (pre : List (List (Fin n))) (b : List (Fin n))
    (post : List (List (Fin n)))
    (hblocks : p.blocks = pre ++ b :: post) (a : Fin n) :
    (canonicalPlacement p a).2.val = blockAtomCount pre ↔ a ∈ b := by
  have hnonempty : ∀ c ∈ pre ++ b :: post, c ≠ [] := by
    simpa [← hblocks] using p.nonempty
  have hnodup : (pre ++ b :: post).flatten.Nodup := by
    rw [← hblocks]
    exact p.flatten_perm.nodup_iff.mpr (List.nodup_finRange n)
  obtain ⟨q, hq, _⟩ := orderedPartition_blockCoordinate p a
  have hi := blockCoordinate_eq_prefix_iff pre b post hnonempty hnodup a
  simpa [canonicalPlacement, ← hblocks, hq] using hi

/-- Immediately before a continuation's `d₁`, port 1 contains exactly the
previous packet at port 0.  The newly lifted singleton stays at port 0, and
no completed packet at another site is included in that parent. -/
theorem instruction_continuation_port_one_iff
    (n : Nat) (hn : 1 < n) (P : Placement n) (i : LoadInstruction n)
    (a : Fin n) :
    packet (liftPacket n (by omega) (instructionPrepared n hn false P i))
        true (site1 n hn) a ↔
      packet P true (site0 n (by omega)) a := by
  unfold packet
  cases hPa : P a with
  | mk layer q =>
      cases layer with
      | false =>
          simp only [instructionPrepared, bitCost, Bool.not_false,
            rotateMany_apply, hPa, Bool.false_eq_true, ↓reduceIte,
            liftPacket]
          split <;> simp [site0, site1]
      | true =>
          have hnext : next n (by omega) q = site1 n hn ↔
              q = site0 n (by omega) := by
            constructor
            · intro h
              exact next_injective n (by omega)
                (h.trans (next_zero n hn).symm)
            · intro h
              simpa [h] using next_zero n hn
          simp [instructionPrepared, bitCost, rotateMany_apply, nextMany,
            hPa, liftPacket, hnext]

/-- An already loaded atom advances without wraparound before the elevator.
The first-instruction branch has no already loaded atoms. -/
theorem instructionPrepared_upper_site
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (k : Nat) (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k) (hk : k < n)
    (hfirst : first = true → k = 0)
    (a : Fin n) (ha : (P a).1 = true) :
    ∃ q : Fin n,
      instructionPrepared n hn first P i a = (true, q) ∧
      q.val = (P a).2.val + bitCost (!first) := by
  have hbound := hupper a ha
  cases hf : first with
  | true => have := hfirst hf; omega
  | false =>
      have hlt : (P a).2.val + 1 < n := by omega
      refine ⟨next n (by omega) (P a).2, ?_, ?_⟩
      · simp [instructionPrepared, bitCost, rotateMany_apply, nextMany,
          ha]
      · simp [bitCost, next, hlt]

/-- The real instruction has exactly the coordinate-only step specified by
`advanceUpper`.  The still-unloaded singleton family supplies the source and
ensures that no other lower atom is lifted. -/
theorem instructionResult_upperCoordinate
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (rest : List (Fin n)) (phase k : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k) (hk : k < n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (i.atom :: rest) phase)
    (hnodup : (i.atom :: rest).Nodup)
    (hsub : lowerSupportSubset P (i.atom :: rest))
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0)
    (a : Fin n) :
    upperCoordinate (instructionResult n hn first P i) a =
      if a = i.atom then some 0
      else (upperCoordinate P a).map (advanceUpper first i.continueBlock) := by
  by_cases hai : a = i.atom
  · subst a
    have hsource := hfamily i.atom (by simp)
    have hprepared : instructionPrepared n hn first P i i.atom =
        (false, site0 n (by omega)) := by
      exact rotateMany_lower_aligned n hn
        (rotateMany n (by omega) P true (bitCost (!first))) i.atom
        (phaseSite n i.atom phase) i.sourceTurns
        ((rotateMany_upper_lower_iff n hn P (bitCost (!first)) i.atom
          (phaseSite n i.atom phase)).2 hsource) halign
    cases hc : i.continueBlock <;>
      simp [instructionResult, hc, liftPacket, collapse, hprepared,
        upperCoordinate, site0]
  · cases ha : (P a).1 with
    | false =>
        have hmem : a ∈ rest := by
          have := hsub a ha
          simpa [hai] using this
        have htail := lowerFamily_after_instructionResult_tail n hn P rest
          phase first i hnodup hfamily halign a hmem
        simp [upperCoordinate, htail, ha, hai]
    | true =>
        obtain ⟨q, hq, hval⟩ := instructionPrepared_upper_site n hn P k first
          i hupper hk hfirst a ha
        have hlift : liftPacket n (by omega)
            (instructionPrepared n hn first P i) a = (true, q) := by
          simp [liftPacket, hq]
        have hqone : q = site1 n hn ↔ q.val = 1 := by
          constructor
          · intro heq; simpa [site1] using congrArg Fin.val heq
          · intro heq; apply Fin.ext; simpa [site1] using heq
        cases hc : i.continueBlock <;>
          by_cases hone : (P a).2.val + bitCost (!first) = 1 <;>
          simp [instructionResult, hc, hlift, collapse, upperCoordinate,
            ha, hai, advanceUpper, hqone, hval, hone, site0]

/-- The existing guarded execution follows the coordinate model at every
instruction boundary, retaining the no-wrap support bound in the induction. -/
theorem guardedPlan_annotateMarked_upperCoordinate
    (n : Nat) (hn : 1 < n)
    (phase k : Nat) (first : Bool) (P R : Placement n)
    (xs : List (Fin n × Bool))
    (hupper : upperSupportBelow P k)
    (hk : k + xs.length ≤ n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (xs.map Prod.fst) phase)
    (hnodup : (xs.map Prod.fst).Nodup)
    (hsub : lowerSupportSubset P (xs.map Prod.fst))
    (hguarded : GuardedPlan n hn first P (annotateMarked n phase xs) R) :
    ∀ a, upperCoordinate R a = packAtom first xs a (upperCoordinate P a) := by
  induction xs generalizing phase k first P with
  | nil => cases hguarded; intro a; rfl
  | cons x rest ih =>
      rcases x with ⟨a, continues⟩
      let q : Fin n :=
        ⟨(a.val + phase) % n, Nat.mod_lt _ (by omega)⟩
      let i : LoadInstruction n := ⟨a, lowerBackCount n q, continues⟩
      have hk' : k < n := by simp only [List.length_cons] at hk; omega
      have hkrest : (k + 1) + rest.length ≤ n := by
        simp only [List.length_cons] at hk; omega
      have hfamily' : lowerFamily P (i.atom :: rest.map Prod.fst) phase :=
        hfamily
      have hnodup' : (i.atom :: rest.map Prod.fst).Nodup := hnodup
      have hsub' : lowerSupportSubset P (i.atom :: rest.map Prod.fst) := hsub
      have halign :
          ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0 := by
        simpa [i, q] using lowerBackCount_phaseSite_aligns n (by omega) a phase
      have hinv := loadingInvariant_after_instructionResult_cons n hn P
        (rest.map Prod.fst) phase k first i hupper hk' hfirst hfamily'
        hnodup' halign
      have hsubnext := lowerSupportSubset_after_instructionResult_tail n hn P
        (rest.map Prod.fst) phase first i hsub' hfamily' halign
      change GuardedPlan n hn first P
        (i :: annotateMarked n (phase + i.sourceTurns) rest) R at hguarded
      cases hguarded with
      | cons hguard hrest =>
          have htail := ih (phase := phase + i.sourceTurns) (k := k + 1)
            (first := false) (P := instructionResult n hn first P i)
            hinv.1 hkrest (by simp) hinv.2.1 hinv.2.2 hsubnext hrest
          intro b
          rw [htail b]
          have hstep := instructionResult_upperCoordinate n hn P
            (rest.map Prod.fst) phase k first i hupper hk' hfirst
            hfamily' hnodup' hsub' halign b
          simpa only [packAtom, i] using
            congrArg (packAtom false rest b) hstep

/-- Atomwise upper coordinates determine the entire canonical placement,
including the absence of all lower packets. -/
theorem eq_canonicalPlacement_of_upperCoordinate
    (p : RSR2.OrderedPartition n) (P : Placement n)
    (h : ∀ a, upperCoordinate P a = blockCoordinate p.blocks a) :
    P = canonicalPlacement p := by
  funext a
  obtain ⟨q, hq, _⟩ := orderedPartition_blockCoordinate p a
  have ha := h a
  cases hPa : P a with
  | mk layer site =>
      cases layer with
      | false => simp [upperCoordinate, hPa, hq] at ha
      | true =>
          have hsite : site.val = q := by
            simpa [upperCoordinate, hPa, hq] using ha
          apply Prod.ext
          · simp [canonicalPlacement]
          · apply Fin.ext
            simp [canonicalPlacement, hq, hsite]

/-- The actual five-generator guarded execution reaches the literal canonical
stacked placement for every ordered partition. -/
theorem orderedPartition_run_canonical
    (n : Nat) (hn : 1 < n) (p : RSR2.OrderedPartition n) :
    run n hn (seed n) (emitPlan (interleavedPlan n p.blocks)) =
      some (canonicalPlacement p) := by
  let xs := markedReverseBlocks p.blocks
  have hlen : xs.length = n := by
    dsimp [xs]
    rw [markedReverseBlocks_length n p.blocks]
    exact orderedPartition_blockAtomCount p
  have hupper := seed_upperSupportBelow_zero n
  have hfamily := seed_lowerFamily n (by omega) (xs.map Prod.fst)
  have hnodup : (xs.map Prod.fst).Nodup := by
    dsimp [xs]
    exact markedReverseBlocks_atom_nodup p
  have hsub : lowerSupportSubset (seed n) (xs.map Prod.fst) := by
    intro a _
    dsimp [xs]
    rw [markedReverseBlocks_atoms, flatten_reverse_blocks]
    apply List.mem_reverse.mpr
    exact p.flatten_perm.mem_iff.mpr (List.mem_finRange a)
  have hk : 0 + xs.length ≤ n := by omega
  obtain ⟨R, hguarded⟩ := guardedPlan_annotateMarked n hn 0 0 true
    (seed n) xs hupper hk (by simp) hfamily hnodup
  have hcoord := guardedPlan_annotateMarked_upperCoordinate n hn 0 0 true
    (seed n) R xs hupper hk (by simp) hfamily hnodup hsub hguarded
  have hR : R = canonicalPlacement p := by
    apply eq_canonicalPlacement_of_upperCoordinate
    intro a
    simpa [upperCoordinate, seed, packAtom_first_empty, xs,
      packAtom_markedReverseBlocks] using hcoord a
  have hrun := guardedPlan_run_emitPlan n hn (seed n) R
    (annotateMarked n 0 xs) hguarded
  simpa [interleavedPlan, xs, hR] using hrun

/-- Executable Bell realization with the existing raw-letter bound; no new
cost estimate is needed for the canonical endpoint proof. -/
theorem orderedPartition_bell_realization
    (n : Nat) (hn : 1 < n) (p : RSR2.OrderedPartition n) :
    ∃ W, run n hn (seed n) W = some (canonicalPlacement p) ∧
      W.length ≤ n * n + 2 * n - p.blockCount - 1 := by
  exact ⟨emitPlan (interleavedPlan n p.blocks),
    orderedPartition_run_canonical n hn p,
    orderedPartition_interleavedPlan_length_bound p (by omega)⟩

/-- The uniform endpoint-partition budget follows from nonempty block count. -/
theorem orderedPartition_bell_realization_uniform
    (n : Nat) (hn : 1 < n) (p : RSR2.OrderedPartition n) :
    ∃ W, run n hn (seed n) W = some (canonicalPlacement p) ∧
      W.length ≤ n * n + 2 * n - 2 := by
  obtain ⟨W, hrun, hlength⟩ := orderedPartition_bell_realization n hn p
  have hblocks := RSR2.blockCount_positive p (by omega)
  exact ⟨W, hrun, by omega⟩

end RSR2.Parametric
