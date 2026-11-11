import FusionLogEnumeration.LiteralSurvivorRecovery

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation
  FusionLogSchedule

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

private theorem lastAtSite_fixed_of_cast (q : ZMod n) (x : ℤ)
    (same : (x : ZMod n) = q) : lastAtSite q x = x := by
  have cast : ((q.val : ℤ) : ZMod n) = (x : ZMod n) := by simpa using same.symm
  obtain ⟨k, hk⟩ := (ZMod.intCast_eq_intCast_iff_dvd_sub (q.val : ℤ) x n).mp cast
  have eq : x = (q.val : ℤ) + k * n := by nlinarith [hk]
  rw [eq, lastAtSite_periodic]
  simp [lastAtSite]

/-- At a hole, the floor-to-occupied-site lift has no new output value.
This is a static property of the canonical source encoding. -/
theorem occupiedRounding_map_step_of_hole (S : Finset (ZMod n)) (nonempty : S.Nonempty)
    (x : ℤ) (hole : ((x + 1 : ℤ) : ZMod n) ∉ S) :
    (occupiedRounding S nonempty).map (x + 1) = (occupiedRounding S nonempty).map x := by
  apply le_antisymm
  · obtain ⟨q, hq, top⟩ := Finset.exists_mem_eq_sup' nonempty
      (fun q => lastAtSite q (x + 1))
    have upper := lastAtSite_le q (x + 1)
    have strict : lastAtSite q (x + 1) ≠ x + 1 := by
      intro same
      have cast := lastAtSite_cast q (x + 1)
      rw [same] at cast
      exact hole (cast ▸ hq)
    have below : lastAtSite q (x + 1) ≤ x := by omega
    have fixed := lastAtSite_fixed_of_cast q (lastAtSite q (x + 1))
      (lastAtSite_cast q (x + 1))
    have mono := lastAtSite_monotone q below
    rw [fixed] at mono
    change S.sup' nonempty (fun q => lastAtSite q (x + 1)) ≤ _
    rw [top]
    exact mono.trans (Finset.le_sup' (fun q => lastAtSite q x) hq)
  · exact (occupiedRounding S nonempty).monotone (by omega)

theorem occupiedRounding_position_step_of_hole
    (S : Finset (ZMod n)) (nonempty : S.Nonempty) (q : ZMod n)
    (hole : q + 1 ∉ S) :
    (occupiedRounding S nonempty).position (q + 1) =
      (occupiedRounding S nonempty).position q := by
  have h := occupiedRounding_map_step_of_hole S nonempty (q.val : ℤ) (by simpa using hole)
  have casts := congrArg (fun z : ℤ => (z : ZMod n)) h
  simpa only [← SourceOrderLift.position_intCast, Int.cast_add, Int.cast_natCast,
    Int.cast_one, ZMod.natCast_zmod_val] using casts

theorem occupiedRounding_position_through_holes
    (S : Finset (ZMod n)) (nonempty : S.Nonempty) (q : ZMod n)
    (present : q ∈ S) (f : ℕ)
    (holes : ∀ t : ℕ, 1 ≤ t → t ≤ f → q + (t : ZMod n) ∉ S) :
    (occupiedRounding S nonempty).position (q + (f : ZMod n)) = q := by
  induction f with
  | zero => simpa using occupiedRounding_fixed S nonempty q present
  | succ f ih =>
    rw [Nat.cast_add, Nat.cast_one, ← add_assoc,
      occupiedRounding_position_step_of_hole S nonempty _ (by
        simpa [Nat.cast_add, add_assoc] using holes (f + 1) (by omega) (by omega))]
    exact ih (by intro t ht htf; exact holes t ht (by omega))

namespace LiteralPacketStart

variable {C : MarkedCircle α} [NeZero C.rank]

/-- Source indices whose initial physical packet intersects the atom block.
Intersection makes this encoding preserve unions on all blocks; the circle
certificate proves exact decoding for the blocks actually used by a schedule. -/
def indexBlock (start : LiteralPacketStart C n) (B : Finset α) : Finset (ZMod n) :=
  Finset.univ.filter (fun z =>
    ((siteLabels start.initial
      ((occupiedRounding (occupiedSites start.initial) start.occupied_nonempty).position z))
      ∩ B).Nonempty)

theorem indexBlock_union (start : LiteralPacketStart C n) (A B : Finset α) :
    start.indexBlock (A ∪ B) = start.indexBlock A ∪ start.indexBlock B := by
  ext z
  simp only [indexBlock, Finset.mem_filter, Finset.mem_univ, true_and,
    Finset.nonempty_def, Finset.mem_inter, Finset.mem_union]
  aesop

theorem indexBlock_of_initial_at (start : LiteralPacketStart C n)
    {q : ZMod n} {B : Finset α} (atSite : start.initial q = some B) :
    start.indexBlock B = sourceFiber
      (occupiedRounding (occupiedSites start.initial) start.occupied_nonempty).position q := by
  ext z
  simp only [indexBlock, Finset.mem_filter, Finset.mem_univ, true_and, mem_sourceFiber]
  let r := (occupiedRounding (occupiedSites start.initial) start.occupied_nonempty).position z
  have present := occupiedRounding_image (occupiedSites start.initial) start.occupied_nonempty z
  simp only [occupiedSites, Finset.mem_filter, Finset.mem_univ, true_and] at present
  change start.initial r ≠ none at present
  obtain ⟨D, hD⟩ : ∃ D, start.initial r = some D := by
    cases h : start.initial r with
    | none => exact (present h).elim
    | some D => exact ⟨D, rfl⟩
  change (siteLabels start.initial r ∩ B).Nonempty ↔ r = q
  simp only [siteLabels, hD, Option.getD_some]
  constructor
  · rintro ⟨a, ha⟩
    obtain ⟨haD, haB⟩ := Finset.mem_inter.mp ha
    by_contra different
    exact (Finset.disjoint_left.mp
      (start.packetPartition.disjoint r q D B different hD atSite)) haD haB
  · intro same
    have blocks : D = B := Option.some.inj ((same ▸ hD).symm.trans atSite)
    obtain ⟨a, ha⟩ := start.packetPartition.nonempty q B atSite
    exact ⟨a, Finset.mem_inter.mpr ⟨blocks ▸ ha, ha⟩⟩

theorem expand_indexBlock_of_initial_at (start : LiteralPacketStart C n)
    {q : ZMod n} {B : Finset α} (atSite : start.initial q = some B) :
    expandBlock (siteLabels start.initial) (start.indexBlock B) = B := by
  rw [start.indexBlock_of_initial_at atSite]
  have present : q ∈ occupiedSites start.initial := by simp [occupiedSites, atSite]
  have member := occupiedRounding_fixed (occupiedSites start.initial) start.occupied_nonempty q present
  have encoded := (placementOfMap_some_iff
    (occupiedRounding (occupiedSites start.initial) start.occupied_nonempty).position q _).mpr
      ⟨rfl, q, (mem_sourceFiber _ _ _).mpr member⟩
  have interpreted := congrFun (initial_placement_interprets start.initial start.occupied_nonempty) q
  rw [atSite] at interpreted
  change some B = (placementOfMap _ q).map _ at interpreted
  rw [encoded] at interpreted
  exact (Option.some.inj interpreted).symm

/-- Positive named order supplies a source-atom boundary for every ordered
neighbour pair, including the wrap and both orientations at rank two. -/
theorem initial_indexBlocks_adjacent (start : LiteralPacketStart C n) (i : ZMod C.rank) :
    SourceAtomAdjacent (start.indexBlock (start.named.block i))
      (start.indexBlock (start.named.block (i + 1))) := by
  let named := start.named.admit start.positiveOrder
  let frame := named.toGapFrame
  have initial : start.initial = frame.decode := by
    rw [named.toGapFrame_decode]
    exact start.initial_eq_named
  have left : start.initial (start.named.position i) = some (start.named.block i) := by
    rw [start.initial_eq_named, start.named.placed_at]
  have right : start.initial (start.named.position (i + 1)) =
      some (start.named.block (i + 1)) := by
    rw [start.initial_eq_named, start.named.placed_at]
  rw [start.indexBlock_of_initial_at left, start.indexBlock_of_initial_at right]
  let a : ZMod n := frame.position i + (frame.gap i : ZMod n)
  have atLeft : (occupiedRounding (occupiedSites start.initial)
      start.occupied_nonempty).position a = frame.position i := by
    apply occupiedRounding_position_through_holes
    · change start.named.position i ∈ occupiedSites start.initial
      simp [occupiedSites, left]
    · intro t ht bound
      have empty := frame.faithful i t (by omega) bound
      rw [← initial] at empty
      simp [occupiedSites, empty]
  have next : a + 1 = frame.position (i + 1) := by
    rw [frame.next_eq]
    dsimp [a]
    abel
  refine ⟨a, (mem_sourceFiber _ _ _).mpr atLeft, ?_⟩
  rw [mem_sourceFiber, next]
  apply occupiedRounding_fixed
  change start.named.position (i + 1) ∈ occupiedSites start.initial
  simp [occupiedSites, right]

end LiteralPacketStart

end FusionLogEnumeration
