import FusionLogReplay.PacketSet

namespace FusionLogReplay

open RegisteredAbsorptionChains FusionLogCompression

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

def occupiedSites (P : Placement n (Finset α)) : Finset (ZMod n) :=
  Finset.univ.filter (fun q => P q ≠ none)

def packetRank (P : Placement n (Finset α)) : ℕ := (packetSet P).card

theorem packetRank_eq_occupied (P : Placement n (Finset α))
    (unique : UniquePackets P) :
    packetRank P = (occupiedSites P).card := by
  classical
  have disjoint : (↑(Finset.univ : Finset (ZMod n)) : Set (ZMod n)).PairwiseDisjoint
      (fun q => (P q).toFinset) := by
    intro q _ q' _ ne
    apply Finset.disjoint_left.mpr
    intro B hq hq'
    have a : P q = some B := by simpa using hq
    have b : P q' = some B := by simpa using hq'
    exact ne (unique q q' B a b)
  unfold packetRank packetSet occupiedSites
  rw [Finset.card_biUnion disjoint, Finset.card_filter]
  apply Finset.sum_congr rfl
  intro q _
  cases hq : P q <;> simp [occupiedSites, hq]

theorem packetRank_le_sites (P : Placement n (Finset α))
    (unique : UniquePackets P) : packetRank P ≤ n := by
  rw [packetRank_eq_occupied P unique]
  have h := Finset.card_le_card (Finset.subset_univ (occupiedSites P))
  simpa using h

/-- The actual route's empty coordinates are disjoint from every occupied site. -/
theorem gap_le_hole_count (P : Placement n (Finset α)) (q : ZMod n) (f : ℕ)
    (short : f < n) (unique : UniquePackets P)
    (empty : ∀ i : ℕ, 1 ≤ i → i ≤ f → P (q - (i : ZMod n)) = none) :
    f ≤ n - packetRank P := by
  classical
  let holes := (Finset.range f).image (fun i => q - ((i + 1 : ℕ) : ZMod n))
  have injective : Set.InjOn (fun i : ℕ => q - ((i + 1 : ℕ) : ZMod n))
      (↑(Finset.range f) : Set ℕ) := by
    intro i hi j hj eq
    have hi' : i + 1 < n := by have := Finset.mem_range.mp hi; omega
    have hj' : j + 1 < n := by have := Finset.mem_range.mp hj; omega
    have castEq : ((i + 1 : ℕ) : ZMod n) = ((j + 1 : ℕ) : ZMod n) := by
      have h := congrArg (fun z : ZMod n => q - z) eq
      simpa using h
    have h := congrArg ZMod.val castEq
    rw [ZMod.val_natCast_of_lt hi', ZMod.val_natCast_of_lt hj'] at h
    omega
  have cardinal : holes.card = f := by
    rw [Finset.card_image_of_injOn injective, Finset.card_range]
  have disjoint : Disjoint holes (occupiedSites P) := by
    apply Finset.disjoint_left.mpr
    intro z hz ho
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hz
    have e := empty (i + 1) (by omega) (by have := Finset.mem_range.mp hi; omega)
    have occupied : P (q - ((i + 1 : ℕ) : ZMod n)) ≠ none := by
      simpa [occupiedSites] using ho
    exact occupied e
  have count := Finset.card_le_card (Finset.subset_univ (holes ∪ occupiedSites P))
  rw [Finset.card_union_of_disjoint disjoint, cardinal] at count
  have rankEq := packetRank_eq_occupied P unique
  simp only [Finset.card_univ, ZMod.card] at count
  omega

theorem sourceOrdered_packet_nonempty
    (P : Placement n (Finset (ZMod n))) (ordered : SourceOrdered P)
    (q : ZMod n) (A : Finset (ZMod n)) (atSite : P q = some A) : A.Nonempty := by
  obtain ⟨lift, hp⟩ := ordered
  exact ((placementOfMap_some_iff lift.position q A).mp (hp ▸ atSite)).2

theorem sourceOrdered_site_disjoint
    (P : Placement n (Finset (ZMod n))) (ordered : SourceOrdered P)
    (q q' : ZMod n) (A B : Finset (ZMod n))
    (left : P q = some A) (right : P q' = some B) (different : q ≠ q') :
    Disjoint A B := by
  obtain ⟨lift, hp⟩ := ordered
  have hA := ((placementOfMap_some_iff lift.position q A).mp (hp ▸ left)).1
  have hB := ((placementOfMap_some_iff lift.position q' B).mp (hp ▸ right)).1
  apply Finset.disjoint_left.mpr
  intro a ha hb
  have hq := (mem_sourceFiber lift.position a q).mp (hA.symm ▸ ha)
  have hq' := (mem_sourceFiber lift.position a q').mp (hB.symm ▸ hb)
  exact different (hq.symm.trans hq')

/-- A genuine occupied-port fusion removes exactly one named packet. -/
theorem packetRank_fusion_drop
    (P : Placement n (Finset (ZMod n))) (ordered : SourceOrdered P)
    (A B : Finset (ZMod n)) (hn : 3 ≤ n)
    (left : P 0 = some A) (right : P 1 = some B) :
    packetRank (fusionPlacement P) + 1 = packetRank P := by
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro eq
    have h := ZMod.one_eq_zero_iff.mp eq.symm
    omega
  have hA := sourceOrdered_packet_nonempty P ordered 0 A left
  have hB := sourceOrdered_packet_nonempty P ordered 1 B right
  have disjoint := sourceOrdered_site_disjoint P ordered 0 1 A B left right h01
  have distinct : B ≠ A := by
    intro eq
    obtain ⟨a, ha⟩ := hB
    exact (Finset.disjoint_left.mp disjoint) (eq ▸ ha) ha
  have memA : A ∈ packetSet P := (mem_packetSet P A).mpr ⟨0, left⟩
  have memB : B ∈ (packetSet P).erase A := by
    simp [Finset.mem_erase, distinct, (mem_packetSet P B).mpr ⟨1, right⟩]
  have notUnion : A ∪ B ∉ packetSet P := by
    intro mem
    obtain ⟨q, hq⟩ := (mem_packetSet P _).mp mem
    by_cases zero : q = 0
    · subst q
      have eq : A ∪ B = A := Option.some.inj (hq.symm.trans left)
      obtain ⟨b, hb⟩ := hB
      have ha : b ∈ A := eq ▸ Finset.mem_union_right A hb
      exact (Finset.disjoint_left.mp disjoint) ha hb
    · have other := sourceOrdered_site_disjoint P ordered 0 q A (A ∪ B)
        left hq (Ne.symm zero)
      obtain ⟨a, ha⟩ := hA
      exact (Finset.disjoint_left.mp other) ha (Finset.mem_union_left B ha)
  have notErase : A ∪ B ∉ ((packetSet P).erase A).erase B :=
    fun h => notUnion (Finset.mem_of_mem_erase (Finset.mem_of_mem_erase h))
  have positive := Finset.card_pos.mpr ⟨B, memB⟩
  rw [Finset.card_erase_of_mem memA] at positive
  unfold packetRank
  rw [packetSet_fusion P A B (sourceOrdered_uniquePackets P ordered) left right,
    Finset.card_insert_of_notMem notErase, Finset.card_erase_of_mem memB,
    Finset.card_erase_of_mem memA]
  omega

theorem packetRank_step_event (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (a : Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.placed) :
    packetRank (step F s a).placed + (effectiveEvent s a).toList.length =
      packetRank s.placed := by
  cases a with
  | p =>
      simp only [effectiveEvent, Option.toList_none, List.length_nil, Nat.add_zero]
      exact congrArg Finset.card (packetSet_rotate s.placed 1)
  | d =>
      cases h0 : s.placed 0 <;> cases h1 : s.placed 1
      all_goals try {
        have empty : effectiveEvent s .d = none := by simp [effectiveEvent, h0, h1]
        simpa [packetRank, empty] using congrArg Finset.card (packetSet_step_of_noEvent F s .d empty) }
      rw [show (step F s .d).placed = fusionPlacement s.placed from stepDefect_placed_eq F s]
      simpa [effectiveEvent, h0, h1] using packetRank_fusion_drop _ ordered _ _ hn h0 h1

theorem packetRank_run_ledger (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.placed) :
    packetRank (run F s word).placed + (eventTrace F s word).length =
      packetRank s.placed := by
  induction word generalizing s with
  | nil => simp [run, eventTrace]
  | cons a rest ih =>
      have head := packetRank_step_event F s a hn ordered
      have tail := ih (step F s a) (step_ordered F s a (by omega) ordered)
      simp only [eventTrace, List.length_append]
      change packetRank (run F (step F s a) rest).placed + _ = _
      omega

theorem prefix_rank_and_holes (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 3 ≤ n)
    (ordered : SourceOrdered s.placed) :
    packetRank (run F s word).placed = packetRank s.placed - (eventTrace F s word).length ∧
      n - packetRank (run F s word).placed =
        n - packetRank s.placed + (eventTrace F s word).length := by
  have ledger := packetRank_run_ledger F s word hn ordered
  have bound := packetRank_le_sites s.placed (sourceOrdered_uniquePackets _ ordered)
  omega

end FusionLogReplay
