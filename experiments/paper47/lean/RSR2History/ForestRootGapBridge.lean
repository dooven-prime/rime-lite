import RSR2History.ForestRootGapMoment
import RSR2History.ForestGapFrameRigidity

/-! The released-root profile is the actual cyclic physical gap profile,
up to the common cyclic cut of the same named roots. -/
namespace RSR2History
open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)

variable {n : Nat} [NeZero n]

private theorem sum_zmod_fin_profile {r : Nat} [NeZero r] (h : Fin r → Nat) :
    (∑ j : ZMod r, h ⟨j.val,ZMod.val_lt j⟩) = ∑ i : Fin r, h i := by
  cases r with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ r => rfl

namespace ReservationFrame
variable {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
  {site : Nat → Fin n}

theorem root_anchor_strict
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    StrictMono (fun i : Fin terminal.length => site terminal[i].firstLeaf) := by
  intro i j hij
  have hjlt : i.val+1 < terminal.length := by have := j.isLt; omega
  have hs := frame.root_anchor_step i.val hjlt
  have hp := terminal[i.val].leaves_length_pos
  have hsub : (terminal.take (i.val+1)).Sublist (terminal.take j.val) := by
    have he := List.take_sublist (i.val+1) (terminal.take j.val)
    simpa only [List.take_take, Nat.min_eq_left (by omega : i.val+1 ≤ j.val)] using he
  have hlen := (hsub.flatMap UpperFusionTree.leaves).length_le
  change (forestLeaves (terminal.take (i.val+1))).length ≤
    (forestLeaves (terminal.take j.val)).length at hlen
  rw [← frame.root_anchor_prefix ⟨i.val+1,hjlt⟩,
    ← frame.root_anchor_prefix j] at hlen
  change (site terminal[i].firstLeaf).val < (site terminal[j].firstLeaf).val
  simp only [Fin.getElem_fin] at *
  omega

theorem root_anchor_injective
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    Function.Injective (fun i : Fin terminal.length => site terminal[i].firstLeaf) :=
  frame.root_anchor_strict.injective

theorem root_anchor_zero
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site) :
    site terminal[(0 : Fin terminal.length)].firstLeaf = 0 := by
  apply Fin.ext
  change (site terminal[(0 : Fin terminal.length)].firstLeaf).val = 0
  simpa only [Fin.val_zero, List.take_zero, forestLeaves, List.flatMap_nil, List.length_nil] using
    frame.root_anchor_prefix (0 : Fin terminal.length)

/-- A gap frame in the original root order, read at one common physical
cursor. Every gap is exactly the root's released interval size. -/
noncomputable def rootPhysicalGapFrame
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (cursor : Fin n) : GapFrame n terminal.length (Fin n) := by
  let index : ZMod terminal.length → Fin terminal.length := fun j =>
    ⟨j.val, ZMod.val_lt j⟩
  let pos : ZMod terminal.length → ZMod n := fun j =>
    ((site terminal[(index j)].firstLeaf).val : ZMod n)-(cursor.val : ZMod n)
  refine {
    position := pos
    block := fun j => terminal[index j].packet
    gap := fun j => forestRootGapProfile terminal (index j)
    anchor := pos 0
    anchor_eq := rfl
    position_injective := ?_
    next_eq := ?_
    gap_total := ?_ }
  · intro j
    have hj := ZMod.val_lt j
    have hp := terminal[(index j)].leaves_length_pos
    have hlen : 1+forestRootGapProfile terminal (index j) =
        terminal[index j].leaves.length := by
      dsimp only [forestRootGapProfile]
      omega
    have hnext : (j+1).val = (j.val+1)%terminal.length := by
      have he : j+1 = ((j.val+1 : Nat) : ZMod terminal.length) := by simp
      rw [he, ZMod.val_natCast]
    by_cases he : j.val+1 < terminal.length
    · have hn : (j+1).val = j.val+1 := hnext.trans (Nat.mod_eq_of_lt he)
      have hs := frame.root_anchor_step j.val he
      have hz := congrArg (fun x : Nat => (x : ZMod n)) hs
      have hidx : index (j+1) = ⟨j.val+1,he⟩ := Fin.ext hn
      dsimp only [pos]
      rw [hidx]
      simp only [Fin.getElem_fin]
      simp only [Nat.cast_add] at hz
      have hc := congrArg (fun x : Nat => (x : ZMod n)) hlen
      simp only [Nat.cast_add,Nat.cast_one] at hc
      simp only [index,Fin.getElem_fin] at hz hc
      rw [hz]
      dsimp only [index]
      linear_combination -hc
    · have heq : j.val+1 = terminal.length := by omega
      have hn : (j+1).val = 0 := by rw [hnext,heq,Nat.mod_self]
      have hs := frame.root_anchor_last (index j) heq
      have hz := congrArg (fun x : Nat => (x : ZMod n)) hs
      simp only [Nat.cast_add,ZMod.natCast_self] at hz
      have hc := congrArg (fun x : Nat => (x : ZMod n)) hlen
      simp only [Nat.cast_add,Nat.cast_one] at hc
      have hidx : index (j+1) = 0 := Fin.ext hn
      dsimp only [pos]
      rw [hidx]
      have hzero := frame.root_anchor_zero
      have hz0 : (site terminal[(0 : Fin terminal.length)].firstLeaf).val = 0 := congrArg Fin.val hzero
      simp only [hz0,Nat.cast_zero]
      simp only [index,Fin.getElem_fin] at hz hc
      simp only [Fin.getElem_fin]
      dsimp only [index]
      linear_combination -hc - hz
  · intro i j he
    have hcast : ((site terminal[index i].firstLeaf).val : ZMod n) =
        ((site terminal[index j].firstLeaf).val : ZMod n) := by
      dsimp only [pos] at he
      linear_combination he
    have hh : site terminal[index i].firstLeaf = site terminal[index j].firstLeaf :=
      by simpa only [zsite_cast] using congrArg zsite hcast
    have hi := frame.root_anchor_injective hh
    exact ZMod.val_injective _ (congrArg Fin.val hi)
  · calc
      _ = ∑ i : Fin terminal.length, forestRootGapProfile terminal i :=
        sum_zmod_fin_profile _
      _ = n-terminal.length := frame.root_gap_total

end ReservationFrame

private theorem fin_val_natCast_zmod {r : Nat} [NeZero r] (i : Fin r) :
    ⟨(i.val : ZMod r).val, ZMod.val_lt _⟩ = i := by
  apply Fin.ext
  exact (ZMod.val_natCast _ _).trans (Nat.mod_eq_of_lt i.isLt)

theorem ReservationFrame.rootPhysicalGapFrame_profile
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (cursor : Fin n) :
    forestFrameGapProfile (frame.rootPhysicalGapFrame cursor) = forestRootGapProfile terminal := by
  funext i
  change forestRootGapProfile terminal ⟨(i.val : ZMod terminal.length).val, ZMod.val_lt _⟩ =
    forestRootGapProfile terminal i
  rw [fin_val_natCast_zmod]

theorem ReservationFrame.rootPhysicalGapFrame_blocks
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (frame : ReservationFrame n terminal terminal (forestLeaves terminal) site)
    (cursor : Fin n) :
    frameBlocks (frame.rootPhysicalGapFrame cursor) = forestPackets terminal := by
  rw [frameBlocks, forestPackets, ← List.ofFn_getElem_eq_map]
  apply congrArg List.ofFn
  funext i
  change terminal[(⟨(i.val : ZMod terminal.length).val, ZMod.val_lt _⟩ : Fin terminal.length)].packet =
    terminal[i].packet
  rw [fin_val_natCast_zmod]

theorem UpperReservedReplay.rootPhysicalGapFrame_packet_at_position
    {P : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal (forestLeaves terminal) site)
    (j : ZMod terminal.length) :
    packetAt P true (zsite ((state.frame.rootPhysicalGapFrame cursor).position j)) =
      (state.frame.rootPhysicalGapFrame cursor).block j := by
  let i : Fin terminal.length := ⟨j.val, ZMod.val_lt j⟩
  exact state.packet_at_anchor (tree := terminal[i]) (List.getElem_mem i.isLt)

/-- The abstract released-root profile and the actual sorted physical
source profile have exactly the same moment. Root identities, circular
order and the common physical cursor are retained throughout. -/
theorem UpperReservedReplay.gapMoment_eq_root
    (hn : 1 < n) {P : Placement n} {cursor : Fin n}
    {terminal : List (UpperFusionTree n)} [NeZero terminal.length]
    {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor n terminal terminal (forestLeaves terminal) site)
    (source : ForestTerminalSource n terminal.length P) :
    forestGapMoment source.gapProfile = forestGapMoment (forestRootGapProfile terminal) := by
  classical
  let A := source.sourceFrame
  let B := state.frame.rootPhysicalGapFrame cursor
  have hcycle : (frameBlocks A).IsRotated (frameBlocks B) := by
    rw [show frameBlocks A = cyclicSignature P true from source.frame_blocks,
      show frameBlocks B = forestPackets terminal from state.frame.rootPhysicalGapFrame_blocks cursor]
    exact (state.forest_packet_cycle hn).symm
  obtain ⟨cut,hcut⟩ := hcycle
  have hb : (reindexGapFrame A (cut : ZMod terminal.length)).block = B.block := by
    apply (frameBlocks_eq_iff _ _).mp
    rw [frameBlocks_reindex,hcut]
  have positions : ∀ j : ZMod terminal.length,
      A.position (j+(cut : ZMod terminal.length)) = B.position j+0 := by
    intro j
    have hnon : (B.block j).Nonempty := by
      exact state.packet_nonempty _ (List.getElem_mem (ZMod.val_lt j))
    obtain ⟨a,ha⟩ := hnon
    have hblock := congrFun hb j
    change A.block (j+(cut : ZMod terminal.length)) = B.block j at hblock
    have hA : a ∈ packetAt P true (zsite (A.position (j+(cut : ZMod terminal.length)))) := by
      rw [source.frame_packetAt,hblock]
      exact ha
    have hB : a ∈ packetAt P true (zsite (B.position j)) := by
      rw [state.rootPhysicalGapFrame_packet_at_position]
      exact ha
    have hpA := (mem_packetAt _ _ _ _).mp hA
    have hpB := (mem_packetAt _ _ _ _).mp hB
    have he : zsite (A.position (j+(cut : ZMod terminal.length))) = zsite (B.position j) :=
      congrArg Prod.snd (hpA.symm.trans hpB)
    simpa only [add_zero] using zsite_inj.mp he
  have hm := forestGapFrame_moment_eq_of_positions A B
    (cut : ZMod terminal.length) 0 positions
  simpa only [A,B,ForestTerminalSource.gapProfile,
    state.frame.rootPhysicalGapFrame_profile cursor] using hm

end RSR2History
