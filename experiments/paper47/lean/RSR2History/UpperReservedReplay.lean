import RSR2History.UpperCursorSlack
import RSR2History.ReservedGeometry
import RSR2History.PhaseFreeFusion

/-! Actual upper layouts with a retained cursor; no physical phase restoration. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

def UpperReservedReplay (P : Placement n) (cursor : Fin n) (k : Nat)
    (forest terminal : List (UpperFusionTree n)) (omega : List Nat)
    (site : Nat → Fin n) : Prop :=
  ReservedState (phaseShift P true (cursor.val : ZMod n)) k forest terminal omega site

theorem upperReserved_seed_of_forestPath
    (hn : 0 < n) {kfinal : Nat} {terminal : List (UpperFusionTree n)}
    {events : List (EffectiveEvent n)} (cursor : Fin n)
    (path : UpperForestPath 0 [] events kfinal terminal)
    (hlen : (forestLeaves terminal).length ≤ n) :
    UpperReservedReplay (seed n) cursor 0 [] terminal (forestLeaves terminal)
      (reservationSite hn (forestLeaves terminal) hlen) := by
  unfold UpperReservedReplay
  have he : phaseShift (seed n) true (cursor.val : ZMod n) = seed n := by
    funext a
    simp [seed, phaseShift]
  rw [he]
  exact reserved_seed_of_forestPath hn path hlen

theorem UpperReservedReplay.reframe
    {P : Placement n} {cursor : Fin n} {k : Nat}
    {forest next terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k forest terminal omega site)
    (same : forest.Perm next) (frame : ReservationFrame k next terminal omega site) :
    UpperReservedReplay P cursor k next terminal omega site :=
  ReservedState.reframe h same frame

theorem UpperReservedReplay.congr_upper
    {P Q : Placement n} {cursor : Fin n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k forest terminal omega site)
    (same : ∀ a q, Q a = (true, q) ↔ P a = (true, q)) :
    UpperReservedReplay Q cursor k forest terminal omega site := by
  refine ⟨h.frame, h.packet_nonempty, ?_⟩
  intro atom q
  have he (R : Placement n) :
      phaseShift R true (cursor.val : ZMod n) atom = (true, q) ↔
        R atom = (true, zsite ((q.val : ZMod n) - (cursor.val : ZMod n))) := by
    rw [← mem_packetAt, ← zsite_cast q, packetAt_phaseShift, mem_packetAt]
    simp
  exact (he Q).trans ((same _ _).trans ((he P).symm.trans (h.upper_position atom q)))

theorem UpperReservedReplay.packet_at_anchor
    {P : Placement n} {cursor : Fin n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k forest terminal omega site)
    {tree : UpperFusionTree n} (ht : tree ∈ forest) :
    packetAt P true (zsite ((site tree.firstLeaf).val - (cursor.val : ZMod n))) = tree.packet := by
  have he := ReservedState.packet_at_anchor h ht
  rw [← zsite_cast (site tree.firstLeaf), packetAt_phaseShift] at he
  exact he

theorem UpperReservedReplay.future_site_empty
    {P : Placement n} {cursor : Fin n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k forest terminal omega site)
    {i : Nat} (hi : k ≤ i) (hiomega : i ∈ omega) :
    packetAt P true (zsite ((site i).val - (cursor.val : ZMod n))) = ∅ := by
  have he := ReservedState.future_site_empty h hi hiomega
  rw [← zsite_cast (site i), packetAt_phaseShift] at he
  exact he

theorem phaseShift_relocate_upper (P : Placement n) (source target c : ZMod n) :
    phaseShift (relocateAt P true source target) true c =
      relocateAt (phaseShift P true c) true (source + c) (target + c) := by
  funext atom
  by_cases hs : P atom = (true, zsite source)
  · simp [relocateAt, phaseShift, hs]
  · have hne : phaseShift P true c atom ≠ (true, zsite (source + c)) := by
      intro he
      by_cases hu : (P atom).1 = true
      · simp only [phaseShift, if_pos hu, Prod.mk.injEq, true_and, zsite_inj] at he
        have hval : ((P atom).2.val : ZMod n) = source := add_right_cancel he
        apply hs
        exact Prod.ext hu (by simpa using congrArg zsite hval)
      · have hp : P atom ≠ (true, zsite (source + c)) := fun h => hu (congrArg Prod.fst h)
        exact hp (by simpa [phaseShift, hu] using he)
    calc
      phaseShift (relocateAt P true source target) true c atom = phaseShift P true c atom := by
        unfold phaseShift
        rw [show relocateAt P true source target atom = P atom by simp [relocateAt, hs]]
      _ = relocateAt (phaseShift P true c) true (source+c) (target+c) atom :=
        (if_neg hne).symm

def cursorTransferWord (cursor target : Fin n) : List Letter :=
  pWord true ((cursor.val : ZMod n) - target.val).val ++ [.v]

/-- Lower preparation has already placed the named packet at lower port zero. -/
theorem UpperReservedReplay.transfer_word
    (hn : 1 < n) {P : Placement n} {cursor : Fin n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k forest terminal omega site)
    (hsource : (packetAt P false (site0 n (by omega))).Nonempty)
    (frame : ReservationFrame (k+1)
      (.leaf k (packetAt P false (site0 n (by omega))) :: forest) terminal omega site) :
    ∃ Q, runLogged n hn P (cursorTransferWord cursor (site k)) =
      some (Q, [.transfer (packetAt P false (site0 n (by omega)))]) ∧
      UpperReservedReplay Q (site k) (k+1)
        (.leaf k (packetAt P false (site0 n (by omega))) :: forest) terminal omega site ∧
      (cursorTransferWord cursor (site k)).length = cursorTurn n cursor.val (site k).val + 1 := by
  let c : ZMod n := cursor.val
  let j : ZMod n := (site k).val
  let R := phaseShift P true (c-j)
  have hlo : packetAt R false (site0 n (by omega)) = packetAt P false (site0 n (by omega)) :=
    packetAt_phaseShift_other P true false (by decide) (c-j) _
  have hk : k ∈ omega := frame.firstLeaf_in_omega
    (tree := .leaf k (packetAt P false (site0 n (by omega)))) (by simp)
  have hempty : packetAt R true (site0 n (by omega)) = ∅ := by
    rw [← zsite_zero, packetAt_phaseShift]
    have hz : (0 : ZMod n) - (c-j) = j-c := by ring
    rw [hz]
    exact h.future_site_empty (Nat.le_refl k) hk
  have hg : liftGuard n (by omega) R := by
    constructor
    · exact (packetAt_nonempty _ _ _).mp (hlo.symm ▸ hsource)
    · intro ho
      have he := (packetAt_nonempty R true (site0 n (by omega))).mpr ho
      simp [hempty] at he
  have hv : step n hn R .v = some (liftPacket n (by omega) R) := by simp [step, hg]
  have heq : phaseShift (liftPacket n (by omega) R) true j =
      transferAt (phaseShift P true c) 0 j := by
    simpa [phaseShift_zero, phaseShift_add, sub_eq_add_neg, R] using
      transfer_phase_restored (phaseShift P true c) 0 j
  have hsource' : packetAt (phaseShift P true c) false (zsite 0) =
      packetAt P false (site0 n (by omega)) := by
    rw [packetAt_phaseShift_other _ _ _ (by decide), zsite_zero]
  dsimp only [c] at hsource'
  refine ⟨liftPacket n (by omega) R, ?_, ?_, ?_⟩
  · have hpre : runLogged n hn P (pWord true (c-j).val) = some (R, []) :=
      runLogged_phase hn P true (c-j)
    change runLogged n hn P (pWord true (c-j).val ++ [.v]) = _
    rw [runLogged_append, hpre]
    simp [runLogged, hv, emittedEvents, hlo]
  · change ReservedState (phaseShift (liftPacket n (by omega) R) true j) _ _ _ _ _
    rw [heq]
    have hframe := frame
    rw [← hsource'] at hframe
    have ht := ReservedState.transferAt h 0 (hsource'.symm ▸ hsource) hframe
    simpa only [hsource'] using ht
  · simp only [cursorTransferWord, List.length_append, pWord, List.length_replicate,
      List.length_singleton]
    rw [cursorTurn_eq_zmod_val cursor.isLt (site k).isLt]

private theorem cursor_fusion_length (cursor left right : Fin n) (f : Nat)
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

/-- Future compatibility supplies the holes and the exact debt, not a budget premise. -/
theorem UpperReservedReplay.fusion_word
    (hn : 1 < n) {P : Placement n} {cursor : Fin n} {k : Nat}
    {A B T : UpperFusionTree n} {tail : List (UpperFusionTree n)} {site : Nat → Fin n}
    (h : UpperReservedReplay P cursor k (A :: B :: tail) [T] T.leaves site)
    (frame : ReservationFrame k (.merge A B :: tail) [T] T.leaves site) :
    ∃ Q, let f := A.leaves.length - 1
      let word := phaseFreeFusionWord true
        (((site A.firstLeaf).val : ZMod n) - (cursor.val : ZMod n))
        (((site B.firstLeaf).val : ZMod n) - (cursor.val : ZMod n)) f
      runLogged n hn P word = some (Q, [.fusion true A.packet B.packet (A.packet ∪ B.packet)]) ∧
      UpperReservedReplay Q (site A.firstLeaf) k (.merge A B :: tail) [T] T.leaves site ∧
      word.length = cursorTurn n cursor.val ((site A.firstLeaf).val + f) + 2*f + 1 := by
  obtain ⟨root, hr, hsub⟩ := frame.subtrees (.merge A B) (by simp)
  have hroot : root = T := by simpa using hr
  subst root
  have hAB := hsub.anchor_gap h.frame.omega_nodup
  have hnat : (site B.firstLeaf).val = (site A.firstLeaf).val + A.leaves.length := by
    simpa only [h.frame.site_index A.firstLeaf (h.frame.firstLeaf_in_omega (by simp)),
      h.frame.site_index B.firstLeaf (h.frame.firstLeaf_in_omega (by simp))] using hAB
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
  have hholes : ∀ j : Nat, 1 ≤ j → j ≤ f →
      packetAt P true (zsite (b-c-j)) = ∅ := by
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
  · exact cursor_fusion_length cursor (site A.firstLeaf) (site B.firstLeaf) f (by dsimp [f]; omega)

end RSR2History
