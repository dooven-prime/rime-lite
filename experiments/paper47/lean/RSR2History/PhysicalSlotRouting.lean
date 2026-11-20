import RSR2History.CyclicSignature

namespace RSR2History

open RSR2.Parametric

theorem silent_split_rotate (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (xs ys : List (Finset (Fin n)))
    (hslots : layerSlots P layer = xs ++ ys) :
    ∃ Q, SilentReachable n hn P Q ∧
      layerSlots Q layer = ys ++ xs ∧
      ∀ other, other ≠ layer → layerSlots Q other = layerSlots P other := by
  have hc : xs.length ≤ n := by
    have hlen := congrArg List.length hslots
    simp only [layerSlots_length, List.length_append] at hlen
    omega
  refine ⟨rotateMany n (by omega) P layer (n-xs.length),
    silent_rotateMany n hn P layer _, ?_, ?_⟩
  · rw [layerSlots_rotateMany n hn P layer xs.length hc, hslots]
    exact List.rotate_append_length_eq xs ys
  · intro other hne
    exact layerSlots_rotateMany_other n (by omega) P layer other hne _

theorem packetAt_collapse (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (q : Fin n) :
    packetAt (collapse n hn P layer) layer q =
      if q = site0 n (by omega) then
        packetAt P layer (site0 n (by omega)) ∪ packetAt P layer (site1 n hn)
      else if q = site1 n hn then ∅ else packetAt P layer q := by
  have h01 : site0 n (by omega) ≠ site1 n hn := by
    intro h
    have := congrArg Fin.val h
    simp [site0, site1] at this
  apply Finset.ext
  intro a
  by_cases hq0 : q = site0 n (by omega)
  · subst q
    simp only [if_pos, Finset.mem_union, mem_packetAt]
    by_cases ha : P a = (layer, site1 n hn)
    · simp [collapse, ha]
    · simp [collapse, ha]
  · simp only [if_neg hq0]
    by_cases hq1 : q = site1 n hn
    · subst q
      simp only [if_pos, Finset.notMem_empty, mem_packetAt]
      by_cases ha : P a = (layer, site1 n hn)
      · simp [collapse, ha, h01]
      · simp [collapse, ha]
    · simp only [if_neg hq1, mem_packetAt]
      by_cases ha : P a = (layer, site1 n hn)
      · simp [collapse, ha, Ne.symm hq0, Ne.symm hq1]
      · simp [collapse, ha]

theorem layerSlots_collapse_other (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer other : Layer) (hne : other ≠ layer) :
    layerSlots (collapse n hn P layer) other = layerSlots P other := by
  unfold layerSlots
  congr 1
  funext q
  apply Finset.ext
  intro a
  simp only [mem_packetAt]
  by_cases ha : P a = (layer, site1 n hn)
  · simp only [collapse, ha, if_pos]
    constructor <;> intro h <;>
      exact False.elim (hne (congrArg Prod.fst h).symm)
  · simp [collapse, ha]

/-- Exact physical slot update when the left port is empty. -/
theorem layerSlots_collapse_front (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (a : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P layer = ∅ :: a :: post) :
    layerSlots (collapse n hn P layer) layer = a :: ∅ :: post := by
  have hzero : packetAt P layer (site0 n (by omega)) = ∅ := by
    have h := congrArg (fun xs => xs[0]?) hslots
    simpa [layerSlots, site0, show 0 < n by omega] using h
  have hone : packetAt P layer (site1 n hn) = a := by
    have h := congrArg (fun xs => xs[1]?) hslots
    simpa [layerSlots, site1, show 1 < n by omega] using h
  apply List.ext_getElem
  · have := congrArg List.length hslots
    simp only [layerSlots_length, List.length_cons] at *
    omega
  · intro q hq hq'
    rw [layerSlots_getElem, packetAt_collapse]
    rcases q with _ | q
    · rw [if_pos (show (⟨0, by simpa using hq⟩ : Fin n) =
          site0 n (by omega) from rfl)]
      change packetAt P layer (site0 n (by omega)) ∪
        packetAt P layer (site1 n hn) = a
      rw [hzero, hone, Finset.empty_union]
    · rcases q with _ | q
      · simp [site0, site1]
      · have hz : (⟨q+2, by simpa using hq⟩ : Fin n) ≠ site0 n (by omega) := by
          intro h; have := congrArg Fin.val h; simp [site0] at this
        have ho : (⟨q+2, by simpa using hq⟩ : Fin n) ≠ site1 n hn := by
          intro h; have := congrArg Fin.val h; simp [site1] at this
        simp only [if_neg hz, if_neg ho, List.getElem_cons_succ]
        have h := congrArg (fun xs => xs[q+2]?) hslots
        have hqn : q+2 < n := by simpa using hq
        have hpost : q < post.length := by simpa using hq'
        simpa [layerSlots, hqn, List.getElem?_eq_getElem hpost] using h

/-- An actual empty left port enables the silent slide at the list head. -/
theorem silent_front_slide (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (a : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P layer = ∅ :: a :: post) :
    ∃ Q, SilentReachable n hn P Q ∧
      layerSlots Q layer = a :: ∅ :: post ∧
      ∀ other, other ≠ layer → layerSlots Q other = layerSlots P other := by
  have hzero : packetAt P layer (site0 n (by omega)) = ∅ := by
    have h := congrArg (fun xs => xs[0]?) hslots
    simpa [layerSlots, site0, show 0 < n by omega] using h
  have hempty : ¬ occupiedAt P layer (site0 n (by omega)) := by
    rw [← packetAt_nonempty, hzero]
    simp
  exact ⟨collapse n hn P layer,
    ((silentStep_d_iff n hn P layer).mpr (fun h => hempty h.1)).reachable,
    layerSlots_collapse_front n hn P layer a post hslots,
    fun other hne => layerSlots_collapse_other n hn P layer other hne⟩

/-- Lift every combinatorial slot route to the original guarded executor. -/
theorem SlotRoute.realize {n : Nat} (hn : 1 < n) {xs ys : List (Finset (Fin n))}
    (h : SlotRoute ∅ xs ys) (P : Placement n) (layer : Layer)
    (hslots : layerSlots P layer = xs) :
    ∃ Q, SilentReachable n hn P Q ∧ layerSlots Q layer = ys ∧
      ∀ other, other ≠ layer → layerSlots Q other = layerSlots P other := by
  induction h generalizing P with
  | refl xs => exact ⟨P, .refl n hn P, hslots, fun _ _ => rfl⟩
  | rotate xs ys => exact silent_split_rotate n hn P layer xs ys hslots
  | slide pre post a =>
      obtain ⟨R, hPR, hR, hRother⟩ :=
        silent_split_rotate n hn P layer pre (∅ :: a :: post) hslots
      obtain ⟨T, hRT, hT, hTother⟩ :=
        silent_front_slide n hn R layer a (post ++ pre)
          (by simpa [List.append_assoc] using hR)
      obtain ⟨Q, hTQ, hQ, hQother⟩ :=
        silent_split_rotate n hn T layer (a :: ∅ :: post) pre
          (by simpa [List.append_assoc] using hT)
      exact ⟨Q, hPR.trans (hRT.trans hTQ), hQ,
        fun other hne => (hQother other hne).trans
          ((hTother other hne).trans (hRother other hne))⟩
  | trans _ _ ih₁ ih₂ =>
      obtain ⟨R, hPR, hR, hRother⟩ := ih₁ P hslots
      obtain ⟨Q, hRQ, hQ, hQother⟩ := ih₂ R hR
      exact ⟨Q, hPR.trans hRQ, hQ,
        fun other hne => (hQother other hne).trans (hRother other hne)⟩

end RSR2History
