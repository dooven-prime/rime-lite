import RSR2History.ForestCrossDefect

/-!
A declared ordered forest with one nontrivial left-comb root and otherwise
singleton roots.  This is a combinatorial normal-form certificate only:
it neither permutes roots nor supplies a physical terminal-routing budget.
-/
namespace RSR2History
open RSR2.Parametric

/-- The displayed forest order is retained literally.  Leaves are transfer
occurrences, as in `UpperFusionTree`, rather than source atom labels. -/
structure CombRootForestNormalForm (terminal : List (UpperFusionTree n))
    (k : Nat) where
  before : List (UpperFusionTree n)
  comb : UpperFusionTree n
  after : List (UpperFusionTree n)
  forest_eq : terminal = before ++ comb :: after
  two_le : 2 ≤ k
  lt_sites : k < n
  comb_leftComb : comb.IsLeftComb
  comb_leaf_count : comb.leaves.length = k
  before_singleton : ∀ T ∈ before, T.leaves.length = 1
  after_singleton : ∀ T ∈ after, T.leaves.length = 1

private theorem singletonRoots_mergeMass_zero
    (forest : List (UpperFusionTree n))
    (h : ∀ T ∈ forest, T.leaves.length = 1) :
    forestMergeMass forest = 0 := by
  induction forest with
  | nil => rfl
  | cons T rest ih =>
      have hT := h T (by simp)
      have hrest : ∀ U ∈ rest, U.leaves.length = 1 := by
        intro U hU
        exact h U (by simp [hU])
      have hT' : T.leaves.length - 1 = 0 := by omega
      have ih' : (rest.map (fun U => U.leaves.length - 1)).sum = 0 := by
        simpa [forestMergeMass] using ih hrest
      simp only [forestMergeMass, List.map_cons, List.sum_cons]
      omega

private theorem singletonRoots_gapDebt_zero
    (forest : List (UpperFusionTree n))
    (h : ∀ T ∈ forest, T.leaves.length = 1) :
    forestGapDebt forest = 0 := by
  induction forest with
  | nil => rfl
  | cons T rest ih =>
      have hT := T.gapDebt_add_defect
      have hlen := h T (by simp)
      have hzero : T.leftGapDebt = 0 := by simp [hlen] at hT; omega
      have hrest : ∀ U ∈ rest, U.leaves.length = 1 := by
        intro U hU
        exact h U (by simp [hU])
      have ih' : (rest.map UpperFusionTree.leftGapDebt).sum = 0 := by
        simpa [forestGapDebt] using ih hrest
      simp only [forestGapDebt, List.map_cons, List.sum_cons]
      omega

private theorem singletonRoots_branchDefect_zero
    (forest : List (UpperFusionTree n))
    (h : ∀ T ∈ forest, T.leaves.length = 1) :
    (forest.map UpperFusionTree.leftBranchDefect).sum = 0 := by
  induction forest with
  | nil => rfl
  | cons T rest ih =>
      have hT := T.gapDebt_add_defect
      have hlen := h T (by simp)
      have hzero : T.leftBranchDefect = 0 := by simp [hlen] at hT; omega
      have hrest : ∀ U ∈ rest, U.leaves.length = 1 := by
        intro U hU
        exact h U (by simp [hU])
      simp [hzero, ih hrest]

namespace CombRootForestNormalForm

variable {terminal : List (UpperFusionTree n)} {k : Nat}

/-- The unique nontrivial root occupies one contiguous interval in the
expanded ordered leaf list.  No cyclic reordering is performed here. -/
theorem leaf_interval (h : CombRootForestNormalForm terminal k) :
    forestLeaves terminal =
      forestLeaves h.before ++ h.comb.leaves ++ forestLeaves h.after := by
  calc
    forestLeaves terminal = forestLeaves (h.before ++ h.comb :: h.after) :=
      congrArg forestLeaves h.forest_eq
    _ = forestLeaves h.before ++ h.comb.leaves ++ forestLeaves h.after := by
      simp [forestLeaves, List.flatMap_append, List.append_assoc]

theorem comb_mem (h : CombRootForestNormalForm terminal k) :
    h.comb ∈ terminal := by
  simp [h.forest_eq]

private theorem comb_leaves_head_tail (h : CombRootForestNormalForm terminal k) :
    h.comb.leaves = h.comb.firstLeaf :: h.comb.leaves.tail := by
  obtain ⟨tail, he⟩ := h.comb.leaves_eq_first_cons
  conv_lhs => rw [he]
  simp [he]

/-- In the frame using the displayed forest's leaf order, leaf offset `i`
is physically reserved at the start of the comb interval plus `i`. -/
theorem reservation_site_index (h : CombRootForestNormalForm terminal k)
    {transfers : Nat} {forest : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site)
    (i : Nat) (hi : i < h.comb.leaves.length) :
    (site h.comb.leaves[i]).val = (forestLeaves h.before).length + i := by
  let pre := forestLeaves h.before
  have he : forestLeaves terminal = pre ++ (h.comb.leaves ++ forestLeaves h.after) :=
    h.leaf_interval.trans (List.append_assoc _ _ _)
  have hbound : pre.length + i < (forestLeaves terminal).length := by
    rw [he]
    simp only [List.length_append]
    omega
  have hlookup :
      (forestLeaves terminal)[pre.length + i] = h.comb.leaves[i] := by
    revert hbound
    rw [he]
    intro hbound
    rw [List.getElem_append_right (Nat.le_add_right _ _)]
    simp only [Nat.add_sub_cancel_left, List.getElem_append_left hi]
  rw [← hlookup, frame.site_index _ (List.getElem_mem hbound),
    frame.omega_nodup.idxOf_getElem]

theorem reservation_anchor_index (h : CombRootForestNormalForm terminal k)
    {transfers : Nat} {forest : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site) :
    (site h.comb.firstLeaf).val = (forestLeaves h.before).length := by
  have hzero : h.comb.leaves[0]'(h.comb.leaves_length_pos) = h.comb.firstLeaf := by
    obtain ⟨tail, he⟩ := h.comb.leaves_eq_first_cons
    simp [he]
  simpa only [hzero, Nat.add_zero] using
    h.reservation_site_index frame 0 h.comb.leaves_length_pos

/-- The reservations released by the comb's merges, in leaf order. -/
def releasedSites (h : CombRootForestNormalForm terminal k)
    (site : Nat → Fin n) : List (Fin n) :=
  h.comb.leaves.tail.map site

theorem releasedSites_length (h : CombRootForestNormalForm terminal k)
    (site : Nat → Fin n) :
    (h.releasedSites site).length = k - 1 := by
  simp [releasedSites, h.comb_leaf_count]

/-- The non-anchor reservations are exactly the consecutive physical
coordinates after the anchor in the comb's leaf interval. -/
theorem releasedSites_values (h : CombRootForestNormalForm terminal k)
    {transfers : Nat} {forest : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site) :
    (h.releasedSites site).map Fin.val =
      List.range' ((site h.comb.firstLeaf).val + 1) (k - 1) := by
  apply List.ext_getElem
  · simp [h.releasedSites_length]
  · intro i hi hj
    have hitail : i < h.comb.leaves.tail.length := by
      simpa [releasedSites] using hi
    have hik : i + 1 < h.comb.leaves.length := by
      simp only [List.length_tail] at hitail
      omega
    have hv : (site h.comb.leaves[i + 1]).val = (forestLeaves h.before).length + (i + 1) :=
      h.reservation_site_index frame (i + 1) hik
    simp only [releasedSites, List.getElem_map, List.getElem_tail,
      List.getElem_range'_1, h.reservation_anchor_index frame]
    omega

theorem releasedSites_card (h : CombRootForestNormalForm terminal k)
    {transfers : Nat} {forest : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site) :
    (h.releasedSites site).toFinset.card = k - 1 := by
  apply (List.toFinset_card_of_nodup ?_).trans (h.releasedSites_length site)
  change (h.comb.leaves.tail.map site).Nodup
  have hnd := (List.nodup_flatMap.mp frame.omega_nodup).1 h.comb h.comb_mem
  have hmem {a : Nat} (ha : a ∈ h.comb.leaves.tail) : a ∈ forestLeaves terminal :=
    List.mem_flatMap.mpr ⟨h.comb, h.comb_mem, List.mem_of_mem_tail ha⟩
  apply List.Nodup.map_on (fun a ha b hb he => frame.site_injective (hmem ha) (hmem hb) he)
  have he := h.comb_leaves_head_tail
  rw [he] at hnd
  exact (List.nodup_cons.mp hnd).2

/-- At the final reserved placement the comb occupies its anchor, and all
of its other leaf reservations are vacant. -/
theorem releasedSites_empty (h : CombRootForestNormalForm terminal k)
    {P : Placement n} {transfers : Nat} {site : Nat → Fin n}
    (state : ReservedState P transfers terminal terminal (forestLeaves terminal) site)
    {q : Fin n} (hq : q ∈ h.releasedSites site) :
    packetAt P true q = ∅ := by
  obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hq
  have hleaf := List.mem_of_mem_tail ha
  have homega : a ∈ forestLeaves terminal :=
    List.mem_flatMap.mpr ⟨h.comb, h.comb_mem, hleaf⟩
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro atom hm
  obtain ⟨tree, ht, _, he⟩ := (state.upper_position atom (site a)).mp
    ((mem_packetAt _ _ _ _).mp hm)
  have hid := state.frame.site_injective homega (state.frame.firstLeaf_in_omega ht) he
  have parts := List.nodup_flatMap.mp state.frame.omega_nodup
  by_cases hsame : tree = h.comb
  · subst tree
    have hnd : (h.comb.firstLeaf :: h.comb.leaves.tail).Nodup := by
      have hnd := parts.1 h.comb h.comb_mem
      rw [h.comb_leaves_head_tail] at hnd
      exact hnd
    exact (List.nodup_cons.mp hnd).1 (hid ▸ ha)
  · have : Std.Symm (fun A B : UpperFusionTree n => List.Disjoint A.leaves B.leaves) :=
      ⟨fun _ _ hd => hd.symm⟩
    exact List.disjoint_left.mp (parts.2.forall h.comb_mem ht (fun heq => hsame heq.symm))
      hleaf (hid ▸ tree.firstLeaf_mem)

theorem mergeMass_eq (h : CombRootForestNormalForm terminal k) :
    forestMergeMass terminal = k - 1 := by
  have hbefore := singletonRoots_mergeMass_zero h.before h.before_singleton
  have hafter := singletonRoots_mergeMass_zero h.after h.after_singleton
  rw [h.forest_eq]
  simp only [forestMergeMass, List.map_append, List.sum_append, List.map_cons,
    List.sum_cons]
  have hb : (h.before.map (fun T => T.leaves.length - 1)).sum = 0 := by
    simpa [forestMergeMass] using hbefore
  have ha : (h.after.map (fun T => T.leaves.length - 1)).sum = 0 := by
    simpa [forestMergeMass] using hafter
  rw [hb, ha, h.comb_leaf_count]
  omega

theorem branchDefect_eq_zero (h : CombRootForestNormalForm terminal k) :
    (terminal.map UpperFusionTree.leftBranchDefect).sum = 0 := by
  have hbefore := singletonRoots_branchDefect_zero h.before h.before_singleton
  have hafter := singletonRoots_branchDefect_zero h.after h.after_singleton
  have hcomb := (h.comb.defect_zero_iff_leftComb).mpr h.comb_leftComb
  rw [h.forest_eq]
  simp only [List.map_append, List.map_cons, List.sum_append, List.sum_cons]
  rw [hbefore, hafter]
  omega

theorem gapDebt_eq (h : CombRootForestNormalForm terminal k) :
    forestGapDebt terminal = (k - 1).choose 2 := by
  have hbefore := singletonRoots_gapDebt_zero h.before h.before_singleton
  have hafter := singletonRoots_gapDebt_zero h.after h.after_singleton
  have hcomb := h.comb.gapDebt_add_defect
  have hzero := (h.comb.defect_zero_iff_leftComb).mpr h.comb_leftComb
  have hdebt : h.comb.leftGapDebt = (k - 1).choose 2 := by
    simpa [hzero, h.comb_leaf_count] using hcomb
  rw [h.forest_eq]
  simp only [forestGapDebt, List.map_append, List.map_cons, List.sum_append,
    List.sum_cons]
  have hb : (h.before.map UpperFusionTree.leftGapDebt).sum = 0 := by
    simpa [forestGapDebt] using hbefore
  have ha : (h.after.map UpperFusionTree.leftGapDebt).sum = 0 := by
    simpa [forestGapDebt] using hafter
  rw [hb, ha, hdebt]
  simp

theorem crossDefect_eq_zero (h : CombRootForestNormalForm terminal k) :
    forestCrossDefect terminal = 0 := by
  have haccount := forest_crossDefect_identity terminal
  rw [h.gapDebt_eq, h.branchDefect_eq_zero, h.mergeMass_eq] at haccount
  omega

/-- A full `n`-leaf forest of this shape has exactly `n-k+1` roots. -/
theorem length_eq (h : CombRootForestNormalForm terminal k)
    (hleaves : (forestLeaves terminal).length = n) :
    terminal.length = n - k + 1 := by
  have hmass := forestMergeMass_balance terminal
  rw [h.mergeMass_eq, hleaves] at hmass
  have hk := h.two_le
  have hkn := h.lt_sites
  omega

end CombRootForestNormalForm
end RSR2History
