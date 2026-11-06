import RegisteredAbsorptionChains.NoSplitting
import RegisteredAbsorptionChains.SourceOrderAdmission
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Two source atoms belong to a common current packet. -/
def PacketTogether (placed : Placement n (Finset (ZMod n)))
    (x y : ZMod n) : Prop :=
  ∃ q B, placed q = some B ∧ x ∈ B ∧ y ∈ B

/-- `coarse` may fuse packets of `fine`, but cannot separate one of them. -/
def PacketRefines (fine coarse : Placement n (Finset (ZMod n))) : Prop :=
  ∀ x y, PacketTogether fine x y → PacketTogether coarse x y

theorem actual_word_refines (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F s.placed) :
    PacketRefines s.placed (run F s word).placed := by
  intro x y together
  obtain ⟨q, B, hpacket, hx, hy⟩ := together
  exact no_split_from_reachable F s word hn reachable q B hpacket x y hx hy

/-- Failure of refinement rules out every actual continuation to the target.
Refinement alone is not asserted sufficient for a guarded placement word. -/
theorem no_word_to_nonrefining_target (F : Finset (ZMod n))
    (s : Execution n (ZMod n))
    (target : Placement n (Finset (ZMod n))) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F s.placed)
    (hnot : ¬ PacketRefines s.placed target) :
    ¬ ∃ word : List Letter, (run F s word).placed = target := by
  rintro ⟨word, htarget⟩
  apply hnot
  rw [← htarget]
  exact actual_word_refines F s word hn reachable

/-- The whole source packet, not merely a selected pair of its atoms,
lies in one future packet after a literal word. -/
theorem source_packet_subset_future (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f)
    (q : ZMod n) (B : Finset (ZMod n))
    (hpacket : s.placed q = some B) :
    ∃ q' B', (run F s word).placed q' = some B' ∧ B ⊆ B' := by
  obtain ⟨hB, hne⟩ :=
    (placementOfMap_some_iff f q B).mp (hplaced ▸ hpacket)
  obtain ⟨x, hx⟩ := hne
  let g := forwardMapRun f word
  let q' := g x
  have hfx : f x = q := by
    apply (mem_sourceFiber f x q).mp
    exact hB.symm ▸ hx
  have hsubset : B ⊆ sourceFiber g q' := by
    intro y hy
    have hfy : f y = q := by
      apply (mem_sourceFiber f y q).mp
      exact hB.symm ▸ hy
    exact (mem_sourceFiber g y q').mpr
      (forwardMapRun_preserves_equal f word y x (hfy.trans hfx.symm))
  have hnonempty : (sourceFiber g q').Nonempty := ⟨x, by simp [q']⟩
  refine ⟨q', sourceFiber g q', ?_, hsubset⟩
  rw [run_placementOfMap F s f word hn hplaced]
  exact (placementOfMap_some_iff g q' (sourceFiber g q')).mpr
    ⟨rfl, hnonempty⟩

/-- A target cut can be reached only if every current packet sits inside one
of its actual target blocks. This is necessary, not a word-construction. -/
theorem source_packet_subset_target_block (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F s.placed)
    (target : Placement n (Finset (ZMod n)))
    (htarget : (run F s word).placed = target)
    (q : ZMod n) (B : Finset (ZMod n))
    (hpacket : s.placed q = some B) :
    ∃ B' ∈ placedBlocks target, B ⊆ B' := by
  obtain ⟨lift, hplaced⟩ :=
    reachable_source_ordered F s.placed hn reachable
  obtain ⟨q', B', hfuture, hsubset⟩ :=
    source_packet_subset_future F s lift.position word hn hplaced q B hpacket
  refine ⟨B', ?_, hsubset⟩
  apply (mem_placedBlocks target B').mpr
  have hBne : B.Nonempty :=
    ((placementOfMap_some_iff lift.position q B).mp (hplaced ▸ hpacket)).2
  exact ⟨hBne.mono hsubset, q', htarget ▸ hfuture⟩

/-- If a target cut consists of the selected carrier and named outside
intervals, every current outside packet must fit in one target interval. -/
theorem outside_packet_within_target_interval (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F s.placed)
    (target : Placement n (Finset (ZMod n)))
    (htarget : (run F s word).placed = target)
    (C : Finset (ZMod n))
    (intervals : Finset (Finset (ZMod n)))
    (hblocks : placedBlocks target = insert C intervals)
    (q : ZMod n) (B : Finset (ZMod n))
    (hpacket : s.placed q = some B) (hBne : B.Nonempty)
    (houtside : Disjoint B C) :
    ∃ I ∈ intervals, B ⊆ I := by
  obtain ⟨B', hB', hsubset⟩ :=
    source_packet_subset_target_block F s word hn reachable target htarget q B hpacket
  have hmember : B' = C ∨ B' ∈ intervals := by
    simpa [hblocks] using hB'
  rcases hmember with hC | hI
  · obtain ⟨x, hx⟩ := hBne
    exact False.elim ((Finset.disjoint_left.mp houtside) hx (hC ▸ hsubset hx))
  · exact ⟨B', hI, hsubset⟩

end RegisteredAbsorptionChains
