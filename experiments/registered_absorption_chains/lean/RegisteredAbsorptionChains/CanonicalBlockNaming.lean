import RegisteredAbsorptionChains.SourceOrderAdmission
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem sourceOrdered_blocks_disjoint
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (B C : Finset (ZMod n))
    (hB : B ∈ placedBlocks placed) (hC : C ∈ placedBlocks placed)
    (hne : B ≠ C) : Disjoint B C := by
  obtain ⟨lift, hplaced⟩ := ordered
  obtain ⟨_, qB, hqB⟩ := (mem_placedBlocks placed B).mp hB
  obtain ⟨_, qC, hqC⟩ := (mem_placedBlocks placed C).mp hC
  have hfiberB := (placementOfMap_some_iff lift.position qB B).mp
    (hplaced ▸ hqB)
  have hfiberC := (placementOfMap_some_iff lift.position qC C).mp
    (hplaced ▸ hqC)
  apply Finset.disjoint_left.mpr
  intro a haB haC
  have heq : qB = qC := by
    have hb := (mem_sourceFiber lift.position a qB).mp
      (hfiberB.1.symm ▸ haB)
    have hc := (mem_sourceFiber lift.position a qC).mp
      (hfiberC.1.symm ▸ haC)
    exact hb.symm.trans hc
  exact hne (Option.some.inj (hqB.symm.trans (heq ▸ hqC)))

theorem sourceOrdered_blocks_cover
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) (a : ZMod n) :
    ∃ B ∈ placedBlocks placed, a ∈ B := by
  obtain ⟨lift, hplaced⟩ := ordered
  let B := sourceFiber lift.position (lift.position a)
  have ha : a ∈ B := by simp [B]
  have hB : B.Nonempty := ⟨a, ha⟩
  refine ⟨B, (mem_placedBlocks placed B).mpr ⟨hB, lift.position a, ?_⟩, ha⟩
  rw [hplaced]
  exact (placementOfMap_some_iff lift.position (lift.position a) B).mpr
    ⟨rfl, hB⟩

noncomputable def occupiedBlockKey
    (placed : Placement n (Finset (ZMod n)))
    (B : placedBlocks placed) : ℕ :=
  sourceBlockKey B.1 ((mem_placedBlocks placed B.1).mp B.2).1

theorem occupiedBlockKey_mem
    (placed : Placement n (Finset (ZMod n)))
    (B : placedBlocks placed) :
    ((occupiedBlockKey placed B : ℕ) : ZMod n) ∈ B.1 := by
  exact sourceBlockKey_mem B.1 ((mem_placedBlocks placed B.1).mp B.2).1

theorem occupiedBlockKey_lt
    (placed : Placement n (Finset (ZMod n)))
    (B : placedBlocks placed) : occupiedBlockKey placed B < n := by
  exact sourceBlockKey_lt B.1 ((mem_placedBlocks placed B.1).mp B.2).1

theorem occupiedBlockKey_injective
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    Function.Injective (occupiedBlockKey placed) := by
  intro B C hkey
  by_contra hne
  have hdisj := sourceOrdered_blocks_disjoint placed ordered B.1 C.1
    B.2 C.2 (by intro h; apply hne; exact Subtype.ext h)
  have hcontra := sourceBlockKey_injective_of_disjoint B.1 C.1
    ((mem_placedBlocks placed B.1).mp B.2).1
    ((mem_placedBlocks placed C.1).mp C.2).1 hdisj hkey
  exact hcontra

noncomputable def occupiedKeys
    (placed : Placement n (Finset (ZMod n))) : Finset ℕ :=
  Finset.univ.image (occupiedBlockKey placed)

theorem occupiedKeys_card
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    (occupiedKeys placed).card = (placedBlocks placed).card := by
  unfold occupiedKeys
  rw [Finset.card_image_of_injective _ (occupiedBlockKey_injective placed ordered)]
  simp

noncomputable def occupiedBlockKeyEquiv
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    (placedBlocks placed) ≃ (occupiedKeys placed) := by
  let f : (placedBlocks placed) → (occupiedKeys placed) := fun B =>
    ⟨occupiedBlockKey placed B,
      Finset.mem_image.mpr ⟨B, Finset.mem_univ _, rfl⟩⟩
  refine Equiv.ofBijective f ⟨?_, ?_⟩
  · intro B C h
    apply occupiedBlockKey_injective placed ordered
    exact congrArg Subtype.val h
  · intro k
    obtain ⟨B, _, hkey⟩ := Finset.mem_image.mp k.2
    refine ⟨B, ?_⟩
    apply Subtype.ext
    exact hkey

noncomputable def canonicalBlock
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (i : Fin (placedBlocks placed).card) : placedBlocks placed :=
  (occupiedBlockKeyEquiv placed ordered).symm
    ((occupiedKeys placed).orderIsoOfFin (occupiedKeys_card placed ordered) i)

theorem canonicalBlock_key
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (i : Fin (placedBlocks placed).card) :
    occupiedBlockKey placed (canonicalBlock placed ordered i) =
      ((occupiedKeys placed).orderIsoOfFin
        (occupiedKeys_card placed ordered) i).val := by
  have h := (occupiedBlockKeyEquiv placed ordered).apply_symm_apply
    ((occupiedKeys placed).orderIsoOfFin (occupiedKeys_card placed ordered) i)
  exact congrArg Subtype.val h

theorem canonicalBlock_key_strict
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (i j : Fin (placedBlocks placed).card) (hij : i < j) :
    occupiedBlockKey placed (canonicalBlock placed ordered i) <
      occupiedBlockKey placed (canonicalBlock placed ordered j) := by
  rw [canonicalBlock_key, canonicalBlock_key]
  exact (Finset.orderIsoOfFin (occupiedKeys placed)
    (occupiedKeys_card placed ordered)).strictMono hij

theorem canonicalBlock_bijective
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    Function.Bijective (canonicalBlock placed ordered) := by
  have h₁ : Function.Bijective
      ((occupiedKeys placed).orderIsoOfFin (occupiedKeys_card placed ordered)) :=
    (Finset.orderIsoOfFin (occupiedKeys placed)
      (occupiedKeys_card placed ordered)).bijective
  have h₂ : Function.Bijective (occupiedBlockKeyEquiv placed ordered).symm :=
    (occupiedBlockKeyEquiv placed ordered).symm.bijective
  exact h₂.comp h₁

theorem sourceOrdered_blocks_card_pos
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    0 < (placedBlocks placed).card := by
  obtain ⟨B, hB, _⟩ := sourceOrdered_blocks_cover placed ordered 0
  exact Finset.card_pos.mpr ⟨B, hB⟩

theorem sourceOrdered_block_site_unique
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed)
    (B : Finset (ZMod n)) (hB : B.Nonempty)
    (q q' : ZMod n) (hq : placed q = some B)
    (hq' : placed q' = some B) : q = q' := by
  obtain ⟨lift, hplaced⟩ := ordered
  obtain ⟨a, ha⟩ := hB
  have hfiberq := (placementOfMap_some_iff lift.position q B).mp
    (hplaced ▸ hq)
  have hfiberq' := (placementOfMap_some_iff lift.position q' B).mp
    (hplaced ▸ hq')
  have hposq := (mem_sourceFiber lift.position a q).mp
    (hfiberq.1.symm ▸ ha)
  have hposq' := (mem_sourceFiber lift.position a q').mp
    (hfiberq'.1.symm ▸ ha)
  exact hposq.symm.trans hposq'

noncomputable def occupiedBlockSite
    (placed : Placement n (Finset (ZMod n)))
    (B : Finset (ZMod n)) (hB : B ∈ placedBlocks placed) : ZMod n :=
  Classical.choose ((mem_placedBlocks placed B).mp hB).2

theorem occupiedBlockSite_spec
    (placed : Placement n (Finset (ZMod n)))
    (B : Finset (ZMod n)) (hB : B ∈ placedBlocks placed) :
    placed (occupiedBlockSite placed B hB) = some B :=
  Classical.choose_spec ((mem_placedBlocks placed B).mp hB).2

theorem canonicalBlock_zero_mem
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) :
    (0 : ZMod n) ∈
      (canonicalBlock placed ordered
        ⟨0, sourceOrdered_blocks_card_pos placed ordered⟩).1 := by
  obtain ⟨B, hB, hzero⟩ := sourceOrdered_blocks_cover placed ordered 0
  let block : placedBlocks placed := ⟨B, hB⟩
  have hkeyzero : occupiedBlockKey placed block = 0 := by
    have hle := sourceBlockKey_le B ((mem_placedBlocks placed B).mp hB).1 0 hzero
    simp only [ZMod.val_zero] at hle
    exact Nat.eq_zero_of_le_zero hle
  have hzeroKey : 0 ∈ occupiedKeys placed := by
    exact Finset.mem_image.mpr ⟨block, Finset.mem_univ _, hkeyzero⟩
  have hkeys_nonempty : (occupiedKeys placed).Nonempty := ⟨0, hzeroKey⟩
  have hmin : (occupiedKeys placed).min' hkeys_nonempty = 0 := by
    have hle := Finset.min'_le (occupiedKeys placed) 0 hzeroKey
    omega
  have hfirst : occupiedBlockKey placed
      (canonicalBlock placed ordered
        ⟨0, sourceOrdered_blocks_card_pos placed ordered⟩) = 0 := by
    rw [canonicalBlock_key]
    rw [Finset.coe_orderIsoOfFin_apply]
    exact (Finset.orderEmbOfFin_zero (occupiedKeys_card placed ordered)
      (sourceOrdered_blocks_card_pos placed ordered)).trans hmin
  have hmem := occupiedBlockKey_mem placed
    (canonicalBlock placed ordered
      ⟨0, sourceOrdered_blocks_card_pos placed ordered⟩)
  simpa [hfirst] using hmem

noncomputable def canonicalLegalNamed
    (base target : Placement n (Finset (ZMod n)))
    (orderedBase : SourceOrdered base) (orderedTarget : SourceOrdered target)
    (same : placedBlocks base = placedBlocks target)
    [NeZero (placedBlocks base).card] :
    LegalNamedPlacement n (placedBlocks base).card (ZMod n) := by
  let r := (placedBlocks base).card
  let enum : ZMod r → placedBlocks base := fun i =>
    canonicalBlock base orderedBase ((ZMod.finEquiv r).symm i)
  let site : ZMod r → ZMod n := fun i =>
    occupiedBlockSite target (enum i).1 (same ▸ (enum i).2)
  have hsite (i : ZMod r) : target (site i) = some (enum i).1 :=
    occupiedBlockSite_spec target (enum i).1 (same ▸ (enum i).2)
  refine {
    placed := target
    position := site
    block := fun i => (enum i).1
    position_injective := ?_
    placed_at := hsite
    only_named := ?_
    block_nonempty := ?_
    block_disjoint := ?_
    atom_covered := ?_ }
  · intro i j hij
    have hblocks : (enum i).1 = (enum j).1 := by
      exact Option.some.inj ((hsite i).symm.trans (hij ▸ hsite j))
    have hen : enum i = enum j := Subtype.ext hblocks
    have hfin := (canonicalBlock_bijective base orderedBase).1 hen
    exact (ZMod.finEquiv r).symm.injective hfin
  · intro q hq
    cases hvalue : target q with
    | none => exact (hq hvalue).elim
    | some B =>
        have hBne := (sourceOrdered_blocks_are_cyclic_arcs target
          orderedTarget q B hvalue).1
        have hBtarget : B ∈ placedBlocks target :=
          (mem_placedBlocks target B).mpr ⟨hBne, q, hvalue⟩
        have hBbase : B ∈ placedBlocks base := same.symm ▸ hBtarget
        obtain ⟨i, hi⟩ := (canonicalBlock_bijective base orderedBase).2
          (⟨B, hBbase⟩ : placedBlocks base)
        let j : ZMod r := ZMod.finEquiv r i
        have henum : enum j = ⟨B, hBbase⟩ := by
          simpa [enum, j] using hi
        refine ⟨j, ?_⟩
        have hj : target (site j) = some B := by simpa [henum] using hsite j
        exact (sourceOrdered_block_site_unique target orderedTarget B hBne
          (site j) q hj hvalue)
  · intro i
    exact ((mem_placedBlocks base (enum i).1).mp (enum i).2).1
  · intro i j hij
    have hen : enum i ≠ enum j := by
      intro heq
      have hfin := (canonicalBlock_bijective base orderedBase).1 heq
      exact hij ((ZMod.finEquiv r).symm.injective hfin)
    exact sourceOrdered_blocks_disjoint base orderedBase
      (enum i).1 (enum j).1 (enum i).2 (enum j).2
      (fun h => hen (Subtype.ext h))
  · intro a
    obtain ⟨B, hBtarget, ha⟩ := sourceOrdered_blocks_cover target orderedTarget a
    have hBbase : B ∈ placedBlocks base := same.symm ▸ hBtarget
    obtain ⟨i, hi⟩ := (canonicalBlock_bijective base orderedBase).2
      (⟨B, hBbase⟩ : placedBlocks base)
    refine ⟨ZMod.finEquiv r i, ?_⟩
    simpa [enum] using (hi.symm ▸ ha)

theorem finEquiv_symm_natCast {r : ℕ} [NeZero r]
    (k : ℕ) (hk : k < r) :
    (ZMod.finEquiv r).symm (k : ZMod r) = (⟨k, hk⟩ : Fin r) := by
  cases r with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ r =>
      apply Fin.ext
      change (k : ZMod (r + 1)).val = k
      simp [ZMod.val_natCast, Nat.mod_eq_of_lt hk]

theorem canonicalLegalNamed_block
    (base target : Placement n (Finset (ZMod n)))
    (orderedBase : SourceOrdered base) (orderedTarget : SourceOrdered target)
    (same : placedBlocks base = placedBlocks target)
    [NeZero (placedBlocks base).card]
    (i : ZMod (placedBlocks base).card) :
    (canonicalLegalNamed base target orderedBase orderedTarget same).block i =
      (canonicalBlock base orderedBase
        ((ZMod.finEquiv (placedBlocks base).card).symm i)).1 := rfl

theorem canonicalLegalNamed_position
    (base target : Placement n (Finset (ZMod n)))
    (orderedBase : SourceOrdered base) (orderedTarget : SourceOrdered target)
    (same : placedBlocks base = placedBlocks target)
    [NeZero (placedBlocks base).card]
    (i : ZMod (placedBlocks base).card) :
    (canonicalLegalNamed base target orderedBase orderedTarget same).position i =
      occupiedBlockSite target
        (canonicalBlock base orderedBase
          ((ZMod.finEquiv (placedBlocks base).card).symm i)).1
        (same ▸ (canonicalBlock base orderedBase
          ((ZMod.finEquiv (placedBlocks base).card).symm i)).2) := rfl

theorem canonicalLegalNamed_positive
    (base target : Placement n (Finset (ZMod n)))
    (orderedBase : SourceOrdered base) (orderedTarget : SourceOrdered target)
    (same : placedBlocks base = placedBlocks target)
    [NeZero (placedBlocks base).card] :
    (canonicalLegalNamed base target orderedBase orderedTarget same).PositivelyOrdered := by
  let r := (placedBlocks base).card
  let named := canonicalLegalNamed base target orderedBase orderedTarget same
  have hrpos : 0 < r := sourceOrdered_blocks_card_pos base orderedBase
  have hzero : (0 : ZMod n) ∈ named.block 0 := by
    change (0 : ZMod n) ∈
      (canonicalLegalNamed base target orderedBase orderedTarget same).block 0
    rw [canonicalLegalNamed_block]
    have hidx0 : (ZMod.finEquiv r).symm (0 : ZMod r) = ⟨0, hrpos⟩ := by
      have h := finEquiv_symm_natCast (r := r) 0 hrpos
      simpa only [Nat.cast_zero] using h
    rw [hidx0]
    exact canonicalBlock_zero_mem base orderedBase
  intro k hk
  by_cases hnext : k + 1 < r
  · have hidxk : (ZMod.finEquiv (placedBlocks base).card).symm
        (k : ZMod (placedBlocks base).card) =
        (⟨k, hk⟩ : Fin (placedBlocks base).card) :=
      finEquiv_symm_natCast k hk
    have hidxnext : (ZMod.finEquiv (placedBlocks base).card).symm
        ((k + 1 : ℕ) : ZMod (placedBlocks base).card) =
        (⟨k + 1, hnext⟩ : Fin (placedBlocks base).card) :=
      finEquiv_symm_natCast (k + 1) hnext
    have hkey : sourceBlockKey (named.block (k : ZMod r))
        (named.block_nonempty (k : ZMod r)) <
        sourceBlockKey (named.block ((k + 1 : ℕ) : ZMod r))
          (named.block_nonempty ((k + 1 : ℕ) : ZMod r)) := by
      simpa only [named, canonicalLegalNamed_block,
        hidxk, hidxnext,
        occupiedBlockKey] using
        (canonicalBlock_key_strict base orderedBase
          ⟨k, hk⟩ ⟨k + 1, hnext⟩ (by simp))
    have hB₀ : named.block 0 ∈ placedBlocks target := by
      have h : (canonicalBlock base orderedBase ⟨0, hrpos⟩).1 ∈
          placedBlocks target := same ▸ (canonicalBlock base orderedBase ⟨0, hrpos⟩).2
      simpa [named, canonicalLegalNamed_block, finEquiv_symm_natCast 0 hrpos] using h
    have hB : named.block (k : ZMod r) ∈ placedBlocks target := by
      have h : (canonicalBlock base orderedBase ⟨k, hk⟩).1 ∈
          placedBlocks target := same ▸ (canonicalBlock base orderedBase ⟨k, hk⟩).2
      simpa [named, canonicalLegalNamed_block, hidxk] using h
    have hC : named.block ((k + 1 : ℕ) : ZMod r) ∈ placedBlocks target := by
      have h : (canonicalBlock base orderedBase ⟨k + 1, hnext⟩).1 ∈
          placedBlocks target := same ▸
            (canonicalBlock base orderedBase ⟨k + 1, hnext⟩).2
      simpa only [named, canonicalLegalNamed_block, hidxnext] using h
    have hpos := sourceOrdered_block_key_offsets target orderedTarget
      (named.position 0) (named.position (k : ZMod r))
      (named.position ((k + 1 : ℕ) : ZMod r))
      (named.block 0) (named.block (k : ZMod r))
      (named.block ((k + 1 : ℕ) : ZMod r))
      (named.placed_at 0) hzero
      (named.placed_at (k : ZMod r))
      (named.placed_at ((k + 1 : ℕ) : ZMod r))
      (named.block_nonempty (k : ZMod r))
      (named.block_nonempty ((k + 1 : ℕ) : ZMod r)) hkey
    change named.offset k < named.offset (k + 1)
    have hnext' : k + 1 < (placedBlocks base).card := hnext
    simpa [LegalNamedPlacement.offset, hk, hnext'] using hpos
  · have hend : k + 1 = r := by omega
    have hlt : (named.position (k : ZMod r) - named.position 0).val < n :=
      ZMod.val_lt _
    change named.offset k < named.offset (k + 1)
    rw [hend, named.offset_end]
    simpa only [LegalNamedPlacement.offset, if_pos hk] using hlt

/-- Common atom blocks are named by their first source atom. Two independent
lift certificates therefore induce the same positive block cycle. -/
theorem sourceOrdered_same_blocks_admit
    (first second : Placement n (Finset (ZMod n)))
    (ordered₁ : SourceOrdered first) (ordered₂ : SourceOrdered second)
    (same : placedBlocks first = placedBlocks second)
    [NeZero (placedBlocks first).card] :
    SameOrientedBlockCycle (r := (placedBlocks first).card) first second := by
  let a := canonicalLegalNamed first first ordered₁ ordered₁ rfl
  let b := canonicalLegalNamed first second ordered₁ ordered₂ same
  refine ⟨a, b, rfl, rfl, ?_⟩
  refine ⟨?_, canonicalLegalNamed_positive first first ordered₁ ordered₁ rfl,
    canonicalLegalNamed_positive first second ordered₁ ordered₂ same⟩
  funext i
  simp only [a, b, canonicalLegalNamed_block]

/-- Lemma 2.2 can be applied directly to two source-ordered placements with
the same actual atom blocks; no lift is used to choose the block names. -/
theorem realize_source_ordered_same_blocks
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n)))
    (orderedSource : SourceOrdered s.placed)
    (orderedTarget : SourceOrdered target)
    (same : placedBlocks s.placed = placedBlocks target)
    (hn : 2 ≤ n) :
    ∃ word : List Letter,
      run F s word = { s with placed := target } ∧
      FusionFree F s word := by
  let r := (placedBlocks s.placed).card
  have hrpos : 0 < r := sourceOrdered_blocks_card_pos s.placed orderedSource
  haveI : NeZero r := ⟨by omega⟩
  have hadmit := sourceOrdered_same_blocks_admit
    s.placed target orderedSource orderedTarget same
  by_cases hr : 2 ≤ r
  · exact realize_same_oriented_block_cycle F s s.placed target hn hr rfl hadmit
  · have hr1 : r = 1 := by omega
    change SameOrientedBlockCycle (r := r) s.placed target at hadmit
    have hsingleCycle : SameOrientedBlockCycle (r := 1) s.placed target := by
      simpa only [hr1] using hadmit
    obtain ⟨a, b, ha, hb, hblocks, _, _⟩ := hsingleCycle
    have hone : SameSingleBlock s.placed target := by
      exact ⟨a, b, ha, hb, hblocks⟩
    exact realize_same_single_block_cycle F s s.placed target rfl hone

end RegisteredAbsorptionChains
