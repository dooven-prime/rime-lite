import RSR2History.ReservedForestGapIntervals
import RSR2History.ForestGapMoment

/-! Root-wise released-hole profiles. The profile uses the retained literal
forest order; a root's internal binary shape does not affect its entry. -/
namespace RSR2History

def forestRootGapProfile (terminal : List (UpperFusionTree n))
    (i : Fin terminal.length) : Nat := terminal[i].leaves.length-1

theorem forestRootGapProfile_eq_zero_iff (terminal : List (UpperFusionTree n))
    (i : Fin terminal.length) :
    forestRootGapProfile terminal i = 0 ↔ terminal[i].leaves.length = 1 := by
  have hp := terminal[i].leaves_length_pos
  simp only [forestRootGapProfile]
  omega

theorem forestRootGapProfile_pos_iff (terminal : List (UpperFusionTree n))
    (i : Fin terminal.length) :
    0 < forestRootGapProfile terminal i ↔ 2 ≤ terminal[i].leaves.length := by
  simp only [forestRootGapProfile]
  omega

theorem forestRootGapProfile_sum (terminal : List (UpperFusionTree n)) :
    (∑ i, forestRootGapProfile terminal i) = forestMergeMass terminal := by
  rw [forestMergeMass, ← List.ofFn_getElem_eq_map, List.sum_ofFn]
  rfl

theorem forestRootGapProfile_mass_balance (terminal : List (UpperFusionTree n)) :
    terminal.length + (∑ i, forestRootGapProfile terminal i) =
      (forestLeaves terminal).length := by
  rw [forestRootGapProfile_sum]
  exact forestMergeMass_balance terminal

/-- At full transfer capacity, released hole mass is exactly the rank loss. -/
theorem ReservationFrame.root_gap_total
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    (∑ i, forestRootGapProfile terminal i) = n-terminal.length := by
  have hb := forestRootGapProfile_mass_balance terminal
  have hl : (forestLeaves terminal).length = n := by
    simpa only [List.length_range] using frame.complete.length_eq
  omega

/-- Consecutive root anchors are separated by precisely the first root's
leaf count in the fixed reservation coordinates. -/
theorem ReservationFrame.root_anchor_step
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (i : Nat) (hi : i+1 < terminal.length) :
    (site terminal[i+1].firstLeaf).val =
      (site terminal[i].firstLeaf).val+terminal[i].leaves.length := by
  have hi0 : i < terminal.length := by omega
  have hdecomp (j : Nat) (hj : j < terminal.length) :
      terminal = terminal.take j ++ terminal[j] :: terminal.drop (j+1) := by
    rw [List.getElem_cons_drop hj, List.take_append_drop]
  have hleaves : forestLeaves (terminal.take (i+1)) =
      forestLeaves (terminal.take i) ++ terminal[i].leaves := by
    rw [List.take_succ_eq_append_getElem hi0]
    simp only [forestLeaves, List.flatMap_append, List.flatMap_cons,
      List.flatMap_nil, List.append_nil]
  rw [frame.root_anchor_index (hdecomp (i+1) hi),
    frame.root_anchor_index (hdecomp i hi0), hleaves, List.length_append]

theorem ReservationFrame.root_anchor_prefix
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (i : Fin terminal.length) :
    (site terminal[i].firstLeaf).val = (forestLeaves (terminal.take i.val)).length := by
  have he : terminal = terminal.take i.val ++ terminal[i.val] :: terminal.drop (i.val+1) := by
    rw [List.getElem_cons_drop i.isLt, List.take_append_drop]
  exact frame.root_anchor_index he

theorem ReservationFrame.root_anchor_last
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (i : Fin terminal.length) (hi : i.val+1 = terminal.length) :
    (site terminal[i].firstLeaf).val+terminal[i].leaves.length = n := by
  have hdecomp : terminal = terminal.take i.val ++ [terminal[i]] := by
    have he : terminal = terminal.take i.val ++ terminal[i.val] :: terminal.drop (i.val+1) := by
      rw [List.getElem_cons_drop i.isLt, List.take_append_drop]
    simpa only [hi, List.drop_length, Fin.getElem_fin] using he
  have hl : (forestLeaves terminal).length = n := by
    simpa only [List.length_range] using frame.complete.length_eq
  rw [frame.root_anchor_prefix]
  rw [hdecomp, forestLeaves, List.flatMap_append, List.flatMap_cons,
    List.flatMap_nil, List.append_nil, List.length_append] at hl
  exact hl

/-- Zero cyclic hole moment is equivalent to having at most one
nontrivial terminal root. The index is in the original forest order. -/
theorem forestRootGapMoment_eq_zero_iff
    (terminal : List (UpperFusionTree n)) [NeZero terminal.length] :
    forestGapMoment (forestRootGapProfile terminal) = 0 ↔
      ∃ q : Fin terminal.length, ∀ i, i ≠ q → terminal[i].leaves.length = 1 := by
  rw [forestGapMoment_eq_zero_iff]
  simp only [forestRootGapProfile_eq_zero_iff]

/-- Two distinct nontrivial roots force a strictly positive numerical gain. -/
theorem forestRootGapMoment_pos_of_two_roots
    (terminal : List (UpperFusionTree n)) [NeZero terminal.length]
    (i j : Fin terminal.length) (hne : i ≠ j)
    (hi : 2 ≤ terminal[i].leaves.length) (hj : 2 ≤ terminal[j].leaves.length) :
    0 < forestGapMoment (forestRootGapProfile terminal) := by
  by_contra h
  have hz : forestGapMoment (forestRootGapProfile terminal) = 0 := by omega
  obtain ⟨q,hq⟩ := (forestRootGapMoment_eq_zero_iff terminal).mp hz
  by_cases he : i=q
  · have he' : j ≠ q := by intro hh; exact hne (he.trans hh.symm)
    have := hq j he'
    omega
  · have := hq i he
    omega

/-- The gain pays all released holes except at most the largest root's
own interval, independently of the roots' cyclic separation. -/
theorem ReservationFrame.root_gap_moment_lower_bound
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    (n-terminal.length)-Finset.univ.sup (forestRootGapProfile terminal) ≤
      forestGapMoment (forestRootGapProfile terminal) := by
  rw [← frame.root_gap_total]
  exact forestGapMoment_lower_bound _

/-- Any two-root forest whose trees each have two leaves has unit moment. -/
theorem forestRootGapMoment_two_binary_roots
    (A B : UpperFusionTree n) (ha : A.leaves.length = 2)
    (hb : B.leaves.length = 2) :
    forestGapMoment (forestRootGapProfile [A,B]) = 1 := by
  have he : forestRootGapProfile [A,B] = (fun _ : Fin 2 => 1) := by
    funext i
    fin_cases i <;> simp [forestRootGapProfile,ha,hb]
  rw [he]
  exact forestGapMoment_two_unit

end RSR2History
