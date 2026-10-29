import RegisteredAbsorptionChains.FixedPartnerSchedule
import RegisteredAbsorptionChains.CheckpointPortGeometry
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- A source-addressed linear interval, embedded in the cyclic atom carrier.
All applications below keep its upper endpoint at most `n`, so no residue
wrap is hidden in this definition. -/
def sourceInterval (lo hi : ℕ) : Finset (ZMod n) :=
  (Finset.Ico lo hi).image (fun a : ℕ => (a : ZMod n))

theorem mem_sourceInterval_iff (lo hi : ℕ) (hhi : hi ≤ n) (a : ZMod n) :
    a ∈ sourceInterval lo hi ↔ lo ≤ a.val ∧ a.val < hi := by
  constructor
  · intro ha
    obtain ⟨i, hiI, rfl⟩ := Finset.mem_image.mp ha
    have hi := Finset.mem_Ico.mp hiI
    simpa [ZMod.val_natCast_of_lt (show i < n by omega)] using hi
  · intro ha
    apply Finset.mem_image.mpr
    exact ⟨a.val, Finset.mem_Ico.mpr ha, ZMod.natCast_zmod_val a⟩

omit [NeZero n] in
theorem card_sourceInterval (lo hi : ℕ) (hhi : hi ≤ n) :
    (sourceInterval (n := n) lo hi).card = hi - lo := by
  unfold sourceInterval
  rw [Finset.card_image_iff.mpr]
  · simp
  · intro a ha b hb hab
    have ha' := Finset.mem_Ico.mp ha
    have hb' := Finset.mem_Ico.mp hb
    have hv := congrArg ZMod.val hab
    simpa [ZMod.val_natCast_of_lt (show a < n by omega),
      ZMod.val_natCast_of_lt (show b < n by omega)] using hv

theorem sourceInterval_adjacent (lo mid hi : ℕ)
    (hlo : lo ≤ mid) (hmid : mid ≤ hi) (hhi : hi ≤ n) :
    sourceInterval (n := n) lo mid ∪ sourceInterval mid hi =
      sourceInterval lo hi := by
  ext a
  rw [Finset.mem_union, mem_sourceInterval_iff lo mid (by omega),
    mem_sourceInterval_iff mid hi hhi, mem_sourceInterval_iff lo hi hhi]
  omega

/-- The symbolic carrier has consumed a prefix `[2,lo)` and a suffix
`[hi,n)` of the original outside list `(2,...,n-1)`. -/
structure CheckpointSourceFrontier (n : ℕ) [NeZero n] where
  lo : ℕ
  hi : ℕ
  lo_valid : 2 ≤ lo
  noncrossing : lo ≤ hi
  hi_valid : hi ≤ n

def CheckpointSourceFrontier.carrier (f : CheckpointSourceFrontier n) :
    Finset (ZMod n) :=
  selectedPair n ∪ sourceInterval 2 f.lo ∪ sourceInterval f.hi n

def CheckpointSourceFrontier.remaining (f : CheckpointSourceFrontier n) :
    Finset (ZMod n) := sourceInterval f.lo f.hi

theorem CheckpointSourceFrontier.mem_carrier_iff
    (f : CheckpointSourceFrontier n) (a : ZMod n) :
    a ∈ f.carrier ↔ a.val < f.lo ∨ f.hi ≤ a.val := by
  have hn : 2 ≤ n := le_trans f.lo_valid (le_trans f.noncrossing f.hi_valid)
  have hpair : a ∈ selectedPair n ↔ a.val < 2 := by
    constructor
    · intro ha
      simp only [selectedPair, Finset.mem_insert, Finset.mem_singleton] at ha
      rcases ha with h0 | h1
      · simp [h0]
      · subst a
        rw [show (1 : ZMod n).val = 1 by
          simpa only [Nat.cast_one] using
            (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))]
        omega
    · intro ha
      have hv : a.val = 0 ∨ a.val = 1 := by omega
      rcases hv with h0 | h1
      · have hz : a = 0 := by
          rw [← ZMod.natCast_zmod_val a, h0]
          simp
        simp [selectedPair, hz]
      · have ho : a = 1 := by
          rw [← ZMod.natCast_zmod_val a, h1]
          simp
        simp [selectedPair, ho]
  simp only [CheckpointSourceFrontier.carrier, Finset.mem_union,
    hpair, mem_sourceInterval_iff 2 f.lo (le_trans f.noncrossing f.hi_valid),
    mem_sourceInterval_iff f.hi n (le_refl n)]
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have haval := a.val_lt
  omega

theorem CheckpointSourceFrontier.not_mem_carrier_iff_remaining
    (f : CheckpointSourceFrontier n) (a : ZMod n) :
    a ∉ f.carrier ↔ a ∈ f.remaining := by
  rw [f.mem_carrier_iff, CheckpointSourceFrontier.remaining,
    mem_sourceInterval_iff f.lo f.hi f.hi_valid]
  omega

def CheckpointSourceFrontier.absorbed (f : CheckpointSourceFrontier n) : ℕ :=
  (f.lo - 2) + (n - f.hi)

theorem CheckpointSourceFrontier.remaining_card
    (f : CheckpointSourceFrontier n) :
    f.remaining.card = f.hi - f.lo :=
  card_sourceInterval f.lo f.hi f.hi_valid

theorem CheckpointSourceFrontier.remaining_plus_absorbed
    (f : CheckpointSourceFrontier n) :
    f.remaining.card + f.absorbed = n - 2 := by
  rw [f.remaining_card]
  dsimp [CheckpointSourceFrontier.absorbed]
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  omega

def CheckpointSourceFrontier.partnerR (f : CheckpointSourceFrontier n)
    (ell : ℕ) : Finset (ZMod n) :=
  sourceInterval f.lo (f.lo + ell)

def CheckpointSourceFrontier.partnerL (f : CheckpointSourceFrontier n)
    (ell : ℕ) : Finset (ZMod n) :=
  sourceInterval (f.hi - ell) f.hi

def CheckpointSourceFrontier.nextR (f : CheckpointSourceFrontier n)
    (ell : ℕ) (h : ell ≤ f.hi - f.lo) : CheckpointSourceFrontier n :=
  ⟨f.lo + ell, f.hi,
    by have := f.lo_valid; omega,
    by have := f.noncrossing; omega,
    f.hi_valid⟩

def CheckpointSourceFrontier.nextL (f : CheckpointSourceFrontier n)
    (ell : ℕ) (h : ell ≤ f.hi - f.lo) : CheckpointSourceFrontier n :=
  ⟨f.lo, f.hi - ell, f.lo_valid,
    by have := f.noncrossing; omega,
    by have := f.hi_valid; omega⟩

theorem CheckpointSourceFrontier.partnerR_card
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.partnerR ell).card = ell := by
  have hle := f.noncrossing
  have hhi := f.hi_valid
  rw [CheckpointSourceFrontier.partnerR, card_sourceInterval]
  · omega
  · omega

theorem CheckpointSourceFrontier.partnerL_card
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.partnerL ell).card = ell := by
  have hle := f.noncrossing
  rw [CheckpointSourceFrontier.partnerL, card_sourceInterval]
  · omega
  · exact f.hi_valid

theorem CheckpointSourceFrontier.partnerR_disjoint_carrier
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    Disjoint (f.partnerR ell) f.carrier := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hn : 2 ≤ n := by omega
  apply Finset.disjoint_left.mpr
  intro a ha hb
  have hrange := (mem_sourceInterval_iff f.lo (f.lo + ell) (by omega) a).mp ha
  rcases Finset.mem_union.mp hb with hinit | hright
  · rcases Finset.mem_union.mp hinit with hpair | hleft
    · simp only [selectedPair, Finset.mem_insert, Finset.mem_singleton] at hpair
      rcases hpair with h0 | h1
      · subst a
        simp at hrange
        omega
      · subst a
        have hval : (1 : ZMod n).val = 1 := by
          simpa only [Nat.cast_one] using
            (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
        rw [hval] at hrange
        omega
    · have hv := (mem_sourceInterval_iff 2 f.lo (by omega) a).mp hleft
      omega
  · have hv := (mem_sourceInterval_iff f.hi n (le_refl n) a).mp hright
    omega

theorem CheckpointSourceFrontier.partnerL_disjoint_carrier
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    Disjoint (f.partnerL ell) f.carrier := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hn : 2 ≤ n := by omega
  apply Finset.disjoint_left.mpr
  intro a ha hb
  have hrange := (mem_sourceInterval_iff (f.hi - ell) f.hi f.hi_valid a).mp ha
  rcases Finset.mem_union.mp hb with hinit | hright
  · rcases Finset.mem_union.mp hinit with hpair | hleft
    · simp only [selectedPair, Finset.mem_insert, Finset.mem_singleton] at hpair
      rcases hpair with h0 | h1
      · subst a
        simp at hrange
        omega
      · subst a
        have hval : (1 : ZMod n).val = 1 := by
          simpa only [Nat.cast_one] using
            (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
        rw [hval] at hrange
        omega
    · have hv := (mem_sourceInterval_iff 2 f.lo (by omega) a).mp hleft
      omega
  · have hv := (mem_sourceInterval_iff f.hi n (le_refl n) a).mp hright
    omega

theorem CheckpointSourceFrontier.carrier_nextR
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.nextR ell h).carrier = f.carrier ∪ f.partnerR ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hadd := sourceInterval_adjacent (n := n) 2 f.lo (f.lo + ell)
    (by omega) (by omega) (by omega)
  dsimp [CheckpointSourceFrontier.nextR, CheckpointSourceFrontier.carrier,
    CheckpointSourceFrontier.partnerR]
  rw [← hadd]
  ext a
  simp only [Finset.mem_union]
  tauto

theorem CheckpointSourceFrontier.carrier_nextL
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.nextL ell h).carrier = f.carrier ∪ f.partnerL ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hadd := sourceInterval_adjacent (n := n) (f.hi - ell) f.hi n
    (by omega) (by omega) (le_refl n)
  dsimp [CheckpointSourceFrontier.nextL, CheckpointSourceFrontier.carrier,
    CheckpointSourceFrontier.partnerL]
  rw [← hadd]
  ext a
  simp only [Finset.mem_union]
  tauto

theorem CheckpointSourceFrontier.remaining_splitR
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    f.partnerR ell ∪ (f.nextR ell h).remaining = f.remaining := by
  have hadd := sourceInterval_adjacent (n := n) f.lo (f.lo + ell) f.hi
    (by omega) (by have := f.noncrossing; omega) f.hi_valid
  simpa [CheckpointSourceFrontier.partnerR, CheckpointSourceFrontier.nextR,
    CheckpointSourceFrontier.remaining] using hadd

theorem CheckpointSourceFrontier.remaining_splitL
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.nextL ell h).remaining ∪ f.partnerL ell = f.remaining := by
  have hadd := sourceInterval_adjacent (n := n) f.lo (f.hi - ell) f.hi
    (by have := f.noncrossing; omega) (by omega) f.hi_valid
  simpa [CheckpointSourceFrontier.partnerL, CheckpointSourceFrontier.nextL,
    CheckpointSourceFrontier.remaining] using hadd

theorem CheckpointSourceFrontier.absorbed_nextR
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.nextR ell h).absorbed = f.absorbed + ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  dsimp [CheckpointSourceFrontier.nextR, CheckpointSourceFrontier.absorbed]
  omega

theorem CheckpointSourceFrontier.absorbed_nextL
    (f : CheckpointSourceFrontier n) (ell : ℕ)
    (h : ell ≤ f.hi - f.lo) :
    (f.nextL ell h).absorbed = f.absorbed + ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  dsimp [CheckpointSourceFrontier.nextL, CheckpointSourceFrontier.absorbed]
  omega

/-- A nonzero code position is cumulative absorbed size. The difference
from the previous checkpoint fits exactly in the remaining source interval. -/
theorem CheckpointSourceFrontier.checkpoint_gap
    (f : CheckpointSourceFrontier n) (bNext : ℕ)
    (hnext : f.absorbed < bNext) (hmax : bNext ≤ n - 2) :
    0 < bNext - f.absorbed ∧
      bNext - f.absorbed ≤ f.hi - f.lo := by
  have htotal := f.remaining_plus_absorbed
  rw [f.remaining_card] at htotal
  omega

theorem CheckpointSourceFrontier.nextR_checkpoint
    (f : CheckpointSourceFrontier n) (bNext : ℕ)
    (hnext : f.absorbed < bNext) (hmax : bNext ≤ n - 2) :
    (f.nextR (bNext - f.absorbed)
      (f.checkpoint_gap bNext hnext hmax).2).absorbed = bNext := by
  rw [f.absorbed_nextR]
  omega

theorem CheckpointSourceFrontier.nextL_checkpoint
    (f : CheckpointSourceFrontier n) (bNext : ℕ)
    (hnext : f.absorbed < bNext) (hmax : bNext ≤ n - 2) :
    (f.nextL (bNext - f.absorbed)
      (f.checkpoint_gap bNext hnext hmax).2).absorbed = bNext := by
  rw [f.absorbed_nextL]
  omega

/-- Cleanliness and genuine seed reachability determine the complete packet
set: one carrier and exactly one singleton for every remaining source atom. -/
theorem CheckpointSourceFrontier.clean_placedBlocks
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (clean : CleanOutside f.carrier s) :
    placedBlocks s.placed =
      insert f.carrier (f.remaining.image fun a => ({a} : Finset (ZMod n))) := by
  have hn : 2 ≤ n := le_trans f.lo_valid (le_trans f.noncrossing f.hi_valid)
  obtain ⟨word, hword⟩ := reachable
  have ordered : SourceOrdered s.placed :=
    reachable_source_ordered F s.placed hn ⟨word, congrArg Execution.placed hword⟩
  have hCne : f.carrier.Nonempty := by
    refine ⟨0, ?_⟩
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hC : f.carrier ∈ placedBlocks s.placed :=
    (mem_placedBlocks s.placed f.carrier).mpr ⟨hCne, clean.1⟩
  ext B
  constructor
  · intro hB
    by_cases hBC : B = f.carrier
    · simp [hBC]
    obtain ⟨_, q, hq⟩ := (mem_placedBlocks s.placed B).mp hB
    rcases clean.2 q B hq with h | ⟨a, ha⟩
    · exact False.elim (hBC h)
    have hdisj := sourceOrdered_blocks_disjoint s.placed ordered B f.carrier
      hB hC hBC
    have hnot : a ∉ f.carrier := by
      intro hmem
      exact (Finset.disjoint_left.mp hdisj) (ha.symm ▸ Finset.mem_singleton_self a) hmem
    have hremaining := (f.not_mem_carrier_iff_remaining a).mp hnot
    exact Finset.mem_insert_of_mem (Finset.mem_image.mpr ⟨a, hremaining, ha.symm⟩)
  · intro hB
    rcases Finset.mem_insert.mp hB with hBC | hsingle
    · exact hBC ▸ hC
    obtain ⟨a, ha, rfl⟩ := Finset.mem_image.mp hsingle
    have hnot := (f.not_mem_carrier_iff_remaining a).mpr ha
    obtain ⟨q, hq⟩ := clean_reachable_outside_singletons F f.carrier s hn
      ⟨word, hword⟩ clean a hnot
    exact (mem_placedBlocks s.placed {a}).mpr ⟨Finset.singleton_nonempty a, q, hq⟩

theorem CheckpointSourceFrontier.clean_block_count
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (clean : CleanOutside f.carrier s) :
    (placedBlocks s.placed).card = f.hi - f.lo + 1 := by
  rw [f.clean_placedBlocks F s reachable clean]
  have hnot : f.carrier ∉
      f.remaining.image (fun a => ({a} : Finset (ZMod n))) := by
    intro h
    obtain ⟨a, ha, hEq⟩ := Finset.mem_image.mp h
    have hno := (f.not_mem_carrier_iff_remaining a).mpr ha
    apply hno
    rw [← hEq]
    simp
  rw [Finset.card_insert_of_notMem hnot]
  rw [Finset.card_image_of_injective _ Finset.singleton_injective]
  rw [f.remaining_card]

theorem occupiedBlockKey_of_singleton
    (placed : Placement n (Finset (ZMod n)))
    (B : placedBlocks placed) (a : ZMod n)
    (hB : B.1 = {a}) : occupiedBlockKey placed B = a.val := by
  have hmem := occupiedBlockKey_mem placed B
  rw [hB] at hmem
  have heq : ((occupiedBlockKey placed B : ℕ) : ZMod n) = a := by
    simpa using hmem
  have hval := congrArg ZMod.val heq
  simpa only [ZMod.val_natCast_of_lt (occupiedBlockKey_lt placed B)] using hval

theorem occupiedBlockKey_of_zero
    (placed : Placement n (Finset (ZMod n)))
    (B : placedBlocks placed)
    (hzero : (0 : ZMod n) ∈ B.1) : occupiedBlockKey placed B = 0 := by
  have hle := sourceBlockKey_le B.1
    ((mem_placedBlocks placed B.1).mp B.2).1 0 hzero
  simp only [ZMod.val_zero] at hle
  exact Nat.eq_zero_of_le_zero hle

theorem CheckpointSourceFrontier.clean_occupiedKeys
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (clean : CleanOutside f.carrier s) :
    occupiedKeys s.placed = insert 0 (Finset.Ico f.lo f.hi) := by
  have hn : 2 ≤ n := le_trans f.lo_valid (le_trans f.noncrossing f.hi_valid)
  have hblocks := f.clean_placedBlocks F s reachable clean
  have hCne : f.carrier.Nonempty := by
    refine ⟨0, ?_⟩
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hC : f.carrier ∈ placedBlocks s.placed :=
    (mem_placedBlocks s.placed f.carrier).mpr ⟨hCne, clean.1⟩
  ext k
  constructor
  · intro hk
    obtain ⟨B, _, hkey⟩ := Finset.mem_image.mp hk
    have hB : B.1 ∈ insert f.carrier
        (f.remaining.image fun a => ({a} : Finset (ZMod n))) := by
      rw [← hblocks]
      exact B.2
    rcases Finset.mem_insert.mp hB with hcarrier | hsingle
    · have hzero : (0 : ZMod n) ∈ B.1 := by
        rw [hcarrier]
        simp [CheckpointSourceFrontier.carrier, selectedPair]
      have h0 := occupiedBlockKey_of_zero s.placed B hzero
      exact Finset.mem_insert.mpr (Or.inl (hkey.symm.trans h0))
    · obtain ⟨a, ha, hEq⟩ := Finset.mem_image.mp hsingle
      have hkeya := occupiedBlockKey_of_singleton s.placed B a hEq.symm
      apply Finset.mem_insert.mpr
      right
      have hrange := (mem_sourceInterval_iff f.lo f.hi f.hi_valid a).mp ha
      simpa [Finset.mem_Ico, hkey.symm.trans hkeya] using hrange
  · intro hk
    rcases Finset.mem_insert.mp hk with hk0 | hki
    · subst k
      unfold occupiedKeys
      exact Finset.mem_image.mpr
        ⟨⟨f.carrier, hC⟩, Finset.mem_univ _,
          occupiedBlockKey_of_zero s.placed ⟨f.carrier, hC⟩ (by
            simp [CheckpointSourceFrontier.carrier, selectedPair])⟩
    · have hrange := Finset.mem_Ico.mp hki
      let a : ZMod n := (k : ZMod n)
      have hval : a.val = k := ZMod.val_natCast_of_lt (by
        have hhi := f.hi_valid
        omega)
      have ha : a ∈ f.remaining := by
        exact (mem_sourceInterval_iff f.lo f.hi f.hi_valid a).mpr (by
          rw [hval]
          exact hrange)
      have hnot := (f.not_mem_carrier_iff_remaining a).mpr ha
      obtain ⟨q, hq⟩ := clean_reachable_outside_singletons F f.carrier s hn
        reachable clean a hnot
      have hB : ({a} : Finset (ZMod n)) ∈ placedBlocks s.placed :=
        (mem_placedBlocks s.placed {a}).mpr ⟨Finset.singleton_nonempty a, q, hq⟩
      unfold occupiedKeys
      exact Finset.mem_image.mpr
        ⟨⟨{a}, hB⟩, Finset.mem_univ _, by
          rw [occupiedBlockKey_of_singleton s.placed ⟨{a}, hB⟩ a rfl,
            hval]⟩

private theorem sorted_checkpoint_keys
    (lo hi : ℕ) (hlo : 0 < lo) (hle : lo ≤ hi) :
    (insert 0 (Finset.Ico lo hi)).sort =
      0 :: List.range' lo (hi - lo) := by
  let l := 0 :: List.range' lo (hi - lo)
  have hnodup : l.Nodup := by
    dsimp [l]
    apply List.nodup_cons.mpr
    constructor
    · intro h
      have hr := List.mem_range'_1.mp h
      omega
    · exact List.nodup_range'
  have hpair : l.Pairwise (· ≤ ·) := by
    dsimp [l]
    apply List.pairwise_cons.mpr
    constructor
    · intro x _
      omega
    · exact List.pairwise_le_range' _
  have hset : l.toFinset = insert 0 (Finset.Ico lo hi) := by
    ext x
    simp only [l, List.toFinset_cons, Finset.mem_insert, List.mem_toFinset,
      List.mem_range'_1, Finset.mem_Ico]
    omega
  have hsort := (List.toFinset_sort (r := (· ≤ ·)) hnodup).mpr hpair
  rw [hset] at hsort
  exact hsort

theorem CheckpointSourceFrontier.canonical_outside_key
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (clean : CleanOutside f.carrier s)
    (ordered : SourceOrdered s.placed)
    (i : ℕ) (hi0 : 1 ≤ i) (hir : i < (placedBlocks s.placed).card) :
    occupiedBlockKey s.placed
      (canonicalBlock s.placed ordered ⟨i, hir⟩) = f.lo + i - 1 := by
  have hcount := f.clean_block_count F s reachable clean
  have hkeys := f.clean_occupiedKeys F s reachable clean
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hsort : (occupiedKeys s.placed).sort =
      0 :: List.range' f.lo (f.hi - f.lo) := by
    rw [hkeys]
    exact sorted_checkpoint_keys f.lo f.hi (by omega) f.noncrossing
  rw [canonicalBlock_key, Finset.coe_orderIsoOfFin_apply,
    Finset.orderEmbOfFin_apply]
  simp only [hsort]
  cases i with
  | zero => omega
  | succ j =>
      have hj : j < f.hi - f.lo := by omega
      change (0 :: List.range' f.lo (f.hi - f.lo))[j + 1]'(by simp; omega) =
        f.lo + (j + 1) - 1
      simp only [List.getElem_cons_succ]
      rw [List.getElem_range'_1 j (by simpa using hj)]
      omega

theorem CheckpointSourceFrontier.canonical_outside_block
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (clean : CleanOutside f.carrier s)
    (ordered : SourceOrdered s.placed)
    (i : ℕ) (hi0 : 1 ≤ i) (hir : i < (placedBlocks s.placed).card) :
    (canonicalBlock s.placed ordered ⟨i, hir⟩).1 =
      {((f.lo + i - 1 : ℕ) : ZMod n)} := by
  let B := canonicalBlock s.placed ordered ⟨i, hir⟩
  have hB : B.1 ∈ insert f.carrier
      (f.remaining.image fun a => ({a} : Finset (ZMod n))) := by
    rw [← f.clean_placedBlocks F s reachable clean]
    exact B.2
  have hkey := f.canonical_outside_key F s reachable clean ordered i hi0 hir
  change occupiedBlockKey s.placed B = f.lo + i - 1 at hkey
  rcases Finset.mem_insert.mp hB with hC | hsingle
  · have hzero : (0 : ZMod n) ∈ B.1 := by
      rw [hC]
      simp [CheckpointSourceFrontier.carrier, selectedPair]
    have hkey0 := occupiedBlockKey_of_zero s.placed B hzero
    have hlo := f.lo_valid
    omega
  · obtain ⟨a, _, hEq⟩ := Finset.mem_image.mp hsingle
    have hkeya := occupiedBlockKey_of_singleton s.placed B a hEq.symm
    have hval : a.val = f.lo + i - 1 := hkeya.symm.trans hkey
    have ha : a = ((f.lo + i - 1 : ℕ) : ZMod n) := by
      calc
        a = (a.val : ZMod n) := (ZMod.natCast_zmod_val a).symm
        _ = ((f.lo + i - 1 : ℕ) : ZMod n) := by rw [hval]
    simpa [B, ha] using hEq.symm

/-- A generated clean state together with the precise source-order naming
needed by the fixed R/L assembly theorems. Existence of this alignment for
every decoded code checkpoint is a separate construction theorem. -/
structure CheckpointNamedAlignment
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n)) : Prop where
  reachable : ReachableExecution F s
  registered : s.origin.isSome = true
  selected : F.Nonempty
  inside : F ⊆ f.carrier
  clean : CleanOutside f.carrier s
  source : s.placed = first.placed
  ordered : first.PositivelyOrdered
  count : r = f.hi - f.lo + 1
  carrier : first.block 0 = f.carrier
  outside : ∀ i : ℕ, 1 ≤ i → i < r →
    first.block (i : ZMod r) = {((f.lo + i - 1 : ℕ) : ZMod n)}

/-- In the existing source-key canonical naming, block zero is the actual
carrier whenever that carrier contains source atom zero. -/
theorem canonical_named_carrier
    (s : Execution n (ZMod n))
    (ordered : SourceOrdered s.placed)
    [NeZero (placedBlocks s.placed).card]
    (C : Finset (ZMod n))
    (hcarrier : ∃ q, s.placed q = some C)
    (hzero : (0 : ZMod n) ∈ C) :
    (canonicalLegalNamed s.placed s.placed ordered ordered rfl).block 0 = C := by
  let r := (placedBlocks s.placed).card
  let named := canonicalLegalNamed s.placed s.placed ordered ordered rfl
  obtain ⟨qC, hC⟩ := hcarrier
  obtain ⟨i, hi⟩ := named.only_named qC (by
    change s.placed qC ≠ none
    simp [hC])
  have hBi : named.block i = C :=
    Option.some.inj ((named.placed_at i).symm.trans (hi ▸ hC))
  have hrpos : 0 < r := sourceOrdered_blocks_card_pos s.placed ordered
  have hzeroNamed : (0 : ZMod n) ∈ named.block 0 := by
    change (0 : ZMod n) ∈
      (canonicalLegalNamed s.placed s.placed ordered ordered rfl).block 0
    rw [canonicalLegalNamed_block]
    have hidx0 : (ZMod.finEquiv r).symm (0 : ZMod r) = ⟨0, hrpos⟩ := by
      have h := finEquiv_symm_natCast (r := r) 0 hrpos
      simpa only [Nat.cast_zero] using h
    rw [hidx0]
    exact canonicalBlock_zero_mem s.placed ordered
  by_cases hi0 : i = 0
  · simpa [named, hi0] using hBi
  · have hdisj := named.block_disjoint 0 i (Ne.symm hi0)
    have hzeroI : (0 : ZMod n) ∈ named.block i := by
      rw [hBi]
      exact hzero
    exact False.elim ((Finset.disjoint_left.mp hdisj) hzeroNamed hzeroI)

/-- The source-key naming is forced by an actual reachable clean state whose
carrier is the decoded prefix/suffix frontier. No outside block ordering is
supplied by the caller. -/
theorem CheckpointSourceFrontier.exists_named_alignment
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s) :
    ∃ (r : ℕ) (hr : NeZero r),
      letI : NeZero r := hr
      ∃ first : LegalNamedPlacement n r (ZMod n),
        CheckpointNamedAlignment F f s first := by
  have hn : 2 ≤ n := le_trans f.lo_valid (le_trans f.noncrossing f.hi_valid)
  obtain ⟨word, hword⟩ := reachable
  have ordered : SourceOrdered s.placed :=
    reachable_source_ordered F s.placed hn ⟨word, congrArg Execution.placed hword⟩
  let r := (placedBlocks s.placed).card
  have hrpos : 0 < r := sourceOrdered_blocks_card_pos s.placed ordered
  letI : NeZero r := ⟨Nat.ne_of_gt hrpos⟩
  let first := canonicalLegalNamed s.placed s.placed ordered ordered rfl
  refine ⟨r, inferInstance, first, ?_⟩
  refine {
    reachable := ⟨word, hword⟩
    registered := registered
    selected := selected
    inside := inside
    clean := clean
    source := rfl
    ordered := canonicalLegalNamed_positive s.placed s.placed ordered ordered rfl
    count := f.clean_block_count F s ⟨word, hword⟩ clean
    carrier := ?_
    outside := ?_
  }
  · apply canonical_named_carrier s ordered f.carrier clean.1
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  · intro i hi1 hir
    change (canonicalLegalNamed s.placed s.placed ordered ordered rfl).block
      (i : ZMod r) = {((f.lo + i - 1 : ℕ) : ZMod n)}
    rw [canonicalLegalNamed_block]
    rw [finEquiv_symm_natCast i hir]
    exact f.canonical_outside_block F s ⟨word, hword⟩ clean ordered i hi1 hir

theorem CheckpointNamedAlignment.admitR
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (ell : ℕ) (hpos : 0 < ell) (hbound : ell ≤ f.hi - f.lo) :
    RPartnerPrefix first (f.partnerR ell) ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hcount := aligned.count
  refine ⟨hpos, by omega, ?_, ?_⟩
  · intro i hi1 hile
    have hir : i < r := by omega
    rw [aligned.outside i hi1 hir]
    apply Finset.singleton_subset_iff.mpr
    apply (mem_sourceInterval_iff f.lo (f.lo + ell) (by omega) _).mpr
    have hval : ((f.lo + i - 1 : ℕ) : ZMod n).val = f.lo + i - 1 := by
      exact ZMod.val_natCast_of_lt (by omega)
    rw [hval]
    omega
  · intro a ha
    have hrange := (mem_sourceInterval_iff f.lo (f.lo + ell) (by omega) a).mp ha
    let i := a.val - f.lo + 1
    have hi1 : 1 ≤ i := by dsimp [i]; omega
    have hile : i ≤ ell := by dsimp [i]; omega
    have hir : i < r := by omega
    refine ⟨i, hi1, hile, ?_⟩
    rw [aligned.outside i hi1 hir]
    have hidx : f.lo + i - 1 = a.val := by dsimp [i]; omega
    simpa only [Finset.mem_singleton, hidx] using
      (ZMod.natCast_zmod_val a).symm

theorem CheckpointNamedAlignment.admitL
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (ell : ℕ) (hpos : 0 < ell) (hbound : ell ≤ f.hi - f.lo) :
    LPartnerSuffix first (f.partnerL ell) ell := by
  have hlo := f.lo_valid
  have hle := f.noncrossing
  have hhi := f.hi_valid
  have hcount := aligned.count
  refine ⟨hpos, by omega, ?_, ?_⟩
  · intro i hil hir
    have hi1 : 1 ≤ i := by omega
    rw [aligned.outside i hi1 hir]
    apply Finset.singleton_subset_iff.mpr
    apply (mem_sourceInterval_iff (f.hi - ell) f.hi f.hi_valid _).mpr
    have hval : ((f.lo + i - 1 : ℕ) : ZMod n).val = f.lo + i - 1 := by
      exact ZMod.val_natCast_of_lt (by omega)
    rw [hval]
    omega
  · intro a ha
    have hrange :=
      (mem_sourceInterval_iff (f.hi - ell) f.hi f.hi_valid a).mp ha
    let i := a.val - f.lo + 1
    have hi1 : 1 ≤ i := by dsimp [i]; omega
    have hil : r - ell ≤ i := by dsimp [i]; omega
    have hir : i < r := by dsimp [i]; omega
    refine ⟨i, hil, hir, ?_⟩
    rw [aligned.outside i hi1 hir]
    have hidx : f.lo + i - 1 = a.val := by dsimp [i]; omega
    simpa only [Finset.mem_singleton, hidx] using
      (ZMod.natCast_zmod_val a).symm

/-- Conditional code-side admission and actual assembly, retaining the same
named endpoint. The separately supplied alignment is the remaining
actual-history-to-symbolic-source bridge. -/
theorem CheckpointNamedAlignment.assembleR
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (ell : ℕ) (hpos : 0 < ell) (hbound : ell ≤ f.hi - f.lo) :
    ∃ (m : ℕ) (hm : NeZero m),
      letI : NeZero m := hm
      ∃ (final : Execution n (ZMod n))
        (lastNamed : LegalNamedPlacement n m (ZMod n)),
        m = r - ell + 1 ∧
        final.placed = lastNamed.placed ∧
        lastNamed.PositivelyOrdered ∧
        lastNamed.block 0 = f.carrier ∧
        lastNamed.block 1 = f.partnerR ell ∧
        CountedOutsideSchedule F f.carrier (ell - 1) s final ∧
        PartnerAssemblyInvariant f.carrier (f.partnerR ell) final := by
  have hrn : r ≤ n := by
    have hcount := aligned.count
    have hlo := f.lo_valid
    have hle := f.noncrossing
    have hhi := f.hi_valid
    omega
  exact RPartnerPrefix.assemble_named ell F f.carrier (f.partnerR ell)
    s first aligned.ordered hrn aligned.source aligned.carrier
    aligned.registered aligned.selected aligned.inside
    (clean_partner_assembly_invariant f.carrier (f.partnerR ell) s aligned.clean)
    (CheckpointNamedAlignment.admitR F f s first aligned ell hpos hbound)

theorem CheckpointNamedAlignment.assembleL
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (ell : ℕ) (hpos : 0 < ell) (hbound : ell ≤ f.hi - f.lo) :
    ∃ (m : ℕ) (hm : NeZero m),
      letI : NeZero m := hm
      ∃ (final : Execution n (ZMod n))
        (lastNamed : LegalNamedPlacement n m (ZMod n)),
        m = r - ell + 1 ∧
        final.placed = lastNamed.placed ∧
        lastNamed.PositivelyOrdered ∧
        lastNamed.block 0 = f.carrier ∧
        lastNamed.block ((m - 1 : ℕ) : ZMod m) = f.partnerL ell ∧
        CountedOutsideSchedule F f.carrier (ell - 1) s final ∧
        PartnerAssemblyInvariant f.carrier (f.partnerL ell) final := by
  have hrn : r ≤ n := by
    have hcount := aligned.count
    have hlo := f.lo_valid
    have hle := f.noncrossing
    have hhi := f.hi_valid
    omega
  exact LPartnerSuffix.assemble_named ell F f.carrier (f.partnerL ell)
    s first aligned.ordered hrn aligned.source aligned.carrier
    aligned.registered aligned.selected aligned.inside
    (clean_partner_assembly_invariant f.carrier (f.partnerL ell) s aligned.clean)
    (CheckpointNamedAlignment.admitL F f s first aligned ell hpos hbound)

/-- A code checkpoint on the R side is one continuous actual word: partner
assembly is followed by the unique selected absorption, not by `ell`
singleton absorptions. -/
theorem CheckpointNamedAlignment.realizeR_checkpoint
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (bNext : ℕ) (hnext : f.absorbed < bNext)
    (hmax : bNext ≤ n - 2) :
    let ell := bNext - f.absorbed
    let hbound := (f.checkpoint_gap bNext hnext hmax).2
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [checkpointRecord true f.carrier (f.partnerR ell)] ∧
      CleanOutside (f.nextR ell hbound).carrier (run F s word) := by
  dsimp
  have hgap := f.checkpoint_gap bNext hnext hmax
  obtain ⟨m, hm, final, lastNamed, hmEq, hplaced, hordered, hcarrier,
    hpartner, hschedule, hinvariant⟩ :=
    aligned.assembleR F f s first (bNext - f.absorbed) hgap.1 hgap.2
  letI : NeZero m := hm
  have hr : 2 ≤ m := by
    have hcount := aligned.count
    omega
  have hrn : m ≤ n := by
    have hcount := aligned.count
    have hhi := f.hi_valid
    have hle := f.noncrossing
    have hlo := f.lo_valid
    have hell := hgap.1
    omega
  obtain ⟨word, hreach, horigin, hchain, hclean⟩ :=
    realize_packed_R_checkpoint F f.carrier (f.partnerR (bNext - f.absorbed))
      s final hschedule.toSchedule lastNamed hordered hrn hr aligned.reachable
      hplaced hcarrier hpartner aligned.registered aligned.inside hinvariant
  refine ⟨word, hreach, horigin, hchain, ?_⟩
  simpa only [f.carrier_nextR (bNext - f.absorbed) hgap.2] using hclean

/-- The L-side version retains the parent-port order in the selected record. -/
theorem CheckpointNamedAlignment.realizeL_checkpoint
    {r : ℕ} [NeZero r]
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (first : LegalNamedPlacement n r (ZMod n))
    (aligned : CheckpointNamedAlignment F f s first)
    (bNext : ℕ) (hnext : f.absorbed < bNext)
    (hmax : bNext ≤ n - 2) :
    let ell := bNext - f.absorbed
    let hbound := (f.checkpoint_gap bNext hnext hmax).2
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [checkpointRecord false f.carrier (f.partnerL ell)] ∧
      CleanOutside (f.nextL ell hbound).carrier (run F s word) := by
  dsimp
  have hgap := f.checkpoint_gap bNext hnext hmax
  obtain ⟨m, hm, final, lastNamed, hmEq, hplaced, hordered, hcarrier,
    hpartner, hschedule, hinvariant⟩ :=
    aligned.assembleL F f s first (bNext - f.absorbed) hgap.1 hgap.2
  letI : NeZero m := hm
  have hr : 2 ≤ m := by
    have hcount := aligned.count
    omega
  have hrn : m ≤ n := by
    have hcount := aligned.count
    have hhi := f.hi_valid
    have hle := f.noncrossing
    have hlo := f.lo_valid
    have hell := hgap.1
    omega
  obtain ⟨word, hreach, horigin, hchain, hclean⟩ :=
    realize_gap_L_checkpoint F f.carrier (f.partnerL (bNext - f.absorbed))
      s final hschedule.toSchedule lastNamed hordered hrn hr aligned.reachable
      hplaced hcarrier hpartner aligned.registered aligned.inside hinvariant
  refine ⟨word, hreach, horigin, hchain, ?_⟩
  simpa only [f.carrier_nextL (bNext - f.absorbed) hgap.2] using hclean

/-- An actual clean checkpoint source determines its R partner and admits the
full batched checkpoint without a separately supplied naming certificate. -/
theorem CheckpointSourceFrontier.realizeR_checkpoint
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s)
    (bNext : ℕ) (hnext : f.absorbed < bNext)
    (hmax : bNext ≤ n - 2) :
    let ell := bNext - f.absorbed
    let hbound := (f.checkpoint_gap bNext hnext hmax).2
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [checkpointRecord true f.carrier (f.partnerR ell)] ∧
      CleanOutside (f.nextR ell hbound).carrier (run F s word) := by
  obtain ⟨r, hr, first, aligned⟩ :=
    f.exists_named_alignment F s reachable registered selected inside clean
  letI : NeZero r := hr
  exact aligned.realizeR_checkpoint F f s first bNext hnext hmax

/-- The same source facts admit the L checkpoint with its distinct ordered
parent-port record. -/
theorem CheckpointSourceFrontier.realizeL_checkpoint
    (F : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s)
    (bNext : ℕ) (hnext : f.absorbed < bNext)
    (hmax : bNext ≤ n - 2) :
    let ell := bNext - f.absorbed
    let hbound := (f.checkpoint_gap bNext hnext hmax).2
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [checkpointRecord false f.carrier (f.partnerL ell)] ∧
      CleanOutside (f.nextL ell hbound).carrier (run F s word) := by
  obtain ⟨r, hr, first, aligned⟩ :=
    f.exists_named_alignment F s reachable registered selected inside clean
  letI : NeZero r := hr
  exact aligned.realizeL_checkpoint F f s first bNext hnext hmax

end RegisteredAbsorptionChains
