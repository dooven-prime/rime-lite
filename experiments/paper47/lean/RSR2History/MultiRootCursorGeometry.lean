import RSR2History.SingletonCursorReplay
import RSR2History.BudgetedSilentPreparation

/-! Joint forest reservations use one global leaf order and one cursor.
Terminal routing restores a complete placement, not independent root phases. -/
namespace RSR2History
open RSR2.Parametric

private theorem idxOf_at_middle (pre tail : List Nat) (a : Nat)
    (hnd : (pre ++ a :: tail).Nodup) :
    (pre ++ a :: tail).idxOf a = pre.length := by
  have ha : a ∉ pre := by
    intro hm
    exact (List.nodup_append.mp hnd).2.2 a hm a (by simp) rfl
  simp [List.idxOf_append, ha]

/-- A current merge is an interval of the entire terminal forest expansion,
including the offset contributed by earlier terminal roots. -/
theorem ReservationFrame.forest_ordered_merge_anchor_gap
    {n k : Nat} {A B : UpperFusionTree n}
    {roots terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (before : ReservationFrame k (A :: B :: roots) terminal (forestLeaves terminal) site)
    (after : ReservationFrame k (.merge A B :: roots) terminal (forestLeaves terminal) site) :
    (site B.firstLeaf).val = (site A.firstLeaf).val + A.leaves.length := by
  obtain ⟨root, hroot, hsub⟩ := after.subtrees (.merge A B) (by simp)
  obtain ⟨treesBefore, treesAfter, hforest⟩ := List.append_of_mem hroot
  obtain ⟨left, right, hleaves⟩ := hsub.leaf_interval
  have hinterval : ∃ pre post, forestLeaves terminal = pre ++ A.leaves ++ B.leaves ++ post := by
    refine ⟨forestLeaves treesBefore ++ left, right ++ forestLeaves treesAfter, ?_⟩
    rw [hforest]
    simp [forestLeaves, hleaves, UpperFusionTree.leaves, List.append_assoc]
  obtain ⟨pre, post, hinterval⟩ := hinterval
  obtain ⟨as, ha⟩ := A.leaves_eq_first_cons
  obtain ⟨bs, hb⟩ := B.leaves_eq_first_cons
  have hA : forestLeaves terminal = pre ++ A.firstLeaf :: (as ++ B.leaves ++ post) := by
    simpa [ha, List.append_assoc] using hinterval
  have hB : forestLeaves terminal = (pre ++ A.leaves) ++ B.firstLeaf :: (bs ++ post) := by
    simpa [hb, List.append_assoc] using hinterval
  have iA : (forestLeaves terminal).idxOf A.firstLeaf = pre.length := by
    rw [hA]
    exact idxOf_at_middle _ _ _ (hA ▸ before.omega_nodup)
  have iB : (forestLeaves terminal).idxOf B.firstLeaf = (pre ++ A.leaves).length := by
    rw [hB]
    exact idxOf_at_middle _ _ _ (hB ▸ before.omega_nodup)
  rw [before.site_index A.firstLeaf (before.firstLeaf_in_omega (by simp)),
    before.site_index B.firstLeaf (before.firstLeaf_in_omega (by simp)), iA, iB]
  simp

section Physical
variable {n : Nat} [NeZero n]

private theorem fusion_length (cursor left right : Fin n) (f : Nat)
    (hgap : right.val = left.val + f + 1) :
    (phaseFreeFusionWord true ((left.val : ZMod n) - (cursor.val : ZMod n))
      ((right.val : ZMod n) - (cursor.val : ZMod n)) f).length =
      cursorTurn n cursor.val (left.val + f) + 2*f + 1 := by
  have haf : left.val + f < n := by have := right.isLt; omega
  rw [cursorTurn_eq_zmod_val cursor.isLt haf]
  by_cases hf : f = 0
  · subst f
    have he : -((left.val : ZMod n) - (cursor.val : ZMod n)) =
        (cursor.val : ZMod n) - ((left.val + 0 : Nat) : ZMod n) := by simp
    simp [phaseFreeFusionWord, he, pWord]
  · have he : (1 : ZMod n) - ((right.val : ZMod n) - (cursor.val : ZMod n)) =
        (cursor.val : ZMod n) - ((left.val + f : Nat) : ZMod n) := by
      rw [hgap, Nat.cast_add, Nat.cast_add, Nat.cast_one]
      ring
    simp only [phaseFreeFusionWord, if_neg hf, List.length_append, pWord,
      List.length_replicate, List.length_map, FusionLogCompression.pdWord_length,
      List.length_cons, List.length_nil, he]
    omega

/-- The same guarded fusion primitive works inside any terminal root,
without restoring the global cursor phase after each event. -/
theorem UpperReservedReplay.forest_fusion_word
    (hn : 1 < n) {P : Placement n} {cursor : Fin n} {k : Nat}
    {A B : UpperFusionTree n} {tail terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k (A :: B :: tail) terminal (forestLeaves terminal) site)
    (frame : ReservationFrame k (.merge A B :: tail) terminal (forestLeaves terminal) site) :
    ∃ Q, let f := A.leaves.length - 1
      let word := phaseFreeFusionWord true
        (((site A.firstLeaf).val : ZMod n) - (cursor.val : ZMod n))
        (((site B.firstLeaf).val : ZMod n) - (cursor.val : ZMod n)) f
      runLogged n hn P word = some (Q, [.fusion true A.packet B.packet (A.packet ∪ B.packet)]) ∧
      UpperReservedReplay Q (site A.firstLeaf) k (.merge A B :: tail)
        terminal (forestLeaves terminal) site ∧
      word.length = cursorTurn n cursor.val ((site A.firstLeaf).val + f) + 2*f + 1 := by
  have hnat := h.frame.forest_ordered_merge_anchor_gap frame
  let a : ZMod n := (site A.firstLeaf).val
  let b : ZMod n := (site B.firstLeaf).val
  let c : ZMod n := cursor.val
  let f := A.leaves.length - 1
  let N := phaseShift P true c
  have hsize := A.leaves_length_pos
  have hfn : f ≤ n-2 := by have := (site B.firstLeaf).isLt; dsimp [f]; omega
  have hab : b = a + 1 + (f : ZMod n) := by
    dsimp only [a, b]
    rw [hnat, Nat.cast_add]
    have he : (A.leaves.length : ZMod n) = 1 + (f : ZMod n) := by
      have hp := congrArg (fun x : Nat => (x : ZMod n))
        (show A.leaves.length = 1 + f by dsimp [f]; omega)
      simpa only [Nat.cast_add, Nat.cast_one] using hp
    rw [he]
    ring
  have hA : packetAt N true (zsite a) = A.packet := by
    simpa [N, a] using ReservedState.packet_at_anchor h (tree := A) (by simp)
  have hB : packetAt N true (zsite b) = B.packet := by
    simpa [N, b] using ReservedState.packet_at_anchor h (tree := B) (by simp)
  obtain ⟨g, hgn, hggap, hgholes⟩ := cyclic_parents_gap hn N true a b A.packet B.packet
    (forestPackets tail) hA hB (h.packet_nonempty A (by simp))
    (h.packet_nonempty B (by simp))
    (by simpa [forestPackets] using (ReservedState.current_packet_cycle h).symm)
  have hgf : g = f := by
    have he : (g : ZMod n) = (f : ZMod n) := by
      apply add_left_cancel (a := a+1)
      exact hggap.symm.trans hab
    have hv := congrArg ZMod.val he
    simpa [ZMod.val_natCast_of_lt (show g < n by omega),
      ZMod.val_natCast_of_lt (show f < n by omega)] using hv
  subst g
  have hholes : ∀ j : Nat, 1 ≤ j → j ≤ f → packetAt P true (zsite (b-c-j)) = ∅ := by
    intro j hj hjf
    have he := hgholes j hj hjf
    change packetAt (phaseShift P true c) true (zsite (b-j)) = ∅ at he
    rw [packetAt_phaseShift] at he
    rw [show b-c-(j : ZMod n) = b-j-c by ring]
    exact he
  have hAp : packetAt P true (zsite (a-c)) = A.packet := h.packet_at_anchor (by simp)
  have hBp : packetAt P true (zsite (b-c)) = B.packet := h.packet_at_anchor (by simp)
  have hrun := phaseFreeFusionWord_spec hn P true (a-c) (b-c) f hfn
    (by rw [hab]; ring) (hAp.symm ▸ h.packet_nonempty A (by simp))
    (hBp.symm ▸ h.packet_nonempty B (by simp)) hholes
  let Q := phaseShift (relocateAt P true (b-c) (a-c)) true (-(a-c))
  have hnorm : phaseShift Q true a = relocateAt N true b a := by
    change phaseShift (phaseShift _ true (-(a-c))) true a = _
    rw [phaseShift_add, show -(a-c)+a = c by ring, phaseShift_relocate_upper]
    simp only [sub_add_cancel]
    rfl
  refine ⟨Q, ?_, ?_, ?_⟩
  · simpa only [hAp, hBp] using hrun
  · change ReservedState (phaseShift Q true a) _ _ _ _ _
    rw [hnorm]
    exact ReservedState.mergeAt h frame
  · exact fusion_length cursor (site A.firstLeaf) (site B.firstLeaf) f (by dsimp [f]; omega)

theorem UpperReservedReplay.forest_packet_cycle
    (hn : 1 < n) {P : Placement n} {cursor : Fin n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor k forest terminal omega site) :
    (forestPackets forest).IsRotated (cyclicSignature P true) := by
  have phase := runLogged_empty_signatures n hn _
    (runLogged_phase hn P true (cursor.val : ZMod n))
  exact state.current_packet_cycle.trans (phase true).symm

end Physical

theorem cyclicSignature_lower_of_empty {n : Nat} {P : Placement n}
    (empty : lowerConfiguration P = lowerExtractionEmpty n) :
    cyclicSignature P false = [] := by
  have hp : ∀ q : Fin n, packetAt P false q = ∅ := by
    intro q
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro a ha
    rw [mem_packetAt, ← lowerConfiguration_eq_some, empty] at ha
    simp [lowerExtractionEmpty] at ha
  simp [cyclicSignature, layerSlots, hp, stripEmpty]

/-- One joint silent route restores every root's prescribed physical site.
The bound depends on the total terminal rank, not a sum of root phases. -/
theorem UpperReservedReplay.joint_terminal_route
    {n : Nat} [NeZero n] (hn : 1 < n) {P Q : Placement n} {cursor : Fin n} {k : Nat}
    {terminal : List (UpperFusionTree n)} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor k terminal terminal (forestLeaves terminal) site)
    (lowerP : lowerConfiguration P = lowerExtractionEmpty n)
    (lowerQ : lowerConfiguration Q = lowerExtractionEmpty n)
    (cycle : (forestPackets terminal).IsRotated (cyclicSignature Q true)) :
    ∃ word, SameCyclicSignatures P Q ∧ runLogged n hn P word = some (Q,[]) ∧
      word.length ≤ layerBudget n terminal.length := by
  have current := state.forest_packet_cycle hn
  have same : SameCyclicSignatures P Q := by
    intro layer
    cases layer with
    | false => rw [cyclicSignature_lower_of_empty lowerP, cyclicSignature_lower_of_empty lowerQ]
    | true => exact current.symm.trans cycle
  obtain ⟨word, hw, hlen⟩ := silent_preparation_short n hn P Q same
  have h0 : layerRank P false = 0 := by
    rw [layerRank, cyclicSignature_lower_of_empty lowerP]
    rfl
  have h1 : layerRank P true = terminal.length := by
    simpa [layerRank, forestPackets] using current.perm.length_eq.symm
  refine ⟨word, same, hw, ?_⟩
  simpa only [silentBudget, h0, h1, show layerBudget n 0 = 0 from rfl, Nat.zero_add] using hlen

end RSR2History
