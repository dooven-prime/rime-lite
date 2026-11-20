import RSR2History.ForestTerminalSource
import RSR2History.ReservedForestGapIntervals

/-!
Extract a general named terminal source directly from the occupied sites of
an actual all-upper placement. Its displayed cut is the occupied physical
port zero. Root names, strict site order and atom assignment are all read
from that placement; neither a routing allowance nor new labeling is input.
-/
namespace RSR2History
open RSR2.Parametric
variable {n r : Nat} [NeZero n] [NeZero r]

theorem forestTerminalSource_of_occupied
    (P : Placement n)
    (upper : ∀ a, (P a).1 = true)
    (port : (packetAt P true 0).Nonempty)
    (rank : (occupiedSites P true).length = r) :
    Nonempty (ForestTerminalSource n r P) := by
  classical
  let sites := occupiedSites P true
  have hnd : sites.Nodup := (List.nodup_finRange n).filter _
  have hmem (a : Fin n) : (P a).2 ∈ sites := by
    change (P a).2 ∈ occupiedSites P true
    simp only [occupiedSites, List.mem_filter, List.mem_finRange, true_and, bne_iff_ne]
    exact Finset.nonempty_iff_ne_empty.mp
      ⟨a, (mem_packetAt _ _ _ _).mpr (Prod.ext (upper a) rfl)⟩
  let root : Fin n → Fin r := fun a =>
    ⟨sites.idxOf (P a).2, by
      have hlt := List.idxOf_lt_length_iff.mpr (hmem a)
      simpa only [sites, rank] using hlt⟩
  let site : Fin r → Fin n := fun j => sites[j.val]'(by simpa only [sites, rank] using j.isLt)
  have hstrict : StrictMono site := by
    intro i j hij
    apply occupiedSites_strict P true
      (show (⟨i.val, by simpa only [rank] using i.isLt⟩ : Fin _) <
        ⟨j.val, by simpa only [rank] using j.isLt⟩ from hij)
  have hzmem : (0 : Fin n) ∈ sites := by
    simp only [sites, occupiedSites, List.mem_filter, List.mem_finRange, true_and, bne_iff_ne]
    exact port.ne_empty
  let zeroIndex : Fin r := ⟨sites.idxOf 0, by
    have hlt := List.idxOf_lt_length_iff.mpr hzmem
    simpa only [sites, rank] using hlt⟩
  have hzero : site zeroIndex = 0 := by
    have hzlt := List.idxOf_lt_length_iff.mpr hzmem
    change sites[sites.idxOf 0]'hzlt = 0
    exact List.getElem_idxOf hzlt
  have hz : site 0 = 0 := by
    by_cases he : zeroIndex = 0
    · simpa only [he] using hzero
    · have hpos : (0 : Fin r) < zeroIndex := by
        have hi : zeroIndex.val ≠ 0 := by
          intro he'
          apply he
          exact Fin.ext he'
        simpa only [Fin.lt_def, Fin.val_zero] using Nat.pos_of_ne_zero hi
      have hh := hstrict hpos
      rw [hzero] at hh
      exact (Fin.not_lt_zero _ hh).elim
  have hnempty : ∀ j, ∃ a, root a = j := by
    intro j
    have hm : site j ∈ sites := List.getElem_mem _
    have hpacket : (packetAt P true (site j)).Nonempty := by
      apply Finset.nonempty_iff_ne_empty.mpr
      simpa only [sites, occupiedSites, List.mem_filter, List.mem_finRange,
        true_and, bne_iff_ne] using hm
    obtain ⟨a, ha⟩ := hpacket
    have hpos := congrArg Prod.snd ((mem_packetAt _ _ _ _).mp ha)
    refine ⟨a, Fin.ext ?_⟩
    change sites.idxOf (P a).2 = j.val
    rw [hpos]
    exact hnd.idxOf_getElem j.val _
  have hstart : ∀ a, P a = (true, site (root a)) := by
    intro a
    apply Prod.ext (upper a)
    have hlt := List.idxOf_lt_length_iff.mpr (hmem a)
    change (P a).2 = sites[sites.idxOf (P a).2]'hlt
    exact (List.getElem_idxOf hlt).symm
  exact ⟨⟨root, site, hstrict, hz, hnempty, hstart⟩⟩

theorem UpperReservedReplay.forest_terminal_source_of_anchor
    (hn : 1 < n) {P : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal
      (forestLeaves terminal) site)
    (upper : ∀ a, (P a).1 = true)
    (rank : terminal.length = r)
    {T : UpperFusionTree n} (ht : T ∈ terminal)
    (anchor : cursor = site T.firstLeaf) :
    Nonempty (ForestTerminalSource n r P) := by
  have hp := state.packet_at_anchor ht
  rw [← anchor] at hp
  simp only [sub_self, zsite_zero] at hp
  have hport : (packetAt P true 0).Nonempty := hp.symm ▸ state.packet_nonempty T ht
  have hrank : (occupiedSites P true).length = r := by
    have he := (state.forest_packet_cycle hn).perm.length_eq
    simpa only [forestPackets, List.length_map, signature_eq_occupied_map, rank] using he.symm
  exact forestTerminalSource_of_occupied P upper hport hrank

end RSR2History
