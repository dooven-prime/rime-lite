import RSR2History.ReservedInvariant
import Mathlib.Data.List.Sort

/-! Deriving physical cyclic order and the fusion gap from reservation data. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

theorem forestLeaves_filter_heads (forest : List (UpperFusionTree n))
    (hnd : (forestLeaves forest).Nodup) :
    (forestLeaves forest).filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf) =
      forest.map UpperFusionTree.firstLeaf := by
  have hparts := List.nodup_flatMap.mp hnd
  have : Std.Symm (fun A B : UpperFusionTree n => List.Disjoint A.leaves B.leaves) :=
    ⟨fun _ _ h => h.symm⟩
  have ht : ∀ tree ∈ forest,
      tree.leaves.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf) = [tree.firstLeaf] := by
    intro tree htree
    have hp : ∀ a ∈ tree.leaves,
        (a ∈ forest.map UpperFusionTree.firstLeaf) ↔ a = tree.firstLeaf := by
      intro a ha
      constructor
      · rintro hm
        obtain ⟨other, ho, he⟩ := List.mem_map.mp hm
        by_cases hsame : tree = other
        · simpa [← hsame] using he.symm
        · have hd := hparts.2.forall htree ho hsame
          exact False.elim (List.disjoint_left.mp hd ha (he ▸ other.firstLeaf_mem))
      · intro he
        exact he ▸ List.mem_map.mpr ⟨tree, htree, rfl⟩
    have he : tree.leaves.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf) =
        tree.leaves.filter (fun a => a = tree.firstLeaf) := by
      apply List.filter_congr
      intro a ha
      exact decide_eq_decide.mpr (hp a ha)
    rw [he, List.filter_eq, List.count_eq_one_of_mem (hparts.1 tree htree) tree.firstLeaf_mem]
    rfl
  change (forest.flatMap UpperFusionTree.leaves).filter _ = _
  rw [List.filter_flatMap, List.flatMap_congr ht]
  exact List.map_eq_flatMap.symm

theorem ReservationFrame.anchor_cycle
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site) :
    (forest.map UpperFusionTree.firstLeaf).IsRotated
      (omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)) := by
  have hnd : (forestLeaves forest).Nodup := h.complete.nodup_iff.mpr List.nodup_range
  have hc := cyclic_filter h.prefix_order (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)
  rw [forestLeaves_filter_heads forest hnd] at hc
  have he : (omega.filter (fun a => a < k)).filter
      (fun a => a ∈ forest.map UpperFusionTree.firstLeaf) =
      omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf) := by
    rw [List.filter_filter]
    apply List.filter_congr
    intro a _
    by_cases ha : a ∈ forest.map UpperFusionTree.firstLeaf
    · obtain ⟨tree, ht, rfl⟩ := List.mem_map.mp ha
      simp [h.firstLeaf_lt ht, ha]
    · simp [ha]
  exact he ▸ hc

theorem ReservationFrame.sites_strict
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site) :
    (omega.map site).Pairwise (· < ·) := by
  rw [List.pairwise_iff_getElem]
  intro i j hi hj hij
  have hi' : i < omega.length := by simpa using hi
  have hj' : j < omega.length := by simpa using hj
  simp only [List.getElem_map]
  change (site omega[i]).val < (site omega[j]).val
  rw [h.site_index _ (List.getElem_mem hi'), h.site_index _ (List.getElem_mem hj'),
    h.omega_nodup.idxOf_getElem i hi', h.omega_nodup.idxOf_getElem j hj']
  exact hij

theorem ReservedState.occupied_sites
    {P : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) :
    occupiedSites P true =
      (omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)).map site := by
  have hsorted : (occupiedSites P true).Pairwise (· < ·) := by
    rw [List.pairwise_iff_getElem]
    intro i j hi hj hij
    exact occupiedSites_strict P true (show (⟨i, hi⟩ : Fin _) < ⟨j, hj⟩ from hij)
  have hsorted' : (((omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)).map site)).Pairwise (· < ·) := by
    rw [List.pairwise_map]
    exact (List.pairwise_map.mp h.frame.sites_strict).filter _
  apply hsorted.eq_of_mem_iff hsorted'
  intro q
  simp only [occupiedSites, List.mem_filter, List.mem_finRange, true_and,
    bne_iff_ne, List.mem_map, decide_eq_true_eq]
  constructor
  · intro hne
    obtain ⟨a, ha⟩ := Finset.nonempty_iff_ne_empty.mpr hne
    obtain ⟨tree, ht, _, he⟩ := (h.upper_position a q).mp ((mem_packetAt _ _ _ _).mp ha)
    exact ⟨tree.firstLeaf, ⟨h.frame.firstLeaf_in_omega ht, ⟨tree, ht, rfl⟩⟩, he.symm⟩
  · rintro ⟨id, ⟨_, hid⟩, he⟩
    obtain ⟨tree, ht, rfl⟩ := hid
    rw [← he, h.packet_at_anchor ht]
    exact (h.packet_nonempty tree ht).ne_empty

/-- The physical anchor order is derived, rather than supplied to `Reserved`. -/
theorem ReservedState.current_packet_cycle
    {P : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) :
    (forestPackets forest).IsRotated (cyclicSignature P true) := by
  have hc : ((forest.map UpperFusionTree.firstLeaf).map site).IsRotated
      ((omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)).map site) :=
    h.frame.anchor_cycle.map site
  have he : ((forest.map UpperFusionTree.firstLeaf).map site).map (packetAt P true) =
      forestPackets forest := by
    simp only [List.map_map, forestPackets]
    apply List.map_congr_left
    intro tree ht
    exact h.packet_at_anchor ht
  have hm : (((forest.map UpperFusionTree.firstLeaf).map site).map (packetAt P true)).IsRotated
      (((omega.filter (fun a => a ∈ forest.map UpperFusionTree.firstLeaf)).map site).map (packetAt P true)) :=
    hc.map (packetAt P true)
  rw [he, ← h.occupied_sites, ← signature_eq_occupied_map] at hm
  exact hm

section FusionGeometry
variable [NeZero n]
open RegisteredAbsorptionChains (GapFrame)

theorem layerView_some_packet (P : Placement n) (layer : Layer) (q : ZMod n)
    (B : Finset (Fin n)) (hb : layerView P layer q = some B) :
    packetAt P layer (zsite q) = B := by
  change (if packetAt P layer (zsite q) = ∅ then none
    else some (packetAt P layer (zsite q))) = some B at hb
  split at hb
  · contradiction
  · exact Option.some.inj hb

/-- Cyclic adjacency supplies the actual consecutive physical holes, with
no prescribed intermediate placement and with both two-packet bindings. -/
theorem cyclic_parents_gap (hn : 1 < n) (P : Placement n) (layer : Layer)
    (left right : ZMod n) (A B : Finset (Fin n)) (tail : List (Finset (Fin n)))
    (hA : packetAt P layer (zsite left) = A) (hB : packetAt P layer (zsite right) = B)
    (hAn : A.Nonempty) (hBn : B.Nonempty)
    (hc : (cyclicSignature P layer).IsRotated (A :: B :: tail)) :
    ∃ f : Nat, f ≤ n-2 ∧ right = left+1+(f : ZMod n) ∧
      ∀ j : Nat, 1 ≤ j → j ≤ f → packetAt P layer (zsite (right-j)) = ∅ := by
  let r := tail.length+2
  have hr : 2 ≤ r := by omega
  have : NeZero r := ⟨by omega⟩
  have hlen : (occupiedSites P layer).length = r := by
    simpa [signature_eq_occupied_map, r] using hc.perm.length_eq
  let original := layerGapFrameOfRank P layer hlen
  obtain ⟨cut, hcut⟩ := hc
  let frame : GapFrame n r (Fin n) := reindexGapFrame original (cut : ZMod r)
  have hdecode : frame.decode = layerView P layer := by simp [frame, original]
  have hblocks : frameBlocks frame = A :: B :: tail := by
    rw [frameBlocks_reindex]
    simpa [original] using hcut
  have h01 : (1 : ZMod r).val = 1 := by
    have : Fact (1 < r) := ⟨by omega⟩
    exact ZMod.val_one r
  have hb0 : frame.block 0 = A := by
    have he := congrArg (fun xs => xs[0]?) hblocks
    simpa [frameBlocks, r] using he
  have hb1 : frame.block 1 = B := by
    have he := congrArg (fun xs => xs[1]?) hblocks
    simpa [frameBlocks, r] using he
  have position_of_block (j : ZMod r) (q : ZMod n) (packet : Finset (Fin n))
      (hblock : frame.block j = packet) (hpacket : packetAt P layer (zsite q) = packet)
      (hne : packet.Nonempty) : frame.position j = q := by
    have he := frame.decode_at j
    rw [hdecode, hblock] at he
    have hpacket' := layerView_some_packet P layer (frame.position j) packet he
    obtain ⟨a, ha⟩ := hne
    have hpos := (mem_packetAt P layer (zsite (frame.position j)) a).mp (hpacket'.symm ▸ ha)
    have hpos' := (mem_packetAt P layer (zsite q) a).mp (hpacket.symm ▸ ha)
    exact zsite_inj.mp (congrArg Prod.snd (hpos.symm.trans hpos'))
  have hp0 := position_of_block 0 left A hb0 hA hAn
  have hp1 := position_of_block 1 right B hb1 hB hBn
  have hgap : frame.gap 0 ≤ n-2 := by
    have he := frame.gap_total
    have hle := Finset.single_le_sum (fun j _ => Nat.zero_le (frame.gap j)) (Finset.mem_univ (0 : ZMod r))
    omega
  have hnext := frame.next_eq 0
  simp only [zero_add, hp0, hp1] at hnext
  refine ⟨frame.gap 0, hgap, hnext, ?_⟩
  intro j hj hjf
  have ht : 1 ≤ 1+frame.gap 0-j := by omega
  have ht' : 1+frame.gap 0-j ≤ frame.gap 0 := by omega
  have hempty := frame.faithful 0 (1+frame.gap 0-j) (by omega) ht'
  have hsite : frame.position 0 + ((1+frame.gap 0-j : Nat) : ZMod n) = right-j := by
    rw [hp0, Nat.cast_sub (by omega : j ≤ 1+frame.gap 0), Nat.cast_add, Nat.cast_one, hnext]
    ring
  rw [hsite, hdecode] at hempty
  exact (layerView_eq_none P layer (right-j)).mp hempty

theorem ReservedState.fusion_word
    (hn : 1 < n) {P : Placement n} {k : Nat} {A B : UpperFusionTree n}
    {tail terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k (A :: B :: tail) terminal omega site)
    (frame : ReservationFrame k (.merge A B :: tail) terminal omega site) :
    ∃ Q word, runLogged n hn P word =
      some (Q, [.fusion true A.packet B.packet (A.packet ∪ B.packet)]) ∧
      ReservedState Q k (.merge A B :: tail) terminal omega site ∧ word.length ≤ 4*n := by
  obtain ⟨f, hfn, hgap, hholes⟩ := cyclic_parents_gap hn P true
    ((site A.firstLeaf).val : ZMod n) ((site B.firstLeaf).val : ZMod n)
    A.packet B.packet (forestPackets tail)
    (by simpa using h.packet_at_anchor (tree := A) (by simp))
    (by simpa using h.packet_at_anchor (tree := B) (by simp))
    (h.packet_nonempty A (by simp)) (h.packet_nonempty B (by simp))
    (by simpa [forestPackets] using h.current_packet_cycle.symm)
  exact h.fusion_word_of_gap hn frame f hfn hgap hholes

/-- The target frame is derived from the future forest, rather than assumed
as a physical postcondition. No target placement or word is an input. -/
theorem ReservedState.fusion_word_of_future
    (hn : 1 < n) {P : Placement n} {k kfinal : Nat} {A B : UpperFusionTree n}
    {tail terminal : List (UpperFusionTree n)} {events : List (EffectiveEvent n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k (A :: B :: tail) terminal omega site)
    (future : UpperForestPath k (.merge A B :: tail) events kfinal terminal) :
    ∃ Q word, runLogged n hn P word =
      some (Q, [.fusion true A.packet B.packet (A.packet ∪ B.packet)]) ∧
      ReservedState Q k (.merge A B :: tail) terminal omega site ∧ word.length ≤ 4*n := by
  have update : UpperForestStep k (A :: B :: tail)
      (.fusion true A.packet B.packet (A.packet ∪ B.packet)) k (.merge A B :: tail) :=
    .fusion A B tail (.refl _) (.refl _)
  have frame := ReservationFrame.of_path future (update.complete_leaves h.frame.complete)
    h.frame.terminal_order h.frame.site_injective h.frame.site_index
  exact h.fusion_word hn frame

theorem ReservedState.transfer_word_of_future
    (hn : 1 < n) {P : Placement n} {k kfinal : Nat}
    {forest terminal : List (UpperFusionTree n)} {events : List (EffectiveEvent n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) (source : ZMod n)
    (hsource : (packetAt P false (zsite source)).Nonempty)
    (future : UpperForestPath (k+1)
      (.leaf k (packetAt P false (zsite source)) :: forest) events kfinal terminal) :
    ∃ Q word, runLogged n hn P word =
      some (Q, [.transfer (packetAt P false (zsite source))]) ∧
      ReservedState Q (k+1) (.leaf k (packetAt P false (zsite source)) :: forest)
        terminal omega site ∧ word.length ≤ 2*n+1 := by
  have update : UpperForestStep k forest (.transfer (packetAt P false (zsite source)))
      (k+1) (.leaf k (packetAt P false (zsite source)) :: forest) :=
    .transfer _ forest (.refl _) (.refl _)
  have frame := ReservationFrame.of_path future (update.complete_leaves h.frame.complete)
    h.frame.terminal_order h.frame.site_injective h.frame.site_index
  exact h.transfer_word hn source hsource frame

end FusionGeometry

end RSR2History
