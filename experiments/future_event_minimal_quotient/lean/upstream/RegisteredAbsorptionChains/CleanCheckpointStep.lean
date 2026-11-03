import RegisteredAbsorptionChains.CleanChainWitness
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- `true` is R: carrier at port zero. `false` is L: carrier at port one. -/
def CheckpointPorts (side : Side)
    (placed : Placement n (Finset (ZMod n)))
    (C B : Finset (ZMod n)) : Prop :=
  if side then placed 0 = some C ∧ placed 1 = some B
  else placed 0 = some B ∧ placed 1 = some C

/-- The ordered record is part of the source-addressed chain; its parents
cannot be swapped after the fact. -/
def checkpointRecord (side : Side) (C B : Finset (ZMod n)) :
    FusionRecord (ZMod n) :=
  if side then ⟨C, B, C ∪ B⟩ else ⟨B, C, B ∪ C⟩

/-- At the end of partner assembly, only the carrier and the chosen partner
may be nonsingleton. The checkpoint port condition locates both packets. -/
def PartnerAssemblyShape (C B : Finset (ZMod n))
    (s : Execution n (ZMod n)) : Prop :=
  ∀ q D, s.placed q = some D →
    D = C ∨ D = B ∨ ∃ x, D = {x}

/-- The weaker invariant during partner assembly: the carrier remains a
separate packet; temporary nonsingleton outside packets may occur, but only
inside the prescribed partner block `B`. -/
def PartnerAssemblyInvariant (C B : Finset (ZMod n))
    (s : Execution n (ZMod n)) : Prop :=
  (∃ q, s.placed q = some C) ∧
    ∀ q D, s.placed q = some D →
      D = C ∨ (D.Nonempty ∧ D ⊆ B) ∨
        ∃ x, x ∉ B ∧ D = {x}

omit [NeZero n] in
/-- A clean checkpoint state begins a valid partner-assembly interval. -/
theorem clean_partner_assembly_invariant
    (C B : Finset (ZMod n)) (s : Execution n (ZMod n))
    (hclean : CleanOutside C s) :
    PartnerAssemblyInvariant C B s := by
  refine ⟨hclean.1, ?_⟩
  intro q D hD
  rcases hclean.2 q D hD with hcarrier | ⟨x, hsingle⟩
  · exact Or.inl hcarrier
  · by_cases hx : x ∈ B
    · exact Or.inr (Or.inl ⟨hsingle ▸ Finset.singleton_nonempty x,
        hsingle ▸ (by simpa using hx)⟩)
    · exact Or.inr (Or.inr ⟨x, hx, hsingle⟩)

/-- Moving the same named packets without fusion preserves the prescribed
partner subpacket condition. -/
theorem partner_invariant_same_named_blocks
    {r : ℕ} [NeZero r]
    (C B : Finset (ZMod n)) (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (source : s.placed = first.placed)
    (sameBlocks : first.block = second.block)
    (hinvariant : PartnerAssemblyInvariant C B s) :
    PartnerAssemblyInvariant C B { s with placed := second.placed } := by
  obtain ⟨qC, hC⟩ := hinvariant.1
  have hfirstC : first.placed qC = some C := source ▸ hC
  obtain ⟨iC, hiC⟩ := first.only_named qC (by simp [hfirstC])
  have hblockC : first.block iC = C :=
    Option.some.inj ((first.placed_at iC).symm.trans (hiC ▸ hfirstC))
  constructor
  · refine ⟨second.position iC, ?_⟩
    change second.placed (second.position iC) = some C
    rw [second.placed_at, ← sameBlocks, hblockC]
  · intro q D hD
    change second.placed q = some D at hD
    obtain ⟨i, hi⟩ := second.only_named q (by simp [hD])
    have hblock : second.block i = D :=
      Option.some.inj ((second.placed_at i).symm.trans (hi ▸ hD))
    have hsourceBlock : s.placed (first.position i) = some D := by
      rw [source, first.placed_at, sameBlocks, hblock]
    exact hinvariant.2 (first.position i) D hsourceBlock

omit [NeZero n] in
/-- One actual outside fusion of two subpackets of `B` preserves the weak
assembly invariant. It is not a clean-to-clean step unless `B` is complete. -/
theorem partner_invariant_after_outside_merge
    (F C B u v : Finset (ZMod n))
    (s : Execution n (ZMod n)) (hn : 2 ≤ n)
    (hbefore : PartnerAssemblyInvariant C B s)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hu : u.Nonempty) (huB : u ⊆ B) (hvB : v ⊆ B)
    (qC : ZMod n) (hC : s.placed qC = some C)
    (hq0 : qC ≠ 0) (hq1 : qC ≠ 1) :
    PartnerAssemblyInvariant C B (stepDefect F s) := by
  have hplaced : (stepDefect F s).placed = fusionPlacement s.placed :=
    stepDefect_placed F s
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  constructor
  · refine ⟨qC, ?_⟩
    rw [hplaced, fusionPlacement_other_site s.placed qC hq0 hq1]
    exact hC
  · intro q D hD
    rw [hplaced] at hD
    by_cases hq : q = 0
    · subst q
      have hmerged : fusionPlacement s.placed 0 = some (u ∪ v) := by
        simp [fusionPlacement, h0, h1]
      have hD' : D = u ∪ v :=
        (Option.some.inj (hmerged.symm.trans hD)).symm
      exact Or.inr (Or.inl ⟨hD' ▸ hu.mono (Finset.subset_union_left),
        hD' ▸ Finset.union_subset huB hvB⟩)
    · by_cases hq1 : q = 1
      · subst q
        simp [fusionPlacement, h10] at hD
      · have hold : s.placed q = some D := by
          simpa [fusionPlacement, hq, hq1] using hD
        exact hbefore.2 q D hold

/-- One supplied same-order placement stage yields a literal word that merges
two subpackets of `B` outside the carrier. The preparatory prefix is
fusion-free; the final defect is a real nonselected fusion. -/
theorem realize_one_partner_assembly_stage
    {r : ℕ} [NeZero r]
    (F C B u v : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (h0 : second.placed 0 = some u)
    (h1 : second.placed 1 = some v)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ C)
    (leftOutside : Disjoint C u) (rightOutside : Disjoint C v)
    (huB : u ⊆ B) (hvB : v ⊆ B)
    (qC : ZMod n) (hC : second.placed qC = some C)
    (hq0 : qC ≠ 0) (hq1 : qC ≠ 1)
    (hinvariant : PartnerAssemblyInvariant C B s) :
    ∃ word : List Letter,
      (run F s word).origin = s.origin ∧
      (run F s word).chain = s.chain ∧
      PartnerAssemblyInvariant C B (run F s word) := by
  obtain ⟨prep, hprep, hfree⟩ :=
    realize_same_oriented_placements F s first second hn hr source same
  have hpreparedInvariant : PartnerAssemblyInvariant C B (run F s prep) := by
    rw [hprep]
    exact partner_invariant_same_named_blocks C B s first second
      source same.1 hinvariant
  have hp0 : (run F s prep).placed 0 = some u := by
    simpa [hprep] using h0
  have hp1 : (run F s prep).placed 1 = some v := by
    simpa [hprep] using h1
  have hpC : (run F s prep).placed qC = some C := by
    simpa [hprep] using hC
  have hu : u.Nonempty := by
    obtain ⟨i, hi⟩ := second.only_named 0 (by simp [h0])
    have hblock : second.block i = u :=
      Option.some.inj ((second.placed_at i).symm.trans (hi ▸ h0))
    exact hblock ▸ second.block_nonempty i
  obtain ⟨huOutside, hvOutside⟩ :=
    outside_parents_not_selected F C u v selected inside
      leftOutside rightOutside
  have hrecords := run_prepared_outside_merge F s prep hfree u v
    hp0 hp1 registered huOutside hvOutside
  have hafter := partner_invariant_after_outside_merge F C B u v
    (run F s prep) hn hpreparedInvariant hp0 hp1 hu huB hvB
    qC hpC hq0 hq1
  refine ⟨prep ++ [.d], hrecords.2.1, hrecords.2.2, ?_⟩
  rw [run_append]
  exact hafter

/-- Once the whole partner packet `B` is present, disjointness of the actual
source-ordered partition rules out any distinct residual subpacket of `B`. -/
theorem partner_finished_shape
    (C B : Finset (ZMod n)) (s : Execution n (ZMod n))
    (ordered : SourceOrdered s.placed)
    (hinvariant : PartnerAssemblyInvariant C B s)
    (hB : ∃ q, s.placed q = some B) :
    PartnerAssemblyShape C B s := by
  obtain ⟨qB, hqB⟩ := hB
  obtain ⟨lift, hplaced⟩ := ordered
  have hordered : SourceOrdered s.placed := ⟨lift, hplaced⟩
  have hBne : B.Nonempty :=
    ((placementOfMap_some_iff lift.position qB B).mp (hplaced ▸ hqB)).2
  have hBmem : B ∈ placedBlocks s.placed :=
    (mem_placedBlocks s.placed B).mpr ⟨hBne, qB, hqB⟩
  intro q D hD
  rcases hinvariant.2 q D hD with hC | ⟨hDne, hDB⟩ | ⟨x, _, hsingle⟩
  · exact Or.inl hC
  · by_cases hEq : D = B
    · exact Or.inr (Or.inl hEq)
    · have hDmem : D ∈ placedBlocks s.placed :=
        (mem_placedBlocks s.placed D).mpr ⟨hDne, q, hD⟩
      have hdisj := sourceOrdered_blocks_disjoint s.placed hordered
        D B hDmem hBmem hEq
      obtain ⟨x, hx⟩ := hDne
      exact False.elim ((Finset.disjoint_left.mp hdisj) hx (hDB hx))
  · exact Or.inr (Or.inr ⟨x, hsingle⟩)

omit [NeZero n] in
/-- A registered defect event appends exactly one ordered selected record,
regardless of the number of atoms in the partner packet. -/
theorem checkpoint_step_records
    (F C B : Finset (ZMod n)) (side : Side)
    (s : Execution n (ZMod n))
    (hn : 2 ≤ n) (hregistered : s.origin.isSome = true)
    (hFC : F ⊆ C)
    (hports : CheckpointPorts side s.placed C B) :
    (stepDefect F s).origin = s.origin ∧
    (stepDefect F s).chain = s.chain ++ [checkpointRecord side C B] ∧
    (stepDefect F s).placed 0 = some (C ∪ B) ∧
    (stepDefect F s).placed 1 = none := by
  have hsome : s.origin ≠ none := by
    cases h : s.origin <;> simp_all
  have h10 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  cases side with
  | false =>
      obtain ⟨h0, h1⟩ := hports
      simp [checkpointRecord, stepDefect, fusionPlacement, h0, h1,
        hsome, hregistered, hFC, h10, Finset.union_comm]
  | true =>
      obtain ⟨h0, h1⟩ := hports
      simp [checkpointRecord, stepDefect, fusionPlacement, h0, h1,
        hsome, hregistered, hFC, h10]

/-- A common named packet enumeration carries the weak partner-assembly
shape through a fusion-free placement adjustment. -/
theorem partner_shape_same_named_blocks
    {r : ℕ} [NeZero r]
    (C B : Finset (ZMod n)) (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (source : s.placed = first.placed)
    (sameBlocks : first.block = second.block)
    (hshape : PartnerAssemblyShape C B s) :
    PartnerAssemblyShape C B { s with placed := second.placed } := by
  intro q D hD
  change second.placed q = some D at hD
  obtain ⟨i, hi⟩ := second.only_named q (by simp [hD])
  have hblock : second.block i = D :=
    Option.some.inj ((second.placed_at i).symm.trans (hi ▸ hD))
  have hsourceBlock : s.placed (first.position i) = some D := by
    rw [source, first.placed_at, sameBlocks, hblock]
  exact hshape (first.position i) D hsourceBlock

/-- In a legal named placement, the two checkpoint packets occur only at
the declared kernel ports. -/
theorem checkpoint_special_sites
    {r : ℕ} [NeZero r]
    (second : LegalNamedPlacement n r (ZMod n))
    (side : Side) (C B : Finset (ZMod n))
    (hports : CheckpointPorts side second.placed C B) :
    ∀ q D, second.placed q = some D →
      (D = C ∨ D = B) → q = 0 ∨ q = 1 := by
  cases side with
  | false =>
      obtain ⟨h0, h1⟩ := hports
      intro q D hD hspecial
      rcases hspecial with hC | hB
      · exact Or.inr (unique_named_block_site second C q 1 (hC ▸ hD) h1)
      · exact Or.inl (unique_named_block_site second B q 0 (hB ▸ hD) h0)
  | true =>
      obtain ⟨h0, h1⟩ := hports
      intro q D hD hspecial
      rcases hspecial with hC | hB
      · exact Or.inl (unique_named_block_site second C q 0 (hC ▸ hD) h0)
      · exact Or.inr (unique_named_block_site second B q 1 (hB ▸ hD) h1)

omit [NeZero n] in
/-- The assembled partner disappears into the selected carrier in one
fusion. All other occupied outside packets were singleton and stay so. -/
theorem checkpoint_step_clean
    (F C B : Finset (ZMod n)) (side : Side)
    (s : Execution n (ZMod n))
    (hn : 2 ≤ n) (hregistered : s.origin.isSome = true)
    (hFC : F ⊆ C)
    (hports : CheckpointPorts side s.placed C B)
    (hshape : PartnerAssemblyShape C B s)
    (hspecial : ∀ q D, s.placed q = some D →
      (D = C ∨ D = B) → q = 0 ∨ q = 1) :
    CleanOutside (C ∪ B) (stepDefect F s) := by
  have hrecords := checkpoint_step_records F C B side s hn hregistered hFC hports
  have hplaced : (stepDefect F s).placed = fusionPlacement s.placed :=
    stepDefect_placed F s
  constructor
  · exact ⟨0, hrecords.2.2.1⟩
  · intro q D hD
    by_cases hq0 : q = 0
    · subst q
      exact Or.inl (Option.some.inj (hD.symm.trans hrecords.2.2.1))
    by_cases hq1 : q = 1
    · subst q
      simp [hrecords.2.2.2] at hD
    · rw [hplaced] at hD
      have hold : s.placed q = some D := by
        simpa [fusionPlacement, hq0, hq1] using hD
      rcases hshape q D hold with hC | hB | ⟨x, hx⟩
      · rcases hspecial q D hold (Or.inl hC) with h | h
        · exact False.elim (hq0 h)
        · exact False.elim (hq1 h)
      · rcases hspecial q D hold (Or.inr hB) with h | h
        · exact False.elim (hq0 h)
        · exact False.elim (hq1 h)
      · exact Or.inr ⟨x, hx⟩

/-- A supplied actual partner-assembly schedule, followed by one fusion-free
placement adjustment and one defect letter, realizes one complete checkpoint.
The schedule's existence for every symbolic interval is not assumed here. -/
theorem realize_clean_checkpoint_from_schedule
    {r : ℕ} [NeZero r]
    (F C B : Finset (ZMod n)) (side : Side)
    (start assembled : Execution n (ZMod n))
    (schedule : OutsideAssemblySchedule F C start assembled)
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F start)
    (source : assembled.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (ports : CheckpointPorts side second.placed C B)
    (registered : start.origin.isSome = true)
    (inside : F ⊆ C)
    (shape : PartnerAssemblyShape C B assembled) :
    ∃ word : List Letter,
      ReachableExecution F (run F start word) ∧
      (run F start word).origin = start.origin ∧
      (run F start word).chain =
        start.chain ++ [checkpointRecord side C B] ∧
      CleanOutside (C ∪ B) (run F start word) := by
  obtain ⟨assemblyWord, hassembly, horigin, hchain⟩ := schedule.realize
  obtain ⟨prep, hprep, _⟩ :=
    realize_same_oriented_placements F assembled first second hn hr source same
  let prepared := run F assembled prep
  have hprepared : prepared = { assembled with placed := second.placed } := hprep
  have hregistered : prepared.origin.isSome = true := by
    rw [hprepared]
    simpa [horigin] using registered
  have hports : CheckpointPorts side prepared.placed C B := by
    simpa [hprepared] using ports
  have hshape : PartnerAssemblyShape C B prepared := by
    rw [hprepared]
    exact partner_shape_same_named_blocks C B assembled first second
      source same.1 shape
  have hspecial : ∀ q D, prepared.placed q = some D →
      (D = C ∨ D = B) → q = 0 ∨ q = 1 := by
    simpa [hprepared] using checkpoint_special_sites second side C B ports
  have hrecords := checkpoint_step_records F C B side prepared hn
    hregistered inside hports
  have hclean := checkpoint_step_clean F C B side prepared hn
    hregistered inside hports hshape hspecial
  let word := assemblyWord ++ prep ++ [.d]
  have hrun : run F start word = stepDefect F prepared := by
    dsimp [word]
    rw [List.append_assoc, run_append, hassembly, run_append]
    rfl
  obtain ⟨initialWord, hinitial⟩ := reachable
  refine ⟨word, ⟨initialWord ++ word, ?_⟩, ?_, ?_, ?_⟩
  · rw [run_append, hinitial]
  · rw [hrun, hrecords.1]
    simpa [hprepared] using horigin
  · rw [hrun, hrecords.2.1]
    simpa [hprepared] using
      congrArg (fun x => x ++ [checkpointRecord side C B]) hchain
  · rw [hrun]
    exact hclean

/-- The final strong shape can be *derived* from an assembled partner and the
weak assembly invariant, rather than supplied as a separate assertion. -/
theorem realize_clean_checkpoint_from_finished_partner
    {r : ℕ} [NeZero r]
    (F C B : Finset (ZMod n)) (side : Side)
    (start assembled : Execution n (ZMod n))
    (schedule : OutsideAssemblySchedule F C start assembled)
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F start)
    (source : assembled.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (ports : CheckpointPorts side second.placed C B)
    (registered : start.origin.isSome = true)
    (inside : F ⊆ C)
    (hinvariant : PartnerAssemblyInvariant C B assembled) :
    ∃ word : List Letter,
      ReachableExecution F (run F start word) ∧
      (run F start word).origin = start.origin ∧
      (run F start word).chain =
        start.chain ++ [checkpointRecord side C B] ∧
      CleanOutside (C ∪ B) (run F start word) := by
  obtain ⟨assemblyWord, hassembly, _, _⟩ := schedule.realize
  obtain ⟨initialWord, hinitial⟩ := reachable
  have hword : run F (singletonExecution n) (initialWord ++ assemblyWord) =
      assembled := by
    rw [run_append, hinitial, hassembly]
  have hfrom : ReachableFromSingleton F assembled.placed :=
    ⟨initialWord ++ assemblyWord, congrArg Execution.placed hword⟩
  have hordered : SourceOrdered assembled.placed :=
    reachable_source_ordered F assembled.placed hn hfrom
  have hBsecond : ∃ q, second.placed q = some B := by
    cases side with
    | false => exact ⟨0, ports.1⟩
    | true => exact ⟨1, ports.2⟩
  obtain ⟨qB, hqB⟩ := hBsecond
  obtain ⟨iB, hiB⟩ := second.only_named qB (by simp [hqB])
  have hblockB : second.block iB = B :=
    Option.some.inj ((second.placed_at iB).symm.trans (hiB ▸ hqB))
  have hB : ∃ q, assembled.placed q = some B := by
    refine ⟨first.position iB, ?_⟩
    rw [source, first.placed_at, same.1, hblockB]
  have hshape := partner_finished_shape C B assembled hordered hinvariant hB
  exact realize_clean_checkpoint_from_schedule F C B side start assembled
    schedule first second hn hr ⟨initialWord, hinitial⟩ source same ports
    registered inside hshape

/-- The singleton case needs no outside assembly. Unlike the older
carrier-at-zero lemma, this covers both ordered kernel-port orientations. -/
theorem realize_clean_singleton_checkpoint
    {r : ℕ} [NeZero r]
    (F C : Finset (ZMod n)) (x : ZMod n) (side : Side)
    (s : Execution n (ZMod n))
    (first second : LegalNamedPlacement n r (ZMod n))
    (hn : 2 ≤ n) (hr : 2 ≤ r)
    (reachable : ReachableExecution F s)
    (source : s.placed = first.placed)
    (same : SameOrientedCyclicOrder first second)
    (ports : CheckpointPorts side second.placed C {x})
    (registered : s.origin.isSome = true)
    (inside : F ⊆ C)
    (clean : CleanOutside C s) :
    ∃ word : List Letter,
      ReachableExecution F (run F s word) ∧
      (run F s word).origin = s.origin ∧
      (run F s word).chain =
        s.chain ++ [checkpointRecord side C {x}] ∧
      CleanOutside (C ∪ {x}) (run F s word) := by
  have shape : PartnerAssemblyShape C {x} s := by
    intro q D hD
    rcases clean.2 q D hD with hcarrier | hsingle
    · exact Or.inl hcarrier
    · exact Or.inr (Or.inr hsingle)
  exact realize_clean_checkpoint_from_schedule F C {x} side s s
    (OutsideAssemblySchedule.empty s) first second hn hr reachable
    source same ports registered inside shape

/-- Strictly increasing nonzero checkpoint indices, starting after `prev`. -/
def StrictCheckpointList : ℕ → List ℕ → Prop
  | _, [] => True
  | prev, b :: rest => prev < b ∧ StrictCheckpointList b rest

/-- The required number of nonselected fusions when each checkpoint partner
is assembled from singleton atoms. This is a specification, not a word count. -/
def checkpointOutsideCost : ℕ → List ℕ → ℕ
  | _, [] => 0
  | prev, b :: rest => (b - prev - 1) + checkpointOutsideCost b rest

def checkpointEnd : ℕ → List ℕ → ℕ
  | prev, [] => prev
  | _, b :: rest => checkpointEnd b rest

/-- The batch costs telescope: outside fusions plus selected absorptions
equal the final checkpoint index minus the starting index. -/
theorem checkpoint_cost_ledger (prev : ℕ) (bs : List ℕ)
    (hstrict : StrictCheckpointList prev bs) :
    checkpointOutsideCost prev bs + bs.length + prev =
      checkpointEnd prev bs := by
  induction bs generalizing prev with
  | nil => simp [checkpointOutsideCost, checkpointEnd]
  | cons b rest ih =>
      obtain ⟨hprev, hrest⟩ := hstrict
      have htail := ih b hrest
      simp only [checkpointOutsideCost, checkpointEnd, List.length_cons]
      omega

private def batchFourF : Finset (ZMod 4) := {0, 1}

private def batchFourWord : List Letter :=
  [.d, .p, .p, .d, .p, .d, .p, .d]

/-- Finite regression control: the `n=4`, `(0,R)` batch assembles `{2,3}`
outside the carrier and records its absorption only at the final defect. -/
private example :
    (run batchFourF (singletonExecution 4) [.d, .p, .p, .d]).chain = [] ∧
    (run batchFourF (singletonExecution 4) [.d, .p, .p, .d]).placed 0 =
      some ({2, 3} : Finset (ZMod 4)) ∧
    (run batchFourF (singletonExecution 4) batchFourWord).chain =
      [checkpointRecord true ({0, 1} : Finset (ZMod 4)) {2, 3}] ∧
    (run batchFourF (singletonExecution 4) batchFourWord).placed 0 =
      some (Finset.univ : Finset (ZMod 4)) := by
  refine ⟨rfl, by decide, rfl, by decide⟩

end RegisteredAbsorptionChains
