import RSR2History.CyclicEventPath

/-!
Cost-free ordered upper fusion forests. Transfer occurrences, not atoms,
are leaves. The cyclic relations below have no physical-site or length
premises. Actual typed event paths admit annotations by these forests.
-/
namespace RSR2History
open RSR2.Parametric

inductive UpperFusionTree (n : Nat) where
  | leaf (occurrence : Nat) (packet : Finset (Fin n))
  | merge (left right : UpperFusionTree n)
  deriving DecidableEq

def UpperFusionTree.packet : UpperFusionTree n → Finset (Fin n)
  | .leaf _ packet => packet
  | .merge left right => left.packet ∪ right.packet

def UpperFusionTree.leaves : UpperFusionTree n → List Nat
  | .leaf occurrence _ => [occurrence]
  | .merge left right => left.leaves ++ right.leaves

def forestLeaves (forest : List (UpperFusionTree n)) : List Nat :=
  forest.flatMap UpperFusionTree.leaves

def forestPackets (forest : List (UpperFusionTree n)) : List (Finset (Fin n)) :=
  forest.map UpperFusionTree.packet

inductive UpperFusionTree.Subtree : UpperFusionTree n → UpperFusionTree n → Prop
  | refl (tree) : Subtree tree tree
  | left {tree A B} (h : Subtree tree A) : Subtree tree (.merge A B)
  | right {tree A B} (h : Subtree tree B) : Subtree tree (.merge A B)

theorem UpperFusionTree.Subtree.trans {A B C : UpperFusionTree n}
    (hAB : A.Subtree B) (hBC : B.Subtree C) : A.Subtree C := by
  induction hBC with
  | refl => exact hAB
  | left _ ih => exact .left ih
  | right _ ih => exact .right ih

/-- Subtree leaves occupy an actual interval, not just a subset of leaves. -/
theorem UpperFusionTree.Subtree.leaf_interval {A B : UpperFusionTree n}
    (h : A.Subtree B) : ∃ left right, B.leaves = left ++ A.leaves ++ right := by
  induction h with
  | refl => exact ⟨[], [], by simp⟩
  | @left A B _ ih =>
      obtain ⟨left, right, he⟩ := ih
      exact ⟨left, right ++ B.leaves, by simp [UpperFusionTree.leaves, he, List.append_assoc]⟩
  | @right A B _ ih =>
      obtain ⟨left, right, he⟩ := ih
      exact ⟨A.leaves ++ left, right, by simp [UpperFusionTree.leaves, he, List.append_assoc]⟩

/-- Expanding named cyclic blocks preserves rotation equivalence, even when
the blocks have different lengths. -/
theorem cyclic_flatMap {α β : Type*} {xs ys : List α}
    (h : xs.IsRotated ys) (f : α → List β) :
    (xs.flatMap f).IsRotated (ys.flatMap f) := by
  obtain ⟨k, hk⟩ := h
  rw [List.rotate_eq_drop_append_take_mod] at hk
  rw [← hk, List.flatMap_append]
  have hs : xs = xs.take (k % xs.length) ++ xs.drop (k % xs.length) :=
    (List.take_append_drop _ _).symm
  conv_lhs => rw [hs, List.flatMap_append]
  exact List.isRotated_append

theorem cyclic_filter {α : Type*} {xs ys : List α}
    (h : xs.IsRotated ys) (p : α → Bool) :
    (xs.filter p).IsRotated (ys.filter p) := by
  obtain ⟨k, hk⟩ := h
  rw [List.rotate_eq_drop_append_take_mod] at hk
  rw [← hk, List.filter_append]
  have hs : xs = xs.take (k % xs.length) ++ xs.drop (k % xs.length) :=
    (List.take_append_drop _ _).symm
  conv_lhs => rw [hs, List.filter_append]
  exact List.isRotated_append

/-- Physical frames can be rotated without changing the ordered trees. -/
theorem forest_rotation_lift (forest : List (UpperFusionTree n))
    (packets : List (Finset (Fin n)))
    (h : (forestPackets forest).IsRotated packets) :
    ∃ rotated, forest.IsRotated rotated ∧ forestPackets rotated = packets := by
  obtain ⟨k, hk⟩ := h
  exact ⟨forest.rotate k, ⟨k, rfl⟩, by simpa [forestPackets, List.map_rotate] using hk⟩

/-- One observable event on an ordered forest. The last two trees may be
fused in either cyclic binding; their order is fixed by the event tuple. -/
inductive UpperForestStep : Nat → List (UpperFusionTree n) → EffectiveEvent n →
    Nat → List (UpperFusionTree n) → Prop
  | lower {k xs ys} (A B : Finset (Fin n)) (same : xs.IsRotated ys) :
      UpperForestStep k xs (.fusion false A B (A ∪ B)) k ys
  | fusion {k xs ys} (A B : UpperFusionTree n) (tail : List (UpperFusionTree n))
      (before : xs.IsRotated (A :: B :: tail))
      (after : ys.IsRotated (.merge A B :: tail)) :
      UpperForestStep k xs (.fusion true A.packet B.packet (A.packet ∪ B.packet)) k ys
  | transfer {k xs ys} (packet : Finset (Fin n)) (tail : List (UpperFusionTree n))
      (before : xs.IsRotated tail)
      (after : ys.IsRotated (.leaf k packet :: tail)) :
      UpperForestStep k xs (.transfer packet) (k+1) ys

inductive UpperForestPath : Nat → List (UpperFusionTree n) → List (EffectiveEvent n) →
    Nat → List (UpperFusionTree n) → Prop
  | nil {k xs ys} (same : xs.IsRotated ys) : UpperForestPath k xs [] k ys
  | cons {k k' k'' xs ys zs event events}
      (head : UpperForestStep k xs event k' ys)
      (tail : UpperForestPath k' ys events k'' zs) :
      UpperForestPath k xs (event :: events) k'' zs

theorem UpperForestStep.next_mono {k k' : Nat} {xs ys : List (UpperFusionTree n)}
    {event} (h : UpperForestStep k xs event k' ys) : k ≤ k' := by
  cases h <;> omega

/-- Erasing future transfer leaves commutes with every event. In particular,
an upper merge preserves the complete ordered expansion, not just its set. -/
theorem UpperForestStep.filtered_leaves {k k' cut : Nat}
    {xs ys : List (UpperFusionTree n)} {event}
    (h : UpperForestStep k xs event k' ys) (hc : cut ≤ k) :
    ((forestLeaves xs).filter (fun a => a < cut)).IsRotated
      ((forestLeaves ys).filter (fun a => a < cut)) := by
  cases h with
  | lower A B same => exact cyclic_filter (cyclic_flatMap same _) _
  | fusion A B tail before after =>
      have hb := cyclic_filter (cyclic_flatMap before UpperFusionTree.leaves) (fun a => a < cut)
      have ha := cyclic_filter (cyclic_flatMap after UpperFusionTree.leaves) (fun a => a < cut)
      exact hb.trans (by simpa [forestLeaves, UpperFusionTree.leaves] using ha.symm)
  | transfer packet tail before after =>
      have hb := cyclic_filter (cyclic_flatMap before UpperFusionTree.leaves) (fun a => a < cut)
      have ha := cyclic_filter (cyclic_flatMap after UpperFusionTree.leaves) (fun a => a < cut)
      exact hb.trans (by simpa [forestLeaves, UpperFusionTree.leaves,
        show ¬ k < cut by omega] using ha.symm)

theorem UpperForestPath.filtered_leaves {k k' cut : Nat}
    {xs ys : List (UpperFusionTree n)} {events}
    (h : UpperForestPath k xs events k' ys) (hc : cut ≤ k) :
    ((forestLeaves xs).filter (fun a => a < cut)).IsRotated
      ((forestLeaves ys).filter (fun a => a < cut)) := by
  induction h with
  | nil same => exact cyclic_filter (cyclic_flatMap same _) _
  | cons head tail ih => exact (head.filtered_leaves hc).trans (ih (hc.trans head.next_mono))

theorem UpperForestStep.complete_leaves {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {event}
    (h : UpperForestStep k xs event k' ys)
    (complete : (forestLeaves xs).Perm (List.range k)) :
    (forestLeaves ys).Perm (List.range k') := by
  cases h with
  | lower A B same => exact (cyclic_flatMap same _).perm.symm.trans complete
  | fusion A B tail before after =>
      have hb := (cyclic_flatMap before UpperFusionTree.leaves).perm.symm.trans complete
      exact (cyclic_flatMap after UpperFusionTree.leaves).perm.trans
        (by simpa [forestLeaves, UpperFusionTree.leaves] using hb)
  | transfer packet tail before after =>
      have hb := (cyclic_flatMap before UpperFusionTree.leaves).perm.symm.trans complete
      have hc := List.Perm.cons k hb
      have hr : (k :: List.range k).Perm (List.range (k+1)) := by
        rw [List.range_succ]
        exact (List.isRotated_append (l := [k]) (l' := List.range k)).perm
      have hc' : forestLeaves (.leaf k packet :: tail) |>.Perm (k :: List.range k) := by
        simpa [forestLeaves, UpperFusionTree.leaves] using hc
      exact (cyclic_flatMap after UpperFusionTree.leaves).perm.trans (hc'.trans hr)

theorem UpperForestPath.complete_leaves {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {events}
    (h : UpperForestPath k xs events k' ys)
    (complete : (forestLeaves xs).Perm (List.range k)) :
    (forestLeaves ys).Perm (List.range k') := by
  induction h with
  | nil same => exact (cyclic_flatMap same _).perm.symm.trans complete
  | cons head tail ih => exact ih (head.complete_leaves complete)

/-- Every current tree survives as a subtree of one terminal root. -/
theorem UpperForestStep.retains_tree {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {event}
    (h : UpperForestStep k xs event k' ys) {tree} (ht : tree ∈ xs) :
    ∃ root ∈ ys, tree.Subtree root := by
  cases h with
  | lower A B same => exact ⟨tree, same.perm.mem_iff.mp ht, .refl _⟩
  | fusion A B tail before after =>
      have hm := before.perm.mem_iff.mp ht
      simp only [List.mem_cons] at hm
      rcases hm with rfl | rfl | hm
      · exact ⟨.merge tree B, after.perm.mem_iff.mpr (by simp), .left (.refl _)⟩
      · exact ⟨.merge A tree, after.perm.mem_iff.mpr (by simp), .right (.refl _)⟩
      · exact ⟨tree, after.perm.mem_iff.mpr (by simp [hm]), .refl _⟩
  | transfer packet tail before after =>
      exact ⟨tree, after.perm.mem_iff.mpr (List.mem_cons_of_mem _
        (before.perm.mem_iff.mp ht)), .refl _⟩

theorem UpperForestPath.retains_tree {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {events}
    (h : UpperForestPath k xs events k' ys) {tree} (ht : tree ∈ xs) :
    ∃ root ∈ ys, tree.Subtree root := by
  induction h generalizing tree with
  | nil same => exact ⟨tree, same.perm.mem_iff.mp ht, .refl _⟩
  | cons head tail ih =>
      obtain ⟨mid, hm, hsub⟩ := head.retains_tree ht
      obtain ⟨root, hr, hsub'⟩ := ih hm
      exact ⟨root, hr, hsub.trans hsub'⟩

theorem UpperForestPath.tree_leaf_interval {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {events}
    (h : UpperForestPath k xs events k' ys) {tree} (ht : tree ∈ xs) :
    ∃ left right, forestLeaves ys = left ++ tree.leaves ++ right := by
  obtain ⟨root, hr, hsub⟩ := h.retains_tree ht
  obtain ⟨before, after, rfl⟩ := List.append_of_mem hr
  obtain ⟨left, right, he⟩ := hsub.leaf_interval
  exact ⟨forestLeaves before ++ left, right ++ forestLeaves after,
    by simp [forestLeaves, he, List.append_assoc]⟩

/-- The strong cyclic compatibility statement: the final leaf cycle,
restricted to transfer occurrences already present, is the current expanded
packet cycle up to rotation. This includes zero, one and two current packets. -/
theorem UpperForestPath.prefix_compatibility {k k' : Nat}
    {xs ys : List (UpperFusionTree n)} {events}
    (h : UpperForestPath k xs events k' ys)
    (complete : (forestLeaves xs).Perm (List.range k)) :
    ((forestLeaves ys).filter (fun a => a < k)).IsRotated (forestLeaves xs) := by
  have hall : (forestLeaves xs).filter (fun a => a < k) = forestLeaves xs := by
    apply List.filter_eq_self.mpr
    intro a ha
    simpa using List.mem_range.mp (complete.mem_iff.mp ha)
  simpa [hall] using (h.filtered_leaves (Nat.le_refl k)).symm

/-- A forest path synchronized with an actual typed cyclic event path.
The cycle matches at each boundary are proved from that path, not supplied as a
new assumption about future compatibility. No raw-length field occurs. -/
inductive UpperForestTrace : Placement n → Nat → List (UpperFusionTree n) →
    List (EffectiveEvent n) → Placement n → Nat → List (UpperFusionTree n) → Prop
  | nil {P Q k forest}
      (hmatch : (forestPackets forest).IsRotated (cyclicSignature P true))
      (same : SameCyclicSignatures P Q) : UpperForestTrace P k forest [] Q k forest
  | cons {P R Q k k' k'' xs ys zs event events}
      (hmatch : (forestPackets xs).IsRotated (cyclicSignature P true))
      (edge : CyclicEventEdge P event R)
      (update : UpperForestStep k xs event k' ys)
      (tail : UpperForestTrace R k' ys events Q k'' zs) :
      UpperForestTrace P k xs (event :: events) Q k'' zs

theorem UpperForestTrace.toPath {P Q : Placement n} {k k' xs ys events}
    (h : UpperForestTrace P k xs events Q k' ys) : UpperForestPath k xs events k' ys := by
  induction h with
  | nil => exact .nil (.refl _)
  | cons _ _ update _ ih => exact .cons update ih

theorem UpperForestTrace.source_cycle {P Q : Placement n} {k k' xs ys events}
    (h : UpperForestTrace P k xs events Q k' ys) :
    (forestPackets xs).IsRotated (cyclicSignature P true) := by
  cases h with
  | nil hmatch _ => exact hmatch
  | cons hmatch _ _ _ => exact hmatch

theorem UpperForestTrace.target_cycle {P Q : Placement n} {k k' xs ys events}
    (h : UpperForestTrace P k xs events Q k' ys) :
    (forestPackets ys).IsRotated (cyclicSignature Q true) := by
  induction h with
  | nil hmatch same => exact hmatch.trans (same true)
  | cons _ _ _ _ ih => exact ih

/-- Each actual cyclic event edge automatically lifts its current tree
annotation. Upper ordered parents are read from that exact event. -/
theorem CyclicEventEdge.upper_forest_step {P Q : Placement n} {event}
    (h : CyclicEventEdge P event Q) (k : Nat) (forest : List (UpperFusionTree n))
    (hmatch : (forestPackets forest).IsRotated (cyclicSignature P true)) :
    ∃ k' next, UpperForestStep k forest event k' next ∧
      (forestPackets next).IsRotated (cyclicSignature Q true) := by
  cases h with
  | fusion layer A B tail Q hA hB hdis before after other =>
      cases layer with
      | false =>
          exact ⟨k, forest, .lower A B (.refl _), hmatch.trans (other true (by decide))⟩
      | true =>
          obtain ⟨rotated, hrot, hpack⟩ := forest_rotation_lift forest _ (hmatch.trans before)
          cases rotated with
          | nil => simp [forestPackets] at hpack
          | cons left rest =>
              cases rest with
              | nil => simp [forestPackets] at hpack
              | cons right rest =>
                  have he : left.packet = A ∧ right.packet = B ∧ forestPackets rest = tail := by
                    simpa [forestPackets] using hpack
                  refine ⟨k, .merge left right :: rest, ?_, ?_⟩
                  · simpa [he.1, he.2.1] using
                      (UpperForestStep.fusion left right rest hrot (List.IsRotated.refl _))
                  · change ((left.packet ∪ right.packet) :: forestPackets rest).IsRotated _
                    rw [he.1, he.2.1, he.2.2]
                    exact after.symm
  | transfer packet lower upper Q hp hls hlt before after cap =>
      obtain ⟨rotated, hrot, hpack⟩ := forest_rotation_lift forest upper (hmatch.trans before)
      refine ⟨k+1, .leaf k packet :: rotated, .transfer packet rotated hrot (.refl _), ?_⟩
      change (packet :: forestPackets rotated).IsRotated _
      rw [hpack]
      exact after.symm

theorem CyclicEventPath.upper_forest_trace {P Q : Placement n} {events}
    (h : CyclicEventPath P events Q) (k : Nat) (forest : List (UpperFusionTree n))
    (hmatch : (forestPackets forest).IsRotated (cyclicSignature P true)) :
    ∃ k' next, UpperForestTrace P k forest events Q k' next := by
  induction h generalizing k forest with
  | nil same => exact ⟨k, forest, .nil hmatch same⟩
  | cons edge tail ih =>
      obtain ⟨mid, next, update, hm⟩ := edge.upper_forest_step k forest hmatch
      obtain ⟨last, final, ht⟩ := ih mid next hm
      exact ⟨last, final, .cons hmatch edge update ht⟩

/-- Cut an annotation at any event boundary of this same path. -/
theorem UpperForestTrace.split {P Q : Placement n} {k k' xs ys}
    (early later : List (EffectiveEvent n))
    (h : UpperForestTrace P k xs (early ++ later) Q k' ys) :
    ∃ R mid forest,
      UpperForestTrace P k xs early R mid forest ∧
      UpperForestTrace R mid forest later Q k' ys := by
  induction early generalizing P k xs with
  | nil => exact ⟨P, k, xs, .nil h.source_cycle (.refl _), h⟩
  | cons event rest ih =>
      cases h with
      | cons hmatch edge update tail =>
          obtain ⟨R, mid, forest, first, last⟩ := ih tail
          exact ⟨R, mid, forest, .cons hmatch edge update first, last⟩

@[simp] theorem cyclicSignature_seed_upper (n : Nat) :
    cyclicSignature (seed n) true = [] := by
  have hp : ∀ q : Fin n, packetAt (seed n) true q = ∅ := by
    intro q
    ext a
    simp [packetAt, seed]
  simp [cyclicSignature, layerSlots, hp, stripEmpty]

/-- A successful raw history supplies its ordered forest without an extra
forest-compatibility premise. In particular its leaves are distinct transfer
occurrences and its roots match the actual terminal upper packet cycle. -/
theorem singleton_run_ordered_forest {n : Nat} (hn : 1 < n)
    {word : List Letter} {Q : Placement n} {events}
    (h : runLogged n hn (seed n) word = some (Q, events)) :
    ∃ k forest,
      UpperForestTrace (seed n) 0 [] events Q k forest ∧
      (forestLeaves forest).Perm (List.range k) ∧
      (forestPackets forest).IsRotated (cyclicSignature Q true) := by
  obtain ⟨k, forest, ht⟩ :=
    (runLogged_cyclicEventPath n hn word h).upper_forest_trace 0 [] (by simp [forestPackets])
  exact ⟨k, forest, ht, ht.toPath.complete_leaves (by simp [forestLeaves]), ht.target_cycle⟩

/-- Strong compatibility at every prefix of the same actual event history.
The final expansion filtered to already-created leaves is the current
expanded packet cycle, and each current tree is an interval of that final
expansion. Neither intermediate physical coordinates nor routing costs occur. -/
theorem UpperForestTrace.prefix_compatibility {P Q : Placement n}
    {k k' xs ys} (early later : List (EffectiveEvent n))
    (h : UpperForestTrace P k xs (early ++ later) Q k' ys)
    (complete : (forestLeaves xs).Perm (List.range k)) :
    ∃ R mid forest,
      UpperForestTrace P k xs early R mid forest ∧
      UpperForestTrace R mid forest later Q k' ys ∧
      ((forestLeaves ys).filter (fun a => a < mid)).IsRotated (forestLeaves forest) ∧
      (forestPackets forest).IsRotated (cyclicSignature R true) ∧
      (∀ tree ∈ forest, ∃ left right, forestLeaves ys = left ++ tree.leaves ++ right) := by
  obtain ⟨R, mid, forest, first, last⟩ := h.split early later
  exact ⟨R, mid, forest, first, last,
    last.toPath.prefix_compatibility (first.toPath.complete_leaves complete),
    last.source_cycle, fun tree ht => last.toPath.tree_leaf_interval ht⟩

end RSR2History
