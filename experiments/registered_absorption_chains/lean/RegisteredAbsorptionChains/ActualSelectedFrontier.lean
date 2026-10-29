import RegisteredAbsorptionChains.CodeChainUniqueness
import RegisteredAbsorptionChains.NoSplitting
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- In an actual source-ordered placement, a nonempty source-marked set can
belong to only one current packet. No clean-outside hypothesis is used. -/
theorem sourceOrdered_selected_packet_unique
    (s : Execution n (ZMod n)) (F C D : Finset (ZMod n))
    (q r : ZMod n) (ordered : SourceOrdered s.placed)
    (selected : F.Nonempty)
    (hC : s.placed q = some C) (insideC : F ⊆ C)
    (hD : s.placed r = some D) (insideD : F ⊆ D) :
    q = r ∧ C = D := by
  obtain ⟨x, hx⟩ := selected
  obtain ⟨lift, hplaced⟩ := ordered
  have hq := (placementOfMap_some_iff lift.position q C).mp
    (hplaced ▸ hC)
  have hr := (placementOfMap_some_iff lift.position r D).mp
    (hplaced ▸ hD)
  have hxq : lift.position x = q := by
    exact (mem_sourceFiber lift.position x q).mp (hq.1.symm ▸ insideC hx)
  have hxr : lift.position x = r := by
    exact (mem_sourceFiber lift.position x r).mp (hr.1.symm ▸ insideD hx)
  have hqr : q = r := hxq.symm.trans hxr
  constructor
  · exact hqr
  · exact Option.some.inj (hC.symm.trans (hqr ▸ hD))

theorem sourceOrdered_distinct_packets_disjoint
    (s : Execution n (ZMod n)) (C D : Finset (ZMod n))
    (q r : ZMod n) (ordered : SourceOrdered s.placed)
    (hqr : q ≠ r) (hC : s.placed q = some C)
    (hD : s.placed r = some D) : Disjoint C D := by
  obtain ⟨lift, hplaced⟩ := ordered
  have hfC := (placementOfMap_some_iff lift.position q C).mp (hplaced ▸ hC)
  have hfD := (placementOfMap_some_iff lift.position r D).mp (hplaced ▸ hD)
  apply Finset.disjoint_left.mpr
  intro x hxC hxD
  have hxq := (mem_sourceFiber lift.position x q).mp (hfC.1.symm ▸ hxC)
  have hxr := (mem_sourceFiber lift.position x r).mp (hfD.1.symm ▸ hxD)
  exact hqr (hxq.symm.trans hxr)

/-- The selected packet persists under every real letter, and its entire
source-atom set can only grow. This remains true during unselected outside
fusions and does not require clean outside packets. -/
theorem sourceOrdered_selected_packet_step
    (s : Execution n (ZMod n)) (F C : Finset (ZMod n))
    (q : ZMod n) (a : Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) (selected : F.Nonempty)
    (hC : s.placed q = some C) (inside : F ⊆ C) :
    ∃ (q' : ZMod n) (C' : Finset (ZMod n)),
      (step F s a).placed q' = some C' ∧
      C ⊆ C' ∧ F ⊆ C' := by
  obtain ⟨x, hx⟩ := selected
  obtain ⟨lift, hplaced⟩ := ordered
  have hfiber := (placementOfMap_some_iff lift.position q C).mp
    (hplaced ▸ hC)
  let f' := forwardMapStep lift.position a
  let q' := f' x
  let C' := sourceFiber f' q'
  have hxq : lift.position x = q :=
    (mem_sourceFiber lift.position x q).mp (hfiber.1.symm ▸ inside hx)
  have hsubset : C ⊆ C' := by
    intro y hy
    have hyq : lift.position y = q :=
      (mem_sourceFiber lift.position y q).mp (hfiber.1.symm ▸ hy)
    have heq : f' y = q' := by
      cases a with
      | p => simp [f', q', forwardMapStep, hyq, hxq]
      | d => simp [f', q', forwardMapStep, hyq, hxq]
    exact (mem_sourceFiber f' y q').mpr heq
  have hnonempty : C'.Nonempty := ⟨x, by simp [C', q']⟩
  have hpacket : (step F s a).placed q' = some C' := by
    rw [step_placementOfMap F s lift.position a hn hplaced]
    exact (placementOfMap_some_iff f' q' C').mpr ⟨rfl, hnonempty⟩
  exact ⟨q', C', hpacket, hsubset, inside.trans hsubset⟩

theorem sourceOrdered_selected_packet_run
    (s : Execution n (ZMod n)) (F C : Finset (ZMod n))
    (q : ZMod n) (word : List Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) (selected : F.Nonempty)
    (hC : s.placed q = some C) (inside : F ⊆ C) :
    ∃ (q' : ZMod n) (C' : Finset (ZMod n)),
      (run F s word).placed q' = some C' ∧
      C ⊆ C' ∧ F ⊆ C' := by
  induction word generalizing s C q with
  | nil => exact ⟨q, C, by simpa [run] using hC, Finset.Subset.rfl, inside⟩
  | cons a rest ih =>
      obtain ⟨q₁, C₁, hstep, hsub, hinside⟩ :=
        sourceOrdered_selected_packet_step s F C q a hn
          ordered selected hC inside
      obtain ⟨q₂, C₂, hrest, hsub₂, hinside₂⟩ :=
        ih (step F s a) C₁ q₁ (step_ordered F s a hn ordered)
          hstep hinside
      exact ⟨q₂, C₂, by simpa [run] using hrest,
        hsub.trans hsub₂, hinside₂⟩

/-- A defect step which does not select the tracked packet leaves its atom
set unchanged, even when two unrelated outside packets merge. -/
theorem actual_unselected_carrier_defect
    (s : Execution n (ZMod n)) (F C : Finset (ZMod n))
    (q : ZMod n) (hC : s.placed q = some C) (inside : F ⊆ C)
    (unselected : ∀ u v : Finset (ZMod n),
      s.placed 0 = some u → s.placed 1 = some v →
        ¬(F ⊆ u ∨ F ⊆ v)) :
    ∃ q' : ZMod n, (stepDefect F s).placed q' = some C := by
  by_cases hq0 : q = 0
  · subst q
    cases h1 : s.placed 1 with
    | none =>
        refine ⟨0, ?_⟩
        simp [stepDefect_placed, fusionPlacement, hC, h1]
    | some v =>
        exact False.elim ((unselected C v hC h1) (Or.inl inside))
  by_cases hq1 : q = 1
  · subst q
    cases h0 : s.placed 0 with
    | none =>
        refine ⟨0, ?_⟩
        simp [stepDefect_placed, fusionPlacement, hC, h0]
    | some u =>
        exact False.elim ((unselected u C h0 hC) (Or.inr inside))
  refine ⟨q, ?_⟩
  simp [stepDefect_placed, fusionPlacement, hq0, hq1, hC]

/-- The nonselected part of an actual word step preserves the recorded
carrier block; only its physical position may change. -/
theorem actual_unselected_carrier_step
    (s : Execution n (ZMod n)) (F C : Finset (ZMod n))
    (q : ZMod n) (a : Letter)
    (hC : s.placed q = some C) (inside : F ⊆ C)
    (unselected : a = .p ∨
      (∀ u v : Finset (ZMod n),
        s.placed 0 = some u → s.placed 1 = some v →
          ¬(F ⊆ u ∨ F ⊆ v))) :
    ∃ q' : ZMod n, (step F s a).placed q' = some C := by
  cases a with
  | p =>
      refine ⟨q + 1, ?_⟩
      simpa [step, rotate, add_sub_cancel_right] using hC
  | d =>
      rcases unselected with hbad | hno
      · cases hbad
      · exact actual_unselected_carrier_defect s F C q hC inside hno

/-- Any genuine selected merger strictly enlarges its source-addressed
carrier, even if the outside partner was assembled earlier. -/
theorem actual_selected_partner_strict
    (s : Execution n (ZMod n)) (C B : Finset (ZMod n))
    (side : Side) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (ports : CheckpointPorts side s.placed C B) :
    B.Nonempty ∧ C.card < (C ∪ B).card := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro heq
    have h10 : (1 : ZMod n) = 0 := heq.symm
    have := ZMod.one_eq_zero_iff.mp h10
    omega
  have hsizes (qC qB : ZMod n) (hqr : qC ≠ qB)
      (hC : s.placed qC = some C) (hB : s.placed qB = some B) :
      B.Nonempty ∧ C.card < (C ∪ B).card := by
    obtain ⟨lift, hplaced⟩ := ordered
    have hnonempty : B.Nonempty :=
      ((placementOfMap_some_iff lift.position qB B).mp (hplaced ▸ hB)).2
    have hdisj := sourceOrdered_distinct_packets_disjoint
      s C B qC qB ⟨lift, hplaced⟩ hqr hC hB
    have hcard : (C ∪ B).card = C.card + B.card :=
      Finset.card_union_of_disjoint hdisj
    exact ⟨hnonempty, by have := Finset.card_pos.mpr hnonempty; omega⟩
  cases side with
  | false => exact hsizes 1 0 h01.symm ports.2 ports.1
  | true => exact hsizes 0 1 h01 ports.1 ports.2

theorem actual_selected_checkpoint_increases
    (s : Execution n (ZMod n)) (C B : Finset (ZMod n))
    (side : Side) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (inside : selectedPair n ⊆ C)
    (ports : CheckpointPorts side s.placed C B) :
    C.card - 2 < (C ∪ B).card - 2 := by
  have hcard := (actual_selected_partner_strict s C B side hn ordered ports).2
  have hpair : (selectedPair n).card = 2 := by
    have h01 : (0 : ZMod n) ≠ 1 := by
      intro heq
      have := ZMod.one_eq_zero_iff.mp heq.symm
      omega
    simp [selectedPair, h01]
  have hbase : 2 ≤ C.card := by
    have := Finset.card_le_card inside
    omega
  omega

/-- If a genuine defect step is selected, the parent containing `F` is the
unique current carrier. This is a statement about one actual state and one
actual letter, with no clean-outside or singleton-partner assumption. -/
theorem actual_selected_step_uses_carrier
    (s : Execution n (ZMod n)) (F C u v : Finset (ZMod n))
    (q : ZMod n) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) (selected : F.Nonempty)
    (hC : s.placed q = some C) (inside : F ⊆ C)
    (registered : s.origin.isSome = true)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hselected : F ⊆ u ∨ F ⊆ v) :
    ∃ (side : Side) (B : Finset (ZMod n)),
      CheckpointPorts side s.placed C B ∧
      (stepDefect F s).origin = s.origin ∧
      (stepDefect F s).chain =
        s.chain ++ [checkpointRecord side C B] ∧
      (stepDefect F s).placed 0 = some (C ∪ B) := by
  rcases hselected with hu | hv
  · obtain ⟨hq, hCu⟩ := sourceOrdered_selected_packet_unique
      s F C u q 0 ordered selected hC inside h0 hu
    subst u
    have hports : CheckpointPorts true s.placed C v := by
      exact ⟨h0, h1⟩
    obtain ⟨horigin, hchain, hplaced, _⟩ :=
      checkpoint_step_records F C v true s hn registered inside hports
    exact ⟨true, v, hports, horigin, hchain, hplaced⟩
  · obtain ⟨hq, hCv⟩ := sourceOrdered_selected_packet_unique
      s F C v q 1 ordered selected hC inside h1 hv
    subst v
    have hports : CheckpointPorts false s.placed C u := by
      exact ⟨h0, h1⟩
    obtain ⟨horigin, hchain, hplaced, _⟩ :=
      checkpoint_step_records F C u false s hn registered inside hports
    exact ⟨false, u, hports, horigin, hchain, hplaced⟩

/-- The last selected record, or the registration event before the first
selected merger, names the current carrier atom set. -/
def recordedCarrierResult (s : Execution n (ZMod n)) : Option (Finset (ZMod n)) :=
  (s.chain.getLast?.map FusionRecord.result).or
    (s.origin.map FusionRecord.result)

def RecordedCarrier (F : Finset (ZMod n)) (s : Execution n (ZMod n)) : Prop :=
  ∃ (q : ZMod n) (C : Finset (ZMod n)),
    s.placed q = some C ∧ F ⊆ C ∧ recordedCarrierResult s = some C

theorem recordedCarrierResult_append
    (s : Execution n (ZMod n)) (rho : FusionRecord (ZMod n)) :
    recordedCarrierResult {s with chain := s.chain ++ [rho]} =
      some rho.result := by
  simp [recordedCarrierResult]

/-- For a registered actual state, one real letter preserves the agreement
between the recorded carrier and the physical packet containing `F`. -/
theorem actual_registered_carrier_step
    (s : Execution n (ZMod n)) (F : Finset (ZMod n)) (a : Letter)
    (hn : 2 ≤ n) (ordered : SourceOrdered s.placed)
    (selected : F.Nonempty) (registered : s.origin.isSome = true)
    (aligned : RecordedCarrier F s) :
    (step F s a).origin.isSome = true ∧
      RecordedCarrier F (step F s a) := by
  obtain ⟨q, C, hC, inside, hrecord⟩ := aligned
  cases a with
  | p =>
      refine ⟨registered, ⟨q + 1, C, ?_, inside, ?_⟩⟩
      · simpa [step, rotate, add_sub_cancel_right] using hC
      · simpa [step, recordedCarrierResult] using hrecord
  | d =>
      cases h0 : s.placed 0 with
      | none =>
          have hno : ∀ u v : Finset (ZMod n),
              s.placed 0 = some u → s.placed 1 = some v →
                ¬(F ⊆ u ∨ F ⊆ v) := by
            intro u v hu _
            simp [h0] at hu
          obtain ⟨q', hC'⟩ :=
            actual_unselected_carrier_defect s F C q hC inside hno
          have hsame : (stepDefect F s).origin = s.origin ∧
              (stepDefect F s).chain = s.chain := by
            simp [stepDefect, h0]
          refine ⟨by simpa [step, hsame.1] using registered,
            ⟨q', C, hC', inside, ?_⟩⟩
          change recordedCarrierResult (stepDefect F s) = some C
          simpa [recordedCarrierResult, hsame.1, hsame.2] using hrecord
      | some u =>
          cases h1 : s.placed 1 with
          | none =>
              have hno : ∀ u v : Finset (ZMod n),
                  s.placed 0 = some u → s.placed 1 = some v →
                    ¬(F ⊆ u ∨ F ⊆ v) := by
                intro u v _ hv
                simp [h1] at hv
              obtain ⟨q', hC'⟩ :=
                actual_unselected_carrier_defect s F C q hC inside hno
              have hsame : (stepDefect F s).origin = s.origin ∧
                  (stepDefect F s).chain = s.chain := by
                simp [stepDefect, h0, h1]
              refine ⟨by simpa [step, hsame.1] using registered,
                ⟨q', C, hC', inside, ?_⟩⟩
              change recordedCarrierResult (stepDefect F s) = some C
              simpa [recordedCarrierResult, hsame.1, hsame.2] using hrecord
          | some v =>
              by_cases hsel : F ⊆ u ∨ F ⊆ v
              · obtain ⟨side, B, hports, horigin, hchain, hplaced⟩ :=
                  actual_selected_step_uses_carrier s F C u v q hn ordered
                    selected hC inside registered h0 h1 hsel
                refine ⟨by simpa [step, horigin] using registered,
                  ⟨0, C ∪ B, hplaced, inside.trans Finset.subset_union_left,
                    ?_⟩⟩
                change recordedCarrierResult (stepDefect F s) = some (C ∪ B)
                cases side <;>
                  simp [recordedCarrierResult, hchain,
                    checkpointRecord, Finset.union_comm]
              · have hno : ∀ u' v' : Finset (ZMod n),
                    s.placed 0 = some u' → s.placed 1 = some v' →
                      ¬(F ⊆ u' ∨ F ⊆ v') := by
                  intro u' v' hu hv
                  have huu : u = u' := Option.some.inj (h0.symm.trans hu)
                  have hvv : v = v' := Option.some.inj (h1.symm.trans hv)
                  subst u'
                  subst v'
                  exact hsel
                obtain ⟨q', hC'⟩ :=
                  actual_unselected_carrier_defect s F C q hC inside hno
                have hsame : (stepDefect F s).origin = s.origin ∧
                    (stepDefect F s).chain = s.chain := by
                  cases horigin : s.origin with
                  | none => simp [horigin] at registered
                  | some origin =>
                      simp [stepDefect, h0, h1, horigin, hsel]
                refine ⟨by simpa [step, hsame.1] using registered,
                  ⟨q', C, hC', inside, ?_⟩⟩
                change recordedCarrierResult (stepDefect F s) = some C
                simpa [recordedCarrierResult, hsame.1, hsame.2] using hrecord

/-- The unregistered state has no selected records. Once registration occurs,
the latest selected record always names one actual packet containing `F`. -/
def ActualCarrierTrace (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) : Prop :=
  (s.origin = none ∧ s.chain = []) ∨
    (s.origin.isSome = true ∧ RecordedCarrier F s)

theorem actual_carrier_trace_step
    (s : Execution n (ZMod n)) (F : Finset (ZMod n))
    (a : Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) (selected : F.Nonempty)
    (trace : ActualCarrierTrace F s) :
    ActualCarrierTrace F (step F s a) := by
  rcases trace with ⟨horigin, hchain⟩ | ⟨hregistered, hcarrier⟩
  · cases a with
    | p =>
        left
        simpa [step, horigin, hchain]
    | d =>
        cases h0 : s.placed 0 with
        | none =>
            left
            simp [step, stepDefect, h0, horigin, hchain]
        | some u =>
            cases h1 : s.placed 1 with
            | none =>
                left
                simp [step, stepDefect, h0, h1, horigin, hchain]
            | some v =>
                by_cases hregister : u ∪ v = F
                · right
                  have hplaced : (stepDefect F s).placed 0 = some F := by
                    simpa [stepDefect_placed, fusionPlacement, h0, h1,
                      hregister]
                  have hnew : (stepDefect F s).origin =
                      some ⟨u, v, u ∪ v⟩ ∧
                      (stepDefect F s).chain = [] := by
                    simp [stepDefect, h0, h1, horigin, hchain,
                      hregister]
                  refine ⟨by simp [step, hnew.1],
                    ⟨0, F, hplaced, Finset.Subset.rfl, ?_⟩⟩
                  change recordedCarrierResult (stepDefect F s) = some F
                  simp [recordedCarrierResult, hnew.1, hnew.2,
                    hregister]
                · left
                  simp [step, stepDefect, h0, h1, horigin, hchain,
                    hregister]
  · exact Or.inr (actual_registered_carrier_step s F a hn ordered
      selected hregistered hcarrier)

theorem actual_carrier_trace_run
    (s : Execution n (ZMod n)) (F : Finset (ZMod n))
    (word : List Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed) (selected : F.Nonempty)
    (trace : ActualCarrierTrace F s) :
    ActualCarrierTrace F (run F s word) := by
  induction word generalizing s with
  | nil => simpa [run] using trace
  | cons a rest ih =>
      change ActualCarrierTrace F (run F (step F s a) rest)
      exact ih (step F s a) (step_ordered F s a hn ordered)
        (actual_carrier_trace_step s F a hn ordered selected trace)

/-- For every actual registered history from the singleton seed, the last
selected record (or the origin before any absorption) identifies the whole
current carrier packet. -/
theorem actual_registered_carrier_from_seed
    (F : Finset (ZMod n)) (word : List Letter)
    (hn : 2 ≤ n) (selected : F.Nonempty)
    (registered : (run F (singletonExecution n) word).origin.isSome = true) :
    RecordedCarrier F (run F (singletonExecution n) word) := by
  have htrace : ActualCarrierTrace F (run F (singletonExecution n) word) :=
    actual_carrier_trace_run (singletonExecution n) F word hn
      singletonExecution_ordered selected (Or.inl ⟨rfl, rfl⟩)
  rcases htrace with hpre | hpost
  · simp [hpre.1] at registered
  · exact hpost.2

/-- A cyclic source arc containing atom zero has a linearly convex
complement. In particular the complement of a registered carrier cannot
split into two source intervals. -/
theorem selected_arc_complement_convex
    (C : Finset (ZMod n)) (zero : (0 : ZMod n) ∈ C)
    (arc : CyclicSourceArc C) :
    LinearSourceConvex (Finset.univ \ C) := by
  rcases arc with hlinear | ⟨_, hcomplement⟩
  · intro x y z hxy hyz hzn hx _
    have hylt : y < n := by omega
    simp only [Finset.mem_sdiff, Finset.mem_univ, true_and] at hx ⊢
    intro hy
    have hxC := hlinear 0 x y (by omega) hxy hylt
      (by simpa using zero) hy
    exact hx hxC
  · exact hcomplement

theorem actual_selected_complement_convex
    (s : Execution n (ZMod n)) (C : Finset (ZMod n))
    (q : ZMod n) (ordered : SourceOrdered s.placed)
    (hC : s.placed q = some C)
    (inside : selectedPair n ⊆ C) :
    LinearSourceConvex (Finset.univ \ C) := by
  have hzero : (0 : ZMod n) ∈ C := inside (by simp [selectedPair])
  exact selected_arc_complement_convex C hzero
    (sourceOrdered_blocks_are_cyclic_arcs s.placed ordered q C hC).2

/-- A nonempty linearly convex atom set has unique endpoint values, hence
is exactly one source interval rather than merely a convexity predicate. -/
theorem nonempty_linear_set_eq_sourceInterval
    (B : Finset (ZMod n)) (nonempty : B.Nonempty)
    (convex : LinearSourceConvex B) :
    ∃ lo hi : ℕ, lo < hi ∧ hi ≤ n ∧ B = sourceInterval lo hi := by
  let vals := B.image ZMod.val
  have hvals : vals.Nonempty := nonempty.image ZMod.val
  let lo := vals.min' hvals
  let top := vals.max' hvals
  have hlomem : lo ∈ vals := Finset.min'_mem vals hvals
  have htopmem : top ∈ vals := Finset.max'_mem vals hvals
  obtain ⟨a, ha, haval⟩ := Finset.mem_image.mp hlomem
  obtain ⟨b, hb, hbval⟩ := Finset.mem_image.mp htopmem
  have hlo_top : lo ≤ top := by
    exact Finset.min'_le vals top htopmem
  have htop_n : top < n := by
    simpa [top, ← hbval] using b.val_lt
  refine ⟨lo, top + 1, by omega, by omega, ?_⟩
  ext x
  rw [mem_sourceInterval_iff lo (top + 1) (by omega)]
  constructor
  · intro hx
    have hxval : x.val ∈ vals := Finset.mem_image.mpr ⟨x, hx, rfl⟩
    have hmin : lo ≤ x.val := Finset.min'_le vals x.val hxval
    have hmax : x.val ≤ top := Finset.le_max' vals x.val hxval
    omega
  · intro hx
    have hlo_eq : (lo : ZMod n) = a := by
      rw [← haval]
      simp
    have htop_eq : (top : ZMod n) = b := by
      rw [← hbval]
      simp
    have hm := convex lo x.val top hx.1 (by omega) htop_n
      (by simpa [hlo_eq] using ha) (by simpa [htop_eq] using hb)
    simpa using hm

/-- Every actual selected carrier admits the same source-interval frontier
type as the symbolic decoder, without any clean-outside condition. -/
theorem actual_selected_has_frontier
    (s : Execution n (ZMod n)) (C : Finset (ZMod n))
    (q : ZMod n) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (hC : s.placed q = some C)
    (inside : selectedPair n ⊆ C) :
    ∃ f : CheckpointSourceFrontier n, f.carrier = C := by
  let B := Finset.univ \ C
  have hconvex : LinearSourceConvex B :=
    actual_selected_complement_convex s C q ordered hC inside
  have h0not : (0 : ZMod n) ∉ B := by
    have hzeroC : (0 : ZMod n) ∈ C :=
      inside (show (0 : ZMod n) ∈ selectedPair n by simp [selectedPair])
    simpa [B] using hzeroC
  have h1not : (1 : ZMod n) ∉ B := by
    have honeC : (1 : ZMod n) ∈ C :=
      inside (show (1 : ZMod n) ∈ selectedPair n by simp [selectedPair])
    simpa [B] using honeC
  by_cases hB : B.Nonempty
  · obtain ⟨lo, hi, hlohi, hhin, hinterval⟩ :=
      nonempty_linear_set_eq_sourceInterval B hB hconvex
    have hlo : 2 ≤ lo := by
      have hmember : (lo : ZMod n) ∈ B := by
        rw [hinterval, mem_sourceInterval_iff lo hi hhin]
        have hln : lo < n := by omega
        simpa [ZMod.val_natCast_of_lt hln] using
          (show lo ≤ lo ∧ lo < hi by omega)
      by_contra hbad
      have hlo01 : lo = 0 ∨ lo = 1 := by omega
      rcases hlo01 with rfl | rfl
      · exact h0not (by simpa using hmember)
      · exact h1not (by simpa using hmember)
    let f : CheckpointSourceFrontier n :=
      ⟨lo, hi, hlo, hlohi.le, hhin⟩
    refine ⟨f, ?_⟩
    have hcomp : f.remaining = B := by
      exact hinterval.symm
    rw [f.carrier_eq_compl_remaining, hcomp]
    ext a
    simp [B]
  · have hEmpty : B = ∅ := Finset.not_nonempty_iff_eq_empty.mp hB
    let f : CheckpointSourceFrontier n :=
      ⟨n, n, hn, le_refl n, le_refl n⟩
    refine ⟨f, ?_⟩
    have hcomp : f.remaining = B := by
      rw [hEmpty]
      simp [f, CheckpointSourceFrontier.remaining, sourceInterval]
    rw [f.carrier_eq_compl_remaining, hcomp]
    ext a
    simp [B]

/-- Actual outside packets cannot wrap across source zero, because the
selected carrier contains that atom. They are genuine linear subintervals
of the current complementary source interval. -/
theorem actual_outside_packet_linear
    (s : Execution n (ZMod n)) (C B : Finset (ZMod n))
    (qC qB : ZMod n) (ordered : SourceOrdered s.placed)
    (distinct : qC ≠ qB)
    (hC : s.placed qC = some C) (hB : s.placed qB = some B)
    (zero : (0 : ZMod n) ∈ C) :
    B.Nonempty ∧ LinearSourceConvex B ∧ B ⊆ Finset.univ \ C := by
  have hdisjoint := sourceOrdered_distinct_packets_disjoint
    s C B qC qB ordered distinct hC hB
  obtain ⟨hnonempty, harc⟩ :=
    sourceOrdered_blocks_are_cyclic_arcs s.placed ordered qB B hB
  have hzero_not_B : (0 : ZMod n) ∉ B :=
    fun hz => Finset.disjoint_left.mp hdisjoint zero hz
  have hlinear : LinearSourceConvex B := by
    rcases harc with hlinear | ⟨hzero, _⟩
    · exact hlinear
    · exact False.elim (hzero_not_B hzero)
  refine ⟨hnonempty, hlinear, ?_⟩
  intro a ha
  simp only [Finset.mem_sdiff, Finset.mem_univ, true_and]
  exact fun hca => Finset.disjoint_left.mp hdisjoint hca ha

/-- In positive physical port order, the selected carrier's next occupied
packet begins at the left endpoint of its complementary source interval. -/
theorem actual_right_partner_contains_lo
    (s : Execution n (ZMod n)) (f : CheckpointSourceFrontier n)
    (B : Finset (ZMod n)) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some f.carrier)
    (h1 : s.placed 1 = some B) :
    (f.lo : ZMod n) ∈ B := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h.symm
    omega
  obtain ⟨hBne, _, hsubset⟩ := actual_outside_packet_linear
    s f.carrier B 0 1 ordered h01 h0 h1
    (by simp [CheckpointSourceFrontier.carrier, selectedPair])
  obtain ⟨b, hb⟩ := hBne
  have hbrem : b ∈ f.remaining := by
    have hnotC := (Finset.mem_sdiff.mp (hsubset hb)).2
    exact (f.not_mem_carrier_iff_remaining b).mp hnotC
  have hbval := (mem_sourceInterval_iff f.lo f.hi f.hi_valid b).mp hbrem
  have hlt : f.lo < f.hi := by omega
  have hlo_n : f.lo < n := by
    have := f.hi_valid
    omega
  have hlo_rem : (f.lo : ZMod n) ∈ f.remaining := by
    change (f.lo : ZMod n) ∈ sourceInterval f.lo f.hi
    rw [mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simpa [ZMod.val_natCast_of_lt hlo_n] using
      (show f.lo ≤ f.lo ∧ f.lo < f.hi by omega)
  by_contra hlo_not_B
  obtain ⟨lift, hplaced⟩ := ordered
  have hCfiber := (placementOfMap_some_iff lift.position 0 f.carrier).mp
    (hplaced ▸ h0)
  have hBfiber := (placementOfMap_some_iff lift.position 1 B).mp
    (hplaced ▸ h1)
  have hposition0 : lift.position 0 = 0 := by
    apply (mem_sourceFiber lift.position 0 0).mp
    rw [hCfiber.1]
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hpositionb : lift.position b = 1 := by
    apply (mem_sourceFiber lift.position b 1).mp
    rw [hBfiber.1]
    exact hb
  have hpositionlo_ne0 : lift.position (f.lo : ZMod n) ≠ 0 := by
    intro heq
    have hmem : (f.lo : ZMod n) ∈ f.carrier := by
      rw [← hCfiber.1]
      exact (mem_sourceFiber lift.position _ 0).mpr heq
    exact (f.not_mem_carrier_iff_remaining _).mpr hlo_rem hmem
  have hpositionlo_ne1 : lift.position (f.lo : ZMod n) ≠ 1 := by
    intro heq
    have hmem : (f.lo : ZMod n) ∈ B := by
      rw [← hBfiber.1]
      exact (mem_sourceFiber lift.position _ 1).mpr heq
    exact hlo_not_B hmem
  have hbgt : f.lo < b.val := by
    have hne : f.lo ≠ b.val := by
      intro heq
      have hbeq : b = (f.lo : ZMod n) := by
        calc
          b = (b.val : ZMod n) := (ZMod.natCast_zmod_val b).symm
          _ = (f.lo : ZMod n) := by rw [← heq]
      exact hlo_not_B (hbeq ▸ hb)
    omega
  have horder := lift.distinct_blocks_preserve_order
    (f.lo : ZMod n) b
    (by simpa [ZMod.val_natCast_of_lt hlo_n] using hbgt)
    (by simpa [hpositionb] using hpositionlo_ne1)
    (by simpa [hpositionb, hposition0] using h01.symm)
  have hval1 : (1 : ZMod n).val = 1 := by
    simpa only [Nat.cast_one] using
      (ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega))
  have hsmallZ : ((lift.position (f.lo : ZMod n)).val : ℤ) < 1 := by
    simpa only [hposition0, hpositionb, sub_zero, hval1,
      Int.ofNat_one] using horder.2
  have hsmall : (lift.position (f.lo : ZMod n)).val < 1 := by
    exact_mod_cast hsmallZ
  have hz : lift.position (f.lo : ZMod n) = 0 := by
    have hv : (lift.position (f.lo : ZMod n)).val = 0 := by omega
    calc
      lift.position (f.lo : ZMod n) =
          ((lift.position (f.lo : ZMod n)).val : ZMod n) :=
        (ZMod.natCast_zmod_val _).symm
      _ = 0 := by simp [hv]
  exact hpositionlo_ne0 hz

/-- With the carrier at port one, the preceding source packet reaches the
right endpoint of the complementary source interval. -/
theorem actual_left_partner_contains_hi_pred
    (s : Execution n (ZMod n)) (f : CheckpointSourceFrontier n)
    (B : Finset (ZMod n)) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (h0 : s.placed 0 = some B)
    (h1 : s.placed 1 = some f.carrier) :
    ((f.hi - 1 : ℕ) : ZMod n) ∈ B := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h.symm
    omega
  obtain ⟨hBne, _, hsubset⟩ := actual_outside_packet_linear
    s f.carrier B 1 0 ordered h01.symm h1 h0
    (by simp [CheckpointSourceFrontier.carrier, selectedPair])
  obtain ⟨b, hb⟩ := hBne
  have hbrem : b ∈ f.remaining := by
    have hnotC := (Finset.mem_sdiff.mp (hsubset hb)).2
    exact (f.not_mem_carrier_iff_remaining b).mp hnotC
  have hbval := (mem_sourceInterval_iff f.lo f.hi f.hi_valid b).mp hbrem
  have hlt : f.lo < f.hi := by omega
  have hlast_n : f.hi - 1 < n := by
    have := f.hi_valid
    omega
  have hlast_rem : ((f.hi - 1 : ℕ) : ZMod n) ∈ f.remaining := by
    change ((f.hi - 1 : ℕ) : ZMod n) ∈ sourceInterval f.lo f.hi
    rw [mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simpa [ZMod.val_natCast_of_lt hlast_n] using
      (show f.lo ≤ f.hi - 1 ∧ f.hi - 1 < f.hi by omega)
  by_contra hlast_not_B
  obtain ⟨lift, hplaced⟩ := ordered
  have hCfiber := (placementOfMap_some_iff lift.position 1 f.carrier).mp
    (hplaced ▸ h1)
  have hBfiber := (placementOfMap_some_iff lift.position 0 B).mp
    (hplaced ▸ h0)
  have hposition0 : lift.position 0 = 1 := by
    apply (mem_sourceFiber lift.position 0 1).mp
    rw [hCfiber.1]
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hpositionb : lift.position b = 0 := by
    apply (mem_sourceFiber lift.position b 0).mp
    rw [hBfiber.1]
    exact hb
  have hpositionlast_ne1 :
      lift.position ((f.hi - 1 : ℕ) : ZMod n) ≠ 1 := by
    intro heq
    have hmem : ((f.hi - 1 : ℕ) : ZMod n) ∈ f.carrier := by
      rw [← hCfiber.1]
      exact (mem_sourceFiber lift.position _ 1).mpr heq
    exact (f.not_mem_carrier_iff_remaining _).mpr hlast_rem hmem
  have hpositionlast_ne0 :
      lift.position ((f.hi - 1 : ℕ) : ZMod n) ≠ 0 := by
    intro heq
    have hmem : ((f.hi - 1 : ℕ) : ZMod n) ∈ B := by
      rw [← hBfiber.1]
      exact (mem_sourceFiber lift.position _ 0).mpr heq
    exact hlast_not_B hmem
  have hblt : b.val < f.hi - 1 := by
    have hne : b.val ≠ f.hi - 1 := by
      intro heq
      have hbeq : b = ((f.hi - 1 : ℕ) : ZMod n) := by
        calc
          b = (b.val : ZMod n) := (ZMod.natCast_zmod_val b).symm
          _ = ((f.hi - 1 : ℕ) : ZMod n) := by rw [heq]
      exact hlast_not_B (hbeq ▸ hb)
    omega
  have horder := lift.distinct_blocks_preserve_order
    b ((f.hi - 1 : ℕ) : ZMod n)
    (by simpa [ZMod.val_natCast_of_lt hlast_n] using hblt)
    (by simpa [hpositionb] using hpositionlast_ne0.symm)
    (by simpa [hposition0] using hpositionlast_ne1)
  have hnegval : (-1 : ZMod n).val = n - 1 := by
    cases n with
    | zero => omega
    | succ m => simpa using ZMod.val_neg_one m
  have hlarge : n - 1 <
      (lift.position ((f.hi - 1 : ℕ) : ZMod n) - 1).val := by
    have h := horder.2
    simp only [hpositionb, hposition0, zero_sub] at h
    rw [hnegval] at h
    exact_mod_cast h
  have hbound := (lift.position ((f.hi - 1 : ℕ) : ZMod n) - 1).val_lt
  omega

theorem linear_partner_from_left_endpoint
    (f : CheckpointSourceFrontier n) (B : Finset (ZMod n))
    (nonempty : B.Nonempty) (linear : LinearSourceConvex B)
    (inside : B ⊆ f.remaining)
    (endpoint : (f.lo : ZMod n) ∈ B) :
    ∃ ell : ℕ, 0 < ell ∧ ell ≤ f.hi - f.lo ∧ B = f.partnerR ell := by
  obtain ⟨lo, hi, hlohi, hhin, hB⟩ :=
    nonempty_linear_set_eq_sourceInterval B nonempty linear
  have hlo_n : f.lo < n := by
    obtain ⟨b, hb⟩ := nonempty
    have hval := (mem_sourceInterval_iff f.lo f.hi f.hi_valid b).mp
      (inside hb)
    have := f.hi_valid
    omega
  have hendpoint := (mem_sourceInterval_iff lo hi hhin (f.lo : ZMod n)).mp
    (hB ▸ endpoint)
  have hle : lo ≤ f.lo := by
    simpa [ZMod.val_natCast_of_lt hlo_n] using hendpoint.1
  have hlo_mem : (lo : ZMod n) ∈ B := by
    rw [hB, mem_sourceInterval_iff lo hi hhin]
    have hln : lo < n := by omega
    simpa [ZMod.val_natCast_of_lt hln] using
      (show lo ≤ lo ∧ lo < hi by omega)
  have hlo_rem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
    (inside hlo_mem)
  have hge : f.lo ≤ lo := by
    have hln : lo < n := by omega
    simpa [ZMod.val_natCast_of_lt hln] using hlo_rem.1
  have hloeq : lo = f.lo := by omega
  have htop_mem : ((hi - 1 : ℕ) : ZMod n) ∈ B := by
    rw [hB, mem_sourceInterval_iff lo hi hhin]
    have htop_n : hi - 1 < n := by omega
    simpa [ZMod.val_natCast_of_lt htop_n] using
      (show lo ≤ hi - 1 ∧ hi - 1 < hi by omega)
  have htop_rem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
    (inside htop_mem)
  have hhi_le : hi ≤ f.hi := by
    have htop_n : hi - 1 < n := by omega
    have hbound : hi - 1 < f.hi := by
      simpa [ZMod.val_natCast_of_lt htop_n] using htop_rem.2
    omega
  refine ⟨hi - f.lo, by omega, by omega, ?_⟩
  rw [hB, hloeq]
  have heq : f.lo + (hi - f.lo) = hi := by omega
  simpa [CheckpointSourceFrontier.partnerR, heq]

theorem linear_partner_from_right_endpoint
    (f : CheckpointSourceFrontier n) (B : Finset (ZMod n))
    (nonempty : B.Nonempty) (linear : LinearSourceConvex B)
    (inside : B ⊆ f.remaining)
    (endpoint : ((f.hi - 1 : ℕ) : ZMod n) ∈ B) :
    ∃ ell : ℕ, 0 < ell ∧ ell ≤ f.hi - f.lo ∧ B = f.partnerL ell := by
  obtain ⟨lo, hi, hlohi, hhin, hB⟩ :=
    nonempty_linear_set_eq_sourceInterval B nonempty linear
  have hlast_n : f.hi - 1 < n := by
    have := f.hi_valid
    omega
  have hendpoint := (mem_sourceInterval_iff lo hi hhin _).mp
    (hB ▸ endpoint)
  have hlast_lt_hi : f.hi - 1 < hi := by
    simpa [ZMod.val_natCast_of_lt hlast_n] using hendpoint.2
  have hlo_mem : (lo : ZMod n) ∈ B := by
    rw [hB, mem_sourceInterval_iff lo hi hhin]
    have hln : lo < n := by omega
    simpa [ZMod.val_natCast_of_lt hln] using
      (show lo ≤ lo ∧ lo < hi by omega)
  have hlo_rem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
    (inside hlo_mem)
  have hlo_ge : f.lo ≤ lo := by
    have hln : lo < n := by omega
    simpa [ZMod.val_natCast_of_lt hln] using hlo_rem.1
  have htop_mem : ((hi - 1 : ℕ) : ZMod n) ∈ B := by
    rw [hB, mem_sourceInterval_iff lo hi hhin]
    have htop_n : hi - 1 < n := by omega
    simpa [ZMod.val_natCast_of_lt htop_n] using
      (show lo ≤ hi - 1 ∧ hi - 1 < hi by omega)
  have htop_rem := (mem_sourceInterval_iff f.lo f.hi f.hi_valid _).mp
    (inside htop_mem)
  have hhi_le : hi ≤ f.hi := by
    have htop_n : hi - 1 < n := by omega
    have hbound : hi - 1 < f.hi := by
      simpa [ZMod.val_natCast_of_lt htop_n] using htop_rem.2
    omega
  have hhi_eq : hi = f.hi := by omega
  refine ⟨f.hi - lo, by omega, by omega, ?_⟩
  rw [hB, hhi_eq]
  have heq : f.hi - (f.hi - lo) = lo := by omega
  simpa [CheckpointSourceFrontier.partnerL, heq]

theorem frontier_partner_checkpoint_size
    (f : CheckpointSourceFrontier n) (C B : Finset (ZMod n))
    (side : Side) (ell : ℕ)
    (hC : f.carrier = C) (hbound : ell ≤ f.hi - f.lo)
    (hB : B = if side then f.partnerR ell else f.partnerL ell) :
    (C ∪ B).card - 2 = f.absorbed + ell := by
  cases side with
  | true =>
      have hnext : C ∪ B = (f.nextR ell hbound).carrier := by
        rw [← hC, hB]
        exact (f.carrier_nextR ell hbound).symm
      rw [hnext, (f.nextR ell hbound).carrier_card,
        f.absorbed_nextR]
      omega
  | false =>
      have hnext : C ∪ B = (f.nextL ell hbound).carrier := by
        rw [← hC, hB]
        exact (f.carrier_nextL ell hbound).symm
      rw [hnext, (f.nextL ell hbound).carrier_card,
        f.absorbed_nextL]
      omega

/-- Actual selected-fusion frontier: in any registered source-ordered state,
regardless of earlier outside fusions, the next selected parent is a nonempty
prefix or suffix of the remaining source interval. Its port and the appended
record are those of this same real defect step. -/
theorem actual_selected_fusion_frontier
    (s : Execution n (ZMod n)) (C u v : Finset (ZMod n))
    (q : ZMod n) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (hC : s.placed q = some C) (inside : selectedPair n ⊆ C)
    (registered : s.origin.isSome = true)
    (h0 : s.placed 0 = some u) (h1 : s.placed 1 = some v)
    (hselected : selectedPair n ⊆ u ∨ selectedPair n ⊆ v) :
    ∃ (f : CheckpointSourceFrontier n) (side : Side)
      (B : Finset (ZMod n)) (ell : ℕ),
      f.carrier = C ∧ 0 < ell ∧ ell ≤ f.hi - f.lo ∧
      CheckpointPorts side s.placed C B ∧
      B = (if side then f.partnerR ell else f.partnerL ell) ∧
      (stepDefect (selectedPair n) s).origin = s.origin ∧
      (stepDefect (selectedPair n) s).chain =
        s.chain ++ [checkpointRecord side C B] ∧
      (stepDefect (selectedPair n) s).placed 0 = some (C ∪ B) ∧
      (C ∪ B).card - 2 = f.absorbed + ell ∧
      f.absorbed < (C ∪ B).card - 2 := by
  obtain ⟨f, hfC⟩ := actual_selected_has_frontier
    s C q hn ordered hC inside
  have hselected_ne : (selectedPair n).Nonempty :=
    ⟨0, by simp [selectedPair]⟩
  obtain ⟨side, B, hports, horigin, hchain, hplaced⟩ :=
    actual_selected_step_uses_carrier s (selectedPair n) C u v q hn
      ordered hselected_ne hC inside registered h0 h1 hselected
  cases side with
  | true =>
      have hports' : s.placed 0 = some C ∧ s.placed 1 = some B :=
        hports
      have hzero : (0 : ZMod n) ∈ C :=
        inside (show (0 : ZMod n) ∈ selectedPair n by simp [selectedPair])
      obtain ⟨hBne, hlinear, houtside⟩ :=
        actual_outside_packet_linear s C B 0 1 ordered
          (by intro heq; have := ZMod.one_eq_zero_iff.mp heq.symm; omega)
          hports'.1 hports'.2 hzero
      have hremain : B ⊆ f.remaining := by
        intro a ha
        have hnot : a ∉ C := (Finset.mem_sdiff.mp (houtside ha)).2
        exact (f.not_mem_carrier_iff_remaining a).mp (hfC ▸ hnot)
      have hlo := actual_right_partner_contains_lo s f B hn ordered
        (hfC ▸ hports'.1) hports'.2
      obtain ⟨ell, hellpos, hellbound, hBeq⟩ :=
        linear_partner_from_left_endpoint f B hBne hlinear hremain hlo
      have hsize := frontier_partner_checkpoint_size f C B true ell
        hfC hellbound (by simpa using hBeq)
      exact ⟨f, true, B, ell, hfC, hellpos, hellbound,
        hports, by simpa using hBeq, horigin, hchain, hplaced,
        hsize, by omega⟩
  | false =>
      have hports' : s.placed 0 = some B ∧ s.placed 1 = some C :=
        hports
      have hzero : (0 : ZMod n) ∈ C :=
        inside (show (0 : ZMod n) ∈ selectedPair n by simp [selectedPair])
      obtain ⟨hBne, hlinear, houtside⟩ :=
        actual_outside_packet_linear s C B 1 0 ordered
          (by intro heq; have := ZMod.one_eq_zero_iff.mp heq; omega)
          hports'.2 hports'.1 hzero
      have hremain : B ⊆ f.remaining := by
        intro a ha
        have hnot : a ∉ C := (Finset.mem_sdiff.mp (houtside ha)).2
        exact (f.not_mem_carrier_iff_remaining a).mp (hfC ▸ hnot)
      have hhi := actual_left_partner_contains_hi_pred s f B hn ordered
        hports'.1 (hfC ▸ hports'.2)
      obtain ⟨ell, hellpos, hellbound, hBeq⟩ :=
        linear_partner_from_right_endpoint f B hBne hlinear hremain hhi
      have hsize := frontier_partner_checkpoint_size f C B false ell
        hfC hellbound (by simpa using hBeq)
      exact ⟨f, false, B, ell, hfC, hellpos, hellbound,
        hports, by simpa using hBeq, horigin, hchain, hplaced,
        hsize, by omega⟩

/-- The frontier theorem applied to an actual singleton-seed history. Its
carrier is read from that history's latest selected record, not chosen
independently from the source partition. -/
theorem reachable_selected_fusion_frontier
    (word : List Letter) (hn : 2 ≤ n)
    (registered : (run (selectedPair n) (singletonExecution n) word).origin.isSome = true)
    (u v : Finset (ZMod n))
    (h0 : (run (selectedPair n) (singletonExecution n) word).placed 0 = some u)
    (h1 : (run (selectedPair n) (singletonExecution n) word).placed 1 = some v)
    (hselected : selectedPair n ⊆ u ∨ selectedPair n ⊆ v) :
    ∃ (C : Finset (ZMod n)) (f : CheckpointSourceFrontier n)
      (side : Side) (B : Finset (ZMod n)) (ell : ℕ),
      recordedCarrierResult
        (run (selectedPair n) (singletonExecution n) word) = some C ∧
      f.carrier = C ∧ 0 < ell ∧ ell ≤ f.hi - f.lo ∧
      CheckpointPorts side
        (run (selectedPair n) (singletonExecution n) word).placed C B ∧
      B = (if side then f.partnerR ell else f.partnerL ell) ∧
      (stepDefect (selectedPair n)
        (run (selectedPair n) (singletonExecution n) word)).chain =
        (run (selectedPair n) (singletonExecution n) word).chain ++
          [checkpointRecord side C B] ∧
      (C ∪ B).card - 2 = f.absorbed + ell := by
  let s := run (selectedPair n) (singletonExecution n) word
  have hselected_ne : (selectedPair n).Nonempty :=
    ⟨0, by simp [selectedPair]⟩
  obtain ⟨q, C, hC, inside, hrecord⟩ :=
    actual_registered_carrier_from_seed (selectedPair n) word hn
      hselected_ne registered
  have hordered : SourceOrdered s.placed :=
    run_ordered (selectedPair n) (singletonExecution n) word hn
      singletonExecution_ordered
  obtain ⟨f, side, B, ell, hfC, hellpos, hellbound,
      hports, hBeq, _, hchain, _, hsize, _⟩ :=
    actual_selected_fusion_frontier s C u v q hn hordered
      hC inside registered h0 h1 hselected
  exact ⟨C, f, side, B, ell, hrecord, hfC, hellpos,
    hellbound, hports, hBeq, hchain, hsize⟩

end RegisteredAbsorptionChains
