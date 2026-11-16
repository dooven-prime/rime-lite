import RSR2.RetentionAssembly
import RSR2.PartialLoading

/-!
# Constructive sufficiency of lower retention

Load the complementary blocks upstairs while reserving lower singletons.
Restore their source phase, then assemble the admissible retained intervals.
All words run in the original guarded five-generator semantics.
-/

namespace RSR2.Parametric

theorem blocksDisjoint_of_flatten_nodup (family : List (List α))
    (h : family.flatten.Nodup) : BlocksDisjoint family := by
  induction family with
  | nil => intro B hB; simp at hB
  | cons D rest ih =>
      have hd := List.nodup_append.mp h
      intro B hB C hC a ha hb
      rcases List.mem_cons.mp hB with rfl | hB
      · rcases List.mem_cons.mp hC with rfl | hC
        · rfl
        · exact False.elim (hd.2.2 a ha a (List.mem_flatten.mpr ⟨C,hC,hb⟩) rfl)
      · rcases List.mem_cons.mp hC with hCD | hCrest
        · subst C
          exact False.elim (hd.2.2 a hb a (List.mem_flatten.mpr ⟨B,hB,ha⟩) rfl)
        · exact ih hd.2.1 B hB C hCrest a ha hb

theorem flatten_filter_nodup (family : List (List α))
    (h : family.flatten.Nodup) (test : List α → Bool) :
    (family.filter test).flatten.Nodup := by
  have hh := List.pairwise_flatten.mp h
  apply List.pairwise_flatten.mpr
  exact ⟨fun B hB => hh.1 B (List.mem_filter.mp hB).1, hh.2.filter test⟩

theorem blockCoordinate_none_iff (blocks : List (List (Fin n))) (a : Fin n) :
    blockCoordinate blocks a = none ↔ a ∉ blocks.flatten := by
  induction blocks with
  | nil => simp [blockCoordinate]
  | cons B rest ih =>
      by_cases ha : a ∈ B
      · simp [blockCoordinate,ha]
      · simp [blockCoordinate,ha,ih]

/-- A subfamily's coordinate model separates its nonempty disjoint blocks.
Unlike the canonical full-partition theorem, coverage of every atom is not
required. -/
theorem blockCoordinate_same_iff (blocks : List (List (Fin n)))
    (hne : ∀ B ∈ blocks, B ≠ []) (hnd : blocks.flatten.Nodup)
    (a b : Fin n) (ha : a ∈ blocks.flatten) :
    blockCoordinate blocks a = blockCoordinate blocks b ↔
      ∃ B ∈ blocks, a ∈ B ∧ b ∈ B := by
  obtain ⟨B,hB,haB⟩ := List.mem_flatten.mp ha
  obtain ⟨pre,post,hblocks⟩ := List.mem_iff_append.mp hB
  have hne' : ∀ C ∈ pre++B::post, C ≠ [] := hblocks ▸ hne
  have hnd' : (pre++B::post).flatten.Nodup := hblocks ▸ hnd
  have haq := (blockCoordinate_eq_prefix_iff pre B post hne' hnd' a).mpr haB
  constructor
  · intro hab
    refine ⟨B,hB,haB,?_⟩
    apply (blockCoordinate_eq_prefix_iff pre B post hne' hnd' b).mp
    rw [← hblocks] at haq ⊢
    exact hab ▸ haq
  · rintro ⟨C,hC,haC,hbC⟩
    have he := blocksDisjoint_of_flatten_nodup blocks hnd C hC B hB a haC haB
    subst C
    have hbq := (blockCoordinate_eq_prefix_iff pre B post hne' hnd' b).mpr hbC
    rw [hblocks]
    exact haq.trans hbq.symm

/-- Partial loading followed by a lower-only phase correction.  The atoms
reserved below return to their literal source sites; upper coordinates are
the block-packing model, including `none` on reserved atoms. -/
theorem load_upper_subfamily (n : Nat) (hn : 1 < n)
    (p : RSR2.OrderedPartition n) (retained : List (List (Fin n)))
    (hsub : ∀ B ∈ retained, B ∈ p.blocks) :
    ∃ W P,
      run n hn (seed n) W = some P ∧
      (∀ a, retainedAtoms retained a → P a = (false,a)) ∧
      (∀ a, (P a).1 = false → retainedAtoms retained a) ∧
      (∀ a, upperCoordinate P a = blockCoordinate
        (p.blocks.filter (fun B => !decide (B ∈ retained))) a) := by
  classical
  let upper := p.blocks.filter (fun B => !decide (B ∈ retained))
  let reserved := (List.finRange n).filter (fun a => decide (retainedAtoms retained a))
  let xs := markedReverseBlocks upper
  have hnd := p.flatten_perm.nodup_iff.mpr (List.nodup_finRange n)
  have hdisj := blocksDisjoint_of_flatten_nodup p.blocks hnd
  have hupper (a : Fin n) : a ∈ upper.flatten ↔ ¬retainedAtoms retained a := by
    constructor
    · rintro ha ⟨B,hB,haB⟩
      obtain ⟨C,hC,haC⟩ := List.mem_flatten.mp ha
      obtain ⟨hCp,hCn⟩ := List.mem_filter.mp hC
      have he := hdisj C hCp B (hsub B hB) a haC haB
      have : C ∉ retained := by simpa using hCn
      exact this (he ▸ hB)
    · intro ha
      obtain ⟨B,hB,haB⟩ := List.mem_flatten.mp
        (p.flatten_perm.mem_iff.mpr (List.mem_finRange a))
      exact List.mem_flatten.mpr ⟨B,List.mem_filter.mpr
        ⟨hB,by simpa using (show B ∉ retained from fun h => ha ⟨B,h,haB⟩)⟩,haB⟩
  have hxs : xs.map Prod.fst = upper.flatten.reverse := by
    exact (markedReverseBlocks_atoms upper).trans (flatten_reverse_blocks upper)
  have hres (a : Fin n) : a ∈ reserved ↔ retainedAtoms retained a := by
    simp [reserved]
  have hcover (a : Fin n) : a ∈ xs.map Prod.fst ++ reserved := by
    by_cases ha : retainedAtoms retained a
    · exact List.mem_append.mpr (Or.inr ((hres a).mpr ha))
    · exact List.mem_append.mpr (Or.inl (by simpa [hxs] using (hupper a).mpr ha))
  have hnodup : (xs.map Prod.fst ++ reserved).Nodup := by
    apply List.nodup_append.mpr
    refine ⟨?_,(List.nodup_finRange n).filter _,?_⟩
    · rw [hxs]
      apply List.pairwise_reverse.mpr
      exact (flatten_filter_nodup p.blocks hnd _).imp (fun h => Ne.symm h)
    · intro a ha b hb he
      subst b
      exact (hupper a).mp (by simpa [hxs] using ha) ((hres a).mp hb)
  have hlen : xs.length ≤ n := by
    have hh := List.Nodup.length_le_of_subset hnodup
      (show ∀ a ∈ xs.map Prod.fst++reserved, a ∈ List.finRange n from
        fun a _ => List.mem_finRange a)
    simp only [List.length_append,List.length_map,List.length_finRange] at hh
    omega
  obtain ⟨R,phase,hguard,hfamily,hsupport,hcoords⟩ :=
    partialLoading_coordinates n hn xs reserved 0 0 true (seed n)
      (seed_upperSupportBelow_zero n) (by omega) (by simp)
      (seed_lowerFamily n (by omega) _) hnodup (fun a _ => hcover a)
  let turns := n-phase%n
  let P := rotateMany n (by omega) R false turns
  have hphase (a : Fin n) : nextMany n (by omega) (phaseSite n a phase) turns = a := by
    apply Fin.ext
    rw [nextMany_val,phaseSite_val n (by omega)]
    have ht : (a.val+phase)%n = (a.val+phase%n)%n := (Nat.add_mod_mod _ _ _).symm
    rw [ht, Nat.mod_add_mod]
    have hph := Nat.mod_lt phase (show 0<n by omega)
    have he : a.val+phase%n+turns = a.val+n := by dsimp [turns]; omega
    rw [he,Nat.add_mod_right,Nat.mod_eq_of_lt a.isLt]
  refine ⟨emitPlanAux true (annotateMarked n 0 xs) ++ pWord false turns,P,?_,?_,?_,?_⟩
  · rw [run_append,guardedPlan_run_emitPlanAux n hn _ _ _ _ hguard]
    exact run_powers n hn R false turns
  · intro a ha
    simp only [P,rotateMany_apply,hfamily a ((hres a).mpr ha),
      ↓reduceIte,hphase]
  · intro a ha
    exact (hres a).mp ((lowerSupportSubset_after_rotateMany n hn R reserved
      false turns hsupport) a ha)
  · intro a
    have hc := hcoords a
    dsimp only [xs] at hc
    simp only [seed,upperCoordinate,Bool.false_eq_true,↓reduceIte,
      packAtom_first_empty,packAtom_markedReverseBlocks] at hc
    rcases he : R a with ⟨layer,q⟩
    cases layer <;> simpa [P,upperCoordinate,rotateMany_apply,he,xs,upper] using hc

theorem samePacket_iff_upperCoordinate_eq (P : Placement n) (a b : Fin n)
    (ha : (P a).1 = true) (hb : (P b).1 = true) :
    samePacket P a b ↔ upperCoordinate P a = upperCoordinate P b := by
  unfold samePacket upperCoordinate
  rw [ha,hb]
  simp only [if_true,Option.some.injEq]
  constructor
  · intro he
    exact congrArg (fun loc : Bool × Fin n => loc.2.val) he
  · intro h
    exact Prod.ext (ha.trans hb.symm) (Fin.ext h)

/-- Every admissible subfamily of an ordered partition can be retained
downstairs by a legal word. Complementary blocks are loaded upstairs first;
lower assembly fixes their coordinates and never uses another transfer. -/
theorem retentionAdmissible_realization (n : Nat) (hn : 1 < n)
    (p : RSR2.OrderedPartition n) (retained : List (List (Fin n)))
    (hsub : ∀ B ∈ retained, B ∈ p.blocks)
    (hadm : RetentionAdmissible n (by omega) retained) :
    ∃ W P, run n hn (seed n) W = some P ∧
      OrderedLayerAllocation P p retained := by
  classical
  have hnd := p.flatten_perm.nodup_iff.mpr (List.nodup_finRange n)
  have hdisj := blocksDisjoint_of_flatten_nodup p.blocks hnd
  have hrd : BlocksDisjoint retained := fun B hB C hC a ha hb =>
    hdisj B (hsub B hB) C (hsub C hC) a ha hb
  obtain ⟨w0,P0,hrun0,hinit,hbelow,hcoords⟩ :=
    load_upper_subfamily n hn p retained hsub
  obtain ⟨w,f,hrun,hwithin,hconst⟩ := lower_assemble_retained n hn retained
    (fun B hB => p.nonempty B (hsub B hB)) hrd hadm retained (fun _ h => h)
  let P := lowerRemap f P0
  have hlow (a : Fin n) (ha : retainedAtoms retained a) : P a = (false,f a) := by
    simp [P,lowerRemap,hinit a ha]
  have hup (a : Fin n) (ha : ¬retainedAtoms retained a) : P a = P0 a := by
    have hh : (P0 a).1 ≠ false := fun h => ha (hbelow a h)
    simp only [P,lowerRemap,if_neg hh]
  have hlayer (a : Fin n) : lowerAtoms P a ↔ retainedAtoms retained a := by
    constructor
    · intro ha
      by_cases h : retainedAtoms retained a
      · exact h
      · exact False.elim (h (hbelow a (by simpa only [lowerAtoms,hup a h] using ha)))
    · intro ha
      simp only [lowerAtoms,hlow a ha]
  have hupper (a : Fin n) : a ∈
      (p.blocks.filter (fun B => !decide (B ∈ retained))).flatten ↔
      ¬retainedAtoms retained a := by
    constructor
    · rintro ha ⟨B,hB,haB⟩
      obtain ⟨C,hC,haC⟩ := List.mem_flatten.mp ha
      obtain ⟨hCp,hCn⟩ := List.mem_filter.mp hC
      have he := hdisj C hCp B (hsub B hB) a haC haB
      have : C ∉ retained := by simpa using hCn
      exact this (he ▸ hB)
    · intro ha
      obtain ⟨B,hB,haB⟩ := List.mem_flatten.mp
        (p.flatten_perm.mem_iff.mpr (List.mem_finRange a))
      exact List.mem_flatten.mpr ⟨B,List.mem_filter.mpr
        ⟨hB,by simpa using (show B ∉ retained from fun h => ha ⟨B,h,haB⟩)⟩,haB⟩
  have hupeq (a b : Fin n) (ha : ¬retainedAtoms retained a)
      (hb : ¬retainedAtoms retained b) :
      samePacket P a b ↔ ∃ B ∈ p.blocks.filter (fun B => !decide (B ∈ retained)),
        a ∈ B ∧ b ∈ B := by
    have hPa : (P0 a).1 = true := by
      cases h : (P0 a).1
      · exact False.elim (ha (hbelow a h))
      · rfl
    have hPb : (P0 b).1 = true := by
      cases h : (P0 b).1
      · exact False.elim (hb (hbelow b h))
      · rfl
    change P a = P b ↔ _
    rw [hup a ha,hup b hb]
    change samePacket P0 a b ↔ _
    rw [samePacket_iff_upperCoordinate_eq P0 a b hPa hPb]
    rw [hcoords a,hcoords b]
    exact blockCoordinate_same_iff _
      (fun B hB => p.nonempty B (List.mem_filter.mp hB).1)
      (flatten_filter_nodup p.blocks hnd _) a b ((hupper a).mpr ha)
  have hpartition : ∀ a b, samePacket P a b ↔
      ∃ B ∈ p.blocks, a ∈ B ∧ b ∈ B := by
    intro a b
    constructor
    · intro hab
      by_cases ha : retainedAtoms retained a
      · have hb : retainedAtoms retained b := (hlayer b).mp (by
          unfold lowerAtoms
          rw [← hab,hlow a ha])
        obtain ⟨B,hB,haB⟩ := ha
        obtain ⟨C,hC,hbC⟩ := hb
        have he : f a = f b := by
          have hh : P a = P b := hab
          rw [hlow a ⟨B,hB,haB⟩,hlow b ⟨C,hC,hbC⟩] at hh
          exact congrArg Prod.snd hh
        have hBC := hrd B hB C hC (f a) (hwithin B hB a haB)
          (he ▸ hwithin C hC b hbC)
        exact ⟨B,hsub B hB,haB,hBC ▸ hbC⟩
      · have hb : ¬retainedAtoms retained b := fun hb => ha ((hlayer a).mp (by
          unfold lowerAtoms
          rw [hab,hlow b hb]))
        obtain ⟨B,hB,haB,hbB⟩ := (hupeq a b ha hb).mp hab
        exact ⟨B,(List.mem_filter.mp hB).1,haB,hbB⟩
    · rintro ⟨B,hB,haB,hbB⟩
      by_cases hret : B ∈ retained
      · change P a = P b
        rw [hlow a ⟨B,hret,haB⟩,hlow b ⟨B,hret,hbB⟩,
          hconst B hret a haB b hbB]
      · have hnot (c : Fin n) (hc : c ∈ B) : ¬retainedAtoms retained c := by
          rintro ⟨C,hC,hcC⟩
          exact hret ((hdisj C (hsub C hC) B hB c hcC hc) ▸ hC)
        exact (hupeq a b (hnot a haB) (hnot b hbB)).mpr
          ⟨B,List.mem_filter.mpr ⟨hB,by simpa using hret⟩,haB,hbB⟩
  refine ⟨w0++w,P,?_,⟨hpartition,hsub,?_⟩⟩
  · rw [run_append,hrun0]
    exact hrun P0
  · intro B hB
    constructor
    · rintro ⟨a,ha,hl⟩
      obtain ⟨C,hC,haC⟩ := (hlayer a).mp hl
      exact (hdisj C (hsub C hC) B hB a haC ha) ▸ hC
    · intro hBret
      cases B with
      | nil => exact False.elim (p.nonempty [] hB rfl)
      | cons a tail =>
        exact ⟨a,by simp,(hlayer a).mpr ⟨a::tail,hBret,by simp⟩⟩

/-- Exact ordered retention criterion, over the actual guarded executor. -/
theorem orderedLayerAllocation_reachable_iff (n : Nat) (hn : 1 < n)
    (p : RSR2.OrderedPartition n) (retained : List (List (Fin n)))
    (hsub : ∀ B ∈ retained, B ∈ p.blocks) :
    (∃ W P, run n hn (seed n) W = some P ∧ OrderedLayerAllocation P p retained) ↔
      RetentionAdmissible n (by omega) retained := by
  constructor
  · rintro ⟨W,P,hrun,halloc⟩
    exact singleton_run_retentionAdmissible n hn W P hrun p retained halloc
  · exact retentionAdmissible_realization n hn p retained hsub

/-- An order-free admissible lower atom set can be realized by the guarded
executor. We choose an ordered presentation only as a construction aid; the
endpoint statement is phrased entirely in the input equivalence relation. -/
theorem unorderedRetentionAdmissible_realization (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop)
    (hadm : UnorderedRetentionAdmissible n (by omega) π U) :
    ∃ W P, run n hn (seed n) W = some P ∧ EndpointLayerAllocation P π U := by
  classical
  obtain ⟨p,hp⟩ := RSR2.unorderedPartition_has_orderedPresentation π
  let retained := p.blocks.filter (fun B => decide (∃ a ∈ B, U a))
  have hnd := p.flatten_perm.nodup_iff.mpr (List.nodup_finRange n)
  have hdisj := blocksDisjoint_of_flatten_nodup p.blocks hnd
  have hsub : ∀ B ∈ retained, B ∈ p.blocks := by
    intro B hB
    exact (List.mem_filter.mp hB).1
  have hretained (a : Fin n) : retainedAtoms retained a ↔ U a := by
    constructor
    · rintro ⟨B,hB,haB⟩
      obtain ⟨c,hcB,hcU⟩ := of_decide_eq_true (List.mem_filter.mp hB).2
      have hrel : π.r a c := (hp a c).mp ⟨B,(List.mem_filter.mp hB).1,haB,hcB⟩
      exact (hadm.1 a c hrel).mpr hcU
    · intro ha
      obtain ⟨B,hB,haB⟩ := List.mem_flatten.mp
        (p.flatten_perm.mem_iff.mpr (List.mem_finRange a))
      have hclass : ∃ c ∈ B, U c := ⟨a,haB,ha⟩
      exact ⟨B,List.mem_filter.mpr ⟨hB,of_decide_eq_true (by
        simpa only [decide_eq_true_eq] using hclass)⟩,haB⟩
  have hadmBlocks : RetentionAdmissible n (by omega) retained := by
    intro B hB
    obtain ⟨a,haB,haU⟩ := of_decide_eq_true (List.mem_filter.mp hB).2
    have hclass (b : Fin n) : b ∈ B ↔ π.r b a := by
      constructor
      · intro hb
        exact (hp b a).mp ⟨B,(List.mem_filter.mp hB).1,hb,haB⟩
      · intro hba
        obtain ⟨C,hC,hbC,haC⟩ := (hp b a).mpr hba
        have hBC := hdisj C hC B (List.mem_filter.mp hB).1 a haC haB
        exact hBC ▸ hbC
    exact (hadm.2 a haU).congr (fun x => (hretained x).symm)
      (fun b => (hclass b).symm)
  obtain ⟨W,P,hrun,halloc⟩ := retentionAdmissible_realization n hn p retained
    hsub hadmBlocks
  have hendpoint := halloc.toEndpointLayerAllocation hp
  exact ⟨W,P,hrun,⟨hendpoint.1,fun a => (hendpoint.2 a).trans (hretained a)⟩⟩

/-- Exact unordered endpoint criterion: a chosen union of target classes is
reachable on the lower layer iff each retained class is cyclically convex in
the source cycle restricted to that union. -/
theorem endpointLayerAllocation_reachable_iff (n : Nat) (hn : 1 < n)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop) :
    (∃ W P, run n hn (seed n) W = some P ∧ EndpointLayerAllocation P π U) ↔
      UnorderedRetentionAdmissible n (by omega) π U := by
  constructor
  · rintro ⟨W,P,hrun,halloc⟩
    exact singleton_run_unorderedRetentionAdmissible n hn W P hrun π U halloc
  · exact unorderedRetentionAdmissible_realization n hn π U

end RSR2.Parametric
