import RSR2History.ReverseExtraction
import RSR2History.SlotRouting

/-!
The lower ring seen from its physical port.  After holes are erased, a
nonfusion slide leaves the linear packet list unchanged.  One physical
rotation moves at most one last packet to the front.  This is a relaxation
of the actual extraction machine, not an assumption about its scheduling.
-/

namespace RSR2History
open RSR2.Parametric

def extractionPacketAt (c : LowerConfiguration n) (q : Fin n) : Finset (Fin n) :=
  Finset.univ.filter fun a => c a = some q

@[simp] theorem mem_extractionPacketAt (c : LowerConfiguration n) (q a : Fin n) :
    a ∈ extractionPacketAt c q ↔ c a = some q := by
  simp [extractionPacketAt]

def extractionSlots (c : LowerConfiguration n) : List (Finset (Fin n)) :=
  List.ofFn (extractionPacketAt c)

@[simp] theorem extractionSlots_length (c : LowerConfiguration n) :
    (extractionSlots c).length = n := by simp [extractionSlots]

@[simp] theorem extractionSlots_getElem (c : LowerConfiguration n) (i : Nat)
    (hi : i < (extractionSlots c).length) :
    (extractionSlots c)[i] = extractionPacketAt c ⟨i, by simpa using hi⟩ := by
  simp [extractionSlots]

def portFacingPackets (c : LowerConfiguration n) : List (Finset (Fin n)) :=
  stripEmpty ∅ (extractionSlots c)

theorem portFacingPackets_seed (n : Nat) :
    portFacingPackets (lowerExtractionSeed n) =
      (List.finRange n).map (fun a => ({a} : Finset (Fin n))) := by
  have hs : extractionSlots (lowerExtractionSeed n) =
      (List.finRange n).map (fun a => ({a} : Finset (Fin n))) := by
    apply List.ext_getElem
    · simp
    · intro i hi hi'
      simp only [extractionSlots_getElem, List.getElem_map, List.getElem_finRange]
      ext a
      simp [lowerExtractionSeed]
  simp [portFacingPackets, hs, stripEmpty]

theorem extractionSlots_rotate (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) :
    (extractionSlots (lowerRotate n hn c)).rotate 1 = extractionSlots c := by
  apply List.ext_getElem
  · simp
  · intro i hi hi'
    simp only [List.getElem_rotate, extractionSlots_length, extractionSlots_getElem]
    apply Finset.ext
    intro a
    simp only [mem_extractionPacketAt]
    cases hca : c a with
    | none => simp [lowerRotate, hca]
    | some q =>
        simp only [lowerRotate, hca, Option.map_some, Option.some.injEq]
        have hi : i < n := by simpa using hi'
        have ht : (⟨(i + 1) % n, Nat.mod_lt _ (by omega)⟩ : Fin n) =
            next n (by omega) ⟨i, hi⟩ := by
          apply Fin.ext
          simp only [next]
          split_ifs with h
          · simp [Nat.mod_eq_of_lt h]
          · have he : i + 1 = n := by omega
            simp [he]
        rw [ht]
        exact ⟨fun h => next_injective n (by omega) h, congrArg _⟩

private theorem strip_one_rotation {α : Type*} [DecidableEq α]
    (empty : α) {xs ys : List α} (h : ys.rotate 1 = xs) :
    ∃ j ≤ 1, (stripEmpty empty ys).rotate j = stripEmpty empty xs := by
  subst xs
  cases ys with
  | nil => exact ⟨0, by omega, rfl⟩
  | cons y ys =>
      by_cases hy : y = empty
      · subst y
        exact ⟨0, by omega, by simp [stripEmpty, List.rotate_cons_succ]⟩
      · exact ⟨1, by omega, by simp [stripEmpty, hy, List.rotate_cons_succ]⟩

/-- At most one live-list rotation is induced by a physical rotation;
crossing an empty site induces none. -/
theorem portFacingPackets_rotate (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) :
    ∃ j ≤ 1, (portFacingPackets (lowerRotate n hn c)).rotate j = portFacingPackets c :=
  strip_one_rotation ∅ (extractionSlots_rotate n hn c)

theorem portFacingPackets_slide (n : Nat) (hn : 1 < n) (c : LowerConfiguration n)
    (empty : ∀ a, c a ≠ some (site0 n (by omega))) :
    portFacingPackets (lowerSlide n hn c) = portFacingPackets c := by
  have h0 : extractionPacketAt c (site0 n (by omega)) = ∅ := by
    ext a
    simp [empty a]
  have hs : ∃ tail, extractionSlots c = ∅ :: extractionPacketAt c (site1 n hn) :: tail ∧
      extractionSlots (lowerSlide n hn c) =
        extractionPacketAt c (site1 n hn) :: ∅ :: tail := by
    refine ⟨(extractionSlots c).drop 2, ?_, ?_⟩
    · apply List.ext_getElem
      · simp; omega
      · intro i hi hi'
        cases i with
        | zero => simpa [site0] using h0
        | succ i =>
            cases i with
            | zero => simp [site1]
            | succ i => simp [Nat.add_comm, Nat.add_left_comm]
    · apply List.ext_getElem
      · simp; omega
      · intro i hi hi'
        cases i with
        | zero =>
          simp only [extractionSlots_getElem, List.getElem_cons_zero]
          ext a
          simp only [mem_extractionPacketAt]
          change (if c a = some (site1 n hn) then some (site0 n (by omega)) else c a) =
            some (site0 n (by omega)) ↔ c a = some (site1 n hn)
          by_cases ha : c a = some (site1 n hn)
          · simp [ha]
          · simp only [if_neg ha]
            exact iff_of_false (empty a) ha
        | succ i =>
          cases i with
          | zero =>
            simp only [extractionSlots_getElem, List.getElem_cons_succ,
              List.getElem_cons_zero]
            ext a
            simp only [mem_extractionPacketAt, Finset.notMem_empty, iff_false]
            change ¬ (if c a = some (site1 n hn) then some (site0 n (by omega)) else c a) =
              some (site1 n hn)
            by_cases ha : c a = some (site1 n hn)
            · simp [ha, site0, site1, Fin.ext_iff]
            · simpa only [if_neg ha] using ha
          | succ i =>
            simp only [List.getElem_cons_succ, List.getElem_drop,
              extractionSlots_getElem]
            ext a
            simp only [mem_extractionPacketAt, lowerSlide]
            by_cases ha : c a = some (site1 n hn)
            · simp [ha, site0, site1, Fin.ext_iff]; omega
            · simp [ha, Nat.add_comm, Nat.add_left_comm]
  obtain ⟨tail, hbefore, hafter⟩ := hs
  by_cases hpacket : extractionPacketAt c (site1 n hn) = ∅ <;>
    simp [portFacingPackets, hbefore, hafter, stripEmpty, hpacket]

theorem portFacingPackets_delete {n : Nat} (hn : 1 < n)
    (c : LowerConfiguration n) (a : Fin n)
    (atPort : c a = some (site0 n (by omega)))
    (singleton : ∀ b, c b = some (site0 n (by omega)) → b = a) :
    ∃ tail, portFacingPackets c = {a} :: tail ∧
      portFacingPackets (lowerDelete c a) = tail := by
  have hpacket : extractionPacketAt c (site0 n (by omega)) = {a} := by
    ext b
    simp only [mem_extractionPacketAt, Finset.mem_singleton]
    exact ⟨singleton b, fun h => h ▸ atPort⟩
  have hslots : extractionSlots c = {a} :: (extractionSlots c).drop 1 := by
    apply List.ext_getElem
    · simp; omega
    · intro i hi hi'
      cases i with
      | zero => simpa [site0] using hpacket
      | succ i => simp
  have hdeleted : extractionSlots (lowerDelete c a) =
      ∅ :: (extractionSlots c).drop 1 := by
    apply List.ext_getElem
    · simp; omega
    · intro i hi hi'
      cases i with
      | zero =>
          simp only [extractionSlots_getElem, List.getElem_cons_zero]
          ext b
          by_cases hba : b = a
          · simp [lowerDelete, hba]
          · simp only [mem_extractionPacketAt, lowerDelete, if_neg hba,
              Finset.notMem_empty, iff_false]
            exact fun h => hba (singleton b h)
      | succ i =>
          simp only [List.getElem_cons_succ, List.getElem_drop,
            extractionSlots_getElem]
          ext b
          by_cases hba : b = a
          · subst b
            simp [lowerDelete, atPort, site0, Fin.ext_iff]; omega
          · simp [lowerDelete, hba, Nat.add_comm]
  exact ⟨stripEmpty ∅ ((extractionSlots c).drop 1),
    by simpa [portFacingPackets, stripEmpty] using congrArg (stripEmpty ∅) hslots,
    by simp [portFacingPackets, hdeleted, stripEmpty]⟩

/-- Every actual deletion-free preparation projects to at most its cost
many unit rotations of the live packet list. Slides cannot bypass this. -/
theorem LowerExtractionPath.portFacing_noDeletion
    {n : Nat} {hn : 1 < n} {c d : LowerConfiguration n}
    {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k) (hz : z = []) :
    ∃ j ≤ k, (portFacingPackets d).rotate j = portFacingPackets c := by
  induction path with
  | refl c => exact ⟨0, by omega, by simp⟩
  | rotate c => exact portFacingPackets_rotate n hn c
  | slide c empty occupied =>
      exact ⟨0, by omega, by simpa using portFacingPackets_slide n hn c empty⟩
  | delete => simp at hz
  | trans first second ih₁ ih₂ =>
      obtain ⟨hu, hv⟩ := List.append_eq_nil_iff.mp hz
      obtain ⟨j, hj, hfirst⟩ := ih₁ hu
      obtain ⟨l, hl, hsecond⟩ := ih₂ hv
      exact ⟨l + j, by omega, by rw [← List.rotate_rotate, hsecond, hfirst]⟩

private theorem rotated_same_head {α : Type*} {a : α} {xs ys : List α}
    (hnd : (a :: xs).Nodup)
    (hrot : (a :: xs).IsRotated (a :: ys)) : xs = ys := by
  obtain ⟨k, hk, hrotate⟩ := List.isRotated_iff_mod.mp hrot
  by_cases hend : k = xs.length + 1
  · subst k
    have hfull : (a :: xs).rotate (xs.length + 1) = a :: xs := by simp
    rw [hfull] at hrotate
    exact (List.cons.inj hrotate).2
  · have hlt : k < xs.length + 1 := by simp_all; omega
    by_cases hzero : k = 0
    · subst k
      simpa using (List.cons.inj (by simpa using hrotate : a :: xs = a :: ys)).2
    · obtain ⟨j, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hzero
      have hj : j < xs.length := by omega
      have hrotate' : (xs ++ [a]).rotate j = a :: ys := by
        simpa only [List.rotate_cons_succ] using hrotate
      have hhead : ((xs ++ [a]).rotate j).head? = some a := by rw [hrotate']; rfl
      rw [List.head?_rotate (by simp; omega)] at hhead
      have hget : (xs ++ [a])[j]? = some a := by simpa using hhead
      rw [List.getElem?_append_left hj] at hget
      exact False.elim ((List.nodup_cons.mp hnd).1
        (List.mem_iff_getElem?.mpr ⟨j, hget⟩))

/-- If the next prescribed deletion is the second live atom, the actual
deletion-free interval costs at least `liveCount - 1`.  Its residual list
is determined, even if the interval made additional complete turns. -/
theorem LowerExtractionPath.second_live_deletion
    {n : Nat} {hn : 1 < n} {c d : LowerConfiguration n} {k : Nat}
    {x y : Fin n} {tail : List (Fin n)}
    (path : LowerExtractionPath n hn c [] d k)
    (horder : portFacingPackets c =
      (x :: y :: tail).map (fun a => ({a} : Finset (Fin n))))
    (hnd : (x :: y :: tail).Nodup)
    (atPort : d y = some (site0 n (by omega)))
    (singleton : ∀ b, d b = some (site0 n (by omega)) → b = y) :
    tail.length + 1 ≤ k ∧ portFacingPackets (lowerDelete d y) =
      (tail ++ [x]).map (fun a => ({a} : Finset (Fin n))) := by
  obtain ⟨j, hj, hrotation⟩ := path.portFacing_noDeletion rfl
  obtain ⟨after, hbefore, hafter⟩ := portFacingPackets_delete hn d y atPort singleton
  let original := (x :: y :: tail).map (fun a => ({a} : Finset (Fin n)))
  let rest := (tail ++ [x]).map (fun a => ({a} : Finset (Fin n)))
  have horig : original.Nodup := hnd.map (by
    intro a b h
    simpa using h : Function.Injective (fun a : Fin n => ({a} : Finset (Fin n))))
  have hturn : original.rotate 1 = {y} :: rest := by
    simp [original, rest, List.rotate_cons_succ]
  have hrot : ({y} :: after).rotate j = original := by
    simpa only [horder, hbefore] using hrotation
  have hndturn : ({y} :: rest).Nodup := by
    rw [← hturn]
    exact (List.rotate_perm original 1).nodup_iff.mpr horig
  have hcircle : ({y} :: rest).IsRotated ({y} :: after) := by
    rw [← hturn]
    exact (List.IsRotated.forall original 1).trans (List.IsRotated.symm ⟨j, hrot⟩)
  have hrest : rest = after := rotated_same_head hndturn hcircle
  have hself : original.rotate (1 + j) = original := by
    rw [← List.rotate_rotate, hturn, hrest]
    exact hrot
  have hmod : (1 + j) % original.length = 0 := by
    exact (horig.rotate_eq_self_iff.mp hself).resolve_right (by simp [original])
  have hcost : tail.length + 1 ≤ j := by
    by_contra h
    have hlt : 1 + j < original.length := by simp [original]; omega
    rw [Nat.mod_eq_of_lt hlt] at hmod
    omega
  exact ⟨by omega, hafter.trans hrest.symm⟩

end RSR2History
