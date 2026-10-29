import RegisteredAbsorptionChains.FiberParamDecode
import RegisteredAbsorptionChains.OutsideBlockAssembly
import RegisteredAbsorptionChains.SourceOrderInvariant
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

/-- A supplied outside-merge schedule and a correctly named final placement
form one literal word. Only the final placement adjustment is fusion-free. -/
theorem realize_rank_target_after_outside_schedule
    {n k t : ℕ} [NeZero n]
    (u : ℕ) (hu : 0 < u) (huk : u + k ≤ n)
    (hk : 0 < k) (ht : 0 < t)
    (params : RankFiberParams n k t)
    (F C : Finset (ZMod n))
    (start assembled : Execution n (ZMod n))
    (schedule : OutsideAssemblySchedule F C start assembled)
    (source : LegalNamedPlacement n (t + 1) (ZMod n))
    (source_eq : assembled.placed = source.placed)
    (source_order : source.PositivelyOrdered)
    (same_blocks : source.block =
      (ValidFiberPlacement.ofRankParams u hu huk hk ht params).toLegal.block) :
    ∃ assemblyWord suffix : List Letter,
      run F start assemblyWord = assembled ∧
      FusionFree F assembled suffix ∧
      run F start (assemblyWord ++ suffix) =
        { assembled with placed :=
          (ValidFiberPlacement.ofRankParams u hu huk hk ht params).target } ∧
      (run F start (assemblyWord ++ suffix)).origin = start.origin ∧
      (run F start (assemblyWord ++ suffix)).chain = start.chain := by
  obtain ⟨assemblyWord, hassembly, horigin, hchain⟩ := schedule.realize
  obtain ⟨suffix, hsuffix, hfree⟩ :=
    rankFiberParams_realize_from_named_source u hu huk hk ht params F
      assembled source source_eq source_order same_blocks
  refine ⟨assemblyWord, suffix, hassembly, hfree, ?_, ?_, ?_⟩
  · rw [run_append, hassembly, hsuffix]
  · calc
      (run F start (assemblyWord ++ suffix)).origin = assembled.origin := by
        rw [run_append, hassembly, hsuffix]
      _ = start.origin := horigin
  · calc
      (run F start (assemblyWord ++ suffix)).chain = assembled.chain := by
        rw [run_append, hassembly, hsuffix]
      _ = start.chain := hchain

/-- A complete carrier at a specified site, with no other occupied site. -/
def fullCarrierPlacement {n : ℕ} (B : Finset α) (q : ZMod n) :
    Placement n (Finset α) := fun site =>
  if site = q then some B else none

theorem fullCarrierPlacement_injective {n : ℕ} (B : Finset α) :
    Function.Injective (fullCarrierPlacement B : ZMod n → Placement n (Finset α)) := by
  intro q q' heq
  have hq := congrFun heq q
  by_contra hne
  simp [fullCarrierPlacement, hne] at hq

/-- The phase placements of one fixed carrier are distinct. This counts
placements, not fixed-chain summaries before their identity is established. -/
noncomputable def fullCarrierPlacements {n : ℕ} [NeZero n]
    (B : Finset α) : Finset (Placement n (Finset α)) := by
  classical
  exact Finset.univ.image (fullCarrierPlacement B)

theorem card_fullCarrierPlacements {n : ℕ} [NeZero n]
    (B : Finset α) :
    (fullCarrierPlacements (n := n) B).card = n := by
  classical
  simp only [fullCarrierPlacements]
  rw [Finset.card_image_of_injective _ (fullCarrierPlacement_injective B)]
  simp

theorem placementOfMap_fullCarrier {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (q : ZMod n)
    (hfiber : sourceFiber f q = Finset.univ) :
    placementOfMap f = fullCarrierPlacement (Finset.univ : Finset (ZMod n)) q := by
  have hconstant : ∀ a, f a = q := by
    intro a
    have ha : a ∈ sourceFiber f q := by rw [hfiber]; simp
    exact (mem_sourceFiber f a q).mp ha
  funext site
  by_cases hsite : site = q
  · subst site
    simp [placementOfMap, fullCarrierPlacement, hfiber]
  · have hempty : sourceFiber f site = ∅ := by
      ext a
      simp [sourceFiber, hconstant a, Ne.symm hsite]
    simp [placementOfMap, fullCarrierPlacement, hempty, hsite]

/-- In an actually source-ordered placement, a full carrier at one site
forces every other site to be empty. -/
theorem sourceOrdered_fullCarrier {n : ℕ} [NeZero n]
    (placed : Placement n (Finset (ZMod n)))
    (ordered : SourceOrdered placed) (q : ZMod n)
    (hq : placed q = some Finset.univ) :
    placed = fullCarrierPlacement (Finset.univ : Finset (ZMod n)) q := by
  obtain ⟨lift, hplaced⟩ := ordered
  rw [hplaced] at hq ⊢
  have hfiber := (placementOfMap_some_iff lift.position q Finset.univ).mp hq
  exact placementOfMap_fullCarrier lift.position q hfiber.1

theorem rotate_fullCarrierPlacement {n : ℕ} (B : Finset α)
    (q₀ q : ZMod n) :
    rotate (q - q₀) (fullCarrierPlacement B q₀) =
      fullCarrierPlacement B q := by
  funext site
  by_cases h : site = q
  · subst site
    have hphase : q - (q - q₀) = q₀ := by abel
    simp [rotate, fullCarrierPlacement, hphase]
  · have hsource : site - (q - q₀) ≠ q₀ := by
      intro heq
      apply h
      calc
        site = (site - (q - q₀)) + (q - q₀) := by abel
        _ = q₀ + (q - q₀) := by rw [heq]
        _ = q := by abel
    simp [rotate, fullCarrierPlacement, h, hsource]

/-- The `k=0` placement step needs no outside schedule. This assumes an
execution with the declared complete carrier; registering that execution and
identifying it with each fixed chain remain separate theorems. -/
theorem realize_full_carrier_rotation {n : ℕ} [NeZero n] [DecidableEq α]
    (F B : Finset α) (start : Execution n α)
    (q₀ q : ZMod n)
    (hsource : start.placed = fullCarrierPlacement B q₀) :
    ∃ word : List Letter,
      run F start word = { start with placed := fullCarrierPlacement B q } ∧
      FusionFree F start word := by
  refine ⟨pWord (q - q₀).val, ?_, fusionFree_pWord F start _⟩
  rw [run_rotation, hsource, rotate_fullCarrierPlacement]

/-- A reachable execution whose carrier is all atoms has exactly
the one-block placement, and its `n` phases are all attained without changing
its origin or selected chain. The chain-to-carrier identity is not assumed. -/
theorem realize_reachable_fullCarrier_phases {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (hn : 2 ≤ n) (reachable : ReachableFromSingleton F start.placed)
    (q₀ : ZMod n) (hcarrier : start.placed q₀ = some Finset.univ) :
    ∀ q : ZMod n, ∃ word : List Letter,
      run F start word =
        { start with placed := fullCarrierPlacement Finset.univ q } ∧
      FusionFree F start word := by
  have hsource : start.placed = fullCarrierPlacement Finset.univ q₀ :=
    sourceOrdered_fullCarrier start.placed
      (reachable_source_ordered F start.placed hn reachable) q₀ hcarrier
  intro q
  exact realize_full_carrier_rotation F Finset.univ start q₀ q hsource

/-- Reachability here is of the complete execution record, not merely of its
placed partition. -/
def ReachableExecution {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) : Prop :=
  ∃ word : List Letter, run F (singletonExecution n) word = s

/-- Actual executions with fixed origin and selected chain and a complete
current carrier. The full-carrier condition is intentionally explicit. -/
def FullCarrierFixedRecords {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (origin : Option (FusionRecord (ZMod n)))
    (chain : List (FusionRecord (ZMod n))) :
    Set (Execution n (ZMod n)) :=
  { s | ReachableExecution F s ∧ s.origin = origin ∧
    s.chain = chain ∧ ∃ q, s.placed q = some Finset.univ }

/-- Conditional `k=0` fiber classification. Once one complete-carrier
history exists, fixing its source-addressed records leaves exactly its `n`
physical phases; neither a symbolic-chain witness nor its carrier identity is
manufactured by this statement. -/
theorem fullCarrierFixedRecords_eq_phases {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (hn : 2 ≤ n)
    (base : Execution n (ZMod n))
    (hbase : base ∈ FullCarrierFixedRecords F base.origin base.chain) :
    FullCarrierFixedRecords F base.origin base.chain =
      Set.range (fun q : ZMod n =>
        { base with placed := fullCarrierPlacement Finset.univ q }) := by
  obtain ⟨⟨baseWord, hbaseWord⟩, _, _, ⟨q₀, hq₀⟩⟩ := hbase
  ext s
  constructor
  · intro hs
    obtain ⟨⟨word, hword⟩, horigin, hchain, ⟨q, hq⟩⟩ := hs
    have hsource : SourceOrdered s.placed :=
      reachable_source_ordered F s.placed hn
        ⟨word, congrArg Execution.placed hword⟩
    have hplaced := sourceOrdered_fullCarrier s.placed hsource q hq
    refine ⟨q, ?_⟩
    cases s with
    | mk placed origin chain =>
      cases base with
      | mk basePlaced baseOrigin baseChain =>
        simp_all
  · rintro ⟨q, rfl⟩
    have hreach : ReachableFromSingleton F base.placed :=
      ⟨baseWord, congrArg Execution.placed hbaseWord⟩
    obtain ⟨phaseWord, hphase, _⟩ :=
      realize_reachable_fullCarrier_phases F base hn hreach q₀ hq₀ q
    refine ⟨⟨baseWord ++ phaseWord, ?_⟩, rfl, rfl, ⟨q, ?_⟩⟩
    · rw [run_append, hbaseWord, hphase]
    · simp [fullCarrierPlacement]

theorem fullCarrierFixedRecords_card {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (hn : 2 ≤ n)
    (base : Execution n (ZMod n))
    (hbase : base ∈ FullCarrierFixedRecords F base.origin base.chain) :
    (FullCarrierFixedRecords F base.origin base.chain).ncard = n := by
  rw [fullCarrierFixedRecords_eq_phases F hn base hbase]
  have hinj : Function.Injective (fun q : ZMod n =>
      { base with placed := fullCarrierPlacement Finset.univ q }) := by
    intro q q' heq
    exact fullCarrierPlacement_injective Finset.univ
      (congrArg Execution.placed heq)
  rw [Set.ncard_range_of_injective hinj]
  simp

end RegisteredAbsorptionChains
