import RSR2History.PhysicalSlotRouting

/-!
H1: the two named packet cycles are a complete invariant of silent guarded
reachability. No source-order hypothesis, nonempty-layer hypothesis, budget
assumption, or import of the single-ring compression project is used.
-/

namespace RSR2History

open RSR2.Parametric

theorem SlotRoute.to_rotate {α : Type*} [DecidableEq α]
    (empty : α) (xs : List α) (k : Nat) :
    SlotRoute empty xs (xs.rotate k) := by
  have h := SlotRoute.rotate (empty := empty)
    (xs.take (k % xs.length)) (xs.drop (k % xs.length))
  simpa only [List.take_append_drop, List.rotate_eq_drop_append_take_mod] using h

theorem collapse_eq_of_empty_right (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer)
    (h : ¬ occupiedAt P layer (site1 n hn)) : collapse n hn P layer = P := by
  funext a
  have ha : P a ≠ (layer, site1 n hn) := by
    intro he
    exact h ⟨a, he⟩
  simp [collapse, ha]

/-- Every actual silent letter preserves the two physical packet cycles. -/
theorem SilentStep.sameCyclicSignatures {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {letter : Letter} (h : SilentStep n hn P Q letter) :
    SameCyclicSignatures P Q := by
  intro other
  cases letter with
  | p layer =>
      have he : Q = rotate n (by omega) P layer := by
        simpa [step_p] using h.1.symm
      subst Q
      change (stripEmpty ∅ (layerSlots P other)).IsRotated
        (stripEmpty ∅ (layerSlots (rotate n (by omega) P layer) other))
      by_cases hl : other = layer
      · subst other
        have hc : n - (n-1) = 1 := by omega
        have hr := layerSlots_rotateMany n hn P layer (n-1) (by omega)
        rw [hc] at hr
        change layerSlots (rotate n (by omega) P layer) layer = _ at hr
        rw [hr]
        exact (SlotRoute.to_rotate ∅ (layerSlots P layer) (n-1)).strip_rotated
      · have hr := layerSlots_rotateMany_other n (by omega) P layer other hl 1
        change layerSlots (rotate n (by omega) P layer) other = _ at hr
        rw [hr]
  | d layer =>
      have he : Q = collapse n hn P layer := by
        simpa [step_d] using h.1.symm
      subst Q
      change (stripEmpty ∅ (layerSlots P other)).IsRotated
        (stripEmpty ∅ (layerSlots (collapse n hn P layer) other))
      by_cases hl : other = layer
      · subst other
        have hsilent := (silentStep_d_iff n hn P layer).mp h
        by_cases hright : occupiedAt P layer (site1 n hn)
        · have hleft : ¬ occupiedAt P layer (site0 n (by omega)) :=
            fun hp => hsilent ⟨hp, hright⟩
          have hzero : packetAt P layer (site0 n (by omega)) = ∅ := by
            apply Finset.eq_empty_iff_forall_notMem.mpr
            intro a ha
            exact hleft ⟨a, (mem_packetAt _ _ _ _).mp ha⟩
          obtain ⟨a, b, post, hslots⟩ :
              ∃ a b post, layerSlots P layer = a :: b :: post := by
            have hlen := layerSlots_length P layer
            cases hs : layerSlots P layer with
            | nil => simp [hs] at hlen; omega
            | cons a rest =>
                cases rest with
                | nil => simp [hs] at hlen; omega
                | cons b post => exact ⟨a, b, post, rfl⟩
          have ha : a = ∅ := by
            have hs := congrArg (fun xs => xs[0]?) hslots
            have he : packetAt P layer (site0 n (by omega)) = a := by
              simpa [layerSlots, site0, show 0 < n by omega] using hs
            exact he.symm.trans hzero
          subst a
          rw [layerSlots_collapse_front n hn P layer b post hslots, hslots]
          exact (SlotRoute.slide (empty := (∅ : Finset (Fin n))) [] post b).strip_rotated
        · rw [collapse_eq_of_empty_right n hn P layer hright]
      · rw [layerSlots_collapse_other n hn P layer other hl]
  | v => exact False.elim (not_silentStep_v n hn P Q h)

/-- Necessity is an induction on the same actual logged execution. -/
theorem runLogged_empty_signatures (n : Nat) (hn : 1 < n)
    (word : List Letter) {P Q : Placement n}
    (h : runLogged n hn P word = some (Q, [])) : SameCyclicSignatures P Q := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa [runLogged] using h
      subst Q
      exact fun _ => .refl _
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at h
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at h
          | some result =>
              obtain ⟨S, events⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ events = [] := by
                simpa [runLogged, hs, hr] using h
              obtain ⟨hempty, htail⟩ := List.append_eq_nil_iff.mp he.2
              have hfirst : SilentStep n hn P R letter := ⟨hs, hempty⟩
              have hrest : runLogged n hn R rest = some (Q, []) := by
                simpa [he.1, htail] using hr
              exact fun layer => (hfirst.sameCyclicSignatures layer).trans (ih hrest layer)

/-- Sufficiency routes the two layers in succession, preserving the other
layer exactly. The list theorem includes empty, singleton and full layers. -/
theorem SameCyclicSignatures.silentReachable {n : Nat} (hn : 1 < n)
    {P Q : Placement n} (h : SameCyclicSignatures P Q) : SilentReachable n hn P Q := by
  have hlow : SlotRoute ∅ (layerSlots P false) (layerSlots Q false) :=
    (slotRoute_iff _ _ _).mpr ⟨by simp, h false⟩
  obtain ⟨R, hPR, hR, hRother⟩ := hlow.realize hn P false rfl
  have hupp : SlotRoute ∅ (layerSlots R true) (layerSlots Q true) := by
    rw [hRother true (by decide)]
    exact (slotRoute_iff _ _ _).mpr ⟨by simp, h true⟩
  obtain ⟨S, hRS, hS, hSother⟩ := hupp.realize hn R true rfl
  have he : S = Q := by
    apply layerSlots_ext
    intro layer
    cases layer with
    | false => exact (hSother false (by decide)).trans hR
    | true => exact hS
  exact he ▸ hPR.trans hRS

/-- H1, for every size supported by the original five-letter executor. -/
theorem silent_reachable_iff_cyclic_signatures (n : Nat) (hn : 1 < n)
    (P Q : Placement n) :
    SilentReachable n hn P Q ↔ SameCyclicSignatures P Q := by
  exact ⟨fun ⟨word, hw⟩ => runLogged_empty_signatures n hn word hw,
    fun h => h.silentReachable hn⟩

/-- The constructed witness has the requested literal endpoint and no events
under the original guarded executor, not merely in a combinatorial model. -/
theorem silent_preparation_witness (n : Nat) (hn : 1 < n)
    {P Q : Placement n} (h : SameCyclicSignatures P Q) :
    ∃ word, run n hn P word = some Q ∧
      runLogged n hn P word = some (Q, []) := by
  obtain ⟨word, hw⟩ := h.silentReachable hn
  refine ⟨word, ?_, hw⟩
  have hp := runLogged_project n hn P word
  simpa [hw] using hp.symm

end RSR2History
