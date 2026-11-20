import RSR2History.CyclicGapFrames
import RSR2History.PhysicalSlotRouting

namespace RSR2History
open RSR2.Parametric

private def optionPacket (b : Finset (Fin n)) : Option (Finset (Fin n)) :=
  if b = ∅ then none else some b

@[simp] theorem layerView_eq_none {n : Nat} [NeZero n]
    (P : Placement n) (layer : Layer) (q : ZMod n) :
    layerView P layer q = none ↔ packetAt P layer ⟨q.val, ZMod.val_lt q⟩ = ∅ := by
  simp [layerView]

private theorem pred_val {n : Nat} [NeZero n] (q : ZMod n) :
    (q-1).val = (q.val+(n-1)) % n := by
  have hn : 0 < n := Nat.pos_of_ne_zero (NeZero.ne n)
  have he : q-1 = ((q.val+(n-1) : Nat) : ZMod n) := by
    rw [Nat.cast_add, Nat.cast_sub (by omega : 1 ≤ n), ZMod.natCast_self]
    simp [sub_eq_add_neg]
  rw [he, ZMod.val_natCast]

theorem layerView_rotate {n : Nat} [NeZero n] (hn : 1 < n)
    (P : Placement n) (layer : Layer) :
    layerView (rotate n (by omega) P layer) layer =
      RegisteredAbsorptionChains.rotate 1 (layerView P layer) := by
  have hl := layerSlots_rotateMany n hn P layer (n-1) (by omega)
  have hcount : n-(n-1) = 1 := by omega
  rw [hcount] at hl
  change layerSlots (rotate n (by omega) P layer) layer = _ at hl
  funext q
  have h := congrArg (fun xs : List (Finset (Fin n)) => xs[q.val]?) hl
  have hq := ZMod.val_lt q
  have hL : (layerSlots (rotate n (by omega) P layer) layer)[q.val]? =
      some (packetAt (rotate n (by omega) P layer) layer ⟨q.val, hq⟩) := by
    simp [layerSlots_length, hq]
  have hR : ((layerSlots P layer).rotate (n-1))[q.val]? =
      some (packetAt P layer ⟨(q.val+(n-1)) % n, Nat.mod_lt _ (by omega)⟩) := by
    simp [layerSlots_length, hq, List.getElem_rotate]
  rw [hL, hR, Option.some.injEq] at h
  change optionPacket (packetAt (rotate n (by omega) P layer) layer ⟨q.val, hq⟩) =
    optionPacket (packetAt P layer ⟨(q-1).val, ZMod.val_lt _⟩)
  congr 1
  simpa only [pred_val] using h

theorem layerView_collapse {n : Nat} [NeZero n] (hn : 1 < n)
    (P : Placement n) (layer : Layer) :
    layerView (collapse n hn P layer) layer =
      RegisteredAbsorptionChains.fusionPlacement (layerView P layer) := by
  have h01 : (1 : ZMod n).val = 1 := by
    have : Fact (1 < n) := ⟨hn⟩
    exact ZMod.val_one n
  funext q
  have hq0 : (⟨q.val, ZMod.val_lt q⟩ : Fin n) = site0 n (by omega) ↔ q = 0 := by
    rw [Fin.ext_iff]
    exact ⟨fun h => (ZMod.val_injective n) (by simpa [site0] using h),
      fun h => by subst q; simp [site0]⟩
  have hq1 : (⟨q.val, ZMod.val_lt q⟩ : Fin n) = site1 n hn ↔ q = 1 := by
    rw [Fin.ext_iff]
    exact ⟨fun h => (ZMod.val_injective n) (by simpa [site1, h01] using h),
      fun h => by subst q; simpa [site1] using h01⟩
  unfold layerView
  rw [packetAt_collapse]
  simp only [hq0, hq1, RegisteredAbsorptionChains.fusionPlacement]
  by_cases h0 : q = 0
  · subst q
    simp only [ite_true, ZMod.val_zero]
    by_cases hL : packetAt P layer (site0 n (by omega)) = ∅ <;>
      by_cases hR : packetAt P layer (site1 n hn) = ∅ <;>
      simp_all [site0, site1]
  · by_cases h1 : q = 1
    · subst q
      simp [h0]
    · simp [h0, h1]

/-- One upstream raw letter maps to exactly one of the five original letters. -/
def layerLetter (layer : Layer) : RegisteredAbsorptionChains.Letter → Letter
  | .p => .p layer
  | .d => .d layer

theorem layerWord_simulation {n : Nat} [NeZero n] (hn : 1 < n)
    (P : Placement n) (layer : Layer)
    (s : RegisteredAbsorptionChains.Execution n (Fin n))
    (word : List RegisteredAbsorptionChains.Letter)
    (source : s.placed = layerView P layer)
    (free : RegisteredAbsorptionChains.FusionFree ∅ s word) :
    ∃ Q, runLogged n hn P (word.map (layerLetter layer)) = some (Q, []) ∧
      layerView Q layer = (RegisteredAbsorptionChains.run ∅ s word).placed ∧
      ∀ other, other ≠ layer → layerSlots Q other = layerSlots P other := by
  induction word generalizing P s with
  | nil => exact ⟨P, rfl, source.symm, fun _ _ => rfl⟩
  | cons letter rest ih =>
      let Q := match letter with
        | .p => rotate n (by omega) P layer
        | .d => collapse n hn P layer
      have hs : step n hn P (layerLetter layer letter) = some Q := by
        cases letter <;> simp [layerLetter, Q, step]
      have hv : layerView Q layer = (RegisteredAbsorptionChains.step ∅ s letter).placed := by
        cases letter with
        | p => simpa [Q, RegisteredAbsorptionChains.step, source] using layerView_rotate hn P layer
        | d =>
            have hd : (RegisteredAbsorptionChains.step ∅ s .d).placed =
                RegisteredAbsorptionChains.fusionPlacement s.placed := by
              simp only [RegisteredAbsorptionChains.step, RegisteredAbsorptionChains.stepDefect]
              split <;> rfl
            rw [hd, source]
            exact layerView_collapse hn P layer
      have he : emittedEvents n hn P (layerLetter layer letter) = [] := by
        cases letter with
        | p => rfl
        | d =>
            have hhole := free.1
            rw [source] at hhole
            have h0 : layerView P layer 0 = none ↔ ¬ occupiedAt P layer (site0 n (by omega)) := by
              rw [layerView_eq_none]
              simpa [site0] using Finset.not_nonempty_iff_eq_empty.symm.trans
                (not_congr (packetAt_nonempty P layer (site0 n (by omega))))
            have h1 : layerView P layer 1 = none ↔ ¬ occupiedAt P layer (site1 n hn) := by
              rw [layerView_eq_none]
              have hval : (1 : ZMod n).val = 1 := by
                have : Fact (1 < n) := ⟨hn⟩
                exact ZMod.val_one n
              simpa [site1, hval] using
                (Finset.not_nonempty_iff_eq_empty.symm.trans (not_congr
                  (packetAt_nonempty P layer (site1 n hn))))
            have hno : ¬ (occupiedAt P layer (site0 n (by omega)) ∧
                occupiedAt P layer (site1 n hn)) := by
              rcases hhole with h | h
              · exact fun hboth => (h0.mp h) hboth.1
              · exact fun hboth => (h1.mp h) hboth.2
            simp [layerLetter, emittedEvents, hno]
      have htail : RegisteredAbsorptionChains.FusionFree ∅
          (RegisteredAbsorptionChains.step ∅ s letter) rest := by
        cases letter with
        | p => exact free
        | d => exact free.2
      obtain ⟨R, hr, hview, hother⟩ := ih Q _ hv.symm htail
      refine ⟨R, ?_, ?_, ?_⟩
      · simpa [List.map_cons, runLogged, hs, he] using hr
      · simpa [RegisteredAbsorptionChains.run, List.foldl_cons] using hview
      · intro other hne
        rw [hother other hne]
        cases letter with
        | p => exact layerSlots_rotateMany_other n (by omega) P layer other hne 1
        | d => exact layerSlots_collapse_other n hn P layer other hne

end RSR2History
