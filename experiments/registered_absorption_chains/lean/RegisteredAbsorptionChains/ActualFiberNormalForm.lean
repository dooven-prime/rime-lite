import RegisteredAbsorptionChains.FiberFullSufficiency
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The code recovered from an actual registered chain names its physical
carrier, not merely a formal source set. No clean-outside hypothesis is used. -/
theorem actual_code_carrier_at_site
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn) :
    ∃ q : ZMod n,
      (run (selectedPair n) (singletonExecution n) word).placed q =
        some (decodedCarrier c hn) := by
  let s := run (selectedPair n) (singletonExecution n) word
  rcases actual_decoded_trace_run word hn with hpre |
    ⟨c', j, hj, hsuffix, _, hprefixChain, hprefixRead, _, hcarrier⟩
  · simp [hpre.1] at hregistered
  · have hskip := decodeCodePrefix_skip c' hn j hj (n - 2) (le_refl _)
      (by omega) (by
        intro i hji _
        exact hsuffix i hji)
    have hcode : c' = c := by
      apply decodeChain_injective hn
      exact (hskip.2.trans hprefixChain.symm).trans hchain
    obtain ⟨q, C, hsite, _, hread⟩ := hcarrier
    have hC : C = (decodeCodePrefix c' hn j hj).frontier.carrier := by
      exact Option.some.inj (hread.symm.trans hprefixRead)
    refine ⟨q, ?_⟩
    have hfull : (decodeCode c' hn).frontier.carrier =
        (decodeCodePrefix c' hn j hj).frontier.carrier :=
      congrArg CheckpointSourceFrontier.carrier hskip.1
    have hCfull : C = (decodeCode c hn).frontier.carrier := by
      simpa [hcode] using hC.trans hfull.symm
    simpa [s, decodedCarrier, hCfull] using hsite

/-- Every actual packet outside the decoded carrier is a nonempty linear
source interval inside the decoded complement. -/
theorem actual_code_outside_block_interval
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn)
    (q : ZMod n) (B : Finset (ZMod n))
    (hB : (run (selectedPair n) (singletonExecution n) word).placed q = some B)
    (hne : B ≠ decodedCarrier c hn) :
    ∃ lo hi : ℕ,
      (decodeCode c hn).frontier.lo ≤ lo ∧ lo < hi ∧
      hi ≤ (decodeCode c hn).frontier.hi ∧
      B = sourceInterval lo hi := by
  let s := run (selectedPair n) (singletonExecution n) word
  let f := (decodeCode c hn).frontier
  obtain ⟨qC, hC⟩ := actual_code_carrier_at_site word hn c hregistered hchain
  have hdistinct : qC ≠ q := by
    intro heq
    exact hne (Option.some.inj (hB.symm.trans (heq ▸ hC)))
  have hordered : SourceOrdered s.placed :=
    reachable_source_ordered (selectedPair n) s.placed hn ⟨word, rfl⟩
  obtain ⟨hBne, hlinear, hsubset⟩ :=
    actual_outside_packet_linear s f.carrier B qC q hordered hdistinct
      hC hB (by simp [CheckpointSourceFrontier.carrier, selectedPair])
  obtain ⟨lo, hi, hlohi, hhin, hinterval⟩ :=
    nonempty_linear_set_eq_sourceInterval B hBne hlinear
  have hlo : f.lo ≤ lo := by
    have hmem : (lo : ZMod n) ∈ B := by
      rw [hinterval, mem_sourceInterval_iff lo hi hhin]
      simpa [ZMod.val_natCast_of_lt (by omega : lo < n)] using
        (show lo ≤ lo ∧ lo < hi by omega)
    have hrem : (lo : ZMod n) ∈ f.remaining :=
      (f.not_mem_carrier_iff_remaining _).mp
        (Finset.mem_sdiff.mp (hsubset hmem)).2
    have := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp hrem
    simpa [ZMod.val_natCast_of_lt (by omega : lo < n)] using this.1
  have hhi : hi ≤ f.hi := by
    have hlast : hi - 1 < n := by omega
    have hmem : ((hi - 1 : ℕ) : ZMod n) ∈ B := by
      rw [hinterval, mem_sourceInterval_iff lo hi hhin]
      simpa [ZMod.val_natCast_of_lt hlast] using
        (show lo ≤ hi - 1 ∧ hi - 1 < hi by omega)
    have hrem : ((hi - 1 : ℕ) : ZMod n) ∈ f.remaining :=
      (f.not_mem_carrier_iff_remaining _).mp
        (Finset.mem_sdiff.mp (hsubset hmem)).2
    have := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp hrem
    have hval : ((hi - 1 : ℕ) : ZMod n).val = hi - 1 :=
      ZMod.val_natCast_of_lt hlast
    rw [hval] at this
    omega
  exact ⟨lo, hi, hlo, hlohi, hhi, hinterval⟩

/-- The source-key naming of an actual state starts at its decoded carrier
and has at least one outside packet whenever the complement is nonempty. -/
theorem actual_code_canonical_named
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn)
    (hremaining :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    ∃ (r : ℕ) (hr : NeZero r),
      letI : NeZero r := hr
      ∃ named : LegalNamedPlacement n r (ZMod n),
        2 ≤ r ∧
        named.placed =
          (run (selectedPair n) (singletonExecution n) word).placed ∧
        named.block 0 = decodedCarrier c hn ∧
        named.PositivelyOrdered ∧
        StrictMono (fun i : Fin r =>
          sourceBlockKey (named.block (i.val : ZMod r))
            (named.block_nonempty (i.val : ZMod r))) := by
  let s := run (selectedPair n) (singletonExecution n) word
  let f := (decodeCode c hn).frontier
  have hfremaining : f.lo < f.hi := hremaining
  have hordered : SourceOrdered s.placed :=
    reachable_source_ordered (selectedPair n) s.placed hn ⟨word, rfl⟩
  obtain ⟨qC, hC⟩ := actual_code_carrier_at_site word hn c hregistered hchain
  have hCne : f.carrier.Nonempty := by
    refine ⟨0, ?_⟩
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hCmem : f.carrier ∈ placedBlocks s.placed :=
    (mem_placedBlocks s.placed f.carrier).mpr ⟨hCne, qC, hC⟩
  have hlo_n : f.lo < n := by
    have := f.hi_valid
    omega
  have hrem : (f.lo : ZMod n) ∈ f.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simpa [ZMod.val_natCast_of_lt hlo_n] using
      (show f.lo ≤ f.lo ∧ f.lo < f.hi by omega)
  obtain ⟨B, hBmem, haB⟩ :=
    sourceOrdered_blocks_cover s.placed hordered (f.lo : ZMod n)
  have hBne : B ≠ f.carrier := by
    intro heq
    have haC : (f.lo : ZMod n) ∈ f.carrier := heq ▸ haB
    exact (f.not_mem_carrier_iff_remaining _).mpr hrem haC
  let r := (placedBlocks s.placed).card
  have hr2 : 2 ≤ r := by
    have hlt : 1 < (placedBlocks s.placed).card :=
      Finset.one_lt_card.mpr ⟨B, hBmem, f.carrier, hCmem, hBne⟩
    omega
  letI : NeZero r := ⟨by omega⟩
  let named := canonicalLegalNamed s.placed s.placed hordered hordered rfl
  have hcarrier : named.block 0 = f.carrier :=
    canonical_named_carrier s hordered f.carrier ⟨qC, hC⟩
      (by simp [CheckpointSourceFrontier.carrier, selectedPair])
  have hkeys : StrictMono (fun i : Fin r =>
      sourceBlockKey (named.block (i.val : ZMod r))
        (named.block_nonempty (i.val : ZMod r))) := by
    intro i j hij
    have h := canonicalBlock_key_strict s.placed hordered i j hij
    have hii : (ZMod.finEquiv r).symm (i.val : ZMod r) = i := by
      simpa using finEquiv_symm_natCast i.val i.isLt
    have hjj : (ZMod.finEquiv r).symm (j.val : ZMod r) = j := by
      simpa using finEquiv_symm_natCast j.val j.isLt
    change sourceBlockKey
      ((canonicalBlock s.placed hordered
        ((ZMod.finEquiv r).symm (i.val : ZMod r))).1) _ <
      sourceBlockKey
      ((canonicalBlock s.placed hordered
        ((ZMod.finEquiv r).symm (j.val : ZMod r))).1) _
    simpa only [hii, hjj, occupiedBlockKey] using h
  exact ⟨r, inferInstance, named, hr2, rfl, hcarrier,
    canonicalLegalNamed_positive s.placed s.placed hordered hordered rfl,
    hkeys⟩

variable {r : ℕ} [NeZero r]

/-- The least source address in a named packet. -/
noncomputable def namedSourceKey
    (named : LegalNamedPlacement n r (ZMod n)) (i : Fin r) : ℕ :=
  sourceBlockKey (named.block (i.val : ZMod r))
    (named.block_nonempty (i.val : ZMod r))

theorem namedSourceKey_mem
    (named : LegalNamedPlacement n r (ZMod n)) (i : Fin r) :
    (namedSourceKey named i : ZMod n) ∈
      named.block (i.val : ZMod r) :=
  sourceBlockKey_mem _ _

theorem namedSourceKey_le
    (named : LegalNamedPlacement n r (ZMod n)) (i : Fin r)
    (a : ZMod n) (ha : a ∈ named.block (i.val : ZMod r)) :
    namedSourceKey named i ≤ a.val :=
  sourceBlockKey_le _ _ a ha

/-- Canonical source-key naming is strictly increasing at the integer
indices. This uses the source-only block keys, not physical sites. -/
theorem canonical_namedSourceKey_strict
    (P : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered P)
    [NeZero (placedBlocks P).card] :
    StrictMono (namedSourceKey
      (canonicalLegalNamed P P ordered ordered rfl)) := by
  intro i j hij
  have h := canonicalBlock_key_strict P ordered i j hij
  simpa only [namedSourceKey, canonicalLegalNamed_block,
    finEquiv_symm_natCast i.val i.isLt,
    finEquiv_symm_natCast j.val j.isLt,
    occupiedBlockKey] using h

/-- Pure interval-partition interface obtained from one actual state. -/
structure OrderedOutsideNaming
    (f : CheckpointSourceFrontier n)
    (named : LegalNamedPlacement n r (ZMod n)) : Prop where
  count : 2 ≤ r
  carrier : named.block 0 = f.carrier
  key_strict : StrictMono (namedSourceKey named)
  linear : ∀ i : Fin r, 0 < i.val →
    LinearSourceConvex (named.block (i.val : ZMod r))
  remaining : ∀ i : Fin r, 0 < i.val →
    named.block (i.val : ZMod r) ⊆ f.remaining

/-- An actual source-ordered endpoint supplies the interval-partition
interface without assuming that its outside packets are singletons. -/
theorem actual_code_ordered_outside_naming
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn)
    (hremaining :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    ∃ (r : ℕ) (hr : NeZero r),
      letI : NeZero r := hr
      ∃ named : LegalNamedPlacement n r (ZMod n),
        named.placed =
          (run (selectedPair n) (singletonExecution n) word).placed ∧
        named.PositivelyOrdered ∧
        OrderedOutsideNaming (decodeCode c hn).frontier named := by
  obtain ⟨r, hr, named, hr2, hplaced, hcarrier, hpositive, hkeys⟩ :=
    actual_code_canonical_named word hn c hregistered hchain hremaining
  letI : NeZero r := hr
  let s := run (selectedPair n) (singletonExecution n) word
  let f := (decodeCode c hn).frontier
  have hordered : SourceOrdered s.placed :=
    reachable_source_ordered (selectedPair n) s.placed hn ⟨word, rfl⟩
  have hstrict : StrictMono (namedSourceKey named) := hkeys
  have hout (i : Fin r) (hi : 0 < i.val) :
      LinearSourceConvex (named.block (i.val : ZMod r)) ∧
        named.block (i.val : ZMod r) ⊆ f.remaining := by
    have hi0 : (i.val : ZMod r) ≠ 0 := by
      intro heq
      have hv := congrArg ZMod.val heq
      rw [ZMod.val_natCast_of_lt i.isLt, ZMod.val_zero] at hv
      omega
    have hsites : named.position (i.val : ZMod r) ≠ named.position 0 :=
      named.position_injective.ne hi0
    have hC : s.placed (named.position 0) = some f.carrier := by
      rw [← hplaced]
      change named.block 0 = f.carrier at hcarrier
      simpa only [hcarrier] using named.placed_at 0
    have hB : s.placed (named.position (i.val : ZMod r)) =
        some (named.block (i.val : ZMod r)) := by
      rw [← hplaced]
      exact named.placed_at _
    obtain ⟨_, hlinear, hsubset⟩ :=
      actual_outside_packet_linear s f.carrier
        (named.block (i.val : ZMod r))
        (named.position 0) (named.position (i.val : ZMod r))
        hordered hsites.symm hC hB
        (by simp [CheckpointSourceFrontier.carrier, selectedPair])
    refine ⟨hlinear, ?_⟩
    intro a ha
    exact (f.not_mem_carrier_iff_remaining a).mp
      (Finset.mem_sdiff.mp (hsubset ha)).2
  refine ⟨r, hr, named, hplaced, hpositive, ⟨hr2, hcarrier, hstrict, ?_, ?_⟩⟩
  · intro i hi
    exact (hout i hi).1
  · intro i hi
    exact (hout i hi).2

theorem OrderedOutsideNaming.key_bounds
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (i : Fin r) (hi : 0 < i.val) :
    f.lo ≤ namedSourceKey named i ∧ namedSourceKey named i < f.hi := by
  have hmem := h.remaining i hi (namedSourceKey_mem named i)
  have hval :=
    (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp hmem
  have hlt : namedSourceKey named i < n :=
    sourceBlockKey_lt _ _
  simpa [CheckpointSourceFrontier.remaining,
    ZMod.val_natCast_of_lt hlt] using hval

theorem OrderedOutsideNaming.key_first
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (hremaining : f.lo < f.hi) :
    namedSourceKey named ⟨1, by have := h.count; omega⟩ = f.lo := by
  have hr2 := h.count
  have hlo_n : f.lo < n := by
    have := f.hi_valid
    omega
  have hlo_rem : (f.lo : ZMod n) ∈ f.remaining := by
    rw [CheckpointSourceFrontier.remaining,
      mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simpa [ZMod.val_natCast_of_lt hlo_n] using
      (show f.lo ≤ f.lo ∧ f.lo < f.hi by omega)
  obtain ⟨j, hj⟩ := named.atom_covered (f.lo : ZMod n)
  have hjpos : 0 < j.val := by
    by_contra hnot
    have hj0 : j = 0 := ZMod.val_injective r (by
      simpa only [ZMod.val_zero] using Nat.eq_zero_of_not_pos hnot)
    have hcarrier : (f.lo : ZMod n) ∈ f.carrier := by
      simpa [hj0, h.carrier] using hj
    exact (f.not_mem_carrier_iff_remaining _).mpr hlo_rem hcarrier
  let ij : Fin r := ⟨j.val, j.val_lt⟩
  let one : Fin r := ⟨1, by omega⟩
  have hjblock : named.block (ij.val : ZMod r) = named.block j := by
    simp [ij, ZMod.natCast_zmod_val]
  have hkey_le : namedSourceKey named ij ≤ f.lo := by
    have hle := namedSourceKey_le named ij (f.lo : ZMod n)
      (by simpa [hjblock] using hj)
    simpa [ZMod.val_natCast_of_lt hlo_n] using hle
  have hkey_ge := (h.key_bounds ij hjpos).1
  have hkeyeq : namedSourceKey named ij = f.lo := by omega
  have hjone : j.val = 1 := by
    by_contra hnot
    have hjgt : 1 < j.val := by omega
    have hstrict := h.key_strict
      (show one < ij from Fin.mk_lt_mk.mpr hjgt)
    have hfirst_ge := (h.key_bounds one (by simp [one])).1
    omega
  have hij : ij = one := Fin.ext hjone
  simpa [hij, one] using hkeyeq

noncomputable def OrderedOutsideNaming.upper
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named) (i : Fin r) : ℕ :=
  if hi : i.val + 1 < r then
    namedSourceKey named ⟨i.val + 1, hi⟩ else f.hi

theorem OrderedOutsideNaming.key_lt_upper
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (i : Fin r) (hi : 0 < i.val) :
    namedSourceKey named i < h.upper i ∧ h.upper i ≤ f.hi := by
  unfold OrderedOutsideNaming.upper
  split_ifs with hnext
  · have hlt := h.key_strict
      (show i < (⟨i.val + 1, hnext⟩ : Fin r) from
        Fin.mk_lt_mk.mpr (by omega))
    have hpositive : 0 < i.val + 1 := by omega
    have hbound := (h.key_bounds ⟨i.val + 1, hnext⟩ hpositive).2
    omega
  · have hbound := (h.key_bounds i hi).2
    omega

/-- Between consecutive source keys there is exactly one outside packet.
Disjointness and convexity rule out overlap; atom coverage rules out gaps. -/
theorem OrderedOutsideNaming.block_eq_interval
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (i : Fin r) (hi : 0 < i.val) :
    named.block (i.val : ZMod r) =
      sourceInterval (namedSourceKey named i) (h.upper i) := by
  have hkey := h.key_bounds i hi
  have hu := h.key_lt_upper i hi
  have hupperN : h.upper i ≤ n := hu.2.trans f.hi_valid
  ext a
  rw [mem_sourceInterval_iff _ _ hupperN]
  constructor
  · intro ha
    have hlow : namedSourceKey named i ≤ a.val :=
      namedSourceKey_le named i a ha
    have hrem :=
      (mem_sourceInterval_iff f.lo f.hi f.hi_valid a).mp
        (h.remaining i hi ha)
    refine ⟨hlow, ?_⟩
    by_cases hnext : i.val + 1 < r
    · let j : Fin r := ⟨i.val + 1, hnext⟩
      have hkeylt : namedSourceKey named i < namedSourceKey named j :=
        h.key_strict (Fin.mk_lt_mk.mpr (by simp [j]))
      have hkeyn : namedSourceKey named j < n := by
        have := (h.key_bounds j (by simp [j])).2
        have := f.hi_valid
        omega
      have hneq : (i.val : ZMod r) ≠ (j.val : ZMod r) := by
        intro heq
        have hv := congrArg ZMod.val heq
        rw [ZMod.val_natCast_of_lt i.isLt,
          ZMod.val_natCast_of_lt j.isLt] at hv
        change i.val = i.val + 1 at hv
        omega
      have hlt : a.val < namedSourceKey named j := by
        by_contra hnot
        have hbetween :
            (namedSourceKey named j : ZMod n) ∈
              named.block (i.val : ZMod r) :=
          h.linear i hi (namedSourceKey named i)
            (namedSourceKey named j) a.val
            hkeylt.le (by omega) a.val_lt
            (namedSourceKey_mem named i)
            (by simpa only [ZMod.natCast_zmod_val] using ha)
        exact (Finset.disjoint_left.mp
          (named.block_disjoint _ _ hneq)) hbetween
            (namedSourceKey_mem named j)
      simpa [OrderedOutsideNaming.upper, hnext, j] using hlt
    · simpa [OrderedOutsideNaming.upper, hnext] using hrem.2
  · rintro ⟨halow, haupper⟩
    have harem : a ∈ f.remaining := by
      rw [CheckpointSourceFrontier.remaining,
        mem_sourceInterval_iff f.lo f.hi f.hi_valid]
      have := h.key_bounds i hi
      have := (h.key_lt_upper i hi).2
      omega
    obtain ⟨j, hj⟩ := named.atom_covered a
    let jj : Fin r := ⟨j.val, j.val_lt⟩
    have hjblock : a ∈ named.block (jj.val : ZMod r) := by
      simpa [jj] using hj
    have hjpos : 0 < jj.val := by
      by_contra hnot
      have hjzero : j = 0 := ZMod.val_injective r (by
        simpa only [ZMod.val_zero] using Nat.eq_zero_of_not_pos hnot)
      have haC : a ∈ f.carrier := by
        simpa [jj, hjzero, h.carrier] using hj
      exact (f.not_mem_carrier_iff_remaining a).mpr harem haC
    by_cases heq : jj = i
    · simpa [heq] using hjblock
    rcases lt_or_gt_of_ne heq with hbefore | hafter
    · have hless : namedSourceKey named jj < namedSourceKey named i :=
        h.key_strict hbefore
      have hbetween : (namedSourceKey named i : ZMod n) ∈
          named.block (jj.val : ZMod r) :=
        h.linear jj hjpos (namedSourceKey named jj)
          (namedSourceKey named i) a.val hless.le halow
          a.val_lt (namedSourceKey_mem named jj)
          (by simpa only [ZMod.natCast_zmod_val] using hjblock)
      have hneq : (jj.val : ZMod r) ≠ (i.val : ZMod r) := by
        intro hcast
        apply heq
        apply Fin.ext
        have hv := congrArg ZMod.val hcast
        simpa [ZMod.val_natCast_of_lt jj.isLt,
          ZMod.val_natCast_of_lt i.isLt] using hv
      exact False.elim ((Finset.disjoint_left.mp
        (named.block_disjoint _ _ hneq)) hbetween
          (namedSourceKey_mem named i))
    · have hnext : i.val + 1 < r := by
        have := jj.isLt
        omega
      let next : Fin r := ⟨i.val + 1, hnext⟩
      have hnextle : next ≤ jj := Fin.mk_le_mk.mpr (by
        have hv : i.val < jj.val := hafter
        change i.val + 1 ≤ j.val
        change i.val < j.val at hv
        omega)
      have hkeyle : namedSourceKey named next ≤ namedSourceKey named jj :=
        h.key_strict.monotone hnextle
      have hkeya := namedSourceKey_le named jj a hjblock
      have hupper : h.upper i = namedSourceKey named next := by
        simp [OrderedOutsideNaming.upper, hnext, next]
      omega

/-- Cut zero precedes the first outside packet; cut `j` thereafter is the
source key of the next packet, or the complement endpoint at the end. -/
noncomputable def OrderedOutsideNaming.cut
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (_h : OrderedOutsideNaming f named) (j : ℕ) : ℕ :=
  if hj : j + 1 < r then
    namedSourceKey named ⟨j + 1, hj⟩ else f.hi

theorem OrderedOutsideNaming.cut_zero
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named) (hremaining : f.lo < f.hi) :
    h.cut 0 = f.lo := by
  have hr2 := h.count
  change (if hj : 1 < r then
    namedSourceKey named ⟨1, hj⟩ else f.hi) = f.lo
  rw [dif_pos (by omega : 1 < r)]
  exact h.key_first hremaining

theorem OrderedOutsideNaming.cut_last
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named) :
    h.cut (r - 1) = f.hi := by
  have hr2 := h.count
  simp [OrderedOutsideNaming.cut, show ¬ r - 1 + 1 < r by omega]

theorem OrderedOutsideNaming.cut_step
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (i : ℕ) (hi : i + 1 < r) : h.cut i < h.cut (i + 1) := by
  by_cases hnext : i + 2 < r
  · have hkey := h.key_strict
      (show (⟨i + 1, hi⟩ : Fin r) < ⟨i + 2, hnext⟩ from
        Fin.mk_lt_mk.mpr (by omega))
    simpa [OrderedOutsideNaming.cut, hi, hnext] using hkey
  · have hpos : 0 < (⟨i + 1, hi⟩ : Fin r).val := by
      change 0 < i + 1
      omega
    have hkey := (h.key_bounds ⟨i + 1, hi⟩ hpos).2
    simpa [OrderedOutsideNaming.cut, hi, hnext] using hkey

noncomputable def OrderedOutsideNaming.toCutNamed
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : OrderedOutsideNaming f named)
    (hremaining : f.lo < f.hi) : CutNamed f named := by
  refine {
    count := h.count
    carrier := h.carrier
    cut := h.cut
    cut_zero := h.cut_zero hremaining
    cut_last := h.cut_last
    cut_step := h.cut_step
    outside := ?_
  }
  intro i hi hir
  let idx : Fin r := ⟨i, hir⟩
  have hblock := h.block_eq_interval idx (by
    change 0 < i
    omega)
  have hstart : h.cut (i - 1) = namedSourceKey named idx := by
    have hidx : i - 1 + 1 = i := by omega
    simp [OrderedOutsideNaming.cut, hidx, hir, idx]
  have hend : h.cut i = h.upper idx := by
    simp [OrderedOutsideNaming.cut, OrderedOutsideNaming.upper, idx]
  simpa [idx, hstart, hend] using hblock

/-- The physical offsets of a positively ordered naming are strictly
increasing on its occupied indices. -/
theorem namedOffset_strict
    {named : LegalNamedPlacement n r (ZMod n)}
    (hpositive : named.PositivelyOrdered) :
    StrictMono (fun i : Fin r => named.offset i.val) := by
  have aux : ∀ j : ℕ, j < r → ∀ i : ℕ, i < j →
      named.offset i < named.offset j := by
    intro j hj
    induction j with
    | zero =>
        intro i hi
        omega
    | succ j ih =>
        intro i hi
        by_cases hij : i = j
        · subst i
          exact hpositive j (by omega)
        · exact (ih (by omega) i (by omega)).trans
            (hpositive j (by omega))
  intro i j hij
  exact aux j.val j.isLt i.val hij

/-- A source cut together with the actual positive physical order gives
the complete cut/occupied-site/carrier-phase parameter. -/
noncomputable def CutNamed.toValidFiberPlacement
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n (t + 1) (ZMod n)}
    (h : CutNamed f named) (hpositive : named.PositivelyOrdered)
    (hremaining : f.lo < f.hi) : ValidFiberPlacement n t := by
  have ht : 0 < t := by have := h.count; omega
  refine {
    ht := ht
    u := f.lo
    v := f.hi
    hu := by have := f.lo_valid; omega
    huv := hremaining
    hvn := f.hi_valid
    cut := fun i => h.cut i.val
    cut_zero := h.cut_zero
    cut_last := by simpa using h.cut_last
    cut_strict := h.cutFin_strict
    q := named.position 0
    offset := fun i => named.offset i.val
    offset_zero := named.offset_zero
    offset_strict := namedOffset_strict hpositive
    offset_lt := ?_
  }
  intro i
  simp only [LegalNamedPlacement.offset, if_pos i.isLt]
  exact ZMod.val_lt _

theorem CutNamed.toValidFiberPlacement_siteFin
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n (t + 1) (ZMod n)}
    (h : CutNamed f named) (hpositive : named.PositivelyOrdered)
    (hremaining : f.lo < f.hi) (i : Fin (t + 1)) :
    (h.toValidFiberPlacement hpositive hremaining).siteFin i =
      named.position (i.val : ZMod (t + 1)) := by
  simpa [CutNamed.toValidFiberPlacement, ValidFiberPlacement.siteFin]
    using (named.position_offset i.val i.isLt).symm

theorem CutNamed.toValidFiberPlacement_blockFin
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n (t + 1) (ZMod n)}
    (h : CutNamed f named) (hpositive : named.PositivelyOrdered)
    (hremaining : f.lo < f.hi) (i : Fin (t + 1)) :
    (h.toValidFiberPlacement hpositive hremaining).blockFin i =
      named.block (i.val : ZMod (t + 1)) := by
  let data := h.toValidFiberPlacement hpositive hremaining
  by_cases hi : i.val = 0
  · have hcarrier : data.carrier = f.carrier :=
      fiber_carrier_eq_frontier f data rfl rfl
    simpa [ValidFiberPlacement.blockFin, hi, hcarrier, data]
      using h.carrier.symm
  · have hipos : 1 ≤ i.val := by omega
    have hi' : i.val < t + 1 := i.isLt
    have hout := h.outside i.val hipos hi'
    have hsub : i.val - 1 + 1 = i.val := by omega
    have houts : data.outside ⟨i.val - 1, by omega⟩ =
        sourceInterval (h.cut (i.val - 1)) (h.cut i.val) := by
      simpa [data, CutNamed.toValidFiberPlacement, hsub] using
        data.outside_eq_sourceInterval ⟨i.val - 1, by omega⟩
    simpa [ValidFiberPlacement.blockFin, hi, houts, data] using hout.symm

theorem CutNamed.toValidFiberPlacement_target
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n (t + 1) (ZMod n)}
    (h : CutNamed f named) (hpositive : named.PositivelyOrdered)
    (hremaining : f.lo < f.hi) :
    (h.toValidFiberPlacement hpositive hremaining).target = named.placed := by
  let data := h.toValidFiberPlacement hpositive hremaining
  funext q
  by_cases hoccupied : named.placed q = none
  · have htarget : data.target q = none := by
      by_contra hnot
      obtain ⟨i, hi⟩ := data.target_only_sites q hnot
      have hsite := h.toValidFiberPlacement_siteFin hpositive hremaining i
      change data.siteFin i = named.position (i.val : ZMod (t + 1)) at hsite
      have hnamed : named.placed q =
          some (named.block (i.val : ZMod (t + 1))) := by
        rw [← hi, hsite]
        exact named.placed_at _
      rw [hoccupied] at hnamed
      cases hnamed
    exact htarget.trans hoccupied.symm
  · obtain ⟨i, hi⟩ := named.only_named q hoccupied
    have hival := ZMod.natCast_zmod_val i
    let j : Fin (t + 1) := ⟨i.val, i.val_lt⟩
    have hjsite := h.toValidFiberPlacement_siteFin hpositive hremaining j
    have hjblock := h.toValidFiberPlacement_blockFin hpositive hremaining j
    change data.siteFin j = named.position (j.val : ZMod (t + 1)) at hjsite
    change data.blockFin j = named.block (j.val : ZMod (t + 1)) at hjblock
    have hcast : (j.val : ZMod (t + 1)) = i := by
      simpa [j] using hival
    rw [← hi, ← hcast, ← hjsite, data.target_at, hjblock, hjsite]
    exact (named.placed_at _).symm

/-- Reverse fixed-chain fiber classification for nonempty decoded complement:
every generated endpoint is exactly one of the declared fiber targets. This
is an existence theorem; parameter uniqueness is established separately. -/
theorem actual_fiber_normal_form
    (word : List Letter) (hn : 2 ≤ n)
    (c : Code (n - 2))
    (hregistered :
      (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (hchain :
      (run (selectedPair n) (singletonExecution n) word).chain =
        decodeChain c hn)
    (hremaining :
      (decodeCode c hn).frontier.lo < (decodeCode c hn).frontier.hi) :
    ∃ (t : ℕ) (data : ValidFiberPlacement n t),
      data.u = (decodeCode c hn).frontier.lo ∧
      data.v = (decodeCode c hn).frontier.hi ∧
      (run (selectedPair n) (singletonExecution n) word).placed =
        data.target := by
  obtain ⟨r, hr, named, hplaced, hpositive, hnaming⟩ :=
    actual_code_ordered_outside_naming word hn c hregistered hchain hremaining
  letI : NeZero r := hr
  have hr2 := hnaming.count
  obtain ⟨t, ht⟩ : ∃ t, r = t + 1 := ⟨r - 1, by omega⟩
  subst r
  let hcut : CutNamed (decodeCode c hn).frontier named :=
    hnaming.toCutNamed hremaining
  let data : ValidFiberPlacement n t :=
    hcut.toValidFiberPlacement hpositive hremaining
  refine ⟨t, data, rfl, rfl, ?_⟩
  exact hplaced.symm.trans (hcut.toValidFiberPlacement_target
    hpositive hremaining).symm

/-- A code whose decoded complement is empty has an actual full-carrier
witness, so the previously conditional phase classification applies to its
fixed source-addressed records without an extra existence assumption. -/
theorem full_carrier_code_fiber_phases
    (c : Code (n - 2)) (hn : 2 ≤ n)
    (hempty :
      (decodeCode c hn).frontier.lo = (decodeCode c hn).frontier.hi) :
    ∃ base : Execution n (ZMod n),
      base.origin = (registrationExecution n).origin ∧
      base.chain = decodeChain c hn ∧
      FullCarrierFixedRecords (selectedPair n) base.origin base.chain =
        Set.range (fun q : ZMod n =>
          { base with placed := fullCarrierPlacement Finset.univ q }) ∧
      (FullCarrierFixedRecords (selectedPair n) base.origin base.chain).ncard = n := by
  obtain ⟨word, q, hq, horigin, hchain, _⟩ :=
    realize_clean_code_actual_carrier c hn
  let base := run (selectedPair n) (singletonExecution n) word
  have hcarrier : decodedCarrier c hn = (Finset.univ : Finset (ZMod n)) := by
    let f := (decodeCode c hn).frontier
    change f.carrier = Finset.univ
    ext a
    rw [f.mem_carrier_iff]
    simp only [Finset.mem_univ, iff_true]
    have := f.noncrossing
    change f.lo = f.hi at hempty
    omega
  have hfull : base.placed q = some (Finset.univ : Finset (ZMod n)) := by
    simpa [base, hcarrier] using hq
  have hbase : base ∈ FullCarrierFixedRecords (selectedPair n)
      base.origin base.chain := ⟨⟨word, rfl⟩, rfl, rfl, ⟨q, hfull⟩⟩
  refine ⟨base, horigin, hchain, ?_, ?_⟩
  · exact fullCarrierFixedRecords_eq_phases (selectedPair n) hn base hbase
  · exact fullCarrierFixedRecords_card (selectedPair n) hn base hbase

/-- Every occupied named packet occurs exactly once among the blocks of its
placement. This identifies the number of target packets with the name count. -/
theorem LegalNamedPlacement.blocks_image_eq
    {named : LegalNamedPlacement n r (ZMod n)} :
    Finset.univ.image (fun i : Fin r => named.block (i.val : ZMod r)) =
      placedBlocks named.placed := by
  ext B
  simp only [Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨i, rfl⟩
    exact (mem_placedBlocks named.placed _).mpr
      ⟨named.block_nonempty _, named.position _, named.placed_at _⟩
  · intro hB
    obtain ⟨_, q, hq⟩ := (mem_placedBlocks named.placed B).mp hB
    obtain ⟨i, hi⟩ := named.only_named q (by simp [hq])
    let j : Fin r := ⟨i.val, i.val_lt⟩
    have hcast : (j.val : ZMod r) = i := by
      simpa [j] using ZMod.natCast_zmod_val i
    refine ⟨j, ?_⟩
    rw [hcast]
    exact Option.some.inj ((named.placed_at i).symm.trans (hi ▸ hq))

theorem LegalNamedPlacement.blocks_card
    {named : LegalNamedPlacement n r (ZMod n)} :
    (placedBlocks named.placed).card = r := by
  rw [← named.blocks_image_eq]
  have hinj : Function.Injective
      (fun i : Fin r => named.block (i.val : ZMod r)) := by
    intro i j hij
    by_contra hne
    have hz : (i.val : ZMod r) ≠ (j.val : ZMod r) := by
      intro heq
      apply hne
      apply Fin.ext
      have hv := congrArg ZMod.val heq
      rwa [ZMod.val_natCast_of_lt i.isLt,
        ZMod.val_natCast_of_lt j.isLt] at hv
    have hdisj := named.block_disjoint _ _ hz
    have hnonempty := named.block_nonempty (i.val : ZMod r)
    change named.block (i.val : ZMod r) = named.block (j.val : ZMod r) at hij
    rw [← hij] at hdisj
    obtain ⟨a, ha⟩ := hnonempty
    exact (Finset.disjoint_left.mp hdisj) ha ha
  rw [Finset.card_image_of_injective _ hinj]
  simp

theorem sourceBlockKey_sourceInterval
    (lo hi : ℕ) (hlo : lo < hi) (hhi : hi ≤ n)
    (hne : (sourceInterval (n := n) lo hi).Nonempty) :
    sourceBlockKey (sourceInterval (n := n) lo hi) hne = lo := by
  have hkeyMem := sourceBlockKey_mem (sourceInterval (n := n) lo hi) hne
  have hkeyLt := sourceBlockKey_lt (sourceInterval (n := n) lo hi) hne
  have hkey_ge : lo ≤ sourceBlockKey (sourceInterval (n := n) lo hi) hne := by
    have h := (mem_sourceInterval_iff lo hi hhi _).mp hkeyMem
    simpa [ZMod.val_natCast_of_lt hkeyLt] using h.1
  have hloN : lo < n := by omega
  have hloMem : (lo : ZMod n) ∈ sourceInterval (n := n) lo hi := by
    rw [mem_sourceInterval_iff lo hi hhi]
    simpa [ZMod.val_natCast_of_lt hloN] using
      (show lo ≤ lo ∧ lo < hi by omega)
  have hkey_le := sourceBlockKey_le
    (sourceInterval (n := n) lo hi) hne (lo : ZMod n) hloMem
  rw [ZMod.val_natCast_of_lt hloN] at hkey_le
  omega

theorem LegalNamedPlacement.keys_image_eq
    {named : LegalNamedPlacement n r (ZMod n)} :
    Finset.univ.image (namedSourceKey named) = occupiedKeys named.placed := by
  ext k
  simp only [occupiedKeys, Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨i, rfl⟩
    let B : placedBlocks named.placed :=
      ⟨named.block (i.val : ZMod r),
        (mem_placedBlocks named.placed _).mpr
          ⟨named.block_nonempty _, named.position _, named.placed_at _⟩⟩
    exact ⟨B, by simp [B, namedSourceKey, occupiedBlockKey]⟩
  · rintro ⟨B, hB⟩
    have hmem : B.1 ∈
        Finset.univ.image (fun i : Fin r => named.block (i.val : ZMod r)) := by
      rw [named.blocks_image_eq]
      exact B.2
    obtain ⟨i, _, hi⟩ := Finset.mem_image.mp hmem
    refine ⟨i, ?_⟩
    simpa [namedSourceKey, occupiedBlockKey, hi] using hB

/-- Two source-key-sorted namings of the same concrete placement cannot
disagree about the block or its physical site at any index. -/
theorem LegalNamedPlacement.same_sorted_names
    {first second : LegalNamedPlacement n r (ZMod n)}
    (hplaced : first.placed = second.placed)
    (hfirst : StrictMono (namedSourceKey first))
    (hsecond : StrictMono (namedSourceKey second)) :
    (∀ i : Fin r,
      first.block (i.val : ZMod r) = second.block (i.val : ZMod r)) ∧
    (∀ i : Fin r,
      first.position (i.val : ZMod r) =
        second.position (i.val : ZMod r)) := by
  have hkeys : namedSourceKey first = namedSourceKey second := by
    apply strictMono_fin_eq_of_image_eq _ _ hfirst hsecond
    rw [first.keys_image_eq, second.keys_image_eq, hplaced]
  have hblocks (i : Fin r) :
      first.block (i.val : ZMod r) = second.block (i.val : ZMod r) := by
    let x : ZMod n := (namedSourceKey first i : ZMod n)
    have hxi : x ∈ first.block (i.val : ZMod r) :=
      namedSourceKey_mem first i
    have hxsecond : x ∈ second.block (i.val : ZMod r) := by
      simpa [x, ← congrFun hkeys i] using namedSourceKey_mem second i
    have hq : first.placed (second.position (i.val : ZMod r)) ≠ none := by
      rw [hplaced, second.placed_at]
      simp
    obtain ⟨j, hj⟩ := first.only_named _ hq
    have hBj : first.block j = second.block (i.val : ZMod r) := by
      have hfirstAt := first.placed_at j
      have hsecondAt := second.placed_at (i.val : ZMod r)
      rw [hj, hplaced, hsecondAt] at hfirstAt
      exact (Option.some.inj hfirstAt).symm
    have hxj : x ∈ first.block j := hBj ▸ hxsecond
    have hjeq : j = (i.val : ZMod r) := by
      by_contra hne
      have hdisj := first.block_disjoint j (i.val : ZMod r) hne
      exact (Finset.disjoint_left.mp hdisj) hxj hxi
    simpa [hjeq] using hBj
  refine ⟨hblocks, ?_⟩
  intro i
  have hq : first.placed (second.position (i.val : ZMod r)) =
      some (first.block (i.val : ZMod r)) := by
    rw [hplaced, second.placed_at, hblocks]
  have hq' := first.placed_at (i.val : ZMod r)
  have hne := first.block_nonempty (i.val : ZMod r)
  obtain ⟨j, hj⟩ := first.only_named
    (second.position (i.val : ZMod r)) (by rw [hq]; simp)
  have hBj : first.block j = first.block (i.val : ZMod r) := by
    have hat := first.placed_at j
    rw [hj, hq] at hat
    exact (Option.some.inj hat).symm
  have hjeq : j = (i.val : ZMod r) := by
    by_contra hneq
    have hdisj := first.block_disjoint j (i.val : ZMod r) hneq
    obtain ⟨x, hx⟩ := hne
    exact (Finset.disjoint_left.mp hdisj) (hBj ▸ hx) hx
  calc
    first.position (i.val : ZMod r) = first.position j := by rw [hjeq]
    _ = second.position (i.val : ZMod r) := hj

theorem CutNamed.key_zero
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) :
    namedSourceKey named ⟨0, by have := h.count; omega⟩ = 0 := by
  have hmem : (0 : ZMod n) ∈ named.block 0 := by
    rw [h.carrier]
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hle := namedSourceKey_le named
    ⟨0, by have := h.count; omega⟩ 0 (by simpa using hmem)
  simp only [ZMod.val_zero] at hle
  omega

theorem CutNamed.key_outside
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) (i : Fin r) (hi : 0 < i.val) :
    namedSourceKey named i = h.cut (i.val - 1) := by
  have hsub : i.val - 1 + 1 = i.val := by omega
  have hstep : h.cut (i.val - 1) < h.cut i.val := by
    simpa [hsub] using h.cut_step (i.val - 1) (by omega)
  have hout := h.outside i.val (by omega) i.isLt
  have hne := named.block_nonempty (i.val : ZMod r)
  have hkey := sourceBlockKey_sourceInterval (h.cut (i.val - 1))
    (h.cut i.val) hstep (h.cut_le_n i.val i.isLt)
    (hout ▸ hne)
  simpa [namedSourceKey, hout] using hkey

theorem CutNamed.key_strict
    {f : CheckpointSourceFrontier n}
    {named : LegalNamedPlacement n r (ZMod n)}
    (h : CutNamed f named) : StrictMono (namedSourceKey named) := by
  intro i j hij
  by_cases hi0 : i.val = 0
  · have hjpos : 0 < j.val := by omega
    have hkeyi : namedSourceKey named i = 0 := by
      have hieq : i = ⟨0, by have := h.count; omega⟩ := Fin.ext hi0
      simpa [hieq] using h.key_zero
    have hkeyj := h.key_outside j hjpos
    have hlow := h.cut_mono 0 (j.val - 1) (by omega) (by omega)
    rw [h.cut_zero] at hlow
    have := f.lo_valid
    omega
  · have hipos : 0 < i.val := by omega
    have hjpos : 0 < j.val := by omega
    rw [h.key_outside i hipos, h.key_outside j hjpos]
    have hlt : (⟨i.val - 1, by omega⟩ : Fin r) <
        ⟨j.val - 1, by omega⟩ := Fin.mk_lt_mk.mpr (by omega)
    exact h.cutFin_strict hlt

/-- If two exact source-cut namings describe the same endpoint, every cut
and every named physical site agrees. In particular, no existential witness
can exchange adjacent outside blocks while keeping the placement fixed. -/
theorem CutNamed.same_placement_cuts_sites
    {f : CheckpointSourceFrontier n}
    {first second : LegalNamedPlacement n r (ZMod n)}
    (hfirst : CutNamed f first) (hsecond : CutNamed f second)
    (hplaced : first.placed = second.placed) :
    (∀ i : ℕ, i < r → hfirst.cut i = hsecond.cut i) ∧
    (∀ i : Fin r, first.position (i.val : ZMod r) =
      second.position (i.val : ZMod r)) := by
  obtain ⟨_, hsites⟩ := LegalNamedPlacement.same_sorted_names hplaced
    hfirst.key_strict hsecond.key_strict
  refine ⟨?_, hsites⟩
  intro i hi
  by_cases hlast : i = r - 1
  · simpa [hlast] using hfirst.cut_last.trans hsecond.cut_last.symm
  · have hnext : i + 1 < r := by omega
    let j : Fin r := ⟨i + 1, hnext⟩
    have hpos : 0 < j.val := by change 0 < i + 1; omega
    have hkey := congrFun (strictMono_fin_eq_of_image_eq
      (namedSourceKey first) (namedSourceKey second)
      hfirst.key_strict hsecond.key_strict (by
        rw [first.keys_image_eq, second.keys_image_eq, hplaced])) j
    have hk1 := hfirst.key_outside j hpos
    have hk2 := hsecond.key_outside j hpos
    have hsub : j.val - 1 = i := by change i + 1 - 1 = i; omega
    rw [hk1, hk2, hsub] at hkey
    exact hkey

/-- The cut/phase/offset record extracted from a fixed endpoint is unique,
even if that endpoint was initially given with two different witnesses for
its source-ordered naming. -/
theorem CutNamed.same_placement_fiber_data
    {f : CheckpointSourceFrontier n}
    {first second : LegalNamedPlacement n (t + 1) (ZMod n)}
    (hfirst : CutNamed f first) (hsecond : CutNamed f second)
    (pfirst : first.PositivelyOrdered)
    (psecond : second.PositivelyOrdered)
    (hremaining : f.lo < f.hi)
    (hplaced : first.placed = second.placed) :
    hfirst.toValidFiberPlacement pfirst hremaining =
      hsecond.toValidFiberPlacement psecond hremaining := by
  obtain ⟨hcuts, hsites⟩ :=
    hfirst.same_placement_cuts_sites hsecond hplaced
  have hcutFn : (fun i : Fin (t + 1) => hfirst.cut i.val) =
      (fun i : Fin (t + 1) => hsecond.cut i.val) := by
    funext i
    exact hcuts i.val i.isLt
  have hsite0 : first.position 0 = second.position 0 := by
    simpa using hsites ⟨0, by omega⟩
  have hoffFn : (fun i : Fin (t + 1) => first.offset i.val) =
      (fun i : Fin (t + 1) => second.offset i.val) := by
    funext i
    simp only [LegalNamedPlacement.offset, if_pos i.isLt]
    rw [hsites i, hsite0]
  unfold CutNamed.toValidFiberPlacement
  simp only [hcutFn, hsite0, hoffFn]

end RegisteredAbsorptionChains
