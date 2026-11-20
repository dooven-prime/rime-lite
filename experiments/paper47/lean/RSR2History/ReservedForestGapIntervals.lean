import RSR2History.UpperReservedReplay
import RSR2History.ForestCrossDefect

/-!
Released reservations of an arbitrary terminal forest. Each root contributes
one consecutive non-anchor interval in the fixed expanded leaf order. The
same cursor maps these to disjoint circular intervals of actual vacant
physical sites. No tree shape, new root order, or routing budget is assumed.
-/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

/-- The reservations consumed inside one root, retaining its own leaf order. -/
def UpperFusionTree.releasedReservations (T : UpperFusionTree n)
    (site : Nat → Fin n) : List (Fin n) := T.leaves.tail.map site

private theorem leaves_first_tail (T : UpperFusionTree n) :
    T.leaves = T.firstLeaf :: T.leaves.tail := by
  obtain ⟨tail, ht⟩ := T.leaves_eq_first_cons
  simp [ht]

theorem forest_root_leaf_interval
    {terminal before after : List (UpperFusionTree n)} {T : UpperFusionTree n}
    (h : terminal = before ++ T :: after) :
    forestLeaves terminal = forestLeaves before ++ T.leaves ++ forestLeaves after := by
  simp [h, forestLeaves, List.flatMap_append, List.append_assoc]

namespace ReservationFrame

variable {transfers : Nat} {forest terminal : List (UpperFusionTree n)}
  {site : Nat → Fin n}

/-- A leaf's integer reservation index is its literal root-prefix length
plus its index inside the root. -/
theorem root_site_index
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site)
    {before after : List (UpperFusionTree n)} {T : UpperFusionTree n}
    (h : terminal = before ++ T :: after) (i : Nat) (hi : i < T.leaves.length) :
    (site T.leaves[i]).val = (forestLeaves before).length+i := by
  let pre := forestLeaves before
  have he : forestLeaves terminal = pre ++ (T.leaves ++ forestLeaves after) :=
    (forest_root_leaf_interval h).trans (List.append_assoc _ _ _)
  have hbound : pre.length+i < (forestLeaves terminal).length := by
    rw [he]
    simp only [List.length_append]
    omega
  have hlookup : (forestLeaves terminal)[pre.length+i] = T.leaves[i] := by
    revert hbound
    rw [he]
    intro hbound
    rw [List.getElem_append_right (Nat.le_add_right _ _)]
    simp only [Nat.add_sub_cancel_left, List.getElem_append_left hi]
  rw [← hlookup, frame.site_index _ (List.getElem_mem hbound),
    frame.omega_nodup.idxOf_getElem]

theorem root_anchor_index
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site)
    {before after : List (UpperFusionTree n)} {T : UpperFusionTree n}
    (h : terminal = before ++ T :: after) :
    (site T.firstLeaf).val = (forestLeaves before).length := by
  have hz : T.leaves[0]'T.leaves_length_pos = T.firstLeaf := by
    obtain ⟨tail, ht⟩ := T.leaves_eq_first_cons
    simp [ht]
  simpa only [hz, Nat.add_zero] using frame.root_site_index h 0 T.leaves_length_pos

/-- The entire released interval, rather than only its cardinality. -/
theorem root_released_interval
    (frame : ReservationFrame transfers forest terminal (forestLeaves terminal) site)
    {before after : List (UpperFusionTree n)} {T : UpperFusionTree n}
    (h : terminal = before ++ T :: after) :
    (T.releasedReservations site).map Fin.val =
      List.range' ((site T.firstLeaf).val+1) (T.leaves.length-1) := by
  apply List.ext_getElem
  · simp [UpperFusionTree.releasedReservations]
  · intro i hi hj
    have hitail : i < T.leaves.tail.length := by
      simpa [UpperFusionTree.releasedReservations] using hi
    have hin : i+1 < T.leaves.length := by
      simp only [List.length_tail] at hitail
      omega
    have hv := frame.root_site_index h (i+1) hin
    simp only [UpperFusionTree.releasedReservations, List.getElem_map,
      List.getElem_tail, List.getElem_range'_1, frame.root_anchor_index h]
    omega

end ReservationFrame

theorem UpperFusionTree.releasedReservations_length (T : UpperFusionTree n)
    (site : Nat → Fin n) :
    (T.releasedReservations site).length = T.leaves.length-1 := by
  simp [releasedReservations]

theorem ReservedState.root_released_empty
    {P : Placement n} {transfers : Nat} {terminal : List (UpperFusionTree n)}
    {site : Nat → Fin n}
    (state : ReservedState P transfers terminal terminal (forestLeaves terminal) site)
    {T : UpperFusionTree n} (ht : T ∈ terminal) {q : Fin n}
    (hq : q ∈ T.releasedReservations site) : packetAt P true q = ∅ := by
  obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hq
  have hleaf := List.mem_of_mem_tail ha
  have homega : a ∈ forestLeaves terminal := List.mem_flatMap.mpr ⟨T, ht, hleaf⟩
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro atom hm
  obtain ⟨tree, htree, _, he⟩ := (state.upper_position atom (site a)).mp
    ((mem_packetAt _ _ _ _).mp hm)
  have hid := state.frame.site_injective homega (state.frame.firstLeaf_in_omega htree) he
  have parts := List.nodup_flatMap.mp state.frame.omega_nodup
  by_cases hsame : tree = T
  · subst tree
    have hnd : (T.firstLeaf :: T.leaves.tail).Nodup := by
      rw [← leaves_first_tail]
      exact parts.1 T ht
    exact (List.nodup_cons.mp hnd).1 (hid ▸ ha)
  · have : Std.Symm (fun A B : UpperFusionTree n => List.Disjoint A.leaves B.leaves) :=
      ⟨fun _ _ hd => hd.symm⟩
    exact List.disjoint_left.mp (parts.2.forall ht htree (fun heq => hsame heq.symm))
      hleaf (hid ▸ tree.firstLeaf_mem)

/-- Different root intervals do not share a reserved site. -/
theorem ReservationFrame.released_intervals_pairwise
    {transfers : Nat} {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame transfers terminal terminal (forestLeaves terminal) site) :
    terminal.Pairwise (fun A B =>
      List.Disjoint (A.releasedReservations site) (B.releasedReservations site)) := by
  have hp := (List.nodup_flatMap.mp frame.omega_nodup).2
  apply hp.imp_of_mem
  intro A B hA hB hd
  apply List.disjoint_left.mpr
  intro q hqA hqB
  obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hqA
  obtain ⟨b, hb, he⟩ := List.mem_map.mp hqB
  have ha' := List.mem_of_mem_tail ha
  have hb' := List.mem_of_mem_tail hb
  have hid := frame.site_injective
    (List.mem_flatMap.mpr ⟨B, hB, hb'⟩)
    (List.mem_flatMap.mpr ⟨A, hA, ha'⟩) he
  exact List.disjoint_left.mp hd ha' (hid ▸ hb')

/-- At full leaf capacity, the intervals account for every vacancy, not
just a selected family of usable empty sites. -/
theorem ReservedState.vacant_iff_released_reservation
    {P : Placement n} {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : ReservedState P n terminal terminal (forestLeaves terminal) site)
    (q : Fin n) :
    packetAt P true q = ∅ ↔
      ∃ T ∈ terminal, q ∈ T.releasedReservations site := by
  constructor
  · intro he
    have hlen : (forestLeaves terminal).length = n := by
      simpa only [List.length_range] using state.frame.complete.length_eq
    have hbound : q.val < (forestLeaves terminal).length := by
      simpa only [hlen] using q.isLt
    let a := (forestLeaves terminal)[q.val]
    have ha : a ∈ forestLeaves terminal := List.getElem_mem hbound
    have hsite : site a = q := by
      apply Fin.ext
      rw [state.frame.site_index a ha]
      exact state.frame.omega_nodup.idxOf_getElem q.val hbound
    obtain ⟨T, ht, hleaf⟩ := List.mem_flatMap.mp ha
    have hne : a ≠ T.firstLeaf := by
      intro hs
      have hp := state.packet_at_anchor ht
      rw [← hs, hsite, he] at hp
      exact (state.packet_nonempty T ht).ne_empty hp.symm
    have htail : a ∈ T.leaves.tail := by
      rw [leaves_first_tail] at hleaf
      exact (List.mem_cons.mp hleaf).resolve_left hne
    exact ⟨T, ht, List.mem_map.mpr ⟨a, htail, hsite⟩⟩
  · rintro ⟨T, ht, hq⟩
    exact state.root_released_empty ht hq

/-- The total number of released sites is exactly the leaf-rank loss.
Pairwise disjointness above makes this the size of their union as well. -/
theorem ReservationFrame.released_interval_count
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    terminal.length + (terminal.map (fun T => (T.releasedReservations site).length)).sum = n := by
  have he := forestMergeMass_balance terminal
  have hlen : (forestLeaves terminal).length = n := by simpa using frame.complete.length_eq
  simpa only [UpperFusionTree.releasedReservations_length, forestMergeMass, hlen] using he

section Physical
variable [NeZero n]

/-- The same retained cursor acts on every interval. This is a coordinate
reading of the actual placement, not a physical rotation or new operation. -/
def UpperFusionTree.releasedPhysicalSites (T : UpperFusionTree n)
    (site : Nat → Fin n) (cursor : Fin n) : List (Fin n) :=
  (T.releasedReservations site).map
    (fun q => zsite ((q.val : ZMod n)-(cursor.val : ZMod n)))

private theorem shiftedSite_injective (cursor : Fin n) :
    Function.Injective (fun q : Fin n =>
      zsite ((q.val : ZMod n)-(cursor.val : ZMod n))) := by
  intro p q he
  have hz := zsite_inj.mp he
  have hz' : (p.val : ZMod n) = (q.val : ZMod n) := by linear_combination hz
  simpa only [zsite_cast] using congrArg zsite hz'

theorem UpperFusionTree.releasedPhysicalSites_length (T : UpperFusionTree n)
    (site : Nat → Fin n) (cursor : Fin n) :
    (T.releasedPhysicalSites site cursor).length = T.leaves.length-1 := by
  simp [releasedPhysicalSites, releasedReservations_length]

/-- In physical coordinates the interval may cross site zero. It is
exactly the cyclic image of the fixed integer reservation interval. -/
theorem UpperReservedReplay.root_released_physical_interval
    {P : Placement n} {cursor : Fin n} {transfers : Nat}
    {terminal before after : List (UpperFusionTree n)} {T : UpperFusionTree n}
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor transfers terminal terminal
      (forestLeaves terminal) site)
    (h : terminal = before ++ T :: after) :
    T.releasedPhysicalSites site cursor =
      (List.range' ((site T.firstLeaf).val+1) (T.leaves.length-1)).map
        (fun q : Nat => zsite ((q : ZMod n)-(cursor.val : ZMod n))) := by
  have hi := state.frame.root_released_interval h
  have hm := congrArg
    (fun xs : List Nat => xs.map
      (fun q : Nat => zsite ((q : ZMod n)-(cursor.val : ZMod n)))) hi
  change (T.releasedReservations site).map
      (fun q : Fin n => zsite ((q.val : ZMod n)-(cursor.val : ZMod n))) = _
  rw [List.map_map] at hm
  exact hm

theorem UpperReservedReplay.root_released_physical_empty
    {P : Placement n} {cursor : Fin n} {transfers : Nat}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor transfers terminal terminal
      (forestLeaves terminal) site)
    {T : UpperFusionTree n} (ht : T ∈ terminal) {q : Fin n}
    (hq : q ∈ T.releasedPhysicalSites site cursor) : packetAt P true q = ∅ := by
  obtain ⟨q', hq', rfl⟩ := List.mem_map.mp hq
  have he := ReservedState.root_released_empty state ht hq'
  rw [← zsite_cast q', packetAt_phaseShift] at he
  exact he

/-- All released physical intervals are disjoint under the same cursor.
No assertion that their routing costs add is made. -/
theorem UpperReservedReplay.released_physical_intervals_pairwise
    {P : Placement n} {cursor : Fin n} {transfers : Nat}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor transfers terminal terminal
      (forestLeaves terminal) site) :
    terminal.Pairwise (fun A B =>
      List.Disjoint (A.releasedPhysicalSites site cursor)
        (B.releasedPhysicalSites site cursor)) := by
  apply state.frame.released_intervals_pairwise.imp
  intro A B hd
  apply List.disjoint_left.mpr
  intro q hqA hqB
  obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hqA
  obtain ⟨b, hb, he⟩ := List.mem_map.mp hqB
  have hid := shiftedSite_injective cursor he
  exact List.disjoint_left.mp hd ha (hid ▸ hb)

/-- The physical interval union is exactly the empty-site set of the
actual final replay placement. -/
theorem UpperReservedReplay.vacant_iff_released_physical_site
    {P : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal
      (forestLeaves terminal) site) (q : Fin n) :
    packetAt P true q = ∅ ↔
      ∃ T ∈ terminal, q ∈ T.releasedPhysicalSites site cursor := by
  constructor
  · intro he
    let q' := zsite ((q.val : ZMod n)+(cursor.val : ZMod n))
    have he' : packetAt (phaseShift P true (cursor.val : ZMod n)) true q' = ∅ := by
      dsimp [q']
      rw [packetAt_phaseShift]
      simpa only [add_sub_cancel_right, zsite_cast] using he
    obtain ⟨T, ht, hq'⟩ := (state.vacant_iff_released_reservation q').mp he'
    refine ⟨T, ht, List.mem_map.mpr ⟨q', hq', ?_⟩⟩
    dsimp [q']
    have hz : ((zsite ((q.val : ZMod n)+(cursor.val : ZMod n))).val : ZMod n) =
        (q.val : ZMod n)+(cursor.val : ZMod n) := by simp [zsite]
    rw [hz, add_sub_cancel_right, zsite_cast]
  · rintro ⟨T, ht, hq⟩
    exact state.root_released_physical_empty ht hq

end Physical
end RSR2History
