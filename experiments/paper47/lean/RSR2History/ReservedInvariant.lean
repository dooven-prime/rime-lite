import RSR2History.OrderedForestCompatibility
import RSR2History.ReservedEventPrimitives

/-!
Physical reservations use the first transfer leaf of each ordered tree as
its permanent anchor. `ReservationFrame` contains only combinatorial and
coordinate data, with no execution or cost premise. `ReservedState` adds
exact atom ownership at those anchors, including absence of extra packets.
In particular, future vacancy is a theorem, not a premise of event replay.
-/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

def UpperFusionTree.firstLeaf : UpperFusionTree n → Nat
  | .leaf occurrence _ => occurrence
  | .merge left _ => left.firstLeaf

theorem UpperFusionTree.firstLeaf_mem (tree : UpperFusionTree n) :
    tree.firstLeaf ∈ tree.leaves := by
  induction tree with
  | leaf => simp [firstLeaf, leaves]
  | merge A B ihA _ => simp [firstLeaf, leaves, ihA]

/-- Explicit bounded leaf embedding; unused natural labels map to site zero. -/
def reservationSite (hn : 0 < n) (omega : List Nat) (hlen : omega.length ≤ n)
    (a : Nat) : Fin n :=
  if ha : a ∈ omega then ⟨omega.idxOf a, (List.idxOf_lt_length_iff.mpr ha).trans_le hlen⟩
  else ⟨0, hn⟩

theorem reservationSite_index (hn : 0 < n) (omega : List Nat) (hlen : omega.length ≤ n)
    (a : Nat) (ha : a ∈ omega) :
    (reservationSite hn omega hlen a).val = omega.idxOf a := by
  simp [reservationSite, ha]

theorem reservationSite_injective (hn : 0 < n) (omega : List Nat) (hlen : omega.length ≤ n)
    {a b : Nat} (ha : a ∈ omega) (hb : b ∈ omega)
    (he : reservationSite hn omega hlen a = reservationSite hn omega hlen b) : a = b := by
  apply (List.idxOf_inj ha).mp
  have hv := congrArg Fin.val he
  simpa [reservationSite, ha, hb] using hv

structure ReservationFrame (k : Nat) (forest terminal : List (UpperFusionTree n))
    (omega : List Nat) (site : Nat → Fin n) : Prop where
  complete : (forestLeaves forest).Perm (List.range k)
  terminal_order : (forestLeaves terminal).IsRotated omega
  omega_nodup : omega.Nodup
  subtrees : ∀ tree ∈ forest, ∃ root ∈ terminal, tree.Subtree root
  prefix_order : (forestLeaves forest).IsRotated (omega.filter (fun a => a < k))
  site_injective : ∀ {a b}, a ∈ omega → b ∈ omega → site a = site b → a = b
  site_index : ∀ a ∈ omega, (site a).val = omega.idxOf a

/-- All order/interval obligations come from the already proved future forest
path. The only new input here is the chosen finite physical leaf embedding. -/
theorem ReservationFrame.of_path
    {k k' : Nat} {forest terminal : List (UpperFusionTree n)}
    {events : List (EffectiveEvent n)} {omega : List Nat} {site : Nat → Fin n}
    (path : UpperForestPath k forest events k' terminal)
    (complete : (forestLeaves forest).Perm (List.range k))
    (horder : (forestLeaves terminal).IsRotated omega)
    (hinj : ∀ {a b}, a ∈ omega → b ∈ omega → site a = site b → a = b)
    (hindex : ∀ a ∈ omega, (site a).val = omega.idxOf a) :
    ReservationFrame k forest terminal omega site := by
  refine ⟨complete, horder, ?_, fun tree ht => path.retains_tree ht, ?_, hinj, hindex⟩
  · exact horder.nodup_iff.mp ((path.complete_leaves complete).nodup_iff.mpr List.nodup_range)
  · exact (path.prefix_compatibility complete).symm.trans (cyclic_filter horder _)

theorem ReservationFrame.leaf_in_omega
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site) {a : Nat}
    (ha : a ∈ forestLeaves forest) : a ∈ omega := by
  exact (List.mem_filter.mp (h.prefix_order.perm.mem_iff.mp ha)).1

theorem ReservationFrame.firstLeaf_lt
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site)
    {tree : UpperFusionTree n} (ht : tree ∈ forest) : tree.firstLeaf < k := by
  apply List.mem_range.mp
  apply h.complete.mem_iff.mp
  exact List.mem_flatMap.mpr ⟨tree, ht, tree.firstLeaf_mem⟩

theorem ReservationFrame.firstLeaf_in_omega
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site)
    {tree : UpperFusionTree n} (ht : tree ∈ forest) : tree.firstLeaf ∈ omega :=
  h.leaf_in_omega (List.mem_flatMap.mpr ⟨tree, ht, tree.firstLeaf_mem⟩)

theorem ReservationFrame.anchors_pairwise
    {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site) :
    forest.Pairwise (fun A B => site A.firstLeaf ≠ site B.firstLeaf) := by
  have hnd : (forestLeaves forest).Nodup := h.complete.nodup_iff.mpr List.nodup_range
  have hp := (List.nodup_flatMap.mp hnd).2
  apply hp.imp_of_mem
  intro A B hA hB hd he
  have hi := h.site_injective (h.firstLeaf_in_omega hA) (h.firstLeaf_in_omega hB) he
  exact List.disjoint_left.mp hd A.firstLeaf_mem (hi ▸ B.firstLeaf_mem)

structure ReservedState (P : Placement n) (k : Nat)
    (forest terminal : List (UpperFusionTree n))
    (omega : List Nat) (site : Nat → Fin n) : Prop where
  frame : ReservationFrame k forest terminal omega site
  packet_nonempty : ∀ tree ∈ forest, tree.packet.Nonempty
  upper_position : ∀ (a : Fin n) (q : Fin n), P a = (true, q) ↔
    ∃ tree ∈ forest, a ∈ tree.packet ∧ q = site tree.firstLeaf

theorem ReservedState.empty
    {P : Placement n} {terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (frame : ReservationFrame 0 [] terminal omega site)
    (hempty : ∀ a : Fin n, (P a).1 = false) :
    ReservedState P 0 [] terminal omega site := by
  refine ⟨frame, by simp, ?_⟩
  intro a q
  have hno : P a ≠ (true, q) := by
    intro he
    have := (congrArg Prod.fst he).symm.trans (hempty a)
    contradiction
  simp [hno]

theorem reserved_seed_of_forestPath
    (hn : 0 < n) {kfinal : Nat} {terminal : List (UpperFusionTree n)}
    {events : List (EffectiveEvent n)}
    (path : UpperForestPath 0 [] events kfinal terminal)
    (hlen : (forestLeaves terminal).length ≤ n) :
    ReservedState (seed n) 0 [] terminal (forestLeaves terminal)
      (reservationSite hn (forestLeaves terminal) hlen) := by
  apply ReservedState.empty
  · apply ReservationFrame.of_path path (by simp [forestLeaves]) (.refl _)
    · exact reservationSite_injective hn _ hlen
    · exact reservationSite_index hn _ hlen
  · intro a
    rfl

theorem ReservedState.packet_at_anchor
    {P : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site)
    {tree : UpperFusionTree n} (ht : tree ∈ forest) :
    packetAt P true (site tree.firstLeaf) = tree.packet := by
  ext a
  rw [mem_packetAt, h.upper_position]
  have : Std.Symm (fun A B : UpperFusionTree n => site A.firstLeaf ≠ site B.firstLeaf) :=
    ⟨fun _ _ he => he.symm⟩
  constructor
  · rintro ⟨other, ho, ha, he⟩
    by_cases hot : other = tree
    · simpa [hot] using ha
    · exact False.elim ((h.frame.anchors_pairwise.forall ho ht hot) he.symm)
  · intro ha
    exact ⟨tree, ht, ha, rfl⟩

/-- No upper packet can occupy a not-yet-transferred leaf reservation. -/
theorem ReservedState.future_site_empty
    {P : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site)
    {a : Nat} (ha : k ≤ a) (haomega : a ∈ omega) :
    packetAt P true (site a) = ∅ := by
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro atom hm
  obtain ⟨tree, ht, _, he⟩ := (h.upper_position atom (site a)).mp
    ((mem_packetAt _ _ _ _).mp hm)
  have hid := h.frame.site_injective haomega (h.frame.firstLeaf_in_omega ht) he
  have := h.frame.firstLeaf_lt ht
  omega

/-- In a fixed forest, the relation determines all upper physical coordinates. -/
theorem ReservedState.upper_unique
    {P Q : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (hP : ReservedState P k forest terminal omega site)
    (hQ : ReservedState Q k forest terminal omega site) :
    layerSlots P true = layerSlots Q true := by
  unfold layerSlots
  congr 1
  funext q
  ext a
  simp only [mem_packetAt, hP.upper_position, hQ.upper_position]

/-- Rotation changes the representation of a forest, not its physical
reservations. The supplied frame contains purely combinatorial data. -/
theorem ReservedState.reframe
    {P : Placement n} {k : Nat} {forest next terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site)
    (same : forest.Perm next) (frame : ReservationFrame k next terminal omega site) :
    ReservedState P k next terminal omega site := by
  refine ⟨frame, ?_, ?_⟩
  · intro tree ht
    exact h.packet_nonempty tree (same.mem_iff.mpr ht)
  · intro a q
    rw [h.upper_position]
    constructor <;> rintro ⟨tree, ht, ha, hq⟩
    · exact ⟨tree, same.mem_iff.mp ht, ha, hq⟩
    · exact ⟨tree, same.mem_iff.mpr ht, ha, hq⟩

section EventPreservation
variable [NeZero n]

theorem transferAt_upper_position (P : Placement n) (source target : ZMod n)
    (a : Fin n) (q : Fin n) :
    transferAt P source target a = (true, q) ↔
      (P a = (false, zsite source) ∧ q = zsite target) ∨ P a = (true, q) := by
  by_cases hs : P a = (false, zsite source)
  · simp [transferAt, hs, eq_comm]
  · simp [transferAt, hs]

/-- Exact physical layout is preserved by transfer into the fresh leaf site.
The target frame is an order certificate, with no target execution or
physical-placement hypothesis. -/
theorem ReservedState.transferAt
    {P : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) (source : ZMod n)
    (hsource : (packetAt P false (zsite source)).Nonempty)
    (frame : ReservationFrame (k+1)
      (.leaf k (packetAt P false (zsite source)) :: forest) terminal omega site) :
    ReservedState (RSR2History.transferAt P source ((site k).val : ZMod n)) (k+1)
      (.leaf k (packetAt P false (zsite source)) :: forest) terminal omega site := by
  refine ⟨frame, ?_, ?_⟩
  · intro tree ht
    rcases List.mem_cons.mp ht with rfl | ht
    · exact hsource
    · exact h.packet_nonempty tree ht
  · intro a q
    rw [transferAt_upper_position, h.upper_position]
    simp only [zsite_cast, List.mem_cons]
    constructor
    · rintro (⟨ha, hq⟩ | ⟨tree, ht, ha, hq⟩)
      · exact ⟨.leaf k (packetAt P false (zsite source)), Or.inl rfl,
          (mem_packetAt _ _ _ _).mpr ha, hq⟩
      · exact ⟨tree, Or.inr ht, ha, hq⟩
    · rintro ⟨tree, (rfl | ht), ha, hq⟩
      · exact Or.inl ⟨(mem_packetAt _ _ _ _).mp ha, hq⟩
      · exact Or.inr ⟨tree, ht, ha, hq⟩

theorem ReservedState.transfer_word
    (hn : 1 < n) {P : Placement n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) (source : ZMod n)
    (hsource : (packetAt P false (zsite source)).Nonempty)
    (frame : ReservationFrame (k+1)
      (.leaf k (packetAt P false (zsite source)) :: forest) terminal omega site) :
    ∃ Q word, runLogged n hn P word =
      some (Q, [.transfer (packetAt P false (zsite source))]) ∧
      ReservedState Q (k+1) (.leaf k (packetAt P false (zsite source)) :: forest)
        terminal omega site ∧ word.length ≤ 2*n+1 := by
  have hk : k ∈ omega := frame.firstLeaf_in_omega
    (tree := .leaf k (packetAt P false (zsite source))) (by simp)
  have hempty : packetAt P true (zsite ((site k).val : ZMod n)) = ∅ := by
    simpa using h.future_site_empty (Nat.le_refl k) hk
  obtain ⟨hrun, hlen⟩ := reservedTransferWord_spec hn P source ((site k).val : ZMod n)
    hsource hempty
  exact ⟨_, _, hrun, h.transferAt source hsource frame, hlen⟩

theorem ReservedState.mergeAt
    {P : Placement n} {k : Nat} {A B : UpperFusionTree n}
    {tail terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k (A :: B :: tail) terminal omega site)
    (frame : ReservationFrame k (.merge A B :: tail) terminal omega site) :
    ReservedState (relocateAt P true ((site B.firstLeaf).val : ZMod n)
      ((site A.firstLeaf).val : ZMod n)) k (.merge A B :: tail) terminal omega site := by
  have hp := h.frame.anchors_pairwise
  have hAB : site A.firstLeaf ≠ site B.firstLeaf := (List.pairwise_cons.mp hp).1 B (by simp)
  have hBT : ∀ tree ∈ tail, site B.firstLeaf ≠ site tree.firstLeaf :=
    (List.pairwise_cons.mp (List.pairwise_cons.mp hp).2).1
  have hB := h.packet_at_anchor (tree := B) (by simp)
  refine ⟨frame, ?_, ?_⟩
  · intro tree ht
    rcases List.mem_cons.mp ht with rfl | ht
    · exact (h.packet_nonempty A (by simp)).mono Finset.subset_union_left
    · exact h.packet_nonempty tree (by simp [ht])
  · intro a q
    by_cases hm : a ∈ B.packet
    · have ha : P a = (true, site B.firstLeaf) :=
        (mem_packetAt _ _ _ _).mp (hB.symm ▸ hm)
      have htail : ∀ tree ∈ tail, a ∉ tree.packet := by
        intro tree ht hat
        have hat' : P a = (true, site tree.firstLeaf) :=
          (h.upper_position a _).mpr ⟨tree, by simp [ht], hat, rfl⟩
        exact hBT tree ht (congrArg Prod.snd (ha.symm.trans hat'))
      simp only [relocateAt, zsite_cast]
      rw [if_pos ha]
      simp only [Prod.mk.injEq, true_and]
      constructor
      · intro hq
        exact ⟨.merge A B, by simp, Finset.mem_union_right _ hm, hq.symm⟩
      · rintro ⟨tree, ht, hat, hq⟩
        rcases List.mem_cons.mp ht with rfl | ht
        · exact hq.symm
        · exact False.elim (htail tree ht hat)
    · have ha : P a ≠ (true, site B.firstLeaf) := by
        intro he
        exact hm (hB ▸ (mem_packetAt _ _ _ _).mpr he)
      simp only [relocateAt, zsite_cast]
      rw [if_neg ha, h.upper_position]
      simp only [List.mem_cons]
      constructor
      · rintro ⟨tree, (rfl | rfl | ht), hat, hq⟩
        · exact ⟨.merge tree B, Or.inl rfl, Finset.mem_union_left _ hat, hq⟩
        · exact False.elim (hm hat)
        · exact ⟨tree, Or.inr ht, hat, hq⟩
      · rintro ⟨tree, (rfl | ht), hat, hq⟩
        · exact ⟨A, Or.inl rfl, (Finset.mem_union.mp hat).resolve_right hm, hq⟩
        · exact ⟨tree, Or.inr (Or.inr ht), hat, hq⟩

theorem ReservedState.fusion_word_of_gap
    (hn : 1 < n) {P : Placement n} {k : Nat} {A B : UpperFusionTree n}
    {tail terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k (A :: B :: tail) terminal omega site)
    (frame : ReservationFrame k (.merge A B :: tail) terminal omega site)
    (f : Nat) (hfn : f ≤ n-2)
    (hgap : ((site B.firstLeaf).val : ZMod n) =
      ((site A.firstLeaf).val : ZMod n)+1+(f : ZMod n))
    (hholes : ∀ j : Nat, 1 ≤ j → j ≤ f →
      packetAt P true (zsite (((site B.firstLeaf).val : ZMod n)-j)) = ∅) :
    ∃ Q word, runLogged n hn P word =
      some (Q, [.fusion true A.packet B.packet (A.packet ∪ B.packet)]) ∧
      ReservedState Q k (.merge A B :: tail) terminal omega site ∧ word.length ≤ 4*n := by
  have hA : packetAt P true (zsite ((site A.firstLeaf).val : ZMod n)) = A.packet := by
    simpa using h.packet_at_anchor (tree := A) (by simp)
  have hB : packetAt P true (zsite ((site B.firstLeaf).val : ZMod n)) = B.packet := by
    simpa using h.packet_at_anchor (tree := B) (by simp)
  obtain ⟨hrun, hlen⟩ := reservedFusionWord_spec hn P true
    ((site A.firstLeaf).val : ZMod n) ((site B.firstLeaf).val : ZMod n) f hfn hgap
    (hA.symm ▸ h.packet_nonempty A (by simp)) (hB.symm ▸ h.packet_nonempty B (by simp)) hholes
  exact ⟨_, _, by simpa only [hA, hB] using hrun, h.mergeAt frame, hlen⟩

end EventPreservation

end RSR2History
